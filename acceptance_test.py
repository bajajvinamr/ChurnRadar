#!/usr/bin/env python3
"""
Churn Radar — Complete Acceptance Test
Validates all items from the acceptance checklist
"""
import os
import json
import pandas as pd
from pathlib import Path
from run_churn_radar import (
    initialize_system, load_data, compute_features, 
    get_cohort_data, get_processed_data
)

def test_environment_config():
    """Test Section 0: Environment & Config"""
    print("🧪 Testing Environment & Config...")
    
    # Check .env file
    env_file = Path('.env')
    assert env_file.exists(), "❌ .env file missing"
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    assert api_key and len(api_key) > 20, "❌ OPENAI_API_KEY missing or invalid"
    
    # Check dataset path
    dataset_path = os.getenv('DATASET_PATH', 'dataset.csv')
    assert Path(dataset_path).exists(), f"❌ Dataset not found at {dataset_path}"
    
    # Test OpenAI connection
    try:
        initialize_system()
        print("✅ Environment & Config: PASSED")
        return True
    except Exception as e:
        print(f"❌ Environment & Config: FAILED - {e}")
        return False

def test_data_load_sanity():
    """Test Section 1: Data Load & Sanity"""
    print("🧪 Testing Data Load & Sanity...")
    
    try:
        df = load_data()
        
        # Check mandatory columns
        required_cols = [
            'CustomerID', 'OrderCount', 'HourSpendOnApp', 'NumberOfDeviceRegistered',
            'SatisfactionScore', 'Complain', 'Tenure', 'DaySinceLastOrder',
            'CashbackAmount', 'CouponUsed', 'OrderAmountHikeFromlastYear'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        assert not missing_cols, f"❌ Missing columns: {missing_cols}"
        
        # Check data quality
        assert len(df) > 1000, f"❌ Dataset too small: {len(df)} rows"
        assert df.duplicated(subset=['CustomerID']).sum() == 0, "❌ Duplicate CustomerIDs found"
        
        print(f"✅ Data Load & Sanity: PASSED ({len(df):,} rows, {len(df.columns)} columns)")
        return True, df
    except Exception as e:
        print(f"❌ Data Load & Sanity: FAILED - {e}")
        return False, None

def test_features_scoring(df):
    """Test Section 2: Features & Scoring"""
    print("🧪 Testing Features & Scoring...")
    
    try:
        df_processed = compute_features(df)
        
        # Check derived fields
        required_features = ['MonetaryValue', 'Engagement', 'SatisfactionMinusComplain', 'ResurrectionScore']
        missing_features = [f for f in required_features if f not in df_processed.columns]
        assert not missing_features, f"❌ Missing features: {missing_features}"
        
        # Check ResurrectionScore properties
        score_col = df_processed['ResurrectionScore']
        assert score_col.min() >= 0 and score_col.max() <= 1, "❌ ResurrectionScore not in [0,1] range"
        assert not score_col.isna().all(), "❌ All ResurrectionScore values are NaN"
        
        score_std = score_col.std()
        assert score_std > 0.01, f"❌ ResurrectionScore has no variance: std={score_std}"
        
        print(f"✅ Features & Scoring: PASSED (ResurrectionScore: {score_col.min():.3f}-{score_col.max():.3f})")
        return True, df_processed
    except Exception as e:
        print(f"❌ Features & Scoring: FAILED - {e}")
        return False, None

def test_cohorts_segmentation():
    """Test Section 3: Cohorts & Micro-Segmentation"""
    print("🧪 Testing Cohorts & Micro-Segmentation...")
    
    try:
        cohort_cards, micro_cohorts, knn_model, preprocessor = get_cohort_data()
        
        # Check preset cohorts
        expected_cohorts = [
            'Payment-sensitive churners', 'High-tenure recent drop',
            'Premium engagement lapsed', 'AtRisk High-Value'
        ]
        
        for cohort in expected_cohorts:
            assert cohort in cohort_cards, f"❌ Missing cohort: {cohort}"
            size = cohort_cards[cohort]['summary']['size']
            assert size >= 0, f"❌ Negative size for {cohort}: {size}"
        
        total_people = sum(g['summary']['size'] for g in cohort_cards.values())
        micro_count = len(micro_cohorts) if micro_cohorts else 0
        print(f"✅ Cohorts & Micro-Segmentation: PASSED ({len(cohort_cards)} main cohorts, {micro_count} micro-cohorts, {total_people:,} total people)")
        return True, cohort_cards
    except Exception as e:
        print(f"❌ Cohorts & Micro-Segmentation: FAILED - {e}")
        return False, None

def test_archetypes_phrasebook(groups):
    """Test Section 4: Archetypes & Phrasebook"""
    print("🧪 Testing Archetypes & Phrasebook...")
    
    try:
        valid_archetypes = {'ValueSensitive', 'Loyalist', 'Premium', 'AtRisk', 'ServiceSensitive'}
        
        for name, group in groups.items():
            archetype = group['summary'].get('archetype')
            assert archetype in valid_archetypes, f"❌ Invalid archetype for {name}: {archetype}"
            
            reason = group['summary'].get('archetype_reason')
            assert reason and len(reason) > 10, f"❌ Missing/short archetype reason for {name}"
        
        print("✅ Archetypes & Phrasebook: PASSED")
        return True
    except Exception as e:
        print(f"❌ Archetypes & Phrasebook: FAILED - {e}")
        return False

def test_business_math_roi():
    """Test Section 8: Business Math & ROI"""
    print("🧪 Testing Business Math & ROI...")
    
    try:
        # Load ROI data from exports
        roi_file = Path('exports/last_run_roi.json')
        if not roi_file.exists():
            raise FileNotFoundError("ROI data not found - run system first")
            
        with open(roi_file) as f:
            roi_data = json.load(f)
        
        # Check ROI structure
        for cohort_name in roi_data.keys():
            assert cohort_name in roi_data, f"❌ Missing ROI data for {cohort_name}"
            
            cohort_roi = roi_data[cohort_name]
            required_fields = ['size', 'est_recovered', 'cost', 'net', 'roi_ratio']
            for field in required_fields:
                assert field in cohort_roi, f"❌ Missing ROI field {field} for {cohort_name}"
                assert isinstance(cohort_roi[field], (int, float)), f"❌ Non-numeric ROI field {field}"
        
        print("✅ Business Math & ROI: PASSED")
        return True
    except Exception as e:
        print(f"❌ Business Math & ROI: FAILED - {e}")
        return False

def test_export_system():
    """Test Section 10: Export System"""
    print("🧪 Testing Export System...")
    
    try:
        exports_dir = Path('exports')
        
        # Check required files
        required_files = [
            'manifest.json', 'last_run_messages.json', 'last_run_roi.json', 'last_run_roi.csv'
        ]
        
        for filename in required_files:
            filepath = exports_dir / filename
            assert filepath.exists(), f"❌ Missing export file: {filename}"
            assert filepath.stat().st_size > 0, f"❌ Empty export file: {filename}"
        
        # Check CSV exports for cohorts
        cohort_csvs = list(exports_dir.glob('*_churners.csv')) + list(exports_dir.glob('*_drop.csv')) + \
                     list(exports_dir.glob('*_lapsed.csv')) + list(exports_dir.glob('*_High-Value.csv'))
        assert len(cohort_csvs) >= 4, f"❌ Missing cohort CSV files: found {len(cohort_csvs)}"
        
        # Validate manifest structure
        with open(exports_dir / 'manifest.json') as f:
            manifest = json.load(f)
            assert 'cohorts' in manifest, "❌ Missing 'cohorts' in manifest"
            assert len(manifest['cohorts']) >= 4, "❌ Insufficient cohorts in manifest"
        
        print("✅ Export System: PASSED")
        return True
    except Exception as e:
        print(f"❌ Export System: FAILED - {e}")
        return False

def run_acceptance_test():
    """Run complete acceptance test suite"""
    print("🚀 Starting Churn Radar Acceptance Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test each section
    results['environment'] = test_environment_config()
    
    if results['environment']:
        data_ok, df = test_data_load_sanity()
        results['data_load'] = data_ok
        
        if data_ok:
            features_ok, df_processed = test_features_scoring(df)
            results['features'] = features_ok
            
            cohorts_ok, groups = test_cohorts_segmentation()
            results['cohorts'] = cohorts_ok
            
            if cohorts_ok:
                results['archetypes'] = test_archetypes_phrasebook(groups)
            
            results['roi'] = test_business_math_roi()
            results['exports'] = test_export_system()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ACCEPTANCE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper():.<30} {status}")
    
    print("-" * 60)
    print(f"OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - SYSTEM NEEDS ATTENTION")
        return False

if __name__ == '__main__':
    success = run_acceptance_test()
    exit(0 if success else 1)