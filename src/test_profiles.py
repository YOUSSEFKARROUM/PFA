"""
test_profiles.py — 3 profils fictifs de PME pour tester rapidement
l'application (exigence du Jalon 2 : "Tester avec 2-3 profils fictifs de PME").

Les réponses sont groupées par domaine (5 réponses Likert 1-5 par domaine),
reprises du Jalon 1 (Analyse & Conception).
"""

TEST_PROFILES = {
    "PME Finance (profil moyen/faible)": {
        "sector": "Finance",
        "responses": {
            "dom_gov": [3, 3, 4, 3, 2],
            "dom_acc": [3, 3, 4, 3, 3],
            "dom_infra": [3, 2, 3, 2, 2],
            "dom_inc": [3, 3, 3, 3, 3],
            "dom_sens": [2, 2, 3, 2, 2],
        },
    },
    "PME Commerce (profil faible/critique)": {
        "sector": "Commerce",
        "responses": {
            "dom_gov": [2, 2, 3, 2, 1],
            "dom_acc": [2, 1, 2, 2, 2],
            "dom_infra": [2, 2, 2, 1, 2],
            "dom_inc": [1, 2, 2, 1, 2],
            "dom_sens": [2, 2, 2, 1, 2],
        },
    },
    "PME Technologie (profil avancé)": {
        "sector": "Technologie",
        "responses": {
            "dom_gov": [4, 5, 4, 4, 4],
            "dom_acc": [5, 4, 5, 5, 4],
            "dom_infra": [5, 5, 4, 5, 5],
            "dom_inc": [4, 4, 5, 4, 4],
            "dom_sens": [4, 4, 4, 3, 4],
        },
    },
}


def expand_profile_to_question_responses(profile_key: str, question_domain_map: dict) -> dict:
    """
    Convertit les réponses groupées par domaine d'un profil de test en
    dict {question_id: valeur}, dans l'ordre des questions de chaque domaine.

    question_domain_map: {question_id: domain_id} (ordre d'insertion = ordre des questions)
    """
    profile = TEST_PROFILES[profile_key]
    domain_responses = {k: list(v) for k, v in profile["responses"].items()}
    result = {}
    for qid, domain_id in question_domain_map.items():
        queue = domain_responses.get(domain_id, [])
        if queue:
            result[qid] = queue.pop(0)
    return result
