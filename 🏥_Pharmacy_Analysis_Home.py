import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data  # Import your centralized load_data function

st.set_page_config(
    page_title="Pharmacy Startup Analysis Dashboard",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Pharmacy Startup Analysis Dashboard")
st.markdown("**Data-driven insights for your pharmacy startup - What to stock first to maximize revenue**")

# File uploader
uploaded_file = st.file_uploader("Upload your pharmacy data CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if 'month_year' in df.columns:
        df['month_year'] = pd.to_datetime(df['month_year'], errors='coerce')
    st.session_state['uploaded_df'] = df
    st.success("File uploaded and data loaded successfully!")

# Load data via centralized function
df = load_data()

if df is not None:
    total_revenue = df['revenue'].sum()
    total_products = df['product_code'].nunique()
    total_months = df['month_year'].nunique() if 'month_year' in df.columns else 'N/A'
    avg_margin = df['margin_pct'].mean()

    st.header("📈 Business Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col2:
        st.metric("Unique Products", f"{total_products:,}")
    with col3:
        st.metric("Analysis Period", f"{total_months} months")
    with col4:
        st.metric("Avg Profit Margin", f"{avg_margin:.1f}%")

    st.subheader("📅 Monthly Revenue Trends")
    if 'month_year' in df.columns:
        monthly_revenue = df.groupby('month_year')['revenue'].sum().reset_index()
        fig_revenue = px.line(monthly_revenue, x='month_year', y='revenue',
                              title="Monthly Revenue Trend",
                              labels={'month_year': 'Month', 'revenue': 'Revenue ($)'})
        fig_revenue.update_traces(line_color='#1f77b4', line_width=3)
        st.plotly_chart(fig_revenue, use_container_width=True)
    else:
        st.info("No 'month_year' column found for revenue trend.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Top Products by Revenue")
        top_products_revenue = df.groupby(['product_code', 'product_name']).agg({
            'revenue': 'sum',
            'quantity': 'sum',
            'margin_pct': 'mean'
        }).sort_values('revenue', ascending=False).head(10)

        fig_bar = px.bar(x=top_products_revenue.index.get_level_values(1),
                         y=top_products_revenue['revenue'],
                         title="Top 10 Products by Revenue",
                         labels={'x': 'Product', 'y': 'Total Revenue ($)'})
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("📊 Quantity vs Revenue")
        product_summary = df.groupby('product_code').agg({
            'quantity': 'sum',
            'revenue': 'sum',
            'margin_pct': 'mean',
            'product_name': 'first'
        }).reset_index().head(50)

        fig_scatter = px.scatter(product_summary, x='quantity', y='revenue',
                                 color='margin_pct',
                                 hover_data=['product_name'],
                                 title="Product Performance: Quantity vs Revenue",
                                 color_continuous_scale='viridis')
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    st.markdown("**💡 Use the sidebar to navigate to different analysis pages for detailed insights**")
    st.markdown("**📊 Each page provides specific recommendations for your pharmacy startup**")

    st.markdown("---")
    st.markdown("**💡 Dashboard built for pharmacy startup analysis | Data-driven inventory decisions**")

else:
    st.info("No data available yet. Please upload a CSV file above to get started.")