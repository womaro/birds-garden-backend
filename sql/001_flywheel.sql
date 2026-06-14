-- birds.garden — kolumny pod flywheel etykietowania
-- Uruchom raz na VPS:
--   PGPASSWORD=$DB_PASSWORD psql -h localhost -U bird -d birddb -f sql/001_flywheel.sql
-- (idempotentne — IF NOT EXISTS)

ALTER TABLE detections ADD COLUMN IF NOT EXISTS species_confidence REAL;
ALTER TABLE detections ADD COLUMN IF NOT EXISTS verified_species   TEXT;
ALTER TABLE detections ADD COLUMN IF NOT EXISTS verified_at        TIMESTAMPTZ;

-- indeks pod eksport zweryfikowanych cropów
CREATE INDEX IF NOT EXISTS idx_detections_verified
    ON detections (verified_species) WHERE verified_species IS NOT NULL;
