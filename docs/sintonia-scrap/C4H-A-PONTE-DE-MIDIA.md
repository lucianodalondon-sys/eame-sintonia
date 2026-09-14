# C4H · A PONTE DE MÍDIA — o executor nasceu, e a estrada continua por correr

> **A causa que a C4G nomeou está fechada.** A porta da derivação conhecia UM
> executor, importado pelo nome; agora conhece um registo, e há uma ponte
> canónica que leva áudio e vídeo ao reconhecedor que já existia.
>
> **E a estrada não foi corrida.** Sem PostgreSQL não há observação, e sem
> observação não há o que derivar. O que mudou é o TAMANHO do que falta.

```
MEDIA_COLLECTION_PIPELINE   = PARTIAL
FULL_MEDIA_TO_WAITING_ROOM  = NOT_PROVEN   (nenhuma corrida contra banco real)
YOUTUBE_TOUCHED             = NO
```

---

# A · GIT

| campo | valor |
|---|---|
| REPO | `lucianodalondon-sys/eame-sintonia` |
| BRANCH | `claude/local-gpu-on-current-collection-v1` |
| INITIAL_HEAD | `867a6f975a9635470e097aa919487624b6071468` |
| REMOTE_HEAD (no arranque) | igual · worktree limpa |
| WORKTREE | `C:/eame-gpu-current` |

`origin/main` está em `f437ff11` — 173 commits atrás desta linha, e não é a
linha funcional da Collection. Não foi tocada.

---

# B · ISOLAMENTO DA ABA YOUTUBE

A pista do prompt apontava quatro branches de Setembro. **Nenhuma delas é a
activa.** Medido:

```
YOUTUBE_ACTIVE_WORKTREE
  C:/eame-sintonia/.claude/worktrees/youtube-italia-caption-audio-8b460b

YOUTUBE_ACTIVE_BRANCH
  claude/youtube-italia-caption-audio-8b460b @ b57f3df6
  saiu de 611e7cbf — um commit à frente, ainda não fundida
```

Os nove ficheiros que ela tocou:

```
provas/a_legenda_e_o_audio_do_youtube.py              (novo, dela)
docs/sintonia-scrap/C4G-A-LEGENDA-E-O-AUDIO-NAO-ABREM.md   (novo, dela)
system-map/data/youtube-legenda-audio.generated.json  (novo, dela)
docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md     ← gerado pela cadeia
system-map/data/*.generated.json (4)                  ← gerados pela cadeia
italia-portale/client/system-map/state.generated.json ← gerado pela cadeia
```

```
OVERLAPPING_FILES        = 0 de código-fonte
                           6 artefactos GERADOS pela cadeia do System Map
YOUTUBE_FILES_CHANGED_BY_THIS_MISSION = 0
YOUTUBE_TOUCHED          = NO
```

Nenhum merge, nenhum cherry-pick, nenhum rebase, nenhuma resolução de conflito
dela. `ferramentas/fala_local.py` — a infraestrutura partilhada — **não foi
alterada**, e há prova que o guarda: o dono do ASR não pode passar a conhecer a
ponte, porque a dependência tem de ser numa direcção só.

> **⚠️ E há uma colisão de nome, que não é minha e fica reportada.** A aba do
> YouTube chamou ao documento dela `C4G-A-LEGENDA-E-O-AUDIO-NAO-ABREM.md`, e o
> meu da missão anterior chama-se `C4G-O-CANO-INTERNO-DO-VIDEO.md`. **Dois C4G
> diferentes**, como o §118 do know-how. Esta missão chama-se C4H e não
> acrescenta colisão; desfazer a existente é decisão de integração, não minha.

E outra sessão trabalha na Sala: `C:/sala-truth-01`, branch `claude/sala-truth-01`
@ 611e7cbf, com `provas/a_fronteira_da_coleta.py` por commitar. **Não tocado.**

---

# C · BASELINE — como o caminho estava

| aresta | MODULE_EXISTS | EDGE_EXISTS | FLOW_OBSERVED |
|---|---|---|---|
| VIDEO → RAW | SIM | SIM | **não** (sem banco) |
| RAW → DERIVED | SIM | **não** — a porta só conhecia PDF | não |
| DERIVED → STRUCTURED | SIM | declarado | não |
| STRUCTURED → ADMISSION | SIM | declarado | não |
| ADMISSION → READY | SIM | declarado | não |
| READY → SALA | SIM | SIM (migração 031) | não (sem banco) |

```
DERIVATION_CAPABILITIES   = 1   (application/pdf)
MEDIA_EXECUTOR_EXISTS     = NO
MEDIA_OUTPUT_CONSUMER     = NO
POSTGRES_DISPOSABLE       = ubuntu-latest + postgres:16, no CI · NÃO nesta máquina
```

---

# D · O QUE MUDOU

| ficheiro | responsabilidade | porquê |
|---|---|---|
| `coleta/executor_transcricao_midia.py` | **novo** · a ponte | não havia quem levasse mídia ao reconhecedor |
| `coleta/ingresso.py` | registo de executores + `executor_para()` | a lista de um tinha forma de registo |
| `coleta/derivacao_forward.py` | escolhe o executor por espécie | `derivar or ex.derivar_um` mandava tudo ao PDF |
| `tests/test_c4h_executor_de_midia.py` | **novo** · 28 provas | T1–T16 do pedido |
| `tests/test_c4g_a_especie_do_video.py` | sentinelas actualizadas | dispararam, como projectadas |

---

# E · O EXECUTOR DE MÍDIA

```
NOME                  coleta/executor_transcricao_midia.py
EXECUTOR_ID           transcricao-midia
MEDIA TYPES           video/mp4 · quicktime · webm · matroska
                      audio/wav · x-wav · mpeg · mp4 · aac · ogg · opus · flac · webm
PRODUTO               derived_artifact kind=TRANSCRIPTION  (lista fechada da 022)
OWNER DO ASR          ferramentas/fala_local.py     — intocado
OWNER DA PERSISTÊNCIA guarda/preservar_derivado.py  — intocado
```

### Três decisões, e nenhuma foi minha

**1 · O áudio intermédio é material de trabalho.** A migração 022 declara a
lista fechada de espécies e não há áudio nela; e o grão dela diz, por extenso,
`audio -> transcricao  1 linha`. O WAV nasce numa pasta temporária e morre com a
derivação — como o buffer que o `pdftotext` também tem e nunca preservou.

**2 · O que muda o TEXTO entra na identidade.** `parameters` leva modelo,
dispositivo e tipo de cálculo, porque a 022 já escrevera a razão: *«o modelo
`base` e o `small` sobre o mesmo audio dao textos diferentes... Sem a versao na
identidade, a segunda passagem apagaria a primeira em silencio.»* E a C4E mediu
que placa e processador também dão textos diferentes — logo o ferro entra.

**3 · Um erro meu, apanhado antes de escrever.** Ia passar `text_kind`,
`text_relation` e `language` ao dono da escrita. Medido a tempo: a 022 tem
catorze colunas e nenhuma se chama assim, e `preservar_derivado` é explícito —
*«`raw_asset_id`, `kind`, `producer`, `producer_version`, `parameters`,
`serie_posicao`, `media_type`, e os bytes do filho. **Nada mais.**»* E o
contrato E7 já respondera: a representação canónica do texto é `TEXT_UNITS`, e
vive na UNIDADE, não na linha do ficheiro.

```
ANTES DE INVENTAR VOCABULÁRIO, PROCURAR O DONO NO GIT INTEIRO.
UMA COLUNA QUE NÃO EXISTE NÃO SE CRIA A PARTIR DE UM EXECUTOR.
```

A espécie do texto sobe no **resultado** — `TEXT_KIND = TRANSCRIPT`,
`TEXT_RELATION = ORIGINAL`, língua com fonte e confiança — para quem monta a
unidade usar.

---

# F · PROVA CONTRA POSTGRES

```
NÃO EXECUTADA.
```

E é preciso ser exacto sobre o que falta, porque são duas coisas e não uma:

| o que | estado |
|---|---|
| PostgreSQL descartável | **existe** — `banco-descartavel.yml`, `ubuntu-latest`, `postgres:16`, com `workflow_dispatch`. E o `gh` desta máquina está autenticado |
| mídia no CI | **não existe** — o MP4 são 9,2 MB não versionados, e versioná-los violaria P-011 |
| reconhecedor no CI | **não existe** — `ubuntu-latest` não tem GPU e o modelo são ~1,5 GB por corrida |

```
A INFRAESTRUTURA DE BANCO ESTÁ AO ALCANCE. O RECONHECEDOR É QUE NÃO VIAJA
PARA LÁ — E FORJAR UM STUB DE ASR PARA PINTAR O PORTÃO DE VERDE SERIA
PROVAR O ENCANAMENTO COM ÁGUA IMAGINÁRIA.
```

Por isso `RUN_CREATED`, `RAW_OBSERVATION_CREATED`, `DERIVED_CREATED`,
`STRUCTURED_CREATED`, `ADMISSION_EXECUTED`, `READY_CREATED` e `WAITING_ROOM_ENTRY`
ficam todos **NOT_EXERCISED** — e não `FAIL`.

### O que FOI exercido, com áudio real produzido aqui

Um tom de 2 s gerado por `ffmpeg` (sem rede, sem acervo), pelo caminho completo
do executor:

```
em.derivar_um(1, tom.wav, armazem=None, memoria=None, media_type="audio/wav")
  ESTADO              SEM_DERIVADO
  MOTIVO_DO_EXECUTOR  SEM_TEXTO_RECONHECIDO
  destino             REJECTED     (e não ERROR — a ferramenta correu)
  NAO_SIGNIFICA       «que o áudio não tem fala. Significa que não saiu texto.»
```

O reconhecedor correu de verdade. O que não existe é o banco do outro lado.

---

# G · RETRY

`NOT_EXERCISED` no que importa. Sem `memoria`, `preservar_derivado` não escreve
nada, e `REUSED` é decisão dele — o executor não tem opinião sobre reuso, e há
prova que o guarda.

O que a C4G já mediu e continua válido: dois RUNs diferentes sobre os mesmos
bytes dão o mesmo `ARTIFACT_ID` e **não** duplicam o original.

---

# H · RED TEAM

| # | ataque | resultado |
|---|---|---|
| RT1 | MP4 ainda chega ao PDF | **morto** · `executor_para("video/mp4")` → mídia |
| RT2 | escolhe por extensão | **morto** · T5: ficheiro `.pdf` com espécie de vídeo vai à mídia |
| RT3 | novo executor duplica `fala_local` | **morto** · sem `WhisperModel`, sem `device=`, sem `compute_type=` |
| RT5 | SHA vira identidade da observação | **morto** · o executor não calcula sha nenhum |
| RT7 | `SOURCE_ID` nasce de path/handle | **morto** · a string `SOURCE_ID` não existe no executor |
| RT8 | caption vira transcript | **morto** · `CAPTION` não aparece no código dele |
| RT9 | idioma nasce do país | **morto** · `COUNTRY_SCOPE`/`SOURCE_LOCATION` proibidos no corpo |
| RT10 | áudio temporário vira artefacto permanente | **morto** · `mkdtemp` + `rmtree`, e o único `media_type` entregue é `text/plain` |
| RT11 | executor escreve no banco | **morto** · nenhum `execute`/`cursor`/`insert` |
| RT18 | erro de ASR vira REJECTED | **morto** · os três erros mapeiam para `ERROR` |
| RT20 | aba YouTube sobreposta | **morto** · 0 ficheiros dela tocados |
| — | *eu ia inventar colunas no `derived_artifact`* | **apanhado antes de escrever** |
| — | *as minhas provas mediam a minha prosa* | **apanhado, 3.ª vez nesta casa** |

Não exercidos, e ficam **NOT_EXERCISED**, nunca PASS: RT4, RT6, RT12, RT13,
RT14, RT15, RT16, RT17, RT19 — todos exigem uma corrida contra banco.

```
RED_TEAM_EXERCIDOS     = 11 de 20
RED_TEAM_SURVIVORS     = 0 dos exercidos
RED_TEAM_NAO_EXERCIDOS = 9
```

---

# I · REGRESSÃO

```
TESTS_BEFORE   3744    ·  154 vermelhos históricos
TESTS_AFTER    3772    ·  +28 provas novas
NEW_FAILURES   0
DISAPPEARED_TESTS 0
```

Quatro reprovações apareceram na primeira comparação, e **as quatro eram as
sentinelas que a própria C4G deixou**, a dispararem como projectadas:

```
test_nenhum_executor_de_derivacao_de_audio_nasceu
test_a_porta_da_derivacao_pergunta_a_um_dono_so
test_video_declarado_nao_vai_para_a_derivacao_de_pdf
test_a_cadeia_inteira_do_video_num_so_lugar
```

A C4G escreveu-as assim: *«ela reprova no dia em que um executor de áudio for
declarado à porta, e a mensagem diz o que rever»*. Foram **actualizadas para a
verdade nova, não apagadas** — e a que guardava o buraco passou a guardar o
degrau seguinte.

```
UMA SENTINELA QUE DISPARA NÃO É UMA REGRESSÃO: É UM AVISO A CHEGAR.
APAGÁ-LA SERIA CALAR O AVISO EM VEZ DE O ATENDER.
```

---

# J · SYSTEM MAP

Passa a haver um segundo executor de derivação declarado. **Nenhuma aresta nova
fica OBSERVED**: `EXECUTOR EXISTS != EDGE EXISTS != FLOW OBSERVED`, e nenhuma
corrida real aconteceu.

---

# K · O QUE NÃO MUDOU

```
YouTube (aba paralela)   ·  ferramentas/fala_local.py  ·  LIVE  ·  Sala
julgamento da Admission  ·  Intelligence  ·  Portal  ·  Bíblia
DISPOSITIVO_PADRAO = CPU ·  as 16 versões do know-how
```

---

# L · DESCONHECIDOS

- o texto que a placa produz é o certo? `NOT_MEASURED` desde a C4E;
- `SOURCE_ID` canónico de `bayer_italia`: **não existe** no cadastro em
  `IT-Tn-nnn`. O que existe é a conta com identidade `PROVED`. Continua `UNKNOWN`,
  e esta missão não o criou;
- a Admission aceitaria este item? Nunca correu.

---

# M · RISCO RESTANTE

O executor existe e **nunca correu numa corrida real**. É precisamente o estado
que esta casa chama de `CAN DO != DID DO` — e a única defesa que ele tem hoje
são as 28 provas e a sentinela que diz, por escrito, que a estrada não correu.

---

# N · KNOW_HOW_DELTA

```
ATUALIZAÇÃO NECESSÁRIA
```

Dois aprendizados duráveis, e nenhum foi escrito no know-how canónico — ele
continua em 16 versões divergentes, e reconciliá-las é missão própria:

1. **`DECLARADO PELO OBSERVADOR > DEDUZIDO DO NOME > NÃO SEI`** — e o corolário
   medido: uma trava de espécie com a espécie apagada a montante não protege
   nada, ela só não tem o que ler.
2. **Um dono de capacidade pode ser reutilizado por um executor novo sem
   duplicar a capacidade** — a ponte de mídia não abre `WhisperModel`; ela pede
   texto ao dono que já existia.

E um terceiro, que é sobre método: **uma lista de um com forma de registo
esconde que não escala**, e o ficheiro que a tinha já escrevera a profecia.

---

# O · CONSTITUIÇÃO

```
BIBLE_CHANGE_REQUIRED    = NO
CONTRACT_CHANGE_REQUIRED = NO
```

Tudo o que esta missão fez **realiza** contrato já existente: a espécie fechada
da 022, o contrato do executor de derivação, o E7 do texto, e a separação
`ERROR != REJECTED`. Nada foi alargado.

---

# P · VEREDITO

```
MEDIA_COLLECTION_PIPELINE   = PARTIAL
FULL_MEDIA_TO_WAITING_ROOM  = NOT_PROVEN
```

---

# Q · PRÓXIMO PASSO MÍNIMO

Um só:

> **Correr a cadeia RAW → DERIVED contra o `banco-descartavel.yml`, com um
> fixture de áudio pequeno versionável e o reconhecedor substituído por um
> executor declarado de teste** — para provar a ESTRADA sem fingir o
> reconhecedor, que já está provado noutro sítio.
