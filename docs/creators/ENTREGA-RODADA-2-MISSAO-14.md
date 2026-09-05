# MISSÃO 14 · RODADA 2 — ENTREGA A–S

**Data:** 2026-08-30 · **Branch:** `claude/eame-agro-creators-map-77c4ld`
**Suíte:** 368 provas · **novas falhas introduzidas: 0**

---

## A · WORKFLOW DE CREATORS DESPACHÁVEL

`WORKFLOW_DISPATCH_AVAILABLE = YES` — provado por execução, não por leitura.

Movimento mínimo, como pedido: **um arquivo, 149 linhas**,
`.github/workflows/apify-creators.yml`, num commit próprio sobre o branch padrão.
Nenhum script, dado, documento, casco ou arquitetura foi levado junto.

O workflow é despachável a partir do padrão mas os scripts vivem no branch de trabalho.
O **passo 0** falha com mensagem explícita se o ref despachado não os contiver — dez
segundos de guarda em vez de um traceback de import que não diz o que houve.

## B · ISOLAMENTO EARLY SIGNAL × CREATOR MAP — provado

| dimensão | EARLY SIGNAL | CREATOR MAP |
|---|---|---|
| workflow | `apify-sensores.yml` | `apify-creators.yml` |
| dataset | `data/samples/SENSOR-PILOT/` | `data/samples/CREATOR-MAP-EAME/` |
| `RUN_ID` | `SENSOR-*` | `14-MAPA-DE-CREATORS-EAME-*` |
| manifesto | `RUN-MANIFEST.json` | `CREATOR-MAP-EAME/RUN-MANIFEST-CREATORS.json` |
| commit | `git add -A data/samples/...` | **caminhos nomeados**, nunca `-A` |

**A ponte foi removida.** `apify-sensores.yml` não tem mais nenhuma referência a creators.

Sobre a disputa no arquivo global: não era corrida improvável, era **corrida garantida** —
`pv.gravar()` lê tudo, junta e reescreve o arquivo **inteiro**; quem terminasse por último
apagaria o outro. A correção não é lock, é **namespace**: `pv.MANIFESTO` é redirecionado,
a porta única do `coletor` continua intacta, e o ponto de disputa deixa de existir.
`concurrency: creator-map-${{ github.ref_name }}` impede dois jobs **desta** missão
colidirem; paralelismo **entre** missões continua permitido.

## C · CREATORS RESOLVIDOS POR PAÍS

**6 identidades resolvidas em fonte primária** — e os seis falharam de **cinco maneiras
diferentes**, o que é o achado mais reaproveitável da rodada:

| classe de erro da seed | n | caso |
|---|---|---|
| `HANDLE_ERRADO_NA_SEED` | 1 | `@davide_gomiero` → o real é **`@gomierofarm`** (457 mil, 3.920 posts) |
| `NOME_E_HANDLE_ERRADOS_NA_SEED` | 1 | "Leggeri" → **Leggieri**; e `@evolovers` → `@narduccio_capicchiaro` |
| `PESSOA_DIFERENTE_DE_PERSONA` | 1 | "Tomy Rohde" é **alter ego** de Fernando Giraldo |
| `PESSOA_DIFERENTE_DE_EMPRESA` | 1 | `@biocampojoyma` é a conta da **empresa** Bio Campojoyma |
| `SEM_ERRO_NA_SEED` | 2 | David Forge · Gilles Van Kempen |

As duas do meio são a lei do `ES-01717` aplicada à rede social: **a entidade que assina não
é necessariamente a entidade que se procura**. Fechar ativação com `@biocampojoyma` é
acordo B2B com uma produtora de 15 milhões de quilos de pimento — não contrato de
influencer com um produtor. Os dois podem interessar; **não são a mesma coisa**.

E `@evolovers` — o handle da seed — está **parado desde 2012-11-29**. A comunidade real
nasceu em 2020. Medir atividade ali teria produzido `DORMANT` para alguém que publica.

## D · ACTIVATION_READY POR PAÍS

**De 0 para 2.** E os dois só existem porque o handle foi corrigido **antes** de medir.

| país | região | cultura | creator | atividade |
|---|---|---|---|---|
| **IT** | Limena, Padova (Veneto) | MILHO (+alfafa, soja, forragem) | **Davide Gomiero** `@gomierofarm` | 6 posts/30d · 12/90d |
| **ES** | Níjar, Almería | PIMENTO, TOMATE, hortícolas | **Bio Campojoyma** `@biocampojoyma` | 1 post/30d · 7/90d ⚠️ conta de **empresa** |

Estado geral das 18 fichas: `ACTIVATION_READY` **2** · `PROMISING` **4** ·
`RESEARCH_NEEDED` **12**. Por país: IT 7 · FR 6 · ES 5.

`ACTIVATION_READY` significa **"o Marketing já consegue avaliar esta pessoa"** — não
"deve contratar", não "campanha aprovada".

## E · FARMER CREATORS PROVADOS

`ACTUAL_FARMER = PROVED`, com evidência própria e separada do papel de creator:

**Davide Gomiero** (IT, ~400 ha, 1.200 bovinos) · **Leonardo Leggieri** (IT, olivicultor
pugliês) · **Fernando Giraldo** (ES, olivarero, marca própria *Aceite de Tom*) ·
**Francisco J. Montoya** (ES, fundador da Bio Campojoyma) · **David Forge** (FR, 160 ha
cerealíferos) · **Gilles Van Kempen** (FR, grandes culturas).

## F · CREATORS POR CULTURA

| cultura | creators com `CROP_STATE ∈ {PROVED, PARTIAL}` |
|---|---|
| **MILHO** | Gomiero (IT) · Van Kempen (FR) |
| **TRIGO / CEREAIS** | Forge (FR) · Van Kempen (FR) |
| **OLIVO** | Leggieri (IT) · Giraldo (ES) |
| **HORTÍCOLAS / PIMENTO / TOMATE** | Montoya (ES) |
| **COLZA · CEVADA · SEMENTE DE CEBOLA** | Van Kempen (FR) |

## G · CREATORS POR REGIÃO

IT: Veneto (Limena/Padova) · Puglia. ES: Almería (Níjar) · Córdoba (La Carlota).
FR: Indre-et-Loire (Touraine) · Loiret. **Todas com fonte.**

## H · ATIVIDADE 30/90 DIAS — 28 perfis medidos, US$ 0,065

E o padrão é o achado, não o número:

| estado | n |
|---|---|
| `ACTIVE_RECENT` | 11 |
| `NOT_MEASURED` | 11 |
| `DORMANT` | 4 |
| `ACTIVE_STALE` | 2 |

> Entre os perfis **da seed italiana**, os que publicam com cadência alta e constante são
> os de **mídia de vinho e azeite** — `@doctor.wine` 11 posts/30d, `@italianwinelover` 10,
> `@giulia_sattin` 9, `@enoblogger` 7. Os perfis de **produção agrícola** estão dormentes
> (`@agromoderni` desde 2020, `@filippoballardin` desde fevereiro), inexistentes, ou
> estavam **no endereço errado**.

`NOT_MEASURED` nunca virou `DORMANT`: sem data de conteúdo o estado permanece
`NOT_MEASURED`, porque falha de leitura não é ausência de atividade.

## I · CASOS DE COLABORAÇÃO COM MARCAS — 7 pares nomeados

E **sete patrocinadores** do AgroInfluye 2026, por categoria:

| marca | categoria | tipo |
|---|---|---|
| **Seipasa** | *Tomatito* (TOMATE) | **crop protection** |
| **Syngenta** | *Embajador del AOVE* (OLIVO) | **crop protection** |
| Kuhn Ibérica | *Espiga Dorada* (CEREAIS) | maquinaria |
| FENDT | maquinaria agrícola | maquinaria |
| DEUTZ FAHR | vinho e cultivo da vide | maquinaria |
| ZOETIS | setor pecuário | saúde animal |
| ANAGAN | lenhosos: frutal, frutos secos, berries | a validar |

## J · CROP PROTECTION — os casos, e só os casos

| caso | marca | tipo de relação | mensagem |
|---|---|---|---|
| `#YoSoyAgricultor` (ES, 2020) | BASF Agro | `BRAND_COLLABORATION_PROVED` | imagem corporativa |
| *Tomatito* (ES, 2026) | Seipasa | `BRAND_ECOSYSTEM_SPONSORSHIP` | presença em evento |
| *Embajador del AOVE* (ES, 2026) | Syngenta | `BRAND_ECOSYSTEM_SPONSORSHIP` | presença em evento |
| Salon de l'Agriculture (FR, 2023) | Bayer | `PAID_PARTNERSHIP_PROVED` | imagem corporativa |

Os cinco tipos vivem num **`frozenset` sem índice**, e há teste proibindo dar-lhes ordem —
porque num contínuo *"a Syngenta patrocinou uma categoria"* vira, três leituras depois,
*"a Syngenta ativa produto com creators"*.

`PRODUCT_ACTIVATION_PROVED`: **nenhum caso** nos três países.

## K · MAPA DE CONCORRENTES

Observados: **BASF** (ES) · **Seipasa** (ES) · **Syngenta** (ES) · **Bayer** (FR).
Não observados nesta rodada: Corteva, FMC, UPL, Nufarm, Albaugh, Certis Belchim, LAINCO.
Não-concorrentes: Manitou × Jean-Baptiste De Wever · Kuhn · FENDT · DEUTZ FAHR · ZOETIS.

## L · HISTÓRICO ADAMA

`ADAMA_CREATOR_COLLABORATION = NOT_OBSERVED` em ES, IT e FR — **busca feita, nada
encontrado**. Não é `NOT_TESTED` e **não** é "a ADAMA nunca fez".

A colisão medida continua registrada: buscar *ADAMA embaixador* devolve **Adamo**, uma
operadora de telecom espanhola, em campanha com Jesús Calleja. Uma letra separa as duas.

## M · WHO COULD MARKETING CALL?

`WHO-COULD-MARKETING-CALL.json` — 18 fichas em `COUNTRY → REGION → CROP`, cada uma com:
creator · `ACTUAL_FARMER` · `WHY_RELEVANT` · `AUDIENCE_FIT_FOR_ADAMA` · atividade 30/90d ·
histórico de marca · conflito com concorrente · rota pública de contato ·
`ACTIVATION_STATE` · **`MISSING_PROOFS`** · evidência.

`MISSING_PROOFS` é o campo operacional: um `PROMISING` que diz
`RECENT_ACTIVITY_PROVED=FALTA` diz a alguém **o que buscar**. Um `PROMISING` sozinho manda
a pessoa de volta para a fila.

**Ordenação por ESTADO, nunca por seguidores** — e a razão está medida em N.

## N · RENDIMENTO POR PORTA (`VALID_CREATORS_PER_HUB`)

| porta | nomes até agora |
|---|---|
| BASF `#YoSoyAgricultor` | 6 |
| Seed do dono (ES) | 6 |
| AgroInfluye 2026 | 4 |
| Seed externa (IT) | 25 handles → **16 resolvidos**, 4 com handle errado, 3 não devolvidos, 2 ínfimos |

**Declarado:** os 66 nomeados do AgroInfluye **não** foram extraídos — as páginas do prêmio
não abrem (egresso bloqueado). `HUB_YIELD` mede o que a porta rendeu **até agora**, não o
que ela tem. 34 dos 43 hubs seguem `NOT_TESTED`, com `PEOPLE_EXTRACTED = 0`.

## O · ITÁLIA — veredito atualizado

`CROP_PROTECTION = NOT_OBSERVED_IN_MEASURED_CORPUS`.

**Não significa** `ITALY_DOES_NOT_USE_AGRICULTURAL_CREATORS` — a Itália usa, e está provado
neste mesmo documento (Regione Veneto recruta creators desde 2023; The Roman Farmer produz
para empresas do setor). Significa que **não se observou uso ligado especificamente a crop
protection dentro do corpus medido**.

## P · ESPANHA — veredito atualizado

`CROP_PROTECTION = PARTIAL`, agora com **três** casos e sustentação mais forte: duas das
sete categorias patrocinadas do AgroInfluye são de empresas de proteção de cultivo, e uma
delas (*Tomatito*/Seipasa) é **ligada a uma cultura**.

## Q · FRANÇA — veredito atualizado

`CROP_PROTECTION = PARTIAL` (Bayer, 2023). A lacuna de **cultura** fechou: dois creators
franceses com `CROP_STATE = PROVED`, ambos em **grandes culturas**.

Registrado como fato daquele caso, e **não** como causa geral do mercado: a creator
encerrou a parceria após repercussão pública. Não se infere disso por que a ativação de
produto não foi observada nos outros países.

## R · LACUNAS REAIS

1. **34 dos 43 hubs intocados**, `PEOPLE_EXTRACTED = 0`. Os TIER 1 (AgroInfluye, Cajamar,
   ASAJA/COAG/UPA Joven, EIMA, Enovitis, SITEVI, SIVAL, Innov-Agri) são a próxima porta.
2. **Os 66 nomeados do AgroInfluye** não extraídos — precisa da rota do runner.
3. **11 perfis com atividade `NOT_MEASURED`** — a rota não devolveu dado.
4. **Itália ainda sem snowball** a partir de EIMA / Enovitis / Fieragricola.
5. **`FIELD_VOICE` não iniciado** (§9 do briefing anterior).
6. **Nenhum mapa de pecuária** — Conor e outros criadores de gado ficaram deliberadamente
   fora do mapa de crop protection vegetal.
7. **Audiência não medida em ninguém**: `AUDIENCE_TYPE` segue `NOT_KNOWN` fora do caso
   Gomiero. Sem isso, `AUDIENCE_FIT_FOR_ADAMA` fica em `MEDIUM` por padrão.
8. **Só Instagram.** TikTok, YouTube e LinkedIn têm ator disponível e não foram usados.

## S · APIFY — custo e execuções

| métrica | valor |
|---|---|
| execuções desta missão | 7 |
| perfis coletados | 25 + 28 |
| **custo total** | **≈ US$ 0,13** |
| creators válidos resolvidos | 16 + 6 em fonte primária |
| **custo por perfil resolvido** | **≈ US$ 0,006** |
| duplicatas interceptadas | 1 (Lucía Casal, 2 rotas) |

---

## AS LEIS NOVAS DESTA RODADA

| # | lei | prova |
|---|---|---|
| 8 | ausência observada num corpus **não** é ausência no mercado | `AUSENTE_NO_CORPUS` + `ESTE_ESTADO_NAO_SIGNIFICA` + teste de frase |
| 9 | os cinco tipos de relação **não** são degraus | `frozenset` sem índice + teste |
| 10 | `ACTIVATION_READY` exige **seis provas**; marca e seguidores não estão entre elas | `provas_de_ativacao()` + 5 testes |
| 11 | quatro papéis, quatro campos, nenhum herdando do outro | teste de campo |
| 12 | fase desconhecida **não** cai em `contratos` | sai com código 2 |

**51 provas na missão · 368 na suíte · 0 falhas novas.**

**Casco não alterado. Arquitetura canônica não alterada.**
