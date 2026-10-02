# -*- coding: utf-8 -*-
# MEDICAO (nao conserta nada): quanto do texto que hoje vai ao Opus e menu/rodape/formulario/
# "veja tambem" / aviso de cookies. Duas extracoes sobre o MESMO HTML:
#   (A) exatamente a regra do motor/fast_auto/passo1_selecionar.py  -> t_corpo
#   (B) a mesma regra, descartando o texto que vem da casca          -> t_limpo
# (A) tem de bater caractere a caractere com o raw_texto da rodada, senao a medicao nao vale.
#
# A casca e reconhecida por TAG SEMANTICA (nav/header/footer/form/aside/button/select/label/input)
# e por TOKEN INTEIRO de class/id (nao por substring): classe de wrapper tipo
# "wp-singular post-template-default single ... navigation ..." contem "navigation" mas NAO e casca,
# e casar por substring engoliria a materia inteira. As regras de token estao em TOKENS_CASCA.
import collections, json, os, re, sys
from html.parser import HTMLParser

ARM = r"C:/Users/London1/sintonia-sala-italia/armazem/"
SKIP = {"script", "style", "noscript", "svg", "head", "template"}
BLOCOS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "tr", "section", "article", "td", "header", "footer"}
TAGS_CASCA = {"nav", "header", "footer", "form", "aside", "button", "select", "label", "input"}
TOKENS_CASCA = {"menu", "menu-item", "menu-label", "menulabel", "navbar", "navigation", "submenu", "megamenu",
                "breadcrumb", "breadcrumbs", "cookie", "cookiebanner", "cookie-banner", "cmplz-cookiebanner",
                "widget", "sidebar", "related", "correlati", "correlate", "leggi-anche", "leggianche",
                "newsletter", "subscribe", "abbonati", "abbonamento", "login", "login-form", "search-form",
                "searchform", "subscr", "consent", "gdpr", "sponsor", "sponsorizzato", "pagination",
                "paginazione", "social", "share", "tags", "tagcloud", "skip-link", "site-header", "site-footer",
                "main-menu", "primary-menu", "secondary-menu", "footer-widgets", "topbar", "toolbar"}
PREFIXOS_CASCA = ("menu-item-", "menu-", "td_block_wrap", "td_block", "td_module", "cmplz-")


class L(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.pilha = []
        s.corpo = []
        s.limpo = []
        s.skip = 0
        s.casca = collections.Counter()

    def _m(s, tag, attrs):
        if tag in TAGS_CASCA:
            return "<%s>" % tag
        a = dict(attrs)
        toks = []
        for chave in ("class", "id", "role", "aria-label"):
            toks += (a.get(chave) or "").split()
        for t in toks:
            tl = t.lower()
            if tl in TOKENS_CASCA or tl.startswith(PREFIXOS_CASCA):
                return t[:45]
        return None

    def motivo_atual(s):
        for t, m in reversed(s.pilha):
            if m:
                return m
        return None

    def handle_starttag(s, tag, attrs):
        if tag in SKIP:
            s.skip += 1
            return
        s.pilha.append((tag, s._m(tag, attrs)))
        if tag in BLOCOS:
            s.corpo.append("\n")
            s.limpo.append("\n")

    def handle_endtag(s, tag):
        if tag in SKIP:
            if s.skip:
                s.skip -= 1
            return
        for i in range(len(s.pilha) - 1, -1, -1):
            if s.pilha[i][0] == tag:
                del s.pilha[i:]
                break
        if tag in BLOCOS:
            s.corpo.append("\n")
            s.limpo.append("\n")

    def handle_data(s, x):
        if s.skip:
            return
        s.corpo.append(x)                      # regra A: identica ao passo1, sem excecao
        m = s.motivo_atual()
        if m is None:
            s.limpo.append(x)
        elif x.strip():
            s.casca[m] += len(re.sub(r"[ \t\u00a0]+", " ", x))


def norm(t):
    t = re.sub(r"[ \t\u00a0]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def analisar(caminho):
    p = L()
    p.feed(open(caminho, "rb").read().decode("utf-8", "replace"))
    return norm("".join(p.corpo)), norm("".join(p.limpo)), p.casca


def main():
    pasta = sys.argv[1]
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 18000
    D = json.load(open(os.path.join(pasta, "DOCUMENTOS_FAST.json"), encoding="utf-8"))
    linhas, tot = [], collections.Counter()
    todos, tampl = collections.Counter(), {}
    iguais = 0
    for d in D:
        p = ARM + d["STORAGE_PATH"]
        if d["MEDIA_TYPE"] != "text/html" or not os.path.exists(p):
            continue
        corpo, limpo, casca = analisar(p)
        extraido = open(os.path.join(pasta, "raw_texto", d["DOCUMENT_ID"] + ".txt"), encoding="utf-8").read()
        # o raw_texto foi escrito em modo texto no Windows (CRLF) e lido de volta com universal newlines;
        # comparar exigindo LF normalizado nos dois lados, senao a diferenca e so do fim de linha
        iguais += corpo.replace("\r\n", "\n") == extraido.replace("\r\n", "\n")
        tot["extraido"] += len(extraido); tot["limpo"] += len(limpo)
        tot["corta_fora"] += max(0, len(limpo) - lim)
        for l in extraido.split("\n"):
            n = re.sub(r"\s+", " ", l).strip().lower()
            if len(n) > 15:
                todos[n] += 1
        linhas.append(dict(DOC=d["DOCUMENT_ID"], FONTE=d["SOURCE_ID"], EXTRAIDO=len(extraido), LIMPO=len(limpo),
                           CASCA=len(extraido) - len(limpo),
                           PCT_CASCA=round(100.0 * (len(extraido) - len(limpo)) / max(1, len(extraido)), 1),
                           NAO_ENTREGUE=max(0, len(limpo) - lim)))
    tmpl = sum(len(n) for n, c in todos.items() if c >= 3)
    print("PASTA %s" % pasta)
    print("CONFERE_COM_O_RAW_ENTREGUE (A == raw_texto byte a byte): %d/%d documentos" % (iguais, len(linhas)))
    for l in linhas:
        print("  %-11s %-11s entregue_hoje=%6d  corpo_da_materia=%6d  casca=%6d (%4.1f%%)  cortado_fora=%6d"
              % (l["DOC"], l["FONTE"], l["EXTRAIDO"], l["LIMPO"], l["CASCA"], l["PCT_CASCA"], l["NAO_ENTREGUE"]))
    print("TOTAL docs=%d  entregue_hoje=%d  corpo_da_materia=%d  casca=%d (%.1f%%)  chars_que_o_modelo_nunca_viu=%d" % (
        len(linhas), tot["extraido"], tot["limpo"], tot["extraido"] - tot["limpo"],
        100.0 * (tot["extraido"] - tot["limpo"]) / max(1, tot["extraido"]), tot["corta_fora"]))
    print("LINHAS IDENTICAS EM >=3 DOCUMENTOS: %d chars = %.1f%% do texto entregue hoje"
          % (tmpl, 100.0 * tmpl / max(1, tot["extraido"])))
    for k, v in [(k, v) for k, v in todos.most_common(20) if v >= 3]:
        print("   x%-3d %s" % (v, k[:86]))
    json.dump(dict(CONFERE=iguais, POR_DOC=linhas, TOTAL=dict(tot), LINHAS_TEMPLATE=tmpl),
              open(os.path.join(pasta, "MEDICAO-TEXTO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
