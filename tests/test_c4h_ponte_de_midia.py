#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C4H — a ponte generica de midia: escolha, contrato do texto e os «nao».

    py -m unittest tests.test_c4h_ponte_de_midia

O QUE ESTES TESTES SAO, E O QUE ELES NAO SUBSTITUEM
----------------------------------------------------
Sao rapidos e nao chamam o reconhecedor de verdade: onde precisam de uma
transcricao, injectam um duplo. Isso prova a LIGACAO e o CONTRATO.

    NAO provam que o ASR ouve bem — isso e de `provas/a_ponte_de_midia_atravessa.py`,
    que corre o video real e demora ~29 s.
    NAO provam nada sobre o banco — isso exige Postgres, e esta maquina nao tem.

    UM TESTE RAPIDO QUE FINGE SER O LENTO E PIOR QUE NENHUM DOS DOIS.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
import ingresso as ing                             # noqa: E402
import executor_transcricao_midia as midia         # noqa: E402
import executor_texto_de_pdf as pdf                # noqa: E402
import derivacao_forward as deriv                  # noqa: E402
import proveniencia as pv                          # noqa: E402


class AEscolhaDoExecutor(unittest.TestCase):
    """T1 · T2 · T3 · T4 · T5 — quem abre o quê, e quem NUNCA abre o quê."""

    def test_T1_video_mp4_vai_ao_executor_de_midia(self):
        self.assertEqual(ing.executor_para("video/mp4").EXECUTOR_ID,
                         midia.EXECUTOR_ID)

    def test_T2_audio_vai_ao_executor_de_midia(self):
        for tipo in ("audio/mpeg", "audio/mp4", "audio/wav", "audio/ogg",
                     "audio/x-m4a", "audio/flac"):
            with self.subTest(tipo=tipo):
                self.assertEqual(ing.executor_para(tipo).EXECUTOR_ID,
                                 midia.EXECUTOR_ID)

    def test_T3_pdf_continua_a_ir_ao_executor_de_pdf(self):
        """A REGRESSAO QUE MAIS IMPORTA: o caminho antigo nao se mexeu."""
        self.assertEqual(ing.executor_para("application/pdf").EXECUTOR_ID,
                         pdf.EXECUTOR_ID)

    def test_T4_nenhuma_midia_chega_ao_pdftotext(self):
        for tipo in ("video/mp4", "video/webm", "video/quicktime",
                     "audio/mpeg", "audio/flac"):
            with self.subTest(tipo=tipo):
                self.assertNotEqual(
                    getattr(ing.executor_para(tipo), "EXECUTOR_ID", None),
                    pdf.EXECUTOR_ID,
                    "midia encaminhada ao extrator de PDF: %s" % tipo)

    def test_T5_o_tipo_com_parametros_ainda_e_o_tipo(self):
        """`video/mp4; codecs=avc1` e um media_type legitimo.

        Um `==` cru falharia aqui — e falharia em silencio, mandando o video
        ao executor errado por causa de um ponto e virgula.
        """
        self.assertEqual(
            ing.executor_para('video/mp4; codecs="avc1.4d401e"').EXECUTOR_ID,
            midia.EXECUTOR_ID)

    def test_T5b_especie_nao_declarada_nao_encolhe_a_coleta(self):
        """AUSENCIA DE EVIDENCIA NAO E EVIDENCIA DE AUSENCIA.

        A porta deixa TENTAR quando nao ha especie; a escolha responde `None`,
        que quer dizer «nenhum executor a declara» — nunca «falhou».
        """
        self.assertTrue(ing._quem_deriva_aceita(None))
        self.assertIsNone(ing.executor_para(None))
        self.assertIsNone(ing.executor_para("NAO SEI"))

    def test_T5c_especie_declarada_e_nao_suportada_nao_deriva(self):
        self.assertFalse(ing._quem_deriva_aceita("application/json"))
        self.assertIsNone(ing.executor_para("application/json"))


class OContratoDoTexto(unittest.TestCase):
    """T6 · T7 · T8 — o que sai daqui tem espécie, e ela não se confunde."""

    def test_T6_o_que_sai_e_TRANSCRIPT(self):
        self.assertEqual(midia.TEXT_KIND, pv.TRANSCRIPT)
        self.assertEqual(midia.TEXT_RELATION, pv.ORIGINAL)

    def test_T7_caption_nunca_vira_transcript(self):
        """CAPTION e o que a PLATAFORMA publicou. TRANSCRIPT e o que esta casa
        produziu ouvindo. Sao graus de prova diferentes."""
        self.assertNotEqual(midia.TEXT_KIND, pv.NATIVE_CAPTION)
        self.assertEqual(midia.TEXT_BASIS, pv.PRODUCED_BY_LOCAL_ASR)
        self.assertNotEqual(midia.TEXT_BASIS, pv.DECLARED_BY_PROVIDER)

    def test_T8_a_lingua_detectada_viaja_com_a_fonte_dela(self):
        """O campo nao e so `it`: e `it` MAIS de onde veio esse `it`.

        Sem `LANGUAGE_SOURCE`, «eu declarei» e «a maquina achou» ficam
        indistinguiveis — e sao graus de prova diferentes.
        """
        recibo = self._derivar_com_asr_falso(
            {"TRANSCRIPT": "ciao", "TRANSCRIPT_STATE": "OK",
             "LANGUAGE": "it", "LANGUAGE_SOURCE": "DETECTED",
             "LANGUAGE_CONFIDENCE": 0.98, "ASR_MODEL": "small"})
        self.assertEqual(recibo["LANGUAGE"], "it")
        self.assertEqual(recibo["LANGUAGE_SOURCE"], "DETECTED")
        self.assertEqual(recibo["TEXT_KIND"], pv.TRANSCRIPT)

    def test_T8b_a_lingua_NAO_e_inferida_do_pais_nem_do_caminho(self):
        """O executor chama o dono do ASR com `idioma=None`.

        PAIS e de onde a fonte e; LINGUA e o que se ouve. `COL-LAW-040`.
        """
        vistos = {}

        def falso(wav, **kw):
            vistos.update(kw)
            return {"TRANSCRIPT": "hello", "TRANSCRIPT_STATE": "OK",
                    "LANGUAGE": "en", "LANGUAGE_SOURCE": "DETECTED",
                    "LANGUAGE_CONFIDENCE": 0.9}

        self._com_duplos(transcrever=falso, corpo=lambda: midia.transcrever_ficheiro(
            self._midia_falsa()))
        self.assertIsNone(vistos.get("idioma"),
                          "a ponte declarou uma lingua que ninguem provou")

    # ── auxiliares ───────────────────────────────────────────────────────
    def _midia_falsa(self):
        import tempfile
        f = os.path.join(tempfile.mkdtemp(prefix="c4h-"), "x.mp4")
        with open(f, "wb") as h:
            h.write(b"\x00" * 4096)
        return f

    def _com_duplos(self, *, transcrever, corpo, extrair=None):
        fl = midia.fl
        orig = (fl.transcrever, fl.extrair_audio, fl.duracao)

        def _extrair(entrada, wav):
            with open(wav, "wb") as h:
                h.write(b"\x00" * 2048)
            return wav, None

        fl.transcrever = transcrever
        fl.extrair_audio = extrair or _extrair
        fl.duracao = lambda c: 1.0
        try:
            return corpo()
        finally:
            fl.transcrever, fl.extrair_audio, fl.duracao = orig

    def _derivar_com_asr_falso(self, resposta):
        return self._com_duplos(
            transcrever=lambda wav, **kw: dict(resposta),
            corpo=lambda: _derivar(self._midia_falsa(), resposta))


def _codigo_sem_prosa(caminho):
    """O ficheiro sem comentários e sem literais de texto. → str.

    ⚠️ ESTE AUXILIAR NASCEU DE UM ERRO MEU, E O ERRO VALE REGISTAR.
    A primeira versão destes testes fazia `assertNotIn("youtube", fonte)` sobre
    o ficheiro inteiro — e reprovava, porque a DOCSTRING do executor diz, por
    escrito, que ele não conhece o YouTube. O teste estava a apanhar a frase
    que promete a regra, em vez do código que a cumpre.

        UM TESTE QUE LÊ A PROSA ESTÁ A VERIFICAR A PROMESSA, NÃO O FACTO.

    `tokenize` deixa cair `COMMENT` e `STRING`, e o que sobra é só o que corre.
    """
    import io as _io
    import tokenize
    fonte = open(caminho, encoding="utf-8").read()
    pedacos = []
    try:
        for tok in tokenize.generate_tokens(_io.StringIO(fonte).readline):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                continue
            pedacos.append(tok.string)
    except tokenize.TokenError:                                # pragma: no cover
        return fonte
    return " ".join(pedacos)


class OsNaosDoExecutor(unittest.TestCase):
    """T9 · T10 · T11 · T12 — o que esta peça está proibida de saber."""

    def test_T9_o_executor_nao_inventa_RAW_ASSET_ID(self):
        """Ele RECEBE o pai. Não o procura, não o deduz, não o cria.

        A prova é de forma: `derivar_um` exige `raw_asset_id` como primeiro
        parâmetro posicional, e não há caminho no ficheiro que o produza.
        """
        import inspect
        p = list(inspect.signature(midia.derivar_um).parameters)
        self.assertEqual(p[0], "raw_asset_id")
        codigo = _codigo_sem_prosa(midia.__file__)
        for proibido in ("uuid", "novo_raw", "gerar_id"):
            self.assertNotIn(proibido, codigo,
                             "o executor parece fabricar identidade: %s" % proibido)

    def test_T10_o_sha_nao_vira_identidade_de_observacao(self):
        """O executor não calcula sha nenhum — nem do pai nem do filho."""
        codigo = _codigo_sem_prosa(midia.__file__)
        self.assertNotIn("sha256", codigo)
        self.assertNotIn("hashlib", codigo)

    def test_T11_SOURCE_ID_nao_nasce_de_caminho(self):
        """O executor nem sequer tem a palavra no código que corre."""
        codigo = _codigo_sem_prosa(midia.__file__)
        self.assertNotIn("SOURCE_ID", codigo)
        self.assertNotIn("source_id", codigo)

    def test_T12_o_executor_nao_escreve_no_banco(self):
        """Ele entrega a receita ao dono da escrita. Não conhece SQL."""
        # ⚠️ `insert` NÃO está nesta lista, e a razão vale ficar escrita:
        # `sys.path.insert` apanhava-o, e um teste que reprova por causa de uma
        # linha de `import` não está a medir acesso a banco — está a medir
        # coincidência de letras.
        #
        #     UMA PALAVRA PROIBIDA QUE TAMBÉM É UMA PALAVRA COMUM
        #     NÃO É UMA TRAVA: É UM ALARME FALSO COM HORA MARCADA.
        codigo = _codigo_sem_prosa(midia.__file__).lower()
        for proibido in ("psycopg", "supabase", "commit", "cursor",
                         "executemany", "sqlite3", "memoriadoderivado"):
            self.assertNotIn(proibido, codigo)
        # E a prova positiva: quem escreve é o dono, e ele é chamado por nome.
        self.assertIn("preservar_derivado", codigo)

    def test_T12b_o_ASR_tem_um_dono_so(self):
        """A ponte não implementa reconhecimento: ela chama quem o faz."""
        codigo = _codigo_sem_prosa(midia.__file__)
        self.assertNotIn("WhisperModel", codigo)
        self.assertNotIn("faster_whisper", codigo)
        self.assertEqual(midia.CAPACIDADE["ASR_OWNER"],
                         "ferramentas/fala_local.py")

    def test_T12c_a_ponte_nao_conhece_plataforma_nenhuma(self):
        """⚠️ A FRONTEIRA DESTA MISSAO, E ELA E VERIFICAVEL.

        Uma ponte que soubesse de onde o byte veio seria uma ponte por
        plataforma — e aí seriam cinco, divergindo em silêncio.

        A verificação é sobre o CÓDIGO: a docstring do executor NOMEIA as
        plataformas de propósito, para dizer que as trata a todas por igual.
        """
        codigo = _codigo_sem_prosa(midia.__file__).lower()
        for plataforma in ("youtube", "instagram", "tiktok", "linkedin",
                           "facebook", "yt_dlp", "youtubei"):
            self.assertNotIn(plataforma, codigo,
                             "a ponte generica nomeia uma plataforma: %s"
                             % plataforma)


class OErroDoReconhecedor(unittest.TestCase):
    """T13 — ASR_FAILED != CONTENT_REJECTED != CONTENT_ABSENT."""

    def test_T13_erro_do_ASR_nao_e_recusa_de_conteudo(self):
        fl = midia.fl
        orig = fl.disponivel
        fl.disponivel = lambda: (False, "faster-whisper nao instalado")
        try:
            r = midia.derivar_um(1, "x.mp4", None, None)
        finally:
            fl.disponivel = orig
        self.assertEqual(r["ESTADO"], "SEM_DERIVADO")
        self.assertEqual(r["MOTIVO_DO_EXECUTOR"], fl.ASR_INDISPONIVEL)
        self.assertIn("nao esta aqui", r["NAO_SIGNIFICA"])
        # E NAO e nenhuma destas coisas:
        self.assertNotIn("REJECTED", str(r))
        self.assertNotIn("CONTENT_ABSENT", str(r))

    def test_T13b_sem_faixa_de_som_e_facto_sobre_o_original(self):
        """Um MP4 mudo existe, e não é ficheiro partido."""
        orig = midia.fl.fluxos
        midia.fl.fluxos = lambda c: (1, 0, None)
        try:
            tem, porque = midia.tem_fala_possivel("x.mp4")
        finally:
            midia.fl.fluxos = orig
        self.assertFalse(tem)
        self.assertIn("nao ha faixa de som", porque)

    def test_T13c_nao_conseguir_medir_nao_e_nao_ter_som(self):
        """NAO CONSEGUI VER != VI QUE NAO HA — e a diferença manda tentar."""
        orig = midia.fl.fluxos
        midia.fl.fluxos = lambda c: (midia.fl.NAO_SEI, midia.fl.NAO_SEI,
                                     "ffprobe recusou")
        try:
            tem, porque = midia.tem_fala_possivel("x.mp4")
        finally:
            midia.fl.fluxos = orig
        self.assertTrue(tem, "uma medicao falhada virou ausencia de som")
        self.assertIn("ausencia de medicao nao e ausencia de som", porque)


class ORunnerDespacha(unittest.TestCase):
    """A escolha acontece por UNIDADE, e o rastro diz quem correu."""

    def test_o_ator_do_rastro_e_quem_correu(self):
        self.assertEqual(deriv._ator_da_corrida([midia]), midia.EXECUTOR_ID)
        self.assertEqual(deriv._ator_da_corrida([pdf]), pdf.EXECUTOR_ID)

    def test_corrida_mista_nao_elege_um_vencedor(self):
        """UM CAMPO QUE SO CABE UM NOME NAO AUTORIZA A INVENTAR O VENCEDOR."""
        ator = deriv._ator_da_corrida([pdf, midia])
        self.assertTrue(ator.startswith(deriv.ATOR_MISTO))
        self.assertIn(pdf.EXECUTOR_ID, ator)
        self.assertIn(midia.EXECUTOR_ID, ator)

    def test_a_unidade_carrega_a_especie(self):
        """Sem `MEDIA_TYPE` na unidade, a escolha volta a ser pela extensão."""
        fonte = open(os.path.join(RAIZ, "coleta", "ingresso.py"),
                     encoding="utf-8").read()
        self.assertIn('"MEDIA_TYPE": o.get("MEDIA_TYPE")', fonte)


class AFichaDeCapacidade(unittest.TestCase):
    def test_a_ficha_declara_o_que_aceita_e_o_que_produz(self):
        c = midia.CAPACIDADE
        self.assertEqual(c["PRODUCES"], ["TRANSCRIPT"])
        self.assertEqual(c["NETWORK_REQUIRED"], "NO")
        self.assertEqual(tuple(c["ACEITA_FAMILIAS"]), ("audio", "video"))

    def test_a_ficha_do_pdf_nao_foi_alargada(self):
        """O executor de PDF continua a declarar UM tipo, e nenhuma familia.

        Se alguem lhe acrescentasse `ACEITA_FAMILIAS`, os dois passariam a
        disputar a mesma especie — e a ordem do `import` decidiria em silencio.
        """
        self.assertEqual(tuple(pdf.CAPACIDADE["ACEITA_MEDIA_TYPES"]),
                         ("application/pdf",))
        self.assertFalse(pdf.CAPACIDADE.get("ACEITA_FAMILIAS"))


def _derivar(caminho, resposta):
    """Chama `derivar_um` com donos de escrita falsos, so para ler o recibo."""
    class _Mem:
        def raw_por_id(self, i):
            return {"sha256": "a" * 64, "source_country": "IT"}

    import guarda.preservar_derivado as gpd
    orig = gpd.preservar_derivado
    gpd.preservar_derivado = lambda pedido, bytes_, arm, mem, relogio=None: {
        "ESTADO": "ESCRITO", "PEDIDO": pedido}
    try:
        return midia.derivar_um(1, caminho, None, _Mem())
    finally:
        gpd.preservar_derivado = orig


if __name__ == "__main__":
    unittest.main()
