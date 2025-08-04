import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data  # Import your centralized load_data function

st.set_page_config(page_title="Volume Leaders", page_icon="📦", layout="wide")

# Load data
df = load_data()

st.title("📦 High Volume Sellers")
st.markdown("*Fast-moving products with consistent demand*")

volume_leaders = df.groupby(['product_code', 'product_name']).agg({
    'quantity': 'sum',
    'revenue': 'sum',
    'profit': 'sum',
    'margin_pct': 'mean',
    'month_year': 'nunique'
}).sort_values('quantity', ascending=False).head(20)

volume_leaders['avg_monthly_qty'] = (volume_leaders['quantity'] / volume_leaders['month_year']).round(1)
volume_leaders['avg_monthly_revenue'] = (volume_leaders['revenue'] / volume_leaders['month_year']).round(0)

display_df = volume_leaders[['quantity', 'avg_monthly_qty', 'revenue', 'avg_monthly_revenue', 'margin_pct', 'month_year']].round(2)
display_df.columns = ['Total Quantity', 'Avg Monthly Qty', 'Total Revenue', 'Avg Monthly Revenue', 'Avg Margin %', 'Months Present']
st.dataframe(display_df, use_container_width=True)

# Chart
top_10_volume = volume_leaders.head(10)
fig_bar = px.bar(x=top_10_volume.index.get_level_values(1)[:10], 
                 y=top_10_volume['quantity'].values[:10],
                 title="Top 10 Volume Sellers",
                 labels={'x': 'Product', 'y': 'Total Quantity Sold'},
                 color=top_10_volume['margin_pct'].values[:10],
                 color_continuous_scale='viridis')
fig_bar.update_xaxes(tickangle=45)
st.plotly_chart(fig_bar, use_container_width=True)

# Key insights
st.subheader("🔍 Key Insights")
top_volume_product = volume_leaders.index[0][1]
top_quantity = volume_leaders.iloc[0]['quantity']
top_monthly_qty = volume_leaders.iloc[0]['avg_monthly_qty']

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Highest Volume Product", top_volume_product)
with col2:
    st.metric("Total Units Sold", f"{top_quantity:,.0f}")
with col3:
    st.metric("Monthly Average", f"{top_monthly_qty:,.1f} units")

st.markdown("**💡 Recommendation:** These high-volume products ensure fast inventory turnover. Stock these generously to avoid stockouts and maintain consistent customer satisfaction.")