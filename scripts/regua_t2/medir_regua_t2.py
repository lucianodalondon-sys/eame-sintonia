#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T2-REGUA · MEDIR A REGUA T2 NO GABARITO, E PROVAR QUE OS VIZINHOS NAO MUDARAM.

    py scripts/regua_t2/medir_regua_t2.py [--gabarito=V2|V1] [--textos=DIR] [--corpus=DIR;DIR] [--base=REV]

SEM REDE. Le os textos FORA do Git (confere o sha256 de cada um contra o
GABARITO-T2-V1.json antes de o usar) e julga cada um com `admissao._do_universo`
para T2 — o mesmo caminho da porta, com a escolha de lingua da L1.

Duas medidas (o desenho da `scripts/regua_t8/medir_regua_t8.py`, YT2):
1. A REGUA T2 no gabarito: precisao e recall de SIM (os NAO_SEI do gabarito ficam
   fora da conta), a matriz ouro->regua, e o controlo negativo.
2. OS VIZINHOS: cada texto do corpus (inventario T2 + derivados do armazem +
   lote-76) e julgado em T3 T4 T5 T7 T9 T10 pela admissao ANTES (a versao
   `--base`, por omissao `origin/bc4-correcoes-v1` = instalado) e DEPOIS (a arvore
   de trabalho). VEREDITOS_VIZINHOS_MUDADOS tem de ser 0.

⚠️ A precisao/recall e medida DENTRO da amostra que serviu de referencia. Dito
assim, sem o vender como generalizacao.
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
VERSAO_GAB = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--gabarito=")), "V2")
GAB = AQUI / ("GABARITO-T2-%s.json" % VERSAO_GAB)
SAIDA = AQUI / ("MEDICAO-REGUA-T2-%s.json" % VERSAO_GAB)
VIZINHOS = ("T3", "T4", "T5", "T7", "T9", "T10")
CASA = Path(os.environ.get("USERPROFILE", str(Path.home())))


def _arg(nome, omissao):
    return next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--%s=" % nome)), omissao)


def admissao_da_revisao(rev):
    """A admissao como estava em `rev`, carregada ao lado (outro nome de modulo)."""
    d = tempfile.mkdtemp(prefix="admissao-base-")
    for nome in ("admissao.py", "idioma.py"):
        src = subprocess.run(["git", "-C", str(RAIZ), "show", "%s:admissao/%s" % (rev, nome)],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
        open(os.path.join(d, "admissao_base.py" if nome == "admissao.py" else nome), "w",
             encoding="utf-8").write(src)
    sp = u.spec_from_file_location("admissao_base", os.path.join(d, "admissao_base.py"))
    m = u.module_from_spec(sp)
    sys.modules["admissao_base"] = m        # o @dataclass procura o modulo aqui
    sp.loader.exec_module(m)
    return m


def julgar(mod, texto, universo):
    r, _motivo, ev = mod._do_universo({"texto": texto}, universo,
                                      mod.PERGUNTAS_DO_UNIVERSO.get(universo, []))
    return r, ev


def main():
    textos = Path(_arg("textos", str(CASA / "sintonia-gabarito" / "REGUA-T2-V1" / "textos")))
    corpus_dirs = [Path(p) for p in _arg("corpus", ";".join([
        str(textos),
        str(CASA / "sintonia-sala-italia" / "armazem" / "NAO_SEI" / "derivados" / "TEXT_EXTRACTION"),
        str(RAIZ.parent / "lote-76-v1" / "NAO_SEI" / "derivados"),
        str(CASA / "orca" / "workspaces" / "eame-sintonia" / "lote-76-v1" / "NAO_SEI" / "derivados"),
    ])).split(";") if p]
    base = _arg("base", "origin/bc4-correcoes-v1")
    g = json.load(open(GAB, encoding="utf-8"))

    # ── 1 · A REGUA T2 NO GABARITO ────────────────────────────────────────
    itens, sha_mau = [], []
    for it in g["ITENS"]:
        f = textos / (it["TEXTO_ID"] + ".txt")
        b = f.read_bytes() if f.is_file() else b""
        if hashlib.sha256(b).hexdigest() != it["TEXTO_SHA256"]:
            sha_mau.append(it["TEXTO_ID"])
            continue
        r, ev = julgar(A, b.decode("utf-8"), "T2")
        itens.append({"TEXTO_ID": it["TEXTO_ID"], "SOURCE_ID": it["SOURCE_ID"], "SERIE": it.get("SERIE"),
                      "OURO": it.get("JANELA") or it["UNIVERSE_MATCH"], "REGUA": r, "SINAIS": ev.get("sinais"),
                      "PALAVRAS": ev.get("palavras"), "ANCORAS": ev.get("ancoras"), "FALTA": ev.get("falta"), "IDIOMA": ev.get("idioma"),
                      "OUTRO": ev.get("achado_noutro"), "FORA": bool(it.get("FORA_DA_AMOSTRA"))})
    ouro = [i for i in itens if i["OURO"] in ("YES", "NO")]
    tp = sum(1 for i in ouro if i["OURO"] == "YES" and i["REGUA"] == A.SIM)
    fp = sum(1 for i in ouro if i["OURO"] == "NO" and i["REGUA"] == A.SIM)
    fn = sum(1 for i in ouro if i["OURO"] == "YES" and i["REGUA"] != A.SIM)
    prec = round(tp / (tp + fp), 3) if tp + fp else None
    rec = round(tp / (tp + fn), 3) if tp + fn else None
    matriz = Counter("%s->%s" % (i["OURO"], i["REGUA"]) for i in itens)
    # sem a serie ARPAV: quanto do numero e um molde so
    fora = [i for i in ouro if i["SERIE"] != "ARPAV-AGROMETEO-INFORMA"]
    tp2 = sum(1 for i in fora if i["OURO"] == "YES" and i["REGUA"] == A.SIM)
    fp2 = sum(1 for i in fora if i["OURO"] == "NO" and i["REGUA"] == A.SIM)
    fn2 = sum(1 for i in fora if i["OURO"] == "YES" and i["REGUA"] != A.SIM)

    # a medida FORA DA AMOSTRA: textos que a regua nunca viu (recolha pela rede, Adenda 2)
    fo = [i for i in ouro if i.get("FORA")]
    tpf = sum(1 for i in fo if i["OURO"] == "YES" and i["REGUA"] == A.SIM)
    fpf = sum(1 for i in fo if i["OURO"] == "NO" and i["REGUA"] == A.SIM)
    fnf = sum(1 for i in fo if i["OURO"] == "YES" and i["REGUA"] != A.SIM)

    # ── 1b · T1 (pedido da coordenacao): T1 ja cobre fenologia/tratamento? ─
    t1 = Counter()
    for it in g["ITENS"]:
        if (it.get("JANELA") or it["UNIVERSE_MATCH"]) == "YES":
            t = (textos / (it["TEXTO_ID"] + ".txt")).read_text(encoding="utf-8")
            t1[julgar(A, t, "T1")[0]] += 1

    # ── 2 · OS VIZINHOS ──────────────────────────────────────────────────
    antes = admissao_da_revisao(base)
    corpus, vistos = [], set()
    for d in corpus_dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.txt")):
            t = p.read_text(encoding="utf-8", errors="replace")
            h = hashlib.sha256(t.encode("utf-8")).hexdigest()
            if h not in vistos:
                vistos.add(h)
                corpus.append((d.name + ":" + p.name, t))
    no_gabarito = {i["TEXTO_SHA256"] for i in g["ITENS"]}
    fora_sim = []
    mudou, t2_antes_depois = [], Counter()
    for nome, texto in corpus:
        for uv in VIZINHOS:
            a, _ = julgar(antes, texto, uv)
            d, _ = julgar(A, texto, uv)
            if a != d:
                mudou.append({"TEXTO": nome, "UNIVERSO": uv, "ANTES": a, "DEPOIS": d})
        a, _ = julgar(antes, texto, "T2")
        d, _ = julgar(A, texto, "T2")
        t2_antes_depois["%s->%s" % (a, d)] += 1
        if d == A.SIM and hashlib.sha256(texto.encode("utf-8")).hexdigest() not in no_gabarito:
            fora_sim.append(nome)

    out = {"DATASET": "MEDICAO-REGUA-T2-" + VERSAO_GAB, "GABARITO": GAB.name, "BASE": base,
           "VERSAO_DA_REGRA": A.VERSAO_DA_REGRA,
           "REGUA": {"IT_PT": A.PERGUNTAS_DO_UNIVERSO.get("T2"), "EN": A.PERGUNTAS_EN.get("T2"),
                     "SINAIS_MINIMOS": A.SINAIS_MINIMOS, "PALAVRA_INTEIRA": sorted(A.PALAVRA_INTEIRA),
                     "TRANSVERSAIS": sorted(A.TRANSVERSAIS),
                     "ANCORAS": A.ANCORAS.get("T2"), "ANCORAS_EN": A.ANCORAS_EN.get("T2")},
           "SHA_NAO_CONFERE": sha_mau,
           "T2": {"MEDIDO_DENTRO_DA_AMOSTRA": True,
                  "OURO_YES": sum(1 for i in ouro if i["OURO"] == "YES"),
                  "OURO_NO": sum(1 for i in ouro if i["OURO"] == "NO"),
                  "OURO_NAO_SEI_FORA_DA_CONTA": sum(1 for i in itens if i["OURO"] == "NAO_SEI"),
                  "TP": tp, "FP": fp, "FN": fn, "PRECISAO": prec, "RECALL": rec,
                  "SEM_SERIE_ARPAV": {"TP": tp2, "FP": fp2, "FN": fn2,
                                      "PRECISAO": round(tp2 / (tp2 + fp2), 3) if tp2 + fp2 else None,
                                      "RECALL": round(tp2 / (tp2 + fn2), 3) if tp2 + fn2 else None},
                  "FORA_DA_AMOSTRA": {"ITENS_YES_NO": len(fo), "TP": tpf, "FP": fpf, "FN": fnf,
                                      "PRECISAO": round(tpf / (tpf + fpf), 3) if tpf + fpf else None,
                                      "RECALL": round(tpf / (tpf + fnf), 3) if tpf + fnf else None,
                                      "MATRIZ": dict(Counter("%s->%s" % (i["OURO"], i["REGUA"]) for i in fo))},
                  "YES_QUE_SAIRAM_NAO": sum(1 for i in ouro if i["OURO"] == "YES" and i["REGUA"] == A.NAO),
                  "YES_QUE_FICARAM_NAO_SEI": sum(1 for i in ouro if i["OURO"] == "YES" and i["REGUA"] == A.NAO_SEI),
                  "CONTROLO_NEGATIVO": {"NO_DO_GABARITO": sum(1 for i in ouro if i["OURO"] == "NO"),
                                        "QUE_ENTRARAM_COMO_SIM": fp},
                  "MATRIZ_OURO_REGUA": dict(sorted(matriz.items())),
                  "ERROS": [i for i in ouro if (i["OURO"] == "YES") != (i["REGUA"] == A.SIM)]},
           "T1": {"TEM_REGUA": "T1" in A.PERGUNTAS_DO_UNIVERSO,
                  "JANELAS_DO_GABARITO_JULGADAS_EM_T1": dict(t1),
                  "ATLAS_T1": "docs/fontes/ATLAS-DE-FONTES-EAME.md:45 — area plantada, producao, "
                              "produtividade, calendario agricola, desenvolvimento da cultura, "
                              "previsao de safra, regioes produtoras, historico"},
           "VIZINHOS": {"TEXTOS_NO_CORPUS": len(corpus), "UNIVERSOS": list(VIZINHOS),
                        "JULGAMENTOS": len(corpus) * len(VIZINHOS),
                        "VEREDITOS_VIZINHOS_MUDADOS": len(mudou), "MUDANCAS": mudou[:50]},
           "T2_NO_CORPUS_ANTES_DEPOIS": dict(sorted(t2_antes_depois.items())),
           "FORA_DO_GABARITO_SIM": {"N": len(fora_sim),
                                    "AMOSTRA_25_PARA_LER": __import__("random").Random(24092026).sample(
                                        sorted(fora_sim), min(25, len(fora_sim)))}}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: out["T2"][k] for k in ("OURO_YES", "OURO_NO", "TP", "FP", "FN", "PRECISAO",
                                                 "RECALL", "SEM_SERIE_ARPAV", "FORA_DA_AMOSTRA", "YES_QUE_SAIRAM_NAO",
                                                 "YES_QUE_FICARAM_NAO_SEI", "MATRIZ_OURO_REGUA")},
                     ensure_ascii=False))
    print(json.dumps({"SHA_NAO_CONFERE": len(sha_mau), **{k: out["VIZINHOS"][k] for k in
                      ("TEXTOS_NO_CORPUS", "JULGAMENTOS", "VEREDITOS_VIZINHOS_MUDADOS")},
                      "T2_NO_CORPUS": out["T2_NO_CORPUS_ANTES_DEPOIS"], "FORA_DO_GABARITO_SIM": len(fora_sim)}, ensure_ascii=False))
    return 0 if not mudou and not sha_mau else 1


if __name__ == "__main__":
    raise SystemExit(main())
