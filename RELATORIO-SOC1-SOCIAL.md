# RELATÓRIO SOC1 — LINKEDIN, INSTAGRAM E YOUTUBE PARA A BIG COLLECTION

> Missão SOC1 · worktree `social-prontidao-v1` a partir de `origin/unificacao-v1 @ 77077dee` · 2026-09-23
> Ordens: D16 (social é requisito da Big Collection) e D17 (sem rota paga por agora; nenhuma conta
> pessoal; foco no Scrap; YouTube pelas rotas que o Scrap declara, sem reabrir a análise).
> Missão irmã YT1 (`youtube-oficial-v1`) prova o YouTube pela Data API ponta a ponta — até ao fecho
> desta, a branch dela não tinha commit nenhum além da base; nada dela foi usado aqui.
>
> Nada foi colhido. Nenhuma chamada paga. Nenhum segredo lido. Nenhum byte de vídeo.
> A única rede usada foi ler as páginas públicas de termos (5 páginas, HTTP 200, US$ 0).

> **REORIENTAÇÃO da coordenação (mesmo dia):** o engenheiro do Scrap (`sintonia-scrap-engineer`)
> respondeu a matriz (`auditoria-madrugada/scrap-engineer-resp-social.txt`) e está a ligar as portas
> na worktree `scrap-portas-v1`. A SOC1 NÃO toca no Scrap (D17.2) e passa a ser: (1) conferir a matriz
> dele contra o código, 3 capacidades por plataforma, sem rede; (2) contas-alvo; (3) a decisão do
> LinkedIn para o dono. Essas três partes vêm primeiro; a matriz medida vem depois, como anexo.

## (1) CONFERÊNCIA DA MATRIZ DO ENGENHEIRO — 9 afirmações, sem rede

| # | Afirmação dele | Veredicto | Prova |
|---|---|---|---|
| Y1 | `youtube.public_audio` READY pela porta do pedido; sem porta operacional | **CONFIRMADO** | fase `audio-youtube` (`scrap_colheita.py:248`), `serve_fases` (`receitas.py:499`), CHECK `CAN_COLLECT_NOW`, matriz `FETCH_AUDIO_BYTES` = ALLOWED; `sintonia-scrap.yml` não tem ramo → `FASE_DESCONHECIDA` |
| Y2 | `youtube.channel.discovery` PROVED_BUT_NOT_WIRED; chave só no `scrap-social.yml:311` | **CONFIRMADO, com correção de nome** | a fase `canal-youtube` existe e está em `serve_fases` (`receitas.py:493`) — está LIGADA na porta do pedido; falta a porta operacional (ramo no `sintonia-scrap.yml`) e a chave nesse workflow. O `scrap-social.yml` tem a chave mas corre `social_scrap`, que para no COLLECT |
| Y3 | legenda nativa só pela Apify (paga) → fora por D17 | **CONFIRMADO** | matriz `FETCH_TRANSCRIPT`: `captions.*` = NAO, `timedtext` = ROUTE_NOT_ALLOWED, `apify:transcricao` = CONDICIONAL — a única que não é NAO é paga |
| Y+ | Defeito 1: `sintonia-scrap.yml` recusa `yt-alvos`/`yt-transcrever` com motivo velho | **CONFIRMADO** | `sintonia-scrap.yml:557-559` diz «a matriz nao declara capacidade de BYTES para YOUTUBE»; a matriz declara `FETCH_AUDIO_BYTES` com rota permitida |
| I1 | `instagram.reel.transcribe` PROVEN, grátis, `CAN_COLLECT_NOW` | **REFUTADO como permitido** | a própria matriz do Scrap: `decisao(INSTAGRAM, FETCH_TRANSCRIPT)` = **ROUTE_NOT_ALLOWED** (faster-whisper, PERMITIDA=NAO). O CHECK diz CAN porque **não lê a permissão da matriz** — `scrap_executor.CHECK` nunca chama `social_matriz.decisao` |
| I2 | `reel.capture`/`reel.audio` PROVEN, sem conta, custo zero | **CONFIRMADO na técnica, REFUTADO como pronto** | `cap.da_matriz` = None para as duas: não têm capacidade na matriz, ninguém decidiu se são permitidas; a NIGHT-SHIFT-01 mediu `reel.capture` → `RESULT=ROUTE_NOT_ALLOWED` (`scrap_colheita.py:532`). E a porta da Collection tem o Instagram em POLICY_BLOCK (D15) |
| I3 | `instagram.profile.discovery` READY (ramos `janela*`), só de máquina residencial | **CONFIRMADO o ramo, REFUTADO o READY** | ramo em `sintonia-scrap.yml:476`, mas `decisao(INSTAGRAM, INCREMENTAL)` = **ROUTE_NOT_ALLOWED**: a rota `grade` tem `OWNER_AUTHORIZED=SIM` e `PLATFORM_POLICY=NOT_MEASURED`, e isso fecha (`social_matriz.py:599-615`) |
| L1 | `linkedin.identity.discovery` READY só como catálogo | **CONFIRMADO** | matriz `DISCOVER_ACCOUNT` = ALLOWED (site da organização), CHECK `CAN_COLLECT_NOW`, ramo `sintonia-scrap.yml:518`, fase CATALOG |
| L2 | catálogo não atravessa a Admissão | **CONFIRMADO** | `retorno_da_coleta.ENTRAM_NO_INGRESSO == ('COLHEITA',)` |
| L3 | «técnica PROVEN no histórico: 372 posts e 472 itens (C11)» | **CONFIRMADO, com o que faltava dizer** | `data/samples/RUN-MANIFEST.json`: 472 itens brutos de `apify/harvestapi~linkedin-post-search`, ESPANHA, 29/08, busca por PALAVRA (não por conta). Provado por rota **paga**, que a matriz marca ROUTE_NOT_ALLOWED |

Resumo: **YouTube, 3 de 3 confirmadas** (e o defeito do workflow também). **Instagram: a técnica
existe, a permissão não** — 2 refutadas e 1 com o ramo certo e o READY errado; o erro vem de ler
`CAN_COLLECT_NOW` como «pode colher». **LinkedIn, 3 de 3 confirmadas.**

Para o Scrap (é dele corrigir, D17.2): `CHECK` e o roteador respondem a perguntas diferentes.
`CHECK` = «a peça existe e está configurada»; o roteador = «a matriz deixa». Hoje 4 capacidades do
Instagram dizem SIM no primeiro e NÃO no segundo.

## (2) CONTAS-ALVO

**YouTube — com identidade provada: 53**
- 50 canais nos contratos (`regras/italy_contracts_onboarded.json`): SOURCE_ID conhecido pelo Atlas
  **50/50**, `IDENTITY_MATCH=YES` **50/50** (lida do documento do canal em 20/09), 50 CHANNEL_ID
  distintos. Territórios: T7 18 · T5 10 · T12 8 · T2 4 · T8 3 · T9 3 · T10 2 · T11 2.
- +1: IT-T8-001 Agronotizie (`UCUs2Mg7jvUTRt7_MSOFYM5Q`, contrato em `italy_contracts.mjs`).
- +2 concorrentes IT (`CONTAS-V1.json`): Bayer e Syngenta, PROVED e autorizadas; sem SOURCE_ID.

**YouTube — o que falta qualificar: até 43 das 71 candidatas**
- 71 candidatas (`FONTES-CANDIDATAS.json`, todas `EM_ANALISE`). 36 trazem `/channel/UC…` no
  endereço; **28 dessas já estão nos 50** → 8 canais UC novos.
- 35 vêm como `@handle`, `/user/`, `/c/` ou playlist. **Quantas já estão nos 50: NÃO SEI** —
  transformar um handle em channel_id pede a API (`channels.list forHandle`), e esta missão não usa rede.

**Instagram — com identidade provada: 2** (Bayer Italia, Syngenta Italia — `CONTAS-V1.json`,
autorizadas). A BASF aparece PROVED mas é página global (excluída).
- 25 candidatas IT, **todas declaradas no site oficial do dono** (é essa a evidência de identidade),
  0 com SOURCE_ID, todas POLICY_BLOCK. No Atlas: 1 endereço Instagram (`instagram.com/agronotizie`,
  dentro da ficha IT-T8-001).
- Para a rota oficial (Graph `business_discovery`) servir, o alvo tem de ser conta Business/Creator:
  **quantas das 25 são: NÃO SEI**.

**Quantos faltam para a Big Collection:** nenhum documento define um número-alvo de canais ou
perfis. **NÃO SEI** — é o dono quem diz quantos bastam. O que se mede é o que já existe (acima).

## (3) LINKEDIN — A DECISÃO PARA O DONO (sem rota paga, sem conta pessoal)

O que existe: 44 candidatas IT, todas declaradas no site oficial da organização, todas
POLICY_BLOCK; 3 concorrentes IT PROVED (nenhuma autorizada: 2 páginas globais, 1 de país
desconhecido); 12 perfis de PESSOAS (investigadores, `SENSOR-PILOT/CANAL-IDENTIDADE.json`) — perfil
pessoal é dado pessoal e fica fora de qualquer opção.

| Opção | O que entra | Custo | Risco | Prazo |
|---|---|---|---|---|
| **A. Catálogo de identidade** | o ENDEREÇO LinkedIn das 44, lido do site da própria organização. Não traz posts e não atravessa a Admissão (é CATALOG) | US$ 0 | nenhum (não toca no LinkedIn) | já existe (`identidade-linkedin`, ramo `sintonia-scrap.yml:518`) |
| **B. O mesmo conteúdo pela porta do site** | o que a organização publica no próprio site — muitas vezes o mesmo que põe no LinkedIn — pela coleta HTML canónica | US$ 0 | nenhum novo | já em curso: das 44, **~19** já têm o dono com fonte HTML nos contratos e **~31** têm o dono citado no Atlas (comparação aproximada pelo nome; pode errar para os dois lados) |
| **C. Autorização escrita / parceria** | posts de uma organização que aceite: ela partilha/exporta, ou dá acesso de administrador à página e a API oficial (Community Management) lê só essa página | US$ 0 em dinheiro | baixo; custa gente a pedir | semanas, organização a organização; quantas aceitam: NÃO SEI |
| ~~D. Apify / conta pessoal~~ | — | pago | proibido pelos termos (§8.2 cobre agregadores) e fora por D17 | **fora da mesa** |

**Recomendação:** A + B agora (zero custo, zero risco), e C só para as poucas organizações mais
importantes, se o dono achar que vale o tempo de pedir. **A frase para o dono:** «ler posts do
LinkedIn de outras empresas, de graça e dentro das regras, não existe hoje; o que existe é saber onde
elas estão (A) e ler o que elas publicam no próprio site (B)».


---

# ANEXO — A MATRIZ MEDIDA (antes da reorientação)

## A pergunta (D17)

**O que falta para o Scrap colher LI/IG/YT de graça e entrar na Collection canónica?**

Resposta curta, medida:

| Plataforma | Rota grátis E permitida existe? | O que falta |
|---|---|---|
| YouTube | **SIM** — Data API v3 (`OFFICIAL_API_FREE`) | a chave está só no `scrap-social.yml`, que não corre as fases canónicas; o curator bloqueia YouTube no QUALIFY por «capacidade» que já existe; regra de retenção de 30 dias da API não está no código |
| Instagram | **SÓ UMA, e ainda não construída** — Graph API `business_discovery` | decisão do dono: uma conta Instagram Business **do projeto** + app Meta; depois engenharia (a rota está declarada, não tem código) |
| LinkedIn | **NÃO** para posts de terceiros | não é engenharia: os termos proíbem raspar, a API só lê páginas de que se é administrador, e agregador pago também é proibido (§8.2) |

## MATRIZ (medida no runtime, não escrita à mão)

`py provas/prontidao_social_v1.py --json docs/sintonia-scrap/SOC1-PRONTIDAO-SOCIAL-V1.json`

Junta os três registos em separado — **DECLARADAS** (`scrap_capacidades`), **EXECUTORES**
(`scrap_registo`), **FASES** (`scrap_colheita`) — mais a matriz de rotas (`social_matriz`), a porta
(`ponte_candidatas` + `worker.etapa_qualify` chamado de verdade) e o `scrap_executor.CHECK` (custo 0).

| Capacidade | DECLARADA | Rota ligada | Fase | CHECK | Porta | Prontidão | Rota / custo |
|---|---|---|---|---|---|---|---|
| youtube.search | PROVEN | sim | busca-youtube (CATALOG) | CREDENTIAL_MISSING | enfileirável | READY_PENDING_CREDENTIAL | API grátis, 100 unid./chamada |
| youtube.channel.discovery | PROVEN | sim | canal-youtube (COLHEITA) | CREDENTIAL_MISSING | enfileirável | READY_PENDING_CREDENTIAL | API grátis, 1 unid./50 vídeos |
| youtube.video.metadata | PROVEN | sim | video-youtube (COLHEITA) | CREDENTIAL_MISSING | enfileirável | READY_PENDING_CREDENTIAL | API grátis, 1 unid./50 vídeos |
| youtube.comments | PROVEN | sim | comentarios-youtube (COLHEITA) | CREDENTIAL_MISSING | enfileirável | READY_PENDING_CREDENTIAL | API grátis, 1 unid./página |
| youtube.channel.resolve | PARTIAL | sim | **nenhuma** | CREDENTIAL_MISSING | enfileirável | READY_PENDING_CREDENTIAL | API grátis |
| youtube.native_caption | PARTIAL | sim | nenhuma | CREDENTIAL_MISSING | enfileirável | READY_PENDING_CREDENTIAL | **só Apify (paga)** — fora por D17 |
| youtube.public_audio | PROVEN | sim | audio-youtube (COLHEITA) | CAN_COLLECT_NOW | enfileirável | READY | yt-dlp local, US$ 0 · ⚠️ OWNER_AUTHORIZED=SIM + PLATFORM_POLICY=DISALLOWED |
| youtube.media | BLOCKED | — | — | — | enfileirável | FAIL_CLOSED | nenhuma (e fica assim) |
| instagram.* (7) | 3 PROVEN, 1 PARTIAL, 1 BLOCKED, 2 UNKNOWN/NOT_EXEC | 4 de 7 | só `janela*` (profile.discovery) | 4 CAN_COLLECT_NOW | **POLICY_BLOCK (D15)** | ROUTE_NOT_ALLOWED ×7 | rotas grátis públicas = navegador deslogado, proibidas pelos termos |
| linkedin.* (8) | 1 PARTIAL, 4 BLOCKED, 2 UNKNOWN, 1 NOT_EXEC | 1 de 8 (identity) | identidade-linkedin (CATALOG) | 1 CAN_COLLECT_NOW | **POLICY_BLOCK (D15)** | ROUTE_NOT_ALLOWED ×8 | nenhuma rota de conteúdo grátis permitida |

Totais: YouTube 8 = 1 READY · 6 READY_PENDING_CREDENTIAL · 1 FAIL_CLOSED. Instagram 7 = 7 ROUTE_NOT_ALLOWED.
LinkedIn 8 = 8 ROUTE_NOT_ALLOWED. Nenhuma linha `UNKNOWN`, nenhuma `PROVED_BUT_NOT_WIRED` nas três.

**Discordância entre donos, medida:** o Scrap diz `CAN_COLLECT_NOW` para 4 capacidades do Instagram e
1 do LinkedIn; a porta da Collection diz `POLICY_BLOCK`. A matriz mostra as duas frases lado a lado —
nenhuma apaga a outra. Quem ganha é a D15, até o dono autorizar uma rota.

**Falso positivo na superfície (não corrigido, é do Scrap):** `provas/superficie_do_scrap_v1.py`
marca `youtube.public_audio` como «paga». O `_e_paga()` procura a palavra `coletor` no código-fonte
da rota, e ela aparece num COMENTÁRIO (`coleta/adaptador_youtube.py:716`). A rota é local e custa 0.
Fica para o engenheiro do Scrap (D17 item 2).

## CREDENCIAIS (só estado, nunca valor)

| Nome | Neste shell | Nos workflows | Preenchido no GitHub? |
|---|---|---|---|
| `YOUTUBE_DATA_API_KEY` | ABSENT_LOCAL | `scrap-social.yml:311` | **NÃO SEI** — `gh` sem sessão nesta máquina. Indício: o piloto de 2026-09-08 correu com ela (15 vídeos, 31 unidades) |
| `APIFY_TOKEN_POOL` | ABSENT_LOCAL | apify-conexao, apify-sensores, comunicacao-publica, sintonia-scrap | NÃO SEI (e fora por D17) |
| token Meta Graph (Instagram) | — | nenhum | **não existe nome no repo**: a rota está declarada e nunca foi ligada |

`SECRET_WIRING_GAP`: nenhum para o YouTube (o secret entra no mesmo passo que chama a fase). Para o
Instagram oficial, o gap é total: nem nome, nem secret, nem adaptador.

## TERMOS (trecho + URL + data)

Guardados em `candidatas/PROVA-TERMOS-SOC1-V1.json` (novo, com sha256 e os ficheiros ao lado) e,
para a D15, em `candidatas/PROVA-TERMOS-REDES-SOCIAIS-V1.json` (já existia, não mexido).

- **LinkedIn**, User Agreement (em vigor 03/11/2025, lido 23/09 09:42Z): «Develop, support or use
  software, devices, scripts, robots … to scrape or copy the Services, including profiles and other
  data». API Terms (lido 23/09 10:28Z) só licenciam a API «in connection with your Application»; a
  Community Management API lê páginas de que se é administrador — não as de terceiros.
- **Instagram**, Terms of Use (em vigor 01/01/2025, lido 23/09 09:44Z): «… collecting information in
  an automated way without our express permission, regardless of whether such automated access or
  collection is undertaken while logged-in». Rota oficial, doc da Graph API (lido 23/09 10:40Z):
  `business_discovery` «Retorna dados sobre outros usuários do Instagram com uma conta empresarial ou
  de criador de conteúdo», e exige «um token de acesso de um usuário do Facebook com … instagram_basic
  … pages_read_engagement».
- **YouTube** — D17 manda não reabrir a análise; o texto fica só registado. Terms (em vigor
  15/12/2023, lido 23/09 10:28Z): «access the Service using any automated means … except (a) in the
  case of public search engines … or (b) with YouTube's prior written permission». Developer Policies
  III.E.4 (lido 23/09 10:28Z): «… Non-Authorized Data … but not longer than 30 calendar days» e «an
  API Client must not store the subscriber count … for more than 30 days».
  **Isto é uma regra de RETENÇÃO da rota permitida, não um bloqueio**: a Big Collection guarda RAW
  para sempre, e `grep "30 calendar days"` no código dá 0. Passa para a YT1/coordenação.

## CONTAS_ALVO (identidade provada)

| Plataforma | Candidatas IT (`FONTES-CANDIDATAS.json`) | Declaradas no site oficial do dono | Com SOURCE_ID no atlas | Concorrentes IT PROVED (`CONTAS-V1.json`) |
|---|---|---|---|---|
| LinkedIn | 44, todas POLICY_BLOCK | 44 de 44 | 0 | 3 |
| Instagram | 25, todas POLICY_BLOCK | 25 de 25 | 0 | 3 |
| YouTube | 71, todas EM_ANALISE | 55 de 71 | 0 | 2 |
| YouTube (contratos `italy_contracts_onboarded.json`) | 50 canais UC distintos | — | **50 de 50** (`fonte_do_atlas.conhece`) | — |

«Declarada no site oficial do dono» é leitura minha do campo `ONDE_VIU`; não há campo de identidade.

**RAW já colhido (só leitura):** YouTube IT pela API oficial, 08/09: 5 canais, 15 vídeos, 2
comentários, 31 unidades, US$ 0 (`data/samples/SOCIAL-IT/YOUTUBE-PILOTO-IT.json`; os brutos só
como artifact do Actions, retenção 30 dias). Instagram IT: **nenhum**. LinkedIn de conta italiana:
**nenhum**. O resto é Apify histórico (Espanha, buscas por palavra) — fora por D17.

## LIGAÇÃO NA COLLECTION

Caminho que existe: pedido → `pedido/receitas.py` (executor `scrap-colheita`) → `scrap_colheita.colher`
→ `scrap_executor.COLLECT` → adaptador → envelope → `coleta/ingresso.py` (porta) → `raw_asset` →
Admissão → Sala. Provado offline por `o_fluxo_canonico_do_scrap`, `o_scrap_chega_ao_acervo`,
`o_canario_do_scrap_v1` — nenhum deles com fase do YouTube.

MISSING_ROUTE, com dono:

1. **Curator → Scrap (ENGENHARIA).** `curadoria/worker.py:398` devolve `BLOCK/CAPABILITY` a toda
   candidata YouTube («exige channel_id … capacidade com outro dono»). A capacidade existe no Scrap;
   o worker não sabe encaminhar para `scrap-colheita`. Hoje o SOURCE_ID tem de vir à mão no `--fonte`.
2. **Chave (INFRA).** As 4 fases oficiais só correm onde está `YOUTUBE_DATA_API_KEY` (runner).
3. **JSON → DERIVED (DESENHO).** A observação social entra como `application/json` e nenhum derivador
   aceita esse tipo (`ingresso.py:555`): DERIVED = NOT_APPLICABLE; a Admissão lê o texto do envelope.
4. **Resposta crua da API → RAW (DESENHO).** `social_envelope.guardar_raw` escreve no disco do
   runner, não em `raw_asset` (`SCRAP_RAW_NAO_RECEBIDO`).
5. **Retenção de 30 dias (DONO/YT1).** Ver Termos.
6. **Contratos YouTube desta linha apontam para um adaptador que não está aqui.** Os 50 contratos
   nomeiam `CANAL_PUBLICO_YOUTUBE_V1` (motor JS), cujo código vive em `f98f234c`/`48999d13`, fora
   desta árvore (`RELATORIO-RECONCILIACAO.md:190`). Essa rota **não está na matriz do Scrap**; a
   equivalente declarada pelo Scrap é `canal-youtube` (playlistItems.list). Os mesmos 50 pares
   SOURCE_ID ↔ CHANNEL_ID servem de entrada para ela.
7. **Proveniência.** O envelope traz `PUBLISHED_AT` e `SOURCE_LOCATION` (UNKNOWN por omissão);
   `FACT_TIME`/`FACT_LOCATION` chegam à porta como «NAO SEI». PUBLICATION_TIME ≠ FACT_TIME mantido.

## OPÇÕES PARA O DONO (D17: paga só como último recurso; conta pessoal fora da mesa)

### YouTube — recomendação: **A**
- **A. Data API v3 pelo runner** (rota do Scrap, autorizada por D17). Colhe: lista de vídeos por
  canal, título, descrição, data, métricas, comentários. Custo US$ 0; quota: 50 canais × (1 unidade
  de lista + 1 de metadados) ≈ 100 unidades/dia de 10.000. Prazo: horas depois das portas do engenheiro — as fases já
  existem na porta do pedido. Falta: o ramo e a chave no `sintonia-scrap.yml` (o engenheiro do
  Scrap está nisso, `scrap-portas-v1`), dispatch com `--fonte` dos 50 SOURCE_IDs, e a regra dos 30 dias.
- **B. A + áudio público local** (`audio-youtube`, yt-dlp + transcrição na GTX 1080). Traz a FALA dos
  vídeos. US$ 0. O Scrap já a declara `OWNER_AUTHORIZED=SIM` com a plataforma `DISALLOWED` — D17 cobre
  isto; fica escrito para ninguém dizer que não viu. Só corre em máquina local (IP de datacenter
  barrado).
- C. Legenda pela Apify — **paga**, só último recurso.

### Instagram — recomendação: **B**, se o dono aceitar ter uma conta Business do projeto
- A. Ficar em POLICY_BLOCK. US$ 0, zero dados. É o estado de hoje.
- **B. Graph API `business_discovery`** (oficial, grátis). Precisa de: conta Instagram Business
  **do projeto** (não de uma pessoa), uma Página do Facebook, um app Meta. Colhe dos alvos que forem
  conta empresarial/criador: legendas, datas, contagens de gosto e comentário. Risco: dentro dos termos;
  a Meta pode rever o app. Prazo: a conta e o app dependem do dono; depois ~2–3 dias de engenharia no
  Scrap (a rota está declarada, sem código, sem nome de credencial). Quantas das 25 são contas
  empresariais: **NÃO SEI** (não medido).
- C. Apify — paga **e** continua contra os termos («regardless of whether … logged-in»). Não resolve.

### LinkedIn — recomendação: **A + B**, e dizer ao dono que «coletar posts de graça e dentro das regras» não existe hoje
- **A. Só identidade** (`identidade-linkedin`, lê o site da própria organização). Grátis, permitido,
  já existe. Não traz posts.
- **B. O mesmo conteúdo por outra porta:** as organizações costumam publicar no próprio site/newsletter
  o que põem no LinkedIn; isso já entra pela coleta HTML canónica. Grátis.
- C. Autorização escrita de cada organização ou do LinkedIn (única via legal para posts). Prazo incerto.
- D. Apify — paga **e** proibida (§8.2: dados obtidos «through third parties … data aggregators»).
  Não resolve.

**TÉCNICO (resolve-se):** encaminhar YouTube do curator para o Scrap; dispatch das fases com
SOURCE_ID; derivador de JSON; RAW da resposta crua; o falso «paga» da superfície; código da Graph API.
**DECISÃO DO DONO:** conta Business do projeto no Instagram; regra dos 30 dias da API do YouTube;
aceitar que LinkedIn fica em identidade + site.

## FEITO_SEM_DONO (fase 3)

- `provas/prontidao_social_v1.py` — a matriz acima, medida no runtime, sem rede e sem gasto. Lê a
  superfície da V1 em vez de medir de novo.
- `tests/test_prontidao_social_v1.py` — 18 testes.
- `candidatas/PROVA-TERMOS-SOC1-V1.json` + 4 ficheiros em `candidatas/prova-termos/`.
- `docs/sintonia-scrap/SOC1-PRONTIDAO-SOCIAL-V1.json` — a matriz gravada.

**Não liguei nenhuma rota.** Motivo medido: as únicas grátis-e-permitidas são as do YouTube, e essas
são da YT1 (ordem da coordenação); no Instagram e no LinkedIn não há nenhuma que o dono já tenha
autorizado. Ligar qualquer coisa aqui seria repetir a YT1 ou contornar a D15.

## TESTS · MUTATION

- `py -m unittest tests.test_prontidao_social_v1` → 18 OK.
- Mutação (9 ataques na prova, cópia de segurança fora do repo, `.pyc` apagado a cada ataque):
  valor da chave sai · D15 ignorada · conta pessoal vira grátis · «não sei» vira fechado · ficha do
  worker não restaurada · Apify vira grátis · secret «preenchido» inventado · aviso do dono some ·
  rota paga vira READY → **9/9 mortos** (o de «Apify grátis» sobreviveu à 1.ª ronda; ganhou dois testes
  e morreu na 2.ª).
