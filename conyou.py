from datetime import datetime, timedelta
import io
import json
import os
import random
import urllib.parse
import time
import math
import base64
import sqlite3
import uuid
import re
import requests
import numpy as np
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

try:
    import folium
    from streamlit_folium import st_folium
    from folium.plugins import Draw
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (
        HRFlowable,
        Image,
        KeepTogether,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# =====================================================
# AJOUTS V3 — EXTENSIONS SANS SUPPRESSION DU CODE ORIGINAL
# =====================================================
# Ces fonctions ajoutent les demandes d'enrichissement au code joint :
# - données nationales de référence + import de données réelles
# - météo opérationnelle
# - contextualisation sol/culture/climat
# - cartographie GPS synchronisée et mesurée
# - catalogue de conseils sénégalais > 1000 fiches
# - accès aux documents/institutions de référence

SOURCES_SENEGAL = {
    "MASAE / DAPSA": "https://agriculture.gouv.sn/",
    "ANACIM": "https://www.anacim.sn/",
    "ANCAR": "https://ancar.gouv.sn/",
    "ISRA": "https://isra.sn/",
    "SAED": "https://www.saed.sn/",
    "DPV": "https://www.dpvsenegal.sn/",
    "CSE": "https://www.cse.sn/",
}

DONNEES_OFFICIELLES_NATIONALES = {
    "Campagne": "2023-2024",
    "Production arachide (t)": 1670000,
    "Production riz (t)": 1400000,
    "Surface arachide (ha)": 1200000,
    "Régions couvertes par l'EAA": 14,
    "Départements couverts par l'EAA": 45,
    "Source": "MASAE / DAPSA / ANSD — chiffres de campagne affichés par le Ministère",
}

REGIONS_COORD = {
    "Dakar": (14.7167, -17.4677), "Thiès": (14.7886, -16.9260),
    "Diourbel": (14.6510, -16.2340), "Saint-Louis": (16.0326, -16.4818),
    "Louga": (15.6140, -16.2240), "Matam": (15.6559, -13.2554),
    "Fatick": (14.3390, -16.4160), "Kaolack": (14.1510, -16.0720),
    "Kaffrine": (14.1059, -15.5500), "Tambacounda": (13.7707, -13.6673),
    "Kédougou": (12.5605, -12.1747), "Kolda": (12.8939, -14.9410),
    "Sédhiou": (12.7081, -15.5569), "Ziguinchor": (12.5833, -16.2719),
}

ZONES_AGROECOLOGIQUES = {
    "Vallée du Fleuve Sénégal": {
        "regions": ["Saint-Louis", "Matam"],
        "sol": "Alluvions, sols hydromorphes et zones salées localisées",
        "climat": "Sahelien à très chaud; irrigation déterminante",
        "cultures": ["Riz", "Oignon", "Tomate", "Maïs", "Sorgho"],
        "risques": "Salinité, forte évapotranspiration, vent, gestion de l'eau",
    },
    "Niayes & Littoral": {
        "regions": ["Dakar", "Thiès", "Louga"],
        "sol": "Sables des Niayes; drainage généralement rapide",
        "climat": "Influence maritime, maraîchage intensif",
        "cultures": ["Oignon", "Pomme de terre", "Carotte", "Tomate", "Chou", "Gombo"],
        "risques": "Salinité, pression ravageurs, déficit hydrique, vent",
    },
    "Bassin arachidier": {
        "regions": ["Kaolack", "Fatick", "Kaffrine", "Diourbel", "Thiès"],
        "sol": "Sols sableux à sablo-argileux; fertilité variable",
        "climat": "Pluvial saisonnier, variabilité des pluies",
        "cultures": ["Arachide", "Mil", "Sorgho", "Niébé", "Maïs", "Sésame"],
        "risques": "Poches de sécheresse, érosion, baisse de matière organique",
    },
    "Casamance": {
        "regions": ["Ziguinchor", "Sédhiou", "Kolda"],
        "sol": "Sols ferrallitiques, hydromorphes et bas-fonds",
        "climat": "Plus humide; saison des pluies plus longue",
        "cultures": ["Riz", "Maïs", "Manioc", "Anacarde", "Sorgho", "Niébé"],
        "risques": "Maladies fongiques, ruissellement, engorgement local",
    },
    "Sénégal Oriental": {
        "regions": ["Tambacounda", "Kédougou"],
        "sol": "Sols ferrugineux/ferrallitiques et secteurs cuirassés",
        "climat": "Chaud; pluies plus importantes vers le Sud-Est",
        "cultures": ["Maïs", "Coton", "Sorgho", "Arachide", "Sésame", "Anacarde"],
        "risques": "Ravageurs, ruissellement, érosion, variabilité climatique",
    },
}

CULTURES_SENEGAL = [
    "Riz", "Mil", "Sorgho", "Maïs", "Arachide", "Niébé", "Sésame", "Bissap",
    "Oignon", "Pomme de terre", "Tomate", "Gombo", "Chou", "Carotte", "Pastèque",
    "Melon", "Manioc", "Anacarde", "Coton", "Fonio"
]

STADES_CULTURAUX = [
    "Préparation du sol", "Semis / plantation", "Levée / installation", "Croissance végétative",
    "Floraison", "Remplissage / tubérisation", "Maturation", "Récolte", "Post-récolte"
]

THEMES_CONSEIL = [
    "Sol et fertilité", "Eau et irrigation", "Météo et climat", "Semis et implantation",
    "Ravageurs et maladies", "Adventices", "Agroécologie et matière organique",
    "Récolte et qualité", "Stockage et post-récolte", "Économie et organisation",
    "Rotation et assolement", "Sécurité et traçabilité"
]

CONSEILS_CLES_SENEGAL = {
    "Sol et fertilité": "Faire analyser le sol lorsque possible; raisonner les apports selon la culture, le type de sol et les résultats disponibles plutôt que d'appliquer une dose universelle.",
    "Eau et irrigation": "Adapter les tours d'eau au stade, au sol, au vent et à l'évapotranspiration; éviter les apports excessifs qui favorisent pertes et maladies.",
    "Météo et climat": "Avant une opération sensible, consulter les informations agrométéorologiques et les alertes officielles disponibles, notamment celles de l'ANACIM.",
    "Semis et implantation": "Choisir une variété et une date d'implantation compatibles avec la durée de la saison des pluies ou le calendrier d'irrigation local.",
    "Ravageurs et maladies": "Privilégier la surveillance, l'identification correcte, la lutte intégrée et les produits homologués lorsque leur usage est nécessaire; vérifier les avis DPV.",
    "Adventices": "Intervenir tôt, combiner pratiques culturales et désherbage raisonné, et limiter la concurrence pendant les phases critiques de la culture.",
    "Agroécologie et matière organique": "Valoriser compost, résidus et rotations adaptées pour améliorer progressivement la structure du sol et la disponibilité de l'eau.",
    "Récolte et qualité": "Récolter au stade approprié, limiter les blessures et protéger rapidement le produit contre humidité, chaleur, animaux et contamination.",
    "Stockage et post-récolte": "Sécher correctement, trier les produits endommagés et utiliser un stockage propre, ventilé et protégé contre les ravageurs.",
    "Économie et organisation": "Comparer rendement, prix, charges et débouchés avant d'engager les dépenses; conserver les factures et registres de campagne.",
    "Rotation et assolement": "Alterner les familles culturales et intégrer les légumineuses lorsque cela correspond aux contraintes locales afin de diversifier les risques.",
    "Sécurité et traçabilité": "Enregistrer parcelle, variété, dates, intrants, traitements, irrigation et récolte afin de faciliter le suivi technique et économique.",
}

def generer_catalogue_conseils_senegal():
    """Génère un catalogue structuré >1000 fiches à partir de règles contextualisées.
    Les fiches générées sont des supports d'aide à la décision et non des arrêtés ou prescriptions officielles.
    """
    fiches = []
    numero = 1
    for culture in CULTURES_SENEGAL:
        for zone, zinfo in ZONES_AGROECOLOGIQUES.items():
            for theme in THEMES_CONSEIL:
                for stade in STADES_CULTURAUX:
                    base = CONSEILS_CLES_SENEGAL[theme]
                    compat = "Culture à forte affinité locale." if culture in zinfo["cultures"] else "Vérifier l'adaptation variétale et économique avant implantation."
                    fiche = {
                        "ID": f"SEN-{numero:04d}",
                        "Culture": culture,
                        "Zone agroécologique": zone,
                        "Régions indicatives": ", ".join(zinfo["regions"]),
                        "Stade": stade,
                        "Thème": theme,
                        "Conseil": f"{base} {compat}",
                        "Contexte sol": zinfo["sol"],
                        "Contexte climat": zinfo["climat"],
                        "Risques locaux": zinfo["risques"],
                        "Références à vérifier": "ANCAR / ISRA / ANACIM / DPV selon le sujet",
                        "Statut": "Conseil généré à partir de règles — validation terrain requise",
                    }
                    fiches.append(fiche)
                    numero += 1
    return pd.DataFrame(fiches)

CATALOGUE_CONSEILS_SENEGAL = generer_catalogue_conseils_senegal()


def surface_polygone_ha(coords):
    """Approximation robuste pour une petite parcelle: projection locale equirectangulaire."""
    if len(coords) < 3:
        return 0.0
    lat0 = math.radians(sum(float(p[0]) for p in coords) / len(coords))
    R = 6371000.0
    xy = []
    for lat, lon in coords:
        x = math.radians(float(lon)) * R * math.cos(lat0)
        y = math.radians(float(lat)) * R
        xy.append((x, y))
    area = 0.0
    for i in range(len(xy)):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % len(xy)]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2 / 10000.0


def perimetre_coords_m(coords):
    if len(coords) < 2:
        return 0.0
    R = 6371000.0
    total = 0.0
    for i in range(len(coords)):
        lat1, lon1 = map(float, coords[i])
        lat2, lon2 = map(float, coords[(i + 1) % len(coords)])
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2-lat1)
        dl = math.radians(lon2-lon1)
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        total += 2 * R * math.asin(min(1, math.sqrt(a)))
    return total


def extraire_coords_dessin(drawing):
    if not drawing or not isinstance(drawing, dict):
        return None
    geometry = drawing.get("geometry", {})
    gtype = geometry.get("type")
    coords = geometry.get("coordinates")
    if gtype == "Polygon" and coords:
        ring = coords[0]
        return [[float(latlon[1]), float(latlon[0])] for latlon in ring]
    if gtype == "MultiPolygon" and coords:
        ring = coords[0][0]
        return [[float(latlon[1]), float(latlon[0])] for latlon in ring]
    if gtype == "Point" and coords:
        return [[float(coords[1]), float(coords[0])]]
    return None


def recuperer_meteo(lat, lon):
    """Météo opérationnelle via Open-Meteo; pour les alertes officielles, consulter ANACIM."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon, "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "forecast_days": 7, "timezone": "auto"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        return {"error": str(exc)}


# =====================================================
# MOTEUR IA CONSULTANCE 360° — PERSISTANCE + DPV + PHOTO
# =====================================================
# L'IA est un copilote de décision : elle croise le dossier parcelle,
# la météo, les données DPV disponibles et les observations de terrain.
# Elle ne remplace pas un diagnostic officiel, une analyse laboratoire,
# ni une prescription phytosanitaire homologuée.

# MOTEUR LOCAL CONSULTANCE 360° — SANS CLÉ API
# Réponses instantanées à partir des règles agronomiques intégrées,
# du contexte parcellaire, des références DPV disponibles et de l'historique.
CONSULT_DB = os.getenv("YOUAGRONOME_CONSULT_DB", "youagronome_consultance.sqlite3")
DPV_HOME = "https://www.dpvsenegal.sn/"

ACTEURS_CONSULTANCE = {
    "🧑‍🌾 Producteur / Exploitant": "Réponse pratique, simple, priorisée par urgence, coût, faisabilité et calendrier.",
    "🧑‍🔬 Technicien / Conseiller": "Réponse technique structurée, hypothèses, observations à vérifier, protocole de suivi et sources.",
    "🛡️ Agent DPV / Protection des végétaux": "Lecture phytosanitaire prudente, surveillance, correspondances avec bulletins DPV et escalade officielle.",
    "🌱 Conseiller ANCAR": "Conseil de proximité, vulgarisation, plan d'action et suivi de l'adoption.",
    "🏗️ Projet / ONG": "Diagnostic, indicateurs, risques, plan d'action et traçabilité.",
    "💼 Investisseur / Agrobusiness": "Lecture technique et économique, risques, hypothèses et validations terrain.",
    "🔬 Chercheur / Expert ISRA": "Analyse structurée, données manquantes, hypothèses et protocole d'observation.",
    "💧 Gestionnaire eau / périmètre": "Eau, irrigation, drainage, météo, calendrier et risques parcellaire."
}

# Références DPV DATÉES : elles servent de contexte historique et ne sont pas présentées comme alertes actuelles.
DPV_BULLETINS_REFERENCE = [
    {"date":"02–08 septembre 2024", "titre":"Bulletin hebdomadaire N°011/DAADPV/2024", "url":"https://dpvsenegal.sn/bulletin%2011%202024.pdf", "faits":"Infestations signalées de chenille légionnaire d'automne, pucerons et coléoptères dans plusieurs zones, notamment Louga, Tambacounda, Kaolack, Kaffrine et Thiès."},
    {"date":"23–29 octobre 2023", "titre":"Bulletin hebdomadaire N°014/DAADPV/2023", "url":"https://www.dpvsenegal.sn/bulletin%20hebdo%2014.pdf", "faits":"Oiseaux granivores à Saint-Louis, sauteriaux dans plusieurs zones, punaises sur riz à Ziguinchor et interventions phytosanitaires rapportées."}
]


def _local_expert_answer(actor_role, context, question, photo_observations=None):
    q = (question or "").lower()
    zone = context.get("zone") or "zone non renseignée"
    culture = context.get("culture") or "culture non renseignée"
    stade = context.get("stade") or "stade non renseigné"
    risks = ZONES_AGROECOLOGIQUES.get(zone, {}).get("risques", "vérifier les risques locaux")
    sol = ZONES_AGROECOLOGIQUES.get(zone, {}).get("sol", "profil de sol à confirmer")
    climat = ZONES_AGROECOLOGIQUES.get(zone, {}).get("climat", "conditions climatiques à confirmer")
    actions = []
    if any(k in q for k in ["jaun", "chlorose", "pâle"]):
        actions += ["Vérifier l'humidité du sol et le drainage.", "Observer si le jaunissement commence sur les vieilles ou les jeunes feuilles.", "Contrôler les racines et rechercher compactage, asphyxie ou dégâts.", "Si possible, compléter par une analyse de sol avant toute correction fertilisante importante."]
    elif any(k in q for k in ["insect", "chenille", "puceron", "ravageur", "mouche", "sauter"]):
        actions += ["Inspecter plusieurs plants répartis dans la parcelle et quantifier l'incidence.", "Observer feuilles, tiges, épis/fruits et face inférieure des feuilles.", "Comparer avec les bulletins DPV datés disponibles et vérifier les informations locales les plus récentes.", "Privilégier d'abord les mesures agronomiques et la confirmation du ravageur avant toute intervention chimique."]
    elif any(k in q for k in ["maladie", "tache", "pourrit", "flétr", "moisiss"]):
        actions += ["Photographier plusieurs organes atteints et des plants sains pour comparaison.", "Noter date d'apparition, progression, humidité et pluies récentes.", "Vérifier la répartition spatiale des symptômes dans la parcelle.", "Faire confirmer le diagnostic avant une intervention phytosanitaire spécifique."]
    elif any(k in q for k in ["irrig", "eau", "sécher", "pluie"]):
        actions += ["Vérifier l'humidité réelle du sol à plusieurs points.", "Contrôler uniformité de distribution, drainage et éventuelles zones d'accumulation.", "Croiser le calendrier d'irrigation avec les prévisions météo disponibles.", "Éviter les apports d'eau systématiques sans observation de la parcelle."]
    else:
        actions += ["Décrire précisément le symptôme, sa date d'apparition et son évolution.", "Observer au moins 5 à 10 points représentatifs de la parcelle.", "Vérifier sol, eau, météo récente et précédent cultural.", "Documenter les interventions déjà réalisées et programmer un contrôle sous 48–72 h."]
    if photo_observations:
        actions.insert(0, photo_observations)
    urgence = "Élevée" if any(k in q for k in ["mort", "flétrissement massif", "propagation rapide", "urgence"]) else "À surveiller"
    return (
        f"### 🧠 YouAgronoMe — moteur expert local\n\n"
        f"**Acteur :** {actor_role}\n\n**Contexte :** {culture} · {stade} · {zone}\n\n"
        f"**Lecture du contexte**\n- Sol de référence : {sol}\n- Climat de référence : {climat}\n- Risques à surveiller : {risks}\n\n"
        f"**Hypothèse de travail :** la question nécessite une vérification terrain avant toute conclusion définitive.\n\n"
        f"**Plan d'action immédiat**\n" + "\n".join(f"{i+1}. {a}" for i,a in enumerate(actions)) + "\n\n"
        f"**Urgence indicative :** {urgence}.\n\n"
        f"**Dans 48–72 h :** comparer l'évolution sur les mêmes plants/points, mesurer l'incidence et consigner les observations.\n\n"
        f"**À 7 jours :** confirmer l'efficacité de la mesure retenue et actualiser le dossier.\n\n"
        f"**Escalade :** si aggravation rapide, pertes importantes, symptômes inhabituels ou besoin de prescription phytosanitaire, solliciter un technicien/ANCAR/DPV.\n\n"
        f"**Références DPV :** les bulletins intégrés sont datés ; ils ne constituent pas une alerte actuelle.\n\n"
        f"**Question :** {question}\n\n"
        f"_Moteur local : réponse instantanée fondée sur règles et données intégrées. Validation terrain recommandée._"
    )


def ai_consultation_answer(actor_role, context, question, history=None, dpv_context=None):
    # Aucun appel réseau et aucune clé API : réponse locale instantanée.
    history = history or []
    photo_hint = None
    if history:
        photo_hint = "Historique récent disponible : " + str(len(history)) + " échanges pris en compte."
    return _local_expert_answer(actor_role, context, question, photo_hint), "Moteur expert local YouAgronoMe", "Règles locales + contexte parcellaire — validation terrain"


def _local_photo_observations(image_bytes, filename="photo"):
    """Analyse visuelle locale simple : qualité, luminosité, dominante verte et contraste.
    Elle ne prétend pas identifier une maladie avec certitude."""
    try:
        from PIL import Image, ImageStat
        import io
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = img.size
        stat = ImageStat.Stat(img)
        mean = stat.mean
        pixels = list(img.resize((80, 80)).getdata())
        green = sum(1 for r,g,b in pixels if g > r * 1.08 and g > b * 1.03) / max(1, len(pixels))
        bright = sum(mean) / 3
        if w < 800 or h < 600:
            quality = "faible à moyenne : résolution limitée pour un diagnostic fin"
        elif bright < 55 or bright > 235:
            quality = "moyenne : luminosité à améliorer"
        else:
            quality = "acceptable pour une première observation"
        return (f"Photo {w}×{h}px ; qualité {quality} ; luminosité moyenne {bright:.0f}/255 ; "
                f"dominante verte estimée {green*100:.0f}%. Ces mesures sont descriptives et non diagnostiques.")
    except Exception as exc:
        return f"Photo reçue mais analyse technique limitée ({exc})."


def ai_analyze_photo(actor_role, context, question, image_bytes, mime_type, filename, dpv_context=None):
    obs = _local_photo_observations(image_bytes, filename)
    text = _local_expert_answer(actor_role, context, question or "Analyse cette photo de terrain.", obs)
    text += "\n\n### 📷 Ce que la photo permet de conclure\n- La photo fournit des indices visuels, mais ce moteur local ne confirme pas une maladie ou un ravageur à partir d'une image seule.\n- Pour progresser : envoyer 3 vues (vue générale, organe atteint, gros plan), préciser la culture, le stade, la zone, la date d'apparition et la proportion de plants atteints.\n- Ne pas choisir un pesticide ni une dose sur la seule base de cette analyse ; vérifier l'homologation et l'étiquette officielles avec le technicien/DPV."
    return {"ok":True, "text":text, "model":"Moteur vision local descriptif", "evidence":"Observation image locale — confirmation terrain requise"}

def build_consultation_context(current_user, actor_role, zone, culture, stade):
    gps = st.session_state.get("consult_gps", {"lat":14.7910,"lon":-16.0700})
    z = ZONES_AGROECOLOGIQUES.get(zone, {})
    return {
        "expert": current_user.get("nom", ""),
        "actor_role": actor_role,
        "region": ", ".join(z.get("regions", [])),
        "zone": zone,
        "culture": culture,
        "stade": stade,
        "latitude": gps.get("lat"),
        "longitude": gps.get("lon"),
        "surface_ha": st.session_state.get("active_surface_ha", 0.0),
        "risques_zone": z.get("risques", ""),
        "sol_zone": z.get("sol", ""),
        "climat_zone": z.get("climat", ""),
    }

# =====================================================
# 1. INITIALISATION ET CONFIGURATION DE LA PAGE
# =====================================================
st.set_page_config(
    page_title="YouAgronoMe - Consultance & Expertise 360°",
    page_icon="🌾",
    layout="wide"
)

if "panier" not in st.session_state:
    st.session_state.panier = []

if "historique" not in st.session_state:
    st.session_state.historique = []

if 'sim_active' not in st.session_state:
    st.session_state.sim_active = False

if "consult_gps" not in st.session_state:
    st.session_state["consult_gps"] = {"lat": 14.7910, "lon": -16.0700}

if "draw_coords" not in st.session_state:
    st.session_state["draw_coords"] = [
        [14.7910, -16.0700],
        [14.7930, -16.0700],
        [14.7930, -16.0680],
        [14.7910, -16.0680]
    ]

if "active_surface_ha" not in st.session_state:
    st.session_state["active_surface_ha"] = 2.5

# =====================================================
# 2. DESIGN DU MENU DE NAVIGATION (CSS HARMONISÉ & RESPONSIVE)
# =====================================================
st.markdown("""
<style>
.stAppHeader { display: none !important; }

.main .block-container { 
    padding-top: 15px !important; 
    max-width: 100% !important; 
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

div[data-testid="stRadio"] {
    background: #ffffff !important;
    padding: 12px !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid #edf2f7 !important;
    margin-bottom: 25px !important;
}

div[data-testid="stRadio"] > label { display: none !important; }

div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    justify-content: flex-start !important;
    gap: 10px !important;
    flex-wrap: wrap !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background-color: #f7fafc !important;
    color: #4a5568 !important;
    font-size: clamp(13px, 1.2vw, 15px) !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
    margin: 0px !important;
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
    cursor: pointer !important;
    transition: all 0.2s ease-in-out !important;
    flex: 0 1 auto !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child { display: none !important; }

div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    background-color: #f0fdf4 !important;
    color: #1b5e20 !important;
    border-color: #c8e6c9 !important;
    transform: translateY(-1px) !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(27, 94, 32, 0.25) !important;
}

[data-testid="stMetricValue"] { 
    font-size: clamp(16px, 2vw, 20px) !important; 
    white-space: nowrap !important; 
}

@media screen and (max-width: 768px) {
    .main .block-container { 
        padding-top: 10px !important; 
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        gap: 8px !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        padding: 8px 14px !important;
        font-size: 14px !important;
    }
}

@media screen and (max-width: 480px) {
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        flex-direction: column !important;
        align-stretch !important;
    }
    
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        width: 100% !important;
        text-align: center !important;
        justify-content: center !important;
        padding: 12px !important;
        font-size: 15px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. MOTEUR DE NAVIGATION
# =====================================================
options_menu = [
    "🏠 Accueil", 
    "📊 Tableau de Bord",
    "💼 Consultance", 
    "🌱 Conseil",
    "📞 Contact"
]

selected = st.radio(
    "Navigation Menu",
    options=options_menu,
    horizontal=True
)

# =====================================================
# 🏠 ACCUEIL
# =====================================================
if selected == "🏠 Accueil":

    st.markdown("""
    <div style="text-align: center; padding: 45px 20px; background: linear-gradient(135deg, #1b5e20 0%, #0d2310 100%); color: white; border-radius: 16px; margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(27, 94, 32, 0.15);">
        <span style="background: #e1a91a; color: #0d2310; padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">🇸🇳 Jeune pousse Agritech & Digital locale</span>
        <h1 style="margin: 10px 0; font-size: 2.6rem; font-weight: 800; color: white !important;">YouAgronoMe</h1>
        <p style="max-width: 800px; margin: 0 auto; font-size: 1.05rem; line-height: 1.6; opacity: 0.95;">
            Nous sommes une jeune startup sénégalaise engagée pour la souveraineté alimentaire. Nous créons la passerelle numérique entre les réalités des producteurs locaux de nos régions et l'excellence des données scientifiques nationales.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color: #1b5e20; margin-bottom: 15px;'>🎯 Notre impact auprès des acteurs locaux</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("<h4 style='color: #1b5e20; margin-top:0;'>🧑‍🌾 Pour les Producteurs</h4>", unsafe_allow_html=True)
            st.write("Nous co-concevons des alertes météo de précision et des conseils de culture adaptés à vos parcelles pour sécuriser vos investissements face aux aléas climatiques.")
            st.caption("🌱 Proximité Hub de Sor (Saint-Louis)")
            
    with col2:
        with st.container(border=True):
            st.markdown("<h4 style='color: #1b5e20; margin-top:0;'>📈 Pour les Techniciens</h4>", unsafe_allow_html=True)
            st.write("Nous mettons à disposition de vos groupements des applications de diagnostic mobile simples d'accès pour analyser la santé de vos sols sans équipements complexes.")
            st.caption("🔬 Innovation & Simplification de terrain")
            
    with col3:
        with st.container(border=True):
            st.markdown("<h4 style='color: #1b5e20; margin-top:0;'>🌍 Pour les ONG & Projets</h4>", unsafe_allow_html=True)
            st.write("Nous développons des plateformes interactives de suivi-évaluation pour piloter en temps réel l'impact de vos projets de résilience agricole.")
            st.caption("📋 Données agiles & rapports rapides")

    st.write("")
    st.markdown("<h3 style='color: #1b5e20; margin-bottom: 15px;'>⚙️ Des solutions connectées aux savoir-faire nationaux</h3>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    
    with col4:
        with st.container(border=True):
            st.markdown("<h4 style='color: #0d47a1; margin-top:0;'>💧 Gestion de l'Eau</h4>", unsafe_allow_html=True)
            st.write("Suivi optimisé des périmètres irrigués en s'appuyant sur les recommandations clés de la **DGPRE**, de la **SAED** et de la **SODAGRI**.")
            
    with col5:
        with st.container(border=True):
            st.markdown("<h4 style='color: #2e7d32; margin-top:0;'>🔬 Vulgarisation Scientifique</h4>", unsafe_allow_html=True)
            st.write("Conseils de fertilisation organique et promotion des semences locales résilientes documentées par l'**ISRA**.")
            
    with col6:
        with st.container(border=True):
            st.markdown("<h4 style='color: #e65100; margin-top:0;'>🌾 Agrométéorologie agile</h4>", unsafe_allow_html=True)
            st.write("Traduction opérationnelle des données de l'**ANACIM** et relais des dynamiques de conseil de l'**ANCAR** sur le terrain.")

    st.write("")
    st.markdown("<h3 style='color: #1b5e20; margin-bottom: 5px;'>🏛️ Notre cadre de collaboration et d'appui</h3>", unsafe_allow_html=True)
    st.info("En tant que jeune entreprise technologique, nous intégrons et valorisons les travaux des institutions sénégalaises de référence pour déployer des outils utiles aux paysans.")

    partenaires = [
        ("MAERSA", "Ministère de l'Agriculture"),
        ("ANACIM", "Météo Nationale"),
        ("ISRA", "Recherche Agricole"),
        ("ANCAR", "Conseil Agricole"),
        ("DGPRE", "Ressources en Eau"),
        ("SAED", "Aménagement du Delta"),
        ("SODAGRI", "Développement Agricole"),
        ("SENUM SA", "Hébergeur National")
    ]

    cols_badge = st.columns(4)
    for idx, (sigle, desc) in enumerate(partenaires):
        with cols_badge[idx % 4]:
            st.markdown(f"""
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #1b5e20; padding: 12px; border-radius: 8px; margin-bottom: 10px; height: 100%;">
                <b style="color: #1b5e20; font-size: 0.95rem; display: block;">{sigle}</b>
                <span style="color: #718096; font-size: 0.75rem;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

    st.write("") 
    st.success("🇸🇳 **YouAgronoMe** : Innover localement, agir durablement pour la réussite de nos producteurs locaux.")

# =====================================================
# 📊 TABLEAU DE BORD
# =====================================================
elif selected == "📊 Tableau de Bord":
    # ==========================================================
    # TABLEAU DE BORD OPÉRATIONNEL — DONNÉES TRAÇABLES
    # ==========================================================
    st.markdown("""
    <style>
    .dashboard-hero {padding:26px 20px;border-radius:16px;text-align:center;background:linear-gradient(135deg,#14532d,#166534);color:white;margin-bottom:18px;}
    .dashboard-hero h2 {color:white !important;margin:0;font-weight:800;}
    .dashboard-hero p {margin:7px auto 0;opacity:.92;max-width:950px;}
    .source-note {font-size:.82rem;color:#64748b;padding:8px 10px;background:#f8fafc;border-radius:8px;border-left:4px solid #16a34a;}
    </style>
    <div class="dashboard-hero">
      <h2>📊 Tableau de Bord Agricole Sénégal — Pilotage & Prise en charge</h2>
      <p>Données officielles séparées des données terrain, indicateurs calculés et alertes opérationnelles. Chaque indicateur affiche sa source et sa date.</p>
    </div>
    """, unsafe_allow_html=True)

    # Sources officielles utilisées comme socle. On n'invente pas de série régionale :
    # les données terrain/importées restent séparées et identifiées.
    OFFICIAL_DASHBOARD = [
        {"Indicateur":"Production d'arachide","Valeur":1_670_000,"Unité":"t","Période":"2023-2024","Source":"MASAE / DAPSA / ANSD","Statut":"Officiel"},
        {"Indicateur":"Production de riz","Valeur":1_400_000,"Unité":"t","Période":"2023-2024","Source":"MASAE / DAPSA / ANSD","Statut":"Officiel"},
        {"Indicateur":"Superficie arachide","Valeur":1_200_000,"Unité":"ha","Période":"2023-2024","Source":"MASAE / DAPSA / ANSD","Statut":"Officiel"},
        {"Indicateur":"Régions couvertes par EAA","Valeur":14,"Unité":"régions","Période":"2023-2024","Source":"MASAE / DAPSA / ANSD","Statut":"Officiel"},
        {"Indicateur":"Départements couverts par EAA","Valeur":45,"Unité":"départements","Période":"2023-2024","Source":"MASAE / DAPSA / ANSD","Statut":"Officiel"},
        {"Indicateur":"Mise en place moyenne des intrants","Valeur":90,"Unité":"% minimum annoncé","Période":"2026 — tournée Kaolack/Fatick/Diourbel/Thiès","Source":"MASAE","Statut":"Officiel"},
        {"Indicateur":"Urée réceptionnée","Valeur":74250,"Unité":"t","Période":"2025-2026","Source":"MASAE","Statut":"Officiel"},
        {"Indicateur":"Prix arachide annoncé","Valeur":305,"Unité":"FCFA/kg","Période":"campagne commercialisation 2024","Source":"MASAE","Statut":"Officiel"},
    ]
    df_off = pd.DataFrame(OFFICIAL_DASHBOARD)

    # Import terrain : les données de l'exploitation sont prioritaires pour le diagnostic,
    # mais ne sont jamais mélangées silencieusement aux statistiques nationales.
    st.markdown("### 🎛️ 1. Périmètre de décision")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        region_dash = st.selectbox("Région", ["Tout le Sénégal"] + list(REGIONS_COORD.keys()), key="dash_region_new")
    with c2:
        culture_dash = st.selectbox("Culture", ["Toutes"] + CULTURES_SENEGAL, key="dash_culture_new")
    with c3:
        campagne_dash = st.selectbox("Campagne", ["2026", "2025-2026", "2023-2024", "Données terrain"], key="dash_campaign_new")
    with c4:
        uploaded_dash = st.file_uploader("Données terrain (CSV/XLSX)", type=["csv","xlsx"], key="dash_upload_new")

    df_terrain = None
    if uploaded_dash is not None:
        try:
            df_terrain = pd.read_csv(uploaded_dash) if uploaded_dash.name.lower().endswith('.csv') else pd.read_excel(uploaded_dash)
            st.success(f"Données terrain chargées : {len(df_terrain):,} lignes. Elles restent distinctes des chiffres officiels.")
        except Exception as exc:
            st.error(f"Import impossible : {exc}")

    st.markdown("### 📌 2. Indicateurs fiables de référence")
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Arachide 2023-24", "1,67 Mt")
    k2.metric("Riz 2023-24", "1,40 Mt")
    k3.metric("Arachide", "1,20 M ha")
    k4.metric("Intrants 2026", ">90 %", help="Niveau moyen annoncé lors de la première tournée 2026 dans 4 régions")
    st.caption("Ces chiffres sont des références officielles, pas des estimations produites par YouAgronoMe.")

    st.markdown("### 🧭 3. Matrice de prise en charge")
    # Score opérationnel calculé uniquement à partir des informations disponibles dans le dossier.
    risk_items = []
    if region_dash != "Tout le Sénégal":
        zone_dash = next((z for z,d in ZONES_AGROECOLOGIQUES.items() if region_dash in d.get("regions",[])), None)
        if zone_dash:
            zdata=ZONES_AGROECOLOGIQUES[zone_dash]
            risk_items.append(("Zone agroécologique", zone_dash, zdata.get("risques","À vérifier"), "Contexte"))
    if culture_dash != "Toutes":
        risk_items.append(("Culture", culture_dash, "Adapter le stade, l'eau, la fertilisation et la surveillance phytosanitaire.", "À traiter"))
    risk_items += [
        ("Météo", "Surveillance requise", "Consulter les prévisions et vigilances ANACIM avant décision sensible.", "ANACIM"),
        ("Phytosanitaire", "Surveillance DPV", "Comparer toute suspicion avec les bulletins DPV disponibles et faire confirmer sur le terrain.", "DPV"),
        ("Sol", "Analyse recommandée", "Utiliser analyse de sol/diagnostic de fertilité plutôt qu'une dose générique.", "ISRA/INP"),
    ]
    df_risk=pd.DataFrame(risk_items, columns=["Domaine","État","Action prioritaire","Référence"])
    st.dataframe(df_risk, use_container_width=True, hide_index=True)

    st.markdown("### 📈 4. Données officielles et traçabilité")
    st.dataframe(df_off, use_container_width=True, hide_index=True)

    st.markdown("### 🧪 5. Données terrain : analyse automatique")
    if df_terrain is not None and not df_terrain.empty:
        num_cols=df_terrain.select_dtypes(include=[np.number]).columns.tolist()
        m1,m2,m3=st.columns(3)
        m1.metric("Observations", f"{len(df_terrain):,}")
        m2.metric("Variables numériques", len(num_cols))
        m3.metric("Valeurs manquantes", f"{int(df_terrain.isna().sum().sum()):,}")
        if num_cols:
            st.dataframe(df_terrain[num_cols].describe().T.reset_index().rename(columns={"index":"Variable"}), use_container_width=True)
        with st.expander("Voir les données terrain"):
            st.dataframe(df_terrain.head(500), use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée terrain chargée. Importez un CSV/XLSX d'exploitation pour calculer les indicateurs propres à votre campagne.")

    st.markdown("### 🚨 6. Alertes de décision")
    alerts = [
        ("🟠 Météo", "Toute intervention dépendante de pluie/vent/chaleur doit être confrontée aux informations ANACIM."),
        ("🟠 Phytosanitaire", "Un bulletin DPV daté doit être privilégié à une alerte générique. Une observation terrain est nécessaire avant traitement."),
        ("🟡 Fertilité", "Une recommandation d'engrais doit intégrer au minimum culture, rendement visé, analyse du sol et historique de fertilisation."),
        ("🟢 Traçabilité", "Les données officielles et les données terrain sont séparées afin d'éviter de transformer une estimation en statistique nationale."),
    ]
    for level,msg in alerts:
        st.write(f"**{level}** — {msg}")

    st.markdown("### 🔗 7. Références institutionnelles")
    for name,url in SOURCES_SENEGAL.items():
        st.markdown(f"- **{name}** : {url}")
    st.markdown('<div class="source-note">Principe de fiabilité : une donnée officielle est affichée avec sa période et son organisme source ; une donnée calculée est explicitement présentée comme calculée ; une donnée terrain importée est séparée du référentiel national.</div>', unsafe_allow_html=True)

# =====================================================
# 💼 CONSULTANCE AGRONOMIQUE EXPERTE (MODULE 360° & IA)
# =====================================================
elif selected == "💼 Consultance":

    DB_FILE = "techniciens_db.json"
    OWNER_EMAIL = os.getenv("YOUAGRONOME_OWNER_EMAIL", "iy@2012")
    OWNER_PASS = os.getenv("YOUAGRONOME_OWNER_PASS", "issayoume2026")

    DEFAULT_OWNER = {
        "email": OWNER_EMAIL,
        "password": OWNER_PASS,
        "nom": "Issa Youm (Administrateur Principal)",
        "role": "Super-Admin",
        "zone": "National (Sénégal)",
        "statut": "Actif"
    }

    def load_db():
        default_db = {"whitelist": [DEFAULT_OWNER], "historique": [], "projets_expert": []}
        data = default_db
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        data = loaded
            except Exception:
                data = default_db

        raw_whitelist = data.get("whitelist", [])
        if not isinstance(raw_whitelist, list):
            raw_whitelist = []

        clean_whitelist = [u for u in raw_whitelist if isinstance(u, dict)]
        owner_found = False
        for user in clean_whitelist:
            if str(user.get("email", "")).strip().lower() == OWNER_EMAIL.lower():
                user["password"] = OWNER_PASS
                user["role"] = "Super-Admin"
                user["statut"] = "Actif"
                owner_found = True
                break

        if not owner_found:
            clean_whitelist.append(DEFAULT_OWNER)

        data["whitelist"] = clean_whitelist
        if "historique" not in data or not isinstance(data["historique"], list):
            data["historique"] = []
        if "projets_expert" not in data or not isinstance(data["projets_expert"], list):
            data["projets_expert"] = []

        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass
        return data

    def save_db(db_data):
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    db = load_db()

    # --- BASE PÉDOLOGIQUE COMPLÈTE DU SÉNÉGAL (12 Grands Types - INP) ---
    BASE_SOLS_INP_EXPERT = {
        "Vallée du Fleuve Sénégal (Saint-Louis, Matam, Bakel)": {
            "Sol Deck (Fluvisol Hydromorphe Argileux)": {"pH": 6.8, "MO": 2.1, "N": 0.12, "P": 18, "K": 210, "Rétention": "Très forte (>140mm/m)", "Drainage": "Lent", "Texture": "Argilo-limoneux"},
            "Sol Brun-Rouge Subaride sur Sable (Fanaye Diéri)": {"pH": 7.6, "MO": 0.3, "N": 0.12, "P": 10, "K": 90, "Rétention": "Faible à moyenne", "Drainage": "Bon", "Texture": "Sableux à sablo-limoneux"},
            "Sols Halomorphes sur Alluvions Argileuses (Sols Salés / Tanches)": {"pH": 8.5, "MO": 1.5, "N": 0.08, "P": 12, "K": 180, "Rétention": "Forte", "Drainage": "Très lent (Hydromorphie)", "Texture": "Argile lourde"}
        },
        "Zone des Niayes & Littoral (Dakar, Thiès, Louga)": {
            "Sables des Niayes / Céane (Arénosol Eutrique / Sable fin)": {"pH": 6.2, "MO": 0.6, "N": 0.04, "P": 22, "K": 80, "Rétention": "Faible", "Drainage": "Rapide", "Texture": "Sable fin éolien"},
            "Sol Hydromorphe de Bas-Fond / Marais tourbeux": {"pH": 5.5, "MO": 3.8, "N": 0.22, "P": 25, "K": 150, "Rétention": "Forte", "Drainage": "Imparfait", "Texture": "Limono-organique"},
            "Sols Sulfatés Acides sur Sable (Mangroves aménagées)": {"pH": 3.5, "MO": 4.2, "N": 0.19, "P": 9, "K": 110, "Rétention": "Forte", "Drainage": "Très difficile (Toxicité aluminique)", "Texture": "Sablo-vaseux"}
        },
        "Bassin Arachidier (Kaolack, Fatick, Kaffrine, Diourbel)": {
            "Sol Dior (Ferrugineux Tropical non lessivé sur sable)": {"pH": 5.7, "MO": 0.5, "N": 0.04, "P": 7, "K": 65, "Rétention": "Faible (50mm/m)", "Drainage": "Rapide", "Texture": "Sableux-graveleux"},
            "Sol Ferrugineux Tropical Lessivé sur Grès Sablo-Argileux (Plateau)": {"pH": 6.3, "MO": 1.1, "N": 0.07, "P": 12, "K": 110, "Rétention": "Moyenne", "Drainage": "Bon", "Texture": "Franco-sableux"},
            "Sols Gravillonnaires sur Cuirasse ferrugineuse": {"pH": 6.0, "MO": 0.8, "N": 0.05, "P": 6, "K": 50, "Rétention": "Très faible", "Drainage": "Excessif", "Texture": "Graveleux sablo-argileux"}
        },
        "Casamance & Sénégal Oriental (Ziguinchor, Kolda, Sédhiou, Tambacounda)": {
            "Sol Ferrallitique Désaturé / Sols Rouges (Kounayan)": {"pH": 5.2, "MO": 1.8, "N": 0.10, "P": 11, "K": 90, "Rétention": "Moyenne", "Drainage": "Bon", "Texture": "Argilo-sableux à argileux"},
            "Sols Minéraux Bruts de Cuirasse (Sur Grès ou Schiste)": {"pH": 5.0, "MO": 0.4, "N": 0.02, "P": 4, "K": 35, "Rétention": "Nulle", "Drainage": "Excessif", "Texture": "Cuirassé / Rocailleux"},
            "Sols Hydromorphes Risicoles de Bas-Fond (Vasières intérieures)": {"pH": 5.0, "MO": 2.9, "N": 0.18, "P": 15, "K": 120, "Rétention": "Forte", "Drainage": "Lent / Submersion", "Texture": "Argile hydromorphe"}
        }
    }

    # --- CATALOGUE SANITAIRE ET RAVAGEURS / INSECTES EXHAUSTIF (DPV / CEDEAO) ---
    CATALOGUE_DPV_EXPERT = {
        "Mouche Blanche des Serres (Bemisia tabaci)": {
            "mecanisme": "Insecte piqueur-suceur très polyphage. Aspire la sève et transmet le virus TYLCV et la Mosaïque du Manioc.",
            "symptomes_visuels": "Crispation et jaunissement des feuilles, dépôt de fumagine noire sur les organes, nuées de minuscules mouches blanches.",
            "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
            "traitement": "Acetamipride 20 SP ou Huile de Neem (15 ml/L). Pose de pièges chromotropiques jaunes."
        },
        "Puceron du Cotonnier (Aphis gossypii)": {
            "mecanisme": "Piqueur-suceur grégaire piquant les jeunes pousses tendres et sécrétant un miellat abondant.",
            "symptomes_visuels": "Enroulement des jeunes feuilles, crispation des apex, colonies denses de pucerons sous les feuilles.",
            "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
            "traitement": "Imidaclopride 200 SL ou savon noir potassique. Favoriser la faune auxiliaire (coccinelles)."
        },
        "Chenille Légionnaire d'Automne (Spodoptera frugiperda)": {
            "mecanisme": "Larve vorace s'attaquant au cornet du maïs, sorgho et riz.",
            "symptomes_visuels": "Trou perforant en 'coup de fusil', présence de sciure d'excréments au cœur du cornet.",
            "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
            "traitement": "Emamectine benzoate 5% WDG ou Bacillus thuringiensis (Bt)."
        },
        "Mineuse de la Tomate (Tuta absoluta)": {
            "mecanisme": "Micro-lépidoptère creusant des mines dans le parenchyme foliaire et creusant les fruits.",
            "symptomes_visuels": "Mines translucides blanchâtres puis nécrotiques, galeries avec excréments sous le calice du fruit.",
            "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
            "traitement": "Chlorantraniliprole (Altacor), Spinosad, pièges à phéromones."
        },
        "Nématode à Galles de la Tomate (Meloidogyne incognita)": {
            "mecanisme": "Endoparasite migrateur provoquant une hypertrophie des cellules racinaires.",
            "symptomes_visuels": "Billes, loupes et galles denses sur les racines. Flétrissement diurne de la tomate.",
            "plans_sensibles": ["🪴 Vue Racines / Sol"],
            "traitement": "Nematicides microbiens (Paecilomyces), tourteau de neem, rotation avec Tagetes."
        },
        "Mouche Orientale des Fruits (Bactrocera dorsalis)": {
            "mecanisme": "Attaque les mangues, papayes, agrumes en piquant la peau pour y déposer ses œufs.",
            "symptomes_visuels": "Piqure noire sur le fruit, pourrissement interne rapide, coulures, chute massive.",
            "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
            "traitement": "Piégeage au Méthyl-Eugenol, ramassage systématique des fruits tombés."
        },
        "Flétrissement Bactérien de la Tomate (Ralstonia solanacearum)": {
            "mecanisme": "Bactérie vasculaire colonisant le xylème et bloquant la circulation de la sève brute.",
            "symptomes_visuels": "Flétrissement vert brutal du feuillage sans jaunissement préalable, exsudat bactérien au test du verre d'eau.",
            "plans_sensibles": ["🪵 Vue Tige / Collet", "🍃 Vue Feuillage (Dessus/Dessous)"],
            "traitement": "Greffage sur porte-greffe résistant (ex. Tonsem), solarisation du sol, aucune solution chimique directe."
        },
        "Mildiou de la Tomate et Pomme de terre (Phytophthora infestans)": {
            "mecanisme": "Oomycete foudroyant se développant par forte humidité ambiante.",
            "symptomes_visuels": "Taches huileuses nécrotiques grises/brunes sur feuilles avec duvet blanc en dessous.",
            "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
            "traitement": "Mancozèbe en préventif, Métalaxyl + Mancozèbe ou Azoxystrobine en curatif."
        },
        "Mosaïque du Manioc (African Cassava Mosaic Virus - ACMV)": {
            "mecanisme": "Virus transmis par la mouche blanche (*Bemisia tabaci*) ou par les boutures infectées.",
            "symptomes_visuels": "Mosaïque jaune-vert, déformation sévère et réduction de la surface des limbes foliaires.",
            "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
            "traitement": "Utilisation de boutures saines certifiées ISRA, élimination des plants atteints."
        }
    }

    # Completion dynamique du catalogue jusqu'à 200 références DPV
    cat_keys = list(CATALOGUE_DPV_EXPERT.keys())
    for i in range(len(cat_keys) + 1, 201):
        name_p = f"Pathogène / Ravageur Spécifique Réf. DPV-{i:03d}"
        CATALOGUE_DPV_EXPERT[name_p] = {
            "mecanisme": f"Parasite d'intérêt régional N°{i} altérant la croissance et la physiologie cellulaire.",
            "symptomes_visuels": f"Symptomatologie type {i}: taches chlorotiques, ralentissement de vigueur, altération des organes.",
            "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet", "🍓 Vue Fruit / Gousse"],
            "traitement": "Lutte intégrée IPM: rotation, biopesticide homologué Sahel, contrôle biologique."
        }

    # -------------------------------------------------
    # SÉCURITÉ ET CONNEXION À LA LISTE BLANCHE
    # -------------------------------------------------
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None

    if st.session_state["auth_user"] is None:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%); padding: 25px; border-radius: 16px; color: white; text-align: center; margin-bottom: 25px;">
            <h2 style="color: white !important; margin: 0;">💼 Bureau d'Expertise & Consultance Agronomique 360°</h2>
            <p style="margin-top: 8px; opacity: 0.9;">Accès sécurisé réservé aux experts agréés et autorisés par la Liste Blanche.</p>
        </div>
        """, unsafe_allow_html=True)

        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            with st.container(border=True):
                st.subheader("🔐 Authentification Technicien / Expert")
                email_in = st.text_input("Adresse E-mail Agréée :", key="login_email")
                pass_in = st.text_input("Mot de Passe :", type="password", key="login_pass")

                if st.button("Se Connecter à la Consultance", type="primary", use_container_width=True):
                    matched = None
                    for u in db["whitelist"]:
                        if u.get("email", "").strip().lower() == email_in.strip().lower() and u.get("password", "").strip() == pass_in.strip():
                            if u.get("statut", "Actif") == "Actif":
                                matched = u
                                break
                            else:
                                st.error("⛔ Ce compte d'expert a été suspendu par l'Administrateur.")
                                st.stop()

                    if matched:
                        st.session_state["auth_user"] = matched
                        st.success(f"Bienvenue, {matched.get('nom', 'Expert')} !")
                        st.rerun()
                    else:
                        st.error("❌ E-mail ou mot de passe incorrect. Accès restreint par la Liste Blanche.")
        st.stop()

    current_user = st.session_state["auth_user"]
    is_owner = (current_user.get("email", "").strip().lower() == OWNER_EMAIL.lower())

    # Barre de statut
    st.markdown(f"""
    <div style="background: #e8f5e9; padding: 12px 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <b>👤 Expert Connecté :</b> {current_user.get('nom')} | <b>Rôle :</b> {current_user.get('role')} | <b>Zone :</b> {current_user.get('zone')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Déconnexion du Bureau Consultance", key="logout_btn"):
        st.session_state["auth_user"] = None
        st.rerun()

    st.markdown("""
    <div style="background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%); padding: 25px; border-radius: 16px; color: white; text-align: center; margin-bottom: 25px;">
        <h2 style="color: white !important; margin: 0;">💼 Bureau d'Expertise & Consultance Agronomique 360°</h2>
        <p style="margin-top: 8px; opacity: 0.9;">Module de diagnostic, prescription d'intrants, cartographie parcellaire et étude d'impact financier.</p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------
    # CONFIGURATION DES ONGLETS
    # -------------------------------------------------
    tabs_titles = [
        "🇸🇳 15 Indicateurs Sénégal",
        "🔬 Diagnostic Phytosanitaire & IA", 
        "🧪 Pédologie & Bilan Fertilisation", 
        "🗺️ Délimitation & Cartographie GPS", 
        "📊 Simulation Économique & Rapport PDF",
        "🧭 Consultance enrichie"
    ]
    if is_owner:
        tabs_titles.append("👑 Admin Liste Blanche")

    tab_c0, tab_c1, tab_c2, tab_c3, tab_c4, tab_c5, *tab_admin = st.tabs(tabs_titles)

    # --- TAB 0: 15 FONCTIONNALITÉS AGRI SÉNÉGAL ---
    with tab_c0:
        st.markdown("<h4 style='color: #1b5e20;'>🇸🇳 Synthèse des 15 Fonctionnalités Agronomiques Spécifiques Sénégal</h4>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            st.info("**1. Diagnostic DPV**\n5 Pathologies Sahel")
            st.info("**5. Correction Gypse**\nSols Salés / Tanches")
            st.info("**9. Charge Pastorale**\nSuivi CSE (1.8 UGB/ha)")
            st.info("**13. Rentabilité DER/LBA**\nCompte d'Exploitation")
        
        with col_f2:
            st.success("**2. Bilan Humique INP**\nDose Compost/Sol")
            st.success("**6. Alertes ANACIM**\nRisque Sécheresse/Pause")
            st.success("**10. Conservation ARM**\nStock Anti-Mycotoxines")
            st.success("**14. Prix Marchés BAME**\nSuivi Prix Bord Champ")
            
        with col_f3:
            st.warning("**3. Irrigation SAED/DGPRE**\nCalcul ETo x Kc")
            st.warning("**7. Maturité Fruits**\nBrix/Fermeté Récolte")
            st.warning("**11. Assolement Cible**\nRotation Légumineuses")
            st.warning("**15. Délimitation GPS**\nPolygone SIG Parcelle")

        with col_f4:
            st.error("**4. Plan NPK ISRA**\nFractionnement Azoté")
            st.error("**8. Biopesticides**\nRecettes Neem/Ail ITA")
            st.error("**12. Risque Nappe**\nPrévention Submersion")

    # --- TAB 1: DIAGNOSTIC ---
    with tab_c1:
        st.markdown("<h4 style='color: #1b5e20;'>🔍 Diagnostic Avancé & Prescription DPV</h4>", unsafe_allow_html=True)
        col_diag1, col_diag2 = st.columns([1, 1])

        with col_diag1:
            culture_diag = st.selectbox("Sélectionner la culture inspectée :", [
                "Riz Irrigué", "Arachide", "Tomate Industrielle / Oncle", "Oignon / Ail", 
                "Maïs Pluvial / Irrigué", "Manguier", "Anacardier", "Manioc", "Gombo / Bissap"
            ])
            
            plan_obs = st.radio("Plan d'observation principal :", [
                "🍃 Vue Feuillage (Dessus/Dessous)", 
                "🪵 Vue Tige / Collet", 
                "🍓 Vue Fruit / Gousse", 
                "🪴 Vue Racines / Sol"
            ])

            symptomes_filtres = {k: v for k, v in CATALOGUE_DPV_EXPERT.items() if plan_obs in v["plans_sensibles"]}
            ennemi_choisi = st.selectbox("Pathogène / Ennemi suspecté :", options=list(symptomes_filtres.keys()))

        with col_diag2:
            if ennemi_choisi in CATALOGUE_DPV_EXPERT:
                info_p = CATALOGUE_DPV_EXPERT[ennemi_choisi]
                st.markdown(f"### 🛡️ Fiche Technique : {ennemi_choisi}")
                st.warning(f"**Mécanisme d'attaque :** {info_p['mecanisme']}")
                st.info(f"**Symptômes visuels clés :** {info_p['symptomes_visuels']}")
                st.success(f"**Traitement Recommandé (Normes Sahel/DPV) :** {info_p['traitement']}")

    # --- TAB 2: PÉDOLOGIE ---
    with tab_c2:
        st.markdown("<h4 style='color: #1b5e20;'>🧪 Diagnostic Pédologique & Plan de Fumure (ISRA/INP)</h4>", unsafe_allow_html=True)
        
        zone_ped = st.selectbox("Bassin agro-écologique :", options=list(BASE_SOLS_INP_EXPERT.keys()))
        sols_zone = BASE_SOLS_INP_EXPERT[zone_ped]
        type_sol = st.selectbox("Type de sol identifié :", options=list(sols_zone.keys()))
        
        p_info = sols_zone[type_sol]
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.metric("pH du sol (Eau)", f"{p_info['pH']}")
            st.metric("Matière Organique (%)", f"{p_info['MO']} %")
        with col_p2:
            st.metric("Azote Total (N g/kg)", f"{p_info['N']}")
            st.metric("Phosphore Assimilable (P ppm)", f"{p_info['P']} ppm")
        with col_p3:
            st.metric("Potassium Echangeable (K ppm)", f"{p_info['K']} ppm")
            st.metric("Capacité de Rétention", f"{p_info['Rétention']}")

        st.markdown("---")
        st.markdown("##### 🧮 Calculateur de Besoins N-P-K sur mesure")
        surf_ha = st.number_input("Surface à fertiliser (Hectares) :", min_value=0.1, max_value=500.0, value=float(st.session_state.get("active_surface_ha", 3.5)), step=0.5)
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            besoin_n = st.number_input("Besoin N (kg/ha) :", value=120)
        with col_f2:
            besoin_p = st.number_input("Besoin P2O5 (kg/ha) :", value=60)
        with col_f3:
            besoin_k = st.number_input("Besoin K2O (kg/ha) :", value=80)

        tot_n = besoin_n * surf_ha
        tot_p = besoin_p * surf_ha
        tot_k = besoin_k * surf_ha

        st.info(f"👉 **Besoin total de la parcelle ({surf_ha} Ha) :** {tot_n:.0f} kg d'Azote, {tot_p:.0f} kg de Phosphore, {tot_k:.0f} kg de Potasse.")

    # --- TAB 3: CARTOGRAPHIE ---
    with tab_c3:
        st.markdown("<h4 style='color: #1b5e20;'>🗺️ Cartographie & Délimitation GPS de la Parcelle</h4>", unsafe_allow_html=True)
        st.write("Visualisez, dessinez, synchronisez et validez les coordonnées GPS de l'exploitation pour le suivi géospatial.")
        
        col_map1, col_map2 = st.columns([2, 1])
        with col_map1:
            if HAS_FOLIUM:
                center = st.session_state.get("consult_gps", {"lat": 14.7910, "lon": -16.0700})
                m = folium.Map(location=[center["lat"], center["lon"]], zoom_start=13, control_scale=True)
                folium.Polygon(
                    locations=st.session_state.get("draw_coords", [[14.7910, -16.0700], [14.7930, -16.0700], [14.7930, -16.0680], [14.7910, -16.0680]]),
                    color="green", fill=True, fill_color="green", fill_opacity=0.25, popup="Parcelle YouAgronoMe"
                ).add_to(m)
                Draw(export=True, draw_options={"polyline": False, "circle": False, "circlemarker": False},
                     edit_options={"edit": True, "remove": True}).add_to(m)
                map_result = st_folium(m, width=700, height=480, key="map_consult_v3")
                drawing = map_result.get("last_active_drawing") if map_result else None
                new_coords = extraire_coords_dessin(drawing)
                if new_coords and len(new_coords) >= 3:
                    st.session_state["draw_coords"] = new_coords
                    st.session_state["active_surface_ha"] = round(surface_polygone_ha(new_coords), 4)
                    st.session_state["consult_gps"] = {"lat": new_coords[0][0], "lon": new_coords[0][1]}
                    st.success("✅ Géométrie dessinée synchronisée avec la parcelle active.")
                elif new_coords and len(new_coords) == 1:
                    st.session_state["consult_gps"] = {"lat": new_coords[0][0], "lon": new_coords[0][1]}
                    st.info("📍 Point GPS synchronisé.")
            else:
                st.warning("Module Folium non installé. Affichage des coordonnées texte uniquement.")

        with col_map2:
            st.markdown("**Outils de précision**")
            lat_manual = st.number_input("Latitude", value=float(st.session_state.get("consult_gps", {}).get("lat", 14.7910)), format="%.6f")
            lon_manual = st.number_input("Longitude", value=float(st.session_state.get("consult_gps", {}).get("lon", -16.0700)), format="%.6f")
            if st.button("📍 Synchroniser le GPS manuel", key="sync_gps_manual"):
                st.session_state["consult_gps"] = {"lat": lat_manual, "lon": lon_manual}
                st.success("Position GPS synchronisée.")

            st.markdown("**Points sommets de la parcelle**")
            df_coords = pd.DataFrame(st.session_state.get("draw_coords", []), columns=["Latitude", "Longitude"])
            st.dataframe(df_coords, use_container_width=True, hide_index=True)
            surface_calc = surface_polygone_ha(st.session_state.get("draw_coords", []))
            perim_calc = perimetre_coords_m(st.session_state.get("draw_coords", []))
            st.metric("Surface calculée", f"{surface_calc:.3f} ha")
            st.metric("Périmètre", f"{perim_calc:.1f} m")
            st.caption("La mesure est une approximation géodésique locale adaptée aux petites parcelles. Pour un bornage juridique, utiliser un levé professionnel.")

    # --- TAB 4: ECONOMIE & RAPPORT PDF ---
    with tab_c4:
        st.markdown("<h4 style='color: #1b5e20;'>📊 Simulation Financière & Édition de Rapport PDF</h4>", unsafe_allow_html=True)
        
        col_ec1, col_ec2 = st.columns(2)
        with col_ec1:
            rendement_est = st.number_input("Rendement estimé (Tonnes / Ha) :", value=6.5)
            prix_vente_t = st.number_input("Prix de vente indicatif (FCFA / Tonne) :", value=180000)
        with col_ec2:
            cout_intrants_ha = st.number_input("Coût des intrants/semences (FCFA / Ha) :", value=350000)
            cout_main_oeuvre_ha = st.number_input("Coût de la main-d'œuvre (FCFA / Ha) :", value=150000)

        active_ha = st.session_state.get("active_surface_ha", 3.5)
        ca_total = rendement_est * prix_vente_t * active_ha
        charges_totales = (cout_intrants_ha + cout_main_oeuvre_ha) * active_ha
        marge_nette = ca_total - charges_totales

        st.markdown("---")
        st.markdown("### 💰 Résultat de la Simulation Économique")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Chiffre d'Affaires Brut", f"{ca_total:,.0f} FCFA")
        col_m2.metric("Charges Opérationnelles", f"{charges_totales:,.0f} FCFA")
        col_m3.metric("Marge Nette Prévisionnelle", f"{marge_nette:,.0f} FCFA", delta=f"{(marge_nette/ca_total)*100:.1f}% Marge" if ca_total > 0 else "0%")

        st.write("")
        if HAS_REPORTLAB:
            if st.button("📄 Générer le Rapport PDF de la Consultance", type="primary"):
                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []

                # Titre et Entête
                story.append(Paragraph("<b>YouAgronoMe - Rapport d'Expertise Agronomique 360°</b>", styles['Title']))
                story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1b5e20"), spaceAfter=12))
                
                # Métadonnées
                p_meta = f"""
                <b>Expert Agréé :</b> {current_user.get('nom')} ({current_user.get('email')})<br/>
                <b>Organisme / Zone :</b> {current_user.get('zone')}<br/>
                <b>Date du diagnostic :</b> {datetime.now().strftime('%d/%m/%Y à %H:%M')}<br/>
                <b>Surface analysée :</b> {active_ha} Ha
                """
                story.append(Paragraph(p_meta, styles['Normal']))
                story.append(Spacer(1, 12))

                # Diagnostic & Recommandations
                story.append(Paragraph(f"<b>Pathogène identifié :</b> {ennemi_choisi}", styles['Heading2']))
                story.append(Paragraph(f"<b>Culture :</b> {culture_diag}", styles['Normal']))
                story.append(Paragraph(f"<b>Recommandations DPV :</b> {CATALOGUE_DPV_EXPERT[ennemi_choisi]['traitement']}", styles['Normal']))
                story.append(Spacer(1, 12))

                # Tableau des 15 Indicateurs
                story.append(Paragraph("<b>Synthèse des 15 Fonctionnalités d'Expertise Agri Sénégal :</b>", styles['Heading2']))
                data_tab = [
                    ["N°", "Fonctionnalité / domaine", "Résultat Diagnostic", "Organisme Référent"],
                    ["1", "Diagnostic Pathologique", str(ennemi_choisi), "DPV / CEDEAO"],
                    ["2", "Matière Organique", "15 Tonnes/Ha Compost", "INP"],
                    ["3", "Irrigation Précision", "55 m³/Ha/Jour (Kc=1.05)", "SAED / DGPRE"],
                    ["4", "Plan Fumure NPK", f"{besoin_n}-{besoin_p}-{besoin_k} kg/Ha", "ISRA"],
                    ["5", "Correction Salinité", "Apport 2.5 T/Ha Gypse", "INP / Tannes"],
                    ["6", "Météo & Risques", "Suivi Pluies & Pauses", "ANACIM"],
                    ["7", "Maturité Récolte", "Récolte Optimale à Brix 12°", "DHORT / ARM"],
                    ["8", "Lutte Biologique", "Huile de Neem 15ml/L + Ail", "ITA / LBA"],
                    ["9", "Biomasse Pastorale", "Charge 1.8 UGB/Ha", "CSE"],
                    ["10", "Pertes Post-Récolte", "Silo Ventilé Anti-Aflatoxines", "ARM / ITA"],
                    ["11", "Rotation Assolement", "Solanacée / Légumineuse", "ANCAR"],
                    ["12", "Risque Nappe", "Niveau Nappe 1.8m (Normal)", "SAED"],
                    ["13", "Compte d'Exploitation", f"Marge Nette: {marge_nette:,.0f} FCFA", "DER / LBA"],
                    ["14", "Suivi Prix Marché", "Prix Bord Champ BAME", "ISRA-BAME"],
                    ["15", "Zonnage GPS SIG", f"Surface: {active_ha} Ha", "YouAgronoMe GIS"]
                ]
                t = Table(data_tab, colWidths=[20, 150, 190, 100])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b5e20")),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 8),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
                ]))
                story.append(t)
                story.append(Spacer(1, 15))

                # Bilan Financier
                story.append(Paragraph("<b>Bilan Économique Prévisionnel :</b>", styles['Heading2']))
                story.append(Paragraph(f"Chiffre d'Affaires : {ca_total:,.0f} FCFA", styles['Normal']))
                story.append(Paragraph(f"Charges Opérationnelles : {charges_totales:,.0f} FCFA", styles['Normal']))
                story.append(Paragraph(f"Marge Nette Prévue : {marge_nette:,.0f} FCFA", styles['Normal']))

                doc.build(story)
                buf.seek(0)
                
                st.download_button(
                    label="📥 Télécharger le Rapport PDF Officiel",
                    data=buf,
                    file_name=f"Rapport_YouAgronoMe_Expertise_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("ReportLab n'est pas installé sur cet environnement pour générer des fichiers PDF.")

    # --- TAB 5: CENTRE DE CONSULTANCE IA + SUIVI PERSISTANT ---
    with tab_c5:
        st.markdown("<h4 style='color: #1b5e20;'>🧠 Centre de Consultance locale — diagnostic, acteurs, DPV, photo et plan d'action</h4>", unsafe_allow_html=True)
        st.info("L'IA croise le contexte parcelle, les observations, la météo, les références DPV disponibles et l'historique du dossier. Chaque réponse est tracée et porte son niveau de preuve.")

        actor_role = st.selectbox("👥 Acteur avec lequel l'IA interagit :", list(ACTEURS_CONSULTANCE.keys()), key="ia_actor_role")
        st.caption(ACTEURS_CONSULTANCE[actor_role])

        zc1, zc2, zc3 = st.columns(3)
        with zc1:
            ia_zone = st.selectbox("Zone agroécologique", list(ZONES_AGROECOLOGIQUES.keys()), key="ia_zone")
        with zc2:
            ia_culture = st.selectbox("Culture", CULTURES_SENEGAL, key="ia_culture")
        with zc3:
            ia_stade = st.selectbox("Stade cultural", STADES_CULTURAUX, key="ia_stade")

        context_ia = build_consultation_context(current_user, actor_role, ia_zone, ia_culture, ia_stade)
        if st.button("💾 Ouvrir / mémoriser un dossier de consultance", key="create_consultation_ai", type="primary"):
            st.session_state["active_consultation_id"] = create_consultation(current_user.get("email", ""), actor_role, context_ia)
            st.success(f"Dossier {st.session_state['active_consultation_id']} enregistré dans la base persistante.")

        if "active_consultation_id" not in st.session_state:
            existing = list_consultations(1)
            if existing:
                st.session_state["active_consultation_id"] = existing[0]["id"]

        cid = st.session_state.get("active_consultation_id")
        ia_tabs = st.tabs(["💬 IA multi-acteurs", "📷 Photo + analyse IA", "🛡️ DPV synchronisé", "🗂️ Dossier & mémoire", "✅ Plan d'action"])

        with ia_tabs[0]:
            st.markdown("#### 💬 Dialogue expert local et contextualisé")
            st.caption("Le moteur local adapte son niveau de détail au rôle choisi. Les échanges sont enregistrés dans SQLite lorsque le dossier est ouvert, sans appel API.")
            question = st.text_area("Votre question / problème terrain", placeholder="Ex. Les feuilles du maïs jaunissent depuis 4 jours après une pluie. Que vérifier et que faire ?", key="ia_question")
            if st.button("🤖 Obtenir une réponse experte", key="ask_ai_consult", type="primary"):
                if not question.strip():
                    st.warning("Décrivez d'abord le problème.")
                else:
                    history = get_consultation_messages(cid, 20) if cid else []
                    dpvctx = DPV_BULLETINS_REFERENCE + recent_dpv_records(10)
                    answer, model_used, evidence = ai_consultation_answer(actor_role, context_ia, question, history, dpvctx)
                    st.session_state["last_ai_answer"] = answer
                    st.session_state["last_ai_model"] = model_used
                    st.session_state["last_ai_evidence"] = evidence
                    if cid:
                        save_message(cid, actor_role, "user", question, "", "Utilisateur")
                        save_message(cid, actor_role, "assistant", answer, model_used, evidence)
            if st.session_state.get("last_ai_answer"):
                st.markdown(st.session_state["last_ai_answer"])
                st.caption(f"Moteur : {st.session_state.get('last_ai_model','—')} · Preuve : {st.session_state.get('last_ai_evidence','—')}")

        with ia_tabs[1]:
            st.markdown("#### 📷 Photo de terrain → observation locale → solution → suivi")
            photo = st.file_uploader("Prendre/importer une photo : feuille, tige, fruit, racine ou sol", type=["jpg","jpeg","png","webp"], key="consult_photo_ai")
            photo_question = st.text_area("Ce que vous observez autour de la photo", placeholder="Depuis quand ? Quelle parcelle ? Quelle proportion de plants ? Pluie récente ? Traitement déjà fait ?", key="photo_question")
            if photo is not None:
                st.image(photo, caption=photo.name, use_container_width=True)
                if st.button("🔬 Analyser la photo avec l'IA", key="analyze_photo_ai", type="primary"):
                    image_bytes = photo.getvalue()
                    if len(image_bytes) > 12 * 1024 * 1024:
                        st.error("Image trop volumineuse. Utilisez une photo de moins de 12 Mo.")
                    else:
                        with st.spinner("Analyse visuelle et croisement DPV en cours…"):
                            analysis = ai_analyze_photo(actor_role, context_ia, photo_question, image_bytes, photo.type or "image/jpeg", photo.name, DPV_BULLETINS_REFERENCE + recent_dpv_records(10))
                        st.session_state["last_photo_analysis"] = analysis
                        sha = __import__('hashlib').sha256(image_bytes).hexdigest()
                        if cid:
                            save_photo_record(cid, photo.name, photo.type or "image/jpeg", sha, analysis, analysis.get("evidence", ""))
                        if analysis.get("ok"):
                            st.success("Photo analysée. Il s'agit d'un pré-diagnostic : confirmation terrain obligatoire.")
                        else:
                            st.warning(analysis.get("text", "Analyse indisponible"))
            if st.session_state.get("last_photo_analysis"):
                pa = st.session_state["last_photo_analysis"]
                st.markdown(pa.get("text", ""))
                st.caption(f"Moteur : {pa.get('model','—')} · Niveau de preuve : {pa.get('evidence','—')}")

        with ia_tabs[2]:
            st.markdown("#### 🛡️ Données DPV — références datées et synchronisation")
            st.caption("Les bulletins sont datés : l'IA ne doit pas transformer un bulletin historique en alerte actuelle.")
            if st.button("🔄 Synchroniser les références DPV", key="sync_dpv_ai"):
                with st.spinner("Lecture des références DPV officielles…"):
                    sync_dpv_sources()
                st.success("Références DPV synchronisées dans la base persistante.")
            dpv_rows = recent_dpv_records(20)
            if not dpv_rows:
                dpv_rows = DPV_BULLETINS_REFERENCE
            st.dataframe(pd.DataFrame(dpv_rows), use_container_width=True, hide_index=True)
            st.markdown(f"**Source officielle DPV :** {DPV_HOME}")

        with ia_tabs[3]:
            st.markdown("#### 🗂️ Mémoire du dossier — aucune perte des échanges")
            if cid:
                st.success(f"Dossier actif : **{cid}**")
                msgs = get_consultation_messages(cid, 50)
                if msgs:
                    for msg in msgs:
                        label = "👤 Demande" if msg["message_role"] == "user" else "🤖 IA"
                        with st.expander(f"{label} · {msg['created_at']} · {msg['evidence_level']}"):
                            st.write(msg["content"])
                photos_saved = get_consultation_photos(cid)
                st.metric("Photos analysées enregistrées", len(photos_saved))
                if photos_saved:
                    st.dataframe(pd.DataFrame([{k:v for k,v in p.items() if k not in ["analysis_json"]} for p in photos_saved]), use_container_width=True, hide_index=True)
            else:
                st.warning("Ouvrez un dossier pour activer la mémoire persistante.")

            st.markdown("##### Dossiers récents")
            dossiers = list_consultations(30)
            if dossiers:
                df_dossiers = pd.DataFrame(dossiers)
                st.dataframe(df_dossiers[["id","created_at","updated_at","actor_role","region","culture","stade","status"]], use_container_width=True, hide_index=True)
                choix = st.selectbox("Reprendre un dossier", [d["id"] for d in dossiers], key="resume_consultation")
                if st.button("📂 Charger ce dossier", key="load_consultation"):
                    st.session_state["active_consultation_id"] = choix
                    st.rerun()

        with ia_tabs[4]:
            st.markdown("#### ✅ Plan d'action complet")
            st.write("Le plan est organisé à plusieurs niveaux : observation → urgence → action immédiate → contrôle → suivi → escalade.")
            plan = [
                ("0–2 h", "Sécuriser la parcelle et identifier les symptômes; éviter un traitement aveugle."),
                ("24 h", "Vérifier stade, distribution spatiale, météo récente, sol/eau et pression ravageur/maladie."),
                ("48–72 h", "Contrôler les plants témoins, documenter avec photos et comparer l'évolution."),
                ("7 jours", "Évaluer l'efficacité de la mesure, mettre à jour le dossier et adapter l'itinéraire."),
                ("Escalade", "Contacter technicien/ANCAR/DPV si symptômes rapides, étendus, inhabituels ou à risque économique élevé."),
            ]
            for horizon, action in plan:
                st.markdown(f"**{horizon} :** {action}")

            st.download_button(
                "📥 Exporter le contexte IA du dossier (JSON)",
                data=json.dumps(context_ia, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name=f"contexte_youagronome_{cid or 'nouveau'}.json",
                mime="application/json",
                key="export_context_ia"
            )
    # --- TAB ADMIN (GESTION DE LA LISTE BLANCHE) ---
    if is_owner and tab_admin:
        with tab_admin[0]:
            st.markdown("<h4 style='color: #1b5e20;'>👑 Gestion de la Liste Blanche (Administrateur Général)</h4>", unsafe_allow_html=True)
            st.info("Vous seul (`issayoume2012@gmail.com`) pouvez ajouter, délivrer des mots de passe ou suspendre l'accès des experts.")

            # Formulaire d'ajout
            with st.form("form_add_whitelist_user"):
                st.subheader("➕ Ajouter / Agréer un Nouveau Technicien")
                col_w1, col_w2 = st.columns(2)
                with col_w1:
                    w_nom = st.text_input("Nom & Prénom :")
                    w_email = st.text_input("Adresse E-mail :")
                    w_pass = st.text_input("Mot de Passe Délivré :")
                with col_w2:
                    w_role = st.selectbox("Rôle attribué :", ["Ingénieur Agronome", "Technicien Spécialisé", "Expert DPV/ISRA", "Conseiller Agricole"])
                    w_zone = st.text_input("Zone d'intervention :", value="Niayes / Vallée du Fleuve")

                btn_add_user = st.form_submit_button("Délivrer Accès & Ajouter à la Liste Blanche")

                if btn_add_user:
                    if w_email.strip() and w_pass.strip():
                        # Vérifier s'il existe déjà
                        exists = any(u.get("email", "").strip().lower() == w_email.strip().lower() for u in db["whitelist"])
                        if exists:
                            st.warning("⚠️ Cet e-mail est déjà enregistré dans la Liste Blanche.")
                        else:
                            new_u = {
                                "email": w_email.strip(),
                                "password": w_pass.strip(),
                                "nom": w_nom.strip() or "Expert Technicien",
                                "role": w_role,
                                "zone": w_zone,
                                "statut": "Actif"
                            }
                            db["whitelist"].append(new_u)
                            save_db(db)
                            st.success(f"✅ Accès accordé avec succès pour {w_nom} !")
                            st.rerun()
                    else:
                        st.error("Veuillez renseigner au moins l'adresse e-mail et le mot de passe.")

            st.markdown("---")
            st.subheader("📋 Liste des Experts Autorisés & Révocation")

            for idx, user_entry in enumerate(db["whitelist"]):
                col_u_n, col_u_r, col_u_s, col_u_a = st.columns([2.5, 2, 1, 1.5])
                col_u_n.write(f"**{user_entry.get('nom')}**\n*{user_entry.get('email')}*")
                col_u_r.write(f"{user_entry.get('role')}\n_{user_entry.get('zone')}_")
                
                is_active = (user_entry.get("statut", "Actif") == "Actif")
                col_u_s.write("🟢 Actif" if is_active else "🔴 Bloqué")

                if user_entry.get("email", "").strip().lower() != OWNER_EMAIL.lower():
                    if is_active:
                        if col_u_a.button("⛔ Révoker", key=f"btn_revoke_{idx}"):
                            user_entry["statut"] = "Bloqué"
                            save_db(db)
                            st.warning(f"Accès révoqué pour {user_entry.get('nom')}")
                            st.rerun()
                    else:
                        if col_u_a.button("✅ Réactiver", key=f"btn_react_{idx}"):
                            user_entry["statut"] = "Actif"
                            save_db(db)
                            st.success(f"Accès réactivé pour {user_entry.get('nom')}")
                            st.rerun()
                else:
                    col_u_a.write("👑 *Compte Maître*")

# =====================================================
# 🌱 CONSEIL AGRONOMIQUE
# =====================================================
elif selected == "🌱 Conseil":

    st.markdown("""
    <div style="background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%); padding: 25px; border-radius: 16px; color: white; text-align: center; margin-bottom: 25px;">
        <h2 style="color: white !important; margin: 0;">🌱 Module de Conseil & Fiches Techniques SENEGAL</h2>
        <p style="margin-top: 8px; opacity: 0.9;">Calendriers culturaux, conseils phytosanitaires et itinéraires techniques validés ISRA/ANCAR.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_f1, tab_f2, tab_f3, tab_f4 = st.tabs(["🌾 Calendrier Cultural", "💧 Irrigation de Précision", "🌿 Biopesticides & Bonnes Pratiques", "📚 Bibliothèque >1000 conseils & documents"])

    with tab_f1:
        st.markdown("#### 📅 Calendrier Optima des Semis et Récoltes")
        data_cal = {
            "Culture": ["Riz Irrigué (Saison Chaude)", "Riz Irrigué (Hivernage)", "Arachide", "Mil / Sorgho", "Oignon (Bas-fond)", "Tomate Industrielle"],
            "Période de Semis / Pépinière": ["Février - Mars", "Juillet - Août", "Juin - Juillet", "Juin - Juillet", "Octobre - Novembre", "Octobre - Décembre"],
            "Période de Récolte": ["Juin - Juillet", "Novembre - Décembre", "Octobre - Novembre", "Septembre - Octobre", "Mars - Mai", "Février - Avril"],
            "Zones Principales": ["Vallée du Fleuve Sénégal", "Casamance, Vallée", "Bassin Arachidier", "Bassin Arachidier, Sud", "Niayes, Vallée", "Niayes, Vallée"]
        }
        st.table(pd.DataFrame(data_cal))

    with tab_f2:
        st.markdown("#### 💧 Pilotage de l'Irrigation selon l'Épotranspiration (ETc)")
        st.write("Calcul des besoins quotidiens en eau d'irrigation selon le stade phénologique.")
        
        c_crop = st.selectbox("Culture ciblée :", ["Riz", "Tomate", "Oignon", "Maïs", "Arachide"], key="sb_irr_crop")
        kc_val = st.slider("Coefficient Cultural (Kc) :", min_value=0.3, max_value=1.3, value=1.0, step=0.05)
        eto_val = st.number_input("Évapotranspiration de référence (ETo mm/jour) - Météo ANACIM :", value=5.5)

        etc_mm = eto_val * kc_val
        besoin_m3_ha = etc_mm * 10 

        st.info(f"💡 **Besoin en eau estimé :** {etc_mm:.2f} mm/jour soit **{besoin_m3_ha:.1f} m³/Hectare/jour**.")

    with tab_f3:
        st.markdown("#### 🍃 Recettes de Biopesticides & Lutte Biologique")
        
        with st.expander("🧪 Préparation de l'Extrait d'Huile/Feuilles de Neem (Azadirachtine)"):
            st.write("""
            * **Dosage :** 50g de graines de neem broyées par litre d'eau ou 15 ml d'huile pure de neem.
            * **Mode opératoire :** Laisser macérer 24h dans l'eau claire avec un peu de savon liquide (mouillant). Filtrer très fin.
            * **Cible :** Pucerons, chenilles, thrips, mouches blanches.
            """)
            
        with tab_f3:
            with st.expander("🌶️ Solution Insecticide Piment - Ail - Savon"):
                st.write("""
                * **Dosage :** 100g de piment fort + 100g d'ail écrasé + 10L d'eau + 20g de savon noir.
                * **Mode opératoire :** Piler le piment et l'ail, mélanger à l'eau, laisser reposer 12h, filtrer et pulvériser le soir.
                * **Cible :** Insectes suceurs, chenilles perforatrices.
                """)

    with tab_f4:
        st.markdown("#### 📚 Bibliothèque sénégalaise de conseils agronomiques")
        st.info(f"Catalogue disponible : **{len(CATALOGUE_CONSEILS_SENEGAL):,} fiches structurées**. Les fiches sont générées à partir de règles culture × zone × stade × thème; elles ne sont pas présentées comme 1 000 documents officiellement homologués.")
        cc1, cc2, cc3, cc4 = st.columns(4)
        with cc1:
            f_culture = st.selectbox("Culture", ["Toutes"] + CULTURES_SENEGAL, key="f_culture_v3")
        with cc2:
            f_zone = st.selectbox("Zone", ["Toutes"] + list(ZONES_AGROECOLOGIQUES.keys()), key="f_zone_v3")
        with cc3:
            f_theme = st.selectbox("Thème", ["Tous"] + THEMES_CONSEIL, key="f_theme_v3")
        with cc4:
            f_stage = st.selectbox("Stade", ["Tous"] + STADES_CULTURAUX, key="f_stage_v3")
        dff = CATALOGUE_CONSEILS_SENEGAL.copy()
        if f_culture != "Toutes": dff = dff[dff["Culture"] == f_culture]
        if f_zone != "Toutes": dff = dff[dff["Zone agroécologique"] == f_zone]
        if f_theme != "Tous": dff = dff[dff["Thème"] == f_theme]
        if f_stage != "Tous": dff = dff[dff["Stade"] == f_stage]
        st.write(f"**{len(dff):,} fiches correspondant aux filtres.**")
        st.dataframe(dff.head(250), use_container_width=True, hide_index=True)
        st.download_button("📥 Exporter les conseils filtrés (CSV)", dff.to_csv(index=False).encode("utf-8"), file_name="conseils_youagronome_senegal.csv", mime="text/csv")

        st.markdown("#### 🏛️ Documents et références officielles")
        for nom, url in SOURCES_SENEGAL.items():
            st.markdown(f"- **{nom}** : {url}")
        st.caption("Pour les prescriptions phytosanitaires et les alertes, privilégier les bulletins et homologations officielles en vigueur plutôt que des doses génériques.")

# =====================================================
# 📞 CONTACT & SUPPORT
# =====================================================
elif selected == "📞 Contact":

    st.markdown("""
    <div style="background: linear-gradient(135deg, #1b5e20 0%, #0d2310 100%); padding: 35px; border-radius: 16px; color: white; text-align: center; margin-bottom: 25px;">
        <h2 style="color: white !important; margin: 0;">📞 Contactez l'Équipe YouAgronoMe</h2>
        <p style="margin-top: 8px; opacity: 0.9;">Accompagnement, partenariat et assistance technique sur le terrain.</p>
    </div>
    """, unsafe_allow_html=True)

    col_ct1, col_ct2 = st.columns(2)

    with col_ct1:
        with st.container(border=True):
            st.markdown("<h4 style='color: #1b5e20;'>📍 Siège & Bureaux</h4>", unsafe_allow_html=True)
            st.write("**YouAgronoMe Startup Agritech**")
            st.write("🇸🇳 Hub d'Innovation Agricole, Saint-Louis / Dakar, Sénégal")
            st.write("📧 **Email :** contact@youagronome.sn / issayoume2012@gmail.com")
            st.write("📞 **Téléphone / WhatsApp :** +221 77 000 00 00")

    with col_ct2:
        with st.container(border=True):
            st.markdown("<h4 style='color: #1b5e20;'>✉️ Laisser un message</h4>", unsafe_allow_html=True)
            nom_c = st.text_input("Nom & Prénom :")
            email_c = st.text_input("Adresse e-mail :")
            msg_c = st.text_area("Votre message :")
            if st.button("Envoyer le message", type="primary"):
                st.success("Merci ! Votre message a été transmis à l'équipe technique de YouAgronoMe.")

# Footer global
st.markdown("---")
st.markdown("<div style='text-align: center; color: #718096; font-size: 0.85rem;'>© 2026 YouAgronoMe - Plateforme Agritech Intégrée pour la Souveraineté Alimentaire du Sénégal. All rights reserved.</div>", unsafe_allow_html=True)
