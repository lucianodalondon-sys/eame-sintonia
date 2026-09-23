#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YT3 · CANAIS DE PESSOAS DO AGRO (D24) — canais YouTube, podcasts e newsletters
PUBLICOS de pesquisadores, agronomos, creators e grupos de pesquisa italianos.

    py scripts/canais_pessoas/canais_pessoas.py --sementes            # lista as sementes, sem rede
    py scripts/canais_pessoas/canais_pessoas.py --descobrir [--max=N] # rede: VPN IT, robots, ritmo baixo
    py scripts/canais_pessoas/canais_pessoas.py --medir               # rede: frequencia dos podcasts (RSS)
    py scripts/canais_pessoas/canais_pessoas.py --registar            # porta canonica (fonte_nova), sem rede

O METODO — a rota que a matriz ja permite, e so ela
---------------------------------------------------
`leis/social_matriz.py` tem UMA rota permitida para achar o endereco de uma conta:
`descoberta-indireta:site-da-organizacao` — ler o site da PROPRIA organizacao e trazer
de la o endereco que ELA publicou. Aqui e isso: a pagina oficial liga ao canal, e essa
ligacao e a prova de identidade (quem publicou o link e o dono) e de territorio (o
dominio da pagina). Nao se abre youtube.com, nao se pesquisa na plataforma, nao ha
login, cookie nem pago.

    IDENTIDADE = A PAGINA OFICIAL QUE LIGA AO CANAL. NUNCA O NOME DO CANAL.

AS SEMENTES NAO SAO ADIVINHADAS. Sao as candidatas italianas que a casa JA conhece
(ORGANIZACAO, CIENCIA, IMPRENSA) nesta linha e nas branches da P1 e da P2 — uma pagina
por host. Um canal achado assim vem de uma fonte com dono.

A FREQUENCIA. Podcast: pelo RSS que o proprio podcast publica (1 pedido). Canal YouTube:
a unica rota declarada para listar videos e a Data API (`playlistItems.list`), e a chave
vive so no GitHub (scrap-social.yml) — fica `NAO_MEDIDA` com esse motivo, nunca um
numero inventado.

TRAVAS: portao de egresso IT antes, a cada 15 hosts e depois (PARA se nao for IT);
robots lido e respeitado (robots ilegivel fica CONTADO a parte — nao e proibicao
provada); 1 pagina por host; 2 s entre pedidos; tudo o que se leu fica com sha256.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for g in ("candidatas", "curadoria", "superficie", ""):
    sys.path.insert(0, str(RAIZ / g) if g else str(RAIZ))
import fonte_nova as FN          # noqa: E402 — a porta canonica
import descobrir as D            # noqa: E402 — extrair_links, UA, pais_pela_prova, CTX
import rede                      # noqa: E402 — portao_de_egresso

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "DESCOBERTA-CANAIS-PESSOAS-V1.json"
EVID = Path(os.environ.get("TEMP", "/tmp")) / "yt3-evidencia"
BRANCHES_IRMAS = ("origin/pesquisadores-v1", "origin/pesquisa-projetos-v1")
PAUSA_S = 2.0
TIMEOUT_S = 20
VIGIA_A_CADA = 15


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _fila_de(rev=None):
    if rev is None:
        return json.loads(FN.FILA.read_text(encoding="utf-8"))["CANDIDATAS"]
    r = subprocess.run(["git", "-C", str(RAIZ), "show", "%s:candidatas/FONTES-CANDIDATAS.json" % rev],
                       capture_output=True, text=True, encoding="utf-8")
    return json.loads(r.stdout)["CANDIDATAS"] if r.returncode == 0 else []


def conhecidos():
    """Tudo o que a casa ja conhece: fila desta linha + P1 + P2 + contratos onboarded."""
    urls, ids = set(), set()
    for rev in (None,) + BRANCHES_IRMAS:
        for c in _fila_de(rev):
            urls.add(FN.normalizar(c["URL"]))
            ids.update(re.findall(r"UC[A-Za-z0-9_-]{22}", json.dumps(c)))
    t = json.loads((RAIZ / "regras" / "italy_contracts_onboarded.json").read_text(encoding="utf-8"))
    for l in t["FONTES"]:
        s = json.dumps(l)
        ids.update(re.findall(r"UC[A-Za-z0-9_-]{22}", s))
        for m in re.findall(r"https?://(?:www\.)?youtube\.com/[^\"\s]+", s):
            urls.add(FN.normalizar(m))
    return urls, ids


def sementes():
    """Uma pagina por host: candidatas IT ORGANIZACAO/CIENCIA/IMPRENSA desta linha + P1 + P2."""
    vistos, out = set(), []
    for rev, origem in ((None, "unificacao-v1"),) + tuple((b, b.split("/")[-1]) for b in BRANCHES_IRMAS):
        for c in _fila_de(rev):
            if c.get("PAIS") != "IT" or c.get("TIPO") not in ("ORGANIZACAO", "CIENCIA", "IMPRENSA"):
                continue
            if c.get("ESTADO") == "RECUSADA":
                continue
            u = c["URL"].strip()
            p = urllib.parse.urlparse(u if "://" in u else "https://" + u)
            host = (p.hostname or "").lower().removeprefix("www.")
            if not host or host in vistos:
                continue
            vistos.add(host)
            out.append({"HOST": host, "URL": "%s://%s/" % (p.scheme or "https", p.netloc),
                        "DONO": c["NOME"], "TIPO_DA_SEMENTE": c["TIPO"],
                        "CANDIDATA_DA_SEMENTE": c["CANDIDATA_ID"], "LINHA": origem})
    return out


# ── o que se procura numa pagina ─────────────────────────────────────────────
RE_YT = re.compile(r"^https?://(?:www\.|m\.)?youtube\.com/(@[\w.\-]+|channel/UC[\w-]{22}|c/[\w.\-]+|user/[\w.\-]+)", re.I)
RE_POD = re.compile(r"^https?://(?:(?:open\.)?spotify\.com/show/|podcasts\.apple\.com/|(?:www\.)?spreaker\.com/(?:show|podcast)/"
                    r"|anchor\.fm/|podcasters\.spotify\.com/|(?:www\.)?podbean\.com/|[\w.-]*\.podbean\.com|"
                    r"(?:www\.)?rss\.com/podcasts/)", re.I)
RE_NEWS = re.compile(r"(substack\.com|mailchi\.mp|/newsletter\b|newsletter[-_/]|/iscriviti.*newsletter)", re.I)


def classificar_link(url, anchor):
    m = RE_YT.match(url)
    if m:
        return "YOUTUBE", "https://www.youtube.com/" + m.group(1)
    if RE_POD.match(url):
        return "PODCAST", url.split("?")[0]
    if RE_NEWS.search(url) or re.search(r"\bnewsletter\b", anchor or "", re.I):
        return "NEWSLETTER", url.split("#")[0]
    return None, None


def robots(host):
    """(permitido, estado). 404/410 = sem ficheiro = permitido; outro erro = ILEGIVEL (conta a parte)."""
    url = "https://%s/robots.txt" % host
    req = urllib.request.Request(url, headers={"User-Agent": D.UA})
    rp = urllib.robotparser.RobotFileParser()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S, context=D.CTX) as r:
            corpo = r.read().decode("utf-8", "replace")
        if corpo.lstrip().lower().startswith(("<!doctype", "<html")):
            return None, "ROBOTS_ILEGIVEL (HTML com 200)"
        rp.parse(corpo.splitlines())
        return rp, "LIDO"
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            rp.parse([])
            return rp, "SEM_ROBOTS (%d)" % e.code
        return None, "ROBOTS_ILEGIVEL (HTTP %d)" % e.code
    except Exception as ex:          # noqa: BLE001
        return None, "ROBOTS_ILEGIVEL (%s)" % type(ex).__name__


def buscar(url):
    req = urllib.request.Request(url, headers={"User-Agent": D.UA, "Accept-Language": "it-IT,it;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S, context=D.CTX) as r:
            return r.status, r.geturl(), r.read(1_048_576)
    except urllib.error.HTTPError as e:
        return e.code, url, b""
    except Exception as ex:          # noqa: BLE001
        return 0, url, ("ERRO: %s" % type(ex).__name__).encode()


def portao(onde):
    e = rede.portao_de_egresso("IT", quando=agora())
    return {"ONDE": onde, "GATE": e["EGRESS_GATE"], "PAIS": e.get("EGRESS_COUNTRY_CODE"),
            "QUANDO": agora()}


def descobrir(maximo=None):
    EVID.mkdir(parents=True, exist_ok=True)
    antigo = json.loads(SAIDA.read_text(encoding="utf-8")) if SAIDA.exists() else {"HOSTS": {}, "PORTOES": []}
    feitos = antigo["HOSTS"]
    urls_conh, ids_conh = conhecidos()
    fila = [s for s in sementes() if s["HOST"] not in feitos]
    if maximo:
        fila = fila[:maximo]
    portoes = antigo.get("PORTOES", [])
    g = portao("antes"); portoes.append(g)
    print("portao antes:", g["GATE"], g["PAIS"], "· hosts nesta volta:", len(fila))
    if g["GATE"] != "PASS":
        return 2
    try:
        for i, s in enumerate(fila):
            if i and i % VIGIA_A_CADA == 0:
                g = portao("vigia apos %d hosts" % i); portoes.append(g)
                if g["GATE"] != "PASS":
                    print("PARADO pela vigia:", g); break
            h = s["HOST"]
            rp, estado_robots = robots(h)
            time.sleep(PAUSA_S)
            reg = {**s, "ROBOTS": estado_robots, "QUANDO": agora()}
            if rp is None or not rp.can_fetch(D.UA, s["URL"]):
                reg["RESULTADO"] = "NAO_LIDO_ROBOTS" if rp is not None else "NAO_LIDO_ROBOTS_ILEGIVEL"
                feitos[h] = reg
                continue
            st, final, corpo = buscar(s["URL"])
            time.sleep(PAUSA_S)
            reg.update({"HTTP": st, "URL_FINAL": final})
            if st != 200 or not corpo:
                reg["RESULTADO"] = "NAO_LIDO_HTTP_%s" % st
                feitos[h] = reg
                continue
            sha = hashlib.sha256(corpo).hexdigest()
            (EVID / (h + ".html")).write_bytes(corpo)
            html = corpo.decode("utf-8", "replace")
            achados = {}
            for u, a in D.extrair_links(html, final):
                tipo, canon = classificar_link(u, a)
                if not tipo:
                    continue
                k = FN.normalizar(canon)
                if k in achados:
                    continue
                ja = (k in urls_conh) or any(x in canon for x in ids_conh)
                achados[k] = {"TIPO": tipo, "URL": canon, "ANCORA": (a or "")[:120],
                              "JA_CONHECIDO": ja}
            reg.update({"RESULTADO": "LIDO", "PAGINA_SHA256": sha, "PAGINA_BYTES": len(corpo),
                        "ACHADOS": list(achados.values())})
            feitos[h] = reg
            print("%-40s %s · %d achados" % (h[:40], estado_robots[:12], len(achados)))
    finally:
        g = portao("depois"); portoes.append(g)
        out = {"DATASET": "DESCOBERTA-CANAIS-PESSOAS-V1", "MISSAO": "YT3 canais-pessoas-v1",
               "METODO": "descoberta-indireta:site-da-organizacao (leis/social_matriz.py) — a pagina oficial liga ao canal",
               "UA": D.UA, "EVIDENCIA_FORA_DO_GIT": str(EVID), "PORTOES": portoes, "HOSTS": feitos}
        SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("portao depois:", g["GATE"], g["PAIS"], "->", SAIDA.name)
    return 0


def resumo():
    d = json.loads(SAIDA.read_text(encoding="utf-8"))
    H = d["HOSTS"].values()
    print("hosts", len(d["HOSTS"]), Counter(h["RESULTADO"] for h in H))
    ach = [a | {"HOST": h["HOST"]} for h in H for a in h.get("ACHADOS", [])]
    print("achados", len(ach), Counter((a["TIPO"], a["JA_CONHECIDO"]) for a in ach))
    return 0


def main():
    if "--sementes" in sys.argv:
        s = sementes()
        print(len(s), "sementes", Counter(x["LINHA"] for x in s), Counter(x["TIPO_DA_SEMENTE"] for x in s))
        return 0
    if "--descobrir" in sys.argv:
        mx = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--max=")), None)
        return descobrir(mx)
    if "--resumo" in sys.argv:
        return resumo()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
