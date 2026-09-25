# -*- coding: utf-8 -*-
"""RECEITAS-182 · passo 2a: robots + pagina de entrada, 1 fonte por DOMINIO, guardados com sha256.

    py scripts/receitas_182/capturar_entradas.py <pasta-fora-do-git>

NAO e o robo (D41.3): so as fontes escolhidas aqui (fila filtrada), 1 por dominio registavel,
2 pedidos por dominio (robots pela casa, `gate_de_rota.robots_de`; entrada pelo leitor do reparo,
`reparar_contrato.buscar_com_destino` — mesmo UA, timeout e TLS). So depois do portao de
egresso por consenso dar PASS IT. O que sobra do teto D38 (5 por dominio) fica para os itens.

Escreve CAPTURA-ENTRADAS-V1.json (manifesto com sha256) ao lado deste ficheiro; os bytes e o
texto do robots ficam na pasta dada.
"""
import hashlib
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "superficie"))
import rede                      # noqa: E402
import reparar_contrato as RC    # noqa: E402
import gate_de_rota as GATE      # noqa: E402

VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
# 1 por dominio registavel, das 22 «lista com molde errado» (CLASSIFICACAO-182-V1.json).
# Onde o dominio tem varias, escolhe-se a que tem a lista no proprio endereco (news/notizie...).
ESCOLHIDAS = ["IT-T3-039", "IT-T12-151", "IT-T2-134", "IT-T3-051", "IT-T7-169", "IT-T5-164",
              "IT-T5-177", "IT-T8-061", "IT-T8-065", "IT-T8-066", "IT-T8-067", "IT-T3-062",
              "IT-T7-175", "IT-T8-069"]
PAUSA = 2.0


def main():
    saida = Path(sys.argv[1])
    saida.mkdir(parents=True, exist_ok=True)
    portao = rede.portao_de_egresso("IT")
    if portao["EGRESS_GATE"] != "PASS":
        print("PORTAO FECHADO", portao.get("PORQUE_BLOQUEADO"))
        return 2
    contratos = {c["SOURCE_ID"]: c for c in
                 json.loads((VIVO / "curadoria" / "italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}
    linhas = []
    for sid in ESCOLHIDAS:
        c = contratos[sid]
        aq = c.get("ACQUISITION") or {}
        entrada = aq.get("INDEX_URL") or c.get("CANONICAL_ENTRY_URL")
        host = urlparse(entrada).netloc
        l = {"SOURCE_ID": sid, "ENTRADA": entrada, "HOST": host, "PEDIDOS": 0}
        try:
            _, txt = GATE.robots_de(host)
            l["PEDIDOS"] += 1
            (saida / (sid + ".robots.txt")).write_text(txt or "", encoding="utf-8")
            rp = GATE.urllib.robotparser.RobotFileParser()
            rp.parse((txt or "").splitlines())
            l["ROBOTS"] = "LIDO"
            if not GATE.permitido(entrada, rp):
                l["ROBOTS"] = "PROIBE_A_ENTRADA"
                linhas.append(l)
                continue
        except Exception as e:   # noqa: BLE001
            l.update({"ROBOTS": "ILEGIVEL", "ERRO": repr(e)[:160]})
            linhas.append(l)
            continue
        time.sleep(PAUSA)
        st, b, err, destino = RC.buscar_com_destino(entrada)
        l["PEDIDOS"] += 1
        l.update({"HTTP": st, "ERRO": err or None, "DESTINO": destino if destino != entrada else None,
                  "BYTES": len(b or b"")})
        if b:
            (saida / (sid + ".html")).write_bytes(b)
            l["SHA256"] = hashlib.sha256(b).hexdigest()
            l["COMECO"] = repr(b[:12])
        linhas.append(l)
        print(sid, host, st, len(b or b""), flush=True)
        time.sleep(PAUSA)
    out = {"DATASET": "CAPTURA-ENTRADAS-V1", "EM": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "PORTAO": {k: portao.get(k) for k in ("EGRESS_GATE", "EGRESS_COUNTRY_CODE", "VOTOS_VALIDOS")},
           "PASTA_DOS_BYTES": str(saida), "FONTES": linhas,
           "PEDIDOS_TOTAL": sum(x["PEDIDOS"] for x in linhas)}
    (AQUI / "CAPTURA-ENTRADAS-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("pedidos", out["PEDIDOS_TOTAL"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
