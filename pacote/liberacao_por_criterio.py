#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LIBERACAO POR CRITERIO — o C8 automatico (decisao do dono D-C8-AUTO, Diretoria 30/09/2026 09:05).

    «Objeto que cumpra integralmente C1–C7, as regras vigentes de inteligencia, os requisitos do LAB e o contrato
     de exibicao pode receber C8 automaticamente. Objeto que nao cumpra fica bloqueado. Nao e necessaria minha
     aprovacao objeto por objeto.» (Luciano, dono)

Dono: Intelligence (a liberacao e da Intelligence, objeto por objeto — CONTRATO-LIBERACAO-POR-OBJETO-v2.2).
Nenhuma regua nova: C1..C7 sao as do contrato v2.2 (as mesmas de PARA-O-CASCO-R9/montar_r9.py), agora calculadas
por REGRA a partir do que o motor ja escreve no objeto (EVIDENCE_SPAN, FACT_TIME_BASIS com posicao, trecho do lugar,
prova ate ao RAW). O que mudou e SO o C8: deixa de ser uma frase do dono por objeto e passa a ser
`REGRA_C8_AUTO`, que so passa quando C1..C7 = PASSOU. Qualquer falha -> NAO_PARA_CLIENTE com o motivo gravado.

    C1 PROVA_DO_ARQUIVO          DOCUMENT_ID sabido; RAW_SHA256/RAW_STORAGE_PATH iguais aos da Sala; o byte e RELIDO no
                                 armazem e o sha256 bate; o trecho da afirmacao esta literal no texto do item.
    C2 DATA_PROPRIA              trecho da data literal no texto, na MESMA seccao (entre quebras \\f) da afirmacao;
                                 origem da data nunca calculada da publicacao (RELATIVO_D63 falha).
    C3 LUGAR_PROPRIO             trecho do lugar literal, na mesma seccao; lugar da fonte nunca e lugar do fato.
    C4 LIGACAO_ADAMA             `porta_da_referencia.conferir_ligacao` sem falhas e estado D123 valido.
    C5 SEM_DUPLICADO             nenhum outro objeto liberado com o mesmo item + mesmo trecho.
    C6 ESPECIE_DO_COMPARTIMENTO  tabela do gerador do dono (pote_intelligence_casco.COMPARTIMENTOS).
    C7 SO_SAIDA_DA_INTELLIGENCE  ESPECIE_DITA_POR = INTELLIGENCE e prova = item da Sala.
    C8 REGRA_C8_AUTO             PASSOU sse C1..C7 PASSOU (+ G0 da afirmacao PASSOU, regra vigente do motor).

Objetos sem afirmacao propria (rendimento de fonte, facto sobre o futuro sem lugar, sinal de documento inteiro)
falham C2/C3 por regra e ficam BLOQUEADOS — nunca ha liberacao por omissao (conferencia ausente = nao liberado).

    python pacote/liberacao_por_criterio.py --copia <pasta da copia so-leitura> --afirmacoes <AFIRMACOES.json>
                                            --armazem <raiz do armazem> --entrega <pasta PARA-O-CASCO-AUTO>
                                            [--hoje AAAA-MM-DD]
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import pote_intelligence_casco as P      # noqa: E402 — gerador e fiscal do dono
import validar_pote_v2 as VP             # noqa: E402
import porta_da_referencia as PORTA      # noqa: E402

REGRA = "REGRA_C8_AUTO"
DECISAO = ("D-C8-AUTO · Luciano (dono), sala SINTONIA DIRETORIA 30/09/2026 09:05: C8 automatico por criterio — "
           "objeto que cumpre integralmente C1-C7 recebe C8 sem aprovacao por objeto; o resto bloqueia")
PASSOU = "PASSOU"
NS = "NAO SEI"
CONFERENCIAS = ("C1_PROVA_DO_ARQUIVO", "C2_DATA_PROPRIA", "C3_LUGAR_PROPRIO", "C4_LIGACAO_ADAMA", "C5_SEM_DUPLICADO",
                "C6_ESPECIE_DO_COMPARTIMENTO", "C7_SO_SAIDA_DA_INTELLIGENCE")
ORIGENS_DE_DATA_PROPRIA = ("LITERAL", "CABECALHO_D147", "RELATIVA_ANCORADA_D149")
#: LAB E5 (30/09): TRECHO_* = CITACAO literal do texto da Sala, cada uma com a sua posicao em SECAO (*_EM).
#: Nenhum outro campo pode usar o prefixo — interpretacao do sistema tem outro nome (DATA_LEGIVEL_INTERPRETADA).
TRECHOS_LITERAIS = {"TRECHO_DA_AFIRMACAO": "AFIRMACAO_EM", "TRECHO_DA_DATA": "DATA_EM", "TRECHO_DO_LUGAR": "LUGAR_EM"}


def _como_se_le(linha: str) -> str:
    """Letras dobradas do negrito do PDF desfeitas pela regra do DONO (leis/tempo_da_afirmacao.como_se_le, ramo
    produtor-afirmacoes-v1). Sem o dono disponivel, fica o literal — nunca uma segunda copia da regra."""
    try:
        import tempo_da_afirmacao as TA  # noqa: PLC0415
    except ImportError:
        return linha
    return TA.como_se_le(linha)


def _sabido(v) -> bool:
    return v not in (None, "", NS, "NAO_SEI", "UNKNOWN", "?")


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def seccao(texto: str, i: int) -> tuple[int, int]:
    """Seccao do contrato v2.2 = entre quebras de pagina \\f."""
    ini = texto.rfind("\f", 0, i)
    fim = texto.find("\f", i)
    return (0 if ini < 0 else ini), (len(texto) if fim < 0 else fim)


def conferir_objeto(o: dict, comp: str, linhas: dict, armazem: Path | None, vistos: set, cache: dict) -> dict:
    """-> {C1..C7: PASSOU | FALHOU: motivo, C8: ...}. Puro sobre (objeto, texto da Sala, armazem)."""
    c = {}
    prova = o.get("PROVA") or []
    fora = o.get("FORA_DO_CONTRATO") or {}
    fonte = fora.get("DA_FONTE") or {}
    span = fonte.get("EVIDENCE_SPAN") if isinstance(fonte.get("EVIDENCE_SPAN"), dict) else None
    base = fonte.get("FACT_TIME_BASIS") if isinstance(fonte.get("FACT_TIME_BASIS"), dict) else None
    interp = fora.get("INTERPRETACAO_DO_SISTEMA") or {}
    p0 = prova[0] if prova else {}
    linha = linhas.get(str(p0.get("ITEM_ID")))
    texto = (linha or {}).get("texto") or ""

    # C1
    f = []
    if len(prova) != 1 or "CLAIM_ID" not in p0:
        f.append("objeto sem UMA afirmacao propria (prova de documento inteiro ou agregado)")
    if linha is None:
        f.append("item da prova fora do corte da Sala")
    else:
        if not _sabido(p0.get("DOCUMENT_ID")) or not linha.get("raw_document_key"):
            f.append("DOCUMENT_ID vazio")
        if p0.get("RAW_SHA256") != linha.get("raw_sha256") or p0.get("RAW_STORAGE_PATH") != linha.get("raw_storage_path"):
            f.append("RAW_SHA256/RAW_STORAGE_PATH da prova != Sala")
        lugar = armazem / str(linha.get("raw_storage_path")) if armazem and linha.get("raw_storage_path") else None
        if lugar is None or not lugar.is_file():
            f.append("RAW ausente no armazem")
        else:
            k = str(lugar)
            if k not in cache:
                cache[k] = _sha_bytes(lugar.read_bytes())
            if cache[k] != linha.get("raw_sha256"):
                f.append("sha do byte relido != raw_asset.sha256")
        if not span or texto[span.get("INICIO", -1):span.get("FIM", -1)] != span.get("TRECHO"):
            f.append("trecho da afirmacao nao esta literal no texto, na posicao declarada")
    c["C1_PROVA_DO_ARQUIVO"] = PASSOU if not f else "FALHOU: " + "; ".join(f)

    # C2
    if not span or not base or not isinstance(base.get("INICIO"), int):
        c["C2_DATA_PROPRIA"] = "FALHOU: data sem trecho proprio com posicao"
    elif texto[base["INICIO"]:base["FIM"]] != base.get("TRECHO"):
        c["C2_DATA_PROPRIA"] = "FALHOU: trecho da data nao esta literal no texto"
    elif interp.get("FACT_TIME_ORIGEM") not in ORIGENS_DE_DATA_PROPRIA:
        c["C2_DATA_PROPRIA"] = "FALHOU: origem da data %s (calculada ou nao propria)" % interp.get("FACT_TIME_ORIGEM")
    elif seccao(texto, span["INICIO"]) != seccao(texto, base["INICIO"]):
        c["C2_DATA_PROPRIA"] = "FALHOU: data fora da seccao da afirmacao"
    else:
        c["C2_DATA_PROPRIA"] = PASSOU

    # C3
    trecho_lugar = fonte.get("FACT_LOCATION_TRECHO")
    onde = fonte.get("FACT_LOCATION_ONDE") if isinstance(fonte.get("FACT_LOCATION_ONDE"), dict) else None
    if not span or not _sabido(trecho_lugar) or not _sabido((o.get("CHAVES") or {}).get("FACT_LOCATION")):
        c["C3_LUGAR_PROPRIO"] = "FALHOU: lugar do fato sem trecho proprio"
    elif not onde or not isinstance(onde.get("INICIO"), int) or not isinstance(onde.get("FIM"), int):
        # LAB E5 (30/09): lugar sem posicao nao se prova no texto («Puglia» 16x). O juiz nao afrouxa.
        c["C3_LUGAR_PROPRIO"] = "FALHOU: lugar sem posicao (ONDE) provada pelo produtor"
    elif texto[onde["INICIO"]:onde["FIM"]] != trecho_lugar or onde.get("TRECHO") != trecho_lugar:
        c["C3_LUGAR_PROPRIO"] = "FALHOU: trecho do lugar nao esta literal no texto, na posicao declarada"
    elif not (span["INICIO"] <= onde["INICIO"] and onde["FIM"] <= span["FIM"]):
        c["C3_LUGAR_PROPRIO"] = "FALHOU: trecho do lugar fora do trecho da afirmacao"
    elif o.get("LOCATION_SOURCE") in (None, "UNRESOLVED") and fora.get("LOCATION_SOURCE") in (None, "UNRESOLVED"):
        c["C3_LUGAR_PROPRIO"] = "FALHOU: LOCATION_SOURCE nao resolvido"
    else:
        c["C3_LUGAR_PROPRIO"] = PASSOU

    # C4
    lig = o.get("LIGACAO_ADAMA")
    fl = PORTA.conferir_ligacao(lig) if isinstance(lig, dict) else ["sem LIGACAO_ADAMA"]
    c["C4_LIGACAO_ADAMA"] = PASSOU if not fl else "FALHOU: " + "; ".join(map(str, fl))[:300]

    # C5
    k = (str(p0.get("ITEM_ID")), str((span or {}).get("TRECHO")))
    c["C5_SEM_DUPLICADO"] = PASSOU if k not in vistos else "FALHOU: afirmacao repetida"

    # C6
    c["C6_ESPECIE_DO_COMPARTIMENTO"] = (PASSOU if o.get("ESPECIE") in P.COMPARTIMENTOS.get(comp, {}).get("ESPECIES", ())
                                        else "FALHOU: especie fora do compartimento")
    # C7
    c["C7_SO_SAIDA_DA_INTELLIGENCE"] = (PASSOU if o.get("ESPECIE_DITA_POR") == "INTELLIGENCE" and prova
                                        and all(_sabido(p.get("ITEM_ID")) for p in prova)
                                        and all(p.get("G0") == PASSOU for p in prova)
                                        else "FALHOU: nao e objeto da Intelligence com G0 PASSOU")

    ok = all(c[x] == PASSOU for x in CONFERENCIAS)
    c["C8_DECISAO_DO_DONO"] = (PASSOU + " · " + REGRA + " · " + DECISAO) if ok else \
        "FALHOU: %s so libera com C1-C7 PASSOU (falhou: %s)" % (REGRA, ", ".join(x for x in CONFERENCIAS if c[x] != PASSOU))
    if ok:
        vistos.add(k)
    return c


def liberar(pote: dict, linhas: dict, armazem: Path | None, run_id: str) -> tuple[dict, dict]:
    """Carimba LIBERACAO por objeto no pote (copia). -> (pote carimbado, {OBJETO_ID: conferencia})."""
    pote = json.loads(json.dumps(pote, ensure_ascii=False))
    vistos, cache, conf = set(), {}, {}
    for comp, e in pote["COMPARTIMENTOS"].items():
        for o in e["OBJETOS"]:
            c = conferir_objeto(o, comp, linhas, armazem, vistos, cache)
            ok = c["C8_DECISAO_DO_DONO"].startswith(PASSOU)
            o["LIBERACAO"] = "LIBERADO_PARA_CLIENTE" if ok else "NAO_PARA_CLIENTE"
            o["CONFERENCIA_DE_LIBERACAO"] = c
            o["LIBERADO_POR"] = REGRA if ok else NS
            o["LIBERADO_NA_CORRIDA"] = run_id
            if ok:
                fonte = o["FORA_DO_CONTRATO"]["DA_FONTE"]
                for p in o["PROVA"]:
                    p.update({"TRECHO_DA_AFIRMACAO": fonte["EVIDENCE_SPAN"]["TRECHO"],
                              "TRECHO_DA_DATA": fonte["FACT_TIME_BASIS"]["TRECHO"],
                              "TRECHO_DO_LUGAR": fonte["FACT_LOCATION_TRECHO"],
                              "SECAO": {"AFIRMACAO_EM": fonte["EVIDENCE_SPAN"]["INICIO"],
                                        "DATA_EM": fonte["FACT_TIME_BASIS"]["INICIO"],
                                        "LUGAR_EM": fonte["FACT_LOCATION_ONDE"]["INICIO"]}})
                    legivel = _como_se_le(p["TRECHO_DA_DATA"])
                    if legivel != p["TRECHO_DA_DATA"]:
                        # LAB E5 (30/09): isto NAO e citacao — e o cabecalho desdobrado pela regra do dono. Todo campo
                        # TRECHO_* e literal no texto da Sala na sua posicao; a leitura do sistema tem outro nome (D112 r4).
                        p["DATA_LEGIVEL_INTERPRETADA"] = legivel
                    naoliteral = [k for k in p if k.startswith("TRECHO_") and k not in TRECHOS_LITERAIS]
                    if naoliteral:
                        raise ValueError("campo TRECHO_ que nao e citacao literal: %s" % naoliteral)
            conf[o["OBJETO_ID"]] = dict(c, COMPARTIMENTO=comp, ESPECIE=o.get("ESPECIE"), LIBERACAO=o["LIBERACAO"])
    return pote, conf


def so_liberados(pote: dict) -> dict:
    """O pote PARA_CLIENTE: so objetos LIBERADO_PARA_CLIENTE (contrato v2.2 §3: dois potes por corrida)."""
    p = json.loads(json.dumps(pote, ensure_ascii=False))
    for e in p["COMPARTIMENTOS"].values():
        antes = len(e["OBJETOS"])
        e["OBJETOS"] = [o for o in e["OBJETOS"] if o.get("LIBERACAO") == "LIBERADO_PARA_CLIENTE"]
        if antes and not e["OBJETOS"]:
            e["ESTADO"] = "VAZIO"
            e["PORQUE_VAZIO"] = "NENHUM_OBJETO_LIBERADO"
            e["PORQUE_TEXTO"] = ("%d objeto(s) desta corrida neste compartimento ficaram BLOQUEADOS pela %s "
                                 "(C1-C7 nao passaram); estao no POTE-EXPERIMENTAL.json e em BLOQUEADOS.json" % (antes, REGRA))
    n = sum(len(e["OBJETOS"]) for e in p["COMPARTIMENTOS"].values())
    p["OBJETOS_LIBERADOS"] = n
    p["POTE_DA_CORRIDA"] = "PARA_CLIENTE"
    p["LIBERACAO_POR_CRITERIO"] = {"REGRA": REGRA, "DECISAO": DECISAO, "CONTRATO": "v2.2 C1-C7 + C8 por regra"}
    return p


def _sha(p: Path) -> str:
    return _sha_bytes(p.read_bytes())


def entregar(pote_cliente: dict, pote_todo: dict, conf: dict, entrega: Path, extra: dict) -> dict:
    """POTE.json (so liberados) + BLOQUEADOS.json + MANIFESTO.json + SHA256SUMS.txt (ULTIMO). Troca-se inteira."""
    nova = entrega.with_name(entrega.name + ".nova")
    shutil.rmtree(nova, ignore_errors=True)
    nova.mkdir(parents=True)
    w = lambda n, d: (nova / n).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",  # noqa: E731
                                           encoding="utf-8", newline="\n")
    w("POTE.json", pote_cliente)
    w("POTE-EXPERIMENTAL.json", pote_todo)
    bloq = {oid: c for oid, c in conf.items() if c["LIBERACAO"] != "LIBERADO_PARA_CLIENTE"}
    w("BLOQUEADOS.json", {"REGRA": REGRA, "N": len(bloq), "OBJETOS": bloq})
    man = dict(extra, INTELLIGENCE_RUN_ID=pote_cliente.get("INTELLIGENCE_RUN_ID"),
               RESULT_STATE=pote_cliente.get("RESULT_STATE"), CORRIDA_SINTETICA=pote_cliente.get("CORRIDA_SINTETICA"),
               SOURCE_HEAD=pote_cliente.get("SOURCE_HEAD"), GERADO_EM=datetime.now(timezone.utc).isoformat(),
               GERADO_POR="pacote/liberacao_por_criterio.py (" + REGRA + ")",
               POTE={"ARQUIVO": "POTE.json", "SHA256_ARQUIVO": _sha(nova / "POTE.json"),
                     # o sha do JSON canonico (chaves ordenadas, compacto, UTF-8): o POTE_SHA256 que o envelope leva
                     # no ar e que a prova reversa compara (portoes/PUBLICACAO-AUTOMATICA.json -> NO_MANIFESTO)
                     "SHA256_CANONICO": _sha_bytes(json.dumps(pote_cliente, sort_keys=True, ensure_ascii=False,
                                                              separators=(",", ":")).encode("utf-8")),
                     "CONTRATO": pote_cliente.get("SCHEMA"), "OBJETOS_LIBERADOS": pote_cliente["OBJETOS_LIBERADOS"]},
               POTE_EXPERIMENTAL={"ARQUIVO": "POTE-EXPERIMENTAL.json", "SHA256_ARQUIVO": _sha(nova / "POTE-EXPERIMENTAL.json")},
               BLOQUEADOS=len(bloq), VALIDAR_POTE_V2="PASSA",
               # K2 · EIXO 2 no manifesto: onde este pote pode aparecer (nunca producao por esta via, D141)
               AMBIENTE=pote_cliente.get("AMBIENTE", NS), PRODUCAO=pote_cliente.get("PRODUCAO", NS),
               EIXOS=pote_cliente.get("EIXOS", NS),
               LIBERADOS=[oid for oid, c in conf.items() if c["LIBERACAO"] == "LIBERADO_PARA_CLIENTE"])
    w("MANIFESTO.json", man)
    (nova / "SHA256SUMS.txt").write_text("".join("%s *%s\n" % (_sha(nova / n), n) for n in
                                                 ("POTE.json", "POTE-EXPERIMENTAL.json", "BLOQUEADOS.json",
                                                  "MANIFESTO.json")), encoding="utf-8", newline="\n")
    velha = entrega.with_name(entrega.name + ".velha")
    shutil.rmtree(velha, ignore_errors=True)
    if entrega.exists():
        os.replace(entrega, velha)
    os.replace(nova, entrega)
    shutil.rmtree(velha, ignore_errors=True)
    return man


def main(argv=None) -> int:
    import argparse
    a = argparse.ArgumentParser()
    a.add_argument("--copia", required=True)
    a.add_argument("--afirmacoes", required=True)
    a.add_argument("--armazem", required=True)
    a.add_argument("--entrega", required=True)
    a.add_argument("--hoje", default=date.today().isoformat())
    a.add_argument("--produtor", help="raiz do ramo produtor-afirmacoes (dono de leis/tempo_da_afirmacao.como_se_le)")
    x = a.parse_args(argv)
    if x.produtor:
        sys.path.append(str(Path(x.produtor) / "leis"))
    sys.path.insert(0, str(RAIZ / "admissao"))
    import motor_das_capacidades as M                   # noqa: PLC0415
    import gatilho_da_inteligencia as GI                # noqa: PLC0415
    copia = Path(x.copia)
    sala = copia / "SALA_ATUAL.json"
    ro = (copia / "PROVA_RO.txt").read_text(encoding="utf-8").split()
    if ro[0] != "on":
        raise SystemExit("copia sem prova de transacao so-leitura")
    linhas = json.loads(sala.read_text(encoding="utf-8"))
    export = {"EXPORT": M.EXPORT_DA_SALA, "SINTETICO": False, "CORTE": ro[1] + "T" + ro[2],
              "ORIGEM": "copia so-leitura · sha256 %s" % _sha(sala), "READ_ONLY": ro[0], "LINHAS": linhas,
              "POUSOS_DA_COPIA": [{"run_id": l["run_id"], "ordem": l["ordem"], "item_id": l["item_id"],
                                   "pousado_em": l.get("pousado_em")} for l in linhas]}
    limpo, corte = GI.cortar_vigente(export)
    art = json.loads(Path(x.afirmacoes).read_text(encoding="utf-8"))
    s = M.rodar(M.entrada_do_export(limpo), date.fromisoformat(x.hoje), GI._cabeca(), afirmacoes=art)
    del art
    pote, _ = GI.montar_o_pote(s)
    run = pote.get("INTELLIGENCE_RUN_ID", NS)
    por_item = {str(l["item_id"]): l for l in limpo["LINHAS"]}
    todo, conf = liberar(pote, por_item, Path(x.armazem), run)
    # K2 (01/10): os DOIS eixos — o objeto diz uma coisa sobre o cliente (LIBERACAO), a raiz diz o ambiente
    todo = P.aplicar_eixos(todo)
    cliente = so_liberados(todo)
    for nome, p in (("EXPERIMENTAL", todo), ("PARA_CLIENTE", cliente)):
        v = P.conferir_pote(p) + VP.validar(p)
        if v:
            raise SystemExit("pote %s reprovado pelo fiscal: %s" % (nome, v[:5]))
    if cliente["OBJETOS_LIBERADOS"] == 0:
        print(json.dumps({"LIBERADOS": 0, "BLOQUEADOS": len(conf), "ENTREGA": "NAO GERADA (nada liberado)"}))
        return 0
    man = entregar(cliente, todo, conf, Path(x.entrega), {
        "COPIA_DA_SALA": {"SHA256": _sha(sala), "EM": ro[1] + "T" + ro[2], "READ_ONLY": ro[0]},
        "AFIRMACOES": {"FICHEIRO": Path(x.afirmacoes).name, "SHA256": _sha(Path(x.afirmacoes))},
        "CORTE_VIGENTE": {k: corte.get(k, NS) for k in ("LINHAS_NO_EXPORT", "LINHAS_NO_CORTE")}})
    print(json.dumps({k: man[k] for k in ("INTELLIGENCE_RUN_ID", "POTE", "BLOQUEADOS", "LIBERADOS")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
