"""PROPOSTA-RECEITAS-V3 — o aditamento LD2 ao pacote G1 (as materias que ficaram fora).

PROPOSTA, NAO APLICACAO. Escreve so curadoria/PROPOSTA-RECEITAS-V3.json, no mesmo
formato das V1/V2, que o pacote G1 (scripts/desbloqueio/aplicar_desbloqueio.py) le.

    py scripts/receitas/propor_receitas_v3.py --contratos=<copia do livro, JA com o G1>

O metodo e o do 6-PREP-d (`censo_e_proposta.por_fonte`), chamado sem alteracao:
materia confirmada lida, familia >= 2 na pagina de entrada, o MESMO guarda
(`e_generico`). Duas diferencas, declaradas em cada linha (DERIVACAO):
  1. ENTRADA = a pagina do INDEX_URL que o livro tem DEPOIS do G1 (para as fontes a que
     o G1 corrigiu o indice, a pagina que o G1 buscou e provou). Antes, a entrada era a
     pagina do indice errado — que era ela propria uma materia.
  2. SLUG_COM_PERCENT: so quando o 6-PREP-d disse «o padrao derivado nao casa a propria
     materia»: o slug aceita tambem %XX (URL com acentos codificados, ex. %C2%B0). O
     guarda e a familia minima sao os mesmos; so muda o que conta como letra.
Tudo o resto e NAO SEI com o motivo do proprio por_fonte.

Entradas so leitura: o gabarito e as paginas das receitas (como o 6-PREP-d), o
MANIFESTO-INDICES do G1, e ~/ld2-paginas (a recolha LD2).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
HOME = Path.home()
sys.path.insert(0, str(AQUI))
import censo_e_proposta as CP  # noqa: E402

SAIDA = RAIZ / "curadoria" / "PROPOSTA-RECEITAS-V3.json"
# As 13 fontes cujas materias o LD1 mediu fora da propria receita (depois do G1),
# e a IT-T11-010 (INDEX_URL = materia).
ALVO = ["IT-T10-020", "IT-T12-019", "IT-T12-023", "IT-T12-028", "IT-T12-044", "IT-T2-033",
        "IT-T2-039", "IT-T2-049", "IT-T5-049", "IT-T7-021", "IT-T7-046", "IT-T7-055",
        "IT-T8-008", "IT-T11-010"]
SLUG_COM_PERCENT = r"(?:[A-Za-z0-9]|%[0-9A-Fa-f]{2})+(?:[-_](?:[A-Za-z0-9]|%[0-9A-Fa-f]{2})+)+"


def _host(u: str) -> str:
    return urlparse(u).netloc.lower().removeprefix("www.")


def paginas() -> list[dict]:
    out = CP.paginas()
    mf = HOME / "receitas-paginas" / "indices" / "MANIFESTO-INDICES.json"
    if mf.exists():
        for l in json.loads(mf.read_text(encoding="utf-8")):
            if l.get("FICHEIRO"):
                out.append({"SOURCE_ID": l["SOURCE_ID"], "URL": l["URL"], "VEREDITO": "CAPA",
                            "PAPEL": "CAPA_INDICE", "BYTES": Path(l["FICHEIRO"]),
                            "ORIGEM": "indices-G1:" + l["URL"]})
    ld2 = HOME / "ld2-paginas" / "MANIFESTO.json"
    if ld2.exists():
        rot = AQUI / "ROTULOS-LD2.json"
        rotulos = json.loads(rot.read_text(encoding="utf-8")) if rot.exists() else {}
        for p in json.loads(ld2.read_text(encoding="utf-8"))["PAGINAS"]:
            v = rotulos.get(p["URL"])
            if v:
                out.append({"SOURCE_ID": p["SOURCE_ID"], "URL": p["URL"], "VEREDITO": v,
                            "PAPEL": "CAPA_INDICE" if v == "CAPA" else "MATERIA",
                            "BYTES": HOME / "ld2-paginas" / p["FICHEIRO"], "ORIGEM": "ld2:" + p["URL"]})
    return out


def _entrada_primeiro(pags: list[dict], idx: str) -> list[dict]:
    """A pagina do INDEX_URL de HOJE vai a frente; as antigas «CAPA_INDICE» cujo URL ja nao
    e o indice deixam de ser entrada (continuam a contar como veredito)."""
    hoje = [p for p in pags if p["PAPEL"] == "CAPA_INDICE" and p["URL"].rstrip("/") == idx.rstrip("/")]
    if not hoje:
        # sem pagina guardada do indice de hoje: a antiga pagina de entrada, SE for uma
        # capa (listagem real do site), ainda mede a familia. Uma materia nunca e entrada.
        return ([p for p in pags if p["PAPEL"] == "CAPA_INDICE" and p["VEREDITO"] == "CAPA"]
                + [dict(p, PAPEL="CAPA_ANTIGO_INDICE") if p["PAPEL"] == "CAPA_INDICE" else p
                   for p in pags if not (p["PAPEL"] == "CAPA_INDICE" and p["VEREDITO"] == "CAPA")])
    resto = [dict(p, PAPEL="CAPA_ANTIGO_INDICE") if p["PAPEL"] == "CAPA_INDICE" else p
             for p in pags if p not in hoje]
    return hoje + resto


def propor(contratos: dict, pags: list[dict]) -> list[dict]:
    capas_host: dict[str, list[str]] = {}
    for p in pags:
        if p["VEREDITO"] == "CAPA":
            capas_host.setdefault(_host(p["URL"]), []).append(p["URL"])
    linhas = []
    for sid in ALVO:
        c = contratos.get(sid)
        idx = ((c or {}).get("ACQUISITION") or {}).get("INDEX_URL", "")
        ps = _entrada_primeiro([p for p in pags if p["SOURCE_ID"] == sid], idx)
        l = CP.por_fonte(sid, c, ps, capas_host.get(_host(idx), []))
        l["DERIVACAO"] = "POR_FONTE_6PREPD, ENTRADA=INDEX_URL_DEPOIS_DO_G1"
        if "nao casa a propria materia" in (l.get("SEM_PROPOSTA") or ""):
            orig = CP._SLUG
            CP._SLUG = SLUG_COM_PERCENT
            try:
                l2 = CP.por_fonte(sid, c, ps, capas_host.get(_host(idx), []))
            finally:
                CP._SLUG = orig
            l2["DERIVACAO"] = l["DERIVACAO"] + ", SLUG_COM_PERCENT"
            l2["PRIMEIRA_TENTATIVA"] = l.get("SEM_PROPOSTA")
            l = l2
        linhas.append(l)
    return linhas


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    contratos = {f["SOURCE_ID"]: f for f in json.loads(
        Path(arg["contratos"]).read_text(encoding="utf-8"))["FONTES"]}
    linhas = propor(contratos, paginas())
    d = {"DATASET": "PROPOSTA-RECEITAS-V3", "MISSAO": "LD2 (aditamento ao G1)",
         "ESTADO": "PROPOSTA — aplica-se pelo pacote G1, no cutover",
         "METODO": "scripts/receitas/censo_e_proposta.por_fonte (6-PREP-d), sem alteracao; "
                   "DERIVACAO por linha",
         "CONTRATOS_LIDOS_DE": arg["contratos"], "FONTES": linhas}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for l in linhas:
        print(l["SOURCE_ID"], "PROPOE" if l["PROPOSTAS"] else "NAO_SEI",
              [p["DEPOIS"][:90] for p in l["PROPOSTAS"]] or (l.get("SEM_PROPOSTA") or "")[:140])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
