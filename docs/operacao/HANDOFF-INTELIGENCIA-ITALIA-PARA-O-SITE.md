# HANDOFF — INTELIGÊNCIA ITÁLIA → MISSÃO DO SITE

**Esta aba produz inteligência. Ela não publica o portal.**
Nada aqui foi ingerido no site. O site é outro consumidor, e a ingestão é decisão dele.

---

## 0 · IDENTIDADE

```
BRANCH  = claude/adama-italia-source-discovery-oui6ma
HEAD    = 510ccb1
TREE    = limpa
TESTES  = 329, 0 falhas
```

Commits desta aba, todos nesta branch e em nenhuma outra:

```
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

Os 6 pushes desta aba foram **todos** para `claude/adama-italia-source-discovery-oui6ma`.
Nenhum push, merge, rebase ou fast-forward em `claude/site-v21-ingest-recovery`,
`claude/eame-competitor-public-communication` ou `claude/sintonia-eame-repo-setup-xccfob`.
As branches do site foram **lidas** (`git fetch`) para consultar o corpus canônico da Itália,
e nunca escritas.

---

## 2 · CHECAGEM DE PRODUÇÃO

Feita por **leitura**, sem CLI, sem deploy, sem alias, sem tocar em configuração.

O projeto Vercel ligado a `lucianodalondon-sys/eame-sintonia` é **`sintonia-eame-preview`**
(`prj_rKjzMNHiB2ulP8ev5bmYYeUFUTwe`, team `london-creative`).

Os 6 pushes desta branch produziram 6 deployments, **todos com `target: null` (preview)**:

| DEPLOYMENT | HEAD | TARGET | criado (UTC) |
|---|---|---|---|
| `dpl_4dK6AvzYqyBRxyhvG1eBHyTbgmdB` | 510ccb1 | **null** | 2026-09-03 12:26 |
| `dpl_B7LnJg84rA7izJ8SsDQbKoBHiDtp` | 809328f | **null** | 2026-09-03 12:25 |
| `dpl_59NwZJC3Bp7wa8CpMaF1hnFYJ5id` | 4e3bce4 | **null** | 2026-09-03 11:53 |
| `dpl_AJpaBTPHPVHB1WSAW8Uhkz1dkQBG` | ca464f9 | **null** | 2026-09-03 11:51 |
| `dpl_DXzAXVP2Ziydh7UHZqj69Xuqbz5o` | 30b06bf | **null** | 2026-09-03 11:47 |
| `dpl_BTyabSiAx7bdYVWcKkpyryz3ShGM` | 2f44fe3 | **null** | 2026-09-03 11:37 |

Nenhum preview foi promovido, testado como site oficial, aliasado ou associado a domínio.

> **Limite honesto da checagem:** foram lidos os **20 deployments mais recentes** do projeto.
> Nesses 20 não há **nenhum** `target=production` — de nenhuma branch. Isso é o que foi lido,
> e não uma afirmação sobre todo o histórico.

---

## 3 · O QUE FOI PRODUZIDO

```
NEW SOURCES                = 43 qualificadas · 22 HIGH · 21 MEDIUM
                             9 rejeitadas com motivo · 14 rotas não alcançadas
                             12 são CANAL NOVO de organização já registrada
                             34 perfis sociais declarados por 16 organizações
                             DEDUPE = PASS

NEW RAW                    = 150 bollettini ER de 2026 indexados (o mais recente 2026-09-02)
                             177 pontos da série de trappole de Halyomorpha halys (2021→2026-08-31)
                             27 objetos de fala preservados (9 áudio + 18 vídeo)

NEW NORMALIZED             = 102 objetos de vídeo pelo contrato voz.CAMPOS_VIDEO
                             0 duplicatas · 12 origens · 23 dos 32 campos declarados
                             421 menções de substância ativa ADAMA verificadas com
                             fronteira de palavra nos bollettini

NEW CLIENT-SAFE EVIDENCE   = 6 cruzamentos, todos com PROVES e DOES_NOT_PROVE escritos

NEW VOICES                 = 9 objetos de áudio (SINTONIA_WHISPER_LOCAL)
NEW TRANSCRIPTS            = 9 áudio  · 9.100 s · 130.935 caracteres · 0,00 USD
                             18 vídeo · YOUTUBE_ASR_AUTO · 367.558 caracteres
                             SINAL SÓ NA FALA: 6 de 9 no áudio, 10 de 18 no vídeo

NEW CROSSINGS              = 6  (LINHA_DA_TABELA 3 · SUBSTANCIA_ATIVA 3)
                             5 dos 6 têm evidência que existe SÓ NA FALA
                             4 não-cruzamentos, com o motivo escrito

NEW OPPORTUNITIES          = 0 promovidas. 0 mudanças de status. 0 mudanças de score.
NEW CANDIDATES             = 1 proposto ao método: PATATA × ELATERIDI (Emilia-Romagna)
```

---

## 4 · CLASSIFICAÇÃO PARA A MISSÃO DO SITE

### INGESTIBLE_NOW

| arquivo | o que é |
|---|---|
| `data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json` | 43 fichas de fonte, 30 campos cada |
| `data/samples/IT-CRUZAMENTO-V1/IT-CRUZAMENTOS-V1.json` | 6 cruzamentos, `CLIENT_SAFE: true` |
| `data/samples/IT-CRUZAMENTO-V1/IT-ENRIQUECIMENTO-CONFIRMADAS-V1.json` | evidência nova para 4 das 9 confirmadas |
| `data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-2026-INDICE.json` | índice dos 150 bollettini |
| `data/samples/IT-CAMPO-V1/IT-CIMICE-TRAPPOLE-UNIBO-SERIE.json` | série numérica por província e estádio |
| `data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json` | 421 menções verificadas |
| `data/samples/IT-VOZ-AUDIO-V1/` | 9 transcrições locais + o medidor de só-na-fala |
| `data/samples/IT-VIDEO-V1/` | 102 objetos, 18 falas, 10 sinais só-na-fala |

**IDs citáveis:** fontes `IT-SRCX-001` … `IT-SRCX-043` · cruzamentos `IT-X-2026-001` …
`IT-X-2026-006` · vídeos `YOUTUBE:<external_id>` · falas em `IT-VIDEO-V1/falas/<id>.json`.

### NEEDS_VALIDATION

- `PATATA × ELATERIDI` — candidato novo, **não promovido**. Precisa passar pela régua de
  oportunidade, que **não é** régua desta aba.
- Reclassificar 62 `publicChannels` do pacote V2.1: parte é horticultura doméstica e quatro
  não são italianos. Proposta: `RELEVANCE: LOW` e `COUNTRY != IT`. **Não apagar.**
- `IT-X-2026-004` (cimice) — o denominador `n` de armadilhas mexe semana a semana. Qualquer
  tela que mostre a série precisa mostrar o `n` junto.

### FUTURE

- Coleta de Instagram — o lote está congelado em
  `data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-IT-SOCIAL-BATCH-V1.json` (32 contas,
  `READY_TO_COLLECT_WHEN_RUNNER_AVAILABLE`). Precisa do runner com navegador.
- Transcrição própria de vídeo do YouTube — `IT_VIDEO_AUDIO=1` na máquina do runner.
- `disciplinare` da barbabietola, para fechar `OPP_2BDE8FC566CE`.

### REJECTED

9 fontes, com o motivo escrito em `IT-FONTES-DESCOBERTA-V1.json#REJECTED`.

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
| **owner provável** | camada de ciência/resistência |

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
