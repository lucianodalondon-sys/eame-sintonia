#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTACAO DO CONSERTO-REGUA — cada conserto tem de morder, e os testes tem de reprovar o codigo de ANTES.

M0 repoe os dois ficheiros como estao no vivo (`ce28040c`) e exige VERMELHO: e a prova de que os
testes apanham os defeitos reais, e nao so os que eu inventei. M1..M8 estragam um conserto de cada vez.
Restauro pela copia em memoria, sempre. Sem .pyc (`-B`).

    py tests/mutacao_conserto_regua.py
"""
import io
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
MODULO = "tests.test_conserto_regua"
BASE = "ce28040c"
F = "leis/fato_do_texto.py"
H = "coleta/executor_texto_de_html.py"

CASOS = [
    (F, '    ("TERMO_DE_COMPARACAO", re.compile(', '    ("TERMO_DE_COMPARACAO_DESLIGADO", re.compile(r"(?!x)x") or re.compile(',
     "M1 · o ano de comparacao volta a ser tempo do facto"),
    (F, '    return _janela(frase, pos, pos + len(lugar))', '    return _trecho(frase, 200)',
     "M2 · o trecho do lugar volta a ser o comeco da frase"),
    (F, '    if len(outras) >= 2:', '    if False:',
     "M3 · a lista de eventos volta a juntar lugares"),
    (F, '        return i <= int(mv.group(1)) <= f and i <= int(mv.group(2) or mv.group(1)) <= f',
     '        return False', "M4 · as sessoes de um evento de 3 dias viram eventos diferentes"),
    (F, '    return {"fact_location": fact_location, "fact_location_basis": fact_location_basis,',
     '    return {"fact_location": fact_location, "fact_location_basis": fact_location_basis[:300],',
     "M5 · a base do lugar volta a ser cortada"),
    (F, '    base = original if original is not None and len(original) == len(t) else t',
     '    base = t', "M6 · o trecho da data de evento sai do texto tapado"),
    (F, '            trecho = (_janela(base, ini_f + m.start(), ini_f + m.end()) if ini_f >= 0\n',
     '            trecho = (_trecho(frase) if ini_f >= 0\n', "M7 · o trecho da data de evento volta a ser cortado"),
    (H, '                    (pagina if tipos and not (tipos & TIPOS_QUE_PUBLICAM) else publica).append(v)',
     '                    publica.append(v)', "M8 · um WebPage volta a publicar"),
]


def corre():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([PY, "-B", "-W", "ignore", "-m", "unittest", MODULO], cwd=RAIZ,
                       capture_output=True, text=True, env=env)
    return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1:]


def _ler(f):
    return io.open(os.path.join(RAIZ, f), encoding="utf-8", newline="").read()


def _escrever(f, s):
    io.open(os.path.join(RAIZ, f), "w", encoding="utf-8", newline="").write(s)


def main():
    print("MUTACAO_DO_CONSERTO_REGUA")
    mordeu, falhas = 0, []
    # M0 · o codigo de ANTES (os dois ficheiros do vivo)
    originais = {f: _ler(f) for f in (F, H)}
    try:
        for f in (F, H):
            antes = subprocess.run(["git", "show", "%s:%s" % (BASE, f)], cwd=RAIZ,
                                   capture_output=True).stdout.decode("utf-8")
            crlf = "\r\n" in originais[f]
            _escrever(f, antes.replace("\r\n", "\n").replace("\n", "\r\n") if crlf else antes)
        verde, cauda = corre()
    finally:
        for f, s in originais.items():
            _escrever(f, s)
    if verde:
        print("  NAO_MORDEU   M0 · o codigo de antes (%s) passa nos testes" % BASE)
        falhas.append("M0")
    else:
        mordeu += 1
        print("  MORDEU       M0 · o codigo de antes (%s) — %s" % (BASE, cauda[0][:70] if cauda else ""))
    for f, velho, novo, nome in CASOS:
        original = _ler(f)
        crlf = "\r\n" in original
        v, n_ = (velho.replace("\n", "\r\n"), novo.replace("\n", "\r\n")) if crlf else (velho, novo)
        if original.count(v) != 1:
            print("  NAO_APLICOU  %s (ocorrencias=%d)" % (nome, original.count(v)))
            falhas.append(nome)
            continue
        try:
            _escrever(f, original.replace(v, n_))
            verde, cauda = corre()
        finally:
            _escrever(f, original)
        if verde:
            print("  NAO_MORDEU   %s" % nome)
            falhas.append(nome)
        else:
            mordeu += 1
            print("  MORDEU       %s — %s" % (nome, cauda[0][:70] if cauda else ""))
    print()
    print("MUTACOES_MORDERAM=%d/%d" % (mordeu, len(CASOS) + 1))
    return 0 if not falhas else 1


if __name__ == "__main__":
    sys.exit(main())
