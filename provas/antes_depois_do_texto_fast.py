#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANTES / DEPOIS DA CAMADA DE TEXTO DO FAST (prova, nao conserta nada).

Roda as DUAS extracoes sobre os MESMOS HTML reais de uma rodada e mostra, documento por
documento, o que ia ao Opus antes e o que vai depois. Escreve `PROVA-ANTES-DEPOIS.md` e
`PROVA-ANTES-DEPOIS.json` na pasta onde for chamado.

    python3 provas/antes_depois_do_texto_fast.py <pasta-da-rodada> [limite]

A pasta tem de ter `DOCUMENTOS_FAST.json` e `raw_texto/` (a rodada entregue). O HTML original
vem do armazem, pelo `STORAGE_PATH` de cada documento.

ANTES = a regra que existia (todo o texto, so script/style/head fora) -- replicada aqui.
DEPOIS = a regra que passou a valer (casca por estrutura/token + linha curta repetida na rodada).
A prova imprime, por documento, quantos caracteres saem, e exige que o corpo nao tenha sido
engolido: qualquer documento cuja limpeza derrube abaixo de 15% e' listado como ALARME.
"""
import collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
FONTE = open(os.path.join(RAIZ, "motor", "fast_auto", "passo1_selecionar.py"), encoding="utf-8").read()
# so as definicoes, em dois pedacos que NAO tocam no banco:
#   (a) as constantes da camada de texto   (b) a tabela de casca + a classe T + as funcoes
CONSTANTES = FONTE[FONTE.index("LIMITE_ENTREGA_CHARS = int("):FONTE.index("env = dict(os.environ")]
TRECHO = FONTE[FONTE.index("TAGS_CASCA = {"):FONTE.index("os.makedirs(AQUI")]
NS = {"__name__": "passo1_definicoes", "re": re, "Counter": collections.Counter, "os": os,
      "hashlib": __import__("hashlib"), "HTMLParser": __import__("html.parser", fromlist=["HTMLParser"]).HTMLParser}
exec(CONSTANTES + "\n" + TRECHO, NS)
bruto, normaliza = NS["bruto"], NS["normaliza"]
linhas_de_template, tira_template = NS["linhas_de_template"], NS["tira_template"]
ARM = r"C:/Users/London1/sintonia-sala-italia/armazem/"


def antes(caminho, media_type):
    """A regra ANTIGA, replicada: tudo o que nao e' script/style/head, sem casca e sem repeticao."""
    b = open(caminho, "rb").read()
    if media_type == "application/pdf":
        import pypdf
        r = pypdf.PdfReader(caminho)
        return b, normaliza("\n".join((p.extract_text() or "") for p in r.pages))
    p = _Antigo()
    p.feed(b.decode("utf-8", "replace"))
    return b, normaliza("".join(p.o))


class _Antigo(__import__("html.parser", fromlist=["HTMLParser"]).HTMLParser):
    """A classe T como estava ANTES desta missao (motor/fast_auto/passo1_selecionar.py @ 6de307bd8)."""
    SKIP = {"script", "style", "noscript", "svg", "head", "template"}
    BLOCO = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "tr", "section", "article", "td", "header", "footer"}

    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.o = []
        s.d = 0

    def handle_starttag(s, t, a):
        if t in s.SKIP:
            s.d += 1
        elif t in s.BLOCO:
            s.o.append("\n")

    def handle_endtag(s, t):
        if t in s.SKIP and s.d:
            s.d -= 1
        elif t in s.BLOCO:
            s.o.append("\n")

    def handle_data(s, x):
        if not s.d:
            s.o.append(x)


def principal():
    pasta = sys.argv[1]
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    largura = 700
    D = json.load(open(os.path.join(pasta, "DOCUMENTOS_FAST.json"), encoding="utf-8"))
    antes_de, base_depois = {}, {}
    for d in D:
        d["_caminho"] = ARM + d["STORAGE_PATH"]
        b, t = antes(d["_caminho"], d["MEDIA_TYPE"])
        antes_de[d["DOCUMENT_ID"]] = t
        b2, t2, _ = bruto(d["_caminho"], d["MEDIA_TYPE"])      # (1) estrutura: casca fora
        base_depois[d["DOCUMENT_ID"]] = normaliza(t2)
    template = linhas_de_template(base_depois)                  # (2) template: linha curta repetida na rodada
    linhas, alarmes = [], []
    for d in D:
        t = antes_de[d["DOCUMENT_ID"]]
        limpo, n_lin, ch_lin = tira_template(base_depois[d["DOCUMENT_ID"]], template)
        marca = "LIMPO"
        prosa = sum(len(l) for l in limpo.split("\n") if len(l) >= 80)
        suspeito = len(t) > 2000 and len(limpo) < 0.15 * len(t) and prosa < 400
        if suspeito:                                  # a mesma guarda do passo1: nao corta o corpo em silencio
            marca, limpo = "LIMPEZA_SUSPEITA_MANTIDO_BRUTO", t
        base_depois[d["DOCUMENT_ID"]] = limpo
        pct = 100.0 * (len(t) - len(limpo)) / max(1, len(t))
        linhas.append(dict(DOC=d["DOCUMENT_ID"], FONTE=d["SOURCE_ID"], MARCA=marca,
                           ANTES_CHARS=len(t), DEPOIS_CHARS=len(limpo), REMOVIDO_CHARS=len(t) - len(limpo),
                           REMOVIDO_PCT=round(pct, 1), LINHAS_TEMPLATE=n_lin, TEMPLATE_CHARS=ch_lin,
                           ENTREGUE_INTEIRO=(len(limpo) <= limite) if limite else None))
        if suspeito:
            alarmes.append(d["DOCUMENT_ID"])
    tab = ["# O QUE IA AO OPUS ANTES E O QUE VAI DEPOIS", "",
           "Pasta da rodada: `%s`" % pasta, "",
           "| documento | fonte | marca | antes | depois | saiu | saiu % | linhas template |", "|---|---|---|---:|---:|---:|---:|---:|"]
    for l in linhas:
        tab.append("| %s | %s | %s | %d | %d | %d | %.1f%% | %d |" % (l["DOC"], l["FONTE"], l["MARCA"],
            l["ANTES_CHARS"], l["DEPOIS_CHARS"], l["REMOVIDO_CHARS"], l["REMOVIDO_PCT"], l["LINHAS_TEMPLATE"]))
    ta = sum(l["ANTES_CHARS"] for l in linhas); td = sum(l["DEPOIS_CHARS"] for l in linhas)
    tab += ["", "**TOTAL** antes=%d depois=%d saiu=%d (%.1f%%) · linhas de template da rodada=%d"
            % (ta, td, ta - td, 100.0 * (ta - td) / max(1, ta), len(template)),
            "", "ALARMES (limpeza derrubou abaixo de 15%%): %s" % (", ".join(alarmes) or "nenhum"),
            "", "## O que saiu, explicitamente (linhas de template da rodada)", ""]
    for l in sorted({x.strip() for x in template}):
        tab.append("- `%s`" % l[:100])
    tab += ["", "## Exemplos antes/depois (primeiros %d caracteres)" % largura, ""]
    for l in linhas:
        did = l["DOC"]
        tab += ["### %s · %s (%d -> %d)" % (did, l["FONTE"], l["ANTES_CHARS"], l["DEPOIS_CHARS"]), "",
                "ANTES:", "```", antes_de[did][:largura].replace("\n", " \\n "), "```", "",
                "DEPOIS:", "```", base_depois[did][:largura].replace("\n", " \\n "), "```", ""]
    os.makedirs(pasta, exist_ok=True)
    open("PROVA-ANTES-DEPOIS.md", "w", encoding="utf-8", newline="\n").write("\n".join(tab))
    json.dump(dict(PASTA=pasta, POR_DOC=linhas, TEMPLATE=sorted(template), ALARMES=alarmes,
                   TOTAL=dict(antes=ta, depois=td, removido=ta - td)),
              open("PROVA-ANTES-DEPOIS.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("TOTAL antes=%d depois=%d saiu=%d (%.1f%%) alarmes=%s"
          % (ta, td, ta - td, 100.0 * (ta - td) / max(1, ta), alarmes or "nenhum"))
    print("escrito: PROVA-ANTES-DEPOIS.md / PROVA-ANTES-DEPOIS.json")


if __name__ == "__main__":
    principal()
