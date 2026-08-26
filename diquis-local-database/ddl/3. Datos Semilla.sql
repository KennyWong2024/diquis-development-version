-- =============================================================
-- ARCHIVO 3: DATOS SEMILLA (BLINDADO CON TRANSACCIÓN ATÓMICA)
-- Esquema: app
-- =============================================================

BEGIN;

-- 1. Declaramos explícitamente el entorno solo para esta transacción
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
        RAISE EXCEPTION 'ALERTA CRÍTICA: Intentando ejecutar TRUNCATE en PRODUCCIÓN. Operación abortada.';
    END IF;
    
    RAISE NOTICE 'Entorno seguro detectado (%). Vaciando tablas de categorías...', _env;
    TRUNCATE TABLE app.subcategories CASCADE;
    TRUNCATE TABLE app.categories CASCADE;
    -- Se eliminó el TRUNCATE de tax_rates para proteger los datos existentes
END $$;

-- -------------------------------------------------------------
-- 3. INSERCIÓN DE CATEGORÍAS (Nivel 1)
-- -------------------------------------------------------------
INSERT INTO app.categories (name, domain, icon, is_system, is_essential_default, sort_order) VALUES
('Supermercado',    'grocery',       'ShoppingCart',   TRUE, TRUE,  1),
('Transporte',      'transport',     'Car',            TRUE, TRUE,  2),
('Comida Fuera',    'food_out',      'Utensils',       TRUE, FALSE, 3),
('Hogar',           'home',          'Home',           TRUE, TRUE,  4),
('Salud',           'health',        'HeartPulse',     TRUE, TRUE,  5),
('Entretenimiento', 'entertainment', 'Star',           TRUE, FALSE, 6),
('Educación',       'education',     'FileText',       TRUE, TRUE,  7),
('Servicios',       'utilities',     'Zap',            TRUE, TRUE,  8),
('Ingresos',        'income',        'Briefcase',      TRUE, TRUE,  9),
('Ahorros',         'savings',       'PiggyBank',      TRUE, TRUE,  10),
('Otros',           'other',         'MoreHorizontal', TRUE, FALSE, 11);

-- -------------------------------------------------------------
-- 4. INSERCIÓN DE SUBCATEGORÍAS (Nivel 2)
-- -------------------------------------------------------------
INSERT INTO app.subcategories (category_id, name, is_system, is_essential_default, sort_order) VALUES
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Granos y secos',       TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Carnes Rojas',         TRUE, TRUE,  2),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Carnes Blancas',       TRUE, TRUE,  3),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Pescado',              TRUE, TRUE,  4),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Lácteos',              TRUE, TRUE,  5),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Frutas y verduras',    TRUE, TRUE,  6),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Enlatados',            TRUE, FALSE, 7),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Snacks y dulces',      TRUE, FALSE, 8),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Bebidas',              TRUE, FALSE, 9),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Limpieza hogar',       TRUE, TRUE,  10),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Higiene personal',     TRUE, TRUE,  11),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Café y Té',            TRUE, FALSE, 12),
((SELECT id FROM app.categories WHERE name = 'Supermercado'), 'Panadería',            TRUE, FALSE, 13),
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
((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'Comida rápida', TRUE, FALSE, 2),
((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'Café',          TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'Panadería',     TRUE, FALSE, 4),
((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'Sodas',         TRUE, FALSE, 5),
((SELECT id FROM app.categories WHERE name = 'Comida Fuera'), 'Delivery',      TRUE, FALSE, 6),

((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Utensilios',        TRUE, FALSE, 1),
((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Electrodomésticos', TRUE, FALSE, 2),
((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Muebles',           TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Reparaciones',      TRUE, TRUE,  4),
((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Alquiler',          TRUE, TRUE,  5),
((SELECT id FROM app.categories WHERE name = 'Hogar'), 'Hipoteca',          TRUE, TRUE,  6),

((SELECT id FROM app.categories WHERE name = 'Salud'), 'Consulta médica', TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Salud'), 'Farmacia',        TRUE, TRUE,  2),
((SELECT id FROM app.categories WHERE name = 'Salud'), 'Laboratorios',    TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Salud'), 'Óptica',          TRUE, FALSE, 4),
((SELECT id FROM app.categories WHERE name = 'Salud'), 'Seguro médico',   TRUE, TRUE,  5),

((SELECT id FROM app.categories WHERE name = 'Entretenimiento'), 'Streaming', TRUE, FALSE, 1),
((SELECT id FROM app.categories WHERE name = 'Entretenimiento'), 'Cine',      TRUE, FALSE, 2),
((SELECT id FROM app.categories WHERE name = 'Entretenimiento'), 'Deportes',  TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Entretenimiento'), 'Viajes',    TRUE, FALSE, 4),
((SELECT id FROM app.categories WHERE name = 'Entretenimiento'), 'Juegos',    TRUE, FALSE, 5),

((SELECT id FROM app.categories WHERE name = 'Educación'), 'Cursos',      TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Educación'), 'Universidad', TRUE, TRUE,  2),
((SELECT id FROM app.categories WHERE name = 'Educación'), 'Libros',      TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Educación'), 'Útiles',      TRUE, FALSE, 4),

((SELECT id FROM app.categories WHERE name = 'Servicios'), 'Electricidad',    TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Servicios'), 'Agua',            TRUE, TRUE,  2),
((SELECT id FROM app.categories WHERE name = 'Servicios'), 'Internet',        TRUE, TRUE,  3),
((SELECT id FROM app.categories WHERE name = 'Servicios'), 'Teléfono',        TRUE, TRUE,  4),
((SELECT id FROM app.categories WHERE name = 'Servicios'), 'Seguro vehículo', TRUE, FALSE, 5),

((SELECT id FROM app.categories WHERE name = 'Ingresos'), 'Salario',          TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Ingresos'), 'Freelance',        TRUE, FALSE, 2),
((SELECT id FROM app.categories WHERE name = 'Ingresos'), 'Alquiler cobrado', TRUE, FALSE, 3),
((SELECT id FROM app.categories WHERE name = 'Ingresos'), 'Dividendos',       TRUE, FALSE, 4),
((SELECT id FROM app.categories WHERE name = 'Ingresos'), 'Regalo / bono',    TRUE, FALSE, 5),

((SELECT id FROM app.categories WHERE name = 'Ahorros'), 'Fondo emergencia', TRUE, TRUE,  1),
((SELECT id FROM app.categories WHERE name = 'Ahorros'), 'Meta específica',  TRUE, FALSE, 2),

((SELECT id FROM app.categories WHERE name = 'Otros'), 'Otro gasto',   TRUE, FALSE, 1),
((SELECT id FROM app.categories WHERE name = 'Otros'), 'Otro ingreso', TRUE, FALSE, 2);

COMMIT;

-- -------------------------------------------------------------
-- 5. INSERCIÓN DE TASAS DE IMPUESTO
-- -------------------------------------------------------------
INSERT INTO app.tax_rates (country_code, rate_name, rate_pct, valid_from) VALUES
('CR', 'IVA general',               13.00, '2019-07-01'),
('CR', 'IVA reducido (canasta)',      1.00, '2019-07-01'),
('CR', 'IVA reducido (medicamentos)', 2.00, '2020-01-01'),
('CR', 'IVA exento',                  0.00, '2019-07-01');