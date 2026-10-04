# -*- coding: utf-8 -*-
"""LEGACY-99 v4 · ensaio em COPIA dos livros do vivo: A (21 HTML) e B (41 YouTube pelo Scrap).

Corre DENTRO da copia (recusa a arvore do bot vivo). Sem rede: o que o Scrap declara
le-se dos ficheiros do Scrap na copia; a identidade gerada pelo coletor vem do Node
local. B e aplicado uma fonte de cada vez (o `pelo_scrap` e tudo-ou-nada: assim cada
salto fica com o seu porque). Nada aqui promove: conta-se o estado de cada fonte depois.

Uso (na copia): py ferramentas/legacy99v4/ensaio_na_copia.py --saida X.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
if "source-curator-service-v1" in str(RAIZ).replace("\\", "/"):
    sys.exit("RECUSADO: isto e a arvore do bot vivo")
import importar_do_coletor as I    # noqa: E402
import lifecycle as LC             # noqa: E402
import rota_do_scrap_youtube as RSY  # noqa: E402
import regua_social as RG          # noqa: E402
import ready_split as RS           # noqa: E402


def main(argv) -> int:
    plano = I.planear()
    html = [p["SOURCE_ID"] for p in plano["IMPORTA"]]
    yt = [p["SOURCE_ID"] for p in plano["PELO_SCRAP"]]
    out = {"PLANO": {"IMPORTA": len(html), "PELO_SCRAP": len(yt), "FICA": len(plano["FICA"]),
                     "FICA_PORQUE": dict(Counter(f["PORQUE"].split(":")[0] for f in plano["FICA"]))}}
    a = I.aplicar(html)
    out["A"] = {"IMPORTADAS": len(a["IMPORTADAS"]), "REMEDIDAS": a["REMEDIDAS"],
                "ESTADOS": dict(Counter(LC.estado_de(s) for s in html))}
    b_ok, b_salta = [], {}
    for sid in yt:
        try:
            I.pelo_scrap([sid])
            b_ok.append(sid)
        except I.ImportacaoInvalida as e:
            b_salta[sid] = str(e)[:200]
    contratos = {c["SOURCE_ID"]: c for c in json.loads(I.CURATOR.read_text(encoding="utf-8"))["FONTES"]}
    conf = Counter(RSY.conferir(contratos[s]["ACQUISITION"])[0] for s in b_ok)
    promo = {"OBSERVED_AT": "agora", "EVIDENCE_REF": "EV"}
    regua = Counter(RS.passos_da_promocao(promo, {"DADOS": {}}, contratos[s])["REGUA"] for s in b_ok)
    out["B"] = {"NA_ROTA_DO_SCRAP": len(b_ok), "SALTARAM": b_salta,
                "ESTADOS": dict(Counter(LC.estado_de(s) for s in yt)),
                "CONFERIR_DO_SCRAP_OK": dict(conf), "REGUA_SEM_CANARIO_DO_SCRAP": dict(regua),
                "FASES_VIDEO_DA_REGUA_SOCIAL": sorted(RG.FASES_VIDEO)}
    out["AINDA_READY_DEPOIS"] = sorted(s for s in html + yt if LC.estado_de(s) == LC.READY_FOR_COLLECTION)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if "--saida" in argv:
        Path(argv[argv.index("--saida") + 1]).write_text(json.dumps(
            dict(out, DATASET="LEGACY-99-V4-ENSAIO-NA-COPIA", HTML=html, YOUTUBE=yt), ensure_ascii=False,
            indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
