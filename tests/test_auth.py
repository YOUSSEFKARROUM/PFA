"""Tests unitaires — authentification."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src import auth, database as db


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Utilise une base de données temporaire pour chaque test."""
    test_db_path = tmp_path / "test_app.db"
    monkeypatch.setattr(db, "DB_PATH", test_db_path)
    db.init_database()
    yield


def test_password_hash_and_verify():
    hashed = auth.hash_password("MonMotDePasse123")
    assert auth.verify_password("MonMotDePasse123", hashed) is True
    assert auth.verify_password("mauvais_mdp", hashed) is False


def test_register_success():
    result = auth.register_pme("test@pme.ma", "password123", "Ma PME Test", "Finance")
    assert result["success"] is True
    assert result["pme_id"] is not None


def test_register_invalid_email():
    result = auth.register_pme("email_invalide", "password123", "Ma PME")
    assert result["success"] is False
    assert "email" in result["error"].lower()


def test_register_short_password():
    result = auth.register_pme("test2@pme.ma", "short", "Ma PME")
    assert result["success"] is False
    assert "mot de passe" in result["error"].lower()


def test_register_duplicate_email():
    auth.register_pme("dup@pme.ma", "password123", "PME A")
    result = auth.register_pme("dup@pme.ma", "password456", "PME B")
    assert result["success"] is False
    assert "existe" in result["error"].lower()


def test_login_success():
    auth.register_pme("login@pme.ma", "password123", "PME Login")
    result = auth.login_pme("login@pme.ma", "password123")
    assert result["success"] is True
    assert result["name"] == "PME Login"


def test_login_wrong_password():
    auth.register_pme("login2@pme.ma", "password123", "PME Login2")
    result = auth.login_pme("login2@pme.ma", "wrong_password")
    assert result["success"] is False


def test_login_nonexistent_user():
    result = auth.login_pme("inexistant@pme.ma", "password123")
    assert result["success"] is False
