#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SUITE DO GATE PERCEBE QUANDO O GATE MUDA? — prova por mutacao.

    python3 provas/mutacao_do_gate.py

POR QUE ISTO EXISTE
-------------------
Uma suite verde nao prova que ela morde. Prova que, com o codigo COMO ESTA,
nada rebentou. Sao coisas diferentes, e a diferenca so aparece quando se mexe
no codigo de proposito:

    UMA SUITE QUE NAO REPROVA UM LIMIAR ALTERADO
    NAO ESTA A GUARDAR LIMIAR NENHUM.

O risco concreto deste gate nao e um bug: e alguem — pessoa ou missao futura —
mexer num numero depois de ver um resultado que nao gostou. Se a suite nao
reparar, o gate deixou de ser um alvo desenhado antes e passou a ser uma
opiniao editavel.

    O GATE SO PROTEGE O QUE A SUITE DEFENDE.

COMO FUNCIONA
-------------
Para cada mutacao: altera-se O FICHEIRO REAL do dono do gate, corre-se a suite
real, e exige-se que ela REPROVE. Depois restaura-se o ficheiro, byte a byte,
e confirma-se pelo hash.

    mutante que sobrevive = limiar sem guarda

    SURVIVORS = 0   e a unica saida aceitavel.

O QUE ISTO NAO E
----------------
Nao e um gate, nao classifica nada, nao toca na Admission e nao le documento
nenhum do corpus. Mede a suite — nao o mecanismo.
"""
import hashlib
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

DONO = os.path.join(RAIZ, "provas", "gate_de_aceitacao_tematica.py")
SUITE = "tests.test_gate_de_aceitacao_tematica"


# ══════════════════════════════════════════════════════════════════════════
# AS MUTACOES — uma por cada coisa que a missao mandou mutar
# ══════════════════════════════════════════════════════════════════════════
# Cada uma e um afrouxamento PLAUSIVEL: o tipo de alteracao que alguem faria a
# olhar para um resultado, e nao um disparate que qualquer leitura apanhava.
# Um mutante absurdo passar nao prova nada; um mutante credivel sobreviver
# prova que o numero nao tem dono.
#
# ONDE e PARA incluem a chave do limiar, e nao so o numero: `Fraction(28, 31)`
# aparece duas vezes no ficheiro, e trocar as duas de uma vez mediria outra
# coisa.
MUTACOES = (
    {
        "NOME": "positive capture threshold",
        "O_QUE_AFROUXA": "aceitar 9 de 11 positivos em vez de 10",
        "ONDE": '"POSITIVE_CAPTURE_MINIMUM": {\n        "VALOR": Fraction(10, 11),',
        "PARA": '"POSITIVE_CAPTURE_MINIMUM": {\n        "VALOR": Fraction(9, 11),',
    },
    {
        "NOME": "false-negative max",
        "O_QUE_AFROUXA": "tolerar UM «isto nao e T3» errado sobre um positivo",
        "ONDE": '"EXPLICIT_FALSE_NEGATIVE_MAX": {\n        "VALOR": 0,',
        "PARA": '"EXPLICIT_FALSE_NEGATIVE_MAX": {\n        "VALOR": 1,',
    },
    {
        "NOME": "specificity",
        "O_QUE_AFROUXA": "aceitar 17 de 20 negativas em vez de 18",
        "ONDE": '"SPECIFICITY_MINIMUM": {\n        "VALOR": Fraction(18, 20),',
        "PARA": '"SPECIFICITY_MINIMUM": {\n        "VALOR": Fraction(17, 20),',
    },
    {
        "NOME": "precision",
        "O_QUE_AFROUXA": "aceitar 3 em cada 5 afirmacoes certas em vez de 4",
        "ONDE": '"PRECISION_T3_MINIMUM": {\n        "VALOR": Fraction(4, 5),',
        "PARA": '"PRECISION_T3_MINIMUM": {\n        "VALOR": Fraction(3, 5),',
    },
    {
        "NOME": "decision coverage",
        "O_QUE_AFROUXA": "deixar 4 observacoes sem decisao em vez de 3",
        "ONDE": '"DECISION_COVERAGE_MINIMUM": {\n        "VALOR": Fraction(28, 31),',
        "PARA": '"DECISION_COVERAGE_MINIMUM": {\n        "VALOR": Fraction(27, 31),',
    },
    {
        "NOME": "group-pass",
        "O_QUE_AFROUXA": "aceitar 27 de 31 observacoes resolvidas e certas",
        "ONDE": '"GROUP_PASS_MINIMUM": {\n        "VALOR": Fraction(28, 31),',
        "PARA": '"GROUP_PASS_MINIMUM": {\n        "VALOR": Fraction(27, 31),',
    },
    {
        "NOME": "error max",
        "O_QUE_AFROUXA": "deixar passar um mecanismo que rebentou uma vez",
        "ONDE": '"ERROR_MAX": {\n        "VALOR": 0,',
        "PARA": '"ERROR_MAX": {\n        "VALOR": 1,',
    },
    {
        "NOME": "substring dependency",
        "O_QUE_AFROUXA": "aceitar UM resultado nascido de casamento nao pretendido",
        "ONDE": '"KNOWN_FALSE_SUBSTRING_OUTCOME_DEPENDENCY_MAX": {\n        "VALOR": 0,',
        "PARA": '"KNOWN_FALSE_SUBSTRING_OUTCOME_DEPENDENCY_MAX": {\n        "VALOR": 1,',
    },
    {
        "NOME": "reachability",
        "O_QUE_AFROUXA": "deixar um item com procedencia comprovada nao chegar",
        "ONDE": "REACHABILITY_REQUIRED = Fraction(1, 1)",
        "PARA": "REACHABILITY_REQUIRED = Fraction(35, 36)",
    },
    {
        "NOME": "group count",
        "O_QUE_AFROUXA": "pontuar ficheiros (36) onde a lei manda observacoes (31)",
        "ONDE": 'UNIDADE_PRIMARIA = "INDEPENDENT_OBSERVATION"',
        "PARA": 'UNIDADE_PRIMARIA = "DOCUMENT"',
    },
    # As tres seguintes nao sao numeros: sao as maneiras de um gate deixar de
    # ser um gate sem nenhum limiar mudar de valor.
    {
        "NOME": "fronteira do limiar",
        "O_QUE_AFROUXA": "exigir ACIMA do limiar, e nao a partir dele",
        "ONDE": "return valor >= limiar if op == \">=\" else valor <= limiar",
        "PARA": "return valor > limiar if op == \">=\" else valor < limiar",
    },
    {
        "NOME": "uma media a compensar",
        "O_QUE_AFROUXA": "uma condicao falhada deixa de reprovar o conjunto",
        "ONDE": '"THEMATIC_GATE_PASS": not falhadas,',
        "PARA": '"THEMATIC_GATE_PASS": len(falhadas) <= 1,',
    },
    {
        "NOME": "metrica em falta lida como zero",
        "O_QUE_AFROUXA": "o que rebentou passa por nunca ter falhado",
        "ONDE": '    if faltam:\n        raise MetricaEmFalta("faltam metricas do gate: %s" % faltam)',
        "PARA": '    for _f in faltam:\n        metricas = dict(metricas, **{_f: 0})',
    },
)


def _hash(caminho):
    with open(caminho, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _suite_passa():
    """True se a suite do gate corre a verde.

    ⚠️ A marca no ambiente desliga as guardas que defendem a ARVORE COMMITADA
    (ancoras unicas, ficheiro por mutar). Durante a mutacao o ficheiro esta
    alterado de proposito: se essas guardas corressem, matariam todos os
    mutantes por contabilidade e o SURVIVORS = 0 nao diria nada sobre o gate.
    A marca vale tambem para a corrida verde inicial — as duas medicoes tem de
    ver o mesmo conjunto de testes, ou nao sao comparaveis.
    """
    ambiente = dict(os.environ, SINTONIA_MUTACAO_EM_CURSO="1")
    r = subprocess.run([sys.executable, "-m", "unittest", SUITE],
                       cwd=RAIZ, capture_output=True, text=True, env=ambiente)
    return r.returncode == 0


def correr():
    original = _hash(DONO)
    with open(DONO, encoding="utf-8") as f:
        fonte = f.read()
    backup = DONO + ".mutacao.bak"
    shutil.copy2(DONO, backup)

    print("MUTACAO DO GATE — a suite percebe quando o gate muda?")
    print("=" * 74)
    print(f"  dono   {os.path.relpath(DONO, RAIZ)}")
    print(f"  suite  {SUITE}")
    print(f"  sha256 {original[:32]}…\n")

    if not _suite_passa():
        shutil.copy2(backup, DONO)
        os.remove(backup)
        print("  A suite ja estava VERMELHA antes de qualquer mutacao.")
        print("  Nao se mede mordida numa suite que ja esta a falhar.")
        return 2

    sobreviventes = []
    try:
        for m in MUTACOES:
            if fonte.count(m["ONDE"]) != 1:
                sobreviventes.append(
                    (m["NOME"], "ANCORA NAO E UNICA — a mutacao nao se aplicou"))
                print(f"  ?????  {m['NOME']:<34}ancora ausente ou repetida")
                continue
            with open(DONO, "w", encoding="utf-8") as f:
                f.write(fonte.replace(m["ONDE"], m["PARA"], 1))
            passou = _suite_passa()
            with open(DONO, "w", encoding="utf-8") as f:
                f.write(fonte)
            if passou:
                sobreviventes.append((m["NOME"], m["O_QUE_AFROUXA"]))
                print(f"  VIVE   {m['NOME']:<34}{m['O_QUE_AFROUXA']}")
            else:
                print(f"  morre  {m['NOME']:<34}{m['O_QUE_AFROUXA']}")
    finally:
        shutil.copy2(backup, DONO)
        os.remove(backup)

    restaurado = _hash(DONO)
    print(f"\n  ficheiro restaurado: "
          f"{'sim' if restaurado == original else 'NAO — VERIFICAR A MAO'}")
    if restaurado != original:
        return 3

    print(f"\n  MUTANTES  {len(MUTACOES)}")
    print(f"  SURVIVORS {len(sobreviventes)}")
    if sobreviventes:
        print("\n  Um mutante vivo e um limiar sem guarda:")
        for nome, porque in sobreviventes:
            print(f"    · {nome} — {porque}")
        return 1
    print("\n  Nenhum afrouxamento plausivel deste gate passa despercebido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(correr())
