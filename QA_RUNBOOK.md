# Churn Radar — Agent QA Checklist (CEO-Proof Demo)

> Goal: a first-time marketer/CEO can open the app, understand it in one pass, steer copy, export assets, and find **zero** rough edges.

---

## 0) Pre-Flight (blocking)

* [ ] **Repo**: correct branch/tag for demo (`main` or `demo-v1`), clean `git status`.
* [ ] **Python**: 3.10+; `python -V` prints expected.
* [ ] **Env file**: `.env` with **OPENAI_API_KEY**, **DATASET_PATH**, **USE_RAG=true**, **TZ=Asia/Kolkata**.
* [ ] **Install**: `pip install -r requirements.txt` completes without errors/warnings.
* [ ] **No dummies**: grep shows **no** `DummyClient`/synthetic data paths.
* [ ] **Brand kit**: `brand_kit/` contains required docs (voice, offer_policy, do_dont, examples).
* [ ] **Dataset**: CSV/XLSX exists, ≥ 1,000 rows, columns match sample headers.

---

## 1) Data Intake & Processing

* [ ] **Load**: app loads the dataset from **DATASET_PATH** without prompts.
* [ ] **Canonicalize**: aliases map correctly (e.g., `hourspendonapp` → `HourSpendOnApp`).
* [ ] **Imputation**: numeric NAs → median, categoricals → `"Unknown"`.
* [ ] **Dedup**: on `CustomerID` (keep last); counts printed (before/after).
* [ ] **Derived**: `MonetaryValue`, `Engagement`, `SatisfactionMinusComplain` computed.
* [ ] **Score**: `ResurrectionScore` ∈ [0,1] for all rows; distribution not degenerate.
* [ ] **Processing summary** visible (rows, nulls, columns detected).

---

## 2) Cohorts & Micro-Segmentation

* [ ] **Preset cohorts** (4+): Payment-Sensitive, High-Tenure Drop, Premium Lapsed, At-Risk High-Value appear; non-empty (or meaningful empty state).
* [ ] **Top-3** by **Net Profit** shown on first render; each with a **one-line reason**.
* [ ] **Micro-cohorts** (if enabled): `CohortID` assigned; no runtime warnings.

---

## 3) Output Layer (one-screen story)

**Top tiles**

* [ ] **Recoverable Profit (30d)** shows a rupee value formatted as **₹12,34,567**.
* [ ] **Ready Groups Today** shows an integer ≥ 1.
* [ ] **Expected Reactivations** shows an integer; matches assumptions.

**Where to Start (Top-3 table)**

* [ ] Columns: Group · People · **Last Seen (days)** · **Come-Back Odds (%)** · **Net Profit (₹)**.
* [ ] Sorted by **Net Profit** (desc).
* [ ] Row subtitle = plain "why" sentence (archetype aware).

**Group Passport (selected row)**

* [ ] Exactly **6 facts**: People, Come-Back Odds, Last Seen, Activity, Avg Spend, Months with Brand.
* [ ] **Archetype chip** + one-line guidance (e.g., "Curate, don't discount.").

**ROI Waterfall**

* [ ] Bars labeled: **Revenue → × Margin → − Costs → − Incentives → Net Profit (green)**.
* [ ] Caption shows **assumptions** (rr, AOV, margin) with values.

**Labels/Definitions**

* [ ] All terms plain language; **tooltips** present for Come-Back Odds, Last Seen, Activity, Avg Spend, Months with Brand, Net Profit, Archetype.

---

## 4) Messaging (Generation → Judge → Keep)

* [ ] **Three channels** render a **kept variant**: Email, WhatsApp, Push.
* [ ] Each card displays **Brand-safe ✓ · Eval X★** badge (X ≥ 3.8 overall, Safety ≥ 4.0).
* [ ] **Email**: subject ≤ 50 chars (key in ≤33), body ≤ 110 words, single CTA.
* [ ] **WhatsApp**: 25–30 words, one CTA, template-safe (no dynamic forbidden terms).
* [ ] **Push**: 12–14 words, hook + benefit + verb.
* [ ] **Banned phrases** absent: "guaranteed", "last chance", "only today", "free for everyone".
* [ ] **No PII** tokens present; only safe tokens (e.g., `{{last_category}}`) display.

---

## 5) Regenerate Flow (operator control)

* [ ] **Panel** shows controls: Tone (Premium/Value/Service), Offer (None/Light), Length (Short/Standard), Angle (Curated/Bundle/ServiceFix), Avoid words (chips).
* [ ] Clicking **Regenerate** returns up to **3 candidates** quickly (< 5s each).
* [ ] All candidates evaluated; failing ones are hidden or marked with reason.
* [ ] **Keep** updates the card and **copy_pack.json** (with `_eval` + `regen_meta`).
* [ ] If **all fail**, assistant suggests knob changes; a safe fallback appears.

---

## 6) RAG & Brand Safety

* [ ] RAG **ON**: prompts show "Grounded by: voice.md, offer_policy.md" note (or in logs).
* [ ] Removing a brand doc → app **fails fast** with a helpful error ("Add brand_kit docs or disable RAG").
* [ ] Messages reflect brand tone/offer policy (e.g., Premium → no discounts).

---

## 7) Accessibility & Visual Quality

* [ ] **No legends**; every chart label is **direct** on bars/lines.
* [ ] **Contrast ≥ 4.5:1** in dark/light modes.
* [ ] Numbers use **Indian grouping**, % with **1 decimal**; zero values hidden if noisy.
* [ ] At **125% zoom**, whole story fits one screen without scrolling on 13" display.

---

## 8) Empty States & Errors

* [ ] **No data**: friendly prompt with "See sample headers" link.
* [ ] **No cohorts ready**: "No groups meet the bar today…" explanatory text.
* [ ] **Eval failures**: guided suggestion ("Try Service tone / Short length").
* [ ] **WhatsApp** missing template/opt-in: block with guidance; email/push suggested.
* [ ] **API key missing**: hard stop with remediation (set OPENAI_API_KEY).

---

## 9) Exports (delivery-ready)

* [ ] **Per-cohort CSV** schema: `CustomerID, ComeBackOdds, LastSeenDays, OrderCount, Engagement, AvgSpend, TenureMonths`.
* [ ] **copy_pack.json v1.1**: one kept variant per channel + UTM + assumptions; valid JSON.
* [ ] **manifest.json**: run_id, dataset meta, summaries, thresholds, assumptions, IST timestamp.
* [ ] Paths shown in UI; files open without errors.

---

## 10) Performance & Stability

* [ ] End-to-end run on 10k rows (load → cohorts → messages → ROI) **≤ 15s**.
* [ ] Regenerate latency per channel **≤ 5s avg**, **≤ 10s p95**.
* [ ] LLM calls retried **≤ 2×**; timeouts **20s**; user sees spinner + status.
* [ ] No memory spikes; UI remains responsive.

---

## 11) Privacy & Security

* [ ] No PII in prompts/logs (inspect last 10 logs).
* [ ] Keys never logged; `.env` not checked into VCS.
* [ ] WhatsApp: only show/send content that fits **approved marketing template** model (text structure OK).

---

## 12) Telemetry (for the demo & CEO test)

* [ ] Top-bar mini metrics visible (or accessible): **Eval pass-rate**, **Time-to-ready**, **Manual-edit rate** for this session.
* [ ] `logs/conversation.jsonl` records tool calls (no PII), durations, errors.
* [ ] A **"Demo Mode: ON"** info line shows dataset name, record count, last export time.

---

## 13) CEO "Reality Test" Scenarios (must pass)

1. **Open app → Understand in 60s**

   * Reads tiles and Top-3; clicks first row; sees Passport, Messages, Waterfall; says "Got it."
2. **Change tone & keep a message**

   * Opens Regenerate, sets Tone=Service, Length=Short, clicks Keep. Card updates with badge.
3. **Definitions on demand**

   * Hovers ⓘ on Come-Back Odds and reads a plain definition.
4. **Export**

   * Clicks Export; receives CSV + copy_pack.json + manifest.json; opens them.
5. **Edge case**

   * Selects a cohort with small size; UI still looks clean; messages pass eval or provide a safe fallback.

---

## 14) Dry-Run Script (agent rehearsal)

* [ ] Start with banner: "We rank today's best customer groups to re-activate…"
* [ ] Point to **Recoverable Profit**, then Top-3 ladder.
* [ ] Click **Premium Lapsed** → read Passport (6 facts) → archetype line.
* [ ] Read **Email** kept message; hit **Regenerate** (Value tone) → Keep #1.
* [ ] Show **ROI Waterfall**; read assumptions; sensitivity tweak (if available).
* [ ] **Export**; open files; end with the 3 next steps (send via ESP/WA, track results, learn).

---

## 15) Rollback & Recovery

* [ ] If LLM API fails: messages show a clear banner; advise to retry or check key/network.
* [ ] If RAG fails: show action to **disable RAG** or **add brand docs** (toggle in settings).
* [ ] If dataset malformed: show sample header schema + quick fix link.

---

## 16) Final Go/No-Go Gate

* [ ] All sections above checked ✅.
* [ ] A non-engineer (internal marketer) did a **blind test** and completed: understand → regenerate → export in < 5 minutes.
* [ ] No textual typos, no broken links, no console errors.

---

### Sign-off

* **QA Agent:** __________  Date/Time: __________
* **Owner (Growth Eng):** __________
* **Demo Host:** __________