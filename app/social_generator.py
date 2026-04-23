import random
import re
from app.db import get_db


BONUS_LINE = "Nouveau client sur pack 1 ou 5 crédits : 1 crédit offert."


HOOKS_PROBLEM = [
    "Ton livre est publié sur Amazon KDP, mais il reste invisible.",
    "Publier sur Amazon KDP ne suffit pas à vendre.",
    "Beaucoup d’auteurs publient. Très peu savent vraiment se vendre.",
    "Tu peux avoir un bon livre et faire quand même un mauvais lancement.",
    "Ton problème n’est peut-être pas ton livre, mais ton marketing.",
    "Si personne ne voit ton livre, personne ne l’achètera.",
    "Improviser ton marketing sur Amazon KDP te coûte du temps et des ventes.",
    "Un livre sans stratégie peut passer totalement inaperçu sur Amazon KDP.",
]

HOOKS_AGGRESSIVE = [
    "Tu publies sur Amazon KDP, mais tu laisses sûrement des ventes sur la table.",
    "Ton livre mérite mieux qu’un lancement bricolé.",
    "Arrête d’improviser ton marketing Amazon KDP.",
    "Ton manuscrit ne se vendra pas tout seul.",
    "Sans stratégie, même un bon livre peut échouer sur Amazon KDP.",
    "Le vrai problème de beaucoup d’auteurs KDP, ce n’est pas l’écriture. C’est le positionnement.",
    "Tu peux écrire un bon livre et perdre la bataille de la visibilité.",
    "Sur Amazon KDP, l’improvisation coûte cher.",
]

HOOKS_CURIOSITY = [
    "Et si ton manuscrit pouvait te donner lui-même ta stratégie marketing ?",
    "Et si tu pouvais transformer ton livre en plan d’action marketing en quelques minutes ?",
    "Et si tu arrêtais enfin de deviner quoi faire après la publication ?",
    "Tu veux aller plus vite sur Amazon KDP sans avancer à l’aveugle ?",
    "Et si tu pouvais clarifier ton lancement Amazon KDP dès aujourd’hui ?",
]

BENEFITS = [
    "KDP ULYXEOS t’aide à transformer ton manuscrit en stratégie marketing plus claire.",
    "KDP ULYXEOS t’aide à obtenir un angle plus fort pour vendre sur Amazon KDP.",
    "KDP ULYXEOS t’aide à clarifier ton lancement, ton positionnement et tes messages marketing.",
    "KDP ULYXEOS t’aide à gagner du temps sur les mots-clés, le marketing et la promo.",
    "KDP ULYXEOS t’aide à construire une base plus solide pour vendre ton livre.",
    "KDP ULYXEOS t’aide à sortir de l’improvisation et à structurer ta promotion.",
    "KDP ULYXEOS t’aide à mieux positionner ton livre pour le marché Amazon KDP.",
]

CTA_SOFT = [
    "Découvre KDP ULYXEOS.",
    "Teste KDP ULYXEOS.",
    "Essaie KDP ULYXEOS dès maintenant.",
    "Passe à KDP ULYXEOS.",
]

CTA_STRONG = [
    "Donne enfin une vraie stratégie à ton livre.",
    "Arrête d’avancer à l’aveugle sur Amazon KDP.",
    "Passe d’un simple manuscrit à un vrai plan marketing.",
    "Transforme ton livre en machine à visibilité.",
    "Prends une longueur d’avance sur ton lancement Amazon KDP.",
]

CTA_CREDIT = [
    "Tout nouvel utilisateur qui achète un pack de 1 ou 5 crédits reçoit 1 crédit offert.",
    "Pack 1 ou 5 crédits acheté : 1 crédit offert pour tout nouvel utilisateur.",
    "Offre de bienvenue : 1 crédit offert sur les packs 1 ou 5 crédits.",
]

ANGLE_LIBRARY = {
    "problem": HOOKS_PROBLEM,
    "aggressive": HOOKS_AGGRESSIVE,
    "curiosity": HOOKS_CURIOSITY,
}


def count_sentences(text: str) -> int:
    parts = re.split(r"[.!?]+", text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    return len(parts)


def sanitize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def choose_angle() -> str:
    return random.choice(["problem", "aggressive", "curiosity"])


def build_parts():
    angle = choose_angle()
    hook = random.choice(ANGLE_LIBRARY[angle])
    benefit = random.choice(BENEFITS)

    # On varie la fin selon le ton
    if angle == "aggressive":
        cta = random.choice(CTA_STRONG)
    elif angle == "curiosity":
        cta = random.choice(CTA_SOFT + CTA_STRONG)
    else:
        cta = random.choice(CTA_SOFT + CTA_STRONG)

    credit = random.choice(CTA_CREDIT)

    return angle, hook, benefit, cta, credit


def enforce_brand_and_target(text: str) -> str:
    if "KDP ULYXEOS" not in text:
        text = text + " KDP ULYXEOS."

    lowered = text.lower()
    if "amazon kdp" not in lowered and "auteur" not in lowered and "auteurs" not in lowered:
        text = "Auteurs Amazon KDP : " + text

    return sanitize_text(text)


def generate_social_post() -> str:
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM social_settings WHERE id = 1")
    settings = cur.fetchone()
    conn.close()

    min_sentences = settings["min_sentences"]
    max_sentences = settings["max_sentences"]
    bonus_enabled = settings["bonus_message_enabled"] == 1

    # On tente plusieurs générations jusqu'à obtenir 1 à 3 phrases
    for _ in range(20):
        angle, hook, benefit, cta, credit = build_parts()

        sentence_target = random.randint(min_sentences, max_sentences)

        if sentence_target == 1:
            # 1 phrase : hook + bénéfice compact
            text = f"{hook} {benefit}"
        elif sentence_target == 2:
            # 2 phrases : hook + bénéfice / CTA
            second = random.choice([benefit, cta, credit if bonus_enabled else cta])
            text = f"{hook} {second}"
        else:
            # 3 phrases : hook + bénéfice + CTA ou offre
            third = credit if bonus_enabled and random.random() > 0.4 else cta
            text = f"{hook} {benefit} {third}"

        text = sanitize_text(text)
        text = enforce_brand_and_target(text)

        # Si bonus activé et pas encore mentionné parfois on le force sur les posts courts
        if bonus_enabled and sentence_target < 3:
            if random.random() > 0.55 and all(x not in text for x in CTA_CREDIT):
                text = sanitize_text(text + " " + BONUS_LINE)

        # Nettoyage final
        text = enforce_brand_and_target(text)
        sentences = count_sentences(text)

        if 1 <= sentences <= 3:
            return text

    # Fallback propre
    fallback = (
        "Auteurs Amazon KDP, arrêtez d’improviser votre marketing. "
        "KDP ULYXEOS vous aide à transformer votre manuscrit en stratégie plus claire. "
        "Tout nouvel utilisateur qui achète un pack de 1 ou 5 crédits reçoit 1 crédit offert."
    )
    return sanitize_text(fallback)
