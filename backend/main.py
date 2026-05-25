import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
try:
    from . import schemas, database, service
except ImportError:
    import schemas, database, service

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Industrial Retail Analytics API",
    description="Scalable, asynchronous API for serving deep retail insights.",
    version="2.0.0"
)

# Initialize Service
analytics_service = service.AnalyticsService()

@app.get("/health", tags=["Management"])
async def health_check():
    """Kubernetes health check probe."""
    return {"status": "healthy"}

@app.get("/api/segments", response_model=List[schemas.SegmentSchema], tags=["Analytics"])
async def get_segments(db: Session = Depends(database.get_db)):
    logger.info("Fetching all customer segments")
    try:
        segments = analytics_service.get_all_segments(db)
        return [schemas.SegmentSchema(
            customer_id=s.customer_id,
            recency=s.recency,
            frequency=s.frequency,
            monetary=s.monetary,
            segment=s.prediction
        ) for s in segments]
    except Exception as e:
        logger.error(f"Error fetching segments: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/revenue", response_model=List[schemas.DailyRevenueSchema], tags=["Analytics"])
async def get_revenue(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_daily_revenue(db)
    except Exception as e:
        logger.error(f"Error fetching revenue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/cluster-profiles", response_model=List[schemas.ClusterProfileSchema], tags=["Analytics"])
async def get_cluster_profiles(db: Session = Depends(database.get_db)):
    try:
        profiles = analytics_service.get_cluster_profiles(db)
        return [schemas.ClusterProfileSchema(
            segment=p.prediction,
            avg_recency=p.avg_recency,
            avg_frequency=p.avg_frequency,
            avg_monetary=p.avg_monetary,
            size=p.cluster_size
        ) for p in profiles]
    except Exception as e:
        logger.error(f"Error fetching profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/top-products", response_model=List[schemas.TopProductSchema], tags=["Analytics"])
async def get_top_products(db: Session = Depends(database.get_db)):
    try:
        products = analytics_service.get_top_products(db)
        return [schemas.TopProductSchema(name=p.description, revenue=p.revenue) for p in products]
    except Exception as e:
        logger.error(f"Error fetching top products: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/top-countries", response_model=List[schemas.TopCountrySchema], tags=["Analytics"])
async def get_top_countries(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_top_countries(db)
    except Exception as e:
        logger.error(f"Error fetching top countries: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/monthly-revenue", response_model=List[schemas.MonthlyRevenueSchema], tags=["Analytics"])
async def get_monthly_revenue(db: Session = Depends(database.get_db)):
    try:
        monthly = analytics_service.get_monthly_revenue(db)
        return [schemas.MonthlyRevenueSchema(month=m.month_year, revenue=m.revenue) for m in monthly]
    except Exception as e:
        logger.error(f"Error fetching monthly revenue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/yearly-revenue", response_model=List[schemas.YearlyRevenueSchema], tags=["Analytics"])
async def get_yearly_revenue(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_yearly_revenue(db)
    except Exception as e:
        logger.error(f"Error fetching yearly revenue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/dow-revenue", response_model=List[schemas.DOWRevenueSchema], tags=["Analytics"])
async def get_dow_revenue(db: Session = Depends(database.get_db)):
    try:
        dow = analytics_service.get_dow_revenue(db)
        return [schemas.DOWRevenueSchema(day=d.day_of_week, revenue=d.revenue) for d in dow]
    except Exception as e:
        logger.error(f"Error fetching day of week revenue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/hourly-revenue", response_model=List[schemas.HourlyRevenueSchema], tags=["Analytics"])
async def get_hourly_revenue(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_hourly_revenue(db)
    except Exception as e:
        logger.error(f"Error fetching hourly revenue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/sales-heatmap", response_model=List[schemas.SalesHeatmapSchema], tags=["Analytics"])
async def get_sales_heatmap(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_sales_heatmap(db)
    except Exception as e:
        logger.error(f"Error fetching sales heatmap: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/clv-distribution", response_model=List[schemas.CLVDistributionSchema], tags=["Analytics"])
async def get_clv_distribution(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_clv_distribution(db)
    except Exception as e:
        logger.error(f"Error fetching CLV distribution: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/cohort-retention", response_model=List[schemas.CohortRetentionSchema], tags=["Analytics"])
async def get_cohort_retention(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_cohort_retention(db)
    except Exception as e:
        logger.error(f"Error fetching cohort retention: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/product-performance", response_model=List[schemas.ProductPerformanceSchema], tags=["Analytics"])
async def get_product_performance(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_product_performance(db)
    except Exception as e:
        logger.error(f"Error fetching product performance: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/operational-metrics", response_model=List[schemas.OperationalMetricsSchema], tags=["Analytics"])
async def get_operational_metrics(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_operational_metrics(db)
    except Exception as e:
        logger.error(f"Error fetching operational metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/new-returning-customers", response_model=List[schemas.NewReturningSchema], tags=["Analytics"])
async def get_new_returning_customers(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_new_returning_customers(db)
    except Exception as e:
        logger.error(f"Error fetching new returning customers: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/seasonal-trend", response_model=List[schemas.SeasonalTrendSchema], tags=["Analytics"])
async def get_seasonal_trend(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_seasonal_trend(db)
    except Exception as e:
        logger.error(f"Error fetching seasonal trend: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/geo-distribution", response_model=List[schemas.GeoDistSchema], tags=["Analytics"])
async def get_geo_distribution(db: Session = Depends(database.get_db)):
    try:
        return analytics_service.get_geo_distribution(db)
    except Exception as e:
        logger.error(f"Error fetching geo distribution: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/kpis", response_model=schemas.KPISchema, tags=["Analytics"])
async def get_kpis(db: Session = Depends(database.get_db)):
    try:
        kpis = analytics_service.get_global_kpis(db)
        return schemas.KPISchema(**kpis)
    except Exception as e:
        logger.error(f"Error fetching KPIs: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
