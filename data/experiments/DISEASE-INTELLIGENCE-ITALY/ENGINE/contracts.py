#!/usr/bin/env python3
"""
SINTONIA — UNIVERSAL DISEASE & PEST INTELLIGENCE ENGINE · CONTRACTS

The object is REGION x CROP x ISSUE. Nothing here names Toscana or Peronospora: those were
the calibration case, not the tool.

Every contract below exists because a specific error was made and caught in this project.
The comment on each one names the error, so a future reader knows the rule is paid for.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import datetime as dt

# ─────────────────────────────────────────────────────────── OBSERVED_VS_MODELLED
class EvidenceRole:
    """
    PAID FOR BY: the ARPAV 'Bollettino Peronospora vite' was read as an observation for a
    whole session. Its own cover says 'modello Vitimeteo (versione sperimentale)'. Scoring a
    model against a model proves nothing.
    Also: a 2017 ARPAV sentence read 'un rischio basso di infezione' and was coded as severity.
    """
    OFFICIAL_OBSERVATION = "OFFICIAL_OBSERVATION"   # a person recorded what they saw
    FIELD_REPORTED       = "FIELD_REPORTED"
    MODELLED_RISK        = "MODELLED_RISK"          # NEVER admissible as ground truth
    FORECAST             = "FORECAST"               # NEVER admissible as ground truth
    SCENARIO             = "SCENARIO"
    CONTEXT              = "CONTEXT"                # narrative; not a measurement
    NOT_KNOWN            = "NOT_KNOWN"

    GROUND_TRUTH_ADMISSIBLE = {OFFICIAL_OBSERVATION, FIELD_REPORTED}

    @classmethod
    def assert_admissible_as_outcome(cls, role: str):
        if role not in cls.GROUND_TRUTH_ADMISSIBLE:
            raise ValueError(
                f"REFUSED: evidence_role={role} cannot be an OUTCOME. "
                "RISK_FORECAST != DISEASE_PRESENCE; a model output is not an observation.")


# ─────────────────────────────────────────────────────────── MISSINGNESS
class Missing:
    """
    PAID FOR BY: an Abruzzo season returned 17 rows against 396-935 in every other season.
    2023 was a documented peronospora disaster; coding it 'low' would have inverted the worst
    season in the series. And 182 failed captures were labelled PRESERVED in a sibling mission.
    """
    NOT_KNOWN            = "NOT_KNOWN"
    COLLECTION_FAILED    = "COLLECTION_FAILED"
    NOT_PRESERVED        = "NOT_PRESERVED"
    DISCOVERED_NOT_COLLECTED = "DISCOVERED_NOT_COLLECTED"
    SOURCE_ABSENT        = "SOURCE_ABSENT"          # the source itself never had it
    YEAR_IN_PROGRESS     = "YEAR_IN_PROGRESS"
    INSUFFICIENT_DATA    = "INSUFFICIENT_DATA"

    NEVER_ZERO = {NOT_KNOWN, COLLECTION_FAILED, NOT_PRESERVED,
                  DISCOVERED_NOT_COLLECTED, YEAR_IN_PROGRESS, INSUFFICIENT_DATA}

    @classmethod
    def assert_not_coerced_to_zero(cls, state: str, value):
        if state in cls.NEVER_ZERO and value in (0, 0.0, "0"):
            raise ValueError(f"REFUSED: {state} coerced to zero. FAILURE != ZERO.")


# ─────────────────────────────────────────────────────────── GEOGRAPHY + REGIONALITY
@dataclass
class Geography:
    """
    PAID FOR BY: Toscana and Abruzzo, same country, same crop, same pathogen, do NOT co-move
    (Spearman +0.190, p=0.67). A single national figure would average two independent things.
    And Treviso leaf wetness cannot improve a Toscana outcome however good it is.
    """
    level: str            # POINT | MUNICIPALITY | PROVINCE | REGION | COUNTRY
    region: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    admin_code: Optional[str] = None

    POINT, MUNICIPALITY, PROVINCE, REGION, COUNTRY = "POINT","MUNICIPALITY","PROVINCE","REGION","COUNTRY"

    def coordinates_proved(self) -> bool:
        return (self.lat is not None and self.lon is not None
                and abs(self.lat) > 0.001 and abs(self.lon) > 0.001)


def assert_join_regionally_valid(predictor_region: str, outcome_region: str,
                                 co_movement_rho: Optional[float] = None) -> str:
    """
    Returns the JOIN state. A predictor from region A may only serve an outcome in region A,
    unless co-movement between the two regions has been MEASURED and is strong.
    PAID FOR BY: the temptation to use an excellent Veneto predictor on a Toscana outcome.
    """
    if predictor_region.strip().lower() == outcome_region.strip().lower():
        return "JOIN_VALID_SAME_REGION"
    if co_movement_rho is None:
        return "NOT_APPLICABLE_DIFFERENT_REGION_NO_COMOVEMENT_MEASURED"
    if co_movement_rho < 0.5:
        return f"NOT_APPLICABLE_REGIONS_DO_NOT_CO_MOVE(rho={co_movement_rho})"
    return f"JOIN_ARGUABLE_MEASURED_COMOVEMENT(rho={co_movement_rho})"


# ─────────────────────────────────────────────────────────── TIME + LEAKAGE
@dataclass
class Cutoff:
    """
    PAID FOR BY: the fatal defect. The engine chose its feature by argmax over ALL scored
    years, then reported it as out-of-sample. Day-level leakage was zero and the result was
    still invalid, because leakage at the SELECTION level is still leakage.
    """
    name: str
    issue_date: dt.date
    target_window_start: dt.date
    target_window_end: dt.date

    def assert_no_day_leakage(self, latest_contributing_day: Optional[dt.date]):
        if latest_contributing_day and latest_contributing_day > self.issue_date:
            raise ValueError(f"REFUSED: {self.name} used {latest_contributing_day} "
                             f"after its cutoff {self.issue_date}")

    def is_forecast(self) -> bool:
        return self.issue_date < self.target_window_start

    def label(self) -> str:
        """A cutoff inside the target window is a NOWCAST, never a forecast."""
        return "FORECAST" if self.is_forecast() else "NOWCAST"


class LeakageGuard:
    """Three levels. The engine originally checked only the first and reported success."""
    DAY_LEVEL       = "no predictor day after the cutoff"
    THRESHOLD_LEVEL = "class boundaries fitted on training years only, refitted per test year"
    SELECTION_LEVEL = "feature AND direction chosen inside the training fold only"

    @staticmethod
    def assert_all_three(day_ok: bool, threshold_ok: bool, selection_ok: bool):
        missing = [n for n, ok in (("DAY", day_ok), ("THRESHOLD", threshold_ok),
                                   ("SELECTION", selection_ok)) if not ok]
        if missing:
            raise ValueError(f"REFUSED: leakage guard incomplete at {missing}. "
                             "Day-level cleanliness alone is not out-of-sample.")


# ─────────────────────────────────────────────────────────── BASELINES
class BaselineContract:
    """
    PAID FOR BY: 'beats_baseline' was once a bare '>' with no test. Exact McNemar against the
    best baseline gave p=0.289 on a result that had been published as PROVED.
    And for any k-ahead question, PERSISTENCE is mandatory: a grower already knows what their
    field looked like last week. A nowcast that cannot beat 'nothing changes' is not a product.
    """
    CLIMATOLOGY   = "predict the modal/mean class of the training periods"
    PERSISTENCE   = "predict the previous period"          # MANDATORY for any k-ahead claim
    PREVIOUS_YEAR = "predict the same period last year"
    STATE_TO_DATE = "predict from the current period's own observation"

    MANDATORY_FOR_AHEAD_CLAIMS = {PERSISTENCE}

    @staticmethod
    def assert_beaten(model_acc: float, best_baseline_acc: float,
                      paired_test_p: Optional[float], perm_p: Optional[float],
                      family_size: int) -> str:
        if model_acc <= best_baseline_acc:
            return "REFUTED"
        if perm_p is None or paired_test_p is None:
            return "NOT_PROVED"
        bonf = 0.05 / max(1, family_size)
        if perm_p <= bonf and paired_test_p <= 0.05:
            return "PROVED"
        return "NOT_PROVED"


# ─────────────────────────────────────────────────────────── CAPABILITY ROUTING
class Capability:
    """
    PAID FOR BY: not every case supports every capability, and pretending otherwise is how a
    historical record gets sold as a forecast. A case may be historical-only and still useful.
    """
    HISTORICAL_INTELLIGENCE  = "HISTORICAL_INTELLIGENCE"
    EVOLUTION_MONITOR        = "EVOLUTION_MONITOR"
    CURRENT_PRESSURE_MONITOR = "CURRENT_PRESSURE_MONITOR"
    EARLY_WARNING            = "EARLY_WARNING"
    PRE_SEASON_OUTLOOK       = "PRE_SEASON_OUTLOOK"
    NEXT_SEASON_OUTLOOK      = "NEXT_SEASON_OUTLOOK"

    PROVED, NOT_PROVED, NOT_TESTABLE, INSUFFICIENT_DATA = \
        "PROVED","NOT_PROVED","NOT_TESTABLE","INSUFFICIENT_DATA"

    @staticmethod
    def route(outcome_exists: bool, outcome_numeric: bool, n_comparable_periods: int,
              predictor_region_matches: bool, skill_state: Optional[str],
              latency_days: Optional[int] = None, label_stability: Optional[float] = None,
              publishable_units: Optional[int] = None) -> Dict[str, str]:
        """NOT_TESTABLE means the test could not be run. It is NOT a negative result."""
        C = Capability
        if not outcome_exists:
            return {c: C.NOT_TESTABLE for c in
                    (C.HISTORICAL_INTELLIGENCE, C.EVOLUTION_MONITOR, C.CURRENT_PRESSURE_MONITOR,
                     C.EARLY_WARNING, C.PRE_SEASON_OUTLOOK, C.NEXT_SEASON_OUTLOOK)}
        out = {C.HISTORICAL_INTELLIGENCE: C.PROVED}
        out[C.EVOLUTION_MONITOR] = C.PROVED if n_comparable_periods >= 5 else C.INSUFFICIENT_DATA
        # TIGHTENED 2026-09-06. This line used to read "PROVED if outcome_exists" — an archive
        # from 2009 with nothing since would have been stamped a CURRENT pressure monitor, and
        # the matrix stamped PROVED on five cells where the definition executes on one. A
        # current-state claim needs three things the archive alone cannot supply: data recent
        # enough to be current, a label that survives its own parameters, and at least one
        # regional unit that passes the publication gate.
        if not outcome_exists:
            out[C.CURRENT_PRESSURE_MONITOR] = C.NOT_TESTABLE
        elif latency_days is None or label_stability is None or publishable_units is None:
            out[C.CURRENT_PRESSURE_MONITOR] = C.NOT_TESTABLE      # never measured = never proved
        elif latency_days > 21 or label_stability < 0.80 or publishable_units < 1:
            out[C.CURRENT_PRESSURE_MONITOR] = C.NOT_PROVED
        else:
            out[C.CURRENT_PRESSURE_MONITOR] = C.PROVED
        for c in (C.EARLY_WARNING, C.PRE_SEASON_OUTLOOK, C.NEXT_SEASON_OUTLOOK):
            if not predictor_region_matches:
                out[c] = C.NOT_TESTABLE
            elif n_comparable_periods < 10:
                out[c] = C.INSUFFICIENT_DATA
            else:
                out[c] = skill_state or C.NOT_PROVED
        return out


# ─────────────────────────────────────────────────────────── EVIDENCE + PORTFOLIO
@dataclass
class EvidenceChain:
    """SOURCE -> RAW -> CLAIM -> INTELLIGENCE -> VIEW. A cell without its evidence is not published."""
    source_url: Optional[str] = None
    source_hash: Optional[str] = None
    raw_path: Optional[str] = None
    extraction_method: Optional[str] = None
    verbatim_quote: Optional[str] = None
    locator: Optional[str] = None          # page / table / row
    provenance_class: str = EvidenceRole.NOT_KNOWN

    def publishable(self) -> bool:
        return bool((self.verbatim_quote or self.raw_path) and self.source_url)


class PortfolioRelation:
    """
    PAID FOR BY: an active-substance name matching a registry entry is NOT proof a product was
    used, nor that it is registered for that crop and that target.
    """
    PROVED = "PROVED"; PLAUSIBLE_NOT_PROVED = "PLAUSIBLE_NOT_PROVED"
    NO_MATCH = "NO_MATCH"; UNKNOWN = "UNKNOWN"

    @staticmethod
    def evaluate(substance_proved: bool, registered_in_country: bool,
                 crop_proved_on_label: bool, target_proved_on_label: bool,
                 official_evidence_recoverable: bool) -> str:
        if all((substance_proved, registered_in_country, crop_proved_on_label,
                target_proved_on_label, official_evidence_recoverable)):
            return PortfolioRelation.PROVED
        if substance_proved and registered_in_country:
            return PortfolioRelation.PLAUSIBLE_NOT_PROVED   # a lexical match is never proof
        return PortfolioRelation.UNKNOWN


# ─────────────────────────────────────────────────────────── the two record schemas
@dataclass
class OutcomeRecord:
    region: str; crop: str; issue: str
    observed_at: dt.date
    value_raw: Any
    unit: str
    outcome_type: str                    # INCIDENCE|SEVERITY|PRESENCE|COUNT|PERCENTAGE|INDEX|OTHER|UNKNOWN
    evidence_role: str
    geography: Geography
    denominator: Optional[Any] = None    # a rate without a denominator is not a rate
    defence_regime: str = "UNKNOWN"
    missing_state: Optional[str] = None
    evidence: EvidenceChain = field(default_factory=EvidenceChain)

    def validate(self):
        EvidenceRole.assert_admissible_as_outcome(self.evidence_role)
        if self.missing_state:
            Missing.assert_not_coerced_to_zero(self.missing_state, self.value_raw)
        if self.outcome_type in ("PERCENTAGE", "INCIDENCE") and self.denominator is None:
            raise ValueError("REFUSED: a rate without a stated denominator is not a rate.")


@dataclass
class PredictorRecord:
    region: str
    observed_at: dt.date
    variable: str
    value_raw: Any
    unit: str
    evidence_role: str                   # OFFICIAL_OBSERVATION for a sensor; MODELLED_RISK for a model
    geography: Geography
    station_id: Optional[str] = None
    joint_coverage_pct: Optional[float] = None   # per-variable coverage is NOT usable coverage
    aggregation: Optional[str] = None            # MIN/MAX/MEAN — never invent a MEAN that the source lacks

    def validate(self):
        if self.aggregation == "MEAN" and self.unit.endswith("(min/max only)"):
            raise ValueError("REFUSED: fabricated MEAN from a source that publishes only min and max.")
