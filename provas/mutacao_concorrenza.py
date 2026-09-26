#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTACAO DA CONCORRENZA-V1 — planta um defeito de cada vez e exige que os testes o colham.

    py provas/mutacao_concorrenza.py

Cada mutante e uma troca de texto num ficheiro. O ficheiro original e guardado
em memoria e REPOSTO no `finally` byte a byte — nunca por `git checkout`, que
apagaria trabalho nao commitado de quem estiver na mesma pasta.

Corre com `-B` e apaga o __pycache__ das duas gavetas antes de cada mutante: um
mutante do mesmo tamanho e com a mesma hora pode ser servido pelo .pyc velho.

Saida: uma linha por mutante (COLHIDO | SOBREVIVEU) e exit 1 se algum sobreviver.
"""
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTE = 'tests.test_comunicacao_concorrenza'
EXTRATOR = os.path.join('coleta', 'comunicacao_concorrenza.py')
REGRA = os.path.join('curadoria', 'atribuir_source_id.py')

MUTANTES = [
    # --- a gaveta da fonte
    ('M01 regra volta a ler o endereco inteiro', REGRA,
     '    nome = _nome_e_casa(c)', '    nome = "%s %s" % (c.get("NOME", ""), c.get("URL", ""))'),
    ('M02 forma juridica sem fim de palavra', REGRA,
     'group|gruppo|italia)(?![a-z0-9])', 'group|gruppo|italia)'),
    ('M03 casa do endereco deixa de contar', REGRA,
     '    casa = m.group(1) if m else ""', '    casa = ""'),
    # --- produto
    ('M04 substancia volta a ser produto', EXTRATOR,
     "        destino = subs if (", "        destino = prods if ("),
    ('M05 virgula volta a ser ponte', EXTRATOR,
     r'(?:®|™)\s+(?:e|and|y|et)\s+$', r'(?:®|™)\s*(?:e|and|y|et|,)\s*$'),
    ('M06 palavra depois da marca ignorada', EXTRATOR,
     '        if _RE_DEPOIS_DE_SUBSTANCIA.search(texto[m.end():m.end() + 20]):',
     '        if False:'),
    ('M07 empresa colada a marca vira produto', EXTRATOR,
     '        if ultima and ultima[-1].lower() in MARCAS + [PROPRIA]:', '        if False:'),
    ('M08 nome sem marca vira produto', EXTRATOR,
     r'[\w])\s?(?:®|™|\(R\)|\(TM\))")', r'[\w])\s?(?:®|™|\(R\)|\(TM\))?")'),
    ('M09 duas grafias contam duas vezes', EXTRATOR,
     '        nome = vistos.setdefault(chave_do_nome(nome), nome)', '        pass'),
    # --- empresa e tipo
    ('M10 empresa adivinhada pelo texto', EXTRATOR,
     "    return NAO_SEI, 'a coleta nao declarou canal/conta de empresa conhecida'",
     "    return (_empresas_em(cl._norm(_texto(item))) or [NAO_SEI])[0], 'texto'"),
    ('M11 ADAMA vira concorrente', EXTRATOR,
     "        'COMPANY_ROLE': ('ADAMA_PROPRIA' if empresa == PROPRIA.upper() else",
     "        'COMPANY_ROLE': ('ADAMA_PROPRIA' if False else"),
    ('M12 comunicado sem empresa conhecida', EXTRATOR,
     '    if empresa != NAO_SEI:\n        if _RE_URL_COMUNICADO', '    if True:\n        if _RE_URL_COMUNICADO'),
    ('M13 organico lido como pago', EXTRATOR,
     "    if u('ACTIVITY_TYPE').startswith('ORGANIC') or", "    if u('ACTIVITY_TYPE').startswith('XORGANIC') and"),
    # --- alegacao x facto
    ('M14 alegacao regulatoria vira facto', EXTRATOR,
     "        factos = [f for v in validacoes for f in v.get('FACTOS_REGULATORIOS', [])]",
     "        factos = [f for v in validacoes for f in v.get('FACTOS_REGULATORIOS', [])] + "
     "[a for a in als if 'ALEGACAO_REGULATORIA' in a['TIPOS']]"),
    ('M15 contagens somadas', EXTRATOR,
     "        'CONTAGEM': {'ALEGACOES': len(als), 'FACTOS_REGULATORIOS': len(factos)},",
     "        'CONTAGEM': {'ALEGACOES': len(als) + len(factos), 'FACTOS_REGULATORIOS': len(factos)},"),
    ('M16 sem registo vira nao-registado', EXTRATOR,
     "        return {'PRODUTO': produto, 'ESTADO': 'REGISTO_NAO_LIGADO', 'VALIDADO': NAO_SEI,",
     "        return {'PRODUTO': produto, 'ESTADO': 'REGISTO_NAO_LIGADO', 'VALIDADO': False,"),
    ('M17 outro titular vira validado', EXTRATOR,
     "        if len(do_titular) == len(titulares):", "        if do_titular or True:"),
    ('M18 marca+sufixo nao casa', EXTRATOR,
     '        for r in self._por_marca.get(k, []):', '        for r in []:'),
    ('M19 item de registo ganha alegacoes', EXTRATOR,
     "        # o item E o registo: o facto e ele mesmo, e nao ha alegacao nenhuma\n        als = []",
     "        # o item E o registo: o facto e ele mesmo, e nao ha alegacao nenhuma\n        als = alegacoes(texto, produtos)"),
    # --- tempo, lugar, cultura
    ('M20 data da comunicacao vira data do facto', EXTRATOR,
     "        'FACT_TIME': NAO_SEI,", "        'FACT_TIME': tempo[0],"),
    ('M21 alcance vira lugar do facto', EXTRATOR,
     "        'COUNTRY_OF_FACT': paises[0] if len(paises) == 1 else (paises or NAO_SEI),",
     "        'COUNTRY_OF_FACT': paises[0] if len(paises) == 1 else (paises or item.get('COUNTRY_REACHED') or NAO_SEI),"),
    ('M22 acrescimo de culturas desligado', EXTRATOR,
     'CULTURAS = _somar(cl.CULTURAS, CULTURAS_A_MAIS)', 'CULTURAS = _somar(cl.CULTURAS, {})'),
    ('M23 pero espanhol entra como pereira', EXTRATOR,
     "    'POME_FRUIT': ['melo', 'meleto', 'pomacee'],", "    'POME_FRUIT': ['melo', 'meleto', 'pomacee', 'pero'],"),
    ('M24 lista de marcas diverge do pacote', EXTRATOR,
     "          'certis', 'gowan', 'nufarm', 'belchim', 'sumitomo']",
     "          'certis', 'gowan', 'nufarm', 'belchim', 'sumitomo', 'adama']"),
]


def _limpar_pyc():
    for g in ('coleta', 'curadoria', 'tests'):
        shutil.rmtree(os.path.join(RAIZ, g, '__pycache__'), ignore_errors=True)


def _correr():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    p = subprocess.run([sys.executable, '-B', '-m', 'unittest', TESTE], cwd=RAIZ, env=env,
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    return p.returncode


def main():
    _limpar_pyc()
    if _correr() != 0:
        print('BASE VERMELHA — a prova de mutacao nao vale sobre testes que ja falham')
        return 2
    sobreviventes = 0
    for nome, rel, velho, novo in MUTANTES:
        caminho = os.path.join(RAIZ, rel)
        with open(caminho, 'rb') as f:
            original = f.read()
        texto = original.decode('utf-8')
        n = texto.count(velho)
        if n != 1:
            print('%-48s ALVO_NAO_UNICO (%d) — mutante invalido' % (nome, n))
            sobreviventes += 1
            continue
        try:
            with open(caminho, 'wb') as f:
                f.write(texto.replace(velho, novo).encode('utf-8'))
            _limpar_pyc()
            colhido = _correr() != 0
        finally:
            with open(caminho, 'wb') as f:
                f.write(original)
            _limpar_pyc()
        print('%-48s %s' % (nome, 'COLHIDO' if colhido else 'SOBREVIVEU'))
        sobreviventes += 0 if colhido else 1
    print('\n%d/%d colhidos' % (len(MUTANTES) - sobreviventes, len(MUTANTES)))
    return 1 if sobreviventes else 0


if __name__ == '__main__':
    sys.exit(main())
