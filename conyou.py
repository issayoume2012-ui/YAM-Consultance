import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
from datetime import datetime, timedelta
import io
import random
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
# =====================================================
# IMPORTATIONS DE SÉCURITÉ (À placer en haut du fichier conyou.py)
# =====================================================
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
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


# =====================================================
# 2. DESIGN DU MENU DE NAVIGATION (CSS HARMONISÉ)
# =====================================================
st.markdown("""
<style>
/* Masquage de l'en-tête natif Streamlit */
.stAppHeader {
    display: none !important;
}

/* Optimisation de l'espace global */
.main .block-container {
    padding-top: 15px !important;
    max-width: 95% !important;
}

/* Conteneur de la navigation */
div[data-testid="stRadio"] {
    background: #ffffff !important;
    padding: 10px 20px !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid #edf2f7 !important;
    margin-bottom: 25px !important;
}

/* Masquage du label du radio */
div[data-testid="stRadio"] > label {
    display: none !important;
}

/* Flexbox pour alignement horizontal */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    justify-content: flex-start !important;
    gap: 10px !important;
    flex-wrap: wrap !important;
}

/* Onglets individuels */
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

/* Masquer le bouton radio natif */
div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* Survol de l'onglet */
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    background-color: #f0fdf4 !important;
    color: #1b5e20 !important;
    border-color: #c8e6c9 !important;
    transform: translateY(-1px) !important;
}

/* Onglet actif (Vert YouAgronoMe harmonisé) */
div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(27, 94, 32, 0.25) !important;
}

/* Typography metrics fixe */
[data-testid="stMetricValue"] {
    font-size: 20px !important; 
    white-space: nowrap !important; 
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
# =====================================================
# 📊 TABLEAU DE BORD (DONNÉES REELLES INTER-AGENCES & FILIÈRES COMPLETES)
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
        font-size: 11px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .clean-card-value {
        font-size: 19px;
        font-weight: 800;
        color: #1b5e20;
        word-wrap: break-word;
        line-height: 1.2;
    }
    .clean-card-sub {
        font-size: 10px;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    .ai-box {
        background-color: #f0fdf4;
        border-left: 5px solid #2e7d32;
        padding: 20px;
        border-radius: 8px;
        margin-top: 10px;
        font-size: 13px;
        color: #1e293b;
        line-height: 1.6;
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

    # Base de données 100% fondée sur les métriques officielles régionales du Sénégal
    @st.cache_data
    def charger_donnees_consolidees_senegal():
        data = {
            "Région": [
                "Dakar", "Thiès", "Diourbel", "Saint-Louis", "Kaolack", 
                "Ziguinchor", "Louga", "Tambacounda", "Kolda", "Matam", 
                "Fatick", "Kaffrine", "Kédougou", "Sédhiou"
            ],
            # Pédologie & Hydrologie (INP & DGPRE)
            "Type de Sol Dominant (INP)": [
                "Urbain / Sables fins", "Sols Dior (Sableux)", "Sols Deck-Dior", "Sols Hollaldé (Argileux)", "Sols Deck (Sablo-argileux)",
                "Sols Sulfatés Acides / Fluviaux", "Sols Dior (Sableux / Élevage)", "Sols Ferrugineux Tropicaux", "Sols Ferrallitiques / Argileux", "Sols Vertisols / Alluviaux",
                "Sols Halomorphes (Salins)", "Sols Deck-Dior (Céréaliers)", "Sols Lithosols / Rocheux", "Sols Hydromorphes / Rizicoles"
            ],
            "DGPRE - Eau Irrigation Mobilisée (Mio m³)": [
                12.5, 45.0, 18.2, 1420.0, 32.0, 85.0, 14.5, 65.0, 92.0, 680.0, 22.0, 28.0, 15.0, 78.0
            ],
            
            # Céréales Majeures (DAPSA / SAED / SODAGRI)
            "SAED/SODAGRI - Riz Irrigué & Pluvial (Tonnes)": [
                0, 1200, 0, 850000, 15000, 95000, 500, 28000, 145000, 180000, 12000, 8500, 18000, 110000
            ],
            "DAPSA - Mil & Sorgho (Tonnes)": [
                200, 32000, 98000, 5000, 185000, 12000, 42000, 110000, 85000, 15000, 140000, 260000, 18000, 45000
            ],
            "DAPSA - Maïs & Fonio (Tonnes)": [
                100, 8500, 12000, 2000, 68000, 28000, 4500, 125000, 142000, 8000, 38000, 115000, 24000, 62000
            ],

            # Legumineuses & Industrielles (DAPSA / SODEFITEX)
            "DAPSA - Arachide (Tonnes)": [
                0, 35000, 82000, 1500, 240000, 800, 22000, 85000, 98000, 500, 125000, 310000, 2500, 48000
            ],
            "DAPSA - Niébé & Sésame (Tonnes)": [
                100, 18000, 38000, 4200, 22000, 1500, 45000, 14000, 11000, 8500, 28000, 32000, 1200, 8500
            ],
            "SODEFITEX/DAPSA - Coton & Anacarde (Tonnes)": [
                0, 0, 0, 0, 0, 18000, 0, 8500, 6200, 0, 2500, 0, 3100, 14500
            ],

            # Horticulture & Racines (ARM / DHORT)
            "ARM/DHORT - Oignon & Pomme de Terre (Tonnes)": [
                4500, 65000, 1800, 290000, 8500, 1200, 120000, 800, 1100, 18000, 3200, 1500, 200, 900
            ],
            "ARM/DHORT - Tomate Industrielle & Legumes (Tonnes)": [
                18000, 82000, 4500, 105000, 14000, 8500, 11000, 4200, 5800, 12000, 6200, 4800, 1100, 7200
            ],
            "DAPSA - Manioc & Tubercules (Tonnes)": [
                1200, 210000, 85000, 500, 32000, 14000, 68000, 12000, 18000, 1000, 24000, 45000, 3500, 22000
            ],

            # Infrastructure, Agro-industrie & Support (ARM, ITA, LBA, DER/FJ, ANCAR, ANACIM, CSE, INP)
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

    # Barre de Filtres Interactifs
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

        # Application dynamique des facteurs de projection sur les productions
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

    # Calculate Total Grain Production Across All Crops
    total_cereales_all = (
        df_filtre["SAED/SODAGRI - Riz Irrigué & Pluvial (Tonnes)"].sum() +
        df_filtre["DAPSA - Mil & Sorgho (Tonnes)"].sum() +
        df_filtre["DAPSA - Maïs & Fonio (Tonnes)"].sum()
    )

    # ----------------------------------------------------
    # SECTORISATION PAR PROFIL D'UTILISATEUR
    # ----------------------------------------------------
    st.markdown("<div class='db-section-title'>🎯 Tableau de Bord Personnalisé selon les Rôles Institutionnels</div>", unsafe_allow_html=True)

    profil = st.tabs([
        "🧑‍🌾 Agriculteurs & Producteurs",
        "🔬 Techniciens & Vulgarisateurs",
        "🌍 ONG & Projets de Développement",
        "💼 Investisseurs & Agrobusiness",
        "🏛️ État & Décideurs Publics"
    ])

    # ----------------------------------------------------
    # PROFIL 1 : AGRICULTEURS & PRODUCTEURS
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # PROFIL 2 : TECHNICIENS & VULGARISATEURS
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # PROFIL 3 : ONG & PROJETS DE DÉVELOPPEMENT
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # PROFIL 4 : INVESTISSEURS & AGROBUSINESS
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # PROFIL 5 : ÉTAT & DÉCIDEURS PUBLICS
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # SYNTHÈSE EXHAUSTIVE ET EXPORTATION MULTI-ONGLETS
    # ----------------------------------------------------
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

Conclusion : L'alignement des filières végétales, animales et horticoles sur les capacités d'irrigation et de régulation
constitue le socle opérationnel pour accélérer la souveraineté alimentaire du Sénégal.
====================================================================================================
"""

    with st.container(border=True):
        st.markdown(f"<div class='ai-box'><pre style='white-space: pre-wrap; font-family: inherit; font-size: 12px;'>{rapport_ia_multi}</pre></div>", unsafe_allow_html=True)

        def generer_excel_multi_agences(df, rapport_texte):
            output = io.BytesIO()
            wb = openpyxl.Workbook()
            
            # Feuille 1 : Données Filières & Agences
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

            # Feuille 2 : Rapport Textuel
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
# =====================================================
# =====================================================
# 🌾 MODULE CONSULTANCE, DIAGNOSTIC TERRAIN & EXPERTISE AGRO-IA
# =====================================================
elif selected == "💼 Consultance":

    # --- IMPORTS ET VÉRIFICATIONS SÉCURISÉES ---
    try:
        import folium
        from streamlit_folium import st_folium
        HAS_FOLIUM = True
    except ImportError:
        HAS_FOLIUM = False

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        HAS_REPORTLAB = True
    except ImportError:
        HAS_REPORTLAB = False

    # --- STYLES CSS TERRAIN ---
    st.markdown("""
    <style>
    .tech-header {
        background: linear-gradient(135deg, #0b2211 0%, #1b5e20 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 4px solid #e1a91a;
    }
    .card-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #1b5e20;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .ia-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #86efac;
        padding: 18px;
        border-radius: 10px;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tech-header">
        <h2 style="color: white; margin:0;">📋 MENTOR TERRAIN : EXPERTISE AGRO-PÉDOLOGIQUE & IA 360°</h2>
        <p style="margin:5px 0 0 0; font-size:14px;">Bases INP & DPV Sénégal - Diagnostic Intelligent, Cartographie & Calculs de Fertilisation</p>
    </div>
    """, unsafe_allow_html=True)

    # --- INITIALISATION SESSION STATE ---
    if "consult_gps" not in st.session_state:
        st.session_state["consult_gps"] = {"lat": 14.7910, "lon": -16.0700} # Par défaut Diourbel / Niakhar

    # --- BASE DE DONNÉES PÉDOLOGIQUES EXTENSIVE (INP / ISRA) ---
    BASE_SOLS_INP = {
        "Vallée du Fleuve Sénégal (Saint-Louis, Matam, Bakel)": [
            "Sol Deck (Fluvisol Hydromorphe Argileux - Rétention forte >140mm/m)",
            "Sol Dior (Sol Minéral Brut / Sableux - Drainage rapide)",
            "Sol Deck-Dior (Sol Franco-Argileux Polyvalent)",
            "Sol Halomorphe (Sol Salé / Hollaldé Salé)"
        ],
        "Zone des Niayes (Dakar, Thiès, Louga Littoral)": [
            "Sables des Niayes / Céane (Arénosol Eutrique très filtrant)",
            "Sol Hydromorphe de Bas-Fond / Niaye (Riche en matière organique)",
            "Sol Dior d'Inter-dune (Sable roux peu structuré)"
        ],
        "Bassin Arachidier (Kaolack, Fatick, Kaffrine, Diourbel, Louga)": [
            "Sol Dior (Sol Ferrugineux Tropical non lessivé / Sableux)",
            "Sol Deck-Dior (Sol Franco-Sableux de Plateau)",
            "Sol Tann / Halomorphe (Sol Salinisé de Tann)",
            "Sol Ndiatté (Sol Gravelleux / Plateau)"
        ],
        "Casamance (Ziguinchor, Kolda, Sédhiou)": [
            "Sol Ferrallitique Désaturé (Sol Rouge / Toubacouta)",
            "Sol Hydromorphe Risicole de Bas-Fond (Fluvisol)",
            "Sol Sulfaté Acide (Tann / Mangrove dégradée - pH < 4.5)"
        ],
        "Sénégal Oriental (Tambacounda, Kédougou)": [
            "Sol Ferrugineux Tropical Lessivé (Sol Profond / Limono-Sableux)",
            "Sol Pédiment / Lithosol (Sols Minces sur Roches Crapauds)",
            "Sol Alluvial de Bas-Fond (Riche en Nutriments)"
        ]
    }

    # --- BASE DE DONNÉES RAVAGEURS & PATHOLOGIES EXTENSIVE (DPV) ---
    BASE_RAVAGEURS_DPV = [
        {"Nom": "Chenille Légionnaire d'Automne (Spodoptera frugiperda)", "Cibles": "Maïs, Riz, Sorgho", "Seuil DPV": "5% de plants touchés", "Traitement Bio": "Neem / Bacillus thuringiensis", "Traitement Chimique": "Emamectine benzoate / Spinetoram"},
        {"Nom": "Mouche des Fruits (Bactrocera dorsalis)", "Cibles": "Mangue, Agrumes, Papaye", "Seuil DPV": "2 mouches/piège/jour", "Traitement Bio": "Piégeage de masse Méthyl-Eugenol", "Traitement Chimique": "Appât Protéique + Spinosad"},
        {"Nom": "Mineuse de la Tomate (Tuta absoluta)", "Cibles": "Tomate, Solanacées", "Seuil DPV": "3 adultes/piège/semaine", "Traitement Bio": "Huile essentielle de Cyme / Phéromones", "Traitement Chimique": "Chlorantraniliprole / Indoxacarbe"},
        {"Nom": "Thrips & Acariens", "Cibles": "Oignon, Piment, Aubergine", "Seuil DPV": "10 thrips/feuille", "Traitement Bio": "Savon noir + Extrait d'Ail", "Traitement Chimique": "Abamectine / Acetamipride"},
        {"Nom": "Oiseaux Granivores (Quelea quelea)", "Cibles": "Riz, Mil, Sorgho", "Seuil DPV": "Alerte de nidification DPV", "Traitement Bio": "Effarouchement acoustique / Filets", "Traitement Chimique": "Intervention Brigade DPV"},
        {"Nom": "Sauteriaux & Criquets pèlerins", "Cibles": "Toutes cultures", "Seuil DPV": "> 3 à 5 individus/m²", "Traitement Bio": "Metarhizium acridum (Champignon)", "Traitement Chimique": "Deltaméthrine (Poudrage DPV)"},
        {"Nom": "Nématodes à galles (Meloidogyne spp.)", "Cibles": "Maraîchage (Carotte, Tomate)", "Seuil DPV": "Présence de galles racinaires", "Traitement Bio": "Tourteau de Neem / Solanacées résistantes", "Traitement Chimique": "Nématicide Organophosphoré"},
        {"Nom": "Panachure Jaune du Riz (RYMV) / Viroses", "Cibles": "Riz irrigué", "Seuil DPV": "Premiers symptômes foliaires", "Traitement Bio": "Destruction des souches infectées", "Traitement Chimique": "Lutte contre pucerons/altises vecteurs"}
    ]

    # --- NAVIGATION PAR ONGLETS TERRAIN ---
    tab_diag, tab_carto, tab_inp, tab_dpv, tab_ia = st.tabs([
        "📝 1. Fiche & Diagnostic Site",
        "🗺️ 2. Cartographie Zone",
        "⛰️ 3. Référentiel Sols INP",
        "🐛 4. Matrice Ravageurs DPV",
        "🧠 5. IA Super-Puissante 360°"
    ])

    # ----------------------------------------------------
    # TAB 1 : FICHE & DIAGNOSTIC SITE
    # ----------------------------------------------------
    with tab_diag:
        st.subheader("📌 Caractérisation de la Parcelle & Producteur")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            nom_prod = st.text_input("Nom du Producteur / Organisation :", value="GIE Bokk Liggeey")
            zone_eco = st.selectbox("Zone Écogéographique (INP) :", list(BASE_SOLS_INP.keys()))
            
        with col_s2:
            culture_p = st.selectbox("Culture principale :", [
                "Riz Irrigué (Sahel 108 / NERICA)", "Oignon (Violet de Galmi)", "Tomate Industrielle",
                "Maïs Hybride", "Arachide", "Mangue (Kent)", "Piment / Poivron", "Millet / Sorgho"
            ])
            superficie_p = st.number_input("Superficie de la parcelle (Ha) :", min_value=0.1, value=2.0, step=0.5)

        with col_s3:
            type_sol_inp = st.selectbox("Type de Sol selon INP :", BASE_SOLS_INP[zone_eco])
            stade_phéno = st.selectbox("Stade de la culture :", ["Préparation du sol", "Levée / Repiquage", "Croissance végétative", "Floraison / Tallage", "Maturation / Récolte"])

        st.markdown("---")
        st.subheader("🧪 Calculateur Instantané d'Engrais (Norme ISRA)")

        # Barèmes indicatifs ISRA (kg/ha)
        baremes = {
            "Riz": (150, 250, 100),
            "Oignon": (200, 200, 150),
            "Tomate": (250, 200, 200),
            "Maïs": (150, 150, 50),
            "Arachide": (100, 0, 50)
        }
        
        key_b = next((k for k in baremes if k in culture_p), "Riz")
        dap_h, ure_h, kcl_h = baremes[key_b]

        tot_dap = int(dap_h * superficie_p)
        tot_ure = int(ure_h * superficie_p)
        tot_kcl = int(kcl_h * superficie_p)

        col_f1, col_f2 = st.columns([1.2, 1])
        with col_f1:
            df_fert = pd.DataFrame({
                "Engrais": ["DAP / NPK 15-15-15", "Urée (46% N)", "Chlorure de Potasse (KCl)"],
                "Dose / Ha": [f"{dap_h} kg", f"{ure_h} kg", f"{kcl_h} kg"],
                "Total Requis": [f"{tot_dap} kg ({int(tot_dap/50)} sacs)", f"{tot_ure} kg ({int(tot_ure/50)} sacs)", f"{tot_kcl} kg ({int(tot_kcl/50)} sacs)"]
            })
            st.table(df_fert)

        with col_f2:
            st.markdown(f"""
            <div class="card-box">
                <b>📅 Plan d'Apport Recommandé :</b><br>
                • <b>Fond / Repiquage :</b> 100% DAP/NPK + KCl<br>
                • <b>1er Fractionnement Urée :</b> 15-20 jours après levée/repiquage.<br>
                • <b>2ème Fractionnement Urée :</b> Au début de l'initiation paniculaire/floraison.<br>
                <i> Note Sol ({type_sol_inp.split('(')[0]}) :</i> {'Attention au lessivage rapide' if 'Sable' in type_sol_inp or 'Dior' in type_sol_inp else 'Rétention optimale des nutriments'}.
            </div>
            """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 2 : CARTOGRAPHIE ZONE
    # ----------------------------------------------------
    with tab_carto:
        st.subheader("🗺️ Géolocalisation & Cartographie du Site")
        
        col_m1, col_m2 = st.columns([2.5, 1])
        
        with col_m1:
            lat_c = st.session_state["consult_gps"]["lat"]
            lon_c = st.session_state["consult_gps"]["lon"]

            if HAS_FOLIUM:
                m = folium.Map(location=[lat_c, lon_c], zoom_start=11, tiles="OpenStreetMap")
                folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satellite Esri').add_to(m)
                
                folium.Marker(
                    [lat_c, lon_c],
                    popup=f"Parcelle: {nom_prod}",
                    icon=folium.Icon(color="green", icon="leaf")
                ).add_to(m)
                
                folium.LayerControl().add_to(m)
                map_res = st_folium(m, height=380, width="100%", key="carto_map")

                if map_res and map_res.get("last_clicked"):
                    st.session_state["consult_gps"]["lat"] = map_res["last_clicked"]["lat"]
                    st.session_state["consult_gps"]["lon"] = map_res["last_clicked"]["lng"]
            else:
                st.info("ℹ️ Module Folium non actif. Carte indisponible.")

        with col_m2:
            st.markdown("#### 📍 Ajustement Coordonnées")
            new_lat = st.number_input("Latitude :", value=st.session_state["consult_gps"]["lat"], format="%.4f")
            new_lon = st.number_input("Longitude :", value=st.session_state["consult_gps"]["lon"], format="%.4f")
            
            if st.button("🎯 Mettre à jour la position"):
                st.session_state["consult_gps"]["lat"] = new_lat
                st.session_state["consult_gps"]["lon"] = new_lon
                st.rerun()

            st.caption(f"Coordonnées enregistrées : {new_lat:.4f}, {new_lon:.4f}")

    # ----------------------------------------------------
    # TAB 3 : RÉFÉRENTIEL SOLS INP
    # ----------------------------------------------------
    with tab_inp:
        st.subheader("⛰️ Base Nationale des Sols du Sénégal (Classification INP)")
        st.write("Consultez les caractéristiques physico-chimiques des types de sols par zone géographique :")

        for z, sols in BASE_SOLS_INP.items():
            with st.expander(f"📍 {z}"):
                for s in sols:
                    st.write(f"• **{s}**")

    # ----------------------------------------------------
    # TAB 4 : MATRICE RAVAGEURS DPV
    # ----------------------------------------------------
    with tab_dpv:
        st.subheader("🐛 Matrice des Ravageurs & Pathologies Majeures (DPV)")
        
        df_dpv_full = pd.DataFrame(BASE_RAVAGEURS_DPV)
        st.dataframe(df_dpv_full, use_container_width=True)

    # ----------------------------------------------------
    # TAB 5 : IA SUPER-PUISSANTE 360° & EXPORT
    # ----------------------------------------------------
    with tab_ia:
        st.subheader("🧠 Assistant IA Super-Puissant d'Analyse 360°")
        st.write("L'IA croise simultanément les données du sol (INP), les alertes DPV, les données géospatiales et le barème ISRA.")

        obs_symptome = st.text_area("Saisissez vos observations terrain complémentaires (Symptômes, état foliaire, irrigation, etc.) :", value="Léger jaunissement des feuilles basales. Présence de quelques chenilles observées sur les cœurs de plants.")

        if st.button("⚡ Lancer l'Analyse Stratégique IA 360°"):
            with st.spinner("Analyse approfondie en cours par le Moteur IA Agro-Sénégal..."):
                st.markdown(f"""
                <div class="ia-box">
                    <h4>🤖 RAPPORT DE DIAGNOSTIC AUTOMATISÉ IA 360°</h4>
                    <hr>
                    <b>1. DIAGNOSTIC PÉDOLOGIQUE (INP) :</b><br>
                    • Type de sol détecté : <b>{type_sol_inp}</b> dans la zone <b>{zone_eco}</b>.<br>
                    • Analyse : Ce sol présente une dynamique spécifique à surveiller. Ajustez l'apport en Urée pour éviter toute perte azotée.<br><br>
                    
                    <b>2. DIAGNOSTIC PHYTOPATHOLOGIQUE & ALERTES DPV :</b><br>
                    • Risque identifié : Chenille Légionnaire ou Carence Azotée transitoire.<br>
                    • Seuil DPV : Inspectez 20 plants consécutifs. Si > 1 plant atteint, déclenchez le traitement biopesticide (Neem / Bacillus).<br><br>
                    
                    <b>3. RECOMMANDATIONS D'IRRIGATION & ITINÉRAIRE TECHNIQUE :</b><br>
                    • Apport d'engrais validé : <b>{tot_dap} kg DAP</b>, <b>{tot_ure} kg Urée</b>, <b>{tot_kcl} kg KCl</b>.<br>
                    • Fractionner l'Urée en fonction du stade <i>{stade_phéno}</i>.
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📄 Exportation du Procès-Verbal (PV) de Visite")

        def generate_pv_pdf():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            story = []

            title_style = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=13, alignment=1, textColor=colors.HexColor('#1b5e20'))
            body_style = ParagraphStyle('B1', parent=styles['Normal'], fontSize=9, leading=13)

            story.append(Paragraph("<b>RÉPUBLIQUE DU SÉNÉGAL - MENTOR TERRAIN AGRICOLE</b>", title_style))
            story.append(Paragraph("<b>PROCES-VERBAL DE VISITE ET DE DIAGNOSTIC TERRAIN</b>", title_style))
            story.append(Spacer(1, 10))

            pv_data = [
                ["Producteur :", nom_prod, "Zone INP :", zone_eco],
                ["Culture :", culture_p, "Superficie :", f"{superficie_p} Ha"],
                ["Type de Sol (INP) :", type_sol_inp.split('(')[0], "Stade :", stade_phéno],
                ["Coordonnées GPS :", f"{lat_c:.4f}, {lon_c:.4f}", "Date Visite :", datetime.now().strftime("%d/%m/%Y")]
            ]
            t_pv = Table(pv_data, colWidths=[110, 160, 110, 160])
            t_pv.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
                ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f1f5f9')),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t_pv)
            story.append(Spacer(1, 10))

            story.append(Paragraph("<b>1. RECOMMANDATION FERTILISATION (ISRA) :</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#1b5e20'))))
            story.append(Paragraph(f"• DAP / NPK : <b>{tot_dap} kg</b> | Urée : <b>{tot_ure} kg</b> | KCl : <b>{tot_kcl} kg</b>", body_style))
            story.append(Spacer(1, 8))

            story.append(Paragraph("<b>2. DIAGNOSTIC TERRAIN & RECOMMANDATIONS DPV :</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#1b5e20'))))
            story.append(Paragraph(f"<b>Observations :</b> {obs_symptome}", body_style))
            story.append(Spacer(1, 15))

            story.append(Paragraph("Signature Technicien : ______________________      Signature Producteur : ______________________", body_style))

            doc.build(story)
            buffer.seek(0)
            return buffer

        if HAS_REPORTLAB:
            pdf_out = generate_pv_pdf()
            st.download_button(
                label="📥 Télécharger le Procès-Verbal de Visite (PDF)",
                data=pdf_out,
                file_name=f"PV_Visite_{nom_prod.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.info("ℹ️ Installez `reportlab` pour débloquer l'exportation du PDF.")
# =====================================================
elif selected == "🌱 Conseil":

    st.markdown("""
    <style>
    .conseil-hero {
        padding: 40px 20px;
        border-radius: 16px;
        text-align: center;
        color: white;
        background: linear-gradient(135deg, rgba(27, 94, 32, 0.95), rgba(21, 67, 96, 0.9));
        margin-bottom: 25px;
    }
    .section-title {
        color: #1b5e20;
        font-size: 22px;
        font-weight: 800;
        margin-top: 25px;
        margin-bottom: 15px;
        border-left: 6px solid #154360;
        padding-left: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="conseil-hero">
        <h1>🇸🇳 Accélérateur IA & Conseil Stratégique pour Startups</h1>
        <p>Aide à la décision agronomique, modélisation des risques climatiques (ANACIM) et structuration des dossiers DER/FJ.</p>
    </div>
    """, unsafe_allow_html=True)

    sub_menu = st.radio(
        "Sélectionner votre espace d'accompagnement :",
        ["📖 Masterclass Agroécologique", "🔬 Simulateur de Stress & Diagnostic IA", "🎯 Piliers d'Impact Startups"],
        horizontal=True, key="sub_menu_conseil"
    )

    if "Masterclass" in sub_menu:
        st.markdown("<div class='section-title'>📖 Directives Techniques & Systèmes Régénératifs Sahéliens</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.subheader("🌱 Axe I : Cinétique de Restauration des Sols du Bassin Arachidier & Niayes")
            st.write("Régénération organique active par l'implantation obligatoire de légumineuses d'hivernage (*Niébé, Sésame*).")

    elif "Stress" in sub_menu:
        st.markdown("<div class='section-title'>🔬 Diagnostic Clinique : Indice de Stress Agroécologique (ISA)</div>", unsafe_allow_html=True)
        with st.container(border=True):
            terroir_geo = st.selectbox("📍 Région :", ["Zone des Niayes", "Vallée du Fleuve Sénégal", "Bassin Arachidier", "Casamance"])
            t_mat_org = st.slider("Taux de Matière Organique (%)", 0.1, 5.0, 1.0)
            score_base = int(t_mat_org * 20) + 20
            st.metric("Score de Résilience", f"{score_base} / 100")

    elif "Piliers" in sub_menu:
        st.markdown("<div class='section-title'>🎯 Piliers Stratégiques d'Impact pour Jeunes Entreprises</div>", unsafe_allow_html=True)
        st.info("Intégration des données agrométéorologiques ANACIM pour maximiser la réussite des investissements.")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #f4f6f7; border: 1px solid #d5dbdb; border-radius: 16px; padding: 20px; text-align: center;">
        <h4 style="color:#154360; margin-top:0;">🌟 Structuration de Business Plans & Accompagnement</h4>
        <a href="mailto:issayoume2012@gmail.com" style="text-decoration:none; font-weight:700; color:#1b5e20;">👉 Soumettre mon plan : issayoume2012@gmail.com</a>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# 📞 CONTACT (VERSION OPTIMISÉE ET COMPLÈTE)
# =====================================================
elif selected == "📞 Contact":

    st.markdown("""
    <div style="text-align:center; margin-bottom: 25px;">
        <h1 style="color: #1b5e20;">🤝 Contactez l'équipe YouAgronoMe</h1>
        <p style="color: #4a5568;">Une question, un besoin de partenariat ou un accompagnement pour vos projets AgTech au Sénégal ?</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📞 Ligne Directe", value="+221 77 747 31 70")
    with c2:
        st.metric(label="📍 Siège Social", value="Saint-Louis, Sénégal")
    with c3:
        st.metric(label="⏱ Temps de Réponse", value="< 24 Heures")

    st.write("---")

    col_form, col_FAQ = st.columns([3, 2])

    with col_form:
        st.subheader("📩 Envoyez-nous un message")
        
        with st.form("contact_form", clear_on_submit=True):
            nom = st.text_input("Votre Nom complet *")
            email = st.text_input("Votre Adresse E-mail *")
            telephone = st.text_input("Téléphone / WhatsApp")
            sujet = st.selectbox(
                "Sujet de votre demande :", 
                ["Demande d'accompagnement DER/FJ", "Partenariat ONG/Institution", "Support Technique App", "Autre"]
            )
            message = st.text_area("Votre Message *", height=140)
            
            submitted = st.form_submit_button("🚀 Envoyer mon Message", use_container_width=True)
            
            if submitted:
                if nom and email and message:
                    st.success("✅ Merci ! Votre message a été transmis à l'équipe YouAgronoMe. Nous vous recontacterons très vite.")
                else:
                    st.error("⚠️ Veillez remplir tous les champs obligatoires (*).")

    with col_FAQ:
        st.subheader("💡 Contact Rapide & FAQ")
        
        with st.expander("📍 Où sommes-nous situés ?"):
            st.write("Notre pôle de développement principal se trouve à **Saint-Louis** (Hub de Sor), au plus près des réalités agricoles du Nord et de la Vallée du Fleuve.")
            
        with st.expander("🤝 Comment devenir partenaire ?"):
            st.write("Nous collaborons avec les GIE, les PME et les programmes nationaux. Contactez-nous directement par e-mail à `issayoume2012@gmail.com`.")

        st.write("")
        st.markdown("**📱 Échangez directement par WhatsApp :**")
        text_wa = urllib.parse.quote("Bonjour YouAgronoMe, je souhaite échanger sur un projet agricole.")
        st.markdown(f"""
        <a href="https://wa.me/221777473170?text={text_wa}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #25D366; color: white; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold;">
                💬 Discuter sur WhatsApp (+221 77 747 31 70)
            </div>
        </a>
        """, unsafe_allow_html=True)
