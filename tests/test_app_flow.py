"""
Tests end-to-end de l'application Streamlit (framework officiel AppTest).

Valide le critère du Jalon 2 : "Vérifier que le score reflète bien les
réponses et que l'app est simple à utiliser", dans les DEUX modes prévus
par le brief : "une question par écran OU par section".
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture(autouse=True)
def ensure_db():
    db_path = Path(__file__).resolve().parent.parent / "app.db"
    if not db_path.exists():
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from src import database as db
        db.init_database()
        db.seed_questions_and_domains(
            str(Path(__file__).resolve().parent.parent / "data/questions/questions_fr.json"),
            str(Path(__file__).resolve().parent.parent / "data/questions/questions_en.json"),
            str(Path(__file__).resolve().parent.parent / "data/questions/guidance.json"),
        )
        db.seed_recommendations_from_xlsx(
            str(Path(__file__).resolve().parent.parent / "data/recommendations/Recommendations_Database.xlsx")
        )
    yield


def all_markdown_text(at) -> str:
    """Concatène le contenu réel (.value) de tous les blocs markdown affichés."""
    return " ".join(m.value for m in at.markdown)


def click_button(at, label_exact=None, label_contains=None):
    if label_exact is not None:
        matches = [b for b in at.button if b.label == label_exact]
    else:
        matches = [b for b in at.button if label_contains in b.label]
    assert matches, f"Bouton introuvable: {label_exact or label_contains}"
    return matches[0].click().run()


def test_homepage_loads_without_error():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    assert not at.exception
    assert at.title[0].value == "Auto-évaluation de la maturité cybersécurité"
    labels = [b.label for b in at.button]
    assert "PME Finance" in labels
    assert "PME Commerce" in labels
    assert "PME Technologie" in labels
    assert "Commencer le questionnaire  →" in labels


def test_mode_selector_present_with_both_options():
    """Le choix 'section' vs 'question' doit être proposé, conformément au brief."""
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    assert not at.exception
    mode_radio = at.radio[0]
    assert len(mode_radio.options) == 2
    assert mode_radio.value == "section"  # mode par défaut


def test_quick_test_profile_finance():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    click_button(at, label_exact="PME Finance")
    assert not at.exception
    assert at.title[0].value == "PME Finance"
    assert "44" in all_markdown_text(at)
    assert "Faible" in all_markdown_text(at)


def test_quick_test_profile_commerce():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    click_button(at, label_exact="PME Commerce")
    assert not at.exception
    assert "20" in all_markdown_text(at)
    assert "Critique" in all_markdown_text(at)


def test_quick_test_profile_technologie():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    click_button(at, label_exact="PME Technologie")
    assert not at.exception
    assert "83" in all_markdown_text(at)
    assert "Avancé" in all_markdown_text(at)


# ============================================================
# MODE "SECTION" (défaut)
# ============================================================

def test_section_mode_next_disabled_until_complete():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    click_button(at, label_contains="Commencer")

    assert at.title[0].value == "Gouvernance"
    next_btn = [b for b in at.button if "Suivant" in b.label][0]
    assert next_btn.disabled is True

    for r in at.radio:
        r.set_value(r.options[0]).run()

    next_btn = [b for b in at.button if "Suivant" in b.label][0]
    assert next_btn.disabled is False


def test_section_mode_full_flow_reaches_score():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    click_button(at, label_contains="Commencer")

    domains = ["Gouvernance", "Accès & Identités", "Infrastructure & Sécurité réseau",
               "Incidents & Continuité", "Sensibilisation & Formation"]
    for i in range(5):
        assert at.title[0].value == domains[i]
        for r in at.radio:
            r.set_value(r.options[4]).run()  # meilleure réponse partout
        next_btn = [b for b in at.button if ("Suivant" in b.label or "score" in b.label)][0]
        next_btn.click().run()

    assert not at.exception
    text = all_markdown_text(at)
    assert "100" in text
    assert "Avancé" in text


# ============================================================
# MODE "QUESTION" (une question par écran)
# ============================================================

def test_question_mode_one_question_per_screen():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    at.radio[0].set_value("question").run()
    click_button(at, label_contains="Commencer")

    assert not at.exception
    assert at.title[0].value == "Question 1"
    assert len(at.radio) == 1


def test_question_mode_next_disabled_until_answered():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    at.radio[0].set_value("question").run()
    click_button(at, label_contains="Commencer")

    next_btn = [b for b in at.button if "Suivant" in b.label][0]
    assert next_btn.disabled is True

    at.radio[0].set_value(at.radio[0].options[0]).run()

    next_btn = [b for b in at.button if "Suivant" in b.label][0]
    assert next_btn.disabled is False


def test_question_mode_full_flow_reaches_score():
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    at.radio[0].set_value("question").run()
    click_button(at, label_contains="Commencer")

    for i in range(25):
        assert at.title[0].value == f"Question {i + 1}"
        at.radio[0].set_value(at.radio[0].options[4]).run()
        next_btn = [b for b in at.button if ("Suivant" in b.label or "score" in b.label)][0]
        next_btn.click().run()

    assert not at.exception
    assert "100" in all_markdown_text(at)


def test_question_mode_previous_button_navigates_back():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    at.radio[0].set_value("question").run()
    click_button(at, label_contains="Commencer")

    at.radio[0].set_value(at.radio[0].options[2]).run()
    click_button(at, label_contains="Suivant")
    assert at.title[0].value == "Question 2"

    click_button(at, label_contains="Précédent")
    assert at.title[0].value == "Question 1"
    assert at.radio[0].value == at.radio[0].options[2]


def test_restart_button_resets_state():
    at = AppTest.from_file(APP_PATH, default_timeout=20)
    at.run()
    click_button(at, label_exact="PME Finance")
    assert not at.exception
    click_button(at, label_contains="Refaire")
    assert not at.exception
    assert at.title[0].value == "Auto-évaluation de la maturité cybersécurité"
