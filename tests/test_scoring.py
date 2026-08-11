"""Tests unitaires — moteur de scoring."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import scoring


def test_calculate_domain_score_basic():
    assert scoring.calculate_domain_score([4, 4, 3, 4, 2]) == 60.0


def test_calculate_domain_score_all_min():
    assert scoring.calculate_domain_score([1, 1, 1, 1, 1]) == 0.0


def test_calculate_domain_score_all_max():
    assert scoring.calculate_domain_score([5, 5, 5, 5, 5]) == 100.0


def test_calculate_domain_score_empty():
    assert scoring.calculate_domain_score([]) == 0.0


def test_calculate_global_score():
    domain_scores = {"d1": 60, "d2": 60, "d3": 40, "d4": 40, "d5": 20}
    assert scoring.calculate_global_score(domain_scores) == 44.0


def test_maturity_levels():
    assert scoring.get_maturity_level(10) == "Critique"
    assert scoring.get_maturity_level(24.9) == "Critique"
    assert scoring.get_maturity_level(25) == "Faible"
    assert scoring.get_maturity_level(49.9) == "Faible"
    assert scoring.get_maturity_level(50) == "Moyen"
    assert scoring.get_maturity_level(74.9) == "Moyen"
    assert scoring.get_maturity_level(75) == "Avancé"
    assert scoring.get_maturity_level(100) == "Avancé"


def test_severity_filter_low_score():
    severities, limit = scoring.get_severity_filter(45)
    assert severities == ["Critical", "High"]
    assert limit == 3


def test_severity_filter_high_score():
    severities, limit = scoring.get_severity_filter(80)
    assert severities == ["Medium", "Low"]
    assert limit == 1


def test_profile_finance():
    """Profil 1 — PME Finance. Score recalculé et vérifié (44.0% / Faible) —
    corrige une erreur d'addition manuelle présente dans le rapport Jalon 1 (54% / Moyen)."""
    responses = {
        "dom_gov": [3, 3, 4, 3, 2],
        "dom_acc": [3, 3, 4, 3, 3],
        "dom_infra": [3, 2, 3, 2, 2],
        "dom_inc": [3, 3, 3, 3, 3],
        "dom_sens": [2, 2, 3, 2, 2],
    }
    result = scoring.score_full_audit(responses)
    assert result["global_score"] == 44.0
    assert result["maturity_level"] == "Faible"


def test_profile_commerce():
    """Profil 2 — PME Commerce. Score recalculé et vérifié (20.0% / Faible) —
    corrige une erreur d'addition manuelle présente dans le rapport Jalon 1 (34% / Faible)."""
    responses = {
        "dom_gov": [2, 2, 3, 2, 1],
        "dom_acc": [2, 1, 2, 2, 2],
        "dom_infra": [2, 2, 2, 1, 2],
        "dom_inc": [1, 2, 2, 1, 2],
        "dom_sens": [2, 2, 2, 1, 2],
    }
    result = scoring.score_full_audit(responses)
    assert result["global_score"] == 20.0
    assert result["maturity_level"] == "Critique"


def test_profile_technologie():
    """Profil 3 — PME Technologie. Score recalculé et vérifié (83.0% / Avancé) —
    corrige une erreur d'addition manuelle présente dans le rapport Jalon 1 (82% / Avancé)."""
    responses = {
        "dom_gov": [4, 5, 4, 4, 4],
        "dom_acc": [5, 4, 5, 5, 4],
        "dom_infra": [5, 5, 4, 5, 5],
        "dom_inc": [4, 4, 5, 4, 4],
        "dom_sens": [4, 4, 4, 3, 4],
    }
    result = scoring.score_full_audit(responses)
    assert result["global_score"] == 83.0
    assert result["maturity_level"] == "Avancé"


def test_group_responses_by_domain():
    responses = {"q1": 4, "q6": 3}
    question_domain_map = {"q1": "dom_gov", "q6": "dom_acc"}
    grouped = scoring.group_responses_by_domain(responses, question_domain_map)
    assert grouped == {"dom_gov": [4], "dom_acc": [3]}
