"""Descoberta controlada RESEARCH-MEDIA-SOURCES-V1: robots.txt primeiro, teto 3 pedidos por dominio,
pausa 4 s, sem cookie/login. Guarda cada resposta em prova/ com sha256 e um registo PEDIDOS.jsonl."""
import hashlib, json, sys, time, urllib.parse, urllib.request, urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
AQUI = Path(__file__).resolve().parent
PROVA, LOG, TETO, UA = AQUI / "prova", AQUI / "PEDIDOS.jsonl", 3, "SINTONIA-research/1.0 (+descoberta manual controlada)"

def contagem(dom):
    if not LOG.exists(): return 0
    return sum(1 for l in LOG.read_text(encoding="utf-8").splitlines() if json.loads(l)["DOMINIO"] == dom)

def pedir(url):
    dom = urllib.parse.urlsplit(url).hostname
    if contagem(dom) >= TETO:
        return {"URL": url, "RESULTADO": "TETO_ATINGIDO"}
    time.sleep(4)
    reg = {"URL": url, "DOMINIO": dom, "QUANDO": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25) as r:
            b = r.read(); reg["HTTP"] = r.status
    except urllib.error.HTTPError as e:
        b = e.read() or b""; reg["HTTP"] = e.code
    except Exception as e:
        b = b""; reg["HTTP"] = None; reg["ERRO"] = repr(e)[:200]
    reg["SHA256"] = hashlib.sha256(b).hexdigest(); reg["BYTES"] = len(b)
    f = PROVA / (reg["SHA256"][:16] + ".bin"); f.write_bytes(b); reg["FICHEIRO"] = f.name
    with LOG.open("a", encoding="utf-8") as fh: fh.write(json.dumps(reg, ensure_ascii=False) + "\n")
    return reg, b

def buscar(url):
    s = urllib.parse.urlsplit(url); robots = f"{s.scheme}://{s.netloc}/robots.txt"
    got = pedir(robots)
    if isinstance(got, dict): return got
    reg, b = got
    rp = urllib.robotparser.RobotFileParser()
    if reg["HTTP"] == 200 and not b.lstrip()[:15].lower().startswith((b"<!doctype", b"<html")):
        rp.parse(b.decode("utf-8", "replace").splitlines())
        if not rp.can_fetch(UA, url): return {"URL": url, "RESULTADO": "ROBOTS_DISALLOW"}
    elif reg["HTTP"] in (401, 403) or reg["HTTP"] == 200:
        return {"URL": url, "RESULTADO": "ROBOTS_INVALID_OR_DENIED(D39)", "HTTP": reg["HTTP"]}
    got = pedir(url)
    if isinstance(got, dict): return got
    return {k: got[0][k] for k in ("URL", "HTTP", "SHA256", "BYTES", "FICHEIRO")}

if __name__ == "__main__":
    for u in sys.argv[1:]: print(json.dumps(buscar(u), ensure_ascii=False))
