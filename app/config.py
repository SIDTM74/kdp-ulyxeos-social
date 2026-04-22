import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "KDP ULYXEOS")

SOCIAL_DB_PATH = os.getenv("SOCIAL_DB_PATH", "/var/data/social/social.db")
SOCIAL_IMAGE_DIR = os.getenv("SOCIAL_IMAGE_DIR", "/var/data/social/images")
SOCIAL_VIDEO_DIR = os.getenv("SOCIAL_VIDEO_DIR", "/var/data/social/videos")
SOCIAL_LOG_DIR = os.getenv("SOCIAL_LOG_DIR", "/var/data/social/logs")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me-now")
SESSION_SECRET = os.getenv("SESSION_SECRET", "super-secret-session-key")
INTERNAL_AUTPOST_SECRET = os.getenv("INTERNAL_AUTPOST_SECRET", "super-secret-internal-key")

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")
ADMIN_NOTIFICATION_EMAIL = os.getenv("ADMIN_NOTIFICATION_EMAIL", ADMIN_EMAIL)

FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")

INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")
TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")