import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data  # Import your centralized load_data function

st.set_page_config(page_title="Starter Pack", page_icon="🎯", layout="wide")

# Load data
df = load_data()

st.title("🎯 Recommended Starter Pack")
st.markdown("*Essential products to stock first - top performers across all metrics*")

# Calculate cost per unit
df['cost_per_unit'] = df['cost'] / df['quantity']

# ===========================
# INTERACTIVE FILTERS
# ===========================
st.sidebar.header("⚙️ Filters")
max_cost = st.sidebar.slider("Max cost per unit", 100, 20000, 500)
min_monthly_qty = st.sidebar.slider("Min monthly avg qty", 1, 20, 5)
optimise = st.sidebar.checkbox("Optimise (Ideal Subset)", value=True)

# Filter criteria for starter pack suitability
filtered_df = df[(df['cost_per_unit'] <= max_cost) & (df['quantity'] >= 2)].copy()

# Calculate monthly metrics for filtered data
monthly_metrics = filtered_df.groupby(['product_code', 'product_name']).agg({
    'revenue': 'sum',
    'quantity': 'sum',
    'profit': 'sum',
    'margin_pct': 'mean',
    'month_year': 'nunique',
    'cost_per_unit': 'mean'
}).round(2)

monthly_metrics['monthly_avg_qty'] = (monthly_metrics['quantity'] / monthly_metrics['month_year']).round(1)
monthly_metrics['monthly_avg_revenue'] = (monthly_metrics['revenue'] / monthly_metrics['month_year']).round(0)

# Filter for products with good monthly sales (user-selected)
monthly_metrics = monthly_metrics[monthly_metrics['monthly_avg_qty'] >= min_monthly_qty].copy()

# ===========================
# OPTIMISE TOGGLE
# ===========================
if optimise:
    # Use union of top performers
    revenue_leaders = monthly_metrics.sort_values('revenue', ascending=False).head(25)
    volume_leaders = monthly_metrics.sort_values('quantity', ascending=False).head(25)
    consistency_leaders = monthly_metrics.sort_values('month_year', ascending=False).head(20)
    high_monthly_sales = monthly_metrics.sort_values('monthly_avg_qty', ascending=False).head(25)

    essential_products = set()
    essential_products.update(revenue_leaders.index.get_level_values(0))
    essential_products.update(volume_leaders.index.get_level_values(0))
    essential_products.update(consistency_leaders.index.get_level_values(0))
    essential_products.update(high_monthly_sales.index.get_level_values(0))

    starter_pack = monthly_metrics[monthly_metrics.index.get_level_values(0).isin(essential_products)].copy()
else:
    # Use all filtered products
    starter_pack = monthly_metrics.copy()

# Calculate investment metrics
starter_pack['monthly_cost_estimate'] = ((starter_pack['revenue'] - starter_pack['profit']) / starter_pack['month_year']).round(0)
starter_pack['affordability_score'] = (starter_pack['monthly_avg_revenue'] / starter_pack['monthly_cost_estimate']).replace([float('inf'), -float('inf')], 0).round(2)

# ===========================
# IMPROVED STARTER SCORE
# ===========================
starter_pack['starter_score'] = (
    (starter_pack['monthly_avg_revenue'] / starter_pack['monthly_avg_revenue'].max()) * 0.35 +
    (starter_pack['monthly_avg_qty'] / starter_pack['monthly_avg_qty'].max()) * 0.35 +
    (starter_pack['margin_pct'] / starter_pack['margin_pct'].max()) * 0.2 +
    (starter_pack['affordability_score'] / starter_pack['affordability_score'].max()) * 0.1
).round(3)

# ===========================
# NEW FILTERS FOR SCORE & PRODUCT COUNT
# ===========================
max_products = len(starter_pack)
min_score = float(starter_pack['starter_score'].min())
max_score = float(starter_pack['starter_score'].max())

score_filter = st.sidebar.slider("Min Starter Score", min_score, max_score, min_score)
product_limit = st.sidebar.slider("Number of Products to Display", 10, max_products, min(100, max_products))

# Apply filters
starter_pack = starter_pack[starter_pack['starter_score'] >= score_filter]
starter_pack = starter_pack.sort_values('starter_score', ascending=False).head(product_limit)

# Display the refined table
display_df = starter_pack[['monthly_avg_qty', 'monthly_avg_revenue', 'monthly_cost_estimate', 'cost_per_unit', 'margin_pct', 'affordability_score', 'starter_score']].round(2)
display_df.columns = ['Monthly Avg Qty', 'Monthly Avg Revenue', 'Monthly Cost Est.', 'Cost Per Unit', 'Avg Margin %', 'Affordability Score', 'Starter Score']
st.dataframe(display_df, use_container_width=True)

# Investment summary
total_monthly_revenue_est = starter_pack['monthly_avg_revenue'].sum()
total_investment_estimate = starter_pack['monthly_cost_estimate'].sum()
avg_cost_per_unit = starter_pack['cost_per_unit'].mean()
avg_monthly_qty = starter_pack['monthly_avg_qty'].mean()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Essential Products", f"{len(starter_pack)} items")
with col2:
    st.metric("Monthly Revenue Potential", f"${total_monthly_revenue_est:,.0f}")
with col3:
    st.metric("Initial Investment Est.", f"${total_investment_estimate:,.0f}")
with col4:
    st.metric("Avg Cost Per Unit", f"${avg_cost_per_unit:.0f}")

col1, col2 = st.columns(2)
with col1:
    st.metric("Avg Monthly Units/Product", f"{avg_monthly_qty:.1f}")
with col2:
    st.metric("Projected Monthly ROI", f"{((total_monthly_revenue_est - total_investment_estimate) / total_investment_estimate * 100):.1f}%")

# Filter breakdown
st.subheader("📋 Filtering Criteria Applied")
original_products = df['product_code'].nunique()
after_cost_filter = filtered_df['product_code'].nunique()
after_monthly_sales_filter = len(monthly_metrics)

col1, col2, col3 = st.columns(3)
with col1:
    st.info(f"**Original Products:** {original_products}")
with col2:
    st.info(f"**After Cost Filter:** {after_cost_filter}\n(Max ₹{max_cost}/unit)")
with col3:
    st.info(f"**After Sales Filter:** {after_monthly_sales_filter}\n(Min {min_monthly_qty} units/month)")

# ===========================
# STARTER SCORE BREAKDOWN
# ===========================
st.subheader(f"📊 Starter Score Breakdown ({'Optimised' if optimise else 'Top Selection'})")

st.markdown("""
The **Starter Score** is a combined ranking that helps identify the best products to stock first.  
It is calculated using these weighted factors:
- **Revenue (35%)** – Products that generate higher average monthly revenue get a better score.
- **Quantity (35%)** – Products that sell in larger volumes each month rank higher.
- **Margin (20%)** – Higher profit margins improve the score.
- **Affordability (10%)** – Products that are cheaper to stock relative to the revenue they bring in get a small bonus.

The chart below shows how each factor contributes to the total score for the **top 100 products**.
""")

score_breakdown = starter_pack.copy()
score_breakdown['score_revenue'] = (score_breakdown['monthly_avg_revenue'] / score_breakdown['monthly_avg_revenue'].max()) * 0.35
score_breakdown['score_qty'] = (score_breakdown['monthly_avg_qty'] / score_breakdown['monthly_avg_qty'].max()) * 0.35
score_breakdown['score_margin'] = (score_breakdown['margin_pct'] / score_breakdown['margin_pct'].max()) * 0.2
score_breakdown['score_affordability'] = (score_breakdown['affordability_score'] / score_breakdown['affordability_score'].max()) * 0.1

# Transform to long format
score_long = score_breakdown.reset_index().melt(
    id_vars=['product_name'], 
    value_vars=['score_revenue', 'score_qty', 'score_margin', 'score_affordability'],
    var_name='Score Component', 
    value_name='Score Contribution'
)

score_long['Score Component'] = score_long['Score Component'].replace({
    'score_revenue': 'Revenue',
    'score_qty': 'Quantity',
    'score_margin': 'Margin %',
    'score_affordability': 'Affordability'
})

fig_score_breakdown = px.bar(
    score_long,
    x='Score Contribution',
    y='product_name',
    color='Score Component',
    orientation='h',
    title="Starter Score Breakdown by Component",
    barmode='stack',
    color_discrete_map={
        'Revenue': '#1f77b4',
        'Quantity': '#ff7f0e',
        'Margin %': '#2ca02c',
        'Affordability': '#d62728'
    }
)
fig_score_breakdown.update_layout(height=1000, yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig_score_breakdown, use_container_width=True)

# ===========================
# TREEMAP
# ===========================
fig_treemap = px.treemap(
    starter_pack.reset_index(),
    path=['product_name'],
    values='monthly_cost_estimate',
    color='starter_score',
    title="Investment Breakdown by Product (Sized by Cost, Colored by Starter Score)",
    color_continuous_scale=[[0, "white"], [1, "green"]],
    range_color=[0, 1]
)
fig_treemap.update_layout(height=900)
st.plotly_chart(fig_treemap, use_container_width=True)

# ===========================
# SCATTER PLOT
# ===========================
fig_scatter = px.scatter(
    starter_pack.reset_index(),
    x='monthly_cost_estimate',
    y='monthly_avg_revenue',
    size='monthly_avg_qty',
    color='margin_pct',
    hover_data=['product_name'],
    title="Investment vs Revenue Potential (Size = Monthly Quantity)",
    labels={'monthly_cost_estimate': 'Monthly Investment Required ($)', 'monthly_avg_revenue': 'Monthly Revenue Potential ($)'},
    color_continuous_scale='viridis'
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ===========================
# ROI ANALYSIS
# ===========================
roi_analysis = starter_pack.copy()
roi_analysis['monthly_roi'] = ((roi_analysis['monthly_avg_revenue'] - roi_analysis['monthly_cost_estimate']) / roi_analysis['monthly_cost_estimate'] * 100).round(1)
top_roi = roi_analysis.sort_values('monthly_roi', ascending=False).head(product_limit)

fig_roi = px.bar(
    top_roi,
    x='monthly_roi',
    y=top_roi.index.get_level_values(1),
    orientation='h',
    color='monthly_roi',
    title="Top Products by Monthly ROI (%)",
    labels={'y': 'Product', 'x': 'Monthly ROI (%)'},
    color_continuous_scale='RdYlGn'
)
fig_roi.update_layout(height=2000, yaxis={'categoryorder': 'total ascending'})
fig_roi.update_traces(text=top_roi['monthly_roi'], textposition='outside')
st.plotly_chart(fig_roi, use_container_width=True)

# ===========================
# SUMMARY
# ===========================
st.subheader("🎯 Starter Pack Summary")
st.success(f"""
**This refined starter pack includes {len(starter_pack)} carefully selected products that are:**
- ✅ Affordable to stock (max ₹{max_cost}/unit)
- ✅ Fast-moving (minimum {min_monthly_qty} units sold per month)
- ✅ Profitable with good margins
- ✅ Proven performers across revenue, volume, and consistency

**Investment Summary:**
- Total monthly investment: ₹{total_investment_estimate:,.0f}
- Expected monthly revenue: ₹{total_monthly_revenue_est:,.0f}
- Projected ROI: {((total_monthly_revenue_est - total_investment_estimate) / total_investment_estimate * 100):.1f}%
""")
st.markdown("**💡 Recommendation:** Start with the top products from this list based on your available capital.")
