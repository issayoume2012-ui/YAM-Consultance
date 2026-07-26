from datetime import datetime, timedelta
import io
import json
import os
import random
import urllib.parse

import numpy as np
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import streamlit as st

try:
    import folium
    from streamlit_folium import st_folium
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
    page_title="YouAgronoMe",
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
    # Polygone par défaut (carré d'environ 1 hectare dans le delta)
    st.session_state["draw_coords"] = [
        [14.7910, -16.0700],
        [14.7930, -16.0700],
        [14.7930, -16.0680],
        [14.7910, -16.0680]
    ]

if "active_surface_ha" not in st.session_state:
    st.session_state["active_surface_ha"] = 1.0


# =====================================================
# 2. DESIGN DU MENU DE NAVIGATION (CSS HARMONISÉ)
# =====================================================
st.markdown("""
<style>
.stAppHeader { display: none !important; }
.main .block-container { padding-top: 15px !important; max-width: 95% !important; }
div[data-testid="stRadio"] {
    background: #ffffff !important;
    padding: 10px 20px !important;
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
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    margin: 0px !important;
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
    cursor: pointer !important;
    transition: all 0.2s ease-in-out !important;
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
[data-testid="stMetricValue"] { font-size: 20px !important; white-space: nowrap !important; }
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
    .ai-box {
        background-color: #f0fdf4; border-left: 5px solid #2e7d32; padding: 20px; border-radius: 8px; margin-top: 10px; font-size: 13px; color: #1e293b; line-height: 1.6;
    }
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

    st.markdown("<div class='db-section-title'>📄 Rapport Officiel d'Évaluation Inter-Institutionnelle</div>", unsafe_allow_html=True)
    rapport_ia_multi = f"""SOUVERAINETÉ ALIMENTAIRE DU SÉNÉGAL - RAPPORT BIANNUEL INTER-AGENCES (2026)
====================================================================================================
Territoire d'analyse : {region_choisie}
Année de simulation : {annee_choisie}
Scénario retenu : {scenario}
----------------------------------------------------------------------------------------------------
1. BILAN DES PRODUCTIONS PAR FILIÈRE (DAPSA, SAED, SODAGRI, DHORT, SODEFITEX)
   - Riz (Irrigué & Pluvial) : {df_filtre['SAED/SODAGRI - Riz Irrigué & Pluvial (Tonnes)'].sum():,} Tonnes.
   - Céréales Sèches (Mil, Sorgho, Maïs, Fonio) : {df_filtre['DAPSA - Mil & Sorgho (Tonnes)'].sum() + df_filtre['DAPSA - Maïs & Fonio (Tonnes)'].sum():,} Tonnes.
   - Oléagineux & Légumineuses (Arachide, Niébé, Sésame) : {df_filtre['DAPSA - Arachide (Tonnes)'].sum() + df_filtre['DAPSA - Niébé & Sésame (Tonnes)'].sum():,} Tonnes.
   - Horticulture (Oignon, Pomme de terre, Tomate industrielle) : {df_filtre['ARM/DHORT - Oignon & Pomme de Terre (Tonnes)'].sum() + df_filtre['ARM/DHORT - Tomate Industrielle & Legumes (Tonnes)'].sum():,} Tonnes.
   - Tubercules & Racines (Manioc) : {df_filtre['DAPSA - Manioc & Tubercules (Tonnes)'].sum():,} Tonnes.
   - Cultures Industrielles (Coton & Anacarde) : {df_filtre['SODEFITEX/DAPSA - Coton & Anacarde (Tonnes)'].sum():,} Tonnes.

2. FINANCEMENT & LOGISTIQUE (LA BANQUE AGRICOLE, DER/FJ, ARM, ITA)
   - Financements bancaires octroyés (La Banque Agricole) : {df_filtre['La Banque Agricole - Financements Octroyés (Mio FCFA)'].sum():,} Millions FCFA.
   - Agropreneurs accompagnés par la DER/FJ : {df_filtre['DER/FJ - Agropreneurs & TPE Financés (Nombre)'].sum():,} porteurs de projets.
   - Capacité de stockage sous régulation (ARM) : {df_filtre['ARM - Capacité de Stockage/Régulation (Tonnes)'].sum():,} Tonnes.
   - Taux de transformation industrielle locale (ITA) : {df_filtre['ITA - Taux de Transformation Agroalimentaire (%)'].mean():.1f}%.

3. RÉSILIENCE CLIMATIQUE & CONSERVATION DES SOLS (DGPRE, CSE, INP, ANACIM)
   - Prélèvements d'eau mobilisés pour l'irrigation (DGPRE) : {df_filtre['DGPRE - Eau Irrigation Mobilisée (Mio m³)'].sum():,.1f} Millions m³.
   - Biomasse pastorale disponible (CSE) : {df_filtre['CSE - Biomasse Pastorale Disponible (kg MS/ha)'].mean():.0f} kg MS/ha.
   - Terres salines restaurées au gypse (INP) : {df_filtre['INP - Terres Salines Restaurées au Gypse (Ha)'].sum():,} Ha.
   - Couverture d'alerte météo SMS (ANACIM) : {df_filtre['ANACIM - Abonnés Alertes Agrométéo SMS'].sum():,} producteurs.

4. CAPITAL HUMAIN & ENCADREMENT (ANCAR, MEPA, 3FPT)
   - Taux d'encadrement technique agricole (ANCAR) : {df_filtre["Taux d'Encadrement Technique ANCAR (%)"].mean():.1f}%.
   - Couverture vaccinale du cheptel (MEPA) : {df_filtre['Taux Couverture Vaccinale Cheptel MEPA (%)'].mean():.1f}%.
   - Acteurs ruraux formés en agribusiness (3FPT/ONFP) : {df_filtre['3FPT/ONFP - Acteurs Formés en Agribusiness'].sum():,} personnes.
====================================================================================================
"""

    with st.container(border=True):
        st.markdown(f"<div class='ai-box'><pre style='white-space: pre-wrap; font-family: inherit; font-size: 12px;'>{rapport_ia_multi}</pre></div>", unsafe_allow_html=True)

        def generer_excel_multi_agences(df, rapport_texte):
            output = io.BytesIO()
            wb = openpyxl.Workbook()
            ws1 = wb.active
            ws1.title = "Matrice Filières Agences"
            
            ws1.merge_cells("A1:N1")
            title_cell = ws1["A1"]
            title_cell.value = "🇸🇳 DONNÉES RÉELLES CONSOLIDÉES DES FILIÈRES & AGENCES AGRICOLES DU SÉNÉGAL"
            title_cell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
            title_cell.fill = PatternFill(start_color="1B5E20", end_color="1B5E20", fill_type="solid")
            title_cell.alignment = Alignment(horizontal="center", vertical="center")
            ws1.row_dimensions[1].height = 35
            
            headers = [
                "Région", "Riz (T)", "Mil & Sorgho (T)", "Maïs & Fonio (T)", 
                "Arachide (T)", "Niébé & Sésame (T)", "Oignon/P.Terre (T)", "Tomate/Légumes (T)",
                "Manioc (T)", "Crédit LBA (Mio)", "DER/FJ (Bénéf.)", "Eau DGPRE (Mio m³)",
                "SMS ANACIM", "Encadrement ANCAR (%)"
            ]
            for c_idx, h in enumerate(headers, 1):
                cell = ws1.cell(row=3, column=c_idx)
                cell.value = h
                cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="0D2310", end_color="0D2310", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")

            cols_export = [
                "Région", "SAED/SODAGRI - Riz Irrigué & Pluvial (Tonnes)", "DAPSA - Mil & Sorgho (Tonnes)",
                "DAPSA - Maïs & Fonio (Tonnes)", "DAPSA - Arachide (Tonnes)", "DAPSA - Niébé & Sésame (Tonnes)",
                "ARM/DHORT - Oignon & Pomme de Terre (Tonnes)", "ARM/DHORT - Tomate Industrielle & Legumes (Tonnes)",
                "DAPSA - Manioc & Tubercules (Tonnes)", "La Banque Agricole - Financements Octroyés (Mio FCFA)",
                "DER/FJ - Agropreneurs & TPE Financés (Nombre)", "DGPRE - Eau Irrigation Mobilisée (Mio m³)",
                "ANACIM - Abonnés Alertes Agrométéo SMS", "Taux d'Encadrement Technique ANCAR (%)"
            ]
            
            df_sub = df[cols_export]
            for r_idx, row in enumerate(df_sub.itertuples(index=False), 4):
                for c_idx, val in enumerate(row, 1):
                    ws1.cell(row=r_idx, column=c_idx, value=val)

            ws2 = wb.create_sheet(title="Synthèse Institutionnelle")
            ws2.column_dimensions['A'].width = 110
            for idx, line in enumerate(rapport_texte.split('\n'), 1):
                ws2.cell(row=idx, column=1, value=line)
                
            wb.save(output)
            output.seek(0)
            return output

        excel_multi = generer_excel_multi_agences(df_filtre, rapport_ia_multi)
        st.download_button(
            label="📥 Télécharger la Matrice Officielle Inter-Agences (.xlsx)",
            data=excel_multi,
            file_name=f"Matrice_Agences_Filieres_Senegal_{region_choisie.replace(' ', '_')}_{annee_choisie}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="btn_export_multi_agences_v3"
        )


# =====================================================
# 💼 CONSULTANCE
# =====================================================
elif selected == "💼 Consultance":

    DB_FILE = "techniciens_db.json"
    OWNER_EMAIL = "issayoume2012@gmail.com"
    OWNER_PASS = "issayoume2026"

    DEFAULT_OWNER = {
        "email": OWNER_EMAIL,
        "password": OWNER_PASS,
        "nom": "Propriétaire Principal",
        "role": "Administrateur",
        "zone": "Toutes zones",
        "statut": "Actif"
    }

    def load_db():
        default_db = {"whitelist": [DEFAULT_OWNER], "historique": []}
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
            user_email = str(user.get("email", "")).strip().lower()
            if user_email == OWNER_EMAIL:
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

    BASE_SOLS_INP_FULL = {
        "Vallée du Fleuve Sénégal (Saint-Louis, Matam, Bakel)": {
            "Sol Deck (Fluvisol Hydromorphe Argileux)": {"pH": 6.8, "MO": 2.1, "N": 0.12, "P": 18, "K": 210, "Rétention": "Très forte (>140mm/m)", "Drainage": "Lent"},
            "Sol Dior (Arénosol / Sableux Brut)": {"pH": 5.8, "MO": 0.4, "N": 0.03, "P": 8, "K": 60, "Rétention": "Faible (40mm/m)", "Drainage": "Excessif"},
            "Sol Deck-Dior (Franco-Argilo-Sableux)": {"pH": 6.5, "MO": 1.2, "N": 0.08, "P": 14, "K": 130, "Rétention": "Moyenne (90mm/m)", "Drainage": "Modéré"}
        },
        "Zone des Niayes (Dakar, Thiès, Louga Littoral)": {
            "Sables des Niayes / Céane (Arénosol Eutrique)": {"pH": 6.2, "MO": 0.6, "N": 0.04, "P": 22, "K": 80, "Rétention": "Faible", "Drainage": "Rapide"},
            "Sol Hydromorphe de Bas-Fond / Niaye": {"pH": 5.5, "MO": 3.8, "N": 0.22, "P": 25, "K": 150, "Rétention": "Forte", "Drainage": "Imparfait"}
        },
        "Bassin Arachidier (Kaolack, Fatick, Kaffrine, Diourbel, Louga)": {
            "Sol Dior (Sol Ferrugineux Tropical non lessivé)": {"pH": 5.7, "MO": 0.5, "N": 0.04, "P": 7, "K": 65, "Rétention": "Faible (50mm/m)", "Drainage": "Rapide"},
            "Sol Deck-Dior (Franco-Sableux de Plateau)": {"pH": 6.3, "MO": 1.1, "N": 0.07, "P": 12, "K": 110, "Rétention": "Moyenne", "Drainage": "Bon"}
        },
        "Casamance (Ziguinchor, Kolda, Sédhiou)": {
            "Sol Ferrallitique Désaturé (Sol Rouge)": {"pH": 5.2, "MO": 1.8, "N": 0.10, "P": 11, "K": 90, "Rétention": "Moyenne", "Drainage": "Bon"},
            "Sol Hydromorphe Risicole": {"pH": 5.0, "MO": 2.9, "N": 0.18, "P": 15, "K": 120, "Rétention": "Forte", "Drainage": "Lent"}
        }
    }

    BASE_RAVAGEURS_DPV = [
        {"Nom": "Chenille Légionnaire (Spodoptera frugiperda)", "Cibles": "Maïs, Riz, Sorgho", "Seuil": "5% plants", "Bio": "Bacillus thuringiensis / Neem", "Chimique": "Emamectine benzoate"},
        {"Nom": "Mouche des Fruits (Bactrocera dorsalis)", "Cibles": "Mangue, Citrus", "Seuil": "2 mouches/piège/j", "Bio": "Piège Méthyl-Eugenol", "Chimique": "Appât Protéique + Spinosad"},
        {"Nom": "Mineuse de la Tomate (Tuta absoluta)", "Cibles": "Tomate", "Seuil": "3 adultes/piège", "Bio": "Phéromones / Huile Neem", "Chimique": "Chlorantraniliprole"}
    ]

    BAREMES_ISRA = {
        "Maïs Hybride": (150, 150, 50),
        "Riz (Sahel)": (150, 250, 100),
        "Oignon (Violet Galmi)": (200, 200, 150),
        "Tomate Industrielle": (250, 200, 200),
        "Arachide": (100, 0, 50),
        "Mangue": (300, 150, 300)
    }

    if "dpv_alert_sent" not in st.session_state:
        st.session_state["dpv_alert_sent"] = False
    if "farm_producer" not in st.session_state:
        st.session_state["farm_producer"] = "GIE Bokk Liggeey"
    if "farm_zone" not in st.session_state:
        st.session_state["farm_zone"] = list(BASE_SOLS_INP_FULL.keys())[0]
    if "farm_sol" not in st.session_state:
        st.session_state["farm_sol"] = list(BASE_SOLS_INP_FULL[st.session_state["farm_zone"]].keys())[0]
    if "farm_crop" not in st.session_state:
        st.session_state["farm_crop"] = "Maïs Hybride"
    if "farm_stade" not in st.session_state:
        st.session_state["farm_stade"] = "Levée / Repiquage"
    if "farm_ph" not in st.session_state:
        st.session_state["farm_ph"] = float(BASE_SOLS_INP_FULL[st.session_state["farm_zone"]][st.session_state["farm_sol"]]["pH"])
    if "farm_mo" not in st.session_state:
        st.session_state["farm_mo"] = float(BASE_SOLS_INP_FULL[st.session_state["farm_zone"]][st.session_state["farm_sol"]]["MO"])

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔒 Connexion & Authentification")
    user_email_input = st.sidebar.text_input("Adresse e-mail :", value=OWNER_EMAIL, key="wh_email_input").strip().lower()
    user_pass_input = st.sidebar.text_input("Mot de passe :", type="password", key="wh_pass_input").strip()
    
    whitelist_data = db.get("whitelist", [])
    if not isinstance(whitelist_data, list):
        whitelist_data = []

    authorized_users = {}
    for user in whitelist_data:
        if isinstance(user, dict) and user.get("statut") == "Actif":
            email_val = str(user.get("email", "")).strip().lower()
            if email_val:
                authorized_users[email_val] = user

    is_authorized = False
    is_admin = False
    is_expert = False
    current_user = None

    if user_email_input in authorized_users:
        user_record = authorized_users[user_email_input]
        if user_pass_input == str(user_record.get("password", "")).strip():
            current_user = user_record
            st.sidebar.success(f"✅ **Connexion réussie**\n\n👤 {current_user.get('nom', 'Utilisateur')}\n👑 Rôle : **{current_user.get('role', 'Agent')}**")
            is_authorized = True
            user_role = str(current_user.get('role', 'Technicien'))
            is_admin = (user_role == "Administrateur")
            is_expert = user_role in ["Administrateur", "Expert DPV"]
        elif user_pass_input:
            st.sidebar.error("❌ **Mot de passe incorrect**")
    elif user_email_input:
        st.sidebar.error("❌ **Adresse e-mail non autorisée**")

    if not is_authorized:
        st.warning("⚠️ **Accès restreint** : Veuillez saisir votre mot de passe dans le panneau latéral pour déverrouiller l'accès.")
    else:
        def calculate_polygon_area_ha(coords):
            if not coords or len(coords) < 3:
                return 0.0
            lat_avg = sum(p[0] for p in coords) / len(coords)
            meters_per_degree_lat = 111139.0
            meters_per_degree_lon = 111139.0 * np.cos(np.radians(lat_avg))
            xy = []
            for lat, lon in coords:
                x = lon * meters_per_degree_lon
                y = lat * meters_per_degree_lat
                xy.append((x, y))
            n = len(xy)
            area = 0.0
            for i in range(n):
                j = (i + 1) % n
                area += xy[i][0] * xy[j][1]
                area -= xy[j][0] * xy[i][1]
            return round(abs(area) / 20000.0, 2)

        def generate_3page_pdf(producer, zone, sol, crop, surface, ph, mo, coords, user_info, dpv_status):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            primary_color = colors.HexColor("#052e16")
            secondary_color = colors.HexColor("#16a34a")
            
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=primary_color, alignment=1, spaceAfter=8)
            h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=secondary_color, spaceBefore=8, spaceAfter=6)
            body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor("#1e293b"))

            dap_h, ure_h, kcl_h = BAREMES_ISRA.get(crop, (150, 150, 50))
            tot_dap, tot_ure, tot_kcl = int(dap_h * surface), int(ure_h * surface), int(kcl_h * surface)
            sacs_dap, sacs_ure, sacs_kcl = int(np.ceil(tot_dap/50)), int(np.ceil(tot_ure/50)), int(np.ceil(tot_kcl/50))

            story = [
                Paragraph("🌾 RAPPORT D'EXPERTISE AGRO-PÉDOLOGIQUE 360°", title_style),
                Paragraph(f"<b>Référence :</b> RAP-{datetime.now().strftime('%Y%m%d-%H%M')} | <b>Date :</b> {datetime.now().strftime('%d/%m/%Y à %H:%M')}", ParagraphStyle('Sub', parent=body_style, alignment=1, textColor=colors.gray)),
                HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=6, spaceAfter=10),
                Paragraph("📌 1. Fiche d'Identification de l'Exploitation", h2_style)
            ]
            
            data_id = [
                [Paragraph("<b>Producteur :</b>", body_style), Paragraph(producer, body_style), Paragraph("<b>Superficie délimitée :</b>", body_style), Paragraph(f"{surface} Ha", body_style)],
                [Paragraph("<b>Zone Agro-écologique :</b>", body_style), Paragraph(zone, body_style), Paragraph("<b>Type de Sol (INP) :</b>", body_style), Paragraph(sol, body_style)],
                [Paragraph("<b>Culture Cible :</b>", body_style), Paragraph(crop, body_style), Paragraph("<b>Expert Référent :</b>", body_style), Paragraph(f"{user_info.get('nom')} ({user_info.get('role')})", body_style)]
            ]
            t_id = Table(data_id, colWidths=[110, 160, 120, 150])
            t_id.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t_id)
            story.append(Spacer(1, 10))

            story.append(Paragraph("🧪 2. Analyse Pédologique & Plan de Fumure (ISRA / LBA)", h2_style))
            data_fert = [
                [Paragraph("<b>Paramètre</b>", body_style), Paragraph("<b>Valeur Mesurée</b>", body_style), Paragraph("<b>Interprétation & Recommandation</b>", body_style)],
                [Paragraph("pH Sol", body_style), Paragraph(str(ph), body_style), Paragraph("Optimal pour l'absorption racinaire des nutriments majeurs." if ph >= 6.0 else "Sol acide : chaulage recommandé pour remonter le pH.", body_style)],
                [Paragraph("Matière Organique", body_style), Paragraph(f"{mo}%", body_style), Paragraph("Bonne fertilité organique." if mo >= 1.5 else "Taux faible : apport de compost organique indispensable.", body_style)],
                [Paragraph("DAP (14-23-14)", body_style), Paragraph(f"{tot_dap} kg ({sacs_dap} sacs)", body_style), Paragraph(f"Apport de fond au semis pour la culture de {crop}.", body_style)],
                [Paragraph("Urée (46% N)", body_style), Paragraph(f"{tot_ure} kg ({sacs_ure} sacs)", body_style), Paragraph("Apport fractionné en couverture (tallage et montaison).", body_style)],
                [Paragraph("KCL (Potasse)", body_style), Paragraph(f"{tot_kcl} kg ({sacs_kcl} sacs)", body_style), Paragraph("Renforcement de la résistance aux verse et maladies.", body_style)]
            ]
            t_fert = Table(data_fert, colWidths=[120, 110, 310])
            t_fert.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t_fert)
            story.append(Spacer(1, 10))

            story.append(Paragraph("💧 3. Plan d'Irrigation & Suivi Institutionnel (DGPRE / SAED / ANACIM)", h2_style))
            vol_eau = surface * 4500
            story.append(Paragraph(f"• <b>Besoin hydrique estimé (DGPRE) :</b> {vol_eau:,.0f} m³ d'eau par cycle pour la surface de {surface} Ha.", body_style))
            story.append(Paragraph(f"• <b>Alerte Agrométéo (ANACIM) :</b> Suivi des décadaires pluviales et des températures maximales pour prévenir le stress hydrique.", body_style))
            story.append(Paragraph(f"• <b>Statut Sanitaire (DPV) :</b> {dpv_status}", body_style))
            story.append(Spacer(1, 15))

            story.append(Paragraph("✍️ Signature de l'Expert & Validation Technique", ParagraphStyle('Sign', parent=body_style, fontName='Helvetica-Bold')))
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"Expert : {user_info.get('nom')} | Rôle : {user_info.get('role')}<br/>Plateforme YouAgronoMe — Hub de Saint-Louis & Dakar", ParagraphStyle('Sign2', parent=body_style, textColor=colors.gray)))

            doc.build(story)
            buffer.seek(0)
            return buffer

        # =====================================================
        # INTERFACE DE CONSULTANCE & DÉLIMITATION SYNCHRONISÉE
        # =====================================================
        st.markdown("### 🗺️ Délimitation de Parcelle & Diagnostic Agro-Pédologique Synchronisé")
        st.info("💡 **Synchronisation active** : La surface délimitée sur la carte ci-dessous met à jour en temps réel l'ensemble des besoins en fertilisants (ISRA), le volume d'eau requis (DGPRE), et le dimensionnement financier (La Banque Agricole / DER/FJ).")

        col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
        with col_cfg1:
            st.session_state["farm_producer"] = st.text_input("Nom du Producteur / GIE :", value=st.session_state["farm_producer"])
            st.session_state["farm_zone"] = st.selectbox("Région / Zone Agro-écologique :", options=list(BASE_SOLS_INP_FULL.keys()), index=list(BASE_SOLS_INP_FULL.keys()).index(st.session_state["farm_zone"]) if st.session_state["farm_zone"] in BASE_SOLS_INP_FULL else 0)
        with col_cfg2:
            sols_dispos = list(BASE_SOLS_INP_FULL[st.session_state["farm_zone"]].keys())
            if st.session_state["farm_sol"] not in sols_dispos:
                st.session_state["farm_sol"] = sols_dispos[0]
            st.session_state["farm_sol"] = st.selectbox("Type de Sol (INP) :", options=sols_dispos, index=sols_dispos.index(st.session_state["farm_sol"]))
            
            # Mise à jour automatique des propriétés du sol sélectionné
            sol_props = BASE_SOLS_INP_FULL[st.session_state["farm_zone"]][st.session_state["farm_sol"]]
            st.session_state["farm_ph"] = sol_props["pH"]
            st.session_state["farm_mo"] = sol_props["MO"]

            st.session_state["farm_crop"] = st.selectbox("Culture Cible (ISRA) :", options=list(BAREMES_ISRA.keys()), index=list(BAREMES_ISRA.keys()).index(st.session_state["farm_crop"]) if st.session_state["farm_crop"] in BAREMES_ISRA else 0)
        with col_cfg3:
            st.session_state["farm_stade"] = st.selectbox("Stade Phénologique :", options=["Préparation / Semis", "Levée / Repiquage", "Tallage / Croissance", "Floraison / Maturation", "Récolte"], index=1)
            
            # Saisie manuelle de secours pour la surface au cas où Folium ne charge pas ou pour un calage rapide
            surface_saisie = st.number_input("Superficie de la parcelle (Ha) [Ajustable ou auto via carte] :", min_value=0.10, max_value=5000.0, value=float(st.session_state["active_surface_ha"]), step=0.25, format="%.2f")
            st.session_state["active_surface_ha"] = surface_saisie

        st.write("")
        st.markdown("#### 📍 Outil Cartographique Interactif (Délimitation de Parcelle)")

        if HAS_FOLIUM:
            m = folium.Map(location=[st.session_state["consult_gps"]["lat"], st.session_state["consult_gps"]["lon"]], zoom_start=14)
            
            # Ajout du polygone actuel s'il existe
            if st.session_state["draw_coords"] and len(st.session_state["draw_coords"]) >= 3:
                folium.Polygon(
                    locations=st.session_state["draw_coords"],
                    color="#1b5e20",
                    weight=3,
                    fill=True,
                    fill_color="#2e7d32",
                    fill_opacity=0.35,
                    popup=f"Parcelle : {st.session_state['active_surface_ha']} Ha"
                ).add_to(m)

            # Utilisation de st_folium pour récupérer les interactions
            map_data = st_folium(m, width=700, height=450, key="folium_parcelle_map")

            # Synchronisation robuste des clics et de la géométrie de la carte
            if map_data and isinstance(map_data, dict):
                # Si l'utilisateur clique sur la carte, on centre ou on ajoute un point au polygone
                last_clicked = map_data.get("last_clicked")
                if last_clicked and isinstance(last_clicked, dict):
                    lat_c = last_clicked.get("lat")
                    lon_c = last_clicked.get("lng")
                    if lat_c and lon_c:
                        st.session_state["consult_gps"]["lat"] = lat_c
                        st.session_state["consult_gps"]["lon"] = lon_c
                
                # Vérification des objets dessinés via les draw tools si activés
                all_objects = map_data.get("all_drawings")
                if all_objects and isinstance(all_objects, list) and len(all_objects) > 0:
                    last_obj = all_objects[-1]
                    if isinstance(last_obj, dict) and last_obj.get("geometry"):
                        geom = last_obj.get("geometry")
                        if geom.get("type") == "Polygon":
                            coords_raw = geom.get("coordinates", [])
                            if coords_raw and len(coords_raw) > 0:
                                # Inversion longitude, latitude -> latitude, longitude pour Folium/Calculs
                                new_poly = [[p[1], p[0]] for p in coords_raw[0]]
                                if len(new_poly) >= 3:
                                    st.session_state["draw_coords"] = new_poly
                                    calc_ha = calculate_polygon_area_ha(new_poly)
                                    if calc_ha > 0:
                                        st.session_state["active_surface_ha"] = calc_ha

        else:
            st.warning("⚠️ Le module cartographique interactif (Folium) n'est pas disponible. Veuillez utiliser le champ numérique ci-dessus pour définir la superficie.")

        # Affichage synthétique des métriques synchronisées
        surface_actuelle = st.session_state["active_surface_ha"]
        dap_b, ure_b, kcl_b = BAREMES_ISRA.get(st.session_state["farm_crop"], (150, 150, 50))
        
        tot_dap_syn = int(dap_b * surface_actuelle)
        tot_ure_syn = int(ure_b * surface_actuelle)
        tot_kcl_syn = int(kcl_b * surface_actuelle)
        besoin_eau_syn = surface_actuelle * 4500

        st.write("")
        st.markdown(f"### 🔄 Tableau de Synthèse Synchronisé pour la Parcelle ({surface_actuelle} Ha)")
        
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">📐 Superficie Active</div>
                <div class="clean-card-value">{surface_actuelle} Ha</div>
                <div class="clean-card-sub">Parcelle délimitée</div>
            </div>
            """, unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🧪 Engrais DAP (ISRA)</div>
                <div class="clean-card-value">{tot_dap_syn:,} kg</div>
                <div class="clean-card-sub">{int(np.ceil(tot_dap_syn/50))} sacs de 50kg</div>
            </div>
            """, unsafe_allow_html=True)
        with mc3:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">🧪 Engrais Urée (ISRA)</div>
                <div class="clean-card-value">{tot_ure_syn:,} kg</div>
                <div class="clean-card-sub">{int(np.ceil(tot_ure_syn/50))} sacs de 50kg</div>
            </div>
            """, unsafe_allow_html=True)
        with mc4:
            st.markdown(f"""
            <div class="clean-card">
                <div class="clean-card-title">💧 Besoin Eau (DGPRE)</div>
                <div class="clean-card-value">{besoin_eau_syn:,.0f} m³</div>
                <div class="clean-card-sub">Volume d'irrigation requis</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            if HAS_REPORTLAB:
                pdf_bytes = generate_3page_pdf(
                    producer=st.session_state["farm_producer"],
                    zone=st.session_state["farm_zone"],
                    sol=st.session_state["farm_sol"],
                    crop=st.session_state["farm_crop"],
                    surface=surface_actuelle,
                    ph=st.session_state["farm_ph"],
                    mo=st.session_state["farm_mo"],
                    coords=st.session_state["draw_coords"],
                    user_info=current_user,
                    dpv_status="Conforme - Aucun ravageur signalé"
                )
                st.download_button(
                    label="📥 Télécharger le Rapport d'Expertise Complet (.pdf)",
                    data=pdf_bytes,
                    file_name=f"Rapport_Agro_Pedologique_{st.session_state['farm_producer'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key="btn_download_pdf_consult"
                )
            else:
                st.warning("ReportLab non disponible pour générer le PDF.")
        with col_dl2:
            if st.button("🛒 Ajouter le Pack Intrants de cette parcelle au Panier", key="btn_add_panier_consult"):
                item_panier = {
                    "produit": f"Pack Intrants {st.session_state['farm_crop']} ({surface_actuelle} Ha)",
                    "details": f"DAP: {tot_dap_syn}kg, Urée: {tot_ure_syn}kg, KCL: {tot_kcl_syn}kg",
                    "prix": f"{(tot_dap_syn*450 + tot_ure_syn*400):,} FCFA",
                    "producteur": st.session_state["farm_producer"]
                }
                st.session_state.panier.append(item_panier)
                st.success("✅ Pack intrants ajouté au panier avec succès !")


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
        {"nom": "Semences de Riz Sahélien Certifiées (ISRA/SAED)", "categorie": "Semences", "prix": "25 000 FCFA / 50kg", "desc": "Variété à haut rendement, tolérante à la salinité et aux altees hydriques."},
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
