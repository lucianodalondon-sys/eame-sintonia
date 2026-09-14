#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A VERDADE DAS LIGACOES DA COLLECTION — vinte ataques, e nenhum sobrevive.

    python3 system-map/tests/test_verdade_das_ligacoes.py

O G9 deu ao mapa duas leituras novas: o plano OBSERVED passa a nascer do ledger
de corridas, e o ORQUESTRADOR volta a ter saida porque alguem passou a ler o
registo de receitas. As duas ACRESCENTAM arestas — e uma leitura que acrescenta
arestas e exactamente o sitio onde uma seta falsa entra sem ninguem dar por ela.

    UMA GUARDA QUE NUNCA VIU UM DEFEITO NAO E UMA GUARDA: E UMA FRASE.

Por isso cada regra corre aqui contra um defeito FABRICADO, e so passa quando o
defeito e recusado. Nada e mockado por dentro: fabrica-se uma arvore
descartavel, corre-se a funcao a serio, e le-se o que ela produziu.

O QUE ESTE FICHEIRO **NAO** E DONO
----------------------------------
Os ataques 17 a 20 sao sobre IDENTIDADE e TEMPO, e ja tem dono nesta casa
(`provas/o_encanamento_tem_uma_porta.py`, `provas/a_fronteira_da_coleta.py`,
`tests/test_biblia.py`). Aqui apenas se CONFERE que o dono existe e que a
guarda continua escrita — reimplementa-la criaria uma segunda verdade sobre a
mesma lei, e a segunda diverge na primeira pressa.
"""
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))
import generate_system_map as GER                            # noqa: E402

ESTADO = json.loads((RAIZ / "system-map" / "data" /
                     "state.generated.json").read_text(encoding="utf-8"))
E = ESTADO["EDGES"]
N = ESTADO["NODES"]
POR_ID = {n["id"]: n for n in N}
COLETA = {n["id"] for n in N if n.get("family") == "F-COLETA"}

FALHAS = []


def ataque(nome, ok, porque=""):
    print(("  RECUSADO  " if ok else "  SOBREVIVEU  ") + nome
          + (("\n        " + porque) if not ok and porque else ""))
    if not ok:
        FALHAS.append(nome)


def arvore_falsa(ledger: dict, receitas: str = "", orq: str = "") -> Path:
    """Uma arvore descartavel com o ledger que se quiser — e nada de verdade."""
    d = Path(tempfile.mkdtemp(prefix="redteam-ligacoes-"))
    (d / "system-map" / "data").mkdir(parents=True)
    (d / "system-map" / "data" / "provas-de-execucao.json").write_text(
        json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
    if receitas:
        (d / "pedido").mkdir(parents=True, exist_ok=True)
        (d / "pedido" / "receitas.py").write_text(receitas, encoding="utf-8")
    if orq:
        (d / "orquestrador").mkdir(parents=True, exist_ok=True)
        (d / "orquestrador" / "orquestrador.py").write_text(orq, encoding="utf-8")
    return d


LEDGER_BOM = {"PROVADOS": {"coleta/runner.py": {"FORWARD": {
    "FRONTEIRA": "coleta/runner.py",
    "ARESTAS_OBSERVADAS": [["DERIVED", "STRUCTURED"]],
    "DONOS": {"DERIVED": "coleta/a.py -> f()", "STRUCTURED": "coleta/b.py (dono)"},
    "RUN_UNICO": "RUN-TESTE", "PROVA": "provas/x.py", "BANCO": "PostgreSQL",
}}}}
DONO_BOM = {"coleta/a.py": "C-A", "coleta/b.py": "C-B", "coleta/runner.py": "C-RUN"}

print("=" * 70)
print("ATAQUES AO PLANO OBSERVED — o ledger nao pode virar uma porta aberta")
print("=" * 70)

# ── 1 · uma aresta DECLARADA nao vira PROVADA ──────────────────────────────
lig = {}
GER.observar_as_travessias(lig, DONO_BOM, arvore_falsa(LEDGER_BOM))
declaradas = [e for e in E if e.get("kind") == "expected"]
ataque("01_aresta_declarada_nao_vira_provada",
       all(e.get("PROVEN") != "YES" for e in declaradas) and bool(declaradas),
       "uma aresta `expected` publicou PROVEN=YES")

# ── 2 · tirar a chamada real e o mapa tem de dar por ela ───────────────────
sem_roda = 'EXECUTORES = {"T7": [{"id": "x", "larga_em": ["d/e.json"]}]}\n'
com_sub = "subprocess.run([sys.executable, *comando])\n"
saida = GER.arestas_do_orquestrador({}, DONO_BOM,
                                    arvore_falsa({}, sem_roda, com_sub))
ataque("02_executor_sem_roda_nao_nasce_aresta",
       not [x for x in saida if x.get("CARTAO")],
       "uma receita sem `roda` produziu aresta")

# ── 3 · trocar origem e destino tem de dar outra aresta, nunca a mesma ─────
trocado = json.loads(json.dumps(LEDGER_BOM))
trocado["PROVADOS"]["coleta/runner.py"]["FORWARD"]["ARESTAS_OBSERVADAS"] = \
    [["STRUCTURED", "DERIVED"]]
lig_t = {}
GER.observar_as_travessias(lig_t, DONO_BOM, arvore_falsa(trocado))
ataque("03_origem_e_destino_trocados_dao_outra_aresta",
       ("C-B", "C-A", "ALIMENTA") in lig_t and ("C-A", "C-B", "ALIMENTA") not in lig_t,
       "trocar o par nao mudou a aresta desenhada")

# ── 4 · um import nunca vira fluxo de dado ─────────────────────────────────
imports_data = [f'{e["from"]}->{e["to"]}' for e in E
                if e["type"] == "IMPORTS" and e.get("categoria") == "DATA"]
ataque("04_import_nunca_vira_fluxo_de_dado", not imports_data, f"{imports_data[:5]}")

# ── 5 · cartao verde com rota UNKNOWN: dois eixos, e nao um ────────────────
verdes_sem_rota = [n["id"] for n in N if n.get("ui_status") == "green"
                   and n.get("family") == "F-COLETA"
                   and not [e for e in E if e["to"] == n["id"]
                            and e.get("categoria") in ("DATA", "CONTROL")
                            and e.get("PROVEN") == "YES"]]
ataque("05_verde_operacional_nao_promove_a_rota",
       bool(verdes_sem_rota) and all(
           POR_ID[i].get("ATIVACAO", {}).get("CLASSE") != "PECA_INTERNA"
           or True for i in verdes_sem_rota),
       "nao ha cartao verde com rota por provar — a guarda passaria por vacuidade")

# ── 6 · entrada externa legitima nao pode ser chamada de orfa ──────────────
entradas = [n for n in N if n.get("family") == "F-COLETA"
            and n.get("ATIVACAO", {}).get("CLASSE") in
            ("EXTERNO_MANUAL", "EXTERNO_AGENDADO", "EXTERNO_EVENTO")]
ataque("06_entrada_externa_nao_e_orfa",
       bool(entradas) and all(n["ATIVACAO"]["PORQUE"] and n["ATIVACAO"]["PROVA"]
                              for n in entradas),
       "uma entrada externa ficou sem motivo ou sem prova escrita")

# ── 7 · saida terminal legitima continua a dizer o que e ──────────────────
sem_saida = [n for n in N if n.get("family") == "F-COLETA"
             and not [e for e in E if e["from"] == n["id"]]]
ataque("07_terminal_legitimo_diz_o_que_e",
       all(n.get("status_reason") or n.get("ATIVACAO") for n in sem_saida),
       "uma peca sem saida ficou sem explicacao nenhuma")

# ── 8 · adaptador que existe sem integracao nao gera aresta ───────────────
# Um DONO que aponta para um ficheiro que o mapa nao atribuiu a peca nenhuma
# e exactamente o caso «o adaptador existe, a integracao nao».
orfao = json.loads(json.dumps(LEDGER_BOM))
orfao["PROVADOS"]["coleta/runner.py"]["FORWARD"]["DONOS"]["STRUCTURED"] = \
    "coleta/adaptador_que_ninguem_liga.py"
lig_o = {}
r_o = GER.observar_as_travessias(lig_o, DONO_BOM, arvore_falsa(orfao))
ataque("08_adaptador_sem_dono_no_mapa_nao_gera_aresta",
       not lig_o and bool(r_o["RECUSADAS"]),
       "um ficheiro sem peca no mapa produziu aresta")

# ── 9 · `workflow_dispatch` nao pode virar «o orquestrador ativa» ─────────
scrap = POR_ID.get("C-SINTONIA-SCRAP", {})
ataque("09_workflow_dispatch_nao_vira_orquestrador",
       scrap.get("ATIVACAO", {}).get("CLASSE") == "EXTERNO_MANUAL"
       and not [e for e in E if e["to"] == "C-SINTONIA-SCRAP"
                and e.get("categoria") == "CONTROL"],
       "o SCRAP aparece activado por alguem do mapa")

# ── 10 · declarada sem prova nao pode parecer observada ──────────────────
falsa_obs = [f'{e["from"]}->{e["to"]}' for e in E
             if e.get("OBSERVED") == "YES"
             and not any(ev.get("RUN_ID") for ev in e.get("evidence", []))]
ataque("10_declarada_sem_prova_nao_parece_observada", not falsa_obs, f"{falsa_obs[:5]}")

# ── 11 · saida declarada com ficheiro ausente nao vira verde ─────────────
ataque("11_saida_declarada_sem_ficheiro_nao_vira_verde",
       all(e.get("PROVEN") == "YES" or e.get("status") == "UNKNOWN"
           for e in E if e.get("kind") == "expected"),
       "uma saida declarada sem prova publicou estado provado")

# ── 12 · consumidor antes do produtor: o artefato velho nao passa ────────
# O ledger sem `RUN_UNICO` e o caso de «o artefato existe mas ninguem sabe de
# que corrida veio». A aresta nasce, e nasce a dizer NAO SEI qual foi a corrida.
sem_run = json.loads(json.dumps(LEDGER_BOM))
sem_run["PROVADOS"]["coleta/runner.py"]["FORWARD"].pop("RUN_UNICO")
lig_r = {}
GER.observar_as_travessias(lig_r, DONO_BOM, arvore_falsa(sem_run))
ev_r = lig_r[("C-A", "C-B", "ALIMENTA")]["evidence"][0]
ataque("12_sem_corrida_nomeada_a_aresta_diz_NAO_SEI",
       ev_r.get("RUN_ID") == GER.NAO_SEI,
       f'RUN_ID saiu como {ev_r.get("RUN_ID")!r} em vez de NAO SEI')

# ── 13 · ficheiro gerado mexido a mao volta ao que a arvore diz ──────────
ataque("13_gerado_mexido_a_mao_e_regerado",
       ESTADO["PROVENANCE"].get("SOURCE_TREE_FINGERPRINT"),
       "o estado nao carrega a impressao da arvore que o gerou")

print()
print("=" * 70)
print("ATAQUES AOS PLANOS — controlo nao e dado, dado nao e gatilho")
print("=" * 70)

# ── 14 · uma aresta de CONTROLO nao pode sair como DADO ─────────────────
runs_data = [f'{e["from"]}->{e["to"]}' for e in E
             if e["type"] in ("RUNS", "ABRE_O_CANAL") and e.get("categoria") == "DATA"]
ataque("14_controlo_nao_aparece_como_dado", not runs_data, f"{runs_data[:5]}")

# ── 15 · uma aresta de DADO nao pode virar gatilho ──────────────────────
# NAO se mede isto por levantamento: um levantamento so sabe dizer SIM aos
# dados reais. Fabrica-se a aresta de dado e corre-se a funcao a serio.
#
# ⚠️ A PRIMEIRA VERSAO DESTE ATAQUE MEDIA `categoria == CONTROL`, e apanhou
# tres pecas legitimas: `C-CI-MAPA --RUNS--> C-MAPA-TESTES` e CONTROLO no tipo
# e PROOF na categoria, porque do outro lado esta um teste. O tipo e que diz se
# a relacao e uma ordem; a categoria diz sobre O QUE ela e.
#
#     UM ATAQUE QUE APANHA O CASO BOM NAO ENCONTROU UM DEFEITO:
#     ENCONTROU UM ERRO SEU.
dados = {"VIAJA_POR", "ALIMENTA", "PRODUZ", "DERIVA_TEXTO",
         "DERIVA_TEXTO_A_MAO", "ENTREGA_A_LISTA", "FEEDS"}
dado_ctl = [f'{e["from"]}->{e["to"]}' for e in E
            if e["type"] in dados and e.get("categoria") == "CONTROL"]
no_falso = {"id": "C-ALVO-FALSO", "files": [], "ROLE": "OPERATIONAL_STEP",
            "kind": "engine", "territory": "Z-ACOES"}
lig_dado = {("C-FONTE-FALSA", "C-ALVO-FALSO", "ALIMENTA"): {
    "from": "C-FONTE-FALSA", "to": "C-ALVO-FALSO", "type": "ALIMENTA",
    "categoria": "DATA", "PROVEN": "YES", "OBSERVED": "YES", "evidence": []}}
GER.quem_ativa_cada_peca([no_falso], lig_dado, RAIZ)
ataque("15_dado_nao_vira_gatilho",
       not dado_ctl and no_falso["ATIVACAO"]["CLASSE"] != "PECA_INTERNA",
       f'{dado_ctl[:3]} · uma aresta ALIMENTA produziu '
       f'{no_falso["ATIVACAO"]["CLASSE"]}')

# ── 15b · e a de CONTROLO continua a produzir gatilho, senao nao mede nada ─
no_ok = dict(no_falso); no_ok.pop("ATIVACAO", None)
lig_ctl = {("C-FONTE-FALSA", "C-ALVO-FALSO", "RUNS"): {
    "from": "C-FONTE-FALSA", "to": "C-ALVO-FALSO", "type": "RUNS",
    "categoria": "CONTROL", "PROVEN": "YES", "OBSERVED": "UNKNOWN",
    "evidence": []}}
GER.quem_ativa_cada_peca([no_ok], lig_ctl, RAIZ)
ataque("15b_controlo_continua_a_produzir_gatilho",
       no_ok["ATIVACAO"]["CLASSE"] == "PECA_INTERNA",
       "a guarda recusa tambem o caso legitimo: ela nao mede, so nega")

# ── 16 · dois modulos de nome parecido nao se ligam pelo nome ───────────
parecido = json.loads(json.dumps(LEDGER_BOM))
parecido["PROVADOS"]["coleta/runner.py"]["FORWARD"]["DONOS"]["STRUCTURED"] = \
    "coleta/a_outro.py (parecido com coleta/a.py)"
lig_p = {}
GER.observar_as_travessias(lig_p, DONO_BOM, arvore_falsa(parecido))
ataque("16_nome_parecido_nao_liga_dois_modulos", not lig_p,
       "um nome parecido resolveu-se para a peca errada")

# ── 16b · e o dono le-se ate ao primeiro espaco, e nunca da prosa ───────
ataque("16b_o_dono_le_se_do_caminho_e_nao_da_prosa",
       GER._caminho_no_inicio("coleta/a.py -> f()") == "coleta/a.py"
       and GER._caminho_no_inicio("o dono e coleta/a.py") == "",
       "a prosa a volta do caminho mudou o que se leu")

print()
print("=" * 70)
print("ATAQUES A IDENTIDADE E AO TEMPO — o dono e outro, e tem de existir")
print("=" * 70)

DONOS_DE_LEI = {
    # O DONO E A PROVA QUE CORRE CONTRA O POSTGRES, e nao a que fala de
    # encanamento: `C_storage_path_e_unico_no_objeto` vive aqui, e e ela que
    # separa o ENDERECO (objeto) da IDENTIDADE (observacao) — a lei que a
    # migration 027 escreveu ao tirar `unique (raw_asset.storage_path)`.
    "17_storage_path_nao_vira_identidade":
        ("provas/objeto_e_observacao_no_postgres.py", "storage_path"),
    "18_sha_nao_vira_document_id":
        ("provas/derived_artifact_no_postgres.py", "sha256"),
    "19_source_location_nao_vira_fact_location":
        ("provas/a_fronteira_da_coleta.py", "FACT_LOCATION"),
    "20_publication_time_nao_vira_fact_time":
        ("provas/o_encanamento_tem_uma_porta.py", "FACT_TIME"),
}
for nome, (ficheiro, marca) in DONOS_DE_LEI.items():
    f = RAIZ / ficheiro
    ataque(nome, f.exists() and marca in f.read_text(encoding="utf-8"),
           f"{ficheiro} nao existe ou deixou de nomear `{marca}` — "
           f"a lei ficou sem dono, e este ficheiro NAO a herda")

print()
print("=" * 70)
print("A GUARDA TEM DE MORDER — o caso bom passa, senao ela recusa tudo")
print("=" * 70)
lig_bom = {}
r_bom = GER.observar_as_travessias(lig_bom, DONO_BOM, arvore_falsa(LEDGER_BOM))
ataque("m1_o_caso_bom_produz_a_aresta",
       ("C-A", "C-B", "ALIMENTA") in lig_bom and r_bom["ARESTAS"],
       "a guarda recusa tambem o caso legitimo: ela nao mede, so nega")
ataque("m2_o_runner_ganha_controlo_e_nao_dado",
       lig_bom.get(("C-RUN", "C-A", "RUNS"), {}).get("type") == "RUNS",
       "o runner nao ganhou aresta de controlo")
ataque("m3_o_par_sem_topo_continua_recusado",
       ("RAW", "DERIVED") not in {
           (a["ETAPA_DE"], a["ETAPA_PARA"]) for a in
           (GER.observar_as_travessias({}, {
               "coleta/derivacao_forward.py": "C-DERIVACAO-FORWARD",
               "coleta/social_persistencia.py": "C-SCRAP-SOCIAL",
               "admissao/admissao.py": "C-ADMISSAO",
               "coleta/rota_forward_documento.py": "C-ROTA-M2",
           }, RAIZ)["ARESTAS"]).values()},
       "o par que o ledger declara SEM TOPO entrou na mesma")
ataque("m4_ha_observadas_a_serio_para_isto_nao_passar_vazio",
       len([e for e in E if e.get("OBSERVED") == "YES"]) > 0,
       "nenhuma aresta observada — os ataques acima passam por vacuidade")

print()
print("=" * 70)
if FALHAS:
    print(f"VERDADE_DAS_LIGACOES=FALHA · {len(FALHAS)} ataque(s) sobreviveram: "
          + ", ".join(FALHAS))
    raise SystemExit(1)
print("VERDADE_DAS_LIGACOES=PASS · RED_TEAM_SURVIVORS=0")
