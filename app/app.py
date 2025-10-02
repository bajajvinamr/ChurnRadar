"""
Churn Radar - Main Streamlit Application
Product-grade UI for customer resurrection analytics.
"""
import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Check required environment variables
if not os.getenv('OPENAI_API_KEY'):
    st.error("Missing required environment variable OPENAI_API_KEY. Please set it in your .env file. See README section 'Environment Variables' for details.")
    st.stop()

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from churn_core.logic import get_groups, get_defaults, kept_messages, calculate_roi
    from churn_core.data import format_inr, format_percent, format_days, format_months, format_score_as_odds
    from churn_core.brand import ARCHETYPES
    from churn_core.content import (
        get_metric_label, get_metric_tooltip, get_column_label, get_section_header,
        get_tour_banner, get_archetype_info, get_badge_text
    )
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Churn Radar",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-container {
        background-color: #1F2937;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #374151;
    }
    .group-card {
        background-color: #1F2937;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #374151;
        margin: 1rem 0;
    }
    .message-card {
        background-color: #1F2937;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #374151;
        margin: 0.5rem 0;
    }
    .badge {
        background-color: #3B82F6;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .success-badge {
        background-color: #10B981;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_group' not in st.session_state:
    st.session_state.selected_group = None

# Main app header
st.title("🧭 Churn Radar")
st.markdown("**Actionable User Resurrection at Scale**")

# Demo mode banner
try:
    last_export_time = time.ctime(os.path.getmtime(os.path.join(os.path.dirname(__file__), '..', 'exports', 'manifest.json')))
    st.info(f"Demo Mode: On | Dataset: E Commerce Dataset.csv | Records: 5,630 | Last Export: {last_export_time}")
except:
    st.info("Demo Mode: On | Dataset: E Commerce Dataset.csv | Records: 5,630 | Last Export: Unknown")

# First-time tour banner
tour_banner = get_tour_banner()
if tour_banner:
    with st.expander("💡 What you're seeing", expanded=False):
        st.markdown(tour_banner)

# Cache data loading
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    try:
        groups = get_groups()
        defaults = get_defaults()
        return groups, defaults
    except Exception as e:
        st.error(f"Error loading data: {e}. Ensure run_churn_radar.py has been executed successfully.")
        st.stop()

# Load data
groups, defaults = load_data()

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

# Cohort Ladder
st.markdown("---")
st.subheader(get_section_header("top_opportunities"))

# Build ladder data
ladder_rows = []
for name, card in groups.items():
    summary = card["summary"]
    config = defaults.get(name, {})
    
    if summary["size"] > 0 and config:
        reactivations = int(summary["size"] * config.get("reactivation_rate", 0))
        net_profit = reactivations * config.get("aov", 0) * config.get("margin", 0)
        
        ladder_rows.append({
            "Group": name,
            "People": f"{summary['size']:,}",
            "Last Seen": format_days(summary["avg_recency"]),
            "Come-Back Odds": format_score_as_odds(summary["avg_score"]),
            "Net Profit (₹)": format_inr(net_profit),
            "net_profit_numeric": net_profit  # For sorting
        })

if ladder_rows:
    # Sort by net profit descending and take top 3
    ladder_df = pd.DataFrame(ladder_rows).sort_values("net_profit_numeric", ascending=False).head(3)
    
    # Display table without the numeric sorting column
    display_df = ladder_df.drop(columns=["net_profit_numeric"])
    st.dataframe(display_df, width="stretch", hide_index=True)
    
    # Action buttons for top groups
    st.markdown("**Quick Actions:**")
    cols = st.columns(min(len(ladder_rows), 4))
    
    for i, (_, row) in enumerate(ladder_df.head(4).iterrows()):
        if i < len(cols):
            with cols[i]:
                if st.button(f"Start → {row['Group'][:20]}...", key=f"start_{i}"):
                    st.session_state.selected_group = row['Group']
                    st.switch_page("pages/3_Messages.py")

    # Group Passport for Top Group
    if not ladder_df.empty:
        top_group = ladder_df.iloc[0]["Group"]
        
        st.markdown("---")
        st.subheader(f"Group Passport — {top_group}")
        
        summary = groups[top_group]["summary"]
        archetype = summary.get("archetype", "Premium")
        
        # Passport metrics table
        col1, col2 = st.columns([1, 1])
        
        with col1:
            passport_data = {
                "Metric": [
                    "People",
                    "Come-Back Odds", 
                    "Last Seen",
                    "Activity",
                    "Avg Spend",
                    "Months with Brand"
                ],
                "Value": [
                    f"{summary['size']:,} people",
                    format_score_as_odds(summary['avg_score']),
                    format_days(summary['avg_recency']),
                    f"{summary.get('avg_engagement', 0):.1f}",
                    format_inr(summary.get('avg_value', 0)),
                    format_months(summary.get('avg_tenure', 0))
                ]
            }
            passport_df = pd.DataFrame(passport_data)
            st.dataframe(passport_df, hide_index=True, width="stretch")
        
        with col2:
            # Archetype guidance
            if archetype in ARCHETYPES:
                arch_info = ARCHETYPES[archetype]
                st.markdown(f"**{arch_info['name']} Archetype**")
                st.success(f"✓ {arch_info['what_to_say']}")
                st.warning(f"⚠️ {arch_info['what_to_avoid']}")
            else:
                st.info("Archetype guidance not available")
            
            # Business Insights
            insights = groups[top_group].get("insights", {})
            if insights:
                st.markdown("**💡 Business Insights**")
                
                # Risk level indicator
                risk_level = insights.get("risk_level", "Medium")
                risk_colors = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                risk_color = risk_colors.get(risk_level, "🟡")
                
                st.markdown(f"{risk_color} **Risk Level:** {risk_level}")
                st.markdown(f"⭐ **Priority Score:** {insights.get('priority_score', 3.0):.1f}/5.0")
                
                # Key insights
                for insight in insights.get("insights", [])[:2]:  # Show top 2 insights
                    st.info(f"💡 {insight}")
                
                # Top recommendation
                recommendations = insights.get("recommendations", [])
                if recommendations:
                    st.success(f"🎯 **Next Action:** {recommendations[0]}")
            else:
                st.info("💡 Insights loading...")

        # Messages Preview
        st.markdown("---")
        st.subheader("Ready-to-Send Messages")
        
        msgs = kept_messages(top_group)
        msg_cols = st.columns(3)
        
        for i, channel in enumerate(["email", "whatsapp", "push"]):
            with msg_cols[i]:
                st.markdown(f"**{channel.upper()}**")
                
                variant = msgs.get(channel, {}).get("variants", [{}])[0]
                title = variant.get("title", "(no title)")
                body = variant.get("body", "(no body)")
                eval_data = variant.get("_eval", {})
                
                # Message card
                st.markdown(f"""
                <div class="message-card">
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">{title}</div>
                    <div style="color: #9CA3AF; margin-bottom: 0.75rem;">{body}</div>
                    <div>
                        <span class="success-badge">Brand-safe ✓</span>
                        {f'<span class="badge">Eval {eval_data.get("overall", "-")}★</span>' if eval_data else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ROI Preview
        st.markdown("---")
        st.subheader("Money impact")
        
        roi_data = calculate_roi(top_group)
        if roi_data:
            outputs = roi_data["outputs"]
            
            roi_col1, roi_col2, roi_col3 = st.columns(3)
            
            with roi_col1:
                st.metric("Reactivated", f"{outputs['reactivated']:,}")
            
            with roi_col2:
                st.metric("Net Profit", format_inr(outputs['net_profit']))
            
            with roi_col3:
                st.metric("ROMI", f"{outputs['romi']:.1f}x")
            
            st.caption(f"Assumes {roi_data['inputs']['reactivation_rate']*100:.0f}% reactivation at ₹{roi_data['inputs']['aov']:,.0f} AOV")

else:
    st.warning("No groups available. Please check your data source.")

# Footer
st.markdown("---")
st.caption("Built with ❤️ by the Growth Team")