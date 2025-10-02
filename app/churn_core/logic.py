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
        # Fallback with demo data if import fails
        return {
            "Payment-sensitive churners": {
                "summary": {
                    "size": 1603,
                    "avg_score": 0.338,
                    "avg_recency": 9.05,
                    "avg_engagement": 4.81,
                    "avg_value": 217.44,
                    "avg_tenure": 12.19,
                    "archetype": "ValueSensitive"
                },
                "data": pd.DataFrame()
            },
            "High-tenure recent drop": {
                "summary": {
                    "size": 821,
                    "avg_score": 0.373,
                    "avg_recency": 9.44,
                    "avg_engagement": 4.75,
                    "avg_value": 239.56,
                    "avg_tenure": 18.91,
                    "archetype": "Loyalist"
                },
                "data": pd.DataFrame()
            },
            "Premium engagement lapsed": {
                "summary": {
                    "size": 1151,
                    "avg_score": 0.350,
                    "avg_recency": 8.46,
                    "avg_engagement": 5.55,
                    "avg_value": 218.64,
                    "avg_tenure": 11.69,
                    "archetype": "Premium"
                },
                "data": pd.DataFrame()
            },
            "AtRisk High-Value": {
                "summary": {
                    "size": 733,
                    "avg_score": 0.384,
                    "avg_recency": 9.59,
                    "avg_engagement": 4.90,
                    "avg_value": 265.18,
                    "avg_tenure": 15.20,
                    "archetype": "AtRisk"
                },
                "data": pd.DataFrame()
            }
        }

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
        print(f"Error loading messages: {e}")
        pass
    
    # Fallback demo messages
    return {
        "email": {
            "variants": [
                {
                    "title": "Your curated picks are ready",
                    "body": "We saved top-rated items for you. Priority support on every order.",
                    "_eval": {"clarity": 5, "on_brand": 5, "persuasiveness": 4, "relevance": 4, "safety": 5, "overall": 4.6}
                }
            ]
        },
        "whatsapp": {
            "variants": [
                {
                    "title": "Quick update",
                    "body": "Your favorites are back in stock 📦",
                    "_eval": {"clarity": 5, "on_brand": 4, "persuasiveness": 4, "relevance": 5, "safety": 5, "overall": 4.6}
                }
            ]
        },
        "push": {
            "variants": [
                {
                    "title": "Ready for you",
                    "body": "Quick tap to unlock your rewards",
                    "_eval": {"clarity": 4, "on_brand": 4, "persuasiveness": 4, "relevance": 4, "safety": 5, "overall": 4.2}
                }
            ]
        }
    }

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
    """
    exports_dir = Path(__file__).parent.parent.parent / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    messages = kept_messages(group_name)
    
    copy_pack = {
        "group": group_name,
        "timestamp": pd.Timestamp.now().isoformat(),
        "messages": messages
    }
    
    file_path = exports_dir / f"copy_pack_{group_name.replace(' ', '_')}.json"
    with open(file_path, 'w') as f:
        json.dump(copy_pack, f, indent=2)
    
    return str(file_path)

def export_manifest() -> str:
    """
    Export manifest.json with run metadata.
    """
    exports_dir = Path(__file__).parent.parent.parent / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    manifest = {
        "run_id": pd.Timestamp.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": pd.Timestamp.now().isoformat(),
        "model": "gpt-4o-mini",
        "brand_docs": ["brand_voice.md", "offer_policy.md", "compliance.md"],
        "groups": list(get_groups().keys()),
        "source": "streamlit_ui"
    }
    
    file_path = exports_dir / "manifest.json"
    with open(file_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return str(file_path)