# CMRPI Platform — Auto-évaluation Maturité Cybersécurité

Plateforme d'auto-évaluation de la maturité cybersécurité pour PME marocaines, basée sur le guide CMRPI/AUSIM. Développée dans le cadre d'un stage PFA à CMRPI (ENSA Béni Mellal), sous la supervision du Dr. Rachid Abouettahir.

## Jalon 2 — Périmètre

Conformément au brief : une interface simple qui pose les questions et calcule le score.
- Formulaire web Streamlit — **au choix : une question par écran (25 écrans) ou une section par écran (5 écrans)**, sélectionnable sur l'écran d'accueil
- Calcul du score en Python (`src/scoring.py`)
- **3 profils fictifs de PME intégrés** pour tester instantanément l'application (Finance, Commerce, Technologie)
- Le score s'affiche automatiquement en fin de questionnaire

## Démarrage rapide

```bash
pip install -r requirements.txt
python scripts/init_db.py      # charge questions + recommandations (bonus PDF)
streamlit run app.py
```

Ouvrir : http://localhost:8501

**Pour tester rapidement** : sur l'écran d'accueil, cliquer sur l'un des 3 boutons de profil fictif (PME Finance / Commerce / Technologie) — le score s'affiche immédiatement sans avoir à répondre aux 25 questions.

**Pour le parcours complet** : cliquer sur "Commencer le questionnaire", répondre aux 5 questions de chaque section, puis "Suivant" (activé une fois la section complète).

## Fonctionnalités

- Questionnaire de 25 questions, 5 sections (échelle Likert 1-5)
- Scoring automatique (0-100 par section + score global + niveau de maturité)
- 3 profils fictifs de test intégrés (chargement en un clic)
- Bonus : recommandations prioritaires + export PDF (si `python scripts/init_db.py` exécuté)

## Stack technique

- **Frontend/Backend:** Streamlit (Python)
- **Calcul du score:** Python pur (`src/scoring.py`), testé unitairement
- **Bonus (au-delà du brief) :** base SQLite, authentification bcrypt, génération PDF ReportLab — disponibles mais non requis pour le flux principal
- **Tests:** pytest, pytest-cov, `streamlit.testing.v1.AppTest` (tests end-to-end du flux applicatif)

## Structure du projet

```
cmrpi-platform/
├── app.py                  # Application Streamlit (flux principal, sans login)
├── requirements.txt
├── data/
│   ├── questions/          # questionnaire_fr.json, questionnaire_en.json, guidance.json
│   ├── recommendations/    # Recommendations_Database.xlsx
│   └── schema.sql
├── src/
│   ├── scoring.py          # Moteur de calcul du score
│   ├── questionnaire.py    # Chargement/validation du questionnaire
│   ├── test_profiles.py    # 3 profils fictifs de PME (exigence Jalon 2)
│   ├── auth.py              # Bonus : authentification (non requis Jalon 2)
│   ├── database.py          # Bonus : persistance SQLite (non requis Jalon 2)
│   └── pdf_generator.py     # Bonus : export PDF (non requis Jalon 2)
├── tests/                  # 44 tests, 87% de couverture
├── docs/                   # Scoring_Rules_V1.md
└── scripts/                # init_db.py

```

## Tests

```bash
pytest tests/ -v --cov=src --cov-report=term
```

44 tests, 87% de couverture — incluent des tests end-to-end simulant un utilisateur réel dans l'application (`tests/test_app_flow.py`), ainsi que la validation des 3 profils fictifs (`tests/test_profiles.py`).

## Calendrier du projet

| Jalon | Période | Objectif |
|---|---|---|
| Jalon 1 | 15–31 juillet 2026 | Analyse & Conception (questionnaire, scoring) — validé ✅ |
| Jalon 2 | 1–15 août 2026 | Interface Streamlit simple + calcul du score + tests sur profils fictifs |
| Jalon 3 | 16–31 août 2026 | Finalisation, documentation, rapport de stage |

## Encadrement

- **Encadrant professionnel:** Dr. Rachid Abouettahir (CMRPI)
- **Co-encadrante académique:** Pr. Zakia Errabih (ENSA Béni Mellal)
- **Stagiaire:** Youssef Ait Karroum

## Licence

Propriétaire — CMRPI & ENSA Béni Mellal
