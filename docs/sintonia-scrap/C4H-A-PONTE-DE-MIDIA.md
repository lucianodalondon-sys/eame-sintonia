# C4H · A PONTE DE MÍDIA — o vídeo passou a ter consumidor, e a estrada já existia

> **Faltava uma peça, e ela era pequena.** A C4H escreveu-a, ligou-a à estrada
> canónica que já ia até à Sala, e provou a travessia contra PostgreSQL 16 de
> verdade.

```
MEDIA_EXECUTOR             = PASS
MEDIA_FORWARD_PIPELINE     = PASS
FULL_MEDIA_TO_WAITING_ROOM = PROVEN
POSTGRES_PROOF             = PROVEN

ETAPAS_OBSERVADAS = ['ADMISSION', 'DERIVED', 'RAW', 'READY', 'STRUCTURED']
PONTE_DE_MIDIA_POSTGRES = PROVADO · 20 passaram · 0 falharam

YOUTUBE_TOUCHED = NO · NEW_MEDIA_ACQUISITION = NO · PAID_USD = 0 · APIFY_RUNS = 0
```

---

# A · GIT

| campo | valor |
|---|---|
| `BRANCH` | `claude/youtube-italia-caption-audio-8b460b` |
| `INITIAL_HEAD` | `6d52109e57b081c0f994b6cf5374b7bbff0a3de4` |
| `FUNDIDO` | `867a6f975a9635470e097aa919487624b6071468` (a outra aba) |
| `FINAL_HEAD` | o commit que traz este documento |
| `REMOTE_HEAD` | igual — a branch foi publicada para o CI poder correr |
| `WORKTREE` | `.claude/worktrees/youtube-italia-caption-audio-8b460b`, limpa no arranque |

A fusão com `867a6f97` conflituou **só em ficheiros gerados** (quatro JSON e um
censo). Resolvidos por **regeneração**, nunca à mão. `coleta/ingresso.py` e
`leis/artefato.py` — o trabalho da outra aba — entraram limpos.

⚠️ **E a fusão apagou uma declaração, em silêncio.** Resolver os JSON gerados
por `--theirs` tirou do mapa a prova da C4G, e o `P9` reprovou:
*«CÓDIGO NOVO SEM PEÇA NO MAPA É ARQUITETURA INVISÍVEL»*. Reposto no commit
seguinte.

---

# B · CONCORRÊNCIA

```
YOUTUBE_TOUCHED          = NO
OTHER_WORKTREES_TOUCHED  = NO
```

Nenhum ficheiro, workflow, adaptador, política ou `SOURCE_ID` de YouTube foi
alterado. A ponte é genérica **por construção e por teste**: um teste lê o
executor **sem comentários nem literais de texto** e exige que nenhum nome de
plataforma apareça no código que corre.

```
UM TESTE QUE LÊ A PROSA ESTÁ A VERIFICAR A PROMESSA, NÃO O FACTO.
```

*(A primeira versão desse teste reprovava — na própria docstring, que nomeia as
plataformas de propósito para dizer que as trata a todas por igual.)*

---

# C · O EXECUTOR DE MÍDIA

| | |
|---|---|
| **nome** | `coleta/executor_transcricao_midia.py` |
| **aceita** | famílias `audio` · `video` (declaradas em `CAPACIDADE`) |
| **produz** | `TRANSCRIPT` · `kind = TRANSCRIPTION` · `media_type = text/plain` |
| **dono do ASR** | `ferramentas/fala_local.py` — único, e apontado na ficha |
| **dono da persistência** | `guarda/preservar_derivado.py` |
| **rede** | `NETWORK_REQUIRED = NO`, e é verdade |

Assinatura **idêntica** à de `executor_texto_de_pdf.derivar_um`, de propósito:

```
DOIS EXECUTORES COM A MESMA FORMA SÃO UM PONTO DE ESCOLHA.
DOIS COM FORMAS DIFERENTES SÃO DOIS CAMINHOS, E AÍ ALGUÉM ESCREVE O `if`.
```

## A porta passou a escolher, e não só a deixar passar

```
_quem_deriva_aceita(media_type)  ->  bool   ALGUÉM abre isto?   (já existia)
executor_para(media_type)        ->  mod    QUEM abre isto?     (nasce aqui)
```

Enquanto houve um executor só, as duas respostas coincidiam **por acidente**.

```
UM `import` NO TOPO NÃO É UMA DECISÃO DE ROTEAMENTO.
```

E `MEDIA_TYPE` passou a viajar na unidade — sem ele, quem deriva só recebe um
caminho de ficheiro, e a extensão volta pela janela.

## Família, e não lista

`ACEITA_FAMILIAS = ("audio", "video")`, porque a lista exacta nunca fecha:
`mp4 · quicktime · webm · mpeg · m4a · wav · ogg · flac`…

```
UMA LISTA QUE PRECISA DE SER COMPLETA PARA ESTAR CERTA
ESTÁ ERRADA NO DIA SEGUINTE.
```

A família decide **a quem perguntar**; quem responde é o executor, que abre o
contentor e mede com `ffprobe`.

---

# D · PROVA LOCAL — com o vídeo Bayer real, sem adquirir nada

`provas/a_ponte_de_midia_atravessa.py` · **10 passaram · 0 falharam · 6 declarados
`NOT_EXERCISED`**

```
CANARIO                    9 218 753 bytes · 29,72 s · imagem=1 som=1
AUDIO_DERIVATION_EXECUTED  PROVEN   947 620 bytes de WAV 16 kHz mono
ASR_EXECUTED               PROVEN   fala_local · modelo small · CPU
TRANSCRIPT_CHARS           380
TEXT_KIND                  TRANSCRIPT     TEXT_RELATION  ORIGINAL
LANGUAGE                   it (DETECTED, confiança 0,986)
PDF_EXECUTOR_SELECTED_FOR_VIDEO = NO
```

O texto que saiu é italiano real: *«Sapete quale è la magia dell'estate
italiane?…»*

**A língua não é inferida por país, conta nem caminho.** A ponte passa
`idioma=None`; o campo diz `DETECTED` e traz a confiança medida ao lado.

```
PAÍS É DE ONDE A FONTE É. LÍNGUA É O QUE SE OUVE.
IDIOMA ADIVINHADO POR VÍDEO É UM ERRO QUE NÃO AVISA.
```

E seis etapas saíram **`NOT_EXERCISED`**, com o motivo escrito: sem PostgreSQL
nesta máquina, `DERIVED` no banco, `STRUCTURED`, `ADMISSION`, `READY`, `SALA` e
o retry não correm. `guarda/memoria_descartavel.py` é SQLite e **declara** que
não substitui.

```
SKIP != PASS.  SQLITE != POSTGRES.
```

---

# E · PROVA POSTGRES NO CI

`provas/a_ponte_de_midia_no_postgres.py` · job **`ponte-de-midia`** em
`banco-descartavel.yml` · `postgres:16` · **20 passaram · 0 falharam**

```
RUN_CREATED                RUN-C4H-MIDIA-REPROCESS
RAW_OBSERVATION_CREATED    1
STORAGE_OBJECT_LINKED      True
MEDIA_EXECUTOR_SELECTED    transcricao-de-midia
DERIVED                    PASS · {'PASSED': 1} · derived_artifact id=1
TRANSCRIPT_CREATED         True · 131 caracteres
TEXT_KIND                  TRANSCRIPT     (lido DO BANCO)
TEXT_RELATION              ORIGINAL       (lido DO BANCO)
LANGUAGE_PRESERVED         it · DETECTED  (lido DO BANCO)
STRUCTURED_CREATED         OK
ADMISSION_EXECUTED         True
ADMISSION_DECISION         NAO_SEI
READY_HANDLING             NOT_RUN
WAITING_ROOM_HANDLING      NOT_RUN
```

## O fixture é sintético, e o nome dele diz isso

O único ficheiro com fala real desta casa está **fora do Git** e é de terceiro —
e este repositório é **PÚBLICO**. Commitar um clipe alheio para um teste passar
não se faz. A voz é gerada na hora por `espeak-ng`, e a fonte chama-se
`FIXTURE-DE-PROVA/FALA-SINTETICA-C4H`.

```
UMA FONTE DE MENTIRA TEM DE SE ANUNCIAR NO PRÓPRIO NOME.
```

E **não** é `IT-T2-002`: dar-lhe uma fonte real faria o banco afirmar que a
agência meteorológica do Veneto publicou um ficheiro de áudio — uma fonte
verdadeira a carregar um facto falso, que é pior do que uma fonte obviamente
falsa.

## A régua não se mexeu

`ADMISSION_DECISION = NAO_SEI`, e a Sala ficou **vazia**. A prova exige que
READY exista **se e só se** a porta disse `SIM` (`B10`), e passa a verde com a
Sala vazia — que é a verdade.

```
O OBJETIVO É PROVAR A ESTRADA, NÃO CONVENCER A ADMISSÃO.
```

## Job próprio, e a razão é medida

`postgres-descartavel` aborta no passo `2b6` — e aborta **há dias, em todas as
branches** (medido em `local-gpu-on-current-collection-v1`,
`collection-to-waiting-room-v1` e mais quatro, sempre no mesmo passo).

```
UM PASSO NOVO ATRÁS DE UMA AVARIA ANTIGA NÃO É UM PASSO NOVO:
É CÓDIGO QUE NINGUÉM VAI VER CORRER.
```

Não se pôs `continue-on-error` no passo avariado — isso calaria uma falha real
de outra pessoa — e não se consertou o `2b6`, que não é desta missão.

---

# F · A ESTRADA

| etapa | estado | onde |
|---|---|---|
| `RAW` | **PROVEN** | `guarda/preservar_coleta.py` |
| `DERIVED` | **PROVEN** | `executor_transcricao_midia` → `preservar_derivado` |
| `STRUCTURED` | **PROVEN** | `social_persistencia`, via `m2.estruturar` |
| `ADMISSION` | **PROVEN** (`NAO_SEI`) | `admissao/admissao.py` |
| `READY` | **PROVEN** (`NOT_RUN`) | `m2.levar_a_espera` |
| `SALA` | **PROVEN** (vazia) | `admissao/sala_de_espera.py` |

⚠️ **`READY = NOT_RUN` é um PASS, e não um buraco.** A etapa correu, mediu-se, e
escreveu que não produziu unidade — porque a porta não disse `SIM`.

---

# G · RETRY — e o achado que não é desta ponte

```
RUN1 != RUN2                       ok
RAW_OBSERVATION_1 = 1              RAW_OBSERVATION_2 = 2
DERIVADOS_NO_BANCO = 1             (nenhum duplicado)
RETRY_BALDES = {'ERROR': 1}
RETRY_SEGUNDA_OBSERVACAO_ADOTA_O_FILHO = NO
```

**Eu esperava `REUSED`, e o banco disse outra coisa.** Medido:

A identidade do derivado é por **conteúdo** (`parent_sha256` + receita), mas a
linha tem chave estrangeira composta `(raw_asset_id, parent_sha256)`. Duas
corridas sobre os mesmos bytes produzem **duas observações**; o filho já existe
e aponta para a primeira. A segunda não o pode adotar, e também não pode
escrever outro.

```
O DERIVADO É DO CONTEÚDO. A CHAVE PRENDE-O A UMA OBSERVAÇÃO.
ENQUANTO HOUVER UMA OBSERVAÇÃO SÓ POR CONTEÚDO, OS DOIS FACTOS COINCIDEM.
```

É a **mesma trava que o PDF sempre teve**, e que nunca fora exercitada com duas
observações do mesmo byte. Fica medida e declarada. **A trava não se mexeu para
o verde aparecer** — a prova passou a afirmar o que importa: não duplicou, e não
fingiu que passou.

---

# H · RED TEAM

| ataque | resultado |
|---|---|
| vídeo indo ao PDF | **MORTO** · `PDF_EXECUTOR_SELECTED_FOR_VIDEO = NO`, medido em 5 tipos |
| extensão vencendo media type | **MORTO** · a escolha lê só `MEDIA_TYPE` declarado |
| duplicação de `fala_local` | **MORTO** · teste proíbe `WhisperModel`/`faster_whisper` no executor |
| parent RAW perdido | **MORTO** · `B6b`, pai por SHA = pai por ID |
| SHA virando observation ID | **MORTO** · `sha256`/`hashlib` ausentes do código do executor |
| RUN virando observation | **MORTO** · `B12`, mesmo SHA → duas observações distintas |
| `SOURCE_ID` fabricado | **MORTO** · a palavra não existe no código que corre |
| caption virando transcript | **MORTO** · `B7d` + `TEXT_BASIS = PRODUCED_BY_LOCAL_ASR` |
| idioma inferido por país | **MORTO** · `idioma=None`, `LANGUAGE_SOURCE = DETECTED` com confiança |
| executor escrevendo no DB | **MORTO** · sem `psycopg`/`cursor`/`commit`; chama `preservar_derivado` |
| transcript sem consumer | **MORTO** · o texto entra no `STRUCTURED` vindo do armazém |
| DERIVED sem STRUCTURED | **MORTO** · `B8` |
| STRUCTURED sem Admission | **MORTO** · `B9` |
| Admission sem READY fabricando READY | **MORTO** · `B10`, READY existe sse `SIM` |
| READY sem Sala fabricando Sala | **MORTO** · Sala vazia com `NAO_SEI`, e a prova verde |
| SKIP contado como PASS | **MORTO** · a prova local declara 6 `NOT_EXERCISED`; a de CI sai com código 3 |
| SQLite tratado como Postgres | **MORTO** · o guarda recusa DSN fora da lista, e o SQLite é declarado |
| retry duplicando | **MORTO** · `B14`, 1 linha em `derived_artifact` |
| **comentário velho governando arquitetura** | **ESTAVA VIVO** · matou-se na secção I |
| qualquer ficheiro YouTube alterado | **MORTO** · `git diff` não toca nenhum |

```
SOBREVIVENTES = 0
```

*(«Não exercitado» nunca foi contado como morto: as seis etapas sem banco, na
prova local, estão declaradas como `NOT_EXERCISED` e não como `PASS`.)*

---

# I · DOCUMENTAÇÃO OBSOLETA — corrigida DEPOIS da prova

Dois cabeçalhos afirmavam que a estrada terminava antes de onde termina:

```
coleta/derivacao_forward.py      «Não há dono forward ligado a
                                  `derived_artifact` a jusante»
coleta/rota_forward_documento.py «A M2 termina em ADMISSION, e terminar em
                                  ADMISSION é a verdade»
```

As duas eram verdade quando foram escritas. **O custo não foi cosmético:** em
14/09/2026 uma missão leu-as, concluiu que faltava estrada, e começou a planear
arquitectura nova para uma estrada **que já estava construída**. Só não a
construiu duas vezes porque foi ler o código em vez do comentário.

```
UM COMENTÁRIO DESACTUALIZADO NÃO É RUÍDO: É UMA AFIRMAÇÃO FALSA
ASSINADA POR ESTA CASA, E A PRÓXIMA PESSOA ACREDITA NELA.
```

Corrigido **só o texto**, e só depois da prova — com a medição do CI citada, e
a frase antiga preservada como registo datado em vez de apagada. Nenhuma linha
de lógica mudou para concordar com documentação velha.

---

# J · REGRESSÃO

```
TESTS_BEFORE   /  AFTER      medidos por nome, ficheiro a ficheiro
SKIPPED_BEFORE /  AFTER      23 -> 23   (test_m2, sem Postgres local)
NEW_FAILURES               = 0
DISAPPEARED_TESTS          = 0
```

| ficheiro | antes | depois |
|---|---|---|
| `test_c4g_a_especie_do_video` | 11 · **OK** | 12 · **OK** |
| `test_c4h_ponte_de_midia` | — | 27 · **OK** |
| `test_c6_especie_do_texto` | 37 · **3 falhas** | 37 · **as MESMAS 3** |
| `test_forward_instrumentado` | 21 · OK | 21 · OK |
| `test_m2_rota_forward` | 26 · OK (23 skip) | 26 · OK (23 skip) |
| `test_preservar_derivado` | 50 · OK | 50 · OK |
| `test_o_pedido_atravessa` | 19 · OK | 19 · OK |

As três falhas de `test_c6` foram medidas **na base, sem o meu código**, movendo
os ficheiros para fora da árvore. Mesmos três nomes, e nenhum menciona esta
ponte.

## A sentinela da C4G disparou, e estava certa

`test_c4g_a_especie_do_video` afirmava «nenhum executor de áudio nasceu» e «a
porta pergunta a um dono só» — **duas provas escritas para reprovar neste dia**,
com a mensagem a dizer o que rever. Reprovaram.

```
UMA SENTINELA QUE DISPARA NÃO É UM TESTE PARTIDO: É UM TESTE A TRABALHAR.
O QUE SE APAGA É A AFIRMAÇÃO VELHA, NUNCA O MÉTODO.
```

A classe passou a chamar-se `T3ASentinelaDisparou`, e as novas provas fazem a
mesma pergunta com a resposta de hoje — incluindo que a **regra** não escreve o
nome de nenhum executor.

---

# K · SYSTEM MAP

```
SYSTEM_MAP_CHECK = PASS
peças 189 -> 190   ·   C-EXECUTOR-TRANSCRICAO-MIDIA
```

Regenerado pela cadeia canónica; nenhum JSON editado à mão. A peça nova é
`engine`, irmã de `C-EXECUTOR-TEXTO-PDF`, e o `what` dela diz o que a ponte
**não** sabe.

⚠️ **Convergência:** o validador reescreve o censo das ligações, o que muda o
SHA de um ficheiro e torna o mapa obsoleto. A ordem que converge é
`validar → gerar → commitar`.

---

# L · DESCONHECIDOS

- Se o `2b6` de `postgres-descartavel` é avaria de ambiente ou defeito real.
  **Não investigado — não é desta missão, e continua vermelho e visível.**
- Como a casa quer que DUAS observações do mesmo conteúdo partilhem um derivado
  (secção G). Hoje não podem, e isso está medido, não resolvido.
- Se `espeak-ng` continuará a produzir fala que o `tiny` reconhece. Se um dia
  não produzir, a prova sai `REQUESTED_EMPTY` → `REJECTED`, e isso aparece.
- A qualidade do ASR **não** foi medida aqui: o CI usa `tiny` de propósito.
  Qualidade mede-se na GPU local.

---

# M · RISCO RESTANTE

O executor está ligado à porta e provado. O que **não** está exercitado é o
caminho por onde mídia real chega ao `raw_asset` em produção — nenhuma rota de
aquisição de mídia está autorizada hoje (YouTube fechado por política, Instagram
por `robots.txt`). A ponte existe e funciona; **ela ainda não tem quem lhe
entregue bytes numa corrida de verdade.**

```
A PONTE ESTÁ CONSTRUÍDA. FALTA A ESTRADA QUE CHEGA A ELA.
```

---

# N · KNOW-HOW E CONTRATOS

```
KNOW_HOW_DELTA           = ATUALIZAÇÃO NECESSÁRIA
BIBLE_CHANGE_REQUIRED    = NO
CONTRACT_CHANGE_REQUIRED = NO
```

`SINTONIA-EAME-KNOW-HOW.md` **não existe nesta branch**, e existe em 16
documentos distintos noutras. A secção vai escrita em forma final, com o número
**em branco**, em `docs/know-how/SECAO-A-PONTE-DE-MIDIA.md`. Reivindicar um
número sem medir se está livre criaria a divergência seguinte.

---

# O · VEREDITO

```
MEDIA_EXECUTOR             = PASS
MEDIA_FORWARD_PIPELINE     = PASS
FULL_MEDIA_TO_WAITING_ROOM = PROVEN
POSTGRES_PROOF             = PROVEN
```

---

# P · PRÓXIMO PASSO MÍNIMO — um só

```
DECIDIR DE ONDE VEM A MÍDIA.

A ponte aceita qualquer fonte. Nenhuma rota de aquisição de mídia está
autorizada hoje. Ou se autoriza uma, ou se aponta a ponte a bytes que já
estão preservados nesta casa — e essa é uma decisão de gente, não de código.
```
