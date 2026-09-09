#!/usr/bin/env python3
"""O QUE VAI PARA O BROWSER, FICHEIRO A FICHEIRO.

A S1 respondeu QUAIS ficheiros o deploy publica. Esta ferramenta responde O QUE
ha dentro de cada um — porque o nome nao diz.

    NAO CONFIAR NO NOME DO FICHEIRO.
    `demo-data.js` pode carregar motor; `engine.js` pode ser so desenho.

Nao classifica sozinha. Extrai EVIDENCIA — o cabecalho que o proprio ficheiro
escreveu sobre si, a forma dos dados, as contagens, os sinais de calculo — e
poe-na ao lado da classificacao humana, que vive em `cliente-classificacao.json`.
Uma classificacao sem a evidencia ao lado e uma opiniao; com ela, e uma medicao
que a proxima pessoa pode contestar.

Uso:
    python3 security/censo_do_cliente.py            # relatorio
    python3 security/censo_do_cliente.py --json     # dados
"""
import json, os, pathlib, re, sys

RAIZ = pathlib.Path(os.environ.get("SINTONIA_RATCHET_RAIZ") or
                    pathlib.Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from superficie_publica import superficie  # o dono da fronteira publicada

CLASSES = pathlib.Path(__file__).resolve().parent / "cliente-classificacao.json"

# Sinais de CALCULO: nao provam motor, mas dizem onde olhar.
SINAIS_CALCULO = re.compile(
    r"\b(score|scoring|rank|ranking|weight|peso|threshold|soglia|formula|"
    r"classif|derive|derivat|priorit|promote|reject|judge|verdict|veredito|"
    r"rule|regra|regola|ruleset|coefficient|criteri)", re.I)
SINAIS_PROMPT = re.compile(r"\b(system_prompt|prompt_template|model_instruction|"
                           r"llm_prompt|chain_of_thought)", re.I)
BINARIO = re.compile(r"\.(png|jpe?g|gif|webp|ico|otf|ttf|woff2?|pdf|zip)$", re.I)


def cabecalho(texto, n=3):
    """A primeira coisa que o ficheiro diz sobre si proprio."""
    m = re.match(r"\s*/\*(.*?)\*/", texto, re.S)
    if not m:
        linhas = [l for l in texto.splitlines()[:6] if l.strip().startswith("//")]
        return " ".join(l.strip("/ ") for l in linhas)[:400]
    return " ".join(m.group(1).split())[:400]


def carga(texto):
    """Se o ficheiro atribui um objecto a `window`, mede-o sem o interpretar."""
    m = re.search(r"window\.([A-Za-z_0-9]+)\s*=\s*(\{|\[)", texto)
    if not m:
        return None
    ini = m.end() - 1
    fim = texto.rfind("}" if m.group(2) == "{" else "]")
    if fim <= ini:
        return None
    try:
        d = json.loads(texto[ini:fim + 1])
    except Exception:
        return None
    out = {"global": m.group(1)}
    if isinstance(d, dict):
        out["chaves"] = list(d.keys())[:40]
        col = {}
        for k, v in d.items():
            if isinstance(v, list) and v:
                col[k] = len(v)
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, list) and v2:
                        col[f"{k}/{k2}"] = len(v2)
        out["coleccoes"] = dict(sorted(col.items(), key=lambda x: -x[1])[:25])
        out["registos"] = sum(col.values())
    elif isinstance(d, list):
        out["registos"] = len(d)
    return out


def medir(rel):
    p = RAIZ / rel
    r = {"caminho": rel, "bytes": p.stat().st_size,
         "tipo": p.suffix.lstrip(".").lower() or "sem-extensao",
         "vendor": "/vendor/" in rel, "gerado": None}
    if BINARIO.search(rel):
        r["conteudo"] = "binario"
        return r
    txt = p.read_text(encoding="utf-8", errors="replace")
    r["cabecalho"] = cabecalho(txt)
    r["gerado"] = bool(re.search(r"\bGERAD[OA]\b|GENERATED|DO NOT EDIT|nao editar", txt[:2000], re.I))
    r["sinais_calculo"] = len(SINAIS_CALCULO.findall(txt))
    r["sinais_prompt"] = len(SINAIS_PROMPT.findall(txt))
    r["executavel"] = r["tipo"] in ("js", "mjs", "html")
    c = carga(txt)
    if c:
        r["carga"] = c
    return r


def main():
    s = superficie(RAIZ)
    fich = [medir(f) for f in s["ficheiros"]]
    classes = json.loads(CLASSES.read_text(encoding="utf-8")) if CLASSES.exists() else {}
    curto = lambda f: f.replace("italia-portale/client/", "")
    for f in fich:
        f["classe"] = classes.get(curto(f["caminho"]), {}).get("classe", "UNKNOWN")
        f["porque"] = classes.get(curto(f["caminho"]), {}).get("porque", "")

    if "--json" in sys.argv:
        print(json.dumps({"total_ficheiros": len(fich),
                          "total_bytes": sum(f["bytes"] for f in fich),
                          "ficheiros": fich}, ensure_ascii=False, indent=2))
        return 0

    from collections import Counter
    cb = Counter()
    cn = Counter()
    for f in fich:
        cb[f["classe"]] += f["bytes"]
        cn[f["classe"]] += 1
    total = sum(cb.values())
    print(f"{'CLASSE':34} {'FICH':>5} {'BYTES':>14} {'%':>6}")
    for k, b in cb.most_common():
        print(f"{k:34} {cn[k]:5} {b:14,} {100*b/total:5.1f}%")
    print(f"{'TOTAL':34} {len(fich):5} {total:14,}")
    desconhecidos = [f["caminho"] for f in fich if f["classe"] == "UNKNOWN"]
    if desconhecidos:
        print(f"\nUNKNOWN = {len(desconhecidos)}, e cada um tem de ser nomeado:")
        for d in desconhecidos:
            print("  ", curto(d))
    else:
        print("\nUNKNOWN = 0 · todos os ficheiros publicados foram abertos e classificados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
