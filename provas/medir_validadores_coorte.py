"""R2 · VALE A PENA O ETag? — medir, nos 8 sites da coorte da micro-coleta, se
o servidor oferece um VALIDADOR (ETag ou Last-Modified) na pagina de indice.

    py provas/medir_validadores_coorte.py            # mede e escreve o JSON

PORQUE SO O INDICE. A regra de hoje decide sem bytes e ja da 0 pedidos as
materias conhecidas (provado em provas/recollection_indice_local.mjs). O que
se pede em TODAS as corridas e o indice — e, nas fontes declaradas MUTABLE,
as materias revalidadas. Um validador so poupa corpo onde ha pedido repetido.

TRAVAS (briefing R2): egresso medido ANTES de cada site e paragem se nao for
IT; robots.txt lido e respeitado; UM pedido HEAD por site a pagina de indice
(mais a leitura do robots.txt, que e a propria trava). Sem GET, sem corpo, sem
pedido condicional: um 304 so se provaria com um segundo pedido, e o briefing
da um. Nada escrito no armazem, no livro ou na Sala.

⚠️ O INDICE E UM INDICADOR DO SERVIDOR, NAO DE CADA PAGINA. Um CMS pode dar
ETag ao indice e nao as materias, ou o contrario. O resultado diz «este
servidor emite validador nesta pagina», e mais nada.
"""
import json
import subprocess
import sys
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")   # o do coletor
SAIDA = Path(__file__).with_name("VALIDADORES-COORTE-R2.json")

# Os 8 da coorte (RELATORIO-DESBLOQUEIO-COORTE.md: PASSAM_TUDO = 8). O
# INDEX_URL e o do contrato nesta linha; IT-T2-051 ainda nao tem contrato aqui
# (chega no cutover pelo pacote G1) e o endereco e o da rota provada da M3
# (origin/rotas-elegiveis-v1:curadoria/ROTAS-ELEGIVEIS-V1.json).
COORTE = [
    ("IT-T10-018", "https://www.myfruit.it/", 30, None),
    ("IT-T10-021", "https://plantgest.imagelinenetwork.com/", 1, None),
    ("IT-T10-022", "https://zootecnicainternational.com/news/", 14, "MUTABLE"),
    ("IT-T2-051", "https://www.arpae.it/it", None, None),
    ("IT-T7-017", "https://www.riuniteciv.com/news-e-eventi/", 30, "MUTABLE"),
    ("IT-T7-033", "https://www.chianticlassico.com/news/", 15, None),
    ("IT-T7-041", "https://www.bonificaromagna.it/news", 7, None),
    ("IT-T7-043", "https://agrofarma.federchimica.it/news-ed-eventi", 2, None),
]


def egresso():
    r = subprocess.run(["curl", "-s", "--max-time", "15", "https://ipinfo.io/json"],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        return d.get("country"), d.get("ip"), d.get("city")
    except ValueError:
        return None, None, None


def robots_permite(url):
    """Le o robots.txt com o MESMO User-Agent do coletor, pelo curl.

    ⚠️ A PRIMEIRA VERSAO USAVA `RobotFileParser.read()`, que bate a porta como
    «Python-urllib». O servidor da Agrofarma recusa esse cliente, e o leitor
    le a recusa como «Disallow: /» — deu IT-T7-043 como barrada, quando o host
    nem publica robots.txt (404, que pela norma e «tudo permitido»). Um
    instrumento que se apresenta com outro nome mede outra porta."""
    p = urlsplit(url)
    r = subprocess.run(["curl", "-sS", "-L", "--max-time", "30", "-A", UA, "-o", "-",
                        "-w", "\n__S__%{http_code}", f"{p.scheme}://{p.netloc}/robots.txt"],
                       capture_output=True)
    s = r.stdout.decode("utf-8", "replace")
    k = s.rfind("\n__S__")
    if r.returncode != 0 or k < 0:
        return None, f"robots ilegivel (curl rc={r.returncode})"
    status, corpo = int(s[k + 6:] or 0), s[:k]
    if status in (401, 403):
        return False, f"robots HTTP {status} — tratado como barrado"
    if 400 <= status < 500:
        return True, f"robots HTTP {status} — o host nao publica robots.txt (tudo permitido)"
    if status != 200:
        return None, f"robots HTTP {status} — UNKNOWN, tratado como barrado por prudencia"
    if corpo.lstrip().lower().startswith(("<!doctype", "<html")):
        return None, "robots devolve HTML com 200 — ilegivel, tratado como barrado por prudencia"
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(corpo.splitlines())
    return rp.can_fetch("*", url), "lido"


def head(url):
    r = subprocess.run(["curl", "-sS", "-I", "-L", "--max-time", "30", "-A", UA,
                        "-H", "Accept-Language: it-IT,it;q=0.9", url],
                       capture_output=True)
    texto = r.stdout.decode("latin1")
    # com -L vem um bloco por salto; o que conta e o ultimo
    blocos = [b for b in texto.replace("\r\n", "\n").split("\n\n") if b.strip().startswith("HTTP/")]
    if not blocos:
        return {"ERRO": (r.stderr.decode("latin1") or f"curl rc={r.returncode}").strip()[:200]}
    linhas = blocos[-1].strip().split("\n")
    cab = {}
    for l in linhas[1:]:
        if ":" in l:
            k, v = l.split(":", 1)
            cab[k.strip().lower()] = v.strip()
    return {"STATUS": linhas[0].split()[1] if len(linhas[0].split()) > 1 else "NAO SEI",
            "SALTOS": len(blocos) - 1,
            "ETAG": cab.get("etag"), "LAST_MODIFIED": cab.get("last-modified"),
            "CACHE_CONTROL": cab.get("cache-control"), "CONTENT_LENGTH": cab.get("content-length"),
            "SERVER": cab.get("server")}


def main():
    # `--apenas=ID,ID` volta a medir so esses e junta ao JSON que ja existe
    apenas = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--apenas=")), None)
    antigos = {}
    if apenas and SAIDA.exists():
        antigos = {l["SOURCE_ID"]: l for l in json.loads(SAIDA.read_text(encoding="utf-8"))["SITES"]}
    linhas = []
    for sid, url, maxt, rec in COORTE:
        if apenas and sid not in apenas:
            if sid in antigos:
                linhas.append(antigos[sid])
            continue
        pais, ip, cidade = egresso()
        if pais != "IT":
            print(f"PARADO antes de {sid}: egresso {pais} {ip} {cidade} — nao e IT")
            linhas.append({"SOURCE_ID": sid, "INDEX_URL": url, "RESULTADO": "NAO_MEDIDO_EGRESSO_NAO_IT",
                           "EGRESSO": [pais, ip, cidade]})
            break
        ok, porque = robots_permite(url)
        if ok is not True:
            linhas.append({"SOURCE_ID": sid, "INDEX_URL": url, "RESULTADO": "NAO_MEDIDO_ROBOTS",
                           "ROBOTS": porque if ok is None else "barrado", "EGRESSO": [pais, ip, cidade]})
            print(f"{sid:11} robots: {porque if ok is None else 'barrado'} — nao pedido")
            continue
        h = head(url)
        val = bool(h.get("ETAG") or h.get("LAST_MODIFIED"))
        linhas.append({"SOURCE_ID": sid, "INDEX_URL": url, "MAX_TARGETS": maxt, "RECOLLECTION": rec,
                       "ROBOTS": porque, "EGRESSO": [pais, ip, cidade], "HEAD": h,
                       "RESULTADO": "ERRO" if "ERRO" in h else ("COM_VALIDADOR" if val else "SEM_VALIDADOR")})
        print(f"{sid:11} {h.get('STATUS', 'ERRO'):>4}  ETag={bool(h.get('ETAG'))!s:5} "
              f"Last-Modified={bool(h.get('LAST_MODIFIED'))!s:5}  {url}")
    com = sum(1 for l in linhas if l["RESULTADO"] == "COM_VALIDADOR")
    medidos = sum(1 for l in linhas if l["RESULTADO"] in ("COM_VALIDADOR", "SEM_VALIDADOR"))
    out = {"DATASET": "VALIDADORES-COORTE-R2", "MISSAO": "R2 recollection-prova-v2",
           "MEDIDO_EM": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "METODO": "1 HEAD por site ao INDEX_URL (curl -I -L, UA do coletor) + robots.txt; egresso IT antes de cada site",
           "LIMITE": "o indice indica o servidor, nao cada pagina; sem pedido condicional nao se prova 304",
           "COORTE": len(COORTE), "MEDIDOS": medidos, "COM_VALIDADOR": com, "SITES": linhas}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\nCOM_VALIDADOR {com}/{len(COORTE)} (medidos {medidos}) -> {SAIDA.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
