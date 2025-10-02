# Churn Radar — Help & Guidance

## What You're Seeing

We rank today's best customer groups to re-activate, show the most effective messages to send, and estimate the profit if you act now. Click a group to see facts, copy, and money impact.

---

## Cohort Library

### What are these groups?

Each cohort represents a specific customer segment with unique characteristics and needs. Here's what they mean and how to approach them:

#### 1. Payment-Sensitive Lapsed
**Who:** Uses coupons/cashback; last seen ~7–30 days.

**Why it matters:** Light incentives nudge them back without eroding margin.

**What to say:** Value and bundles; avoid heavy discounts.

**Archetype:** ValueSensitive

---

#### 2. High-Tenure, Recently Dropped
**Who:** With us 12+ months; last seen ~7–30 days.

**Why it matters:** Long relationship deserves respectful approach.

**What to say:** Appreciation + "pick up where you left off"; avoid discounts first.

**Archetype:** Loyalist

---

#### 3. Premium Engagement, Now Quiet
**Who:** Top 30% by Activity; last seen ~5–20 days.

**Why it matters:** High-value customers who engage deeply with your brand.

**What to say:** Curated picks, white-glove tone; no discounts.

**Archetype:** Premium

---

#### 4. At-Risk High-Value
**Who:** High spenders showing signs of lapse; status "At-Risk".

**Why it matters:** Valuable customers you're about to lose.

**What to say:** Quick restart, low friction, reassure service.

**Archetype:** AtRisk

---

#### 5. One-and-Done Buyers
**Who:** Single-order customers nearing 20–40 days.

**Why it matters:** Critical window for converting to repeat buyers.

**What to say:** First-repeat nudge with light incentive or bundle.

**Archetype:** ValueSensitive

---

#### 6. Service-Sensitive
**Who:** Lower satisfaction or recent complaints.

**Why it matters:** Service issues are blocking reactivation.

**What to say:** "We fixed it" + faster delivery/tracking; small apology credit ok.

**Archetype:** ServiceSensitive

---

#### 7. Seasonal Purchasers
**Who:** Past purchases tied to seasons/festivals; now lapsed.

**Why it matters:** Timing is everything for these customers.

**What to say:** Timely season picks; calendar-led reminders.

**Archetype:** ValueSensitive or Premium (context-dependent)

---

#### 8. Category Loyalists
**Who:** Repeat buying in one category (e.g., Electronics).

**Why it matters:** Deep category affinity presents upsell opportunities.

**What to say:** Replenishment cues and category-specific upsell.

**Archetype:** Loyalist

---

#### 9. High AOV, Infrequent
**Who:** Big spend when they buy, but low frequency.

**Why it matters:** Each purchase is valuable; need confidence-building.

**What to say:** Ensure confidence (warranty, support); curated carts.

**Archetype:** Premium

---

#### 10. COD-Only, At-Risk
**Who:** Cash-on-Delivery preference, now lapsed.

**Why it matters:** Payment preference indicates trust concerns.

**What to say:** Trust signals, hassle-free returns, alternative payments.

**Archetype:** ServiceSensitive

---

## Message Copy Rules

### How We Write

**Tone:** Helpful, clear, benefit-first. No hype, no dark patterns.

### Channel-Specific Guidelines

#### Email
- **Subject Line:** Keep key info in first **33 characters**; don't exceed **50 characters**
- **Body:** Maximum **110 words**
- **CTA:** Exactly **1 clear call-to-action**
- **Format:** Text + optional HTML; mobile-first design

#### WhatsApp
- **Length:** 25–30 words maximum
- **Requirement:** Must use **approved marketing templates**
- **Compliance:** Send only to **opt-in users**
- **Format:** Plain text; emoji allowed sparingly

#### Push Notification
- **Length:** 12–14 words (approximately 30–40 characters per line)
- **Structure:** 1 hook + 1 benefit + 1 verb
- **Payload:** Keep tiny for fast delivery
- **Timing:** Respect user preferences and time zones

### Safety Rules

**Never use these phrases:**
- "guaranteed"
- "last chance" 
- "only today"
- "free for everyone"

**Always follow:**
- No dark patterns or deceptive tactics
- No high-pressure language
- One clear CTA per message
- Respect brand voice and guidelines

### Safe Personalization Tokens

You can safely use these tokens in messages:
- `{{last_category}}` — Last category purchased
- `{{top_device}}` — Most-used device
- `{{bundle_hint}}` — Suggested bundle based on history
- `{{tenure_months}}` — Months as customer

### Message Quality Evaluation

Every message is scored by LLM-as-Judge on:
- **Clarity** (0–5) — Easy to understand
- **On-Brand** (0–5) — Matches brand voice
- **Persuasiveness** (0–5) — Motivates action
- **Relevance** (0–5) — Right for the audience
- **Safety** (0–5) — Complies with guidelines

**Passing thresholds:**
- Overall score ≥ 3.8/5
- Safety score ≥ 4.0/5

Messages are automatically marked as **Brand-safe ✓** when they pass all checks.

---

## Glossary

### Core Metrics

**Come-Back Odds (%)**
A 0–100 score estimating how likely this group is to return if we reach out now. Combines past orders, recent activity, time away, spend signals, and satisfaction.

**Last Seen (days)**
Average days since the group's last order. Shorter is "warm", longer is "cold".

**Activity**
How much time this group spends with us (app/web) and devices used. It's a proxy for engagement.

**Avg Spend (₹)**
Average money per purchase for this group (or a proxy built from cashback/coupons/spend uplift).

**Months with Brand**
Average tenure. Longer = stronger relationship; deserves respectful tone and fewer discounts.

**Net Profit (₹)**
Projected profit after margin, sending costs, and any incentives, over 30 days.

### Business Terms

**Reactivation Rate**
Percentage of this group we expect to return after outreach. Based on historical data and group characteristics.

**AOV (Average Order Value)**
Average revenue per order. Used to project potential revenue from reactivations.

**Margin**
Percentage of sales kept after cost of goods. Critical for calculating actual profit vs. just revenue.

**Incentive**
Discount or credit offered to nudge a purchase. We keep it light to protect margins.

**ROMI (Return on Marketing Investment)**
How many rupees of profit you get for each rupee spent on marketing. Formula: Net Profit ÷ Marketing Costs.

### Technical Terms

**Archetype**
A shortcut label describing what usually moves this group (e.g., Premium, ValueSensitive, Loyalist). Helps pick tone and offer strategy.

**Eval (LLM-as-Judge)**
Automated quality and safety review (0–5 stars) before we show copy. Ensures messages meet standards.

**Cohort**
A group of customers with similar characteristics and behaviors. We segment customers into cohorts for targeted messaging.

**Micro-Cohort**
Smaller, more specific customer segments created through machine learning clustering. Allows for hyper-targeted approaches.

---

## Understanding the Dashboard

### Top Metrics (Headline Tiles)

**Recoverable Profit (30d)**
This is the money on the table this month from all recommended groups. It's net profit after all costs.

**Ready Groups Today**
Number of groups that meet our quality bar and are worth contacting right now.

**Expected Reactivations**
Total number of customers we expect to win back if we act on all recommendations.

### Where to Start (Top Groups Table)

Groups are sorted by **Net Profit** (highest first). Each row shows:
- **Group name** — The cohort identifier
- **People** — How many customers
- **Last Seen** — Average days since last order
- **Come-Back Odds** — Likelihood to return (%)
- **Net Profit** — Money you can make (₹)

Below each group is a **one-line reason** explaining why this group matters and how to approach it.

### Group Passport

When you select a group, you see 6 key facts:
1. **People** — Audience size
2. **Come-Back Odds** — Return probability
3. **Last Seen** — Days since last order
4. **Activity** — Engagement level
5. **Avg Spend** — Purchase value
6. **Months with Brand** — Customer tenure

Plus an **Archetype** chip with guidance on tone and offers.

### Ready-to-Send Messages

For each channel (Email, WhatsApp, Push), we show:
- **One kept variant** that passed quality checks
- **Brand-safe ✓** badge — Message meets all safety requirements
- **Eval score** — Quality rating from LLM-as-Judge

You can **Regenerate** messages with different tone, length, or angle settings.

### ROI Waterfall

Shows the path from revenue to net profit:
1. **Revenue** (Reactivations × AOV)
2. **× Margin** (Gross profit)
3. **− Sending Costs** (Email, SMS, etc.)
4. **− Incentives** (Discounts, credits)
5. **= Net Profit** (What you actually make)

Caption shows the assumptions used (reactivation rate, AOV, margin).

---

## Regenerate Panel

When regenerating messages, you can control:

**Tone**
- Premium — Sophisticated, curated, quality-focused
- Value — Practical, straightforward, benefit-focused
- Service Fix — Supportive, reassuring, problem-solving

**Offer**
- None — No discount or incentive
- Light — Small incentive (e.g., ₹100 credit, 10% off)

**Length**
- Short — Concise, quick read
- Standard — Normal length with more detail

**Angle**
- Curated Picks — Personalized recommendations
- Bundle Value — Combined offers and savings
- Service Fix — Problem resolution focus

**Avoid Words**
Add phrases or words to ban from the message (e.g., "sale", "urgent").

The system generates up to **3 candidates**, scores them, and shows the best ones. You can **Keep** your favorite.

---

## Export Schemas

### Per-Group CSV
Contains customer IDs and key metrics:
- CustomerID
- ComeBackOdds (0–1 scale)
- LastSeenDays
- OrderCount
- Engagement (normalized index)
- AvgSpend (₹)
- TenureMonths

### copy_pack.json
Contains kept message variants with evaluation scores:
```json
{
  "cohort": "Premium engagement lapsed",
  "archetype": "Premium",
  "audience_size": 8412,
  "channels": {
    "email": {
      "variant": {
        "title": "Your curated picks are ready",
        "body": "...",
        "_eval": {"overall": 4.6}
      }
    }
  },
  "assumptions": {
    "reactivation_rate": 0.12,
    "aov": 1800,
    "margin": 0.62
  }
}
```

### manifest.json
Contains run metadata:
- Run ID and timestamp
- Dataset name and record counts
- Model version used
- Thresholds and assumptions
- List of groups processed

---

## Tips & Best Practices

### When to Act
- **High Come-Back Odds** (>40%) — Act immediately
- **Recent lapse** (<14 days) — Timing is critical
- **High Net Profit** — Prioritize these groups first

### Message Strategy
- **Premium customers** — Never lead with discounts
- **Loyalists** — Show appreciation, remind of history
- **At-Risk** — Remove friction, make comeback easy
- **Value-Sensitive** — Clear savings, but keep light

### Testing Approach
- Start with top 1–2 groups
- Use standard messages first
- Monitor response rates for 3–5 days
- Adjust tone/offer based on results
- Scale successful approaches to similar groups

### Compliance
- Always use **opt-in lists** for WhatsApp
- Respect **unsubscribe** preferences
- Follow **brand guidelines** in all messages
- Review **eval scores** before sending
- Document **assumptions** in exports

---

## Need Help?

- **Empty screen?** Check that `run_churn_radar.py` has been executed
- **No groups showing?** Adjust minimum thresholds or check data quality
- **Messages failing?** Try different tone/length combinations
- **WhatsApp blocked?** Ensure templates are approved and users opted in

For technical support, see the main README.md documentation.
