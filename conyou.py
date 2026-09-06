# youagronome_v2.py
# YouAgronoMe — Plateforme Agritech Sénégal
# Version 2 : architecture structurée, données sourcées, météo, sols, cartographie,
# consultance, conseil >1000 fiches, documents et rapports PDF.
#
# IMPORTANT :
# - Les chiffres du tableau de bord sont limités aux données officielles explicitement
#   identifiées comme telles.
# - Les recommandations agronomiques générées doivent être validées par un conseiller
#   local et, pour la fertilisation/phytosanitaire, par une analyse de sol et les
#   homologations/recommandations en vigueur.
# - Les prévisions opérationnelles utilisées dans le module météo sont issues d'Open-Meteo.
#   L'ANACIM reste la référence institutionnelle pour les bulletins et alertes officiels.

from __future__ import annotations

import io
import json
import math
import os
import sqlite3
import hashlib
import hmac
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st

# Modules optionnels
try:
    import folium
    from folium.plugins import Draw
    from streamlit_folium import st_folium
    HAS_MAP = True
except Exception:
    HAS_MAP = False

try:
    from shapely.geometry import Polygon, shape
    HAS_SHAPELY = True
except Exception:
    HAS_SHAPELY = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    HAS_PDF = True
except Exception:
    HAS_PDF = False


# ============================================================
# 1. CONFIGURATION
# ============================================================

APP_TITLE = "YouAgronoMe — Agritech Sénégal"
DB_PATH = Path("youagronome.db")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OFFICIAL_SOURCES = {
    "MASAE / DAPSA": {
        "url": "https://agriculture.gouv.sn/",
        "role": "Statistiques agricoles, campagnes, publications officielles",
        "niveau": "Institutionnel",
    },
    "ANACIM": {
        "url": "https://www.anacim.sn/",
        "role": "Météorologie, climat, alertes et services climatologiques",
        "niveau": "Institutionnel",
    },
    "ANCAR": {
        "url": "https://ancar.gouv.sn/",
        "role": "Conseil agricole et rural, E-conseil",
        "niveau": "Institutionnel",
    },
    "ISRA": {
        "url": "https://isra.sn/",
        "role": "Recherche agricole, sols, horticulture, fiches techniques",
        "niveau": "Recherche",
    },
    "SAED": {
        "url": "https://www.saed.sn/",
        "role": "Agriculture irriguée, vallée du fleuve, eau et conseil",
        "niveau": "Institutionnel",
    },
    "DPV": {
        "url": "https://www.dpvsenegal.sn/",
        "role": "Protection des végétaux et avertissements phytosanitaires",
        "niveau": "Institutionnel",
    },
    "CSE": {
        "url": "https://www.cse.sn/",
        "role": "Télédétection, biomasse, environnement et ressources naturelles",
        "niveau": "Institutionnel",
    },
    "Open-Meteo": {
        "url": "https://open-meteo.com/",
        "role": "Prévisions météo opérationnelles utilisées par l'application",
        "niveau": "Service météo numérique",
    },
}

# Coordonnées approximatives de référence pour l'interface.
# Elles servent à centrer la carte et à interroger un service météo.
REGIONS = {
    "Dakar": (14.7167, -17.4677),
    "Diourbel": (14.6565, -16.2342),
    "Fatick": (14.3390, -16.4160),
    "Kaffrine": (14.1059, -15.5508),
    "Kaolack": (14.1510, -16.0726),
    "Kédougou": (12.5605, -12.1747),
    "Kolda": (12.8939, -14.9414),
    "Louga": (15.6142, -16.2244),
    "Matam": (15.6559, -13.2554),
    "Saint-Louis": (16.0326, -16.4818),
    "Sédhiou": (12.7081, -15.5569),
    "Tambacounda": (13.7707, -13.6673),
    "Thiès": (14.7910, -16.9256),
    "Ziguinchor": (12.5833, -16.2719),
}

# Profils agro-écologiques : qualitatifs, pas des analyses de laboratoire.
AGROZONES = {
    "Vallée du Fleuve Sénégal": {
        "regions": ["Saint-Louis", "Matam"],
        "sols": ["alluviaux / argileux", "sablo-limoneux du Diéri", "zones salées/hydromorphes"],
        "cultures": ["Riz", "Oignon", "Tomate", "Maïs", "Sorgho", "Patate douce"],
        "enjeux": ["salinité", "drainage", "gestion de l'eau", "forte chaleur", "ravageurs"],
        "conseil": "Prioriser drainage, suivi de salinité, qualité de l'eau et calendrier d'irrigation.",
    },
    "Niayes & Littoral": {
        "regions": ["Dakar", "Thiès", "Louga"],
        "sols": ["sableux", "sablo-limoneux", "hydromorphes localisés"],
        "cultures": ["Oignon", "Pomme de terre", "Carotte", "Tomate", "Chou", "Pastèque", "Melon"],
        "enjeux": ["eau", "salinité", "vent", "nématodes", "pression maraîchère"],
        "conseil": "Renforcer matière organique, irrigation localisée, rotation et surveillance de la salinité.",
    },
    "Bassin arachidier": {
        "regions": ["Diourbel", "Fatick", "Kaolack", "Kaffrine"],
        "sols": ["sableux Dior", "ferrugineux tropicaux", "gravillonnaires localisés"],
        "cultures": ["Arachide", "Mil", "Niébé", "Maïs", "Sorgho", "Sésame", "Bissap"],
        "enjeux": ["pluviométrie", "matière organique", "érosion", "ravageurs", "fertilité"],
        "conseil": "Sécuriser la date de semis, conserver l'humidité et raisonner la fertilisation.",
    },
    "Casamance": {
        "regions": ["Ziguinchor", "Sédhiou", "Kolda"],
        "sols": ["ferrallitiques", "hydromorphes de bas-fond", "sablo-argileux"],
        "cultures": ["Riz", "Maïs", "Manioc", "Anacarde", "Sésame", "Arachide", "Maraîchage"],
        "enjeux": ["excès d'eau", "acidité", "maladies fongiques", "ravageurs", "conservation"],
        "conseil": "Adapter drainage, variété et calendrier à la forte saison des pluies et aux bas-fonds.",
    },
    "Sénégal Oriental": {
        "regions": ["Tambacounda", "Kédougou"],
        "sols": ["ferrugineux", "ferrallitiques", "cuirassés localisés"],
        "cultures": ["Maïs", "Sorgho", "Mil", "Sésame", "Coton", "Anacarde", "Fonio"],
        "enjeux": ["variabilité des pluies", "érosion", "ravageurs", "feux", "fertilité"],
        "conseil": "Conserver le sol, choisir des variétés adaptées et surveiller les risques climatiques.",
    },
}

CROPS = [
    "Riz", "Mil", "Sorgho", "Maïs", "Arachide", "Niébé", "Sésame", "Bissap",
    "Oignon", "Pomme de terre", "Tomate", "Gombo", "Chou", "Carotte", "Pastèque",
    "Melon", "Manioc", "Anacarde", "Coton", "Fonio"
]

STAGES = [
    "Préparation du sol", "Semis / plantation", "Levée / installation",
    "Croissance végétative", "Floraison", "Remplissage / tubérisation",
    "Maturation", "Récolte", "Post-récolte"
]

THEMES = [
    "sol et fertilité", "eau et irrigation", "météo et climat",
    "semis et implantation", "ravageurs et maladies", "adventices",
    "agroécologie et matière organique", "récolte et qualité",
    "stockage et post-récolte", "économie et organisation",
    "rotation et assolement", "sécurité et traçabilité"
]

# Modèles prudents : on évite de présenter une dose phytosanitaire comme universelle.
ADVICE_TEMPLATES = {
    "sol et fertilité": [
        "Faire une analyse de sol avant toute correction importante de fertilité. Pour {culture}, ajuster la stratégie à la texture, au pH, à la matière organique et aux résultats du laboratoire.",
        "Sur {culture}, privilégier un raisonnement par bilan des besoins et des apports plutôt qu'une dose fixe. Tenir compte des résidus, du précédent cultural et des apports organiques.",
        "Si le sol de la parcelle est très sableux, fractionner davantage les apports mobiles et protéger le sol par couverture et matière organique.",
    ],
    "eau et irrigation": [
        "Pour {culture} au stade {stage}, piloter l'irrigation à partir de l'humidité du sol, du stade de la culture, de la demande atmosphérique et de la qualité de l'eau.",
        "Éviter les irrigations automatiques sans contrôle : vérifier infiltration, drainage, état des racines et salinité si la parcelle est irriguée.",
        "En zone à forte demande évaporative, préférer des apports réguliers et maîtrisés plutôt que de longues irrigations espacées, selon le système installé.",
    ],
    "météo et climat": [
        "Avant une opération importante sur {culture}, consulter le bulletin ANACIM et adapter le calendrier aux pluies prévues, au vent et aux températures.",
        "En saison des pluies, prévoir une solution de repli si une pluie intense est annoncée : éviter de programmer un traitement ou un apport juste avant une pluie significative.",
        "Pour {culture}, conserver la date du semis, les pluies reçues et les incidents climatiques afin d'améliorer le diagnostic de fin de campagne.",
    ],
    "semis et implantation": [
        "Utiliser une semence de qualité et adaptée à la zone agro-écologique. Respecter la densité et la profondeur recommandées pour {culture}.",
        "Ne pas choisir la date de semis uniquement sur le calendrier : croiser humidité réelle du sol, prévisions et recommandations locales.",
        "Après levée de {culture}, vérifier rapidement la régularité de peuplement et corriger les manques lorsqu'une intervention reste agronomiquement possible.",
    ],
    "ravageurs et maladies": [
        "Surveiller régulièrement {culture} avant de traiter. Identifier l'organisme nuisible, son stade et son niveau d'attaque avant toute intervention.",
        "Privilégier la lutte intégrée : prévention, hygiène de parcelle, rotation, auxiliaires, variétés adaptées et traitement seulement lorsque nécessaire.",
        "Pour tout produit phytosanitaire, vérifier l'homologation en vigueur au Sénégal, l'étiquette, le délai avant récolte et les équipements de protection.",
    ],
    "adventices": [
        "Intervenir tôt sur les adventices de {culture}, lorsque leur concurrence est encore limitée et que l'opération est techniquement réalisable.",
        "Combiner rotation, couverture du sol, désherbage mécanique ou manuel et pratiques culturales adaptées plutôt que dépendre d'une seule méthode.",
        "Identifier les principales adventices de la parcelle avant de choisir une méthode de contrôle.",
    ],
    "agroécologie et matière organique": [
        "Augmenter progressivement la matière organique de la parcelle par des apports bien décomposés et disponibles localement, en tenant compte de leur qualité.",
        "Conserver les résidus sains et réduire l'érosion lorsque cela est compatible avec le système de production de {culture}.",
        "Associer légumineuses, rotations et couverture du sol lorsque le système de production le permet afin d'améliorer la résilience.",
    ],
    "récolte et qualité": [
        "Définir le bon stade de récolte de {culture} selon la destination du produit, l'humidité, la qualité visuelle et les exigences du marché.",
        "Éviter de mélanger des lots de qualité différente. Identifier les lots et noter date, parcelle, variété et conditions de récolte.",
        "Réduire les blessures mécaniques pendant la récolte et le transport, car elles accélèrent les pertes et les contaminations.",
    ],
    "stockage et post-récolte": [
        "Sécher {culture} jusqu'à un niveau compatible avec son mode de stockage et vérifier l'absence de réhumidification.",
        "Nettoyer et assainir les équipements de stockage avant l'entrée d'un nouveau lot.",
        "Surveiller régulièrement température, humidité, insectes et moisissures dans les stocks de {culture}.",
    ],
    "économie et organisation": [
        "Tenir un registre simple des dépenses de {culture} : semences, engrais, protection, eau, main-d'œuvre, transport et commercialisation.",
        "Comparer le coût par hectare, le rendement, le prix réellement obtenu et la marge, plutôt que le seul chiffre d'affaires.",
        "Avant un investissement, faire au minimum trois scénarios : prudent, central et défavorable.",
    ],
    "rotation et assolement": [
        "Éviter de reconduire systématiquement la même culture sur la même parcelle. Construire une rotation qui limite les maladies et diversifie les prélèvements nutritifs.",
        "Intégrer une légumineuse dans la rotation lorsque cela est agronomiquement adapté au système.",
        "Pour {culture}, tenir compte du précédent cultural avant de choisir la prochaine culture et les interventions.",
    ],
    "sécurité et traçabilité": [
        "Noter les interventions réalisées sur {culture} : date, produit ou intrant, dose réellement utilisée, opérateur et parcelle.",
        "Séparer les zones de stockage des produits phytosanitaires des denrées alimentaires et respecter les équipements de protection.",
        "Pour chaque lot, conserver l'origine de la semence, la parcelle, la date de récolte et les opérations post-récolte.",
    ],
}

# Ravageurs/maladies : catalogue de départ documenté par le contexte sénégalais.
# Aucun traitement chimique universel n'est imposé.
PESTS = [
    ("Chenille légionnaire d'automne", "Spodoptera frugiperda", ["Maïs", "Sorgho"], "Surveiller le cornet, les dégâts frais et les larves; privilégier la lutte intégrée."),
    ("Pucerons", "Aphididae", ["Arachide", "Niébé", "Gombo", "Oignon"], "Observer les jeunes pousses et la face inférieure des feuilles; favoriser les auxiliaires."),
    ("Mouche blanche", "Bemisia tabaci", ["Tomate", "Manioc", "Gombo"], "Surveiller adultes et nymphes; attention aux virus transmis."),
    ("Tuta absoluta", "Tuta absoluta", ["Tomate"], "Surveiller mines foliaires et fruits; utiliser piégeage et mesures de lutte intégrée."),
    ("Mouche des fruits", "Bactrocera spp.", ["Anacarde", "Mangue"], "Ramasser les fruits tombés et organiser le piégeage selon les recommandations locales."),
    ("Nématodes à galles", "Meloidogyne spp.", ["Tomate", "Gombo", "Carotte"], "Vérifier les racines et pratiquer rotation, matériel sain et mesures de réduction de l'inoculum."),
    ("Maladies foliaires du riz", "Complexe pathologique", ["Riz"], "Surveiller régulièrement les symptômes et solliciter le conseil technique avant traitement."),
    ("Maladies fongiques maraîchères", "Complexe pathologique", ["Oignon", "Tomate", "Pomme de terre", "Chou"], "Gérer humidité, aération, rotation et matériel végétal; confirmer le diagnostic."),
]

# ============================================================
# 2. BASE LOCALE SQLITE
# ============================================================

def db_conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db_conn()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        zone TEXT NOT NULL,
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS parcels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        region TEXT,
        commune TEXT,
        crop TEXT,
        area_ha REAL,
        perimeter_m REAL,
        geojson TEXT,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS diagnoses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parcel_id INTEGER,
        culture TEXT,
        observation TEXT,
        recommendation TEXT,
        created_at TEXT NOT NULL
    );
    """)
    con.commit()
    con.close()

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 150_000)
    return salt.hex() + ":" + digest.hex()

def verify_password(password: str, encoded: str) -> bool:
    try:
        salt_hex, digest_hex = encoded.split(":")
        salt = bytes.fromhex(salt_hex)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 150_000)
        return hmac.compare_digest(digest.hex(), digest_hex)
    except Exception:
        return False

def ensure_admin():
    admin_email = st.secrets.get("ADMIN_EMAIL", os.getenv("ADMIN_EMAIL", ""))
    admin_password = st.secrets.get("ADMIN_PASSWORD", os.getenv("ADMIN_PASSWORD", ""))
    if not admin_email or not admin_password:
        return
    con = db_conn()
    row = con.execute("SELECT id FROM users WHERE email=?", (admin_email.lower(),)).fetchone()
    if not row:
        con.execute(
            "INSERT INTO users(email,password_hash,name,role,zone,active,created_at) VALUES(?,?,?,?,?,?,?)",
            (admin_email.lower(), hash_password(admin_password), "Administrateur", "Administrateur", "National", 1, datetime.now().isoformat())
        )
        con.commit()
    con.close()

init_db()
ensure_admin()

# ============================================================
# 3. UTILITAIRES AGRONOMIQUES
# ============================================================

def find_zone(region: str) -> str:
    for zone, info in AGROZONES.items():
        if region in info["regions"]:
            return zone
    return "Sénégal — zone à préciser"

def haversine_m(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371000 * 2 * math.asin(math.sqrt(h))

def polygon_area_perimeter(coords: List[List[float]]) -> Tuple[float, float]:
    """Approximation robuste pour parcelles locales en projection equirectangulaire."""
    if len(coords) < 3:
        return 0.0, 0.0
    lat0 = math.radians(sum(p[0] for p in coords) / len(coords))
    R = 6371000.0
    xy = []
    for lat, lon in coords:
        x = R * math.radians(lon) * math.cos(lat0)
        y = R * math.radians(lat)
        xy.append((x, y))
    area = 0.0
    perimeter = 0.0
    for i, (x1, y1) in enumerate(xy):
        x2, y2 = xy[(i+1) % len(xy)]
        area += x1*y2 - x2*y1
        perimeter += math.hypot(x2-x1, y2-y1)
    return abs(area)/2/10000, perimeter

def centroid(coords: List[List[float]]) -> Tuple[float, float]:
    if not coords:
        return 0.0, 0.0
    return (
        sum(x[0] for x in coords)/len(coords),
        sum(x[1] for x in coords)/len(coords),
    )

def generate_advice_catalog() -> pd.DataFrame:
    """Génère >1000 fiches structurées à partir de règles explicites.
    Les fiches portent un niveau 'généré' : elles ne remplacent pas une fiche technique officielle.
    """
    rows = []
    idx = 1
    for crop in CROPS:
        for theme in THEMES:
            for stage in STAGES:
                template = ADVICE_TEMPLATES[theme][idx % len(ADVICE_TEMPLATES[theme])]
                for zone_name, zone in AGROZONES.items():
                    if crop not in zone["cultures"] and idx % 5 != 0:
                        continue
                    text = template.format(culture=crop, stage=stage)
                    rows.append({
                        "id": idx,
                        "Culture": crop,
                        "Thème": theme,
                        "Stade": stage,
                        "Zone": zone_name,
                        "Conseil": text,
                        "Priorité": "Élevée" if theme in ["météo et climat", "eau et irrigation", "ravageurs et maladies"] else "Normale",
                        "Statut": "Conseil généré à partir de règles",
                        "Validation requise": "Oui — conseiller local / fiche officielle",
                    })
                    idx += 1
    return pd.DataFrame(rows)

@st.cache_data
def advice_catalog():
    return generate_advice_catalog()

# ============================================================
# 4. MÉTÉO
# ============================================================

@st.cache_data(ttl=1800)
def get_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
            "timezone": "Africa/Dakar",
            "forecast_days": 7,
        }
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def weather_risk(weather: Optional[Dict[str, Any]]) -> List[str]:
    risks = []
    if not weather:
        return ["Météo non disponible : consulter le bulletin ANACIM."]
    cur = weather.get("current", {})
    if cur.get("wind_speed_10m", 0) >= 35:
        risks.append("Vent fort : reporter si possible les traitements foliaires.")
    if cur.get("relative_humidity_2m", 0) >= 85:
        risks.append("Humidité élevée : surveiller les maladies favorisées par l'humidité.")
    daily = weather.get("daily", {})
    rain = daily.get("precipitation_sum", [])[:3]
    if any((x or 0) >= 25 for x in rain):
        risks.append("Pluies importantes prévues : vérifier drainage et risque d'érosion.")
    if not risks:
        risks.append("Aucun signal météo automatique majeur détecté; vérifier néanmoins le bulletin ANACIM.")
    return risks

# ============================================================
# 5. DONNÉES TABLEAU DE BORD — OFFICIELLES UNIQUEMENT
# ============================================================

OFFICIAL_CAMPAIGN_2023_2024 = pd.DataFrame([
    {"Indicateur": "Production d'arachide", "Valeur": 1_670_000, "Unité": "tonnes", "Période": "2023-2024", "Source": "MASAE / DAPSA / ANSD"},
    {"Indicateur": "Production de riz", "Valeur": 1_400_000, "Unité": "tonnes", "Période": "2023-2024", "Source": "MASAE / DAPSA / ANSD"},
    {"Indicateur": "Superficie cultivée en arachide", "Valeur": 1_200_000, "Unité": "ha", "Période": "2023-2024", "Source": "MASAE / DAPSA / ANSD"},
    {"Indicateur": "Régions couvertes par l'EAA", "Valeur": 14, "Unité": "régions", "Période": "2023-2024", "Source": "MASAE / DAPSA / ANSD"},
    {"Indicateur": "Départements", "Valeur": 45, "Unité": "départements", "Période": "2023-2024", "Source": "MASAE / DAPSA / ANSD"},
])

def dashboard_source_status():
    return pd.DataFrame([
        {"Source": "MASAE / DAPSA", "Fonction": "Statistiques agricoles", "Statut": "Référence officielle", "URL": OFFICIAL_SOURCES["MASAE / DAPSA"]["url"]},
        {"Source": "ANACIM", "Fonction": "Météo / climat / alertes", "Statut": "Référence officielle", "URL": OFFICIAL_SOURCES["ANACIM"]["url"]},
        {"Source": "ANCAR", "Fonction": "Conseil agricole et rural", "Statut": "Référence officielle", "URL": OFFICIAL_SOURCES["ANCAR"]["url"]},
        {"Source": "ISRA", "Fonction": "Recherche / sols / itinéraires", "Statut": "Référence scientifique", "URL": OFFICIAL_SOURCES["ISRA"]["url"]},
        {"Source": "DPV", "Fonction": "Protection végétale", "Statut": "Référence phytosanitaire", "URL": OFFICIAL_SOURCES["DPV"]["url"]},
        {"Source": "CSE", "Fonction": "Télédétection / biomasse", "Statut": "Référence environnementale", "URL": OFFICIAL_SOURCES["CSE"]["url"]},
    ])

# ============================================================
# 6. INTERFACE
# ============================================================

st.set_page_config(page_title=APP_TITLE, page_icon="🌾", layout="wide")

st.markdown("""
<style>
:root { --green:#176b3a; --gold:#d6a62c; --soft:#f5f8f6; }
.block-container { padding-top: 1rem; max-width: 1500px; }
.hero {
    background: linear-gradient(135deg,#145a32,#0b2f1b);
    color:white; padding:28px; border-radius:18px; margin-bottom:18px;
    border-bottom:5px solid var(--gold);
}
.card {
    background:white; border:1px solid #dfe8e2; border-radius:14px;
    padding:16px; height:100%; box-shadow:0 2px 8px rgba(0,0,0,.04);
}
.section {
    color:#145a32; font-weight:800; font-size:1.15rem;
    border-left:5px solid #d6a62c; padding-left:10px; margin:18px 0 10px;
}
.small { color:#64748b; font-size:.85rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🇸🇳 YouAgronoMe</h1>
<p style="font-size:1.05rem">Plateforme intégrée de conseil agricole, consultance, cartographie parcellaire,
météo, sols, diagnostic et pilotage des exploitations au Sénégal.</p>
</div>
""", unsafe_allow_html=True)

menu = st.radio(
    "Navigation",
    ["🏠 Accueil", "📊 Tableau de bord", "💼 Consultance", "🌱 Conseil >1000 fiches", "📚 Documents & sources", "📞 Contact"],
    horizontal=True,
    label_visibility="collapsed",
)

# ============================================================
# 7. ACCUEIL
# ============================================================

if menu == "🏠 Accueil":
    st.markdown('<div class="section">Architecture de la nouvelle plateforme</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    modules = [
        ("📊", "Tableau de bord", "Indicateurs officiels séparés des données importées et des estimations."),
        ("🧪", "Consultance 360°", "Parcelle, sol, météo, eau, diagnostic, économie et rapport."),
        ("🗺️", "Cartographie précise", "Dessin GPS, import GeoJSON, surface, périmètre, centroïde et synchronisation."),
        ("🌱", "Conseil", "Catalogue dynamique de plus de 1000 fiches structurées et filtrables."),
    ]
    for c, (ico, title, desc) in zip(cols, modules):
        with c:
            st.markdown(f'<div class="card"><h3>{ico} {title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Principe de fiabilité</div>', unsafe_allow_html=True)
    st.info(
        "La version précédente mélangeait des chiffres présentés comme institutionnels avec des valeurs "
        "non vérifiables et appliquait des coefficients arbitraires à des productions historiques. "
        "Cette version supprime cette logique : chaque donnée est marquée par sa source, sa période et son statut."
    )

    st.markdown('<div class="section">Références nationales intégrées</div>', unsafe_allow_html=True)
    st.dataframe(dashboard_source_status(), use_container_width=True, hide_index=True)

# ============================================================
# 8. TABLEAU DE BORD
# ============================================================

elif menu == "📊 Tableau de bord":
    st.markdown('<div class="section">Observatoire agricole — données vérifiables</div>', unsafe_allow_html=True)
    st.caption("Les chiffres ci-dessous reprennent les indicateurs affichés par le MASAE pour la campagne 2023–2024. Ils ne sont pas extrapolés à 2026.")

    a,b,c,d,e = st.columns(5)
    vals = OFFICIAL_CAMPAIGN_2023_2024.set_index("Indicateur")
    a.metric("Arachide", "1,67 M t")
    b.metric("Riz", "1,40 M t")
    c.metric("Arachide", "1,20 M ha")
    d.metric("Régions EAA", "14")
    e.metric("Départements", "45")

    st.markdown('<div class="section">Données officielles disponibles</div>', unsafe_allow_html=True)
    st.dataframe(OFFICIAL_CAMPAIGN_2023_2024, use_container_width=True, hide_index=True)

    st.markdown('<div class="section">Importer un jeu de données DAPSA / projet / exploitation</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("CSV ou Excel", type=["csv", "xlsx"], key="dashboard_upload")
    if uploaded:
        try:
            if uploaded.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            st.success(f"{len(df):,} lignes chargées. Les données sont marquées comme 'importées' et ne sont pas confondues avec les données officielles.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Télécharger la copie normalisée CSV", csv_bytes, "donnees_normalisees.csv", "text/csv")
        except Exception as exc:
            st.error(f"Impossible de lire le fichier : {exc}")

    st.markdown('<div class="section">Suivi territorial</div>', unsafe_allow_html=True)
    region = st.selectbox("Région", ["Toutes"] + list(REGIONS.keys()))
    if region != "Toutes":
        lat, lon = REGIONS[region]
        zone = find_zone(region)
        st.info(f"**{region}** — zone agro-écologique : **{zone}**. Les informations de sol sont indicatives et ne remplacent pas une analyse de laboratoire.")
        weather = get_weather(lat, lon)
        if weather:
            cur = weather["current"]
            x1,x2,x3,x4 = st.columns(4)
            x1.metric("Température", f"{cur.get('temperature_2m','—')} °C")
            x2.metric("Humidité", f"{cur.get('relative_humidity_2m','—')} %")
            x3.metric("Vent", f"{cur.get('wind_speed_10m','—')} km/h")
            x4.metric("Pluie actuelle", f"{cur.get('precipitation','—')} mm")
            for risk in weather_risk(weather):
                st.warning(risk)
            daily = pd.DataFrame({
                "Date": weather["daily"]["time"],
                "T° max": weather["daily"]["temperature_2m_max"],
                "T° min": weather["daily"]["temperature_2m_min"],
                "Pluie mm": weather["daily"]["precipitation_sum"],
                "Probabilité pluie %": weather["daily"]["precipitation_probability_max"],
                "Vent max km/h": weather["daily"]["wind_speed_10m_max"],
            })
            st.dataframe(daily, use_container_width=True, hide_index=True)
        else:
            st.warning("Prévision opérationnelle indisponible. Consulter le bulletin ANACIM.")

# ============================================================
# 9. CONSULTANCE
# ============================================================

elif menu == "💼 Consultance":
    st.markdown('<div class="section">Bureau de consultance agronomique 360°</div>', unsafe_allow_html=True)

    c0,c1,c2,c3,c4 = st.tabs([
        "🗺️ Parcelle & GPS", "🌦️ Météo & climat", "🧪 Sol & fertilité",
        "🔬 Diagnostic", "💰 Économie & rapport"
    ])

    # ----- Parcelle / cartographie -----
    with c0:
        st.subheader("Délimitation précise et synchronisée")
        region = st.selectbox("Région de référence", list(REGIONS.keys()), key="parcel_region")
        commune = st.text_input("Commune / village", key="parcel_commune")
        parcel_name = st.text_input("Nom de la parcelle", value="Parcelle 01", key="parcel_name")
        crop = st.selectbox("Culture principale", CROPS, key="parcel_crop")

        lat0, lon0 = REGIONS[region]
        if "map_coords" not in st.session_state:
            st.session_state.map_coords = [
                [lat0, lon0],
                [lat0 + 0.0015, lon0],
                [lat0 + 0.0015, lon0 + 0.0015],
                [lat0, lon0 + 0.0015],
            ]

        colmap, coltools = st.columns([2.5, 1])
        with colmap:
            if HAS_MAP:
                m = folium.Map(location=[lat0, lon0], zoom_start=13, control_scale=True, tiles="OpenStreetMap")
                folium.LayerControl().add_to(m)
                Draw(
                    export=True,
                    draw_options={
                        "polyline": False, "rectangle": True, "circle": False,
                        "circlemarker": False, "marker": True, "polygon": True
                    },
                    edit_options={"edit": True, "remove": True}
                ).add_to(m)

                if len(st.session_state.map_coords) >= 3:
                    folium.Polygon(
                        st.session_state.map_coords,
                        color="#176b3a", fill=True, fill_opacity=.25,
                        popup=f"{parcel_name} — {crop}"
                    ).add_to(m)

                map_state = st_folium(m, height=560, width=None, key="consult_map")
                drawings = map_state.get("all_drawings") if map_state else None
                if drawings:
                    latest = drawings[-1]
                    geom = latest.get("geometry", {})
                    coords = geom.get("coordinates")
                    if geom.get("type") == "Polygon" and coords:
                        ring = coords[0]
                        st.session_state.map_coords = [[p[1], p[0]] for p in ring[:-1]]
                        st.rerun()
                    elif geom.get("type") == "Point" and coords:
                        st.session_state.map_center = [coords[1], coords[0]]
                        st.info(f"Point GPS synchronisé : {coords[1]:.6f}, {coords[0]:.6f}")
            else:
                st.warning("Folium/streamlit-folium n'est pas installé. Utilisez l'entrée manuelle ci-dessous.")

        with coltools:
            st.markdown("**Outils de précision**")
            st.caption("1. Dessinez le polygone. 2. L'application récupère les sommets. 3. Surface et périmètre sont recalculés.")
            coords_text = st.text_area(
                "Sommets manuels — une ligne `lat,lon`",
                value="\n".join(f"{a:.6f},{b:.6f}" for a,b in st.session_state.map_coords),
                height=170,
            )
            if st.button("🔄 Synchroniser les coordonnées", key="sync_coords"):
                try:
                    pts = []
                    for line in coords_text.splitlines():
                        if not line.strip():
                            continue
                        la, lo = [float(x.strip()) for x in line.split(",")[:2]]
                        pts.append([la, lo])
                    if len(pts) >= 3:
                        st.session_state.map_coords = pts
                        st.success("Coordonnées synchronisées.")
                        st.rerun()
                    else:
                        st.error("Il faut au moins 3 sommets.")
                except Exception:
                    st.error("Format invalide.")

            area_ha, perimeter_m = polygon_area_perimeter(st.session_state.map_coords)
            cen = centroid(st.session_state.map_coords)
            st.metric("Surface", f"{area_ha:.3f} ha")
            st.metric("Périmètre", f"{perimeter_m:.1f} m")
            st.metric("Centroïde", f"{cen[0]:.6f}, {cen[1]:.6f}")

            st.markdown("**Bordures / emprise**")
            if st.session_state.map_coords:
                lats = [p[0] for p in st.session_state.map_coords]
                lons = [p[1] for p in st.session_state.map_coords]
                st.write(f"Nord : {max(lats):.6f}")
                st.write(f"Sud : {min(lats):.6f}")
                st.write(f"Est : {max(lons):.6f}")
                st.write(f"Ouest : {min(lons):.6f}")

            if st.button("💾 Enregistrer la parcelle", type="primary"):
                con = db_conn()
                con.execute(
                    "INSERT INTO parcels(name,region,commune,crop,area_ha,perimeter_m,geojson,created_at) VALUES(?,?,?,?,?,?,?,?)",
                    (parcel_name, region, commune, crop, area_ha, perimeter_m, json.dumps(st.session_state.map_coords), datetime.now().isoformat())
                )
                con.commit()
                con.close()
                st.success("Parcelle enregistrée dans la base locale.")

        st.markdown("**Importer une emprise GeoJSON**")
        geo = st.file_uploader("GeoJSON", type=["geojson", "json"], key="geo_upload")
        if geo:
            try:
                obj = json.load(geo)
                feature = obj["features"][0] if obj.get("type") == "FeatureCollection" else obj
                geom = feature["geometry"]
                if geom["type"] == "Polygon":
                    ring = geom["coordinates"][0]
                    st.session_state.map_coords = [[p[1], p[0]] for p in ring[:-1]]
                    st.success("GeoJSON importé et synchronisé.")
                    st.rerun()
                else:
                    st.error("Le fichier doit contenir un polygone.")
            except Exception as exc:
                st.error(f"GeoJSON invalide : {exc}")

    # ----- Météo -----
    with c1:
        st.subheader("Météo, climat et risques")
        region_m = st.selectbox("Zone", list(REGIONS.keys()), key="weather_region")
        lat, lon = REGIONS[region_m]
        st.caption("Prévision opérationnelle : Open-Meteo. Pour les alertes et bulletins officiels, consulter ANACIM.")
        weather = get_weather(lat, lon)
        if weather:
            cur = weather["current"]
            x1,x2,x3,x4 = st.columns(4)
            x1.metric("Température", f"{cur.get('temperature_2m','—')} °C")
            x2.metric("Humidité", f"{cur.get('relative_humidity_2m','—')} %")
            x3.metric("Vent", f"{cur.get('wind_speed_10m','—')} km/h")
            x4.metric("Précipitation", f"{cur.get('precipitation','—')} mm")
            st.markdown("**Alertes agronomiques automatiques**")
            for risk in weather_risk(weather):
                st.warning(risk)
            st.dataframe(pd.DataFrame({
                "Date": weather["daily"]["time"],
                "Pluie (mm)": weather["daily"]["precipitation_sum"],
                "Prob. pluie (%)": weather["daily"]["precipitation_probability_max"],
                "T° max": weather["daily"]["temperature_2m_max"],
                "T° min": weather["daily"]["temperature_2m_min"],
                "Vent max": weather["daily"]["wind_speed_10m_max"],
            }), use_container_width=True, hide_index=True)
        else:
            st.error("Service météo indisponible.")
        st.link_button("🌦️ Ouvrir ANACIM", OFFICIAL_SOURCES["ANACIM"]["url"])

    # ----- Sol -----
    with c2:
        st.subheader("Diagnostic sol — raisonné, sans fausse précision")
        region_s = st.selectbox("Région", list(REGIONS.keys()), key="soil_region")
        zone = find_zone(region_s)
        info = AGROZONES.get(zone, {})
        st.info(f"Zone agro-écologique : **{zone}**\n\nSols typiques : {', '.join(info.get('sols', []))}.")
        st.warning("Ces profils sont indicatifs. Une recommandation de fumure doit être basée sur une analyse de sol et sur les références techniques de la culture.")

        pH = st.number_input("pH mesuré", 3.5, 10.0, 6.5, 0.1)
        mo = st.number_input("Matière organique (%)", 0.0, 10.0, 1.0, 0.1)
        n = st.number_input("N disponible (kg/ha)", 0.0, 500.0, 60.0, 5.0)
        p = st.number_input("P2O5 disponible (kg/ha)", 0.0, 500.0, 30.0, 5.0)
        k = st.number_input("K2O disponible (kg/ha)", 0.0, 500.0, 80.0, 5.0)
        texture = st.selectbox("Texture", ["Sableuse", "Sablo-limoneuse", "Limoneuse", "Sablo-argileuse", "Argileuse"])
        if st.button("Analyser le profil du sol"):
            alerts = []
            if pH < 5.5:
                alerts.append("pH acide : vérifier la culture, l'acidité échangeable et la recommandation de correction avant tout chaulage.")
            elif pH > 8.0:
                alerts.append("pH élevé : vérifier salinité/sodicité et qualité de l'eau si parcelle irriguée.")
            if mo < 1.0:
                alerts.append("Matière organique faible selon le seuil saisi : renforcer progressivement les apports organiques et la couverture du sol.")
            if texture == "Sableuse":
                alerts.append("Sol sableux : surveiller infiltration, lessivage et fractionnement des apports.")
            if not alerts:
                alerts.append("Pas d'alerte simple détectée. Interpréter les résultats avec un laboratoire et un conseiller.")
            for x in alerts:
                st.info(x)

        st.markdown("**Calcul arithmétique d'engrais — sans prescription de dose**")
        surface = st.number_input("Surface (ha)", 0.1, 10000.0, 1.0, 0.1, key="fert_surface")
        target_n = st.number_input("Besoin N à fournir (kg/ha)", 0.0, 500.0, 0.0, 5.0)
        product_n = st.number_input("Teneur N du produit (%)", 0.0, 100.0, 46.0, 0.1)
        qty = (target_n * surface) / (product_n/100) if product_n > 0 else 0
        st.metric("Quantité théorique du produit", f"{qty:.1f} kg")
        st.caption("Ce calcul convertit une dose de N déjà validée en quantité de produit. Il ne détermine pas la dose agronomique.")

    # ----- Diagnostic -----
    with c3:
        st.subheader("Diagnostic phytosanitaire raisonné")
        culture = st.selectbox("Culture", CROPS, key="diag_crop")
        symptom = st.text_area("Observations terrain", placeholder="Symptômes, organe atteint, âge des plants, répartition, humidité, présence d'insectes...")
        matching = [p for p in PESTS if culture in p[2]]
        if matching:
            dfp = pd.DataFrame(matching, columns=["Ennemi", "Nom scientifique", "Cultures", "Approche"])
            st.dataframe(dfp[["Ennemi","Nom scientifique","Approche"]], use_container_width=True, hide_index=True)
        if symptom:
            st.info("Diagnostic préliminaire : l'application ne remplace pas une confirmation de terrain/laboratoire. Photographier plusieurs plants représentatifs et documenter la parcelle.")
        st.link_button("🛡️ Ouvrir la DPV", OFFICIAL_SOURCES["DPV"]["url"])

    # ----- Economie + rapport -----
    with c4:
        st.subheader("Économie de la parcelle")
        surface_e = st.number_input("Surface (ha)", 0.1, 10000.0, 1.0, 0.1, key="eco_surface")
        rendement = st.number_input("Rendement attendu (t/ha)", 0.0, 100.0, 2.0, 0.1)
        prix = st.number_input("Prix de vente (FCFA/t)", 0.0, 10_000_000.0, 150_000.0, 5_000.0)
        cout = st.number_input("Charges variables (FCFA/ha)", 0.0, 10_000_000.0, 300_000.0, 10_000.0)
        ca = surface_e * rendement * prix
        charges = surface_e * cout
        marge = ca - charges
        a,b,c = st.columns(3)
        a.metric("Chiffre d'affaires", f"{ca:,.0f} FCFA")
        b.metric("Charges", f"{charges:,.0f} FCFA")
        c.metric("Marge", f"{marge:,.0f} FCFA")

        if HAS_PDF:
            if st.button("📄 Générer le rapport PDF"):
                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
                styles = getSampleStyleSheet()
                story = [
                    Paragraph("YouAgronoMe — Rapport de consultance agronomique", styles["Title"]),
                    Spacer(1, 12),
                    Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]),
                    Paragraph(f"Région : {region}", styles["Normal"]),
                    Paragraph(f"Culture : {crop}", styles["Normal"]),
                    Paragraph(f"Surface cartographiée : {area_ha:.3f} ha", styles["Normal"]),
                    Paragraph(f"Périmètre : {perimeter_m:.1f} m", styles["Normal"]),
                    Paragraph(f"Centroïde : {cen[0]:.6f}, {cen[1]:.6f}", styles["Normal"]),
                    Spacer(1, 12),
                    Paragraph("Sol", styles["Heading2"]),
                    Paragraph(f"pH={pH:.1f}; MO={mo:.1f}%; N={n:.1f}; P2O5={p:.1f}; K2O={k:.1f}; texture={texture}.", styles["Normal"]),
                    Spacer(1, 12),
                    Paragraph("Économie", styles["Heading2"]),
                    Paragraph(f"CA={ca:,.0f} FCFA; charges={charges:,.0f} FCFA; marge={marge:,.0f} FCFA.", styles["Normal"]),
                    Spacer(1, 12),
                    Paragraph("Réserve technique", styles["Heading2"]),
                    Paragraph("Les recommandations phytosanitaires, de fertilisation et d'irrigation doivent être validées avec les références officielles et les mesures de terrain disponibles.", styles["Normal"]),
                ]
                doc.build(story)
                buf.seek(0)
                st.download_button("📥 Télécharger le rapport", buf, f"rapport_youagronome_{date.today().isoformat()}.pdf", "application/pdf")
        else:
            st.warning("ReportLab n'est pas installé.")

# ============================================================
# 10. CONSEIL >1000
# ============================================================

elif menu == "🌱 Conseil >1000 fiches":
    st.markdown('<div class="section">Bibliothèque de conseils adaptés au Sénégal</div>', unsafe_allow_html=True)
    df = advice_catalog()
    st.success(f"📚 Catalogue généré : **{len(df):,} fiches structurées**.")

    st.warning(
        "Le catalogue dépasse 1000 conseils grâce à une combinaison explicite culture × thème × stade × zone. "
        "Les fiches marquées « Conseil généré » doivent être confrontées aux fiches techniques officielles "
        "et aux conditions réelles de la parcelle."
    )

    c1,c2,c3,c4 = st.columns(4)
    f_culture = c1.selectbox("Culture", ["Toutes"] + CROPS)
    f_theme = c2.selectbox("Thème", ["Tous"] + THEMES)
    f_stage = c3.selectbox("Stade", ["Tous"] + STAGES)
    f_zone = c4.selectbox("Zone", ["Toutes"] + list(AGROZONES.keys()))

    q = st.text_input("Recherche libre", placeholder="ex. oignon salinité irrigation, arachide semis, tomate Tuta...")
    result = df.copy()
    if f_culture != "Toutes": result = result[result["Culture"] == f_culture]
    if f_theme != "Tous": result = result[result["Thème"] == f_theme]
    if f_stage != "Tous": result = result[result["Stade"] == f_stage]
    if f_zone != "Toutes": result = result[result["Zone"] == f_zone]
    if q:
        mask = result.astype(str).apply(lambda row: row.str.contains(q, case=False, na=False).any(), axis=1)
        result = result[mask]

    st.write(f"**{len(result):,} conseil(s) trouvé(s)**")
    st.dataframe(result, use_container_width=True, hide_index=True)

    st.markdown('<div class="section">Fiches techniques et références</div>', unsafe_allow_html=True)
    refs = [
        ("ISRA — fiches horticoles actualisées", "Les travaux de l'ISRA/CDH ont porté notamment sur tomate, gombo, chou, oignon, courges, laitue, pomme de terre, bissap, pastèque, melon, poivron, piment, aubergine, haricot, betterave, navet, carotte, concombre, manioc et fraise.", OFFICIAL_SOURCES["ISRA"]["url"]),
        ("ANCAR — conseil agricole et rural", "Référence pour l'approche de conseil, l'accompagnement des producteurs et l'E-conseil.", OFFICIAL_SOURCES["ANCAR"]["url"]),
        ("ANACIM — climat et météo", "À consulter avant les décisions sensibles au calendrier pluviométrique.", OFFICIAL_SOURCES["ANACIM"]["url"]),
        ("DPV — protection des végétaux", "Bulletins phytosanitaires et référence pour la protection des cultures.", OFFICIAL_SOURCES["DPV"]["url"]),
    ]
    for title, desc, url in refs:
        with st.expander(title):
            st.write(desc)
            st.link_button("Ouvrir la source", url)

    st.download_button(
        "📥 Exporter le catalogue complet en CSV",
        df.to_csv(index=False).encode("utf-8"),
        "catalogue_conseils_senegal.csv",
        "text/csv"
    )

# ============================================================
# 11. DOCUMENTS
# ============================================================

elif menu == "📚 Documents & sources":
    st.markdown('<div class="section">Bibliothèque documentaire nationale</div>', unsafe_allow_html=True)
    st.info("Cette section centralise les portes d'entrée officielles. Les documents externes restent hébergés par leurs institutions.")

    for name, info in OFFICIAL_SOURCES.items():
        with st.container(border=True):
            a,b = st.columns([1,4])
            with a:
                st.markdown(f"### {name}")
            with b:
                st.write(info["role"])
                st.caption(f"Niveau : {info['niveau']}")
                st.link_button("📄 Ouvrir le site / document", info["url"])

    st.markdown('<div class="section">Documents de terrain</div>', unsafe_allow_html=True)
    local_docs = st.file_uploader(
        "Ajouter temporairement un PDF, CSV ou Excel de projet",
        type=["pdf", "csv", "xlsx"],
        accept_multiple_files=True,
        key="docs_upload"
    )
    if local_docs:
        for f in local_docs:
            st.success(f"Document chargé dans la session : {f.name} ({f.size/1024:.1f} Ko)")

# ============================================================
# 12. CONTACT
# ============================================================

elif menu == "📞 Contact":
    st.markdown('<div class="section">Contact & support</div>', unsafe_allow_html=True)
    st.write("**YouAgronoMe — Plateforme Agritech Sénégal**")
    st.write("Pour les partenariats, les projets de terrain, les données agricoles et les validations techniques, utiliser les coordonnées officielles des institutions partenaires ou votre canal de support.")
    st.link_button("🌾 MASAE", OFFICIAL_SOURCES["MASAE / DAPSA"]["url"])
    st.link_button("🌦️ ANACIM", OFFICIAL_SOURCES["ANACIM"]["url"])
    st.link_button("👩🏾‍🌾 ANCAR", OFFICIAL_SOURCES["ANCAR"]["url"])

st.markdown("---")
st.caption("YouAgronoMe — version 2 | Les données et conseils doivent conserver leur source, leur date et leur niveau de validation.")
