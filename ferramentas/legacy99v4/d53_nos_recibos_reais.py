# -*- coding: utf-8 -*-
"""LEGACY-99 v4 · a prova da D53 nos recibos REAIS do Scrap (so leitura, sem rede).

Le ENVELOPE.json de colheitas YouTube ja guardadas noutras arvores de trabalho e
passa cada item por `regua_social.provas_do_video`, com o canal que o proprio item
declara (o contrato nao esta ao lado do recibo). Mede se os adaptadores do Scrap
trazem as quatro provas — nao julga fontes, nao escreve em livro nenhum.

Uso: py ferramentas/legacy99v4/d53_nos_recibos_reais.py LISTA.txt RAIZ [--saida X.json]
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AQUI / "curadoria"))
import regua_social as R   # noqa: E402


def main(argv) -> int:
    lista, raiz = Path(argv[1]), Path(argv[2])
    linhas, faltas = [], Counter()
    for rel in [x.strip() for x in lista.read_text(encoding="utf-8").splitlines() if x.strip()]:
        p = raiz / rel
        b = p.read_bytes()
        e = json.loads(b)
        for i, it in enumerate(e.get("COLHEITA") or []):
            ob = it.get("OBSERVACAO") or {}
            raw = ob.get("RAW") or {}
            canal = ob.get("CHANNEL_ID") or raw.get("CHANNEL_ID") or ob.get("SOURCE_ACCOUNT")
            f = R.provas_do_video(ob, canal)
            faltas.update(f or ["NADA"])
            linhas.append({"ENVELOPE": rel, "SHA256": hashlib.sha256(b).hexdigest(), "FASE": e.get("FASE"),
                           "ITEM": i, "NATIVE_ID": ob.get("NATIVE_ID"), "FALTA": f,
                           "CANAL_DECLARADO_PELO_ITEM": canal,
                           # a regua de antes da D53 ja reprovava este item? (CAMPOS_DO_ITEM)
                           "A_REGUA_ANTIGA_JA_REPROVAVA": [k for k in R.CAMPOS_DO_ITEM
                                                           if not ob.get(k) or ob.get(k) == "NAO SEI"]})
    por_fase = Counter((l["FASE"], not l["FALTA"]) for l in linhas)
    print("itens", len(linhas), "· provados", sum(1 for l in linhas if not l["FALTA"]))
    print("por fase (fase, provado):", dict(por_fase))
    print("faltas:", dict(faltas))
    print("itens que a regua de antes da D53 ja reprovava:",
          sum(1 for l in linhas if l["A_REGUA_ANTIGA_JA_REPROVAVA"]), "de", len(linhas))
    if "--saida" in argv:
        Path(argv[argv.index("--saida") + 1]).write_text(json.dumps(
            {"DATASET": "LEGACY-99-V4-D53-RECIBOS-REAIS", "NOTA": (
                "o canal e o que o proprio item declara: prova que os campos existem, nao que o "
                "canal e o do contrato"), "ITENS": linhas}, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
