#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O QUE JA SABEMOS — a linha de base contra a qual toda descoberta nova e medida.

Sem isto, a proxima rodada de pesquisa devolve as mesmas fontes com nomes
diferentes e a planilha cresce sem que o acervo cresca. Por isso o primeiro
trabalho desta missao nao e procurar: e MEDIR o que ja esta no repositorio.

Le todo catalogo de fonte que existe hoje (nesta branch e nas branches irmas
que guardaram a rodada de 2026-09-14), normaliza o endereco, e grava:

    KNOWN-BASELINE.json   { urls, hosts, owners, nomes, canais_sociais }

A chave de deduplicacao e o URL normalizado — a mesma regra de
`candidatas/fonte_nova.py::normalizar`, para que as duas portas concordem.
Guarda tambem o HOST, porque a mesma fonte aparece com dez caminhos
diferentes e o host e o que denuncia que o dono e o mesmo.

NAO decide nada. So conta.
"""

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "candidatas"

# As branches irmas que guardaram a rodada anterior. Nao se le o ficheiro do
# disco delas (nao existe aqui): le-se o blob pelo git, sem trocar de branch.
BRANCHES_IRMAS = [
    ("origin/claude/italy-source-qualification-v1", "candidatas/ITALY-SOURCE-IMPORT-2026-09-14.csv"),
    ("origin/claude/italy-source-qualification-v1", "candidatas/ITALY-SOURCE-FIRST-WAVE-2026-09-14.csv"),
]

URL_RE = re.compile(r"https?://[^\s\"'<>)\]\},;]+", re.I)


def normalizar(url: str) -> str:
    """A mesma chave de fonte_nova.py. Duas portas, uma chave."""
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = u.split("#")[0]
    return u.rstrip("/")


def host(url: str) -> str:
    n = normalizar(url)
    return n.split("/")[0].split("?")[0]


def urls_do_texto(texto: str):
    for m in URL_RE.finditer(texto):
        u = m.group(0).rstrip(".,;:)]}»\"'")
        if u:
            yield u


def ler_ficheiro(p: Path):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def ler_blob(branch: str, caminho: str) -> str:
    try:
        r = subprocess.run(["git", "show", f"{branch}:{caminho}"],
                           cwd=RAIZ, capture_output=True, timeout=60)
        return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else ""
    except Exception:
        return ""


def main() -> int:
    conhecido = {
        "urls": {},        # url normalizado -> [de onde veio]
        "hosts": {},       # host -> contagem
        "owners": set(),
        "nomes": set(),
        "social": {},      # plataforma -> {handle}
    }

    def poe_url(u: str, origem: str):
        n = normalizar(u)
        if not n or "." not in n.split("/")[0]:
            return
        conhecido["urls"].setdefault(n, [])
        if origem not in conhecido["urls"][n]:
            conhecido["urls"][n].append(origem)
        h = host(u)
        conhecido["hosts"][h] = conhecido["hosts"].get(h, 0) + 1
        for plat, marca in (("INSTAGRAM", "instagram.com"), ("YOUTUBE", "youtube.com"),
                            ("LINKEDIN", "linkedin.com"), ("FACEBOOK", "facebook.com"),
                            ("X", "twitter.com"), ("TIKTOK", "tiktok.com")):
            if marca in h:
                handle = "/".join(n.split("/")[1:3])
                if handle:
                    conhecido["social"].setdefault(plat, set()).add(handle.lower())

    # 1 · o master da rodada anterior: donos e fontes declarados
    master = RAIZ / "candidatas" / "ITALY-SOURCE-MASTER-V1.json"
    if master.exists():
        d = json.loads(master.read_text(encoding="utf-8"))
        for o in d.get("owners", []):
            nome = o.get("owner_name") or o.get("name") or o.get("OWNER")
            if nome:
                conhecido["owners"].add(str(nome).strip())
            for k in ("url", "URL", "homepage", "site"):
                if o.get(k):
                    poe_url(str(o[k]), "MASTER-V1/owners")
        for s in d.get("sources", []):
            nome = s.get("source_name") or s.get("name") or s.get("NOME")
            if nome:
                conhecido["nomes"].add(str(nome).strip())
            own = s.get("owner") or s.get("owner_name")
            if own:
                conhecido["owners"].add(str(own).strip())
            for k in ("url", "URL", "url_canonical", "URL_CANONICAL", "endpoint", "route"):
                if s.get(k):
                    poe_url(str(s[k]), "MASTER-V1/sources")
        for u in urls_do_texto(master.read_text(encoding="utf-8")):
            poe_url(u, "MASTER-V1/varredura")

    # 2 · a fila de candidatas canonica (nas duas moradas que o repo ja usou)
    for rel in ("candidatas/FONTES-CANDIDATAS.json",
                "data/samples/FONTES-CANDIDATAS.json"):
        p = RAIZ / rel
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            for c in d.get("CANDIDATAS", []):
                if c.get("URL"):
                    poe_url(c["URL"], "FILA/" + rel)
                if c.get("NOME"):
                    conhecido["nomes"].add(c["NOME"].strip())

    # 3 · o atlas e o indice: as fontes que ja tem ficha
    for rel in ("docs/fontes/ATLAS-DE-FONTES-EAME.md",
                "docs/fontes/INDICE-DE-FONTES.md",
                "docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md",
                "docs/fontes/SOURCE-PACK-ESPANHA-CIENCIA-E-VOZ.md",
                "candidatas/ITALY-SOURCE-MASTER-V1.md"):
        p = RAIZ / rel
        if p.exists():
            for u in urls_do_texto(ler_ficheiro(p)):
                poe_url(u, "ATLAS/" + Path(rel).name)

    # 4 · contas publicas ja mapeadas (o universo social conhecido)
    for rel in ("data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json",
                "data/samples/COMPETITOR-PUBLIC-COMM/UNIVERSO-CONTAS-V1.json"):
        p = RAIZ / rel
        if p.exists():
            txt = ler_ficheiro(p)
            for u in urls_do_texto(txt):
                poe_url(u, "CONTAS/" + Path(rel).name)
            try:
                d = json.loads(txt)
            except Exception:
                d = None

            def anda(x):
                if isinstance(x, dict):
                    plat = x.get("PLATAFORMA") or x.get("platform") or x.get("PLATFORM")
                    hand = x.get("HANDLE") or x.get("handle") or x.get("CONTA")
                    if plat and hand:
                        conhecido["social"].setdefault(str(plat).upper(), set()).add(
                            str(hand).lstrip("@").lower())
                    nm = x.get("OWNER") or x.get("owner") or x.get("EMPRESA")
                    if nm:
                        conhecido["owners"].add(str(nm).strip())
                    for v in x.values():
                        anda(v)
                elif isinstance(x, list):
                    for v in x:
                        anda(v)
            if d is not None:
                anda(d)

    # 5 · todo catalogo de fonte espalhado por research/ e build/
    padroes = ["research/**/*SOURCE*.json", "research/**/*SOURCE*.md",
               "research/**/*FONTES*.md", "build/**/*SOURCE*.json",
               "build/**/*sources*.json", "build/**/*SOURCES*.md",
               "build/**/*FONTES*.md"]
    for pad in padroes:
        for p in RAIZ.glob(pad):
            for u in urls_do_texto(ler_ficheiro(p)):
                poe_url(u, "ACERVO/" + p.relative_to(RAIZ).as_posix())

    # 6 · a rodada de 2026-09-14, que vive nas branches irmas
    for branch, caminho in BRANCHES_IRMAS:
        txt = ler_blob(branch, caminho)
        if not txt:
            continue
        origem = "RODADA-2026-09-14/" + Path(caminho).name
        rdr = csv.DictReader(txt.splitlines())
        for row in rdr:
            for k in ("URL", "URL_CANONICAL", "URL_FINAL"):
                if row.get(k):
                    poe_url(row[k], origem)
            for k in ("NOME", "NAME"):
                if row.get(k):
                    conhecido["nomes"].add(row[k].strip())
            if row.get("OWNER"):
                conhecido["owners"].add(row["OWNER"].strip())

    # 7 · as palavras de busca ja medidas no codigo (nao sao fonte, mas dizem
    #     onde a casa ja procurou — evita repetir busca ja feita)
    saida = {
        "ARTIFACT": "ITALY-DEEP-SOURCE-KNOWN-BASELINE",
        "GERADO_POR": "candidatas/italy_deep_baseline.py",
        "REGRA": ("chave = URL normalizado (a mesma de fonte_nova.py). "
                  "HOST guardado em separado porque a mesma fonte aparece com "
                  "muitos caminhos e o host denuncia o dono repetido."),
        "KNOWN_URLS": len(conhecido["urls"]),
        "KNOWN_HOSTS": len(conhecido["hosts"]),
        "KNOWN_OWNERS": len(conhecido["owners"]),
        "KNOWN_NOMES": len(conhecido["nomes"]),
        "KNOWN_SOCIAL": {k: len(v) for k, v in conhecido["social"].items()},
        "urls": conhecido["urls"],
        "hosts": conhecido["hosts"],
        "owners": sorted(conhecido["owners"]),
        "nomes": sorted(conhecido["nomes"]),
        "social": {k: sorted(v) for k, v in conhecido["social"].items()},
    }
    SAIDA.mkdir(parents=True, exist_ok=True)
    alvo = SAIDA / "KNOWN-BASELINE.json"
    alvo.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"BASELINE={alvo}")
    print(f"  KNOWN_URLS={saida['KNOWN_URLS']}")
    print(f"  KNOWN_HOSTS={saida['KNOWN_HOSTS']}")
    print(f"  KNOWN_OWNERS={saida['KNOWN_OWNERS']}")
    print(f"  KNOWN_NOMES={saida['KNOWN_NOMES']}")
    print(f"  KNOWN_SOCIAL={saida['KNOWN_SOCIAL']}")
    print("  hosts mais repetidos:")
    for h, n in sorted(conhecido["hosts"].items(), key=lambda kv: -kv[1])[:15]:
        print(f"    {n:4d}  {h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
