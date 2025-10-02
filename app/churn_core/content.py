"""
Content management for UI strings, tooltips, and help documentation.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Load content resources
_CONTENT_DIR = Path(__file__).parent.parent / "content"
_STRINGS_FILE = _CONTENT_DIR / "strings.json"
_HELP_FILE = _CONTENT_DIR / "help.md"

# Cache loaded content
_strings_cache: Optional[Dict[str, Any]] = None
_help_cache: Optional[str] = None


def load_strings() -> Dict[str, Any]:
    """Load strings.json content with caching."""
    global _strings_cache
    
    if _strings_cache is None:
        if _STRINGS_FILE.exists():
            with open(_STRINGS_FILE, 'r', encoding='utf-8') as f:
                _strings_cache = json.load(f)
        else:
            # Fallback empty structure
            _strings_cache = {
                "metrics": {},
                "columns": {},
                "archetypes": {},
                "glossary": {},
                "copy_rules": {},
                "badges": {},
                "empty_states": {},
                "tour": {},
                "section_headers": {},
                "ctas": {}
            }
    
    return _strings_cache


def load_help() -> str:
    """Load help.md content with caching."""
    global _help_cache
    
    if _help_cache is None:
        if _HELP_FILE.exists():
            with open(_HELP_FILE, 'r', encoding='utf-8') as f:
                _help_cache = f.read()
        else:
            _help_cache = "# Help documentation not found"
    
    return _help_cache


def get_metric_label(metric_key: str) -> str:
    """Get display label for a metric."""
    strings = load_strings()
    return strings.get("metrics", {}).get(metric_key, {}).get("label", metric_key)


def get_metric_tooltip(metric_key: str) -> str:
    """Get tooltip text for a metric."""
    strings = load_strings()
    return strings.get("metrics", {}).get(metric_key, {}).get("tooltip", "")


def get_column_label(column_key: str) -> str:
    """Get display label for a column."""
    strings = load_strings()
    return strings.get("columns", {}).get(column_key, {}).get("label", column_key)


def get_column_tooltip(column_key: str) -> str:
    """Get tooltip text for a column."""
    strings = load_strings()
    return strings.get("columns", {}).get(column_key, {}).get("tooltip", "")


def get_archetype_info(archetype: str) -> Dict[str, str]:
    """Get archetype label, one-liner, and guidance."""
    strings = load_strings()
    return strings.get("archetypes", {}).get(archetype, {
        "label": archetype,
        "one_liner": "",
        "guidance": ""
    })


def get_glossary_term(term_key: str) -> Dict[str, str]:
    """Get glossary term and definition."""
    strings = load_strings()
    return strings.get("glossary", {}).get(term_key, {
        "term": term_key,
        "definition": ""
    })


def get_copy_rules() -> Dict[str, Any]:
    """Get message copy rules."""
    strings = load_strings()
    return strings.get("copy_rules", {})


def get_empty_state(state_key: str) -> str:
    """Get empty state message."""
    strings = load_strings()
    return strings.get("empty_states", {}).get(state_key, "No data available.")


def get_tour_banner() -> str:
    """Get first-time tour banner text."""
    strings = load_strings()
    return strings.get("tour", {}).get("banner", "")


def get_section_header(header_key: str) -> str:
    """Get section header text."""
    strings = load_strings()
    return strings.get("section_headers", {}).get(header_key, header_key)


def get_badge_text(badge_key: str, **kwargs) -> str:
    """Get badge text with optional formatting."""
    strings = load_strings()
    template = strings.get("badges", {}).get(badge_key, "")
    return template.format(**kwargs) if template else ""


def format_tooltip(text: str) -> str:
    """Format tooltip text for display in Streamlit."""
    # Streamlit tooltips support markdown but have limited space
    # Keep concise and use line breaks effectively
    return text.strip()
