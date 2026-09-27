# CAPACIDADES DE INTELLIGENCE E FERRAMENTAS — V1

```
MISSAO      C-INT-BIBLE-TOOLS-SOURCEPERF-01
ESPECIE     DETALHE SUBORDINADO A LEI — nao e lei
MEDIDO_EM   2026-09-14
LEI DONA    BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md secoes 34 e 35
```

> **As leis duráveis vivem na Bíblia.** Este ficheiro detalha; não decide. Onde
> divergir da Bíblia, a Bíblia vence, e a divergência é defeito deste ficheiro.
>
> **Nenhuma decisão de design, UI, visual, de menu ou de casco é tomada aqui.**
> Classificar função arquitetural é outra coisa. O portal não muda por causa
> deste documento.

---

## 0 · O QUE JÁ TINHA DONO, E NÃO SE REPETE AQUI

| pergunta | dono |
|---|---|
| que papel arquitetural tem cada card, um a um | [`AGRO-INTELLIGENCE-TOOL-ROLES-V1.md`](AGRO-INTELLIGENCE-TOOL-ROLES-V1.md) |
| que dado cada cruzamento exige, na Itália | [`DATA-DEMAND-MATRIX-ITALY.md`](DATA-DEMAND-MATRIX-ITALY.md) |
| que objeto analítico existe e como se liga | [`../../docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json`](../../docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json) |
| quem é dono de que conceito | [`../../docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json`](../../docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json) |
| estado real de cada card | `../../data/derivados/MATRIZ-CARDS-SENSORES-V1.json` |

Este ficheiro faz **uma** coisa que nenhum deles fazia: liga as nove capacidades
da secção 34 às onze superfícies que existem, e nomeia o que sobra dos dois
lados.

---

## 1 · A CONTA, MEDIDA

Re-executado a 2026-09-14 por `system-map/scripts/censo_cards_sensores.py`:

```
CARDS_TOTAL              11
ALIMENTADO_POR_REAL       1
MISTURA_REAL_E_FIXTURE    6
SEM_FONTE_DECLARADA       4
```

```
CAPACIDADES (Biblia §34)              9
CARDS NO PORTAL                      11
CAPACIDADE SEM CARD                   1
CARDS SEM CAPACIDADE ANALITICA        3
```

**Os números não batem, e é esse o achado.** Se as telas fossem a lista das
capacidades, bateriam por construção.

---

## 2 · CAPACIDADE → FERRAMENTA

| capacidade | card de hoje | papel canónico | estado do dado |
|---|---|---|---|
| `CAP-OPP` Opportunity | `meeting` · Radar delle Opportunità | **PRIMARY TOOL** | MISTURA |
| `CAP-PORT` Portfolio | `portfolio` · Portafoglio | **PRIMARY TOOL** (só o registado) | MISTURA |
| `CAP-WIN` Crop Window | `windows` · Finestre Colturali | **SUPPORTING INTELLIGENCE** | **REAL** |
| `CAP-FUT` Future | `future` · Archivio segnali | **SUPPORTING INTELLIGENCE** | SEM FONTE |
| `CAP-MKT` Market | `market` · Polso di Mercato | **EVIDENCE CONTEXT** | MISTURA |
| `CAP-COMP` Competitive | `competitors` · Concorrenza | **EVIDENCE CONTEXT** | MISTURA |
| `CAP-SCI` Scientific | `science` · Intelligence Scientifica | **EVIDENCE CONTEXT** | MISTURA |
| `CAP-FIELD` Field | `voices` · Voci dal Campo | **EVIDENCE CONTEXT** | SEM FONTE |
| `CAP-LABEL` Label | **nenhum** | **UNKNOWN** | — |

E os cards **sem** capacidade analítica atrás:

| card | papel canónico | porquê |
|---|---|---|
| `archive` · Archivio | **ARCHIVE** | é a navegação vertical até à prova (`INT-LAW-234`). Não conclui, e não deve |
| `sources` · Registro delle fonti | **ARCHIVE** | memória da coleta. Dono é a Collection |
| `field` · Rete Commerciale di Campo | **UNKNOWN** | toca dado comercial; sem contrato de acesso e proveniência, não tem papel |

### O que esta tabela diz, em três linhas

```
PRIMARY TOOL              2
SUPPORTING INTELLIGENCE   2
EVIDENCE CONTEXT          4
ARCHIVE                   2
UNKNOWN                   2   (CAP-LABEL sem card · card `field` sem contrato)
```

> **Duas ferramentas primárias em onze superfícies.** As outras nove mostram,
> contextualizam ou arquivam. Isto é a forma de um sistema de entrega — e o alvo
> declarado na Bíblia é *«uma máquina de produção analítica auditável»*, que tem
> outra forma.

---

## 3 · AS DUAS ASSIMETRIAS

### 3.1 · `CAP-LABEL` existe e não tem ferramenta

Existe **material**: `research/adama-italy-product-intelligence-deep/LABEL-USES.json`,
os três ficheiros por categoria, `LABEL-MANIFEST.json`, e a tabela `registro_uso`.

```
MATERIAL != FERRAMENTA
```

Um card que não existe não tem papel arquitetural: tem **uma decisão por tomar**.
Esta é a única capacidade da secção 34 nesse estado, e a decisão **não se toma
aqui** — toca no portal, e o portal está fora desta missão.

### 3.2 · `field` tem ferramenta e não tem capacidade

`Rete Commerciale di Campo` é a única superfície que toca dado comercial. Ligar
CRM ali sem contrato de acesso e de proveniência é precisamente o erro que a
`INT-LAW-186` (minimização e propósito) e a `INT-LAW-187` (provedor externo não
recebe dados automaticamente) proíbem.

Fica `UNKNOWN`, e `UNKNOWN` é uma resposta.

---

## 4 · O QUE CADA FERRAMENTA PODE E NÃO PODE

Repetido da `INT-LAW-280` porque é a fronteira que este ficheiro serve:

```
PODE      FILTER · NAVIGATE · COMPARE · EXPLAIN · RENDER
NAO PODE  fabricar crossing · completar UNKNOWN · inferir independencia ·
          promover signal→finding · promover finding→opportunity ·
          fabricar fact/location/time · recalcular logica escondida
```

### O defeito que já foi apanhado nesta casa

No card `market`, o censo encontrou um `else` no fim de uma escada de prova:

```
UM `else` NO FIM DE UMA ESCADA DE PROVA INVENTA A PROVA QUE FALTA.
```

É `RT-TOOL-02` (a tool preenche `UNKNOWN`) em código real, e não em hipótese. A
lista acima não é preventiva: é a descrição de defeitos que já aconteceram.

---

## 5 · DEMANDA DE DADOS POR CAPACIDADE

Resumo. A matriz completa, com números italianos medidos, tem dono em
[`DATA-DEMAND-MATRIX-ITALY.md`](DATA-DEMAND-MATRIX-ITALY.md) e **não** se duplica
aqui.

| capacidade | chaves de junção exigidas | lacuna conhecida |
|---|---|---|
| `CAP-OPP` | `CROP × ISSUE × REGION × TIME_WINDOW` | famílias aplicáveis por consultar |
| `CAP-PORT` | `PRODUCT × CROP × TARGET × REG_VERSION × GEO` | disponibilidade comercial nasce `NAO_SEI` |
| `CAP-WIN` | `CROP × REGION × PHENOLOGY × TIME_WINDOW` | fenologia observada, não de calendário |
| `CAP-LABEL` | `PRODUCT × CROP × TARGET × AI × MOA × REG_VERSION` | comparabilidade entre jurisdições |
| `CAP-MKT` | `CROP × GEO × PERIOD × UNIT` | unidade e denominador |
| `CAP-FIELD` | `SPEAKER × CROP × ISSUE × FACT_LOCATION × FACT_TIME` | independência entre falantes |
| `CAP-COMP` | `COMPANY × PRODUCT × CROP × GEO × TIME` | camada (regulatório \| comunicação) |
| `CAP-SCI` | `DOI\|TRIAL_ID × RESEARCHER × INSTITUTION × MOLECULE × CROP × ISSUE` | **`DOI`/`trial_id` não atravessam a fronteira** |
| `CAP-FUT` | `ISSUE × GEO × HORIZON_WINDOW` | facto-sobre-o-futuro misturado com sinal fraco |

A lacuna de `CAP-SCI` é a mais dura: sem `DOI`/`trial_id`, a capacidade **não
consegue** distinguir três artigos de um ensaio, e portanto não consegue contar
independência. É `COLLECTION_GAP` (`INT-LAW-150`), não defeito de análise, e
volta pela rota canónica da Collection (`INT-LAW-020`).

---

## 6 · O QUE ESTE FICHEIRO NÃO DECIDE

```
NAO decide criar, apagar ou renomear card
NAO decide layout, icone, cor, componente ou navegacao
NAO decide construir a ferramenta de CAP-LABEL
NAO decide ligar CRM ao card `field`
NAO altera o menu
```

Todas as cinco tocam no portal, e o portal está fora do que a secção 32 da
Bíblia autoriza.
