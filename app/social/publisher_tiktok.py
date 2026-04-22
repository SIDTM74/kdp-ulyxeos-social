from app.social.publishers_base import BasePublisher


class TikTokPublisher(BasePublisher):
    platform_name = "tiktok"

    def publish(self, text: str, media: dict | None = None) -> dict:
        if not media:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {"error": "TikTok requires media in this workflow"}
            }

        return {
            "platform": self.platform_name,
            "status": "success",
            "platform_post_id": "tt_demo_123",
            "response": {
                "message": "TikTok publish simulation ok",
                "text": text,
                "media": media["filename"]
            }
        }