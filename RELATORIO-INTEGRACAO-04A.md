# RELATÓRIO — INTEGRAÇÃO 04A: AS 18 FONTES HTML READY DO SOURCE CURATOR

```
BANCADA      curator-04a-integration
BASE         claude/contract-provenance-cutover-v1 @ 370ce450   (INITIAL_HEAD, medido)
FONTE        claude/bot-de-fontes-v2-plano @ 376c0d9b           (SOURCE_CURATOR_HEAD_USED, medido)
DATA         2026-09-20
MODEL        claude-fable-5-1
```

**Git venceu o briefing em tudo o que foi confirmado.** Cada `MEDIDO` da secção 0 da
missão foi reconfirmado antes de agir; as diferenças encontradas estão em §1.

    INTEGRAR FONTE != COLETAR FONTE.  Nenhuma coleta correu. Nenhum RUN, RAW,
    Admission ou Sala foi tocado. NETWORK_REQUESTS = 0. PAID_USD = 0.

---

## 1 · O QUE CONFIRMEI DA SECÇÃO 0 (e onde o número era outro)

| Medição do coordenador | Reconfirmado | Nota |
|---|---|---|
| curator = 376c0d9b · coordinator = 370ce450 · merge-base = 606974c3 (= it-trunk-v1) | ✅ igual | |
| curator +6 / 0 · coordinator +25 / 0 sobre it-trunk-v1 | ✅ igual | |
| intersecção de ficheiros vazia (39 vs 57) | ✅ igual | |
| coordinator não tocou o Atlas desde a base | ✅ igual | Atlas do coordinator é **prefixo exacto** do Atlas do curator |
| nenhuma outra branch tem `curadoria/`; nenhuma liga o JSON do curator a `regras/` | ✅ igual | varridas **279** branches remotas, não 80 |
| 77 fontes · 18 READY · 50 BLOCKED · 9 CANARY_FAILED · robots 77/77 · ALLOWED 27 / DISALLOWED 50 | ✅ igual | lido do JSON, não do markdown |
| 18 SOURCE_ID distintos · 0 colisões com onboarded (105) · 0 com os 77 | ✅ igual | **mais:** 0 colisões dos 84 com `ITALY-SOURCE-MASTER-V1.json` (54 IDs), que o coordenador não tinha medido |
| Atlas: curator 268 · coordinator 184 · novas 84 | ≈ | contei linhas `SOURCE_ID:`: **269 / 185**; a diferença de 84 é igual. A linha extra é o modelo de ficha em branco do preâmbulo |
| motor tem `HTML_LINK_DISCOVERY`, valida INDEX_URL/LINK_PATTERN (l. 182-184) | ✅ igual | as 18 passam `conferirAquisicao()` e `conferirIdentidade()` no motor real (18/18) |
| `YOUTUBE_CHANNEL_FEED` não existe em regras/coleta | ✅ igual | e `contratoGenerico()` rebenta numa linha YouTube: `OUTPUT_TYPE desconhecido … VIDEO_METADATA` (50/50 rejeitadas) |
| evidência fora do Git, 131 pastas em `C:/bot-fontes-v2/curadoria/evidencia/` | ✅ igual | os 18 exemplos canónicos existem e o **sha256 bate 18/18** com `REAL-EXAMPLE-MANIFEST-V1.json` |

**Contra-exemplo procurado (o que inverteria o achado do motor):** campo que
`contratoGenerico()` exija e as linhas do curator não tragam. Não existe:
exige `OUTPUT_TYPE ∈ {PDF, HTML}`, `ACQUISITION.STRATEGY`, `INDEX_URL`; as 18
trazem os três e mais 23 chaves. A IDENTITY do curator é byte a byte a que
`contratoGenerico()` produz. **As 18 são executáveis pela rota canónica.**

---

## 2 · PROVA PRÉ-INTEGRAÇÃO — as 18, uma a uma

| SOURCE_ID | CANDIDATE_ID | SOURCE_NAME | ENDPOINT (INDEX_URL) | CONTRACT (hash) | CADENCE | CANARY_RESULT | ROBOTS_GATE | DOCUMENT_ID do canário |
|---|---|---|---|---|---|---|---|---|
| IT-T5-039 | CAND-0020 | UNINA Dipartimento di Agraria — Portici | https://www.agraria.unina.it/ | 98af78f5036924c3 | MONTHLY_PROBE | PASS (HTTP 200) | ALLOWED | IT-T5-039:URL:avvisi/bacheca-laureati/esami-di-stato1 |
| IT-T7-017 | CAND-0138 | Cantina Sociale Cooperativa Riunite e CIV | https://www.riuniteciv.com/ | 2f38525b6251be8a | MONTHLY | PASS (HTTP 200) | ALLOWED | IT-T7-017:URL:news-e-eventi/cantine-maschio-e-maratona-dles-dolomites-sedici-anni-sulla-stessa-strada |
| IT-T7-021 | CAND-0155 | Consorzio di Bonifica Est Ticino Villoresi | https://www.etvilloresi.it/ | 2cebb9be67f9ed32 | MONTHLY_PROBE | PASS (HTTP 200) | ALLOWED | IT-T7-021:URL:attivita/progetti/progetto-la-via-del-marmo |
| IT-T12-009 | CAND-0007 | ASSAM Marche — Agenzia Servizi Settore Agroalimentare delle Marche | https://www.assam.marche.it/ | 1da23405d1e61c51 | MONTHLY | PASS (HTTP 200) | ALLOWED | IT-T12-009:URL:progetti-europei/progetti-europei-conclusi |
| IT-T7-031 | CAND-0165 | FederBio | https://feder.bio/ | 9c8c20330b7e877d | MONTHLY | PASS (HTTP 200) | ALLOWED | IT-T7-031:URL:progetti/being-organic-eu-choose-the-european-organic-leaf-for-better-world |
| IT-T10-018 | CAND-0059 | Myfruit.it | https://www.myfruit.it/ | 1fa48b7d8a93f07c | MONTHLY_PROBE | PASS (HTTP 200) | ALLOWED | IT-T10-018:URL:news/annamaria-medici-in-ortofrutta-vince-il-valore-percepito |
| IT-T12-013 | CAND-0011 | Regione Piemonte — Agricoltura e cibo | https://www.regione.piemonte.it/web/temi/agricoltura | 4b7ff0fce14fbda4 | MONTHLY | PASS (HTTP 200) | ALLOWED | IT-T12-013:URL:governo/bollettino/abbonati/2026/corrente |
| IT-T5-049 | CAND-0024 | UNICT Di3A — Dipartimento di Agricoltura Alimentazione e Ambiente | https://www.di3a.unict.it/ | c26b2c56287df546 | DAILY | PASS (HTTP 200) | ALLOWED | IT-T5-049:URL:it/notizie/avvisi-esami-e-prove-itinere |
| IT-T7-033 | CAND-0174 | Consorzio Vino Chianti Classico | https://www.chianticlassico.com/ | f2c2b3cb791b6419 | MONTHLY | PASS (HTTP 200) | ALLOWED | IT-T7-033:URL:news/addio-al-marchese-vittorio-frescobaldi-imprenditore-illuminato-del-vino-italiano |
| IT-T10-020 | CAND-0065 | WineNews | https://winenews.it/ | 6d7e53ac53a52d84 | MONTHLY_PROBE | PASS (HTTP 200) | ALLOWED | IT-T10-020:URL:it/rassegna-stampa/dicono-di-noi |
| IT-T10-021 | CAND-0004 | Plantgest — banca dati varieta | https://plantgest.imagelinenetwork.com/ | 90882cb24279da72 | MONTHLY_PROBE | PASS (HTTP 200) | ALLOWED | IT-T10-021:URL:it/eventi/giornate-tecniche-sul-noce-da-frutto/63565 |
| IT-T8-008 | CAND-0054 | Agroalimentare News | https://www.agroalimentarenews.com/ | 0d1f1d5b3e99bca1 | MONTHLY | PASS (HTTP 200) | ALLOWED | IT-T8-008:URL:notizie/agroalimentarenews/gli-imprenditori-del-gusto |
| IT-T10-022 | CAND-0066 | Zootecnica International | https://www.zootecnicainternational.com/ | 4ab009162dcbe5df | MONTHLY | PASS (HTTP 200) | ALLOWED | IT-T10-022:URL:news/newcastle-disease-hungary-broiler-farms |
| IT-T7-040 | CAND-0141 | Consorzio del Parmigiano Reggiano | https://www.parmigianoreggiano.it/ | dec5341f40347274 | MONTHLY_PROBE | PASS (HTTP 200) | ALLOWED | IT-T7-040:URL:it/news/console-usa-benning |
| IT-T7-041 | CAND-0142 | Consorzio di Bonifica della Romagna | https://www.bonificaromagna.it/ | c564c2ead02ed884 | MONTHLY | PASS (HTTP 200) | ALLOWED | IT-T7-041:URL:news/notte-delle-bonifiche-tricolore-un-segno-di-pace-dalla-romagna |
| IT-T7-042 | CAND-0143 | Consorzio di Tutela dell'Aceto Balsamico di Modena | https://www.consorziobalsamico.it/ | 6034cc60ef7d77fd | WEEKLY | PASS (HTTP 200) | ALLOWED | IT-T7-042:URL:news-blog/a-sostegno-della-filiera-del-vino-italiano |
| IT-T2-030 | CAND-0147 | Nomisma | https://www.nomisma.it/ | 2848c30b3ece121c | WEEKLY | PASS (HTTP 200) | ALLOWED | IT-T2-030:URL:eventi/aidea-forum-varignana-nomisma-confindustria-intelligenza-artificiale-imprese |
| IT-T7-043 | CAND-0161 | Agrofarma — Federchimica | https://agrofarma.federchimica.it/ | 9b4bcb530d6f906f | MONTHLY_PROBE | PASS (HTTP 200) | ALLOWED | IT-T7-043:URL:news-ed-eventi/dettaglio-news/2026/06/07/osservatorio-agrofarma-innovazione-e-bio-ridisegnano-lagricoltura-italiana |

| SOURCE_ID | CONTRACT_VALID | ROUTE_ALLOWED | ROBOTS_GATE | CANARY_PASS | SOURCE_ID_PRESENT | IDENTITY_RESOLVED | ENTRA |
|---|---|---|---|---|---|---|---|
| IT-T5-039 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T7-017 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T7-021 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T12-009 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T7-031 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T10-018 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T12-013 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T5-049 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T7-033 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T10-020 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T10-021 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T8-008 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T10-022 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T7-040 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T7-041 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T7-042 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T2-030 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |
| IT-T7-043 | PASS | PASS | PASS | PASS | PASS | PASS | SIM |

TODAS_VERDES = True | n = 18

`TODAS_VERDES = True · n = 18`. Nenhuma fonte virou READY porque o HTTP respondeu:
o canário exige entrada 200, alvo descoberto pelo LINK_PATTERN, alvo ≠ entrada, alvo
200 e primeiro byte `<`; o gate de robots leu o `robots.txt` vivo de cada host.

---

## 3 · DECISÕES, COM A RAZÃO MEDIDA

### 3.1 Contratos — caminho (1): as 18 linhas entram em `italy_contracts_onboarded.json`

Escolhido o caminho **1**. Razões:

- **Uma tabela, um dono.** `regras/italy_contracts.mjs` já lê a tabela por
  `readFileSync` e expande com `contratoGenerico()`. Um segundo ficheiro seria uma
  segunda autoridade com um filtro por estado que alguém um dia esquece.
- **A forma não era "a mesma".** As linhas do curator têm 26 chaves; a tabela tem 9. E
  50 linhas com `STRATEGY = YOUTUBE_CHANNEL_FEED` / `OUTPUT_TYPE = VIDEO_METADATA`
  rebentam no carregador. Um `readFileSync` do ficheiro inteiro nem carregava.
- **Tradução, não invenção.** `SONDAGEM.ENTRADA_STATUS = 200` é medido (o canário exige
  200 na entrada para prosseguir); `ENTRADA_BYTES` não foi gravado → `NAO SEI`.
  `CARACTERIZACAO` chega inteira, com os `NAO SEI` e `UNKNOWN` que a curadoria escreveu.
- **Proveniência verdadeira.** `contratoGenerico()` escrevia `ONBOARDED_BY` fixo
  («sondagem 2026-09-18»). Passou a ler `linha.ONBOARDED_BY || <o texto antigo>`, e a
  passar `CARACTERIZACAO` e `CURADORIA`. 13 linhas no dono, 0 mudança para as 105.
- **Prova de que o motor não alcança as 50:** `tests/test_integracao_04a_curator.py`
  (17 testes). Posto à prova com três tabelas adulteradas — uma linha YouTube dentro,
  uma das 18 a menos, estratégia trocada — **3/3 reprovaram** (3 testes cada); a tabela
  real passa 7/7. O ficheiro da curadoria fica como registo; um teste reprova se
  `italy_contracts.mjs`, `motor_de_rota.mjs` ou `coleta/*` passarem a lê-lo.

Resultado no dono: `CONTRACT_IDS 118 → 136 · ONBOARDED_IDS 105 → 123`; 123/123 passam
`conferirAquisicao` + `conferirIdentidade`.

### 3.2 Atlas — as **84** fichas entram, cada uma com `ESTADO_04A:` medido

Argumentos medidos de cada lado:

| Só as 18 | As 84 |
|---|---|
| ✅ zero fichas a afirmar rota que o gate reprovou | ⚠️ as 50 dizem `ACCESS_METHOD: RSS … feeds/videos.xml` e `AUTOMATION_FEASIBILITY: HIGH — rota pública … já provada` (escritas ANTES do gate 04A; o commit do gate não tocou o Atlas) |
| ❌ **66 SOURCE_ID alocados ficam fora do trunk**: a alocação seguinte no trunk lê o Atlas para «o próximo número» e escolheria um número já dado — exactamente a colisão de `test_o_atlas_nao_colide_com_os_ids_cunhados_fora_dele` | ✅ identidade inteira no registo canónico; `MESMA_ORGANIZACAO` preservado (canal ≠ site, COL-LAW-034) |
| ❌ parte a unidade que o curator escreveu (o bloco `## ONDA SOURCE CURATOR`) | ✅ o bloco é só acrescento: **3050 linhas +, 0 −** |

Regra que mandou: *o Atlas regista fontes conhecidas; a tabela regista fontes que a casa
sabe buscar.* Entram as 84 no Atlas e as 18 na tabela. Para não deixar a afirmação
pré-gate sozinha, **cada ficha ganhou uma linha `ESTADO_04A:`** copiada do veredito
do curator (`READY-FOR-COLLECTION-V1.json` / `SEM_CONTRATO`), com data — a ficha
original não foi reescrita:

```
ESTADO_04A  READY_FOR_COLLECTION          18   integrada na tabela; manifesto em data/samples/…/MANIFEST.json
ESTADO_04A  CONTRACT_READY_ROUTE_BLOCKED  50   ROBOTS_DISALLOWED_ROUTE · www.youtube.com · CANONICAL_ROUTE_READY=NO
ESTADO_04A  CONTRACTED_CANARY_FAILED       9   EMPTY_LIST (o PORQUE do canário, por fonte)
ESTADO_04A  SEM_CONTRATO                   7   «ramo de índice» — sem contrato no ficheiro do curator
```

Divergências classificadas (não fundidas às cegas):

- **50 fichas YouTube** descrevem a rota reprovada → linha `ESTADO_04A` diz que a
  `ACCESS_METHOD` acima é a rota que o gate reprovou. Owner: SOURCE CURATOR.
- **7 fichas `SEM_CONTRATO`** dizem `COLLECTION_FEASIBILITY: CONTRATO ESCRITO E CANARIO
  CORRIDO` sem contrato no ficheiro → `ESTADO_04A: SEM_CONTRATO`. Owner: SOURCE CURATOR.
- **Cabeçalho do bloco** diz «84 … contrato executável escrito» → nota de reconciliação
  logo abaixo: vale para 77 das 84.
- **`já existe igual` / `existe com divergência`:** 0 e 0 — nenhuma das 84 existia no
  Atlas do coordinator (nem citada, nem em tabela).

### 3.3 Evidência — o **manifesto** foi promovido; os **bytes** não (passo separado, declarado)

Para cada uma das 18 existe agora `data/samples/IT-SOURCE-SAMPLES/<ID>/MANIFEST.json`
com o sha256 do curator (conferido 18/18 contra os bytes no disco), o canário, o gate de
robots, a caracterização e a proveniência (`CANDIDATE_ID`, `376c0d9b`, caminho
original). `RAW_EVIDENCE_STATE = SHA256_VERIFIED_BYTES_NOT_IN_GIT`.

**Porque os bytes ficaram de fora — medido, não suposto.** Na primeira bateria, com os
18 ficheiros (2,5 MB de HTML) em `data/samples/IT-SOURCE-SAMPLES/<ID>/`, o frame de
revisão T3 (`provas/amostragem_neutra_t3.py` conta **todo corpo** em
`data/samples/IT-SOURCE-SAMPLES/*/*`) passou de 53 para 71 documentos e **4 testes
ficaram vermelhos** — `test_sao_53_fichas`, `test_as_46_foram_reaproveitadas_e_7_acrescentadas`,
`test_9_e_10_…`, `test_o_frame_e_maior_que_o_pacote` — que dizem, com todas as letras:
*«o tamanho da população mudou. Pode ser legítimo — mas obriga a refazer o frame, não a
ajustar o número»*. Refazer um frame de revisão humana é decisão do dono do T3, não
desta integração. Com o manifesto só (`.json` não é corpo), o frame fica em 53.

```
BLOCKER      promover os bytes das 18 muda o frame T3 (53 → 71) e o veredito tem de ser refeito
OWNER        dono do pacote de revisão T3 (provas/pacote_de_revisao_t3.py)
MINIMUM_FIX  copiar os 18 ficheiros de C:/bot-fontes-v2/curadoria/evidencia/<CAND>/ para
             data/samples/IT-SOURCE-SAMPLES/<ID>/, conferir o sha256 contra o MANIFEST.json,
             correr `py provas/pacote_de_revisao_t3.py --escrever` e refazer o veredito
```

### 3.4 `curadoria/` — entra o **registo**, não a **ferramenta**

Trazidos 18 ficheiros: os 14 JSON (contratos, veredito, canários, alocação de ID,
manifestos, caracterização, decisões, funil), os 3 MD (handoff, relatórios 02 e 03) e o
`.gitignore` (que documenta onde vivem os bytes e a intenção de promoção); mais
`docs/arquitetura/BOT-DE-FONTES-V2-PLANO.md`.

**Não trazidos: os 19 `.py`** (16 ferramentas + 3 testes delas). Medido na primeira
bateria: `curadoria/gate_de_rota.py` usa `RobotFileParser`, e a guarda
`OPortaoDeTransporteTemUmDonoSo.test_so_um_ficheiro_le_o_robots` só admite
`coleta/scrap_http.py` — *«nasceu um segundo leitor de robots.txt»*. As ferramentas
continuam em `claude/bot-de-fontes-v2-plano @ 376c0d9b`, citado em cada JSON e no
`ONBOARDED_BY`. Um teste reprova se aparecer código em `curadoria/`.

---

## 4 · LINHA VERMELHA — YouTube, verificado

```
YOUTUBE_BLOCKED = 50 · BLOCK_REASON = ROBOTS_DISALLOWED_ROUTE (50/50, inalterado)
SOURCE_CHARACTERIZED = YES · CONTRACT_READY = YES · CANONICAL_ROUTE_READY = NO
```

Nada de `feeds/videos.xml`, nem workaround, nem cookie, nem API key, nem `LOCAL_YTDLP`,
nem executor. Nenhum SOURCE_ID, ficha, contrato ou caracterização das 50 foi apagado:
as 50 fichas estão no Atlas (com `ESTADO_04A` a dizer bloqueada), os 50 contratos estão
em `curadoria/italy_contracts_curator.json` (registo). Nenhuma está na tabela que o
motor lê — provado por teste e por `ONBOARDED_IDS`.

---

## 5 · TESTES — baseline vs. depois, por NOME

Bateria: `py -m unittest discover -s tests -v`, a mesma nas duas medições, uma de cada vez
(nunca duas em paralelo), comparação **por nome**.

| | baseline @ 370ce450 (antes de editar) | final @ fcac49a3 (integração commitada) |
|---|---|---|
| TESTS_RUN | 4937 | **4954** (+17 = `tests/test_integracao_04a_curator.py`) |
| PASSED | 4600 | 4533 |
| FAILED (failures + errors) | 146 = 115 + 31 | 230 = 199 + 31 |
| SKIPPED | 190 | 190 |
| expected failures | 1 | 1 |
| **testes vermelhos distintos** (id sem parâmetro de subteste) | **124** | **124** |
| **NEW_FAILURES por nome** | — | **0** |
| BASELINE_FAILURES que sumiram | — | 0 |

O que explica 146 → 230 linhas com os **mesmos 124 testes**:

- `test_atomicidade_da_intelligence.P12….test_o_espelho_do_mapa_so_ganhou_as_pecas_declaradas`:
  já vermelho na baseline em **16** subtestes (um por fonte do mapa não declarada como
  peça, p.ex. `IT-T10-002`, `IT-T2-001`); agora **100** — +84, um por ficha nova. É o
  mesmo defeito pré-existente medido sobre uma população maior. Documentado em §7.
- `test_metricas.TestDocumentoBateComODono.test_todo_numero_publicado_vem_do_dono`:
  os mesmos **8** subtestes (4 documentos × `SOURCE_ID_COUNT`, 4 × `TEST_COUNT_CURRENT`),
  já vermelhos na baseline com `193` / `4.989`; agora com `277` / `5.006`. O nome do
  subteste inclui o valor, por isso aparecem como 8 «novos» e 8 «sumidos» — é um teste,
  os mesmos documentos, valores desfasados antes e depois.

**Bateria intermédia (antes dos dois ajustes de §3.3 e §3.4)** — 4952 testes, e aí sim
havia vermelhos novos por nome, que foram a razão dos ajustes e não foram «corrigidos
para dar verde»: `test_so_um_ficheiro_le_o_robots` (segundo leitor de robots.txt em
`curadoria/gate_de_rota.py`), 4 testes do frame T3 (53 → 71 documentos com os bytes
promovidos), `test_a_suite_nao_deixou_nada_no_acervo` ×2 + `rt7b` + `rt14` (as 18 pastas
ainda não commitadas apareciam como `??` em `data/samples`) e `M5_o_ponto_fixo` (mapa
ainda não regenerado). Depois do commit e da cadeia do mapa: nenhum deles.

Teste novo: **17 testes, 17 OK**; mutação 3/3 reprovada (ver §3.1).
Resíduo da suite: `data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json` reescrito em cada
corrida — restaurado com `git checkout` antes de cada commit (§7, item 5).

---

## 6 · SYSTEM MAP

- Cadeia canónica corrida **depois** do `git add` de tudo: `generate_system_map.py` →
  `validate_system_map.py` → `git add system-map/data italia-portale/client/system-map
  docs/fontes/INDICE-DE-FONTES.md regras/LEIA-ANTES-DE-COLETAR.md
  docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md` → commit.
- Antes do commit: `P1_SEM_DRIFT` FAIL, **CONTENT_DRIFT esperado** (o mapa commitado era
  o de 370ce450): fontes 213 → **297** (IT 244), `files_tracked 2124 → 2163`.
- Depois do commit `fcac49a3`: **`SYSTEM_MAP_CHECK = PASS`**, P1…P5 todas PASS. O drift
  que sobrou é só **PROVENANCE_DRIFT** (`HEAD` e `GENERATED_AT` nos gerados) — curado
  regenerando nesta bancada no commit final «mapa: regerado sobre a árvore final».
- Sem `--stamp`: a peça `C-IT-CONTRATOS` fica amarela («mudou depois da declaração»),
  que é o estado honesto. Recarimbar carimbaria todas as peças de uma vez.

Depois deste relatório e do know-how §162 entrarem no commit, a cadeia corre outra vez e
o resultado vai no commit «mapa: regerado sobre a árvore final da missão INTEGRACAO-04A»
— o último desta branch. `impressao_da_arvore.py --conferir-carimbo` (portão 2b, pós-commit)
corre depois desse commit; o resultado está na mensagem de entrega.

---

## 7 · FORA DO ESCOPO — documentado, não corrigido

| # | O quê | OWNER | MINIMUM_FIX |
|---|---|---|---|
| 1 | Promover os bytes das 18 (ver 3.3) | dono do T3 | copiar + sha + `pacote_de_revisao_t3.py --escrever` + veredito |
| 2 | Cabeçalho do Atlas diz `<!--M:SOURCE_ID_COUNT-->277<!--/M-->` (linhas 9 e 7277); o ficheiro tinha 185 fichas e agora tem 269. Pré-existente, agora mais desfasado | dono do Atlas | remedir e actualizar o marcador (o mapa já regista `contagem_declarada`) |
| 3 | `C-IT-CONTRATOS` em `architecture.declared.json` diz «13 contratos executáveis»; são 136 (105 + 18 onboarded + 13 à mão). Pré-existente | dono do mapa | reler a peça, corrigir o `what`, carimbar numa releitura geral |
| 4 | 5 dos 18 exemplos canónicos não são agronómicos (`esami-di-stato1`, `women-stem-2026`, `palio-casina-2026`, `documenti-elezioni-2025`, `dicono-di-noi`): o `LINK_PATTERN` é de forma, não de tema. Não é gate desta integração («linha na tabela = a casa sabe chegar; NÃO é aprovação de relevância») | Livro de Relevância / SOURCE CURATOR | rever o `LINK_PATTERN` das 5 ou deixar a relevância decidir na Admissão |
| 5 | A suite reescreve `data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json` a cada corrida (resíduo de teste; restaurado 3× com `git checkout`) | dono do censo da Sala | o teste escreve em `%TEMP%`, não no repo |
| 6 | `PyYAML` não está instalado nesta máquina: módulos de teste não carregam e contam como ERROR na baseline (parte dos 31) | máquina | `pip install pyyaml` ou `PYTHONPATH=.sintonia-libs` noutra bancada |
| 7 | `test_o_espelho_do_mapa_so_ganhou_as_pecas_declaradas` já reprovava 16 fontes do mapa como «peça não declarada»; com as 84 fichas reprova 100. Pré-existente, população maior | dono do mapa / da Intelligence | decidir se fonte do Atlas é peça declarável ou se o teste deve ler `Z-FONTES` como dono das fichas |
| 8 | As fichas das 50 YouTube e das 7 sem contrato carregam texto pré-gate (ver 3.2) — marcado por `ESTADO_04A`, não reescrito | SOURCE CURATOR | reescrever `ACCESS_METHOD` / `COLLECTION_FEASIBILITY` na próxima missão do curator |

---

## 8 · BLOCO DE ENTREGA

```
INITIAL_HEAD = 370ce450        FINAL_HEAD = o commit «mapa: regerado…» que se segue (medido na entrega)        REMOTE_HEAD = = FINAL_HEAD após push (medido na entrega por rev-parse)
SOURCE_CURATOR_HEAD_USED = 376c0d9b
MODEL_EFFECTIVE = claude-fable-5-1

HTML_READY_INPUT            = 18
HTML_SOURCES_INTEGRATED     = 18
HTML_CONTRACTS_INTEGRATED   = 18      (regras/italy_contracts_onboarded.json: 105 → 123; CONTRACT_IDS 118 → 136)
ATLAS_FICHAS_INTEGRADAS     = 84      (o bloco inteiro do curator: 18 READY + 50 BLOCKED + 9 CANARY_FAILED + 7 SEM_CONTRATO,
                                       cada uma com ESTADO_04A — identidade integra-se inteira, rota só a provada; ver 3.2)

YOUTUBE_BLOCKED_PRESERVED   = 50
YOUTUBE_READY_INTEGRATED    = 0
DUPLICATE_SOURCE_IDS_CREATED= 0       (0 vs Atlas 185 · 0 vs onboarded 105 · 0 vs MASTER 54 · 18 distintos)

EVIDENCE_MANIFESTS_PROMOTED = 18      EVIDENCE_BYTES_PROMOTED = 0 (passo separado, ver 3.3)
CURADORIA_FILES_BROUGHT     = 18 + 1 doc     CURADORIA_PY_LEFT_BEHIND = 19 (ver 3.4)

TESTS_RUN / PASSED / FAILED / SKIPPED = 4954 / 4533 / 230 (199 FAIL + 31 ERROR) / 190 @ fcac49a3   ·   baseline 4937 / 4600 / 146 / 190 @ 370ce450
NEW_FAILURES = 0 por nome (124 testes vermelhos distintos antes e depois); +84 subtestes de um teste já vermelho e 8 subtestes de valor desfasado — ver §5
BASELINE_FAILURES = 146 nomes (115 FAIL + 31 ERROR) em 4937 testes @ 370ce450
SYSTEM_MAP_CHECK = PASS
KNOW_HOW_DELTA = §162 (livre em 36/36 branches com o ficheiro; máximo anterior §161)

WORKTREE = C:/Users/London1/orca/workspaces/eame-sintonia/curator-04a-integration
PUSH_STATE = push no fecho (medido na entrega)      LOCAL==REMOTE = provado por git rev-parse após fetch (entrega)
NETWORK_REQUESTS = 0 (só git fetch/push)     PAID_USD = 0
NEXT_BIG_COLLECTION_ELIGIBLE_NEW_SOURCES = 18
```

**HARD STOP.** Integração autorizada não autoriza a execução seguinte. Nenhuma Big
Collection foi corrida. Entregue ao dono.

---

## 9 · EM LINGUAGEM SIMPLES

1. **Quantas fontes novas entraram?** 18 sites italianos ficaram prontos para a casa ir
   buscar. Além disso, 84 fichas novas entraram no Atlas (o caderno onde a casa anota
   todas as fontes que conhece), e 66 dessas fichas dizem, em letras grandes, «esta
   ainda não se busca».
2. **Quantos contratos foram integrados?** 18. Um contrato é a receita de como chegar a
   uma fonte e como saber que se trouxe o documento certo. Esses 18 entraram na única
   tabela que o motor lê, que passou de 105 para 123 receitas.
3. **Quantas YouTube ficaram de fora?** 50, de propósito.
4. **Porquê?** O caminho que o curator usou para as ler (`feeds/videos.xml`) está na
   lista de «não entre» do próprio YouTube (o `robots.txt`). Responder não é o mesmo
   que deixar entrar. Não se inventou porta lateral, não se usou login, chave ou
   programa de descarregar. As 50 continuam anotadas, com nome, número e a razão do
   bloqueio; só não entram na tabela de busca.
5. **O sistema está pronto para uma nova Big Collection com essas 18?** A parte de
   rota, sim: os 18 contratos passam na conferência do motor, o canário chegou a um
   documento real em cada uma, e o `robots.txt` deixa. O que **não** está feito, e não
   era para estar: os bytes dos 18 exemplos ficaram fora do Git (ver 3.3), a
   relevância dessas fontes para a ADAMA não foi julgada, e **eu não corri coleta
   nenhuma** — parei onde a missão manda parar.

Duas coisas que quase correram mal e que vale a pena saber: a primeira bateria mostrou
que trazer as ferramentas do curator criaria um segundo leitor de `robots.txt` (a casa
só admite um) e que trazer os bytes mudava uma população de revisão congelada; as
duas decisões acima nasceram dessas medições, não de gosto.
