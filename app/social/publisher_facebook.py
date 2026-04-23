import requests
from app.social.publishers_base import BasePublisher
from app.config import FACEBOOK_PAGE_ID, FACEBOOK_ACCESS_TOKEN


class FacebookPublisher(BasePublisher):
    platform_name = "facebook"

    def publish(self, text: str, media: dict | None = None) -> dict:
        if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {"error": "Facebook credentials missing"},
            }

        try:
            # Texte seul
            if not media:
                url = f"https://graph.facebook.com/v23.0/{FACEBOOK_PAGE_ID}/feed"
                payload = {
                    "message": text,
                    "access_token": FACEBOOK_ACCESS_TOKEN,
                }
                response = requests.post(url, data=payload, timeout=30)
                data = response.json()

                if response.ok and "id" in data:
                    return {
                        "platform": self.platform_name,
                        "status": "success",
                        "platform_post_id": data["id"],
                        "response": data,
                    }

                return {
                    "platform": self.platform_name,
                    "status": "failed",
                    "platform_post_id": None,
                    "response": data,
                }

            # Si tu veux plus tard : média Facebook
            # pour l’instant on reste simple et fiable
            url = f"https://graph.facebook.com/v23.0/{FACEBOOK_PAGE_ID}/feed"
            payload = {
                "message": text,
                "access_token": FACEBOOK_ACCESS_TOKEN,
            }
            response = requests.post(url, data=payload, timeout=30)
            data = response.json()

            if response.ok and "id" in data:
                return {
                    "platform": self.platform_name,
                    "status": "success",
                    "platform_post_id": data["id"],
                    "response": data,
                }

            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": data,
            }

        except Exception as exc:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {"error": str(exc)},
            }
