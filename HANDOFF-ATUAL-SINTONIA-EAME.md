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

## EM PALAVRAS FÁCEIS

Estamos consertando a fundação da coleta antes de voltar a crescer o sistema.

A casa já aprendeu que **o arquivo guardado e o momento em que vimos esse arquivo são duas coisas diferentes**. Agora falta dar uma identidade segura para as observações novas, sem mentir sobre as antigas.

A especificação das fases 7–9 acabou de passar por uma correção importante: não usar relógio para separar passado/futuro, não aceitar fonte falsa e não transformar hash em identidade documental por conveniência.

O próximo passo é **revisar isso no GitHub e, se estiver realmente fechado, implementar só as fases 7–9**. A trava antiga de `storage_path` continua no lugar. Tirar essa trava é fase 10 e ainda não está autorizada.

Para o SINTONIA SCRAP, a regra simples é: **ele é um executor especializado dentro da coleta, não o cérebro da coleta inteira**. O cérebro continua sendo o orquestrador canônico. Dentro do SCRAP existe apenas um dispatcher/router local que escolhe o adapter e o provider certos para Instagram, Facebook, LinkedIn, X, YouTube, Web e outras fontes absorvidas.