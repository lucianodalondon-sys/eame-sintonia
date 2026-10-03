"""PROPOSTA-RECEITAS-V4 — K1: as fontes dos dois gabaritos que nao passam os 4 passos.

PROPOSTA, NAO APLICACAO. Escreve so curadoria/PROPOSTA-RECEITAS-V4.json, no formato
das V1/V2/V3, que o pacote G1 (scripts/desbloqueio/aplicar_desbloqueio.py) le.

    py scripts/receitas/propor_receitas_v4.py --contratos=<livro do portao, COPIA pos-B2>
                                              --alvo=<json com a lista de SOURCE_ID>

O metodo e o MESMO da V3 (e do 6-PREP-d): `propor_receitas_v3.propor`, que chama
`censo_e_proposta.por_fonte` sem alteracao — materia confirmada lida, familia >= 2
na pagina de entrada, o MESMO guarda `e_generico`, e o SLUG_COM_PERCENT quando o
padrao nao casa a propria materia. UMA diferenca, declarada: as paginas do GABARITO
DE CONTROLO LD2 (~/ld2-controlo, rotuladas por humano) entram tambem como paginas
lidas — a V3 nao as tinha. Tudo o que nao tem prova e NAO SEI com o motivo do
proprio por_fonte.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
HOME = Path.home()
sys.path.insert(0, str(AQUI))
import propor_receitas_v3 as V3  # noqa: E402

SAIDA = RAIZ / "curadoria" / "PROPOSTA-RECEITAS-V4.json"


def paginas_do_controlo() -> list[dict]:
    r = subprocess.run(["git", "show", "origin/listing-detail-v3:scripts/detector_capa/GABARITO-CONTROLO-LD2.json"],
                       cwd=RAIZ, capture_output=True)
    g = json.loads(r.stdout.decode("utf-8"))
    out = []
    for p in g["PAGINAS"]:
        if p.get("VEREDITO") not in ("CAPA", "MATERIA"):
            continue
        papel = "CAPA_INDICE" if "CAPA_INDICE" in (p.get("PAPEL") or "") else (
            "MATERIA" if p["VEREDITO"] == "MATERIA" else "CAPA_OUTRA")
        out.append({"SOURCE_ID": p["SOURCE_ID"], "URL": p["URL"], "VEREDITO": p["VEREDITO"],
                    "PAPEL": papel, "BYTES": HOME / "ld2-controlo" / p["FICHEIRO"],
                    "ORIGEM": "controlo-ld2:" + p["URL"]})
    return out


def paginas() -> list[dict]:
    vistas = set()
    out = []
    for p in V3.paginas() + paginas_do_controlo():
        if p["URL"] in vistas:
            continue
        vistas.add(p["URL"])
        out.append(p)
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    contratos = {f["SOURCE_ID"]: f for f in json.loads(
        Path(arg["contratos"]).read_text(encoding="utf-8"))["FONTES"]}
    V3.ALVO = json.loads(Path(arg["alvo"]).read_text(encoding="utf-8"))
    linhas = V3.propor(contratos, paginas())
    for l in linhas:
        l["DERIVACAO"] = l.get("DERIVACAO", "") + ", PAGINAS_V3+CONTROLO_LD2 (K1)"
    d = {"DATASET": "PROPOSTA-RECEITAS-V4", "MISSAO": "K1 (aditamento ao G1)",
         "ESTADO": "PROPOSTA — aplica-se pelo pacote G1, no cutover",
         "METODO": "scripts/receitas/propor_receitas_v3.propor (= censo_e_proposta.por_fonte), sem alteracao",
         "CONTRATOS_LIDOS_DE": arg["contratos"], "ALVO": V3.ALVO, "FONTES": linhas}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n = sum(1 for l in linhas if l["PROPOSTAS"])
    print("PROPOE %d / NAO_SEI %d" % (n, len(linhas) - n))
    for l in linhas:
        if l["PROPOSTAS"]:
            print(" ", l["SOURCE_ID"], [(p["CAMPO"], p["DEPOIS"][:80]) for p in l["PROPOSTAS"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
