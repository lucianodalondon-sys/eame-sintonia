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


def _curl(url):
    """(status, corpo) pelo curl com o MESMO User-Agent. A licao da R2: o urllib leva
    recusa de TLS/cliente onde o curl entra, e a recusa lia-se como «robots ilegivel»."""
    r = subprocess.run(["curl", "-sS", "-L", "--max-time", str(TIMEOUT_S), "-A", D.UA,
                        "-H", "Accept-Language: it-IT,it;q=0.9", "-o", "-", "-w", "\n__S__%{http_code}", url],
                       capture_output=True)
    s = r.stdout
    k = s.rfind(b"\n__S__")
    if k < 0:
        return 0, b""
    return int(s[k + 6:] or 0), s[:k]


def segunda_passagem():
    """So para os NAO_LIDO_ROBOTS_ILEGIVEL da 1.a: robots pelo curl; «HTML com 200» no
    lugar do robots.txt e a pagina de «nao existe» (soft-404) — sem ficheiro, sem regra,
    DECLARADO no registo. 401/403 continua a fechar. Orcamento: com o pedido da 1.a,
    no maximo 3 por host (robots urllib + robots curl + pagina)."""
    d = json.loads(SAIDA.read_text(encoding="utf-8"))
    urls_conh, ids_conh = conhecidos()
    alvo = [h for h in d["HOSTS"].values() if h["RESULTADO"] == "NAO_LIDO_ROBOTS_ILEGIVEL"]
    g = portao("antes da 2.a passagem"); d["PORTOES"].append(g)
    print("portao:", g["GATE"], "· hosts:", len(alvo))
    if g["GATE"] != "PASS":
        return 2
    for i, reg in enumerate(alvo):
        if i and i % VIGIA_A_CADA == 0:
            g = portao("vigia 2.a passagem %d" % i); d["PORTOES"].append(g)
            if g["GATE"] != "PASS":
                break
        h = reg["HOST"]
        st, corpo = _curl("https://%s/robots.txt" % h)
        time.sleep(PAUSA_S)
        texto = corpo.decode("utf-8", "replace")
        rp = urllib.robotparser.RobotFileParser()
        if st in (401, 403):
            reg.update({"ROBOTS_2": "HTTP %d pelo curl — fechado" % st, "RESULTADO": "NAO_LIDO_ROBOTS_2"})
            continue
        if st == 200 and not texto.lstrip().lower().startswith(("<!doctype", "<html")):
            rp.parse(texto.splitlines()); est = "LIDO pelo curl"
        elif st in (200, 404, 410):
            rp.parse([]); est = ("SEM_ROBOTS: /robots.txt devolve %s — pagina de «nao existe», sem regra"
                                % ("HTML com 200" if st == 200 else "HTTP %d" % st))
        else:
            reg.update({"ROBOTS_2": "HTTP %d pelo curl — continua ilegivel" % st,
                        "RESULTADO": "NAO_LIDO_ROBOTS_ILEGIVEL_2"})
            continue
        reg["ROBOTS_2"] = est
        if not rp.can_fetch(D.UA, reg["URL"]):
            reg["RESULTADO"] = "NAO_LIDO_ROBOTS"
            continue
        st, corpo = _curl(reg["URL"])
        time.sleep(PAUSA_S)
        reg["HTTP"] = st
        if st != 200 or not corpo:
            reg["RESULTADO"] = "NAO_LIDO_HTTP_%s" % st
            continue
        sha = hashlib.sha256(corpo).hexdigest()
        (EVID / (h + ".html")).write_bytes(corpo)
        achados = {}
        for u, a in D.extrair_links(corpo.decode("utf-8", "replace"), reg["URL"]):
            tipo, canon = classificar_link(u, a)
            if not tipo:
                continue
            k = FN.normalizar(canon)
            if k in achados:
                continue
            ja = (k in urls_conh) or any(x in canon for x in ids_conh)
            achados[k] = {"TIPO": tipo, "URL": canon, "ANCORA": (a or "")[:120], "JA_CONHECIDO": ja}
        reg.update({"RESULTADO": "LIDO_2A_PASSAGEM", "PAGINA_SHA256": sha, "PAGINA_BYTES": len(corpo),
                    "ACHADOS": list(achados.values())})
        print("%-40s %s · %d achados" % (h[:40], est[:24], len(achados)), flush=True)
    g = portao("depois da 2.a passagem"); d["PORTOES"].append(g)
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("portao depois:", g["GATE"])
    return 0


RE_DATA = re.compile(r"\b(20[12]\d)[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12]\d|3[01])\b|\b(0[1-9]|[12]\d|3[01])[-/.](0[1-9]|1[0-2])[-/.](20[12]\d)\b")


def medir():
    """Newsletters no PROPRIO host da semente: 1 pedido (3.o do host) — ha arquivo publico com
    edicoes datadas? Se sim, a frequencia sai das datas; se nao, SO_INSCRICAO (o conteudo chega
    por e-mail: nao e publico). Podcast no Spotify: sem RSS publico -> NAO_MEDIDA."""
    d = json.loads(SAIDA.read_text(encoding="utf-8"))
    g = portao("antes de medir"); d["PORTOES"].append(g)
    if g["GATE"] != "PASS":
        return 2
    hoje = datetime.now(timezone.utc).date()
    for h in d["HOSTS"].values():
        for a in h.get("ACHADOS", []):
            if a["JA_CONHECIDO"] or "MEDIDA" in a:
                continue
            if a["TIPO"] == "YOUTUBE":
                a["MEDIDA"] = {"FREQUENCIA": "NAO_MEDIDA",
                               "PORQUE": "a unica rota declarada para listar videos e a Data API "
                                         "(playlistItems.list); a chave vive so no GitHub (scrap-social.yml)"}
                continue
            if a["TIPO"] == "PODCAST":
                a["MEDIDA"] = {"FREQUENCIA": "NAO_MEDIDA",
                               "PORQUE": "Spotify nao publica RSS; o feed do proprio podcast nao esta ligado na pagina oficial"
                               if "spotify" in a["URL"] else "rota de RSS por medir"}
                continue
            host_link = (urllib.parse.urlparse(a["URL"]).hostname or "").lower().removeprefix("www.")
            if host_link != h["HOST"]:
                a["MEDIDA"] = {"ARQUIVO": "NAO_MEDIDO", "PORQUE": "o link sai do host da semente (%s)" % host_link}
                continue
            if h.get("_MEDIDO"):
                a["MEDIDA"] = {"ARQUIVO": "NAO_MEDIDO", "PORQUE": "orcamento do host gasto (3 pedidos)"}
                continue
            st, corpo = _curl(a["URL"])
            time.sleep(PAUSA_S)
            h["_MEDIDO"] = True
            t = corpo.decode("utf-8", "replace")
            datas = set()
            for m in RE_DATA.finditer(t):
                try:
                    y, mo, dd = (m.group(1), m.group(2), m.group(3)) if m.group(1) else (m.group(6), m.group(5), m.group(4))
                    datas.add(datetime(int(y), int(mo), int(dd)).date())
                except ValueError:
                    pass
            ult = sorted(x for x in datas if x <= hoje)
            ano = [x for x in ult if (hoje - x).days <= 365]
            inscr = bool(re.search(r"iscriviti|iscrizione|subscribe|registrati|inserisci.*e-?mail", t, re.I))
            a["MEDIDA"] = {"HTTP": st, "DATAS_NA_PAGINA": len(ult), "DATAS_ULTIMOS_365D": len(ano),
                           "ULTIMA_DATA": ult[-1].isoformat() if ult else None,
                           "FORMULARIO_DE_INSCRICAO": inscr,
                           "ARQUIVO": "PUBLICO_COM_DATAS" if len(ano) >= 3 else "SO_INSCRICAO_OU_SEM_DATAS"}
            print("%-28s %-10s %s" % (h["HOST"][:28], a["TIPO"], a["MEDIDA"]["ARQUIVO"]), flush=True)
    g = portao("depois de medir"); d["PORTOES"].append(g)
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


DECISOES = AQUI / "DECISOES-YT3-V1.json"


def registar():
    """Porta canonica. So entra o que DECISOES-YT3-V1.json diz ENTRA, com a prova na NOTA."""
    d = json.loads(SAIDA.read_text(encoding="utf-8"))
    dec = {x["URL"]: x for x in json.loads(DECISOES.read_text(encoding="utf-8"))["DECISOES"]}
    tipo_da_casa = {"YOUTUBE": "YOUTUBE", "PODCAST": "IMPRENSA", "NEWSLETTER": "IMPRENSA"}
    novas, ja = [], []
    for h in d["HOSTS"].values():
        for a in h.get("ACHADOS", []):
            x = dec.get(a["URL"])
            if not x or x["DECISAO"] != "ENTRA":
                continue
            # O pais le-se PRIMEIRO no dominio da semente (o que a propria organizacao
            # publica) e so depois no endereco apos o redireccionamento: biolchim.it
            # -> biolchim.com deu NAO SEI na 1.a gravacao (YT3, corrigido a mao, 5 linhas).
            pais, prova_pais = D.pais_pela_prova(h["URL"])
            if pais == "NAO SEI" and h.get("URL_FINAL"):
                pais, prova_pais = D.pais_pela_prova(h["URL_FINAL"])
            nota = ("YT3 D24 · IDENTIDADE: a pagina oficial %s (sha256 %s, lida %s) liga a este %s "
                    "[ancora «%s»] — descoberta-indireta:site-da-organizacao · TERRITORIO: %s (%s) · "
                    "DONO: %s (%s; semente %s) · FREQUENCIA: %s · TECNICO: %s · %s") % (
                h.get("URL_FINAL") or h["URL"], h.get("PAGINA_SHA256", "?")[:16], h["QUANDO"][:10],
                a["TIPO"], a["ANCORA"][:60], pais, prova_pais, x["DONO"], x["TIPO_DE_DONO"],
                h["CANDIDATA_DA_SEMENTE"], json.dumps(a.get("MEDIDA", {}), ensure_ascii=False)[:200],
                x["TECNICO"], x["PORQUE"])
            antes = FN.carregar()["TOTAL"] if FN.FILA.exists() else 0
            linha = FN.registar(tipo=tipo_da_casa[a["TIPO"]], pais=pais, nome=x["NOME"], url=a["URL"],
                                para_que=x["PARA_QUE"], quem_viu="scripts/canais_pessoas/canais_pessoas.py (YT3)",
                                onde_viu=h.get("URL_FINAL") or h["URL"], nota=nota)
            (novas if FN.carregar()["TOTAL"] > antes else ja).append(linha["CANDIDATA_ID"])
    print("novas", len(novas), novas, "· ja estavam", len(ja))
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
    if "--segunda-passagem" in sys.argv:
        return segunda_passagem()
    if "--medir" in sys.argv:
        return medir()
    if "--registar" in sys.argv:
        return registar()
    if "--resumo" in sys.argv:
        return resumo()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
