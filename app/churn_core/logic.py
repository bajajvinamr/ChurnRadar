"""
Core integration layer for Streamlit UI.
Wraps existing notebook functions for clean data access.
"""
import sys
import os
from typing import Dict, Any, List, Optional
import pandas as pd
import json
from pathlib import Path

# Add parent directory to path so we can import run_churn_radar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_groups() -> Dict[str, Dict[str, Any]]:
    """
    Returns cohort_cards structure with group summaries and data.
    { group_name: {"summary": {...}, "data": pd.DataFrame} }
    """
    try:
        # Change to parent directory to import and run the backend
        original_cwd = os.getcwd()
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(parent_dir)
        
        # Import and run the analysis
        import run_churn_radar as rcr
        rcr.run()
        
        # Restore original directory
        os.chdir(original_cwd)
        
        return rcr.cohort_cards
    except Exception as e:
        raise Exception(f"Failed to load groups: {e}. Ensure run_churn_radar.py has been executed successfully and all dependencies are installed.")

def get_defaults() -> Dict[str, Dict[str, float]]:
    """
    Returns default ROI parameters for each group.
    """
    return {
        "Payment-sensitive churners": {
            "reactivation_rate": 0.08,
            "aov": 1500,
            "margin": 0.60,
            "send_cost": 0.25,
            "incentive_rate": 0.05
        },
        "High-tenure recent drop": {
            "reactivation_rate": 0.12,
            "aov": 1800,
            "margin": 0.65,
            "send_cost": 0.25,
            "incentive_rate": 0.03
        },
        "Premium engagement lapsed": {
            "reactivation_rate": 0.15,
            "aov": 2000,
            "margin": 0.62,
            "send_cost": 0.25,
            "incentive_rate": 0.02
        },
        "AtRisk High-Value": {
            "reactivation_rate": 0.07,
            "aov": 3000,
            "margin": 0.60,
            "send_cost": 0.25,
            "incentive_rate": 0.08
        }
    }

def get_archetype_notes() -> Dict[str, Dict[str, str]]:
    """
    Returns archetype-specific messaging guidance.
    """
    return {
        "ValueSensitive": {
            "what_to_say": "Lead with value proposition and clear savings",
            "what_to_avoid": "Avoid premium positioning or luxury language"
        },
        "Loyalist": {
            "what_to_say": "Acknowledge their history and offer exclusive benefits",
            "what_to_avoid": "Don't treat them like new customers"
        },
        "Premium": {
            "what_to_say": "Emphasize curation, quality, and personalized service",
            "what_to_avoid": "Avoid generic discounts or mass-market messaging"
        },
        "AtRisk": {
            "what_to_say": "Address concerns directly and offer immediate value",
            "what_to_avoid": "Don't use high-pressure tactics"
        },
        "ServiceSensitive": {
            "what_to_say": "Highlight support quality and problem resolution",
            "what_to_avoid": "Don't focus solely on product features"
        }
    }

def kept_messages(group_name: str) -> Dict[str, Any]:
    """
    Get kept message variants for all channels for a specific group.
    """
    try:
        # Try to read from last run exports
        exports_path = Path(__file__).parent.parent.parent / "exports" / "last_run_messages.json"
        if exports_path.exists():
            with open(exports_path, 'r') as f:
                data = json.load(f)
                if group_name in data:
                    group_data = data[group_name]
                    # Check if this has channel data already
                    if "variants" in group_data:
                        # Single channel format - assume email
                        return {
                            "email": {
                                "variants": group_data["variants"]
                            },
                            "whatsapp": {
                                "variants": [
                                    {
                                        "title": "Quick update",
                                        "body": "Your favorites are back in stock 📦",
                                        "_eval": group_data.get("_eval", {"overall": 4.0})
                                    }
                                ]
                            },
                            "push": {
                                "variants": [
                                    {
                                        "title": "Ready for you",
                                        "body": "Quick tap to unlock your rewards",
                                        "_eval": group_data.get("_eval", {"overall": 4.0})
                                    }
                                ]
                            }
                        }
                    else:
                        # Multi-channel format
                        return group_data
    except Exception as e:
        raise Exception(f"Failed to load messages for {group_name}: {e}. Ensure run_churn_radar.py has generated the exports.")

def calculate_roi(group_name: str, params: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Calculate ROI for a group with given parameters.
    """
    groups = get_groups()
    defaults = get_defaults()
    
    if group_name not in groups:
        return {}
    
    group_summary = groups[group_name]["summary"]
    group_defaults = defaults.get(group_name, {})
    
    # Use provided params or defaults
    config = {**group_defaults, **(params or {})}
    
    size = group_summary["size"]
    reactivation_rate = config.get("reactivation_rate", 0.08)
    aov = config.get("aov", 1500)
    margin = config.get("margin", 0.60)
    send_cost_per_person = config.get("send_cost", 0.25)
    incentive_rate = config.get("incentive_rate", 0.05)
    incentive_takeup = config.get("incentive_takeup", 0.4)
    
    # Calculate outputs
    reactivated = int(size * reactivation_rate)
    revenue = reactivated * aov
    gross_profit = revenue * margin
    
    # Calculate costs
    send_costs = size * send_cost_per_person
    incentive_costs = reactivated * aov * incentive_rate * incentive_takeup
    total_costs = send_costs + incentive_costs
    
    net_profit = gross_profit - total_costs
    romi = (net_profit / total_costs) if total_costs > 0 else 0
    
    return {
        "inputs": {
            "size": size,
            "reactivation_rate": reactivation_rate,
            "aov": aov,
            "margin": margin,
            "send_cost": send_cost_per_person,
            "incentive_rate": incentive_rate,
            "incentive_takeup": incentive_takeup
        },
        "outputs": {
            "reactivated": reactivated,
            "revenue": revenue,
            "gross_profit": gross_profit,
            "send_costs": send_costs,
            "incentive_costs": incentive_costs,
            "total_costs": total_costs,
            "net_profit": net_profit,
            "romi": romi
        }
    }

def export_group_csv(group_name: str) -> str:
    """
    Export group data to CSV and return the file path.
    """
    groups = get_groups()
    if group_name not in groups:
        return ""
    
    # Create exports directory if it doesn't exist
    exports_dir = Path(__file__).parent.parent.parent / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    # Use existing CSV if available, otherwise create minimal one
    group_file = group_name.replace(" ", "_").replace("-", "_") + ".csv"
    file_path = exports_dir / group_file
    
    if not file_path.exists():
        # Create a minimal CSV with group info
        group_data = groups[group_name]
        summary = group_data["summary"]
        
        df = pd.DataFrame([{
            "group": group_name,
            "size": summary["size"],
            "avg_score": summary["avg_score"],
            "avg_recency": summary["avg_recency"],
            "avg_value": summary["avg_value"]
        }])
        df.to_csv(file_path, index=False)
    
    return str(file_path)

def export_copy_pack(group_name: str) -> str:
    """
    Export copy pack JSON for a group and return file path.
    Schema matches UX spec: cohort, archetype, audience_size, channels, assumptions
    """
    exports_dir = Path(__file__).parent.parent.parent / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    groups = get_groups()
    defaults = get_defaults()
    
    if group_name not in groups:
        return ""
    
    group_data = groups[group_name]
    summary = group_data["summary"]
    config = defaults.get(group_name, {})
    messages = kept_messages(group_name)
    
    # Build channels structure with variants and UTM parameters
    channels = {}
    for channel_name, channel_data in messages.items():
        variants = channel_data.get("variants", [])
        if variants:
            variant = variants[0]  # Keep the best variant
            channels[channel_name] = {
                "variant": {
                    "title": variant.get("title", ""),
                    "body": variant.get("body", ""),
                    "_eval": variant.get("_eval", {})
                },
                "utm": {
                    "source": "churn_radar",
                    "medium": channel_name,
                    "campaign": f"winback_{summary.get('archetype', 'general').lower()}_v1"
                }
            }
    
    copy_pack = {
        "cohort": group_name,
        "archetype": summary.get("archetype", "Premium"),
        "audience_size": summary["size"],
        "channels": channels,
        "assumptions": {
            "reactivation_rate": config.get("reactivation_rate", 0.12),
            "aov": config.get("aov", 1800),
            "margin": config.get("margin", 0.62)
        },
        "timestamp": pd.Timestamp.now().isoformat()
    }
    
    file_path = exports_dir / f"copy_pack_{group_name.replace(' ', '_')}.json"
    with open(file_path, 'w') as f:
        json.dump(copy_pack, f, indent=2)
    
    return str(file_path)

def export_manifest() -> str:
    """
    Export manifest.json with run metadata.
    Schema: run_id, timestamp, dataset, model/version, groups, thresholds, assumptions
    """
    exports_dir = Path(__file__).parent.parent.parent / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    groups = get_groups()
    defaults = get_defaults()
    
    # Calculate aggregate counts
    total_customers = sum(g["summary"]["size"] for g in groups.values())
    
    manifest = {
        "run_id": pd.Timestamp.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": pd.Timestamp.now().isoformat(),
        "dataset": {
            "name": "E Commerce Dataset.csv",
            "total_customers": total_customers,
            "active_groups": len([g for g in groups.values() if g["summary"]["size"] > 0])
        },
        "model": {
            "name": "gpt-4o-mini",
            "version": "2024-07-18",
            "provider": "openai"
        },
        "brand_docs": [
            "brand_overview.md",
            "brand_voice.md", 
            "offer_policy.md", 
            "compliance.md"
        ],
        "groups": list(groups.keys()),
        "thresholds": {
            "min_group_size": 100,
            "min_comeback_odds": 0.05,
            "eval_overall": 3.8,
            "eval_safety": 4.0
        },
        "default_assumptions": {
            "reactivation_rate": 0.12,
            "aov": 1800,
            "margin": 0.62,
            "send_cost": 0.25
        },
        "source": "streamlit_ui",
        "timezone": "Asia/Kolkata"
    }
    
    file_path = exports_dir / "manifest.json"
    with open(file_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return str(file_path)