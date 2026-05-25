from sqlalchemy.orm import Session
from sqlalchemy import func
try:
    from . import models
except ImportError:
    import models

class AnalyticsService:
    @staticmethod
    def get_all_segments(db: Session):
        return db.query(models.RFMSegment).all()

    @staticmethod
    def get_daily_revenue(db: Session):
        return db.query(models.DailyRevenue).order_by(models.DailyRevenue.date).all()

    @staticmethod
    def get_cluster_profiles(db: Session):
        return db.query(models.ClusterProfile).all()

    @staticmethod
    def get_top_products(db: Session):
        return db.query(models.TopProduct).order_by(models.TopProduct.revenue.desc()).all()

    @staticmethod
    def get_top_countries(db: Session):
        return db.query(models.TopCountry).order_by(models.TopCountry.revenue.desc()).all()

    @staticmethod
    def get_monthly_revenue(db: Session):
        return db.query(models.MonthlyRevenue).order_by(models.MonthlyRevenue.month_year).all()

    @staticmethod
    def get_yearly_revenue(db: Session):
        return db.query(models.YearlyRevenue).order_by(models.YearlyRevenue.year).all()

    @staticmethod
    def get_dow_revenue(db: Session):
        return db.query(models.DOWRevenue).all()

    @staticmethod
    def get_hourly_revenue(db: Session):
        return db.query(models.HourlyRevenue).order_by(models.HourlyRevenue.hour).all()

    @staticmethod
    def get_sales_heatmap(db: Session):
        return db.query(models.SalesHeatmap).all()

    @staticmethod
    def get_clv_distribution(db: Session):
        return db.query(models.CLVDistribution).all()

    @staticmethod
    def get_cohort_retention(db: Session):
        return db.query(models.CohortRetention).order_by(models.CohortRetention.cohort_month, models.CohortRetention.relative_month).all()

    @staticmethod
    def get_product_performance(db: Session):
        return db.query(models.ProductPerformance).order_by(models.ProductPerformance.revenue.desc()).all()

    @staticmethod
    def get_operational_metrics(db: Session):
        return db.query(models.OperationalMetrics).order_by(models.OperationalMetrics.month_year).all()

    @staticmethod
    def get_new_returning_customers(db: Session):
        return db.query(models.NewReturningCustomers).order_by(models.NewReturningCustomers.month_year).all()

    @staticmethod
    def get_seasonal_trend(db: Session):
        return db.query(models.SeasonalTrend).order_by(models.SeasonalTrend.month).all()

    @staticmethod
    def get_geo_distribution(db: Session):
        return db.query(models.GeoDistribution).all()

    @staticmethod
    def get_global_kpis(db: Session):
        # Base metrics from daily_revenue
        rev_data = db.query(
            func.sum(models.DailyRevenue.daily_revenue),
            func.sum(models.DailyRevenue.transaction_count)
        ).first()
        total_rev = float(rev_data[0] or 0)
        total_orders = float(rev_data[1] or 0)
        
        total_customers = db.query(models.RFMSegment).count()
        
        # Operational metrics for rates
        ops_data = db.query(
            func.avg(models.OperationalMetrics.cancellation_rate)
        ).first()
        avg_cancellation = float(ops_data[0] or 0)
        
        # Retention Rate (approximation from cohort)
        retention = db.query(func.avg(models.CohortRetention.retention_rate)).filter(models.CohortRetention.relative_month > 0).scalar() or 0

        aov = total_rev / total_orders if total_orders > 0 else 0
        
        return {
            "total_revenue": round(total_rev, 2),
            "total_customers": total_customers,
            "total_orders": int(total_orders),
            "aov": round(aov, 2),
            "retention_rate": round(float(retention) * 100, 2), # Convert to percentage
            "cancellation_rate": round(avg_cancellation * 100, 4) # Convert to percentage
        }
