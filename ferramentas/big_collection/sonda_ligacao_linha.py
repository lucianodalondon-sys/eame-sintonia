# -*- coding: utf-8 -*-
"""A SONDA DA LIGACAO DE UMA LINHA AO LIVRO DE 24 H — medida pelo COMPORTAMENTO, nunca pelo texto.

    py ferramentas/big_collection/sonda_ligacao_linha.py --linha=BUSCA

Porque existe: a coleta continua (`coleta_continua.py`) so corre uma linha de rede LIGADA ao contador de
24 h (D86-b/CONTADOR-24H.md). Isso media-se procurando a string `reserva_24h.reservar(` DENTRO do ficheiro
do transporte. Duas coisas partem essa medida:

  · a BUSCA e a SOCIAL reservam no MESMO livro por outra porta (a BUSCA pelo `scrap_http` -> `teto_da_onda`;
    a SOCIAL e o proprio `teto_da_onda`, que fala com o dono `cortesia_adaptativa`). Continuam ligadas e
    ficavam ESPERA_LIGACAO;
  · o inverso tambem era possivel — o texto la, a chamada morta.

A D124-REBASE ja tirou a SITES do texto e pos uma sonda de comportamento (`sonda_ligacao_sites.mjs`). Esta e
a mesma ideia para as linhas Python: nao se le o codigo, liga-se o TRANSPORTE contra um livro TEMPORARIO e
um egresso FECHADO, e mede-se o livro.

O que se mede (ZERO rede externa: proxy para uma porta morta):
  A  um pedido por um dominio LIVRE: o transporte ESCREVE uma RESERVA no livro antes de tentar a rede;
  B  um pedido por um dominio que o livro diz PAUSADO (2 sinais em 24 h): ZERO reservas novas.

LIGADA = A e B. Sai uma linha JSON (a ultima): {"LINHA": ..., "LIGADA": bool, "PORQUE": ..., "MEDIDO": {...}}.

ADENDO-RESERVA (01/10): uma linha com VARIAS portas de rede mede-se porta a porta (PORTAS). A CIENCIA tem tres
(`pesquisadores_t6.PORTAS_DE_REDE`: OpenAlex, Crossref, ORCID); a sonda so exercitava a do OpenAlex e dava LIGADA
com o Crossref e o ORCID a sair sem reserva. Agora cada porta corre A e B contra o SEU livro temporario, e a
linha so esta LIGADA se TODAS estiverem: MEDIDO = {"PORTAS": {porta: {...}}}.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]

LIVRE = "sonda-livre.test"
PAUSADO = "sonda-pausada.test"


def _preparar(tmp: Path) -> None:
    """Egresso fechado, sem nenhum SINTONIA_ herdado, e o livro/politica da cortesia num ficheiro temporario."""
    for k in list(os.environ):
        if k.startswith("SINTONIA_"):
            del os.environ[k]
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
        os.environ[k] = "http://127.0.0.1:9"
    os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost,%s,%s" % (LIVRE, PAUSADO)
    os.environ["PYTHONUTF8"] = "1"
    os.environ["SINTONIA_CORTESIA_LIVRO"] = str(tmp / "LIVRO-CORTESIA.ndjson")
    os.environ["SINTONIA_TETO_ONDA"] = str(tmp / "TETO-ONDA.json")


# ── os motores: cada um faz UM pedido pelo caminho de rede real da linha ─────────────────────────────────
def _motor_busca(url):
    import linha_busca as LB                                          # noqa: PLC0415
    return LB.transporte_real(RAIZ / "coleta")(url)


def _motor_social(url):
    import teto_da_onda as TO                                         # noqa: PLC0415
    host = url.split("//", 1)[-1].split("/", 1)[0]
    return TO.reservar(host)


def _motor_pesquisadores(url):
    import seguir as SG                                               # noqa: PLC0415
    t = SG.Transporte(Path(tempfile.gettempdir()) / "sonda-seguir", buscar=lambda u: (200, b"<html></html>"),
                      pausa=0)
    t._pedir(url, "sonda")
    return t.registo[-1] if t.registo else None


MOTORES = {"BUSCA": _motor_busca, "SOCIAL": _motor_social, "PESQUISADORES": _motor_pesquisadores}


def _portas_ciencia() -> dict:
    """Cada porta de rede da CIENCIA como motor (url -> um pedido por essa porta ao host do url)."""
    import pesquisadores_t6 as T6                                     # noqa: PLC0415
    return {nome: (lambda url, p=p: p(url.split("//", 1)[-1].split("/", 1)[0]))
            for nome, p in T6.PORTAS_DE_REDE.items()}


#: linhas com mais de uma porta de rede: mede-se cada uma (ADENDO-RESERVA)
PORTAS = {"CIENCIA": _portas_ciencia}


def _reservas(livro: Path) -> list:
    if not livro.exists():
        return []
    out = []
    for linha in livro.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        try:
            out.append(json.loads(linha))
        except ValueError:
            continue
    return [e for e in out if e.get("TIPO") == "RESERVA"]


MARCA_DE_RECUSA = ("SEM_RESERVA_24H", "TETO_24H", "TetoDaOnda", "TetoDoDominio", "RotaNaoPermitida")


def _tentar(motor, url) -> tuple:
    """Corre o pedido. A rede esta fechada. → (estado, detalhe): o detalhe diz se o pedido SAIU ou se o LIVRO
    o recusou (e e o que a perna B mede — nao basta o pedido falhar por a rede estar fechada)."""
    try:
        r = motor(url)
        return "CORREU", json.dumps(r, ensure_ascii=False, default=str)[:300]
    except Exception as ex:                                           # noqa: BLE001
        return "LEVANTOU:%s" % type(ex).__name__, "%s: %s" % (type(ex).__name__, str(ex)[:200])


def main(argv=None) -> int:
    arg = {}
    for a in (argv if argv is not None else sys.argv[1:]):
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            arg[k] = v
    linha = (arg.get("linha") or "").upper()
    if linha not in MOTORES and linha not in PORTAS:
        print(json.dumps({"LINHA": linha, "LIGADA": False,
                          "PORQUE": "linha sem motor nesta sonda: %s" % (linha or "(vazia)")}, ensure_ascii=False))
        return 0

    for p in (str(RAIZ), str(RAIZ / "coleta"), str(RAIZ / "ferramentas" / "seguir_pesquisadores")):
        if p not in sys.path:
            sys.path.insert(0, p)

    if linha in PORTAS:
        portas = PORTAS[linha]()
        medidas = {nome: _medir(motor) for nome, motor in portas.items()}
        falhas = ["%s: %s" % (n, porque) for n, (porque, _) in medidas.items() if porque]
        porque = "; ".join(falhas) if falhas else None
        if not portas:
            porque = "a linha declara PORTAS mas nenhuma porta de rede"
        print(json.dumps({"LINHA": linha, "LIGADA": porque is None,
                          "PORQUE": porque or "as %d portas (%s) reservam no livro de 24 h (A) e recusam com o "
                                              "dominio pausado (B)" % (len(portas), ", ".join(portas)),
                          "MEDIDO": {"PORTAS": {n: m for n, (_, m) in medidas.items()}}}, ensure_ascii=False))
        return 0

    porque, medido = _medir(MOTORES[linha])
    print(json.dumps({"LINHA": linha, "LIGADA": porque is None,
                      "PORQUE": porque or "A: o pedido reservou no livro de 24 h (%s); B: com o dominio "
                                          "pausado o livro recusou e 0 reservas novas (%s)"
                                          % (medido["PEDIDO_A"], medido["PEDIDO_B"]),
                      "MEDIDO": medido}, ensure_ascii=False))
    return 0


def _medir(motor) -> tuple:
    """(porque | None, medido): A e B de UM motor, contra um livro da cortesia temporario so dele."""
    with tempfile.TemporaryDirectory(prefix="sonda-ligacao-") as d:
        tmp = Path(d)
        _preparar(tmp)
        livro = Path(os.environ["SINTONIA_CORTESIA_LIVRO"])

        # B precisa do dominio PAUSADO ja no livro ANTES dos pedidos (2 sinais = pausa de 24 h)
        import cortesia_adaptativa as CA                              # noqa: PLC0415
        agora = CA.time.time()
        livro.write_text("".join(json.dumps({"TIPO": "RESPOSTA", "DOMINIO": PAUSADO, "EM": agora - 10 + i,
                                             "RUN_ID": "SONDA", "LINHA": "SONDA", "SINAIS": ["HTTP_429"],
                                             "STATUS": 429, "HOST": PAUSADO}) + "\n" for i in (1, 2)),
                         encoding="utf-8")

        n0 = len(_reservas(livro))
        res_a, det_a = _tentar(motor, "http://%s/pagina" % LIVRE)
        n1 = len(_reservas(livro))
        nB0 = len(_reservas(livro))
        res_b, det_b = _tentar(motor, "http://%s/pagina" % PAUSADO)
        nB1 = len(_reservas(livro))

        liv = _reservas(livro)
        reservas_livres = [e for e in liv if e.get("DOMINIO") == LIVRE]
        reservas_pausadas = [e for e in liv if e.get("DOMINIO") == PAUSADO]
        recusou_b = any(m in det_b for m in MARCA_DE_RECUSA)
        medido = {"RESERVAS_ANTES": n0, "RESERVAS_DEPOIS_A": n1, "PEDIDO_A": res_a,
                  "RESERVAS_LIVRES": len(reservas_livres), "PEDIDO_B": res_b, "RECUSOU_B": recusou_b,
                  "RESERVAS_NOVAS_B": nB1 - nB0, "RESERVAS_PAUSADAS": len(reservas_pausadas)}

        porque = None
        if not reservas_livres:
            porque = "A: o transporte nao escreveu nenhuma RESERVA no livro de 24 h (%s)" % res_a
        elif nB1 - nB0 != 0:
            porque = "B: o livro dizia PAUSADO e %d reserva(s) novas foram escritas" % (nB1 - nB0)
        elif not recusou_b:
            porque = "B: o livro dizia PAUSADO e o pedido nao foi recusado pelo livro (%s: %s)" % (res_b, det_b)
        return porque, medido


if __name__ == "__main__":
    raise SystemExit(main())
