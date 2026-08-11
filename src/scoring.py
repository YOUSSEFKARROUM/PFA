"""
scoring.py — Moteur de scoring pour l'auto-évaluation cybersécurité.

Implémente les formules définies dans docs/Scoring_Rules_V1.md (Jalon 1).
"""

DOMAIN_ORDER = [
    "dom_gov",
    "dom_acc",
    "dom_infra",
    "dom_inc",
    "dom_sens",
]

MATURITY_LEVELS = [
    (25, "Critique"),
    (50, "Faible"),
    (75, "Moyen"),
    (101, "Avancé"),
]


def calculate_domain_score(responses: list) -> float:
    """
    responses: liste de 5 réponses Likert (1-5) pour un domaine.
    returns: score du domaine (0-100), arrondi à 1 décimale.
    """
    if not responses or len(responses) == 0:
        return 0.0
    avg = sum(responses) / len(responses)
    score = ((avg - 1) / 4) * 100
    return round(max(0.0, min(100.0, score)), 1)


def calculate_domain_scores(responses_by_domain: dict) -> dict:
    """
    responses_by_domain: {domain_id: [r1, r2, r3, r4, r5], ...}
    returns: {domain_id: score, ...}
    """
    return {domain_id: calculate_domain_score(resp) for domain_id, resp in responses_by_domain.items()}


def calculate_global_score(domain_scores: dict) -> float:
    """
    domain_scores: {domain_id: score, ...}
    returns: score global (0-100), arrondi à 1 décimale.
    """
    if not domain_scores:
        return 0.0
    values = list(domain_scores.values())
    return round(sum(values) / len(values), 1)


def get_maturity_level(score: float) -> str:
    for threshold, label in MATURITY_LEVELS:
        if score < threshold:
            return label
    return "Avancé"


def get_severity_filter(domain_score: float) -> tuple:
    """
    Retourne (liste de sévérités à filtrer, nombre max de recommandations)
    selon la logique définie dans Scoring_Rules_V1.md section 6.
    """
    if domain_score < 60:
        return (["Critical", "High"], 3)
    return (["Medium", "Low"], 1)


def generate_recommendations(domain_scores: dict, get_recs_fn) -> dict:
    """
    domain_scores: {domain_id: score, ...}
    get_recs_fn: fonction(domain_id, severities) -> liste de recommandations (depuis la DB)
    returns: {domain_id: [recommandations filtrées et limitées], ...}
    """
    result = {}
    for domain_id, score in domain_scores.items():
        severities, limit = get_severity_filter(score)
        recs = get_recs_fn(domain_id, severities)
        result[domain_id] = recs[:limit]
    return result


def score_full_audit(all_responses: dict) -> dict:
    """
    Fonction principale : calcule le score complet d'un audit.

    all_responses: {question_id: response(1-5), ...} — 25 entrées
    Nécessite un mapping question_id -> domain_id (fourni séparément via la DB
    dans l'application ; ici on suppose que all_responses est déjà groupé par domaine
    via `group_responses_by_domain`).

    returns: {
        "domain_scores": {domain_id: score},
        "global_score": float,
        "maturity_level": str
    }
    """
    domain_scores = calculate_domain_scores(all_responses)
    global_score = calculate_global_score(domain_scores)
    level = get_maturity_level(global_score)
    return {
        "domain_scores": domain_scores,
        "global_score": global_score,
        "maturity_level": level,
    }


def group_responses_by_domain(responses: dict, question_domain_map: dict) -> dict:
    """
    responses: {question_id: value}
    question_domain_map: {question_id: domain_id}
    returns: {domain_id: [values...]}
    """
    grouped = {}
    for qid, value in responses.items():
        domain_id = question_domain_map.get(qid)
        if domain_id is None:
            continue
        grouped.setdefault(domain_id, []).append(value)
    return grouped
