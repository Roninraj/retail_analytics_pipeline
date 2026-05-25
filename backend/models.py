from sqlalchemy import Column, Integer, Float, Date, String, BigInteger
try:
    from .database import Base
except ImportError:
    from database import Base

class RFMSegment(Base):
    __tablename__ = "rfm_segments"
    customer_id = Column(Float, primary_key=True, index=True)
    recency = Column(Integer)
    frequency = Column(Integer)
    monetary = Column(Float)
    prediction = Column(Integer)

class DailyRevenue(Base):
    __tablename__ = "daily_revenue"
    date = Column(Date, primary_key=True)
    daily_revenue = Column(Float)
    transaction_count = Column(BigInteger)

class ClusterProfile(Base):
    __tablename__ = "cluster_profiles"
    prediction = Column(Integer, primary_key=True)
    avg_recency = Column(Float)
    avg_frequency = Column(Float)
    avg_monetary = Column(Float)
    cluster_size = Column(BigInteger)

class TopProduct(Base):
    __tablename__ = "top_products"
    description = Column(String(255), primary_key=True)
    revenue = Column(Float)

class TopCountry(Base):
    __tablename__ = "top_countries"
    country = Column(String(100), primary_key=True)
    revenue = Column(Float)

class MonthlyRevenue(Base):
    __tablename__ = "monthly_revenue"
    month_year = Column(String(20), primary_key=True)
    revenue = Column(Float)

class YearlyRevenue(Base):
    __tablename__ = "yearly_revenue"
    year = Column(Integer, primary_key=True)
    revenue = Column(Float)

class DOWRevenue(Base):
    __tablename__ = "dow_revenue"
    day_of_week = Column(String(20), primary_key=True)
    revenue = Column(Float)

class HourlyRevenue(Base):
    __tablename__ = "hourly_revenue"
    hour = Column(Integer, primary_key=True)
    revenue = Column(Float)

# --- New Models for Comprehensive Dashboard ---

class SalesHeatmap(Base):
    __tablename__ = "sales_heatmap"
    day_of_week = Column(String(20), primary_key=True)
    hour = Column(Integer, primary_key=True)
    revenue = Column(Float)

class CLVDistribution(Base):
    __tablename__ = "clv_distribution"
    monetary_bin = Column(String(50), primary_key=True)
    customer_count = Column(BigInteger)

class CohortRetention(Base):
    __tablename__ = "cohort_retention"
    cohort_month = Column(String(20), primary_key=True)
    relative_month = Column(Integer, primary_key=True)
    customer_count = Column(BigInteger)
    retention_rate = Column(Float)
    total_revenue = Column(Float)
    avg_revenue_per_cust = Column(Float)

class ProductPerformance(Base):
    __tablename__ = "product_performance"
    description = Column(String(255), primary_key=True)
    revenue = Column(Float)
    quantity = Column(BigInteger)
    return_rate = Column(Float)

class OperationalMetrics(Base):
    __tablename__ = "operational_metrics"
    month_year = Column(String(20), primary_key=True)
    cancellation_rate = Column(Float)
    return_value = Column(Float)
    total_orders = Column(BigInteger)

class NewReturningCustomers(Base):
    __tablename__ = "new_returning_customers"
    month_year = Column(String(20), primary_key=True)
    new_customers = Column(Integer)
    returning_customers = Column(Integer)

class SeasonalTrend(Base):
    __tablename__ = "seasonal_trend"
    month = Column(Integer, primary_key=True)
    avg_revenue = Column(Float)

class GeoDistribution(Base):
    __tablename__ = "geo_distribution"
    country = Column(String(100), primary_key=True)
    total_orders = Column(BigInteger)
    total_customers = Column(BigInteger)
