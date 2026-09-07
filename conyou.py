# -*- coding: utf-8 -*-
"""
YouAgronoMe — HUB Analyse & Consultance 360°
Refonte complète de l'architecture.

Architecture unique :
1) 🌍 TERRAIN & DONNÉES
2) 🗺️ SIG & DIAGNOSTIC
3) 🤖 IA & DÉCISION
4) 💼 CONSULTANCE & PILOTAGE

Principe central :
Dossier -> Parcelle -> Contexte synchronisé -> Analyses -> Décision -> Mission -> Rapport

Aucune ancienne navigation radio n'est conservée.
Les données SIG, terrain, analyses, IA, économie et rapports utilisent le même
contexte actif et une base SQLite persistante.
"""
from datetime import datetime, timedelta
import io
import json
import math
import os
import hashlib
import sqlite3
import uuid

import pandas as pd
import numpy as np
import streamlit as st
import requests

try:
    import folium
    from folium.plugins import Draw
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except Exception:
    HAS_FOLIUM = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    HAS_REPORTLAB = True
except Exception:
    HAS_REPORTLAB = False


# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="YouAgronoMe — HUB Analyse 360°",
    page_icon="🌾",
    layout="wide",
)

DB_FILE = os.getenv("YOUAGRONOME_HUB_DB", "youagronome_hub.sqlite3")
OWNER_EMAIL = os.getenv("YOUAGRONOME_OWNER_EMAIL", "iy@2012")
OWNER_PASS = os.getenv("YOUAGRONOME_OWNER_PASS", "issayoume2026")

SOURCES = {
    "ANACIM": "https://www.anacim.sn/",
    "DPV": "https://www.dpvsenegal.sn/",
    "ANCAR": "https://ancar.gouv.sn/",
    "ISRA": "https://isra.sn/",
    "SAED": "https://www.saed.sn/",
    "CSE": "https://www.cse.sn/",
    "Ministère Agriculture": "https://agriculture.gouv.sn/",
}

REGIONS_COORD = {
    "Dakar": (14.7167, -17.4677),
    "Thiès": (14.7886, -16.9260),
    "Diourbel": (14.6510, -16.2340),
    "Saint-Louis": (16.0326, -16.4818),
    "Louga": (15.6140, -16.2240),
    "Matam": (15.6559, -13.2554),
    "Fatick": (14.3390, -16.4160),
    "Kaolack": (14.1510, -16.0720),
    "Kaffrine": (14.1059, -15.5500),
    "Tambacounda": (13.7707, -13.6673),
    "Kédougou": (12.5605, -12.1747),
    "Kolda": (12.8939, -14.9410),
    "Sédhiou": (12.7081, -15.5569),
    "Ziguinchor": (12.5833, -16.2719),
}

CULTURES = [
    "Riz", "Mil", "Sorgho", "Maïs", "Arachide", "Niébé", "Sésame",
    "Bissap", "Oignon", "Pomme de terre", "Tomate", "Gombo", "Chou",
    "Carotte", "Pastèque", "Melon", "Manioc", "Anacarde", "Coton", "Fonio"
]

STADES = [
    "Préparation du sol", "Semis / plantation", "Levée / installation",
    "Croissance végétative", "Floraison", "Remplissage / tubérisation",
    "Maturation", "Récolte", "Post-récolte"
]

AGROZONES = {
    "Vallée du Fleuve Sénégal": {
        "regions": ["Saint-Louis", "Matam"],
        "sol": "Alluvions, sols hydromorphes et zones salées localisées",
        "climat": "Sahélien à très chaud; irrigation déterminante",
        "risques": "Salinité, forte évapotranspiration, vent, gestion de l'eau",
    },
    "Niayes & Littoral": {
        "regions": ["Dakar", "Thiès", "Louga"],
        "sol": "Sables des Niayes; drainage généralement rapide",
        "climat": "Influence maritime, maraîchage intensif",
        "risques": "Salinité, pression ravageurs, déficit hydrique, vent",
    },
    "Bassin arachidier": {
        "regions": ["Kaolack", "Fatick", "Kaffrine", "Diourbel", "Thiès"],
        "sol": "Sols sableux à sablo-argileux; fertilité variable",
        "climat": "Pluvial saisonnier, variabilité des pluies",
        "risques": "Poches de sécheresse, érosion, baisse de matière organique",
    },
    "Casamance": {
        "regions": ["Ziguinchor", "Sédhiou", "Kolda"],
        "sol": "Sols ferrallitiques, hydromorphes et bas-fonds",
        "climat": "Plus humide; saison des pluies plus longue",
        "risques": "Maladies fongiques, ruissellement, engorgement local",
    },
    "Sénégal Oriental": {
        "regions": ["Tambacounda", "Kédougou"],
        "sol": "Sols ferrugineux/ferrallitiques et secteurs cuirassés",
        "climat": "Chaud; pluies plus importantes vers le Sud-Est",
        "risques": "Ravageurs, ruissellement, érosion, variabilité climatique",
    },
}

ACTEURS = {
    "Producteur / Exploitant": "Décisions pratiques, coût, urgence et faisabilité.",
    "Technicien / Conseiller": "Analyse technique, hypothèses, contrôles et suivi.",
    "Agent protection végétale": "Surveillance phytosanitaire prudente et escalade officielle.",
    "Conseiller ANCAR": "Conseil de proximité, adoption et suivi.",
    "Projet / ONG": "Indicateurs, risques, résultats et traçabilité.",
    "Investisseur / Agrobusiness": "Rentabilité, risques, hypothèses et scénarios.",
    "Expert / Chercheur": "Données manquantes, hypothèses et protocole d'observation.",
    "Gestionnaire eau": "Eau, irrigation, drainage et risques hydriques.",
}


# =========================================================
# BASE DE DONNÉES — MODÈLE UNIQUE
# =========================================================
def db_conn():
    con = sqlite3.connect(DB_FILE, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def db_exec(sql, params=(), fetch=False, many=False):
    con = db_conn()
    try:
        cur = con.cursor()
        if many:
            cur.executemany(sql, params)
        else:
            cur.execute(sql, params)
        rows = cur.fetchall() if fetch else None
        con.commit()
        return [dict(r) for r in rows] if rows is not None else cur.lastrowid
    finally:
        con.close()


def init_db():
    con = db_conn()
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS dossiers (
        id TEXT PRIMARY KEY, nom TEXT NOT NULL, client TEXT, region TEXT,
        commune TEXT, village TEXT, type_exploitation TEXT,
        latitude REAL, longitude REAL, notes TEXT, created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS parcelles (
        id TEXT PRIMARY KEY, dossier_id TEXT NOT NULL, nom TEXT NOT NULL,
        culture TEXT, stade TEXT, surface_ha REAL DEFAULT 0, perimetre_m REAL DEFAULT 0,
        latitude REAL, longitude REAL, geometry_json TEXT, statut TEXT DEFAULT 'active',
        source TEXT DEFAULT 'Terrain', confidence REAL DEFAULT 1.0,
        date_observation TEXT, created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS observations (
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, domaine TEXT,
        description TEXT, gravite TEXT, incidence REAL, surface_affectee_ha REAL,
        date_observation TEXT, latitude REAL, longitude REAL, photo_name TEXT,
        source TEXT DEFAULT 'Terrain', confidence REAL DEFAULT 0.8,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, type_analyse TEXT,
        parametre TEXT, valeur REAL, unite TEXT, reference TEXT, source TEXT,
        date_analyse TEXT, statut_validation TEXT DEFAULT 'À vérifier',
        confidence REAL DEFAULT 0.8, notes TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS assets (
        id TEXT PRIMARY KEY, dossier_id TEXT, type_asset TEXT, nom TEXT,
        quantite REAL, unite TEXT, etat TEXT, notes TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS missions (
        id TEXT PRIMARY KEY, dossier_id TEXT, client TEXT, objet TEXT,
        statut TEXT, priorite TEXT, responsable TEXT, debut TEXT, echeance TEXT,
        budget REAL DEFAULT 0, notes TEXT, created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS actions (
        id TEXT PRIMARY KEY, dossier_id TEXT, mission_id TEXT, titre TEXT,
        responsable TEXT, echeance TEXT, statut TEXT, priorite TEXT,
        preuve TEXT, created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS finance (
        id TEXT PRIMARY KEY, dossier_id TEXT, mission_id TEXT, type TEXT,
        libelle TEXT, montant REAL, date_operation TEXT, statut TEXT, notes TEXT
    );
    CREATE TABLE IF NOT EXISTS sync_records (
        id TEXT PRIMARY KEY, source TEXT, type_donnee TEXT, url TEXT,
        statut TEXT, message TEXT, nb_elements INTEGER DEFAULT 0,
        fetched_at TEXT
    );
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, domaine TEXT,
        niveau TEXT, titre TEXT, message TEXT, source TEXT,
        statut TEXT DEFAULT 'Ouverte', created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS ai_history (
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, acteur TEXT,
        question TEXT, answer TEXT, evidence TEXT, confidence REAL, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS audit (
        id TEXT PRIMARY KEY, user_email TEXT, action TEXT, entity TEXT,
        entity_id TEXT, details TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY, password_hash TEXT, nom TEXT, role TEXT,
        zone TEXT, statut TEXT DEFAULT 'Actif', created_at TEXT
    );
    """)
    con.commit()
    con.close()

    owner_hash = hashlib.sha256(OWNER_PASS.encode("utf-8")).hexdigest()
    existing = db_exec("SELECT email FROM users WHERE lower(email)=lower(?)", (OWNER_EMAIL,), True)
    if not existing:
        db_exec(
            "INSERT INTO users(email,password_hash,nom,role,zone,statut,created_at) VALUES(?,?,?,?,?,?,?)",
            (OWNER_EMAIL, owner_hash, "Administrateur Principal", "Super-Admin",
             "National Sénégal", "Actif", datetime.now().isoformat(timespec="seconds"))
        )


init_db()


# =========================================================
# SESSION / CONTEXTE CENTRAL
# =========================================================
def init_state():
    defaults = {
        "user": None,
        "dossier_id": None,
        "parcelle_id": None,
        "sync_status": "Non synchronisé",
        "sync_time": None,
        "last_ai": "",
        "last_quality": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def audit(action, entity="", entity_id="", details=""):
    user = st.session_state.get("user") or {}
    db_exec(
        "INSERT INTO audit(id,user_email,action,entity,entity_id,details,created_at) VALUES(?,?,?,?,?,?,?)",
        (str(uuid.uuid4()), user.get("email", "anonymous"), action, entity, entity_id,
         str(details), datetime.now().isoformat(timespec="seconds"))
    )


def now():
    return datetime.now().isoformat(timespec="seconds")


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def polygon_area_ha(coords):
    if not coords or len(coords) < 3:
        return 0.0
    lat0 = math.radians(sum(float(p[0]) for p in coords) / len(coords))
    R = 6371000.0
    xy = []
    for lat, lon in coords:
        xy.append((
            math.radians(float(lon)) * R * math.cos(lat0),
            math.radians(float(lat)) * R
        ))
    area = 0
    for i in range(len(xy)):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % len(xy)]
        area += x1*y2 - x2*y1
    return abs(area) / 2 / 10000


def polygon_perimeter_m(coords):
    if not coords or len(coords) < 2:
        return 0.0
    R = 6371000.0
    total = 0
    for i in range(len(coords)):
        lat1, lon1 = map(float, coords[i])
        lat2, lon2 = map(float, coords[(i + 1) % len(coords)])
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        total += 2*R*math.asin(min(1, math.sqrt(a)))
    return total


def drawing_coords(drawing):
    if not drawing:
        return None
    g = drawing.get("geometry", {})
    typ, c = g.get("type"), g.get("coordinates")
    if typ == "Polygon" and c:
        return [[float(x[1]), float(x[0])] for x in c[0]]
    if typ == "MultiPolygon" and c:
        return [[float(x[1]), float(x[0])] for x in c[0][0]]
    if typ == "Point" and c:
        return [[float(c[1]), float(c[0])]]
    return None


def active_dossier():
    if not st.session_state.get("dossier_id"):
        return None
    rows = db_exec("SELECT * FROM dossiers WHERE id=?", (st.session_state.dossier_id,), True)
    return rows[0] if rows else None


def active_parcelle():
    if not st.session_state.get("parcelle_id"):
        return None
    rows = db_exec("SELECT * FROM parcelles WHERE id=?", (st.session_state.parcelle_id,), True)
    return rows[0] if rows else None


def context():
    d = active_dossier() or {}
    p = active_parcelle() or {}
    geometry = json.loads(p.get("geometry_json") or "[]") if p else []
    return {
        "dossier_id": d.get("id"),
        "dossier": d.get("nom"),
        "client": d.get("client"),
        "region": d.get("region"),
        "commune": d.get("commune"),
        "village": d.get("village"),
        "latitude": p.get("latitude", d.get("latitude")),
        "longitude": p.get("longitude", d.get("longitude")),
        "parcelle_id": p.get("id"),
        "parcelle": p.get("nom"),
        "culture": p.get("culture"),
        "stade": p.get("stade"),
        "surface_ha": p.get("surface_ha", 0),
        "perimetre_m": p.get("perimetre_m", 0),
        "geometry": geometry,
    }


def quality_score():
    c = context()
    score = 100
    if not c["dossier_id"]: score -= 30
    if not c["parcelle_id"]: score -= 20
    if c["latitude"] is None or c["longitude"] is None: score -= 15
    if not c["surface_ha"] or c["surface_ha"] <= 0: score -= 10
    if not c["culture"]: score -= 10
    obs = db_exec("SELECT COUNT(*) n FROM observations WHERE dossier_id=?", (c["dossier_id"],), True) if c["dossier_id"] else [{"n": 0}]
    ana = db_exec("SELECT COUNT(*) n FROM analyses WHERE dossier_id=?", (c["dossier_id"],), True) if c["dossier_id"] else [{"n": 0}]
    if int(obs[0]["n"]) == 0: score -= 5
    if int(ana[0]["n"]) == 0: score -= 5
    return max(0, min(100, score))


# =========================================================
# SYNCHRONISATION — UN SEUL CENTRE
# =========================================================
def sync_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "forecast_days": 7, "timezone": "auto"
    }
    r = requests.get(url, params=params, timeout=12)
    r.raise_for_status()
    data = r.json()
    db_exec(
        "INSERT INTO sync_records(id,source,type_donnee,url,statut,message,nb_elements,fetched_at) VALUES(?,?,?,?,?,?,?,?)",
        (new_id("sync"), "Open-Meteo", "Météo opérationnelle", url, "OK",
         "Prévision météo récupérée pour la parcelle active.", 7, now())
    )
    return data


def sync_official_catalog():
    # La synchronisation officielle ne fabrique pas de données.
    # Elle enregistre les portails de référence et leur date de contrôle.
    n = 0
    for name, url in SOURCES.items():
        db_exec(
            "INSERT INTO sync_records(id,source,type_donnee,url,statut,message,nb_elements,fetched_at) VALUES(?,?,?,?,?,?,?,?)",
            (new_id("sync"), name, "Portail institutionnel", url, "RÉFÉRENCE",
             "Portail enregistré comme source à vérifier; aucune statistique inventée.", 0, now())
        )
        n += 1
    return n


def sync_all():
    c = context()
    results = []
    if c["latitude"] is not None and c["longitude"] is not None:
        try:
            weather = sync_weather(float(c["latitude"]), float(c["longitude"]))
            st.session_state["weather"] = weather
            results.append("Météo opérationnelle")
        except Exception as exc:
            results.append(f"Météo indisponible: {exc}")
            db_exec(
                "INSERT INTO sync_records(id,source,type_donnee,url,statut,message,nb_elements,fetched_at) VALUES(?,?,?,?,?,?,?,?)",
                (new_id("sync"), "Open-Meteo", "Météo opérationnelle",
                 "https://api.open-meteo.com/", "ERREUR", str(exc), 0, now())
            )
    results.append(f"{sync_official_catalog()} portails institutionnels contrôlés")
    st.session_state["sync_status"] = "Synchronisé"
    st.session_state["sync_time"] = now()
    audit("SYNCHRONISATION_GLOBALE", "contexte", c["parcelle_id"] or "", results)
    return results


# =========================================================
# IA LOCALE — SANS CLÉ API
# =========================================================
def local_ai(question, actor):
    c = context()
    q = (question or "").lower()
    zone = next((z for z, v in AGROZONES.items() if c["region"] in v["regions"]), None)
    zinfo = AGROZONES.get(zone or "", {})
    actions = [
        "Décrire et dater précisément le problème.",
        "Contrôler plusieurs points représentatifs de la parcelle.",
        "Croiser observation, sol, eau, météo et historique avant décision.",
        "Documenter l'intervention et programmer un contrôle sous 48–72 h.",
    ]
    if any(x in q for x in ["jaun", "chlorose", "pâle"]):
        actions.insert(1, "Vérifier humidité, drainage, racines et répartition du jaunissement.")
    if any(x in q for x in ["insect", "chenille", "puceron", "ravageur"]):
        actions.insert(1, "Quantifier l'incidence et rechercher le ravageur sur plusieurs plants.")
    if any(x in q for x in ["maladie", "tache", "flétr", "pourrit"]):
        actions.insert(1, "Photographier plusieurs plants atteints et sains et vérifier la progression.")
    if any(x in q for x in ["eau", "irrig", "sécher", "pluie"]):
        actions.insert(1, "Contrôler l'humidité réelle, l'uniformité d'irrigation et le drainage.")

    evidence = [
        "Contexte dossier/parcelle enregistré",
        "Données terrain disponibles" if c["dossier_id"] else "Données terrain absentes",
        "Référentiel agroécologique indicatif",
        "Météo opérationnelle si synchronisée",
    ]
    confidence = min(0.95, 0.45 + quality_score()/200)
    text = f"""### 🧠 Analyse YouAgronoMe — {actor}

**Contexte actif :** {c['dossier'] or 'non sélectionné'} · {c['parcelle'] or 'non sélectionnée'} · {c['culture'] or 'culture non renseignée'} · {c['region'] or 'région non renseignée'}

**Lecture contextuelle**
- Zone agroécologique : {zone or 'à déterminer'}
- Sol de référence : {zinfo.get('sol', 'à confirmer par observation/analyse')}
- Climat : {zinfo.get('climat', 'à confirmer')}
- Risques indicatifs : {zinfo.get('risques', 'à évaluer')}

**Hypothèse de travail**
La question doit être confrontée aux observations réelles. Cette IA locale ne transforme pas une hypothèse en diagnostic officiel.

**Plan priorisé**
{chr(10).join(f'{i+1}. {a}' for i,a in enumerate(actions))}

**Niveau de confiance du dossier :** {confidence*100:.0f} %
**Qualité des données :** {quality_score()}/100

**Preuves mobilisées**
{chr(10).join('- '+x for x in evidence)}

**Sécurité**
Aucune dose ou prescription phytosanitaire spécifique ne doit être décidée uniquement à partir de cette réponse. Pour une suspicion importante, faire confirmer par le technicien/organisme compétent.
"""
    return text, confidence


# =========================================================
# AUTHENTIFICATION
# =========================================================
def login_box():
    st.markdown("## 🔐 Accès professionnel")
    st.caption("Les comptes sont stockés avec un hash de mot de passe dans SQLite.")
    email = st.text_input("E-mail / identifiant", key="auth_email")
    password = st.text_input("Mot de passe", type="password", key="auth_password")
    if st.button("Se connecter", type="primary", key="auth_login"):
        h = hashlib.sha256(password.encode("utf-8")).hexdigest()
        rows = db_exec(
            "SELECT * FROM users WHERE lower(email)=lower(?) AND password_hash=? AND statut='Actif'",
            (email.strip(), h), True
        )
        if rows:
            st.session_state["user"] = rows[0]
            audit("CONNEXION", "user", rows[0]["email"])
            st.rerun()
        st.error("Identifiants invalides ou compte inactif.")


# =========================================================
# EN-TÊTE + CONTEXTE
# =========================================================
def header():
    st.markdown("""
    <style>
    .hero{padding:20px;border-radius:16px;background:linear-gradient(135deg,#14532d,#166534);
    color:white;margin-bottom:16px}
    .hero h1{color:white!important;margin:0}
    .ctx{padding:12px;border:1px solid #dbe5dd;border-radius:12px;background:#f7faf7}
    </style>
    """, unsafe_allow_html=True)
    st.markdown(
        "<div class='hero'><h1>🌾 YouAgronoMe — HUB Analyse & Consultance 360°</h1>"
        "<p>Données → SIG → Diagnostic → IA → Décision → Mission → Rapport</p></div>",
        unsafe_allow_html=True
    )
    c = context()
    q = quality_score()
    cols = st.columns(6)
    cols[0].metric("Dossier", c["dossier"] or "—")
    cols[1].metric("Parcelle", c["parcelle"] or "—")
    cols[2].metric("Surface", f"{c['surface_ha'] or 0:.2f} ha")
    cols[3].metric("Région", c["region"] or "—")
    cols[4].metric("Qualité", f"{q}/100")
    cols[5].metric("Synchro", st.session_state.get("sync_status", "—"))


def context_selector():
    dossiers = db_exec("SELECT * FROM dossiers ORDER BY updated_at DESC", fetch=True)
    names = ["➕ Nouveau dossier"] + [f"{d['id']} · {d['nom']}" for d in dossiers]
    current = st.session_state.get("dossier_id")
    idx = 0
    if current:
        for i, d in enumerate(dossiers, 1):
            if d["id"] == current:
                idx = i
                break
    choice = st.selectbox("📁 Dossier d'exploitation actif", names, index=idx, key="global_dossier")
    if choice == "➕ Nouveau dossier":
        with st.form("new_dossier_global"):
            a,b,c = st.columns(3)
            nom = a.text_input("Nom exploitation")
            client = b.text_input("Client / producteur")
            region = c.selectbox("Région", list(REGIONS_COORD))
            commune = a.text_input("Commune")
            village = b.text_input("Village")
            typ = c.selectbox("Type", ["Agriculture", "Élevage", "Aquaculture", "Agroalimentaire", "Mixte"])
            if st.form_submit_button("Créer le dossier", type="primary"):
                did = new_id("DOS")
                lat, lon = REGIONS_COORD[region]
                db_exec(
                    """INSERT INTO dossiers(id,nom,client,region,commune,village,type_exploitation,
                    latitude,longitude,notes,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (did, nom or "Exploitation sans nom", client, region, commune, village, typ,
                     lat, lon, "", now(), now())
                )
                st.session_state["dossier_id"] = did
                st.session_state["parcelle_id"] = None
                audit("CREATION", "dossier", did)
                st.rerun()
    else:
        did = choice.split(" · ", 1)[0]
        if did != current:
            st.session_state["dossier_id"] = did
            st.session_state["parcelle_id"] = None
            audit("SELECTION", "dossier", did)
    if st.session_state.get("dossier_id"):
        pars = db_exec("SELECT * FROM parcelles WHERE dossier_id=? ORDER BY updated_at DESC",
                       (st.session_state["dossier_id"],), True)
        if pars:
            pnames = [f"{p['id']} · {p['nom']} ({p['surface_ha']:.2f} ha)" for p in pars]
            pidx = next((i for i,p in enumerate(pars) if p["id"] == st.session_state.get("parcelle_id")), 0)
            pc = st.selectbox("📍 Parcelle active — source géographique commune", pnames, index=pidx, key="global_parcelle")
            pid = pc.split(" · ", 1)[0]
            st.session_state["parcelle_id"] = pid
        else:
            st.info("Aucune parcelle. Créez-la dans SIG & Diagnostic → GPS / Polygones.")


# =========================================================
# ONGLET 1 — TERRAIN & DONNÉES
# =========================================================
def terrain_tab():
    subs = st.tabs([
        "📁 Dossier 360°", "🌾 Agriculture", "🐄 Élevage", "🐟 Aquaculture",
        "🏭 Agroalimentaire", "🧪 Analyses", "👁️ Observations", "📋 Historique"
    ])

    with subs[0]:
        d = active_dossier()
        if not d:
            st.info("Sélectionnez ou créez un dossier.")
        else:
            st.subheader("📁 Dossier d'exploitation 360°")
            a,b,c = st.columns(3)
            a.write(f"**Nom :** {d['nom']}")
            b.write(f"**Client :** {d['client'] or '—'}")
            c.write(f"**Type :** {d['type_exploitation']}")
            a.write(f"**Région :** {d['region']}")
            b.write(f"**Commune :** {d['commune'] or '—'}")
            c.write(f"**Village :** {d['village'] or '—'}")
            st.success("Le dossier actif est partagé automatiquement avec tous les autres modules.")
            st.caption("Source du contexte : base persistante YouAgronoMe.")

    with subs[1]:
        st.subheader("🌾 Registre Agriculture")
        if not st.session_state.get("dossier_id"):
            st.warning("Sélectionnez un dossier.")
        else:
            p = active_parcelle()
            if p:
                st.info(f"Parcelle active : {p['nom']} · {p['surface_ha']:.2f} ha")
            st.write("Les cultures sont enregistrées au niveau de la parcelle active.")
            with st.form("agri_update"):
                culture = st.selectbox("Culture", CULTURES, index=CULTURES.index(p["culture"]) if p and p["culture"] in CULTURES else 0)
                stade = st.selectbox("Stade", STADES, index=STADES.index(p["stade"]) if p and p["stade"] in STADES else 0)
                rendement = st.number_input("Rendement cible (t/ha)", 0.0, 100.0, 3.0)
                irrigation = st.selectbox("Mode eau", ["Pluvial", "Irrigué", "Mixte"])
                if st.form_submit_button("Enregistrer l'itinéraire"):
                    if p:
                        db_exec("UPDATE parcelles SET culture=?,stade=?,updated_at=? WHERE id=?",
                                (culture, stade, now(), p["id"]))
                    else:
                        st.warning("Créez d'abord une parcelle.")
                    if p:
                        db_exec("INSERT INTO observations(id,dossier_id,parcelle_id,domaine,description,gravite,incidence,date_observation,source,confidence,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                                (new_id("OBS"), st.session_state["dossier_id"], p["id"], "Agriculture",
                                 f"Rendement cible {rendement} t/ha · {irrigation}", "Information", 0,
                                 now(), "Utilisateur", 1.0, now()))
                        audit("MISE_A_JOUR", "parcelle", p["id"], {"culture": culture, "stade": stade})

    with subs[2]:
        st.subheader("🐄 Élevage — registre du cheptel")
        did = st.session_state.get("dossier_id")
        if not did:
            st.warning("Sélectionnez un dossier.")
        else:
            with st.form("livestock_form"):
                a,b,c = st.columns(3)
                espece = a.selectbox("Espèce", ["Bovin", "Ovin", "Caprin", "Volaille", "Porcin", "Autre"])
                quantite = b.number_input("Effectif", 0, 100000, 0)
                etat = c.selectbox("État", ["Normal", "Surveillance", "Alerte"])
                notes = st.text_area("Observations")
                if st.form_submit_button("Enregistrer le cheptel"):
                    db_exec("INSERT INTO assets(id,dossier_id,type_asset,nom,quantite,unite,etat,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                            (new_id("AST"), did, "Élevage", espece, quantite, "têtes", etat, notes, now()))
                    audit("AJOUT", "elevage", did)
            rows = db_exec("SELECT * FROM assets WHERE dossier_id=? AND type_asset='Élevage' ORDER BY created_at DESC",
                           (did,), True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with subs[3]:
        st.subheader("🐟 Aquaculture — unités de production")
        did = st.session_state.get("dossier_id")
        if not did:
            st.warning("Sélectionnez un dossier.")
        else:
            with st.form("aqua_form"):
                a,b,c = st.columns(3)
                espece = a.text_input("Espèce", "Tilapia")
                volume = b.number_input("Volume / capacité", 0.0, 1e9, 0.0)
                unite = c.selectbox("Unité", ["m³", "étang", "bassin", "cage"])
                oxy = a.number_input("Oxygène dissous (mg/L)", 0.0, 30.0, 0.0)
                ph = b.number_input("pH", 0.0, 14.0, 7.0)
                temp = c.number_input("Température (°C)", 0.0, 50.0, 25.0)
                if st.form_submit_button("Enregistrer unité"):
                    desc = f"O2={oxy} mg/L · pH={ph} · T={temp} °C"
                    db_exec("INSERT INTO assets(id,dossier_id,type_asset,nom,quantite,unite,etat,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                            (new_id("AST"), did, "Aquaculture", espece, volume, unite, "Normal", desc, now()))
                    audit("AJOUT", "aquaculture", did)
            rows = db_exec("SELECT * FROM assets WHERE dossier_id=? AND type_asset='Aquaculture' ORDER BY created_at DESC",
                           (did,), True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with subs[4]:
        st.subheader("🏭 Agroalimentaire")
        did = st.session_state.get("dossier_id")
        if not did:
            st.warning("Sélectionnez un dossier.")
        else:
            with st.form("agrofood_form"):
                a,b,c = st.columns(3)
                produit = a.text_input("Produit transformé")
                volume = b.number_input("Volume", 0.0, 1e9, 0.0)
                unite = c.selectbox("Unité", ["kg", "t", "litres", "unités"])
                pertes = a.number_input("Pertes estimées (%)", 0.0, 100.0, 0.0)
                conservation = b.selectbox("Conservation", ["À définir", "Séchage", "Froid", "Stockage sec", "Transformation"])
                qualite = c.selectbox("Qualité", ["Non évaluée", "Conforme", "À surveiller", "Non conforme"])
                if st.form_submit_button("Enregistrer"):
                    notes = f"Pertes={pertes}% · Conservation={conservation} · Qualité={qualite}"
                    db_exec("INSERT INTO assets(id,dossier_id,type_asset,nom,quantite,unite,etat,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                            (new_id("AST"), did, "Agroalimentaire", produit, volume, unite, qualite, notes, now()))
                    audit("AJOUT", "agroalimentaire", did)
            rows = db_exec("SELECT * FROM assets WHERE dossier_id=? AND type_asset='Agroalimentaire' ORDER BY created_at DESC",
                           (did,), True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with subs[5]:
        st.subheader("🧪 Analyses & laboratoire")
        did, pid = st.session_state.get("dossier_id"), st.session_state.get("parcelle_id")
        if not did:
            st.warning("Sélectionnez un dossier.")
        else:
            with st.form("analysis_form"):
                a,b,c = st.columns(3)
                typ = a.selectbox("Type", ["Sol", "Eau", "Végétal", "Aliment", "Autre"])
                param = b.text_input("Paramètre", "pH")
                valeur = c.number_input("Valeur", -1e9, 1e9, 0.0)
                unite = a.text_input("Unité", "")
                ref = b.text_input("Référence / méthode")
                source = c.selectbox("Source", ["Laboratoire", "Terrain", "Officiel", "Utilisateur"])
                validation = st.selectbox("Validation", ["Validé", "À vérifier", "Rejeté"])
                if st.form_submit_button("Enregistrer l'analyse"):
                    db_exec("""INSERT INTO analyses(id,dossier_id,parcelle_id,type_analyse,parametre,valeur,unite,reference,source,date_analyse,statut_validation,confidence,notes,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (new_id("ANA"), did, pid, typ, param, valeur, unite, ref, source, now(), validation,
                             0.95 if validation == "Validé" else 0.7, "", now()))
                    audit("AJOUT", "analyse", did, {"parametre": param, "valeur": valeur})
            rows = db_exec("SELECT * FROM analyses WHERE dossier_id=? ORDER BY date_analyse DESC", (did,), True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with subs[6]:
        st.subheader("👁️ Observation terrain géolocalisée")
        did, pid = st.session_state.get("dossier_id"), st.session_state.get("parcelle_id")
        if not did:
            st.warning("Sélectionnez un dossier.")
        else:
            c = context()
            with st.form("observation_form"):
                a,b,c1 = st.columns(3)
                domaine = a.selectbox("Domaine", ["Agriculture", "Élevage", "Aquaculture", "Agroalimentaire", "Sol", "Eau", "Phytosanitaire"])
                gravite = b.selectbox("Gravité", ["Information", "Faible", "Moyenne", "Élevée", "Critique"])
                incidence = c1.number_input("Incidence (%)", 0.0, 100.0, 0.0)
                desc = st.text_area("Description précise")
                photo = st.file_uploader("Photo (optionnel)", type=["jpg","jpeg","png","webp"], key="terrain_photo")
                if st.form_submit_button("Enregistrer l'observation"):
                    photo_name = photo.name if photo else ""
                    db_exec("""INSERT INTO observations(id,dossier_id,parcelle_id,domaine,description,gravite,incidence,surface_affectee_ha,date_observation,latitude,longitude,photo_name,source,confidence,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (new_id("OBS"), did, pid, domaine, desc, gravite, incidence, 0,
                             now(), c["latitude"], c["longitude"], photo_name, "Terrain", 0.85, now()))
                    if gravite in ["Élevée", "Critique"]:
                        db_exec("""INSERT INTO alerts(id,dossier_id,parcelle_id,domaine,niveau,titre,message,source,created_at)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                                (new_id("ALT"), did, pid, domaine, gravite,
                                 f"Observation {domaine}", desc or "Observation nécessitant un suivi.",
                                 "Terrain", now()))
                    audit("OBSERVATION", "terrain", did, domaine)
                    st.success("Observation enregistrée dans le dossier central.")
            rows = db_exec("SELECT * FROM observations WHERE dossier_id=? ORDER BY created_at DESC LIMIT 100", (did,), True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with subs[7]:
        st.subheader("📋 Historique unifié")
        did = st.session_state.get("dossier_id")
        if did:
            obs = db_exec("SELECT created_at,'Observation' type,description texte FROM observations WHERE dossier_id=?", (did,), True)
            ana = db_exec("SELECT created_at,'Analyse' type,parametre || ' = ' || valeur texte FROM analyses WHERE dossier_id=?", (did,), True)
            act = db_exec("SELECT created_at,'Action' type,titre texte FROM actions WHERE dossier_id=?", (did,), True)
            hist = sorted(obs+ana+act, key=lambda x: x["created_at"], reverse=True)
            st.dataframe(pd.DataFrame(hist), use_container_width=True, hide_index=True)
        else:
            st.info("Sélectionnez un dossier.")


# =========================================================
# ONGLET 2 — SIG & DIAGNOSTIC
# =========================================================
def sig_tab():
    subs = st.tabs([
        "🗺️ Carte", "📍 GPS / Polygones", "🌱 Sols & Eau",
        "🦠 Phytosanitaire", "🌦️ Climat & Risques", "🔎 Qualité des données"
    ])

    with subs[0]:
        st.subheader("🗺️ Carte centrale du dossier")
        c = context()
        if not c["dossier_id"]:
            st.info("Créez/sélectionnez un dossier.")
        elif HAS_FOLIUM:
            lat = c["latitude"] or 14.7
            lon = c["longitude"] or -16.2
            m = folium.Map(location=[lat, lon], zoom_start=13, control_scale=True)
            if c["geometry"]:
                folium.Polygon(c["geometry"], popup=c["parcelle"] or "Parcelle active",
                               tooltip=f"{c['surface_ha']:.2f} ha").add_to(m)
            folium.Marker([lat, lon], tooltip="Contexte actif").add_to(m)
            st_folium(m, width=1000, height=550, key="central_sig_map")
        else:
            st.warning("Installez folium et streamlit-folium pour la carte interactive.")
            st.write(c)

    with subs[1]:
        st.subheader("📍 GPS & délimitation — source géographique unique")
        did = st.session_state.get("dossier_id")
        if not did:
            st.warning("Sélectionnez un dossier.")
        else:
            d = active_dossier()
            c1,c2 = st.columns(2)
            with c1:
                lat = st.number_input("Latitude", value=float(d.get("latitude") or 14.7), format="%.6f", key="sig_lat")
                lon = st.number_input("Longitude", value=float(d.get("longitude") or -16.2), format="%.6f", key="sig_lon")
                if st.button("📍 Enregistrer le point central", key="sig_save_point"):
                    db_exec("UPDATE dossiers SET latitude=?,longitude=?,updated_at=? WHERE id=?",
                            (lat, lon, now(), did))
                    audit("GPS", "dossier", did, {"lat": lat, "lon": lon})
                    st.success("Point GPS centralisé.")
            with c2:
                parcelles = db_exec("SELECT * FROM parcelles WHERE dossier_id=?", (did,), True)
                with st.form("new_parcel"):
                    nom = st.text_input("Nom de la parcelle", "Parcelle 1")
                    culture = st.selectbox("Culture", CULTURES)
                    if st.form_submit_button("Créer la parcelle"):
                        pid = new_id("PAR")
                        db_exec("""INSERT INTO parcelles(id,dossier_id,nom,culture,stade,latitude,longitude,geometry_json,created_at,updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?)""",
                                (pid,did,nom,culture,STADES[0],lat,lon,"[]",now(),now()))
                        st.session_state["parcelle_id"] = pid
                        audit("CREATION", "parcelle", pid)
                        st.rerun()

            p = active_parcelle()
            if p:
                st.markdown(f"**Parcelle active : {p['nom']}**")
                if HAS_FOLIUM:
                    m = folium.Map(location=[p["latitude"] or lat, p["longitude"] or lon], zoom_start=15)
                    geom = json.loads(p.get("geometry_json") or "[]")
                    if geom:
                        folium.Polygon(geom, color="green", fill=True, fill_opacity=0.2).add_to(m)
                    Draw(export=True, draw_options={"polyline": False, "circle": False, "circlemarker": False},
                         edit_options={"edit": True, "remove": True}).add_to(m)
                    result = st_folium(m, width=900, height=500, key="sig_polygon_map")
                    drawing = result.get("last_active_drawing") if result else None
                    coords = drawing_coords(drawing)
                    if coords and len(coords) >= 3:
                        area = polygon_area_ha(coords)
                        perim = polygon_perimeter_m(coords)
                        db_exec("""UPDATE parcelles SET geometry_json=?,surface_ha=?,perimetre_m=?,latitude=?,longitude=?,source='Terrain',confidence=0.98,date_observation=?,updated_at=? WHERE id=?""",
                                (json.dumps(coords), area, perim, coords[0][0], coords[0][1], now(), now(), p["id"]))
                        db_exec("UPDATE dossiers SET latitude=?,longitude=?,updated_at=? WHERE id=?",
                                (coords[0][0], coords[0][1], now(), did))
                        audit("GEOMETRIE", "parcelle", p["id"], {"surface_ha": area, "perimetre_m": perim})
                        st.success(f"Parcelle synchronisée : {area:.3f} ha · {perim:.1f} m")
                st.metric("Surface", f"{p['surface_ha']:.3f} ha")
                st.metric("Périmètre", f"{p['perimetre_m']:.1f} m")

    with subs[2]:
        st.subheader("🌱 Sols & Eau")
        c = context()
        zone = next((z for z,v in AGROZONES.items() if c["region"] in v["regions"]), None)
        if zone:
            st.info(f"Zone agroécologique indicative : {zone}")
            st.write("**Sol :**", AGROZONES[zone]["sol"])
            st.write("**Climat :**", AGROZONES[zone]["climat"])
            st.write("**Risques :**", AGROZONES[zone]["risques"])
        st.markdown("#### Calcul irrigation")
        a,b,c1,d = st.columns(4)
        eto = a.number_input("ETo (mm/j)", 0.0, 20.0, 5.5, key="sig_eto")
        kc = b.number_input("Kc", 0.1, 1.5, 1.0, key="sig_kc")
        surface = c1.number_input("Surface (ha)", 0.1, 100000.0, float(context()["surface_ha"] or 1), key="sig_surface")
        effic = d.number_input("Efficacité", 0.1, 1.0, 0.75, key="sig_eff")
        etc = eto * kc
        m3 = etc * 10 * surface / effic
        st.metric("ETc", f"{etc:.2f} mm/j")
        st.metric("Besoin brut", f"{m3:.1f} m³/j")
        st.caption("Calcul indicatif; les paramètres doivent être adaptés aux conditions réelles de la parcelle.")

    with subs[3]:
        st.subheader("🦠 Diagnostic phytosanitaire")
        st.warning("Le diagnostic photographique ou textuel est un pré-diagnostic. Une prescription officielle doit être confirmée.")
        symptom = st.text_area("Symptômes observés", key="phyt_symptoms")
        severity = st.select_slider("Niveau", options=["Faible","Moyen","Élevé","Critique"], key="phyt_severity")
        if st.button("🔬 Construire le pré-diagnostic", key="phyt_run"):
            q = f"{symptom} niveau {severity}"
            answer, conf = local_ai(q, "Technicien / Conseiller")
            st.markdown(answer)
            audit("PRE_DIAGNOSTIC", "phytosanitaire", st.session_state.get("parcelle_id",""))

    with subs[4]:
        st.subheader("🌦️ Climat & risques")
        c = context()
        if st.button("🔄 Synchroniser météo de la parcelle", key="sig_weather_sync"):
            if c["latitude"] is not None:
                try:
                    data = sync_weather(float(c["latitude"]), float(c["longitude"]))
                    st.session_state["weather"] = data
                    st.session_state["sync_status"] = "Météo synchronisée"
                    st.success("Météo synchronisée.")
                except Exception as exc:
                    st.error(f"Synchronisation météo impossible : {exc}")
            else:
                st.warning("Coordonnées absentes.")
        weather = st.session_state.get("weather")
        if weather:
            cur = weather.get("current", {})
            a,b,c1,d = st.columns(4)
            a.metric("Température", f"{cur.get('temperature_2m','—')} °C")
            b.metric("Humidité", f"{cur.get('relative_humidity_2m','—')} %")
            c1.metric("Pluie", f"{cur.get('precipitation','—')} mm")
            d.metric("Vent", f"{cur.get('wind_speed_10m','—')} km/h")
            st.dataframe(pd.DataFrame(weather.get("daily", {})), use_container_width=True)
        st.caption("La météo opérationnelle vient d'une source météo numérique; les vigilances officielles doivent être vérifiées auprès de l'ANACIM.")

    with subs[5]:
        st.subheader("🔎 Centre de qualité des données")
        score = quality_score()
        st.progress(score / 100)
        st.metric("Score qualité", f"{score}/100")
        c = context()
        checks = [
            ("Dossier actif", bool(c["dossier_id"]), "Créer/sélectionner un dossier"),
            ("Parcelle active", bool(c["parcelle_id"]), "Créer/sélectionner une parcelle"),
            ("GPS", c["latitude"] is not None and c["longitude"] is not None, "Renseigner les coordonnées"),
            ("Surface", bool(c["surface_ha"] and c["surface_ha"] > 0), "Dessiner/valider le polygone"),
            ("Culture", bool(c["culture"]), "Renseigner la culture"),
        ]
        st.dataframe(pd.DataFrame([
            {"Contrôle": a, "OK": "Oui" if b else "Non", "Action": d} for a,b,d in checks
        ]), use_container_width=True, hide_index=True)
        if st.button("🧹 Recalculer qualité", key="recalc_quality"):
            st.session_state["last_quality"] = score
            st.success(f"Score recalculé : {score}/100")


# =========================================================
# ONGLET 3 — IA & DÉCISION
# =========================================================
def ia_tab():
    subs = st.tabs([
        "🧠 IA Expert 360°", "🔬 Diagnostic", "📊 Simulations",
        "💰 Économie / ROI", "🚨 Alertes", "📈 KPI & Scoring", "✅ Plan d'action"
    ])

    with subs[0]:
        st.subheader("🧠 IA Expert 360° — contexte automatique")
        c = context()
        st.info("L'IA ne redemande pas le GPS, la surface ou la culture : elle lit le contexte central actif.")
        actor = st.selectbox("Acteur", list(ACTEURS), key="ia360_actor")
        st.caption(ACTEURS[actor])
        question = st.text_area("Question / problème terrain", key="ia360_question",
                                placeholder="Ex. Les feuilles du maïs jaunissent depuis quatre jours après une pluie.")
        if st.button("🤖 Analyser avec le moteur local", type="primary", key="ia360_run"):
            if not question.strip():
                st.warning("Décrivez le problème.")
            else:
                answer, conf = local_ai(question, actor)
                st.session_state["last_ai"] = answer
                db_exec("""INSERT INTO ai_history(id,dossier_id,parcelle_id,acteur,question,answer,evidence,confidence,created_at)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                        (new_id("AI"), c["dossier_id"], c["parcelle_id"], actor, question, answer,
                         "Contexte central + règles locales; validation terrain requise", conf, now()))
                audit("IA", "ai_history", c["parcelle_id"] or "", question)
        if st.session_state.get("last_ai"):
            st.markdown(st.session_state["last_ai"])

    with subs[1]:
        st.subheader("🔬 Diagnostic multi-domaine")
        c = context()
        obs = db_exec("SELECT * FROM observations WHERE dossier_id=? ORDER BY created_at DESC LIMIT 30",
                      (c["dossier_id"],), True) if c["dossier_id"] else []
        ana = db_exec("SELECT * FROM analyses WHERE dossier_id=? ORDER BY date_analyse DESC LIMIT 30",
                      (c["dossier_id"],), True) if c["dossier_id"] else []
        st.write("**Observations récentes :", len(obs))
        st.write("**Analyses disponibles :", len(ana))
        if obs:
            st.dataframe(pd.DataFrame(obs), use_container_width=True, hide_index=True)
        if ana:
            st.dataframe(pd.DataFrame(ana), use_container_width=True, hide_index=True)

    with subs[2]:
        st.subheader("📊 Simulations")
        c = context()
        a,b,c1,d = st.columns(4)
        rendement = a.number_input("Rendement (t/ha)", 0.0, 100.0, 4.0, key="sim_yield")
        prix = b.number_input("Prix (FCFA/t)", 0.0, 10000000.0, 180000.0, key="sim_price")
        cout = c1.number_input("Charges (FCFA/ha)", 0.0, 10000000.0, 500000.0, key="sim_cost")
        perte = d.slider("Perte / aléa (%)", 0, 100, 10, key="sim_loss")
        ha = float(c["surface_ha"] or 1)
        production = rendement * ha * (1-perte/100)
        ca = production * prix
        charges = cout * ha
        marge = ca - charges
        x,y,z = st.columns(3)
        x.metric("Production ajustée", f"{production:.2f} t")
        y.metric("CA", f"{ca:,.0f} FCFA")
        z.metric("Marge", f"{marge:,.0f} FCFA")
        st.caption("Simulation d'aide à la décision, non donnée comptable certifiée.")

    with subs[3]:
        st.subheader("💰 Économie & ROI")
        did = st.session_state.get("dossier_id")
        if did:
            rows = db_exec("SELECT type, SUM(montant) montant FROM finance WHERE dossier_id=? GROUP BY type", (did,), True)
            df = pd.DataFrame(rows)
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucune opération financière.")
            with st.form("finance_ia_form"):
                a,b,c = st.columns(3)
                typ = a.selectbox("Type", ["Recette", "Dépense"])
                lib = b.text_input("Libellé")
                amount = c.number_input("Montant FCFA", 0.0, 1e12, 0.0)
                if st.form_submit_button("Ajouter"):
                    db_exec("INSERT INTO finance(id,dossier_id,type,libelle,montant,date_operation,statut,notes) VALUES(?,?,?,?,?,?,?,?)",
                            (new_id("FIN"), did, typ, lib, amount, now(), "Enregistré", ""))
                    audit("FINANCE", "finance", did)

    with subs[4]:
        st.subheader("🚨 Alertes")
        did = st.session_state.get("dossier_id")
        if did:
            rows = db_exec("SELECT * FROM alerts WHERE dossier_id=? ORDER BY created_at DESC", (did,), True)
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.success("Aucune alerte enregistrée.")
            if st.button("🔎 Générer les alertes de cohérence", key="generate_alerts"):
                c = context()
                if not c["parcelle_id"]:
                    st.warning("Pas de parcelle active.")
                if quality_score() < 60:
                    db_exec("""INSERT INTO alerts(id,dossier_id,parcelle_id,domaine,niveau,titre,message,source,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?)""",
                            (new_id("ALT"), did, c["parcelle_id"], "Données", "Moyenne",
                             "Qualité de données insuffisante",
                             "Compléter GPS, surface, culture et observations avant une décision sensible.",
                             "Moteur qualité", now()))
                st.rerun()

    with subs[5]:
        st.subheader("📈 KPI & scoring de décision")
        c = context()
        q = quality_score()
        obs_count = len(db_exec("SELECT id FROM observations WHERE dossier_id=?", (c["dossier_id"],), True)) if c["dossier_id"] else 0
        ana_count = len(db_exec("SELECT id FROM analyses WHERE dossier_id=?", (c["dossier_id"],), True)) if c["dossier_id"] else 0
        scores = {
            "Données": q,
            "Terrain": min(100, obs_count*15),
            "Analyses": min(100, ana_count*20),
            "Géospatial": 100 if c["geometry"] else 30,
            "Contexte cultural": 100 if c["culture"] else 20,
        }
        overall = round(np.mean(list(scores.values())))
        st.metric("Score décision global", f"{overall}/100")
        st.dataframe(pd.DataFrame([{"Domaine":k,"Score":v} for k,v in scores.items()]),
                     use_container_width=True, hide_index=True)
        st.caption("Le score de qualité/confiance est distinct du risque agronomique : une donnée peu fiable ne doit pas être interprétée comme un faible risque.")

    with subs[6]:
        st.subheader("✅ Plan d'action")
        did = st.session_state.get("dossier_id")
        if not did:
            st.warning("Sélectionnez un dossier.")
        else:
            with st.form("action_form"):
                a,b,c,d = st.columns(4)
                titre = a.text_input("Action")
                resp = b.text_input("Responsable")
                echeance = c.date_input("Échéance")
                priorite = d.selectbox("Priorité", ["Basse","Normale","Haute","Critique"])
                if st.form_submit_button("Créer action"):
                    db_exec("""INSERT INTO actions(id,dossier_id,titre,responsable,echeance,statut,priorite,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?)""",
                            (new_id("ACT"), did, titre, resp, str(echeance), "À faire", priorite, now(), now()))
                    audit("CREATION", "action", did)
            rows = db_exec("SELECT * FROM actions WHERE dossier_id=? ORDER BY echeance", (did,), True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# =========================================================
# ONGLET 4 — CONSULTANCE & PILOTAGE
# =========================================================
def consultancy_tab():
    subs = st.tabs([
        "👥 Clients", "📋 Missions", "📝 Devis / Finance",
        "📄 Rapports", "📚 Documents", "👑 Administration", "🛡️ Audit"
    ])

    with subs[0]:
        st.subheader("👥 Clients & dossiers")
        rows = db_exec("SELECT id,nom,client,region,type_exploitation,updated_at FROM dossiers ORDER BY updated_at DESC", fetch=True)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with subs[1]:
        st.subheader("📋 Missions de consultance")
        did = st.session_state.get("dossier_id")
        if not did:
            st.warning("Sélectionnez un dossier.")
        else:
            with st.form("mission_form"):
                a,b,c = st.columns(3)
                objet = a.text_input("Objet")
                client = b.text_input("Client", value=(active_dossier() or {}).get("client",""))
                priorite = c.selectbox("Priorité", ["Normale","Haute","Critique"])
                debut = a.date_input("Début")
                echeance = b.date_input("Échéance")
                budget = c.number_input("Budget FCFA", 0.0, 1e12, 0.0)
                if st.form_submit_button("Créer mission", type="primary"):
                    mid = new_id("MIS")
                    db_exec("""INSERT INTO missions(id,dossier_id,client,objet,statut,priorite,responsable,debut,echeance,budget,notes,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (mid,did,client,objet,"Ouverte",priorite,
                             (st.session_state.get("user") or {}).get("nom",""),
                             str(debut),str(echeance),budget,"",now(),now()))
                    audit("CREATION", "mission", mid)
            rows = db_exec("SELECT * FROM missions WHERE dossier_id=? ORDER BY updated_at DESC", (did,), True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with subs[2]:
        st.subheader("📝 Devis / Finance")
        did = st.session_state.get("dossier_id")
        if did:
            rows = db_exec("SELECT * FROM finance WHERE dossier_id=? ORDER BY date_operation DESC", (did,), True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("Pour une comptabilité réglementaire, connecter ultérieurement le module financier à un système comptable validé.")

    with subs[3]:
        st.subheader("📄 Rapport professionnel")
        c = context()
        if not c["dossier_id"]:
            st.warning("Sélectionnez un dossier.")
        else:
            st.write("Le rapport utilise automatiquement le contexte central actif.")
            if st.button("Préparer le rapport", type="primary", key="prepare_report"):
                st.session_state["report_ready"] = True
            if st.session_state.get("report_ready"):
                st.markdown(f"""
                **Dossier :** {c['dossier']}  
                **Client :** {c['client'] or '—'}  
                **Parcelle :** {c['parcelle'] or '—'}  
                **Culture :** {c['culture'] or '—'}  
                **Surface :** {c['surface_ha']:.3f} ha  
                **Qualité des données :** {quality_score()}/100
                """)
                if HAS_REPORTLAB:
                    buf = io.BytesIO()
                    doc = SimpleDocTemplate(buf, pagesize=A4)
                    styles = getSampleStyleSheet()
                    story = [
                        Paragraph("YouAgronoMe — Rapport d'analyse 360°", styles["Title"]),
                        Spacer(1, 12),
                        Paragraph(f"Dossier : {c['dossier'] or '—'}", styles["Normal"]),
                        Paragraph(f"Client : {c['client'] or '—'}", styles["Normal"]),
                        Paragraph(f"Parcelle : {c['parcelle'] or '—'}", styles["Normal"]),
                        Paragraph(f"Culture : {c['culture'] or '—'}", styles["Normal"]),
                        Paragraph(f"Surface : {c['surface_ha']:.3f} ha", styles["Normal"]),
                        Paragraph(f"Qualité des données : {quality_score()}/100", styles["Normal"]),
                        Spacer(1, 12),
                        Paragraph("Synthèse", styles["Heading2"]),
                        Paragraph("Ce rapport est généré à partir des données enregistrées dans le dossier central. Les diagnostics sensibles doivent être validés par un professionnel compétent.", styles["Normal"]),
                    ]
                    doc.build(story)
                    buf.seek(0)
                    st.download_button("📥 Télécharger le rapport PDF",
                                       buf.getvalue(),
                                       f"rapport_youagronome_{datetime.now():%Y%m%d}.pdf",
                                       "application/pdf", key="download_report")

    with subs[4]:
        st.subheader("📚 Documents & références")
        for name,url in SOURCES.items():
            st.markdown(f"- **{name}** — {url}")
        st.caption("Les portails sont des références externes. Leur contenu doit être vérifié au moment de la décision.")

    with subs[5]:
        st.subheader("👑 Administration")
        user = st.session_state.get("user") or {}
        if user.get("role") != "Super-Admin":
            st.warning("Accès réservé au Super-Admin.")
        else:
            st.success("Accès Super-Admin actif.")
            with st.form("admin_add_user"):
                a,b,c = st.columns(3)
                email = a.text_input("E-mail")
                nom = b.text_input("Nom")
                role = c.selectbox("Rôle", ["Technicien", "Conseiller", "Expert", "Super-Admin"])
                zone = a.text_input("Zone")
                pwd = b.text_input("Mot de passe", type="password")
                if st.form_submit_button("Créer utilisateur"):
                    if email and pwd:
                        ph = hashlib.sha256(pwd.encode("utf-8")).hexdigest()
                        try:
                            db_exec("INSERT INTO users(email,password_hash,nom,role,zone,statut,created_at) VALUES(?,?,?,?,?,?,?)",
                                    (email.strip(),ph,nom or "Utilisateur",role,zone or "Sénégal","Actif",now()))
                            audit("CREATION", "user", email)
                            st.success("Utilisateur créé.")
                        except sqlite3.IntegrityError:
                            st.error("Cet e-mail existe déjà.")
            users = db_exec("SELECT email,nom,role,zone,statut,created_at FROM users ORDER BY created_at DESC", fetch=True)
            st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
            if st.button("🔄 Synchroniser les portails de référence", key="admin_sync_sources"):
                n = sync_official_catalog()
                st.success(f"{n} portails enregistrés dans le journal de synchronisation.")

    with subs[6]:
        st.subheader("🛡️ Audit & synchronisation")
        sync = db_exec("SELECT * FROM sync_records ORDER BY fetched_at DESC LIMIT 100", fetch=True)
        audit_rows = db_exec("SELECT * FROM audit ORDER BY created_at DESC LIMIT 200", fetch=True)
        st.markdown("### Historique synchronisation")
        st.dataframe(pd.DataFrame(sync), use_container_width=True, hide_index=True)
        st.markdown("### Journal d'audit")
        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)


# =========================================================
# APPLICATION
# =========================================================
if st.session_state.get("user") is None:
    login_box()
    st.stop()

header()

with st.sidebar:
    st.markdown("### 🔗 CONTEXTE UNIQUE")
    context_selector()
    st.markdown("---")
    c = context()
    st.write(f"**Dossier :** {c['dossier'] or '—'}")
    st.write(f"**Parcelle :** {c['parcelle'] or '—'}")
    st.write(f"**Surface :** {c['surface_ha']:.3f} ha")
    st.write(f"**GPS :** {c['latitude'] if c['latitude'] is not None else '—'}, {c['longitude'] if c['longitude'] is not None else '—'}")
    if st.button("🔄 SYNCHRONISER TOUT", type="primary", key="global_sync"):
        with st.spinner("Synchronisation du contexte, météo et références..."):
            messages = sync_all()
        for msg in messages:
            st.write("•", msg)
        st.success("Contexte synchronisé.")
    if st.button("🚪 Déconnexion", key="global_logout"):
        audit("DECONNEXION", "user", (st.session_state.get("user") or {}).get("email",""))
        st.session_state["user"] = None
        st.rerun()

# EXACTEMENT 4 GRANDS ESPACES
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 TERRAIN & DONNÉES",
    "🗺️ SIG & DIAGNOSTIC",
    "🤖 IA & DÉCISION",
    "💼 CONSULTANCE & PILOTAGE",
])

with tab1:
    terrain_tab()

with tab2:
    sig_tab()

with tab3:
    ia_tab()

with tab4:
    consultancy_tab()

st.markdown("---")
st.caption("© 2026 YouAgronoMe — Architecture HUB 360°. Données officielles, terrain, calculées et IA sont distinguées. La synchronisation ne transforme jamais une donnée historique en alerte actuelle.")
