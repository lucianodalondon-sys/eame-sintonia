"""FEED-LIGADO · prova de mutacao — cada regra nova, estragada de proposito, tem de fazer um teste falhar.

    py provas/scrap_evolucao/mutantes_feed_ligado.py [saida.json]

O metodo de `mutantes_scrap_evolucao.py`: cada mutante troca UM trecho exacto num ficheiro (a ancora tem de
aparecer uma vez so), corre os testes que guardam a regra e repoe os bytes originais, conferidos por sha256 —
nunca `git checkout`. Os .pyc vao para uma pasta propria por mutante.

Os quatro que a missao nomeou vem primeiro: feed fora do teto · BODY_FROM_FEED rotulado como pagina ·
robots ilegivel = permissao · 304 fora do teto.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = sys.executable
T_LOCAL = ["node", "provas/scrap_evolucao/feed_ligado_local.mjs"]
T_FEED = ["node", "regras/feed_discovery_test.mjs"]
T_PY = [PY, "-m", "unittest", "test_feed_ligado"]
COL = "coleta/italy_pilot_collect.mjs"
MOTOR = "regras/motor_de_rota.mjs"

MUTANTES = [
    # ── os quatro da missao ────────────────────────────────────────────────────────────────────────
    ("TETO: o pedido ao feed nao conta (nem no livro de 24 h, nem no dominio)", COL,
     "  if (livro24h()) {\n    let r;",                     # D124-REBASE: a ancora do codigo novo, o mesmo sitio
     "  if (livro24h() && !/\\/feed\\/?$/.test(url)) {\n    let r;", T_LOCAL, "."),
    ("ROTULO: o corpo do feed sai rotulado como pagina (RAW_PRESERVED)", COL,
     'RAW_EVIDENCE_STATE: "BODY_FROM_FEED",', 'RAW_EVIDENCE_STATE: "RAW_PRESERVED",', T_LOCAL, "."),
    ("ROBOTS: ILEGIVEL passa a ser permissao", COL,
     '  if (rb.estado === "ILEGIVEL") return { recusado: "ROBOTS_ILEGIVEL", porque: rb.porque };\n', "", T_LOCAL, "."),
    ("TETO: o pedido condicional (o que volta 304) nao reserva no livro de 24 h", COL,
     "  if (livro24h()) {\n    let r;",                     # D124-REBASE: a ancora do codigo novo, o mesmo sitio
     "  if (livro24h() && !condicional?.cabecalhos?.length) {\n    let r;", T_LOCAL, "."),
    # ── o resto das regras novas ───────────────────────────────────────────────────────────────────
    ("ROTULO: o ficheiro do corpo do feed tem nome de pagina", COL,
     "const nomeRaw = doFeed ? nomeDoCorpoDoFeed(alvo.nome) : alvo.nome;", "const nomeRaw = alvo.nome;", T_LOCAL, "."),
    ("ROTULO: o executor le o corpo do feed como pagina", "coleta/italy_executor.py",
     '    if obs.get("RAW_EVIDENCE_STATE") == "BODY_FROM_FEED":\n        return None\n', "", T_PY, "tests"),
    ("TEMPO: a data do feed vira FACT_TIME do corpo", COL,
     'FACT_TIME: doFeed ? "UNKNOWN" : (ident.FACT_TIME ?? "UNKNOWN"),',
     'FACT_TIME: doFeed ? (alvo.publicadoNoIndice?.VALOR ?? "UNKNOWN") : (ident.FACT_TIME ?? "UNKNOWN"),', T_LOCAL, "."),
    ("CORPO: o <script> e apagado (sanitizar)", MOTOR,
     "  const corpo = desembrulharXml(rss ? m[1] : m[2]);",
     "  const corpo = desembrulharXml(rss ? m[1] : m[2]).replace(/<script[\\s\\S]*?<\\/script>/gi, \"\");", T_FEED, "."),
    ("CORPO: a <description> (resumo) conta como texto completo", MOTOR,
     "  const re = rss ? /<content:encoded\\b[^>]*>([\\s\\S]*?)<\\/content:encoded>/i",
     "  const re = rss ? /<(?:content:encoded|description)\\b[^>]*>([\\s\\S]*?)<\\/(?:content:encoded|description)>/i", T_FEED, "."),
    ("D40: o item com corpo ocupa um dos 3 lugares de pedido", MOTOR,
     "const aPedir = escolherAlvosD40(semCorpo, classificar, nomeDe, alvosPorFonte);",   # D124-REBASE: + alvosPorFonte
     "const aPedir = escolherAlvosD40([...comCorpo, ...semCorpo], classificar, nomeDe, alvosPorFonte);", T_FEED, "."),
    ("LIVRO: o item com corpo ja conhecido volta a entrar", MOTOR,
     '        if (classificar(url) === "CONHECIDO") { conhecidos++; continue; }\n', "", T_FEED, "."),
    ("SITEMAP: as linhas Sitemap: deitadas fora", COL,
     "    if (m && !fora.includes(m[1])) fora.push(m[1]);", "    if (false) fora.push(m[1]);", T_LOCAL, "."),
    ("ROBOTS 24H: o livro nunca e lido (re-pede em cada corrida)", COL,
     "    rb = robotsDoLivro24h(u.origin);\n", "    rb = null;\n", T_LOCAL, "."),
    ("ROBOTS 24H: entrada LIDO sem texto vira permissao", COL,
     '  if (e.ESTADO === "LIDO" && typeof e.TEXTO === "string") {', '  if (e.ESTADO === "LIDO") {', T_LOCAL, "."),
    ("ROBOTS 24H: ILEGIVEL tambem vai para o livro", COL,
     '!["LIDO", "AUSENTE"].includes(rb.estado)) return;', '!["LIDO", "AUSENTE", "ILEGIVEL"].includes(rb.estado)) return;',
     T_LOCAL, "."),
    ("CONDICIONAL: o validador nunca e enviado", COL,
     "  if (!m) return [];\n  return [...(m.ETAG", "  return [];\n  return [...(m.ETAG", T_LOCAL, "."),
    ("CONDICIONAL: o validador lido do bloco do proxy", COL,
     "  const ultimo = blocos.at(-1) || \"\";", "  const ultimo = blocos[0] || \"\";", T_LOCAL, "."),
    ("INSTALADOR: cria a linha que falta na tabela", "regras/ligar_feeds.py",
     '        elif l is None:\n            d.update(DECISAO="SEM_LINHA_NA_TABELA",',
     '        elif False:\n            d.update(DECISAO="SEM_LINHA_NA_TABELA",', T_PY, "tests"),
    ("INSTALADOR: o LINK_PATTERN antigo passa para o feed", "regras/ligar_feeds.py",
     '    if anterior.get("INDEX_URL"):\n        aq["INDEX_URL"] = anterior["INDEX_URL"]\n',
     '    aq.update({k: v for k, v in anterior.items() if k in ("INDEX_URL", "LINK_PATTERN")})\n', T_PY, "tests"),
    ("PREVISAO: o item com corpo tambem cabe nos 3 do teto", "regras/ligar_feeds.py",
     "DOC_DIA_DEPOIS:r2(C7/7+Math.min(3,S7/7))", "DOC_DIA_DEPOIS:r2(Math.min(3,(C7+S7)/7))", T_PY, "tests"),
    ("CONTRATO: a entrada de uma linha de feed continua a ser o INDEX_URL", "regras/italy_contracts.mjs",
     ': feed ? aq.FEED_URL : aq.INDEX_URL;', ': aq.INDEX_URL;', T_PY, "tests"),
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
        cache = tempfile.mkdtemp(prefix="mut-feed-pyc-")
        env = dict(os.environ, PYTHONPYCACHEPREFIX=cache, PYTHONUTF8="1", NODE_DISABLE_COMPILE_CACHE="1")
        for k in ("SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA", "SINTONIA_TETO_24H"):
            env.pop(k, None)
        try:
            with open(p, "wb") as f:
                f.write(texto.replace(antes, depois).encode("utf-8"))
            r = subprocess.run(cmd, cwd=os.path.join(RAIZ, cwd), env=env, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=900)
            estado = "MORTO" if r.returncode != 0 else "SOBREVIVEU"
            quem = [l.strip()[:140] for l in (r.stdout + r.stderr).splitlines()
                    if l.strip().startswith(("FALHA", "FAIL", "ERROR:"))][:3]
        finally:
            with open(p, "wb") as f:
                f.write(orig)
        assert sha(open(p, "rb").read()) == sha(orig), "nao repus %s" % rel
        res.append({"MUTANTE": nome, "FICHEIRO": rel, "ESTADO": estado, "APANHADO_POR": quem})
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
