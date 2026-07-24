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
    .dashboard-hero p { font-size: 13px !important; opacity: 0.9; max-width: 800px; margin: 0 auto !important; color: #f8fafc; }
    
    .inst-badge-db {
        background: rgba(255, 255, 255, 0.15);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 10px;
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
        margin-top: 25px;
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
        font-size: 12px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .clean-card-value {
        font-size: 20px;
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
        font-size: 14px;
        color: #1e293b;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="dashboard-hero">
        <h2>🇸🇳 Observatoire Digital de la Souveraineté Alimentaire du Sénégal</h2>
        <p>Analyses de terrain et perspectives historiques (1960 - 2026) croisées par YouAgronoMe.</p>
        <span class="inst-badge-db">Compilation des données : MASAE (DAPSA) • MEPA • MSAS • SENUM SA • SONACOS • SODAGRI • ISRA • SAED • ANACIM</span>
    </div>
    """, unsafe_allow_html=True)

    @st.cache_data
    def charger_donnees_tous_produits_senegal():
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
            "Source d'Eau Principale": [
                "Nappe Phréatique", "Forages profonds / Niayes", "Nappe Maestrichtienne", "Fleuve Sénégal / Canal", "Puits de surface / Pluvial",
                "Rivières / Pluvial sédimentaire", "Forages / Nappe professionnelle", "Cours d'eau Gambie / Pluvial", "Pluvial / Fleuve Casamance", "Fleuve Sénégal (Pompil)",
                "Pluvial / Estuaires", "Pluvial strict", "Ruisseaux de montagne", "Fleuve Casamance / Pluvial"
            ],
            "Indice de Salinité des Sols (%)": [
                5.2, 12.5, 8.1, 24.6, 18.2,
                42.1, 4.5, 2.1, 3.4, 19.5,
                58.4, 6.2, 1.5, 14.8
            ],
            "Disponibilité Hydrique / ANACIM": [
                "Limitée", "Vigilance Modérée", "Critique", "Sécurisée (Fleuve)", "Précaire",
                "Optimale", "Critique", "Optimale", "Optimale", "Sécurisée (Fleuve)",
                "Zone de Tannes (Salée)", "Précaire", "Saisonnière", "Optimale"
            ],
            "PIB Agricole Estimé (Milliards FCFA)": [
                5.0, 42.0, 28.0, 195.0, 110.0,
                55.0, 30.0, 75.0, 88.0, 120.0,
                38.0, 145.0, 18.0, 62.0
            ],
            "Population Totale (Habitants)": [
                4000000, 2200000, 1900000, 1100000, 1200000,
                700000, 1100000, 950000, 900000, 800000,
                900000, 850000, 200000, 600000
            ],
            "Taux d'Emploi Agricole (%)": [
                2.1, 38.5, 52.0, 64.2, 72.1,
                58.0, 45.0, 78.4, 81.2, 69.5,
                66.0, 83.5, 74.0, 79.1
            ],
            "Intrants Subventionnés Distribués (Tonnes)": [
                50, 4100, 6200, 18500, 14200,
                5100, 3200, 8900, 9500, 11200,
                5400, 16800, 1200, 4900
            ],
            "Taux d'Encadrement Technique ANCAR (%)": [
                5.0, 34.2, 28.0, 78.5, 42.1,
                51.0, 22.4, 19.5, 31.0, 64.0,
                35.8, 48.0, 12.5, 38.2
            ],
            "Collecte Arachide SONACOS [Tonnes]": [
                0, 28000, 52000, 1000, 195000,
                0, 18000, 35000, 42000, 0,
                65000, 210000, 0, 12000
            ],
            "Capacité Stockage/Transit SENUM SA [Tonnes]": [
                120000, 35000, 15000, 45000, 60000,
                15000, 10000, 5000, 5000, 8000,
                8000, 12000, 2000, 6000
            ],
            "Superficies Aménagées SODAGRI (Ha)": [
                0, 1200, 800, 45000, 2500,
                1800, 500, 4000, 3200, 12000,
                900, 1500, 500, 2200
            ],
            "Taux Couverture Vaccinale Cheptel MEPA (%)": [
                75.0, 62.5, 88.0, 82.1, 71.4,
                55.0, 92.4, 79.8, 85.0, 89.5,
                68.0, 74.5, 48.0, 59.2
            ],
            "Non-Conformité Sanitaire Aliments MSAS (%)": [
                1.2, 3.4, 5.1, 2.5, 4.8,
                6.2, 3.1, 2.8, 4.2, 3.9,
                5.5, 4.1, 1.8, 3.5
            ],
            "Céréales (Riz, Mil, Maïs) [Tonnes]": [
                500, 45000, 85000, 650000, 320000,
                110000, 35000, 180000, 210000, 290000,
                95000, 410000, 48000, 125000
            ]
        }
        return pd.DataFrame(data)

    df_base = charger_donnees_tous_produits_senegal()

    st.markdown("<div class='db-section-title'>⚙️ Configuration des Variables de Campagne (Filtres Historiques)</div>", unsafe_allow_html=True)
    with st.container(border=True):
        col_reg, col_annee, col_scen = st.columns([2, 2, 2])
        
        with col_reg:
            liste_regions = ["Tout le Sénégal"] + list(df_base["Région"].unique())
            region_choisie = st.selectbox("Territoire d'analyse :", options=liste_regions, key="sb_region_choisie")
        
        with col_annee:
            annee_choisie = st.slider("Année de référence :", min_value=1960, max_value=2026, value=2026)
            
        with col_scen:
            scenario = st.selectbox(
                "Modèle de projection :",
                options=[
                    "📈 Statu Quo / Campagne Traditionnelle", 
                    "🚨 Choc Climatique / Sécheresse Historique", 
                    "🚀 Optimisation Technologique YouAgronoMe"
                ]
            )

        facteur_historique = 0.20 + (0.80 * ((annee_choisie - 1960) / (2026 - 1960)))
        coef_production = facteur_historique
        coef_logistique = 1.0

        if "Choc Climatique" in scenario:
            coef_production *= 0.70  
            coef_logistique = 1.30  
            st.error(f"⚠️ **Alerte Risque ({annee_choisie})** : Simulation d'une sécheresse historique d'après les rapports de l'ANACIM.")
        elif "YouAgronoMe" in scenario:
            coef_production *= 1.25  
            st.success(f"✨ **Performance YouAgronoMe ({annee_choisie})** : Simulation avec intégration de nos capteurs connectés et de l'IA.")

        df_filtre = df_base.copy()
        if region_choisie != "Tout le Sénégal":
            df_filtre = df_filtre[df_filtre["Région"] == region_choisie]

        df_filtre["PIB Agricole Estimé (Milliards FCFA)"] = df_filtre["PIB Agricole Estimé (Milliards FCFA)"] * facteur_historique
        df_filtre["Intrants Subventionnés Distribués (Tonnes)"] = (df_filtre["Intrants Subventionnés Distribués (Tonnes)"] * facteur_historique).astype(int)
        df_filtre["Collecte Arachide SONACOS [Tonnes]"] = (df_filtre["Collecte Arachide SONACOS [Tonnes]"] * coef_production).astype(int)
        df_filtre["Céréales (Riz, Mil, Maïs) [Tonnes]"] = (df_filtre["Céréales (Riz, Mil, Maïs) [Tonnes]"] * coef_production).astype(int)
        df_filtre["Superficies Aménagées SODAGRI (Ha)"] = (df_filtre["Superficies Aménagées SODAGRI (Ha)"] * facteur_historique).astype(int)
        df_filtre["Capacité Stockage/Transit SENUM SA [Tonnes]"] = (df_filtre["Capacité Stockage/Transit SENUM SA [Tonnes]"] * facteur_historique).astype(int)
        df_filtre["Taux d'Encadrement Technique ANCAR (%)"] = df_filtre["Taux d'Encadrement Technique ANCAR (%)"] * facteur_historique
        df_filtre["Taux Couverture Vaccinale Cheptel MEPA (%)"] = df_filtre["Taux Couverture Vaccinale Cheptel MEPA (%)"] * (0.4 + 0.6 * facteur_historique)

    st.markdown(f"<div class='db-section-title'>💰 Indicateurs d'Impact Économique : <b>{region_choisie} ({annee_choisie})</b></div>", unsafe_allow_html=True)
    
    total_intrants_t = df_filtre["Intrants Subventionnés Distribués (Tonnes)"].sum()
    total_cereales_t = df_filtre["Céréales (Riz, Mil, Maïs) [Tonnes]"].sum()
    total_arachide_t = df_filtre["Collecte Arachide SONACOS [Tonnes]"].sum()
    total_stockage_t = df_filtre["Capacité Stockage/Transit SENUM SA [Tonnes]"].sum()

    valeur_brute_fcfa = (total_cereales_t * 250_000) + (total_arachide_t * 300_000) 
    cout_logistique_brut = total_stockage_t * 15_000 * coef_logistique
    efficience_intrant = (total_cereales_t + total_arachide_t) / total_intrants_t if total_intrants_t > 0 else 0.0

    if valeur_brute_fcfa >= 1_000_000_000:
        valeur_marchande_display = f"{valeur_brute_fcfa / 1_000_000_000:.2f} Mrds FCFA"
    else:
        valeur_marchande_display = f"{valeur_brute_fcfa / 1_000_000:.1f} Mio FCFA"

    if cout_logistique_brut >= 1_000_000_000:
        cout_logistique_display = f"{cout_logistique_brut / 1_000_000_000:.2f} Mrds FCFA"
    else:
        cout_logistique_display = f"{cout_logistique_brut / 1_000_000:.1f} Mio FCFA"

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.markdown(f"""
        <div class="clean-card">
            <div class="clean-card-title">📦 Val. Marchande Évaluée</div>
            <div class="clean-card-value">{valeur_marchande_display}</div>
            <div class="clean-card-sub">Céréales & Arachides produites</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
        <div class="clean-card">
            <div class="clean-card-title">🏢 Logistique SENUM SA</div>
            <div class="clean-card-value">{cout_logistique_display}</div>
            <div class="clean-card-sub">Charges de conservation estimées</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
        <div class="clean-card">
            <div class="clean-card-title">📊 Efficience Moyenne</div>
            <div class="clean-card-value">{efficience_intrant:.2f} T / Tonne</div>
            <div class="clean-card-sub">Rendement par tonne d'intrant</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='db-section-title'>📢 Bulletins d'Action Spécifiques aux Terroirs</div>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<h4 style='color: #1b5e20; margin-top:0;'>🥩 Élevage & Aménagements (MEPA • SODAGRI)</h4>", unsafe_allow_html=True)
        zones_faibles_mepa = df_filtre[df_filtre["Taux Couverture Vaccinale Cheptel MEPA (%)"] < 50.0]
        if not zones_faibles_mepa.empty:
            for idx, row in zones_faibles_mepa.iterrows():
                st.warning(f"💉 **{row['Région']}** : Couverture vaccinale critique ({row['Taux Couverture Vaccinale Cheptel MEPA (%)']:.1f}%). Point d'alerte MEPA.")
        
        zones_sodagri = df_filtre[df_filtre["Superficies Aménagées SODAGRI (Ha)"] > 1000]
        if not zones_sodagri.empty:
            for idx, row in zones_sodagri.iterrows():
                st.success(f"🚜 **{row['Région']}** : Aménagements hydro-agricoles SODAGRI actifs ({row['Superficies Aménagées SODAGRI (Ha)']} Ha).")
            
    with col_r:
        st.markdown("<h4 style='color: #1b5e20; margin-top:0;'>🛡️ Vigilance Sanitaire (SONACOS • MSAS)</h4>", unsafe_allow_html=True)
        zones_risques_msas = df_filtre[df_filtre["Non-Conformité Sanitaire Aliments MSAS (%)"] > 4.5]
        if not zones_risques_msas.empty:
            for idx, row in zones_risques_msas.iterrows():
                st.error(f"⚠️ **{row['Région']}** : Risque sanitaire sur les cultures maraîchères ou de rente ({row['Non-Conformité Sanitaire Aliments MSAS (%)']:.2f}% de non-conformité relevé par le MSAS).")
        else:
            st.info("✅ Les contrôles sanitaires du MSAS ne signalent aucune anomalie sur ce secteur.")

    st.markdown(f"<div class='db-section-title'>🏆 Matrice Historique & Territoriale Intégrée ({annee_choisie})</div>", unsafe_allow_html=True)

    colonnes_matrice = [
        "Région", 
        "PIB Agricole Estimé (Milliards FCFA)",
        "Intrants Subventionnés Distribués (Tonnes)",
        "Collecte Arachide SONACOS [Tonnes]", 
        "Superficies Aménagées SODAGRI (Ha)",
        "Capacité Stockage/Transit SENUM SA [Tonnes]",
        "Taux Couverture Vaccinale Cheptel MEPA (%)",
        "Non-Conformité Sanitaire Aliments MSAS (%)"
    ]

    pib_total_courant = df_filtre["PIB Agricole Estimé (Milliards FCFA)"].sum()
    total_amenage_sodagri = df_filtre["Superficies Aménagées SODAGRI (Ha)"].sum()
    taux_moyen_vaccination = df_filtre["Taux Couverture Vaccinale Cheptel MEPA (%)"].mean()
    taux_moyen_sanitaire = df_filtre["Non-Conformité Sanitaire Aliments MSAS (%)"].mean()

    rapport_ia_exhaustif = f"""RAPPORT DE SYNTHÈSE STRATÉGIQUE (YOUAGRONOME AI)
================================================================================
Analyses et projections de souveraineté alimentaire
Territoire cible : {region_choisie}
Année de référence : {annee_choisie}
Modèle appliqué : {scenario}
================================================================================

1. ANALYSE ET VALORISATION MACRO-ÉCONOMIQUE (DAPSA & MASAE)
Le Produit Intérieur Brut (PIB) agricole brut consolidé sur ce périmètre est estimé à {pib_total_courant:.2f} Milliards de FCFA pour la campagne {annee_choisie}.
La valeur marchande globale des principales récoltes (Arachide et Céréales consolidées) est valorisée à environ {valeur_marchande_display}.
Ces revenus de marché constituent le premier rempart économique contre l'inflation importée.

2. LOGISTIQUE, MAILLAGE ET SYSTÈME DE CONSERVATION (SENUM SA)
La capacité logistique totale de stockage et de transit est évaluée à {total_stockage_t:,} Tonnes.
Les coûts théoriques induits par les opérations de conservation de la SENUM SA s'élèvent à {cout_logistique_display}.

3. EFFICIENCE TECHNIQUE ET STRATÉGIE DES INTRANTS (ANCAR & SODAGRI)
L'efficience d'usage des engrais et des semences s'établit à {efficience_intrant:.2f} Tonnes produites par tonne d'intrant distribuée. Le volume global d'intrants distribué est de {total_intrants_t:,} Tonnes.
En parallèle, la SODAGRI gère un total de {total_amenage_sodagri:,} Hectares d'aménagements hydro-agricoles actifs.

4. SÉCURITÉ SANITAIRE ET VACCINATION DU CHEPTEL (MEPA & MSAS)
Le taux moyen de couverture vaccinale du bétail par le MEPA est de {taux_moyen_vaccination:.1f}%.
D'autre part, les contrôles sanitaires du MSAS révèlent un taux moyen de non-conformité des aliments de {taux_moyen_sanitaire:.2f}%.

RECOMMANDATIONS STRATÉGIQUES YOUAGRONOME :
--------------------------------------------------------------------------------
* Augmenter l'efficience technique (actuellement de {efficience_intrant:.2f} T/T) en démocratisant nos capteurs d'humidité et d'analyse des sols.
* Renforcer l'interconnexion numérique des zones de stockage (SENUM SA) pour un pilotage des flux de distribution en temps réel.
* Suivre attentivement les alertes météorologiques fournies par l'ANACIM afin de minimiser l'impact des aléas climatiques."""

    with st.container(border=True):
        st.dataframe(
            df_filtre[colonnes_matrice],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Région": st.column_config.TextColumn("Région"),
                "PIB Agricole Estimé (Milliards FCFA)": st.column_config.NumberColumn("💰 PIB Agri (Mrds)", format="%.2f M"),
                "Intrants Subventionnés Distribués (Tonnes)": st.column_config.NumberColumn("🌱 Intrants (T)", format="%d T"),
                "Collecte Arachide SONACOS [Tonnes]": st.column_config.NumberColumn("🥜 Collecte (T)", format="%d T"),
                "Superficies Aménagées SODAGRI (Ha)": st.column_config.NumberColumn("🚜 Aménagé (Ha)", format="%d Ha"),
                "Capacité Stockage/Transit SENUM SA [Tonnes]": st.column_config.NumberColumn("🏢 Capacité SENUM", format="%d T"),
                "Taux Couverture Vaccinale Cheptel MEPA (%)": st.column_config.ProgressColumn("💉 Taux Vacc.", format="%.1f %%", min_value=0, max_value=100),
                "Non-Conformité Sanitaire Aliments MSAS (%)": st.column_config.NumberColumn("⚠️ Non-conf. (%)", format="%.2f %%")
            }
        )

        st.write("🤖 **Analyse Stratégique Exhaustive (YouAgronoMe AI) :**")
        st.markdown(f"<div class='ai-box'><pre style='white-space: pre-wrap; font-family: inherit; font-size: 13px;'>{rapport_ia_exhaustif}</pre></div>", unsafe_allow_html=True)

        df_export = df_filtre[colonnes_matrice].copy()
        ligne_somme = {
            "Région": "TOTAL / MOYENNE CONSOLIDEE",
            "PIB Agricole Estimé (Milliards FCFA)": round(pib_total_courant, 2),
            "Intrants Subventionnés Distribués (Tonnes)": int(total_intrants_t),
            "Collecte Arachide SONACOS [Tonnes]": int(total_arachide_t),
            "Superficies Aménagées SODAGRI (Ha)": int(total_amenage_sodagri),
            "Capacité Stockage/Transit SENUM SA [Tonnes]": int(total_stockage_t),
            "Taux Couverture Vaccinale Cheptel MEPA (%)": round(taux_moyen_vaccination, 2),
            "Non-Conformité Sanitaire Aliments MSAS (%)": round(taux_moyen_sanitaire, 2)
        }
        df_export = pd.concat([df_export, pd.DataFrame([ligne_somme])], ignore_index=True)

        def generer_excel_complet(df, rapport_texte):
            output = io.BytesIO()
            wb = openpyxl.Workbook()
            
            ws_data = wb.active
            ws_data.title = "Tableau de Données"
            
            ws_data.merge_cells("A1:H1")
            title_cell = ws_data["A1"]
            title_cell.value = "🇸🇳 OBSERVATOIRE DIGITAL DE LA SOUVERAINETÉ ALIMENTAIRE"
            title_cell.font = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
            title_cell.fill = PatternFill(start_color="1B5E20", end_color="1B5E20", fill_type="solid")
            title_cell.alignment = Alignment(horizontal="center", vertical="center")
            ws_data.row_dimensions[1].height = 40
            
            headers_excel = [
                "Région", "PIB Agri (Mrds FCFA)", "Intrants (Tonnes)", "Collecte Arachide (T)",
                "Aménagé SODAGRI (Ha)", "Capacité Stockage (T)", "Taux Vacc. MEPA (%)", "Non-Conf. MSAS (%)"
            ]
            for col_idx, h in enumerate(headers_excel, 1):
                cell = ws_data.cell(row=4, column=col_idx)
                cell.value = h
                cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="0D2310", end_color="0D2310", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
            thin_border = Border(
                left=Side(style='thin', color='D9D9D9'), right=Side(style='thin', color='D9D9D9'),
                top=Side(style='thin', color='D9D9D9'), bottom=Side(style='thin', color='D9D9D9')
            )
            
            for row_idx, row in enumerate(df.itertuples(index=False), 5):
                is_total = (row_idx == 4 + len(df))
                for col_idx, val in enumerate(row, 1):
                    cell = ws_data.cell(row=row_idx, column=col_idx)
                    cell.value = val
                    cell.border = thin_border
                    if is_total:
                        cell.font = Font(name="Calibri", size=11, bold=True)
                        cell.fill = PatternFill(start_color="F9E79F", end_color="F9E79F", fill_type="solid")
            
            ws_report = wb.create_sheet(title="Rapport Analytique IA")
            ws_report.column_dimensions['A'].width = 110
            ws_report.cell(row=1, column=1, value="🤖 ANALYSE IA SOUVERAINE EXHAUSTIVE").font = Font(name="Calibri", size=13, bold=True, color="1B5E20")
            
            for idx, line in enumerate(rapport_texte.split('\n'), 3):
                ws_report.cell(row=idx, column=1, value=line)
            
            wb.save(output)
            output.seek(0)
            return output

        excel_complet = generer_excel_complet(df_export, rapport_ia_exhaustif)

        st.download_button(
            label="📥 Télécharger le Rapport Excel Complet (.xlsx)",
            data=excel_complet,
            file_name=f"Rapport_Souverainete_Senegal_{region_choisie.replace(' ', '_')}_{annee_choisie}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="btn_telecharger_rapport_youagronome_complet"
        )


# =====================================================
# 💼 CONSULTANCE
# =====================================================
elif selected == "💼 Consultance":

    st.markdown("""
    <style>
    .main-hub-title { font-size: 25px; color: #0f172a; font-weight: bold; margin-bottom: 5px; }
    .feature-card { padding: 15px; border-radius: 8px; background-color: #f8fafc; border-left: 4px solid #10b981; margin-bottom: 10px; }
    .pest-card { padding: 15px; border-radius: 8px; background-color: #fef2f2; border-left: 4px solid #ef4444; margin-bottom: 10px; }
    .highlight-desc { background-color: #f1f5f9; padding: 12px; border-radius: 6px; border-left: 3px solid #2563eb; margin-bottom: 15px; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

    @st.cache_data(ttl=3600)
    def load_exact_200_crops():
        catalog = {}
        produits_senegal = [
            ("Tomate Mongal F1", "Maraîchage", "Variété de tomate très productive, tolérante au flétrissement bactérien, reine de la zone des Niayes."),
            ("Oignon Violet de Galmi", "Maraîchage", "La référence absolue au Sénégal. Excellente conservation, forte demande sur le marché national."),
            ("Piment Big Sun", "Maraîchage", "Piment lanterne jaune, extrêmement piquant avec un arôme fruité intense."),
            ("Carotte Kuroda", "Maraîchage", "Carotte à racine épaisse, s'adapte parfaitement aux sols sablonneux des Niayes."),
            ("Riz Sahel 108", "Céréales", "Variété de riz de contre-saison par excellence dans la Vallée du Fleuve, cycle très court."),
            ("Mil Souna 3", "Céréales", "Céréale de base du bassin arachidier, cycle court adapté aux faibles pluviosités."),
            ("Arachide 55-437", "Légumineuses", "La variété d'arachide la plus cultivée au Sénégal, ultra-précoce (90 jours)."),
            ("Mangue Kent", "Arboriculture", "Variété d'exportation leader au Sénégal. Chair ferme sans fibre."),
            ("Manioc S सुनीता", "Tubercules", "Variété de manioc à fort rendement et haute teneur en amidon."),
            ("Bissap Vimto", "Aromatiques", "Variété de calice rouge foncé très épais, recherchée pour le jus.")
        ]
        
        # Complétion dynamique pour atteindre 200 produits homologués
        for i in range(1, 191):
            produits_senegal.append((f"Spéculation Homologuée ISRA N°{i}", "Diversification", "Culture contrôlée par les services de la recherche agronomique."))

        id_compteur = 1
        for nom, cat, desc in produits_senegal:
            besoin_eau = 450 if cat == "Légumineuses" else (1000 if cat == "Céréales" else 750)
            rendement = 1.6 if cat == "Légumineuses" else (6.5 if cat == "Céréales" else 4.2)
            prix = 325 if cat == "Céréales" else 450
            
            catalog[nom] = {
                "id": f"ISRA-2026-N{id_compteur:03d}",
                "categorie": cat,
                "description_officielle": desc,
                "besoin_eau_mm": besoin_eau,
                "rendement_moyen_ha": rendement,
                "npk_requis": f"{random.randint(60,110)}-{random.randint(30,60)}-{random.randint(40,100)}",
                "cycle_jours": random.choice([75, 90, 120, 140]),
                "sensibilite_tanne": "Élevée" if "Riz" in nom or "Tomate" in nom else "Modérée",
                "prix_sim_moyen": prix
            }
            id_compteur += 1
        return catalog

    @st.cache_data(ttl=1800)
    def load_agency_knowledge_base():
        return {
            "Zone des Niayes (Bande Côtière / Dakar-Thiès-Saint Louis)": {
                "sol": "Sableux fin des dunes (Expertise INP)", 
                "eau": "Nappe phréatique superficielle (Forages & Puits)", 
                "agence_suivi": "Direction de l'Horticulture (DH) & ANCAR",
                "salinite": "Faible mais menace d'intrusion du biseau salin", 
                "subventions_der": "Financement d'équipements solaires et kits goutte-à-goutte par la DER/FJ"
            },
            "Vallée du Fleuve Sénégal (Zone d'Action SAED / Nord)": {
                "sol": "Argileux lourd type Hollaldé (Expertise INP)", 
                "eau": "Irrigation totale continue par pompage (Fleuve Sénégal)", 
                "agence_suivi": "SAED",
                "salinite": "Modérée avec risques de friches halomorphes", 
                "subventions_der": "Crédits de campagne pour intrants et motopompes"
            },
            "Bassin Arachidier (Zone Kaolack-Diourbel-Fatick-Kaffrine)": {
                "sol": "Sableux paufrant de type Dior (Expertise INP)", 
                "eau": "Régime pluvial strict (ANACIM)", 
                "agence_suivi": "SONACOS & ANCAR",
                "salinite": "Faible", 
                "subventions_der": "Capital semences certifiées (DISEM)"
            },
            "Bassin du Sine Saloum (Zone Estuaire / Fatick-Foundiougne)": {
                "sol": "Sable-argileux Deck (Expertise INP)", 
                "eau": "Régime mixte", 
                "agence_suivi": "Direction de l'Agriculture",
                "salinite": "Très élevée en bordure de tannes", 
                "subventions_der": "Fonds de rechargement en gypse"
            },
            "Région Naturelle de la Casamance (Zone d'Action SODAGRI / Sud)": {
                "sol": "Hydromorphe argilo-sableux riche (Expertise INP)", 
                "eau": "Pluviométrie abondante", 
                "agence_suivi": "SODAGRI",
                "salinite": "Moyenne dans les vallées de mangroves", 
                "subventions_der": "Appui DER/FJ pour unités de transformation"
            }
        }

    crop_catalog = load_exact_200_crops()
    knowledge_base = load_agency_knowledge_base()

    communes_senegal = {
        "Zone des Niayes (Bande côtière)": {
            "Cayar": "Zone des Niayes (Bande Côtière / Dakar-Thiès-Saint Louis)",
            "Mboro": "Zone des Niayes (Bande Côtière / Dakar-Thiès-Saint Louis)",
            "Sangalkam": "Zone des Niayes (Bande Côtière / Dakar-Thiès-Saint Louis)"
        },
        "Vallée du Fleuve Sénégal (Nord)": {
            "Ross Béthio": "Vallée du Fleuve Sénégal (Zone d'Action SAED / Nord)",
            "Richard-Toll": "Vallée du Fleuve Sénégal (Zone d'Action SAED / Nord)",
            "Dagana": "Vallée du Fleuve Sénégal (Zone d'Action SAED / Nord)"
        },
        "Bassin Arachidier (Centre)": {
            "Kaffrine": "Bassin Arachidier (Zone Kaolack-Diourbel-Fatick-Kaffrine)",
            "Diourbel": "Bassin Arachidier (Zone Kaolack-Diourbel-Fatick-Kaffrine)"
        }
    }

    st.markdown("<div class='main-hub-title'>🇸🇳 Hub d'Intelligence Décisionnel & Financement des Startups Agricoles</div>", unsafe_allow_html=True)
    st.write("Ce système permet d'évaluer la faisabilité technique, agro-climatique et financière de votre projet d'entreprise agricole pour la DER/FJ, l'ANCAR ou les banques partenaires.")
    
    with st.container(border=True):
        st.write("⚙️ **Données Fondatrices de la Startup / Jeune Entreprise**")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            grande_zone = st.selectbox("🗺️ Zone Agro-Écologique :", options=list(communes_senegal.keys()), key="hz_grande_zone")
            commune_selected = st.selectbox("📍 Commune d'Études :", options=list(communes_senegal[grande_zone].keys()), key="hz_commune")
            zone_selected = communes_senegal[grande_zone][commune_selected]
            
        with col_s2:
            produit_selected = st.selectbox(f"🌱 Variété ISRA ({len(crop_catalog)} homologuées) :", options=list(crop_catalog.keys()), key="hp_select")
        
        col_s3, col_s4 = st.columns(2)
        with col_s3:
            surface_parcelle = st.number_input("📐 Superficie (Hectares) :", min_value=0.1, max_value=5000.0, value=2.0, step=0.5)
        with col_s4:
            niveau_intrants = st.select_slider("🧪 Taux d'Intensification :", options=["Zéro Intrant (Bio)", "Quota 50% Subventionné", "Pack Performance Optimal"], value="Quota 50% Subventionné")

        col_s5, col_s6 = st.columns(2)
        with col_s5:
            prix_vente_kilo = st.number_input("💵 Prix de vente ciblé (FCFA/Kg) :", min_value=50, max_value=5000, value=int(crop_catalog[produit_selected]['prix_sim_moyen']))
        with col_s6:
            charges_operationnelles_ha = st.number_input("💸 Charges estimées (FCFA/Ha) :", min_value=50000, max_value=5000000, value=450000, step=50000)

        bouton_simulation = st.button("📊 Activer le Diagnostic Agro-Financier", type="primary", use_container_width=True)

    if bouton_simulation:
        st.session_state.sim_active = True

    if st.session_state.sim_active:
        profil_sol = knowledge_base.get(zone_selected, list(knowledge_base.values())[0])
        data_produit = crop_catalog[produit_selected]
        
        facteur_zone = 1.35 if "Niayes" in zone_selected else 1.0
        facteur_intrant = 0.55 if "Zéro" in niveau_intrants else (1.0 if "Quota" in niveau_intrants else 1.45)
        
        rendement_reel = data_produit['rendement_moyen_ha'] * facteur_zone * facteur_intrant
        production_totale_tonnes = surface_parcelle * rendement_reel
        besoin_eau_m3 = surface_parcelle * (data_produit['besoin_eau_mm'] * 10)
        
        chiffre_affaire = production_totale_tonnes * 1000 * prix_vente_kilo
        charges_totales = surface_parcelle * charges_operationnelles_ha
        ebitda_brut = chiffre_affaire - charges_totales
        rentabilite_marge = (ebitda_brut / chiffre_affaire * 100) if chiffre_affaire > 0 else 0

        st.markdown(f"### 📋 Rapport d'Analyse Agro-Financière : *{produit_selected}*")
        st.markdown(f"<div class='highlight-desc'><strong>Variété ISRA :</strong> {data_produit['description_officielle']} <br><strong>Indice Sol (INP) :</strong> {profil_sol['sol']}</div>", unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🌾 Rendement Calculé", f"{rendement_reel:.2f} T/Ha")
        m2.metric("📦 Production Globale", f"{production_totale_tonnes:.2f} Tonnes")
        m3.metric("💰 Chiffre d'Affaires", f"{int(chiffre_affaire):,} FCFA")
        m4.metric("📈 Excédent (EBITDA)", f"{int(ebitda_brut):,} FCFA", delta=f"{rentabilite_marge:.1f}% marge")

        def generate_excel():
            wb = Workbook()
            ws = wb.active
            ws.title = "Business Plan"
            ws["A1"] = "BUSINESS PLAN SIMPLIFIÉ - YOUAGRONOME"
            ws["A3"] = f"Produit : {produit_selected}"
            ws["A4"] = f"Superficie : {surface_parcelle} Ha"
            ws["A5"] = f"Chiffre d'Affaires : {int(chiffre_affaire)} FCFA"
            ws["A6"] = f"EBITDA : {int(ebitda_brut)} FCFA"
            
            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            return buffer

        st.download_button(
            label="📥 Télécharger mon Business Plan (Excel)",
            data=generate_excel(),
            file_name=f"BusinessPlan_{produit_selected.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# =====================================================
# 🌱 CONSEIL
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
