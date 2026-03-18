# ============================================================
# MODULE MISE À JOUR
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
import pickle
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
API_KEY  = os.getenv("ALLSPORTS_API_KEY")
BASE_URL = "https://apiv2.allsportsapi.com/tennis/"
DOSSIER  = os.path.join(os.path.dirname(__file__), '..', 'data')

# ============================================================
# VÉRIFICATION DATE DERNIÈRE MAJ
# ============================================================
def get_derniere_maj():
    fichier = os.path.join(DOSSIER, 'derniere_maj.txt')
    if os.path.exists(fichier):
        with open(fichier, 'r') as f:
            return f.read().strip()
    return "Jamais"

def set_derniere_maj():
    fichier = os.path.join(DOSSIER, 'derniere_maj.txt')
    date    = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(fichier, 'w') as f:
        f.write(date)
    return date

def besoin_maj():
    derniere = get_derniere_maj()
    if derniere == "Jamais":
        return True
    try:
        d = datetime.strptime(derniere, '%Y-%m-%d %H:%M')
        return (datetime.now() - d).days >= 3
    except:
        return True

# ============================================================
# COLLECTE NOUVEAUX MATCHS VIA API
# ============================================================
def collecter_nouveaux_matchs(date_debut, date_fin):
    """Collecte les nouveaux matchs ATP/WTA via API."""
    circuits = ['Atp Singles', 'Wta Singles',
                'Challenger Men Singles',
                'Challenger Women Singles']
    matchs = []
    barre  = st.progress(0)
    total  = len(circuits)

    for i, circuit in enumerate(circuits):
        try:
            res = requests.get(BASE_URL, params={
                "met"    : "Fixtures",
                "APIkey" : API_KEY,
                "from"   : date_debut,
                "to"     : date_fin,
            }, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if data.get("success") == 1:
                    matchs.extend(
                        data.get("result", [])
                    )
        except Exception as e:
            st.warning(f"⚠️ Erreur {circuit} : {e}")
        barre.progress((i + 1) / total)

    return matchs

# ============================================================
# TRAITEMENT NOUVEAUX MATCHS
# ============================================================
def traiter_nouveaux_matchs(matchs_api):
    """Convertit les matchs API en DataFrame unifié."""
    rows = []
    for m in matchs_api:
        if m.get('event_status') != 'Finished':
            continue
        winner = m.get('event_winner', '')
        if 'first' in str(winner).lower():
            winner_name = m.get('event_first_player', '')
            loser_name  = m.get('event_second_player', '')
        else:
            winner_name = m.get('event_second_player', '')
            loser_name  = m.get('event_first_player', '')

        rows.append({
            'tourney_name' : m.get('league_name', ''),
            'tourney_date' : m.get('event_date', ''),
            'surface'      : 'Hard',
            'round'        : m.get('league_round', ''),
            'winner_name'  : winner_name,
            'loser_name'   : loser_name,
            'score'        : m.get('event_final_result', ''),
            'circuit'      : 'ATP',
            'genre'        : 'M',
            'type'         : 'Singles',
        })

    return pd.DataFrame(rows) if rows else pd.DataFrame()

# ============================================================
# PAGE MISE À JOUR
# ============================================================
def page_mise_a_jour(modeles, df_base):
    st.title("🔄 Mise à jour des données")
    st.markdown("---")

    # ── Statut ──
    derniere = get_derniere_maj()
    maj_requise = besoin_maj()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Dernière MAJ", derniere)
    with col2:
        st.metric(
            "⏰ Fréquence recommandée",
            "Tous les 3 jours"
        )
    with col3:
        if maj_requise:
            st.metric("🔔 Statut", "⚠️ MAJ recommandée")
        else:
            st.metric("✅ Statut", "À jour")

    st.markdown("---")

    # ── Option 1 : MAJ via API ──
    st.subheader("🌐 Option 1 — Mise à jour via API")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        date_debut = st.date_input(
            "Date de début",
            value=datetime.now() - timedelta(days=3)
        )
    with col_d2:
        date_fin = st.date_input(
            "Date de fin",
            value=datetime.now()
        )

    if st.button(
        "🔄 Lancer la mise à jour API",
        type="primary",
        width='stretch'
    ):
        with st.spinner("⏳ Collecte des nouveaux matchs..."):
            matchs = collecter_nouveaux_matchs(
                str(date_debut), str(date_fin)
            )

        if matchs:
            df_new = traiter_nouveaux_matchs(matchs)
            st.success(
                f"✅ {len(df_new)} nouveaux matchs collectés !"
            )

            if len(df_new) > 0:
                st.dataframe(
                    df_new.head(10),
                    width='stretch'
                )

                if st.button(
                    "💾 Intégrer dans la base",
                    width='stretch'
                ):
                    chemin_base = os.path.join(
                        DOSSIER, 'BASE_FEATURES.csv'
                    )
                    df_base_updated = pd.concat(
                        [df_base, df_new],
                        ignore_index=True
                    )
                    df_base_updated.to_csv(
                        chemin_base, index=False
                    )
                    set_derniere_maj()
                    st.success(
                        f"✅ Base mise à jour ! "
                        f"{len(df_base_updated):,} matchs total"
                    )
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.warning(
                "⚠️ Aucun nouveau match trouvé "
                "pour cette période"
            )

    st.markdown("---")

    # ── Option 2 : Upload CSV ──
    st.subheader("📁 Option 2 — Upload fichier CSV")
    st.info(
        "Upload un fichier CSV avec les colonnes : "
        "winner_name, loser_name, tourney_date, "
        "surface, score, tourney_name"
    )

    fichier = st.file_uploader(
        "Choisir un fichier CSV",
        type=['csv'],
        key="upload_maj"
    )

    if fichier:
        df_upload = pd.read_csv(fichier)
        st.success(
            f"✅ {len(df_upload)} matchs dans le fichier"
        )
        st.dataframe(
            df_upload.head(5),
            width='stretch'
        )

        col_u1, col_u2 = st.columns(2)
        with col_u1:
            st.write("**Colonnes détectées :**")
            for col in df_upload.columns:
                st.write(f"• {col}")

        with col_u2:
            if st.button(
                "💾 Intégrer dans la base",
                key="btn_integrer_csv",
                width='stretch'
            ):
                chemin_base = os.path.join(
                    DOSSIER, 'BASE_FEATURES.csv'
                )
                df_base_updated = pd.concat(
                    [df_base, df_upload],
                    ignore_index=True
                )
                df_base_updated.to_csv(
                    chemin_base, index=False
                )
                set_derniere_maj()
                st.success(
                    f"✅ {len(df_upload)} matchs intégrés ! "
                    f"Total : {len(df_base_updated):,}"
                )
                st.cache_data.clear()
                st.rerun()

    st.markdown("---")

    # ── Statut base actuelle ──
    st.subheader("📊 Statut de la base actuelle")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.metric("📋 Total matchs", f"{len(df_base):,}")
    with col_b2:
        dates = pd.to_datetime(
            df_base['tourney_date'], errors='coerce'
        ).dropna()
        if len(dates) > 0:
            st.metric(
                "📅 Dernier match",
                str(dates.max())[:10]
            )
    with col_b3:
        nb_joueurs = len(modeles.get('elo_final', {}))
        st.metric("👤 Joueurs", f"{nb_joueurs:,}")