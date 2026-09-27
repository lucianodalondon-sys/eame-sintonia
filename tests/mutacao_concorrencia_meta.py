#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTAÇÃO DA LINHA DA META — cada separação da lei tem de morder.

Cada mutante estraga o CÓDIGO da linha, corre `tests.test_concorrencia_meta` e
exige VERMELHO. O ficheiro é restaurado da cópia em memória (não por
`git checkout`, que apagaria trabalho por commitar), sempre, mesmo em falha.
Corre com `-B` e sem .pyc: um mutante do mesmo tamanho engana o .pyc.

    python3 tests/mutacao_concorrencia_meta.py [saida.json]
"""
import io
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
MODULO = "tests.test_concorrencia_meta"

CASOS = [
    ("coleta/concorrencia_meta.py",
     "        funda = (a.get('cards') or 0) >= (r.get('cards') or 0)",
     "        funda = True",
     "M1 · ler mais fundo volta a contar como anuncio novo (a regra de 31/08 cai)"),
    ("coleta/concorrencia_meta.py",
     "            'no_longer_observed': sumidos if ambas_fechadas else [],",
     "            'no_longer_observed': sumidos,",
     "M2 · sumir de lista incompleta vira terminado"),
    ("regras/meta_identidade.py",
     "    if alvo and primeiro.startswith(alvo):",
     "    if alvo and alvo in (page_name or '').lower():",
     "M3 · token no meio do nome volta a valer (o instituto polaco entra como ADAMA)"),
    ("regras/meta_identidade.py",
     "    if not page_id_provado(pagina):",
     "    if False:",
     "M4 · PAGE_ID sem prova da Meta entra na linha"),
    ("coleta/concorrencia_meta.py",
     "    if login != bib.NAO_LOGADO:",
     "    if False:",
     "M5 · pagina lida com sessao entra na linha (D88)"),
    ("coleta/concorrencia_meta.py",
     "            if str(ad['library_id']) in vistos:",
     "            if False:",
     "M6 · o mesmo anuncio volta a Sala em cada rodada"),
    ("ferramentas/meta_biblioteca.py",
     "    return {'state': COMPLETA_BATE_COM_A_FONTE if (n and lidos >= TOLERANCIA * n)",
     "    return {'state': COMPLETA_BATE_COM_A_FONTE if (n and lidos >= 0.1 * n)",
     "M7 · parou de crescer volta a ser completa (29 de 230)"),
    ("coleta/concorrencia_meta.py",
     "            if r.get('slice_state') == SLICE_OK:",
     "            if True:",
     "M8 · rodada que caiu vira linha de base da seguinte"),
    ("coleta/concorrencia_meta.py",
     "        if str(p['page_id']) in vistos:",
     "        if False:",
     "M9 · a mesma pagina e visitada duas vezes na rodada"),
    ("coleta/concorrencia_meta.py",
     "        'TARGET_LOCATION_STATE': 'NOT_PROVED',",
     "        'TARGET_LOCATION_STATE': 'PROVED',",
     "M10 · pais alcancado vira pais alvo"),
    ("medidas/concorrencia_frentes.py",
     "        entra = entra and bool(p.get('EM_LINHA'))",
     "        entra = bool(p.get('EM_LINHA'))",
     "M11 · o quadro das frentes conta pagina recusada como na linha"),
    ("coleta/meta_anunciante.py",
     "                   if ident.guarda_identidade(i['page_name'], empresa)['state']",
     "                   if True or ident.guarda_identidade(i['page_name'], empresa)['state']",
     "M12 · a descoberta propoe o homonimo sem passar pela guarda"),
]


def corre():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([PY, "-B", "-m", "unittest", MODULO], cwd=RAIZ,
                       capture_output=True, text=True, env=env)
    return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1:]


def main():
    print("MUTACAO_DA_LINHA_DA_META")
    verde_antes, _ = corre()
    resultado = {"DATASET": "CONCORRENCIA-META-MUTACAO", "MODULO": MODULO,
                 "VERDE_SEM_MUTANTE": verde_antes, "CASOS": []}
    mordeu = 0
    for ficheiro, velho, novo, nome in CASOS:
        caminho = os.path.join(RAIZ, ficheiro)
        original = io.open(caminho, encoding="utf-8", newline="").read()
        n = original.count(velho)
        if n != 1:
            print("  NAO_APLICOU  %s (ocorrencias=%d)" % (nome, n))
            resultado["CASOS"].append({"MUTANTE": nome, "ESTADO": "NAO_APLICOU"})
            continue
        try:
            io.open(caminho, "w", encoding="utf-8", newline="").write(
                original.replace(velho, novo))
            verde, cauda = corre()
        finally:
            io.open(caminho, "w", encoding="utf-8", newline="").write(original)
        estado = "SOBREVIVEU" if verde else "MORDEU"
        mordeu += not verde
        print("  %-10s %s  %s" % (estado, nome, " ".join(cauda)))
        resultado["CASOS"].append({"MUTANTE": nome, "FICHEIRO": ficheiro,
                                   "ESTADO": estado, "CAUDA": cauda})
    resultado["MORDERAM"] = "%d/%d" % (mordeu, len(CASOS))
    verde_depois, _ = corre()
    resultado["VERDE_DEPOIS_DE_RESTAURAR"] = verde_depois
    print("MORDERAM %s · verde sem mutante: antes=%s depois=%s"
          % (resultado["MORDERAM"], verde_antes, verde_depois))
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=1)
    return 0 if (mordeu == len(CASOS) and verde_antes and verde_depois) else 1


if __name__ == "__main__":
    sys.exit(main())
