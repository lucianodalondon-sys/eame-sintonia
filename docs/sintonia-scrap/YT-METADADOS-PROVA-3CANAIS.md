# YT-METADADOS · A PROVA COM 3 CANAIS, E AS DUAS OPÇÕES DA FASE

**QUANDO:** 2026-09-25 · **RAMO:** `yt-metadados-v1` · **BASE DESCARTÁVEL**, 31 migrações,
`127.0.0.1:58165`. **Egresso IT `PASS`** antes e depois de cada canal. **Custo US$ 0.**

---

## 1 · O VEREDICTO DA RÉGUA, LINHA A LINHA

Corrida real dos 3 canais pela **porta canónica** (orquestrador → scrap-colheita), com o
código do bloco A/B já dentro:

```
IT-T9-029:audio-youtube  rc 0  RAW 1  DERIVED 0  SALA 0
IT-T5-165:audio-youtube  rc 0  RAW 1  DERIVED 0  SALA 0
IT-T3-025:audio-youtube  rc 0  RAW 1  DERIVED 0  SALA 0
```

A régua (`curadoria/regua_social.py`, dona do veredicto):

```
IT-T9-029 | fase do contrato: canal-youtube | fase da corrida: audio-youtube
   VEREDITO: FALHA
   PORQUE  : o envelope e da fase 'audio-youtube', e o contrato pede canal-youtube
```

**Os três, iguais. `{'FALHA': 3}`.**

> **A RÉGUA PARA NO PRIMEIRO CRITÉRIO — O NOME DA FASE.** Ela não chega a olhar para os
> quatro campos do item (`NATIVE_ID`, `PUBLISHED_AT`, `OWNER_AUTHORIZED`,
> `PLATFORM_POLICY_STATUS`) nem para o autor da página. Por isso **o efeito do bloco A
> sobre o READY ainda não é medível**: ele está a montante de um portão que ainda fecha.

### O que a corrida provou na mesma
1. A aquisição corre e **grava** (`RAW 1` em cada) — com o egresso IT nas duas pontas.
2. `DERIVED 0` e `SALA 0` são esperados: esta fase **adquire som**; transcrever e admitir
   são fases e portas de outros donos.

---

## 2 · O BLOQUEIO QUE VEM ANTES DO PORTÃO, E QUE EU TIVE DE CONTORNAR NA CÓPIA

Antes de a régua poder julgar, o Scrap recusa ancorar um `SOURCE_ID` que o Atlas não
conhece (`leis/fonte_do_atlas.conhece`). Medido na minha árvore:

```
conhece IT-T9-029 -> False · IT-T5-165 -> False · IT-T3-025 -> False
colheita encontrada: 0 item(ns)   (nos TRÊS, com rc 0 e egresso IT)
```

**Onde os 3 números existem, e onde não** (contagem de ocorrências por ficheiro):

| ficheiro | IT-T9-029 |
|---|---|
| `curadoria/SOC-ONDA2-CANARIO-YOUTUBE-V1.json` (o relatório do canário) | **2** |
| `curadoria/italy_contracts_curator.json` (o livro do Curador) | 0 |
| `curadoria/SOURCE-ID-ALLOCATION-V1.json` (o registo de alocação) | 0 |
| `docs/fontes/ATLAS-DE-FONTES-EAME.md` (o Atlas) | 0 |

```
OS 11 NÚMEROS DO YOUTUBE EXISTEM HOJE SÓ DENTRO DO RELATÓRIO QUE OS CUNHOU.
```

Por isso a prova correu numa cópia onde eles **estão** materializados (a base preparada da
SOC-ONDA2, com o meu código transplantado — 3 ficheiros, declarado aqui). **Escrever a
ficha no vivo é passo do coordenador** (o próprio `curadoria/atlas_social.py` o diz), e
não foi feito em lado nenhum fora de cópia.

---

## 3 · ONDE NASCE CADA NOME

| nome | quem o escreve | onde |
|---|---|---|
| **`canal-youtube`** (o que a régua EXIGE) | o **CONTRATO** da fonte | `curadoria/italy_contracts_curator.json` → `FONTES[IT-T9-029].ACQUISITION` = `{STRATEGY: SCRAP_FASE, EXECUTOR: scrap-colheita, FASE: canal-youtube, PLATFORM: YOUTUBE, CAPACIDADE: youtube.channel.discovery, CHANNEL_ID: UC4A5…, FILTROS: …}` |
| | a **régua**, que o lê e o usa como critério | `curadoria/regua_social.py:138` (`fase_do_contrato`) → comparado em `:105` |
| | a **tabela de fases** do Scrap | `coleta/scrap_colheita.py:222` (`'canal-youtube': ('YOUTUBE','youtube.channel.discovery',{'limit':25},COLHEITA)`) · filtro em `:377` (`{'canal_id':'channel_id'}`) |
| **`audio-youtube`** (o que foi CORRIDO) | a **tabela de fases** do Scrap | `coleta/scrap_colheita.py:248` (`'audio-youtube': ('YOUTUBE','youtube.public_audio',{},COLHEITA)`) |
| | quem **escolhe** correr esta fase | o harness do canário (`--fase=audio-youtube`) — e o contrato **não** a nomeia |

**Que fontes isto afeta:** todas as que têm `ACQUISITION.STRATEGY = SCRAP_FASE` com
`CAPACIDADE = youtube.channel.discovery` — os **11 canais novos** desta onda. Não afeta as
fontes cujo contrato já pede a fase que corre (as do LinkedIn, por exemplo).

---

## 4 · AS DUAS OPÇÕES MÍNIMAS (nenhuma aplicada)

### (a) O contrato aceitar o envelope `audio-youtube` quando o canal está provado

**O que muda:** o critério da fase deixa de ser um nome único e passa a ser uma lista
admissível — o contrato declara as fases que o satisfazem quando a capacidade do canal já
está provada (`CAPACIDADE = youtube.channel.discovery` provada pelo bloco B), e a régua
aceita qualquer uma delas.

**Quem toca:** o **livro** (`curadoria/italy_contracts_curator.json`, do Curador) + a
**régua** (`curadoria/regua_social.py:138`, que passa a ler uma lista em vez de um nome).

**O que isso destrava:** o item que a régua julga passa a ser o da **aquisição** — que é o
único que traz `PUBLISHED_AT`, canal e carimbo. A lista do canal deixa de ser confundida
com a observação do vídeo.

**O que fica por resolver na mesma:** a ficha no Atlas (o bloqueio do §2) — sem número no
Atlas, a corrida sai com `COLHEITA 0` antes de chegar à régua.

### (b) O coletor de áudio emitir o envelope `canal-youtube`

**O que muda:** a fase `audio-youtube` — ou o envelope que ela produz — passa a
identificar-se como `canal-youtube`.

**Quem toca:** o **Scrap** (`coleta/scrap_colheita.py`, tabela de fases, e o envelope).

**O que isso custa:** **o nome deixa de dizer o que aconteceu.** `canal-youtube` é
*listar um canal*; `audio-youtube` é *adquirir o som de um vídeo*. Pôr o segundo nome no
primeiro envelope colapsa duas perguntas num só campo — e é exactamente o que esta casa já
proíbe no mesmo ficheiro: *«UMA LISTA DE CONTAS NAO E UMA OBSERVACAO DELAS»*
(`coleta/scrap_colheita.py:170`). E a régua passa a aceitar como «observação do canal» um
item que é som de um vídeo, sem que nada o distinga.

> **A (a) faz o critério acompanhar o que a máquina realmente faz.**
> **A (b) faz o nome acompanhar o que o critério quer ouvir.**

---

## 5 · O QUE NÃO FOI FEITO, E POR QUEM

```
ATLAS/REGISTO/LIVRO ....... escrever as 11 fichas no vivo — passo do coordenador
FASE ...................... decidir entre (a) e (b) — o coordenador leva ao bot Luciano
DERIVED/SALA .............. outras fases e outras portas, com outros donos
```
