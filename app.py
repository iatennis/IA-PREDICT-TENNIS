# ============================================================
# TENNIS IA — Application principale
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION PAGE
# ============================================================
st.set_page_config(
    page_title            = "🎾 Tennis IA",
    page_icon             = "🎾",
    layout                = "wide",
    initial_sidebar_state = "collapsed"
)

# ============================================================
# CSS PERSONNALISÉ — Vert gazon moderne
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0a1628 100%);
    color: #ffffff;
}

.main-header {
    background: linear-gradient(90deg, #1a6b3a 0%, #2d9e56 50%, #1a6b3a 100%);
    padding: 20px 30px;
    border-radius: 16px;
    margin-bottom: 24px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(45,158,86,0.3);
    animation: slideDown 0.6s ease-out;
}
@keyframes slideDown {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.main-header h1 { color:#ffffff; font-size:2.5rem; font-weight:700; margin:0; }
.main-header p  { color:rgba(255,255,255,0.85); font-size:1rem; margin:6px 0 0 0; }

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px; padding: 6px; gap: 4px;
    border: 1px solid rgba(45,158,86,0.2);
}
.stTabs [data-baseweb="tab"] {
    background: transparent; color: rgba(255,255,255,0.6);
    border-radius: 8px; padding: 10px 20px;
    font-weight: 500; transition: all 0.3s ease; border: none;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(45,158,86,0.2); color: #ffffff;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#1a6b3a,#2d9e56) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(45,158,86,0.4);
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(45,158,86,0.3);
    border-radius: 12px; padding: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(45,158,86,0.2);
}
[data-testid="metric-container"] label {
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.85rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #4ade80 !important;
    font-weight: 700 !important;
    font-size: 1.4rem !important;
}

.stButton > button {
    background: linear-gradient(135deg,#1a6b3a,#2d9e56);
    color: white; border: none; border-radius: 10px;
    padding: 12px 24px; font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(45,158,86,0.3);
}
.stButton > button:hover {
    background: linear-gradient(135deg,#2d9e56,#3dbf6e);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(45,158,86,0.5);
}

/* ── INPUTS — texte visible ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background: rgba(15, 40, 30, 0.95) !important;
    border: 1px solid rgba(45,158,86,0.5) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    caret-color: #4ade80 !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #2d9e56 !important;
    box-shadow: 0 0 0 2px rgba(45,158,86,0.3) !important;
}
input::placeholder, textarea::placeholder {
    color: rgba(255,255,255,0.35) !important;
}

/* ── SELECTBOX ── */
.stSelectbox > div > div,
[data-baseweb="select"] > div {
    background: rgba(15, 40, 30, 0.95) !important;
    border: 1px solid rgba(45,158,86,0.5) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}
[data-baseweb="select"] span {
    color: #ffffff !important;
}

/* ── DROPDOWN OPTIONS ── */
[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: #0d2137 !important;
    border: 1px solid rgba(45,158,86,0.3) !important;
    border-radius: 10px !important;
}
[role="option"] {
    background: #0d2137 !important;
    color: #ffffff !important;
}
[role="option"]:hover,
[aria-selected="true"] {
    background: rgba(45,158,86,0.25) !important;
    color: #4ade80 !important;
}

/* ── DATE INPUT ── */
[data-testid="stDateInput"] input {
    background: rgba(15,40,30,0.95) !important;
    color: #ffffff !important;
    border: 1px solid rgba(45,158,86,0.5) !important;
}

/* ── CHECKBOX ── */
[data-testid="stCheckbox"] label {
    color: #ffffff !important;
}

/* ── ALERTS ── */
.stSuccess {
    background: rgba(45,158,86,0.15) !important;
    border: 1px solid rgba(45,158,86,0.4) !important;
    border-radius: 10px !important;
    color: #4ade80 !important;
}
.stError {
    background: rgba(239,68,68,0.15) !important;
    border: 1px solid rgba(239,68,68,0.4) !important;
    border-radius: 10px !important;
}
.stInfo {
    background: rgba(59,130,246,0.15) !important;
    border: 1px solid rgba(59,130,246,0.4) !important;
    border-radius: 10px !important;
}
.stWarning {
    background: rgba(245,158,11,0.15) !important;
    border: 1px solid rgba(245,158,11,0.4) !important;
    border-radius: 10px !important;
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(45,158,86,0.2);
}

hr { border-color: rgba(45,158,86,0.2) !important; }
label { color: rgba(255,255,255,0.8) !important; font-weight:500 !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
::-webkit-scrollbar-thumb { background: #2d9e56; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# REDÉFINITION simplifier_round
# ============================================================
def simplifier_round(r):
    r = str(r).upper()
    if 'QUARTER' in r or 'QF' in r: return 4
    if 'SEMI'    in r or 'SF' in r: return 5
    if r in ['F','FINAL','THE FINAL']: return 6
    if 'R128' in r: return 1
    if 'R64'  in r: return 2
    if 'R32'  in r: return 3
    if 'R16'  in r: return 3
    if 'RR'   in r: return 3
    return 3

# ============================================================
# CHARGEMENT DES MODÈLES
# ============================================================
@st.cache_resource
def charger_modeles():
    chemin = os.path.join(
        os.path.dirname(__file__), 'data', 'modeles_tennis_v2.pkl'
    )
    with open(chemin, 'rb') as f:
        modeles = pickle.load(f)
    modeles['simplifier_round'] = simplifier_round
    return modeles

@st.cache_data
def charger_base():
    chemin = os.path.join(
        os.path.dirname(__file__), 'data', 'BASE_FEATURES.csv'
    )
    return pd.read_csv(chemin, low_memory=False)

# ============================================================
# CHARGEMENT DONNÉES
# ============================================================
with st.spinner("⏳ Chargement de Tennis IA..."):
    try:
        modeles = charger_modeles()
        df_base = charger_base()
        CHARGE  = True
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        CHARGE  = False

# ============================================================
# HEADER PRINCIPAL
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🎾 Tennis IA</h1>
    <p>Intelligence Artificielle de Prédictions Tennis
    · ATP · WTA · Challengers · ITF · 830 000+ matchs</p>
</div>
""", unsafe_allow_html=True)

# ── Stats rapides ──
if CHARGE:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            "👤 Joueurs",
            f"{len(modeles.get('elo_final',{})):,}"
        )
    with col2:
        st.metric(
            "🏆 Vainqueur",
            f"{modeles.get('acc_win',0)*100:.1f}%"
        )
    with col3:
        st.metric(
            "🔢 Nb Sets",
            f"{modeles.get('acc_sets',0)*100:.1f}%"
        )
    with col4:
        st.metric(
            "⚖️ Handicap",
            f"{modeles.get('acc_handi',0)*100:.1f}%"
        )
    with col5:
        st.metric("📊 Matchs analysés", "830 906")

    st.markdown("---")

# ============================================================
# ONGLETS NAVIGATION — 6 onglets
# ============================================================
if CHARGE:
    from modules.prediction     import page_prediction
    from modules.joueurs        import page_joueurs
    from modules.historique     import page_historique
    from modules.mise_a_jour    import page_mise_a_jour
    from modules.performance    import page_performance
    from modules.matchs_du_jour import page_matchs_jour

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📅 Matchs du jour",
        "🎾 Prédiction",
        "👤 Joueurs",
        "🔄 Mise à jour",
        "📚 Historique",
        "📊 Performance IA"
    ])

    with tab1:
        page_matchs_jour(modeles, df_base)
    with tab2:
        page_prediction(modeles, df_base)
    with tab3:
        page_joueurs(modeles, df_base)
    with tab4:
        page_mise_a_jour(modeles, df_base)
    with tab5:
        page_historique()
    with tab6:
        page_performance()

else:
    st.error("❌ Impossible de charger les modèles.")
    st.info(
        "Vérifie que ces fichiers sont dans le dossier data/ :"
        "\n- modeles_tennis_v2.pkl"
        "\n- BASE_FEATURES.csv"
    )