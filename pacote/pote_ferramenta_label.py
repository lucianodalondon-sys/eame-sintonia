#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SAIDA SELADA DA LABEL INTELLIGENCE, NA FORMA DO POTE · um adaptador, nao uma corrida.

    python3 pacote/pote_ferramenta_label.py              # escreve o pote da ferramenta
    python3 pacote/pote_ferramenta_label.py --conferir   # 0 = o ficheiro commitado e o deste payload

    le     italia-portale/client/italy-label-intelligence.js
           (window.ITALY_LABEL_INTELLIGENCE: o payload SELADO da ferramenta
            `pilot-label-intelligence`, Ministero della Salute, snapshot PROD_FTS_6_20260831)
           docs/casco/r7/POTE-R7.json
           (so os CABECALHOS dos doze compartimentos: nome, vistas, especies e chaves do
            contrato POTE_INTELLIGENCE_CASCO/v2 tal como o gerador ce775ff5 os escreveu)
    grava  docs/casco/ferramentas/POTE-FERRAMENTA-LABEL-INTELLIGENCE.json

PORQUE EXISTE (D114 + correcao do dono, 27/09 16:50)
----------------------------------------------------
    «os numeros que estavam no portal antigo nao eram mentiras, portfolio por
     exemplo bulas, parte da label intelligence, cheque o que ja tem e nao
     precisa coletar novamente, apenas organizar nos lugares novos e corretos»

Com o pote publicado, a rota Portafoglio/Etichette desenha SO o compartimento
`portfolio` do pote R7 — e a leitura dos rotulos, que ja estava selada no repo,
deixou de aparecer. A lei D97 diz que o casco mostra so o que a Intelligence
produziu; a Label Intelligence E uma INTELLIGENCE TOOL, e a sua saida pode ir ao
pote como PRODUTO DE FERRAMENTA — com a data do snapshot, sem recalcular.

O QUE ESTE FICHEIRO FAZ, E SO ISTO
-----------------------------------
1. Recalcula o selo (`CONTENT_SHA256`, pelas MESMAS quatro opcoes de
   `v1/inteligencia/selo.py`) e RECUSA se nao bater — nada de adaptar um payload
   que alguem editou.
2. Copia cada registo da ferramenta, inteiro, para `REGISTRO_DA_FERRAMENTA` de um
   objeto do pote: os 166 produtos e os 210 objetos de registro. Os agregados
   (coberturas, crop_check, pair_check, history...) e as 54 versoes do registro vao
   inteiros para `FERRAMENTA`. Do pote da para reconstruir o payload e o selo.
3. Marca tudo `PRODUZIDO_POR` = a ferramenta e o seu RUN. Nenhum objeto diz
   «Intelligence R7»: nenhuma corrida da Intelligence tocou nisto.

O QUE ELE NAO FAZ
-----------------
Nao cruza, nao conta de novo, nao escolhe o que e importante, nao traduz, nao
muda um estado da ferramenta, nao promove uso autorizado a oportunidade (o portao
G-01 da ferramenta continua fechado). Nao publica: o pote da ferramenta fica em
docs/, e quem o instala no casco e o coordenador.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = Path(os.path.dirname(HERE))

FONTE = RAIZ / "italia-portale/client/italy-label-intelligence.js"
PREFIXO = "window.ITALY_LABEL_INTELLIGENCE = "
MOLDE = RAIZ / "docs/casco/r7/POTE-R7.json"
DESTINO = RAIZ / "docs/casco/ferramentas/POTE-FERRAMENTA-LABEL-INTELLIGENCE.json"

CONTRATO = "POTE_INTELLIGENCE_CASCO/v2"
MARCA = "EXPERIMENTAL · NAO_PARA_CLIENTE"
NAO_SEI = "NAO SEI"
FERRAMENTA = "pilot-label-intelligence"
DOZE = ("meeting", "future", "windows", "market", "voices", "competitors", "science",
        "portfolio", "archive", "sources", "field", "casa")
CABECALHO = ("MARCA", "NAO_PARA_CLIENTE", "COMPARTIMENTO", "NOME_IT", "VISTAS_DO_CASCO",
             "ESPECIES_ADMITIDAS", "CONTRATO_CHAVES")
REGISTROS = ("products", "objects", "versions")
# A fonte oficial dos dois tipos de registo e a mesma: os `objects` da ferramenta
# dizem-na em SOURCE_ID; os `products` nao a repetem.
SOURCE_ID = "IT-MINSAL-FITOSANITARI"


class Recusado(Exception):
    pass


def _rel(p: Path) -> str:
    return p.relative_to(RAIZ).as_posix()


def ler_payload(texto: str) -> dict:
    """O mesmo corte que `italia-portale/audit/etichette-gate.mjs` faz: do prefixo ao fim, sem o `;`."""
    i = texto.index(PREFIXO)
    corpo = texto[i + len(PREFIXO):].rstrip()
    if corpo.endswith(";"):
        corpo = corpo[:-1]
    return json.loads(corpo)


def selo(payload: dict) -> str:
    """`v1/inteligencia/selo.py::conteudo_sha` — as quatro opcoes, PRODUCED_BY de fora."""
    corpo = {k: v for k, v in payload.items() if k != "PRODUCED_BY"}
    return hashlib.sha256(json.dumps(corpo, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def canonico(x) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _v(x):
    """Valor da ferramenta para uma chave do pote: vazio vira NAO SEI, nunca some."""
    return NAO_SEI if x is None or x == "" else x


def _data_iso(aaaammdd: str) -> str:
    s = str(aaaammdd or "")
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if len(s) == 8 and s.isdigit() else _v(aaaammdd)


def _objeto_base(oid, run_id, produzido_por):
    return {
        "MARCA": MARCA, "NAO_PARA_CLIENTE": True, "COMPARTIMENTO": "portfolio",
        "OBJETO_ID": oid, "ESPECIE": "FINDING",
        "ESPECIE_DITA_POR": "FERRAMENTA " + FERRAMENTA,
        "ESTADO": "SAIDA_DE_FERRAMENTA_SELADA",
        "PRODUZIDO_POR": produzido_por,
        "CORRIDA_SINTETICA": False,
        "_RUN": run_id,
    }


def objeto_de_produto(p: dict, P: dict, run_id: str, produzido_por: str) -> dict:
    usos = "; ".join(f"{u.get('crop')} × {u.get('target')} [{u.get('proof')}]" for u in (p.get("uses") or []))
    o = _objeto_base(f"LI-PROD-{p['reg']}@{P['RUN']}", run_id, produzido_por)
    chaves = {
        "PRODUCT_ID": _v(p.get("reg")),
        "CROP_ID": NAO_SEI,
        "TARGET_ID": NAO_SEI,
        "ACTIVE_INGREDIENT_ID": _v(p.get("actives")),
        "REGISTRATION_VERSION": _v(p.get("snapshot")),
    }
    o.update({
        "CHAVES": chaves,
        "CHAVES_NAO_SEI": [k for k, v in chaves.items() if v == NAO_SEI],
        "FORA_DO_CONTRATO": {
            "NOME": _v(p.get("name")),
            "TITULAR": _v(p.get("holder")),
            "ESTADO_NO_REGISTRO": _v(p.get("status")),
            "ATIVIDADE": _v(p.get("activity")),
            "FORMULACAO": _v(p.get("formulation")),
            "SCADENZA": _v(p.get("expiry")),
            "DIAS_ATE_A_SCADENZA": f"{_v(p.get('dte'))} (contados pela ferramenta em BUILT_AT {P['BUILT_AT']}, nao hoje)",
            "VALIDADE_DA_ETIQUETA": _v(p.get("label_validity_state")),
            "DOSE": _v(p.get("dose_state")),
            "USOS_LIDOS_PELA_FERRAMENTA": usos or "nenhum uso lido",
        },
        "PORQUE": (f"saida selada da ferramenta {FERRAMENTA} ({P['RUN']}, snapshot {P['DATA_SNAPSHOT_ID']}): "
                   "leitura do rotulo oficial ADAMA; copiada, nao recalculada"),
        "CONTRADIZ": NAO_SEI,
        "INCERTEZA": ("CROP_ID e TARGET_ID ficam NAO SEI por objeto: o produto tem varios usos, e cada par "
                      "cultura × alvo leva a prova da propria ferramenta em USOS_LIDOS; "
                      "USO AUTORIZADO NAO E OPORTUNIDADE COMERCIAL"),
        "PROVA": [
            {"ITEM_ID": f"LI:products[reg={p['reg']}]",
             "RAW_OBSERVATION_ID": f"{_v(p.get('snapshot'))}#{p['reg']}",
             "SOURCE_ID": SOURCE_ID,
             "DOCUMENT_ID": f"ETICHETTA sha256={_v(p.get('pdf_sha'))}",
             "CORRIDA_UPSTREAM": _v(p.get("run")),
             "URL": _v(p.get("pdf_url")),
             "PUBLICADO_EM": _v(p.get("label_effective")),
             "COLHIDO_EM": _v(p.get("captured_at")),
             "FACT_TIME": _v(p.get("label_validity_quote")),
             "INTELLIGENCE_RUN_ID": run_id},
            {"ITEM_ID": f"LI:products[reg={p['reg']}]",
             "RAW_OBSERVATION_ID": f"{_v(p.get('snapshot'))}#{p['reg']}",
             "SOURCE_ID": SOURCE_ID,
             "DOCUMENT_ID": f"{_v(p.get('snapshot'))}.csv sha256={_v(p.get('snapshot_sha'))}",
             "CORRIDA_UPSTREAM": _v(p.get("run")),
             "URL": _v(p.get("source_url")),
             "PUBLICADO_EM": _data_iso(P["DATA_DATE"]),
             "COLHIDO_EM": _v(p.get("captured_at")),
             "FACT_TIME": NAO_SEI,
             "INTELLIGENCE_RUN_ID": run_id},
        ],
        "REGISTRO_DA_FERRAMENTA": p,
    })
    return o


def objeto_de_registro(i: int, r: dict, P: dict, run_id: str, produzido_por: str) -> dict:
    # INTELLIGENCE_OBJECT_ID da ferramenta NAO e unico (201 distintos em 210): a posicao entra no id.
    o = _objeto_base(f"LI-OBJ-{i:03d}-{r.get('INTELLIGENCE_OBJECT_ID')}@{P['RUN']}", run_id, produzido_por)
    chaves = {
        "PRODUCT_ID": _v(r.get("PRODUCT_ID")),
        "CROP_ID": NAO_SEI,
        "TARGET_ID": NAO_SEI,
        "ACTIVE_INGREDIENT_ID": NAO_SEI,
        "REGISTRATION_VERSION": _v(r.get("SOURCE_DOCUMENT_AFTER")),
    }
    o.update({
        "CHAVES": chaves,
        "CHAVES_NAO_SEI": [k for k, v in chaves.items() if v == NAO_SEI],
        "FORA_DO_CONTRATO": {
            "NOME": _v(r.get("PRODUCT_NAME")),
            "TIPO": _v(r.get("OBJECT_TYPE")),
            "ANTES": _v(r.get("BEFORE_VALUE")),
            "DEPOIS": _v(r.get("AFTER_VALUE")),
            "FACTO": _v(r.get("FACT")),
            "ESTADO_DA_PROVA": _v(r.get("PROOF_STATE")),
            "CONFIANCA": _v(r.get("CONFIDENCE_STATE")),
            "JANELA": _v(r.get("TIME_WINDOW")),
        },
        "PORQUE": (f"objeto de registro da ferramenta {FERRAMENTA} ({P['RUN']}): diferenca entre snapshots "
                   "oficiais ou estado de leitura; copiado, nao recalculado"),
        "CONTRADIZ": NAO_SEI,
        "INCERTEZA": (f"PROOF_STATE da ferramenta: {_v(r.get('PROOF_STATE'))}; "
                      f"implicacao de negocio: {_v(r.get('POTENTIAL_BUSINESS_IMPLICATION'))}"),
        "PROVA": [
            {"ITEM_ID": f"LI:objects[{i}]",
             "RAW_OBSERVATION_ID": _v(r.get("EVIDENCE_LOCATION")),
             "SOURCE_ID": _v(r.get("SOURCE_ID")),
             "DOCUMENT_ID": _v(r.get("SOURCE_DOCUMENT_AFTER")),
             "CORRIDA_UPSTREAM": P["RUN"],
             "URL": _v(r.get("SOURCE_URL")),
             "PUBLICADO_EM": _v(r.get("VALID_FROM")),
             "COLHIDO_EM": _v(r.get("CAPTURED_AT")),
             "FACT_TIME": _v(r.get("DETECTED_AT")),
             "INTELLIGENCE_RUN_ID": run_id},
        ],
        "REGISTRO_DA_FERRAMENTA": r,
    })
    return o


def construir(texto_fonte: str, molde: dict) -> dict:
    P = ler_payload(texto_fonte)
    declarado = (P.get("PRODUCED_BY") or {}).get("CONTENT_SHA256")
    recalculado = selo(P)
    if not declarado or recalculado != declarado:
        raise Recusado(f"selo nao bate: declarado {declarado} recalculado {recalculado}")
    for k in REGISTROS:
        if not isinstance(P.get(k), list):
            raise Recusado(f"payload sem a lista {k}")
    run_id = f"FERRAMENTA:{FERRAMENTA}@{P['RUN']}"
    produzido_por = f"{FERRAMENTA} ({P['TOOL']} {P['VERSION']}) · {P['RUN']} · {P['RULESET_VERSION']}"

    objetos = [objeto_de_produto(p, P, run_id, produzido_por) for p in P["products"]]
    objetos += [objeto_de_registro(i, r, P, run_id, produzido_por) for i, r in enumerate(P["objects"])]
    for o in objetos:
        del o["_RUN"]
    ids = [o["OBJETO_ID"] for o in objetos]
    if len(set(ids)) != len(ids):
        raise Recusado("OBJETO_ID repetido")

    mc = molde.get("COMPARTIMENTOS") or {}
    if set(mc) != set(DOZE):
        raise Recusado("o molde nao traz os doze compartimentos do contrato")
    comps = {}
    for k in DOZE:
        e = {c: mc[k][c] for c in CABECALHO}
        objs = objetos if k == "portfolio" else []
        e.update({
            "OBJETOS": objs,
            "UNIVERSO": {"INTELLIGENCE_RUN_ID": run_id, "OBJETOS": len(objs),
                         "LEITURA": "objetos desta SAIDA DE FERRAMENTA; zero aqui nao prova ausencia no mundo"},
            "ESTADO": "COM_OBJETOS" if objs else "VAZIO",
            "PORQUE_VAZIO": None if objs else "FERRAMENTA_NAO_ALIMENTA_ESTA_VISTA",
            "PORQUE_TEXTO": None if objs else (f"a ferramenta {FERRAMENTA} le rotulos e o registro oficial; "
                                               "so alimenta Portafoglio/Etichette"),
            "RECUSADOS_AQUI": 0,
            "LACUNAS": [],
        })
        comps[k] = e

    fonte_sha = hashlib.sha256(FONTE.read_bytes()).hexdigest() if FONTE.exists() else NAO_SEI
    agregados = {k: v for k, v in P.items() if k not in REGISTROS and k != "PRODUCED_BY"}
    return {
        "SCHEMA": CONTRATO,
        "MARCA": MARCA,
        "NAO_PARA_CLIENTE": True,
        "INTELLIGENCE_RUN_ID": run_id,
        "ENTRADA": "SAIDA_DE_INTELLIGENCE_TOOL",
        "PRODUZIDO_POR": {
            "FERRAMENTA": FERRAMENTA,
            "NOME": P["TOOL"], "VERSAO": P["VERSION"], "RUN": P["RUN"],
            "RULESET_VERSION": P["RULESET_VERSION"],
            "MODULE": P["PRODUCED_BY"].get("MODULE"),
            "MODULE_SHA256": P["PRODUCED_BY"].get("MODULE_SHA256"),
            "CONTENT_SHA256_DECLARADO": declarado,
            "CONTENT_SHA256_RECALCULADO": recalculado,
            "NAO_E": "uma corrida da Intelligence (R7 ou outra): nenhuma corrida recalculou isto",
        },
        "SNAPSHOT": {k: P[k] for k in ("COUNTRY", "BUILT_AT", "DATA_DATE", "DATA_SNAPSHOT_ID", "NEWEST_CHANGE_AT",
                                       "COLLECTED_AT", "SOURCE_AUTHORITY", "LICENSE")},
        "ORIGEM": {
            "FICHEIRO": _rel(FONTE),
            "FICHEIRO_SHA256": fonte_sha,
            "PAYLOAD_ORIGINAL": ("v1/dados/CASCO-PAYLOAD.json no ramo claude/label-intelligence-v1-italy "
                                 "(dito no cabecalho do ficheiro; o ramo nao foi lido aqui)"),
            "ADAPTADOR": "pacote/pote_ferramenta_label.py",
            "MOLDE_DOS_COMPARTIMENTOS": _rel(MOLDE),
        },
        "SOURCE_HEAD": {"FERRAMENTA_RUN": P["RUN"], "FICHEIRO_SHA256": fonte_sha},
        "CORTE": {"DATA_DATE": P["DATA_DATE"], "DATA_SNAPSHOT_ID": P["DATA_SNAPSHOT_ID"],
                  "COLLECTED_AT": P["COLLECTED_AT"], "BUILT_AT": P["BUILT_AT"]},
        "RESULT_STATE": "DONE",
        "CORRIDA_SINTETICA": False,
        "LEI": ("saida de INTELLIGENCE TOOL copiada: o casco desenha isto com a data do snapshot; nao refaz leitura, "
                "nao completa NAO SEI, nao promove uso autorizado a oportunidade (G-01 fechado)"),
        "CONTAGENS": {k: len(P[k]) for k in REGISTROS},
        "FERRAMENTA": {"AGREGADOS": agregados, "VERSOES": P["versions"], "PRODUCED_BY": P["PRODUCED_BY"]},
        "COMPARTIMENTOS": comps,
        "LACUNAS_SEM_COMPARTIMENTO": [],
        "RECUSADOS": [],
    }


def reconstruir_payload(pote: dict) -> dict:
    """O caminho de volta: do pote da ferramenta ao payload selado. Se isto nao der o mesmo selo, o adaptador perdeu algo."""
    F = pote["FERRAMENTA"]
    objs = pote["COMPARTIMENTOS"]["portfolio"]["OBJETOS"]
    p = dict(F["AGREGADOS"])
    p["products"] = [o["REGISTRO_DA_FERRAMENTA"] for o in objs if o["OBJETO_ID"].startswith("LI-PROD-")]
    p["objects"] = [o["REGISTRO_DA_FERRAMENTA"] for o in objs if o["OBJETO_ID"].startswith("LI-OBJ-")]
    p["versions"] = F["VERSOES"]
    p["PRODUCED_BY"] = F["PRODUCED_BY"]
    return p


def texto() -> str:
    pote = construir(FONTE.read_text(encoding="utf-8"), json.loads(MOLDE.read_text(encoding="utf-8")))
    return json.dumps(pote, ensure_ascii=False, indent=1) + "\n"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        t = texto()
    except Recusado as e:
        print("RECUSADO: " + str(e))
        return 3
    if "--conferir" in argv:
        atual = DESTINO.read_bytes().decode("utf-8") if DESTINO.exists() else ""
        if atual != t:
            print(f"DIFERENTE: {_rel(DESTINO)} nao e o que o payload selado produz — corra sem --conferir")
            return 1
        print(f"IGUAL: {_rel(DESTINO)} e o do payload selado")
        return 0
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with open(DESTINO, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(t)
    c = json.loads(t)["CONTAGENS"]
    print(f"ESCRITO {_rel(DESTINO)} · {c['products']} produtos · {c['objects']} objetos · {c['versions']} versoes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
