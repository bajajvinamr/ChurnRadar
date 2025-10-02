"""
Overview Page - Main dashboard with key metrics and top groups.
"""
import streamlit as st
import pandas as pd
from churn_core.logic import get_groups, get_defaults, kept_messages, calculate_roi
from churn_core.data import format_inr, format_percent, format_days, format_months, format_score_as_odds
from churn_core.brand import ARCHETYPES
from churn_core.content import (
    get_metric_label, get_metric_tooltip, get_column_label, get_column_tooltip,
    get_archetype_info, get_tour_banner, get_section_header
)

st.set_page_config(page_title="Overview - Churn Radar", page_icon="🏠", layout="wide")

st.title("🏠 Overview")
st.markdown("**Should we act today?**")

# First-time tour banner
tour_banner = get_tour_banner()
if tour_banner:
    st.info(f"💡 **{tour_banner}**")

# Load data
@st.cache_data(ttl=300)
def load_data():
    return get_groups(), get_defaults()

try:
    groups, defaults = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Top Strip - Key Metrics
st.markdown("---")

# Calculate aggregate metrics
ready_groups = sum(1 for card in groups.values() if card["summary"]["size"] > 0)
total_reactivations = 0
total_profit = 0

for name, card in groups.items():
    summary = card["summary"]
    config = defaults.get(name, {})
    
    if summary["size"] > 0 and config:
        reactivations = int(summary["size"] * config.get("reactivation_rate", 0))
        profit = reactivations * config.get("aov", 0) * config.get("margin", 0)
        
        total_reactivations += reactivations
        total_profit += profit

# Display metrics in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=get_metric_label("recoverable_profit"),
        value=format_inr(total_profit),
        help=get_metric_tooltip("recoverable_profit")
    )

with col2:
    st.metric(
        label=get_metric_label("ready_groups"), 
        value=ready_groups,
        help=get_metric_tooltip("ready_groups")
    )

with col3:
    st.metric(
        label=get_metric_label("expected_reactivations"),
        value=f"{total_reactivations:,}",
        help=get_metric_tooltip("expected_reactivations")
    )

st.caption("Based on today's groups and baseline response rates.")

# Cohort Ladder - Top 3 by Net Profit
st.markdown("---")
st.subheader(get_section_header("top_opportunities"))

# Build ladder data with archetype info
ladder_rows = []
for name, card in groups.items():
    summary = card["summary"]
    config = defaults.get(name, {})
    
    if summary["size"] > 0 and config:
        reactivations = int(summary["size"] * config.get("reactivation_rate", 0))
        net_profit = reactivations * config.get("aov", 0) * config.get("margin", 0)
        
        # Get archetype from summary
        archetype = summary.get("archetype", "Premium")
        archetype_info = get_archetype_info(archetype)
        
        ladder_rows.append({
            "Group": name,
            "People": f"{summary['size']:,}",
            "Last Seen": format_days(summary["avg_recency"]),
            "Come-Back Odds": format_score_as_odds(summary["avg_score"]),
            "Net Profit (₹)": format_inr(net_profit),
            "net_profit_numeric": net_profit,  # For sorting
            "archetype": archetype,
            "one_liner": archetype_info.get("one_liner", "")
        })

if ladder_rows:
    # Sort by net profit descending and take top 3
    ladder_df = pd.DataFrame(ladder_rows).sort_values("net_profit_numeric", ascending=False)
    top_3_df = ladder_df.head(3)
    
    # Display column headers
    header_cols = st.columns([2, 1, 1, 1, 1.5])
    with header_cols[0]:
        st.markdown("**Group**")
    with header_cols[1]:
        st.markdown(f"**{get_column_label('people')}**")
    with header_cols[2]:
        st.markdown(f"**{get_column_label('last_seen')}**")
    with header_cols[3]:
        st.markdown(f"**{get_column_label('comeback_odds')}**")
    with header_cols[4]:
        st.markdown(f"**{get_column_label('net_profit')} (₹)**")
    
    st.markdown("---")
    
    # Display each row with one-liner beneath
    for idx, (_, row) in enumerate(top_3_df.iterrows()):
        with st.container():
            # Display row data
            row_cols = st.columns([2, 1, 1, 1, 1.5])
            with row_cols[0]:
                st.markdown(f"**{row['Group']}**")
            with row_cols[1]:
                st.markdown(f"{row['People']}")
            with row_cols[2]:
                st.markdown(f"{row['Last Seen']}")
            with row_cols[3]:
                st.markdown(f"{row['Come-Back Odds']}")
            with row_cols[4]:
                st.markdown(f"**{row['Net Profit (₹)']}**")
            
            # Display one-liner
            if row['one_liner']:
                st.caption(f"💡 {row['one_liner']}")
            
            if idx < len(top_3_df) - 1:
                st.markdown("")  # Add spacing between rows
    
    # Action buttons for top groups
    st.markdown("**Quick Actions:**")
    action_cols = st.columns(3)
    
    for i, (_, row) in enumerate(top_3_df.iterrows()):
        with action_cols[i]:
            if st.button(f"Start → {row['Group']}", key=f"start_{i}", use_container_width=True):
                st.session_state.selected_group = row['Group']
                st.switch_page("pages/3_Messages.py")

    # View all groups
    if len(ladder_rows) > 3:
        if st.button("👥 View All Groups", use_container_width=True):
            st.switch_page("pages/2_Groups.py")

else:
    st.warning("No groups available. Please check your data source.")

# Quick insights
st.markdown("---")
st.subheader("📊 Quick Insights")

if ladder_rows:
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        # Top group insights
        top_group_name = ladder_df.iloc[0]["Group"]
        top_group_data = groups[top_group_name]
        top_summary = top_group_data["summary"]
        
        st.markdown("**🎯 Priority Focus:**")
        st.info(f"**{top_group_name}** has the highest profit potential with {top_summary['size']:,} people and {format_score_as_odds(top_summary['avg_score'])} come-back odds.")
        
        # Archetype insight
        archetype = top_summary.get("archetype", "Premium")
        if archetype in ARCHETYPES:
            arch_info = ARCHETYPES[archetype]
            st.success(f"💡 **{arch_info['name']} Strategy:** {arch_info['what_to_say']}")
    
    with insights_col2:
        # Portfolio insights
        total_people = sum(groups[name]["summary"]["size"] for name in groups.keys())
        avg_odds = sum(groups[name]["summary"]["avg_score"] for name in groups.keys()) / len(groups)
        
        st.markdown("**📈 Portfolio Summary:**")
        st.metric("Total Addressable People", f"{total_people:,}")
        st.metric("Average Come-Back Odds", format_score_as_odds(avg_odds))
        
        # ROI efficiency
        if total_profit > 0 and total_people > 0:
            profit_per_person = total_profit / total_people
            st.metric("Profit per Person", format_inr(profit_per_person))

# Navigation shortcuts
st.markdown("---")
st.subheader("🚀 Quick Navigation")

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    if st.button("👥 Browse Groups", use_container_width=True):
        st.switch_page("pages/2_Groups.py")

with nav_col2:
    if st.button("📝 View Messages", use_container_width=True):
        if st.session_state.get('selected_group'):
            st.switch_page("pages/3_Messages.py")
        else:
            # Set top group as selected
            if ladder_rows:
                st.session_state.selected_group = ladder_df.iloc[0]["Group"]
                st.switch_page("pages/3_Messages.py")
            else:
                st.warning("No groups available")

with nav_col3:
    if st.button("💰 Calculate ROI", use_container_width=True):
        if st.session_state.get('selected_group'):
            st.switch_page("pages/4_ROI.py")
        else:
            # Set top group as selected
            if ladder_rows:
                st.session_state.selected_group = ladder_df.iloc[0]["Group"]
                st.switch_page("pages/4_ROI.py")
            else:
                st.warning("No groups available")

with nav_col4:
    if st.button("📤 Exports", use_container_width=True):
        st.switch_page("pages/5_Exports.py")

# Footer
st.markdown("---")
st.caption("Built with ❤️ by the Growth Team • Powered by Churn Radar Analytics")