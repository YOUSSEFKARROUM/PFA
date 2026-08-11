"""
questionnaire.py — Chargement et rendu du questionnaire d'auto-évaluation.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "questions"

DOMAIN_NAME_TO_ID = {
    "Gouvernance": "dom_gov",
    "Governance": "dom_gov",
    "Accès & Identités": "dom_acc",
    "Access & Identity": "dom_acc",
    "Infrastructure & Sécurité réseau": "dom_infra",
    "Infrastructure & Network Security": "dom_infra",
    "Incidents & Continuité": "dom_inc",
    "Incident & Continuity": "dom_inc",
    "Sensibilisation & Formation": "dom_sens",
    "Awareness & Training": "dom_sens",
}


def load_questions(language: str = "fr") -> list:
    """Charge les 25 questions depuis le fichier JSON correspondant à la langue."""
    filename = f"questions_{language}.json"
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questionnaire"]


def load_guidance() -> dict:
    path = DATA_DIR / "guidance.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["guidance"]


def get_question_domain_map(language: str = "fr") -> dict:
    """Retourne {question_id: domain_id} pour les 25 questions."""
    questions = load_questions(language)
    return {q["id"]: DOMAIN_NAME_TO_ID.get(q["domain"], "dom_gov") for q in questions}


def get_questions_grouped_by_domain(language: str = "fr") -> dict:
    """Retourne {domain_id: [questions...]} conservant l'ordre du questionnaire."""
    questions = load_questions(language)
    grouped = {}
    for q in questions:
        domain_id = DOMAIN_NAME_TO_ID.get(q["domain"], "dom_gov")
        grouped.setdefault(domain_id, []).append(q)
    return grouped


def validate_responses(responses: dict, expected_ids: list) -> tuple:
    """
    Vérifie que toutes les questions ont une réponse valide (1-5).
    returns: (is_valid: bool, missing: list)
    """
    missing = [qid for qid in expected_ids if qid not in responses or responses[qid] not in (1, 2, 3, 4, 5)]
    return (len(missing) == 0, missing)


# ============================================================
# Rendu Streamlit (utilisé par app.py)
# ============================================================

def render_questionnaire_streamlit(st, language: str = "fr"):
    """
    Affiche le questionnaire complet dans Streamlit, groupé par domaine,
    avec barre de progression. Retourne le dict de réponses courant
    (stocké dans st.session_state).
    """
    questions = load_questions(language)
    guidance = load_guidance()
    grouped = {}
    for q in questions:
        grouped.setdefault(q["domain"], []).append(q)

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    total = len(questions)
    answered = len([v for v in st.session_state.responses.values() if v])
    st.progress(answered / total if total else 0)
    st.caption(f"{answered} / {total} questions répondues")

    for domain_name, domain_questions in grouped.items():
        st.subheader(domain_name)
        for q in domain_questions:
            qid = q["id"]
            options = q["options"]
            label = q["text"]
            help_text = guidance.get(qid, {}).get(language, "")
            option_keys = list(options.keys())
            option_labels = [f"{k} — {options[k]}" for k in option_keys]

            default_index = None
            if qid in st.session_state.responses:
                current_val = str(st.session_state.responses[qid])
                if current_val in option_keys:
                    default_index = option_keys.index(current_val)

            selected = st.radio(
                label,
                options=option_labels,
                index=default_index,
                help=help_text,
                key=f"q_{qid}",
            )
            if selected:
                chosen_key = selected.split(" — ")[0]
                st.session_state.responses[qid] = int(chosen_key)
        st.divider()

    return st.session_state.responses
