#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEDE o parser canónico (coleta/rotulo_t4_it.py) nos 163 rótulos PDF reais.

    python provas/medir_rotulo_t4_nos_163.py [PASTA_DOS_PDF] [--saida FICHEIRO.json]

Os PDFs não estão no Git (`data/raw/*` está no .gitignore); só o _MANIFESTO.json
está. Por isso a pasta é argumento: por omissão a deste checkout. Cada PDF é
conferido pelo sha256 do manifesto ANTES de ser lido — bytes diferentes não
contam como o mesmo rótulo.

Só lê. Não escreve na pasta dos PDFs. Sem rede.

O que a medida NÃO prova: que as linhas lidas estão certas. Prova quantos rótulos
atravessam cada degrau (abre → é deste registo → tem linha → tem dose) e deixa a
contagem ao lado do denominador. A precisão da dose está no teste
`ADoseContraOLeitorGeometrico`, contra o leitor por posição.
"""
import hashlib
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'coleta'))
import rotulo_t4_it as R  # noqa: E402

MANIFESTO = os.path.join(ROOT, 'data', 'raw', 'IT-ROTULOS', '_MANIFESTO.json')


def medir(pasta):
    with open(MANIFESTO, encoding='utf-8') as f:
        man = json.load(f)
    reg = R.ler_registo()
    c, por = Counter(), []
    for it in man['ITENS']:
        caminho = os.path.join(pasta, it['ARQUIVO'])
        linha = {'REGISTRATION_ID': it['REGISTRATION_ID'], 'PRODUCT': it['PRODUCT']}
        if not os.path.exists(caminho):
            c['PDF_AUSENTE'] += 1
            por.append(dict(linha, ESTADO='PDF_AUSENTE'))
            continue
        with open(caminho, 'rb') as f:
            dados = f.read()
        if hashlib.sha256(dados).hexdigest() != it['SHA256']:
            c['SHA256_DIFERENTE'] += 1
            por.append(dict(linha, ESTADO='SHA256_DIFERENTE'))
            continue
        c['PDF_CONFERIDO'] += 1
        r = R.ler_rotulo(dados, R.ficha_do_registo(reg, it['REGISTRATION_ID']),
                         product_id=it.get('PRODUCT_ID'), url=it.get('URL'),
                         capturado_em=it.get('BAIXADO_EM'))
        ls = r['LINHAS_DE_USO']
        c['LEITURA_' + r['ESTADO_DA_LEITURA']] += 1
        c['CONFERENCIA_REGISTO_' + (r['CONFERENCIA'].get('REGISTO', {}).get('ESTADO') or 'SEM')] += 1
        c['CONFERENCIA_TITULAR_' + (r['CONFERENCIA'].get('TITULAR', {}).get('ESTADO') or 'SEM')] += 1
        for k in ('DATA_DO_DECRETO', 'VALIDADE_DO_ROTULO', 'TITULAR_NO_ROTULO',
                  'INTERVALO_DE_SEGURANCA_DO_DOCUMENTO'):
            if r['CABECALHO'].get(k, {}).get('ESTADO') == R.ENCONTRADO:
                c['CABECALHO_' + k] += 1
        c['LINHAS'] += len(ls)
        for l in ls:
            c['LINHA_' + l['LIGACAO_NIVEL']] += 1
            c['LINHA_ALVO_' + l['ALVO']['ESTADO']] += 1
            for k in ('DOSE', 'EPOCA', 'RESTRICOES', 'MAX_APLICACOES', 'INTERVALO_DE_SEGURANCA'):
                if l[k]['ESTADO'] == R.ENCONTRADO:
                    c['LINHA_COM_' + k] += 1
        if any(l['DOSE']['ESTADO'] == R.ENCONTRADO for l in ls):
            c['ROTULOS_COM_ALGUMA_DOSE'] += 1
        por.append(dict(linha, ESTADO=r['ESTADO_DA_LEITURA'], EXTRATOR=r['DOCUMENTO'].get('EXTRATOR'),
                        REGISTO=r['CONFERENCIA'].get('REGISTO', {}).get('ESTADO'),
                        LINHAS=len(ls), COM_DOSE=sum(1 for l in ls if l['DOSE']['ESTADO'] == R.ENCONTRADO),
                        MOTIVO=r.get('MOTIVO') or r['DOCUMENTO'].get('MOTIVO')))
    return {'SCHEMA': 'sintonia.medida-rotulo-t4/1', 'MANIFESTO_TOTAL': man['TOTAL'],
            'CONTAGEM': dict(sorted(c.items())), 'POR_ROTULO': por}


def main(argv):
    pasta = os.path.join(ROOT, 'data', 'raw', 'IT-ROTULOS')
    saida = None
    a = list(argv)
    if '--saida' in a:
        i = a.index('--saida')
        saida = a[i + 1]
        del a[i:i + 2]
    if a:
        pasta = a[0]
    m = medir(pasta)
    m['PASTA_LIDA'] = pasta
    txt = json.dumps(m, ensure_ascii=False, indent=1)
    if saida:
        with open(saida, 'w', encoding='utf-8', newline='\n') as f:
            f.write(txt + '\n')
    print(json.dumps(m['CONTAGEM'], ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
