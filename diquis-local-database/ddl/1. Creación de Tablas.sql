-- =============================================================
-- ARCHIVO 1: DDL ESTRUCTURA
-- PostgreSQL 18+
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto"; 

CREATE TYPE account_type_enum      AS ENUM ('checking', 'saving', 'cash', 'digital');
CREATE TYPE sso_provider_enum      AS ENUM ('google', 'outlook', 'local');
CREATE TYPE transaction_type_enum  AS ENUM ('income', 'expense', 'transfer');
CREATE TYPE payment_method_enum    AS ENUM ('cash', 'debit', 'credit', 'transfer', 'sinpe', 'digital');
CREATE TYPE transport_type_enum    AS ENUM ('bus', 'taxi', 'uber', 'train', 'walk', 'bike', 'other');
CREATE TYPE transport_purpose_enum AS ENUM ('work', 'leisure', 'emergency', 'health', 'education', 'other');
CREATE TYPE frequency_enum         AS ENUM ('once', 'daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly');
CREATE TYPE credit_status_enum     AS ENUM ('active', 'paid', 'cancelled');
CREATE TYPE installment_status_enum AS ENUM ('pending', 'paid', 'overdue');
CREATE TYPE goal_status_enum       AS ENUM ('active', 'reached', 'cancelled');
CREATE TYPE category_domain_enum    AS ENUM (
    'grocery', 'transport', 'food_out', 'home', 'health', 
    'entertainment', 'education', 'income', 'savings', 'utilities', 
    'shopping', 'personal_care', 'family', 'other'
);

CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE app.users (
    id               UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    email            VARCHAR(255) NOT NULL UNIQUE,
    full_name        VARCHAR(255) NOT NULL,
    date_of_birth    DATE,
    country_code     CHAR(2)      NOT NULL DEFAULT 'CR',
    default_currency CHAR(3)      NOT NULL DEFAULT 'CRC',
    timezone         VARCHAR(50)  NOT NULL DEFAULT 'America/Costa_Rica',
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_users_timezone_format CHECK (timezone ~ '^[A-Za-z_-]+(/[A-Za-z_-]+)+$')
);

CREATE TABLE app.sso_providers (
    id               UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id          UUID        NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    provider         sso_provider_enum NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    access_token_hash TEXT,
    refresh_token_hash TEXT,
    token_expires_at TIMESTAMPTZ,
    linked_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (provider, provider_user_id)
);

CREATE TABLE app.accounts (
    id                     UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                UUID         NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    name                   VARCHAR(100) NOT NULL,                
    account_type           account_type_enum NOT NULL,
    currency               CHAR(3)      NOT NULL DEFAULT 'CRC',
    initial_balance        NUMERIC(15,2) NOT NULL DEFAULT 0,
    current_balance        NUMERIC(15,2) NOT NULL DEFAULT 0,      
    allow_negative_balance BOOLEAN      NOT NULL DEFAULT FALSE,
    theme_color            VARCHAR(20)  NOT NULL DEFAULT 'silver',
    is_active              BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    is_system              BOOLEAN      NOT NULL DEFAULT FALSE
);

CREATE TABLE app.categories (
    id                   UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id              UUID     REFERENCES app.users(id) ON DELETE CASCADE,
    name                 VARCHAR(100) NOT NULL,
    domain               category_domain_enum NOT NULL,
    icon                 VARCHAR(50),         
    is_system            BOOLEAN  NOT NULL DEFAULT FALSE,
    is_essential_default BOOLEAN  NOT NULL DEFAULT FALSE,
    sort_order           INT      NOT NULL DEFAULT 0,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_system_no_user CHECK ((is_system = TRUE AND user_id IS NULL) OR (is_system = FALSE))
);

CREATE TABLE app.user_category_overrides (
    user_id UUID NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES app.categories(id) ON DELETE CASCADE,
    custom_icon VARCHAR(50),      
    custom_name VARCHAR(100),     
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, category_id)
);

CREATE TABLE app.subcategories (
    id                   UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id          UUID     NOT NULL REFERENCES app.categories(id) ON DELETE CASCADE,
    user_id              UUID     REFERENCES app.users(id) ON DELETE CASCADE,
    name                 VARCHAR(100) NOT NULL,
    is_system            BOOLEAN  NOT NULL DEFAULT FALSE,
    is_essential_default BOOLEAN  NOT NULL DEFAULT FALSE,
    sort_order           INT      NOT NULL DEFAULT 0,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_sub_system_no_user CHECK ((is_system = TRUE AND user_id IS NULL) OR (is_system = FALSE))
);

CREATE TABLE app.tax_rates (
    id           UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    country_code CHAR(2)  NOT NULL,
    rate_name    VARCHAR(100) NOT NULL,   
    rate_pct     NUMERIC(5,2) NOT NULL,   
    valid_from   DATE     NOT NULL,
    valid_until  DATE,                      
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_valid_dates CHECK (valid_until IS NULL OR valid_until > valid_from)
);

CREATE TABLE app.exchange_rates (
    id            UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_currency CHAR(3)  NOT NULL,
    to_currency   CHAR(3)  NOT NULL,
    rate          NUMERIC(12,4) NOT NULL,
    rate_date     DATE     NOT NULL,
    source        VARCHAR(50) NOT NULL DEFAULT 'BCCR',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (from_currency, to_currency, rate_date, source)
);

CREATE TABLE app.credit_plans (
    id                 UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id            UUID     NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    account_id         UUID     NOT NULL REFERENCES app.accounts(id),
    description        TEXT     NOT NULL,              
    total_amount       NUMERIC(15,2) NOT NULL,
    interest_rate_pct  NUMERIC(5,2)  NOT NULL DEFAULT 0,  
    total_installments INT      NOT NULL CHECK (total_installments >= 1),
    start_date         DATE     NOT NULL,
    currency           CHAR(3)  NOT NULL DEFAULT 'CRC',
    status             credit_status_enum NOT NULL DEFAULT 'active',
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE app.transactions (
    id                         UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                    UUID     NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    account_id                 UUID     NOT NULL REFERENCES app.accounts(id),
    category_id                UUID     REFERENCES app.categories(id) ON DELETE SET NULL, 
    type                       transaction_type_enum NOT NULL,
    amount                     NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    currency                   CHAR(3)  NOT NULL DEFAULT 'CRC',
    exchange_rate              NUMERIC(12,4) NOT NULL DEFAULT 1,
    exchange_source            VARCHAR(10)   NOT NULL DEFAULT 'none',
    amount_in_account_currency NUMERIC(15,2) NOT NULL DEFAULT 0, 
    occurred_at                TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    description                TEXT,
    is_essential               BOOLEAN  NOT NULL DEFAULT FALSE,
    essential_reason           TEXT,                               
    payment_method             payment_method_enum NOT NULL DEFAULT 'cash',
    credit_plan_id             UUID     REFERENCES app.credit_plans(id) ON DELETE SET NULL,
    is_refund_of               UUID     REFERENCES app.transactions(id) ON DELETE SET NULL,
    transfer_to_account_id     UUID     REFERENCES app.accounts(id),
    notes                      TEXT,
    is_deleted                 BOOLEAN  NOT NULL DEFAULT FALSE,
    deleted_at                 TIMESTAMPTZ,
    created_at                 TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                 TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_transfer_needs_destination CHECK (
        (type = 'transfer' AND transfer_to_account_id IS NOT NULL) OR 
        (type != 'transfer')
    ),
    CONSTRAINT chk_transfer_different_accounts CHECK (
        transfer_to_account_id IS NULL OR transfer_to_account_id != account_id
    )
);

CREATE TABLE app.transaction_items (
    id             UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID     NOT NULL REFERENCES app.transactions(id) ON DELETE CASCADE,
    user_id        UUID     NOT NULL REFERENCES app.users(id) ON DELETE CASCADE, 
    product_name   VARCHAR(255) NOT NULL,
    brand          VARCHAR(100),
    subcategory_id UUID     REFERENCES app.subcategories(id) ON DELETE SET NULL,  
    quantity       NUMERIC(10,3) NOT NULL DEFAULT 1,
    unit           VARCHAR(20) NOT NULL DEFAULT 'unidad',   
    unit_price     NUMERIC(15,2) NOT NULL,
    has_tax        BOOLEAN  NOT NULL DEFAULT FALSE,
    tax_rate_id    UUID     REFERENCES app.tax_rates(id) ON DELETE SET NULL,
    tax_amount     NUMERIC(15,2) NOT NULL DEFAULT 0,        
    line_total     NUMERIC(15,2) NOT NULL,                  
    is_essential   BOOLEAN  NOT NULL DEFAULT FALSE,         
    nutrition_flags JSONB,   
    extra_meta     JSONB,    
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_line_total_positive CHECK (line_total >= 0),
    CONSTRAINT chk_tax_needs_rate CHECK ((has_tax = FALSE) OR (has_tax = TRUE AND tax_rate_id IS NOT NULL))
);

CREATE TABLE app.tags (
    id          UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID     NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    name        VARCHAR(50) NOT NULL, 
    color_hex   VARCHAR(7),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, name)
);

CREATE TABLE app.item_tags (
    item_id     UUID     NOT NULL REFERENCES app.transaction_items(id) ON DELETE CASCADE,
    tag_id      UUID     NOT NULL REFERENCES app.tags(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (item_id, tag_id)
);

CREATE TABLE app.transport_details (
    id             UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID     NOT NULL UNIQUE REFERENCES app.transactions(id) ON DELETE CASCADE,
    transport_type transport_type_enum NOT NULL,
    purpose        transport_purpose_enum NOT NULL DEFAULT 'other',
    origin         VARCHAR(255),
    destination    VARCHAR(255),
    distance_km    NUMERIC(8,2),
    was_planned    BOOLEAN  NOT NULL DEFAULT TRUE,    
    passengers     INT      NOT NULL DEFAULT 1,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE app.income_details (
    id                 UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id     UUID     NOT NULL UNIQUE REFERENCES app.transactions(id) ON DELETE CASCADE,
    income_type        VARCHAR(50) NOT NULL,   
    gross_amount       NUMERIC(15,2) NOT NULL,
    deduction_ccss     NUMERIC(15,2) NOT NULL DEFAULT 0,
    deduction_ins      NUMERIC(15,2) NOT NULL DEFAULT 0,
    deduction_rent_tax NUMERIC(15,2) NOT NULL DEFAULT 0,
    other_deductions   NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_amount         NUMERIC(15,2) NOT NULL,  
    employer           VARCHAR(255),
    period_start       DATE,
    period_end         DATE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE app.credit_installments (
    id                 UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id            UUID     NOT NULL REFERENCES app.credit_plans(id) ON DELETE CASCADE,
    installment_number INT      NOT NULL CHECK (installment_number >= 1),
    due_date           DATE     NOT NULL,
    amount             NUMERIC(15,2) NOT NULL,
    principal_part     NUMERIC(15,2) NOT NULL DEFAULT 0,
    interest_part      NUMERIC(15,2) NOT NULL DEFAULT 0,
    status             installment_status_enum NOT NULL DEFAULT 'pending',
    transaction_id     UUID     REFERENCES app.transactions(id) ON DELETE SET NULL,
    payment_currency   CHAR(3),
    payment_exchange_rate NUMERIC(12,4) DEFAULT 1,
    paid_at            TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (plan_id, installment_number)
);

CREATE TABLE app.scheduled_transactions (
    id                  UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID     NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    account_id          UUID     NOT NULL REFERENCES app.accounts(id),
    transfer_to_account_id UUID  REFERENCES app.accounts(id),
    category_id         UUID     REFERENCES app.categories(id) ON DELETE SET NULL,
    type                transaction_type_enum NOT NULL,
    name                VARCHAR(100) NOT NULL,        
    expected_amount     NUMERIC(15,2) NOT NULL,
    currency            CHAR(3)  NOT NULL DEFAULT 'CRC',
    is_estimated        BOOLEAN  NOT NULL DEFAULT FALSE,
    frequency           frequency_enum NOT NULL DEFAULT 'monthly',
    next_due_date       DATE     NOT NULL,
    is_essential        BOOLEAN  NOT NULL DEFAULT FALSE,
    is_active           BOOLEAN  NOT NULL DEFAULT TRUE,
    auto_execute        BOOLEAN  NOT NULL DEFAULT FALSE,
    last_transaction_id UUID REFERENCES app.transactions(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_scheduled_transfer_needs_dest CHECK (
        (type = 'transfer' AND transfer_to_account_id IS NOT NULL) OR 
        (type != 'transfer')
    ),
    CONSTRAINT chk_scheduled_transfer_diff_acc CHECK (
        transfer_to_account_id IS NULL OR transfer_to_account_id != account_id
    )
);

CREATE TABLE app.savings_goals (
    id             UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id        UUID     NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    account_id     UUID     REFERENCES app.accounts(id) ON DELETE SET NULL,
    name           VARCHAR(100) NOT NULL,          
    target_amount  NUMERIC(15,2) NOT NULL,
    current_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
    currency       CHAR(3)  NOT NULL DEFAULT 'CRC',
    deadline       DATE,
    status         goal_status_enum NOT NULL DEFAULT 'active',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE app.budgets (
    id                   UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id              UUID     NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    category_id          UUID     NOT NULL REFERENCES app.categories(id) ON DELETE CASCADE,
    period_month         DATE     NOT NULL,    
    amount               NUMERIC(15,2) NOT NULL,
    currency             CHAR(3)  NOT NULL DEFAULT 'CRC',
    alert_threshold_pct  INT      NOT NULL DEFAULT 80 CHECK (alert_threshold_pct BETWEEN 1 AND 100),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, category_id, period_month)
);

CREATE TABLE app.token_blacklist (
    token_jti UUID PRIMARY KEY,
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE app.password_resets (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    token_hash  TEXT NOT NULL, 
    expires_at  TIMESTAMPTZ NOT NULL, 
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    used_at     TIMESTAMPTZ,
    ip_address  INET, 
    user_agent  TEXT
);

-- =============================================================
-- ÍNDICES
-- =============================================================
CREATE INDEX idx_users_email        ON app.users(email);
CREATE INDEX idx_sso_user           ON app.sso_providers(user_id);
CREATE INDEX idx_accounts_user      ON app.accounts(user_id);
CREATE INDEX idx_cat_user           ON app.categories(user_id);
CREATE INDEX idx_cat_domain         ON app.categories(domain);
CREATE INDEX idx_subcat_category    ON app.subcategories(category_id);
CREATE INDEX idx_subcat_user        ON app.subcategories(user_id);

CREATE INDEX idx_tx_user            ON app.transactions(user_id);
CREATE INDEX idx_tx_account         ON app.transactions(account_id);
CREATE INDEX idx_tx_category        ON app.transactions(category_id);
CREATE INDEX idx_tx_type            ON app.transactions(type);
CREATE INDEX idx_tx_essential       ON app.transactions(user_id, is_essential);

CREATE INDEX idx_tx_active_user_date ON app.transactions(user_id, occurred_at DESC) WHERE is_deleted = FALSE;

CREATE INDEX idx_items_tx           ON app.transaction_items(transaction_id);
CREATE INDEX idx_items_user         ON app.transaction_items(user_id);
CREATE INDEX idx_items_subcat       ON app.transaction_items(subcategory_id);
CREATE INDEX idx_items_product      ON app.transaction_items(product_name);
CREATE INDEX idx_items_brand        ON app.transaction_items(brand) WHERE brand IS NOT NULL;
CREATE INDEX idx_items_nutrition    ON app.transaction_items USING GIN(nutrition_flags) WHERE nutrition_flags IS NOT NULL;
CREATE INDEX idx_tags_user          ON app.tags(user_id);
CREATE INDEX idx_item_tags_tag      ON app.item_tags(tag_id);
CREATE INDEX idx_transport_tx       ON app.transport_details(transaction_id);
CREATE INDEX idx_inst_plan          ON app.credit_installments(plan_id);
CREATE INDEX idx_inst_due           ON app.credit_installments(due_date, status);
CREATE INDEX idx_scheduled_due ON app.scheduled_transactions(next_due_date) WHERE is_active = TRUE;
CREATE INDEX idx_scheduled_user ON app.scheduled_transactions(user_id);
CREATE INDEX idx_budget_user_month  ON app.budgets(user_id, period_month DESC);

-- =============================================================
-- ROW-LEVEL SECURITY (RLS)
-- =============================================================
CREATE OR REPLACE FUNCTION app.current_user_id()
RETURNS UUID LANGUAGE sql STABLE AS $$
    SELECT NULLIF(current_setting('app.current_user_id', TRUE), '')::UUID;
$$;

ALTER TABLE app.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY users_isolation ON app.users USING (id = app.current_user_id());

ALTER TABLE app.sso_providers ENABLE ROW LEVEL SECURITY;
CREATE POLICY sso_providers_isolation ON app.sso_providers USING (user_id = app.current_user_id());

ALTER TABLE app.accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY accounts_isolation ON app.accounts USING (user_id = app.current_user_id());

ALTER TABLE app.transactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY transactions_isolation ON app.transactions USING (user_id = app.current_user_id());

ALTER TABLE app.transaction_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY items_isolation ON app.transaction_items USING (user_id = app.current_user_id());

ALTER TABLE app.tags ENABLE ROW LEVEL SECURITY;
CREATE POLICY tags_isolation ON app.tags USING (user_id = app.current_user_id());

ALTER TABLE app.item_tags ENABLE ROW LEVEL SECURITY;
CREATE POLICY item_tags_isolation ON app.item_tags USING (
    item_id IN (SELECT id FROM app.transaction_items WHERE user_id = app.current_user_id())
);

ALTER TABLE app.transport_details ENABLE ROW LEVEL SECURITY;
CREATE POLICY transport_isolation ON app.transport_details USING (
    transaction_id IN (SELECT id FROM app.transactions WHERE user_id = app.current_user_id())
);

ALTER TABLE app.income_details ENABLE ROW LEVEL SECURITY;
CREATE POLICY income_details_isolation ON app.income_details USING (
    transaction_id IN (SELECT id FROM app.transactions WHERE user_id = app.current_user_id())
);

ALTER TABLE app.credit_plans ENABLE ROW LEVEL SECURITY;
CREATE POLICY credit_plans_isolation ON app.credit_plans USING (user_id = app.current_user_id());

ALTER TABLE app.credit_installments ENABLE ROW LEVEL SECURITY;
CREATE POLICY installments_isolation ON app.credit_installments USING (
    plan_id IN (SELECT id FROM app.credit_plans WHERE user_id = app.current_user_id())
);

ALTER TABLE app.scheduled_transactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY scheduled_isolation ON app.scheduled_transactions USING (user_id = app.current_user_id());

ALTER TABLE app.savings_goals ENABLE ROW LEVEL SECURITY;
CREATE POLICY goals_isolation ON app.savings_goals USING (user_id = app.current_user_id());

ALTER TABLE app.budgets ENABLE ROW LEVEL SECURITY;
CREATE POLICY budgets_isolation ON app.budgets USING (user_id = app.current_user_id());

ALTER TABLE app.categories ENABLE ROW LEVEL SECURITY;
CREATE POLICY categories_isolation ON app.categories USING (is_system = TRUE OR user_id = app.current_user_id());

ALTER TABLE app.user_category_overrides ENABLE ROW LEVEL SECURITY;
CREATE POLICY overrides_isolation ON app.user_category_overrides USING (user_id = app.current_user_id());

ALTER TABLE app.subcategories ENABLE ROW LEVEL SECURITY;
CREATE POLICY subcategories_isolation ON app.subcategories USING (is_system = TRUE OR user_id = app.current_user_id());