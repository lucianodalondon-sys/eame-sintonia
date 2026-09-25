"""D34 (3) com rede: o robots.txt INTEIRO de cada site do livro, lido UMA vez, e cada fonte decidida
pela leitura ANTIGA (urllib.robotparser, como o portao de antes) e pela NOVA (coleta/robots_rfc9309.py).

Porque: o robo guardava o robots cortado aos 120 caracteres; offline, 228 dos 391 lidos ficaram
sem a regra que decidia (ROBOTS-LIVRO-INTEIRO.json).

Cortesia: portao de egresso de CONSENSO (IT) no inicio e de 25 em 25 sites — se nao der PASS, para;
1 pedido por site (+ saltos do urlopen); 0,5 s entre sites; UA do portao do Curator (capturador.UA).
Bytes em <saida>/robots/<host>.txt, com sha256 na linha de cada site.
uso: py provas/robots_rfc/medir_robots_com_rede.py <contratos curator.json> <tabela coletor.json> <livro.json> <pasta saida>"""
import collections
import hashlib
import json
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser    # SO para reproduzir a leitura ANTIGA (medicao)
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "coleta"))
sys.path.insert(0, str(RAIZ / "curadoria"))
import robots_rfc9309 as RR   # noqa: E402
import capturador as CAP      # noqa: E402

CONTRATOS, TABELA, LIVRO, SAIDA = map(Path, sys.argv[1:5])
REDE = "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/superficie/rede.py"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def egresso_it() -> bool:
    r = subprocess.run([sys.executable, REDE, "--portao-de-egresso", "IT"], capture_output=True, text=True)
    return '"EGRESS_GATE": "PASS"' in r.stdout


def buscar(origem: str):
    """(status, corpo_bytes, erro) — o mesmo transporte do gate_de_rota (urllib, CAP.UA)."""
    req = urllib.request.Request(origem + "/robots.txt", headers={"User-Agent": CAP.UA})
    try:
        with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
            return r.status, r.read(), None
    except urllib.error.HTTPError as e:
        return e.code, b"", None
    except Exception as e:      # noqa: BLE001
        return None, b"", type(e).__name__


def antigo(status, corpo: str, url: str) -> bool:
    rp = urllib.robotparser.RobotFileParser()
    if status is not None and 200 <= status < 300:
        rp.parse(corpo.splitlines())          # o portao antigo lia HTML como se fosse robots
    elif status in (404, 410):
        rp.parse([])
    else:
        rp.parse(["User-agent: *", "Disallow: /"])
    return rp.can_fetch(CAP.UA, url)


def rota(c: dict) -> str | None:
    aq = c.get("ACQUISITION") or {}
    return aq.get("FEED_URL") or aq.get("INDEX_URL") or aq.get("URL") or c.get("CANONICAL_ENTRY_URL")


def main():
    estado = {}
    for t in json.loads(LIVRO.read_text(encoding="utf-8"))["TRANSICOES"]:
        estado[t["SOURCE_ID"]] = t["NEW_STATE"]
    fontes = {}
    for origem_do_contrato, f in (("LIVRO_DO_ROBO", CONTRATOS), ("TABELA_DO_COLETOR", TABELA)):
        for c in json.loads(f.read_text(encoding="utf-8"))["FONTES"]:
            u = rota(c)
            if u and u.startswith(("http://", "https://")) and c["SOURCE_ID"] not in fontes:
                fontes[c["SOURCE_ID"]] = (u, origem_do_contrato)
    origens = sorted({"%s://%s" % (urlsplit(u).scheme, urlsplit(u).netloc) for u, _ in fontes.values()})
    pasta = SAIDA / "robots"
    pasta.mkdir(parents=True, exist_ok=True)
    if not egresso_it():
        sys.exit("PARAR: portao de egresso de consenso nao da PASS IT")
    lidos = {}
    for i, o in enumerate(origens):
        if i and i % 25 == 0 and not egresso_it():
            sys.exit("PARAR: portao de egresso deixou de dar PASS IT (site %d de %d)" % (i, len(origens)))
        st, corpo, erro = buscar(o)
        host = urlsplit(o).netloc
        (pasta / (host.replace(":", "_") + ".txt")).write_bytes(corpo)
        lidos[o] = {"STATUS": st, "ERRO": erro, "BYTES": len(corpo), "SHA256": hashlib.sha256(corpo).hexdigest()}
        time.sleep(0.5)
        if i % 50 == 0:
            print("site %d/%d %s %s" % (i + 1, len(origens), o, st), flush=True)
    linhas = []
    for sid, (u, org) in sorted(fontes.items()):
        o = "%s://%s" % (urlsplit(u).scheme, urlsplit(u).netloc)
        L = lidos[o]
        corpo = (pasta / (urlsplit(u).netloc.replace(":", "_") + ".txt")).read_bytes()
        rp = RR.de_resposta(L["STATUS"], corpo, erro=L["ERRO"])
        n = rp.decidir(CAP.UA, u)
        a = antigo(L["STATUS"], corpo.decode("utf-8", "replace"), u)
        linhas.append({"SOURCE_ID": sid, "ORIGEM": org, "ESTADO_NO_LIVRO": estado.get(sid), "ROTA": u,
                       "ROBOTS_STATUS": L["STATUS"], "ROBOTS_ESTADO": rp.estado, "ROBOTS_SHA256": L["SHA256"],
                       "ANTIGO": a, "NOVO": n.permite, "REGRA_NOVA": n.regra})
    abre = [x for x in linhas if not x["ANTIGO"] and x["NOVO"]]
    fecha = [x for x in linhas if x["ANTIGO"] and not x["NOVO"]]
    por = lambda xs, k: dict(collections.Counter(x[k] for x in xs))
    out = {"MEDICAO": "D34 (3) com rede — robots inteiro, 1 pedido por site, portao de consenso IT",
           "FONTES": len(linhas), "SITES": len(origens),
           "SITES_POR_ESTADO": dict(collections.Counter(RR.de_resposta(v["STATUS"], b"x", erro=v["ERRO"]).estado
                                                        if v["STATUS"] is None or not (200 <= v["STATUS"] < 300)
                                                        else "2xx" for v in lidos.values())),
           "FONTES_POR_ESTADO_NOVO": por(linhas, "ROBOTS_ESTADO"),
           "PROIBIDA_PARA_PERMITIDA": len(abre), "PROIBIDA_PARA_PERMITIDA_POR_ESTADO": por(abre, "ROBOTS_ESTADO"),
           "PERMITIDA_PARA_PROIBIDA": len(fecha), "PERMITIDA_PARA_PROIBIDA_POR_ESTADO": por(fecha, "ROBOTS_ESTADO"),
           "MUDAM_PELA_REGRA_MAIS_ESPECIFICA": [x for x in abre + fecha if x["ROBOTS_ESTADO"] == RR.LIDO],
           "PROIBIDAS_DE_VERDADE_CONTINUAM": sum(1 for x in linhas if not x["ANTIGO"] and not x["NOVO"]
                                                  and x["ROBOTS_ESTADO"] == RR.LIDO),
           "MUDAM": abre + fecha, "SITES_LIDOS": lidos, "TODAS": linhas}
    (SAIDA / "ROBOTS-COM-REDE.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("MUDAM", "TODAS", "SITES_LIDOS",
                                                              "MUDAM_PELA_REGRA_MAIS_ESPECIFICA")},
                     ensure_ascii=False, indent=1))
    for x in abre + fecha:
        print("%-11s %-28s %s -> %s [%s %s] %s | %s" % (x["SOURCE_ID"], x["ESTADO_NO_LIVRO"], x["ANTIGO"], x["NOVO"],
              x["ROBOTS_STATUS"], x["ROBOTS_ESTADO"], x["REGRA_NOVA"][:55], x["ROTA"][:60]))


if __name__ == "__main__":
    main()
