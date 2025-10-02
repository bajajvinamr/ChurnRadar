#!/usr/bin/env python3
"""
Test script to verify Streamlit app data loading works correctly.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from churn_core.logic import get_groups, get_defaults, kept_messages
from churn_core.data import format_inr

def test_data_loading():
    print("🧪 Testing Churn Radar Streamlit Integration...")
    
    # Test groups loading
    print("\n1. Testing group data loading...")
    try:
        groups = get_groups()
        print(f"✅ Loaded {len(groups)} groups:")
        for name, data in groups.items():
            summary = data["summary"]
            print(f"   • {name}: {summary['size']:,} people, {summary['avg_score']:.3f} score")
    except Exception as e:
        print(f"❌ Error loading groups: {e}")
        return False
    
    # Test defaults loading
    print("\n2. Testing defaults loading...")
    try:
        defaults = get_defaults()
        print(f"✅ Loaded defaults for {len(defaults)} groups:")
        for name, config in defaults.items():
            print(f"   • {name}: {config['reactivation_rate']*100:.1f}% rate, ₹{config['aov']:,} AOV")
    except Exception as e:
        print(f"❌ Error loading defaults: {e}")
        return False
    
    # Test messages loading
    print("\n3. Testing messages loading...")
    try:
        first_group = list(groups.keys())[0]
        messages = kept_messages(first_group)
        print(f"✅ Loaded messages for '{first_group}':")
        for channel, data in messages.items():
            variants = data.get("variants", [])
            if variants:
                variant = variants[0]
                print(f"   • {channel}: '{variant.get('title', 'No title')}'")
    except Exception as e:
        print(f"❌ Error loading messages: {e}")
        return False
    
    # Test formatting
    print("\n4. Testing formatting functions...")
    try:
        test_amount = 1234567
        formatted = format_inr(test_amount)
        print(f"✅ Format test: {test_amount} → {formatted}")
    except Exception as e:
        print(f"❌ Error in formatting: {e}")
        return False
    
    print("\n🎉 All tests passed! Streamlit app should work correctly.")
    return True

if __name__ == "__main__":
    success = test_data_loading()
    sys.exit(0 if success else 1)