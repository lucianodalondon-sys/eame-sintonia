#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DOS QUATRO PLANOS E DA LIGACAO DA EVIDENCIA — G1.

    python3 system-map/tests/test_quatro_planos.py

O mapa media bem e publicava a palavra errada: 659 arestas diziam `PROVEN`
apoiadas so em analise estatica, e 52 tinham a evidencia ligada a afirmacao
errada. O G1 fecha as duas, porque sao a mesma correcao vista de dois lados.

    ANALISE ESTATICA PROVA CAN DO. SO TELEMETRIA PROVA DID DO.

    DECLARED → CODE → OBSERVED → PROVEN — nenhuma seta e automatica.

O QUE ESTE FICHEIRO CONFERE
---------------------------
    PLANOS       os quatro existem, em toda aresta e toda peca
    SEM PROMOCAO nenhuma evidencia estatica produz OBSERVED
    LIGACAO      toda evidencia diz que afirmacao sustenta
    NO != UNKNOWN  falta de prova nunca vira prova de ausencia
    LEGADO       `status` deriva dos planos e nao os contradiz
    SENTINELA    o caso APIFY, fixado como caso de teste
    MORDIDA      cada regra, corrida contra um defeito fabricado
"""

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SCRIPTS = RAIZ / "system-map" / "scripts"
ESTADO = RAIZ / "system-map" / "data" / "state.generated.json"
REVISAO = RAIZ / "data" / "derivados" / "SYSTEM-MAP-EVIDENCE-BINDING-REVIEW-V1.json"

sys.path.insert(0, str(SCRIPTS))
import generate_system_map as GER                 # noqa: E402

FALHAS = []
PLANOS = ("DECLARED", "CODE", "OBSERVED", "PROVEN")
VALORES = {"YES", "NO", "UNKNOWN"}


def prova(nome, ok, porque=""):
    print(("  PASS  " if ok else "  FAIL  ") + nome
          + (("\n        " + porque) if not ok and porque else ""))
    if not ok:
        FALHAS.append(nome)


print("AS PROVAS DOS QUATRO PLANOS — G1")
print("=" * 70)

S = json.loads(ESTADO.read_text(encoding="utf-8"))
E, N = S["EDGES"], S["NODES"]
prova("o_estado_existe_e_tem_arestas", bool(E) and bool(N))

# ── 1 · OS QUATRO PLANOS EXISTEM, E SO TEM TRES VALORES ─────────────────────
for nome, col in (("aresta", E), ("peca", N)):
    faltam = [x for x in col if any(p not in x for p in PLANOS)]
    prova(f"toda_{nome}_publica_os_quatro_planos", not faltam,
          f"{len(faltam)} sem os quatro: {[x.get('id') or x.get('from') for x in faltam[:4]]}")
    maus = [x for x in col for p in PLANOS if x.get(p) not in VALORES]
    prova(f"todo_plano_de_{nome}_tem_valor_conhecido", not maus,
          f"{len(maus)} valores fora de {sorted(VALORES)}")

# UM QUINTO PLANO SERIA O COLAPSO OUTRA VEZ, COM OUTRO NOME.
prova("nao_nasceu_um_quinto_plano",
      all(set(PLANOS) <= set(e) for e in E)
      and not any(k.endswith("_PLANE") and k != "PROVEN_PLANE" for e in E for k in e),
      "apareceu um campo de plano que nao e PROVEN_PLANE")

# ── 2 · SEM PROMOCAO AUTOMATICA ─────────────────────────────────────────────
# Nenhuma evidencia estatica pode produzir OBSERVED. Se alguma aresta disser
# OBSERVED=YES, ela tem de trazer RUN_ID — senao alguem promoveu CODE.
obs_sem_corrida = [f"{e['from']}->{e['to']}" for e in E
                   if e["OBSERVED"] == "YES"
                   and not any(ev.get("RUN_ID") for ev in e.get("evidence", []))]
prova("nenhuma_aresta_diz_OBSERVED_sem_corrida", not obs_sem_corrida,
      f"{obs_sem_corrida[:5]}")

nos_obs = [n for n in N if n["OBSERVED"] == "YES"]
prova("toda_peca_OBSERVED_traz_a_prova_da_corrida",
      all(n.get("OBSERVED_EVIDENCE") for n in nos_obs),
      "uma peca disse OBSERVED sem evidencia de corrida")
prova("ha_pelo_menos_uma_peca_OBSERVED_para_esta_prova_nao_ser_vazia",
      bool(nos_obs), "nenhuma peca observada — as provas acima passam por vacuidade")

# PROVEN nunca sem plano, e nunca num plano que nao esta YES.
sem_plano = [f"{e['from']}->{e['to']}" for e in E
             if e["PROVEN"] == "YES" and not e.get("PROVEN_PLANE")]
prova("PROVEN_declara_sempre_o_plano", not sem_plano, f"{sem_plano[:5]}")
plano_falso = [f"{e['from']}->{e['to']}" for e in E
               if e.get("PROVEN_PLANE") and e.get(e["PROVEN_PLANE"]) != "YES"]
prova("o_plano_provado_esta_mesmo_em_YES", not plano_falso, f"{plano_falso[:5]}")

# ── 3 · TODA EVIDENCIA DIZ QUE AFIRMACAO SUSTENTA ──────────────────────────
sem_campo = [(e["from"], e["to"]) for e in E for ev in e.get("evidence", [])
             if "SUPPORTS" not in ev or "WHY" not in ev]
prova("toda_evidencia_diz_se_sustenta_a_afirmacao", not sem_campo,
      f"{len(sem_campo)} evidencias sem SUPPORTS/WHY")

sem_limite = [(e["from"], e["to"]) for e in E for ev in e.get("evidence", [])
              if not (ev.get("LIMITATIONS") or "").strip()]
prova("toda_evidencia_declara_o_seu_limite", not sem_limite,
      f"{len(sem_limite)} evidencias sem LIMITATIONS")

# A afirmacao apontada tem de ser A DESTA ARESTA, e nao a de outra.
# AS REGRAS SAO FUNCOES, E NAO CONDICOES DENTRO DA ASERCAO. Uma regra escrita a
# direito no `prova(...)` so sabe dizer SIM aos dados reais: afrouxa-la nao
# contradiz nada, porque nesta arvore nada a viola.
#
#     UMA GUARDA QUE NUNCA VIU UM DEFEITO NAO E UMA GUARDA: E UMA FRASE.
def afirmacao_e_da_aresta(ev, e):
    a = ev.get("ASSERTION_SUPPORTED")
    return not a or (a.get("FROM") == e["from"] and a.get("TO") == e["to"]
                     and a.get("RELATION_TYPE") == e["type"])


def code_tem_apoio(e):
    return e.get("CODE") != "YES" or any(
        ev.get("SUPPORTS") == "YES" for ev in e.get("evidence", []))


trocada = [f"{e['from']}->{e['to']}" for e in E for ev in e.get("evidence", [])
           if not afirmacao_e_da_aresta(ev, e)]
prova("a_afirmacao_apontada_e_a_desta_aresta", not trocada, f"{trocada[:5]}")

# E CODE=YES exige que ALGUMA evidencia a sustente. Sem isso, o plano subiu
# por existir linha — que e exactamente o defeito que o G1 veio fechar.
code_sem_apoio = [f"{e['from']}->{e['to']} ({e['type']})" for e in E
                  if not code_tem_apoio(e)]
prova("CODE_YES_exige_evidencia_que_sustente_a_afirmacao", not code_sem_apoio,
      f"{code_sem_apoio[:5]}")

# ── 4 · ROTULO NARRATIVO NAO GANHA CODE POR PROXIMIDADE ────────────────────
narrativas_verdes = [f"{e['from']}->{e['to']} ({e['type']})" for e in E
                     if e.get("raw_type") is None and e["CODE"] == "YES"]
prova("rotulo_narrativo_nunca_recebe_CODE_YES", not narrativas_verdes,
      f"{narrativas_verdes[:5]} — uma linha ao lado nao prova a relacao")

# ── 5 · NO NAO E UNKNOWN ───────────────────────────────────────────────────
# `NO` so com prova de ausencia. Hoje nao ha medidor que a produza, entao
# nenhum plano pode dizer NO — e se um disser, foi UNKNOWN disfarcado.
nos_indevidos = [(e["from"], e["to"], p) for e in E for p in PLANOS
                 if e[p] == "NO"]
prova("nenhum_plano_diz_NO_sem_medidor_de_ausencia", not nos_indevidos,
      f"{nos_indevidos[:5]} — falta de prova e UNKNOWN, nao NO")

# ── 6 · O LEGADO DERIVA, E NAO CONTRADIZ ───────────────────────────────────
contra = [f"{e['from']}->{e['to']}" for e in E
          if (e["status"] == "PROVEN") != (e["PROVEN"] == "YES")]
prova("o_status_legado_nao_contradiz_os_planos", not contra, f"{contra[:5]}")
prova("o_status_legado_diz_que_e_derivado",
      all("DEPRECATED" in (e.get("STATUS_LEGACY_NOTA") or "") for e in E))
# E a aresta declarada e nao provada continua NAO SEI, como a P7 exige.
exp = [f"{e['from']}->{e['to']}" for e in E
       if e.get("kind") == "expected" and e["status"] != "UNKNOWN"]
prova("aresta_declarada_e_nao_provada_continua_NAO_SEI", not exp, f"{exp}")

# ── 7 · A SENTINELA APIFY, FIXADA ──────────────────────────────────────────
# O caso que deu nome ao defeito. Ele nao pode voltar sem reprovar aqui.
def aresta(de, para, tipo):
    return next((e for e in E if e["from"] == de and e["to"] == para
                 and e["type"] == tipo), None)


imp = aresta("C-APIFY-POOL", "C-COLETA-PUBLICA", "IMPORTS")
prova("sentinela_o_import_existe", imp is not None)
if imp:
    prova("sentinela_o_import_tem_CODE_YES", imp["CODE"] == "YES", f"{imp['CODE']}")
    prova("sentinela_o_import_esta_provado_no_plano_CODE",
          imp["PROVEN"] == "YES" and imp["PROVEN_PLANE"] == "CODE")
    prova("sentinela_o_import_nao_diz_OBSERVED", imp["OBSERVED"] == "UNKNOWN")

canais = [aresta("C-APIFY-POOL", v, "ABRE_O_CANAL")
          for v in ("V-FACEBOOK", "V-INSTAGRAM", "V-LINKEDIN")]
prova("sentinela_as_tres_aberturas_de_canal_existem", all(canais))
for c in [c for c in canais if c]:
    prova(f"sentinela_{c['to']}_nao_usa_o_import_como_prova_de_CODE",
          c["CODE"] == "UNKNOWN",
          f"CODE={c['CODE']} — o import prova IMPORTS, nao abertura de canal")
    prova(f"sentinela_{c['to']}_nao_foi_dada_por_provada",
          c["PROVEN"] == "UNKNOWN" and not c["PROVEN_PLANE"])
# E a linha que os tres partilhavam continua a ser a mesma — senao a sentinela
# passaria por a evidencia ter mudado de sitio, e nao por a regra morder.
if imp and canais[0]:
    partilhada = {(v["file"], v["line"]) for v in imp.get("evidence", [])} & {
        (v["file"], v["line"]) for v in canais[0].get("evidence", [])}
    prova("sentinela_a_linha_partilhada_continua_a_ser_a_mesma",
          ("coleta/comunicacao_coleta.py", 57) in partilhada,
          f"{sorted(partilhada)}")

# ── 8 · A REVISAO ARESTA A ARESTA ──────────────────────────────────────────
prova("a_revisao_existe", REVISAO.exists(),
      "corra: py system-map/scripts/revisao_da_evidencia.py")
if REVISAO.exists():
    R = json.loads(REVISAO.read_text(encoding="utf-8"))
    r = R["RESUMO"]
    prova("nenhuma_decisao_da_revisao_sem_porque", not r["SEM_PORQUE"],
          f"{r['SEM_PORQUE'][:5]}")
    # ⚠️ COMPARAR A REVISAO CONSIGO PROPRIA NAO MEDE COBERTURA. A primeira
    # versao exigia `ARESTAS_REVISTAS == len(ARESTAS)` — e as duas encolhem
    # juntas quando alguem deixa uma aresta de fora. A mutacao apanhou-me nisso.
    #
    #     UM TOTAL QUE VEM DA MESMA LISTA QUE ELE CONTA NUNCA ACUSA UMA FALTA.
    #
    # A conta certa vem do ESTADO: que arestas partilham linha de evidencia.
    from collections import defaultdict as _dd
    _onde = _dd(list)
    for _i, _e in enumerate(E):
        for _ev in _e.get("evidence", []):
            _onde[(_ev.get("file"), _ev.get("line"))].append(_i)
    ESPERADAS = {f'{E[i]["from"]}--{E[i]["type"]}-->{E[i]["to"]}'
                 for v in _onde.values() if len(v) > 1 for i in v}
    revistas = {x["EDGE_ID"] for x in R["ARESTAS"]}
    prova("ha_arestas_com_linha_partilhada_para_esta_prova_nao_ser_vazia",
          bool(ESPERADAS), "nenhuma linha partilhada — a prova seguinte nao mede nada")
    prova("a_revisao_cobre_todas_as_arestas_tocadas", revistas == ESPERADAS,
          f"faltam {sorted(ESPERADAS - revistas)[:4]} · "
          f"a mais {sorted(revistas - ESPERADAS)[:4]}")
    prova("a_revisao_conta_o_que_lista",
          r["ARESTAS_REVISTAS"] == len(R["ARESTAS"]),
          f"{r['ARESTAS_REVISTAS']} vs {len(R['ARESTAS'])}")
    prova("a_conta_da_revisao_fecha",
          r["SUPPORTED"] + r["AMBIGUOUS"] + r["UNSUPPORTED"] == r["ARESTAS_REVISTAS"],
          f"{r['SUPPORTED']}+{r['AMBIGUOUS']}+{r['UNSUPPORTED']} != {r['ARESTAS_REVISTAS']}")
    decisoes = {x["DECISION"] for x in R["ARESTAS"]}
    prova("toda_decisao_e_uma_das_tres",
          decisoes <= {"SUPPORTED", "AMBIGUOUS", "UNSUPPORTED"}, f"{decisoes}")
    # o que a revisao diz e o que o estado publica — senao ha dois donos
    porid = {x["EDGE_ID"]: x for x in R["ARESTAS"]}
    divergem = [k for k, x in porid.items()
                for e in [aresta(x["FROM"], x["TO"], x["RELATION_TYPE"])]
                if e and (e["CODE"] != x["CODE_AFTER"]
                          or e["PROVEN"] != x["PROVEN_AFTER"])]
    prova("a_revisao_e_o_estado_dizem_o_mesmo", not divergem, f"{divergem[:5]}")

# ── 9 · AS GUARDAS MORDEM, conferidas com o defeito posto ──────────────────
# Uma regra que nunca viu um defeito e uma frase. Cada uma corre aqui contra
# um caso fabricado, e tem de recusar.
def _ligacoes(*arestas):
    return {(e["from"], e["to"], e["type"]): e for e in arestas}


def _aresta(de, para, tipo, raw, evs):
    return {"from": de, "to": para, "type": tipo, "raw_type": raw,
            "kind": "technical", "evidence": [dict(v) for v in evs]}


LINHA = {"file": "x.py", "line": 1, "snippet": "import y"}
narrativa = _aresta("A", "B", "ABRE_O_CANAL", None, [LINHA])
medida = _aresta("A", "B", "IMPORTS", "IMPORTS", [LINHA])
GER.ligar_evidencia_a_afirmacao(_ligacoes(narrativa, medida))
prova("a_guarda_do_rotulo_narrativo_morde",
      narrativa["evidence"][0]["SUPPORTS"] == "NO"
      and narrativa["evidence"][0]["ASSERTION_SUPPORTED"] is None)
prova("a_guarda_do_rotulo_narrativo_aceita_a_relacao_medida",
      medida["evidence"][0]["SUPPORTS"] == "YES")

leitura = _aresta("A", "B", "READS", "READS", [LINHA])
importa = _aresta("A", "B", "IMPORTS", "IMPORTS", [LINHA])
GER.ligar_evidencia_a_afirmacao(_ligacoes(leitura, importa))
prova("a_guarda_do_import_lido_como_leitura_morde",
      leitura["evidence"][0]["SUPPORTS"] == "AMBIGUOUS")
prova("o_import_da_mesma_linha_continua_sustentado",
      importa["evidence"][0]["SUPPORTS"] == "YES")

so_leitura = _aresta("A", "B", "READS", "READS",
                     [{"file": "d.json", "line": 3, "snippet": "open('d.json')"}])
GER.ligar_evidencia_a_afirmacao(_ligacoes(so_leitura))
prova("uma_leitura_sem_import_ao_lado_continua_sustentada",
      so_leitura["evidence"][0]["SUPPORTS"] == "YES")

# E os planos, corridos sobre esses mesmos casos.
lig = _ligacoes(_aresta("A", "B", "ABRE_O_CANAL", None, [LINHA]),
                _aresta("A", "B", "IMPORTS", "IMPORTS", [LINHA]))
GER.os_quatro_planos(lig, [], RAIZ)
narr = lig[("A", "B", "ABRE_O_CANAL")]
med = lig[("A", "B", "IMPORTS")]
prova("o_plano_do_rotulo_narrativo_fica_UNKNOWN",
      narr["CODE"] == "UNKNOWN" and narr["PROVEN"] == "UNKNOWN"
      and narr["PROVEN_PLANE"] is None)
prova("o_plano_da_relacao_medida_fica_CODE",
      med["CODE"] == "YES" and med["PROVEN_PLANE"] == "CODE")
prova("nem_a_medida_nem_a_narrativa_ganham_OBSERVED",
      narr["OBSERVED"] == "UNKNOWN" and med["OBSERVED"] == "UNKNOWN")
prova("o_status_legado_de_um_caso_fabricado_tambem_deriva",
      med["status"] == "PROVEN" and narr["status"] == "UNKNOWN")

# As duas regras acima, mordidas com o defeito posto.
_boa = {"from": "A", "to": "B", "type": "IMPORTS"}
prova("a_guarda_da_afirmacao_trocada_morde",
      not afirmacao_e_da_aresta(
          {"ASSERTION_SUPPORTED": {"FROM": "A", "TO": "OUTRO", "RELATION_TYPE": "IMPORTS"}},
          _boa))
prova("a_guarda_da_afirmacao_trocada_morde_no_tipo",
      not afirmacao_e_da_aresta(
          {"ASSERTION_SUPPORTED": {"FROM": "A", "TO": "B", "RELATION_TYPE": "READS"}},
          _boa))
prova("a_guarda_da_afirmacao_trocada_aceita_a_certa",
      afirmacao_e_da_aresta(
          {"ASSERTION_SUPPORTED": {"FROM": "A", "TO": "B", "RELATION_TYPE": "IMPORTS"}},
          _boa))
prova("a_guarda_do_CODE_sem_apoio_morde",
      not code_tem_apoio({"CODE": "YES", "evidence": [{"SUPPORTS": "NO"}]}))
prova("a_guarda_do_CODE_sem_apoio_morde_sem_evidencia_nenhuma",
      not code_tem_apoio({"CODE": "YES", "evidence": []}))
prova("a_guarda_do_CODE_sem_apoio_aceita_o_bom",
      code_tem_apoio({"CODE": "YES", "evidence": [{"SUPPORTS": "YES"}]})
      and code_tem_apoio({"CODE": "UNKNOWN", "evidence": []}))

# O ledger de runtime e o unico dono de OBSERVED, e le-se dele.
obs = GER.observado_em_runtime(RAIZ)
prova("o_ledger_de_runtime_e_lido_e_nao_esta_vazio", bool(obs),
      "provas-de-execucao.json nao devolveu nenhum executor provado")
prova("cada_observacao_traz_ambiente_e_modo",
      all("ENVIRONMENT" in v and "EXECUTION_MODE" in v for v in obs.values()))

print()
print("=" * 70)
if FALHAS:
    print(f"QUATRO_PLANOS=FAIL · {len(FALHAS)} prova(s) reprovada(s)")
    for f in FALHAS:
        print("  ·", f)
    raise SystemExit(1)
print("QUATRO_PLANOS=PASS · cada afirmacao no seu plano, cada prova na sua afirmacao")
