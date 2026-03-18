# ============================================================
# MODULE MISE À JOUR
# ============================================================
import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY  = os.getenv("ALLSPORTS_API_KEY")
BASE_URL = "https://apiv2.allsportsapi.com/tennis/"

# ============================================================
# PAGE MISE À JOUR
# ============================================================
def page_mise_a_jour(modeles, df_base):
    st.title("🔄 Mise à jour")
    st.markdown("---")

    st.subheader("📡 Statut de la connexion API")

    col1, col2 = st.columns(2)
    with col1:
        if API_KEY:
            st.success(f"✅ Clé API trouvée : {API_KEY[:10]}...")
        else:
            st.error("❌ Clé API manquante — vérifie le fichier .env")

    with col2:
        if st.button("🔍 Tester la connexion API"):
            try:
                r = requests.get(BASE_URL, params={
                    "met"    : "Fixtures",
                    "APIkey" : API_KEY,
                    "from"   : datetime.now().strftime('%Y-%m-%d'),
                    "to"     : datetime.now().strftime('%Y-%m-%d'),
                }, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    if data.get("success") == 1:
                        nb = len(data.get("result", []))
                        st.success(f"✅ Connexion OK — {nb} matchs trouvés aujourd'hui")
                    else:
                        st.error(f"❌ Erreur API : {data.get('error', 'Inconnue')}")
                else:
                    st.error(f"❌ Erreur HTTP : {r.status_code}")
            except Exception as e:
                st.error(f"❌ Erreur de connexion : {e}")

    st.markdown("---")

    st.subheader("📊 Statut de la base de données")

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.metric("🎾 Matchs en base", "830 906")
    with col_b2:
        st.metric("📅 Dernière mise à jour", "2026")
    with col_b3:
        if df_base is not None:
            st.metric("📁 CSV chargé", f"{len(df_base):,} lignes")
        else:
            st.metric("📁 CSV chargé", "Non disponible")

    st.markdown("---")

    st.subheader("🤖 Statut des modèles IA")

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("🏆 Modèle Vainqueur", f"{modeles.get('acc_win', 0)*100:.1f}%")
    with col_m2:
        st.metric("🔢 Modèle Nb Sets", f"{modeles.get('acc_sets', 0)*100:.1f}%")
    with col_m3:
        st.metric("⚖️ Modèle Handicap", f"{modeles.get('acc_handi', 0)*100:.1f}%")

    st.markdown("---")

    st.subheader("⬆️ Importer de nouveaux matchs")
    st.info("📁 Importez un fichier CSV de nouveaux matchs pour enrichir la base de données")

    fichier = st.file_uploader(
        "Choisir un fichier CSV",
        type=['csv'],
        help="Le fichier doit contenir les colonnes : winner_name, loser_name, surface, tourney_date, score"
    )

    if fichier:
        try:
            df_new = pd.read_csv(fichier)
            st.success(f"✅ {len(df_new)} matchs importés !")
            st.dataframe(df_new.head(5), hide_index=True, use_container_width=True)

            col_imp1, col_imp2 = st.columns(2)
            with col_imp1:
                st.metric("📋 Nouveaux matchs", len(df_new))
            with col_imp2:
                colonnes_requises = ['winner_name', 'loser_name', 'surface', 'tourney_date']
                colonnes_ok = all(c in df_new.columns for c in colonnes_requises)
                if colonnes_ok:
                    st.success("✅ Format correct")
                else:
                    manquantes = [c for c in colonnes_requises if c not in df_new.columns]
                    st.error(f"❌ Colonnes manquantes : {manquantes}")

        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture : {e}")

    st.markdown("---")

    st.subheader("ℹ️ Instructions")
    st.markdown("""
    **Pour mettre à jour les modèles :**
    1. Importez un CSV avec les nouveaux matchs
    2. Vérifiez que le format est correct
    3. Lancez le réentraînement depuis votre PC local
    4. Uploadez le nouveau fichier `modeles_tennis_v2.pkl`

    **Format CSV requis :**
    - `winner_name` — Nom du vainqueur
    - `loser_name` — Nom du perdant
    - `surface` — Hard / Clay / Grass
    - `tourney_date` — Date au format YYYY-MM-DD
    - `score` — Score du match (ex: 6-3 6-4)
    """)