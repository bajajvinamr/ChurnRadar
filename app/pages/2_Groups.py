"""
Groups Detail Page - Complete group analysis with search and filtering.
"""
import streamlit as st
import pandas as pd
from churn_core.logic import get_groups, get_defaults
from churn_core.data import format_inr, format_percent, format_days, format_months, format_score_as_odds
from churn_core.brand import ARCHETYPES

st.set_page_config(page_title="Groups - Churn Radar", page_icon="👥", layout="wide")

st.title("👥 Groups")
st.markdown("**Where do we start?**")

# Load data
@st.cache_data(ttl=300)
def load_data():
    return get_groups(), get_defaults()

groups, defaults = load_data()

# Search and filter controls
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_term = st.text_input("🔍 Search groups", placeholder="Type to search...")

with col2:
    min_size = st.number_input("Min People", min_value=0, value=0, step=100)

with col3:
    sort_by = st.selectbox("Sort by", ["Net Profit", "People", "Come-Back Odds", "Group Name"])

st.markdown("---")

# Build complete groups table
all_rows = []
for name, card in groups.items():
    summary = card["summary"]
    config = defaults.get(name, {})
    
    if summary["size"] > 0 and config:
        reactivations = int(summary["size"] * config.get("reactivation_rate", 0))
        net_profit = reactivations * config.get("aov", 0) * config.get("margin", 0)
        
        all_rows.append({
            "Group": name,
            "People": summary["size"],
            "Last Seen": summary["avg_recency"],
            "Come-Back Odds": summary["avg_score"] * 100,
            "Activity": summary.get("avg_engagement", 0),
            "Avg Spend": summary.get("avg_value", 0),
            "Months with Brand": summary.get("avg_tenure", 0),
            "Net Profit (₹)": net_profit,
            "Archetype": summary.get("archetype", "Premium")
        })

if all_rows:
    df = pd.DataFrame(all_rows)
    
    # Apply filters
    if search_term:
        df = df[df["Group"].str.contains(search_term, case=False)]
    
    if min_size > 0:
        df = df[df["People"] >= min_size]
    
    # Apply sorting
    sort_mapping = {
        "Net Profit": "Net Profit (₹)",
        "People": "People", 
        "Come-Back Odds": "Come-Back Odds",
        "Group Name": "Group"
    }
    
    if sort_by in sort_mapping:
        ascending = sort_by == "Group Name"  # Only group name sorts ascending
        df = df.sort_values(sort_mapping[sort_by], ascending=ascending)
    
    # Format for display
    display_df = df.copy()
    display_df["People"] = display_df["People"].apply(lambda x: f"{x:,}")
    display_df["Last Seen"] = display_df["Last Seen"].apply(format_days)
    display_df["Come-Back Odds"] = display_df["Come-Back Odds"].apply(lambda x: f"{x:.1f}%")
    display_df["Activity"] = display_df["Activity"].apply(lambda x: f"{x:.1f}")
    display_df["Avg Spend"] = display_df["Avg Spend"].apply(format_inr)
    display_df["Months with Brand"] = display_df["Months with Brand"].apply(format_months)
    display_df["Net Profit (₹)"] = display_df["Net Profit (₹)"].apply(format_inr)
    
    # Display results count
    st.write(f"**{len(display_df)}** groups found")
    
    # Display table
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Group selection for detailed view
    st.markdown("---")
    st.subheader("Group Details")
    
    selected_group = st.selectbox(
        "Select a group for detailed analysis:",
        options=[""] + list(df["Group"].values),
        format_func=lambda x: "Choose a group..." if x == "" else x
    )
    
    if selected_group and selected_group in groups:
        # Group Passport Modal
        summary = groups[selected_group]["summary"]
        config = defaults.get(selected_group, {})
        archetype = summary.get("archetype", "Premium")
        
        # Create two columns for passport
        pass_col1, pass_col2 = st.columns([1, 1])
        
        with pass_col1:
            st.markdown(f"### {selected_group}")
            
            # Metrics table
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
            st.dataframe(passport_df, hide_index=True, use_container_width=True)
        
        with pass_col2:
            st.markdown("### Messaging Guidance")
            
            if archetype in ARCHETYPES:
                arch_info = ARCHETYPES[archetype]
                
                st.markdown(f"**{arch_info['name']} Archetype**")
                
                # What to say
                st.markdown("**✅ What to say:**")
                st.success(arch_info['what_to_say'])
                
                # What to avoid  
                st.markdown("**❌ What to avoid:**")
                st.warning(arch_info['what_to_avoid'])
                
                # Tone guidance
                st.markdown("**🎯 Tone:**")
                st.info(arch_info['tone'])
            else:
                st.warning("Archetype guidance not available for this group.")
        
        # AI Insights Section
        st.markdown("---")
        st.markdown("### 🤖 AI Analysis")
        
        insight_col1, insight_col2 = st.columns([2, 1])
        
        with insight_col1:
            if st.button("🔍 Generate Fresh Insights", use_container_width=True):
                from churn_core.logic import generate_ai_insights
                
                with st.spinner("Analyzing group patterns..."):
                    ai_insight = generate_ai_insights(selected_group, groups[selected_group]["data"])
                    st.success(f"💡 **AI Insight:** {ai_insight}")
        
        with insight_col2:
            st.caption("Click to get AI-powered strategic analysis of this group's behavior patterns and retention opportunities.")
        
        # Action buttons
        st.markdown("---")
        button_col1, button_col2, button_col3 = st.columns([1, 1, 2])
        
        with button_col1:
            if st.button("📝 View Messages", use_container_width=True):
                st.session_state.selected_group = selected_group
                st.switch_page("pages/3_Messages.py")
        
        with button_col2:
            if st.button("💰 Calculate ROI", use_container_width=True):
                st.session_state.selected_group = selected_group
                st.switch_page("pages/4_ROI.py")

else:
    st.warning("No groups available. Please check your data source.")

# Navigation footer
st.markdown("---")
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("← Back to Overview", use_container_width=True):
        st.switch_page("app.py")

with nav_col3:
    if st.button("Messages →", use_container_width=True):
        if st.session_state.get('selected_group'):
            st.switch_page("pages/3_Messages.py")
        else:
            st.warning("Please select a group first")