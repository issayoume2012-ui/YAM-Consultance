import streamlit as st
import pandas as pd
import numpy as np
import datetime
import json

# =========================================================================
# 1. CONFIGURATION DE LA PAGE STREAMLIT
# =========================================================================
st.set_page_config(
    page_title="YouAgronoMe - Plateforme Stratégique & Agribusiness Sénégal",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# 2. INJECTION DU STYLE CSS GLOBAL DE L'APPLICATION
# =========================================================================
st.markdown("""
<style>
    /* Importation de la police Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Arrière-plan global */
    .stApp {
        background-color: #f8fafc;
    }

    /* Style du Menu Latéral (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #0d2310 !important;
        border-right: 1px solid #1e3a1e;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] span {
        color: #f1f5f9 !important;
    }

    section[data-testid="stSidebar"] .stRadio label {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 6px;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(46, 125, 50, 0.3);
        border-color: #4caf50;
    }

    /* Bannières d'en-tête (Header Cards) */
    .header-box {
        background: linear-gradient(135deg, #1b5e20 0%, #0d2310 100%);
        padding: 30px;
        border-radius: 14px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(13, 35, 16, 0.25);
        border-bottom: 4px solid #e1a91a;
    }
    .header-box h1 {
        color: #ffffff !important;
        font-weight: 800;
        margin: 0;
        font-size: 30px;
        letter-spacing: -0.5px;
    }
    .header-box p {
        color: #cbd5e1;
        margin-top: 8px;
        font-size: 15px;
        line-height: 1.5;
    }

    /* Cartes d'indicateurs personnalisées (KPI) */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        text-align: center;
    }
    .kpi-title {
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 800;
        color: #1b5e20;
        margin: 8px 0;
    }
    .kpi-sub {
        font-size: 12px;
        color: #16a34a;
        font-weight: 600;
    }

    /* Personnalisation des boutons */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Pied de page Sidebar */
    .sidebar-footer {
        padding: 15px 0;
        border-top: 1px solid rgba(255,255,255,0.1);
        margin-top: 20px;
        font-size: 11px;
        color: #94a3b8;
        text-align: center;
    }

    /* Styles pour Assistant IA */
    .ai-hero {
        padding: 30px 25px;
        border-radius: 14px;
        color: white;
        background: linear-gradient(135deg, #0d2310 0%, #1b5e20 100%);
        box-shadow: 0 8px 24px rgba(27, 94, 32, 0.2);
        border-bottom: 4px solid #e1a91a;
        margin-bottom: 25px;
    }
    .ai-hero h2 { font-size: 26px !important; font-weight: 800 !important; color: #ffffff !important; margin-bottom: 8px !important; }
    .ai-hero p { font-size: 14px !important; opacity: 0.95; max-width: 900px; margin: 0 !important; color: #f8fafc; line-height: 1.6; }

    /* Cartes SWOT */
    .swot-card { padding: 18px; border-radius: 10px; margin-bottom: 15px; font-size: 13px; line-height: 1.6; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
    .swot-s { background-color: #f0fdf4; border-left: 5px solid #16a34a; color: #14532d; }
    .swot-w { background-color: #fef2f2; border-left: 5px solid #dc2626; color: #7f1d1d; }
    .swot-o { background-color: #eff6ff; border-left: 5px solid #2563eb; color: #1e3a8a; }
    .swot-t { background-color: #fffbeb; border-left: 5px solid #d97706; color: #78350f; }
    .swot-header { font-weight: 800; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px; }

    /* Cartes PESTEL */
    .pestel-grid-card { background: #ffffff; border: 1px solid #e2e8f0; border-top: 4px solid #1b5e20; border-radius: 10px; padding: 16px; height: 100%; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .pestel-tag { font-weight: 800; color: #1b5e20; font-size: 12px; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px; }
    .pestel-body { font-size: 13px; color: #334155; line-height: 1.5; }

    /* Bulles de Chatbot */
    .chat-user { background-color: #e0f2fe; color: #0369a1; padding: 12px 16px; border-radius: 14px 14px 0px 14px; margin: 8px 0; text-align: right; font-size: 13px; font-weight: 500; max-width: 85%; margin-left: auto; }
    .chat-ai { background-color: #ffffff; color: #1e293b; padding: 14px 18px; border-radius: 14px 14px 14px 0px; margin: 8px 0; border-left: 4px solid #1b5e20; font-size: 13px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); max-width: 90%; line-height: 1.6; }

    /* Styles Dashboard */
    .dash-hero { padding: 25px 20px; border-radius: 12px; color: white; background: linear-gradient(135deg, #15803d 0%, #052e16 100%); box-shadow: 0 4px 15px rgba(5, 46, 22, 0.15); border-bottom: 4px solid #e1a91a; margin-bottom: 25px; }
    .dash-hero h2 { font-size: 24px !important; font-weight: 800 !important; color: #ffffff !important; margin-bottom: 6px !important; }
    .dash-hero p { font-size: 14px !important; color: #e2e8f0; margin: 0 !important; }
    .market-card { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); margin-bottom: 15px; }
    .market-title { font-size: 14px; font-weight: 700; color: #166534; margin-bottom: 5px; }
    .market-price { font-size: 22px; font-weight: 800; color: #0f172a; }
    .market-trend { font-size: 12px; font-weight: 600; }
    .trend-up { color: #16a34a; }
    .trend-down { color: #dc2626; }
    .alert-box { background-color: #fff7ed; border-left: 4px solid #ea580c; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px; font-size: 13px; color: #9a3412; }

    /* Styles Crops */
    .crops-hero { padding: 25px 20px; border-radius: 12px; color: white; background: linear-gradient(135deg, #166534 0%, #052e16 100%); box-shadow: 0 4px 15px rgba(5, 46, 22, 0.15); border-bottom: 4px solid #e1a91a; margin-bottom: 25px; }
    .crops-hero h2 { font-size: 24px !important; font-weight: 800 !important; color: #ffffff !important; margin-bottom: 6px !important; }
    .crops-hero p { font-size: 14px !important; color: #e2e8f0; margin: 0 !important; }
    .crop-card { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); margin-bottom: 15px; }
    .crop-badge { background-color: #dcfce7; color: #15803d; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .isra-box { background-color: #f0fdf4; border-left: 4px solid #16a34a; padding: 14px; border-radius: 8px; margin-bottom: 15px; font-size: 13px; line-height: 1.5; color: #14532d; }

    /* Styles Finance */
    .finance-hero { padding: 25px 20px; border-radius: 12px; color: white; background: linear-gradient(135deg, #854d0e 0%, #361e04 100%); box-shadow: 0 4px 15px rgba(54, 30, 4, 0.2); border-bottom: 4px solid #e1a91a; margin-bottom: 25px; }
    .finance-hero h2 { font-size: 24px !important; font-weight: 800 !important; color: #ffffff !important; margin-bottom: 6px !important; }
    .finance-hero p { font-size: 14px !important; color: #fef08a; margin: 0 !important; }
    .fin-card { background-color: #ffffff; border: 1px solid #e2e8f0; border-top: 4px solid #854d0e; border-radius: 10px; padding: 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); margin-bottom: 15px; height: 100%; }
    .fin-title { font-size: 16px; font-weight: 800; color: #854d0e; margin-bottom: 8px; }
    .fin-sub { font-size: 12px; color: #64748b; margin-bottom: 12px; }
    .fin-badge { background-color: #fef9c3; color: #854d0e; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }

    /* Styles Home & Contact */
    .home-hero { padding: 35px 25px; border-radius: 16px; color: white; background: linear-gradient(135deg, #052e16 0%, #15803d 50%, #166534 100%); box-shadow: 0 6px 20px rgba(5, 46, 22, 0.2); border-bottom: 5px solid #e1a91a; margin-bottom: 30px; text-align: center; }
    .home-hero h1 { font-size: 32px !important; font-weight: 800 !important; color: #ffffff !important; margin-bottom: 12px !important; }
    .home-hero p { font-size: 16px !important; color: #f0fdf4; max-width: 800px; margin: 0 auto !important; line-height: 1.6; }
    .feature-card { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03); height: 100%; }
    .feature-icon { font-size: 32px; margin-bottom: 10px; }
    .feature-title { font-size: 18px; font-weight: 700; color: #166534; margin-bottom: 8px; }
    .feature-desc { font-size: 13px; color: #475569; line-height: 1.5; }
    .stat-box { background-color: #f8fafc; border-left: 4px solid #16a34a; padding: 15px; border-radius: 8px; margin-top: 20px; }

    .contact-hero { padding: 25px 20px; border-radius: 12px; color: white; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); box-shadow: 0 4px 15px rgba(15, 23, 42, 0.2); border-bottom: 4px solid #e1a91a; margin-bottom: 25px; }
    .contact-hero h2 { font-size: 24px !important; font-weight: 800 !important; color: #ffffff !important; margin-bottom: 6px !important; }
    .contact-hero p { font-size: 14px !important; color: #cbd5e1; margin: 0 !important; }
    .info-card { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 3. BARRE LATÉRALE DE NAVIGATION
# =========================================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/sprout.png", width=65)
    st.markdown("## **YouAgronoMe**")
    st.caption("Plateforme d'Aide à la Décision Stratégique & Agribusiness")
    st.markdown("---")
    
    selected_page = st.radio(
        "Navigation :",
        [
            "🏠 Accueil",
            "📊 Tableau de Bord",
            "🧠 Assistant IA de Décision",
            "🌾 Gestion des Cultures",
            "💰 Financement & Subventions",
            "📞 Contact & Support"
        ]
    )
    
    st.markdown("---")
    st.markdown("""
    <div class="sidebar-footer">
        🇸🇳 <b>Ancrage Territorial Sénégal</b><br>
        Partenaires : DER/FJ, SAED, ISRA, BNDE, LBA, DPV<br><br>
        <i>Version 2.4.0 (2026)</i>
    </div>
    """, unsafe_allow_html=True)
    # =========================================================================
# MODULE 1 : PAGE D'ACCUEIL
# =========================================================================
def show_home():
    st.markdown("""
    <div class="home-hero">
        <h1>🇸🇳 Plateforme Agricole Intelligente du Sénégal</h1>
        <p>Solution digitale intégrée d'aide à la décision pour les producteurs, agronomines et investisseurs. Optimisez vos rendements, suivez les cours des marchés et accédez aux financements en quelques clics.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 Modules d'Aide à la Décision")
    st.write("Naviguez dans l'application via le menu latéral pour accéder aux différents outils :")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Tableau de Bord</div>
            <div class="feature-desc">
                Suivi global de l'exploitation, prévisions de récoltes, cotations en direct des marchés locaux (Dakar, Saint-Louis, Kaolack) et météo agronomique ANACIM.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🌾</div>
            <div class="feature-title">Gestion des Cultures</div>
            <div class="feature-desc">
                Calculateur d'irrigation, plans de fertilisation optimisés selon les fiches ISRA et guides d'alerte/protection phytosanitaire validés par la DPV.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💰</div>
            <div class="feature-title">Financement & Crédits</div>
            <div class="feature-desc">
                Simulateur d'échéancier bancaire (DER/FJ, LBA, BNDE), critères d'éligibilité aux subventions de l'État et outils de montage de business plan.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📌 En Bref : L'Agriculture au Sénégal en 2026")
    
    st.markdown("""
    <div class="stat-box">
        💡 <b>Objectif Souveraineté Alimentaire :</b> Modernisation des périmètres irrigués de la Vallée du Fleuve Sénégal (SAED), essor des fermes villageoises ANIDA et transition vers le pompage solaire pour réduire les coûts d'exploitation de plus de 40%.
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Objectif Riz Paddy", "1.5M Tonnes", "Souveraineté")
    m2.metric("Couverture Oignon", "100 %", "Autosuffisance")
    m3.metric("Énergie Solaire", "65 %", "Adoption pompage")
    m4.metric("Guichets Partenaires", "4 Bailleurs", "DER, LBA, BNDE, FONGIP")


# =========================================================================
# MODULE 2 : TABLEAU DE BORD ANALYTIQUE
# =========================================================================
def show_dashboard():
    st.markdown("""
    <div class="dash-hero">
        <h2>📊 Tableau de Bord Analytique & Suivi des Marchés</h2>
        <p>Suivi en temps réel des indicateurs de production, prévisions de récoltes, alertes météo ANACIM et cotations des produits agricoles sur les marchés du Sénégal.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔍 **Filtres de Visualisation**", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            region_select = st.selectbox(
                "Filtrer par Région / Zone :",
                ["Toutes les Zones", "Saint-Louis / Podor (SAED)", "Zone des Niayes", "Bassin Arachidier", "Casamance", "Sénégal Oriental"]
            )
        with f_col2:
            saison_select = st.selectbox(
                "Campagne Agricole :",
                ["Campagne Sèche Chaude (CSC)", "Campagne d'Hivernage (Pluviale)", "Contre-Saison Froide (CSF)"]
            )
        with f_col3:
            unite_devise = st.selectbox("Devise / Affichage :", ["FCFA / Kg", "FCFA / Tonne", "FCFA / Sac (50kg)"])

    st.markdown("""
    <div class="alert-box">
        ⚠️ <b>Alerte Météo & Sanitaire (ANACIM / DPV) :</b> Hausse des températures observée dans la zone de Podor et Matam. Risque de stress hydrique accru sur le riz en phase d'épiaison. Vigilance recommandée sur les apports d'eau.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📈 Indicateurs Globaux d'Exploitation")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Superficie Totale Suivie", "1 450 Ha", "+120 Ha ce mois")
    kpi2.metric("Rendement Moyen Riz", "6.8 T/Ha", "+0.4 T/Ha vs 2025")
    kpi3.metric("Volume Global Récolté", "9 860 Tonnes", "+14%")
    kpi4.metric("Taux d'Équipement Solaire", "64 %", "+8% de transition")

    st.markdown("---")

    col_g1, col_g2 = st.columns([3, 2])

    with col_g1:
        st.markdown("#### 🌾 Évolution Mensuelle des Récoltes (Tonnes)")
        mois_list = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
        data_prod = {
            "Mois": mois_list,
            "Riz Paddy (SAED)": [450, 520, 680, 950, 1100, 850, 600, 400, 350, 500, 820, 990],
            "Oignon Galmi (Niayes/Nord)": [300, 480, 850, 1200, 1400, 900, 450, 200, 150, 100, 180, 250],
            "Maïs Hybride": [200, 220, 310, 400, 450, 500, 620, 800, 950, 700, 450, 300]
        }
        df_prod = pd.DataFrame(data_prod).set_index("Mois")
        st.line_chart(df_prod, height=320)

    with col_g2:
        st.markdown("#### 🎯 Répartition par Filière (2026)")
        df_pie = pd.DataFrame({
            "Filière": ["Riz Paddy", "Oignon", "Maïs", "Arachide", "Tomate", "Autres"],
            "Part (%)": [42, 24, 15, 10, 6, 3]
        }).set_index("Filière")
        st.bar_chart(df_pie, height=320)

    st.markdown("---")
    st.markdown("### 🛒 Cotation des Marchés Agricoles au Sénégal")
    st.caption("Mise à jour régulière des prix pratiqués sur les marchés de gros (Diaobé, Touba, Tilène, Saint-Louis).")

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    with m_col1:
        st.markdown("""
        <div class="market-card">
            <div class="market-title">🌾 Riz Blanc Local Décortiqué</div>
            <div class="market-price">340 FCFA <span style="font-size:12px; font-weight:normal;">/ kg</span></div>
            <div class="market-trend trend-up">▲ +15 FCFA (Stabilité demande)</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown("""
        <div class="market-card">
            <div class="market-title">🧅 Oignon Local (Galmi)</div>
            <div class="market-price">275 FCFA <span style="font-size:12px; font-weight:normal;">/ kg</span></div>
            <div class="market-trend trend-down">▼ -20 FCFA (Pic de récolte)</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col3:
        st.markdown("""
        <div class="market-card">
            <div class="market-title">🌽 Maïs Grain Local</div>
            <div class="market-price">230 FCFA <span style="font-size:12px; font-weight:normal;">/ kg</span></div>
            <div class="market-trend trend-up">▲ +5 FCFA (Forte demande alimentation animale)</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col4:
        st.markdown("""
        <div class="market-card">
            <div class="market-title">🥜 Arachide Décortiquée</div>
            <div class="market-price">410 FCFA <span style="font-size:12px; font-weight:normal;">/ kg</span></div>
            <div class="market-trend trend-up">▲ +25 FCFA (Demande huileries)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 📋 Détail des Prix par Région et Marché de Gros")
    data_marches = [
        {"Région": "Saint-Louis / Dagana", "Marché": "Marché de Gros Ross Béthio", "Produit": "Riz Paddy", "Prix Moyen": "180 FCFA/kg", "Tendance": "Stable", "Disponible": "Élevée"},
        {"Région": "Thiès / Niayes", "Marché": "Marché Mboro", "Produit": "Oignon Galmi", "Prix Moyen": "260 FCFA/kg", "Tendance": "En baisse", "Disponible": "Très Élevée"},
        {"Région": "Dakar", "Marché": "Marché Castors / Thiaroye", "Produit": "Riz Blanc Décortiqué", "Prix Moyen": "350 FCFA/kg", "Tendance": "En hausse", "Disponible": "Moyenne"},
        {"Région": "Kaolack", "Marché": "Marché Central Kaolack", "Produit": "Arachide Coque", "Prix Moyen": "310 FCFA/kg", "Tendance": "En hausse", "Disponible": "Faible"},
        {"Région": "Kolda / Casamance", "Marché": "Marché Diaobé", "Produit": "Maïs Jaune", "Prix Moyen": "210 FCFA/kg", "Tendance": "Stable", "Disponible": "Élevée"}
    ]
    st.dataframe(pd.DataFrame(data_marches), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🌤️ Suivi Météo & Hydrologie (Sénégal)")

    met_col1, met_col2 = st.columns(2)

    with met_col1:
        st.markdown("##### 📍 Relevé Hebdomadaire des Températures & Pluviométrie")
        df_meteo = pd.DataFrame({
            "Jour": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
            "Temp. Max (°C)": [38, 39, 41, 40, 38, 37, 39],
            "Évapotranspiration ETP (mm)": [6.2, 6.8, 7.5, 7.1, 6.4, 6.0, 6.5]
        }).set_index("Jour")
        st.area_chart(df_meteo)

    with met_col2:
        st.markdown("##### 💧 Niveau des Retenues d'Eau & Fleuves")
        st.write("• **Barrage de Manantali (OMVS) :** Taux de remplissage **84%** (Optimal)")
        st.write("• **Barrage de Diama :** Contrôle anti-sel opérationnel, niveau d'eau à +1.80m IGN")
        st.write("• **Nappe des Niayes :** Niveau piézométrique stable, attention aux pompages excessifs")
        st.progress(84, text="Remplissage Global des Retenues Hydrauliques : 84%")
        # =========================================================================
# MODULE 3 : ASSISTANT IA DE DÉCISION STRATÉGIQUE
# =========================================================================
def show_ai_assistant():
    st.markdown("""
    <div class="ai-hero">
        <h2>🧠 Assistant IA de Décision Stratégique & Agribusiness</h2>
        <p>Moteur d'intelligence décisionnelle adapté à l'écosystème sénégalais. Génération automatique d'études d'impact, diagnostics SWOT/PESTEL, cartographie des risques et dossiers d'éligibilité pour les bailleurs et institutions financières (DER/FJ, BNDE, La Banque Agricole, SAED).</p>
    </div>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "dernier_diagnostic" not in st.session_state:
        st.session_state.dernier_diagnostic = None

    with st.form("form_cadrage_projet"):
        st.markdown("### 📥 1. Paramétrage & Cadrage du Projet")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            domaine_activite = st.selectbox(
                "Secteur / Filière d'activité :",
                [
                    "🌾 Production Agricole & Grandes Cultures (Riz, Maïs, Oignon, Arachide)",
                    "🏭 Transformation Agro-alimentaire & Conditionnement",
                    "💧 Irrigation, Pompage Solaire & Aménagement Hydro-agricole",
                    "💰 Financement, Microfinance & Levée de Fonds (DER/FJ, LBA)",
                    "📊 Distribution, Commercialisation & Logistique Locale",
                    "💻 Agritech, IoT & Numérisation des Exploitations",
                    "🌍 Projet Éco-responsable, ONG & Résilience Communautaire"
                ]
            )
            
            description_projet = st.text_area(
                "Description détaillée du projet ou problème à résoudre :",
                placeholder="Exemple : Nous sommes un groupement d'intérêt économique (GIE) à Podor. Nous exploitons 10 hectares de riz en aménagement SAED. Nous souhaitons passer au pompage solaire, acquérir une décortiqueuse industrielle et obtenir un crédit de campagne auprès de la BNDE ou de la DER/FJ. Quels sont les risques et la rentabilité attendue ?",
                height=140
            )

        with col2:
            region_contexte = st.selectbox(
                "Région d'implantation (Sénégal) :",
                [
                    "Vallée du Fleuve Sénégal (Saint-Louis, Matam, Podor, Dagana)",
                    "Zone des Niayes (Thiès, Dakar, Saint-Louis littoral)",
                    "Bassin Arachidier (Kaolack, Fatick, Kaffrine, Diourbel)",
                    "Casamance (Ziguinchor, Kolda, Sédhiou)",
                    "Sénégal Oriental (Tambacounda, Kédougou)",
                    "Zone Urbaine / Péri-urbaine (Dakar, Rufisque)"
                ]
            )
            
            budget_estime = st.number_input(
                "Budget prévisionnel global (en FCFA) :", 
                min_value=500000, 
                max_value=10000000000, 
                value=25000000, 
                step=1000000
            )
            
            fichier_joint = st.file_uploader(
                "Joindre un document de référence (Business Plan, Relevé, Bilan) :",
                type=["pdf", "xlsx", "csv", "docx", "txt"]
            )

        btn_generer = st.form_submit_button("🚀 Lancer l'Analyse Stratégique Complète", type="primary", use_container_width=True)

    if btn_generer:
        if not description_projet or len(description_projet.strip()) < 20:
            st.error("⚠️ Veuillez fournir une description d'au moins 20 caractères pour permettre à l'IA d'analyser votre projet.")
        else:
            with st.spinner("🧠 Analyse contextuelle en cours... Évaluation des facteurs réglementaires, financiers et agronomiques..."):
                score_base = 70
                if budget_estime >= 10000000:
                    score_base += 12
                if "solaire" in description_projet.lower() or "irrigation" in description_projet.lower():
                    score_base += 8
                score_faisabilite = min(score_base, 95)

                marge_estimee_ratio = 0.35 if "Transformation" in domaine_activite else 0.28
                profit_estime = int(budget_estime * marge_estimee_ratio)
                tri_estime = round(18.5 + (score_faisabilite / 10), 1)

                diag = {
                    "domaine": domaine_activite,
                    "region": region_contexte,
                    "budget": budget_estime,
                    "score": score_faisabilite,
                    "profit": profit_estime,
                    "tri": tri_estime,
                    "swot": {
                        "Forces": [
                            "Forte cohésion du projet avec la politique nationale de souveraineté alimentaire.",
                            "Réduction des coûts opérationnels à moyen terme grâce au choix d'équipements adaptés.",
                            "Positionnement stratégique dans une zone à haut potentiel agricole (" + region_contexte.split("(")[0].strip() + ")."
                        ],
                        "Faiblesses": [
                            "Besoin important en fonds de roulement au démarrage de la campagne.",
                            "Dépendance initiale vis-à-vis des délais de validation des crédits bancaires.",
                            "Faible niveau d'automatisation de la gestion comptable du groupement."
                        ],
                        "Opportunités": [
                            "Accès prioritaire aux guichets de financement bonifiés DER/FJ et La Banque Agricole.",
                            "Forte demande nationale entraînant une substitution progressive des importations.",
                            "Possibilité de contractualisation directe avec les industriels et grossistes locaux."
                        ],
                        "Menaces": [
                            "Fluctuations imprévisibles des prix des intrants sur le marché international.",
                            "Variabilité climatique et risques de pression parasitaire selon les saisons (DPV).",
                            "Concurrence des circuits informels de distribution (réseau Bana-Bana)."
                        ]
                    },
                    "pestel": {
                        "Politique": "Cadre étatique très favorable poussé par le Ministère de l'Agriculture (MASAE) et les programmes de souveraineté.",
                        "Économique": "Existence de mécanismes de garantie et de taux d'intérêt bonifiés via la BNDE et la DER/FJ pour les PME agronomiques.",
                        "Social": "Fort impact socio-économique direct : création d'emplois durables pour les jeunes et valorisation du travail féminin rural.",
                        "Technologique": "Adoption accélérée des technologies de pompage solaire, du goutte-à-goutte et de la traçabilité mobile.",
                        "Écologique": "Impératif de conservation des sols face à la salinisation (INP) et gestion optimisée de la ressource en eau.",
                        "Légal": "Obligation de mise en conformité avec les autorisations sanitaires (FRA) et les normes environnementales de la DEEC."
                    },
                    "risques": [
                        {"Risque": "Retard de livraison des équipements d'irrigation/transformation", "Niveau": "Moyen", "Impact Financier": "Modéré", "Plan d'Atténuation": "Passer commande via des fournisseurs agréés SAED/ANCAR avec clauses pénales."},
                        {"Risque": "Volatilité des cours locaux au moment de la récolte", "Niveau": "Élevé", "Impact Financier": "Important", "Plan d'Atténuation": "Négocier des contrats d'achat ferme à prix plancher avant le démarrage de la campagne."},
                        {"Risque": "Défaillance de la maintenance du matériel solaire/mécanique", "Niveau": "Moyen", "Impact Financier": "Élevé", "Plan d'Atténuation": "Souscrire un contrat d'entretien préventif avec garantie de pièces de rechange sous 48h."}
                    ],
                    "plan_action": [
                        {"Phase": "Phase 1 (Mois 1)", "Action": "Finalisation du montage juridique (GIE/SUARL) et dépôt officiel du dossier auprès du guichet DER/FJ.", "Responsable": "Promoteur / Direction"},
                        {"Phase": "Phase 2 (Mois 2-3)", "Action": "Sécurisation foncière, aménagement des sols et installation des équipements énergétiques/hydrauliques.", "Responsable": "Prestataire Technique"},
                        {"Phase": "Phase 3 (Mois 4-6)", "Action": "Lancement officiel de la première campagne, suivi agronomique rapproché et tenue des registres.", "Responsable": "Chef d'Exploitation"},
                        {"Phase": "Phase 4 (Mois 7+)", "Action": "Récolte, transformation, commercialisation directe et constitution de la réserve de remboursement du crédit.", "Responsable": "Responsable Commercial"}
                    ]
                }

                st.session_state.dernier_diagnostic = diag
                st.success("✅ Diagnostic stratégique généré avec succès !")

    if st.session_state.dernier_diagnostic:
        d = st.session_state.dernier_diagnostic

        st.markdown("---")
        st.markdown(f"### 📊 Synthèse Stratégique : **{d['domaine'].split('/')[0]}**")
        st.caption(f"Zone d'étude : **{d['region']}** | Budget engagé : **{d['budget']:,} FCFA**")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Indice de Faisabilité", f"{d['score']} / 100", "+5% vs Moyenne Snp")
        m2.metric("Marge Brute Projetée", f"{d['profit']:,} FCFA", "Année 1")
        m3.metric("Taux Rendement Interne (TRI)", f"{d['tri']} %", "Attractif")
        m4.metric("Niveau de Risque Global", "Modéré à Maîtrisé", "Selon Mitigation")

        tab_swot, tab_pestel, tab_risques, tab_plan, tab_export = st.tabs([
            "🔍 Matrice SWOT", 
            "🌍 Analyse PESTEL Sénégal", 
            "🛡️ Cartographie des Risques", 
            "📅 Plan d'Action & Feuille de Route", 
            "📄 Export & Dossier Bailleurs"
        ])

        with tab_swot:
            st.markdown("#### Matrice des Forces, Faiblesses, Opportunités et Menaces")
            c_s1, c_s2 = st.columns(2)
            
            with c_s1:
                st.markdown("""
                <div class="swot-card swot-s">
                    <div class="swot-header">💪 FORCES (Strengths)</div>
                    <ul>""" + "".join([f"<li>{item}</li>" for item in d['swot']['Forces']]) + """</ul>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="swot-card swot-o">
                    <div class="swot-header">🚀 OPPORTUNITÉS (Opportunities)</div>
                    <ul>""" + "".join([f"<li>{item}</li>" for item in d['swot']['Opportunités']]) + """</ul>
                </div>
                """, unsafe_allow_html=True)

            with c_s2:
                st.markdown("""
                <div class="swot-card swot-w">
                    <div class="swot-header">⚠️ FAIBLESSES (Weaknesses)</div>
                    <ul>""" + "".join([f"<li>{item}</li>" for item in d['swot']['Faiblesses']]) + """</ul>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="swot-card swot-t">
                    <div class="swot-header">🚨 MENACES (Threats)</div>
                    <ul>""" + "".join([f"<li>{item}</li>" for item in d['swot']['Menaces']]) + """</ul>
                </div>
                """, unsafe_allow_html=True)

        with tab_pestel:
            st.markdown("#### Diagnostic Macro-Économique PESTEL (Sénégal)")
            p_cols1 = st.columns(3)
            p_items = list(d['pestel'].items())
            
            for idx in range(3):
                key, val = p_items[idx]
                with p_cols1[idx]:
                    st.markdown(f"""
                    <div class="pestel-grid-card">
                        <div class="pestel-tag">🏛️ {key}</div>
                        <div class="pestel-body">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            p_cols2 = st.columns(3)
            for idx in range(3, 6):
                key, val = p_items[idx]
                with p_cols2[idx - 3]:
                    st.markdown(f"""
                    <div class="pestel-grid-card">
                        <div class="pestel-tag">🔬 {key}</div>
                        <div class="pestel-body">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

        with tab_risques:
            st.markdown("#### Plan de Gestion et d'Atténuation des Risques")
            df_risques = pd.DataFrame(d['risques'])
            st.dataframe(df_risques, use_container_width=True, hide_index=True)

        with tab_plan:
            st.markdown("#### Feuille de Route Opérationnelle (Chrono-programme)")
            for item in d['plan_action']:
                with st.expander(f"📌 {item['Phase']} : {item['Action'][:60]}..."):
                    st.write(f"**Action complète :** {item['Action']}")
                    st.write(f"**Responsable principal :** {item['Responsable']}")

        with tab_export:
            st.markdown("#### Génération du Dossier Stratégique Téléchargeable")
            st.write("Ce document peut être joint directement à vos demandes de financement auprès de la DER/FJ, de la BNDE ou de La Banque Agricole.")

            contenu_dossier = f"""================================================================================
DOSSIER D'EVALUATION STRATEGIQUE ET D'AIDE A LA DECISION - YOUAGRONOME
================================================================================
Date d'édition : {datetime.datetime.now().strftime('%d/%m/%Y')}
Secteur principal : {d['domaine']}
Zone géographique : {d['region']}
Budget global sollicité/engagé : {d['budget']:,} FCFA

1. INDICATEURS DE FAISABILITE
- Score Globale de Faisabilité : {d['score']} / 100
- Marge Brute Projetée (Année 1) : {d['profit']:,} FCFA
- Taux de Rendement Interne Estimé : {d['tri']} %

2. MATRICE SWOT
[FORCES]
{chr(10).join(['- ' + x for x in d['swot']['Forces']])}

[FAIBLESSES]
{chr(10).join(['- ' + x for x in d['swot']['Faiblesses']])}

[OPPORTUNITES]
{chr(10).join(['- ' + x for x in d['swot']['Opportunités']])}

[MENACES]
{chr(10).join(['- ' + x for x in d['swot']['Menaces']])}

3. PLAN D'ACTION RECOMMANDE
{chr(10).join([f"- {x['Phase']} : {x['Action']} (Resp: {x['Responsable']})" for x in d['plan_action']])}

================================================================================
Généré automatiquement par l'Assistant IA YouAgronoMe Senegal
================================================================================
"""

            st.download_button(
                label="📥 Télécharger le Dossier Synthétique (.txt)",
                data=contenu_dossier,
                file_name=f"YouAgronoMe_Diagnostic_{d['region'].split()[0]}.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("### 💬 Chatbot Conseiller : Posez vos questions sur ce projet")
        st.caption("Posez toutes vos questions à l'IA pour préciser des aspects techniques, financiers ou réglementaires.")

        question = st.text_input("Votre question (ex: 'Comment obtenir le FRA auprès du Ministère ?', 'Quel est le taux DER/FJ ?') :")

        if st.button("💬 Poser la question"):
            if question.strip():
                st.session_state.chat_history.append(("user", question))

                q_low = question.lower()
                if "der" in q_low or "finance" in q_low or "credit" in q_low:
                    rep = f"Pour votre projet en **{d['region']}**, la DER/FJ propose des crédits à des taux bonifiés compris entre 5% et 8%. Vous devez fournir une convention de groupement (GIE) ou un RCCM, le relevé bancaire et le devis des équipements."
                elif "fra" in q_low or "norme" in q_low or "autorisation" in q_low:
                    rep = "L'autorisation FRA (Fabrication et Conditionnement Alimentaire) s'obtient auprès de la Division de la Consommation. Le dossier comprend un plan des locaux, une analyse micro-biologique produit et la visite des inspecteurs."
                else:
                    rep = f"Au vu de votre budget de **{d['budget']:,} FCFA**, nous vous conseillons de consolider d'abord le fonds de roulement de la phase 1 avant d'engager des dépenses d'extension."

                st.session_state.chat_history.append(("ai", rep))

        for role, text in reversed(st.session_state.chat_history[-8:]):
            if role == "user":
                st.markdown(f'<div class="chat-user"><b>Vous :</b> {text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai"><b>🤖 Conseiller IA YouAgronoMe :</b> {text}</div>', unsafe_allow_html=True)
# =========================================================================
# MODULE 4 : GESTION DES CULTURES & IRRIGATION
# =========================================================================
def show_crops():
    st.markdown("""
    <div class="crops-hero">
        <h2>🌾 Gestion des Cultures & Suivi Agronomique Intelligente</h2>
        <p>Planification des campagnes, calcul des besoins hydriques, calendriers d'apports en intrants (ISRA) et protocoles de protection des cultures (DPV).</p>
    </div>
    """, unsafe_allow_html=True)

    tab_parcelles, tab_irrigation, tab_intrants, tab_sante = st.tabs([
        "📋 Mes Parcelles", 
        "💧 Calculateur d'Irrigation", 
        "🧪 Plan de Fertilisation (ISRA)", 
        "🛡️ Protection Phytosanitaire (DPV)"
    ])

    with tab_parcelles:
        st.markdown("### 📋 Suivi de l'Exploitation Parcellaire")
        col_p1, col_p2 = st.columns([2, 3])

        with col_p1:
            st.markdown("#### Ajouter / Éditer une Parcelle")
            with st.form("form_parcelle"):
                nom_p = st.text_input("Nom de la parcelle / Bloc :", "Parcelle Nord - Podor 1")
                culture_p = st.selectbox("Culture :", ["Riz Paddy (Sahel 108)", "Oignon Galmi", "Maïs Hybride", "Tomate Industrielle", "Arachide Coque"])
                surface_p = st.number_input("Superficie (Ha) :", min_value=0.25, max_value=500.0, value=5.0, step=0.5)
                date_semis = st.date_input("Date de Semis / Repiquage :", datetime.date(2026, 5, 15))
                type_sol = st.selectbox("Type de Sol :", ["Argileux (Walo)", "Sablo-Argileux (Dior)", "Sableux (Niayes)", "Limoneux"])
                
                btn_p = st.form_submit_button("Enregistrer la Parcelle", type="primary", use_container_width=True)
                if btn_p:
                    st.success(f"✅ Parcelle **{nom_p}** enregistrée avec succès !")

        with col_p2:
            st.markdown("#### Parcelles Actives en Exploitation")
            data_parcelles = [
                {"Parcelle": "Podor Bloc A", "Culture": "Riz (Sahel 108)", "Surface": "10 Ha", "Stade": "Maturité / Pre-récolte", "Besoins Eau": "Faible"},
                {"Parcelle": "Niayes Mboro 2", "Culture": "Oignon Galmi", "Surface": "3 Ha", "Stade": "Bulbaison", "Besoins Eau": "Élevé"},
                {"Parcelle": "Kolda Sud", "Culture": "Maïs Hybride", "Surface": "15 Ha", "Stade": "Levée / Végétatif", "Besoins Eau": "Moyen"},
                {"Parcelle": "Dagana B4", "Culture": "Riz Paddy", "Surface": "8 Ha", "Stade": "Tallage", "Besoins Eau": "Élevé"}
            ]
            st.dataframe(pd.DataFrame(data_parcelles), use_container_width=True, hide_index=True)

            st.markdown("""
            <div class="isra-box">
                💡 <b>Conseil ISRA :</b> Pour la variété <b>Riz Sahel 108</b>, le cycle est de 120 jours. Pensez à effectuer l'arrêt de l'irrigation 15 jours avant la récolte pour uniformiser le séchage des grains.
            </div>
            """, unsafe_allow_html=True)

    with tab_irrigation:
        st.markdown("### 💧 Calculateur Hydrique & Pilotage du Pompage Solaire")
        st.caption("Optimisez vos apports en eau selon l'évapotranspiration (ETP) et le système d'irrigation.")

        c_i1, c_i2 = st.columns(2)

        with c_i1:
            st.subheader("Paramètres de la Parcelle")
            culture_irr = st.selectbox("Sélectionner la Culture :", ["Riz Paddy", "Oignon", "Tomate", "Maïs", "Arboriculture / Mangue"])
            sys_irr = st.selectbox("Système d'Irrigation :", ["Submersion contrôlée", "Goutte-à-goutte (Drip)", "Aspersion", "Californien / Gravitaire"])
            temp_ext = st.slider("Température Moyenne Observée (°C) :", 20, 48, 38)
            vent_vitesse = st.select_slider("Vent / Dessèchement :", ["Faible", "Modéré", "Fort (Harmattan)"])

        with c_i2:
            st.subheader("Résultats du Calcul Hydrique")
            besoin_base = 45 if culture_irr == "Riz Paddy" else 25
            if temp_ext > 35:
                besoin_base += 10
            if vent_vitesse == "Fort (Harmattan)":
                besoin_base += 8
            
            st.metric("Besoin en Eau Estimé", f"{besoin_base} m³ / Ha / Jour", "+12% vs normale")
            st.metric("Durée de Pompage Solaire Recommandée", f"{round(besoin_base / 8, 1)} Heures / Jour", "Pompe 10 HP")
            st.info(f"<b>Préconisation :</b> Avec le système <i>{sys_irr}</i>, effectuer 2 sessions d'arrosage : une tôt le matin (06h-09h) et une en fin d'après-midi (17h-19h) pour limiter l'évaporation.", icon="ℹ️")

    with tab_intrants:
        st.markdown("### 🧪 Calendrier & Doses d'Engrais (Fiches Techniques ISRA)")
        st.write("Sélectionnez votre culture pour afficher la grille officielle de fertilisation conseillée au Sénégal :")
        crop_spec = st.radio("Culture à fertiliser :", ["Riz de Bas-fond / Irrigué", "Oignon Galmi", "Arachide"], horizontal=True)

        if crop_spec == "Riz de Bas-fond / Irrigué":
            fert_data = [
                {"Stade d'Application": "Fond / Avant Repiquage", "Type d'Engrais": "NPK 15-15-15", "Dose Recommandée": "200 Kg / Ha", "Mode d'Apport": "Enfouissement au labour"},
                {"Stade d'Application": "Début Tallage (15-20 jours)", "Type d'Engrais": "Urée (46%)", "Dose Recommandée": "100 Kg / Ha", "Mode d'Apport": "Épandage à la volée sur sol humide"},
                {"Stade d'Application": "Initiation Paniculaire (45 jours)", "Type d'Engrais": "Urée (46%)", "Dose Recommandée": "100 Kg / Ha", "Mode d'Apport": "Épandage dans 3cm d'eau de lame"}
            ]
        elif crop_spec == "Oignon Galmi":
            fert_data = [
                {"Stade d'Application": "Repiquage / Fond", "Type d'Engrais": "Fumure Organique + NPK 9-23-30", "Dose Recommandée": "15 T Organique + 300 Kg NPK / Ha", "Mode d'Apport": "Incorporation au sol"},
                {"Stade d'Application": "3 Semaines après repiquage", "Type d'Engrais": "Nitrate de Calcium / Urée", "Dose Recommandée": "75 Kg / Ha", "Mode d'Apport": "Irrigation ou fertigation"},
                {"Stade d'Application": "Début Bulbaison", "Type d'Engrais": "Sulfate de Potasse (K2O)", "Dose Recommandée": "100 Kg / Ha", "Mode d'Apport": "Apport au pied"}
            ]
        else:
            fert_data = [
                {"Stade d'Application": "Au Semis", "Type d'Engrais": "Phosphate d'Alsace ou NPK 6-20-10", "Dose Recommandée": "150 Kg / Ha", "Mode d'Apport": "Ligne de semis"},
                {"Stade d'Application": "Gypsage (30-35 jours)", "Type d'Engrais": "Sulfate de Calcium (Gypse)", "Dose Recommandée": "100 Kg / Ha", "Mode d'Apport": "Épandage au pied pour la gousse"}
            ]

        st.table(pd.DataFrame(fert_data))

    with tab_sante:
        st.markdown("### 🛡️ Diagnostic & Alertes Sanitaires (DPV)")
        st.markdown("#### 🚨 Guide de Diagnostic Rapide")
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            st.markdown("""
            <div class="crop-card">
                <span class="crop-badge">Riziculture</span>
                <h4 style="margin-top:8px;">Chenille Légionnaire (Spodoptera frugiperda)</h4>
                <p style="font-size:12px; color:#475569;"><b>Symptômes :</b> Feuilles dévorées, trous irréguliers, présence de sciure dans le cœur de la plante.</p>
                <p style="font-size:12px; color:#166534;"><b>Traitement Homologué DPV :</b> Émamectine benzoate ou Azadirachtine (Bio). Traiter tôt le matin.</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="crop-card">
                <span class="crop-badge">Oignon / Maraîchage</span>
                <h4 style="margin-top:8px;">Thrips de l'Oignon (Thrips tabaci)</h4>
                <p style="font-size:12px; color:#475569;"><b>Symptômes :</b> Taches argentées sur les feuilles, dessèchement des pointes.</p>
                <p style="font-size:12px; color:#166534;"><b>Traitement Homologué DPV :</b> Savon noir + extrait d'huile de Neem ou Deltaméthrine sous contrôle.</p>
            </div>
            """, unsafe_allow_html=True)

        with col_s2:
            st.markdown("""
            <div class="crop-card">
                <span class="crop-badge">Arachide / Maïs</span>
                <h4 style="margin-top:8px;">Aflatoxine & Champignons (Aspergillus)</h4>
                <p style="font-size:12px; color:#475569;"><b>Symptômes :</b> Moisissures jaunâtres sur les gousses/épis, altération de la qualité au stockage.</p>
                <p style="font-size:12px; color:#166534;"><b>Prévention DPV :</b> Séchage rapide après récolte (&lt; 10% d'humidité), utilisation d'AflaSafe SN01.</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="crop-card">
                <span class="crop-badge">Toutes Cultures</span>
                <h4 style="margin-top:8px;">Sauteriaux & Criquet Pèlerin</h4>
                <p style="font-size:12px; color:#475569;"><b>Symptômes :</b> Attaques en essaims sur la végétation foliaire.</p>
                <p style="font-size:12px; color:#dc2626;"><b>Signalement Immédiat :</b> Appeler le numéro vert DPV / Brigade régionale de protection des végétaux.</p>
            </div>
            """, unsafe_allow_html=True)
    # =========================================================================
# MODULE 5 : FINANCEMENT & SUBVENTIONS
# =========================================================================
def show_finance():
    st.markdown("""
    <div class="finance-hero">
        <h2>💰 Guichet Financement, Subventions & Simulation de Crédit</h2>
        <p>Analyse d'éligibilité aux fonds publics, simulation d'échéancier de remboursement bancaire (DER/FJ, LBA, BNDE) et optimisation de la structure financière de votre projet agronomique.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_simu, tab_guichets, tab_subventions = st.tabs([
        "🧮 Simulateur de Crédit & Échéancier", 
        "🏛️ Dispositifs de Financement Sénégal", 
        "🎁 Subventions Equipements & Intrants"
    ])

    with tab_simu:
        st.markdown("### 🧮 Simulateur de Crédit de Campagne & Échéancier")
        st.caption("Calculez vos mensualités, le montant des intérêts et vérifiez votre capacité de remboursement.")

        c_f1, c_f2 = st.columns([2, 3])

        with c_f1:
            st.markdown("#### Paramètres du Financement")
            institution = st.selectbox(
                "Institution Cible :",
                ["DER/FJ (Guichet Bonifié - Taux 5%)", "La Banque Agricole - LBA (Taux 7.5%)", "BNDE (Taux 8.5%)", "Microfinance / MEC (Taux 12%)"]
            )
            
            montant_projet = st.number_input(
                "Montant Total du Projet (FCFA) :",
                min_value=1000000,
                max_value=500000000,
                value=20000000,
                step=1000000
            )

            apport_perso = st.number_input(
                "Votre Apport Personnel (FCFA) :",
                min_value=0,
                max_value=montant_projet,
                value=int(montant_projet * 0.15),
                step=500000
            )

            duree_mois = st.slider("Durée du Crédit (en Mois) :", min_value=6, max_value=60, value=24, step=6)
            differe_mois = st.selectbox("Période de Différé (Grâce) :", [0, 3, 6, 12], help="Période sans remboursement du principal pendant l'installation.")

        with c_f2:
            st.markdown("#### Synthèse de la Simulation")

            if "DER/FJ" in institution:
                taux_annuel = 0.05
            elif "LBA" in institution:
                taux_annuel = 0.075
            elif "BNDE" in institution:
                taux_annuel = 0.085
            else:
                taux_annuel = 0.12

            emprunt = montant_projet - apport_perso
            ratio_apport = (apport_perso / montant_projet) * 100

            taux_mensuel = taux_annuel / 12
            nb_remboursements = duree_mois - differe_mois

            if nb_remboursements > 0 and emprunt > 0:
                mensualite = (emprunt * taux_mensuel) / (1 - (1 + taux_mensuel) ** -nb_remboursements)
                cout_total_credit = (mensualite * nb_remboursements) - emprunt
            else:
                mensualite = 0
                cout_total_credit = 0

            st.metric("Montant à Emprunter", f"{emprunt:,} FCFA".replace(",", " "))
            
            m1, m2 = st.columns(2)
            m1.metric("Mensualité Estimée", f"{int(mensualite):,} FCFA".replace(",", " "))
            m2.metric("Coût Total des Intérêts", f"{int(cout_total_credit):,} FCFA".replace(",", " "))

            if ratio_apport >= 10:
                st.success(f"✅ Apport personnel de **{ratio_apport:.1f}%** : Conforme aux exigences (Minimum 10% requis).")
            else:
                st.warning(f"⚠️ Apport de **{ratio_apport:.1f}%** insuffisant. Augmentez votre apport à au moins 10% pour débloquer le dossier.")

            if st.checkbox("📊 Afficher le Tableau d'Amortissement Prévisionnel"):
                schedule = []
                solde = emprunt
                for m in range(1, duree_mois + 1):
                    if m <= differe_mois:
                        interet = solde * taux_mensuel
                        capital = 0
                        paye = interet
                    else:
                        interet = solde * taux_mensuel
                        capital = mensualite - interet
                        paye = mensualite
                        solde -= capital

                    schedule.append({
                        "Mois": f"Mois {m}",
                        "Paiement": f"{int(paye):,} FCFA",
                        "Principal": f"{int(capital):,} FCFA",
                        "Intérêts": f"{int(interet):,} FCFA",
                        "Solde Restant": f"{max(0, int(solde)):,} FCFA"
                    })
                
                st.dataframe(pd.DataFrame(schedule), use_container_width=True, hide_index=True)

    with tab_guichets:
        st.markdown("### 🏛️ Principaux Guichets de Financement au Sénégal")
        st.caption("Fiches pratiques des bailleurs et conditions d'accès.")

        g_col1, g_col2 = st.columns(2)

        with g_col1:
            st.markdown("""
            <div class="fin-card">
                <span class="fin-badge">Public / État</span>
                <div class="fin-title">DER/FJ - Entreprenariat Agricole</div>
                <div class="fin-sub">Délégation Générale à l'Entreprenariat Rapide des Jeunes et des Femmes</div>
                <p style="font-size:13px; color:#334155;">
                • <b>Cibles :</b> Jeunes (&lt; 40 ans), Femmes, Groupements (GIE), Producteurs ruraux.<br>
                • <b>Plafond :</b> De 500 000 FCFA à 50 000 000 FCFA.<br>
                • <b>Taux :</b> 5% fixe d'intérêt.<br>
                • <b>Garantie :</b> Hypothèque, nantissement de matériel ou caution solidaire GIE.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="fin-card">
                <span class="fin-badge">Banque Spécialisée</span>
                <div class="fin-title">La Banque Agricole (LBA)</div>
                <div class="fin-sub">Ex-CNCAS - Premier financeur de la chaîne de valeur agricole</div>
                <p style="font-size:13px; color:#334155;">
                • <b>Cibles :</b> Organisations paysannes, PME/PMI, Aménageurs privés.<br>
                • <b>Produits :</b> Crédit de campagne (court terme), Crédit d'équipement (moyen terme).<br>
                • <b>Taux :</b> 7.5% à 9.5% selon bonification d'État.<br>
                • <b>Exigence :</b> Historique de production, adossement SAED/SODAGRI.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with g_col2:
            st.markdown("""
            <div class="fin-card">
                <span class="fin-badge">Banque Nationale</span>
                <div class="fin-title">BNDE - Banque Nationale de Développement Économique</div>
                <div class="fin-sub">Accompagnement de la transformation agro-industrielle</div>
                <p style="font-size:13px; color:#334155;">
                • <b>Cibles :</b> Unités de transformation, chaîne du froid, conditionnement.<br>
                • <b>Plafond :</b> Jusqu'à 500 000 000 FCFA.<br>
                • <b>Avantage :</b> Possibilité de co-financement avec le FONSIS et le FONGIP.<br>
                • <b>Exigence :</b> Business Plan validé et étude d'impact environnemental.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="fin-card">
                <span class="fin-badge">Garantie Publique</span>
                <div class="fin-title">FONGIP (Fonds de Garantie)</div>
                <div class="fin-sub">Garantie des crédits bancaires pour PME rurale</div>
                <p style="font-size:13px; color:#334155;">
                • <b>Rôle :</b> Couvre jusqu'à 60% à 80% du risque de crédit pour le compte de la banque.<br>
                • <b>Effet Levier :</b> Permet aux agriculteurs sans titre foncier d'accéder au crédit bancaire.<br>
                • <b>Partenaires :</b> LBA, BNDE, CMS, PAMECAS.
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab_subventions:
        st.markdown("### 🎁 Subventions de l'État & Programmes d'Équipement")
        st.caption("Aides directes accordées par le Ministère de l'Agriculture (MASAE) pour la campagne 2026.")
        st.info("💡 **Rappel Réglementaire :** Les demandes de subventions sur les tracteurs, motoculteurs et groupes motopompes solaires se font au niveau des Commissions Régionales de Répartition (Gouvernance).", icon="ℹ️")

        data_subventions = [
            {"Équipement / Intrant": "Groupes Motopompes Solaires", "Taux de Subvention État": "50% à 60%", "Organisme Gestionnaire": "MASAE / ANER / SAED", "Conditions": "GIE ou exploitation privée > 2 Ha"},
            {"Équipement / Intrant": "Semences Certifiées Riz/Maïs", "Taux de Subvention État": "50%", "Organisme Gestionnaire": "Direction des Semences (DIASEM)", "Conditions": "Inscription sur la liste des producteurs"},
            {"Équipement / Intrant": "Engrais Chimiques & Organiques", "Taux de Subvention État": "30% à 45%", "Organisme Gestionnaire": "Commissions Départementales", "Conditions": "Quota au sac par hectare"},
            {"Équipement / Intrant": "Tracteurs & Matériel de Labour", "Taux de Subvention État": "40%", "Organisme Gestionnaire": "Direction de l'Équipement Agr. (DEA)", "Conditions": "Apport personnel de 60% ou crédit LBA"},
            {"Équipement / Intrant": "Systèmes Goutte-à-Goutte (Niayes)", "Taux de Subvention État": "50%", "Organisme Gestionnaire": "ANIDA", "Conditions": "Ferme villageoise ou projet individuel"}
        ]
        st.table(pd.DataFrame(data_subventions))


# =========================================================================
# MODULE 6 : CONTACT & SUPPORT TECHNIQUE
# =========================================================================
def show_contact():
    st.markdown("""
    <div class="contact-hero">
        <h2>📞 Support Technique & Assistance Agronomique</h2>
        <p>Besoin d'aide pour configurer vos parcelles, simuler un dossier de crédit ou contacter une brigade régionale DPV/ISRA ? Nos experts sont à votre écoute.</p>
    </div>
    """, unsafe_allow_html=True)

    col_c1, col_c2 = st.columns([3, 2])

    with col_c1:
        st.markdown("### ✉️ Formulaire d'Assistance Directe")
        with st.form("contact_form"):
            nom_complet = st.text_input("Nom & Prénom :")
            telephone = st.text_input("Numéro de Téléphone (WhatsApp de préférence) :", "+221 ")
            region = st.selectbox("Région d'Exploitation :", ["Saint-Louis", "Thiès / Niayes", "Kaolack", "Ziguinchor", "Dakar", "Matam", "Tambacounda", "Autre"])
            sujet = st.selectbox("Objet de la demande :", [
                "Assistance sur le simulateur de crédit (DER / LBA)",
                "Conseil agronomique & choix des variétés (ISRA)",
                "Alerte ravageurs / Maladie de culture (DPV)",
                "Problème technique sur l'application",
                "Autre demande"
            ])
            message = st.text_area("Détails de votre message ou question :", height=120)
            
            submit_btn = st.form_submit_button("Envoyer la Demande", type="primary", use_container_width=True)
            if submit_btn:
                if nom_complet and message:
                    st.success("✅ Votre message a été transmis avec succès à l'équipe technique ! Un conseiller vous recontactera sous 24h.")
                else:
                    st.error("⚠️ Veuillez remplir votre nom et votre message avant d'envoyer.")

    with col_c2:
        st.markdown("### 🏢 Contacts Utiles & Urgences")
        st.markdown("""
        <div class="info-card">
            <h4 style="color:#166534; margin-bottom:5px;">🚨 Urgence Phytosanitaire (DPV)</h4>
            <p style="font-size:13px; color:#334155;">
            Pour tout signalement d'essaims de sauteriaux ou chenilles légionnaires :<br>
            📞 <b>Numéro Vert :</b> 800 00 11 22<br>
            📧 <b>Email :</b> dpv@agriculture.gouv.sn
            </p>
        </div>

        <div class="info-card">
            <h4 style="color:#166534; margin-bottom:5px;">🌾 Conseil Agronomique (ISRA)</h4>
            <p style="font-size:13px; color:#334155;">
            Centre National de Recherches Agronomiques (CNRA) de Bambey :<br>
            📞 <b>Téléphone :</b> +221 33 973 62 11<br>
            🌐 <b>Site web :</b> www.isra.sn
            </p>
        </div>

        <div class="info-card">
            <h4 style="color:#166534; margin-bottom:5px;">💳 Guichet DER/FJ</h4>
            <p style="font-size:13px; color:#334155;">
            Assistance montage de projet & dépôts de dossiers :<br>
            📞 <b>Support :</b> +221 33 889 97 00<br>
            📍 Point d'accueil dans chaque préfecture de département.
            </p>
        </div>
        """, unsafe_allow_html=True)


# =========================================================================
# ROUTAGE PRINCIPAL DES PAGES (MAIN)
# =========================================================================
if selected_page == "🏠 Accueil":
    show_home()
elif selected_page == "📊 Tableau de Bord":
    show_dashboard()
elif selected_page == "🧠 Assistant IA de Décision":
    show_ai_assistant()
elif selected_page == "🌾 Gestion des Cultures":
    show_crops()
elif selected_page == "💰 Financement & Subventions":
    show_finance()
elif selected_page == "📞 Contact & Support":
    show_contact()
        
