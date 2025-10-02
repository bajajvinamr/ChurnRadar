"""
Help Page - Comprehensive documentation and glossary.
"""
import streamlit as st
from churn_core.content import load_help, get_copy_rules, load_strings

st.set_page_config(page_title="Help - Churn Radar", page_icon="❓", layout="wide")

st.title("❓ Help & Documentation")
st.markdown("**Everything you need to know**")

# Load content
help_content = load_help()
strings = load_strings()

# Display help tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Overview & Guide",
    "📊 Cohort Library", 
    "✍️ Copy Rules",
    "📚 Glossary"
])

with tab1:
    # Full help content
    st.markdown(help_content)

with tab2:
    # Cohort library section from help
    st.markdown("## Cohort Library")
    st.markdown("### What are these groups?")
    st.markdown("""
Each cohort represents a specific customer segment with unique characteristics and needs. 
Here's what they mean and how to approach them:
    """)
    
    # Payment-Sensitive Lapsed
    with st.expander("1. Payment-Sensitive Lapsed"):
        st.markdown("**Who:** Uses coupons/cashback; last seen ~7–30 days.")
        st.markdown("**Why it matters:** Light incentives nudge them back without eroding margin.")
        st.markdown("**What to say:** Value and bundles; avoid heavy discounts.")
        st.markdown("**Archetype:** ValueSensitive")
    
    # High-Tenure, Recently Dropped
    with st.expander("2. High-Tenure, Recently Dropped"):
        st.markdown("**Who:** With us 12+ months; last seen ~7–30 days.")
        st.markdown("**Why it matters:** Long relationship deserves respectful approach.")
        st.markdown("**What to say:** Appreciation + 'pick up where you left off'; avoid discounts first.")
        st.markdown("**Archetype:** Loyalist")
    
    # Premium Engagement, Now Quiet
    with st.expander("3. Premium Engagement, Now Quiet"):
        st.markdown("**Who:** Top 30% by Activity; last seen ~5–20 days.")
        st.markdown("**Why it matters:** High-value customers who engage deeply with your brand.")
        st.markdown("**What to say:** Curated picks, white-glove tone; no discounts.")
        st.markdown("**Archetype:** Premium")
    
    # At-Risk High-Value
    with st.expander("4. At-Risk High-Value"):
        st.markdown("**Who:** High spenders showing signs of lapse; status 'At-Risk'.")
        st.markdown("**Why it matters:** Valuable customers you're about to lose.")
        st.markdown("**What to say:** Quick restart, low friction, reassure service.")
        st.markdown("**Archetype:** AtRisk")
    
    # One-and-Done Buyers
    with st.expander("5. One-and-Done Buyers"):
        st.markdown("**Who:** Single-order customers nearing 20–40 days.")
        st.markdown("**Why it matters:** Critical window for converting to repeat buyers.")
        st.markdown("**What to say:** First-repeat nudge with light incentive or bundle.")
        st.markdown("**Archetype:** ValueSensitive")
    
    # Service-Sensitive
    with st.expander("6. Service-Sensitive"):
        st.markdown("**Who:** Lower satisfaction or recent complaints.")
        st.markdown("**Why it matters:** Service issues are blocking reactivation.")
        st.markdown("**What to say:** 'We fixed it' + faster delivery/tracking; small apology credit ok.")
        st.markdown("**Archetype:** ServiceSensitive")
    
    # Additional cohorts
    st.info("💡 The system supports 10 standard cohorts plus custom micro-cohorts based on your data.")

with tab3:
    # Copy rules
    copy_rules = get_copy_rules()
    
    st.markdown(f"## {copy_rules.get('title', 'How We Write')}")
    st.markdown(f"**Tone:** {copy_rules.get('tone', 'Helpful and clear')}")
    
    st.markdown("---")
    st.markdown("### Channel-Specific Guidelines")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📧 Email")
        email_rules = copy_rules.get('email', {})
        st.markdown(f"""
- **Subject line:** ≤ {email_rules.get('subject_max', 50)} characters
- **Key info:** First {email_rules.get('subject_key_info', 33)} characters
- **Body:** ≤ {email_rules.get('body_max_words', 110)} words
- **CTAs:** Exactly {email_rules.get('cta_count', 1)}
        """)
    
    with col2:
        st.markdown("#### 💬 WhatsApp")
        wa_rules = copy_rules.get('whatsapp', {})
        st.markdown(f"""
- **Length:** {wa_rules.get('words', '25-30 words')}
- **Requirements:** {wa_rules.get('requirements', 'Approved template')}
- **Compliance:** Opt-in users only
        """)
    
    with col3:
        st.markdown("#### 📱 Push Notification")
        push_rules = copy_rules.get('push', {})
        st.markdown(f"""
- **Length:** {push_rules.get('words', '12-14 words')}
- **Structure:** {push_rules.get('structure', '1 hook + 1 benefit')}
- **Format:** Keep payload tiny
        """)
    
    st.markdown("---")
    st.markdown("### Safety Rules")
    
    safety_rules = copy_rules.get('safety_rules', [])
    for rule in safety_rules:
        st.markdown(f"- {rule}")
    
    st.markdown("---")
    st.markdown("### Safe Personalization Tokens")
    
    tokens = copy_rules.get('safe_tokens', [])
    st.markdown("You can safely use these tokens in messages:")
    for token in tokens:
        st.code(token, language="text")

with tab4:
    # Glossary
    st.markdown("## Glossary")
    st.markdown("### Core Metrics")
    
    glossary = strings.get('glossary', {})
    columns = strings.get('columns', {})
    
    # Display column definitions
    for key, info in columns.items():
        with st.expander(f"**{info.get('label', key)}**"):
            st.markdown(info.get('tooltip', 'No definition available.'))
    
    st.markdown("---")
    st.markdown("### Business Terms")
    
    # Display glossary terms
    for key, term_info in glossary.items():
        with st.expander(f"**{term_info.get('term', key)}**"):
            st.markdown(term_info.get('definition', 'No definition available.'))

# Navigation footer
st.markdown("---")
st.markdown("### Need More Help?")

help_col1, help_col2, help_col3 = st.columns(3)

with help_col1:
    if st.button("🏠 Back to Overview", use_container_width=True):
        st.switch_page("app.py")

with help_col2:
    if st.button("👥 View Groups", use_container_width=True):
        st.switch_page("pages/2_Groups.py")

with help_col3:
    if st.button("📤 Exports", use_container_width=True):
        st.switch_page("pages/5_Exports.py")

# Footer
st.markdown("---")
st.caption("Built with ❤️ by the Growth Team • Churn Radar Help System")
