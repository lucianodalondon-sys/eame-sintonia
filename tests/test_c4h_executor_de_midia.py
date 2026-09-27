#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROVA DO DELTA DA UNIÃO C4H — o que a BIG não tinha antes de 4B2.

DE ONDE ESTE FICHEIRO VEM
--------------------------
`big-collection-gate-01` e `local-gpu-on-current-collection-v1` construíram a
ponte de mídia em paralelo. A união ficou com a ESTRUTURA da BIG e com as
CAPACIDADES que só a GPU tinha. A prova original da GPU, importada tal e qual,
reprovou 25 de 37 casos — e **nenhum** por a ponte estar errada:

    procurava `em.tem_faixa_de_som`; aqui a função chama-se
    `tem_fala_possivel` — mesma lógica, ramo a ramo, nome diferente;

    exigia a string `pv.TRANSCRIPT` DENTRO de `derivar_um`; aqui o símbolo é
    `TEXT_KIND`, que É `pv.TRANSCRIPT`, lido do dono no topo do módulo;

    fazia `assertNotIn("SOURCE_ID", fonte)` e apanhava a DOCSTRING que
    promete, por escrito, que o executor não cria `SOURCE_ID`.

        UM TESTE ACOPLADO AO NOME INTERNO MEDE A FORMA, NÃO O CONTRATO.
        E DUAS FORMAS PODEM CUMPRIR O MESMO CONTRATO.

A MATRIZ DE TRADUÇÃO ESTÁ EM `docs/operacao/INTEGRACAO-C4H-SEMANTICA-V1.md`
----------------------------------------------------------------------------
Cada um dos 37 casos originais aparece lá com destino declarado. Resumo:

    MANTIDO                    9  invariantes da união, provados aqui
    REESCRITO_EQUIVALENTE      6  perguntam pela propriedade, não pelo símbolo
    COBERTO_POR_OUTRO_TESTE   21  `tests/test_c4h_ponte_de_midia.py` já os prova
    BLOQUEADO                  1  `test_familias_NAO_foram_portadas` — ver abaixo

⚠️ O QUE ESTE FICHEIRO NÃO É
-----------------------------
Não é a prova inteira da C4H. `tests/test_c4h_ponte_de_midia.py` continua a ser
o portão da escolha de executor, do contrato do texto e dos «nãos». Este
ficheiro prova o DELTA — e mede por EXECUÇÃO sempre que a pergunta é sobre
comportamento, não por procura de texto.
"""
from __future__ import annotations

import ast
import inspect
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                        # noqa: E402,F401
import derivacao_forward as df                         # noqa: E402
import executor_texto_de_pdf as pdf                    # noqa: E402
import executor_transcricao_midia as em                # noqa: E402
import proveniencia as pv                              # noqa: E402

sys.path.insert(0, os.path.join(RAIZ, "ferramentas"))
import fala_local as fl                                # noqa: E402

FICHEIRO = "coleta/executor_transcricao_midia.py"


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding="utf-8") as fh:
        return fh.read()


def _codigo_de(rel, nome):
    """O CÓDIGO de uma função — sem comentário e sem docstring. → str.

    Herdado da prova da GPU, e pela mesma razão que ela o escreveu: procurar a
    palavra no ficheiro mede o que está ESCRITO, e a pergunta é sobre o que
    EXECUTA. `ast.unparse` deita fora comentários por construção; a docstring
    sai à mão.
    """
    for no in ast.walk(ast.parse(_fonte(rel))):
        if not isinstance(no, ast.FunctionDef) or no.name != nome:
            continue
        corpo = list(no.body)
        if (corpo and isinstance(corpo[0], ast.Expr)
                and isinstance(corpo[0].value, ast.Constant)
                and isinstance(corpo[0].value.value, str)):
            corpo = corpo[1:]
        return "\n".join(ast.unparse(x) for x in corpo)
    raise AssertionError("funcao %s nao existe em %s" % (nome, rel))


class _Mem:
    def raw_por_id(self, i):
        return {"sha256": "a" * 64, "source_country": "IT"}


#: A resposta de um reconhecedor que ouviu e acertou, com as medidas todas.
#: ⚠️ AS QUATRO ÚLTIMAS SÃO O MOTIVO DESTE FICHEIRO EXISTIR: `fala_local` já as
#: media, e o executor da BIG deitava-as fora antes do recibo.
ASR_COMPLETO = {
    "TRANSCRIPT": "una frase detta ad alta voce",
    "TRANSCRIPT_STATE": fl.OK,
    "LANGUAGE": "it",
    "LANGUAGE_SOURCE": "DETECTED",
    "LANGUAGE_CONFIDENCE": 0.94,
    "ASR_MODEL": "small",
    "ASR_ENGINE": "faster-whisper",
    "ASR_BEAM": 5,
    "ASR_DEVICE_USED": "cuda",
    "ASR_DEVICE": "cuda",
    "ASR_DEVICE_EXECUTION": "GPU",
    "AUDIO_SECONDS": 12.0,
    "MACHINE_SECONDS": 1.5,
    "ETAPA_QUE_FALHOU": None,
    "ASR_COMPUTE_SELECTED": "float16",
    "REALTIME_FACTOR": 8.0,
    "VOICED_SEGMENTS": 3,
    "NO_SPEECH_PROB_MEAN": 0.02,
}

#: O que o dono da mídia responde quando MEDIU e não há som.
FLUXOS_SEM_SOM = (1, 0, "")
#: O que ele responde quando NÃO CONSEGUIU medir. A diferença decide se se tenta.
FLUXOS_NAO_SEI = (fl.NAO_SEI, fl.NAO_SEI, "ffprobe recusou")


def _derivar(*, asr=None, fluxos=None, ha_ffmpeg=True, asr_disponivel=True,
             conferir=None):
    """Corre `derivar_um` com todos os donos falsos. → (recibo, chamadas).

    `chamadas["asr"]` conta se o reconhecedor chegou a ser chamado — é assim
    que se prova que um portão fecha ANTES do modelo, e não depois dele.
    """
    chamadas = {"asr": 0, "escreveu": 0}
    gpd = __import__("guarda.preservar_derivado", fromlist=["x"])
    orig = {"preservar": gpd.preservar_derivado,
            "transcrever": em.transcrever_ficheiro,
            "ferramenta": em.ha_ferramenta,
            "disponivel": fl.disponivel,
            "fluxos": fl.fluxos,
            "conferir": pv.conferir_unidade_de_texto}

    def _transcrever(caminho, **kw):
        chamadas["asr"] += 1
        return dict(ASR_COMPLETO if asr is None else asr)

    def _preservar(pedido, bytes_, arm, mem, relogio=None):
        chamadas["escreveu"] += 1
        return {"ESTADO": "ESCRITO", "PEDIDO": pedido, "BYTES": len(bytes_)}

    gpd.preservar_derivado = _preservar
    em.transcrever_ficheiro = _transcrever
    em.ha_ferramenta = lambda: ha_ffmpeg
    fl.disponivel = lambda: (asr_disponivel,
                             "" if asr_disponivel else "reconhecedor ausente")
    if fluxos is not None:
        fl.fluxos = lambda c: fluxos
    if conferir is not None:
        pv.conferir_unidade_de_texto = conferir
    try:
        return em.derivar_um(1, "x.mp4", None, _Mem()), chamadas
    finally:
        gpd.preservar_derivado = orig["preservar"]
        em.transcrever_ficheiro = orig["transcrever"]
        em.ha_ferramenta = orig["ferramenta"]
        fl.disponivel = orig["disponivel"]
        fl.fluxos = orig["fluxos"]
        pv.conferir_unidade_de_texto = orig["conferir"]


# ═════════════════════════════════════════════════════════════════════════════
class AProvenienciaVemDoDono(unittest.TestCase):
    """§7.1 · §7.3 · §7.15 — o vocabulário tem um dono, e é ele quem monta."""

    def test_a_unidade_emitida_nasce_do_construtor_do_dono(self):
        """⚠️ ERA A ÚNICA VIOLAÇÃO DE CONTRATO DAS DUAS IMPLEMENTAÇÕES.

        REESCRITO de `test_o_vocabulario_vem_do_DONO_e_nao_de_literais`: aquele
        exigia a string `pv.TRANSCRIPT` no corpo. Este pergunta pela unidade
        que SAI — e uma unidade com a forma do dono não se monta à mão por
        acidente.
        """
        r, _ = _derivar()
        self.assertIn("TEXT_UNIT", r, "o recibo nao leva a unidade de texto")
        u = r["TEXT_UNIT"]
        modelo = pv.unidade_de_texto(
            texto="x", kind=pv.TRANSCRIPT, kind_basis=pv.PRODUCED_BY_LOCAL_ASR,
            relation=pv.ORIGINAL, language="it", raw_observation_id=1,
            derivation_method=pv.ASR_DA_CASA, unit_id="TU-x-1",
            tool="faster-whisper", model="small")
        self.assertEqual(set(u), set(modelo),
                         "a unidade nao tem a forma que o dono produz")
        self.assertEqual(u["TEXT_KIND"], pv.TRANSCRIPT)
        self.assertEqual(u["TEXT_RELATION"], pv.ORIGINAL)
        self.assertEqual(u["TEXT_KIND_BASIS"], pv.PRODUCED_BY_LOCAL_ASR)

    def test_o_kind_e_a_relacao_pertencem_as_listas_fechadas_do_dono(self):
        """REESCRITO de `test_o_metodo_de_derivacao_esta_na_lista_fechada` e de
        `test_o_kind_continua_na_lista_fechada_da_022`, agora sobre a unidade
        REAL e não sobre a constante do módulo."""
        r, _ = _derivar()
        u = r["TEXT_UNIT"]
        self.assertIn(u["TEXT_KIND"], pv.TEXT_KINDS)
        self.assertIn(u["TEXT_RELATION"], pv.TEXT_RELATIONS)
        self.assertIn(u["LINEAGE"]["DERIVATION_METHOD"], pv.METODOS_DE_DERIVACAO)
        self.assertEqual(u["LINEAGE"]["DERIVATION_METHOD"], "LOCAL_ASR")
        # E o validador do dono aceita-a — a prova que ele faz, feita aqui.
        self.assertEqual(pv.conferir_unidade_de_texto(u), [])

    def test_a_especie_do_derivado_continua_na_lista_fechada_da_022(self):
        """MANTIDO da prova original — a 022 tem sete valores, e um já era
        `TRANSCRIPTION`, com o comentário «whisper sobre audio» ao lado."""
        sql = _fonte("supabase/migrations/022_o_derivado_ganha_casa.sql")
        i = sql.index("kind            text not null check (kind in (")
        bloco = sql[i:i + 400]
        self.assertIn("'%s'" % em.KIND, bloco)
        self.assertNotIn("AUDIO_TRANSCRIPTION", bloco)

    def test_nenhuma_identidade_e_inventada_em_silencio(self):
        """§7.15 — REESCRITO de `test_T9_source_id…`, que lia a DOCSTRING.

        A pergunta não é «a palavra aparece no ficheiro?», é «a unidade e a
        receita que saem contêm identidade que o executor não recebeu?».
        """
        r, _ = _derivar()
        pedido = r["PEDIDO"]
        self.assertNotIn("SOURCE_ID", pedido)
        self.assertNotIn("source_id", pedido)
        self.assertEqual(pedido["raw_asset_id"], 1, "o pai veio de fora")
        self.assertEqual(r["TEXT_UNIT"]["LINEAGE"]["RAW_OBSERVATION_ID"], 1)
        # E o sha do pai continua a ser do dono da escrita, nunca deste.
        corpo = _codigo_de(FICHEIRO, "derivar_um")
        for proibido in ("sha256", "hashlib"):
            self.assertNotIn(proibido, corpo)


# ═════════════════════════════════════════════════════════════════════════════
class UnidadeRecusadaNaoESucesso(unittest.TestCase):
    """§7.2 · §7.4 · §7.5 — o dono confere ANTES, e a recusa tem nome próprio."""

    @staticmethod
    def _recusa_tudo(_u):
        return ["METHOD_NOT_IN_CLOSED_LIST"]

    def test_o_dono_confere_antes_de_qualquer_byte_ser_escrito(self):
        """§7.2 — e a ordem é o ponto: o validador serve para apanhar a unidade
        inválida ENQUANTO ainda não se escreveu nada no armazém."""
        r, ch = _derivar(conferir=self._recusa_tudo)
        self.assertEqual(ch["escreveu"], 0,
                         "escreveu no armazem apesar de a unidade ser invalida")
        self.assertEqual(r["ESTADO"], "SEM_DERIVADO")

    def test_a_recusa_do_dono_tem_motivo_proprio(self):
        """§7.4 — `ASR_FALHOU != CONTENT_REJECTED != UNIDADE_RECUSADA`."""
        r, _ = _derivar(conferir=self._recusa_tudo)
        self.assertEqual(r["MOTIVO_DO_EXECUTOR"], em.UNIDADE_RECUSADA)
        self.assertNotEqual(r["MOTIVO_DO_EXECUTOR"], fl.ASR_INDISPONIVEL)
        self.assertIn("METHOD_NOT_IN_CLOSED_LIST", r["ERRO"])

    def test_a_recusa_nao_se_disfarca_de_sucesso(self):
        """§7.5 — e diz por extenso o que NÃO significa."""
        r, _ = _derivar(conferir=self._recusa_tudo)
        self.assertNotIn("TEXT_UNIT", r)
        self.assertNotEqual(r.get("ESTADO"), "ESCRITO")
        self.assertIn("NAO_SIGNIFICA", r)
        self.assertIn("nao tem fala", r["NAO_SIGNIFICA"].lower())

    def test_a_recusa_leva_as_medidas_do_que_correu(self):
        """Um fracasso sem medidas não se distingue de um fracasso de outra
        causa — e aqui o reconhecedor CORREU."""
        r, ch = _derivar(conferir=self._recusa_tudo)
        self.assertEqual(ch["asr"], 1)
        self.assertEqual(r["MEDIDAS"]["REALTIME_FACTOR"], 8.0)


# ═════════════════════════════════════════════════════════════════════════════
class OsPortoesFechamAntesDoModelo(unittest.TestCase):
    """§7.6 · §7.7 · §7.8 — carregar o modelo é caro, e alguns «nãos» são de graça."""

    def test_sem_ffmpeg_nao_se_chama_o_reconhecedor(self):
        """§7.7 — o portão que só a BIG tinha. FERRAMENTA QUE FALTA NÃO É
        DOCUMENTO QUEBRADO (`COL-LAW-503`)."""
        r, ch = _derivar(ha_ffmpeg=False)
        self.assertEqual(ch["asr"], 0, "tentou transcrever sem ffmpeg")
        self.assertEqual(r["ESTADO"], "SEM_DERIVADO")
        self.assertEqual(r["MOTIVO_DO_EXECUTOR"], fl.ASR_INDISPONIVEL)
        self.assertIn("ffmpeg", r["PORQUE"])
        self.assertIn("nao tem fala", r["NAO_SIGNIFICA"].lower())

    def test_sem_reconhecedor_instalado_tambem_nao_se_tenta(self):
        r, ch = _derivar(asr_disponivel=False)
        self.assertEqual(ch["asr"], 0)
        self.assertEqual(r["MOTIVO_DO_EXECUTOR"], fl.ASR_INDISPONIVEL)

    def test_contentor_sem_faixa_de_som_para_antes_do_modelo(self):
        """§7.6 — REESCRITO de `test_ficheiro_sem_faixa_de_som_e_facto_do_ORIGINAL`.

        Aquele exigia a função `tem_faixa_de_som` pelo nome. Este mede o
        COMPORTAMENTO: com o dono da mídia a dizer «medi e não há som», o
        reconhecedor não pode ser chamado.
        """
        r, ch = _derivar(fluxos=FLUXOS_SEM_SOM)
        self.assertEqual(ch["asr"], 0, "pagou o modelo para saber o que o "
                                       "contentor dizia de graca")
        self.assertEqual(r["MOTIVO_DO_EXECUTOR"], "SEM_FAIXA_DE_AUDIO")
        self.assertIn(r["MOTIVO_DO_EXECUTOR"], df.DESTINO_DO_MOTIVO)

    def test_nao_conseguir_medir_nao_autoriza_concluir_que_nao_ha_som(self):
        """§7.8 — REESCRITO de `test_nao_medir_nao_autoriza_concluir…`, que
        chamava `em.tem_faixa_de_som(x, _Mudo)` com injecção da GPU.

            NAO CONSEGUI VER != VI QUE NAO HA.
        """
        r, ch = _derivar(fluxos=FLUXOS_NAO_SEI)
        self.assertEqual(ch["asr"], 1, "ausencia de medicao virou ausencia de som")
        self.assertEqual(r["ESTADO"], "ESCRITO")
        ok, porque = em.tem_fala_possivel("x")
        self.assertTrue(ok)
        self.assertIn("ausencia de medicao", porque)

    def test_a_pergunta_dos_fluxos_vai_ao_DONO_da_midia(self):
        """MANTIDO — porta-se a ideia, não o código: um segundo `ffprobe` seria
        um segundo dono da mesma pergunta."""
        corpo = _codigo_de(FICHEIRO, "tem_fala_possivel")
        self.assertIn("fl.fluxos", corpo)
        for proibido in ("subprocess", "Popen", "shutil.which"):
            self.assertNotIn(proibido, corpo)


# ═════════════════════════════════════════════════════════════════════════════
class AsMedidasQueOExecutorTransporta(unittest.TestCase):
    """§7.9 a §7.12 · §7.13 — o dono mede, e o recibo tem de levar."""

    #: As quatro que `fala_local` media e a BIG deitava fora.
    PORTADAS = ("ASR_COMPUTE_SELECTED", "REALTIME_FACTOR",
                "VOICED_SEGMENTS", "NO_SPEECH_PROB_MEAN")

    def test_as_quatro_medidas_portadas_chegam_ao_recibo(self):
        r, _ = _derivar()
        for campo in self.PORTADAS:
            with self.subTest(campo=campo):
                self.assertIn(campo, r["MEDIDAS"])
                self.assertEqual(r["MEDIDAS"][campo], ASR_COMPLETO[campo])

    def test_o_dono_do_ASR_realmente_produz_estas_quatro(self):
        """Elas não foram inventadas por esta união: existem em `fala_local`."""
        fonte = _fonte("ferramentas/fala_local.py")
        for campo in self.PORTADAS:
            with self.subTest(campo=campo):
                self.assertIn(campo, fonte)

    def test_nao_medir_nao_vira_zero(self):
        """⚠️ `REALTIME_FACTOR = 0` diria «correu infinitamente rápido».
        `None` diz «não se mediu». São factos opostos."""
        magro = {k: v for k, v in ASR_COMPLETO.items()
                 if k not in self.PORTADAS}
        r, _ = _derivar(asr=magro)
        for campo in self.PORTADAS:
            with self.subTest(campo=campo):
                self.assertIsNone(r["MEDIDAS"][campo])

    def test_o_fracasso_mede_se_com_a_mesma_regua_do_sucesso(self):
        """Antes da união, o caminho de falha levava cinco campos escolhidos à
        mão — e comparar as duas corridas era comparar vocabulários."""
        falhou = dict(ASR_COMPLETO, TRANSCRIPT=None,
                      TRANSCRIPT_STATE="REQUESTED_EMPTY",
                      ETAPA_QUE_FALHOU="ASR")
        r, _ = _derivar(asr=falhou)
        self.assertEqual(r["ESTADO"], "SEM_DERIVADO")
        for campo in self.PORTADAS:
            self.assertIn(campo, r["MEDIDAS"])
        self.assertEqual(r["MEDIDAS"]["ETAPA_QUE_FALHOU"], "ASR")

    def test_FFMPEG_PRESENTE_continua_no_olhar_seco(self):
        """§7.13 — capacidade da BIG, e não se perdeu na união."""
        self.assertIn("FFMPEG_PRESENTE", _codigo_de(FICHEIRO, "_seco"))

    def test_a_medida_da_maquina_nao_entra_na_identidade_do_artefato(self):
        """O que varia entre duas corridas iguais não é identidade: é medida.
        Se `MACHINE_SECONDS` entrasse na receita, a mesma mídia transcrita duas
        vezes pareceria dois artefatos."""
        r, _ = _derivar()
        params = r["PEDIDO"]["parameters"]
        for medida in ("MACHINE_SECONDS", "REALTIME_FACTOR", "AUDIO_SECONDS",
                       "VOICED_SEGMENTS", "NO_SPEECH_PROB_MEAN"):
            self.assertNotIn(medida, params)
        # E o que MUDA O TEXTO continua na identidade.
        for identidade in ("ASR_MODEL", "ASR_ENGINE", "LANGUAGE"):
            self.assertIn(identidade, params)


# ═════════════════════════════════════════════════════════════════════════════
class OContratoDaBaseNaoRegride(unittest.TestCase):
    """§7.14 — a união não pode ter custado nada à forma que a BIG já tinha."""

    def test_derivar_um_mantem_a_forma_do_irmao_de_PDF(self):
        """DOIS EXECUTORES COM A MESMA FORMA SÃO UM PONTO DE ESCOLHA.
        DOIS COM FORMAS DIFERENTES SÃO DOIS CAMINHOS, E AÍ ALGUÉM ESCREVE O `if`.

        ⚠️ A PROVA É SOBRE A POSIÇÃO, NÃO SOBRE O NOME. O segundo parâmetro
        chama-se `midia` aqui e `pdf` lá, de propósito — é o que cada um é. O
        que `derivacao_forward.correr()` precisa é que a POSIÇÃO coincida, para
        poder chamar os dois sem saber qual tem na mão. A primeira versão deste
        teste comparava os nomes e reprovava a própria regra que queria provar.
        """
        a = list(inspect.signature(em.derivar_um).parameters)
        b = list(inspect.signature(pdf.derivar_um).parameters)
        self.assertEqual(len(a), len(b), "as duas pontes deixaram de ter a "
                                         "mesma aridade")
        self.assertEqual(a[0], b[0])
        self.assertEqual(a[2:], b[2:], "so o segundo parametro pode diferir "
                                       "no nome, e so no nome")
        self.assertEqual(a[1], "midia")

    def test_a_ponte_continua_a_ter_as_pecas_que_a_BIG_declarava(self):
        for nome in ("ha_ferramenta", "transcrever_ficheiro",
                     "tem_fala_possivel", "aceita", "derivar_um", "_seco"):
            with self.subTest(peca=nome):
                self.assertTrue(callable(getattr(em, nome, None)))

    def test_o_executor_continua_sem_escrever_no_banco(self):
        corpo = _codigo_de(FICHEIRO, "derivar_um")
        for proibido in ("psycopg", "insert into", "cursor", "commit(",
                         "execute("):
            self.assertNotIn(proibido, corpo.lower())
        self.assertIn("preservar_derivado", corpo)

    def test_o_executor_continua_sem_duplicar_o_reconhecedor(self):
        """RT3 — `fala_local` é o dono único de FALA -> TEXTO."""
        fonte = _fonte(FICHEIRO)
        for proibido in ("WhisperModel(", "BatchedInferencePipeline(",
                         "faster_whisper", "compute_type="):
            self.assertNotIn(proibido, fonte)
        self.assertIn("import fala_local", fonte)

    def test_o_dono_do_ASR_nao_foi_alterado_pela_uniao(self):
        """`fala_local` é infraestrutura partilhada — a dependência é numa
        direcção só."""
        self.assertNotIn("executor_transcricao_midia",
                         _fonte("ferramentas/fala_local.py"))

    def test_o_wav_intermedio_nao_vira_derivado(self):
        """MANTIDO de `test_o_wav_nasce_e_morre_numa_pasta_temporaria`, sem o
        `shutil.rmtree` que era forma da GPU: aqui a limpeza é `os.remove` +
        `os.rmdir` num `finally`."""
        fonte = _fonte(FICHEIRO)
        self.assertIn("tempfile.mkdtemp", fonte)
        corpo = _codigo_de(FICHEIRO, "transcrever_ficheiro")
        self.assertIn("finally", _fonte(FICHEIRO)[
            _fonte(FICHEIRO).index("def transcrever_ficheiro"):])
        self.assertIn("os.remove", corpo)
        self.assertIn('"media_type": "text/plain"', fonte)
        self.assertNotIn('"media_type": "audio', fonte)


# ═════════════════════════════════════════════════════════════════════════════
class OQueJaEProvadoNoutroSitio(unittest.TestCase):
    """As exigências da prova da GPU que `test_c4h_ponte_de_midia.py` já cobre.

    ⚠️ ESTA CLASSE NÃO É DECORAÇÃO. Ela falha se o ficheiro que assume a
    cobertura deixar de existir ou perder o teste que a sustenta — que é
    exactamente o risco de delegar cobertura por nota de rodapé.
    """

    #: exigência original da GPU  ->  teste da BIG que a prova
    DELEGADAS = {
        "test_T1_video_mp4_escolhe_o_executor_de_midia":
            "test_T1_video_mp4_vai_ao_executor_de_midia",
        "test_T2_audio_escolhe_o_executor_de_midia":
            "test_T2_audio_vai_ao_executor_de_midia",
        "test_T3_pdf_continua_a_escolher_o_executor_de_pdf":
            "test_T3_pdf_continua_a_ir_ao_executor_de_pdf",
        "test_T4_o_declarado_vence_a_extensao":
            "test_T5_o_tipo_com_parametros_ainda_e_o_tipo",
        "test_T5_ficheiro_chamado_pdf_com_especie_de_video_nao_vai_ao_pdf":
            "test_T4_nenhuma_midia_chega_ao_pdftotext",
        "test_nenhum_executor_recebe_o_que_declarou_nao_aceitar":
            "test_T5c_especie_declarada_e_nao_suportada_nao_deriva",
        "test_a_porta_conhece_mais_do_que_um":
            "test_a_ficha_declara_o_que_aceita_e_o_que_produz",
        "test_T6_o_produto_e_TRANSCRIPT_e_a_especie_do_derivado_e_TRANSCRIPTION":
            "test_T6_o_que_sai_e_TRANSCRIPT",
        "test_T7_caption_nunca_e_rebatizada_transcript":
            "test_T7_caption_nunca_vira_transcript",
        "test_T8_a_lingua_vem_da_evidencia_e_nao_do_pais":
            "test_T8_a_lingua_detectada_viaja_com_a_fonte_dela",
        "test_a_traducao_nao_substitui_o_original":
            "test_T8b_a_lingua_NAO_e_inferida_do_pais_nem_do_caminho",
        "test_T10_o_executor_nao_inventa_raw_asset_id":
            "test_T9_o_executor_nao_inventa_RAW_ASSET_ID",
        "test_T16_o_sha_nao_e_usado_como_identidade_da_observacao":
            "test_T10_o_sha_nao_vira_identidade_de_observacao",
        "test_T9_source_id_desconhecido_continua_desconhecido":
            "test_T11_SOURCE_ID_nao_nasce_de_caminho",
        "test_T11_o_executor_nao_escreve_no_banco":
            "test_T12_o_executor_nao_escreve_no_banco",
        "test_o_executor_nao_duplica_o_reconhecedor":
            "test_T12b_o_ASR_tem_um_dono_so",
        "test_o_executor_de_midia_nao_conhece_youtube":
            "test_T12c_a_ponte_nao_conhece_plataforma_nenhuma",
        "test_T12_falha_de_ASR_e_ERROR_e_nunca_REJECTED":
            "test_T13_erro_do_ASR_nao_e_recusa_de_conteudo",
        "test_T13_audio_sem_texto_nao_vira_ausencia_de_fala":
            "test_T13b_sem_faixa_de_som_e_facto_sobre_o_original",
        "test_todo_motivo_declarado_tem_destino":
            "test_T13c_nao_conseguir_medir_nao_e_nao_ter_som",
        "test_T14_o_dono_da_escrita_e_que_decide_reuso":
            "test_a_unidade_carrega_a_especie",
    }

    def test_o_ficheiro_que_assume_a_cobertura_existe(self):
        self.assertTrue(os.path.isfile(
            os.path.join(RAIZ, "tests", "test_c4h_ponte_de_midia.py")))

    def test_cada_exigencia_delegada_tem_teste_vivo_do_outro_lado(self):
        fonte = _fonte("tests/test_c4h_ponte_de_midia.py")
        nomes = {n.name for n in ast.walk(ast.parse(fonte))
                 if isinstance(n, ast.FunctionDef)}
        for origem, destino in sorted(self.DELEGADAS.items()):
            with self.subTest(exigencia=origem):
                self.assertIn(destino, nomes,
                              "a cobertura de %s desapareceu" % origem)


# ═════════════════════════════════════════════════════════════════════════════
class OQueFicouBloqueado(unittest.TestCase):
    """⚠️ UMA EXIGÊNCIA DA GPU NÃO ENTROU, E NÃO SE APAGA POR ISSO.

    `test_familias_NAO_foram_portadas` exigia que a ficha declarasse uma LISTA
    EXACTA de `media_type` e que `FAMILIAS` não existisse. A BIG declara-se por
    FAMÍLIA (`audio`, `video`), com a razão escrita no próprio executor:

        UMA LISTA QUE PRECISA DE SER COMPLETA PARA ESTAR CERTA
        ESTÁ ERRADA NO DIA SEGUINTE.

    As duas posições são defensáveis e **contradizem-se**. A base desta união é
    a BIG (§3 da missão 4B2), logo a família fica. Este teste guarda o preço
    dessa escolha, em vez de o esconder: a declaração é larga, e quem estreita
    de verdade é a MEDIÇÃO, não a ficha.
    """

    def test_a_familia_e_larga_e_isso_esta_declarado(self):
        self.assertIn("ACEITA_FAMILIAS", em.CAPACIDADE)
        self.assertTrue(em.aceita("audio/x-inventado"),
                        "a familia deixou de aceitar o que a GPU temia — se "
                        "isto passar a False, a objeccao dela foi resolvida "
                        "e este teste tem de ser reescrito")

    def test_quem_estreita_de_verdade_e_a_medicao_e_nao_a_ficha(self):
        """O preço da família é pago aqui: um `audio/x-inventado` sem faixa de
        som não chega ao modelo, porque quem decide é o `ffprobe`."""
        r, ch = _derivar(fluxos=FLUXOS_SEM_SOM)
        self.assertEqual(ch["asr"], 0)
        self.assertEqual(r["MOTIVO_DO_EXECUTOR"], "SEM_FAIXA_DE_AUDIO")


if __name__ == "__main__":
    unittest.main(verbosity=2)
