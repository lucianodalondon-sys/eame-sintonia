#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DERIVACAO-ESTRUTURA-V2 (28/09) — uma etiqueta não atravessa outro «<».

O replay do coordenador no armazém real (536 páginas) achou o defeito da `limpar/2`:
HTML malformado com «</» solto (`…>ES</a></</div></div>…`, consorziobalsamico.it,
IT-T7-042). A 1.ª passagem trocava `</div>` por `\\n`; o «</» órfão ficava sem o
seu «>», e a 2.ª passagem `<[^>]+>` engolia dali até o PRÓXIMO «>» — título e
subtítulo do artigo inteiros.

As fixtures são RECORTES CONTÍGUOS, byte a byte, de duas páginas públicas guardadas
na árvore (`data/collection-store/italy/IT-T7-042/…`); o sha256 de cada recorte é
conferido, e o do ficheiro de onde saiu fica escrito ao lado.
"""
from __future__ import annotations

import hashlib
import html
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in (RAIZ, os.path.join(RAIZ, "leis")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas  # noqa: E402,F401
from coleta import texto_fonte as tf  # noqa: E402
import fato_do_texto as FT  # noqa: E402

PASTA = os.path.join(RAIZ, "tests", "fixtures", "balsamico_orfao")

#: nome -> (sha256 do recorte, sha256 da página de onde saiu, título, subtítulo)
RECORTES = {
    "mixology": (
        "420803cabdfe2ed0d4a38f5ce4ba83913dddfd7f694ba5c801c55af768c6fc34",
        "114bdcdb5c3172115638d308e78eb3ae9322c487ec3d19a0593686003e7c7751",
        "L’ACETO BALSAMICO DI MODENA IGP DIVENTA L’INGREDIENTE SEGRETO DELLA MIXOLOGY",
        "L’utilizzo dell’Aceto Balsamico di Modena IGP nella preparazione dei cocktail "
        "è un trend in continua crescita"),
    "filiera-del-vino": (
        "f2858d63cb870fb5fd242c68299dcb7d97790060d34b7ca1f0409b821ef1db88",
        "2797e324a40f447c10b48d3b6a980f459a0001e0ff06de4517815d2976504325",
        "CRISI DEL VINO: IL CONSORZIO TUTELA ACETO BALSAMICO DI MODENA A SOSTEGNO DELLA "
        "FILIERA DEL VINO ITALIANO",
        "Ogni anno oltre 2,5 milioni di quintali di uva e fino a 60 milioni di litri di vino "
        "ma eliminando le imitazioni la domanda potrebbe crescere di almeno il 30%"),
}


def _recorte(nome):
    with open(os.path.join(PASTA, "%s.recorte.html" % nome), "rb") as fh:
        return fh.read()


def limpar_duas_passagens(dados, ctype=""):
    """A `limpar/2` (EXECUTOR_VERSION "3"), para provar que estes testes a apanham."""
    t = dados.decode("utf-8", errors="replace")
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"</?(?:%s)\b[^>]*>" % "|".join(tf.BLOCOS), "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t\xa0]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return "\n".join(l.strip() for l in t.split("\n") if l.strip())


class ORecorteEOReal(unittest.TestCase):

    def test_sha_de_cada_recorte(self):
        for nome in RECORTES:
            with self.subTest(nome):
                self.assertEqual(hashlib.sha256(_recorte(nome)).hexdigest(), RECORTES[nome][0])

    def test_o_recorte_tem_o_orfao(self):
        for nome in RECORTES:
            with self.subTest(nome):
                self.assertEqual(_recorte(nome).count(b"</</div>"), 1)


class TituloESubtituloSobrevivem(unittest.TestCase):

    @staticmethod
    def _faltas(limpar):
        """O que falta: (recorte, peça, onde). Título e subtítulo têm de ser LINHAS do
        texto e estar no `corpo()` vivo."""
        faltas = []
        for nome, (_s, _p, titulo, subtitulo) in RECORTES.items():
            texto = limpar(_recorte(nome), "text/html")
            linhas, corpo = texto.split("\n"), FT.corpo(texto)
            for peca, valor in (("TITULO", titulo), ("SUBTITULO", subtitulo)):
                if valor not in linhas:
                    faltas.append((nome, peca, "TEXTO"))
                if valor not in corpo:
                    faltas.append((nome, peca, "CORPO"))
        return faltas

    def test_a_limpar_viva(self):
        self.assertEqual(self._faltas(tf.limpar), [])

    def test_voltar_as_duas_passagens_perde_titulo_e_subtitulo(self):
        # a mutação «voltar à v3» tem de pôr o teste acima vermelho — e pelas peças certas
        # (no mixology o título ainda chega ao `corpo()` pela migalha «Home / News / …»,
        # que o repete; como LINHA própria some nos dois, e o subtítulo some de tudo)
        faltas = self._faltas(limpar_duas_passagens)
        for nome in RECORTES:
            self.assertIn((nome, "TITULO", "TEXTO"), faltas)
            self.assertIn((nome, "SUBTITULO", "TEXTO"), faltas)
            self.assertIn((nome, "SUBTITULO", "CORPO"), faltas)

    def test_o_orfao_nao_deixa_lixo(self):
        for nome in RECORTES:
            with self.subTest(nome):
                texto = tf.limpar(_recorte(nome), "text/html")
                self.assertNotIn("<", texto)
                self.assertIn("ES", texto.split("\n"))


class AEtiquetaNaoAtravessaOutroMenor(unittest.TestCase):

    def L(self, s):
        return tf.limpar(s.encode("utf-8"), "text/html")

    def test_orfao_de_fecho_antes_de_bloco(self):
        self.assertEqual(self.L("<p>ES</a></</div><h1>Titolo</h1>testo"), "ES\nTitolo\ntesto")

    def test_orfao_antes_de_inline(self):
        self.assertEqual(self.L("<p>resto </<b>grassetto</b></p>"), "resto grassetto")

    def test_orfao_de_marcacao_vira_espaco_so_ate_o_branco(self):
        self.assertEqual(self.L("<p>x <!doctype y <? z</p>"), "x y z")

    def test_menor_diante_de_espaco_ou_algarismo_e_texto(self):
        self.assertEqual(self.L("<p>se a < 5 e b >= 2</p>"), "se a < 5 e b >= 2")
        self.assertEqual(self.L("<p>a <5 b> c</p>"), "a <5 b> c")

    def test_comentario_com_bloco_dentro_acaba_no_primeiro_maior_como_sempre(self):
        # dentro de `<!--` o «<» não abre etiqueta; o comentário acaba no 1.º «>»
        # (a `limpar()` sempre fez assim; ir até `-->` é outra mudança, medida e não feita)
        self.assertEqual(self.L('a<!-- <div class="x"> -->b'), "a -->b")
        self.assertEqual(self.L("a<!-- x -->b"), "a b")

    def test_etiqueta_multilinha_legitima_continua_etiqueta(self):
        self.assertEqual(self.L('<p>a<img\r\n src="x"\r\n/>b</p>'), "a b")
        self.assertEqual(self.L('a<div\n class="x">b'), "a\nb")

    def test_o_bloco_continua_decidido_pelo_nome(self):
        self.assertEqual(self.L("a<pa>b</pa>c<param>d<thead>e"), "a b c d e")
        self.assertEqual(self.L("a<BR/>b<P ALIGN=x>c"), "a\nb\nc")

    def test_a_sonda_tem_o_caso(self):
        self.assertIn(b"</</div>", tf.SONDA)
        self.assertIn(b"</<b>", tf.SONDA)
        self.assertIn(b" < 5 ", tf.SONDA)


if __name__ == "__main__":
    unittest.main(verbosity=2)
