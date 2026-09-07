# -*- coding: utf-8 -*-
"""
YouAgronoMe — PLATEFORME PROFESSIONNELLE DE CONSULTANCE AGRICOLE 360°
Refonte orientée cabinet de consultance : client -> mission -> zone d'étude -> données
-> contrôle qualité -> analyse -> décision -> plan d'action -> rapport -> suivi.

100+ fonctionnalités opérationnelles sont regroupées dans des espaces cohérents.
Aucune clé API IA n'est requise : moteur local, règles, calculs, scoring et traçabilité.
La carte permet de DESSINER LA ZONE CONCERNÉE : parcelle, périmètre d'étude,
zone d'observation, point d'eau ou zone à risque. Cette géométrie devient le
périmètre commun des analyses.

Dépendances principales :
streamlit, pandas, numpy
Optionnelles : folium, streamlit-folium, reportlab, requests
"""

from datetime import datetime, date, timedelta
import hashlib
import io
import json
import math
import os
import sqlite3
import uuid

import numpy as np
import pandas as pd
import streamlit as st

try:
    import requests
    HAS_REQUESTS = True
except Exception:
    HAS_REQUESTS = False

try:
    import folium
    from folium.plugins import Draw
    from streamlit_folium import st_folium
    HAS_MAP = True
except Exception:
    HAS_MAP = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    HAS_PDF = True
except Exception:
    HAS_PDF = False



# ============================================================
# CONTRÔLE CENTRAL DES MODULES — DROITS PAR PROFIL
# ============================================================
MODULES_AUTORISABLES = {
    "terrain": "🌍 Terrain & Données",
    "sig": "🗺️ SIG & Diagnostic",
    "ia": "🤖 IA & Décision",
    "consultance": "💼 Consultance & Pilotage",
    "agriculture": "🌾 Agriculture",
    "elevage": "🐄 Élevage",
    "aquaculture": "🐟 Aquaculture",
    "agroalimentaire": "🏭 Agroalimentaire",
    "analyses": "🧪 Analyses & Laboratoire",
    "missions": "📋 Missions",
    "finance": "💰 Devis / Finance",
    "rapports": "📄 Rapports",
    "documents": "📁 Documents",
    "alertes": "🚨 Alertes",
    "administration": "⚙️ Administration",
    "audit": "🛡️ Audit",
}

PROFILS_MODULES = {
    "Super-admin": list(MODULES_AUTORISABLES),
    "Administrateur": [m for m in MODULES_AUTORISABLES if m != "audit"],
    "Consultant": [
        "terrain", "sig", "ia", "consultance", "agriculture", "elevage",
        "aquaculture", "agroalimentaire", "analyses", "missions",
        "rapports", "documents", "alertes",
    ],
    "Technicien": [
        "terrain", "sig", "ia", "agriculture", "elevage", "aquaculture",
        "agroalimentaire", "analyses", "alertes", "rapports",
    ],
    "Observateur": ["terrain", "sig", "rapports"],
}

def modules_autorises(role=None):
    role = role or st.session_state.get("role", "Observateur")
    personnalisés = st.session_state.get("modules_autorises")
    if isinstance(personnalisés, (list, tuple, set)):
        return [m for m in personnalisés if m in MODULES_AUTORISABLES]
    return PROFILS_MODULES.get(role, PROFILS_MODULES["Observateur"])

def module_autorise(module_key):
    return module_key in modules_autorises()

def enregistrer_sync_hub(statut="OK"):
    from datetime import datetime
    st.session_state["last_sync"] = datetime.now().isoformat(timespec="seconds")
    st.session_state["sync_status"] = statut

# =========================================================
# 0. CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="YouAgronoMe — Consultance Pro 360°",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = os.getenv("YOUAGRONOME_DB", "youagronome_consultance_pro.sqlite3")
OWNER_EMAIL = os.getenv("YOUAGRONOME_OWNER_EMAIL", "iy@2012")
OWNER_PASS = os.getenv("YOUAGRONOME_OWNER_PASS", "issayoume2026")

SOURCES = {
    "ANACIM": "https://www.anacim.sn/",
    "DPV": "https://www.dpvsenegal.sn/",
    "ANCAR": "https://ancar.gouv.sn/",
    "ISRA": "https://isra.sn/",
    "SAED": "https://www.saed.sn/",
    "CSE": "https://www.cse.sn/",
    "Ministère de l'Agriculture": "https://agriculture.gouv.sn/",
    "Open-Meteo": "https://open-meteo.com/",
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

CULTURES = [
    "Riz", "Mil", "Sorgho", "Maïs", "Arachide", "Niébé", "Sésame", "Bissap",
    "Oignon", "Pomme de terre", "Tomate", "Gombo", "Chou", "Carotte",
    "Pastèque", "Melon", "Manioc", "Anacarde", "Coton", "Fonio", "Autre"
]
STAGES = [
    "Préparation", "Semis / plantation", "Levée", "Croissance",
    "Floraison", "Remplissage", "Maturation", "Récolte", "Post-récolte"
]
DOMAINS = ["Agriculture", "Élevage", "Aquaculture", "Agroalimentaire", "Sol", "Eau", "Phytosanitaire", "Économie"]
ROLES = ["Producteur", "Technicien", "Conseiller", "Expert", "Projet / ONG", "Investisseur", "Super-Admin"]

AGROZONES = {
    "Vallée du Fleuve Sénégal": {
        "regions": ["Saint-Louis", "Matam"],
        "sol": "Alluvions; secteurs hydromorphes et zones salées localisées",
        "risques": "Salinité, évapotranspiration, vent, gestion de l'eau",
    },
    "Niayes & Littoral": {
        "regions": ["Dakar", "Thiès", "Louga"],
        "sol": "Sables des Niayes; drainage généralement rapide",
        "risques": "Salinité, ravageurs, déficit hydrique, vent",
    },
    "Bassin arachidier": {
        "regions": ["Kaolack", "Fatick", "Kaffrine", "Diourbel", "Thiès"],
        "sol": "Sols sableux à sablo-argileux; fertilité variable",
        "risques": "Sécheresse, érosion, baisse de matière organique",
    },
    "Casamance": {
        "regions": ["Ziguinchor", "Sédhiou", "Kolda"],
        "sol": "Sols ferrallitiques, hydromorphes et bas-fonds",
        "risques": "Maladies, engorgement, ruissellement",
    },
    "Sénégal Oriental": {
        "regions": ["Tambacounda", "Kédougou"],
        "sol": "Sols ferrugineux/ferrallitiques",
        "risques": "Ravageurs, ruissellement, érosion",
    },
}

FEATURE_TYPES = [
    "Parcelle", "Zone d'étude", "Zone d'observation", "Point d'eau",
    "Bâtiment", "Bassin / étang", "Zone d'élevage", "Zone à risque", "Autre"
]


# =========================================================
# 1. OUTILS GÉNÉRAUX / BASE
# =========================================================
def now():
    return datetime.now().isoformat(timespec="seconds")


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def db_conn():
    con = sqlite3.connect(DB_FILE, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def db_exec(sql, params=(), *, fetch=False, many=False):
    if isinstance(params, bool):
        raise TypeError(
            "db_exec(): utilisez fetch=True comme argument nommé, pas comme paramètre positionnel."
        )
    """Executeur SQLite robuste; les options fetch/many sont nommées."""
    con = db_conn()
    try:
        cur = con.cursor()
        try:
            if many:
                cur.executemany(sql, params)
            else:
                cur.execute(sql, params)
        except sqlite3.OperationalError as exc:
            # Une base SQLite ancienne peut ne pas avoir reçu une nouvelle
            # colonne malgré CREATE TABLE IF NOT EXISTS.
            msg = str(exc).lower()
            if "no such column" in msg:
                con.rollback()
                ensure_sqlite_schema()
                if many:
                    cur.executemany(sql, params)
                else:
                    cur.execute(sql, params)
            else:
                raise
        rows = cur.fetchall() if fetch else None
        con.commit()
        return [dict(r) for r in rows] if rows is not None else cur.lastrowid
    finally:
        con.close()


def sha256(value):
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()



def ensure_sqlite_schema():
    """Met à niveau une base SQLite existante sans supprimer les données.
    CREATE TABLE IF NOT EXISTS ne modifie pas une table déjà créée : les
    colonnes ajoutées dans les nouvelles versions doivent donc être migrées.
    """
    migrations = {
        "clients": {
            "updated_at": "TEXT",
            "created_at": "TEXT",
            "nom": "TEXT",
            "telephone": "TEXT",
            "email": "TEXT",
            "organisation": "TEXT",
            "adresse": "TEXT",
            "region": "TEXT",
            "notes": "TEXT",
        },
        "dossiers": {
            "updated_at": "TEXT",
            "created_at": "TEXT",
            "client_id": "TEXT",
            "nom": "TEXT",
            "type_exploitation": "TEXT",
            "region": "TEXT",
            "commune": "TEXT",
            "village": "TEXT",
            "latitude": "REAL",
            "longitude": "REAL",
            "notes": "TEXT",
            "statut": "TEXT DEFAULT 'Actif'",
        },
    }

    con = db_conn()
    try:
        cur = con.cursor()
        for table, columns in migrations.items():
            existing = {
                row[1] for row in cur.execute(f'PRAGMA table_info("{table}")').fetchall()
            }
            if not existing:
                continue
            for column, definition in columns.items():
                if column not in existing:
                    cur.execute(
                        f'ALTER TABLE "{table}" ADD COLUMN "{column}" {definition}'
                    )

        # Répare les anciennes lignes qui n'ont pas de date de mise à jour.
        cur.execute(
            "UPDATE clients SET updated_at=COALESCE(updated_at, created_at, ?) "
            "WHERE updated_at IS NULL OR TRIM(updated_at)=''",
            (now(),),
        )
        cur.execute(
            "UPDATE clients SET created_at=COALESCE(created_at, ?) "
            "WHERE created_at IS NULL OR TRIM(created_at)=''",
            (now(),),
        )
        cur.execute(
            "UPDATE dossiers SET updated_at=COALESCE(updated_at, created_at, ?) "
            "WHERE updated_at IS NULL OR TRIM(updated_at)=''",
            (now(),),
        )
        cur.execute(
            "UPDATE dossiers SET created_at=COALESCE(created_at, ?) "
            "WHERE created_at IS NULL OR TRIM(created_at)=''",
            (now(),),
        )
        con.commit()
    finally:
        con.close()

def init_db():
    con = db_conn()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        email TEXT PRIMARY KEY, password_hash TEXT, nom TEXT, role TEXT,
        zone TEXT, statut TEXT DEFAULT 'Actif', created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS clients(
        id TEXT PRIMARY KEY, nom TEXT, telephone TEXT, email TEXT, organisation TEXT,
        adresse TEXT, region TEXT, notes TEXT, created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS dossiers(
        id TEXT PRIMARY KEY, client_id TEXT, nom TEXT, type_exploitation TEXT,
        region TEXT, commune TEXT, village TEXT, latitude REAL, longitude REAL,
        notes TEXT, statut TEXT DEFAULT 'Actif', created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS parcelles(
        id TEXT PRIMARY KEY, dossier_id TEXT, nom TEXT, culture TEXT, stade TEXT,
        surface_ha REAL DEFAULT 0, perimeter_m REAL DEFAULT 0, latitude REAL,
        longitude REAL, geometry_json TEXT DEFAULT '[]', feature_type TEXT DEFAULT 'Parcelle',
        source_type TEXT DEFAULT 'Terrain', confidence REAL DEFAULT 0.9,
        validation_status TEXT DEFAULT 'À vérifier', notes TEXT,
        created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS observations(
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, domaine TEXT,
        type_observation TEXT, description TEXT, gravite TEXT, incidence REAL,
        surface_affectee_ha REAL, latitude REAL, longitude REAL, photo_name TEXT,
        date_observation TEXT, source_type TEXT DEFAULT 'Terrain',
        confidence REAL DEFAULT 0.8, validation_status TEXT DEFAULT 'À vérifier',
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS analyses(
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, type_analyse TEXT,
        parametre TEXT, valeur REAL, unite TEXT, methode TEXT, laboratoire TEXT,
        date_analyse TEXT, source_type TEXT DEFAULT 'Laboratoire',
        confidence REAL DEFAULT 0.9, validation_status TEXT DEFAULT 'À vérifier',
        notes TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS cultures(
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, culture TEXT,
        variete TEXT, date_semis TEXT, date_recolte_prevue TEXT, irrigation TEXT,
        rendement_cible REAL, rendement_reel REAL, fertilisation TEXT,
        protection TEXT, notes TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS livestock(
        id TEXT PRIMARY KEY, dossier_id TEXT, espece TEXT, categorie TEXT,
        effectif INTEGER, poids_moyen REAL, alimentation TEXT, mortalite INTEGER,
        vaccination TEXT, reproduction TEXT, date_suivi TEXT, notes TEXT
    );
    CREATE TABLE IF NOT EXISTS aquaculture(
        id TEXT PRIMARY KEY, dossier_id TEXT, unite TEXT, espece TEXT,
        volume_m3 REAL, densite REAL, oxygene REAL, ph REAL, temperature REAL,
        mortalite INTEGER, aliment_kg REAL, poids_moyen_g REAL, date_suivi TEXT, notes TEXT
    );
    CREATE TABLE IF NOT EXISTS agrofood(
        id TEXT PRIMARY KEY, dossier_id TEXT, produit TEXT, quantite REAL,
        unite TEXT, transformation TEXT, stockage TEXT, pertes_pct REAL,
        qualite TEXT, lot TEXT, date_operation TEXT, notes TEXT
    );
    CREATE TABLE IF NOT EXISTS assets(
        id TEXT PRIMARY KEY, dossier_id TEXT, type_asset TEXT, nom TEXT,
        quantite REAL, unite TEXT, etat TEXT, valeur_fcfa REAL, notes TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS missions(
        id TEXT PRIMARY KEY, dossier_id TEXT, client_id TEXT, objet TEXT, type_mission TEXT,
        statut TEXT, priorite TEXT, responsable TEXT, date_debut TEXT, echeance TEXT,
        budget_fcfa REAL, avancement REAL DEFAULT 0, notes TEXT, created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS actions(
        id TEXT PRIMARY KEY, dossier_id TEXT, mission_id TEXT, domaine TEXT, titre TEXT,
        responsable TEXT, echeance TEXT, priorite TEXT, statut TEXT, cout_estime REAL,
        preuve TEXT, notes TEXT, created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS finance(
        id TEXT PRIMARY KEY, dossier_id TEXT, mission_id TEXT, type_operation TEXT,
        categorie TEXT, libelle TEXT, montant_fcfa REAL, date_operation TEXT,
        statut TEXT, reference TEXT, notes TEXT
    );
    CREATE TABLE IF NOT EXISTS quotes(
        id TEXT PRIMARY KEY, client_id TEXT, dossier_id TEXT, reference TEXT,
        objet TEXT, montant_ht REAL, taxes REAL, total REAL, statut TEXT,
        date_creation TEXT, date_validite TEXT, notes TEXT
    );
    CREATE TABLE IF NOT EXISTS reports(
        id TEXT PRIMARY KEY, dossier_id TEXT, mission_id TEXT, type_rapport TEXT,
        titre TEXT, contenu TEXT, confidence REAL, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS documents(
        id TEXT PRIMARY KEY, dossier_id TEXT, mission_id TEXT, nom TEXT,
        type_document TEXT, chemin TEXT, description TEXT, source TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS alerts(
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, domaine TEXT,
        niveau TEXT, titre TEXT, message TEXT, source TEXT, due_date TEXT,
        statut TEXT DEFAULT 'Ouverte', created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS gis_features(
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, type_feature TEXT,
        nom TEXT, geometry_json TEXT, surface_ha REAL, perimeter_m REAL,
        latitude REAL, longitude REAL, source TEXT, confidence REAL,
        validation_status TEXT, notes TEXT, created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS weather_cache(
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, latitude REAL, longitude REAL,
        payload_json TEXT, fetched_at TEXT, source TEXT
    );
    CREATE TABLE IF NOT EXISTS sync_log(
        id TEXT PRIMARY KEY, dossier_id TEXT, source TEXT, type_data TEXT,
        status TEXT, message TEXT, fetched_at TEXT, duration_ms INTEGER
    );
    CREATE TABLE IF NOT EXISTS audit(
        id TEXT PRIMARY KEY, user_email TEXT, action TEXT, entity TEXT,
        entity_id TEXT, details TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS ai_history(
        id TEXT PRIMARY KEY, dossier_id TEXT, parcelle_id TEXT, question TEXT,
        answer TEXT, confidence REAL, evidence TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS entretiens(
        id TEXT PRIMARY KEY, dossier_id TEXT, client_id TEXT, type_entretien TEXT,
        question TEXT, reponse TEXT, domaine TEXT, auteur TEXT,
        ordre INTEGER DEFAULT 0, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS settings(
        key TEXT PRIMARY KEY, value TEXT
    );
    """)
    con.commit()
    con.close()

    if not db_exec("SELECT email FROM users WHERE lower(email)=lower(?)", (OWNER_EMAIL,), fetch=True):
        db_exec(
            "INSERT INTO users(email,password_hash,nom,role,zone,statut,created_at) VALUES(?,?,?,?,?,?,?)",
            (OWNER_EMAIL, sha256(OWNER_PASS), "Administrateur Principal", "Super-Admin", "National", "Actif", now())
        )


init_db()
ensure_sqlite_schema()

def ensure_owner_account():
    rows = db_exec(
        "SELECT email, role, statut FROM users WHERE lower(email)=lower(?)",
        (OWNER_EMAIL,),
        fetch=True
    )
    if not rows:
        db_exec(
            """INSERT INTO users(email,password_hash,nom,role,zone,statut,created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (
                OWNER_EMAIL, sha256(OWNER_PASS), "Administrateur Principal",
                "Super-Admin", "National", "Actif", now()
            )
        )
    elif rows[0].get("role") != "Super-Admin" or rows[0].get("statut") != "Actif":
        db_exec(
            "UPDATE users SET role=?, statut=? WHERE lower(email)=lower(?)",
            ("Super-Admin", "Actif", OWNER_EMAIL)
        )

ensure_owner_account()


def audit(action, entity="", entity_id="", details=""):
    user = st.session_state.get("user") or {}
    db_exec(
        "INSERT INTO audit(id,user_email,action,entity,entity_id,details,created_at) VALUES(?,?,?,?,?,?,?)",
        (new_id("AUD"), user.get("email", "anonymous"), action, entity, entity_id, str(details), now())
    )


# =========================================================
# 2. ÉTAT ET CONTEXTE UNIQUE
# =========================================================
def init_state():
    defaults = {
        "user": None,
        "client_id": None,
        "dossier_id": None,
        "parcelle_id": None,
        "zone_feature_id": None,
        "weather": None,
        "sync_status": "Jamais synchronisé",
        "sync_time": None,
        "last_ai": "",
        "selected_mission": None,
        "map_nonce": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def active_client():
    cid = st.session_state.get("client_id")
    rows = db_exec("SELECT * FROM clients WHERE id=?", (cid,), fetch=True) if cid else []
    return rows[0] if rows else None


def active_dossier():
    did = st.session_state.get("dossier_id")
    rows = db_exec("SELECT * FROM dossiers WHERE id=?", (did,), fetch=True) if did else []
    return rows[0] if rows else None


def active_parcelle():
    pid = st.session_state.get("parcelle_id")
    rows = db_exec("SELECT * FROM parcelles WHERE id=?", (pid,), fetch=True) if pid else []
    return rows[0] if rows else None


def active_zone():
    zid = st.session_state.get("zone_feature_id")
    rows = db_exec("SELECT * FROM gis_features WHERE id=?", (zid,), fetch=True) if zid else []
    return rows[0] if rows else None


def load_geometry(obj):
    try:
        return json.loads(obj or "[]")
    except Exception:
        return []


def context():
    d = active_dossier() or {}
    p = active_parcelle() or {}
    z = active_zone() or {}
    geom = load_geometry(z.get("geometry_json")) if z else load_geometry(p.get("geometry_json"))
    return {
        "client_id": d.get("client_id"),
        "client": (active_client() or {}).get("nom"),
        "dossier_id": d.get("id"),
        "dossier": d.get("nom"),
        "region": d.get("region"),
        "commune": d.get("commune"),
        "village": d.get("village"),
        "parcelle_id": p.get("id"),
        "parcelle": p.get("nom"),
        "culture": p.get("culture"),
        "stade": p.get("stade"),
        "surface_ha": float(p.get("surface_ha") or 0),
        "latitude": p.get("latitude", d.get("latitude")),
        "longitude": p.get("longitude", d.get("longitude")),
        "zone_id": z.get("id"),
        "zone_nom": z.get("nom"),
        "zone_type": z.get("type_feature"),
        "zone_surface_ha": float(z.get("surface_ha") or 0),
        "zone_geometry": geom,
    }


def set_active_dossier(did):
    st.session_state["dossier_id"] = did
    st.session_state["parcelle_id"] = None
    st.session_state["zone_feature_id"] = None
    d = active_dossier()
    if d:
        st.session_state["client_id"] = d.get("client_id")
    audit("SELECTION", "dossier", did)


# =========================================================
# 3. GÉOMÉTRIE : ZONE CONCERNÉE
# =========================================================
def haversine_m(a, b):
    R = 6371000.0
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    q = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(min(1, math.sqrt(q)))


def polygon_area_ha(coords):
    if not coords or len(coords) < 3:
        return 0.0
    lat0 = math.radians(sum(float(p[0]) for p in coords) / len(coords))
    R = 6371000.0
    xy = []
    for lat, lon in coords:
        xy.append((math.radians(float(lon))*R*math.cos(lat0), math.radians(float(lat))*R))
    area = 0.0
    for i in range(len(xy)):
        x1, y1 = xy[i]
        x2, y2 = xy[(i+1) % len(xy)]
        area += x1*y2 - x2*y1
    return abs(area) / 2 / 10000


def polygon_perimeter_m(coords):
    if len(coords) < 2:
        return 0.0
    return sum(haversine_m(coords[i], coords[(i+1) % len(coords)]) for i in range(len(coords)))


def centroid(coords):
    if not coords:
        return None, None
    return sum(p[0] for p in coords)/len(coords), sum(p[1] for p in coords)/len(coords)


def drawing_to_coords(drawing):
    if not drawing:
        return []
    g = drawing.get("geometry", {})
    typ, c = g.get("type"), g.get("coordinates")
    if typ == "Polygon" and c:
        return [[float(y), float(x)] for x, y in c[0]]
    if typ == "MultiPolygon" and c:
        return [[float(y), float(x)] for x, y in c[0][0]]
    return []


def coords_inside_bbox(coords):
    return bool(coords and len(coords) >= 3)


def save_zone(coords, feature_type, name, dossier_id, parcelle_id=None):
    if not coords_inside_bbox(coords):
        return None
    area = polygon_area_ha(coords)
    perim = polygon_perimeter_m(coords)
    lat, lon = centroid(coords)
    fid = new_id("GIS")
    db_exec("""INSERT INTO gis_features
        (id,dossier_id,parcelle_id,type_feature,nom,geometry_json,surface_ha,perimeter_m,
         latitude,longitude,source,confidence,validation_status,notes,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (fid, dossier_id, parcelle_id, feature_type, name, json.dumps(coords),
         area, perim, lat, lon, "Terrain/GPS", 0.98, "À valider",
         "Géométrie dessinée par l'utilisateur.", now(), now()))
    audit("CREATION_GEOMETRIE", "gis_features", fid, {"area_ha": area, "perimeter_m": perim})
    return fid


def map_for_context(lat, lon, height=560, key="main_map", allow_draw=False):
    m = folium.Map(location=[lat, lon], zoom_start=14, control_scale=True, tiles="OpenStreetMap")
    if allow_draw:
        Draw(
            export=True,
            draw_options={
                "polyline": False, "rectangle": True, "circle": False,
                "circlemarker": False, "marker": True, "polygon": True
            },
            edit_options={"edit": True, "remove": True},
        ).add_to(m)
    return st_folium(m, width=None, height=height, key=key)


# =========================================================
# 4. QUALITÉ, CONFIANCE, RISQUE
# =========================================================
def data_quality():
    c = context()
    score = 100
    checks = []

    def check(label, ok, penalty, action):
        nonlocal score
        if not ok:
            score -= penalty
        checks.append({"Contrôle": label, "État": "OK" if ok else "À corriger", "Impact": penalty, "Action": action})

    check("Client identifié", bool(c["client_id"]), 8, "Créer/sélectionner le client")
    check("Dossier actif", bool(c["dossier_id"]), 15, "Créer/sélectionner le dossier")
    check("Parcelle active", bool(c["parcelle_id"]), 10, "Créer une parcelle")
    check("Coordonnées GPS", c["latitude"] is not None and c["longitude"] is not None, 10, "Renseigner le GPS")
    check("Zone d'étude délimitée", bool(c["zone_geometry"]), 18, "Dessiner la zone concernée")
    check("Surface valide", c["zone_surface_ha"] > 0 or c["surface_ha"] > 0, 10, "Définir la surface")
    check("Culture renseignée", bool(c["culture"]), 6, "Renseigner la culture")
    did = c["dossier_id"]
    obs_n = len(db_exec("SELECT id FROM observations WHERE dossier_id=?", (did,), fetch=True)) if did else 0
    ana_n = len(db_exec("SELECT id FROM analyses WHERE dossier_id=?", (did,), fetch=True)) if did else 0
    check("Observations terrain", obs_n > 0, 8, "Ajouter une observation")
    check("Analyses disponibles", ana_n > 0, 5, "Ajouter une analyse ou justifier l'absence")
    return max(0, min(100, score)), checks


def confidence_from_sources():
    q, _ = data_quality()
    c = context()
    source_bonus = 0
    if c["zone_geometry"]:
        source_bonus += 0.10
    if c["dossier_id"]:
        source_bonus += 0.05
    return min(0.98, 0.35 + q/200 + source_bonus)


def risk_score():
    c = context()
    risk = 20
    if not c["zone_geometry"]:
        risk += 15
    if not c["culture"]:
        risk += 5
    obs = db_exec("SELECT gravite,incidence FROM observations WHERE dossier_id=? ORDER BY created_at DESC LIMIT 50",
                  (c["dossier_id"],), fetch=True) if c["dossier_id"] else []
    for o in obs:
        risk += {"Faible": 2, "Moyenne": 7, "Élevée": 14, "Critique": 25, "Information": 0}.get(o.get("gravite"), 0)
        risk += min(10, float(o.get("incidence") or 0)/10)
    return int(min(100, risk))


# =========================================================
# 5. SYNCHRONISATION
# =========================================================
def log_sync(source, dtype, status, message, dossier_id=None, duration=0):
    db_exec("""INSERT INTO sync_log(id,dossier_id,source,type_data,status,message,fetched_at,duration_ms)
               VALUES(?,?,?,?,?,?,?,?)""",
            (new_id("SYN"), dossier_id or context()["dossier_id"], source, dtype,
             status, message, now(), int(duration)))


def sync_weather():
    c = context()
    if not HAS_REQUESTS:
        raise RuntimeError("requests n'est pas installé.")
    if c["latitude"] is None or c["longitude"] is None:
        raise ValueError("Coordonnées GPS manquantes.")
    import time
    t0 = time.time()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": float(c["latitude"]), "longitude": float(c["longitude"]),
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "forecast_days": 7, "timezone": "auto"
    }
    r = requests.get(url, params=params, timeout=12)
    r.raise_for_status()
    data = r.json()
    st.session_state["weather"] = data
    db_exec("""INSERT INTO weather_cache(id,dossier_id,parcelle_id,latitude,longitude,payload_json,fetched_at,source)
               VALUES(?,?,?,?,?,?,?,?)""",
            (new_id("WTH"), c["dossier_id"], c["parcelle_id"], c["latitude"], c["longitude"],
             json.dumps(data), now(), "Open-Meteo"))
    log_sync("Open-Meteo", "Météo", "OK", "Prévision 7 jours récupérée.", c["dossier_id"], (time.time()-t0)*1000)
    return data


def sync_reference_catalog():
    did = context()["dossier_id"]
    for name, url in SOURCES.items():
        log_sync(name, "Référentiel", "RÉFÉRENCE",
                 f"Portail enregistré; vérifier le contenu au moment de la décision. {url}", did)
    return len(SOURCES)


def sync_all():
    c = context()
    results = []
    if not c["dossier_id"]:
        return ["Aucun dossier actif."]
    try:
        sync_weather()
        results.append("Météo synchronisée")
    except Exception as exc:
        results.append(f"Météo non disponible : {exc}")
        log_sync("Open-Meteo", "Météo", "ERREUR", str(exc), c["dossier_id"])
    n = sync_reference_catalog()
    results.append(f"{n} sources institutionnelles enregistrées")
    q, _ = data_quality()
    st.session_state["sync_status"] = "Synchronisé"
    st.session_state["sync_time"] = now()
    audit("SYNCHRONISATION_GLOBALE", "hub", c["dossier_id"], results)
    return results


# =========================================================
# 6. MOTEUR DE DÉCISION LOCAL
# =========================================================
def local_expert(question, actor="Technicien"):
    c = context()
    q = (question or "").lower()
    zone = next((z for z, v in AGROZONES.items() if c["region"] in v["regions"]), None)
    zinfo = AGROZONES.get(zone or "", {})
    quality, checks = data_quality()
    risk = risk_score()

    hypotheses = []
    actions = [
        "Confirmer le problème sur plusieurs points représentatifs de la zone délimitée.",
        "Comparer observation actuelle, historique, sol/eau et conditions météo.",
        "Documenter les preuves : photos, dates, localisation et incidence.",
        "Définir un contrôle de suivi avec échéance et responsable.",
    ]
    if any(x in q for x in ["jaun", "chlorose", "pale", "pâle"]):
        hypotheses += ["Carence ou déséquilibre nutritionnel", "Excès d'eau / problème racinaire", "Stress hydrique ou autre facteur environnemental"]
        actions.insert(1, "Vérifier pH, disponibilité des éléments, humidité et état racinaire avant correction.")
    if any(x in q for x in ["insect", "chenille", "puceron", "ravageur"]):
        hypotheses += ["Pression de ravageurs", "Dommages non entomologiques à différencier"]
        actions.insert(1, "Quantifier l'incidence sur plusieurs placettes et rechercher les stades du ravageur.")
    if any(x in q for x in ["tache", "maladie", "flétr", "pourrit"]):
        hypotheses += ["Maladie potentiellement infectieuse", "Stress abiotique à différencier"]
        actions.insert(1, "Comparer plants sains/atteints et rechercher une progression spatiale et temporelle.")
    if any(x in q for x in ["eau", "irrig", "sécher", "pluie"]):
        hypotheses += ["Stress hydrique", "Irrigation non uniforme", "Drainage insuffisant"]
        actions.insert(1, "Contrôler humidité, uniformité d'irrigation, drainage et pluviométrie locale.")
    if not hypotheses:
        hypotheses = ["Hypothèse indéterminée : données supplémentaires nécessaires."]

    confidence = min(0.97, 0.35 + quality/200 + (0.10 if c["zone_geometry"] else 0))
    evidence = [
        f"Qualité du dossier : {quality}/100",
        f"Risque séparé de la confiance : {risk}/100",
        f"Zone d'étude : {c['zone_nom'] or 'non délimitée'}",
        f"Observations : {len(db_exec('SELECT id FROM observations WHERE dossier_id=?', (c['dossier_id'],), fetch=True)) if c['dossier_id'] else 0}",
        f"Analyses : {len(db_exec('SELECT id FROM analyses WHERE dossier_id=?', (c['dossier_id'],), fetch=True)) if c['dossier_id'] else 0}",
        "Météo : synchronisée" if st.session_state.get("weather") else "Météo : non synchronisée",
    ]
    text = f"""## 🧠 Avis expert local — {actor}

**Contexte**
- Client : {c['client'] or '—'}
- Dossier : {c['dossier'] or '—'}
- Parcelle : {c['parcelle'] or '—'}
- Zone étudiée : {c['zone_nom'] or 'non délimitée'} ({c['zone_surface_ha']:.3f} ha)
- Culture : {c['culture'] or '—'} · Stade : {c['stade'] or '—'}
- Zone agroécologique indicative : {zone or 'à déterminer'}

**Hypothèses à tester**
{chr(10).join('- '+h for h in hypotheses)}

**Plan de vérification**
{chr(10).join(f'{i+1}. {a}' for i,a in enumerate(actions))}

**Confiance de l'analyse :** {confidence*100:.0f} %
**Qualité des données :** {quality}/100
**Risque estimé :** {risk}/100

**Preuves / limites**
{chr(10).join('- '+e for e in evidence)}

> Cet avis est un outil d'aide à la décision. Il ne transforme pas une hypothèse en diagnostic officiel et ne remplace pas un laboratoire, un technicien compétent ou les organismes officiels.
"""
    return text, confidence, evidence


# =========================================================
# 7. AUTHENTIFICATION
# =========================================================
def login():
    st.markdown("## 🔐 Accès au cabinet YouAgronoMe")
    st.caption("Les mots de passe sont stockés sous forme de hash.")
    a, b = st.columns(2)
    email = a.text_input("Identifiant", key="login_email")
    password = b.text_input("Mot de passe", type="password", key="login_password")
    if st.button("Se connecter", type="primary", key="login_button"):
        rows = db_exec(
            "SELECT * FROM users WHERE lower(email)=lower(?) AND password_hash=? AND statut='Actif'",
            (email.strip(), sha256(password)), fetch=True
        )
        if rows:
            st.session_state["user"] = rows[0]
            audit("CONNEXION", "user", rows[0]["email"])
            st.rerun()
        else:
            st.error("Identifiants invalides ou compte inactif.")


# =========================================================
# 8. SÉLECTEUR GLOBAL CLIENT / DOSSIER / PARCELLE / ZONE
# =========================================================
def global_selector():
    st.markdown("### 🎯 Dossier de consultance actif")
    clients = db_exec("SELECT * FROM clients ORDER BY COALESCE(updated_at, created_at, '') DESC, COALESCE(created_at, '') DESC", fetch=True)
    client_labels = ["➕ Nouveau client"] + [f"{x['id']} · {x['nom']}" for x in clients]
    current_client = st.session_state.get("client_id")
    cidx = next((i+1 for i,x in enumerate(clients) if x["id"] == current_client), 0)
    cc = st.selectbox("Client", client_labels, index=cidx, key="global_client")

    if cc == "➕ Nouveau client":
        with st.form("global_new_client"):
            nom = st.text_input("Nom / exploitation")
            tel = st.text_input("Téléphone")
            email = st.text_input("E-mail")
            org = st.text_input("Organisation")
            region = st.selectbox("Région", list(REGIONS_COORD))
            if st.form_submit_button("Créer le client"):
                cid = new_id("CLI")
                db_exec("""INSERT INTO clients(id,nom,telephone,email,organisation,adresse,region,notes,created_at,updated_at)
                           VALUES(?,?,?,?,?,?,?,?,?,?)""",
                        (cid, nom or "Client sans nom", tel, email, org, "", region, "", now(), now()))
                st.session_state["client_id"] = cid
                audit("CREATION", "client", cid)
                st.rerun()
    else:
        cid = cc.split(" · ", 1)[0]
        if cid != current_client:
            st.session_state["client_id"] = cid
            st.session_state["dossier_id"] = None
            st.session_state["parcelle_id"] = None
            st.session_state["zone_feature_id"] = None

    cid = st.session_state.get("client_id")
    if cid:
        dossiers = db_exec("SELECT * FROM dossiers WHERE client_id=? ORDER BY COALESCE(updated_at, created_at, '') DESC", (cid,), fetch=True)
        labels = ["➕ Nouveau dossier"] + [f"{x['id']} · {x['nom']}" for x in dossiers]
        cur = st.session_state.get("dossier_id")
        didx = next((i+1 for i,x in enumerate(dossiers) if x["id"] == cur), 0)
        dd = st.selectbox("Dossier / mission d'étude", labels, index=didx, key="global_dossier")
        if dd == "➕ Nouveau dossier":
            with st.form("global_new_dossier"):
                nom = st.text_input("Nom du dossier")
                typ = st.selectbox("Type", ["Agriculture", "Élevage", "Aquaculture", "Agroalimentaire", "Mixte"])
                region = st.selectbox("Région", list(REGIONS_COORD))
                commune = st.text_input("Commune")
                village = st.text_input("Village")
                if st.form_submit_button("Créer le dossier", type="primary"):
                    did = new_id("DOS")
                    lat, lon = REGIONS_COORD[region]
                    db_exec("""INSERT INTO dossiers
                        (id,client_id,nom,type_exploitation,region,commune,village,latitude,longitude,notes,created_at,updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (did,cid,nom or "Dossier sans nom",typ,region,commune,village,lat,lon,"",now(),now()))
                    set_active_dossier(did)
                    st.rerun()
        else:
            did = dd.split(" · ", 1)[0]
            if did != st.session_state.get("dossier_id"):
                set_active_dossier(did)

        did = st.session_state.get("dossier_id")
        if did:
            pars = db_exec("SELECT * FROM parcelles WHERE dossier_id=? ORDER BY COALESCE(updated_at, created_at, '') DESC", (did,), fetch=True)
            plabels = ["— Aucune parcelle sélectionnée —"] + [f"{x['id']} · {x['nom']} ({x['surface_ha']:.2f} ha)" for x in pars]
            curp = st.session_state.get("parcelle_id")
            pidx = next((i+1 for i,x in enumerate(pars) if x["id"] == curp), 0)
            pp = st.selectbox("Unité / parcelle", plabels, index=pidx, key="global_parcelle")
            if pp.startswith("—"):
                st.session_state["parcelle_id"] = None
            else:
                st.session_state["parcelle_id"] = pp.split(" · ", 1)[0]


# =========================================================
# 9. EN-TÊTE PROFESSIONNEL
# =========================================================
def professional_header():
    """En-tête du cabinet : identité, contexte actif et indicateurs essentiels."""
    st.markdown("""
    <style>
    .block-container{padding-top:1.15rem;padding-bottom:2.5rem;max-width:1500px}
    [data-testid="stSidebar"]{border-right:1px solid #dfe8e2}
    .ya-hero{background:linear-gradient(135deg,#103d2c 0%,#146c43 58%,#198754 100%);color:#fff;border-radius:22px;padding:24px 28px;box-shadow:0 10px 30px rgba(16,61,44,.16);margin-bottom:14px}
    .ya-hero h1{margin:0;color:#fff!important;font-size:2rem;letter-spacing:-.03em}
    .ya-hero p{margin:7px 0 0;color:#e9f6ef;font-size:.96rem}
    .ya-strip{display:flex;gap:8px;flex-wrap:wrap;margin-top:15px}
    .ya-pill{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);border-radius:999px;padding:6px 11px;font-size:.81rem}
    .ya-section{background:#f5f8f6;border:1px solid #dfe8e2;border-radius:16px;padding:12px 15px;margin:8px 0 14px}
    .ya-section-title{font-weight:750;color:#18322a;font-size:1.02rem}
    .ya-kicker{color:#66756e;font-size:.84rem;margin-top:2px}
    div[data-testid="stTabs"] button{font-weight:700;font-size:.95rem} .stSelectbox{margin-bottom:.4rem}
    </style>
    """, unsafe_allow_html=True)
    c=context(); q,_=data_quality(); risk=risk_score()
    surface=c["zone_surface_ha"] or c["surface_ha"] or 0
    st.markdown(f"""
    <div class='ya-hero'>
      <h1>🌾 YouAgronoMe</h1>
      <p>Cabinet numérique de consultance agricole 360° — qualifier, étudier, décider, suivre.</p>
      <div class='ya-strip'>
        <span class='ya-pill'>👤 {c['client'] or 'Client non sélectionné'}</span>
        <span class='ya-pill'>📁 {c['dossier'] or 'Dossier non sélectionné'}</span>
        <span class='ya-pill'>📍 {c['zone_nom'] or 'Zone non délimitée'}</span>
        <span class='ya-pill'>📐 {surface:.2f} ha</span>
        <span class='ya-pill'>🛡️ Qualité {q}/100</span>
        <span class='ya-pill'>⚠️ Risque {risk}/100</span>
      </div>
    </div>
    """, unsafe_allow_html=True)



# =========================================================
# INTERFACE V9 — ORGANISATION SANS SURCHARGE
# =========================================================
def compact_context():
    c = context()
    st.markdown(
        f"**Contexte unique :** 👤 {c['client'] or '—'}  ›  📁 {c['dossier'] or '—'}  ›  "
        f"📍 {c['parcelle'] or c['zone_nom'] or 'Zone non définie'}"
    )

def interview_questions(domain):
    base = [
        ("Situation", "Pouvez-vous décrire votre exploitation et le problème principal rencontré actuellement ?"),
        ("Historique", "Depuis quand le problème existe-t-il et qu'est-ce qui s'est passé juste avant son apparition ?"),
        ("Production", "Quelle culture, quel élevage ou quelle production est concerné(e), et à quel stade ?"),
        ("Pratiques", "Quelles pratiques avez-vous utilisées récemment : irrigation, fertilisation, alimentation, traitements ou autres interventions ?"),
        ("Observations", "Qu'avez-vous observé précisément sur le terrain, les animaux, l'eau ou les produits ?"),
        ("Impact", "Quelle est l'importance du problème : surface, nombre d'animaux, volume de production ou pertes estimées ?"),
        ("Actions", "Qu'avez-vous déjà essayé de faire et avec quel résultat ?"),
        ("Besoin", "Quelle aide ou quelle décision attendez-vous de YouAgronoMe ?"),
    ]
    if domain == "Élevage":
        base[2] = ("Cheptel", "Quelle espèce, catégorie, effectif et état général sont concernés ?")
    elif domain == "Aquaculture":
        base[2] = ("Bassin", "Quelle espèce, quel bassin, quel volume et quelle densité sont concernés ?")
    elif domain == "Agroalimentaire":
        base[2] = ("Produit", "Quel produit, quel lot, quelle quantité et quelle étape de transformation sont concernés ?")
    return base

def save_interview_answer(domain, question, answer, order_no):
    c = context()
    if not c["dossier_id"]:
        return False
    user = st.session_state.get("user") or {}
    db_exec(
        """INSERT INTO entretiens
        (id,dossier_id,client_id,type_entretien,question,reponse,domaine,auteur,ordre,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (new_id("ENT"), c["dossier_id"], c["client_id"], "Entretien agricole",
         question, answer, domain, user.get("nom","Utilisateur"), order_no, now())
    )
    audit("ENTRETIEN_REPONSE", "entretien", c["dossier_id"], {"domaine": domain, "ordre": order_no})
    return True

def interview_summary_text():
    c = context()
    rows = db_exec(
        "SELECT * FROM entretiens WHERE dossier_id=? ORDER BY ordre, created_at",
        (c["dossier_id"],), fetch=True
    ) if c["dossier_id"] else []
    if not rows:
        return ""
    lines = [
        "COMPTE RENDU D'ENTRETIEN — YouAgronoMe",
        f"Client : {c['client'] or '—'}",
        f"Dossier : {c['dossier'] or '—'}",
        f"Zone / parcelle : {c['parcelle'] or c['zone_nom'] or '—'}",
        f"Date de génération : {now()}",
        "",
    ]
    for i, r in enumerate(rows, 1):
        lines += [
            f"{i}. {r['domaine']} — {r['question']}",
            f"Réponse : {r['reponse'] or 'Aucune réponse'}",
            ""
        ]
    return "\n".join(lines)

def build_interview_pdf():
    if not HAS_PDF:
        return None
    text_report = interview_summary_text()
    if not text_report:
        return None
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = [Paragraph("YouAgronoMe — Compte rendu d'entretien agricole", styles["Title"]), Spacer(1, 12)]
    for line in text_report.splitlines():
        if not line.strip():
            story.append(Spacer(1, 7))
        else:
            safe = (line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
            story.append(Paragraph(safe, styles["Normal"]))
            story.append(Spacer(1, 4))
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

def entretien_space():
    compact_context()
    st.subheader("💬 Entretien avec l'agriculteur / producteur")
    c = context()
    if not c["dossier_id"]:
        st.info("Sélectionnez d'abord un dossier dans la barre latérale.")
        return

    domain = st.selectbox(
        "Domaine de l'entretien",
        ["Agriculture", "Élevage", "Aquaculture", "Agroalimentaire"],
        key="entretien_domain"
    )
    questions = interview_questions(domain)
    idx = st.session_state.get("entretien_index", 0)
    idx = min(idx, len(questions)-1)
    label, question = questions[idx]

    st.markdown(f"### Question {idx+1}/{len(questions)} — {label}")
    st.info(question)
    answer = st.text_area(
        "Réponse de l'agriculteur / interlocuteur",
        key=f"entretien_answer_{idx}",
        height=130,
        placeholder="Saisissez fidèlement la réponse donnée sur le terrain."
    )

    b1,b2,b3 = st.columns(3)
    with b1:
        if st.button("💾 Enregistrer la réponse", type="primary", key=f"save_entretien_{idx}"):
            if not answer.strip():
                st.warning("Saisissez la réponse avant d'enregistrer.")
            else:
                save_interview_answer(domain, question, answer.strip(), idx+1)
                st.session_state["entretien_index"] = min(idx+1, len(questions)-1)
                st.success("Réponse enregistrée dans le dossier.")
                st.rerun()
    with b2:
        if st.button("↩️ Question précédente", key="prev_entretien"):
            st.session_state["entretien_index"] = max(0, idx-1)
            st.rerun()
    with b3:
        if st.button("➡️ Question suivante", key="next_entretien"):
            st.session_state["entretien_index"] = min(len(questions)-1, idx+1)
            st.rerun()

    rows = db_exec(
        "SELECT * FROM entretiens WHERE dossier_id=? ORDER BY ordre,created_at",
        (c["dossier_id"],), fetch=True
    )
    if rows:
        st.markdown("### 📝 Discussion enregistrée")
        st.dataframe(
            pd.DataFrame([{
                "N°": r["ordre"], "Domaine": r["domaine"],
                "Question": r["question"], "Réponse": r["reponse"],
                "Date": r["created_at"]
            } for r in rows]),
            use_container_width=True, hide_index=True
        )

        st.markdown("### 📄 Rapport de discussion")
        st.caption("Le PDF reprend uniquement les échanges réellement enregistrés : aucune réponse n'est inventée.")
        if HAS_PDF:
            pdf = build_interview_pdf()
            if pdf:
                st.download_button(
                    "📥 Générer / télécharger le PDF de l'entretien",
                    pdf,
                    f"entretien_youagronome_{datetime.now():%Y%m%d_%H%M}.pdf",
                    "application/pdf",
                    key="download_interview_pdf"
                )
        else:
            st.warning("ReportLab n'est pas installé : installez-le pour activer l'export PDF.")
    else:
        st.caption("Aucune réponse enregistrée pour ce dossier.")


# =========================================================
# 10. ESPACE 1 — TERRAIN & DONNÉES
# =========================================================
def terrain_space():
    compact_context()
    choice = st.selectbox(
        "🧭 Ouvrir",
        ["Dossier & client", "Production", "Observations & analyses", "Équipements & historique", "💬 Entretien agriculteur"],
        key="terrain_menu_v9"
    )
    if choice == "Dossier & client":
        c = active_client(); d = active_dossier()
        st.subheader("📁 Dossier 360°")
        if d:
            a,b,c1,d1 = st.columns(4)
            a.metric("Client", c["nom"] if c else "—")
            b.metric("Type", d["type_exploitation"] or "—")
            c1.metric("Région", d["region"] or "—")
            d1.metric("Statut", d["statut"] or "—")
            st.write(d.get("notes") or "Aucune note.")
        else:
            st.info("Créez ou sélectionnez un dossier dans la barre latérale.")
    elif choice == "Production":
        domain = st.selectbox("Type de production", ["Agriculture", "Élevage", "Aquaculture", "Agroalimentaire"], key="production_domain_v9")
        if domain == "Agriculture":
            c = context()
            if not c["parcelle_id"]: st.info("Sélectionnez une parcelle.")
            else:
                p = active_parcelle()
                with st.form("agri_compact_v9"):
                    culture = st.selectbox("Culture", CULTURES, index=CULTURES.index(p["culture"]) if p["culture"] in CULTURES else 0)
                    stade = st.selectbox("Stade", STAGES, index=STAGES.index(p["stade"]) if p["stade"] in STAGES else 0)
                    variete = st.text_input("Variété")
                    irrigation = st.selectbox("Irrigation", ["Pluvial","Irrigué","Mixte","Goutte-à-goutte","Aspersion"])
                    cible = st.number_input("Rendement cible t/ha", 0.0, 100.0, 3.0)
                    reel = st.number_input("Rendement réel t/ha", 0.0, 100.0, 0.0)
                    notes = st.text_area("Fertilisation / protection / remarques")
                    if st.form_submit_button("Enregistrer le suivi", type="primary"):
                        db_exec("UPDATE parcelles SET culture=?,stade=?,updated_at=? WHERE id=?", (culture,stade,now(),p["id"]))
                        db_exec("""INSERT INTO cultures
                            (id,dossier_id,parcelle_id,culture,variete,date_semis,date_recolte_prevue,irrigation,
                             rendement_cible,rendement_reel,fertilisation,protection,notes,created_at)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (new_id("CUL"),c["dossier_id"],p["id"],culture,variete,str(date.today()),str(date.today()+timedelta(days=90)),
                             irrigation,cible,reel,notes,"", "",now()))
                        audit("SUIVI_CULTURE","parcelle",p["id"]); st.success("Suivi agricole enregistré.")
        elif domain == "Élevage":
            did = context()["dossier_id"]
            if did:
                with st.form("elevage_compact_v9"):
                    espece = st.selectbox("Espèce", ["Bovin","Ovin","Caprin","Volaille","Porcin","Autre"])
                    categorie = st.selectbox("Catégorie", ["Adulte","Jeune","Reproducteur","Engraissement","Pondeuse","Autre"])
                    effectif = st.number_input("Effectif", 0, 100000, 0)
                    poids = st.number_input("Poids moyen kg", 0.0, 1000.0, 0.0)
                    alimentation = st.text_input("Alimentation")
                    mortalite = st.number_input("Mortalités", 0, 100000, 0)
                    vaccination = st.text_input("Vaccination")
                    notes = st.text_area("Observations")
                    if st.form_submit_button("Enregistrer le suivi", type="primary"):
                        db_exec("""INSERT INTO livestock
                            (id,dossier_id,espece,categorie,effectif,poids_moyen,alimentation,mortalite,vaccination,reproduction,date_suivi,notes)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (new_id("ELV"),did,espece,categorie,effectif,poids,alimentation,mortalite,vaccination,"",now(),notes))
                        audit("SUIVI_ELEVAGE","dossier",did); st.success("Suivi élevage enregistré.")
        elif domain == "Aquaculture":
            did = context()["dossier_id"]
            if did:
                with st.form("aqua_compact_v9"):
                    unite = st.text_input("Bassin / unité", "Bassin 1")
                    espece = st.text_input("Espèce", "Tilapia")
                    volume = st.number_input("Volume m³", 0.0, 1e9, 0.0)
                    densite = st.number_input("Densité ind./m³", 0.0, 10000.0, 0.0)
                    oxy = st.number_input("O₂ mg/L", 0.0, 30.0, 0.0)
                    ph = st.number_input("pH", 0.0, 14.0, 7.0)
                    temp = st.number_input("Température °C", 0.0, 50.0, 25.0)
                    mort = st.number_input("Mortalités", 0, 100000, 0)
                    notes = st.text_area("Notes")
                    if st.form_submit_button("Enregistrer le suivi", type="primary"):
                        db_exec("""INSERT INTO aquaculture
                            (id,dossier_id,unite,espece,volume_m3,densite,oxygene,ph,temperature,mortalite,aliment_kg,poids_moyen_g,date_suivi,notes)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (new_id("AQU"),did,unite,espece,volume,densite,oxy,ph,temp,mort,0,0,now(),notes))
                        audit("SUIVI_AQUACULTURE","dossier",did); st.success("Suivi aquacole enregistré.")
        else:
            did = context()["dossier_id"]
            if did:
                with st.form("agrofood_compact_v9"):
                    produit = st.text_input("Produit")
                    quantite = st.number_input("Quantité", 0.0, 1e9, 0.0)
                    unite = st.selectbox("Unité", ["kg","t","L","unités"])
                    lot = st.text_input("N° lot")
                    transformation = st.text_input("Transformation")
                    stockage = st.selectbox("Stockage", ["Sec","Froid","Congélation","Ambiant","Autre"])
                    pertes = st.number_input("Pertes %", 0.0, 100.0, 0.0)
                    qualite = st.selectbox("Qualité", ["Non évaluée","Conforme","À surveiller","Non conforme"])
                    if st.form_submit_button("Enregistrer", type="primary"):
                        db_exec("""INSERT INTO agrofood
                            (id,dossier_id,produit,quantite,unite,transformation,stockage,pertes_pct,qualite,lot,date_operation,notes)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (new_id("AGF"),did,produit,quantite,unite,transformation,stockage,pertes,qualite,lot,now(),""))
                        audit("SUIVI_AGROALIMENTAIRE","dossier",did); st.success("Opération enregistrée.")
    elif choice == "Observations & analyses":
        c = context()
        st.subheader("👁️ Observations et 🧪 analyses")
        if not c["dossier_id"]: st.info("Sélectionnez un dossier.")
        else:
            left,right = st.columns(2)
            with left:
                with st.form("obs_compact_v9"):
                    domaine = st.selectbox("Domaine", DOMAINS)
                    typ = st.selectbox("Type", ["Inspection","Incident","Symptôme","Mesure","Suivi","Photo","Autre"])
                    gravite = st.selectbox("Gravité", ["Information","Faible","Moyenne","Élevée","Critique"])
                    incidence = st.number_input("Incidence %",0.0,100.0,0.0)
                    desc = st.text_area("Observation factuelle")
                    if st.form_submit_button("Ajouter observation"):
                        db_exec("""INSERT INTO observations
                            (id,dossier_id,parcelle_id,domaine,type_observation,description,gravite,incidence,surface_affectee_ha,
                             latitude,longitude,photo_name,date_observation,source_type,confidence,validation_status,created_at)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (new_id("OBS"),c["dossier_id"],c["parcelle_id"],domaine,typ,desc,gravite,incidence,0,c["latitude"],c["longitude"],"",now(),"Terrain",0.85,"À vérifier",now()))
                        audit("OBSERVATION","observation",c["dossier_id"]); st.success("Observation enregistrée.")
            with right:
                with st.form("ana_compact_v9"):
                    typ = st.selectbox("Type analyse", ["Sol","Eau","Végétal","Aliment","Fourrage","Autre"])
                    param = st.text_input("Paramètre","pH")
                    valeur = st.number_input("Valeur",-1e12,1e12,0.0)
                    unite = st.text_input("Unité")
                    labo = st.text_input("Laboratoire / source")
                    validation = st.selectbox("Validation", ["Validé","À vérifier","Rejeté"])
                    if st.form_submit_button("Ajouter analyse"):
                        conf = 0.95 if validation=="Validé" else 0.65
                        db_exec("""INSERT INTO analyses
                            (id,dossier_id,parcelle_id,type_analyse,parametre,valeur,unite,methode,laboratoire,date_analyse,
                             source_type,confidence,validation_status,notes,created_at)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (new_id("ANA"),c["dossier_id"],c["parcelle_id"],typ,param,valeur,unite,"",labo,now(),
                             "Laboratoire" if labo else "Terrain",conf,validation,"",now()))
                        audit("ANALYSE","analyse",c["dossier_id"]); st.success("Analyse enregistrée.")
    elif choice == "Équipements & historique":
        did = context()["dossier_id"]
        if did:
            assets = db_exec("SELECT * FROM assets WHERE dossier_id=? ORDER BY created_at DESC",(did,), fetch=True)
            st.subheader("📦 Équipements")
            st.dataframe(pd.DataFrame(assets), use_container_width=True, hide_index=True) if assets else st.caption("Aucun équipement.")
            st.subheader("📚 Historique")
            hist=[]
            for typ,sql,col in [
                ("Observation","SELECT created_at,description FROM observations WHERE dossier_id=?","description"),
                ("Analyse","SELECT created_at,parametre FROM analyses WHERE dossier_id=?","parametre"),
                ("Action","SELECT created_at,titre FROM actions WHERE dossier_id=?","titre"),
                ("Mission","SELECT created_at,objet FROM missions WHERE dossier_id=?","objet")]:
                for r in db_exec(sql,(did,), fetch=True): hist.append({"Date":r["created_at"],"Type":typ,"Événement":r[col]})
            hist.sort(key=lambda x:x["Date"], reverse=True)
            st.dataframe(pd.DataFrame(hist), use_container_width=True, hide_index=True) if hist else st.caption("Historique vide.")
    else:
        entretien_space()


# =========================================================
# 11. ESPACE 2 — SIG & DIAGNOSTIC
# =========================================================
def sig_space():
    compact_context()
    choice = st.selectbox(
        "🧭 Ouvrir",
        ["Carte & zone d'étude", "GPS & parcelles", "Sol, eau & irrigation", "Santé & phytosanitaire", "Climat & risques", "Fiabilité des données"],
        key="diagnostic_menu_v9"
    )
    c = context()
    if choice == "Carte & zone d'étude":
        st.subheader("🗺️ Zone réellement étudiée")
        if not c["dossier_id"]: st.info("Sélectionnez un dossier.")
        elif not HAS_MAP: st.warning("Installez folium et streamlit-folium pour la carte interactive.")
        else:
            lat=float(c["latitude"] or REGIONS_COORD.get(c["region"],(14.7,-16.2))[0])
            lon=float(c["longitude"] or REGIONS_COORD.get(c["region"],(14.7,-16.2))[1])
            result=map_for_context(lat,lon,560,"study_zone_map_v9",allow_draw=True)
            drawing=result.get("last_active_drawing") if result else None
            coords=drawing_to_coords(drawing)
            if len(coords)>=3:
                st.success(f"Zone : {polygon_area_ha(coords):.3f} ha · périmètre {polygon_perimeter_m(coords):.1f} m")
                typ=st.selectbox("Type",["Zone d'étude","Parcelle","Zone d'observation","Zone à risque"],key="v9_zone_type")
                nom=st.text_input("Nom", "Zone d'étude principale",key="v9_zone_name")
                if st.button("💾 Enregistrer le périmètre",type="primary",key="v9_save_zone"):
                    zid=save_zone(coords,typ,nom,c["dossier_id"],c["parcelle_id"])
                    st.session_state["zone_feature_id"]=zid; st.success("Périmètre enregistré."); st.rerun()
    elif choice == "GPS & parcelles":
        if c["dossier_id"]:
            d=active_dossier()
            a,b=st.columns(2)
            lat=a.number_input("Latitude",value=float(d["latitude"] or 14.7),format="%.6f",key="v9_lat")
            lon=b.number_input("Longitude",value=float(d["longitude"] or -16.2),format="%.6f",key="v9_lon")
            if st.button("Enregistrer GPS",key="v9_gps"):
                db_exec("UPDATE dossiers SET latitude=?,longitude=?,updated_at=? WHERE id=?",(lat,lon,now(),c["dossier_id"]))
                audit("GPS","dossier",c["dossier_id"],{"lat":lat,"lon":lon}); st.success("GPS enregistré.")
    elif choice == "Sol, eau & irrigation":
        zone=next((z for z,v in AGROZONES.items() if c["region"] in v["regions"]),None)
        if zone:
            st.info(
                f"Zone agroécologique indicative : {zone}\n\n"
                f"Sol : {AGROZONES[zone]['sol']}\n\n"
                f"Risques : {AGROZONES[zone]['risques']}"
            )
        a,b,c1,d=st.columns(4)
        eto=a.number_input("ETo mm/j",0.0,20.0,5.5,key="v9_eto")
        kc=b.number_input("Kc",0.1,1.5,1.0,key="v9_kc")
        surf=c1.number_input("Surface ha",0.1,100000.0,float(c["zone_surface_ha"] or c["surface_ha"] or 1),key="v9_surf")
        eff=d.number_input("Efficacité",0.1,1.0,0.75,key="v9_eff")
        st.metric("Besoin brut",f"{eto*kc*10*surf/eff:.1f} m³/j")
    elif choice == "Santé & phytosanitaire":
        st.warning("Pré-diagnostic : il s'agit d'une aide à la vérification, pas d'une prescription homologuée.")
        symptoms=st.text_area("Symptômes / problème observé",key="v9_symptoms")
        if st.button("Analyser",type="primary",key="v9_phyt"):
            answer,_,_=local_expert(symptoms,"Technicien"); st.markdown(answer)
    elif choice == "Climat & risques":
        if st.button("🔄 Synchroniser la météo",key="v9_weather"):
            try: sync_weather(); st.success("Météo synchronisée.")
            except Exception as exc: st.error(str(exc))
        w=st.session_state.get("weather")
        if w:
            cur=w.get("current",{}); a,b,c1,d=st.columns(4)
            a.metric("Température",f"{cur.get('temperature_2m','—')} °C")
            b.metric("Humidité",f"{cur.get('relative_humidity_2m','—')} %")
            c1.metric("Pluie",f"{cur.get('precipitation','—')} mm")
            d.metric("Vent",f"{cur.get('wind_speed_10m','—')} km/h")
    else:
        q,checks=data_quality()
        st.metric("Qualité des données",f"{q}/100")
        st.metric("Confiance",f"{confidence_from_sources()*100:.0f}%")
        st.metric("Risque",f"{risk_score()}/100")
        st.dataframe(pd.DataFrame(checks),use_container_width=True,hide_index=True)


# =========================================================
# 12. ESPACE 3 — IA & DÉCISION
# =========================================================
def decision_space():
    compact_context()
    choice = st.selectbox(
        "🧭 Ouvrir",
        ["IA Expert 360°", "Diagnostic transversal", "Simulations & économie", "Alertes & KPI", "Plan d'action"],
        key="decision_menu_v9"
    )
    c=context()
    if choice == "IA Expert 360°":
        st.subheader("🧠 IA Expert local — sans clé API")
        question=st.text_area("Votre question / problème",key="v9_ia_question",height=120)
        if st.button("🤖 Analyser",type="primary",key="v9_ia_run"):
            if question.strip():
                answer,conf,evidence=local_expert(question,"Consultant")
                st.session_state["last_ai"]=answer
                if c["dossier_id"]:
                    db_exec("""INSERT INTO ai_history(id,dossier_id,parcelle_id,question,answer,confidence,evidence,created_at)
                               VALUES(?,?,?,?,?,?,?,?)""",
                            (new_id("AI"),c["dossier_id"],c["parcelle_id"],question,answer,conf,json.dumps(evidence),now()))
                st.markdown(answer)
        elif st.session_state.get("last_ai"):
            st.markdown(st.session_state["last_ai"])
    elif choice == "Diagnostic transversal":
        if c["dossier_id"]:
            obs=db_exec("SELECT * FROM observations WHERE dossier_id=? ORDER BY created_at DESC LIMIT 30",(c["dossier_id"],),fetch=True)
            ana=db_exec("SELECT * FROM analyses WHERE dossier_id=? ORDER BY date_analyse DESC LIMIT 30",(c["dossier_id"],),fetch=True)
            a,b,c1=st.columns(3); a.metric("Observations",len(obs)); b.metric("Analyses",len(ana)); c1.metric("Confiance",f"{confidence_from_sources()*100:.0f}%")
            if obs: st.dataframe(pd.DataFrame(obs),use_container_width=True,hide_index=True)
            if ana: st.dataframe(pd.DataFrame(ana),use_container_width=True,hide_index=True)
    elif choice == "Simulations & économie":
        a,b,c1,d=st.columns(4)
        y=a.number_input("Rendement t/ha",0.0,100.0,4.0,key="v9_y")
        price=b.number_input("Prix FCFA/t",0.0,10000000.0,180000.0,key="v9_price")
        cost=c1.number_input("Charges FCFA/ha",0.0,10000000.0,500000.0,key="v9_cost")
        loss=d.slider("Pertes %",0,100,10,key="v9_loss")
        ha=float(c["zone_surface_ha"] or c["surface_ha"] or 1)
        prod=y*ha*(1-loss/100); ca=prod*price; charges=cost*ha
        x,z,w=st.columns(3); x.metric("Production",f"{prod:.2f} t"); z.metric("CA",f"{ca:,.0f} FCFA"); w.metric("Marge",f"{ca-charges:,.0f} FCFA")
    elif choice == "Alertes & KPI":
        did=c["dossier_id"]
        if did:
            q,_=data_quality(); risk=risk_score()
            alerts=db_exec("SELECT * FROM alerts WHERE dossier_id=? AND statut='Ouverte' ORDER BY created_at DESC",(did,),fetch=True)
            a,b,c1=st.columns(3); a.metric("Qualité",f"{q}/100"); b.metric("Risque",f"{risk}/100"); c1.metric("Alertes",len(alerts))
            if alerts: st.dataframe(pd.DataFrame(alerts),use_container_width=True,hide_index=True)
    else:
        did=c["dossier_id"]
        if did:
            with st.form("action_v9"):
                titre=st.text_input("Action à réaliser")
                resp=st.text_input("Responsable")
                echeance=st.date_input("Échéance",date.today()+timedelta(days=3))
                priorite=st.selectbox("Priorité",["Basse","Normale","Haute","Critique"])
                if st.form_submit_button("Créer l'action",type="primary"):
                    db_exec("""INSERT INTO actions
                        (id,dossier_id,mission_id,domaine,titre,responsable,echeance,priorite,statut,cout_estime,preuve,notes,created_at,updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("ACT"),did,st.session_state.get("selected_mission"),"Général",titre,resp,str(echeance),priorite,"À faire",0,"","",now(),now()))
                    audit("CREATION","action",did,titre); st.success("Action créée.")
            rows=db_exec("SELECT * FROM actions WHERE dossier_id=? ORDER BY echeance",(did,),fetch=True)
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True) if rows else st.caption("Aucune action.")



# =========================================================
# 13. ESPACE 4 — CONSULTANCE & PILOTAGE
# =========================================================
def consultancy_space():
    compact_context()
    choice = st.selectbox(
        "🧭 Ouvrir",
        ["Clients & dossiers", "Missions", "Devis & finance", "Rapports", "Documents & agenda", "Administration & audit"],
        key="cabinet_menu_v9"
    )
    c=context()
    if choice == "Clients & dossiers":
        rows=db_exec("SELECT * FROM clients ORDER BY COALESCE(updated_at,created_at,'') DESC",fetch=True)
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True) if rows else st.caption("Aucun client.")
    elif choice == "Missions":
        did=c["dossier_id"]
        if did:
            with st.form("mission_v9"):
                objet=st.text_input("Objet de mission")
                typ=st.selectbox("Type",["Diagnostic","Étude","Suivi","Conseil","Formation","Audit","Cartographie","Évaluation économique"])
                responsable=st.text_input("Responsable",value=(st.session_state.get("user") or {}).get("nom",""))
                echeance=st.date_input("Échéance",date.today()+timedelta(days=7))
                budget=st.number_input("Budget FCFA",0.0,1e12,0.0)
                statut=st.selectbox("Étape",["Demande","Devis","Validée","Intervention","Suivi","Rapport","Clôturée"])
                if st.form_submit_button("Créer la mission",type="primary"):
                    mid=new_id("MIS")
                    db_exec("""INSERT INTO missions
                        (id,dossier_id,client_id,objet,type_mission,statut,priorite,responsable,date_debut,echeance,budget_fcfa,avancement,notes,created_at,updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (mid,did,c["client_id"],objet,typ,statut,"Normale",responsable,str(date.today()),str(echeance),budget,0,"",now(),now()))
                    st.session_state["selected_mission"]=mid; audit("CREATION","mission",mid,objet); st.success("Mission créée.")
            rows=db_exec("SELECT * FROM missions WHERE dossier_id=? ORDER BY COALESCE(updated_at,created_at,'') DESC",(did,),fetch=True)
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True) if rows else st.caption("Aucune mission.")
    elif choice == "Devis & finance":
        did=c["dossier_id"]; cid=c["client_id"]
        if did:
            with st.form("finance_v9"):
                typ=st.selectbox("Opération",["Recette","Dépense"]); cat=st.selectbox("Catégorie",["Intrants","Main-d'œuvre","Irrigation","Transport","Conseil","Vente","Autre"])
                lib=st.text_input("Libellé"); amount=st.number_input("Montant FCFA",0.0,1e12,0.0)
                if st.form_submit_button("Enregistrer",type="primary"):
                    db_exec("""INSERT INTO finance
                        (id,dossier_id,mission_id,type_operation,categorie,libelle,montant_fcfa,date_operation,statut,reference,notes)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("FIN"),did,st.session_state.get("selected_mission"),typ,cat,lib,amount,now(),"Enregistré","",""))
                    audit("FINANCE","finance",did)
            rows=db_exec("SELECT * FROM finance WHERE dossier_id=? ORDER BY date_operation DESC",(did,),fetch=True)
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True) if rows else st.caption("Aucune opération.")
    elif choice == "Rapports":
        if not c["dossier_id"]: st.info("Sélectionnez un dossier.")
        else:
            report_type=st.selectbox("Type",["Diagnostic initial","Rapport de mission","Rapport de suivi","Rapport économique","Rapport final","Note de conseil"])
            title=st.text_input("Titre","Rapport YouAgronoMe")
            if st.button("Préparer le rapport",type="primary",key="v9_prepare_report"):
                q,_=data_quality()
                obs=db_exec("SELECT * FROM observations WHERE dossier_id=? ORDER BY created_at DESC LIMIT 20",(c["dossier_id"],),fetch=True)
                ana=db_exec("SELECT * FROM analyses WHERE dossier_id=? ORDER BY date_analyse DESC LIMIT 20",(c["dossier_id"],),fetch=True)
                report=f"""CLIENT : {c['client'] or '—'}
DOSSIER : {c['dossier'] or '—'}
ZONE : {c['zone_nom'] or 'Non délimitée'}
PARCELLE : {c['parcelle'] or '—'}
QUALITÉ : {q}/100
CONFIANCE : {confidence_from_sources()*100:.0f}%
RISQUE : {risk_score()}/100
OBSERVATIONS : {len(obs)}
ANALYSES : {len(ana)}

Conclusion : recommandations à confirmer selon les preuves et référentiels applicables."""
                db_exec("""INSERT INTO reports(id,dossier_id,mission_id,type_rapport,titre,contenu,confidence,created_at)
                           VALUES(?,?,?,?,?,?,?,?)""",
                        (new_id("RPT"),c["dossier_id"],st.session_state.get("selected_mission"),report_type,title,report,confidence_from_sources(),now()))
                st.session_state["report_text"]=report
            if st.session_state.get("report_text"):
                st.text_area("Synthèse",st.session_state["report_text"],height=250,key="v9_report_view")
                if HAS_PDF:
                    buf=io.BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4); styles=getSampleStyleSheet()
                    story=[Paragraph(title,styles["Title"]),Spacer(1,12)]
                    for line in st.session_state["report_text"].splitlines():
                        if line.strip(): story.append(Paragraph(line.replace("&","&amp;"),styles["Normal"]))
                    doc.build(story); buf.seek(0)
                    st.download_button("📥 PDF",buf.getvalue(),f"rapport_{datetime.now():%Y%m%d_%H%M}.pdf","application/pdf",key="v9_report_pdf")
    elif choice == "Documents & agenda":
        did=c["dossier_id"]
        if did:
            docs=db_exec("SELECT * FROM documents WHERE dossier_id=? ORDER BY created_at DESC",(did,),fetch=True)
            acts=db_exec("SELECT * FROM actions WHERE dossier_id=? ORDER BY echeance",(did,),fetch=True)
            st.markdown("#### Documents")
            st.dataframe(pd.DataFrame(docs),use_container_width=True,hide_index=True) if docs else st.caption("Aucun document.")
            st.markdown("#### Échéances")
            st.dataframe(pd.DataFrame(acts),use_container_width=True,hide_index=True) if acts else st.caption("Aucune échéance.")
    else:
        user=st.session_state.get("user") or {}
        if user.get("role")!="Super-Admin":
            st.warning("Administration réservée au Super-Admin.")
        else:
            users=db_exec("SELECT email,nom,role,zone,statut,created_at FROM users ORDER BY created_at DESC",fetch=True)
            st.dataframe(pd.DataFrame(users),use_container_width=True,hide_index=True)
            if st.button("🔄 Synchroniser tout le dossier",key="v9_admin_sync"):
                for m in sync_all(): st.write("•",m)
                st.success("Synchronisation terminée.")
            audit_rows=db_exec("SELECT * FROM audit ORDER BY created_at DESC LIMIT 200",fetch=True)
            st.markdown("#### Traçabilité")
            st.dataframe(pd.DataFrame(audit_rows),use_container_width=True,hide_index=True) if audit_rows else st.caption("Aucune trace.")


# =========================================================
# 14. DASHBOARD CONSULTANCE
# =========================================================
def dashboard():
    st.subheader("📊 Cockpit du cabinet")
    did = context()["dossier_id"]
    if not did:
        st.info("Sélectionnez un dossier pour afficher les indicateurs.")
        return
    c = context()
    q,_ = data_quality()
    obs = len(db_exec("SELECT id FROM observations WHERE dossier_id=?",(did,), fetch=True))
    missions = len(db_exec("SELECT id FROM missions WHERE dossier_id=?",(did,), fetch=True))
    actions = len(db_exec("SELECT id FROM actions WHERE dossier_id=?",(did,), fetch=True))
    alerts = len(db_exec("SELECT id FROM alerts WHERE dossier_id=? AND statut='Ouverte'",(did,), fetch=True))
    a,b,c1,d = st.columns(4)
    a.metric("Qualité données",f"{q}/100")
    b.metric("Missions",missions)
    c1.metric("Actions",actions)
    d.metric("Alertes ouvertes",alerts)
    st.markdown("### Chaîne de prise en charge")
    flow = pd.DataFrame({
        "Étape":["Client","Dossier","Zone GPS","Observations","Analyses","Décision","Mission","Rapport"],
        "État":[
            bool(c["client_id"]),bool(c["dossier_id"]),bool(c["zone_geometry"]),obs>0,
            len(db_exec("SELECT id FROM analyses WHERE dossier_id=?",(did,), fetch=True))>0,
            bool(st.session_state.get("last_ai")),missions>0,
            len(db_exec("SELECT id FROM reports WHERE dossier_id=?",(did,), fetch=True))>0
        ]
    })
    flow["État"] = flow["État"].map({True:"✓ OK",False:"À compléter"})
    st.dataframe(flow,use_container_width=True,hide_index=True)


# =========================================================
# 15. CATALOGUE DES 100+ FONCTIONNALITÉS
# =========================================================
FEATURE_CATALOG = [
"01. Gestion des clients",
"02. Fiche client enrichie",
"03. Gestion des dossiers d'exploitation",
"04. Dossier 360°",
"05. Sélection d'un contexte actif unique",
"06. Gestion multi-parcelles",
"07. Délimitation GPS par polygone",
"08. Délimitation d'une zone d'étude",
"09. Délimitation d'une zone d'observation",
"10. Délimitation d'une zone à risque",
"11. Calcul automatique de surface",
"12. Calcul automatique de périmètre",
"13. Calcul du centroïde",
"14. Cartographie interactive",
"15. Couches SIG",
"16. Points GPS",
"17. Parcelles agricoles",
"18. Points d'eau",
"19. Bâtiments / infrastructures",
"20. Bassins aquacoles",
"21. Zones d'élevage",
"22. Historique géographique",
"23. Culture et variété",
"24. Stade cultural",
"25. Dates semis/récolte",
"26. Rendement cible",
"27. Rendement réel",
"28. Irrigation",
"29. Fertilisation",
"30. Protection des cultures",
"31. Observations terrain",
"32. Incidence des problèmes",
"33. Surface affectée",
"34. Gravité",
"35. Photos de preuve",
"36. Géolocalisation des observations",
"37. Analyses de sol",
"38. Analyses d'eau",
"39. Analyses végétales",
"40. Analyses alimentaires",
"41. Validation des analyses",
"42. Niveau de confiance des données",
"43. Source de donnée",
"44. Date de donnée",
"45. Contrôle de qualité",
"46. Contrôle de cohérence",
"47. Score de qualité 0–100",
"48. Score de risque séparé",
"49. Score de confiance séparé",
"50. Profil agroécologique indicatif",
"51. Diagnostic phytosanitaire préliminaire",
"52. Moteur IA local sans clé API",
"53. IA multi-domaine",
"54. Historique des questions IA",
"55. Preuves mobilisées par l'IA",
"56. Plan de vérification",
"57. Alertes terrain",
"58. Alertes qualité des données",
"59. Alertes d'échéance",
"60. Synchronisation météo",
"61. Cache météo",
"62. Journal de synchronisation",
"63. Référentiels institutionnels",
"64. Agriculture",
"65. Élevage",
"66. Suivi zootechnique",
"67. Mortalité animale",
"68. Vaccination",
"69. Reproduction",
"70. Aquaculture",
"71. Qualité de l'eau aquacole",
"72. Densité d'élevage aquacole",
"73. Aliment aquacole",
"74. Croissance aquacole",
"75. Agroalimentaire",
"76. Pertes post-récolte",
"77. Traçabilité des lots",
"78. Qualité produit",
"79. Parc matériel",
"80. Suivi des actifs",
"81. Missions de consultance",
"82. Workflow demande → clôture",
"83. Responsable de mission",
"84. Priorité de mission",
"85. Avancement de mission",
"86. Échéancier",
"87. Plan d'action",
"88. Responsable d'action",
"89. Preuve attendue",
"90. Devis",
"91. Statut du devis",
"92. Finance",
"93. Recettes",
"94. Dépenses",
"95. Marge",
"96. Simulation économique",
"97. Scénarios prudent/central/optimiste",
"98. ROI / rentabilité de base",
"99. Rapports professionnels",
"100. Rapport de diagnostic",
"101. Rapport de mission",
"102. Rapport de suivi",
"103. Rapport économique",
"104. Rapport final",
"105. Export PDF",
"106. Registre documentaire",
"107. Agenda des échéances",
"108. Administration utilisateurs",
"109. Rôles et permissions",
"110. Super-Admin",
"111. Authentification par hash",
"112. Journal d'audit",
"113. Traçabilité des modifications",
"114. Séparation données terrain/officielles/calculées/IA",
"115. Conservation du dernier état connu hors ligne",
"116. Indication de synchronisation",
"117. Tableau de bord du cabinet",
"118. KPI décisionnels",
"119. Historique unifié",
"120. Architecture extensible pour import/export et connecteurs futurs",
]


def show_feature_catalog():
    st.subheader("🧩 Couverture fonctionnelle")
    st.caption("Les fonctions détaillées restent disponibles dans les espaces regroupés, sans multiplier les menus.")
    cols = st.columns(3)
    for i, item in enumerate(FEATURE_CATALOG):
        cols[i % 3].markdown(f"- {item}")


# =========================================================
# 16. APPLICATION
# =========================================================
if st.session_state.get("user") is None:
    login()
    st.stop()

professional_header()

with st.sidebar:
    st.markdown("### 🎯 CONTEXTE DE MISSION")
    global_selector()
    c=context(); q,_=data_quality()
    st.markdown("---")
    st.markdown("**Contexte synchronisé**")
    st.caption(f"Client : {c['client'] or '—'}")
    st.caption(f"Dossier : {c['dossier'] or '—'}")
    st.caption(f"Zone : {c['zone_nom'] or 'Non délimitée'}")
    st.caption(f"Surface : {(c['zone_surface_ha'] or c['surface_ha']):.2f} ha")
    st.progress(q/100)
    st.caption(f"Qualité des données : {q}/100")
    if st.button("🔄 Synchroniser le dossier", type="primary", key="sidebar_sync_pro"):
        with st.spinner("Synchronisation du contexte, météo et référentiels..."):
            msgs=sync_all()
        for m in msgs: st.write("•",m)
        st.success("Synchronisation terminée.")
    if st.button("🚪 Déconnexion", key="logout_pro"):
        audit("DECONNEXION","user",(st.session_state.get("user") or {}).get("email",""))
        st.session_state["user"]=None
        st.rerun()

main_tabs = st.tabs([
    "🌍 TERRAIN",
    "🗺️ DIAGNOSTIC",
    "🤖 DÉCISION",
    "💼 CABINET",
])

with main_tabs[0]:
    st.markdown("<div class='ya-section'><div class='ya-section-title'>🌍 Terrain & données</div><div class='ya-kicker'>Le dossier client, les unités d'exploitation et les preuves terrain alimentent toutes les analyses.</div></div>", unsafe_allow_html=True)
    terrain_space()

with main_tabs[1]:
    st.markdown("<div class='ya-section'><div class='ya-section-title'>🗺️ SIG & diagnostic</div><div class='ya-kicker'>La zone réellement étudiée devient le périmètre géographique commun des diagnostics et rapports.</div></div>", unsafe_allow_html=True)
    sig_space()

with main_tabs[2]:
    st.markdown("<div class='ya-section'><div class='ya-section-title'>🤖 IA & décision</div><div class='ya-kicker'>Séparer systématiquement preuves, hypothèses, confiance, risque et décisions opérationnelles.</div></div>", unsafe_allow_html=True)
    decision_space()

with main_tabs[3]:
    st.markdown("<div class='ya-section'><div class='ya-section-title'>💼 Consultance & pilotage</div><div class='ya-kicker'>Clients → missions → devis → intervention → rapport → facturation → suivi → audit.</div></div>", unsafe_allow_html=True)
    consultancy_space()

st.markdown("---")
st.caption(
    "© 2026 YouAgronoMe — Cabinet de consultance 360°. "
    "Les données officielles, terrain, calculées et IA sont distinguées. "
    "La zone géographique active constitue le périmètre commun des analyses. "
    "Une recommandation sensible doit être validée selon les preuves disponibles et les référentiels applicables."
)
