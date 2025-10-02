"""
Consultant-friendly definitions and content for Churn Radar UI.
"""

# Tooltip definitions for metrics
METRIC_DEFINITIONS = {
    "come_back_odds": {
        "title": "Come-Back Odds (%)",
        "definition": "A 0–100 score estimating how likely this group is to return if we reach out now.",
        "how_computed": "Combines past orders, recent activity, time away, spend signals, and satisfaction into one number.",
        "why_matters": "Higher odds → higher chance of immediate revenue from win-back."
    },
    "last_seen": {
        "title": "Last Seen (days)",
        "definition": "Average days since the group's last order.",
        "note": "Shorter is 'warm', longer is 'cold'."
    },
    "activity": {
        "title": "Activity",
        "definition": "How much time this group spends with us (app/web) and devices used.",
        "note": "It's a proxy for engagement."
    },
    "avg_spend": {
        "title": "Avg Spend (₹)",
        "definition": "Average money per purchase for this group (or a proxy built from cashback/coupons/spend uplift)."
    },
    "months_with_brand": {
        "title": "Months with Brand",
        "definition": "Average tenure. Longer = stronger relationship; deserves respectful tone and fewer discounts."
    },
    "net_profit": {
        "title": "Net Profit (₹)",
        "definition": "Projected profit after margin, sending costs, and any incentives, over 30 days."
    },
    "archetype": {
        "title": "Archetype",
        "definition": "A shortcut label describing what usually moves this group (e.g., Premium, ValueSensitive).",
        "note": "Helps pick tone and offer."
    }
}

# Archetype-based one-line reasons
ARCHETYPE_REASONS = {
    "ValueSensitive": "Responds to value—try bundles/cashback, keep it light.",
    "Loyalist": "Long relationship—remind and appreciate, no discount needed.",
    "Premium": "High activity and recently lapsed—curate, don't discount.",
    "AtRisk": "Close to churning—one-tap reorder, reduce friction.",
    "ServiceSensitive": "Reassure: faster delivery, better tracking, small apology credit."
}

# Cohort library definitions
COHORT_LIBRARY = {
    "Payment-sensitive churners": {
        "who": "Uses coupons/cashback; last seen ~7–30 days.",
        "why_matters": "Light incentives nudge them back without eroding margin.",
        "say": "Value and bundles; avoid heavy discounts."
    },
    "High-tenure recent drop": {
        "who": "With us 12+ months; last seen ~7–30 days.",
        "say": "Appreciation + 'pick up where you left off'; avoid discounts first."
    },
    "Premium engagement lapsed": {
        "who": "Top 30% by Activity; last seen ~5–20 days.",
        "say": "Curated picks, white-glove tone; no discounts."
    },
    "AtRisk High-Value": {
        "who": "High spenders showing signs of lapse; status 'At-Risk'.",
        "say": "Quick restart, low friction, reassure service."
    }
}

# Message copy rules
COPY_RULES = {
    "tone": "Helpful, clear, benefit-first. No hype, no dark patterns.",
    "email": {
        "subject": "≤ 50 chars, key info in the first 33",
        "body": "≤ 110 words",
        "cta": "1 CTA"
    },
    "whatsapp": {
        "length": "25–30 words",
        "policy": "approved template, opt-in only"
    },
    "push": {
        "length": "12–14 words",
        "structure": "1 hook + 1 benefit + 1 verb"
    },
    "banned_phrases": ["guaranteed", "last chance", "only today", "free for everyone"],
    "safe_tokens": ["{{last_category}}", "{{top_device}}", "{{bundle_hint}}", "{{tenure_months}}"],
    "eval_badge": "Brand-safe ✓ · Eval 4.5★ = passed clarity, on-brand, relevance, safety"
}

# Regenerate options
REGENERATE_OPTIONS = {
    "tone": ["Premium", "Value", "Service Fix"],
    "offer": ["None", "Light incentive"],
    "length": ["Short", "Standard"],
    "angle": ["Curated picks", "Bundle value", "We fixed it"]
}