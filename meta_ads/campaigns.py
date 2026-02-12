"""
Kampagne-operationer til Meta Ads.
Opretter, opdaterer og henter kampagner.
"""

import json
import logging

from . import config
from .api_client import MetaAPIClient

logger = logging.getLogger(__name__)


class CampaignManager:
    """Håndterer kampagne-CRUD-operationer mod Meta Marketing API."""

    def __init__(self, client: MetaAPIClient = None):
        self.client = client or MetaAPIClient()

    def create_campaign(
        self,
        name,
        objective=None,
        status=None,
        daily_budget_cents=None,
        lifetime_budget_cents=None,
        special_ad_categories=None,
    ):
        """
        Opret en ny kampagne.

        Args:
            name: Kampagnenavn.
            objective: Kampagnemål (f.eks. OUTCOME_TRAFFIC).
            status: ACTIVE eller PAUSED.
            daily_budget_cents: Dagligt budget i cents (øre).
            lifetime_budget_cents: Samlet budget i cents (øre).
            special_ad_categories: Liste af specielle annoncekategorier.

        Returns:
            Dict med den oprettede kampagnes ID.
        """
        params = {
            "name": name,
            "objective": objective or config.DEFAULT_CAMPAIGN["objective"],
            "status": status or config.DEFAULT_CAMPAIGN["status"],
            "special_ad_categories": json.dumps(
                special_ad_categories
                if special_ad_categories is not None
                else config.DEFAULT_CAMPAIGN["special_ad_categories"]
            ),
        }

        if daily_budget_cents:
            params["daily_budget"] = str(daily_budget_cents)

        if lifetime_budget_cents:
            params["lifetime_budget"] = str(lifetime_budget_cents)

        endpoint = f"{self.client.ad_account_id}/campaigns"
        result = self.client.post(endpoint, params)

        campaign_id = result.get("id")
        logger.info("Kampagne oprettet: %s (ID: %s)", name, campaign_id)
        return result

    def get_campaigns(self, status_filter=None, limit=25):
        """Hent alle kampagner fra kontoen."""
        params = {
            "fields": "id,name,objective,status,daily_budget,lifetime_budget,created_time",
            "limit": str(limit),
        }
        if status_filter:
            params["effective_status"] = json.dumps(status_filter)

        endpoint = f"{self.client.ad_account_id}/campaigns"
        return self.client.get(endpoint, params)

    def update_campaign(self, campaign_id, **updates):
        """Opdater en eksisterende kampagne."""
        result = self.client.post(campaign_id, updates)
        logger.info("Kampagne opdateret: %s", campaign_id)
        return result

    def delete_campaign(self, campaign_id):
        """Slet en kampagne (sætter status til DELETED)."""
        result = self.client.post(campaign_id, {"status": "DELETED"})
        logger.info("Kampagne slettet: %s", campaign_id)
        return result
