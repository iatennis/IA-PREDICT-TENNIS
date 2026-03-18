# ============================================================
# MODULE HISTORIQUE
# ============================================================
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

FICHIER_HISTORIQUE = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'historique.json'
)

# ============================================================
# CHARGEMENT HISTORIQUE
# ============================================================
def charger_historique():
    if not os.path.exists(FICHIER_HISTORIQUE):
        return []
    try:
        with open(FICHIER_HISTORIQUE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# ============================================================
# SAUVEGARDE HISTORIQUE
# ============================================================
def sauvegarder_historique(historique):
    with open(FICHIER_HISTORIQUE, 'w', encoding='utf-8') as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

# ============================================================
# PAGE HISTORIQUE
# ============================================================
def page_historique():
    st.title("📚 Historique des prédictions")
    st.markdown("---")

    historique = charger_historique()

    if not historique:
        st.info(
            "📭 Aucune prédiction enregistrée pour l'instant."
            "\n\nFais ta première prédiction dans l'onglet 🎾 Prédiction !"
        )
        return

    # ── Résumé ──
    total     = len(historique)
    avec_res  = [h for h in historique if h.get('resultat_reel')]
    corrects  = [
        h for h in avec_res
        if h.get('resultat_reel') == h.get('vainqueur')
    ]
    pct_ok    = (
        round(len(corrects) / len(avec_res) * 100, 1)
        if avec_res else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Total prédictions", total)
    with col2:
        st.metric("✅ Résultats saisis", len(avec_res))
    with col3:
        st.metric("🎯 Prédictions correctes", len(corrects))
    with col4:
        st.metric("📊 Précision réelle", f"{pct_ok}%")

    st.markdown("---")

    # ── Tableau historique ──
    st.subheader("📋 Toutes les prédictions")

    rows = []
    for i, h in enumerate(reversed(historique)):
        rows.append({
            'ID'            : total - i,
            'Date'          : h.get('date', 'N/A'),
            'Joueur A'      : h.get('joueur_a', 'N/A'),
            'Joueur B'      : h.get('joueur_b', 'N/A'),
            'Surface'       : h.get('surface', 'N/A'),
            'Tournoi'       : h.get('tournoi', 'N/A'),
            'IA prédit'     : h.get('vainqueur', 'N/A'),
            'Probabilité'   : f"{h.get('proba_v', 0)}%",
            'Score prédit'  : h.get('score_exact', 'N/A'),
            'Sets prédits'  : h.get('nb_sets', 'N/A'),
            'Résultat réel' : h.get('resultat_reel', '❓ Non saisi'),
            'Correct'       : (
                '✅' if h.get('resultat_reel') == h.get('vainqueur')
                else ('❌' if h.get('resultat_reel') else '❓')
            ),
        })

    df_hist = pd.DataFrame(rows)
    st.dataframe(
        df_hist, hide_index=True,
        width='stretch'
    )

    st.markdown("---")

    # ── Saisie résultat réel ──
    st.subheader("✏️ Saisir le résultat réel")
    st.info(
        "Après le match, saisis le vrai vainqueur "
        "pour affiner l'IA !"
    )

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        id_pred = st.number_input(
            "ID de la prédiction",
            min_value=1,
            max_value=total,
            value=total,
            step=1
        )
    with col_r2:
        # Trouve la prédiction correspondante
        pred = historique[total - id_pred]
        choix_vainqueur = st.selectbox(
            "Vrai vainqueur",
            [pred['joueur_a'], pred['joueur_b']]
        )

    score_reel = st.text_input(
        "Score réel (optionnel)",
        placeholder="Ex: 6-3 6-4",
        key="score_reel"
    )

    if st.button(
        "💾 Enregistrer le résultat",
        type="primary",
        width='stretch'
    ):
        historique[total - id_pred]['resultat_reel'] = choix_vainqueur
        if score_reel:
            historique[total - id_pred]['score_reel'] = score_reel
        sauvegarder_historique(historique)
        st.success(
            f"✅ Résultat enregistré ! "
            f"Vainqueur réel : {choix_vainqueur}"
        )
        st.rerun()

    st.markdown("---")

    # ── Analyse par surface ──
    if avec_res:
        st.subheader("📊 Précision par surface")
        surfaces = {}
        for h in avec_res:
            surf = h.get('surface', 'Unknown')
            if surf not in surfaces:
                surfaces[surf] = {'total': 0, 'correct': 0}
            surfaces[surf]['total'] += 1
            if h.get('resultat_reel') == h.get('vainqueur'):
                surfaces[surf]['correct'] += 1

        surf_rows = []
        for surf, stats in surfaces.items():
            pct = round(
                stats['correct'] / stats['total'] * 100, 1
            )
            surf_rows.append({
                'Surface'   : surf,
                'Total'     : stats['total'],
                'Corrects'  : stats['correct'],
                'Précision' : f"{pct}%"
            })

        st.dataframe(
            pd.DataFrame(surf_rows),
            hide_index=True,
            width='stretch'
        )

    # ── Export ──
    st.markdown("---")
    st.subheader("📥 Exporter l'historique")
    if st.button("⬇️ Télécharger en CSV"):
        csv = df_hist.to_csv(index=False)
        st.download_button(
            label     = "📥 Télécharger CSV",
            data      = csv,
            file_name = f"historique_predictions_"
                        f"{datetime.now().strftime('%Y%m%d')}.csv",
            mime      = "text/csv"
        )