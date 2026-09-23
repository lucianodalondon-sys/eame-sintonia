# -*- coding: utf-8 -*-
"""V1A — a V1 ligada: o INDEX_URL do contrato e CAPA, SO com a regua dos 4 passos a mandar.

    MESMA PAGINA -> MESMO VEREDITO EM PYTHON E EM NODE.
    UMA FONTE QUE NAO PASSA OS 4 PASSOS NAO USA A V1.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
for p in ("", "curadoria", "coleta", "orquestrador", "guarda"):
    sys.path.insert(0, str(RAIZ / p))
import _gavetas  # noqa: E402,F401
import retrato_html as RH  # noqa: E402
import admissao as adm  # noqa: E402
import orquestrador as ORQ  # noqa: E402

MJS = (RAIZ / "coleta" / "retrato_html.mjs").as_posix()
INDICE = "https://www.regione.it/news/"
CONTRATO = {"SOURCE_ID": "IT-T7-900", "OUTPUT_TYPE": "HTML",
            "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": INDICE,
                            "LINK_PATTERN": "^https://www\\.regione\\.it/news/.+$"}}
FIXO = {"SOURCE_ID": "IT-T2-900", "OUTPUT_TYPE": "HTML",
        "ACQUISITION": {"STRATEGY": "STATIC_ENDPOINT", "INDEX_URL": INDICE}}


def artigo():
    corpo = "La mosca dell'olivo accelera con il calo termico. " * 40
    return "<html><body><h1>Bollettino</h1><p>%s</p><p>%s</p><a href='/a'>a</a></body></html>" % (corpo, corpo)


def listagem(n=60):
    return "<html><body><nav>%s</nav></body></html>" % "".join(
        "<a href='/news/item-%d'>T %d</a>" % (i, i) for i in range(n))


def misto():
    return "<html><body><div>" + ("testo senza paragrafi " * 30) + "</div><a href='/x'>x</a></body></html>"


class AV1(unittest.TestCase):
    def v(self, html, url, regua, contrato=CONTRATO):
        return RH.veredito(RH.retrato_do_html(html.encode()), url=url, contrato=contrato, regua_a_mandar=regua)

    def test_positivo_o_indice_de_fonte_com_regua_e_capa_mesmo_que_o_detector_diga_materia(self):
        self.assertEqual("MATERIA_PROVAVEL", RH.retrato_do_html(artigo().encode())["CAPA_OU_MATERIA"])
        self.assertEqual("CAPA_PROVAVEL", self.v(artigo(), INDICE, True))
        self.assertEqual("CAPA_PROVAVEL", self.v(misto(), INDICE.upper().rstrip("/") + "//", True),
                         "a mesma normalizacao da regua: barra final e maiusculas")

    def test_negativo_fonte_que_nao_passa_os_4_passos_nao_usa_a_v1(self):
        self.assertEqual("MATERIA_PROVAVEL", self.v(artigo(), INDICE, False))
        self.assertEqual("NAO_SEI", self.v(misto(), INDICE, False))

    def test_negativo_outra_pagina_rota_fixa_ou_sem_endereco_fica_o_detector(self):
        self.assertEqual("MATERIA_PROVAVEL", self.v(artigo(), INDICE + "uma-noticia", True))
        self.assertEqual("MATERIA_PROVAVEL", self.v(artigo(), INDICE, True, FIXO))
        self.assertEqual("MATERIA_PROVAVEL", self.v(artigo(), None, True))
        self.assertEqual("MATERIA_PROVAVEL", self.v(artigo(), INDICE, True, None))

    def test_so_true_manda(self):
        self.assertEqual("MATERIA_PROVAVEL", self.v(artigo(), INDICE, "sim"))

    def test_o_gate_reprova_o_indice_com_regua_e_diz_que_foi_a_v1(self):
        g = RH.gate_capa_nao_e_materia(CONTRATO, RH.retrato_do_html(artigo().encode()),
                                       url=INDICE, regua_a_mandar=True)
        self.assertIn(RH.REGRA_V1, g)
        self.assertIsNone(RH.gate_capa_nao_e_materia(CONTRATO, RH.retrato_do_html(artigo().encode()),
                                                     url=INDICE, regua_a_mandar=False))

    def test_chamador_que_esqueca_o_endereco_rebenta_e_nao_julga_calado(self):
        with self.assertRaises(TypeError):
            RH.gate_capa_nao_e_materia(CONTRATO, RH.retrato_do_html(artigo().encode()))  # noqa
        with self.assertRaises(TypeError):
            RH.veredito(RH.retrato_do_html(artigo().encode()))  # noqa


class TodosOsChamadores(unittest.TestCase):
    """Cada chamada do gate, em Python e em Node, nesta arvore, passa o endereco e a regua."""

    def _chamadas(self, padrao, globs):
        r = subprocess.run(["git", "grep", "-n", padrao, "--"] + globs, cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8")
        return [l for l in r.stdout.splitlines() if "def " not in l and "function " not in l
                and not l.split(":", 2)[2].lstrip().startswith(("#", "//", "*"))]

    def test_python(self):
        """Pela arvore sintactica, nao por linha: uma chamada partida em duas linhas conta."""
        import ast
        r = subprocess.run(["git", "grep", "-l", "gate_capa_nao_e_materia", "--", "*.py"], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8")
        vistas = 0
        for f in r.stdout.split():
            for no in ast.walk(ast.parse((RAIZ / f).read_text(encoding="utf-8"))):
                if isinstance(no, ast.Call) and getattr(no.func, "attr", getattr(no.func, "id", None))                         == "gate_capa_nao_e_materia":
                    vistas += 1
                    nomes = {k.arg for k in no.keywords}
                    if f == "tests/test_v1a_v1_ligada.py" and not nomes:
                        continue          # o teste que prova que a chamada sem eles rebenta
                    self.assertLessEqual({"url", "regua_a_mandar"}, nomes, "%s:%d" % (f, no.lineno))
        self.assertGreaterEqual(vistas, 8)

    def test_producao_le_a_regua_do_dono(self):
        for f in ("curadoria/canario.py", "medidas/canario_rotas_elegiveis.py", "medidas/micro_colheita.py"):
            t = (RAIZ / f).read_text(encoding="utf-8")
            self.assertIn("_regua_manda(", t, f)

    def test_o_canario_da_ao_gate_a_morada_do_item_e_a_regua_da_fonte(self):
        import canario as CAN
        import test_canario_detalhe as TCD
        pedidas = []
        with mock.patch.object(CAN, "buscar", TCD.rede({TCD.INDEX: TCD.indice_com_itens(),
                                                       TCD.ITEM: TCD.artigo_sintetico()})),              mock.patch.object(CAN, "_regua_manda", side_effect=lambda s: pedidas.append(s) or True),              mock.patch.object(CAN.RH, "gate_capa_nao_e_materia", wraps=RH.gate_capa_nao_e_materia) as g:
            r = CAN.canario_html(TCD.CONTRATO)
        self.assertEqual([TCD.CONTRATO["SOURCE_ID"]], pedidas)
        self.assertEqual({"url": r["ALVO"], "regua_a_mandar": True}, g.call_args.kwargs)

    def test_a_regua_do_canario_e_a_do_dono(self):
        import canario as CAN
        RS = adm._da_curadoria("ready_split")
        for regua, esperado in (("DETAIL/v1", True), ("LEGACY", False), ("NAO SEI", False)):
            with mock.patch.object(RS, "regua_de", return_value=regua):
                self.assertIs(esperado, CAN._regua_manda("IT-T7-900"), regua)

    def test_node_nesta_arvore(self):
        for l in self._chamadas("gateCapaNaoEMateria(", ["*.mjs", "*.js"]):
            if "retrato_html.mjs" in l.split(":", 1)[0]:
                continue
            self.fail("chamador Node sem { url, reguaAMandar } por conferir: " + l)

    def test_node_levanta_sem_as_opcoes(self):
        r = _node("""const m = await import(pathToFileURL(%s).href);
try { m.gateCapaNaoEMateria(%s, m.retratoDoHtml(Buffer.from("<p>x</p>"))); console.log(JSON.stringify("NAO LEVANTOU")); }
catch (e) { console.log(JSON.stringify(e.name)); }""" % (json.dumps(MJS), json.dumps(CONTRATO)))
        self.assertEqual("TypeError", r)


def _node(corpo):
    driver = 'import { pathToFileURL } from "node:url";\n' + corpo
    r = subprocess.run(["node", "--input-type=module", "-e", driver], cwd=RAIZ, capture_output=True,
                       text=True, encoding="utf-8", timeout=300)
    if r.returncode:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def _paginas_de_paridade():
    pags = [("artigo", artigo().encode()), ("listagem", listagem().encode()), ("misto", misto().encode()),
            ("vazia", b"<html><script>x</script></html>"), ("bom", b"\xef\xbb\xbf<p>" + b"a&amp;b " * 200 + b"</p>"),
            ("entidades", "<p>&#8217;&#x2019;&nbsp;&bogus;</p>".encode())]
    for pasta in (Path.home() / "detector-capa-gabarito", Path.home() / "ld2-controlo"):
        man = pasta / "MANIFESTO.json"
        if man.exists():
            for p in json.loads(man.read_text(encoding="utf-8"))["PAGINAS"]:
                f = pasta / p["FICHEIRO"]
                if f.exists():
                    pags.append((pasta.name + "/" + p["FICHEIRO"], f.read_bytes()))
    return pags


# ⚠️ DIVIDA DECLARADA (V1A, 2026-09-23), anterior a V1: nestas 8 das 251 paginas
# reais dos gabaritos, os DOIS detectores contam caracteres diferente — e o
# veredito e o mesmo nas 251. Causas medidas: em 6 o Node conta em unidades
# UTF-16 (um caractere fora do plano basico, ex. emoji, vale 2 — T11-009 x2,
# T7-031, T8-016, T12-030, T7-125); em 1 o `\s` do JavaScript apanha U+FEFF e o
# do Python nao (IT-T12-044). Em 1 (IT-T2-049) a causa e NAO SEI.
# Nao se corrige aqui: mudar a contagem e mudar o detector, e isso mede-se nos
# gabaritos antes (lei da D1). A lista so pode encolher.
CONTAGEM_DIVERGE_JA_CONHECIDA = {
    "IT-T11-009-CAPA_INDICE-e8ec6edfc1f8.html", "IT-T11-009-MATERIA-8a38fc35e8b2.html",
    "IT-T7-031-CAPA_INDICE-ff56a17355e8.html", "IT-T8-016-MATERIA-9259dc00c47a.html",
    "IT-T2-049-CAPA_INDICE-28043fdabbb4.html", "IT-T12-030-MATERIA-f5006cd2c544.html",
    "IT-T12-044-CAPA_INDICE-9ba614e536d2.html", "IT-T7-125-CAPA_INDICE-bb6856908f2c.html"}


class ParidadePythonNode(unittest.TestCase):
    """A mesma pagina, o mesmo contexto -> o mesmo veredito e o mesmo gate; e o mesmo
    retrato, salvo a divida de contagem declarada acima."""

    CONTEXTOS = [(INDICE, True), (INDICE, False), (INDICE + "x", True), (None, True)]

    def test_mesma_pagina_mesmo_veredito(self):
        pags = _paginas_de_paridade()
        with tempfile.TemporaryDirectory() as d:
            ent = Path(d) / "pags.json"
            ent.write_text(json.dumps([[n, b.hex()] for n, b in pags]), encoding="utf-8")
            node = _node("""import { readFileSync } from "node:fs";
const m = await import(pathToFileURL(%s).href);
const pags = JSON.parse(readFileSync(%s, "utf8"));
const ctx = %s; const c = %s;
const out = {};
for (const [n, hex] of pags) {
  const r = m.retratoDoHtml(Buffer.from(hex, "hex"));
  out[n] = { r, v: ctx.map(([url, regua]) => [m.veredito(r, c, { url, reguaAMandar: regua }),
                                               m.gateCapaNaoEMateria(c, r, { url, reguaAMandar: regua })]) };
}
console.log(JSON.stringify(out));""" % (json.dumps(MJS), json.dumps(ent.as_posix()),
                                       json.dumps(self.CONTEXTOS), json.dumps(CONTRATO)))
        self.assertEqual(len(pags), len(node))
        disparou = 0
        divergem = set()
        for n, b in pags:
            r = RH.retrato_do_html(b)
            self.assertEqual(r["CAPA_OU_MATERIA"], node[n]["r"]["CAPA_OU_MATERIA"], n)
            self.assertEqual(r["HTML_KIND"], node[n]["r"]["HTML_KIND"], n)
            if r != node[n]["r"]:
                divergem.add(n.replace("\\", "/").rsplit("/", 1)[-1])
            # a V1 e o gate, alimentados com o MESMO retrato (o do Node): o texto do
            # motivo leva as contagens, e a divida de contagem nao e da V1
            rn = node[n]["r"]
            py = [[RH.veredito(rn, url=u, contrato=CONTRATO, regua_a_mandar=g),
                   RH.gate_capa_nao_e_materia(CONTRATO, rn, url=u, regua_a_mandar=g)] for u, g in self.CONTEXTOS]
            self.assertEqual(py, node[n]["v"], n)
            # e com o retrato de cada um, o veredito e se o gate reprova sao iguais
            proprio = [[RH.veredito(r, url=u, contrato=CONTRATO, regua_a_mandar=g),
                        RH.gate_capa_nao_e_materia(CONTRATO, r, url=u, regua_a_mandar=g) is None]
                       for u, g in self.CONTEXTOS]
            self.assertEqual(proprio, [[v, gt is None] for v, gt in node[n]["v"]], n)
            disparou += py[0][0] != rn["CAPA_OU_MATERIA"]
        self.assertGreater(disparou, 0, "a paridade tem de ver a V1 a disparar, senao prova so o detector")
        self.assertLessEqual(divergem, CONTAGEM_DIVERGE_JA_CONHECIDA, "divergencia de contagem NOVA")

    def test_as_duas_constantes_iguais(self):
        node = _node("const m = await import(pathToFileURL(%s).href); console.log(JSON.stringify([m.V1_LIGADA, m.REGRA_V1]));"
                     % json.dumps(MJS))
        self.assertEqual([RH.V1_LIGADA, RH.REGRA_V1], node)


def _item(url, fonte="IT-T7-900", html=None):
    est = {"SOURCE_ID": fonte, "TEXTO": "Difesa integrata del pomodoro: peronospora e larva.",
           "DERIVED_ARTIFACT_ID": 7, "RAW_ASSET_ID": 7, "PARENT_SHA256": "d" * 64,
           "CAPTURED_AT": "2026-09-23T00:00:00Z",
           "RETRATO_DO_DETECTOR": RH.retrato_do_html((html or artigo()).encode()), "SOURCE_URL": url}
    return ORQ.item_documental_para_a_porta(est, source_id=fonte)


class APorta(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        antes = adm.QUARENTENA_HUMANA
        self.addCleanup(lambda: setattr(adm, "QUARENTENA_HUMANA", antes))
        adm.QUARENTENA_HUMANA = Path(self.tmp.name) / "H.jsonl"

    def porta(self, item, regua):
        with mock.patch.object(adm, "_fonte_bem_configurada", return_value=regua), \
             mock.patch.object(adm, "_contrato_da_fonte", return_value=CONTRATO):
            return adm._e_materia(item)

    def test_o_endereco_viaja_ate_a_porta(self):
        self.assertEqual(INDICE, _item(INDICE)["url_da_pagina"])
        self.assertNotIn("url_da_pagina", _item(None))

    def test_positivo_indice_de_fonte_com_regua_e_barrado_pela_v1(self):
        res, motivo, ev = self.porta(_item(INDICE), True)
        self.assertEqual(adm.NAO, res)
        self.assertEqual(RH.REGRA_V1, ev["v1"]["REGRA"])
        self.assertEqual("MATERIA_PROVAVEL", ev["v1"]["DETECTOR"])
        self.assertIn("V1", motivo)

    def test_negativo_indice_de_fonte_sem_regua_segue_o_detector(self):
        res, _, ev = self.porta(_item(INDICE), False)
        self.assertEqual(adm.SIM, res)
        self.assertNotIn("v1", ev)

    def test_negativo_noticia_da_fonte_com_regua_entra(self):
        self.assertEqual(adm.SIM, self.porta(_item(INDICE + "uma-noticia"), True)[0])

    def test_sem_endereco_a_v1_nao_se_aplica(self):
        self.assertEqual(adm.SIM, self.porta(_item(None), True)[0])

    def test_o_nao_sei_do_indice_com_regua_vira_capa_barrada_e_nao_quarentena(self):
        res, _, ev = self.porta(_item(INDICE, html=misto()), True)
        self.assertEqual((adm.NAO, "NAO_SEI"), (res, ev["v1"]["DETECTOR"]))
        self.assertNotIn("estado", ev)

    def test_a_regua_e_lida_do_dono_ready_split(self):
        with mock.patch.object(adm._da_curadoria("ready_split"), "regua_de", return_value="DETAIL/v1"):
            self.assertTrue(adm._fonte_bem_configurada("IT-T7-900"))
        with mock.patch.object(adm._da_curadoria("ready_split"), "regua_de", return_value="LEGACY"):
            self.assertFalse(adm._fonte_bem_configurada("IT-T7-900"))


class OTransporte(unittest.TestCase):
    def test_a_observacao_confirmada_leva_o_source_url(self):
        import preservar_coleta as PC
        linhas = [{"id": 5, "run_id": "R", "storage_path": "a/b.html", "sha256": "e" * 64,
                   "source_url": INDICE, "media_type": "text/html", "captured_at": None, "source_id": "IT-T7-900"}]
        obs = PC.observacoes_confirmadas({"RUN_ID": "R"}, linhas, {"CONFERIDOS": ["a/b.html"]})
        self.assertEqual(INDICE, obs[0]["SOURCE_URL"])

    def test_a_unidade_da_derivacao_leva_o_source_url(self):
        import ingresso as ING
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            f.write(b"<p>x</p>")
        self.addCleanup(Path(f.name).unlink)
        arm = mock.Mock()
        arm.caminho_local.return_value = f.name
        un, _ = ING.unidades_para_a_derivacao({"RAW_OBSERVATIONS": [
            {"RAW_OBSERVATION_ID": 5, "STORAGE_PATH": "a/b.html", "MEDIA_TYPE": "text/html",
             "SOURCE_ID": "IT-T7-900", "SOURCE_URL": INDICE}]}, arm)
        self.assertEqual(INDICE, un[0]["SOURCE_URL"])

    def test_derivacao_e_orquestrador_passam_o_campo(self):
        d = (RAIZ / "coleta" / "derivacao_forward.py").read_text(encoding="utf-8")
        o = (RAIZ / "orquestrador" / "orquestrador.py").read_text(encoding="utf-8")
        self.assertIn('"SOURCE_URL": u.get("SOURCE_URL")', d)
        self.assertIn('"SOURCE_URL": r.get("SOURCE_URL")', o.split("def pela_estruturacao")[1].split("\ndef ")[0])


class ORealReproduzAK1(unittest.TestCase):
    R = json.loads((RAIZ / "curadoria" / "V1A-MEDICAO-V1.json").read_text(encoding="utf-8"))

    def test_30_5_3_e_noticias_iguais(self):
        v, d = self.R["V1_LIGADA"], self.R["V1_DESLIGADA"]
        self.assertEqual([30, 5, 3], [v[f]["CAPAS_QUE_ENTRAM"] for f in
                                      ("ORIGINAL", "CONTROLO_DESENVOLVIMENTO", "CONTROLO_CEGA")])
        for f in v:
            self.assertEqual((d[f]["NOTICIAS_BARRADAS"], d[f]["NOTICIAS_RETIDAS"]),
                             (v[f]["NOTICIAS_BARRADAS"], v[f]["NOTICIAS_RETIDAS"]), f)
            self.assertLessEqual(v[f]["CAPAS_QUE_ENTRAM"], d[f]["CAPAS_QUE_ENTRAM"], f)
            self.assertEqual(self.R["K1_SIMULACAO"]["V1"][f]["CAPAS_QUE_ENTRAM"], v[f]["CAPAS_QUE_ENTRAM"], f)

    def test_a_v1_so_disparou_em_capas_de_fontes_com_regua(self):
        for l in self.R["PAGINAS_ONDE_A_V1_DISPAROU"]:
            self.assertEqual(("CAPA", True), (l["VEREDITO_HUMANO"], l["REGUA_A_MANDAR"]), l)


if __name__ == "__main__":
    unittest.main()
