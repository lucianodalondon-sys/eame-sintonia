#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PRIMEIRA COLETA CONTROLADA DA ITÁLIA — aquisição real, fonte a fonte,
até onde cada uma chega DE VERDADE.

    BANCO_DESCARTAVEL_URL=postgresql://...@localhost:54329/descartavel \\
        python3 provas/primeira_coleta_controlada_italia.py IT-T3-002 [SID...]

O QUE ISTO É
------------
O corredor da execução que as duas provas anteriores não faziam juntas:

    provas/a_fonte_t4_italiana_atravessa.py    adquire da rede, pára em DERIVED
    provas/o_material_italiano_chega_a_sala.py chega à Sala, mas REPROCESSA

    AQUISIÇÃO REAL + CHEGADA À SALA, NA MESMA CORRIDA — é isto que se mede.

Cada fonte entra pela PORTA CANÓNICA: um Pedido com `pais` e `fonte`, o
orquestrador cunha a RUN, escolhe o executor pelo consumo de filtros (BG-05),
o coletor exige a fonte nomeada (BG-06), e a estrada corre até onde a verdade
dela chega. NADA aqui chama coletor, ingresso, derivação ou Sala diretamente.

    EXPECTATIVA NÃO É RESULTADO. O PASS desta prova é a máquina dizer a
    VERDADE sobre onde cada fonte chegou — não é «as seis chegam à Sala».

O QUE ISTO NÃO FAZ
------------------
Não decide o veredito do piloto (isso é leitura humana da tabela), não toca
produção (a trava do descartável recusa qualquer URL que não seja local com
nome da lista curta), e não escreve no livro versionado: o OPS_ROOT é um
tempdir criado aqui e destruído pelo chamador.
"""
import importlib.util as _u
import io
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401

URL = os.environ.get("BANCO_DESCARTAVEL_URL") or ""

_sp = _u.spec_from_file_location(
    "prova_pg", os.path.join(RAIZ, "provas", "preservar_coleta_no_postgres.py"))
_pg = _u.module_from_spec(_sp)
_sp.loader.exec_module(_pg)

if not _pg._e_descartavel(URL):
    raise SystemExit(
        "RECUSADO: BANCO_DESCARTAVEL_URL ausente ou nao-descartavel. "
        "PRODUCAO NAO E LABORATORIO.")

# A Sala canónica É este banco — declarada ANTES de qualquer import que a use.
os.environ["SINTONIA_SALA_BACKEND"] = "POSTGRES"
os.environ["SINTONIA_SALA_DSN"] = URL

# O OPS_ROOT é descartável: a certificação de 15/09 mediu o que acontece sem
# isto — o livro versionado foi de 175 para 182 e cinco guardas de outras
# missões reprovaram. O módulo lê o ambiente NO IMPORT, por isso as duas
# atribuições: o ambiente para os filhos, o atributo para este processo.
OPS = tempfile.mkdtemp(prefix="primeira-coleta-it-")
os.environ["ITALY_OPS_ROOT"] = OPS

import coleta_checkpoint as cc                     # noqa: E402
import italy_executor as ie                        # noqa: E402
import sala_de_espera as espera                    # noqa: E402
from pedido import Pedido                          # noqa: E402
import orquestrador as orq                         # noqa: E402

ie.OPS_ROOT = OPS


def _psql(sql):
    r = subprocess.run(["psql", "-X", "-q", "-A", "-t", "-F", "\x1f",
                        "-v", "ON_ERROR_STOP=1", "-f", "-", URL],
                       input=sql, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:400])
    return [l.split("\x1f") for l in r.stdout.strip().splitlines() if l]


def _um(sql):
    r = _psql(sql)
    return r[0][0] if r else ""


def _alvo_de(sid):
    """O alvo do PEDIDO é o território que o próprio SOURCE_ID declara."""
    return sid.split("-")[1]


def _ledger_da_corrida(run_id):
    caminho = os.path.join(OPS, "data", "collection-ledger", "italy",
                           "observations.ndjson")
    if not os.path.exists(caminho):
        return []
    todas = [json.loads(l) for l in io.open(caminho, encoding="utf-8")
             if l.strip()]
    return [o for o in todas if o.get("RUN_ID") == run_id]


def _egresso_da_corrida():
    caminho = os.path.join(OPS, "data", "collection-ledger", "italy",
                           "runs.ndjson")
    if not os.path.exists(caminho):
        return "NAO SEI"
    linhas = [json.loads(l) for l in io.open(caminho, encoding="utf-8")
              if l.strip()]
    return linhas[-1].get("VPN_COUNTRY", "NAO SEI") if linhas else "NAO SEI"


def _sala_noutro_processo(run_id):
    """PERGUNTAR À TABELA NÃO É PERGUNTAR AO DONO — e o dono responde de
    OUTRO processo, com o mesmo ambiente."""
    codigo = ("import sys; sys.path.insert(0, %r)\n"
              "import _gavetas, sala_de_espera as espera\n"
              "v = espera.ler(%r)\n"
              "print(0 if v is None else len(v['ITENS']))\n") % (RAIZ, run_id)
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       env=os.environ.copy(), cwd=RAIZ)
    saida = (r.stdout or "").strip().splitlines()
    return int(saida[-1]) if saida and saida[-1].isdigit() else -1


def correr_uma(sid):
    alvo = _alvo_de(sid)
    p = Pedido(alvo=alvo, filtros={"pais": "IT", "fonte": sid})
    recibo = orq.correr(p, memoria=_pg.MemoriaPostgres(URL),
                        banco_do_rastro=cc.Banco(URL))
    recibo.pop("_plano", None)
    run = recibo["RUN_ID"]
    # As contagens seguem as CHAVES reais: storage e derived não têm
    # run_id — chegam-se pela raw_asset da corrida; o estruturado tem.
    def q(sql):
        return int(_um(sql % run) or 0)
    obs = _ledger_da_corrida(run)
    etapas = {l[0]: l[1] for l in _psql(
        "select etapa, estado from public.etapa_da_corrida "
        "where run_id = '%s' order by id" % run)}
    # A admissão responde pelo RECIBO do orquestrador — o dono da resposta.
    # Perguntar à tabela com colunas adivinhadas já rebentou uma corrida.
    admissao = dict((recibo.get("ADMISSAO") or {}).get("por_resultado") or {})
    raw = q("select count(*) from public.raw_asset where run_id='%s'")
    sala = q("select count(*) from public.sala_de_espera where run_id='%s'")
    linha = {
        "SOURCE_ID": sid,
        "ALVO_DO_PEDIDO": alvo,
        "RUN_ID": run,
        "EXECUTOR": recibo.get("ACTOR", "NAO SEI"),
        "STATUS_DA_CORRIDA": recibo.get("STATUS", "NAO SEI"),
        "NETWORK_REQUEST_OBSERVED": bool(obs),
        "EGRESS_DA_CORRIDA": _egresso_da_corrida(),
        "OBSERVATIONS": len(obs),
        "OBSERVATION_RESULTS": sorted({o.get("OBSERVATION_RESULT", "?")
                                       for o in obs}),
        "HTTP_SAUDE": sorted({o.get("HEALTH_STATE", "?") for o in obs}),
        "RAW": raw,
        "STORAGE": q("select count(distinct r.storage_object_id) "
                     "from public.raw_asset r where r.run_id='%s' "
                     "and r.storage_object_id is not null"),
        "MEDIA_TYPES": [l[0] for l in _psql(
            "select distinct media_type from public.raw_asset "
            "where run_id = '%s'" % run)],
        "SHA256": [l[0][:16] for l in _psql(
            "select sha256 from public.raw_asset where run_id='%s' "
            "order by id limit 4" % run)],
        "DOCUMENT_IDS": sorted({o.get("DOCUMENT_ID") for o in obs
                                if o.get("DOCUMENT_ID")}),
        "DERIVED": q("select count(*) from public.derived_artifact d "
                     "join public.raw_asset r on r.id = d.raw_asset_id "
                     "where r.run_id='%s'"),
        "STRUCTURED": q("select count(*) from public.documento_estruturado "
                        "where run_id='%s'"),
        "ETAPAS": etapas,
        "ADMISSION": admissao or dict(
            (recibo.get("ADMISSAO") or {}).get("por_resultado") or {}),
        "SALA_ROWS": sala,
        "SALA_READ_OTHER_PROCESS": _sala_noutro_processo(run) if sala else 0,
        "COST_USD": recibo.get("COST_USD", "NAO SEI"),
        "ITEM_COUNT": recibo.get("ITEM_COUNT_RAW", "NAO SEI"),
        "ERROR": (recibo.get("ERROR") or "")[:300],
    }
    linha["ADMISSION"] = admissao or "NAO CORREU"
    return linha


def main():
    fontes = sys.argv[1:]
    if not fontes:
        raise SystemExit("uso: primeira_coleta_controlada_italia.py SID [SID...]")
    print("OPS_ROOT (descartavel): %s" % OPS)
    print("BANCO: %s" % URL.rsplit("@", 1)[-1])
    resultados = []
    for sid in fontes:
        print("\n===== %s =====" % sid)
        try:
            linha = correr_uma(sid)
        except Exception as ex:                        # noqa: BLE001
            linha = {"SOURCE_ID": sid, "ERROR": "%s: %s" % (type(ex).__name__, ex)}
        resultados.append(linha)
        print(json.dumps(linha, ensure_ascii=False, indent=1))
    saida = os.path.join(OPS, "RESULTADO.json")
    io.open(saida, "w", encoding="utf-8").write(
        json.dumps(resultados, ensure_ascii=False, indent=1))
    print("\nresultado integral: %s" % saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
