"""SINTONIA_FAST -> leitura do casco (historico de rodadas).

Le as rodadas da Intelligence COMO ESTAO, confere SHA256SUMS de cada uma e grava
italia-portale/client/sintonia-fast.local.js.
Nao muda, nao filtra e nao reinterpreta nenhum objeto: so empacota para a tela.

Rodadas lidas (todas; a tela poe a mais nova primeiro):
  - FAST-V1 (primeira rodada, manual; raw_texto ali nao esta no SHA256SUMS);
  - FAST-AUTO/<RUN_ID>/ para cada pasta com SHA256SUMS.txt (raw_texto so entra se
    estiver no SHA256SUMS e conferir; senao a tela diz NAO SEI).
Rodada cujos 4 JSON nao conferem fica FORA da tela (motivo impresso); as outras seguem.
ULTIMA.txt (RUN_ID=<id>) so diz qual rodada automatica e a mais recente entregue.

Uso: python italia-portale/audit/casco/gerar_fast_local.py [--saida ARQ] [raiz]
  raiz = pasta intelligence-experimental (padrao abaixo).
"""
import hashlib, json, os, sys

RAIZ = "C:/Users/London1/sintonia-sala-italia/intelligence-experimental"
ARQS = ["FACTS_FAST.json", "SIGNALS_FAST.json", "OPPORTUNITIES_FAST.json", "DOCUMENTOS_FAST.json"]
AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.normpath(os.path.join(AQUI, "..", "..", "client", "sintonia-fast.local.js"))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def carregar(pasta, nome_rodada, texto_exige_soma):
    somas = {}
    for linha in open(os.path.join(pasta, "SHA256SUMS.txt"), encoding="utf-8"):
        if linha.strip():
            h, nome = linha.split(None, 1)
            somas[nome.strip().lstrip("*")] = h
    conf = {}
    for a in ARQS:
        real = sha(os.path.join(pasta, a))
        if somas.get(a) != real:
            raise ValueError(f"{a} sha {real} != SHA256SUMS {somas.get(a)}")
        conf[a] = real
    j = {a: json.load(open(os.path.join(pasta, a), encoding="utf-8")) for a in ARQS}
    textos = {}
    for d in j["DOCUMENTOS_FAST.json"]:
        p = os.path.join(pasta, "raw_texto", d["DOCUMENT_ID"] + ".txt")
        nome = "raw_texto/" + d["DOCUMENT_ID"] + ".txt"
        if not os.path.exists(p):
            textos[d["DOCUMENT_ID"]] = None
        elif (texto_exige_soma or nome in somas) and somas.get(nome) != sha(p):
            textos[d["DOCUMENT_ID"]] = None  # sem conferencia = NAO SEI na tela
        else:
            textos[d["DOCUMENT_ID"]] = open(p, encoding="utf-8").read()
    # integridade do caminho de clique, DENTRO da rodada (so mede; nada e removido)
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
    return {
        "RODADA": nome_rodada,
        "SHA256": conf,
        "FACTS": j["FACTS_FAST.json"],
        "SIGNALS": j["SIGNALS_FAST.json"],
        "OPPORTUNITIES": j["OPPORTUNITIES_FAST.json"],
        "DOCUMENTOS": j["DOCUMENTOS_FAST.json"],
        "RAW_TEXTO": textos,
        "LINKS_QUEBRADOS": quebras,
    }


def main():
    args = sys.argv[1:]
    saida = SAIDA
    if "--saida" in args:
        i = args.index("--saida")
        saida = os.path.abspath(args[i + 1])
        del args[i:i + 2]
    raiz = args[0] if args else RAIZ
    candidatas = []
    v1 = os.path.join(raiz, "FAST-V1")
    if os.path.exists(os.path.join(v1, "SHA256SUMS.txt")):
        candidatas.append(("FAST-V1", v1, False))
    auto = os.path.join(raiz, "FAST-AUTO")
    ultima = None
    if os.path.isdir(auto):
        p = os.path.join(auto, "ULTIMA.txt")
        if os.path.exists(p):
            linhas = [l.strip() for l in open(p, encoding="utf-8") if l.strip()]
            if len(linhas) == 1 and linhas[0].startswith("RUN_ID="):
                ultima = linhas[0][len("RUN_ID="):].strip()
        for n in sorted(os.listdir(auto)):
            d = os.path.join(auto, n)
            if os.path.isdir(d) and os.path.exists(os.path.join(d, "SHA256SUMS.txt")):
                candidatas.append((n, d, True))
    rodadas, recusadas = [], []
    for nome, pasta, exige in candidatas:
        try:
            rodadas.append(carregar(pasta, nome, exige))
        except Exception as e:  # uma rodada ruim nao derruba as outras
            recusadas.append(f"{nome}: {e}")
    rodadas.sort(key=lambda r: r["OPPORTUNITIES"].get("GERADO_EM") or "", reverse=True)
    if not rodadas:
        sys.exit("RECUSADO: nenhuma rodada conferida; arquivo anterior mantido. " + "; ".join(recusadas))
    pacote = {"RODADAS": rodadas, "ULTIMA": ultima, "RODADAS_RECUSADAS": recusadas}
    corpo = json.dumps(pacote, ensure_ascii=False).replace("</", "<\\/")
    tmp = saida + ".tmp"
    open(tmp, "w", encoding="utf-8", newline="\n").write(
        "/* GERADO por italia-portale/audit/casco/gerar_fast_local.py */\n"
        "window.SINTONIA_FAST = " + corpo + ";\n")
    os.replace(tmp, saida)
    print(f"OK {saida} ultima={ultima}")
    for r in rodadas:
        print(f"  {r['RODADA']}: docs={len(r['DOCUMENTOS'])} fatos={len(r['FACTS']['FATOS'])} "
              f"sinais={len(r['SIGNALS']['SINAIS'])} oportunidades={len(r['OPPORTUNITIES']['OPORTUNIDADES'])} "
              f"textos={sum(1 for v in r['RAW_TEXTO'].values() if v)} links_quebrados={len(r['LINKS_QUEBRADOS'])}")
    for x in recusadas:
        print("  RECUSADA", x)


if __name__ == "__main__":
    main()
