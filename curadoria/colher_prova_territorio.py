#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COLHER PROVA DE TERRITÓRIO — as 3 páginas que o canal DECISOES-SEMANTICAS exige, e mais nada. (MICRO-PROVA, 26/09)

Não é rota de coleta: não escreve RAW, não toca a Sala, não enfileira. Lê, por candidata, no MÁXIMO 5 pedidos ao seu
domínio (teto D38): robots.txt · a entrada da ficha · (a página «chi siamo/about», se a entrada não disser quem é) ·
2 páginas do que o site publica. Tudo pelo leitor da casa (`canario.buscar`: UA, TLS, timeout, teto de 4 MB), com o
robots.txt lido e CUMPRIDO (`urllib.robotparser`), e o portão de egresso IT por consenso antes de cada candidata.

Escreve PROPOSTAS no formato do canal (`curadoria/decisao_semantica.py`): PROVAS com PAPEL/URL/SHA256/BYTES/LIDO_EM/
EGRESSO/BYTES_EM, e `TERRITORIO = "A_DECIDIR"` — o canal IGNORA uma entrada assim (não é T1..T12). A decisão é de
Opus/humano: preenche TERRITORIO, PAIS (da prova), DECIDIDO_POR, PORQUE. Só depois:

    py curadoria/colher_prova_territorio.py --lote=LOTE.json --bytes=<pasta fora do Git> --saida=PROPOSTAS.json
    py curadoria/colher_prova_territorio.py --aplicar=DECIDIDAS.json        # escreve no canal SÓ as que valem

`--aplicar` passa cada decisão pelo validador do próprio canal (`porque_invalida` contra a ficha) e, se a candidata
já tinha um «NAO SEI» (PROVA_INSUFICIENTE…), SUBSTITUI-O guardando-o em `ANTERIOR` — duas entradas para a mesma
candidata são um conflito que o QUALIFY recusa. Nunca escreve TERRITORIO sem DECIDIDO_POR.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "superficie"))
sys.path.insert(0, str(RAIZ / "candidatas"))

CANDIDATAS = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
DECISOES = RAIZ / "curadoria" / "DECISOES-SEMANTICAS-V1.json"
TETO_D38 = 5
A_DECIDIR = "A_DECIDIR"

_INSTITUCIONAL = re.compile(r"chi[-_ ]?siamo|about|presentazion|il[-_]dipartimento|l[-_]ente|istituzional|"
                            r"mission|statuto|organizzazione|who[-_]we[-_]are|contatti-e-sede", re.I)
_NAO_CONTEUDO = re.compile(r"(privacy|cookie|login|contatt|accessibil|note-legali|mappa|search|cerca|feed|"
                           r"wp-(admin|json|content)|\.(pdf|jpg|png|zip|css|js)(\?|$))", re.I)
# ⚠️ LOTE 1 (26/09, 69 pedidos reais): 7 das 9 «provas completas» tinham como CONTEUDO o favicon.ico (a pasta do tema
# chama-se `unipd_2017`: o ano casava), a ajuda do site (`2013-04-04-08-54-42/help.html`), «Assicurazione della
# Qualita», «Struttura e sedi», a taxa de publicacao de uma revista... O endereco so filtra o obvio; quem decide se e
# conteudo PUBLICADO e o juizo dos bytes (`juizo_de_conteudo`): pagina HTML, texto a serio e data de publicacao.
_ESTATICO = re.compile(r"\.(ico|svg|gif|webp|jpe?g|png|bmp|woff2?|ttf|eot|otf|xml|json|txt|csv|mp[34]|avi|mov|"
                       r"docx?|xlsx?|pptx?|odt|rar|7z|gz|tar)(\?|$)|/(themes?|assets|static|sites/all|wp-includes|"
                       r"templates|media/system|images?|img|fonts?|css|js)/", re.I)
_PAGINA_DE_SERVICO = re.compile(r"(?<![a-z])(help|aiuto|faq|segnalazion\w*|assicurazione-della-qualita|qualita|"
                                r"organi(-collegiali)?|struttura|sedi|storia|piano-strategico|trasparen\w*|bandi-di-gara|"
                                r"publishing-fee|fee|ethics?|guidelines?|author|istruzioni|didattica|corsi|iscrizion\w*|"
                                r"orari|newsletter|summer|winter|school|registra\w*|carrello|shop|abbona\w*|"
                                r"lavora-con-noi|credits|sitemap|dove-siamo|come-raggiungerci)(?![a-z])", re.I)
_ANO = re.compile(r"(?<![A-Za-z0-9_])(19|20)\d\d(?![0-9])")
_NOTICIA = re.compile(r"(?<![a-z])(notizi\w*|news|comunicat\w*|avvis\w*|bollettin\w*|articol\w*|eventi|evento|"
                      r"campagn\w*|informator\w*|circolar\w*)(?![a-z])", re.I)
_TITULO = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
LETRAS_CONTEUDO = 600          # texto visivel minimo de uma pagina de conteudo (menos que isto e casca ou formulario)
LETRAS_INSTITUCIONAL = 300     # a pagina que diz quem a organizacao E tem de dizer alguma coisa
_MESES = {m: i for i, m in enumerate(
    "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split(), 1)}
_MESES.update({m: i for i, m in enumerate(
    "january february march april may june july august september october november december".split(), 1)})
_D_NUM = re.compile(r"(?<!\d)(\d{1,2})[/.\-](\d{1,2})[/.\-]((?:19|20)\d\d)(?!\d)")
_D_ISO = re.compile(r"(?<!\d)((?:19|20)\d\d)[/\-](\d{1,2})[/\-](\d{1,2})(?!\d)")
_D_EXT = re.compile(r"(?<!\d)(\d{1,2})\s+(%s)\s+((?:19|20)\d\d)(?!\d)" % "|".join(_MESES), re.I)
_D_META = re.compile(r"""(?:article:published_time|datePublished|dc\.date|pubdate|"date")["']?\s*(?:content|:)\s*=?\s*["']"""
                     r"""((?:19|20)\d\d-\d\d-\d\d)""", re.I)
_D_TIME = re.compile(r"""<time[^>]*datetime\s*=\s*["']((?:19|20)\d\d-\d\d-\d\d)""", re.I)


def _texto_visivel(html: str) -> str:
    s = re.sub(r"(?is)<(script|style|noscript|svg|nav|header|footer|aside|form|iframe)[^>]*>.*?</\1>", " ", html)
    m = re.search(r"(?is)<(article|main)[^>]*>(.*?)</\1>", s)
    s = m.group(2) if m else s
    s = re.sub(r"<[^>]+>", " ", s)
    import html as _h
    return re.sub(r"\s+", " ", _h.unescape(s)).strip()


def _e_pagina_html(b: bytes) -> bool:
    """Texto HTML, nao ficheiro: sem NUL, nao comeca por %PDF, poucos caracteres ilegiveis e com marcacao."""
    if not b or b"\x00" in b[:2048] or b.lstrip()[:5] == b"%PDF-":
        return False
    s = b.decode("utf-8", "replace")
    return s.count("�") <= len(s) // 20 and bool(re.search(r"(?i)<(html|body|p|div)\b", s))


def _letras_de_pagina(b: bytes) -> int:
    """Letras visiveis de uma PAGINA; um PDF ou binario tem 0 (o LOTE 2B contou 288 265 «letras» de um PDF)."""
    return len(_texto_visivel(b.decode("utf-8", "replace"))) if _e_pagina_html(b) else 0


def _datas(*textos) -> list:
    out = []
    for t in textos:
        for d, m, a in _D_NUM.findall(t):
            out.append((int(a), int(m), int(d)))
        for a, m, d in _D_ISO.findall(t):
            out.append((int(a), int(m), int(d)))
        for d, m, a in _D_EXT.findall(t):
            out.append((int(a), _MESES[m.lower()], int(d)))
    return out


def juizo_de_conteudo(b: bytes, url: str, hoje: str | None = None) -> dict:
    """Esta pagina e CONTEUDO PUBLICADO? -> {SERVE, LETRAS, DATA_PUBLICADA, PORQUE}. So bytes, sem rede.

    Serve: HTML, >= LETRAS_CONTEUDO letras de texto visivel (sem menu/cabecalho/rodape) e UMA data de publicacao —
    nos metadados, num <time>, no endereco, no titulo ou no inicio do texto. A data de HOJE nao conta: e o aviso do
    dia no topo do site (LaMMA: «Codice Allerta meteo Sabato 26 Settembre 2026» em todas as paginas)."""
    hoje = hoje or datetime.now(timezone.utc).date().isoformat()
    if not b or b"\x00" in b[:2048] or b.lstrip()[:5] == b"%PDF-":   # ico/png/jpeg trazem NUL; o PDF pode nao trazer
        return {"SERVE": False, "LETRAS": 0, "DATA_PUBLICADA": None, "PORQUE": "nao e texto (bytes de ficheiro binario)"}
    s = b.decode("utf-8", "replace")
    if s.count("�") > len(s) // 20 or not re.search(r"(?i)<(html|body|p|div)\b", s):
        return {"SERVE": False, "LETRAS": 0, "DATA_PUBLICADA": None, "PORQUE": "nao e pagina HTML"}
    texto = _texto_visivel(s)
    t = _TITULO.search(s)
    titulo = t.group(1) if t else ""
    datas = []
    for a, m, d in _datas(url, titulo, texto[:600]) + [tuple(map(int, x.split("-"))) for x in
                                                       _D_META.findall(s) + _D_TIME.findall(s)]:
        if 1990 <= a and 1 <= m <= 12 and 1 <= d <= 31:
            iso = "%04d-%02d-%02d" % (a, m, d)
            if iso < hoje:                      # hoje e o aviso do dia; o futuro e agenda, nao publicacao
                datas.append(iso)
    if len(texto) < LETRAS_CONTEUDO:
        return {"SERVE": False, "LETRAS": len(texto), "DATA_PUBLICADA": max(datas) if datas else None,
                "PORQUE": "texto curto (%d letras < %d): casca, formulario ou lista vazia" % (len(texto), LETRAS_CONTEUDO)}
    if not datas:
        return {"SERVE": False, "LETRAS": len(texto), "DATA_PUBLICADA": None,
                "PORQUE": "sem data de publicacao (so a de hoje, ou nenhuma): pagina fixa, nao publicacao"}
    return {"SERVE": True, "LETRAS": len(texto), "DATA_PUBLICADA": max(datas), "PORQUE": "conteudo publicado"}


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mesmo_site(u: str, base: str) -> bool:
    a, b = urlparse(u).netloc.lower().removeprefix("www."), urlparse(base).netloc.lower().removeprefix("www.")
    return a == b


def _links(html: bytes, base: str) -> list[str]:
    s = html.decode("utf-8", "replace")
    vistos, out = set(), []
    for h in re.findall(r'href\s*=\s*["\']([^"\'#]+)', s, re.I):
        u = urljoin(base, h.strip())
        if u.startswith(("http://", "https://")) and _mesmo_site(u, base) and u not in vistos:
            vistos.add(u)
            out.append(u)
    return out


def _parece_conteudo(u: str, base: str) -> bool:
    p = urlparse(u).path
    if (_NAO_CONTEUDO.search(u) or _ESTATICO.search(u) or _PAGINA_DE_SERVICO.search(p)
            or _INSTITUCIONAL.search(p) or p.rstrip("/") in ("", urlparse(base).path.rstrip("/"))):
        return False
    ultimo = [x for x in p.split("/") if x][-1:] or [""]
    return bool(_ANO.search(p) or ultimo[0].count("-") >= 3)


def _prioridade(u: str) -> int:
    """Primeiro o que tem cara de publicacao datada: com o teto D38 so ha 2 ou 3 tiros por site."""
    p = urlparse(u).path
    return -(2 * bool(_ANO.search(p)) + bool(_NOTICIA.search(p)))


def colher(ficha: dict, buscar, portao, pasta: Path, dormir=time.sleep, pausa: float = 3.0,
           hoje: str | None = None) -> dict:
    """Uma candidata. `buscar(url)->(status, bytes, erro)` e `portao()->dict` injectados (testável sem rede)."""
    cid, url = ficha["CANDIDATA_ID"], ficha["URL"]
    out = {"CANDIDATA_ID": cid, "NOME": ficha.get("NOME"), "URL": url, "TERRITORIO": A_DECIDIR,
           "PROVAS": [], "PEDIDOS": 0, "TITULOS": [], "REJEITADAS": []}
    g = portao()
    out["EGRESS_GATE"] = g.get("EGRESS_GATE")
    if g.get("EGRESS_GATE") != "PASS":
        out["PORQUE_PAROU"] = "portao de egresso sem PASS IT — 0 pedidos"
        return out

    def pedir(u):
        if out["PEDIDOS"] >= TETO_D38:
            return 0, b"", "teto D38"
        if out["PEDIDOS"]:
            dormir(pausa)
        out["PEDIDOS"] += 1
        return buscar(u)

    p = urlparse(url)
    st, txt, err = pedir("%s://%s/robots.txt" % (p.scheme or "https", p.netloc))
    rp = urllib.robotparser.RobotFileParser()
    if st == 200:
        rp.parse(txt.decode("utf-8", "replace").splitlines())
        out["ROBOTS"] = "LIDO"
    elif st == 404:
        rp.parse([])
        out["ROBOTS"] = "404 (nao publica: tudo permitido)"
    else:
        out["ROBOTS"] = "ILEGIVEL (%s) — nao se pede mais nada" % (err or st)
        out["PORQUE_PAROU"] = "robots.txt ilegivel: UNKNOWN nao e licenca"
        return out

    def guardar(papel, u, st, b, juizo=None):
        sha = hashlib.sha256(b).hexdigest()
        n = len(out["PROVAS"]) + len(out["REJEITADAS"])
        dest = pasta / cid / ("%d_%s.bin" % (n, papel))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b)
        linha = {"PAPEL": papel, "URL": u, "SHA256": sha, "BYTES": len(b), "HTTP": st,
                 "LIDO_EM": _agora(), "EGRESSO": "IT", "BYTES_EM": str(dest)}
        if juizo is not None:
            linha["JUIZO"] = juizo
        if papel == "REJEITADA":                   # guardada para auditoria; NUNCA conta como prova
            out["REJEITADAS"].append(linha)
            return
        t = _TITULO.search(b.decode("utf-8", "replace"))
        out["TITULOS"].append((t.group(1).strip()[:120] if t else ""))
        out["PROVAS"].append(linha)

    if not rp.can_fetch("*", url):
        out["PORQUE_PAROU"] = "robots.txt proibe a entrada da ficha"
        return out
    st, entrada, err = pedir(url)
    if st != 200 or not entrada:
        out["PORQUE_PAROU"] = "entrada nao abriu: %s" % (err or st)
        return out
    links = [u for u in _links(entrada, url) if rp.can_fetch("*", u)]
    # LOTE 2B: «presentazion» casava num PDF (PRESENTAZIONE-DATI-2025.pdf) e o STATUTO em PDF — a institucional
    # tem de ser uma PAGINA que se le; ficheiros nao.
    inst = next((u for u in links if _INSTITUCIONAL.search(urlparse(u).path)
                 and not _ESTATICO.search(u) and not _NAO_CONTEUDO.search(u)), None)
    if inst:
        st2, b2, err2 = pedir(inst)                           # a pagina que diz quem a organizacao E
        if st2 == 200 and b2:
            guardar("INSTITUCIONAL", inst, st2, b2)
    else:
        guardar("INSTITUCIONAL", url, st, entrada)             # a propria entrada diz quem e (casa do site)
    conteudos = sorted((u for u in links if _parece_conteudo(u, url)), key=_prioridade)
    shas_vistas = {x["SHA256"] for x in out["PROVAS"]}
    for u in conteudos:
        if sum(1 for x in out["PROVAS"] if x["PAPEL"] == "CONTEUDO") >= 2 or out["PEDIDOS"] >= TETO_D38:
            break
        st3, b3, err3 = pedir(u)
        if st3 == 200 and b3 and hashlib.sha256(b3).hexdigest() not in shas_vistas:
            j = juizo_de_conteudo(b3, u, hoje)
            guardar("CONTEUDO" if j["SERVE"] else "REJEITADA", u, st3, b3, j)
            shas_vistas.add(hashlib.sha256(b3).hexdigest())
    n_cont = sum(1 for x in out["PROVAS"] if x["PAPEL"] == "CONTEUDO")
    inst_prova = next((x for x in out["PROVAS"] if x["PAPEL"] == "INSTITUCIONAL"), None)
    letras_inst = _letras_de_pagina(Path(inst_prova["BYTES_EM"]).read_bytes()) if inst_prova else 0
    if inst_prova:
        inst_prova["LETRAS"] = letras_inst
    inst_ok = bool(inst_prova) and letras_inst >= LETRAS_INSTITUCIONAL
    out["PROVA_COMPLETA"] = bool(inst_ok and n_cont >= 2)
    if not out["PROVA_COMPLETA"]:
        motivos = []
        if not inst_prova:
            motivos.append("sem pagina institucional")
        elif not inst_ok:
            motivos.append("institucional quase vazia (%d letras < %d)" % (letras_inst, LETRAS_INSTITUCIONAL))
        if n_cont < 2:
            motivos.append("%d conteudo publicado de 2" % n_cont)
        for r in out["REJEITADAS"]:
            motivos.append("rejeitada %s: %s" % (urlparse(r["URL"]).path[-50:], r["JUIZO"]["PORQUE"]))
        if not conteudos:
            motivos.append("a entrada nao linka nenhuma pagina com cara de publicacao")
        out["PORQUE_PAROU"] = "prova incompleta: " + "; ".join(motivos)
    try:
        import atribuir_source_id as ASI                        # a regra da casa, so como SUGESTAO
        t, porque = ASI.territorio_de({"NOME": "%s %s" % (ficha.get("NOME") or "", " ".join(out["TITULOS"][:1])),
                                       "URL": url})
        out["SUGESTAO_DA_REGRA"] = {"TERRITORIO": t, "PORQUE": porque}
    except Exception as ex:  # noqa: BLE001
        out["SUGESTAO_DA_REGRA"] = {"TERRITORIO": "NAO SEI", "PORQUE": "regra indisponivel: %s" % ex}
    return out


RE_ID_NAO_REGISTADA = re.compile(r"^L[0-9A-Z]+-\d{2,3}$")


def fichas_do_lote(lote: dict, candidatas: list[dict]) -> dict:
    """{id: ficha} do lote, pela ordem. `CANDIDATAS` = CAND-ids da porta; `FICHAS_NOVAS` = pistas AINDA NAO
    registadas ({ID provisorio «L2B-01», NOME, URL}) — so se registam pela porta as que a prova aprovar (passo 9),
    para nao encher a fila com sites que nao publicam nada. Uma «nova» que ja esta na porta e erro: usa o CAND-id."""
    por_id = {c["CANDIDATA_ID"]: c for c in candidatas}
    import fonte_nova as FN
    por_url = {FN.normalizar(c["URL"]): c["CANDIDATA_ID"] for c in candidatas}
    out = {}
    for cid in lote.get("CANDIDATAS", []):
        if cid not in por_id:
            raise SystemExit("lote: %s nao existe na porta" % cid)
        out[cid] = por_id[cid]
    for f in lote.get("FICHAS_NOVAS", []):
        if not RE_ID_NAO_REGISTADA.match(f.get("ID", "")):
            raise SystemExit("lote: id provisorio invalido %r (ex.: L2B-01)" % f.get("ID"))
        ja = por_url.get(FN.normalizar(f["URL"]))
        if ja:
            raise SystemExit("lote: %s ja esta na porta como %s — usar o CAND-id" % (f["URL"], ja))
        if f["ID"] in out:
            raise SystemExit("lote: id repetido %s" % f["ID"])
        out[f["ID"]] = {"CANDIDATA_ID": f["ID"], "NOME": f["NOME"], "URL": f["URL"], "NAO_REGISTADA": True}
    return out


def aplicar(decididas: list[dict], caminho: Path = DECISOES, fichas: dict | None = None) -> dict:
    import decisao_semantica as DS
    fichas = fichas if fichas is not None else {c["CANDIDATA_ID"]: c for c in
                                                json.loads(CANDIDATAS.read_text(encoding="utf-8"))["CANDIDATAS"]}
    doc = json.loads(caminho.read_text(encoding="utf-8"))
    por_cand = {}
    for i, d in enumerate(doc["DECISOES"]):
        por_cand.setdefault(d.get("CANDIDATA_ID"), []).append(i)
    entram, ficam = [], []
    for d in decididas:
        cid = d.get("CANDIDATA_ID")
        motivo = None
        if d.get("TERRITORIO") in (A_DECIDIR, None, ""):
            motivo = "ainda A_DECIDIR"
        elif cid not in fichas:
            motivo = "candidata desconhecida na porta"
        else:
            motivo = DS.porque_invalida(d, fichas[cid])
        if motivo:
            ficam.append({"CANDIDATA_ID": cid, "PORQUE": motivo})
            continue
        velhas = [doc["DECISOES"][i] for i in por_cand.get(cid, [])]
        if any(v.get("TERRITORIO") not in ("NAO SEI", None) for v in velhas):
            ficam.append({"CANDIDATA_ID": cid, "PORQUE": "ja tem territorio decidido — nao se sobrescreve"})
            continue
        nova = {k: v for k, v in d.items() if k not in ("TITULOS", "PEDIDOS", "EGRESS_GATE", "ROBOTS",
                                                        "PROVA_COMPLETA", "PORQUE_PAROU")}
        if not nova.get("DECIDIDO_EM"):
            nova["DECIDIDO_EM"] = _agora()
        if velhas:
            nova["ANTERIOR"] = velhas
        entram.append(nova)
    if entram:
        sai = {e["CANDIDATA_ID"] for e in entram}
        doc["DECISOES"] = [d for d in doc["DECISOES"] if d.get("CANDIDATA_ID") not in sai] + entram
        doc["TOTAL"] = len(doc["DECISOES"])
        doc["DECIDIDAS"] = sum(1 for d in doc["DECISOES"] if d.get("TERRITORIO") != "NAO SEI")
        doc["NAO_SEI"] = doc["TOTAL"] - doc["DECIDIDAS"]
        tmp = caminho.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        tmp.replace(caminho)
    return {"ENTRAM": [e["CANDIDATA_ID"] for e in entram], "FICAM": ficam}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    if a.get("aplicar"):
        r = aplicar(json.loads(Path(a["aplicar"]).read_text(encoding="utf-8"))["PROPOSTAS"])
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    if not a.get("lote") or not a.get("bytes"):
        print(__doc__)
        return 2
    import canario as CAN      # noqa: E402
    import rede                # noqa: E402
    lote = json.loads(Path(a["lote"]).read_text(encoding="utf-8"))
    porta = (Path(a["vivo"]) / CANDIDATAS.relative_to(RAIZ)) if a.get("vivo") else CANDIDATAS   # a porta DO VIVO
    fichas = fichas_do_lote(lote, json.loads(porta.read_text(encoding="utf-8"))["CANDIDATAS"])
    props = [colher(f, CAN.buscar, lambda: rede.portao_de_egresso("IT"), Path(a["bytes"])) for f in fichas.values()]
    out = {"DATASET": "PROPOSTAS-DE-TERRITORIO", "GERADO_EM": _agora(), "PEDIDOS": sum(p["PEDIDOS"] for p in props),
           "PROVA_COMPLETA": sum(1 for p in props if p.get("PROVA_COMPLETA")), "PROPOSTAS": props}
    Path(a.get("saida", "PROPOSTAS-DE-TERRITORIO.json")).write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("PEDIDOS", "PROVA_COMPLETA")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
