"""LD1 — o detector CAPA != MATERIA antes e depois das receitas do G1, no MESMO gabarito.

    py scripts/detector_capa/medir_apos_receitas.py --antes=<livro> --depois=<livro> [--pasta=<gabarito>]

Sem rede. Os dois livros sao COPIAS (o do servico vivo, e o mesmo com o pacote G1
aplicado). Os juizes sao os de `medir_gabarito.py`, sem os reescrever.

Os dois erros do gate (mandato v2 §18), por juiz:
  FALSE_LISTING_AS_ARTICLE  capa que ATRAVESSA o portao de hoje (julgada MATERIA ou
                            NAO_SEI — o portao so reprova CAPA_PROVAVEL); e, a parte,
                            a capa calada como MATERIA (sem ninguem a ler)
  FALSE_ARTICLE_AS_LISTING  materia julgada CAPA (barrada)

⚠️ AMEACA DE CIRCULARIDADE, MEDIDA E SEPARADA: o pacote G1 so aceitou um padrao novo
se ele casasse TODAS as materias e NENHUMA das 109 capas DESTE gabarito. Nas paginas
das fontes cuja receita mudou, a morada acerta POR CONSTRUCAO. Por isso cada numero
sai tambem por fatia: AFETADAS (receita mudou) · NAO_AFETADAS · e as capas que nao
sao o INDEX_URL.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import medir_gabarito as MG  # noqa: E402

JUIZES = ("ACTUAL", "SO_MORADA", "PROPOSTA", "V1_SO_INDICE", "V2_DESEMPATE")


def _livro(p: Path) -> dict:
    return {f["SOURCE_ID"]: f.get("ACQUISITION")
            for f in json.loads(p.read_text(encoding="utf-8"))["FONTES"]}


def _julgar(paginas, pasta, contratos, retratos):
    out = {}
    for nome in JUIZES:
        juiz = MG.JUIZES[nome]
        erros = {"ATRAVESSA": [], "CALADA": [], "BARRADA": []}
        for p in paginas:
            v = juiz(retratos[p["ID"]], p["URL"], contratos.get(p["SOURCE_ID"]))
            if p["VEREDITO"] == "CAPA" and v != MG.CAPA:
                erros["ATRAVESSA"].append(p["ID"])
                if v == MG.MAT:
                    erros["CALADA"].append(p["ID"])
            if p["VEREDITO"] == "MATERIA" and v == MG.CAPA:
                erros["BARRADA"].append(p["ID"])
        out[nome] = erros
    return out


def _fmt(erros, nc, nm):
    return {"FALSE_LISTING_AS_ARTICLE": "%d/%d" % (len(erros["ATRAVESSA"]), nc),
            "CAPA_CALADA_COMO_MATERIA": "%d/%d" % (len(erros["CALADA"]), nc),
            "FALSE_ARTICLE_AS_LISTING": "%d/%d" % (len(erros["BARRADA"]), nm),
            "IDS": {k: v for k, v in erros.items() if v}}


def medir(antes: Path, depois: Path, pasta: Path, gabarito: Path | None = None) -> dict:
    g = json.loads((gabarito or AQUI / "GABARITO-CAPA-V1.json").read_text(encoding="utf-8"))
    paginas = [p for p in g["PAGINAS"] if p["VEREDITO"] in ("CAPA", "MATERIA")]
    la, ld = _livro(antes), _livro(depois)
    mudadas = sorted(s for s in la if (la[s] or {}).get("LINK_PATTERN") != (ld.get(s) or {}).get("LINK_PATTERN")
                     or (la[s] or {}).get("INDEX_URL") != (ld.get(s) or {}).get("INDEX_URL"))
    retratos = {p["ID"]: MG.RH.retrato_do_html((pasta / p["FICHEIRO"]).read_bytes())
                for p in paginas}

    def _indice(p, livro):
        aq = livro.get(p["SOURCE_ID"]) or {}
        return p["URL"].rstrip("/") == str(aq.get("INDEX_URL", "")).rstrip("/")

    fatias = {
        "TODAS": paginas,
        "AFETADAS_CIRCULAR": [p for p in paginas if p["SOURCE_ID"] in mudadas],
        "NAO_AFETADAS": [p for p in paginas if p["SOURCE_ID"] not in mudadas],
        "CAPAS_NAO_INDICE_MAIS_MATERIAS": [p for p in paginas if p["VEREDITO"] == "MATERIA"
                                           or not _indice(p, la)],
    }
    res = {"FONTES_COM_RECEITA_MUDADA": mudadas,
           "FONTES_MUDADAS_NO_GABARITO": sorted({p["SOURCE_ID"] for p in fatias["AFETADAS_CIRCULAR"]}),
           "FATIAS": {}}
    for nome, ps in fatias.items():
        nc = sum(1 for p in ps if p["VEREDITO"] == "CAPA")
        nm = len(ps) - nc
        ea, ed = _julgar(ps, pasta, la, retratos), _julgar(ps, pasta, ld, retratos)
        res["FATIAS"][nome] = {"CAPAS": nc, "MATERIAS": nm, "JUIZES": {
            j: {"ANTES_RECEITAS": _fmt(ea[j], nc, nm), "DEPOIS_RECEITAS": _fmt(ed[j], nc, nm)}
            for j in JUIZES}}
    return res


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    pasta = Path(arg.get("pasta", str(Path.home() / "detector-capa-gabarito")))
    res = medir(Path(arg["antes"]), Path(arg["depois"]), pasta)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
