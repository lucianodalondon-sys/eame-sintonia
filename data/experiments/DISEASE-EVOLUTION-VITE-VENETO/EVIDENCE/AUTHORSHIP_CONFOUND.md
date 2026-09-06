# The confound that decides the Veneto question — verified mechanically

A scale designer claimed the severity vocabulary is era-bound. I checked it rather than
repeating it, and the check both **corrected the specific claim** and made the **underlying
finding sharper**.

## Word counts per document, all 26

| word | designer said | actually first appears |
|---|---|---|
| `severità` | 2021 | **2021** ✔ |
| `gravità` | 2016 | **2016** ✔ |
| `intensità` | "only 2024-25" | **2000-01** ✘ — the claim was overstated |
| `virulenza` | (implied recent) | **2001-02** ✘ |

`pressione` appears in several old reports, but **every occurrence is barometric**
(*"alta pressione"*, *"depressione al suolo"*), not disease pressure. Checked directly.

So two of the four vocabulary claims were wrong. The designer overstated its case.

## But the real confound is cleaner than the one it described

The reports carry a co-authorship line — *"In collaborazione con: Regione del Veneto,
Settore Servizi Fitosanitari / U.O. Fitosanitario"*. Its presence is a **perfect era split**:

| block | documents | co-authored by the plant-health service |
|---|---|---|
| 2000-01 … 2014 | 15 | **0** |
| 2015 … 2025 | 11 | **11** |

Not a tendency. Every document before 2015, none. Every document from 2015, all.

And that split is exactly where the outcome becomes assignable. The frozen mechanical
lexicon scan finds a severity marker in **3 of 14** documents from 2000–2013 and **9 of 12**
from 2014–2025.

## Why this is close to fatal for a 25-season Veneto backtest

**The probability that a season carries a usable outcome is a function of who wrote the
report, not of what the disease did.** When a plant-health service co-signs, disease gets
graded; when a meteorological office writes alone, it gets mentioned in passing or not at
all.

That makes the missing seasons **not missing at random**, in the direction that matters
most: the gap correlates with time. A model trained on early seasons to predict late ones
would be comparing two reporting regimes, not two epidemics — and it would produce a
confident, entirely spurious "peronospora pressure has declined" trend, because report
length roughly doubled and the grading vocabulary arrived at the same moment.

## The corpus also falsifies the rescue rule, at the one point where it can be tested

The generous scale wanted to promote a season on region-wide scope language. There is
**exactly one season** where a scope phrase co-occurs with an explicit severity word:

> **2021** — *"infezioni di Peronospora in tutti gli ambienti vitati, generalmente di
> **bassa severità**"*

The single internal calibration point available says region-wide occurrence is compatible
with the **lowest** band. Scope is not severity, and the corpus says so itself. Every
season promoted on scope alone is inference **against** the only evidence the source
offers on that inference.

## The confound nobody can remove by reading harder

Every severity sentence in this corpus records disease **after control**. Fungicide
chemistry, spray scheduling, decision-support adoption and the organic share of Veneto's
vineyards all changed substantially between 2001 and 2025. 2022's *"pressoché assente"* is
explicitly qualified *"nei vigneti regolarmente difesi"*; 2024 and 2025 report organic
vineyards separately and worse.

So the low end of the scale in recent years may be measuring **modern fungicide programmes**
and the high end may be measuring **2002's**. No re-reading of the text separates them, and
no amount of additional ARPAV collection would either.
