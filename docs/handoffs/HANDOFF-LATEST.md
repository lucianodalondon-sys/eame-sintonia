# HANDOFF — ÚLTIMO ESTADO · 2026-09-08

> O ficheiro grande é
> [`HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md`](HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md).
> **Este é só o ponteiro para onde o trabalho parou.**

```
WORK_BRANCH   claude/collection-foundation-integration-v1
WORK_HEAD     ef9803bb          (medir outra vez: git fetch)
WORKTREE      limpa
M2_STATE      CLOSED
```

⚠️ **Duas sessões trabalham nesta branch ao mesmo tempo.** Já colidimos cinco
vezes — duas delas nesta missão, e as duas correram bem porque a regra foi
cumprida. `git fetch` **antes de começar** e **antes de cada commit**. Nunca
`--force`. Se o remoto andou: **parar de escrever, ler os commits novos, e
integrar por medição** — não por antiguidade, e não por quem chegou primeiro.

## Checkpoints empurrados

| commit | o que fechou |
|---|---|
| `51a26550` … `0552424a` | **M1A · O1–O8** · a trava, o contrato, o fluxo no seco |
| `105602f6` | **O8B** · o mapa deixa de dizer que não existe o que existe |
| `124c6999` · `44e2de1b` | **O9** · o primeiro executor fala; a fronteira do replay |
| `c293be65` | **O10R** · os nomes deixam de prometer mais do que provam |
| `8e1947d2` | **O9R** · o sensor sai do replay e entra na estrada oficial |
| `a13565b6` | **preflight** · quatro nomes que ainda prometiam demais |
| `700da777` | **M2** · a rota atravessa DERIVED → STRUCTURED → ADMISSION |
| `ef9803bb` | **M2** · a aresta deixa de ser desenhada e passa a ser percorrida |

## A rota da M2, e quem são os donos

```
DERIVED      coleta/derivacao_forward.py      → executor_texto_de_pdf.derivar_um
                                                 → guarda/preservar_derivado.py
STRUCTURED   coleta/social_persistencia.py     o dono de public.conteudo
ADMISSION    admissao/admissao.py              a peneira comum
COSTURA      coleta/rota_forward_documento.py  não reimplementa nenhuma decisão
```

`ROUTE_IDENTITY` = o par **`(source_id, route_class_id)`** = **`(IT-T2-002, RC-1)`**.
**Não é um id novo:** é a chave por que a `024` agrupa `v_saude_da_rota` — *«a
saúde é do par (fonte, rota)»*.

## O que `ef9803bb` fechou, e por que era o que faltava

O portão já exigia que **a mesma rota** carregasse as três etapas. Isso é
necessário e não chega:

```
TRÊS ETAPAS NA MESMA ROTA PODEM SER TRÊS ACONTECIMENTOS SOLTOS.
```

Medido no banco, não suposto — na corrida que provava a rota havia
`STRUCTURED edge_from=DERIVED PASS` e **nenhuma passagem de `DERIVED`**: a
etapa de cima correra noutra corrida, noutro ficheiro.

```
DECLARED EDGE ≠ OBSERVED EDGE.
UMA SETA DESENHADA NÃO É UM CAMINHO PERCORRIDO.
```

E o artefato também não viajava: o `STRUCTURED` lia um ficheiro de
`data/derivados/texto/` (o registo **legado**), e não o `derived_artifact` que
o DERIVED acabara de escrever.

```
ARTEFATO QUE NÃO VIAJA NÃO É ARESTA: É COINCIDÊNCIA.
```

Agora `rastro.o_que_a_rota_observou()` lê do **banco** e só conta uma aresta
com os **dois topos**. O que fica só declarado aparece em
`ARESTAS_DECLARADAS_SEM_TOPO` — visível, e não contado.

## GOOD_PATH · uma corrida, uma rota, o artefato a viajar

`provas/a_rota_m2_atravessa.py` — 18 factos contra PostgreSQL 16 descartável:

```
raw_asset REAL       escrito pelo dono do bruto, id lido do banco
DERIVED              derived_artifact real, linhagem fechada no pai
o artefato viaja     os BYTES do derivado, conferidos por sha256
STRUCTURED           1 artefato → 1 registo
ADMISSION            a porta respondeu NAO_SEI · item por `unknown`
UMA rota na corrida  (IT-T2-002, RC-1)
as duas arestas      com os DOIS topos
conta fecha          UNACCOUNTED_INPUT = 0 nas três etapas
last good            ADMISSION
READY                zero — perguntado ao banco
```

⚠️ **A porta disse `NAO_SEI`, e isso não é falha.** O boletim agrometeo da
ARPAV não encontra vocabulário de universo nenhum. A **etapa** passou; o
**item** saiu por `unknown`. *Ausência de evidência não é evidência de
ausência* — por isso não é um `NAO`.

## FAULT_PATH

Os três caminhos de falha vivem em `tests/test_m2_rota_forward.py` (a outra
sessão): `STRUCTURED` recusa → `ADMISSION NOT_RUN` com `UPSTREAM_NOT_RUN`;
`STRUCTURED` quebra → `FAIL` com estado canónico; a porta diz **NÃO** (universo
T9) → a **etapa** continua `PASS` e o **item** sai por `REJECTED`.

```
UMA RECUSA NÃO É UMA FALHA TÉCNICA. A PENEIRA A FUNCIONAR NÃO É AVARIA.
```

E as mutações da aresta em `tests/test_m2_aresta_observada.py`: três etapas sem
arestas **não** abrem o portão; meia cadeia **não** abre; `NOT_RUN` não cobre.

## Os dois portões, e por que podem ser os dois `YES`

```
TELEMETRY_INFRASTRUCTURE_PROVED   YES   e agora CONSOME paridade_da_lingua
CANONICAL_FORWARD_PATH_PROVED     YES
M2_ROUTE_OBSERVABILITY_READY      YES   com as ARESTAS por trás
```

`QUESTION A ≠ QUESTION B` **não é** `ANSWER A ≠ ANSWER B`. A separação está no
dono, no critério e na evidência — e há mutação que exige que `YES/YES` seja
permitido.

## Um susto que virou trava

O censo media **e** escrevia na mesma função. Uma mutação que trocava o
veredito da paridade **gravou `PARIDADE: UNKNOWN` no artefato commitado**.

```
UM TESTE QUE PERSISTE A PRÓPRIA MENTIRA DEIXA-A LÁ DEPOIS DE ACABAR.
```

`medir_tudo()` mede e não toca no disco; `principal()` escreve. Há teste que
reprova se a medição voltar a alcançar o ficheiro.

## O que continua aberto, com nome

| gap | quem | o que custa |
|---|---|---|
| `RAW_FORWARD_NAO_EMITE` | `guarda/preservar_coleta.py` | a aresta `RAW→DERIVED` fica **declarada sem topo** — agora visível na medição, e não só em prosa |
| `CHANNEL_IDENTITY_NOT_RESOLVED` | ninguém | `conteudo` exige `canal_id`; criar canal exige decidir **de quem** ele é, e o writer recusa-se a escolher. *CHANNEL_ID prova o canal, não prova a origem.* Na prova é resolvido no banco descartável com dados do catálogo |
| `TELEMETRY_FAILURE_SEM_POLITICA` | ninguém | a excepção do rastro **sobe** pelo chamador; não há política escrita, e **não se inventou uma para passar num teste** |
| `024` não aplicada em produção | — | de propósito. Missão própria, com autorização própria |

## NEXT_CHECKPOINT

**O menor próximo trabalho é `CHANNEL_IDENTITY_NOT_RESOLVED`** — é a única
pré-condição que hoje só existe dentro do banco descartável, e é o que separa
«a rota corre numa bancada» de «a rota corre». Depois dele: `RAW_FORWARD_NAO_EMITE`,
que fecharia a única aresta que ainda é só declarada.

**Não** perseguir cobertura por número, **não** instrumentar executor genérico,
**não** tocar Portal nem Inteligência.

## Verificar em oito comandos

```bash
cd <repo> && git fetch origin && git status --porcelain
python3 system-map/scripts/validate_system_map.py
python3 provas/paridade_da_lingua.py
python3 provas/o_executor_conta_se.py
export BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel
python3 provas/o_forward_conta_se.py
python3 provas/a_rota_m2_atravessa.py
python3 -m unittest discover -s tests -q
```

Esperado: `SYSTEM_MAP_CHECK=PASS` · `PARIDADE=PASS` · `EXECUTOR_CONTA_SE=PASS` ·
`FORWARD_CONTA_SE=PASS` · `ROTA_M2_ATRAVESSA=PASS`, e a suíte em
**1629 · 1422 PASS · 17 FAIL · 20 ERROR · 170 SKIP**, com as **38 falhas
herdadas** medidas em `700da777` (`NEW_FAILURES = 0`).

⚠️ `pdftotext` (poppler-utils) tem de estar na máquina. Sem ele as provas
**recusam correr**, em vez de passarem a verde medindo a ausência da máquina.

**Zero escritas em produção. Zero Supabase. Zero rede na coleta. `024` por
aplicar. A M2 termina em ADMISSION — e terminar aí é a verdade.**
