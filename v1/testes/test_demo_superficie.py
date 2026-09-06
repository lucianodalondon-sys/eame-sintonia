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
    b.close()
print()
if FALHAS:
    for onde, o in FALHAS: print(f"  FALHA  {onde}: {o}")
    print(f"\n  {len(FALHAS)} falha(s) -> DEMO_SURFACE_TEST = FAIL")
    sys.exit(1)
print("  0 falhas -> DEMO_SURFACE_TEST = PASS")
