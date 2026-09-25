#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTAÇÃO DA 033 (MIGRACAO-SALA, D68) — as travas do banco têm de morder.

Cada mutante estraga a migration, o desfazer ou o dono da Sala, corre
`tests.test_migracao_033_sala` (um Postgres descartável NOVO por mutante) e
exige VERMELHO. Restauro pela cópia em memória, sempre. Pesado: ~3 min por
mutante — corre só com LOCK-PESADO.

    py tests/mutacao_migracao_033.py
"""
import glob
import io
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
MODULO = "tests.test_migracao_033_sala"
MIG = os.path.relpath(glob.glob(os.path.join(RAIZ, "supabase", "migrations", "033_*.sql"))[0], RAIZ)

CASOS = [
    (MIG, "  raise exception 'SALA_REVISAO_SO_ACRESCENTA: % recusado em sala_de_espera_revisao. '\r\n"
          "    'Uma revisao nao se edita nem se apaga: escreve-se outra.', tg_op;",
     "  return coalesce(new, old);", False,
     "MM1 · a trava so-acrescenta deixa passar UPDATE/DELETE"),
    (MIG, "order by r.revisao desc limit 1", "order by r.revisao asc limit 1", True,
     "MM2 · a vista le a PRIMEIRA revisao em vez da ultima"),
    ("admissao/sala_de_espera.py",
     "  if v_atual is distinct from {valor} or b_atual is distinct from {base} then",
     "  if true then", False,
     "MM3 · reprocessar duas vezes duplica revisoes"),
    ("admissao/sala_de_espera.py",
     '            "from public.sala_de_espera_atual where run_id = %s order by ordem"',
     '            "from public.sala_de_espera where run_id = %s order by ordem"', False,
     "MM4 · a leitura da Intelligence ignora as revisoes"),
    ("supabase/desfazer/033_desfazer.sql",
     "delete from public.schema_migracao where versao = '033';", "select 1;", False,
     "MM5 · o desfazer esquece o livro-razao e a 033 nao volta a subir"),
    (MIG, "'observed_at', 'completude_tempo_lugar', 'janela_declarada',",
     "'observed_at', 'completude_tempo_lugar', 'janela_declarada', 'texto',", False,
     "MM6 · o banco passa a aceitar rever o TEXTO"),
]


def corre():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([PY, "-B", "-W", "ignore", "-m", "unittest", MODULO], cwd=RAIZ,
                       capture_output=True, text=True, env=env)
    return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1:]


def main():
    print("MUTACAO_DA_033")
    mordeu, falhas = 0, []
    for ficheiro, velho, novo, todas, nome in CASOS:
        caminho = os.path.join(RAIZ, ficheiro)
        original = io.open(caminho, encoding="utf-8", newline="").read()
        n = original.count(velho)
        if n == 0 or (n > 1 and not todas):
            print("  NAO_APLICOU  %s (ocorrencias=%d)" % (nome, n))
            falhas.append(nome)
            continue
        try:
            io.open(caminho, "w", encoding="utf-8", newline="").write(
                original.replace(velho, novo))
            verde, cauda = corre()
        finally:
            io.open(caminho, "w", encoding="utf-8", newline="").write(original)
        if verde:
            print("  NAO_MORDEU   %s" % nome)
            falhas.append(nome)
        else:
            mordeu += 1
            print("  MORDEU       %s — %s" % (nome, cauda[0][:80] if cauda else ""))
    print()
    print("MUTACOES_MORDERAM=%d/%d" % (mordeu, len(CASOS)))
    return 0 if not falhas else 1


if __name__ == "__main__":
    sys.exit(main())
