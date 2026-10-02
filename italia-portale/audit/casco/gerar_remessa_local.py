"""Casco - le uma remessa do fluxo unico COMO ESTA e grava client/sintonia-remessa.local.js.

Entrada (pasta da remessa, ex. C:/Users/London1/sintonia-fluxo-unico/remessa-001):
  DOCUMENTOS.jsonl            (Coleta/Scrap: texto original)
  FATOS.validado.json         (LLM triagem, ja conferido pela ETAPA 4)
  SIGNALS.validado.json       (LLM cruzamento, ja conferido)
  OPPORTUNITIES.validado.json (LLM cruzamento, ja conferido)
  VALIDACAO.json              (resumo do conferidor)
O casco nao muda, nao filtra, nao cruza: so embute para a tela ler.
"""
import hashlib, json, os, sys, datetime

def main():
    pasta = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/London1/sintonia-fluxo-unico/remessa-001"
    saida = os.path.join(os.path.dirname(__file__), "..", "..", "client", "sintonia-remessa.local.js")
    if len(sys.argv) > 2:
        saida = sys.argv[2]
    nomes = ["FATOS.validado.json", "SIGNALS.validado.json", "OPPORTUNITIES.validado.json", "VALIDACAO.json"]
    pac = {"PASTA": os.path.basename(os.path.normpath(pasta)), "SHA256": {}}
    for n in nomes + ["DOCUMENTOS.jsonl"]:
        p = os.path.join(pasta, n)
        b = open(p, "rb").read()
        pac["SHA256"][n] = hashlib.sha256(b).hexdigest()
        pac.setdefault("MTIME", {})[n] = datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="minutes")
    pac["FATOS"] = json.load(open(os.path.join(pasta, nomes[0]), encoding="utf-8"))
    pac["SIGNALS"] = json.load(open(os.path.join(pasta, nomes[1]), encoding="utf-8"))
    pac["OPPORTUNITIES"] = json.load(open(os.path.join(pasta, nomes[2]), encoding="utf-8"))
    pac["VALIDACAO"] = json.load(open(os.path.join(pasta, nomes[3]), encoding="utf-8"))
    docs = {}
    for linha in open(os.path.join(pasta, "DOCUMENTOS.jsonl"), encoding="utf-8"):
        if linha.strip():
            d = json.loads(linha)
            docs[d["DOCUMENT_ID"]] = d
    pac["DOCUMENTOS"] = docs
    # contagem de ligacoes quebradas (so informa; nao corrige nada)
    fatos = {f["FACT_ID"] for d in pac["FATOS"]["documentos"] for f in d.get("fatos", [])}
    sinais = {s["SIGNAL_ID"] for s in pac["SIGNALS"]["itens"]}
    q = 0
    for s in pac["SIGNALS"]["itens"] + pac["OPPORTUNITIES"]["itens"]:
        q += sum(1 for f in s.get("FACT_IDS_VALIDOS", []) if f not in fatos)
        q += sum(1 for x in s.get("SIGNAL_IDs", []) if x not in sinais)
    q += sum(1 for d in pac["FATOS"]["documentos"] if d["DOCUMENT_ID"] not in docs)
    pac["LIGACOES_QUEBRADAS"] = q
    corpo = json.dumps(pac, ensure_ascii=False).replace("</", "<\\/")
    open(saida, "w", encoding="utf-8").write("window.SINTONIA_REMESSA=" + corpo + ";\n")
    print("OK", saida, "docs", len(docs), "fatos", len(fatos), "sinais", len(sinais),
          "oportunidades", len(pac["OPPORTUNITIES"]["itens"]), "ligacoes_quebradas", q)

if __name__ == "__main__":
    main()
