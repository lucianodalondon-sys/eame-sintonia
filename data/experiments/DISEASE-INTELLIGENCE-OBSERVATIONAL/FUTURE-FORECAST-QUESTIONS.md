# FUTURE-FORECAST-QUESTIONS

Forecast is **out of scope** for this mission and nothing in this build attempts it. This file
exists only so the question is written down instead of drifting back in as an implication.

Nothing here is a plan and nothing here is a promise. It is the list of things that would have
to be true before anyone should try, written now while the observational work is fresh.

---

## What this build actually is

A **nowcast of what scouts recorded**, per province, per 28-day window, with a real
denominator. Its verbs are all past tense by construction: `observed_trend` describes windows
that have already ended, and the renderer's closing block says so in every card.

The distance between that and a forecast is not a modelling step. It is a different evidential
claim.

---

## 1. What would have to exist before a forecast could be attempted

**An outcome series that is not the instrument reading itself later.**
Today the only thing available to validate against is the same drupe-sampling column at a
later date. Scoring a prediction of the sampling against the sampling proves the sampling is
autocorrelated, not that anything was predicted. A real outcome would be damage at harvest,
yield loss, oil quality downgrade, or a treatment decision that a grower actually took.
None of those is in this repository or on this API.

**A panel that survives its own baseline.**
Measured here: 7 of 10 provinces cannot support a matched historical comparison at all,
because the groves monitored today are not the ones monitored in their own past. A model
trained on a rotating panel learns the panel.

**A weather or degree-day predictor that belongs to the same place.**
The previous generation of this work established that a predictor from region A may not serve
an outcome in region B unless co-movement has been measured. Nothing of the kind exists for
this case.

---

## 2. Questions that must be answered BEFORE, not after

1. **What exactly would be forecast?** The share of sampled drupes with live infestation, at a
   province, at a horizon of k days. Written as a sentence with the unit and the denominator
   in it, before any code.
2. **Against which baseline?** Persistence is mandatory. A grower already knows what their
   grove looked like last week; a forecast that cannot beat "nothing changes" is not a
   product. Climatology and last-year's-same-window are the other two.
3. **What is the horizon, and is it agronomically useful?** Olive fly is controllable while the
   infestation is at egg or first/second instar. A forecast that lands after the third instar
   is a description of a decision already lost.
4. **How would leakage be prevented at all three levels** — day, threshold and feature
   selection? The previous work in this repository failed on the third while passing the first.
5. **What is the detectability floor?** With 20 seasons and 10 provinces, how large an effect
   could a study of this size detect at all? Answer that with a power analysis before running
   any model, not after seeing one.
6. **Who owns the false alarm?** A forecast that fires wrongly costs a spray. That cost must
   have a named owner before the first alarm, not after.

---

## 3. What must NOT be reused from this build

- `observed_trend` is **not** a weak forecast. It is arithmetic over three windows that have
  already ended, and relabelling it would be the exact error this whole mission exists to
  avoid.
- The matched-panel comparison answers "how does this window rank against its own past". It
  says nothing about the next window.
- `ADAMA_RELEVANCE` is a portfolio fact. It may never become a trigger, forecast or not.

---

## 4. The honest position today

```
FORECAST_ATTEMPTED   = NO
FORECAST_POSSIBLE    = NOT KNOWN
WHAT_WOULD_SETTLE_IT = an outcome series independent of the instrument, and a panel stable
                       enough that a baseline means something. Neither exists here today.
```

If a forecast layer is ever built, it is a **new capability with its own certification**, and
the fact that the observational layer passed its own gates says nothing whatsoever about it.
