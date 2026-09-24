#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P5 · PESSOAS PELO SITE OFICIAL — a pagina de cada docente/investigador.

A YT3 concluiu que a pagina oficial de uma ORGANIZACAO liga ao canal da organizacao,
nunca ao da pessoa. O caminho para a pessoa e a pagina da propria pessoa no site
oficial (departamento de Agraria/Veterinaria, instituto agrario do CNR): se ESSA
pagina liga a um LinkedIn/Instagram/YouTube, a casa oficial esta a dizer «este perfil
e desta pessoa» — prova de identidade D24/D21 e territorio pelo dominio oficial.

Caminho, por semente (SEMENTES-P5.json):
  casa  ->  paginas de PESSOAL/DOCENTI  ->  pagina de cada pessoa  ->  links sociais.

Armadilhas guardadas no codigo:
  · o rodape da universidade (o LinkedIn/Instagram/YouTube da PROPRIA casa) aparece
    em todas as paginas — tudo o que ja estava na casa ou na listagem, e tudo o que
    se repete em >= 3 pessoas da mesma semente, e da instituicao, nao da pessoa;
  · linkedin.com/company e da organizacao; so linkedin.com/in/ e perfil pessoal;
  · CREA e Bologna ficam com a P4 (nao se bate duas vezes no mesmo site).

Rota: descoberta-indireta:site-da-organizacao (DIRECT_HTTP) — a unica que a matriz
permite para achar contas. Nenhum pedido a LinkedIn/Instagram/YouTube/ResearchGate.

Uso:
  py scripts/pessoas_docentes/pessoas_docentes.py --descobrir [--max-pessoas=N]
  py scripts/pessoas_docentes/pessoas_docentes.py --registar
  py scripts/pessoas_docentes/pessoas_docentes.py --resumo
"""
from __future__ import annotations

import hashlib
import html as H
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
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
import descobrir as D            # noqa: E402 — extrair_links, UA, CTX
import rede                      # noqa: E402 — portao_de_egresso

AQUI = Path(__file__).resolve().parent
# P5_SEMENTES / P5_SAIDA: so para o ensaio pequeno (nao toca os ficheiros da entrega).
SEMENTES = Path(os.environ.get("P5_SEMENTES") or AQUI / "SEMENTES-P5.json")
SAIDA = Path(os.environ.get("P5_SAIDA") or AQUI / "DESCOBERTA-PESSOAS-DOCENTES-V1.json")
DECISOES = AQUI / "DECISOES-P5-V1.json"
EVID = Path(os.environ.get("TEMP", "/tmp")) / "p5-evidencia"
# Filas irmas: P1, P2, YT3 e a P4 (a P4 pode ainda nao ter publicado: le-se tambem o disco dela).
BRANCHES_IRMAS = ("origin/bc4-correcoes-v1", "origin/pesquisadores-v1", "origin/pesquisadores-v2",
                  "origin/pesquisa-projetos-v1", "origin/canais-pessoas-v1", "origin/pessoas-agro-v1")
# P1d e P4b correm em paralelo (24/09) e podem nao ter publicado: le-se a fila no disco de cada bancada irma.
_WT = Path(r"C:\Users\London1\orca\workspaces\eame-sintonia")
WORKTREES_IRMAS = tuple(_WT / n for n in ("pesquisadores-v1", "pesquisadores-v2", "pessoas-agro-v1",
                                          "pesquisa-projetos-v1", "provas-p1"))
P4_ACHADOS = Path(r"C:\Users\London1\auditoria-madrugada")
PAUSA_S = 2.0
TIMEOUT_S = 20
VIGIA_A_CADA = 20   # a P4 viu a VPN cair e o vigia de 100 pedidos so parou 6 min depois
MAX_PESSOAS = 200   # IBBR tem ~160 pessoas; 80 deixou 11 do ISAFOM por ler (1.a volta)
MAX_LISTAGENS = 3


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── o que a casa ja conhece ─────────────────────────────────────────────────
def _fila_de(rev=None):
    if rev is None:
        return json.loads(FN.FILA.read_text(encoding="utf-8"))["CANDIDATAS"]
    r = subprocess.run(["git", "-C", str(RAIZ), "show", "%s:candidatas/FONTES-CANDIDATAS.json" % rev],
                       capture_output=True, text=True, encoding="utf-8")
    return json.loads(r.stdout)["CANDIDATAS"] if r.returncode == 0 else []


def conhecidos():
    """{url normalizada: onde}. Fila desta linha + irmas + fila em disco da P4 + achados da P4."""
    k = {}
    for rev in (None,) + BRANCHES_IRMAS:
        for c in _fila_de(rev):
            k.setdefault(FN.normalizar(c["URL"]), "fila %s %s" % (rev or "desta linha", c["CANDIDATA_ID"]))
    for wt in WORKTREES_IRMAS:
        f = wt / "candidatas" / "FONTES-CANDIDATAS.json"
        if f.exists():
            for c in json.loads(f.read_text(encoding="utf-8"))["CANDIDATAS"]:
                k.setdefault(FN.normalizar(c["URL"]), "fila em disco de %s %s" % (wt.name, c["CANDIDATA_ID"]))
    for j in sorted(P4_ACHADOS.glob("_p4_*.jsonl")):
        for linha in j.read_text(encoding="utf-8", errors="replace").splitlines():
            for u in re.findall(r"https?://[^\"\s]+", linha):
                if re.search(r"linkedin\.com/in/|instagram\.com/|youtube\.com/", u):
                    k.setdefault(FN.normalizar(u), "achado da P4 (%s)" % j.name)
    return k


# ── forma dos links ─────────────────────────────────────────────────────────
RE_LISTAGEM = re.compile(r"(docent|personale|persone|people|staff|rubrica|organico|ricercator|faculty|"
                         r"componenti|afferenti|il-dipartimento/person|chi-siamo/person)", re.I)
RE_PERFIL_HREF = re.compile(r"(/persone?/|/people/|/person/|/docenti?/|/personale/|/staff/|/p-doc|Show\?_id|"
                            r"/ugov/person|/rubrica/|/utenti/|/scheda|/members?/|/team/|/ricercator|"
                            r"cnr\.it/people|/it/people/|/en/people/|sitoweb/|/info/people/[\w-]+$|cercapersone_detail|"
                            r"/cris/rp/)", re.I)
RE_NOME = re.compile(r"^(?:(?:Prof|Dott|Dr|Ing)\.?(?:ssa)?\.?\s+)?"
                     r"[A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]+(?:\s+[A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]+){1,3}$")
NAV = re.compile(r"\b(home|dipartimento|contatti|ricerca|didattica|news|eventi|servizi|bandi|"
                 r"amministrazione|trasparenza|albo|privacy|cookie|mappa|laboratori|corsi|avvisi|"
                 r"personale|docenti|people|staff|login|area|accedi|seguici|english|italiano)\b", re.I)
RE_LI = re.compile(r"^https?://(?:[a-z]{2,3}\.)?linkedin\.com/in/([A-Za-z0-9\-_%]{3,100})", re.I)
RE_IG = re.compile(r"^https?://(?:www\.)?instagram\.com/([A-Za-z0-9_.]{2,30})/?(?:[?#].*)?$", re.I)
RE_YT = re.compile(r"^https?://(?:www\.|m\.)?youtube\.com/(@[\w.\-]+|channel/UC[\w-]{22}|c/[\w.\-]+|user/[\w.\-]+)",
                   re.I)
RE_RG = re.compile(r"^https?://(?:www\.)?researchgate\.net/profile/([A-Za-z0-9_\-%]+)", re.I)
IG_NAO = {"p", "reel", "reels", "explore", "accounts", "stories", "tv", "share"}


def social(url):
    """(PLATAFORMA, url canonica) ou (None, None). So o que e perfil, nunca post nem empresa."""
    m = RE_LI.match(url)
    if m:
        return "LINKEDIN", "https://www.linkedin.com/in/%s" % m.group(1).rstrip("/")
    m = RE_IG.match(url)
    if m and m.group(1).lower() not in IG_NAO:
        return "INSTAGRAM", "https://www.instagram.com/%s" % m.group(1)
    m = RE_YT.match(url)
    if m:
        return "YOUTUBE", "https://www.youtube.com/" + m.group(1)
    m = RE_RG.match(url)
    if m:
        return "RESEARCHGATE", "https://www.researchgate.net/profile/%s" % m.group(1)
    return None, None


def dominio(host):
    p = (host or "").lower().split(".")
    return ".".join(p[-2:])


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c)).lower()


def nome_casa_slug(nome, slug):
    """Quantos pedacos do nome (>=3 letras) aparecem no slug. 0 = a identidade depende so da ligacao."""
    s = sem_acento(urllib.parse.unquote(slug))
    return sum(1 for t in re.findall(r"[a-z]{3,}", sem_acento(nome))
               if t not in ("prof", "dott", "dottssa", "ing") and t in s)


# ── rede ─────────────────────────────────────────────────────────────────────
PEDIDOS = [0]


def buscar(url):
    PEDIDOS[0] += 1
    req = urllib.request.Request(url, headers={"User-Agent": D.UA, "Accept-Language": "it-IT,it;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S, context=D.CTX) as r:
            return r.status, r.geturl(), r.read(2_097_152)
    except urllib.error.HTTPError as e:
        return e.code, url, b""
    except Exception as ex:          # noqa: BLE001
        return 0, url, ("ERRO: %s" % type(ex).__name__).encode()
    finally:
        time.sleep(PAUSA_S)


def _curl(url):
    """A licao da R2: o urllib leva recusa de TLS onde o curl entra."""
    PEDIDOS[0] += 1
    r = subprocess.run(["curl", "-sS", "-L", "--max-time", str(TIMEOUT_S), "-A", D.UA, "-o", "-",
                        "-w", "\n__S__%{http_code}", url], capture_output=True)
    time.sleep(PAUSA_S)
    s = r.stdout
    k = s.rfind(b"\n__S__")
    return (0, b"") if k < 0 else (int(s[k + 6:] or 0), s[:k])


ROBOTS = {}


def robots(host):
    """(parser|None, estado). HTML com 200 ou 404/410 = sem ficheiro (permitido). urllib e depois curl."""
    if host in ROBOTS:
        return ROBOTS[host]
    url = "https://%s/robots.txt" % host
    st, _, corpo = buscar(url)
    via = "urllib"
    if st == 0 or st >= 500 or st in (401, 403):
        st, corpo = _curl(url)
        via = "curl"
    rp = urllib.robotparser.RobotFileParser()
    txt = corpo.decode("utf-8", "replace")
    if st in (404, 410) or (st == 200 and txt.lstrip().lower().startswith(("<!doctype", "<html"))):
        rp.parse([])
        r = (rp, "SEM_ROBOTS (%d, %s)" % (st, via))
    elif st == 200:
        rp.parse(txt.splitlines())
        r = (rp, "LIDO (%s)" % via)
    else:
        r = (None, "ROBOTS_ILEGIVEL (HTTP %d, %s)" % (st, via))
    ROBOTS[host] = r
    return r


def pode(url):
    host = urllib.parse.urlparse(url).hostname or ""
    rp, estado = robots(host)
    if rp is None:
        return False, estado
    return rp.can_fetch(D.UA, url), estado


def portao(onde):
    e = rede.portao_de_egresso("IT", quando=agora())
    return {"ONDE": onde, "GATE": e["EGRESS_GATE"], "PAIS": e.get("EGRESS_COUNTRY_CODE"), "QUANDO": agora()}


def portao_ou_espera(onde, portoes):
    """Portao; se BLOCKED, espera 60 s e repete ate 5 vezes. Nenhum pedido sai com egresso fora de IT."""
    for i in range(6):
        p = portao(onde if i == 0 else "%s (repeticao %d)" % (onde, i))
        portoes.append(p)
        if p["GATE"] == "PASS":
            return True
        print("  PORTAO BLOCKED (%s) — espera 60 s" % p.get("PAIS"), flush=True)
        time.sleep(60)
    return False


def pagina(url):
    """(status, url_final, texto, sha256, titulo, h1) — so se o robots deixa."""
    ok, estado = pode(url)
    if not ok:
        return {"STATUS": "ROBOTS_NEGA", "ROBOTS": estado}
    st, fim, corpo = buscar(url)
    if st != 200 or not corpo or corpo.startswith(b"ERRO"):
        st2, corpo2 = _curl(url)
        if st2 == 200 and corpo2:
            st, corpo = st2, corpo2
    txt = corpo.decode("utf-8", "replace")
    t = re.search(r"<title[^>]*>(.*?)</title>", txt, re.S | re.I)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", txt, re.S | re.I)
    limpa = lambda m: re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip()[:160] if m else ""
    sha = hashlib.sha256(corpo).hexdigest()
    if st == 200:
        EVID.mkdir(parents=True, exist_ok=True)
        (EVID / (sha[:16] + ".html")).write_bytes(corpo)
    return {"STATUS": st, "URL_FINAL": fim, "TEXTO": txt, "SHA256": sha, "TITULO": limpa(t), "H1": limpa(h1),
            "ROBOTS": estado}


def links_sociais(txt, base):
    out = {}
    for u, a in D.extrair_links(txt, base):
        p, c = social(u)
        if p:
            out.setdefault(c, (p, (a or "").strip()[:60]))
    return out


# ── descoberta ───────────────────────────────────────────────────────────────
def _grava(d):
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=False) + "\n", encoding="utf-8")


def descobrir(max_pessoas=MAX_PESSOAS, refazer=False):
    sem = json.loads(SEMENTES.read_text(encoding="utf-8"))["SEMENTES"]
    d = json.loads(SAIDA.read_text(encoding="utf-8")) if SAIDA.exists() else {
        "_LEIA": "P5 · casa -> listagem de pessoal -> pagina de cada pessoa -> links sociais. "
                 "Rota descoberta-indireta:site-da-organizacao. Evidencia (html) em %TEMP%/p5-evidencia/<sha16>.html.",
        "PORTOES": [], "SEMENTES": {}}
    if not portao_ou_espera("antes", d["PORTOES"]):
        _grava(d)
        return 2
    ultimo = PEDIDOS[0]
    for s in sem:
        host = urllib.parse.urlparse(s["URL"]).hostname
        velho = d["SEMENTES"].get(host) or {}
        lidas_antes = {p["URL"]: p for p in velho.get("PESSOAS", []) if p.get("STATUS") == 200}
        if velho.get("FIM"):
            # --refazer: so o que nao abriu, nao achou pessoas, ou deixou pessoas por ler.
            por_ler = velho.get("PESSOAS_LISTADAS", 0) > velho.get("PESSOAS_LIDAS", 0)
            if not (refazer and (velho.get("RESULTADO") in ("CASA_NAO_ABRE", "SEM_PESSOAS")
                                 or por_ler or velho.get("FAMILIA") == "CNR")):
                continue                                # ja feita (retoma depois de queda)
        r = {"URL": s["URL"], "DONO": s["DONO"], "FAMILIA": s["FAMILIA"], "INICIO": agora(),
             "LISTAGENS": [], "PESSOAS": []}
        if velho.get("FIM"):
            r["VOLTA_ANTERIOR"] = {k: velho.get(k) for k in ("INICIO", "FIM", "RESULTADO", "PESSOAS_LISTADAS",
                                                             "PESSOAS_LIDAS", "COM_SOCIAL", "CASA")}
        d["SEMENTES"][host] = r
        casa = pagina(s["URL"])
        r["CASA"] = {k: casa.get(k) for k in ("STATUS", "URL_FINAL", "SHA256", "ROBOTS")}
        if casa.get("STATUS") != 200:
            r["RESULTADO"] = "CASA_NAO_ABRE"
            r["FIM"] = agora()
            _grava(d)
            print(host, "CASA_NAO_ABRE", casa.get("STATUS"), casa.get("ROBOTS"), flush=True)
            continue
        base = casa["URL_FINAL"]
        dom = dominio(urllib.parse.urlparse(base).hostname)
        institucional = set(links_sociais(casa["TEXTO"], base))
        nav = {u.split("#")[0] for u, _ in D.extrair_links(casa["TEXTO"], base)}
        # 1) as listagens: pela ancora ou pelo caminho; docenti/ricercatori a frente
        cand = []
        for u, a in D.extrair_links(casa["TEXTO"], base):
            u = u.split("#")[0]
            h = urllib.parse.urlparse(u).hostname or ""
            if dominio(h) != dom or not RE_LISTAGEM.search(u + " " + (a or "")):
                continue
            if re.search(r"\.(pdf|docx?|xlsx?)$|amministrativ|tecnico-ammin|/news|bando|concors", u, re.I):
                continue
            pri = 0 if re.search(r"docent|ricercator|faculty|people|persone", u + " " + (a or ""), re.I) else 1
            cand.append((pri, u, (a or "").strip()[:60]))
        vistos, listagens = set(), []
        for pri, u, a in sorted(cand):
            if u not in vistos and u.rstrip("/") != base.rstrip("/"):
                vistos.add(u)
                listagens.append((u, a))
        pessoas = {}
        for u, a in listagens[:MAX_LISTAGENS]:
            lp = pagina(u)
            r["LISTAGENS"].append({"URL": u, "ANCORA": a, "STATUS": lp.get("STATUS"), "SHA256": lp.get("SHA256"),
                                   "ROBOTS": lp.get("ROBOTS")})
            if lp.get("STATUS") != 200:
                continue
            institucional |= set(links_sociais(lp["TEXTO"], lp["URL_FINAL"]))
            for pu, pa in D.extrair_links(lp["TEXTO"], lp["URL_FINAL"]):
                pu = pu.split("#")[0]
                pa = re.sub(r"\s+", " ", (pa or "")).strip()
                h = urllib.parse.urlparse(pu).hostname or ""
                if dominio(h) != dom or pu in nav or pu == u or re.search(r"\.(pdf|docx?|jpe?g|png)$", pu, re.I):
                    continue
                nome_ok = bool(RE_NOME.match(pa)) and not NAV.search(pa) and len(pa) <= 60
                # 2.a volta: IBBA liga a pessoa por imagem (ancora vazia) e IBBR poe a ficha inteira na
                # ancora (>60 letras). O caminho da pessoa chega; o nome le-se depois no H1 da pagina.
                if nome_ok or (RE_PERFIL_HREF.search(pu) and not NAV.search(pa[:60])):
                    if pa and not nome_ok:
                        pa = " ".join(pa.split()[:3])
                    if pu not in pessoas or (pa and not pessoas[pu]):
                        pessoas[pu] = pa
        r["PESSOAS_LISTADAS"] = len(pessoas)
        # 2) a pagina de cada pessoa
        for pu, pa in list(pessoas.items())[:max_pessoas]:
            if PEDIDOS[0] - ultimo >= VIGIA_A_CADA:
                ultimo = PEDIDOS[0]
                if not portao_ou_espera("vigia %s" % host, d["PORTOES"]):
                    _grava(d)
                    return 2
            if pu in lidas_antes:                       # lida na volta anterior: nao se pede outra vez
                r["PESSOAS"].append(dict(lidas_antes[pu], SOCIAIS=lidas_antes[pu].get("SOCIAIS_BRUTOS",
                                                                                      lidas_antes[pu].get("SOCIAIS", []))))
                continue
            pp = pagina(pu)
            reg = {"URL": pu, "ANCORA": pa, "STATUS": pp.get("STATUS"), "SHA256": pp.get("SHA256"),
                   "TITULO": pp.get("TITULO"), "H1": pp.get("H1"), "QUANDO": agora()}
            if pp.get("STATUS") == 200:
                reg["SOCIAIS"] = [{"URL": c, "PLATAFORMA": p, "ANCORA": a}
                                  for c, (p, a) in links_sociais(pp["TEXTO"], pp["URL_FINAL"]).items()
                                  if c not in institucional]
                reg["SOCIAIS_BRUTOS"] = list(reg["SOCIAIS"])
            r["PESSOAS"].append(reg)
        # 3) o rodape: o que se repete em >= 3 pessoas e da casa
        rep = Counter(x["URL"] for p in r["PESSOAS"] for x in p.get("SOCIAIS", []))
        r["INSTITUCIONAIS"] = sorted(institucional | {u for u, n in rep.items() if n >= 3})
        for p in r["PESSOAS"]:
            p["SOCIAIS"] = [x for x in p.get("SOCIAIS", []) if x["URL"] not in r["INSTITUCIONAIS"]]
        r["PESSOAS_LIDAS"] = sum(1 for p in r["PESSOAS"] if p["STATUS"] == 200)
        r["COM_SOCIAL"] = sum(1 for p in r["PESSOAS"] if p.get("SOCIAIS"))
        r["RESULTADO"] = "LIDA" if r["PESSOAS_LIDAS"] else ("SEM_LISTAGEM" if not listagens else "SEM_PESSOAS")
        r["FIM"] = agora()
        _grava(d)
        print(host, r["RESULTADO"], "listagens", len(listagens), "pessoas", r["PESSOAS_LISTADAS"],
              "lidas", r["PESSOAS_LIDAS"], "com_social", r["COM_SOCIAL"], "pedidos", PEDIDOS[0], flush=True)
    ok = portao_ou_espera("depois", d["PORTOES"])
    d["PEDIDOS_DESTA_CORRIDA"] = PEDIDOS[0]
    _grava(d)
    return 0 if ok else 2


def achados():
    """Uma linha por (pessoa, perfil), com JA_CONHECIDO medido contra a casa inteira."""
    d = json.loads(SAIDA.read_text(encoding="utf-8"))
    k = conhecidos()
    out = []
    for host, s in d["SEMENTES"].items():
        for p in s.get("PESSOAS", []):
            for x in p.get("SOCIAIS", []):
                nome = p.get("H1") or p.get("ANCORA") or p.get("TITULO")
                slug = x["URL"].rstrip("/").rsplit("/", 1)[-1]
                out.append({"URL": x["URL"], "PLATAFORMA": x["PLATAFORMA"], "PESSOA": nome,
                            "ANCORA_NA_LISTAGEM": p.get("ANCORA"), "PAGINA_OFICIAL": p["URL"],
                            "PAGINA_SHA256": p.get("SHA256"), "QUANDO": p.get("QUANDO"), "SEMENTE": host,
                            "DONO": s["DONO"], "FAMILIA": s["FAMILIA"],
                            "NOME_NO_SLUG": nome_casa_slug(p.get("ANCORA") or nome, slug),
                            "JA_CONHECIDO": k.get(FN.normalizar(x["URL"]))})
    return out


# ── registo ──────────────────────────────────────────────────────────────────
def registar():
    """Porta canonica. So entra o que DECISOES-P5-V1.json diz ENTRA, com a prova na NOTA."""
    dec = {x["URL"]: x for x in json.loads(DECISOES.read_text(encoding="utf-8"))["DECISOES"]}
    k = conhecidos()
    novas, ja = [], []
    for a in achados():
        x = dec.get(a["URL"])
        if not x or x["DECISAO"] != "ENTRA":
            continue
        if a["JA_CONHECIDO"] or k.get(FN.normalizar(a["URL"])):
            ja.append(a["URL"])
            continue
        host = urllib.parse.urlparse(a["PAGINA_OFICIAL"]).hostname or ""
        pais = "IT" if host.endswith(".it") else "NAO SEI"
        nota = ("P5 D24 · IDENTIDADE: a pagina oficial da pessoa %s (sha256 %s, lida %s; titulo «%s») liga a este "
                "perfil %s — descoberta-indireta:site-da-organizacao · TERRITORIO: %s (dominio oficial %s) · "
                "PESSOA: %s · CASA: %s (%s) · NOME NO ENDERECO: %d pedaco(s) · %s") % (
            a["PAGINA_OFICIAL"], (a["PAGINA_SHA256"] or "?")[:16], (a["QUANDO"] or "")[:10],
            (a["PESSOA"] or "")[:80], a["PLATAFORMA"], pais, host, x["PESSOA"], a["DONO"], a["FAMILIA"],
            a["NOME_NO_SLUG"], x["PORQUE"])
        antes = FN.carregar()["TOTAL"]
        linha = FN.registar(tipo=a["PLATAFORMA"], pais=pais, nome="%s — %s" % (x["PESSOA"], a["DONO"]),
                            url=a["URL"], para_que=x["PARA_QUE"],
                            quem_viu="scripts/pessoas_docentes/pessoas_docentes.py (P5)",
                            onde_viu=a["PAGINA_OFICIAL"], nota=nota)
        if FN.carregar()["TOTAL"] > antes:
            novas.append(linha["CANDIDATA_ID"])
        else:
            ja.append(a["URL"])
    print("novas", len(novas), novas, "· ja estavam", len(ja))
    return 0


def resumo():
    d = json.loads(SAIDA.read_text(encoding="utf-8"))
    S = d["SEMENTES"].values()
    print("sementes", len(d["SEMENTES"]), Counter(s.get("RESULTADO") for s in S))
    print("pessoas lidas", sum(s.get("PESSOAS_LIDAS", 0) for s in S),
          "com social", sum(s.get("COM_SOCIAL", 0) for s in S))
    A = achados()
    print("achados", len(A), Counter(a["PLATAFORMA"] for a in A),
          "ja conhecidos", sum(1 for a in A if a["JA_CONHECIDO"]))
    print("portoes", Counter((p["GATE"], p["PAIS"]) for p in d["PORTOES"]))
    for a in A:
        print(" ", a["PLATAFORMA"], a["URL"], "|", (a["PESSOA"] or "")[:40], "|", a["SEMENTE"],
              "| slug", a["NOME_NO_SLUG"], "|", a["JA_CONHECIDO"] or "")
    return 0


def main():
    a = sys.argv[1:]
    mx = next((int(x.split("=")[1]) for x in a if x.startswith("--max-pessoas=")), MAX_PESSOAS)
    if "--descobrir" in a:
        return descobrir(mx, refazer="--refazer" in a)
    if "--registar" in a:
        return registar()
    if "--resumo" in a:
        return resumo()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
