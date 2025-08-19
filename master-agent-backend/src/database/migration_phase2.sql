-- Phase 2 schema updates for ResearchResult and user preferences

-- 1. Research Results Table
CREATE TABLE IF NOT EXISTS research_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_url TEXT NOT NULL,
    source_type VARCHAR(100) NOT NULL,
    title TEXT,
    author TEXT,
    published_at TIMESTAMP,
    raw_text TEXT,
    content_summary TEXT,
    key_points JSONB,
    tags JSONB,
    sentiment VARCHAR(50),
    importance_score INTEGER,
    category VARCHAR(100),
    storage_key TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Extend users table with preferences JSONB column
ALTER TABLE users
ADD COLUMN IF NOT EXISTS preferences JSONB;