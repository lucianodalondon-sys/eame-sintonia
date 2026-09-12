#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.8B-R — A MUTAÇÃO DIZ SE A SENTINELA MEDE ALGUMA COISA.

    py provas/raw_entre_jobs.py

Uma bateria verde só prova que ela passou. A pergunta é outra:

    SE EU PARTIR O MECANISMO, ALGUMA SENTINELA FICA VERMELHA?

Cada mutação abaixo estraga UMA garantia do transporte da evidência. A prova
espera que a bateria `tests/test_c10_8b_r_raw_entre_jobs.py` fique VERMELHA em
todas. Uma mutação que sobrevive é uma garantia que ninguém está a guardar.

    SURVIVORS > 0 SIGNIFICA QUE A BATERIA MEDE A SI PRÓPRIA.

O QUE É MUTADO: uma CÓPIA da árvore, numa pasta temporária. A árvore real não é
tocada — nem por um instante, nem «e depois eu reponho».

    APIFY_RUNS = 0 · PAID_USD = 0 · REDE = 0
"""
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATERIA = 'tests.test_c10_8b_r_raw_entre_jobs'

#: (nome, ficheiro, texto antigo, texto novo, garantia que isto parte)
MUTACOES = [
    ('M1 · o SHA passa a vir do manifesto, sem recálculo',
     'coleta/social_scrap.py',
     "        sha, tam, _d = _sha_e_bytes(alvo)\n"
     "        bate = (sha == decl['SHA256']) and (tam == decl['RAW_BYTES'])",
     "        sha, tam = decl['SHA256'], decl['RAW_BYTES']\n"
     "        bate = True",
     'o SHA recalculado é a medida'),

    ('M2 · a recuperação passa a aceitar «o último pacote»',
     'coleta/social_scrap.py',
     "    pasta = os.path.join(de, str(run_id))\n"
     "    if not os.path.isdir(pasta):",
     "    pasta = os.path.join(de, str(run_id))\n"
     "    if not os.path.isdir(pasta) and os.path.isdir(de):\n"
     "        restantes = sorted(os.listdir(de))\n"
     "        if restantes:\n"
     "            pasta = os.path.join(de, restantes[-1])\n"
     "    if not os.path.isdir(pasta):",
     'a chave é o RUN_ID, e só ele'),

    ('M3 · o RUN_ID do manifesto deixa de ser conferido',
     'coleta/social_scrap.py',
     "    if str(manifesto.get('RUN_ID')) != str(run_id):",
     "    if False and str(manifesto.get('RUN_ID')) != str(run_id):",
     'um manifesto de outra corrida não é este'),

    ('M4 · a sonda de segredo deixa de descomprimir',
     'coleta/social_scrap.py',
     "    if dados[:2] == b'\\x1f\\x8b':",
     "    if False:",
     'o bruto pago nasce comprimido'),

    ('M5 · a sonda de segredo passa a dar sempre verde',
     'coleta/social_scrap.py',
     "    formas = [dados]",
     "    return None\n    formas = [dados]",
     'segredo nenhum viaja no pacote'),

    ('M6 · o segredo passa a ser redigido em silêncio',
     'coleta/social_scrap.py',
     "        if termo:\n"
     "            raise EvidenciaComSegredo(",
     "        if termo:\n"
     "            dados = dados.replace(termo.encode(), b'[REDIGIDO]')\n"
     "            sha, tam = _sha_e_bytes(caminho)[0], len(dados)\n"
     "        if False:\n"
     "            raise EvidenciaComSegredo(",
     'apagar evidência para o pacote passar destrói a evidência'),

    ('M7 · o pacote passa a ser escrito ANTES da sonda de segredo',
     'coleta/social_scrap.py',
     "    itens, faltaram = [], []\n    for caminho in origem:",
     "    itens, faltaram = [], []\n"
     "    if origem:\n"
     "        if os.path.isdir(alvo):\n"
     "            shutil.rmtree(alvo)\n"
     "        os.makedirs(alvo)\n"
     "    for caminho in origem:",
     'a recusa não deixa pacote meio escrito'),

    ('M8 · publicar sem ficheiro passa a devolver STAGED',
     'coleta/social_scrap.py',
     "        return {'EVIDENCE_TRANSFERRED': 'NO_RAW_PRODUCED',",
     "        return {'EVIDENCE_TRANSFERRED': 'STAGED',",
     'um upload que não sobe nada é falha'),

    ('M9 · o pacote passa a dizer-se preservação forward canônica',
     'coleta/social_scrap.py',
     "        'CANONICAL_FORWARD_PRESERVATION': 'NO',\n"
     "        'NOTA': (",
     "        'CANONICAL_FORWARD_PRESERVATION': 'YES',\n"
     "        'NOTA': (",
     'WORKFLOW ARTIFACT != CANONICAL FORWARD STORAGE'),

    ('M10 · a porta paga deixa de registar o bruto no inventário',
     'coleta/coletor.py',
     "            _env.registar_produzido(os.path.join(RAW_DIR, nome))",
     "            _env.produzidos()",
     'o que o inventário não vê não atravessa a fronteira'),

    ('M11 · o inventário passa a aceitar o mesmo ficheiro duas vezes',
     'coleta/social_envelope.py',
     "    if caminho and caminho not in _PRODUZIDOS:",
     "    if caminho:",
     'registar é idempotente'),

    ('M12 · o upload volta a avisar em vez de falhar',
     '.github/workflows/scrap-evidencia.yml',
     "          if-no-files-found: error",
     "          if-no-files-found: warn",
     'UPLOAD STEP SUCCESS != ARTIFACT EXISTS'),

    ('M13 · o job B passa a correr dentro do job A',
     '.github/workflows/scrap-evidencia.yml',
     "  recuperar:\n    needs: produzir\n    runs-on: ubuntu-latest",
     "  recuperar:\n    needs: produzir\n    runs-on: windows-latest",
     'os dois jobs correm em máquinas separadas'),

    ('M14 · a rota paga é promovida a PROVED',
     'leis/social_matriz.py',
     "  r('apify:transcricao', 'APIFY', 'CONDICIONAL', 'PARTIAL',",
     "  r('apify:transcricao', 'APIFY', 'CONDICIONAL', 'PROVED',",
     'PROVIDER REACHED != CAPABILITY DELIVERED'),
]


def _copia_da_arvore(destino):
    """Uma cópia da árvore. Nada é escrito na árvore real.

    Enumerar as pastas à mão faz a cópia partir-se cada vez que um módulo muda
    de casa — já aconteceu duas vezes ao escrever isto. Copia-se tudo o que é
    leve, e liga-se o que é pesado.
    """
    pesadas = {'.git', 'data', 'node_modules', 'italia-portale', '__pycache__',
               '.tmp', 'build'}
    for nome in os.listdir(RAIZ):
        if nome in pesadas:
            continue
        origem = os.path.join(RAIZ, nome)
        alvo = os.path.join(destino, nome)
        if os.path.isdir(origem):
            shutil.copytree(origem, alvo,
                            ignore=shutil.ignore_patterns('__pycache__',
                                                          'node_modules'),
                            symlinks=True)
        else:
            shutil.copy2(origem, alvo)
    # Pesadas: ligadas, não copiadas. RT34 lê a fixture e pergunta ao git.
    for nome in ('.git', 'data'):
        os.symlink(os.path.join(RAIZ, nome), os.path.join(destino, nome))


def _correr(arvore):
    """→ (código, saída). A bateria, na cópia."""
    p = subprocess.run([sys.executable, '-m', 'unittest', BATERIA],
                       cwd=arvore, capture_output=True, text=True)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def main():
    print('C10.8B-R · MUTAÇÃO DO TRANSPORTE DA EVIDÊNCIA')
    print('=' * 74)
    base = tempfile.mkdtemp(prefix='c108br-mut-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    try:
        _copia_da_arvore(arvore)
        codigo, saida = _correr(arvore)
        if codigo != 0:
            print('A CÓPIA JÁ NASCE VERMELHA — a mutação não mediria nada.')
            print(saida[-2000:])
            return 3
        print('cópia limpa: bateria VERDE\n')

        sobreviventes = []
        for nome, rel, velho, novo, garantia in MUTACOES:
            alvo = os.path.join(arvore, rel)
            with open(alvo, encoding='utf-8') as f:
                original = f.read()
            if velho not in original:
                print('%-58s ALVO_AUSENTE' % nome[:58])
                sobreviventes.append((nome, 'ALVO_AUSENTE'))
                continue
            with open(alvo, 'w', encoding='utf-8') as f:
                f.write(original.replace(velho, novo, 1))
            try:
                codigo, saida = _correr(arvore)
            finally:
                with open(alvo, 'w', encoding='utf-8') as f:
                    f.write(original)
            apanhada = codigo != 0
            marca = 'MORTA  ' if apanhada else 'SOBREVIVE'
            quantas = saida.count('FAIL: ') + saida.count('ERROR: ')
            print('%-58s %s (%d sentinelas)' % (nome[:58], marca, quantas))
            print('%-58s   guarda: %s' % ('', garantia))
            if not apanhada:
                sobreviventes.append((nome, garantia))

        print('=' * 74)
        print('MUTATIONS = %d' % len(MUTACOES))
        print('SURVIVORS = %d' % len(sobreviventes))
        for nome, porque in sobreviventes:
            print('  SOBREVIVEU · %s — ninguém guarda: %s' % (nome, porque))
        return 0 if not sobreviventes else 1
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
