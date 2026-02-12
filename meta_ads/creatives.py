"""
Ad Creative-operationer til Meta Ads.
Opretter annoncekreativer (billede, video, karrusel).
"""

import json
import logging

from .api_client import MetaAPIClient

logger = logging.getLogger(__name__)


class CreativeManager:
    """Håndterer annoncekreativer mod Meta Marketing API."""

    def __init__(self, client: MetaAPIClient = None):
        self.client = client or MetaAPIClient()

    def create_link_ad_creative(
        self,
        name,
        page_id,
        message,
        link,
        image_hash=None,
        image_url=None,
        headline=None,
        description=None,
        call_to_action_type="LEARN_MORE",
    ):
        """
        Opret en link-annonce kreativ (billede + link).

        Args:
            name: Kreativ-navn.
            page_id: Facebook Page ID.
            message: Annoncetekst (primary text).
            link: Destinations-URL.
            image_hash: Hash af uploadet billede.
            image_url: URL til billede (alternativ til image_hash).
            headline: Overskrift under billedet.
            description: Beskrivelse under overskriften.
            call_to_action_type: CTA-knap type.

        Returns:
            Dict med den oprettede kreativs ID.
        """
        link_data = {
            "link": link,
            "message": message,
            "call_to_action": {"type": call_to_action_type},
        }

        if image_hash:
            link_data["image_hash"] = image_hash
        elif image_url:
            link_data["picture"] = image_url

        if headline:
            link_data["name"] = headline
        if description:
            link_data["description"] = description

        object_story_spec = {
            "page_id": page_id,
            "link_data": link_data,
        }

        params = {
            "name": name,
            "object_story_spec": json.dumps(object_story_spec),
        }

        endpoint = f"{self.client.ad_account_id}/adcreatives"
        result = self.client.post(endpoint, params)

        creative_id = result.get("id")
        logger.info("Kreativ oprettet: %s (ID: %s)", name, creative_id)
        return result

    def create_video_ad_creative(
        self,
        name,
        page_id,
        message,
        video_id,
        link,
        image_url=None,
        headline=None,
        description=None,
        call_to_action_type="LEARN_MORE",
    ):
        """Opret en video-annonce kreativ."""
        video_data = {
            "video_id": video_id,
            "message": message,
            "call_to_action": {
                "type": call_to_action_type,
                "value": {"link": link},
            },
        }

        if image_url:
            video_data["image_url"] = image_url
        if headline:
            video_data["title"] = headline
        if description:
            video_data["link_description"] = description

        object_story_spec = {
            "page_id": page_id,
            "video_data": video_data,
        }

        params = {
            "name": name,
            "object_story_spec": json.dumps(object_story_spec),
        }

        endpoint = f"{self.client.ad_account_id}/adcreatives"
        result = self.client.post(endpoint, params)

        creative_id = result.get("id")
        logger.info("Video-kreativ oprettet: %s (ID: %s)", name, creative_id)
        return result

    def create_carousel_ad_creative(
        self,
        name,
        page_id,
        message,
        cards,
        link,
        call_to_action_type="LEARN_MORE",
    ):
        """
        Opret en karrusel-annonce kreativ.

        Args:
            name: Kreativ-navn.
            page_id: Facebook Page ID.
            message: Annoncetekst.
            cards: Liste af card-dicts med keys:
                   - link, name (headline), description, image_hash/picture
            link: Fallback-link.
            call_to_action_type: CTA-knap type.

        Returns:
            Dict med den oprettede kreativs ID.
        """
        child_attachments = []
        for card in cards:
            attachment = {
                "link": card.get("link", link),
                "name": card.get("name", ""),
                "description": card.get("description", ""),
                "call_to_action": {"type": call_to_action_type},
            }
            if "image_hash" in card:
                attachment["image_hash"] = card["image_hash"]
            elif "picture" in card:
                attachment["picture"] = card["picture"]
            child_attachments.append(attachment)

        link_data = {
            "link": link,
            "message": message,
            "child_attachments": child_attachments,
            "multi_share_optimized": True,
        }

        object_story_spec = {
            "page_id": page_id,
            "link_data": link_data,
        }

        params = {
            "name": name,
            "object_story_spec": json.dumps(object_story_spec),
        }

        endpoint = f"{self.client.ad_account_id}/adcreatives"
        result = self.client.post(endpoint, params)

        creative_id = result.get("id")
        logger.info("Karrusel-kreativ oprettet: %s (ID: %s)", name, creative_id)
        return result

    def upload_image(self, image_path):
        """
        Upload et billede til annoncekontoen.

        Note: Kræver multipart form upload, som ikke understøttes
        af den simple urllib-klient. Brug `curl` eller requests-biblioteket
        til billeduploads i produktion.
        """
        raise NotImplementedError(
            "Billed-upload kræver multipart form data. "
            "Brug image_url parameter i stedet, eller implementer "
            "upload med requests-biblioteket."
        )

    def get_creatives(self, limit=25):
        """Hent alle kreativere fra kontoen."""
        params = {
            "fields": "id,name,object_story_spec,status,thumbnail_url",
            "limit": str(limit),
        }
        endpoint = f"{self.client.ad_account_id}/adcreatives"
        return self.client.get(endpoint, params)
