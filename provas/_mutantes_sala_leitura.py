"""SALA-LEITURA (D9/D10) · mutacao: cada mutante estraga o so-leitura ou o READY inteiro de ler_atual.

    py -B provas/_mutantes_sala_leitura.py

Precisa do Postgres descartavel (os testes negativos N1-N3 e P1/D10 correm num banco
proprio, nunca na Sala real): e trabalho pesado, so com LOCK-PESADO e >= 5 GB livres.
Le e grava em BYTES: o ficheiro volta byte a byte (sem trocar o fim de linha).
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTES = ["tests.test_sala_leitura_d9_d10"]
ALVO = "admissao/sala_de_espera.py"
MUTANTES = [
    ("S1 o PGOPTIONS do chamador volta a ser deitado fora",
     'return dict(os.environ, PGOPTIONS=(chamador + " " + nossa).strip())',
     'return dict(os.environ, PGOPTIONS=nossa)'),
    ("S2 a escrita em modo leitura deixa de pedir read only ao banco",
     '            script = "set transaction read only;\\n" + script',
     '            pass'),
    ("S3 o modo leitura deixa de conferir o on",
     '            if prova.strip("\\r") != "on":',
     '            if False:'),
    ("S6 a prova on deixa de ser separada dos dados (o defeito real de 26/09)",
     '            prova, _, bruto = bruto.partition("\\n")',
     '            prova, bruto = "on", bruto'),
    ("S4 ler_atual perde o historico das revisoes",
     '            u["HISTORICO_DE_REVISOES"] = historico.get(ordem, [])',
     '            u["HISTORICO_DE_REVISOES"] = []'),
    ("S5 a leitura deixa de abrir a transacao em read only",
     '            sql = ("begin read only;\\nshow transaction_read_only;\\n"',
     '            sql = ("begin;\\nshow transaction_read_only;\\n"'),
]


def main():
    alvo = os.path.join(RAIZ, ALVO)
    with open(alvo, "rb") as f:
        original = f.read()
    mortos = 0
    for nome, de, para in MUTANTES:
        de_b, para_b = de.encode("utf-8"), para.encode("utf-8")
        assert original.count(de_b) == 1, "trecho nao unico/ausente: " + nome
        try:
            with open(alvo, "wb") as f:
                f.write(original.replace(de_b, para_b))
            r = subprocess.run([sys.executable, "-B", "-m", "unittest"] + TESTES, cwd=RAIZ,
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            saiu = r.stderr.strip().splitlines()[-1:] or [""]
            skip = "skipped" in saiu[0] and "FAILED" not in saiu[0]
            morto = r.returncode != 0
            mortos += morto
            print("%-62s %s%s" % (nome, "MORTO" if morto else "VIVO",
                                  "  (atencao: testes de banco saltados)" if skip else ""))
        finally:
            with open(alvo, "wb") as f:
                f.write(original)
    print("MUTANTES %d/%d mortos" % (mortos, len(MUTANTES)))
    return 0 if mortos == len(MUTANTES) else 1


if __name__ == "__main__":
    sys.exit(main())
