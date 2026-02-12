"""
Ad-operationer til Meta Ads.
Opretter selve annoncerne, som binder annoncesæt og kreativere sammen.
"""

import logging

from .api_client import MetaAPIClient

logger = logging.getLogger(__name__)


class AdManager:
    """Håndterer annoncer (ads) mod Meta Marketing API."""

    def __init__(self, client: MetaAPIClient = None):
        self.client = client or MetaAPIClient()

    def create_ad(self, name, ad_set_id, creative_id, status="PAUSED"):
        """
        Opret en ny annonce.

        Args:
            name: Annoncenavn.
            ad_set_id: ID på annoncesættet.
            creative_id: ID på den kreative.
            status: ACTIVE eller PAUSED.

        Returns:
            Dict med den oprettede annonces ID.
        """
        params = {
            "name": name,
            "adset_id": ad_set_id,
            "creative": f'{{"creative_id": "{creative_id}"}}',
            "status": status,
        }

        endpoint = f"{self.client.ad_account_id}/ads"
        result = self.client.post(endpoint, params)

        ad_id = result.get("id")
        logger.info("Annonce oprettet: %s (ID: %s)", name, ad_id)
        return result

    def get_ads(self, ad_set_id=None, limit=25):
        """Hent annoncer, evt. filtreret på annoncesæt."""
        params = {
            "fields": "id,name,adset_id,creative,status,created_time",
            "limit": str(limit),
        }

        if ad_set_id:
            endpoint = f"{ad_set_id}/ads"
        else:
            endpoint = f"{self.client.ad_account_id}/ads"

        return self.client.get(endpoint, params)

    def update_ad(self, ad_id, **updates):
        """Opdater en eksisterende annonce."""
        result = self.client.post(ad_id, updates)
        logger.info("Annonce opdateret: %s", ad_id)
        return result

    def delete_ad(self, ad_id):
        """Slet en annonce."""
        result = self.client.post(ad_id, {"status": "DELETED"})
        logger.info("Annonce slettet: %s", ad_id)
        return result

    def get_ad_insights(self, ad_id, date_preset="last_7d", fields=None):
        """
        Hent performance-data for en annonce.

        Args:
            ad_id: Annonce-ID.
            date_preset: Tidsperiode (f.eks. last_7d, last_30d, today).
            fields: Liste af metrics at hente.

        Returns:
            Dict med insights-data.
        """
        default_fields = [
            "impressions",
            "clicks",
            "spend",
            "cpc",
            "cpm",
            "ctr",
            "reach",
            "actions",
            "cost_per_action_type",
        ]
        params = {
            "fields": ",".join(fields or default_fields),
            "date_preset": date_preset,
        }

        endpoint = f"{ad_id}/insights"
        return self.client.get(endpoint, params)
