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
    "Amazon n’est pas une bibliothèque, c'est un moteur de recherche. Traites-tu ton livre comme tel ?",
    "Écrire un best-seller est un talent. Le vendre est une science.",
    "Le 'Post and Pray' (publier et prier) n'est pas une stratégie marketing, c'est un billet de loterie.",
    "Pourquoi 90 % des livres sur KDP ne dépassent jamais les 10 ventes ?",
    "Ton livre est exceptionnel, mais l'algorithme d'Amazon n'a pas de cœur : il n'a que des données.",
    "J’ai ouvert le capot d'Amazon KDP pour voir ce qui faisait vraiment vendre.",
    "J'ai remplacé mes doutes d'auteur par des scripts Python. Voici le résultat.",
    "Et si tu pouvais injecter de la donnée là où tu ne mettais que de l'intuition ?",
    "J'ai automatisé la partie la plus ennuyeuse de KDP pour ne garder que le plaisir d'écrire.",
    "Le marketing KDP n'est pas un art divin, c'est une structure. J'ai codé cette structure pour toi.",
    "Tu as passé 6 mois à écrire. Vas-tu vraiment gâcher ce travail en 6 minutes à cause d'un mauvais SEO ?",
    "Arrête de jeter ton budget pub par les fenêtres sur des mots-clés qui ne convertissent pas.",
    "Ton manuscrit est prêt ? Félicitations. Maintenant, construisons son armure de vente.",
    "La différence entre un auteur qui stagne et un auteur qui décolle ? La clarté de son lancement.",
    "Invisible ou irrésistible : choisis ton camp sur Amazon.",
    "KDP n'est pas une option, c'est une compétition.",
    "Ton livre mérite une audience, pas seulement une étagère virtuelle.",
    "L'écriture est ton job. Le marketing est celui d'Ulyxeos.",

]

BENEFITS = [
    "KDP ULYXEOS t’aide à mieux positionner ton livre.",
    "KDP ULYXEOS t’aide à clarifier ton lancement Amazon KDP.",
    "KDP ULYXEOS t’aide à structurer ton marketing plus clairement.",
    "KDP ULYXEOS transforme ton manuscrit en base marketing exploitable.",
    "KDP ULYXEOS t’aide à trouver un angle plus clair pour vendre ton livre.",
    "KDP ULYXEOS t’aide à gagner du temps sur les mots-clés, le positionnement et la promotion.",
    "KDP ULYXEOS automatise la corvée administrative pour te redonner du temps pour écrire.",
    "Passe de l'upload de ton manuscrit à un dossier marketing complet en quelques secondes.",
    "KDP ULYXEOS fait le travail de recherche à ta place : tu n'as plus qu'à publier.",
    "Libère-toi des tableaux Excel et laisse l'algorithme d'Ulyxeos optimiser tes métadonnées.",
    "KDP ULYXEOS transforme ton histoire en un argumentaire de vente irrésistible.",
    "Trouve les mots exacts pour toucher le cœur de tes lecteurs et déclencher l'achat.",
    "Ne devine plus ce que veulent tes lecteurs : KDP ULYXEOS décrypte leur psychologie d'achat pour toi.",
    "Génère une description de livre optimisée qui convertit les curieux en acheteurs.",
    "Passe d'un simple manuscrit à une stratégie de lancement digne d'une maison d'édition.",
    "KDP ULYXEOS te donne l'avantage injuste pour dominer ta niche sur Amazon.",
    "Identifie ton angle d'attaque marketing unique pour te démarquer de la concurrence.",
    "Construis un univers visuel et stratégique cohérent autour de ton livre.",
    "Élimine le stress du lancement grâce à une feuille de route claire et structurée.",
    "KDP ULYXEOS est ton copilote intelligent dans la jungle d'Amazon KDP.",
    "Ne te demande plus jamais 'par où commencer' : Ulyxeos te guide pas à pas.",
    "Le pont entre ton talent d'écrivain et ton succès commercial.",
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
    "Réclame l'un des 50 accès privilège.",
    "Sois parmi les premiers à automatiser ton succès KDP.",
    "Profite de ton analyse offerte avant qu'il ne soit trop tard.",
    "Rejoins les 50 auteurs qui publient plus intelligemment.",
    "Génère ton dossier marketing complet en un clic.",
    "Récupère 3 heures sur ton prochain lancement.",
    "Automatise la corvée KDP et retourne à ton écriture.",
    "Passe du manuscrit au plan d'action en moins de 2 minutes.",
    "Donne à ton livre les armes pour dominer sa niche.",
    "Découvre les mots-clés qui vont transformer ton classement Amazon.",
    "Obtiens une stratégie de lancement digne d'une grande maison d'édition.",
    "Arrête de deviner, commence à vendre avec une vraie stratégie.",
    "Deviens bêta-testeur d'Ulyxeos et booste tes publications.",
    "Teste l'outil, donne-moi ton avis, et garde tes résultats.",
    "Aide-moi à construire le futur de l'auto-édition.",
    "Essaye gratuitement : je ne veux que ton retour d'auteur.",

]

BONUS = [
    "BONUS : Envie de tester ? Répondez simplement -Ulyxeos- en commentaire ! J'offre une analyse complète et gratuite aux 50 premiers. Tout ce que je vous demande en échange, c’est de partager ce post et de me donner votre avis honnête pour m'aider à perfectionner l'outil.",
]

HASHTAGS = [
        "#auteurautoedite",
        "#auteurs",
        "#amazonkdp",
        "#auteurfrancophone",
        "#auteurindependant",
        "#auteurs",
        "#autoedition",
        "#communautéauteurs",
        "#conseilsauteurs",
        "#copywritingfrancais",
        "#innovationlitteraire",
        "#kdp",
        "#kindlepublishing",
        "#kdp2026",
        "#kdpbeginner",
        "#kdpcommunity",
        "#kdpfrance",
        "#kdpmarketing",
        "#kdpulyxeos",
        "#kdpoptimization",
        "#kdpniches",
        "#kdpkeywords",
        "#kindlepublishing",
        "#kdpstrategy",
        "#kdptools",
        "#livreindependant",
        "#nichekdp",
        "#motsclesamazon",
        "#outilecrivain",
        "#motscleskdp",
        "#publicitékdp",
        "#seoamazon",
        "#strategiemarketing",
        "#ulyxeos",
        "#publierunlivre",
        "#ulyxeosanalyse",
        "#ulyxeosauteur",
        "#vendresonlivre",
        "#ulyxeoscreator",
        "#vendresuramazon",
        "#trouveruneniche"

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
