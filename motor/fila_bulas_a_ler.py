#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FILA BULAS_A_LER — que bulas os fatos da Intelligence pedem para ler (D123 · D117 item 2).

    python3 motor/fila_bulas_a_ler.py <ficheiro.json> [...] [--saida FILA.json]

    MISSAO   LIGACAO-ADAMA-OBRIGATORIA (D123 do dono, 27/09/2026)
    ENTRADA  qualquer JSON que traga objetos com LIGACAO_ADAMA (a saida do motor, os itens do
             pote, o CRUZAMENTOS-MAX...). So conta a ligacao que passa em
             `porta_da_referencia.conferir_ligacao` (selo da porta): ligacao feita fora da
             porta nao pede bula nenhuma.
    SAIDA    FILA_BULAS_A_LER/v1 — deterministica (mesma entrada, mesmo ficheiro), SEM REDE.

A FILA NAO COLETA. Diz o que ler, por esta ordem:
    1. bulas ADAMA  — mais fatos a pedir primeiro; depois registo
    2. concorrentes — por substancia das culturas dos fatos. Hoje NAO SEI: a edicao da referencia
                      so traz registos ADAMA (lacuna 3 de PORTA-UNICA-REFERENCIA.md); a fila diz
                      que substancias pedem o cadastro concorrente, sem inventar bula.

O TETO (5 pedidos por dominio por 24 h) e da Coleta, que o aplica (coleta/espera_por_dominio.py, D38).
A fila so PROPOE lotes: por host do URL da bula, 5 por lote, `LOTE_24H` = 0, 1, 2... Bula sem URL
fica no host NAO SEI — a Coleta acha-a pelo numero de registo, nao a fila.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "motor") not in sys.path:
    sys.path.insert(0, str(RAIZ / "motor"))
import porta_da_referencia as PORTA  # noqa: E402

CONTRATO = "FILA_BULAS_A_LER/v1"
TETO_POR_DOMINIO_24H = 5   # D117 item 2, como a missao o escreveu; quem o faz cumprir e a Coleta
NAO_SEI = PORTA.NAO_SEI


def ligacoes_em(dado, caminho="$"):
    """Todas as (id_do_fato, LIGACAO_ADAMA) de um JSON qualquer, na ordem em que aparecem."""
    if isinstance(dado, dict):
        if isinstance(dado.get("LIGACAO_ADAMA"), dict):
            fid = next((str(dado[k]) for k in ("OBJETO_ID", "SIGNAL_ID", "ITEM_ID", "VOICE_ID", "ACERVO_ID",
                                               "CROP_WINDOW_ID", "FATO_ID") if dado.get(k)), caminho)
            yield fid, dado["LIGACAO_ADAMA"]
        for k, v in dado.items():
            if k != "LIGACAO_ADAMA":
                yield from ligacoes_em(v, "%s.%s" % (caminho, k))
    elif isinstance(dado, list):
        for i, v in enumerate(dado):
            yield from ligacoes_em(v, "%s[%d]" % (caminho, i))


def _host(url) -> str:
    try:
        h = urlparse(str(url)).hostname
    except ValueError:
        h = None
    return h or NAO_SEI


def fila(pares) -> dict:
    """pares = [(id_do_fato, LIGACAO_ADAMA)] -> a fila, ordenada e em lotes por host."""
    pedidas, recusadas, subs_conc, edicoes = {}, [], defaultdict(set), set()
    fatos = set()
    for fid, lig in pares:
        falhas = PORTA.conferir_ligacao(lig)
        if falhas:
            recusadas.append({"FATO": fid, "PORQUE": falhas[:3]})
            continue
        fatos.add(fid)
        if lig["CARIMBO"].get("EDICAO_REGISTRO") not in (None, NAO_SEI):
            edicoes.add(lig["CARIMBO"]["EDICAO_REGISTRO"])
        for b in lig.get("BULAS_A_LER") or []:
            x = pedidas.setdefault((b["EMPRESA"], b["REGISTRO"]), {
                "EMPRESA": b["EMPRESA"], "REGISTRO": b["REGISTRO"], "PRODUTO": b.get("PRODUTO", NAO_SEI),
                "BULA": b.get("BULA") or {"DOCUMENT_ID": NAO_SEI, "URL": NAO_SEI},
                "ESTADO_DA_LEITURA": b.get("ESTADO_DA_LEITURA", NAO_SEI), "FATOS": set(), "PORQUES": set(),
                "CULTURAS_PERGUNTADAS": set()})
            x["FATOS"].add(fid)
            x["PORQUES"].add(b.get("PORQUE") or NAO_SEI)
            x["CULTURAS_PERGUNTADAS"].update(lig["PERGUNTA"].get("CULTURA") or [])
        if lig.get("CONCORRENTES_ESTADO") == NAO_SEI:
            for s in lig["PERGUNTA"].get("SUBSTANCIA") or []:
                subs_conc[s].add(fid)
    adama = sorted((x for x in pedidas.values() if x["EMPRESA"] == "ADAMA"),
                   key=lambda x: (-len(x["FATOS"]), x["REGISTRO"]))
    por_host = defaultdict(int)
    saida = []
    for ordem, x in enumerate(adama, 1):
        h = _host((x["BULA"] or {}).get("URL"))
        lote = por_host[h] // TETO_POR_DOMINIO_24H
        por_host[h] += 1
        saida.append({"ORDEM": ordem, "EMPRESA": "ADAMA", "REGISTRO": x["REGISTRO"], "PRODUTO": x["PRODUTO"],
                      "BULA": x["BULA"], "HOST": h, "LOTE_24H": lote,
                      "ESTADO_DA_LEITURA": x["ESTADO_DA_LEITURA"], "N_FATOS_QUE_PEDEM": len(x["FATOS"]),
                      "FATOS_EXEMPLO": sorted(x["FATOS"])[:5], "PORQUE": sorted(x["PORQUES"]),
                      "CULTURAS_PERGUNTADAS": sorted(x["CULTURAS_PERGUNTADAS"])})
    concorrentes = [{"SUBSTANCIA": s, "N_FATOS_QUE_PEDEM": len(f), "ESTADO": NAO_SEI,
                     "PORQUE": "a edicao da referencia so traz registos ADAMA (lacuna 3): o cadastro "
                               "concorrente desta substancia nao esta na casa — pede-se o cadastro, nao uma bula"}
                    for s, f in sorted(subs_conc.items(), key=lambda kv: (-len(kv[1]), kv[0]))]
    return {"SCHEMA": CONTRATO, "MARCA": "EXPERIMENTAL · NAO_PARA_CLIENTE", "GERADO_POR": "motor/fila_bulas_a_ler.py",
            "NAO_COLETA": True, "TETO_POR_DOMINIO_24H": TETO_POR_DOMINIO_24H,
            "TETO_QUEM_APLICA": "a Coleta (coleta/espera_por_dominio.py, D38); a fila so propoe LOTE_24H por host",
            "EDICOES_DA_REFERENCIA": sorted(edicoes),
            "FATOS_LIDOS": len(fatos), "LIGACOES_RECUSADAS": recusadas,
            "ORDEM": "1) ADAMA, mais fatos a pedir primeiro · 2) concorrentes por substancia (hoje NAO SEI)",
            "ADAMA": saida, "CONCORRENTES": concorrentes,
            "LOTES_POR_HOST": {h: -(-n // TETO_POR_DOMINIO_24H) for h, n in sorted(por_host.items())}}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    saida = None
    if "--saida" in argv:
        i = argv.index("--saida")
        saida = argv[i + 1]
        del argv[i:i + 2]
    if not argv:
        print(__doc__.strip().split("\n\n")[0])
        return 2
    pares = []
    for p in argv:
        pares += list(ligacoes_em(json.loads(Path(p).read_text(encoding="utf-8"))))
    f = fila(pares)
    texto = json.dumps(f, ensure_ascii=False, indent=1) + "\n"
    if saida:
        Path(saida).write_text(texto, encoding="utf-8")
    else:
        sys.stdout.write(texto)
    print("%s · %d fatos · %d bulas ADAMA a ler · %d substancias pedem cadastro concorrente · recusadas %d"
          % (CONTRATO, f["FATOS_LIDOS"], len(f["ADAMA"]), len(f["CONCORRENTES"]), len(f["LIGACOES_RECUSADAS"])),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
