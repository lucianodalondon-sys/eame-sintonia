#!/usr/bin/env python3
"""CENSO DOS DONOS — quem JA responde por cada conceito, antes de inventar dono.

    python3 system-map/scripts/censo_dos_donos.py

PORQUE ISTO VEM ANTES DE QUALQUER TELEMETRIA
---------------------------------------------
A missao seguinte e observabilidade: saber contar o proprio fluxo. A maneira
mais rapida de a estragar e comecar por desenhar tabelas.

    REUSE FIRST.
    MEDIR QUEM JA E DONO ANTES DE NOMEAR UM NOVO.

Esta casa ja errou assim: desenhou-se primeiro e mediu-se depois, e o buraco
ficou do tamanho da tampa ja comprada. Este censo nao propoe nada. Ele so
pergunta ao repositorio, conceito a conceito:

    quem ESCREVE isto?      (o dono)
    quem so LE?             (consumidor)
    ha mais do que um?      (dono duplicado = risco de divergencia)
    nao ha nenhum?          (buraco honesto, e fica UNKNOWN)

AS DISTINCOES QUE ELE NAO PODE ACHATAR
--------------------------------------
    OWNER EXISTS  ≠  OWNER CONNECTED
    ESCREVER      ≠  LER
    MENCIONAR     ≠  USAR

Um ficheiro que cita `collection_run` num comentario nao e dono dele. Por isso
a medida separa escrita de leitura, e diz qual foi o sinal usado.

O QUE ELE NAO FAZ
-----------------
Nao cria schema. Nao propoe tabela. Nao decide quem DEVIA ser dono. Um censo
que ja recomenda deixou de medir.
"""
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
SAIDA = os.path.join(RAIZ, 'system-map', 'data', 'donos.generated.json')

# Os conceitos que a observabilidade vai precisar de citar. Para cada um:
#   ALVO      o que se procura no codigo
#   ESCRITA   os sinais que denunciam ESCRITA (nao mencao)
CONCEITOS = [
    {'ID': 'COLLECTION_RUN', 'ALVO': r'collection_run',
     'ESCRITA': [r'insert\s+into\s+\w*\.?collection_run', r'update\s+\w*\.?collection_run']},
    {'ID': 'RUN_MANIFEST', 'ALVO': r'RUN-MANIFEST',
     'ESCRITA': [r'open\([^)]*RUN-MANIFEST[^)]*[\'"]w', r'json\.dump\([^)]*manifest']},
    {'ID': 'CHECKPOINT', 'ALVO': r'checkpoint_coleta|coleta_checkpoint',
     'ESCRITA': [r'insert\s+into\s+\w*\.?checkpoint_coleta', r'def\s+gravar', r'def\s+salvar']},
    {'ID': 'RAW_ASSET', 'ALVO': r'raw_asset',
     'ESCRITA': [r'insert\s+into\s+\w*\.?raw_asset']},
    {'ID': 'DERIVED_ARTIFACT', 'ALVO': r'derived_artifact',
     'ESCRITA': [r'insert\s+into\s+\w*\.?derived_artifact']},
    {'ID': 'ADMISSION', 'ALVO': r'admissao|ADMISSION|READY',
     'ESCRITA': [r'def\s+admitir', r'def\s+julgar', r'READY\s*=']},
    {'ID': 'ORQUESTRADOR', 'ALVO': r'orquestrador',
     'ESCRITA': [r'def\s+despachar', r'subprocess\.(run|Popen)']},
    {'ID': 'RECEITAS', 'ALVO': r'receitas',
     'ESCRITA': [r'EXECUTORES\s*=', r'PLANOS\s*=']},
    {'ID': 'ROUTE_MODEL', 'ALVO': r'estradas-it\.model|ROUTE_CLASS',
     'ESCRITA': [r'json\.dump']},
    {'ID': 'SYSTEM_MAP', 'ALVO': r'architecture\.declared|state\.generated',
     'ESCRITA': [r'json\.dump']},
    {'ID': 'COST', 'ALVO': r'\bCUSTO\b|\bCOST\b|creditos|credits',
     'ESCRITA': [r'CUSTO\s*=', r'COST\s*=']},
    {'ID': 'ERRORS', 'ALVO': r'PARSE_ERROR|ERROR_CODE|FAILURE',
     'ESCRITA': [r'PARSE_ERROR\s*=', r'ERROR_CODE\s*=']},
    {'ID': 'COUNTS', 'ALVO': r'OBSERVATION_RESULT|CONTAGEM|COUNTS',
     'ESCRITA': [r'COUNTS\s*=', r'OBSERVATION_RESULT\s*=']},
    {'ID': 'HISTORY', 'ALVO': r'observations\.ndjson|runs\.ndjson',
     'ESCRITA': [r'[\'"]a[\'"]\s*\)', r'write\(']},
    {'ID': 'DURATION', 'ALVO': r'TEMPO_S|DURATION|duracao',
     'ESCRITA': [r'TEMPO_S\s*=', r'DURATION\s*=']},
]

EXTS = ('.py', '.mjs', '.js', '.sql')
# Gavetas que MEDEM ou PROVAM. Elas citam tudo por oficio, e por isso nunca
# contam como donas — senao o censo elegia o proprio instrumento.
INSTRUMENTO = ('system-map/', 'provas/', 'tests/')


def _ficheiros():
    r = subprocess.run(['git', 'ls-files'], cwd=RAIZ,
                       capture_output=True, text=True)
    return [p for p in r.stdout.splitlines() if p.endswith(EXTS)]


def _sem_comentarios(texto, rel):
    """⚠️ ISTO EXISTE PORQUE JA ME ENGANEI CINCO VEZES DA MESMA MANEIRA.

    Um ficheiro que EXPLICA porque nao escreve em `collection_run` contem a
    palavra `collection_run`. Contar o cabecalho como uso e transformar prosa
    em arquitetura."""
    if rel.endswith('.sql'):
        return '\n'.join(l for l in texto.splitlines()
                         if not l.strip().startswith('--'))
    return '\n'.join(l for l in texto.splitlines()
                     if not l.strip().startswith('#'))


def censo():
    fich = _ficheiros()
    corpo = {}
    for rel in fich:
        try:
            with open(os.path.join(RAIZ, rel), encoding='utf-8',
                      errors='ignore') as f:
                corpo[rel] = _sem_comentarios(f.read(), rel)
        except OSError:
            continue

    fora = []
    for c in CONCEITOS:
        alvo = re.compile(c['ALVO'], re.I)
        escrita = [re.compile(p, re.I) for p in c['ESCRITA']]
        escrevem, leem, instrumentos = [], [], []
        for rel, txt in corpo.items():
            if not alvo.search(txt):
                continue
            e_instr = any(rel.startswith(p) for p in INSTRUMENTO)
            if any(p.search(txt) for p in escrita):
                (instrumentos if e_instr else escrevem).append(rel)
            elif not e_instr:
                leem.append(rel)
            else:
                instrumentos.append(rel)

        # ⚠️ NAO PUBLICAR UNKNOWN QUE E ARTEFATO DA MINHA PROPRIA MEDIDA.
        # Excluo `system-map/`, `provas/` e `tests/` porque citam tudo por
        # oficio. Mas ha conceitos cujo dono legitimo VIVE la — o modelo de
        # estradas e o proprio System Map. Dizer UNKNOWN sobre eles seria
        # inventar um buraco que so existe porque eu tapei os olhos.
        if not escrevem and instrumentos:
            estado = 'DONO_E_INSTRUMENTO'
            nota = ('nenhum dono fora das gavetas de medida, e %d ficheiros de '
                    'medida escrevem. Para este conceito isso e o esperado: o '
                    'dono legitimo mora no instrumento. NAO e um buraco.'
                    % len(instrumentos))
        elif len(escrevem) == 1:
            estado, nota = 'UM_DONO', 'um so ficheiro escreve'
        elif len(escrevem) > 1:
            estado = 'DONO_DUPLICADO'
            nota = ('%d ficheiros escrevem. Nao e erro por si: pode ser um '
                    'dono canonico mais um legado. Mas e onde a verdade se '
                    'parte em duas se ninguem olhar.' % len(escrevem))
        elif leem:
            estado = 'SEM_DONO_MAS_LIDO'
            nota = ('ninguem escreve e %d leem. Ou o dono esta fora deste '
                    'repositorio, ou o dado vem de fora e ninguem o produz '
                    'aqui.' % len(leem))
        else:
            estado, nota = 'UNKNOWN', 'nem escrita nem leitura medidas'

        fora.append({
            'CONCEITO': c['ID'],
            'ESTADO': estado,
            'NOTA': nota,
            'ESCREVEM': sorted(escrevem),
            'LEEM': sorted(leem)[:12],
            'QUANTOS_LEEM': len(leem),
            'INSTRUMENTOS_QUE_CITAM': len(instrumentos),
            'COMO_FOI_MEDIDO': ('grep sem comentarios: escrita por padrao '
                                'declarado, leitura por mencao. E grosseiro de '
                                'proposito, e o mesmo para todos os conceitos '
                                '— criterio que muda por conceito deixa de '
                                'comparar.'),
        })
    return fora


def main():
    linhas = censo()
    por_estado = {}
    for l in linhas:
        por_estado[l['ESTADO']] = por_estado.get(l['ESTADO'], 0) + 1
    rel = {
        'SCHEMA': 'donos/v1',
        'O_QUE_E': ('quem JA responde por cada conceito que a observabilidade '
                    'vai precisar de citar. REUSE FIRST: medir antes de nomear '
                    'dono novo.'),
        'O_QUE_NAO_E': ('nao propoe schema, nao cria tabela, e nao diz quem '
                        'DEVIA ser dono. Um censo que ja recomenda deixou de '
                        'medir.'),
        'LEIS': [
            'OWNER EXISTS != OWNER CONNECTED',
            'ESCREVER != LER != MENCIONAR',
            'UNKNOWN != ZERO',
        ],
        'CONCEITOS': len(linhas),
        'POR_ESTADO': dict(sorted(por_estado.items())),
        'DETALHE': linhas,
    }
    with open(SAIDA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(rel, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('CONCEITOS %d · %s' % (len(linhas), por_estado))
    for l in linhas:
        print('  %-18s %-18s %s' % (l['CONCEITO'], l['ESTADO'],
                                    (l['ESCREVEM'] or ['—'])[0]))
    print('\nescrito em %s' % os.path.relpath(SAIDA, RAIZ).replace('\\', '/'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
