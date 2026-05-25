import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, max, min, expr, countDistinct, to_date, lit, month, year, concat, desc, date_format, hour, when, abs, floor, months_between, first, avg
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
import sys

def run_analytics():
    # Configuration
    db_user = os.getenv('DB_USER', 'retail_user')
    db_password = os.getenv('DB_PASSWORD', 'retail_password')
    db_host = os.getenv('DB_HOST', 'mysql-service')
    db_name = os.getenv('DB_NAME', 'retail_db')
    
    jdbc_url = f"jdbc:mysql://{db_host}/{db_name}"
    properties = {
        "user": db_user,
        "password": db_password,
        "driver": "com.mysql.cj.jdbc.Driver"
    }

    spark = SparkSession.builder \
        .appName("RetailAnalytics") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .getOrCreate()

    try:
        print("Reading raw data from MySQL...")
        raw_df = spark.read.jdbc(url=jdbc_url, table="raw_transactions", properties=properties)
        
        # --- Stage 2: Data Cleaning & Transformation ---
        print("Cleaning data...")
        base_df = raw_df.dropna(subset=["customer_id", "description"])
        base_df = base_df.withColumn("total_price", col("quantity") * col("price"))
        base_df = base_df.withColumn("month_year", date_format(col("invoicedate"), "yyyy-MM"))
        
        clean_df = base_df.filter(~col("invoice").cast("string").startswith("C"))
        clean_df = clean_df.filter((col("quantity") > 0) & (col("price") > 0)).cache()
        
        returns_df = base_df.filter(col("invoice").cast("string").startswith("C") | (col("quantity") < 0))
        
        # --- Stage 3: RFM Analysis & Clustering ---
        print("Performing RFM Analysis...")
        max_date_row = clean_df.select(max("invoicedate")).collect()[0]
        if not max_date_row or max_date_row[0] is None:
            print("No data found in clean_df. Skipping analytics.")
            return

        max_date = max_date_row[0]
        rfm_df = clean_df.groupBy("customer_id").agg(
            expr(f"datediff('{max_date}', max(invoicedate))").alias("recency"),
            countDistinct("invoice").alias("frequency"),
            sum("total_price").alias("monetary")
        ).cache()
        
        assembler = VectorAssembler(inputCols=["recency", "frequency", "monetary"], outputCol="features")
        rfm_features = assembler.transform(rfm_df)
        scaler = StandardScaler(inputCol="features", outputCol="scaled_features", withStd=True, withMean=False)
        scaler_model = scaler.fit(rfm_features)
        rfm_scaled = scaler_model.transform(rfm_features)
        
        kmeans = KMeans(featuresCol="scaled_features", k=4, seed=42)
        model = kmeans.fit(rfm_scaled)
        final_segments = model.transform(rfm_scaled).select("customer_id", "recency", "frequency", "monetary", "prediction")
        
        # --- Stage 4: Comprehensive Metrics ---

        # 1. Sales Heatmap (Day vs Hour)
        sales_heatmap = clean_df.withColumn("day_of_week", date_format(col("invoicedate"), "EEEE")) \
            .withColumn("hour", hour(col("invoicedate"))) \
            .groupBy("day_of_week", "hour").agg(sum("total_price").alias("revenue"))

        # 2. CLV Distribution (Monetary Bins)
        clv_distribution = rfm_df.withColumn("monetary_bin", 
            when(col("monetary") < 100, "0-100")
            .when(col("monetary") < 500, "100-500")
            .when(col("monetary") < 2000, "500-2000")
            .when(col("monetary") < 10000, "2000-10000")
            .otherwise("10000+")) \
            .groupBy("monetary_bin").agg(count("*").alias("customer_count"))

        # 3. Enhanced Cohort Analysis
        customer_cohorts = clean_df.groupBy("customer_id").agg(min("invoicedate").alias("first_purchase")) \
            .withColumn("cohort_month", date_format(col("first_purchase"), "yyyy-MM"))
        
        retention_base = clean_df.join(customer_cohorts, "customer_id") \
            .withColumn("relative_month", ((year(col("invoicedate")) - year(col("first_purchase"))) * 12 + (month(col("invoicedate")) - month(col("first_purchase")))).cast("int"))
        
        cohort_metrics = retention_base.groupBy("cohort_month", "relative_month").agg(
            countDistinct("customer_id").alias("customer_count"),
            sum("total_price").alias("total_revenue")
        )

        cohort_sizes = cohort_metrics.filter(col("relative_month") == 0).select(
            col("cohort_month").alias("c_m"), 
            col("customer_count").alias("base_count")
        )
        
        cohort_retention = cohort_metrics.join(cohort_sizes, cohort_metrics.cohort_month == cohort_sizes.c_m) \
            .withColumn("retention_rate", col("customer_count") / col("base_count")) \
            .withColumn("avg_revenue_per_cust", col("total_revenue") / col("customer_count")) \
            .select("cohort_month", "relative_month", "customer_count", "retention_rate", "total_revenue", "avg_revenue_per_cust")

        # 4. Product Performance
        prod_sales = clean_df.groupBy("description").agg(sum("total_price").alias("revenue"), sum("quantity").alias("quantity"))
        prod_returns = returns_df.groupBy("description").agg(sum(abs(col("quantity"))).alias("return_qty"))
        
        product_performance = prod_sales.join(prod_returns, "description", "left").fillna(0) \
            .withColumn("return_rate", col("return_qty") / (col("quantity") + col("return_qty"))) \
            .select("description", "revenue", "quantity", "return_rate")

        # 5. Operational Metrics
        total_ops = base_df.groupBy("month_year").agg(countDistinct("invoice").alias("total_orders"))
        cancel_ops = returns_df.groupBy("month_year").agg(countDistinct("invoice").alias("cancel_count"), sum(abs(col("total_price"))).alias("return_value"))
        
        operational_metrics = total_ops.join(cancel_ops, "month_year", "left").fillna(0) \
            .withColumn("cancellation_rate", col("cancel_count") / col("total_orders")) \
            .select("month_year", "cancellation_rate", "return_value", "total_orders")

        # 6. New vs Returning Customers (Monthly)
        cust_monthly = clean_df.groupBy("month_year", "customer_id").agg(count("invoice").alias("order_count"))
        new_returning = cust_monthly.join(customer_cohorts, "customer_id") \
            .withColumn("is_new", when(col("month_year") == col("cohort_month"), 1).otherwise(0)) \
            .groupBy("month_year").agg(sum("is_new").alias("new_customers"), (count("customer_id") - sum("is_new")).alias("returning_customers"))

        # 7. Seasonal Trend (Avg Monthly across all years)
        seasonal_trend = clean_df.withColumn("month", month("invoicedate")) \
            .groupBy("month").agg(avg("total_price").alias("avg_revenue")) \
            .orderBy("month")

        # 8. Geo-Distribution (Orders & Customers)
        geo_dist = clean_df.groupBy("country").agg(countDistinct("invoice").alias("total_orders"), countDistinct("customer_id").alias("total_customers"))

        # --- Compatibility & Final Metrics ---
        daily_revenue = clean_df.withColumn("date", to_date("invoicedate")).groupBy("date").agg(sum("total_price").alias("daily_revenue"), countDistinct("invoice").alias("transaction_count"))
        cluster_profiles = final_segments.groupBy("prediction").agg(expr("avg(recency)").alias("avg_recency"), expr("avg(frequency)").alias("avg_frequency"), expr("avg(monetary)").alias("avg_monetary"), count("*").alias("cluster_size"))
        top_products = product_performance.orderBy(desc("revenue")).limit(10).select(col("description"), col("revenue"))
        top_countries = clean_df.groupBy("country").agg(sum("total_price").alias("revenue")).orderBy(desc("revenue")).limit(10)
        monthly_revenue = clean_df.groupBy("month_year").agg(sum("total_price").alias("revenue")).orderBy("month_year")
        yearly_revenue = clean_df.withColumn("year", year("invoicedate")).groupBy("year").agg(sum("total_price").alias("revenue")).orderBy("year")
        dow_revenue = sales_heatmap.groupBy("day_of_week").agg(sum("revenue").alias("revenue"))
        hourly_revenue = sales_heatmap.groupBy("hour").agg(sum("revenue").alias("revenue")).orderBy("hour")

        # --- Stage 5: Writing Results to MySQL ---
        print("Writing analytical results to MySQL...")
        
        sales_heatmap.write.jdbc(url=jdbc_url, table="sales_heatmap", mode="overwrite", properties=properties)
        clv_distribution.write.jdbc(url=jdbc_url, table="clv_distribution", mode="overwrite", properties=properties)
        cohort_retention.write.jdbc(url=jdbc_url, table="cohort_retention", mode="overwrite", properties=properties)
        product_performance.write.jdbc(url=jdbc_url, table="product_performance", mode="overwrite", properties=properties)
        operational_metrics.write.jdbc(url=jdbc_url, table="operational_metrics", mode="overwrite", properties=properties)
        new_returning.write.jdbc(url=jdbc_url, table="new_returning_customers", mode="overwrite", properties=properties)
        seasonal_trend.write.jdbc(url=jdbc_url, table="seasonal_trend", mode="overwrite", properties=properties)
        geo_dist.write.jdbc(url=jdbc_url, table="geo_distribution", mode="overwrite", properties=properties)
        
        # Legacy/Compatibility
        final_segments.write.jdbc(url=jdbc_url, table="rfm_segments", mode="overwrite", properties=properties)
        daily_revenue.write.jdbc(url=jdbc_url, table="daily_revenue", mode="overwrite", properties=properties)
        cluster_profiles.write.jdbc(url=jdbc_url, table="cluster_profiles", mode="overwrite", properties=properties)
        top_products.write.jdbc(url=jdbc_url, table="top_products", mode="overwrite", properties=properties)
        top_countries.write.jdbc(url=jdbc_url, table="top_countries", mode="overwrite", properties=properties)
        monthly_revenue.write.jdbc(url=jdbc_url, table="monthly_revenue", mode="overwrite", properties=properties)
        yearly_revenue.write.jdbc(url=jdbc_url, table="yearly_revenue", mode="overwrite", properties=properties)
        dow_revenue.write.jdbc(url=jdbc_url, table="dow_revenue", mode="overwrite", properties=properties)
        hourly_revenue.write.jdbc(url=jdbc_url, table="hourly_revenue", mode="overwrite", properties=properties)
        
        print("Analytics job completed successfully.")
        
    except Exception as e:
        print(f"Error during analytics job: {e}")
        sys.exit(1)
    finally:
        spark.stop()

if __name__ == "__main__":
    run_analytics()
