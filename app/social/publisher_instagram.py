from app.social.publishers_base import BasePublisher


class InstagramPublisher(BasePublisher):
    platform_name = "instagram"

    def publish(self, text: str, media: dict | None = None) -> dict:
        if not media:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {"error": "Instagram requires media in this workflow"}
            }

        return {
            "platform": self.platform_name,
            "status": "success",
            "platform_post_id": "ig_demo_123",
            "response": {
                "message": "Instagram publish simulation ok",
                "text": text,
                "media": media["filename"]
            }
        }