# Churn Radar 🧭
**Production-Ready AI-Powered Customer Resurrection Platform**

[![Tests](https://img.shields.io/badge/tests-7%2F7%20passing-brightgreen)](./acceptance_test.py)
[![Python](https://img.shields.io/badge/python-3.12+-blue)](https://python.org)
[![OpenAI](https://img.shields.io/badge/powered%20by-OpenAI-black)](https://openai.com)
[![Streamlit](https://img.shields.io/badge/ui-Streamlit-red)](https://streamlit.io)

## 🎯 Problem Statement
E-commerce companies lose 20-30% of customers annually while overspending on acquisition. Churn Radar transforms customer data into actionable retention strategies using AI-powered insights, ML-driven segmentation, and brand-consistent messaging.

## ⚡ Quick Start

### 1. Environment Setup
```bash
# Clone and setup
git clone https://github.com/bajajvinamr/Metuzi.git
cd Metuzi

# Install dependencies (dev container ready)
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### 2. Run Analytics Engine
```bash
# Full pipeline execution
python run_churn_radar.py

# Streamlit dashboard
cd app && streamlit run app.py
```

### 3. Validate System
```bash
# Comprehensive acceptance tests
python acceptance_test.py
```

## 🏗️ System Architecture

### Core Analytics Engine (`run_churn_radar.py`)
- **Data Processing**: 5,630 → 4,308 active customers with feature engineering
- **ML Segmentation**: 4 traditional cohorts + 100 micro-cohorts via KMeans clustering
- **Scoring System**: ResurrectionScore (0.100-0.712) for retention likelihood
- **AI Integration**: OpenAI GPT-4o-mini for insights and message generation

### Brand Kit & RAG System (`brand_kit/`)
- **4 Brand Documents**: Overview, voice, compliance, offer policy
- **Context-Aware Messaging**: Brand-consistent content generation
- **Archetype Classification**: 5 customer personas (ValueSensitive, Loyalist, Premium, AtRisk, ServiceSensitive)

### Interactive Dashboard (`app/`)
- **Real-time Insights**: Business intelligence with risk assessment
- **Group Passport**: Detailed cohort analytics with AI recommendations
- **ROI Calculator**: Financial impact projections with Indian currency formatting
- **Dark Theme UI**: Professional interface with responsive design

## 🚀 Features

### 🤖 AI-Powered Intelligence
- **LLM Insights Generation**: Business insights with risk levels and priority scores
- **Message Generation**: Brand-safe content with LLM-as-Judge evaluation
- **Archetype Classification**: Behavioral customer segmentation
- **Quality Scoring**: Automated message evaluation (relevance, clarity, persuasion)

### 📊 Advanced Analytics
- **ML Clustering**: scikit-learn KMeans for micro-segmentation
- **Feature Engineering**: Engagement, monetary value, recency, tenure analysis
- **Persona Matching**: kNN-based customer similarity matching
- **ROI Modeling**: Revenue impact projections with cost analysis

### 🛡️ Production Ready
- **Comprehensive Testing**: 7/7 acceptance tests passing
- **Error Handling**: Robust fallbacks and logging
- **Privacy First**: No PII sent to AI models
- **Export System**: CSV, JSON outputs with detailed manifests

## 📈 Sample Results

### Customer Segmentation
- **Payment-sensitive churners**: 1,603 customers, ₹217.44 avg value
- **High-tenure recent drop**: 892 customers, ₹298.63 avg value
- **Premium engagement lapsed**: 945 customers, ₹314.89 avg value
- **AtRisk High-Value**: 868 customers, ₹421.33 avg value

### AI-Generated Insights
```json
{
  "insights": [
    "Cohort shows moderate engagement with price sensitivity",
    "8.2 month tenure suggests stable customer base",
    "15.5 day recency indicates active engagement"
  ],
  "recommendations": [
    "Implement loyalty program with value-based rewards",
    "Use personalized marketing highlighting savings"
  ],
  "risk_level": "Low",
  "priority_score": 3.5
}
```

## 🗂️ Project Structure

```
Metuzi/
├── run_churn_radar.py          # Main analytics engine
├── acceptance_test.py          # Comprehensive test suite
├── dataset.csv                 # Sample customer data
├── requirements.txt            # Python dependencies
├── brand_kit/                  # Brand documents for RAG
│   ├── brand_overview.md
│   ├── brand_voice.md
│   ├── compliance.md
│   └── offer_policy.md
├── app/                        # Streamlit dashboard
│   ├── app.py                  # Main UI application
│   └── churn_core/             # Core integration modules
├── exports/                    # Generated outputs
│   ├── manifest.json           # Export metadata
│   ├── last_run_roi.json       # ROI calculations
│   └── *.csv                   # Cohort exports
└── tests/                      # Unit test suite
```

## 🧪 Testing & Validation

### Acceptance Test Suite
```bash
python acceptance_test.py
```

**Test Coverage:**
- ✅ Environment & Config Setup
- ✅ Data Load & Sanity Checks  
- ✅ Features & Scoring
- ✅ Cohorts & Micro-Segmentation
- ✅ Archetypes & Phrasebook
- ✅ Business Math & ROI
- ✅ Export System

### Unit Tests
```bash
python -m pytest tests/
```

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY="sk-..."           # Required for AI features
OPENAI_API_BASE="https://..."     # Optional: Custom endpoint
LIVE_ONLY=1                       # Optional: Disable fallbacks
```

### Brand Kit Customization
Update documents in `brand_kit/` to customize:
- Brand voice and messaging guidelines
- Compliance requirements
- Offer policies and restrictions
- Company overview and values

## 📊 Performance Metrics

- **Processing Speed**: 5,630 rows processed in ~30 seconds
- **Memory Usage**: <2GB for full pipeline
- **API Efficiency**: ~10-15 OpenAI calls per full run
- **Export Generation**: 4 CSVs + 2 JSON files with manifests

## 🚀 Production Deployment

### Docker (Recommended)
```bash
docker build -t churn-radar .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... churn-radar
```

### Direct Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Run backend
python run_churn_radar.py

# Start dashboard
streamlit run app/app.py --server.port 8501
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python acceptance_test.py`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **OpenAI**: GPT-4o-mini for AI-powered insights
- **Streamlit**: Interactive dashboard framework
- **scikit-learn**: ML clustering and preprocessing
- **Pandas**: Data processing and analysis

---

**Built with ❤️ for modern retention marketing**

*Transform churning customers into loyal advocates with AI-powered precision.*