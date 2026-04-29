import random
import re

SITE_URL = "https://kdp-ulyxeos.com"

HOOKS = [
    "Publier sur Amazon KDP ne suffit pas toujours à vendre.",
    "Un livre sans stratégie peut rester invisible sur Amazon KDP.",
    "Beaucoup d’auteurs publient, mais peu construisent un vrai lancement.",
    "Ton marketing Amazon KDP mérite une approche plus structurée.",
    "Ton livre mérite mieux qu’un lancement au hasard.",
    "Tu peux avoir un bon livre et rester invisible sur Amazon.",
    "Arrête d’improviser ton lancement Amazon KDP.",
    "Sur Amazon KDP, la visibilité ne se gagne pas au hasard.",
    "Tu publies sur Amazon… mais personne ne voit ton livre ?",
    "Ton livre est en ligne… mais invisible ?",
    "Tu as publié ton livre… et maintenant ?",
    "Pourquoi ton livre ne se vend pas sur Amazon ?",
]

BENEFITS = [
    "KDP ULYXEOS t’aide à mieux positionner ton livre.",
    "KDP ULYXEOS t’aide à clarifier ton lancement Amazon KDP.",
    "KDP ULYXEOS t’aide à structurer ton marketing plus clairement.",
    "KDP ULYXEOS transforme ton manuscrit en base marketing exploitable.",
    "KDP ULYXEOS t’aide à trouver un angle plus clair pour vendre ton livre.",
    "KDP ULYXEOS t’aide à gagner du temps sur les mots-clés, le positionnement et la promotion.",
]

CTA = [
    "Teste KDP ULYXEOS dès maintenant.",
    "Découvre KDP ULYXEOS.",
    "Donne à ton livre une stratégie plus claire.",
    "Passe d’un simple manuscrit à un vrai plan marketing.",
    "Arrête d’avancer à l’aveugle.",
    "Teste KDP ULYXEOS dès maintenant.",
    "Découvre ton potentiel de vente en quelques minutes.",
    "Passe à une vraie stratégie Amazon.",
]

BONUS = [
    "Nouveau client sur pack 1 ou 5 crédits : 1 crédit offert.",
    "Tout nouvel utilisateur qui achète un pack de 1 ou 5 crédits reçoit 1 crédit offert.",
    "Offre de bienvenue : 1 crédit offert sur les packs 1 ou 5 crédits.",
]

HASHTAGS = [
    "#AmazonKDP",
    "#AutoEdition",
    "#AuteurIndependant",
    "#KDP",
    "#MarketingAuteur",
    "#PublierUnLivre",
    "#Ecriture",
    "#Livre",
    "#KdpUlyxeos",
]


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def generate_hashtags(max_tags: int = 5) -> str:
    tags = random.sample(HASHTAGS, k=min(max_tags, len(HASHTAGS)))
    return " ".join(tags)


def generate_social_post() -> str:
    hook = random.choice(HOOKS)
    benefit = random.choice(BENEFITS)
    cta = random.choice(CTA)
    bonus = random.choice(BONUS)

    formats = [
        f"{hook} {benefit} {cta}",
        f"{hook} {benefit} {bonus}",
        f"{hook} {cta} {bonus}",
        f"{hook} {benefit}",
    ]

    text = clean_text(random.choice(formats))

    if SITE_URL not in text:
        text += f"\n\n🚀 Découvre KDP ULYXEOS :\n{SITE_URL}"

    text += f"\n\n{generate_hashtags()}"

    return text
