# C8 · CONVERGÊNCIA GPU → LINHA SCRAP — a entrega

Duas frentes cresceram da mesma raiz e não se viram mais. Uma ensinou a máquina
a dizer a verdade sobre o ferro que usou; a outra ensinou o corpus a dizer a
verdade sobre a procedência do texto e o lugar do facto.

Esta missão junta-as. Não por merge: por **delta semântico**, ficheiro a
ficheiro, com a razão escrita ao lado de cada um que veio e de cada um que ficou.

```
HEAD MAIS NOVO NUMA FRENTE != ESTADO GLOBAL MAIS NOVO.
```

---

# A · BASE

```
BASE_BRANCH  claude/sintonia-fact-location-c7
BASE_HEAD    95f097a9041b2e518c71c16ac150511f2414c9bf
```

# B · FONTE DOS DELTAS

```
SOURCE_GPU_BRANCH  claude/sintonia-scrap-gpu-quality-c4c
SOURCE_GPU_HEAD    06b5055d2acefe6e462cf9ac170a2a24eccdf018
```

# C · BASE COMUM

```
MERGE_BASE  6ea058d3b5f67e0a74f4db09ab81d26d61d9c3f1
```

As quatro referências do coordenador foram medidas e conferem. A base é a C7; a
linha GPU é fonte, nunca destino.

# D · BRANCH DE INTEGRAÇÃO

```
INTEGRATION_BRANCH  claude/sintonia-scrap-convergence-c8
```

# E · ESTADO FINAL

```
FINAL_HEAD   ver rodapé
PUSH_STATE   PUSHED, sem force
WORKTREE     uma, limpa
```

---

# F · O QUE TORNOU A INTEGRAÇÃO SEGURA, E FOI MEDIDO ANTES DE TOCAR EM NADA

Duas medições, e as duas mudam o risco da missão:

**1 · as duas frentes tocaram conjuntos DISJUNTOS de ficheiros.**

```
so a linha GPU   11 ficheiros
so a linha C7    14 ficheiros
INTERSECAO        0
```

**2 · os cinco ficheiros que a linha GPU alterou estão IDÊNTICOS entre a base
comum e a C7.**

```
ferramentas/fala_local.py             merge-base == C7
ferramentas/instagram_transcrever.py  merge-base == C7
ferramentas/youtube_transcrever.py    merge-base == C7
provas/asr_banco.py                   merge-base == C7
.github/workflows/scrap-social.yml    merge-base == C7
```

Logo tomar a versão da linha GPU **introduz exactamente os deltas dela e nada
mais**. Isso não é uma esperança: é uma propriedade verificável dos três
`git rev-parse`, e é o que separa esta integração de uma cópia cega.

```
COMPARAR PRIMEIRO NAO E BUROCRACIA: E O QUE TRANSFORMA UMA COPIA NUMA DECISAO.
```

O workflow foi a excepção e por isso foi tratado à parte: nele a linha GPU pôs
**duas** fases, e só uma devia vir. Foi **recortado**, não copiado.

---

# G · DELTAS PORTADOS

| ficheiro | o que traz |
|---|---|
| `ferramentas/fala_local.py` | o trace verdadeiro do dispositivo e o runtime CUDA process-local |
| `ferramentas/instagram_transcrever.py` | ficha de ferro só quando houve execução |
| `ferramentas/youtube_transcrever.py` | idem, e a queda passa a levar o trace |
| `provas/asr_banco.py` | o banco lê `DEVICE_EXECUTION`, não só a escolha |
| `provas/gpu_asr_smoke.py` | a prova técnica da placa, reproduzível |
| `tests/test_c4_gpu_local.py` | a renomeação propagada |
| `tests/test_c4b_gpu_execucao.py` | o red team do trace, 26 provas |
| `.github/workflows/scrap-social.yml` | **só** a fase `gpu-asr` |

# H · DELTAS **NÃO** PORTADOS, E A RAZÃO DE CADA UM

A pergunta que decidiu cada linha:

```
ISTO E CAPACIDADE OPERACIONAL, OU TESTEMUNHA HISTORICA DE UMA INVESTIGACAO?
```

| o que ficou | porquê |
|---|---|
| `provas/corpus_recuperar.py` | lê o manifesto dos **oito Reels legados**. Testemunha de uma investigação, não capacidade desta linha |
| `tests/test_c4c_corpus.py` | segue o anterior |
| fase `gpu-bench` | depende de um corpus que **não está** na máquina da placa. Uma fase que hoje não pode passar não é capacidade: é uma promessa vermelha |
| a secção C4C do documento da C4 | reduzida a um ponteiro para a branch que a produziu |
| os 8 RAW legados | não entram no Git, não sobem ao bucket, não viram `raw_asset` |

Nada disto foi apagado: vive na sua branch, com o seu head escrito no ponteiro.

---

# I · O CONTRATO DO FERRO, DEPOIS DA CONVERGÊNCIA

| campo | o que diz | quando se sabe |
|---|---|---|
| `ASR_DEVICE_REQUESTED` | o que se pediu | antes de tudo |
| `ASR_DEVICE_SELECTED` | o que o resolvedor escolheu | na resolução |
| `ASR_ACCELERATOR_SELECTED` | o acelerador da escolha | idem |
| `ASR_DEVICE` | a configuração tentada | idem |
| `ASR_DEVICE_EXECUTION` | `PROVEN` · `FAILED` · `NOT_RUN` | **depois da inferência** |
| `ASR_DEVICE_USED` | o ferro, só quando `PROVEN` | idem |
| `ASR_ACCELERATOR` | idem | idem |

Exercido nesta árvore integrada:

```
GPU escolhida + queda  ->  EXECUTION FAILED · USED NOT_KNOWN · ACCELERATOR NOT_KNOWN
GPU escolhida + OK     ->  EXECUTION PROVEN · USED GPU       · ACCELERATOR CUDA
```

```
DEVICE REQUESTED != DEVICE SELECTED != DEVICE EXECUTION PROVEN != DEVICE USED
```

# J · ASR OWNERS

```
ASR_OWNERS = 1   ·   ferramentas/fala_local.py
```

Varrida a árvore inteira por sintaxe: nenhum outro sítio instancia
`WhisperModel`. Nenhum adaptador toca em política de dispositivo.

---

# K · C5 · L · C6 · M · C7 — OS INVARIANTES

Medidos na árvore integrada, e não assumidos:

```
C5   ESPECIES_DO_TEXTO = (NATIVE_CAPTION_ORIGINAL, NATIVE_CAPTION_TRANSLATED,
                          ASR_LOCAL, «NAO SEI»)

C6   serve_para_original(NAO SEI)                  False
     serve_para_original(NATIVE_CAPTION_TRANSLATED) False
     serve_para_original(ASR_LOCAL)                 True
     medir() continua a chamar pv.serve_para_original

C7   «Periodico olivo 1 Maggio 2026»   -> NOT_KNOWN
     «calendario fitosanitario»        -> NOT_KNOWN
     «barbabietole da zucchero»        -> NOT_KNOWN
     «beaucoup de pluie»               -> NOT_KNOWN
     «ho parlato con Francesco»        -> NOT_KNOWN
     «La Rioja» -> ES   «Verona» -> IT   «Champagne» -> FR
     lugar_do_fato nao chama _tem / _perto / _raizes
```

As três suítes correm verdes: **88 provas** de C5, C6 e C7, sem uma alteração.

# N · GPU TESTS

```
tests/test_c4b_gpu_execucao.py   26 provas   verdes
tests/test_c4_gpu_local.py       51 provas   verdes
tests/test_c8_convergencia.py    21 provas   verdes
```

# O · REGRESSÃO GLOBAL

```
BASE_TOTAL     2079      FINAL_TOTAL     ver rodapé
BASE_FAILURES    20      FINAL_FAILURES  ver rodapé
BASE_ERRORS       1      FINAL_ERRORS    ver rodapé
NEW_FAILURES              ver rodapé
```

---

# P · WORKFLOW

A fase `gpu-asr` entrou; a `gpu-bench` não. E a guarda do job `scrap` foi
corrigida ao mesmo tempo, porque ela decide por **exclusão**:

```
if: inputs.fase != 'hardware' && inputs.fase != 'gpu-asr'
```

```
UMA LISTA DE EXCLUSAO NAO SABE O QUE AINDA NAO NASCEU.
```

Há prova que varre os **jobs** do workflow e exige que cada fase de máquina
esteja excluída do `scrap`. Ela mede jobs, não linhas — a primeira versão media
linhas e apanhava condições de passo dentro do próprio `scrap`.

A fase não instala nada, não adquire mídia, não usa YouTube nem Apify, não
escreve RAW e para com `MODEL_NOT_PRESENT` se o modelo não estiver em cache.

# Q · SCRAP × COLLECTION CANÓNICA

```
COL-LAW-505 = NOT_APPLICABLE_TO_THIS_CONVERGENCE
```

| | |
|---|---|
| segundo modelo de `RUN` | **NÃO** |
| segundo `RAW` | **NÃO** |
| `SOURCE_ID` / `DOCUMENT_ID` fabricado | **NÃO** |
| Admission paralela | **NÃO** |
| orquestrador novo | **NÃO** |
| `raw_asset`, `storage.objects`, bucket `raw` | **intocados** |

Provado por `git diff --name-only` contra a base comum em `coleta/ingresso.py`,
`orquestrador/`, `supabase/` e `leis/retorno_da_coleta.py`: vazio.

Os oito RAW legados **não** foram importados. Um storage object sem observação
canónica seria um defeito novo, e `RAW_OBSERVATION_ID = raw_asset.id` continua a
valer.

---

# R · A LEI DA AQUISIÇÃO — AUDIO-ONLY

```
TRANSCRIPTION NEED != VIDEO DOWNLOAD.
```

Esta missão **não** implementa a rota. Regista a decisão, que é o que ela pode
fazer honestamente.

**O QUE.** Quando o objectivo é ASR, o artefato de aquisição desejado é **áudio**,
não vídeo.

**POR QUÊ.** Vídeo completo gasta banda, armazenamento e processamento que a
transcrição não precisa. O fluxo desejado é:

```
SOURCE -> AUDIO-ONLY ACQUISITION -> RAW AUDIO -> ASR -> TRANSCRIPT
```

e **não**:

```
VIDEO DOWNLOAD -> EXTRACT AUDIO -> DISCARD VIDEO
```

**PROVA.** A capacidade GPU está provada e não depende dos pixels. E o próprio
extractor da casa já pede `-vn` ao `ffmpeg` — o vídeo é descartado no primeiro
passo, o que mostra que ele nunca foi requisito e sim um efeito colateral de
como se adquiriu.

**CONSEQUÊNCIA.** Onde uma plataforma não oferecer rota audio-only permitida, o
estado é `AUDIO_ONLY_ROUTE = BLOCKED` ou `REQUIRES_AUTHORIZATION`.

```
AUSENCIA DE ROTA AUDIO-ONLY NAO E AUTORIZACAO PARA BAIXAR O VIDEO INTEIRO.
```

Vídeo completo só quando a missão precisar mesmo dos pixels.

---

# S · O QUE MUDOU

O reconhecedor desta linha passou a dizer a verdade sobre o ferro que usou, e a
saber encontrar o runtime CUDA no processo sem tocar na máquina. A prova técnica
da placa entrou como fase do workflow canónico. Os dois transcritores deixaram
de carimbar ferro em registos onde nada correu.

# T · O QUE NÃO MUDOU

O gate de política do YouTube da C5. A espécie do texto da C6. O casador de
lugar da C7. O classificador temático. A política de compute — `COMPUTE_GPU`
continua `float16` e o dispositivo padrão continua `CPU`. A Collection inteira.
A chave `YOUTUBE_DATA_API_KEY`, que não foi usada nesta missão.

# U · O QUE CONTINUA DESCONHECIDO

Se a placa **melhora a qualidade** do texto: `GPU_QUALITY_BENCHMARK = NOT_RUN`,
porque o corpus com verdade declarada não está na máquina que tem a placa. E
quais plataformas oferecem rota audio-only permitida — é a pergunta da próxima
missão, não desta.

# V · RISCO RESTANTE

A fase `gpu-asr` depende de o toolkit CUDA estar onde `_pastas_de_dll()` procura.
Se mudar de sítio, ela falha **com diagnóstico** — não em silêncio. E a linha
C4C fica viva noutra branch: quem precisar da investigação do corpus tem de lá
ir, o que é intencional e está escrito no ponteiro.
