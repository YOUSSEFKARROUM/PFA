"""
app.py — Plateforme d'auto-évaluation de la maturité cybersécurité (CMRPI).

Design : système sur-mesure (src/ui_components.py) — palette navy/teal/sable,
typographie Space Grotesk + Inter + JetBrains Mono, radar chart des 5 domaines.

Fonctionnel (Jalon 2, brief respecté) :
- Formulaire Streamlit — au choix : UNE QUESTION PAR ÉCRAN ou UNE SECTION PAR ÉCRAN
- Calcul du score en Python (src/scoring.py)
- 3 profils fictifs de PME intégrés pour test rapide

Lancement : streamlit run app.py
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

from src import scoring, questionnaire as qmod, pdf_generator  # noqa: E402
from src.test_profiles import TEST_PROFILES, expand_profile_to_question_responses  # noqa: E402
from src import ui_components as ui  # noqa: E402

st.set_page_config(page_title="CMRPI — Auto-évaluation Cybersécurité", page_icon="🛡️", layout="centered")
st.markdown(ui.base_css(), unsafe_allow_html=True)

QUESTIONS = qmod.load_questions("fr")
GUIDANCE = qmod.load_guidance()
DOMAIN_GROUPS = qmod.get_questions_grouped_by_domain("fr")
QUESTION_DOMAIN_MAP = qmod.get_question_domain_map("fr")
DOMAIN_ORDER = list(DOMAIN_GROUPS.keys())
DOMAIN_LABELS = pdf_generator.DOMAIN_LABELS_FR

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "screen": "accueil",
    "mode": "section",
    "index": 0,
    "responses": {},
    "pme_name": "",
    "sector": "",
    "result": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_all():
    for k, v in defaults.items():
        st.session_state[k] = v


# ============================================================
# ÉCRAN ACCUEIL
# ============================================================
def screen_accueil():
    st.markdown('<div class="cmrpi-eyebrow">CMRPI · ESPACE MAROC CYBERCONFIANCE</div>', unsafe_allow_html=True)
    st.title("Auto-évaluation de la maturité cybersécurité")
    st.markdown(
        '<div class="cmrpi-hero-sub">25 questions, 5 domaines, basés sur le guide CMRPI/AUSIM. '
        'Répondez selon la situation actuelle de votre organisation — votre score et vos '
        'recommandations prioritaires s\'affichent immédiatement à la fin.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    with st.container():
        st.markdown('<div class="cmrpi-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        st.session_state.pme_name = c1.text_input(
            "Nom de l'organisation", st.session_state.pme_name, placeholder="Optionnel"
        )
        st.session_state.sector = c2.selectbox(
            "Secteur d'activité",
            ["", "Finance", "Commerce", "Technologie", "Industrie", "Services", "Santé", "Éducation", "Autre"],
            index=0,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cmrpi-eyebrow" style="margin-top:0.6rem;">Mode d\'affichage</div>', unsafe_allow_html=True)
    st.markdown(ui.mode_selector_html(st.session_state.mode), unsafe_allow_html=True)
    st.session_state.mode = st.radio(
        "Choisir le mode", options=["section", "question"],
        format_func=lambda m: "Par section (5 écrans)" if m == "section" else "Question par question (25 écrans)",
        horizontal=True, label_visibility="collapsed",
    )

    st.write("")
    if st.button("Commencer le questionnaire  →", type="primary", use_container_width=True):
        st.session_state.index = 0
        st.session_state.screen = "form"
        st.rerun()

    st.write("")
    st.markdown('<div class="cmrpi-eyebrow">Démonstration rapide</div>', unsafe_allow_html=True)
    st.caption("Charger un profil fictif de PME pour voir un résultat instantanément.")
    cols = st.columns(3)
    for i, profile_key in enumerate(TEST_PROFILES.keys()):
        if cols[i].button(profile_key.split(" (")[0], use_container_width=True):
            st.session_state.responses = expand_profile_to_question_responses(profile_key, QUESTION_DOMAIN_MAP)
            st.session_state.pme_name = profile_key.split(" (")[0]
            st.session_state.sector = TEST_PROFILES[profile_key]["sector"]
            st.session_state.result = None
            st.session_state.screen = "resultats"
            st.rerun()


# ============================================================
# WIDGET DE QUESTION PARTAGÉ
# ============================================================
def render_question_widget(q, show_domain_caption=False):
    qid = q["id"]
    options = q["options"]
    option_keys = list(options.keys())
    option_labels = [f"{k} — {options[k]}" for k in option_keys]
    help_text = GUIDANCE.get(qid, {}).get("fr", "")

    default_index = None
    if qid in st.session_state.responses:
        current_val = str(st.session_state.responses[qid])
        if current_val in option_keys:
            default_index = option_keys.index(current_val)

    st.markdown(f"**{q['text']}**")
    if help_text:
        st.caption(help_text)
    selected = st.radio(
        q["text"], options=option_labels, index=default_index,
        key=f"radio_{qid}", label_visibility="collapsed",
    )
    if selected:
        st.session_state.responses[qid] = int(selected.split(" — ")[0])


# ============================================================
# FORMULAIRE — MODE "SECTION"
# ============================================================
def screen_form_section():
    idx = st.session_state.index
    domain_id = DOMAIN_ORDER[idx]
    domain_questions = DOMAIN_GROUPS[domain_id]
    domain_label = domain_questions[0]["domain"]
    total = len(DOMAIN_ORDER)

    st.markdown(ui.domain_dots_html(DOMAIN_ORDER, domain_id), unsafe_allow_html=True)
    st.markdown(f'<div class="cmrpi-eyebrow">Section {idx + 1} / {total}</div>', unsafe_allow_html=True)
    st.title(domain_label)
    st.write("")

    for q in domain_questions:
        st.markdown('<div class="cmrpi-card">', unsafe_allow_html=True)
        render_question_widget(q)
        st.markdown('</div>', unsafe_allow_html=True)

    section_ids = [q["id"] for q in domain_questions]
    section_complete = all(qid in st.session_state.responses for qid in section_ids)

    col1, col2 = st.columns(2)
    if col1.button("← Précédent", use_container_width=True, disabled=(idx == 0)):
        st.session_state.index -= 1
        st.rerun()

    label = "Suivant →" if idx < total - 1 else "Voir mon score  ✓"
    if col2.button(label, type="primary", use_container_width=True, disabled=not section_complete):
        if idx < total - 1:
            st.session_state.index += 1
        else:
            st.session_state.screen = "resultats"
        st.rerun()

    if not section_complete:
        st.caption("Répondez à toutes les questions de cette section pour continuer.")


# ============================================================
# FORMULAIRE — MODE "QUESTION"
# ============================================================
def screen_form_question():
    idx = st.session_state.index
    q = QUESTIONS[idx]
    total = len(QUESTIONS)
    domain_id = QUESTION_DOMAIN_MAP[q["id"]]

    st.markdown(ui.domain_dots_html(DOMAIN_ORDER, domain_id), unsafe_allow_html=True)
    eyebrow = f'<div class="cmrpi-eyebrow">Question {idx + 1} / {total} · {q["domain"]}</div>'
    st.markdown(eyebrow, unsafe_allow_html=True)
    st.title(f"Question {idx + 1}")
    st.progress((idx + 1) / total)
    st.write("")

    st.markdown('<div class="cmrpi-card">', unsafe_allow_html=True)
    render_question_widget(q)
    st.markdown('</div>', unsafe_allow_html=True)

    answered = q["id"] in st.session_state.responses

    col1, col2 = st.columns(2)
    if col1.button("← Précédent", use_container_width=True, disabled=(idx == 0)):
        st.session_state.index -= 1
        st.rerun()

    label = "Suivant →" if idx < total - 1 else "Voir mon score  ✓"
    if col2.button(label, type="primary", use_container_width=True, disabled=not answered):
        if idx < total - 1:
            st.session_state.index += 1
        else:
            st.session_state.screen = "resultats"
        st.rerun()

    if not answered:
        st.caption("Répondez à la question pour continuer.")


# ============================================================
# ÉCRAN RÉSULTATS
# ============================================================
def screen_results():
    if st.session_state.result is None:
        grouped = scoring.group_responses_by_domain(st.session_state.responses, QUESTION_DOMAIN_MAP)
        st.session_state.result = scoring.score_full_audit(grouped)

    result = st.session_state.result
    name = st.session_state.pme_name or "Votre organisation"

    st.markdown('<div class="cmrpi-eyebrow">Résultat de l\'auto-évaluation</div>', unsafe_allow_html=True)
    st.title(name)
    st.caption(f"Secteur : {st.session_state.sector or 'non précisé'} · {datetime.now().strftime('%d/%m/%Y')}")

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown('<div class="cmrpi-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown(ui.gauge_arc_svg(result["global_score"], result["maturity_level"]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="cmrpi-card">', unsafe_allow_html=True)
        st.markdown(ui.radar_chart_svg(result["domain_scores"], DOMAIN_ORDER), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    detail_eyebrow = '<div class="cmrpi-eyebrow" style="margin-top:0.8rem;">Détail par section</div>'
    st.markdown(detail_eyebrow, unsafe_allow_html=True)
    for domain_id, score in result["domain_scores"].items():
        level = scoring.get_maturity_level(score)
        color = ui.LEVEL_COLORS.get(level, ui.TEAL)
        st.markdown(
            f'<div style="display:flex; justify-content:space-between; align-items:center; '
            f'padding:0.5rem 0; border-bottom:1px solid #EAE7DF;">'
            f'<span>{DOMAIN_LABELS.get(domain_id, domain_id)}</span>'
            f'<span style="font-family:\'JetBrains Mono\',monospace; font-weight:700; color:{color};">'
            f'{score:.0f}% · {level}</span></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown('<div class="cmrpi-eyebrow">Recommandations prioritaires</div>', unsafe_allow_html=True)
    if Path("app.db").exists():
        from src import database as db
        recommendations = scoring.generate_recommendations(result["domain_scores"], db.get_recommendations_for_domain)
        sev_colors = {"Critical": "#C0392B", "High": "#D68910", "Medium": "#B7950B", "Low": "#0E7C7B"}
        sev_labels_fr = {"Critical": "Critique", "High": "Haute", "Medium": "Moyenne", "Low": "Basse"}
        for domain_id, recs in recommendations.items():
            if not recs:
                continue
            st.markdown(f"**{DOMAIN_LABELS.get(domain_id, domain_id)}**")
            for r in recs:
                c = sev_colors.get(r["severity"], ui.TEAL)
                sev_fr = sev_labels_fr.get(r["severity"], r["severity"])
                badge = f'<div class="cmrpi-badge" style="background:{c}22; color:{c};">{sev_fr}</div>'
                st.markdown(f'{badge}{r["text_fr"]}', unsafe_allow_html=True)
    else:
        st.caption("Base de recommandations non initialisée (voir `python scripts/init_db.py`).")

    st.write("")
    col1, col2 = st.columns(2)
    if col1.button("↻ Refaire le test", use_container_width=True):
        reset_all()
        st.rerun()

    if Path("app.db").exists():
        from src import database as db
        recommendations = scoring.generate_recommendations(result["domain_scores"], db.get_recommendations_for_domain)
        pdf_bytes = pdf_generator.generate_audit_report(
            pme_name=name, sector=st.session_state.sector, audit_date=datetime.now().strftime("%d/%m/%Y"),
            domain_scores=result["domain_scores"], global_score=result["global_score"],
            maturity_level=result["maturity_level"], recommendations=recommendations,
        )
        col2.download_button(
            "↓ Télécharger le PDF", data=pdf_bytes,
            file_name="rapport_audit_cmrpi.pdf", mime="application/pdf",
            use_container_width=True,
        )


# ============================================================
# ROUTER
# ============================================================
screen = st.session_state.screen
if screen == "accueil":
    screen_accueil()
elif screen == "form":
    if st.session_state.mode == "section":
        screen_form_section()
    else:
        screen_form_question()
else:
    screen_results()
