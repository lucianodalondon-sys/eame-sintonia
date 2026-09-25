#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1 · REVISAR AS READY NOVAS, UMA A UMA — numa banca, nunca no vivo.

    py <banca>/scripts/reparo/revisar_ready.py --banca <banca> --fontes a,b,c --saida <json>

1. Corre o ciclo do reparo SO para as fontes dadas (o mesmo gatilho e worker da
   medicao; o detector capa/materia e o da arvore da banca = o instalado).
2. Para cada fonte que acaba READY_FOR_COLLECTION, le a prova do canario (o item
   que ele abriu) e volta a abrir ESSE item (1 pedido, robots da casa) para tirar
   titulo, h1, a primeira data que aparecer e o inicio do texto em paragrafos.
3. Marca sinais de suspeita (nao decide sozinho — a decisao e de quem le):
     CAMINHO_DE_SERVICO   o endereco do item tem vocabulario de pagina fixa
     SEM_DATA             nenhuma data no titulo, h1 ou inicio do texto
Escreve tudo em --saida; o veredito humano junta-se depois ao mesmo ficheiro.
"""
from __future__ import annotations

import argparse
import html as H
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SERVICO = re.compile(
    r"(lavora-con-noi|contatt|uffic|organizzazion|trasparen|accesso-civico|tribut|servizi|"
    r"chi-siamo|sostenibilit|associazione|area-studi|didattic|corso|brand|privacy|"
    r"alunni|accreditament|autorizzazion|impianti|istituzional|strutture|anagrafe)", re.I)
DATA = re.compile(r"\b(\d{1,2}[./-]\d{1,2}[./-](?:19|20)\d{2}|(?:19|20)\d{2}-\d{2}-\d{2}|"
                  r"\d{1,2}\s+(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|"
                  r"settembre|ottobre|novembre|dicembre)\s+(?:19|20)\d{2})\b", re.I)


def _texto(s: str) -> str:
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def extrair(b: bytes) -> dict:
    t = b.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", t)
    tit = re.search(r"(?is)<title[^>]*>(.*?)</title>", t)
    h1 = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", t)
    paras = [_texto(p) for p in re.findall(r"(?is)<p\b[^>]*>(.*?)</p>", t)]
    corpo = " ".join(p for p in paras if len(p) > 40)
    alvo = " ".join([_texto(tit.group(1)) if tit else "", _texto(h1.group(1)) if h1 else "", corpo[:1500]])
    d = DATA.search(alvo) or DATA.search(_texto(t)[:20000])
    return {"TITULO": _texto(tit.group(1))[:160] if tit else "", "H1": _texto(h1.group(1))[:160] if h1 else "",
            "DATA_VISTA": d.group(0) if d else None, "INICIO": corpo[:400]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--banca", required=True)
    ap.add_argument("--fontes", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args(argv)
    banca = Path(a.banca).resolve()
    if "source-curator-service-v1" in str(banca).replace("\\", "/"):
        print("RECUSO: a banca aponta para o bot vivo")
        return 2
    sys.path.insert(0, str(banca / "curadoria"))
    import canario as CAN            # noqa: E402
    import fila as F                 # noqa: E402
    import gate_de_rota as GATE      # noqa: E402
    import gatilho_discovery as GD   # noqa: E402
    import lifecycle as LC           # noqa: E402
    import worker as W               # noqa: E402
    assert Path(F.FILA).resolve().is_relative_to(banca)
    alvo = set(a.fontes.split(","))
    orig = GD.candidatas_a_reparar
    GD.candidatas_a_reparar = lambda agora, **kw: [c for c in orig(agora, **kw) if c["SOURCE_ID"] in alvo]
    GD.requalificar_se_a_prova_mudou = lambda agora: []
    for _ in range(20):
        rp = GD.reparar_encalhadas(datetime.now(timezone.utc))
        feitos = W.correr(pausa=0.5, verboso=True)
        if not rp["ENFILEIRADAS"] and not feitos:
            break
    est = LC.snapshot()
    prova = {}
    for p in json.loads(W.EVIDENCIA.read_text(encoding="utf-8"))["PROVAS"]:
        if p["SOURCE_ID"] in alvo and p["ETAPA"] in ("CANARY", "REVALIDATE") and (p["DADOS"] or {}).get("PASS"):
            prova[p["SOURCE_ID"]] = p
    contratos = W._contratos()
    out = []
    for sid in sorted(alvo):
        linha = {"SOURCE_ID": sid, "ESTADO": est.get(sid), "NOME": (contratos.get(sid) or {}).get("NAME")}
        if est.get(sid) == LC.READY_FOR_COLLECTION and sid in prova:
            d = prova[sid]["DADOS"]
            item = d.get("ITEM_ABERTO") or {}
            aq = contratos[sid]["ACQUISITION"]
            linha.update(INDEX_URL=aq.get("INDEX_URL"), LINK_PATTERN=aq.get("LINK_PATTERN"),
                         ITEM=item.get("URL") or d.get("ALVO"), EVIDENCE_REF=prova[sid]["EVIDENCE_REF"],
                         RETRATO={k: item.get(k) for k in ("HTML_KIND", "CAPA_OU_MATERIA", "LINKS",
                                                           "PARAGRAPH_CHARACTERS", "TEXT_SHA256")},
                         REPARADA=bool(contratos[sid].get("REPARO_DE_CONTRATO")))
            url = linha["ITEM"]
            rp_, _ = GATE.robots_de(url.split("/")[2])
            if GATE.permitido(url, rp_):
                st, b, err = CAN.buscar(url)
                linha["RELIDO_HTTP"] = st
                if st == 200 and b:
                    linha.update(extrair(b))
            sinais = []
            if SERVICO.search(url.split("?")[0]):
                sinais.append("CAMINHO_DE_SERVICO: %s" % SERVICO.search(url).group(0))
            if not linha.get("DATA_VISTA"):
                sinais.append("SEM_DATA")
            linha["SINAIS"] = sinais
        out.append(linha)
        print(sid, linha.get("ESTADO"), linha.get("SINAIS"), (linha.get("ITEM") or "")[-70:], flush=True)
    Path(a.saida).write_text(json.dumps({"DATASET": "R1-REVISAO-READY", "MEDIDO_EM":
                                         datetime.now(timezone.utc).isoformat(), "FONTES": out},
                                        ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
