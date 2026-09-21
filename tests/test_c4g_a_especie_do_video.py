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
        """⚠️ A AFIRMAÇÃO MUDOU NA C4H, E O QUE ELA PROVA NÃO MUDOU.

        Até aqui esta prova dizia `assertFalse(_quem_deriva_aceita("video/mp4"))`
        — e estava CERTA: não havendo executor de mídia, a única maneira de o
        vídeo não ir ao `pdftotext` era não ser derivado de todo.

        A C4H escreveu esse executor. Agora a porta ACEITA vídeo, e aceita-o
        porque há quem o abra. Manter o `assertFalse` seria pedir à casa que
        continuasse a recusar mídia para um teste não mudar.

            O QUE ESTA PROVA SEMPRE QUIS DIZER ERA «O VÍDEO NÃO VAI AO
            EXTRATOR DE PDF» — E ISSO MEDE-SE NO DESTINO, NÃO NA PORTA.

        `_quem_deriva_aceita` responde «ALGUÉM abre?». O destino responde
        «QUEM abre?». Enquanto houve um executor só, as duas perguntas tinham
        a mesma resposta, e era fácil confundi-las.
        """
        for tipo in ("video/mp4", "audio/wav"):
            with self.subTest(tipo=tipo):
                self.assertTrue(ing._quem_deriva_aceita(tipo),
                                "a midia deixou de ter quem a abra")
                self.assertNotEqual(
                    getattr(ing.executor_para(tipo), "EXECUTOR_ID", None),
                    "texto-de-pdf",
                    "a midia foi encaminhada ao extrator de PDF")

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
        """Declarado -> chega à ficha -> vai ao executor de MÍDIA. Os três.

        A C4G provou os dois primeiros elos e travava no terceiro por falta de
        destino. A C4H deu-lhe destino, e a cadeia fecha aqui inteira.
        """
        f = _ficha(CONTENT_TYPE="video/mp4")
        self.assertEqual(f.CONTENT_TYPE, "video/mp4")
        self.assertTrue(ing._quem_deriva_aceita(f.CONTENT_TYPE))
        self.assertEqual(
            getattr(ing.executor_para(f.CONTENT_TYPE), "EXECUTOR_ID", None),
            "transcricao-de-midia")


class T3ASentinelaDisparou(unittest.TestCase):
    """A sentinela da C4G fez exactamente o que foi construída para fazer.

    ⚠️ ESTA CLASSE CHAMAVA-SE `T3OQueContinuaEmAberto`, E O QUE ESTAVA EM
    ABERTO FECHOU.

    A C4G escreveu duas provas cujo trabalho era REPROVAR no dia em que um
    executor de mídia nascesse: `test_nenhum_executor_de_derivacao_de_audio_nasceu`
    e `test_a_porta_da_derivacao_pergunta_a_um_dono_so`. A mensagem de falha
    dizia, por escrito, o que rever. Na C4H elas reprovaram, e a mensagem
    estava certa.

        UMA SENTINELA QUE DISPARA NÃO É UM TESTE PARTIDO: É UM TESTE A
        TRABALHAR. O QUE SE APAGA É A AFIRMAÇÃO VELHA, NUNCA O MÉTODO.

    O que substitui as duas não é «o contrário»: é a mesma pergunta com a
    resposta de hoje — a porta conhece mais do que PDF, e conhece-o por
    DECLARAÇÃO, sem que o nome de nenhum executor esteja escrito na regra.
    """

    def test_a_porta_conhece_pdf_E_midia_e_nada_mais(self):
        """O registo cresceu de um para dois, e não para «qualquer coisa».

        ⚠️ E CRESCEU PARA TRÊS NA `DUAS-PORTAS-V1`, E A SENTINELA DISPAROU
        OUTRA VEZ — que é o trabalho dela. O nome do teste diz «pdf E mídia»
        e passa a dizer menos do que a lista; o MÉTODO que ele guarda é o que
        não muda: a porta conhece um conjunto FECHADO e DECLARADO de espécies,
        e não «qualquer coisa».

        O que entrou, e porquê: `text/html` e `application/xhtml+xml`, pelo
        `coleta/executor_texto_de_html.py`. 46 observações reais paravam em
        `DERIVED` com `MISSING_ROUTE` — a peça de extração já existia em
        `coleta/texto_fonte.py::limpar` e tinha ZERO chamadores.

        ⚠️ E `ACEITA_FAMILIAS` NÃO CRESCEU, de propósito. A família `text`
        apanharia `text/csv` e `text/plain`, que esta casa não sabe abrir —
        e `IT-T4-001` é `text/csv` e está medido como `MISSING_ROUTE` de
        OUTRO dono. Declarar a família aqui roubava-lhe a rota.
        """
        exactos, familias = set(), set()
        for cap in ing._capacidades_de_derivacao():
            exactos.update(str(a).lower()
                           for a in (cap.get("ACEITA_MEDIA_TYPES") or ()))
            familias.update(str(f).lower()
                            for f in (cap.get("ACEITA_FAMILIAS") or ()))
        self.assertEqual(exactos, {"application/pdf", "text/html",
                                   "application/xhtml+xml"},
                         "a porta passou a conhecer uma especie nova — "
                         "declare-a e reveja esta prova, que e a trava de "
                         "metodo")
        self.assertEqual(familias, {"audio", "video"},
                         "a porta passou a conhecer uma familia nova — declare-a "
                         "e reveja esta prova, que e a trava de metodo")

    def test_a_porta_nao_escreve_o_nome_de_nenhum_executor_na_regra(self):
        """A regra lê o registo; o registo é que nomeia os donos.

        A C4G mediu o defeito ao contrário — `import executor_texto_de_pdf`
        DENTRO da função que responde — e previu que «no dia em que entrasse um
        executor de áudio os dois divergiam em silêncio». Não divergiram
        porque o nome saiu da regra e foi para uma lista com dono.
        """
        with io.open(os.path.join(RAIZ, "coleta", "ingresso.py"),
                     encoding="utf-8") as fh:
            fonte = fh.read()
        i = fonte.index("def _cabe_na_capacidade")
        regra = fonte[i:fonte.index("\ndef ", i + 10)]
        self.assertNotIn("executor_texto_de_pdf", regra,
                         "a regra voltou a conhecer um executor pelo nome")
        self.assertNotIn("executor_transcricao_midia", regra)
        # E o registo existe, com os dois, num sítio só.
        self.assertIn("executor_texto_de_pdf", fonte[:i])
        self.assertIn("executor_transcricao_midia", fonte[:i])

    def test_o_video_passou_a_ter_consumidor(self):
        """`VIDEO_OUTPUT_HAS_CONSUMER` era `NO` por falta EXACTAMENTE disto."""
        mod = ing.executor_para("video/mp4")
        self.assertIsNotNone(mod, "o video voltou a nao ter quem o abra")
        self.assertIn("TRANSCRIPT", mod.CAPACIDADE["PRODUCES"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
