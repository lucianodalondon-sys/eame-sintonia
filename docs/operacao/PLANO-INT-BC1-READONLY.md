# PLANO — C-INT-BC1-READONLY (fase 1 = PREPARAR)

> **Estado: PLANO. Nada foi executado.** Nenhuma leitura da Sala, nenhum banco aberto,
> nenhum motor corrido, nenhuma suite. A fase 2 só começa quando o COORDENADOR disser:
> 1.ª onda fechada, volumes reconciliados, delta READY admitido e máquina livre.

| campo | valor |
|---|---|
| missão | `C-INT-BC1-READONLY` — decidida pelo bot Luciano (delegação do dono), 24/09 ~08:20 |
| árvore | `intelligence-bc1-v1` a partir de `origin/unificacao-v1` @ `98ec8fbf` (a linha instalada) |
| rodada anterior | `C-INT-PILOT-SALA-V2` — `claude/int-pilot-sala-v1` @ `d51ea98a` (20/09): Sala 46, 17 novos, 1 utilizável, 0 crossings |
| lei | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` — INT-LAW-010, 012, 014, 020, 037, 053, 054, 070–077, 091, 095 |
| coorte | `C:\bc\COORTE-BIG-COLLECTION.json` — `COORTE-BIG-COLLECTION-V1`, CONGELADA em 2026-09-24T03:29:47Z (árvore `8eec2e2a`), 18 fontes |

---

## 0 · A RESPOSTA ANTES DA EXECUÇÃO (declarada agora, para não ser escolhida depois)

A coorte tem **0 fontes IT-T3** (T10 = 3, T2 = 2, T5 = 1, T7 = 12). O único leitor da Sala
que existe (`o_piloto_da_sala.py`, PIPELINE_VERSION 2) só tenta crossing e só espera `CROP`
em `IT-T3`. Logo, **por construção e antes de ver um único item**:

| grandeza | valor esperado | porquê |
|---|---|---|
| `CROSSINGS_TENTADOS` | **0** | `FAMILIAS_AGRO = ("IT-T3",)`; nenhuma fonte da onda é T3 |
| `ITEMS_EXPECTING_CROP` | **0** | `FAMILIAS_QUE_ESPERAM_CROP = ("IT-T3",)` |
| `OPPORTUNITY_CANDIDATES` | **0** | nenhum crossing fecha join key |
| resultado | **`NO_DEFENSIBLE_ACTION_YET`** | INT-LAW-012: é sucesso, não falha |
| G0 do `INTELLIGENCE_RUN` | provavelmente **`BLOQUEADO_EM_G0`** em todos | na R2, `FACT_TIME = NAO SEI` em 46/46; o G0 exige `FACT_TIME` |

⚠️ **Se a fase 2 der um número diferente destes, isso é um achado a medir, não uma boa
notícia a publicar.** Um crossing > 0 sem T3 indicaria que a régua mudou, não que a onda
trouxe inteligência.

Sem T3 também quer dizer, por ordem: **nada de diagnóstico agronómico, risco de cultura ou
recomendação técnica** — nem que um texto T10/T7 fale de doença ou produto.

---

## 1 · A ENTRADA — só o delta READY da 1.ª onda, por identidade

```text
DELTA_BC1 = { (RUN_ID, ORDEM) em public.sala_de_espera
              cujo RUN_ID pertence às corridas da 1.ª onda }
```

- **Chave:** `(RUN_ID, ORDEM)` — a que a migration 031 declara como endereço da linha.
  `ITEM_ID` não serve (duas fontes podem dar o mesmo nome). Data não serve (filtro ≠ checkpoint).
- **A Sala anterior entra só como contexto de redundância** (md5 do texto contra o que já lá
  estava). Não é reanalisada, não é reclassificada, não entra no censo.
- **Fonte dos RUN_ID da onda:** o relatório da corrida (`C:\bc\corrida`, runbook passo 5) —
  lido, não inferido. Conferência cruzada: `SALA_AFTER − SALA_BEFORE` do runbook (passos 3 e 7)
  tem de bater com `|DELTA_BC1|`. Se não bater → **PARAR e medir** antes de analisar.
- Cada item do delta tem de ter a `SOURCE_ID` numa das 18 da coorte. Item de fonte fora da
  coorte → registado como anomalia de volume, **não analisado**.

### 1.1 · O que a verificação estática encontrou sobre o checkpoint (sem executar)

**V1 — o leitor não está na linha instalada.** `provas/o_piloto_da_sala.py` e os dois artefatos
(`data/derivados/O-PILOTO-DA-SALA.json`, `…-R2-DELTA.json`) só existem em
`claude/int-pilot-sala-v1` (e `crop-e2e-v1`). `origin/unificacao-v1` não os tem. Na fase 2 são
trazidos **sem alteração** (`git checkout d51ea98a -- <3 ficheiros>`), com a peça do System
Map. Não é motor novo: é o mesmo ficheiro, a mesma versão.
As duas referências que ele lê (`data/samples/IT-T4-001/IT-T4-001-adama-portfolio.json`,
`referencia/adama/AUTHORIZED-USES.json`) têm o **mesmo blob** nas duas linhas
(`47b81dda…`, `0e6cc777…`) — a régua de referência não mudou.

**V2 — o artefato da R2 NÃO serve sozinho como checkpoint.** O `CENSO` de cada artefato só
guarda os itens **daquela** rodada: R1 = 29, R2 = 17. `--desde-artefato` aceita **um** ficheiro
e subtrai só o `CENSO` dele. Passar só o da R2 faria o piloto tratar os 29 da R1 como novos —
exactamente a «Sala inteira reanalisada» que a missão proíbe.

**V3 — o checkpoint por artefato dá «tudo o que ainda não processei», não «a 1.ª onda».**
A Sala passou de 46 (R2, 20/09) para 66 antes da onda (BC2 tardia, micros BC4c/BC4d; C4 PASS
64 → 66 às 07:19). Esses ~20 itens **nunca foram processados** pela Intelligence e **não são
da onda**. Se entrassem, o delta misturaria duas coisas.

**Consequência — o checkpoint da fase 2 é um ficheiro montado, não um artefato antigo:**

```text
CHECKPOINT_BC1.json = {
  "PIPELINE_VERSION": "2",
  "CENSO": [ (RUN_ID, ORDEM) de TODA a Sala anterior à onda ]
}
   onde «Sala anterior à onda» = linhas da Sala cujo RUN_ID NÃO está na lista da onda
   conferido: |CENSO| == SALA_BEFORE (passo 3 do runbook)
```

Assim `--desde-artefato CHECKPOINT_BC1.json` devolve exactamente `DELTA_BC1`, e o cálculo de
redundância do piloto (que compara o delta com o resto da Sala) continua certo. Os ~20
pré-onda não processados ficam **declarados como dívida** (`NAO_PROCESSADOS_PRE_BC1`), não
analisados à boleia.

**V4 — idempotência `(RUN_ID, ORDEM) + PIPELINE_VERSION`: serve, com uma condição.** Mesma
versão → subtrai o checkpoint; versão diferente → reprocessa **tudo** (e avisa em stderr).
Condição: **ninguém sobe `PIPELINE_VERSION` antes da fase 2.** Se subir, a corrida
reanalisaria a Sala inteira — proibido. A fase 2 confere `PIPELINE_VERSION == "2"` antes de
correr, e aborta se não for.

**V5 — a ligação à Sala é read-only POR CÓDIGO, não POR BANCO.** O piloto só emite dois
`select` via `psql -f -` (opções antes da DSN, DSN nunca ecoada). Mas a DSN é a do dono da
Sala, que pode escrever. Na fase 2 a sessão é forçada a só-leitura **sem mudar código**:

```text
PGOPTIONS="-c default_transaction_read_only=on"
```

e a prova de que nada mudou é a fotografia `SALA_AFTER` do runbook repetida **depois** da
Intelligence: as 5 contagens iguais (`sala_de_espera`, `raw_asset`, `storage_object`,
`derived_artifact`, `collection_run`). Qualquer diferença → PARAR.

**V6 — `motor/corrida_da_inteligencia.py` (o `INTELLIGENCE_RUN` mínimo) não abre a Sala**, e
é de propósito. Recebe os itens num ficheiro. As chaves que ele lê (`ITEM_ID`, `SOURCE_ID`,
`RAW_OBSERVATION_ID`, `FACT_TIME`, `UNIVERSO`) estão no `CENSO` do piloto; `CORRIDA` não
está (o piloto chama-lhe `RUN_ID`). Na entrada do motor, `CORRIDA := RUN_ID` é **renomear**,
declarado no manifesto — não é cunhar identidade.

**V7 — o que NÃO se corre:** `motor/cadeia_canonica.sh` (aplica migrations e `insert`s num
banco), `motor/v21_cadeia.sh` (recusa-se nesta linhagem; é o pacote V2.1 do Portal, não lê
a Sala). A «cadeia V2.1» não é leitor da Sala e não entra nesta missão.

---

## 2 · A EXECUÇÃO (fase 2 — NÃO começar sem ordem)

| # | passo | escreve em | lê |
|---|---|---|---|
| 0 | conferir: ordem do coordenador; bot/coletor parados; RAM livre; `PIPELINE_VERSION == "2"` | — | — |
| 1 | trazer o piloto e os 2 artefatos de `d51ea98a` sem alteração; peça no System Map | árvore | git |
| 2 | ler a lista de RUN_ID da onda do relatório da corrida; conferir contra a coorte (18) | `data/derivados/BC1/` | `C:\bc\corrida` |
| 3 | fotografia `SALA_ANTES_INT` (5 contagens) | `data/derivados/BC1/` | Sala, só-leitura |
| 4 | montar `CHECKPOINT_BC1.json`; conferir `|CENSO| == SALA_BEFORE` | `data/derivados/BC1/` | Sala, só-leitura |
| 5 | `py provas/o_piloto_da_sala.py --dsn … --desde-artefato CHECKPOINT_BC1.json --json data/derivados/BC1/PILOTO-BC1-DELTA.json` com `PGOPTIONS` só-leitura | `data/derivados/BC1/` | Sala, só-leitura; `referencia/adama/` |
| 6 | conferir `|CENSO do artefato| == |DELTA_BC1|` e `PROCESSADOS_QUE_SUMIRAM_DA_SALA == []` | — | — |
| 7 | `INTELLIGENCE_RUN`: `motor/corrida_da_inteligencia.py` sobre o `CENSO` do delta (com `CORRIDA := RUN_ID`); gravar o livro | `data/derivados/BC1/` | ficheiro |
| 8 | fotografia `SALA_DEPOIS_INT` — tem de ser **igual** à do passo 3 | `data/derivados/BC1/` | Sala, só-leitura |
| 9 | relatório + métricas + pedidos de gap; know-how; mapa; commit + push | árvore | — |

Nenhum passo escreve na Sala, na Admission, no READY, nos livros das fontes ou na Collection.
Nenhum passo chama coletor ou abre rede externa. Uma só medição de cada vez (a máquina é
partilhada; duas medições ao mesmo tempo mentem).

---

## 3 · AS 5 PERGUNTAS FECHADAS — o que responde cada uma e como

| # | pergunta | como se mede | o que NÃO se faz |
|---|---|---|---|
| 1 | **O que é realmente novo?** | `DELTA_BC1` por `(RUN_ID, ORDEM)`; depois `DELTA_REDUNDANTE_VS_SALA` (md5 do texto contra a Sala anterior). NOVO NA FILA ≠ NOVO COMO EVIDÊNCIA | contar item em dobro como dois; chamar «novo» a re-observação |
| 2 | **Fontes independentes que se apoiam/contradizem?** | grafo de dependência primeiro (INT-LAW-070): mesmo md5 = uma observação; mesmo originador (ex.: 5 `cia.it`/`caf-cia.it` = **uma família CIA**, INT-LAW-071) não multiplica fontes. SUPPORT/CONTRADICTION só entre claims com a **mesma** pergunta, tempo e lugar compatíveis — com `FACT_TIME`/`FACT_LOCATION` = `NAO SEI`, o estado é `UNKNOWN`, não «apoia» | declarar apoio por palavra comum; contar 5 páginas da CIA como 5 fontes |
| 3 | **Crossings possíveis com tempo, território e chaves provadas?** | `CROSSINGS_TENTADOS / POSSIVEIS / BLOQUEADOS`, cada bloqueio com `JOIN_KEYS_MISSING` (INT-LAW-091). Esperado: 0 tentados (sem T3). Se alguém quiser T2-clima × cultura: bloqueado por falta de `CROP` e de `FACT_LOCATION`; registar como `NOT_POSSIBLE`, não tentar | ler cultura/região do corpo do texto para fechar a chave; correlação virar causa (INT-LAW-095) |
| 4 | **Algum finding/oportunidade passa todos os gates?** | contagem de `FINDINGS` e `OPPORTUNITY_CANDIDATES` depois de G0 + crossing. Resposta esperada: **`NO_DEFENSIBLE_ACTION_YET`** | relaxar gate; procurar «cards» até achar (INT-LAW-014) |
| 5 | **Que lacunas voltam à Collection?** | `REQUIREMENT_ID` do motor (G0) + os GAP da R2 re-medidos no delta (`FACT_TIME`, `FACT_LOCATION`, `EVIDENCE_CLASS`, `CROP`, ausência de T3). Saem como `COLLECTION_GAP_REQUEST` **escritos**, não despachados (INT-LAW-020) | chamar coletor; escolher rota ou executor |

---

## 4 · MÉTRICAS (todas com denominador, e `NAO SEI` contado — nunca preenchido)

| métrica | forma |
|---|---|
| entradas por tipo | `ESTAGIO` × n / `|DELTA_BC1|` |
| entradas por idioma | idioma **declarado** pelo item; sem campo → `NAO SEI` (não detectar a idioma para o preencher) |
| entradas por fonte | `SOURCE_ID` × n, e por família de originador (CIA, ARPA, ISTAT, …) |
| novidade / redundância | novos por identidade; redundantes por md5 vs Sala anterior; redundantes dentro do delta |
| independência | textos distintos; originadores distintos; `INDEPENDENT_SOURCE_COUNT` separado de `EXTERNAL_SIGNAL_COUNT` (INT-LAW-092) |
| suporte / contradição | pares avaliados / pares com chave compatível / `UNKNOWN` |
| crossings | tentados / possíveis / bloqueados (com a chave em falta) |
| `UNKNOWN` | `FACT_TIME`, `FACT_LOCATION`, `EVIDENCE_CLASS`, idioma: n com `NAO SEI` / total |
| classe | `USABLE` / `WEAK` / `INSUFFICIENT` (régua da v2, limiares 20/5 **inalterados**) |
| findings | n (esperado 0) |
| oportunidades defensáveis | n (esperado 0) |
| gaps | n de `REQUIREMENT_ID` e de `COLLECTION_GAP_REQUEST`, por campo em falta |
| estados | `NOT_RUN` / `ERROR` / `EMPTY_RESULT` / `NO_FINDING` separados (INT-LAW-053) |

---

## 5 · ENTREGAS (fase 2)

Tudo em `data/derivados/BC1/` e `docs/operacao/INT-BC1-RELATORIO.md`:

1. **Manifesto do `INTELLIGENCE_RUN`** — o livro do motor (`INTELLIGENCE_RUN_ID`, `REQUEST_ID`,
   `RULESET_VERSION`, `CODE_VERSION`, `PIPELINE_VERSION` do piloto, HEAD, `RESULT_STATE`).
2. **Inventário do delta** — `(RUN_ID, ORDEM, SOURCE_ID, RAW_OBSERVATION_ID, ESTAGIO)` de cada item.
3. **Proveniência** — cada item até `RAW_OBSERVATION_ID` e `RUN_ID`; o checkpoint e a lista de
   RUN_ID da onda, com o sha256 de onde vieram.
4. **Métricas** — a tabela da secção 4.
5. **Findings** — incluindo `NO_DEFENSIBLE_ACTION_YET`, com o porquê.
6. **Pedidos de gap** — `COLLECTION_GAP_REQUEST` escritos, não despachados.
7. **Prova de só-leitura** — `SALA_ANTES_INT` == `SALA_DEPOIS_INT`.

---

## 6 · RISCOS

| risco | efeito | defesa |
|---|---|---|
| checkpoint só da R2 | reanalisa os 29 da R1 | checkpoint montado (V2/V3) + conferência de contagem |
| pré-onda misturado no delta | «1.ª onda» mede outra coisa | filtro por RUN_ID da onda; os ~20 ficam como dívida declarada |
| `PIPELINE_VERSION` mexida antes da fase 2 | reprocessa a Sala inteira | aborta se ≠ "2" |
| DSN com escrita | escrita acidental | `PGOPTIONS` só-leitura + fotografia antes/depois |
| duplicados na Sala (`SALA_ITENS_JA_NA_SALA_POR_OUTRA_CORRIDA`, runbook §7) | contar a mesma observação duas vezes | redundância por md5 vs Sala anterior **e** dentro do delta |
| a CIA pesa 6 de 18 fontes (`cia.it` ×5, `caf-cia.it`, `ciatoscana.eu`) | «convergência» que é uma só voz | família por originador antes de qualquer contagem de apoio |
| `IT-T10-022` (Zootecnica International, avicultura) | material de saúde/produção animal | contado e classificado, **não analisado** como tema (veterinária está fora do foco por decisão do dono de 23/09) |
| régua de densidade agro em italiano | T10 em inglês (Zootecnica) cai em `INSUFFICIENT` pela língua, não pelo conteúdo | declarar a limitação por item; não mudar a régua a meio (isso muda a versão) |
| RAM (suite da BC5 + coleta) | medição truncada ou morta a meio | só com ordem do coordenador e máquina livre |
| volumes da onda não reconciliados | delta errado | só corre depois de o coordenador dizer «reconciliados» |

---

## 7 · O QUE FOI VERIFICADO NESTA FASE (sem executar)

- base da árvore = `origin/unificacao-v1` @ `98ec8fbf` (conferido por `git rev-parse`);
  `origin/bc4-correcoes-v1` @ `f48ed6ed` leva a BC4b–BC4d por cima;
- leitura do código do piloto em `d51ea98a` (checkpoint, versão, só `select`, DSN nunca ecoada);
- `CENSO` do artefato R1 = 29, R2 = 17, `PIPELINE_VERSION` R2 = "2", R1 sem versão;
- referências ADAMA com o mesmo blob nas duas linhas;
- motor `corrida_da_inteligencia.py`: não abre a Sala; G0 exige `ITEM_ID`, `SOURCE_ID`,
  `FACT_TIME`, `RAW_OBSERVATION_ID`;
- coorte: 18 fontes, 0 T3, 0 duplicadas, 19 fora;
- Bíblia: INT-LAW-010/012/014/020/053/054/091 lidas no texto.

**Não verificado:** o conteúdo real da Sala hoje (proibido nesta fase); os RUN_ID reais da onda
(ainda não existem); se o `FACT_TIME` continua `NAO SEI` nos itens novos (é a expectativa, não
um facto medido).
