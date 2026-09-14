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
Que o vídeo passou a ser transcrito pelo caminho canónico. **Não passou.**
`VIDEO_OUTPUT_HAS_CONSUMER` continua `NO`, e continua por duas razões que este
conserto não toca: não existe executor de derivação de áudio para a porta
encontrar, e sem PostgreSQL não há observação nenhuma a chegar à fronteira.

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
        self.assertFalse(ing._quem_deriva_aceita("video/mp4"))
        self.assertFalse(ing._quem_deriva_aceita("audio/wav"))

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
        self.assertFalse(ing._quem_deriva_aceita(f.CONTENT_TYPE))


class T3OQueContinuaEmAberto(unittest.TestCase):
    """A sentinela que impede esta missão de ser lida como maior do que foi."""

    def test_nenhum_executor_de_derivacao_de_audio_nasceu(self):
        """Enquanto não houver, `VIDEO_OUTPUT_HAS_CONSUMER` continua `NO`.

        No dia em que um executor de áudio for escrito e DECLARADO à porta,
        esta prova reprova — e a mensagem diz o que rever. É uma trava de
        método, e não um veredito sobre o executor.
        """
        aceites = set()
        for cap in ing._capacidades_de_derivacao():
            aceites.update(str(a).lower() for a in (cap.get("ACEITA_MEDIA_TYPES") or ()))
        self.assertEqual(
            aceites, {"application/pdf"},
            "a porta da derivacao passou a conhecer mais do que PDF — reveja "
            "VIDEO_OUTPUT_HAS_CONSUMER, que estava NO por falta disto")

    def test_a_porta_da_derivacao_pergunta_a_um_dono_so(self):
        """E ele é importado pelo NOME. É aqui que o executor de áudio entrará.

        `_capacidades_de_derivacao` faz `import executor_texto_de_pdf` e
        devolve a capacidade dele. Não é um registo: é uma lista de um, com
        forma de registo — e o próprio ficheiro previu o problema, ao escrever
        «no dia em que entrasse um executor de áudio os dois divergiam em
        silêncio».
        """
        with io.open(os.path.join(RAIZ, "coleta", "ingresso.py"),
                     encoding="utf-8") as fh:
            fonte = fh.read()
        i = fonte.index("def _capacidades_de_derivacao")
        bloco = fonte[i:fonte.index("\n\n", i)]
        self.assertIn("import executor_texto_de_pdf", bloco)


if __name__ == "__main__":
    unittest.main(verbosity=2)
