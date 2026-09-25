# -*- coding: utf-8 -*-
"""RECEITAS-182 · a familia que a guarda recusava por casar navegacao (WordPress com noticias na raiz).

    cd curadoria && py -m unittest test_reparo_titulos_longos

Sem rede: as ligacoes sao escritas a mao, com a forma medida em asnacodi.it/news/ (25/09).
"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reparar_contrato as R   # noqa: E402

B = "https://www.exemplo-wp.it"
NOTICIAS = [B + "/agrifondo-giuseppe-boatto-e-il-nuovo-direttore/",
            B + "/assemblea-soci-il-sistema-si-confronta-risultati-priorita/",
            B + "/maltempo-oltre-700-milioni-di-danni-la-ricognizione/",
            B + "/vinitaly-calabria-la-filiera-si-racconta/"]
FIXAS = [B + "/adempimenti-degli-obblighi-di-trasparenza-e-di-pubblicita/", B + "/cookie-policy-ue/",
         B + "/privacy-policy/", B + "/chi-siamo/", B + "/contatti/", B + "/le-sedi-condifesa/",
         B + "/tesi-di-laurea/", B + "/news/", B + "/news/page/2/", B + "/feed/"]
LISTAGEM = B + "/news/"


def _familias(hrefs):
    return [f for f in R.familias(set(hrefs), LISTAGEM) if f["FLUXO"]]


class TestTitulosLongos(unittest.TestCase):
    def test_a_familia_recusada_por_navegacao_volta_so_com_titulos_longos(self):
        fams = _familias(NOTICIAS + FIXAS)
        self.assertEqual(1, len(fams), fams)
        f = fams[0]
        self.assertIn(R.COMO_TITULOS_LONGOS, f["COMO"])
        membros = sorted(h for h in NOTICIAS + FIXAS if re.match(f["PADRAO"], h))
        self.assertEqual(sorted(NOTICIAS), membros, "so as noticias; a pagina de trasparenza e as fixas ficam fora")
        self.assertEqual(NOTICIAS[0], membros[0], "o item que o canario abre (o 1.o ordenado) e uma noticia")

    def test_a_guarda_continua_a_valer_para_a_versao_estrita(self):
        est = R._so_titulos_longos(r"^https?://(www\.)?exemplo\-wp\.it/" + R.RC._SLUG + "/?$")
        self.assertIsNone(R.RC.e_generico(est, LISTAGEM, NOTICIAS + FIXAS, []))
        # uma pagina de navegacao com titulo longo continua a reprovar a familia
        nav_longa = B + "/chi-siamo-la-nostra-storia-dal-1990-ad-oggi-e-domani/"
        self.assertFalse(re.match(est, nav_longa), "vocabulario institucional fica fora do titulo")

    def test_sem_titulos_longos_nao_ha_familia(self):
        curtas = [B + "/app-meteo/", B + "/tesi-di-laurea/", B + "/linee-di-ricerca/", B + "/social-media-policy/"]
        self.assertEqual([], _familias(curtas + FIXAS))

    def test_recusa_que_nao_e_de_navegacao_nao_se_contorna(self):
        # mais de 80 % dos links: a guarda recusa, e nao ha versao estrita para isso
        muitas = [B + "/noticia-numero-%d-sobre-a-vindima-de-hoje-em-italia/" % i for i in range(20)]
        est = R._so_titulos_longos(r"^https?://(www\.)?exemplo\-wp\.it/" + R.RC._SLUG + "/?$")
        recusa = R.RC.e_generico(est, LISTAGEM, muitas, [])
        self.assertTrue(recusa and "80%" in recusa, recusa)
        self.assertEqual([], _familias(muitas), "a versao estrita tambem passa pela guarda, e ela recusa")

    def test_so_se_tenta_uma_vez(self):
        est = R._so_titulos_longos(r"^https?://(www\.)?exemplo\-wp\.it/" + R.RC._SLUG + "/?$")
        self.assertIsNone(R._so_titulos_longos(est), "a versao estrita nao gera outra versao")


if __name__ == "__main__":
    unittest.main()
