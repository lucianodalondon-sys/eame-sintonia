# MATRIZ DE COMPOSIÇÃO — MEDIÇÃO D0.4

```
DOCUMENT_TYPE   MEASUREMENT · genealogia e propriedade
DATE            2026-09-08
BASELINE        a4fb6d81681094925ccfd1638bc7386cbec6f4d4
OWNER_HEAD      fb96f49d   ← SOURCE_HEAD declarado pelo próprio snapshot
DADOS           MATRIZ-DE-COMPOSICAO-V1.json
CONTRATO        ../CONTRATO-DE-COMPOSICAO-V1.md
RUNTIME 0 · PORTAL 0 · MERGE 0
```

## §1 · O ACHADO QUE PRECEDE TUDO

O snapshot declara `SOURCE_HEAD = fb96f49d`. **O baseline não é o gerador.**

```
scripts/v21_oportunidades.py
    a4fb6d8  (ramo do portal)   1.216 linhas   estado_de_acao: NÃO   VALIDATE_NOW: NÃO
    fb96f49d (gerador real)     2.475 linhas   estado_de_acao: SIM   VALIDATE_NOW: SIM
```

**Metade do ficheiro.** D0.3 leu o vizinho e chamou-lhe autor. Correção em
`CONTRATO §1`, com a lei que ela compra:

> **`L-29` · `SCRIPT PRESENT IN THE BASELINE ≠ SCRIPT THAT PRODUCED THE DATA`**

**Verificação:** transcrita a lei de `fb96f49d` e reexecutada sobre os 43 do snapshot,
reproduz **34 de 34** dos casos não sobrescritos, e recupera o estado apagado nos 9
restantes. Ver `RED-TEAM-COMPOSICAO-V1.md §1`.

## §2 · GENEALOGIA — os comandos e o que devolveram

```
git log --all -S'VALIDATE_NOW'             42 commits · mais antigo caa69379 · 2026-09-03
git log --all -S'PUBLICATION_STATE'        39 commits
git log --all -S'EXTERNAL_MATERIAL_READY'  26 commits
git log --all -S'SALES_READY'              40 commits
```

`VALIDATE_NOW` nasce em **`caa69379`, 2026-09-03** —
*«o cartao para de dizer ACT NOW quando nao ha janela, e passa a dizer o que falta»*.
E vive hoje, em `scripts/`, em **duas linhagens**:
`claude/opportunity-commercial-priority-v1` e `claude/trilha-universal-inteligencia-a5rx9d`.
**Nenhuma delas é o baseline.**

## §3 · AS SETE DIMENSÕES, COM DONO PROVADO

| # | dimensão | pergunta | dono | derivado de |
|---|---|---|---|---|
| 1 | `ELIGIBILITY_CLASS` | ligação factual defensável com produto ADAMA? | `adama_relevance.py` | — |
| 2 | `ELIGIBILITY_SURFACE` | em que superfície se apresenta? | `adama_relevance.py` | **`ELIGIBILITY_CLASS`** (declarado, lossy) |
| 3 | `TEMPORAL_STATE` | o que sabemos do momento real? | `v21_oportunidades.py::estado_de_acao` | — |
| 4 | `VALIDATION_GATE_STATE` | que portão falhou? | `v21_oportunidades.py::portoes` + `red_team` | — |
| 5 | `COMMERCIAL_PRIORITY` | isto vende, e porquê? | `v21_comercial.py::prioridade` | — |
| 6 | `EXTERNAL_MATERIAL_READY` | pode sair para terceiro? | `v21_comercial.py::externo` | `COMMERCIAL_PRIORITY` (parcial) |
| 7 | `PUBLICATION_STATE` | pode atravessar para o publicável? | **`v21_catraca.py`** | **`EXTERNAL_MATERIAL_READY`** (declarado) |

```
DONOS PROVADOS ........ 7 / 7      (eram 5 / 7 em D0.3)
U-25 PUBLICATION_STATE  RESOLVIDO  → scripts/v21_catraca.py
U-26 VALIDATE_NOW ..... RESOLVIDO  → estado TEMPORAL, dono estado_de_acao()
```

## §4 · A CADEIA QUE EXPLICA A IGUALDADE DE CONJUNTOS

```
COMMERCIAL_PRIORITY ──▶ EXTERNAL_MATERIAL_READY ──▶ PUBLICATION_STATE
   (vende?)                 (pode sair?)               (pode atravessar?)
                        só REBAIXA               só REBAIXA · «A CATRACA SÓ
                                                  SEGURA. NUNCA EMPURRA.»
```

Nos 43, **nenhum dos dois passos rebaixou nada** — por isso os três conjuntos coincidem.
`EXTERNAL_BLOCKER_CODES` confirma: **um só dos oito códigos disparou**
(`NOT_SALES_READY`, 37 vezes).

**Não é coincidência. É derivação declarada com dois passos que não fizeram nada.**

## §5 · A PROJEÇÃO LOSSY

```python
SUPERFICIE = {'A':'OPPORTUNITA','B':'RADAR','C':'SEGNALI','D':'ERRORE','E':'ERRORE'}
```

Um dono, uma projeção declarada — **e não injetiva**: `D` e `E` colapsam em `ERRORE`.
De `ERRORE` não se recupera a classe. `L-30` no contrato.

## §6 · O QUE ESTA MEDIÇÃO NÃO FEZ

Não corrigiu a cópia obsoleta. Não renomeou campos. Não separou `STATUS`. Não tocou
engine, portal, collection nem snapshot. Cinco itens em `RUNTIME_RECONCILIATION_REQUIRED`.
