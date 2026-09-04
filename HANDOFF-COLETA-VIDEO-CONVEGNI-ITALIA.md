# HANDOFF · COLETA / VÍDEO / CONVEGNI / CRUZAMENTOS ITÁLIA

**Data:** 2026-09-04
**Branch:** `claude/retomada-coleta-video-convegni-vz50er`
**Base recebida:** `34e4ce8` (era a ponta de `claude/adama-italia-source-discovery-oui6ma`)

O próximo agente deve conseguir continuar **sem reconstruir esta história pela conversa**.
Tudo o que importa está em arquivo versionado, e este documento diz onde.

---

## 0 · A COISA MAIS IMPORTANTE DESTE HANDOFF

**O contêiner da conta anterior morreu, e com ele morreram resultados que já tinham fechado.**

O handoff que recebi dizia "11 workflows vivos, não duplicar" e "22 objetos fechados, não
recolher". As duas frases foram escritas **acreditando que os resultados estavam salvos**.
Não estavam.

```
processos vivos da conta anterior neste contêiner ........... ZERO
scratchpad da conta anterior (b6cc5475-...) ................. NÃO EXISTE
falas de convegno commitadas ................................ 17
falas de convegno que a conta anterior tinha fechado ........ 22
```

Os 11 workflows não podiam ser duplicados nem preservados: eles **não existem mais**. Eles
escreviam em memória de agente e em `/tmp/claude-0/.../b6cc5475-b0e9-5242-bac3-292cc842a48f/`,
que é efêmero e foi reclamado junto com o contêiner. Só o que virou commit sobreviveu.

**A lição operacional, e ela vale para a próxima troca de conta:**
resultado que não virou commit não é resultado fechado — é resultado em risco. O `PROCESSED`
de `IT-CHECKPOINT-V1.json` estava vazio (`{}`) e por isso o livro-caixa não sabia dizer o que
tinha sido consumido.

---

## 1 · TABELA DE ESTADO REAL

| WORKFLOW / AGENTE | OBJETO | STATUS | ÚLTIMA ATIVIDADE | RESULTADO PERSISTIDO? | RETOMAR? |
|---|---|---|---|---|---|
| colhedor paciente (sem agente) | 17 falas de convegno | **CLOSED** | 2026-09-03 23:53 | SIM · `IT-CONVEGNO-V1/falas/` | NÃO |
| colhedor paciente | `wh20ZkHf5Cc` | **CLOSED** (bytes perdidos → **resgatado**) | 2026-09-04 01:18 | SIM, agora · `IT-CONVEGNO-V2/falas/` | NÃO |
| colhedor paciente | `AOOVhtTQvPA` | **CLOSED** (bytes perdidos → **resgatado**) | 2026-09-04 01:18 | SIM, agora | NÃO |
| colhedor paciente | `-4lUyIORl4A` (olivo I sessione) | **CLOSED** (bytes perdidos → **resgatado**) | 2026-09-04 01:20 | SIM, agora | NÃO |
| colhedor paciente | `c2bJ4IqqXek` (drupacee) | **BLOCKED** | 2026-09-04 01:28 | SIM (o *bloqueio* está registrado) | NÃO |
| colhedor paciente | 2 objetos não identificados | **UNKNOWN** | — | NÃO | ver §5 |
| `cruzamento-shard` × `pomacee-drupacee` | 4 cruzamentos | **CLOSED** | 2026-09-04 00:49 | SIM · `IT-CRUZAMENTOS-V2.json` | NÃO |
| `cruzamento-shard` × `vite` | — | **LOST** | perdido com o contêiner | NÃO | SIM (§6) |
| `cruzamento-shard` × `seminativi` | — | **LOST** | perdido com o contêiner | NÃO | SIM (§6) |
| `cruzamento-shard` × `olivo-agrumi` | — | **LOST** | perdido com o contêiner | NÃO | SIM (§6) |
| `convegno-shard` lotes A–F | 12 leituras em curso | **LOST** | perdido com o contêiner | NÃO | SIM (§6) |
| intel V1 (sinais) | 44 sinais testados | **CLOSED** | 2026-09-03 | SIM · `IT-CAMPO-SINAIS-VERIFICADOS-V1/V2` | NÃO |

**Nenhum processo foi morto por ficar minutos sem output.** Não havia nenhum processo para matar.

---

## 2 · O RESGATE (o que fiz e por quê)

Três objetos tinham **fechado** na conta anterior e **nunca foram commitados**. Recolhi
exatamente esses três, pela **mesma rota** (`youtube.com/api/timedtext`, json3, sem
credencial, sem cookie, 0 USD).

**Isto não é recoletar os 22.** Os 17 objetos de `IT-CONVEGNO-V1` não foram tocados: mesmo
sha, mesma data de captura, mesma proveniência.

**A prova de que são os mesmos objetos é `CHARS_DELTA = 0` nos três:**

| ID | caracteres medidos agora | medidos pela conta anterior | delta |
|---|---|---|---|
| `wh20ZkHf5Cc` | 59.137 | 59.137 | **0** |
| `AOOVhtTQvPA` | 4.767 | 4.767 | **0** |
| `-4lUyIORl4A` | 171.715 | 171.715 | **0** |

Se fosse outra faixa de legenda, outro idioma ou outra passagem do ASR, o número não bateria.

Testemunhas HTTP linha a linha: `data/samples/IT-CONVEGNO-V2/testemunhas/*.witness.json`.

---

## 3 · FIX-06 REMEDIDO, E O LIMITE **NÃO** FOI ALARGADO

`-4lUyIORl4A` levou bot-check nas tentativas 1 e 2 e devolveu **HTTP 200 com 3.155.193 B na
tentativa 3**, depois de espera, sem credencial. `c2bJ4IqqXek` levou bot-check em 4 tentativas
de metadado e abriu na 5ª.

**A metade "fila" do FIX-06 foi confirmada por outra conta, em outro contêiner, com outra
instalação do yt-dlp.** A metade "muro" **não foi testada de novo, de propósito**.

```
youtube.com/api/timedtext  LEGENDA  ->  bot-check que CEDE à espera     = FILA
googlevideo.com            BINÁRIO  ->  HTTP 403 da política de saída   = MURO
```

**Nenhuma segunda regra foi criada.** O FIX-06 já carrega o próprio limite escrito dentro
dele, em `data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json` →
`CORRECTIONS_TO_MY_OWN_MEASUREMENTS` → `FIX-06` → `E_O_LIMITE_DESTA_PROPRIA_CORRECAO`.
Duplicar a conclusão em dois lugares faria as duas divergirem com o tempo.

---

## 4 · `c2bJ4IqqXek` — BLOQUEIO LEGÍTIMO, CONFIRMADO SEM GASTAR TENTATIVA

**Estado:** `NO_ITALIAN_CAPTION` + `AUDIO_BINARY_EGRESS_BLOCKED`

Remedição desta conta — **só metadado, zero bytes de mídia pedidos**:

- `CAPTION_LANGS_OFFERED` voltou **vazia**. Não é apenas "sem legenda italiana": este objeto
  **não oferece legenda em idioma nenhum**. O diagnóstico anterior fica confirmado e mais preciso.
- `AUDIO_ONLY_FORMATS` = **48, 106, 129 kbps** — exatamente os três da medição anterior.
- `DURATION_S` = 15.388 (4h16) — confere.
- `AUDIO_BINARY_ATTEMPTED` = **false**.

**A rota alternativa permitida foi testada UMA vez, e era ler a política, não repetir o
caminho bloqueado:** `$HTTPS_PROXY/__agentproxy/status` devolve `selective=false`,
`toolScoped=false`, `recentRelayFailures=[]`. Não há allowlist por host para acionar. A rota
de áudio local desta casa (`scripts/it_audio.py`, `IT-VOZ-AUDIO`) busca MP3 de host de
podcast e não serve para vídeo do YouTube. **Não existe nesta casa rota que obtenha o áudio
sem passar por googlevideo.com.**

Não desliguei verificação TLS e não removi `HTTPS_PROXY`.

Se o áudio um dia abrir, o caminho é `download → whisper local → SINTONIA_WHISPER_LOCAL`,
e **não** `YOUTUBE_ASR_AUTO`, que para este objeto não existe.

---

## 5 · O BURACO QUE **NÃO** FECHEI

O FIX-06 declara **22 objetos e 3.075.569 caracteres**. A conta fecha assim:

```
convegno em git ............ 17 obj   2.811.477 ch
resgatados nesta conta .....  3 obj     235.619 ch
                             -----------------------
subtotal ................... 20 obj   3.047.096 ch
declarado no FIX-06 ........ 22 obj   3.075.569 ch
FALTA ......................  2 obj      28.473 ch
```

**Os ids desses 2 objetos não estão escritos em nenhum arquivo versionado.** Procurei em
`IT-VIDEO-V1` um objeto de 28.473 caracteres e um par que somasse 28.473: **nenhum dos dois
existe**. Inventar dois ids para fechar a aritmética seria pior que declarar o buraco.

**Estado: `UNKNOWN_2_OBJECTS`.**

---

## 6 · O QUE AINDA ESTÁ PENDENTE

### Três grupos de cruzamento

| GROUP_ID | STATUS | INPUTS | OUTPUT PERSISTIDO? | PRÓXIMA AÇÃO |
|---|---|---|---|---|
| `pomacee-drupacee` | **CLOSED** | — | SIM | nada |
| `vite` | **LOST** (output) | íntegros em git | NÃO | refazer |
| `seminativi` | **LOST** (output) | íntegros em git | NÃO | refazer |
| `olivo-agrumi` | **LOST** (output) | íntegros em git | NÃO | refazer |

### Doze leituras de convegno (lotes A–F do `convegno-shard`)

Estavam no ar quando os créditos acabaram. **Output perdido; inputs íntegros.**

**Os INPUTS estão todos em git** — as 38 falas e os arquivos de sinais. **Os OUTPUTS não.**
Refazer é possível e custa fan-out novo, que a missão restringe. **Não refiz por decisão, e
não por esquecimento:** a missão manda não reabrir fan-out amplo, e o handoff é mais valioso
que uma rodada parcial que a próxima troca de conta perderia de novo.

**Aviso ao próximo agente:** antes de disparar qualquer workflow, corrija o caminho dentro de
`.claude/workflows/*.js` — a constante `SC` ainda aponta para o scratchpad morto
`b6cc5475-b0e9-5242-bac3-292cc842a48f`, e os pacotes `v21/*.json` que ela referencia **não
existem mais**. Rodar sem corrigir isso produz agente cego.

---

## 7 · ARQUIVOS QUE **NÃO** PODEM SER REGENERADOS

Se algum destes se perder, ele volta só recoletando — e alguns nem isso:

```
data/samples/IT-CONVEGNO-V1/falas/*.json          17 falas · 2.811.477 ch
data/samples/IT-CONVEGNO-V2/falas/*.json           3 falas ·   235.619 ch  (o resgate)
data/samples/IT-VIDEO-V1/falas/*.json             18 falas ·   367.558 ch
data/samples/IT-CAMPO-V1/IT-CAMPO-SINAIS-VERIFICADOS-V1.json    21 sinais sobreviventes
data/samples/IT-CAMPO-V1/IT-CAMPO-SINAIS-VERIFICADOS-V2.json    19 sinais sobreviventes
data/samples/IT-CRUZAMENTO-V1/IT-CRUZAMENTOS-V1.json             7 cruzamentos
data/samples/IT-CRUZAMENTO-V2/IT-CRUZAMENTOS-V2.json     grupo pomacee-drupacee INTEIRO
data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json   FIX-01..06 e os bloqueios medidos
data/samples/IT-VOZ-AUDIO-V1/ e V2/                      transcrições whisper local
data/samples/IT-INSTAGRAM-V1/ V2/ V3/                    transcrições whisper local
```

`IT-CRUZAMENTOS-V2.json` é o mais insubstituível: os **11 descartes com motivo** e os **2
refutados** valem tanto quanto os 2 sobreviventes, e nenhum deles se reconstrói por inferência.

---

## 8 · COMANDOS EXATOS DE RETOMADA

```bash
cd /home/user/eame-sintonia
git fetch origin claude/retomada-coleta-video-convegni-vz50er
git checkout claude/retomada-coleta-video-convegni-vz50er

# dependências (o contêiner vem limpo)
pip3 install yt-dlp pytest

# a suíte que tem de continuar verde
python3 -m pytest tests/ -q          # esperado: 329 passed, 4676 subtests

# conferir que os três resgatados continuam com delta 0
python3 -c "import json,glob
for p in sorted(glob.glob('data/samples/IT-CONVEGNO-V2/falas/*.json')):
    d=json.load(open(p)); print(d['EXTERNAL_ID'], d['TRANSCRIPT_LENGTH'], 'delta', d['CHARS_DELTA'])"

# a rota de coleta que funciona (paciente, sem credencial, 0 USD)
#   scripts/it_video.py :: _fala_youtube()   — legenda, É FILA
#   scripts/it_video.py :: _fala_local()     — áudio+whisper, SÓ com IT_VIDEO_AUDIO=1
#                                              e bloqueado por egresso neste ambiente
```

**NÃO rodar** nada que peça binário de `googlevideo.com` neste ambiente: são 403 garantidos.

---

## 9 · GAPS RESTANTES

1. **2 objetos / 28.473 caracteres** não identificados (§5). `UNKNOWN`.
2. **3 grupos de cruzamento** sem output (§6).
3. **12 leituras de convegno** sem output (§6).
4. **`-4lUyIORl4A` foi coletada e nunca foi lida** por nenhum agente — é a I sessione do
   bilancio do olivo, 171.715 caracteres, e o OLIVO é a maior assimetria declarada do radar
   (1 par de rótulo lido contra 3 oportunidades).
5. **`c2bJ4IqqXek`** bloqueado por egresso (§4).
6. **136 dos 150 bollettini de 2026** ainda sem texto extraído. Toda afirmação sobre "quando
   a instituição falou pela primeira vez" carrega esse limite.
7. **61 dos 163 registros ADAMA** sem rótulo lido. Toda afirmação de ausência sobre eles é
   frágil — foi assim que o único sinal já refutado desta casa caiu.

---

## 10 · PRÓXIMA AÇÃO EXATA

**Ler `-4lUyIORl4A`** (I sessione do bilancio do olivo, 171.715 caracteres, já em disco, custo
zero de coleta). É a única massa de fala nova que entrou e ainda não foi lida, e ela cai
exatamente em cima da maior assimetria declarada do radar. Ler antes de abrir qualquer
fan-out novo.

Depois, e só depois, decidir com o dono da missão se vale refazer os 3 grupos de cruzamento e
as 12 leituras — corrigindo antes o caminho `SC` dentro de `.claude/workflows/*.js`.

---

## 11 · FRONTEIRAS RESPEITADAS

Portal, design, Vercel, produção e o snapshot congelado da reunião: **intocados**. Nenhum
resultado desta missão foi inserido no portal de amanhã. O meeting build usa cutoff próprio e
estes resultados entram depois via backfill.

`STATUS_CHANGES = 0`. `SCORE_CHANGES = 0`. Nenhum segundo Opportunity Engine foi criado.
Esta missão coleta e estrutura evidência; ela não decide prioridade comercial.
