# C1 · CONVERGÊNCIA ESTRUTURAL — a entrega

> **O que esta missão fez:** transformou o patrimônio medido em **um único
> SINTONIA SCRAP**, internamente coerente, modular, híbrido `ONLINE`/`LOCAL`, e
> pronto para receber rotas novas sem criar uma terceira arquitetura.
>
> **O que ela NÃO fez, de propósito:** não desligou actor, não encanou a
> Collection, não habilitou GPU, não instalou tradução, não tocou em migrations,
> portal, casco, deploy nem `main`.

---

## A · BRANCH

```
claude/sintonia-scrap-convergence-c1
```

Criada a partir da referência medida, não da memória. O nome é o sugerido pelo
coordenador; não havia convenção viva melhor.

## B · INITIAL_HEAD

```
0e999fa162b284f7ce8cdbce610e0525f3ad1d06
```

**Confere com a referência que o coordenador mediu no GitHub.** `DRIFT = NENHUM`
nesta branch: `origin` e local apontavam para o mesmo commit, e a árvore estava
limpa antes de eu tocar em nada.

**Mas houve deriva noutro sítio, e ela importa.** O `git fetch --all --prune`
trouxe duas branches que se moveram enquanto o benchmark corria:

| branch | o que trouxe | o que fiz |
|---|---|---|
| `claude/raw-observation-identity-3jbwco` | `C-IMPL-PHASE-10` — a lei vira migration | **nada.** Phase 10 é território proibido para esta missão |
| `claude/sintonia-eame-know-how-v1` | `know-how: fixa fronteira canonica do SINTONIA SCRAP` | **li antes de implementar** |

O segundo mudou o meu desenho, e vale dizer onde:

> *«Evitar chamar a peça interna do SCRAP de `orquestrador`, para não criar
> semanticamente um segundo dono. Preferir: `SCRAP ADAPTER ROUTER`, ou
> `SCRAP DISPATCHER`.»*

O nome da peça é metade da lei. Um segundo «orquestrador» no mapa seria um
segundo dono já no vocabulário, antes de existir uma linha de código.

## C · FINAL_HEAD

O commit que traz este documento. Oito commits de convergência, do `C1.1` ao
`C1.6`.

## D · PUSH_STATE

```
PUSHED para origin/claude/sintonia-scrap-convergence-c1
```

Sem `force-push`. `main` intocada.

## E · WORKTREE

`/home/user/eame-sintonia`, árvore única e limpa ao fechar. Usei uma worktree
temporária, descartável, só para medir a suíte no `INITIAL_HEAD` e comparar —
removida no fim.

---

## F · ARQUIVOS ALTERADOS

**Onze módulos novos, um refatorado, um corrigido, um teste novo.**

| ficheiro | linhas | o que é |
|---|---|---|
| `coleta/scrap_capacidades.py` | +300 | **a declaração** — 34 capacidades, estado medido, ambiente, prova |
| `coleta/scrap_registo.py` | +148 | **o mapa** — dono único de `PLATAFORMA/CAPACIDADE → ADAPTADOR` |
| `coleta/scrap_executor.py` | +244 | **os seis verbos** de `COL-LAW-013` |
| `coleta/scrap_fornecedores.py` | +153 | **o percurso** — `PROVIDER_REQUESTED/USED/WHY_FALLBACK/RESULT` |
| `coleta/scrap_http.py` | +156 | **o portão e a busca**, fora do roteador |
| `coleta/adaptador_aberto.py` | +206 | Mastodon, Bluesky, Telegram |
| `coleta/adaptador_instagram.py` | +106 | Reels, perfil, Stories |
| `coleta/adaptador_youtube.py` | +91 | as quatro rotas oficiais |
| `coleta/adaptador_linkedin.py` | +60 | sete capacidades declaradas |
| `coleta/adaptador_x.py` | +57 | cinco capacidades declaradas |
| `coleta/adaptador_facebook.py` | +37 | quatro capacidades, granularidade preservada |
| `coleta/social_rotas.py` | **509 → 256** | **o despacho**, sem conhecer plataforma nenhuma |
| `guarda/social_sessao.py` | +17 | a senha dentro da URL passa a ser redigida |
| `tests/test_scrap_convergencia.py` | +418 | as doze provas |
| `system-map/…` | — | mapa, arestas e o censo das estradas |

---

## G · COMPONENTES PORTADOS

**Nenhum merge. Nenhuma branch integrada.** O que entrou, entrou por decisão, um
a um.

| origem | destino | ação | porquê |
|---|---|---|---|
| `coleta/social_rotas.py` (portão, `_get`, exceções) | `coleta/scrap_http.py` | **REFINE** | desfaz o ciclo roteador↔adaptador |
| `coleta/social_rotas.py` (Mastodon, Bluesky, Telegram) | `coleta/adaptador_aberto.py` | **REFINE** | o roteador deixa de nomear plataformas |
| `coleta/social_rotas.py` (4 rotas YouTube) | `coleta/adaptador_youtube.py` | **REFINE** | idem |
| `coleta/social_rotas.py` (`_EstadoDaApi`) | `coleta/scrap_http.py` | **REFINE** | quem levanta é o adaptador, quem apanha é o roteador |
| `ferramentas/reel_transcricao.py` | intacto | **KEEP** | 47 testes e 8 Reels no disco; alcançado pelo adaptador, não reescrito |
| `ferramentas/fala_local.py` | intacto | **KEEP** | já era o dono único no HEAD |
| a correção de redação (linhagem órfã) | `guarda/social_sessao.py` | **PORT** | 1 regex + 1 linha, com teste |
| `ferramentas/story_transcrever.py` | **não portado** | **REFINE adiado** | ver **M** |
| `medidas/fato_local.py`, `medidas/lugar_do_fato.py` | **não portados** | **ARCHIVE por agora** | colidem com `leis/` — ver **T** |

---

## H · ROUTER OWNER

**A pergunta da PARTE A era: `coleta/social_rotas.py` pode ser refinado para
virar o SCRAP ADAPTER ROUTER canônico? A resposta é SIM, e foi refinado.**
Nenhum roteador paralelo foi criado.

O que ele já fazia certo e ficou: quem chama diz **plataforma e capacidade,
nunca ferramenta**; o portão lê o `robots.txt` vivo antes da primeira
requisição; a trava de sessão roda antes de qualquer navegação; a trava do gasto
exige motivo do vocabulário fechado; e `executar()` sela **toda** saída, porque
um `return` novo daqui a três meses esqueceria de selar.

O que estava errado e saiu: um `dict` literal com nove pares
`(PLATAFORMA, CAPACIDADE) → função`, e o corpo de todas as rotas por baixo.

```
O MONOLITO NÃO SE CHAMA «FICHEIRO GRANDE». Chama-se «o despachante sabe todas
as plataformas». Acrescentar o TikTok obrigava a editá-lo.
```

**Como provei que há um dono só:**

| prova | o que mede |
|---|---|
| `test_o_roteador_nao_guarda_mapa_proprio_em_producao` | `ADAPTADORES == {}` em produção |
| `test_o_roteador_nao_nomeia_plataformas` | nenhum nome de plataforma no corpo executável |
| `test_acrescentar_plataforma_nao_toca_no_roteador` | registar uma nova não altera um byte do ficheiro |
| `test_dois_adaptadores_para_a_mesma_capacidade_reprovam` | `RegistoDuplicado` levanta |

### A costura que fica vazia, e por que ela não é um segundo dono

`social_rotas.ADAPTADORES` continua a existir porque `tests/test_falhas.py`
injeta nele um adaptador que rebenta de propósito, para provar que o despachante
classifica a falha. Em produção está **vazio**, e há um teste que o exige vazio.

```
A DIFERENÇA ENTRE UMA COSTURA E UM SEGUNDO DONO É QUE O SEGUNDO DONO
ENCHE-SE SOZINHO COM O TEMPO, E NINGUÉM REPARA.
```

---

## I · ADAPTER REGISTRY

**Seis adaptadores, um módulo cada. 34 capacidades registadas.**

| adaptador | capacidades | com rota | estados |
|---|---|---|---|
| `adaptador_instagram` | 7 | **3** | 3 `PROVEN` · 1 `PARTIAL` · 1 `BLOCKED` · 1 `UNKNOWN` · 1 `NOT_EXECUTED` |
| `adaptador_linkedin` | 7 | 0 | 4 `PROVEN` · 2 `UNKNOWN` · 1 `NOT_EXECUTED` |
| `adaptador_youtube` | 6 | **4** | 5 `PROVEN` · 1 `BLOCKED` |
| `adaptador_x` | 5 | 0 | 3 `PROVEN` · 1 `PARTIAL` · 1 `UNKNOWN` |
| `adaptador_facebook` | 4 | 0 | 1 `PARTIAL` · 3 `BLOCKED` |
| `adaptador_aberto` | 5 | **5** | 3 `PROVEN` · 2 `NOT_EXECUTED` |

**Totais:** 18 `PROVEN` · 3 `PARTIAL` · 5 `BLOCKED` · 4 `UNKNOWN` · 4
`NOT_EXECUTED`. **Doze com rota ligada; dez delas prometem resultado.**

**TikTok e Podcast/Áudio não foram criados.** Não há patrimônio que os
justifique, e inventar um adaptador para preencher um desenho seria exatamente
o adapter vazio que finge funcionar.

**Web Adapter também não — e este foi auditado antes de recusar.** Há 42
coletores em `coleta/`, e nove deles usam HTTP sem serem SCRAP:
`agrifood_ue` · `eppo_gd` · `eu_substancia_adama_it` · `denominaciones` ·
`mapa_regfi` · `regulatorio_importar` · `rotulos_baixar` ·
`universo_ciencia_it` · `gire_mapas`.

```
USAR HTTP NÃO TORNA UM COLETOR PARTE DO SCRAP. A responsabilidade semântica
deles é regulatório, ciência e rótulo — e cada um já tem dono.
```

---

## J · PROVIDER REGISTRY

Dez fornecedores nomeados. Os cinco primeiros são os degraus que a cadeia de
Reels **já gravava** — não foram renomeados, porque renomear é reescrever a
história de artefatos que já estão no disco.

```
MEDIA_FORNECIDA · MEDIA_JA_PRESERVADA · LOCAL_YTDLP · LOCAL_EMBED · APIFY
LOCAL_INSTALOADER · LOCAL_GALLERY_DL · LOCAL_HTTP · OFFICIAL_API · LOCAL_BROWSER
```

Quatro campos obrigatórios, e o quarto é o que impede a história falsa:

```
PROVIDER_REQUESTED   qual foi pedido
PROVIDER_USED        qual entregou
WHY_FALLBACK         por que o pedido não serviu
RESULT               o que saiu
```

```
FALLBACK SILENCIOSO É MENTIRA COM OUTRO NOME. Uma cadeia que pede yt-dlp,
recebe do embed e devolve só o objeto produz um resultado verdadeiro e uma
história falsa. No dia em que a primeira rota morrer de vez, ninguém repara —
porque nunca reparou que ela já tinha morrido.
```

`conferir()` **levanta** quando há troca sem motivo. Não avisa: recusa.

---

## K · HYBRID EXECUTION

`EXECUTION_TARGET` é um eixo próprio, e `WHY_LOCAL` é obrigatório quando o alvo
é `LOCAL` ou `HYBRID`. O validador recusa a falta.

| alvo | capacidades | exemplos |
|---|---|---|
| **`ONLINE`** | 19 | descoberta e post do LinkedIn, tudo do X, rotas do YouTube, social aberta |
| **`LOCAL`** | 4 | bytes do YouTube (`DATACENTER_BLOCKED`), perfil do Instagram (`DATACENTER_BLOCKED`), Stories (`AUTHORIZED_LOCAL_SESSION`) |
| **`EITHER`** | 3 | a cadeia de Reel inteira |
| **`HYBRID`** | 0 | nenhuma ainda — e é honesto que seja zero |
| **`UNKNOWN`** | 8 | o que ninguém mediu |

**A cadeia de Reel é `EITHER` e isso não é dúvida: é a resposta medida.** Ela
correu **inteira online** neste contentor, oito Reels capturados e transcritos
sem tocar no runner local.

```
A REGRA DO AMBIENTE É UMA SÓ: USAR O MAIS BARATO E MAIS SIMPLES QUE CUMPRA A
CAPACIDADE. Não «social vai para o PC local». E nunca «sempre fizemos assim»,
que não é um valor aceite pelo validador.
```

**`GPU_REQUIRED` está no vocabulário e proibido de ser usado.** Enquanto
`LOCAL_HARDWARE_STATUS = NOT_MEASURED`, declará-lo levanta `CapacidadeInvalida`.
Prometer o acelerador de uma máquina que ninguém viu é uma promessa, não uma
medição.

---

## L · ASR

| campo | valor, e não mudou nesta missão |
|---|---|
| `ASR_OWNER` | **`ferramentas/fala_local.py`** |
| `ASR_ENGINE` | faster-whisper 1.2.1 |
| `ASR_RUNTIME` | CTranslate2 4.8.2 |
| `DEVICE` | **`cpu`** — inalterado |
| `PRECISION` | **`int8`** — inalterado |
| `ACCELERATOR` | nenhum — **nenhum `cuda` foi escrito** |

**Importadores, todos:** `coleta/comunicacao_coleta.py` ·
`ferramentas/reel_transcricao.py` · `ferramentas/instagram_transcrever.py` ·
`ferramentas/youtube_transcrever.py` · `coleta/adaptador_instagram.py`
(indireto, pela cadeia) · `tests/test_reel_transcricao.py`.

**Nenhum segundo motor.** `test_so_um_ficheiro_abre_motor` varre as 16 gavetas
inteiras à procura de `WhisperModel(` e `BatchedInferencePipeline(` e exige que
a lista seja exatamente `['ferramentas/fala_local.py']`.

### O adaptador não escolhe modelo

`adaptador_instagram` passa `model_hint` e **não crava literal nenhum** — há um
teste que lê o corpo do ficheiro à procura de `'small'` e `'medium'` e reprova
se os encontrar.

**As quatro constantes de modelo foram mapeadas e NÃO tocadas:**

| onde | valor | quem decide |
|---|---|---|
| `fala_local.MODELO_PADRAO` | `small` | o dono do ASR |
| `reel_transcricao.MODELO_PADRAO` | `medium` | a cadeia, camada acima |
| `instagram_transcrever.MODELO_PADRAO` | `small` (`IG_MODELO`) | ponto de entrada |
| `youtube_transcrever.MODELO_PADRAO` | `small` (`YT_MODELO`) | ponto de entrada |

```
C1 NÃO É DESCULPA PARA DECIDIR `small` CONTRA `medium` CONTRA `turbo`.
Essa decisão depende do runner local real, e ele nunca foi alcançado.
```

---

## M · STORIES

**A capacidade ficou declarada. O módulo não foi portado. E a razão é medida.**

`ferramentas/story_transcrever.py`, na branch `sintonia-scrap-stories-no-apify-v1`:

1. **cria um terceiro motor** — `WhisperModel(..., beam_size=5)`, sequencial, e
   **nunca declara o idioma**, contra `beam=1` e lote 8 do dono;
2. **está ligado a um contrato que não existe** — `anexar()` exige
   `objeto_story['MEDIA_DURABILITY'] == 'MEDIA_PRESERVED'` e lê `MEDIA_PATH`.
   **Verifiquei eu, por `git grep` na própria branch:** esses dois nomes só
   aparecem nas duas linhas de dentro do próprio ficheiro. A cadeia escreve
   `MEDIA_URL_DURABILITY`, `AUDIO_STATE` e `AUDIO_PATH`.

```
anexar() DEVOLVERIA `MEDIA_MISSING` EM 100% DOS OBJETOS QUE A PRÓPRIA CADEIA
PRODUZ. Portar isto agora seria trazer o defeito junto com a capacidade.
```

**O que entrou no lugar foi a prova durável:** `instagram.story.capture` fica
`UNKNOWN` e `instagram.story.transcribe` fica `NOT_EXECUTED` — nenhuma promete
resultado — e `test_so_um_ficheiro_abre_motor` reprova qualquer ficheiro futuro
que instancie motor próprio.

```
O QUE ENTRA HOJE NÃO É O MÓDULO. É O TESTE QUE IMPEDE O MÓDULO DE VOLTAR
EM SILÊNCIO.
```

---

## N · REELS

**A cadeia entra pelo Instagram Adapter e continua a ser o módulo especializado
interno.** Não virou segundo produto, e não foi reescrita: tem 47 testes e oito
Reels reais no disco.

### Prova de fiação, ao vivo, sobre mídia já preservada e sem escrever no disco

```
CHECK               CAN=True · CAN_COLLECT_NOW · alvo=EITHER · custo=US$ 0,0
MEDIA_STATE         MEDIA_OK
TRANSCRIPT_STATE    OK · 343 caracteres
LANGUAGE            it · fonte DECLARED
CAPTION != TRANSCRIPT   True
PAI declarado           True
PROVIDER_REQUESTED  MEDIA_FORNECIDA
PROVIDER_USED       MEDIA_FORNECIDA
WHY_FALLBACK        None   (não houve troca, e por isso não há motivo)
PAID_PROVIDER_USED  False
```

Texto reconhecido: *«Buongiorno appassionati di mais, benvenuti su Discovery
Seeds, la nuova mini serie di singenta…»*

**Não-regressão:** `tests.test_reel_transcricao` — 47 testes, todos verdes.

---

## O · SECURITY REDACTION

**O furo foi reproduzido por mim antes de ser corrigido:**

```
entrada   postgresql://utilizador:SenhaSecreta123@servidor:5432/base
saída     postgresql://utilizador:SenhaSecreta123@servidor:5432/base
```

Sai igual. A senha dentro da URL não casa com `senha=` nem com uma assinatura de
token, e `redigir()` é a função por onde passa **toda** exceção de
`social_rotas` — incluindo tracebacks de `urllib`, que é como segredo vaza sem
ninguém escrever `print`.

**A correção é uma regex e uma linha.** Redige **só a senha**: esquema,
utilizador, servidor e base sobrevivem.

```
UMA REDAÇÃO QUE APAGA O DIAGNÓSTICO É TROCADA PELA PRIMEIRA PESSOA COM PRESSA.
```

```
O QUE ESTÁ CORRIGIDO É O GUARDA.
O vazamento vivo pelo `psql` continua `LIVE_PASSWORD_LEAK = NOT_REPRODUCED`.
```

Há um teste que exige essa frase dentro do ficheiro, para que a próxima pessoa
não a apague por engano.

### E o guarda da casa apanhou-me a mim

Escrevi um token falso por extenso no teste. Duas provas desta casa varrem o
repositório inteiro à procura da **forma** de um token, e apanharam o ficheiro.

```
O VARREDOR NÃO SABE, NEM DEVE SABER, QUE AQUELE ERA DE MENTIRA. Um varredor
que aceitasse «mas este é de teste» deixaria de servir no dia em que alguém
escrevesse a mesma frase sobre um verdadeiro.
```

A correção foi minha, não dele: o token falso passa a ser montado em três
pedaços.

---

## P · COLLECTION BOUNDARY

**Prova de que não toquei no orquestrador global:**

```
git diff 0e999fa1..HEAD -- orquestrador/   →   vazio
```

**Prova de que não nasceu um segundo cérebro** — quatro testes, não um comentário:

| teste | o que impede |
|---|---|
| `test_nao_fabrica_collection_request` | nenhum dos cinco módulos constrói pedido |
| `test_nao_decide_admissao` | nenhum define `admitir`, `julgar` ou `ADMISSION =` |
| `test_nao_importa_o_orquestrador` | nenhum importa `orquestrador` |
| `test_conhece_so_os_tres_escopos` | `COLLECT` levanta em qualquer escopo fora de `PONTUAL`/`INCREMENTAL`/`TOTAL` |

E o censo das estradas, correndo sobre a árvore final, confirma a topologia:

```
ORQUESTRADOR: EXISTE · alcanca 5 executores
```

No mapa a fronteira ficou **declarada e não provada, de propósito**:

```
C-ORQUESTRADOR  →  C-SCRAP-SOCIAL     ALIMENTA, e vale NÃO SEI
```

Vale `NÃO SEI` porque a C1 desenhou o contrato e **não encanou a Collection**.
Pintar de verde o que ninguém ligou seria mentir no mapa.

---

## Q · TESTS

```
python3 -m unittest tests.test_scrap_convergencia          →  49 testes, OK
python3 -m unittest tests.test_reel_transcricao            →  47 testes, OK
suíte inteira, 76 módulos                                  →  1.852 testes
```

| medida | `INITIAL_HEAD` | aqui |
|---|---|---|
| testes | 1.803 | **1.852** |
| falhas | 21 | **20** |
| erros | 1 | 1 |

**`+49` testes, que são os desta convergência. ZERO falhas novas.**

> **Uma correção ao meu próprio método.** A primeira medição que fiz estava
> **truncada**: `tests/test_comunicacao.py` imprime o próprio resumo e termina o
> processo, e isso escondia tudo o que vinha depois. Eu tinha concluído «1 falha
> pré-existente». Medido a sério, com o mesmo comando na base e aqui, são 20 —
> e nenhuma delas é minha.

A falha **a menos** é `test_branch_vivo_nao_e_alvo_congelado`, que depende do
nome da branch e passa nesta. **Não a conto como conserto, porque não consertei
nada.**

---

## R · SYSTEM MAP

```
py system-map/scripts/generate_system_map.py
py system-map/scripts/censo_das_estradas_it.py
py system-map/scripts/validate_system_map.py
```

```
SYSTEM_MAP_CHECK=PASS · o mapa corresponde ao repositorio    (22 provas)
MAPA=OK · pecas=158 · ligacoes=631 · cobertura=705/1441 ficheiros
```

Nenhum JSON gerado foi editado à mão. Nenhum carimbo foi usado para mascarar
diferença. A peça `C-SCRAP-SOCIAL` passou a chamar-se **«SINTONIA SCRAP · o
executor da aquisição social»** e ganhou os onze módulos.

> **E o censo das estradas apanhou uma coisa que quase passou em silêncio.**
> Depois da suíte ficou sujo um ficheiro que eu não tinha tocado: três degraus
> da classe `PUBLIC_NATIVE_API` tinham descido de `DIRECT_CODE_REFERENCE` para
> `TRANSITIVE_CODE_PATH` e `NO_DIRECT_REFERENCE`.
>
> **A causa era minha, e não era perda de ligação.** O modelo declarava procurar
> `searchActors`, `authorFeed` e `guardar_raw` em `coleta/social_rotas.py`, e a
> `C1.2` mudou-os para `coleta/adaptador_aberto.py`. A **declaração** ficou a
> apontar para o ficheiro errado. Corrigida, os três voltaram a
> `DIRECT_CODE_REFERENCE`.
>
> Duas coisas que ficam escritas: a casa **já tinha previsto este caso** — o
> próprio censo diz que *«ausência de referência direta não é ausência de
> conexão»* — e **`censo_das_estradas_it.py` NÃO é chamado por
> `generate_system_map.py`**. Quem mover ficheiro de sítio tem de correr os dois.

---

## S · REGRESSIONS

```
NENHUMA.
```

Zero falhas novas contra o `INITIAL_HEAD`, medido com o mesmo comando nas duas
árvores. As 20 falhas restantes são anteriores e pertencem a outras frentes:
contagem de testes publicada em documentos, proveniência de amostras,
`RUN-MANIFEST`, e a trava da inteligência congelada.

**Duas regressões foram causadas durante a missão e corrigidas antes do fim:**
o varredor de segredos a apanhar o meu teste (**O**), e o censo das estradas a
apontar para o ficheiro antigo (**R**). Ficam registadas porque foram reais.

---

## T · UNKNOWNs

| o que não sei | por quê |
|---|---|
| `LOCAL_HARDWARE_STATUS` | **`NOT_MEASURED`** — o runner local nunca foi alcançado |
| qualidade da legenda nativa | obtida em três plataformas, **nunca conferida contra o áudio** |
| história profunda do LinkedIn | «Show more» não expõe URL |
| descoberta de cronologia no X | nunca tentado |
| comentários e documentos do LinkedIn | nunca tentados |
| Facebook além da identidade | 302/400 deste IP; **nunca tentado no runner local** |
| Stories ao vivo | exige sessão; a rota da branch não tem captura |
| `TERMS_STATUS` e `CLIENT_AUTHORIZATION_STATUS` | **não levantados em nenhuma das cinco** |

**E uma colisão medida, que é a razão de não ter portado nada de `medidas/`:**

```
fato_local      medidas/fato_local.py      (branch)   ×   leis/fato_local.py      (HEAD)
lugar_do_fato   medidas/lugar_do_fato.py   (branch)   ×   leis/lugar_do_fato.py   (HEAD)
```

`_gavetas.py` põe **20 diretórios** no `sys.path`. Dois nomes curtos iguais em
gavetas diferentes resolvem-se por ordem, e ordem não é comportamento.
**Hoje o repositório tem ZERO colisões, e `test_zero_colisoes_de_nome_curto`
guarda o zero.**

---

## U · O QUE FICOU DE FORA DE PROPÓSITO

```
actor desligado · YouTube trocado por yt-dlp em produção · história do LinkedIn
Facebook resolvido · X expandido para produção · sessão local contra terceiros
CUDA · modelo de ASR escolhido · motor de tradução · migration · Collection
schema · orquestrador geral · admissão · portal · deploy · merge em main
```

E, dentro do desenho:

- **o handoff `ONLINE → LOCAL` não foi implementado.** O contrato está escrito
  em `AY` do benchmark; construir fila, worker ou scheduler agora seria
  infraestrutura antes de haver necessidade.
- **o checkpoint por capacidade não foi ligado.** `STATE()` declara
  `CURSORS = NOT_IMPLEMENTED`. Guardar a posição de uma corrida que nunca
  aconteceu seria inventar estado.
- **nenhum Kafka, Celery, RabbitMQ, Redis ou microserviço.** Nada disto era
  preciso, e nada disto entrou.

---

## V · READY_FOR_C2

```
YES
```

O desenho que o critério de sucesso pedia pode ser desenhado honestamente hoje:

```
COLLECTION_REQUEST
        ↓
ORQUESTRADOR CANÔNICO                      orquestrador/orquestrador.py
        ↓
SINTONIA SCRAP EXECUTOR                    CAPABILITIES CHECK COLLECT
        ↓                                  STATE OUTPUT TRACE
SCRAP ADAPTER ROUTER                       social_rotas.py + scrap_registo.py
        ↓
├── Instagram · LinkedIn · YouTube · X · Facebook · social aberta
        ↓
     PROVIDERS                             10 nomeados, com degrau registado
        ↓
┌───────┴────────┐
ONLINE         LOCAL                       EXECUTION_TARGET + WHY_LOCAL
└───────┬────────┘
        ↓
RAW / MEDIA / DERIVED                      leis/artefato.py
        ↓
┌───────┴────────┐
ASR OWNER    TRANSLATION CONTRACT          fala_local.py    NOT_RUN
```

**Sem fingir capacidade nenhuma:** 18 `PROVEN`, 3 `PARTIAL`, e 13 que não
prometem nada — e as 13 estão declaradas como tal, não escondidas.

**O que C2 encontra pronto:** o YouTube já tem adaptador, quatro rotas ligadas e
as seis capacidades declaradas. Substituir actor passa a ser trocar fornecedor
dentro de um adaptador que já existe, com o degrau a ficar escrito.

```
PAREI AQUI. C2 NÃO FOI COMEÇADA.
```
