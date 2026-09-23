"""D18 · LINKEDIN = A + B — O CONTEUDO VEM PELO SITE DA PROPRIA ORGANIZACAO.

    py curadoria/linkedin_pelo_site.py              # so mede e mostra
    py curadoria/linkedin_pelo_site.py --escrever   # candidata os sites que faltam

A D18 (bot Luciano, 23/09) decidiu: do LinkedIn entra o ENDERECO (catalogo, A) e o
CONTEUDO entra pelo SITE de cada organizacao (B), pela coleta HTML canonica, US$ 0.

Cada uma das 44 candidatas LinkedIn traz, em `ONDE_VIU`, o site onde a propria
organizacao declara a pagina («declarado no site oficial do dono: https://…»).
E esse site — e so esse — que aqui se procura na casa:

    NA_TABELA_DO_COLETOR    o host esta num contrato da tabela do coletor
                            (`regras/italy_contracts_onboarded.json`): ja se colhe.
    SO_NO_LIVRO_DO_CURATOR  tem contrato no livro do Curator, ainda nao na tabela.
    SO_NO_ATLAS             o Atlas conhece o host, sem contrato.
    JA_CANDIDATA            ja esta na porta de candidatas com outro tipo.
    AUSENTE                 a casa nao o conhece: candidata-se pela porta normal
                            (`fonte_nova.registar`), e o circuito do Curator decide.
    SEM_SITE_NA_FICHA       a ficha nao diz o site: NAO SEI, sem inventar.

A comparacao e pelo HOST exacto (sem `www.`). Um subdominio diferente
(`appa.provincia.tn.it` × `provincia.tn.it`) NAO conta como o mesmo site: o
dominio registavel parecido fica escrito ao lado (`PARECIDO_COM`) para um
humano ver, e nao decide nada.

    O MESMO DONO NAO E O MESMO SITE.

Nada aqui toca no LinkedIn, e nada aqui toca no Scrap. `--escrever` so chama a
porta das candidatas, que e idempotente pela URL normalizada.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "candidatas"))
import fonte_nova as FN  # noqa: E402

TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"
LIVRO = RAIZ / "curadoria" / "italy_contracts_curator.json"
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"

QUEM_VIU = "SOC2 · D18 (LinkedIn A+B): site declarado pela organizacao na candidata LinkedIn"
RE_URL = re.compile(r"https?://[^\s)>|`\"'<]+")
SOCIAIS = ("LINKEDIN", "INSTAGRAM", "YOUTUBE", "FACEBOOK")


def host(url: str) -> str:
    u = (url or "").strip()
    h = urlparse(u if "://" in u else "https://" + u).hostname or ""
    return re.sub(r"^www\.", "", h.lower())


def registavel(h: str) -> str:
    """Os dois ultimos rotulos — so para mostrar o parecido, nunca para decidir."""
    p = h.split(".")
    return ".".join(p[-2:]) if len(p) >= 2 else h


def site_da_ficha(c: dict) -> str | None:
    m = RE_URL.search(c.get("ONDE_VIU") or "")
    return m.group(0).rstrip(".,;") if m else None


def _hosts_dos_contratos(caminho: Path) -> dict[str, set]:
    d = json.loads(caminho.read_text(encoding="utf-8"))
    fontes = d["FONTES"] if isinstance(d, dict) else d
    out: dict[str, set] = {}
    for x in fontes:
        s = json.dumps(x.get("ACQUISITION") or {}) + " " + str(x.get("CANONICAL_ENTRY_URL") or "")
        for u in RE_URL.findall(s):
            out.setdefault(host(u), set()).add(x["SOURCE_ID"])
    return out


def _atlas_por_host(texto: str) -> dict[str, set]:
    """host -> SOURCE_IDs das fichas do Atlas (`#### IT-Tx-nnn`) onde o host aparece.
    Um host no Atlas sem SOURCE_ID ao lado conta como conhecido, com conjunto vazio."""
    out: dict[str, set] = {}
    sid = None
    for linha in texto.splitlines():
        m = re.match(r"^#### ([A-Z]{2}-T\d+-\d+)", linha)
        if m:
            sid = m.group(1)
        for u in RE_URL.findall(linha):
            out.setdefault(host(u), set()).update({sid} if sid else set())
    return out


def _estado_no_livro(sid: str) -> str:
    try:
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import lifecycle as LC
        return LC.estado_de(sid) or "NAO SEI"
    except Exception as e:  # noqa: BLE001
        return "NAO SEI (%s)" % type(e).__name__


def medir(candidatas: dict | None = None, tabela: dict | None = None,
          livro: dict | None = None, atlas: dict | None = None,
          estado_de=None) -> list[dict]:
    cand = FN.carregar() if candidatas is None else candidatas
    tabela = _hosts_dos_contratos(TABELA) if tabela is None else tabela
    livro = _hosts_dos_contratos(LIVRO) if livro is None else livro
    if atlas is None:
        atlas = _atlas_por_host(ATLAS.read_text(encoding="utf-8"))
    estado_de = _estado_no_livro if estado_de is None else estado_de
    sids_tabela = {s for v in tabela.values() for s in v}
    sids_livro = {s for v in livro.values() for s in v}
    outras = {host(c["URL"]): c["CANDIDATA_ID"] for c in cand["CANDIDATAS"]
              if c.get("TIPO") not in SOCIAIS}
    conhecidos = set(tabela) | set(livro) | set(atlas) | set(outras)
    linhas = []
    for c in cand["CANDIDATAS"]:
        if c.get("TIPO") != "LINKEDIN":
            continue
        site = site_da_ficha(c)
        l = {"CANDIDATA_ID": c["CANDIDATA_ID"], "NOME": c.get("NOME", ""),
             "LINKEDIN": c.get("URL"), "SITE": site, "PAIS": c.get("PAIS") or "NAO SEI"}
        if not site:
            l.update(ESTADO="SEM_SITE_NA_FICHA", PORQUE="ONDE_VIU nao traz o site: NAO SEI")
        else:
            h = host(site)
            l["HOST"] = h
            if h in tabela:
                l.update(ESTADO="NA_TABELA_DO_COLETOR", SOURCE_IDS=sorted(tabela[h]))
            elif h in livro:
                l.update(ESTADO="SO_NO_LIVRO_DO_CURATOR", SOURCE_IDS=sorted(livro[h]))
            elif h in atlas and atlas[h] & sids_tabela:
                # o contrato usa outro endereco do mesmo site; o Atlas liga os dois
                l.update(ESTADO="NA_TABELA_DO_COLETOR", SOURCE_IDS=sorted(atlas[h] & sids_tabela),
                         VIA="Atlas")
            elif h in atlas and atlas[h] & sids_livro:
                l.update(ESTADO="SO_NO_LIVRO_DO_CURATOR", SOURCE_IDS=sorted(atlas[h] & sids_livro),
                         VIA="Atlas")
            elif h in atlas:
                l.update(ESTADO="SO_NO_ATLAS", SOURCE_IDS=sorted(atlas[h]))
            elif h in outras:
                l.update(ESTADO="JA_CANDIDATA", CANDIDATA_DO_SITE=outras[h])
            else:
                l.update(ESTADO="AUSENTE")
            parecidos = sorted(k for k in conhecidos
                               if k != h and registavel(k) == registavel(h))
            if parecidos and l["ESTADO"] == "AUSENTE":
                l["PARECIDO_COM"] = parecidos[:5]
        if l["ESTADO"] in ("SO_NO_LIVRO_DO_CURATOR", "SO_NO_ATLAS") and l.get("SOURCE_IDS"):
            # Por que o contrato nao chegou a tabela: o livro de estado responde.
            l["ESTADO_NO_LIVRO"] = {s: estado_de(s) for s in l["SOURCE_IDS"]}
        linhas.append(l)
    return linhas


def candidatar(linhas: list[dict], registar=None) -> list[dict]:
    """So as AUSENTE, pela porta normal. Idempotente: a porta devolve a que ja existia."""
    registar = FN.registar if registar is None else registar
    feitas = []
    for l in linhas:
        if l["ESTADO"] != "AUSENTE":
            continue
        nome = l["NOME"].split("—")[0].strip() + " — sito ufficiale"
        r = registar("ORGANIZACAO", l["PAIS"] if l["PAIS"] in FN.PAISES else "NAO SEI",
                     nome, l["SITE"],
                     "D18 (LinkedIn A+B): o conteudo que a organizacao publica chega pelo "
                     "site dela, pela coleta HTML canonica, em vez do LinkedIn",
                     QUEM_VIU, onde_viu="candidata LinkedIn %s (%s)" % (l["CANDIDATA_ID"], l["LINKEDIN"]),
                     nota="D18/SOC2. Site declarado pela propria organizacao; o circuito do Curator decide.")
        feitas.append({"CANDIDATA_LINKEDIN": l["CANDIDATA_ID"], "SITE": l["SITE"],
                       "CANDIDATA_DO_SITE": r["CANDIDATA_ID"]})
    return feitas


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    linhas = medir()
    for l in linhas:
        print("%-22s %-10s %-34s %s %s" % (l["ESTADO"], l["CANDIDATA_ID"], (l.get("HOST") or "—")[:34],
                                           ",".join(l.get("SOURCE_IDS", [])) or l.get("CANDIDATA_DO_SITE", "")
                                           or ",".join(l.get("PARECIDO_COM", [])),
                                           ",".join("%s" % v for v in (l.get("ESTADO_NO_LIVRO") or {}).values())))
    print("RESUMO", dict(Counter(l["ESTADO"] for l in linhas)), "de", len(linhas))
    if "--escrever" in argv:
        feitas = candidatar(linhas)
        print("CANDIDATADAS", len(feitas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
