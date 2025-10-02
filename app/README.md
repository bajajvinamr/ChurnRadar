# Churn Radar Streamlit UI

## 🎯 Product-Grade UI for Customer Resurrection Analytics

Beautiful, production-ready Streamlit application that transforms your churn analysis into actionable insights a marketer or CEO can understand at a glance.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Working Churn Radar analytics backend (`run_churn_radar.py`)

### Installation

1. **Navigate to the app directory:**
   ```bash
   cd app
   ```

2. **Install dependencies:**
   ```bash
   pip install streamlit plotly pandas numpy pydantic
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser:**
   - Local: http://localhost:8501
   - Network: Available on your network IP

## 📊 Features

### 🏠 Overview Page
- **Top Strip Metrics**: Recoverable Profit, Ready Groups, Expected Reactivations
- **Cohort Ladder**: Top opportunities ranked by net profit potential
- **Group Passport**: Detailed metrics for top-performing group
- **Message Preview**: Sample messages across email/WhatsApp/push
- **ROI Preview**: Quick financial impact summary

### 👥 Groups Page
- **Complete Group Analysis**: All cohorts with search and filtering
- **Group Passport Modal**: Detailed metrics and archetype guidance
- **Messaging Guidelines**: What to say/avoid for each archetype
- **Quick Actions**: Direct navigation to messages and ROI

### 📝 Messages Page
- **Channel-Specific Cards**: Email, WhatsApp, Push message variants
- **Brand Safety Badges**: Compliance and evaluation scores
- **Copy Operations**: One-click copy and regeneration
- **Archetype Guidance**: Tone and messaging recommendations
- **Batch Operations**: Export copy packs and bulk actions

### 💰 ROI Calculator Page
- **Interactive Sliders**: Reactivation rate, AOV, margin, costs
- **Live Waterfall Chart**: Visual profit flow breakdown
- **Sensitivity Analysis**: Optimistic/conservative scenarios
- **Key Metrics**: Reactivated customers, net profit, ROMI
- **Cost Breakdown**: Detailed expense analysis

### 📤 Exports Page
- **Single Group Exports**: CSV data and copy packs
- **Bulk Operations**: All groups at once
- **Manifest Generation**: Audit trail and metadata
- **File Browser**: Browse and manage exports
- **Export Settings**: Customizable output options

## 🎨 Design System

### Theme
- **Dark Mode**: Professional, low-eye-strain interface
- **Brand Color**: #3B82F6 (primary blue)
- **High Contrast**: Accessible color ratios
- **Modern Cards**: Clean, bordered containers

### Typography
- **Headers**: Clear hierarchy with emoji icons
- **Metrics**: Large, readable numbers with context
- **Body Text**: Comfortable reading size (14px+)
- **Captions**: Subtle guidance text

### Navigation
- **Page Tabs**: Clear section organization
- **Action Buttons**: Prominent CTAs with icons
- **Breadcrumbs**: Context-aware navigation
- **Quick Actions**: One-click workflows

## 🔧 Technical Architecture

### Integration Layer (`churn_core/`)
- **logic.py**: Wraps existing analytics functions
- **data.py**: Formatting and utility functions
- **brand.py**: Archetype definitions and messaging guidance

### Data Flow
1. **Backend Integration**: Imports `run_churn_radar.py` functions
2. **Data Caching**: 5-minute cache for performance
3. **Session State**: Maintains selected group across pages
4. **Error Handling**: Clear error messages with remediation steps

### Performance
- **Caching Strategy**: Smart data caching with TTL
- **Lazy Loading**: Load data only when needed
- **Efficient Updates**: Minimal re-computation
- **Background Processing**: Non-blocking operations

## 📱 Usage Patterns

### Marketing Manager Workflow
1. **Overview** → See total opportunity and top groups
2. **Groups** → Dive deep into specific cohorts
3. **Messages** → Review and copy campaign content
4. **Exports** → Download data for campaign tools

### CEO/Executive Workflow
1. **Overview** → Get high-level metrics at a glance
2. **ROI Calculator** → Understand financial impact
3. **Quick Actions** → Start campaigns on highest-value groups

### Analyst Workflow
1. **Groups** → Analyze all cohorts with filters
2. **ROI Calculator** → Model different scenarios
3. **Exports** → Download data for further analysis

## 🎯 Key Metrics Explained

### Business Language Translation
- **Size** → People (more relatable)
- **avg_score** → Come-Back Odds (intuitive percentage)
- **avg_recency** → Last Seen (temporal context)
- **avg_value** → Avg Spend (clear monetary value)

### Indian Currency Formatting
- **Grouping**: ₹12,34,567 (lakhs/crores format)
- **Precision**: Rounded to nearest rupee for clarity
- **Consistency**: Same format across all displays

## 🔐 Privacy & Security

### Data Handling
- **No PII**: Customer data stays aggregated
- **Local Processing**: All computation happens locally
- **Secure Exports**: Files saved to local exports directory
- **Clean Separation**: UI layer doesn't modify core data

### Compliance
- **Brand Safety**: All messages checked for compliance
- **Audit Trail**: Full manifest of all exports
- **Metadata**: Timestamps and source tracking

## 🚀 Deployment Options

### Development
```bash
streamlit run app.py
```

### Production
```bash
streamlit run app.py --server.port 8501 --server.headless true
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install streamlit plotly pandas numpy pydantic
CMD ["streamlit", "run", "app.py", "--server.headless", "true"]
```

## 🎨 Customization

### Brand Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#YOUR_BRAND_COLOR"
backgroundColor = "#YOUR_BG_COLOR"
```

### Messaging
Update `churn_core/brand.py` for custom archetype guidance.

### Metrics
Modify `churn_core/logic.py` to adjust calculation logic.

## 📞 Support

### Common Issues

**"No groups available"**
- Ensure `run_churn_radar.py` runs successfully
- Check that `dataset.csv` exists in parent directory

**"Error loading data"**
- Verify Python environment has required packages
- Check parent directory structure

**"Export failed"**
- Ensure write permissions to `exports/` directory
- Check disk space availability

### Performance Tips
- Use Chrome/Edge for best Plotly chart performance
- Clear browser cache if experiencing issues
- Restart Streamlit if data seems stale

## 🎉 Success Metrics

The UI is working correctly when you see:
- ✅ Top strip shows actual profit numbers
- ✅ Groups table populates with real data
- ✅ Messages show generated content with badges
- ✅ ROI calculator responds to slider changes
- ✅ Exports create files in `/exports` directory

---

**Built with ❤️ by the Growth Team • Powered by Streamlit & Plotly**