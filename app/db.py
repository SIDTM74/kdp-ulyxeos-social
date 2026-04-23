import os
import sqlite3
from app.config import SOCIAL_DB_PATH, SOCIAL_IMAGE_DIR, SOCIAL_VIDEO_DIR, SOCIAL_LOG_DIR


def ensure_directories() -> None:
    os.makedirs(os.path.dirname(SOCIAL_DB_PATH), exist_ok=True)
    os.makedirs(SOCIAL_IMAGE_DIR, exist_ok=True)
    os.makedirs(SOCIAL_VIDEO_DIR, exist_ok=True)
    os.makedirs(SOCIAL_LOG_DIR, exist_ok=True)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(
        SOCIAL_DB_PATH,
        timeout=30,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=30000;")

    return conn


def ensure_column_exists(cur: sqlite3.Cursor, table_name: str, column_name: str, alter_sql: str) -> None:
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cur.fetchall()]
    if column_name not in columns:
        cur.execute(alter_sql)


def init_db() -> None:
    ensure_directories()
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS social_media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        media_type TEXT NOT NULL,
        platform_hint TEXT DEFAULT 'all',
        is_active INTEGER NOT NULL DEFAULT 1,
        usage_count INTEGER NOT NULL DEFAULT 0,
        last_used_at TEXT,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS social_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hook TEXT NOT NULL,
        benefit TEXT NOT NULL,
        cta TEXT NOT NULL,
        include_bonus_credit INTEGER NOT NULL DEFAULT 1,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS social_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        posts_per_day INTEGER NOT NULL,
        facebook_enabled INTEGER NOT NULL,
        instagram_enabled INTEGER NOT NULL,
        tiktok_enabled INTEGER NOT NULL,
        email_notifications_enabled INTEGER NOT NULL,
        notification_email TEXT NOT NULL,
        bonus_message_enabled INTEGER NOT NULL,
        min_sentences INTEGER NOT NULL,
        max_sentences INTEGER NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    ensure_column_exists(
        cur,
        "social_settings",
        "content_mode",
        "ALTER TABLE social_settings ADD COLUMN content_mode TEXT NOT NULL DEFAULT 'viral'"
    )

    cur.execute("""
    CREATE TABLE IF NOT EXISTS social_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_text TEXT NOT NULL,
        sentence_count INTEGER NOT NULL,
        media_id INTEGER,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(media_id) REFERENCES social_media(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS social_post_targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        social_post_id INTEGER NOT NULL,
        platform TEXT NOT NULL,
        platform_post_id TEXT,
        status TEXT NOT NULL,
        response_json TEXT,
        sent_at TEXT,
        FOREIGN KEY(social_post_id) REFERENCES social_posts(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS social_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trigger_type TEXT NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        status TEXT NOT NULL,
        summary TEXT
    )
    """)

    cur.execute("SELECT COUNT(*) AS count FROM social_settings")
    row = cur.fetchone()
    if row["count"] == 0:
        cur.execute("""
        INSERT INTO social_settings (
            id, posts_per_day, facebook_enabled, instagram_enabled, tiktok_enabled,
            email_notifications_enabled, notification_email, bonus_message_enabled,
            min_sentences, max_sentences, updated_at, content_mode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
        """, (1, 4, 1, 1, 1, 1, "admin@example.com", 1, 1, 3, "viral"))
    else:
        cur.execute("""
            UPDATE social_settings
            SET content_mode = COALESCE(content_mode, 'viral')
            WHERE id = 1
        """)

    cur.execute("SELECT COUNT(*) AS count FROM social_templates")
    row = cur.fetchone()
    if row["count"] == 0:
        defaults = [
            (
                "Auteurs Amazon KDP, arrêtez d’improviser votre marketing.",
                "KDP ULYXEOS vous aide à transformer votre manuscrit en stratégie plus claire.",
                "Nouveau client sur pack 1 ou 5 crédits : 1 crédit offert."
            ),
            (
                "Votre livre mérite mieux qu’un lancement au hasard sur Amazon KDP.",
                "KDP ULYXEOS vous aide à gagner du temps sur votre marketing.",
                "Essayez KDP ULYXEOS dès maintenant."
            ),
            (
                "Publier sur Amazon KDP ne suffit pas toujours à vendre.",
                "KDP ULYXEOS vous aide à mieux positionner votre livre.",
                "Pack 1 ou 5 crédits acheté = 1 crédit offert pour tout nouvel utilisateur."
            )
        ]
        for hook, benefit, cta in defaults:
            cur.execute("""
            INSERT INTO social_templates (hook, benefit, cta, include_bonus_credit, is_active, created_at)
            VALUES (?, ?, ?, 1, 1, datetime('now'))
            """, (hook, benefit, cta))

    conn.commit()
    conn.close()
