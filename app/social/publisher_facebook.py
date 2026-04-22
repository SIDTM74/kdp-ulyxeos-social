from app.social.publishers_base import BasePublisher


class FacebookPublisher(BasePublisher):
    platform_name = "facebook"

    def publish(self, text: str, media: dict | None = None) -> dict:
        return {
            "platform": self.platform_name,
            "status": "success",
            "platform_post_id": "fb_demo_123",
            "response": {
                "message": "Facebook publish simulation ok",
                "text": text,
                "media": media["filename"] if media else None
            }
        }