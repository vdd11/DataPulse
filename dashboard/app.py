import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR / "src"))

from analytics import (
    get_sales_data,
    get_kpis,
    monthly_revenue,
    revenue_by_category,
    revenue_by_region,
    top_products,
    top_customers,
    customer_segments
)

from forecasting import forecast_revenue

st.set_page_config(
    page_title="DataPulse Business Analytics",
    layout="wide"
)

st.title("DataPulse: Business Intelligence & Sales Analytics Platform")

st.markdown(
    """
    DataPulse is an interactive business analytics dashboard that analyzes revenue,
    profit, customer behavior, product performance, and sales forecasting.
    """
)

df = get_sales_data()
df["order_date"] = pd.to_datetime(df["order_date"])

st.sidebar.header("Filters")

region_filter = st.sidebar.multiselect(
    "Region",
    options=sorted(df["region"].unique()),
    default=sorted(df["region"].unique())
)

category_filter = st.sidebar.multiselect(
    "Category",
    options=sorted(df["category"].unique()),
    default=sorted(df["category"].unique())
)

segment_filter = st.sidebar.multiselect(
    "Customer Segment",
    options=sorted(df["segment"].unique()),
    default=sorted(df["segment"].unique())
)

date_range = st.sidebar.date_input(
    "Date Range",
    value=[df["order_date"].min(), df["order_date"].max()]
)

filtered_df = df[
    (df["region"].isin(region_filter)) &
    (df["category"].isin(category_filter)) &
    (df["segment"].isin(segment_filter))
]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["order_date"] >= pd.to_datetime(start_date)) &
        (filtered_df["order_date"] <= pd.to_datetime(end_date))
    ]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Overview",
    "Sales Analytics",
    "Customer Analytics",
    "Product Analytics",
    "Forecasting"
])

with tab1:
    st.header("Executive Overview")

    total_revenue = filtered_df["sales"].sum()
    total_profit = filtered_df["profit"].sum()
    total_orders = filtered_df["order_id"].nunique()
    total_customers = filtered_df["customer_id"].nunique()
    profit_margin = total_profit / total_revenue if total_revenue > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Revenue", f"${total_revenue:,.0f}")
    col2.metric("Profit", f"${total_profit:,.0f}")
    col3.metric("Orders", f"{total_orders:,}")
    col4.metric("Customers", f"{total_customers:,}")
    col5.metric("Profit Margin", f"{profit_margin:.1%}")

    monthly = filtered_df.copy()
    monthly["month"] = monthly["order_date"].dt.to_period("M").astype(str)

    monthly_summary = monthly.groupby("month", as_index=False).agg({
        "sales": "sum",
        "profit": "sum"
    })

    fig = px.line(
        monthly_summary,
        x="month",
        y="sales",
        title="Monthly Revenue Trend",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

    col6, col7 = st.columns(2)

    with col6:
        category_summary = filtered_df.groupby("category", as_index=False).agg({
            "sales": "sum",
            "profit": "sum"
        })

        fig = px.bar(
            category_summary,
            x="category",
            y="sales",
            title="Revenue by Category"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col7:
        region_summary = filtered_df.groupby("region", as_index=False).agg({
            "sales": "sum",
            "profit": "sum"
        })

        fig = px.bar(
            region_summary,
            x="region",
            y="sales",
            title="Revenue by Region"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Sales Analytics")

    monthly = filtered_df.copy()
    monthly["month"] = monthly["order_date"].dt.to_period("M").astype(str)

    monthly_summary = monthly.groupby("month", as_index=False).agg({
        "sales": "sum",
        "profit": "sum",
        "order_id": "nunique"
    })

    monthly_summary = monthly_summary.rename(columns={
        "sales": "Revenue",
        "profit": "Profit",
        "order_id": "Orders"
    })

    fig = px.line(
        monthly_summary,
        x="month",
        y=["Revenue", "Profit"],
        title="Monthly Revenue and Profit"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        monthly_summary,
        x="month",
        y="Orders",
        title="Monthly Order Volume"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Sales Table")
    st.dataframe(monthly_summary, use_container_width=True)

with tab3:
    st.header("Customer Analytics")

    customer_summary = filtered_df.groupby("customer_id", as_index=False).agg({
        "order_id": "nunique",
        "sales": "sum",
        "profit": "sum"
    })

    customer_summary = customer_summary.rename(columns={
        "order_id": "Orders",
        "sales": "Revenue",
        "profit": "Profit"
    })

    customer_summary["Customer Value Segment"] = pd.qcut(
        customer_summary["Revenue"],
        q=3,
        labels=["Low Value", "Medium Value", "High Value"]
    )

    col1, col2 = st.columns(2)

    with col1:
        segment_summary = filtered_df.groupby("segment", as_index=False).agg({
            "sales": "sum",
            "profit": "sum",
            "customer_id": "nunique"
        })

        fig = px.pie(
            segment_summary,
            names="segment",
            values="sales",
            title="Revenue by Customer Segment"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        value_counts = customer_summary["Customer Value Segment"].value_counts().reset_index()
        value_counts.columns = ["Customer Value Segment", "Count"]

        fig = px.bar(
            value_counts,
            x="Customer Value Segment",
            y="Count",
            title="Customer Value Segmentation"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Customers")
    st.dataframe(
        customer_summary.sort_values("Revenue", ascending=False).head(20),
        use_container_width=True
    )

with tab4:
    st.header("Product Analytics")

    product_summary = filtered_df.groupby(["product", "category"], as_index=False).agg({
        "quantity": "sum",
        "sales": "sum",
        "profit": "sum"
    })

    product_summary["profit_margin"] = product_summary["profit"] / product_summary["sales"]

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            product_summary.sort_values("sales", ascending=False).head(10),
            x="product",
            y="sales",
            color="category",
            title="Top 10 Products by Revenue"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            product_summary.sort_values("profit_margin", ascending=False).head(10),
            x="product",
            y="profit_margin",
            color="category",
            title="Top 10 Products by Profit Margin"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Product Performance Table")
    st.dataframe(
        product_summary.sort_values("sales", ascending=False),
        use_container_width=True
    )

with tab5:
    st.header("Revenue Forecasting")

    monthly = filtered_df.copy()
    monthly["month"] = monthly["order_date"].dt.to_period("M").astype(str)

    monthly_summary = monthly.groupby("month", as_index=False).agg({
        "sales": "sum"
    })

    monthly_summary = monthly_summary.rename(columns={
        "sales": "revenue"
    })

    forecast_df = forecast_revenue(monthly_summary, periods=6)

    monthly_summary["month"] = pd.to_datetime(monthly_summary["month"])
    forecast_df["month"] = pd.to_datetime(forecast_df["month"])

    fig = px.line(
        monthly_summary,
        x="month",
        y="revenue",
        title="Historical Revenue"
    )

    fig.add_scatter(
        x=forecast_df["month"],
        y=forecast_df["forecasted_revenue"],
        mode="lines+markers",
        name="Forecasted Revenue"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Next 6 Months Forecast")
    forecast_display = forecast_df.copy()
    forecast_display["month"] = forecast_display["month"].dt.strftime("%Y-%m")
    forecast_display["forecasted_revenue"] = forecast_display["forecasted_revenue"].round(2)

    st.dataframe(forecast_display, use_container_width=True)
