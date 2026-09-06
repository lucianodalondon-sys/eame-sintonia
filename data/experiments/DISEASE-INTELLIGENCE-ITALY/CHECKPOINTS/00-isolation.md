# CHECKPOINT 0 — ISOLATION (measured, not assumed)

    DISEASE_BASE_BRANCH  = claude/pilot-disease-evolution-vite-veneto
    DISEASE_BASE_HEAD    = d7631a29aeef46e1e528ce31cc38059436477dda
    OVERNIGHT_BRANCH     = claude/disease-intelligence-italy-overnight
    OVERNIGHT_HEAD_START = d7631a29aeef46e1e528ce31cc38059436477dda

Branch did not previously exist, locally or on origin. Nothing was reset, deleted or
force-updated. Created from the measured remote HEAD of the disease pilot, **not** from
canonical.

## Parallel local collection

    LOCAL_COLLECTION_BRANCH = claude/disease-local-collection-italy
    LOCAL_COLLECTION_STATE  = PENDING — branch ABSENT on origin at 2026-09-06T05:13Z

No handoff, no manifest, no files. Per the coordination rule, nothing is assumed about
what it has or has not found. Re-checked at the start of every major mission.

## Scope lock

    CURRENT_PRODUCT_SCOPE   = ITALY_ONLY
    SPAIN_OPERATIONAL_DATA  = 0
    FRANCE_OPERATIONAL_DATA = 0

Andalucía (`data/experiments/ALT-VITE-MILDIU-ANDALUCIA`) is inherited from the base branch
and is reclassified here as `EXTERNAL_SCIENTIFIC_BENCHMARK`: it is not collected further,
not shown, and never mixed into Italian product data. It stays on disk because deleting
prior evidence is forbidden and because it is the control that refuted the 12-month
hypothesis on quantitative data.

## Untouched

    CANONICAL_TOUCHED        = NO
    P0_2_TOUCHED             = NO
    LABEL_INTELLIGENCE_TOUCHED = NO
    PASSAPORTE_TOUCHED       = NO
    UNIVERSAL_TOUCHED        = NO
    OFFICIAL_PORTAL_TOUCHED  = NO
    OFFICIAL_DEPLOY          = NO
