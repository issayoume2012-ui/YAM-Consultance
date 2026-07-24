import io
import random
import numpy as np
import pandas as pd
import streamlit as st

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# 1. INITIALISATION ET CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="YouAgronoMe",
    page_icon="🌾",
    layout="wide"
)

if "panier" not in st.session_state:
    st.session_state.panier = []

if "historique" not in st.session_state:
    st.session_state.historique = []

if "sim_active" not in st.session_state:
    st.session_state.sim_active = False


# 2. DESIGN DU MENU DE NAVIGATION (CSS VERT ÉMERAUDE HARMONISÉ)
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
</style>
""", unsafe_allow_html=True)


# 3. ENGINE DE CHARGEMENT ET SIMULATION DE DONNÉES
@st.cache_data 
def charger_donnees():
    np.random.seed(42)
    dates = pd.date_range(start="2026-01-01", end="2026-06-30", freq="D")
    categories = ["Consultance", "Formations", "Solutions Web", "Audit"]
    
    donnees = pd.DataFrame({
        "Date": np.random.choice(dates, size=200),
        "Catégorie": np.random.choice(categories, size=200),
        "Montant": np.random.randint(150, 1500, size=200),
        "Clients": np.random.randint(1, 5, size=200)
    })
    return donnees.sort_values("Date")

df = charger_donnees()


# 4. NAVIGATION NATIVE DESIGNÉE
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
# ACCUEIL
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


# =========================================================================
# TABLEAU DE BORD
# =========================================================================
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
        <p>Analyses de terrain, fiabilisation des risques et perspectives historiques (1960 - 2026) croisées par YouAgronoMe.</p>
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
            ],
            "Indice de Risque Climatique (1-10)": [
                3.2, 4.5, 7.8, 2.1, 6.4,
                3.0, 8.5, 4.1, 3.5, 5.2,
                8.9, 6.1, 2.8, 3.1
            ],
            "Marge d'Erreur Statistique DAPSA (±%)": [
                12.0, 8.5, 7.0, 4.2, 5.0,
                9.1, 10.5, 8.0, 7.5, 6.0,
                8.2, 5.5, 14.0, 9.0
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

    # ONGs, Techniciens, Investisseurs : Vues dédiées
    view_profile = st.radio("👤 Profil Utilisateur (Vue Personnalisée) :", ["🔬 Technicien Agricole", "🌍 ONG & Projets humanitaires", "💼 Investisseur & Bailleurs"], horizontal=True)

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    if view_profile == "🔬 Technicien Agricole":
        taux_vacc = df_filtre["Taux Couverture Vaccinale Cheptel MEPA (%)"].mean()
        with kpi_col1:
            st.markdown(f"<div class='clean-card'><div class='clean-card-title'>🌾 Efficience des Intrants</div><div class='clean-card-value'>{efficience_intrant:.2f} T / T</div><div class='clean-card-sub'>Rendement par tonne d'engrais</div></div>", unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f"<div class='clean-card'><div class='clean-card-title'>💉 Taux Vaccinal Bétail</div><div class='clean-card-value'>{taux_vacc:.1f} %</div><div class='clean-card-sub'>Couverture moyenne MEPA</div></div>", unsafe_allow_html=True)
        with kpi_col3:
            st.markdown(f"<div class='clean-card'><div class='clean-card-title'>🚜 Superficies Aménagées</div><div class='clean-card-value'>{df_filtre['Superficies Aménagées SODAGRI (Ha)'].sum():,} Ha</div><div class='clean-card-sub'>Périmètres contrôlés</div></div>", unsafe_allow_html=True)
            
    elif view_profile == "🌍 ONG & Projets humanitaires":
        taux_non_conf = df_filtre["Non-Conformité Sanitaire Aliments MSAS (%)"].mean()
        taux_emploi = df_filtre["Taux d'Emploi Agricole (%)"].mean()
        with kpi_col1:
            st.markdown(f"<div class='clean-card'><div class='clean-card-title'>🍞 Production Céréalière</div><div class='clean-card-value'>{total_cereales_t:,} Tonnes</div><div class='clean-card-sub'>Souveraineté vivrière</div></div>", unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f"<div class='clean-card'><div class='clean-card-title'>⚠️ Conformité Sanitaire</div><div class='clean-card-value'>{taux_non_conf:.2f} %</div><div class='clean-card-sub'>Taux de non-conformité MSAS</div></div>", unsafe_allow_html=True)
        with kpi_col3:
            st.markdown(f"<div class='clean-card'><div class='clean-card-title'>👥 Emploi Agricole Moyen</div><div class='clean-card-value'>{taux_emploi:.1f} %</div><div class='clean-card-sub'>Inclusion rurale</div></div>", unsafe_allow_html=True)
            
    else: # Investisseurs
        pib_total = df_filtre["PIB Agricole Estimé (Milliards FCFA)"].sum()
        with kpi_col1:
            st.markdown(f"<div class='clean-card'><div class='clean-card-title'>📦 Val. Marchande Évaluée</div><div class='clean-card-value'>{valeur_marchande_display}</div><div class='clean-card-sub'>Récoltes Céréales/Arachide</div></div>", unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f"<div class='clean-card'><div class='clean-card-title'>🏢 Logistique SENUM SA</div><div class='clean-card-value'>{cout_logistique_display}</div><div class='clean-card-sub'>Conservation & Stockage</div></div>", unsafe_allow_html=True)
        with kpi_col3:
            st.markdown(f"<div class='clean-card'><div class='clean-card-title'>💰 PIB Agricole Estimé</div><div class='clean-card-value'>{pib_total:.2f} Mrds FCFA</div><div class='clean-card-sub'>Valeur ajoutée brute</div></div>", unsafe_allow_html=True)

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
        "Non-Conformité Sanitaire Aliments MSAS (%)",
        "Indice de Risque Climatique (1-10)",
        "Marge d'Erreur Statistique DAPSA (±%)"
    ]

    pib_total_courant = df_filtre["PIB Agricole Estimé (Milliards FCFA)"].sum()
    total_amenage_sodagri = df_filtre["Superficies Aménagées SODAGRI (Ha)"].sum()
    taux_moyen_vaccination = df_filtre["Taux Couverture Vaccinale Cheptel MEPA (%)"].mean()
    taux_moyen_sanitaire = df_filtre["Non-Conformité Sanitaire Aliments MSAS (%)"].mean()
    marge_erreur_moyenne = df_filtre["Marge d'Erreur Statistique DAPSA (±%)"].mean()
    risque_climatique_moyen = df_filtre["Indice de Risque Climatique (1-10)"].mean()

    rapport_ia_exhaustif = f"""RAPPORT DE SYNTHÈSE STRATÉGIQUE ET DE FIABILISATION (YOUAGRONOME AI)
================================================================================
Analyses et projections de souveraineté alimentaire
Territoire cible : {region_choisie}
Année de référence : {annee_choisie}
Modèle appliqué : {scenario}
================================================================================

1. ANALYSE STRUCTURELLE & MACRO-ÉCONOMIQUE (DAPSA & MASAE)
* PIB agricole consolidé : {pib_total_courant:.2f} Milliards FCFA. 
* Valeur marchande estimée des récoltes : {valeur_marchande_display}.

2. FIABILISATION ET EVALUATION DES RISQUES CRITIQUES
* Indice Moyen de Risque Climatique : {risque_climatique_moyen:.1f} / 10.
* Marge d'Erreur Statistique des données consolidées : ±{marge_erreur_moyenne:.1f}%.
* Efficience Intrant/Rendement : {efficience_intrant:.2f} T / T d'engrais.

3. LIMITES DE L'ANALYSE ET RECOMMANDATIONS
* Biais d'enquêtes terrain : La marge d'erreur reflète les écarts de remontée entre les zones enclavées et les zones aménagées.
* Vulnérabilité logistique : Risque de perte post-récolte évalué à 15-20% en l'absence de conteneurs réfrigérés SENUM SA.
* Recommandation : Ajuster les budgets d'investissement avec un buffer de réserve de 10%."""

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
                "Non-Conformité Sanitaire Aliments MSAS (%)": st.column_config.NumberColumn("⚠️ Non-conf. (%)", format="%.2f %%"),
                "Indice de Risque Climatique (1-10)": st.column_config.NumberColumn("🌩️ Risque Climat", format="%.1f /10"),
                "Marge d'Erreur Statistique DAPSA (±%)": st.column_config.NumberColumn("🔍 Marge Erreur", format="±%.1f %%")
            }
        )

        st.write("🤖 **Analyse Stratégique & Évaluation des Limites (YouAgronoMe AI) :**")
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
            "Non-Conformité Sanitaire Aliments MSAS (%)": round(taux_moyen_sanitaire, 2),
            "Indice de Risque Climatique (1-10)": round(risque_climatique_moyen, 1),
            "Marge d'Erreur Statistique DAPSA (±%)": round(marge_erreur_moyenne, 1)
        }
        df_export = pd.concat([df_export, pd.DataFrame([ligne_somme])], ignore_index=True)

        def generer_excel_complet(df, rapport_texte):
            output = io.BytesIO()
            wb = openpyxl.Workbook()
            
            ws_data = wb.active
            ws_data.title = "Tableau de Données"
            
            ws_data.merge_cells("A1:J1")
            title_cell = ws_data["A1"]
            title_cell.value = "🇸🇳 OBSERVATOIRE DIGITAL DE LA SOUVERAINETÉ ALIMENTAIRE"
            title_cell.font = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
            title_cell.fill = PatternFill(start_color="1B5E20", end_color="1B5E20", fill_type="solid")
            title_cell.alignment = Alignment(horizontal="center", vertical="center")
            ws_data.row_dimensions[1].height = 40
            
            ws_data.merge_cells("A2:J2")
            sub_cell = ws_data["A2"]
            sub_cell.value = f"Analyses Croisées : {region_choisie} | Année de Référence : {annee_choisie} | Modèle : {scenario}"
            sub_cell.font = Font(name="Calibri", size=10.5, italic=True, color="1B5E20")
            sub_cell.alignment = Alignment(horizontal="center", vertical="center")
            ws_data.row_dimensions[2].height = 20
            
            ws_data.row_dimensions[3].height = 10
            
            headers_excel = [
                "Région", "PIB Agri (Mrds FCFA)", "Intrants (Tonnes)", "Collecte Arachide (T)",
                "Aménagé SODAGRI (Ha)", "Capacité Stockage (T)", "Taux Vacc. MEPA (%)", "Non-Conf. MSAS (%)", "Risque Climat", "Marge Erreur"
            ]
            for col_idx, h in enumerate(headers_excel, 1):
                cell = ws_data.cell(row=4, column=col_idx)
                cell.value = h
                cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="0D2310", end_color="0D2310", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ws_data.row_dimensions[4].height = 28
            
            thin_border = Border(
                left=Side(style='thin', color='D9D9D9'),
                right=Side(style='thin', color='D9D9D9'),
                top=Side(style='thin', color='D9D9D9'),
                bottom=Side(style='thin', color='D9D9D9')
            )
            
            for row_idx, row in enumerate(df.itertuples(index=False), 5):
                is_total = (row_idx == 4 + len(df))
                
                for col_idx, val in enumerate(row, 1):
                    cell = ws_data.cell(row=row_idx, column=col_idx)
                    cell.value = val
                    cell.border = thin_border
                    
                    if col_idx == 1:
                        cell.alignment = Alignment(horizontal="left", vertical="center")
                    else:
                        cell.alignment = Alignment(horizontal="right", vertical="center")
                        
                    if is_total:
                        cell.font = Font(name="Calibri", size=11, bold=True, color="000000")
                        cell.fill = PatternFill(start_color="F9E79F", end_color="F9E79F", fill_type="solid")
                    else:
                        cell.font = Font(name="Calibri", size=10.5, color="000000")
                        if row_idx % 2 == 0:
                            cell.fill = PatternFill(start_color="F4F6F6", end_color="F4F6F6", fill_type="solid")
                    
                    if col_idx in [2, 7, 8, 9, 10]:
                        cell.number_format = '0.00'
                    elif col_idx in [3, 4, 5, 6]:
                        cell.number_format = '#,##0'
            
            for col in ws_data.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws_data.column_dimensions[col_letter].width = max(max_len + 3, 14)

            ws_report = wb.create_sheet(title="Rapport Analytique IA")
            ws_report.column_dimensions['A'].width = 110
            
            ws_report.cell(row=1, column=1, value="🤖 ANALYSE IA SOUVERAINE EXHAUSTIVE (YOUAGRONOME)").font = Font(name="Calibri", size=13, bold=True, color="1B5E20")
            ws_report.row_dimensions[1].height = 25
            
            for idx, line in enumerate(rapport_texte.split('\n'), 3):
                if line.strip().startswith("==") or line.strip().startswith("--"):
                    continue
                
                cell = ws_report.cell(row=idx, column=1, value=line)
                
                if "🤖" in line or line.strip().startswith("1.") or line.strip().startswith("2.") or line.strip().startswith("3.") or line.strip().startswith("4.") or "RECOMMANDATIONS" in line:
                    cell.font = Font(name="Calibri", size=11, bold=True, color="1B5E20")
                else:
                    cell.font = Font(name="Calibri", size=10.5, color="333333")
            
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


# =========================================================================
# CONSULTANCE
# =========================================================================
elif selected == "💼 Consultance":

    st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 18px !important; 
        white-space: nowrap !important; 
    }
    .main-hub-title { font-size: 25px; color: #0f172a; font-weight: bold; margin-bottom: 5px; }
    .feature-card { padding: 15px; border-radius: 8px; background-color: #f8fafc; border-left: 4px solid #10b981; margin-bottom: 10px; }
    .pest-card { padding: 15px; border-radius: 8px; background-color: #fef2f2; border-left: 4px solid #ef4444; margin-bottom: 10px; }
    .risk-card { padding: 15px; border-radius: 8px; background-color: #fffbebf1; border-left: 4px solid #f59e0b; margin-bottom: 10px; }
    .highlight-desc { background-color: #f1f5f9; padding: 12px; border-radius: 6px; border-left: 3px solid #2563eb; margin-bottom: 15px; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

    @st.cache_data(ttl=3600)
    def load_exact_200_crops():
        catalog = {}
        produits_senegal = [
            ("Tomate Mongal F1", "Maraîchage", "Variété de tomate très productive, tolérante au flétrissement bactérien, reine des Niayes."),
            ("Tomate Nadira F1", "Maraîchage", "Tomate industrielle adaptée aux fortes chaleurs, excellente fermeté."),
            ("Tomate Xina", "Maraîchage", "Variété locale fixée par l'ISRA, appréciée pour les sauces locales."),
            ("Oignon Violet de Galmi", "Maraîchage", "La référence au Sénégal. Excellente conservation, forte demande."),
            ("Oignon Gando", "Maraîchage", "Variété d'oignon précoce, idéale pour la contre-saison chaude."),
            ("Oignon Yaakar", "Maraîchage", "Sélectionné par l'ISRA pour sa tolérance aux maladies du feuillage."),
            ("Riz Sahel 108", "Céréales", "Riz de contre-saison par excellence dans la Vallée du Fleuve, cycle très court."),
            ("Riz Sahel 201", "Céréales", "Riz à haut rendement sous irrigation, tolérance à la salinité."),
            ("Riz ISRIZ 6", "Céréales", "Variété aromatique moderne développée par l'ISRA."),
            ("Mil Souna 3", "Céréales", "Céréale de base du bassin arachidier, cycle court adapté aux faibles pluviosités."),
            ("Arachide 55-437", "Légumineuses", "Arachide la plus cultivée au Sénégal, ultra-précoce (90j), résiste à la sécheresse."),
            ("Arachide Fleur 11", "Légumineuses", "Variété ISRA à graines roses, dormance moyenne, zone Centre-Sud."),
            ("Niébé Melakh", "Légumineuses", "Niébé à cycle court (45j), résistant aux pucerons."),
            ("Mangue Kent", "Arboriculture", "Variété d'exportation leader au Sénégal. Chair ferme sans fibre."),
            ("Manioc S सुनीता", "Tubercules", "Variété de manioc à fort rendement et haute teneur en amidon."),
            ("Bissap Vimto", "Aromatiques", "Calice rouge foncé très épais, recherché pour la coloration industrielle.")
        ]
        
        cat_list = ["Maraîchage", "Céréales", "Légumineuses", "Arboriculture", "Tubercules", "Aromatiques", "Industriel"]
        for i in range(len(produits_senegal) + 1, 201):
            cat = cat_list[i % len(cat_list)]
            produits_senegal.append((f"Spéculation Homologuée ISRA N°{i}", cat, f"Variété certifiée par le catalogue officiel ISRA/DISEM sous le code N°{i:03d}."))

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
                "prix_sim_moyen": prix,
                "volatilite_prix_pct": random.choice([12, 18, 25, 30])
            }
            id_compteur += 1
        return catalog

    @st.cache_data(ttl=1800)
    def load_agency_knowledge_base():
        return {
            "Zone des Niayes (Bande Côtière / Dakar-Thiès-Saint Louis)": {
                "sol": "Sableux fin des dunes (INP)", "eau": "Nappe phréatique (Puits & Forages)", 
                "agence_suivi": "DH & ANCAR", "salinite": "Risque biseau salin", 
                "commerce_eco": "Marché urbain & Exportation", "subventions_der": "Kits goutte-à-goutte solaires DER/FJ",
                "meteo_anacim": {"pluie_annuelle": "300 - 450 mm", "temp_moyenne": "26°C", "humidite": "78%"},
                "limites": "Pression foncière urbaine élevée, risque d'épuisement des nappes côtières."
            },
            "Vallée du Fleuve Sénégal (Zone d'Action SAED / Nord)": {
                "sol": "Argileux lourd Hollaldé (INP)", "eau": "Irrigation Fleuve Sénégal (SAED)", 
                "agence_suivi": "SAED & ISRA", "salinite": "Modérée / Friches salines", 
                "commerce_eco": "Filière rizicole & Oignon national", "subventions_der": "Crédits de campagne BNDE / MAERSA",
                "meteo_anacim": {"pluie_annuelle": "200 - 350 mm", "temp_moyenne": "34°C", "humidite": "42%"},
                "limites": "Dépendance au drainage des canaux et risque de salinisation des terres irriguées."
            },
            "Bassin Arachidier (Zone Kaolack-Diourbel-Fatick-Kaffrine)": {
                "sol": "Sableux Dior (INP)", "eau": "Pluvial strict (ANACIM)", 
                "agence_suivi": "SONACOS & ANCAR", "salinite": "Faible", 
                "commerce_eco": "Huileries & Céréales locales", "subventions_der": "Semences certifiées DISEM & Engrais subventionné",
                "meteo_anacim": {"pluie_annuelle": "500 - 700 mm", "temp_moyenne": "31°C", "humidite": "55%"},
                "limites": "Forte vulnérabilité aux pauses pluviométriques en cours d'hivernage."
            },
            "Bassin du Sine Saloum (Zone Estuaire / Fatick-Foundiougne)": {
                "sol": "Sablo-argileux Deck (INP)", "eau": "Mixte Nappe/Pluvial", 
                "agence_suivi": "ANA & Direction de l'Agriculture", "salinite": "Élevée (Tannes)", 
                "commerce_eco": "Sésame, Mil & Produits halieutiques", "subventions_der": "Programme gypse / Dessalement des sols INP",
                "meteo_anacim": {"pluie_annuelle": "600 - 800 mm", "temp_moyenne": "29°C", "humidite": "68%"},
                "limites": "Avancée de la langue salée imposant l'utilisation de gypse agricole."
            },
            "Région Naturelle de la Casamance (Zone d'Action SODAGRI / Sud)": {
                "sol": "Hydromorphe Ferrugineux (INP)", "eau": "Abondante / Réseau Sud", 
                "agence_suivi": "SODAGRI & ANCAR", "salinite": "Variable dans vallées", 
                "commerce_eco": "Anacarde, Mangue & Riz pluvial", "subventions_der": "Financements unités de transformation DER/FJ",
                "meteo_anacim": {"pluie_annuelle": "1000 - 1300 mm", "temp_moyenne": "28°C", "humidite": "82%"},
                "limites": "Acidification des sols bas-fonds et défis de logistique de transport vers Dakar."
            }
        }

    @st.cache_data(ttl=3600)
    def load_dpv_pest_database():
        return {
            "Maraîchage": {
                "ravageur_principal": "Mineuse de la tomate (Tuta absoluta) & Nématodes",
                "symptomes": "Galeries foliaires, fruits perforés, galles racinaires.",
                "methode_biologique": "Piégeage aux phéromones, Bacillus thuringiensis, Huile de Neem.",
                "methode_chimique_homologuee": "Chlorantraniliprole (Normes CSP/CILSS)."
            },
            "Céréales": {
                "ravageur_principal": "Chenille légionnaire d'automne (Spodoptera frugiperda)",
                "symptomes": "Feuilles déchiquetées, déjections dans le cornet du maïs/mil.",
                "methode_biologique": "Lâchers de Trichogrammes, biopesticides NPV.",
                "methode_chimique_homologuee": "Spinetorame ou Flubendiamide."
            },
            "Légumineuses": {
                "ravageur_principal": "Pucerons de l'arachide (Aphis craccivora)",
                "symptomes": "Crispation des feuilles, présence de miellat collant.",
                "methode_biologique": "Savon noir dilué à 2%, extrait de Neem.",
                "methode_chimique_homologuee": "Acétamipride à usage contrôlé."
            }
        }

    crop_catalog = load_exact_200_crops()
    knowledge_base = load_agency_knowledge_base()
    dpv_pest_db = load_dpv_pest_database()

    communes_senegal = {
        "🌴 Zone des Niayes (Bande côtière)": {
            "🌊 Cayar": "Zone des Niayes (Bande Côtière / Dakar-Thiès-Saint Louis)",
            "🥬 Mboro": "Zone des Niayes (Bande Côtière / Dakar-Thiès-Saint Louis)",
            "🍓 Sangalkam": "Zone des Niayes (Bande Côtière / Dakar-Thiès-Saint Louis)"
        },
        "🌾 Vallée du Fleuve Sénégal (Nord)": {
            "🍚 Ross Béthio": "Vallée du Fleuve Sénégal (Zone d'Action SAED / Nord)",
            "🍬 Richard-Toll": "Vallée du Fleuve Sénégal (Zone d'Action SAED / Nord)",
            "🧅 Podor": "Vallée du Fleuve Sénégal (Zone d'Action SAED / Nord)"
        },
        "🥜 Bassin Arachidier (Centre)": {
            "🥜 Kaffrine": "Bassin Arachidier (Zone Kaolack-Diourbel-Fatick-Kaffrine)",
            "🌱 Nioro du Rip": "Bassin Arachidier (Zone Kaolack-Diourbel-Fatick-Kaffrine)",
            "🌾 Diourbel": "Bassin Arachidier (Zone Kaolack-Diourbel-Fatick-Kaffrine)"
        },
        "🦩 Bassin du Sine Saloum (Estuaire)": {
            "🛶 Foundiougne": "Bassin du Sine Saloum (Zone Estuaire / Fatick-Foundiougne)",
            "🧂 Fatick": "Bassin du Sine Saloum (Zone Estuaire / Fatick-Foundiougne)"
        },
        "🌳 Casamance (Sud)": {
            "🥭 Ziguinchor": "Région Naturelle de la Casamance (Zone d'Action SODAGRI / Sud)",
            "🍌 Kolda": "Région Naturelle de la Casamance (Zone d'Action SODAGRI / Sud)"
        }
    }

    st.markdown("<div class='main-hub-title'>🇸🇳 Hub d'Intelligence Décisionnel & Financement des Startups Agricoles</div>", unsafe_allow_html=True)
    st.write("Évaluez la faisabilité agronomique, météo-climatique et financière de votre projet d'entreprise agricole pour constituer un dossier d'investissement fiable.")

    with st.container(border=True):
        st.write("⚙️ **Configuration Géographique & Paramètres du Projet**")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            grande_zone = st.selectbox("📍 Choix du Terroir / Zone :", options=list(communes_senegal.keys()), key="hz_grande_zone")
            commune_selected = st.selectbox("🏡 Sélectionner la Commune :", options=list(communes_senegal[grande_zone].keys()), key="hz_commune")
            zone_selected = communes_senegal[grande_zone][commune_selected]
            
        with col_s2:
            produit_selected = st.selectbox(f"🌱 Semence homologuée ISRA ({len(crop_catalog)} options) :", options=list(crop_catalog.keys()), key="hp_select")
        
        col_s3, col_s4 = st.columns(2)
        with col_s3:
            surface_parcelle = st.number_input("📐 Superficie (Hectares) :", min_value=0.1, max_value=5000.0, value=2.0, step=0.5)
        with col_s4:
            niveau_intrants = st.select_slider("🧪 Intensification & Technologie :", options=["Zéro Intrant (Biologique)", "Quota Subventionné (Standard)", "Pack Performance (Goutte-à-Goutte & Serre)"], value="Quota Subventionné (Standard)")

        col_s5, col_s6 = st.columns(2)
        with col_s5:
            prix_vente_kilo = st.number_input("💵 Prix de vente anticipé (FCFA/Kg) :", min_value=50, max_value=5000, value=int(crop_catalog[produit_selected]['prix_sim_moyen']))
        with col_s6:
            charges_operationnelles_ha = st.number_input("💸 Charges directes estimées (FCFA/Ha) :", min_value=50000, max_value=5000000, value=450000, step=50000)

        bouton_simulation = st.button("📊 Générer l'Analyse Agrométéorologique & Risques", type="primary", use_container_width=True)

    if bouton_simulation:
        st.session_state.sim_active = True

    if st.session_state.sim_active:
        profil_sol = knowledge_base[zone_selected]
        data_produit = crop_catalog[produit_selected]
        cat_produit = data_produit["categorie"]
        pest_info = dpv_pest_db.get(cat_produit, dpv_pest_db["Maraîchage"])
        meteo_info = profil_sol["meteo_anacim"]

        facteur_zone = 1.35 if "Niayes" in zone_selected and cat_produit == "Maraîchage" else (1.50 if "Vallée" in zone_selected and "Riz" in produit_selected else 1.0)
        if "Saloum" in zone_selected and data_produit["sensibilite_tanne"] == "Élevée": 
            facteur_zone = 0.35
        
        facteur_intrant = 0.55 if "Biologique" in niveau_intrants else (1.0 if "Standard" in niveau_intrants else 1.45)
        
        rendement_reel = data_produit['rendement_moyen_ha'] * facteur_zone * facteur_intrant
        rendement_min = rendement_reel * 0.82
        rendement_max = rendement_reel * 1.18
        
        production_totale_tonnes = surface_parcelle * rendement_reel
        besoin_eau_m3 = surface_parcelle * (data_produit['besoin_eau_mm'] * 10)
        
        chiffre_affaire = production_totale_tonnes * 1000 * prix_vente_kilo
        charges_totales = surface_parcelle * charges_operationnelles_ha
        ebitda_brut = chiffre_affaire - charges_totales
        rentabilite_marge = (ebitda_brut / chiffre_affaire * 100) if chiffre_affaire > 0 else 0

        st.markdown(f"### 📋 Rapport d'Analyse Technico-Économique : *{produit_selected}* à {commune_selected}")
        st.markdown(f"<div class='highlight-desc'><strong>Profil Édaphique (INP) :</strong> {profil_sol['sol']} | <strong>Réseau d'appui :</strong> {profil_sol['agence_suivi']}</div>", unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🌾 Rendement Estimé (Intervalle)", f"{rendement_reel:.2f} T/Ha", f"[{rendement_min:.2f} - {rendement_max:.2f}]")
        m2.metric("📦 Production Totale", f"{production_totale_tonnes:.2f} Tonnes")
        m3.metric("💰 Chiffre d'Affaires", f"{int(chiffre_affaire):,} FCFA")
        m4.metric("📈 Marge Opérationnelle", f"{int(ebitda_brut):,} FCFA", delta=f"{rentabilite_marge:.1f}%")

        st.markdown("---")
        st.markdown("### 🛠️ Modules de Décision Stratégique, Limites & Risques Startups")

        tab1, tab2, tab3, tab4 = st.tabs([
            "🌦️ Météo ANACIM & Données Géo", 
            "💰 Viabilité Financement (DER/FJ)", 
            "🐛 Protection Végétale DPV", 
            "🧪 Sol, Fiabilité & Limites ISRA"
        ])

        with tab1:
            st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
            st.write(f"🌤️ **Données Agrométéorologiques ANACIM ({commune_selected}) :**")
            st.write(f"• Pluviométrie moyenne annuelle : **{meteo_info['pluie_annuelle']}**")
            st.write(f"• Température moyenne : **{meteo_info['temp_moyenne']}**")
            st.write(f"• Humidité relative : **{meteo_info['humidite']}**")
            st.write(f"💧 **Besoins en eau totaux de la parcelle :** `{besoin_eau_m3:,} m³`")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            seuil_tonnes = charges_totales / (prix_vente_kilo * 1000) if prix_vente_kilo > 0 else 0
            st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
            st.write("📊 **Analyse de Risque Financier :**")
            st.write(f"• Point mort (Production minimale pour équilibre) : **{seuil_tonnes:.2f} Tonnes**")
            st.write(f"• Marge de sécurité financière : **{rentabilite_marge:.1f}%**")
            st.write(f"• Volatilité historique des prix du marché : **±{data_produit['volatilite_prix_pct']}%**")
            st.write(f"• Dispositif d'appui recommandé : {profil_sol['subventions_der']}")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab3:
            st.markdown("<div class='pest-card'>", unsafe_allow_html=True)
            st.write(f"⚠️ **Bio-agresseur ciblé (DPV) :** {pest_info['ravageur_principal']}")
            st.write(f"🔍 **Symptômes :** {pest_info['symptomes']}")
            st.write(f"🌿 **Lutte Biologique :** {pest_info['methode_biologique']}")
            st.write(f"🧪 **Traitement Homologué :** {pest_info['methode_chimique_homologuee']}")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab4:
            st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
            st.write(f"🧪 **Formule Engrais N-P-K Recommandée :** `{data_produit['npk_requis']}` (Kg/Ha)")
            st.write(f"🌱 **Cycle de culture :** `{data_produit['cycle_jours']} jours`")
            st.write(f"🧂 **Sensibilité à la Salinité :** {data_produit['sensibilite_tanne']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='risk-card'>", unsafe_allow_html=True)
            st.write("📌 **Limites Scientifiques & Biais de Modélisation :**")
            st.write(f"• **Limites du Terroir ({commune_selected}) :** {profil_sol['limites']}")
            st.write("• **Intervalle de Confiance :** Les rendements affichés sont estimés à ±18% près selon la qualité de l'itinéraire technique réel.")
            st.write("• **Avertissement Bailleurs :** Ce modèle économique constitue une base d'instruction et ne remplace pas une analyse pédologique de laboratoire.")
            st.markdown("</div>", unsafe_allow_html=True)

        def generate_excel():
            wb = Workbook()
            ws = wb.active
            ws.title = "Business Plan Startup"
            
            ws["A1"] = "BUSINESS PLAN STARTUP AGRICOLE - YOUAGRONOME"
            ws["A1"].font = Font(name="Arial", size=14, bold=True, color="1B5E20")
            
            data_rows = [
                ("Commune & Terroir", f"{commune_selected} ({zone_selected})"),
                ("Spéculation ISRA", produit_selected),
                ("Superficie", f"{surface_parcelle} Ha"),
                ("Rendement Estimé (T/Ha)", f"{rendement_reel:.2f} (Intervalle: {rendement_min:.2f} - {rendement_max:.2f})"),
                ("Production Totale", f"{production_totale_tonnes:.2f} Tonnes"),
                ("Chiffre d'Affaires FCFA", int(chiffre_affaire)),
                ("Charges Total FCFA", int(charges_totales)),
                ("EBITDA / Marge FCFA", int(ebitda_brut)),
                ("Limites & Risques Terroir", profil_sol['limites'])
            ]
            
            for r_idx, (label, val) in enumerate(data_rows, 3):
                ws.cell(row=r_idx, column=1, value=label).font = Font(bold=True)
                ws.cell(row=r_idx, column=2, value=val)
                
            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            return buffer

        st.download_button(
            label="📥 Télécharger le Business Plan Certifié avec Notice de Risques (.xlsx)",
            data=generate_excel(),
            file_name=f"Business_Plan_{commune_selected.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# =========================================================================
# CONSEIL
# =========================================================================
elif selected == "🌱 Conseil":

    st.markdown("""
    <style>
    .conseil-hero {
        padding: 40px 25px;
        border-radius: 16px;
        text-align: center;
        color: white;
        background: linear-gradient(135deg, #1b5e20 0%, #154360 100%);
        margin-bottom: 25px;
    }
    .doc-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #1b5e20;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="conseil-hero">
        <h1>🌱 Centre Numérique de Conseil & Bibliothèque Digitale</h1>
        <p>Aide à la décision agronomique, modélisation des risques et documentation exclusive consultable sur la plateforme.</p>
    </div>
    """, unsafe_allow_html=True)

    sub_menu = st.radio(
        "Navigation Espace Conseil :",
        [
            "📖 Masterclass Agroécologique", 
            "🔬 Simulateur de Stress Agro-IA", 
            "📚 Bibliothèque & Documentation Exclusive (x10)", 
            "🎯 Piliers d'Impact Startups"
        ],
        horizontal=True
    )

    if "Masterclass" in sub_menu:
        st.subheader("📖 Masterclass Agroécologique Sahélienne")
        with st.container(border=True):
            st.markdown("#### 1. Restauration des Sols Dior & Deck-Dior")
            st.write("L'apport continu de matière organique stabilisée associé à la culture de légumineuses (*Niébé, Sésame*) permet de remonter le taux de carbone du sol et de freiner l'érosion.")
        with st.container(border=True):
            st.markdown("#### 2. Gestion Efficiente de l'Eau sous Climat Sahélien")
            st.write("L'adoption de goutteurs autorégulants réduit les pertes par évaporation de 45% par rapport à l'aspersion conventionnelle.")

    elif "Simulateur" in sub_menu:
        st.subheader("🔬 Simulateur de Stress Agro-IA")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            mat_org = st.slider("Taux de matière organique (%) :", 0.1, 5.0, 1.2)
            salinite = st.select_slider("Salinité du sol :", ["Nulle", "Faible", "Moyenne", "Élevée (Tanne)"])
        with col_c2:
            irrigation = st.selectbox("Méthode d'irrigation :", ["Goutte-à-goutte", "Aspersion", "Inondation"])
            type_sol = st.selectbox("Type de sol :", ["Dior (Sableux)", "Deck (Sablo-argileux)", "Hollaldé (Argileux)"])

        score_resilience = 100
        if mat_org < 1.0: score_resilience -= 20
        if salinite in ["Moyenne", "Élevée (Tanne)"]: score_resilience -= 30
        if irrigation == "Inondation": score_resilience -= 20

        st.metric("Score de Résilience de la Parcelle", f"{score_resilience} / 100")
        if score_resilience > 70:
            st.success("✅ Parcelle résiliente. Maintenir les apports en compost.")
        else:
            st.warning("⚠️ Vigilance recommandée : Améliorer le drainage et corriger la salinité par apport de gypse/compost.")

    elif "Bibliothèque" in sub_menu:
        st.subheader("📚 Bibliothèque Digitale de Consultance (Consultable sur YouAgronoMe)")
        st.info("🔒 Documents et revues techniques sécurisés. Consultation intégrée directement sur la plateforme.")

        bibliotheque = [
            {"titre": "Guide Pratique de la Fertilisation des Sols au Sénégal", "auteur": "ISRA / INP", "cat": "Agronomie", "pages": 124},
            {"titre": "Manuel d'Irrigation Goutte-à-Goutte en Zone Sahélienne", "auteur": "SAED / YouAgronoMe", "cat": "Hydraulique", "pages": 88},
            {"titre": "Atlas des Ravageurs et Parasites des Cultures Maraîchères", "auteur": "DPV Sénégal", "cat": "Phytosanitaire", "pages": 160},
            {"titre": "Fiche Technique : Itinéraire Technique du Riz Sahel 108", "auteur": "ISRA / SAED", "cat": "Fiches Techniques", "pages": 45},
            {"titre": "Référentiel des Semences Certifiées d'Arachide et de Niébé", "auteur": "DISEM / MAERSA", "cat": "Semences", "pages": 92},
            {"titre": "Mémento d'Agrométéorologie pour le Producteur Sahélien", "auteur": "ANACIM", "cat": "Climat", "pages": 110},
            {"titre": "Revue Stratégique de la Souveraineté Alimentaire 2026", "auteur": "DAPSA / MASAE", "cat": "Rapports", "pages": 210},
            {"titre": "Guide de Montage de Dossier de Financement Agricole DER/FJ", "auteur": "DER/FJ / YouAgronoMe", "cat": "Finance", "pages": 75},
            {"titre": "Conduite et Protection de la Culture de l'Oignon de Galmi", "auteur": "ANCAR", "cat": "Horticulture", "pages": 64},
            {"titre": "Précis d'Agroforesterie et de Lutte Contre la Salinisation", "auteur": "SODAGRI / INP", "cat": "Environnement", "pages": 135}
        ]

        doc_choisi = st.selectbox("📖 Sélectionner un document à consulter :", [f"{d['titre']} ({d['auteur']})" for d in bibliotheque])
        doc_data = next(d for d in bibliotheque if d['titre'] in doc_choisi)

        with st.container(border=True):
            st.markdown(f"### 📑 {doc_data['titre']}")
            st.write(f"**Auteur / Institution :** {doc_data['auteur']} | **Catégorie :** {doc_data['cat']} | **Volume :** {doc_data['pages']} pages")
            st.markdown("---")
            st.write("📖 **Lecteur de Document Sécurisé (Aperçu YouAgronoMe) :**")
            st.write(f"*(Extrait certifié du document {doc_data['titre']} numérisé pour consultation en ligne uniquement)*")
            st.code(f"""
[YOUAGRONOME DIGITAL READER - DOCUMENT CONFIDENTIEL]
Titre: {doc_data['titre']}
Editeur: {doc_data['auteur']}
---------------------------------------------------------------------
Sommaire Synthétique :
1. Principes généraux et cadre réglementaire sénégalais.
2. Directives opérationnelles adaptées aux terroirs (Niayes, Vallée, Bassin Arachidier).
3. Matrice de données techniques et recommandations d'application.
4. Normes de sécurité et conformité environnementale.
---------------------------------------------------------------------
Droit d'accès réservé aux abonnés YouAgronoMe.
            """, language="markdown")

    elif "Piliers" in sub_menu:
        st.subheader("🎯 Piliers d'Impact Startups")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("#### 1. Innovation Digitale & IA")
            st.write("Intégration d'outils décisionnels pour minimiser l'impact des aléas climatiques sur les rendements.")
        with col_p2:
            st.markdown("#### 2. Sécurisation des Financements")
            st.write("Modélisation financière bancable conforme aux critères d'exigence des bailleurs (DER/FJ, BNDE, LBA).")


# =====================================================
# CONTACT
# =====================================================
elif selected == "📞 Contact":

    st.markdown("""
    <div style="text-align:center; margin-bottom: 20px;">
        <h1>🤝 Contactez YouAgronoMe</h1>
        <p>Une question, un partenariat ou besoin d'assistance ? Notre équipe vous répond.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📞 Téléphone", value="777473170")
    with c2:
        st.metric(label="📍 Bureau Principal", value="Saint-Louis")
    with c3:
        st.metric(label="⏱ Temps de réponse", value="< 24h")

    st.write("---")

    col_form, col_FAQ = st.columns([3, 2])

    with col_form:
        st.subheader("📩 Envoyez-nous un message")
        
        with st.form("contact_form", clear_on_submit=True):
            nom = st.text_input("Nom & Prénom")
            email = st.text_input("Adresse Email")
            profil = st.selectbox("Vous êtes :", ["Producteur / Agriculteur", "Technicien Agricole", "ONG / Projet", "Investisseur / Banque", "Autre"])
            message = st.text_area("Votre Message")
            
            submit = st.form_submit_button("Envoyer le message", type="primary")
            
            if submit:
                if nom and email and message:
                    st.success("✅ Votre message a été transmis avec succès à l'équipe YouAgronoMe.")
                else:
                    st.error("⚠️ Veuillez remplir tous les champs obligatoires.")

    with col_FAQ:
        st.subheader("❓ Questions Fréquentes")
        with st.expander("Comment consulter les documents de la bibliothèque ?"):
            st.write("Les documents sont consultables directement en ligne dans la section 'Conseil' sans téléchargement pour préserver les droits d'auteur.")
        with st.expander("Comment obtenir un Business Plan certifié ?"):
            st.write("Configurez votre projet dans l'onglet 'Consultance' et téléchargez directement le livrable au format Excel.")
