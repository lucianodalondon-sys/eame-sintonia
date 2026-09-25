#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DA PONTE DO CURATOR — cada lei desligada a mao, uma de cada vez.

    UM TESTE QUE NAO MORRE QUANDO A LEI DESAPARECE NAO ESTA A GUARDAR NADA.

Protocolo (§165), cumprido a letra:

  * `PYTHONDONTWRITEBYTECODE=1` e `__pycache__` limpo AO APLICAR **e** AO
    RESTAURAR. Um mutante do MESMO TAMANHO do original engana a cache do
    `.pyc` — o ataque ia ao disco e o interpretador continuava a correr o
    codigo antigo, e isso le-se como SURVIVOR quando foi so cache velha.
  * PROVA-SE O DIFF: o ficheiro em disco mudou mesmo, com bytes antes/depois.
  * PROVA-SE QUE O MUTANTE EXECUTOU: relê-se o ficheiro e confirma-se que a
    linha nova la esta no momento em que a suite corre.
  * Ancoras SEM `\\n`: estes ficheiros estao em CRLF, e um padrao com `\\n`
    nunca casaria — o ataque «falhava» por nao encontrar o alvo, e o relatorio
    diria PASS sobre um ataque que nunca aconteceu.

`SURVIVORS = 0` e a unica saida aceitavel. Um sobrevivente e reportado com o
nome do ataque e do teste que devia te-lo apanhado.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CUR = RAIZ / "curadoria"
SAIDA = CUR / "RED-TEAM-PONTE-CURADOR-V1.json"

SUITE = ["curadoria.test_reconciliar_livros", "curadoria.test_collection_gate",
         "curadoria.test_ready_split"]

# (nome, ficheiro, texto original, texto mutante, a lei que se desliga)
ATAQUES = [
    ("RT-A1_livro_do_bot_sobrescreve_o_canonico", "reconciliar_livros.py",
     '    if tA is not None and _quando(tC) <= _quando(tA):',
     '    if False:',
     "o bot passa a derrubar medicoes mais recentes desta arvore"),

    ("RT-A2_promocao_sem_prova_de_canario_passa", "reconciliar_livros.py",
     '        if not prova_do_bot_resolve:',
     '        if False:',
     "READY do bot com EVIDENCE_REF que nao resolve passa a promover"),

    ("RT-A3_legacy_lavada_para_current", "reconciliar_livros.py",
     '    if final in (READY_LEGACY, READY_CURRENT) and vC in (READY_LEGACY, READY_CURRENT):',
     '    if False:',
     "o bot passa a subir a regua de uma READY_LEGACY"),

    ("RT-A4_policy_block_some_por_omissao", "reconciliar_livros.py",
     '    b = bloqueio_de(chave, chaves_originais, ctx)',
     '    b = {}',
     "bloqueios provados deixam de ser preservados"),

    ("RT-A5_fonte_so_do_bot_desaparece", "reconciliar_livros.py",
     '    for k in sorted(A | B | B2 | C):',
     '    for k in sorted(A | B | B2):',
     "as fontes que so o bot conhece somem do censo"),

    ("RT-A6_fonte_so_da_collection_desaparece", "reconciliar_livros.py",
     '    A, B, B2, C = (set(ctx["_ULT"][n]) for n in LIVROS)',
     '    A, B, B2, C = (set(ctx["_ULT"][n]) for n in LIVROS); A = A & C',
     "as fontes que so a Collection conhece somem do censo"),

    ("RT-A7_identidade_duplicada_passa", "reconciliar_livros.py",
     '        alvo = ctx["ALIAS"].get(sid)',
     '        alvo = None',
     "a candidata deixa de ser alias e vira uma segunda identidade"),

    ("RT-A8_ponte_apaga_em_vez_de_acrescentar", "reconciliar_livros.py",
     '        LC.registar(t["SOURCE_ID"], t["NOVO"], t["REASON"], owner=t["OWNER"],',
     '        LC._gravar({"DATASET": "LIFECYCLE-LEDGER-V1", "CONTRATO": LC.CONTRATO, "LEI": "x", "TRANSICOES": []}); LC.registar(t["SOURCE_ID"], t["NOVO"], t["REASON"], owner=t["OWNER"],',
     "aplicar passa a reescrever o livro em vez de acrescentar"),

    ("RT-A9_reconciliacao_sem_proveniencia", "reconciliar_livros.py",
     '                                   "EXTRA": {"IMPORTADO_DE": {"LIVRO": origem, "COMMIT": ctx["COMMITS"][origem],',
     '                                   "EXTRA": {"SEM_PROVENIENCIA": {"LIVRO": origem, "COMMIT": ctx["COMMITS"][origem],',
     "o que vem de outro livro deixa de dizer de onde veio"),

    ("RT-A10_portao_deixa_de_morder", "collection_gate.py",
     '    if regua not in RS.REGUAS_QUE_ADMITEM:',
     '    if False:',
     "READY_LEGACY passa a entrar na Collection"),

    ("RT-A11_portao_ignora_revisao_humana", "collection_gate.py",
     '    if revisao:',
     '    if False:',
     "item que parece seccao passa a entrar sem olho humano"),

    ("RT-A12_regua_aceita_capa_como_item", "ready_split.py",
     '    passos["BODY_UTIL"] = (dados.get("DETAIL_GATE_PASSED") is True',
     '    passos["BODY_UTIL"] = (True or dados.get("DETAIL_GATE_PASSED") is True',
     "um MIXED/NAO_SEI passa a contar como corpo util"),

    ("RT-A13_ponte_presa_a_um_commit_fixo", "reconciliar_livros.py",
     '    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else REF_C_MEDIDO',
     '    return REF_C_MEDIDO',
     "a ponte deixa de ver o trabalho futuro do bot"),

    ("RT-A14_prova_do_bot_nao_atravessa", "reconciliar_livros.py",
     '    provas = importar_provas_do_bot([t for t in p if t["SOURCE_ID"] not in ilegais], ctx)',
     '    provas = {"PROVAS_CITADAS_DE_C": 0, "PROVAS_IMPORTADAS": 0, "PROVAS_JA_PRESENTES_IDENTICAS": 0, "COLISOES_NAO_IMPORTADAS": [], "PROVAS_NO_MANIFESTO_DEPOIS": 0}',
     "o estado atravessa mas a prova fica para tras — cano entupido no fim"),

    ("RT-A15_colisao_de_prova_sobrepoe_a_local", "reconciliar_livros.py",
     '            if igual:',
     '            if True:',
     "uma prova do bot com a mesma referencia passa a substituir a desta arvore"),

    # ⚠️ O ESPELHO DO RT-A1. Ali o bot vencia SEMPRE; aqui nunca vence — e o
    # efeito e pior, porque e silencioso: as promocoes ja aconteceram e o que
    # deixa de atravessar e a MA noticia. Uma fonte que se degrada fica
    # elegivel para sempre, com tudo verde.
    ("RT-A16_despromocao_do_bot_nao_atravessa", "reconciliar_livros.py",
     '    if tA is not None and _quando(tC) <= _quando(tA):',
     '    if tA is not None:',
     "o bot deixa de poder despromover: quem se degrada continua elegivel"),

    ("RT-A17_regua_ignora_gate_reprovado", "ready_split.py",
     '    passos["BODY_UTIL"] = (dados.get("DETAIL_GATE_PASSED") is True',
     '    passos["BODY_UTIL"] = (dados.get("DETAIL_GATE_PASSED") is not None',
     "um canario REPROVADO passa a contar como corpo util"),
]


def limpar_cache() -> None:
    for p in RAIZ.rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)


def correr_suite() -> tuple[bool, str]:
    amb = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-m", "unittest"] + SUITE,
                       cwd=str(RAIZ), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=amb, timeout=900)
    return r.returncode == 0, (r.stderr or "")[-1500:]


def correr_prova_ao_vivo() -> bool:
    """A prova de runtime tambem conta como guarda: um ataque que a suite nao
    apanhe mas que parta a ponte ao vivo continua a ser um ataque apanhado."""
    amb = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "curadoria/provar_ponte_curador.py"],
                       cwd=str(RAIZ), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=amb, timeout=900)
    return r.returncode == 0


def atacar(nome: str, ficheiro: str, de: str, para: str, lei: str) -> dict:
    alvo = CUR / ficheiro
    original = alvo.read_bytes()
    texto = original.decode("utf-8")
    if de not in texto:
        return {"ATAQUE": nome, "FICHEIRO": ficheiro, "LEI_DESLIGADA": lei,
                "RESULTADO": "ANCORA_NAO_ENCONTRADA",
                "MORTO": False,
                "NOTA": "o ataque NAO aconteceu — ancora fora do ficheiro; isto nao e um PASS"}
    if texto.count(de) != 1:
        return {"ATAQUE": nome, "FICHEIRO": ficheiro, "LEI_DESLIGADA": lei,
                "RESULTADO": "ANCORA_AMBIGUA (%d ocorrencias)" % texto.count(de),
                "MORTO": False, "NOTA": "o ataque NAO aconteceu"}
    mutante = texto.replace(de, para, 1).encode("utf-8")
    try:
        limpar_cache()                      # ao APLICAR
        alvo.write_bytes(mutante)
        # PROVA de que o mutante esta no disco no momento em que a suite corre
        em_disco = alvo.read_bytes()
        executou = (em_disco == mutante and para in em_disco.decode("utf-8")
                    and em_disco != original)
        verde_suite, saida = correr_suite()
        verde_vivo = correr_prova_ao_vivo() if verde_suite else False
        morto = executou and not (verde_suite and verde_vivo)
        return {
            "ATAQUE": nome, "FICHEIRO": ficheiro, "LEI_DESLIGADA": lei,
            "DIFF": {"BYTES_ANTES": len(original), "BYTES_DEPOIS": len(mutante),
                     "DE": de.strip()[:110], "PARA": para.strip()[:110]},
            "MUTANTE_EXECUTOU": executou,
            "SUITE_VERDE_COM_MUTANTE": verde_suite,
            "PROVA_AO_VIVO_VERDE_COM_MUTANTE": verde_vivo,
            "MORTO": morto,
            "APANHADO_POR": ("suite" if not verde_suite else
                             ("prova ao vivo" if not verde_vivo else None)),
            "SAIDA": None if morto and not verde_suite is False else saida[-400:],
        }
    finally:
        alvo.write_bytes(original)
        limpar_cache()                      # ao RESTAURAR
        assert alvo.read_bytes() == original, "restauro falhou em %s" % ficheiro


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    limpar_cache()
    base_verde, _ = correr_suite()
    base_vivo = correr_prova_ao_vivo()
    linhas = [atacar(*a) for a in ATAQUES]
    sobreviventes = [l for l in linhas if not l["MORTO"]]
    d = {"DATASET": "RED-TEAM-PONTE-CURADOR-V1",
         "LEI": "cada lei da ponte desligada a mao; um teste tem de morrer por cada uma",
         "PROTOCOLO": ("§165 cache-safe: PYTHONDONTWRITEBYTECODE=1, __pycache__ limpo ao "
                       "aplicar E ao restaurar, diff provado, execucao do mutante provada, "
                       "ancoras sem \\n (ficheiros em CRLF)"),
         "BASE": {"SUITE_VERDE_SEM_MUTANTE": base_verde,
                  "PROVA_AO_VIVO_VERDE_SEM_MUTANTE": base_vivo},
         "ATAQUES": len(linhas), "MORTOS": len(linhas) - len(sobreviventes),
         "SURVIVORS": len(sobreviventes),
         "SOBREVIVENTES": [{"ATAQUE": l["ATAQUE"], "LEI_DESLIGADA": l["LEI_DESLIGADA"],
                            "RESULTADO": l.get("RESULTADO")} for l in sobreviventes],
         "LINHAS": linhas}
    if "--escrever" in argv:
        SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("BASE suite=%s vivo=%s" % (base_verde, base_vivo))
    for l in linhas:
        print("  %-46s MORTO=%-5s %s" % (l["ATAQUE"], l["MORTO"],
                                         l.get("APANHADO_POR") or l.get("RESULTADO") or ""))
    print("ATAQUES %d  MORTOS %d  SURVIVORS %d" % (d["ATAQUES"], d["MORTOS"], d["SURVIVORS"]))
    return 0 if (d["SURVIVORS"] == 0 and base_verde and base_vivo) else 1


if __name__ == "__main__":
    raise SystemExit(main())
