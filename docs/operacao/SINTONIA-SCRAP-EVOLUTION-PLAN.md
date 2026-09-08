# PLANO DE EVOLUÇÃO — SINTONIA SCRAP

> Ordem incremental. **Sem big bang. Nada é removido.**
> Cada passo tem: o que muda · o que prova · o que NÃO faz.
> Base: `docs/decisoes/ADR-SINTONIA-SCRAP-EVOLUTION.md`.

---

## AS CINCO MUDANÇAS DE MAIOR GANHO COM MENOS CÓDIGO

Em ordem de retorno por linha.

| # | Mudança | Tamanho | Ganho |
|---|---|---|---|
| **1** | Extrair a taxonomia de falha de `apify_pool` para `falhas.py`, neutra de rota | ~60 linhas movidas | **Coletor quebrado passa a ser NOTADO em vez de virar "a fonte está vazia"** — em toda rota, não só na paga |
| **2** | Legenda-primeiro na mídia | ~40 linhas | Deixa de pagar transcrição por texto que já existe. **~1000× por vídeo com legenda** |
| **3** | Ligar `coleta_checkpoint` e `source_health` (já existem, já testados, órfãos) | ~0 linhas novas | Retomada depois de reboot e detecção de fonte parada, de graça |
| **4** | Absorver os três dicts `ATORES` em linhas de `social_matriz` | ~80 linhas movidas | **Uma única fonte de verdade de rota.** Fim do resolvedor escrito como `if` |
| **5** | `feedparser` + `trafilatura` para imprensa técnica IT | 2 deps, ~120 linhas apagadas | Rota livre, sem anti-bot, incremental de graça por `ETag` |

**As três primeiras não adicionam nenhuma dependência e não tocam em nada que funciona.**

---

## PASSO 0 · ACEITAR O ALVO *(decisão humana, zero código)*

Ler `SINTONIA-SCRAP-TARGET.md`. Aceitar, corrigir ou recusar as três leis:
`PERMITIDA → BARATA → CAPAZ` · parse é função pura · um bit separa "o site disse não" de
"nosso parser quebrou".
**Sem isso, todo passo abaixo é chute.**

---

## PASSO 1 · CONTRATO COMUM DE FALHA  ← **a primeira missão de código**

**Muda:** nasce `scripts/falhas.py` com a taxonomia neutra de rota
(`PLATFORM_FAILURE` / `ROUTE_FAILURE` / `AUTH_FAILURE` / `QUERY_FAILURE` /
**`PARSER_FAILURE`** / `LIBRARY_STALE` / `ROUTE_NOT_ALLOWED` / `BUDGET_EXHAUSTED`),
com a flag `esperado` e a regra `ROTACIONAM` / `NAO_ROTACIONAM`.
`apify_pool` e `social_rotas` passam a **importá-la**.

**Prova:** o teste existente de `apify_pool` continua verde sem alteração de
comportamento; e um teste novo mostra que uma falha de parse na rota **grátis** é
classificada `PARSER_FAILURE, esperado=False`.

**NÃO faz:** não muda uma linha de coleta, não mexe em Supabase, não toca no workflow.

---

## PASSO 2 · LIGAR OS ÓRFÃOS

**Muda:** `social_scrap` passa a usar `coleta_checkpoint` (retomada) e `source_health`
(contrato de fonte). `source_health` ganha o segundo eixo, `ROUTE_HEALTH`.

**Prova:** matar o processo no meio do piloto e reexecutar → **retoma de onde parou, sem
recoletar o que já veio**. E uma quota esgotada aparece como
`SOURCE=HEALTHY / ROUTE=UNAVAILABLE`, não como fonte morta.

**NÃO faz:** não generaliza ainda o estado do `instagram_diario`.

---

## PASSO 3 · MÍDIA COMO DERIVAÇÃO, COM LEGENDA PRIMEIRO

**Muda:** `instagram_transcrever.py` → `midia_derivar.py`, neutro de plataforma.
Entrada: **referência de mídia**. Ordem: `legenda existente → só áudio → whisper local`.
O miolo bom fica intacto (idioma **declarado** pelo país; teto de tempo 6×; lote 8).

**Prova:** um objeto com legenda **não** baixa mídia nenhuma. Um sem legenda baixa **só
áudio**, nunca o fluxo de vídeo. Medir os dois caminhos e registrar o custo evitado.

**NÃO faz:** não apaga `instagram_transcrever.py` — vira casca fina que chama o novo.

---

## PASSO 4 · REGISTRO ÚNICO DE ROTA

**Muda:** os três dicts `ATORES` viram linhas de `social_matriz` com a **união** dos
campos que cada um descobriu sozinho: `executor`, `build`, `teto_usd`, `verificacao`,
`rota_alternativa`. O `if` de reserva em `sensor_coleta.py:711` vira **dado**.

**Prova:** `social_matriz.resumo()` lista rota paga e grátis lado a lado, e
`gap_apify()` fica correto pela primeira vez. Os coletores antigos continuam rodando.

**NÃO faz:** não reescreve `comunicacao_coleta`, `sensor_coleta` nem `instagram_coleta`.

---

## PASSO 5 · APIFY VIRA UMA ROTA ATRÁS DO RESOLVER

**Muda:** `coletor.executar()` é **embrulhado** como `executor_apify` e passa a ser
alcançado **pelo** `social_rotas`, sujeito às mesmas cinco perguntas
(permitida? capaz? saudável? tem credencial? cabe no orçamento?).

**Prova:** um pedido de capacidade que tem rota grátis permitida **nunca** chega na Apify.
Um que só tem rota paga chega, **com teto**, e o gasto sai no manifesto.

**NÃO faz:** **não remove o fallback pago.** Não toca no `contrato_ator`.

---

## PASSO 6 · RATE POLICY DE TRÊS EIXOS

**Muda:** `PAUSA_ENTRE_CHAMADAS = 1.0` vira política:
(1) cortesia por domínio, de posse do resolver; (2) **orçamento por identidade**
(plataforma, conta), proativo, com backoff separado no 429 e pontuação que aposenta a
sessão **antes** do banimento; (3) teto global por execução.
Regras: **4xx nunca é retentado**; rotação de sessão conta **separado** de retentativa.

**Prova:** um 429 simulado contra servidor **local** produz o backoff certo, e o teto
global interrompe a execução em vez de queimar a conta.

---

## PASSO 7 · FIXTURES E CANÁRIA

**Muda:** uma fixture de payload por plataforma (hoje: **1** para 30 arquivos de teste).
Roteamento de URL testado 100% offline. Nasce um workflow de canária, **em agenda separada
da coleta**, com um punhado de URLs públicas estáveis por adaptador:
`FETCH → CONTRATO DE FORMA` (presença, tipo, faixa) **+ asserção estatística sobre o lote**.

**Prova:** quebrar um seletor de propósito → a canária acusa `SOURCE_DRIFT` **antes** de
qualquer coleta grande.

**NÃO faz:** **não** constrói suíte de cassete VCR para a camada de busca — resposta
gravada que não bate mais com o site vivo é pior que teste nenhum.

---

## PASSO 8 · IMPRENSA TÉCNICA COM `feedparser` + `trafilatura`

**Muda:** duas dependências pequenas; a cauda longa de site de notícia agrícola IT deixa
de precisar de parser por site. `ETag`/`If-Modified-Since` dão incremental de graça.

**Prova:** o número de linhas **apagadas** é maior que o peso trazido. Se não for,
**o passo é revertido** — é a regra do ADR-19.

---

## PASSO 9 · SESSÃO LOCAL AUTENTICADA *(só quando Instagram entrar de verdade)*

**Muda:** Playwright entra **só aqui**. Dois níveis: um perfil `user_data_dir` de longa
vida por (plataforma, conta) para o ritual de login, exportado para um `storage_state` de
vida curta por execução. Rota barata primeiro: **`page.on('response')`** para colher o
JSON que a própria página busca; DOM só como reserva.

**Segurança, sem negociação:** `storage_state` é **credencial ao portador**.
Nunca no Git. Nunca em artefato do Actions. ACL restrita no NTFS. DPAPI em repouso.
Conta **descartável**, nunca a principal. Pré-voo estilo `cookies_check` **antes** do
trabalho — falhar alto com "sessão vencida" em vez de devolver 200 resultados vazios.

**NÃO faz:** não substitui `cdp.py` nas rotas públicas — ele funciona e não tem dependência.

---

## PASSO 10 · PRIMEIRA PLATAFORMA NOVA, PELO CONTRATO

**Muda:** acrescentar uma plataforma = **uma função `collect()` + uma linha na matriz**.
**Prova:** se exigir tocar em mais de dois arquivos, **o contrato falhou** e o passo para.

**Qual primeiro, depois da reorganização:** **YouTube pela Data API oficial**.
Motivo: é onde está 96% do gasto Apify histórico, é a maior massa de vídeo agrícola
italiano, e a rota permitida é a oficial. **`CREDENTIAL_MISSING` é o bloqueio real —
conseguir a chave da Data API v3 é tarefa, não otimização.**

---

## PASSO 11 · `StreamExecutor` *(quando remoção e edição importarem)*

**Muda:** a segunda forma de executor — conexão longa, cursor persistido, reconexão com
backoff, recebendo `create`/`update`/**`delete`**. Bluesky/Jetstream é o caso de prova:
grátis, aberto, e a única plataforma com evento de remoção **e** edição em tempo real.

**Fato operacional:** **GitHub Actions é hospedeiro ruim para isto** (teto de 6h por job).
Quer ser serviço no PC local, com reinício programado e cursor persistido.
**É outra forma de runtime.**

---

## PASSO 12 · REABRIR A DECISÃO SOBRE CRAWLEE

**Gatilho, não calendário:** só quando existir workload de volume real (≥500 URLs em fila,
com retomada obrigatória) **e** os passos 1-7 já estiverem em pé.

**O piloto precisa responder duas perguntas, e só duas:**
1. A conversão para asyncio custa **menos** do que manter o equivalente à mão?
2. Os wheels de `impit` (Rust compilado) instalam limpo no Python exato dos runners Windows?

**Se qualquer resposta for não: fica como está.** Os padrões já foram copiados de graça
nos passos 2, 6 e 7 — que é onde estava a maior parte do valor.

---

## MÉTRICAS DO SCRAP

Sem Prometheus. JSON no repositório, ao lado do que já existe.

`REQUESTS` · `DISCOVERED` · `FETCHED` · `FAILED` · `BLOCKED` · `ROUTE_NOT_ALLOWED` ·
`AUTH_REQUIRED` · `RATE_LIMITED` · `RETRIED` · `NEW` · `REUSED` · `MEDIA_FOUND` ·
`CAPTION_AVAILABLE` · `TRANSCRIBED_LOCAL` · `BYTES` · `ELAPSED` · `ROUTE` · `COST` ·
`APIFY_COST`

Três derivadas que dizem se o plano está funcionando:
- **`APIFY_COST / COST`** → tem de cair. Meta: ≤5%.
- **`CAPTION_AVAILABLE / MEDIA_FOUND`** → mede a economia do passo 3.
- **`PARSER_FAILURE / FAILED`** → mede deriva. Se subir, uma rede mudou.

---

## NO SYSTEM MAP

`SINTONIA SCRAP` = **EXECUTOR COMPOSTO**.
Raio-X: `CAPABILITY REGISTRY` · `ROUTE RESOLVER` · `ADAPTERS` · `AUTH` · `QUEUE` ·
`MEDIA` · `HEALTH` · `RUN`.
Estado por adaptador: `PROVED` / `POSSIBLE_NOT_PROVED` / `BLOCKED` / `ROUTE_NOT_ALLOWED` /
`CREDENTIAL_MISSING` / `SOURCE_DRIFT`.

---

## O QUE FICA ONDE

| Camada | O quê |
|---|---|
| **GitHub Actions** | **burro.** Agenda, entrega o pedido, devolve o resultado ao repositório. Nunca a árvore `if Instagram / if YouTube / if TikTok`. Teto de 6h **impede** fluxo longo |
| **PC Windows local** | navegador com perfil autenticado, ffmpeg, faster-whisper, yt-dlp, cache de download, IP residencial italiano, `StreamExecutor` |
| **Supabase** | estado operacional canônico: objeto, evidência, marca d'água, saúde de rota, custo, execução |
| **Repositório** | matriz de capacidade, contrato, régua, canária, ledger |

> **O estado canônico não pode depender de "esse arquivo está perdido em `C:\Users\...`".**
> O PC local é onde o trabalho acontece. **Não é onde a verdade mora.**
