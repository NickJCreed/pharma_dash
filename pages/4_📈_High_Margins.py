import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data  # Import your centralized load_data function

st.set_page_config(page_title="High Margins", page_icon="📈", layout="wide")

# Load data
df = load_data()

st.title("📈 Highest Profit Margin Products")
st.markdown("*Best ROI products for maximum profitability*")

high_margin = df.groupby(['product_code', 'product_name']).agg({
    'margin_pct': 'mean',
    'revenue': 'sum',
    'quantity': 'sum',
    'profit': 'sum',
    'month_year': 'nunique'
}).query('revenue > 1000').sort_values('margin_pct', ascending=False).head(15)

high_margin['avg_monthly_revenue'] = (high_margin['revenue'] / high_margin['month_year']).round(0)

display_df = high_margin[['margin_pct', 'revenue', 'avg_monthly_revenue', 'quantity', 'profit']].round(2)
display_df.columns = ['Avg Margin %', 'Total Revenue', 'Avg Monthly Revenue', 'Total Quantity', 'Total Profit']
st.dataframe(display_df, use_container_width=True)

# Margin chart
fig_bar = px.bar(x=high_margin.index.get_level_values(1), 
                 y=high_margin['margin_pct'].values,
                 title="Highest Profit Margin Products",
                 labels={'x': 'Product', 'y': 'Profit Margin (%)'},
                 color=high_margin['revenue'].values,
                 color_continuous_scale='reds')
fig_bar.update_xaxes(tickangle=45)
st.plotly_chart(fig_bar, use_container_width=True)

# Revenue vs Margin scatter
fig_scatter = px.scatter(high_margin, x='margin_pct', y='revenue',
                        size='quantity',
                        title="Margin vs Revenue Analysis",
                        labels={'margin_pct': 'Profit Margin (%)', 'revenue': 'Total Revenue ($)'})
st.plotly_chart(fig_scatter, use_container_width=True)

# Key insights
st.subheader("🔍 Key Insights")
highest_margin_product = high_margin.index[0][1]
highest_margin = high_margin.iloc[0]['margin_pct']
avg_margin = high_margin['margin_pct'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Highest Margin Product", highest_margin_product)
with col2:
    st.metric("Margin Rate", f"{highest_margin:.1f}%")
with col3:
    st.metric("Average Margin (Top 15)", f"{avg_margin:.1f}%")

st.markdown("**💡 Recommendation:** Focus on these high-margin products for maximum profitability per sale. Even with lower volumes, they can significantly boost your bottom line.")