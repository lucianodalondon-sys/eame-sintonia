"""PROVA DA ORQUESTRA (CUR-PRONTA): coleta e Curator ao mesmo tempo, na copia C:/cur/t1.

A = a coleta: pergunta ao portao por cada fonte da coorte, pelo MESMO caminho do
    executor (italy_executor.admissao_do_curator), em ciclo.
B = o Curator: ao mesmo tempo, tira da READY as fontes da coorte (VALIDATE_ROUTE
    faz isto: READY -> CANARY_PENDING), grava evidencia e fila, sem parar.
Duas corridas: COM a foto da onda (ONDA-EM-CURSO) e SEM ela. Sem rede.
"""
import json, os, subprocess, sys, time, threading
RAIZ = "C:/cur/t1"
os.chdir(RAIZ)
sys.path.insert(0, RAIZ + "/curadoria"); sys.path.insert(0, RAIZ + "/coleta")
import collection_gate as CG, lifecycle as LC, fila as F, onda_em_curso as OND
import worker as W
from pathlib import Path

LIVROS = ["curadoria/LIFECYCLE-LEDGER-V1.json", "curadoria/LIFECYCLE-QUEUE-V1.json",
          "curadoria/LIFECYCLE-EVIDENCE-V1.json"]
FOTO = "C:/cur/foto-20260924-1024"


def repor():
    for f in LIVROS + ["curadoria/italy_contracts_curator.json"]:
        Path(RAIZ, f).write_bytes(Path(FOTO, f).read_bytes())


def admissao(fonte):
    import italy_executor as IE
    return IE.admissao_do_curator(fonte, RAIZ)


def corrida(com_foto: bool, voltas=3):
    repor()
    OND.fechar()
    coorte = sorted(CG.elegiveis())
    Path("C:/cur/COORTE-PROVA.json").write_text(json.dumps(
        {"COORTE": [{"SOURCE_ID": s, "INDEX_URL": ""} for s in coorte]}), encoding="utf-8")
    if com_foto:
        OND.abrir(Path("C:/cur/COORTE-PROVA.json"))
    res = {"ADMITIDAS": 0, "RECUSADAS": 0, "GATE_NAO_RESPONDEU": 0, "MOTIVOS": {}}
    curator = {"ESCRITAS": 0, "FALHAS_DE_ESCRITA": []}
    parar = threading.Event()

    def B():
        i = 0
        while not parar.is_set():
            sid = coorte[i % len(coorte)]
            try:
                if LC.estado_de(sid) == LC.READY_FOR_COLLECTION:
                    LC.registar(sid, LC.CANARY_PENDING, "prova da orquestra: re-medir", evidence_ref=None)
                W._guardar_evidencia(sid, "PROVA_ORQUESTRA", {"i": i})
                F.enfileirar(sid, F.VALIDATE_ROUTE, priority=55, motivo="prova da orquestra")
                curator["ESCRITAS"] += 3
            except Exception as e:  # noqa: BLE001
                curator["FALHAS_DE_ESCRITA"].append("%s: %s" % (type(e).__name__, str(e)[:80]))
            i += 1
            time.sleep(0.05)

    t = threading.Thread(target=B, daemon=True)
    t.start()
    t0 = time.time()
    for v in range(voltas):
        for s in coorte:
            a = admissao(s)
            k = "ADMITIDAS" if a["ADMITIDA"] else "RECUSADAS"
            res[k] += 1
            if a["MOTIVO"] == "GATE_NAO_RESPONDEU":
                res["GATE_NAO_RESPONDEU"] += 1
            res["MOTIVOS"][a["MOTIVO"]] = res["MOTIVOS"].get(a["MOTIVO"], 0) + 1
    parar.set(); t.join()
    OND.fechar()
    fora_de_ready = sum(1 for s in coorte if LC.estado_de(s) != LC.READY_FOR_COLLECTION)
    return {"COM_FOTO": com_foto, "COORTE": len(coorte), "PERGUNTAS": voltas * len(coorte),
            "SEGUNDOS": round(time.time() - t0), **res,
            "CURATOR": {"ESCRITAS": curator["ESCRITAS"], "FALHAS": len(curator["FALHAS_DE_ESCRITA"]),
                        "EXEMPLOS": curator["FALHAS_DE_ESCRITA"][:3]},
            "COORTE_FORA_DE_READY_NO_FIM": fora_de_ready}


if __name__ == "__main__":
    out = [corrida(True), corrida(False)]
    repor()
    print(json.dumps(out, ensure_ascii=False, indent=1))
    Path("C:/cur/PROVA-ORQUESTRA.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
