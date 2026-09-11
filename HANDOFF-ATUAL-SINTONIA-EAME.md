# HANDOFF ATUAL — SINTONIA EAME

**Atualizado em 2026-09-10.**

Este arquivo é o handoff operacional curto para retomar o trabalho sem reabrir decisões já fechadas. O repositório continua sendo a autoridade final: se este texto divergir do código, migrations, provas ou documentos canônicos, **o repositório vence** e a divergência deve ser reportada.

---

## 1. ONDE ESTAMOS AGORA

### Linha de trabalho ativa

- **Branch funcional:** `claude/raw-observation-identity-3jbwco`
- **HEAD observado no GitHub ao gerar este handoff:** `09277bf89c0d9a28324fa7681e437b5e5e094b67`
- **Último commit funcional antes da regeneração do mapa:** `cb8e0968c27ba48aeb88d9ee5151c0c852bc7c3d`
- `09277bf` é uma **regeneração mecânica da cadeia canônica do System Map** após `cb8e096`; não representa nova decisão arquitetural.

### Linha de know-how

- **Branch:** `claude/sintonia-eame-know-how-v1`
- Esta branch existe para preservar handoffs e know-how. **Não é a branch de implementação.**

### Foco atual

Estamos fechando a **fundação canônica da Collection**, especificamente a identidade entre:

`RUN → RAW OBSERVATION → STORAGE OBJECT → DERIVED → STRUCTURED → ADMISSION → READY`

O portal/casco não é o foco. A ordem permanece:

**réguas → coleta → ferramentas → casco por último**.

---

## 2. FUNDAÇÃO QUE NÃO DEVE SER REABERTA

Estas decisões estão fechadas e só podem ser reabertas diante de contraexemplo reproduzível ou incompatibilidade concreta do repositório:

1. `RAW_OBSERVATION_ID = raw_asset.id` surrogate estável.
2. `RUN ≠ OBSERVATION ≠ CONTENT ≠ STORAGE OBJECT`.
3. `SHA256` identifica bytes/conteúdo, **não** observação.
4. `storage_path` identifica/endereço o storage object, **não** a observação.
5. Retry da **mesma RUN**, mesma fonte, mesmo documento e mesmos bytes deve reutilizar a observação lógica.
6. **Nova RUN** sobre o mesmo documento e os mesmos bytes deve criar **nova observação**.
7. `SOURCE_ID` é o código textual canônico da Collection, por exemplo `IT-T2-002`; **não** é `public.fonte_externa.id` bigint.
8. `DOCUMENT_KEY` só usa identidade documental quando o contrato da fonte realmente prova `DOCUMENT_ID`.
9. Hash **não é mais fallback silencioso de identidade documental**. A especificação mais recente revogou o antigo `CONTENT_DERIVED` como base válida de `DOCUMENT_KEY` para o estado identificado.
10. Histórico não pode ser “corrigido” inventando `SOURCE_ID`, `DOCUMENT_ID`, `DOCUMENT_KEY`, país, data ou qualquer outra identidade não provada.
11. `SOURCE_LOCATION ≠ FACT_LOCATION`.
12. `FACT_TIME ≠ PUBLICATION_TIME ≠ OBSERVED_TIME ≠ COLLECTED_TIME`.
13. Ausência continua `UNKNOWN/NÃO SEI`; nunca inferir silenciosamente.

---

## 3. B5 — OBJETO FÍSICO X OBSERVAÇÃO

O defeito original era estrutural: `raw_asset` dizia representar observação, mas `unique(storage_path)` o forçava a comportar-se como storage object.

### B5A — fases 1–6

Já implementadas por `supabase/migrations/025_o_objeto_ganha_casa.sql`.

O que ficou estabelecido:

- existe `public.storage_object`;
- `storage_object` tem grain de uma cópia física em um endereço;
- `storage_path` é chave única do storage object;
- `sha256` **não** é unique em storage object;
- `raw_asset.storage_object_id` liga observação ao objeto físico;
- `raw_asset.id` foi preservado;
- FK de derived para `raw_asset(id, sha256)` permaneceu intacta;
- `preserved=true` exige storage object ligado;
- writer recebeu adaptação mínima para criar/ligar storage object antes da observação.

**Importante:** B5A não resolveu nova RUN sobre o mesmo `storage_path`, porque `unique(raw_asset.storage_path)` ainda existe por desenho. Isso só pode ser removido depois de a identidade forward estar protegida.

---

## 4. B5B — fases 7–9: ESTADO ATUAL

**Ainda não foram implementadas em migration/runtime.**

O commit funcional mais recente, `cb8e096`, foi uma correção da especificação contra PostgreSQL 16 descartável. Ele fechou três bloqueios que tinham aparecido na revisão:

### Bloqueio 1 — forward sem fonte real

Um estado forward não pode escapar carregando `source_id` sentinela como `NAO_SEI`.

Regra corrigida: **todo estado que não seja `LEGACY_PRE_IDEMPOTENCY` precisa de fonte real**, usando o vocabulário de sentinelas já medido no repositório.

### Bloqueio 2 — `CONTENT_DERIVED`

A ordem antiga que aceitava `CONTENT_DERIVED` foi revogada/superseded. Não deixar duas regras executáveis contraditórias no documento.

### Bloqueio 3 — corte do legado por tempo

`created_at` foi reproduzido e **reprovou** como fronteira de legado, porque `now()` em PostgreSQL é `transaction_timestamp()` e uma transação antiga pode inserir depois do corte carregando um timestamp anterior.

A solução especificada e testada usa o surrogate:

- `ACCESS EXCLUSIVE` no início da fase de classificação;
- congela `max(raw_asset.id)` sob lock;
- ids até o corte recebem estado legado;
- writes concorrentes esperam ou são vistos antes do corte;
- depois a coluna de estado pode tornar-se obrigatória.

O commit reporta dois cenários concorrentes reproduzidos em PostgreSQL 16.13 e uma bateria final de **27 casos** com veredito esperado.

### Estado que continua aberto

`PHASE_10_UNPROVEN_GATE` continua **não resolvido**.

O índice parcial da fase 9 não protege observações `FORWARD_IDENTITY_UNPROVEN`. Hoje isso ainda não abre duplicação física porque `unique(raw_asset.storage_path)` permanece. Portanto:

- isso **não bloqueia automaticamente fases 7–9**;
- isso **bloqueia autorizar fase 10 sem uma decisão/prova adicional**.

Nunca confundir “B5B pronto para ser implementado” com “fase 10 autorizada”.

---

## 5. IDENTIDADE FORWARD — CONTRATO A PRESERVAR

### RUN_ID

- pertence à corrida criada pelo orquestrador antes do executor;
- o writer já recebe/persiste `run_id`;
- não criar segundo dono nem gerar novo RUN_ID no writer.

### SOURCE_ID

- autoridade = cadastro textual da Collection;
- exemplo: `IT-T2-002`;
- já existe upstream em `coleta/ingresso.py` / artefato de coleta;
- o gap medido era de **wiring** até o RAW writer, não de definição da identidade;
- nunca reconstruir SOURCE_ID a partir de URL, slug, owner, caminho ou `fonte_externa.id`.

### DOCUMENT_KEY

A especificação mais recente deve ser lida no documento canônico antes de implementar. Não ressuscitar uma regra revogada.

Princípio atual:

- documento identificado: identidade vem de `DOCUMENT_ID` semanticamente válido e provado pelo contrato da fonte;
- ausência de identidade documental provada não pode ser convertida silenciosamente em “documento identificado pelo hash”;
- estados forward precisam separar **identidade provada** de **identidade documental não provada**.

### Idempotência

Para observações forward identificadas, a distinção lógica continua baseada em:

`RUN + SOURCE + DOCUMENT + CONTENT`

Consequência essencial:

- mesma RUN + mesma identidade + mesmos bytes = retry/reuse;
- RUN diferente + mesma fonte/documento/bytes = observação diferente.

Mas **reconhecer chaves diferentes não significa ainda conseguir persistir as duas observações** enquanto `unique(raw_asset.storage_path)` existir.

---

## 6. SYSTEM MAP

Lei permanente:

- o mapa mostra o sistema; **não decide a arquitetura**;
- generated JSON é sempre mecânico;
- nunca editar `*.generated.json` à mão;
- nunca usar `--stamp` para mascarar árvore desatualizada;
- qualquer source tracked que altere a árvore exige regeneração pela cadeia canônica quando aplicável.

O HEAD `09277bf` regenerou a cadeia na ordem declarada:

`scan_repo → scan_sources → scan_casco → censo_da_coleta → pente_fino_da_coleta → censo_dos_buracos → generate_system_map`

O commit registra que alguns artefatos gerados carregavam provenance antiga porque rodadas anteriores haviam executado apenas parte da cadeia. O conteúdo semântico não mudou; a provenance foi atualizada mecanicamente.

Não herdar o estado dos checks de memória. **Remeça os checks no HEAD atual.**

---

## 7. REGRAS DE TRABALHO PARA A PRÓXIMA ABA

- Antes de qualquer conclusão sobre estado: `fetch`, branch, HEAD, status, log.
- Separar **fato medido** de inferência.
- Sem base: `NÃO SEI / precisa medir`.
- Não abrir auditoria repo-wide sem bloqueio concreto.
- Missões pequenas: **medir → decidir/implementar → hard stop**.
- Não criar arquitetura paralela para resolver detalhe local.
- `ONE CONCEPT → ONE OWNER`.
- `COLETAR ≠ ADMITIR ≠ JULGAR`.
- `RAW ≠ DERIVED ≠ STRUCTURED ≠ ADMISSION ≠ READY`.
- `MODULE EXISTS ≠ EDGE EXISTS ≠ FLOW EXISTS`.
- `CAN DO ≠ DID DO`.
- `DECLARED EDGE ≠ OBSERVED EDGE`.
- `ERROR ≠ REJECTED ≠ UNKNOWN ≠ NOT_RUN ≠ REUSED`.
- Intelligence pode pedir Collection Gap; não chama collector diretamente.
- Cards do System Map refletem runtime real, não arquitetura desejada.
- Sem portal/frontend/deploy durante esta fundação, salvo ordem explícita do usuário.

---

## 8. PRÓXIMO PASSO EXATO

A próxima aba **não deve começar implementando fase 10**.

Primeiro deve revisar criticamente o estado final de `cb8e096` + regeneração `09277bf` e responder:

1. os três bloqueios realmente ficaram fechados no documento canônico sem ordem contraditória sobrevivente?
2. o estado forward não consegue escapar silenciosamente por `NULL`/sentinela?
3. a fronteira de legado por surrogate + lock está especificada de forma implementável e compatível com os writers reais?
4. `CONTENT_DERIVED` está realmente revogado em todos os trechos executáveis da especificação?
5. o `PHASE_10_UNPROVEN_GATE` está explicitamente preservado como bloqueio futuro, sem ser resolvido por suposição?
6. quais checks estão verdes/vermelhos no HEAD atual, separando falhas preexistentes de regressões desta linha?

Se e somente se não houver bloqueio real, a próxima missão bounded é:

**`C-IMPL-B5B — implementar apenas fases 7–9`**

Ainda sem fase 10, sem remoção de `unique(raw_asset.storage_path)`, sem fase 11, sem portal.

Depois da implementação B5B deve existir uma rodada separada de prova/revisão antes de qualquer autorização destrutiva.

---

## 9. COMO REVISAR ENTREGAS DO CLAUDE

Fluxo combinado:

1. Claude Opus 5 executa a missão bounded.
2. Revisão independente procura apenas bloqueios reais, sem redesenhar arquitetura.
3. Verificação no GitHub confirma branch, HEAD, diff, migrations, provas, mapa e checks.
4. Veredito final: **PASS / PARTIAL / FAIL**.
5. Só então emitir o próximo prompt inteiro.

Pontos de revisão prioritários nesta linha:

- estabilidade de `raw_asset.id`;
- compatibilidade dos writers;
- diferença entre retry e reobservação;
- impossibilidade de histórico inventar identidade;
- forward não escapar de constraints por NULL/sentinela;
- índice parcial não prometer mais do que protege;
- prova real em PostgreSQL descartável quando a semântica depende do banco;
- nenhuma fase posterior entrar escondida no mesmo commit.

---

## 10. SINTONIA SCRAP — FRONTEIRA CANÔNICA PARA NÃO CRIAR UM SEGUNDO CÉREBRO

Esta seção registra o caminho arquitetural que deve ser preservado nos próximos prompts e implementações do **SINTONIA SCRAP**.

### Autoridade superior

A autoridade continua sendo a `BIBLIA-CANONICA-DA-COLETA.md`, especialmente o princípio de **um único dono da orquestração**.

O SINTONIA SCRAP **NÃO É** o orquestrador geral da coleta e **NÃO DEVE** competir com `orquestrador/orquestrador.py` pela pergunta global:

> `COMO ATENDER ESTE COLLECTION_REQUEST?`

Essa pergunta pertence ao **ORQUESTRADOR CANÔNICO DA COLETA**.

O SINTONIA SCRAP entra **abaixo dele**, como executor/família especializada em aquisição social, web e mídia.

### Caminho obrigatório

```text
SINTONIA — COLETA
        │
        ▼
COLLECTION_REQUEST
        │
        ▼
ORQUESTRADOR CANÔNICO DA COLETA
orquestrador/orquestrador.py
        │
        ├── outros executores
        │
        └── SINTONIA SCRAP EXECUTOR
                 │
                 ▼
        SCRAP ADAPTER ROUTER / DISPATCHER
                 │
                 ├── Instagram Adapter
                 ├── Facebook Adapter
                 ├── LinkedIn Adapter
                 ├── X / Twitter Adapter
                 ├── YouTube Adapter
                 ├── Web Adapter
                 ├── TikTok Adapter, se comprovado útil
                 ├── Podcast / Audio Adapter, se comprovado pertinente
                 └── outros adapters que fizer sentido absorver
                         │
                         ▼
                    PROVIDERS
                         │
                         ▼
              RAW + DERIVAÇÕES + TRACE
```

### Nome da peça interna

Evitar chamar a peça interna do SCRAP de `orquestrador`, para não criar semanticamente um segundo dono.

Preferir:

- `SCRAP ADAPTER ROUTER`, ou
- `SCRAP DISPATCHER`.

Ela responde uma pergunta **local e menor**:

> `Dado que o orquestrador geral já escolheu o SINTONIA SCRAP e uma capacidade, qual adapter/provider interno deve executar?`

Ela **NÃO DEVE** decidir:

- qual missão global executar;
- quais domínios gerais da Collection coletar;
- admissão;
- julgamento;
- prioridade global entre Ciência, Regulatório, Social etc.;
- identidade canônica da Collection;
- política global do `COLLECTION_REQUEST`.

### Um produto, vários adapters

O conceito é **um único produto interno chamado SINTONIA SCRAP**, com adapters especializados.

NÃO criar vários produtos separados por plataforma.

NÃO criar um arquivo monolítico cheio de condicionais `if/elif` por rede.

Os adapters são módulos internos do mesmo executor:

```text
SINTONIA SCRAP
│
├── Instagram Adapter
├── Facebook Adapter
├── LinkedIn Adapter
├── X / Twitter Adapter
├── YouTube Adapter
├── Web Adapter
├── TikTok Adapter, se comprovado útil
├── Podcast / Audio Adapter, se comprovado pertinente
└── outros adapters quando houver razão comprovada
```

### Adapter ≠ Provider

O **adapter** é dono da semântica da plataforma.

O **provider** é a tecnologia substituível usada para cumprir uma capacidade.

Exemplo conceitual:

```text
LinkedIn Adapter
├── Discovery Provider
├── Direct Post Provider
└── Media Provider
```

Um provider pode ser API oficial, `yt-dlp`, HTTP, browser, CDP, serviço externo ou outra rota comprovada. Fallback deve ser explícito e observável, nunca silencioso.

### Serviços transversais não pertencem aos adapters

Não criar um Whisper por plataforma nem fazer cada adapter traduzir por conta própria.

Devem existir responsabilidades compartilhadas, com **um dono por conceito**, por exemplo:

```text
SINTONIA SCRAP EXECUTOR
│
├── SCRAP ADAPTER ROUTER / DISPATCHER
│   └── adapters por plataforma
├── MEDIA RESOLVER / DOWNLOADER
├── ASR OWNER
├── TRANSLATION OWNER
├── PROVENANCE / EVIDENCE
├── OBSERVABILITY / TRACE
└── OUTPUT CONTRACT
```

Portanto:

- `Instagram Adapter` não é dono de ASR;
- `LinkedIn Adapter` não é dono de tradução;
- `YouTube Adapter` não deve criar seu próprio Whisper;
- mídia, ASR, tradução, provenance e observabilidade são serviços transversais quando a responsabilidade for a mesma.

### Contrato externo do SCRAP com o orquestrador geral

O SINTONIA SCRAP deve comportar-se como executor compatível com a Bíblia da coleta e declarar, quando aplicável:

```text
CAPABILITIES   o que o SCRAP sabe fazer
CHECK          se consegue executar a capacidade agora sem iniciar gasto indevido
COLLECT        executa pelo adapter/provider apropriado
STATE          checkpoint interno das fontes sociais/web
OUTPUT         onde largou RAW e derivados, em que forma
TRACE          provider, fallback, custo, duração, erros e resultado
```

O `COLLECTION_REQUEST` não conhece `yt-dlp`, browser, Apify, nomes de script nem detalhe interno do SCRAP.

### Checkpoint

Checkpoint específico de fonte/plataforma pertence ao executor/adapters, não ao orquestrador geral.

Exemplos:

- cursor de paginação;
- último post observado;
- page token;
- continuation token;
- timestamp/cursor próprio da plataforma.

O orquestrador geral conhece o escopo (`PONTUAL`, `INCREMENTAL`, `TOTAL`); o SCRAP conhece a semântica do checkpoint de cada adapter.

### Rota e custo

A escolha interna de provider deve respeitar a lei canônica da **rota de menor custo capaz de cumprir o contrato**, sem transformar Apify em default.

Meta da frente SCRAP:

> `ZERO APIFY` quando houver substituição própria/OSS comprovadamente funcional, sustentável e compatível com a política da fonte.

Mas `ZERO APIFY` não autoriza rota tecnicamente frágil, sem provenance ou fora da política apenas para eliminar custo.

### Fronteira com a Collection

SINTONIA SCRAP **coleta**; ele não admite nem julga.

Preservar sempre:

```text
COLETAR != ADMITIR != JULGAR
RAW != DERIVED != STRUCTURED != ADMISSION != READY
RUN != OBSERVATION != CONTENT != STORAGE OBJECT
SOURCE_LOCATION != FACT_LOCATION
FACT_TIME != PUBLICATION_TIME != OBSERVED_TIME != COLLECTED_TIME
```

Para mídia:

```text
POST OBSERVATION
└── VIDEO / AUDIO RAW OU STORAGE OBJECT, conforme contrato canônico
    └── AUDIO DERIVED, quando derivado de vídeo
        └── TRANSCRIPT DERIVED
            └── TRANSLATION DERIVED
```

Caption, transcript, tradução, vídeo e áudio são objetos/artefatos distintos e não se sobrescrevem.

### Regra para a convergência das linhagens SCRAP atuais

O benchmark de SINTONIA SCRAP encontrou patrimônio em linhagens que ainda não convergiram. A futura convergência **NÃO DEVE** ser resolvida simplesmente por merge cego.

A convergência deve preservar esta topologia:

1. **um único executor SINTONIA SCRAP** visto pelo orquestrador geral;
2. **um router/dispatcher interno**, não um segundo cérebro;
3. **adapters independentes por plataforma**;
4. **providers substituíveis dentro dos adapters**;
5. **serviços transversais com dono único** para mídia, ASR, tradução, provenance e trace;
6. nenhum monólito de condicionais;
7. nenhum conjunto de produtos independentes por rede;
8. nenhuma invasão da responsabilidade de `orquestrador/orquestrador.py`.

Se código existente contrariar esta fronteira, classificar como conflito arquitetural a resolver — não transformar o desvio em nova arquitetura canônica.

---

---

## 11. SINTONIA SCRAP — O QUE FOI CONSTRUÍDO E PROVADO (C1 · C2 · C3)

> A seção 10 fixou a **fronteira**. Esta registra o que passou a **existir**, e
> com que prova. Cada bloco segue: **O QUE mudou → POR QUÊ → PROVA →
> CONSEQUÊNCIA**.

### 11.1 · C1 — o executor único existe

**O QUE.** O SINTONIA SCRAP deixou de ser um conjunto de linhagens que não se
conheciam e passou a ser **um executor**, com os seis verbos de `COL-LAW-013`
em `coleta/scrap_executor.py`. Por dentro:

```text
coleta/social_rotas.py        o SCRAP ADAPTER ROUTER canônico
coleta/scrap_registo.py       dono único de PLATAFORMA/CAPACIDADE -> ADAPTADOR
coleta/scrap_capacidades.py   as capacidades declaradas, com estado medido
coleta/scrap_fornecedores.py  PROVIDER_REQUESTED / USED / WHY_FALLBACK / RESULT
coleta/scrap_http.py          o portão do robots e a busca
coleta/adaptador_*.py         seis adaptadores, um módulo cada
```

**POR QUÊ.** O roteador guardava um `dict` literal com o nome de todas as
plataformas: acrescentar uma obrigava a editá-lo. Isso é o monólito, e o nome
dele não é «arquivo grande» — é «o despachante sabe todas as plataformas».

**PROVA.** `tests/test_scrap_convergencia.py`, 49 provas. Uma delas exige que
acrescentar uma plataforma **não altere um byte** do roteador.

**CONSEQUÊNCIA.** `ADAPTER ≠ PROVIDER ≠ EXECUTION_ENVIRONMENT` são três eixos, e
`ONLINE`/`LOCAL`/`EITHER`/`HYBRID`/`UNKNOWN` é eixo do SCRAP, com `WHY_LOCAL`
obrigatório. O dono único de ASR continua sendo `ferramentas/fala_local.py`, e
há prova que varre as 16 gavetas para o garantir.

### 11.2 · C2 — a API oficial do YouTube atende, e está provada ao vivo

**O QUE.** `YOUTUBE_DATA_API_KEY` **já existia** nos GitHub Secrets, ligada ao
passo `1 · rodar a fase` de `.github/workflows/scrap-social.yml` e lida por
`coleta/youtube_oficial.py`. Quatro capacidades passaram a atravessar a cadeia
inteira até ela.

> **O valor da chave nunca é registrado.** Nem inteiro, nem em pedaços, nem em
> hash. Um comprimento com prefixo é meio segredo, e meio segredo num log é um
> segredo num log. **A prova de que a chave serve é a chamada funcionar.**

**PROVA.** Corrida real no runner hospedado:

| capacidade | método | resultado |
|---|---|---|
| `youtube.search` | `search.list` | 5 itens |
| `youtube.channel.discovery` | `playlistItems.list` | 5 itens |
| `youtube.video.metadata` | `videos.list` | 5 numa chamada |
| `youtube.comments` | `commentThreads.list` | 25 comentários |

**CONSEQUÊNCIA.** `youtube.transcript` e `youtube.media` **continuam fora**:
`captions.download` exige ser dono do vídeo, e os bytes dão 403 de IP de
datacenter. Portanto **`YOUTUBE_ZERO_APIFY_TOTAL = PARTIAL`**, e o total não se
calcula por maioria.

### 11.3 · C3 — os callers antigos largaram os dois Actors

**O QUE.** Três caminhos de runtime paravam de precisar do Actor e continuavam
capazes de chamá-lo. Deixaram de ser capazes:

```text
comunicacao_coleta.ATORES['YOUTUBE']        -> CAPACIDADES_SCRAP
sensor_coleta.ATORES['YOUTUBE_SEARCH']      -> youtube.search
sensor_coleta.ATORES['YOUTUBE_COMMENTS']    -> youtube.comments
```

**POR QUÊ.** «A capacidade já não precisa do Actor» e «o código ainda chama» são
duas frases verdadeiras ao mesmo tempo, e escrever só a primeira declararia uma
economia que ninguém realizou.

**PROVA.** Corrida real: os três callers saíram por `OFFICIAL_API`, nenhum pago,
zero chamadas de Apify. A comunicação pública trouxe 100 itens com
`ACTOR = NAO_SE_APLICA`.

**CONSEQUÊNCIA.** `streamers~youtube-scraper` e
`streamers~youtube-comments-scraper` não têm mais **nenhum caller de runtime**.
`pintostudio~youtube-transcript-scraper` **fica**: legenda de terceiro não tem
rota oficial gratuita, e retirar sem substituto trocaria um gasto por um buraco.

### 11.4 · A distinção do registro: `rota` ≠ `executa`

Uma capacidade entra no registro por **um** de dois papéis, nunca os dois — o
registro levanta se alguém tentar:

```text
rota       a função CRUA, que `social_rotas` despacha DEPOIS dos portões
           (robots, sessão, gasto). Devolve a lista de objetos.
           Para capacidade que a matriz de rotas CONHECE.

executa    a função de NÍVEL DE ADAPTADOR, que devolve (objetos, trace).
           Para capacidade que a matriz NÃO conhece, e por isso não tem
           porta a atravessar.
```

**Exemplos reais:** as quatro do YouTube têm `rota`. A cadeia de Reel e
`youtube.channel.resolve` têm `executa`.

```text
NENHUMA CAPACIDADE TEM OS DOIS. Isso seria dois caminhos para o mesmo pedido,
e o segundo caminho é sempre o que ninguém mede.
```

E há um terceiro papel, opcional: `pronto` — a **sonda gratuita** que responde
«consigo chegar lá agora?» lendo configuração, sem chamar rota nenhuma. É ela
que faz o `CHECK` recusar antes de gastar.

### 11.5 · Lei nova da casa: RAW de teste nunca entra no acervo

**O QUE.** Todo teste que exerce gravação de bruto redireciona
`social_envelope.RAW_DIR` para uma pasta temporária que morre com ele.

**POR QUÊ.** Na C2, seis ficheiros de bruto **inventado** entraram num commit,
na pasta do bruto verdadeiro, com nomes como `videos-aaaaaaaaaaa`.

```text
BRUTO DE TESTE AO LADO DE BRUTO DE COLETA É PIOR QUE LIXO: é a prova de uma
coleta que nunca aconteceu, com o nome certo e na pasta certa.
```

**PROVA.** Sentinela em `tests/test_c3_youtube_cutover.py`: exige o
redirecionamento nos testes que gravam, e reprova se `git status` mostrar bruto
novo no acervo depois da suíte.

**CONSEQUÊNCIA.** Depois de correr a suíte, `git status --short` sobre `data/`
tem de vir vazio. Se não vier, alguém escreveu no acervo real.

### 11.6 · Três coisas que o cutover ensinou, e valem para a próxima migração

**Resolver endereço de conta é um degrau, não um detalhe.** O lote congelado
guarda URLs; a API oficial pede `channelId`. Enquanto a rota era paga, o Actor
engolia a URL. Das sete contas de YouTube, seis resolvem por `forHandle` ou
`forUsername` a 1 unidade; a sétima, `/c/NOME`, **não tem rota oficial
gratuita** e sai `CHANNEL_IDENTITY_UNRESOLVED`.

```text
UM PALPITE COM ID VÁLIDO É PIOR QUE UM ESTADO HONESTO: o palpite entra no
acervo com cara de fato e ninguém volta a perguntar.
```

**A conta da quota muda de forma.** O Actor engolia N termos numa corrida; a API
oficial aceita um por chamada, e busca é o balde escasso — 100 por dia, não
10.000. **N termos = N chamadas**, e isso fica declarado, não escondido.

**Contador que não distingue quem pagou não é contador de custo.**
`APIFY_RUNS` contava toda corrida enquanto toda corrida era paga. Agora conta só
as **pagas**, e ao lado dele vivem `COLLECTION_RUNS` e
`OFFICIAL_API_QUOTA_USED`. Quota não se converte em dólar.

E no item: `ACTOR = NAO_SE_APLICA` quando não houve Actor.

```text
«NÃO SEI QUAL ATOR» E «NÃO HOUVE ATOR» SÃO RESPOSTAS DIFERENTES.
```

### 11.7 · O gasto, e a palavra que ainda não se pode usar

| medida | valor |
|---|---|
| gasto histórico medido, total | US$ 12,8140 |
| do YouTube | US$ 12,3300 — 96,2% |
| dos dois Actors agora sem caller | **US$ 12,2000** |
| ainda associado ao Actor de legenda | US$ 0,1300 |
| corridas que gastaram sem registrar quanto | **25** |

```text
RUNTIME_PAID_DEPENDENCY_REMOVED_FOR_A_D = YES
SAVINGS_REALIZED = ainda não. O futuro ainda precisa rodar.
```

---

### 11.8 · O contrato do medidor — quem gasta é quem sabe quanto

**O QUE mudou.** `coleta/social_rotas.py` passou a carregar um balde genérico,
`MEDIDA`, no registro de cada execução. Ele vai **para** a rota e volta **dentro**
do registro; `scrap_fornecedores.do_registo` sobe para o trace só o que existir
lá. As quatro rotas do YouTube enchem-no com o que a sessão contou.

**POR QUÊ.** A casa já tinha campo para o eixo do dinheiro — `COST_USD`, desde
sempre. O eixo da **quota** não tinha nenhum. Os callers preenchiam-no à mão.

```text
UM EIXO SEM CAMPO É MEDIDO POR PALPITE DE QUEM LÊ.
```

**PROVA.** O primeiro corte da C3 escrevia `+= 1` para o passo da colheita,
com o raciocínio «uma página de `playlistItems` custa uma unidade». Medido com
transporte injetado, o passo custa **duas**: `channels.list` para achar a
playlist de uploads, `playlistItems.list` para a ler. O artefato publicava
metade do gasto real, com cara de medida. Depois do conserto, a corrida ao vivo
`34564613643` publica `geral=3/MEASURED` por conta — que é exatamente o que a
sessão contou.

**CONSEQUÊNCIA.** Quatro regras duráveis, e nenhuma é sobre YouTube:

1. **O balde é genérico.** Não há nome de plataforma no roteador, e não vai
   haver. Quem sabe o preço da chamada é o dono da chamada.
2. **Dois baldes não são um.** `SEARCH` conta **chamadas** (100/dia), `GENERAL`
   conta **unidades** (10.000/dia). Viajam em campos separados até ao artefato:
   `OFFICIAL_API_SEARCH_CALLS` e `OFFICIAL_API_QUOTA_USED`. Somá-los daria um
   número que não existe.
3. **A medida sobrevive à recusa.** Escrita em `finally`, nunca em `else`: quem
   gastou quota e só depois levou `403` gastou na mesma, e apagar isso faria a
   execução parecer de graça.
4. **Balde vazio não vira zero.** «A rota não declarou» e «a rota gastou zero»
   são coisas diferentes. Quando alguma etapa não declara, o artefato sai
   `OFFICIAL_API_QUOTA_STATE = PARTIAL`, e o inteiro vale como **piso** — a
   mesma palavra que a casa já usa para o custo histórico, que se lê
   «≥ US$ 12,81» e nunca «12,81».

**E a lição de método, que é a parte que se repete.** A sentinela certa não é «o
valor está correto» — um valor certo hoje fica errado quando a API muda de
preço. A sentinela certa lê a árvore sintática dos callers e reprova **qualquer
dígito escrito à mão** naquele campo. Há também uma prova que **mede** que a
colheita custa mais de uma unidade: se um dia passar a custar uma, ela reprova, e
aí sim a discussão se reabre com número novo.

```text
UM NÚMERO SUPOSTO COM CARA DE MEDIDO É PIOR QUE NENHUM NÚMERO:
NINGUÉM VOLTA A PERGUNTAR A UM CAMPO QUE JÁ TEM DÍGITO.
```

As cinco rotas abertas — Mastodon, Bluesky, Telegram — passaram a **tolerar** o
balde e não o enchem. Não medem, e por isso não declaram, o que é a verdade
sobre elas.

---

---

## 12. C4 — A PLACA É AMBIENTE, E A MÁQUINA NÃO ATENDEU

```
MISSAO  = C4 · RUNNER LOCAL + GPU ASR, 2026-09-11
BRANCH  = claude/sintonia-scrap-local-gpu-c4
ENTREGA = docs/sintonia-scrap/C4-RUNNER-LOCAL-GPU-ASR.md
VEREDITO = PARTIAL
```

### 12.1 · O relógio contava o download, e o áudio levava a culpa

**O QUE.** Em `ferramentas/fala_local.py`, o relógio da transcrição arrancava
**antes** de o modelo estar pronto. Agora arranca depois, e o tempo de preparar
sai em `MODEL_PREPARE_SECONDS`, campo próprio.

**POR QUÊ.** O tecto de tempo existe para apanhar áudio em laço — o caso real de
2026-09-02 em que um decodificador se alimentava do próprio texto e não
terminava. Mas o tecto contava desde antes da carga.

**PROVA.** O banco de prova desta missão deu `TRANSCRIPTION_TIMEOUT` num Reel
italiano de **34 s** com `medium`, tecto de 204 s. Repetido com o modelo já
pronto: **6,4 s**, estado `OK`, RTF 5,35, e o texto certo — «appassionati di
mais», «Discovery Seeds». O que consumiu os 204 s foi o **descarregamento** do
modelo, 1,5 GB, na primeira vez que aquela máquina o usou.

```text
O ESTADO DIZIA «o que saiu pode estar em laco» — uma afirmacao SOBRE O AUDIO.
A VERDADE ERA «estavamos a baixar um modelo» — uma afirmacao sobre a MAQUINA.

TROCAR UMA PELA OUTRA E O DEFEITO QUE ESTA CASA MAIS PERSEGUE.
```

**CONSEQUÊNCIA.** `MACHINE_SECONDS` passa a ser só reconhecimento, e o RTF
passa a significar o que diz. Preparar falhar tem frase própria: «o modelo é que
não ficou pronto nesta máquina», nunca «o áudio não tem fala».

---

### 12.2 · Cinco eixos, cinco campos — a placa não é o motor

**O QUE.** `ENGINE != MODEL != RUNTIME != DEVICE != ACCELERATOR`. O carimbo do
reconhecedor passou a ter os cinco, com `ASR_DEVICE_REQUESTED`,
`ASR_DEVICE_USED`, `ASR_ACCELERATOR` e `ASR_WHY_FALLBACK`.

**POR QUÊ.** `ASR_DEVICE` era o literal `cpu/int8/N threads`, escrito à mão ao
lado de uma chamada que também tinha `cpu` escrito à mão.

```text
AS DUAS CONCORDAVAM POR COINCIDENCIA DE TECLADO, NAO POR CONSTRUCAO.
No dia em que uma mudasse, a outra continuaria a jurar o contrario —
e o artefato levaria a assinatura da errada.
```

**PROVA.** O campo vem agora do trace que o resolvedor devolve. Sem trace, ele
**confessa** `NOT_KNOWN` em vez de adivinhar. E `faster-whisper` continua a ser
o motor e o `CTranslate2` o runtime **nos dois ferros** — a placa é acelerador,
nunca motor.

**CONSEQUÊNCIA.** Três valores no dono: `CPU`, `GPU`, `AUTO`. O `AUTO` pergunta
ao `CTranslate2` quantos dispositivos CUDA ele **vê**, e uma prova reprova se a
detecção passar a sair de `os.environ`.

```text
UM «AUTO» QUE ASSUME GPU NAO E DETECAO: E UM PALPITE COM CARA DE POLITICA.
```

E a queda é sempre explícita — `None` em `WHY_FALLBACK` quer dizer «não houve
queda», e **nunca** «não sei».

---

### 12.3 · Uma política escrita em quatro sítios é quatro políticas

**O QUE.** A tabela de modelo saiu de `reel_transcricao`, `instagram_transcrever`
e `youtube_transcrever` e passou a viver em `fala_local.MODELOS_POR_CHAMADOR`.

**POR QUÊ.** Quatro constantes, quatro nomes de variável, para uma pergunta —
e nenhuma estava errada, que era o problema.

```text
ELAS CONCORDAM POR COINCIDENCIA, E NO DIA EM QUE O DONO APRENDER ALGUMA
COISA, OS OUTROS TRES CONTINUAM A NAO SABER.
```

**PROVA.** Os três valores não mudaram: `reel` continua `medium`, os dois
programas de lote continuam `small`. As variáveis antigas — `SINTONIA_REEL_MODELO`,
`IG_MODELO`, `YT_MODELO` — continuam todas a valer.

**CONSEQUÊNCIA.** Os chamadores dizem **quem são**; o dono responde **qual
modelo**. Uma prova reprova se um deles voltar a guardar o próprio literal.

```text
CENTRALIZAR A POLITICA NAO AUTORIZA MUDAR OS VALORES DELA
POR BAIXO DE QUEM OS PEDIU.
```

---

### 12.4 · `timeout-minutes` não limita a fila, e runner offline é medição

**O QUE.** No GitHub Actions, `timeout-minutes` só começa a contar quando um
runner **aceita** o job. Um job à espera de máquina que não atende fica `queued`
até às 24 horas.

**PROVA.** Três corridas do `sintonia-scrap` em setembro morreram exactamente às
24 h sem nunca terem corrido. E nesta missão, três despachos para as **duas**
máquinas locais somaram ~80 minutos de fila com **zero** atendimentos — foram
canceladas à mão.

```text
UM TECTO QUE SO CONTA DEPOIS DE COMECAR NAO PROTEGE DE NUNCA COMECAR.
```

**CONSEQUÊNCIA.** Quem despacha para runner local tem de saber: alguns minutos
sem atendimento **é** a resposta. Cancelar e registar, nunca esperar.

E o vocabulário que isso obriga:

```text
RUNNER QUE NAO ATENDE != RUNNER QUE NAO EXISTE != MAQUINA SEM PLACA.
```

Por isso a C4 fecha com `LOCAL_GPU_AVAILABLE = NOT_MEASURED`, e **não** `NO`.
Escrever `NO` mandaria alguém comprar hardware que pode já estar na máquina.

---

### 12.5 · A qualidade já cabe no processador — a placa é vazão

**O QUE.** Medido sobre o corpus já preservado, com verdade de referência
declarada termo a termo:

| língua | `small` | `medium` |
|---|---|---|
| IT | **0/2** termos · RTF 11,6 | **2/2** · RTF 4,7 |
| ES | **2/3** termos · RTF 15,1 | **3/3** · RTF 6,2 |
| FR · EN | empatam em termos | RTF 3,0 e 4,8 |

**POR QUÊ.** `small` acerta a frase e erra **exactamente o que interessa**: o
nome da cultura e o nome da marca.

**CONSEQUÊNCIA.** `medium` custa ~2,5x e corre ainda **3x a 6x mais depressa do
que o tempo real, sem placa nenhuma**.

```text
A QUALIDADE QUE ESTA CASA PRECISA JA CABE NO PROCESSADOR.
A PLACA, SE VIER, E QUESTAO DE VAZAO — NAO DE QUALIDADE.
```

Isto muda a ordem das missões seguintes: a GPU deixa de ser pré-requisito de
qualidade e passa a ser optimização de custo de tempo.

---

### 12.6 · O que a C4 **não** mexeu, e uma distinção que fica

```text
CAN TRANSCRIBE != CAN ACQUIRE MEDIA.

GPU ASR resolve  AUDIO -> TRANSCRICAO.
Ela NAO resolve  YOUTUBE -> AUDIO.
```

`youtube.media` continua `BLOCKED` com `403` de IP de datacenter, e **não existe
capacidade de mídia declarada na matriz** para o YouTube — só o TikTok tem
`FETCH_VIDEO_BYTES`. Os dois Actors de legenda continuam ligados, com prova que
reprova se saírem.

E fica registado o caminho que a medição abre, e que é **mais barato** do que a
placa: `youtube.native_caption` já está **`PROVED`**.

```text
NO YOUTUBE A LEGENDA JA EXISTE. Transcrever com ASR o que a plataforma
ja escreveu e pagar hora de maquina por texto que estava a mao.
```

---

---

## 13. C5 — QUEM PEGA NA CHAVE PEGA NO CONTRATO

```
MISSAO   = C5 · YOUTUBE TRANSCRIPT ROUTE GATE, 2026-09-11
BRANCH   = claude/sintonia-scrap-youtube-transcript-c5
ENTREGA  = docs/sintonia-scrap/C5-YOUTUBE-TRANSCRIPT-ROUTE-GATE.md
DECISAO  = D · BLOCKED_NEEDS_AUTHORIZATION
```

### 13.1 · Usar a API oficial prende a casa a muito mais do que ao `robots.txt`

**O QUE.** O SINTONIA usa a YouTube Data API com `YOUTUBE_DATA_API_KEY`. Isso
faz dele um **API Client**, e API Clients estão presos às *YouTube API Services
Developer Policies* — que são muito mais largas que o `robots.txt` e que os
Termos gerais.

**POR QUÊ.** Até aqui a casa media política olhando o `robots.txt`. Ele responde
«que caminhos um motor de busca pode percorrer». Não responde «quem pode
percorrê-los» nem «o que se pode fazer com o que se trouxe».

**PROVA.** Cinco secções, lidas na fonte viva em 2026-09-11:

```text
III.D.7    nao usar API nao documentada sem permissao expressa
III.E.6    nao fazer scraping — NEM «encourage, enable, or require others to,
           directly or indirectly» faze-lo
III.I.14   nao usar outra tecnologia para obter API Data, incluindo qualquer
           porcao do conteudo audiovisual
III.I.7    nao separar, isolar ou modificar as componentes de audio ou video
III.E.1.a  nao descarregar, importar, copiar ou armazenar copias do conteudo
           audiovisual sem aprovacao escrita
```

**CONSEQUÊNCIA.** Três rotas que a casa discutia como problema **técnico** são,
na verdade, problema de **política**:

| rota | o que a casa pensava | o que a lei diz |
|---|---|---|
| `timedtext` | «não documentado» | III.D.7 + III.E.6 |
| `yt-dlp` | «403 deste IP» | III.I.14 + III.E.6 |
| `YouTube → áudio → ASR local` | «403 de datacenter» | **III.E.1.a + III.I.7** |

```text
UM BLOQUEIO TECNICO CONVIDA A PROCURAR OUTRO IP.
UM BLOQUEIO DE POLITICA NAO SE RESOLVE MUDANDO DE REDE.
```

A terceira linha é a que muda planeamento: o reconhecedor local que a C4 provou
**não tem como ser alimentado a partir do YouTube**, e isso não depende de
hardware, de runner residencial nem de navegador real.

```text
LOCAL / ONLINE E AMBIENTE. NAVEGADOR REAL E AMBIENTE.
RUNNER RESIDENCIAL E AMBIENTE. NENHUM DOS TRES E AUTORIZACAO.
```

---

### 13.2 · Tradução não é transcrição, e o campo tem de dizer qual é

**O QUE.** A saída de transcrição do sensor passou a declarar a **espécie** do
texto, com vocabulário fechado de quatro: `NATIVE_CAPTION_ORIGINAL`,
`NATIVE_CAPTION_TRANSLATED`, `ASR_LOCAL` e `NÃO SEI`.

**POR QUÊ.** Porque as três primeiras estavam a ser guardadas no mesmo campo, com
o mesmo nome, sem nada que as distinguisse.

**PROVA.** Medido sobre os 48 itens já preservados e pagos:

```text
TRANSCRIPT_LANGUAGE = «NAO SEI»   em 48 de 48
ONZE dos 28 com texto sao INGLES vindo de video NAO-INGLES
```

O caso que fecha o assunto: vídeo `RisRARQSFAg`, canal **AIPO Verona**, título
**«Periodico olivo 1° Maggio 2026»**, descrição em italiano. O que ficou no campo
`TRANSCRIPT` foi:

> «Olive growers, welcome back to issue 18 of the May 1, 2026 periodical.»

```text
TRADUCAO ROTULADA COMO TRANSCRICAO ORIGINAL E O PIOR DEFEITO POSSIVEL NUM
CORPUS QUE EXISTE PARA SABER DE QUE CULTURA E DE QUE PRODUTO O CONCORRENTE
FALA, E EM QUE PAIS.
```

Um termo agronómico italiano traduzido para inglês deixa de bater com o léxico
italiano. A peneira que procura «granella» nunca mais a encontra — e o vídeo está
lá, legendado, a falar de granella.

**CONSEQUÊNCIA.** A espécie é **declarada pelo provedor, nunca inferida do
conteúdo**. Ler o texto para adivinhar seria adivinhar duas vezes: primeiro a
língua, depois a intenção. Enquanto o provedor não declarar, a resposta é
`NÃO SEI` — e aqui isso é medição, não desculpa.

E a lição que vale para qualquer fornecedor:

```text
NAO INFERIR A CAPACIDADE PELO NOME COMERCIAL DO PRODUTO.
Medir o que ele DEVOLVEU, no artefato que ele ja produziu.
```

---

### 13.3 · «Eu não quis» e «não me deixam» não se escrevem com a mesma palavra

**O QUE.** `social_matriz.ESTADOS` ganhou dois estados:
`REQUIRES_OWNER_PERMISSION` e `REQUIRES_AUTHORIZATION`.

**POR QUÊ.** `captions.download` e `captions.list` estavam os dois como
`ROUTE_NOT_ALLOWED` — que nesta casa significa «ela permitiria tecnicamente, e eu
escolhi não fazer». Não é o caso de nenhum dos dois.

```text
ROUTE_NOT_ALLOWED          eu podia, e decidi nao fazer.
REQUIRES_OWNER_PERMISSION  o dono do video teria de me autorizar.
REQUIRES_AUTHORIZATION     falta-me credencial mais forte, nao decisao.
```

**PROVA.** `captions.download` exige, na documentação viva, «permission to edit
the video». `captions.list` exige OAuth — a chave de API não autentica — e a
resposta **não contém o texto da legenda**.

```text
LISTAR UMA FAIXA NUNCA FOI O MESMO QUE PODER LE-LA.
```

**CONSEQUÊNCIA.** A diferença é **quem tem a chave da porta**. Colapsá-los faria a
casa carregar a culpa de uma recusa que não é dela — e esconderia que um deles
abre com autorização enquanto o outro depende de terceiros.

---

### 13.4 · Uma lista fechada que ninguém confere é uma lista aberta com outro nome

**O QUE.** `ESTADOS` era uma tupla fechada **sem ninguém a fazê-la valer**.

**PROVA.** Escrevi dois estados novos na matriz e a suíte inteira — mais de dois
mil testes — passou sem reparar. O defeito foi encontrado por eu próprio o ter
cometido e ter ido conferir.

**CONSEQUÊNCIA.** Há agora uma prova que varre a matriz inteira, plataforma por
plataforma, e reprova qualquer estado fora do vocabulário.

```text
DECLARAR UM VOCABULARIO FECHADO E METADE DO TRABALHO.
A OUTRA METADE E A TRAVA QUE O FAZ VALER.
```

E a lição irmã, das sentinelas desta missão: duas provas minhas liam **texto
cru** e reprovavam a coisa errada — uma reprovou o comentário que explica o
defeito, outra encontrou-se a si própria na lista do que procurava.

```text
UMA SENTINELA ANCORADA NO TEXTO MEDE O TEXTO, NAO A LEI.
Ler a arvore sintatica e a diferenca entre medir e adivinhar.
```

---

---

## 14. C6 — O TEXTO DECIDIA O LUGAR DO FACTO SEM DIZER DE ONDE VINHA

```
MISSAO   = C6 · TEXT SPECIES / TRANSCRIPT PROVENANCE GATE, 2026-09-11
BRANCH   = claude/sintonia-scrap-text-provenance-c6
ENTREGA  = docs/sintonia-scrap/C6-ESPECIE-DO-TEXTO.md
DECISAO  = GATE FECHADO · ORIGINAL_PROVEN = 0
```

### 14.1 · A C5 nomeou a espécie; ninguém a jusante perguntava por ela

**O QUE.** A C5 fechou o vocabulário da espécie do texto e carimbou o campo. Mas
carimbar um campo não obriga ninguém a lê-lo. O censo dos consumidores — a peça
central desta missão — encontrou um leitor que usava `TRANSCRIPT` como se fosse
texto original **sem nunca olhar para `TRANSCRIPT_KIND`**.

```text
CARIMBAR O CAMPO E METADE. A OUTRA METADE E O CONSUMIDOR PERGUNTAR POR ELE.
```

**PROVA.** `regras/sensor_medir.py::medir()` juntava título, descrição e
transcrição numa só corda e entregava-a a `lugar_do_fato`, que decide
`COUNTRY_OF_FACT`. Isolando a transcrição nos 28 vídeos que têm texto:

```text
EM 15 DOS 28, O TEXTO MUDOU O PAIS DO FACTO
EM 14 DESSES 15, MUDOU-O PARA «ES»
```

Títulos italianos inequívocos — `CONTRASTO ALLA FLAVESCENZA DORATA DELLA VITE`,
`Diserbo in post-emergenza` — e um francês, `Protection de la vigne en
Champagne`, todos acabavam em Espanha depois de lhes juntar um texto cuja espécie
a casa não conhecia.

**CONSEQUÊNCIA.** O lugar do facto sai das palavras ditas, e por isso só aceita
texto de espécie que sustente original. O tipo de conteúdo **não** foi fechado:
ele sobrevive à tradução.

```text
O QUE O VIDEO E SOBREVIVE A TRADUCAO.
ONDE O FACTO ACONTECEU NAO SOBREVIVE.
PORTAO PEQUENO, NO SITIO CERTO — NAO PORTAO GRANDE A APANHAR TUDO.
```

---

### 14.2 · Um conceito, um dono — e a mudança só se faz quando aparece o segundo

**O QUE.** O vocabulário da espécie vivia em `regras/sensor_coleta.py`, onde
nasceu. Passou para `regras/proveniencia.py`, que já era o dono de `NÃO SEI`,
`NOT_PRESERVED` e das listas fechadas da casa.

**POR QUÊ.** Não por arrumação. Porque apareceu um **segundo** consumidor — o
medidor — e um conceito transversal com dois leitores e nenhum dono acaba com
duas cópias que divergem em silêncio.

```text
MOVER CEDO DEMAIS E INVENTAR CAMADA. MOVER TARDE DEMAIS E TER DUAS VERDADES.
O GATILHO E O SEGUNDO CONSUMIDOR, NAO O GOSTO.
```

**CONSEQUÊNCIA.** A decisão canónica depende **só da declaração do provedor** —
sem detecção de língua, sem comparar com o título, sem regex, sem LLM. Quem
infere pode suspeitar; quem infere não carimba.

---

### 14.3 · A auditoria que suspeita não pode ser a identidade que se guarda

**O QUE.** A C5 observou onze textos ingleses vindos de vídeo não-inglês. Isso é
verdadeiro e útil, e **não** é a espécie daqueles textos. A observação foi para
uma camada derivada separada, com campos de prefixo próprio.

**PROVA.** `data/samples/SENSOR-PILOT/ESPECIE-DO-TEXTO-AUDITORIA-V1.json`
declara `ARTIFACT_KIND = DERIVED`, nomeia os cinco artefatos-pai, e o seu
`TRANSCRIPT_KIND_CANONICAL` sai `NÃO SEI` em todos os 48 — mesmo nos sete em que
a peneira tem quase a certeza.

```text
AUDIT_CLASSIFICATION != TRANSCRIPT_KIND
```

A peneira é de palavra funcional — `della`, `para`, `pour`, `the` — porque
palavra funcional fala de gramática, não de assunto: um texto agronómico
italiano e um espanhol partilham `fusariosi/fusariosis`, não partilham `della` e
`para`. Tem três estados, e abaixo de três marcadores devolve `UNKNOWN`.

```text
UMA PENEIRA QUE CONFESSA O BURACO VALE MAIS DO QUE UM DETECTOR QUE NAO O CONFESSA.
```

**CONSEQUÊNCIA.** Nada desta camada alimenta o contrato de procedência, e há
prova que reprova quem os ligar. Os 48 artefatos históricos não foram tocados:
o que ficou gravado continua a dizer o que a casa sabia quando os gravou.

```text
HISTORICAL_EVIDENCE != REWRITTEN_HISTORY
```

---

### 14.4 · O estado real do corpus, dito como é

```text
ORIGINAL_PROVEN     0
TRANSLATED_PROVEN   0
ASR_LOCAL           0
KIND_UNKNOWN       28
NO_TEXT            20
TOTAL              48
```

Zero textos com origem provada. Não é «quase original», não é «provavelmente
original»: é zero provado e 28 por saber, e as duas coisas escrevem-se com
palavras diferentes.

```text
0 != NAO SEI != NOT_PRESERVED
ARREDONDAR «NAO SEI» PARA «ORIGINAL» E A UNICA MANEIRA DE PERDER O CORPUS INTEIRO.
```

E a tradução **não** foi banida: um texto traduzido continua a servir para saber
de que cultura e de que praga o concorrente fala.

```text
FIT_FOR_PURPOSE PERTENCE AO CONSUMIDOR. PROCEDENCIA PERTENCE A COLETA.
```

---

### 14.5 · Um defeito maior, encontrado e deixado por corrigir de propósito

**O QUE.** Ao isolar porque é que os textos mandavam tudo para Espanha, apareceu
o mecanismo — e é muito maior do que a questão da procedência. `lugar_do_fato`
casa nomes de lugar por **raiz truncada**: `'la rioja'` vira `['rio']`, e `'rio'`
casa com qualquer palavra que o contenha.

**PROVA.** Nos 28 textos: `period` 54 vezes, `prior` 16, `various` 14. Em
italiano e espanhol, `periodico`, `calendario`, `fitosanitario`.

```text
lugar_do_fato('calendario fitosanitario')  ->  ('ES', 'la rioja')

230 DOS 1071 VIDEOS — 21% — JA DISPARAM ISTO SO PELO TITULO E DESCRICAO,
SEM TRANSCRICAO NENHUMA.
```

**CONSEQUÊNCIA.** Não foi corrigido aqui, e a razão que manda é a terceira:
consertá-lo mudaria 230 registos publicados de `COUNTRY_OF_FACT`. Isso é decisão
da casa, não efeito colateral de uma missão sobre espécie de texto.

```text
UM CONSERTO GRANDE ESCONDIDO DENTRO DE UMA MISSAO PEQUENA
E UMA MUDANCA QUE NINGUEM REVISOU.
```

Fica registado com o mecanismo, o alcance medido e o comando que o reproduz. O
próximo a fechar é `leis/regua_italia.py`, que tem o mesmo padrão sem filtro e
é o casador léxico italiano — hoje nunca dispara, porque nenhum dos 1071 itens
da medição carrega `TRANSCRIPT`, mas dispararia no dia em que carregasse.

```text
UM CONSUMIDOR QUE NAO DISPARA HOJE E UM CONSUMIDOR, NAO UMA AUSENCIA.
```

---

---

## 15. C7 — A BETERRABA VIRAVA TOLEDO

```
MISSAO   = C7 · FACT_LOCATION MATCHER REPAIR, 2026-09-11
BRANCH   = claude/sintonia-fact-location-c7
ENTREGA  = docs/sintonia-scrap/C7-LUGAR-DO-FATO.md
DECISAO  = FACT_LOCATION_MATCHER = PASS · derivado regenerado apos o portao
```

### 15.1 · A peneira que serve o assunto destrói o nome próprio

**O QUE.** `lugar_do_fato` usava `_tem`, a peneira de ASSUNTO da casa. Ela
trunca a palavra de propósito — é assim que `diserbo` apanha `diserbato` — e
procura a raiz **dentro** de qualquer palavra.

**POR QUÊ.** Para assunto, truncar é virtude: a ideia sobrevive à conjugação.
Para nome próprio é ruína, porque nome truncado não vira o mesmo nome — vira
outro.

```text
_raizes('la rioja')  ->  ['rio']
```

**PROVA.** Contado nos 4.759 textos do acervo, e não só em «la rioja»:

```text
la rioja  <- septoriose (48x), fusariosi (17x)   o nome da DOENCA
toledo    <- barbabietole, bietole               a BETERRABA
france    <- francesco, francesca                o NOME DA PESSOA
beauce    <- beaucoup (43x)                      «muito»
verona    <- davvero (37x), vero (36x)           «deveras»
cordoba   <- ricordo (27x), accordo              «recordo»
italia    <- italiana, italiano, digitale        e IDIOMA != LUGAR DO FATO
```

Não era um lugar infeliz: **37 dos 59 lugares declarados** casavam assim.

**CONSEQUÊNCIA.** A geografia tem matcher próprio, e ele não trunca nada. A
regra de fronteira foi **copiada, não inventada**: veio de
`leis/fato_local.py::mencoes`, que já a tinha escrito com a razão ao lado —
«substring acidental foi um dos falsos positivos medidos no Brasil».

```text
PENEIRA DE ASSUNTO TRUNCA PORQUE A IDEIA SOBREVIVE A CONJUGACAO.
NOME PROPRIO NAO SOBREVIVE A TRUNCAGEM — ELE VIRA OUTRO NOME.

NORMALIZAR != STEMMING.
```

E a lição de método que a acompanha: o defeito foi encontrado numa entrada e
consertado nas cinquenta e nove. Red-teamar só o caso que doeu deixaria as
outras trinta e seis bombas no sítio.

---

### 15.2 · Um artefato derivado sem hora de derivação envelhece em segredo

**O QUE.** O `MEDICAO.json` publicado era de **2026-09-06**. A régua por baixo
dele mudou três vezes desde então e ninguém o refez.

**POR QUÊ.** Porque nada no artefato dizia de quando ele era. Ele não declarava
`CAPTURED_AT`, nem os pais, nem a régua — e por isso parecia ter a idade da
coleta.

**PROVA.** A decomposição que só apareceu por se ter medido em três pontos, em
vez de comparar o artefato antigo com o novo:

```text
publicado, codigo de 2026-09-06        236 videos com pais
codigo de HOJE, geografia ANTIGA       510      <- 5 dias de deriva
codigo de HOJE, geografia NOVA         184      <- o efeito da C7
```

Comparar 236 com 184 diria «a C7 tirou 52». O efeito da C7 é **510 → 184**, e o
`236 → 510` é de missões anteriores que mexeram na isca e nunca refizeram o
derivado. Na mesma regeneração, `RESEARCH_COMMUNICATION` salta de 11 para 284 —
e **nada disso é da C7**: medida zero divergência em `classificar_conteudo`
(1115 itens) e `classificar_comentario` (3737).

**CONSEQUÊNCIA.** O artefato passou a declarar `ARTIFACT_KIND`, os quinze
artefatos-pai, a hora da derivação e a **régua** que produziu os números.

```text
ARTEFATO DERIVADO SEM HORA DE DERIVACAO ENVELHECE EM SEGREDO.
A REGUA MUDA O NUMERO — ENTAO O NUMERO TEM DE DIZER QUE REGUA O FEZ.
```

---

### 15.3 · «Afetados» não é «errados», e a diferença mede-se

**O QUE.** A C6 registou «230 dos 1071» e escreveu que consertar mudaria **230
registos publicados**. A C7 foi verificar e a frase estava errada.

**PROVA.** Os 230 reproduzem exactamente — mas **no código**, não no artefato. A
lista tinha `la rioja` desde 2026-09-06; o casamento por raiz só chegou a
2026-09-07, e ninguém regenerou depois disso. O artefato publicado tinha **zero**
evidências de «la rioja».

Decompondo os 230 no código: `EXACT_PHRASE_MATCH` **0**, `TOKEN_MATCH` **0**,
`FUZZY_ROOT_MATCH` **230**. Nenhum deles era um lugar escrito.

E o artefato publicado tinha erro seu, de outra espécie — substring simples, que
é anterior à raiz truncada:

```text
videos   236 com pais, dos quais  61 com evidencia FALSA
coments  131 com pais, dos quais  56 com evidencia FALSA
```

«Evidência falsa» é o campo dizer «o texto nomeia X» sem que o texto escreva X:
`aragon` vindo de `paragonabile`, `jaen` de um handle `canalsurjaen`, `italia`
de `italiano`.

**CONSEQUÊNCIA.** O número certo de registos publicados errados era **117**, não
230 — e nem sequer pela mesma causa.

```text
AFETADOS NO CODIGO != ERRADOS NO ARTEFATO.
UM DEFEITO LATENTE E O QUE ESTOURA NA PROXIMA REGERACAO,
E POR ISSO O CONSERTO TEM DE VIR ANTES DELA.
```

---

### 15.4 · Cair de 510 para 184 não é perder capacidade

**O QUE.** Depois do conserto, o acervo conhece o país do facto em muito menos
itens.

**PROVA.** Dos 71 vídeos que mudaram de um país para outro, **todos** foram para
o país certo: vídeos italianos sobre flavescência dourada que diziam Espanha
passaram a dizer Itália; vídeos franceses sobre míldio que diziam Espanha
passaram a dizer França. E `UNKNOWN_TO_KNOWN = 0`: nenhum país novo apareceu do
nada. Os dois lugares que só existem depois — `gironde` e `chianti` — estavam
escritos no texto e estavam tapados por um falso positivo que casava primeiro.

**CONSEQUÊNCIA.** O que caiu era conhecimento falso.

```text
UNKNOWN CORRECTO VALE MAIS DO QUE PAIS FABRICADO.
```

E a perda real foi medida, não assumida: das 793 quedas, o nome só aparece
escrito em 75, e dessas **55 são gentílicos** (`italiano`, `siciliano`) e **16
são handles ou domínios** (`canalsurjaen`, `francetvinfo`). Gentílico fala da
pessoa e handle fala da fonte:

```text
COUNTRY_OF_PERSON != COUNTRY_OF_FACT
SOURCE_LOCATION   != FACT_LOCATION
```

Sobram três menções genuínas em 4.759 textos, duas delas saudações («un caro
saluto dalle Marche»), que também são da pessoa. A lista declara `le marche` e
não `dalle marche`; ampliá-la é decisão de quem declara a lista, e fica
registada por decidir — não feita em silêncio.

---

### 15.5 · Uma prova que se apoia num defeito morre quando o defeito morre

**O QUE.** A prova viva do portão de espécie da C6 usava texto inglês com
«prior period», «superior», «various» e «scenarios».

**PROVA.** Aquelas palavras mudavam o país **porque a raiz `rio` casava dentro
delas**. Consertado o casador, a prova deixou de reproduzir e passou a não medir
nada — e foi a suíte que o disse.

**CONSEQUÊNCIA.** Não foi apagada: o texto passou a nomear um lugar, que é o que
um texto original faria. A prova voltou a medir o que lhe compete — se a
**espécie** decide a entrada do texto — em vez de depender de o casador de lugar
ser mau.

```text
UMA PROVA QUE SE APOIA NUM DEFEITO MORRE QUANDO O DEFEITO MORRE.
A PERGUNTA CERTA E SE ELA AINDA MEDE A LEI, NAO SE ELA AINDA PASSA.
```

### 15.6 · Cinco missões construíram uma frente que o orquestrador não alcança

**O QUE.** No fechamento da C7, ao ler o contrato canônico de retorno da coleta
sem o integrar, mediu-se o caminho do SCRAP até à porta da Collection. Ele não
fecha — e a parte que falta não é a que se supunha.

**PROVA.** Três medições, nenhuma delas opinião:

```text
quem importa `ingresso` em toda a arvore:  ['orquestrador']
nenhum modulo do SCRAP la chega por importacao — medido por travessia do grafo

pedido/receitas.py declara 5 executores:
  corpus-pesquisador · rotulos-oficiais · eppo · italia-recorrente
  comunicacao-publica
NENHUMA e do YouTube.

system-map/data/fronteira.observada.json:
  DESTINO_EXISTE  False
  CONSUMIDORES    []
  GAP             READY_SEM_CONSUMIDOR
```

A ligação SCRAP → Collection existe por **pasta declarada** (`larga_em`, lida por
`a_colheita()`), não por chamada. E a frente de YouTube que as missões C3 a C7
construíram — rota oficial, portão de política, procedência do texto, geografia —
não tem receita nenhuma. O orquestrador não sabe pedi-la.

**CONSEQUÊNCIA.** Os três níveis, ditos sem arredondar:

```text
SCRAP MODULE EXISTS          YES
SCRAP -> Collection EDGE     PARTIAL — por pasta, nao por chamada
SCRAP -> Collection FLOW     NO
```

```text
UM EXECUTOR SEM RECEITA NAO ESTA LIGADO AO ORQUESTRADOR. ESTA AO LADO DELE.
MODULE EXISTS != EDGE EXISTS != FLOW EXISTS — e cinco missoes de capacidade
nao movem o terceiro nivel sozinhas.
```

E a lição de método que a acompanha, porque foi ela que evitou a conclusão
errada: uma missão `DERIVED` não atravessar o envelope **não prova** que o
executor o cumpre. A resposta certa para a compatibilidade do SCRAP era
`UNKNOWN`, e escrevê-la custou menos do que teria custado descobri-la depois.

```text
UMA MISSAO DERIVED NAO E CREDENCIAL DO EXECUTOR.
```

---

### 15.7 · Um laço que procura por si próprio nunca sai

**O QUE.** Duas tarefas de fundo ficaram indefinidamente em «Em execução». Não
era a suíte: era o esperador.

**PROVA.** O laço era `until ! pgrep -f PADRAO; do sleep N; done`. A linha de
comando do próprio laço **contém** o padrão, e por isso `pgrep -f` encontra-se a
si mesmo — a condição nunca fica falsa. As suítes reais tinham terminado há
muito, com código de saída 0, e os ficheiros de saída dos esperadores tinham
zero bytes: eles nunca chegaram a emitir nada.

**CONSEQUÊNCIA.** É a cicatriz da C5 noutra forma. Lá era uma sentinela que se
procurava a si própria no texto do ficheiro; aqui é um laço que se procura a si
próprio na tabela de processos.

```text
UMA SENTINELA QUE SE LE A SI PROPRIA ENCONTRA-SE SEMPRE —
E ISSO VALE PARA `grep` NO FICHEIRO E PARA `pgrep` NO PROCESSO.
```

Esperar por um processo pede uma âncora que o esperador não possa ter: o PID, o
ficheiro de saída, o código de saída. Nunca o nome que ele próprio carrega.

---

## 16. C4B — ESCOLHER O FERRO NÃO É TER CORRIDO NELE

```
MISSAO   = C4B · FECHAR GPU ASR COM PROVA DURAVEL, 2026-09-11
BRANCH   = claude/sintonia-scrap-local-gpu-c4
ENTREGA  = docs/sintonia-scrap/C4-RUNNER-LOCAL-GPU-ASR.md (seccoes B2·B3·B4·G2·H2·R2)
DECISAO  = C4_GPU_ASR = PROVEN · GPU_QUALITY_BENCHMARK = NOT_RUN
```

### 16.1 · Um campo chamado «USED» que se enchia antes de alguém usar

**O QUE.** `resolver_dispositivo()` devolvia `DEVICE_USED` — e devolvia-o antes
de existir uma única amostra transcrita. Quando a inferência caía, o artefato
saía a dizer que a placa tinha corrido.

**PROVA.** Medido na máquina local, com a GTX 1080 a responder e o cuBLAS em
falta:

```text
TRANSCRIPT_STATE   ASR_FALHOU
ASR_DEVICE_USED    GPU          <- e nada correu na placa
ASR_ACCELERATOR    CUDA
ERROR              RuntimeError: Library cublas64_12.dll is not found
```

**CONSEQUÊNCIA.** Três momentos, três campos, e cada um sabido na sua hora:
`REQUESTED` (antes), `SELECTED` (na resolução), `EXECUTION` (depois da
inferência: `PROVEN` · `FAILED` · `NOT_RUN`). `USED` foi preservado porque tem
consumidores — o que mudou é que fora de `PROVEN` ele é `NOT_KNOWN`.

```text
DEVICE SELECTED != DEVICE EXECUTION PROVEN.
QUEM DECIDE ANTES NAO PODE TESTEMUNHAR DEPOIS.
```

E a escolha continua dita de propósito: é no caso que falha que se precisa de
saber onde se estava. Apagá-la seria o defeito oposto — perder o diagnóstico.

---

### 16.2 · Contar a placa não é poder multiplicar nela

**O QUE.** `cuda_disponivel()` devolvia `1` e a inferência caía a seguir por
falta de `cublas64_12.dll`. Não é contradição: são duas perguntas.

**PROVA.** `get_cuda_device_count()` só precisa do driver. O cuBLAS só é chamado
na **primeira multiplicação de matrizes**, já dentro da inferência. Entre uma
coisa e a outra cabia o defeito inteiro.

A terceira corrida no runner disse onde:

```text
PATH_TEM_CUDA  false
...NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin   existe no disco
```

A DLL estava lá. O PATH do **serviço** do runner é que não a continha — ele
arrancou antes de o toolkit ser instalado, e serviços não apanham mudança de
PATH sem reiniciar.

**CONSEQUÊNCIA.** `_caminho_das_libs()` só mexia no `sys.path`, e isso chega para
**importar** e não chega para **carregar**. Passou a registar as pastas de DLL.
E `os.add_dll_directory` sozinho **não bastou** — medido:

```text
REGISTAR A PASTA E DIZE-LO A QUEM USA A API NOVA.
QUEM USA A ANTIGA CONTINUA A LER O PATH.
```

Fazem-se as duas coisas, e as duas no **processo**: morrem com ele, e não tocam
na máquina.

```text
PLACA PRESENTE != DRIVER COM CUDA != BIBLIOTECA A CONTAR A PLACA
                                  != BIBLIOTECA A PODER USAR A PLACA.
```

---

### 16.3 · Perguntar à biblioteca errada dá uma resposta verdadeira sobre outra pergunta

**O QUE.** A prova parava com `MODEL_NOT_PRESENT` sobre um modelo que **estava**
na máquina.

**PROVA.** Ela chamava `huggingface_hub.snapshot_download(local_files_only=True)`,
que exige o repositório **inteiro**. O `faster-whisper` baixa só os ficheiros de
que precisa — `model.bin`, `config.json`, tokenizer — e por isso a cópia local é
legitimamente **parcial**.

Quem revelou isto foi o diagnóstico acrescentado na corrida anterior: ele
imprimiu a cache consultada e os modelos visíveis nela, e o modelo estava na
lista.

**CONSEQUÊNCIA.** Pergunta-se a `faster_whisper.utils.download_model` — a mesma
função que o carregador usa, com os mesmos `allow_patterns`.

```text
DIZER «NAO ENCONTREI» SEM DIZER ONDE PROCUREI NAO AJUDA NINGUEM.
PERGUNTAR A BIBLIOTECA ERRADA DA UMA RESPOSTA VERDADEIRA SOBRE OUTRA PERGUNTA.
```

---

### 16.4 · A prova que se vê apanhar o caso que a motivou

**O QUE.** Quatro corridas no runner real até ao verde. Nenhuma foi «tentar
outra vez»: cada uma mediu o que a anterior não sabia.

**PROVA.**

```text
1  MODEL_NOT_PRESENT  a fase nova disparava DOIS jobs
2  MODEL_NOT_PRESENT  a pergunta estava errada — o modelo estava la
3  FAIL · cuBLAS      a inferencia caiu, e o contrato novo DISSE A VERDADE
4  PASS               as DLL estavam no disco; o processo e que nao as via
```

A terceira vale por si. O defeito que motivou a missão reproduziu-se no runner
real e o contrato novo apanhou-o:

```text
ASR_DEVICE_SELECTED   GPU
ASR_DEVICE_EXECUTION  FAILED       <- o campo novo
ASR_DEVICE_USED       NOT_KNOWN    <- antes dizia GPU
```

**CONSEQUÊNCIA.** É a única forma de saber que um conserto serve: vê-lo apanhar
o caso que o produziu, no sítio onde o caso acontece.

```text
UM CONSERTO SO ESTA PROVADO QUANDO SE VE APANHAR O DEFEITO ORIGINAL.
O QUE NAO CORRE OUTRA VEZ NAO E PROVA. E UMA LEMBRANCA.
```

E a corrida final, com nome e número:

```text
RUN 34621682770 · JOB 103336938609 · commit 2df00244 · SINTONIA-EAME-LOCAL
RESULT PASS · TRANSCRIPT_STATE OK · 55 caracteres
ASR_DEVICE_EXECUTION PROVEN · ASR_DEVICE_USED GPU · cuda/int8_float32
```

---

### 16.5 · A capacidade entrou. A política não.

**O QUE.** A placa declara `int8_float32`, `int8` e `float32` — e **não**
`float16`, que era o padrão do código. A prova passou com `int8_float32`. O
padrão **não** mudou.

**POR QUÊ.** Três razões, e a terceira manda: `float16` falhar numa Pascal não é
`float16` falhar; não há benchmark de qualidade no corpus real; e a lei da C4
continua a valer — a capacidade entra, a decisão não.

**CONSEQUÊNCIA.** `int8_float32` vive como override **explícito e declarado**, na
fase do workflow, à vista de quem lê.

```text
UMA POLITICA TIRADA DE UMA AMOSTRA DE UM
NAO E POLITICA. E UMA COINCIDENCIA PROMOVIDA.

GPU TECHNICAL SMOKE != GPU QUALITY BENCHMARK.
CAN DO != DID DO != DOES IT WELL.
```

O banco de qualidade continua `NOT_RUN`, e por uma razão que **mudou**: antes era
a máquina que não atendia; agora é o corpus com verdade de referência que não
está nela.

---

### 16.6 · A casa apanhou-me a mim

**O QUE.** Escrevi o perfil pessoal real do utilizador dentro de um comentário
commitado, ao citar um log do runner.

**PROVA.** A sentinela de credenciais da casa reprovou, pelo nome, na regressão:

```text
RASTREADO  provas/gpu_asr_smoke.py:82  caminho pessoal Windows
```

**CONSEQUÊNCIA.** Saiu do código e passou a sair mascarado também em tempo de
execução. O diagnóstico precisa de saber QUE pasta foi consultada — nunca DE QUEM
ela é.

```text
O CAMINHO E DIAGNOSTICO. O DONO DO PERFIL NAO E.
```

E a cicatriz irmã, pela terceira vez nesta casa: uma sentinela minha procurava
`snapshot_download` no **texto** do ficheiro e encontrava-o no comentário que
explicava por que essa chamada tinha saído — reprovou o próprio conserto.

```text
UMA SENTINELA ANCORADA NO TEXTO MEDE O TEXTO, NAO A LEI.
```

---

## 17. C4C — O CORPUS ESTAVA PRESERVADO; ERA A PERGUNTA QUE ESTAVA ERRADA

```
MISSAO   = C4C · RECUPERAR 1 AMOSTRA REAL E MEDIR CPU x GPU, 2026-09-11
BRANCH   = claude/sintonia-scrap-gpu-quality-c4c
ENTREGA  = docs/sintonia-scrap/C4-RUNNER-LOCAL-GPU-ASR.md (seccao C4C)
DECISAO  = CPU_SAMPLE_BENCHMARK = PROVEN
           GPU_SAMPLE_BENCHMARK = BLOCKED_CORPUS_NOT_ON_GPU_MACHINE
```

### 17.1 · Onde o bruto preservado vive, e como se pergunta por ele

**O QUE.** A C4B concluiu `SEM_CORPUS` e a conclusão estava errada. O corpus
estava inteiro, e o manifesto da casa já dizia onde.

**POR QUÊ.** Ela procurou `C-FanW_CYMz.wav`. O `.wav` é **derivado** — nasce de
`extrair_audio` e pode ser refeito a qualquer momento. Quem está preservado, com
hash, é o **`.mp4`**.

**PROVA.** `data/samples/REEL-TRANSCRICOES/TRANSCRICOES-REEL.json` carrega, por
item, um bloco `RAW` completo:

```text
ARTIFACT_ID       RAW-a44827ebd61f0e0b
STORAGE_LOCATION  data/raw/REEL-MIDIA/C-FanW_CYMz.mp4
SHA256            a44827ebd61f0e0b5a8878ffed10ac0da4477f5139c6c3835542ae88734031d4
BYTES             1788869
RUN_ID · EXECUTOR_ID · COLLECTED_AT · STATE
```

Perguntando ao manifesto em vez de procurar um nome de ficheiro: **8 de 8**
artefatos recuperados e provados por hash, quatro deles com verdade de
referência declarada.

**CONSEQUÊNCIA.** `provas/corpus_recuperar.py` faz essa pergunta e não vai à
rede. E a regra que ele carrega dentro da própria resposta:

```text
PROCURAR O ARTEFATO ERRADO DA UMA RESPOSTA VERDADEIRA SOBRE OUTRA COISA.
PATH != IDENTIDADE. SHA != OBSERVACAO.
AUSENCIA DE CORPUS NAO E AUTORIZACAO DE RECOLHER.
```

O `SHA256` identifica os BYTES. Não é `DOCUMENT_ID`, e o próprio manifesto
explica: dois RUNs que tragam o mesmo vídeo têm o mesmo hash e são **duas
observações**.

---

### 17.2 · O corpus e a placa estão em máquinas diferentes

**O QUE.** A pergunta «CPU contra GPU sobre a mesma amostra» não se pode
responder hoje, e o motivo não é técnico nem de autorização.

**PROVA.** Medido nos dois lados, não suposto:

```text
contentor Linux desta sessao     corpus 8/8, hash confere    placa: NAO
runner SINTONIA-EAME-LOCAL       corpus 0/8                  placa: SIM
```

O lado do runner é a corrida `34623490650`: o censo respondeu `NOT_FOUND`, o
banco não correu, e o job disse porquê.

E não há canal para lá levar o byte sem quebrar uma regra: o Git está fora
(`data/raw` é ignorado de propósito), recolher outra vez seria aquisição, não há
artefato de corrida anterior (`total_count = 0`) e a casa não declara storage
remoto para RAW.

**CONSEQUÊNCIA.** O bloqueio ficou escrito com o nome exacto —
`BLOCKED_CORPUS_NOT_ON_GPU_MACHINE` — e não como `SEM_CORPUS`, que já tinha
enganado uma vez.

```text
O CORPUS EXISTE E ESTA PROVADO. ELE SO NAO ESTA ONDE A PLACA ESTA.
UMA AUSENCIA DE CANAL NAO E UMA AUTORIZACAO DE ATALHO.
```

A metade que se podia medir foi medida: `medium` em CPU sobre as quatro amostras
reais, todas `OK`, língua estável, e o sentinela italiano a reproduzir
exactamente o `PARTIAL` que já estava registado — `2/2` nos termos do CAPTION e
`0/1` na marca, porque `syngenta` vem da identidade da conta e não é dito na
fala.

```text
METADE MEDIDA E DECLARADA VALE MAIS DO QUE UM NUMERO INTEIRO INVENTADO.
```

---

## EM PALAVRAS FÁCEIS

Estamos consertando a fundação da coleta antes de voltar a crescer o sistema.

A casa já aprendeu que **o arquivo guardado e o momento em que vimos esse arquivo são duas coisas diferentes**. Agora falta dar uma identidade segura para as observações novas, sem mentir sobre as antigas.

A especificação das fases 7–9 acabou de passar por uma correção importante: não usar relógio para separar passado/futuro, não aceitar fonte falsa e não transformar hash em identidade documental por conveniência.

O próximo passo é **revisar isso no GitHub e, se estiver realmente fechado, implementar só as fases 7–9**. A trava antiga de `storage_path` continua no lugar. Tirar essa trava é fase 10 e ainda não está autorizada.

Para o SINTONIA SCRAP, a regra simples é: **ele é um executor especializado dentro da coleta, não o cérebro da coleta inteira**. O cérebro continua sendo o orquestrador canônico. Dentro do SCRAP existe apenas um dispatcher/router local que escolhe o adapter e o provider certos para Instagram, Facebook, LinkedIn, X, YouTube, Web e outras fontes absorvidas.