import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data  # Import your centralized load_data function

st.set_page_config(page_title="Revenue Leaders", page_icon="💰", layout="wide")

# Load data
df = load_data()

st.title("💰 Top Revenue Generators")
st.markdown("*Your biggest money makers - prioritize these for maximum revenue*")

revenue_leaders = df.groupby(['product_code', 'product_name']).agg({
    'revenue': 'sum',
    'quantity': 'sum', 
    'profit': 'sum',
    'margin_pct': 'mean',
    'month_year': 'nunique'
}).sort_values('revenue', ascending=False).head(20)

revenue_leaders['avg_monthly_revenue'] = (revenue_leaders['revenue'] / revenue_leaders['month_year']).round(0)
revenue_leaders['avg_monthly_qty'] = (revenue_leaders['quantity'] / revenue_leaders['month_year']).round(1)

# Display table
display_df = revenue_leaders[['revenue', 'avg_monthly_revenue', 'avg_monthly_qty', 'profit', 'margin_pct', 'month_year']].round(2)
display_df.columns = ['Total Revenue', 'Avg Monthly Revenue', 'Avg Monthly Qty', 'Total Profit', 'Avg Margin %', 'Months Present']
st.dataframe(display_df, use_container_width=True)

# Chart
top_10_revenue = revenue_leaders.head(10)
fig_bar = px.bar(x=top_10_revenue.index.get_level_values(1)[:10], 
                 y=top_10_revenue['revenue'].values[:10],
                 title="Top 10 Revenue Generators",
                 labels={'x': 'Product', 'y': 'Total Revenue ($)'})
fig_bar.update_xaxes(tickangle=45)
st.plotly_chart(fig_bar, use_container_width=True)

# Key insights
st.subheader("🔍 Key Insights")
top_product = revenue_leaders.index[0][1]
top_revenue = revenue_leaders.iloc[0]['revenue']
top_monthly = revenue_leaders.iloc[0]['avg_monthly_revenue']

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Top Product", top_product)
with col2:
    st.metric("Total Revenue", f"${top_revenue:,.0f}")
with col3:
    st.metric("Monthly Average", f"${top_monthly:,.0f}")

st.markdown("**💡 Recommendation:** Focus your initial inventory investment on the top 10-15 products listed above. These generate the most revenue and should be your priority for stocking.")