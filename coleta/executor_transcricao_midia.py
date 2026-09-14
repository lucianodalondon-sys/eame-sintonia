#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O EXECUTOR DE TRANSCRIÇÃO DE MÍDIA — fala vira texto, e nada mais.

    py coleta/executor_transcricao_midia.py --ficha      # a ficha de capacidade
    py coleta/executor_transcricao_midia.py --seco FICH  # olha e conta, sem escrever

ELE É O IRMÃO DE `executor_texto_de_pdf`, E TEM O MESMO CONTRATO
-----------------------------------------------------------------
    application/pdf   ->  executor_texto_de_pdf      ->  TEXT_EXTRACTED
    audio/*  video/*  ->  ESTE FICHEIRO             ->  TRANSCRIPT

A porta da derivação não conhece nenhum dos dois pelo nome: ela lê a
`CAPACIDADE` que cada um declara. Foi por isso que este ficheiro coube sem se
mexer na regra dela.

    ONE CONCEPT -> ONE OWNER. QUEM SABE ABRIR É QUEM DIZ O QUE ABRE.

⚠️ ELE NÃO SABE DE ONDE A MÍDIA VEIO, E ISSO É A FUNCIONALIDADE
----------------------------------------------------------------
YouTube, Instagram, site oficial, carregamento à mão ou ficheiro local podem um
dia entregar bytes a esta mesma ponte. Ela recebe **um caminho e um pai
canónico**, e mais nada. Não há uma linha aqui sobre plataforma, conta, URL ou
política de aquisição — e não pode passar a haver:

    UMA PONTE QUE SABE DE ONDE O BYTE VEIO É UMA PONTE POR PLATAFORMA,
    E AÍ SÃO CINCO PONTES QUE DIVERGEM EM SILÊNCIO.

O QUE ELE NÃO FAZ, E CADA «NÃO» TEM DONO
-----------------------------------------
    não implementa ASR          `ferramentas/fala_local.py` é o dono único
    não escolhe GPU/CPU         idem — quem decide dispositivo é o dono do ASR
    não escreve no banco        `guarda/preservar_derivado.py` é o dono
    não inventa RAW_ASSET_ID    recebe-o como contexto da unidade de trabalho
    não cria SOURCE_ID          não é dele, e não é derivável de caminho
    não sai à rede              `NETWORK_REQUIRED = NO`, e é verdade
    não julga relevância        a peneira é a Admissão
    não decide READY nem Sala   a rota forward é que leva lá

A LÍNGUA NÃO SE ADIVINHA POR PAÍS, POR CONTA NEM POR CAMINHO
-------------------------------------------------------------
Este executor passa `idioma=None` ao dono do ASR quando o chamador não declarou
— e aí o campo sai `LANGUAGE_SOURCE = DETECTED`, com a confiança ao lado. A
tentação é olhar para `source_country` do pai e escrever `it`.

    UM VÍDEO ITALIANO PODE TER UM CONVIDADO A FALAR INGLÊS.
    PAÍS É DE ONDE A FONTE É; LÍNGUA É O QUE SE OUVE. `COL-LAW-040`.

⚠️ E O ERRO DO RECONHECEDOR NÃO É RECUSA DO CONTEÚDO
-----------------------------------------------------
`ASR_INDISPONIVEL` quer dizer que a ferramenta não está nesta máquina.
`REQUESTED_EMPTY` quer dizer que o áudio não tinha fala reconhecível. Nenhum dos
dois é «este vídeo não serve»: essa frase é da Admissão, e ela nem foi chamada.

    ASR_FAILED != CONTENT_REJECTED != CONTENT_ABSENT.

Por isso a saída sem derivado carrega o estado do dono do ASR por extenso, e
não um `False`.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import artefato as art  # noqa: E402
import proveniencia as pv  # noqa: E402 — o dono da espécie do texto

sys.path.insert(0, str(RAIZ / "ferramentas"))
import fala_local as fl  # noqa: E402 — o dono único de FALA -> TEXTO

# ── A FICHA DE CAPACIDADE ───────────────────────────────────────────────────
# Mesma doutrina do executor de PDF: dizer ANTES de correr o que se sabe fazer.
EXECUTOR_ID = "transcricao-de-midia"
EXECUTOR_VERSION = "1"
PIPELINE_VERSION = "1"

#: As famílias de `media_type` que esta ponte abre.
#:
#: ⚠️ POR QUE FAMÍLIA, E NÃO LISTA DE TIPOS EXACTOS.
#: O executor de PDF declara `("application/pdf",)` e isso chega-lhe: é um tipo
#: só. Mídia não é: `video/mp4` · `video/quicktime` · `video/webm` ·
#: `audio/mpeg` · `audio/mp4` · `audio/wav` · `audio/ogg` · `audio/x-m4a`, e a
#: lista nunca fecha. Escrever uma lista exacta aqui garantia que, no dia em que
#: chegasse um `audio/flac`, esta casa responderia `NÃO SUPORTADO` a uma coisa
#: que o `ffmpeg` abre há vinte anos.
#:
#:     UMA LISTA QUE PRECISA DE SER COMPLETA PARA ESTAR CERTA
#:     ESTÁ ERRADA NO DIA SEGUINTE.
#:
#: E a família não é um curinga preguiçoso: `ffmpeg` abre o contentor e
#: `ffprobe` diz se há faixa de áudio lá dentro. Quem responde de verdade é a
#: medição em `tem_fala_possivel()`, não esta declaração. A declaração só
#: decide A QUEM PERGUNTAR.
FAMILIAS = ("audio", "video")

CAPACIDADE = {
    "EXECUTOR_ID": EXECUTOR_ID,
    "VERSION": EXECUTOR_VERSION,
    "SUPPORTS": ["AUDIO_RAW", "VIDEO_RAW"],
    # Nenhum tipo exacto: esta ponte declara-se por FAMÍLIA. O campo existe e
    # fica vazio de propósito, para que a porta não tenha de saber que este
    # executor é diferente — ela lê os dois campos em todos.
    "ACEITA_MEDIA_TYPES": (),
    "ACEITA_FAMILIAS": FAMILIAS,
    "PRODUCES": ["TRANSCRIPT"],
    "NETWORK_REQUIRED": "NO",
    "OCR": "NO",
    "CHECKPOINT": art.NAO_SE_APLICA,
    "COST_CLASS": "LOCAL",
    "FERRAMENTA_EXTERNA": "ffmpeg (extração) + faster-whisper (reconhecimento)",
    # ⚠️ O DONO DO ASR VAI NA FICHA, E NÃO É DECORAÇÃO.
    # Quem ler a capacidade tem de conseguir chegar a quem realmente ouve, sem
    # abrir este ficheiro. Foi assim que `adaptador_instagram` já declarava
    # `ASR_OWNER`, e repetir o dono aqui é o contrário de duplicar o dono: é
    # apontar para ele.
    "ASR_OWNER": "ferramentas/fala_local.py",
}

#: A espécie do texto que sai daqui. NÃO é escolha por chamada: é uma
#: propriedade deste produtor, e por isso é constante.
#:
#:     CAPTION é texto que a PLATAFORMA publicou.
#:     TRANSCRIPT é texto que ESTA CASA produziu ouvindo.
#:
#: Colapsá-los apagaria a única pergunta que importa quando os dois discordam:
#: quem disse. `regras/proveniencia.py` é o dono deste vocabulário, e estes
#: nomes são lidos de lá, não escritos aqui.
TEXT_KIND = pv.TRANSCRIPT
TEXT_RELATION = pv.ORIGINAL
TEXT_BASIS = pv.PRODUCED_BY_LOCAL_ASR

#: O `kind` da linha do derivado, na língua da tabela.
KIND = "AUDIO_TRANSCRIPTION"


def ha_ferramenta() -> bool:
    """O `ffmpeg` está nesta máquina? O ASR responde por si em `fl.disponivel()`."""
    import shutil
    return shutil.which("ffmpeg") is not None


def aceita(media_type) -> bool:
    """Esta ponte abre esta espécie? → True/False. A pergunta é a da porta.

    ⚠️ AUSÊNCIA NÃO É ACEITAÇÃO. Aqui, ao contrário de `_quem_deriva_aceita`,
    `None` responde `False` — e a diferença é de posição, não de opinião. A
    porta pergunta «ALGUÉM abre isto?», e aí não saber obriga a tentar. Esta
    função responde «EU abro isto?», e aí não saber é não.
    """
    if media_type is None or not str(media_type).strip():
        return False
    tipo = str(media_type).split(";")[0].strip().lower()
    if tipo in tuple(str(t).lower() for t in CAPACIDADE["ACEITA_MEDIA_TYPES"]):
        return True
    return tipo.split("/")[0] in FAMILIAS


def tem_fala_possivel(caminho) -> tuple:
    """Há faixa de áudio neste contentor? → (bool, porquê).

    Medido com `ffprobe`, pelo dono da mídia. Um MP4 só de vídeo existe, e
    mandá-lo ao reconhecedor produziria `REQUESTED_EMPTY` — que é verdade, mas
    uma verdade cara: paga-se o carregamento do modelo para descobrir uma coisa
    que o contentor dizia de graça.
    """
    try:
        imagem, som, porque = fl.fluxos(caminho)
    except Exception as e:                                     # noqa: BLE001
        return True, ("nao deu para ler os fluxos (%s) — e NAO SEI nao autoriza "
                      "concluir que nao ha audio" % type(e).__name__)
    # ⚠️ `fluxos()` devolve `(NAO_SEI, NAO_SEI, motivo)` quando NAO CONSEGUIU
    # MEDIR, e o proprio dono escreve porque: «nao consegui abrir» e «nao tem
    # som» sao coisas diferentes. Aqui a diferenca decide se se tenta.
    #
    #     NAO CONSEGUI VER != VI QUE NAO HA.
    if porque:
        return True, ("nao deu para medir os fluxos (%s) — tenta-se, porque "
                      "ausencia de medicao nao e ausencia de som" % porque)
    if not som:
        return False, ("ffprobe leu os fluxos e nao ha faixa de som "
                       "(imagem=%s, som=%s)" % (imagem, som))
    return True, "ffprobe encontrou %s faixa(s) de som" % som


def transcrever_ficheiro(caminho, *, idioma=None, dispositivo=None,
                         modelo_nome=None) -> dict:
    """MÍDIA → texto, pelo dono do ASR. → o dicionário dele, sem reescrita.

    ⚠️ ESTA FUNÇÃO NÃO INTERPRETA O RESULTADO, E ISSO É DE PROPÓSITO.
    Ela extrai o áudio quando a entrada é vídeo, chama `fala_local.transcrever`
    e devolve o que ele disse. Traduzir aqui `REQUESTED_EMPTY` para «sem fala»
    criaria um segundo vocabulário do mesmo facto.

        TRANSPORTAR NÃO É CONHECER. E TRADUZIR É UMA FORMA DE CONHECER.
    """
    caminho = str(caminho)
    pasta = tempfile.mkdtemp(prefix="sintonia-asr-")
    wav = os.path.join(pasta, "audio.wav")
    try:
        # `so_audio` responde se o contentor JÁ é áudio puro; nesse caso o
        # `ffmpeg` continua a correr, porque 16 kHz mono é o que o modelo
        # espera e um MP3 a 44,1 kHz não é isso.
        saida, porque = fl.extrair_audio(caminho, wav)
        if not saida:
            return {"TRANSCRIPT": None,
                    "TRANSCRIPT_STATE": fl.ASR_INDISPONIVEL,
                    "TRANSCRIPT_CHARS": 0,
                    "ERRO": porque,
                    "ETAPA_QUE_FALHOU": "EXTRACAO_DE_AUDIO",
                    "LANGUAGE": fl.NAO_SEI,
                    "LANGUAGE_SOURCE": "DETECTED"}
        dur = fl.duracao(saida)
        r = fl.transcrever(saida, idioma=idioma, duracao_s=dur,
                           dispositivo=dispositivo, modelo_nome=modelo_nome)
        r = dict(r)
        r["AUDIO_EXTRACTED_BYTES"] = os.path.getsize(saida)
        r["ETAPA_QUE_FALHOU"] = None if r.get("TRANSCRIPT_STATE") == fl.OK else "ASR"
        return r
    finally:
        for f in (wav,):
            try:
                os.path.exists(f) and os.remove(f)
            except OSError:                                    # pragma: no cover
                pass
        try:
            os.rmdir(pasta)
        except OSError:                                        # pragma: no cover
            pass


def derivar_um(raw_asset_id, midia, armazem, memoria, relogio=None,
               contexto_da_passagem=None) -> dict:
    """Uma mídia, um pai canónico, um transcript — pelo dono da escrita.

    A assinatura é, PROPOSITADAMENTE, a mesma de
    `executor_texto_de_pdf.derivar_um`. O segundo parâmetro chama-se `midia` e
    não `pdf` porque é o que é — mas a POSIÇÃO é a mesma, para que
    `derivacao_forward.correr()` possa chamar os dois sem saber qual tem na mão.

        DOIS EXECUTORES COM A MESMA FORMA SÃO UM PONTO DE ESCOLHA.
        DOIS COM FORMAS DIFERENTES SÃO DOIS CAMINHOS, E AÍ ALGUÉM ESCREVE O `if`.

    ⚠️ O QUE ESTE EXECUTOR NÃO CALCULA, E POR ISSO NÃO PODE MENTIR:
    `parent_sha256`, `sha256` do filho, `parameters_hash`, `derived_at` e
    `storage_path` são todos do dono da escrita. Ele entrega a RECEITA e os
    BYTES.
    """
    from guarda.preservar_derivado import agora_utc, preservar_derivado

    ha, porque_asr = fl.disponivel()
    if not ha or not ha_ferramenta():
        # ⚠️ FERRAMENTA QUE FALTA NÃO É DOCUMENTO QUEBRADO — `COL-LAW-503`.
        return {"ESTADO": "SEM_DERIVADO",
                "MOTIVO_DO_EXECUTOR": fl.ASR_INDISPONIVEL,
                "ERRO": porque_asr if not ha else "ffmpeg ausente nesta maquina",
                "NAO_SIGNIFICA": ("que a midia nao tem fala. A ferramenta e que "
                                  "nao esta aqui."),
                "MEDIDAS": {}}

    tem, porque_fluxo = tem_fala_possivel(midia)
    if not tem:
        # Facto sobre o ORIGINAL, e vai no recibo. Não vira linha de derivado,
        # exactamente como o PDF sem camada de texto.
        return {"ESTADO": "SEM_DERIVADO",
                "MOTIVO_DO_EXECUTOR": "SEM_FAIXA_DE_AUDIO",
                "ERRO": porque_fluxo,
                "NAO_SIGNIFICA": "que o ficheiro esta corrompido.",
                "MEDIDAS": {"FLUXOS": porque_fluxo}}

    r = transcrever_ficheiro(midia)
    estado = r.get("TRANSCRIPT_STATE")
    texto = r.get("TRANSCRIPT")
    if estado != fl.OK or not texto:
        return {"ESTADO": "SEM_DERIVADO",
                "MOTIVO_DO_EXECUTOR": estado,
                "ERRO": r.get("ERRO") or "",
                "NAO_SIGNIFICA": ("que a Admissao recusou. A Admissao nem foi "
                                  "chamada: ASR_FAILED != CONTENT_REJECTED."),
                "MEDIDAS": {k: r.get(k) for k in
                            ("AUDIO_SECONDS", "MACHINE_SECONDS",
                             "ASR_DEVICE_USED", "ASR_MODEL",
                             "ETAPA_QUE_FALHOU")}}

    # ── A RECEITA ───────────────────────────────────────────────────────────
    # ⚠️ SÓ ENTRA AQUI O QUE DEFINE O ARTEFATO, NUNCA O QUE MEDE A MÁQUINA.
    # `parameters` é hasheado para `parameters_hash`, e esse hash é metade da
    # identidade da receita. Pôr `MACHINE_SECONDS` aqui faria a MESMA mídia,
    # transcrita duas vezes, parecer dois artefatos diferentes — e a segunda
    # corrida escreveria linha nova em vez de reencontrar a primeira.
    #
    #     O QUE VARIA ENTRE DUAS CORRIDAS IGUAIS NÃO É IDENTIDADE: É MEDIDA.
    #
    # A língua DETECTADA entra, e entra de propósito: ela é uma propriedade dos
    # bytes lidos com este modelo, não do relógio. Dois modelos que ouçam
    # línguas diferentes produziram artefatos diferentes, e têm de o dizer.
    parametros = {
        "TEXT_KIND": TEXT_KIND,
        "TEXT_RELATION": TEXT_RELATION,
        "TEXT_BASIS": TEXT_BASIS,
        "LANGUAGE": r.get("LANGUAGE"),
        "LANGUAGE_SOURCE": r.get("LANGUAGE_SOURCE"),
        "ASR_OWNER": CAPACIDADE["ASR_OWNER"],
        # Os nomes são os do carimbo do dono do ASR, lidos de lá. Inventar
        # `MODEL_USED` aqui — como esta função fez na primeira escrita — dava
        # `None` em silêncio, e um `None` numa receita vira um `parameters_hash`
        # que não distingue `small` de `large`.
        #
        #     UM CAMPO COM O NOME ERRADO NÃO FICA VAZIO: FICA FALSAMENTE IGUAL.
        "ASR_MODEL": r.get("ASR_MODEL"),
        "ASR_ENGINE": r.get("ASR_ENGINE") or fl.MOTOR,
        "ASR_BEAM": r.get("ASR_BEAM"),
    }

    recibo = preservar_derivado(
        {**(contexto_da_passagem or {}),
         "raw_asset_id": raw_asset_id,
         "kind": KIND,
         "producer": EXECUTOR_ID,
         "producer_version": EXECUTOR_VERSION,
         "pipeline_version": PIPELINE_VERSION,
         "parameters": parametros,
         "serie_posicao": None,
         "media_type": "text/plain"},
        texto.encode("utf-8"), armazem, memoria,
        relogio=relogio or agora_utc)

    # A espécie do texto viaja no recibo TAMBÉM, e não só dentro de
    # `parameters`. Quem lê o recibo não tem de desempacotar um hash para saber
    # que isto é um TRANSCRIPT e não uma CAPTION.
    return {**recibo,
            "TEXT_KIND": TEXT_KIND,
            "TEXT_RELATION": TEXT_RELATION,
            "LANGUAGE": r.get("LANGUAGE"),
            "LANGUAGE_SOURCE": r.get("LANGUAGE_SOURCE"),
            "LANGUAGE_CONFIDENCE": r.get("LANGUAGE_CONFIDENCE"),
            "DEVICE_USED": r.get("ASR_DEVICE_USED"),
            "DEVICE_EXECUTION": r.get("ASR_DEVICE_EXECUTION"),
            "ASR_MODEL": r.get("ASR_MODEL"),
            "AUDIO_SECONDS": r.get("AUDIO_SECONDS"),
            "MACHINE_SECONDS": r.get("MACHINE_SECONDS")}


def _seco(caminho):
    """Olha a mídia e conta o que daria — sem ASR, sem escrever, sem banco."""
    tem, porque = tem_fala_possivel(caminho)
    ha_asr, porque_asr = fl.disponivel()
    imagem, som, porque_fluxos = fl.fluxos(caminho)
    return {
        "FICHEIRO": os.path.basename(caminho),
        "BYTES": os.path.getsize(caminho) if os.path.isfile(caminho) else 0,
        "DURACAO_S": fl.duracao(caminho),
        "FLUXOS_IMAGEM": imagem,
        "FLUXOS_SOM": som,
        "FLUXOS_PORQUE": porque_fluxos,
        "TEM_FAIXA_DE_AUDIO": tem,
        "PORQUE": porque,
        "FFMPEG_PRESENTE": ha_ferramenta(),
        "ASR_DISPONIVEL": ha_asr,
        "ASR_PORQUE": "" if ha_asr else porque_asr,
        "TEXT_KIND_QUE_SAIRIA": TEXT_KIND,
        "TEXT_RELATION_QUE_SAIRIA": TEXT_RELATION,
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--ficha" in args or not args:
        print(json.dumps(CAPACIDADE, ensure_ascii=False, indent=1, default=str))
        raise SystemExit(0)
    if "--seco" in args:
        alvo = [a for a in args if a != "--seco"]
        if not alvo:
            print("uso: --seco <ficheiro>")
            raise SystemExit(2)
        print(json.dumps(_seco(alvo[0]), ensure_ascii=False, indent=1,
                         default=str))
        raise SystemExit(0)
    print("uso: --ficha | --seco <ficheiro>")
    raise SystemExit(2)
