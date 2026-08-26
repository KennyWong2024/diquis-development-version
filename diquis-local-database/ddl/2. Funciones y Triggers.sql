-- =============================================================
-- ARCHIVO 2: FUNCIONES Y TRIGGERS
-- Esquema: app
-- =============================================================

-- =============================================================
-- PARTE 1: FUNCIONES (Lógica de Negocio)
-- =============================================================

-- 1.1 AUTOMATIZACIÓN DE FECHAS
CREATE OR REPLACE FUNCTION app.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- 1.2 CÁLCULO DEFENSIVO DEL MONTO EN MONEDA LOCAL
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

-- 1.3 MOTOR FINANCIERO: SALDOS EN TIEMPO REAL (LÓGICA BLINDADA POR DELTAS)
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
    -- LÓGICA UNIVERSAL: ¿Cuánto dinero REAL entra al Destino?
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
                
            -- Caso B: La cuenta destino está en la misma moneda que la transacción
            ELSIF _new_dst_curr = NEW.currency THEN
                _new_dst_impact := NEW.amount;
                
            -- Caso C: Cruce complejo (Multiplica por el rate que proveyó el usuario)
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
    -- MANEJO DE UPDATE (LÓGICA CON JOINS SEGUROS)
    -- ==========================================
    IF TG_OP = 'UPDATE' THEN
        WITH deltas AS (
            -- 1. REVERTIR transacción VIEJA
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

            -- 2. APLICAR transacción NUEVA
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

-- 1.4 NUEVO: VALIDACIÓN DIFERIDA DE SALDOS NEGATIVOS (REEMPLAZA AL CHECK)
CREATE OR REPLACE FUNCTION app.check_negative_balance()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- Validamos si la cuenta permite negativos, si no, y está en rojo, disparamos error
    IF NEW.current_balance < 0 AND NEW.allow_negative_balance = FALSE THEN
        -- Lanzamos este texto específico para que FastAPI lo atrape y envíe el banner elegante
        RAISE EXCEPTION 'chk_no_negative_balance';
    END IF;
    RETURN NEW;
END;
$$;

-- 1.5 VALIDACIÓN DE INTEGRIDAD EN CRÉDITOS
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

-- 1.6 BOTÓN DE PÁNICO: RECONCILIACIÓN MASIVA DE SALDOS
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

-- 1.7 CREADOR AUTOMÁTICO DE DATOS PARA USUARIOS NUEVOS
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

-- 2.1 Triggers de Auditoría
DROP TRIGGER IF EXISTS trg_users_updated_at ON app.users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON app.users
    FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

DROP TRIGGER IF EXISTS trg_transactions_updated_at ON app.transactions;
CREATE TRIGGER trg_transactions_updated_at
    BEFORE UPDATE ON app.transactions
    FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

-- 2.2 Trigger de Cálculo de Moneda (Se ejecuta ANTES para preparar los datos)
DROP TRIGGER IF EXISTS trg_compute_amount_in_currency ON app.transactions;
CREATE TRIGGER trg_compute_amount_in_currency
    BEFORE INSERT OR UPDATE ON app.transactions
    FOR EACH ROW EXECUTE FUNCTION app.compute_amount_in_account_currency();


-- 2.3 Trigger del Motor Financiero (Se ejecuta DESPUÉS de guardar la transacción)
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

-- 2.4 TRIGGER DE RESTRICCIÓN DIFERIDO PARA SALDOS (Se ejecuta al momento del db.commit)
DROP TRIGGER IF EXISTS trg_chk_no_negative_balance ON app.accounts;
CREATE CONSTRAINT TRIGGER trg_chk_no_negative_balance
    AFTER INSERT OR UPDATE ON app.accounts
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION app.check_negative_balance();

-- 2.5 Trigger de Validación de Créditos
DROP TRIGGER IF EXISTS trg_validate_installments ON app.credit_installments;
CREATE TRIGGER trg_validate_installments
    BEFORE INSERT OR UPDATE ON app.credit_installments
    FOR EACH ROW EXECUTE FUNCTION app.validate_credit_installments_sum();


-- 2.6 Trigger de Bienvenida para Usuarios
DROP TRIGGER IF EXISTS trg_create_default_data ON app.users;
CREATE TRIGGER trg_create_default_data
    AFTER INSERT ON app.users
    FOR EACH ROW EXECUTE FUNCTION app.create_default_user_data();