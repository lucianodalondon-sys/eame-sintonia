#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEPARAR OS DOIS READY — a regua antiga e a regua do gate de detalhe.

    READY_LEGACY   promovida quando «a rota resolve e traz HTML» chegava.
    READY_CURRENT  promovida com o item aberto, retratado e sem capa
                   (DETAIL_GATE_PASSED = True na evidencia da promocao).

    NAO SE APAGA. NAO SE MISTURA.

O livro e append-only, e a regua fica escrita na linha que promoveu: a
evidencia da ultima transicao para READY_FOR_COLLECTION tem, ou nao tem,
`DETAIL_GATE_PASSED`. Nao ha campo a reescrever nem carimbo a inventar —
a regua LE-SE, e por isso nao pode ser mudada a mao.

⚠️ E HA UMA TERCEIRA COISA, QUE NAO E NENHUMA DAS DUAS. Medido: este livro
tem 18 READY; o livro de aquisicao-detalhe-v1 (f98f234c) tem 160 READY e 18
DEGRADED, sobre 195 fontes. Nao sao duas contagens do mesmo — sao dois livros
que divergiram em 61 commits. Uma fonte READY so num deles nao e LEGACY nem
CURRENT: e `SO_NUM_DOS_LIVROS`, e fica dita assim.

⚠️ CONTRATO ALTERADO DEPOIS DO READY. Quando a rota de uma fonte muda (a
integracao do gate corrigiu 9 contratos com `ROUTE_PROVENANCE`), o READY que
existia foi medido contra a rota antiga. Continua LEGACY, e ganha a marca
`CONTRATO_ALTERADO_DEPOIS_DO_READY`: e a lista do que o worker tem de remedir
antes de a Collection confiar. `remedir()` faz exactamente isso — poe a fonte
em CANARY_PENDING (o livro guarda o READY antigo) e enfileira VALIDATE_ROUTE,
que por sua vez enfileira o canario. Nada e promovido aqui.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402

EVIDENCIA = RAIZ / "curadoria" / "LIFECYCLE-EVIDENCE-V1.json"
CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
SAIDA = RAIZ / "curadoria" / "READY-SPLIT-V1.json"

REGUA_CURRENT = "DETAIL/v1"
REGUA_LEGACY = "LEGACY"
# D42 (2): a regua IRMA para a forma «a pagina e o boletim» (FORMA = PAGINA_E_BOLETIM). Nao ha
# lista -> item: a pagina fixa E o documento, e a edicao identifica-se pela data comprovada (+ a
# impressao do conteudo recortado). Uma fonte dessa forma nunca passa a DETAIL/v1 (nao tem itens),
# e uma de lista nunca passa a PAGINA_BOLETIM/v1: a forma e explicita no contrato.
REGUA_PAGINA_BOLETIM = "PAGINA_BOLETIM/v1"
REGUAS_CORRENTES = frozenset({REGUA_CURRENT, REGUA_PAGINA_BOLETIM})
BOLETIM_MINIMO = 300
OUTRO_LIVRO = "f98f234c"   # a arvore final de aquisicao-detalhe-v1


def _evidencias() -> dict:
    if not EVIDENCIA.exists():
        return {}
    d = json.loads(EVIDENCIA.read_text(encoding="utf-8"))
    return {p["EVIDENCE_REF"]: p for p in d["PROVAS"]}


def _contratos() -> dict:
    if not CONTRATOS.exists():
        return {}
    return {c["SOURCE_ID"]: c for c in
            json.loads(CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}


def ultima_promocao(source_id: str, livro: dict | None = None) -> dict | None:
    """A ultima linha que levou a fonte a READY — e onde a regua esta escrita."""
    d = livro if livro is not None else LC._ler_bruto()
    ult = None
    for t in d["TRANSICOES"]:
        if t["SOURCE_ID"] == source_id and t["NEW_STATE"] == LC.READY_FOR_COLLECTION:
            ult = t
    return ult


# ---------------------------------------------------------------------------
# A REGUA DE READY_CURRENT — QUATRO PASSOS, NAO DOIS.
#
#     INDEX_URL correto -> DETAIL_LINKS -> ITEM DE DETALHE ABERTO -> BODY UTIL
#
# Medido na RECONCILIACAO-V1 (2026-09-21): `DETAIL_GATE_PASSED=True` so diz
# que o item aberto NAO PARECE CAPA (o gate reprova apenas CAPA_PROVAVEL,
# ver retrato_html.gate_capa_nao_e_materia). Um item MIXED com
# CAPA_OU_MATERIA=NAO_SEI passa o gate e nao prova BODY UTIL. `NAO SEI` nao
# vira READY_CURRENT por conveniencia: fica READY_LEGACY, e diz-se porque.
#
# Os limiares sao os do retrato (800 caracteres em paragrafos), lidos do
# proprio retrato guardado — esta funcao nao volta a medir bytes.
# ---------------------------------------------------------------------------
MINIMO_DE_LIGACOES = 2          # a lei das listagens: 2+ itens debaixo da seccao
MATERIA = "MATERIA_PROVAVEL"


def _sem_barra(u: str) -> str:
    return (u or "").strip().rstrip("/").lower()


def _homepage(u: str) -> str:
    m = re.match(r"^(https?://[^/]+)", (u or "").strip(), re.I)
    return (m.group(1).lower() if m else "")


def passos_da_promocao(promocao: dict | None, evidencia: dict | None,
                       contrato: dict | None) -> dict:
    """Le os quatro passos NA EVIDENCIA da promocao. Nao mede nada.

    Devolve {"REGUA": DETAIL/v1 | LEGACY | NAO SEI, "PASSOS": {...}, "PORQUE": str}.
    """
    passos = {"INDEX_URL": False, "DETAIL_LINKS": False, "ITEM_ABERTO": False,
              "BODY_UTIL": False, "CONTRATO_ATUAL": False}
    if not promocao:
        return {"REGUA": "NAO SEI", "PASSOS": passos, "PORQUE": "nunca promovida"}
    if (contrato or {}).get("FORMA") == "PAGINA_E_BOLETIM":
        return _passos_pagina_boletim(promocao, evidencia, contrato)
    dados = (evidencia or {}).get("DADOS") or {}
    acq = ((contrato or {}).get("ACQUISITION") or {})
    index = acq.get("INDEX_URL") or (contrato or {}).get("CANONICAL_ENTRY_URL") or ""
    passos["INDEX_URL"] = bool(index)

    alvos = dados.get("DETAIL_ENUMERATED")
    if alvos is None:
        alvos = dados.get("ALVOS_DESCOBERTOS")
    passos["DETAIL_LINKS"] = isinstance(alvos, int) and alvos >= MINIMO_DE_LIGACOES

    item = dados.get("ITEM_ABERTO") or {}
    url_item = item.get("URL") or ""
    aberto = (item.get("HTTP") == 200 and bool(url_item)
              and _sem_barra(url_item) != _sem_barra(index)
              and _sem_barra(url_item) != _sem_barra(_homepage(index))
              and _sem_barra(url_item) != _sem_barra(_homepage(url_item)))
    passos["ITEM_ABERTO"] = bool(aberto)

    # D32 (4): um item PDF prova corpo pela camada de texto (a esteira de PDF da Collection),
    # com a mesma exigencia de 800 caracteres; imagem sem texto (NEEDS_OCR) nao conta.
    corpo_html = (item.get("HTML_KIND") == "CONTENT"
                  and item.get("CAPA_OU_MATERIA") == MATERIA
                  and (item.get("PARAGRAPH_CHARACTERS") or 0) >= 800)
    corpo_pdf = (item.get("DOC_KIND") == "PDF"
                 and item.get("TEXT_LAYER") == "TEXT_LAYER_PRESENT"
                 and (item.get("TEXT_CHARACTERS") or 0) >= 800)
    passos["BODY_UTIL"] = dados.get("DETAIL_GATE_PASSED") is True and (corpo_html or corpo_pdf)

    quando = ((contrato or {}).get("ROUTE_PROVENANCE") or {}).get("INTEGRADO_EM")
    if not quando:
        passos["CONTRATO_ATUAL"] = True
    else:
        try:
            passos["CONTRATO_ATUAL"] = (datetime.fromisoformat(quando)
                                        <= datetime.fromisoformat(promocao["OBSERVED_AT"]))
        except (ValueError, KeyError, TypeError):
            passos["CONTRATO_ATUAL"] = False

    if all(passos.values()):
        return {"REGUA": REGUA_CURRENT, "PASSOS": passos,
                "PORQUE": "os quatro passos estao na evidencia e o contrato e o atual"}
    faltam = [k for k, v in passos.items() if not v]
    if dados.get("DETAIL_GATE_PASSED") is True and not passos["BODY_UTIL"]:
        porque = ("o gate passou por «nao parece capa», mas o corpo e %s/%s — BODY UTIL "
                  "nao provado; PASS_PARCIAL" % (item.get("HTML_KIND"), item.get("CAPA_OU_MATERIA")))
    else:
        porque = "PASS_PARCIAL: falta %s" % ",".join(faltam)
    return {"REGUA": REGUA_LEGACY, "PASSOS": passos, "PORQUE": porque}


def _contrato_atual(promocao: dict, contrato: dict | None) -> bool:
    quando = ((contrato or {}).get("ROUTE_PROVENANCE") or {}).get("INTEGRADO_EM")
    if not quando:
        return True
    try:
        return datetime.fromisoformat(quando) <= datetime.fromisoformat(promocao["OBSERVED_AT"])
    except (ValueError, KeyError, TypeError):
        return False


def _passos_pagina_boletim(promocao: dict, evidencia: dict | None, contrato: dict | None) -> dict:
    """PAGINA_BOLETIM/v1 — os passos NA EVIDENCIA do canario da forma. DATA_COMPROVADA e dita, mas
    NAO e exigida: a D42 manda que a data ausente fique UNKNOWN e o boletim seja colhido na mesma."""
    dados = (evidencia or {}).get("DADOS") or {}
    item = dados.get("ITEM_ABERTO") or {}
    c = contrato or {}
    aq = c.get("ACQUISITION") or {}
    passos = {
        "URL_FIXA": aq.get("STRATEGY") == "STATIC_ENDPOINT" and bool(aq.get("URL")),
        "RECOLHA_MUTAVEL": ((c.get("RECOLLECTION") or {}).get("DETAIL_CONTENT") == "MUTABLE"),
        "IDENTIDADE": (item.get("FORMA") == "PAGINA_E_BOLETIM" and bool(item.get("DOCUMENT_ID"))
                       and bool(item.get("CONTENT_SHA256"))),
        "CORPO_DO_BOLETIM": (dados.get("DETAIL_GATE_PASSED") is True
                             and (item.get("BOLETIM_CARACTERES") or 0) >= BOLETIM_MINIMO),
        "CONTRATO_ATUAL": _contrato_atual(promocao, c),
    }
    info = {"DATA_COMPROVADA": item.get("DATA_COMPROVADA") is True,
            "SOURCE_DATE_ISO": item.get("SOURCE_DATE_ISO") or "UNKNOWN"}
    if all(passos.values()):
        return {"REGUA": REGUA_PAGINA_BOLETIM, "PASSOS": passos, "INFO": info,
                "PORQUE": "a pagina e o boletim: identidade pelo motor, corpo recortado, recolha mutavel"}
    return {"REGUA": REGUA_LEGACY, "PASSOS": passos, "INFO": info,
            "PORQUE": "PASS_PARCIAL (pagina = boletim): falta %s" % ",".join(k for k, v in passos.items() if not v)}


def e_corrente(regua: str | None) -> bool:
    """A regua de hoje, para qualquer forma declarada (DETAIL/v1 ou PAGINA_BOLETIM/v1)."""
    return regua in REGUAS_CORRENTES


def regua_de(source_id: str, *, livro: dict | None = None,
             evidencias: dict | None = None, contratos: dict | None = None) -> str:
    """DETAIL/v1 se a evidencia da promocao tem os quatro passos; LEGACY caso
    contrario. `NAO SEI` se a fonte nunca foi promovida."""
    p = ultima_promocao(source_id, livro)
    if not p:
        return "NAO SEI"
    ev = (evidencias if evidencias is not None else _evidencias()).get(p.get("EVIDENCE_REF") or "")
    c = (contratos if contratos is not None else _contratos()).get(source_id)
    return passos_da_promocao(p, ev, c)["REGUA"]


def regua_manda(source_id: str | None) -> bool:
    """V1A: a fonte passa os 4 passos? E a condicao para a V1 do detector valer
    (`retrato_html.veredito`). Um so sitio para a pergunta; duvida = False."""
    if not source_id:
        return False
    try:
        return regua_de(source_id) == REGUA_CURRENT
    except Exception:                                            # noqa: BLE001
        return False


def contrato_de(source_id: str | None) -> dict | None:
    """O contrato que a regua le (o livro do Curator), para a V1 ler o INDEX_URL."""
    return _contratos().get(source_id) if source_id else None


def contrato_alterado_depois(source_id: str, promocao: dict | None,
                             contratos: dict | None = None) -> bool:
    """A rota mudou depois do READY? Le ROUTE_PROVENANCE.INTEGRADO_EM."""
    if not promocao:
        return False
    c = (contratos if contratos is not None else _contratos()).get(source_id) or {}
    quando = (c.get("ROUTE_PROVENANCE") or {}).get("INTEGRADO_EM")
    if not quando:
        return False
    try:
        return datetime.fromisoformat(quando) > datetime.fromisoformat(promocao["OBSERVED_AT"])
    except ValueError:
        return False


def _ready_do_outro_livro(ref: str) -> set | None:
    """Os READY do livro de outra arvore, por `git show`. None = NAO SEI."""
    try:
        r = subprocess.run(["git", "show", "%s:curadoria/LIFECYCLE-LEDGER-V1.json" % ref],
                           capture_output=True, text=True, encoding="utf-8",
                           cwd=str(RAIZ), timeout=60)
        if r.returncode != 0 or not r.stdout:
            return None
        est = {}
        for t in json.loads(r.stdout)["TRANSICOES"]:
            est[t["SOURCE_ID"]] = t["NEW_STATE"]
        return {s for s, e in est.items() if e == LC.READY_FOR_COLLECTION}
    except Exception:
        return None


def separar(*, outro_livro: str | None = OUTRO_LIVRO,
            ready_do_outro: set | None = None) -> dict:
    livro = LC._ler_bruto()
    ev = _evidencias()
    contratos = _contratos()
    est = {}
    for t in livro["TRANSICOES"]:
        est[t["SOURCE_ID"]] = t["NEW_STATE"]
    ready = sorted(s for s, e in est.items() if e == LC.READY_FOR_COLLECTION)

    legacy, current, alterados = [], [], []
    for sid in ready:
        p = ultima_promocao(sid, livro)
        r = regua_de(sid, livro=livro, evidencias=ev, contratos=contratos)
        alt = contrato_alterado_depois(sid, p, contratos)
        linha = {"SOURCE_ID": sid, "READY_RULE": r,
                 "PROMOVIDA_EM": p.get("OBSERVED_AT") if p else None,
                 "EVIDENCE_REF": p.get("EVIDENCE_REF") if p else None,
                 "CONTRATO_ALTERADO_DEPOIS_DO_READY": alt,
                 "SOURCE_CONTRACT_HASH": (contratos.get(sid) or {}).get("SOURCE_CONTRACT_HASH")}
        (current if e_corrente(r) else legacy).append(linha)
        if alt:
            alterados.append(sid)

    # As promocoes LEGACY que ja foram SUBSTITUIDAS: a fonte saiu de READY
    # para remedir. Ficam contadas, porque «nao apagar» inclui nao esquecer.
    substituidas = sorted(s for s in est
                          if est[s] != LC.READY_FOR_COLLECTION
                          and ultima_promocao(s, livro) is not None
                          and regua_de(s, livro=livro, evidencias=ev, contratos=contratos) == REGUA_LEGACY)

    if ready_do_outro is None and outro_livro:
        ready_do_outro = _ready_do_outro_livro(outro_livro)
    aqui = set(ready)
    if ready_do_outro is None:
        terceiro = {"OUTRO_LIVRO": outro_livro, "MEDIDO": False,
                    "PORQUE": "nao se conseguiu ler o livro da outra arvore — NAO SEI"}
    else:
        terceiro = {"OUTRO_LIVRO": outro_livro, "MEDIDO": True,
                    "READY_NO_OUTRO": len(ready_do_outro),
                    "NOS_DOIS": len(aqui & ready_do_outro),
                    "SO_AQUI": sorted(aqui - ready_do_outro),
                    "SO_NO_OUTRO": len(ready_do_outro - aqui),
                    "SO_NO_OUTRO_POR_TERRITORIO": _por_territorio(ready_do_outro - aqui)}

    return {
        "DATASET": "READY-SPLIT-V1",
        "LEI": ("READY_LEGACY (regua antiga) e READY_CURRENT (gate de detalhe) nao se "
                "misturam nem se apagam; a regua le-se na evidencia da promocao. Uma "
                "fonte READY so num dos livros e SO_NUM_DOS_LIVROS, nao e nenhuma das duas."),
        "GERADO_EM": LC.agora(),
        "READY_TOTAL": len(ready),
        "READY_LEGACY": len(legacy),
        "READY_CURRENT": len(current),
        "READY_LEGACY_SUBSTITUIDAS": len(substituidas),
        "LEGACY_COM_CONTRATO_ALTERADO": len(alterados),
        "SO_NUM_DOS_LIVROS": terceiro,
        "DETALHE_LEGACY": legacy,
        "DETALHE_CURRENT": current,
        "DETALHE_LEGACY_SUBSTITUIDAS": substituidas,
        "DETALHE_LEGACY_COM_CONTRATO_ALTERADO": alterados,
    }


def _por_territorio(ids) -> dict:
    out: dict = {}
    for s in ids:
        t = s.split("-")[1] if s.count("-") >= 2 else "?"
        out[t] = out.get(t, 0) + 1
    return dict(sorted(out.items()))


def remedir(source_ids: list[str], *, motivo: str) -> list[dict]:
    """Tira as READY_LEGACY com contrato novo de READY e manda-as ao canario
    pela regua de hoje. O READY antigo fica no livro; nada e promovido aqui."""
    feitas = []
    for sid in source_ids:
        if LC.estado_de(sid) != LC.READY_FOR_COLLECTION:
            feitas.append({"SOURCE_ID": sid, "FEITO": False,
                           "PORQUE": "nao esta READY: %s" % LC.estado_de(sid)})
            continue
        LC.registar(sid, LC.CANARY_PENDING, motivo,
                    evidence_ref="CONTRATO:ROUTE_PROVENANCE")
        t = F.enfileirar(sid, F.VALIDATE_ROUTE, priority=55,
                         motivo="remedir pela regua de detalhe: %s" % motivo[:80])
        feitas.append({"SOURCE_ID": sid, "FEITO": True, "TASK_ID": t["TASK_ID"]})
    return feitas


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    r = separar()
    SAIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("READY_TOTAL                    %d" % r["READY_TOTAL"])
    print("READY_LEGACY                   %d" % r["READY_LEGACY"])
    print("READY_CURRENT                  %d" % r["READY_CURRENT"])
    print("READY_LEGACY_SUBSTITUIDAS      %d" % r["READY_LEGACY_SUBSTITUIDAS"])
    print("LEGACY_COM_CONTRATO_ALTERADO   %d  %s" % (r["LEGACY_COM_CONTRATO_ALTERADO"],
                                                    r["DETALHE_LEGACY_COM_CONTRATO_ALTERADO"]))
    t = r["SO_NUM_DOS_LIVROS"]
    if t["MEDIDO"]:
        print("SO_NUM_DOS_LIVROS (%s)   nos dois %d · so aqui %d · so la %d"
              % (t["OUTRO_LIVRO"], t["NOS_DOIS"], len(t["SO_AQUI"]), t["SO_NO_OUTRO"]))
    else:
        print("SO_NUM_DOS_LIVROS              NAO SEI (%s)" % t["PORQUE"])
    if "--remedir" in argv:
        feitas = remedir(r["DETALHE_LEGACY_COM_CONTRATO_ALTERADO"],
                         motivo=("contrato alterado depois do READY (ROUTE_PROVENANCE); "
                                 "o READY antigo e LEGACY — remedir pela regua de detalhe"))
        print("REMEDIR: %s" % json.dumps(feitas, ensure_ascii=False))
        r2 = separar()
        SAIDA.write_text(json.dumps(r2, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("depois: READY_LEGACY %d · SUBSTITUIDAS %d · fila %s"
              % (r2["READY_LEGACY"], r2["READY_LEGACY_SUBSTITUIDAS"],
                 json.dumps(F.metricas())))
    print("escrito: %s" % SAIDA.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
