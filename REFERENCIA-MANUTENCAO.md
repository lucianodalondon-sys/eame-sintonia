# REFERENCIA-MANUTENCAO — D116 + D117 (dono, 27/09/2026)

Ramo `claude/reference-maintenance-collection-8s2lwy`, base `18461b9`. Offline: nenhum site visitado,
nenhum coletor/scraper/banco novo. Livros vivos intocados (`curadoria/*-V1.json`, `data/collection-ledger`,
`candidatas/FONTES-CANDIDATAS.json`).

## A · Quem colheu IT-T4-001, e por que não houve coleta em 21/09

**O coletor canônico** é `coleta/italy_pilot_collect.mjs` (ramo `case "IT-T4-001"`, `:768` descoberta, `:847`
identidade), chamado por dois caminhos:

| caminho | quem manda | IT-T4-001 |
|---|---|---|
| **manual**: `orquestrador/orquestrador.py` → receita `italia-recorrente` → `coleta/italy_executor.py` → Node | pedido de pessoa | foi assim a corrida `XX-T3-2026-09-18-172035-48e8b1ad851f9d53` (`data/samples/RUN-MANIFEST.json`: `acionamento MANUAL`, `alvo T3`, `fonte=IT-T4-001`, `COMANDO coleta/italy_executor.py IT-T4-001`). O `XX-T3` é o prefixo `{pais}-{alvo}` de um pedido sem país e com alvo T3 (o BG-05 ainda obrigava T3) |
| **agendado**: Agendador do Windows → `ferramentas/italy-forward-only-live.cmd` → `coleta/italy_recurrent_collect.mjs --gate-hour` (20h Roma) | relógio, de hora em hora | **nunca** colheu IT-T4-001 |

A «recoleta» da MISSAO-RECOLLECTION **não é agenda**: `RECOLLECTION: { DETAIL_CONTENT: "IMMUTABLE" }`
(`regras/italy_contracts.mjs:205`) responde «revisito um detalhe já conhecido?», e **nenhum contrato tinha campo
que dissesse QUANDO voltar à fonte**. Os «7 contratos com RECOLLECTION» são 7 regras de revisita, não 7 cadências.

**Por que não houve coleta em 21/09 (e nenhuma depois de 18/09) — três causas, cada uma provada:**

1. **A agenda nunca a incluiu.** Até 22/09 o perfil tinha lista fixa `SOURCES: ["IT-T3-005","IT-T2-002","IT-T2-004"]`
   (comentário datado em `candidatas/italy_profiles.mjs:4-10`); IT-T4-001 não estava nela.
2. **A agenda estava partida.** O lançador apontava para `scripts\italy_recurrent_collect.mjs`, que já não existia;
   a tarefa devolvia `Último resultado: 1` de hora em hora até ao conserto de 22/09 (`ferramentas/italy-forward-only-live.cmd:17-26`).
3. **Desde 21-22/09 o portão recusa-a nos dois caminhos.** `curadoria/collection_gate.py:161` → `MOTIVO READY_LEGACY`
   (medido hoje: `STATE READY_FOR_COLLECTION · READY_RULE LEGACY`). A agenda pergunta ao portão sem lista (passo 6b) e o
   manual pergunta em `coleta/italy_executor.py:679` (desde 21/09). Prova no livro de corridas:
   `data/collection-ledger/italy/logs/runs.log`, corrida `OPS_forward-only-live_20260922185447_a9d037` (terça 22/09,
   20h Roma, 9 fontes colhidas) — IT-T4-001 em `COLLECTION_REFUSED_BY_MOTIVE.READY_LEGACY`.

> Nenhuma das réguas que admitem hoje (`DETAIL/v1`, `PAGINA_BOLETIM/v1`, `SOCIAL/v1`) foi feita para um CSV de dados
> abertos. **Destravar é decisão do dono/Curator** (livro vivo) — ver `COMANDO-HOJE.md`. Não foi feito aqui.

## B · A cadência D117 no mecanismo que já existe

- **Contrato (dono da cadência):** `regras/italy_contracts.mjs:210` `CADENCIA` em IT-T4-001 (SEMANAL · TER · retenta
  QUA/QUI · alerta continua); `:222` `ENDPOINTS_DE_REFERENCIA.ETICHETTE` (bulas: ROTACAO_DIARIA até 3/dia, disparadas pelo
  diff primeiro, robots obrigatório, teto 5/`salute.gov.it`/24 h **partilhado com o CSV**); `:537` em IT-T9-008
  `ENDPOINTS_DE_REFERENCIA.CATALOGO` (portfólio: MENSAL + EXTRAORDINARIA pelo diff). Bulas e portfólio entram como
  **endpoints** das fontes que já existem (COL-LAW-009/205, mesma decisão do know-how §127) — sem SOURCE_ID novo, sem
  tocar em `candidatas/`.
- **Quem lê:** `regras/cadencia_da_referencia.mjs` — `devidaHoje` `:72`, `planoDaRotacao` `:132`, `filtrarPorCadencia` `:163`.
- **Quem aplica:** `coleta/italy_recurrent_collect.mjs:246-268` (passo 6c', filtro aplicado em `:265`), **depois** do portão e do contrato, antes do
  coletor. Tira do dia quem não é devida, com o porquê (`FORA_DA_CADENCIA`, `ALERTAS_DE_CADENCIA` no log); **nunca
  acrescenta** fonte. Quem não declara cadência continua diária. A última checagem vem do dono dela (D, abaixo).
- **Declarado NÃO LIGADO** (nos contratos): executor das bulas (`coleta/rotulos_baixar.py` baixa sem robots e sem teto
  24 h) e do catálogo (exige navegador/WAF). Ligar é decisão pendente.

## C · O diff das edições e o EVENTO_REGULATORIO

`coleta/it/edicoes_do_registro.py` — `comparar` `:248`, `guardar_diff` `:301`, `edicoes_do_livro` `:321`,
`item_do_evento` `:353`, `emitir` `:396`. Aplica a régua que **já existia** (`docs/regras/REGUA-DE-CHANGE-EVENT-EAME.md`:
vocabulário, campos, portão de versão `medidas/source_health.py::version_state`). Cada mudança traz
`NUMERO_REGISTRAZIONE · CAMPO · ANTES · DEPOIS · EDICAO` (e os nomes da régua ao lado). Revogação =
`stato_amministrativo` → `STATUS_CHANGE/REVOGACAO` datada por `data_decreto_revoca` da linha; **sair do ficheiro não é
revogação** (`REGISTRATION_LEFT_THE_LIST`, `UNRESOLVED`); grafia só = `UNKNOWN_CHANGE`, sem evento. Emissão pelo
caminho canônico: `admissao.decidir(item,"T4")` → `pronto_para_inteligencia` → `sala_de_espera.pousar` (run id
determinístico `IT-T4-DIFF-<A>-<B>`, retry = `JA_ESTAVA`).

**Achado medido:** com o nome do produto na 1.ª linha do texto, a porta lia **cultura «vite»** de `RAME VITE`
(`admissao._cultura_fora_da_regua` lê o título). Corrigido do lado do evento (`:360-371`): valores só da 2.ª linha
para baixo. Os 8 READY da fixture saem com `CULTURA = NAO SEI`.

Real, nesta árvore: o livro conhece a edição `20260914`, mas os bytes dela não estão aqui → a CLI diz **NAO SEI** e
não compara (só `20260907` tem bytes).

## D · Frescor

`leis/frescor_da_referencia.py::estado_frescor` `:77` (pura) e `checagens_do_livro` `:125`; CLI `--json` para a
Intelligence / Label Intelligence e para o corredor. `EDICAO_DATA · ULTIMA_CHECAGEM_OK · ESTADO_FRESCOR ·
AUTORIZACOES`; <14 `EM_DIA`, ≥14 `PODE_ESTAR_DESATUALIZADO`, ≥30 autorizações `A_CONFIRMAR`, sem checagem `NAO_SEI`;
conta **desde a checagem** (HEALTHY, inclui SEEN_AGAIN). Hoje: IT-T4-001 `EM_DIA` (edição 14/09, checagem 18/09).

## E · F

- `COMANDO-HOJE.md`: comando exato (egresso → portão → orquestrador), 3 idas HTTP medidas no código (robots + página +
  CSV) dentro do teto; **avisa que hoje o portão o recusa**.
- `docs/propostas/PATCH-BIBLIAS-REFERENCIA-D116-D117.patch` (**não aplicado**, `git apply --check` OK): COL-LAW-407
  (Coleta) e INT-LAW-285 (Intelligence). Aplicar exige COL-LAW-069 (diário + VERSION + `docs/biblia/leis.json`).

## Testes, mutação, mapa

- **Bateria inteira por nome** (`provas/integra_noite/bateria_inteira_por_nome.py`, 3 workers, rede cortada), base `18461b9` × ramo `bdf86ab`:

| | base | ramo |
|---|---|---|
| ficheiros de teste | 393 | 396 (+3 desta missão) |
| testes corridos | 7.373 | 7.404 |
| ficheiros vermelhos | 77 | 77 |
| falhas por nome | 338 | 338 |

  **Comparadas pelo nome (system-map sem os números): 337 = 337 · 0 NOVAS · 0 consertadas.** `regras/italy_contract_test.mjs` continua com as mesmas 82 falhas herdadas da base (conferidas uma a uma pelo nome).

- Novos: `tests/test_edicoes_do_registro.py` 20/20 · `tests/test_frescor_da_referencia.py` 11/11 ·
  `regras/cadencia_da_referencia_test.mjs` 35/35. Nenhum teste existente foi alterado.
- **Mutação** `provas/mutacao_referencia_manutencao.py`: **16/16 mortos** (S1-S2 sobrescrever, C1-C2 inventar
  cultura, R1-R3 pular/fingir revogação, F1-F4 frescor, K1-K5 cadência). K5 (o corredor calcula a cadência e deita o
  resultado fora) **sobreviveu** na 1.ª volta → guarda nova no teste.
- Mapa: `correr_a_cadeia.py REGERAR` → `VALIDAR` = **SYSTEM_MAP_CHECK=PASS**; `--conferir-carimbo` = **IGUAL**. 4 peças
  novas declaradas; **sem `--stamp`** (carimbaria como lido tudo o que ninguém releu) — ficam 🟡 até leitura humana.
- Dependências: PyYAML e Node 22 presentes; nada contornado.

## EM PALAVRAS SIMPLES

O registro oficial italiano dos defensivos parou de ser colhido depois de 18/09 porque **ninguém nunca o agendou**:
a agenda automática nunca o teve na lista, esteve quebrada até 22/09, e desde então o porteiro da coleta o recusa
(foi aprovado por uma régua antiga). Agora o contrato da fonte diz **quando** voltar (toda terça, tentando de novo
quarta e quinta, com alarme se falhar), a agenda obedece a isso, há um comparador que pega duas edições e diz produto
a produto o que mudou (registro novo, revogação com a data do decreto, troca de titular, de substância, de
vencimento) e manda cada mudança para a Sala pela porta de sempre, sem nunca inventar cultura, e há uma régua simples
que diz se a informação está fresca (14 dias sem olhar = pode estar velha; 30 = autorizações a confirmar). **Falta uma
decisão do dono**: liberar o registro no porteiro. Sem ela, o comando de hoje para no porteiro — como deve.

**HARD STOP.**
