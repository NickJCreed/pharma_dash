import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data  # Import your centralized load_data function

st.set_page_config(page_title="Consistent Products", page_icon="🔄", layout="wide")

# Load data
df = load_data()
total_months = df['month_year'].nunique()

st.title("🔄 Most Consistent Products")
st.markdown("*Reliable monthly sellers - low risk inventory*")

consistency = df.groupby(['product_code', 'product_name']).agg({
    'month_year': 'nunique',
    'quantity': ['sum', 'mean'],
    'revenue': ['sum', 'mean'],
    'profit': 'sum',
    'margin_pct': 'mean'
}).round(2)

consistency.columns = ['months_present', 'total_qty', 'avg_monthly_qty', 'total_revenue', 'avg_monthly_revenue', 'total_profit', 'avg_margin']
most_consistent = consistency.sort_values(['months_present', 'total_revenue'], ascending=[False, False]).head(15)

most_consistent['consistency_pct'] = ((most_consistent['months_present'] / total_months) * 100).round(1)

display_df = most_consistent[['months_present', 'consistency_pct', 'avg_monthly_qty', 'avg_monthly_revenue', 'total_revenue', 'avg_margin']].round(2)
display_df.columns = ['Months Present', 'Consistency %', 'Avg Monthly Qty', 'Avg Monthly Revenue', 'Total Revenue', 'Avg Margin %']
st.dataframe(display_df, use_container_width=True)

# Consistency chart
fig_scatter = px.scatter(most_consistent, x='months_present', y='total_revenue',
                       size='avg_monthly_qty', color='avg_margin',
                       hover_data=['consistency_pct'],
                       title="Product Consistency vs Revenue",
                       labels={'months_present': 'Months Present', 'total_revenue': 'Total Revenue ($)'},
                       color_continuous_scale='plasma')
st.plotly_chart(fig_scatter, use_container_width=True)

# Key insights
st.subheader("🔍 Key Insights")
most_consistent_product = most_consistent.index[0][1]
consistency_rate = most_consistent.iloc[0]['consistency_pct']
avg_products_100_percent = len(most_consistent[most_consistent['consistency_pct'] == 100])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Most Consistent Product", most_consistent_product)
with col2:
    st.metric("Consistency Rate", f"{consistency_rate:.1f}%")
with col3:
    st.metric("100% Consistent Products", f"{avg_products_100_percent}")

st.markdown("**💡 Recommendation:** These products sell consistently every month, making them low-risk investments. Perfect for maintaining steady cash flow and customer satisfaction.")