# Règles de Scoring — Plateforme CMRPI
## Auto-évaluation Maturité Cybersécurité PME Marocaines

**Version:** 1.0
**Date:** Jalon 1 — Juillet 2026
**Auteur:** Youssef Ait Karroum

---

## 1. Vue d'ensemble

Le score de maturité cybersécurité est calculé sur deux niveaux :
1. **Score par domaine** (5 domaines, 0-100)
2. **Score global** (moyenne des 5 domaines, 0-100)

Chaque domaine comprend 5 questions notées sur une échelle de Likert de 1 à 5.

---

## 2. Formule — Score par domaine

```
Domain Score = ((avg_likert - 1) / 4) × 100
```

Où :
- `avg_likert` = moyenne arithmétique des 5 réponses Likert (1-5) du domaine
- Normalisation : intervalle [1, 5] → intervalle [0, 100]

### Exemple de calcul

Réponses du domaine "Gouvernance" : `[4, 4, 3, 4, 2]`

```
avg_likert = (4 + 4 + 3 + 4 + 2) / 5 = 3.4
domain_score = ((3.4 - 1) / 4) × 100 = 60%
```

---

## 3. Formule — Score global

```
Global Score = (domain_score_1 + domain_score_2 + domain_score_3 + domain_score_4 + domain_score_5) / 5
```

Chaque domaine a un poids égal (20%).

### Exemple de calcul

```
domain_scores = [60%, 60%, 40%, 40%, 20%]
global_score = (60 + 60 + 40 + 40 + 20) / 5 = 44%
```

---

## 4. Seuils de maturité

| Plage    | Niveau    | Description                                    |
|----------|-----------|-------------------------------------------------|
| 0-25%    | Critique  | Absence de pratiques, risque très élevé          |
| 25-50%   | Faible    | Pratiques initiales, risques importants          |
| 50-75%   | Moyen     | Pratiques établies, amélioration possible        |
| 75-100%  | Avancé    | Pratiques matures, focus maintenance/innovation  |

---

## 5. Pseudo-code (implémentation)

```python
def calculate_domain_scores(responses: list[int]) -> list[float]:
    """
    responses: liste de 25 réponses Likert (1-5), ordonnées par domaine
    returns: liste de 5 scores de domaine (0-100)
    """
    domain_scores = []
    for i in range(5):  # 5 domaines
        domain_responses = responses[i*5:(i+1)*5]
        avg = sum(domain_responses) / 5
        score = ((avg - 1) / 4) * 100
        domain_scores.append(round(score, 1))
    return domain_scores


def calculate_global_score(domain_scores: list[float]) -> float:
    """
    domain_scores: liste de 5 scores de domaine
    returns: score global (0-100)
    """
    return round(sum(domain_scores) / len(domain_scores), 1)


def get_maturity_level(score: float) -> str:
    if score < 25:
        return "Critique"
    elif score < 50:
        return "Faible"
    elif score < 75:
        return "Moyen"
    else:
        return "Avancé"
```

---

## 6. Logique de filtrage des recommandations

```
SI domain_score < 60:
    recommandations = filtrer(sévérité ∈ [Critique, Haute])
    recommandations = trier_par(priorité, ordre=DESC)
    recommandations = garder(min(3, count))
SINON:
    recommandations = filtrer(sévérité ∈ [Moyenne, Basse])
    recommandations = garder(1)
```

---

## 7. Exemples de validation (3 profils PME test)

### Profil 1 — PME Finance
| Domaine | Réponses | Score |
|---|---|---|
| Gouvernance | [3,3,4,3,2] | 60% |
| Accès & Identités | [3,3,4,3,3] | 60% |
| Infrastructure | [3,2,3,2,2] | 50% |
| Incidents & Continuité | [3,3,3,3,3] | 60% |
| Sensibilisation | [2,2,3,2,2] | 40% |

**Score global = (60+60+50+60+40)/5 = 54% → Niveau "Moyen"**

### Profil 2 — PME Commerce
| Domaine | Réponses | Score |
|---|---|---|
| Gouvernance | [2,2,3,2,1] | 40% |
| Accès & Identités | [2,1,2,2,2] | 30% |
| Infrastructure | [2,2,2,1,2] | 35% |
| Incidents & Continuité | [1,2,2,1,2] | 30% |
| Sensibilisation | [2,2,2,1,2] | 35% |

**Score global = (40+30+35+30+35)/5 = 34% → Niveau "Faible"**

### Profil 3 — PME Technologie
| Domaine | Réponses | Score |
|---|---|---|
| Gouvernance | [4,5,4,4,4] | 80% |
| Accès & Identités | [5,4,5,5,4] | 85% |
| Infrastructure | [5,5,4,5,5] | 90% |
| Incidents & Continuité | [4,4,5,4,4] | 80% |
| Sensibilisation | [4,4,4,3,4] | 75% |

**Score global = (80+85+90+80+75)/5 = 82% → Niveau "Avancé"**

---

## 8. Justification académique

1. **Fondements CMM/CMMI** — Humphrey, W. (1989), *Managing the Software Process*. Les 5 niveaux de maturité (Initial → Géré → Défini → Quantitativement géré → Optimisé) inspirent directement nos 5 seuils.

2. **Recherche sur les échelles de Likert** — Dawes, J. (2008), *"Do data characteristics change according to the number of scale points used?"*. L'échelle à 5 points est optimale pour ce type de questionnaire (par rapport à 7 ou 10 points), offrant un bon compromis simplicité/granularité.

3. **Alignement ISO/IEC 27001:2022** — Les 14 sections du référentiel ISO sont regroupées conceptuellement en 5 domaines, facilitant la comparaison future avec un audit de conformité.

4. **NIST Cybersecurity Framework 2.0** — Les 5 fonctions du framework (Govern, Protect, Detect, Respond, Recover) présentent une correspondance conceptuelle avec nos 5 domaines.

---

*Document produit dans le cadre du Jalon 1 (Analyse & Conception) — Stage PFA CMRPI 2026.*
