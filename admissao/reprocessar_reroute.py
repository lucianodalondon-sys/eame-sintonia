#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPROCESSAR A SALA QUE JA EXISTE PELA D56 — cada linha perguntada as outras reguas, sem rede.

REROUTE-D56 (28/09). A porta passou a perguntar o documento pronto a TODAS as reguas
(`admissao.decidir_todas`), e um item com SIM em varios universos e UMA linha com varias gavetas
(`sala_de_espera_gaveta`, 033). As linhas que pousaram ANTES disto so conhecem o universo do pedido.
Este script da a cada uma as gavetas que a porta de hoje lhe daria, e MAIS NADA:

    linha.texto -> admissao.julgar_reroute(universo) para cada universo do Atlas != o da linha
                -> SIM (com trecho, regua medida, gaveta no escopo D130 = T1/T2) = uma gaveta nova

    O RAW NAO MUDA. A LINHA NAO MUDA. NENHUMA LINHA NASCE. SO SE ACRESCENTAM GAVETAS.

    py admissao/reprocessar_reroute.py --exportar copia.json                       # SO LE a Sala
    py admissao/reprocessar_reroute.py --entrada copia.json --saida plano.json     # SECO (omissao)
    py admissao/reprocessar_reroute.py --aplicar plano.json --backup PROVA-BACKUP-SALA.json [--recibo r.json]

SECO (omissao): nao abre banco nenhum. Le a COPIA exportada (`sala_de_espera.linhas_para_revisao()`:
RUN_ID, ORDEM, ITEM_ID, UNIVERSO, SOURCE_ID, SHA256, MEDIA_TYPE, TEXTO) e escreve o PLANO: as gavetas
novas, as decisoes de cada par (linha, universo) para o livro, e a VERSAO (sha256 do codigo).

`--aplicar` so escreve com as TRES travas:
  1 · o backup da Sala com PROVA_VALE = true (`scripts/micro_coleta/provar_backup_da_sala.py`);
  2 · `curadoria/PARAR.flag` presente — o robo parado, ninguem a pousar ao mesmo tempo;
  3 · a VERSAO do plano igual a do codigo de agora (o que se reviu a seco e o que se aplica).
Depois exige a Sala canonica (`sala_de_espera.exigir_canonica`), escreve as decisoes no livro
(`admissao.escrever`, so acrescenta) e as gavetas por `sala_de_espera.acrescentar_gavetas` — so INSERT,
so em linhas que existem com a ORIGEM lida, e a mesma gaveta outra vez nao escreve nada.

O que NAO faz: nao abre rede; nao cria linha; nao apaga nem funde as linhas que ja estavam em dobro antes
da D56 (o mesmo documento em dois universos = duas linhas: ficam, e ficam listadas em
`DUPLICADOS_ANTES_DA_D56`); nao da a uma linha uma gaveta que ja e a linha de outra copia do mesmo
documento; nao refaz a decisao do pedido.
"""
import argparse
import hashlib
import json
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import admissao as adm  # noqa: E402

RAIZ = os.path.dirname(HERE)
PARAR = os.path.join(RAIZ, "curadoria", "PARAR.flag")
CORRIDA = "REPROCESSO-D56"
#: O codigo que produz o resultado. A versao E o sha256 dele (o criterio dos outros reprocessos).
CODIGO_DA_VERSAO = ("admissao/reprocessar_reroute.py", "admissao/admissao.py", "admissao/idioma.py",
                    "leis/fato_do_texto.py", "leis/fato_local.py", "leis/territorios.py")


def versao_do_codigo(raiz=RAIZ) -> str:
    h = hashlib.sha256()
    for f in CODIGO_DA_VERSAO:
        with open(os.path.join(raiz, f), "rb") as fh:
            h.update(f.encode("utf-8") + b"\0" + fh.read() + b"\0")
    return h.hexdigest()


def _linhas(entrada):
    return entrada.get("ITENS", entrada) if isinstance(entrada, dict) else entrada


def planear(linhas: list) -> dict:
    """SECO: as gavetas que a porta de hoje daria a cada linha. Deterministico; nao abre banco."""
    linhas = sorted(_linhas(linhas), key=lambda l: (str(l.get("RUN_ID")), int(l.get("ORDEM", 0))))
    # o mesmo documento (mesmo sha256 do bruto) em varias linhas: anteriores a D56, ficam como estao
    grupos = OrderedDict()
    for l in linhas:
        grupos.setdefault(l.get("SHA256") or "linha:%s#%s" % (l["RUN_ID"], l["ORDEM"]), []).append(l)
    gavetas, decisoes, duplicados = [], [], []
    for chave, g in grupos.items():
        canonica = g[0]
        ja_sao_linha = {l["UNIVERSO"] for l in g}
        if len(g) > 1:
            duplicados.append({"DOCUMENTO": chave, "LINHAS": ["%s#%s:%s" % (l["RUN_ID"], l["ORDEM"],
                                                                             l["UNIVERSO"]) for l in g]})
        item = {"id": canonica["ITEM_ID"], "texto": canonica.get("TEXTO") or "",
                "source_id": canonica.get("SOURCE_ID"), "media_type": canonica.get("MEDIA_TYPE")}
        lingua = adm._lingua_do_item(item)
        for u in adm.universos_da_porta():
            if u in ja_sao_linha:
                continue
            r, motivo, ev = adm.julgar_reroute(item, u, lingua)
            d = adm.Decisao(item=canonica["ITEM_ID"], universo=u, resultado=r,
                            regra=adm.REGRA_DO_REROUTE, motivo=motivo,
                            evidencia=dict(ev, d56={"papel": adm.PAPEL_REROUTE,
                                                    "pedido": canonica["UNIVERSO"],
                                                    "versao_do_reroute": adm.VERSAO_DO_REROUTE,
                                                    "reprocesso_da_linha": "%s#%s" % (
                                                        canonica["RUN_ID"], canonica["ORDEM"])}),
                            corrida=CORRIDA, quando="REPROCESSO")
            decisoes.append({k: v for k, v in d.__dict__.items() if k != "quando"})
            # D130: so as gavetas que o dono liberou (T1/T2) viram gaveta; as outras so anotam
            if r == adm.SIM and adm.REROUTE_ENTRA_NA_SALA and u in adm.REROUTE_NA_SALA_D130:
                trechos = ev.get("trechos") or []
                motivo_g = "%s v%s (reroute v%s) · PEDIDO=%s · %s%s" % (
                    d.regra, d.versao, adm.VERSAO_DO_REROUTE, canonica["UNIVERSO"], motivo,
                    (" · trecho: «%s»" % trechos[0]["trecho"]) if trechos else "")
                gavetas.append({"RUN_ID": canonica["RUN_ID"], "ORDEM": int(canonica["ORDEM"]),
                                "ITEM_ID": canonica["ITEM_ID"], "ORIGEM": canonica["UNIVERSO"],
                                "UNIVERSO": u, "PONTUACAO": adm.pontuacao(d),
                                "MOTIVO": motivo_g[:adm.MOTIVO_MAXIMO_NA_GAVETA]})
    por_u = {}
    for g in gavetas:
        por_u[g["UNIVERSO"]] = por_u.get(g["UNIVERSO"], 0) + 1
    return {"PLANO": "REPROCESSO-D56", "VERSAO_DO_CODIGO": versao_do_codigo(),
            "VERSAO_DA_REGRA": adm.VERSAO_DA_REGRA, "VERSAO_DO_REROUTE": adm.VERSAO_DO_REROUTE,
            "REROUTE_PROMOVE": sorted(adm.REROUTE_PROMOVE, key=adm._ordem_no_atlas),
            "REROUTE_NA_SALA_D130": sorted(adm.REROUTE_NA_SALA_D130, key=adm._ordem_no_atlas),
            "LINHAS_LIDAS": len(linhas), "DOCUMENTOS": len(grupos),
            "GAVETAS_NOVAS": len(gavetas), "GAVETAS_POR_UNIVERSO": por_u,
            "LINHAS_COM_GAVETA_NOVA": len({(g["RUN_ID"], g["ORDEM"]) for g in gavetas}),
            "DUPLICADOS_ANTES_DA_D56": duplicados,
            "GAVETAS": gavetas, "DECISOES": decisoes}


class TravaFechada(Exception):
    """Uma das tres travas do --aplicar nao abriu. Nada foi escrito."""


def conferir_travas(plano: dict, backup: dict, parar: str = PARAR) -> None:
    if not isinstance(backup, dict) or backup.get("PROVA_VALE") is not True:
        raise TravaFechada("o backup da Sala nao tem PROVA_VALE = true (provar_backup_da_sala.py): "
                           "sem backup provado nao se escreve na Sala")
    if not os.path.exists(parar):
        raise TravaFechada("curadoria/PARAR.flag nao existe: o robo pode estar a pousar ao mesmo "
                           "tempo. Pare-o (PARAR.flag) antes de aplicar")
    agora = versao_do_codigo()
    if plano.get("VERSAO_DO_CODIGO") != agora:
        raise TravaFechada("o plano foi feito com outro codigo (%s != %s): refaca o seco"
                           % (str(plano.get("VERSAO_DO_CODIGO"))[:12], agora[:12]))


def aplicar(plano: dict, backup: dict, parar: str = PARAR) -> dict:
    conferir_travas(plano, backup, parar)
    import sala_de_espera as espera  # noqa: PLC0415 — so quem aplica abre a Sala
    estado = espera.exigir_canonica()
    livro = adm.escrever([adm.Decisao(**d) for d in plano["DECISOES"]]) if plano["DECISOES"] else None
    r = espera.acrescentar_gavetas(plano["GAVETAS"])
    return {"APLICADO": True, "BACKEND": estado.get("BACKEND"), "LIVRO_DECISOES_TOTAL": livro,
            "DECISOES_ESCRITAS": len(plano["DECISOES"]), **r}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--exportar")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    ap.add_argument("--aplicar")
    ap.add_argument("--backup")
    ap.add_argument("--recibo")
    a = ap.parse_args(argv)
    if a.exportar:
        import sala_de_espera as espera  # noqa: PLC0415
        linhas = espera.linhas_para_revisao()
        with open(a.exportar, "w", encoding="utf-8") as f:
            json.dump({"ITENS": linhas}, f, ensure_ascii=False, indent=1)
        print("exportadas %d linhas (so leitura) -> %s" % (len(linhas), a.exportar))
        return 0
    if a.aplicar:
        with open(a.aplicar, encoding="utf-8") as f:
            plano = json.load(f)
        backup = {}
        if a.backup:
            with open(a.backup, encoding="utf-8") as f:
                backup = json.load(f)
        try:
            r = aplicar(plano, backup)
        except TravaFechada as e:
            print("NADA FOI ESCRITO: %s" % e)
            return 2
        if a.recibo:
            with open(a.recibo, "w", encoding="utf-8") as f:
                json.dump(r, f, ensure_ascii=False, indent=1)
        print(json.dumps(r, ensure_ascii=False))
        return 0
    if not a.entrada:
        ap.error("SECO precisa de --entrada (a copia exportada)")
    with open(a.entrada, encoding="utf-8") as f:
        plano = planear(json.load(f))
    corpo = json.dumps(plano, ensure_ascii=False, indent=1) + "\n"
    if a.saida:
        with open(a.saida, "w", encoding="utf-8") as f:
            f.write(corpo)
    print(json.dumps({k: plano[k] for k in ("LINHAS_LIDAS", "DOCUMENTOS", "GAVETAS_NOVAS",
                                            "GAVETAS_POR_UNIVERSO", "LINHAS_COM_GAVETA_NOVA")},
                     ensure_ascii=False))
    print("SECO: nada foi escrito na Sala nem no livro.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
