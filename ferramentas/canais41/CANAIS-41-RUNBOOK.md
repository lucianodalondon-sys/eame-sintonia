# CANAIS-41 — roteiro do teste de qualificação dos 41 canais YouTube pelo Scrap

Ramo `canais-41-runbook-v1` (a partir de `legacy-99-v5` @ ed86cb97, que contém o vivo
`83de0ccd`). **Sem rede.** Quem corre é o coordenador, **depois** da micro social.

## Em palavras simples

- **Hoje o teste não pode correr.** Antes faltam: instalar a v5 (P0), **2 consertos**
  (P1 as marcas nos itens, P2 o workflow aceitar todos os grupos) e **2 conferências**
  (P3 os runners ligados, P4 em que banco o job grava). Sem o P1, os 41 canais seriam
  **todos reprovados por um defeito nosso**, não deles — medido a seco, com o código
  verdadeiro do Scrap.
- **O defeito principal:** o caminho da API do YouTube traz de cada vídeo o endereço, o
  título, a data e o canal, mas **não** escreve duas marcas que a régua exige: «o dono
  autorizou» (`OWNER_AUTHORIZED`) e «o que a plataforma permite»
  (`PLATFORM_POLICY_STATUS`). A régua lê «falta» e reprova. Com as duas marcas (hipótese),
  **41 de 41** canais normais passariam, e um canal com vídeo privado no meio reprovaria
  pela D53, com o nome da prova que falta.
- **A chave da API** não está nesta máquina. Vive **só** no segredo do GitHub
  `YOUTUBE_DATA_API_KEY`, e o GitHub só a entrega ao passo 6 do workflow
  `sintonia-scrap.yml`, e só nas fases oficiais do YouTube. Não se imprime, não se copia,
  não se cria conta nova (D16–D24).
- **Pedidos por canal:** **2**, os dois para `www.googleapis.com` (a lista do canal + a
  página dos vídeos). **0** para `youtube.com` e **0** para `googlevideo.com`. O teto de 5
  por domínio (D38) nem chega a apertar; mesmo assim cada corrida leva um **freio de 2
  pedidos**, e a rodada é de **2 canais** (4 pedidos) → **21 rodadas**.

## 1 · A chave da API do YouTube

| Pergunta | Resposta medida |
|---|---|
| Onde vive? | Segredo do repositório no GitHub, `YOUTUBE_DATA_API_KEY`. Nesta máquina: **ausente** nas variáveis de Utilizador, Máquina e Processo (conferido sem ler o valor, só «tem/não tem» e o comprimento 0). |
| O Scrap precisa dela? | **Sim**, na fase `canal-youtube` (`youtube.channel.discovery` → `playlistItems.list`). Sem ela: `CREDENTIAL_MISSING`, e o código **não** cai para raspagem (`youtube_oficial.SemCredencial`). A fase `audio-youtube` não usa chave. |
| Como se usa sem a imprimir? | Pelo workflow `sintonia-scrap.yml`: o passo 6 recebe-a em `env` **só** se `fase` for uma das quatro fases oficiais (`busca/canal/video/comentarios-youtube`); o passo imprime a fase, o runner e o ramo, nunca a chave. O `guarda/social_guarda.py` confirma que nenhum segredo entrou no repositório. |
| E correr nesta máquina, fora do GitHub? | Só se o **dono** decidir pôr a mesma chave no ambiente de um processo (é a chave existente, não conta nova). **Não recomendado**: o GitHub já a entrega ao runner local sem ela passar por ficheiro nenhum. |
| Quota | 1 unidade por chamada; **2 unidades por canal**, 82 para os 41, de 10 000 por dia. Teto por execução: `YT_TETO_GENERAL_UNITS` (padrão 2000). |

## 2 · Os pré-requisitos (antes da 1.ª rodada)

| # | O quê | Porque bloqueia | Dono | Estado |
|---|---|---|---|---|
| **P0** | `legacy-99-v5` instalada e o B aplicado: `py curadoria/importar_do_coletor.py --pelo-scrap --ids=…` (bot parado) | os contratos dos 41 têm de ser `SCRAP_FASE` · `canal-youtube` | coordenador | pronto para instalar (INTEGRA-NOITE lote 1) |
| **P1** | **As duas marcas nos itens da API.** Proposta: a matriz (`leis/social_matriz.py`) declara, para a rota oficial do YouTube, `OWNER_AUTHORIZED=SIM` (a autorização D17.4 já está escrita em `rota_do_scrap_youtube.AUTORIZACAO`) e `PLATFORM_POLICY_STATUS=ALLOWED`; o adaptador `youtube_uploads` copia-as da matriz para cada item, como `youtube_canal_publico` já faz. Alternativa: a régua social aceitar rota que a plataforma permite sem `OWNER_AUTHORIZED`. | sem elas, **100 %** dos canais com vídeos → `FALHA` «item 0 sem OWNER_AUTHORIZED, PLATFORM_POLICY_STATUS» (123/123 corridas a seco) | **dono** decide o texto; Scrap engineer escreve | **por decidir** |
| **P2** | O workflow só aceita fontes `IT-T8-*` e `IT-T9-*` na fase `canal-youtube` (`assunto_do_alvo_da_fonte`). Acrescentar os outros grupos com a tabela que o canário SOC-ONDA2 já usou (`provas/canario_social_onda2.py::APELIDO`: T2 clima, T5 ciencia, T7 cooperativas, T10 mercado, T11 feiras, T12 politica…) + `--filtro universo=<T>`; e, **na mesma mudança**, `YT_TETO_GENERAL_UNITS: '2'` e `YT_TETO_SEARCH_CALLS: '0'` no passo 6 quando `fase == canal-youtube`. | **35 de 41** canais (T2, T5, T7, T10, T11, T12) saem com `FONTE_SEM_APELIDO`; e sem o teto a corrida não tem freio próprio | coordenador (workflow) | por fazer |
| **P3** | Os runners do projeto nesta máquina (`SINTONIA-EAME-LOCAL` e `-2`, pastas `C:/actions-runner-eame*`) têm o último registo de diagnóstico a **11/09 e 13/09**; o único runner em execução agora é o de outro repositório. | o workflow fica em fila para sempre | coordenador (ligar o serviço) | **NÃO SEI** se estão online — sem rede não se confirma no GitHub |
| **P4** | Saber em que banco o workflow grava o RAW: o job usa `SINTONIA_SALA_BACKEND=POSTGRES` com `SUPABASE_DB_URL` (segredo). **Não sei** se é o mesmo banco do `SALA_DSN.txt` desta máquina. | a régua exige ≥ 1 linha RAW da corrida (visto ≠ guardado); contar no banco errado dá 0 e reprova | coordenador | **NÃO SEI** |

Não bloqueia, mas fica dito (**P5**, Scrap engineer): a matriz declara para `canal-youtube`
a rota `youtube:pagina-publica-do-canal`, mas quem corre a fase usa a API
(`youtube-data-api-v3:playlistItems.list`). O contrato escrito pelo bloco 4 guarda em
`ROTA_DECLARADA_PELO_SCRAP` uma rota que a fase não usa.

## 3 · As rodadas

- **Uma corrida = um canal** (a fase recebe um só `canal_id`) = **2 pedidos** a
  `www.googleapis.com`, **0** a `youtube.com`/`googlevideo.com`.
- **Uma rodada = 2 corridas** seguidas = 4 pedidos (≤ 5, D38, contando `googleapis.com`
  como YouTube, que é a leitura mais apertada). **21 rodadas** (a última com 1 canal).
- Lista e ordem: `ferramentas/canais41/RODADAS-41.tsv` (T8 e T9 primeiro: são os únicos
  que o workflow de hoje aceita).
- **Nunca** na mesma janela da micro social (D35.4): primeiro a micro social inteira,
  depois estas rodadas.

## 4 · Os comandos, rodada a rodada

Ramo instalado no vivo = `servico-20260923-0923` (conferir antes). `NN` = número da rodada.

```bash
# 0 · antes de cada rodada: VPN IT pelo portão de consenso (nunca o ipinfo direto)
py C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/superficie/rede.py --portao-de-egresso IT

# 1 · as duas corridas da rodada (uma de cada vez; esperar a 1.ª acabar)
gh workflow run sintonia-scrap.yml --ref servico-20260923-0923 \
   -f fase=canal-youtube -f fonte=<SOURCE_ID> -f canal_id=<CHANNEL_ID> -f runner=1
gh run watch <RUN_GH>                     # o id vem de: gh run list --workflow sintonia-scrap.yml -L 1
gh run view <RUN_GH> --log | grep -E "RUN_ID|SCRAP_COLHEITA|colheita|BUDGET_EXHAUSTED|CREDENTIAL|FONTE_SEM_APELIDO"
#    anotar SOURCE_ID<TAB>RUN_ID (o RUN_ID do orquestrador, não o do GitHub) em rodada-NN.tsv
#    ⚠️ a linha exacta onde o log mostra o RUN_ID não foi vista a seco: conferir no 1.º log

# 2 · PARAGEM (qualquer uma pára a rodada e as seguintes)
#    - o log diz CREDENTIAL_MISSING, FONTE_SEM_APELIDO, BUDGET_EXHAUSTED ou QuotaEstourada
#    - o portão de egresso não diz IT
#    - a colheita tem > 25 itens (o limite da fase), ou o envelope não é da fonte pedida

# 3 · julgar (sem escrever): o envelope fica na pasta de trabalho do runner
ENV=C:/actions-runner-eame/_work/eame-sintonia/eame-sintonia/data/colheita/scrap   # runner=1; conferir
py ferramentas/canais41/montar_corridas.py --rodada=rodada-NN.tsv --envelopes=$ENV \
   --dsn-ficheiro=<DSN do banco onde o job gravou (P4)> --saida=corridas-NN.json
py curadoria/regua_social.py --corridas corridas-NN.json --envelopes $ENV --json regua-NN.json
py ferramentas/canais41/para_aplicar.py --regua=regua-NN.json --corridas=corridas-NN.json \
   --saida=aplicar-NN.json              # e aplicar-NN.fora.json com o que NÃO se escreve

# 4 · escrever no livro SÓ o que é da fonte (bot parado: curadoria/PARAR.flag)
py curadoria/regua_social.py --corridas aplicar-NN.json --envelopes $ENV --aplicar --vivo
#    tirar o PARAR.flag; esperar >= 60 s; rodada seguinte
```

`montar_corridas.py` lê o RAW **só para consultar** (`default_transaction_read_only=on`) e
nunca imprime o DSN. `regua_social.py --aplicar` recusa o vivo sem `--vivo` e sem o
`PARAR.flag`.

**A prova de teto por rodada:** a `provas/prova_teto_dominio.py` lê o livro de corridas
do **coletor de sites** (`runs.ndjson`), que o Scrap **não** escreve, e o recibo do Scrap
não traz a contagem de pedidos. Por isso o freio é o do próprio código:
`YT_TETO_GENERAL_UNITS=2` faz a corrida **parar** ao 3.º pedido (medido a seco: teto 1 →
1 pedido e `BUDGET_EXHAUSTED`; teto 2 → 2 pedidos e colheita normal). A prova
independente é o número de itens do envelope e o `RESULT` do recibo. ⚠️ Uma contagem
independente dos pedidos do Scrap **não existe hoje**; o Scrap engineer pode pôr
`Sessao.requests` no `RUN_RECEIPT`.

## 5 · O que conta como PASS por canal

Veredito `READY` de `curadoria/regua_social.py` para a fase do **contrato**
(`canal-youtube`), que exige **tudo** isto:

1. o envelope é da fonte pedida, `RESULT=OK`, ≥ 1 item de colheita;
2. em **cada** item: identidade da plataforma (`NATIVE_ID`), `PUBLISHED_AT`,
   `OWNER_AUTHORIZED=SIM` e `PLATFORM_POLICY_STATUS` escrito;
3. **D53**, em **cada** item: a página pública do vídeo (o endereço nomeia o `NATIVE_ID`),
   o título (não «Private video»/«Deleted video»), a data de publicação (nem `NAO SEI`
   nem `UNKNOWN`) e o canal do **contrato**; a transcrição não é exigida;
4. ≥ 1 linha RAW dessa corrida no banco (visto ≠ guardado).

Só então o livro passa a fonte a `READY_FOR_COLLECTION`, com a régua `SOCIAL/v1`.

## 6 · O que fazer com quem não passa

| O que a régua / o filtro diz | Classe | O que fazer |
|---|---|---|
| `ZERO` (a rota abriu e o canal não tem vídeo público) | REMEDIR_DEPOIS | fica `CANARY_PENDING`; voltar a medir numa próxima onda |
| D53 `TITULO` (vídeo privado/apagado na lista) | da fonte | `CONTRACTED_CANARY_FAILED` com o porquê; re-medir depois (a lista muda); se repetir, leitura humana |
| D53 `CANAL` ou `IDENTIDADE A CONFERIR POR HUMANO` | da fonte | parar esta fonte; decisão humana (D21: nome parecido não prova identidade) |
| D53 `PAGINA_DO_VIDEO` / `DATA_DE_PUBLICACAO` | da fonte | como a linha anterior; abrir o envelope e ler o item |
| sem `OWNER_AUTHORIZED` / `PLATFORM_POLICY_STATUS` | **defeito nosso** (P1) | **não** escrever; consertar P1 e voltar a correr |
| `CREDENTIAL_MISSING`, `BUDGET_EXHAUSTED`, quota | defeito nosso | não escrever; ver a chave / o teto; voltar a correr |
| 0 linhas RAW no banco | defeito nosso (P4 ou ingresso) | não escrever; ver onde o job gravou |
| envelope de outra fonte/fase; Atlas não conhece | defeito nosso | não escrever; registo/pedido errado |
| `FONTE_SEM_APELIDO` (não chega a haver envelope) | defeito nosso (P2) | não correr os T≠8/9 antes do P2 |

O `para_aplicar.py` faz esta separação e escreve o que ficou de fora em
`aplicar-NN.fora.json`, com a classe e o porquê.

## 7 · O ensaio a seco (sem rede)

`ferramentas/canais41/ensaio_a_seco.py`: corre o código verdadeiro do Scrap
(`scrap_colheita.colher` → `COLLECT` → `adaptador_youtube.youtube_uploads` →
`youtube_oficial.uploads_recentes`), com duas trocas: chave falsa só no processo e o
transporte da API trocado por respostas literais que contam cada pedido. Proxy fechado
para tudo o resto. Três cenários por canal: NORMAL (3 vídeos), PRIVADO (1 «Private video»
no meio), VAZIO.

**Sobre `integra-noite-v1` @ 2a2fa154 + `legacy-99-v5` @ ed86cb97** (junção feita numa
cópia temporária, desfeita no fim; livros do vivo `83de0ccd`, sha256 em
`ENSAIO-INTEGRA-NOITE-copia-livros.sha256`):

| | NORMAL | PRIVADO | VAZIO | pedidos por corrida |
|---|---|---|---|---|
| **hoje** (`ENSAIO-INTEGRA-NOITE-HOJE.json`) | 41 FALHA «sem OWNER_AUTHORIZED, PLATFORM_POLICY_STATUS» | 41 FALHA (idem) | 41 ZERO | 2 × `www.googleapis.com` (123/123) |
| **hipótese P1 feito** (`…-SIMULADO.json`) | **41 READY** | 41 FALHA «D53: o item 1 não prova TITULO» | 41 ZERO | 2 × `www.googleapis.com` |

- Os 41 passam para a rota do Scrap pelo `--pelo-scrap` na mesma cópia (41/41), e o Atlas
  conhece os 41.
- O caminho inteiro do roteiro (`montar_corridas` → `regua_social` → `para_aplicar`)
  correu sobre os 123 envelopes. Hoje: **APLICAR 0 / FORA 123**. Na hipótese: APLICAR 41
  (as falhas D53 da fonte); os READY ficam de fora por **RAW não contado** (sem banco no
  ensaio) — como deve.
- **Conflito ao juntar a v5 ao `integra-noite-v1`:** um só, em `curadoria/worker.py`
  (`etapa_canary`): fica o despacho `FORMA_PAGINA_E_BOLETIM` do integra-noite e sai o do
  canal antigo (`canario_youtube_canal`, que a v5 retira). Resolução em
  `RESOLUCAO-WORKER-INTEGRA-NOITE-mais-v5.diff`; com ela, os 72 testes da v5 passam na
  junção. O resto dos conflitos são ficheiros gerados do mapa (refazem-se pela cadeia).

## 9 · Os 22 canais candidatos da BLOQUEADAS — qualificar ANTES, separados dos 41

Entrada: `auditoria-madrugada/CANAIS-YOUTUBE-22-PARA-CANAIS-41.json` (BLOQUEADAS-DESTRAVAR).
São **candidatas** (sem SOURCE_ID), não estão nos 41. As 22 tarefas QUALIFY estão
`BLOCKED` desde **22/09** com a frase da **regra antiga** («YouTube exige channel_id e
molde de video»), que o `worker.py` de hoje já não usa — ficaram presas porque ninguém
as reabriu.

**Ensaio a seco** (`curadoria/ensaiar_qualify_youtube.py` **sem** `--reabrir`: corre a
etapa QUALIFY real com fila, livro, alocação e evidência numa pasta temporária; cópia
com os livros do vivo; rede fechada) — `QUALIFY-22-ENSAIO.txt`:

| Resultado | N | Candidatas | O que fazer |
|---|---|---|---|
| **OK, número novo** | 7 | 0289, 0423, 0469, 0335, 0377, 0873, 0877 | reabrir → o robô dá o número (herança D21 do site), escreve o contrato da rota do Scrap e pára em `CANARY_PENDING`; depois entram nas rodadas como os 41 (**+4 rodadas**) |
| **OK, já tem número** | 2 | 0733 → **IT-T2-026** (é uma dos 41); 0332 → o mesmo canal da 0335 | nada de novo: um canal, um SOURCE_ID |
| **BLOCK, sem channel_id** — resolvível | 7 | `@`: 0488, 0792, 0815 · `/user/`: 0561, 0653, 0769, 0876 | o workflow `curator-youtube-handles.yml` (SOC4) pergunta à API `channels.list forHandle/forUsername` (1 unidade cada, teto 60, chave só no passo 2) e grava `curadoria/RESOLUCAO-HANDLES-YOUTUBE-V1.json`; depois reabrir outra vez |
| **BLOCK, playlist** | 3 | 0452, 0331, 0414 | **fica NAO SEI**: uma playlist não é um canal, e o resolvedor recusa-se a adivinhar o dono (seria identidade fabricada); só uma pessoa pode dizer de que canal é |
| **BLOCK, SEMANTIC** | 3 | 0271 (ISMEA) e 1199: sem ligação oficial canal↔site escrita na ficha · 0300: território indeterminado pelo nome | decisão humana (D21). ⚠️ A BLOQUEADAS diz que a 0300 tem D21 medido (T12), mas a ficha não o traz na forma que o QUALIFY lê — escrever a prova na ficha, não o número |

⚠️ Os números novos (IT-T12-152, IT-T5-191, IT-T7-253, IT-T7-254, IT-T2-165, IT-T2-166,
IT-T12-153) são os que a **cópia** daria: os reais saem na hora, do registo de alocação
vivo, e podem ser outros.

**Comandos** (o coordenador; serviço parado durante o `--reabrir`):

```bash
# 1 · ensaio de novo no dia (só pasta temporária) e conferir o quadro acima
py curadoria/ensaiar_qualify_youtube.py
# 2 · reabrir, na fila real, SÓ as QUALIFY barradas pela frase antiga
py curadoria/ensaiar_qualify_youtube.py --reabrir
#    (reabre TODAS as QUALIFY com essa frase; no vivo 83de0ccd são exactamente estas 22 — conferir a lista que imprime)
# 3 · tirar o PARAR.flag; o serviço qualifica na volta seguinte
# 4 · os 7 @/user/: disparar a resolução (API oficial, chave no segredo)
gh workflow run curator-youtube-handles.yml --ref <ramo com o PEDIDO>   # ou push de curadoria/PEDIDO-RESOLVER-HANDLES.json
#    o registo volta commitado nesse ramo: levá-lo ao vivo (quem instala é o coordenador)
#    e repetir os passos 1–3
```

**Ordem:** as 22 **não** entram nas rodadas dos 41. Primeiro qualificar (sem rede nos
passos 1–3; o passo 4 gasta ~7–11 unidades da API, não `youtube.com`), depois as que
ganharem número e contrato entram em rodadas **próprias**, a seguir às 21 dos 41, com a
mesma regra (2 canais por rodada, freio de 2 pedidos por corrida).

## 8 · O que isto não prova

- Que a API responde assim de verdade: as respostas são literais, com a forma documentada
  e a que os testes do Scrap usam. Nenhum pedido real foi feito.
- Quantos dos 41 têm vídeos públicos hoje, ou vídeos privados na lista.
- Que os runners estão online (P3) e em que banco o job grava (P4).
- O texto de P1 é uma proposta: a decisão é do dono.
