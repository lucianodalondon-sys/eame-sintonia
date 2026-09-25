# -*- coding: utf-8 -*-
"""RECEITAS-182 · passo 2b: o reparo (com o conserto) e o canario nas fontes capturadas.

    py scripts/receitas_182/medir_com_rede.py <pasta-das-entradas> [--sem-rede]

NAO e o robo (D41.3), NAO escreve em livro nenhum (nem no vivo, nem nesta arvore).
  · reparo: `reparar_contrato.inferir`, como o worker o chama (`worker.etapa_repair_contract`):
    `outros` = contratos do livro vivo que estao READY ou ja reparados (a guarda DUPLICADA).
  · a entrada e o robots vem da CAPTURA-ENTRADAS-V1 (sha256 conferido): 0 pedidos.
  · os itens vao a rede SO se faltarem, com teto de 3 pedidos por dominio (D38: 5 por dominio,
    2 ja gastos na captura), depois de o portao de egresso por consenso dar PASS IT.
    `--sem-rede`: nenhum pedido; o que faltar fica NAO_MEDIDO.
  · canario: `canario.canario_html` sobre o contrato reparado (`reparar_contrato.aplicar`, puro),
    com `canario.buscar` servido do que o reparo ja leu — o canario abre a MESMA entrada e o MESMO
    item. Se precisar de outra pagina, NAO_MEDIDO (nao se pede).

Escreve MEDICAO-COM-REDE-V1.json ao lado; bytes novos na pasta dada, com sha256 no JSON.
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
import canario as CAN            # noqa: E402
import gate_de_rota as GATE      # noqa: E402
import reparar_contrato as RC    # noqa: E402

VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
TETO_ITENS_POR_DOMINIO = 3
SUFIXOS_REGIONAIS = {"campania", "marche", "veneto", "toscana", "sardegna", "fvg", "vda", "sicilia", "umbria",
                     "puglia", "lombardia", "molise", "calabria", "basilicata", "liguria", "lazio", "piemonte",
                     "abruzzo", "trentino", "bz", "gov"}


def dominio(host: str) -> str:
    p = host.lower().removeprefix("www.").split(".")
    return ".".join(p[-3:]) if len(p) >= 3 and p[-2] in SUFIXOS_REGIONAIS else ".".join(p[-2:])


def main():
    pasta = Path(sys.argv[1])
    sem_rede = "--sem-rede" in sys.argv
    cap = json.loads((AQUI / "CAPTURA-ENTRADAS-V1.json").read_text(encoding="utf-8"))
    livro = json.loads((VIVO / "curadoria" / "italy_contracts_curator.json").read_text(encoding="utf-8"))
    ledger = json.loads((VIVO / "curadoria" / "LIFECYCLE-LEDGER-V1.json").read_text(encoding="utf-8"))
    estado = {}
    for t in ledger.get("TRANSICOES", []):
        estado[t.get("SOURCE_ID")] = t.get("NEW_STATE")
    contratos = {c["SOURCE_ID"]: c for c in livro["FONTES"]}

    cache, robots_txt = {}, {}
    for f in cap["FONTES"]:
        b = (pasta / (f["SOURCE_ID"] + ".html")).read_bytes()
        if hashlib.sha256(b).hexdigest() != f["SHA256"]:
            raise SystemExit("%s: sha256 da entrada mudou" % f["SOURCE_ID"])
        cache[f["ENTRADA"]] = (f["HTTP"], b, "", f.get("DESTINO") or f["ENTRADA"])
        robots_txt[urlparse(f["ENTRADA"]).netloc] = (pasta / (f["SOURCE_ID"] + ".robots.txt")).read_text(encoding="utf-8")

    if not sem_rede:
        import rede   # noqa: PLC0415
        portao = rede.portao_de_egresso("IT")
        if portao["EGRESS_GATE"] != "PASS":
            print("PORTAO FECHADO — sigo sem rede:", portao.get("PORQUE_BLOQUEADO"))
            sem_rede = True
    gasto, novos_bytes = {}, []

    def buscar(url):
        if url in cache:
            return cache[url]
        d = dominio(urlparse(url).netloc)
        if sem_rede or gasto.get(d, 0) >= TETO_ITENS_POR_DOMINIO:
            return 0, b"", "NAO_MEDIDO: %s" % ("sem rede" if sem_rede else "teto D38 do dominio"), url
        gasto[d] = gasto.get(d, 0) + 1
        r = RC.buscar_com_destino(url)
        cache[url] = r
        if r[1]:
            nome = hashlib.sha256(url.encode()).hexdigest()[:16] + ".html"
            (pasta / nome).write_bytes(r[1])
            novos_bytes.append({"URL": url, "HTTP": r[0], "FICHEIRO": nome, "SHA256": hashlib.sha256(r[1]).hexdigest()})
        return r

    def robots_de(host):
        txt = robots_txt.get(host)
        if txt is None:
            raise RuntimeError("robots de %s nao capturado — nao se pede" % host)
        rp = GATE.urllib.robotparser.RobotFileParser()
        rp.parse(txt.splitlines())
        return rp, txt

    linhas = []
    for f in cap["FONTES"]:
        sid = f["SOURCE_ID"]
        base = contratos[sid]
        outros = {c["SOURCE_ID"]: c for c in livro["FONTES"] if c["SOURCE_ID"] != sid
                  and (estado.get(c["SOURCE_ID"]) == "READY_FOR_COLLECTION" or c.get("REPARO_DE_CONTRATO"))}
        p = RC.inferir(base, outros=outros, buscar=buscar, robots_de=robots_de, permitido=GATE.permitido, pausa=2.0)
        l = {"SOURCE_ID": sid, "DESFECHO": p["DESFECHO"], "MOTIVO": p.get("MOTIVO"), "PORQUE": (p.get("PORQUE") or "")[:300],
             "LINK_PATTERN": p.get("LINK_PATTERN"), "COMO": p.get("COMO"), "ITEM_LIDO": p.get("ITEM_LIDO"),
             "TENTADOS": [{k: t.get(k) for k in ("PADRAO", "ALVO", "VEREDITO")} for t in p.get("TENTADOS") or []]}
        if p["DESFECHO"] == "PADRAO_NOVO":
            novo = RC.aplicar(base, p)
            antes = CAN.buscar
            CAN.buscar = lambda u: (lambda r: (r[0], r[1], r[2]))(cache[u]) if u in cache else (0, b"", "NAO_MEDIDO: pagina nao lida pelo reparo")
            try:
                r = CAN.canario_html(novo)
            finally:
                CAN.buscar = antes
            l["CANARIO"] = {k: r.get(k) for k in ("PASS", "CLASSE", "PORQUE", "ALVO", "DETAIL_GATE_PASSED")}
        linhas.append(l)
        print(sid, p["DESFECHO"], p.get("MOTIVO") or "", "| canario:", (l.get("CANARIO") or {}).get("PASS"), flush=True)
    out = {"DATASET": "MEDICAO-COM-REDE-V1", "EM": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "SEM_REDE": sem_rede, "PEDIDOS_DE_ITENS_POR_DOMINIO": gasto, "PEDIDOS_DE_ITENS": sum(gasto.values()),
           "BYTES_NOVOS": novos_bytes, "FONTES": linhas,
           "PADRAO_NOVO": sum(1 for x in linhas if x["DESFECHO"] == "PADRAO_NOVO"),
           "CANARIO_PASS": sum(1 for x in linhas if (x.get("CANARIO") or {}).get("PASS"))}
    (AQUI / "MEDICAO-COM-REDE-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("PADRAO_NOVO", out["PADRAO_NOVO"], "CANARIO_PASS", out["CANARIO_PASS"], "pedidos", out["PEDIDOS_DE_ITENS"])


if __name__ == "__main__":
    main()
