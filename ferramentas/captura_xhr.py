#!/usr/bin/env python3
"""CAPTURA_XHR — o navegador ACHA o endereco do JSON que uma pagina de JavaScript carrega; a coleta pede-o por HTTP.

    py ferramentas/captura_xhr.py --url=<pagina> --source-id=IT-Tn-nnn --livros=<pasta das ondas> \
                                  [--recibos=<pasta>] --saida=<pasta> [--porta=9335] [--segundos=20] [--teto=5]

SCRAP-EVOLUCAO-V1 (26/09, peca F do ESTUDO-SCRAPLING-UNIAO). Uma pagina que monta a lista por JavaScript
devolve ao curl um esqueleto sem itens (EMPTY_LIST garantido: IT-T7-164 pecorinoromano.com; o indice de
IT-T3-008 agrometeopuglia.it). Mas o JavaScript vai buscar os itens a ALGUM endereco — quase sempre um JSON.
Esta ferramenta abre a pagina UMA vez no Chrome (ferramentas/cdp.py, dominio Network), anota as respostas
XHR/fetch com cara de JSON e devolve uma PROPOSTA de contrato `STATIC_ENDPOINT` com esse endereco. A partir
dai a coleta e HTTP normal, com os bytes do servidor — o RAW continua honesto (nao e o DOM desenhado).

O TETO MANDA NO NAVEGADOR TAMBEM. Um navegador pede dezenas de coisas por pagina. Aqui cada pedido passa
pelo dominio Fetch do Chrome ANTES de sair (`Fetch.requestPaused`) e o `Porteiro` decide:
  · imagem, fonte, folha de estilo, media e o favicon (o Chrome pede-o sozinho): nunca saem;
  · o resto conta no orcamento do dominio (a regra da prova-teto, D38/D41) e, esgotado, e recusado
    (`Fetch.failRequest`, BlockedByClient) — o pedido nao sai da maquina.
O robots.txt lido antes conta 1 no mesmo orcamento, e CADA pedido do navegador pede licenca ao robots
do seu host (D91): origem nova = o robots dela e lido (1 pedido no teto dela) antes de o pedido sair. O recibo (RECIBO-CAPTURA-XHR.json) leva
PEDIDOS_POR_DOMINIO + GERADO_EM, e as rodadas leem-no para a janela de 24 h (D79).

O QUE NAO FAZ: nao faz login, nao le nem escreve cookie (perfil novo e vazio a cada corrida), nao resolve
CAPTCHA, nao pede POST (so GET vira proposta), nao escreve contrato — a proposta e para o dono/coordenador
confirmar com 1 pedido HTTP. Rota na proveniencia: COL-LAW-704.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import select
import sys
import time
from urllib.parse import urlsplit

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, "provas"))
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import cdp                       # noqa: E402
import prova_teto_dominio as PT  # noqa: E402

TIPOS_QUE_NUNCA_SAEM = frozenset({"Image", "Font", "Stylesheet", "Media"})


def parece_json(mime: str, url: str) -> bool:
    m = (mime or "").lower()
    return "json" in m or urlsplit(url).path.lower().endswith(".json")


class Porteiro:
    """Decide cada pedido do navegador ANTES de sair. `gastos` ja traz o que se gastou (o robots).

    D91 (26/09 22:32): o robots.txt e OBRIGATORIO em cada pagina comum. Com `robots` (url -> (ok, motivo)),
    CADA pedido do navegador — a pagina, os scripts, o JSON — pede licenca ao robots do seu host. A primeira
    vez que aparece uma origem nova, ler o robots dela e um pedido e conta no teto do dominio dela; sem teto
    para o ler, o pedido nao sai. `robots_lidos` traz as origens cujo robots ja foi lido (a da pagina)."""

    def __init__(self, teto: int = 5, gastos: dict | None = None, dominio_de=PT.orcamento_de,
                 robots=None, robots_lidos=()):
        self.teto, self.dominio_de, self.robots = teto, dominio_de, robots
        self.gastos = dict(gastos or {})
        self.robots_lidos = set(robots_lidos)
        self.recusados = []

    def _recusar(self, url, tipo, porque):
        self.recusados.append((url, tipo, porque))
        return False, porque

    def decidir(self, url: str, tipo: str) -> tuple[bool, str]:
        if not url.startswith(("http://", "https://")):
            return True, "nao e rede (data:/blob:)"
        if tipo in TIPOS_QUE_NUNCA_SAEM or urlsplit(url).path.endswith("/favicon.ico"):
            self.recusados.append((url, tipo, "tipo que nao serve para achar o JSON"))
            return False, "tipo %s nunca sai" % tipo
        p = urlsplit(url)
        d = self.dominio_de(p.hostname or "")
        if self.robots is not None:
            origem = "%s://%s" % (p.scheme, p.netloc)
            if origem not in self.robots_lidos:
                if self.gastos.get(d, 0) >= self.teto:
                    return self._recusar(url, tipo, "teto do dominio %s antes de ler o robots de %s" % (d, origem))
                self.gastos[d] = self.gastos.get(d, 0) + 1          # ler o robots desta origem e um pedido
                self.robots_lidos.add(origem)
            ok, motivo = self.robots(url)
            if not ok:
                return self._recusar(url, tipo, "ROBOTS: %s" % motivo)
        if self.gastos.get(d, 0) >= self.teto:
            self.recusados.append((url, tipo, "teto %d do dominio %s" % (self.teto, d)))
            return False, "teto do dominio %s" % d
        self.gastos[d] = self.gastos.get(d, 0) + 1
        return True, "dentro do teto (%d/%d em %s)" % (self.gastos[d], self.teto, d)


def candidatos(eventos: list) -> list:
    """Dos eventos do dominio Network, as respostas XHR/fetch com cara de JSON, pela ordem em que chegaram."""
    metodo, fim, out = {}, {}, []
    for e in eventos:
        p = e.get("params") or {}
        if e.get("method") == "Network.requestWillBeSent":
            metodo[p.get("requestId")] = (p.get("request") or {}).get("method")
        elif e.get("method") == "Network.loadingFinished":
            fim[p.get("requestId")] = p.get("encodedDataLength")
    for e in eventos:
        if e.get("method") != "Network.responseReceived":
            continue
        p = e["params"]
        r = p.get("response") or {}
        if not parece_json(r.get("mimeType"), r.get("url", "")):
            continue                      # um JSON pedido pelo documento (<script src=x.json>) tambem serve
        out.append({"REQUEST_ID": p.get("requestId"), "URL": r.get("url"), "HTTP": r.get("status"),
                    "MIME": r.get("mimeType"), "TIPO": p.get("type"), "METODO": metodo.get(p.get("requestId")),
                    "TERMINOU": p.get("requestId") in fim, "BYTES_NA_REDE": fim.get(p.get("requestId"))})
    return out


def proposta(source_id: str, pagina: str, c: dict, corpo: bytes | None) -> dict:
    """A proposta de contrato para o dono confirmar. So GET com HTTP 200 vira proposta."""
    base = {"SOURCE_ID": source_id, "PAGINA": pagina, "ENDERECO": c["URL"], "HTTP": c["HTTP"], "MIME": c["MIME"],
            "METODO": c["METODO"]}
    if c.get("METODO") != "GET" or c.get("HTTP") != 200:
        return {**base, "ESTADO": "NAO_SERVE", "PORQUE": "so GET com 200 vira STATIC_ENDPOINT (metodo %s, HTTP %s)"
                % (c.get("METODO"), c.get("HTTP"))}
    return {**base, "ESTADO": "PROPOSTA",
            "ACQUISITION": {"STRATEGY": "STATIC_ENDPOINT", "URL": c["URL"]},
            "AMOSTRA_SHA256": hashlib.sha256(corpo).hexdigest() if corpo is not None else None,
            "AMOSTRA_BYTES": len(corpo) if corpo is not None else None,
            "DESCOBERTO_POR": "captura_xhr (Chrome, dominio Network) — COL-LAW-704; os bytes da coleta virao do "
                              "servidor por HTTP, nao do navegador",
            "FALTA": "o dono/coordenador confirma com 1 pedido HTTP a este endereco (sem navegador) e escreve "
                     "IDENTITY/OUTPUT_TYPE do contrato"}


# ── a conversa com o Chrome ───────────────────────────────────────────────────────────────────
def _mandar(aba, metodo, **params) -> int:
    aba._n += 1
    cdp._enviar(aba._s, json.dumps({"id": aba._n, "method": metodo, "params": params}))
    return aba._n


def _um(aba, espera: float):
    """Uma mensagem, ou None se nada chegou em `espera` segundos (o socket fica bloqueante: o quadro le-se inteiro)."""
    pronto, _, _ = select.select([aba._s], [], [], espera)
    return json.loads(cdp._receber(aba._s)) if pronto else None


def capturar(aba, url: str, porteiro: Porteiro, *, segundos: float = 20.0, relogio=time.monotonic) -> dict:
    """Navega com o porteiro a decidir cada pedido; ouve `segundos`; depois le os corpos dos JSON."""
    eventos, respostas, decisoes = [], {}, []

    def tratar(m):
        if "id" in m:
            respostas[m["id"]] = m
            return
        eventos.append(m)
        if m.get("method") == "Fetch.requestPaused":
            p = m["params"]
            ok, porque = porteiro.decidir(p["request"]["url"], p.get("resourceType", ""))
            decisoes.append({"URL": p["request"]["url"], "TIPO": p.get("resourceType"), "SAIU": ok, "PORQUE": porque})
            if ok:
                _mandar(aba, "Fetch.continueRequest", requestId=p["requestId"])
            else:
                _mandar(aba, "Fetch.failRequest", requestId=p["requestId"], errorReason="BlockedByClient")

    def esperar(i, ate):
        while i not in respostas and relogio() < ate:
            m = _um(aba, 0.5)
            if m:
                tratar(m)
        return respostas.get(i)

    t0 = relogio()
    for metodo, params in (("Network.enable", {}), ("Fetch.enable", {"patterns": [{"urlPattern": "*"}]}),
                           ("Page.enable", {})):
        esperar(_mandar(aba, metodo, **params), t0 + 10)
    _mandar(aba, "Page.navigate", url=url)
    while relogio() < t0 + segundos:
        m = _um(aba, 0.5)
        if m:
            tratar(m)
    cands = candidatos(eventos)
    corpos = {}
    for c in cands:
        if not c["TERMINOU"]:
            continue
        r = esperar(_mandar(aba, "Network.getResponseBody", requestId=c["REQUEST_ID"]), relogio() + 10)
        res = (r or {}).get("result")
        if res is not None:
            b = res.get("body", "")
            corpos[c["REQUEST_ID"]] = base64.b64decode(b) if res.get("base64Encoded") else b.encode("utf-8")
    esperar(_mandar(aba, "Fetch.disable"), relogio() + 5)
    return {"CANDIDATOS": cands, "CORPOS": corpos, "DECISOES": decisoes}


# ── a corrida do coordenador: portao inteiro, UMA pagina ─────────────────────────────────────
def correr(url, source_id, *, livros, recibos, saida, porta=9335, segundos=20.0, teto=5,
           egresso=None, janela=None, robots=None, abrir_aba=None) -> dict:
    import rota_navegador as RN                                          # noqa: PLC0415
    from datetime import datetime, timezone                             # noqa: PLC0415
    os.makedirs(saida, exist_ok=True)
    host = urlsplit(url).hostname or ""
    dom = PT.orcamento_de(host)
    out = {"URL": url, "SOURCE_ID": source_id, "PEDIDOS_POR_DOMINIO": {dom: 0}, "ROTA_HTTP": "NAVEGADOR_CDP",
           "ROTA_HTTP_DESCRICAO": "Chrome com perfil novo via DevTools (captura_xhr) — COL-LAW-704"}

    def fim(porque=None):
        out["PAROU"] = porque
        out["GERADO_EM"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with open(os.path.join(saida, "RECIBO-CAPTURA-XHR.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        return out
    g = (egresso or RN._egresso_do_dono)()
    out["EGRESSO"] = {"PAIS": g.get("EGRESS_COUNTRY_CODE"), "VOTOS": g.get("VOTOS")}
    if g.get("EGRESS_COUNTRY_CODE") != "IT":
        return fim("EGRESSO_NAO_IT: nada saiu")
    fecha = (janela or RN._janela_24h)(host, livros, recibos)
    if fecha:
        return fim("JANELA_24H: o dominio foi pedido ha menos de 24 h (abre %s)" % fecha)
    ok, motivo = (robots or RN._robots_vivo)(url)
    out["ROBOTS"] = motivo
    out["PEDIDOS_POR_DOMINIO"][dom] = 1
    if not ok:
        return fim("ROBOTS: %s" % motivo)
    p = urlsplit(url)
    porteiro = Porteiro(teto=teto, gastos={dom: 1}, robots=robots or RN._robots_vivo,
                        robots_lidos={"%s://%s" % (p.scheme, p.netloc)})
    aba, fechar = (abrir_aba or _abrir_aba)(porta)
    try:
        r = capturar(aba, url, porteiro, segundos=segundos)
    finally:
        fechar()
    out["PEDIDOS_POR_DOMINIO"] = porteiro.gastos
    out["RECUSADOS_PELO_PORTEIRO"] = len(porteiro.recusados)
    out["DECISOES"] = r["DECISOES"]
    props = []
    for i, c in enumerate(r["CANDIDATOS"]):
        corpo = r["CORPOS"].get(c["REQUEST_ID"])
        if corpo is not None:
            with open(os.path.join(saida, "AMOSTRA-%02d.json.bin" % i), "wb") as f:
                f.write(corpo)
        props.append(proposta(source_id, url, c, corpo))
    out["PROPOSTAS"] = props
    return fim(None if any(p["ESTADO"] == "PROPOSTA" for p in props) else "NENHUM_JSON: a pagina nao pediu JSON "
               "dentro do teto (ver DECISOES e RECUSADOS) — NAO SEI se o conteudo vem por outro caminho")


def _abrir_aba(porta):
    """Chrome COM JANELA (a ADAMA mediu headless=403), perfil NOVO e vazio: sem cookie de ninguem."""
    import subprocess                                                    # noqa: PLC0415
    import tempfile                                                      # noqa: PLC0415
    import navegador                                                     # noqa: PLC0415
    perfil = tempfile.mkdtemp(prefix="captura-xhr-")
    achado = navegador.descobrir()
    if not achado["FOUND"]:
        raise cdp.Erro("sem Chrome nesta maquina: %s" % achado.get("WHY"))
    p = subprocess.Popen([achado["EXECUTABLE"]] + navegador.argumentos("about:blank", perfil=perfil,
                                                                        porta_devtools=porta),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    fim = time.time() + 25
    while True:
        try:
            aba = cdp.Aba(cdp._aba_de_pagina(porta)["webSocketDebuggerUrl"])
            break
        except cdp.Erro:
            if time.time() > fim:
                p.kill()
                raise
            time.sleep(1)

    def fechar():
        aba.fechar()
        p.kill()
    return aba, fechar


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    if not all(k in a for k in ("url", "source-id", "livros", "saida")):
        print(__doc__)
        return 2
    r = correr(a["url"], a["source-id"], livros=a["livros"], recibos=a.get("recibos"), saida=a["saida"],
               porta=int(a.get("porta", 9335)), segundos=float(a.get("segundos", 20)), teto=int(a.get("teto", 5)))
    print(json.dumps({k: v for k, v in r.items() if k != "DECISOES"}, ensure_ascii=False, indent=1))
    return 0 if not r.get("PAROU") else 1


if __name__ == "__main__":
    raise SystemExit(main())
