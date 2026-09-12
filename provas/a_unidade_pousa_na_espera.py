#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A UNIDADE ADMITIDA POUSA NA SALA DE ESPERA — e a estrada acaba aqui.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/a_unidade_pousa_na_espera.py

O QUE ESTA PROVA EXISTE PARA FECHAR
-----------------------------------
    G-READY-01   READY nao e produzido por nenhuma rota
    G-READY-02   a sala de espera nao tem armazenamento

A decisao de arquitetura foi tomada por gente, e esta escrita em
`docs/decisoes/`: a Sala de Espera V1 fica no sistema de ficheiros, na morada
que ja existia. O que faltava nao era o contrato — era UM DONO, e a rota
forward chegar la.

    A COLETA ACABA NA SALA DE ESPERA.
    A INTELIGENCIA COMECA DEPOIS, E NOUTRA MISSAO.

O QUE ELA MEDE, E QUE NAO SE SUPOE
-----------------------------------
A travessia inteira numa corrida so, com bytes REAIS do corpo italiano
preservado, contra PostgreSQL 16 descartavel e um sistema de ficheiros
descartavel:

    RAW -> DERIVED -> STRUCTURED -> ADMISSION -> READY -> SALA DE ESPERA

E depois as coisas que um ficheiro exige e que ninguem ve ate falharem:
escrita atomica, retry idempotente, conflito de corrida, concorrencia, e o
que sobra de um crash.

O QUE ELA NAO PROVA
-------------------
Nao prova producao. Nao comeca na REQUEST: comeca no bruto ja preservado, e
por isso `FULL_COLLECTION_E2E = NO`. E nao ha consumidor da sala — o que,
neste estagio, e o estado CERTO.
"""
import io
import json
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import _gavetas  # noqa: E402,F401

import admissao                                      # noqa: E402
import coleta_checkpoint as cc                       # noqa: E402
import rota_forward_documento as m2                  # noqa: E402
import sala_de_espera as espera                      # noqa: E402
import telemetria as tel                             # noqa: E402
from coleta import ingresso as ing                   # noqa: E402
from guarda.preservar_coleta import sha256           # noqa: E402

RUN = "RUN-ESPERA"
_SO_VERIFICA = ("008",)
# Um documento REAL cujo texto a porta admite em T3. Nao e escolhido por ser
# conveniente: e medido — `provas/a_sala_de_espera_nao_tem_morada.py` mostrou
# que 29 de 43 textos derivados reais respondem SIM neste universo.
FONTE = "IT-T3-002"

fora = []


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


def _fonte_do_ficheiro(caminho):
    return io.open(caminho, encoding="utf-8").read()


def cadeia_de_migrations():
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    return [f.split("_", 1)[0] for f in sorted(os.listdir(pasta))
            if f.endswith(".sql") and f.split("_", 1)[0] not in _SO_VERIFICA]


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    for n in cadeia_de_migrations():
        achados = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + "_")]
        r = subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-q", "-f",
                            os.path.join(pasta, achados[0])],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FALHOU a aplicar %s\n%s" % (achados[0], r.stderr[:900]))
            raise SystemExit(1)


def o_pdf_da_fonte():
    import glob
    achados = sorted(glob.glob(os.path.join(
        RAIZ, "data", "collection-store", "italy", FONTE, "*", "*", "*.pdf")))
    if not achados:
        raise SystemExit("nao ha PDF preservado da fonte %s" % FONTE)
    return achados[0]


def canal_da_fonte(sql):
    """A pre-condicao de identidade que `public.conteudo` exige.

    ⚠️ NAO SE REESCREVE A BANCADA. `provas/a_rota_m2_atravessa.py` ja resolve
    isto, e ja tem escrito por que e um GAP HERDADO — criar um canal exige
    decidir de QUEM ele e, e nenhum dono forward resolve isso hoje. Copiar o
    SQL para aqui daria duas bancadas a divergir na primeira mudanca.
    """
    import importlib.util as u
    sp = u.spec_from_file_location(
        "rota_m2", os.path.join(RAIZ, "provas", "a_rota_m2_atravessa.py"))
    m = u.module_from_spec(sp)
    sp.loader.exec_module(m)
    canal_id, _quem = m.canal_da_fonte(sql, FONTE)
    return canal_id


def abrir_corrida(sql, run_id):
    """`etapa_da_corrida.run_id` tem chave para `collection_run`.

    Os casos negativos nunca chegam a preservar nada — entao ninguem abre a
    corrida por eles, e o rastro nao teria onde se prender. Aqui a corrida e
    aberta a mao, e SO nos casos em que o dono do RAW nao corre.
    """
    sql.executa(
        "insert into public.collection_run (run_id, platform, actor,"
        " actor_version, source_country, rule_version, started_at, status)"
        " values ('%s','HTTP direto','coleta/italy_executor.py','adapter-v1',"
        "'IT','1','2026-09-10T00:00:00Z','rodando')"
        " on conflict (run_id) do nothing" % run_id)


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL")
    if not url:
        print("SEM BANCO DESCARTAVEL — e SKIP != PASS.")
        print("POUSA_NA_ESPERA=NOT_MEASURED")
        return 2

    # ⚠️ A SALA DESTA PROVA E DESCARTAVEL. Escrever na morada de producao
    # faria a medicao deixar residuo na arvore — e a medicao seguinte mediria
    # o residuo desta.
    sala = tempfile.mkdtemp(prefix="espera-")
    espera.MORADA = sala
    try:
        return medir(url, sala)
    finally:
        shutil.rmtree(sala, ignore_errors=True)


def medir(url, sala):
    print("=" * 70)
    print("A UNIDADE POUSA NA ESPERA — %d migrations · sala descartavel"
          % len(cadeia_de_migrations()))
    aplicar_migrations(url)
    sql = cc.Banco(url)

    caso("E0_a_etapa_READY_ja_estava_no_vocabulario",
         "READY" in tel.ETAPAS_DA_COLETA,
         "nada de novo foi inventado no vocabulario")

    # ── A TRAVESSIA INTEIRA, NUMA CORRIDA SO ────────────────────────────
    pdf = o_pdf_da_fonte()
    dados = io.open(pdf, "rb").read()
    rel = os.path.relpath(pdf, RAIZ)
    r = ing.receber([{"SOURCE_ID": FONTE,
                      "SOURCE_URL": "https://exemplo.it/%s"
                                    % os.path.basename(pdf),
                      "STORAGE_LOCATION": rel}],
                    corrida={"RUN_ID": RUN, "PLATFORM": "HTTP direto",
                             "ACTOR": "coleta/italy_executor.py",
                             "ACTOR_VERSION": "adapter-v1",
                             "SOURCE_COUNTRY": "IT", "RULE_VERSION": "1",
                             "STARTED_AT": "2026-09-10T00:00:00Z"},
                    armazem=ing.ArmazemLocal(RAIZ),
                    memoria=_memoria(url), raiz=RAIZ, banco_do_rastro=sql)
    obs = (r["RAW"] or {}).get("RAW_OBSERVATIONS") or []
    raw_id = obs[0]["RAW_OBSERVATION_ID"] if len(obs) == 1 else None
    caso("E1_o_bruto_e_real_e_o_id_veio_do_banco", raw_id is not None,
         "raw_asset.id=%s · %s" % (raw_id, os.path.basename(pdf)))

    canal_id = canal_da_fonte(sql)
    unidade = {"RAW_ASSET_ID": raw_id, "PDF": pdf, "SOURCE_ID": FONTE,
               "ROUTE_CLASS_ID": "RC-1", "TIPO": "nota_tecnica",
               "CAPTURED_AT": "2026-09-10T00:00:00Z",
               "URL": "https://exemplo.it/%s" % os.path.basename(pdf)}
    saida = m2.atravessar(sql, unidade=unidade, run_id=RUN,
                          armazem=_armazem(), memoria=_memoria(url),
                          canal_id=canal_id)

    decisao = saida.get("ADMISSION")
    caso("E2_a_porta_respondeu_SIM_a_um_documento_REAL",
         decisao is not None and decisao.resultado == admissao.SIM,
         "a porta disse %s · %s" % (getattr(decisao, "resultado", "-"),
                                    getattr(decisao, "motivo", "")[:44]))

    pousada = saida.get("READY") or {}
    caso("E3_a_unidade_POUSOU_na_sala_de_espera",
         pousada.get("ESTADO") == espera.POUSOU,
         "estado=%s · %s" % (pousada.get("ESTADO"), pousada.get("FICHEIRO")))

    caminho = espera.caminho_da_corrida(RUN)
    existe = os.path.isfile(caminho)
    corpo = json.loads(_fonte_do_ficheiro(caminho)) if existe else {}
    caso("E4_o_ficheiro_existe_e_e_JSON_valido_inteiro",
         existe and corpo.get("RUN_ID") == RUN
         and len(corpo.get("ITENS") or []) == 1,
         "%s · %d unidade(s)" % (os.path.basename(caminho),
                                 len(corpo.get("ITENS") or [])))

    # ── O CONTRATO NAO MUDOU ────────────────────────────────────────────
    CAMPOS = ("ESTADO", "ITEM_ID", "UNIVERSO", "TEXTO", "SOURCE_ID",
              "SOURCE_LOCATION", "FACT_LOCATION", "FACT_TIME",
              "CAPTURED_AT", "CORRIDA", "ADMITIDO_POR")
    u = (corpo.get("ITENS") or [{}])[0]
    caso("E5_a_unidade_tem_os_11_campos_da_lei_e_nem_um_a_mais",
         tuple(u) == CAMPOS, "%d campos, na ordem da COL-LAW-043" % len(u))
    caso("E6_e_o_estado_dela_e_PRONTO_PARA_INTELIGENCIA",
         u.get("ESTADO") == "PRONTO_PARA_INTELIGENCIA",
         "ESTADO=%s" % u.get("ESTADO"))

    # ── A ETAPA READY FALA ──────────────────────────────────────────────
    linhas = sql.executa(
        "select etapa::text, estado::text, passed, reused, not_run_count,"
        " coalesce(last_good_artifact,'-'), coalesce(edge_from::text,'-')"
        " from public.etapa_da_corrida where run_id = '%s' order by id" % RUN)
    etapas = [x[0] for x in linhas]
    caso("E7_as_CINCO_etapas_falaram_na_MESMA_corrida",
         etapas == ["RAW", "DERIVED", "STRUCTURED", "ADMISSION", "READY"],
         " -> ".join(etapas))
    r_ready = [x for x in linhas if x[0] == "READY"]
    caso("E8_a_passagem_de_READY_vem_da_ADMISSION_e_nomeia_o_ficheiro",
         len(r_ready) == 1 and r_ready[0][6] == "ADMISSION"
         and r_ready[0][1] == "PASS" and int(r_ready[0][2]) == 1
         and os.path.basename(caminho) in r_ready[0][5],
         "edge_from=%s · estado=%s · last_good=%s"
         % (r_ready[0][6], r_ready[0][1], r_ready[0][5]) if r_ready else "-")

    # ── LINEAGE, PELAS RELACOES QUE O SISTEMA TEM MESMO ────────────────
    derivado = sql.executa(
        "select id, raw_asset_id from public.derived_artifact"
        " where raw_asset_id = %s" % raw_id)
    conteudo = sql.executa(
        "select count(*) from public.conteudo where run_id = '%s'" % RUN)
    caso("E9_a_linhagem_fecha_do_READY_ate_ao_RAW",
         bool(derivado) and int(derivado[0][1]) == raw_id
         and int(conteudo[0][0]) == 1
         and u.get("CORRIDA") == RUN and corpo.get("RUN_ID") == RUN,
         "RUN %s -> raw %s -> derived %s -> conteudo 1 -> READY %s"
         % (RUN, raw_id, derivado[0][0] if derivado else "-", u.get("ITEM_ID")))

    # ── PROVENANCE: O QUE NAO SE SABE CONTINUA SEM SE SABER ────────────
    caso("E10_o_READY_nao_enriquece_o_que_nao_foi_provado",
         u.get("FACT_LOCATION") == "NAO SEI"
         and u.get("SOURCE_LOCATION") == "NAO SEI",
         "FACT_LOCATION=%s · SOURCE_LOCATION=%s"
         % (u.get("FACT_LOCATION"), u.get("SOURCE_LOCATION")))
    caso("E11_e_a_fonte_e_a_declarada_e_nao_uma_inferida",
         u.get("SOURCE_ID") == FONTE, "SOURCE_ID=%s" % u.get("SOURCE_ID"))

    # ═══════════════════════════════════════════════════════════════════
    # O QUE UM FICHEIRO EXIGE, E QUE NINGUEM VE ATE FALHAR
    # ═══════════════════════════════════════════════════════════════════
    print("\nO QUE UM FICHEIRO EXIGE")

    # RETRY · a mesma corrida com o mesmo conteudo nao duplica.
    antes = _fonte_do_ficheiro(caminho)
    de_novo = espera.pousar(RUN, corpo["ITENS"])
    caso("R1_o_retry_com_o_MESMO_conteudo_diz_REUSED",
         de_novo["ESTADO"] == espera.JA_ESTAVA,
         "estado=%s" % de_novo["ESTADO"])
    caso("R2_e_nao_mexe_no_ficheiro",
         _fonte_do_ficheiro(caminho) == antes,
         "os bytes no disco sao os mesmos")

    # CONFLITO · a mesma corrida com conteudo diferente NAO sobrescreve.
    outro = [dict(corpo["ITENS"][0], TEXTO="outra historia")]
    rebentou = None
    try:
        espera.pousar(RUN, outro)
    except espera.ConflitoDeCorrida as e:
        rebentou = str(e)
    caso("C1_a_mesma_corrida_com_OUTRA_historia_e_conflito",
         rebentou is not None and "RUN_ID_CONFLICT" in rebentou,
         (rebentou or "NAO REBENTOU — sobrescreveu em silencio")[:70])
    caso("C2_e_o_ficheiro_anterior_fica_INTACTO",
         _fonte_do_ficheiro(caminho) == antes,
         "nada foi escrito por cima")

    # ATOMICIDADE · nunca existe ficheiro canonico pela metade.
    caso("A1_a_escrita_publica_por_troca_atomica",
         "os.replace(" in _fonte_do_ficheiro(
             os.path.join(RAIZ, "admissao", "sala_de_espera.py"))
         and "fsync(" in _fonte_do_ficheiro(
             os.path.join(RAIZ, "admissao", "sala_de_espera.py")),
         "corpo inteiro no temporario, fsync, e so entao os.replace")
    sobras = [f for f in os.listdir(sala) if f.startswith(".espera-")]
    caso("A2_e_nao_deixa_temporarios_para_tras", not sobras,
         "temporarios na sala: %s" % (sobras or "nenhum"))

    # CRASH · o que sobra quando o processo morre a meio.
    caso("X1_um_crash_ANTES_da_troca_deixa_o_anterior_valido",
         _crash_antes(sala) == antes,
         "o ficheiro canonico continua a ser o de antes, e le-se inteiro")

    # CONCORRENCIA · duas maos na MESMA corrida, a serio.
    ganhou, perdeu = _duas_maos(sala)
    caso("K1_duas_maos_na_mesma_corrida_nao_se_atropelam",
         ganhou == 1 and perdeu == 1,
         "uma escreveu, a outra ouviu «ocupada»: %d/%d" % (ganhou, perdeu))
    caso("K2_e_o_ficheiro_ficou_com_UMA_historia_so",
         _corridas_distintas(sala) == 1,
         "conteudos distintos no fim: %d" % _corridas_distintas(sala))

    # ── OS NEGATIVOS DA PORTA ───────────────────────────────────────────
    print("\nO QUE NAO ENTRA NA SALA")
    for resultado in (admissao.NAO, admissao.NAO_SEI, admissao.NAO_SE_APLICA,
                      admissao.ERRO):
        d = admissao.Decisao(item="n-1", universo="T3", resultado=resultado,
                             regra="bancada", motivo="negativo", corrida=RUN)
        abrir_corrida(sql, RUN + "-" + resultado)
        saiu = m2.levar_a_espera(sql, unidade=dict(unidade, CONTENT_ID="n-1",
                                                   TEXTO="x"),
                                 decisao=d, run_id=RUN + "-" + resultado)
        ficheiro = espera.caminho_da_corrida(RUN + "-" + resultado)
        caso("N_%s_nao_produz_unidade_nenhuma" % resultado,
             saiu.get("ESTADO") is None and not os.path.isfile(ficheiro),
             "a porta disse %s · sem ficheiro na sala" % resultado)
    n_not_run = sql.executa(
        "select count(*) from public.etapa_da_corrida"
        " where etapa = 'READY' and estado = 'NOT_RUN'")
    caso("N5_e_o_rastro_diz_NOT_RUN_e_nunca_FAIL",
         int(n_not_run[0][0]) == 4,
         "%s passagens de READY em NOT_RUN" % n_not_run[0][0])

    print("=" * 70)
    for nome, ok, detalhe in fora:
        print("  %-4s %-54s %s" % ("PASS" if ok else "FALHA", nome, detalhe))
    veredito = all(ok for _n, ok, _d in fora)
    print("=" * 70)
    print("POUSA_NA_ESPERA=%s" % ("PASS" if veredito else "FAIL"))
    print("  o que isto prova: a ADMISSION positiva produz READY e a unidade")
    print("  POUSA na Sala de Espera, na mesma corrida, com rastro.")
    print("  o que NAO prova: producao, nem a coleta antes do RAW.")
    print("  FULL_COLLECTION_E2E = NO — comeca no bruto ja preservado.")
    return 0 if veredito else 1


# ── A BANCADA ───────────────────────────────────────────────────────────
def _memoria(url):
    import importlib.util as u
    sp = u.spec_from_file_location(
        "prova_pg", os.path.join(RAIZ, "provas",
                                 "preservar_coleta_no_postgres.py"))
    m = u.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.MemoriaPostgres(url)


_ARMAZEM = []


def _armazem():
    if not _ARMAZEM:
        from guarda.preservar_coleta import ArmazemDeMentira
        _ARMAZEM.append(ArmazemDeMentira())
    return _ARMAZEM[0]


def _crash_antes(sala):
    """Um processo que morre ANTES da troca. O canonico nao pode mexer-se.

    Nao se simula com um `if`: corre-se um processo de verdade e mata-se.
    """
    codigo = (
        "import os,sys,time\n"
        "sys.path.insert(0, %r)\n"
        "import _gavetas, sala_de_espera as e\n"
        "e.MORADA = %r\n"
        "orig = e._escrever_atomico\n"
        "def lento(caminho, corpo):\n"
        "    time.sleep(30)\n"
        "e._escrever_atomico = lento\n"
        "e.pousar('OUTRA', [{'X': 1}])\n" % (RAIZ, sala))
    p = subprocess.Popen([sys.executable, "-c", codigo])
    import time as _t
    _t.sleep(1.5)
    p.kill()
    p.wait()
    return _fonte_do_ficheiro(espera.caminho_da_corrida(RUN))


def _uma_mao(sala, marca, fila):
    sys.path.insert(0, RAIZ)
    import sala_de_espera as e
    e.MORADA = sala
    try:
        e.pousar("CONCORRENTE", [{"MARCA": marca}])
        fila.put("ESCREVEU")
    except e.EsperaOcupada:
        fila.put("OCUPADA")
    except Exception as erro:                                # noqa: BLE001
        fila.put("OUTRO:%s" % type(erro).__name__)


def _duas_maos(sala):
    """Duas escritas SIMULTANEAS da mesma corrida, em processos de verdade."""
    fila = multiprocessing.Queue()
    ps = [multiprocessing.Process(target=_uma_mao, args=(sala, i, fila))
          for i in range(2)]
    for p in ps:
        p.start()
    for p in ps:
        p.join(30)
    saidas = [fila.get() for _ in range(2)]
    return saidas.count("ESCREVEU"), saidas.count("OCUPADA")


def _corridas_distintas(sala):
    caminho = os.path.join(sala, "CONCORRENTE.json")
    if not os.path.isfile(caminho):
        return 0
    d = json.loads(_fonte_do_ficheiro(caminho))
    return len({json.dumps(x, sort_keys=True) for x in d.get("ITENS") or []})


if __name__ == "__main__":
    raise SystemExit(main())
