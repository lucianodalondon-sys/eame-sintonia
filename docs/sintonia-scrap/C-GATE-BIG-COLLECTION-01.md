# C-GATE-BIG-COLLECTION-01 · O READY EXISTE MESMO — e a linha está na Sala

> **A prova anterior media, e media com honestidade:** a etapa `READY` correu e
> **nenhum READY existiu**. Esta missão foi ver a linha.

```
BIG_COLLECTION_GATE = PARTIAL
BIG_COLLECTION_READY = NO

ONE_INTEGRATED_CANDIDATE        YES
MIGRATION_032_POSTGRES          PASS
READY_19_POSTGRES               PASS
MEDIA_TO_ADMISSION              PROVEN
ADMISSIBLE_CANARY_ADMISSION_SIM PROVEN
READY_ACTUALLY_CREATED          PROVEN
WAITING_ROOM_ACTUALLY_HIT       PROVEN
PROCESS_EXIT_DURABILITY         PROVEN
CANONICAL_COLLECTION_GATE_RUNNABLE  YES (o portão de egresso) · ver J
NEW_FAILURES                    0
SYSTEM_MAP_CHECK                PASS
LIVE_TOUCHED                    NO
```

**`PARTIAL`, e a razão é uma só:** o job `postgres-descartavel` continua
vermelho num passo **anterior a esta missão**, cuja causa é arquitectural e
está diagnosticada na secção J. Nada foi escondido para obter verde.

---

# A · GIT / ANCESTRY

| | |
|---|---|
| `MEDIA_BRANCH` / `HEAD` | `claude/youtube-italia-caption-audio-8b460b` · `fa980fe7` |
| `FACTS_BRANCH` / `HEAD` | `claude/collection-preserve-facts-2139eb` · `4708f772` |
| `merge-base` | `56617781` |
| divergência | **23** commits só em MEDIA · **4** só em FACTS |
| candidata | **`claude/big-collection-gate-01`** (nova, a partir de MEDIA) |
| `DIRTY_STATE` | limpa no arranque · 37 worktrees vivos na máquina |

```
FACTS NÃO estava em MEDIA.  MEDIA NÃO estava em FACTS.
```

Nenhuma continha a outra, e eram **complementares**:

```
MEDIA  executor_transcricao_midia · executor_para · dispatch por unidade
       migration 032 ........... AUSENTE
FACTS  migration 032 · CAMPOS_READY de 19 · o fato na Sala
       executor de mídia ....... AUSENTE
```

---

# B · O QUE FOI INTEGRADO

```
ponte de mídia                    coleta/executor_transcricao_midia.py
registry/dispatch de derivação    ingresso.executor_para · _cabe_na_capacidade
contrato de proveniência          regras/proveniencia.py (TEXT_KIND/RELATION)
preservação dos 19 campos         admissao.pronto_para_inteligencia
migration 032                     supabase/migrations/032_*.sql
Sala correspondente               admissao/sala_de_espera.py (19 campos)
provas e testes de ambos os lados
```

Verificado depois da fusão: `CAMPOS_READY = 19` · migration 032 presente ·
`executor_para` sobreviveu · despacho por unidade sobreviveu.

## O único conflito de código era a mesma lei escrita duas vezes

`generate_system_map.py`: **os dois lados consertaram o mesmo defeito** — o
gerador a escrever CRLF numa pasta que o `.gitattributes` declara `-text`,
abrindo diffs de 80 mil linhas sem uma vírgula de conteúdo.

Ficou a versão de MEDIA, **por medição**: ela confere NUL nos primeiros 4096
bytes e deixa binário passar intacto. A versão inline lê tudo como utf-8 — e
teria corrompido um `.png` ou uma fonte no dia em que a pasta publicada levasse
um.

```
DUAS ABAS A CONSERTAR A MESMA COISA PRODUZEM DUAS LEIS.
ESCOLHE-SE UMA POR MEDIÇÃO, E NÃO POR ORDEM DE CHEGADA.
```

Os JSON gerados **não** foram resolvidos à mão: regenerados pela cadeia
canónica, como o `§2` manda.

---

# C · O QUE NÃO FOI INTEGRADO

- Nada de `LIVE`. Nenhuma credencial de produção foi lida.
- O `2b5` do job antigo **não foi consertado** (secção J).
- Os testes da Sala que constroem READY de 12 campos à mão continuam
  vermelhos — dívida da FACTS, medida na secção K e **não mascarada**.

---

# D · POSTGRES / MIGRATION 032

Contra `postgres:16` descartável, no CI (`job portao-big-collection`):

```
MIGRATIONS_APLICADAS   31   (a 008 fica de fora: é verificação pós-aplicação)
MIGRATION_032_APPLIED  True
COLUNAS_NA_SALA        24
```

As **sete colunas** da 032 existem na tabela: `estagio` · `fact_time_basis` ·
`fact_location_basis` · `published_at` · `observed_at` ·
`source_declared_evidence_class` · `fato`.

```
READY_CONTRACT_FIELDS     19   (lido do dono, não contado à mão)
CAMPOS_COM_COLUNA_PROPRIA 17
```

⚠️ **E os outros dois estão certos assim.** A primeira versão da prova exigia
coluna homónima para os 19 e **reprovava sobre uma tabela correcta**:

```
ESTADO   constante do contrato — guardar uma coluna cujo valor é sempre o
         mesmo seria guardar a palavra, e não o facto
CORRIDA  mora em `run_id`, que é como a casa inteira lhe chama. Uma segunda
         coluna seria um segundo nome para a mesma identidade, livre para divergir
```

```
UM CAMPO DE CONTRATO NÃO É UMA COLUNA. A EQUIVALÊNCIA DECLARA-SE.
```

A equivalência passou a ser **declarada e verificada**: se um deles ganhar
coluna própria ou mudar de casa, o caso reprova e obriga a reescrevê-la.

---

# E · MÍDIA ATÉ ADMISSION

`job ponte-de-midia` · **SUCCESS** na candidata integrada:

```
RUN → RAW OBSERVATION → STORAGE → DERIVED (TRANSCRIPTION) → STRUCTURED → ADMISSION
TEXT_KIND = TRANSCRIPT   TEXT_RELATION = ORIGINAL   LANGUAGE = it (DETECTED)
ADMISSION_DECISION = NAO_SEI
```

**E isto continua a NÃO ser `FULL_MEDIA_TO_WAITING_ROOM`.** A porta disse
`NAO_SEI`, a Sala ficou vazia, e a verdade anterior fica preservada — como o
`§3` exige. A Admissão **não foi enfraquecida** para a mídia entrar.

`SOURCE_ID` não fabricado (`FIXTURE-DE-PROVA/FALA-SINTETICA-C4H`, que se anuncia
no próprio nome) · `RAW_OBSERVATION_ID = raw_asset.id`, lido do banco.

---

# F · CANÁRIO ADMISSION = SIM

```
CANARIOS_TENTADOS          IT-T3-010: SIM
ADMISSION_DECISION_CANARIO SIM        (boletim Mosca dell'Olivo, universo T3)
CONTROLO_NEGATIVO          NAO_SEI    (texto de preço e mercado em T3)
```

O canário **não foi escolhido por ser fácil**: é um boletim italiano real que
`provas/a_porta_le_italiano.py` já media como positivo antes desta missão. E há
**controlo negativo na mesma corrida** — uma porta que só diz SIM não é uma
porta.

```
A RÉGUA NÃO SE MEXEU. O OBJETIVO É PROVAR A ESTRADA, NÃO CONVENCER A ADMISSÃO.
```

---

# G · O READY REAL

```
RAW_OBSERVATION_ID   1        (raw_asset.id, escrito pelo dono e lido do banco)
READY_FIELD_COUNT    19       (contado no objeto produzido)
ADMITIDO_POR         "pertence ao universo v5"
```

O READY sai do **construtor único** — `admissao.pronto_para_inteligencia` — e
não de um dicionário montado pela prova.

---

# H · A SALA, COM LINHA

```
SALA_BACKEND   POSTGRES   CANONICO = True
SALA_ESTADO    PASSED     escrita publicada nesta execução
WAITING_ROWS   1          contadas NA TABELA, não no recibo
```

⚠️ **O backend é declarado ao NÍVEL DO JOB**, e não dentro de um passo. Sem
isso o dono da Sala cai para `FICHEIRO`, e um READY escrito no disco efémero do
runner passaria por READY persistido. É a mesma lei que o portão de egresso
guarda:

```
UM PORTÃO QUE MEDE UM AMBIENTE E DEIXA PASSAR PARA OUTRO NÃO MEDIU NADA.
```

## E a durabilidade, noutro processo

```
READY_EXISTS_AFTER_PROCESS_EXIT  True
LEITURA_CAMPOS                   19
VIA                              sala_de_espera.ler
```

O processo escritor terminou. Um **interpretador novo** perguntou ao **dono
canónico** — não à tabela:

```
PERGUNTAR À TABELA NÃO É PERGUNTAR AO DONO.
```

Um `select` mediria o Postgres; no dia em que o dono mudasse de forma de
guardar, a prova continuaria verde sobre uma casa vazia. A linhagem fecha do
outro lado: observação, corrida e fonte batem.

```
PORTAO_BIG_COLLECTION = PROVADO · 18 passaram · 0 falharam
```

---

# I · RETRY

Medido na prova de mídia, e **declarado como é**:

```
RETRY = ERROR   (e NÃO REUSED)
RETRY_SEGUNDA_OBSERVACAO_ADOTA_O_FILHO = NO
DERIVADOS_NO_BANCO = 1   (nenhum duplicado)
```

A identidade do derivado é por **conteúdo**; a linha tem chave estrangeira
composta `(raw_asset_id, parent_sha256)`. Duas corridas sobre os mesmos bytes
produzem duas observações; o filho já existe e aponta para a primeira.

**Não foi corrigido de carona**, como o `§8` manda. Fica como **dívida aberta**,
e é a mesma trava que o PDF sempre teve — nunca exercitada com duas observações
do mesmo byte.

---

# J · EGRESS / CANONICAL GATE

## O portão de egresso volta a correr — e era só uma dependência

`provas/o_egresso_antes_da_aquisicao.py` abortava **há dias, em todas as
branches**, com `ModuleNotFoundError: yaml`. Causa medida: PyYAML ausente no
runner. **Não é arquitectura.**

Escrever um analisador de YAML caseiro para fugir à dependência poria um segundo
dono a interpretar o mesmo ficheiro — e um analisador que se engane deixa o
portão passar por cima da lei que ele guarda.

```
CASOS=34 · PASS=34 · FAIL=0 · RED_TEAM_SURVIVORS=0
EGRESSO_ANTES_DA_AQUISICAO = PASS          →  CANONICAL_COLLECTION_GATE = RUNNABLE
```

```
UM PORTÃO QUE NÃO CORRE NÃO É UM PORTÃO FECHADO: É UM PORTÃO AUSENTE,
E ELE ESTAVA VERMELHO A DIZER ISSO.
```

## ⚠️ E consertá-lo revelou o passo de trás — HARD STOP

Com o `2b6` a correr, o job passou a falhar **antes**, no `2b5`
(`a_sala_sobrevive_ao_processo.py`). Medido: **já falhava na própria FACTS**, no
HEAD dela, antes desta fusão.

A causa **não** é 12 vs 19 campos. É outra, e é arquitectural:

```
ValueError: item NAO SEI nao passou a porta (NAO_SEI)
```

O ataque 26 dessa prova precisa de **dois itens com o MESMO `ITEM_ID` ambíguo**
para verificar que `espera.retirar` os recusa. A prova comenta, por escrito:
*«`admissao.decidir()` devolve "?" quando o item não traz id nem url»*. Hoje já
não devolve: `"?"` virou `NAO SEI`, e **a porta recusa item sem identidade**.

```
A CASA FICOU MAIS ESTRITA, E O ATAQUE DEIXOU DE SER CONSTRUÍVEL PELA PORTA.
```

Decidir se a guarda de ambiguidade em `retirar` continua alcançável — e por
onde — é **mudança arquitectural**. `§9`: HARD STOP e reportar. Não foi
escondido, não foi *skippado*, e o job continua vermelho a dizê-lo.

---

# K · REGRESSÃO

Medida **nos dois pais**, com worktrees temporários, e comparada por nome.

```
TEST_COUNT   MEDIA 3831 · FACTS 3802 · CANDIDATA 3878
FICHEIROS    MEDIA 163  · FACTS 161  · CANDIDATA 164
DISAPPEARED_TESTS = 0   (nenhum ficheiro dos pais sumiu na fusão)
NEW_FAILURES      = 0
```

| suíte | MEDIA | FACTS | candidata |
|---|---|---|---|
| `test_metricas` | 5 falhas | **5 falhas** | 5 falhas — **as mesmas** |
| `test_a_sala_de_espera_tem_um_dono` | — | 1+5 | 1+5 — ficheiro **idêntico** ao da FACTS |
| `test_sala_duravel` · `test_scrap_convergencia` | — | — | `fcntl` ausente no Windows |
| `test_c6_especie_do_texto` | 3 | 3 | 3 — as mesmas |
| `test_c4h_ponte_de_midia` | 27 OK | — | **27 OK** |
| `test_a_collection_preserva_o_fato` | — | 47 OK | **47 OK** |
| `test_red_team_estrada` | — | 18 OK | **18 OK** |

As 5 falhas de `test_metricas` são `TEST_COUNT_CURRENT`: quatro documentos
publicam **3.952** e nenhuma das três árvores tem esse número. É stale de uma
linhagem anterior, **em ambos os pais**.

---

# L · RED TEAM

| ataque | resultado |
|---|---|
| migration 032 ausente | **MORTO** · `A1`, aplicada e medida na corrida |
| READY ainda com 12 campos | **MORTO** · `B1` 19 do dono · `D1` 19 produzidos · `E2` 19 lidos |
| Admission `NAO_SEI` contado como READY | **MORTO** · a mídia deu `NAO_SEI` e a Sala ficou **vazia**; só o canário `SIM` pousou |
| etapa READY registada mas nenhum READY produzido | **MORTO** · `D6` conta a LINHA, não o recibo |
| módulo Sala existente sem linha WAITING | **MORTO** · `WAITING_ROWS = 1` |
| mídia desviada para PDF | **MORTO** · `B3b` + 5 tipos em `test_c4h` |
| CAPTION tratado como TRANSCRIPT | **MORTO** · `TEXT_BASIS = PRODUCED_BY_LOCAL_ASR` |
| source/location promovido para fact/location | **MORTO** · `test_a_sala_de_espera_nao_tem_morada` (14 OK) + `a_collection_preserva_o_fato` (47 OK) |
| publication time promovido para fact time | **MORTO** · `PUBLISHED_AT`/`OBSERVED_AT` têm campo próprio; `FACT_TIME` não faz fallback |
| retry mascarado como REUSED | **MORTO** · declarado `ERROR`, secção I |
| System Map declarando FLOW por módulo/edge | **MORTO** · `SYSTEM_MAP_CHECK = PASS`; nenhuma aresta virou `OBSERVED` sem correr |
| know-how concorrente | **MORTO** · `docs/know-how/` retirada, delta movido para `handoff/` (secção P) |
| egress gate não executável | **MORTO** · 34/34, secção J |

```
SOBREVIVENTES = 0
```

*(Um ataque não exercitado nunca foi contado como morto: as etapas sem banco,
na prova local, saem `NOT_EXERCISED`.)*

---

# M · SYSTEM MAP

```
SYSTEM_MAP_CHECK = PASS   ·   peças 190   ·   ligações 975
```

Regenerado pela cadeia canónica. Nenhum JSON editado à mão — inclusive os que
conflituaram na fusão.

---

# N · DESCONHECIDOS

- Se a guarda de ambiguidade de `espera.retirar` continua alcançável depois de
  a porta passar a recusar item sem identidade (secção J).
- Como a casa quer que duas observações do mesmo conteúdo partilhem um derivado
  (secção I).
- De onde vem `3.952` em quatro documentos — nenhuma das três árvores o produz.
- Se `postgres-descartavel` tem outras avarias **depois** do `2b5`: ainda
  ninguém passou desse passo.

---

# O · RISCOS

O maior não é técnico. **A ponte de mídia está provada e não tem quem lhe
entregue bytes numa corrida real** — nenhuma rota de aquisição de mídia está
autorizada (YouTube fechado por política, Instagram por `robots.txt`). O canário
que pousou na Sala é um **documento**, não mídia.

```
A ESTRADA ESTÁ PROVADA DE PONTA A PONTA. O QUE ENTRA NELA, HOJE, É PDF.
```

---

# P · KNOW-HOW

```
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
```

`docs/know-how/SECAO-A-PONTE-DE-MIDIA.md` foi **retirado**. A C4H escreveu-o
com número em branco — a intenção era boa — mas **o sítio estava errado**: uma
pasta `know-how/` dentro do repositório é, para quem chegar depois, um segundo
lugar onde procurar a lei.

```
NÃO RECLAMAR O NÚMERO NÃO CHEGA. UM DELTA NO SÍTIO ERRADO
AINDA É UM SEGUNDO ENDEREÇO PARA A MESMA AUTORIDADE.
```

Convertido para `handoff/KNOW-HOW-DELTA-A-PONTE-DE-MIDIA.md`, na forma que os
outros três já fixaram, com a cabeça canónica **medida agora**:

```
KNOW_HOW_MEDIDO  claude/sintonia-eame-know-how-v1 @ 5705ac7b
ÚLTIMA SECÇÃO    §119
NÚMERO DESTA     por atribuir — quem integrar escolhe o primeiro livre
```

---

# Q · VEREDITO

```
BIG_COLLECTION_GATE = PARTIAL
```

Dez dos onze critérios estão `PASS`/`PROVEN`. O que falta não é a estrada: é o
job antigo, vermelho num passo anterior a esta missão, cuja causa é
arquitectural e está reportada em vez de contornada.

# R · BIG_COLLECTION_READY

```
BIG_COLLECTION_READY = NO
```

# S · PRÓXIMO PASSO MÍNIMO — um só

```
DECIDIR O `2b5`: a guarda de ambiguidade de `espera.retirar` ainda é
alcançável agora que a porta recusa item sem identidade?

  · se SIM  — a prova reconstrói o par ambíguo por outro caminho
  · se NÃO  — a prova declara o ataque defendido a montante, e diz onde

É a única coisa entre a candidata e um `postgres-descartavel` verde.
```
