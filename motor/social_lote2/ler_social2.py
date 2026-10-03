"""SOCIAL-LOTE-2: le os 300 itens de SOCIAL-TEXTO-BRUTO-2026-10-03.json + transcricoes LinkedIn ja na Sala, sem filtro.
Codigo so transporta, chama o Opus sem ferramentas, confere TRECHO literal e IDs. Uso: python ler_social2.py <saida>"""
import json, sys, subprocess, hashlib, time, re, html, os, shutil, concurrent.futures as cf
CLAUDE = shutil.which("claude.cmd") or shutil.which("claude")
DIR = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
SRC = "C:/eame-sintonia/.claude/worktrees/intelligence-bible-canonical-review-749b7c/data/samples/SOCIAL-TEXTO-BRUTO-2026-10-03.json"
TR = "C:/Users/London1/sintonia-sala-italia/intelligence-experimental/SOCIAL-TRANSCRICOES-LOTE-1"
bruto = json.load(open(SRC, encoding="utf-8"))
itens = []
for x in bruto["itens"]:
    itens.append({"ID": x["id"], "PLATAFORMA": x["plataforma"], "URL": x["url"], "AUTOR": x["autor"], "EMPRESA_DECLARADA": x.get("empresa"),
                  "PAIS_DO_CANAL": x.get("escopo_pais"), "PUBLICADO_EM": x.get("publicado_em"), "CAPTURADO_EM": x.get("capturado_em"),
                  "TIPO_TEXTO": x.get("texto_tipo"), "TEXTO": html.unescape(x.get("texto") or ""), "ORIGEM": "SOCIAL-TEXTO-BRUTO"})
fich = json.load(open(TR + "/FICHAS.json", encoding="utf-8"))
if isinstance(fich, dict): fich = fich["FICHAS"]
for f in fich:
    if not str(f.get("URL","")).startswith("https://it.linkedin.com"): continue
    p = TR + "/texto/RAW-%s.txt" % f["RAW_ASSET_ID"]; b = open(p, "rb").read()
    assert hashlib.sha256(b).hexdigest() == f["TRANSCRICAO_SHA256"], p
    itens.append({"ID": "li:RAW-%s" % f["RAW_ASSET_ID"], "PLATAFORMA": "linkedin", "URL": f["URL"], "AUTOR": f["URL"].split("/posts/")[1].split("_")[0],
                  "EMPRESA_DECLARADA": None, "PAIS_DO_CANAL": "IT", "PUBLICADO_EM": "NAO_SEI", "CAPTURADO_EM": f.get("CAPTURADO_EM"),
                  "TIPO_TEXTO": "TRANSCRICAO_ASR", "TEXTO": b.decode("utf-8"), "ORIGEM": "SALA raw_asset %s + derived %s" % (f["RAW_ASSET_ID"], f["DERIVED_ID"])})
json.dump(itens, open(os.path.join(OUT, "ENTRADA.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def opus(prompt_file, dados, tag):
    bp = os.path.join(OUT, "bruto_%s.json" % tag)
    if not os.path.exists(bp):
        msg = open(os.path.join(DIR, prompt_file), encoding="utf-8").read() + "\n<<<DADOS>>>\n" + json.dumps(dados, ensure_ascii=False) + "\n<<<FIM_DADOS>>>\n"
        t0 = time.time()
        r = subprocess.run([CLAUDE, "-p", "--model", "claude-opus-5", "--tools", "", "--strict-mcp-config", "--no-session-persistence",
                            "--output-format", "json"], input=msg, capture_output=True, text=True, encoding="utf-8", timeout=1700)
        env = json.loads(r.stdout); env["_SEGUNDOS"] = round(time.time() - t0, 1)
        json.dump(env, open(bp, "w", encoding="utf-8"), ensure_ascii=False)
    env = json.load(open(bp, encoding="utf-8")); txt = env.get("result", "")
    m = re.search(r"[\[{].*[\]}]", txt, re.S)
    return json.loads(m.group(0)), {"tag": tag, "s": env.get("_SEGUNDOS"), "custo_usd": env.get("total_cost_usd"), "modelos": list((env.get("modelUsage") or {}).keys())}

def norm(s): return re.sub(r"\s+", " ", (s or "")).strip().lower()
def entrada(it): return {k: it[k] for k in ("ID", "PLATAFORMA", "AUTOR", "PAIS_DO_CANAL", "PUBLICADO_EM", "TIPO_TEXTO", "TEXTO")}
lotes = [itens[i:i + 20] for i in range(0, len(itens), 20)]
fichas, custos = [], []
with cf.ThreadPoolExecutor(4) as ex:
    futs = [ex.submit(opus, "ficha.prompt.md", [entrada(x) for x in l], "ficha%02d" % n) for n, l in enumerate(lotes)]
    for f in futs:
        fs, c = f.result(); fichas += fs; custos.append(c)
por = {it["ID"]: it for it in itens}
for f in fichas:
    it = por.get(f.get("ID"))
    if not it: f["CONFERENCIA"] = "REJEITADO_ID_INEXISTENTE"; continue
    t = norm(f.get("TRECHO")); f["CONFERENCIA"] = "OK" if t and t in norm(it["TEXTO"]) else "TRECHO_NAO_ENCONTRADO"
    for k in ("PLATAFORMA", "URL", "AUTOR", "PAIS_DO_CANAL", "PUBLICADO_EM", "CAPTURADO_EM", "TIPO_TEXTO", "ORIGEM"): f["_" + k] = it[k]
    f["MARCA"] = "TESTE / NAO_PARA_CLIENTE"
vistos = [f.get("ID") for f in fichas]
falt = [i for i in por if i not in vistos]; dup = [i for i in set(vistos) if vistos.count(i) > 1]
json.dump(fichas, open(os.path.join(OUT, "FICHAS.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
leve = [{k: f.get(k) for k in ("ID", "_AUTOR", "_PLATAFORMA", "_PAIS_DO_CANAL", "_PUBLICADO_EM", "RELEVANTE", "CATEGORIA", "TEMA", "CULTURA", "PRAGA_DOENCA_ALVO",
         "PRODUTO_OU_SUBSTANCIA", "EMPRESA", "LOCAL", "MOVIMENTO", "TIPO_DE_SAIDA", "O_QUE_FALTA", "PROMISSOR_PARA_TRANSCREVER", "IMPORTANCIA", "RESUMO")} for f in fichas]
conj, c = opus("conjunto.prompt.md", leve, "conjunto"); custos.append(c)
for g in conj.get("GRUPOS", []) + conj.get("SINAIS", []) + conj.get("LEADS", []) + conj.get("GAPS", []):
    g["IDS_INEXISTENTES"] = [v for v in g.get("IDS", []) if v not in por]
    g["AUTORES_DISTINTOS_CONTADOS"] = len({por[v]["AUTOR"] for v in g.get("IDS", []) if v in por})
conj["MARCA"] = "TESTE / NAO_PARA_CLIENTE"
json.dump(conj, open(os.path.join(OUT, "CONJUNTO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
man = {"ENTRADA": SRC, "ENTRADA_SHA256": hashlib.sha256(open(SRC, "rb").read()).hexdigest(), "ITENS_DO_ARQUIVO": len(bruto["itens"]),
       "ITENS_LINKEDIN_DA_SALA": len(itens) - len(bruto["itens"]), "ITENS_LIDOS": len(itens), "FICHAS": len(fichas), "FALTANDO": falt, "DUPLICADOS": dup,
       "TRECHO_OK": sum(f.get("CONFERENCIA") == "OK" for f in fichas), "MODELO": "claude-opus-5 (claude -p, sem ferramentas)", "CHAMADAS": custos,
       "CUSTO_TOTAL_USD_REPORTADO": round(sum(x["custo_usd"] or 0 for x in custos), 2)}
json.dump(man, open(os.path.join(OUT, "MANIFESTO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in man.items() if k != "CHAMADAS"}, ensure_ascii=False))
