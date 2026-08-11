"""
ui_components.py — Système de design CMRPI : CSS partagé + composants SVG
sur-mesure (radar chart des 5 domaines, jauge de score).

Palette :
  Navy   #14213D  (fond profond, texte fort)
  Teal   #0E7C7B  (accent, actions)
  Sable  #C9A46A  (accent chaud, highlights)
  Ivoire #F7F5F0  (fond de page)
  Encre  #2A2A2A  (texte courant)

Typo :
  Titres : "Space Grotesk"  (géométrique, technique, distinctif)
  Corps  : "Inter"
  Données/scores : "JetBrains Mono"
"""
import math

NAVY = "#14213D"
NAVY_SOFT = "#1F3358"
TEAL = "#0E7C7B"
TEAL_LIGHT = "#E4F3F2"
SAND = "#C9A46A"
IVORY = "#F7F5F0"
INK = "#2A2A2A"
MUTED = "#6B7280"

LEVEL_COLORS = {
    "Critique": "#C0392B",
    "Faible": "#D9822B",
    "Moyen": "#8A8A1F",
    "Avancé": "#0E7C7B",
}

DOMAIN_SHORT_LABELS = {
    "dom_gov": "Gouvernance",
    "dom_acc": "Accès",
    "dom_infra": "Infra.",
    "dom_inc": "Incidents",
    "dom_sens": "Sensibi-\nlisation",
}


def base_css() -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}
.stApp {{
    background: {IVORY};
}}
h1, h2, h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: {NAVY} !important;
    letter-spacing: -0.01em;
}}
p, label, span, div {{
    color: {INK};
}}

/* ---- Boutons ---- */
div.stButton > button {{
    background: {TEAL};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
}}
div.stButton > button:hover {{
    background: {NAVY};
    color: white;
    transform: translateY(-1px);
}}
div.stButton > button:disabled {{
    background: #D8DCE3;
    color: #9AA1AC;
}}
div.stDownloadButton > button {{
    background: {SAND};
    color: {NAVY};
    border: none;
    border-radius: 10px;
    font-weight: 600;
}}

/* ---- Barre de progression ---- */
.stProgress > div > div > div > div {{ background-color: {TEAL}; }}

/* ---- Radio (Likert) transformés en cartes ---- */
div[role="radiogroup"] {{
    gap: 0.4rem;
}}
div[role="radiogroup"] label {{
    background: white;
    border: 1.5px solid #E5E2DA;
    border-radius: 10px;
    padding: 0.55rem 0.9rem !important;
    margin-bottom: 0 !important;
    transition: border-color 0.15s ease, background 0.15s ease;
}}
div[role="radiogroup"] label:hover {{
    border-color: {TEAL};
    background: {TEAL_LIGHT};
}}

/* ---- Cartes génériques ---- */
.cmrpi-card {{
    background: white;
    border: 1px solid #EAE7DF;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(20,33,61,0.06);
}}
.cmrpi-eyebrow {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {TEAL};
    font-weight: 700;
    margin-bottom: 0.2rem;
}}
.cmrpi-hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: {NAVY};
    line-height: 1.15;
    margin: 0.2rem 0 0.4rem 0;
}}
.cmrpi-hero-sub {{
    color: {MUTED};
    font-size: 1rem;
    max-width: 560px;
}}

/* ---- Dots de progression par domaine ---- */
.cmrpi-dots {{ display: flex; gap: 10px; align-items: center; margin: 0.6rem 0 1.2rem 0; }}
.cmrpi-dot {{
    width: 34px; height: 34px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700;
    border: 2px solid #DDD9CE; color: #B4AFA2; background: white;
}}
.cmrpi-dot.done {{ background: {TEAL}; border-color: {TEAL}; color: white; }}
.cmrpi-dot.active {{ border-color: {NAVY}; color: {NAVY}; background: {IVORY}; }}
.cmrpi-dot-line {{ flex: 1; height: 2px; background: #DDD9CE; }}
.cmrpi-dot-line.done {{ background: {TEAL}; }}

/* ---- Badge de sévérité ---- */
.cmrpi-badge {{
    display: inline-block; padding: 0.15rem 0.55rem; border-radius: 6px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.03em; margin-right: 0.5rem;
}}

/* ---- Score global ---- */
.cmrpi-score-number {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 3.2rem; font-weight: 700; color: {NAVY};
}}
hr {{ border-color: #E5E2DA; }}
</style>
"""


def mode_selector_html(selected: str) -> str:
    """Affiche deux cartes explicatives au-dessus du widget de sélection (radio natif requis pour l'état)."""
    color_a = TEAL if selected == "section" else "#EAE7DF"
    color_b = TEAL if selected == "question" else "#EAE7DF"
    return f"""
<div style="display:flex; gap:0.8rem; margin-bottom:0.4rem;">
  <div class="cmrpi-card" style="flex:1; padding:1rem 1.2rem; border-color:{color_a};">
    <div class="cmrpi-eyebrow">Mode A</div>
    <b>Par section</b><br><span style="color:{MUTED}; font-size:0.9rem;">5 écrans, 5 questions chacun</span>
  </div>
  <div class="cmrpi-card" style="flex:1; padding:1rem 1.2rem; border-color:{color_b};">
    <div class="cmrpi-eyebrow">Mode B</div>
    <b>Question par question</b><br><span style="color:{MUTED}; font-size:0.9rem;">25 écrans, 1 question chacun</span>
  </div>
</div>

"""


def domain_dots_html(domain_order, current_domain_id) -> str:
    parts = ['<div class="cmrpi-dots">']
    current_idx = domain_order.index(current_domain_id)
    for i, dom_id in enumerate(domain_order):
        state = "done" if i < current_idx else ("active" if i == current_idx else "")
        parts.append(f'<div class="cmrpi-dot {state}">{i + 1}</div>')
        if i < len(domain_order) - 1:
            line_state = "done" if i < current_idx else ""
            parts.append(f'<div class="cmrpi-dot-line {line_state}"></div>')
    parts.append("</div>")
    return "".join(parts)


# ============================================================
# SVG — Radar chart des 5 domaines (signature visuelle)
# ============================================================
def radar_chart_svg(domain_scores: dict, domain_order: list, width: int = 380, height: int = 380) -> str:
    cx, cy = width / 2, height / 2 + 10
    max_r = min(width, height) / 2 - 60
    n = len(domain_order)
    angle_step = 2 * math.pi / n
    start_angle = -math.pi / 2

    def point_at(index, value_ratio):
        angle = start_angle + index * angle_step
        r = max_r * value_ratio
        return cx + r * math.cos(angle), cy + r * math.sin(angle)

    # Grille (25/50/75/100 %)
    grid_polys = []
    for ratio in [0.25, 0.5, 0.75, 1.0]:
        pts = [point_at(i, ratio) for i in range(n)]
        path = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        grid_polys.append(f'<polygon points="{path}" fill="none" stroke="#E2DFD6" stroke-width="1"/>')

    # Axes
    axis_lines = []
    labels = []
    for i, dom_id in enumerate(domain_order):
        x, y = point_at(i, 1.0)
        axis_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#E2DFD6" stroke-width="1"/>')
        lx, ly = point_at(i, 1.22)
        label = DOMAIN_SHORT_LABELS.get(dom_id, dom_id)
        for j, line in enumerate(label.split("\n")):
            labels.append(
                f'<text x="{lx:.1f}" y="{ly + j * 12:.1f}" font-size="11" font-family="Inter, sans-serif" '
                f'fill="{NAVY}" text-anchor="middle" font-weight="600">{line}</text>'
            )

    # Polygone des données
    data_pts = []
    value_labels = []
    for i, dom_id in enumerate(domain_order):
        score = domain_scores.get(dom_id, 0)
        ratio = max(0.02, score / 100)
        x, y = point_at(i, ratio)
        data_pts.append((x, y))
        vx, vy = point_at(i, ratio + 0.13 if ratio < 0.85 else ratio - 0.13)
        value_labels.append(
            f'<text x="{vx:.1f}" y="{vy:.1f}" font-size="11" font-family="JetBrains Mono, monospace" '
            f'fill="{TEAL}" text-anchor="middle" font-weight="700">{score:.0f}</text>'
        )
    data_path = " ".join(f"{x:.1f},{y:.1f}" for x, y in data_pts)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{TEAL}"/>' for x, y in data_pts)

    svg = f"""
<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" xmlns="http://www.w3.org/2000/svg">
  {''.join(grid_polys)}
  {''.join(axis_lines)}
  <polygon points="{data_path}" fill="{TEAL}" fill-opacity="0.18" stroke="{TEAL}" stroke-width="2.5"/>
  {dots}
  {''.join(labels)}
  {''.join(value_labels)}
</svg>
"""
    return svg


# ============================================================
# SVG — Jauge en arc pour le score global
# ============================================================
def gauge_arc_svg(score: float, level: str, width: int = 300, height: int = 180) -> str:
    cx, cy = width / 2, height - 20
    r = width / 2 - 20
    color = LEVEL_COLORS.get(level, TEAL)

    def polar(angle_deg, radius):
        angle = math.radians(angle_deg)
        return cx + radius * math.cos(angle), cy - radius * math.sin(angle)

    start_angle, end_angle = 180, 0
    bg_x1, bg_y1 = polar(start_angle, r)
    bg_x2, bg_y2 = polar(end_angle, r)
    bg_path = f"M {bg_x1:.1f} {bg_y1:.1f} A {r} {r} 0 0 1 {bg_x2:.1f} {bg_y2:.1f}"

    value_angle = 180 - (score / 100) * 180
    val_x, val_y = polar(value_angle, r)
    large_arc = 1 if score > 50 else 0
    val_path = f"M {bg_x1:.1f} {bg_y1:.1f} A {r} {r} 0 {large_arc} 1 {val_x:.1f} {val_y:.1f}"

    return f"""
<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <path d="{bg_path}" fill="none" stroke="#E5E2DA" stroke-width="18" stroke-linecap="round"/>
  <path d="{val_path}" fill="none" stroke="{color}" stroke-width="18" stroke-linecap="round"/>
  <text x="{cx}" y="{cy - 28}" text-anchor="middle" font-family="JetBrains Mono, monospace"
        font-size="40" font-weight="700" fill="{NAVY}">{score:.0f}%</text>
  <text x="{cx}" y="{cy - 6}" text-anchor="middle" font-family="Inter, sans-serif"
        font-size="13" font-weight="600" fill="{color}">{level}</text>
</svg>
"""
