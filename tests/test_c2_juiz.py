# -*- coding: utf-8 -*-
"""C2-JUIZ (2026-09-26): os 8 casos reais da 3.a onda contra o juiz de pagina.

Os 7 de `relatorio/CAPAS-A-CONFIRMAR.tsv` (ONDA3-WEB-20260925-1934) e a lista ENEA que o
juiz deixou entrar na Sala. Lidos a mao (FECHO-ONDA3.md, seccao 6):

  1495 1501 1502 1515 1523 1558  materia  (noticia curta com menu grande: o formato diz capa)
  1533                           capa     («Chi siamo» do CAI)
  1520                           capa     (lista de eventos ENEA, 10 «Leggi tutto»)

A V2 conserta o 1520 e nao muda os outros 7. As 6 noticias continuam barradas pelo
formato: LIMITE CONHECIDO, declarado aqui para que ninguem o tome por acerto.

    py -m unittest tests.test_c2_juiz -v
"""
import hashlib
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "curadoria"))
import retrato_html as RH  # noqa: E402

DADOS = os.path.join(RAIZ, "tests", "dados", "c2-juiz")

# raw_asset.id -> (sha256 na Sala, SOURCE_ID, leitura humana)
CASOS = {
    1495: ("00fd0192558d0a16e9d090193acf2030cfecffa9ddd0cbfc0154d0cd83517e96", "IT-T12-024", "MATERIA"),
    1501: ("84d76b1d4ad073ddb56126800299783ac828135be222b653537786334a405df6", "IT-T12-129", "MATERIA"),
    1502: ("2b913754613ffa77da1872410e4bf779aa288936933313f57862c13a3f1f0e8e", "IT-T12-129", "MATERIA"),
    1515: ("af2b085d00542e90d0a6e7c5664da25d6e6872711dc188b3fc720db41393e3e8", "IT-T2-146", "MATERIA"),
    1523: ("9b29a1aea41ccdc2e66c6e77e51c828719ad4071c9ad8b001701530fff5a6d90", "IT-T7-017", "MATERIA"),
    1558: ("fc7330c30eede4b038c58a0dc0dfb7a3510b07aa6604b70199ad111b8425c0c1", "IT-T9-009", "MATERIA"),
    1533: ("f76c8d6c40dd066cebf1bcfac54c9fe8f81a221548ddd6e7e5a0167c4de67dd2", "IT-T7-048", "CAPA"),
    1520: ("384723e6624a6a439b9cdeca8f19855955ab5faafee7412b16596db00a48efa7", "IT-T5-186", "CAPA"),
}
NOTICIAS_BARRADAS_PELO_FORMATO = {1495, 1501, 1502, 1515, 1523, 1558}


def _bytes(i):
    with open(os.path.join(DADOS, "raw-%d.html" % i), "rb") as f:
        return f.read()


def _veredito(r):
    return RH.veredito(r, url=None, contrato=None, regua_a_mandar=False)


class OsOitoCasosReais(unittest.TestCase):

    def test_bytes_sao_os_da_sala(self):
        for i, (sha, _, _) in CASOS.items():
            self.assertEqual(hashlib.sha256(_bytes(i)).hexdigest(), sha, i)

    def test_a_lista_enea_passa_a_capa_pela_v2(self):
        r = RH.retrato_do_html(_bytes(1520))
        self.assertEqual(r["CAPA_OU_MATERIA"], "MATERIA_PROVAVEL")   # o formato engana-se
        self.assertEqual(r["READ_MORE_LINKS"], 10)
        self.assertEqual(RH.regra_e_veredito(r, url=None, contrato=None, regua_a_mandar=False),
                         (RH.REGRA_V2, "CAPA_PROVAVEL"))

    def test_chi_siamo_continua_capa(self):
        self.assertEqual(_veredito(RH.retrato_do_html(_bytes(1533))), "CAPA_PROVAVEL")

    def test_v2_nao_mexe_nas_noticias_curtas(self):
        """A V2 so aperta materia; a noticia que o formato ja barra fica como estava."""
        for i in NOTICIAS_BARRADAS_PELO_FORMATO:
            r = RH.retrato_do_html(_bytes(i))
            self.assertLess(r["READ_MORE_LINKS"], RH.LEIA_MAIS_MINIMO, i)
            self.assertEqual(_veredito(r), r["CAPA_OU_MATERIA"], i)

    def test_limite_conhecido_as_seis_noticias_continuam_barradas(self):
        """NAO e acerto: as 6 sao materias. Se isto mudar, remedir o gabarito antes de aceitar."""
        for i in NOTICIAS_BARRADAS_PELO_FORMATO:
            self.assertEqual(_veredito(RH.retrato_do_html(_bytes(i))), "CAPA_PROVAVEL", i)

    def test_acertos_na_onda3(self):
        acerto = sum(1 for i, (_, _, h) in CASOS.items()
                     if (_veredito(RH.retrato_do_html(_bytes(i))) == "CAPA_PROVAVEL") == (h == "CAPA"))
        self.assertEqual(acerto, 2)   # 1520 e 1533; antes da V2 era 1 (so o 1533)

    def test_o_gate_diz_a_regra_v2(self):
        contrato = {"ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY"}, "OUTPUT_TYPE": "HTML"}
        m = RH.gate_capa_nao_e_materia(contrato, RH.retrato_do_html(_bytes(1520)),
                                       url=None, regua_a_mandar=False)
        self.assertIn(RH.REGRA_V2, m)
        self.assertIn("10", m)

    def test_a_v1_continua_antes_da_v2(self):
        r = dict(RH.retrato_do_html(_bytes(1520)))
        contrato = {"ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY",
                                    "INDEX_URL": "https://x.test/lista"}}
        self.assertEqual(RH.regra_e_veredito(r, url="https://x.test/lista/", contrato=contrato,
                                             regua_a_mandar=True)[0], RH.REGRA_V1)

    def test_limiar_exacto(self):
        base = {"CAPA_OU_MATERIA": "MATERIA_PROVAVEL"}
        self.assertEqual(_veredito(dict(base, READ_MORE_LINKS=RH.LEIA_MAIS_MINIMO)), "CAPA_PROVAVEL")
        self.assertEqual(_veredito(dict(base, READ_MORE_LINKS=RH.LEIA_MAIS_MINIMO - 1)),
                         "MATERIA_PROVAVEL")
        self.assertEqual(_veredito({"CAPA_OU_MATERIA": "NAO_SEI", "READ_MORE_LINKS": 50}), "NAO_SEI")

    def test_contagem_leia_mais_so_ligacoes(self):
        """D79: conta-se ELEMENTOS <a> cujo texto ou rotulo COMECA pela frase."""
        c = lambda s: RH.retrato_do_html(s.encode("utf-8"))["READ_MORE_LINKS"]
        self.assertEqual(c('<a href="/1">Leggi tutto</a><a href="/2">leggi  di più</a>'
                           '<a href="/3">Continua a leggere</a><a href="/4">leggi di piu</a>'), 4)
        self.assertEqual(c('<a href="/1">Leggi tutto<span> su ENEA a ICOE</span></a>'), 1)   # a forma ENEA
        self.assertEqual(c('<a href="/1" aria-label="Leggi tutto: titolo"><img></a>'
                           "<a href='/2' title='leggi di più'>›</a>"), 2)                  # so o rotulo
        self.assertEqual(c('<a href="/1">xleggi tutto</a><a href="/2">Titolo — leggi tutto</a>'
                           '<a href="/3">Read more</a><a href="/4">Scopri di più</a>'
                           '<script>"<a>leggi tutto</a>"</script>'), 0)

    def test_negativo_d79_frase_sem_ligacao_nao_e_lista(self):
        """O defeito da D79: a frase repetida no TEXTO, sem nenhuma ligacao, nao faz uma lista."""
        corpo = "<p>" + "Leggi tutto il regolamento prima di partecipare. " * 40 + "</p>"
        r = RH.retrato_do_html(("<html><body><h1>Bando</h1>" + corpo * 2 + "</body></html>").encode("utf-8"))
        self.assertEqual(r["LINKS"], 0)
        self.assertEqual(r["READ_MORE_LINKS"], 0)
        self.assertEqual(r["CAPA_OU_MATERIA"], "MATERIA_PROVAVEL")
        self.assertEqual(_veredito(r), "MATERIA_PROVAVEL")


class AAdmissaoBarraALista(unittest.TestCase):
    """A porta da Sala (pergunta `materia`): a lista ENEA passa a NAO pela V2."""

    def _materia(self, i, fonte, url):
        sys.path.insert(0, RAIZ)
        from admissao import admissao as adm
        return adm._e_materia({"retrato_do_detector": RH.retrato_do_html(_bytes(i)), "source_id": fonte,
                               "url_da_pagina": url, "parent_sha256": CASOS[i][0]})

    def test_lista_enea_e_nao_pela_v2(self):
        res, motivo, ev = self._materia(1520, "IT-T5-186",
                                        "https://sostenibilita.enea.it/eventi/meeting-internazionali-0")
        self.assertEqual(res, "NAO")
        self.assertTrue(motivo.startswith("V2:"), motivo)
        self.assertEqual(ev["v1"]["REGRA"], RH.REGRA_V2)

    def test_chi_siamo_continua_nao_pelo_detector(self):
        res, motivo, ev = self._materia(1533, "IT-T7-048", "http://www.caiagromec.it/node/8")
        self.assertEqual(res, "NAO")
        self.assertNotIn("v1", ev)


class OGemeoNodeJulgaIgual(unittest.TestCase):

    def test_paridade_nos_oito(self):
        js = ("import('./coleta/retrato_html.mjs').then(m=>{const fs=require('fs');"
              "const o={};for(const i of JSON.parse(process.argv[1])){"
              "const r=m.retratoDoHtml(fs.readFileSync('tests/dados/c2-juiz/raw-'+i+'.html'));"
              "o[i]=[r.READ_MORE_LINKS,r.CAPA_OU_MATERIA,"
              "m.regraEVeredito(r,null,{url:null,reguaAMandar:false})]}"
              "console.log(JSON.stringify(o))})")
        p = subprocess.run(["node", "-e", js, json.dumps(sorted(CASOS))], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr[-400:])
        node = json.loads(p.stdout.strip().splitlines()[-1])
        for i in CASOS:
            r = RH.retrato_do_html(_bytes(i))
            py = [r["READ_MORE_LINKS"], r["CAPA_OU_MATERIA"],
                  list(RH.regra_e_veredito(r, url=None, contrato=None, regua_a_mandar=False))]
            self.assertEqual(node[str(i)], py, i)

    def test_contagem_leia_mais_com_acento_e_negativos(self):
        """`\\b` do JavaScript nao conta «ù» como letra: o gemeo usa fronteira Unicode.
        E, como no Python: frase sem ligacao e «xleggi» nao contam; rotulo conta."""
        js = ("import('./coleta/retrato_html.mjs').then(m=>console.log(m.retratoDoHtml("
              "Buffer.from('<a href=1>leggi di più</a><a href=2 title=\\'leggi tutto\\'>x</a>"
              "<a href=3>xleggi tutto</a><a href=4>leggi dipiùx</a><p>leggi tutto leggi tutto</p>')).READ_MORE_LINKS))")
        p = subprocess.run(["node", "-e", js], cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", timeout=120)
        self.assertEqual(p.stdout.strip(), "2", p.stderr[-400:])


if __name__ == "__main__":
    unittest.main()
