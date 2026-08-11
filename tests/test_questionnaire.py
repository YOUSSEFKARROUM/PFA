"""Tests unitaires — questionnaire.py (fonctions de chargement/validation)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import questionnaire as qmod


def test_load_questions_fr():
    questions = qmod.load_questions("fr")
    assert len(questions) == 25
    assert questions[0]["id"] == "q1"


def test_load_questions_en():
    questions = qmod.load_questions("en")
    assert len(questions) == 25
    assert questions[0]["domain"] == "Governance"


def test_load_guidance():
    guidance = qmod.load_guidance()
    assert len(guidance) == 25
    assert "fr" in guidance["q1"]
    assert "en" in guidance["q1"]


def test_get_question_domain_map():
    mapping = qmod.get_question_domain_map("fr")
    assert len(mapping) == 25
    assert mapping["q1"] == "dom_gov"
    assert mapping["q6"] == "dom_acc"
    assert mapping["q11"] == "dom_infra"
    assert mapping["q16"] == "dom_inc"
    assert mapping["q21"] == "dom_sens"


def test_get_questions_grouped_by_domain():
    grouped = qmod.get_questions_grouped_by_domain("fr")
    assert len(grouped) == 5
    assert len(grouped["dom_gov"]) == 5
    assert len(grouped["dom_sens"]) == 5


def test_validate_responses_complete():
    expected_ids = [f"q{i}" for i in range(1, 26)]
    responses = {qid: 3 for qid in expected_ids}
    is_valid, missing = qmod.validate_responses(responses, expected_ids)
    assert is_valid is True
    assert missing == []


def test_validate_responses_incomplete():
    expected_ids = [f"q{i}" for i in range(1, 26)]
    responses = {qid: 3 for qid in expected_ids[:20]}
    is_valid, missing = qmod.validate_responses(responses, expected_ids)
    assert is_valid is False
    assert len(missing) == 5


def test_validate_responses_invalid_value():
    expected_ids = ["q1", "q2"]
    responses = {"q1": 3, "q2": 9}  # 9 hors plage [1-5]
    is_valid, missing = qmod.validate_responses(responses, expected_ids)
    assert is_valid is False
    assert "q2" in missing
