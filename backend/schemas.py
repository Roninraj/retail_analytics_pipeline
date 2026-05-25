from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class SegmentSchema(BaseModel):
    customer_id: float
    recency: int
    frequency: int
    monetary: float
    segment: int

    class Config:
        from_attributes = True

class DailyRevenueSchema(BaseModel):
    date: date
    daily_revenue: float
    transaction_count: int

    class Config:
        from_attributes = True

class ClusterProfileSchema(BaseModel):
    segment: int
    avg_recency: float
    avg_frequency: float
    avg_monetary: float
    size: int

    class Config:
        from_attributes = True

class TopProductSchema(BaseModel):
    name: str
    revenue: float

    class Config:
        from_attributes = True

class TopCountrySchema(BaseModel):
    country: str
    revenue: float

    class Config:
        from_attributes = True

class MonthlyRevenueSchema(BaseModel):
    month: str
    revenue: float

    class Config:
        from_attributes = True

class YearlyRevenueSchema(BaseModel):
    year: int
    revenue: float

    class Config:
        from_attributes = True

class DOWRevenueSchema(BaseModel):
    day: str
    revenue: float

    class Config:
        from_attributes = True

class HourlyRevenueSchema(BaseModel):
    hour: int
    revenue: float

    class Config:
        from_attributes = True

# --- New Schemas ---

class SalesHeatmapSchema(BaseModel):
    day_of_week: str
    hour: int
    revenue: float

    class Config:
        from_attributes = True

class CLVDistributionSchema(BaseModel):
    monetary_bin: str
    customer_count: int

    class Config:
        from_attributes = True

class CohortRetentionSchema(BaseModel):
    cohort_month: str
    relative_month: int
    customer_count: int
    retention_rate: float
    total_revenue: float
    avg_revenue_per_cust: float

    class Config:
        from_attributes = True

class ProductPerformanceSchema(BaseModel):
    description: str
    revenue: float
    quantity: int
    return_rate: float

    class Config:
        from_attributes = True

class OperationalMetricsSchema(BaseModel):
    month_year: str
    cancellation_rate: float
    return_value: float
    total_orders: int

    class Config:
        from_attributes = True

class NewReturningSchema(BaseModel):
    month_year: str
    new_customers: int
    returning_customers: int

    class Config:
        from_attributes = True

class SeasonalTrendSchema(BaseModel):
    month: int
    avg_revenue: float

    class Config:
        from_attributes = True

class GeoDistSchema(BaseModel):
    country: str
    total_orders: int
    total_customers: int

    class Config:
        from_attributes = True

class KPISchema(BaseModel):
    total_revenue: float
    total_customers: int
    aov: float
    total_orders: int
    retention_rate: float
    cancellation_rate: float
