"""D39: a medicao com rede (ROBOTS-COM-REDE.json, 25/09) relida pelo leitor D39 — OFFLINE, sobre os
MESMOS robots baixados (C:/cur/rfc/rede/robots, sha256 em ROBOTS-BAIXADOS.sha256) e os mesmos codigos
de resposta guardados. Nenhum pedido de rede.
uso: py provas/robots_rfc/reler_com_d39.py <pasta dos robots baixados>"""
import collections
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "coleta"))
import robots_rfc9309 as RR   # noqa: E402

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0"
PASTA = Path(sys.argv[1])
AQUI = Path(__file__).parent
d = json.loads((AQUI / "ROBOTS-COM-REDE.json").read_text(encoding="utf-8"))
linhas = []
for x in d["TODAS"]:
    u = urlsplit(x["ROTA"])
    corpo = (PASTA / (u.netloc.replace(":", "_") + ".txt")).read_bytes()
    assert hashlib.sha256(corpo).hexdigest() == x["ROBOTS_SHA256"], x["SOURCE_ID"]
    rp = RR.de_resposta(x["ROBOTS_STATUS"], corpo, erro="rede" if x["ROBOTS_STATUS"] is None else None)
    n = rp.decidir(UA, x["ROTA"])
    linhas.append(dict(x, ROBOTS_ESTADO_D39=rp.estado, NOVO_D39=n.permite, REGRA_D39=n.regra))
abre = [x for x in linhas if not x["ANTIGO"] and x["NOVO_D39"]]
fecha = [x for x in linhas if x["ANTIGO"] and not x["NOVO_D39"]]
so_nome = [x for x in linhas if x["ANTIGO"] == x["NOVO_D39"] and x["ROBOTS_ESTADO_D39"] in
           (RR.ACCESS_DENIED, RR.INVALID_CONTENT)]
mudam = abre + fecha + [x for x in linhas if x["SOURCE_ID"] in {m["SOURCE_ID"] for m in d["MUDAM"]}
                        and x not in abre and x not in fecha]
por = lambda xs: dict(collections.Counter(x["ROBOTS_ESTADO_D39"] for x in xs))
out = {"MEDICAO": "D39 — ROBOTS-COM-REDE relida pelo leitor %s, offline" % RR.VERSAO,
       "FONTES": len(linhas),
       "PROIBIDA_PARA_PERMITIDA": len(abre), "PROIBIDA_PARA_PERMITIDA_POR_ESTADO": por(abre),
       "PERMITIDA_PARA_PROIBIDA": len(fecha), "PERMITIDA_PARA_PROIBIDA_POR_ESTADO": por(fecha),
       "MESMO_VEREDITO_NOME_NOVO": len(so_nome), "MESMO_VEREDITO_NOME_NOVO_POR_ESTADO": por(so_nome),
       "A_RE_MEDIR_DEPOIS_DE_INSTALAR": len(mudam),
       "MUDAM": mudam, "TODAS": linhas}
(AQUI / "ROBOTS-COM-REDE-D39.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k not in ("MUDAM", "TODAS")}, ensure_ascii=False, indent=1))
