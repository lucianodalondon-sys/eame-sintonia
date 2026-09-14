#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ESPÉCIE DOS BYTES SOBREVIVE À PORTA — e o vídeo deixa de ir ao extrator de PDF.

    py -m unittest tests.test_c4g_a_especie_do_video

O DEFEITO, MEDIDO COM UM FICHEIRO REAL
----------------------------------------
Um `.mp4` de 9,2 MB, italiano, já preservado nesta casa. O coletor entregava-o à
porta com a espécie declarada:

    item["CONTENT_TYPE"] = "video/mp4"

e a ficha do contrato comum nascia assim:

    CONTENT_TYPE = "NAO SEI"

porque `leis/artefato.raw_do_disco` deduzia a espécie de uma tabela de QUATRO
extensões (`.pdf .txt .json .html`) e deitava fora o que vinha declarado.

E `NAO SEI` não é neutro. `ingresso._quem_deriva_aceita` trata a ausência como
«tenta» — de propósito, e com razão:

    AUSÊNCIA DE EVIDÊNCIA NÃO É EVIDÊNCIA DE AUSÊNCIA.

Resultado: o vídeo seguia para `executor_texto_de_pdf`, e o `pdftotext` era
chamado sobre um MP4. A lei que evita isso — a porta da espécie — existia,
estava certa, e nunca recebia o dado de que precisava.

    UMA TRAVA DE ESPÉCIE COM A ESPÉCIE APAGADA A MONTANTE NÃO PROTEGE NADA:
    ELA SÓ NÃO TEM O QUE LER.

O QUE ESTAS PROVAS **NÃO** AFIRMAM
-----------------------------------
Que o vídeo passou a ser transcrito pelo caminho canónico.

⚠️ ACTUALIZADO PELA C4H. Quando este ficheiro nasceu, faltavam DUAS coisas: um
executor de áudio que a porta soubesse encontrar, e um PostgreSQL onde a
observação pudesse existir. A primeira deixou de faltar — e a trava de método
que a guardava DISPAROU, que era exactamente para o que ela servia.

A segunda continua a faltar, e por isso a estrada continua por correr:

    MODULE EXISTS != EDGE EXISTS != FLOW OBSERVED.
    PARAR DE ENTREGAR AO DONO ERRADO != ENTREGAR AO DONO CERTO.
"""
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                            # noqa: E402,F401
import artefato as art                                     # noqa: E402
import ingresso as ing                                     # noqa: E402

#: Um ficheiro que existe nesta árvore, e cuja extensão a tabela conhece. Serve
#: de corpo para a ficha; o que se mede é a ESPÉCIE, nunca o conteúdo dele.
UM_FICHEIRO = "README.md"


def _ficha(**extra):
    item = {"SOURCE_ID": "PROVA/C4G", "SOURCE_NATIVE_ID": "c4g",
            "STORAGE_LOCATION": UM_FICHEIRO, "NAME": UM_FICHEIRO}
    item.update(extra)
    return ing.ficha(item, corrida={"RUN_ID": "C4G", "STARTED_AT": art.agora()})


class T1OColetorDeclaraEAPortaLeva(unittest.TestCase):

    def test_a_especie_declarada_chega_a_ficha(self):
        self.assertEqual(_ficha(CONTENT_TYPE="video/mp4").CONTENT_TYPE,
                         "video/mp4")

    def test_CONTENT_TYPE_esta_na_lista_do_coletor(self):
        """Sem isto, `ficha()` nem sequer vê o campo — ele fica no item."""
        self.assertIn("CONTENT_TYPE", ing.DO_COLETOR)

    def test_sem_declaracao_a_extensao_continua_a_mandar(self):
        """O caminho antigo não muda para quem não declara nada."""
        self.assertEqual(_ficha().CONTENT_TYPE, art.NAO_SEI)
        self.assertEqual(
            _ficha(STORAGE_LOCATION="package.json",
                   NAME="package.json").CONTENT_TYPE, "application/json")

    def test_uma_confissao_nao_vence_a_extensao(self):
        """`NAO SEI` é honesto sobre a ausência — e não é uma espécie.

        Deixá-lo ganhar faria um coletor que preenche o campo por hábito
        APAGAR a dedução que a extensão ainda conseguia dar.
        """
        for confissao in (art.NAO_SEI, "NAO_SEI", art.NAO_SE_APLICA, "  "):
            with self.subTest(confissao=confissao):
                self.assertEqual(
                    _ficha(STORAGE_LOCATION="package.json", NAME="package.json",
                           CONTENT_TYPE=confissao).CONTENT_TYPE,
                    "application/json")

    def test_a_impressao_digital_e_o_tamanho_nao_mudam(self):
        """Mexer na espécie não pode mexer nos bytes."""
        a, b = _ficha(), _ficha(CONTENT_TYPE="video/mp4")
        self.assertEqual(a.SHA256, b.SHA256)
        self.assertEqual(a.BYTES, b.BYTES)


class T2APortaDaEspecieRecebeOQuePrecisa(unittest.TestCase):
    """RT — o vídeo deixa de ser entregue ao extrator de PDF."""

    def test_video_declarado_nao_vai_para_a_derivacao_de_pdf(self):
        """⚠️ REESCRITA PELA C4H, E A AFIRMACAO E A MESMA.

        Ela dizia `_quem_deriva_aceita("video/mp4") is False` — porque em C4G
        NINGUEM sabia abrir video, e a unica forma de o video nao ir ao
        `pdftotext` era nao ir a lado nenhum.

        Hoje ha quem o abra, e a pergunta certa deixou de ser «alguem aceita?»
        para ser «QUEM aceita?». A lei guardada nao mudou uma virgula: o video
        nao vai para o extrator de PDF.

            A PROVA MUDA DE INSTRUMENTO QUANDO O MUNDO MUDA.
            O QUE ELA AFIRMA E QUE NAO PODE MUDAR EM SILENCIO.
        """
        for mt in ("video/mp4", "audio/wav"):
            with self.subTest(media_type=mt):
                self.assertNotEqual(ing.executor_para(mt)[0],
                                    "executor_texto_de_pdf")

    def test_o_pdf_continua_a_passar(self):
        self.assertTrue(ing._quem_deriva_aceita("application/pdf"))

    def test_a_ausencia_continua_a_ser_tentativa_e_nao_recusa(self):
        """⚠️ ISTO NÃO PODE SER «ENDURECIDO».

        Tratar `None` como recusa encolheria a coleta em silêncio: uma linha
        antiga sem `media_type` deixaria de ser derivada sem ninguém decidir
        isso. A lei é a do ficheiro, e fica guardada aqui.
        """
        self.assertTrue(ing._quem_deriva_aceita(None))
        self.assertTrue(ing._quem_deriva_aceita(art.NAO_SEI))

    def test_a_cadeia_inteira_do_video_num_so_lugar(self):
        """Declarado -> chega à ficha -> a porta da espécie recusa. Os três."""
        f = _ficha(CONTENT_TYPE="video/mp4")
        self.assertEqual(f.CONTENT_TYPE, "video/mp4")
        self.assertEqual(ing.executor_para(f.CONTENT_TYPE)[0],
                         "executor_transcricao_midia")


class T3OQueContinuaEmAberto(unittest.TestCase):
    """A sentinela que impede esta missão de ser lida como maior do que foi."""

    def test_o_executor_de_audio_nasceu_e_a_trava_disparou(self):
        """⚠️ ESTA PROVA DISPAROU, E FOI POR ISSO QUE ELA EXISTIA.

        Em C4G ela dizia: «a porta so conhece PDF; no dia em que um executor de
        audio for declarado, esta prova reprova e a mensagem diz o que rever».
        Em C4H ele foi declarado, e ela reprovou — a trava de metodo funcionou.

        O que ela guarda agora e o degrau seguinte: a porta conhece o executor
        de midia, e ISSO NAO E O MESMO que a estrada ter corrido.

            MODULE EXISTS != EDGE EXISTS != FLOW OBSERVED.
        """
        aceites = set()
        for cap in ing._capacidades_de_derivacao():
            aceites.update(str(a).lower() for a in (cap.get("ACEITA_MEDIA_TYPES") or ()))
        self.assertIn("application/pdf", aceites)
        self.assertIn("video/mp4", aceites)
        self.assertIn("audio/wav", aceites)

    def test_a_porta_deixou_de_perguntar_a_um_dono_so(self):
        """C4G mediu a lista de um. C4H trocou-a por um registo NOMEADO.

        A lista continua curta e escrita à mão de propósito: varrer a pasta à
        procura de executores copiaria em silêncio o que lá estivesse, e
        faltaria em silêncio o que não estivesse.
        """
        self.assertGreaterEqual(len(ing.EXECUTORES_DE_DERIVACAO), 2)
        self.assertIn("executor_texto_de_pdf", ing.EXECUTORES_DE_DERIVACAO)
        self.assertIn("executor_transcricao_midia", ing.EXECUTORES_DE_DERIVACAO)
        self.assertEqual(len(ing._capacidades_de_derivacao()),
                         len(ing.EXECUTORES_DE_DERIVACAO),
                         "um executor declarado que nao importa fica calado")



if __name__ == "__main__":
    unittest.main(verbosity=2)
