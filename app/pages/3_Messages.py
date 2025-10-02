"""
Messages Page - Channel-specific message management and generation.
"""
import streamlit as st
import json
from churn_core.logic import get_groups, kept_messages
from churn_core.brand import ARCHETYPES
from churn_core.content import (
    get_copy_rules, get_badge_text, get_archetype_info,
    get_section_header, get_empty_state
)

st.set_page_config(page_title="Messages - Churn Radar", page_icon="📝", layout="wide")

st.title("📝 Messages")
st.markdown("**What goes out?**")

# Check if we have a selected group
if 'selected_group' not in st.session_state or not st.session_state.selected_group:
    st.warning(get_empty_state("no_group_selected"))
    
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
    if group_name not in groups:
        return None, None
    return groups[group_name], kept_messages(group_name)

group_data, messages = load_group_data(selected_group)

if not group_data:
    st.error(f"Group '{selected_group}' not found.")
    st.stop()

# Group context header
summary = group_data["summary"]
archetype = summary.get("archetype", "Premium")

st.info(f"**{selected_group}** • {summary['size']:,} people • {archetype} archetype")

# Channel tabs
tab1, tab2, tab3 = st.tabs(["📧 Email", "💬 WhatsApp", "📱 Push"])

def render_message_card(channel, variant, channel_icon):
    """Render a message card with evaluation badge."""
    title = variant.get("title", "(no title)")
    body = variant.get("body", "(no body)")
    eval_data = variant.get("_eval", {})
    
    # Message preview card
    st.markdown(f"""
    <div style="background-color: #1F2937; padding: 1.5rem; border-radius: 0.5rem; border: 1px solid #374151; margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 1.1rem; font-weight: 600; color: #E5E7EB;">
                {channel_icon} {channel.upper()}
            </div>
            <div>
                <span style="background-color: #10B981; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem; margin-right: 0.5rem;">
                    Brand-safe ✓
                </span>
                {f'<span style="background-color: #3B82F6; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem;">Eval {eval_data.get("overall", "-")}★</span>' if eval_data else ''}
            </div>
        </div>
        
        <div style="font-weight: 600; margin-bottom: 0.75rem; color: #E5E7EB; font-size: 1.1rem;">
            {title}
        </div>
        
        <div style="color: #9CA3AF; line-height: 1.5; margin-bottom: 1rem;">
            {body}
        </div>
        
        <div style="border-top: 1px solid #374151; padding-top: 1rem; color: #9CA3AF; font-size: 0.9rem;">
            <strong>CTA:</strong> Clear button on page
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"📋 Copy {channel.title()}", key=f"copy_{channel}"):
            # Copy to clipboard (simulated)
            message_text = f"Subject: {title}\n\n{body}"
            st.success(f"✅ {channel.title()} message copied to clipboard!")
            # In a real app, you'd use JavaScript to copy to clipboard
    
    with col2:
        if st.button(f"🔄 Regenerate {channel.title()}", key=f"regen_{channel}"):
            st.info(f"🔄 Regenerating {channel} message... (Feature coming soon)")
    
    # Evaluation details (expandable)
    if eval_data:
        with st.expander(f"📊 Evaluation Details - {channel.title()}"):
            eval_cols = st.columns(5)
            metrics = ["clarity", "on_brand", "persuasiveness", "relevance", "safety"]
            
            for i, metric in enumerate(metrics):
                if i < len(eval_cols):
                    with eval_cols[i]:
                        score = eval_data.get(metric, 0)
                        st.metric(metric.replace("_", " ").title(), f"{score}/5")

# Email Tab
with tab1:
    email_variants = messages.get("email", {}).get("variants", [])
    if email_variants:
        render_message_card("email", email_variants[0], "📧")
    else:
        st.warning("No email messages available for this group.")

# WhatsApp Tab  
with tab2:
    whatsapp_variants = messages.get("whatsapp", {}).get("variants", [])
    if whatsapp_variants:
        render_message_card("whatsapp", whatsapp_variants[0], "💬")
    else:
        st.warning("No WhatsApp messages available for this group.")

# Push Tab
with tab3:
    push_variants = messages.get("push", {}).get("variants", [])
    if push_variants:
        render_message_card("push", push_variants[0], "📱")
    else:
        st.warning("No push messages available for this group.")

# Archetype guidance
st.markdown("---")
st.subheader(get_section_header("messaging_guidelines"))

if archetype in ARCHETYPES:
    arch_info = ARCHETYPES[archetype]
    archetype_content = get_archetype_info(archetype)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**✅ What to say:**")
        st.success(arch_info['what_to_say'])
        
        st.markdown("**🎯 Recommended tone:**")
        st.info(arch_info['tone'])
    
    with col2:
        st.markdown("**❌ What to avoid:**")
        st.warning(arch_info['what_to_avoid'])

# Copy rules help panel
with st.expander("📖 Message Copy Rules & Guidelines"):
    copy_rules = get_copy_rules()
    
    st.markdown(f"### {copy_rules.get('title', 'How We Write')}")
    st.markdown(f"**Tone:** {copy_rules.get('tone', 'Helpful and clear')}")
    
    st.markdown("---")
    st.markdown("### Channel Guidelines")
    
    rule_col1, rule_col2, rule_col3 = st.columns(3)
    
    with rule_col1:
        st.markdown("**📧 Email**")
        email_rules = copy_rules.get('email', {})
        st.markdown(f"- Subject: ≤{email_rules.get('subject_max', 50)} chars")
        st.markdown(f"- Key info in first {email_rules.get('subject_key_info', 33)} chars")
        st.markdown(f"- Body: ≤{email_rules.get('body_max_words', 110)} words")
        st.markdown(f"- CTAs: {email_rules.get('cta_count', 1)}")
    
    with rule_col2:
        st.markdown("**💬 WhatsApp**")
        wa_rules = copy_rules.get('whatsapp', {})
        st.markdown(f"- Length: {wa_rules.get('words', '25-30 words')}")
        st.markdown(f"- Requirements: {wa_rules.get('requirements', 'Approved template')}")
    
    with rule_col3:
        st.markdown("**📱 Push**")
        push_rules = copy_rules.get('push', {})
        st.markdown(f"- Length: {push_rules.get('words', '12-14 words')}")
        st.markdown(f"- Structure: {push_rules.get('structure', '1 hook + 1 benefit')}")
    
    st.markdown("---")
    st.markdown("### Safety Rules")
    for rule in copy_rules.get('safety_rules', []):
        st.markdown(f"- {rule}")

# Batch operations
st.markdown("---")
st.subheader("🔧 Batch Operations")

batch_col1, batch_col2, batch_col3 = st.columns(3)

with batch_col1:
    if st.button("📋 Copy All Messages", use_container_width=True):
        # Simulate copying all messages
        all_messages = {}
        for channel in ["email", "whatsapp", "push"]:
            variants = messages.get(channel, {}).get("variants", [])
            if variants:
                variant = variants[0]
                all_messages[channel] = {
                    "title": variant.get("title", ""),
                    "body": variant.get("body", "")
                }
        
        st.success("✅ All messages copied to clipboard!")
        with st.expander("📝 View copied content"):
            st.json(all_messages)

with batch_col2:
    if st.button("🔄 Regenerate All", use_container_width=True):
        st.info("🔄 Regenerating all messages... (Feature coming soon)")

with batch_col3:
    if st.button("📤 Export Copy Pack", use_container_width=True):
        st.session_state.selected_group = selected_group
        st.switch_page("pages/5_Exports.py")

# Grounding source
st.markdown("---")
st.caption("Grounded by: brand_voice.md • offer_policy.md • compliance.md")

# Navigation
st.markdown("---")
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("← Groups", use_container_width=True):
        st.switch_page("pages/2_Groups.py")

with nav_col2:
    if st.button("💰 Calculate ROI", use_container_width=True):
        st.switch_page("pages/4_ROI.py")

with nav_col3:
    if st.button("Exports →", use_container_width=True):
        st.switch_page("pages/5_Exports.py")