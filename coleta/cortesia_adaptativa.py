# -*- coding: utf-8 -*-
"""A CORTESIA ADAPTATIVA — o UNICO dono da politica do teto por dominio (D124, 27/09/2026).

    from coleta import cortesia_adaptativa as CA
    CA.orcamento_do_dominio("www.cia.it")      -> quantos pedidos ainda cabem agora (int; None = NAO SEI)
    CA.reservar("www.cia.it", run_id=..., linha="SITES")
          -> {"ESTADO": "RESERVADO" | "ADIADO_ATE" | "FAIL" | "UNKNOWN", "ATE": ..., "MOTIVO": ...}
    CA.registrar_resposta("www.cia.it", 429, {"Retry-After": "120"}, run_id=..., linha="SITES")
          -> {"ESTADO": "REGISTADO", "SINAIS": ["HTTP_429", "RETRY_AFTER"], "DEPOIS": {...}}
    CA.registrar_rendimento("cia.it", pedidos=40, documentos_novos=3, run_id=..., linha="SITES")

O DONO FALOU (D124): «o sintonia e um portal feito pra cobrir um pais inteiro, nos precisamos dos maiores
limites ou sem limites de scrap e coleta por dia [...] esses limites precisam ser aumentados ate o limite
das ferramentas que temos, quando chegamos no limite, precisamos avisar o scrap engineer». O 5/dominio/24h
(D7 teste -> D38/D41 incidente -> D79 janela -> D86 manteve) nunca foi medido. Deixa de ser a regra.

A POLITICA (os numeros vivem num so sitio: `regras/POLITICA-CORTESIA-ADAPTATIVA.json`, lido tambem pelo
gemeo `coleta/cortesia_adaptativa.mjs`):
  · classes: PLATAFORMA_GRANDE (youtube, linkedin, instagram, facebook) · API_COM_LIMITE_PUBLICADO
    (openalex, crossref, orcid, googleapis: o limite PUBLICADO deles) · SITE (o resto);
  · o orcamento de 24 h de um dominio comeca no inicial da classe e DOBRA a cada janela de 24 h que
    correu SEM sinal de resistencia E usou pelo menos metade do orcamento, ate ao teto de seguranca;
  · ao 1.o SINAL (429, 503, 403 novo, Retry-After, pagina de desafio, timeouts em serie, queda brusca
    de bytes na mesma URL) corta para metade (nunca abaixo do minimo) e cumpre o Retry-After;
    2 sinais em 24 h = o dominio PARA 24 h;
  · 1 pedido de cada vez por dominio, com pausa minima entre pedidos (o Crawl-delay do robots, se maior);
    dominios diferentes em paralelo, ate LIMITE_GLOBAL_EM_PARALELO.

O LIVRO (append-only, ndjson; SINTONIA_CORTESIA_LIVRO, e o nome antigo SINTONIA_TETO_24H como sinonimo):
  {"TIPO": "RESERVA",    "DOMINIO", "EM", "RUN_ID", "LINHA", "HOST", "CRAWL_DELAY_S"}
  {"TIPO": "RESPOSTA",   "DOMINIO", "EM", "STATUS", "SINAIS", "MARCAS", "RETRY_AFTER_S", "BYTES", "URL", ...}
  {"TIPO": "RENDIMENTO", "DOMINIO", "EM", "PEDIDOS", "DOCUMENTOS_NOVOS", "RUN_ID", "LINHA"}
O estado de um dominio NAO se guarda: DERIVA-SE do livro, sempre pela mesma funcao (`dobrar_eventos`),
aqui e no gemeo. Nada se reescreve; so se acrescenta.

O TRINCO e o da casa (`coleta/reserva_24h.py`, `italy_pilot_collect.mjs`): um DIRECTORIO `<livro>.trinco`,
que o sistema cria ou recusa de uma vez. Perguntar e escrever acontecem dentro dele: dois executores no
mesmo dominio nao passam os dois (o 2.o recebe ADIADO_ATE sem pedir).

    SEM LIVRO NAO HA CONTADOR: reservar devolve FAIL e nao se pede.
    LIVRO ILEGIVEL NAO E LIVRO VAZIO: UNKNOWN, e nada se escreve.
    O SINAL E MEDIDO, NUNCA ADIVINHADO. O ALERTA E TEXTO MONTADO, SEM LLM.

O que CONTINUA (nao e limite de quantidade): robots.txt (D91), Crawl-delay, sem login/cookie/CAPTCHA/
contorno/rota paga, D88 desligado, VPN IT medida, um escritor da Sala, Admission. Esta peca nao toca nenhum.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
RAIZ = _AQUI.parent
sys.path.insert(0, str(_AQUI))
import dominio_registavel as _DR                                   # noqa: E402 — um so dono da regra do dominio

POLITICA_F = RAIZ / "regras" / "POLITICA-CORTESIA-ADAPTATIVA.json"
ENV_LIVRO = "SINTONIA_CORTESIA_LIVRO"
ENV_LIVRO_ANTIGO = "SINTONIA_TETO_24H"          # D90: o mesmo contador, agora adaptativo (sinonimo declarado)
ENV_ALERTAS = "SINTONIA_CORTESIA_ALERTAS"
ENV_POLITICA = "SINTONIA_CORTESIA_POLITICA"
ALERTAS_NOME = "ALERTAS-SCRAP-ENGINEER.ndjson"
TRINCO_ESPERA_S = 10.0
ESPERA_CURTA = ("UM_DE_CADA_VEZ", "PAUSA_MINIMA", "LIMITE_GLOBAL")

_POL = None


class LivroIlegivel(ValueError):
    """O livro existe e nao se consegue ler: NAO SEI (nunca «vazio»)."""


# ── a politica ────────────────────────────────────────────────────────────────
def politica(recarregar: bool = False) -> dict:
    global _POL
    f = os.environ.get(ENV_POLITICA) or str(POLITICA_F)
    if _POL is None or recarregar or _POL.get("_F") != f:
        with open(f, encoding="utf-8") as h:
            p = json.load(h)
        p["_F"] = f
        _POL = p
    return _POL


def dominio(host: str) -> str:
    """O dominio que PAGA o pedido: o registavel (`coleta/dominio_registavel.py`), juntado pela D41."""
    d = _DR.dominio_registavel(host)
    return politica()["MESMO_ORCAMENTO"].get(d, d)


def classe_de(dom: str, pol: dict | None = None) -> tuple:
    """(nome da classe, parametros: INICIAL, TETO_DE_SEGURANCA, MINIMO, PAUSA_MINIMA_S, DOBRA)."""
    pol = pol or politica()
    c = pol["CLASSES"]
    api = c["API_COM_LIMITE_PUBLICADO"]
    if dom in api["DOMINIOS"]:
        a = api["DOMINIOS"][dom]
        return "API_COM_LIMITE_PUBLICADO", {"INICIAL": a["ORCAMENTO_24H"], "TETO": a["ORCAMENTO_24H"],
                                            "MINIMO": api["MINIMO_24H"], "PAUSA_S": a["PAUSA_MINIMA_S"],
                                            "DOBRA": bool(api["DOBRA"])}
    nome = "PLATAFORMA_GRANDE" if dom in c["PLATAFORMA_GRANDE"]["DOMINIOS"] else "SITE"
    k = c[nome]
    return nome, {"INICIAL": k["ORCAMENTO_INICIAL_24H"], "TETO": k["TETO_DE_SEGURANCA_24H"],
                  "MINIMO": k["MINIMO_24H"], "PAUSA_S": k["PAUSA_MINIMA_S"], "DOBRA": bool(k["DOBRA"])}


# ── o livro ───────────────────────────────────────────────────────────────────
def livro() -> Path | None:
    f = os.environ.get(ENV_LIVRO) or os.environ.get(ENV_LIVRO_ANTIGO)
    return Path(f) if f else None


def alertas_f() -> Path | None:
    a = os.environ.get(ENV_ALERTAS)
    if a:
        return Path(a)
    f = livro()
    return f.parent / ALERTAS_NOME if f else None


# ── o livro ANTIGO (D90, 26/09): {"RESERVAS": [{DOMINIO, QTD, EM, RUN_ID, LINHA}]} ─────────────────────
# D124-REBASE (verificador independente, 28/09): o livro vivo `%SI%\TETO-24H.json`, passado pela coleta
# continua em --teto-24h, esta neste formato. Lido como ndjson dava ILEGIVEL -> toda a reserva UNKNOWN ->
# a coleta parava. Agora: LEITURA COMPATIVEL (cada reserva antiga vira QTD eventos RESERVA, com o mesmo EM,
# e conta no gasto de 24 h como contava) e MIGRACAO no 1.o escrito, sob o trinco: o ficheiro passa a ndjson
# (o original fica em `<livro>.D90.json`, uma vez). Um livro antigo MALFORMADO continua ILEGIVEL (NAO SEI).
# Nenhuma resposta e inventada: a reserva antiga sem resposta segura o dominio so ate ao LEASE.
MIGRADO_DE = "TETO-24H/D90"
_RE_ANTIGO = re.compile(r'^\s*\{\s*"RESERVAS"\s*:')


def e_livro_antigo(texto: str) -> bool:
    return bool(_RE_ANTIGO.match(texto[:256]))


def eventos_do_livro_antigo(texto: str) -> list:
    try:
        d = json.loads(texto)
    except ValueError as ex:
        raise LivroIlegivel("livro D90 (RESERVAS[]) nao e JSON: %s" % ex)
    if not isinstance(d, dict) or not isinstance(d.get("RESERVAS"), list):
        raise LivroIlegivel("livro D90 sem RESERVAS[]")
    out = []
    for i, r in enumerate(d["RESERVAS"], 1):
        if not isinstance(r, dict) or not isinstance(r.get("DOMINIO"), str) or not r["DOMINIO"] \
                or isinstance(r.get("EM"), bool) or not isinstance(r.get("EM"), (int, float)) \
                or isinstance(r.get("QTD"), bool) or not isinstance(r.get("QTD"), int) or r["QTD"] < 1:
            raise LivroIlegivel("livro D90: reserva %d sem DOMINIO/EM/QTD validos" % i)
        for _ in range(r["QTD"]):
            out.append({"TIPO": "RESERVA", "DOMINIO": dominio(r["DOMINIO"]), "EM": r["EM"],
                        "RUN_ID": r.get("RUN_ID"), "LINHA": r.get("LINHA"), "HOST": r["DOMINIO"],
                        "MIGRADO_DE": MIGRADO_DE})
    return out


def migrar_livro_antigo(f: Path) -> dict:
    """Chamar SOB o trinco. Livro D90 -> ndjson (o original fica em `<livro>.D90.json`). Idempotente."""
    if not f.exists():
        return {"ESTADO": "SEM_LIVRO", "LIVRO": str(f)}
    texto = f.read_text(encoding="utf-8")
    if not e_livro_antigo(texto):
        return {"ESTADO": "JA_NDJSON", "LIVRO": str(f)}
    ev = eventos_do_livro_antigo(texto)                            # malformado levanta: nada se escreve
    copia = Path(str(f) + ".D90.json")
    if not copia.exists():
        copia.write_text(texto, encoding="utf-8")
    tmp = Path(str(f) + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as h:
        for e in ev:
            h.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(tmp, f)
    return {"ESTADO": "MIGRADO", "LIVRO": str(f), "COPIA_D90": str(copia), "EVENTOS": len(ev)}


def ler_eventos(f: Path) -> list:
    if not f.exists():
        return []
    texto = f.read_text(encoding="utf-8")
    if e_livro_antigo(texto):
        return eventos_do_livro_antigo(texto)
    out = []
    for i, l in enumerate(texto.splitlines(), 1):
        if not l.strip():
            continue
        try:
            e = json.loads(l)
        except ValueError as ex:
            raise LivroIlegivel("linha %d nao e JSON: %s" % (i, ex))
        if not isinstance(e, dict) or e.get("TIPO") not in ("RESERVA", "RESPOSTA", "RENDIMENTO") \
                or not isinstance(e.get("DOMINIO"), str) or not isinstance(e.get("EM"), (int, float)):
            raise LivroIlegivel("linha %d sem TIPO/DOMINIO/EM validos" % i)
        out.append(e)
    return out


def _acrescentar(f: Path, e: dict) -> None:
    f.parent.mkdir(parents=True, exist_ok=True)
    if f.exists():
        with open(f, encoding="utf-8") as h:
            cabeca = h.read(256)
        if e_livro_antigo(cabeca):
            migrar_livro_antigo(f)                                 # sob o trinco de quem escreve (D124-REBASE)
    with open(f, "a", encoding="utf-8", newline="\n") as h:
        h.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")


class _Trinco:
    def __init__(self, f: Path):
        self.d = Path(str(f) + ".trinco")

    def __enter__(self):
        self.d.parent.mkdir(parents=True, exist_ok=True)
        fim = time.monotonic() + TRINCO_ESPERA_S
        while True:
            try:
                os.mkdir(self.d)
                return self
            except FileExistsError:
                if time.monotonic() > fim:
                    raise TimeoutError("CORTESIA_TRINCO: %s ocupado ha mais de %.0f s" % (self.d, TRINCO_ESPERA_S))
                time.sleep(0.025)

    def __exit__(self, *a):
        os.rmdir(self.d)


# ── o estado de um dominio: DERIVADO do livro (a mesma funcao no gemeo .mjs) ──
def dobrar_eventos(eventos: list, dom: str, agora: float, pol: dict | None = None) -> dict:
    pol = pol or politica()
    J = float(pol["JANELA_S"])
    R = pol["RECUO"]
    nome, k = classe_de(dom, pol)
    nivel, desde = int(k["INICIAL"]), None
    reservas, sinais_em = [], []
    pausado_ate = retry_ate = 0.0
    ult_res = ult_resp = None
    crawl = 0.0
    ultimo_sinal = None
    evs = sorted((e for e in eventos if e["DOMINIO"] == dom), key=lambda e: float(e["EM"]))

    def promover(t):
        nonlocal nivel, desde
        if desde is None:
            return
        while t >= desde + J:
            fim = desde + J
            usados = sum(1 for x in reservas if desde <= x < fim)
            teve_sinal = any(desde < x < fim for x in sinais_em)   # o sinal que ABRIU a janela nao conta contra ela
            if k["DOBRA"] and not teve_sinal and usados > 0 and usados >= math.ceil(R["FRACAO_DE_USO_PARA_DOBRAR"] * nivel):
                nivel = min(int(k["TETO"]), nivel * 2)
            desde = fim
            if not any(x >= desde for x in reservas) and t >= desde + 2 * J:
                desde += math.floor((t - desde) / J - 1) * J        # dias parados nao dobram: salta-os de uma vez

    for e in evs:
        t = float(e["EM"])
        if desde is None:
            desde = t
        promover(t)
        if e["TIPO"] == "RESERVA":
            reservas.append(t)
            ult_res = t
            if e.get("CRAWL_DELAY_S") is not None:
                crawl = float(e["CRAWL_DELAY_S"])
        elif e["TIPO"] == "RESPOSTA":
            ult_resp = t
            if e.get("SINAIS"):
                nivel = max(int(k["MINIMO"]), int(math.floor(nivel * R["FATOR"])))
                desde = t
                sinais_em.append(t)
                ultimo_sinal = {"EM": t, "SINAIS": list(e["SINAIS"]), "STATUS": e.get("STATUS")}
                if e.get("RETRY_AFTER_S"):
                    retry_ate = max(retry_ate, t + float(e["RETRY_AFTER_S"]))
                if sum(1 for x in sinais_em if x > t - R["JANELA_DOS_SINAIS_S"]) >= R["SINAIS_PARA_PAUSA"]:
                    pausado_ate = max(pausado_ate, t + float(R["PAUSA_S"]))
    promover(agora)

    vivas = sorted(x for x in reservas if x > agora - J)
    gasto = len(vivas)
    cabem_24h = max(0, nivel - gasto)
    pausa = max(float(k["PAUSA_S"]), crawl)
    em_curso_ate = None
    if ult_res is not None and (ult_resp is None or ult_res > ult_resp) and agora < ult_res + pol["LEASE_S"]:
        em_curso_ate = ult_res + pol["LEASE_S"]
    marcos = [x for x in (ult_res, ult_resp) if x is not None]
    pausa_ate = (max(marcos) + pausa) if marcos else None
    orc_ate = vivas[gasto - nivel] + J if cabem_24h == 0 and gasto >= nivel and nivel > 0 else None
    bloq = max(pausado_ate, retry_ate)
    if pausado_ate > agora:
        situ = "PAUSADO"
    elif retry_ate > agora:
        situ = "RETRY_AFTER"
    elif any(x > agora - J for x in sinais_em):
        situ = "EM_RECUO"
    elif nivel >= int(k["TETO"]):
        situ = "NO_TETO_DE_SEGURANCA"
    else:
        situ = "NORMAL"
    proximos = [x for x in (bloq, em_curso_ate, pausa_ate, orc_ate) if x is not None and x > agora]
    return {"DOMINIO": dom, "CLASSE": nome, "SITUACAO": situ,
            "ORCAMENTO_24H": nivel, "ORCAMENTO_INICIAL_24H": int(k["INICIAL"]), "TETO_DE_SEGURANCA_24H": int(k["TETO"]),
            "MINIMO_24H": int(k["MINIMO"]), "GASTO_24H": gasto, "CABEM_24H": cabem_24h,
            "CABEM": 0 if bloq > agora else cabem_24h,
            "PAUSA_MINIMA_S": pausa, "SINAIS_24H": sum(1 for x in sinais_em if x > agora - J),
            "ULTIMO_SINAL": ultimo_sinal, "PAUSADO_ATE": pausado_ate or None, "RETRY_ATE": retry_ate or None,
            "EM_CURSO_ATE": em_curso_ate, "PAUSA_ATE": pausa_ate, "ORCAMENTO_ATE": orc_ate,
            "PROXIMO_PEDIDO_EM": max(proximos) if proximos else agora, "JANELA_DESDE": desde}


def em_curso_global(eventos: list, agora: float, pol: dict | None = None, menos: str | None = None) -> list:
    """[(dominio, ate)] com pedido em curso agora (reserva sem resposta, dentro do LEASE)."""
    pol = pol or politica()
    ult = {}
    for e in eventos:
        if e["TIPO"] in ("RESERVA", "RESPOSTA"):
            r = ult.setdefault(e["DOMINIO"], [None, None])
            i = 0 if e["TIPO"] == "RESERVA" else 1
            if r[i] is None or float(e["EM"]) >= r[i]:
                r[i] = float(e["EM"])
    out = []
    for d, (res, resp) in ult.items():
        if d != menos and res is not None and (resp is None or res > resp) and agora < res + pol["LEASE_S"]:
            out.append((d, res + pol["LEASE_S"]))
    return sorted(out)


# ── os sinais (medidos; a mesma funcao no gemeo) ──────────────────────────────
def _cab(headers, nome):
    for k, v in (headers or {}).items():
        if str(k).lower() == nome:
            return str(v).strip()
    return None


def retry_after_s(valor, agora: float, pol: dict | None = None):
    pol = pol or politica()
    if valor in (None, ""):
        return None
    v = str(valor).strip()
    if re.fullmatch(r"\d+", v):
        s = float(int(v))
    else:
        try:
            s = parsedate_to_datetime(v).timestamp() - agora
        except (TypeError, ValueError, IndexError, OverflowError):
            return None
    return max(0.0, min(s, float(pol["RECUO"]["RETRY_AFTER_MAXIMO_S"])))


def detectar_sinais(status, headers=None, corpo=None, n_bytes=None, url=None, marcas=(), historico=(),
                    agora: float = 0.0, pol: dict | None = None) -> tuple:
    """(sinais, retry_after_s). `historico` = as RESPOSTA anteriores DESTE dominio, pela ordem do livro."""
    pol = pol or politica()
    S = pol["SINAIS"]
    sinais = []
    st = int(status or 0)
    if st == 429:
        sinais.append("HTTP_429")
    if st == 503:
        sinais.append("HTTP_503")
    if st == 403 and not (historico and int(historico[-1].get("STATUS") or 0) == 403):
        sinais.append("HTTP_403_NOVO")
    ra = retry_after_s(_cab(headers, "retry-after"), agora, pol)
    if ra is not None:
        sinais.append("RETRY_AFTER")
    txt = (corpo.decode("utf-8", "replace") if isinstance(corpo, (bytes, bytearray)) else str(corpo or ""))[:65536].lower()
    tam = n_bytes if n_bytes is not None else (len(corpo) if corpo is not None else None)
    desafio = (_cab(headers, "cf-mitigated") or "").lower() == "challenge" or any(m in txt for m in S["DESAFIO_FORTE"])
    if not desafio and (st >= 400 or (tam is not None and tam < S["DESAFIO_FRACO_SO_ABAIXO_DE_BYTES"])):
        desafio = any(m in txt for m in S["DESAFIO_FRACO"])
    if desafio:
        sinais.append("PAGINA_DE_DESAFIO")
    if "TIMEOUT" in (marcas or ()):
        serie = 1
        for h in reversed(list(historico)):
            if "TIMEOUT" in (h.get("MARCAS") or ()):
                serie += 1
            else:
                break
        if serie >= S["TIMEOUTS_EM_SERIE"]:
            sinais.append("TIMEOUTS_EM_SERIE")
    if url and n_bytes is not None and 200 <= st < 300:
        ant = [h for h in historico if h.get("URL") == url and 200 <= int(h.get("STATUS") or 0) < 300
               and h.get("BYTES") is not None]
        if ant and ant[-1]["BYTES"] >= S["QUEDA_DE_BYTES_REFERENCIA_MINIMA"] \
                and n_bytes < S["QUEDA_DE_BYTES_FRACAO"] * ant[-1]["BYTES"]:
            sinais.append("QUEDA_DE_BYTES")
    return sinais, ra


# ── a API ─────────────────────────────────────────────────────────────────────
def estado_do_dominio(host: str, agora: float | None = None) -> dict:
    t = time.time() if agora is None else agora
    dom = dominio(host)
    f = livro()
    try:
        ev = ler_eventos(f) if f else []
    except LivroIlegivel as ex:
        return {"DOMINIO": dom, "ESTADO": "UNKNOWN", "PORQUE": "livro ilegivel: %s" % ex}
    e = dobrar_eventos(ev, dom, t)
    e["ESTADO"] = "LIDO" if f else "SEM_LIVRO"
    return e


def orcamento_do_dominio(host: str, agora: float | None = None):
    """Quantos pedidos ainda cabem AGORA neste dominio (24 h). None = NAO SEI (livro ilegivel).
    Sem livro: o inicial da classe (nao ha memoria de nada)."""
    e = estado_do_dominio(host, agora)
    return None if e.get("ESTADO") == "UNKNOWN" else e["CABEM"]


def teto_vigente(host: str, agora: float | None = None) -> int:
    """O orcamento de 24 h EM VIGOR para o dominio (o nivel adaptativo). Livro ilegivel: levanta
    (quem planeia com um teto que nao leu esta a adivinhar)."""
    e = estado_do_dominio(host, agora)
    if e.get("ESTADO") == "UNKNOWN":
        raise LivroIlegivel(e["PORQUE"])
    return e["ORCAMENTO_24H"]


def teto_sem_livro(host: str) -> int:
    """D124-REBASE: o teto POR CORRIDA de quem pede SEM livro (sem memoria entre corridas nao ha prova de
    que o site aguenta o inicial): o que a politica declara em SEM_LIVRO (o MINIMO da classe, o chao do recuo)."""
    pol = politica()
    _, k = classe_de(dominio(host), pol)
    regra = (pol.get("SEM_LIVRO") or {}).get("TETO_POR_CORRIDA", "MINIMO_24H")
    if regra != "MINIMO_24H":
        raise ValueError("POLITICA: SEM_LIVRO.TETO_POR_CORRIDA=%r (so MINIMO_24H e conhecido)" % regra)
    return int(k["MINIMO"])


def reservar(host: str, *, run_id: str, linha: str, crawl_delay_s: float | None = None,
             agora: float | None = None) -> dict:
    """Pergunta e escreve num so passo, sob o trinco. Nunca levanta: devolve o estado."""
    f = livro()
    base = {"DOMINIO": None, "RUN_ID": run_id, "LINHA": linha}
    if f is None:
        return dict(base, ESTADO="FAIL", PORQUE="%s vazio: sem contador partilhado nao se pede" % ENV_LIVRO)
    try:
        dom = dominio(host)
    except Exception as ex:                                        # noqa: BLE001
        return dict(base, ESTADO="FAIL", PORQUE="host invalido: %s" % ex)
    base["DOMINIO"] = dom
    if not dom or not run_id or not linha:
        return dict(base, ESTADO="FAIL", PORQUE="pedido invalido (host, run_id, linha)")
    try:
        with _Trinco(f):
            ev = ler_eventos(f)
            t = time.time() if agora is None else agora
            pol = politica()
            e = dobrar_eventos(ev, dom, t, pol)
            if crawl_delay_s is not None:
                marcos = [float(x["EM"]) for x in ev if x["DOMINIO"] == dom and x["TIPO"] in ("RESERVA", "RESPOSTA")]
                if marcos and max(marcos) + float(crawl_delay_s) > (e["PAUSA_ATE"] or 0):
                    e["PAUSA_ATE"] = max(marcos) + float(crawl_delay_s)
            porque = None
            if (e["PAUSADO_ATE"] or 0) > t:
                porque, ate = "PAUSA_24H", e["PAUSADO_ATE"]
            elif (e["RETRY_ATE"] or 0) > t:
                porque, ate = "RETRY_AFTER", e["RETRY_ATE"]
            elif e["CABEM_24H"] <= 0:
                porque, ate = "ORCAMENTO_ESGOTADO", e["ORCAMENTO_ATE"] or t + pol["JANELA_S"]
            elif e["EM_CURSO_ATE"] is not None:
                porque, ate = "UM_DE_CADA_VEZ", e["EM_CURSO_ATE"]
            elif e["PAUSA_ATE"] is not None and e["PAUSA_ATE"] > t:
                porque, ate = "PAUSA_MINIMA", e["PAUSA_ATE"]
            else:
                outros = em_curso_global(ev, t, pol, menos=dom)
                if len(outros) >= pol["LIMITE_GLOBAL_EM_PARALELO"]:
                    porque, ate = "LIMITE_GLOBAL", min(a for _, a in outros)
            if porque:
                if porque == "ORCAMENTO_ESGOTADO" and e["ORCAMENTO_24H"] >= e["TETO_DE_SEGURANCA_24H"]:
                    _alertar(f, dom, e, linha, "LIMITE_PUBLICADO" if e["CLASSE"] == "API_COM_LIMITE_PUBLICADO"
                             else "TETO_DE_SEGURANCA", {"ORCAMENTO_24H": e["ORCAMENTO_24H"], "GASTO_24H": e["GASTO_24H"]},
                             [run_id], t)
                return dict(base, ESTADO="ADIADO_ATE", ATE=ate, MOTIVO=porque, GASTO_24H=e["GASTO_24H"],
                            ORCAMENTO_24H=e["ORCAMENTO_24H"])
            r = {"TIPO": "RESERVA", "DOMINIO": dom, "EM": t, "RUN_ID": run_id, "LINHA": linha,
                 "HOST": _DR.host_limpo(host)}
            if crawl_delay_s is not None:
                r["CRAWL_DELAY_S"] = float(crawl_delay_s)
            _acrescentar(f, r)
            return dict(base, ESTADO="RESERVADO", EM=t, GASTO_24H=e["GASTO_24H"] + 1,
                        ORCAMENTO_24H=e["ORCAMENTO_24H"], CABEM_24H=e["CABEM_24H"] - 1)
    except TimeoutError as ex:
        return dict(base, ESTADO="UNKNOWN", PORQUE=str(ex))
    except LivroIlegivel as ex:
        return dict(base, ESTADO="UNKNOWN", PORQUE="livro ilegivel: %s" % ex)


def reservar_ou_esperar(host: str, *, run_id: str, linha: str, crawl_delay_s: float | None = None,
                        espera_max_s: float = 180.0, dormir=time.sleep) -> dict:
    """Como `reservar`, mas uma espera CURTA (um de cada vez, pausa minima, limite global) espera-se
    em vez de desistir. Orcamento esgotado, Retry-After e pausa de 24 h NUNCA se esperam aqui."""
    fim = time.time() + espera_max_s
    while True:
        r = reservar(host, run_id=run_id, linha=linha, crawl_delay_s=crawl_delay_s)
        if r["ESTADO"] != "ADIADO_ATE" or r.get("MOTIVO") not in ESPERA_CURTA or r["ATE"] > fim:
            return r
        dormir(max(0.01, r["ATE"] - time.time()))


def registrar_resposta(host: str, status, headers=None, *, sinais=(), marcas=(), url=None, n_bytes=None,
                       corpo=None, run_id: str, linha: str, agora: float | None = None) -> dict:
    """Escreve a resposta (fecha o «um de cada vez») e o que ela MEDIU. Sinal -> recuo + alerta."""
    f = livro()
    base = {"RUN_ID": run_id, "LINHA": linha}
    if f is None:
        return dict(base, ESTADO="FAIL", PORQUE="%s vazio" % ENV_LIVRO)
    pol = politica()
    fora = [s for s in sinais if s not in pol["SINAIS"]["VOCABULARIO"]] + \
           [m for m in marcas if m not in pol["SINAIS"]["MARCAS"]]
    if fora:
        return dict(base, ESTADO="FAIL", PORQUE="sinal/marca fora do vocabulario: %s" % fora)
    dom = dominio(host)
    try:
        with _Trinco(f):
            ev = ler_eventos(f)
            t = time.time() if agora is None else agora
            hist = [e for e in ev if e["DOMINIO"] == dom and e["TIPO"] == "RESPOSTA"]
            med, ra = detectar_sinais(status, headers, corpo, n_bytes, url, marcas, hist, t, pol)
            todos = sorted(set(med) | set(sinais), key=pol["SINAIS"]["VOCABULARIO"].index)
            e = {"TIPO": "RESPOSTA", "DOMINIO": dom, "EM": t, "STATUS": int(status or 0), "SINAIS": todos,
                 "MARCAS": list(marcas), "RETRY_AFTER_S": ra, "BYTES": n_bytes, "URL": url,
                 "RUN_ID": run_id, "LINHA": linha}
            _acrescentar(f, e)
            depois = dobrar_eventos(ev + [e], dom, t, pol)
            alerta = None
            if todos:
                alerta = _alertar(f, dom, depois, linha, "PAUSA_24H" if depois["SITUACAO"] == "PAUSADO" else "RECUO",
                                  {"STATUS": int(status or 0), "SINAIS": todos, "RETRY_AFTER_S": ra, "URL": url},
                                  [run_id] + ([url] if url else []), t)
            return dict(base, ESTADO="REGISTADO", DOMINIO=dom, SINAIS=todos, RETRY_AFTER_S=ra,
                        DEPOIS=depois, ALERTA=alerta)
    except TimeoutError as ex:
        return dict(base, ESTADO="UNKNOWN", PORQUE=str(ex))
    except LivroIlegivel as ex:
        return dict(base, ESTADO="UNKNOWN", PORQUE="livro ilegivel: %s" % ex)


def registrar_rendimento(host: str, *, pedidos: int, documentos_novos: int, run_id: str, linha: str,
                         recibos=(), agora: float | None = None) -> dict:
    """Quanto um dominio RENDEU (documentos novos por pedido). Pouco rendimento com amostra -> alerta."""
    f = livro()
    if f is None:
        return {"ESTADO": "FAIL", "PORQUE": "%s vazio" % ENV_LIVRO}
    dom = dominio(host)
    pol = politica()
    try:
        with _Trinco(f):
            ev = ler_eventos(f)
            t = time.time() if agora is None else agora
            e = {"TIPO": "RENDIMENTO", "DOMINIO": dom, "EM": t, "PEDIDOS": int(pedidos),
                 "DOCUMENTOS_NOVOS": int(documentos_novos), "RUN_ID": run_id, "LINHA": linha}
            _acrescentar(f, e)
            A = pol["ALERTAS"]
            alerta = None
            if pedidos >= A["RENDIMENTO_AMOSTRA_MINIMA_PEDIDOS"] and \
                    documentos_novos / pedidos < A["RENDIMENTO_MINIMO_DOC_POR_PEDIDO"]:
                alerta = _alertar(f, dom, dobrar_eventos(ev, dom, t, pol), linha, "RENDIMENTO_BAIXO",
                                  {"PEDIDOS": int(pedidos), "DOCUMENTOS_NOVOS": int(documentos_novos),
                                   "DOC_POR_PEDIDO": round(documentos_novos / pedidos, 4)},
                                  [run_id] + list(recibos), t)
            return {"ESTADO": "REGISTADO", "DOMINIO": dom, "ALERTA": alerta}
    except TimeoutError as ex:
        return {"ESTADO": "UNKNOWN", "PORQUE": str(ex)}
    except LivroIlegivel as ex:
        return {"ESTADO": "UNKNOWN", "PORQUE": "livro ilegivel: %s" % ex}


# ── o alerta ao Scrap Engineer (dentro do trinco do livro; sem LLM) ───────────
def _iso(t: float) -> str:
    return datetime.fromtimestamp(t, tz=timezone.utc).isoformat(timespec="seconds")


def ler_alertas(a: Path | None = None) -> list:
    a = a or alertas_f()
    if not a or not a.exists():
        return []
    return [json.loads(l) for l in a.read_text(encoding="utf-8").splitlines() if l.strip()]


def _alertar(f: Path, dom: str, est: dict, linha: str, tipo: str, sinal: dict, recibos: list, t: float):
    pol = politica()
    a = alertas_f()
    janela = pol["ALERTAS"]["UM_POR_DOMINIO_E_TIPO_POR_S"]
    for x in ler_alertas(a):
        if x.get("DOMINIO") == dom and x.get("TIPO_ALERTA") == tipo and float(x.get("EM", 0)) > t - janela:
            return None                                            # ja avisado nas ultimas 24 h
    b = {"TIPO_ALERTA": tipo, "DOMINIO": dom, "CLASSE": est.get("CLASSE"), "LINHA": linha, "EM": t,
         "EM_ISO": _iso(t), "SINAL_MEDIDO": sinal, "RECIBOS": [r for r in recibos if r],
         "ORCAMENTO_24H": est.get("ORCAMENTO_24H"), "SITUACAO": est.get("SITUACAO"),
         "ESTUDAR": pol["ALERTAS"]["MELHORIAS_A_ESTUDAR"], "LIVRO": str(f)}
    _acrescentar(a, b)
    return b


ALERTA_EM_PALAVRAS = {
    "RECUO": "o site deu sinal de resistencia e o nosso orcamento diario nele caiu para metade",
    "PAUSA_24H": "o site deu 2 sinais de resistencia em 24 h: esta parado 24 h",
    "TETO_DE_SEGURANCA": "chegamos ao teto de seguranca deste site (a ferramenta esta no limite)",
    "LIMITE_PUBLICADO": "chegamos ao limite PUBLICADO desta API",
    "RENDIMENTO_BAIXO": "cada pedido a este dominio traz poucos documentos novos",
}


def pergunta_scrap_engineer(data: str | None = None, saida: Path | None = None) -> Path | None:
    """PERGUNTA-SCRAP-ENGINEER-<data>.txt com os alertas do dia (UTC), pronta para o coordenador mandar
    ao bot (consultar_scrap_engineer.sh). Sem alertas no dia: nao escreve nada, devolve None."""
    data = data or datetime.now(timezone.utc).date().isoformat()
    a = alertas_f()
    doDia = [x for x in ler_alertas(a) if str(x.get("EM_ISO", ""))[:10] == data]
    if not doDia:
        return None
    saida = saida or (a.parent if a else RAIZ / "data" / "cortesia")
    linhas = ["PERGUNTA AO SCRAP ENGINEER — SINTONIA EAME — %s (UTC)" % data, "",
              "Contexto (D124 do dono): o limite de coleta e o limite das ferramentas. Quando um dominio bate",
              "o limite, recua por sinal de resistencia ou rende pouco por pedido, pedimos que estudes como",
              "trazer MAIS materia-prima com MENOS pedidos. Continua proibido: login, cookie, CAPTCHA, contorno,",
              "rota paga, disfarce (D88), ignorar robots.txt (D91).", "",
              "%d alerta(s) de hoje:" % len(doDia), ""]
    for i, x in enumerate(doDia, 1):
        linhas += ["%d. %s — %s [%s, linha %s]" % (i, x["DOMINIO"], x["TIPO_ALERTA"], x.get("CLASSE"), x.get("LINHA")),
                   "   em palavras: %s." % ALERTA_EM_PALAVRAS.get(x["TIPO_ALERTA"], x["TIPO_ALERTA"]),
                   "   medido: %s" % json.dumps(x.get("SINAL_MEDIDO"), ensure_ascii=False, sort_keys=True),
                   "   orcamento 24 h agora: %s · situacao: %s · em %s" % (x.get("ORCAMENTO_24H"), x.get("SITUACAO"), x.get("EM_ISO")),
                   "   recibos: %s" % (", ".join(map(str, x.get("RECIBOS") or [])) or "(nenhum)"), ""]
    linhas += ["Pergunta: para cada dominio acima, existe feed RSS/Atom, sitemap.xml, conditional GET",
               "(ETag / If-Modified-Since), rota JSON do proprio site ou lote de API que traga os mesmos",
               "documentos com menos pedidos? Responde com o dominio, a rota proposta e como medir o ganho.", "",
               "(gerado por coleta/cortesia_adaptativa.py --pergunta; texto montado, sem LLM)"]
    saida.mkdir(parents=True, exist_ok=True)
    p = saida / ("PERGUNTA-SCRAP-ENGINEER-%s.txt" % data)
    p.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    return p


def resumo(agora: float | None = None) -> dict:
    """Todos os dominios do livro, o estado de cada um (so leitura)."""
    f = livro()
    t = time.time() if agora is None else agora
    if f is None:
        return {"ESTADO": "SEM_LIVRO", "DOMINIOS": {}}
    try:
        ev = ler_eventos(f)
    except LivroIlegivel as ex:
        return {"ESTADO": "UNKNOWN", "PORQUE": str(ex), "DOMINIOS": {}}
    pol = politica()
    return {"ESTADO": "LIDO", "LIVRO": str(f), "EM_ISO": _iso(t),
            "DOMINIOS": {d: dobrar_eventos(ev, d, t, pol) for d in sorted({e["DOMINIO"] for e in ev})}}


def main(argv=None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if a[:1] == ["--pergunta"]:
        data = a[1] if len(a) > 1 else None
        p = pergunta_scrap_engineer(data)
        print(p if p else "SEM_ALERTAS no dia %s" % (data or "de hoje"))
        return 0
    if a[:1] == ["--estado"] and len(a) > 1:
        print(json.dumps(estado_do_dominio(a[1]), ensure_ascii=False, indent=1))
        return 0
    if a[:1] == ["--migrar"]:
        # py coleta/cortesia_adaptativa.py --migrar [livro]  -> o livro D90 ({RESERVAS:[]}) passa a ndjson
        f = Path(a[1]) if len(a) > 1 else livro()
        if f is None:
            print("SEM_LIVRO: --migrar <livro> ou %s" % ENV_LIVRO)
            return 2
        try:
            with _Trinco(f):
                r = migrar_livro_antigo(f)
        except (LivroIlegivel, TimeoutError) as ex:
            r = {"ESTADO": "UNKNOWN", "LIVRO": str(f), "PORQUE": str(ex)}
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["ESTADO"] != "UNKNOWN" else 2
    if a[:1] == ["--resumo"]:
        r = resumo()
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["ESTADO"] != "UNKNOWN" else 2
    print(__doc__)
    print("uso: --estado <host> | --resumo | --pergunta [AAAA-MM-DD] | --migrar [livro]   (livro em %s)" % ENV_LIVRO)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
