import random
import re
from app.db import get_db


BONUS_LINE = "Tout nouvel utilisateur qui achète un pack de 1 ou 5 crédits reçoit 1 crédit offert."


def count_sentences(text: str) -> int:
    parts = re.split(r"[.!?]+", text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    return len(parts)


def generate_social_post() -> str:
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT hook, benefit, cta, include_bonus_credit
        FROM social_templates
        WHERE is_active = 1
        ORDER BY RANDOM()
        LIMIT 1
    """)
    tpl = cur.fetchone()

    cur.execute("SELECT * FROM social_settings WHERE id = 1")
    settings = cur.fetchone()
    conn.close()

    if not tpl:
        raise ValueError("No active social template found.")

    parts = [tpl["hook"], tpl["benefit"], tpl["cta"]]

    if settings["bonus_message_enabled"] and tpl["include_bonus_credit"]:
        if BONUS_LINE not in parts:
            parts.append(BONUS_LINE)

    sentence_target = random.randint(settings["min_sentences"], settings["max_sentences"])
    final_parts = parts[:sentence_target]
    text = " ".join(final_parts).strip()

    if "KDP ULYXEOS" not in text:
        text += " KDP ULYXEOS."

    if "KDP" not in text and "Amazon KDP" not in text:
        text = "Auteurs Amazon KDP : " + text

    sentences = count_sentences(text)
    if sentences < 1 or sentences > 3:
        raise ValueError(f"Generated post has invalid sentence count: {sentences}")

    return text