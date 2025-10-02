#!/usr/bin/env python3
"""
Brand Kit Validator CLI
Validates the presence and basic structure of brand kit documents.
"""
import os
import sys
from pathlib import Path

REQUIRED_FILES = [
    "brand_overview.md",
    "brand_voice.md",
    "compliance.md",
    "offer_policy.md"
]

def validate_brand_kit(brand_kit_path: str = "brand_kit") -> bool:
    """
    Validate brand kit directory and files.
    Returns True if valid, False otherwise.
    """
    kit_path = Path(brand_kit_path)
    
    if not kit_path.exists():
        print(f"❌ Brand kit directory not found: {brand_kit_path}")
        return False
    
    if not kit_path.is_dir():
        print(f"❌ Brand kit path is not a directory: {brand_kit_path}")
        return False
    
    missing_files = []
    empty_files = []
    
    for filename in REQUIRED_FILES:
        file_path = kit_path / filename
        if not file_path.exists():
            missing_files.append(filename)
        elif file_path.stat().st_size == 0:
            empty_files.append(filename)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    if empty_files:
        print(f"❌ Empty files: {', '.join(empty_files)}")
        return False
    
    # Check basic content structure
    overview_path = kit_path / "brand_overview.md"
    with open(overview_path, 'r') as f:
        content = f.read().lower()
        if not any(keyword in content for keyword in ["company", "brand", "overview"]):
            print("⚠️  brand_overview.md may not contain expected content")
    
    compliance_path = kit_path / "compliance.md"
    with open(compliance_path, 'r') as f:
        content = f.read().lower()
        if not any(keyword in content for keyword in ["compliance", "legal", "policy"]):
            print("⚠️  compliance.md may not contain expected content")
    
    print("✅ Brand kit validation passed")
    print(f"📁 Location: {kit_path.absolute()}")
    print(f"📄 Files: {len(REQUIRED_FILES)} present and non-empty")
    return True

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Churn Radar brand kit")
    parser.add_argument("--path", default="brand_kit", help="Path to brand kit directory")
    
    args = parser.parse_args()
    
    print("🔍 Churn Radar Brand Kit Validator")
    print("=" * 40)
    
    success = validate_brand_kit(args.path)
    
    if not success:
        print("\n💡 Remediation: Ensure all four brand documents exist and contain content:")
        for filename in REQUIRED_FILES:
            print(f"   - {filename}")
        sys.exit(1)
    
    print("\n🎉 Ready for message generation!")
    sys.exit(0)

if __name__ == "__main__":
    main()