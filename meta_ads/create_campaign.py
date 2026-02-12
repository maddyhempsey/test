#!/usr/bin/env python3
"""
Meta Ads kampagne-automatisering.

Automatisk oprettelse af en komplet kampagnestruktur:
  Kampagne → Annoncesæt (med targeting) → Kreativ → Annonce

Brug:
    python -m meta_ads.create_campaign --config kampagne.json
    python -m meta_ads.create_campaign --interactive

Kræver environment variables:
    META_ACCESS_TOKEN   - Adgangstoken fra Meta Business Suite
    META_AD_ACCOUNT_ID  - Annoncekonto-ID (med eller uden act_ prefix)
"""

import argparse
import json
import logging
import sys

from .ad_sets import AdSetManager, build_targeting
from .ads import AdManager
from .api_client import MetaAPIClient, MetaAPIError
from .campaigns import CampaignManager
from .creatives import CreativeManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def create_full_campaign(config_data):
    """
    Opret en komplet kampagnestruktur ud fra en konfiguration.

    Args:
        config_data: Dict med kampagnekonfiguration.

    Returns:
        Dict med alle oprettede ressource-ID'er.
    """
    client = MetaAPIClient()
    campaigns = CampaignManager(client)
    ad_sets = AdSetManager(client)
    creatives = CreativeManager(client)
    ads = AdManager(client)

    results = {"campaigns": [], "ad_sets": [], "creatives": [], "ads": []}

    # 1. Opret kampagne
    camp_config = config_data["campaign"]
    logger.info("Opretter kampagne: %s", camp_config["name"])

    campaign_result = campaigns.create_campaign(
        name=camp_config["name"],
        objective=camp_config.get("objective"),
        status=camp_config.get("status", "PAUSED"),
        daily_budget_cents=camp_config.get("daily_budget_cents"),
        lifetime_budget_cents=camp_config.get("lifetime_budget_cents"),
        special_ad_categories=camp_config.get("special_ad_categories"),
    )
    campaign_id = campaign_result["id"]
    results["campaigns"].append(campaign_result)
    logger.info("Kampagne oprettet med ID: %s", campaign_id)

    # 2. Opret annoncesæt
    for adset_config in config_data.get("ad_sets", []):
        targeting_config = adset_config.get("targeting", {})
        targeting = build_targeting(
            countries=targeting_config.get("countries", ["DK"]),
            age_min=targeting_config.get("age_min", 18),
            age_max=targeting_config.get("age_max", 65),
            genders=targeting_config.get("genders"),
            interests=targeting_config.get("interests"),
            custom_audiences=targeting_config.get("custom_audiences"),
            locales=targeting_config.get("locales"),
        )

        logger.info("Opretter annoncesæt: %s", adset_config["name"])
        adset_result = ad_sets.create_ad_set(
            name=adset_config["name"],
            campaign_id=campaign_id,
            daily_budget_cents=adset_config["daily_budget_cents"],
            targeting=targeting,
            start_time=adset_config.get("start_time"),
            end_time=adset_config.get("end_time"),
            optimization_goal=adset_config.get("optimization_goal"),
            status=adset_config.get("status", "PAUSED"),
            promoted_object=adset_config.get("promoted_object"),
        )
        adset_id = adset_result["id"]
        results["ad_sets"].append(adset_result)
        logger.info("Annoncesæt oprettet med ID: %s", adset_id)

        # 3. Opret kreativere og annoncer for hvert annoncesæt
        for creative_config in adset_config.get("creatives", []):
            creative_type = creative_config.get("type", "link")

            if creative_type == "link":
                creative_result = creatives.create_link_ad_creative(
                    name=creative_config["name"],
                    page_id=creative_config["page_id"],
                    message=creative_config["message"],
                    link=creative_config["link"],
                    image_hash=creative_config.get("image_hash"),
                    image_url=creative_config.get("image_url"),
                    headline=creative_config.get("headline"),
                    description=creative_config.get("description"),
                    call_to_action_type=creative_config.get(
                        "call_to_action_type", "LEARN_MORE"
                    ),
                )
            elif creative_type == "video":
                creative_result = creatives.create_video_ad_creative(
                    name=creative_config["name"],
                    page_id=creative_config["page_id"],
                    message=creative_config["message"],
                    video_id=creative_config["video_id"],
                    link=creative_config["link"],
                    image_url=creative_config.get("image_url"),
                    headline=creative_config.get("headline"),
                    description=creative_config.get("description"),
                    call_to_action_type=creative_config.get(
                        "call_to_action_type", "LEARN_MORE"
                    ),
                )
            elif creative_type == "carousel":
                creative_result = creatives.create_carousel_ad_creative(
                    name=creative_config["name"],
                    page_id=creative_config["page_id"],
                    message=creative_config["message"],
                    cards=creative_config["cards"],
                    link=creative_config["link"],
                    call_to_action_type=creative_config.get(
                        "call_to_action_type", "LEARN_MORE"
                    ),
                )
            else:
                logger.warning("Ukendt kreativ-type: %s, springer over", creative_type)
                continue

            creative_id = creative_result["id"]
            results["creatives"].append(creative_result)
            logger.info("Kreativ oprettet med ID: %s", creative_id)

            # 4. Opret annonce
            ad_name = creative_config.get("ad_name", f"Ad - {creative_config['name']}")
            ad_result = ads.create_ad(
                name=ad_name,
                ad_set_id=adset_id,
                creative_id=creative_id,
                status=adset_config.get("status", "PAUSED"),
            )
            results["ads"].append(ad_result)
            logger.info("Annonce oprettet med ID: %s", ad_result["id"])

    return results


def interactive_mode():
    """Interaktiv tilstand - spørg brugeren om kampagneindstillinger."""
    print("\n=== Meta Ads Kampagne-automatisering ===\n")

    campaign_name = input("Kampagnenavn: ").strip()
    if not campaign_name:
        print("Fejl: Kampagnenavn er påkrævet.")
        sys.exit(1)

    print("\nTilgængelige kampagnemål:")
    objectives = [
        "OUTCOME_AWARENESS",
        "OUTCOME_ENGAGEMENT",
        "OUTCOME_LEADS",
        "OUTCOME_SALES",
        "OUTCOME_TRAFFIC",
    ]
    for i, obj in enumerate(objectives, 1):
        print(f"  {i}. {obj}")

    obj_choice = input(f"Vælg mål (1-{len(objectives)}) [5]: ").strip() or "5"
    objective = objectives[int(obj_choice) - 1]

    daily_budget = input("Dagligt budget i DKK (f.eks. 100): ").strip()
    daily_budget_cents = int(float(daily_budget) * 100) if daily_budget else 10000

    page_id = input("Facebook Page ID: ").strip()
    if not page_id:
        print("Fejl: Page ID er påkrævet.")
        sys.exit(1)

    countries_input = input("Lande (kommasepareret, f.eks. DK,SE) [DK]: ").strip()
    countries = [c.strip().upper() for c in countries_input.split(",")] if countries_input else ["DK"]

    age_min = int(input("Minimumsalder [18]: ").strip() or "18")
    age_max = int(input("Maksimumsalder [65]: ").strip() or "65")

    ad_message = input("Annoncetekst: ").strip()
    ad_link = input("Destinations-URL: ").strip()
    ad_headline = input("Overskrift: ").strip()
    ad_image_url = input("Billede-URL (valgfrit): ").strip()

    config_data = {
        "campaign": {
            "name": campaign_name,
            "objective": objective,
            "status": "PAUSED",
        },
        "ad_sets": [
            {
                "name": f"{campaign_name} - Annoncesæt 1",
                "daily_budget_cents": daily_budget_cents,
                "targeting": {
                    "countries": countries,
                    "age_min": age_min,
                    "age_max": age_max,
                },
                "creatives": [
                    {
                        "type": "link",
                        "name": f"{campaign_name} - Kreativ 1",
                        "page_id": page_id,
                        "message": ad_message,
                        "link": ad_link,
                        "headline": ad_headline,
                        "image_url": ad_image_url or None,
                        "call_to_action_type": "LEARN_MORE",
                    }
                ],
            }
        ],
    }

    print("\n--- Kampagneoversigt ---")
    print(json.dumps(config_data, indent=2, ensure_ascii=False))

    confirm = input("\nOpret kampagne? (j/n) [j]: ").strip().lower()
    if confirm and confirm != "j":
        print("Afbrudt.")
        sys.exit(0)

    return config_data


def main():
    parser = argparse.ArgumentParser(
        description="Automatisk oprettelse af Meta Ads kampagner"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Sti til JSON-konfigurationsfil",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Kør i interaktiv tilstand",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Vis konfiguration uden at oprette noget",
    )
    args = parser.parse_args()

    if args.interactive:
        config_data = interactive_mode()
    elif args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    else:
        parser.print_help()
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] Konfiguration der ville blive oprettet:")
        print(json.dumps(config_data, indent=2, ensure_ascii=False))
        sys.exit(0)

    try:
        results = create_full_campaign(config_data)
        print("\n=== Kampagne oprettet! ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
    except MetaAPIError as e:
        logger.error("Meta API fejl: %s (kode: %s)", e, e.error_code)
        sys.exit(1)
    except Exception as e:
        logger.error("Uventet fejl: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
