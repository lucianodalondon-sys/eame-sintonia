# -*- coding: utf-8 -*-
"""O FREIO DO TETO D38 NO SCRAP — o pedido que passaria do teto NAO SAI.

    reservar(host)            -> o dominio que pagou, ou levanta TetoDaOnda (nada saiu)
    orcamento_de(host)        -> o nome do orcamento (dominio registavel; D41 junta os do YouTube)
    recusas() / zerar()       -> as recusas deste processo (vao para a linha do livro de corridas)

FREIO-SOCIAL (26/09). Ate aqui o Scrap so CONTAVA (PROVA-TETO-SOCIAL): a prova-teto
dizia depois se a onda tinha passado dos 5. Contar depois e saber que se partiu o
vidro. O transporte web ja travava ANTES (`coleta/italy_pilot_collect.mjs`,
`tetoAtingido` + `gastarNaOnda`); esta peca e o mesmo travao do lado do Scrap, e
fala o MESMO livro, para uma onda que misture web e redes pagar tudo no mesmo sitio:

  · o livro da onda e o ficheiro em SINTONIA_TETO_ONDA: {"PEDIDOS_POR_DOMINIO": {...}};
  · escreve-se sob o MESMO trinco (o directorio `<livro>.trinco`) e por renomeacao;
  · o teto: D124 (dono, 27/09) — o 5 fixo SAIU. O teto de um dominio e o ORCAMENTO VIGENTE da politica
    adaptativa (`coleta/cortesia_adaptativa.py`); SINTONIA_TETO_POR_HOST, se declarada, e um teto manual.
  · com o livro da cortesia (SINTONIA_CORTESIA_LIVRO) o pedido tambem RESERVA la antes de sair (1 de cada
    vez por dominio, pausa minima, orcamento de 24 h) e `registrar_resposta` escreve o que ele mediu.

Duas diferencas, as duas de proposito:
  1. RESERVAR E ATOMICO: ler, comparar e gastar acontecem dentro do trinco. Dois
     processos da onda nao passam os dois pelo 5.o lugar.
  2. D41 (25/09): youtube.com e googlevideo.com sao UM orcamento (o stream do
     YouTube vem do googlevideo; contados a parte, cada video gastava 5 + 5).

SEM LIVRO NAO HA FREIO AQUI. Quem liga o freio e quem conduz: a onda nomeia o livro,
e `scrap_colheita` nomeia um livro PROPRIO da corrida nas fases sociais quando a onda
nao o deu (uma corrida social sozinha continua com 5 por dominio). As outras fases do
Scrap (APIs com paginacao, janelas) nao mudam de comportamento por esta peca.

O dominio registavel e calculado AQUI, sem Public Suffix List (nenhuma se vai buscar
a rede): as duas ultimas etiquetas, salvo sufixo publico de dois niveis declarado. A
lista e a do transporte web (teste de paridade em tests/test_freio_social.py). Um
sufixo que falte junta MAIS do que devia: o freio fica mais apertado, nunca mais largo.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time

TETO_POR_OMISSAO = None          # D124: sem numero fixo — o teto e o vigente da politica adaptativa
ENV_LIVRO = "SINTONIA_TETO_ONDA"
ENV_TETO = "SINTONIA_TETO_POR_HOST"
# Onde um processo FILHO (o yt-dlp com freio) deixa as recusas dele, uma por linha.
ENV_RECUSAS = "SINTONIA_TETO_RECUSAS"
MOTIVO = "TETO_DOMINIO"

SUFIXOS_DE_DOIS_NIVEIS = frozenset("""
gov.it edu.it
abruzzo.it abr.it basilicata.it bas.it calabria.it cal.it campania.it cam.it
emilia-romagna.it emiliaromagna.it emr.it friuli-venezia-giulia.it friuli-vgiulia.it
friulivenezia-giulia.it friulivgiulia.it fvg.it lazio.it laz.it liguria.it lig.it
lombardia.it lom.it marche.it mar.it molise.it mol.it piemonte.it pmn.it
puglia.it pug.it sardegna.it sar.it sicilia.it sic.it toscana.it tos.it
trentino.it trentino-alto-adige.it trentinoaltoadige.it taa.it umbria.it umb.it
valledaosta.it valle-daosta.it vda.it vao.it veneto.it ven.it
co.uk org.uk ac.uk gov.uk com.br org.br gov.br com.au org.au
co.jp com.es com.pt co.nz com.ar com.mx
""".split())

# D41: dominios DIFERENTES que sao o MESMO orcamento. So o que a decisao nomeou.
MESMO_ORCAMENTO = {"googlevideo.com": "youtube.com"}


class TetoDaOnda(RuntimeError):
    """O pedido nao saiu: o orcamento do dominio ja estava gasto."""


def _site(host):
    h = str(host or "").strip().lower().rstrip(".")
    return h[4:] if h.startswith("www.") else h


def dominio_registavel(host):
    h = _site(host)
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", h) or ":" in h:
        return h
    p = [x for x in h.split(".") if x]
    if len(p) <= 2:
        return ".".join(p)
    dois = ".".join(p[-2:])
    return ".".join(p[-3:]) if dois in SUFIXOS_DE_DOIS_NIVEIS else dois


def orcamento_de(host):
    d = dominio_registavel(host)
    return MESMO_ORCAMENTO.get(d, d)


def _ca():
    import sys                                                     # noqa: PLC0415
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import cortesia_adaptativa as CA                               # noqa: PLC0415 — o dono unico (D124)
    return CA


def teto(host=None):
    """O teto do dominio de `host`: o manual declarado (SINTONIA_TETO_POR_HOST) ou o ORCAMENTO VIGENTE da
    politica adaptativa (D124). Sem host e sem manual: o texto que diz de onde vem (para o livro)."""
    v = os.environ.get(ENV_TETO)
    if v in (None, ""):
        if host is None:
            return "ADAPTATIVO_POR_DOMINIO (D124: coleta/cortesia_adaptativa.py)"
        try:
            return _ca().teto_vigente(host)
        except ValueError as e:                                    # livro ilegivel: nao se adivinha um teto
            raise TetoDaOnda("TETO_ADAPTATIVO_ILEGIVEL: %s" % e)
    n = int(v)
    if n < 1:
        raise ValueError("TETO_INVALIDO: %s=%r (inteiro >= 1)" % (ENV_TETO, v))
    return n


def livro():
    return os.environ.get(ENV_LIVRO) or None


def ler_livro(f=None):
    f = f or livro()
    if not f:
        return {}
    try:
        with open(f, encoding="utf-8") as fh:
            return json.load(fh).get("PEDIDOS_POR_DOMINIO") or {}
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as e:
        # Livro ilegivel NAO e livro vazio: vazio deixava a onda recomecar do zero.
        raise TetoDaOnda("TETO_ONDA_ILEGIVEL: %s: %s" % (f, e))


_LOCK = threading.Lock()
_RECUSAS = []


def _trinco(f):
    t = f + ".trinco"
    for i in range(401):
        try:
            os.mkdir(t)
            return t
        except FileExistsError:
            if i >= 400:
                raise TetoDaOnda("TETO_ONDA_TRINCO: %s" % t)
            time.sleep(0.025)


def _porta():
    import sys                                                     # noqa: PLC0415
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import reserva_24h as R24                                      # noqa: PLC0415 — a porta das linhas Python
    return R24


def reservar(host, *, url=None, quem="scrap_http", crawl_delay_s=None):
    """Gasta um lugar do orcamento deste host ANTES do pedido sair.

    Sem livro nomeado: devolve None e nao trava (ver o cabecalho). Com livro: se o
    orcamento ja chegou ao teto, regista a recusa e levanta `TetoDaOnda` — o pedido
    nao sai. O lugar gasto nao se devolve se o pedido falhar: saiu, bateu a porta."""
    f = livro()
    ca = _ca()
    if not f and not ca.livro():
        return None
    if ca.livro() and _porta().dentro_da_porta(host, url):
        return orcamento_de(host)                                  # LINHAS-NO-CONTADOR: a porta ja reservou
    orc = orcamento_de(host)
    t_dom = teto(host)
    if f and int(ler_livro(f).get(orc, 0)) >= t_dom:               # leitura: a onda ja esgotou, nem se reserva
        _recusar(url, host, orc, int(ler_livro(f).get(orc, 0)), t_dom, quem,
                 "teto de %d pedidos ao dominio %s nesta onda" % (t_dom, orc))
    if ca.livro():
        # D124: a reserva no livro da cortesia (atomica, 1 de cada vez, pausa minima, orcamento de 24 h).
        # LINHAS-NO-CONTADOR: o URL decide a ROTA onde a politica as separa (googleapis: CSE != YouTube), e o
        # Crawl-delay do robots lido entra na pausa minima do dominio.
        r = ca.reservar_ou_esperar(host, run_id=os.environ.get("SINTONIA_RUN_ID") or "scrap-%d" % os.getpid(),
                                   linha=os.environ.get("SINTONIA_LINHA") or quem, url=url,
                                   crawl_delay_s=crawl_delay_s)
        if r["ESTADO"] != "RESERVADO":
            _recusar(url, host, orc, r.get("GASTO_24H"), r.get("ORCAMENTO_24H"), quem,
                     "cortesia adaptativa: %s %s %s" % (r["ESTADO"], r.get("MOTIVO") or "", r.get("PORQUE") or ""),
                     motivo="TETO_24H")
        if not f:
            return orc
    with _LOCK:
        t = _trinco(f)
        try:
            p = ler_livro(f)
            gasto = int(p.get(orc, 0))
            if gasto >= t_dom:
                _recusar(url, host, orc, gasto, t_dom, quem, "teto de %d pedidos ao dominio %s nesta onda" % (t_dom, orc))
            p[orc] = gasto + 1
            tmp = f + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump({"PEDIDOS_POR_DOMINIO": p}, fh, indent=1)
            os.replace(tmp, f)
        finally:
            os.rmdir(t)
    return orc


def _recusar(url, host, orc, gasto, t_dom, quem, porque, motivo=MOTIVO):
    r = {"URL": url, "HOST": _site(host), "ORCAMENTO": orc, "GASTO": gasto, "TETO": t_dom, "MOTIVO": motivo,
         "QUEM": quem, "PORQUE": porque}
    _RECUSAS.append(r)
    _escrever_recusa_para_o_pai(r)
    raise TetoDaOnda("%s: %s" % (motivo, porque))


def registrar_resposta(host, status, headers=None, url=None, quem="scrap_http", marcas=()):
    """D124: com o livro da cortesia, a resposta vai la (fecha o «um de cada vez») com o que mediu."""
    ca = _ca()
    if not ca.livro():
        return None
    if _porta().dentro_da_porta(host, url):
        return None                                                # a porta regista a resposta dela
    return ca.registrar_resposta(host, status, dict(headers or {}), url=url, marcas=list(marcas),
                                 run_id=os.environ.get("SINTONIA_RUN_ID") or "scrap-%d" % os.getpid(),
                                 linha=os.environ.get("SINTONIA_LINHA") or quem)


def _escrever_recusa_para_o_pai(r):
    f = os.environ.get(ENV_RECUSAS)
    if f:
        with open(f, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def acrescentar_recusas(lista):
    """As recusas de um filho (lidas do ficheiro dele) entram nas deste processo."""
    with _LOCK:
        _RECUSAS.extend(lista)


def ler_recusas_do_filho(f):
    try:
        with open(f, encoding="utf-8") as fh:
            return [json.loads(l) for l in fh if l.strip()]
    except FileNotFoundError:
        return []


def recusas():
    with _LOCK:
        return list(_RECUSAS)


def zerar():
    with _LOCK:
        _RECUSAS.clear()
