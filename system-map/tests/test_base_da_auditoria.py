#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SYSTEM_MAP_AUDIT_BASE_GUARD — a arvore auditada contem a Collection actual?

    python3 system-map/tests/test_base_da_auditoria.py

POR QUE ISTO EXISTE, E CUSTOU UMA NOITE
----------------------------------------
Uma missao inteira auditou a Collection card a card, com validador a passar,
22 guardas verdes e red team a zero — sobre uma arvore de tres dias antes. O
censo estava CORRECTO. O sistema e que era outro.

    NADA FALHOU. E POR ISSO NINGUEM DEU POR NADA.

Todas as guardas do mapa perguntam «o mapa corresponde a ESTA arvore?». Nenhuma
perguntava «ESTA arvore e o sistema?». Esta pergunta essa.

    MAP CURRENT != SYSTEM CURRENT.
    O MAPA TEM DE IR ATE AO SISTEMA; O SISTEMA NAO VOLTA NO TEMPO.

O QUE ELA FAZ
-------------
Le `system-map/COLLECTION-AUDIT-BASE.json`, resolve a REFERENCIA declarada (e
nao um SHA cravado — um ficheiro que se edita todos os dias deixa de ser lei) e
pergunta ao git se a arvore auditada a contem.

O QUE ELA RECUSA FAZER
----------------------
Passar por nao ter medido. Se a referencia nao resolve — remoto ausente, clone
raso, ref apagada — a resposta e `CANNOT_MEASURE`, e `CANNOT_MEASURE` REPROVA.

    UMA GUARDA QUE PASSA POR NAO CONSEGUIR MEDIR
    E PIOR DO QUE GUARDA NENHUMA: ELA DA SOSSEGO SEM DAR PROVA.

Foi exactamente esse o defeito de `T18_nenhum_pais_fora_da_italia_foi_alterado`
noutra linha: `git diff` respondia «no merge base», a lista saia vazia, e a
prova reprovava sem conseguir dizer que nao tinha medido. Aqui o motivo e
explicito e tem nome proprio.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CONTRATO = RAIZ / "system-map" / "COLLECTION-AUDIT-BASE.json"

FALHAS = []


def prova(nome, ok, porque=""):
    print(("  PASS  " if ok else "  FAIL  ") + nome
          + (("\n        " + porque) if not ok and porque else ""))
    if not ok:
        FALHAS.append(nome)


def git(*args):
    r = subprocess.run(["git", "-C", str(RAIZ), *args],
                       capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def resolver(ref: str):
    """O HEAD da referencia declarada, medido AGORA — local ou remoto.

    Procura-se em varias formas porque o mesmo ramo chama-se de tres maneiras
    conforme quem clonou: `X`, `origin/X`, `refs/remotes/origin/X`. Nao achar
    em nenhuma nao e «nao existe»: e NAO CONSEGUI MEDIR.
    """
    for forma in (f"refs/remotes/origin/{ref}", f"origin/{ref}",
                  f"refs/heads/{ref}", ref):
        rc, out, _ = git("rev-parse", "--verify", "--quiet", forma + "^{commit}")
        if rc == 0 and out:
            return out, forma
    return None, None


print("=" * 70)
print("SYSTEM_MAP_AUDIT_BASE_GUARD — a arvore auditada e o sistema actual?")
print("=" * 70)

prova("o_contrato_da_base_existe", CONTRATO.is_file(),
      "sem contrato nao ha base declarada, e sem base declarada qualquer "
      "arvore serve — que e o defeito que esta guarda veio fechar")
if not CONTRATO.is_file():
    raise SystemExit(1)

C = json.loads(CONTRATO.read_text(encoding="utf-8"))
REF = C.get("COLLECTION_FUNCTIONAL_REF")
prova("o_contrato_nomeia_uma_referencia", bool(REF), f"REF={REF!r}")

esperado, forma = resolver(REF) if REF else (None, None)
rc_head, HEAD, _ = git("rev-parse", "HEAD")

# ── 1 · A REFERENCIA RESOLVE? ──────────────────────────────────────────────
prova("a_referencia_declarada_resolve", bool(esperado),
      f"CANNOT_MEASURE: `{REF}` nao existe como ref local nem remota nesta "
      f"copia. Isto NAO e «a base esta certa»: e nao ter medido, e nao medir "
      f"reprova.")

# ── 2 · A ARVORE AUDITADA CONTEM A LINHA FUNCIONAL? ────────────────────────
if esperado:
    rc, _, _ = git("merge-base", "--is-ancestor", esperado, "HEAD")
    contem = rc == 0
    prova("AUDIT_TREE_CONTAINS_COLLECTION_CURRENT_HEAD", contem,
          f"FAIL HIGH · a arvore auditada NAO contem a linha funcional.\n"
          f"        esperado (de {forma}): {esperado}\n"
          f"        HEAD auditado:         {HEAD}\n"
          f"        Auditar aqui produz um censo correcto de um sistema que "
          f"nao e este. Rebase a auditoria sobre `{REF}` antes de medir "
          f"um unico cartao.")

    # ── 3 · E A LINHA FUNCIONAL TEM MESMO O QUE DIZ TER ────────────────────
    # Conter o commit nao chega: um `git revert` mantem a ancestralidade e
    # tira o codigo. Confere-se que as pecas nomeadas estao no disco.
    #     ANCESTRY != CONTEUDO.
    marcos = [m for m in C.get("MARCOS_OBRIGATORIOS", []) if m]
    if marcos:
        faltam = [m for m in marcos if not (RAIZ / m).exists()]
        prova("os_marcos_declarados_estao_na_arvore", not faltam,
              f"a ancestralidade contem a linha e estes ficheiros nao estao no "
              f"disco: {faltam[:6]}. ANCESTRY != CONTEUDO.")

    # ── 3b · O OBSERVADOR NAO ALTEROU O OBJECTO OBSERVADO ─────────────────
    # Nao ha baseline guardado: compara-se a arvore auditada com a PROPRIA
    # linha funcional declarada. Se trazer o mapa mexeu numa gaveta da
    # Collection, aparece aqui — e o contrato diz quais gavetas contam.
    #
    #     O OBSERVADOR NAO PODE ALTERAR O OBJECTO OBSERVADO.
    gavetas = [g for g in C.get("GAVETAS_FUNCIONAIS", []) if g]
    fora = set(C.get("FORA_DA_GUARDA", []))
    if gavetas:
        rc, saida, err = git("diff", "--name-only", esperado, "HEAD", "--", *gavetas)
        mexidos = [f for f in saida.split() if f and f not in fora]
        prova("FUNCTIONAL_COLLECTION_DIFF_FROM_BASE_e_zero",
              rc == 0 and not mexidos,
              (f"a integracao do observador mexeu em codigo funcional: "
               f"{mexidos[:8]}" if rc == 0 else
               f"CANNOT_MEASURE: o git nao comparou ({err[:90]})"))

# ── 4 · O CONTRATO NAO PODE VIRAR UM SHA CRAVADO ───────────────────────────
# Se alguem trocar a REF por um SHA, a guarda deixa de acompanhar a linha e
# passa a defender um ponto morto. Nomear um ramo e nomear algo que anda.
parece_sha = bool(REF) and len(REF) >= 7 and all(
    ch in "0123456789abcdef" for ch in REF.lower())
prova("a_base_e_uma_referencia_viva_e_nao_um_SHA", not parece_sha,
      f"`{REF}` parece um SHA. Um SHA cravado obriga a editar o contrato a "
      f"cada commit da Collection, e um ficheiro que se edita todos os dias "
      f"deixa de ser lei em duas semanas.")

print()
if FALHAS:
    print(f"AUDIT_BASE_GUARD=FAIL · {len(FALHAS)} reprovada(s): "
          + ", ".join(FALHAS))
    raise SystemExit(1)
print("AUDIT_BASE_GUARD=PASS · a arvore auditada contem a Collection actual")
