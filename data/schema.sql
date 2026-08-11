-- ============================================================
-- CMRPI Platform — Schéma de base de données (SQLite)
-- Jalon 1 — Juillet 2026
-- ============================================================

CREATE TABLE IF NOT EXISTS pme (
    id TEXT PRIMARY KEY,              -- UUID
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    sector TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS domain (
    id TEXT PRIMARY KEY,              -- UUID
    name_fr TEXT NOT NULL,
    name_en TEXT NOT NULL,
    description TEXT,
    display_order INTEGER
);

CREATE TABLE IF NOT EXISTS question (
    id TEXT PRIMARY KEY,              -- ex: 'q1'
    domain_id TEXT NOT NULL REFERENCES domain(id),
    display_order INTEGER,
    text_fr TEXT NOT NULL,
    text_en TEXT NOT NULL,
    guidance_fr TEXT,
    guidance_en TEXT
);

CREATE TABLE IF NOT EXISTS audit (
    id TEXT PRIMARY KEY,              -- UUID
    pme_id TEXT NOT NULL REFERENCES pme(id),
    global_score REAL,
    questionnaire_version TEXT DEFAULT '1.0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

CREATE TABLE IF NOT EXISTS audit_response (
    id TEXT PRIMARY KEY,              -- UUID
    audit_id TEXT NOT NULL REFERENCES audit(id),
    question_id TEXT NOT NULL REFERENCES question(id),
    response INTEGER NOT NULL CHECK (response BETWEEN 1 AND 5),
    domain_score REAL
);

CREATE TABLE IF NOT EXISTS recommendation (
    id TEXT PRIMARY KEY,              -- ex: 'rec_gov_001'
    domain_id TEXT NOT NULL REFERENCES domain(id),
    severity TEXT NOT NULL CHECK (severity IN ('Critical','High','Medium','Low')),
    priority INTEGER,
    text_fr TEXT NOT NULL,
    text_en TEXT NOT NULL,
    reference TEXT,
    effort TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,              -- UUID
    pme_id TEXT REFERENCES pme(id),
    action TEXT NOT NULL,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_pme_email ON pme(email);
CREATE INDEX IF NOT EXISTS idx_audit_pme ON audit(pme_id);
CREATE INDEX IF NOT EXISTS idx_response_audit ON audit_response(audit_id);
CREATE INDEX IF NOT EXISTS idx_question_domain ON question(domain_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_domain ON recommendation(domain_id);

-- Seed: 5 domaines
INSERT OR IGNORE INTO domain (id, name_fr, name_en, display_order) VALUES
('dom_gov', 'Gouvernance', 'Governance', 1),
('dom_acc', 'Accès & Identités', 'Access & Identity', 2),
('dom_infra', 'Infrastructure & Sécurité réseau', 'Infrastructure & Network Security', 3),
('dom_inc', 'Incidents & Continuité', 'Incident & Continuity', 4),
('dom_sens', 'Sensibilisation & Formation', 'Awareness & Training', 5);
