import streamlit as st
import pandas as pd
import plotly.express as px 
from data_loader import load_data  # Import your centralized load_data function

st.set_page_config(page_title="Sales Trends", page_icon="📊", layout="wide")

# Load data
df = load_data()

st.title("📊 Sales Trends Analysis")
st.markdown("*Seasonal patterns and growth trends*")

# Monthly trends
monthly_data = df.groupby('month_year').agg({
    'revenue': 'sum',
    'quantity': 'sum',
    'profit': 'sum'
}).reset_index()
monthly_data['month_year'] = pd.to_datetime(monthly_data['month_year'])
monthly_data['growth_rate'] = monthly_data['revenue'].pct_change() * 100

# Revenue trend
fig_line = px.line(monthly_data, x='month_year', y='revenue',
                  title="Monthly Revenue Trend",
                  labels={'month_year': 'Month', 'revenue': 'Revenue ($)'})
fig_line.add_scatter(x=monthly_data['month_year'], y=monthly_data['revenue'], 
                    mode='markers', name='Monthly Revenue')
st.plotly_chart(fig_line, use_container_width=True)

# Growth rate
fig_growth = px.bar(monthly_data, x='month_year', y='growth_rate',
                   title="Month-over-Month Growth Rate (%)",
                   labels={'month_year': 'Month', 'growth_rate': 'Growth Rate (%)'})
st.plotly_chart(fig_growth, use_container_width=True)

# Seasonal analysis
df['month'] = pd.to_datetime(df['month_year']).dt.month
seasonal_data = df.groupby('month')['revenue'].sum().reset_index()
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
seasonal_data['month_name'] = [month_names[m-1] for m in seasonal_data['month']]

fig_seasonal = px.bar(seasonal_data, x='month_name', y='revenue',
                     title="Seasonal Sales Pattern",
                     labels={'month_name': 'Month', 'revenue': 'Total Revenue ($)'},
                     color='revenue',
                     color_continuous_scale='viridis')
st.plotly_chart(fig_seasonal, use_container_width=True)

# Quarterly comparison
df['quarter'] = pd.to_datetime(df['month_year']).dt.quarter
df['year'] = pd.to_datetime(df['month_year']).dt.year
quarterly_data = df.groupby(['year', 'quarter'])['revenue'].sum().reset_index()
quarterly_data['quarter_label'] = quarterly_data['year'].astype(str) + ' Q' + quarterly_data['quarter'].astype(str)

fig_quarterly = px.bar(quarterly_data, x='quarter_label', y='revenue',
                      title="Quarterly Revenue Comparison",
                      labels={'quarter_label': 'Quarter', 'revenue': 'Revenue ($)'})
st.plotly_chart(fig_quarterly, use_container_width=True)

# Key insights
st.subheader("🔍 Key Insights")
peak_month = seasonal_data.loc[seasonal_data['revenue'].idxmax(), 'month_name']
peak_revenue = seasonal_data['revenue'].max()
avg_growth = monthly_data['growth_rate'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Peak Sales Month", peak_month)
with col2:
    st.metric("Peak Month Revenue", f"${peak_revenue:,.0f}")
with col3:
    st.metric("Avg Monthly Growth", f"{avg_growth:.1f}%")

st.markdown("**💡 Recommendation:** Use these trends to plan inventory levels seasonally and identify the best times for promotions or new product launches.")