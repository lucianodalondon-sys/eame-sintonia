#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A MAQUINA COM VARIAS CORRIDAS AO MESMO TEMPO.

    BANCO_DESCARTAVEL_URL=... SALA_DESCARTAVEL=/tmp/sala \\
        python3 provas/a_maquina_sob_carga.py [QUANTAS]

A PERGUNTA
----------
    QUANDO VARIAS CORRIDAS CORREM JUNTAS, ALGUMA COISA SE CRUZA,
    SE PERDE, SE DUPLICA OU SE CALA?

Em serie a maquina esta provada (`provas/o_pedido_t4_atravessa.py`). Isto nao
diz nada sobre o que acontece quando duas corridas partilham banco, disco e
fonte — e a operacao real e isso.

    UMA MAQUINA PROVADA EM SERIE E UMA MAQUINA PROVADA EM SERIE.

O QUE ELA NAO FAZ
-----------------
Nao bombardeia a fonte. O executor reaproveita os bytes que esta arvore ja
preservou, e por isso N corridas nao sao N descargas — sao N travessias sobre
o mesmo documento, que e exactamente o pior caso para as corridas de
reaproveitamento e para as chaves unicas.

    O PIOR CASO PARA A CONCORRENCIA NAO E MUITO MATERIAL:
    E O MESMO MATERIAL, AO MESMO TEMPO.
"""
import io
import json
import os
import subprocess
import sys
import threading
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao                                     # noqa: E402
import coleta_checkpoint as cc                      # noqa: E402
import sala_de_espera as espera                     # noqa: E402
from pedido import Pedido                           # noqa: E402

CELEX = "32026R1696"
SAIDA = os.path.join("data", "derivados", "A-MAQUINA-SOB-CARGA.json")
_SO_VERIFICA = ("008",)

fora = []


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    for f in sorted(os.listdir(pasta)):
        if not f.endswith(".sql") or f.split("_", 1)[0] in _SO_VERIFICA:
            continue
        r = subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-q", "-f",
                            os.path.join(pasta, f)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FALHOU a aplicar %s\n%s" % (f, r.stderr[:400]))
            raise SystemExit(1)


def _memoria(url):
    import importlib.util as u
    sp = u.spec_from_file_location(
        "prova_pg", os.path.join(RAIZ, "provas",
                                 "preservar_coleta_no_postgres.py"))
    m = u.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.MemoriaPostgres(url)


def uma_corrida(url, resultados, indice):
    """Uma travessia inteira, do botao a sala. Cada fio tem o SEU banco aberto.

    ⚠️ UMA LIGACAO PARTILHADA MEDIRIA A LIGACAO, e nao a maquina: dois fios a
    escrever no mesmo cursor dao erros que a producao nunca teria.
    """
    import orquestrador as orq
    inicio = time.time()
    try:
        sql = cc.Banco(url)
        recibo = orq.correr(
            Pedido(alvo="T4", filtros={"pais": "IT", "celex": CELEX}),
            memoria=_memoria(url), banco_do_rastro=sql)
        recibo.pop("_plano", None)
        resultados[indice] = {
            "RUN_ID": recibo.get("RUN_ID"),
            "STATUS": recibo.get("STATUS"),
            "COLHEITA": recibo.get("COLHEITA_ENCONTRADA"),
            "ADMISSAO": (recibo.get("ADMISSAO") or {}).get("por_resultado"),
            "PRONTOS": (recibo.get("ADMISSAO") or {}).get("prontos"),
            "ERRO": None,
            # ⚠️ UM BALDE `ERROR` SEM MOTIVO E UM ROTULO. Quando a derivacao
            # perde um item, o porque tem de chegar aqui — senao a medicao
            # diz «dois falharam» e a missao seguinte tem de os reproduzir.
            "DERIVACAO": {
                k: v for k, v in (recibo.get("DERIVACAO") or {}).items()
                if k in ("ESTADO_DA_ETAPA", "BALDES", "ERROS", "DERIVADOS",
                         "PORQUE", "SEM_DERIVADO")},
            "SEGUNDOS": round(time.time() - inicio, 2),
            # O que o executor disse, quando a corrida nao foi SUCCESS.
            "SAIDA": (recibo.get("SAIDA") or "")[-300:]
                     if recibo.get("STATUS") != "SUCCESS" else "",
            "ERRO_EXEC": (recibo.get("ERRO") or "")[-300:],
        }
    except Exception as ex:                                   # noqa: BLE001
        resultados[indice] = {
            "RUN_ID": None, "STATUS": "EXCECAO", "ERRO":
                "%s: %s" % (type(ex).__name__, str(ex)[:200]),
            "SEGUNDOS": round(time.time() - inicio, 2)}


def medir(url, quantas, sala):
    resultados = {}
    fios = [threading.Thread(target=uma_corrida, args=(url, resultados, i))
            for i in range(quantas)]
    t0 = time.time()
    for f in fios:
        f.start()
    for f in fios:
        f.join()
    duracao = round(time.time() - t0, 2)

    sql = cc.Banco(url)
    q = sql.executa
    corridas = [r for r in resultados.values() if r.get("RUN_ID")]
    ids = [r["RUN_ID"] for r in corridas]

    # ── CADA OBSERVACAO PERTENCE A UMA CORRIDA SO ───────────────────────
    por_corrida = q("select run_id, count(*) from public.raw_asset"
                    " group by run_id order by run_id")
    orfas = q("select count(*) from public.raw_asset r"
              " left join public.collection_run c on c.run_id = r.run_id"
              " where c.run_id is null")

    # ── NENHUM DERIVADO LIGA A OBSERVACAO DE OUTRA CORRIDA ──────────────
    # A participacao e (observacao, derivado). Um derivado pode ser
    # partilhado — e e o contrato. O que NAO pode e uma observacao declarar
    # participacao num derivado cujo pai nao tem nada que ver com ela.
    cruzado = q(
        "select count(*) from public.participacao_na_derivacao p"
        " join public.raw_asset r on r.id = p.raw_asset_id"
        " join public.derived_artifact d on d.id = p.derived_artifact_id"
        " where d.parent_sha256 <> r.sha256")

    # ── OS DOCUMENTOS NAO DUPLICAM POR DERIVADO ─────────────────────────
    docs = q("select count(*), count(distinct derived_artifact_id)"
             " from public.documento_estruturado")

    # ── A SALA TEM UM FICHEIRO POR CORRIDA QUE ADMITIU ──────────────────
    na_sala = sorted(f for f in os.listdir(sala) if f.endswith(".json"))
    orfaos_na_sala = [f for f in na_sala
                      if not any(rid in f for rid in ids)]

    baldes = q("select coalesce(sum(passed),0), coalesce(sum(reused),0),"
               " coalesce(sum(rejected),0), coalesce(sum(error_count),0),"
               " coalesce(sum(not_run_count),0)"
               " from public.etapa_da_corrida where etapa = 'DERIVED'")
    passed, reused, rej, err, notrun = [int(x) for x in baldes[0]]

    excecoes = [r for r in resultados.values() if r.get("ERRO")]

    return {
        "REQUESTS": quantas,
        "SUCCESS": len([r for r in corridas if r["STATUS"] == "SUCCESS"]),
        "ERROR": len(excecoes),
        "ERROS": [r["ERRO"] for r in excecoes][:5],
        "DURATION_S": duracao,
        "CORRIDAS_DISTINTAS": len(set(ids)),
        "OBSERVACOES_POR_CORRIDA": {c[0]: int(c[1]) for c in por_corrida},
        "ORPHANS": int(orfas[0][0]),
        "CROSS_RUN_CONTAMINATION": int(cruzado[0][0]),
        "DOCUMENTOS": int(docs[0][0]),
        "DOCUMENTOS_DISTINTOS": int(docs[0][1]),
        "SALA": len(na_sala),
        "SALA_ORFAOS": orfaos_na_sala,
        "BALDES": {"PASSED": passed, "REUSED": reused, "REJECTED": rej,
                   "ERROR": err, "NOT_RUN": notrun},
        "_resultados": resultados,
    }


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL")
    sala = os.environ.get("SALA_DESCARTAVEL")
    if not url or not sala:
        print("FALTA AMBIENTE DESCARTAVEL — e SKIP != PASS.")
        print("CARGA=NOT_MEASURED")
        return 2
    espera.MORADA = sala
    import pathlib
    import tempfile
    admissao.LIVRO = (pathlib.Path(tempfile.mkdtemp(prefix="livro-carga-"))
                      / "LIVRO-DE-DECISOES.json")

    escadas = [int(x) for x in (sys.argv[1:] or ["5", "10", "20"])]
    print("=" * 70)
    print("A MAQUINA SOB CARGA — %s corridas concorrentes"
          % " / ".join(str(x) for x in escadas))
    print("=" * 70)

    medidas = []
    for quantas in escadas:
        # Cada degrau comeca do zero: medir carga sobre o estado da anterior
        # mediria as duas juntas.
        subprocess.run(["psql", url.rsplit("/", 1)[0] + "/postgres",
                        "-q", "-c", "drop database descartavel;",
                        "-c", "create database descartavel;"],
                       capture_output=True, text=True)
        aplicar_migrations(url)
        for f in os.listdir(sala):
            os.unlink(os.path.join(sala, f))

        m = medir(url, quantas, sala)
        medidas.append(m)
        print("\n  %d corridas · %.1fs · SUCCESS=%d ERROR=%d"
              % (quantas, m["DURATION_S"], m["SUCCESS"], m["ERROR"]))
        print("     orfas=%d · cruzamento=%d · sala=%d · baldes=%s"
              % (m["ORPHANS"], m["CROSS_RUN_CONTAMINATION"], m["SALA"],
                 m["BALDES"]))
        if m["ERROS"]:
            for e in m["ERROS"]:
                print("     ERRO: %s" % e[:110])
        for r in m["_resultados"].values():
            if r.get("STATUS") not in ("SUCCESS", None):
                print("     CORRIDA %s -> %s · saida=%s · erro=%s"
                      % (r.get("RUN_ID"), r.get("STATUS"),
                         (r.get("SAIDA") or "")[:150],
                         (r.get("ERRO_EXEC") or "")[:150]))
        for r in m["_resultados"].values():
            d = r.get("DERIVACAO") or {}
            if (d.get("BALDES") or {}).get("ERROR"):
                print("     DERIVACAO FALHOU em %s: %s"
                      % (r.get("RUN_ID"), json.dumps(d, ensure_ascii=False,
                                                     default=str)[:420]))
                break

        n = quantas
        caso("C%d_todas_as_corridas_terminaram_sem_excecao" % n,
             m["ERROR"] == 0, "excecoes: %d · %s" % (m["ERROR"], m["ERROS"]))
        caso("C%d_cada_corrida_tem_a_SUA_identidade" % n,
             m["CORRIDAS_DISTINTAS"] == m["SUCCESS"],
             "corridas distintas=%d · sucessos=%d"
             % (m["CORRIDAS_DISTINTAS"], m["SUCCESS"]))
        caso("C%d_nenhuma_observacao_ficou_ORFA" % n, m["ORPHANS"] == 0,
             "observacoes sem corrida: %d" % m["ORPHANS"])
        caso("C%d_nenhum_derivado_ligou_a_observacao_de_OUTRO_pai" % n,
             m["CROSS_RUN_CONTAMINATION"] == 0,
             "participacoes com pai errado: %d"
             % m["CROSS_RUN_CONTAMINATION"])
        caso("C%d_o_documento_NAO_duplicou_por_derivado" % n,
             m["DOCUMENTOS"] == m["DOCUMENTOS_DISTINTOS"],
             "documentos=%d · distintos=%d"
             % (m["DOCUMENTOS"], m["DOCUMENTOS_DISTINTOS"]))
        caso("C%d_a_sala_nao_recebeu_ficheiro_de_corrida_nenhuma_alheia" % n,
             not m["SALA_ORFAOS"], "orfaos na sala: %s" % m["SALA_ORFAOS"])
        # ⚠️ REUSED != NOT_RUN, E COM N CORRIDAS SOBRE O MESMO DOCUMENTO
        # a maior parte TEM de ser reaproveitamento. Zero reuse com N>1 seria
        # a regua de unicidade a nao morder; tudo reuse seria ninguem a
        # derivar de facto.
        caso("C%d_o_reaproveitamento_aconteceu_e_esta_nos_baldes_certos" % n,
             m["BALDES"]["PASSED"] >= 1
             and m["BALDES"]["REUSED"] == n - m["BALDES"]["PASSED"]
             and m["BALDES"]["ERROR"] == 0
             and m["BALDES"]["NOT_RUN"] == 0,
             "passed=%d reused=%d de %d corridas"
             % (m["BALDES"]["PASSED"], m["BALDES"]["REUSED"], n))

    print()
    for nome, ok, detalhe in fora:
        print("  %-5s %-58s %s" % ("PASS" if ok else "FALHA", nome,
                                   str(detalhe)[:62]))
    inteiro = all(ok for _n, ok, _d in fora)
    print("=" * 70)
    print("CARGA_CONCORRENTE=%s" % ("PASS" if inteiro else "FAIL"))

    caminho = os.path.join(RAIZ, SAIDA)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    limpas = [{k: v for k, v in m.items() if not k.startswith("_")}
              for m in medidas]
    with io.open(caminho, "w", encoding="utf-8") as fh:
        json.dump({"ESCADAS": escadas, "MEDIDAS": limpas,
                   "VEREDICTO": "PASS" if inteiro else "FAIL",
                   "GENERATED_BY": "provas/a_maquina_sob_carga.py"},
                  fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("escrito: %s" % SAIDA)
    return 0 if inteiro else 1


if __name__ == "__main__":
    raise SystemExit(main())
