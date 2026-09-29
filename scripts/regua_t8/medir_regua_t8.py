"""YT2 · MEDIR A REGUA T8 NO GABARITO, E PROVAR QUE OS VIZINHOS NAO MUDARAM.

    py scripts/regua_t8/medir_regua_t8.py [--transcricoes=DIR] [--lote76=DIR] [--base=REV]

SEM REDE. Le as transcricoes FORA do Git (confere o sha256 de cada uma contra o
GABARITO-T8-V1.json antes de a usar) e julga cada uma com `admissao._do_universo`
para T8 — o mesmo caminho da porta, com a escolha de lingua da L1.

Duas medidas:
1. A REGUA T8 no gabarito: precisao e recall de SIM (os NAO_SEI do gabarito ficam
   fora da conta e sao contados a parte), e o controlo negativo — quantos NAO do
   gabarito a regua deixou entrar.
2. OS VIZINHOS: cada texto do corpus (lote-76 + as transcricoes do gabarito) e
   julgado em T3 T4 T5 T7 T9 T10 pela admissao ANTES (a versao `--base`, por
   omissao HEAD) e DEPOIS (a arvore de trabalho). IT_VERDICTS_CHANGED tem de ser 0.

⚠️ A precisao/recall e medida DENTRO da amostra que serviu de referencia: o
gabarito e o mesmo onde a regua foi medida. Dito assim, sem o vender como
generalizacao.
"""
import hashlib
import importlib.util as u
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ / "admissao"), str(RAIZ)]
import admissao as A  # noqa: E402

AQUI = Path(__file__).parent
GAB = AQUI / "GABARITO-T8-V1.json"
SAIDA = AQUI / "MEDICAO-REGUA-T8-V1.json"
VIZINHOS = ("T3", "T4", "T5", "T7", "T9", "T10")


def _arg(nome, omissao):
    return next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--%s=" % nome)), omissao)


def admissao_da_revisao(rev):
    """A admissao como estava em `rev`, carregada ao lado (outro nome de modulo)."""
    src = subprocess.run(["git", "-C", str(RAIZ), "show", "%s:admissao/admissao.py" % rev],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    d = tempfile.mkdtemp(prefix="admissao-base-")
    f = os.path.join(d, "admissao_base.py")
    open(f, "w", encoding="utf-8").write(src)
    # a admissao carrega `idioma.py` do lado dela: vai a MESMA revisao
    idi = subprocess.run(["git", "-C", str(RAIZ), "show", "%s:admissao/idioma.py" % rev],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    open(os.path.join(d, "idioma.py"), "w", encoding="utf-8").write(idi)
    sp = u.spec_from_file_location("admissao_base", f)
    m = u.module_from_spec(sp)
    sys.modules["admissao_base"] = m        # o @dataclass procura o modulo aqui
    sp.loader.exec_module(m)
    return m


def julgar(mod, texto, universo):
    r, _motivo, ev = mod._do_universo({"texto": texto}, universo,
                                      mod.PERGUNTAS_DO_UNIVERSO.get(universo, []))
    return r, ev


def main():
    trans = Path(_arg("transcricoes", os.path.join(os.environ.get("TEMP", ""), "yt2-gabarito", "transcricoes")))
    lote76 = Path(_arg("lote76", str(RAIZ.parent / "lote-76-v1" / "NAO_SEI" / "derivados")))
    base = _arg("base", "HEAD")
    g = json.load(open(GAB, encoding="utf-8"))

    # ── 1 · A REGUA T8 NO GABARITO ────────────────────────────────────────
    itens, sha_mau = [], []
    for it in g["ITENS"]:
        f = trans / (it["VIDEO_ID"] + ".txt")
        b = f.read_bytes() if f.is_file() else b""
        if hashlib.sha256(b).hexdigest() != it["TRANSCRICAO_SHA256"]:
            sha_mau.append(it["VIDEO_ID"])
            continue
        t = b.decode("utf-8")
        r, ev = julgar(A, t, "T8")
        itens.append({"VIDEO_ID": it["VIDEO_ID"], "SOURCE_ID": it["SOURCE_ID"], "OURO": it["UNIVERSE_MATCH"],
                      "REGUA": r, "SINAIS": ev.get("sinais"), "PALAVRAS": ev.get("palavras"),
                      "IDIOMA": ev.get("idioma"), "OUTRO": ev.get("achado_noutro")})
    ouro = [i for i in itens if i["OURO"] in ("SIM", "NAO")]
    tp = sum(1 for i in ouro if i["OURO"] == "SIM" and i["REGUA"] == A.SIM)
    fp = sum(1 for i in ouro if i["OURO"] == "NAO" and i["REGUA"] == A.SIM)
    fn = sum(1 for i in ouro if i["OURO"] == "SIM" and i["REGUA"] != A.SIM)
    prec = round(tp / (tp + fp), 3) if tp + fp else None
    rec = round(tp / (tp + fn), 3) if tp + fn else None
    matriz = Counter("%s->%s" % (i["OURO"], i["REGUA"]) for i in itens)

    # ── 2 · OS VIZINHOS ──────────────────────────────────────────────────
    antes = admissao_da_revisao(base)
    corpus = [(("gab:" + i["VIDEO_ID"]), (trans / (i["VIDEO_ID"] + ".txt")).read_text(encoding="utf-8"))
              for i in itens]
    if lote76.is_dir():
        corpus += [("lote76:" + p.name, p.read_text(encoding="utf-8", errors="replace"))
                   for p in sorted(lote76.rglob("*.txt"))]
    mudou = []
    for nome, texto in corpus:
        for uv in VIZINHOS:
            a, _ = julgar(antes, texto, uv)
            d, _ = julgar(A, texto, uv)
            if a != d:
                mudou.append({"TEXTO": nome, "UNIVERSO": uv, "ANTES": a, "DEPOIS": d})

    out = {"DATASET": "MEDICAO-REGUA-T8-V1", "GABARITO": GAB.name,
           "REGUA": {"IT_PT": A.PERGUNTAS_DO_UNIVERSO.get("T8"), "EN": A.PERGUNTAS_EN.get("T8"),
                     "SINAIS_MINIMOS": A.SINAIS_MINIMOS, "PALAVRA_INTEIRA": sorted(A.PALAVRA_INTEIRA),
                     "TRANSVERSAIS": sorted(A.TRANSVERSAIS)},
           "SHA_NAO_CONFERE": sha_mau,
           "T8": {"MEDIDO_DENTRO_DA_AMOSTRA": True, "OURO_SIM": sum(1 for i in ouro if i["OURO"] == "SIM"),
                  "OURO_NAO": sum(1 for i in ouro if i["OURO"] == "NAO"), "TP": tp, "FP": fp, "FN": fn,
                  "PRECISAO": prec, "RECALL": rec,
                  "CONTROLO_NEGATIVO": {"NAO_DO_GABARITO": sum(1 for i in ouro if i["OURO"] == "NAO"),
                                        "QUE_ENTRARAM_COMO_SIM": fp},
                  "MATRIZ_OURO_PARA_REGUA": dict(sorted(matriz.items())), "ITENS": itens},
           "VIZINHOS": {"BASE": base, "UNIVERSOS": list(VIZINHOS), "TEXTOS": len(corpus),
                        "LOTE76_DIR": str(lote76) if lote76.is_dir() else "AUSENTE",
                        "JULGAMENTOS": len(corpus) * len(VIZINHOS),
                        "IT_VERDICTS_CHANGED": len(mudou), "MUDANCAS": mudou}}
    json.dump(out, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("T8  TP=%d FP=%d FN=%d  precisao=%s recall=%s  (ouro SIM %d / NAO %d, sha mau %d)"
          % (tp, fp, fn, prec, rec, out["T8"]["OURO_SIM"], out["T8"]["OURO_NAO"], len(sha_mau)))
    print("    matriz", dict(sorted(matriz.items())))
    print("VIZINHOS  textos=%d  julgamentos=%d  IT_VERDICTS_CHANGED=%d"
          % (len(corpus), len(corpus) * len(VIZINHOS), len(mudou)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
