"""
Ad Set-operationer til Meta Ads.
Opretter og håndterer annoncesæt med targeting.
"""

import json
import logging

from . import config
from .api_client import MetaAPIClient

logger = logging.getLogger(__name__)


class AdSetManager:
    """Håndterer annoncesæt (ad sets) mod Meta Marketing API."""

    def __init__(self, client: MetaAPIClient = None):
        self.client = client or MetaAPIClient()

    def create_ad_set(
        self,
        name,
        campaign_id,
        daily_budget_cents,
        targeting,
        start_time=None,
        end_time=None,
        billing_event=None,
        optimization_goal=None,
        bid_strategy=None,
        status=None,
        promoted_object=None,
    ):
        """
        Opret et nyt annoncesæt.

        Args:
            name: Annoncesæt-navn.
            campaign_id: ID på den tilknyttede kampagne.
            daily_budget_cents: Dagligt budget i cents.
            targeting: Targeting-dict (se build_targeting()).
            start_time: Starttidspunkt (ISO 8601).
            end_time: Sluttidspunkt (ISO 8601).
            billing_event: Faktureringsbegivenhed (f.eks. IMPRESSIONS).
            optimization_goal: Optimeringsmål (f.eks. LINK_CLICKS).
            bid_strategy: Budstrategi.
            status: ACTIVE eller PAUSED.
            promoted_object: Det promoverede objekt (f.eks. pixel_id, page_id).

        Returns:
            Dict med det oprettede annoncesæts ID.
        """
        params = {
            "name": name,
            "campaign_id": campaign_id,
            "daily_budget": str(daily_budget_cents),
            "targeting": json.dumps(targeting),
            "billing_event": billing_event
            or config.DEFAULT_AD_SET["billing_event"],
            "optimization_goal": optimization_goal
            or config.DEFAULT_AD_SET["optimization_goal"],
            "bid_strategy": bid_strategy
            or config.DEFAULT_AD_SET["bid_strategy"],
            "status": status or config.DEFAULT_AD_SET["status"],
        }

        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if promoted_object:
            params["promoted_object"] = json.dumps(promoted_object)

        endpoint = f"{self.client.ad_account_id}/adsets"
        result = self.client.post(endpoint, params)

        ad_set_id = result.get("id")
        logger.info("Annoncesæt oprettet: %s (ID: %s)", name, ad_set_id)
        return result

    def get_ad_sets(self, campaign_id=None, limit=25):
        """Hent annoncesæt, evt. filtreret på kampagne."""
        params = {
            "fields": "id,name,campaign_id,status,daily_budget,targeting,optimization_goal,start_time,end_time",
            "limit": str(limit),
        }

        if campaign_id:
            endpoint = f"{campaign_id}/adsets"
        else:
            endpoint = f"{self.client.ad_account_id}/adsets"

        return self.client.get(endpoint, params)

    def update_ad_set(self, ad_set_id, **updates):
        """Opdater et eksisterende annoncesæt."""
        if "targeting" in updates and isinstance(updates["targeting"], dict):
            updates["targeting"] = json.dumps(updates["targeting"])
        result = self.client.post(ad_set_id, updates)
        logger.info("Annoncesæt opdateret: %s", ad_set_id)
        return result

    def delete_ad_set(self, ad_set_id):
        """Slet et annoncesæt."""
        result = self.client.post(ad_set_id, {"status": "DELETED"})
        logger.info("Annoncesæt slettet: %s", ad_set_id)
        return result


def build_targeting(
    countries=None,
    age_min=18,
    age_max=65,
    genders=None,
    interests=None,
    custom_audiences=None,
    excluded_custom_audiences=None,
    locales=None,
):
    """
    Byg et targeting-objekt til brug i annoncesæt.

    Args:
        countries: Liste af landekoder, f.eks. ["DK", "SE"].
        age_min: Minimumsalder (default 18).
        age_max: Maksimumsalder (default 65).
        genders: Liste af køn [1=mænd, 2=kvinder], None = alle.
        interests: Liste af interest-dicts, f.eks. [{"id": "123", "name": "Fitness"}].
        custom_audiences: Liste af custom audience dicts.
        excluded_custom_audiences: Liste af ekskluderede custom audience dicts.
        locales: Liste af locale-koder for sprogmålretning.

    Returns:
        Dict klar til brug som targeting-parameter.
    """
    targeting = {
        "age_min": age_min,
        "age_max": age_max,
    }

    if countries:
        targeting["geo_locations"] = {"countries": countries}

    if genders:
        targeting["genders"] = genders

    if interests:
        targeting["flexible_spec"] = [{"interests": interests}]

    if custom_audiences:
        targeting["custom_audiences"] = custom_audiences

    if excluded_custom_audiences:
        targeting["excluded_custom_audiences"] = excluded_custom_audiences

    if locales:
        targeting["locales"] = locales

    return targeting
