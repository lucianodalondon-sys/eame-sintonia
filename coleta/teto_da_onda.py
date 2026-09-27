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
  · o teto e SINTONIA_TETO_POR_HOST (omissao 5), o mesmo nome do transporte web.

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

TETO_POR_OMISSAO = 5
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


def teto():
    v = os.environ.get(ENV_TETO)
    if v in (None, ""):
        return TETO_POR_OMISSAO
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


def reservar(host, *, url=None, quem="scrap_http"):
    """Gasta um lugar do orcamento deste host ANTES do pedido sair.

    Sem livro nomeado: devolve None e nao trava (ver o cabecalho). Com livro: se o
    orcamento ja chegou ao teto, regista a recusa e levanta `TetoDaOnda` — o pedido
    nao sai. O lugar gasto nao se devolve se o pedido falhar: saiu, bateu a porta."""
    f = livro()
    if not f:
        return None
    orc = orcamento_de(host)
    with _LOCK:
        t = _trinco(f)
        try:
            p = ler_livro(f)
            gasto = int(p.get(orc, 0))
            if gasto >= teto():
                r = {"URL": url, "HOST": _site(host), "ORCAMENTO": orc, "GASTO": gasto,
                     "TETO": teto(), "MOTIVO": MOTIVO, "QUEM": quem,
                     "PORQUE": "teto de %d pedidos ao dominio %s nesta onda" % (teto(), orc)}
                _RECUSAS.append(r)
                _escrever_recusa_para_o_pai(r)
                raise TetoDaOnda("%s: %s" % (MOTIVO, r["PORQUE"]))
            p[orc] = gasto + 1
            tmp = f + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump({"PEDIDOS_POR_DOMINIO": p}, fh, indent=1)
            os.replace(tmp, f)
        finally:
            os.rmdir(t)
    return orc


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
