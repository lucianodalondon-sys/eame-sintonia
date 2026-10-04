# A ÁRVORE ÚNICA DA INTELLIGENCE — RELATÓRIO V1

```
MISSAO      C-INT-ATOMICITY-01
ESPECIE     INTEGRACAO + RE-ARBITRAGEM + PROVA
MEDIDO_EM   2026-09-14
IMPLEMENTACAO_AUTORIZADA   NAO
```

> Pergunta única:
>
> *Conseguimos construir uma árvore Git que contenha simultaneamente as
> autoridades e provas da Intelligence e, a partir dela, re-medir corretamente
> os conceitos e owners?*
>
> **Sim. E a re-medição já corrigiu duas conclusões anteriores — uma delas
> minha.**

---

# 1 · A CORREÇÃO OBRIGATÓRIA — E A CAUSA, PROVADA

```
PREVIOUS_NO_COMMON_ANCESTOR_CLAIM = FALSO
ACTUAL_MERGE_BASE                 = 96933996e136cbbbca17dbe99e75f668fe050ec5
                                    2026-08-29
CAUSE_OF_PREVIOUS_DISCREPANCY     = CLONE RASO (PROVADO, NAO INFERIDO)
```

## A medição

```
git rev-parse --is-shallow-repository   ->  true
cat .git/shallow                        ->  472b4f9da48fa9f62002d6435bfcb52dd2f15f84
git log -1 472b4f9d                     ->  2026-09-06
git merge-base --is-ancestor 96933996 472b4f9d  ->  verdadeiro
```

O ancestral comum é de **2026-08-29**; o enxerto cortava em **2026-09-06**. O
`git merge-base` devolveu vazio porque, dentro do grafo que lhe deram, vazio
**era** a resposta certa.

## A prova, antes e depois de um comando que não mudou código nenhum

| | antes | depois de `git fetch --unshallow` |
|---|---|---|
| `--is-shallow-repository` | `true` | `false` |
| profundidade da branch | 51 commits | **190 commits** |
| `merge-base` com 7 autoridades | vazio, 7× | `96933996`, **7×** |

```
LOCAL_GRAPH_COMPLETE   = SIM (depois do unshallow)
SHALLOW_REPOSITORY     = NAO (era SIM)
REMOTE_REFS_CURRENT    = SIM · git fetch --all --prune corrido
```

Os sete HEADs do enunciado foram re-medidos e **nenhum mudou**.

```
UM CLONE RASO NAO DEVOLVE ERRO. DEVOLVE SILENCIO.
E SILENCIO LE-SE COMO AUSENCIA.
```

---

# 2 · O TRONCO

```
TRUNK_SELECTED = claude/epic-archimedes-ryo0ms @ dc00583d
```

**Re-medido, não herdado.** Quatro branches contêm a linha funcional
`f888776d`. A mais recente é `claude/sala-persistente-preflight-real-v1`
(`12c919af`), 46 segundos mais nova — e foi **recusada**:

```
o que ela traz a mais:
  supabase/migrations/031_a_sala_de_espera_ganha_dono_duravel.sql   238 linhas
  provas/a_sala_sobrevive_ao_processo.py                            627 linhas
  provas/o_egresso_antes_da_aquisicao.py                            212 linhas
  superficie/rede.py                                                150 linhas
```

É **Collection em andamento**, com migration por aplicar. O §6 proíbe
incorporá-la só para ficar mais novo.

```
TRUNK_REASON = o estado funcional mais actual que NAO importa trabalho
               de Collection ainda por fechar
```

---

# 3 · A BRANCH DE INTEGRAÇÃO — E POR QUE NÃO É A DESIGNADA

`claude/label-intelligence-v1-italy` é a linha do piloto **Label Intelligence**,
divergida do tronco em 2026-08-29. Medido:

```
ficheiros tocados pelo lado PILOTO desde a base   279
ficheiros tocados pelo lado TRONCO desde a base  1772
INTERSECAO                                         33
merge de ensaio (worktree descartavel)             32 conflitos
```

Dos 32, seis são runtime e CI adjacentes à Collection — `scripts/coletor.py`,
`scripts/portao.py`, `scripts/proveniencia.py` e três workflows. Resolvê-los é
decisão do dono da Collection, e seria exatamente o ataque 2 do red team.

```
FINAL_BRANCH = claude/intelligence-atomicity-v1   (autorizada explicitamente)
```

O ensaio de merge correu numa **worktree descartável** e foi abortado. Nada
dele entrou.

---

# 4 · AS AUTORIDADES INTEGRADAS

| autoridade | origem | commit | caminho final | status |
|---|---|---|---|---|
| Bíblia de Engenharia da Intelligence V0.2 | `research/intelligence-bible-engineering-v1` | `7ae1b510` | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` | `CANDIDATE` |
| Benchmark de engenharia | idem | `7ae1b510` | `research/intelligence/BENCHMARK-DE-ENGENHARIA-...md` | pesquisa |
| Red team da Bíblia V0.2 | idem | `7ae1b510` | `research/intelligence/RED-TEAM-BIBLIA-...md` | evidência |
| Motor Intelligence V2 — requisitos | `claude/intelligence-backlog-canonical` | `4df24aa9` | `docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` | contrato subordinado |
| Backlog obrigatório V2 | idem | `4df24aa9` | `docs/intelligence/BACKLOG-OBRIGATORIO.md` | contrato |
| Arbitragem da Intelligence V1 | `claude/funny-hypatia-y7ho5s` | `87712a01` | `docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md` | arbitragem |
| Concept Ownership V1 (21 conceitos) | idem | `87712a01` | `docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V1.json` | arbitragem |
| Censo da Intelligence | idem | `87712a01` | `docs/operacao/CENSO-ATUAL-DA-INTELLIGENCE.{md,json}` | medição ⚠️ |
| Authority Registry (38 autoridades) | idem | `87712a01` | `controle/AUTORIDADES-CANONICAS.json` | registo |
| Sala de Controle | idem | `87712a01` | `SALA-DE-CONTROLE-SINTONIA.md` | control plane |
| Benchmark agro + 9 irmãos | **já no tronco** | `dc00583d` | `research/intelligence/AGRO-*.md` | pesquisa |
| Espinha: contrato, arbitragem, red team | `claude/label-intelligence-v1-italy` | `b755ecff` | `research/intelligence/INTELLIGENCE-SPINE-*` | candidato |
| Espinha: máquina + provas | idem | `b755ecff` | `provas/espinha_da_intelligence.py` · `tests/` | prova |
| Know-how canónico + 25 peças | `claude/sintonia-eame-know-how-v1` | `338e171a` | `SINTONIA-EAME-KNOW-HOW.md` · `know-how/` | **único** |
| Bíblia canónica da Coleta | **já no tronco** | `dc00583d` | `BIBLIA-CANONICA-DA-COLETA.md` | canónica |
| `GESTAO_DA_COLETA/v1` | **já no tronco** | `dc00583d` | `leis/gestao_da_coleta.py` | contrato |
| Contrato READY (12 campos) | **já no tronco** | `dc00583d` | `admissao/admissao.py` | em runtime |

⚠️ `docs/operacao/CENSO-DA-INTELLIGENCE.md` **diverge de `87712a01` em uma
palavra**: um caminho pessoal Windows foi redigido para `<UTILIZADOR>`. Ver §9.

## O conflito que a missão anterior previu, resolvido por medição

`controle/AUTORIDADES-CANONICAS.json` existia nas duas branches, diferente.

```
7ae1b510 (Biblia)      36 autoridades
87712a01 (arbitragem)  38 autoridades

so na arbitragem:  A-BIBLIA-ENG-INTELIGENCIA · A-MOTOR-V2-REQUISITOS
so na Biblia:      nenhuma
diferente:         A-BIBLIA-INTELIGENCIA — e a arbitragem so LHE ACRESCENTA
                   SUPERSEDED_BY e fecha o RECOVERY_PENDING
```

O registo mais novo contém o mais antigo inteiro. **Não houve merge criativo:
houve uma medição que mostrou qual supersede qual.**

## O que NÃO foi trazido, e porquê

```
AGENTS.md                          o tronco esta A FRENTE  (-368 linhas se viesse)
.github/workflows/system-map.yml   o tronco esta A FRENTE  (-490 linhas)
handoff/KNOW-HOW-DELTA-MORADA-DA-SALA-DE-ESPERA.md
                                   e delta da COLLECTION. Vinha na mesma pasta;
                                   nao vem no mesmo saco.
10 dos 16 ficheiros de b755ecff    metricas e documentos da branch do piloto
```

```
ATAQUE 1 DO RED TEAM MORREU AQUI, E MORREU POR MEDICAO PREVIA —
NAO POR SORTE.
```

---

# 5 · A ARBITRAGEM RE-MEDIDA

`provas/arbitragem_da_intelligence.py` · `docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V2.json`

```
conceitos 25 · owner provado 7 · so definido 9 · sem dono humano 2 · CONFLITO 0
```

## ⚠️ Primeira correção: eram 21, não 22

O enunciado — e a minha própria entrega anterior — dizem que a arbitragem V1
tinha **22 conceitos**. Contados:

```
len(INTELLIGENCE-CONCEPT-OWNERSHIP-V1.json["CONCEITOS"])  ->  21
```

Ninguém contou. Repetiu-se.

## Como se chegou a 25

```
ARB-V1                     21
ESPINHA                    15
uniao com apelidos resolvidos   24
+ SCREENING                     1   (era portao sem entrada no censo)
                           = 25
```

## A tabela

| conceito | owner | current | verdict |
|---|---|---|---|
| `SOURCE_FACT / READY_ITEM` | COLLECTION | IMPLEMENTED | OWNER_PROVEN |
| `CLAIM_DOMAIN_JUDGMENT` | INTELLIGENCE | IMPLEMENTED | OWNER_PROVEN |
| `CROSSING` | INTELLIGENCE | IMPLEMENTED | OWNER_PROVEN |
| `CONVERGENCE` | INTELLIGENCE | IMPLEMENTED | OWNER_PROVEN |
| `FINDING / ANALYTIC_JUDGMENT` | INTELLIGENCE | IMPLEMENTED | OWNER_PROVEN |
| `OPPORTUNITY` | INTELLIGENCE | IMPLEMENTED | OWNER_PROVEN |
| `GAP / SATISFACTION / DECISION / ROTA` | **COLLECTION** | IMPLEMENTED | OWNER_PROVEN |
| `INTELLIGENCE_REQUEST` | INTELLIGENCE | DEFINED_ONLY | declarado |
| `INTELLIGENCE_RUN` | INTELLIGENCE | DEFINED_ONLY | declarado |
| `SCREENING` | INTELLIGENCE | DEFINED_ONLY | declarado |
| `DEPENDENCY / INDEPENDENCE` | INTELLIGENCE | DEFINED_ONLY | declarado |
| `ANALYTIC_ASSUMPTION` | INTELLIGENCE | DEFINED_ONLY | declarado |
| `ANALYTIC_HYPOTHESIS` | INTELLIGENCE | DEFINED_ONLY | declarado |
| `REVERSAL / DEMOTED_BY` | INTELLIGENCE | DEFINED_ONLY | declarado |
| `ANALYTIC_RECOMMENDATION` | INTELLIGENCE | DEFINED_ONLY | declarado |
| `INTELLIGENCE_REQUIREMENT` | INTELLIGENCE | DEFINED_ONLY | declarado |
| `SIGNAL` · `SUPPORT` · `CONTRADICTION` · `VALIDATION_STATE` · `FUTURE_SIGNAL` · `INTELLIGENCE_PACKAGE` · `CONFIDENCE` | INTELLIGENCE | DISPERSO | declarado |
| `RELEVANCE` | **HUMAN_DECISION_REQUIRED** | DISPERSO | por decidir |
| `PRIORITY` | **HUMAN_DECISION_REQUIRED** | DISPERSO | por decidir |

## ⚠️ Segunda correção: `DEFINED_ONLY` não existia, e faltava

Um `grep` cru conta lei e código no mesmo saldo. O instrumento passou a separar:

```
ABSENT         ninguem o menciona
DEFINED_ONLY   so em lei e prova — contrato, nao runtime
DISPERSO       em codigo de producao, sem dono unico
IMPLEMENTED    ha modulo dono, e ele existe
```

```
CONTAR LEI E CODIGO NO MESMO SALDO FOI COMO A INTELLIGENCE
CHEGOU A TER DOCUMENTO A DIZER IMPLEMENTED SOBRE CONTRATO.
```

## O que mudou face à arbitragem V1

| | V1 | V2 | porquê |
|---|---|---|---|
| conceitos | 21 | 25 | união + `SCREENING`; apelidos resolvidos |
| `COLLECTION_GAP` | 1 conceito, owner INTELLIGENCE, «0 ficheiros» | **2 conceitos, 2 owners, ambos IMPLEMENTED do lado certo** | a V1 correu sem `leis/gestao_da_coleta.py` |
| estado de 9 conceitos | «NÃO IMPLEMENTADO» | `DEFINED_ONLY` | passaram a ter lei na mesma árvore |
| conflitos de dono | não mensurável | **0** | as autoridades coexistem |
| `RELEVANCE` · `PRIORITY` | sem dono | **sem dono** | inalterado, e por decisão |

---

# 6 · `COLLECTION_GAP` — O CASO TESTEMUNHA

```
VEREDITO = CONFIRMED
```

E com prova mais dura do que a hipótese que o propôs.

```
motor/ e superficie/  tocam  GAP_ID · SATISFACTION_STATE · COLLECT_NOW ·
                             DO_NOT_COLLECT · DEFER_UNKNOWN
                             em ZERO ficheiros
```

E a costura entre os dois donos é **um campo só** — declarado pela própria lei
da Collection:

```
CAMPOS_DA_NECESSIDADE ∩ CAMPOS_DA_FALTA  =  {REQUIREMENT_ID}
```

```
INTELLIGENCE  escreve a NECESSIDADE inteira (7 campos)
COLLECTION    mede a FALTA, decide e escolhe a rota
A COSTURA     REQUIREMENT_ID, e mais nada
```

A divisão não foi inventada pela Intelligence. Estava desenhada em
`GESTAO_DA_COLETA/v1` desde 2026-09-08, à espera de um declarante que o
contrato não nomeia.

```
UM CONTRATO COM UMA CHAVE ESTRANGEIRA PARA NINGUEM
ESTA A DESCREVER UM DONO QUE AINDA NAO CHEGOU.
```

---

# 7 · A ESPINHA, RE-VALIDADA CONTRA A ÁRVORE COMPLETA

Nenhuma das cinco decisões da missão anterior foi contradita. **Uma ganhou
prova que antes não podia existir:**

```
admissao.pronto_para_inteligencia()   ->  12 campos
CAMPOS_DO_READY (copia declarada)     ->  12 campos
so no real: []      so na copia: []
```

Na branch onde a espinha nasceu, `admissao/` não existia e a cópia não tinha
contra o que ser conferida.

```
UMA COPIA QUE NINGUEM PODE CONFERIR NAO E UMA COPIA: E UMA CRENCA.
```

| decisão da `C-INT-SPINE-01` | re-medida | estado |
|---|---|---|
| `EVIDENCE` não é entidade da Intelligence | contrato real = 12/12 campos, dono Collection | **CONFIRMADA** |
| `JUDGMENT` não é estágio separado | ARB-V1 e Bíblia concordam; Motor V2 não cria duplicado (0 ocorrências) | **CONFIRMADA** |
| `CANDIDATE_FINDING = ANALYTIC_HYPOTHESIS` | nenhuma autoridade define os dois | **CONFIRMADA** |
| `VALIDATION_QUEUE` é projeção de estado | `fila_de_validacao()` sem id, sem persistência | **CONFIRMADA** |
| `REVERSAL` é transição, não entidade | 7 causas; `Evento` frozen; `Historia` sem `apagar` | **CONFIRMADA** |

E o bloqueio `G0` continua medido: **nenhum dos 8 campos agronómicos atravessa
a fronteira.** O teste falha no dia em que atravessar — e falhar é o certo.

---

# 8 · AS PROVAS

```
python3 -m unittest tests.test_atomicidade_da_intelligence     36 testes · OK
python3 -m unittest tests.test_espinha_da_intelligence         39 testes · OK
python3 -m unittest discover -s tests                        3960 testes
```

| prova | o que morde | estado |
|---|---|---|
| `P1` | as 15 autoridades abrem na mesma árvore; a fotografia é declarada; **shallow = false** | ✅ |
| `P2` | um só know-how; uma Bíblia por domínio; o registo aponta para caminhos que existem | ✅ |
| `P3` | a re-arbitragem corre aqui; 0 conflitos; o V2 gravado bate com a medição de agora | ✅ |
| `P4` | `GESTAO_DA_COLETA/v1` é dono do gap; Intelligence não o escreve; a costura é 1 campo | ✅ |
| `P5–P10` | a cópia do contrato READY bate com o real; `SIGNAL ≠ FINDING`; crossing sem julgamento; fila é projeção; reversão preserva; dois domínios | ✅ |
| `P10b` | **a exceção pedida à trava, paga com prova** | ✅ |
| `P11` | o mapa observa; nenhum documento diz `IMPLEMENTED` sem módulo | ✅ |
| `P12` | zero ficheiros de Collection, Portal ou migration tocados; a integração só acrescentou; tudo o que mudou tem gerador ou razão escrita | ✅ |

---

# 9 · O QUE FOI TOCADO FORA DA INTELLIGENCE, E PORQUÊ

Três, e cada uma tem nome.

## 9.1 · `system-map/data/architecture.declared.json` — §17

O validador reprovou duas vezes, e **as duas tinham razão**:

```
P9  provas/espinha_da_intelligence.py e arbitragem_da_intelligence.py
    eram codigo que o mapa nao conhecia
P8  ao declara-los, reivindiquei tests/ que ja era de C-TESTES
```

Consertado na fonte. `SYSTEM_MAP_CHECK=PASS`.

## 9.2 · `system-map/scripts/censo_do_congelamento.py` — a trava da Collection

A integração fez morder a trava. Dois falsos positivos do classificador:

```
provas/arbitragem_da_intelligence.py -> IMPLEMENTATION
   escreve SIGNAL/CROSSING/OPPORTUNITY por extenso — para os PROCURAR
controle/AUTORIDADES-CANONICAS.json  -> CONTRACT
   declara "SCHEMA" — mas o contrato e de GOVERNANCA
```

O contrato da trava já os autorizava («preservar histórico», «medir o que a
inteligência futura vai esperar da coleta») e o classificador já tinha
`INSTRUMENTOS` para isto. Declarados lá, **com a exceção paga por `P10b`**.

```
provas/espinha_da_intelligence.py NAO pediu excepcao — continua sob a trava.
```

## 9.3 · `docs/operacao/CENSO-DA-INTELLIGENCE.md` — dado pessoal

O guarda de credenciais apanhou `C:\Users\<NOME>\AppData\Local` no censo que
integrei — ele estava a **citar** o defeito de `motor/v21_tm_colher.py` e
trouxe o nome de utilizador junto. Redigido para `<UTILIZADOR>`, que é a saída
que o próprio regex do guarda desenhou (`[A-Z]:\\Users\\(?!<)`).

```
⚠️ DIVERGENCIA DECLARADA: esta copia difere de 87712a01 em UMA palavra.
   O dono do censo deve redigi-lo na origem.
```

---

# 10 · TESTES — BASELINE VERSUS FINAL

```
BASELINE_TESTS      3885      (tronco dc00583d, medido antes de tocar em nada)
BASELINE_FAILURES     18 falhas + 16 erros = 34
FINAL_TESTS         3960
FINAL_FAILURES        18 falhas + 16 erros = 34
NEW_FAILURES           0
RESOLVIDAS             0
```

O conjunto de falhas é **idêntico**, nome a nome.

## As 34 falhas herdadas — não maquiadas

Estavam vermelhas no tronco antes desta missão e continuam. Duas merecem nome
porque a missão as diagnosticou de caminho:

```
test_a_contagem_de_testes_do_handoff_bate
test_o_total_de_testes_declarado_vem_da_suite
   CAUSA MEDIDA: o ledger publica `3.967` com separador de milhar e os dois
   guardas exigem `3967` sem ele. Ficou visivel quando a suite passou de 1000.
   NAO CORRIGIDO: escolher entre as duas grafias e uma convencao de publicacao,
   e nao e da Intelligence.

test_nenhum_artefato_congelado_mudou
   6 artefatos de coleta/ derivaram no tronco. Nenhum e desta missao.
```

## §8 · O defeito do sincronizador **não foi portado**

```
O TRONCO JA O TINHA CORRIGIDO, SOZINHO, EM 2026-08-29.
```

`pacote/metricas_canonicas.py::documentos_com_numero()` já percorre a raiz, e o
comentário escreve o mesmo diagnóstico que eu tinha escrito na branch do
piloto. E o crash latente do marcador sem dono **não é alcançável**: o
`<!--M:NOME-->` da prosa não tem fecho, e o regex não o apanha.

```
DUAS MEDICOES INDEPENDENTES ACHARAM O MESMO BURACO E TAPARAM-NO IGUAL.
PORTAR A SEGUNDA SERIA PO-LO DUAS VEZES.
```

O que **foi** feito: correr o `--sync` canónico. Os 8 documentos estavam em
`3.892` desde antes desta missão, e as minhas provas moveram o número. Deixá-los
velhos seria o defeito; digitá-los também.

---

# 11 · SYSTEM MAP

```
SYSTEM_MAP_CHECK = PASS · o mapa corresponde ao repositorio
```

Cadeia canónica completa corrida: 20 scanners + `generate_system_map` +
`censo_da_topologia` + `validate_system_map`. Nenhum JSON gerado foi editado à
mão — e há prova disso:

```
test_nenhum_gerado_foi_editado_a_mao
test_tudo_o_que_foi_modificado_tem_gerador_com_nome
```

A segunda apanhou **as minhas próprias edições** na primeira versão, e o
conserto não foi alargar a categoria «gerado» até as engolir: foi separar a
terceira, com a razão de cada uma escrita ao lado.

```
O QUE E GERADO DECLARA-SE PELO SUFIXO, NAO PELA PASTA.
```

⚠️ O espelho do mapa vive em `italia-portale/client/system-map/` e mudou 536
linhas. Medido antes de aceitar: **2 ids entram, 0 saem**, e os dois são os que
esta missão declarou.

---

# 12 · RED TEAM

| # | ataque | veredito | como caiu |
|---|---|---|---|
| 1 | artefato antigo sobrescreve versão mais nova | **KILLED** | medido antes: `AGENTS.md` e o workflow do mapa ficaram fora; `P12` prova que a integração só acrescentou |
| 2 | merge traz código de Collection acidentalmente | **KILLED** | merge recusado; ensaio em worktree descartável; `P12` prova 0 ficheiros de `coleta/`, `admissao/`, `guarda/`, `leis/` |
| 3 | Motor V2 cria conceito duplicado | **KILLED** | 0 ocorrências de `CANDIDATE_FINDING`, `VALIDATION_QUEUE`, `ANALYTIC_HYPOTHESIS`, `INTELLIGENCE_RUN`, `COLLECTION_GAP` |
| 4 | Bíblia e arbitragem divergem em ownership | **KILLED** | `INT-LAW-000` × 21 conceitos da V1 → 0 choques |
| 5 | Authority Registry aponta para branch antiga | **KILLED** | `P2` exige que `CANONICAL_PATH` das duas autoridades da Intelligence resolva nesta árvore |
| 6 | System Map acha duas autoridades para o mesmo conceito | **KILLED** | `P8_UM_DONO` do validador; e ele apanhou-me a mim |
| 7 | `COLLECTION_GAP` volta a ser um conceito único | **KILLED** | `P4`, 4 testes; e a costura de 1 campo |
| 8 | `RELEVANCE` ganha owner por acidente | **KILLED** | `HUMAN_DECISION_REQUIRED` no V2; nenhum portão o consulta |
| 9 | `PRIORITY` ganha owner por acidente | **KILLED** | idem |
| 10 | branch integrada contém dois know-hows | **KILLED** | `P2`, 2 testes |
| 11 | documentos dizem IMPLEMENTED onde há só contrato | **KILLED** | `DEFINED_ONLY` existe agora; `P11` exige módulo para `IMPLEMENTED` |
| 12 | testes passam porque medem a fotografia errada | **KILLED** | `P1` exige `SHALLOW = false`; o instrumento declara o commit |
| 13 | commit da espinha traz alterações não relacionadas | **KILLED** | 6 de 16 ficheiros; os 10 do piloto ficaram |
| 14 | integração perde prova existente | **KILLED** | `P12`: 0 ficheiros com estado `D`; 39 provas da espinha correm aqui |
| 15 | integração altera Collection runtime | **PARTIAL** | 0 ficheiros de runtime. **Mas um scanner do System Map que serve a trava da Collection foi editado** — declarado, autorizado, e pago com `P10b` |

```
KILLED    14
PARTIAL    1
SURVIVED   0
```

O `PARTIAL` é honesto e está inteiro no §9.2: mexi num classificador de outra
frente. Não é runtime, não é lei, não muda o que a trava tranca — e a máquina
de estados da Intelligence **continua congelada por ela**.

---

# 13 · VEREDITOS

```
CONTROL_PLANE_ATOMICITY               = PASS
INTELLIGENCE_CONCEPT_ARBITRATION_VALID = YES
INTELLIGENCE_SPINE_CONTRACT_READY      = YES
BIBLE_CANONICAL_PROMOTION_READY        = NO
INTELLIGENCE_RUNTIME_IMPLEMENTED       = NO
COLLECTION_RUNTIME_CHANGED             = NO
PORTAL_CHANGED                         = NO   (só o espelho do System Map, regenerado)
LIVE_CHANGED                           = NO
MIGRATIONS_CHANGED                     = NO
```

## Por que `BIBLE_CANONICAL_PROMOTION_READY = NO`

A Bíblia fixa nove condições (§31). Medidas **agora**, nesta árvore:

| # | condição | antes | agora |
|---|---|---|---|
| 1 | reconciliação com a Bíblia da Collection | ✅ | ✅ |
| 2 | reconciliação com Motor V2 | ✅ | ✅ **re-medida aqui: 0 duplicados** |
| 3 | owner collision count = 0 | ⚠️ 2 pendentes | ⚠️ **2 pendentes** — `RELEVANCE`, `PRIORITY` |
| 4 | registo no Control Plane | ✅ | ✅ |
| 5 | **snapshot onde a autoridade não fique invisível** | ❌ **BLOQUEADOR** | ✅ **FECHADO POR ESTA MISSÃO** |
| 6 | governance gate | ✅ | ✅ |
| 7 | System Map pela cadeia canónica | ✅ | ✅ `PASS` |
| 8 | know-how delta aplicado ao owner canónico | ⚠️ pendente | ✅ **§111–§113 aplicados** |
| 9 | aprovação explícita da promoção | ❌ humana | ❌ **humana, e não é minha** |

```
DAS NOVE, RESTAM DUAS: OS DOIS DONOS HUMANOS, E A APROVACAO HUMANA.
E AS DUAS SAO DE GENTE.
```

---

# 14 · O QUE FICA EM NÃO SEI

```
NAO_SEI  quem possui RELEVANCE e PRIORITY. Nenhuma autoridade os nomeia, e
         esta missao nao os decidiu em silencio.

NAO_SEI  se `3.967` ou `3967` e a grafia certa do numero publicado. Os dois
         guardas do tronco discordam, e a escolha e uma convencao de
         publicacao que nao e da Intelligence.

NAO_SEI  por que 6 artefatos congelados de coleta/ derivaram no tronco.
         Medido que derivaram; nao medido o porque, e nao e desta frente.

NAO_SEI  se KIT/KIQ, FIELD_VOICES e DECISION_TELEMETRY devem entrar na Biblia
         antes da promocao. O inventario pediu-os; a V0.2 nao os tem.

NAO_SEI  se `CONFIDENCE` deve ter escala congelada. Continua NEEDS_CONTRACT.

NAO_SEI  o custo real dos sete portoes em corpus real. Nada correu contra a
         Sala de Espera, e continua a nao correr.

NAO_SEI  se o campo UNIVERSO do contrato READY chega para o universo analitico
         de INT-LAW-110/111.
```

Nenhum destes foi preenchido por inferência.

---

# 15 · KNOW-HOW

```
KNOW_HOW_DELTA = ATUALIZACAO NECESSARIA — E APLICADA
```

```
tail medido antes de escrever:   §110
escrito:                         §111 · §112 · §113
```

E foi aplicado **no ficheiro canónico**, não num handoff — porque desta vez o
ficheiro está na mesma árvore. O delta anterior (`handoff/KNOW-HOW-DELTA-
INTELLIGENCE-SPINE.md`) ganhou um aviso no topo dizendo que a sua premissa era
falsa, **sem ser apagado**:

```
UMA CORRECCAO QUE APAGA O ENGANO APAGA TAMBEM A LICAO.
```

---

# 16 · O PRÓXIMO PASSO MÍNIMO — UMA MISSÃO

```
C-INT-OWNER-01

   Levar a DECISAO HUMANA de quem possui RELEVANCE e PRIORITY, e so isso.

   Nao promove a Biblia. Nao implementa INTELLIGENCE_RUN.
   Nao toca Collection, Portal nem LIVE.
```

**Porquê esta, e não `INTELLIGENCE_RUN`:** das nove condições de promoção da
Bíblia, sete estão fechadas. As duas que faltam são a mesma coisa vista de dois
lados — dois conceitos sem dono, e uma aprovação humana que não pode acontecer
enquanto houver conceito sem dono.

```
IMPLEMENTAR INTELLIGENCE_RUN SOBRE UMA CONSTITUICAO NAO PROMOVIDA
E CONSTRUIR SOBRE UMA LEI QUE AINDA PODE MUDAR.
E DESTA VEZ O BLOQUEADOR NAO E TECNICO: SAO DUAS PERGUNTAS
QUE SO GENTE RESPONDE.
```
