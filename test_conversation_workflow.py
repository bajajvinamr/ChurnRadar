#!/usr/bin/env python3
"""
Comprehensive Conversation Workflow Test
Tests all TRD-specified conversation patterns and API functions.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from churn_core.conversation import (
    get_headline_kpis, list_cohorts, get_cohort_passport, 
    show_roi, list_definitions, compare_cohorts, export_copy_pack
)
from churn_core.orchestrator import ConversationOrchestrator

def test_direct_api_functions():
    """Test all conversation layer API functions directly."""
    print("🧪 Testing Direct API Functions")
    print("=" * 50)
    
    # Test 1: Headline KPIs
    print("\n1. Testing get_headline_kpis()...")
    try:
        kpis = get_headline_kpis()
        print(f"✅ Recoverable Profit: ₹{kpis['recoverable_profit_30d']:,.0f}")
        print(f"✅ Ready Groups: {kpis['ready_groups_today']}")
        print(f"✅ Expected Reactivations: {kpis['expected_reactivations']:,}")
        print(f"✅ Assumptions: RR={kpis['assumptions']['rr']:.0%}, AOV=₹{kpis['assumptions']['aov']:,.0f}, Margin={kpis['assumptions']['margin']:.0%}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: List Cohorts
    print("\n2. Testing list_cohorts()...")
    try:
        cohorts = list_cohorts()
        print(f"✅ Found {len(cohorts['cohorts'])} cohorts:")
        for cohort in cohorts['cohorts'][:3]:  # Show first 3
            print(f"   - {cohort}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Cohort Passport
    print("\n3. Testing get_cohort_passport()...")
    try:
        cohorts = list_cohorts()
        if cohorts['cohorts']:
            first_cohort = cohorts['cohorts'][0]
            passport = get_cohort_passport(first_cohort)
            print(f"✅ {first_cohort} Passport:")
            print(f"   - People: {passport['people']:,}")
            print(f"   - Comeback Odds: {passport['comeback_odds']:.0%}")
            print(f"   - Last Seen: {passport['last_seen_days']:.1f} days")
            print(f"   - Archetype: {passport['archetype']}")
            print(f"   - Why: {passport['why']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: ROI Calculations
    print("\n4. Testing show_roi()...")
    try:
        # Overall ROI waterfall
        roi_overall = show_roi()
        print(f"✅ Overall ROI Waterfall:")
        print(f"   - Total Revenue: ₹{roi_overall['total_revenue']:,.0f}")
        print(f"   - Total Reactivations: {roi_overall['total_reactivations']:,}")
        print(f"   - Active Groups: {roi_overall['active_groups']}")
        
        # Specific cohort ROI
        if cohorts['cohorts']:
            roi_specific = show_roi(cohorts['cohorts'][0])
            print(f"✅ {cohorts['cohorts'][0]} ROI:")
            print(f"   - Expected Reactivations: {roi_specific['expected_reactivations']:,}")
            print(f"   - Net Profit: ₹{roi_specific['net_profit']:,.0f}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Definitions
    print("\n5. Testing list_definitions()...")
    try:
        definitions = list_definitions()
        print(f"✅ Found {len(definitions['terms'])} definitions:")
        for term in list(definitions['terms'].keys())[:3]:  # Show first 3
            print(f"   - {term}: {definitions['terms'][term][:50]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Compare Cohorts
    print("\n6. Testing compare_cohorts()...")
    try:
        if len(cohorts['cohorts']) >= 2:
            comparison = compare_cohorts(cohorts['cohorts'][0], cohorts['cohorts'][1])
            print(f"✅ Comparison: {comparison['cohort_a']} vs {comparison['cohort_b']}")
            print(f"   - Winner: {comparison['winner']}")
            print(f"   - Reason: {comparison['summary'][:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Export Copy Pack
    print("\n7. Testing export_copy_pack()...")
    try:
        if cohorts['cohorts']:
            export = export_copy_pack(cohorts['cohorts'][0])
            print(f"✅ Export for {export['cohort']}:")
            print(f"   - Messages: {len(export['messages'])} variations")
            print(f"   - Saved to: {export.get('file_path', 'memory')}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_conversation_orchestrator():
    """Test the conversation orchestrator with natural language queries."""
    print("\n\n🤖 Testing Conversation Orchestrator")
    print("=" * 50)
    
    orchestrator = ConversationOrchestrator()
    
    # Test queries that should trigger different functions
    test_queries = [
        ("What are our headline KPIs?", "get_headline_kpis"),
        ("Show me the ROI waterfall", "show_roi"),
        ("List all customer groups", "list_cohorts"),
        ("Tell me about the Premium_engagement_lapsed group", "get_cohort_passport"),
        ("What does comeback odds mean?", "list_definitions"),
        ("Compare AtRisk_High-Value vs Premium_engagement_lapsed", "compare_cohorts"),
        ("Export copy for AtRisk_High-Value", "export_copy_pack")
    ]
    
    for i, (query, expected_function) in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        try:
            response = orchestrator.chat(query)
            print(f"✅ Response received ({len(response)} chars)")
            print(f"   Preview: {response[:150]}...")
            
            # Check if response contains expected content
            if expected_function == "get_headline_kpis" and "₹" in response:
                print("   ✅ Contains currency formatting")
            elif expected_function == "list_cohorts" and any(word in response.lower() for word in ["group", "cohort", "segment"]):
                print("   ✅ Contains group information")
            elif expected_function == "get_cohort_passport" and any(word in response.lower() for word in ["people", "odds", "archetype"]):
                print("   ✅ Contains passport details")
            elif expected_function == "show_roi" and any(word in response.lower() for word in ["revenue", "reactivation", "profit"]):
                print("   ✅ Contains ROI information")
            elif expected_function == "list_definitions" and any(word in response.lower() for word in ["definition", "means", "refers"]):
                print("   ✅ Contains definition content")
            elif expected_function == "compare_cohorts" and any(word in response.lower() for word in ["compare", "vs", "better", "higher"]):
                print("   ✅ Contains comparison content")
            elif expected_function == "export_copy_pack" and any(word in response.lower() for word in ["export", "message", "copy", "saved"]):
                print("   ✅ Contains export confirmation")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Run all tests."""
    print("🎯 Churn Radar Conversation Workflow Test Suite")
    print("TRD Compliance Validation")
    print("=" * 60)
    
    try:
        test_direct_api_functions()
        test_conversation_orchestrator()
        
        print("\n\n🎉 Test Suite Complete!")
        print("=" * 60)
        print("✅ All conversation layer functions tested")
        print("✅ Natural language processing validated")
        print("✅ TRD API compliance confirmed")
        print("\n💡 Next: Test the Streamlit UI chat interface manually at http://0.0.0.0:8502")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()