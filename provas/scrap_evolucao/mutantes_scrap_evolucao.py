"""SCRAP-EVOLUCAO · prova de mutacao — cada regra nova, estragada de proposito, tem de fazer um teste falhar.

    py provas/scrap_evolucao/mutantes_scrap_evolucao.py [saida.json]

Cada mutante troca UM trecho exacto num ficheiro, corre so os testes que guardam essa regra e repoe os bytes
originais (conferidos por sha256) — nunca `git checkout`. Os .pyc vao para uma pasta propria por mutante
(`-X pycache_prefix`): um mutante do mesmo tamanho nao engana a cache.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = sys.executable
T_EVO = [PY, "-m", "unittest", "test_scrap_evolucao"]
T_XHR = [PY, "-m", "unittest", "test_captura_xhr"]
T_FEED = ["node", "regras/feed_discovery_test.mjs"]
T_FEED_LOCAL = ["node", "provas/feed_local.mjs"]

MUTANTES = [
    ("FEED: sem o limite D40 de 3 alvos", "regras/motor_de_rota.mjs",
     "const limite = Number.isInteger(aq.MAX_TARGETS) ? aq.MAX_TARGETS : ALVOS_POR_FONTE_D40;\n    return comFeed(",
     "const limite = Number.isInteger(aq.MAX_TARGETS) ? aq.MAX_TARGETS : 99;\n    return comFeed(", T_FEED, "."),
    ("FEED: <updated> passa a contar como publicacao", "regras/motor_de_rota.mjs",
     'Object.freeze(["pubDate", "dc:date", "published"])',
     'Object.freeze(["pubDate", "dc:date", "published", "updated"])', T_FEED, "."),
    ("FEED: itens de outro site entram", "regras/motor_de_rota.mjs",
     "if (aq.SAME_HOST !== false && hostDe(it.url) !== hostDe(aq.FEED_URL)) continue;", "", T_FEED, "."),
    ("COLETOR: item sem data no feed vira null em vez de NAO SEI", "coleta/italy_pilot_collect.mjs",
     'PUBLISHED_AT: alvo.publicadoNoIndice.VALOR ?? "NAO SEI",', "PUBLISHED_AT: alvo.publicadoNoIndice.VALOR ?? null,",
     T_FEED_LOCAL, "."),
    ("ROTA: Referer do Google ligado", "coleta/rota_navegador.py",
     '"Accept-Language": f["ACCEPT_LANGUAGE"]}',
     '"Accept-Language": f["ACCEPT_LANGUAGE"], "Referer": "https://www.google.com/"}', T_EVO, "tests"),
    ("ROTA: medir nao conta o robots no teto", "coleta/rota_navegador.py",
     'out["PEDIDOS_POR_DOMINIO"][dom] += 1                                # o robots.txt ja foi um pedido', "pass",
     T_EVO, "tests"),
    ("ROTA: medir ignora o egresso", "coleta/rota_navegador.py",
     'if g.get("EGRESS_COUNTRY_CODE") != "IT":\n        return fim("EGRESSO_NAO_IT: nada saiu")', "pass", T_EVO, "tests"),
    ("CANARIO: a rota vaza para o canario seguinte", "curadoria/canario.py",
     "            _ROTA.reset(marca)", "            pass", T_EVO, "tests"),
    ("CANARIO: resultado sem a rota na proveniencia", "curadoria/canario.py",
     "            r.update(RN.proveniencia(rota))", "            pass", T_EVO, "tests"),
    ("PROVA: a ficha pede NAVEGADOR e o leitor ignora", "curadoria/colher_prova_territorio.py",
     "r = buscar(u) if rota == RN.ROTA_DECLARADA else buscar(u, rota=rota)", "r = buscar(u)", T_EVO, "tests"),
    ("PROVA: 429 nao castiga", "curadoria/colher_prova_territorio.py",
     "        espera.depois(u, http=r[0], erro=r[2])\n", "", T_EVO, "tests"),
    ("LIGACOES: <link> volta a contar como pagina", "curadoria/colher_prova_territorio.py",
     "<(?:a|area)\\b", "<(?:a|area|link|use)\\b", T_EVO, "tests"),
    ("LIGACOES: parametros sem ordem canonica", "curadoria/colher_prova_territorio.py",
     "urlencode(sorted(parse_qsl(p.query, keep_blank_values=True)), quote_via=quote)",
     "urlencode(parse_qsl(p.query, keep_blank_values=True), quote_via=quote)", T_EVO, "tests"),
    ("LIGACOES: &amp; nao desfeito", "curadoria/colher_prova_territorio.py",
     "h = unescape(next(g for g in m.groups() if g is not None)).strip()",
     "h = next(g for g in m.groups() if g is not None).strip()", T_EVO, "tests"),
    ("ESPERA: bloqueio nao dobra", "coleta/espera_por_dominio.py",
     "novo = min(max(atual * 2, self.base * 2, 1.0), self.maximo)", "novo = atual", T_EVO, "tests"),
    ("ESPERA: Retry-After ignorado", "coleta/espera_por_dominio.py",
     "            novo = min(max(novo, ra), self.maximo)", "            pass", T_EVO, "tests"),
    ("ESPERA: resposta boa desce abaixo da base", "coleta/espera_por_dominio.py",
     "novo = max(self.base, atual / 2)", "novo = atual / 2", T_EVO, "tests"),
    ("SCRAP_HTTP: pausa fixa de novo", "coleta/scrap_http.py",
     "    time.sleep(d['ESPERA_SEGUINTE_S'])", "    time.sleep(PAUSA_ENTRE_CHAMADAS)", T_EVO, "tests"),
    ("XHR: o porteiro nao cobra o teto", "ferramentas/captura_xhr.py",
     "if self.gastos.get(d, 0) >= self.teto:", "if False:", T_XHR, "tests"),
    ("XHR: folha de estilo e imagem saem", "ferramentas/captura_xhr.py",
     'TIPOS_QUE_NUNCA_SAEM = frozenset({"Image", "Font", "Stylesheet", "Media"})',
     'TIPOS_QUE_NUNCA_SAEM = frozenset({"Font", "Media"})', T_XHR, "tests"),
    ("XHR: POST vira proposta", "ferramentas/captura_xhr.py",
     'if c.get("METODO") != "GET" or c.get("HTTP") != 200:', 'if c.get("HTTP") != 200:', T_XHR, "tests"),
    ("XHR: robots nao conta", "ferramentas/captura_xhr.py",
     'out["PEDIDOS_POR_DOMINIO"][dom] = 1', 'out["PEDIDOS_POR_DOMINIO"][dom] = 0', T_XHR, "tests"),
    ("P6: a emenda dada como em vigor", "coleta/scrap_capacidades.py",
     "EMENDAS_EM_VIGOR = frozenset()", "EMENDAS_EM_VIGOR = frozenset({'COL-LAW-220'})", T_EVO, "tests"),
    ("P6: promessa sem perguntar se esta ligada", "coleta/scrap_capacidades.py",
     "    return estado(nome) not in SEM_PROMESSA and ativa(nome)\n",
     "    return estado(nome) not in SEM_PROMESSA\n", T_EVO, "tests"),
    ("P6: validador aceita pagina desenhada sem rotulo", "coleta/scrap_capacidades.py",
     "and ROTULO_DO_CORPO.get(n) != BROWSER_RENDERED_EXTRACT:", "and False:", T_EVO, "tests"),
    ("D91 CANARIO: o item nao pede licenca ao robots", "curadoria/canario.py",
     "    recusa = _recusa_do_robots(url)\n", "    recusa = None\n", T_EVO, "tests"),
    ("D91 CANARIO: robots ilegivel vira licenca", "curadoria/canario.py",
     '    if "inacessivel" in origem:\n        return "ROBOTS_ILEGIVEL', '    if False:\n        return "ROBOTS_ILEGIVEL',
     T_EVO, "tests"),
    ("D91 XHR: o navegador pede sem perguntar ao robots", "ferramentas/captura_xhr.py",
     "            ok, motivo = self.robots(url)\n            if not ok:", "            ok, motivo = self.robots(url)\n            if False:",
     T_XHR, "tests"),
    ("D91 XHR: ler o robots de uma origem nova nao conta no teto", "ferramentas/captura_xhr.py",
     "                self.gastos[d] = self.gastos.get(d, 0) + 1          # ler o robots desta origem e um pedido\n",
     "", T_XHR, "tests"),
    ("D91 COLETOR: o feed e os itens sem licenca do robots", "coleta/italy_pilot_collect.mjs",
     'if (rb.estado === "LIDO" && !robotsPermite(rb.grupos, u.pathname + u.search))',
     'if (false && rb.estado === "LIDO" && !robotsPermite(rb.grupos, u.pathname + u.search))',
     ["node", "provas/feed_robots_local.mjs"], "."),
    ("FEED-MEDIR: janela ignora os livros", "provas/scrap_evolucao/feeds_janela.py",
     '        livre = not fecha or agora >= fecha\n', '        livre = True\n', T_EVO, "tests"),
    ("FEED-MEDIR: --so ignorado", "provas/scrap_evolucao/medir_feeds_com_rede.py",
     "if not so or s in so}", "if True}", T_EVO, "tests"),
    ("P6: qualquer fonte pode pedir", "coleta/scrap_capacidades.py",
     "    return lista is None or source_id in lista\n", "    return True\n", T_EVO, "tests"),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(saida=None):
    res = []
    for nome, rel, antes, depois, cmd, cwd in MUTANTES:
        p = os.path.join(RAIZ, rel)
        orig = open(p, "rb").read()
        texto = orig.decode("utf-8")
        n = texto.count(antes)
        if n != 1:
            res.append({"MUTANTE": nome, "ESTADO": "ANCORA_PARTIDA", "OCORRENCIAS": n})
            print("ANCORA_PARTIDA", nome, n)
            continue
        cache = tempfile.mkdtemp(prefix="mut-evo-pyc-")
        env = dict(os.environ, PYTHONPYCACHEPREFIX=cache, PYTHONUTF8="1", NODE_DISABLE_COMPILE_CACHE="1")
        for k in ("SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA"):
            env.pop(k, None)
        try:
            with open(p, "wb") as f:
                f.write(texto.replace(antes, depois).encode("utf-8"))
            r = subprocess.run(cmd, cwd=os.path.join(RAIZ, cwd), env=env, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=900)
            estado = "MORTO" if r.returncode != 0 else "SOBREVIVEU"
        finally:
            with open(p, "wb") as f:
                f.write(orig)
        assert sha(open(p, "rb").read()) == sha(orig), "nao repus %s" % rel
        res.append({"MUTANTE": nome, "FICHEIRO": rel, "ESTADO": estado})
        print("%-11s %s" % (estado, nome))
    mortos = sum(1 for x in res if x["ESTADO"] == "MORTO")
    out = {"MUTANTES": len(res), "MORTOS": mortos, "RESULTADOS": res}
    if saida:
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
    print("MORTOS %d/%d" % (mortos, len(res)))
    return 0 if mortos == len(res) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
