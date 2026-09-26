# -*- coding: utf-8 -*-
"""ACERVO-PARA-SALA-3 (decisao do coordenador, 26/09 14:00): V3 — a pagina de UM video e materia.

Medido (ACERVO-PARA-SALA-2): 612/612 paginas `youtube.com/watch?v=` do acervo foram julgadas capa pelo
retrato (o conteudo vive num <script>). Opcao B: SO `youtube.com/watch?v=<id>` passa a MATERIA_PROVAVEL.
Canal, playlist, pesquisa, shorts, youtu.be e a raiz continuam com o detector (teste negativo).

    py -m unittest tests.test_v3_pagina_de_video -v
"""
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "curadoria"))
import retrato_html as RH  # noqa: E402

AMOSTRA = os.path.join(RAIZ, "tests", "dados", "descricao-yt", "it-t7-015-raw201-videodetails.html")
CAPA = {"CAPA_OU_MATERIA": "CAPA_PROVAVEL", "HTML_KIND": "NAVIGATION", "LINKS": 14,
        "NON_WHITESPACE_CHARACTERS": 209, "PARAGRAPH_CHARACTERS": 0, "READ_MORE_LINKS": 0}

VIDEO = [
    "https://www.youtube.com/watch?v=Yp6q5K-fEF8",          # o do ensaio (IT-T10-017, raw 1647)
    "https://www.youtube.com/watch?v=f-Up25Lyn9I",
    "http://youtube.com/watch?v=Yp6q5K-fEF8",
    "https://m.youtube.com/watch?v=Yp6q5K-fEF8",
    "https://WWW.YOUTUBE.COM/watch?v=Yp6q5K-fEF8",
    "https://www.youtube.com/watch?v=Yp6q5K-fEF8&t=42s",
    "https://www.youtube.com/watch?feature=share&v=Yp6q5K-fEF8",
    "https://www.youtube.com/watch?v=Yp6q5K-fEF8&list=PLabc",  # um video DENTRO de uma lista: a pagina e o video
    "  https://www.youtube.com/watch?v=Yp6q5K-fEF8#comentarios",
]
NAO_VIDEO = [
    "https://www.youtube.com/@ConsorzioVini",                 # canal
    "https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv",
    "https://www.youtube.com/c/ConsorzioVini/videos",
    "https://www.youtube.com/user/consorzio",
    "https://www.youtube.com/playlist?list=PLabcdefghijk",    # playlist
    "https://www.youtube.com/results?search_query=vite",
    "https://www.youtube.com/shorts/Yp6q5K-fEF8",
    "https://youtu.be/Yp6q5K-fEF8",
    "https://www.youtube.com/",
    "https://www.youtube.com/watch",
    "https://www.youtube.com/watch?vv=Yp6q5K-fEF8",
    "https://www.youtube.com/watch?v=Yp6q5K",                 # id curto
    "https://www.youtube.com/watch?v=Yp6q5K-fEF8x",           # id comprido
    "https://notyoutube.com/watch?v=Yp6q5K-fEF8",
    "https://www.youtube.com.evil.it/watch?v=Yp6q5K-fEF8",
    "https://www.consorzio.it/watch?v=Yp6q5K-fEF8",
    None, "",
]


def _rv(retrato, url, contrato=None, regua=False):
    return RH.regra_e_veredito(retrato, url=url, contrato=contrato, regua_a_mandar=regua)


class AV3SoNaPaginaDeUmVideo(unittest.TestCase):

    def test_pagina_de_video_e_materia_pela_v3(self):
        for u in VIDEO:
            self.assertTrue(RH.e_pagina_de_um_video(u), u)
            self.assertEqual(_rv(CAPA, u), (RH.REGRA_V3, "MATERIA_PROVAVEL"), u)

    def test_canal_playlist_e_outros_continuam_com_o_detector(self):
        for u in NAO_VIDEO:
            self.assertFalse(RH.e_pagina_de_um_video(u), u)
            self.assertEqual(_rv(CAPA, u), (None, "CAPA_PROVAVEL"), u)

    def test_sem_retrato_nao_ha_veredito_inventado(self):
        self.assertEqual(_rv(None, VIDEO[0]), (None, None))

    def test_ja_materia_nao_conta_como_regra(self):
        self.assertEqual(_rv(dict(CAPA, CAPA_OU_MATERIA="MATERIA_PROVAVEL"), VIDEO[0]),
                         (None, "MATERIA_PROVAVEL"))

    def test_v1_continua_antes_da_v3(self):
        contrato = {"ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": VIDEO[0]}}
        self.assertEqual(_rv(CAPA, VIDEO[0], contrato, True), (None, "CAPA_PROVAVEL"))

    def test_o_gate_do_coletor_deixa_passar_a_pagina_de_video_e_barra_o_canal(self):
        contrato = {"ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": NAO_VIDEO[0]},
                    "OUTPUT_TYPE": "HTML"}
        self.assertIsNone(RH.gate_capa_nao_e_materia(contrato, CAPA, url=VIDEO[0], regua_a_mandar=False))
        self.assertIsNotNone(RH.gate_capa_nao_e_materia(contrato, CAPA, url=NAO_VIDEO[4], regua_a_mandar=False))

    def test_a_pagina_guardada_real(self):
        with open(AMOSTRA, "rb") as fh:
            r = RH.retrato_do_html(fh.read())
        self.assertNotEqual(r["CAPA_OU_MATERIA"], "MATERIA_PROVAVEL")   # o retrato sozinho nao ve o video
        self.assertEqual(_rv(r, "https://www.youtube.com/watch?v=f-Up25Lyn9I")[1], "MATERIA_PROVAVEL")


class APortaDaSala(unittest.TestCase):

    def _materia(self, url):
        # outro teste pode ja ter importado `admissao/admissao.py` como modulo de topo `admissao`
        # (com `admissao/` no caminho): entao e ele; senao, o pacote. O mesmo ficheiro nos dois casos.
        adm = sys.modules.get("admissao")
        if not hasattr(adm, "_e_materia"):
            sys.path.insert(0, RAIZ)
            from admissao import admissao as adm
        return adm._e_materia({"retrato_do_detector": dict(CAPA), "source_id": "IT-T10-017",
                               "url_da_pagina": url, "parent_sha256": "0" * 64})

    def test_video_entra_pela_v3(self):
        res, motivo, ev = self._materia(VIDEO[0])
        self.assertEqual(res, "SIM")
        self.assertTrue(motivo.startswith("V3:"), motivo)
        self.assertEqual(ev["v1"]["REGRA"], RH.REGRA_V3)

    def test_canal_e_playlist_continuam_barrados(self):
        for u in (NAO_VIDEO[0], NAO_VIDEO[4]):
            res, motivo, ev = self._materia(u)
            self.assertEqual(res, "NAO", u)
            self.assertNotIn("v1", ev, u)


class OGemeoNodeJulgaIgual(unittest.TestCase):

    def test_paridade_nos_enderecos(self):
        urls = VIDEO + [u for u in NAO_VIDEO if u]
        js = ("import('./coleta/retrato_html.mjs').then(m=>{const o={};"
              "const r=JSON.parse(process.argv[2]);"
              "for(const u of JSON.parse(process.argv[1])){o[u]=[m.ePaginaDeUmVideo(u),"
              "m.regraEVeredito(r,null,{url:u,reguaAMandar:false})]}"
              "console.log(JSON.stringify(o))})")
        p = subprocess.run(["node", "-e", js, json.dumps(urls), json.dumps(CAPA)], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr[-400:])
        node = json.loads(p.stdout.strip().splitlines()[-1])
        for u in urls:
            self.assertEqual(node[u], [RH.e_pagina_de_um_video(u), list(_rv(CAPA, u))], u)


if __name__ == "__main__":
    unittest.main()
