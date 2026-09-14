#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E SE A CORRIDA MORRER A MEIO?

    BANCO_DESCARTAVEL_URL=... SALA_DESCARTAVEL=/tmp/sala \\
        python3 provas/a_maquina_depois_do_crash.py

A PERGUNTA
----------
    DEPOIS DE UMA CORRIDA MORRER NUMA FRONTEIRA,
    A MAQUINA SABE O QUE JA TINHA ACONTECIDO?

Nao se pergunta «recupera sozinha» — recuperacao automatica e outra decisao, e
nao foi tomada. Pergunta-se se o estado que ficou e LEGIVEL: se a corrida
seguinte consegue distinguir «isto ja foi feito» de «isto nunca correu», e se
nada do que ficou para tras se faz passar por trabalho desta.

    UM ESTADO PRESO E AUDITAVEL E MELHOR
    DO QUE UMA LIMPEZA AUTOMATICA QUE NAO SABE SE O OUTRO LADO AINDA CORRE.

AS TRES FRONTEIRAS, E POR QUE SAO ESTAS
----------------------------------------
    A · depois do ENVELOPE, antes do INGRESSO
        o executor foi a fonte e declarou; ninguem leu. Ficou um envelope.

    B · depois do RAW, antes do DERIVED
        os bytes estao preservados e a corrida parou. Ficou material sem
        derivado.

    C · depois de ADMISSION = SIM, antes da SALA DE ESPERA
        a porta decidiu e a unidade nao pousou. Ficou uma decisao sem destino.

Sao as tres onde ha ESCRITA DURAVEL de um lado e nao do outro. Onde nao ha
persistencia nao se simula crash: nao havia o que sobreviver.
"""
import io
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao                                     # noqa: E402
import coleta_checkpoint as cc                      # noqa: E402
import retorno_da_coleta as rdc                     # noqa: E402
import sala_de_espera as espera                     # noqa: E402
from pedido import Pedido                           # noqa: E402
from receitas import EXECUTORES                     # noqa: E402

CELEX = "32026R1696"
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


def _pedido():
    return Pedido(alvo="T4", filtros={"pais": "IT", "celex": CELEX})


# ══════════════════════════════════════════════════════════════════════════
# A · MORREU DEPOIS DO ENVELOPE, ANTES DO INGRESSO
# ══════════════════════════════════════════════════════════════════════════
def fronteira_a(url, sql):
    """Fica um envelope de uma corrida que nunca chegou ao banco.

    ⚠️ ESTE E O CENARIO QUE `G-ENV-01` TORNAVA PERIGOSO. Com um endereco por
    executor, o envelope orfao ficava no caminho que a proxima corrida ia ler
    — e ela consumia trabalho que nao era dela, sem nota nenhuma.
    """
    import orquestrador as orq
    e = (EXECUTORES.get("T4") or [{}])[0]
    padrao = (e.get("retorno") or {}).get("ENVELOPE")

    # a corrida que "morreu": o executor correu e declarou; ninguem leu.
    morta = "IT-T4-CORRIDA-QUE-MORREU"
    r = subprocess.run(
        [sys.executable, "coleta/eu_regulatorio_executor.py", CELEX,
         "--run-id=%s" % morta],
        cwd=RAIZ, capture_output=True, text=True, timeout=600)
    onde = os.path.join(RAIZ, rdc.endereco_do_envelope(padrao, morta))
    caso("A1_o_envelope_da_corrida_morta_ficou_em_disco",
         os.path.isfile(onde),
         "%s · saida=%s" % (os.path.basename(onde), r.stdout.strip()[:60]))
    caso("A2_e_a_corrida_morta_NAO_existe_no_banco",
         not sql.executa("select run_id from public.collection_run"
                         " where run_id = '%s'" % morta),
         "collection_run para a corrida morta: nenhuma")

    # agora a corrida seguinte, viva e inteira
    recibo = orq.correr(_pedido(), memoria=_memoria(url), banco_do_rastro=sql)
    recibo.pop("_plano", None)
    viva = recibo.get("RUN_ID")
    caso("A3_a_corrida_SEGUINTE_nao_consumiu_o_envelope_orfao",
         viva != morta and recibo.get("STATUS") == "SUCCESS",
         "corrida viva=%s · status=%s" % (viva, recibo.get("STATUS")))

    # ⚠️ E O ORFAO CONTINUA LA, E ISSO E O CERTO.
    # Apaga-lo seria a maquina a limpar prova de que uma corrida morreu.
    caso("A4_o_orfao_continua_legivel_e_nomeia_a_corrida_dele",
         os.path.isfile(onde)
         and json.load(io.open(onde, encoding="utf-8")).get("RUN_ID") == morta,
         "o envelope orfao continua a dizer de quem e")
    os.unlink(onde)


# ══════════════════════════════════════════════════════════════════════════
# B · MORREU DEPOIS DO RAW, ANTES DO DERIVED
# ══════════════════════════════════════════════════════════════════════════
def fronteira_b(url, sql):
    """A corrida preserva o bruto e morre antes de derivar.

    Simula-se rebentando a derivacao — e nao apagando linhas a mao: uma
    bancada que fabrica o estado mede a bancada.
    """
    import orquestrador as orq
    import derivacao_forward as deriv

    real = deriv.correr

    def morre(*_a, **_k):
        raise RuntimeError("CRASH SIMULADO depois do RAW, antes do DERIVED")

    antes = {r[0] for r in sql.executa("select run_id from public.raw_asset")}
    deriv.correr = morre
    rebentou = False
    try:
        try:
            recibo = orq.correr(_pedido(), memoria=_memoria(url),
                                banco_do_rastro=sql)
            recibo.pop("_plano", None)
        except RuntimeError:
            rebentou = True
    finally:
        deriv.correr = real

    # ⚠️ QUANDO O CRASH SOBE, NAO HA RECIBO — E O RECIBO NAO E A VERDADE.
    # A primeira versao desta prova, sem recibo, dava-se por satisfeita com
    # «a excecao subiu». Isso mede o chamador, e a pergunta e sobre o ESTADO:
    # o que e que ficou escrito, e da para o ler?
    #
    #     UM CASO QUE PASSA PORQUE NAO CONSEGUIU MEDIR
    #     E UM CASO QUE NAO MEDIU.
    #
    # A corrida morta encontra-se onde ela deixou marca: no banco.
    depois = {r[0] for r in sql.executa("select run_id from public.raw_asset")}
    novas = sorted(depois - antes)
    morta = novas[0] if novas else None
    caso("B0_o_crash_nao_foi_engolido", rebentou,
         "a excecao subiu ao chamador: a corrida nao fingiu sucesso")

    brutos = sql.executa(
        "select count(*) from public.raw_asset where run_id = '%s'" % morta) \
        if morta else [[0]]
    derivados = sql.executa(
        "select count(*) from public.derived_artifact d"
        " join public.participacao_na_derivacao p"
        "   on p.derived_artifact_id = d.id"
        " join public.raw_asset r on r.id = p.raw_asset_id"
        " where r.run_id = '%s'" % morta) if morta else [[0]]
    estado = sql.executa(
        "select status from public.collection_run where run_id = '%s'"
        % morta) if morta else []
    caso("B1_o_RAW_da_corrida_morta_SOBREVIVEU",
         bool(morta) and int(brutos[0][0]) > 0,
         "corrida morta=%s · observacoes preservadas: %s"
         % (morta, brutos[0][0]))
    # ⚠️ E A PERGUNTA QUE IMPORTA: DA PARA SABER QUE ELA PAROU AI?
    # Um RAW sem derivado e um estado legivel — «chegou ate aqui». O que
    # seria mau era nao haver maneira de o distinguir de uma corrida que
    # derivou e nao produziu nada.
    caso("B2_e_da_para_VER_que_ela_parou_antes_de_derivar",
         bool(morta) and int(derivados[0][0]) == 0,
         "derivados da corrida morta: %s · status da corrida=%s"
         % (derivados[0][0], estado[0][0] if estado else "sem linha"))

    # a corrida SEGUINTE corre inteira, e nao herda o estado da morta
    recibo2 = orq.correr(_pedido(), memoria=_memoria(url), banco_do_rastro=sql)
    recibo2.pop("_plano", None)
    viva = recibo2.get("RUN_ID")
    seus = sql.executa(
        "select count(*) from public.raw_asset where run_id = '%s'" % viva)
    caso("B3_a_corrida_seguinte_corre_inteira_e_so_com_o_que_e_dela",
         recibo2.get("STATUS") == "SUCCESS" and int(seus[0][0]) > 0
         and viva != morta,
         "corrida viva=%s · observacoes dela=%s" % (viva, seus[0][0]))


# ══════════════════════════════════════════════════════════════════════════
# C · MORREU DEPOIS DE ADMISSION = SIM, ANTES DA SALA
# ══════════════════════════════════════════════════════════════════════════
def fronteira_c(url, sql, sala):
    """A porta decide SIM e a unidade nao chega a pousar."""
    import orquestrador as orq

    real = espera.pousar

    def morre(*_a, **_k):
        raise RuntimeError("CRASH SIMULADO depois do SIM, antes da SALA")

    antes = sorted(f for f in os.listdir(sala) if f.endswith(".json"))
    antes_raw = {r[0] for r in sql.executa(
        "select run_id from public.raw_asset")}
    espera.pousar = morre
    rebentou = False
    try:
        try:
            recibo = orq.correr(_pedido(), memoria=_memoria(url),
                                banco_do_rastro=sql)
            recibo.pop("_plano", None)
        except RuntimeError:
            rebentou = True
    finally:
        espera.pousar = real
    # Mesma razao do B: sem recibo, a corrida encontra-se pela marca que
    # deixou, e nao pelo valor que nunca voltou.
    depois_raw = {r[0] for r in sql.executa(
        "select run_id from public.raw_asset")}
    novas = sorted(depois_raw - antes_raw)
    morta = novas[0] if novas else None
    caso("C0_o_crash_nao_foi_engolido", rebentou,
         "a excecao subiu: a corrida nao disse que pousou")

    depois = sorted(f for f in os.listdir(sala) if f.endswith(".json"))
    caso("C1_a_SALA_nao_recebeu_nada_da_corrida_que_morreu",
         depois == antes, "sala antes=%d · depois=%d" % (len(antes),
                                                         len(depois)))
    # ⚠️ A DECISAO FICOU ESCRITA, E A UNIDADE NAO POUSOU.
    # Isto e um estado legivel e NAO e uma perda silenciosa: o livro diz que
    # a porta decidiu, e a sala diz que nada chegou. As duas coisas a serem
    # verdade ao mesmo tempo e o que permite reconciliar depois.
    livro = json.load(io.open(str(admissao.LIVRO), encoding="utf-8")) \
        if os.path.isfile(str(admissao.LIVRO)) else {"DECISOES": []}
    dela = [d for d in livro.get("DECISOES") or []
            if d.get("corrida") == morta]
    caso("C2_mas_a_DECISAO_ficou_escrita_no_livro",
         bool(morta) and bool(dela),
         "corrida morta=%s · decisoes dela no livro: %d" % (morta, len(dela)))

    # e a corrida seguinte pousa, sem duplicar a anterior
    recibo2 = orq.correr(_pedido(), memoria=_memoria(url), banco_do_rastro=sql)
    recibo2.pop("_plano", None)
    viva = recibo2.get("RUN_ID")
    final = sorted(f for f in os.listdir(sala) if f.endswith(".json"))
    caso("C3_a_corrida_seguinte_POUSA_e_com_o_nome_dela",
         len(final) == len(antes) + 1 and any(viva in f for f in final),
         "sala final=%s" % final[-2:])
    caso("C4_e_a_sala_NAO_ganhou_ficheiro_da_corrida_morta",
         not any(morta and morta in f for f in final),
         "nenhum ficheiro da corrida morta")


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL")
    sala = os.environ.get("SALA_DESCARTAVEL")
    if not url or not sala:
        print("FALTA AMBIENTE DESCARTAVEL — e SKIP != PASS.")
        print("CRASH=NOT_MEASURED")
        return 2
    espera.MORADA = sala
    import pathlib
    import tempfile
    admissao.LIVRO = (pathlib.Path(tempfile.mkdtemp(prefix="livro-crash-"))
                      / "LIVRO-DE-DECISOES.json")

    print("=" * 70)
    print("A MAQUINA DEPOIS DO CRASH — tres fronteiras")
    print("=" * 70)
    aplicar_migrations(url)
    sql = cc.Banco(url)

    fronteira_a(url, sql)
    fronteira_b(url, sql)
    fronteira_c(url, sql, sala)

    print()
    for nome, ok, detalhe in fora:
        print("  %-5s %-56s %s" % ("PASS" if ok else "FALHA", nome,
                                   str(detalhe)[:64]))
    inteiro = all(ok for _n, ok, _d in fora)
    print("=" * 70)
    print("CRASH_RETRY=%s" % ("PASS" if inteiro else "FAIL"))
    return 0 if inteiro else 1


if __name__ == "__main__":
    raise SystemExit(main())
