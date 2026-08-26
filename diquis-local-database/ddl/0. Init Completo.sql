-- =============================================================
-- SCRIPT MAESTRO DE INICIALIZACIÓN DE DIQUIS (RECONSTRUCCIÓN TOTAL)
-- =============================================================
-- ADVERTENCIA: Esto destruirá el esquema 'app' y todos sus datos.
-- =============================================================

DROP SCHEMA IF EXISTS app CASCADE;

DROP TYPE IF EXISTS account_type_enum CASCADE;
DROP TYPE IF EXISTS sso_provider_enum CASCADE;
DROP TYPE IF EXISTS transaction_type_enum CASCADE;
DROP TYPE IF EXISTS payment_method_enum CASCADE;
DROP TYPE IF EXISTS transport_type_enum CASCADE;
DROP TYPE IF EXISTS transport_purpose_enum CASCADE;
DROP TYPE IF EXISTS frequency_enum CASCADE;
DROP TYPE IF EXISTS credit_status_enum CASCADE;
DROP TYPE IF EXISTS installment_status_enum CASCADE;
DROP TYPE IF EXISTS goal_status_enum CASCADE;
DROP TYPE IF EXISTS category_domain_enum CASCADE;

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
-- ÃNDICES
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



-- =============================================================
-- ARCHIVO 2: FUNCIONES Y TRIGGERS
-- Esquema: app
-- =============================================================

-- =============================================================
-- PARTE 1: FUNCIONES (LÃ³gica de Negocio)
-- =============================================================

-- 1.1 AUTOMATIZACIÃ“N DE FECHAS
CREATE OR REPLACE FUNCTION app.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- 1.2 CÃLCULO DEFENSIVO DEL MONTO EN MONEDA LOCAL
CREATE OR REPLACE FUNCTION app.compute_amount_in_account_currency()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    _src_currency CHAR(3);
BEGIN
    SELECT currency INTO _src_currency FROM app.accounts WHERE id = NEW.account_id;

    IF NEW.currency = _src_currency THEN
        NEW.amount_in_account_currency := NEW.amount;
    ELSE
        NEW.amount_in_account_currency := NEW.amount * NEW.exchange_rate;
    END IF;

    RETURN NEW;
END;
$$;

-- 1.3 MOTOR FINANCIERO: SALDOS EN TIEMPO REAL (LÃ“GICA BLINDADA POR DELTAS)
CREATE OR REPLACE FUNCTION app.update_account_balance()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    _old_src_curr CHAR(3);
    _old_dst_curr CHAR(3);
    _old_dst_impact NUMERIC := 0;

    _new_src_curr CHAR(3);
    _new_dst_curr CHAR(3);
    _new_dst_impact NUMERIC := 0;
BEGIN
    -- =========================================================
    -- LÃ“GICA UNIVERSAL: Â¿CuÃ¡nto dinero REAL entra al Destino?
    -- =========================================================
    IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
        IF OLD.type = 'transfer' AND OLD.transfer_to_account_id IS NOT NULL THEN
            SELECT currency INTO _old_src_curr FROM app.accounts WHERE id = OLD.account_id;
            SELECT currency INTO _old_dst_curr FROM app.accounts WHERE id = OLD.transfer_to_account_id;

            -- Caso 1: Origen CRC -> Destino CRC (Sin importar si Tx fue en USD o EUR)
            IF _old_dst_curr = _old_src_curr THEN
                _old_dst_impact := OLD.amount_in_account_currency;
                
            -- Caso 2: Origen CRC -> Destino USD (Tx fue en USD)
            ELSIF _old_dst_curr = OLD.currency THEN
                _old_dst_impact := OLD.amount;
                
            -- Caso 3: Origen USD -> Destino CRC (Tx fue en USD o diferente)
            ELSE
                _old_dst_impact := OLD.amount_in_account_currency * OLD.exchange_rate;
            END IF;
        END IF;
    END IF;

    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        IF NEW.type = 'transfer' AND NEW.transfer_to_account_id IS NOT NULL THEN
            SELECT currency INTO _new_src_curr FROM app.accounts WHERE id = NEW.account_id;
            SELECT currency INTO _new_dst_curr FROM app.accounts WHERE id = NEW.transfer_to_account_id;

            -- Caso A: Misma moneda entre cuentas (Arregla tu bug actual)
            IF _new_dst_curr = _new_src_curr THEN
                _new_dst_impact := NEW.amount_in_account_currency;
                
            -- Caso B: La cuenta destino estÃ¡ en la misma moneda que la transacciÃ³n
            ELSIF _new_dst_curr = NEW.currency THEN
                _new_dst_impact := NEW.amount;
                
            -- Caso C: Cruce complejo (Multiplica por el rate que proveyÃ³ el usuario)
            ELSE
                _new_dst_impact := NEW.amount_in_account_currency * NEW.exchange_rate;
            END IF;
        END IF;
    END IF;

    -- ==========================================
    -- MANEJO DE DELETE
    -- ==========================================
    IF TG_OP = 'DELETE' THEN
        IF OLD.is_deleted = FALSE THEN
            IF OLD.type = 'income' THEN
                UPDATE app.accounts SET current_balance = current_balance - OLD.amount_in_account_currency WHERE id = OLD.account_id;
            ELSIF OLD.type = 'expense' THEN
                UPDATE app.accounts SET current_balance = current_balance + OLD.amount_in_account_currency WHERE id = OLD.account_id;
            ELSIF OLD.type = 'transfer' THEN
                UPDATE app.accounts SET current_balance = current_balance + OLD.amount_in_account_currency WHERE id = OLD.account_id;
                UPDATE app.accounts SET current_balance = current_balance - _old_dst_impact WHERE id = OLD.transfer_to_account_id;
            END IF;
        END IF;
        RETURN OLD;
    END IF;

    -- ==========================================
    -- MANEJO DE INSERT
    -- ==========================================
    IF TG_OP = 'INSERT' THEN
        IF NEW.is_deleted = FALSE THEN
            IF NEW.type = 'income' THEN
                UPDATE app.accounts SET current_balance = current_balance + NEW.amount_in_account_currency WHERE id = NEW.account_id;
            ELSIF NEW.type = 'expense' THEN
                UPDATE app.accounts SET current_balance = current_balance - NEW.amount_in_account_currency WHERE id = NEW.account_id;
            ELSIF NEW.type = 'transfer' THEN
                UPDATE app.accounts SET current_balance = current_balance - NEW.amount_in_account_currency WHERE id = NEW.account_id;
                UPDATE app.accounts SET current_balance = current_balance + _new_dst_impact WHERE id = NEW.transfer_to_account_id;
            END IF;
        END IF;
        RETURN NEW;
    END IF;

    -- ==========================================
    -- MANEJO DE UPDATE (LÃ“GICA CON JOINS SEGUROS)
    -- ==========================================
    IF TG_OP = 'UPDATE' THEN
        WITH deltas AS (
            -- 1. REVERTIR transacciÃ³n VIEJA
            SELECT OLD.account_id AS acc_id,
                   CASE
                       WHEN OLD.type = 'income' THEN -OLD.amount_in_account_currency
                       WHEN OLD.type = 'expense' THEN OLD.amount_in_account_currency
                       WHEN OLD.type = 'transfer' THEN OLD.amount_in_account_currency
                       ELSE 0
                   END AS amount
            WHERE OLD.is_deleted = FALSE

            UNION ALL

            SELECT OLD.transfer_to_account_id AS acc_id,
                   -_old_dst_impact AS amount
            WHERE OLD.is_deleted = FALSE AND OLD.type = 'transfer'

            UNION ALL

            -- 2. APLICAR transacciÃ³n NUEVA
            SELECT NEW.account_id AS acc_id,
                   CASE
                       WHEN NEW.type = 'income' THEN NEW.amount_in_account_currency
                       WHEN NEW.type = 'expense' THEN -NEW.amount_in_account_currency
                       WHEN NEW.type = 'transfer' THEN -NEW.amount_in_account_currency
                       ELSE 0
                   END AS amount
            WHERE NEW.is_deleted = FALSE

            UNION ALL

            SELECT NEW.transfer_to_account_id AS acc_id,
                   _new_dst_impact AS amount
            WHERE NEW.is_deleted = FALSE AND NEW.type = 'transfer'
        ),
        grouped_deltas AS (
            SELECT acc_id, SUM(amount) AS net_change
            FROM deltas
            WHERE acc_id IS NOT NULL
            GROUP BY acc_id
            HAVING SUM(amount) != 0
        )
        UPDATE app.accounts a
        SET current_balance = a.current_balance + gd.net_change
        FROM grouped_deltas gd
        WHERE a.id = gd.acc_id;

        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$;

-- 1.4 NUEVO: VALIDACIÃ“N DIFERIDA DE SALDOS NEGATIVOS (REEMPLAZA AL CHECK)
CREATE OR REPLACE FUNCTION app.check_negative_balance()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- Validamos si la cuenta permite negativos, si no, y estÃ¡ en rojo, disparamos error
    IF NEW.current_balance < 0 AND NEW.allow_negative_balance = FALSE THEN
        -- Lanzamos este texto especÃ­fico para que FastAPI lo atrape y envÃ­e el banner elegante
        RAISE EXCEPTION 'chk_no_negative_balance';
    END IF;
    RETURN NEW;
END;
$$;

-- 1.5 VALIDACIÃ“N DE INTEGRIDAD EN CRÃ‰DITOS
CREATE OR REPLACE FUNCTION app.validate_credit_installments_sum()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    _total_plan NUMERIC;
    _current_principal_sum NUMERIC;
BEGIN
    SELECT total_amount INTO _total_plan 
    FROM app.credit_plans WHERE id = NEW.plan_id;
    
    SELECT COALESCE(SUM(principal_part), 0) INTO _current_principal_sum 
    FROM app.credit_installments 
    WHERE plan_id = NEW.plan_id AND id != NEW.id;
    
    IF (_current_principal_sum + NEW.principal_part) > _total_plan THEN
        RAISE EXCEPTION 'Integridad Financiera: La suma del capital (%) excede el total del plan (%)', 
            (_current_principal_sum + NEW.principal_part), _total_plan;
    END IF;
    
    RETURN NEW;
END;
$$;

-- 1.6 BOTÃ“N DE PÃNICO: RECONCILIACIÃ“N MASIVA DE SALDOS
CREATE OR REPLACE FUNCTION app.reconcile_account(_account_id UUID)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE app.accounts a
    SET current_balance = a.initial_balance + (
        SELECT COALESCE(SUM(
            CASE 
                WHEN t.type = 'income' THEN t.amount_in_account_currency
                WHEN t.type = 'expense' THEN -t.amount_in_account_currency
                WHEN t.type = 'transfer' AND t.account_id = a.id THEN -t.amount_in_account_currency
                WHEN t.type = 'transfer' AND t.transfer_to_account_id = a.id THEN t.amount_in_account_currency
                ELSE 0 
            END
        ), 0)
        FROM app.transactions t
        WHERE (t.account_id = a.id OR t.transfer_to_account_id = a.id)
          AND t.is_deleted = FALSE
    )
    WHERE a.id = _account_id;
END;
$$;

-- 1.7 CREADOR AUTOMÃTICO DE DATOS PARA USUARIOS NUEVOS
CREATE OR REPLACE FUNCTION app.create_default_user_data()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO app.accounts 
        (user_id, name, account_type, currency, theme_color, is_system, allow_negative_balance)
    VALUES 
        (NEW.id, 'Billetera Principal', 'checking', NEW.default_currency, 'silver', FALSE, TRUE);

    INSERT INTO app.accounts 
        (user_id, name, account_type, currency, theme_color, is_system, allow_negative_balance)
    VALUES 
        (NEW.id, 'Cuenta de Ahorros', 'saving', NEW.default_currency, 'green', FALSE, FALSE);

    RETURN NEW;
END;
$$;


-- =============================================================
-- PARTE 2: TRIGGERS (Disparadores de Base de Datos)
-- =============================================================

-- 2.1 Triggers de AuditorÃ­a
DROP TRIGGER IF EXISTS trg_users_updated_at ON app.users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON app.users
    FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

DROP TRIGGER IF EXISTS trg_transactions_updated_at ON app.transactions;
CREATE TRIGGER trg_transactions_updated_at
    BEFORE UPDATE ON app.transactions
    FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

-- 2.2 Trigger de CÃ¡lculo de Moneda (Se ejecuta ANTES para preparar los datos)
DROP TRIGGER IF EXISTS trg_compute_amount_in_currency ON app.transactions;
CREATE TRIGGER trg_compute_amount_in_currency
    BEFORE INSERT OR UPDATE ON app.transactions
    FOR EACH ROW EXECUTE FUNCTION app.compute_amount_in_account_currency();


-- 2.3 Trigger del Motor Financiero (Se ejecuta DESPUÃ‰S de guardar la transacciÃ³n)
DROP TRIGGER IF EXISTS trg_update_balance ON app.transactions;
CREATE TRIGGER trg_update_balance
    AFTER INSERT OR DELETE ON app.transactions
    FOR EACH ROW EXECUTE FUNCTION app.update_account_balance();

DROP TRIGGER IF EXISTS trg_update_balance_on_change ON app.transactions;
CREATE TRIGGER trg_update_balance_on_change
    AFTER UPDATE ON app.transactions
    FOR EACH ROW 
    WHEN (
        OLD.amount_in_account_currency IS DISTINCT FROM NEW.amount_in_account_currency OR
        OLD.account_id IS DISTINCT FROM NEW.account_id OR
        OLD.transfer_to_account_id IS DISTINCT FROM NEW.transfer_to_account_id OR
        OLD.type IS DISTINCT FROM NEW.type OR
        OLD.is_deleted IS DISTINCT FROM NEW.is_deleted
    )
    EXECUTE FUNCTION app.update_account_balance();

-- 2.4 TRIGGER DE RESTRICCIÃ“N DIFERIDO PARA SALDOS (Se ejecuta al momento del db.commit)
DROP TRIGGER IF EXISTS trg_chk_no_negative_balance ON app.accounts;
CREATE CONSTRAINT TRIGGER trg_chk_no_negative_balance
    AFTER INSERT OR UPDATE ON app.accounts
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION app.check_negative_balance();

-- 2.5 Trigger de ValidaciÃ³n de CrÃ©ditos
DROP TRIGGER IF EXISTS trg_validate_installments ON app.credit_installments;
CREATE TRIGGER trg_validate_installments
    BEFORE INSERT OR UPDATE ON app.credit_installments
    FOR EACH ROW EXECUTE FUNCTION app.validate_credit_installments_sum();


-- 2.6 Trigger de Bienvenida para Usuarios
DROP TRIGGER IF EXISTS trg_create_default_data ON app.users;
CREATE TRIGGER trg_create_default_data
    AFTER INSERT ON app.users
    FOR EACH ROW EXECUTE FUNCTION app.create_default_user_data();



-- =============================================================
-- ARCHIVO 3: DATOS SEMILLA (BLINDADO CON TRANSACCIÃ“N ATÃ“MICA)
-- Esquema: app
-- =============================================================

BEGIN;

-- 1. Declaramos explÃ­citamente el entorno solo para esta transacciÃ³n
SET LOCAL app.environment = 'development';

-- 2. Ejecutamos el Guard de Entorno (SIN tocar tax_rates)
DO $$
DECLARE
    _env text;
BEGIN
    BEGIN
        _env := current_setting('app.environment');
    EXCEPTION WHEN OTHERS THEN
        _env := 'production';
    END;

    IF _env = 'production' THEN
        RAISE EXCEPTION 'ðŸ›‘ ALERTA CRÃTICA: Intentando ejecutar TRUNCATE en PRODUCCIÃ“N. OperaciÃ³n abortada.';
    END IF;
    
    RAISE NOTICE 'Entorno seguro detectado (%). Vaciando tablas de categorÃ­as...', _env;
    TRUNCATE TABLE app.subcategories CASCADE;
    TRUNCATE TABLE app.categories CASCADE;
    -- Se eliminÃ³ el TRUNCATE de tax_rates para proteger los datos existentes
END $$;

-- -------------------------------------------------------------
-- 3. INSERCIÃ“N DE CATEGORÃAS (Nivel 1)
-- -------------------------------------------------------------
INSERT INTO app.categories (name, domain, icon, is_system, is_essential_default, sort_order) VALUES
('Supermercado',    'grocery',       'ShoppingCart',   TRUE, TRUE,  1),
('Transporte',      'transport',     'Car',            TRUE, TRUE,  2),
('Comida Fuera',    'food_out',      'Utensils',       TRUE, FALSE, 3),
('Hogar',           'home',          'Home',           TRUE, TRUE,  4),
('Salud',           'health',        'HeartPulse',     TRUE, TRUE,  5),
('Entretenimiento', 'entertainment', 'Star',           TRUE, FALSE, 6),
('EducaciÃ³n',       'education',     'FileText',       TRUE, TRUE,  7),
('Servicios',       'utilities',     'Zap',            TRUE, TRUE,  8),
('Ingresos',        'income',        'Briefcase',      TRUE, TRUE,  9),
('Ahorros',         'savings',       'PiggyBank',      TRUE, TRUE,  10),
('Otros',           'other',         'MoreHorizontal', TRUE, FALSE, 11);

-- -------------------------------------------------------------
-- 4. INSERCIÃ“N DE SUBCATEGORÃAS (Nivel 2)
-- -------------------------------------------------------------
INSERT INTO app.subcategories (category_id, name, is_system, is_essential_default, sort_order) VALUES
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Granos y secos',       TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Carnes Rojas',         TRUE, TRUE,  2),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Carnes Blancas',       TRUE, TRUE,  3),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Pescado',              TRUE, TRUE,  4),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'LÃ¡cteos',              TRUE, TRUE,  5),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Frutas y verduras',    TRUE, TRUE,  6),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Enlatados',            TRUE, FALSE, 7),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Snacks y dulces',      TRUE, FALSE, 8),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Bebidas',              TRUE, FALSE, 9),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Limpieza hogar',       TRUE, TRUE,  10),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Higiene personal',     TRUE, TRUE,  11),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'CafÃ© y TÃ©',            TRUE, FALSE, 12),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'PanaderÃ­a',            TRUE, FALSE, 13),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Comida preparada',     TRUE, FALSE, 14),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Salsas y condimentos', TRUE, FALSE, 15),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Embutidos',            TRUE, FALSE, 16),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Mariscos',             TRUE, FALSE, 17),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Aceites',              TRUE, FALSE, 18),

((SELECT id FROM app.categories WHERE name = 'Transporte'), 'Bus',          TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Transporte'), 'Tren',         TRUE, TRUE,  2),
((SELECT id FROM app.categories WHERE name = 'Transporte'), 'Taxi',         TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Transporte'), 'Uber',         TRUE, FALSE, 4),
((SELECT id FROM app.categories WHERE name = 'Transporte'), 'Didi',         TRUE, FALSE, 5),
((SELECT id FROM app.categories WHERE name = 'Transporte'), 'Combustible',  TRUE, FALSE, 6),
((SELECT id FROM app.categories WHERE name = 'Transporte'), 'Parqueo',      TRUE, FALSE, 7),
((SELECT id FROM app.categories WHERE name = 'Transporte'), 'Vuelo',        TRUE, FALSE, 8),

((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'Restaurante',   TRUE, FALSE, 1),
((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'Comida rÃ¡pida', TRUE, FALSE, 2),
((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'CafÃ©',          TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'PanaderÃ­a',     TRUE, FALSE, 4),
((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'Sodas',         TRUE, FALSE, 5),
((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'Delivery',      TRUE, FALSE, 6),

((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Utensilios',        TRUE, FALSE, 1),
((SELECT id FROM app.categories WHERE name = 'Hogar'), 'ElectrodomÃ©sticos', TRUE, FALSE, 2),
((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Muebles',           TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Reparaciones',      TRUE, TRUE,  4),
((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Alquiler',          TRUE, TRUE,  5),
((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Hipoteca',          TRUE, TRUE,  6),

((SELECT id FROM app.categories WHERE name = 'Salud'), 'Consulta mÃ©dica', TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Salud'), 'Farmacia',        TRUE, TRUE,  2),
((SELECT id FROM app.categories WHERE name = 'Salud'), 'Laboratorios',    TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Salud'), 'Ã“ptica',          TRUE, FALSE, 4),
((SELECT id FROM app.categories WHERE name = 'Salud'), 'Seguro mÃ©dico',   TRUE, TRUE,  5),

((SELECT id FROM app.categories WHERE name = 'Entretenimiento'), 'Streaming', TRUE, FALSE, 1),
((SELECT id FROM app.categories WHERE name = 'Entretenimiento'), 'Cine',      TRUE, FALSE, 2),
((SELECT id FROM app.categories WHERE name = 'Entretenimiento'), 'Deportes',  TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Entretenimiento'), 'Viajes',    TRUE, FALSE, 4),
((SELECT id FROM app.categories WHERE name = 'Entretenimiento'), 'Juegos',    TRUE, FALSE, 5),

((SELECT id FROM app.categories WHERE name = 'EducaciÃ³n'), 'Cursos',      TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'EducaciÃ³n'), 'Universidad', TRUE, TRUE,  2),
((SELECT id FROM app.categories WHERE name = 'EducaciÃ³n'), 'Libros',      TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'EducaciÃ³n'), 'Ãštiles',      TRUE, FALSE, 4),

((SELECT id FROM app.categories WHERE name = 'Servicios'), 'Electricidad',    TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Servicios'), 'Agua',            TRUE, TRUE,  2),
((SELECT id FROM app.categories WHERE name = 'Servicios'), 'Internet',        TRUE, TRUE,  3),
((SELECT id FROM app.categories WHERE name = 'Servicios'), 'TelÃ©fono',        TRUE, TRUE,  4),
((SELECT id FROM app.categories WHERE name = 'Servicios'), 'Seguro vehÃ­culo', TRUE, FALSE, 5),

((SELECT id FROM app.categories WHERE name = 'Ingresos'), 'Salario',          TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Ingresos'), 'Freelance',        TRUE, FALSE, 2),
((SELECT id FROM app.categories WHERE name = 'Ingresos'), 'Alquiler cobrado', TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Ingresos'), 'Dividendos',       TRUE, FALSE, 4),
((SELECT id FROM app.categories WHERE name = 'Ingresos'), 'Regalo / bono',    TRUE, FALSE, 5),

((SELECT id FROM app.categories WHERE name = 'Ahorros'), 'Fondo emergencia', TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Ahorros'), 'Meta especÃ­fica',  TRUE, FALSE, 2),

((SELECT id FROM app.categories WHERE name = 'Otros'), 'Otro gasto',   TRUE, FALSE, 1),
((SELECT id FROM app.categories WHERE name = 'Otros'), 'Otro ingreso', TRUE, FALSE, 2);

COMMIT;

-- -------------------------------------------------------------
-- 5. INSERCIÃ“N DE TASAS DE IMPUESTO
-- -------------------------------------------------------------
INSERT INTO app.tax_rates (country_code, rate_name, rate_pct, valid_from) VALUES
('CR', 'IVA general',               13.00, '2019-07-01'),
('CR', 'IVA reducido (canasta)',      1.00, '2019-07-01'),
('CR', 'IVA reducido (medicamentos)', 2.00, '2020-01-01'),
('CR', 'IVA exento',                  0.00, '2019-07-01');
