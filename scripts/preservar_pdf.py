#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRESERVA DOCUMENTO PESADO — binário para fora do Git, hash e manifesto para dentro.

    python3 scripts/preservar_pdf.py data/samples/PIEMONTE-FD IT/PIEMONTE-FD

Obedece a decisão que o próprio repositório já tomou e escreveu no `.gitignore`:

    « RAW pesado de rota paga NÃO entra mais no Git. Medido em 2026-08-29: gzip tem
      ratio 1,00 no pack e ZERO delta base. Cada versão nova entra pelo tamanho
      integral, PARA SEMPRE. Daqui para frente o bruto vai para Storage; o Git
      guarda hash e manifesto. »

O que muda aqui é só a origem: aquela regra nasceu para o bruto de rota PAGA. Um PDF
oficial de 5 MB baixado de graça pesa no pack exatamente igual — a regra é sobre o
TAMANHO no pack, não sobre o custo de aquisição.

    O MANIFESTO NÃO É O DOCUMENTO. Ele prova QUE existe, com que hash e de onde veio.
    Quem precisar do conteúdo vai ao Storage, ou baixa de novo da fonte, e confere o hash.
"""
import hashlib
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PESADO = 400 * 1024          # acima disto sai do Git


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    if len(sys.argv) < 3:
        print(__doc__); return 2
    origem = os.path.join(ROOT, sys.argv[1])
    prefixo = sys.argv[2]
    destino = os.path.join(ROOT, 'data', 'raw', prefixo)
    os.makedirs(destino, exist_ok=True)

    itens, movidos, ficaram = [], 0, 0
    for nome in sorted(os.listdir(origem)):
        p = os.path.join(origem, nome)
        if not os.path.isfile(p):
            continue
        tam = os.path.getsize(p)
        h = sha(p)
        pesado = tam > PESADO
        item = {
            'ARQUIVO': nome,
            'BYTES': tam,
            'SHA256': h,
            'ESTADO': 'MOVIDO_PARA_RAW_FORA_DO_GIT' if pesado else 'PERMANECE_EM_SAMPLES',
            'CAMINHO_LOCAL': ('data/raw/%s/%s' % (prefixo, nome)) if pesado
                             else ('%s/%s' % (sys.argv[1], nome)),
            'CONTEUDO_VERIFICADO': False,
        }
        if pesado:
            shutil.move(p, os.path.join(destino, nome))
            movidos += 1
        else:
            ficaram += 1
        itens.append(item)

    man = {
        'MANIFESTO': 'PRESERVACAO-' + os.path.basename(origem),
        'SOURCE_LOCATION': 'ver ORIGEM por item no artefato que gerou o download',
        'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'PRESERVATION_MANIFEST',
        'CAPTURED_AT': '2026-09-02',
        'REGRA': ('binario acima de %d KB sai do Git e vai para data/raw (ignorado). '
                  'O Git guarda hash e manifesto.' % (PESADO // 1024)),
        'O_QUE_ISTO_NAO_E': [
          'nao e prova de que o conteudo foi lido',
          'nao e prova de preservacao em Storage — so diz onde o arquivo esta NESTA maquina',
          'CONTEUDO_VERIFICADO=false em todos: presenca no disco nao e verificacao de conteudo',
        ],
        'ARQUIVOS': len(itens),
        'MOVIDOS_PARA_RAW': movidos,
        'PERMANECEM_EM_SAMPLES': ficaram,
        'BYTES_TOTAIS': sum(i['BYTES'] for i in itens),
        'ITENS': itens,
    }
    cam = os.path.join(origem, 'MANIFESTO-PRESERVACAO.json')
    with open(cam, 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    print('%d arquivos · %d movidos para data/raw/%s · %d ficaram · %.1f MB'
          % (len(itens), movidos, prefixo, ficaram, man['BYTES_TOTAIS'] / 1e6))
    print('manifesto: %s/MANIFESTO-PRESERVACAO.json' % sys.argv[1])
    return 0


if __name__ == '__main__':
    sys.exit(main())
