# A UNIÃO SEMÂNTICA DA PONTE DE MÍDIA C4H — V1

> ⚠️ **C4H UNIFICADA NÃO SIGNIFICA COLLECTION + SALA CANÔNICA.**
> Este documento decide **uma peça**. A linha `claude/collection-sala-unified-v1`
> continua a ser uma **candidata**, e o System Map continua deliberadamente
> **não reconciliado** — isso é a Fase 5.

**Base:** `e73cc8ff0669e6c060432e15b02c313793e5a48f` (`claude/big-collection-gate-01`)
**Fonte de capacidades:** `06bd0efe` (`claude/local-gpu-on-current-collection-v1`)
**Data:** 2026-09-14

---

## 1 · DUAS PONTES NASCERAM NO MESMO DIA, COM SETE MINUTOS DE DIFERENÇA

As duas linhas separaram-se em `867a6f97` (16:31) e construíram a mesma coisa
sem saber uma da outra:

| | BIG | GPU |
|---|---|---|
| `coleta/executor_transcricao_midia.py` criado | **17:19:13** | 17:26:11 |
| commits C4H depois do corte | **6** (até 18:50) | 2 (até 18:12) |
| linhas do executor | 401 | 436 |

Sete dos sete ficheiros disputados foram tocados pelos **dois** lados depois do
corte. Um `cherry-pick` da GPU teria apagado o `ingresso.py` de 18:50 e o
`derivacao_forward.py` de 18:21 da BIG.

## 2 · NENHUMA ERA SUPERCONJUNTO DA OUTRA

Medido por API (`ast`), não por diferença de texto.

**Só a BIG tinha:**

- `ha_ferramenta()` → `shutil.which("ffmpeg")`, e **recusa antes de tentar**:
  `if not ha or not ha_ferramenta():`. A GPU só verificava o reconhecedor —
  numa máquina com ASR e sem `ffmpeg`, falharia tarde.
- `FFMPEG_PRESENTE` no olhar seco.
- `transcrever_ficheiro()` como função separada e reutilizável.
- A assinatura `derivar_um(raw_asset_id, midia, …)`, que `ingresso.py` e
  `derivacao_forward.py` já usam.

**Só a GPU tinha:**

- `pv.unidade_de_texto(...)` — o **construtor** do dono da proveniência.
- `pv.conferir_unidade_de_texto(u)` — o **validador** do dono.
- O estado `UNIDADE_RECUSADA`.
- Quatro medidas que `ferramentas/fala_local.py` já produzia e o executor da
  BIG deitava fora: `ASR_COMPUTE_SELECTED`, `REALTIME_FACTOR`,
  `VOICED_SEGMENTS`, `NO_SPEECH_PROB_MEAN`.

A própria GPU registou, no código, que houve uma arbitragem `C4H-ARB` e que
**nenhuma das duas** implementações chamava o construtor do dono:

> *"Os valores que eu escrevia à mão estavam CERTOS hoje. O defeito não era o
> valor: era haver dois sítios a decidi-lo. UM VALOR CERTO ESCRITO NO SÍTIO
> ERRADO É UM VALOR QUE VAI DERIVAR."*

## 3 · O QUE FOI PRESERVADO E O QUE FOI PORTADO

| capacidade | BIG | GPU | unificada |
|---|:--:|:--:|:--:|
| portão do `ffmpeg` | ✅ | ✗ | ✅ preservado |
| recusa antecipada sem ferramenta | ✅ | ✗ | ✅ preservado |
| `FFMPEG_PRESENTE` | ✅ | ✗ | ✅ preservado |
| `transcrever_ficheiro()` | ✅ | ✗ | ✅ preservado |
| `derivar_um(…, midia, …)` | ✅ | ✗ | ✅ preservado |
| `tem_fala_possivel` | ✅ | ✗ | ✅ preservado |
| construtor do dono | ✗ | ✅ | ✅ **portado** |
| validador do dono | ✗ | ✅ | ✅ **portado** |
| `UNIDADE_RECUSADA` | ✗ | ✅ | ✅ **portado** |
| `pv.ASR_DA_CASA` (lista fechada) | ✗ | ✅ | ✅ **portado** |
| as 4 medidas | ✗ | ✅ | ✅ **portado** |
| `TEXT_UNIT` no recibo | ✗ | ✅ | ✅ **portado** |

A construção da unidade vem **antes** de `preservar_derivado`, de propósito: o
validador serve para apanhar a unidade inválida enquanto ainda não se escreveu
byte nenhum no armazém.

## 4 · POR QUE A PROVA DA GPU ESTAVA ACOPLADA À IMPLEMENTAÇÃO

Importada tal e qual, reprovou **25 de 37** casos. Nenhum por a ponte estar
errada:

- procurava `em.tem_faixa_de_som`; aqui a função é `tem_fala_possivel` — mesma
  lógica, ramo a ramo;
- exigia a string `pv.TRANSCRIPT` **dentro** de `derivar_um`; aqui o símbolo é
  `TEXT_KIND`, que **é** `pv.TRANSCRIPT`, lido do dono no topo;
- fazia `assertNotIn("SOURCE_ID", fonte)` e apanhava a **docstring** que
  promete, por escrito, que o executor não cria `SOURCE_ID`;
- exigia nomes internos da GPU: `ESPECIE`, `DESTINO_DOS_MOTIVOS`,
  `ASR_FALHOU`, `SEM_FAIXA_DE_SOM`, `SEM_TEXTO_RECONHECIDO`, `_medidas`,
  `_e_video`.

> **UM TESTE ACOPLADO AO NOME INTERNO MEDE A FORMA, NÃO O CONTRATO.**
> **E DUAS FORMAS PODEM CUMPRIR O MESMO CONTRATO.**

## 5 · MATRIZ DE TRADUÇÃO — OS 37 CASOS ORIGINAIS

Nenhum desapareceu sem destino declarado.

| # | teste original da GPU | tipo | destino |
|---|---|---|---|
| 1 | `test_T1_video_mp4_escolhe_o_executor_de_midia` | BEHAVIOR | COBERTO_POR_OUTRO_TESTE |
| 2 | `test_T2_audio_escolhe_o_executor_de_midia` | BEHAVIOR | COBERTO_POR_OUTRO_TESTE |
| 3 | `test_T3_pdf_continua_a_escolher_o_executor_de_pdf` | BEHAVIOR | COBERTO_POR_OUTRO_TESTE |
| 4 | `test_T4_o_declarado_vence_a_extensao` | BEHAVIOR | COBERTO_POR_OUTRO_TESTE |
| 5 | `test_T5_ficheiro_chamado_pdf_com_especie_de_video…` | SAFETY | COBERTO_POR_OUTRO_TESTE |
| 6 | `test_nenhum_executor_recebe_o_que_declarou_nao_aceitar` | CONTRACT | COBERTO_POR_OUTRO_TESTE |
| 7 | `test_a_porta_conhece_mais_do_que_um` | CONTRACT | COBERTO_POR_OUTRO_TESTE |
| 8 | `test_T6_o_produto_e_TRANSCRIPT…` | CONTRACT | COBERTO + REESCRITO¹ |
| 9 | `test_T7_caption_nunca_e_rebatizada_transcript` | CONTRACT | COBERTO_POR_OUTRO_TESTE |
| 10 | `test_T8_a_lingua_vem_da_evidencia_e_nao_do_pais` | PROVENANCE | COBERTO_POR_OUTRO_TESTE |
| 11 | `test_a_traducao_nao_substitui_o_original` | PROVENANCE | COBERTO + REESCRITO¹ |
| 12 | `test_T9_source_id_desconhecido_continua_desconhecido` | SAFETY | **REESCRITO_EQUIVALENTE** |
| 13 | `test_T10_o_executor_nao_inventa_raw_asset_id` | SAFETY | COBERTO_POR_OUTRO_TESTE |
| 14 | `test_T11_o_executor_nao_escreve_no_banco` | SAFETY | MANTIDO |
| 15 | `test_o_executor_nao_duplica_o_reconhecedor` | CONTRACT | MANTIDO |
| 16 | `test_o_executor_nao_julga_relevancia_nem_tempo_do_facto` | SAFETY | COBERTO_POR_OUTRO_TESTE |
| 17 | `test_T12_falha_de_ASR_e_ERROR_e_nunca_REJECTED` | BEHAVIOR | COBERTO_POR_OUTRO_TESTE |
| 18 | `test_T13_audio_sem_texto_nao_vira_ausencia_de_fala` | BEHAVIOR | COBERTO_POR_OUTRO_TESTE |
| 19 | `test_todo_motivo_declarado_tem_destino` | CONTRACT | COBERTO_POR_OUTRO_TESTE |
| 20 | `test_T15_o_que_muda_o_TEXTO_entra_na_identidade` | CONTRACT | **REESCRITO_EQUIVALENTE**² |
| 21 | `test_T16_o_sha_nao_e_usado_como_identidade` | SAFETY | **REESCRITO_EQUIVALENTE** |
| 22 | `test_T14_o_dono_da_escrita_e_que_decide_reuso` | CONTRACT | COBERTO_POR_OUTRO_TESTE |
| 23 | `test_a_lista_fechada_de_especies_nao_tem_audio` | CONTRACT | MANTIDO |
| 24 | `test_o_wav_nasce_e_morre_numa_pasta_temporaria` | SAFETY | **REESCRITO_EQUIVALENTE**³ |
| 25 | `test_um_tom_sem_fala_sai_SEM_TEXTO_RECONHECIDO` | BEHAVIOR | **REESCRITO_EQUIVALENTE**⁴ |
| 26 | `test_nenhum_ficheiro_de_youtube_entrou_nesta_missao` | OBSOLETE_PROVEN | REMOVER_OBSOLETO_PROVADO⁵ |
| 27 | `test_o_executor_de_midia_nao_conhece_youtube` | SAFETY | COBERTO_POR_OUTRO_TESTE |
| 28 | `test_o_dono_do_ASR_nao_foi_alterado_por_esta_missao` | SAFETY | MANTIDO |
| 29 | `test_o_vocabulario_vem_do_DONO_e_nao_de_literais` | PROVENANCE | **REESCRITO_EQUIVALENTE** |
| 30 | `test_o_dono_confere_a_unidade_antes_de_ela_sair` | PROVENANCE | MANTIDO |
| 31 | `test_a_unidade_que_este_executor_monta_passa_no_dono` | PROVENANCE | MANTIDO |
| 32 | `test_o_metodo_de_derivacao_esta_na_lista_fechada` | CONTRACT | MANTIDO |
| 33 | `test_o_kind_continua_na_lista_fechada_da_022` | CONTRACT | MANTIDO |
| 34 | `test_ficheiro_sem_faixa_de_som_e_facto_do_ORIGINAL` | BEHAVIOR | **REESCRITO_EQUIVALENTE** |
| 35 | `test_a_pergunta_dos_fluxos_vai_ao_DONO_da_midia` | CONTRACT | MANTIDO |
| 36 | `test_nao_medir_nao_autoriza_concluir_que_nao_ha_som` | BEHAVIOR | **REESCRITO_EQUIVALENTE** |
| 37 | `test_familias_NAO_foram_portadas` | IMPLEMENTATION_COUPLING | **BLOQUEADO** — ver §6 |

```
MANTIDOS                   9
REESCRITOS_EQUIVALENTES    9
COBERTOS_POR_OUTRO_TESTE  17
OBSOLETOS_PROVADOS         1
BLOQUEADOS                 1
                          ──
                          37
```

¹ o invariante está coberto por `test_c4h_ponte_de_midia.py` **e** reforçado
aqui sobre a unidade real, não sobre a constante do módulo.
² deixou de procurar `ASR_ENGINE_VERSION` num bloco de texto e passou a medir a
receita que sai: medida da máquina **fora**, o que muda o texto **dentro**.
³ a limpeza da BIG é `os.remove` + `os.rmdir` num `finally`, não `shutil.rmtree`
— o invariante (o WAV nasce e morre numa pasta temporária, e nunca vira
derivado) é o mesmo.
⁴ o original exigia `ffmpeg` **e** o modelo instalados, e fazia `skipTest` sem
eles. Aqui a mesma distinção (`a ferramenta correu e não havia texto` ≠ `erro`)
é medida com o dono do ASR em dublê, sem serviço externo.
⁵ era uma prova sobre o **escopo da missão da GPU**, não sobre a ponte. A
missão terminou; o invariante que interessa (a ponte não conhece plataforma)
está no #27.

## 6 · ⚠️ A EXIGÊNCIA QUE NÃO ENTROU, E NÃO FOI APAGADA

`test_familias_NAO_foram_portadas` exigia que a ficha declarasse uma **lista
exacta** de `media_type` e que `FAMILIAS` não existisse. A GPU argumentava:
`audio/*` aceitaria `audio/x-inventado`.

A BIG declara-se por **família**, com a razão escrita no executor:

> *"UMA LISTA QUE PRECISA DE SER COMPLETA PARA ESTAR CERTA ESTÁ ERRADA NO DIA
> SEGUINTE."*

**As duas posições são defensáveis e contradizem-se.** A base desta união é a
BIG, logo a família fica. O preço está guardado na classe `OQueFicouBloqueado`
de `tests/test_c4h_executor_de_midia.py`, que **prova que a objecção da GPU é
real** (`aceita("audio/x-inventado")` é `True`) e prova também o que a mitiga:
quem estreita de verdade é a **medição** do `ffprobe`, não a ficha. Se um dia a
ficha estreitar, esse teste falha e obriga a reescrever a decisão — em vez de a
deixar esquecida.

## 7 · A PROVA NOVA DETECTA AS REGRESSÕES QUE MOTIVARAM A UNIÃO

Mutação aplicada a uma cópia descartável **fora** dos worktrees:

| mutação | resultado |
|---|---|
| validador do dono desligado | **FAILED** (2 falhas, 1 erro) |
| recusa da unidade ignorada | **FAILED** (2 falhas, 1 erro) |
| um dos 4 campos de medida removido | **FAILED** (2 falhas, 2 erros) |
| «não medido» convertido em zero | **FAILED** (4 falhas) |
| portão do `ffmpeg` removido | **FAILED** (1 falha) |
| `TEXT_UNIT` retirado do recibo | **FAILED** (1 falha, 2 erros) |
| controlo, sem mutação | **OK** |

## 8 · `architecture.declared.json` — OS 4 IDs

| ID | o que a união fez |
|---|---|
| `C-IT-CONTRATOS` | **nada** — a BASE já contém todos os `files` da GPU, e mais `regras/contratos_de_fonte.py` |
| `C-PROVA-COLETA` | **nada** — a BASE já é superconjunto (+`provas/a_collection_preserva_o_fato.py`) |
| `C-PROVA-ROTAS-REAIS` | **nada** — a BASE tem 8 ficheiros contra 4, e diz «Cinco medições» onde a GPU dizia «Quatro». Não se regride para menos. |
| `C-EXECUTOR-TRANSCRICAO-MIDIA` | **`what` e `why_here` unidos** — os factos dos dois lados, sem perder nenhum |

Nenhum ID duplicado: 163 entradas, 163 identidades únicas, antes e depois.
Edição cirúrgica de **2 linhas** — a reserialização do JSON inteiro foi
desfeita porque produzia 4.145 linhas de diff fantasma.

## 9 · TESTES

| suíte | BASE | UNIFICADA | |
|---|---|---|---|
| `test_c4h_executor_de_midia` (reescrito) | n/a | **29 OK** | novo |
| `test_c4h_ponte_de_midia` | OK | **OK** | sem regressão |
| `test_c4g_a_especie_do_video` | OK | **OK** | sem regressão |
| `test_proveniencia` | FAILED (5) | FAILED (5) | **herdado** |

As 5 falhas de `test_proveniencia` reproduzem-se de forma idêntica na BASE e
**não** foram introduzidas por esta união.

Nada foi executado contra serviço externo: sem ASR pago, sem Supabase, sem
Vercel, sem coleta. A migration **não** foi executada.
