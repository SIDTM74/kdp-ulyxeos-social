import requests
from app.social.publishers_base import BasePublisher
from app.config import INSTAGRAM_BUSINESS_ACCOUNT_ID, INSTAGRAM_ACCESS_TOKEN


class InstagramPublisher(BasePublisher):
    platform_name = "instagram"

    def publish(self, text: str, media: dict | None = None) -> dict:
        if not INSTAGRAM_BUSINESS_ACCOUNT_ID or not INSTAGRAM_ACCESS_TOKEN:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {"error": "Instagram credentials missing"},
            }

        if not media:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {"error": "Instagram requires media"},
            }

        media_url = (media.get("public_url") or "").strip()
        if not media_url:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {"error": "Missing public_url for Instagram media"},
            }

        try:
            create_url = f"https://graph.facebook.com/v23.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
            payload = {
                "caption": text,
                "access_token": INSTAGRAM_ACCESS_TOKEN,
            }

            if media.get("media_type") == "video":
                payload["media_type"] = "REELS"
                payload["video_url"] = media_url
            else:
                payload["image_url"] = media_url

            create_response = requests.post(create_url, data=payload, timeout=60)
            create_data = create_response.json()

            if not create_response.ok or "id" not in create_data:
                return {
                    "platform": self.platform_name,
                    "status": "failed",
                    "platform_post_id": None,
                    "response": create_data,
                }

            creation_id = create_data["id"]

            publish_url = f"https://graph.facebook.com/v23.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": INSTAGRAM_ACCESS_TOKEN,
            }

            publish_response = requests.post(publish_url, data=publish_payload, timeout=60)
            publish_data = publish_response.json()

            if publish_response.ok and "id" in publish_data:
                return {
                    "platform": self.platform_name,
                    "status": "success",
                    "platform_post_id": publish_data["id"],
                    "response": publish_data,
                }

            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": publish_data,
            }

        except Exception as exc:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {"error": str(exc)},
            }
