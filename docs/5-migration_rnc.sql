-- Agregar la columna rnc a la tabla business
ALTER TABLE business ADD COLUMN rnc VARCHAR(11) NOT NULL DEFAULT '';
ALTER TABLE business ADD CONSTRAINT uq_business_rnc UNIQUE (rnc);

-- Nota: Una vez actualices los registros existentes con RNCs válidos,
-- elimina el default temporal:
-- ALTER TABLE business ALTER COLUMN rnc DROP DEFAULT;
