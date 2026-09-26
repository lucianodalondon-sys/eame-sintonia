#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVA DE MUTAÇÃO do parser canónico do rótulo T4 (coleta/rotulo_t4_it.py).

    python tests/mutacao_rotulo_t4.py

Planta um defeito de cada vez, corre `tests/test_rotulo_t4_it.py` e exige que
ele FALHE. Um mutante que sobrevive é um teste que falta (ou código que sobra).

Restaura sempre os bytes originais guardados em memória — nunca `git checkout`,
que apagaria trabalho não salvo — e no fim confere o sha256 do ficheiro.
"""
import hashlib
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ALVO = os.path.join(os.path.dirname(AQUI), 'coleta', 'rotulo_t4_it.py')

MUTANTES = [
    ('M01 VERIFICADO sem conferir o numero do rotulo',
     "documento_deste_registo = conf['REGISTO']['ESTADO'] == VERIFICADO",
     "documento_deste_registo = True"),
    ('M02 rotulo de outro registo passa',
     "    if conf['REGISTO']['ESTADO'] == ERRO:\n        # rótulo",
     "    if False:\n        # rótulo"),
    ('M03 dose = o primeiro numero da linha',
     "m = cand[0] if len(cand) == 1 else None",
     "m = cand[0] if cand else None"),
    ('M04 a linha da tabela nao acaba na linha em branco',
     "if corpo and not x.strip():",
     "if False:"),
    ('M05 faixa invertida aceite como dose',
     "doses = [d for d in doses if d['MAX'] >= d['MIN']]",
     "doses = list(doses)"),
    ('M06 NAO_CONHECIDO guarda valor',
     "    if estado == NAO_CONHECIDO:\n        valor = None",
     "    if False:\n        valor = None"),
    ('M07 vocabulario de estados aberto',
     "    if estado not in ESTADOS:",
     "    if False:"),
    ('M08 sem linha lida vira NAO_AUTORIZADO',
     "ENCONTRADO if res['LINHAS_DE_USO'] else NAO_CONHECIDO",
     "ENCONTRADO if res['LINHAS_DE_USO'] else 'NAO_AUTORIZADO'"),
    ('M09 substancia UE por pedaco de palavra',
     "r'(?<![a-z])' + re.escape(alvo) + r'(?![a-z])'",
     "re.escape(alvo)"),
    ('M10 Revocato conta como vivo',
     "r'^(autorizzato|ri-registrato|rinnovato)'",
     "r'^(autorizzato|ri-registrato|rinnovato|revocato)'"),
    ('M11 titular em conflito escondido',
     "    if conf.get('TITULAR', {}).get('ESTADO') == ERRO:",
     "    if False:"),
    ('M12 bloco de cultura promovido a VERIFICADO',
     "(documento_deste_registo and nivel == 'LINHA_DA_TABELA')",
     "documento_deste_registo"),
    ('M13 BBCH vaza para a dose',
     "r'|bbch\\s*\\d+(?:\\s*[-–]\\s*(?:bbch\\s*)?\\d+)?'",
     "r'|bbch'"),
    ('M14 numero de aplicacoes e dias ficam como candidatos',
     "|applicazion\\w*|trattament\\w*|interventi)",
     "|xx_nada)"),
    ('M15 unidade herdada com duas unidades no cabecalho',
     "    if len(unids) == 1:",
     "    if unids:"),
    ('M16 carencia do documento some',
     "    out['INTERVALO_DE_SEGURANCA_DO_DOCUMENTO'] = (",
     "    out['_X'] = ("),
    ('M17 registo sem zeros a esquerda',
     "return d.zfill(6) if d else None",
     "return d if d else None"),
    ('M18 documento vazio nao e erro',
     "        doc.update(ESTADO=ERRO, MOTIVO='documento vazio (0 bytes)')\n        return '', doc",
     "        pass"),
]


def correr_testes():
    r = subprocess.run([sys.executable, '-m', 'unittest', 'test_rotulo_t4_it'],
                       cwd=AQUI, capture_output=True, text=True, timeout=300)
    return r.returncode


def main():
    with open(ALVO, 'rb') as f:
        original = f.read()
    sha0 = hashlib.sha256(original).hexdigest()
    texto = original.decode('utf-8')
    if correr_testes() != 0:
        print('BASE VERMELHA: os testes falham sem mutante; nada a provar')
        return 2
    vivos = []
    try:
        for nome, velho, novo in MUTANTES:
            n = texto.count(velho)
            if n != 1:
                print('%-58s NAO_APLICADO (%d ocorrencias)' % (nome, n))
                vivos.append(nome)
                continue
            with open(ALVO, 'wb') as f:
                f.write(texto.replace(velho, novo).encode('utf-8'))
            rc = correr_testes()
            print('%-58s %s' % (nome, 'MORTO' if rc != 0 else 'SOBREVIVEU'))
            if rc == 0:
                vivos.append(nome)
    finally:
        with open(ALVO, 'wb') as f:
            f.write(original)
    with open(ALVO, 'rb') as f:
        assert hashlib.sha256(f.read()).hexdigest() == sha0, 'restauro falhou'
    print('\n%d mutantes, %d mortos, %d vivos · sha256 restaurado %s'
          % (len(MUTANTES), len(MUTANTES) - len(vivos), len(vivos), sha0[:12]))
    return 1 if vivos else 0


if __name__ == '__main__':
    sys.exit(main())
