#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D34: o leitor UNICO de robots.txt, pela RFC 9309 (`coleta/robots_rfc9309.py`).

1. os casos da norma (regra mais especifica, empate -> Allow, `*` e `$`, grupo do agente,
   estados da resposta) e o caso medido que abriu isto: o SFR Lombardia;
2. o gemeo Node (`coleta/italy_pilot_collect.mjs`) le igual, caso a caso;
3. nenhum segundo leitor: nada fora do dono importa `urllib.robotparser` nem le linhas
   Allow/Disallow por conta propria; os tres pontos (gate_de_rota, descobrir, scrap_http)
   perguntam ao dono.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "coleta"))
import robots_rfc9309 as RR   # noqa: E402

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0"
LOMBARDIA = """User-agent: *
Disallow: /wps/
Allow: /wps/portal/site/sfr
Allow: /wps/wcm/connect
Sitemap: http://www.fitosanitario.regione.lombardia.it/sitemap.xml
Crawl-delay: 1  #Tempo di attesa in secondi fra una richiesta e un altra
"""

# (robots, agente, caminho, permitido) — a mesma tabela vai ao gemeo Node
CASOS = [
    # o caso medido (IA-CUR, 24/09): a regra mais especifica vence
    (LOMBARDIA, UA, "/wps/portal/site/sfr", True),
    (LOMBARDIA, UA, "/wps/portal/site/sfr/home", True),
    (LOMBARDIA, UA, "/wps/portal/outro", False),
    (LOMBARDIA, UA, "/", True),
    # mais longo vence, venha antes ou depois
    ("User-agent: *\nAllow: /p\nDisallow: /", UA, "/page", True),
    ("User-agent: *\nDisallow: /\nAllow: /p", UA, "/page", True),
    ("User-agent: *\nAllow: /p\nDisallow: /", UA, "/x", False),
    # empate -> Allow
    ("User-agent: *\nDisallow: /pagina\nAllow: /pagina", UA, "/pagina", True),
    # RFC 9309 §5.2 (exemplos)
    ("User-agent: *\nAllow: /example/page/\nDisallow: /example/page/disallowed.gif", UA,
     "/example/page/disallowed.gif", False),
    ("User-agent: *\nAllow: /example/page/\nDisallow: /example/page/disallowed.gif", UA,
     "/example/page/ok.html", True),
    ("User-agent: *\nAllow: /$\nDisallow: /", UA, "/", True),
    ("User-agent: *\nAllow: /$\nDisallow: /", UA, "/page.html", False),
    # curingas
    ("User-agent: *\nDisallow: /*.gif$", UA, "/fotos/a.gif", False),
    ("User-agent: *\nDisallow: /*.gif$", UA, "/fotos/a.gif?x=1", True),
    ("User-agent: *\nDisallow: /*?", UA, "/lista?pagina=2", False),
    ("User-agent: *\nDisallow: /*?", UA, "/lista", True),
    ("User-agent: *\nDisallow: /a*b", UA, "/a/x/b/c", False),
    # Disallow vazio nao proibe; sem regra que case = permitido
    ("User-agent: *\nDisallow:", UA, "/tudo", True),
    ("User-agent: *\nDisallow: /privado/", UA, "/publico/", True),
    # o grupo do nosso token vence o *; maiusculas no agente nao importam
    ("User-agent: *\nDisallow: /\n\nUser-agent: MOZILLA\nAllow: /", UA, "/x", True),
    ("User-agent: sintoniascrap\nDisallow: /api/\n\nUser-agent: *\nDisallow: /",
     "SintoniaScrap/1.0 (+EAME)", "/perfil", True),
    ("User-agent: sintoniascrap\nDisallow: /api/\n\nUser-agent: *\nDisallow: /",
     "SintoniaScrap/1.0 (+EAME)", "/api/v1", False),
    # grupos do mesmo agente juntam-se
    ("User-agent: *\nDisallow: /a/\n\nUser-agent: *\nDisallow: /b/", UA, "/b/x", False),
    # varios User-agent seguidos partilham o grupo
    ("User-agent: outro\nUser-agent: *\nDisallow: /c/", UA, "/c/1", False),
    # nenhum grupo para nos nem para * -> permitido
    ("User-agent: googlebot\nDisallow: /", UA, "/x", True),
    # regra antes de qualquer User-agent nao e de ninguem
    ("Disallow: /\nUser-agent: *\nAllow: /", UA, "/x", True),
    # %-escape: /~joe e /%7Ejoe sao o mesmo caminho
    ("User-agent: *\nDisallow: /%7Ejoe/", UA, "/~joe/index.html", False),
    ("User-agent: *\nDisallow: /~joe/", UA, "/%7Ejoe/index.html", False),
    # /robots.txt e sempre permitido
    ("User-agent: *\nDisallow: /", UA, "/robots.txt", True),
]


def decide(robots, agente, caminho):
    return RR.de_resposta(200, robots).decidir(agente, "https://ex.it" + caminho)


class OsCasosDaNorma(unittest.TestCase):

    def test_casos(self):
        for robots, agente, caminho, esperado in CASOS:
            with self.subTest(robots=robots[:40], caminho=caminho):
                self.assertEqual(esperado, decide(robots, agente, caminho).permite)

    def test_a_decisao_diz_a_regra_que_decidiu(self):
        d = decide(LOMBARDIA, UA, "/wps/portal/site/sfr")
        self.assertEqual("Allow: /wps/portal/site/sfr", d.regra)
        self.assertEqual("Disallow: /wps/", decide(LOMBARDIA, UA, "/wps/x").regra)

    def test_crawl_delay_do_grupo(self):
        self.assertEqual(1.0, RR.de_resposta(200, LOMBARDIA).crawl_delay(UA))

    def test_can_fetch_mantem_a_assinatura_antiga(self):
        rp = RR.de_resposta(200, LOMBARDIA)
        self.assertTrue(rp.can_fetch(UA, "https://www.fitosanitario.regione.lombardia.it/wps/portal/site/sfr"))


class OsEstadosDaResposta(unittest.TestCase):
    """RFC 9309 §2.3.1: 4xx = sem robots (pode); 5xx/rede = tudo proibido; HTML = ilegivel."""

    def test_4xx_que_nao_e_401_403_e_ausencia(self):
        for st in (400, 404, 410, 418, 429):
            with self.subTest(st=st):
                rp = RR.de_resposta(st)
                self.assertEqual(RR.AUSENTE, rp.estado)
                self.assertTrue(rp.can_fetch(UA, "https://ex.it/qualquer"))

    def test_401_403_e_ACCESS_DENIED_recusa_por_prudencia_nao_disallow(self):
        """D39: mais conservador que a RFC (que diria «pode»), e declarado."""
        for st in (401, 403):
            with self.subTest(st=st):
                rp = RR.de_resposta(st)
                self.assertEqual("ROBOTS_ACCESS_DENIED", rp.estado)
                d = rp.decidir(UA, "https://ex.it/qualquer")
                self.assertFalse(d.permite)
                self.assertTrue(d.regra.startswith("ROBOTS_ACCESS_DENIED"))
                self.assertNotIn("Disallow:", d.regra)

    def test_5xx_e_rede_sao_nao_sei_e_recusa(self):
        for st in (500, 502, 503):
            with self.subTest(st=st):
                self.assertFalse(RR.de_resposta(st).can_fetch(UA, "https://ex.it/"))
        rp = RR.de_resposta(None, erro="URLError")
        self.assertEqual(RR.INACESSIVEL, rp.estado)
        self.assertFalse(rp.can_fetch(UA, "https://ex.it/"))

    def test_html_no_lugar_do_robots_e_INVALID_CONTENT_recusa_nao_disallow(self):
        for corpo in (b"<!DOCTYPE html><html>...", b"  <html><body>login</body></html>"):
            with self.subTest(corpo=corpo[:12]):
                rp = RR.de_resposta(200, corpo)
                self.assertEqual("ROBOTS_INVALID_CONTENT", rp.estado)
                d = rp.decidir(UA, "https://ex.it/")
                self.assertFalse(d.permite)
                self.assertTrue(d.regra.startswith("ROBOTS_INVALID_CONTENT"))
                self.assertNotIn("Disallow:", d.regra)

    def test_as_recusas_d39_sao_recusas_e_nenhuma_e_lido(self):
        self.assertTrue({RR.INVALID_CONTENT, RR.ACCESS_DENIED, RR.INACESSIVEL, RR.ILEGIVEL} <= RR.RECUSAS)
        self.assertNotIn(RR.LIDO, RR.RECUSAS)
        self.assertNotIn(RR.AUSENTE, RR.RECUSAS)

    def test_proibicao_real_continua_bloqueada(self):
        rp = RR.de_resposta(200, "User-agent: *\nDisallow: /")
        self.assertFalse(rp.can_fetch(UA, "https://ex.it/noticias/1"))


@unittest.skipUnless(shutil.which("node"), "sem node nesta maquina")
class OGemeoNodeLeIgual(unittest.TestCase):
    """O coletor (Node) ja lia pela norma; o leitor Python tem de dar o MESMO veredito."""

    def test_paridade_caso_a_caso(self):
        """O gemeo decide sempre com o token do UA do coletor («mozilla»): comparam-se os casos
        com esse agente (os de outro agente so o Python os tem)."""
        mod = (RAIZ / "coleta" / "italy_pilot_collect.mjs").as_uri()
        idx = [i for i, (_, a, _, _) in enumerate(CASOS) if RR.token_de(a) == "mozilla"]
        self.assertGreater(len(idx), 20)
        casos = [{"r": CASOS[i][0], "c": CASOS[i][2]} for i in idx]
        js = ("import(%s).then(m => { const cs = JSON.parse(process.argv[1]);"
              " console.log(JSON.stringify(cs.map(x => m.robotsPermite(m.lerRobots(x.r), x.c)))); })"
              % json.dumps(mod))
        r = subprocess.run(["node", "--input-type=module", "-e", js, json.dumps(casos)],
                           capture_output=True, text=True, timeout=60, cwd=str(RAIZ))
        self.assertEqual(0, r.returncode, r.stderr[-800:])
        node = json.loads(r.stdout.strip().splitlines()[-1])
        diverge = [(CASOS[i][2], CASOS[i][0][:40], decide(*CASOS[i][:3]).permite, node[k])
                   for k, i in enumerate(idx) if decide(*CASOS[i][:3]).permite != node[k]]
        self.assertEqual([], diverge)


class NenhumSegundoLeitor(unittest.TestCase):
    DONO = "coleta/robots_rfc9309.py"
    PROIBIDO = re.compile(r"^\s*(import\s+urllib\.robotparser|from\s+urllib\s+import\s+robotparser)"
                          r"|RobotFileParser\s*\("
                          r"|==\s*[\"']disallow[\"']|[\"']disallow[\"']\s*\)|\(\s*[\"']allow[\"']\s*,\s*[\"']disallow[\"']",
                          re.M | re.I)

    def _codigo(self):
        for raiz, dirs, fich in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "__pycache__", "BASELINE", "data",
                                                    "provas", "tests")]
            for f in fich:
                if f.endswith(".py"):
                    p = Path(raiz, f)
                    yield p.relative_to(RAIZ).as_posix(), p.read_text(encoding="utf-8", errors="replace")

    def test_so_o_dono_le_robots(self):
        leitores = sorted(rel for rel, txt in self._codigo() if self.PROIBIDO.search(txt))
        self.assertEqual([self.DONO], leitores, "nasceu (ou sobrou) um segundo leitor de robots.txt")

    def test_os_tres_pontos_perguntam_ao_dono(self):
        for rel in ("curadoria/gate_de_rota.py", "curadoria/descobrir.py", "coleta/scrap_http.py"):
            with self.subTest(rel=rel):
                self.assertIn("import robots_rfc9309 as RR", (RAIZ / rel).read_text(encoding="utf-8"))

    def test_o_portao_do_curator_abre_o_sfr_lombardia(self):
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import gate_de_rota as G   # noqa: PLC0415
        rp = RR.de_resposta(200, LOMBARDIA)
        self.assertTrue(G.permitido("https://www.fitosanitario.regione.lombardia.it/wps/portal/site/sfr", rp))
        self.assertFalse(G.permitido("https://www.fitosanitario.regione.lombardia.it/wps/portal/x", rp))


    def test_a_descoberta_decide_pelo_dono(self):
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import descobrir as D   # noqa: PLC0415
        h = "www.fitosanitario.regione.lombardia.it"
        D._robots_cache[h] = RR.de_resposta(200, LOMBARDIA)
        try:
            self.assertTrue(D._permitido("https://%s/wps/portal/site/sfr" % h))
            self.assertFalse(D._permitido("https://%s/wps/portal/x" % h))
        finally:
            D._robots_cache.pop(h, None)

    def test_o_portao_de_transporte_decide_pelo_dono(self):
        import scrap_http as H   # noqa: PLC0415
        base = "https://www.fitosanitario.regione.lombardia.it"
        H._ROBOTS[base] = (RR.de_resposta(200, LOMBARDIA), "LIDO")
        try:
            self.assertTrue(H.permitido(base + "/wps/portal/site/sfr")[0])
            self.assertFalse(H.permitido(base + "/wps/portal/x")[0])
        finally:
            H._ROBOTS.pop(base, None)


    def test_o_transporte_recusa_pelo_nome_e_a_excecao_do_dono_nao_alcanca(self):
        import scrap_http as H   # noqa: PLC0415
        base = "https://negado.example"
        for rp in (RR.de_resposta(403), RR.de_resposta(200, b"<!doctype html><html></html>")):
            with self.subTest(estado=rp.estado):
                H._ROBOTS[base] = (rp, rp.estado)
                try:
                    with mock.patch.object(H, "autorizacao_actual",
                                           side_effect=AssertionError("a excecao do dono nao atravessa D39")):
                        ok, motivo = H.permitido(base + "/x")
                    self.assertFalse(ok)
                    self.assertTrue(motivo.startswith(rp.estado))
                finally:
                    H._ROBOTS.pop(base, None)


class ORoboRegistaARecusaComNome(unittest.TestCase):
    """D39: no robo, a recusa e BLOCK com CLASSE = nome do estado; o livro (vocabulario fechado)
    diz rota bloqueada e guarda ROBOTS_ESTADO ao lado; o PORQUE nunca diz Disallow."""

    def _contrato(self):
        return {"SOURCE_ID": "IT-X-901", "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY",
                                                          "INDEX_URL": "https://negado.example/news/"}}

    def test_etapa_devolve_block_com_o_nome(self):
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import worker as W   # noqa: PLC0415
        for rp, nome in ((RR.de_resposta(403), "ROBOTS_ACCESS_DENIED"),
                         (RR.de_resposta(200, b"<!DOCTYPE html>"), "ROBOTS_INVALID_CONTENT")):
            with self.subTest(nome=nome), mock.patch.object(W.GATE, "robots_de", return_value=(rp, rp.porque)):
                r, d = W.etapa_validate_route("IT-X-901", self._contrato())
                self.assertEqual("BLOCK", r)
                self.assertEqual(nome, d["CLASSE"])
                self.assertEqual(nome, d["ROBOTS_ESTADO"])
                self.assertNotIn("Disallow:", d["PORQUE"]); self.assertTrue(d["PORQUE"].startswith(nome))

    def test_404_continua_a_passar(self):
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import worker as W   # noqa: PLC0415
        rp = RR.de_resposta(404)
        with mock.patch.object(W.GATE, "robots_de", return_value=(rp, rp.porque)):
            r, _ = W.etapa_validate_route("IT-X-901", self._contrato())
        self.assertEqual("OK", r)

    def test_o_livro_diz_rota_bloqueada_com_o_nome_ao_lado(self):
        import tempfile   # noqa: PLC0415
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import fila as F        # noqa: PLC0415
        import lifecycle as LC  # noqa: PLC0415
        import worker as W      # noqa: PLC0415
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            antes = (LC.LIVRO, F.FILA, W.EVIDENCIA, W.PULSO)
            LC.LIVRO, F.FILA, W.EVIDENCIA, W.PULSO = (d / "L.json", d / "Q.json", d / "E.json", d / "P.json")
            try:
                LC.registar("IT-X-901", LC.CANARY_PENDING, "prova")
                F.enfileirar("IT-X-901", F.VALIDATE_ROUTE, priority=55)
                rp = RR.de_resposta(403)
                with mock.patch.object(W.GATE, "robots_de", return_value=(rp, rp.porque)):
                    W.executar_uma(F.proxima(), {"IT-X-901": self._contrato()})
                ult = LC.historia("IT-X-901")[-1]
                self.assertEqual(LC.CONTRACT_READY_ROUTE_BLOCKED, ult["NEW_STATE"])
                self.assertEqual("ROBOTS_ACCESS_DENIED", ult["ROBOTS_ESTADO"])
                self.assertNotIn("Disallow:", ult["REASON"]); self.assertTrue(ult["REASON"].startswith("ROBOTS_ACCESS_DENIED"))
            finally:
                LC.LIVRO, F.FILA, W.EVIDENCIA, W.PULSO = antes


class AGuardaDoRobotsInteiro(unittest.TestCase):
    """D34: a prova guarda a impressao digital do robots INTEIRO (sha256 + tamanho), nao so os 120
    primeiros caracteres — medido: 228 de 391 robots lidos ficavam sem a regra que decidia."""

    def test_sha256_e_do_ficheiro_inteiro_e_a_regra_vem_de_depois_dos_120(self):
        import hashlib   # noqa: PLC0415
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import worker as W   # noqa: PLC0415
        texto = "User-agent: *\n" + "".join("Disallow: /arquivo-%03d/\n" % i for i in range(12)) \
                + "Disallow: /news/\n"
        self.assertGreater(texto.index("/news/"), 120)
        rp = RR.de_resposta(200, texto.encode("utf-8"))
        contrato = {"SOURCE_ID": "IT-X-902", "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY",
                                                              "INDEX_URL": "https://longo.example/news/"}}
        with mock.patch.object(W.GATE, "robots_de", return_value=(rp, rp.texto)):
            r, d = W.etapa_validate_route("IT-X-902", contrato)
        self.assertEqual("BLOCK", r)
        self.assertEqual(hashlib.sha256(texto.encode("utf-8")).hexdigest(), d["ROBOTS_SHA256"])
        self.assertEqual(len(texto), d["ROBOTS_CARACTERES"])
        self.assertEqual("Disallow: /news/", d["REGRA"])
        self.assertNotIn("/news/", d["ROBOTS"], "o recorte de 120 nao contem a regra — por isso o sha")


class OScriptDeEnfileirarAs52(unittest.TestCase):
    """D39 (3): so mostra por omissao; READY primeiro; recusa um leitor que nao seja o D39."""

    def _modulo(self, d):
        import importlib.util   # noqa: PLC0415
        spec = importlib.util.spec_from_file_location(
            "e52", RAIZ / "provas" / "robots_rfc" / "enfileirar_as_52.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.MEDICAO = d / "M.json"
        m.MEDICAO.write_text(json.dumps({"MUDAM": [
            {"SOURCE_ID": s, "ANTIGO": True, "NOVO_D39": False, "REGRA_D39": "Disallow: /*?"}
            for s in ("IT-X-001", "IT-X-002", "IT-X-003")]}), encoding="utf-8")
        m.CONTRATOS = d / "C.json"
        m.CONTRATOS.write_text(json.dumps({"FONTES": [{"SOURCE_ID": "IT-X-001"}, {"SOURCE_ID": "IT-X-002"}]}),
                               encoding="utf-8")
        return m

    def test_so_mostra_ready_primeiro_e_sem_contrato_fica_fora(self):
        import tempfile   # noqa: PLC0415
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            m = self._modulo(d)
            antes = (m.LC.LIVRO, m.F.FILA)
            m.LC.LIVRO, m.F.FILA = d / "L.json", d / "Q.json"
            try:
                m.LC.registar("IT-X-002", m.LC.CANARY_PENDING, "prova")
                m.LC.registar("IT-X-002", m.LC.READY_FOR_COLLECTION, "prova", evidence_ref="EV")
                m.LC.registar("IT-X-001", m.LC.CANARY_PENDING, "prova")
                _, entra, fora = m.plano()
                self.assertEqual(["IT-X-002", "IT-X-001"], [e["SOURCE_ID"] for e in entra])
                self.assertEqual(85, entra[0]["PRIORIDADE"])
                self.assertEqual(["IT-X-003"], [s for s, _ in fora])
                with mock.patch.object(sys, "argv", ["x"]):
                    m.main()
                self.assertFalse((d / "Q.json").exists(), "sem --aplicar nao se escreve na fila")
                with mock.patch.object(sys, "argv", ["x", "--aplicar"]):
                    m.main()
                tarefas = json.loads((d / "Q.json").read_text(encoding="utf-8"))["TAREFAS"]
                self.assertEqual({("IT-X-001", "VALIDATE_ROUTE"), ("IT-X-002", "VALIDATE_ROUTE")},
                                 {(x["SOURCE_ID"], x["TASK_TYPE"]) for x in tarefas})
            finally:
                m.LC.LIVRO, m.F.FILA = antes

    def test_recusa_leitor_que_nao_e_o_d39(self):
        import tempfile   # noqa: PLC0415
        with tempfile.TemporaryDirectory() as tmp:
            m = self._modulo(Path(tmp))
            with mock.patch.object(m.RR, "VERSAO", "ROBOTS/RFC9309-v1"), self.assertRaises(SystemExit):
                m.plano()


if __name__ == "__main__":
    unittest.main()
