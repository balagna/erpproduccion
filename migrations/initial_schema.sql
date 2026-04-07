-- initial_schema.sql
-- Referencia de esquema inicial para V5.1

CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS role_permissions (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) NOT NULL,
    permission_id INTEGER NOT NULL REFERENCES permissions(id)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    company_id INTEGER REFERENCES companies(id),
    branch_id INTEGER REFERENCES branches(id),
    is_active_user BOOLEAN NOT NULL DEFAULT TRUE,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ NULL,
    last_login_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL,
    two_factor_email_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    two_factor_totp_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    totp_secret VARCHAR(64) NULL
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS email_otps (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    code VARCHAR(12) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NULL REFERENCES users(id),
    action VARCHAR(120) NOT NULL,
    detail TEXT NULL,
    ip_address VARCHAR(80) NULL,
    created_at TIMESTAMPTZ NOT NULL
);
