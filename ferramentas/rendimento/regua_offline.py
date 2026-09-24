# -*- coding: utf-8 -*-
"""LOTE-MICRO · a regua de HOJE sobre os textos JA colhidos, sem rede.

Corre `admissao._do_universo` (so o portao «pertence ao universo», que e o que
separa SIM de NAO/NAO_SEI) do bot instalado sobre cada documento_estruturado
das fontes pedidas. Serve para prever SIM com o historico, nao para decidir:
os outros portoes da Admissao (legivel, origem, identidade, materia) nao correm
aqui, por isso o numero e um TETO do que a regua deixaria entrar.

Uso: py ferramentas/rendimento/regua_offline.py --bot <arvore do bot> --ids IT-..,IT-.. --saida X.json
"""
import collections
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sala_por_fonte import psql  # noqa: E402


def main(argv):
    bot = Path(argv[argv.index("--bot") + 1])
    ids = argv[argv.index("--ids") + 1].split(",")
    sys.path.insert(0, str(bot / "admissao"))
    sys.path.insert(0, str(bot))
    import admissao as A  # noqa: E402
    lista = ",".join("'%s'" % i.replace("'", "") for i in ids)
    por = collections.defaultdict(collections.Counter)
    exemplo = {}
    for r in psql("select source_id, derived_artifact_id, regexp_replace(texto, '[\\r\\n\\x1e]+', ' ', 'g') "
                  "from documento_estruturado where source_id in (%s)" % lista):
        if len(r) < 3:
            continue
        sid, _did, texto = r
        u = sid.split("-")[1]
        res, motivo, _ev = A._do_universo({"texto": texto}, u, A.PERGUNTAS_DO_UNIVERSO.get(u, []))
        por[sid][res] += 1
        if res == "SIM" and sid not in exemplo:
            exemplo[sid] = motivo[:160]
    d = {"DATASET": "LOTE-REGUA-OFFLINE-V1", "MEDIDO_EM": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "REGUAS_INSTALADAS": sorted(A.PERGUNTAS_DO_UNIVERSO, key=lambda s: int(s[1:])),
         "SO_O_PORTAO_DO_UNIVERSO": True,
         "POR_FONTE": {s: {"TEXTOS": sum(por[s].values()), **dict(por[s]), "EXEMPLO_SIM": exemplo.get(s)} for s in ids}}
    Path(argv[argv.index("--saida") + 1]).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for s in ids:
        print(s, d["POR_FONTE"][s])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
