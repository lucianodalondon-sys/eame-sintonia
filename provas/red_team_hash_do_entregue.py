#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM DO HASH DO TEXTO ENTREGUE (custo zero).

O defeito antigo: o sha256 gravado descrevia o texto TODO no disco, mas o modelo so recebia o
corte de 18000 chars -- nada provava o que o modelo viu.

Esta prova roda o passo2 a serio sobre uma rodada de ensaio com o corte em 800 chars, com um STUB
de modelo (nenhuma chamada de rede, nenhum custo) que:
  - devolve um TRECHO tirado DO PROPRIO PROMPT  -> tem de ser ACEITO (estava no que o modelo viu);
  - devolve um TRECHO que vive SO' DEPOIS do corte -> tem de ser REJEITADO.
Depois confere no FACTS_FAST.json que:
  - TEXTO_ENTREGUE_SHA256 == sha256(texto_do_ficheiro[:800]) e != sha256(texto_todo);
  - TEXTO_ENTREGUE_CHARS == 800 e TEXTO_CORTADO_EM == 800;
  - CONFERE_COM_DOCUMENTOS == True (o ficheiro lido e' o que o passo1 hasheou).

Uso:  python3 provas/red_team_hash_do_entregue.py <rodada-de-ensaio-com-corte-800> <doc-para-trecho-fora-do-corte>
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
PASSO2 = os.path.join(RAIZ, "motor", "fast_auto", "passo2_fatos.py")
CORTE = int(os.environ.get("CORTE_DA_PROVA", "800"))


def stub_claude(prompt):
    """Finge o modelo: nao le rede nem ficheiro. So' o que veio no prompt."""
    m = re.search(r"<<<\n(.*)\n>>>", prompt, re.S)
    texto = m.group(1) if m else ""
    return {"FATOS": [{"TIPO": "PRAGA_DOENCA",
                       "O_QUE": {"VALOR": "teste de encanamento", "TRECHO": texto[40:100]},
                       "ONDE": {"VALOR": "NAO_SEI", "TRECHO": ""},
                       "QUANDO": {"VALOR": "NAO_SEI", "TRECHO": ""},
                       "CULTURA": {"VALOR": "NAO_SEI", "TRECHO": ""},
                       "PRAGA_DOENCA": {"VALOR": "NAO_SEI", "TRECHO": ""},
                       "PRODUTO_OU_EMPRESA": {"VALOR": "fora do corte", "TRECHO": os.environ["STUB_TRECHO"]},
                       "NUMERO": {"VALOR": "NAO_SEI", "TRECHO": ""}}]}, {"total_cost_usd": 0.0, "modelUsage": {"stub": {}}}


def main():
    pasta, doc_fora = sys.argv[1], sys.argv[2]
    # o texto que vive SO' DEPOIS do corte daquele documento (vem do ficheiro, nao do prompt)
    inteiro = open(os.path.join(pasta, "raw_texto", doc_fora + ".txt"), encoding="utf-8").read()
    assert len(inteiro) > CORTE + 200, "documento curto demais para a prova: %d chars" % len(inteiro)
    os.environ["STUB_TRECHO"] = inteiro[-80:].strip()
    fonte = open(PASSO2, encoding="utf-8").read()
    # troca SO' a funcao que fala com o modelo; todo o resto do passo2 e' o codigo a serio
    fonte = (fonte[:fonte.index("def chamar(prompt):")] +
             "def chamar(prompt):\n    return STUB_CHAMAR(prompt)\n\n\n" +
             fonte[fonte.index("def extrair(d):"):])
    ns = {"__name__": "__main__", "__file__": PASSO2, "__builtins__": __builtins__,
          "STUB_CHAMAR": stub_claude}
    sys.argv = [PASSO2, pasta]

    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(fonte, PASSO2, "exec"), ns)

    F = json.load(open(os.path.join(pasta, "FACTS_FAST.json"), encoding="utf-8"))
    problemas, checados = [], 0
    for d in F["DOCUMENTOS"]:
        if d["ESTADO"] != "PROCESSADO":
            continue
        did = d["DOCUMENT_ID"]
        t = open(os.path.join(pasta, "raw_texto", did + ".txt"), "rb").read().decode("utf-8")
        esperado = hashlib.sha256(t[:CORTE].encode("utf-8")).hexdigest()
        checados += 1
        if d["TEXTO_ENTREGUE_SHA256"] != esperado:
            problemas.append("%s: sha do entregue != sha do corte" % did)
        if d["TEXTO_ENTREGUE_CHARS"] != min(len(t), CORTE):
            problemas.append("%s: chars entregues %s" % (did, d["TEXTO_ENTREGUE_CHARS"]))
        if len(t) > CORTE and d["TEXTO_CORTADO_EM"] != CORTE:
            problemas.append("%s: corte nao registado" % did)
        if not d["CONFERE_COM_DOCUMENTOS"]:
            problemas.append("%s: ficheiro lido != ficheiro hasheado pelo passo1" % did)
    # o trecho que so' existe depois do corte tem de estar REJEITADO no documento testado
    fato = [f for f in F["FATOS"] if f["DOCUMENT_ID"] == doc_fora][0]
    ver_fora = fato["PRODUTO_OU_EMPRESA"]["VERIFICACAO"]
    ver_dentro = fato["O_QUE"]["VERIFICACAO"]
    if ver_fora != "REJEITADO_TRECHO_NAO_EXISTE_NO_RAW":
        problemas.append("trecho de fora do corte foi ACEITO em %s (%s)" % (doc_fora, ver_fora))
    if ver_dentro != "TRECHO_ENCONTRADO_NO_RAW":
        problemas.append("trecho que o modelo viu foi REJEITADO em %s (%s)" % (doc_fora, ver_dentro))
    print("documentos conferidos: %d" % checados)
    print("corte da prova: %d chars · documento do teste: %s (%d chars no ficheiro)" % (CORTE, doc_fora, len(inteiro)))
    print("trecho de DENTRO do corte -> %s" % ver_dentro)
    print("trecho de FORA do corte -> %s" % ver_fora)
    print("PROBLEMAS: %s" % ("nenhum" if not problemas else problemas))
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
