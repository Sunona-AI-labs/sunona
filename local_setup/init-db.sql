-- Sunona Voice AI - Database Initialization
-- This script runs when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================================================================
-- Users & Authentication
-- ==========================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    company_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================================
-- Billing
-- ==========================================================================
CREATE TABLE IF NOT EXISTS billing_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    balance DECIMAL(12, 4) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    auto_pay_enabled BOOLEAN DEFAULT false,
    auto_pay_threshold DECIMAL(10, 2) DEFAULT 10.00,
    auto_pay_amount DECIMAL(10, 2) DEFAULT 50.00,
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES billing_accounts(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'credit', 'debit', 'auto_topup'
    amount DECIMAL(12, 4) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payment_methods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES billing_accounts(id) ON DELETE CASCADE,
    type VARCHAR(50) DEFAULT 'card',
    last4 VARCHAR(4),
    brand VARCHAR(50),
    exp_month INTEGER,
    exp_year INTEGER,
    is_default BOOLEAN DEFAULT false,
    stripe_payment_method_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================================
-- Usage Tracking
-- ==========================================================================
CREATE TABLE IF NOT EXISTS usage_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES billing_accounts(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'stt', 'tts', 'llm', 'telephony'
    quantity DECIMAL(12, 4) NOT NULL,
    unit VARCHAR(50), -- 'minutes', 'characters', 'tokens'
    unit_cost DECIMAL(12, 6),
    total_cost DECIMAL(12, 4),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================================
-- Knowledge Bases
-- ==========================================================================
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    total_chunks INTEGER DEFAULT 0,
    total_words INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    knowledge_base_id UUID REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    source VARCHAR(500),
    source_type VARCHAR(50),
    title VARCHAR(255),
    metadata JSONB,
    embedding VECTOR(1536), -- For OpenAI embeddings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================================
-- Agents
-- ==========================================================================
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) DEFAULT 'contextual',
    system_prompt TEXT,
    knowledge_base_id UUID REFERENCES knowledge_bases(id),
    config JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================================
-- Call Logs
-- ==========================================================================
CREATE TABLE IF NOT EXISTS call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id),
    call_sid VARCHAR(255),
    from_number VARCHAR(50),
    to_number VARCHAR(50),
    direction VARCHAR(20), -- 'inbound', 'outbound'
    duration_seconds INTEGER,
    status VARCHAR(50),
    transcript TEXT,
    summary TEXT,
    cost DECIMAL(10, 4),
    metadata JSONB,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================================
-- Indexes
-- ==========================================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_usage_events_account ON usage_events(account_id);
CREATE INDEX IF NOT EXISTS idx_usage_events_type ON usage_events(type);
CREATE INDEX IF NOT EXISTS idx_call_logs_user ON call_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_call_logs_started ON call_logs(started_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_kb ON knowledge_chunks(knowledge_base_id);

-- ==========================================================================
-- Default Admin User (password: admin123)
-- ==========================================================================
INSERT INTO users (email, password_hash, name, is_admin)
VALUES (
    'admin@sunona.ai',
    crypt('admin123', gen_salt('bf')),
    'Admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- Create billing account for admin
INSERT INTO billing_accounts (user_id, balance)
SELECT id, 100.00
FROM users WHERE email = 'admin@sunona.ai'
ON CONFLICT DO NOTHING;
