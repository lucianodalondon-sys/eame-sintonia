#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DO SYSTEM MAP

    UM MAPA DE AUDITORIA QUE NAO E AUDITADO NAO VALE NADA.

O validador (`validate_system_map.py`) prova que o mapa CORRESPONDE ao repo.
Este ficheiro prova outra coisa: que as REGRAS do mapa continuam a ser as que
foram escritas — que ele nao pinta verde sem evidencia, nao inventa aresta e
nao converte NAO SEI em certeza.

A diferenca importa. O validador reprova um mapa velho; estes testes reprovam
um mapa cujas regras alguem afrouxou. Um gerador que passasse a dar verde a
tudo continuaria a passar no validador — e falha aqui.

Corre como os outros testes desta casa:  py system-map/tests/test_system_map.py
"""

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))

import generate_system_map as GEN  # noqa: E402

DADOS = RAIZ / "system-map" / "data"
S = json.loads((DADOS / "state.generated.json").read_text(encoding="utf-8"))
G = json.loads((DADOS / "architecture.generated.json").read_text(encoding="utf-8"))
D = json.loads((DADOS / "architecture.declared.json").read_text(encoding="utf-8"))

falhas: list[str] = []


def prova(nome: str, ok: bool, detalhe: str = ""):
    print(f"  {'PASS' if ok else 'FAIL'}  {nome}" + (f"\n        {detalhe}" if not ok and detalhe else ""))
    if not ok:
        falhas.append(nome)


# ── identidade ───────────────────────────────────────────────────────────────
ids = [n["id"] for n in S["NODES"]]
prova("ids_unicos", len(ids) == len(set(ids)))
prova("todo_no_tem_frase_de_gente",
      all(n["what"].strip() and n["why_here"].strip() for n in S["NODES"]),
      "peca sem 'o que faz' ou 'por que esta aqui' e peca que ninguem entende")
prova("todo_no_tem_motivo_de_status",
      all(n["status_reason"].strip() for n in S["NODES"]))

# ── arestas ──────────────────────────────────────────────────────────────────
conhecidos = set(ids)
prova("nenhuma_aresta_solta",
      all(e["from"] in conhecidos and e["to"] in conhecidos for e in S["EDGES"]))
prova("nenhuma_aresta_tecnica_sem_prova",
      all(e["evidence"] for e in S["EDGES"] if e.get("kind") == "technical"),
      "aresta tecnica sem linha de codigo e aresta inventada")
prova("toda_prova_aponta_para_ficheiro_real",
      all(ev["file"] in {f["path"] for f in G["FILES"]}
          for e in S["EDGES"] for ev in e.get("evidence", [])))
prova("aresta_declarada_e_nao_provada_fica_cinza",
      all(e["status"] == "UNKNOWN" for e in S["EDGES"] if e.get("kind") == "expected"))

# ── status ───────────────────────────────────────────────────────────────────
VALIDOS = {"PROVEN", "PENDING", "BROKEN", "UNKNOWN"}
prova("status_do_vocabulario_fechado", all(n["status"] in VALIDOS for n in S["NODES"]))
prova("verde_nunca_e_so_existir",
      all(n["inbound"] or n["outbound"] for n in S["NODES"] if n["status"] == "PROVEN"),
      "peca verde sem nenhuma ligacao provada e verde por existir")
prova("vermelho_e_so_ausencia",
      all(n["file_count"] == 0 for n in S["NODES"] if n["status"] == "BROKEN"))
prova("cinza_nao_tem_ligacao",
      all(not n["inbound"] and not n["outbound"]
          for n in S["NODES"] if n["status"] == "UNKNOWN"))

# O NAO SEI tem de ser alcancavel. Um mapa onde tudo e verde nao esta saudavel:
# esta a esconder. Nao exijo que EXISTA cinza hoje — exijo que a REGRA que o
# produz continue viva, e isso testa-se chamando a regra.
passou, frase = GEN.prova_do_tipo("engine", [], [], False)
prova("regra_produz_nao_verde_sem_evidencia", not passou, frase)
passou_t, _ = GEN.prova_do_tipo("test", [], [], False)
prova("teste_sem_alvo_nao_e_verde", not passou_t)
passou_g, _ = GEN.prova_do_tipo("gate", [], [], False)
prova("portao_que_ninguem_chama_nao_e_verde", not passou_g)

# ── ficheiros ────────────────────────────────────────────────────────────────
existentes = {f["path"] for f in G["FILES"]}
prova("todo_ficheiro_declarado_existe",
      all(f in existentes for n in S["NODES"] for f in n["files"]))
prova("todo_codigo_tem_dono", not S["UNCLAIMED_CODE_FILES"],
      f"{len(S['UNCLAIMED_CODE_FILES'])} ficheiro(s) de codigo sem peca no mapa")
prova("nenhum_ficheiro_com_dois_donos", not S["OWNERSHIP_CONFLICTS"])

# ── negocio nao se mistura com tecnica ───────────────────────────────────────
prova("negocio_separado_da_tecnica",
      all(e["to"].startswith("DEPT:") for e in S["BUSINESS_EDGES"])
      and not any(e["to"].startswith("DEPT:") for e in S["EDGES"]),
      "'A importa B' e 'A serve o Comercial' sao factos diferentes e vivem em listas diferentes")
prova("departamento_declarado_tem_fonte",
      all(e.get("source") and e.get("declared_by") and e.get("reason")
          for e in S["BUSINESS_EDGES"]),
      "departamento sem fonte declarada e departamento inferido")

# ── determinismo ─────────────────────────────────────────────────────────────
# Mesma arvore + mesmo HEAD tem de dar byte a byte o mesmo ficheiro. Se falhar,
# o CI acusaria drift a cada corrida e a lei perderia os dentes numa semana.
antes = (DADOS / "architecture.generated.json").read_text(encoding="utf-8")
subprocess.run([sys.executable, str(RAIZ / "system-map" / "scripts" / "scan_repo.py")],
               capture_output=True)
prova("scanner_e_deterministico",
      antes == (DADOS / "architecture.generated.json").read_text(encoding="utf-8"),
      "correr duas vezes deu resultado diferente")

# A proveniencia (HEAD, BRANCH, data) tem de viver FORA da arquitetura. Se
# alguem a voltar a misturar, o CI passa a reprovar toda a gente em todo o
# commit — e a lei morre por excesso de dentes, nao por falta.
prova("proveniencia_separada_da_arquitetura",
      "PROVENANCE" in S and "HEAD" not in S and "BRANCH" not in S,
      "HEAD/BRANCH no corpo do estado fariam o portao reprovar sempre")

# ── a lei existe e aponta para o validador ───────────────────────────────────
agents = RAIZ / "AGENTS.md"
prova("AGENTS_md_existe", agents.exists())
if agents.exists():
    lei = agents.read_text(encoding="utf-8")
    prova("AGENTS_md_manda_correr_o_validador",
          "validate_system_map.py" in lei,
          "a lei tem de dizer o comando, nao so pedir bom senso")
    prova("AGENTS_md_diz_que_o_mapa_e_derivado",
          "derivado" in lei.lower())
claude = RAIZ / "CLAUDE.md"
prova("CLAUDE_md_aponta_para_AGENTS_md",
      claude.exists() and "AGENTS.md" in claude.read_text(encoding="utf-8"))
readme = RAIZ / "README.md"
prova("README_aponta_agentes_para_AGENTS_md",
      readme.exists() and "AGENTS.md" in readme.read_text(encoding="utf-8"))

# ── a app so renderiza ───────────────────────────────────────────────────────
js = (RAIZ / "system-map" / "app" / "map.js").read_text(encoding="utf-8")
prova("a_tela_le_o_estado_de_um_ficheiro", "state.generated.json" in js)
prova("a_tela_usa_tokens_do_design_system",
      "--st-proven" in (RAIZ / "system-map" / "app" / "map.css").read_text(encoding="utf-8"))
html = (RAIZ / "system-map" / "app" / "index.html").read_text(encoding="utf-8")
prova("a_pagina_carrega_o_design_system_oficial", "_ds/adama-brandwell" in html)
prova("a_pagina_sobrevive_sem_javascript", "<noscript>" in html and "semjs" in html)

print()
if falhas:
    print(f"TESTES_SYSTEM_MAP=FAIL · {len(falhas)} reprovada(s): {', '.join(falhas)}")
    raise SystemExit(1)
print("TESTES_SYSTEM_MAP=PASS")
