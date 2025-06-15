-- NEO Database Seed Data
-- This script creates initial data for development

-- Create default admin user
INSERT INTO users (id, email, password_hash, full_name, email_verified, is_active)
VALUES (
    uuid_generate_v4(),
    'admin@neo.local',
    crypt('admin123', gen_salt('bf')),
    'NEO Administrator',
    TRUE,
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Create default account for admin
INSERT INTO accounts (id, name, slug, personal_account, billing_email)
VALUES (
    uuid_generate_v4(),
    'Default Account',
    'default',
    TRUE,
    'admin@neo.local'
) ON CONFLICT (slug) DO NOTHING;

-- Link admin user to default account
INSERT INTO account_users (account_id, user_id, role)
SELECT 
    a.id,
    u.id,
    'owner'
FROM accounts a, users u
WHERE a.slug = 'default' 
AND u.email = 'admin@neo.local'
ON CONFLICT (account_id, user_id) DO NOTHING;

-- Create default project
INSERT INTO projects (id, name, description, account_id, is_public)
SELECT 
    uuid_generate_v4(),
    'Default Project',
    'Default project for NEO agents',
    a.id,
    FALSE
FROM accounts a
WHERE a.slug = 'default'
ON CONFLICT DO NOTHING;