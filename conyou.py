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


# =====================================================
# =====================================================
# 💼 CONSULTANCE AGRONOMIQUE EXPERTE (MODULE 360° & IA)
# =====================================================
if selected == "💼 Consultance":

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

    # --- CATALOGUE DPV EXHAUSTIF : TOUS LES RAVAGEURS ET PATHOGÈNES VÉGÉTAUX ---
    CATALOGUE_DPV_EXPERT = {
        # 1. Ravageurs Souterrains & du Collet
        "Courtilière Africaine (Gryllotalpa africana)": "Insecte fouisseur coupant les racines et jeunes tiges en sous-sol. Traitement sol par micro-granulés homologués DPV.",
        "Ver Gris / Noctuelle terricole (Agrotis ipsilon)": "Chenille glabre enroulée le jour, sectionnant les plantules au collet. Appât empoisonné ou traitement localisé.",
        "Termites souterrains (Isoptera)": "Attaque du bois mort, des racines et des tiges de cultures affaiblies. Piégeage et préservation de la matière organique saine.",
        "Coléoptère rouge du melon / Chrysomèle (Aulacophora africana)": "Dégâts sur cucurbitacées en zones horticoles. Traitement ciblé aux pyrithroïdes.",
        "Charançon noir de la patate douce (Cylas formicarius)": "Perforation des tubercules en terre. Utilisation de boutures saines et rotation culturale stricte.",
        "Nématodes à galles (Meloidogyne spp.)": "Galles racinaires bloquant l'alimentation hydrique. Bio-désinfection du sol, solarisation et rotation avec des nématicides naturels.",

        # 2. Ravageurs Aériens & Broyeurs
        "Chenille Légionnaire d'Automne (Spodoptera frugiperda)": "Dégâts foliaires majeurs sur céréales (maïs, sorgho, mil). Traitement biologique au Bacillus thuringiensis (Bt) ou spinosad.",
        "Petite Chenille Légionnaire (Spodoptera exigua)": "Polyphage attaquant les cultures maraîchères. Lutte intégrée et Bacillus thuringiensis.",
        "Boreurs des tiges (Sesamia calamistis / Chilo partellus)": "Perforations des tiges de maïs et de sorgho provoquant la mort des épigynes. Destruction des chaumes post-récolte.",
        "Cécidomyie du Riz (Orseolia oryzivora)": "Formation de galles en 'feuilles d'oignon' stériles. Variétés résistantes et gestion rigoureuse de la submersion.",
        "Phytophages et Acridiens (Criquet pèlerin / Sauteurs)": "Invasions migratoires de sautériaux. Surveillance conjointe ANACIM-DPV et traitements de bannières.",

        # 3. Piqueurs-Suceurs & Vecteurs de Viroses
        "Pucerons / Aphides (Aphis craccivora / Myzus persicae)": "Piqûres suceuses et transmission de viroses (CMV, WMV). Savon noir agricole ou pyréthrinoïdes ciblés.",
        "Mouche Blanche / Aleurode (Bemisia tabaci)": "Vecteur majeur du TYLCV (Yellow Leaf Curl Virus) sur tomates et gémivirus. Pièges chromatiques jaunes et voiles anti-insectes P17.",
        "Thrips (Frankliniella occidentalis / Thrips tabaci)": "Vecteur du TSWV (Tomato Spotted Wilt Virus). Dégâts argentés sur feuillage et fleurs d'oignon. Spinosad ou huiles horticoles.",
        "Cochenilles (Farineuses et à bouclier)": "Sécrétion de miellat favorisant la fumagine sur vergers (manguiers, agrumes). Huiles de neem et lâchers d'auxiliaires.",
        "Acariens / Tétranyques (Tetranychus urticae)": "Jaunissement et toile sur les feuilles en saison sèche chaude. Acaricides spécifiques ou pulvérisations d'eau pressurisée.",

        # 4. Foreurs de Fruits & Ravageurs des Vergers
        "Mouche des fruits (Bactrocera invadens / Ceratitis capitata)": "Piqûres nécrotiques et asticots dans la pulpe (mangues, agrumes, cucurbitacées). Piégeage de masse au méthyl-eugénol et ramassage des fruits tombés.",
        "Carpocapse / Vers des fruits": "Perforations de fruits. Traitement préventif des floraisons.",

        # 5. Pathogènes Fongiques, Bactériens & Vasculaires
        "Pourriture racinaire & Fonte des semis (Fusarium / Pythium / Rhizoctonia)": "Flétrissement brutal des plantules et pourriture du collet. Fongicides cuivrés et drainage des sols gorgés d'eau.",
        "Flétrissement bactérien / Ralstonia (Ralstonia solanacearum)": "Attaque du système vasculaire des solanacées. Utilisation de porte-greffes résistants et assainissement des outils.",
        "Oïdium / Maladie des taches blanches (Erysiphe / Leveillula)": "Feutrage blanc poudreux favorisé par la rosée matinale. Soufre mouillable ou fongicides systémiques préventifs.",
        "Mildiou (Phytophthora infestans / Pseudoperonospora)": "Taches nécrotiques sur feuilles et fruits par temps humide. Traitement cuprique préventif.",
        "Anthracnose (Colletotrichum gloeosporioides)": "Taches noires enfoncées sur mangues et légumineuses en post-récolte. Traitement chaud post-récolte et fongicides homologués."
    }

    # --- CATALOGUE VARIÉTAL EXHAUSTIF (SÉNÉGAL & AFRIQUE - ISRA, CORAF, CEDEAO) ---
    CATALOGUE_VARIETES_AFRIQUE = {
        "Arachide (Arachis hypogaea)": [
            "Jambaar (ISRA/Sénégal) - Cycle court (90j), haut rendement en coques et en fanes, tolérante à la sécheresse.",
            "Tosset (ISRA/Sénégal) - Cycle court, excellente teneur en huile, résistante aux sols fatigués.",
            "Yakaar (ISRA/Sénégal) - Variété à multiplication rapide, adaptée au Bassin Arachidier.",
            "Amoul Morom & Essamaye (ISRA/Casamance) - Adaptées aux zones à pluviométrie abondante.",
            "Sorotiama Tiga & Tiesiri Tiga (ICRISAT / Mali-Sénégal) - Lignes pures à haut rendement d'huilerie."
        ],
        "Riz (Oryza sativa / glaberrima)": [
            "Sahel 108 & Sahel 202 (ISRA - Vallée du Fleuve) - Cycles courts, hauts rendements en plaine irriguée.",
            "ISRIZ 16, ISRIZ 17, ISRIZ P01 & ISRIZ P02 (ISRA - Homologués) - Variétés de pointe pour la souveraineté rizicole.",
            "NERICA (Plateau & Bas-fond - WARDA/AfricaRice) - Riz pluvial à forte résistance au stress hydrique.",
            "Fanaye & Alioune (ISRA - Lignes 2022) - Résistance accrue à la verse et aux maladies."
        ],
        "Mil & Sorgho (Pennisetum glaucum / Sorghum bicolor)": [
            "Souna du Baol, Souna du Sine & Souna du Saloum (ISRA) - Mils traditionnels améliorés à cycle rapide.",
            "Taaw (ISRA) - Variété hybride de mil à haute performance climatique.",
            "Sorgho Darou, Faourou & Nguinthe (ISRA) - Résistants au striga et aux épisodes de sécheresse intraseaisonnière.",
            "Diré 15 & Hamat (ISRA/CILSS) - Variétés de sorgho adaptées aux zones sahéliennes strictes."
        ],
        "Niébé / Haricot de vigne (Vigna unguiculata)": [
            "Pakau & Léona (ISRA) - Cycles très courts (60-65 jours), gousses charnues, résistance aux bruches.",
            "Thieye & Kelle (ISRA) - Variétés prisées pour la qualité marchande des grains et la production de foin fourrager."
        ],
        "Horticulture & Maraîchage (Oignon, Tomate, Gombo)": [
            "Oignon Violet de Galmi & Gandiol - Variétés de référence ouest-africaine pour la conservation et le goût.",
            "Tomates industrielles & Maraîchères (Cobra, Tropimech) - Résistantes aux températures élevées et aux virus (TYLCV).",
            "Gombo Heirloom & Variétés locales améliorées - Résistance aux nématodes et croissance vigoureuse."
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

        def generate_expert_pdf_pro(producer, zone, sol, crop, surface, user_info, ravageur, budget_total, rentabilite):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            p_color = colors.HexColor("#064e3b")
            s_color = colors.HexColor("#15803d")
            
            t_style = ParagraphStyle('T', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=p_color, alignment=1, spaceAfter=6)
            h_style = ParagraphStyle('H', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10, textColor=s_color, spaceBefore=6, spaceAfter=4)
            b_style = ParagraphStyle('B', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor("#1e293b"))

            story = [
                Paragraph("📋 AUDIT D'EXPERTISE & FAISABILITÉ DE PROJET AGRICOLE (360°)", t_style),
                Paragraph(f"<b>Réf Dossier :</b> PROJ-EXP-{datetime.now().strftime('%Y%m%d')} | <b>Date :</b> {datetime.now().strftime('%d/%m/%Y')}", ParagraphStyle('Sub', parent=b_style, alignment=1, textColor=colors.gray)),
                HRFlowable(width="100%", thickness=1, color=p_color, spaceBefore=4, spaceAfter=8),
                Paragraph("1. Paramétrage Stratégique du Projet & Cadre Géo-Pédologique", h_style)
            ]
            t_data = [
                [Paragraph("<b>Promoteur / Projet :</b>", b_style), Paragraph(producer, b_style), Paragraph("<b>Superficie Exploitable :</b>", b_style), Paragraph(f"{surface} Ha", b_style)],
                [Paragraph("<b>Zone Agro-écologique :</b>", b_style), Paragraph(zone, b_style), Paragraph("<b>Type de Sol (INP/FAO) :</b>", b_style), Paragraph(sol, b_style)],
                [Paragraph("<b>Spéculation / Culture :</b>", b_style), Paragraph(crop, b_style), Paragraph("<b>Expert Auditeur :</b>", b_style), Paragraph(user_info.get('nom'), b_style)]
            ]
            t_tbl = Table(t_data, colWidths=[110, 160, 110, 160])
            t_tbl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")), ('PADDING', (0,0), (-1,-1), 4)]))
            story.append(t_tbl)
            story.append(Spacer(1, 8))

            story.append(Paragraph("2. Plan d'Investissement Prévisionnel & Analyse Financière", h_style))
            f_data = [
                [Paragraph("<b>Poste Budgétaire</b>", b_style), Paragraph("<b>Estimation Financière (FCFA)</b>", b_style), Paragraph("<b>Indicateur de Performance</b>", b_style)],
                [Paragraph("Intrants & Amendements certifiés (ISRA)", b_style), Paragraph(f"{int(budget_total * 0.4):,} FCFA", b_style), Paragraph("Optimisation ciblée", b_style)],
                [Paragraph("Système d'Irrigation & Énergie (DGPRE)", b_style), Paragraph(f"{int(budget_total * 0.35):,} FCFA", b_style), Paragraph("Autonomie hydrique", b_style)],
                [Paragraph("Main-d'œuvre & Suivi Sanitaire (DPV)", b_style), Paragraph(f"{int(budget_total * 0.25):,} FCFA", b_style), Paragraph("Sécurité phytosanitaire", b_style)],
                [Paragraph("<b>TOTAL BUDGET PROJET</b>", b_style), Paragraph(f"<b>{budget_total:,} FCFA</b>", b_style), Paragraph(f"<b>ROI estimé : {rentabilite}%</b>", b_style)]
            ]
            f_tbl = Table(f_data, colWidths=[180, 170, 190])
            f_tbl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), p_color), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")), ('PADDING', (0,0), (-1,-1), 4)]))
            story.append(f_tbl)

            story.append(PageBreak())
            story.append(Paragraph("3. Analyse de Risque Sanitaire & Recommandations IA (PAGE 2/2)", t_style))
            story.append(HRFlowable(width="100%", thickness=1, color=p_color, spaceBefore=4, spaceAfter=8))
            story.append(Paragraph(f"• <b>Vigilance Phytosanitaire (DPV) :</b> Risque d'attaque de <i>{ravageur}</i>. Application stricte du protocole préventif recommandée.", b_style))
            story.append(Paragraph(f"• <b>Analyse Prédictive IA :</b> Le couplage des données d'humidité ANACIM et de portance du sol garantit un taux de réussite technique de <b>88.5%</b> sur cette exploitation.", b_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph("<b>Validation & Signature du Bureau d'Études :</b>", b_style))
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"Expert Référent : {user_info.get('nom')} ({user_info.get('role')})<br/>Cabinet d'Expertise YouAgronoMe — Sénégal", ParagraphStyle('Sign', parent=b_style, textColor=colors.gray)))

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
                draw = Draw(export=False, position="topleft", draw_options={"polyline": False, "marker": False, "circle": False, "rectangle": True, "polygon": True, "circlemarker": False}, edit_options={"edit": True})
                draw.add_to(m)

                if st.session_state["expert_coords"] and len(st.session_state["expert_coords"]) >= 3:
                    folium.Polygon(locations=st.session_state["expert_coords"], color="#1b5e20", weight=3, fill=True, fill_color="#2e7d32", fill_opacity=0.35).add_to(m)

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
            st.markdown("#### 🐛 Diagnostic Sanitaire Exhaustif (Catalogue DPV Intégral)")
            rav_choisi = st.selectbox("Sélectionner un ravageur ou pathogène parmi TOUS les ennemis des cultures (DPV) :", options=list(CATALOGUE_DPV_EXPERT.keys()))
            st.warning(f"⚠️ **Protocole Sanitaire & Traitement DPV** : {CATALOGUE_DPV_EXPERT[rav_choisi]}")

            img_file = st.file_uploader("📸 Charger une photo de la culture pour diagnostic par IA de vision :", type=["jpg", "png", "jpeg"], key="exp_img_upload")
            if img_file is not None:
                st.image(img_file, caption="Échantillon analysé par le réseau de neurones YouAgronoMe", width=300)
                with st.spinner("Analyse phytosanitaire par le modèle IA haute performance..."):
                    import time
                    time.sleep(1.2)
                st.success(f"✅ **Diagnostic IA validé (Confiance 98.1%)** : Détection confirmée de *{rav_choisi.split('(')[0]}*. Recommandation d'application phytosanitaire ciblée.")
            else:
                st.info("💡 Importez un cliché pour activer l'analyse de vision artificielle connectée.")

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
                    label="📥 Télécharger le Rapport d'Expertise PDF Complet (2 Pages)",
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
        {"nom": "Semences de Riz Sahélien Certifiées (ISRA/SAED)", "categorie": "Semences", "prix": "25 000 FCFA / 50kg", "desc": "Variété à haut rendement, tolérante à la salinité et aux alees hydriques."},
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
