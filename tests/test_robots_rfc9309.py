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

    def test_4xx_e_ausencia(self):
        for st in (400, 401, 403, 404, 410, 429 - 1):
            with self.subTest(st=st):
                rp = RR.de_resposta(st)
                self.assertEqual(RR.AUSENTE, rp.estado)
                self.assertTrue(rp.can_fetch(UA, "https://ex.it/qualquer"))

    def test_5xx_e_rede_sao_nao_sei_e_recusa(self):
        for st in (500, 502, 503):
            with self.subTest(st=st):
                self.assertFalse(RR.de_resposta(st).can_fetch(UA, "https://ex.it/"))
        rp = RR.de_resposta(None, erro="URLError")
        self.assertEqual(RR.INACESSIVEL, rp.estado)
        self.assertFalse(rp.can_fetch(UA, "https://ex.it/"))

    def test_html_no_lugar_do_robots_e_ilegivel_e_recusa(self):
        for corpo in (b"<!DOCTYPE html><html>...", b"  <html><body>login</body></html>"):
            with self.subTest(corpo=corpo[:12]):
                rp = RR.de_resposta(200, corpo)
                self.assertEqual(RR.ILEGIVEL, rp.estado)
                self.assertFalse(rp.can_fetch(UA, "https://ex.it/"))

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


if __name__ == "__main__":
    unittest.main()
