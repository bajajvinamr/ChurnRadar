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
    from churn_core.content import METRIC_DEFINITIONS, ARCHETYPE_REASONS, COHORT_LIBRARY, COPY_RULES
    from chat_interface import render_chat_interface, render_conversation_starter
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

# First-time user banner
if 'hide_intro_banner' not in st.session_state:
    st.session_state.hide_intro_banner = False

if not st.session_state.hide_intro_banner:
    with st.container():
        st.info("""
        **What you're seeing:** We rank today's best customer groups to re-activate, show the most effective messages to send, and estimate the profit if you act now. Click a group to see facts, copy, and money impact.
        """)
        if st.button("Got it, hide this"):
            st.session_state.hide_intro_banner = True
            st.rerun()

# Demo mode banner
try:
    last_export_time = time.ctime(os.path.getmtime(os.path.join(os.path.dirname(__file__), '..', 'exports', 'manifest.json')))
    st.info(f"Demo Mode: On | Dataset: E Commerce Dataset.csv | Records: 5,630 | Last Export: {last_export_time}")
except:
    st.info("Demo Mode: On | Dataset: E Commerce Dataset.csv | Records: 5,630 | Last Export: Unknown")

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

# Render chat interface in sidebar
render_chat_interface()

# Conversation starter in main content
render_conversation_starter()

# Headline KPIs (TRD Section 2.1)
st.markdown("---")

# Get headline KPIs using conversation layer
try:
    from churn_core.conversation import get_headline_kpis
    kpis = get_headline_kpis()
    
    # Top Tiles: Recoverable Profit (30d) · Ready Groups Today · Expected Reactivations
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💰 Recoverable Profit (30d)",
            format_inr(kpis["recoverable_profit_30d"]),
            help="Total profit recoverable from re-engaging at-risk customers within 30 days"
        )
    
    with col2:
        st.metric(
            "📊 Ready Groups Today", 
            kpis["ready_groups_today"],
            help="Customer groups that meet criteria for immediate re-engagement campaigns"
        )
    
    with col3:
        st.metric(
            "👥 Expected Reactivations",
            f"{kpis['expected_reactivations']:,}",
            help="Estimated customers who will return based on historical reactivation rates"
        )
    
    # Show assumptions in expandable section
    with st.expander("📋 Assumptions", expanded=False):
        assumptions = kpis["assumptions"]
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Reactivation Rate", f"{assumptions['rr']:.0%}")
        with col_b:
            st.metric("Average Order Value", format_inr(assumptions['aov']))
        with col_c:
            st.metric("Profit Margin", f"{assumptions['margin']:.0%}")

except Exception as e:
    # Fallback to original metrics if conversation layer fails
    st.warning("Using fallback metrics. Conversation layer unavailable.")
    
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
    
    # Display fallback metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💰 Recoverable Profit (30d)",
            format_inr(total_profit)
        )
    
    with col2:
        st.metric(
            "📊 Ready Groups Today", 
            ready_groups
        )
    
    with col3:
        st.metric(
            "👥 Expected Reactivations",
            f"{total_reactivations:,}"
        )

st.caption("Based on today's groups and baseline response rates.")

# ROI Waterfall (TRD Section 2.2)
st.markdown("---")
st.subheader("📊 ROI Waterfall")
st.markdown("*Revenue · Reactivations · Groups breakdown*")

try:
    # Get ROI data from conversation layer
    from churn_core.conversation import show_roi
    roi_data = show_roi()
    
    # Display waterfall metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💰 Total Revenue Potential",
            format_inr(roi_data["total_revenue"]),
            help="Total revenue if all reactivation campaigns succeed"
        )
    
    with col2:
        st.metric(
            "👥 Total Reactivations",
            f"{roi_data['total_reactivations']:,}",
            help="Expected customers to reactivate across all groups"
        )
    
    with col3:
        st.metric(
            "📊 Active Groups",
            roi_data["active_groups"],
            help="Number of customer groups ready for campaigns"
        )
    
    # Show top contributors
    if roi_data.get("top_contributors"):
        st.markdown("**Top Contributors:**")
        for i, contributor in enumerate(roi_data["top_contributors"][:3], 1):
            st.markdown(f"{i}. **{contributor['group']}** - {format_inr(contributor['revenue'])} ({contributor['people']:,} people)")

except Exception as e:
    # Fallback to calculated metrics
    st.warning("Using calculated ROI metrics. Conversation layer unavailable.")
    
    total_revenue = 0
    total_reactivations = 0
    active_groups = 0
    contributors = []
    
    for name, card in groups.items():
        summary = card["summary"]
        config = defaults.get(name, {})
        
        if summary["size"] > 0 and config:
            active_groups += 1
            reactivations = int(summary["size"] * config.get("reactivation_rate", 0))
            revenue = reactivations * config.get("aov", 0)
            
            total_reactivations += reactivations
            total_revenue += revenue
            
            contributors.append({
                "group": name,
                "revenue": revenue,
                "people": reactivations
            })
    
    # Display fallback metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Total Revenue Potential", format_inr(total_revenue))
    
    with col2:
        st.metric("👥 Total Reactivations", f"{total_reactivations:,}")
    
    with col3:
        st.metric("📊 Active Groups", active_groups)
    
    # Show top contributors
    if contributors:
        contributors.sort(key=lambda x: x["revenue"], reverse=True)
        st.markdown("**Top Contributors:**")
        for i, contributor in enumerate(contributors[:3], 1):
            st.markdown(f"{i}. **{contributor['group']}** - {format_inr(contributor['revenue'])} ({contributor['people']:,} people)")

# Cohort Ladder with help
st.markdown("---")
col_header, col_help = st.columns([3, 1])
with col_header:
    st.subheader("🎯 Where to Start (Top-3)")
    st.markdown("*Groups ranked by profit potential with one-line reasons*")
with col_help:
    with st.expander("ⓘ What are these groups?"):
        for cohort_name, info in COHORT_LIBRARY.items():
            st.markdown(f"**{cohort_name}**")
            st.markdown(f"*Who:* {info['who']}")
            if 'why_matters' in info:
                st.markdown(f"*Why it matters:* {info['why_matters']}")
            st.markdown(f"*Say:* {info['say']}")
            st.markdown("---")

# Build ladder data with reasons
ladder_rows = []
for name, card in groups.items():
    summary = card["summary"]
    config = defaults.get(name, {})
    
    if summary["size"] > 0 and config:
        reactivations = int(summary["size"] * config.get("reactivation_rate", 0))
        net_profit = reactivations * config.get("aov", 0) * config.get("margin", 0)
        
        # Get archetype-based reason
        archetype = summary.get("archetype", "Premium")
        reason = ARCHETYPE_REASONS.get(archetype, "Focus on value and clear messaging.")
        
        ladder_rows.append({
            "Group": name,
            "People": f"{summary['size']:,}",
            "Last Seen": format_days(summary["avg_recency"]),
            "Come-Back Odds": format_score_as_odds(summary["avg_score"]),
            "Net Profit (₹)": format_inr(net_profit),
            "net_profit_numeric": net_profit,  # For sorting
            "reason": reason
        })

if ladder_rows:
    # Sort by net profit descending and take top 3
    ladder_df = pd.DataFrame(ladder_rows).sort_values("net_profit_numeric", ascending=False).head(3)
    
    # Display each group with its reason
    for _, row in ladder_df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1.5])
        
        with col1:
            st.markdown(f"**{row['Group']}**")
            st.caption(row['reason'])
        with col2:
            st.metric("People", row['People'])
        with col3:
            st.metric("Last Seen", row['Last Seen'], help=METRIC_DEFINITIONS["last_seen"]["definition"])
        with col4:
            st.metric("Come-Back Odds", row['Come-Back Odds'], help=METRIC_DEFINITIONS["come_back_odds"]["definition"])
        with col5:
            st.metric("Net Profit", row['Net Profit (₹)'], help=METRIC_DEFINITIONS["net_profit"]["definition"])
        
        st.markdown("---")
    
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
            st.markdown("**Group Passport**")
            
            # Display metrics with tooltips
            metrics = [
                ("People", f"{summary['size']:,} people", None),
                ("Come-Back Odds", format_score_as_odds(summary['avg_score']), METRIC_DEFINITIONS["come_back_odds"]),
                ("Last Seen", format_days(summary['avg_recency']), METRIC_DEFINITIONS["last_seen"]),
                ("Activity", f"{summary.get('avg_engagement', 0):.1f}", METRIC_DEFINITIONS["activity"]),
                ("Avg Spend", format_inr(summary.get('avg_value', 0)), METRIC_DEFINITIONS["avg_spend"]),
                ("Months with Brand", format_months(summary.get('avg_tenure', 0)), METRIC_DEFINITIONS["months_with_brand"])
            ]
            
            for metric_name, value, definition in metrics:
                help_text = None
                if definition:
                    help_text = f"{definition['definition']}"
                    if 'note' in definition:
                        help_text += f" {definition['note']}"
                
                st.metric(metric_name, value, help=help_text)
        
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
            if insights and insights.get("insights"):
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
                # Provide AI-enhanced insights with fallback
                from churn_core.logic import generate_ai_insights
                summary = groups[top_group]["summary"]
                group_data = groups[top_group]["data"]
                
                st.markdown("**💡 Business Insights**")
                
                # Generate basic metrics
                avg_recency = summary.get("avg_recency", 10)
                avg_score = summary.get("avg_score", 0.3)
                avg_value = summary.get("avg_value", 250)
                
                risk_level = "High" if avg_recency > 15 else "Medium" if avg_recency > 10 else "Low"
                risk_colors = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                risk_color = risk_colors.get(risk_level, "🟡")
                
                st.markdown(f"{risk_color} **Risk Level:** {risk_level}")
                st.markdown(f"⭐ **Priority Score:** {min(5.0, avg_score * 10 + 1):.1f}/5.0")
                
                # Generate AI insights (with fallback)
                with st.spinner("Generating AI insights..."):
                    ai_insight = generate_ai_insights(top_group, group_data)
                    st.info(f"🤖 {ai_insight}")
                
                # Additional data-driven insights
                if avg_recency <= 7:
                    st.info("💡 Recent activity suggests high engagement potential")
                elif avg_recency <= 14:
                    st.info("💡 Moderate recency - good timing for re-engagement")
                else:
                    st.info("💡 Extended absence - requires compelling offer")
                
                if avg_value > 300:
                    st.info("💡 High-value customers - worth premium approach")
                
                # Archetype-based recommendation
                archetype_rec = {
                    "Premium": "Lead with curation and personalized service",
                    "ValueSensitive": "Emphasize value and smart bundling",
                    "Loyalist": "Acknowledge loyalty and provide exclusive access",
                    "AtRisk": "Reduce friction and provide immediate value"
                }.get(archetype, "Focus on clear value proposition")
                
                st.success(f"🎯 **Next Action:** {archetype_rec}")

        # Messages Preview
        st.markdown("---")
        col_msg_header, col_msg_help = st.columns([3, 1])
        with col_msg_header:
            st.subheader("Ready-to-Send Messages")
        with col_msg_help:
            with st.expander("ⓘ How we write"):
                st.markdown(f"**Tone:** {COPY_RULES['tone']}")
                st.markdown("**Email:**")
                st.markdown(f"- Subject: {COPY_RULES['email']['subject']}")
                st.markdown(f"- Body: {COPY_RULES['email']['body']}")
                st.markdown(f"- {COPY_RULES['email']['cta']}")
                st.markdown("**WhatsApp:**")
                st.markdown(f"- Length: {COPY_RULES['whatsapp']['length']}")
                st.markdown(f"- Policy: {COPY_RULES['whatsapp']['policy']}")
                st.markdown("**Push:**")
                st.markdown(f"- Length: {COPY_RULES['push']['length']}")
                st.markdown(f"- Structure: {COPY_RULES['push']['structure']}")
                st.markdown(f"**Banned phrases:** {', '.join(COPY_RULES['banned_phrases'])}")
                st.markdown(f"**Safe tokens:** {', '.join(COPY_RULES['safe_tokens'])}")
                st.markdown(f"**Eval badge:** {COPY_RULES['eval_badge']}")
        
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

        # ROI Waterfall
        st.markdown("---")
        st.subheader("ROI Waterfall")
        
        roi_data = calculate_roi(top_group)
        if roi_data:
            inputs = roi_data["inputs"]
            outputs = roi_data["outputs"]
            
            # Create waterfall visualization with text
            revenue = outputs['revenue']
            gross_profit = outputs['gross_profit']
            total_costs = outputs['total_costs']
            net_profit = outputs['net_profit']
            
            # Display waterfall steps
            waterfall_col1, waterfall_col2, waterfall_col3, waterfall_col4, waterfall_col5 = st.columns(5)
            
            with waterfall_col1:
                st.metric("Revenue", format_inr(revenue), help="Total revenue from reactivated customers")
            
            with waterfall_col2:
                st.metric("× Margin", f"{inputs['margin']*100:.0f}%", help="Gross profit margin after cost of goods")
                st.caption(f"= {format_inr(gross_profit)}")
            
            with waterfall_col3:
                st.metric("− Send Costs", format_inr(outputs['send_costs']), help="Cost to send messages to all customers")
            
            with waterfall_col4:
                st.metric("− Incentives", format_inr(outputs['incentive_costs']), help="Cost of discounts/credits given")
            
            with waterfall_col5:
                st.metric("Net Profit", format_inr(net_profit), help="Final profit after all costs", delta_color="normal")
            
            # Assumptions caption
            st.caption(f"Assumes **{inputs['reactivation_rate']*100:.0f}% reactivation**, **{format_inr(inputs['aov'])} AOV**, **{inputs['margin']*100:.0f}% margin**.")

else:
    st.warning("No groups available. Please check your data source.")

# Footer
st.markdown("---")
st.caption("Built with ❤️ by the Growth Team")