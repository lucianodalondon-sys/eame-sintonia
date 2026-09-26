#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENSAIO A SECO do LOTE 1 da MICRO-PROVA — o circuito inteiro, sem rede real. CORRER SÓ NUMA CÓPIA DO VIVO.

    py <copia>/curadoria/ensaio_micro_prova_lote1.py --saida=<json>

A cópia é uma árvore descartável (checkout + os livros sujos do vivo copiados). Tudo o que este ensaio escreve,
escreve NA CÓPIA (fila, ledger, alocação, contratos, DECISOES, tabela do coletor). Rede: um servidor HTTP REAL em
127.0.0.1 faz de conta que é os 20 sites; `urllib.request.urlopen` (o ÚNICO ponto por onde o Curator pede páginas:
canario, capturador, gate_de_rota, reparar_contrato) é redirigido para ele — o pedido é HTTP de verdade, o destino é
local, e `geturl()` devolve o endereço ORIGINAL (senão o reparo gravaria 127.0.0.1 no contrato).

Passos, pelas peças da casa:
  1  colher_prova_territorio.colher    3 páginas por candidata (portão SIMULADO = PASS; teto D38)
  2  decisão de ENSAIO                 TERRITORIO do desenho do site; DECIDIDO_POR diz ENSAIO — não é decisão
  3  colher_prova_territorio.aplicar   entra no canal pelo validador do próprio canal
  4  fila.recuperar_bloqueadas_por_defeito(["territorio indeterminado pelo nome"], {"QUALIFY"})
  5  worker.executar_uma               QUALIFY -> BUILD_CONTRACT -> VALIDATE_ROUTE -> CANARY (-> REPAIR) -> READY
  6  collection_gate.avaliar           o portão
  7  canario_rotas_elegiveis.provar    a rota do lado do coletor (ROUTE_PROVEN) -> ROTAS-ELEGIVEIS-V1.json
  8  onboardar_rotas_provadas          a linha na tabela do coletor
«Entraria na coorte» = portão ELIGIBLE + linha no coletor (as duas condições de que a coorte cresce; a coorte
congelada em si é feita por coorte_unica sobre o plano da onda, que este ensaio não corre).

Desenho dos sites (é uma ESCOLHA do ensaio, não uma previsão): 17 bons; 3 falham de propósito, um em cada ponto
— Fitogest (robots proíbe tudo), Laimburg (casca JS: os mesmos bytes em todo o lado, como medido a 23/09), Laore
(notícias curtas: o canário recusa). Na 1.ª corrida a «notícia curta» tinha 4 parágrafos de ~380 caracteres
(~1 500 no total, acima do mínimo de 800) e PASSOU — defeito do desenho, não do robô; agora tem 1 parágrafo de ~190.
"""
from __future__ import annotations

import http.server
import json
import sys
import threading
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
for p in ("curadoria", "superficie", "medidas"):
    sys.path.insert(0, str(RAIZ / p))

import colher_prova_territorio as CP   # noqa: E402

LOTE = json.loads((RAIZ / "curadoria" / "MICRO-PROVA-LOTE1.json").read_text(encoding="utf-8"))["CANDIDATAS"]
CLASSE_DO_ENSAIO = {
    "CAND-1173": "T3", "CAND-1069": "T3", "CAND-1070": "T3", "CAND-1164": "T3", "CAND-1167": "T3",
    "CAND-1049": "T5", "CAND-0953": "T2", "CAND-1032": "T5", "CAND-1018": "T5", "CAND-1019": "T5",
    "CAND-1021": "T5", "CAND-1055": "T5", "CAND-1029": "T5", "CAND-0026": "T5", "CAND-0647": "T5",
    "CAND-1045": "T5", "CAND-1043": "T5", "CAND-0018": "T12", "CAND-0015": "T12", "CAND-0003": "T4"}
FALHA = {"CAND-0003": "ROBOTS_PROIBE", "CAND-0026": "CASCA_JS", "CAND-0015": "NOTICIAS_CURTAS"}
FRASE = ("La campagna in corso richiede attenzione alle condizioni meteorologiche e allo stato fitosanitario "
         "delle colture; i tecnici raccomandano monitoraggi settimanali in campo e interventi mirati. ")


def _site(ficha: dict) -> dict:
    """{caminho: (status, bytes)} de um site de faz-de-conta para a candidata."""
    cid, url, nome = ficha["CANDIDATA_ID"], ficha["URL"], ficha.get("NOME") or ficha["CANDIDATA_ID"]
    entrada = urlparse(url).path or "/"
    falha = FALHA.get(cid)
    if falha == "CASCA_JS":
        casca = b"<html><head><title>app</title></head><body><div id=app></div><script src=/app.js></script></body></html>"
        return {"*": (200, casca), "/robots.txt": (200, b"User-agent: *\nAllow: /\n")}
    corpo = FRASE * (1 if falha == "NOTICIAS_CURTAS" else 14)
    itens = ["/notizie/2026/%s-aggiornamento-tecnico-numero-%d-per-le-aziende" % (cid.lower(), i) for i in range(6)]
    casa = ("<html><head><title>%s</title></head><body><header><a href='/chi-siamo'>Chi siamo</a> "
            "<a href='/contatti'>Contatti</a> <a href='/privacy'>Privacy</a></header><main><h1>%s</h1><ul>%s</ul>"
            "</main></body></html>" % (nome, nome, "".join("<li><a href='%s'>Notizia %d</a></li>" % (u, i)
                                                          for i, u in enumerate(itens))))
    pag = {entrada: (200, casa.encode()), "/": (200, casa.encode()),
           "/robots.txt": (200, b"User-agent: *\nDisallow: /\n" if falha == "ROBOTS_PROIBE"
                           else b"User-agent: *\nDisallow: /riservato/\n"),
           "/chi-siamo": (200, ("<html><head><title>Chi siamo - %s</title></head><body><main><h1>Chi siamo</h1>"
                                "<p>%s e un ente italiano che opera nel settore agricolo.</p></main></body></html>"
                                % (nome, nome)).encode())}
    for i, u in enumerate(itens):
        dia = "2026-09-%02d" % (10 + i)
        pag[u] = (200, ("<html><head><title>Notizia %d - %s</title>"
                        "<meta property='article:published_time' content='%sT09:00:00+02:00'></head><body>"
                        "<a href='/'>Home</a><article><h1>Aggiornamento tecnico numero %d</h1><time datetime='%s'>%s</time>"
                        "%s</article></body></html>" % (i, nome, dia, i, dia, dia,
                                                        "".join("<p>%s</p>" % corpo for _ in range(1 if falha == "NOTICIAS_CURTAS" else 4)))).encode())
    return pag


def _servidor(sites: dict):
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            partes = self.path.lstrip("/").split("/", 1)
            host = partes[0].lower().removeprefix("www.")
            caminho = "/" + (partes[1] if len(partes) > 1 else "")
            caminho = caminho.split("?", 1)[0]
            s = sites.get(host, {})
            st, b = s.get(caminho) or s.get(caminho.rstrip("/")) or s.get("*") or (404, b"nao existe")
            self.send_response(st)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _redirigir(porto: int):
    original = urllib.request.urlopen
    pedidos = []

    class Resp:
        def __init__(self, r, url):
            self._r, self._url = r, url
            self.status, self.headers = r.status, r.headers

        def read(self, *a):
            return self._r.read(*a)

        def geturl(self):
            return self._url

        def getcode(self):
            return self.status

        def info(self):
            return self.headers

        def __enter__(self):
            return self

        def __exit__(self, *a):
            self._r.close()
            return False

    def urlopen(req, *a, **kw):
        url = req.full_url if isinstance(req, urllib.request.Request) else req
        p = urlparse(url)
        local = "http://127.0.0.1:%d/%s%s%s" % (porto, p.netloc, p.path or "/", ("?" + p.query) if p.query else "")
        hdrs = dict(req.header_items()) if isinstance(req, urllib.request.Request) else {}
        pedidos.append(url)
        kw.pop("context", None)
        return Resp(original(urllib.request.Request(local, headers=hdrs), *a, **kw), url)

    urllib.request.urlopen = urlopen
    return pedidos


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    fichas = {c["CANDIDATA_ID"]: c for c in json.loads(CP.CANDIDATAS.read_text(encoding="utf-8"))["CANDIDATAS"]}
    sites = {urlparse(fichas[c]["URL"]).netloc.lower().removeprefix("www."): _site(fichas[c]) for c in LOTE}
    srv = _servidor(sites)
    pedidos = _redirigir(srv.server_address[1])
    import fila as F                      # noqa: E402 — depois do redirecionamento
    import lifecycle as LC                # noqa: E402
    import worker as W                    # noqa: E402
    import collection_gate as G           # noqa: E402
    import canario_rotas_elegiveis as CRE  # noqa: E402
    import onboardar_rotas_provadas as ONB  # noqa: E402
    import sha_do_contrato as SHA         # noqa: E402

    bytes_dir = Path(a.get("bytes", str(RAIZ / "ENSAIO-BYTES")))
    rel = {c: {"CANDIDATA_ID": c, "NOME": fichas[c].get("NOME"), "DESENHO": FALHA.get(c, "BOM")} for c in LOTE}
    # 1 · prova
    props = []
    for c in LOTE:
        r = CP.colher(fichas[c], __import__("canario").buscar, lambda: {"EGRESS_GATE": "PASS"}, bytes_dir,
                      dormir=lambda s: None)
        rel[c].update({"PROVA_COMPLETA": bool(r.get("PROVA_COMPLETA")), "PEDIDOS_DA_PROVA": r["PEDIDOS"],
                       "PROVA_PAROU": r.get("PORQUE_PAROU")})
        props.append(r)
    # 2 · decisao de ENSAIO (so para as de prova completa)
    decididas = [dict(r, TERRITORIO=CLASSE_DO_ENSAIO[r["CANDIDATA_ID"]], PAIS="IT",
                      DECIDIDO_POR="ENSAIO — nao e decisao (dry-run MICRO-PROVA-LOTE1)",
                      PORQUE="classe do desenho do site de ensaio", PAIS_PROVA="site de ensaio (.it)")
                 for r in props if r.get("PROVA_COMPLETA")]
    ap = CP.aplicar(decididas)
    for c in ap["ENTRAM"]:
        rel[c]["DECISAO_NO_CANAL"] = CLASSE_DO_ENSAIO[c]
    # 4 · reabrir as QUALIFY (a porta da fila)
    reab = F.recuperar_bloqueadas_por_defeito(["territorio indeterminado pelo nome"], {F.QUALIFY})
    # 5 · o worker, so sobre o lote (as outras QUALIFY reabertas voltam a bloquear sozinhas; nao interessam)
    def nossos():
        alloc = json.loads((RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json").read_text(encoding="utf-8"))
        m = {x["SOURCE_ID"]: x.get("CANDIDATE_ID") for x in alloc.get("NOVAS", []) if x.get("CANDIDATE_ID") in LOTE}
        return set(LOTE) | set(m), m
    agora = datetime.now(timezone.utc)
    passos = []
    for _ in range(400):
        ids, _m = nossos()
        el = [t for t in F.elegiveis(agora) if t["SOURCE_ID"] in ids]
        if not el:
            agora += timedelta(hours=1)          # deixa vencer RETRY/esperas, sem dormir
            if not [t for t in F.elegiveis(agora + timedelta(days=2)) if t["SOURCE_ID"] in ids]:
                break
            continue
        t = el[0]
        r = W.executar_uma(t, W._contratos())
        passos.append({k: r.get(k) for k in ("SOURCE_ID", "TASK_TYPE", "RESULTADO", "PORQUE")})
    ids, sid_de = nossos()
    cand_para_sid = {v: k for k, v in sid_de.items()}
    # 6-8 · portao, canario do coletor, onboarding
    contratos = W._contratos()
    linhas = []
    for c in LOTE:
        sid = cand_para_sid.get(c)
        rel[c]["SOURCE_ID"] = sid
        if not sid:
            rel[c]["ESTADO"] = "SEM_SOURCE_ID (QUALIFY nao passou)"
            continue
        rel[c]["ESTADO"] = LC.estado_de(sid)
        rel[c]["PORTAO"] = (G.avaliar(sid) or {}).get("MOTIVO")
        if sid in contratos:
            l = CRE.provar(sid, contratos[sid])
            l.update({"CONTRATO_SHA256": SHA.do_contrato(contratos[sid]),
                      "PROVADO_EM": datetime.now(timezone.utc).isoformat()})
            linhas.append(l)
            rel[c]["ROTA_DO_COLETOR"] = l.get("VEREDITO")
    CRE.SAIDA.write_text(json.dumps({"DATASET": "ROTAS-ELEGIVEIS-V1", "GERADO_EM": datetime.now(timezone.utc).isoformat(),
                                     "LINHAS": linhas}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    plano = ONB.planear()
    nossos_sids = {v.get("SOURCE_ID") for v in rel.values()}
    entra = [e for e in plano["ENTRA"] if e.get("SOURCE_ID") in nossos_sids]
    ONB.aplicar(entra)
    no_coletor = ONB.ids_com_contrato_no_coletor()
    for c, v in rel.items():
        sid = v.get("SOURCE_ID")
        v["NO_COLETOR"] = bool(sid and sid in no_coletor)
        v["ENTRARIA_NA_COORTE"] = bool(v["NO_COLETOR"] and v.get("PORTAO") == "ELIGIBLE")
        v["FICA_PORQUE"] = next((f["PORQUE"] for f in plano["FICA"] if f["SOURCE_ID"] == sid), None)
        v["FIM"] = "PRONTA" if v["ENTRARIA_NA_COORTE"] else "NAO"
    srv.shutdown()
    from collections import Counter
    out = {"DATASET": "ENSAIO-MICRO-PROVA-LOTE1", "REDE_REAL": 0, "PEDIDOS_AO_SERVIDOR_LOCAL": len(pedidos),
           "HOSTS_PEDIDOS": sorted({urlparse(u).netloc for u in pedidos}),
           "APLICAR": ap, "QUALIFY_REABERTAS": len(reab), "PASSOS_DO_WORKER": len(passos),
           "POR_FIM": dict(Counter(v["FIM"] for v in rel.values())),
           "POR_DESENHO_E_FIM": dict(Counter("%s -> %s" % (v["DESENHO"], v["FIM"]) for v in rel.values())),
           "CANDIDATAS": list(rel.values()), "PASSOS": passos}
    Path(a.get("saida", str(RAIZ / "ENSAIO-MICRO-PROVA-LOTE1.json"))).write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("REDE_REAL", "PEDIDOS_AO_SERVIDOR_LOCAL", "QUALIFY_REABERTAS",
                                          "PASSOS_DO_WORKER", "POR_FIM", "POR_DESENHO_E_FIM")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
