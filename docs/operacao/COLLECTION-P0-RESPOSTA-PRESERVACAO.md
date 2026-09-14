# RESPOSTA AO `COLLECTION-P0-CHANGE-REQUEST` — o que era perda, o que era falta, e o que não é obra de código

```
MISSAO          C-COL-PRESERVE-FACTS-V1
BRANCH          claude/collection-preserve-facts-2139eb
BASE FUNCIONAL  claude/collection-to-waiting-room-v1 @ 56617781
PEDIDO          docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md
                lido em claude/intelligence-pilot-v1 @ 0c26981b — READ-ONLY,
                sem merge, sem cherry-pick
MEDIDO EM       2026-09-14
```

> **⚠️ O PEDIDO FOI MEDIDO NOUTRA ÁRVORE.** A linha de Intelligence mediu contra
> `claude/raw-observation-identity-3jbwco @ f888776d`. A linha funcional da
> Collection andou **25 commits** desde esse ponto comum. **Nada aqui foi
> aceite de memória**: cada achado foi reproduzido contra esta árvore antes de
> ser tocado, e um deles já estava metade curado.

---

## 1 · A BRANCH CERTA — e ela não era a deste worktree

O worktree nasceu apontado a `claude/collection-preserve-facts-2139eb @ c88690ca`,
de **3 de setembro**, com **317 ficheiros** e **sem `BIBLIA-CANONICA-DA-COLETA.md`**.
Não é a linha da Collection: é a linha do Sintonia Scrap.

```
linha funcional medida    claude/collection-to-waiting-room-v1   902 commits · 1917 ficheiros
linha de Intelligence     claude/intelligence-pilot-v1           915 commits
base comum das duas       f888776d
```

Os 45 commits que a branch tinha estão preservados em
`origin/claude/sintonia-eame-repo-setup-xccfob`, que aponta para o mesmo
`c88690ca`. **Nenhum trabalho se perdeu**; a branch foi reapontada.

```
BRANCH VELHA != BRANCH ERRADA, MAS TRABALHAR SOBRE ELA SERIA MEDIR OUTRA CASA.
```

---

## 2 · BASELINE — os nove achados, reproduzidos ou não

| # | achado do pedido | veredito **nesta** árvore | prova |
|---|---|---|---|
| A | facto com muitos campos perde campos ao virar `READY` | **CONFIRMED** | 25 campos entram, 12 saem, **20 perdidos** |
| B1 | `FACT_TIME` por *fallback* de `published_at` | **ALREADY_FIXED** | `_tem_quando` já devolvia `PUBLICATION_TIME` e `fact_time: NAO SEI` |
| B2 | a prova do portão temporal não chega ao livro | **CONFIRMED** | `decidir()` guardava só a evidência da ÚLTIMA pergunta |
| B3 | campo genérico `data` vira `FACT_TIME` | **CONFIRMED — e em DOIS sítios** | `_tem_quando` **e** `pronto_para_inteligencia` |
| C | `FACT_LOCATION` existe a montante e desaparece | **PARTIAL** | o contrato de saída levava-o; **a rota real nunca o punha no item** |
| D | `SOURCE_LOCATION` existe a montante e desaparece | **PARTIAL** | idem |
| E | `EVIDENCE_CLASS` some no `READY` | **CONFIRMED** | 13 de 13 contratos de fonte declaram-no; zero atravessam |
| F | `claim_id`, `crop_eppo`, `method`, `unit`… somem | **CONFIRMED** | ver A |
| G | `ITEM_ID` pode virar `"?"` | **CONFIRMED** | item sem `id` e sem `url` passava e pousava com `'?'` |
| H | a prova que admitiu fica registada? | **CONFIRMED (não ficava)** | só a evidência da régua do universo |
| I | a rota real transporta tempo/lugar/procedência? | **CONFIRMED (não transportava)** | `item_para_a_porta` punha **4** nomes; nenhum era esses |

---

## 3 · TRÊS ESPÉCIES DE BURACO, E SÓ DUAS SÃO OBRA DE CÓDIGO

### TIPO A — PERDA (a informação existe estruturada e a Collection deita-a fora)

| o quê | onde se perdia | onde está o dono |
|---|---|---|
| `claim_id` · `subject` · `predicate` · `crop_eppo` · `problem_eppo` · `method` · `unit` · `scale` · `denominator` · `doi` · `registration_id` … | `pronto_para_inteligencia` — 12 chaves fixas | `admissao.MARCAS_DE_FATO` |
| a espécie da coisa (`DOCUMENTO` vs `FATO`) | calculada e deitada fora | `admissao.estagio()` |
| `PUBLISHED_AT` · `OBSERVED_AT` | sem campo de saída | `ingresso.FRONTEIRA_TRANSPORTA` |
| a espécie probatória declarada pela fonte | sem campo de saída | `regras/italy_contracts.mjs` (13/13) |
| o **porquê** de cada `NAO SEI` de tempo e de lugar | sem campo de saída | `leis/artefato.py::conferir` **já o exigia** |
| `SOURCE_LOCATION` · `FACT_LOCATION` · `FACT_TIME` | `item_para_a_porta` — o item nascia sem eles | `ingresso.FRONTEIRA_TRANSPORTA` |

**AÇÃO TOMADA:** o contrato `READY` passou de 12 para 19 campos, a rota real
passou a transportar o que a fronteira declara, e o livro de decisões passou a
guardar a prova de **cada** portão. Detalhe em `COL-LAW-043`.

### TIPO B — FALTA DE ESTRUTURA (existe no texto e nunca virou campo)

| o quê | medido nesta árvore | ação |
|---|---|---|
| identidade do problema (EPPO) | **27 de 43** textos derivados contêm um binómio latino que casa exactamente com o dicionário EPPO **já no repositório** | `motor/normalize_agro.py::mencoes_de_problema` — casamento exacto, termo original preservado, autoridade e versão da regra em cada achado |
| `SOURCE_LOCATION` da fonte | **10 de 13** contratos declaram um lugar conferível contra o gazetteer | `regras/contratos_de_fonte.py::lugar_declarado_pela_fonte` |

**E o que NÃO se estruturou, de propósito:** nomes comuns italianos —
`peronospora`, `oidio`, `botrite`, `ticchiolatura`. **Não há autoridade
italiano→EPPO nesta árvore.** Cunhar o código por semelhança com o espanhol
seria junção por semelhança textual, que a `COL-LAW-034` proíbe. Ficam
`UNKNOWN`, com o termo original preservado e **contáveis**
(`termos_sem_autoridade`).

### TIPO C — FALTA DE FONTE (não existe no material, e não se inventa)

Ver §6. **Nenhuma linha de código foi escrita para estes.**

---

## 4 · O QUE ATRAVESSOU, COM MATERIAL REAL

`provas/a_collection_preserva_o_fato.py` — zero rede, zero coleta, zero
observação nova.

```
observacoes no livro do coletor ............ 175
com texto derivado nesta arvore ............  30
admitidos ate READY ........................   6   (3 boletins x 2 observacoes)
nao admitidos ..............................  24   ARPAV agrometeo — T3_NAO,
                                                   e recusar e a resposta certa

PRESERVADO
  SOURCE_LOCATION conhecido ................ 6/6   Napoli · Bari · Lecce
  especie declarada pela fonte ............. 6/6
  PUBLISHED_AT conhecido ................... 6/6

CONTINUA `NAO SEI`, E ESTA CERTO
  FACT_TIME ................................ 6/6
  FACT_LOCATION ............................ 6/6

IDENTIDADE DO PROBLEMA (derivado, com linhagem — NAO entra no READY)
  documentos com mencao confirmada por autoridade ....... 28
  mencoes totais ......................................... 76
  documentos com termo italiano SEM autoridade ...........  6
```

> **O ALVO NÃO ERA ENCHER CAMPOS.** `FACT_TIME` sai `NAO SEI` nos seis porque o
> livro do coletor **já tinha medido e escrito** que não sabe — *«UNKNOWN — o
> PDF nao expoe a data do fato medido, so a de geracao»*. O que mudou é que essa
> frase **chega agora ao outro lado**, em `FACT_TIME_BASIS`.

### Duas recusas que valem mais do que os campos preenchidos

```
"BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO"
   → FACT_LOCATION = Salerno        ANTES (a âncora `bollettino` governava)
   → RECUSADO: âmbito do documento  DEPOIS

"comunicati ufficiali dell'Osservatorio Fitosanitario della Regione Puglia"
   → FACT_LOCATION = Puglia         ANTES (`osservat[oaie]` casava DENTRO de
                                     `Osservatorio` — sem fronteira de palavra)
   → RECUSADO                       DEPOIS
```

`_ancoras()` não exigia fronteira de palavra e `mencoes()`, doze linhas acima,
exigia. **O nome de um órgão virava prova de que alguém observou alguma coisa
num sítio** — e o trecho guardado fazia a afirmação parecer auditada.

---

## 5 · O QUE **NÃO** FOI PROVADO

```
A SALA ESCREVE OS 19 CAMPOS? .................. NAO PROVADO
   esta maquina nao tem `psql` (backend canonico)
   nem `fcntl` (backend de ficheiro). O contrato foi CONFERIDO
   (`_conferir_unidades` aceita), a ESCRITA nao foi exercitada.

A MIGRATION 032 APLICA? ....................... NAO PROVADO
   DESIGNED != DB_TESTED != LIVE. Parou no primeiro.

CONCORRENCIA / RETRY / CRASH NA SALA? ......... NAO PROVADO
   pelo mesmo motivo.
```

**Próximo passo mínimo, e é um só:** correr `tests/test_sala_duravel.py` e a
`032` contra PostgreSQL descartável, numa máquina com `psql`.

---

## 6 · `REAL_SOURCE_GAP` — o que **não** se resolve com código

Medido pela linha de Intelligence em
`research/intelligence/COLLECTION-GAPS-FOR-INTELLIGENCE-ITALY.csv`, e **aqui
apenas classificado**. Esta missão não colheu nada disto e **não deve**.

| gap | família | é aquisição? |
|---|---|---|
| `GAP-IT-004` | registos/rótulos de **concorrente** em Itália — **zero** hoje | **SIM** — mas a fonte já tem contrato (`IT-T4-001`, GREEN); falta o **recorte** sem filtro de titular |
| `GAP-IT-005` | voz de campo com **data absoluta e lugar declarado** | **NÃO SEI** — estado medido é `NOT REACHED`, não `KILL`. As rotas nunca foram testadas |
| `GAP-IT-007` | identidade de **ensaio científico** (`trial_id`) | **NÃO SEI** — nunca foi medido se as publicações italianas a declaram |
| `GAP-IT-009` | **mercado de defensivo** em Itália | **NÃO SEI** — nunca foi procurada fonte pública. `NÃO SEI ≠ ZERO` |
| `GAP-IT-002` | fenologia/janelas da safra corrente | **PARCIALMENTE** — 5 contratos T3 já a trazem **em texto**; é reprocessamento primeiro |
| `GAP-IT-003` | linha de uso dos rótulos já guardados | **NÃO** — 163/163 rótulos já estão guardados com URL. É reprocessamento |
| `GAP-IT-006` | assunto da comunicação do concorrente | **PARCIALMENTE** — o criativo já está guardado; 2 de 4 majors com rota `403` |
| `GAP-IT-010` | **quatro registos de fonte a conviver** | **NÃO** — é arbitragem de identidade, não aquisição |

> **A autoridade italiano→EPPO é o gap de fonte mais barato e mais caro de
> ignorar.** `EU-T3-001` (EPPO Global Database) já está registada e está
> `NÃO SEI`. Com ela, os nomes comuns italianos que hoje ficam `UNKNOWN`
> passam a ter identidade — **sem uma única coleta nova de documento**.

---

## 7 · O QUE ESTA MISSÃO **NÃO** FEZ

- **Não extraiu claim de texto.** `COL-LAW-202` diz que extracção de claim é
  `TARGET` e **não existe** nesta casa. `FATO` **transporta** o que o produtor
  declarou; não adivinha.
- **Não criou enum de `EVIDENCE_CLASS`.** O valor é texto livre e é **da
  fonte**. Se deve virar lista fechada continua em aberto, de propósito
  (`STRUCTURED-POR-ESPECIE-E-NOT-APPLICABLE.md` §14.4).
- **Não afrouxou a porta.** As duas mudanças de régua **apertam**: `identidade`
  passou a ser perguntada, e `data` deixou de promover a `FACT_TIME`.
- **Não colheu nada.** Nenhuma fonte nova, nenhum coletor disparado, nenhuma
  observação criada.
