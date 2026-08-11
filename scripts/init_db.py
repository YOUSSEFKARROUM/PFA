"""
scripts/init_db.py — Initialise la base de données SQLite et charge les
questions, guidance et recommandations produites au Jalon 1.

Usage: python scripts/init_db.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import database as db

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def main():
    print("Initialisation de la base de données...")
    db.init_database()
    print(f"  Schéma appliqué : {DATA_DIR / 'schema.sql'}")

    n_questions = db.seed_questions_and_domains(
        str(DATA_DIR / "questions" / "questions_fr.json"),
        str(DATA_DIR / "questions" / "questions_en.json"),
        str(DATA_DIR / "questions" / "guidance.json"),
    )
    print(f"  {n_questions} questions chargées (FR + EN + guidance)")

    n_recs = db.seed_recommendations_from_xlsx(
        str(DATA_DIR / "recommendations" / "Recommendations_Database.xlsx")
    )
    print(f"  {n_recs} recommandations chargées")

    print("Base de données prête : app.db")


if __name__ == "__main__":
    main()
