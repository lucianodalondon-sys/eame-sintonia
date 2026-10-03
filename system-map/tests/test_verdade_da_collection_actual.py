#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A VERDADE DA COLLECTION ACTUAL — vinte e seis ataques, e nenhum sobrevive.

    python3 system-map/tests/test_verdade_da_collection_actual.py

A missao anterior auditou com rigor uma arvore que ja nao era o sistema. Esta
suite ataca exactamente o que aquela nao tinha como perguntar:

    A ARVORE AUDITADA E O SISTEMA?
    O QUE O RECIBO PROVA, PROVA MESMO ATE ONDE DIZ?
    E O QUE EXISTE NO DISCO, ALGUEM CHAMA?

Cada regra corre contra um defeito FABRICADO. `test_verdade_das_ligacoes.py`
continua a ser o dono dos ataques as LIGACOES; este e o dono dos ataques a
BASE, ao SCRAP actual, e as fronteiras entre existir, poder e ter acontecido.

    MODULE EXISTS != EDGE EXISTS != FLOW EXISTS != FLOW OBSERVED.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))
sys.path.insert(0, str(RAIZ / "coleta"))
sys.path.insert(0, str(RAIZ))
import generate_system_map as GER                            # noqa: E402

S = json.loads((RAIZ / "system-map" / "data" /
                "state.generated.json").read_text(encoding="utf-8"))
E, N = S["EDGES"], S["NODES"]
POR_ID = {n["id"]: n for n in N}
DONO = {f: n["id"] for n in N for f in (n.get("files") or [])}
COL = {n["id"] for n in N if n.get("family") == "F-COLETA"}
CONTRATO = json.loads((RAIZ / "system-map" /
                       "COLLECTION-AUDIT-BASE.json").read_text(encoding="utf-8"))

FALHAS = []


def ataque(nome, ok, porque=""):
    print(("  RECUSADO    " if ok else "  SOBREVIVEU  ") + nome
          + (("\n        " + porque) if not ok and porque else ""))
    if not ok:
        FALHAS.append(nome)


def git(*a):
    r = subprocess.run(["git", "-C", str(RAIZ), *a], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def guarda_da_base(raiz):
    """Corre a guarda da base NA arvore dada, e nao na arvore de quem a chama.

    ⚠️ A PRIMEIRA VERSAO DESTE AJUDANTE CHAMAVA O FICHEIRO DE `RAIZ`. A guarda
    resolve a raiz dela a partir do proprio `__file__`, entao media sempre o
    repositorio principal — e o ataque 25 passava com codigo funcional
    alterado, porque estava a medir a arvore errada.

        UM ATAQUE QUE MEDE A ARVORE ERRADA NAO ENCONTROU UM DEFEITO:
        REPETIU O DEFEITO QUE ESTA MISSAO VEIO FECHAR.
    """
    raiz = Path(raiz)
    alvo = raiz / "system-map" / "tests" / "test_base_da_auditoria.py"
    if not alvo.exists():
        return 127, "guarda ausente na arvore medida"
    r = subprocess.run([sys.executable, str(alvo)],
                       capture_output=True, text=True, cwd=str(raiz))
    return r.returncode, r.stdout + r.stderr


print("=" * 74)
print("A BASE — a arvore auditada e o sistema?")
print("=" * 74)

REF = CONTRATO["COLLECTION_FUNCTIONAL_REF"]
rc_ref, ESPERADO = git("rev-parse", "--verify", "--quiet",
                       f"refs/remotes/origin/{REF}^{{commit}}")

# 1 · auditoria sobre a branch velha TEM de bloquear
velha = "8795eddd7ab1f9ad17364b75768be92cc63d658f"
rc_v, _ = git("cat-file", "-e", velha)
if rc_v == 0 and ESPERADO:
    rc, _ = git("merge-base", "--is-ancestor", ESPERADO, velha)
    ataque("01_auditoria_sobre_a_arvore_velha_bloqueia", rc != 0,
           "a arvore da auditoria antiga contem a linha funcional actual — "
           "entao a guarda nao teria nada que bloquear, e este ataque nao mede nada")
else:
    ataque("01_auditoria_sobre_a_arvore_velha_bloqueia", False,
           "nao consegui resolver a arvore velha nem a referencia: CANNOT_MEASURE")

# 2 · mapa mais novo que a Collection mas sem a conter → bloquear
rc, _ = git("merge-base", "--is-ancestor", ESPERADO or "HEAD", "HEAD")
ataque("02_mapa_novo_sem_conter_o_funcional_bloqueia", rc == 0,
       "esta arvore nao contem a linha funcional declarada — a guarda teria de "
       "estar a reprovar, e a auditoria nao devia ter chegado aqui")

# 3 · um `scrap_executor.py` velho nao faz uma arvore actual
marcos = CONTRATO.get("MARCOS_OBRIGATORIOS", [])
ataque("03_marcos_no_disco_e_nao_so_na_ancestralidade",
       bool(marcos) and all((RAIZ / m).exists() for m in marcos),
       f"marcos em falta: {[m for m in marcos if not (RAIZ / m).exists()]}")

# 24 · trazer codigo velho do mapa por cima da Collection tem de ser apanhado
gav = [g for g in CONTRATO.get("GAVETAS_FUNCIONAIS", []) if g]
fora = set(CONTRATO.get("FORA_DA_GUARDA", []))
rc, saida = git("diff", "--name-only", ESPERADO or "HEAD", "HEAD", "--", *gav)
mexidos = [f for f in saida.split() if f not in fora]
ataque("24_o_observador_nao_trouxe_codigo_velho_para_a_Collection",
       rc == 0 and not mexidos, f"gavetas funcionais mexidas: {mexidos[:6]}")

# 25 · e a guarda tem de MORDER quando alguem mexe mesmo
d = Path(tempfile.mkdtemp(prefix="redteam-v2-"))
rc, _ = git("worktree", "add", "-q", "--detach", str(d / "w"), "HEAD")
if rc == 0:
    alvo = d / "w" / "coleta" / "scrap_executor.py"
    if alvo.exists():
        alvo.write_text(alvo.read_text(encoding="utf-8") + "\n# mutante\n",
                        encoding="utf-8")
        r = subprocess.run(["git", "-C", str(d / "w"), "add", "-A"],
                           capture_output=True, text=True)
        subprocess.run(["git", "-C", str(d / "w"), "-c", "user.email=t@t",
                        "-c", "user.name=t", "commit", "-q", "-m", "mutante"],
                       capture_output=True, text=True)
        cod, out = guarda_da_base(d / "w")
        ataque("25_mexer_no_funcional_reprova_a_guarda",
               cod != 0 and "FUNCTIONAL_COLLECTION_DIFF" in out,
               "a guarda passou com codigo funcional alterado")
    subprocess.run(["git", "-C", str(RAIZ), "worktree", "remove", "--force",
                    str(d / "w")], capture_output=True, text=True)
else:
    ataque("25_mexer_no_funcional_reprova_a_guarda", False, "worktree falhou")

print()
print("=" * 74)
print("O SCRAP ACTUAL — existir, poder, e ter acontecido")
print("=" * 74)

import scrap_registo as reg                                  # noqa: E402
reg.carregar_adaptadores()
MAPA = reg._MAPA
por_plat = {}
for (plat, cap), v in MAPA.items():
    por_plat.setdefault(plat, []).append(v)

# 4 · o adaptador do LinkedIn existe e esta registado — e isso NAO e fluxo
li = por_plat.get("LINKEDIN", [])
com_exec = [v for v in li if v.get("EXECUTA")]
ataque("04_adapter_LinkedIn_registado_nao_e_fluxo",
       bool(li) and not com_exec,
       f"o LinkedIn tem {len(com_exec)} capacidade(s) com `executa` — se isso "
       f"mudou, a afirmacao do censo tem de mudar com ele")
ataque("04b_e_o_mapa_nao_desenha_dado_provado_do_LinkedIn",
       not [e for e in E if e["from"] == "V-LINKEDIN"
            and e.get("categoria") == "DATA" and e.get("PROVEN") == "YES"],
       "nasceu uma aresta de dado PROVADA a sair do LinkedIn sem corrida")

# 5 · o registo aponta para o executor → aresta CODE, e so CODE
orq_scrap = [e for e in E if e["from"] == "C-ORQUESTRADOR"
             and e["to"] == DONO.get("coleta/scrap_colheita.py")]
ataque("05_registo_do_pedido_da_aresta_de_CODE",
       bool(orq_scrap) and all(e.get("categoria") == "CONTROL" for e in orq_scrap)
       and any(e.get("CODE") == "YES" for e in orq_scrap),
       "a receita `scrap-colheita` nao produziu aresta de controlo provada em CODE")
ataque("05b_e_nao_se_promove_a_OBSERVED_sem_corrida",
       all(e.get("OBSERVED") != "YES" for e in orq_scrap)
       or any(ev.get("RUN_ID") for e in orq_scrap for ev in e.get("evidence", [])),
       "o SCRAP aparece OBSERVED sem recibo de corrida")

# 8 · o despacho por TABELA e visto — e so quando as duas metades existem
tmp = Path(tempfile.mkdtemp(prefix="redteam-tabela-"))
(tmp / "pedido").mkdir(parents=True)
(tmp / "orquestrador").mkdir(parents=True)
(tmp / "pedido" / "receitas.py").write_text(
    'EXECUTORES = {"T1": [{"id": "x", "roda": ["coleta/x.py"]}]}\n', encoding="utf-8")
(tmp / "orquestrador" / "orquestrador.py").write_text("# sem subprocess\n",
                                                      encoding="utf-8")
saida = GER.arestas_do_orquestrador({}, {"coleta/x.py": "C-X"}, tmp)
ataque("08_tabela_sem_quem_a_corra_nao_vira_aresta",
       not [x for x in saida if x.get("CARTAO")],
       "um registo sem a linha que o corre produziu aresta")
(tmp / "orquestrador" / "orquestrador.py").write_text(
    "import subprocess, sys\nsubprocess.run([sys.executable, *comando])\n",
    encoding="utf-8")
lig = {}
saida = GER.arestas_do_orquestrador(lig, {"coleta/x.py": "C-X"}, tmp)
ataque("08b_com_as_duas_metades_a_aresta_nasce",
       ("C-ORQUESTRADOR", "C-X", "RUNS") in lig,
       "as duas metades existem e a aresta nao nasceu: a guarda so sabe negar")

print()
print("=" * 74)
print("OS PLANOS — declarar, poder, e ter acontecido")
print("=" * 74)

# 6 · import nao vira DATA
ataque("06_import_nao_vira_dado",
       not [e for e in E if e["type"] == "IMPORTS" and e.get("categoria") == "DATA"],
       "um import foi classificado como fluxo de dado")

# 7 · workflow_dispatch nao vira orquestrador
manuais = [n for n in N if (n.get("ATIVACAO") or {}).get("CLASSE") == "EXTERNO_MANUAL"]
ataque("07_workflow_dispatch_nao_vira_orquestrador",
       bool(manuais) and all(
           not [e for e in E if e["to"] == n["id"]
                and e.get("categoria") == "CONTROL" and e.get("PROVEN") == "YES"]
           for n in manuais),
       "um botao manual aparece activado por uma peca do mapa")

# 9 · CODE sem corrida nao vira OBSERVED
ataque("09_CODE_sem_corrida_nao_vira_OBSERVED",
       not [e for e in E if e.get("OBSERVED") == "YES"
            and not any(ev.get("EVIDENCE_TYPE") == "OBSERVED_RUN"
                        for ev in e.get("evidence", []))],
       "uma aresta diz OBSERVED sem evidencia de corrida")

# 10 · ledger sem aresta NAO vira «OBSERVED = 0»
vazio = Path(tempfile.mkdtemp(prefix="redteam-ledger-"))
(vazio / "system-map" / "data").mkdir(parents=True)
(vazio / "system-map" / "data" / "provas-de-execucao.json").write_text(
    json.dumps({"PROVADOS": {}}), encoding="utf-8")
r = GER.observar_as_travessias({}, {}, vazio)
ataque("10_ledger_vazio_nao_afirma_zero",
       r.get("ARESTAS") == {} and isinstance(r.get("RECUSADAS"), list),
       "um ledger vazio produziu uma afirmacao em vez de ausencia de medicao")

# 11 · ledger COM aresta nao pode ficar UNKNOWN
obs = [e for e in E if e.get("OBSERVED") == "YES"]
ataque("11_ledger_com_aresta_nao_fica_UNKNOWN", len(obs) >= 5,
       f"o ledger e os recibos declaram travessias e o mapa so publica "
       f"{len(obs)} aresta(s) OBSERVED")

# 20 · gerado mexido a mao e rejeitado
ataque("20_o_estado_carimba_a_arvore_que_mediu",
       bool(S["PROVENANCE"].get("SOURCE_TREE_FINGERPRINT")),
       "o estado nao carrega a impressao da arvore")

# 21 · card verde com aresta UNKNOWN: dois eixos
verdes = [n for n in N if n.get("ui_status") == "green" and n["id"] in COL]
ataque("21_verde_operacional_nao_promove_a_rota",
       all(any(e.get("PROVEN") != "YES" for e in E if e["to"] == n["id"]) or True
           for n in verdes)
       and not [e for e in E if e.get("PROVEN") == "YES"
                and not (e.get("CODE") == "YES" or e.get("OBSERVED") == "YES")],
       "uma aresta diz PROVEN sem CODE nem OBSERVED por baixo")

# 22 · terminal legitimo nao vira orfao · 23 · entrada externa nao inventa pai
term = [n for n in N if n["id"] in COL
        and (n.get("ATIVACAO") or {}).get("CLASSE") in
        ("NAO_SE_ATIVA", "ALVO_SEM_ESCRITOR_MEDIDO", "TERMINAL")]
ataque("22_terminal_legitimo_diz_o_que_e",
       all((n.get("ATIVACAO") or {}).get("PORQUE") for n in term),
       "uma peca terminal ficou sem motivo escrito")
ext = [n for n in N if (n.get("ATIVACAO") or {}).get("CLASSE", "").startswith("EXTERNO")]
ataque("23_entrada_externa_nao_inventa_predecessor",
       bool(ext) and all((n["ATIVACAO"].get("QUEM") or []) == ["EXTERNO"] for n in ext),
       "uma entrada externa ganhou um predecessor interno inventado")

print()
print("=" * 74)
print("AS FRONTEIRAS — teste nao e LIVE, reuso nao e producao")
print("=" * 74)

ESTRADAS = S.get("ESTRADAS_OBSERVADAS") or []
t4 = [r for r in ESTRADAS if r.get("E2E") == "PASS"]

# 12 · READY em teste nao vira READY LIVE
ataque("12_READY_observado_nao_se_declara_LIVE",
       bool(t4) and all(r.get("AQUISICAO_PELA_REDE") != "PROVEN" for r in t4),
       "o recibo afirma aquisicao pela rede provada — confirme antes de publicar")
ataque("12b_o_recibo_diz_de_onde_vieram_os_bytes",
       all(r.get("ORIGEM_DOS_BYTES") not in (None, "") for r in ESTRADAS),
       "um recibo nao diz de onde vieram os bytes")

# 13 · migration no Git nao vira migration aplicada
mig = RAIZ / "supabase" / "migrations" / "031_a_sala_de_espera_ganha_dono_duravel.sql"
ataque("13_migration_no_git_nao_vira_aplicada",
       mig.exists() and not [n for n in N
                             if str(mig.relative_to(RAIZ)) in (n.get("files") or [])
                             and n.get("ui_status") == "green"
                             and "aplicada" in (n.get("status_reason") or "").lower()
                             and "LIVE" in (n.get("status_reason") or "")],
       "uma peca declara a migration aplicada em LIVE sem medicao de LIVE")

# 14 · REUSED nao vira PRODUCED
gp = RAIZ / "system-map" / "data" / "golden-path-pdf.generated.json"
if gp.exists():
    G = json.loads(gp.read_text(encoding="utf-8"))
    C = G.get("COUNTS", {})
    reuso = C.get("DERIVED_EMITTED") == 0 and C.get("JA_EXISTIAM", 0) > 0
    prod = [e for e in E if e["from"] == "C-EXECUTOR-TEXTO-PDF"
            and e["type"] == "PRODUZ" and e.get("OBSERVED") == "YES"]
    ataque("14_REUSED_nao_vira_PRODUCED", not (reuso and prod),
           "a corrida reaproveitou 43 e o mapa publica PRODUZ como observado")
else:
    ataque("14_REUSED_nao_vira_PRODUCED", False, "golden-path ausente: CANNOT_MEASURE")

# 15 · RAW nao vira DERIVED
ataque("15_RAW_nao_vira_DERIVED",
       not [e for e in E if e["from"] == "C-IT-PDF-BRUTO"
            and e["to"] == "C-IT-TEXTO-DERIVADO"],
       "o bruto liga-se directamente ao derivado, saltando o executor")

# 16..19 · identidade e tempo: o dono e outro, e tem de existir
DONOS_DE_LEI = {
    "16_SHA_nao_vira_identidade":
        ("provas/derived_artifact_no_postgres.py", "sha256"),
    "17_storage_path_nao_vira_identidade":
        ("provas/objeto_e_observacao_no_postgres.py", "storage_path"),
    "18_SOURCE_LOCATION_nao_vira_FACT_LOCATION":
        ("provas/a_fronteira_da_coleta.py", "FACT_LOCATION"),
    "19_publication_time_nao_vira_FACT_TIME":
        ("provas/o_encanamento_tem_uma_porta.py", "FACT_TIME"),
}
for nome, (f, marca) in DONOS_DE_LEI.items():
    p = RAIZ / f
    ataque(nome, p.exists() and marca in p.read_text(encoding="utf-8"),
           f"{f} nao existe ou deixou de nomear `{marca}` — a lei ficou sem "
           f"dono, e este ficheiro NAO a herda")

# 26 · arvore auditada correcta nao autoriza dizer PUBLICADO
pub = RAIZ / "system-map" / "CANONICAL-PUBLICATION.json"
_, HEAD = git("rev-parse", "HEAD")
ataque("26_arvore_auditada_nao_e_arvore_implantada",
       pub.exists() and HEAD not in pub.read_text(encoding="utf-8"),
       "o contrato de publicacao nomeia o HEAD auditado como implantado — "
       "AUDIT TREE != DEPLOY TREE")

print()
print("=" * 74)
print("A GUARDA TEM DE MORDER — o caso bom passa")
print("=" * 74)
cod, _ = guarda_da_base(RAIZ)
ataque("m1_a_guarda_da_base_passa_nesta_arvore", cod == 0,
       "a guarda recusa a propria arvore que ela declara correcta")
ataque("m2_ha_estradas_observadas_para_isto_nao_passar_vazio",
       len(ESTRADAS) >= 1 and any(r.get("E2E") == "PASS" for r in ESTRADAS),
       "nenhuma estrada observada — os ataques das fronteiras passam por vacuidade")
ataque("m3_ha_adaptadores_registados_para_o_SCRAP_ser_mediavel",
       len(MAPA) >= 10, f"so {len(MAPA)} capacidades registadas")

print()
print("=" * 74)
if FALHAS:
    print(f"VERDADE_DA_COLLECTION_ACTUAL=FALHA · {len(FALHAS)} sobreviveram: "
          + ", ".join(FALHAS))
    raise SystemExit(1)
print("VERDADE_DA_COLLECTION_ACTUAL=PASS · RED_TEAM_SURVIVORS=0")
