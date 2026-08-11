"""Tests unitaires — database.py et pdf_generator.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src import database as db, pdf_generator

BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_app.db"
    monkeypatch.setattr(db, "DB_PATH", test_db_path)
    db.init_database()
    yield


def test_init_database_creates_domains():
    domains = db.get_all_domains()
    assert len(domains) == 5


def test_create_and_get_pme():
    pme_id = db.create_pme("t@pme.ma", "hashed_pw", "Test PME", "Finance")
    pme = db.get_pme_by_id(pme_id)
    assert pme["email"] == "t@pme.ma"
    assert pme["name"] == "Test PME"


def test_seed_questions_and_domains():
    n = db.seed_questions_and_domains(
        str(BASE_DIR / "data" / "questions" / "questions_fr.json"),
        str(BASE_DIR / "data" / "questions" / "questions_en.json"),
        str(BASE_DIR / "data" / "questions" / "guidance.json"),
    )
    assert n == 25
    questions = db.get_all_questions()
    assert len(questions) == 25


def test_seed_recommendations():
    n = db.seed_recommendations_from_xlsx(str(BASE_DIR / "data" / "recommendations" / "Recommendations_Database.xlsx"))
    assert n >= 40
    recs = db.get_recommendations_for_domain("dom_gov", ["Critical", "High"])
    assert len(recs) > 0


def test_audit_lifecycle():
    db.seed_questions_and_domains(
        str(BASE_DIR / "data" / "questions" / "questions_fr.json"),
        str(BASE_DIR / "data" / "questions" / "questions_en.json"),
        str(BASE_DIR / "data" / "questions" / "guidance.json"),
    )
    pme_id = db.create_pme("audit@pme.ma", "hash", "PME Audit")
    audit_id = db.create_audit(pme_id)
    db.save_response(audit_id, "q1", 4, 60.0)
    db.complete_audit(audit_id, 60.0)
    history = db.get_audit_history(pme_id)
    assert len(history) == 1
    assert history[0]["global_score"] == 60.0
    responses = db.get_audit_responses(audit_id)
    assert len(responses) == 1


def test_pdf_generation_returns_bytes():
    domain_scores = {"dom_gov": 60.0, "dom_acc": 55.0, "dom_infra": 35.0, "dom_inc": 50.0, "dom_sens": 30.0}
    recommendations = {"dom_gov": [{"severity": "Critique", "text_fr": "Établir une politique"}]}
    pdf_bytes = pdf_generator.generate_audit_report(
        pme_name="PME Test",
        sector="Finance",
        audit_date="23/07/2026",
        domain_scores=domain_scores,
        global_score=44.0,
        maturity_level="Faible",
        recommendations=recommendations,
    )
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1000
