# HANDOFF — INTELIGÊNCIA ITÁLIA → MISSÃO DO SITE

**Esta aba produz inteligência. Ela não publica o portal.**
Nada aqui foi ingerido no site. O site é outro consumidor, e a ingestão é decisão dele.

---

## 0 · IDENTIDADE

```
BRANCH  = claude/adama-italia-source-discovery-oui6ma
HEAD    = 4a97dbb
TREE    = limpa
TESTES  = 329, 0 falhas
```

Commits desta aba, todos nesta branch e em nenhuma outra:

```
4a97dbb  a rota de audio rendeu 84,6% de sinal so na fala, e a auditoria derrubou 8 dos 11
a419e9c  depois de tres lotes de Instagram renderem 5, 2 e 0, a casa abriu a rota de audio
8a50400  o acervo de fontes da Italia passou de 43 para 87, e duas delas cairam na conferencia
87523cd  21 sinais sobreviveram a refutacao, e o melhor deles ESFRIA um caso
73888cb  testei a minha propria hipotese sobre o Instagram e ela falhou
c715ac8  eu estava errado sobre o Instagram: era o User-Agent, nao o navegador
6f6c5d7  a fronteira fica escrita, e o numero errado que eu publiquei fica corrigido
510ccb1  o calendario regulatorio ganha as duas metades: quando abre, e quando some
809328f  o Sintonia Scrap ganha a metade que faltava: video, pelo mesmo contrato e motor
4e3bce4  li a rota que eu mesmo tinha listado como desbloqueio, e ela nao fecha o caso
ca464f9  o relatorio da missao: o que esta acontecendo agora, e onde olhar amanha
30b06bf  a varredura paralela achou a rota de dado que faltava
1a62592  o Atlas aponta para a descoberta sem mover a sentinela que um teste vigia
2f44fe3  Italia: a rede de fontes vira acervo, e a fala revela o que a legenda nao dizia
```

---

## 1 · FRONTEIRA — verificado, não presumido

| | |
|---|---|
| **SITE CHANGED** | **NO** |
| **VERCEL CHANGED** | **NO** |
| **PRODUCTION TOUCHED** | **NO** — verificado por leitura, ver §2 |
| **CANONICAL BUILD CHANGED** | **NO** — o pacote V2.1 não foi tocado |

`vercel.json`, `.vercel/` e `italia-portale/` **não existem nesta branch**. O único HTML da
árvore é `prototype/portal/index.html`, que está `CONGELADO.md` e cujo diff contra a base é
**vazio**.

Os **11** pushes desta aba foram **todos** para `claude/adama-italia-source-discovery-oui6ma`.
Nenhum push, merge, rebase ou fast-forward em `claude/site-v21-ingest-recovery`,
`claude/eame-competitor-public-communication` ou `claude/sintonia-eame-repo-setup-xccfob`.
As branches do site foram **lidas** (`git fetch`) para consultar o corpus canônico da Itália,
e nunca escritas.

---

## 2 · CHECAGEM DE PRODUÇÃO

Feita por **leitura**, sem CLI, sem deploy, sem alias, sem tocar em configuração.

O projeto Vercel ligado a `lucianodalondon-sys/eame-sintonia` é **`sintonia-eame-preview`**
(`prj_rKjzMNHiB2ulP8ev5bmYYeUFUTwe`, team `london-creative`).

Os pushes desta branch produziram deployments **todos com `target: null` (preview)**.
Releitura em 2026-09-03 20:16 UTC, dos 20 deployments mais recentes do projeto:

| origem | deployments lidos | `target` |
|---|---|---|
| `claude/adama-italia-source-discovery-oui6ma` (esta aba) | 7 | **null** em todos os 7 |
| `claude/site-v21-ingest-recovery` (a missão do site) | 12 | `production` em todos os 12 |
| `claude/opportunity-commercial-priority-v1` | 1 | **null** |

Nenhum preview desta aba foi promovido, testado como site oficial, aliasado ou associado a
domínio. **Os 12 `target=production` desta janela vêm todos da branch do site**, que é a dona
dessa decisão — nenhum vem daqui.

### Uma correção ao que este handoff dizia antes

A versão anterior desta seção afirmava `target: null` para os 6 deployments desta branch, e
isso continua verdadeiro. O que ela **não** dizia é o `state`: **os deployments desta branch
falham no build**, e sempre falharam. O motivo, lido nos logs:

```
npm error enoent Could not read package.json:
  ENOENT: no such file or directory, open '/vercel/path0/package.json'
Error: Command "npm run build" exited with 254
```

O projeto Vercel roda `npm run build` em **toda** branch, e esta branch é um repositório de
inteligência em Python, sem `package.json`. **Não é defeito introduzido aqui** — a mesma
falha aparece em `claude/opportunity-commercial-priority-v1`. É a configuração de build do
site aplicada a branches que não são o site.

> **Não toquei nisso, e não vou tocar.** A regra de isolamento é explícita: Vercel está fora
> de escopo, e "consertar o Vercel" não é tarefa desta aba. Fica registrado como `CMF-05`.

`TARGET=NULL` é o que a regra de isolamento exige, e é o que foi medido. `STATE=ERROR` é
ruído de configuração alheia, e agora está dito em vez de omitido.

---

## 3 · O QUE FOI PRODUZIDO

```
NEW SOURCES                = 90 qualificadas · 43 HIGH · 47 MEDIUM
                             11 rejeitadas com motivo no código
                             + 95 rejeições da varredura preservadas em bruto
                             21 rotas não alcançadas · 1 contradição aberta
                             32 são CANAL NOVO de organização já registrada
                             45 perfis sociais declarados por 27 organizações
                             52 AUTOMATABLE · 29 com feed ou API
                             DEDUPE = PASS
                             3 CORREÇÕES ÀS MINHAS PRÓPRIAS MEDIÇÕES

NEW RAW                    = 150 bollettini ER de 2026 indexados (o mais recente 2026-09-02)
                             177 pontos da série de trappole de Halyomorpha halys (2021→2026-08-31)
                             27 objetos de fala preservados (9 áudio + 18 vídeo)

NEW NORMALIZED             = 102 objetos de vídeo pelo contrato voz.CAMPOS_VIDEO
                             0 duplicatas · 12 origens · 23 dos 32 campos declarados
                             421 menções de substância ativa ADAMA verificadas com
                             fronteira de palavra nos bollettini

NEW CLIENT-SAFE EVIDENCE   = 6 cruzamentos, todos com PROVES e DOES_NOT_PROVE escritos

NEW VOICES                 = 22 objetos de áudio (SINTONIA_WHISPER_LOCAL)
                             30 contas de Instagram em 3 lotes congelados
NEW TRANSCRIPTS            = 9 áudio V1 · 9.100 s · 130.935 caracteres · 0,00 USD
                             13 áudio V2 · 19.058 s · 286.395 caracteres · 0,00 USD
                             48 reels · 3.630 + 4.210 caracteres · 0,00 USD
                             18 vídeo · YOUTUBE_ASR_AUTO · 367.558 caracteres
                             SINAL SÓ NA FALA: 6/9 e 11/13 no áudio, 10/18 no vídeo,
                             7 de 48 nos reels
                             AUDITADO: das 11 marcas do áudio V2, 8 são inventário de
                             cultura, 3 nomeiam avversità e 1 é falso positivo do meu
                             próprio vocabulário (`grano saraceno` lido como FRUMENTO)

NEW CROSSINGS              = 7  (LINHA_DA_TABELA 4 · SUBSTANCIA_ATIVA 3)
                             6 dos 7 têm evidência que existe SÓ NA FALA
                             6 não-cruzamentos, com o motivo escrito
                             DOIS dos 7 ESFRIAM o caso em vez de esquentar

NEW OPPORTUNITIES          = 0 promovidas. 0 mudanças de status. 0 mudanças de score.
NEW CANDIDATES             = 1 proposto ao método: PATATA × ELATERIDI (Emilia-Romagna)
```

---

## 4 · CLASSIFICAÇÃO PARA A MISSÃO DO SITE

### INGESTIBLE_NOW

| arquivo | o que é |
|---|---|
| `data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json` | **90** fichas de fonte, 30 campos cada |
| `data/samples/IT-FONTES-V1/IT-FONTES-RECONFERENCIA-V1.json` | as minhas releituras host a host, e os dois handles que caíram |
| `data/samples/IT-FONTES-V1/IT-FONTES-REJEICOES-LOTE2-V1.json` | as 95 rejeições da varredura, em bruto |
| `data/samples/IT-CAMPO-V1/IT-CAMPO-SINAIS-VERIFICADOS-V1.json` | 21 sinais que sobreviveram à refutação adversarial (24 testados, 3 refutados) |
| `data/samples/IT-INSTAGRAM-V3/` | 8 contas, 48 objetos, 6 vídeos, 5 transcritos |
| `data/samples/IT-VOZ-AUDIO-V2/` | camada de áudio permanente (`scripts/it_audio.py`) |
| `data/samples/IT-CRUZAMENTO-V1/IT-CRUZAMENTOS-V1.json` | **7** cruzamentos, `CLIENT_SAFE: true` |
| `data/samples/IT-CRUZAMENTO-V1/IT-ENRIQUECIMENTO-CONFIRMADAS-V1.json` | evidência nova para **5** das 9 confirmadas — e uma delas **esfria** o caso |
| `data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-2026-INDICE.json` | índice dos 150 bollettini |
| `data/samples/IT-CAMPO-V1/IT-CIMICE-TRAPPOLE-UNIBO-SERIE.json` | série numérica por província e estádio |
| `data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json` | 421 menções verificadas |
| `data/samples/IT-VOZ-AUDIO-V1/` | 9 transcrições locais + o medidor de só-na-fala |
| `data/samples/IT-VIDEO-V1/` | 102 objetos, 18 falas, 10 sinais só-na-fala |

**IDs citáveis:** fontes `IT-SRCX-001` … `IT-SRCX-090` · cruzamentos `IT-X-2026-001` …
`IT-X-2026-007` · vídeos `YOUTUBE:<external_id>` · falas em `IT-VIDEO-V1/falas/<id>.json` ·
episódios de áudio `SPREAKER:<episode_id>` em `IT-VOZ-AUDIO-V2/`.

### NEEDS_VALIDATION

- `PATATA × ELATERIDI` — candidato novo, **não promovido**. Precisa passar pela régua de
  oportunidade, que **não é** régua desta aba.
- Reclassificar 62 `publicChannels` do pacote V2.1: parte é horticultura doméstica e quatro
  não são italianos. Proposta: `RELEVANCE: LOW` e `COUNTRY != IT`. **Não apagar.**
- `IT-X-2026-004` (cimice) — o denominador `n` de armadilhas mexe semana a semana. Qualquer
  tela que mostre a série precisa mostrar o `n` junto.

### FUTURE

- Instagram: a coleta **foi feita** em três lotes (V1, V2, V3 — 180 objetos, 48 reels
  transcritos, 0,00 USD). O que ainda precisa do runner é a **grade completa** (esta rota
  entrega 6 itens por conta, o Chrome com janela entrega 12) e os **comentários**, que
  nenhuma rota gratuita entrega.
- Transcrição própria de vídeo do YouTube — `IT_VIDEO_AUDIO=1` na máquina do runner.
- `disciplinare` da barbabietola: o elo de `OPP_2BDE8FC566CE` **foi encontrado** (o par de
  rótulo `IT-LBL-409`, SPYRALE) e ele **esfria** o caso. O disciplinare continua sendo o
  documento que diria se alguma molécula é de fato posicionada.
- Os 21 hosts em `NAO_ALCANCADAS` — TLS antigo, muro de bot, túnel 502. Estado desta saída,
  não do mundo.

### REJECTED

11 fontes com o motivo escrito em `IT-FONTES-DESCOBERTA-V1.json#REJECTED`, mais 95 em bruto
em `IT-FONTES-REJEICOES-LOTE2-V1.json`. Duas das 11 são **correções à varredura paralela**:
`anicav.it` (muro de bot vendido como conteúdo) e o LinkedIn do CSO Italy (handle não
declarado na casa do dono).

---

## 5 · CROSS_MISSION_FINDING — não corrigido aqui, de propósito

### CMF-01 · `SRC_IMAGE_LINE_COM` aponta para a empresa errada

| | |
|---|---|
| **arquivo** | pacote canônico V2.1, tabela `sources` (branch do site) |
| **problema** | `SRC_IMAGE_LINE_COM` está como `TYPE: TECHNICAL_MEDIA`, `ACCESS_STATUS: GREEN`, **sem campo `NAME`**, apontando para `image-line.com` |
| **evidência** | `image-line.com` lido em 2026-09-03: *"FL Studio — Music Production Software"*. A editora agrícola italiana é a **Image Line s.r.l.**, em `imagelinenetwork.com` |
| **impacto** | uma fonte de mídia técnica italiana que não é italiana nem agrícola. Mesma família do caso `repilouk` da Espanha |
| **owner provável** | missão dona do pacote canônico / do site |

### CMF-02 · a lista de produtos das páginas de empresa do AgroNotizie é do site, não da empresa

| | |
|---|---|
| **problema** | a rota `agronotizie.imagelinenetwork.com/aziende/<slug>/<id>` responde 200 e parece dar o portfólio da empresa |
| **evidência** | a lista de 32 produtos da página da Syngenta é **subconjunto estrito** da lista de 50 da página da ADAMA, sobreposição 32/32, e os mesmos itens aparecem na home do Fitogest |
| **impacto** | ler portfólio de concorrente dali produziria afirmação que não existe |
| **owner provável** | quem consumir competitor products |

### CMF-03 · duas contagens de resistência que não batem

| | |
|---|---|
| **problema** | o GIRE declara *Echinochloa crus-galli* resistente a propanil (HRAC 5 / C2) em Piemonte, Lombardia e Toscana desde 2000; o sumário por país do `weedscience.org` lido em 2026-09-03 mostra a Itália com **zero** no grupo HRAC 5 |
| **impacto** | toca `OPP_4C39CCC05EEB` (RISO × ECHINOCHLOA). É `INVESTIGATE`, **não** um número a escolher |
| **estado** | registrada como `IT-CONTRA-001` em `IT-FONTES-DESCOBERTA-V1.json#OPEN_CONTRADICTIONS`. A linha 36 da tabela de Heap foi conferida por mim: `Total 29 \| HRAC1 8 \| HRAC2 15 \| HRAC5 0 \| HRAC9 4 \| HRAC4 1`. Os grupos somam 29 |
| **owner provável** | camada de ciência/resistência |

### CMF-05 · o projeto Vercel roda o build do site em toda branch

| | |
|---|---|
| **arquivo** | configuração do projeto `sintonia-eame-preview` (Vercel), não versionada nesta branch |
| **problema** | o build command é `npm run build` e roda em **qualquer** branch. Branches que não são o site não têm `package.json` e falham com `ENOENT ... exited with 254` |
| **evidência** | logs de `dpl_DqANDFPjkyvxZQGWEHkDCX2ki9Cb` (esta branch) e o mesmo estado em `claude/opportunity-commercial-priority-v1` |
| **impacto** | ruído: todo push de branch de inteligência gera um preview vermelho. Nenhum efeito em produção — `target` continua `null` |
| **owner provável** | quem administra o projeto Vercel / a missão do site |
| **por que não corrigi** | a regra de isolamento proíbe explicitamente alterar configuração da Vercel e "tentar consertar o Vercel". Registrado, não tocado |

### CMF-04 · uma afirmação do repositório ficou velha, e foi datada em vez de reescrita

`docs/descoberta/CAMADA-DE-VOZ-ESPANHA.md` dizia *"França e Itália não foram abertas"*. A
frase continua verdadeira **sobre aquela missão** e foi preservada; um adendo datado registra
que a camada de voz italiana foi aberta em 2026-09-03. **A França continua não aberta**, e o
veredito daquela seção — a voz não antecipa no tempo — continua valendo.

---

## 6 · UM ARQUIVO COMPARTILHADO FOI ALTERADO, E ISSO PRECISA SER DITO

`scripts/voz.py` é o contrato de vídeo (32 campos) e é **compartilhado com a linhagem
espanhola**. Ele foi **estendido, nunca reescrito**:

- os vocabulários espanhóis (`VOCAB_CROP`, `VOCAB_ISSUE`, `VOCAB_MOLECULE`, `VOCAB_LUGAR`)
  continuam **byte a byte** onde estavam e continuam sendo o **padrão**;
- os italianos entram como dicionários **novos e separados** (`*_IT`);
- `marcar_assunto`, `marcar_molecula_e_lugar` e `pipeline_video` passaram a **aceitar** o
  vocabulário por injeção — sem argumento, o comportamento é exatamente o de antes;
- o relatório do pipeline passou a declarar **qual** vocabulário rodou
  (`VOCAB_DECLARED`), porque dois países produzindo `CROP` com réguas diferentes sem dizer
  qual é o defeito que a cobertura por campo existe para impedir.

Os 329 testes passam antes e depois.

---

## 7 · A FRONTEIRA QUE ESTA ABA NÃO ATRAVESSOU

O Scrap decidiu apenas o que lhe cabe: **vale coletar · quem é a fonte · o conteúdo é
relevante · qual a proveniência · há sinal no transcript · qual crop e topic aparecem.**

Ele **não** decidiu `SALES_READY`, `ACT_NOW`, produto recomendado nem oportunidade
confirmada. Por isso:

```
NEW VERIFIED = nenhuma
STATUS CHANGES = 0
SCORE CHANGES  = 0
```

Nenhuma fonte foi direto para o portal. O caminho foi
`RAW → NORMALIZED → QA → CANONICAL/CANDIDATE`, e o que está em `CANDIDATE` continua em
`CANDIDATE`.
