# RELATÓRIO SOC2 — O CURATOR ENCAMINHA O YOUTUBE PARA O SCRAP

> Branch `curator-youtube-v1` a partir de `origin/social-prontidao-v1 @ ffef59cf` · 2026-09-23.
> Ordens: D17 (Scrap é do engenheiro; YouTube tal como o Scrap declara), D18 (LinkedIn A+B),
> D19 (Instagram continua POLICY_BLOCK), D20 (metadados da API com prazo de 30 dias).
>
> Serviço vivo NÃO tocado · Collection NÃO correu · nada na Sala · nada pago · nenhuma conta.
> Os livros da lane (fila, livro de estado, alocação, contratos, candidatas) NÃO foram escritos:
> conferido por md5 antes/depois de cada ensaio e de cada ronda de testes.
> Nenhum ficheiro do Scrap foi tocado (`coleta/scrap_*`, `coleta/adaptador_*`,
> `leis/social_matriz.py`, `sintonia-scrap.yml`, `fala_local.py`): o Curator só os LÊ.

```
CURATOR_YOUTUBE   = encaminha para o Scrap (teste: OQualifyDoYoutube, OContratoNomeiaOScrap)
CONTRATOS_50      = migrados no pacote G1, bloco 4 — ensaio em cópia: 1.ª passagem 50+50, 2.ª = 0
UC_NOVAS_8        = qualificadas 0 / NAO SEI 8 (território indeterminado pelo nome; 7 canais distintos)
LINKEDIN_B        = 44 sites medidos: 28 já colhidos · 9 conhecidos e parados no Curator · 7 já candidatos · 0 ausentes
INSTAGRAM         = não encaminhado (D19)
```

## 1. Curator → Scrap (`curadoria/worker.py`)

Antes: `etapa_qualify` devolvia `BLOCK/CAPABILITY` a TODA candidata YouTube («exige channel_id e
molde de video — capacidade com outro dono»). A capacidade existe no Scrap (fase `canal-youtube`,
`youtube.channel.discovery`, API oficial, matriz ALLOWED).

Agora, para uma candidata YouTube:

| Situação | Resultado | Porquê |
|---|---|---|
| endereço sem `/channel/UC…` (`@handle`, `/user/`, `/c/`, playlist) | `BLOCK/CAPABILITY`, «NAO SEI» | resolver pede a API com chave e rede; sem fabricar |
| canal que já tem SOURCE_ID (tabela, livro, alocação ou contrato escrito à mão) | `OK`, reusa o SOURCE_ID, **nenhum número novo**, nenhum BUILD_CONTRACT | um canal = uma fonte |
| canal ligado a 2+ SOURCE_ID | `BLOCK/SEMANTIC` | colisão de identidade: decisão humana |
| canal novo, território indeterminado | `BLOCK/SEMANTIC` (o caminho de sempre) | sem fabricar |
| canal novo, território decidido | aloca SOURCE_ID com `SOURCE_NATIVE_ID` = canal → `BUILD_CONTRACT` | circuito normal |

`BUILD_CONTRACT` de uma fonte YouTube escreve o molde novo `escrever_contratos.contrato_youtube_scrap`:
`ACQUISITION = {STRATEGY: SCRAP_FASE, EXECUTOR: scrap-colheita, FASE: canal-youtube,
FILTROS: {canal_id}, ROTA_DECLARADA_PELO_SCRAP, AUTORIZACAO: D17.4}`. O bloco é escrito por
`curadoria/rota_do_scrap_youtube.py`, que **lê** `scrap_colheita.FASES/NOMEADOS` e
`social_matriz.decisao` — nunca os escreve. O validador do Curator aceita `SCRAP_FASE` só se o
Scrap ainda declarar a rota HOJE (fase, capacidade, filtro, matriz ALLOWED, rota igual).

`VALIDATE_ROUTE` de uma rota do Scrap lê a matriz dele (não o robots — não há página) e **para em
`CANARY_PENDING`**: o canário desta rota é uma colheita do Scrap, com a chave do runner, e a régua de
promoção dos quatro passos é de HTML. `etapa_canary` recusa (`BLOCK/CAPABILITY`) se alguém a
enfileirar por outra porta. **Nenhum caminho promove YouTube a READY.**

Ensaio sobre as 71 candidatas YouTube reais (`curadoria/SOC2-QUALIFY-YOUTUBE-ENSAIO-V1.json`,
etapa real, lane redirecionada para pasta temporária):

| Resultado | n |
|---|---|
| OK — o canal já é uma fonte (reusa SOURCE_ID) | 28 |
| NAO SEI — sem channel_id no endereço | 35 |
| NAO SEI — território indeterminado (as UC novas) | 8 |

As 11 tarefas QUALIFY YouTube que estão **BLOCKED** na fila real com a frase antiga não voltam
sozinhas (ninguém chama `fila.recuperar_bloqueadas_por_defeito` em produção). O verbo existe:
`py curadoria/ensaiar_qualify_youtube.py --reabrir` — **não o corri**: toca a fila real; é para o
cutover, pelo dono do serviço.

## 2. Os 50 contratos YouTube — bloco 4 do pacote G1

`scripts/desbloqueio/aplicar_desbloqueio.py --rota-scrap=SOC2` (bloco novo, ledger `DECISAO = D17.4`):

* **livro do Curator**: `ACQUISITION` passa de `YOUTUBE_CHANNEL_FEED` (feed em `Disallow`) para
  `SCRAP_FASE`; os campos que descreviam o feed passam a descrever a rota do Scrap; o anterior fica
  em `ROTA_DO_SCRAP.ANTES`; `SOURCE_CONTRACT_HASH` recalculado pela fórmula do worker. A nota que o
  próprio contrato trazia — «só a ROTA de aquisição tem de mudar antes de coletar; rota permitida por
  medir: playlistItems.list» — é exactamente isto.
* **tabela do coletor**: ACRESCENTA `COLETADO_POR` (executor, fase, filtro). A `ACQUISITION` do motor
  fica como está (os testes do motor fixam-na; o motor não a usa mais para estas fontes).
* **só com prova**: canal do livro = canal da tabela = `SOURCE_NATIVE_ID`; `IDENTITY_MATCH = YES` na
  sondagem de 20/09; o canal é de UMA só fonte na casa; o Scrap declara a rota hoje.
* **invariantes**: nunca muda SOURCE_ID, TERRITORY, BATCH_ID nem o canal; na tabela só `COLETADO_POR`;
  `COLETADO_POR` sem autorização do bloco → exit 4.

Ensaio em cópia (`scripts/desbloqueio/ENSAIO-SOC2-BLOCO4-V1.json`): **1.ª passagem 50 livro + 50
tabela APLICA; 2.ª passagem 0.** Os livros da árvore NÃO foram escritos: o pacote aplica-se uma vez,
no cutover, com os blocos 1-3 que ainda estão por aplicar nesta linha.

**Coletor JS** (`coleta/italy_pilot_collect.mjs`): medido — hoje, uma destas 50 fontes admitida
fazia `alvosDoContrato` lançar «ADAPTER_ID não está no registry», e como a rodada não apanha
exceções, **uma fonte derrubava a corrida inteira**. Com `COLETADO_POR` (passado pela
`contratoGenerico`, `regras/italy_contracts.mjs`), `alvosDe` devolve
`COLETADO_POR_OUTRO_EXECUTOR: scrap-colheita/canal-youtube` — um resultado por fonte. Hoje nada
disto corre: o portão só admite READY, e as 50 não são.

## 3. MISSING_ROUTE que ficam (e de quem são)

1. **Pedido → Scrap para estes territórios (PEDIDO/ORQUESTRADOR).** `pedido/receitas.py` escolhe o
   executor pelo TERRITÓRIO; `scrap-colheita` só está registado em T8/T9. Das 50, **44** estão em
   T2/T5/T7/T10/T11/T12 → `fase=canal-youtube` dá `FILTRO_NAO_CONSUMIDO`. Proposta: o `resolver` ler
   `COLETADO_POR` da fonte nomeada. Não fiz — é código do orquestrador e o engenheiro está a ligar as
   portas do Scrap (`scrap-portas-v1`); coordenar antes.
2. **Chave no workflow das fases** (SOC1): é do engenheiro.
3. **Régua de promoção para YouTube (CURATOR, proposta)**: READY de uma fonte `SCRAP_FASE` = existe
   envelope do Scrap com `SOURCE_ID` desta fonte, ≥ 1 unidade `COLHEITA` com `VIDEO_ID` e `PUBLISHED_AT`.
   Hoje fica em CANARY_PENDING, dito.
4. **8 UC novas**: 7 canais distintos (CAND-0332 e CAND-0335 são o mesmo). Proposta, NÃO aplicada:
   herdar o território da fonte do SITE da mesma organização quando o site declara o canal (ex.:
   Olio Officina → `olioofficina.it` = IT-T5-046). É regra nova de identidade — decisão, não
   engenharia (a lição de «QUALIFY pela amostra fabrica território» vale aqui).
5. **35 @handle**: esperam `youtube.channel.resolve` (API, chave, rede).

## 4. LinkedIn A+B (D18) — `curadoria/linkedin_pelo_site.py`

O site de cada uma das 44 vem da própria ficha (`ONDE_VIU`: «declarado no site oficial do dono»),
comparado por host exato (o Atlas liga host → SOURCE_ID; subdomínio diferente NÃO conta):

| Estado do site | n |
|---|---|
| já na tabela do coletor (colhido) | 28 |
| tem contrato no Curator, parado (READY 2, CANARY_PENDING 1, CONTRACTED_CANARY_FAILED 2, CAPABILITY_BLOCK 2, CONTRACT_READY_ROUTE_BLOCKED 1) | 8 |
| só no Atlas, sem contrato (IT-T7-038 Valpolicella, CAPABILITY_BLOCK) | 1 |
| já é candidata na porta | 7 |
| ausente → candidatar | **0** |

Nada a candidatar: a ferramenta tem `--escrever` (chama `fonte_nova.registar`, idempotente) e hoje
faria 0. As 2 READY sem linha na tabela (IT-T5-041 crpv, IT-T7-050 coldiretti) são o caso conhecido
«elegível sem contrato é do livro» (IT-T5-041 é a da D10, condição 4).

## 5. D20 — onde vive o prazo de 30 dias (MEDIDO, PROPOSTO, não feito)

Medido:
* Developer Policies III.E.4 (texto e sha256 em `candidatas/PROVA-TERMOS-SOC1-V1.json`): dado da API
  guardado no máximo 30 dias, depois apagar ou refrescar.
* `raw_asset` não reescreve a identidade (trigger `a_identidade_da_observacao_nao_se_reescreve`,
  migração 027); `preserved` e `not_preserved_reason` **podem** mudar. O derivado aponta para o raw com
  `on delete restrict` (022). Logo, «apagar a linha» choca com a lei da casa; **apagar os bytes e deixar
  a lápide** não choca.
* Nada no código conhece o prazo (`30 calendar days` = 0 fora da prova dos termos).

Proposta (dono: Collection/Storage — não o Scrap, que só colhe):
1. a regra lê-se pela PROVENIÊNCIA: observação cuja rota é `youtube-data-api-v3:*`;
2. todo dia: o que tem `captured_at` < agora − 30 dias → nova colheita (observação NOVA) e, depois,
   os bytes da antiga saem do Storage, com `preserved=false`,
   `not_preserved_reason='YOUTUBE_API_III_E_4_30D'`; o mesmo para o derivado e para a linha da Sala;
3. prova em runtime: `count(*) where rota youtube-data-api-v3 and captured_at < now()-'30 days' and
   preserved` = **0**, no portão diário;
4. áudio e transcrição locais (`yt-dlp:public_audio` + ASR) NÃO entram: não são «API Data» (D20).

## 6. JSON social → DERIVED e resposta crua → RAW (MEDIDO, PROPOSTO, não feito)

* A observação social entra como `application/json`; nenhum derivador a aceita
  (`ingresso.executor_para`: pdf, mídia, html) → DERIVED = NOT_APPLICABLE, e a Admissão lê o texto do
  envelope. Proposta: um dono de derivação para `application/json` social que escreva o texto
  (título + descrição) como derivado com `raw_asset_id`.
* A resposta crua da API (páginas de `playlistItems`/`videos`) não chega a `raw_asset`
  (`SCRAP_RAW_NAO_RECEBIDO`). Proposta: preservá-la como RAW da corrida, com o mesmo prazo de 30 dias.
* **Não mexi**: o engenheiro está a pôr o ASR no DERIVED; dois donos no mesmo ficheiro ao mesmo tempo
  é o erro que a casa já pagou. Coordenar pelo WRITESET abaixo.

## WRITESET (o que esta missão escreveu)

| Ficheiro | O quê |
|---|---|
| `curadoria/worker.py` | QUALIFY YouTube; BUILD_CONTRACT YouTube; VALIDATE_ROUTE/CANARY da rota do Scrap; alocação guarda o canal; `BUILD_CONTRACT` lê a alocação pelo mesmo `ALLOCATION` que o QUALIFY escreve |
| `curadoria/rota_do_scrap_youtube.py` (novo) | leitura da rota do Scrap do lado do Curator |
| `curadoria/escrever_contratos.py` | molde `contrato_youtube_scrap` |
| `curadoria/validar_contratos.py` | estratégia `SCRAP_FASE` |
| `scripts/desbloqueio/aplicar_desbloqueio.py` | bloco 4 + invariantes |
| `regras/italy_contracts.mjs` | passa `COLETADO_POR` ao contrato |
| `coleta/italy_pilot_collect.mjs` | guarda `COLETADO_POR`; `alvosDe` exportada para o teste |
| `curadoria/linkedin_pelo_site.py`, `curadoria/ensaiar_qualify_youtube.py` (novos) | D18-B e ensaio |
| `curadoria/test_soc2_curator_youtube.py` (novo), `curadoria/test_collection_gate.py` | 29 testes; o teste novo declarado TEST_ONLY |
| provas JSON | `SOC2-LINKEDIN-PELO-SITE-V1`, `SOC2-QUALIFY-YOUTUBE-ENSAIO-V1`, `ENSAIO-SOC2-BLOCO4-V1` |

NÃO escrito: livros da lane, candidatas, Scrap, workflows, `pedido/`, `supabase/`.

## TESTS · MUTATION

* `curadoria.test_soc2_curator_youtube`: **29 OK**.
* Vizinhos (17 módulos, 246 testes) medidos na base `ffef59cf` e na branch, **comparados por nome**:
  base 3 falhas; branch as mesmas 3 + 1 nova (o teste novo não estava classificado no guarda de
  caminhos até ao coletor) → classificado TEST_ONLY → 0 novas.
* JS: `motor_de_rota_test` 47/0, `paridade` 32/0, `recollection` 31/0, `incrementalidade` 26/0 nas duas;
  `italy_contract_test` 349/76 nas duas, **as mesmas 76 por nome** (pré-existentes).
* Mutação: **26 ataques, 26 mortos** (2.ª ronda; na 1.ª sobreviveram 3 — VALIDATE sem conferir,
  FASE_EXISTE redundante na mensagem, subdomínio — ganharam testes e morreram). Cópia fora do repo,
  `.pyc` apagado a cada ataque, md5 conferido no fim.
