"""SINTONIA_FAST_V1 -> leitura do casco (so local).

Le a pasta FAST-V1 da Intelligence COMO ESTA, confere SHA256SUMS (falha fechada)
e grava italia-portale/client/sintonia-fast.local.js (ignorado pelo Git e pela Vercel).
Nao muda, nao filtra e nao reinterpreta nenhum objeto: so empacota para a tela.

Uso: python italia-portale/audit/casco/gerar_fast_local.py [pasta]
  pasta = uma corrida (FAST-V1) ou a raiz FAST-AUTO: com ULTIMA.txt (RUN_ID=<id>) le so
  FAST-AUTO/<id>/; raw_texto/ so entra se estiver no SHA256SUMS e conferir.
"""
import hashlib, json, os, sys

PADRAO = "C:/Users/London1/sintonia-sala-italia/intelligence-experimental/FAST-V1"
ARQS = ["FACTS_FAST.json", "SIGNALS_FAST.json", "OPPORTUNITIES_FAST.json", "DOCUMENTOS_FAST.json"]
AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.normpath(os.path.join(AQUI, "..", "..", "client", "sintonia-fast.local.js"))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    pasta = sys.argv[1] if len(sys.argv) > 1 else PADRAO
    run_id = None
    ponteiro = os.path.join(pasta, "ULTIMA.txt")
    if os.path.exists(ponteiro):
        linhas = [l.strip() for l in open(ponteiro, encoding="utf-8") if l.strip()]
        if len(linhas) != 1 or not linhas[0].startswith("RUN_ID="):
            sys.exit(f"RECUSADO: ULTIMA.txt fora do contrato: {linhas!r}")
        run_id = linhas[0][len("RUN_ID="):].strip()
        if not run_id or "/" in run_id or "\\" in run_id or ".." in run_id:
            sys.exit(f"RECUSADO: RUN_ID invalido {run_id!r}")
        pasta = os.path.join(pasta, run_id)
    somas = {}
    for linha in open(os.path.join(pasta, "SHA256SUMS.txt"), encoding="utf-8"):
        if linha.strip():
            h, nome = linha.split(None, 1)
            somas[nome.strip().lstrip("*")] = h
    conf = {}
    for a in ARQS:
        real = sha(os.path.join(pasta, a))
        if somas.get(a) != real:
            sys.exit(f"RECUSADO: {a} sha {real} != SHA256SUMS {somas.get(a)}")
        conf[a] = real
    j = {a: json.load(open(os.path.join(pasta, a), encoding="utf-8")) for a in ARQS}
    textos = {}
    for d in j["DOCUMENTOS_FAST.json"]:
        p = os.path.join(pasta, "raw_texto", d["DOCUMENT_ID"] + ".txt")
        nome = "raw_texto/" + d["DOCUMENT_ID"] + ".txt"
        if not os.path.exists(p):
            textos[d["DOCUMENT_ID"]] = None
        elif run_id is not None and somas.get(nome) != sha(p):
            textos[d["DOCUMENT_ID"]] = None  # sem conferencia = NAO SEI na tela
        else:
            textos[d["DOCUMENT_ID"]] = open(p, encoding="utf-8").read()
    # integridade do caminho de clique (so mede; nada e removido)
    fatos = {f["FACT_ID"] for f in j["FACTS_FAST.json"]["FATOS"]}
    sinais = {s["SIGNAL_ID"] for s in j["SIGNALS_FAST.json"]["SINAIS"]}
    docs = {d["DOCUMENT_ID"] for d in j["DOCUMENTOS_FAST.json"]}
    quebras = []
    for o in j["OPPORTUNITIES_FAST.json"]["OPORTUNIDADES"]:
        quebras += [f"{o['OPPORTUNITY_ID']}->{x}" for x in o.get("FACT_IDS", []) if x not in fatos]
        quebras += [f"{o['OPPORTUNITY_ID']}->{x}" for x in o.get("SIGNAL_IDS", []) if x not in sinais]
    for s in j["SIGNALS_FAST.json"]["SINAIS"]:
        quebras += [f"{s['SIGNAL_ID']}->{x}" for x in s.get("FACT_IDS", []) if x not in fatos]
    for f in j["FACTS_FAST.json"]["FATOS"]:
        if f["DOCUMENT_ID"] not in docs:
            quebras.append(f"{f['FACT_ID']}->{f['DOCUMENT_ID']}")
    pacote = {
        "PASTA": pasta.replace("\\", "/"),
        "RUN_ID_PONTEIRO": run_id,
        "SHA256": conf,
        "FACTS": j["FACTS_FAST.json"],
        "SIGNALS": j["SIGNALS_FAST.json"],
        "OPPORTUNITIES": j["OPPORTUNITIES_FAST.json"],
        "DOCUMENTOS": j["DOCUMENTOS_FAST.json"],
        "RAW_TEXTO": textos,
        "LINKS_QUEBRADOS": quebras,
    }
    corpo = json.dumps(pacote, ensure_ascii=False).replace("</", "<\\/")
    open(SAIDA, "w", encoding="utf-8", newline="\n").write(
        "/* GERADO por italia-portale/audit/casco/gerar_fast_local.py — so local, nunca publicar */\n"
        "window.SINTONIA_FAST = " + corpo + ";\n")
    print(f"OK {SAIDA} run={run_id}\n  fatos={len(fatos)} sinais={len(sinais)} oportunidades="
          f"{len(j['OPPORTUNITIES_FAST.json']['OPORTUNIDADES'])} docs={len(docs)} "
          f"textos={sum(1 for v in textos.values() if v)} links_quebrados={len(quebras)}")


if __name__ == "__main__":
    main()
