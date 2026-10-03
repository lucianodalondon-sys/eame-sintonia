"""T1 · QUANTO CUSTA UM PRAZO DE VALIDADE (TTL) NAS FONTES MUTABLE?

    py provas/ttl_mutable_simulacao.py --extrair   # le os bytes guardados nesta maquina
    py provas/ttl_mutable_simulacao.py             # simula a partir do JSON de datas

SEM REDE. Duas etapas, e a segunda so le o que a primeira escreveu:

1. EXTRAIR. Os bytes das materias das fontes MUTABLE de noticias estao fora do
   Git (livros de coleta desta maquina). De cada materia tira-se o que ELA
   declara: `article:published_time` e `article:modified_time`. Fica em
   TTL-MUTABLE-DATAS-T1.json — e o dado, versionado, para a simulacao se refazer
   sem estes discos.
2. SIMULAR. Uma corrida a cada C horas. Cada materia entra no indice quando e
   publicada, e sai quando MAX_TARGETS materias mais novas a empurram para fora
   (so se ve o que o indice anuncia). A edicao e a `modified_time`: e apanhada
   na primeira revisita a partir dela. Politicas:

     ATUAL          revisita todas as conhecidas em todas as corridas (hoje)
     TTL_<X>d       revisita quando a ultima visita tem mais de X dias
     CURVA          o intervalo cresce com a idade da materia (desde a 1.a visita):
                    max(C, min(14 d, idade / 6)) — nova todas as corridas, antiga menos

   Mede-se, em regime (os ultimos 90 dias simulados), os pedidos de revisita por
   corrida; e, para cada edicao que acontece DEPOIS da primeira captura (antes
   dela, a primeira captura ja traz o texto final), o atraso ate ser vista.
   Uma edicao cuja materia sai do indice antes da revisita e PERDIDA — e conta-se
   separada, porque a politica ATUAL tambem a perde.

⚠️ O QUE ESTE DADO NAO DIZ. Cada pagina declara so a ULTIMA modificacao: se uma
materia foi editada tres vezes, ve-se uma. O numero de edicoes e um minimo. E a
cadencia das corridas em producao e NAO SEI — por isso simula-se com duas (24 h
e 6 h), e nao com uma inventada.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

AQUI = Path(__file__).parent
DATAS = AQUI / "TTL-MUTABLE-DATAS-T1.json"
SAIDA = AQUI / "TTL-MUTABLE-SIMULACAO-T1.json"

# As fontes MUTABLE de NOTICIAS (morada propria por materia) com datas proprias.
# Os boletins reescritos na mesma morada (IT-T3-005, IT-T2-002, IT-T2-004) ficam
# FORA: la a revisita a cada corrida e a coleta, e nao ha prazo que se aplique.
FONTES = {"IT-T7-017": 30, "IT-T10-022": 14, "IT-T7-042": None}
RAIZES = ["C:/eame-sintonia-ops", ".", "C:/eame-sintonia", "C:/eame-sintonia-sysmap"]


def _iso(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def extrair():
    docs = {}
    for r in RAIZES:
        f = Path(r) / "data/collection-ledger/italy/observations.ndjson"
        if not f.exists():
            continue
        for linha in f.read_text(encoding="utf-8").splitlines():
            if not linha.strip():
                continue
            o = json.loads(linha)
            if o.get("SOURCE_ID") not in FONTES or not o.get("RAW_PATH"):
                continue
            p = Path(o["RAW_PATH"])
            if not p.is_absolute():
                p = Path(r) / p
            if not p.exists():
                continue
            t = p.read_bytes().decode("utf-8", "replace")
            pub = re.search(r'article:published_time"\s+content="([^"]+)"', t)
            mod = re.search(r'article:modified_time"\s+content="([^"]+)"', t)
            chave = (o["SOURCE_ID"], o["SOURCE_URL"].rstrip("/"))
            d = docs.setdefault(chave, {"SOURCE_ID": o["SOURCE_ID"], "URL": o["SOURCE_URL"].rstrip("/"),
                                        "PUBLISHED": None, "MODIFIED": set(), "CAPTURAS": set()})
            if pub:
                d["PUBLISHED"] = pub.group(1)
            if mod:
                d["MODIFIED"].add(mod.group(1))
            d["CAPTURAS"].add(o.get("CAPTURED_AT"))
    saida = []
    for d in docs.values():
        caps = sorted(c for c in d["CAPTURAS"] if c)
        mods = sorted(d["MODIFIED"])
        # ⚠️ A NOSSA VISITA NAO E UMA EDICAO: um modified_time a menos de 10
        # minutos de uma captura nossa e a hora a que batemos a porta (know-how
        # «o carimbo de hora do site e a nossa visita»), e nao conta.
        caps_dt = [_iso(c) for c in caps]
        reais = [m for m in mods if not any(abs((_iso(m) - c).total_seconds()) < 600 for c in caps_dt)]
        saida.append({"SOURCE_ID": d["SOURCE_ID"], "URL": d["URL"], "PUBLISHED": d["PUBLISHED"],
                      "MODIFIED": reais[-1] if reais else None,
                      "MODIFIED_VISTOS": mods, "MODIFIED_DESCARTADOS_POR_SER_A_VISITA": sorted(set(mods) - set(reais)),
                      "CAPTURAS": len(caps), "PRIMEIRA_CAPTURA": caps[0] if caps else None})
    saida.sort(key=lambda x: (x["SOURCE_ID"], x["PUBLISHED"] or ""))
    out = {"DATASET": "TTL-MUTABLE-DATAS-T1", "MISSAO": "T1 ttl-mutable-v1",
           "EXTRAIDO_EM": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "ORIGEM": "bytes guardados nos livros de coleta desta maquina (fora do Git): " + ", ".join(RAIZES),
           "LIMITE": "cada pagina declara so a ULTIMA modificacao: o numero de edicoes e um minimo",
           "MATERIAS": saida}
    DATAS.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    por = {}
    for m in saida:
        por.setdefault(m["SOURCE_ID"], []).append(m)
    for sid, l in por.items():
        com = [m for m in l if m["PUBLISHED"] and m["MODIFIED"]]
        print(f"{sid}: {len(l)} materias, {sum(1 for m in l if m['PUBLISHED'])} com data de publicacao, "
              f"{len(com)} com modificacao real")
    print(f"-> {DATAS.name}")


# ── A SIMULACAO ──────────────────────────────────────────────────────────────
DIA = 86400


def politicas(C):
    p = {"ATUAL": lambda idade, desde: True}
    for x in (1, 3, 7, 14):
        p[f"TTL_{x}d"] = (lambda X: lambda idade, desde: desde >= X * DIA - 1)(x)
    p["CURVA"] = lambda idade, desde: desde >= max(C, min(14 * DIA, idade / 6)) - 1
    return p


def simular(materias, max_targets, C, revisitar):
    """Devolve (pedidos por corrida em regime, lista de edicoes com atraso/perda)."""
    ms = [m for m in materias if m["PUBLISHED"]]
    pub = sorted(((_iso(m["PUBLISHED"]).timestamp(), m) for m in ms), key=lambda x: x[0])
    fim = max(_iso(m["PRIMEIRA_CAPTURA"]).timestamp() for m in ms if m["PRIMEIRA_CAPTURA"])
    fim = max(fim, max((_iso(m["MODIFIED"]).timestamp() for m in ms if m["MODIFIED"]), default=fim)) + 30 * DIA
    # sai do indice quando MAX_TARGETS materias mais novas ja foram publicadas
    saida = {}
    for i, (t, m) in enumerate(pub):
        mais_novas = [t2 for t2, _ in pub[i + 1:]]
        saida[m["URL"]] = mais_novas[max_targets - 1] if max_targets and len(mais_novas) >= max_targets else float("inf")
    inicio = pub[0][0]
    t = inicio - (inicio % C) + C
    primeira, ultima, vista = {}, {}, {}
    pedidos_regime, corridas_regime = 0, 0
    while t <= fim:
        n = 0
        for tp, m in pub:
            u = m["URL"]
            if tp > t or t >= saida[u]:
                continue                               # nao anunciado nesta corrida
            if u not in primeira:
                primeira[u] = ultima[u] = t            # materia nova: 1.a captura (nao e revisita)
                vista[u] = t
                continue
            if revisitar(t - primeira[u], t - ultima[u]):
                n += 1
                ultima[u] = t
                vista.setdefault(("rev", u), []).append(t)
        if t >= fim - 90 * DIA:
            pedidos_regime += n
            corridas_regime += 1
        t += C
    edicoes = []
    for tp, m in pub:
        if not m["MODIFIED"]:
            continue
        u, tm = m["URL"], _iso(m["MODIFIED"]).timestamp()
        if u not in primeira or tm <= primeira[u]:
            continue                                   # a 1.a captura ja traz o texto final
        revs = [x for x in vista.get(("rev", u), []) if x >= tm]
        if revs:
            edicoes.append({"URL": u, "ATRASO_DIAS": round((revs[0] - tm) / DIA, 2)})
        else:
            edicoes.append({"URL": u, "PERDIDA": True, "PORQUE": "saiu do indice antes da revisita"
                            if saida[u] < float("inf") else "fim da simulacao"})
    return (pedidos_regime / corridas_regime if corridas_regime else 0), edicoes


def main():
    if "--extrair" in sys.argv:
        extrair()
        return 0
    dados = json.loads(DATAS.read_text(encoding="utf-8"))["MATERIAS"]
    linhas = []
    for C_h in (24, 6):
        C = C_h * 3600
        for nome, f in politicas(C).items():
            tot_ped, eds = 0.0, []
            por_fonte = {}
            for sid, mt in FONTES.items():
                mats = [m for m in dados if m["SOURCE_ID"] == sid]
                if not mats:
                    continue
                ped, e = simular(mats, mt, C, f)
                tot_ped += ped
                eds += e
                por_fonte[sid] = {"PEDIDOS_POR_CORRIDA": round(ped, 2), "EDICOES_DEPOIS_DA_1A_CAPTURA": len(e),
                                  "PERDIDAS": sum(1 for x in e if x.get("PERDIDA")),
                                  "ATRASO_MAX_DIAS": max((x["ATRASO_DIAS"] for x in e if "ATRASO_DIAS" in x), default=0)}
            atrasos = [x["ATRASO_DIAS"] for x in eds if "ATRASO_DIAS" in x]
            linhas.append({"CADENCIA_H": C_h, "POLITICA": nome, "PEDIDOS_POR_CORRIDA": round(tot_ped, 2),
                           "EDICOES": len(eds), "PERDIDAS": sum(1 for x in eds if x.get("PERDIDA")),
                           "ATRASO_MEDIO_DIAS": round(sum(atrasos) / len(atrasos), 2) if atrasos else 0,
                           "ATRASO_MAX_DIAS": max(atrasos, default=0),
                           "DIAS_DE_EDICAO_NAO_VISTA": round(sum(atrasos), 2),
                           "POR_FONTE": por_fonte})
    base = {l["CADENCIA_H"]: l["PEDIDOS_POR_CORRIDA"] for l in linhas if l["POLITICA"] == "ATUAL"}
    for l in linhas:
        l["PEDIDOS_POUPADOS_POR_CORRIDA"] = round(base[l["CADENCIA_H"]] - l["PEDIDOS_POR_CORRIDA"], 2)
    SAIDA.write_text(json.dumps({"DATASET": "TTL-MUTABLE-SIMULACAO-T1", "ENTRADA": DATAS.name,
                                 "MODELO": __doc__.split("2. SIMULAR.")[1].split("⚠️")[0].strip(),
                                 "LINHAS": linhas}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{'C':>4} {'politica':9} {'pedidos/corr':>12} {'poupados':>9} {'edicoes':>8} {'perdidas':>8} "
          f"{'atraso med':>10} {'atraso max':>10} {'dias nao vistos':>15}")
    for l in linhas:
        print(f"{l['CADENCIA_H']:>3}h {l['POLITICA']:9} {l['PEDIDOS_POR_CORRIDA']:>12} {l['PEDIDOS_POUPADOS_POR_CORRIDA']:>9} "
              f"{l['EDICOES']:>8} {l['PERDIDAS']:>8} {l['ATRASO_MEDIO_DIAS']:>10} {l['ATRASO_MAX_DIAS']:>10} "
              f"{l['DIAS_DE_EDICAO_NAO_VISTA']:>15}")
    print(f"-> {SAIDA.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
