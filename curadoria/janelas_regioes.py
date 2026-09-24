#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JANELAS DE CULTURA POR REGIAO (D29, missao P1g).

Para cada regiao italiana, tres colunas:
  FITO       servizio fitosanitario regionale — bollettini / avvisi di difesa integrata
  AGROMETEO  servico agrometeorologico — bollettino agrometeo, fenologia, modelli
  CONSORZIO  consorzi di difesa com avisos

Cada celula e medida (robots, HTTP, login, exemplo real de boletim com data,
formato) e, se for nova e publica, registada pela porta canonica
(candidatas/fonte_nova.py::registar). Nada e escrito na fila a mao.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "candidatas"))
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "superficie"))

from fonte_nova import registar, normalizar, carregar  # noqa: E402
import descobrir as D                                   # noqa: E402
import rede as R                                        # noqa: E402

SAIDA = RAIZ / "curadoria" / "JANELAS-REGIOES-V1.json"
REGIOES = ("Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli Venezia Giulia",
           "Lazio", "Liguria", "Lombardia", "Marche", "Molise", "Piemonte", "Puglia", "Sardegna",
           "Sicilia", "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto")
COLUNAS = ("FITO", "AGROMETEO", "CONSORZIO")
OUTRAS_LANES = ("origin/pesquisadores-v2", "origin/pesquisa-projetos-v1")
VIGIA_A_CADA = 10

_MESES = {m: i for i, m in enumerate(
    "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split(), 1)}
_DATA_RE = [
    (re.compile(r"(?<!\d)(\d{1,2})[/.\-_](\d{1,2})[/.\-_](20\d{2})(?!\d)"), "dmy"),
    (re.compile(r"(?<!\d)(20\d{2})[/.\-_](\d{1,2})[/.\-_](\d{1,2})(?!\d)"), "ymd"),
    (re.compile(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)"), "ymd"),
    (re.compile(r"(?<!\d)(\d{1,2})\s+(%s)\s+(20\d{2})" % "|".join(_MESES), re.I), "dMy"),
]
_BOLETIM_RE = re.compile(r"bollettin|avvis|notiziari|comunicat|bulletin|\.pdf($|\?)", re.I)
_LOGIN_RE = re.compile(r"type=[\"']?password|area riservata|effettua il login|accedi con spid", re.I)


class VigiaParou(RuntimeError):
    pass


def vigia() -> str:
    e = R.portao_de_egresso("IT")
    if e["EGRESS_GATE"] != "PASS":
        raise VigiaParou("EGRESS=%s" % e["EGRESS_COUNTRY_CODE"])
    return "PASS"


def _data(texto: str):
    melhor = None
    for rx, ordem in _DATA_RE:
        for m in rx.finditer(texto):
            try:
                if ordem == "dmy":
                    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                elif ordem == "ymd":
                    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                else:
                    d, mo, y = int(m.group(1)), _MESES[m.group(2).lower()], int(m.group(3))
                dt = datetime(y, mo, d).date()
            except (ValueError, KeyError):
                continue
            if dt.year >= 2020 and dt <= datetime.now().date() and (melhor is None or dt > melhor):
                melhor = dt
    return melhor


_diag: dict = {}


def robots(url: str, orcam) -> tuple[bool, str]:
    host = urllib.parse.urlsplit(url).netloc.lower()
    if host not in _diag:
        rp = urllib.robotparser.RobotFileParser()
        r_url = "%s://%s/robots.txt" % (urllib.parse.urlsplit(url).scheme or "https", host)
        orcam.pausar(r_url)
        orcam.registar(r_url)
        try:
            req = urllib.request.Request(r_url, headers={"User-Agent": D.UA})
            with urllib.request.urlopen(req, timeout=D.TIMEOUT_S, context=D.CTX) as r:
                rp.parse(r.read().decode("utf-8", "replace").splitlines())
                classe = "ROBOTS_200"
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                rp.parse([])
                classe = "ROBOTS_AUSENTE"
            else:
                rp.parse(["User-agent: *", "Disallow: /"])
                classe = "ROBOTS_ILEGIVEL_%d" % e.code
        except Exception as ex:
            rp.parse(["User-agent: *", "Disallow: /"])
            classe = "ROBOTS_ILEGIVEL_%s" % type(ex).__name__
        _diag[host] = (classe, rp)
    classe, rp = _diag[host]
    if classe.startswith("ROBOTS_ILEGIVEL"):
        return False, classe
    if not rp.can_fetch(D.UA, url):
        return False, "ROBOTS_PROIBE"
    return True, classe


def conhecidos() -> tuple[dict, dict]:
    prod = {normalizar(c["URL"]): c["CANDIDATA_ID"] for c in carregar()["CANDIDATAS"]}
    lanes: dict = {}
    for ref in OUTRAS_LANES:
        try:
            bruto = subprocess.run(["git", "show", ref + ":candidatas/FONTES-CANDIDATAS.json"],
                                   cwd=str(RAIZ), capture_output=True, check=True).stdout
            for c in json.loads(bruto)["CANDIDATAS"]:
                k = normalizar(c["URL"])
                if k not in prod:
                    lanes.setdefault(k, "%s %s" % (ref.split("/")[-1], c["CANDIDATA_ID"]))
        except Exception:
            pass
    return prod, lanes


def inspecionar(url: str, orcam) -> dict:
    """Mede a pagina: robots, HTTP, login, exemplo real de boletim com data, formato."""
    out = {"URL": url}
    ok, porque = robots(url, orcam)
    out["ROBOTS"] = porque
    if not ok:
        out["ESTADO_MEDIDO"] = "ROBOTS_PROIBE" if porque == "ROBOTS_PROIBE" else "ROBOTS_ILEGIVEL"
        return out
    html, code, ct = D._buscar_pagina_html(url, orcam)
    out["HTTP"], out["CONTENT_TYPE"] = code, (ct or "")[:60]
    if code in (401, 403):
        out["ESTADO_MEDIDO"] = "LOGIN_OU_BLOQUEIO"
        return out
    if not (200 <= code < 300):
        out["ESTADO_MEDIDO"] = "SEM_LIGACAO" if code == 0 else "HTTP_%d" % code
        return out
    html = html or ""
    out["LOGIN_NA_PAGINA"] = bool(_LOGIN_RE.search(html))
    exemplos = []
    for u, a in D.extrair_links(html, url):
        alvo = u + " " + a
        if not _BOLETIM_RE.search(alvo):
            continue
        dt = _data(alvo)
        if dt:
            exemplos.append((dt, u, a))
    if not exemplos:
        dt = _data(re.sub(r"<[^>]+>", " ", html))
        out["DATA_MAIS_RECENTE_NA_PAGINA"] = dt.isoformat() if dt else None
    exemplos.sort(reverse=True)
    if exemplos:
        dt, u, a = exemplos[0]
        out["EXEMPLO"] = {"URL": u, "DATA": dt.isoformat(), "TEXTO": " ".join(a.split())[:100]}
        out["N_BOLETINS_COM_DATA"] = len(exemplos)
    pdfs = sum(1 for _, u, _ in exemplos if ".pdf" in u.lower())
    out["FORMATO"] = ("PDF" if exemplos and pdfs * 2 >= len(exemplos) else
                      "HTML" if exemplos else ("TABELA_HTML" if html.count("<table") >= 2 else "HTML"))
    out["ESTADO_MEDIDO"] = "PUBLICO_COM_BOLETIM" if exemplos else "PUBLICO_SEM_BOLETIM_DATADO"
    return out


def explorar(url: str, padrao: str, orcam) -> list:
    ok, porque = robots(url, orcam)
    if not ok:
        print("HUB FECHADO", porque, url)
        return []
    html, code, ct = D._buscar_pagina_html(url, orcam)
    if not html:
        print("HUB SEM HTML", code, ct, url)
        return []
    rx = re.compile(padrao, re.I)
    vistos, out = set(), []
    for u, a in D.extrair_links(html, url):
        u = u.split("#")[0]
        if u in vistos or not u.startswith("http") or not (rx.search(u) or rx.search(a)):
            continue
        vistos.add(u)
        out.append((u, " ".join(a.split())))
    return out


def correr(celulas: list, orcamento: int = 300, registar_novas: bool = True) -> dict:
    prod, lanes = conhecidos()
    orcam = D.Orcamento(total=orcamento, por_dominio=12)
    visitados = D._ler_visitados()
    vigias, linhas, n, novos_aqui = [vigia()], [], 0, {}
    inicio = datetime.now(timezone.utc).isoformat()
    parou = None
    try:
        for c in celulas:
            n += 1
            if n % VIGIA_A_CADA == 0:
                vigias.append(vigia())
            k = normalizar(c["url"])
            linha = {"REGIAO": c["regiao"], "COLUNA": c["coluna"], "NOME": c["nome"], "URL": c["url"],
                     "DISCOVERED_FROM": c["de"]}
            linha.update(inspecionar(c["url"], orcam))
            if k in novos_aqui:
                linha["ESTADO"] = "NOVA %s (mesma pagina serve as duas colunas)" % novos_aqui[k]
            elif k in prod:
                linha["ESTADO"] = "JA_NA_FILA %s" % prod[k]
            elif linha["ESTADO_MEDIDO"] == "PUBLICO_COM_BOLETIM" or (
                    linha["ESTADO_MEDIDO"] == "PUBLICO_SEM_BOLETIM_DATADO" and c["coluna"] != "CONSORZIO"):
                # consorzio so entra com aviso datado ("consorzi di difesa COM avisos");
                # pagina oficial de boletins entra mesmo sem data legivel, e a tabela diz isso.
                if registar_novas:
                    ex = linha.get("EXEMPLO") or {}
                    nota = ("DISCOVERED_FROM=%s | DISCOVERED_AT=%s | DISCOVERED_HTTP=%s | ROBOTS=%s | "
                            "FORMATO=%s | EXEMPLO=%s (%s) | LOGIN_NA_PAGINA=%s | JANELA=%s/%s | MISSAO=P1G-JANELAS"
                            % (c["de"], datetime.now(timezone.utc).isoformat(), linha.get("HTTP"),
                               linha["ROBOTS"], linha.get("FORMATO"), ex.get("URL", "NAO_SEI"),
                               ex.get("DATA", "sem data"), linha.get("LOGIN_NA_PAGINA"), c["regiao"], c["coluna"]))
                    r = registar(tipo=c.get("tipo", "BASE_OFICIAL"), pais="IT", nome=c["nome"], url=c["url"],
                                 para_que=c["para_que"], quem_viu="curadoria/janelas_regioes.py (P1g)",
                                 onde_viu=c["de"], nota=nota)
                    novos_aqui[k] = r["CANDIDATA_ID"]
                    D._marcar_visitado(k, "REGISTADO_%s" % r["CANDIDATA_ID"], visitados)
                    linha["ESTADO"] = "NOVA %s" % r["CANDIDATA_ID"] + (
                        "" if linha.get("EXEMPLO") else " (sem exemplo datado)")
                else:
                    linha["ESTADO"] = "SERIA_NOVA"
                if k in lanes:
                    linha["TAMBEM_NA_LANE"] = lanes[k]
            elif linha["ESTADO_MEDIDO"] == "PUBLICO_SEM_BOLETIM_DATADO":
                linha["ESTADO"] = "SEM_AVISO_DATADO"
            else:
                linha["ESTADO"] = linha["ESTADO_MEDIDO"]
            linhas.append(linha)
            time.sleep(c.get("pausa", 2))
        vigias.append(vigia())
    except VigiaParou as ex:
        parou = str(ex)
    finally:
        D._gravar_visitados(visitados)
    matriz = {r: {col: [] for col in COLUNAS} for r in REGIOES}
    for l in linhas:
        matriz[l["REGIAO"]][l["COLUNA"]].append(l["ESTADO"].split()[0])
    out = {"DATASET": "JANELAS-REGIOES-V1", "CORRIDA_EM": inicio, "VIGIA_PAROU": parou, "VIGIAS": vigias,
           "PEDIDOS_DE_REDE": orcam.pedidos_feitos, "MAX_PEDIDOS_UM_DOMINIO": orcam.max_num_dominio(),
           "NOVAS": [l["ESTADO"].split()[1] for l in linhas if l["ESTADO"].startswith("NOVA")],
           "MATRIZ": matriz, "CELULAS": linhas}
    fd, tmp = tempfile.mkstemp(dir=str(SAIDA.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, SAIDA)
    return out


def main() -> int:
    import argparse
    from janelas_celulas import CELULAS, REGIOES_SEM_FONTE
    ap = argparse.ArgumentParser(description="Janelas de cultura por regiao (P1g).")
    ap.add_argument("--correr", action="store_true", help="mede e regista (rede, VPN IT)")
    ap.add_argument("--orcamento", type=int, default=300)
    a = ap.parse_args()
    if not a.correr:
        from collections import Counter
        print("CELULAS", len(CELULAS), dict(Counter(c["coluna"] for c in CELULAS)))
        print("REGIOES_COBERTAS", len({c["regiao"] for c in CELULAS}), "de", len(REGIOES))
        return 0
    r = correr(CELULAS, orcamento=a.orcamento)
    for (reg, col), porque in REGIOES_SEM_FONTE.items():
        if not r["MATRIZ"][reg][col]:
            r["MATRIZ"][reg][col] = ["SEM_FONTE_ACHADA: " + porque]
    fd, tmp = tempfile.mkstemp(dir=str(SAIDA.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(r, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, SAIDA)
    from collections import Counter
    print("NOVAS", len(r["NOVAS"]), "PEDIDOS", r["PEDIDOS_DE_REDE"], "VIGIA_PAROU", r["VIGIA_PAROU"], "VIGIAS", r["VIGIAS"])
    print("ESTADOS", dict(Counter(l["ESTADO"].split()[0] for l in r["CELULAS"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


_SUBBOLETIM_RE = re.compile(r"bollettin|avvis|notiziari|agrometeo|fenolog|difesa|archivio", re.I)


def aprofundar(orcamento: int = 120) -> dict:
    """Para as celulas sem exemplo datado: abre ate 2 subpaginas de boletins do mesmo site
    e procura la um boletim com data. So mede; nao regista subpaginas."""
    r = json.loads(SAIDA.read_text(encoding="utf-8"))
    orcam = D.Orcamento(total=orcamento, por_dominio=6)
    vigias, n = [vigia()], 0
    for l in r["CELULAS"]:
        if l.get("EXEMPLO") or l.get("ESTADO_MEDIDO") != "PUBLICO_SEM_BOLETIM_DATADO" or l["COLUNA"] == "CONSORZIO":
            continue
        n += 1
        if n % VIGIA_A_CADA == 0:
            vigias.append(vigia())
        host = urllib.parse.urlsplit(l["URL"]).netloc.lower()
        html, code, ct = D._buscar_pagina_html(l["URL"], orcam)
        subs = []
        for u, a in D.extrair_links(html or "", l["URL"]):
            u = u.split("#")[0]
            if urllib.parse.urlsplit(u).netloc.lower() != host or u.rstrip("/") == l["URL"].rstrip("/"):
                continue
            if _SUBBOLETIM_RE.search(u + " " + a) and u not in subs and not u.lower().endswith(".pdf"):
                subs.append(u)
        tentados = []
        for u in subs[:2]:
            m = inspecionar(u, orcam)
            tentados.append({"URL": u, "ESTADO_MEDIDO": m.get("ESTADO_MEDIDO")})
            if m.get("EXEMPLO"):
                l["EXEMPLO"] = dict(m["EXEMPLO"], VIA=u)
                l["FORMATO"] = m.get("FORMATO")
                break
            time.sleep(1)
        l["APROFUNDADO"] = tentados or "sem subpagina de boletins no mesmo site"
        time.sleep(1)
    vigias.append(vigia())
    r["APROFUNDAMENTO"] = {"PEDIDOS": orcam.pedidos_feitos, "VIGIAS": vigias,
                           "COM_EXEMPLO_AGORA": sum(1 for l in r["CELULAS"] if l.get("EXEMPLO"))}
    fd, tmp = tempfile.mkstemp(dir=str(SAIDA.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(r, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, SAIDA)
    return r["APROFUNDAMENTO"]
