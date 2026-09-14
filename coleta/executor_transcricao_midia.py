#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PONTE ENTRE A COLLECTION E O RECONHECEDOR — e é só isso que ela é.

    import executor_transcricao_midia as ex
    ex.CAPACIDADE["ACEITA_MEDIA_TYPES"]
    ex.derivar_um(raw_asset_id, caminho, armazem, memoria, ...)

O QUE ESTE FICHEIRO **NÃO** É
-------------------------------
Não é um reconhecedor de fala. O dono de `FALA → TEXTO` nesta casa já existe e
continua a ser `ferramentas/fala_local.py`: ele escolhe o ferro, negoceia a
aritmética, aplica o detetor de voz, mede a língua e carimba o que correu.

    ONE CONCEPT → ONE OWNER. ESTE FICHEIRO NÃO ESCOLHE MODELO, NÃO ESCOLHE
    DISPOSITIVO, NÃO APLICA LIMIAR E NÃO ABRE `WhisperModel`.

E também não é um segundo dono da escrita. Ele entrega a RECEITA e os BYTES a
`guarda/preservar_derivado.preservar_derivado()`, exactamente como
`coleta/executor_texto_de_pdf.py` faz. Não calcula `parent_sha256`,
`parameters_hash`, `sha256` do filho, `derived_at` nem `storage_path` — esses
são do dono, e é isso que impede um executor de declarar uma linhagem que não
pode provar.

    O EXECUTOR PRODUZ O QUE SÓ ELE SABE. ESCREVER É DE QUEM É DONO DA ESCRITA.

POR QUE ELE EXISTE, MEDIDO
----------------------------
A C4G mediu que `coleta/ingresso._capacidades_de_derivacao()` conhecia UM
executor, importado pelo nome — e que o próprio ficheiro tinha previsto o
problema por escrito:

    «no dia em que entrasse um executor de áudio os dois divergiam em silêncio»

Sem esta peça, um `video/mp4` com a espécie declarada saía da porta como
`DERIVACAO_ESPECIE_NAO_SUPORTADA` — honesto, e final. O texto que a máquina
sabia produzir não tinha por onde entrar na Collection.

    VIDEO_OUTPUT_WRITTEN = YES  ·  VIDEO_OUTPUT_CONSUMED = NO

O ÁUDIO INTERMÉDIO É MATERIAL DE TRABALHO, E A AUTORIDADE É DE 2022
---------------------------------------------------------------------
Um vídeo precisa de virar áudio antes de virar texto. Esse áudio **não** é um
derivado desta casa, e isso não é escolha minha: `022_o_derivado_ganha_casa.sql`
declara uma lista FECHADA de espécies —

    TEXT_EXTRACTION · OCR · TRANSCRIPTION · TRANSLATION ·
    THUMBNAIL · FRAME · TABLE_EXTRACTION

— e não há espécie de áudio nela. E a mesma migration enuncia o grão com o caso
testado por extenso:

    audio -> transcricao              1 linha

UMA linha. Logo o pai da transcrição é a OBSERVAÇÃO (o vídeo), e o WAV pelo
caminho é o que o `pdftotext` também tem por dentro e nunca preservou: meio, e
não produto. Ele nasce numa pasta temporária e morre com a derivação.

    INVENTAR UMA TERCEIRA CATEGORIA EM SILÊNCIO SERIA ARQUITETURA NOVA
    ESCRITA POR DESCUIDO. A LISTA JÁ RESPONDE, E FECHADA.

O QUE ENTRA NA IDENTIDADE DO DERIVADO, E POR QUÊ
--------------------------------------------------
A chave única do derivado é
`(parent_sha256, kind, producer, producer_version, parameters_hash,
serie_posicao)`, e a 022 explica porquê com o caso real:

    «o modelo `base` e o `small` sobre o mesmo audio dao textos diferentes, e os
     dois sao legitimos. Sem a versao na identidade, a segunda passagem apagaria
     a primeira em silencio.»

Por isso `parameters` leva **modelo, dispositivo e tipo de cálculo**. E o
dispositivo entra por medição, não por simetria: a C4E mediu que o texto da
placa difere do texto do processador em 4 de 6 peças com fala — logo dois
dispositivos produzem dois artefatos legítimos, e colapsá-los apagaria um.

    MESMO ÁUDIO + OUTRO FERRO = OUTRO TEXTO = OUTRA LINHA.
    E retry no MESMO ferro = a mesma chave = REUSED, como deve ser.
"""
from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas                                            # noqa: E402,F401
import artefato as art                                     # noqa: E402

EXECUTOR_ID = "transcricao-midia"
EXECUTOR_VERSION = "1"
PIPELINE_VERSION = "1"

#: A espécie do derivado, na lista FECHADA da migration 022. Não se inventa
#: nem se alarga aqui: alargar é uma migration, com um caso real a justificar.
ESPECIE = "TRANSCRIPTION"

# ── OS MOTIVOS DE NÃO HAVER DERIVADO, E SÃO DOIS MUNDOS ─────────────────────
# `coleta/derivacao_forward.DESTINO_DO_MOTIVO` já separa os dois para o PDF:
#
#     TEXT_LAYER_ABSENT   REJECTED   o PDF é fotografia. Propriedade DELE.
#     EXTRACTION_ERROR    ERROR      a ferramenta falhou, ou não está cá.
#
# O áudio tem o mesmo par, e o nome do primeiro é onde se erra facilmente.
#
#     ⚠️ `SEM_TEXTO_RECONHECIDO` NÃO QUER DIZER «NÃO HAVIA FALA».
#
# `fala_local` é explícito e tem razão: «AUSÊNCIA DE TEXTO != AUSÊNCIA DE
# FALA». O reconhecedor não tem autoridade para afirmar o que havia no áudio —
# ele diz o que produziu. O motivo abaixo diz exactamente isso e mais nada, e é
# por isso que não se chama `SEM_FALA`.
SEM_TEXTO_RECONHECIDO = "SEM_TEXTO_RECONHECIDO"
ASR_INDISPONIVEL = "ASR_INDISPONIVEL"
ASR_FALHOU = "ASR_FALHOU"
AUDIO_NAO_OBTIDO = "AUDIO_NAO_OBTIDO"

#: O que cada motivo é, na língua de `derivacao_forward`. Registado aqui e lido
#: lá — um executor novo diz por que porta sai, e não deixa o `UNKNOWN` apanhá-lo.
DESTINO_DOS_MOTIVOS = {
    # Propriedade do ITEM: correu até ao fim e não saiu texto.
    SEM_TEXTO_RECONHECIDO: "REJECTED",
    # Factos sobre NÓS. A fonte não tem culpa nenhuma destes três.
    ASR_INDISPONIVEL: "ERROR",
    ASR_FALHOU: "ERROR",
    AUDIO_NAO_OBTIDO: "ERROR",
}

# ── O QUE ESTE EXECUTOR SABE ABRIR ──────────────────────────────────────────
# Declarado na MESMA língua que a porta lê (`raw_asset.media_type`), como o
# executor de PDF já faz. Não é uma segunda declaração da capacidade: é a
# mesma, legível dos dois lados.
#
# ⚠️ A LISTA É DO QUE SE PODE PROVAR, E NÃO DO QUE SERIA SIMPÁTICO ACEITAR.
# `ffmpeg` abre dezenas de contentores; o que esta casa mediu foram estes. Um
# tipo que não esteja aqui sai da porta como espécie não suportada — que é uma
# resposta honesta, e não uma recusa da fonte.
ACEITA = (
    "video/mp4", "video/quicktime", "video/webm", "video/x-matroska",
    "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp4", "audio/aac",
    "audio/ogg", "audio/opus", "audio/flac", "audio/webm",
)

CAPACIDADE = {
    "EXECUTOR_ID": EXECUTOR_ID,
    "VERSION": EXECUTOR_VERSION,
    "SUPPORTS": ["MEDIA_RAW"],
    "ACEITA_MEDIA_TYPES": ACEITA,
    "PRODUCES": [ESPECIE],
    "NETWORK_REQUIRED": "NO",
    "CHECKPOINT": art.NAO_SE_APLICA,
    "COST_CLASS": "LOCAL",
    "FERRAMENTA_EXTERNA": "ffmpeg (áudio) + faster-whisper via ferramentas/fala_local.py",
    # Quem manda no reconhecedor. Escrito para que uma varredura encontre o
    # dono a partir daqui, e não haja dúvida de que este ficheiro não é ele.
    "ASR_OWNER": "ferramentas/fala_local.py",
    "ESCRITA_DO_DERIVADO": "guarda/preservar_derivado.py",
}


def aceita(media_type) -> bool:
    """Esta espécie cabe aqui? → True/False. Sem adivinhar, e sem extensão.

    ⚠️ `None` É **NÃO**, E AQUI A REGRA É O CONTRÁRIO DA PORTA.

    `ingresso._quem_deriva_aceita` trata a ausência como «tenta», e tem razão:
    lá a pergunta é «algum executor saberá?», e fechar a porta à ausência
    encolheria a coleta em silêncio. Aqui a pergunta é outra — «EU sei abrir
    isto?» — e a um «não sei o que é» a resposta honesta é não.

        QUEM NÃO SABE O QUE RECEBEU NÃO PODE AFIRMAR QUE SABE ABRI-LO.
    """
    if media_type is None:
        return False
    t = str(media_type).split(";")[0].strip().lower()
    if not t or t.upper() in ("NAO SEI", "NAO_SEI", "NÃO SEI", art.NAO_SE_APLICA):
        return False
    return t in ACEITA


def _e_video(media_type) -> bool:
    return str(media_type or "").split("/")[0].strip().lower() == "video"


def derivar_um(raw_asset_id, caminho, armazem, memoria, relogio=None,
               contexto_da_passagem=None, media_type=None) -> dict:
    """Um áudio/vídeo, um pai canónico, uma transcrição — pelo dono da escrita.

    A assinatura é a do executor de PDF de propósito: quem chama é o mesmo
    runner, e um segundo formato de chamada seria um segundo contrato.
    `media_type` é o único acrescento, e ele vem da OBSERVAÇÃO — nunca do nome
    do ficheiro.

    `contexto_da_passagem` é um envelope OPACO que este executor não lê. Viaja
    daqui para o dono da escrita e nada mais.
    """
    from guarda.preservar_derivado import agora_utc, preservar_derivado
    sys.path.insert(0, os.path.join(RAIZ, "ferramentas"))
    import fala_local as fl                                 # noqa: PLC0415

    ha, porque = fl.disponivel()
    if not ha:
        return {"ESTADO": "SEM_DERIVADO", "MOTIVO_DO_EXECUTOR": ASR_INDISPONIVEL,
                "ERRO": porque,
                "NAO_SIGNIFICA": "que o áudio não tem fala. A ferramenta é que "
                                 "não está nesta máquina."}

    # ── O ÁUDIO, QUANDO O QUE VEIO FOI VÍDEO ────────────────────────────
    # Pasta temporária: o WAV é meio, não produto. Ver o cabeçalho e a 022.
    temporaria = None
    try:
        alvo = caminho
        if _e_video(media_type):
            temporaria = tempfile.mkdtemp(prefix="transcricao-midia-")
            wav = os.path.join(temporaria, "audio.wav")
            alvo, falhou = fl.extrair_audio(caminho, wav)
            if not alvo:
                return {"ESTADO": "SEM_DERIVADO",
                        "MOTIVO_DO_EXECUTOR": AUDIO_NAO_OBTIDO, "ERRO": falhou,
                        "NAO_SIGNIFICA": "que o vídeo não tem som. Não consegui "
                                         "separar o áudio dele."}

        duracao = fl.duracao(alvo)
        r = fl.transcrever(alvo, idioma=None, duracao_s=(
            duracao if isinstance(duracao, (int, float)) else None))
    finally:
        if temporaria:
            import shutil                                   # noqa: PLC0415
            shutil.rmtree(temporaria, ignore_errors=True)

    estado = r.get("TRANSCRIPT_STATE")
    if estado in (fl.ASR_INDISPONIVEL,):
        return {"ESTADO": "SEM_DERIVADO", "MOTIVO_DO_EXECUTOR": ASR_INDISPONIVEL,
                "ERRO": r.get("ERROR"), "MEDIDAS": _medidas(r)}
    if estado in (fl.ASR_FALHOU, fl.TRANSCRIPTION_TIMEOUT):
        # ⚠️ NENHUM DOS DOIS É `REJECTED`. O reconhecedor caiu, ou passou do
        # tecto e o texto pode estar em laço — os dois são factos sobre NÓS.
        # Chamar-lhes recusa poria a culpa na fonte, e a fonte não fez nada.
        #
        #     ERROR != REJECTED. O SISTEMA FALHOU / O ITEM NÃO SERVIA.
        return {"ESTADO": "SEM_DERIVADO", "MOTIVO_DO_EXECUTOR": ASR_FALHOU,
                "ERRO": r.get("ERROR") or r.get("WHY"), "MEDIDAS": _medidas(r),
                "NAO_SIGNIFICA": r.get("NAO_SIGNIFICA") or ""}

    texto = r.get("TRANSCRIPT") or ""
    if not texto.strip():
        # Correu até ao fim e não saiu texto. Propriedade do que se ouviu —
        # e NÃO a afirmação «não havia fala», que esta gaveta não pode fazer.
        return {"ESTADO": "SEM_DERIVADO",
                "MOTIVO_DO_EXECUTOR": SEM_TEXTO_RECONHECIDO,
                "ERRO": "", "MEDIDAS": _medidas(r),
                "NAO_SIGNIFICA": r.get("NAO_SIGNIFICA")
                or "que o áudio não tem fala. Significa que não saiu texto."}

    # ── A RECEITA PARA O DONO DA ESCRITA ────────────────────────────────
    # `parameters` leva o que MUDA O TEXTO, e é por isso que ele entra na
    # chave única através do `parameters_hash`. Ver o cabeçalho.
    fora = preservar_derivado(
        {**(contexto_da_passagem or {}),
         "raw_asset_id": raw_asset_id,
         "kind": ESPECIE,
         "producer": EXECUTOR_ID,
         "producer_version": EXECUTOR_VERSION,
         "pipeline_version": PIPELINE_VERSION,
         "parameters": {
             "ASR_ENGINE": r.get("ASR_ENGINE"),
             "ASR_ENGINE_VERSION": r.get("ASR_ENGINE_VERSION"),
             "ASR_MODEL": r.get("ASR_MODEL"),
             "ASR_DEVICE_USED": r.get("ASR_DEVICE_USED"),
             "ASR_COMPUTE_SELECTED": r.get("ASR_COMPUTE_SELECTED"),
             "ASR_BEAM": r.get("ASR_BEAM"),
             "TRANSCRIBER_VERSION": r.get("TRANSCRIBER_VERSION"),
         },
         "serie_posicao": None,
         "media_type": "text/plain"},
        texto.encode("utf-8"), armazem, memoria,
        relogio=relogio or agora_utc)
    # ── E A ESPÉCIE DO TEXTO VIAJA AQUI, E NÃO NA LINHA DO DERIVADO ─────
    # ⚠️ EU IA ESCREVÊ-LA NO `derived_artifact`, E ESTAVA A INVENTAR COLUNAS.
    #
    # Medido antes de a escrever: a 022 declara catorze colunas e nenhuma se
    # chama `text_kind`, `text_relation` ou `language`. E o dono da escrita é
    # explícito sobre o que aceita — «`raw_asset_id`, `kind`, `producer`,
    # `producer_version`, `parameters`, `serie_posicao`, `media_type`, e os
    # bytes do filho. **Nada mais.**»
    #
    # O contrato E7 também já tinha respondido: a representação canónica do
    # texto é `TEXT_UNITS`, e ela vive na UNIDADE que atravessa a Collection —
    # não na linha do ficheiro derivado.
    #
    #     ANTES DE INVENTAR VOCABULÁRIO, PROCURAR O DONO NO GIT INTEIRO.
    #     E UMA COLUNA QUE NÃO EXISTE NÃO SE CRIA A PARTIR DE UM EXECUTOR.
    #
    # Então isto sobe no RESULTADO, para quem monta a unidade usar — e o
    # derivado guarda o que o derivado guarda: bytes, espécie e régua.
    fora["TEXT_UNIT"] = {
        # Fala reconhecida por NÓS. `CAPTION` é texto que o autor escreveu, e
        # nunca passa por aqui — somar os dois apaga qual deles sustentou uma
        # classificação, que é a primeira pergunta que a inteligência faz.
        "TEXT_KIND": "TRANSCRIPT",
        # Fala na língua em que foi dita. Tradução, se um dia existir, é outra
        # unidade que APONTA para esta — nunca uma substituição dela.
        "TEXT_RELATION": "ORIGINAL",
        # A língua vem da EVIDÊNCIA do reconhecedor. Não do país da conta, não
        # do `SOURCE_LOCATION`, não do domínio do endereço.
        "LANGUAGE": r.get("LANGUAGE"),
        "LANGUAGE_SOURCE": r.get("LANGUAGE_SOURCE"),
        "LANGUAGE_CONFIDENCE": r.get("LANGUAGE_CONFIDENCE"),
        "TEXT_CHARS": len(texto),
        "DERIVATION_METHOD": "%s/%s" % (EXECUTOR_ID, EXECUTOR_VERSION),
    }
    fora["MEDIDAS"] = _medidas(r)
    return fora


def _medidas(r) -> dict:
    """O que se mediu, mesmo quando não houve derivado. Um fracasso sem
    medidas não se distingue de um fracasso de outra causa."""
    return {k: r.get(k) for k in (
        "TRANSCRIPT_STATE", "ASR_MODEL", "ASR_DEVICE_USED", "ASR_DEVICE",
        "ASR_DEVICE_EXECUTION", "ASR_COMPUTE_SELECTED", "AUDIO_SECONDS",
        "MACHINE_SECONDS", "REALTIME_FACTOR", "LANGUAGE", "LANGUAGE_SOURCE",
        "LANGUAGE_CONFIDENCE", "VOICED_SEGMENTS", "NO_SPEECH_PROB_MEAN")}
