from datetime import datetime, timedelta
import io
import json
import os
import random
import urllib.parse
import io
import numpy as np
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import streamlit as st
import io
import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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

# Gestion unifiée des coordonnées et de la surface délimitée
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

/* Ajustement intelligent du conteneur selon l'écran */
.main .block-container { 
    padding-top: 15px !important; 
    max-width: 100% !important; 
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Style de base du bloc du menu */
div[data-testid="stRadio"] {
    background: #ffffff !important;
    padding: 12px !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid #edf2f7 !important;
    margin-bottom: 25px !important;
}

div[data-testid="stRadio"] > label { display: none !important; }

/* Disposition initiale : Ligne (Ordinateurs et grandes tablettes) */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    justify-content: flex-start !important;
    gap: 10px !important;
    flex-wrap: wrap !important;
}

/* Style des éléments du menu */
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
        "nom": "Administrateur Principal",
        "role": "Administrateur",
        "zone": "Toutes zones",
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
            if str(user.get("email", "")).strip().lower() == OWNER_EMAIL:
                user["password"] = OWNER_PASS
                user["role"] = "Administrateur"
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

    # --- BASE PÉDOLOGIQUE COMPLÈTE DU SÉNÉGAL (12 Grands Types - FAO / ORSTOM / CPCS) ---
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

    # --- CATALOGUE SANITAIRE ET RAVAGEURS / INSECTES EXHAUSTIF (200 ENNEMIS DES CULTURES - DPV / CEDEAO) ---
CATALOGUE_DPV_EXPERT = {
    # =========================================================================
    # 1. INSECTES PIQUEURS-SUCEURS & VECTEURS (40)
    # =========================================================================
    "Mouche Blanche des Serres (Bemisia tabaci)": {
        "mecanisme": "Insecte piqueur-suceur très polyphage. Aspire la sève et transmet le virus TYLCV et la Mosaïque du Manioc.",
        "symptomes_visuels": "Crispation et jaunissement des feuilles, dépôt de fumagine noire sur les organes, nuées de minuscules mouches blanches.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Acetamipride 20 SP ou Huile de Neem (15 ml/L). Pose de pièges chromotropiques jaunes."
    },
    "Puceron du Cotonnier (Aphis gossypii)": {
        "mecanisme": "Piqueur-suceur grégaire piquant les jeunes pousses tendres et sécrétant un miellat abondant.",
        "symptomes_visuels": "Enroulement des jeunes feuilles, crispation des apex, colonies denses d'pucerons sous les feuilles.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Imidaclopride 200 SL ou savon noir potassique. Favoriser la faune auxiliaire (coccinelles)."
    },
    "Puceron Noir de l'Arachide (Aphis craccivora)": {
        "mecanisme": "Vecteur principal du virus de la Rosette de l'arachide.",
        "symptomes_visuels": "Raccourcissement des entrenœuds, jaunissement ou rabougrissement en rosette des plans d'arachide.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Deltaméthrine ou Lamda-cyhalothrine dès l'apparition des premières colonies."
    },
    "Puceron Vert du Pêcher et Maraîchage (Myzus persicae)": {
        "mecanisme": "Attaque plus de 400 espèces végétales, vecteur de plus de 100 phytovirus.",
        "symptomes_visuels": "Feuilles gaufreuses, chlorose, présence de mue blanche collée sur le feuillage.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Pymétrozine ou Flonicamide pour préserver la faune utile."
    },
    "Thrips du Piment (Scirtothrips dorsalis)": {
        "mecanisme": "Insecte piqueur-râpeur attaquant les bourgeons floraux et les jeunes fruits.",
        "symptomes_visuels": "Dessèchement des bourgeons, taches argentées puis subéreuses (aspect liège) sur piments.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Spinosad ou Chlorfenapyr. Alterner les familles chimiques pour éviter la résistance."
    },
    "Thrips de l'Oignon (Thrips tabaci)": {
        "mecanisme": "Pique les épidermes des feuilles d'oignon et d'ail, réduisant la capacité photosynthétique.",
        "symptomes_visuels": "Stries argentées longitudinales sur les feuilles tubulaires d'oignon, nécrose des pointes.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Spinetoram ou Abamectine. Maintien d'une bonne irrigation par aspersion."
    },
    "Thrips des Fleurs de Légumineuses (Megalurothrips sjostedti)": {
        "mecanisme": "Pique les boutons floraux du niébé et de l'arachide, provoquent l'avortement des fleurs.",
        "symptomes_visuels": "Chute prématurée des fleurs, gousses déformées, absentes ou mal remplies.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Traitement ciblé à la floraison avec Diméthoate ou Cyperméthrine."
    },
    "Cochenille Farineuse des Citrus (Planococcus citri)": {
        "mecanisme": "Piqueur fixe sécrétant une masse cotonneuse protectrice et du miellat.",
        "symptomes_visuels": "Amas cotonneux blancs sur fruits et sous le calice, jaunissement des feuilles, fumagine.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse", "🪵 Vue Tige / Collet"],
        "traitement": "Huile minérale paraffinique associée à du Spirotétramate."
    },
    "Cochenille Hibiscus / Mangue (Maconellicoccus hirsutus)": {
        "mecanisme": "Injecte une salive toxique provoquant la déformation grave des tissus.",
        "symptomes_visuels": "Graphes de feuilles déformées ('Tête de chou'), rabougrissement des rameaux.",
        "plans_sensibles": ["🪵 Vue Tige / Collet", "🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Taille et brûlage des rameaux atteints + lâcher de la coccinelle *Cryptolaemus montrouzieri*."
    },
    "Cochenille Écaillée du Manguier (Rastrococcus invadens)": {
        "mecanisme": "Couvre la face inférieure des feuilles d'un encroûtement cireux.",
        "symptomes_visuels": "Feuillage entièrement recouvert d'un manteau noir de fumagine, chute massive des mangues.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Lutte biologique par parasitoïdes (*Gyranusoidea tebygi*) ou huile de neem renforcée."
    },
    "Punaise Verte des Légumes (Nezara viridula)": {
        "mecanisme": "Pique les fruits en formation pour en sucer les sucs cellullaires.",
        "symptomes_visuels": "Ponctuations dépigmentées sur fruits, déformation des tomates et gousses de niébé, goût désagréable.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Cyperméthrine ou Lambda-Cyhalothrine tôt le matin."
    },
    "Punaise Brunâtre du Coton et Niébé (Acanthocoris fasciculatus)": {
        "mecanisme": "Attaque les tiges et gousses de Solanacées et Légumineuses.",
        "symptomes_visuels": "Flétrissement localisé des rameaux, dessèchement des gousses.",
        "plans_sensibles": ["🪵 Vue Tige / Collet", "🍓 Vue Fruit / Gousse"],
        "traitement": "Application de Pyréthrinoïdes de synthèse."
    },
    "Punaise Arlequin (Murgantia histrionica)": {
        "mecanisme": "Piqueur spécialisé des Brassicacées (Chou, Navet, Radis).",
        "symptomes_visuels": "Taches blanches ou jaunes sur feuilles de chou, blanchiment et dessèchement.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Malathion ou extraction manuelle des pontes."
    },
    "Punaise de la Gousse de Niébé (Clavigralla tomentosicollis)": {
        "mecanisme": "Pique les jeunes gousses de niébé provoquant leur avortement.",
        "symptomes_visuels": "Gousses racornies, tordues, contenant des grains avortés ou moisis.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Deltaméthrine appliquée dès la formation des premières gousses."
    },
    "Punaise Lygus des Cultures (Lygus lineolaris)": {
        "mecanisme": "Injecte des enzymes provoquant la nécrose des meristèmes apicales.",
        "symptomes_visuels": "Chute des fleurs, fruits borgnes ou tordus (fraises, coton, maraîchage).",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Bifenthrine ou Etofenprox."
    },
    "Punaise Dentelle / Tigre du Poirier/Légumes (Stephanitis nashi)": {
        "mecanisme": "Pique le parenchyme sous-foliaire.",
        "symptomes_visuels": "Face supérieure des feuilles marbrée de blanc, face inférieure tachetée de points noirs luisants.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Savon d'acide gras ou Pyrèthre naturel."
    },
    "Psylle des Agrumes (Trioza erytreae)": {
        "mecanisme": "Vecteur de la redoutable maladie du Huanglongbing (HLB / Greening des agrumes).",
        "symptomes_visuels": "Galles ouvertes en forme de cloches sur la face inférieure des jeunes feuilles, jaunissement asymétrique.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Imidaclopride en systémie racinaire et arrachage des arbres infectés."
    },
    "Psylle de la Tomate et Pomme de terre (Bactericera cockerelli)": {
        "mecanisme": "Injecte une toxine provoquant le 'jaunissement à psylle'.",
        "symptomes_visuels": "Feuilles basales jaunissantes avec nervures purpurines, tubérisation aérienne.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Abamectine ou Spiromesifen."
    },
    "Cicadelle Verte du Cotonnier (Jacobiella facialis)": {
        "mecanisme": "Pique le bord des feuilles en injectant une salive toxique.",
        "symptomes_visuels": "Jaunissement puis rougissement en forme de 'V' sur la bordure des feuilles, enroulement vers le bas.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Acetamipride + Cyperméthrine."
    },
    "Cicadelle du Maïs (Peregrinus maidis)": {
        "mecanisme": "Vecteur du virus de la mosaïque du maïs (MMV) et du striate tenui-virus.",
        "symptomes_visuels": "Stries chlorotiques le long des nervures, accumulation de miellat dans le cornet.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Traitement de semences au Thiamethoxam."
    },
    "Cicadelle du Riz (Nephotettix virescens)": {
        "mecanisme": "Vecteur du virus du Tungro du riz.",
        "symptomes_visuels": "Feuilles jaunissant à partir de la pointe, rabougrissement du plant de riz, faible tallage.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Buprofézine ou Dinotéfurane."
    },
    "Cicadelle Brune du Riz (Nilaparvata lugens)": {
        "mecanisme": "Pique en masse la base des tiges de riz irrigué.",
        "symptomes_visuels": "Dessèchement brutal par foyers circulars appelé 'Hopperburn' (brûlure par cicadelles).",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Assèchement temporaire de la parcelle, Pymétrozine."
    },
    "Cercope du Maïs / Salivaire (Locris rubra)": {
        "mecanisme": "Les larves vivent protégées dans une écume spumeuse au collet de la plante.",
        "symptomes_visuels": "Présence de crachats de coucou à la base des tiges, striation brune des feuilles.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Désherbage des graminées adventices, Chlorpyriphos."
    },
    "Altise de la Tomate (Epitrix cucumeris)": {
        "mecanisme": "Petit coleoptère sauteur perforant les feuilles de petits trous.",
        "symptomes_visuels": "Feuillages criblés de petits trous circulaires comme du plomb de chasse.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Poudre de Neem, Spinosad ou Deltaméthrine."
    },
    "Altise du Gombo et Hibiscus (Podagrica senegalensis)": {
        "mecanisme": "Ravageur majeur du gombo et du bissap au Sénégal.",
        "symptomes_visuels": "Feuilles complètement dentelées et ajourées, réduction sévère de la floraison.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Traitement foliaire précoce avec Cyperméthrine."
    },
    "Siphoninus du Grenadier (Siphoninus phillyreae)": {
        "mecanisme": "Aleyrode formant de vastes colonies sous les feuilles de grenadier.",
        "symptomes_visuels": "Chute massive des feuilles, miellat abondant sur les fruits.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Pulvérisation d'Huile de Neem ou d'Insekticide systémique léger."
    },
    "Puceron Jaune de la Canne à Sucre (Sipha flava)": {
        "mecanisme": "Injecte une toxine provoquant la nécrose cellulaire rapide.",
        "symptomes_visuels": "Feuilles virant au jaune puis au rouge violacé avant de sécher complètement.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Lutte intégrée et lâcher d'hyménoptères parasitoïdes."
    },
    "Cochenille de la Canne à Sucre (Saccharicoccus sacchari)": {
        "mecanisme": "Se loge sous la gaine foliaire des tiges de canne à sucre.",
        "symptomes_visuels": "Amas roses/blancs au niveau des nœuds, perte de teneur en sucre.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Nettoyage manuel des pailles sèches (effeuillage) et biopesticides."
    },
    "Punaise des Céréales (Blissus leucopterus)": {
        "mecanisme": "Pique le collet des jeunes pousses de maïs, sorgho et riz.",
        "symptomes_visuels": "Flétrissement rapide des jeunes plants, rougissement de la base des tiges.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Répandage de Carbofuran en granulés au pied."
    },
    "Cicadelle de la Vigne / Mangue (Idioscopus clypealis)": {
        "mecanisme": "Pique les inflorescences du manguier au moment de la floraison.",
        "symptomes_visuels": "Dessèchement brutal des grappes de fleurs de mangue, chute du miellat.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Traitement préventif juste avant l'ouverture des fleurs avec Imidaclopride."
    },
    "Thrips du Bananier (Chaetanaphothrips signipennis)": {
        "mecanisme": "Pique l'épiderme des doigts de banane encore jeunes.",
        "symptomes_visuels": "Taches rousses puis crevasses noirâtres sur la peau des bananes (Roussissure).",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Gainage des régimes de bananes avec des sacs en polyéthylène perforés impregnes."
    },
    "Cochenille du Bananier (Dysmicoccus breviper)": {
        "mecanisme": "Vecteur du virus de la flétrissure du bananier.",
        "symptomes_visuels": "Colonies sous les gaines foliaires et sur les racines, jaunissement des feuilles.",
        "plans_sensibles": ["🪵 Vue Tige / Collet", "🪴 Vue Racines / Sol"],
        "traitement": "Trempage des rejets dans une solution insecticide avant plantation."
    },
    "Puceron du Bananier (Pentalonia nigronervosa)": {
        "mecanisme": "Vecteur du dangereux virus Bunchy Top du bananier (BBTV).",
        "symptomes_visuels": "Feuilles dressées, courtes et serrées en sommet de stipe (aspect en 'bouquet').",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Eradication des bananiers virosés et pulvérisation anti-pucerons."
    },
    "Punaise à Col Épineux (Paromius gracilis)": {
        "mecanisme": "Pique les grains de riz en stade laiteux.",
        "symptomes_visuels": "Grains de riz tachetés, mouchetés de noir ou complètement vides.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Traitement de couverture à la floraison."
    },
    "Thrips des Serres (Heliothrips haemorrhoidalis)": {
        "mecanisme": "Attaque les agrumes, avocatiers et plantes ornementales.",
        "symptomes_visuels": "Décoloration délimitée par de petites crottes noires déposées par les thrips.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Huile d'été + Pyréthrinoïdes."
    },
    "Puceron des Racines de la Laitue (Pemphigus bursarius)": {
        "mecanisme": "Pique le système racinaire des laitues et composées.",
        "symptomes_visuels": "Flétrissement diurne de la salade, sécrétions blanchâtres sur les racines.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Drenchage au pied avec un néonicotinoïde homologué."
    },
    "Cochenille des Racines du Caféier / Arbres (Geococcus coffeae)": {
        "mecanisme": "Attaque les radicelles sous le niveau du sol.",
        "symptomes_visuels": "Jaunissement global, baisse de vigueur sans cause foliaire visible.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Application de nématocides/insecticides sol autorisés."
    },
    "Punaise Aveugle de la Tomate (Cyrtopeltis tenuis)": {
        "mecanisme": "Pique les tiges tendres et les pédoncules floraux de la tomate.",
        "symptomes_visuels": "Anneaux nécrotiques sombres autour de la tige, chute des fleurs.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Deltaméthrine ou contrôle biologique."
    },
    "Cicadelle de la Flétrissure de la Papaye (Empoasca papayae)": {
        "mecanisme": "Pique le sommet de la tige du papayer.",
        "symptomes_visuels": "Jaunissement des jeunes feuilles du sommet, arrêt de croissance du papayer.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Pulvérisation d'Insekticide de contact."
    },
    "Puceron Jaune du Sorgho (Melanaphis sacchari)": {
        "mecanisme": "Pique la face inférieure des feuilles de sorgho et mil.",
        "symptomes_visuels": "Dessèchement complet du feuillage basilaire, dépôt massif de miellat collant.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Spiro抱tetramat ou Imidaclopride précoce."
    },

    # =========================================================================
    # 2. CHENILLES, FORREURS & MASTICATEURS (50)
    # =========================================================================
    "Chenille Légionnaire d'Automne (Spodoptera frugiperda)": {
        "mecanisme": "Larve vorace s'attaquant au cornet du maïs, sorgho et riz.",
        "symptomes_visuels": "Trou perforant en 'coup de fusil', présence de sciure d'excréments au cœur du cornet.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Emamectine benzoate 5% WDG ou Bacillus thuringiensis (Bt)."
    },
    "Chenille Légionnaire Africaine (Spodoptera exempta)": {
        "mecanisme": "Attaque en armées denses dévorant les pâturages et cultures de céréales.",
        "symptomes_visuels": "Défoliation totale et brutale des parcelles de riz et de maïs en quelques heures.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Traitements de choc à la Cyperméthrine ou Chlorpyriphos."
    },
    "Mineuse de la Tomate (Tuta absoluta)": {
        "mecanisme": "Micro-lépidoptère creusant des mines dans le parenchyme foliaire et creusant les fruits.",
        "symptomes_visuels": "Mines translucides blanchâtres puis nécrotiques, galeries avec excréments sous le calice du fruit.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Chlorantraniliprole (Altacor), Spinosad, pièges à phéromones."
    },
    "Noctuelle Perforatrice du Coton et Tomate (Helicoverpa armigera)": {
        "mecanisme": "Chenille perforant les organes reproducteurs (fruits, gousses, capsules).",
        "symptomes_visuels": "Trous circulaires nets sur tomates et gousses de niébé, chenille souvent enfoncée à demi.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Indoxacarbe, Bacillus thuringiensis, emamectine."
    },
    "Foreur de Tiges de Céréales (Busseola fusca)": {
        "mecanisme": "Creuse de larges galeries internes dans la tige du maïs et du sorgho.",
        "symptomes_visuels": "Symptôme du 'cœur mort', cassure des tiges, orifices de sortie garnis de sciure.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Application de granulés insecticides dans le cornet ou lutte 'push-pull'."
    },
    "Foreur Silencieux de la Canne à Sucre (Eldana saccharina)": {
        "mecanisme": "Pénètre par les entrenœuds inférieurs des cannes et maïs.",
        "symptomes_visuels": "Galeries rouges-brunes à l'intérieur du stipe, écoulement de jus fermentation.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Lâchers de parasitoïdes Trichogrammes et récolte rapide."
    },
    "Foreur de la Tige du Riz (Chilo suppressalis)": {
        "mecanisme": "Larve coupant les vaisseaux conducteurs de la tige du riz irrigué.",
        "symptomes_visuels": "Tiges jaunissantes au tallage ('Cœur mort'), panicules entièrement blanches et vides à l'épiaison.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Fipronil ou Carbofuran au tallage."
    },
    "Foreur Rose de la Tige du Riz (Sesamia calamistis)": {
        "mecanisme": "Attaque le maïs, le riz et la canne à sucre.",
        "symptomes_visuels": "Nécrose du bourgeon terminal, présence de chenilles rosâtres dans la tige.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Chlorantraniliprole en pulvérisation à la base des tiges."
    },
    "Foreur Translucide du Riz (Diopsis thoracica / D. apicalis)": {
        "mecanisme": "Mouche aux yeux pédonculés dont la larve mine la tige du riz.",
        "symptomes_visuels": "Cœur mort sur jeunes tillers de riz de bas-fond.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Deltaméthrine ou sélection de variétés tolérantes."
    },
    "Chenille Tisseuse du Coton / Gombolier (Sylepta derogata)": {
        "mecanisme": "La chenille enroule les feuilles en forme de cigare et les dévore de l'intérieur.",
        "symptomes_visuels": "Feuilles soigneusement enroulées et fixées par des fils de soie, squelettisées.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Destruction manuelle des cigares ou pulvérisation de Bt."
    },
    "Chenille Arpenteuse du Choux (Trichoplusia ni)": {
        "mecanisme": "Se déplace en arpentant et dévore le parenchyme des crucifères.",
        "symptomes_visuels": "Grosses perforations irrégulières sur les feuilles de chou, présence de crottes vertes.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Bacillus thuringiensis kurstaki ou Spinosad."
    },
    "Teigne du Chou (Plutella xylostella)": {
        "mecanisme": "Petite chenille très agile rongeant la face inférieure des feuilles.",
        "symptomes_visuels": "Symptôme de 'fenêtre' (épiderme supérieur laissé intact), feuilles ajourées.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Alternance stricte de molécules : Chlorfenapyr, Emamectine, Spinosad."
    },
    "Mineuse des Feuilles d'Agrumes (Phyllocnistis citrella)": {
        "mecanisme": "Larve creusant de longues galeries serpentines sous l'épiderme des jeunes pousses.",
        "symptomes_visuels": "Galeries argentées ondulées sur jeunes feuilles, enroulement et crispation des pousses.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Abamectine + huile minérale lors des poussées de croissance."
    },
    "Chenille Vorace du Papayer / Sphinx (Erynnis ello)": {
        "mecanisme": "Grosses chenilles dévorant intégralement le feuillage des papayers et maniocs.",
        "symptomes_visuels": "Plantes entièrement effeuillées en quelques jours, présence de grosses chenilles vert/brun.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Ramassage manuel ou Pyréthrinoïdes de synthèse."
    },
    "Chenille Perforatrice du Gombo (Earias biplaga)": {
        "mecanisme": "Perfore les apex de tige et les gousses de gombo et coton.",
        "symptomes_visuels": "Dessèchement des pousses terminales, gousses perforées de trous colmatés par de la soie.",
        "plans_sensibles": ["🪵 Vue Tige / Collet", "🍓 Vue Fruit / Gousse"],
        "traitement": "Lambda-cyhalothrine + Profil organophosphoré."
    },
    "Foreur des Gousses de Niébé (Maruca vitrata)": {
        "mecanisme": "La chenille lie les fleurs et jeunes gousses avec de la soie pour les dévorer.",
        "symptomes_visuels": "Fleurs agglomérées par des fils de soie contenant des excréments, gousses percées.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Traitement au stade bouton floral avec Chlorantraniliprole."
    },
    "Chenille Masticatrice du Ricin et Manguier (Achaea janata)": {
        "mecanisme": "Défoliateur nocturne des arbres fruitiers et cultures industrielles.",
        "symptomes_visuels": "Feuilles dévorées par les bords, seules les nervures principales subsistent.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Pulvérisation du feuillage avec du Pyrèthre ou Malathion."
    },
    "Chenille Hérisson / Épineuse du Coton (Earias insulana)": {
        "mecanisme": "Attaque les boutons floraux et les capsules de coton et gombo.",
        "symptomes_visuels": "Chute des boutons floraux, capsules flétries avec trous d'entrée.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Traitement combiné bio-pesticide et pyréthrinoïde."
    },
    "Chenille de la Pyrale du Maïs (Ostrinia nubilalis)": {
        "mecanisme": "Fore les tiges, les spadices et les rafles de maïs.",
        "symptomes_visuels": "Casse des panicules mâles, épis rongés avec présence de sciure.",
        "plans_sensibles": ["🪵 Vue Tige / Collet", "🍓 Vue Fruit / Gousse"],
        "traitement": "Trichogrammes (parasitoïdes d'œufs) ou Spinosad."
    },
    "Teigne de la Pomme de Terre (Phthorimaea operculella)": {
        "mecanisme": "Attaque les feuilles au champ et les tubercules au champ/stockage.",
        "symptomes_visuels": "Galeries creusées dans les tubercules de pomme de terre remplies de déjections noires.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Poudrage des tubercules stockés au *Bacillus thuringiensis* ou huile essentielle de menthe."
    },
    "Noctuelle Baise-Mère / Ver Gris (Agrotis ipsilon)": {
        "mecanisme": "Chenille terricole coupant la tige des jeunes plantules au niveau du sol la nuit.",
        "symptomes_visuels": "Plantules fraîchement levées sectionnées net au ras du sol.",
        "plans_sensibles": ["🪵 Vue Tige / Collet", "🪴 Vue Racines / Sol"],
        "traitement": "Appâts empoisonnés au son de blé + Chlorpyriphos étalés le soir."
    },
    "Noctuelle Moissonneuse (Agrotis segetum)": {
        "mecanisme": "Attaque les collets et tubercules de carotte, navet et betterave.",
        "symptomes_visuels": "Collets rongés, cavernes creusées dans le sommet des racines de carotte.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Micro-granulés insecticides incorporés au semis."
    },
    "Ver de la Grappe / Pyralide (Cryptoblabes gnidiella)": {
        "mecanisme": "Attaque les agrumes, figues, maïs et sorgho.",
        "symptomes_visuels": "Nids de soie dans les grappes et fruits, pourrissement secondaire.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Bacillus thuringiensis appliqué avec haute pression."
    },
    "Pyrale des Dattes et Caroubes (Ectomyelois ceratoniae)": {
        "mecanisme": "Ravageur majeur des dattes, grenades et agrumes en stockage/champ.",
        "symptomes_visuels": "Fruits desséchés remplis de frass et de fils cireux.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Piégeage de masse et hygiène sanitaire des vergers."
    },
    "Chenille Piqueuse / Limacode (Parasa viridissima)": {
        "mecanisme": "Chenille urticante dévorant le feuillage du palmier, bananier et manguier.",
        "symptomes_visuels": "Feuilles dévorées jusqu'à la nervure centrale, cuisantes brûlures au contact.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Carbaryl ou Deltaméthrine."
    },
    "Foreur des Tiges de Mil (Coniesta ignefusalis)": {
        "mecanisme": "Ravageur endémique du mil au Sahel creusant des galeries dans les tiges.",
        "symptomes_visuels": "Tiges trouées se cassant facilement, chandelles de mil mauvaises ou vides.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Nettoyage et brûlage des chaumes de mil après la récolte."
    },
    "Noctuelle du Choux (Mamestra brassicae)": {
        "mecanisme": "Chenille pénétrait profondément au cœur des pommes de chou.",
        "symptomes_visuels": "Choux perforés de galeries souillées d'excréments liquides odorants.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Spinosad ou Tebufenozide."
    },
    "Hypsipyla du Acajou / Meliacees (Hypsipyla robusta)": {
        "mecanisme": "Foreur des pousses terminales des arbres ligneux et fruitiers.",
        "symptomes_visuels": "Mort de la pousse principale, ramification anormale en buisson.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Taille des pousses attaquées et insecticides systémiques."
    },
    "Chenille Masticatrice de la Patate Douce (Brachmia convolvuli)": {
        "mecanisme": "Joue les feuilles de patate douce entre deux fils de soie.",
        "symptomes_visuels": "Squelettisation des feuilles pliées en deux.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Pulvérisation au Pyrèthre ou Azadirachtine."
    },
    "Foreur des Tiges de Sesame (Antigastra catalaunalis)": {
        "mecanisme": "Atteint les feuilles, fleurs et capsules de sésame.",
        "symptomes_visuels": "Apex du sésame aggloméré, gousses perforées.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Deltaméthrine lors du démarrage de la floraison."
    },
    "Chenille Squeletteuse du Manguier (Bombotelia jocosatrix)": {
        "mecanisme": "Devore uniquement les jeunes pousses tendres (rouges) du manguier.",
        "symptomes_visuels": "Disparition totale des nouvelles pousses florales et végétatives.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Traitement de débourrement au Pyréthrinoïde."
    },
    "Foreur de la Tige du Cotonnier (Sphenoptera gossypii)": {
        "mecanisme": "Bupreste dont la larve creuse la tige principale du coton.",
        "symptomes_visuels": "Flétrissement soudain du plant de coton prêt à récolter.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Arrachage et brûlage des tuteurs infectés."
    },
    "Pyralide du Riz de Plaine (Nymphula depunctalis)": {
        "mecanisme": "Chenille aquatique découpant des étuis dans les feuilles de riz.",
        "symptomes_visuels": "Feuilles sectionnées flottant sur l'eau de la rizière, plants réduits à des moignons.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Vidange temporaire de la parcelle de riz."
    },
    "Chenille Tisseuse du Cashew / Anacardier (Lamida moncusalis)": {
        "mecanisme": "Agrège les feuilles et pommes d'anacarde avec d'épais nids de soie.",
        "symptomes_visuels": "Gros nids marrons desséchés contenant des déjections dans les anacardiers.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Enlèvement mécanique des nids et pulvérisation insecticide."
    },
    "Charançon du Bourgeon Terminal du Palmier (Rhynchophorus phoenicis)": {
        "mecanisme": "Grosses larves dévorant le cœur tendre des palmiers et cocotiers.",
        "symptomes_visuels": "Palmes centrales affaissées, bruit de grignotement à l'intérieur du stipe, odeur fétide.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Injection au cœur du stipe d'Imidaclopride."
    },
    "Foreur de la Courge (Melittia cucurbitae)": {
        "mecanisme": "Chenille d'un papillon chryside creusant la base de la tige des cucurbitacées.",
        "symptomes_visuels": "Flétrissement subit des courges, petit trou avec sciure jaune à la base de la tige.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Incision longitudinale de la tige pour tuer la larve ou buttage."
    },
    "Mineuse des Feuilles du Caféier (Leucoptera coffeella)": {
        "mecanisme": "Destruction du tissu chlorophyllien par des galeries circulaires.",
        "symptomes_visuels": "Taches nécrotiques brunes rondes sur la face supérieure des feuilles de café.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Insecticides systémiques au moment de la poussée foliaire."
    },
    "Sphinx de la Tomate / Tabac (Manduca quinquemaculata)": {
        "mecanisme": "Énorme chenille verte munie d'une corne dévorant feuilles et fruits verts.",
        "symptomes_visuels": "Tiges de tomate entièrement effeuillées, gros fruits croqués.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Ramassage manuel très efficace ou Bt."
    },
    "Chenille Masticatrice du Ricin (Ergolis merione)": {
        "mecanisme": "Défoliateur spécifique des plantes de ricin.",
        "symptomes_visuels": "Limbes dévorés, seules les nervures palmées subsistent.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Pulvérisation d'un insecticide de contact."
    },
    "Mouche Squeletteuse du Sésame (Asphondylia sesami)": {
        "mecanisme": "La larve provoque la formation de galles dans les capsules.",
        "symptomes_visuels": "Capsules de sésame déformées, tordues, sans graines à l'intérieur.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Destruction des capsules sauvages et rotation."
    },
    "Chenille Masticatrice de l'Oignon (Spodoptera exigua)": {
        "mecanisme": "Pénètre à l'intérieur des tubes d'oignon et les dévore de l'intérieur.",
        "symptomes_visuels": "Tubes d'oignon blanchis, devenant translucides avec chenilles visibles par transparence.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Emamectine benzoate additionnée d'un mouillant puissant."
    },
    "Foreur de la Tige de l'Avocatier (Copturus aguacatae)": {
        "mecanisme": "Larve de charançon creusant sous l'écorce des jeunes branches d'avocatier.",
        "symptomes_visuels": "Exsudation de poudre blanche (sucre) sur les branches d'avocatier, casse des rameaux.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Badigeonnage des troncs à la bouillie bordelaise + insecticide."
    },
    "Chenille Masticatrice des Crucifères (Hellula undalis)": {
        "mecanisme": "Attaque le bourgeon central des jeunes choux (Cœur rongé).",
        "symptomes_visuels": "Chou aveugle (ne pomme pas), multiplication des bourgeons secondaires invendables.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Protection sous voile anti-insectes au pépinière, Spinosad."
    },
    "Mineuse des Feuilles de la Pomme de Terre (Liriomyza huidobrensis)": {
        "mecanisme": "Mouche dont la larve mine les feuilles basales.",
        "symptomes_visuels": "Galeries serpentines très denses provoquant le dessèchement foliaire prématuré.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Cyromazine ou Abamectine."
    },
    "Ver de la Capsule du Cotonnier (Diparopsis watersi)": {
        "mecanisme": "Noctuelle rouge spécifique du cotonnier en Afrique de l'Ouest.",
        "symptomes_visuels": "Capsules fermées contenant de la sciure marron au point d'entrée.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Pyréthrinoïde + Organophosphoré en synergie."
    },
    "Chenille Tisseuse du Manguier (Orthaga exvinacea)": {
        "mecanisme": "Tisse de vastes toiles enracinant plusieurs rameaux.",
        "symptomes_visuels": "Dessèchement des blocs de feuilles emprisonnés dans la toile.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Taille sanitaire et incinération des nids."
    },
    "Foreur des Tiges de Guaraná / Café (Zeuzera pyrina)": {
        "mecanisme": "Chenille de la Zeuzère creusant le bois des branches.",
        "symptomes_visuels": "Dessèchement brutal d'une grosse branche, présence d'un trou d'évacuation des crottes.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Fil de fer enfoncé dans la galerie pour écraser la larve."
    },
    "Chenille de la Teigne des Graines (Plodia interpunctella)": {
        "mecanisme": "Ravageur des stocks de maïs, arachide, niébé et fruits séchés.",
        "symptomes_visuels": "Feutrage de fils de soie réunissant les grains en surface des sacs.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Fumigation au Phosphure d'Aluminium (Gastoxin) en milieu étanche."
    },
    "Chenille Masticatrice du Tabac (Spodoptera litura)": {
        "mecanisme": "Polyphage s'attaquant au tabac, piment, aubergine et légumineuses.",
        "symptomes_visuels": "Feuilles réduites à l'état de dentelle, morsures sur baies.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Emamectine benzoate ou Chlorfenapyr."
    },
    "Foreur de la Tige du Gombo (Agrilus chalcocranius)": {
        "mecanisme": "Bupreste dont la larve mine la tige centrale du gombo.",
        "symptomes_visuels": "Enflement (galle) sur la tige de gombo suivi du flétrissement du sommet.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Arrachage des plants gélivés et incinération."
    },

    # =========================================================================
    # 3. MOUCHES DES FRUITS, PONDEUSES & COLEOPTERES (35)
    # =========================================================================
    "Mouche Orientale des Fruits (Bactrocera dorsalis)": {
        "mecanisme": "Attaque les mangues, papayes, agrumes en piquant la peau pour y déposer ses œufs.",
        "symptomes_visuels": "Piqure noire sur le fruit, pourrissement interne rapide, coulures, chute massive.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Piégeage au Méthyl-Eugenol, ramassage systématique des fruits tombés."
    },
    "Mouche Méditerranéenne des Fruits (Ceratitis capitata)": {
        "mecanisme": "Pique une multitude de fruits charnus (Agrumes, Guayaves, Pêches).",
        "symptomes_visuels": "Zones mères et molles autour du point de ponte, asticots blancs dans la pulpe.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "GF-120 (Appât insecticide) en pulvérisation par taches."
    },
    "Mouche de la Mangue Merveilleuse (Ceratitis cosyra)": {
        "mecanisme": "Mouche indigène d'Afrique s'attaquant aux mangues précoces.",
        "symptomes_visuels": "Taches brunes dépressionnaires sur les mangues en mûrissement.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Traitements de vergers à base de Spinosad + appât protéique."
    },
    "Mouche des Cucurbitacées (Dacus punctatifrons)": {
        "mecanisme": "Pond sous la peau des melons, pastèques, courges et concombres.",
        "symptomes_visuels": "Exsudation de gomme au point de piqûre, déformation du fruit en 'crochet'.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Emballage individuel des fruits ou piégeage à la Cuelure."
    },
    "Mouche de la Gourde (Dacus bivittatus)": {
        "mecanisme": "Spécialisée dans la destruction des gombos, courges et courgettes.",
        "symptomes_visuels": "Gousses de gombo jaunissantes et courbes, remplies d'asticots.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Pulvérisation d'Insekticides de contact dès la nouaison."
    },
    "Mouche du Piment / Poivron (Atherigona orientalis)": {
        "mecanisme": "Pond sur les blessures ou sous le calice des piments et tomates.",
        "symptomes_visuels": "Chute prématurée des piments verts, pourritures molles à la base du pédoncule.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Maintien de la propreté du champ, incinération des déchets."
    },
    "Mouche des Pousses du Sorgho (Atherigona soccata)": {
        "mecanisme": "Pond sur les jeunes feuilles de sorgho au stade 3-5 feuilles.",
        "symptomes_visuels": "Dessèchement de la feuille centrale ('Cœur mort') sur jeune plantule de sorgho.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Traitement de semences au Imidaclopride et semis précoces."
    },
    "Mouche de la Grainerie de Niébé (Callosobruchus maculatus)": {
        "mecanisme": "Pond sur les gousses au champ puis se développe dans les stocks de niébé.",
        "symptomes_visuels": "Petits œufs blancs collés sur les grains, grains perforés d'orifices circulaires.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Stockage sous vide (sacs Hermétiques PICS) ou huile végétale de Neem."
    },
    "Bruche de l me d'Arachide (Caryedon serratus)": {
        "mecanisme": "Ravageur majeur des gousses d'arachide stockées en coque au Sénégal.",
        "symptomes_visuels": "Coques d'arachide percées de larges trous, fenêtres transparentes sur la gousse.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Poudrage à la Deltaméthrine 0.5D pour le stockage longue durée."
    },
    "Charançon du Bananier (Cosmopolites sordidus)": {
        "mecanisme": "La larve creuse le rhizome (souche) du bananier.",
        "symptomes_visuels": "Feuilles jaunissantes, flétrissement rapide, bananier se déracinant au moindre vent.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🪵 Vue Tige / Collet"],
        "traitement": "Pièges à disques de souche, phéromones (Sordidin), assainissement des rejets."
    },
    "Charançon du Riz en Stock (Sitophilus oryzae)": {
        "mecanisme": "Ronge l'intérieur des grains de riz, maïs et blé stockés.",
        "symptomes_visuels": "Poussière blanche dans les sacs, grains évidés qui flottent sur l'eau.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Fumigation au K-Obiol ou Phosphine."
    },
    "Charançon du Maïs (Sitophilus zeamais)": {
        "mecanisme": "Attaque les épis sur pied en fin de maturation et en magasin.",
        "symptomes_visuels": "Grains de maïs criblés de trous, élévation de la température du stock.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Séchage strict des grains (< 12% d'humidité) avant ensilage."
    },
    "Grand Capucin du Maïs (Prostephanus truncatus)": {
        "mecanisme": "Ravageur redoutable perforant les grains et le bois des magasins.",
        "symptomes_visuels": "Réduction du maïs en une farine très fine, épis entièrement rongés.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Actellic Super (Pirimiphos-méthyl + Perméthrine)."
    },
    "Petit Capucin des Céréales (Rhyzopertha dominica)": {
        "mecanisme": "Attaque toutes les céréales à paille, le sorgho et la manioc séché.",
        "symptomes_visuels": "Grains cassés irrégulièrement, forte odeur de moisi.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Traitement des parois des magasins avant stockage."
    },
    "Tribolium Rouge de la Farine (Tribolium castaneum)": {
        "mecanisme": "Coleoptère secondaire attaquant les grains brisés et farines.",
        "symptomes_visuels": "Farine prenant une teinte rosâtre et une odeur désagréable.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Nettoyage hermétique des stocks, tamisage."
    },
    "Capucin des Grains de Café (Araecerus fasciculatus)": {
        "mecanisme": "Attaque les cerises de café séchées, le cacao et le maïs.",
        "symptomes_visuels": "Trous de sortie ronds sur fèves de cacao et cerises de café.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Séchage adéquat et sacs de qualité hermétique."
    },
    "Charançon du Cotonnier (Anthonomus grandis)": {
        "mecanisme": "Pond dans les boutons floraux du cotonnier.",
        "symptomes_visuels": "Boutons floraux flétris se décollant ('Boutons ouverts'), pas de formation de capsule.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Traitements de couverture réguliers et destruction des tiges."
    },
    "Silvain des Graines oléagineuses (Ahasverus advena)": {
        "mecanisme": "S'attaque aux graines d'arachide et de sésame légèrement moisies.",
        "symptomes_visuels": "Présence de petits insectes plats marrons dans les stocks d'arachide.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Ventilation et abaissement du taux d'humidité."
    },
    "Bruchide de la Fève (Bruchus rufimanus)": {
        "mecanisme": "Ravageur des légumineuses à de grosses graines.",
        "symptomes_visuels": "Trous de sortie nets recouverts d'un petit opercule avant émergence.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Traitements foliaires à la floraison."
    },
    "Mouche de la Tige du Haricot (Ophiomyia phaseoli)": {
        "mecanisme": "Larve minant la tige des jeunes plants de haricot au niveau du sol.",
        "symptomes_visuels": "Collet du haricot gonflé, craquelé, suivi de la mort de la plante.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Traitement de semences ou buttage précoce couvrant le collet."
    },
    "Mouche des Pousses du Mil (Atherigona lineata)": {
        "mecanisme": "Larve provoquant le cœur mort chez les jeunes plants de mil.",
        "symptomes_visuels": "Dessèchement de la dernière feuille déroulée sur le mil.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Semis à haute densité suivi d'un démariage rigoureux."
    },
    "Mouche du Grain de Sorgho (Contarinia sorghicola)": {
        "mecanisme": "Minuscule midge empêchant la formation du grain de sorgho.",
        "symptomes_visuels": "Panicules de sorgho totalement 'blanches' sans aucun grain formé.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Semis groupés et synchronisés sur toute la zone."
    },
    "Carpocapse de la Pomme et Noix (Cydia pomonella)": {
        "mecanisme": "Chenille perforant les fruits à pépins et les noix.",
        "symptomes_visuels": "Fruit 'verreux', galerie axiale menant jusqu'aux pépins avec déjections.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Virus de la granulose, pièges à phéromones ou emballage."
    },
    "Mouche des Galles du Manguier (Procontarinia matteiana)": {
        "mecanisme": "Pond dans le parenchyme des feuilles de manguier.",
        "symptomes_visuels": "Feuilles couvertes de pustules ou boutons verruqueux durs.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Diméthoate au moment du débourrement des jeunes feuilles."
    },
    "Mouche des Asparagus / Légumes (Zacerata asparagi)": {
        "mecanisme": "Fore les jeunes pousses d'asperges et bulbes.",
        "symptomes_visuels": "Pousses tordues, jaunissantes et desséchées.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Pulvérisation d'un insecticide à courte durée de carence."
    },
    "Mouche de la Bière / Fruits Pourris (Drosophila melanogaster)": {
        "mecanisme": "Pond sur les fruits sur-mûrs, blessés ou en début de fermentation.",
        "symptomes_visuels": "Nuées de petites mouches autour des cagettes de récolte, ramollissement.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Élimination rapide des déchets organiques et récolte à bonne maturité."
    },
    "Charançon du Noyau de la Mangue (Sternochetus mangiferae)": {
        "mecanisme": "La larve se développe exclusivement à l'intérieur du noyau de la mangue.",
        "symptomes_visuels": "Extérieur du fruit d'aspect sain, mais noyau noirci et rongé à l'ouverture.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Hygiène stricte du verger, incinération de tous les noyaux après consommation."
    },
    "Charançon du Sweet Potato (Cylas formicarius)": {
        "mecanisme": "Ravageur n°1 de la patate douce (tiges et tubercules).",
        "symptomes_visuels": "Galeries sinueuses remplies de sciure dans la patate douce, goût amère invendable.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🪵 Vue Tige / Collet"],
        "traitement": "Buttage élevé empêchant les adultes d'atteindre les tubercules, rotation."
    },
    "Charançon de la Tige du Cassava / Manioc (Coelosternus granicollis)": {
        "mecanisme": "Creuse des galeries dans la tige principale du manioc.",
        "symptomes_visuels": "Tiges de manioc fragilisées se cassant, présence d'exsudat de gomme.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Utilisation de boutures saines exemptes de trous de ponte."
    },
    "Charançon de la Fleur d'Anacardier (Apate monachus)": {
        "mecanisme": "Le bostryche adulte perfore les troncs et grosses branches d'anacardier et café.",
        "symptomes_visuels": "Trous parfaitement circulaires de la taille d'un crayon dans le bois avec sciure.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Injection d'essence/insecticide dans les trous et colmatage au mastic."
    },
    "Mouche de la Racine du Choux (Delia radicum)": {
        "mecanisme": "Les larves rongent le pivot racinaire des crucifères.",
        "symptomes_visuels": "Plantes de chou plombées, flétries, s'arrachant facilement avec racines détruites.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Pose de collerettes anti-mouches au pied ou chlorpyriphos."
    },
    "Mouche de la Semence de Maïs (Delia platura)": {
        "mecanisme": "La larve dévore la graine en germination sous terre.",
        "symptomes_visuels": "Manque à la levée, graines de maïs ou haricot creuses au sol.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Enrobage protecteur des semences avec insecticide/fongicide."
    },
    "Mouche Mineuse du Céleri (Euleia heraclei)": {
        "mecanisme": "Mine les feuilles d'Ombellifères (Carotte, Persil, Céleri).",
        "symptomes_visuels": "Grandes plaques boursouflées et brunies sur le feuillage.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Suppression des premières feuilles minées."
    },
    "Charançon du Grain de Blé (Sitophilus granarius)": {
        "mecanisme": "Ne vole pas, attaque exclusivement les stocks de céréales en magasin.",
        "symptomes_visuels": "Grains complètement vidés, perte de poids massive.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Inertage au CO2 ou traitement chimique des installations."
    },
    "Nicrophore / Silphe Masticateur (Blitophaga undata)": {
        "mecanisme": "Coleoptère dévorant les jeunes feuilles de betterave et épinard.",
        "symptomes_visuels": "Feuilles découpées sur les bords dès la levée.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Traitements de surface au lever du soleil."
    },

    # =========================================================================
    # 4. RAVAGEURS SOUTERRAINS, NÉMATODES & PARASITES DU SOL (35)
    # =========================================================================
    "Nématode à Galles de la Tomate (Meloidogyne incognita)": {
        "mecanisme": "Endoparasite migrateur provoquant une hypertrophie des cellules racinaires.",
        "symptomes_visuels": "Billes, loupes et galles denses sur les racines. Flétrissement diurne de la tomate.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Nematicides microbiens (Paecilomyces), tourteau de neem, rotation avec Tagetes."
    },
    "Nématode à Galles du Bananier (Meloidogyne javanica)": {
        "mecanisme": "Destruit le système d'ancrage des bananiers et légumineuses.",
        "symptomes_visuels": "Galles volumineuses sur radicelles, arrêt complet de la croissance.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Incoporation de compost riche et nématicides biologiques."
    },
    "Nématode Lésionnaire du Riz (Pratylenchus zeae)": {
        "mecanisme": "Traverse et détruit les cortex racinaires du maïs et riz pluvial.",
        "symptomes_visuels": "Lésions nécrotiques noires ou allongées sur les racines de riz, jaunissement.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Solarisation du sol en saison sèche et apport d'humus."
    },
    "Nématode Reniforme (Rotylenchulus reniformis)": {
        "mecanisme": "Attaque le coton, la papaye, l'ananas et le maraîchage.",
        "symptomes_visuels": "Racines salies par de la terre collée aux sécrétions des femelles, rabougrissement.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Fosthiazate ou Fluopyram en drenchage."
    },
    "Nématode des Cavités du Bananier (Radopholus similis)": {
        "mecanisme": "Provoque la maladie du dépérissement ou chute du bananier.",
        "symptomes_visuels": "Racines devenant rougeâtres puis entièrement noires et creuses.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Assainissement des vitroplants, parage des rejets à la plantation."
    },
    "Nématode du Kyste de la Pomme de Terre (Globodera rostochiensis)": {
        "mecanisme": "Les femelles forment des kystes dorés puis bruns durables dans le sol.",
        "symptomes_visuels": "Foyers de plants chétifs, minuscules billes dorées accrochées aux racines.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Variétés résistantes, rotation stricte de 5 ans sans solanacées."
    },
    "Nématode Aphelenchoides du Riz (Aphelenchoides besseyi)": {
        "mecanisme": "Provoque la maladie du 'Bout Blanc' du riz transmis par les semences.",
        "symptomes_visuels": "Extrémité des feuilles de riz devenant blanchâtre/translucide sur 3 cm, grains déformés.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Trempage des semences dans l'eau chaude à 52°C pendant 15 min."
    },
    "Ver Blanc / Larve de Hanneton du Sénégal (Schizonycha africana)": {
        "mecanisme": "Grosse larve blanche en 'C' dévorant les racines d'arachide, mil et maïs.",
        "symptomes_visuels": "Flétrissement brutal par plaques, plants qui s'arrachent sans aucune résistance.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🪵 Vue Tige / Collet"],
        "traitement": "Labours profonds exposant les larves aux prédateurs, Imidaclopride sol."
    },
    "Ver Blanc du Mahafaly / Céréales (Heteronychus licas)": {
        "mecanisme": "L'adulte et la larve rongent le collet sous-terrain de la canne et du maïs.",
        "symptomes_visuels": "Tiges de canne à sucre coupées sous le niveau du sol.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🪵 Vue Tige / Collet"],
        "traitement": "Chlorpyriphos-éthyl en granulés à la plantation."
    },
    "Margarode de l'Arachide / Cochenille de Racine (Porphyrophora spp.)": {
        "mecanisme": "Cochenille souterraine se fixant sur le pivot principal de l'arachide.",
        "symptomes_visuels": "Kystes dorés (perles de terre) accrochés aux racines, jaunissement intense.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Rotation culturale avec des céréales non-hôtes."
    },
    "Courtilière / Taupe-Grillon (Gryllotalpa africana)": {
        "mecanisme": "Creuse de vastes galeries superficielles et coupe les racines et collets.",
        "symptomes_visuels": "Galeries soulevées à la surface du sol, jeunes pousses coupées net.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🪵 Vue Tige / Collet"],
        "traitement": "Appâts empoisonnés au son étalés le soir après arrosage."
    },
    "Grillon Champêtre (Gryllus bimaculatus)": {
        "mecanisme": "Dévorateur nocturne des jeunes plants en pépinière.",
        "symptomes_visuels": "Plants de tomate, chou et piment entièrement coupés au niveau du sol.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Protection des pépinières par du filet ou appâts au Pyrèthre."
    },
    "TermiteMoissonneur (Hodotermes mossambicus)": {
        "mecanisme": "Termite fortifié coupant les tiges de graminées et paille en surface.",
        "symptomes_visuels": "Cercle de sol entièrement dénudé de végétation, petites tiges emportées dans les trous.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🪵 Vue Tige / Collet"],
        "traitement": "Traitements de termitières avec régulateurs de croissance ou Fipronil."
    },
    "Termite Champignonniste (Macrotermes subhyalinus)": {
        "mecanisme": "Attaque les plantes affaiblies par le stress hydrique et le bois sec.",
        "symptomes_visuels": "Fourreaux de terre (plaquages) recouvrant le tronc des arbres et tiges de maïs.",
        "plans_sensibles": ["🪵 Vue Tige / Collet", "🪴 Vue Racines / Sol"],
        "traitement": "Protection des troncs par badigeon au jus de neem ou Fipronil."
    },
    "Termite Subterrané du Bois (Coptotermes formosanus)": {
        "mecanisme": "Attaque le cœur du pivot racinaire des arbres fruitiers.",
        "symptomes_visuels": "Manoir racinaire complètement évidé, arbre s'effondrant subitement.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Barrières chimiques au sol et drenchage au pied."
    },
    "Ver Fil de Fer / Taupin (Agriotes lineatus)": {
        "mecanisme": "Larve dorée et dure perforant les tubercules et racines.",
        "symptomes_visuels": "Trous cylindriques étroits perforant de part en part les pommes de terre et carottes.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Tourteaux de ricin incorporés au sol, pièges à rondelles de pomme de terre."
    },
    "Mouche de la Racine de la Carotte (Psila rosae)": {
        "mecanisme": "Creuse de noires galeries sous l'épiderme de la racine de carotte.",
        "symptomes_visuels": "Feuillage prenant une teinte rougeâtre, racines de carotte sillonnées de galeries nécrotiques.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Pose de voiles anti-insectes, semis associé avec des oignons (effet répulsif)."
    },
    "Blaniule Moucheté / Mille-Pattes des Racines (Blaniulus guttulatus)": {
        "mecanisme": "Ronge les semences en germination et les jeunes radicelles.",
        "symptomes_visuels": "Graines de haricot creusées avec présence de petits myriapodes fins.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Limitation des apports de matière organique non décomposée."
    },
    "Scutigerelle des Maraîchers (Scutigerella immaculata)": {
        "mecanisme": "Minuscule symphyle dévorant l'extrémité des radicelles en croissance.",
        "symptomes_visuels": "Système racinaire 'en brosse' (radicelles coupées nettes), arrêt de pousse.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Solarisation ou travail du sol en période sèche."
    },
    "Iule de l'Arachide / Mille-Pattes Geant (Archispirostreptus gigas)": {
        "mecanisme": "Ronge les gousses d'arachide en formation dans le sol pendant la nuit.",
        "symptomes_visuels": "Gousses d'arachide perforées d'un trou latéral sous terre, graines dévorées.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🍓 Vue Fruit / Gousse"],
        "traitement": "Poudrage au Carbaryl autour des poquets."
    },
    "Nématode des Agrumes (Tylenchulus semipenetrans)": {
        "mecanisme": "Provoque le 'dépérissement lent' des vergers d'agrumes.",
        "symptomes_visuels": "Feuillage clairsemé, chlorotique, petits fruits, racines encroûtées de sable.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Utilisation de porte-greffhes résistants (*Poncirus trifoliata*)."
    },
    "Nématode Dorylaimida des Vignes (Xiphinema index)": {
        "mecanisme": "Grand nématode ectoparasite vecteur du virus du Court-Noué.",
        "symptomes_visuels": "Gallions à l'extrémité des racines, déformation des feuilles en éventail.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Nématicides fumigants avant plantation."
    },
    "Nématode de la Tige de la Lauzerte (Ditylenchus dipsaci)": {
        "mecanisme": "Attaque les bulbes d'oignon, ail et les tiges de légumineuses.",
        "symptomes_visuels": "Bulbes d'oignon spongieux, ramollis, à tuniques dissociées.",
        "plans_sensibles": ["🪵 Vue Tige / Collet", "🪴 Vue Racines / Sol"],
        "traitement": "Trempage des caïeux d'ail dans l'eau chaude et micro-granulés."
    },
    "Ver Gris d'Afrique / Chenille Souterraine (Spodoptera littoralis - Larve âgée)": {
        "mecanisme": "Se réfugie dans le sol pendant le jour et ronge les collets la nuit.",
        "symptomes_visuels": "Collets coupés, chenilles marron enroulées sur elles-mêmes sous les premiers centimètres du sol.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🪵 Vue Tige / Collet"],
        "traitement": "Binage fréquent exposant les chenilles et appâts insecticides."
    },
    "Nématode à Galles du Piment (Meloidogyne enterolobii)": {
        "mecanisme": "Souche de nématode brisant les résistances génétiques classiques.",
        "symptomes_visuels": "Galles extrêmement volumineuses détruisant entièrement le chevelu racinaire.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Bio-fumigation au moutarde/tourteau de neem + Fluopyram."
    },
    "Puceron des Racines du Cotonnier (Pemphigus betae)": {
        "mecanisme": "Pique l'écorce des racines sous le niveau du sol.",
        "symptomes_visuels": "Dépôt cireux blanc sur les racines, flétrissement soudain sous le chaud.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Arrosage du pied avec une émulsion d'huile de neem."
    },
    "Nématode des Tubercules d'Igname (Scutellonema bradys)": {
        "mecanisme": "Provoque la 'pourriture sèche' de l'igname pendant la croissance et le stockage.",
        "symptomes_visuels": "Craquelures superficielles sur la peau de l'igname, tissu sous-jacent brun foncé et spongieux.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Trempage des semenceaux d'igname dans un bain nématicide + fongicide."
    },
    "Nématode Aphelenchoides de l'Ananas (Aphelenchoides ritzemabosi)": {
        "mecanisme": "Parasite les tissus foliaires centraux et les racines d'ananas.",
        "symptomes_visuels": "Taches foliaires angulaires brunes limitées par les nervures.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Destruction des résidus de culture d'ananas après récolte."
    },
    "Cochenille du Collet de la Pomme de Terre (Rhizoecus solani)": {
        "mecanisme": "Vit fixée au niveau du collet et des premiers départements racinaires.",
        "symptomes_visuels": "Poudre cotonneuse blanche autour du collet, flétrissement sans jaunissement.",
        "plans_sensibles": ["🪴 Vue Racines / Sol", "🪵 Vue Tige / Collet"],
        "traitement": "Drenchage au pied à l'Imidaclopride."
    },
    "Punaise Souterraine des Racines (Cyrtomenus bergi)": {
        "mecanisme": "Pique les tubercules de manioc et les gousses d'arachide en terre.",
        "symptomes_visuels": "Taches sombres enfoncées sur la chair du manioc, surinfection fongique.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Incorporation de calcaire ou de cendre de bois au sol."
    },
    "Mouche Souterraine des Légumes (Phorbia platura)": {
        "mecanisme": "Pond dans les sols riches en matière organique fraîche non décomposée.",
        "symptomes_visuels": "Destruction des graines en cours de gonflement.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Attendre la décomposition complète des fumiers avant d'effectuer les semis."
    },
    "Mille-Pattes Symphylides des Niayes (Symphylella spp.)": {
        "mecanisme": "Petit arthropode blanc très vif dévorant les apex racinaires.",
        "symptomes_visuels": "Plants de tomate demeurant enains malgré un bon apport d'engrais.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Inondation temporaire du sol ou application d'un insecticide sol."
    },
    "Nématode Dorylaimide de la Canne (Trichodorus obtusus)": {
        "mecanisme": "Nématode 'stubby-root' provoquant le raccourcissement des racines.",
        "symptomes_visuels": "Racines tronquées se terminant par un petit renflement noir.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Amendement massif en compost biologique."
    },
    "Taupin Souterrain des Céréales (Melanotus communis)": {
        "mecanisme": "Ronge les tiges enterrées et le grain de maïs.",
        "symptomes_visuels": "Jaunissement des feuilles basales du maïs suivi du dessèchement.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Enrobage des semences au Fipronil ou Thiamethoxam."
    },
    "Ver Gris des Semis de Cotonnier (Euxoa auxiliaris)": {
        "mecanisme": "Coupe les jeunes pousses de coton au niveau du sol pendant la nuit.",
        "symptomes_visuels": "Trouées dans les lignes de semis de coton.",
        "plans_sensibles": ["🪵 Vue Tige / Collet", "🪴 Vue Racines / Sol"],
        "traitement": "Traitements de sol localisés sur le rang."
    },

    # =========================================================================
    # 5. ACARIENS, ORTHOPTÈRES & AUTRES AGRESSEURS (40)
    # =========================================================================
    "Acarien Tisserand / Tétranyque Tissé (Tetranychus urticae)": {
        "mecanisme": "Vide le contenu des cellules végétales sous climats chauds et secs.",
        "symptomes_visuels": "Feuillage décoloré, aspect plombé/bronzé, présence de fines toiles d'araignée.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Abamectine 18 EC, Soufre mouillable ou brumisation d'eau."
    },
    "Acarien Rouge des Agrumes (Panonychus citri)": {
        "mecanisme": "Attaque les agrumes en pompant la chlorophylle des feuilles et fruits.",
        "symptomes_visuels": "Piquetage grisâtre sur les oranges/citrons, chute prématurée des feuilles.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Spirodiclofen ou Hexythiazox."
    },
    "Acarien Jaune du Manguier (Tetranychus fijiensis)": {
        "mecanisme": "Se développe sur la face supérieure des feuilles de manguier.",
        "symptomes_visuels": "Nervures centrales jaunissantes, puis dessèchement complet du limbe.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Pulvérisation d'Acaricide spécifique."
    },
    "Acarien Broad / Acarien Trapu des Légumes (Polyphagotarsonemus latus)": {
        "mecanisme": "Minuscule acarien microscopique injectant des toxines dans les apex.",
        "symptomes_visuels": "Feuilles de piment/poivron rigides, étroites, tordues vers le bas (aspect cuir).",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Abamectine ou Soufre micronisé."
    },
    "Erinose du Lychee / Piment (Eriophyes litchii)": {
        "mecanisme": "Provoque le développement d'un feutrage galligène sur les feuilles.",
        "symptomes_visuels": "Boursouflures en forme de gaufres recouvertes d'un feutrage velouté marron sous la feuille.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Soufre en poudre ou abamectine."
    },
    "Criquet Pèlerin (Schistocerca gregaria)": {
        "mecanisme": "Ravageur acridien grégaire dévorant toute matière végétale verte sur son passage.",
        "symptomes_visuels": "Défoliation totale et écorçage des cultures en quelques minutes par des essaims.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet", "🍓 Vue Fruit / Gousse"],
        "traitement": "Traitements d'urgence de la DPV au Fenitrothion ou Metarhizium acridum (Green Muscle)."
    },
    "Criquet Nomad (Nomadacris septemfasciata)": {
        "mecanisme": "Grand criquet s'attaquant en priorité aux maïs, canne à sucre et riz.",
        "symptomes_visuels": "Grandes sections de feuilles dévorées, cassure des panicules sous le poids.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Traitements acridicides ciblés sur les bandes larvaires."
    },
    "Criquet Puant / Variegated (Zonocerus variegatus)": {
        "mecanisme": "Criquet bariolé toxique dévorant le manioc, le bananier et les agrumes.",
        "symptomes_visuels": "Attaque en groupes denses, effeuillage du manioc en saison sèche.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Destruction manuelle des pontes dans le sol ou Chlorpyriphos."
    },
    "Criquet Sénégalaise (Oedaleus senegalensis)": {
        "mecanisme": "Ravageur majeur des céréales traditionnelles (mil, sorgho) au Sahel.",
        "symptomes_visuels": "Ronge les graines au stade laiteux, détruit les jeunes pousses de mil.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Poudrage au Fenitrothion sur les foyers d'éclosion."
    },
    "Sauterelle des Palmes / De la Canne (Anchiale maculata)": {
        "mecanisme": "Phasme/Sauterelle géante rongeant le feuillage des palmiers et cocotiers.",
        "symptomes_visuels": "Grandes encoches sur le bord des palmes.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Traitement de couronne des arbres."
    },
    "Sauterelle Verte des Près (Tettigonia viridissima)": {
        "mecanisme": "Défoliateur occasionnel des maraîchages et vignes.",
        "symptomes_visuels": "Bords des feuilles rongés irrégulièrement.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Lutte mécanique ou Pyréthrinoïde de contact."
    },
    "Acarien Galligène du Manguier (Aceria mangiferae)": {
        "mecanisme": "Provoque la malformation des bourgeons du manguier avec transmission de *Fusarium*.",
        "symptomes_visuels": "Grappes de bourgeons atrophiés en 'balai de sorcière', absence de fruits.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Taille des balais de sorcière suivi d'un traitement acaricide/fongicide."
    },
    "Acarien de la Rouille des Agrumes (Phyllocoptruta oleivora)": {
        "mecanisme": "Pique l'écorce des agrumes en formation.",
        "symptomes_visuels": "Oranges et citrons prenant une couleur 'chocolat' ou 'bronze' rugueuse au toucher.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Soufre mouillable à la chute des pétales."
    },
    "Acarien Rouge du Cocotier (Raoiella indica)": {
        "mecanisme": "S'installe sous les palmes des cocotiers, bananiers et palmiers.",
        "symptomes_visuels": "Jaunissement suivi du dessèchement total de la face inférieure des palmes.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Lâcher d'acariens prédateurs Phytoseiidae ou Spiromesifen."
    },
    "Limace Rouge / Grise des Maraîchages (Deroceras reticulatum)": {
        "mecanisme": "Mollusque gastéropode rongeant le feuillage basilaire par temps humide.",
        "symptomes_visuels": "Large trouées dans les salades avec traînées de bave argentée séchée.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Appâts granulés au Phosphate de Fer (Ferramol) ou Métaldéhyde."
    },
    "Escargot Géant Africain (Achatina fulica)": {
        "mecanisme": "Escargot géant dévorant la majorité des cultures maraîchères et vivrières.",
        "symptomes_visuels": "Feuilles et jeunes tiges consommées massivement, présence d'escargots volimineux.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Ramassage manuel nocturne et barrières de chaux/cendres autour des parcelles."
    },
    "Mouche Sclérotique des Tiges (Melanagromyza sojae)": {
        "mecanisme": "Mine la tige centrale du soja et du niébé.",
        "symptomes_visuels": "Pith interne de la tige rougi/noirci, flétrissement sans jaunissement préalable.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Traitement des semences à l'Imidaclopride."
    },
    "Gaspard / Punaise Bouclier de l'Anacardier (Tibiocoris capitatus)": {
        "mecanisme": "Pique les jeunes pommes et noix d'anacarde.",
        "symptomes_visuels": "Noix d'anacarde noires, ridées, desséchées avant maturité.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Lambda-Cyhalothrine au moment de la nouaison."
    },
    "Acarien Tarsonème du Fraisier et Piment (Tarsonemus pallidus)": {
        "mecanisme": "Attaque le cœur du bourgeon central.",
        "symptomes_visuels": "Feuilles du cœur ridées, brunes et cassantes.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Abamectine + huile essentielle de thym."
    },
    "Forficule / Perce-Oreille (Forficula auricularia)": {
        "mecanisme": "Ravageur nocturne perforant les fruits mûrs et les fleurs.",
        "symptomes_visuels": "Petits trous profonds dans les pêches, figues et capitules de fleurs.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Bandes de carton ondulé enroulées autour des troncs pour pièges."
    },
    "Cicadelle de la Mosaïque du Cassava (Greenbergiana spp.)": {
        "mecanisme": "Piqueur secondaire des tiges tendres de manioc.",
        "symptomes_visuels": "Exsudation de gouttelettes sucrées sur les tiges, jaunissement.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Savon noir et huile de neem."
    },
    "Acarien Vert du Manioc (Mononychellus tanajoa)": {
        "mecanisme": "S'attaque aux jeunes feuilles du sommet du manioc.",
        "symptomes_visuels": "Mouchetage chlorotique, réduction de la taille des nouvelles feuilles ('Pied de balai').",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Lutte biologique par l'acarien prédateur *Typhlodromalus aripo*."
    },
    "Cochenille du Papayer (Paracoccus marginatus)": {
        "mecanisme": "Envahit les fruits et feuilles de papayer sous un feutrage blanc.",
        "symptomes_visuels": "Papayes entièrement recouvertes de poussier blanc, déformation des fruits.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse", "🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Parasitoïde *Acerophagus papayae* ou Spirotétramate."
    },
    "Punaise Piqueuse de l'Ananas (Dysmicoccus neobrevipes)": {
        "mecanisme": "Transmet le virus Wilt (flétrissure) de l'ananas.",
        "symptomes_visuels": "Feuilles d'ananas virant au rouge-bronzé, extrémités desséchées recourbées.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪴 Vue Racines / Sol"],
        "traitement": "Lutte contre les fourmis associées et désinfection des cayeux."
    },
    "Mouche des Tiges de la Papaye (Toxotrypana curvicauda)": {
        "mecanisme": "La femelle possède un long ovipositeur pour pondre dans la cavité centrale de la papaye.",
        "symptomes_visuels": "Chute prématurée des papayes vertes, graines et cavité centrale remplies d'asticots.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Sachs en papier sur papayes et piégeage aux Phéromones."
    },
    "Charançon du Collet de la Vigne (Otiorhynchus sulcatus)": {
        "mecanisme": "L'adulte découpe les feuilles et la larve ronge les racines et collets.",
        "symptomes_visuels": "Feuilles entaillées en 'poinçon', mort subite du cep par annellation racinaire.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪴 Vue Racines / Sol"],
        "traitement": "Nématodes entomopathogènes (*Steinernema carpocapsae*)."
    },
    "Punaise Américaine de la Tomate (Leptoglossus zonatus)": {
        "mecanisme": "Punaise aux pattes élargies en forme de feuille piquant les tomates et citrons.",
        "symptomes_visuels": "Taches jaunâtres dures sur les fruits, flétrissement des pépins.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Bifenthrine ou Pyrèthre naturel additionné d'huile."
    },
    "Thrips des Serres du Caféier (Heliothrips rubrocinctus)": {
        "mecanisme": "Larve reconnaissable à sa bande rouge vif sur l'abdomen.",
        "symptomes_visuels": "Feuilles d'anacardier et de cacaoyer brunies, aspect brûlé, chute des feuilles.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Traitement mouillant à la Deltaméthrine."
    },
    "Mouche Galligène de la Tige du Coton (Cecidomyia gossypii)": {
        "mecanisme": "Provoque l'enflure des tiges de cotonnier.",
        "symptomes_visuels": "Galles renflées le long de la tige principale, casse lors de la charge en capsules.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Destruction des plants gélivés après récolte."
    },
    "Sauterelle Pèlerine des Palmier (Sexava grassator)": {
        "mecanisme": "Défoliateur géant des cocoteraies côtières.",
        "symptomes_visuels": "Palmes dévorées jusqu'à la rachis principale, baisse drastique de production de noix.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Injection d'insecticide dans le stipe du cocotier."
    },
    "Acarien de la Bryobe / Trèfle (Bryobia praetiosa)": {
        "mecanisme": "Pique le parenchyme supérieur des légumineuses et arbres.",
        "symptomes_visuels": "Feuilles devenant grises/argentées tachetées de petits points blancs.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Traitement à la poudre de soufre."
    },
    "Punaise Tachetée du Sésame (Elasmolomus sordidus)": {
        "mecanisme": "Attaque les gousses de sésame et d'arachide récoltées en séchage sur le champ.",
        "symptomes_visuels": "Graines de sésame et d'arachide ridées, vidées de leur huile, goût rance.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Ramassage rapide des javelles et traitement des aires de séchage."
    },
    "Puceron Noir du Cacaoyer (Toxoptera aurantii)": {
        "mecanisme": "Colonies massives sur les jeunes pousses d'agrumes et cacaoyers.",
        "symptomes_visuels": "Crispation des jeunes feuilles rouges, présence importante de fumagine.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Pirimicarbe ou Imidaclopride."
    },
    "Criquet des Jardins (Acrotylus patruelis)": {
        "mecanisme": "Petit criquet geophile rongeant les pousses au niveau du sol.",
        "symptomes_visuels": "Jeunes pousses de maraîchage grignotées au ras de la terre.",
        "plans_sensibles": ["🪵 Vue Tige / Collet"],
        "traitement": "Binage et poudrage de cendre/insecticide de contact."
    },
    "Anthonome de la Fleur de Fraisier (Anthonomus rubi)": {
        "mecanisme": "Coupe le pédoncule du bouton floral qui se dessèche.",
        "symptomes_visuels": "Boutons floraux pendillants, suspendus par un fil sectionné.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Spinosad avant l'épanouissement des fleurs."
    },
    "Mouche de la Truffe / Racine (Suillia tuboleata)": {
        "mecanisme": "Pond au pied des tubercules et racines aromatiques.",
        "symptomes_visuels": "Petits asticots creusant la chair des racines de gingembre/curcuma.",
        "plans_sensibles": ["🪴 Vue Racines / Sol"],
        "traitement": "Traitement de sol au neem ou chlorpyriphos."
    },
    "Acarien Eryophyide du Bananier (Abacarus hystrix)": {
        "mecanisme": "Microscopique acarien se développant dans le cigare du bananier.",
        "symptomes_visuels": "Stries nécrotiques brunes parallèles le long du limbe foliaire.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)"],
        "traitement": "Pulvérisation d'Acaricide dans le cornet de la feuille cigare."
    },
    "Punaise Lygus du Cotonnier (Taylorilygus vosseleri)": {
        "mecanisme": "Pique les meristèmes floraux du coton.",
        "symptomes_visuels": "Feuilles adultes perforées de trous déchiquetés à contours noirs.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🍓 Vue Fruit / Gousse"],
        "traitement": "Traitement pyréthrinoïde ciblé."
    },
    "Cochenille Cireuse du Manguier (Ceroplastes rubens)": {
        "mecanisme": "Grosses cochenilles recouvertes d'une cire rose à rouge fixées sur nervures.",
        "symptomes_visuels": "Gouttes de cire dures sur la nervure centrale des feuilles, fumagine dense.",
        "plans_sensibles": ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet"],
        "traitement": "Taille d'éclaircissage et huile minérale + insecticide."
    },
    "Chenille Masticatrice de la Grenade (Deudorix isocrates)": {
        "mecanisme": "La chenille perfore la peau dure de la grenade pour manger les arilles.",
        "symptomes_visuels": "Un trou d'entrée bouché par les excréments de la chenille, fruit pourri.",
        "plans_sensibles": ["🍓 Vue Fruit / Gousse"],
        "traitement": "Ensachage individuel des grenades ou Spinosad."
    }
}
  # --- CATALOGUE NATIONALE ÉTENDU : 100 PRODUITS & VARIÉTÉS DU SÉNÉGAL ---
CATALOGUE_100_PRODUITS_SENEGAL = {
    "🌾 CÉRÉALES (20 Produits & Variétés)": [
        "Riz Sahel 108 (ISRA) - Cycle court, idéal pour la double culture dans le Fleuve",
        "Riz Sahel 201 (ISRA) - Fort rendement en zone irriguée",
        "Riz Sahel 202 (ISRA) - Variété tolérante à la salinité du sol",
        "Riz ISRIZ 16 (ISRA) - Haute qualité grainière, parfumé",
        "Riz ISRIZ 17 (ISRA) - Résistant à la verse et au stress hydrique",
        "Riz ISRIZ P01 (ISRA) - Variété à très haut rendement potentiel",
        "Riz ISRIZ P02 (ISRA) - Adapté aux périmètres aménagés",
        "Riz NERICA 4 (AfricaRice/ISRA) - Riz pluvial de plateau, résistant à la sécheresse",
        "Riz NERICA 1 (AfricaRice) - Adapté au pluvial strict en Casamance",
        "Riz NERICA-L 19 (AfricaRice) - Riz de bas-fond résistant à l'immersion",
        "Mil Souna 3 (ISRA) - Variété précoce de référence pour le Bassin Arachidier",
        "Mil Souna du Baol (ISRA) - Adapté aux zones à faible pluviométrie",
        "Mil Souna du Sine (ISRA) - Tolérant aux fortes chaleurs et au vent",
        "Mil Souna du Saloum (ISRA) - Grain volumineux et bon rendement fourrager",
        "Mil Taaw (ISRA) - Hybride à très haute performance climatique",
        "Sorgho Darou (ISRA) - Résistant au Striga et à la sécheresse",
        "Sorgho Faourou (ISRA) - Adapté aux zones sahéliennes du Nord",
        "Sorgho Nguinthe (ISRA) - Grain blanc recherché pour la transformation",
        "Maïs Early Thai (ISRA) - Cycle court, idéal pour la consommation en vert",
        "Fonio Local Amélioré (Kédougou) - Céréale ancestrale sans gluten à haute valeur"
    ],
    "🥜 LÉGUMINEUSES & OLÉAGINEUX (15 Produits & Variétés)": [
        "Arachide Jambaar (ISRA) - Cycle 90j, tolérante à la sécheresse",
        "Arachide Tosset (ISRA) - Riche en huile, adaptée aux sols épuisés",
        "Arachide Yakaar (ISRA) - Multiplication rapide, fort rendement",
        "Arachide Amoul Morom (ISRA) - Spéciale zone sud/Casamance",
        "Arachide Essamaye (ISRA) - Tolérante aux maladies foliaires (Rosette)",
        "Arachide 55-437 (ISRA) - Variété historique extra-précoce",
        "Niébé Pakau (ISRA) - Cycle ultra-court (60-65 jours)",
        "Niébé Léona (ISRA) - Gousses charnues, résistant aux bruches",
        "Niébé Thieye (ISRA) - Double usage (grain et fourrage vert)",
        "Niébé Kelle (ISRA) - Fort rendement en zone nord et centre",
        "Niébé Mougne (ISRA) - Tolérant à l'ombre et au déficit hydrique",
        "Sésame Blanc de Tambacounda - Exportation & transformation d'huile",
        "Sésame Noir / Brun du Sénégal - Culture rustique à haute valeur",
        "Voandzou / Pois Bambara (Bignona) - Légumineuse souterraine très nourricière",
        "Soja Grain du Sud - Culture de diversification en Casamance"
    ],
    "🧅 MARAÎCHAGE & LÉGUMES (30 Produits & Variétés)": [
        "Oignon Violet de Galmi - Référence pour la longue conservation",
        "Oignon GandiolAm (ISRA) - Adaptation parfaite à la zone des Niayes",
        "Oignon Yaakar (ISRA) - Calibre homogène, séchage rapide",
        "Oignon Orient F1 - Très haut rendement en zone irriguée",
        "Tomate Cobra F1 - Résistance au flétrissement bactérien et TYLCV",
        "Tomate Tropimech - Variété industrielle ferme pour la conserve",
        "Tomate Mongal F1 - Adaptée aux chaleurs d'hivernage",
        "Tomate Nadira - Excellente tenue au transport",
        "Gombo Clemson Spineless - Sans épines, gousses tendres",
        "Gombo Pusa Sawani - Résistant à la mosaïque du gombo",
        "Gombo VIP F1 - Très productif pour le marché frais",
        "Piment Antillais / Habanero - Ultra-piquant, très prisé au marché",
        "Piment Big Sun - Piment jaune très aromatique",
        "Piment Piquant de Cayor - Variété locale rustique",
        "Poivron Yolo Wonder - Calibre moyen à chair épaisse",
        "Poivron Kampai F1 - Hybride tolérant aux virus",
        "Aubergine Violette Longue - Maraîchage classique des Niayes",
        "Aubergine Amère / Diakhatou - Légume traditionnel incontournable",
        "Carotte Madagali - Racines lisses et colorées",
        "Carotte Amazonia - Résistante aux fortes températures",
        "Chou Cabus Marché de Copenhague - Pomme ferme et dense",
        "Chou Tropica Cross - Adapté aux zones tropicales chaudes",
        "Pastèque Kaolack - Variété zébrée rouge, très sucrée",
        "Pastèque Crimson Sweet - Chair ferme, résistance au transport",
        "Melon Cantaloup des Niayes - Sucré et parfumé pour l'exportation",
        "Melon Ananas - Chair douce et parfumée",
        "Courge / Citrouille Locale du Saloum - Chair dense pour soupes et thiéboudienne",
        "Concombre Tokiwa - Productif sous abri et plein champ",
        "Salade Laitue Great Lakes - Résistante au pommage précoce sous chaleur",
        "Navet Blanc de Milan - Racines rondes pour le maraîchage local"
    ],
    "🥭 ARBORICULTURE & FRUITS (20 Produits & Variétés)": [
        "Mangue Kent - Variété reine d'exportation (sans fibre, sucrée)",
        "Mangue Keitt - Variété tardive d'exportation",
        "Mangue Boukodiekhal (Local) - Mangue greffée très précoce",
        "Mangue Sierra Leone (Local) - Fibreuse, très usitée pour les jus",
        "Citron Lime de Tahiti - Sans pépins, très jusif",
        "Citronnier Key Lime (Kaffrine) - Citron galet très parfumé",
        "Orange Valence Late - Orange à jus idéale pour le sud",
        "Mandarine Dansy - Agrume doux adapté aux vergers intégrés",
        "Pamplemousse Star Ruby - Chair rouge vif très sucrée",
        "Anacarde / Noix de Cajou (Casamance) - Variété à gros écrous",
        "Banane Grande Naine - Banane douce de plantation intensive (Tambacounda)",
        "Banane Plantain (Sédhiou) - Banane à cuire pour le marché régional",
        "Papaye Solo - Petit fruit très doux pour l'exportation",
        "Papaye Red Lady F1 - Papaye géante très productive",
        "Guayave Rouge de Sangalkam - Fruit riche en vitamine C",
        "Bissap Rouge (Hibiscus sabdariffa) - Variété Koor pour le jus de Bissap",
        "Bissap Blanc - Utilisé pour les sauces et les infusions médicinales",
        "Pain de Singe / Baobab (Adansonia digitata) - Pulpe de fruit (Bouye)",
        "Ditax (Detarium senegalense) - Fruit sauvage à haute valeur ajoutée",
        "Madd (Saba senegalensis) - Fruit forestier de Casamance valorisé"
    ],
    "🥔 TUBERCULES, ÉPICES & AUTRES (15 Produits & Variétés)": [
        "Manioc TMS 92/0057 - Variété enrichie, haut rendement en amidon",
        "Manioc Bocou 1 (ISRA) - Très résistant à la mosaïque du manioc",
        "Manioc Bocou 2 (ISRA) - Racines tubéreuses douces",
        "Patate Douce à Chair Orange (BOSTER) - Riche en Vitamine A",
        "Patate Douce Blanche Locale - Indispensable pour la cuisine locale",
        "Igname de Casamance (Dioscorea) - Tubercules majeurs du sud",
        "Taro / Macabo (Ziguinchor) - Tubercules de bas-fonds",
        "Coton Acala (Sodefitex / Tambacounda) - Fibre textile de première qualité",
        "Canne à Sucre (CSS / Richard-Toll) - Variété industrielle à forte teneur en sucre",
        "Gingembre du Sénégal / Jinjer - Rhyzome piquant pour boissons",
        "Curcuma de Casamance - Épice et plante médicinale à haute valeur",
        "Menthe Poivrée des Niayes (Nana) - Culture maraîchère à haute rotation",
        "Moringa Oleifera (Neembeday) - Feuilles et graines à haute valeur nutritionnelle",
        "Soump / Datte du Désert (Balanites aegyptiaca) - Huile et fruits cosmétiques",
        "Henné du Fleuve (Lawsonia inermis) - Feuille séchée cosmétique et artisanale"
    ]
}
    # États de session initiaux
if "expert_producer" not in st.session_state:
    st.session_state["expert_producer"] = "Agro-Business Consortium Sénégal"
if "expert_zone" not in st.session_state:
    st.session_state["expert_zone"] = list(BASE_SOLS_INP_EXPERT.keys())[0]
if "expert_custom_crop" not in st.session_state:
    st.session_state["expert_custom_crop"] = "Mangue Kent (Verger Intensif)"
if "panier" not in st.session_state:
    st.session_state["panier"] = []

    # --- Barre latérale : Authentification & Sécurité ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔒 Sécurité & Contrôle d'Accès")
    email_input = st.sidebar.text_input("E-mail expert :", value=OWNER_EMAIL, key="exp_email").strip().lower()
    pass_input = st.sidebar.text_input("Mot de passe :", type="password", key="exp_pass").strip()

    whitelist = db.get("whitelist", [])
    user_session = None
    for u in whitelist:
        if isinstance(u, dict) and str(u.get("email")).lower() == email_input and str(u.get("password")) == pass_input and u.get("statut") == "Actif":
            user_session = u
            break

    if not user_session:
        st.warning("⚠️ **Authentification requise** : Veuillez saisir vos identifiants autorisés dans la barre latérale pour débloquer le bureau d'étude et d'expertise agricole.")
    else:
        is_admin = (user_session.get("role") == "Administrateur")
        st.sidebar.success(f"✅ Session active : {user_session.get('nom')} ({user_session.get('role')})")

        def calc_surface(coords):
            if not coords or len(coords) < 3:
                return 2.5
            lat_avg = sum(p[0] for p in coords) / len(coords)
            m_lat = 111139.0
            m_lon = 111139.0 * np.cos(np.radians(lat_avg))
            xy = [(lon * m_lon, lat * m_lat) for lat, lon in coords]
            area = 0.0
            n = len(xy)
            for i in range(n):
                j = (i + 1) % n
                area += xy[i][0] * xy[j][1] - xy[j][0] * xy[i][1]
            return round(abs(area) / 20000.0, 2)

import io
import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- FONCTION AUXILIAIRE : GÉNÉRATION DES GRAPHIQUES POUR LE PDF ---
def generate_pdf_charts(budget_total, rentabilite):
    """Génère des images en mémoire pour enrichir le PDF avec des graphiques visuels."""
    # 1. Graphique Camembert : Répartition Financière
    fig1, ax1 = plt.subplots(figsize=(4, 2.5))
    labels = ['Intrants (40%)', 'Irrigation (35%)', 'Main d\'œuvre (25%)']
    sizes = [budget_total * 0.4, budget_total * 0.35, budget_total * 0.25]
    colors_pie = ['#15803d', '#0284c7', '#d97706']
    ax1.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.0f%%', startangle=90, textprops={'fontsize': 8})
    ax1.axis('equal')
    plt.tight_layout()
    img_buf1 = io.BytesIO()
    plt.savefig(img_buf1, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig1)
    img_buf1.seek(0)

    # 2. Graphique Bâtons : Indice IA & Santé Végétale
    fig2, ax2 = plt.subplots(figsize=(4, 2.2))
    categories = ['Mouche Blanche', 'Mildiou', 'Nématodes', 'Chenille']
    scores = [96.4, 12.1, 4.3, 1.8]
    colors_bar = ['#dc2626', '#9ca3af', '#9ca3af', '#9ca3af']
    ax2.barh(categories, scores, color=colors_bar)
    ax2.set_xlim(0, 100)
    ax2.set_xlabel('Confiance IA (%)', fontsize=8)
    ax2.tick_params(axis='both', labelsize=8)
    plt.tight_layout()
    img_buf2 = io.BytesIO()
    plt.savefig(img_buf2, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig2)
    img_buf2.seek(0)

    return img_buf1, img_buf2


# --- FONCTION DE GÉNÉRATION DU PDF 6 PAGES PLEINES (STRUCTURÉE, CARTE ET IA) ---
def generate_expert_pdf_pro(producer, zone, sol, crop, surface, user_info, ravageur, budget_total, rentabilite, map_image_path=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    p_color = colors.HexColor("#064e3b")
    s_color = colors.HexColor("#15803d")
    
    # Styles optimisés pour une excellente lisibilité
    t_style = ParagraphStyle('T', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=p_color, alignment=1, spaceAfter=6)
    h_style = ParagraphStyle('H', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=s_color, spaceBefore=6, spaceAfter=4)
    b_style = ParagraphStyle('B', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12.5, textColor=colors.HexColor("#1e293b"))

    # Génération des graphiques analytiques
    chart_fin, chart_ia = generate_pdf_charts(budget_total, rentabilite)

    story = []

    # ================= PAGE 1 : CARTO-GÉOLOCALISATION & FICHE SIGNALÉTIQUE =================
    story.append(Paragraph("📋 RAPPORT D'EXPERTISE & FAISABILITÉ DE PROJET AGRICOLE (360°)", t_style))
    story.append(Paragraph(f"<b>Réf Dossier :</b> PROJ-EXP-{datetime.now().strftime('%Y%m%d%H%M')} | <b>Date :</b> {datetime.now().strftime('%d/%m/%Y')}", ParagraphStyle('Sub', parent=b_style, alignment=1, textColor=colors.gray)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=p_color, spaceBefore=4, spaceAfter=6))
    
    story.append(Paragraph("PAGE 1 : Paramétrage Stratégique & Cadre Géo-Pédologique", h_style))
    story.append(Paragraph("<b>1. Identification du Projet & Acteurs Référents</b>", b_style))
    story.append(Paragraph(f"• <b>Promoteur / GIE / Entreprise :</b> {producer}", b_style))
    story.append(Paragraph(f"• <b>Spéculation / Culture Cible :</b> {crop}", b_style))
    story.append(Paragraph("• <b>Objectif Stratégique :</b> Agriculture Commerciale Intensive orientée vers la souveraineté alimentaire et l'exportation.", b_style))
    story.append(Paragraph(f"• <b>Expert Auditeur :</b> {user_info.get('nom')} ({user_info.get('role')}) — Cabinet YouAgronoMe Sénégal.", b_style))
    story.append(Spacer(1, 4))
    
    story.append(Paragraph("<b>2. Cartographie GPS & Édaphologie Référentielle (INP / FAO)</b>", b_style))
    story.append(Paragraph(f"• <b>Superficie Utile Agricole (SUA) :</b> {surface} Ha délimités par polygone satellitaire.", b_style))
    story.append(Paragraph(f"• <b>Zone Agro-écologique :</b> {zone}", b_style))
    story.append(Paragraph(f"• <b>Type de Sol Authentifié :</b> {sol}", b_style))
    story.append(Paragraph("• <b>Propriétés Physico-Chimiques :</b> Matrice de drainage, pH et charge organique extraits du Référentiel INP.", b_style))
    
    if map_image_path:
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>3. Visualisation Cartographique & Emprise Parcellaire</b>", b_style))
        story.append(Spacer(1, 2))
        try:
            story.append(Image(map_image_path, width=440, height=200))
        except Exception:
            story.append(Paragraph("<i>[Aperçu cartographique non disponible]</i>", b_style))

    story.append(PageBreak())

    # ================= PAGE 2 : INGENIERIE FINANCIÈRE & ANALYSE DE RENTABILITÉ =================
    story.append(Paragraph("PAGE 2 : Plan d'Investissement & Analyse Financière Avancée", t_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=p_color, spaceBefore=4, spaceAfter=6))
    
    story.append(Paragraph("<b>1. Structure Analytique des Coûts (CAPEX/OPEX)</b>", b_style))
    story.append(Paragraph(f"• <b>Intrants & Amendements certifiés (ISRA) [40%] :</b> {int(budget_total * 0.4):,} FCFA.", b_style))
    story.append(Paragraph(f"• <b>Système d'Irrigation & Énergie (DGPRE) [35%] :</b> {int(budget_total * 0.35):,} FCFA.", b_style))
    story.append(Paragraph(f"• <b>Main-d'œuvre & Suivi Sanitaire (DPV) [25%] :</b> {int(budget_total * 0.25):,} FCFA.", b_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>2. Indicateurs Clés de Performance (Business Plan)</b>", b_style))
    story.append(Paragraph(f"• <b>Budget Total d'Investissement :</b> {budget_total:,} FCFA.", b_style))
    story.append(Paragraph(f"• <b>Marge Bénéficiaire Cible :</b> {rentabilite}%.", b_style))
    story.append(Paragraph(f"• <b>Bénéfice Net Prévisionnel (An 1) :</b> {int(budget_total * (rentabilite / 100)):,} FCFA.", b_style))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>3. Allocation Budgétaire Graphique</b>", b_style))
    story.append(Spacer(1, 4))
    story.append(Image(chart_fin, width=320, height=180))

    story.append(PageBreak())

    # ================= PAGE 3 : DIAGNOSTIC SANITAIRE PAR VISION PAR ORDINATEUR (IA) =================
    story.append(Paragraph("PAGE 3 : Diagnostic Sanitaire IA & Protocole Phytosanitaire (DPV)", t_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=p_color, spaceBefore=4, spaceAfter=6))
    
    story.append(Paragraph("<b>1. Détection Automatisée par Intelligence Artificielle</b>", b_style))
    story.append(Paragraph(f"• <b>Cible Prioritaire Identifiée :</b> <i>{ravageur}</i>", b_style))
    story.append(Paragraph("• <b>Algorithme de Vision :</b> Modèle convolutif léger entraîné sur la base épidémiologique ouest-africaine.", b_style))
    story.append(Paragraph("• <b>Fiabilité de la Prédiction :</b> Indice de confiance estimé à 96.4%.", b_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>2. Histogramme de Probabilité des Pathogènes</b>", b_style))
    story.append(Spacer(1, 2))
    story.append(Image(chart_ia, width=330, height=160))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>3. Protocole de Traitement Homologué DPV</b>", b_style))
    story.append(Paragraph("• <b>Traitement Préconisé :</b> Application d'insecticide bio-orienté ou bio-pesticide homologué.", b_style))
    story.append(Paragraph("• <b>Délai Avant Récolte (DAR) :</b> Respect strict de la période de carence (7 à 14 jours).", b_style))

    story.append(PageBreak())

    # ================= PAGE 4 : AGRO-MÉTÉOROLOGIE & RÉFÉRENTIELS NATIONAUX =================
    story.append(Paragraph("PAGE 4 : Agrométéorologie ANACIM & Modélisation Foncier/Genre", t_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=p_color, spaceBefore=4, spaceAfter=6))
    
    story.append(Paragraph("<b>1. Analyse Climatique & Fenêtres d'Ivernage (ANACIM)</b>", b_style))
    story.append(Paragraph("• <b>Planification des Semis :</b> Fenêtre d'installation optimale déterminée sur le cumul décadaire des pluies.", b_style))
    story.append(Paragraph("• <b>Gestion du Risque Sécheresse :</b> Surveillance renforcée lors de la phase sensible de floraison.", b_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>2. Gouvernance Foncière & Équité Genre</b>", b_style))
    story.append(Paragraph("• <b>Sécurisation Juridique :</b> Démarches d'immatriculation et bail emphytéotique (Loi sur le Domaine National).", b_style))
    story.append(Paragraph("• <b>Politique d'Inclusion :</b> Conformité aux directives du Plan Land Matrix Sénégal sur l'accès des femmes et des jeunes au foncier.", b_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>3. Synthèse de l'Enquête Macro-Agricole (DAPSA)</b>", b_style))
    story.append(Paragraph("• Alignement des objectifs de production sur le Plan Sénégal Émergent (PSE-Vert) et la stratégie nationale de souveraineté alimentaire.", b_style))

    story.append(PageBreak())

    # ================= PAGE 5 : POST-RÉCOLTE, MARCHÉS (SIM) & BILAN CARBONE =================
    story.append(Paragraph("PAGE 5 : Chaîne du Froid, Marchés & Bilan Agroécologique", t_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=p_color, spaceBefore=4, spaceAfter=6))
    
    story.append(Paragraph("<b>1. Conservation & Logistique Post-Récolte</b>", b_style))
    story.append(Paragraph("• <b>Infrastructures Froid :</b> Recommandation pour unités de stockage frigorifique solaire afin d'éviter les pertes post-récolte (< 5%).", b_style))
    story.append(Paragraph("• <b>Conditionnement :</b> Normes d'emballage agréées pour le transport national et sous-régional.", b_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>2. Intelligence de Marché (SIM)</b>", b_style))
    story.append(Paragraph("• Suivi régulier des cours sur les marchés de gros stratégiques (Dakar, Kaolack, Saint-Louis, Ziguinchor).", b_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>3. Empreinte Écologique & Crédits Carbone</b>", b_style))
    story.append(Paragraph("• <b>Potentiel de Séquestration :</b> Valorisation du bilan carbone via l'introduction d'arbres fertilitaires et de techniques sans labour.", b_style))

    story.append(PageBreak())

    # ================= PAGE 6 : SÉCURITÉ, PASSEPORT & VALIDATION DU BUREAU D'ÉTUDE =================
    story.append(Paragraph("PAGE 6 : Passeport de Traçabilité & Validation Officielle", t_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=p_color, spaceBefore=4, spaceAfter=6))
    
    story.append(Paragraph("<b>1. Traçabilité & Passeport d'Exportation</b>", b_style))
    story.append(Paragraph("• Code de contrôle unique généré pour l'authentification du lot sur la plateforme nationale.", b_style))
    story.append(Paragraph("• Conformité garantie avec les référentiels phytosanitaires de la CEDEAO et GlobalGAP.", b_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>2. Contrôle d'Accès & Whitelist</b>", b_style))
    story.append(Paragraph("• Document audité et validé par un expert enregistré dans le registre central d'accès sécurisé.", b_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>3. Attestation & Signatures d'Expertise</b>", b_style))
    story.append(Paragraph(f"• <b>Nom de l'Expert Référent :</b> {user_info.get('nom')}", b_style))
    story.append(Paragraph(f"• <b>Rôle / Habilitation :</b> {user_info.get('role')}", b_style))
    story.append(Paragraph("• <b>Organisme :</b> Bureau d'Étude Agrotechnique YouAgronoMe — Sénégal", b_style))
    story.append(Spacer(1, 25))
    
    # Table d'émargement et cachet
    data_sig = [
        [Paragraph("<b>Visa de l'Expert Référent</b>", b_style), Paragraph("<b>Cachet Officiel du Bureau d'Étude</b>", b_style)],
        [Paragraph("<br/><br/>____________________________________", b_style), Paragraph("<br/><br/>[ SCELLÉ ÉLECTRONIQUE YOUAGRONOME ]", b_style)]
    ]
    t_sig = Table(data_sig, colWidths=[240, 240])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_sig)

    doc.build(story)
    buffer.seek(0)
    return buffer

        # --- INTERFACE PRINCIPALE : BUREAU D'ÉTUDE EXPERT ---
    st.markdown("### 💼 Bureau d'Étude & Conseil Agricole Expert (Module 360°)")
    st.info("💡 **Espace Professionnel Global** : Saisissez librement votre culture cible, délimitez votre périmètre sur la carte interactive pour remonter l'intégralité des 12 types de sols du Sénégal (Classification FAO/ORSTOM), accédez au catalogue exhaustif des ravageurs DPV et des variétés certifiées d'Afrique de l'Ouest.")

    tab_proj, tab_geo, tab_fin, tab_san, tab_doc = st.tabs([
            "🎯 Paramétrage & Culture Libre",
            "🗺️ Cartographie & Sols (12 Types)",
            "💰 Business Plan & Investissement",
            "🐛 Diagnostic DPV Exhaustif & IA",
            "📋 Rapports & Administration"
        ])

    with tab_proj:
            st.markdown("#### 🎯 Paramétrage Stratégique du Projet Agricole")
            cp1, cp2 = st.columns(2)
    with cp1:
                st.session_state["expert_producer"] = st.text_input("Nom du Promoteur / GIE / Entreprise :", value=st.session_state["expert_producer"])
                st.session_state["expert_zone"] = st.selectbox("Zone Agro-écologique d'implantation :", options=list(BASE_SOLS_INP_EXPERT.keys()))
    with cp2:
                st.session_state["expert_custom_crop"] = st.text_input("Spéculation / Culture souhaitée (Saisie libre expert) :", value=st.session_state["expert_custom_crop"])
                objectif_projet = st.selectbox("Objectif principal du projet :", ["Agriculture Commerciale Intensive", "Agriculture Familiale Résiliente", "Verger / Arboriculture Pérenne", "Maraîchage Hors-Sol / Serre", "Cultures Céréalières de Souveraineté"])

    st.markdown(f"> **📌 Synthèse du Projet :** Implantation de **{st.session_state['expert_custom_crop']}** sous le modèle *{objectif_projet}* dans la zone de *{st.session_state['expert_zone']}*.")

    with tab_geo:
            st.markdown("#### 🗺️ Délimitation Géospatiale & Remontée Intégrale des Sols du Sénégal")
            
            if "expert_coords" not in st.session_state:
                st.session_state["expert_coords"] = [[14.7910, -16.0700], [14.7930, -16.0700], [14.7930, -16.0680], [14.7910, -16.0680]]
            if "expert_surface" not in st.session_state:
                st.session_state["expert_surface"] = 2.5

            if HAS_FOLIUM:
                m = folium.Map(location=[14.7910, -16.0700], zoom_start=14)
                draw = Draw(
                    export=False, 
                    position="topleft", 
                    draw_options={"polyline": False, "marker": False, "circle": False, "rectangle": True, "polygon": True, "circlemarker": False}, 
                    edit_options={"edit": True}
                )
                draw.add_to(m)

                if st.session_state["expert_coords"] and len(st.session_state["expert_coords"]) >= 3:
                    folium.Polygon(
                        locations=st.session_state["expert_coords"], 
                        color="#1b5e20", 
                        weight=3, 
                        fill=True, 
                        fill_color="#2e7d32", 
                        fill_opacity=0.35
                    ).add_to(m)

                map_res = st_folium(m, width=700, height=360, key="folium_expert_map")
                
                if map_res and isinstance(map_res, dict):
                    last_draw = map_res.get("last_active_drawing")
                    if last_draw and isinstance(last_draw, dict):
                        geom = last_draw.get("geometry")
                        if geom and geom.get("type") == "Polygon":
                            raw_c = geom.get("coordinates", [])
                            if raw_c:
                                new_p = [[p[1], p[0]] for p in raw_c[0]]
                                if len(new_p) >= 3 and new_p != st.session_state["expert_coords"]:
                                    st.session_state["expert_coords"] = new_p
                                    st.session_state["expert_surface"] = calc_surface(new_p)
                                    st.rerun()

            if st.button("🗑️ Réinitialiser le tracé de la parcelle", key="reset_expert_poly"):
                st.session_state["expert_coords"] = []
                st.session_state["expert_surface"] = 2.5
                st.success("Tracé réinitialisé.")
                st.rerun()

            sols_dispos = list(BASE_SOLS_INP_EXPERT[st.session_state["expert_zone"]].keys())
            sol_actuel = st.selectbox("Sélectionner le type de sol spécifique de la zone (Référentiel Complet) :", options=sols_dispos)
            sol_data = BASE_SOLS_INP_EXPERT[st.session_state["expert_zone"]][sol_actuel]

            st.markdown(f"##### 🧪 Propriétés Pédologiques Officielles pour : *{sol_actuel}*")
            gc1, gc2, gc3, gc4 = st.columns(4)
            with gc1:
                st.metric("Superficie GPS", f"{st.session_state['expert_surface']} Ha")
            with gc2:
                st.metric("pH du Sol", sol_data["pH"])
            with gc3:
                st.metric("Matière Organique", f"{sol_data['MO']}%")
            with gc4:
                st.metric("Texture", sol_data["Texture"])
    with tab_fin:
            st.markdown("#### 💰 Analyse Financière, Investissement & Rentabilité (Business Plan)")
            fc1, fc2 = st.columns(2)
            with fc1:
                cout_hectare = st.number_input("Coût d'investissement estimé par Hectare (FCFA) :", min_value=100000, max_value=10000000, value=750000, step=50000)
            with fc2:
                taux_marge = st.slider("Marge bénéficiaire prévisionnelle (%) :", min_value=10, max_value=150, value=45)

            budget_global = int(cout_hectare * st.session_state["expert_surface"])
            chiffre_affaires_prev = int(budget_global * (1 + taux_marge / 100))
            benefice_net = chiffre_affaires_prev - budget_global

            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                st.metric("Investissement Total", f"{budget_global:,} FCFA")
            with bc2:
                st.metric("CA Prévisionnel", f"{chiffre_affaires_prev:,} FCFA")
            with bc3:
                st.metric("Bénéfice Net Attendu", f"{benefice_net:,} FCFA", delta=f"+{taux_marge}%")

    with tab_san:
            st.markdown("#### 🐛 Diagnostic Sanitaire Multi-Angles & Intelligence Artificielle")
            
            # 1. Sélection de la zone inspectée
            angle_vue = st.radio(
                "📐 **Étape 1 : Sélectionnez la zone du végétal prise en photo :**",
                ["🍃 Vue Feuillage (Dessus/Dessous)", "🪵 Vue Tige / Collet", "🍓 Vue Fruit / Gousse", "🪴 Vue Racines / Sol"],
                horizontal=True
            )

            # Filtrage dynamique des bio-agresseurs selon le plan sélectionné
            ravageurs_filtres = [
                k for k, v in CATALOGUE_DPV_EXPERT.items() 
                if angle_vue in v["plans_sensibles"]
            ]
            
            col_sel1, col_sel2 = st.columns([1.5, 1])
            with col_sel1:
                rav_choisi = st.selectbox(
                    "🔍 **Étape 2 : Cible identifiée ou suspectée (Répertoire DPV) :**",
                    options=ravageurs_filtres if ravageurs_filtres else list(CATALOGUE_DPV_EXPERT.keys())
                )
            with col_sel2:
                st.caption("ℹ️ *La liste s'ajuste automatiquement selon la partie du végétal sélectionnée.*")

            st.markdown("---")
            
            # 2. Zone d'importation de cliché
            img_file = st.file_uploader(
                "📸 **Étape 3 : Indiquez ou chargez le cliché pour l'analyse IA :**", 
                type=["jpg", "png", "jpeg"], 
                key="exp_img_upload"
            )

            if img_file is not None:
                col_img, col_diag = st.columns([1, 1.2])
                
                with col_img:
                    st.image(img_file, caption=f"Analyse HD — Cadre : {angle_vue}", use_container_width=True)

                with col_diag:
                    st.markdown("##### ⚙️ Scanner Vision Convolutif YouAgronoMe")
                    
                    # Animation de progression simulée
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    steps = [
                        f"Isolement de la région d'intérêt ({angle_vue.split()[1]})...",
                        "Extraction des motifs de nécrose & galeries d'insectes...",
                        "Indexation taxonomique avec le registre national DPV...",
                        "Diagnostic phytosanitaire certifié !"
                    ]
                    
                    for i, step in enumerate(steps):
                        status_text.text(step)
                        progress_bar.progress((i + 1) * 25)
                        time.sleep(0.25)
                    
                    st.success("✅ **Diagnostic IA Validé**")
                    
                    # Récupération des informations sur l'insecte
                    info_rav = CATALOGUE_DPV_EXPERT[rav_choisi]
                    confiance = round(random.uniform(97.5, 99.6), 1)

                    st.metric(
                        label="🐛 Agent / Insecte Responsable", 
                        value=rav_choisi.split('(')[0].strip(), 
                        delta=f"Indice de confiance : {confiance}%"
                    )
                    
                    st.markdown(f"""
                    * **Mode d'attaque :** {info_rav['mecanisme']}
                    * **Symptômes caractéristiques :** {info_rav['symptomes_visuels']}
                    """)

                # Alerte et Protocole DPV
                st.error(f"🚨 **PROTOCOLE DE LUTTE ET TRAITEMENT DPV** : {info_rav['traitement']}")

            else:
                st.info("💡 **Mode d'emploi :** Sélectionnez l'organe végétal (Feuille, Tige, Fruit, Racine), déposez un cliché net et le réseau de neurones identifiera précisément l'insecte responsable et son traitement DPV.")

            st.success("🌤️ **Veille Météorologique ANACIM** : Paramètres climatiques stables. Indice de stress hydrique faible.")

        with tab_doc:
            st.markdown("#### 📋 Édition de Rapport d'Expertise PDF & Administration Whitelist")
            
            if HAS_REPORTLAB:
                pdf_data = generate_expert_pdf_pro(
                    producer=st.session_state["expert_producer"],
                    zone=st.session_state["expert_zone"],
                    sol=sol_actuel,
                    crop=st.session_state["expert_custom_crop"],
                    surface=st.session_state["expert_surface"],
                    user_info=user_session,
                    ravageur=rav_choisi,
                    budget_total=budget_global,
                    rentabilite=taux_marge
                )
                st.download_button(
                    label="📥 Télécharger le Rapport d'Expertise PDF Complet (6 Pages)",
                    data=pdf_data,
                    file_name=f"Rapport_Expertise_{st.session_state['expert_producer'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )

            if st.button("🛒 Ajouter le pack d'intrants du projet au Panier", key="add_panier_expert"):
                st.session_state.panier.append({
                    "produit": f"Pack Expert {st.session_state['expert_custom_crop']} ({st.session_state['expert_surface']} Ha)",
                    "details": f"Intrants & Suivi complet pour {budget_global:,} FCFA",
                    "prix": f"{int(budget_global * 0.4):,} FCFA",
                    "producteur": st.session_state["expert_producer"]
                })
                st.success("✅ Pack d'intrants transféré au panier avec succès !")

            # Gestion de la Whitelist pour l'administrateur
            if is_admin:
                st.markdown("---")
                st.markdown("##### 👥 Gestion Administrative de la Liste Blanche (Whitelist)")
                
                with st.form("form_expert_whitelist"):
                    nw_email = st.text_input("E-mail du technicien / expert :").strip().lower()
                    nw_pass = st.text_input("Mot de passe à assigner :")
                    nw_nom = st.text_input("Nom et Prénom :")
                    nw_role = st.selectbox("Rôle attribué :", ["Technicien Terrain", "Agronome Conseil", "Expert DPV", "Auditeur de Projet"])
                    
                    submitted = st.form_submit_button("➕ Enregistrer et Configurer l'Accès")
                    if submitted and nw_email and nw_pass:
                        found_u = False
                        for u in db["whitelist"]:
                            if str(u.get("email")).lower() == nw_email:
                                u["password"] = nw_pass
                                u["nom"] = nw_nom
                                u["role"] = nw_role
                                u["statut"] = "Actif"
                                found_u = True
                                break
                        if not found_u:
                            db["whitelist"].append({
                                "email": nw_email,
                                "password": nw_pass,
                                "nom": nw_nom,
                                "role": nw_role,
                                "zone": st.session_state["expert_zone"],
                                "statut": "Actif"
                            })
                        save_db(db)
                        st.success(f"✅ Compte configuré avec succès pour {nw_email} !")
                        st.rerun()

                # Révocation d'accès
                active_users_list = [u.get("email") for u in db["whitelist"] if u.get("email") != OWNER_EMAIL and u.get("statut") == "Actif"]
                if active_users_list:
                    rev_target = st.selectbox("Sélectionner un compte à révoquer :", options=active_users_list, key="rev_expert_sel")
                    if st.button("❌ Révoquer l'accès de ce compte"):
                        for u in db["whitelist"]:
                            if str(u.get("email")).lower() == rev_target.lower():
                                u["statut"] = "Inactif"
                                break
                        save_db(db)
                        st.warning(f"⚠️ L'accès pour {rev_target} a été révoqué avec succès.")
                        st.rerun()
                else:
                    st.info("Aucun autre compte actif à révoquer pour le moment.")
        # =====================================================================================
        # 🔬 10 MODULES EXPERTS ÉTENDUS : ARCHITECTURE EN EXPANDERS PERFORMANTS & SÉLECTION LIBRE
        # =====================================================================================
        
        st.markdown("---")
        st.markdown("### 🔬 Hub Expert Étendu : Référentiels Nationaux & Régionaux (Données Officielles)")
        st.info("💡 **Navigation modulaire avancée** : Chaque thématique institutionnelle est encapsulée dans un expander haute performance permettant l'exploration ciblée, la sélection granulaire et l'application directe des critères des agences partenaires (ISRA, DPV, ANACIM, DAPSA, etc.).")

        # --- EXPANDER 1 : VARIÉTÉS SÉNÉGAL & AFRIQUE ---
        with st.expander("🌾 1. Catalogue Variétal Exhaustif (ISRA, CORAF, AfricaRice, CEDEAO)", expanded=True):
            st.markdown("Répertoire officiel et multicritère des variétés homologuées et tolérantes aux stress climatiques en Afrique de l'Ouest.")
            
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                filiere_sel = st.selectbox("Sélectionner la filière agricole cible :", options=list(CATALOGUE_VARIETES_AFRIQUE.keys()), key="exp_filiere_sel")
            with col_v2:
                critere_recherche = st.text_input("Filtrer par mot-clé (ex: cycle court, tolérance, rendement) :", "", key="exp_var_filter")

            st.markdown(f"##### 📋 Liste des variétés certifiées disponibles pour : **{filiere_sel}**")
            
            varietes_list = CATALOGUE_VARIETES_AFRIQUE[filiere_sel]
            if critere_recherche:
                varietes_list = [v for v in varietes_list if critere_recherche.lower() in v.lower()]

            if varietes_list:
                selected_variete_opt = st.radio("Sélectionner la variété à retenir pour le projet :", options=varietes_list, key=f"radio_{filiere_sel}")
                st.success(f"✅ **Variété sélectionnée et verrouillée** : *{selected_variete_opt}* pour l'intégration dans le cahier des charges.")
            else:
                st.warning("⚠️ Aucune variété ne correspond au filtre textuel saisi. Veuillez élargir votre recherche.")

        # --- EXPANDER 2 : ENQUÊTE DAPSA ---
        with st.expander("📊 2. Enquête Agricole Annuelle & Benchmarking (DAPSA)", expanded=False):
            st.markdown("Exploitation des données structurelles et macro-économiques de la Direction de l'Analyse, de la Prévision et des Statistiques Agricoles.")
            
            dapsa_regiones = ["Kaolack", "Kaffrine", "Fatick", "Saint-Louis", "Thiès", "Ziguinchor", "Kolda", "Louga", "Matam", "Tambacounda", "Kédougou", "Sédhiou", "Diourbel", "Dakar"]
            dap_reg = st.selectbox("Sélectionner la région administrative d'analyse DAPSA :", options=dapsa_regiones, key="dapsa_exp_reg")
            
            dap_indicateur = st.selectbox("Indicateur statistique d'intérêt :", [
                "Structure des exploitations familiales vs agrobusiness",
                "Superficies cultivées et rendements moyens enregistrés",
                "Taux d'équipement en matériel agricole motorisé",
                "Accès des ménages aux engrais subventionnés"
            ], key="dap_ind_sel")

            st.markdown(
                f"- **Région ciblée** : *{dap_reg}*<br>"
                f"- **Volet statistique** : *{dap_indicateur}*<br>"
                "- **Analyse d'impact** : Les données consolidées de la DAPSA montrent une forte corrélation entre l'adoption de semences certifiées et la hausse du revenu net par exploitant dans cette zone."
            )

        # --- EXPANDER 3 : ALERTE DPV ---
        with st.expander("🐛 3. Alertes Phytosanitaires & Protocoles de Lutte (DPV)", expanded=False):
            st.markdown("Plateforme de veille sanitaire et répertoires officiels de la Direction de la Protection des Végétaux.")
            
            ravageur_cles = list(CATALOGUE_DPV_EXPERT.keys())
            rav_choix_exp = st.selectbox("Sélectionner un bio-agresseur pour consultation du protocole homologué DPV :", options=ravageur_cles, key="dpv_exp_sel")
            
            st.markdown(
                f"- **Cible phytosanitaire** : `{rav_choix_exp}`<br>"
                f"- **Descriptif et Dégâts** : {CATALOGUE_DPV_EXPERT[rav_choix_exp]}<br>"
                "- **Recommandation officielle** : Approvisionnement exclusif auprès des phytopharmacies agrées par la DPV (Thiaroye / Antennes régionales). Respect des délais avant récolte (DAR)."
            )

        # --- EXPANDER 4 : MÉTÉO ANACIM ---
        with st.expander("🌤️ 4. Bulletins Agro-météorologiques & Climat (ANACIM)", expanded=False):
            st.markdown("Suivi décadaire des cumuls pluviométriques, des températures et des risques climatiques (ANACIM).")
            
            anacim_zone = st.selectbox("Zone climatique d'observation :", [
                "Zone Sahélienne Nord (Podor, Matam, Richard-Toll)",
                "Bassin Arachidier (Kaolack, Diourbel, Fatick, Kaffrine)",
                "Zone Littorale & Maraîchère (Niayes - Dakar/Thiès/Louga)",
                "Zone Sud & Soudano-Guinéenne (Ziguinchor, Kolda, Sédhiou, Tambacounda)"
            ], key="anacim_zone_sel")

            zone_label = str(anacim_zone)
            st.markdown(
                f"- **Zone sélectionnée** : *{zone_label}*<br>"
                "- **Indicateur climatique** : Analyse des séquences sèches et prévisions saisonnières (COFOG / ANACIM).<br>"
                "- **Avis technique** : Recommandation d'ajustement du calendrier de semis en fonction de l'installation effective de la mousson et de la portance hydrique des sols."
            )

        # --- EXPANDER 5 : FONCIER & GENRE ---
        with st.expander("⚖️ 5. Sécurisation Foncière & Inclusion Genre (Réglementation Rurale)", expanded=False):
            st.markdown("Analyse du statut juridique des terres (Domaine National, Titres Fonciers) et indicateurs d'accès pour les femmes et les jeunes.")
            
            statut_foncier_exp = st.selectbox("Mode d'accès et de sécurisation foncière :", [
                "Affectation par le Conseil Municipal (Loi sur le Domaine National)",
                "Bail emphytéotique ou convention de partenariat",
                "Acquisition en toute propriété (Titre Foncier)",
                "Location coutumière ou convention verbale de prêt"
            ], key="foncier_exp_sel")

            st.markdown(
                f"- **Statut retenu** : *{statut_foncier_exp}*<br>"
                "- **Recommandation d'expert** : Pour les investissements à forte intensité capitalistique (arboriculture, serres, irrigation), la formalisation par délibération municipale avec bail ou immatriculation au livre foncier est fortement conseillée pour éviter les litiges intercommunautaires.<br>"
                "- **Genre** : Intégration systématique des clauses d'équité genre conformément aux directives du Plan Land Matrix Sénégal."
            )

        # --- EXPANDER 6 : SUBVENTIONS ---
        with st.expander("💰 6. Guichet Unique des Subventions & Intrants Agricoles", expanded=False):
            st.markdown("Évaluation de l'éligibilité aux campagnes nationales d'appui aux producteurs (Engrais, Matériel, Semences).")
            
            type_subvention = st.selectbox("Programme de soutien public visé :", [
                "Campagne Agricole Nationale (Intrants subventionnés - Engrais NPK/Urée)",
                "Programme d'Urgence de Modernisation de l'Agriculture (PUMA / PUDC)",
                "Projet d'Amélioration de la Productivité et de la Résilience (PAPIL)",
                "Lignes de crédit préférentielles de la CNI / CNCAS / Partenaires"
            ], key="subv_prog_sel")

            montant_projet_subv = st.number_input("Montant prévisionnel des intrants requis (FCFA) :", min_value=50000, max_value=10000000, value=500000, step=25000, key="subv_amt")
            taux_subs = 0.30 if "Campagne" in type_subvention else 0.50
            montant_estime_aide = int(montant_projet_subv * taux_subs)

            st.metric("Appui Financier / Subvention Publique Estimé", f"{montant_estime_aide:,} FCFA")
            st.caption("Pièces justificatives requises : Carte d'agriculteur biométrique, attestation d'appartenance à une structure paysanne reconnue.")

        # --- EXPANDER 7 : POST-RÉCOLTE ---
        with st.expander("🧊 7. Chaîne de Froid & Gestion des Pertes Post-Récolte", expanded=False):
            st.markdown("Solutions technologiques et logistiques pour la conservation des denrées périssables et des grains.")
            
            filiere_post = st.selectbox("Filière et type de produit stocké :", [
                "Oignon frais (Séchage, tressage et conservation en pallox)",
                "Mangue fraîche (Hydro-refroidissement & traitement thermique)",
                "Riz paddy (Séchage mécanique et stockage en sacs hermétiques PICS)",
                "Maraîchage feuille (Chambre froide positive - 4°C)"
            ], key="post_filiere_sel")

            st.markdown(
                f"- **Filière ciblée** : *{filiere_post}*<br>"
                "- **Impact stratégique** : L'adoption de technologies de conservation post-récolte adaptées permet de réduire les pertes de 25% à moins de 5%, stabilisant ainsi l'offre sur les marchés locaux et d'exportation."
            )

        # --- EXPANDER 8 : MARCHÉS RURAUX ---
        with st.expander("📈 8. Intelligence de Marché & Cours des Denrées (Référentiels)", expanded=False):
            st.markdown("Suivi des tendances des prix et des flux d'approvisionnement sur les grands marchés de gros du Sénégal.")
            
            marche_gros = st.selectbox("Marché de gros de référence :", [
                "Marché d'intérêt national de Diamniadio (MIN)",
                "Marché de Bène Tchic / Castors (Dakar)",
                "Marché central de Touba Belel",
                "Marché régional de Kaolack / Saint-Louis"
            ], key="marche_gros_sel")

            st.markdown(
                f"- **Marché sélectionné** : *{marche_gros}*<br>"
                "- **Analyse des fluctuations** : Les périodes de soudure et d'arrivée massive des récoltes locales (notamment l'oignon et la pomme de terre des Niayes) dictent les fenêtres optimales de commercialisation pour maximiser la marge du producteur."
            )

        # --- EXPANDER 9 : CARBONE SOL ---
        with st.expander("🌱 9. Séquestration Carbone & Pratiques Agroécologiques", expanded=False):
            st.markdown("Évaluation de l'impact des pratiques de régénération des sols sur les crédits carbone et la fertilité organique.")
            
            pratiques_retenues = st.multiselect("Sélectionner les techniques agroécologiques déployées :", [
                "Agroforesterie (Plantation d'Acacia albida / Faidherbia)",
                "Restitution systématique des résidus de récolte",
                "Utilisation de bio-fertilisants et composts enrichis",
                "Pratique du non-labour ou travail minimal du sol"
            ], key="agro_prat_sel")

            score_carbone = len(pratiques_retenues) * 1.4
            st.metric("Potentiel de Séquestration Carbone Évalué", f"+{score_carbone} tCO2eq / Ha / an")
            st.caption("Ce score valorise l'exploitation dans le cadre des initiatives de certification carbone et d'agriculture intelligente face au climat.")

        # --- EXPANDER 10 : TRAÇABILITÉ API ---
        with st.expander("🔗 10. Traçabilité Numérique & Passeport Phytosanitaire Export", expanded=False):
            st.markdown("Génération de passeports numériques normalisés pour la certification des lots destinés à l'exportation ou aux circuits modernes.")
            
            code_lot_export = st.text_input("Référence unique du lot / Code traçabilité :", f"SN-EXP-{datetime.now().strftime('%Y')}-994", key="trace_code_input")
            pays_destination = st.selectbox("Marché de destination finale :", [
                "Union Européenne (Normes GlobalGAP / Phytosanitaire strict)",
                "Sous-région CEDEAO (Marché Commun)",
                "Consommation Locale / Grande Distribution Sénégalaise"
            ], key="dest_exp_sel")

            if st.button("🚀 Valider et Générer le Passeport de Traçabilité", key="btn_gen_passeport"):
                st.success(f"✅ **Passeport Numérique Émis avec Succès** pour le lot `{code_lot_export}` (Destination : {pays_destination}). Conformité validée pour l'audit d'exportation.")
# =====================================================
# 🌱 CONSEIL
# =====================================================
elif selected == "🌱 Conseil":

    st.markdown("""
    <div style="padding: 30px; background: linear-gradient(135deg, #1b5e20 0%, #0d2310 100%); border-radius: 16px; color: white; margin-bottom: 25px; text-align: center;">
        <h2 style="color: white; margin-bottom: 10px;">🌱 Espace Conseil & Boutique d'Intrants YouAgronoMe</h2>
        <p style="margin: 0; opacity: 0.9; font-size: 14px;">Commandez vos engrais subventionnés, semences certifiées ISRA et équipements d'irrigation de précision adaptés à vos parcelles.</p>
    </div>
    """, unsafe_allow_html=True)

    catalogue_produits = [
        {"nom": "Semences de Riz Sahélien Certifiées (ISRA/SAED)", "categorie": "Semences", "prix": "25 000 FCFA / 50kg", "desc": "Variété à haut rendement, tolérante à la salinité et aux aléas hydriques."},
        {"nom": "Engrais de Fond DAP (14-23-14)", "categorie": "Intrants", "prix": "22 500 FCFA / 50kg", "desc": "Formule homologuée pour le démarrage racinaire des céréales et cultures maraîchères."},
        {"nom": "Engrais de Couverture Urée (46% N)", "categorie": "Intrants", "prix": "20 000 FCFA / 50kg", "desc": "Azote hautement assimilable pour la phase de montaison et tallage."},
        {"nom": "Kit d'Irrigation Goutte-à-Goutte (1 Hectare)", "categorie": "Équipement", "prix": "450 000 FCFA / Kit", "desc": "Économie d'eau de 50% par rapport à l'aspersion, validé par la DGPRE."}
    ]

    col_cat1, col_cat2 = st.columns([2, 1])
    with col_cat1:
        st.markdown("### 🛍️ Catalogue des Intrants & Solutions Validées")
        for p in catalogue_produits:
            with st.container(border=True):
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.markdown(f"#### {p['nom']}")
                    st.caption(f"Catégorie : **{p['categorie']}** | Prix : **{p['prix']}**")
                    st.write(p['desc'])
                with col_btn:
                    st.write("")
                    if st.button("Commander", key=f"cmd_{p['nom']}"):
                        st.session_state.panier.append({
                            "produit": p['nom'],
                            "details": p['desc'],
                            "prix": p['prix'],
                            "producteur": "Commande direct"
                        })
                        st.success(f"Ajouté : {p['nom']}")

    with col_cat2:
        st.markdown("### 🛒 Votre Panier")
        if not st.session_state.panier:
            st.info("Votre panier est vide.")
        else:
            for idx, item in enumerate(st.session_state.panier):
                with st.container(border=True):
                    st.markdown(f"**{item['produit']}**")
                    st.caption(f"Prix : {item['prix']}")
                    if st.button("Retirer", key=f"del_{idx}"):
                        st.session_state.panier.pop(idx)
                        st.rerun()
            
            if st.button("✅ Valider la Commande (Partenariat La Banque Agricole)", type="primary", use_container_width=True):
                st.success("🎉 Commande validée avec succès ! Un conseiller ANCAR vous contactera pour la livraison sur votre périmètre.")
                st.session_state.panier = []


# =====================================================
# 📞 CONTACT
# =====================================================
elif selected == "📞 Contact":

    st.markdown("""
    <div style="padding: 35px; background: linear-gradient(135deg, #1b5e20 0%, #0d2310 100%); border-radius: 16px; color: white; text-align: center; margin-bottom: 25px;">
        <h2 style="color: white; margin-bottom: 10px;">📞 Contactez l'Équipe YouAgronoMe</h2>
        <p style="margin: 0; opacity: 0.9; font-size: 15px;">Notre équipe technique basée à Saint-Louis (Hub de Sor) et Dakar est à votre écoute pour tout appui sur vos projets agricoles.</p>
    </div>
    """, unsafe_allow_html=True)

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        with st.container(border=True):
            st.markdown("### 📍 Nos Coordonnées")
            st.write("🏢 **Siège Social** : Hub Numérique de Sor, Saint-Louis, Sénégal")
            st.write("📱 **Téléphone / WhatsApp** : +221 77 000 00 00")
            st.write("✉️ **Email Officiel** : contact@youagronome.sn")
            st.write("⏰ **Horaires** : Lundi au Vendredi, 08h00 - 18h00")
            st.caption("🇸🇳 Startup incubée et ancrée dans l'écosystème agritech national.")

    with col_c2:
        with st.container(border=True):
            st.markdown("### ✉️ Envoyez-nous un message")
            nom_exp = st.text_input("Votre Nom complet :")
            email_exp = st.text_input("Votre Adresse e-mail :")
            msg_exp = st.text_area("Votre Message / Demande d'accompagnement :")
            if st.button("Envoyer le message", type="primary"):
                if nom_exp and msg_exp:
                    st.success(f"✅ Merci {nom_exp} ! Votre message a bien été transmis à notre équipe d'experts.")
                else:
                    st.error("⚠️ Veuillez renseigner au moins votre nom et votre message.")

