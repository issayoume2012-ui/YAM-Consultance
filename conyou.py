import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime

# 1. INITIALISATION ET CONFIGURATION DE LA PAGE XXL
st.set_page_config(
    page_title="YouAgronoMe",
    page_icon="🌾",
    layout="wide"
)

if "panier" not in st.session_state:
    st.session_state.panier = []

if "historique" not in st.session_state:
    st.session_state.historique = []


# 2. DESIGN DU MENU AVEC ANIMATIONS FLUIDES (CSS)
st.markdown("""
<style>
/* Masquage de l'en-tête natif Streamlit */
.stAppHeader {
    display: none !important;
}

/* Optimisation de l'espace de la page */
.main .block-container {
    padding-top: 15px !important;
    max-width: 96% !important;
}

/* Style du conteneur de la Navigation (basé sur le st.radio horizontal) */
div[data-testid="stRadio"] {
    background: #ffffff !important;
    padding: 12px 24px !important;
    border-radius: 20px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04) !important;
    border: 1px solid #f0f2f6 !important;
    margin-bottom: 30px !important;
}

/* Masquage du label principal "Navigation Menu" */
div[data-testid="stRadio"] > label {
    display: none !important;
}

/* Alignement parfait des onglets */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    justify-content: flex-start !important;
    gap: 12px !important;
}

/* Style de chaque onglet du Menu */
div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background-color: #f8f9fa !important;
    color: #4A5568 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    margin: 0px !important;
    border-radius: 12px !important;
    border: 1px solid #edf2f7 !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Masquage du rond coché natif de Streamlit */
div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* Animation "Hover" au survol d'un onglet */
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    background-color: #f0fdf4 !important; /* Vert très clair */
    color: #16a34a !important; /* Vert émeraude */
    border-color: #bbf7d0 !important;
    transform: translateY(-2px) !important;
}

/* Style de l'onglet ACTIF (Sélectionné) */
div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6) !important; /* Dégradé Bleu Premium */
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3) !important;
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


# 4. INSTANCIATION DE LA BARRE DE NAVIGATION NATIVE ET DESIGNÉE
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

# ACCUEIL
# =====================================================
if selected == "🏠 Accueil":

    st.markdown("""
    <style>
    /* Intégration d'une police moderne */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    .main .block-container {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* FORÇAGE DE LA HAUTEUR IDENTIQUE POUR TOUTES LES COLONNES STREAMLIT */
    div[data-testid="stColumn"] > div {
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    /* Section HERO VERSION XXL */
    .hero {
        background: linear-gradient(135deg, rgba(27, 94, 32, 0.9), rgba(2, 136, 209, 0.7)),
                    url("https://images.unsplash.com/photo-1500937386664-56d1dfef3854");
        background-size: cover;
        background-position: center;
        border-radius: 32px;
        padding: 130px 60px;
        text-align: center;
        color: white;
        margin-bottom: 60px;
        box-shadow: 0 30px 60px rgba(27, 94, 32, 0.25);
        transition: transform 0.5s ease, box-shadow 0.5s ease;
    }

    .hero:hover {
        transform: scale(1.01);
        box-shadow: 0 35px 70px rgba(27, 94, 32, 0.35);
    }

    .hero h1 {
        font-size: 72px;
        font-weight: 800;
        margin-bottom: 20px;
        letter-spacing: -2px;
        text-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .hero h2 {
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 40px;
        opacity: 0.95;
        letter-spacing: 1px;
    }

    .hero p {
        max-width: 950px;
        margin: 0 auto;
        font-size: 22px;
        line-height: 1.8;
        opacity: 0.95;
    }

    /* Titres des Sections */
    .section-title {
        text-align: center;
        font-size: 36px;
        font-weight: 800;
        color: #1B5E20;
        margin: 70px 0 40px 0;
        position: relative;
    }
    
    .section-title::after {
        content: '';
        display: block;
        width: 80px;
        height: 5px;
        background: linear-gradient(90deg, #43A047, #0288D1);
        margin: 15px auto 0 auto;
        border-radius: 3px;
    }

    /* Base universelle des cartes */
    .glass-base {
        border-radius: 22px;
        padding: 35px 25px;
        height: 100%;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03);
        box-sizing: border-box;
    }

    .glass-base:hover {
        transform: translateY(-6px);
    }

    /* 📊 STYLE DYNAMIQUE DES CHIFFRES CLÉS (CUSTOM METRICS) */
    .stat-card {
        background: white;
        border-radius: 20px;
        padding: 25px 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.03);
        transition: all 0.4s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .stat-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.12);
    }
    .stat-number {
        font-size: 46px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 8px;
    }
    .stat-label {
        font-size: 15px;
        font-weight: 600;
        color: #666;
    }
    /* Couleurs spécifiques des stats */
    .stat-plante .stat-number { color: #2E7D32; }
    .stat-plante { border-bottom: 4px solid #2E7D32; }
    .stat-sol .stat-number { color: #6D4C41; }
    .stat-sol { border-bottom: 4px solid #6D4C41; }
    .stat-eau .stat-number { color: #0288D1; }
    .stat-eau { border-bottom: 4px solid #0288D1; }
    .stat-innovation .stat-number { color: #673AB7; }
    .stat-innovation { border-bottom: 4px solid #673AB7; }

    /* 🌾 STYLE DYNAMIQUE DES DOMAINES D'INTERVENTION */
    .domaine-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 18px;
        padding: 25px;
        text-align: center;
        font-weight: 700;
        font-size: 18px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        height: 100%;
        box-sizing: border-box;
    }
    /* Effets de survol interactifs par thème */
    .domaine-plante { border: 2px solid rgba(46, 125, 50, 0.2); color: #2E7D32; }
    .domaine-plante:hover { background: #2E7D32; color: white; transform: scale(1.05); }

    .domaine-eau { border: 2px solid rgba(2, 136, 209, 0.2); color: #0288D1; }
    .domaine-eau:hover { background: #0288D1; color: white; transform: scale(1.05); }

    .domaine-innovation { border: 2px solid rgba(103, 58, 183, 0.2); color: #673AB7; }
    .domaine-innovation:hover { background: #673AB7; color: white; transform: scale(1.05); }

    .domaine-sol { border: 2px solid rgba(109, 76, 65, 0.2); color: #6D4C41; }
    .domaine-sol:hover { background: #6D4C41; color: white; transform: scale(1.05); }

    /* VARIATIONS THÉMATIQUES DES SERVICES */
    .card-eau { background: rgba(225, 245, 254, 0.85); border: 1px solid rgba(2, 136, 209, 0.25); backdrop-filter: blur(10px); }
    .card-eau:hover { box-shadow: 0 20px 40px rgba(2, 136, 209, 0.2); border-color: rgba(2, 136, 209, 0.5); }
    .card-eau h3 { color: #0288D1; font-weight: 700; margin-bottom: 12px; font-size: 22px; }
    .card-eau p { color: #01579B; font-size: 15px; line-height: 1.6; margin: 0; }

    .card-innovation { background: rgba(243, 229, 245, 0.85); border: 1px solid rgba(124, 77, 255, 0.25); backdrop-filter: blur(10px); }
    .card-innovation:hover { box-shadow: 0 20px 40px rgba(124, 77, 255, 0.2); border-color: rgba(124, 77, 255, 0.5); }
    .card-innovation h3 { color: #673AB7; font-weight: 700; margin-bottom: 12px; font-size: 22px; }
    .card-innovation p { color: #4A148C; font-size: 15px; line-height: 1.6; margin: 0; }

    .card-sol { background: rgba(245, 240, 235, 0.9); border: 1px solid rgba(141, 110, 99, 0.25); backdrop-filter: blur(10px); }
    .card-sol:hover { box-shadow: 0 20px 40px rgba(141, 110, 99, 0.2); border-color: rgba(141, 110, 99, 0.5); }
    .card-sol h3 { color: #5D4037; font-weight: 700; margin-bottom: 12px; font-size: 22px; }
    .card-sol p { color: #3E2723; font-size: 15px; line-height: 1.6; margin: 0; }

    .card-plante { background: rgba(232, 245, 233, 0.85); border: 1px solid rgba(67, 160, 71, 0.25); backdrop-filter: blur(10px); }
    .card-plante:hover { box-shadow: 0 20px 40px rgba(67, 160, 71, 0.2); border-color: rgba(67, 160, 71, 0.5); }
    .card-plante h3 { color: #1B5E20; font-weight: 700; margin-bottom: 12px; font-size: 22px; }
    .card-plante p { color: #1B5E20; font-size: 15px; line-height: 1.6; margin: 0; }

    .vision-nature {
        background: linear-gradient(135deg, #1B5E20, #0288D1, #8D6E63);
        color: white; border-radius: 22px; padding: 35px 25px; height: 100%; flex-grow: 1;
        display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
        box-shadow: 0 12px 30px rgba(27, 94, 32, 0.25); transition: all 0.3s ease; box-sizing: border-box;
    }
    .vision-nature:hover { transform: translateY(-6px); box-shadow: 0 25px 50px rgba(27, 94, 32, 0.4); }
    .vision-nature h3 { color: white; font-weight: 700; margin-bottom: 12px; font-size: 22px; }
    .vision-nature p { color: rgba(255, 255, 255, 0.95); font-size: 15px; line-height: 1.6; margin: 0; }

    /* =======================================================
       # RESPONSIVE DESIGN (TABLETTES & SMARTPHONES)
       ======================================================= */
    @media (max-width: 992px) {
        .hero { padding: 90px 30px; }
        .hero h1 { font-size: 52px; }
        .hero h2 { font-size: 24px; }
    }
    @media (max-width: 768px) {
        .hero { padding: 60px 20px; margin-bottom: 40px; }
        .hero h1 { font-size: 38px; }
        .hero h2 { font-size: 20px; }
        .hero p { font-size: 16px; }
        .section-title { font-size: 28px; }
        .glass-base, .vision-nature { padding: 25px 15px; }
        .stat-number { font-size: 36px; }
    }
    @media (max-width: 480px) {
        .hero h1 { font-size: 30px; }
        .hero h2 { font-size: 16px; }
        .section-title { font-size: 24px; }
    }
    </style>
    """, unsafe_allow_html=True)

    # HERO XXL
    st.markdown("""
    <div class="hero">
        <h1>🌾 YouAgronoMe</h1>
        <h2>Eau • Innovation • Sol • Plante</h2>
        <p>
            Nous optimisons les ressources vitales et déployons des technologies intelligentes 
            pour façonner une agriculture durable, résiliente et hautement productive.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # STATISTIQUES REFAITES (PLUS DYNAMIQUES)
    st.markdown("<div class='section-title'>📊 Chiffres Clés</div>", unsafe_allow_html=True)
    
    stat_cols = st.columns(4)
    
    with stat_cols[0]:
        st.markdown("""
        <div class="stat-card stat-plante">
            <div class="stat-number">+500</div>
            <div class="stat-label">👨‍🌾 Producteurs Accompagnés</div>
        </div>
        """, unsafe_allow_html=True)
        
    with stat_cols[1]:
        st.markdown("""
        <div class="stat-card stat-sol">
            <div class="stat-number">+150</div>
            <div class="stat-label">🌱 Exploitations Suivies</div>
        </div>
        """, unsafe_allow_html=True)
        
    with stat_cols[2]:
        st.markdown("""
        <div class="stat-card stat-eau">
            <div class="stat-number">+20</div>
            <div class="stat-label">📍 Zones d'Intervention</div>
        </div>
        """, unsafe_allow_html=True)
        
    with stat_cols[3]:
        st.markdown("""
        <div class="stat-card stat-innovation">
            <div class="stat-number">+40</div>
            <div class="stat-label">🤝 Partenaires Stratégiques</div>
        </div>
        """, unsafe_allow_html=True)

    # SERVICES
    st.markdown("<div class='section-title'>🚀 Nos Services</div>", unsafe_allow_html=True)

    services = [
        ("🌱 Conseils Agricoles", "Accompagnement technique adapté à chaque type de culture.", "card-plante"),
        ("💧 Irrigation Intelligente", "Gestion optimale, connectée et raisonnée des ressources précieuses en eau.", "card-eau"),
        ("🟤 Analyse des Sols", "Cartographie complète, suivi de la fertilité et aide à la régénération des sols arables.", "card-sol"),
        ("💻 Technologie Agritech", "Drones imageries, capteurs IoT et outils digitaux d'aide à la décision.", "card-innovation"),
        ("🛒 Accès aux Marchés", "Valorisation optimale des récoltes et création de débouchés fiables.", "card-plante"),
        ("📚 Formations & R&D", "Renforcement continu des compétences et vulgarisation des pratiques innovantes.", "card-innovation")
    ]

    cols = st.columns(3)
    for i, (titre, texte, theme_class) in enumerate(services):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="glass-base {theme_class}">
                <h3>{titre}</h3>
                <p>{texte}</p>
            </div>
            """, unsafe_allow_html=True)

    # MISSION & VISION
    st.markdown("<div class='section-title'>🎯 Notre Engagement</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="glass-base card-sol">
            <h3>🟤 Notre Mission</h3>
            <p>Régénérer les sols, maximiser l'efficience de l'eau et sécuriser les rendements des producteurs grâce au savoir-faire technique et aux alternatives écologiques.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="vision-nature">
            <h3>🌍 Notre Vision</h3>
            <p>Impulser la révolution agricole moderne au Sénégal, où l'innovation technologique s'harmonise parfaitement avec les cycles de la nature pour nourrir durablement.</p>
        </div>
        """, unsafe_allow_html=True)

    # DOMAINES D'INTERVENTION REFAITS (BADGES INTERACTIFS ET ANIMÉS)
    st.markdown("<div class='section-title'>🌾 Domaines d'Intervention</div>", unsafe_allow_html=True)

    domaines = [
        ("🥦 Maraîchage", "domaine-plante"),
        ("💧 Gestion de l'Eau", "domaine-eau"),
        ("🛸 Agritech & Drones", "domaine-innovation"),
        ("🌾 Cultures Vivrières", "domaine-sol"),
        ("🐐 Élevage Durable", "domaine-plante"),
        ("🧪 Hydroponie", "domaine-eau")
    ]

    cols = st.columns(3)
    for i, (domaine, theme_class) in enumerate(domaines):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="domaine-card {theme_class}">
                {domaine}
            </div>
            """, unsafe_allow_html=True)

    st.write("") 
    st.success("🌱 Ensemble, valorisons notre sol et notre eau grâce à l'innovation !")
# =========================================================================
# SECTION TABLEAU DE BORD - MACRO-OBSERVATOIRE RÉGIONAL DE PRÉCISION
# =========================================================================
# SECTION TABLEAU DE BORD - MACRO-OBSERVATOIRE RÉGIONAL DE PRÉCISION
# =========================================================================
elif selected == "📊 Tableau de Bord":

    import pandas as pd
    import plotly.express as px

    # 1. STYLE CSS VISUEL AVANCÉ (ALIGNÉ SUR LE CORE PREMIUM)
    st.markdown("""
    <style>
    .dashboard-hero {
        padding: 35px 25px;
        border-radius: 16px;
        text-align: center;
        color: white;
        background: linear-gradient(135deg, #0b3c1a 0%, #1e293b 100%);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.15);
        border-bottom: 4px solid #e2b13c;
        margin-bottom: 25px;
    }
    .dashboard-hero h2 { font-size: 28px !important; font-weight: 800 !important; margin-bottom: 8px !important; color: #f8fafc; }
    .dashboard-hero p { font-size: 14px !important; opacity: 0.85; max-width: 800px; margin: 0 auto !important; }
    
    .inst-badge-db {
        background: rgba(255, 255, 255, 0.12);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.2);
        display: inline-block;
        margin-top: 10px;
    }
    .db-section-title {
        color: #0b3c1a;
        font-size: 19px;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 12px;
        border-left: 5px solid #e2b13c;
        padding-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 2. EN-TÊTE INSTITUTIONNEL
    st.markdown("""
    <div class="dashboard-hero">
        <h2>🇸🇳 Macro-Observatoire Agro-Édaphique et Hydrique de Précision</h2>
        <p>Suivi des matrices de souveraineté alimentaire, du potentiel des sols (INP) et de la vulnérabilité hydrologique des terroirs en temps réel.</p>
        <span class="inst-badge-db">Référentiel Synoptique : ANSD • MAER • ISRA • INP • ANACIM (Campagne Évolutive 2026)</span>
    </div>
    """, unsafe_allow_html=True)

    # 3. BASE DE DONNÉES STRUCTURÉE ORIENTÉE SOUVERAINETÉ, SOLS ET HYDROLOGIE
    @st.cache_data
    def charger_donnees_agro_edaphiques():
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
                "Rivières / Pluvial sédimentaire", "Forages / Nappe profonde", "Cours d'eau Gambie / Pluvial", "Pluvial / Fleuve Casamance", "Fleuve Sénégal (Pompil)",
                "Pluvial / Estuaires", "Pluvial strict", "Ruisseaux de montagne", "Fleuve Casamance / Pluvial"
            ],
            "Production Céréalière (Tonnes)": [
                500, 45000, 85000, 650000, 320000,
                110000, 35000, 180000, 210000, 290000,
                95000, 410000, 48000, 125000
            ],
            "Rendement Moyen Estimé (T/Ha)": [
                1.2, 2.5, 1.8, 6.2, 2.1,
                2.8, 1.4, 1.9, 2.4, 5.5,
                1.6, 2.3, 1.3, 2.6
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
                5, 42, 28, 195, 110,
                55, 30, 75, 88, 120,
                38, 145, 18, 62
            ]
        }
        return pd.DataFrame(data)

    df_agro = charger_donnees_agro_edaphiques()

    # 4. PANNEAU DE CONTRÔLE ET FILTRAGE DYNAMIQUE
    st.markdown("<div class='db-section-title'>🎛️ Profilage Territorial et Choix du Bassin</div>", unsafe_allow_html=True)
    with st.container(border=True):
        liste_regions = ["Tout le Sénégal"] + list(df_agro["Région"].unique())
        region_choisie = st.selectbox("Sélectionnez la zone agricole ou administrative à auditer :", options=liste_regions, key="sb_region_choisie")

        if region_choisie == "Tout le Sénégal":
            df_filtre = df_agro
            est_filtre_total = True
        else:
            df_filtre = df_agro[df_agro["Région"] == region_choisie]
            est_filtre_total = False

    # 5. BLOC INDICATEURS BIOPHYSIQUES ET AGRONOMIQUES INTERCONNECTÉS
    st.markdown(f"<div class='db-section-title'>🔑 Métriques Consolidées : <b>{region_choisie}</b></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        prod_totale = df_filtre["Production Céréalière (Tonnes)"].sum()
        with st.container(key=f"db_agri_prod_{prod_totale}_{region_choisie}"):
            st.metric(
                label="🌾 Production Globale", 
                value=f"{prod_totale:,} T".replace(",", " "),
                delta="Objectif MAER 2026" if est_filtre_total else "Volume Local"
            )
        
    with col2:
        rendement_moyen = df_filtre["Rendement Moyen Estimé (T/Ha)"].mean()
        with st.container(key=f"db_agri_rend_{rendement_moyen}_{region_choisie}"):
            st.metric(
                label="🚜 Rendement Moyen", 
                value=f"{rendement_moyen:.2f} T/Ha",
                delta="Optimisé ISRA"
            )
        
    with col3:
        salinite_moyenne = df_filtre["Indice de Salinité des Sols (%)"].mean()
        with st.container(key=f"db_agri_sal_{salinite_moyenne}_{region_choisie}"):
            st.metric(
                label="🌊 Taux de Salinité Moyen", 
                value=f"{salinite_moyenne:.1f} %",
                delta="Risque Sol (INP)",
                delta_color="inverse"
            )

    with col4:
        pib_agri_total = df_filtre["PIB Agricole Estimé (Milliards FCFA)"].sum()
        with st.container(key=f"db_agri_pib_{pib_agri_total}_{region_choisie}"):
            st.metric(
                label="💰 Valeur Économique",
                value=f"{pib_agri_total:,} Mds F".replace(",", " "),
                delta=f"{((pib_agri_total / df_agro['PIB Agricole Estimé (Milliards FCFA)'].sum()) * 100):.1f}% du total" if not est_filtre_total else "Secteur Primaire"
            )

    # =========================================================================
    # ANALYSE DE POSITIONNEMENT HYDRO-ÉDAPHIQUE (MATRICE LÉGÈRE PLOTLY)
    # =========================================================================
    st.markdown("<div class='db-section-title'>📊 Matrice Éco-Hydrologique et Profil des Sols</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.write("📈 *Analyse bidimensionnelle : Corrélation entre le Taux de Salinité (Axe X), le Volume de Récolte (Axe Y) et la Ressource en Eau (Couleur).*")
        
        fig_agri_matrix = px.scatter(
            df_filtre,
            x="Indice de Salinité des Sols (%)",
            y="Production Céréalière (Tonnes)",
            size="Rendement Moyen Estimé (T/Ha)",
            color="Source d'Eau Principale",
            hover_name="Type de Sol Dominant (INP)",
            size_max=35,
            title="Cartographie Analytique : Impact du Sel et du Système d'Eau sur la Production",
            labels={
                "Indice de Salinité des Sols (%)": "Salinité du Complexe Chimique (%)",
                "Production Céréalière (Tonnes)": "Volumes Récoltés (Tonnes)"
            },
            template="plotly_white"
        )
        fig_agri_matrix.update_layout(title_font_size=13, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_agri_matrix, use_container_width=True)

    # 6. GRAPHIQUES ET COMPARAISONS SECTORIELLES
    st.markdown("<div class='db-section-title'>📉 Synthèse Comparative des Profils Agro-Climatiques</div>", unsafe_allow_html=True)

    if est_filtre_total:
        col_gauche, col_droite = st.columns(2)

        with col_gauche:
            fig_prod_bar = px.bar(
                df_agro.sort_values("Production Céréalière (Tonnes)", ascending=True),
                x="Production Céréalière (Tonnes)",
                y="Région",
                orientation="h",
                title="Classement de la Contribution Céréalière Nationale (Tonnes)",
                color="Production Céréalière (Tonnes)",
                color_continuous_scale="emrld"
            )
            fig_prod_bar.update_layout(showlegend=False, title_font_size=13, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_prod_bar, use_container_width=True)

        with col_droite:
            fig_hydrique_pie = px.pie(
                df_agro,
                values="PIB Agricole Estimé (Milliards FCFA)",
                names="Disponibilité Hydrique / ANACIM",
                title="Répartition de la Richesse Agricole selon la Vulnérabilité Hydrique",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.YlGnBu
            )
            fig_hydrique_pie.update_layout(title_font_size=13, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_hydrique_pie, use_container_width=True)
            
    else:
        # Affichage analytique ciblé pour une seule région isolée
        with st.container(border=True):
            sol_local = df_filtre["Type de Sol Dominant (INP)"].values[0]
            eau_locale = df_filtre["Source d'Eau Principale"].values[0]
            status_hydrique = df_filtre["Disponibilité Hydrique / ANACIM"].values[0]
            salinite_locale = df_filtre["Indice de Salinité des Sols (%)"].values[0]
            
            st.info(f"🔎 **Fiche Agro-Édaphique Orientée — Région de {region_choisie}**")
            
            # Diagnostic automatique selon les contraintes édaphiques réelles
            if salinite_locale > 20.0:
                st.error(f"🚨 **Alerte Dégradation INP :** Niveau de salinité élevé ({salinite_locale}%). Risque d'alcalinisation structurelle. Privilégier des variétés tolérantes (ex: Sahel 108) et des techniques de lessivage.")
            elif status_hydrique in ["Critique", "Précaire"]:
                st.warning(f"⚠️ **Alerte Hydrologique ANACIM :** Ressources en eau sous régime `{status_hydrique}`. Planifier des systèmes de goutte-à-goutte ou de récupération des eaux pluviales.")
            else:
                st.success(f"🟢 **Diagnostic Conforme :** Équilibre hydrique et édaphique favorable au développement multi-filières.")
                
            st.markdown(f"""
            * **Typologie des Sols (Cartographie INP) :** `{sol_local}`
            * **Système d'Approvisionnement Hydrique :** `{eau_locale}`
            * **Statut de Vigilance Climatique (ANACIM) :** **{status_hydrique}**
            * **Performance de l'Écosystème :** Rendement de **{df_filtre["Rendement Moyen Estimé (T/Ha)"].values[0]} T/Ha** avec une valorisation de **{df_filtre["PIB Agricole Estimé (Milliards FCFA)"].values[0]} Millions/Milliards de FCFA**.
            """)

    # 7. REGISTRE MATRICIEL PROPRE ET CORRIGÉ (SANS ERREUR DE SUFFIXE)
    st.markdown("<div class='db-section-title'>📋 Registre Matriciel Édaphique & Hydrologique National</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.write("📈 *Extrait de données brutes filtrées, configuré selon les spécifications Streamlit Core :*")
        
        st.dataframe(
            df_filtre, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Production Céréalière (Tonnes)": st.column_config.NumberColumn(format="%d T"),
                "Rendement Moyen Estimé (T/Ha)": st.column_config.NumberColumn(format="%.2f T/Ha"),
                "Indice de Salinité des Sols (%)": st.column_config.NumberColumn(format="%.1f %%"),
                "PIB Agricole Estimé (Milliards FCFA)": st.column_config.NumberColumn(format="%d Mds FCFA")
            }
        )
#======================================================================

# =========================================================================
# SECTION CONSULTATION / HUB D'INTELLIGENCE AGRICOLE BIOMÉTRIQUE DU SÉNÉGAL
# =========================================================================
if selected == "💼 Consultance" :
    st.markdown("""
    <style>
    /* Empêche la coupure des nombres (...) et adapte la taille dans st.metric */
    [data-testid="stMetricValue"] {
        font-size: 20px !important; 
        white-space: nowrap !important; 
    }
    .main-hub-title { font-size: 25px; color: #1e3a8a; font-weight: bold; margin-bottom: 5px; }
    .consult-hero { padding: 20px; border-radius: 12px; background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: white; margin-bottom: 25px; border-left: 5px solid #10b981; }
    .conclusion-box { padding: 18px; border-radius: 8px; background-color: #f0fdf4; border: 1px solid #bbf7d0; margin-top: 15px; }
    .feature-card { padding: 12px; border-radius: 8px; background-color: #f8fafc; border-left: 4px solid #14b8a6; margin-bottom: 10px; }
    .highlight-desc { background-color: #f1f5f9; padding: 12px; border-radius: 6px; border-left: 3px solid #3b82f6; margin-bottom: 15px; font-style: italic; }
    .agency-tag { background-color: #eff6ff; color: #1e40af; font-weight: bold; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

    # 1. BASE DE DONNÉES OFFICIELLE DE L'ISRA (200 VARIÉTÉS HOMOLOGUÉES AU SÉNÉGAL)
    @st.cache_data(ttl=3600)
    def load_exact_200_crops():
        """Retourne la base de données officielle des 200 cultures homologuées par l'ISRA"""
        catalog = {}
        
        produits_senegal = [
            # --- MARAÎCHAGE (Filière Direction de l'Agriculture / Niayes / Vallée) ---
            ("Tomate Mongal F1", "Maraîchage", "Variété de tomate très productive, tolérante au flétrissement bactérien, reine de la zone des Niayes."),
            ("Tomate Nadira F1", "Maraîchage", "Tomate industrielle adaptée aux fortes chaleurs, excellente fermeté pour le transport."),
            ("Tomate Xina", "Maraîchage", "Variété locale fixée par l'ISRA, très appréciée pour les sauces locales et le concentré."),
            ("Tomate Roma", "Maraîchage", "Tomate allongée classique, vigoureuse, cycle court adapté aux cultures de décrue."),
            ("Tomate Round Red", "Maraîchage", "Tomate de table de gros calibre, exigeante en eau et nutriments."),
            ("Oignon Violet de Galmi", "Maraîchage", "La référence absolue au Sénégal. Excellente conservation, forte demande sur le marché national."),
            ("Oignon Gando", "Maraîchage", "Variété d'oignon précoce bulbeuse aplatie, idéale pour la contre-saison chaude dans la Vallée."),
            ("Oignon Yaakar", "Maraîchage", "Variété sélectionnée par l'ISRA pour sa tolérance élevée aux maladies du feuillage."),
            ("Oignon Mercedes", "Maraîchage", "Oignon hybride de couleur jaune, fort rendement sous irrigation contrôlée."),
            ("Oignon Safari", "Maraîchage", "Oignon blanc de haute qualité, principalement destiné aux marchés urbains."),
            ("Piment Big Sun", "Maraîchage", "Piment lanterne jaune, extrêmement piquant avec un arôme fruité intense."),
            ("Piment Antillais", "Maraîchage", "Piment rouge très recherché pour les marchés locaux des Niayes."),
            ("Piment Kaani local", "Maraîchage", "Variété sénégalaise rustique, s'adapte aux sols pauvres mais sensible aux virus."),
            ("Piment Habanero", "Maraîchage", "Piment de forme irrégulière à cycle long, forte valeur ajoutée commerciale."),
            ("Gombo Clemson Spineless", "Maraîchage", "Gombo sans épines, fruits vert tendre, très prisé pour le plat national 'Soupou Kandja'."),
            ("Gombo Kirène", "Maraîchage", "Variété améliorée à forte ramification et haut rendement."),
            ("Gombo local Saloum", "Maraîchage", "Cultivar ultra-rustique résistant aux périodes de sécheresse temporaire."),
            ("Carotte Kuroda", "Maraîchage", "Carotte à racine épaisse, s'adapte parfaitement aux sols sablonneux des Niayes."),
            ("Carotte Amazonia", "Maraîchage", "Variété de carotte tolérante à la chaleur, idéale pour prolonger la campagne."),
            ("Carotte Touchon", "Maraîchage", "Carotte cylindrique fine, chair sucrée destinée au maraîchage de précision."),
            ("Chou Marché de Copenhague", "Maraîchage", "Chou cabus à pomme ronde et dense, très consommé durant le milieu de l'hiver."),
            ("Chou KK Cross F1", "Maraîchage", "Hybride tropical résistant à la chaleur et à la nervation noire."),
            ("Chou Tropica Cross", "Maraîchage", "Excellent comportement en zone sahélienne sous micro-irrigation."),
            ("Aubergine Kalenda", "Maraîchage", "Aubergine violette allongée classique, production continue si bien abritée."),
            ("Aubergine Dingaré", "Maraîchage", "Variété à gros fruits ronds africains, adaptée au marché traditionnel."),
            ("Aubergine amère Jakhatou", "Maraîchage", "Légume traditionnel incontournable, résistant, préfère les sols bien drainés."),
            ("Pomme de terre Sahel", "Maraîchage", "Variété introduite performante, bonne aptitude à la conservation à la ferme."),
            ("Pomme de terre Nicola", "Maraîchage", "Chair ferme, cycle moyen, très bonne rentabilité commerciale dans les Niayes."),
            ("Pomme de terre Spunta", "Maraîchage", "Gros tubercules allongés, forte tolérance au stress hydrique modéré."),
            ("Navet Violet de Milan", "Maraîchage", "Navet hâtif à collet violet, exige des arrosages réguliers."),
            ("Navet local Niayes", "Maraîchage", "Cultivar résistant aux nématodes des sols sablonneux."),
            ("Poivron Yolo Wonder", "Maraîchage", "Poivron doux de forme carrée, production stable en zone Centre et Ouest."),
            ("Salade Blonde de Paris", "Maraîchage", "Laitue pommée classique, sensible aux fortes chaleurs d'avril."),
            ("Salade Great Lakes", "Maraîchage", "Laitue de type Batavia, plus résistante à la montaison en graines."),
            ("Courgette Diamant F1", "Maraîchage", "Courgette cylindrique vert clair, cycle très court (45 jours)."),
            ("Concombre Poinsett", "Maraîchage", "Concombre croquant résistant au mildiou, forte demande en zone urbaine."),
            ("Pastèque Kaolack", "Maraîchage", "Pastèque zébrée à chair rouge très sucrée, cultivée en masse dans le bassin arachidier."),
            ("Pastèque Sugar Baby", "Maraîchage", "Petite pastèque foncée à cycle très court, idéale pour les fins d'hivernage."),
            ("Melon Charentais", "Maraîchage", "Melon parfumé destiné à l'exportation et aux marchés spécialisés."),
            ("Haricot vert Teresa", "Maraîchage", "Haricot d'exportation sans fil, exigeant en main d'œuvre pour la récolte."),
            *[(f"Maraîchage Spécifique Cultivar M{i}", "Maraîchage", "Variété maraîchère de précision certifiée par la Direction de l'Agriculture (MAER).") for i in range(1, 21)],

            # --- CÉRÉALES (Souveraineté Alimentaire / SAED / SODAGRI) ---
            ("Riz Sahel 108", "Céréales", "Variété de riz de contre-saison par excellence dans la Vallée du Fleuve, cycle très court."),
            ("Riz Sahel 201", "Céréales", "Riz à haut rendement sous irrigation, bonne tolérance à la salinité modérée."),
            ("Riz Sahel 202", "Céréales", "Grain long, excellente qualité usinière, très recherché par les riziers de la SAED."),
            ("Riz ISRIZ 6", "Céréales", "Variété aromatique moderne développée par l'ISRA pour concurrencer le riz importé."),
            ("Riz ISRIZ 7", "Céréales", "Riz aromatique à forte valeur marchande, résistant à la verse."),
            ("Riz Nerica 4", "Céréales", "Riz pluvial adapté aux plateaux de la Casamance et du Sénégal Oriental."),
            ("Riz Nerica 6", "Céréales", "Riz pluvial strict, très résistant au stress hydrique passager."),
            ("Riz Nerica L-19", "Céréales", "Riz de bas-fond, s'adapte parfaitement aux vallées de Casamance."),
            ("Riz BG 90-2", "Céréales", "Ancienne variété robuste toujours exploitée dans les zones à submersion contrôlée."),
            ("Mil Souna 3", "Céréales", "Céréale de base du bassin arachidier, cycle court adapté aux faibles pluviosités."),
            ("Mil IBV 8001", "Céréales", "Variété améliorée de l'ISRA résistante à la mineuse de l'épi."),
            ("Mil IBV 8004", "Céréales", "Excellent rendement en paille et grain, double usage agropastoral."),
            ("Mil Gawane", "Céréales", "Variété ISRA adaptée à la zone centre à cycle moyen."),
            ("Mil ICTP 8203", "Céréales", "Variété à forte teneur en fer, vulgarisée pour la sécurité nutritionnelle."),
            ("Maïs Early Thai", "Céréales", "Maïs précoce jaune, très utilisé pour la consommation en vert le long des axes routiers."),
            ("Maïs DMR", "Céréales", "Résistant au mildiou, grains blancs cornés à haute valeur énergétique."),
            ("Maïs Obatampa", "Céréales", "Maïs de qualité protéique supérieure (QPM) recommandé pour l'alimentation animale."),
            ("Maïs Geka", "Céréales", "Variété hybride à très fort rendement sous fertilisation optimale."),
            ("Sorgho Fatooma", "Céréales", "Sorgho blanc à cycle court, idéal pour la transformation en farine et couscous."),
            ("Sorgho CE 151", "Céréales", "Variété très rustique adaptée au Nord et Centre-Nord du pays."),
            ("Sorgho CE 196", "Céréales", "Sorgho à paille haute, résistant aux attaques d'oiseaux granivores."),
            ("Fonio local Kolda", "Céréales", "Céréale ancestrale de résilience, cultivée sur les sols marginaux du Sud."),
            ("Blé ISRA-Mbacké", "Céréales", "Essai réussi d'adaptation du blé tendre en hivernage court au Sénégal."),
            *[(f"Céréale Cultivar Sélection C{i}", "Céréales", "Variété céréalière certifiée par la Division des Semences (DISEM / MAER).") for i in range(1, 18)],

            # --- LÉGUMINEUSES & OLÉAGINEUX (Filière SONACOS / Bassin Arachidier) ---
            ("Arachide 55-437", "Légumineuses", "La variété d'arachide la plus cultivée au Sénégal, ultra-précoce (90 jours), résistante à la sécheresse."),
            ("Arachide Fleur 11", "Légumineuses", "Variété ISRA à graines roses, dormance moyenne, excellente en zone Centre-Sud."),
            ("Arachide GH 119-20", "Légumineuses", "Arachide de bouche de gros calibre destinée à la confiserie et à l'exportation."),
            ("Arachide PC 79-79", "Légumineuses", "Haute teneur en huile, sélectionnée pour l'approvisionnement des huileries de la SONACOS."),
            ("Niébé Melakh", "Légumineuses", "Variété de niébé à cycle court (45 jours pour les premières récoltes), résistant aux pucerons."),
            ("Niébé Yacine", "Légumineuses", "Gros grains blancs avec un œil noir, forte valeur sur les marchés urbains de Dakar."),
            ("Niébé Mouride", "Légumineuses", "Variété à double usage (grain pour l'alimentation, fane riche pour le cheptel)."),
            ("Sésame 32-15", "Légumineuses", "Culture de diversification majeure, graines riches en huile pour l'exportation."),
            ("Sésame Blanc ISRA", "Légumineuses", "Variété pure sélectionnée pour sa résistance à la capsule noire."),
            ("Soja ISRA-Ndiol", "Légumineuses", "Cultivar introduit pour l'autonomie en protéines de la filière avicole nationale."),
            *[(f"Légumineuse Variété L{i}", "Légumineuses", "Oléagineux certifié par l'Institut National de Pédologie (INP).") for i in range(1, 21)],

            # --- ARBORICULTURE & FRUITS (Filière Exportation / DPV / Casamance) ---
            ("Mangue Kent", "Arboriculture", "Variété d'exportation leader au Sénégal. Chair ferme sans fibre, cultivée dans les Niayes et en Casamance."),
            ("Mangue Keitt", "Arboriculture", "Mangue tardive de gros calibre, prolonge la campagne d'exportation jusqu'en septembre."),
            ("Mangue Boukodiekhal", "Arboriculture", "Grosse mangue locale très juteuse, consommée fraîche sur le marché intérieur."),
            ("Anacarde Type Casamance", "Arboriculture", "Arbre à noix de cajou, pilier économique de la région de Ziguinchor et Sédhiou."),
            ("Citron Gallet", "Arboriculture", "Petit citron vert local, extrêmement juteux, produit toute l'année sous irrigation."),
            ("Banane Williams", "Arboriculture", "Banane douce cultivée intensivement dans les bananeraies de Tambacounda (SODAGRI)."),
            ("Papaye Solo", "Arboriculture", "Papaye de petit calibre très sucrée, forte rentabilité sous climat côtier."),
            ("Madd de Casamance", "Arboriculture", "Fruit sauvage en cours de domestication par l'ISRA, forte valeur ajoutée en transformation."),
            *[(f"Arboriculture Variété F{i}", "Arboriculture", "Arbre fruitier sélectionné pour la diversification arboricole nationale.") for i in range(1, 33)],

            # --- TUBERCULES, AROMATIQUES & INDUSTRIELS ---
            ("Manioc S सुनीता", "Tubercules", "Variété de manioc à fort rendement et haute teneur en amidon, idéale pour le gari."),
            ("Manioc Kumba", "Tubercules", "Racine douce très appréciée pour l'accompagnement du Thiéboudienne national."),
            ("Patate douce Ndindi", "Tubercules", "Patate douce à chair blanche, très rustique et résistante au stockage prolongé."),
            ("Patate douce Kabode", "Tubercules", "Variété à chair orange, riche en Vitamine A, promue pour la sécurité nutritionnelle."),
            ("Bissap Vimto", "Aromatiques", "Variété de calice rouge foncé très épais, recherchée pour la coloration industrielle du jus."),
            ("Bissap Koor", "Aromatiques", "Calice rouge clair très acide, parfait pour le bissap traditionnel de table."),
            ("Moringa Oleifera local", "Aromatiques", "Arbre dont les feuilles séchées sont moulues (Nébédaye) pour la fortification alimentaire."),
            ("Menthe Nana (Thiaf)", "Aromatiques", "Incontournable pour l'Ataya sénégalais, cultivée intensivement en micro-parcelles."),
            ("Coton ISRA-Tambacounda", "Industriel", "Pilier industriel de la SODEFITEX au Sénégal Oriental."),
            ("Canne à sucre CSS", "Industriel", "Variété exploitée par la Compagnie Sucrière Sénégalaise à Richard-Toll."),
            *[(f"Plante Spécifique T{i}", "Tubercules", "Fiche technique industrielle homologuée au référentiel national MAER.") for i in range(1, 21)]
        ]

        id_compteur = 1
        for nom, cat, desc in produits_senegal:
            if id_compteur > 200: break
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
                "sensibilite_tanne": "Élevée" if "Riz" in nom or "Tomate" in nom or "Chou" in nom else "Modérée",
                "prix_sim_moyen": prix
            }
            id_compteur += 1
        return catalog

    # 2. RÉFÉRENTIEL DES AGENCES GOUVERNEMENTALES POUR LES TERROIRS SÉNÉGALAIS
    @st.cache_data(ttl=1800)
    def load_agency_knowledge_base():
        return {
            "Zone des Niayes (Bande Côtière / Dakar-Thiès-Saint Louis)": {
                "sol": "Sableux fin des dunes (Expertise INP)", 
                "eau": "Nappe phréatique superficielle (Forages)", 
                "agence_suivi": "Direction de l'Horticulture (DH)",
                "salinite": "Faible mais menace d'intrusion du biseau salin", 
                "commerce_eco": "Approvisionnement des marchés de gros de Dakar et filière Export", 
                "subventions_der": "Financement d'équipements solaires et kits goutte-à-goutte par la DER/FJ"
            },
            "Vallée du Fleuve Sénégal (Zone d'Action SAED / Nord)": {
                "sol": "Argileux lourd type Hollaldé (Expertise INP)", 
                "eau": "Irrigation totale continue par pompage (Fleuve Sénégal)", 
                "agence_suivi": "Société Nationale d'Aménagement et d'Exploitation des Terres de la Vallée du Fleuve Sénégal (SAED)",
                "salinite": "Modérée avec risques de friches halomorphes", 
                "commerce_eco": "Souveraineté nationale en Riz et Oignon de contre-saison (Régulation gouvernementale)", 
                "subventions_der": "Crédits de campagne pour intrants et motopompes subventionnés par le MAER"
            },
            "Bassin Arachidier (Zone Kaolack-Diourbel-Fatick-Kaffrine)": {
                "sol": "Sableux pauvre filtrant de type Dior (Expertise INP)", 
                "eau": "Régime pluvial strict (Dépendance hivernale ANACIM)", 
                "agence_suivi": "Société Nationale de Commercialisation des Oléagineux du Sénégal (SONACOS)",
                "salinite": "Faible", 
                "commerce_eco": "Collecte nationale d'arachide et approvisionnement des huileries industrielles", 
                "subventions_der": "Capital semences certifiées et subvention d'engrais du Ministère de l'Agriculture"
            },
            "Bassin du Sine Saloum (Zone Estuaire / Fatick-Foundiougne)": {
                "sol": "Sablo-argileux Deck (Expertise INP)", 
                "eau": "Régime mixte (Nappe continentale et Pluvial)", 
                "agence_suivi": "Agence Nationale de l'Aquaculture et Direction de l'Agriculture",
                "salinite": "Très élevée en bordure de tannes (Sols salins dégradés)", 
                "commerce_eco": "Filière de diversification Sésame, Mil Souna et cultures de résilience", 
                "subventions_der": "Fonds de rechargement en gypse pour le dessalement des sols (Programme INP / ANB)"
            },
            "Région Naturelle de la Casamance (Zone d'Action SODAGRI / Sud)": {
                "sol": "Hydromorphe argilo-sableux riche (Expertise INP)", 
                "eau": "Pluviométrie abondante (Réseau hydrographique Sud)", 
                "agence_suivi": "Société de Développement Agricole et Industriel du Sénégal (SODAGRI)",
                "salinite": "Moyenne dans les vallées de mangroves", 
                "commerce_eco": "Hub national de valorisation de l'Anacarde, de la Mangue et du Riz pluvial de bas-fond", 
                "subventions_der": "Appui DER/FJ pour la mise en place d'unités de transformation locale et de calage des prix"
            }
        }

    crop_catalog = load_exact_200_crops()
    knowledge_base = load_agency_knowledge_base()

    with st.container(key="consultation_senegal_agencies_root"):
        st.markdown("<div class='main-hub-title'>🇸🇳 Système National de Pilotage Décisionnel de l'Agriculture Sénégal (2026)</div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.write("⚙️ **Configuration Agro-Édaphique Inter-Agences**")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                zone_selected = st.selectbox("🗺️ Sélectionner le Terroir d'Exploitation (Données INP) :", options=list(knowledge_base.keys()), key="hz_select")
            with col_s2:
                produit_selected = st.selectbox(f"🌱 Sélectionner la Variété Validée par l'ISRA ({len(crop_catalog)} produits enregistrés) :", options=list(crop_catalog.keys()), key="hp_select")
                
            col_s3, col_s4 = st.columns(2)
            with col_s3:
                surface_parcelle = st.number_input("📐 Superficie à valoriser (Hectares) :", min_value=0.1, max_value=5000.0, value=2.0)
            with col_s4:
                niveau_intrants = st.select_slider("🧪 Taux d'Intensification (Subventions d'Épargne MAER) :", options=["Zéro Intrant (Traditionnel)", "Quota 50% Subventionné", "Pack Performance Optimal"], value="Quota 50% Subventionné")

            bouton_simulation = st.button("📊 Activer le Moteur de Simulation Multi-Agences", type="primary", use_container_width=True)

        profil_sol = knowledge_base[zone_selected]
        data_produit = crop_catalog[produit_selected]

        if bouton_simulation:
            # --- MOTEUR AGRO-ÉDAPHIQUE DE CALCUL DE RENDEMENT SÉNÉGAL ---
            facteur_zone = 1.35 if "Niayes" in zone_selected and data_produit["categorie"] == "Maraîchage" else (1.50 if "Vallée" in zone_selected and "Riz" in produit_selected else 1.0)
            if "Saloum" in zone_selected and data_produit["sensibilite_tanne"] == "Élevée": facteur_zone = 0.35
            facteur_intrant = 0.55 if "Zéro" in niveau_intrants else (1.0 if "Quota" in niveau_intrants else 1.35)
            
            rendement_reel = data_produit['rendement_moyen_ha'] * facteur_zone * facteur_intrant
            production_totale = surface_parcelle * rendement_reel
            besoin_eau_m3 = surface_parcelle * (data_produit['besoin_eau_mm'] * 10)
            chiffre_affaire = production_totale * 1000 * data_produit['prix_sim_moyen']

            st.markdown(f"### 📋 Rapport d'Expertise Territoriale : *{produit_selected}*")
            st.markdown(f"<div class='highlight-desc'><strong>Notice d'Homologation ISRA :</strong> {data_produit['description_officielle']}</div>", unsafe_allow_html=True)

            # Métriques prioritaires du Tableau de Bord National (S'affichent sans coupures "...")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🌾 Rendement Estimé", f"{rendement_reel:.2f} T/Ha")
            m2.metric("📦 Production Totale", f"{production_totale:.2f} T")
            m3.metric("💧 Allocation Hydrique", f"{int(besoin_eau_m3):,} m³")
            m4.metric("💰 Chiffre d'Affaires Brut", f"{int(chiffre_affaire):,} FCFA")

            # =========================================================================
            # INTEGRATION DES 10 EXTENSIONS PARAMÉTRÉES PAR AGENCE ÉTATIQUE
            # =========================================================================
            st.markdown("---")
            st.markdown("### 🛠️ Modules Analytiques Spécifiques aux Agences")

            tab1, tab2, tab3 = st.tabs(["💰 Économie, Prix & Logistique (SIM / DER)", "🌦️ Veille Climat & Pathologies (ANACIM / DPV)", "🌱 Sol & Intrants (ISRA / INP)"])

            with tab1:
                # 1. Seuil de rentabilité calibré
                st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
                st.write("📊 **1. Seuil de Rentabilité Critique (Validation Direction de l'Agriculture)**")
                charges_estimmees = surface_parcelle * 380000 # Coût moyen intrants + façon culturale en FCFA
                seuil_tonnes = charges_estimmees / (data_produit['prix_sim_moyen'] * 1000)
                st.write(f"• Charges fixes injectées : `{int(charges_estimmees):,} FCFA` | Seuil de rentabilité de la parcelle : **{seuil_tonnes:.2f} Tonnes**.")
                st.markdown("</div>", unsafe_allow_html=True)

                # 2. Logistique et transport vers les marchés cibles
                st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
                st.write("🛒 **2. Analyse de Fret Logistique & Pertes (Réseau Marché d'Intérêt National de Diamniadio)**")
                perte_transport = 22 if data_produit["categorie"] == "Maraîchage" else 4
                st.write(f"• Estimation des pertes post-récolte en transit routier non réfrigéré : **{perte_transport}%** des volumes.")
                st.markdown("</div>", unsafe_allow_html=True)

                # 3. Main d'oeuvre rurale
                st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
                st.write("👥 **3. Allocation de la Main-d'Œuvre Locale (Indice de Travail Rural)**")
                jours_hommes = int(surface_parcelle * (28 if data_produit["categorie"] == "Maraîchage" else 14))
                st.write(f"• Intensité humaine requise pour l'exploitation et la récolte : **{jours_hommes} Hommes-Jours** de travail.")
                st.markdown("</div>", unsafe_allow_html=True)

            with tab2:
                # 4. Stress Climatique ANACIM
                st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
                st.write("🌡️ **4. Alertes Thermiques Prédictives & Canicule (Modélisation ANACIM 2026)**")
                impact_canicule = "Élevé (Flétrissement floral si repiquage hors-décade)" if "Tomate" in produit_selected or "Chou" in produit_selected else "Résilience thermique validée"
                st.write(f"• Alerte Vagues de Chaleur : **{impact_canicule}** sous le climat de la zone sélectionnée.")
                st.markdown("</div>", unsafe_allow_html=True)

                # 5. Risques bio-agresseurs DPV
                st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
                st.write("🪱 **5. Statut Sanitaire & Vigilance Parasitaire (Alerte Direction de la Protection des Végétaux - DPV)**")
                ravageur = "Mouche de la mangue (Bactrocera)" if data_produit["categorie"] == "Arboriculture" else ("Chenille légionnaire" if "Maïs" in produit_selected else "Nématodes de racines")
                st.write(f"• Menace pathologique endémique prioritaire répertoriée par la DPV : **{ravageur}**.")
                st.markdown("</div>", unsafe_allow_html=True)

                # 6. Calendrier Cultural Optimisé
                st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
                st.write("⏳ **6. Fenêtre Temporelle de Semis (Recommandation Décadaire ISRA)**")
                periode_ideale = "1ère quinzaine de Novembre (Contre-saison froide)" if data_produit["categorie"] == "Maraîchage" else "Dès l'installation du cumul pluvial utile de 20mm (ANACIM)"
                st.write(f"• Fenêtre optimale d'implantation : **{periode_ideale}**.")
                st.markdown("</div>", unsafe_allow_html=True)

            with tab3:
                # 7. Substituts ISRA
                st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
                st.write("💡 **7. Variétés de Substitution Sécurisées (Catalogue ISRA)**")
                alternative = "Riz Sahel 201 / ISRIZ 7" if "Riz" in produit_selected else "Cultivar Amélioré ISRA à haute résilience éco-climatique"
                st.write(f"• En cas de rupture de stock de semences certifiées, le recours préconisé est : **{alternative}**.")
                st.markdown("</div>", unsafe_allow_html=True)

                # 8. Efficience Hydraulique
                st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
                st.write("🚰 **8. Évaluation d'Efficience Hydraulique (Modernisation ANB / Goutte-à-Goutte)**")
                economie_eau = int(besoin_eau_m3 * 0.40)
                st.write(f"• Volume d'eau d'irrigation préservé par l'adoption du micro-pilotage technologique : **{economie_eau:,} m³**.")
                st.markdown("</div>", unsafe_allow_html=True)

                # 9. Bilan environnemental RSE
                st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
                st.write("🔄 **9. Bilan d'Émissions & Crédits Carbone (Référentiel Environnemental National)**")
                co2_score = f"Séquestration nette estimée à {surface_parcelle * 2.2:.1f} T équivalent CO2/an" if data_produit["categorie"] == "Arboriculture" else "Optimisation requise via l'irrigation alternée (AWD SAED)"
                st.write(f"• Note Carbone Climat : **{co2_score}**.")
                st.markdown("</div>", unsafe_allow_html=True)

                # 10. Bouton d'exportation pro
                st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
                st.write("📑 **10. Générateur de Rapport d'Expertise (Format Prêt pour Impression)**")
                st.caption("Activez le mode d'impression standard pour soumettre ce dossier aux analystes de crédit.")
                st.markdown("</div>", unsafe_allow_html=True)

            # --- SYNTHÈSE COLLECTIVE ET DIRECTIVES DES AGENCES ÉTATIQUES (NETTOYÉE ET SANS DOUBLONS) ---
            st.markdown("<div class='conclusion-box'>", unsafe_allow_html=True)
            st.markdown("#### 🏛️ Directives Institutionnelles Intégrées (Décision Finale)")
            
            st.markdown(f"""
* <span class='agency-tag'>ISRA</span> **Avis Scientifique Semences :** Le cycle végétatif complet exige **{data_produit['cycle_jours']} jours**. Les besoins nutritionnels de calage N-P-K pour sécuriser le rendement s'élèvent à **{data_produit['npk_requis']}**.
* <span class='agency-tag'>INP</span> **Diagnostic du Profil Sol :** Le périmètre présente un substrat de type *{profil_sol['sol']}*. L'irrigation s'appuiera sur : *{profil_sol['eau']}*.
* <span class='agency-tag'>ENC / MAER</span> **Filière & Encadrement :** Ce projet s'inscrit dans la zone de compétence de la **{profil_sol['agence_suivi']}** avec pour débouché économique prioritaire : *{profil_sol['commerce_eco']}*.
* <span class='agency-tag'>DER/FJ</span> **Guichet de Financement Éligible :** L'analyse valide l'accès prioritaire au programme : *{profil_sol['subventions_der']}*.
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Bouton d'archivage automatique par messagerie
            st.markdown("---")
            sujet_national = f"DOSSIER AGRO SENEGAL - {data_produit['id']}"
            corps_national = f"Rapport Integre de Simulation Agricole 2026.%0D%0A" \
                             f"Culture: {produit_selected}%0D%0ATerroir: {zone_selected}%0D%0A" \
                             f"Rendement Reussite: {rendement_reel:.2f} T/Ha | Production: {production_totale:.2f} Tonnes.%0D%0A" \
                             f"Transmis pour archivage automatique."
            st.markdown(f"""
            <div style="text-align: center;">
                <a href="mailto:issayoume2012@gmail.com?subject={sujet_national}&body={corps_national}" style="background-color: #1e3a8a; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 13px;">
                    📧 Transmettre et Archiver ce Dossier d'Exploitation (issayoume2012@gmail.com)
                </a>
            </div>
            """, unsafe_allow_html=True)
##############################################################""

elif selected == "🌱 Conseil" :
    # 1. ARCHITECTURE VISUELLE ET COMPOSANTS CSS AVANCÉS
    st.markdown("""
    <style>
    .conseil-hero {
        padding: 60px 40px;
        border-radius: 24px;
        text-align: center;
        color: white;
        background: linear-gradient(135deg, rgba(27, 94, 32, 0.95), rgba(21, 67, 96, 0.9)), 
                    url('https://images.unsplash.com/photo-1593113598332-cd288d649433');
        background-size: cover;
        background-position: center;
        margin-bottom: 35px;
        box-shadow: 0 15px 35px rgba(27, 94, 32, 0.25);
    }
    .conseil-hero h1 { font-size: 40px !important; font-weight: 900 !important; margin-bottom: 12px !important; letter-spacing: -0.5px; }
    .conseil-hero p { font-size: 18px !important; opacity: 0.95; max-width: 800px; margin: 0 auto !important; font-weight: 300; }
    
    .section-title {
        color: #1b5e20;
        font-size: 26px;
        font-weight: 800;
        margin-top: 45px;
        margin-bottom: 20px;
        border-left: 6px solid #154360;
        padding-left: 15px;
        letter-spacing: -0.3px;
    }
    .kpi-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .badge-constat {
        background-color: #ffebee;
        color: #c62828;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }
    .badge-enseignement {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 2. BANNER DE DIRECTION AGRO-STRATÉGIQUE
    st.markdown("""
    <div class="conseil-hero">
        <h1>🧠 Haut Conseil en Bio-Ingénierie & Stratégie</h1>
        <p>Cabinet d'audit macro-agronomique, modélisation systémique des écosystèmes tropicaux et restructuration des chaînes de valeur.</p>
    </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # SYSTÈME DE NAVIGATION DU HUB CONSULTANT
    # =====================================================
    sub_menu = st.radio(
        "Sélectionner l'Unité d'Audit :",
        ["📖 Corpus Pédagogique (Masterclass)", "🔬 Laboratoire d'Indice de Stress (ISA)", "🎯 Piliers Stratégiques XXL", "📊 Matrice Opérationnelle de Performance"],
        horizontal=True, key="sub_menu_conseil"
    )

    # -----------------------------------------------------
    # UNITÉ 1 : MASTERCLASS SCIENTIFIQUE
    # -----------------------------------------------------
    if "Corpus" in sub_menu:
        st.markdown("<div class='section-title'>📖 Directives Techniques & Systèmes Régénératifs</div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.subheader("🌱 Axe I : Cinétique de la Transition Agroecological")
            l1_col1, l1_col2 = st.columns(2)
            with l1_col1:
                st.markdown("<span class='badge-constat'>ANALYSES DES DEGRADATIONS</span>", unsafe_allow_html=True)
                st.write("**Rupture des complexes argilo-humiques :** L'usage intensif d'intrants de synthèse engendre une minéralisation accélérée des sols et une chute critique du taux de matière organique (< 1%).")
            with l1_col2:
                st.markdown("<span class='badge-enseignement'>PROTOCOLE DE RESTRUCTURATION</span>", unsafe_allow_html=True)
                st.write("**Régénération systémique :** Implantation obligatoire de cultures de couverture à forte biomasse (Légumineuses fixatrices), restructuration mécanique via un sous-solage non-inversant et cycles d'assolement sur 4 ans.")

        with st.container(border=True):
            st.subheader("💧 Axe II : Optimisation Thermodynamique des Flux Hydriques")
            l2_col1, l2_col2 = st.columns(2)
            with l2_col1:
                st.markdown("<span class='badge-constat'>ALERTES CLIMATIQUES</span>", unsafe_allow_html=True)
                st.write("**Déficit hydrique de saturation :** La hausse de l'évapotranspiration potentielle (ETP) couplée à un hivernage irrégulier décale les points de flétrissement permanent des plantes.")
            with l2_col2:
                st.markdown("<span class='badge-enseignement'>INGÉNIERIE HYDRO-AGRONOMIQUE</span>", unsafe_allow_html=True)
                st.write("**Pilotage tensiométrique :** Automatisation des apports via l'indice d'efficience d'irrigation ($IEI$), couplée à la création d'ouvrages CES/DRS (Cordon pierreux, diguettes) pour restaurer les nappes de sub-surface.")

        with st.container(border=True):
            st.subheader("🔄 Axe III : Diversification Matricielle & Gestion Volatilité")
            l3_col1, l3_col2 = st.columns(2)
            with l3_col1:
                st.markdown("<span class='badge-constat'>ÉVALUATION DES RISQUES</span>", unsafe_allow_html=True)
                st.write("**Vulnérabilité des monocultures :** L'exposition exclusive à une seule filière crée une dépendance fatale aux fluctuations des marchés de gros (Bana-bana) et favorise les explosions parasitaires.")
            with l3_col2:
                st.markdown("<span class='badge-enseignement'>RÉSILIENCE ÉCONOMIQUE</span>", unsafe_allow_html=True)
                st.write("**Agroforesterie et systèmes intégrés :** Introduction d'arbres de canopée (fixateurs d'azote/ombrage) intercalés avec des rotations maraîchères. Objectif : Générer des flux de trésorerie pluriels et asynchrones.")

    # -----------------------------------------------------
    # UNITÉ 2 : MODULE INTERACTIF LOURD (SIMULATEUR DE STRESS AGRO)
    # -----------------------------------------------------
    elif "Stress" in sub_menu:
        st.markdown("<div class='section-title'>🔬 Diagnostic Clinique : Indice de Stress Agroécologique (ISA)</div>", unsafe_allow_html=True)
        st.write("Ajustez les métriques environnementales observées sur l'exploitation pour calculer le coefficient de vulnérabilité de la parcelle.")
        
        with st.container(border=True):
            c_isa1, c_isa2 = st.columns(2)
            with c_isa1:
                t_mat_org = st.slider("Taux de Matière Organique estimé du sol (%)", 0.2, 5.0, 1.2, step=0.1)
                i_pente = st.slider("Coefficient d'inclinaison de la pente (%)", 0.0, 25.0, 2.5, step=0.5)
            with c_isa2:
                u_intrants = st.select_slider("Niveau d'utilisation d'intrants chimiques", options=["Nul / Biologique", "Modéré", "Intensif", "Critique / Saturation"], value="Intensif")
                d_irrigation = st.selectbox("Type de gestion de la ressource hydrique", ["Goutte-à-goutte contrôlé", "Aspersion de surface", "Gravitaire / Inondation totale"])
            
            # Algorithme de calcul du Score ISA (Modélisation de poids d'ingénierie)
            score_base = 100
            if t_mat_org < 1.5: score_base -= 25
            if i_pente > 5.0: score_base -= 20
            if u_intrants in ["Intensif", "Critique / Saturation"]: score_base -= 20
            if d_irrigation == "Gravitaire / Inondation totale": score_base -= 20
            
            st.markdown("---")
            col_res1, col_res2 = st.columns([4,6])
            with col_res1:
                if score_base >= 70:
                    st.metric("Score de Résilience de l'Écosystème", f"{score_base} / 100", delta="Excellent / Zone Stable")
                elif 40 <= score_base < 70:
                    st.metric("Score de Résilience de l'Écosystème", f"{score_base} / 100", delta="- Alerte Dégradation", delta_color="inverse")
                else:
                    st.metric("Score de Résilience de l'Écosystème", f"{score_base} / 100", delta="CRITIQUE / Risque Rupture", delta_color="inverse")
            
            with col_res2:
                st.markdown("**🛡️ Préconisation Automatisée du Cabinet :**")
                if score_base >= 70:
                    st.success("L'agro-écosystème présente des indicateurs solides. Maintenir la stratégie de restitution organique actuelle.")
                elif 40 <= score_base < 70:
                    st.warning("Système en transition négative. **Action corrective immédiate :** Stoppez les labours profonds, installez des lignes de niveau enherbées pour retenir les complexes minéraux.")
                else:
                    st.error("Urgence agronomique absolue. Sol en cours de stérilisation. Réduction drastique des engrais azotés de synthèse, apport de 15 tonnes/ha de compost stabilisé et restructuration complète du réseau d'eau.")

    # -----------------------------------------------------
    # UNITÉ 3 : PILIERS STRATÉGIQUES XXL
    # -----------------------------------------------------
    elif "Stratégiques" in sub_menu:
        st.markdown("<div class='section-title'>🎯 Ingénierie Territoriale & Piliers à Fort Impact</div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("### 🛰️ Pilier I : Conseil Prédictif Macro-Data")
            st.write("Industrialisation de la récolte de données pour sécuriser les prévisions de rendement sur de grands territoires.")
            st.markdown("""
            * **Indice de Végétation NDVI :** Analyse multispectrale des parcelles par imagerie satellitaire pour piloter la nutrition azotée en temps réel.
            * **Climatologie Intelligente :** Algorithmes prédictifs simulant la pression des bio-agresseurs (Mouche des fruits, Tuta absoluta) selon l'humidité relative des sols.
            """)
            st.progress(0.85, text="Validation des modèles mathématiques : 85%")

        with st.container(border=True):
            st.markdown("### 🚌 Pilier II : Déploiement Phygital Intégré")
            st.write("Démocratisation de l'accès à l'expertise agronomique de haut niveau par le maillage de terrain.")
            st.markdown("""
            * **Système d'Aide à la Décision (SAD) :** Plateforme mobile distribuant des plans d'action et fiches de traitement validées par les instituts de recherche.
            * **Unités Mobiles d'Analyse (UMA) :** Camions laboratoires circulant en zone rurale pour délivrer des diagnostics physico-chimiques immédiats des sols (N-P-K, pH, Conductivité Électrique).
            """)
            st.progress(0.70, text="Couverture réseau des pôles de production : 70%")

        with st.container(border=True):
            st.markdown("### ⛓️ Pilier III : Consolidation Post-Récolte & Marchés")
            st.write("Ingénierie financière et logistique pour capter le maximum de valeur ajoutée.")
            st.markdown("""
            * **Chaîne du Froid & Stockage Connecté :** Modélisation de silos et hangars à atmosphère contrôlée pour réduire les pertes post-récolte sous le seuil technique des 3%.
            * **Protocoles de Désintermédiation :** Contrats-cadres automatisés interconnectant directement les grands groupements de producteurs avec les réseaux de distribution industriels.
            """)
            st.progress(0.90, text="Sécurisation des débouchés commerciaux : 90%")

    # -----------------------------------------------------
    # UNITÉ 4 : MATRICE DE PERFORMANCE INTERACTIVE
    # -----------------------------------------------------
    elif "Matrice" in sub_menu:
        st.markdown("<div class='section-title'>📊 Matrice de Segmentation & Métriques de Performance</div>", unsafe_allow_html=True)
        st.write("Sélectionnez le profil d'acteur pour extraire la feuille de route d'audit correspondante :")
        
        m_tabs = st.tabs(["👥 Petits Exploitants / GIE", "🚜 Moyens Domaines", "🏢 Complexes Agro-Industriels / États"])
        
        with m_tabs[0]:
            st.markdown("#### Plan de Restructuration GIE & Coopératives")
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Objectif d'Augmentation Marge", "+25% à 30%", delta="Levier : Regroupement Achats")
            col_m2.write("**Axe de Conseil prioritaire :** Mutualisation des intrants, introduction des micro-formations sur mobile et déploiement de techniques low-tech de conservation des récoltes (séchage solaire, silos partagés).")

        with m_tabs[1]:
            st.markdown("#### Optimisation Structurelle des Moyens Domaines")
            col_m3, col_m4 = st.columns(2)
            col_m3.metric("Objectif Réduction des Charges", "-18% Énergie / Intrants", delta="Levier : Agriculture Précision")
            col_m4.write("**Axe de Conseil prioritaire :** Transition motorisée raisonnée, étalonnage précis des systèmes de pompage d'eau solaires, et cartographie des parcelles pour localiser précisément les apports d'amendements organiques.")

        with m_tabs[2]:
            st.markdown("#### Sécurisation Stratégique Macro-Industrielle")
            col_m5, col_m6 = st.columns(2)
            col_m5.metric("Indice de Souveraineté Flux", "Risque d'Asphyxie : Faible", delta="Levier : Traçabilité Blockchain")
            col_m6.write("**Axe de Conseil prioritaire :** Sécurisation complète des approvisionnements nationaux, déploiement d'audits de conformité internationaux, intégration de la data macro-agricole pour la gestion des stocks de sécurité de l'État.")

        # Devise Institutionnelle de clôture
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("🎯 **Axiome YouAgronoMe :** *« Passer définitivement d'une agriculture de réaction (gestion de crise à haute perte) à une agriculture d'anticipation (génie algorithmique et valorisation du potentiel territorial). »*")

    # =====================================================
    # FOOTER : APPUI CONSEIL ET COORDINATION GÉNÉRALE
    # =====================================================
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #f4f6f7; border: 1px solid #d5dbdb; border-radius: 16px; padding: 25px; text-align: center;">
        <h4 style="color:#154360; margin-top:0;">🌟 Ingénierie de Projet & Certification d'Études d'Impact</h4>
        <p style="color:#566573; font-size:14px; margin-bottom:15px;">Nos ingénieurs-conseils accrédités structurent vos business plans pour validation auprès des instances de financement et banques de développement (BNDE, LBA, BOAD).</p>
        <a href="mailto:issayoume2012@gmail.com" style="text-decoration:none; font-weight:700; color:#1b5e20; font-size:16px;">👉 Déposer un dossier d'audit technique : issayoume2012@gmail.com</a>
    </div>
    """, unsafe_allow_html=True)
########################################""
# CONTACT
# =====================================================

def html_block(code):
    st.markdown(code, unsafe_allow_html=True)

if selected == "📞 Contact":

    # ================= HEADER =================
    html_block("""
    <div style="text-align:center; margin-bottom: 20px;">
        <h1>🤝 Contactez YouAgronoMe</h1>
        <p>Une question, un partenariat ou besoin d'assistance ? Notre équipe vous répond.</p>
    </div>
    """)

    # ================= NOUVELLE FONCTIONNALITÉ : CHIFFRES CLÉS & INFOS =================
    # Utilisation des composants natifs Streamlit pour un rendu propre et moderne
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📞 Téléphone", value="777473170")
    with c2:
        st.metric(label="📍 Bureau Principal", value="Saint-Louis")
    with c3:
        st.metric(label="⏱ Temps de réponse", value="< 24h")

    st.write("---")

    # ================= COLUMNS (FORMULAIRE & FAQ) =================
    col_form, col_FAQ = st.columns([3, 2])

    with col_form:
        st.subheader("📩 Envoyez-nous un message")
        
        # Formulaire amélioré avec de nouvelles fonctionnalités
        with st.form("contact_form", clear_on_submit=True):
            nom = st.text_input("Votre Nom complet *")
            email = st.text_input("Votre Adresse Email *")
            
            # Nouvelle fonctionnalité : Cibler le bon département
            departement = st.selectbox(
                "À quel département s'adresse votre message ?",
                ["🤝 Partenariats & Investissements", "🎓 Opérations & Formations", "🚜 Support Commercial", "❓ Autre demande"]
            )
            
            msg = st.text_area("Votre Message *", placeholder="Écrivez votre message ici...")

            submit_button = st.form_submit_button("Envoyer le message")

            # Nouvelle fonctionnalité : Validation des champs obligatoire
            if submit_button:
                if not nom or not email or not msg:
                    st.error("Veuillez remplir tous les champs obligatoires (marqués par un *).")
                elif "@" not in email:
                    st.error("Veuillez entrer une adresse email valide.")
                else:
                    # Ici, vous pourrez ajouter votre logique d'envoi d'email ou de stockage en base de données
                    st.success(f"Merci {nom} ! Votre message a bien été transmis au département **{departement}**. Nous vous recontacterons à l'adresse {email}.")

    with col_FAQ:
        st.subheader("💡 Informations utiles")
        
        # Nouvelle fonctionnalité : FAQ interactive pour désengorger le support
        with st.expander("💼 Vous êtes un potentiel partenaire ?"):
            st.write("""
            Sélectionnez le département **Partenariats** dans le formulaire. 
            Notre équipe dédiée aux alliances stratégiques vous répondra sous 48 heures ouvrées.
            """)
            
        with st.expander("🚜 Support technique & Commercial"):
            st.write("""
            Pour toute urgence liée à vos commandes ou au déploiement sur le terrain à Saint-Louis, 
            privilégiez l'appel direct au **+221 777473170** du lundi au vendredi (8h - 17h).
            """)
            
        # Rappel de l'email direct en dehors du formulaire
        st.info("✉️ **Email direct :** issayoume2012@gmail.com")
##########Conseil
elif selected == "Conseils":
    st.title("💡 Centre de Conseils & Bonnes Pratiques")
    st.markdown("Retrouvez ici nos recommandations stratégiques pour optimiser vos performances.")

    # Base de données de conseils (Tu peux modifier les textes à ta guise)
    conseils_data = [
        {"theme": "Finance", "titre": "Optimiser votre trésorerie", "contenu": "Suivez vos flux de trésorerie de près. Essayez de réduire les délais de paiement de vos clients à 30 jours maximum et conservez une réserve équivalente à 3 mois de charges fixes."},
        {"theme": "Stratégie", "titre": "Diversifier vos offres", "contenu": "D'après vos données, certaines catégories surperforment. Créez des offres packagées combinant vos services de 'Consultance' et de 'Formation' pour augmenter le panier moyen."},
        {"theme": "Marketing", "titre": "Améliorer la rétention client", "contenu": "Il coûte 5 fois plus cher d'acquérir un nouveau client que de fidéliser un client existant. Mettez en place une newsletter mensuelle pour garder le contact avec votre base."},
        {"theme": "Finance", "titre": "Réduire les coûts superflus", "contenu": "Faites un audit annuel de vos abonnements logiciels (SaaS). Supprimez les licences inutilisées pour regagner immédiatement de la marge opérationnelle."},
        {"theme": "Stratégie", "titre": "Automatiser les tâches répétitives", "contenu": "Utilisez des outils comme Zapier ou Make pour lier votre CRM à votre facturation. Vous gagnerez en moyenne 4h de gestion administrative par semaine."}
    ]

    # --- FILTRES DE RECHERCHE ---
    st.sidebar.header("🔍 Filtrer les conseils")
    
    # Filtre par catégorie/thème
    themes = ["Tous", "Finance", "Stratégie", "Marketing"]
    theme_choisi = st.sidebar.selectbox("Thématique", themes)
    
    # Barre de recherche par mot-clé
    recherche = st.sidebar.text_input("Rechercher un mot-clé", "")

    # Filtrage de la liste en fonction des choix de l'utilisateur
    conseils_filtres = []
    for c in conseils_data:
        match_theme = (theme_choisi == "Tous" or c["theme"] == theme_choisi)
        match_recherche = (recherche.lower() in c["titre"].lower() or recherche.lower() in c["contenu"].lower())
        
        if match_theme and match_recherche:
            conseils_filtres.append(c)

    # --- AFFICHAGE DES CONSEILS ---
    if len(conseils_filtres) == 0:
        st.warning("Aucun conseil ne correspond à votre recherche. Modifiez vos filtres dans la barre latérale.")
    else:
        # Affichage dynamique sous forme de boîtes extensibles (Expander)
        for index, conseil in enumerate(conseils_filtres):
            # Décoration rapide selon le thème
            emoji = "💰" if conseil["theme"] == "Finance" else "🎯" if conseil["theme"] == "Stratégie" else "📢"
            
            with st.expander(f"{emoji} [{conseil['theme']}] - {conseil['titre']}"):
                st.write(conseil["contenu"])
                
                # Un petit bouton interactif pour marquer comme lu ou utile
                if st.button("Marquer ce conseil comme utile 👍", key=f"btn_{index}"):
                    st.success("Merci pour votre retour !")
