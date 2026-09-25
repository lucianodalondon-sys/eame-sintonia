"""D34 (3): o leitor RFC 9309 no LIVRO INTEIRO — OFFLINE, sobre os robots.txt que o robo JA GUARDOU.

Cada prova VALIDATE_ROUTE do livro (LIFECYCLE-EVIDENCE-V1) guarda a ROTA e o robots.txt lido na hora
(o texto, ou o porque quando nao houve texto). Para cada fonte, a ULTIMA dessas provas e lida duas
vezes:
  ANTIGO = o portao de antes da D34, reproduzido linha a linha (urllib.robotparser; 404/410 = pode;
           outro HTTP = Disallow total; rede em baixo = Disallow total; HTML lido como se fosse robots)
  NOVO   = coleta/robots_rfc9309.py (o leitor unico)
e a leitura ANTIGA reproduzida e conferida contra o que o robo registou na altura (PERMITIDO/CLASSE):
se nao bater, a comparacao nao vale e o script diz quantas nao batem.

⚠️ O ROBO GUARDA O robots.txt CORTADO AOS 120 CARACTERES (curadoria/worker.py: `origem[:120]`).
Por isso so e FIAVEL aqui o que esta no comeco: o codigo da resposta (404/403/inacessivel) e o HTML
no lugar do robots. A regra (qual Allow/Disallow vence) so e fiavel nos robots COMPLETOS (< 120
caracteres); nos CORTADOS fica ESPERA VPN (re-ler o robots inteiro com rede).

ZERO pedidos de rede.
uso: py provas/robots_rfc/medir_robots_livro.py <pasta com as copias> <saida.json>"""
import collections
import hashlib
import json
import re
import sys
import urllib.robotparser    # SO para reproduzir a leitura ANTIGA (medicao); o codigo da casa nao o usa
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "coleta"))
import robots_rfc9309 as RR   # noqa: E402

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0"  # CAP.UA
COPIAS, SAIDA = Path(sys.argv[1]), Path(sys.argv[2])


def estado_guardado(txt: str):
    """(status, corpo) reconstruidos do que o robo guardou em ROBOTS."""
    m = re.match(r"^HTTP (\d{3})", txt or "")
    if m:
        return int(m.group(1)), ""
    if (txt or "").startswith("robots inacessivel"):
        return None, ""
    return 200, txt or ""


def antigo(status, corpo, rota):
    rp = urllib.robotparser.RobotFileParser()
    if status == 200:
        rp.parse(corpo.splitlines())
    elif status in (404, 410):
        rp.parse([])
    else:
        rp.parse(["User-agent: *", "Disallow: /"])
    return rp.can_fetch(UA, rota)


def main():
    provas = json.loads((COPIAS / "LIFECYCLE-EVIDENCE-V1.json").read_text(encoding="utf-8"))["PROVAS"]
    livro = json.loads((COPIAS / "LIFECYCLE-LEDGER-V1.json").read_text(encoding="utf-8"))["TRANSICOES"]
    estado = {}
    for t in livro:
        estado[t["SOURCE_ID"]] = t["NEW_STATE"]
    ult = {}
    for p in provas:
        if p["ETAPA"] == "VALIDATE_ROUTE" and (p.get("DADOS") or {}).get("ROTA"):
            ult[p["SOURCE_ID"]] = p              # a ultima vence
    linhas, confere, estados_novos = [], collections.Counter(), collections.Counter()
    for sid, p in sorted(ult.items()):
        d = p["DADOS"]
        rota, txt = d["ROTA"], d.get("ROBOTS") or ""
        st, corpo = estado_guardado(txt)
        a = antigo(st, corpo, rota)
        rp = RR.de_resposta(st, corpo)
        n = rp.decidir(UA, rota)
        estados_novos[rp.estado] += 1
        # o que o robo registou na altura: PERMITIDO True = passou; CLASSE ROBOTS = barrado pelo robots;
        # sem nenhum dos dois (RETRY de rede) = nao se sabia
        cortado = rp.estado == RR.LIDO and len(txt) >= 120
        registado = True if d.get("PERMITIDO") is True else (False if d.get("CLASSE") == "ROBOTS" else None)
        if registado is not None:
            confere[("BATE" if registado == a else "NAO_BATE") + ("_CORTADO" if cortado else "")] += 1
        linhas.append({"SOURCE_ID": sid, "ROBOTS_CORTADO_AOS_120": cortado, "ESTADO_NO_LIVRO": estado.get(sid), "ROTA": rota,
                       "EVIDENCE_REF": p["EVIDENCE_REF"], "OBSERVADO_EM": p.get("OBSERVED_AT"),
                       "ROBOTS_ESTADO": rp.estado, "ROBOTS_SHA256": hashlib.sha256(txt.encode("utf-8")).hexdigest(),
                       "ANTIGO": a, "NOVO": n.permite, "REGRA_NOVA": n.regra,
                       "REGISTADO_NA_ALTURA": registado})
    abre = [x for x in linhas if not x["ANTIGO"] and x["NOVO"]]
    fecha = [x for x in linhas if x["ANTIGO"] and not x["NOVO"]]
    motivo = lambda xs: dict(collections.Counter(x["ROBOTS_ESTADO"] for x in xs))
    out = {
        "MEDICAO": "D34 (3) — robots RFC 9309 no livro inteiro, offline",
        "COPIAS": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(COPIAS.glob("*.json"))},
        "FONTES_COM_ROBOTS_GUARDADO": len(linhas),
        "PROVAS_VALIDATE_ROUTE": sum(1 for p in provas if p["ETAPA"] == "VALIDATE_ROUTE"),
        "A_LEITURA_ANTIGA_REPRODUZIDA_BATE_COM_O_REGISTADO": dict(confere),
        "ROBOTS_POR_ESTADO_NOVO": dict(estados_novos),
        "PROIBIDA_PARA_PERMITIDA": len(abre), "PROIBIDA_PARA_PERMITIDA_POR_ESTADO": motivo(abre),
        "PERMITIDA_PARA_PROIBIDA": len(fecha), "PERMITIDA_PARA_PROIBIDA_POR_ESTADO": motivo(fecha),
        "IGUAIS": len(linhas) - len(abre) - len(fecha),
        "LIDOS_COMPLETOS": sum(1 for x in linhas if x["ROBOTS_ESTADO"] == RR.LIDO and not x["ROBOTS_CORTADO_AOS_120"]),
        "LIDOS_CORTADOS_ESPERA_VPN": sum(1 for x in linhas if x["ROBOTS_CORTADO_AOS_120"]),
        "MUDAM_SO_POR_REGRA_EM_ROBOTS_COMPLETO": sum(1 for x in abre + fecha
                                                     if x["ROBOTS_ESTADO"] == RR.LIDO and not x["ROBOTS_CORTADO_AOS_120"]),
        "MUDAM": abre + fecha,
        "TODAS": linhas,
    }
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("MUDAM", "TODAS", "COPIAS")}, ensure_ascii=False, indent=1))
    for x in abre + fecha:
        print("%-11s %-28s %s -> %s  [%s] %s | %s" % (x["SOURCE_ID"], x["ESTADO_NO_LIVRO"], x["ANTIGO"], x["NOVO"],
                                                    x["ROBOTS_ESTADO"], x["REGRA_NOVA"][:60], x["ROTA"][:70]))


if __name__ == "__main__":
    main()
