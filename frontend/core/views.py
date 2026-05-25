import os
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.utils
from django.shortcuts import render
import plotly.io as pio
import base64
import numpy as np

API_URL = os.getenv('API_URL')

def empty_fig(title="Data Not Available"):
    """Helper to return a styled empty figure."""
    fig = go.Figure()
    fig.add_annotation(text="No data available for this metric.",
                  xref="paper", yref="paper",
                  showarrow=False, font=dict(size=16))
    fig.update_layout(title=title, template="plotly_white")
    return fig

def safe_fetch_json(url):
    """Safely fetch JSON from an API endpoint, returning empty list on error."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        print(f"API Error at {url}: {response.status_code}")
        return []
    except Exception as e:
        print(f"Connection error to {url}: {e}")
        return []

def dashboard_view(request):
    context = {}
    try:
        # Dynamically determine the API_URL if not explicitly set in env
        api_url = API_URL
        if not api_url:
            scheme = 'https' if request.is_secure() or request.headers.get('x-forwarded-proto') == 'https' else 'http'
            api_url = f"{scheme}://{request.get_host()}"

        # --- 1. Fetch ALL Data from API ---
        kpis = safe_fetch_json(f"{api_url}/api/kpis")
        if not kpis:
            kpis = {"total_revenue": 0, "total_customers": 0, "total_orders": 0, "aov": 0, "retention_rate": 0, "cancellation_rate": 0}
            
        revenue_data = safe_fetch_json(f"{api_url}/api/revenue")
        segment_data = safe_fetch_json(f"{api_url}/api/segments")
        top_products_raw = safe_fetch_json(f"{api_url}/api/top-products")
        top_countries = safe_fetch_json(f"{api_url}/api/top-countries")
        monthly_rev = safe_fetch_json(f"{api_url}/api/monthly-revenue")
        
        sales_heatmap_raw = safe_fetch_json(f"{api_url}/api/sales-heatmap")
        clv_dist_raw = safe_fetch_json(f"{api_url}/api/clv-distribution")
        cohort_raw = safe_fetch_json(f"{api_url}/api/cohort-retention")
        prod_perf_raw = safe_fetch_json(f"{api_url}/api/product-performance")
        ops_raw = safe_fetch_json(f"{api_url}/api/operational-metrics")
        
        new_returning_raw = safe_fetch_json(f"{api_url}/api/new-returning-customers")
        seasonal_raw = safe_fetch_json(f"{api_url}/api/seasonal-trend")
        geo_dist_raw = safe_fetch_json(f"{api_url}/api/geo-distribution")

        # --- 2. Build Visualizations ---
        
        # SECTION A: EXECUTIVE SUMMARY
        df_rev = pd.DataFrame(revenue_data)
        if not df_rev.empty:
            fig_revenue_trend = px.line(x=df_rev['date'].tolist(), 
                                        y=df_rev['daily_revenue'].tolist(), 
                                        title='Daily Revenue Trend', template='plotly_white',
                                        labels={'x': 'Date', 'y': 'Revenue'})
            
            fig_rev_orders = make_subplots(specs=[[{"secondary_y": True}]])
            fig_rev_orders.add_trace(go.Scatter(x=df_rev['date'].tolist(), y=df_rev['daily_revenue'].tolist(), name="Revenue", line=dict(color="#3b82f6")), secondary_y=False)
            fig_rev_orders.add_trace(go.Scatter(x=df_rev['date'].tolist(), y=df_rev['transaction_count'].tolist(), name="Orders", line=dict(color="#10b981", dash='dot')), secondary_y=True)
            fig_rev_orders.update_layout(title="Revenue vs Orders Relationship", template="plotly_white")
        else:
            fig_revenue_trend = empty_fig("Daily Revenue Trend")
            fig_rev_orders = empty_fig("Revenue vs Orders Relationship")

        # SECTION B: SALES PERFORMANCE
        df_heatmap = pd.DataFrame(sales_heatmap_raw)
        if not df_heatmap.empty:
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            df_heatmap['day_of_week'] = df_heatmap['day_of_week'].str.title()
            df_heatmap_pivot = df_heatmap.pivot(index='day_of_week', columns='hour', values='revenue').reindex(days_order).fillna(0)
            fig_peak_hours = px.imshow(df_heatmap_pivot.values.tolist(), 
                                    labels=dict(x="Hour of Day", y="Day of Week", color="Revenue"),
                                    x=df_heatmap_pivot.columns.tolist(),
                                    y=df_heatmap_pivot.index.tolist(),
                                    title="Peak Shopping Hours (Revenue Velocity)", aspect="auto")
        else:
            fig_peak_hours = empty_fig("Peak Shopping Hours")

        # SECTION C: CUSTOMER ANALYTICS
        df_cohort = pd.DataFrame(cohort_raw)
        if not df_cohort.empty and 'cohort_month' in df_cohort.columns:
            df_cohort_pivot = df_cohort.pivot(index='cohort_month', columns='relative_month', values='retention_rate').fillna(0)
            df_cohort_pivot.index = df_cohort_pivot.index.astype(str)
            df_cohort_pivot = df_cohort_pivot.sort_index(ascending=False)
            
            fig_cohort_ret = px.imshow(df_cohort_pivot.values.tolist(), 
                                labels=dict(x="Months Since First Purchase", y="Cohort Month", color="Ret %"),
                                x=df_cohort_pivot.columns.tolist(),
                                y=df_cohort_pivot.index.tolist(),
                                title="Customer Retention Cohort Analysis", aspect="auto", color_continuous_scale="Blues")

            fig_cohort_rev = px.line(df_cohort, x='relative_month', y='avg_revenue_per_cust', color='cohort_month',
                                    title="Cohort Revenue Evolution (Avg Spend per Customer)",
                                    labels={'relative_month': 'Months Since First Purchase', 'avg_revenue_per_cust': 'Avg Revenue ($)', 'cohort_month': 'Cohort'})
        else:
            fig_cohort_ret = empty_fig("Customer Retention Cohort Analysis")
            fig_cohort_rev = empty_fig("Cohort Revenue Evolution")
        
        df_seg = pd.DataFrame(segment_data)
        if not df_seg.empty:
            df_seg['segment'] = df_seg['segment'].astype(str)
            df_seg['monetary_size'] = df_seg['monetary'].clip(lower=1)
            fig_rfm = px.scatter(x=df_seg['recency'].tolist(), 
                                y=df_seg['frequency'].tolist(), 
                                size=df_seg['monetary_size'].tolist(), 
                                color=df_seg['segment'].tolist(), 
                                title="Customer Segmentation (RFM Bubble Chart)",
                                labels={'x': 'Recency', 'y': 'Frequency', 'color': 'Segment', 'size': 'Monetary'})
        else:
            fig_rfm = empty_fig("Customer Segmentation")

        df_clv = pd.DataFrame(clv_dist_raw)
        if not df_clv.empty:
            fig_clv = px.bar(x=df_clv['monetary_bin'].astype(str).tolist(), 
                            y=df_clv['customer_count'].tolist(), 
                            title='Customer Lifetime Value (CLV) Distribution',
                            category_orders={"x": ["0-100", "100-500", "500-2000", "2000-10000", "10000+"]},
                            labels={'x': 'CLV Range ($)', 'y': 'Count of Customers'})
        else:
            fig_clv = empty_fig("CLV Distribution")

        # SECTION D: PRODUCT INTELLIGENCE
        df_top_prod = pd.DataFrame(top_products_raw)
        if not df_top_prod.empty:
            df_top_prod = df_top_prod.sort_values('revenue', ascending=True).tail(10)
            fig_top_products = px.bar(x=df_top_prod['revenue'].tolist(), 
                                    y=df_top_prod['name'].astype(str).tolist(), 
                                    orientation='h', title='Top 10 Products by Revenue',
                                    color=df_top_prod['revenue'].tolist(), 
                                    color_continuous_scale='Viridis',
                                    labels={'x': 'Revenue', 'y': 'Product'})
        else:
            fig_top_products = empty_fig("Top Products")

        df_prod = pd.DataFrame(prod_perf_raw)
        if not df_prod.empty:
            df_prod = df_prod.sort_values('revenue', ascending=False)
            df_prod['cumulative_revenue'] = df_prod['revenue'].cumsum()
            df_prod['revenue_pct'] = 100 * df_prod['cumulative_revenue'] / df_prod['revenue'].sum()
            fig_pareto = go.Figure()
            fig_pareto.add_trace(go.Bar(x=df_prod['description'][:20].tolist(), y=df_prod['revenue'][:20].tolist(), name="Revenue"))
            fig_pareto.add_trace(go.Scatter(x=df_prod['description'][:20].tolist(), y=df_prod['revenue_pct'][:20].tolist(), name="Cumulative %", yaxis="y2"))
            fig_pareto.update_layout(title="Product Revenue Concentration (Pareto 80/20)", yaxis2=dict(overlaying="y", side="right", range=[0, 100]), template='plotly_white')

            df_prod_risk = df_prod.head(50).copy()
            df_prod_risk['return_rate'] = df_prod_risk['return_rate'].fillna(0)
            fig_return_risk = px.scatter(x=df_prod_risk['quantity'].tolist(), 
                                        y=df_prod_risk['revenue'].tolist(), 
                                        size=df_prod_risk['return_rate'].tolist(), 
                                        color=df_prod_risk['return_rate'].tolist(),
                                        hover_name=df_prod_risk['description'].tolist(), 
                                        title="Product Return Risk (Size/Color = Return Rate)",
                                        labels={'x': 'Quantity', 'y': 'Revenue', 'color': 'Return Rate', 'size': 'Return Rate'})
        else:
            fig_pareto = empty_fig("Revenue Concentration (Pareto)")
            fig_return_risk = empty_fig("Product Return Risk")

        # SECTION E: GEOSPATIAL ANALYSIS
        df_geo = pd.DataFrame(geo_dist_raw)
        if not df_geo.empty:
            df_geo['country'] = df_geo['country'].astype(str)
            fig_geo_map = px.choropleth(locations=df_geo["country"].tolist(), 
                                        locationmode='country names', 
                                        color=df_geo["total_orders"].tolist(),
                                        hover_name=df_geo["country"].tolist(), 
                                        title="Global Geographic Performance (Order Volume)",
                                        color_continuous_scale=px.colors.sequential.Plasma,
                                        labels={'color': 'Total Orders', 'locations': 'Country'})
        else:
            fig_geo_map = empty_fig("Geographic Performance")

        # SECTION F: OPERATIONS & RETURNS
        df_ops = pd.DataFrame(ops_raw)
        if not df_ops.empty:
            total_rev = pd.DataFrame(monthly_rev)['revenue'].sum() if monthly_rev else 0
            total_returns = df_ops['return_value'].sum()
            net_rev = total_rev - total_returns
            fig_waterfall = go.Figure(go.Waterfall(
                name = "Revenue Leakage", orientation = "v",
                measure = ["relative", "relative", "total"],
                x = ["Gross Revenue", "Returns/Cancellations", "Net Revenue"],
                textposition = "outside",
                text = [f"${total_rev:,.0f}", f"-${total_returns:,.0f}", f"${net_rev:,.0f}"],
                y = [total_rev, -total_returns, net_rev],
                connector = {"line":{"color":"rgb(63, 63, 63)"}},
            ))
            fig_waterfall.update_layout(title = "Revenue Leakage & Returns Analysis", template='plotly_white')

            fig_cancellation = px.line(x=df_ops['month_year'].tolist(), 
                                    y=df_ops['cancellation_rate'].tolist(), 
                                    title='Monthly Cancellation Rate Monitoring',
                                    markers=True, line_shape='spline',
                                    labels={'x': 'Month-Year', 'y': 'Cancellation Rate'})
        else:
            fig_waterfall = empty_fig("Revenue Leakage Analysis")
            fig_cancellation = empty_fig("Cancellation Monitoring")

        # --- 3. Package Plots ---
        def fig_to_json(fig):
            """Use Plotly's built-in JSON conversion for reliability."""
            return fig.to_json()

        context = {
            'kpis': kpis,
            'exec_plots': {
                'trend': fig_to_json(fig_revenue_trend),
                'relationship': fig_to_json(fig_rev_orders),
            },
            'sales_plots': {
                'peak_hours': fig_to_json(fig_peak_hours),
            },
            'cust_plots': {
                'retention': fig_to_json(fig_cohort_ret),
                'revenue_evo': fig_to_json(fig_cohort_rev),
                'segmentation': fig_to_json(fig_rfm),
                'clv': fig_to_json(fig_clv),
            },
            'prod_plots': {
                'top_analysis': fig_to_json(fig_top_products),
                'concentration': fig_to_json(fig_pareto),
                'return_risk': fig_to_json(fig_return_risk),
            },
            'geo_plots': {
                'map': fig_to_json(fig_geo_map),
            },
            'ops_plots': {
                'leakage': fig_to_json(fig_waterfall),
                'cancellation': fig_to_json(fig_cancellation),
            }
        }
    except Exception as e:
        print(f"Error building analytics dashboard: {e}")
        import traceback
        traceback.print_exc()
        context['error'] = str(e)

    return render(request, 'core/dashboard.html', context)
