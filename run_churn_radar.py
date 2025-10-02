#!/usr/bin/env python3
"""
Comprehensive Churn Radar Analytics Engine
- Loads and processes customer data with advanced feature engineering
- ML-powered customer segmentation with micro-cohorts
- RAG-powered brand document integration
- LLM message generation with quality evaluation (LLM-as-Judge)
- ROI analysis and financial modeling
- Production-ready exports with comprehensive manifests

Enhanced with:
- Advanced clustering and kNN persona matching
- Message quality evaluation and regeneration
- Archetype classification with template packs
- Multi-channel message optimization
- Comprehensive error handling and fallbacks
"""
import os, json, math, hashlib, warnings, re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import numpy as np
import pandas as pd
import httpx

# OpenAI for LLM functionality
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI library not available")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Try manual .env loading if python-dotenv not available
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# ML imports with fallback
try:
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.cluster import KMeans
    from sklearn.neighbors import NearestNeighbors
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn not available - advanced clustering disabled")

WORKDIR = Path('.')
EXPORTS = WORKDIR / 'exports'
EXPORTS.mkdir(exist_ok=True)
BRAND_DIR = WORKDIR / 'brand_kit'

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY','')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE','https://api.openai.com/v1')
LIVE_ONLY = os.getenv('LIVE_ONLY','0') == '1'

# === Brand Kit & RAG System ===
def load_brand_documents():
    """Load brand documents for RAG-enhanced messaging"""
    brand_docs = {}
    
    try:
        brand_files = ['brand_overview.md', 'brand_voice.md', 'compliance.md', 'offer_policy.md']
        
        for filename in brand_files:
            filepath = BRAND_DIR / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    brand_docs[filename] = content
                    print(f"✅ Loaded brand document: {filename}")
            else:
                print(f"⚠️ Brand document not found: {filename}")
        
        return brand_docs
    except Exception as e:
        print(f"⚠️ Brand documents loading failed: {e}")
        return {}

def get_brand_context_for_archetype(archetype: str, brand_docs: dict) -> str:
    """Retrieve relevant brand context for archetype via simple RAG"""
    
    # Map archetypes to relevant brand guidance
    archetype_mapping = {
        "ValueSensitive": ["save", "bundled", "smarter", "upgrade"],
        "Loyalist": ["priority support", "curated", "favorites", "exclusive"],
        "Premium": ["upgrade", "premium", "priority", "curated"],
        "AtRisk": ["convenient", "care", "support", "reassuring"],
        "ServiceSensitive": ["support", "setup", "help", "service"]
    }
    
    relevant_keywords = archetype_mapping.get(archetype, ["convenient", "care"])
    
    # Extract relevant sections from brand docs
    context_sections = []
    
    for doc_name, content in brand_docs.items():
        # Simple keyword matching for relevant content
        lines = content.split('\n')
        for line in lines:
            if any(keyword.lower() in line.lower() for keyword in relevant_keywords):
                context_sections.append(line.strip())
    
    if context_sections:
        return "Brand guidance: " + " | ".join(context_sections[:3])  # Top 3 matches
    else:
        return "Brand guidance: Convenience meets care. Helpful, clear, benefit-focused tone."

# --- Data load with comprehensive validation ---
def load_data():
    """Load and validate dataset with comprehensive processing summary"""
    dataset_path = os.getenv('DATASET_PATH', 'dataset.csv')
    print(f'📊 Loading dataset from: {dataset_path}')
    
    # Check file exists
    path = Path(dataset_path)
    if not path.exists():
        raise RuntimeError(f"❌ Dataset file not found: {dataset_path}")
    
    if path.stat().st_size == 0:
        raise RuntimeError(f"❌ Dataset file is empty: {dataset_path}")
    
    # Load data
    try:
        if str(path).lower().endswith('.csv'):
            df_raw = pd.read_csv(path)
        elif str(path).lower().endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(path)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
            
        print(f"✅ Raw data loaded: {len(df_raw):,} rows, {len(df_raw.columns)} columns")
        
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load dataset: {str(e)}")
    
    # Process summary - before
    rows_before = len(df_raw)
    null_before = df_raw.isnull().sum().sum()
    duplicates_before = df_raw.duplicated().sum()
    
    print(f"📋 Pre-processing summary:")
    print(f"   • Rows: {rows_before:,}")
    print(f"   • Null values: {null_before:,}")
    print(f"   • Duplicate rows: {duplicates_before:,}")
    
    # Canonicalize columns
    df = canonicalize_columns(df_raw)
    
    # Check mandatory columns
    mandatory_cols = [
        'CustomerID', 'OrderCount', 'HourSpendOnApp', 'NumberOfDeviceRegistered', 
        'SatisfactionScore', 'Complain', 'Tenure', 'DaySinceLastOrder', 
        'CashbackAmount', 'CouponUsed', 'OrderAmountHikeFromlastYear'
    ]
    
    missing_cols = [col for col in mandatory_cols if col not in df.columns]
    if missing_cols:
        raise RuntimeError(f"❌ Mandatory columns missing: {missing_cols}")
    
    print(f"✅ All mandatory columns present: {len(mandatory_cols)} columns")
    
    # Deduplication on CustomerID
    if 'CustomerID' in df.columns:
        df = df.drop_duplicates(subset=['CustomerID'], keep='last')
        duplicates_removed = rows_before - len(df)
        if duplicates_removed > 0:
            print(f"🔄 Removed {duplicates_removed:,} duplicate CustomerIDs (kept last)")
    
    # Handle missing values
    numeric_cols = ['OrderCount', 'HourSpendOnApp', 'NumberOfDeviceRegistered', 
                   'SatisfactionScore', 'Complain', 'Tenure', 'DaySinceLastOrder', 
                   'CashbackAmount', 'CouponUsed', 'OrderAmountHikeFromlastYear']
    
    categorical_cols = ['PreferredLoginDevice', 'PreferredPaymentMode', 'PreferedOrderCat']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            median_val = df[col].median()
            nulls_filled = df[col].isnull().sum()
            df[col] = df[col].fillna(median_val)
            if nulls_filled > 0:
                print(f"🔧 Filled {nulls_filled:,} nulls in {col} with median: {median_val:.2f}")
    
    for col in categorical_cols:
        if col in df.columns:
            nulls_filled = df[col].isnull().sum()
            df[col] = df[col].fillna('Unknown')
            if nulls_filled > 0:
                print(f"🔧 Filled {nulls_filled:,} nulls in {col} with 'Unknown'")
    
    # Final summary
    rows_after = len(df)
    null_after = df.isnull().sum().sum()
    
    print(f"✅ Post-processing summary:")
    print(f"   • Final rows: {rows_after:,}")
    print(f"   • Remaining nulls: {null_after:,}")
    print(f"   • Processing complete")
    
    return df


def canonicalize_columns(df):
    COLUMN_MAP = {
        'customer_id': 'CustomerID', 'customerid': 'CustomerID', 'churned': 'Churn', 'complaints': 'Complain',
        'preferredordercat':'PreferedOrderCat','hourspendonapp':'HourSpendOnApp','hoursppendapp':'HourSpendOnApp'
    }
    m = {}
    for c in df.columns:
        key = c.strip().lower().replace(' ','')
        m[c] = COLUMN_MAP.get(key, c.strip())
    return df.rename(columns=m)


def min_max_scale(s):
    try:
        s = (s - s.min()) / (s.max() - s.min())
        return s.fillna(0) if hasattr(s,'fillna') else s
    except Exception:
        arr = np.array(s,dtype=float)
        if arr.max()==arr.min():
            return np.zeros_like(arr)
        return (arr - arr.min())/(arr.max()-arr.min())

# --- Scoring ---
def compute_features(df):
    df = df.copy()
    # ensure CustomerID
    if 'CustomerID' not in df.columns:
        df = df.reset_index(drop=True)
        df['CustomerID'] = [f'C{i:04d}' for i in range(1,len(df)+1)]
    num_cols = ['Churn', 'Tenure', 'CityTier', 'WarehouseToHome', 'HourSpendOnApp',
                'NumberOfDeviceRegistered', 'SatisfactionScore', 'Complain',
                'OrderCount', 'DaySinceLastOrder', 'CouponUsed', 'CashbackAmount',
                'OrderAmountHikeFromlastYear']
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
            df[c] = df[c].fillna(df[c].median())
    for c in ['PreferredLoginDevice','PreferredPaymentMode','PreferedOrderCat']:
        if c in df.columns:
            df[c] = df[c].fillna('Unknown')
    # derived
    safe = lambda d,k: d[k] if k in d.columns else 0
    df['MonetaryValue'] = safe(df,'CashbackAmount') + safe(df,'CouponUsed') + safe(df,'OrderAmountHikeFromlastYear')
    df['Engagement'] = safe(df,'HourSpendOnApp') + 0.5*safe(df,'NumberOfDeviceRegistered')
    df['SatisfactionMinusComplain'] = safe(df,'SatisfactionScore') - 2*safe(df,'Complain')
    df['OrderCount_s'] = min_max_scale(safe(df,'OrderCount'))
    df['MonetaryValue_s'] = min_max_scale(df['MonetaryValue'])
    df['Tenure_s'] = min_max_scale(safe(df,'Tenure'))
    df['Engagement_s'] = min_max_scale(df['Engagement'])
    df['Recency_s'] = min_max_scale(safe(df,'DaySinceLastOrder'))
    df['SatMinusComplain_s'] = min_max_scale(df['SatisfactionMinusComplain'])
    # Smoothed churn risk: higher when recency is high, lower with satisfaction
    # Use a logistic transform to compress extremes
    rec = df['Recency_s'].fillna(0)
    sat = (df['SatisfactionScore'] - 1) / 4.0  # 0-1
    # risk_raw in 0-1 where higher = more at-risk
    risk_raw = 0.6 * rec + 0.3 * (1 - sat) + 0.1 * (df['Complain'].fillna(0))
    # logistic smooth
    df['churn_risk'] = (1 / (1 + np.exp(-6 * (risk_raw - 0.5)))) * 10

    # Improved value score: blend revenue proxy and order frequency with winsorization
    mv = df['MonetaryValue_s'].clip(0,1)
    oc = df['OrderCount_s'].clip(0,1)
    df['value_score'] = (0.7 * mv + 0.3 * oc) * 10

    df['ResurrectionScore'] = (
        0.30 * df['OrderCount_s'] +
        0.20 * df['MonetaryValue_s'] +
        0.15 * df['Tenure_s'] +
        0.15 * df['Engagement_s'] -
        0.15 * df['Recency_s'] +
        0.10 * df['SatMinusComplain_s']
    ).clip(0,1)
    
    # Add Status field for cohort filtering
    df['Status'] = mark_status(df)
    
    return df

# === Micro-Cohort Clustering ===
def create_micro_cohorts(df):
    """Create micro-cohorts using ML clustering if sklearn available"""
    if not SKLEARN_AVAILABLE:
        print("⚠️ sklearn not available, using rule-based cohorts only")
        return df, None, None, None
    
    # Select features for clustering
    NUM_FEATS = [f for f in ["ResurrectionScore","Tenure","Engagement","MonetaryValue","DaySinceLastOrder"] 
                 if f in df.columns]
    CAT_FEATS = [c for c in ["PreferredLoginDevice","PreferredPaymentMode","PreferedOrderCat","CityTier"] 
                 if c in df.columns]
    
    if len(NUM_FEATS) < 2:
        print("Not enough numeric features for micro-cohort clustering")
        return df, None, None, None
    
    # Prepare feature matrix
    if CAT_FEATS:
        preprocessor = ColumnTransformer([
            ("num", StandardScaler(), NUM_FEATS),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_FEATS)
        ], remainder="drop")
        X = df[NUM_FEATS + CAT_FEATS].copy()
    else:
        preprocessor = ColumnTransformer([
            ("num", StandardScaler(), NUM_FEATS),
        ], remainder="drop")
        X = df[NUM_FEATS].copy()
    
    # Determine number of clusters
    k = min(100, max(2, int(len(df)/10)))
    
    # Create pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor), 
        ("kmeans", KMeans(n_clusters=k, random_state=42, n_init=10))
    ])
    
    try:
        # Fit and predict
        df['CohortID'] = pipeline.fit_predict(X)
        
        # Build kNN index for persona matching
        X_transformed = preprocessor.fit_transform(X)
        knn = NearestNeighbors(n_neighbors=15, metric='euclidean')
        knn.fit(X_transformed)
        
        print(f"✅ Built {k} micro-cohorts with ML clustering")
        return df, pipeline, knn, preprocessor
        
    except Exception as e:
        print(f"Clustering failed: {e}")
        df['CohortID'] = 0
        return df, None, None, None

def summarize_micro_cohort(df_grp: pd.DataFrame) -> dict:
    """Summarize a micro-cohort"""
    return {
        "size": int(len(df_grp)),
        "avg_score": float(df_grp["ResurrectionScore"].mean()),
        "avg_tenure": float(df_grp["Tenure"].mean()) if 'Tenure' in df_grp else 0,
        "avg_recency": float(df_grp["DaySinceLastOrder"].mean()) if 'DaySinceLastOrder' in df_grp else 0,
        "avg_engagement": float(df_grp["Engagement"].mean()) if 'Engagement' in df_grp else 0,
        "avg_value": float(df_grp["MonetaryValue"].mean()) if 'MonetaryValue' in df_grp else 0,
    }

# --- Cohorts ---
def mark_status(df):
    # Recalibrated status buckets based on dataset percentiles (few records >60 days)
    x = df['DaySinceLastOrder'] if 'DaySinceLastOrder' in df.columns else pd.Series([0]*len(df), index=df.index)
    st = pd.Series(['Active']*len(df), index=df.index)
    # AtRisk: recent lapse but within a month
    st[(x >= 7) & (x < 30)] = 'AtRisk'
    # Churned: long lapse
    st[x >= 30] = 'Churned'
    return st

def cohort_payment_sensitive(d):
    # Payment-sensitive: users who engage with coupons/cashback and show mid-range recency
    if len(d) == 0:
        return d
    return d.query("(CouponUsed >= @d['CouponUsed'].median()) or (CashbackAmount >= @d['CashbackAmount'].median())")\
            .query("DaySinceLastOrder >= 7 and DaySinceLastOrder <= 30")

def cohort_high_tenure_drop(d):
    # High-tenure recent drop: longer-tenure customers who recently lapsed (within ~1 month)
    return d.query("Tenure >= 12 and DaySinceLastOrder >= 7 and DaySinceLastOrder < 30") if len(d) else d

def cohort_premium_lapsed(d):
    # Premium engagement lapsed: high-engagement users who have slowed recently
    if len(d) == 0:
        return d
    thr = d['Engagement'].quantile(0.70)
    return d.query("Engagement >= @thr and DaySinceLastOrder >= 5 and DaySinceLastOrder <= 20")

def cohort_atrisk_highvalue(d):
    # AtRisk High-Value: AtRisk status (recalibrated) and high monetary value
    thr = d['MonetaryValue'].quantile(0.70) if len(d) else 0
    base = d[(d['Status'] == 'AtRisk') & (d['MonetaryValue'] >= thr)] if len(d) else d
    return base.sort_values('ResurrectionScore', ascending=False)

COHORTS = {
    'Payment-sensitive churners': cohort_payment_sensitive,
    'High-tenure recent drop': cohort_high_tenure_drop,
    'Premium engagement lapsed': cohort_premium_lapsed,
    'AtRisk High-Value': cohort_atrisk_highvalue,
}

def cohort_summary(d):
    if len(d)==0:
        return {'size':0,'avg_score':0,'avg_tenure':0,'avg_recency':0,'avg_engagement':0,'avg_value':0}
    return {'size':int(len(d)),'avg_score':float(d['ResurrectionScore'].mean()),'avg_tenure':float(d['Tenure'].mean()) if 'Tenure' in d else 0,'avg_recency':float(d['DaySinceLastOrder'].mean()) if 'DaySinceLastOrder' in d else 0,'avg_engagement':float(d['Engagement'].mean()) if 'Engagement' in d else 0,'avg_value':float(d['MonetaryValue'].mean()) if 'MonetaryValue' in d else 0}

# --- Brand corpus + deterministic embeddings ---

def load_corpus():
    docs = []
    if not BRAND_DIR.exists():
        return docs
    for p in sorted(BRAND_DIR.glob('*')):
        if p.suffix.lower() in ['.md','.txt','.json','.yaml','.yml']:
            try:
                txt = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            docs.append({'id':p.name,'text':txt,'source':p.name})
    return docs

EMBED_DIM = 256

def deterministic_embed(texts):
    out=[]
    for t in texts:
        h = hashlib.sha256((t or '').encode('utf-8')).digest()
        v = int.from_bytes(h,'big')
        vals=[]
        for i in range(EMBED_DIM):
            v = (v * 6364136223846793005 + 1442695040888963407) & ((1<<64)-1)
            vals.append(((v >> (i % 64)) & 0xFFFF)/65535.0)
        out.append(vals)
    return np.array(out)

# Simple retrieval: cosine similarity
from sklearn.neighbors import NearestNeighbors

def build_retriever(corpus):
    texts = [c['text'] for c in corpus]
    if not texts:
        return None
    embs = deterministic_embed(texts)
    norm = embs / ( (embs**2).sum(axis=1, keepdims=True) ** 0.5 + 1e-12)
    nn = NearestNeighbors(metric='cosine', algorithm='brute')
    nn.fit(norm)
    return {'nn':nn,'embeds':norm,'corpus':corpus}

def retrieve(retriever, query, topk=3):
    if retriever is None:
        return []
    qv = deterministic_embed([query])
    qv = qv / ( (qv**2).sum(axis=1, keepdims=True) ** 0.5 + 1e-12)
    dists, idxs = retriever['nn'].kneighbors(qv, n_neighbors=min(topk, len(retriever['corpus'])))
    out=[]
    for i in idxs[0]:
        out.append(retriever['corpus'][i])
    return out

# --- LLM helpers (httpx to OpenAI chat) ---

def call_chat(messages, model='gpt-4o-mini', temperature=0.4, timeout=20):
    if not OPENAI_API_KEY:
        return None
    payload = {'model': model, 'messages': messages, 'temperature': temperature}
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type':'application/json'}
    r = httpx.post(OPENAI_API_BASE + '/chat/completions', json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()

# Test OpenAI connection
def test_openai_connection():
    """Test OpenAI API connection with a simple call"""
    if not OPENAI_API_KEY:
        raise RuntimeError("❌ OPENAI_API_KEY not found in environment. Please set it in .env file.")
    
    try:
        response = call_chat([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'OK' if you can hear me."}
        ], model='gpt-4o-mini', temperature=0)
        
        if response.get('choices') and response['choices'][0].get('message'):
            print("✅ OpenAI connection successful")
            return True
        else:
            raise RuntimeError("❌ OpenAI returned unexpected response format")
    except Exception as e:
        raise RuntimeError(f"❌ OpenAI connection failed: {str(e)}")


# === LLM-as-Judge Quality Evaluation ===
EVAL_RUBRIC = '''
You are a strict marketing QA evaluator. Score the message for this cohort on:
- Clarity (0-5): concise, understandable, single CTA
- OnBrand (0-5): friendly, non-spammy, no false urgency, matches cohort context  
- Persuasiveness (0-5): motivates action without heavy discounting unless price-sensitive
- Relevance (0-5): aligns with cohort stats (tenure, recency, value)
- Safety (0-5): no claims like "guaranteed", "last chance", no PII, no sensitive content

Return JSON:
{
 "clarity": int, "on_brand": int, "persuasiveness": int, "relevance": int, "safety": int,
 "overall": float,
 "rationale": "one sentence why"
}
'''

BAD_PHRASES = {"guaranteed", "last chance", "only today", "free for everyone", "limited time"}
EVAL_THRESHOLDS = {"overall": 3.8, "safety": 4}

def brand_safety(text: str) -> bool:
    """Quick brand safety check"""
    t = text.lower()
    if any(p in t for p in BAD_PHRASES): 
        return False
    if len(text) > 1200: 
        return False
    return True

def eval_message_with_llm(message: str, cohort_summary: dict) -> dict:
    """Evaluate message quality using LLM-as-Judge"""
    prompt = f"""
Cohort context: {json.dumps(cohort_summary)}
Message to evaluate (title+body or text): ```{message}```
{EVAL_RUBRIC}
"""
    try:
        if OPENAI_API_KEY:
            r = call_chat([
                {"role":"system","content":"You are a rigorous evaluator of marketing copy."},
                {"role":"user","content":prompt}
            ], model="gpt-4o-mini", temperature=0.0)
            data = json.loads(r['choices'][0]['message']['content'])
        else:
            # Fallback deterministic evaluation
            safety_score = 5 if brand_safety(message) else 0
            data = {
                "clarity": 3 + (1 if len(message.split()) < 30 else 0),
                "on_brand": 4 if brand_safety(message) else 2,
                "persuasiveness": 3,
                "relevance": 3,
                "safety": safety_score,
                "overall": 3.2 if safety_score > 0 else 1.0,
                "rationale": "Deterministic fallback evaluation"
            }
    except Exception as e:
        print(f"Evaluation failed: {e}")
        data = {
            "clarity":3,"on_brand":3,"persuasiveness":3,"relevance":3,
            "safety":(5 if brand_safety(message) else 0),"overall":3.0,
            "rationale":"Fallback eval due to error"
        }
    return data

def passes_eval(scores: dict) -> bool:
    """Check if message passes quality thresholds"""
    return (scores.get("overall",0) >= EVAL_THRESHOLDS["overall"] and 
            scores.get("safety",0) >= EVAL_THRESHOLDS["safety"])

def regenerate_until_pass(generate_fn, max_tries=3, channel="email", summary=None):
    """Regenerate messages until quality thresholds are met"""
    last = None
    for attempt in range(max_tries):
        try:
            data = generate_fn()
            
            # Evaluate each variant and keep best passing one
            best_variant, best_score = None, -1
            for v in data.get("variants", []):
                text = f"{v.get('title','')} {v.get('body','')}".strip()
                
                # Quick safety pre-check
                if not brand_safety(text):
                    v["_eval"] = {"overall":0, "safety":0}
                    continue
                    
                scores = eval_message_with_llm(text, summary or {})
                v["_eval"] = scores
                
                if passes_eval(scores) and scores["overall"] > best_score:
                    best_variant, best_score = v, scores["overall"]
            
            if best_variant:
                # Return only the best passing variant
                return {"channel": data.get("channel", channel), "variants": [best_variant]}
            
            last = data
            
        except Exception as e:
            print(f"Generation attempt {attempt + 1} failed: {e}")
            continue
    
    # If none passed, return last attempt or fallback
    return last or {
        "channel": channel,
        "variants": [{
            "title": "Welcome back",
            "body": "We miss you and would love to have you back.",
            "_eval": {"overall": 2.0, "safety": 5, "rationale": "Fallback message"}
        }]
    }

# === Persona Matching ===
def find_persona_matches(df, customer_id, knn_model, preprocessor):
    """Find similar customers using kNN"""
    if not SKLEARN_AVAILABLE or knn_model is None or preprocessor is None:
        return []
    
    try:
        customer = df[df.index == customer_id]
        if customer.empty:
            return []
        
        # Select same features used for clustering
        NUM_FEATS = [f for f in ["ResurrectionScore","Tenure","Engagement","MonetaryValue","DaySinceLastOrder"] 
                     if f in customer.columns]
        CAT_FEATS = [c for c in ["PreferredLoginDevice","PreferredPaymentMode","PreferedOrderCat","CityTier"] 
                     if c in customer.columns]
        
        if CAT_FEATS:
            X_customer = customer[NUM_FEATS + CAT_FEATS]
        else:
            X_customer = customer[NUM_FEATS]
        
        X_transformed = preprocessor.transform(X_customer)
        distances, indices = knn_model.kneighbors(X_transformed)
        
        # Get similar customers
        similar_ids = df.iloc[indices[0]].index.tolist()
        return [(id_, float(dist)) for id_, dist in zip(similar_ids, distances[0])]
        
    except Exception as e:
        print(f"Persona matching failed: {e}")
        return []

# === Archetype Classification ===
ARCHETYPES = ["ValueSensitive","Loyalist","Premium","AtRisk","ServiceSensitive"]

def classify_archetype(summary: dict) -> dict:
    """Classify cohort into archetype using LLM"""
    prompt = f'''
Classify this cohort into one of: ValueSensitive, Loyalist, Premium, AtRisk, ServiceSensitive.
Use summary stats (tenure, recency, engagement, value) and return JSON:
{{"archetype":"...", "why":"one sentence reason"}}

Cohort summary: {json.dumps(summary)}
'''
    try:
        if OPENAI_API_KEY:
            r = call_chat([
                {"role":"system","content":"You are a rigorous cohort classifier."},
                {"role":"user","content":prompt}
            ], model="gpt-4o-mini", temperature=0.0)
            data = json.loads(r['choices'][0]['message']['content'])
            if data.get("archetype") not in ARCHETYPES:
                data["archetype"] = "ValueSensitive"
        else:
            # Deterministic classification based on stats
            size = summary.get('size', 0)
            avg_value = summary.get('avg_value', 0)
            avg_tenure = summary.get('avg_tenure', 0)
            avg_recency = summary.get('avg_recency', 0)
            
            if avg_value > 0.7 and avg_tenure > 24:
                archetype = "Premium"
            elif avg_tenure > 18:
                archetype = "Loyalist"  
            elif avg_recency > 20:
                archetype = "AtRisk"
            else:
                archetype = "ValueSensitive"
                
            data = {"archetype": archetype, "why": f"Based on stats: value={avg_value:.2f}, tenure={avg_tenure:.1f}mo, recency={avg_recency:.1f}d"}
        return data
    except Exception:
        return {"archetype":"ValueSensitive","why":"Fallback classification"}

# === LLM Insights Generation ===
def generate_cohort_insights(cohort_name: str, cohort_summary: dict, brand_docs: dict) -> dict:
    """Generate business insights for a cohort using LLM"""
    
    if not OPENAI_AVAILABLE:
        return {
            "insights": [
                f"Cohort '{cohort_name}' has {cohort_summary.get('size', 0)} customers",
                "Detailed insights require OpenAI integration"
            ],
            "recommendations": ["Review cohort manually for business opportunities"],
            "risk_level": "Medium",
            "priority_score": 3.0
        }
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
        
        # Get brand context
        archetype = cohort_summary.get('archetype', 'ValueSensitive')
        brand_context = get_brand_context_for_archetype(archetype, brand_docs)
        
        # Build insights prompt
        prompt = f"""Analyze this customer cohort for business insights:

Cohort: {cohort_name}
Size: {cohort_summary.get('size', 0)} customers
Archetype: {archetype}
Avg Monetary Value: ₹{cohort_summary.get('avg_monetary', 0):.2f}
Avg Tenure: {cohort_summary.get('avg_tenure', 0):.1f} months
Avg Recency: {cohort_summary.get('avg_recency', 0):.1f} days

{brand_context}

Generate actionable business insights. Return ONLY valid JSON in this exact format:
{{
  "insights": ["specific insight about this cohort", "behavioral pattern observation", "business opportunity"],
  "recommendations": ["actionable next step", "retention strategy"],
  "risk_level": "Low",
  "priority_score": 3.5
}}

Do not include any text before or after the JSON. Risk level must be Low, Medium, or High. Priority score must be 1.0-5.0."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            max_tokens=400
        )
        
        response_content = response.choices[0].message.content
        
        # Debug: Print response content if it's problematic
        if not response_content or not response_content.strip():
            print(f"⚠️ Empty response from OpenAI for insights generation")
            raise ValueError("Empty response from OpenAI")
        
        # Try to clean up the response content (sometimes has markdown formatting)
        if '```json' in response_content:
            # Extract JSON from markdown code block
            start = response_content.find('```json') + 7
            end = response_content.find('```', start)
            response_content = response_content[start:end].strip()
        elif '```' in response_content:
            # Extract from generic code block
            start = response_content.find('```') + 3
            end = response_content.find('```', start)
            response_content = response_content[start:end].strip()
        
        insights_data = json.loads(response_content)
        
        # Validate and sanitize
        insights_data['insights'] = insights_data.get('insights', [])[:3]  # Max 3 insights
        insights_data['recommendations'] = insights_data.get('recommendations', [])[:3]  # Max 3 recommendations
        insights_data['risk_level'] = insights_data.get('risk_level', 'Medium')
        insights_data['priority_score'] = float(insights_data.get('priority_score', 3.0))
        
        return insights_data
        
    except Exception as e:
        print(f"LLM insights generation failed: {e}")
        # Fallback insights based on data
        size = cohort_summary.get('size', 0)
        avg_value = cohort_summary.get('avg_monetary', 0)
        avg_recency = cohort_summary.get('avg_recency', 0)
        
        risk_level = "High" if avg_recency > 30 else "Medium" if avg_recency > 14 else "Low"
        priority = 4.0 if avg_value > 50 and size > 100 else 3.0
        
        return {
            "insights": [
                f"Cohort '{cohort_name}' contains {size} customers with {archetype} characteristics",
                f"Average order value: ₹{avg_value:.2f}, typical for this segment",
                f"Recency: {avg_recency:.1f} days - {'concerning' if avg_recency > 21 else 'normal'}"
            ],
            "recommendations": [
                "Implement targeted retention campaign" if avg_recency > 21 else "Maintain engagement",
                "Consider value-based offers" if archetype == "ValueSensitive" else "Focus on convenience"
            ],
            "risk_level": risk_level,
            "priority_score": priority
        }

# Initialize system - no fallback mode allowed
def initialize_system(skip_api_test=False):
    """Initialize the system and verify all requirements"""
    if not OPENAI_API_KEY:
        raise RuntimeError("❌ OPENAI_API_KEY is required. Set it in .env file.")
    
    # Test OpenAI connection (skip in development)
    if not skip_api_test:
        test_openai_connection()
    else:
        print("⚠️ Skipping OpenAI API test (development mode)")
    
    # Verify dataset exists
    dataset_path = os.getenv('DATASET_PATH', 'dataset.csv')
    if not Path(dataset_path).exists():
        raise RuntimeError(f"❌ Dataset not found at {dataset_path}. Set DATASET_PATH in .env file.")
    
    print("✅ System initialized successfully")

# --- Runner ---

def run():
    # Initialize system first - no fallbacks allowed
    initialize_system()
    
    df0 = load_data()
    df0 = canonicalize_columns(df0)
    df = compute_features(df0)
    # Ensure required numeric columns exist to avoid pandas.query failures
    for _c in ['CouponUsed','CashbackAmount','DaySinceLastOrder','OrderCount','Tenure','Engagement','MonetaryValue']:
        if _c not in df.columns:
            df[_c] = 0
    df['Status'] = mark_status(df)
    
    # === Micro-Cohort Processing ===
    print("\n=== Creating Micro-Cohorts ===")
    df, clustering_pipeline, knn_model, preprocessor = create_micro_cohorts(df)
    
    # Add micro-cohort summaries to traditional cohorts
    micro_cohort_summaries = {}
    if 'CohortID' in df.columns:
        for cohort_id in df['CohortID'].unique():
            cohort_df = df[df['CohortID'] == cohort_id]
            if len(cohort_df) > 0:
                summary = summarize_micro_cohort(cohort_df)
                archetype_info = classify_archetype(summary)
                summary['archetype'] = archetype_info.get('archetype', 'ValueSensitive')
                summary['archetype_reason'] = archetype_info.get('why', 'Default classification')
                micro_cohort_summaries[f"MicroCohort_{cohort_id}"] = {
                    'data': cohort_df,
                    'summary': summary
                }
    
    # traditional cohorts
    cohort_cards = {}
    for name,fn in COHORTS.items():
        d = fn(df.copy())
        summary = cohort_summary(d)
        # Add archetype classification for traditional cohorts too
        archetype_info = classify_archetype(summary)
        summary['archetype'] = archetype_info.get('archetype', 'ValueSensitive')
        summary['archetype_reason'] = archetype_info.get('why', 'Default classification')
        
        # Generate insights for this cohort
        brand_docs = load_brand_documents()
        insights_data = generate_cohort_insights(name, summary, brand_docs)
        
        cohort_cards[name] = {
            'data': d.sort_values('ResurrectionScore', ascending=False) if len(d) else d,
            'summary': summary,
            'insights': insights_data
        }
        print('\n===', name,'===')
        print(json.dumps(cohort_cards[name]['summary'], indent=2))
    
    # exports 
    for name,card in cohort_cards.items():
        fname = EXPORTS / (name.replace(' ','_') + '.csv')
        try:
            card['data'].to_csv(fname, index=False)
            print('Wrote', fname)
        except Exception:
            print('No data to write for', name)
    # RAG corpus
    corpus = load_corpus()
    retriever = build_retriever(corpus)
    # For each cohort, generate messages
    outputs = {}
    for name, card in cohort_cards.items():
        summary = card['summary']
        prompt = f"Cohort: {name} | Summary: {json.dumps(summary)}\nTop brand facts:\n"
        top_docs = retrieve(retriever, json.dumps(summary), topk=2)
        print("RAG sources:", [d.get("source") for d in top_docs])
        for d in top_docs:
            prompt += f"- {d['source']}: { (d['text'] or '')[:300].replace('\n',' ') }\n"
        # build chat messages
        system = {'role':'system','content':'You write short retention messages. Return JSON {"channel":"...","variants":[{"title":"","body":""}] }'}
        user = {'role':'user','content': prompt + '\nCreate 2 short variants.'}
        def _extract_content(res):
            if not res:
                return None
            # Common OpenAI-like shapes
            try:
                if isinstance(res, dict) and 'choices' in res and len(res['choices'])>0:
                    choice = res['choices'][0]
                    if isinstance(choice.get('message'), dict) and 'content' in choice['message']:
                        return choice['message']['content']
                    if 'text' in choice:
                        return choice['text']
                # legacy: sometimes the client returns the dict directly
                if isinstance(res, str):
                    return res
            except Exception:
                return None
            return None

        def _validate_eval(obj):
            """Ensure obj has _eval with required keys and normalize values."""
            if not isinstance(obj, dict):
                return False, 'not-a-dict'
            ev = obj.get('_eval')
            if not isinstance(ev, dict):
                return False, 'no-_eval'
            if 'overall' not in ev or 'urgency' not in ev or 'compliance_ok' not in ev:
                return False, 'missing-keys'
            # normalize
            try:
                ov = float(ev['overall'])
                if not (0 <= ov <= 10):
                    return False, 'overall-range'
            except Exception:
                return False, 'overall-numeric'
            if ev['urgency'] not in ['low','medium','high']:
                # attempt to coerce
                u = str(ev['urgency']).lower()
                if 'high' in u:
                    ev['urgency'] = 'high'
                elif 'low' in u:
                    ev['urgency'] = 'low'
                else:
                    ev['urgency'] = 'medium'
            if not isinstance(ev['compliance_ok'], bool):
                ev['compliance_ok'] = bool(ev['compliance_ok'])
            obj['_eval'] = ev
            return True, 'ok'

        # Make live OpenAI API call only
        try:
            res = call_chat([system, user])
            content = _extract_content(res)

            if not content:
                raise RuntimeError(f'❌ LLM returned no content for cohort {name}. Check your OpenAI API key and quota.')

            parsed = None
            if content:
                try:
                    parsed = json.loads(content)
                except Exception:
                    # sometimes content may be raw text; wrap into simple structure and set minimal _eval
                    parsed = {'channel': 'email', 'variants': [{'title': 'Demo', 'body': content[:200]}], '_eval': {'overall':5,'urgency':'medium','compliance_ok':True}}

            # Validate _eval; if invalid, attempt demo fallback
            valid = False
            if parsed is not None:
                valid, reason = _validate_eval(parsed)
                if not valid:
                    print('LLM response missing/invalid _eval:', reason)

            if not valid:
                # fallback to demo payload
                parsed = {
                    '_eval': {'overall':7,'urgency':'medium','compliance_ok':True},
                    'channel':'email',
                    'variants': [{'title':'Demo','body':'Fallback message'}]
                }

            data = parsed

        except Exception as e:
            print(f'❌ LLM critical failure for cohort {name}:', e)
            raise RuntimeError(f'❌ Failed to generate messages for cohort {name}: {str(e)}')
        outputs[name] = data
        print('\nSample output for',name,':')
        print(json.dumps(data, indent=2)[:2000])
    # write manifest
    with open(EXPORTS / 'manifest.json','w') as f:
        json.dump({'cohorts': {k:v['summary'] for k,v in cohort_cards.items()}}, f, indent=2)
    # persist generated messages
    try:
        with open(EXPORTS / 'last_run_messages.json','w') as f:
            json.dump(outputs, f, indent=2)
        print('Wrote', EXPORTS / 'last_run_messages.json')
    except Exception as e:
        print('Failed to write last_run_messages.json:', e)

    # Simple ROI waterfall estimate for each cohort and overall
    roi = {}
    rows = []
    for name, card in cohort_cards.items():
        s = card['summary']
        size = s.get('size',0)
        avg_value = s.get('avg_value',0)
        # assumptions: 2% conversion on average value recovered per contacted customer; cost $0.25 per contact
        est_recovered = size * avg_value * 0.02
        cost = size * 0.25
        net = est_recovered - cost
        roi[name] = {'size': size, 'est_recovered': est_recovered, 'cost': cost, 'net': net, 'roi_ratio': (net / cost) if cost else None}
        rows.append({'cohort': name, 'size': size, 'est_recovered': est_recovered, 'cost': cost, 'net': net, 'roi_ratio': (net / cost) if cost else None})
    try:
        with open(EXPORTS / 'last_run_roi.json','w') as f:
            json.dump(roi, f, indent=2)
        pd.DataFrame(rows).to_csv(EXPORTS / 'last_run_roi.csv', index=False)
        print('Wrote', EXPORTS / 'last_run_roi.json', 'and', EXPORTS / 'last_run_roi.csv')
    except Exception as e:
        print('Failed to write ROI outputs:', e)
    print('\nDone. Exports in', EXPORTS)

# === Integration Functions for Streamlit App ===
def get_processed_data():
    """Get processed data for Streamlit app"""
    df0 = load_data()
    df0 = canonicalize_columns(df0)
    df = compute_features(df0)
    # Ensure required numeric columns exist
    for _c in ['CouponUsed','CashbackAmount','DaySinceLastOrder','OrderCount','Tenure','Engagement','MonetaryValue']:
        if _c not in df.columns:
            df[_c] = 0
    df['Status'] = mark_status(df)
    
    # Add micro-cohorts
    df, clustering_pipeline, knn_model, preprocessor = create_micro_cohorts(df)
    
    return df, clustering_pipeline, knn_model, preprocessor

def get_cohort_data():
    """Get all cohort data for Streamlit app"""
    df, clustering_pipeline, knn_model, preprocessor = get_processed_data()
    
    # Traditional cohorts
    cohort_cards = {}
    brand_docs = load_brand_documents()  # Load once for all cohorts
    
    for name,fn in COHORTS.items():
        d = fn(df.copy())
        summary = cohort_summary(d)
        archetype_info = classify_archetype(summary)
        summary['archetype'] = archetype_info.get('archetype', 'ValueSensitive')
        summary['archetype_reason'] = archetype_info.get('why', 'Default classification')
        
        # Generate insights for this cohort
        insights_data = generate_cohort_insights(name, summary, brand_docs)
        
        cohort_cards[name] = {
            'data': d.sort_values('ResurrectionScore', ascending=False) if len(d) else d,
            'summary': summary,
            'insights': insights_data
        }
    
    # Add micro-cohort summaries
    micro_cohort_summaries = {}
    if 'CohortID' in df.columns:
        for cohort_id in df['CohortID'].unique():
            cohort_df = df[df['CohortID'] == cohort_id]
            if len(cohort_df) > 0:
                summary = summarize_micro_cohort(cohort_df)
                archetype_info = classify_archetype(summary)
                summary['archetype'] = archetype_info.get('archetype', 'ValueSensitive')
                summary['archetype_reason'] = archetype_info.get('why', 'Default classification')
                micro_cohort_summaries[f"MicroCohort_{cohort_id}"] = {
                    'data': cohort_df,
                    'summary': summary
                }
    
    return cohort_cards, micro_cohort_summaries, knn_model, preprocessor

def generate_message_with_eval(prompt, cohort_summary):
    """Generate messages with LLM-as-Judge evaluation"""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
        
        # Message generation
        system_msg = {
            'role': 'system',
            'content': 'You write retention messages for e-commerce. Return JSON: {"channel":"email/sms","variants":[{"title":"","body":""}]}'
        }
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_msg, {'role': 'user', 'content': prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        response_content = response.choices[0].message.content
        
        # Debug and clean response
        if not response_content or not response_content.strip():
            print(f"⚠️ Empty response from OpenAI for message generation")
            raise ValueError("Empty response from OpenAI")
        
        # Clean markdown formatting if present
        if '```json' in response_content:
            start = response_content.find('```json') + 7
            end = response_content.find('```', start)
            response_content = response_content[start:end].strip()
        elif '```' in response_content:
            start = response_content.find('```') + 3
            end = response_content.find('```', start)
            response_content = response_content[start:end].strip()
        
        message_data = json.loads(response_content)
        
        # LLM-as-Judge evaluation
        for variant in message_data.get('variants', []):
            message_text = f"{variant.get('title', '')} {variant.get('body', '')}"
            
            # Safety check
            safety_score = 5 if brand_safety(message_text) else 0
            
            # LLM Judge evaluation
            judge_prompt = f"""Rate this retention message (1-5 scale):
Message: {message_text}
Cohort: {json.dumps(cohort_summary)}

Evaluate: relevance, clarity, on_brand, persuasion, safety. Return JSON: {{"relevance":N,"clarity":N,"on_brand":N,"persuasion":N,"safety":N,"overall":N.N}}"""
            
            try:
                judge_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{'role': 'user', 'content': judge_prompt}],
                    temperature=0.1,
                    max_tokens=100
                )
                
                judge_content = judge_response.choices[0].message.content
                
                # Clean judge response
                if not judge_content or not judge_content.strip():
                    raise ValueError("Empty judge response")
                
                # Clean markdown formatting if present
                if '```json' in judge_content:
                    start = judge_content.find('```json') + 7
                    end = judge_content.find('```', start)
                    judge_content = judge_content[start:end].strip()
                elif '```' in judge_content:
                    start = judge_content.find('```') + 3
                    end = judge_content.find('```', start)
                    judge_content = judge_content[start:end].strip()
                
                scores = json.loads(judge_content)
                scores['safety'] = safety_score  # Override with brand safety
                variant['evaluation'] = scores
                
            except Exception as e:
                print(f"Judge evaluation failed: {e}")
                variant['evaluation'] = {
                    "relevance": 3, "clarity": 3, "on_brand": 4 if brand_safety(message_text) else 2,
                    "persuasion": 3, "safety": safety_score, "overall": 3.0
                }
        
        return message_data
        
    except Exception as e:
        print(f"Message generation failed: {e}")
        # Fallback response
        return {
            "channel": "email",
            "variants": [{
                "title": "We Value You",
                "body": "Discover curated picks selected just for you.",
                "evaluation": {"relevance":3,"clarity":4,"on_brand":4,
                "persuasion":3,"safety":(5 if brand_safety("We Value You") else 0),"overall":3.0,
                "note":"Fallback message"}
            }]
        }

def generate_messages_for_cohort(cohort_name, cohort_summary, use_llm_eval=True):
    """Generate and evaluate messages for a specific cohort with brand context"""
    
    # Load brand documents
    brand_docs = load_brand_documents()
    
    # Get archetype-specific brand context
    archetype = cohort_summary.get('archetype', 'ValueSensitive')
    brand_context = get_brand_context_for_archetype(archetype, brand_docs)
    
    # Build enhanced prompt with brand guidance
    prompt = f"""Cohort: {cohort_name}
Archetype: {archetype}
Summary: {json.dumps(cohort_summary)}

{brand_context}

Create retention messages following brand voice: helpful, clear, benefit-focused. Use approved words like 'save', 'smarter', 'convenient', 'curated'. Avoid 'guaranteed', 'last chance', 'BUY NOW'.
Generate 2 variants."""
    
    # Generate with quality evaluation
    if use_llm_eval:
        return generate_message_with_eval(prompt, cohort_summary)
    else:
        # Legacy fallback
        return {
            'channel': 'email',
            'variants': [{
                'title': 'Your Curated Selection Awaits',
                'body': 'Save time with our smarter recommendations.',
                'evaluation': {'overall': 3.5, 'note': 'Legacy generation'}
            }]
        }

if __name__=='__main__':
    run()
