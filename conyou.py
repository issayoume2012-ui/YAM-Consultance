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
    """Executeur SQLite robuste; fetch et many sont des options nommées."""
    if isinstance(params, bool):
        raise TypeError(
            "db_exec(): utilisez fetch=True comme argument nommé, pas comme paramètre positionnel."
        )
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
    CREATE TABLE IF NOT EXISTS settings(
        key TEXT PRIMARY KEY, value TEXT
    );
    CREATE TABLE IF NOT EXISTS entretiens(
        id TEXT PRIMARY KEY, dossier_id TEXT, client_id TEXT, domaine TEXT,
        mode TEXT, question TEXT, reponse TEXT, auteur TEXT, ordre INTEGER,
        created_at TEXT
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
    div[data-testid="stTabs"] button{font-weight:650}
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
# 💬 ENTRETIEN / MESSAGES — dossier agriculteur
# =========================================================
INTERVIEW_DOMAINS = ["Agriculture", "Élevage", "Aquaculture", "Agroalimentaire", "Général"]

def interview_questions(domain):
    common = [
        "Quel est votre principal problème ou objectif actuellement ?",
        "Depuis quand avez-vous constaté cette situation ?",
        "Quelles actions avez-vous déjà essayées et avec quel résultat ?",
        "Quelles contraintes faut-il prendre en compte (eau, main-d'œuvre, intrants, budget, marché) ?",
        "Quels changements avez-vous observés récemment ?",
        "Disposez-vous de photos, analyses, factures ou autres preuves utiles ?",
        "Quel résultat souhaitez-vous obtenir en priorité ?",
        "Y a-t-il une information importante que vous souhaitez ajouter ?",
    ]
    extras = {
        "Élevage": [
            "Quels sont les effectifs, espèces/races et principaux changements de santé, alimentation ou reproduction ?",
            "Avez-vous observé mortalité, baisse de croissance ou problème de vaccination ?",
        ],
        "Aquaculture": [
            "Quelle espèce élevez-vous et quelle est la densité du bassin ?",
            "Avez-vous observé un changement de qualité de l'eau, d'alimentation, croissance ou mortalité ?",
        ],
        "Agroalimentaire": [
            "Quel produit transformez-vous et à quelle étape apparaissent les pertes ou problèmes de qualité ?",
            "Comment gérez-vous actuellement stockage, conservation, hygiène et traçabilité ?",
        ],
    }
    return extras.get(domain, []) + common

def save_interview_answer(dossier_id, client_id, domain, mode, question, answer, order_no):
    db_exec("""INSERT INTO entretiens(id,dossier_id,client_id,domaine,mode,question,reponse,auteur,ordre,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (new_id("ENT"), dossier_id, client_id, domain, mode, question, answer,
             (st.session_state.get("user") or {}).get("nom", "Conseiller"), order_no, now()))
    audit("ENTRETIEN", "entretien", dossier_id, question)

def interview_transcript(dossier_id):
    return db_exec("SELECT * FROM entretiens WHERE dossier_id=? ORDER BY ordre,created_at", (dossier_id,), fetch=True)

def build_interview_pdf(context_data, rows, ai_summary=""):
    if not HAS_PDF:
        return None
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=40)
    styles=getSampleStyleSheet()
    story=[Paragraph("Compte rendu d'entretien — YouAgronoMe", styles["Title"]), Spacer(1,10)]
    meta=(f"Client : {context_data.get('client') or '—'} | "
          f"Dossier : {context_data.get('dossier') or '—'} | "
          f"Zone : {context_data.get('zone_nom') or 'Non définie'}")
    story += [Paragraph(meta.replace('&','&amp;'), styles["Normal"]), Spacer(1,12)]
    if ai_summary:
        story += [Paragraph("Synthèse structurée (IA locale)", styles["Heading2"]),
                  Paragraph(ai_summary.replace('&','&amp;').replace('\n','<br/>'), styles["Normal"]), Spacer(1,12)]
    story += [Paragraph("Transcription de l'entretien", styles["Heading2"])]
    for i,r in enumerate(rows,1):
        q=(r.get('question') or '').replace('&','&amp;')
        a=(r.get('reponse') or '').replace('&','&amp;').replace('\n','<br/>')
        story += [Paragraph(f"{i}. {q}", styles["Heading3"]), Paragraph(a or "—", styles["Normal"]), Spacer(1,7)]
    story += [Spacer(1,12), Paragraph(f"Généré le {datetime.now():%d/%m/%Y à %H:%M}", styles["Italic"])]
    doc.build(story); buf.seek(0)
    return buf.getvalue()

def entretien_space():
    c=context()
    st.subheader("💬 Entretien / Messages avec l'agriculteur")
    st.caption("Un seul espace pour conduire l'entretien, conserver les réponses et produire un compte rendu PDF.")
    if not c.get("dossier_id"):
        st.warning("Sélectionnez d'abord un client et un dossier dans le contexte de mission.")
        return
    d1,d2,d3=st.columns([1,1,2])
    with d1:
        domain=st.selectbox("Domaine", INTERVIEW_DOMAINS, key="interview_domain")
    with d2:
        mode=st.selectbox("Mode", ["Questionnaire guidé","Message libre"], key="interview_mode")
    with d3:
        st.metric("Réponses enregistrées", len(interview_transcript(c["dossier_id"])))

    questions=interview_questions(domain)
    if mode == "Questionnaire guidé":
        idx=st.session_state.get("interview_idx",0)
        idx=min(idx,len(questions)-1)
        st.markdown(f"**Question {idx+1}/{len(questions)}**")
        st.info(questions[idx])
        answer=st.text_area("Réponse de l'agriculteur", key=f"interview_answer_{idx}", height=140,
                            placeholder="Saisissez fidèlement la réponse, sans la reformuler si possible.")
        b1,b2,b3=st.columns(3)
        if b1.button("💾 Enregistrer la réponse", type="primary", key="interview_save"):
            if answer.strip():
                existing=len(interview_transcript(c["dossier_id"]))
                save_interview_answer(c["dossier_id"],c["client_id"],domain,"guidé",questions[idx],answer.strip(),existing+1)
                st.session_state["interview_idx"]=min(idx+1,len(questions)-1)
                st.rerun()
            else:
                st.warning("Saisissez la réponse avant d'enregistrer.")
        if b2.button("⬅️ Précédente", key="interview_prev"):
            st.session_state["interview_idx"]=max(0,idx-1); st.rerun()
        if b3.button("➡️ Suivante", key="interview_next"):
            st.session_state["interview_idx"]=min(len(questions)-1,idx+1); st.rerun()
    else:
        q=st.text_input("Votre question", placeholder="Ex. Quel problème observez-vous sur la parcelle ?", key="interview_free_q")
        a=st.text_area("Réponse de l'agriculteur", height=130, key="interview_free_a")
        if st.button("💾 Enregistrer le message", type="primary", key="interview_free_save"):
            if q.strip() and a.strip():
                existing=len(interview_transcript(c["dossier_id"]))
                save_interview_answer(c["dossier_id"],c["client_id"],domain,"libre",q.strip(),a.strip(),existing+1)
                st.rerun()
            else:
                st.warning("La question et la réponse sont nécessaires.")

    rows=interview_transcript(c["dossier_id"])
    if rows:
        st.markdown("### 📜 Discussion enregistrée")
        st.dataframe(pd.DataFrame([{"N°":i+1,"Domaine":r.get("domaine"),"Question":r.get("question"),"Réponse":r.get("reponse"),"Date":r.get("created_at")} for i,r in enumerate(rows)]),
                     use_container_width=True, hide_index=True)
        transcript="\n".join([f"Q: {r.get('question','')}\nR: {r.get('reponse','')}" for r in rows])
        ai_summary=st.session_state.get("interview_summary","")
        if st.button("🧠 Analyser et structurer l'entretien", key="interview_analyse"):
            prompt=("Analyse cet entretien agricole en distinguant uniquement ce qui est explicitement dit "
                    "de ce qui reste à vérifier. Donne : problème principal, objectifs, faits observés, "
                    "contraintes, risques à vérifier, informations manquantes et prochaines actions.\n\n"+transcript)
            try:
                result=local_expert(prompt, actor=(st.session_state.get("role") or "Consultant"))
                ai_summary=result.get("answer","") if isinstance(result,dict) else str(result)
            except Exception:
                ai_summary="Synthèse automatique indisponible. Utilisez la transcription comme base factuelle."
            st.session_state["interview_summary"]=ai_summary
            audit("ANALYSE_ENTRETIEN","entretien",c["dossier_id"],"Synthèse structurée")
        if ai_summary:
            st.markdown("### 🧠 Synthèse structurée")
            st.text_area("Synthèse",ai_summary,height=240,key="interview_summary_view")
        pdf=build_interview_pdf(c,rows,ai_summary)
        if pdf:
            st.download_button("📄 Générer le rapport PDF de la discussion",pdf,
                               f"entretien_youagronome_{datetime.now():%Y%m%d_%H%M}.pdf",
                               "application/pdf",key="interview_pdf")

# =========================================================
# 10. ESPACE 1 — TERRAIN & DONNÉES
# =========================================================
def _legacy_terrain_space(selected=None):
    section = selected or st.session_state.get("compact__legacy_terrain_space", '📁 Dossier 360°')

    if section == '📁 Dossier 360°':
        c = context()
        st.subheader("📁 Dossier d'exploitation / étude")
        if not c["dossier_id"]:
            st.info("Sélectionnez ou créez un dossier dans la barre latérale.")
        else:
            d = active_dossier()
            a,b,c1,d1 = st.columns(4)
            a.write(f"**Client**\n\n{context()['client'] or '—'}")
            b.write(f"**Type**\n\n{d['type_exploitation']}")
            c1.write(f"**Localisation**\n\n{d['commune'] or '—'} / {d['region']}")
            d1.write(f"**Statut**\n\n{d['statut']}")
            st.success("Ce dossier est la source de contexte commune aux analyses, à la carte, aux missions et aux rapports.")
            st.text_area("Notes générales", value=d["notes"] or "", key="dossier_notes_view", disabled=True)

    if section == '👥 Client':
        c = active_client()
        if not c:
            st.info("Sélectionnez un client.")
        else:
            st.subheader("👥 Fiche client professionnelle")
            with st.form("client_update"):
                nom = st.text_input("Nom", c["nom"])
                tel = st.text_input("Téléphone", c["telephone"] or "")
                email = st.text_input("E-mail", c["email"] or "")
                org = st.text_input("Organisation", c["organisation"] or "")
                region = st.selectbox("Région", list(REGIONS_COORD), index=list(REGIONS_COORD).index(c["region"]) if c["region"] in REGIONS_COORD else 0)
                notes = st.text_area("Notes", c["notes"] or "")
                if st.form_submit_button("Mettre à jour le client"):
                    db_exec("UPDATE clients SET nom=?,telephone=?,email=?,organisation=?,region=?,notes=?,updated_at=? WHERE id=?",
                            (nom,tel,email,org,region,notes,now(),c["id"]))
                    audit("MISE_A_JOUR", "client", c["id"])
                    st.success("Client mis à jour.")

    if section == '🌾 Agriculture':
        st.subheader("🌾 Registre technique des cultures")
        c = context()
        if not c["parcelle_id"]:
            st.info("Sélectionnez une parcelle.")
        else:
            p = active_parcelle()
            with st.form("agri_form"):
                a,b,c1,d = st.columns(4)
                culture = a.selectbox("Culture", CULTURES, index=CULTURES.index(p["culture"]) if p["culture"] in CULTURES else 0)
                stade = b.selectbox("Stade", STAGES, index=STAGES.index(p["stade"]) if p["stade"] in STAGES else 0)
                variete = c1.text_input("Variété")
                irrigation = d.selectbox("Irrigation", ["Pluvial", "Irrigué", "Mixte", "Goutte-à-goutte", "Aspersion"])
                a2,b2,c2,d2 = st.columns(4)
                semis = a2.date_input("Date semis", date.today())
                recolte = b2.date_input("Récolte prévue", date.today()+timedelta(days=90))
                cible = c2.number_input("Rendement cible t/ha", 0.0, 100.0, 3.0)
                reel = d2.number_input("Rendement réel t/ha", 0.0, 100.0, 0.0)
                fert = st.text_area("Fertilisation / amendements")
                prot = st.text_area("Protection / interventions")
                if st.form_submit_button("Enregistrer le suivi"):
                    db_exec("UPDATE parcelles SET culture=?,stade=?,updated_at=? WHERE id=?",
                            (culture,stade,now(),p["id"]))
                    db_exec("""INSERT INTO cultures
                        (id,dossier_id,parcelle_id,culture,variete,date_semis,date_recolte_prevue,irrigation,
                         rendement_cible,rendement_reel,fertilisation,protection,notes,created_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("CUL"),c["dossier_id"],p["id"],culture,variete,str(semis),str(recolte),
                         irrigation,cible,reel,fert,prot,"",now()))
                    audit("SUIVI_CULTURE", "parcelle", p["id"])
                    st.success("Suivi agricole enregistré.")

    if section == '🐄 Élevage':
        st.subheader("🐄 Élevage — suivi zootechnique")
        did = context()["dossier_id"]
        if did:
            with st.form("livestock_form"):
                a,b,c1,d = st.columns(4)
                espece = a.selectbox("Espèce", ["Bovin","Ovin","Caprin","Volaille","Porcin","Autre"])
                categorie = b.selectbox("Catégorie", ["Adulte","Jeune","Reproducteur","Engraissement","Pondeuse","Autre"])
                effectif = c1.number_input("Effectif", 0, 100000, 0)
                poids = d.number_input("Poids moyen kg", 0.0, 1000.0, 0.0)
                a2,b2,c2,d2 = st.columns(4)
                mortalite = a2.number_input("Mortalités période", 0, 100000, 0)
                alimentation = b2.text_input("Alimentation")
                vaccination = c2.text_input("Vaccination")
                reproduction = d2.text_input("Reproduction")
                notes = st.text_area("Observations zootechniques")
                if st.form_submit_button("Enregistrer le suivi élevage"):
                    db_exec("""INSERT INTO livestock
                        (id,dossier_id,espece,categorie,effectif,poids_moyen,alimentation,mortalite,
                         vaccination,reproduction,date_suivi,notes)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("ELV"),did,espece,categorie,effectif,poids,alimentation,mortalite,
                         vaccination,reproduction,now(),notes))
                    audit("SUIVI_ELEVAGE", "dossier", did)
                    st.success("Suivi enregistré.")
            rows = db_exec("SELECT * FROM livestock WHERE dossier_id=? ORDER BY date_suivi DESC", (did,), fetch=True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if section == '🐟 Aquaculture':
        st.subheader("🐟 Aquaculture — suivi de production")
        did = context()["dossier_id"]
        if did:
            with st.form("aqua_form"):
                a,b,c1,d = st.columns(4)
                unite = a.text_input("Unité / bassin", "Bassin 1")
                espece = b.text_input("Espèce", "Tilapia")
                volume = c1.number_input("Volume m³", 0.0, 1e9, 0.0)
                densite = d.number_input("Densité ind./m³", 0.0, 10000.0, 0.0)
                a2,b2,c2,d2 = st.columns(4)
                oxy = a2.number_input("O₂ mg/L", 0.0, 30.0, 0.0)
                ph = b2.number_input("pH", 0.0, 14.0, 7.0)
                temp = c2.number_input("Température °C", 0.0, 50.0, 25.0)
                mort = d2.number_input("Mortalités", 0, 100000, 0)
                a3,b3 = st.columns(2)
                aliment = a3.number_input("Aliment kg/j", 0.0, 100000.0, 0.0)
                poids = b3.number_input("Poids moyen g", 0.0, 10000.0, 0.0)
                notes = st.text_area("Notes")
                if st.form_submit_button("Enregistrer le suivi aquacole"):
                    db_exec("""INSERT INTO aquaculture
                        (id,dossier_id,unite,espece,volume_m3,densite,oxygene,ph,temperature,
                         mortalite,aliment_kg,poids_moyen_g,date_suivi,notes)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("AQU"),did,unite,espece,volume,densite,oxy,ph,temp,mort,aliment,poids,now(),notes))
                    audit("SUIVI_AQUACULTURE", "dossier", did)
                    st.success("Suivi aquacole enregistré.")

    if section == '🏭 Agroalimentaire':
        st.subheader("🏭 Agroalimentaire — transformation, pertes et qualité")
        did = context()["dossier_id"]
        if did:
            with st.form("agrofood_form"):
                a,b,c1,d = st.columns(4)
                produit = a.text_input("Produit")
                quantite = b.number_input("Quantité", 0.0, 1e9, 0.0)
                unite = c1.selectbox("Unité", ["kg","t","L","unités"])
                lot = d.text_input("N° lot")
                transformation = a.text_input("Transformation")
                stockage = b.selectbox("Stockage", ["Sec","Froid","Congélation","Ambiant","Autre"])
                pertes = c1.number_input("Pertes %", 0.0, 100.0, 0.0)
                qualite = d.selectbox("Qualité", ["Non évaluée","Conforme","À surveiller","Non conforme"])
                notes = st.text_area("Traçabilité / remarques")
                if st.form_submit_button("Enregistrer l'opération"):
                    db_exec("""INSERT INTO agrofood
                        (id,dossier_id,produit,quantite,unite,transformation,stockage,pertes_pct,
                         qualite,lot,date_operation,notes)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("AGF"),did,produit,quantite,unite,transformation,stockage,pertes,qualite,lot,now(),notes))
                    audit("SUIVI_AGROALIMENTAIRE", "dossier", did)
                    st.success("Opération enregistrée.")

    if section == '👁️ Observations':
        st.subheader("👁️ Observation terrain")
        c = context()
        if not c["dossier_id"]:
            st.info("Sélectionnez un dossier.")
        else:
            with st.form("observation_form"):
                a,b,c1,d = st.columns(4)
                domaine = a.selectbox("Domaine", DOMAINS)
                typ = b.selectbox("Type", ["Inspection","Incident","Symptôme","Mesure","Suivi","Photo","Autre"])
                gravite = c1.selectbox("Gravité", ["Information","Faible","Moyenne","Élevée","Critique"])
                incidence = d.number_input("Incidence %", 0.0, 100.0, 0.0)
                surface = st.number_input("Surface affectée ha", 0.0, 100000.0, 0.0)
                desc = st.text_area("Description factuelle et précise")
                photo = st.file_uploader("Photo de preuve", type=["jpg","jpeg","png","webp"], key="obs_photo")
                if st.form_submit_button("Enregistrer l'observation"):
                    db_exec("""INSERT INTO observations
                        (id,dossier_id,parcelle_id,domaine,type_observation,description,gravite,incidence,
                         surface_affectee_ha,latitude,longitude,photo_name,date_observation,source_type,confidence,
                         validation_status,created_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("OBS"),c["dossier_id"],c["parcelle_id"],domaine,typ,desc,gravite,incidence,
                         surface,c["latitude"],c["longitude"],photo.name if photo else "",now(),"Terrain",0.85,
                         "À vérifier",now()))
                    if gravite in ["Élevée","Critique"]:
                        db_exec("""INSERT INTO alerts
                            (id,dossier_id,parcelle_id,domaine,niveau,titre,message,source,due_date,created_at)
                            VALUES(?,?,?,?,?,?,?,?,?,?)""",
                                (new_id("ALT"),c["dossier_id"],c["parcelle_id"],domaine,gravite,
                                 f"Observation {domaine}",desc or "Contrôle requis.","Terrain",
                                 str(date.today()+timedelta(days=2)),now()))
                    audit("OBSERVATION", "observation", c["dossier_id"])
                    st.success("Observation enregistrée et synchronisée au dossier.")

    if section == '🧪 Analyses':
        st.subheader("🧪 Analyses laboratoire / terrain")
        c = context()
        if c["dossier_id"]:
            with st.form("analysis_form"):
                a,b,c1,d = st.columns(4)
                typ = a.selectbox("Type analyse", ["Sol","Eau","Végétal","Aliment","Fourrage","Autre"])
                param = b.text_input("Paramètre", "pH")
                valeur = c1.number_input("Valeur", -1e12, 1e12, 0.0)
                unite = d.text_input("Unité")
                a2,b2,c2 = st.columns(3)
                methode = a2.text_input("Méthode")
                labo = b2.text_input("Laboratoire / source")
                validation = c2.selectbox("Validation", ["Validé","À vérifier","Rejeté"])
                notes = st.text_area("Commentaire")
                if st.form_submit_button("Enregistrer l'analyse"):
                    conf = 0.95 if validation == "Validé" else 0.65
                    db_exec("""INSERT INTO analyses
                        (id,dossier_id,parcelle_id,type_analyse,parametre,valeur,unite,methode,laboratoire,
                         date_analyse,source_type,confidence,validation_status,notes,created_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("ANA"),c["dossier_id"],c["parcelle_id"],typ,param,valeur,unite,methode,labo,
                         now(),"Laboratoire" if labo else "Terrain",conf,validation,notes,now()))
                    audit("ANALYSE", "analyse", c["dossier_id"], {"param":param,"value":valeur})
                    st.success("Analyse enregistrée.")
            rows = db_exec("SELECT * FROM analyses WHERE dossier_id=? ORDER BY date_analyse DESC", (c["dossier_id"],), fetch=True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if section == '📦 Équipements':
        st.subheader("📦 Parc matériel et actifs")
        did = context()["dossier_id"]
        if did:
            with st.form("asset_form"):
                a,b,c1,d = st.columns(4)
                typ = a.selectbox("Type", ["Matériel","Bâtiment","Irrigation","Véhicule","Stock","Autre"])
                nom = b.text_input("Désignation")
                qte = c1.number_input("Quantité", 0.0, 1e9, 0.0)
                unite = d.text_input("Unité")
                valeur = st.number_input("Valeur estimée FCFA", 0.0, 1e12, 0.0)
                etat = st.selectbox("État", ["Bon","Moyen","À réparer","Hors service"])
                notes = st.text_area("Notes")
                if st.form_submit_button("Ajouter l'actif"):
                    db_exec("""INSERT INTO assets(id,dossier_id,type_asset,nom,quantite,unite,etat,valeur_fcfa,notes,created_at)
                               VALUES(?,?,?,?,?,?,?,?,?,?)""",
                            (new_id("AST"),did,typ,nom,qte,unite,etat,valeur,notes,now()))
                    audit("AJOUT_ACTIF","asset",did)

    if section == '📚 Historique':
        st.subheader("📚 Historique unifié")
        did = context()["dossier_id"]
        if did:
            tables = [
                ("Observation","SELECT created_at,description AS texte FROM observations WHERE dossier_id=?"),
                ("Analyse","SELECT created_at,parametre || ' = ' || valeur AS texte FROM analyses WHERE dossier_id=?"),
                ("Action","SELECT created_at,titre AS texte FROM actions WHERE dossier_id=?"),
                ("Mission","SELECT created_at,objet AS texte FROM missions WHERE dossier_id=?"),
            ]
            hist = []
            for typ, sql in tables:
                for row in db_exec(sql,(did,), fetch=True):
                    hist.append({"Date":row["created_at"],"Type":typ,"Événement":row["texte"]})
            hist.sort(key=lambda x:x["Date"], reverse=True)
            st.dataframe(pd.DataFrame(hist), use_container_width=True, hide_index=True)


# =========================================================
# 11. ESPACE 2 — SIG & DIAGNOSTIC
# =========================================================
def _legacy_sig_space(selected=None):
    section = selected or st.session_state.get("compact__legacy_sig_space", '🗺️ Zone concernée')

    if section == '🗺️ Zone concernée':
        st.subheader("🗺️ Délimiter précisément la zone concernée")
        c = context()
        if not c["dossier_id"]:
            st.info("Créez/sélectionnez un dossier.")
        elif not HAS_MAP:
            st.warning("Pour le dessin interactif, installez : folium streamlit-folium")
        else:
            lat = float(c["latitude"] or REGIONS_COORD.get(c["region"], (14.7,-16.2))[0])
            lon = float(c["longitude"] or REGIONS_COORD.get(c["region"], (14.7,-16.2))[1])
            st.info("Utilisez l’outil **Polygone** dans la barre de dessin de la carte, cliquez sur chaque limite de la parcelle, puis double-cliquez pour terminer. La surface, le périmètre et les coordonnées sont calculés automatiquement.")
            st.caption("🖊️ Outils disponibles : polygone, rectangle, point GPS/repère, modification et suppression. Choisissez **Parcelle** pour enregistrer directement le contour dans le dossier.")
            result = map_for_context(lat, lon, 600, "study_zone_map", allow_draw=True)
            drawing = result.get("last_active_drawing") if result else None
            coords = drawing_to_coords(drawing)
            if len(coords) >= 3:
                area = polygon_area_ha(coords)
                perim = polygon_perimeter_m(coords)
                st.success(f"Zone détectée : {area:.3f} ha · périmètre {perim:.1f} m")
                a,b,c1 = st.columns(3)
                typ = a.selectbox("Type de zone", ["Zone d'étude","Parcelle","Zone d'observation","Zone à risque"], key="zone_type_draw")
                nom = b.text_input("Nom de la zone", "Zone d'étude principale", key="zone_name_draw")
                c1.write(f"**Centre**\n{centroid(coords)[0]:.6f}, {centroid(coords)[1]:.6f}")
                if st.button("💾 Enregistrer la délimitation", type="primary", key="save_zone_draw"):
                    # Une délimitation de type Parcelle est enregistrée dans la table parcelles
                    # afin que la surface et la géométrie soient directement réutilisables
                    # par les diagnostics, calculs et rapports.
                    if typ == "Parcelle":
                        did = c["dossier_id"]
                        pid = c.get("parcelle_id")
                        if not pid:
                            pid = new_id("PAR")
                            db_exec(
                                """INSERT INTO parcelles
                                   (id,dossier_id,nom,culture,stade,surface_ha,perimeter_m,latitude,longitude,geometry_json,feature_type,source_type,confidence,validation_status,notes,created_at,updated_at)
                                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                (pid, did, nom, CULTURES[0], STAGES[0], area, perim,
                                 centroid(coords)[0], centroid(coords)[1], json.dumps(coords),
                                 "Parcelle", "GPS/Polygone", 0.98, "À vérifier",
                                 "Parcelle délimitée sur la carte.", now(), now())
                            )
                        else:
                            db_exec(
                                """UPDATE parcelles
                                   SET nom=?, surface_ha=?, perimeter_m=?, latitude=?, longitude=?,
                                       geometry_json=?, source_type=?, confidence=?, validation_status=?, updated_at=?
                                   WHERE id=? AND dossier_id=?""",
                                (nom, area, perim, centroid(coords)[0], centroid(coords)[1],
                                 json.dumps(coords), "GPS/Polygone", 0.98, "À vérifier", now(), pid, did)
                            )
                        st.session_state["parcelle_id"] = pid
                        zid = save_zone(coords, "Parcelle", nom, did, pid)
                        st.session_state["zone_feature_id"] = zid
                        audit("DELIMITATION_PARCELLE", "parcelle", pid,
                              {"surface_ha": area, "perimeter_m": perim, "points": len(coords)})
                        st.success(f"Parcelle « {nom} » délimitée et enregistrée : {area:.3f} ha.")
                    else:
                        zid = save_zone(coords, typ, nom, c["dossier_id"], c["parcelle_id"])
                        st.session_state["zone_feature_id"] = zid
                        st.success("Périmètre enregistré dans le SIG du dossier.")
                    st.session_state["map_nonce"] += 1
                    st.rerun()
            if c["zone_geometry"]:
                st.metric("Zone active", f"{c['zone_surface_ha']:.3f} ha")
                st.caption(f"{c['zone_nom']} · {c['zone_type']} · source GPS/terrain")

    if section == '📍 GPS & polygones':
        st.subheader("📍 GPS, coordonnées et création de parcelle")
        did = context()["dossier_id"]
        if did:
            d = active_dossier()
            a,b = st.columns(2)
            lat = a.number_input("Latitude centrale", value=float(d["latitude"] or 14.7), format="%.6f", key="gps_lat_main")
            lon = b.number_input("Longitude centrale", value=float(d["longitude"] or -16.2), format="%.6f", key="gps_lon_main")
            if st.button("Enregistrer le point GPS", key="save_gps_main"):
                db_exec("UPDATE dossiers SET latitude=?,longitude=?,updated_at=? WHERE id=?", (lat,lon,now(),did))
                audit("GPS","dossier",did,{"lat":lat,"lon":lon})
                st.success("GPS enregistré.")
            with st.form("new_parcel_sig"):
                nom = st.text_input("Nom de la parcelle", "Parcelle 1")
                culture = st.selectbox("Culture", CULTURES)
                if st.form_submit_button("Créer la parcelle"):
                    pid = new_id("PAR")
                    db_exec("""INSERT INTO parcelles
                        (id,dossier_id,nom,culture,stade,latitude,longitude,geometry_json,created_at,updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?)""",
                        (pid,did,nom,culture,STAGES[0],lat,lon,"[]",now(),now()))
                    st.session_state["parcelle_id"] = pid
                    audit("CREATION","parcelle",pid)
                    st.success("Parcelle créée. Vous pouvez maintenant la délimiter avec l’outil Polygone dans « Zone & GPS ». ")

            st.markdown("#### 🖊️ Délimitation cartographique de la parcelle")
            st.caption("Sélectionnez une parcelle ci-dessus ou créez-en une, puis dessinez son contour sur la carte.")
            result_parcel = map_for_context(lat, lon, 520, "parcel_draw_map", allow_draw=True) if HAS_MAP else None
            drawing_parcel = result_parcel.get("last_active_drawing") if result_parcel else None
            coords_parcel = drawing_to_coords(drawing_parcel)
            if len(coords_parcel) >= 3:
                area_p = polygon_area_ha(coords_parcel)
                perim_p = polygon_perimeter_m(coords_parcel)
                st.success(f"Contour de parcelle : {area_p:.3f} ha · périmètre {perim_p:.1f} m")
                if st.button("💾 Enregistrer ce contour sur la parcelle active", type="primary", key="save_parcel_polygon"):
                    pid = st.session_state.get("parcelle_id")
                    if not pid:
                        st.error("Sélectionnez ou créez d’abord une parcelle.")
                    else:
                        la, lo = centroid(coords_parcel)
                        db_exec(
                            """UPDATE parcelles SET surface_ha=?, perimeter_m=?, latitude=?, longitude=?,
                               geometry_json=?, source_type=?, confidence=?, validation_status=?, updated_at=?
                               WHERE id=? AND dossier_id=?""",
                            (area_p, perim_p, la, lo, json.dumps(coords_parcel), "GPS/Polygone",
                             0.98, "À vérifier", now(), pid, did)
                        )
                        zid = save_zone(coords_parcel, "Parcelle", "Parcelle active", did, pid)
                        st.session_state["zone_feature_id"] = zid
                        audit("DELIMITATION_PARCELLE", "parcelle", pid, {"surface_ha": area_p, "perimeter_m": perim_p})
                        st.success("Contour enregistré sur la parcelle active.")
                        st.rerun()

    if section == '🧭 Couches SIG':
        st.subheader("🧭 Couches SIG du dossier")
        did = context()["dossier_id"]
        if did:
            rows = db_exec("SELECT * FROM gis_features WHERE dossier_id=? ORDER BY created_at DESC", (did,), fetch=True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            if rows:
                options = [f"{r['id']} · {r['nom']} ({r['type_feature']})" for r in rows]
                cur = context()["zone_id"]
                idx = next((i for i,r in enumerate(rows) if r["id"] == cur),0)
                sel = st.selectbox("Périmètre géographique actif", options, index=idx, key="active_zone_select")
                zid = sel.split(" · ",1)[0]
                if zid != st.session_state.get("zone_feature_id"):
                    st.session_state["zone_feature_id"] = zid
                    st.rerun()

    if section == '🌱 Sols & Eau':
        st.subheader("🌱 Sols & Eau")
        c = context()
        zone = next((z for z,v in AGROZONES.items() if c["region"] in v["regions"]), None)
        if zone:
            st.info(f"Zone agroécologique indicative : {zone}")
            st.write("**Profil de sol indicatif :**", AGROZONES[zone]["sol"])
            st.write("**Risques indicatifs :**", AGROZONES[zone]["risques"])
        st.markdown("#### Besoin d'irrigation")
        a,b,c1,d = st.columns(4)
        eto = a.number_input("ETo mm/j", 0.0, 20.0, 5.5, key="irrig_eto_pro")
        kc = b.number_input("Kc", 0.1, 1.5, 1.0, key="irrig_kc_pro")
        surf = c1.number_input("Surface ha", 0.1, 100000.0, float(c["zone_surface_ha"] or c["surface_ha"] or 1), key="irrig_surface_pro")
        eff = d.number_input("Efficacité", 0.1, 1.0, 0.75, key="irrig_eff_pro")
        etc = eto * kc
        gross = etc * 10 * surf / eff
        st.metric("ETc", f"{etc:.2f} mm/j")
        st.metric("Besoin brut", f"{gross:.1f} m³/j")
        st.caption("Calcul indicatif; confirmer les paramètres par les conditions locales et les données techniques disponibles.")

    if section == '🦠 Phytosanitaire':
        st.subheader("🦠 Pré-diagnostic phytosanitaire")
        st.warning("La sortie est un pré-diagnostic et une procédure de vérification, pas une prescription homologuée.")
        symptoms = st.text_area("Symptômes / ravageurs observés", key="phyt_symptoms_pro")
        severity = st.select_slider("Sévérité", ["Faible","Moyenne","Élevée","Critique"], key="phyt_level_pro")
        if st.button("Construire le pré-diagnostic", key="phyt_run_pro"):
            answer, conf, evidence = local_expert(f"{symptoms} sévérité {severity}", "Technicien")
            st.markdown(answer)
            audit("PRE_DIAGNOSTIC","phytosanitaire",context()["parcelle_id"] or "")

    if section == '🌦️ Climat & risques':
        st.subheader("🌦️ Climat & risques")
        c = context()
        if st.button("🔄 Synchroniser la météo de la zone", key="weather_sync_pro"):
            try:
                sync_weather()
                st.success("Météo synchronisée.")
            except Exception as exc:
                st.error(str(exc))
        weather = st.session_state.get("weather")
        if weather:
            cur = weather.get("current", {})
            a,b,c1,d = st.columns(4)
            a.metric("Température", f"{cur.get('temperature_2m','—')} °C")
            b.metric("Humidité", f"{cur.get('relative_humidity_2m','—')} %")
            c1.metric("Pluie", f"{cur.get('precipitation','—')} mm")
            d.metric("Vent", f"{cur.get('wind_speed_10m','—')} km/h")
            daily = weather.get("daily", {})
            if daily:
                st.dataframe(pd.DataFrame(daily), use_container_width=True, hide_index=True)
        st.caption("Pour les vigilances officielles, vérifier les communications ANACIM au moment de la décision.")

    if section == '🔎 Qualité & preuves':
        st.subheader("🔎 Qualité des données, preuves et fiabilité")
        q, checks = data_quality()
        st.progress(q/100)
        st.metric("Score de qualité", f"{q}/100")
        st.dataframe(pd.DataFrame(checks), use_container_width=True, hide_index=True)
        st.markdown(f"**Confiance calculée séparément :** {confidence_from_sources()*100:.0f} %")
        st.markdown(f"**Risque séparé :** {risk_score()}/100")
        st.caption("Une faible qualité de données ne signifie pas un faible risque. Qualité, confiance et risque sont volontairement séparés.")


# =========================================================
# 12. ESPACE 3 — IA & DÉCISION
# =========================================================
def _legacy_decision_space(selected=None):
    section = selected or st.session_state.get("compact__legacy_decision_space", '🧠 IA Expert 360°')

    if section == '🧠 IA Expert 360°':
        st.subheader("🧠 IA Expert 360° sans clé API")
        st.caption("Le moteur lit automatiquement le dossier, la parcelle, la zone GPS, les observations, analyses et météo disponibles.")
        actor = st.selectbox("Profil d'analyse", ROLES, key="ia_actor_pro")
        question = st.text_area("Question / problème", key="ia_question_pro",
                                placeholder="Ex. La tomate présente des taches depuis 4 jours dans la zone nord délimitée.")
        if st.button("🤖 Produire une analyse structurée", type="primary", key="ia_run_pro"):
            if not question.strip():
                st.warning("Décrivez le problème.")
            else:
                answer, conf, evidence = local_expert(question, actor)
                st.session_state["last_ai"] = answer
                c = context()
                db_exec("""INSERT INTO ai_history
                    (id,dossier_id,parcelle_id,question,answer,confidence,evidence,created_at)
                    VALUES(?,?,?,?,?,?,?,?)""",
                        (new_id("AI"),c["dossier_id"],c["parcelle_id"],question,answer,conf,
                         json.dumps(evidence),now()))
                audit("IA_ANALYSE","ai_history",c["dossier_id"],question)
        if st.session_state.get("last_ai"):
            st.markdown(st.session_state["last_ai"])

    if section == '🔬 Diagnostic multi-domaine':
        st.subheader("🔬 Diagnostic transversal")
        c = context()
        if not c["dossier_id"]:
            st.info("Sélectionnez un dossier.")
        else:
            obs = db_exec("SELECT * FROM observations WHERE dossier_id=? ORDER BY created_at DESC LIMIT 50", (c["dossier_id"],), fetch=True)
            ana = db_exec("SELECT * FROM analyses WHERE dossier_id=? ORDER BY date_analyse DESC LIMIT 50", (c["dossier_id"],), fetch=True)
            a,b,c1 = st.columns(3)
            a.metric("Observations", len(obs))
            b.metric("Analyses", len(ana))
            c1.metric("Confiance", f"{confidence_from_sources()*100:.0f}%")
            if obs: st.dataframe(pd.DataFrame(obs), use_container_width=True, hide_index=True)
            if ana: st.dataframe(pd.DataFrame(ana), use_container_width=True, hide_index=True)

    if section == '📊 Simulations':
        st.subheader("📊 Simulations de scénarios")
        c = context()
        a,b,c1,d = st.columns(4)
        yield_t = a.number_input("Rendement t/ha", 0.0, 100.0, 4.0, key="sim_yield_pro")
        price = b.number_input("Prix FCFA/t", 0.0, 10000000.0, 180000.0, key="sim_price_pro")
        cost = c1.number_input("Charges FCFA/ha", 0.0, 10000000.0, 500000.0, key="sim_cost_pro")
        loss = d.slider("Pertes / aléas %", 0, 100, 10, key="sim_loss_pro")
        ha = float(c["zone_surface_ha"] or c["surface_ha"] or 1)
        production = yield_t * ha * (1-loss/100)
        revenue = production * price
        charges = cost * ha
        margin = revenue - charges
        x,y,z = st.columns(3)
        x.metric("Production ajustée", f"{production:.2f} t")
        y.metric("Chiffre d'affaires", f"{revenue:,.0f} FCFA")
        z.metric("Marge simulée", f"{margin:,.0f} FCFA")
        st.caption("Simulation : modifier les hypothèses pour comparer plusieurs scénarios.")
        scenario = pd.DataFrame({
            "Scénario":["Prudent","Central","Optimiste"],
            "Rendement t/ha":[yield_t*0.75,yield_t,yield_t*1.20],
            "Pertes %":[min(100,loss+15),loss,max(0,loss-7)]
        })
        scenario["Production t"] = scenario["Rendement t/ha"]*ha*(1-scenario["Pertes %"]/100)
        scenario["CA FCFA"] = scenario["Production t"]*price
        st.dataframe(scenario, use_container_width=True, hide_index=True)

    if section == '💰 Économie / ROI':
        st.subheader("💰 Économie, coûts, ROI et marge")
        did = context()["dossier_id"]
        if did:
            with st.form("finance_form_pro"):
                a,b,c1,d = st.columns(4)
                typ = a.selectbox("Type", ["Recette","Dépense"])
                cat = b.selectbox("Catégorie", ["Intrants","Main-d'œuvre","Irrigation","Transport","Conseil","Vente","Autre"])
                lib = c1.text_input("Libellé")
                amount = d.number_input("Montant FCFA", 0.0, 1e12, 0.0)
                if st.form_submit_button("Enregistrer l'opération"):
                    db_exec("""INSERT INTO finance
                        (id,dossier_id,mission_id,type_operation,categorie,libelle,montant_fcfa,date_operation,statut,reference,notes)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("FIN"),did,st.session_state.get("selected_mission"),typ,cat,lib,amount,now(),"Enregistré","", ""))
                    audit("FINANCE","finance",did)
            rows = db_exec("SELECT type_operation,SUM(montant_fcfa) montant FROM finance WHERE dossier_id=? GROUP BY type_operation",(did,), fetch=True)
            df = pd.DataFrame(rows)
            recettes = float(df.loc[df["type_operation"]=="Recette","montant"].sum()) if not df.empty else 0
            depenses = float(df.loc[df["type_operation"]=="Dépense","montant"].sum()) if not df.empty else 0
            a,b,c1 = st.columns(3)
            a.metric("Recettes", f"{recettes:,.0f} FCFA")
            b.metric("Dépenses", f"{depenses:,.0f} FCFA")
            c1.metric("Solde", f"{recettes-depenses:,.0f} FCFA")

    if section == '🚨 Alertes':
        st.subheader("🚨 Centre des alertes")
        did = context()["dossier_id"]
        if did:
            if st.button("Générer les alertes de cohérence", key="generate_alerts_pro"):
                q,_ = data_quality()
                if q < 70:
                    db_exec("""INSERT INTO alerts
                        (id,dossier_id,parcelle_id,domaine,niveau,titre,message,source,due_date,created_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("ALT"),did,context()["parcelle_id"],"Données","Moyenne",
                         "Qualité insuffisante",
                         "Compléter la zone GPS, les observations et les analyses avant décision sensible.",
                         "Moteur qualité",str(date.today()+timedelta(days=2)),now()))
                audit("GENERATION_ALERTES","alerts",did)
            rows = db_exec("SELECT * FROM alerts WHERE dossier_id=? ORDER BY created_at DESC",(did,), fetch=True)
            if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else: st.success("Aucune alerte enregistrée.")

    if section == '📈 KPI':
        st.subheader("📈 Tableau de bord décisionnel")
        c = context()
        q,_ = data_quality()
        risk = risk_score()
        obs = len(db_exec("SELECT id FROM observations WHERE dossier_id=?",(c["dossier_id"],), fetch=True)) if c["dossier_id"] else 0
        ana = len(db_exec("SELECT id FROM analyses WHERE dossier_id=?",(c["dossier_id"],), fetch=True)) if c["dossier_id"] else 0
        actions = len(db_exec("SELECT id FROM actions WHERE dossier_id=?",(c["dossier_id"],), fetch=True)) if c["dossier_id"] else 0
        scores = {
            "Qualité données": q,
            "Preuves terrain": min(100,obs*15),
            "Analyses": min(100,ana*20),
            "SIG / zone": 100 if c["zone_geometry"] else 15,
            "Contexte cultural": 100 if c["culture"] else 20,
            "Suivi actions": min(100,actions*15),
        }
        decision = int(np.mean(list(scores.values())))
        a,b,c1 = st.columns(3)
        a.metric("Score décision", f"{decision}/100")
        b.metric("Confiance", f"{confidence_from_sources()*100:.0f}%")
        c1.metric("Risque", f"{risk}/100")
        st.dataframe(pd.DataFrame([{"Indicateur":k,"Score":v} for k,v in scores.items()]),
                     use_container_width=True, hide_index=True)

    if section == '✅ Plan d’action':
        st.subheader("✅ Plan d'action et suivi")
        did = context()["dossier_id"]
        if did:
            with st.form("action_form_pro"):
                a,b,c1,d = st.columns(4)
                domaine = a.selectbox("Domaine", DOMAINS)
                titre = b.text_input("Action")
                resp = c1.text_input("Responsable")
                echeance = d.date_input("Échéance", date.today()+timedelta(days=3))
                a2,b2,c2 = st.columns(3)
                priorite = a2.selectbox("Priorité", ["Basse","Normale","Haute","Critique"])
                cout = b2.number_input("Coût estimé FCFA", 0.0, 1e12, 0.0)
                statut = c2.selectbox("Statut", ["À faire","En cours","Bloquée","Terminée"])
                notes = st.text_area("Notes / preuve attendue")
                if st.form_submit_button("Créer l'action"):
                    db_exec("""INSERT INTO actions
                        (id,dossier_id,mission_id,domaine,titre,responsable,echeance,priorite,statut,cout_estime,preuve,notes,created_at,updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("ACT"),did,st.session_state.get("selected_mission"),domaine,titre,resp,str(echeance),
                         priorite,statut,cout,"",notes,now(),now()))
                    audit("CREATION","action",did,titre)
            rows = db_exec("SELECT * FROM actions WHERE dossier_id=? ORDER BY echeance",(did,), fetch=True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if section == '🧪 Contrôle de cohérence':
        st.subheader("🧪 Contrôles automatiques de cohérence")
        c = context()
        issues = []
        if c["surface_ha"] and c["zone_surface_ha"] and abs(c["surface_ha"]-c["zone_surface_ha"]) > max(0.5, c["surface_ha"]*0.20):
            issues.append("La surface parcelle et la surface de zone diffèrent fortement.")
        if c["latitude"] is not None and not (-90 <= float(c["latitude"]) <= 90):
            issues.append("Latitude invalide.")
        if c["longitude"] is not None and not (-180 <= float(c["longitude"]) <= 180):
            issues.append("Longitude invalide.")
        if not c["zone_geometry"]:
            issues.append("Aucune zone d'étude délimitée.")
        if issues:
            for x in issues: st.error(x)
        else:
            st.success("Aucune incohérence critique détectée par les contrôles simples.")


# =========================================================
# 13. ESPACE 4 — CONSULTANCE & PILOTAGE
# =========================================================
def _legacy_consultancy_space(selected=None):
    section = selected or st.session_state.get("compact__legacy_consultancy_space", '👥 Clients')

    if section == '👥 Clients':
        st.subheader("👥 Portefeuille clients")
        rows = db_exec("SELECT * FROM clients ORDER BY COALESCE(updated_at, created_at, '') DESC", fetch=True)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if section == '📋 Missions':
        st.subheader("📋 Workflow professionnel des missions")
        did = context()["dossier_id"]
        if did:
            with st.form("mission_form_pro"):
                a,b,c1,d = st.columns(4)
                objet = a.text_input("Objet de la mission")
                typ = b.selectbox("Type", ["Diagnostic","Étude","Suivi","Conseil","Formation","Audit","Cartographie","Évaluation économique"])
                priorite = c1.selectbox("Priorité", ["Normale","Haute","Critique"])
                responsable = d.text_input("Consultant responsable", value=(st.session_state.get("user") or {}).get("nom",""))
                a2,b2,c2,d2 = st.columns(4)
                debut = a2.date_input("Début", date.today())
                echeance = b2.date_input("Échéance", date.today()+timedelta(days=7))
                budget = c2.number_input("Budget FCFA", 0.0, 1e12, 0.0)
                statut = d2.selectbox("Étape", ["Demande","Devis","Validée","Intervention","Suivi","Rapport","Clôturée"])
                if st.form_submit_button("Créer la mission", type="primary"):
                    mid = new_id("MIS")
                    db_exec("""INSERT INTO missions
                        (id,dossier_id,client_id,objet,type_mission,statut,priorite,responsable,date_debut,echeance,budget_fcfa,avancement,notes,created_at,updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (mid,did,context()["client_id"],objet,typ,statut,priorite,responsable,str(debut),str(echeance),
                         budget,0,"",now(),now()))
                    st.session_state["selected_mission"] = mid
                    audit("CREATION","mission",mid,objet)
            rows = db_exec("SELECT * FROM missions WHERE dossier_id=? ORDER BY COALESCE(updated_at, created_at, '') DESC",(did,), fetch=True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if section == '📝 Devis':
        st.subheader("📝 Devis et offres de consultance")
        cid, did = context()["client_id"], context()["dossier_id"]
        if cid:
            with st.form("quote_form"):
                a,b,c1,d = st.columns(4)
                ref = a.text_input("Référence", new_id("DEV").upper())
                objet = b.text_input("Objet")
                ht = c1.number_input("Montant HT FCFA",0.0,1e12,0.0)
                taxes = d.number_input("Taxes FCFA",0.0,1e12,0.0)
                valid = st.date_input("Valide jusqu'au", date.today()+timedelta(days=15))
                statut = st.selectbox("Statut", ["Brouillon","Envoyé","Accepté","Refusé","Expiré"])
                if st.form_submit_button("Enregistrer le devis"):
                    db_exec("""INSERT INTO quotes
                        (id,client_id,dossier_id,reference,objet,montant_ht,taxes,total,statut,date_creation,date_validite,notes)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (new_id("QTE"),cid,did,ref,objet,ht,taxes,ht+taxes,statut,now(),str(valid),""))
                    audit("DEVIS","quote",cid,ref)
            rows = db_exec("SELECT * FROM quotes WHERE client_id=? ORDER BY date_creation DESC",(cid,), fetch=True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if section == '💳 Finance':
        st.subheader("💳 Finance et rentabilité du cabinet")
        did = context()["dossier_id"]
        if did:
            rows = db_exec("SELECT * FROM finance WHERE dossier_id=? ORDER BY date_operation DESC",(did,), fetch=True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if section == '📄 Rapports':
        st.subheader("📄 Rapports professionnels")
        c = context()
        if not c["dossier_id"]:
            st.info("Sélectionnez un dossier.")
        else:
            report_type = st.selectbox("Type de rapport",
                                       ["Diagnostic initial","Rapport de mission","Rapport de suivi","Rapport économique","Rapport final","Note de conseil"])
            title = st.text_input("Titre du rapport", "Rapport YouAgronoMe")
            q,_ = data_quality()
            if st.button("Préparer la synthèse", key="report_prepare_pro"):
                obs = db_exec("SELECT * FROM observations WHERE dossier_id=? ORDER BY created_at DESC LIMIT 20",(c["dossier_id"],), fetch=True)
                ana = db_exec("SELECT * FROM analyses WHERE dossier_id=? ORDER BY date_analyse DESC LIMIT 20",(c["dossier_id"],), fetch=True)
                text = (
                    f"CLIENT : {c['client'] or '—'}\n"
                    f"DOSSIER : {c['dossier'] or '—'}\n"
                    f"ZONE : {c['zone_nom'] or 'Non délimitée'} ({c['zone_surface_ha']:.3f} ha)\n"
                    f"PARCELLE : {c['parcelle'] or '—'}\n"
                    f"CULTURE : {c['culture'] or '—'}\n"
                    f"QUALITÉ DES DONNÉES : {q}/100\n"
                    f"CONFIANCE : {confidence_from_sources()*100:.0f}%\n"
                    f"RISQUE : {risk_score()}/100\n\n"
                    f"OBSERVATIONS RÉCENTES : {len(obs)}\n"
                    f"ANALYSES DISPONIBLES : {len(ana)}\n\n"
                    "Conclusion : les recommandations doivent être confirmées selon les preuves "
                    "terrain, analyses disponibles et sources officielles applicables."
                )
                db_exec("""INSERT INTO reports(id,dossier_id,mission_id,type_rapport,titre,contenu,confidence,created_at)
                           VALUES(?,?,?,?,?,?,?,?)""",
                        (new_id("RPT"),c["dossier_id"],st.session_state.get("selected_mission"),
                         report_type,title,text,confidence_from_sources(),now()))
                st.session_state["report_text"] = text
                audit("RAPPORT","report",c["dossier_id"],report_type)
            if st.session_state.get("report_text"):
                st.text_area("Synthèse", st.session_state["report_text"], height=300, key="report_text_view")
                if HAS_PDF:
                    buf = io.BytesIO()
                    doc = SimpleDocTemplate(buf,pagesize=A4)
                    styles = getSampleStyleSheet()
                    story = [Paragraph(title,styles["Title"]),Spacer(1,12)]
                    for line in st.session_state["report_text"].splitlines():
                        if line.strip():
                            story.append(Paragraph(line.replace("&","&amp;"),styles["Normal"]))
                            story.append(Spacer(1,5))
                    doc.build(story)
                    buf.seek(0)
                    st.download_button("📥 Télécharger le rapport PDF",buf.getvalue(),
                                       f"rapport_youagronome_{datetime.now():%Y%m%d_%H%M}.pdf",
                                       "application/pdf",key="report_pdf_pro")

    if section == '📚 Documents':
        st.subheader("📚 Documents et référentiels")
        for name,url in SOURCES.items():
            st.markdown(f"- **{name}** — {url}")
        did = context()["dossier_id"]
        if did:
            with st.form("document_form"):
                nom = st.text_input("Nom du document")
                typ = st.selectbox("Type", ["Photo","Analyse","Contrat","Devis","Rapport","Carte","Autre"])
                chemin = st.text_input("Chemin / référence")
                desc = st.text_area("Description")
                if st.form_submit_button("Enregistrer le document"):
                    db_exec("""INSERT INTO documents
                        (id,dossier_id,mission_id,nom,type_document,chemin,description,source,created_at)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                        (new_id("DOC"),did,st.session_state.get("selected_mission"),nom,typ,chemin,desc,"Utilisateur",now()))
                    audit("DOCUMENT","document",did,nom)

    if section == '📆 Suivi & agenda':
        st.subheader("📆 Agenda des échéances")
        did = context()["dossier_id"]
        if did:
            actions = db_exec("SELECT * FROM actions WHERE dossier_id=? ORDER BY echeance",(did,), fetch=True)
            missions = db_exec("SELECT * FROM missions WHERE dossier_id=? ORDER BY echeance",(did,), fetch=True)
            upcoming = []
            for x in actions:
                upcoming.append({"Type":"Action","Objet":x["titre"],"Échéance":x["echeance"],"Statut":x["statut"],"Priorité":x["priorite"]})
            for x in missions:
                upcoming.append({"Type":"Mission","Objet":x["objet"],"Échéance":x["echeance"],"Statut":x["statut"],"Priorité":x["priorite"]})
            st.dataframe(pd.DataFrame(upcoming), use_container_width=True, hide_index=True)

    if section == '👑 Administration':
        st.subheader("👑 Administration")
        user = st.session_state.get("user") or {}
        if user.get("role") != "Super-Admin":
            st.warning("Accès réservé au Super-Admin.")
        else:
            with st.form("admin_user_form_pro"):
                a,b,c1,d = st.columns(4)
                email = a.text_input("Identifiant")
                nom = b.text_input("Nom")
                role = c1.selectbox("Rôle", ROLES)
                zone = d.text_input("Zone")
                pwd = st.text_input("Mot de passe", type="password")
                if st.form_submit_button("Créer l'utilisateur"):
                    if email and pwd:
                        try:
                            db_exec("""INSERT INTO users(email,password_hash,nom,role,zone,statut,created_at)
                                       VALUES(?,?,?,?,?,?,?)""",
                                    (email.strip(),sha256(pwd),nom or "Utilisateur",role,zone or "National","Actif",now()))
                            audit("CREATION","user",email)
                            st.success("Utilisateur créé.")
                        except sqlite3.IntegrityError:
                            st.error("Cet identifiant existe déjà.")
            users = db_exec("SELECT email,nom,role,zone,statut,created_at FROM users ORDER BY created_at DESC", fetch=True)
            st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)

    if section == '🛡️ Audit & synchronisation':
        st.subheader("🛡️ Audit, synchronisation et traçabilité")
        sync = db_exec("SELECT * FROM sync_log ORDER BY fetched_at DESC LIMIT 200", fetch=True)
        aud = db_exec("SELECT * FROM audit ORDER BY created_at DESC LIMIT 300", fetch=True)
        st.markdown("### Synchronisations")
        st.dataframe(pd.DataFrame(sync), use_container_width=True, hide_index=True)
        st.markdown("### Audit")
        st.dataframe(pd.DataFrame(aud), use_container_width=True, hide_index=True)
        if st.button("🔄 Synchroniser tout le HUB", key="audit_global_sync"):
            messages = sync_all()
            for m in messages:
                st.write("•",m)
            st.success("Synchronisation terminée avec conservation du dernier état connu.")


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
    st.caption(f"{len(FEATURE_CATALOG)} fonctionnalités prévues dans cette architecture.")
    cols = st.columns(3)
    for i, item in enumerate(FEATURE_CATALOG):
        cols[i % 3].markdown(f"- {item}")


# =========================================================
# 16. APPLICATION — INTERFACE V10 SANS SURCHARGE
# =========================================================
if st.session_state.get("user") is None:
    login()
    st.stop()

professional_header()

with st.sidebar:
    st.markdown("### 🎯 CONTEXTE ACTIF")
    global_selector()
    c=context(); q,_=data_quality()
    st.markdown("---")
    st.caption(f"👤 {c['client'] or 'Client non sélectionné'}")
    st.caption(f"📁 {c['dossier'] or 'Dossier non sélectionné'}")
    st.caption(f"📍 {c['zone_nom'] or 'Zone non délimitée'}")
    st.caption(f"📐 {(c['zone_surface_ha'] or c['surface_ha']):.2f} ha")
    st.progress(q/100)
    st.caption(f"Qualité des données : {q}/100")
    if st.button("🔄 Synchroniser le dossier", type="primary", key="v10_sync"):
        with st.spinner("Synchronisation du contexte, météo et référentiels..."):
            msgs=sync_all()
        for m in msgs: st.write("•",m)
        st.success("Synchronisation terminée.")
    if st.button("🚪 Déconnexion", key="v10_logout"):
        audit("DECONNEXION","user",(st.session_state.get("user") or {}).get("email",""))
        st.session_state["user"]=None
        st.rerun()

# Une seule navigation principale. Les anciennes sous-onglets sont remplacées par des rubriques compactes.
space=st.segmented_control(
    "Espace de travail",
    ["🏠 Accueil","🌍 Terrain","🗺️ Diagnostic","🤖 Décision","💼 Cabinet"],
    default=st.session_state.get("v10_space","🏠 Accueil"),
    key="v10_space"
)

if space == "🏠 Accueil":
    dashboard()
    st.markdown("### ⚡ Accès rapide")
    a,b,c,d=st.columns(4)
    if a.button("📁 Ouvrir le dossier",use_container_width=True,key="quick_dossier"):
        st.session_state["v10_space"]="🌍 Terrain"; st.session_state["terrain_v10_section"]="📁 Dossier 360°"; st.rerun()
    if b.button("💬 Entretien agriculteur",use_container_width=True,key="quick_interview"):
        st.session_state["v10_space"]="🌍 Terrain"; st.session_state["terrain_v10_section"]="💬 Entretien / Messages"; st.rerun()
    if c.button("🧠 Diagnostic 360°",use_container_width=True,key="quick_diag"):
        st.session_state["v10_space"]="🗺️ Diagnostic"; st.session_state["diagnostic_v10_section"]="🔬 Diagnostic 360°"; st.rerun()
    if d.button("📄 Rapports",use_container_width=True,key="quick_report"):
        st.session_state["v10_space"]="💼 Cabinet"; st.session_state["cabinet_v10_section"]="📄 Rapports"; st.rerun()

elif space == "🌍 Terrain":
    st.markdown("### 🌍 Terrain")
    section=st.selectbox("Rubrique",[
        "📁 Dossier 360°","🌾 Production","👁️ Observations","🧪 Analyses",
        "💬 Entretien / Messages","📦 Équipements","📚 Historique"
    ],key="terrain_v10_section")
    mapping={
        "📁 Dossier 360°":"📁 Dossier 360°","🌾 Production":"🌾 Agriculture",
        "👁️ Observations":"👁️ Observations","🧪 Analyses":"🧪 Analyses",
        "📦 Équipements":"📦 Équipements","📚 Historique":"📚 Historique"
    }
    if section=="💬 Entretien / Messages": entretien_space()
    else:
        _legacy_terrain_space(mapping[section])

elif space == "🗺️ Diagnostic":
    st.markdown("### 🗺️ Diagnostic")
    section=st.selectbox("Rubrique",[
        "🗺️ Zone & GPS","🧭 Couches SIG","🌱 Sols & Eau","🦠 Santé / Phytosanitaire",
        "🌦️ Climat & risques","🔎 Qualité & preuves","🔬 Diagnostic 360°"
    ],key="diagnostic_v10_section")
    mapping={
        "🗺️ Zone & GPS":"🗺️ Zone concernée","🧭 Couches SIG":"🧭 Couches SIG",
        "🌱 Sols & Eau":"🌱 Sols & Eau","🦠 Santé / Phytosanitaire":"🦠 Phytosanitaire",
        "🌦️ Climat & risques":"🌦️ Climat & risques","🔎 Qualité & preuves":"🔎 Qualité & preuves",
        "🔬 Diagnostic 360°":"🔬 Diagnostic multi-domaine"
    }
    _legacy_sig_space(mapping[section])

elif space == "🤖 Décision":
    st.markdown("### 🤖 Décision")
    section=st.selectbox("Rubrique",[
        "🧠 IA Expert 360°","🔬 Recommandations / Diagnostic","📊 Simulations & ROI",
        "🚨 Alertes","📈 KPI","✅ Plan d'action","🧪 Contrôle de cohérence"
    ],key="decision_v10_section")
    mapping={
        "🧠 IA Expert 360°":"🧠 IA Expert 360°","🔬 Recommandations / Diagnostic":"🔬 Diagnostic multi-domaine",
        "📊 Simulations & ROI":"📊 Simulations","🚨 Alertes":"🚨 Alertes","📈 KPI":"📈 KPI",
        "✅ Plan d'action":"✅ Plan d'action","🧪 Contrôle de cohérence":"🧪 Contrôle de cohérence"
    }
    _legacy_decision_space(mapping[section])

elif space == "💼 Cabinet":
    st.markdown("### 💼 Cabinet")
    section=st.selectbox("Rubrique",[
        "👥 Clients & dossiers","📋 Missions","💰 Devis & Finance","📄 Rapports",
        "📚 Documents","📆 Suivi & agenda","⚙️ Administration","🛡️ Traçabilité"
    ],key="cabinet_v10_section")
    mapping={
        "👥 Clients & dossiers":"👥 Clients","📋 Missions":"📋 Missions","💰 Devis & Finance":"💳 Finance",
        "📄 Rapports":"📄 Rapports","📚 Documents":"📚 Documents","📆 Suivi & agenda":"📆 Suivi & agenda",
        "⚙️ Administration":"👑 Administration","🛡️ Traçabilité":"🛡️ Audit & synchronisation"
    }
    # Devis et Finance sont fusionnés visuellement : on garde le module Devis accessible depuis Finance.
    _legacy_consultancy_space(mapping[section])

st.markdown("---")
st.caption("© 2026 YouAgronoMe — Cabinet de consultance agricole 360°. Interface V10 : fonctions regroupées, contexte unique, entretien intégré et traçabilité des données.")

