"""
ROI Calculator Page - Interactive financial impact analysis.
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from churn_core.logic import get_groups, get_defaults, calculate_roi
from churn_core.data import format_inr

st.set_page_config(page_title="ROI Calculator - Churn Radar", page_icon="💰", layout="wide")

st.title("💰 ROI Calculator")
st.markdown("**What's the money?**")

# Check if we have a selected group
if 'selected_group' not in st.session_state or not st.session_state.selected_group:
    st.warning("No group selected. Please choose a group from the Overview or Groups page.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Overview"):
            st.switch_page("app.py")
    with col2:
        if st.button("Browse Groups →"):
            st.switch_page("pages/2_Groups.py")
    st.stop()

selected_group = st.session_state.selected_group

# Load data
@st.cache_data(ttl=300)
def load_group_data(group_name):
    groups = get_groups()
    defaults = get_defaults()
    if group_name not in groups:
        return None, None
    return groups[group_name], defaults.get(group_name, {})

group_data, default_params = load_group_data(selected_group)

if not group_data:
    st.error(f"Group '{selected_group}' not found.")
    st.stop()

summary = group_data["summary"]
group_size = summary["size"]

# Group context
st.info(f"**{selected_group}** • {group_size:,} people")

# Parameter controls
st.subheader("🎛️ Scenario Parameters")

param_col1, param_col2 = st.columns(2)

with param_col1:
    st.markdown("**Response & Economics**")
    
    reactivation_rate = st.slider(
        "Reactivation Rate (%)",
        min_value=1.0,
        max_value=25.0,
        value=default_params.get("reactivation_rate", 0.08) * 100,
        step=0.5,
        help="Percentage of contacted customers who reactivate"
    ) / 100
    
    aov = st.slider(
        "Average Order Value (₹)",
        min_value=500,
        max_value=10000,
        value=int(default_params.get("aov", 1500)),
        step=100,
        help="Expected AOV for reactivated customers"
    )
    
    margin = st.slider(
        "Gross Margin (%)",
        min_value=30.0,
        max_value=80.0, 
        value=default_params.get("margin", 0.60) * 100,
        step=1.0,
        help="Gross profit margin on sales"
    ) / 100

with param_col2:
    st.markdown("**Costs & Incentives**")
    
    send_cost = st.slider(
        "Send Cost per Person (₹)",
        min_value=0.1,
        max_value=5.0,
        value=default_params.get("send_cost", 0.25),
        step=0.05,
        help="Cost to reach each customer across channels"
    )
    
    incentive_rate = st.slider(
        "Incentive Rate (%)",
        min_value=0.0,
        max_value=20.0,
        value=default_params.get("incentive_rate", 0.05) * 100,
        step=0.5,
        help="Discount/incentive as % of AOV"
    ) / 100
    
    incentive_takeup = st.slider(
        "Incentive Takeup (%)",
        min_value=10.0,
        max_value=90.0,
        value=40.0,
        step=5.0,
        help="% of reactivated customers who use incentive"
    ) / 100

# Calculate ROI with current parameters
params = {
    "reactivation_rate": reactivation_rate,
    "aov": aov,
    "margin": margin,
    "send_cost": send_cost,
    "incentive_rate": incentive_rate,
    "incentive_takeup": incentive_takeup
}

roi_data = calculate_roi(selected_group, params)

if roi_data:
    outputs = roi_data["outputs"]
    
    # Key metrics display
    st.markdown("---")
    st.subheader("📊 Financial Impact")
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric(
            "Reactivated Customers",
            f"{outputs['reactivated']:,}",
            help="Expected number of customers who will respond"
        )
    
    with metric_col2:
        st.metric(
            "Gross Revenue",
            format_inr(outputs['revenue']),
            help="Total revenue from reactivated customers"
        )
    
    with metric_col3:
        st.metric(
            "Net Profit",
            format_inr(outputs['net_profit']),
            help="Profit after all costs and incentives"
        )
    
    with metric_col4:
        st.metric(
            "ROMI",
            f"{outputs['romi']:.1f}x",
            help="Return on Marketing Investment"
        )
    
    # Waterfall chart
    st.markdown("---")
    st.subheader("💧 ROI Waterfall")
    
    # Prepare waterfall data
    steps = [
        "Gross Revenue",
        "Gross Profit", 
        "Send Costs",
        "Incentive Costs",
        "Net Profit"
    ]
    
    values = [
        outputs['revenue'],
        outputs['gross_profit'] - outputs['revenue'],  # Margin impact (negative)
        -outputs['send_costs'],
        -outputs['incentive_costs'],
        outputs['net_profit']
    ]
    
    measures = ["absolute", "relative", "relative", "relative", "total"]
    
    # Create waterfall chart
    fig = go.Figure(go.Waterfall(
        name="ROI Analysis",
        orientation="v",
        measure=measures,
        x=steps,
        y=values,
        text=[format_inr(v) for v in values],
        textposition="outside",
        connector={"line": {"color": "#6B7280"}},
        decreasing={"marker": {"color": "#EF4444"}},
        increasing={"marker": {"color": "#10B981"}},
        totals={"marker": {"color": "#3B82F6"}}
    ))
    
    fig.update_layout(
        title=None,
        showlegend=False,
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E5E7EB"),
        height=400,
        margin=dict(t=20, b=40, l=40, r=40),
        yaxis=dict(
            gridcolor="#374151",
            zerolinecolor="#374151",
            tickformat="₹,.0f",
            title="Amount (₹)"
        ),
        xaxis=dict(
            tickangle=0,
            title=""
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Assumptions summary
    st.caption(f"Assumes {reactivation_rate*100:.1f}% reactivation at {format_inr(aov)} AOV with {margin*100:.0f}% margin")
    
    # Sensitivity analysis
    st.markdown("---")
    st.subheader("📈 Sensitivity Analysis")
    
    # Quick scenario buttons
    scenario_col1, scenario_col2, scenario_col3 = st.columns(3)
    
    with scenario_col1:
        if st.button("🎯 Optimistic (+25%)", use_container_width=True):
            optimistic_params = params.copy()
            optimistic_params["reactivation_rate"] *= 1.25
            opt_roi = calculate_roi(selected_group, optimistic_params)
            st.success(f"Optimistic Net Profit: {format_inr(opt_roi['outputs']['net_profit'])}")
    
    with scenario_col2:
        if st.button("📊 Conservative (-25%)", use_container_width=True):
            conservative_params = params.copy()
            conservative_params["reactivation_rate"] *= 0.75
            cons_roi = calculate_roi(selected_group, conservative_params)
            st.warning(f"Conservative Net Profit: {format_inr(cons_roi['outputs']['net_profit'])}")
    
    with scenario_col3:
        if st.button("💥 Double Response", use_container_width=True):
            double_params = params.copy()
            double_params["reactivation_rate"] *= 2
            double_roi = calculate_roi(selected_group, double_params)
            st.info(f"Double Response Net Profit: {format_inr(double_roi['outputs']['net_profit'])}")
    
    # Cost breakdown
    st.markdown("---")
    with st.expander("💰 Cost Breakdown"):
        cost_data = {
            "Cost Type": ["Send Costs", "Incentive Costs", "Total Costs"],
            "Amount": [
                format_inr(outputs['send_costs']),
                format_inr(outputs['incentive_costs']),
                format_inr(outputs['total_costs'])
            ],
            "Per Customer": [
                format_inr(outputs['send_costs'] / group_size),
                format_inr(outputs['incentive_costs'] / outputs['reactivated'] if outputs['reactivated'] > 0 else 0),
                format_inr(outputs['total_costs'] / outputs['reactivated'] if outputs['reactivated'] > 0 else 0)
            ]
        }
        
        cost_df = pd.DataFrame(cost_data)
        st.dataframe(cost_df, hide_index=True, use_container_width=True)

else:
    st.error("Unable to calculate ROI. Please check your parameters.")

# Export current scenario
st.markdown("---")
export_col1, export_col2 = st.columns(2)

with export_col1:
    if st.button("📊 Save Scenario", use_container_width=True):
        scenario_data = {
            "group": selected_group,
            "parameters": params,
            "results": outputs if roi_data else {},
            "timestamp": pd.Timestamp.now().isoformat()
        }
        st.success("✅ Scenario saved! (Feature coming soon)")

with export_col2:
    if st.button("📤 Export Analysis", use_container_width=True):
        st.switch_page("pages/5_Exports.py")

# Navigation
st.markdown("---")
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("← Messages", use_container_width=True):
        st.switch_page("pages/3_Messages.py")

with nav_col2:
    if st.button("🏠 Overview", use_container_width=True):
        st.switch_page("app.py")

with nav_col3:
    if st.button("Exports →", use_container_width=True):
        st.switch_page("pages/5_Exports.py")