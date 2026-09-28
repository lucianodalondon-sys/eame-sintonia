#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A CORRIDA SOBRE A COPIA — o motor canonico sobre uma copia so-leitura da Sala, com os precos.

    MISSAO   PRECO-NO-MOTOR (Diretoria 28/09). Substitui, para o preco, a montagem fora do Git
             (`PARA-O-CASCO-R9/montar_r9.py`): o objeto de mercado nasce em `correr()`, nao aqui.
    ESPECIE  EXECUTOR DA CORRIDA (Z-MOTOR). Le FICHEIROS. NAO abre banco, rede nem coletor.

    python motor/corrida_sobre_a_copia.py --copia <RUN>/copia --saida <pasta> --armazem <armazem>

A COPIA e a do modelo so-leitura (uma transacao REPEATABLE READ READ ONLY):
    SALA_ATUAL.json   `sala_de_espera_atual` + raw_asset (sha256, document_key, source_url, storage_path)
    PRECOS.json       `sala_de_espera_precos` (migration 038), NO MESMO snapshot
    PROVA_RO.txt / PROVA_RO_FIM.txt   `show transaction_read_only` = on, no inicio e no fim

O que este ficheiro faz, e so isto:
    1. confere que a copia e prova so-leitura e que a arvore do motor esta limpa (a corrida carimba o HEAD);
    2. traduz cada linha da Sala para o contrato READY pela TABELA DO DONO (`COLUNA_E_CAMPO` de
       `admissao/sala_de_espera.py`, lida por AST — este ficheiro nao importa o leitor da Sala);
    3. chama `corrida_da_inteligencia.correr` com TODOS os READY do corte (sem pre-filtro, G0/v4), as
       linhas de preco e o armazem;
    4. grava o livro, a entrada do pote e o pote (gerador do dono, `pacote/pote_intelligence_casco.py`).
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _g in ("", "motor", "leis", "provas", "pacote"):
    if str(RAIZ / _g) not in sys.path:
        sys.path.insert(0, str(RAIZ / _g))

import corrida_da_inteligencia as CI            # noqa: E402
import porta_da_referencia as PORTA             # noqa: E402

NAO_SEI = CI.NAO_SEI
PERGUNTA = "PRECO-NO-MOTOR: o que a Sala entrega a Intelligence, com o preco do mesmo item"
#: raw_asset -> o item (so COPIA; nada e calculado). Nomes fora do contrato READY, lidos pelo preco e
#: pelo grafo de dependencia (RAW_SHA256 e um dos CAMPOS_DE_SHA do dono do grafo).
DO_RAW = (("raw_sha256", "RAW_SHA256"), ("raw_storage_path", "RAW_STORAGE_PATH"),
          ("raw_document_key", "RAW_DOCUMENT_KEY"), ("raw_source_url", "RAW_SOURCE_URL"))


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tabela_do_dono() -> tuple:
    """`COLUNA_E_CAMPO` + `COLUNA_E_CAMPO_JSON` de admissao/sala_de_espera.py, por AST (sem importar)."""
    arv = ast.parse((RAIZ / "admissao" / "sala_de_espera.py").read_text(encoding="utf-8"))
    achado = {}
    for n in arv.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) \
                and n.targets[0].id in ("COLUNA_E_CAMPO", "COLUNA_E_CAMPO_JSON"):
            achado[n.targets[0].id] = ast.literal_eval(n.value)
    if set(achado) != {"COLUNA_E_CAMPO", "COLUNA_E_CAMPO_JSON"}:
        raise SystemExit("RECUSADO: a tabela do dono da Sala nao foi encontrada por AST")
    return achado["COLUNA_E_CAMPO"] + achado["COLUNA_E_CAMPO_JSON"]


def ready(linha: dict, tabela) -> dict:
    u = {"ESTADO": "PRONTO_PARA_INTELIGENCIA", "CORRIDA": linha["run_id"], "ORDEM": linha["ordem"],
         "RAW_OBSERVATION_ID": NAO_SEI if linha.get("raw_observation_id") is None else linha["raw_observation_id"]}
    for coluna, campo in tabela:
        u[campo] = linha.get(coluna)
    for coluna, campo in DO_RAW:
        v = linha.get(coluna)
        u[campo] = NAO_SEI if v in (None, "") else v
    return u


def git(*a) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *a], capture_output=True, text=True).stdout.strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--copia", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--armazem", required=True)
    ap.add_argument("--sem-precos", action="store_true", help="contraprova: a mesma corrida sem a vista")
    a = ap.parse_args(argv)
    copia, saida = Path(a.copia), Path(a.saida)
    ro = (copia / "PROVA_RO.txt").read_text(encoding="utf-8").split()
    ro_fim = (copia / "PROVA_RO_FIM.txt").read_text(encoding="utf-8").split()
    if not ro or ro[0] != "on" or not ro_fim or ro_fim[0] != "on":
        raise SystemExit("RECUSADO: a copia nao prova transaction_read_only = on no inicio e no fim")
    head = git("rev-parse", "HEAD")
    sujo = git("status", "--porcelain", "--", "motor", "leis", "pacote", "admissao/sala_de_espera.py")
    if sujo:
        raise SystemExit("RECUSADO: a arvore do motor tem alteracoes nao commitadas:\n" + sujo)

    tabela = tabela_do_dono()
    linhas = json.loads((copia / "SALA_ATUAL.json").read_text(encoding="utf-8"))
    precos = None if a.sem_precos else json.loads((copia / "PRECOS.json").read_text(encoding="utf-8"))
    corte = [r for r in linhas if r.get("estado_da_fila") == "WAITING"]
    itens = [ready(r, tabela) for r in corte]
    universo = {"CORTE_SALA_ATUAL_SHA256": _sha(copia / "SALA_ATUAL.json"), "ITENS_NO_CORTE": len(itens),
                "ESTADO_DA_FILA": "WAITING", "READY_NO_CORTE_TOTAL": len(linhas)}
    if precos is not None:
        universo["PRECOS_SHA256"] = _sha(copia / "PRECOS.json")
        universo["PRECOS_NO_CORTE"] = len(precos)
    ref = PORTA.abrir()
    livro = CI.correr(PERGUNTA, itens, universo=universo, precos=precos, armazem=a.armazem, referencia=ref)
    saida.mkdir(parents=True, exist_ok=True)
    p_livro = saida / ("LIVRO-%s.json" % livro["INTELLIGENCE_RUN_ID"])
    p_livro.write_text(json.dumps(livro, ensure_ascii=False, indent=1, default=str), encoding="utf-8")

    entrada = {k: v for k, v in livro.items() if k != "SIGNALS"}
    entrada.update({
        "SOURCE_HEAD": {"MOTOR": head, "RAMO": git("rev-parse", "--abbrev-ref", "HEAD"),
                        "EXECUTOR": "motor/corrida_sobre_a_copia.py", "POTE": head},
        "CORTE": {"COPIA_DA_SALA_EM": " ".join(ro[1:3]) if len(ro) > 2 else NAO_SEI,
                  "TRANSACTION_READ_ONLY": ro[0] + "/" + ro_fim[0], "SNAPSHOT": ro[3] if len(ro) > 3 else NAO_SEI,
                  "SALA_ATUAL_SHA256": universo["CORTE_SALA_ATUAL_SHA256"],
                  "PRECOS_SHA256": universo.get("PRECOS_SHA256", NAO_SEI), "READY": len(linhas)},
        "GAPS": [], "SINTETICA": False, "EXPERIMENTAL": "NAO_PARA_CLIENTE",
    })
    entrada.setdefault("ITENS_POR_FERRAMENTA", {})
    p_ent = saida / "ENTRADA-DO-POTE.json"
    p_ent.write_text(json.dumps(entrada, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    p_pote = saida / "POTE-EXPERIMENTAL.json"
    r = subprocess.run([sys.executable, str(RAIZ / "pacote" / "pote_intelligence_casco.py"), str(p_ent), str(p_pote)],
                       cwd=str(RAIZ), capture_output=True, text=True, encoding="utf-8",
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    resumo = {"INTELLIGENCE_RUN_ID": livro["INTELLIGENCE_RUN_ID"], "RESULT_STATE": livro["RESULT_STATE"],
              "ERRORS": livro["ERRORS"], "MOTOR_HEAD": head, "ITENS": len(itens), "SINAIS": len(livro["SIGNALS"]),
              "PRECOS": {k: v for k, v in (livro.get("PRECOS") or {}).items() if k not in ("RECUSADOS",)},
              "PRECOS_RECUSADOS": (livro.get("PRECOS") or {}).get("RECUSADOS", NAO_SEI),
              "OBJETOS_DE_MERCADO": [(o["OBJETO_ID"], o["PROVA"][0]["ITEM_ID"], o["CHAVES"]["PRICE"],
                                      o["CHAVES"]["UNIT"]) for o in livro.get("OBJETOS_DE_MERCADO", [])],
              "POTE": {"RC": r.returncode, "STDOUT": r.stdout.strip()[-400:], "STDERR": r.stderr.strip()[-1500:]},
              "LIVRO": p_livro.name, "LIVRO_SHA256": _sha(p_livro),
              "ENTRADA_SHA256": _sha(p_ent), "POTE_SHA256": _sha(p_pote) if p_pote.exists() else NAO_SEI}
    (saida / "RESUMO.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=1, default=str))
    return 0 if livro["RESULT_STATE"] == "DONE" and r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
