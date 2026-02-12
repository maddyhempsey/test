"""
Konfiguration til Meta Ads automation.
Alle følsomme værdier læses fra environment variables.
"""

import os

# Meta API credentials - sættes via environment variables
META_APP_ID = os.environ.get("META_APP_ID", "")
META_APP_SECRET = os.environ.get("META_APP_SECRET", "")
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
META_AD_ACCOUNT_ID = os.environ.get("META_AD_ACCOUNT_ID", "")

# API version
API_VERSION = "v21.0"

# Standard kampagne-defaults
DEFAULT_CAMPAIGN = {
    "objective": "OUTCOME_TRAFFIC",
    "status": "PAUSED",
    "special_ad_categories": [],
}

DEFAULT_AD_SET = {
    "billing_event": "IMPRESSIONS",
    "optimization_goal": "LINK_CLICKS",
    "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    "status": "PAUSED",
}

# Tilgængelige kampagnemål
CAMPAIGN_OBJECTIVES = [
    "OUTCOME_AWARENESS",
    "OUTCOME_ENGAGEMENT",
    "OUTCOME_LEADS",
    "OUTCOME_SALES",
    "OUTCOME_TRAFFIC",
    "OUTCOME_APP_PROMOTION",
]

# Tilgængelige optimeringsmål
OPTIMIZATION_GOALS = [
    "LINK_CLICKS",
    "IMPRESSIONS",
    "REACH",
    "LANDING_PAGE_VIEWS",
    "LEAD_GENERATION",
    "CONVERSIONS",
    "VALUE",
]
