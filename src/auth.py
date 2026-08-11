"""
auth.py — Authentification des utilisateurs PME (bcrypt).
"""
import re
import bcrypt
from src import database as db


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def register_pme(email: str, password: str, name: str, sector: str = None) -> dict:
    """
    Inscrit une nouvelle PME.
    Returns: {"success": bool, "pme_id": str|None, "error": str|None}
    """
    email = email.strip().lower()

    if not EMAIL_REGEX.match(email):
        return {"success": False, "pme_id": None, "error": "Adresse email invalide."}
    if len(password) < 8:
        return {"success": False, "pme_id": None, "error": "Le mot de passe doit contenir au moins 8 caractères."}
    if not name or len(name.strip()) < 2:
        return {"success": False, "pme_id": None, "error": "Nom de l'organisation requis."}
    if db.get_pme_by_email(email):
        return {"success": False, "pme_id": None, "error": "Un compte existe déjà avec cet email."}

    password_hash = hash_password(password)
    pme_id = db.create_pme(email, password_hash, name.strip(), sector)
    db.log_action(pme_id, "register", f"Nouveau compte créé: {email}")
    return {"success": True, "pme_id": pme_id, "error": None}


def login_pme(email: str, password: str) -> dict:
    """
    Authentifie une PME.
    Returns: {"success": bool, "pme_id": str|None, "name": str|None, "error": str|None}
    """
    email = email.strip().lower()
    pme = db.get_pme_by_email(email)

    if not pme:
        return {"success": False, "pme_id": None, "name": None, "error": "Email ou mot de passe incorrect."}
    if not verify_password(password, pme["password_hash"]):
        return {"success": False, "pme_id": None, "name": None, "error": "Email ou mot de passe incorrect."}

    db.log_action(pme["id"], "login", f"Connexion: {email}")
    return {"success": True, "pme_id": pme["id"], "name": pme["name"], "error": None}
