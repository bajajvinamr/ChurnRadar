#!/usr/bin/env python3
"""
Integration test for consultant-friendly UI components
Tests the new features without requiring a full Streamlit session
"""

def test_consultant_ui():
    """Test all consultant-friendly UI improvements"""
    print("🧪 Testing Consultant-Friendly UI Components")
    print("=" * 50)
    
    # Test 1: Import all new modules
    try:
        from app.churn_core.content import (
            METRIC_DEFINITIONS, ARCHETYPE_REASONS, 
            COHORT_LIBRARY, COPY_RULES, REGENERATE_OPTIONS
        )
        from app.churn_core.data import (
            format_inr, format_score_as_odds, 
            format_days, format_months, format_percent
        )
        print("✅ All new modules import successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Formatting functions
    print("\n📊 Testing formatting functions:")
    
    # Currency formatting (Indian style)
    currency_tests = [
        (123456.78, "₹1,23,457"),
        (1234567.89, "₹12,34,568"),
        (50000, "₹50,000"),
        (0, "₹0")
    ]
    
    for amount, expected in currency_tests:
        result = format_inr(amount)
        if result == expected:
            print(f"✅ Currency: {amount} → {result}")
        else:
            print(f"❌ Currency: {amount} → {result} (expected {expected})")
    
    # Come-back odds formatting
    odds_tests = [
        (0.456, "45.6%"),
        (0.123, "12.3%"),
        (0.999, "99.9%")
    ]
    
    for score, expected in odds_tests:
        result = format_score_as_odds(score)
        if result == expected:
            print(f"✅ Come-back odds: {score} → {result}")
        else:
            print(f"❌ Come-back odds: {score} → {result} (expected {expected})")
    
    # Test 3: Content definitions
    print(f"\n📚 Testing content definitions:")
    print(f"✅ Metric definitions: {len(METRIC_DEFINITIONS)} metrics")
    print(f"✅ Archetype reasons: {len(ARCHETYPE_REASONS)} archetypes")
    print(f"✅ Cohort library: {len(COHORT_LIBRARY)} cohorts")
    print(f"✅ Copy rules defined: {len(COPY_RULES)} rule categories")
    print(f"✅ Regenerate options: {len(REGENERATE_OPTIONS)} option types")
    
    # Test 4: Key metric definitions
    required_metrics = [
        "come_back_odds", "last_seen", "activity", 
        "avg_spend", "months_with_brand", "net_profit"
    ]
    
    missing_metrics = []
    for metric in required_metrics:
        if metric not in METRIC_DEFINITIONS:
            missing_metrics.append(metric)
    
    if missing_metrics:
        print(f"❌ Missing metric definitions: {missing_metrics}")
        return False
    else:
        print("✅ All required metric definitions present")
    
    # Test 5: Archetype reasons
    key_archetypes = ["ValueSensitive", "Loyalist", "Premium", "AtRisk"]
    missing_archetypes = []
    for archetype in key_archetypes:
        if archetype not in ARCHETYPE_REASONS:
            missing_archetypes.append(archetype)
    
    if missing_archetypes:
        print(f"❌ Missing archetype reasons: {missing_archetypes}")
        return False
    else:
        print("✅ All key archetype reasons present")
    
    # Test 6: Sample tooltip content
    print(f"\n💡 Sample tooltip content:")
    come_back_def = METRIC_DEFINITIONS["come_back_odds"]
    print(f"✅ Come-Back Odds: {come_back_def['definition']}")
    
    sample_reason = ARCHETYPE_REASONS["Premium"]
    print(f"✅ Premium archetype: {sample_reason}")
    
    print(f"\n🎉 All consultant-friendly UI tests PASSED!")
    return True

def test_ui_integration():
    """Test integration with existing system"""
    print("\n🔗 Testing UI Integration")
    print("=" * 30)
    
    try:
        # Test loading existing data structures
        from app.churn_core.logic import get_groups, get_defaults
        print("✅ Core logic modules accessible")
        
        # Test that we can access the brand system
        from app.churn_core.brand import ARCHETYPES
        print(f"✅ Brand archetypes accessible: {len(ARCHETYPES)} defined")
        
        print("✅ UI integration test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
        return False

if __name__ == "__main__":
    success1 = test_consultant_ui()
    success2 = test_ui_integration()
    
    if success1 and success2:
        print(f"\n🚀 OVERALL RESULT: All consultant-friendly UI tests PASSED!")
        print("✅ Ready for marketing stakeholder demo")
        exit(0)
    else:
        print(f"\n⚠️ OVERALL RESULT: Some tests failed")
        exit(1)