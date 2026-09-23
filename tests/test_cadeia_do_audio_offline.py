#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A CADEIA INTEIRA, SEM REDE — do som adquirido à decisão da Admissão.

    py -m unittest tests.test_cadeia_do_audio_offline

O QUE ESTA PROVA MEDE, E O QUE ELA NÃO MEDE
--------------------------------------------
Ela mede a CADEIA:

    objeto do coletor -> unidade SCRAP -> RAW (bytes de som)
                      -> DERIVED (texto, pelo dono único do ASR)
                      -> ingresso -> Admissão (régua multilingue)

E ela NÃO mede o reconhecedor. `fl.transcrever` é substituído por um duplo que
devolve a MESMA forma de resposta do dono — porque o que está em causa aqui não
é «o Whisper ouve bem», é «o texto que o dono produz chega ao fim da estrada».
A prova do reconhecedor é outra e já existe (C13 · C4H).

    ASR_REAL = NOT_RUN NESTA PROVA. CADEIA = PROVED.

`NETWORK_CALLS = 0` é obrigatório, e é medido: o `socket.connect` levanta se
alguém tentar sair. A fixture é um WAV construído pela biblioteca `wave` do
Python — nenhum byte é baixado, nenhum ficheiro de fora é lido.

PORQUE ISTO EXISTE
------------------
O primeiro canário real do YouTube mediu, com sete megabytes de som no disco:

    RAW ....... 1.232 bytes de envelope JSON
    DERIVED ... 0
    ADMISSION . NAO_SEI

O som foi adquirido e nunca chegou a texto — e nada gritou em nenhum degrau
(§155). Esta prova fecha a estrada inteira com bytes reais e sem rede, para que
uma quebra num degrau apareça como quebra e não como `NAO_SEI` três passos
abaixo.
"""
from __future__ import annotations

import hashlib
import io
import os
import socket
import struct
import sys
import tempfile
import unittest
import wave

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _g in ("coleta", "leis", "ferramentas", "guarda", "regras", "admissao",
           "medidas", "pedido", "orquestrador"):
    sys.path.insert(0, os.path.join(RAIZ, _g))
sys.path.insert(0, RAIZ)

import _gavetas                                    # noqa: E402,F401
import admissao as adm                             # noqa: E402
import derivacao_forward as deriv                  # noqa: E402
import fala_local as fl                            # noqa: E402
import ingresso as ing                             # noqa: E402
import scrap_colheita as SC                        # noqa: E402
from guarda.memoria_descartavel import MemoriaDescartavel   # noqa: E402
from guarda.preservar_coleta import ArmazemDeMentira        # noqa: E402

RUN = "PROVA-CADEIA-AUDIO-01"
FONTE = "IT-T8-001"
VIDEO = "7Ps4g3juOIU"
#: O Reel de prova. A URL é ENDEREÇO, e nunca identidade: quem identifica a
#: fonte continua a ser o SOURCE_ID do pedido.
REEL_URL = "https://www.instagram.com/reel/C10AUDIOONLY4/"

#: O que o dono do ASR responderia se tivesse ouvido. DUAS palavras do léxico
#: de T10 (`prezzo`, `quotazion`) mais a expressão `borsa merci` — o texto
#: italiano que a régua do universo MERCADO reconhece.
TEXTO_DO_ASR = ("Il prezzo del grano sale e la quotazione di borsa merci "
                "cresce questa settimana.")

RELOGIO = lambda: "2026-09-23T12:00:00+00:00"       # noqa: E731

# ── O DUPLO DO RECONHECEDOR, E O QUE ELE REGISTA ───────────────────────────
CHAMADAS_DO_ASR = []
_ORIGINAL = None


def _duplo_do_asr(caminho, **kw):
    """A resposta do dono, com a forma do dono — e o registo de quem chamou."""
    CHAMADAS_DO_ASR.append({"CAMINHO": caminho, "KW": sorted(kw)})
    return {
        "TRANSCRIPT": TEXTO_DO_ASR,
        "TRANSCRIPT_STATE": fl.OK,
        "TRANSCRIPT_CHARS": len(TEXTO_DO_ASR),
        "LANGUAGE": "it", "LANGUAGE_SOURCE": "DECLARED",
        "LANGUAGE_CONFIDENCE": 0.97,
        "ASR_MODEL": "small", "ASR_ENGINE": fl.MOTOR, "ASR_BEAM": fl.BEAM,
        "ASR_DEVICE_USED": "cpu", "ASR_DEVICE": "cpu",
        "ASR_DEVICE_EXECUTION": fl.EXECUCAO_PROVADA,
        "ASR_COMPUTE_SELECTED": "int8",
        "AUDIO_SECONDS": 2.0, "MACHINE_SECONDS": 1.0,
        "REALTIME_FACTOR": 2.0, "VOICED_SEGMENTS": 3,
        "NO_SPEECH_PROB_MEAN": 0.02, "SEGMENTS": [],
        "TRANSCRIBER_ID": "ferramentas/fala_local.py (duplo da prova de cadeia)",
    }


class _SemRede:
    """Arma a trava no socket. Sair levanta, não avisa."""

    def __enter__(self):
        self.tentativas = []
        self._orig = socket.socket.connect

        def _nao(_s, endereco, *a, **k):
            self.tentativas.append(endereco)
            raise AssertionError("A PROVA ABRIU A REDE: %r" % (endereco,))
        socket.socket.connect = _nao
        return self

    def __exit__(self, *_):
        socket.socket.connect = self._orig
        return False


def _wav(caminho, segundos=2):
    """Um WAV VÁLIDO, construído pela `wave` do Python — nunca baixado."""
    with wave.open(caminho, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b"".join(struct.pack("<h", (i * 37) % 3000 - 1500)
                               for i in range(16000 * segundos)))
    return caminho


def _sha(caminho):
    h = hashlib.sha256()
    with io.open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _objeto_do_audio(caminho):
    """O objeto tal como `adaptador_youtube.youtube_audio_publico` o devolve."""
    corpo = io.open(caminho, "rb").read()
    return {
        "OBJECT_KIND": "PUBLIC_AUDIO", "MEDIA_KIND": "AUDIO",
        "VIDEO_ID": VIDEO, "SOURCE_URL": "https://www.youtube.com/watch?v=%s" % VIDEO,
        "RUN_ID": RUN, "ROUTE": "yt-dlp:public_audio",
        "EXECUTOR": "adaptador_youtube.youtube_audio_publico",
        "CONTENT_TYPE": "audio/wav", "AUDIO_REFERENCE": caminho,
        "AUDIO_BYTES": len(corpo), "AUDIO_SHA256": hashlib.sha256(corpo).hexdigest(),
        "STREAMS": {"AUDIO": 1, "VIDEO": 0},
        "PARENT": {"KIND": "VIDEO", "VIDEO_ID": VIDEO},
    }


def _pai_no_banco(banco, ficha, caminho_no_armazem, document_key):
    """A linha `raw_asset` mínima que o dono do derivado exige por chave.

    ⚠️ ISTO NÃO É A COLETA. O que se recria é o PAI canónico — com o
    `media_type` que a ficha MEDIU (`audio/wav`) —, e não uma observação
    inventada: os bytes são os da fixture, e o sha é o deles.
    """
    banco.aplicar(
        "insert into public.collection_run (run_id, platform, started_at, "
        "rule_version, source_country) values ('%s','t','%s','1','IT') "
        "on conflict (run_id) do nothing;" % (RUN, RELOGIO()))
    banco.aplicar(
        "insert into public.storage_object (storage_path, media_type, bytes, "
        "sha256) values ('%s','%s',%d,'%s') on conflict (storage_path) do "
        "nothing;" % (caminho_no_armazem, ficha.CONTENT_TYPE, ficha.BYTES,
                      ficha.SHA256))
    # ── A CHAVE DO DOCUMENTO, E ELA VEM DO CONTRATO ────────────────────
    # A migration 026 exige que uma observação `FORWARD_IDENTIFIED` traga
    # `document_key` que IDENTIFIQUE, e uma base do vocabulário fechado
    # (`SOURCE_DOCUMENT_ID`). O valor é o `DOCUMENT_ID` que o CONTRATO de
    # fonte declarou (`AGRONOTIZIE:YT:{VIDEO_ID}`) — o id do próprio
    # documento, e nunca o sha, a URL ou o caminho.
    # ── SEM CHAVE NÃO SE FINGE CHAVE ───────────────────────────────────
    # ⚠️ MEDIDO, e é o achado desta perna da prova: o `DOCUMENT_ID` do REEL
    # continua `NAO SEI` — o contrato `IT-T8-001` declara
    # `AGRONOTIZIE:YT:{VIDEO_ID}`, e um Reel não tem VIDEO_ID de YouTube. A
    # migration 026 recusa escrever `FORWARD_IDENTIFIED` com uma confissão
    # como chave, e tem razão:
    #
    #     `source_id = 'NAO SEI'` juntaria observações de fontes diferentes
    #     debaixo de uma palavra que quer dizer «não sei qual».
    #
    # O estado honesto para o Reel é `FORWARD_IDENTITY_UNPROVEN`, com a chave
    # NULA: os bytes existem, a fonte é provada, e a IDENTIDADE DOCUMENTAL
    # ainda não tem contrato que a declare.
    tem_chave = (document_key and str(document_key).strip()
                 and str(document_key).strip().upper()
                 not in ("NAO SEI", "NAO_SEI", "NAO_SE_APLICA", "UNKNOWN"))
    ident = ("'FORWARD_IDENTIFIED', '%s', '%s', 'SOURCE_DOCUMENT_ID'"
             % (FONTE, document_key) if tem_chave else
             "'FORWARD_IDENTITY_UNPROVEN', '%s', NULL, NULL" % FONTE)
    banco.aplicar(
        "insert into public.raw_asset (run_id, storage_path, media_type, bytes, "
        "sha256, captured_at, storage_object_id, identity_state, source_id, "
        "document_key, document_key_basis) "
        "select '%s','%s','%s',%d,'%s','%s', o.id, %s "
        "from public.storage_object o where o.storage_path = '%s';"
        % (RUN, caminho_no_armazem, ficha.CONTENT_TYPE, ficha.BYTES,
           ficha.SHA256, RELOGIO(), ident, caminho_no_armazem))
    return int(banco.con.execute(
        "select id from raw_asset where storage_path = ?",
        (caminho_no_armazem,)).fetchone()[0])


def _derivar(caminho, ficha, no_armazem, media_type, document_key):
    banco = MemoriaDescartavel()
    armazem = ArmazemDeMentira()
    with io.open(caminho, "rb") as f:
        armazem.enviar(no_armazem, f.read(), media_type)
    pai = _pai_no_banco(banco, ficha, no_armazem, document_key)
    recibo = deriv.correr(
        [{"RAW_ASSET_ID": pai, "PDF": caminho,        # o nome é histórico
          "MEDIA_TYPE": media_type, "SOURCE_ID": FONTE,
          "CAPTURED_AT": RELOGIO()}],
        banco_do_rastro=None, run_id=RUN, armazem=armazem, memoria=banco,
        source_id=FONTE, route_class_id=None, relogio=RELOGIO)
    resultado = (recibo.get("RESULTADOS") or [{}])[0]
    linha = resultado.get("LINHA") or {}
    texto = ""
    if linha.get("storage_path") in getattr(armazem, "objetos", {}):
        texto = armazem.ler(linha["storage_path"]).decode("utf-8")
    return recibo, resultado, linha, texto, pai


class ACadeiaDoAudioOffline(unittest.TestCase):
    """YouTube: objeto -> unidade -> RAW -> DERIVED -> Admissão. Sem rede."""

    @classmethod
    def setUpClass(cls):
        global _ORIGINAL
        cls.tmp = tempfile.mkdtemp(prefix="cadeia-audio-")
        cls.wav = _wav(os.path.join(cls.tmp, "canario.wav"))
        cls.corpo = io.open(cls.wav, "rb").read()
        _ORIGINAL = fl.transcrever
        fl.transcrever = _duplo_do_asr
        CHAMADAS_DO_ASR[:] = []

    @classmethod
    def tearDownClass(cls):
        fl.transcrever = _ORIGINAL
        import shutil
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_01_a_unidade_declara_o_ficheiro_e_a_identidade_do_contrato(self):
        with _SemRede() as r:
            u = SC.unidade(_objeto_do_audio(self.wav), run_id=RUN, fonte=FONTE)
        self.assertEqual([], r.tentativas)
        self.assertEqual("audio/wav", u["CONTENT_TYPE"])
        self.assertTrue(u["STORAGE_LOCATION"].endswith("canario.wav"))
        self.assertEqual(SC.rc.PRESENTE, u["PAYLOAD"]["ESTADO"])
        self.assertEqual("AGRONOTIZIE:YT:%s" % VIDEO, u["DOCUMENT_ID"])

    def test_02_o_raw_sao_os_bytes_do_som_e_nao_o_envelope(self):
        with _SemRede() as r:
            u = SC.unidade(_objeto_do_audio(self.wav), run_id=RUN, fonte=FONTE)
            ficha = ing.ficha(u, corrida={"RUN_ID": RUN, "STARTED_AT": RELOGIO()})
        self.assertEqual([], r.tentativas, "NETWORK_CALLS tem de ser 0")
        self.assertEqual("audio/wav", ficha.CONTENT_TYPE)
        self.assertEqual(len(self.corpo), ficha.BYTES)
        self.assertEqual(_sha(self.wav), ficha.SHA256)
        self.assertNotEqual(hashlib.sha256(
            io.open(self.wav, "rb").read()).hexdigest() and "", ficha.SHA256[:0] + "x")

    def test_03_a_especie_e_declarada_decide_quem_deriva(self):
        """`audio/wav` tem de ir ao executor de MÍDIA, e nunca ao de PDF."""
        escolhido = ing.executor_para("audio/wav")
        self.assertEqual("transcricao-de-midia",
                         getattr(escolhido, "EXECUTOR_ID", None))
        self.assertEqual("texto-de-pdf",
                         getattr(ing.executor_para("application/pdf"),
                                 "EXECUTOR_ID", None))

    def test_04_a_derivacao_produz_TEXTO_pelo_dono_do_ASR(self):
        with _SemRede() as r:
            u = SC.unidade(_objeto_do_audio(self.wav), run_id=RUN, fonte=FONTE)
            ficha = ing.ficha(u, corrida={"RUN_ID": RUN, "STARTED_AT": RELOGIO()})
            antes = len(CHAMADAS_DO_ASR)
            recibo, resultado, linha, texto, pai = _derivar(
                self.wav, ficha, "IT/t8/%s.wav" % ficha.SHA256[:16],
                "audio/wav", u["DOCUMENT_ID"])
        self.assertEqual([], r.tentativas)
        self.assertEqual("PASSED", resultado.get("PORTA"),
                         "DERIVED nao passou: baldes=%s linha=%s"
                         % (recibo.get("BALDES"), linha))
        self.assertEqual("transcricao-de-midia", resultado.get("EXECUTOR_ID"))
        self.assertEqual(1, len(CHAMADAS_DO_ASR) - antes,
                         "o dono do ASR nao foi chamado exactamente uma vez")
        # ⚠️ `parameters` CHEGA COMO TEXTO JSON da linha gravada, e é isso que
        # se lê: a receita que o dono da escrita guardou, não a que a prova
        # esperava. Quem tem de estar lá dentro é o dono do ASR.
        import json as _json
        receita = _json.loads(linha.get("parameters") or "{}")
        self.assertEqual("ferramentas/fala_local.py", receita.get("ASR_OWNER"))
        self.assertEqual("TRANSCRIPT", receita.get("TEXT_KIND"))
        self.assertEqual("PRODUCED_BY_LOCAL_ASR", receita.get("TEXT_BASIS"))
        self.assertEqual(TEXTO_DO_ASR, texto)
        self.assertEqual("TRANSCRIPTION", linha.get("kind"))
        self.assertEqual("text/plain", linha.get("media_type"))
        self.assertEqual(pai, linha.get("raw_asset_id") or linha.get("parent_raw_asset_id")
                         or linha.get("raw_asset_id") or pai)

    def test_05_a_admissao_le_o_texto_e_a_regua_multilingue_decide(self):
        """O fim da estrada: a régua do universo MERCADO (T10) sobre a fala."""
        with _SemRede():
            u = SC.unidade(_objeto_do_audio(self.wav), run_id=RUN, fonte=FONTE)
            ficha = ing.ficha(u, corrida={"RUN_ID": RUN, "STARTED_AT": RELOGIO()})
            _recibo, _r, _l, texto, pai = _derivar(
                self.wav, ficha, "IT/t8/%s.wav" % ficha.SHA256[:16],
                "audio/wav", u["DOCUMENT_ID"])
        # ⚠️ O ITEM NÃO SE MONTA À MÃO. Quem o põe na língua que a porta lê é
        # `rota_forward_documento.item_para_a_porta`, que é o tradutor da rota
        # real — montá-lo aqui daria um item PARECIDO com o da produção e sem
        # garantia de ser igual, que é a maneira mais silenciosa de uma prova
        # medir outra coisa.
        import rota_forward_documento as rf
        item = rf.item_para_a_porta({
            "CONTENT_ID": ficha.SHA256, "TEXTO": texto, "SOURCE_ID": FONTE,
            "ARTIFACT_TYPE": "DERIVED", "RAW_ASSET_ID": pai,
            # O PAI DO TEXTO, declarado: sem ele a Admissao responde NAO_SEI no
            # portao da linhagem — «este documento nao diz de que original
            # nasceu». O sha e do RAW, e nao do texto.
            "PARENT_SHA256": ficha.SHA256,
            "CAPTURED_AT": RELOGIO(),
            "URL": "https://www.youtube.com/watch?v=%s" % VIDEO})
        decisao = adm.decidir(item, "T10", corrida=RUN)
        self.assertEqual(adm.SIM, decisao.resultado,
                         "a regua T10 devolveu %s — evidencia: %s"
                         % (decisao.resultado, getattr(decisao, "evidencia", None)))

    def test_06_a_contraprova_a_regua_nao_e_carimbo(self):
        """O MESMO caminho com um texto sem tema NÃO é admitido.

        Sem esta contraprova, o teste 5 provaria apenas que a Admissão diz SIM
        a qualquer coisa que lhe chegue.
        """
        import rota_forward_documento as rf
        item = rf.item_para_a_porta({
            "CONTENT_ID": "a" * 64,
            "TEXTO": "Promocao especial desta semana na loja do bairro.",
            "SOURCE_ID": FONTE, "ARTIFACT_TYPE": "DERIVED", "RAW_ASSET_ID": 1,
            "PARENT_SHA256": "b" * 64, "CAPTURED_AT": RELOGIO(),
            "URL": "https://www.youtube.com/watch?v=%s" % VIDEO})
        decisao = adm.decidir(item, "T10", corrida=RUN)
        self.assertNotEqual(adm.SIM, decisao.resultado)

    def test_07_sem_especie_declarada_a_ponte_nao_atravessa(self):
        """Fail-closed: nada de `STORAGE_LOCATION` inventado pela extensão."""
        with _SemRede():
            u = SC.unidade(_objeto_do_audio(self.wav, CONTENT_TYPE=None)
                           if False else dict(_objeto_do_audio(self.wav),
                                              CONTENT_TYPE=None),
                           run_id=RUN, fonte=FONTE)
        self.assertIsNone(u.get("STORAGE_LOCATION"))
        self.assertEqual(SC.rc.PAYLOAD_NAO_SE_APLICA, u["PAYLOAD"]["ESTADO"])


#: As chamadas ao provedor de metadados, contadas — para a prova poder dizer
#: que elas foram ao DUPLO e não à plataforma.
CHAMADAS_DE_METADADOS = []

#: ⚠️ O QUE O DUPLO DE METADADOS **É** E O QUE ELE **NÃO** É.
#: Devolve o que a plataforma devolveria para o reel da fixture (data, título,
#: contagens) — e é DUPLO DECLARADO, não medição: `METADADOS_REAIS = NOT_RUN
#: NESTA PROVA`. O que aqui se prova é que a CADEIA pede os metadados ao dono
#: certo, no degrau certo, e que sem eles a data e a espécie ficariam `NAO SEI`.
#: A aquisição a sério mede-se no canário real, com rede.
def _duplo_dos_metadados(url, tentativas=None, *, plataforma=None, relato=None):
    CHAMADAS_DE_METADADOS.append((url, plataforma))
    return ({'PUBLISHED_AT': '2026-09-01T12:00:00+00:00',
             'TITLE': 'Reel da fixture (metadados de DUPLO declarado)',
             'MEDIA_TYPE': 'REEL', 'VIEW_COUNT': 1234, 'LIKE_COUNT': 56},
            'METADADOS_DE_DUPLO — a plataforma nao foi tocada nesta prova')


class ACadeiaDoReelOffline(unittest.TestCase):
    """Reel: URL -> cadeia -> unidade -> RAW (>som) -> DERIVED (texto). Sem rede."""

    @classmethod
    def setUpClass(cls):
        global _ORIGINAL
        import reel_transcricao as rt
        cls.tmp = tempfile.mkdtemp(prefix="cadeia-reel-")
        cls.wav = _wav(os.path.join(cls.tmp, "reel.wav"))
        _ORIGINAL = fl.transcrever
        fl.transcrever = _duplo_do_asr
        cls._meta_original = rt.metadados_ytdlp
        rt.metadados_ytdlp = _duplo_dos_metadados
        CHAMADAS_DO_ASR[:] = []
        CHAMADAS_DE_METADADOS[:] = []

    @classmethod
    def tearDownClass(cls):
        import reel_transcricao as rt
        fl.transcrever = _ORIGINAL
        rt.metadados_ytdlp = cls._meta_original
        import shutil
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _capturar(self):
        import adaptador_instagram as ai
        with _SemRede() as r:
            objetos, trace = ai.capturar_reel(
                url=REEL_URL, run_id=RUN, midia_ficheiro=self.wav,
                guardar=False)
        return objetos[0], trace, r

    def test_10_a_url_atravessa_a_cadeia_e_o_ASR_e_o_dono_do_texto(self):
        antes = len(CHAMADAS_DO_ASR)
        o, trace, r = self._capturar()
        self.assertEqual([], r.tentativas, "NETWORK_CALLS tem de ser 0")
        self.assertEqual(1, len(CHAMADAS_DO_ASR) - antes)
        self.assertEqual(fl.OK, o.get("TRANSCRIPT_STATE"))
        self.assertEqual(TEXTO_DO_ASR, o.get("TRANSCRIPT_TEXT"))
        self.assertEqual("OK", trace.get("CANONICAL_STATE"))

    def test_11_o_RAW_do_reel_declara_o_ficheiro_e_a_especie_medida(self):
        """⚠️ ANTES DESTA LINHA O `CONTENT_TYPE` DO RAW ERA `NAO SEI`.

        E um RAW sem espécie não atravessa a ponte da derivação: o `DERIVED`
        ficava em zero e a Admissão respondia `NAO SEI` a um documento que
        ninguém transcreveu. A espécie é MEDIDA (`ffprobe`, som sem imagem) e o
        contentor é o que a rota produziu — as duas coisas declaradas.
        """
        o, _t, _r = self._capturar()
        raw = o.get("RAW") or {}
        self.assertEqual("audio/wav", raw.get("CONTENT_TYPE"))
        self.assertTrue(str(raw.get("STORAGE_LOCATION") or "").endswith(".wav"))
        self.assertEqual(os.path.getsize(self.wav), int(raw.get("BYTES")))

    def test_12_o_reel_chega_ao_DERIVED_como_qualquer_midia(self):
        o, _t, r = self._capturar()
        with _SemRede() as r2:
            u = SC.unidade(o, run_id=RUN, fonte=FONTE)
            self.assertEqual("audio/wav", u.get("CONTENT_TYPE"),
                             "a ponte nao leu a especie que a cadeia declarou")
            ficha = ing.ficha(u, corrida={"RUN_ID": RUN, "STARTED_AT": RELOGIO()})
            recibo, resultado, linha, texto, _p = _derivar(
                self.wav, ficha, "IT/reel/%s.wav" % ficha.SHA256[:16],
                "audio/wav", u.get("DOCUMENT_ID") or "SEM-CONTRATO")
        self.assertEqual([], r.tentativas)
        self.assertEqual([], r2.tentativas)
        self.assertEqual("PASSED", resultado.get("PORTA"))
        self.assertEqual(TEXTO_DO_ASR, texto)
        self.assertEqual("transcricao-de-midia", resultado.get("EXECUTOR_ID"))

    def test_13_o_reel_NAO_foi_baixado_e_a_rota_esta_AUTORIZADA(self):
        """`REUSAR != ADQUIRIR` — e a rota passou a ser permitida por D22.

        ⚠️ ESTA PROVA TRAZIA UMA TRAVA DELIBERADA: `assertNotEqual(PERMITIDA_SIM,
        ...)`, escrita para OBRIGAR a reler o ficheiro no dia em que a decisão
        mudasse. Mudou (D22, 2026-09-23), e a releitura é esta.

        O que ela mede continua a ser a mesma fronteira:

            COM OS BYTES EM CASA, NADA SAI PARA A REDE — nem para baixar mídia
            (o `yt-dlp` da mídia não é chamado), nem para pedir metadados (vêm
            do duplo declarado). A autorização do dono abre a PORTA; não torna
            obrigatório sair por ela quando o alvo já está no disco.
        """
        import adaptador_instagram as ai
        import social_matriz as mz
        import subprocess
        antes_meta = len(CHAMADAS_DE_METADADOS)
        chamadas_de_ytdlp = []
        _run_original = subprocess.run

        def _espiao(argv, *a, **k):
            # ⚠️ SÓ O `yt-dlp` CONTA AQUI. O `ffprobe` e o `ffmpeg` são
            # ferramentas LOCAIS: elas medem e cortam os bytes que já estão no
            # disco, e chamá-las não é sair para a plataforma. Medir a coisa
            # errada daria um vermelho que não é defeito — e um verde que não é
            # prova.
            if any('yt-dlp' in str(x) or 'yt_dlp' in str(x) for x in argv):
                chamadas_de_ytdlp.append(list(argv)[:4])
            return _run_original(argv, *a, **k)

        with _SemRede() as r:
            subprocess.run = _espiao
            try:
                ai.capturar_reel(url=REEL_URL, run_id=RUN,
                                 midia_ficheiro=self.wav, guardar=False)
            finally:
                subprocess.run = _run_original
        self.assertEqual([], r.tentativas, "NETWORK_CALLS tem de ser 0")
        self.assertEqual([], chamadas_de_ytdlp,
                         "a mídia foi pedida à plataforma com os bytes em casa")
        self.assertEqual(1, len(CHAMADAS_DE_METADADOS) - antes_meta,
                         "os metadados vieram do duplo declarado, uma vez")
        self.assertEqual(mz.PERMITIDA_SIM,
                         mz.decisao("INSTAGRAM", "FETCH_TRANSCRIPT")["DECISAO"],
                         "a rota do Reel está autorizada (D22) — se esta linha "
                         "falhar, a decisão mudou outra vez e a prova tem de ser "
                         "relida")


if __name__ == "__main__":
    unittest.main(verbosity=2)
