# ============================================================
# MODULE PERFORMANCE IA
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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
# PAGE PERFORMANCE
# ============================================================
def page_performance():
    st.title("📊 Performance de l'IA")
    st.markdown("---")

    historique = charger_historique()
    avec_res   = [
        h for h in historique
        if h.get('resultat_reel')
    ]

    if not avec_res:
        st.info(
            "📭 Pas encore assez de données.\n\n"
            "Pour voir les statistiques :\n"
            "1. Fais des prédictions dans l'onglet 🎾\n"
            "2. Saisis les résultats réels dans 📚\n"
            "3. Reviens ici pour voir les stats !"
        )

        # Affiche quand même les stats du modèle entraîné
        st.markdown("---")
        st.subheader("📈 Performance du modèle entraîné")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "🏆 Précision Vainqueur",
                "67.8%",
                "+17.8% vs hasard"
            )
        with col2:
            st.metric(
                "🔢 Précision Nb Sets",
                "70.9%",
                "+45.9% vs hasard"
            )
        with col3:
            st.metric(
                "⚖️ Précision Handicap",
                "69.5%",
                "+36.5% vs hasard"
            )
        return

    # ── Métriques globales ──
    total    = len(avec_res)
    corrects = [
        h for h in avec_res
        if h.get('resultat_reel') == h.get('vainqueur')
    ]
    pct_ok   = round(len(corrects) / total * 100, 1)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Prédictions testées", total)
    with col2:
        st.metric("✅ Correctes", len(corrects))
    with col3:
        st.metric("❌ Incorrectes", total - len(corrects))
    with col4:
        delta = round(pct_ok - 50, 1)
        st.metric(
            "🎯 Précision globale",
            f"{pct_ok}%",
            f"+{delta}% vs hasard"
        )

    st.markdown("---")

    # ── Graphique évolution précision ──
    st.subheader("📈 Évolution de la précision")

    resultats_cumul = []
    correct_cumul   = 0
    for i, h in enumerate(avec_res):
        if h.get('resultat_reel') == h.get('vainqueur'):
            correct_cumul += 1
        pct = round(correct_cumul / (i + 1) * 100, 1)
        resultats_cumul.append({
            'Prédiction' : i + 1,
            'Précision'  : pct,
        })

    df_cumul = pd.DataFrame(resultats_cumul)
    fig_evol = go.Figure()
    fig_evol.add_trace(go.Scatter(
        x    = df_cumul['Prédiction'],
        y    = df_cumul['Précision'],
        mode = 'lines+markers',
        name = 'Précision cumulative',
        line = dict(color='#2196F3', width=2),
    ))
    fig_evol.add_hline(
        y          = 50,
        line_dash  = "dash",
        line_color = "gray",
        annotation_text = "Baseline hasard (50%)"
    )
    fig_evol.add_hline(
        y          = 67.8,
        line_dash  = "dot",
        line_color = "green",
        annotation_text = "Modèle entraîné (67.8%)"
    )
    fig_evol.update_layout(
        xaxis_title = "Nombre de prédictions",
        yaxis_title = "Précision (%)",
        height      = 350,
        yaxis_range = [0, 100],
    )
    st.plotly_chart(fig_evol, width='stretch')

    st.markdown("---")

    # ── Précision par surface ──
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.subheader("🎾 Précision par surface")
        surfaces = {}
        for h in avec_res:
            surf = h.get('surface', 'Unknown')
            if surf not in surfaces:
                surfaces[surf] = {'total': 0, 'correct': 0}
            surfaces[surf]['total'] += 1
            if h.get('resultat_reel') == h.get('vainqueur'):
                surfaces[surf]['correct'] += 1

        if surfaces:
            surf_data = [
                {
                    'Surface'   : s,
                    'Précision' : round(
                        v['correct'] / v['total'] * 100, 1
                    ),
                    'Total'     : v['total'],
                }
                for s, v in surfaces.items()
            ]
            df_surf = pd.DataFrame(surf_data)
            fig_surf = px.bar(
                df_surf,
                x     = 'Surface',
                y     = 'Précision',
                color = 'Précision',
                color_continuous_scale = 'Blues',
                text  = 'Précision',
            )
            fig_surf.update_traces(
                texttemplate='%{text}%',
                textposition='outside'
            )
            fig_surf.update_layout(
                height      = 300,
                yaxis_range = [0, 100],
                showlegend  = False,
            )
            st.plotly_chart(
                fig_surf, width='stretch'
            )

    with col_s2:
        st.subheader("🏆 Précision par circuit")
        circuits = {}
        for h in avec_res:
            circ = h.get('tournoi', 'Unknown')
            if circ not in circuits:
                circuits[circ] = {'total': 0, 'correct': 0}
            circuits[circ]['total'] += 1
            if h.get('resultat_reel') == h.get('vainqueur'):
                circuits[circ]['correct'] += 1

        if circuits:
            circ_data = [
                {
                    'Circuit'   : c,
                    'Précision' : round(
                        v['correct'] / v['total'] * 100, 1
                    ),
                    'Total'     : v['total'],
                }
                for c, v in circuits.items()
            ]
            df_circ = pd.DataFrame(circ_data)
            fig_circ = px.bar(
                df_circ,
                x     = 'Circuit',
                y     = 'Précision',
                color = 'Précision',
                color_continuous_scale = 'Oranges',
                text  = 'Précision',
            )
            fig_circ.update_traces(
                texttemplate='%{text}%',
                textposition='outside'
            )
            fig_circ.update_layout(
                height      = 300,
                yaxis_range = [0, 100],
                showlegend  = False,
            )
            st.plotly_chart(
                fig_circ, width='stretch'
            )

    st.markdown("---")

    # ── Value bets ──
    st.subheader("💰 Performance Value Bets")
    value_bets = [
        h for h in avec_res
        if h.get('value_bet_info')
    ]

    if value_bets:
        vb_corrects = [
            h for h in value_bets
            if h.get('resultat_reel') == h.get('vainqueur')
        ]
        pct_vb = round(
            len(vb_corrects) / len(value_bets) * 100, 1
        )

        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            st.metric(
                "🎯 Value bets détectés",
                len(value_bets)
            )
        with col_v2:
            st.metric(
                "✅ Value bets gagnants",
                len(vb_corrects)
            )
        with col_v3:
            st.metric(
                "📊 Précision value bets",
                f"{pct_vb}%"
            )

        # ROI simulé
        roi_total = 0
        for h in value_bets:
            info = h.get('value_bet_info', {})
            cote = info.get('cote', 2.0)
            if h.get('resultat_reel') == h.get('vainqueur'):
                roi_total += (cote - 1)
            else:
                roi_total -= 1

        roi_pct = round(roi_total / len(value_bets) * 100, 1)
        st.metric(
            "💵 ROI simulé (1 unité par bet)",
            f"{roi_pct}%",
            delta=f"{'+' if roi_pct >= 0 else ''}{roi_pct}%"
        )
    else:
        st.info(
            "Utilise les cotes bookmakers lors des prédictions "
            "pour voir les stats value bets ici."
        )

    st.markdown("---")

    # ── Précision par probabilité prédite ──
    st.subheader("📊 Calibration des probabilités")
    st.caption(
        "Si l'IA prédit 70%, le vrai vainqueur devrait "
        "gagner 70% du temps"
    )

    bins    = [(50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
    calib_data = []
    for low, high in bins:
        subset = [
            h for h in avec_res
            if low <= h.get('proba_v', 0) < high
        ]
        if subset:
            ok  = sum(
                1 for h in subset
                if h.get('resultat_reel') == h.get('vainqueur')
            )
            pct = round(ok / len(subset) * 100, 1)
            calib_data.append({
                'Probabilité IA' : f"{low}-{high}%",
                'Précision réelle': pct,
                'Nb prédictions' : len(subset),
            })

    if calib_data:
        df_calib = pd.DataFrame(calib_data)
        fig_cal  = go.Figure()
        fig_cal.add_trace(go.Bar(
            x    = df_calib['Probabilité IA'],
            y    = df_calib['Précision réelle'],
            name = 'Précision réelle',
            marker_color = '#2196F3',
            text = df_calib['Précision réelle'],
            texttemplate='%{text}%',
            textposition='outside',
        ))
        fig_cal.add_trace(go.Scatter(
            x    = df_calib['Probabilité IA'],
            y    = [55, 65, 75, 85, 95],
            mode = 'lines',
            name = 'Calibration parfaite',
            line = dict(
                color='red', dash='dash', width=2
            ),
        ))
        fig_cal.update_layout(
            height      = 350,
            yaxis_range = [0, 110],
            yaxis_title = "Précision réelle (%)",
        )
        st.plotly_chart(fig_cal, width='stretch')