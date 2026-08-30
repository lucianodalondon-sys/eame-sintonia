# As cicatrizes do Brasil, transferidas para o EAME

`2026-08-30` · último portão antes da primeira importação espanhola.
**Nada importado.** Nenhuma migration em produção, catálogo não importado, handoff não
mesclado, Supabase intocado.

> **`CATALOG_IMPORT_ENGINEERING_GATE = READY`** · **`EAME_COLLECTION_ENTRY_GATE = PARTIAL`**
> · **`RAW_PRESERVATION_GATE = OPEN_EXTERNAL_REPAIR`** · **`IMPORT_CAN_BE_NEXT_MISSION = NO`**
>
> São dois portões, e não um. Um nome estava fazendo dois trabalhos — a engenharia de
> importar o catálogo regulatório, que não tem lugar de fato, e a entrada da coleta em
> geral, que tem. Estados derivados em `scripts/portoes_eame.py`; nenhum deles é digitado.

---

## A cicatriz que governa todas as outras

Lida em `ACHADO-praca-do-canal-nao-e-praca-da-lavoura.md`, do repositório brasileiro:

> *"A regra existe. Ela não foi aplicada ao campo `praca` do documento — e é esse campo
> que decide a praça dos padrões publicados."*

Lá, a região do CANAL carimbava a região de cada documento. O padrão número 1 do portal
publicou 44 pessoas "discutindo nematoide de café" numa praça com 7.868 hectares de café
— contra 1,1 milhão de hectares na região que o sistema chamava de outra coisa. **E a lei
já estava escrita no `CLAUDE.md` deles.**

Por isso esta missão não termina em documento. Cada lei que dá para virar campo virou
campo, e cada campo tem uma tentativa de violá-lo que o banco recusa.

## O método

25 cicatrizes **lidas** do repositório brasileiro, não lembradas. Para cada uma:
`BRAZIL_LESSON` · `ONDE_NO_BRASIL` · `WHY_IT_EXISTS` · `EAME_APPLICABLE` · `EAME_STATUS` ·
`OWNER` · `EXECUTABLE_PROOF` · `GAP` · `MINIMAL_ACTION`.

**`PROVED` exige testemunha executável.** `scripts/cicatrizes_brasil.py` confere cada uma
contra o acervo — teste, constraint, função ou afirmação nomeada — e **rebaixa para
`NOT_MEASURED`** o que não encontrar. Há mutação provando que o verificador reprova:
uma testemunha inventada em tempo de execução derruba a linha.

Nenhum número, tabela ou decisão brasileira foi copiado. Há teste que reprova se os
números de lá (`7.868`, `4.548`, `299`) aparecerem como dado do EAME.

## O placar

| status | nº |
|---|---|
| **PROVED** | **20** |
| **PARTIAL** | **5** |
| ABSENT | 0 |
| NOT_MEASURED | 0 |

Por família: localização 3 · relevância 3 · ausência 3 · proveniência 3 · identidade 3 ·
unidade analítica 3 · resiliência 3 · tempo 2 · método 1 · isolamento 1.

## O que virou trava nesta rodada — migration 015

### Localização

As duas colunas existiam desde a 003. Faltava a terceira pergunta, que é a que o Brasil
pagou: **como se soube?**

```
ESCRITO   o texto afirma o lugar do fato
CITADO    o nome do lugar aparece no meio — o balde mais fraco
DA_FONTE  veio do cadastro da fonte   ⛔ PROIBIDO sustentar fact
DEDUZIDO  a inteligência inferiu      ⛔ PROIBIDO sustentar fact
```

Duas constraints. `local_do_fato_diz_como_se_soube` exige origem **e** trecho literal;
`local_da_fonte_nao_sustenta_local_do_fato` recusa `DA_FONTE` e `DEDUZIDO`. **A `praca`
brasileira deixa de ser possível de inserir.**

No Brasil `deduzido` era permitido com aviso escrito. Aqui não é — a 001 já dizia que
geografia é *"lugar declarado, NUNCA inferido"*, e agora a 015 torna essa lei impossível
de violar por este caminho.

| caso | resultado |
|---|---|
| **A** fonte em Foggia relata fato na Toscana | as duas linhas convivem; nenhuma vira a outra |
| **B** fonte tem lugar, fato não tem | `fact_precision = NOT_KNOWN`; Foggia não preencheu nada |
| **C** o fato nomeia a província | `PROVINCIA`, `ESCRITO`, com evidência |
| **D** país conhecido, região desconhecida | `PAIS` — o país não faz as vezes de uma região |
| **E** origem e evidência obrigatórias | sem elas o lugar do fato não entra |

Mutações: `DA_FONTE`, `DEDUZIDO` e "sem dizer como se soube" são **recusados pelo banco**.

### Relevância

`conteudo_crop_issue.relacao` já separava cinco forças desde a 004, com
`COOCORRENCIA_TEXTUAL` como a mais fraca e `evidencia` NOT NULL. Faltava o outro eixo:
`sinal`, e a resposta derivada à pergunta **"por que este conteúdo entrou?"**.

`f_relevancia_ao_caso` devolve `EXACT_SIGNAL / NEIGHBOURING_SIGNAL / CONTEXT_ONLY /
RETROSPECTIVE / UNRELATED` **com o motivo escrito**. Não é score — e há teste que reprova
se aparecer coluna de score.

| cicatriz italiana | resultado |
|---|---|
| `RIGHT_CLASS + WRONG_CROP ≠ CASE_SIGNAL` | `UNRELATED` |
| `RIGHT_CROP + WRONG_ISSUE ≠ CASE_SIGNAL` | `UNRELATED` |
| `RIGHT_TOPIC + WRONG_YEAR ≠ CASE_SIGNAL` | `RETROSPECTIVE` |
| `KEYWORD_MATCH ≠ RELEVANT_EVIDENCE` | `CONTEXT_ONLY` |
| país A não fecha pergunta do país B | `UNRELATED` |

A cicatriz brasileira que sustenta isso: **contagem alta com régua limpa continua não
distinguindo sentido.** `Leiteiro` é gado, `Cupim` é o meme, `Murcha` é seca, `Tiririca` é
grama de jardim, `Caruru` é comida — e as cinco voltaram altas na segunda medição.

### Ausência

`tentativa_de_coleta` separa **o mundo, a instalação e nós**:

```
RESPONDEU_COM_EVIDENCIA · RESPONDEU_SEM_O_CAMPO   ← o mundo
LOGIN_WALL · THROTTLED · NOT_FOUND · ACCESS_FAILURE ← a instalação
PARSER_FAILURE · SEM_CHECKPOINT_NAO_GASTEI · NAO_TESTADO ← nós
```

A cicatriz, textual: *"não li vestido de não há, desta vez PAGO: 299 fichas contadas como
'o perfil não declara lugar' quando ninguém chegou a perguntar"*. Um estado fora do
vocabulário é **recusado pelo banco**.

### Proveniência

`f_runs_pagos_sem_bruto` responde ao defeito medido na Itália: **ator executou + item
voltou + zero `raw_asset` = `PAGO_E_NAO_PRESERVADO`**. E uma rodada sem item sai como
`SEM_ITEM_NADA_A_PRESERVAR` — vazia é um estado, não um defeito.

## Os cinco PARTIAL, e o que cada um bloqueia

| id | lacuna | ação mínima | bloqueia |
|---|---|---|---|
| **BR-14** | o schema sabe marcar `obra_id` e `duplicata_de`; nenhum caminho produtivo foi medido contando obra distinta | medir o mesmo número pelos dois caminhos quando a primeira coleta social entrar | coleta social |
| **BR-16** | não existe estado `AGGREGATOR`. Um canal institucional e uma pessoa entram pelo mesmo caminho | medir quantas origens têm mais de um autor declarado — o censo brasileiro contou `autor_hash` distintos, e isso não é heurística | **HUMAN SENSOR LAYER** |
| **BR-19** | o vocabulário `SEM_CHECKPOINT_NAO_GASTEI` existe e a **guarda no chamador** não | pôr a guarda em `coletor.py`: sem linha aberta, não chama o ator | coleta paga |
| **BR-20** | os estados de rodada existem e a regra de não-repetir não está escrita no caminho produtivo | mesma guarda, mesmo lugar | coleta paga |
| **BR-21** | não há pool de chaves nem retomada | salvar o bruto por lote e declarar o pool como dado antes de usá-lo | coleta paga |

> **Os cinco foram fechados na rodada seguinte** (016 · 017 · `scripts/coleta_checkpoint.py`
> · `supabase/tests/regressoes_coleta.sql` · `tests/test_coleta_resiliente.py`). A tabela
> acima fica como estava porque é o registro do que se sabia então — ver
> `docs/relatorios/RELATORIO-PORTAO-DE-ENTRADA-DA-COLETA.md` para o estado corrente e para
> as **seis lacunas novas** que a conferência de localização abriu.

**Nenhum dos cinco bloqueia a importação do catálogo espanhol** — ela é SQL idempotente
sobre chave natural, não gasta rota paga e não coleta rede social. Os cinco bloqueiam a
**próxima coleta**, que é outra decisão.

Isso não torna o portão READY. O portão se chama *collection entry gate*, e cinco leis de
coleta não estão provadas.

## Contratos

| contrato | completo? |
|---|---|
| `LOCATION_CONTRACT_COMPLETE` | ~~**YES**~~ → **NO** — rebaixado pela conferência: BR-26 · BR-30 · BR-31 · BR-32 · BR-34 |
| `RELEVANCE_CONTRACT_COMPLETE` | **YES** |
| `TEMPORAL_CONTRACT_COMPLETE` | **YES** |
| `PROVENANCE_CONTRACT_COMPLETE` | **YES** |
| `IDENTITY_CONTRACT_COMPLETE` | **YES** |
| `UNKNOWN_STATE_CONTRACT_COMPLETE` | **YES** |
| `COUNTRY_ISOLATION_COMPLETE` | **YES** |
| `ANALYTICAL_UNIT_CONTRACT_COMPLETE` | ~~**NO**~~ → **YES** — BR-16 fechado na 016 |
| `RAW_PRESERVATION_GATE` | **OPEN_EXTERNAL_REPAIR** — 184 de 196 verificados, 12 falharam no envio, 0 hash divergente. Prova externa; ver `data/samples/RAW-GATE-ES.json` |
| `RESILIENCE_CONTRACT_COMPLETE` | ~~**NO**~~ → **YES** — BR-19 · BR-20 · BR-21 fechados |

O `LOCATION_CONTRACT_COMPLETE` saiu de **YES** e foi para **NO** na mesma rodada em que os
outros dois saíram de NO para YES. Isso não é um retrocesso: é o resultado de passar dez
cicatrizes brasileiras mais novas por cima de um contrato que já tinha sido dado por
fechado, e descobrir que ele fechava seis das dez. Manter o YES teria sido mover a régua.

## Ordem canônica das migrations

```
001–007 · 009 · 010–012 · 013 · 014 catálogo · 015 · 016 · 017 · 008 por último
```

**O 014 fica vago de propósito.** É o `010_catalogo_publico_fabricante.sql` da branch
paralela e só ganha número quando entrar. A reserva está escrita na 015 e o teste de
numeração aceita **buraco declarado** — e continua reprovando buraco silencioso.

## O que não foi reaberto

`CAPTURE ≠ REGISTRATION` · `BBCH 00–07` · `ISSUE_RELATIONS` · `CUPROXI FLO` · os quatro
relógios · country isolation · `ES-CASE-001`. Foram usados como **testes de controle** e
continuam verdes. Concorrência e Meta Ads permanecem congeladas.

## Uma honestidade, pela sexta vez — e duas na mesma manhã

Um teste que proíbe a palavra `score` reprovou no comentário que **enuncia** a proibição:
*"-- sem score. a relevância ao caso é derivada na pergunta"*. Corrigido para procurar
**coluna** chamada score, não a palavra.

E na mesma hora, a mesma armadilha em outra forma: a mutação que prova o verificador da
matriz usava uma testemunha falsa escrita **literalmente** no arquivo de teste — que está
dentro do corpus que o verificador varre. A testemunha existia, e o teste passava por
engano. Agora ela é montada em tempo de execução.

O padrão é sempre o mesmo: **a proibição escrita no lugar que a proibição varre**.

---

O detalhe linha a linha está em `data/samples/BRAZIL-LESSONS-TRANSFER-EAME.json`, e ele é
regenerável: `python3 scripts/cicatrizes_brasil.py --build`.
