# AUDIO-312 · A FALA->TEXTO E O INTERPRETADOR DA PRODUCAO

**Data:** 2026-09-24 (madrugada, antes da Big Collection)
**Lane:** `claude/it-scrap-v1` · **Mudou codigo?** NAO. Mudou a MAQUINA.
**Veredito:** `ASR_NO_INTERPRETADOR_DA_PRODUCAO = PROVED` (era `BLOCKED`)

---

## 1 · O QUE FOI MEDIDO — QUE INTERPRETADOR USA CADA PECA

| peca | interpretador MEDIDO | onde esta a prova |
|---|---|---|
| **workflow local / GitHub** | `py` -> `C:\actions-runner-2\_work\_tool\Python\3.12.10\x64\python.exe` | `py -0p` devolve **este e so este**; `.github/workflows/sintonia-scrap.yml` §1 resolve `$PY` com `for c in py python3 python` |
| **coletor** (`coleta/coletor.py`) | 3.12.10 | lancado por `orquestrador/orquestrador.py`, que faz `subprocess.run([sys.executable, *comando])` (linha 827) — herda o pai |
| **worker do Scrap/Curador** | 3.12.10 | `curadoria/supervisor.py:321` -> `cmd = cmd or [sys.executable, ... ciclo_continuo.py ...]`; **processo vivo medido agora**: `C:\actions-runner-2\_work\_tool\Python\3.12.10\x64\python.exe curadoria/supervisor.py` (PID 36620) e `... ponte_automatica.py --servir` (PID 23036) |
| **transcricao** (`ferramentas/fala_local.py`) | o do chamador -> 3.12.10 | `coleta/executor_transcricao_midia.py`, `coleta/ingresso.py` chamam-no no MESMO processo |

**A producao corre 3.12.10.** Nao ha um Python 3.11 de projeto nesta maquina:
`py -0p` so lista o 3.12.10. O unico 3.11 presente e o **proprio runtime do
Hermes** (`...hermes-agent\venv` e `...\.hermes-runtime\python\cpython-3.11...`),
e e por isso que uma medicao feita de dentro de uma sessao Hermes com `python`
ve a fala->texto a funcionar: **aquele 3.11 traz o `faster_whisper` no seu
proprio `site-packages`, nao nas libs da casa.**

```
O 3.11 QUE RESPONDIA NAO ERA O 3.11 DA PRODUCAO. ERA O DO OBSERVADOR.
INTERPRETADOR_PINNED = python3.11  ->  REFUTADO (ver §6)
```

## 2 · A CAUSA (medida, com traceback)

As bibliotecas de fala vivem FORA do repositorio, em `~/.sintonia-libs`, e
`ferramentas/fala_local.py` poe essa pasta no `sys.path` (linha 426). O que la
estava eram binarios **cp311**:

```
~/.sintonia-libs/ctranslate2/_ext.cp311-win_amd64.pyd
~/.sintonia-libs/yaml/_yaml.cp311-win_amd64.pyd
```

Sob o 3.12 da producao isso rebenta — nao por falta da biblioteca, por
**incompatibilidade de ABI**, e o traceback do teste diz exatamente onde:

```
File "C:\Users\London1\.sintonia-libs\numpy\_core\multiarray.py" ...
ModuleNotFoundError: No module named 'numpy._core._multiarray_umath'
```

Modulo a modulo, sob 3.12.10 com `PYTHONPATH=~/.sintonia-libs` (cp311):

```
numpy        FAIL  (ImportError)
onnxruntime  FAIL  (DLL load failed)
faster_whisper FAIL (ImportError, por arrasto)
ctranslate2  OK  · av OK · tokenizers OK · yt_dlp OK · yaml OK
```

Ou seja: **o import falhava, mas nao por estar «desinstalado»** — estava
instalado para o interpretador errado. A frase de erro do `fala_local`
(`ASR_INDISPONIVEL ... Instale FORA do repositorio`) aponta para o problema
certo sem dizer a ABI.

```
INSTALADO != IMPORT importa -> LIB_AUSENTE != LIB_INCOMPATIVEL_COM_O_INTERPRETADOR
```

## 3 · O QUE FOI APLICADO (a forma menos arriscada)

**Duas renomeacoes. Zero `pip`, zero rede, zero desinstalacao, zero codigo.**

```
~/.sintonia-libs               (cp311)  ->  ~/.sintonia-libs.bak-cp311   [PRESERVADO]
~/.sintonia-libs.bak-cp312     (cp312)  ->  ~/.sintonia-libs             [ATIVO]
```

A pasta `cp312` **ja existia nesta maquina** (tinha sido guardada como
`.bak-cp312` a 2026-09-18, e e importavel sob o 3.12.10 — medido antes de a
activar). Nao se instalou nada de novo; restaurou-se a build que casa com o
interpretador que a producao usa.

> ⚠️ **O Python do runner do GitHub e PARTILHADO.** `C:\actions-runner-2\.runner`
> declara `gitHubUrl = lucianodalondon-sys/portal-sintonia` e o unico repo em
> `_work\` e `portal-sintonia`. **Nada lhe foi feito** — nem pacotes, nem
> `site-packages`. A correcao mexe so em `~/.sintonia-libs`, do utilizador.
> O `site-packages` de `AppData\Local\Programs\Python\Python312` tambem nao foi
> tocado (e emprestado por `PYTHONPATH` nos testes, como a casa ja fazia).

### Versoes agora ativas em `~/.sintonia-libs` (cp312, AMD64)

```
faster_whisper 1.2.1 · ctranslate2 4.8.2 · numpy 2.5.2 · onnxruntime 1.29.0
av 18.1.0 · tokenizers 0.23.1 · huggingface_hub 1.29.0 · hf_xet 1.6.0
yt_dlp 2026.8.19 · pyyaml 6.0.3 · pypdf 6.16.2 · protobuf 7.36.1
fsspec 2026.7.0 · filelock 3.32.5 · flatbuffers 25.12.19 · tqdm 4.70.0
httpx 0.28.1 · httpcore 1.0.9 · h11 0.16.0 · anyio 4.14.2 · idna 3.19
certifi 2026.7.22 · packaging 26.3 · typing_extensions 4.16.0
click 8.5.0 · colorama 0.4.6
```

Preservado em `~/.sintonia-libs.bak-cp311` (cp311, para quem ainda corra 3.11):
`numpy 2.4.6 · onnxruntime 1.30.0 · huggingface_hub 1.32.0 · anyio 4.15.1 ·
filelock 4.0.1 · fsspec 2026.9.0 · protobuf 7.36.2 · tokenizers 0.23.2 ·
tqdm 4.70.1 · idna 3.20` (o resto igual).
**Reverter = as mesmas duas renomeacoes ao contrario.**

## 4 · A PROVA

### 4.1 os testes que a fala->texto bloqueava

Conjunto medido: os 18 ficheiros de `tests/` que tocam `fala_local` /
`executor_transcricao_midia`. Corridos com o **interpretador da producao**
(3.12.10), antes e depois de o caminho das libs casar com ele:

| | antes (`~/.sintonia-libs` cp311) | depois (cp312 no mesmo caminho) |
|---|---|---|
| OK | 119 | **127** |
| FAIL | 3 | 2 |
| ERROR | 4 | **0** |

**8 testes sairam do vermelho, todos por causa da ABI** — nao por eu ter mexido
no caminho `SINTONIA_LIBS`: a corrida final foi sem override nenhum, pelo
caminho POR OMISSAO que a producao usa.

```
test_c4_gpu_local.py::test_modelo_que_nao_carrega_nao_e_audio_sem_fala      ERROR -> OK
test_c4_gpu_local.py::test_rt6_a_placa_que_cai_na_carga_cai_para_o_processador_com_nome ERROR -> OK
test_c4_gpu_local.py::test_rt6b_falha_que_nao_e_memoria_cai_como_indisponivel ERROR -> OK
test_c4_gpu_local.py::test_oom_durante_o_reconhecimento_sobe_com_nome       (nao colhia) -> OK
test_c4_gpu_local.py::test_rt7_audio_invalido_nao_e_audio_sem_fala          (nao colhia) -> OK
test_c4_gpu_local.py::test_uma_falha_qualquer_no_reconhecimento_nao_vira_oom (nao colhia) -> OK
test_c4b_gpu_execucao.py::test_o_modelo_so_e_aceite_se_ja_estiver_na_maquina FAIL -> OK
test_c4h_ponte_de_midia.py::test_T8_a_lingua_detectada_viaja_com_a_fonte_dela ERROR -> OK
```

Ficaram **2 vermelhos, os mesmos de antes e alheios a isto**: dois testes da C6
que leem o proprio ficheiro e comparam `guarda\...` com `guarda/...` (separador
do Windows). Ja eram vermelhos na bateria da BC4.

### 4.2 uma transcricao real, com o interpretador da producao

Audio **que ja estava nesta maquina** (nenhuma rede nova), e que e o mesmo da
prova C13 — mesma SHA:

```
WAV          sintonia-canary-youtube-v1/YOUTUBE-PUBLIC-AUDIO-V1/zaEk8LE6SOQ.wav
SHA256       0167e22599b5fed72b534c60bc05c728341057b9def4dee7e18a4d7acca2ad95  (== C13)
ffprobe      pcm_s16le · 16 kHz · mono · 244,04 s · 7.809.414 bytes
INTERPRETADOR C:\actions-runner-2\_work\_tool\Python\3.12.10\x64\python.exe  (o da producao)
SINTONIA_LIBS C:\Users\London1\.sintonia-libs   (por omissao, sem override)
```

```
TRANSCRIPT_STATE       OK
TRANSCRIPT_CHARS       3010            (a C13 registou 3010 caracteres)
ASR_ENGINE             faster-whisper 1.2.1 · small · CTranslate2 · cpu/int8/16 threads
ASR_DEVICE_EXECUTION   PROVEN
LANGUAGE               it  ·  DETECTED  ·  confianca 0,983
MACHINE_SECONDS        89,0 s para 244,04 s de audio (RTF 2,74x)
COST_USD               0
ERROR                  None
```

Texto comparado com o gabarito guardado (`Temp/yt2-gabarito/zaEk8LE6SOQ.txt`):
**similaridade 0,976** — as diferencas sao nomes proprios («EGREA»/«gria»,
«Kestrel»/«acetamiprid»), que e o comportamento conhecido do motor.

Nao foi criado `RAW_ASSET_ID`, nao foi criado `SOURCE_ID`, nada foi escrito no
banco nem no acervo: caminho entra, texto sai.

## 5 · O QUE NAO MUDOU

- nenhuma linha de codigo (nem `fala_local.py`, nem workflows, nem adaptadores);
- nada instalado nem desinstalado por `pip`; **zero rede**;
- o 3.11 da casa intacto (`~/.sintonia-libs.bak-cp311` + o runtime do Hermes);
- o Python do runner do GitHub intacto — e ele e de outro repo (`portal-sintonia`);
- `site-packages` de `Python312` intacto;
- banco, acervo, RAW, `SOURCE_ID`, `DOCUMENT_ID`: nao tocados.

## 6 · ACHADOS, E UM DELES CORRIGE UMA AUDITORIA

1. **`INTERPRETER_PINNED = python3.11` esta REFUTADO** (auditoria de
   capacidades, §3.1). A capacidade nao esta «presa ao 3.11»: esta presa a
   **ABI das libs**. Com libs cp312, ela corre no 3.12 — que e o da producao.
   Consequencia pratica: a Big Collection desta madrugada **nao** perdia o texto
   do YouTube/Reels por causa disto *depois* desta correcao; antes dela, perdia.
2. **`fcntl` continua a derrubar 7 modulos** de `tests/` neste lane
   (`test_c10_audio_only`, `test_reel_transcricao`, `test_c10_4_route_gate`,
   `test_c10_4b_um_caminho_so`, `test_c10_5d_decisao_instagram`,
   `test_c10_6_crash_retry`, e `test_c10_4c_rota_aposentada` **sem** o
   `site-packages` emprestado no `PYTHONPATH`). O know-how §140 diz que isto foi
   fechado; neste lane, hoje, **nao esta**. `NAO SEI` se e atraso de branch ou
   regressao — nao foi medido. **Fora do escopo desta missao.**
3. **A correcao e da MAQUINA, nao do repo.** Numa maquina nova, ou em CI, a
   pasta nao existe e o sintoma volta. A proxima melhoria minima e de codigo:
   `fala_local._caminho_das_libs()` escolher a pasta pela `sys.version_info`
   (ex.: `~/.sintonia-libs-cp312` quando corre 3.12) e o erro dizer a ABI. **Nao
   aplicado** — mexe no dono do ASR e pede missao propria com testes.
4. `py -0p` **nao ve** o `site-packages` de `Python312`
   (`AppData\Local\Programs\Python\Python312` tem `Lib`/`DLLs`, **sem**
   `python.exe`). Medir «que python existe» por `py -0p` sozinho nao basta.

## 7 · KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = ATUALIZACAO NECESSARIA
```

O que ha a registar no `SINTONIA-EAME-KNOW-HOW.md` (dono: lane da BC4, §199
nesta madrugada — **nao editado por mim, estava a ser escrito ao vivo**):

- `~/.sintonia-libs` tem ABI: a pasta tem de casar com o interpretador que a
  usa (cp311 vs cp312). A ativa passa a ser **cp312**; a cp311 fica em `.bak-cp311`.
- Versoes ativas (§3).
- `INTERPRETER_PINNED = python3.11` -> **REFUTADO**; a regra certa e
  «as libs seguem o interpretador», nao «o interpretador segue as libs».
- O runner `LUCIANO-2` (`C:\actions-runner-2`) e de `portal-sintonia`: **NAO
  MEXER**.

## 8 · PROXIMO PASSO MINIMO

Decidir se `fala_local.py` passa a escolher a pasta de libs por versao do
interpretador (§6.3) — uma linha de politica, um teste, uma missao.

```
HARD STOP
```
