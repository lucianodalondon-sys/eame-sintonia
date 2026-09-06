#!/usr/bin/env python3
"""
test_demo_superficie.py — o que a DEMO pode mostrar.

A build de demonstracao retira deliberadamente a camada cultura x alvo x dose,
que a terceira rodada adversarial ainda julga. Este teste prova que ela saiu de
verdade: varre as nove telas e falha se qualquer CELULA de tabela ou valor de
lista de definicao exibir dose, selo de juncao, ou um dos pares conhecidos.

A distincao entre CELULA e PROSA e proposital: a tela pode explicar "o rotulo
escreve alla dose di 1-3 l/ha" sem que isso seja uma afirmacao sobre um produto.
Claim mora em <td> e <dd>; explicacao mora em .lei e .meta.
"""
from playwright.sync_api import sync_playwright
import glob, os, re, sys
exe=(glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome')+['/opt/pw-browsers/chromium'])[0]
import os
U="file://" + os.path.abspath("v1/casco/label-intelligence.html")
# padroes de CLAIM, nao de prosa: a palavra "listadas" em portugues nao e o selo LISTADA
import re as _re
PROIBIDO=[("dose g/ha", _re.compile(r'\d[\d.,\-— ]*\s*(g|kg|l|ml)\s*/\s*ha', _re.I)),
          ("selo EXATA", _re.compile(r'\bEXATA\b')),
          ("selo LISTADA", _re.compile(r'\bLISTADA\b')),
          ("selo AMBIGUA", _re.compile(r'\bAMBIGUA\b')),
          ("par TABACCO x CIMICI", _re.compile(r'TABACCO\s*[x×]\s*CIMICI', _re.I)),
          ("par SOIA x NOTTUE", _re.compile(r'SOIA\s*[x×]\s*NOTTUE', _re.I)),
          ("tabela de usos autorizados", _re.compile(r'Usos autorizados(?! e dose)'))]
FALHAS = []
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=exe,args=["--no-sandbox"]); pg=b.new_page(viewport={"width":1500,"height":1200})
    errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(1800)
    print("ERROS JS:", errs)
    navs=[a.get_attribute("data-v") for a in pg.query_selector_all("nav a")]
    print("NAV:", navs)
    for v in navs:
        pg.click(f"nav a[data-v='{v}']"); pg.wait_for_timeout(800)
        # Um CLAIM mora em celula de tabela ou valor de lista de definicao.
        # Prosa explicativa (.lei/.meta) pode citar "alla dose di 1-3 l/ha" como
        # exemplo de como o rotulo escreve — isso e explicacao, nao afirmacao.
        celulas = " \n".join(e.inner_text() for e in pg.query_selector_all(f"#v-{v} td, #v-{v} dd"))
        t=pg.inner_text(f"#v-{v}")
        achou=[n for n,rx in PROIBIDO if rx.search(celulas)]
        print(f"  {v:<9} {len(t):>7} chars | claim proibido: {achou if achou else 'nenhum'}")
        if achou: FALHAS.extend((v, a) for a in achou)
    # produto 360 num produto com muitos usos
    pg.click("nav a[data-v='produto']"); pg.wait_for_timeout(400)
    pg.select_option("#psel","008259"); pg.wait_for_timeout(900)
    t=pg.inner_text("#pdet")
    celulas = " \n".join(e.inner_text() for e in pg.query_selector_all("#pdet td, #pdet dd"))
    achou=[n for n,rx in PROIBIDO if rx.search(celulas)]
    print("  produto 008259 | claim proibido:", achou if achou else "nenhum")
    if achou: FALHAS.extend(('produto/008259', a) for a in achou)
    print("  retencao explicada:", "retidos nesta demonstracao" in t)
    if "PILOT / SHADOW TOOL" not in pg.inner_text("header"):
        FALHAS.append(("header", "a demo nao se declara PILOT / SHADOW TOOL"))
    if errs: FALHAS.extend(("js", e) for e in errs)
    print("  PILOT/SHADOW no cabecalho: True" if not any(f[0]=="header" for f in FALHAS) else "  PILOT/SHADOW AUSENTE")

    # ---------------------------------------------------------------- CENSO
    # A primeira versao deste teste olhava as nove telas e UMA ficha, e por isso
    # deu PASS numa build em que o valor retido estava impresso em 13 cards de
    # ficha e 6 gavetas de evidencia. Superficie nao visitada nao e superficie
    # limpa. Agora ele visita as 166 fichas e as gavetas dos 210 objetos.
    sup = {}
    for v in navs:
        pg.click(f"nav a[data-v=\'{v}\']"); pg.wait_for_timeout(250)
        sup["tela:" + v] = pg.inner_text("#v-" + v)
    pg.click("nav a[data-v=\'produto\']"); pg.wait_for_timeout(250)
    regs = pg.eval_on_selector_all("#psel option", "o=>o.map(x=>x.value)")
    for reg in regs:
        pg.select_option("#psel", reg); pg.wait_for_timeout(20)
        sup["ficha:" + reg] = pg.inner_text("#pdet")
    nobj = pg.evaluate("window.__PAYLOAD__.objects.length")
    for i in range(nobj):
        pg.evaluate(f"evIdx({i})"); pg.wait_for_timeout(3)
        sup["gaveta:%d" % i] = pg.inner_text("#dr")
    pg.evaluate("document.getElementById(\'dr\').classList.remove(\'open\')")
    print(f"  censo: {len(sup)} superficies ({len(navs)} telas, {len(regs)} fichas, {nobj} gavetas)")

    # Cada linha aqui e um claim que o PRE-DEMO GATE reprovou e que foi retirado.
    # O teste falha se qualquer um voltar, em qualquer superficie.
    CENSO = [
        ("valor de dose retido 280-600",                r"280\s*-\s*600"),
        ("valor de dose retido 560-1000",               r"560\s*-\s*1000"),
        ("cultura retida Cavolo cappuccio",             r"cavolo cappuccio"),
        ("alvo retido Cimici",                          r"\bcimici\b"),
        ("cultura retida Tabacco",                      r"\btabacco\b"),
        ("posse afirmada de valor que nao foi lido",    r"existem e estao no dossie"),
        ("leitor de uso nomeado no lugar do de dose",   r"nenhuma tabela de uso localizada"),
        ("recusa afirmada sobre zero pares",            r"recusando a publica-la[\s\S]{0,200}?sao 0 pares"),
        ("nao-tentativa afirmada sobre o extrator PHI", r"nunca rodou"),
        ("zero de PHI reapresentado como decisao",      r"=\s*0\s*por decisao"),
    ]
    for nome, pat in CENSO:
        rx = re.compile(pat, re.I)
        onde = [k for k, txt in sup.items() if rx.search(txt)]
        if onde:
            FALHAS.append(("censo", f"{nome}: voltou em {len(onde)} superficie(s), ex. {onde[:3]}"))
    print("  claim retirado que voltou:",
          "nenhum" if not any(f[0] == "censo" for f in FALHAS) else "HA")

    # O estado do leitor de DOSE nunca aparece sozinho: nu, ele le como
    # "este rotulo nao tem uso", que e PARSER_FAILURE lido como ausencia.
    nus = 0
    for k, txt in sup.items():
        for m in re.finditer(r"NO_USE_TABLE_FOUND|TABLE_FOUND_NO_ROWS", txt):
            if "leitor de" not in txt[m.end():m.end() + 80]:
                nus += 1
    if nus:
        FALHAS.append(("censo", f"{nus} ocorrencia(s) do estado do leitor de dose sem glosa"))
    print(f"  estado do leitor de dose sem glosa: {nus}")

    # "adjudicacao em curso" so onde o payload marca NEEDS_REVIEW.
    esp = pg.evaluate("window.__PAYLOAD__.products.filter(p=>p.states&&p.states.NEEDS_REVIEW).length")
    ach = sum(t.count("adjudicacao em curso") for k, t in sup.items() if k.startswith("ficha:"))
    if ach != esp:
        FALHAS.append(("censo", f"adjudicacao em curso em {ach} fichas; o payload marca {esp}"))
    print(f"  'adjudicacao em curso': {ach} ficha(s) · payload marca {esp}")

    # A busca nao pode responder sobre a camada retirada por nenhuma porta —
    # nem pelo nome da cultura, nem pelo valor da dose.
    pg.click("nav a[data-v=\'search\']"); pg.wait_for_timeout(200)
    def _busca(q):
        pg.fill("#sq", q); pg.wait_for_timeout(140)
        t = pg.inner_text("#sres")
        a = re.search(r"produtos \((\d+)\)", t, re.I); c = re.search(r"eventos \((\d+)\)", t, re.I)
        return (int(a.group(1)) if a else -1, int(c.group(1)) if c else -1)
    for q in ["TABACCO", "CIMICI", "VITE", "Cavolo", "280-600", "300", "560-1000", "l/ha"]:
        r = _busca(q)
        if r != (0, 0):
            FALHAS.append(("busca", f"\"{q}\" devolve {r[0]} produto(s) e {r[1]} evento(s)"))
    viva = _busca("GOLTIX")
    if viva[0] == 0:
        FALHAS.append(("busca", "a busca por produto parou de funcionar"))
    print(f"  busca: camada retirada muda · GOLTIX devolve {viva[0]} produto(s) e {viva[1]} evento(s)")

    # A gaveta tem de abrir o objeto DA LINHA. Os identificadores nao sao unicos
    # (7 colisoes), e resolver por identificador abria a prova de outra linha.
    pg.click("nav a[data-v=\'review\']"); pg.wait_for_timeout(300)
    div = tot = 0
    for tr in pg.query_selector_all("#v-review table tr"):
        btn = tr.query_selector("button.ev")
        if not btn or "evidencia" not in (btn.inner_text() or ""):
            continue
        tds = tr.query_selector_all("td")
        onde = tds[-2].inner_text() if len(tds) >= 2 else ""
        if "pagina" not in onde.lower():
            continue
        btn.click(); pg.wait_for_timeout(50)
        m = re.search(r"LOCAL DA EVIDENCIA\s*\n(.+)", pg.inner_text("#dr"), re.I)
        gav = m.group(1) if m else ""
        pg.evaluate("document.getElementById(\'dr\').classList.remove(\'open\')")
        a = re.search(r"pagina\s*(\d+)", onde, re.I); c = re.search(r"pagina\s*(\d+)", gav, re.I)
        tot += 1
        if not (a and c and a.group(1) == c.group(1)):
            div += 1
    if div:
        FALHAS.append(("evidencia", f"{div} de {tot} linhas abrem a gaveta de outro objeto"))
    print(f"  evidencia: {tot - div}/{tot} linha(s) abrem a propria prova")
    if errs: FALHAS.extend(("js", e) for e in errs if ("js", e) not in FALHAS)
    print(f"  erros de JS no censo inteiro: {len(errs)}")
    b.close()
print()
if FALHAS:
    for onde, o in FALHAS: print(f"  FALHA  {onde}: {o}")
    print(f"\n  {len(FALHAS)} falha(s) -> DEMO_SURFACE_TEST = FAIL")
    sys.exit(1)
print("  0 falhas -> DEMO_SURFACE_TEST = PASS")
