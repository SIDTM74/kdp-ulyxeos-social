import time
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
            # --------------------------------------------------
            # 1. CREATE INSTAGRAM MEDIA CONTAINER
            # --------------------------------------------------

            create_url = f"https://graph.facebook.com/v23.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"

            payload = {
                "caption": text,
                "access_token": INSTAGRAM_ACCESS_TOKEN,
            }

            media_type = (media.get("media_type") or "").lower()

            if media_type == "video":
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
                    "response": {
                        "step": "create_media_container",
                        "http_status": create_response.status_code,
                        "data": create_data,
                    },
                }

            creation_id = create_data["id"]

            # --------------------------------------------------
            # 2. WAIT UNTIL INSTAGRAM MEDIA IS READY
            # --------------------------------------------------

            last_status_data = {}

            for _ in range(54):  # 54 x 5 sec = max 240 sec
                status_url = f"https://graph.facebook.com/v23.0/{creation_id}"

                status_response = requests.get(
                    status_url,
                    params={
                        "fields": "status_code",
                        "access_token": INSTAGRAM_ACCESS_TOKEN,
                    },
                    timeout=30,
                )

                last_status_data = status_response.json()
                status_code = last_status_data.get("status_code")

                if status_code == "FINISHED":
                    break

                if status_code == "ERROR":
                    return {
                        "platform": self.platform_name,
                        "status": "failed",
                        "platform_post_id": None,
                        "response": {
                            "step": "wait_media_ready",
                            "error": "Instagram media processing failed",
                            "data": last_status_data,
                        },
                    }

                time.sleep(5)

            else:
                return {
                    "platform": self.platform_name,
                    "status": "failed",
                    "platform_post_id": None,
                    "response": {
                        "step": "wait_media_ready",
                        "error": "Instagram media not ready after waiting",
                        "creation_id": creation_id,
                        "last_status": last_status_data,
                    },
                }

            # --------------------------------------------------
            # 3. PUBLISH MEDIA
            # --------------------------------------------------

            publish_url = f"https://graph.facebook.com/v23.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"

            publish_payload = {
                "creation_id": creation_id,
                "access_token": INSTAGRAM_ACCESS_TOKEN,
            }

            publish_response = requests.post(
                publish_url,
                data=publish_payload,
                timeout=60,
            )

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
                "response": {
                    "step": "publish_media",
                    "http_status": publish_response.status_code,
                    "data": publish_data,
                },
            }

        except Exception as exc:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {
                    "error": str(exc),
                    "type": exc.__class__.__name__,
                },
            }
