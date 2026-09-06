# CHECKPOINT 7 — ADAMA PORTFOLIO CROSS (a different gap closed, not the one asked for)

The branch pointed to — `claude/eame-competitor-public-communication` @ `87077f6` — is **not
the local disease collection.** It carries no bagnatura, no leaf wetness, no station data, no
meteo series, no phytosanitary observations. Those searches are still negative.

What it does carry is `research/adama-italy-product-intelligence-deep`, the **verified ADAMA
Italy portfolio** — the exact input I recorded as missing when I wrote
`ADAMA_PRODUCT_RELATION = UNKNOWN`.

## The package, checked rather than trusted

| | |
|---|---|
| registry source | `PROD_FTS_6_20260831.csv`, Ministero, snapshot **2026-08-31** |
| registry rows | 17,695 |
| ADAMA group records | 602 |
| admin-active and unexpired | 155 |
| **active ingredients** | **122** |
| synthetic records | **0** |
| QA | 49 sampled · 46 pass · 2 corrected · **0 rejected** |

That package caught its own defect and recorded it: mixtures separate on `|`, not `+`, so the
previous run had produced **169 false active substances instead of 122 real ones**. A package
that publishes its own error is worth more than one that reports none.

## The cross

Tuscan observations name **28 distinct active substances** across **21,694 applications**
against vine peronospora, 2006–2026.

**My first attempt was wrong and I caught it before reporting.** A naive substring match
returned 2 of 28, because the `IT-AI-` registry prefix broke containment and Italian/English
orthography differs (`Dimetomorf`/`DIMETHOMORPH`, `Cimoxanil`/`CYMOXANIL`,
`Amisulbron`/`AMISULBROM`, `Benthiovalicarb`/`BENTHIAVALICARB`). After stripping the prefix,
normalising `ph→f`, `th→t`, `y→i`, and splitting mixtures, the real overlap is:

| observed active | applications | ADAMA-registered |
|---|---|---|
| Prodotti rameici (copper) | 15,548 | no |
| **Dimetomorf (CAA)** | 1,633 | ✔ `DIMETHOMORPH` |
| **Cimoxanil** | 1,070 | ✔ `CYMOXANIL` |
| Fosetil-Al | 816 | no |
| Iprovalicarb | 435 | no |
| Fluopicolide | 315 | no |
| **Metalaxyl-M** (+ variant spelling) | 483 | ✔ `METALAXYL-M` |
| zoxamide | 279 | no |
| **Folpet** | 206 | ✔ `FOLPET` |
| **Amisulbron** | 14 | ✔ `AMISULBROM` |
| **Benthiovalicarb** | 12 | ✔ `BENTHIAVALICARB` |
| **Valifenalate + Mancozeb** | 2 | ✔ `MANCOZEB` |

```
ADAMA_ACTIVE_SUBSTANCE_OVERLAP = 8 of 28 observed actives
applications using an ADAMA-registered active = 3,420 / 21,694 = 15.8 %
excluding copper                              = 3,420 /  6,146 = 55.6 %
```

**Copper alone is 71.7 % of every application**, and its share is rising (70.6 % → 80.5 %,
ρ = +0.780). So the non-copper segment — where ADAMA's actives cover more than half of
observed use — is the shrinking half of the market.

## What this proves, and three reasons it is not more

**`ADAMA_PRODUCT_RELATION = PLAUSIBLE_NOT_PROVED`** — upgraded from `UNKNOWN`, and
deliberately not to `PROVED`.

1. **This is substance overlap, not product usage.** Dimethomorph is sold by many companies.
   An application recorded as `Dimetomorf` is **not** evidence an ADAMA product was used. The
   Tuscan field records the active substance, never a brand.
2. **Crop and target remain unverified.** `FUNGICIDE-LABEL-USES.json` is empty with
   `STATE: REAL_GAP` — *"nenhuma etichetta foi lida. 7 rotas de recuperação tentadas, 0
   documentos recuperados."* So I cannot confirm that any of these eight registrations covers
   **vite × peronospora** specifically. An active registered in Italy may be registered for a
   different crop entirely.
3. **The registry is a 2026 snapshot matched against 2006–2026 applications.** Registrations
   are granted and withdrawn over time, so matching a 2026-08-31 registry against a 2008
   application is anachronistic in an unquantified direction.

```
ADAMA_PRODUCT_RELATION = PLAUSIBLE_NOT_PROVED
CROP_MATCH             = NOT_PROVED   (blocked by the label-uses REAL_GAP)
TARGET_MATCH           = NOT_PROVED   (same block)
TIMING_MATCH           = NOT_ASSESSED
```

**What would unblock it**, quoted from the package itself: reading the labels, which needs a
machine with a graphical window and the local archive — the same local route that has not
yet delivered the disease collection either.
