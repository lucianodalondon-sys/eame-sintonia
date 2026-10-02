"""Casco - le uma remessa do fluxo unico COMO ESTA e grava client/sintonia-remessa.local.js.

Entrada (pasta da remessa, ex. C:/Users/London1/sintonia-fluxo-unico/remessa-001):
  DOCUMENTOS.jsonl            (Coleta/Scrap: texto original)
  FATOS.validado.json         (LLM triagem, ja conferido pela ETAPA 4)
  SIGNALS.validado.json       (LLM cruzamento, ja conferido)
  OPPORTUNITIES.validado.json (LLM cruzamento, ja conferido)
  VALIDACAO.json              (resumo do conferidor)
O casco nao muda, nao filtra, nao cruza: so embute para a tela ler.

TRAVA (contrato fixado pelo coordenador antes do teste):
  APROVA somente se  total > 0  E  fatos_ok == total  E  LIGACOES_QUEBRADAS == 0
    total    = VALIDACAO.json["fatos_in"]  (inteiro, obrigatorio)
    fatos_ok = VALIDACAO.json["fatos_ok"]  (inteiro, obrigatorio)
    e o numero de fatos presentes em FATOS.validado.json tem de ser == fatos_ok
    (o resumo do conferidor nao pode contradizer o arquivo que ele resume).
  Arquivo ausente, ilegivel, campo ausente ou de tipo errado = RECUSA (na duvida, recusa).
  RECUSA: linha "RECUSADA: ..." em stderr, exit 3, sem traceback,
          e NADA e escrito na saida (o .js anterior fica intacto, mesmo SHA256).
  APROVA: grava num temporario na mesma pasta e troca pelo definitivo (os.replace, atomico).
  O .js embute REMESSA_ID e VALIDACAO_SHA256: e isso que a tela mostra para dizer qual remessa esta no ar.
"""
import hashlib, json, os, sys, datetime, tempfile

EXIT_RECUSA = 3
NOMES = ["FATOS.validado.json", "SIGNALS.validado.json", "OPPORTUNITIES.validado.json", "VALIDACAO.json"]


class Recusa(Exception):
    pass


def _ler_json(pasta, nome):
    p = os.path.join(pasta, nome)
    if not os.path.isfile(p):
        raise Recusa(f"{nome} ausente")
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception as e:
        raise Recusa(f"{nome} ilegivel ({type(e).__name__})")


def _inteiro(v, campo):
    if campo not in v:
        raise Recusa(f"VALIDACAO.json sem o campo '{campo}'")
    x = v[campo]
    if isinstance(x, bool) or not isinstance(x, int):
        raise Recusa(f"VALIDACAO.json campo '{campo}' nao e inteiro: {x!r}")
    return x


def montar(pasta):
    if not os.path.isdir(pasta):
        raise Recusa(f"pasta da remessa nao existe: {pasta}")
    pac = {"PASTA": os.path.basename(os.path.normpath(pasta)), "SHA256": {}, "MTIME": {}}
    for n in NOMES + ["DOCUMENTOS.jsonl"]:
        p = os.path.join(pasta, n)
        if not os.path.isfile(p):
            raise Recusa(f"{n} ausente")
        pac["SHA256"][n] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        pac["MTIME"][n] = datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="minutes")
    v = _ler_json(pasta, "VALIDACAO.json")
    if not isinstance(v, dict):
        raise Recusa("VALIDACAO.json nao e um objeto")
    total = _inteiro(v, "fatos_in")
    ok = _inteiro(v, "fatos_ok")
    pac["FATOS"] = _ler_json(pasta, NOMES[0])
    pac["SIGNALS"] = _ler_json(pasta, NOMES[1])
    pac["OPPORTUNITIES"] = _ler_json(pasta, NOMES[2])
    pac["VALIDACAO"] = v
    docs = {}
    try:
        for linha in open(os.path.join(pasta, "DOCUMENTOS.jsonl"), encoding="utf-8"):
            if linha.strip():
                d = json.loads(linha)
                docs[d["DOCUMENT_ID"]] = d
        lista_fatos = [f["FACT_ID"] for d in pac["FATOS"]["documentos"] for f in d.get("fatos", [])]
        fatos = set(lista_fatos)
        sinais = {s["SIGNAL_ID"] for s in pac["SIGNALS"]["itens"]}
        q = 0
        for s in pac["SIGNALS"]["itens"] + pac["OPPORTUNITIES"]["itens"]:
            q += sum(1 for f in s.get("FACT_IDS_VALIDOS", []) if f not in fatos)
            q += sum(1 for x in s.get("SIGNAL_IDs", []) if x not in sinais)
        q += sum(1 for d in pac["FATOS"]["documentos"] if d["DOCUMENT_ID"] not in docs)
    except Exception as e:
        raise Recusa(f"estrutura da remessa ilegivel ({type(e).__name__}: {e})")
    pac["DOCUMENTOS"] = docs
    pac["LIGACOES_QUEBRADAS"] = q

    # ---- TRAVA: total > 0  E  fatos_ok == total  E  LIGACOES_QUEBRADAS == 0
    if total <= 0:
        raise Recusa(f"remessa vazia: total de fatos = {total} (precisa ser > 0)")
    if ok != total:
        raise Recusa(f"validacao reprovada: fatos_ok {ok} != total {total}")
    if len(lista_fatos) != ok:
        raise Recusa(f"VALIDACAO.json diz {ok} fatos conferidos, FATOS.validado.json tem {len(lista_fatos)}")
    if q != 0:
        raise Recusa(f"LIGACOES_QUEBRADAS = {q} (precisa ser 0)")

    pac["REMESSA_ID"] = pac["PASTA"]
    pac["VALIDACAO_SHA256"] = pac["SHA256"]["VALIDACAO.json"]
    pac["GERADO_EM"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    return pac, len(docs), len(fatos), len(sinais)


def gravar_atomico(saida, texto):
    fd, tmp = tempfile.mkstemp(prefix=".remessa-", suffix=".tmp", dir=os.path.dirname(os.path.abspath(saida)))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(texto)
        os.replace(tmp, saida)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def main():
    pasta = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/London1/sintonia-fluxo-unico/remessa-001"
    saida = os.path.join(os.path.dirname(__file__), "..", "..", "client", "sintonia-remessa.local.js")
    if len(sys.argv) > 2:
        saida = sys.argv[2]
    try:
        pac, nd, nf, ns = montar(pasta)
    except Recusa as e:
        print("RECUSADA:", e, "| nada foi escrito em", saida, file=sys.stderr)
        return EXIT_RECUSA
    corpo = json.dumps(pac, ensure_ascii=False).replace("</", "<\\/")
    gravar_atomico(saida, "window.SINTONIA_REMESSA=" + corpo + ";\n")
    print("OK", saida, "remessa", pac["REMESSA_ID"], "validacao_sha256", pac["VALIDACAO_SHA256"],
          "docs", nd, "fatos", nf, "sinais", ns,
          "oportunidades", len(pac["OPPORTUNITIES"]["itens"]), "ligacoes_quebradas", pac["LIGACOES_QUEBRADAS"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
