import os
import shutil
from typing import Optional
from app.db import get_db
from app.utils import now_iso
from app.config import SOCIAL_IMAGE_DIR, SOCIAL_VIDEO_DIR


def save_uploaded_media(upload_file, media_type: str) -> str:
    target_dir = SOCIAL_IMAGE_DIR if media_type == "image" else SOCIAL_VIDEO_DIR
    filepath = os.path.join(target_dir, upload_file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return filepath


def create_media_record(filename: str, filepath: str, media_type: str, platform_hint: str = "all") -> None:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO social_media (filename, filepath, media_type, platform_hint, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, filepath, media_type, platform_hint, now_iso()))
    conn.commit()
    conn.close()


def get_active_media_for_platform(platform: str) -> Optional[dict]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM social_media
        WHERE is_active = 1
          AND (platform_hint = 'all' OR platform_hint = ?)
        ORDER BY usage_count ASC, last_used_at ASC NULLS FIRST, RANDOM()
        LIMIT 1
    """, (platform,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def mark_media_used(media_id: int) -> None:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE social_media
        SET usage_count = usage_count + 1,
            last_used_at = ?
        WHERE id = ?
    """, (now_iso(), media_id))
    conn.commit()
    conn.close()