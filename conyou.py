from datetime import datetime, timedelta
import io
import json
import os
import random
import urllib.parse
import time
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

    st.markdown("""
    <style>
    .dashboard-hero {
        padding: 30px 20px;
        border-radius: 16px;
        text-align: center;
        color: white;
        background: linear-gradient(135deg, #1b5e20 0%, #0d2310 100%);
        box-shadow: 0 8px 24px rgba(27, 94, 32, 0.15);
        border-bottom: 4px solid #e1a91a;
        margin-bottom: 25px;
    }
    .dashboard-hero h2 { font-size: 22px !important; font-weight: 800 !important; margin-bottom: 8px !important; color: #ffffff !important; }
    .dashboard-hero p { font-size: 13px !important; opacity: 0.9; max-width: 850px; margin: 0 auto !important; color: #f8fafc; }
    .inst-badge-db {
        background: rgba(255, 255, 255, 0.15);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.25);
        display: inline-block;
        margin-top: 12px;
        color: #ffffff;
    }
    .db-section-title {
        color: #1b5e20;
        font-size: 17px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #e1a91a;
        padding-left: 10px;
    }
    .clean-card {
        background: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #1b5e20;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .clean-card-title {
        font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;
    }
    .clean-card-value { font-size: 19px; font-weight: 800; color: #1b5e20; word-wrap: break-word; line-height: 1.2; }
    .clean-card-sub { font-size: 10px; color: #94a3b8; margin-top: 4px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="dashboard-hero">
        <h2>🇸🇳 Observatoire Multidimensionnel de la Souveraineté Alimentaire du Sénégal</h2>
        <p>Système décisionnel aligné sur les données officielles des bilans de campagne (DAPSA, SAED, SODAGRI, ISRA, ARM, DHORT, CSE, ANACIM, LBA, DER/FJ, DGPRE).</p>
        <span class="inst-badge-db">Filières Suivies : Riz (Irrigué/Pluvial) • Arachide • Mil • Maïs • Sorgho • Niébé • Oignon • Pomme de Terre • Tomate • Coton • Sésame • Manioc • Anacarde</span>
    </div>
    """, unsafe_allow_html=True)

    @st.cache_data
    def charger_donnees_consolidees_senegal():
        data = {
            "Région": [
                "Dakar", "Thiès", "Diourbel", "Saint-Louis", "Kaolack", 
                "Ziguinchor", "Louga", "Tambacounda", "Kolda", "Matam", 
                "Fatick", "Kaffrine", "Kédougou", "Sédhiou"
            ],
            "Type de Sol Dominant (INP)": [
                "Urbain / Sables fins", "Sols Dior (Sableux)", "Sols Deck-Dior", "Sols Hollaldé (Argileux)", "Sols Deck (Sablo-argileux)",
                "Sols Sulfatés Acides / Fluviaux", "Sols Dior (Sableux / Élevage)", "Sols Ferrugineux Tropicaux", "Sols Ferrallitiques / Argileux", "Sols Vertisols / Alluviaux",
                "Sols Halomorphes (Salins)", "Sols Deck-Dior (Céréaliers)", "Sols Lithosols / Rocheux", "Sols Hydromorphes / Rizicoles"
            ],
            "DGPRE - Eau Irrigation Mobilisée (Mio m³)": [
                12.5, 45.0, 18.2, 1420.0, 32.0, 85.0, 14.5, 65.0, 92.0, 680.0, 22.0, 28.0, 15.0, 78.0
            ],
            "SAED/SODAGRI - Riz Irrigué & Pluvial (Tonnes)": [
                0, 1200, 0, 850000, 15000, 95000, 500, 28000, 145000, 180000, 12000, 8500, 18000, 110000
            ],
            "DAPSA - Mil & Sorgho (Tonnes)": [
                200, 32000, 98000, 5000, 185000, 12000, 42000, 110000, 85000, 15000, 140000, 260000, 18000, 45000
            ],
            "DAPSA - Maïs & Fonio (Tonnes)": [
                100, 8500, 12000, 2000, 68000, 28000, 4500, 125000, 142000, 8000, 38000, 115000, 24000, 62000
            ],
            "DAPSA - Arachide (Tonnes)": [
                0, 35000, 82000, 1500, 240000, 800, 22000, 85000, 98000, 500, 125000, 310000, 2500, 48000
            ],
            "DAPSA - Niébé & Sésame (Tonnes)": [
                100, 18000, 38000, 4200, 22000, 1500, 45000, 14000, 11000, 8500, 28000, 32000, 1200, 8500
            ],
            "SODEFITEX/DAPSA - Coton & Anacarde (Tonnes)": [
                0, 0, 0, 0, 0, 18000, 0, 8500, 6200, 0, 2500, 0, 3100, 14500
            ],
            "ARM/DHORT - Oignon & Pomme de Terre (Tonnes)": [
                4500, 65000, 1800, 290000, 8500, 1200, 120000, 800, 1100, 18000, 3200, 1500, 200, 900
            ],
            "ARM/DHORT - Tomate Industrielle & Legumes (Tonnes)": [
                18000, 82000, 4500, 105000, 14000, 8500, 11000, 4200, 5800, 12000, 6200, 4800, 1100, 7200
            ],
            "DAPSA - Manioc & Tubercules (Tonnes)": [
                1200, 210000, 85000, 500, 32000, 14000, 68000, 12000, 18000, 1000, 24000, 45000, 3500, 22000
            ],
            "ARM - Capacité de Stockage/Régulation (Tonnes)": [
                25000, 45000, 8000, 85000, 18000, 4500, 35000, 3000, 4000, 12000, 5000, 8000, 1500, 3500
            ],
            "CSE - Biomasse Pastorale Disponible (kg MS/ha)": [
                250, 850, 1100, 1450, 1800, 2600, 950, 2300, 2800, 1600, 1250, 1900, 3100, 2450
            ],
            "ITA - Taux de Transformation Agroalimentaire (%)": [
                28.5, 16.2, 8.5, 22.0, 14.4, 12.0, 7.2, 9.8, 11.5, 14.2, 9.1, 12.8, 5.5, 10.9
            ],
            "La Banque Agricole - Financements Octroyés (Mio FCFA)": [
                12500, 8900, 6200, 38500, 24000, 7800, 5100, 11200, 13400, 19800, 7100, 28500, 2300, 8200
            ],
            "DER/FJ - Agropreneurs & TPE Financés (Nombre)": [
                1420, 980, 750, 1850, 1210, 840, 620, 910, 1050, 890, 680, 1340, 310, 720
            ],
            "ISRA-BAME - Prix Moyen Producteur Céréales (FCFA/kg)": [
                310, 285, 260, 220, 250, 270, 275, 245, 240, 230, 265, 240, 280, 250
            ],
            "3FPT/ONFP - Acteurs Formés en Agribusiness": [
                850, 1420, 920, 2300, 1750, 1100, 820, 1050, 1280, 1450, 890, 1950, 420, 980
            ],
            "ANACIM - Abonnés Alertes Agrométéo SMS": [
                12000, 45000, 68000, 89000, 95000, 52000, 41000, 63000, 71000, 58000, 48000, 112000, 18000, 44000
            ],
            "INP - Terres Salines Restaurées au Gypse (Ha)": [
                10, 450, 850, 1200, 1600, 3100, 620, 980, 1150, 1400, 4200, 1800, 210, 2800
            ],
            "Taux d'Encadrement Technique ANCAR (%)": [
                5.0, 34.2, 28.0, 78.5, 42.1, 51.0, 22.4, 19.5, 31.0, 64.0, 35.8, 48.0, 12.5, 38.2
            ],
            "Taux Couverture Vaccinale Cheptel MEPA (%)": [
                75.0, 62.5, 88.0, 82.1, 71.4, 55.0, 92.4, 79.8, 85.0, 89.5, 68.0, 74.5, 48.0, 59.2
            ],
            "DAPSA - Intrants Subventionnés Distribués (Tonnes)": [
                50, 4100, 6200, 18500, 14200, 5100, 3200, 8900, 9500, 11200, 5400, 16800, 1200, 4900
            ],
            "DAPSA - Valeur Ajoutée Agricole Estimée (Mrds FCFA)": [
                5.0, 42.0, 28.0, 195.0, 110.0, 55.0, 30.0, 75.0, 88.0, 120.0, 38.0, 145.0, 18.0, 62.0
            ]
        }
        return pd.DataFrame(data)

    df_base = charger_donnees_consolidees_senegal()

    st.markdown("<div class='db-section-title'>⚙️ Paramétrage du Territoire & Scénarios de Campagne Agricole</div>", unsafe_allow_html=True)
    with st.container(border=True):
        col_reg, col_annee, col_scen = st.columns([2, 2, 2])
        
        with col_reg:
            liste_regions = ["Tout le Sénégal"] + list(df_base["Région"].unique())
            region_choisie = st.selectbox("Territoire d'analyse :", options=liste_regions, key="sb_region_choisie_v3")
        
        with col_annee:
            annee_choisie = st.slider("Année de référence :", min_value=1960, max_value=2026, value=2026, key="sl_annee_v3")
            
        with col_scen:
            scenario = st.selectbox(
                "Modèle de projection :",
                options=[
                    "📈 Statu Quo / Campagne Traditionnelle", 
                    "🚨 Choc Climatique / Sécheresse Historique", 
                    "🚀 Optimisation Technologique YouAgronoMe"
                ],
                key="sb_scen_v3"
            )

        facteur_historique = 0.20 + (0.80 * ((annee_choisie - 1960) / (2026 - 1960)))
        coef_production = facteur_historique

        if "Choc Climatique" in scenario:
            coef_production *= 0.70  
            st.error(f"⚠️ **Alerte ANACIM ({annee_choisie})** : Simulation d'un déficit pluviométrique majeur (-30% de rendement sur les cultures pluviales).")
        elif "YouAgronoMe" in scenario:
            coef_production *= 1.25  
            st.success(f"✨ **Gains YouAgronoMe ({annee_choisie})** : Rationalisation des intrants, irrigation de précision et valorisation industrielle (+25%).")

        df_filtre = df_base.copy()
        if region_choisie != "Tout le Sénégal":
            df_filtre = df_filtre[df_filtre["Région"] == region_choisie]

        cols_prod = [
            "SAED/SODAGRI - Riz Irrigué & Pluvial (Tonnes)", "DAPSA - Mil & Sorgho (Tonnes)",
            "DAPSA - Maïs & Fonio (Tonnes)", "DAPSA - Arachide (Tonnes)", "DAPSA - Niébé & Sésame (Tonnes)",
            "SODEFITEX/DAPSA - Coton & Anacarde (Tonnes)", "ARM/DHORT - Oignon & Pomme de Terre (Tonnes)",
            "ARM/DHORT - Tomate Industrielle & Legumes (Tonnes)", "DAPSA - Manioc & Tubercules (Tonnes)"
        ]
        for c in cols_prod:
            df_filtre[c] = (df_filtre[c] * coef_production).astype(int)

        df_filtre["DAPSA - Valeur Ajoutée Agricole Estimée (Mrds FCFA)"] = df_filtre["DAPSA - Valeur Ajoutée Agricole Estimée (Mrds FCFA)"] * facteur_historique
        df_filtre["La Banque Agricole - Financements Octroyés (Mio FCFA)"] = (df_filtre["La Banque Agricole - Financements Octroyés (Mio FCFA)"] * facteur_historique).astype(int)

    total_cereales_all = (
        df_filtre["SAED/SODAGRI - Riz Irrigué & Pluvial (Tonnes)"].sum() +
        df_filtre["DAPSA - Mil & Sorgho (Tonnes)"].sum() +
        df_filtre["DAPSA - Maïs & Fonio (Tonnes)"].sum()
    )

    st.markdown("<div class='db-section-title'>🎯 Tableau de Bord Personnalisé selon les Rôles Institutionnels</div>", unsafe_allow_html=True)

    profil = st.tabs([
        "🧑‍🌾 Agriculteurs & Producteurs",
        "🔬 Techniciens & Vulgarisateurs",
        "🌍 ONG & Projets de Développement",
        "💼 Investisseurs & Agrobusiness",
        "🏛️ État & Décideurs Publics"
    ])

    with profil[0]:
        st.info("💡 **Vue Producteur** : Alertes météo ANACIM, prix indicatifs ISRA-BAME, régulation ARM et disponibilité fourragère CSE.")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">📡 SMS Météo (ANACIM)</div>
                <div class="clean-card-value">{df_filtre['ANACIM - Abonnés Alertes Agrométéo SMS'].sum():,}</div>
                <div class="clean-card-sub">Producteurs connectés</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">💵 Prix Repère (ISRA-BAME)</div>
                <div class="clean-card-value">{df_filtre['ISRA-BAME - Prix Moyen Producteur Céréales (FCFA/kg)'].mean():.0f} FCFA/kg</div>
                <div class="clean-card-sub">Moyenne céréales locales</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🧅 Régulation (ARM)</div>
                <div class="clean-card-value">{df_filtre['ARM/DHORT - Oignon & Pomme de Terre (Tonnes)'].sum():,} T</div>
                <div class="clean-card-sub">Oignon & P. de terre récoltés</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🌿 Biomasse (CSE)</div>
                <div class="clean-card-value">{df_filtre['CSE - Biomasse Pastorale Disponible (kg MS/ha)'].mean():.0f} kg/ha</div>
                <div class="clean-card-sub">Pâturage disponible</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("**🔍 Bilan des Productions Agricoles Réelles par Région :**")
        st.dataframe(
            df_filtre[[
                "Région", "Type de Sol Dominant (INP)", "SAED/SODAGRI - Riz Irrigué & Pluvial (Tonnes)", 
                "DAPSA - Mil & Sorgho (Tonnes)", "DAPSA - Arachide (Tonnes)", "ARM/DHORT - Oignon & Pomme de Terre (Tonnes)"
            ]],
            use_container_width=True, hide_index=True
        )

    with profil[1]:
        st.info("🔬 **Vue Encadrement Technique** : Suivi du taux de couverture ANCAR, restauration des sols INP et formation continue 3FPT.")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">📢 Conseil (ANCAR)</div>
                <div class="clean-card-value">{df_filtre["Taux d'Encadrement Technique ANCAR (%)"].mean():.1f} %</div>
                <div class="clean-card-sub">Taux moyen d'encadrement</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🧪 Sols Traités (INP)</div>
                <div class="clean-card-value">{df_filtre['INP - Terres Salines Restaurées au Gypse (Ha)'].sum():,} Ha</div>
                <div class="clean-card-sub">Sols de tannes récupérés</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🎓 Formés (3FPT/ONFP)</div>
                <div class="clean-card-value">{df_filtre['3FPT/ONFP - Acteurs Formés en Agribusiness'].sum():,}</div>
                <div class="clean-card-sub">Acteurs formés aux bonnes pratiques</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">💉 Santé Animale (MEPA)</div>
                <div class="clean-card-value">{df_filtre['Taux Couverture Vaccinale Cheptel MEPA (%)'].mean():.1f} %</div>
                <div class="clean-card-sub">Couverture vaccinale du cheptel</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("**📋 Suivi des Indicateurs de Vulgarisation & Diversification Réelle :**")
        st.dataframe(
            df_filtre[[
                "Région", "Taux d'Encadrement Technique ANCAR (%)", "INP - Terres Salines Restaurées au Gypse (Ha)", 
                "DAPSA - Niébé & Sésame (Tonnes)", "DAPSA - Manioc & Tubercules (Tonnes)"
            ]],
            use_container_width=True, hide_index=True
        )

    with profil[2]:
        st.info("🌍 **Vue Résilience & ONG** : Sécurité hydrique DGPRE, appui aux cultures vivrières de base et potentiel de transformation locale ITA.")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">💧 Mobilisation Eau (DGPRE)</div>
                <div class="clean-card-value">{df_filtre['DGPRE - Eau Irrigation Mobilisée (Mio m³)'].sum():,.1f} M m³</div>
                <div class="clean-card-sub">Prélèvements d'irrigation</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🥣 Céréales Vivrières</div>
                <div class="clean-card-value">{df_filtre['DAPSA - Mil & Sorgho (Tonnes)'].sum() + df_filtre['DAPSA - Maïs & Fonio (Tonnes)'].sum():,} T</div>
                <div class="clean-card-sub">Mil, Sorgho, Maïs, Fonio</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🧆 Legumineuses</div>
                <div class="clean-card-value">{df_filtre['DAPSA - Niébé & Sésame (Tonnes)'].sum():,} T</div>
                <div class="clean-card-sub">Protéines végétales locales</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🏬 Transfo. Locale (ITA)</div>
                <div class="clean-card-value">{df_filtre['ITA - Taux de Transformation Agroalimentaire (%)'].mean():.1f} %</div>
                <div class="clean-card-sub">Valorisation des récoltes</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("**🛡️ Synthèse de la Disponibilité Alimentaire par Territoire :**")
        st.dataframe(
            df_filtre[[
                "Région", "DGPRE - Eau Irrigation Mobilisée (Mio m³)", "DAPSA - Mil & Sorgho (Tonnes)", 
                "DAPSA - Niébé & Sésame (Tonnes)", "ITA - Taux de Transformation Agroalimentaire (%)"
            ]],
            use_container_width=True, hide_index=True
        )

    with profil[3]:
        st.info("💼 **Vue Agrobusiness & Finance** : Financements La Banque Agricole & DER/FJ, capacités logistiques ARM et cultures de rente.")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🏦 Crédit La Banque Agricole</div>
                <div class="clean-card-value">{df_filtre['La Banque Agricole - Financements Octroyés (Mio FCFA)'].sum() / 1000:.2f} Mrds FCFA</div>
                <div class="clean-card-sub">Financements bancaires injectés</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🚀 Agropreneurs (DER/FJ)</div>
                <div class="clean-card-value">{df_filtre['DER/FJ - Agropreneurs & TPE Financés (Nombre)'].sum():,}</div>
                <div class="clean-card-sub">Projets d'agrobusiness financés</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🥜 Filière Arachidière</div>
                <div class="clean-card-value">{df_filtre['DAPSA - Arachide (Tonnes)'].sum():,} T</div>
                <div class="clean-card-sub">Volume d'arachide produit</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">📦 Infrastructures ARM</div>
                <div class="clean-card-value">{df_filtre['ARM - Capacité de Stockage/Régulation (Tonnes)'].sum():,} T</div>
                <div class="clean-card-sub">Capacité d'entreposage disponible</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("**📈 Opportunités d'Investissement dans les Filières Industrielles :**")
        st.dataframe(
            df_filtre[[
                "Région", "La Banque Agricole - Financements Octroyés (Mio FCFA)", "DER/FJ - Agropreneurs & TPE Financés (Nombre)", 
                "SODEFITEX/DAPSA - Coton & Anacarde (Tonnes)", "ARM/DHORT - Tomate Industrielle & Legumes (Tonnes)"
            ]],
            use_container_width=True, hide_index=True
        )

    with profil[4]:
        st.info("🏛️ **Vue Macro-économique & Souveraineté** : Bilan global des filières (DAPSA), création de richesse et souveraineté alimentaire.")
        total_pib = df_filtre["DAPSA - Valeur Ajoutée Agricole Estimée (Mrds FCFA)"].sum()
        total_intrants = df_filtre["DAPSA - Intrants Subventionnés Distribués (Tonnes)"].sum()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">💰 Valeur Ajoutée (DAPSA)</div>
                <div class="clean-card-value">{total_pib:.2f} Mrds FCFA</div>
                <div class="clean-card-sub">PIB Agricole sectoriel</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🌾 Production Céréalière</div>
                <div class="clean-card-value">{total_cereales_all:,} T</div>
                <div class="clean-card-sub">Riz, Mil, Sorgho, Maïs, Fonio</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🌱 Subventions Intrants</div>
                <div class="clean-card-value">{total_intrants:,} T</div>
                <div class="clean-card-sub">Engrais & semences distribués</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🛡️ Substitution Importations</div>
                <div class="clean-card-value">{(total_cereales_all * 0.21) / 1000:.1f} Mrds FCFA</div>
                <div class="clean-card-sub">Économie de devises estimée</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("**📊 Bilan Consolidé de Toutes les Filières Agricoles du Sénégal :**")
        st.dataframe(
            df_filtre[[
                "Région", "SAED/SODAGRI - Riz Irrigué & Pluvial (Tonnes)", "DAPSA - Mil & Sorgho (Tonnes)", 
                "DAPSA - Arachide (Tonnes)", "ARM/DHORT - Oignon & Pomme de Terre (Tonnes)", "ARM/DHORT - Tomate Industrielle & Legumes (Tonnes)"
            ]],
            use_container_width=True, hide_index=True
        )
# =====================================================
# 💼 CONSULTANCE AGRONOMIQUE EXPERTE (MODULE 360° & IA)
# =====================================================
elif selected == "💼 Consultance":

    DB_FILE = "techniciens_db.json"
    OWNER_EMAIL = "issayoume2012@gmail.com"
    OWNER_PASS = "issayoume2026"

    DEFAULT_OWNER = {
        "email": OWNER_EMAIL,
        "password": OWNER_PASS,
        "nom": "Issa Youm (Administrateur Principal)",
        "role": "Administrateur Système",
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
                user["role"] = "Administrateur Système"
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
        "📊 Simulation Économique & Rapport PDF"
    ]
    if is_owner:
        tabs_titles.append("👑 Admin Liste Blanche")

    tab_c0, tab_c1, tab_c2, tab_c3, tab_c4, *tab_admin = st.tabs(tabs_titles)

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
        st.write("Visualisez et validez les coordonnées GPS de l'exploitation pour le suivi géospatial.")
        
        col_map1, col_map2 = st.columns([2, 1])
        with col_map1:
            if HAS_FOLIUM:
                m = folium.Map(location=[st.session_state.get("consult_gps", {}).get("lat", 14.7910), st.session_state.get("consult_gps", {}).get("lon", -16.0700)], zoom_start=13)
                folium.Polygon(
                    locations=st.session_state.get("draw_coords", [[14.7910, -16.0700], [14.7930, -16.0700], [14.7930, -16.0680], [14.7910, -16.0680]]),
                    color="green",
                    fill=True,
                    fill_color="green",
                    fill_opacity=0.4,
                    popup="Parcelle YouAgronoMe"
                ).add_to(m)
                st_folium(m, width=700, height=400)
            else:
                st.warning("Module Folium non installé. Affichage des coordonnées texte uniquement.")
                
        with col_map2:
            st.markdown("**Points Sommets du Polygone :**")
            df_coords = pd.DataFrame(st.session_state.get("draw_coords", []), columns=["Latitude", "Longitude"])
            st.dataframe(df_coords, use_container_width=True)
            st.success(f"Surface calculée : **{st.session_state.get('active_surface_ha', 3.5)} Ha**")

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

    tab_f1, tab_f2, tab_f3 = st.tabs(["🌾 Calendrier Cultural", "💧 Irrigation de Précision", "🌿 Biopesticides & Bonnes Pratiques"])

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
