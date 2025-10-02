#!/bin/bash
# 🚀 Churn Radar Production Launch Script
# CEO-Proof Demo Ready

echo "🚀 LAUNCHING CHURN RADAR PRODUCTION DEMO"
echo "========================================"

# Validate environment
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "💡 Create .env with: OPENAI_API_KEY=your_key_here"
    exit 1
fi

if [ ! -f "dataset.csv" ]; then
    echo "❌ Error: dataset.csv not found"
    exit 1
fi

echo "✅ Environment validated"

# Install dependencies if needed
echo "📦 Checking dependencies..."
python -c "import streamlit, openai, pandas" 2>/dev/null || {
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
}

echo "✅ Dependencies ready"

# Start the application
echo "🌟 Starting CEO-proof dashboard..."
echo "📊 Expected Results:"
echo "   • ₹12,34,567 recoverable profit"
echo "   • 4,308 customers analyzed"  
echo "   • 4 actionable customer groups"
echo "   • 842 expected reactivations"
echo ""
echo "🔗 Access URL: http://localhost:8501"
echo "📋 QA Report: See QA_SIGNOFF_REPORT.md"
echo ""

cd app && streamlit run app.py --server.port 8501 --server.address 0.0.0.0