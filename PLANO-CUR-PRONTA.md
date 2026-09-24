# PLANO CUR-PRONTA — o robô de fontes leva cada fonte até PRONTA

> Missão CUR-PRONTA (D28, 24/09/2026) + requisitos do dono: a **orquestra** (fontes, coleta e
> Intelligence nunca param), o **passo de IA contínuo** e a **janela de cultura** (D29).
> Ramo `curador-ate-pronta-v1`, a partir de `origin/bc4-correcoes-v1` (4a5afc27, o que está
> instalado + docs). **Nada foi instalado.** Tudo foi medido em cópias com os livros vivos
> copiados só por leitura (fotos de 09:09 e 10:24, sha256 em
> `provas/cur_pronta/FOTOS-DOS-LIVROS-VIVOS.sha256`).

## 1 · O que estava parado (medido na foto das 10:24)

**1040 fontes no livro e ZERO com tarefa aberta** (fila: 2333 DONE, 222 BLOCKED, 7 FAILED). O
ciclo vivo (`gatilho_discovery.talvez_alimentar`) só alimentava três coisas: REVIVER (FAILED
por transporte), REVALIDAR (as ELEGÍVEIS com prova > 7 dias) e a PONTE (candidata nova →
QUALIFY, uma vez por candidata). O `alimentar_fila.py` sabia pôr REPAIR/REVALIDATE/BUILD_CONTRACT
na fila, mas só corre à mão.

## 2 · A máquina de estados — estado → tarefa → dono → código → medido

Tabela viva: `py curadoria/funil_do_curador.py` (declarada em `MAQUINA`; os testes conferem que
todo o estado de `lifecycle.ESTADOS` tem linha, que o enfileirador existe e que o que se diz
AUTOMÁTICO é chamado pelo ciclo).

| estado | N (10:24) | tarefa que o avança | quem enfileira | automático no ciclo? |
|---|---:|---|---|---|
| CONTRACTED_CANARY_FAILED | 403 | REPAIR_CONTRACT | `reparar_encalhadas` (R1 v2, junta neste ramo) | **SIM** (era NÃO: R1 não instalada) |
| SEMANTIC_REVIEW | 198 | — | canal `decisao_semantica` (humano/Opus) | NÃO — é aqui que entra a IA (§6) |
| READY_FOR_COLLECTION | 143 | VALIDATE_ROUTE / BUILD_CONTRACT | `avancar_fontes` (LEGACY) + REVALIDAR (CURRENT) | **SIM** (era só CURRENT elegível) |
| CANARY_PENDING | 102 | VALIDATE_ROUTE/CANARY | cadeia do worker; órfãs: `reparar_encalhadas` (R1) | **SIM** |
| POLICY / AUTH / CAPABILITY / ROUTE_BLOCKED | 69/5/39/13 | — | decisão do dono / capacidade nova | NÃO, por desenho (`PARADOS`) |
| UNKNOWN | 34 | — | **NINGUÉM** | NÃO — buraco nomeado (33 são «item é capa») |
| DEGRADED | 18 | BUILD_CONTRACT (importa) → canário | `avancar_fontes` | **SIM** |
| RETRY_AFTER | 11 | VALIDATE_ROUTE | relógio da fila; sem tarefa > 24 h: `avancar_fontes` | **SIM** |
| CONTRACT_PENDING | 5 | BUILD_CONTRACT | worker após QUALIFY; sem tarefa: `avancar_fontes` | **SIM** |
| RECONCILIATION_REQUIRED | 0 | — | ninguém (adaptador noutra árvore) | NÃO — buraco por desenho |

## 3 · Os três buracos, fechados no dono certo

**(a) READY pela régua antiga (100)** — `curadoria/avancar_fontes.py`, nível 0d do gatilho:
- 26 HTML com contrato do robô → VALIDATE_ROUTE → canário → a régua dos quatro passos decide;
- 24 com contrato **só na tabela do coletor** → BUILD_CONTRACT importa a linha (molde da casa,
  ACQUISITION **igual byte a byte** à da coleta; `ROUTE_PROVENANCE.INTEGRADO_EM` = agora, para a
  promoção antiga continuar LEGACY); a tabela é só lida;
- 41 canais YouTube pelo feed (Disallow no robots): não se re-medem pelo feed (iria para
  ROUTE_BLOCKED); o caminho é a rota do Scrap — buraco social (c);
- 8 do piloto com contrato escrito à mão: buraco nomeado, dono Collection.

**(b) Reparo** — o dono é a R1 (`reparar_contrato.py`, REPAIR_CONTRACT determinístico, UM por
fonte). Este ramo **junta a R1 v2** (9c05877e, o último validado; o CHECKPOINT 8f4cc16b «NÃO
testado» fica de fora) e não duplica nada dela. As 18 DEGRADED (BCR-2026-09-20, contrato só na
tabela do coletor) entram pelo AVANÇAR: importar → canário → se falhar, CCF → R1.
`SEM_CONTRATO_DE_COLETA` / `SEM_RECEITA_WEB_PARA_T8/T9/T12` (19 no portão da BC) **não são do
Curator**: são da tabela do coletor (`onboardar_rotas_provadas.py --aplicar`, pela mão do dono) e
das receitas da Collection — ficam nomeados, não se enfileiram aqui.

**(c) Sociais** — devolvida ao ramo **só a SOC2** (a SOC3 continua fora; 0 vermelhos novos nos
módulos das 4 leis): QUALIFY de canal YouTube com `channel_id` → SOURCE_ID → contrato
`SCRAP_FASE` (a rota é do Scrap, conferida pela matriz) → VALIDATE_ROUTE OK. **O canário para**:
é uma colheita do Scrap no runner, com a chave que só lá existe; o Curator não corre o Scrap
(D28: sem disparo paralelo). Falta, com dono: o pedido ao orquestrador para o canário
(`canal-youtube`, `--fonte`, `--canal_id`) e a leitura do resultado de volta como evidência
(o mecanismo existe na SOC5, que está fora da linha por assentar na SOC3); e a resolução dos
`@handle`/`/user/` (SOC4, no runner).

## 4 · Prioridade: avanço e reparo antes de descoberta

Ordem do gatilho (resolvida na junção com a R1): REVIVER → REVALIDAR → **REPARAR (R1, 0c)** →
**AVANÇAR (CUR, 0d)** → FEEDER → `REPARO_ANTES_DE_DISCOVERY` → `AVANCO_ANTES_DE_DISCOVERY` →
DISCOVERY. A procura de fontes novas só abre com reparo **e** avanço elegíveis a zero.

**D29 — janela de cultura sobe na fila** (`curadoria/janela_de_cultura.py`): todo o T3 (PEST /
DISEASE / WEEDS no Atlas) + quem se declara janela com uma FRASE (bollettino agrometeorologico,
fitosanitario, consorzio di difesa, difesa integrata...). Palavras soltas mentiam: a primeira
regra deu 59 e trazia «Bandi e avvisi pubblici», o Bollettino Ufficiale e páginas institucionais
do CREA; com frases, **21**. Passam à frente no AVANÇAR e no REPARAR (+15 de prioridade). Só a
ordem do Curator; a agenda da Collection não é tocada.

| janela (foto 10:24) | N |
|---|---:|
| no livro | 21 (T3 17, T1 2, T2 2) |
| CANARY_PENDING | 8 |
| READY_FOR_COLLECTION | 5 |
| CONTRACTED_CANARY_FAILED | 3 |
| UNKNOWN / DEGRADED / SEMANTIC | 2 / 2 / 1 |
| elegíveis no portão (depois das voltas) | 1 |

## 5 · A orquestra — o Curator continua durante a coleta

**Medido ficheiro a ficheiro: nenhum dos dois escreve nos ficheiros do outro.**

| ficheiro | Curator | Coleta |
|---|---|---|
| `curadoria/LIFECYCLE-LEDGER`, `-QUEUE`, `-EVIDENCE`, `italy_contracts_curator`, `SOURCE-ID-ALLOCATION`, `BRIDGE-LEDGER`, `DISCOVERY-*`, `READY-BATCHES`, `candidatas/FONTES-CANDIDATAS` | escreve | **lê** (portão, por fonte) |
| `regras/italy_contracts_onboarded.json` (tabela do coletor) | lê | lê (quem escreve é o dono, `onboardar_rotas_provadas`) |
| `data/collection-ledger/italy/*`, `collection-store`, `data/samples/LIVRO-DE-DECISOES`, `RUN-MANIFEST`, Sala | — | escreve |
| `interface_collection.source_repair_needed` (Collection → livro) | — | **ninguém a chama** fora de testes/provas |

**A colisão era de LEITURA**: `italy_executor.admissao_do_curator` pergunta ao portão VIVO antes
de CADA fonte. Com o Curator a trabalhar, (1) uma fonte da coorte tirada de READY por uma
re-medição é recusada a meio da onda; (2) o worker escrevia evidência e contratos por cima do
ficheiro (`write_text`) — leitura a meio = JSON cortado = GATE_NAO_RESPONDEU; (3) no Windows o
leitor trava o `os.replace` do escritor; (4) a cortesia por host da A5 vale num processo, não
entre dois.

**O desenho** (`curadoria/onda_em_curso.py`): quem abre a onda grava a FOTO da coorte
(`data/collection-ledger/italy/ONDA-EM-CURSO.json`, com o sha256 do `COORTE-BIG-COLLECTION.json`).
Com a foto: o portão perguntado por `--ids` responde por ela e **não abre livro do Curator**; foto
ilegível = NÃO SEI = recusa (rc 3); o AVANÇAR não canaria anfitriões da onda; o que o Curator
promover entra na onda seguinte. O worker passou a escrever evidência e contratos de forma
atómica (temporário + `os.replace` com a paciência da fila).

**Prova (dois processos ao mesmo tempo, `provas/cur_pronta/PROVA-ORQUESTRA.json`)** — coorte 37,
3 ciclos de perguntas pelo caminho do executor, enquanto o Curator tira as 37 de READY e escreve:

| | COM a foto | SEM a foto (hoje) |
|---|---:|---:|
| admitidas | **111 / 111** | **0 / 111** (ESTADO_NAO_READY) |
| portão sem resposta | 0 | 0 |
| escritas do Curator / falhas | 459 / 0 | 756 / 0 |

Passo 1 do BIG-COLLECTION-RUNBOOK passa a ser: **abrir a onda** (`py curadoria/onda_em_curso.py
--abrir <COORTE>`), não parar o bot; fechar no fim (`--fechar`).

## 6 · O passo de IA contínuo (desenho — NÃO construído; «sem pago» nesta missão)

**Onde a regra para hoje** (foto 10:24):

| motivo | fontes | porta determinística por onde a proposta volta |
|---|---:|---|
| território NÃO SEI | 197 | `decisao_semantica` (≥1 institucional + ≥2 de conteúdo, URL + sha256) → QUALIFY |
| padrão de endereços não casa (EMPTY_LIST) | 391 (346 CCF + 45 CANARY_PENDING) | só o que a R1 **recusa** → porta de contratos D10 da R1 (`reparar_contrato.aplicar`) → VALIDATE_ROUTE → CANARY → régua |
| item é capa / sem corpo | 111 (29 + 33 + 49) | proposta de outro INDEX_URL/LINK_PATTERN → mesma porta D10 → canário → régua |

**Como**: um executor à parte (`ia_propoe`, não o worker), que só corre sobre fontes paradas há
> 24 h e que a regra já recusou. O **Curator busca as páginas** (o mesmo leitor do canário) e
guarda bytes e sha256; a IA **lê esse texto** e devolve uma PROPOSTA estruturada (território +
papéis das provas; ou INDEX_URL + LINK_PATTERN + o item que o canário abriria). A proposta
escreve-se num livro próprio (`PROPOSTAS-IA-V1.json`, append) e **atravessa as portas de
sempre**: a IA nunca escreve no livro de estados, nunca promove, nunca contorna o canário nem a
régua. Uma proposta por fonte por 7 dias; teto diário `IA_POR_DIA`; sem prova = NÃO SEI.

**Motor**: `claude-opus-5-5` (o oficial). Pensamento sempre ligado (não se desliga); esforço
`medium` (o padrão dele); saída estruturada (`output_config.format`), sem `tool_choice`
forçado (400 neste modelo).

**Custo (tabela oficial: US$ 4 / 1M de entrada, US$ 20 / 1M de saída, cache US$ 0,20 / 1M; Batch
= metade)** — ESTIMATIVA, não medida (nenhuma chamada foi feita):
- por caso: ~3 páginas × ~6 mil tokens ≈ 18 mil de entrada + ~4,5 mil de saída (pensamento
  incluído) ≈ **US$ 0,16** (em lote ≈ US$ 0,08);
- a passagem pelos ~700 parados: ≈ **US$ 110** (lote ≈ US$ 55);
- contínuo: depende do ritmo de descoberta — com ~60 paragens novas/dia, ≈ US$ 10/dia
  (lote ≈ US$ 5). Margem de erro grande: a página real pode ter 2× ou ½ destes tokens.

**O que destravaria — medido onde há medida, NÃO SEI onde não há**: a única medida real da casa
é o lote semântico S2/S3 (181 decisões Opus 5.5): **25 decididas (14 %)**, 156 NÃO SEI; 18
viraram SOURCE_ID na produção e **5 estão READY hoje** (13 CCF). Aplicado às 197: ~27 decididas,
~7 READY. Para padrões e capas **NÃO SEI**: a R1 determinística levou 29 de 432 a READY; a IA
pode fazer melhor ou pior. Proposta: um **piloto de 30 casos (≈ US$ 5)**, medido, antes de ligar
em contínuo.

**Dependência da conta**: precisa de credencial da API (chave ou perfil `ant`), que **não** é a
assinatura do Claude Code. A troca de conta de hoje mostra o risco: sem credencial ou com limite
atingido, o passo pára e o ciclo determinístico continua (a IA é opcional e falha para NÃO SEI).
A regra desta missão é «sem pago»: ligar a IA é **decisão do dono**.

## 7 · Antes → depois (cópia do livro vivo, rede pela VPN IT, só o CUR sem a R1)

Oito voltas do ciclo, egresso IT conferido em cada volta e no fim, até o avanço elegível chegar a 0
(`provas/cur_pronta/CICLO-COM-REDE-8-VOLTAS.*`):

| | antes | depois |
|---|---:|---:|
| READY pela régua de hoje — WEB | 43 | **57** |
| elegíveis no portão (o que a coleta pode colher) | 37 | **50** |
| READY pela régua antiga — WEB (nunca colhia) | 59 | 12 |
| READY — SOCIAL (todas antigas, pelo feed) | 41 | 41 |
| fontes com tarefa aberta | 0 | 7 |
| avanço elegível | 143 | 0 |

As READY antigas que caíram não foram perdidas: a régua de hoje reprovou-as com prova e estão em
CCF, à espera do reparo da R1. Social: 59 QUALIFY de canais → 30 com número (28 **já eram fontes**
— a QUALIFY reconheceu o mesmo canal, sem duplicar; 2 novos à espera do canário do Scrap) e 29 NÃO
SEI (`/user/`, `@handle` sem channel_id — resolução no runner, SOC4).

Achados no caminho:
- a tabela do coletor tem contratos cujo LINK_PATTERN casa com a própria INDEX_URL (IT-T2-023
  ARPA Basilicata, IT-T5-025): o validador do robô recusa importá-los — a coleta pode estar a
  guardar a página de listagem como item;
- a QUALIFY aloca o SOURCE_ID mas **não o escreve de volta** na ficha da porta das candidatas; o
  funil conta pelos dois (sem isso dizia 762 web + 170 social «sem número»; são 184 + 118);
- `alimentar_fila.py` nunca foi ligado ao ciclo — as regras dele vivem agora no AVANÇAR.

**Medida conjunta CUR + R1** (a que vai ser instalada): em §9, quando o egresso IT voltar.

## 8 · Plano de instalação e WRITESET (não instalar: o coordenador decide o momento)

O ramo **descende da R1 v2** (9c05877e): instalar a R1 e depois este ramo não tem colisão
(o único conflito de código, o gatilho, está resolvido aqui). Se a R1 ainda não estiver instalada,
este ramo instala-a junto — é a mesma árvore.

| peça | na INSTALAÇÃO escreve | em FUNCIONAMENTO passa a escrever | livros tocados na instalação |
|---|---|---|---|
| **CUR-PRONTA** (este ramo) | código: `curadoria/avancar_fontes.py`, `funil_do_curador.py`, `onda_em_curso.py`, `janela_de_cultura.py`, `gatilho_discovery.py`, `worker.py`, `collection_gate.py`, a SOC2 (`rota_do_scrap_youtube.py`, `escrever_contratos.py`, `validar_contratos.py`, `linkedin_pelo_site.py`, `coleta/italy_pilot_collect.mjs` guarda COLETADO_POR, `regras/italy_contracts.mjs`), testes, provas, docs e mapa | os MESMOS livros de hoje, pelo MESMO processo (o bot): `LIFECYCLE-QUEUE` (mais tarefas: AVANÇAR 20/volta), `LIFECYCLE-LEDGER`/`-EVIDENCE` (append), `italy_contracts_curator.json` (contratos importados da tabela do coletor); **lê** `ONDA-EM-CURSO.json` | **0** |
| **R1 v2** (dentro deste ramo) | `reparar_contrato.py`, `gatilho_discovery.py`, `worker.py`, `fila.py` | `italy_contracts_curator.json` (REPAIR_CONTRACT), livros do ciclo | 0 |
| **quem abre a onda** (coordenador) | — | `data/collection-ledger/italy/ONDA-EM-CURSO.json` (abrir/fechar) | — |

Um escritor por livro: tudo o que escreve livro do Curator é o processo do bot. A onda é escrita
por quem a abre e só lida pelo resto.

Passos: os do `CUTOVER-RUNBOOK.md` / `PLANO-INSTALACAO-M5G.md` (parar com PARAR.flag, foto dos
livros, `merge --no-ff` no bot + ff na ponte, conferir 0 livros mudados, relançar, medir; DESFAZER
= `git reset --keep <HEAD_antes>`). Ensaio desta árvore sobre a cópia fiel: §9.

## 9 · Ensaio da instalação (feito) — cópia fiel do vivo, 24/09 ~13:25

`provas/cur_pronta/ensaio_instalacao.sh` + `ENSAIO-INSTALACAO.log` (só lê o vivo; bot parado por
PARAR.flag de outra operação nessa hora — não tocado):

```
VIVO bot   servico-20260923-0923 @ fca4f2b6  (14 livros alterados + 20 pastas novas do acervo)
VIVO ponte cutover-20260923-0923 @ 4a5afc27  (3 livros alterados)
FINAL      ce2e8fb7
BOT 1. merge --no-ff (com os livros no sitio)      rc=0  conflitos=0
BOT 2. livros alterados: IGUAIS byte a byte (14)
BOT 3. arvore commitada vs FINAL: 0 ficheiros diferentes
BOT 4. testes na copia instalada: 93 corridos, OK (portao, guarda, avancar, onda, reparo)
       portao com os livros vivos: elegiveis = 37 de 143
BOT 5. DESFAZER: git reset --keep fca4f2b6   rc=0, 0 codigo diferente, livros IGUAIS
PONTE  4a5afc27 esta na linha: avanco rapido rc=0; livros IGUAIS (3); --lane presente;
       DESFAZER rc=0, livros IGUAIS
```

Medida conjunta CUR + R1 com rede: parada à porta — o portão de egresso deu
`EGRESS_COUNTRY_CODE = UNKNOWN` (o serviço de medição não devolveu país) desde as 13:15; o
lançador tenta de 2 em 2 min e não faz nenhum pedido sem IT. A medida da R1 sozinha, na cópia
do vivo, está no ramo dela (143 → 189 READY; 29 das 432 por reparar chegam a READY).
