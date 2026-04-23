import random
import re
from app.db import get_db


BONUS_LINE = "Tout nouvel utilisateur qui achète un pack de 1 ou 5 crédits reçoit 1 crédit offert."

HOOKS_STANDARD = [
    "Publier sur Amazon KDP ne suffit pas toujours à vendre.",
    "Un livre sans stratégie peut rester invisible sur Amazon KDP.",
    "Beaucoup d’auteurs publient, mais peu construisent un vrai lancement.",
    "Ton marketing Amazon KDP mérite une approche plus structurée.",
]

HOOKS_VIRAL = [
    "Ton livre est publié sur Amazon KDP, mais il reste invisible.",
    "Tu peux avoir un bon livre et faire quand même un mauvais lancement.",
    "Ton problème n’est peut-être pas ton livre, mais ton marketing.",
    "Si personne ne voit ton livre, personne ne l’achètera.",
    "Tu publies sur Amazon KDP, mais tu laisses sûrement des ventes sur la table.",
    "Ton livre mérite mieux qu’un lancement bricolé.",
    "Arrête d’improviser ton marketing Amazon KDP.",
    "Sans stratégie, même un bon livre peut échouer sur Amazon KDP.",
]

HOOKS_ULTRA = [
    "Ton livre ne se vend pas ? Le problème n’est peut-être pas l’écriture.",
    "Tu publies sur Amazon KDP, mais ton livre reste noyé dans la masse.",
    "Chaque jour sans stratégie te fait perdre des ventes Amazon KDP.",
    "Improviser ton lancement, c’est laisser Amazon décider à ta place.",
    "Un mauvais marketing peut étouffer un excellent livre.",
    "Si ton livre reste invisible, il ne peut pas générer de ventes.",
    "Beaucoup d’auteurs KDP échouent non par manque de talent, mais par manque de stratégie.",
    "Tu peux écrire un très bon livre et le condamner avec un mauvais positionnement.",
    "Sur Amazon KDP, la qualité seule ne suffit pas à vendre.",
    "Le marché ne récompense pas forcément le meilleur livre, mais le mieux positionné.",
]

BENEFITS_STANDARD = [
    "KDP ULYXEOS t’aide à structurer ton marketing plus clairement.",
    "KDP ULYXEOS t’aide à clarifier ton lancement Amazon KDP.",
    "KDP ULYXEOS t’aide à mieux positionner ton livre.",
]

BENEFITS_VIRAL = [
    "KDP ULYXEOS t’aide à transformer ton manuscrit en stratégie marketing plus claire.",
    "KDP ULYXEOS t’aide à obtenir un angle plus fort pour vendre sur Amazon KDP.",
    "KDP ULYXEOS t’aide à clarifier ton lancement, ton positionnement et tes messages marketing.",
    "KDP ULYXEOS t’aide à gagner du temps sur les mots-clés, le marketing et la promo.",
    "KDP ULYXEOS t’aide à sortir de l’improvisation et à structurer ta promotion.",
]

BENEFITS_ULTRA = [
    "KDP ULYXEOS t’aide à passer d’un manuscrit à un vrai plan marketing exploitable.",
    "KDP ULYXEOS t’aide à arrêter l’improvisation et à construire une stratégie plus rentable.",
    "KDP ULYXEOS t’aide à corriger ton positionnement avant de perdre plus de visibilité.",
    "KDP ULYXEOS t’aide à transformer ton livre en offre plus claire, plus visible et plus vendable.",
    "KDP ULYXEOS t’aide à reprendre le contrôle sur les mots-clés, la promesse et le lancement.",
]

CTA_STANDARD = [
    "Découvre KDP ULYXEOS.",
    "Teste KDP ULYXEOS.",
    "Essaie KDP ULYXEOS dès maintenant.",
]

CTA_VIRAL = [
    "Donne enfin une vraie stratégie à ton livre.",
    "Arrête d’avancer à l’aveugle sur Amazon KDP.",
    "Passe d’un simple manuscrit à un vrai plan marketing.",
    "Transforme ton livre en machine à visibilité.",
]

CTA_ULTRA = [
    "Arrête de publier sans plan.",
    "Ne laisse plus ton livre disparaître dans l’ombre.",
    "Reprends le contrôle de ton lancement Amazon KDP.",
    "Donne à ton livre une vraie chance de vendre.",
    "Passe enfin d’auteur publié à auteur visible.",
]

CTA_CREDIT = [
    "Nouveau client sur pack 1 ou 5 crédits : 1 crédit offert.",
    "Pack 1 ou 5 crédits acheté : 1 crédit offert pour tout nouvel utilisateur.",
    "Offre de bienvenue : 1 crédit offert sur les packs 1 ou 5 crédits.",
]


def count_sentences(text: str) -> int:
    parts = re.split(r"[.!?]+", text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    return len(parts)


def sanitize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def enforce_brand_and_target(text: str) -> str:
    if "KDP ULYXEOS" not in text:
        text = text + " KDP ULYXEOS."

    lowered = text.lower()
    if "amazon kdp" not in lowered and "auteur" not in lowered and "auteurs" not in lowered:
        text = "Auteurs Amazon KDP : " + text

    return sanitize_text(text)


def get_mode_libraries(mode: str):
    if mode == "standard":
        return HOOKS_STANDARD, BENEFITS_STANDARD, CTA_STANDARD
    if mode == "ultra_aggressive":
        return HOOKS_ULTRA, BENEFITS_ULTRA, CTA_ULTRA
    return HOOKS_VIRAL, BENEFITS_VIRAL, CTA_VIRAL


def generate_social_post() -> str:
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM social_settings WHERE id = 1")
    settings = cur.fetchone()
    conn.close()

    min_sentences = settings["min_sentences"]
    max_sentences = settings["max_sentences"]
    bonus_enabled = settings["bonus_message_enabled"] == 1
    content_mode = settings["content_mode"] if "content_mode" in settings.keys() else "viral"

    hooks, benefits, ctas = get_mode_libraries(content_mode)

    for _ in range(20):
        hook = random.choice(hooks)
        benefit = random.choice(benefits)
        cta = random.choice(ctas)
        credit = random.choice(CTA_CREDIT)

        sentence_target = random.randint(min_sentences, max_sentences)

        if sentence_target == 1:
            text = f"{hook} {benefit}"
        elif sentence_target == 2:
            second = random.choice([benefit, cta, credit if bonus_enabled else cta])
            text = f"{hook} {second}"
        else:
            third = credit if bonus_enabled and random.random() > 0.35 else cta
            text = f"{hook} {benefit} {third}"

        text = sanitize_text(text)
        text = enforce_brand_and_target(text)

        if bonus_enabled and sentence_target < 3:
            if random.random() > 0.6 and all(x not in text for x in CTA_CREDIT):
                text = sanitize_text(text + " " + BONUS_LINE)

        text = enforce_brand_and_target(text)
        sentences = count_sentences(text)

        if 1 <= sentences <= 3:
            return text

    fallback = (
        "Ton livre ne se vend pas ? Le problème n’est peut-être pas l’écriture. "
        "KDP ULYXEOS t’aide à passer d’un manuscrit à un vrai plan marketing exploitable. "
        "Tout nouvel utilisateur qui achète un pack de 1 ou 5 crédits reçoit 1 crédit offert."
    )
    return sanitize_text(fallback)
