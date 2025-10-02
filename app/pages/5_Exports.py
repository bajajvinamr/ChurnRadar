"""
Exports Page - Data export and copy pack generation.
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from churn_core.logic import (
    get_groups, 
    get_defaults, 
    kept_messages, 
    export_group_csv, 
    export_copy_pack, 
    export_manifest
)
from churn_core.data import format_inr
from churn_core.content import get_empty_state

st.set_page_config(page_title="Exports - Churn Radar", page_icon="📤", layout="wide")

st.title("📤 Exports")
st.markdown("**How do we ship?**")

# Load data
@st.cache_data(ttl=300)
def load_export_data():
    return get_groups(), get_defaults()

groups, defaults = load_export_data()

# Export options
st.subheader("📦 Export Options")

# Single group export (if selected)
if st.session_state.get('selected_group'):
    selected_group = st.session_state.selected_group
    
    st.info(f"**Selected Group:** {selected_group}")
    
    single_col1, single_col2, single_col3 = st.columns(3)
    
    with single_col1:
        if st.button("📊 Export Group CSV", use_container_width=True):
            try:
                file_path = export_group_csv(selected_group)
                if file_path:
                    st.success(f"✅ CSV exported successfully!")
                    st.code(f"File: {file_path}")
                else:
                    st.error("Failed to export CSV")
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with single_col2:
        if st.button("📝 Export Copy Pack", use_container_width=True):
            try:
                file_path = export_copy_pack(selected_group)
                if file_path:
                    st.success(f"✅ Copy pack exported successfully!")
                    st.code(f"File: {file_path}")
                    
                    # Show preview
                    with st.expander("📄 Preview Copy Pack"):
                        with open(file_path, 'r') as f:
                            copy_data = json.load(f)
                        st.json(copy_data)
                else:
                    st.error("Failed to export copy pack")
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with single_col3:
        if st.button("📋 Generate Manifest", use_container_width=True):
            try:
                file_path = export_manifest()
                if file_path:
                    st.success(f"✅ Manifest generated successfully!")
                    st.code(f"File: {file_path}")
                else:
                    st.error("Failed to generate manifest")
            except Exception as e:
                st.error(f"Export failed: {e}")

# Bulk export options
st.markdown("---")
st.subheader("🔄 Bulk Operations")

bulk_col1, bulk_col2, bulk_col3 = st.columns(3)

with bulk_col1:
    if st.button("📊 Export All CSVs", use_container_width=True):
        exported_files = []
        errors = []
        
        for group_name in groups.keys():
            try:
                file_path = export_group_csv(group_name)
                if file_path:
                    exported_files.append(file_path)
                else:
                    errors.append(f"Failed to export {group_name}")
            except Exception as e:
                errors.append(f"{group_name}: {str(e)}")
        
        if exported_files:
            st.success(f"✅ Exported {len(exported_files)} CSV files!")
            with st.expander("📁 View exported files"):
                for file_path in exported_files:
                    st.code(file_path)
        
        if errors:
            st.warning("⚠️ Some exports failed:")
            for error in errors:
                st.text(error)

with bulk_col2:
    if st.button("📝 Export All Copy Packs", use_container_width=True):
        exported_files = []
        errors = []
        
        for group_name in groups.keys():
            try:
                file_path = export_copy_pack(group_name)
                if file_path:
                    exported_files.append(file_path)
                else:
                    errors.append(f"Failed to export {group_name}")
            except Exception as e:
                errors.append(f"{group_name}: {str(e)}")
        
        if exported_files:
            st.success(f"✅ Exported {len(exported_files)} copy packs!")
            with st.expander("📁 View exported files"):
                for file_path in exported_files:
                    st.code(file_path)
        
        if errors:
            st.warning("⚠️ Some exports failed:")
            for error in errors:
                st.text(error)

with bulk_col3:
    if st.button("📦 Full Export Package", use_container_width=True):
        st.info("🔄 Creating full export package...")
        
        # Export all CSVs
        csv_files = []
        for group_name in groups.keys():
            try:
                file_path = export_group_csv(group_name)
                if file_path:
                    csv_files.append(file_path)
            except:
                pass
        
        # Export all copy packs  
        copy_files = []
        for group_name in groups.keys():
            try:
                file_path = export_copy_pack(group_name)
                if file_path:
                    copy_files.append(file_path)
            except:
                pass
        
        # Generate manifest
        try:
            manifest_path = export_manifest()
        except:
            manifest_path = None
        
        total_files = len(csv_files) + len(copy_files) + (1 if manifest_path else 0)
        
        if total_files > 0:
            st.success(f"✅ Full package exported! ({total_files} files)")
            
            with st.expander("📋 Package Contents"):
                if csv_files:
                    st.markdown("**CSV Files:**")
                    for f in csv_files:
                        st.text(f"• {Path(f).name}")
                
                if copy_files:
                    st.markdown("**Copy Packs:**")
                    for f in copy_files:
                        st.text(f"• {Path(f).name}")
                
                if manifest_path:
                    st.markdown("**Manifest:**")
                    st.text(f"• {Path(manifest_path).name}")
        else:
            st.error("❌ Export package failed")

# Export summary
st.markdown("---")
st.subheader("📋 Export Summary")

# Check existing exports
exports_dir = Path(__file__).parent.parent.parent / "exports"
if exports_dir.exists():
    files = list(exports_dir.glob("*"))
    
    if files:
        # Filter by type
        csv_files = [f for f in files if f.suffix == '.csv']
        json_files = [f for f in files if f.suffix == '.json']
        
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            st.metric("CSV Files", len(csv_files))
            
        with summary_col2:
            st.metric("JSON Files", len(json_files))
            
        with summary_col3:
            st.metric("Total Files", len(files))
        
        # File browser
        with st.expander("📁 Browse Export Directory"):
            file_data = []
            for file_path in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True):
                stat = file_path.stat()
                file_data.append({
                    "File": file_path.name,
                    "Type": file_path.suffix.upper() or "DIR",
                    "Size": f"{stat.st_size / 1024:.1f} KB" if stat.st_size > 0 else "0 KB",
                    "Modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                })
            
            if file_data:
                files_df = pd.DataFrame(file_data)
                st.dataframe(files_df, hide_index=True, use_container_width=True)
            else:
                st.info("No files in export directory")
    else:
        st.info("No exports found. Create your first export above!")
else:
    st.warning("Export directory not found.")

# Export schemas documentation
st.markdown("---")
st.subheader("📖 Export Schemas")

with st.expander("📊 Per-Group CSV Schema"):
    st.markdown("""
**Columns:**
- `CustomerID` - Unique customer identifier
- `ComeBackOdds` - 0–1 score (use % in UI)
- `LastSeenDays` - Integer days since last order
- `OrderCount` - Total number of orders
- `Engagement` - Normalized engagement index (0–1)
- `AvgSpend` (₹) - Average spending per order
- `TenureMonths` - Months as customer

**Format:** CSV with headers, Indian rupee grouping in UI display
    """)

with st.expander("📝 copy_pack.json Schema"):
    st.markdown("""
**Structure:**
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
        "_eval": {"overall": 4.6, "safety": 5}
      },
      "utm": {
        "source": "churn_radar",
        "medium": "email",
        "campaign": "winback_premium_v1"
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
    """)

with st.expander("📦 manifest.json Schema"):
    st.markdown("""
**Structure:**
- `run_id` - Unique run identifier (YYYYMMDD_HHMMSS)
- `timestamp` - ISO 8601 timestamp
- `dataset` - Name, counts, active groups
- `model` - Name, version, provider
- `brand_docs` - List of brand documents used
- `groups` - List of all group names
- `thresholds` - Quality and safety thresholds
- `default_assumptions` - Default economic parameters
- `source` - Generation source (streamlit_ui, cli, etc)
- `timezone` - Asia/Kolkata (IST)
    """)

# Export configuration
st.markdown("---")
st.subheader("⚙️ Export Settings")

settings_col1, settings_col2 = st.columns(2)

with settings_col1:
    include_metadata = st.checkbox("Include metadata in exports", value=True)
    include_timestamps = st.checkbox("Include timestamps", value=True)
    
with settings_col2:
    export_format = st.selectbox(
        "Default export format",
        ["JSON", "CSV", "Both"],
        index=0
    )
    
    compression = st.selectbox(
        "Compression",
        ["None", "ZIP", "GZIP"],
        index=0
    )

# Advanced export options
with st.expander("🔧 Advanced Options"):
    st.markdown("**Custom Export Settings:**")
    
    custom_col1, custom_col2 = st.columns(2)
    
    with custom_col1:
        include_raw_data = st.checkbox("Include raw customer data", value=False)
        include_eval_details = st.checkbox("Include evaluation details", value=True)
        
    with custom_col2:
        anonymize_data = st.checkbox("Anonymize customer data", value=True)
        include_debug_info = st.checkbox("Include debug information", value=False)
    
    if st.button("🚀 Custom Export", use_container_width=True):
        st.info("Custom export functionality coming soon!")

# Navigation
st.markdown("---")
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("← ROI Calculator", use_container_width=True):
        st.switch_page("pages/4_ROI.py")

with nav_col2:
    if st.button("🏠 Overview", use_container_width=True):
        st.switch_page("app.py")

with nav_col3:
    if st.button("👥 Groups", use_container_width=True):
        st.switch_page("pages/2_Groups.py")

# Footer with export location
st.markdown("---")
st.caption(f"📁 Export location: `{exports_dir}`")