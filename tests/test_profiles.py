"""Tests unitaires — profils fictifs de test (exigence Jalon 2)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import questionnaire as qmod, scoring
from src.test_profiles import TEST_PROFILES, expand_profile_to_question_responses


def test_three_profiles_exist():
    """Le Jalon 2 exige de tester avec 2-3 profils fictifs de PME."""
    assert len(TEST_PROFILES) == 3


def test_expand_profile_covers_all_25_questions():
    question_domain_map = qmod.get_question_domain_map("fr")
    for profile_key in TEST_PROFILES:
        expanded = expand_profile_to_question_responses(profile_key, question_domain_map)
        assert len(expanded) == 25
        assert all(v in (1, 2, 3, 4, 5) for v in expanded.values())


def test_profiles_produce_expected_scores():
    question_domain_map = qmod.get_question_domain_map("fr")
    expected = {
        "PME Finance (profil moyen/faible)": (44.0, "Faible"),
        "PME Commerce (profil faible/critique)": (20.0, "Critique"),
        "PME Technologie (profil avancé)": (83.0, "Avancé"),
    }
    for profile_key, (exp_score, exp_level) in expected.items():
        expanded = expand_profile_to_question_responses(profile_key, question_domain_map)
        grouped = scoring.group_responses_by_domain(expanded, question_domain_map)
        result = scoring.score_full_audit(grouped)
        assert result["global_score"] == exp_score
        assert result["maturity_level"] == exp_level
