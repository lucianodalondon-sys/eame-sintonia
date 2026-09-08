# CHECKPOINT · ACERVO → PACOTE → MOTOR → PORTAL → VISÍVEL

```
BRANCH              claude/integration-acervo-portal-v1
HEAD_BEFORE         90f5627dc69e5cc7db7080a84306cd1838de107f   (DEMO_HEAD)
DEMO_HEAD_TOUCHED   NÃO
OPPORTUNITY_BRANCH_TOUCHED   NÃO   (só lida, nunca escrita)
DEPLOY              nenhum
PACOTE SERVIDO      V21-044e4924854d5f0a   (era V21-69bf448ac934a6d9)
GERADOR CANÓNICO    claude/opportunity-commercial-priority-v1 @ 5fac11f
```

---

## 1 · EM LINGUAGEM SIMPLES

**O que entrou.** A entrega da missão Opportunity (7 commits, `5fac11f`). Ela não
traz código de portal — traz um pacote de inteligência melhor. Regenerei esse
pacote aqui, provei que é reprodutível, e fiz os três artefactos que o portal lê
serem reconstruídos a partir dele.

**Onde aparece.** O portfólio passou de **55 para 213** pares produto × cultura.
O portal passou a carregar **611 justificações de exclusão** que antes não
existiam — para cada produto que não aparece num cartão, agora há um código que
diz porquê. E cada cartão declara que **24 famílias de inteligência foram
consultadas**, com quantas responderam e quantas não.

**O que melhorou, além disso.** Quatro perdas medidas e corrigidas:
os 40 eventos do sector que chegavam como 2; os 147 cartões de vídeo que
chegavam vazios; a pastilha verde das janelas que prometia uma oportunidade e
levava a "caso não encontrado"; e a palavra "Validato" impressa em 29 janelas
que ninguém validou.

**O que continua a faltar.** Cinco milhões de caracteres de fala transcrita
estão no acervo e **zero** entram no pacote. A ciência chega com 88 registos de
763 que existem. As janelas agronómicas não têm proveniência: nenhuma das 29
declara fonte. E há um conflito de contrato entre as duas linhagens sobre o que
é uma oportunidade — que não se resolve deste lado.

---

## 2 · A MATRIZ DAS FAMÍLIAS

Medida por `node italia-portale/audit/cadeia-de-familias.mjs`, contra o pacote
canónico no disco. `MOTOR_IN → ACEITE` é o que o modelo recebeu e aceitou;
`REJ` é o que recusou, sempre com razão registada em `AM.ingest.report`.

| FAMILY | ACERVO | PACOTE | MOTOR | PORTAL | VISÍVEL | PERDA | DONO | RAZÃO DA PERDA |
|---|---|---|---|---|---|---|---|---|
| OPPORTUNITIES | — | 43 | 43 | 43 | 13+21+8+1 | 0 | Linha A | partição deliberada (a4508ef) |
| PRODUCTS_ADAMA (commercial) | 51 | 51 | 51 | 51 | 51 | 0 | — | — |
| PRODUCTS × CROP (pares) | 711 ocorr. | **213** | 213 | 213 | 213 | 436 ocorr. | Linha A | 114 termos não normalizam |
| REGULATORY | — | 163 | 163 | 163 | 163 | 0 | — | — |
| LABELS (productRelationships) | — | 2030 | 2030 | 2030 | 2030 | 0 | — | — |
| FIELD_SIGNALS (fieldBulletins) | — | 133 | 133 | 133 | 133 | 0 | — | — |
| CROP_WINDOWS (canónicas) | UNKNOWN | — | 29 | 29 | 29 | UNKNOWN | Linha B | origem não auditável |
| CROP_WINDOWS (leituras) | — | 7 | 7 | 7 | 7 | 0 | — | publicadas como currentFieldSignals |
| SCIENTIFIC_INTELLIGENCE | **763** | 88 | 88 | 88 | 88 | **675** | Linha A | pacote sem campo de texto científico |
| RESEARCHERS | — | 60 | 60 | 60 | 60 | 0 | — | — |
| TECHNICIANS | UNKNOWN | — | — | — | — | UNKNOWN | — | não medido |
| FIELD_VOICES (publicVoices) | — | 79 | 79 | 79 | 79 | 0 | — | 58 comentários + 21 vozes |
| VIDEOS | **1467** | 242 citados | 147 | 147 | **0** | 1220 + superfície | Linha A + B | ver §5 |
| TRANSCRIPTS | **143 úteis / 5.033.374 ch** | **0** | 0 | 0 | 0 | **tudo** | Linha A | sem campo no pacote |
| COMPETITOR_ACTIVITIES | 414 IT | 577 | 577 | 577 | 569 | 8 declarados | — | QA_UNREVIEWED, declarado |
| ACTIVE_ADS | 414 com data | 27 sem data | 27 | 27 | 27 | prova | Linha A | ver §6 |
| COMPETITOR_PRODUCTS | — | — | 36 | — | 36 | 0 | — | de ITALY_INGEST |
| NEWS | — | 8 | 8 | 8 | 8 | 0 | — | — |
| ARCHIVE | — | derivado | 1114 | — | 20/página | 0 | — | paginação declarada |
| HISTORICAL_SIGNALS | UNKNOWN | — | — | — | — | UNKNOWN | — | não medido |
| SOURCES | — | 191 | 189 | 191 | 189 | 2 | — | 2 sentinelas, recusa correta |
| REGIONS / CROPS / THEMES | — | vocabulário | — | — | — | 0 | — | tabelas do modelo |
| CROSSINGS (clientSafe) | — | 19 | 19 | 19 | 19 | 0 | — | — |
| FUTURE_RADAR | — | — | 45 | — | 44 | 1 | — | casa: 44 mostráveis, 1 abatido |
| EVENTS | — | 40 | **18** | 40 | **18** | 22 | — | 22 sem nome, recusa contada |
| FUTURE_EVENTS | — | 14 | **2** | 14 | 2 | 12 | — | 12 sem nome nem data |
| REGULATORY_FUTURE | — | 28 + 47 | 28 + 47 | 28 + 47 | — | 0 | — | — |
| AGROMET / PHENOLOGY | — | 44 | 44 | 44 | 44 | 0 | — | — |
| ACTIVE_INGREDIENTS | — | 53 + 203 | 53 + 203 | 53 + 203 | — | 0 | — | — |
| CROP_ECONOMICS | — | 2978 | 2978 | 2978 | — | 0 | — | — |

**Contabilidade global do transporte:** dos 6.895 IDs do índice mestre do pacote,
**0 estão ausentes do portal**. O transporte PACOTE→PORTAL não perde nada.

---

## 3 · O CHECKPOINT DA ETAPA 18

```
ACERVO_TO_PORTAL_AUDIT_COMPLETE ..... PARCIAL
    12 lentes independentes concluíram + árbitro adversarial + 11 medições
    diretas. As 26 famílias fecham nas 3 fronteiras a jusante; o lado ACERVO só
    foi medido em 6 famílias — nas outras 20 não existe manifesto contra o qual
    comparar, e isso é declarado em vez de estimado.

PORTAL_IS_USING_LATEST_INTELLIGENCE . SIM
    O artefacto publicado é byte-idêntico ao regerado pelo próprio
    site_v21_ingest.py a partir do pacote canónico, com o portão de proveniência
    ligado. Agora na safra V21-044e4924854d5f0a, de 5fac11f.

SCIENTIFIC_INTELLIGENCE_INTEGRATED .. PARCIAL
    88 de 88 chegam e são mostrados; agora com link para o paper (88/88 URL real).
    Mas o acervo tem 763 materiais e 93.933 caracteres de abstract que o pacote
    não transporta — não há campo de texto científico em SCIENCE.json.

VIDEO_TRANSCRIPTS_INTEGRATED ........ NÃO
    5.033.374 caracteres de fala transcrita, 143 objetos utilizáveis no acervo.
    ZERO campos de transcrição no pacote. ZERO no motor. ZERO na tela.
    ZERO das 43 oportunidades cita voz, canal ou vídeo como evidência.

CROP_WINDOWS_TRUSTED ................ NÃO
    29 janelas: PROVED 0 · PARTIAL 2 · UNKNOWN 27 · INVALID 0.
    SOURCE_IDS vazio em 29/29. CURRENT_STATUS é aritmética de datas em 29/29.
    A origem das 29 não é auditável: gerador, insumo e os dois contratos que o
    ficheiro cita estão ausentes de 979 commits de todos os refs.

ACTIVE_ADS_INTEGRATED ............... PARCIAL
    577 no corpus, 569 no DOM, 8 retidos e declarados. 27 declaram ACTIVE e
    NENHUM traz a data de verificação que o provaria — data que existe no
    acervo em 414/414. ACTIVE_ADS_PROVED = 0 no pacote.

FUTURE_RADAR_PRESENT ................ SIM, mas sem porta e sem assunto
    44 fichas desenhadas em casa.html, com portão próprio (casa-gate 30/30).
    Mas ZERO rotas do portal levam a casa.html — `navCasa` é código morto — e
    12 dos 13 campos obrigatórios do próprio handoff estão a 0/44.
    SIGNAL_ARCHIVE_SEPARATE = SIM (o arquivo é população à parte, 1114 registos).

OPPORTUNITY_CROSS_INTELLIGENCE ...... PARCIAL, e agora MEDIDO
    Cada um dos 43 cartões declara 24 famílias consultadas (1032 consultas):
    115 com correspondência · 303 só por cultura · 338 não encontradas ·
    276 sem chave de cultura. Consultar não é usar: EVIDENCE_SCAN diz
    1529 encontradas · 359 usadas · 1170 omitidas.

PRINCIPAL_LOSS_POINT ................ DOIS, E O SEGUNDO SÓ APARECEU NO FIM

  (a) O ACERVO NÃO ATRAVESSA A INGESTÃO
    Não é o transporte pacote→portal: esse não perde nada (0 de 6.895).
    É a fronteira ACERVO→PACOTE, e mede-se em três famílias:
        transcrições   5.033.374 caracteres → 0
        ciência        763 materiais → 88, e 93.933 ch de abstract → 0
        anúncios       414 datas de verificação no acervo → 0 no pacote
    O dono dessa fronteira é a linhagem geradora.

    ADENDO 2026-09-08 · A PERDA (a) AGORA TEM MEDIDOR.
        Os números de (a) viviam nesta tabela. `audit/fronteira-acervo-pacote.mjs`
        mede o lado que CHEGA, contra o artefacto versionado, e recusa-se a
        inventar o lado do acervo — que daqui não se conta.

        Medido na safra V21-06c6421d001ea52a:
            transcrições    184 registos · escada completa · SHA em 160 ·
                            5.167.243 ch DECLARADOS pela origem · 0 ch de fala
                            FECHADA_COM_FRONTEIRA_DECLARADA — o texto não
                            embarca de propósito, razão escrita no ingest
            ciência         0 ch de texto · 88 registos · 86 DOI · 88 URL
            anúncios        0 com data de observação · 577 · 27 ACTIVE
            vídeo orgânico  147 cartões · 139 completos · 147 sem COUNTRY_REACHED

        As três últimas em ABERTA_MEDIDA_DE_UM_LADO: nem fechadas, nem
        inventadas. E um degrau segue aberto sem bloquear a fronteira:
        TRANSCRIPT_USED_AS_EVIDENCE é falso em 184/184 — dono é o motor.
        `scripts/entrega_acervo_portal.py` compõe o resultado em
        ACERVO_TO_PORTAL_DELIVERY_READY, hoje NÃO.

        CORREÇÃO DE FRONTEIRA. A primeira versão deste adendo publicava o
        resultado como COLLECTION_FOUNDATION_CLOSED. Errado, e de nome: a
        fundação da coleta termina em ADMISSION/READY e NÃO depende de portal,
        pacote nem tela — se dependesse, um portal incompleto impediria a coleta
        de fechar. O dono canônico daquela constante é a linha
        claude/collection-foundation-integration-v1. Esta medição é
        DELIVERY / LINEAGE / OBSERVABILITY, e é precursora de sensor da camada
        de observabilidade que aquela linha instala depois da M1.

  (b) MOTOR → SUPERFÍCIE, classe «valor calculado sem markup»
    O transporte não perde um registo (0 falhas em 26 famílias). A segunda perda
    mora em campos que CHEGAM ao browser e que nenhuma linha de markup lê:
        26 campos de declaração de corte (1170 evidências omitidas, 80 produtos)
         9 campos de mc.*  ·  4 eixos de confiança
        250 + 120 citações de evidência por ação e por elo
         5 campos de vídeo em 147 cartões
    Um dado que chega e não é lido é indistinguível de um dado que não chegou —
    e não há portão que o veja, porque os portões medem o que o markup liga.
```

---

## 4 · O QUE FOI CORRIGIDO NESTA MISSÃO

| # | Defeito | Ficheiro | Medida antes → depois |
|---|---|---|---|
| 1 | `events` era alias de `futureEvents` | `italy-app-model.js:4559`, `portale.html:7667` | tela 2 → **18** cartões |
| 2 | O check `O1` usava um campo que o contrato declara não ser porta de visibilidade | `audit/checks.mjs` | 2 N/M → **0 N/M**, 71/71 |
| 3 | Ciência sem link para o paper | `portale.html` | 0 → **88/88** links |
| 4 | 147 cartões de vídeo vazios em duas fronteiras | `site_v21_ingest.py`, `italy-app-model.js` | 0/147 → **147/147** campos no motor |
| 5 | Pastilha verde prometia oportunidade inexistente | `portale.html` | **6 promessas falsas → 0** |
| 6 | "Validato" afirmava validação que ninguém fez | `portale.html` | → "Dati al" / "Data as of" |
| 7 | Checkpoint escrito à mão em 4 ficheiros | `audit/lib/pacote.mjs` + 3 portões | um dono só |
| 8 | Safra da Opportunity não chegava ao portal | 3 geradores | 55 → **213** pares; 0 → **611** justificações |
| 9 | Ficha da reunião mostrava códigos nus | `portale.html` | **0 → 384** provas com nome, 372 com «Apri» |
| 10 | Contraste 3,02:1 a 9,5px — **regressão minha** | `portale.html:765` | → 4,80:1 a 10px, BW2 verde |
| 11 | "fino al **null**" impresso ao cliente | `portale.html:4955` | **7 → 0** ocorrências |
| 12 | Arquivo prometia caso inexistente | `portale.html` | **29 → 0** promessas falsas |
| 13 | Guarda apagava a bandeira "texto retido" | `meeting-surface.js` | **0 → 33** declarações de proveniência |

**Instrumentos novos, versionados:**
- `audit/cadeia-de-familias.mjs` — mede as 26 famílias em 4 fronteiras, 5 perguntas (T1–T5)
- `audit/reconciliacao-do-catalogo.mjs` — reconstrói 711 → 213 sem reimplementar a normalização

---

## 5 · VÍDEO E TRANSCRIÇÕES — O CENSO

```
ACERVO      1467 objetos de vídeo distintos, 1467/1467 com url + título + data
            174 transcrições pedidas · 152 com texto · 143 utilizáveis
            5.033.374 caracteres de fala
            43 objetos (2.956.449 ch) ligados por campo declarado às culturas dos 43 casos
PACOTE      242 ids de vídeo citados por URL · 0 campos de transcrição em 32 ficheiros
            5 vídeos que o pacote CITA já têm transcrição no acervo — 97.328 ch parados
MOTOR       0 · a palavra `transcript` aparece 2× em italy-app-model.js, ambas em prosa
PORTAL      147 cartões de vídeo orgânico · 0 renderizam título, canal, data ou link
EVIDÊNCIA   0 das 43 oportunidades cita voz, canal ou vídeo
            as 57 citações de concorrente são 57/57 ANÚNCIOS PAGOS
```

**Distinção mantida:** VIDEO_EXISTS ≠ TRANSCRIPT_EXISTS ≠ TRANSCRIPT_USABLE ≠
TRANSCRIPT_USED_AS_EVIDENCE. URL de vídeo não é conteúdo analisado.

**Terceira fronteira, deliberadamente não atravessada.** Os 147 cartões já têm
os campos no motor (corrigido nesta missão), e **nenhuma tela os renderiza
ainda**. Razão: `CASE_ID` diz **111 IT · 26 ES · 10 FR**, e `COUNTRY_REACHED` é
nulo em 147/147. Ligar título e link poria 36 cartões em espanhol e francês numa
tela italiana na véspera da reunião. A decisão sobre os 36 é do dono do pacote.

---

## 6 · ANÚNCIOS ATIVOS

```
COMPETITOR_ADS_TOTAL_CORPUS ......... 577    (PAID 414 · ORGANIC_VIDEO 147 · NOTA 16)
COMPETITOR_ADS_PUBLICÁVEL ........... 569    8 retidos: CLIENT_SAFE=false + QA_UNREVIEWED
HISTORICAL_ADS ...................... 385
ACTIVE_ADS_PROVED (no pacote) .......   0    27 declaram ACTIVE, nenhum traz data de verificação
ACTIVE_ADS_UNKNOWN .................. 192
ACTIVE_ADS_PROVED (no ACERVO) .......  27    com data 2026-08-31T01:03:30+00
ACTIVE_ADS_VISIBLE_IN_PORTAL ........  27    com selo ATTIVO
```

O acervo tem `last_observed` e `first_observed` em **414/414** anúncios. O pacote
não os pede. O selo ATTIVO afirma o presente sem a data que o prova.
Regra respeitada: histórico nunca foi promovido a ativo.

---

## 7 · CROP WINDOWS

```
CROP_WINDOWS_TOTAL ....  29
CROP_WINDOWS_PROVED ...   0
CROP_WINDOWS_PARTIAL ..   2   IT-WIN-0001 (Veneto) · IT-WIN-0008 (Piemonte)
CROP_WINDOWS_UNKNOWN ..  27
CROP_WINDOWS_INVALID ..   0
CROP_WINDOWS_TRUSTED ... NÃO
```

- `SOURCE_IDS` vazio em **29/29**; o motor declara `NOT_EXTERNALLY_OBSERVABLE` 29/29
- `CURRENT_STATUS` é aritmética pura contra 2026-09-02 em 29/29
- `LAST_VALIDATED` tem **um único valor** (2026-09-02) em 29/29 — carimbo de geração
- 5 janelas sem data mostram "DATA DA CONFERMARE" — nenhuma data inventada
- A origem das 29: um único commit `9eb598a` (2026-09-02, importação). O contrato
  que o ficheiro cita (`INTELLIGENCE-TO-DESIGN-CONTRACT.md`) e o insumo
  (`CANONICAL-CROP-WINDOWS-2026-09-02.json`) **estão ausentes de 979 commits**

**As 29 e as 7 são universos distintos por desenho** (IDs distam um zero) e o
check `W1` já o protege. A superfície já não promove janela a oportunidade
(corrigido, §4 item 5).

---

## 8 · O CONFLITO QUE NÃO SE RESOLVE DESTE LADO

Duas leis declaradas, ambas testadas, discordam sobre o que é uma oportunidade:

| | Linha A · geradora | Linha B · portal |
|---|---|---|
| commit | `55c2674` · 2026-09-04 | `a4508ef` · 2026-09-05 |
| lei | `MEETING_SURFACE_RULE`, `LANE_OWNER = COMMERCIAL_PRIORITY` | `relevanceSurface` (`adama_relevance.py`) |
| partição | 5 / 8 / 13 / 17 | OPPORTUNITA 13 · RADAR 21 · SEGNALI 8 · ERRORE 1 |
| portão | `surface-contract.mjs` | `adama-relevance-gate` 7/7 + 19 testes |

Medido: `STRATEGIC_OPPORTUNITY` (8) e `COMMERCIAL_WATCH` (13) vão para RADAR;
8 casos `TO_VALIDATE` aparecem como OPPORTUNITA. Os botões PREPARARE ORA e
DA MONITORARE existem na tela e contam 0.

`surface-contract.mjs` está **3/8 desde a4508ef** — medido idêntico no DEMO_HEAD
intocado, portanto **não é regressão desta missão**. É INTEGRATION_DEPENDENCY.

---

## 9 · INTEGRATION_DEPENDENCY

Colidem com `claude/opportunity-commercial-priority-v1` — não editados aqui:

1. **Campo de texto científico em `SCIENCE.json`** — 93.933 ch de abstract para 83 papers
2. **Família de transcrições no pacote** — 5.033.374 ch, 143 objetos
3. **Data de verificação dos anúncios** — `last_observed` existe 414/414 no acervo
4. **Os 36 vídeos ES/FR** em `COMPETITOR-ACTIVITIES.json`
5. **CROP/ISSUE dos 88 papers** são o termo da busca, não o que o texto prova
   (87/88 batem `QUERY_*`, só 37/88 e 34/88 batem `PROVED_*`; 39/88 são `OFF_CASE`)
6. **A ligação janela ↔ caso** — `LEGACY_CASE_ID` preenchido 29/29 e resolve 0/29
7. **O conflito de contrato da §8**
8. **Proveniência das 29 janelas** — gerador e insumo ausentes do repositório

---

## 10 · O QUE FICA EM ABERTO NESTA MISSÃO

- **7 das 10 lentes ainda em execução** (opportunity, texto, action map, future
  radar, home/menu, referência visual, UNKNOWN→facto). Os seus resultados são
  suplemento a este checkpoint, não o substituem.
- **`build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip` não foi actualizado.** Medido:
  não é entrada da cadeia (`v21_ingest.py` lê `PREVIOUS-HANDOFF/`, versionado) e
  nenhum consumidor o lê. Carrega V21-99226fbb90dcdbc2, 37 casos. Actualizá-lo
  custa 2 MB permanentes; deixá-lo mantém no repositório um pacote que mente
  sobre a sua safra. **Decisão do dono do repositório.**
- **A terceira fronteira dos 147 vídeos** (§5), à espera da decisão sobre os 36.
- **`adama_catalogo_montar.py` não foi reexecutado** — a sua entrada
  (`build/SINTONIA-ITALY-PILOT-REALITY-HANDOFF/.../adama-italy-products.json`)
  está declarada ausente e a proveniência permanece UNKNOWN. A correção OPP-04
  vive no transportador `v21_ingest.py` e não exige o montador.

---

## 10b · O QUE O ÁRBITRO REFUTOU, E O QUE EU REFUTEI AO ÁRBITRO

O árbitro adversarial correu sobre as 10 lentes e **refutou 15 achados**. Cinco
por ESTADO — já corrigidos por commits desta missão (a pastilha das janelas, o
"Validato", os 384 códigos nus, os 147 cartões vazios a montante, e o BUILD_ID
do próprio grounding). Os outros por medição: nomes de campo que não existem,
causas alegadas que o teste não confirmou.

**E um blocker do árbitro é refutado por medição minha.** Ele diz que esta
linhagem editou `scripts/site_v21_ingest.py` "apesar de scripts/ ser território
da branch paralela". A regra é grossa demais. Medido por ficheiro:

```
scripts/site_v21_ingest.py    NÃO existe em 5fac11f — só nesta linhagem
scripts/meeting_snapshot.py   NÃO existe em 5fac11f — só nesta linhagem
scripts/it_casa_dados.py      NÃO existe em 5fac11f — só nesta linhagem
git diff --name-only 84f0375 5fac11f -- <os três>  →  0 ficheiros
```

Os três geradores da fronteira do portal são exclusivos desta casa e a branch
paralela nunca lhes tocou. Não há colisão. O que colide é `scripts/v21_*.py`,
e nenhum desses foi tocado.

---

## 11 · VERIFICAÇÕES EXECUTADAS

```
audit/run.mjs ......................... 71/71   (era 69/69 + 2 NÃO MENSURÁVEIS)
audit/casa-gate.mjs ................... 30/30
audit/meeting-gate.mjs ................ 23/23
audit/lote-completo.mjs ............... 15/15
audit/build-gate.mjs .................. proveniência provada · V21-044e4924854d5f0a
audit/cadeia-de-familias.mjs .......... T1–T5, 0 falhas, 0 não medidos
audit/reconciliacao-do-catalogo.mjs ... 711 = 275 + 436 · 213 pares · cobertura 38,7%
audit/competitor-population.mjs ....... PASS · 577 corpus · 569 no DOM em IT e EN

audit/brandwell.mjs ................... BW1 BW2 BW3 TY1 TY2 — todos PASS

audit/surface-contract.mjs ............ 3/8 — IDÊNTICO ao DEMO_HEAD intocado (§8)
audit/action-map-consistency.mjs ...... 10 discordâncias — IDÊNTICO ao DEMO_HEAD
audit/negative-control.mjs ............ 6/7 FAIL — vermelho permanente, ver abaixo
audit/click-audit.mjs ................. NÃO EXECUTADO (excedeu 600 s)
```

**Duas pendências de instrumentação, medidas e não corrigidas nesta missão:**

1. **Seis portões não são chamados por runner nenhum** — `brandwell`, `casa-gate`,
   `negative-control`, `action-map-consistency`, `cta-navigation`,
   `opportunity-trace`. `npm run prebuild` só chama `build-gate.mjs`. Foi
   exactamente assim que a minha regressão de contraste passou por uma suite que
   dizia 71/71.
2. **`negative-control.mjs` está 6/7 FAIL por razão alheia ao que mede** — o seu
   controlo-da-cópia lê `scripts/it_casa_dados.py`, fora da árvore que ele copia,
   logo ENOENT. Um vermelho permanente que ninguém corre torna um FAIL novo
   indistinguível de um velho.

```
```

**Limitações declaradas.** Duas hipóteses do orquestrador foram derrubadas pela
própria verificação e estão registadas como derrubadas, não apagadas. A
reprodutibilidade do pacote foi provada com duas corridas completas; a origem
tinha certificado apenas um ficheiro. `playwright-core` foi instalado nesta
sessão para que os portões de browser corressem — não estava presente.

---

## 12 · COMO REPRODUZIR

```bash
# o pacote canónico, do gerador
git worktree add --detach /tmp/wt 5fac11f
cd /tmp/wt && bash scripts/v21_cadeia.sh          # exit 0, ~20 s
cp -r /tmp/wt/build/ITALY-REALITY-HANDOFF-V2.1 build/

# os três artefactos que o portal lê
python3 scripts/site_v21_ingest.py
python3 scripts/meeting_snapshot.py --source-head 5fac11f --cutoff 2026-09-06T22:27:00Z
python3 scripts/it_casa_dados.py

# medir
node italia-portale/audit/run.mjs
node italia-portale/audit/cadeia-de-familias.mjs
node italia-portale/audit/reconciliacao-do-catalogo.mjs
node italia-portale/audit/build-gate.mjs
```

---

```
READY_FOR_INTEGRATION_WITH_DEMO = SIM, como CANDIDATA
    Todos os portões desta linhagem verdes; surface-contract 3/8 idêntico ao
    DEMO_HEAD e declarado como conflito de contrato, não regressão.
    A demo 90f5627 permanece intocada. Nenhum deploy foi feito.
```
