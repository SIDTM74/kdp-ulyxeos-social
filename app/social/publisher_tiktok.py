import requests
from app.social.publishers_base import BasePublisher
from app.config import TIKTOK_ACCESS_TOKEN, TIKTOK_VIDEO_URL


class TikTokPublisher(BasePublisher):
    platform_name = "tiktok"

    def publish(self, text: str, media: dict | None = None) -> dict:
        if not TIKTOK_ACCESS_TOKEN:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {"error": "TikTok access token missing"},
            }

        # V1 simple : on force une URL vidéo publique
        video_url = TIKTOK_VIDEO_URL
        if not video_url:
            return {
                "platform": self.platform_name,
                "status": "failed",
                "platform_post_id": None,
                "response": {"error": "TikTok video URL missing"},
            }

        try:
            url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
            headers = {
                "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
                "Content-Type": "application/json; charset=UTF-8",
            }

            payload = {
                "post_info": {
                    "title": text[:90],
                    "privacy_level": "SELF_ONLY",
                    "disable_comment": False,
                    "disable_duet": False,
                    "disable_stitch": False,
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": video_url
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=60)
            data = response.json()

            if response.ok:
                return {
                    "platform": self.platform_name,
                    "status": "success",
                    "platform_post_id": data.get("data", {}).get("publish_id"),
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
