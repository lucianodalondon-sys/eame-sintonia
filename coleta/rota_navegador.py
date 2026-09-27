# -*- coding: utf-8 -*-
"""A ROTA HTTP COM CARA DE NAVEGADOR — uma PECA dos leitores da casa, nao um coletor. Biblioteca padrao.

    cabecalhos(rota, do_leitor=)  -> os cabecalhos da rota (DECLARADA: os do leitor; NAVEGADOR: regras/ROTA-NAVEGADOR.json)
    rota_da_fonte(contrato)       -> a rota que o contrato pede (ACQUISITION.ROTA_HTTP; omissao DECLARADA)
    proveniencia(rota)            -> o que a prova/RAW leva para dizer por onde veio (COL-LAW-704)
    py coleta/rota_navegador.py --medir=<url> --livros=<pasta das ondas> [--recibos=<pasta>] --saida=<pasta>

SCRAP-EVOLUCAO-V1 (26/09), degrau (a) da decisao do coordenador (ESTUDO-SCRAPLING-UNIAO): o que o
Piemonte ja provou — o painel da Bacheca (dashboard01.green-planet.it) da 52 bytes a quem bate sem cara
de navegador, e a pagina inteira a quem bate com UA de Chrome + it-IT — resolve-se com CABECALHOS, pela
biblioteca padrao. O degrau (b), a impressao TLS (`curl_cffi`), so entra se um alvo MEDIDO o exigir:
nesta fase, zero dependencia nova.

A LEI. O cabecalho de `coleta/scrap_http.py` diz «nao finge ser navegador de gente». Para material
PUBLICO essa frase foi substituida pela D88 do dono, escrita na Biblia da Coleta como `COL-LAW-704`
(ramo `lei-pesquisadores-v1`, c8e25cdf). Esta peca NAO repete a lei: cumpre-a — so material publico,
teto e respiro intactos, VPN IT provada, e a ROTA NA PROVENIENCIA (o que veio por aqui diz que veio).
O Referer falso fica DESLIGADO: o registo nao mente sobre de onde vimos.

MEDIDO NESTA CASA (26/09): o coletor web (`italy_pilot_collect.mjs`) JA pede com o UA de Chrome 140 e
it-IT; os leitores Python do canario e da prova de territorio pediam com `Chrome/125.0` SEM `Safari/`
(`curadoria/capturador.py`). Uma fonte que filtra pela cara do pedido deixava passar o coletor e barrava
o canario. O UA passa a ter UM dono — `regras/ROTA-NAVEGADOR.json` — lido pelos dois lados.

O QUE ESTA PECA NAO FAZ: nao le robots, nao conta teto, nao espera. Isso e do portao de quem a chama
(excepto `medir`, que e o portao inteiro para UM pedido do coordenador).
"""
from __future__ import annotations

import json
import os
import sys

ROTA_DECLARADA = "DECLARADA"
ROTA_NAVEGADOR = "NAVEGADOR"
ROTAS = (ROTA_DECLARADA, ROTA_NAVEGADOR)
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHA = os.path.join(RAIZ, "regras", "ROTA-NAVEGADOR.json")


def ficha() -> dict:
    with open(FICHA, encoding="utf-8") as f:
        return json.load(f)


def cabecalhos(rota: str, *, do_leitor: dict | None = None) -> dict:
    """DECLARADA: os cabecalhos do proprio leitor (nao se mexe). NAVEGADOR: os da ficha, sem Referer."""
    if rota == ROTA_DECLARADA:
        return dict(do_leitor or {})
    if rota != ROTA_NAVEGADOR:
        raise ValueError("rota desconhecida: %r (uma de %s)" % (rota, ", ".join(ROTAS)))
    f = ficha()
    return {"User-Agent": f["UA"], "Accept": f["ACCEPT"], "Accept-Language": f["ACCEPT_LANGUAGE"]}


def rota_da_fonte(contrato: dict | None) -> str:
    """A rota que o contrato pede. Omissao = a declarada. Valor desconhecido = erro, nao palpite."""
    r = ((contrato or {}).get("ACQUISITION") or {}).get("ROTA_HTTP") or ROTA_DECLARADA
    if r not in ROTAS:
        raise ValueError("ROTA_HTTP desconhecida no contrato: %r (uma de %s)" % (r, ", ".join(ROTAS)))
    return r


def proveniencia(rota: str) -> dict:
    """O que a prova/RAW leva para dizer por onde veio (COL-LAW-704)."""
    if rota == ROTA_NAVEGADOR:
        return {"ROTA_HTTP": ROTA_NAVEGADOR,
                "ROTA_HTTP_DESCRICAO": "cabecalhos de navegador (UA Chrome, it-IT, sem Referer) — "
                                       "regras/ROTA-NAVEGADOR.json, COL-LAW-704"}
    if rota == ROTA_DECLARADA:
        return {"ROTA_HTTP": ROTA_DECLARADA, "ROTA_HTTP_DESCRICAO": "os cabecalhos do proprio leitor"}
    raise ValueError("rota desconhecida: %r" % (rota,))


# ── medir UMA vez com rede (o coordenador corre; D89: medir antes de adotar) ─────────────────────
def pedir(url: str, rota: str = ROTA_NAVEGADOR, *, timeout: float = 25, max_bytes: int = 8_000_000):
    """UM pedido urllib com os cabecalhos da rota. Nao segue saltos (o salto voltaria ao portao).
    → (http, bytes, erro, url_final, retry_after)"""
    import urllib.error                                                 # noqa: PLC0415
    import urllib.request                                               # noqa: PLC0415

    class _SemSaltos(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    abridor = urllib.request.build_opener(_SemSaltos())
    req = urllib.request.Request(url, headers=cabecalhos(rota))
    try:
        with abridor.open(req, timeout=timeout) as r:
            return r.status, r.read(max_bytes), "", r.geturl(), r.headers.get("Retry-After")
    except urllib.error.HTTPError as e:
        corpo = e.read(max_bytes) if e.fp else b""
        return e.code, corpo, "HTTP %d" % e.code, url, e.headers.get("Retry-After")
    except Exception as e:                                              # noqa: BLE001
        return 0, b"", "%s: %s" % (type(e).__name__, str(e)[:120]), url, None


def medir(url: str, *, livros: str, recibos: str | None, saida: str, egresso=None, janela=None,
          robots=None, pedido=None) -> dict:
    """Portao de egresso IT → janela de 24 h do dominio (a MESMA das rodadas, D79) → robots vivo → 1
    pedido pela rota de navegador. Escreve os bytes e um RECIBO que as rodadas leem (PEDIDOS_POR_DOMINIO
    + GERADO_EM). Robots conta como pedido: 2 no total, dentro do teto 5."""
    import hashlib                                                      # noqa: PLC0415
    from datetime import datetime, timezone                             # noqa: PLC0415
    from urllib.parse import urlsplit                                   # noqa: PLC0415
    os.makedirs(saida, exist_ok=True)
    host = urlsplit(url).hostname or ""
    dom = _dominio(host)
    out = {"URL": url, "HOST": host, "PEDIDOS_POR_DOMINIO": {dom: 0}, **proveniencia(ROTA_NAVEGADOR)}

    def fim(porque=None):
        out["PAROU"] = porque
        out["GERADO_EM"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with open(os.path.join(saida, "RECIBO-ROTA-NAVEGADOR.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        return out
    g = (egresso or _egresso_do_dono)()
    out["EGRESSO"] = {"PAIS": g.get("EGRESS_COUNTRY_CODE"), "VOTOS": g.get("VOTOS")}
    if g.get("EGRESS_COUNTRY_CODE") != "IT":
        return fim("EGRESSO_NAO_IT: nada saiu")
    fecha = (janela or _janela_24h)(host, livros, recibos)
    out["JANELA_24H"] = fecha
    if fecha:
        return fim("JANELA_24H: o dominio foi pedido ha menos de 24 h (abre %s)" % fecha)
    ok, motivo = (robots or _robots_vivo)(url)
    out["ROBOTS"] = motivo
    out["PEDIDOS_POR_DOMINIO"][dom] += 1                                # o robots.txt ja foi um pedido
    if not ok:
        return fim("ROBOTS: %s" % motivo)
    st, corpo, erro, final, ra = (pedido or pedir)(url)
    out["PEDIDOS_POR_DOMINIO"][dom] += 1
    out.update({"HTTP": st, "BYTES": len(corpo), "ERRO": erro, "URL_FINAL": final, "RETRY_AFTER": ra,
                "SHA256": hashlib.sha256(corpo).hexdigest(),
                "PRIMEIROS_200": corpo[:200].decode("utf-8", "replace")})
    with open(os.path.join(saida, "CORPO.bin"), "wb") as f:
        f.write(corpo)
    return fim(None)


def _dominio(host):
    """O orcamento do dominio, pela regra da prova-teto (D38/D41), a mesma que as rodadas usam."""
    sys.path.insert(0, os.path.join(RAIZ, "coleta"))
    import dominio_registavel as DR                                     # noqa: PLC0415  (DA-21: runtime, nao provas/)
    return DR.orcamento_de(host)


def _egresso_do_dono():
    import importlib.util                                               # noqa: PLC0415
    s = importlib.util.spec_from_file_location("rede_egresso", os.path.join(RAIZ, "superficie", "rede.py"))
    r = importlib.util.module_from_spec(s)
    s.loader.exec_module(r)
    return r.egresso()


def _janela_24h(host, livros, recibos):
    import importlib.util                                               # noqa: PLC0415
    from datetime import datetime, timedelta, timezone                  # noqa: PLC0415
    from pathlib import Path                                            # noqa: PLC0415
    s = importlib.util.spec_from_file_location(
        "rodadas_janela", os.path.join(RAIZ, "ferramentas", "big_collection", "rodadas.py"))
    R = importlib.util.module_from_spec(s)
    s.loader.exec_module(R)
    ult = R.ultima_visita_por_dominio(Path(livros), tuple(Path(x) for x in [recibos] if x))
    sys.path.insert(0, os.path.join(RAIZ, "coleta"))
    import dominio_registavel as DR                                     # noqa: PLC0415
    t = ult.get(DR.dominio_registavel(host))
    agora = datetime.now(timezone.utc)
    return (t + timedelta(hours=24)).isoformat(timespec="seconds") if t and agora < t + timedelta(hours=24) else None


def _robots_vivo(url):
    sys.path.insert(0, os.path.join(RAIZ, "coleta"))
    import scrap_http as H                                              # noqa: PLC0415
    return H.permitido(url)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    if "medir" not in arg or "livros" not in arg or "saida" not in arg:
        print(__doc__)
        return 2
    r = medir(arg["medir"], livros=arg["livros"], recibos=arg.get("recibos"), saida=arg["saida"])
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if not r.get("PAROU") else 1


if __name__ == "__main__":
    raise SystemExit(main())
