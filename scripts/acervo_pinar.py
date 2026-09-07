#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PINA O ACERVO — descobre os insumos e escreve o manifesto imutável.

    python3 scripts/acervo_pinar.py

Roda UMA VEZ por safra de acervo, à mão. NÃO entra na cadeia: a cadeia lê o
manifesto pinado, nunca redescobre. Redescobrir a cada build faria o pacote
mudar quando um ref remoto mexesse — e aí o pacote deixaria de ser função do
seu insumo declarado.

    O QUE A CADEIA LÊ TEM DE SER IMUTÁVEL, OU O DETERMINISMO É DECORATIVO.

Os refs de onde o acervo vem, e por quê:

    sintonia/canonical          as transcrições (convegni, vídeo, instagram,
                                voz-áudio) e o corpus de 763 materiais científicos
    claude/eame-meta-competitor os anúncios Meta com first/last_observed
    HEAD (esta linhagem)        SENSOR-PILOT e ES-T8-001, que já vivem aqui

Nenhum destes é ancestral do outro: `integration-acervo-portal-v1` e
`opportunity-commercial-priority-v1` não têm merge-base. Por isso o endereço do
insumo precisa carregar o COMMIT, e não só o caminho.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data', 'acervo', 'ACERVO-SOURCES-V1.json')

# ref -> (rótulo humano, o que se busca ali)
REFS = [
    ('refs/remotes/origin/sintonia/canonical', 'sintonia/canonical'),
    ('refs/remotes/origin/claude/eame-meta-competitor', 'claude/eame-meta-competitor'),
    ('HEAD', 'HEAD'),
]

# (regex do caminho, FAMILY, ROLE) — a ordem manda: o primeiro que casa vence.
REGRAS = [
    (r'^data/samples/META-EAME/META-ADS-ENTITIES-EAME-V1\.json$', 'ADS', 'ENTITIES'),
    (r'^data/samples/META-EAME/META-ADS-EVENTS-EAME-V1\.json$', 'ADS', 'EVENTS'),
    (r'^data/samples/RESEARCHER-CORPUS-EAME-V1\.json$', 'SCIENCE', 'CORPUS'),
    (r'^data/samples/IT-(CONVEGNO|VIDEO)-V\d/falas/[^/]+\.json$', 'TRANSCRIPTS', 'FALA'),
    (r'^data/samples/IT-CONVEGNO-V1/IT-CONVEGNO-V1\.json$', 'TRANSCRIPTS', 'MANIFEST'),
    (r'^data/samples/IT-CONVEGNO-V2/IT-CONVEGNO-RESGATE-V2\.json$', 'TRANSCRIPTS', 'MANIFEST'),
    (r'^data/samples/IT-VIDEO-V1/IT-VIDEO-FALAS-V1\.json$', 'TRANSCRIPTS', 'MANIFEST'),
    (r'^data/samples/IT-INSTAGRAM-V\d/IT-INSTAGRAM-TRANSCRICOES-V\d\.json$',
     'TRANSCRIPTS', 'BATCH'),
    # ⚠️ `IT-VOZ-AUDIO-LOCAIS-V2.json` FALTAVA, e a regra so pedia TRANSCRICOES.
    # Sao 10 objetos, 8 com fala e 129.566 caracteres — os boletins semanais da
    # oliveira de agosto/2026, Diachem em Voghera, Agrion no Piemonte, arroz e
    # grao duro em Foggia. A regra estreita nao dava erro: dava silencio.
    #
    #     REGRA DE DESCOBERTA QUE NAO ACHA NAO RECLAMA. SO ENTREGA MENOS.
    (r'^data/samples/IT-VOZ-AUDIO-V\d/IT-VOZ-AUDIO-(TRANSCRICOES|LOCAIS)-V\d\.json$',
     'TRANSCRIPTS', 'BATCH'),
    # ── ENRIQUECIMENTO ──────────────────────────────────────────────────────
    # Estes DOIS carregam titulo, canal, pais do fato e CASE_ID dos videos —
    # que os lotes de transcricao nao carregam. Sao lidos SO por metadado:
    # ambos tambem tem campo TRANSCRIPT, e conta-lo seria contar a mesma fala
    # duas vezes.
    #
    #     ARQUIVO DE ENRIQUECIMENTO ENTRA PELO QUE ELE SABE A MAIS,
    #     NUNCA PELO QUE ELE REPETE.
    (r'^data/samples/SENSOR-PILOT/MEDICAO\.json$', 'TRANSCRIPTS', 'ENRICHMENT'),
    (r'^data/samples/ES-T8-001-videos\.json$', 'TRANSCRIPTS', 'ENRICHMENT'),
    (r'^data/samples/SENSOR-PILOT/TRANSCRICOES-[A-E]\.json$', 'TRANSCRIPTS', 'BATCH'),
    (r'^data/samples/ES-T8-001-transcricoes\.json$', 'TRANSCRIPTS', 'BATCH'),
]


def git(*a):
    p = subprocess.run(['git'] + list(a), cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise SystemExit('git ' + ' '.join(a) + ':\n' +
                         p.stderr.decode('utf-8', 'replace'))
    return p.stdout


def classifica(path):
    for rx, fam, papel in REGRAS:
        if re.match(rx, path):
            return fam, papel
    return None, None


def chave(fam, path):
    """Chave estável e legível — o nome do arquivo diz de onde veio."""
    n = re.sub(r'[^A-Z0-9]+', '_', path.upper().replace('DATA/SAMPLES/', ''))
    return (fam + '__' + n.strip('_'))[:120]


def main():
    achados = {}          # path -> registro (o primeiro ref que tiver vence)
    ordem_ref = []
    for ref, rotulo in REFS:
        try:
            commit = git('rev-parse', ref).decode().strip()
        except SystemExit:
            print('  ref ausente, ignorado: %s' % rotulo)
            continue
        ordem_ref.append((rotulo, commit))
        for linha in git('ls-tree', '-r', '--long', commit,
                         '--', 'data/samples').decode('utf-8', 'replace').splitlines():
            m = re.match(r'\S+\s+blob\s+(\S+)\s+(\d+)\s+(.+)$', linha)
            if not m:
                continue
            blob, tam, path = m.group(1), int(m.group(2)), m.group(3)
            if path in achados:
                continue
            fam, papel = classifica(path)
            if not fam:
                continue
            bruto = git('cat-file', 'blob', blob)
            achados[path] = {
                'KEY': chave(fam, path), 'FAMILY': fam, 'ROLE': papel,
                'REF': rotulo, 'COMMIT': commit, 'PATH': path, 'BLOB': blob,
                'BYTES': tam, 'SHA256': hashlib.sha256(bruto).hexdigest(),
            }

    fontes = sorted(achados.values(), key=lambda s: (s['FAMILY'], s['PATH']))
    dup = [k for k, n in __import__('collections').Counter(
        s['KEY'] for s in fontes).items() if n > 1]
    if dup:
        raise SystemExit('CHAVE DUPLICADA no manifesto: %s' % dup)

    corpo = {
        'DATASET': 'ACERVO-SOURCES-V1',
        'SCHEMA_VERSION': 'V1',
        'O_QUE_ISTO_E': (
            'o endereco IMUTAVEL de cada insumo de acervo que atravessa para o '
            'pacote. Endereco = (COMMIT, PATH, BLOB) + SHA256 do conteudo.'),
        'O_QUE_ISTO_NAO_E': [
            'nao e copia do acervo: o byte continua vivendo no seu ref de origem',
            'nao e descoberta em tempo de build: a cadeia LE isto, nunca reescreve',
            'nao prova que o insumo esta correto — prova que e ESTE insumo',
        ],
        'LEI': ('um caminho sem ref nao e endereco. Dois refs desta arvore nao tem '
                'merge-base: o mesmo caminho pode ser outro arquivo noutro ref.'),
        'REFS_LIDOS': [{'REF': r, 'COMMIT': c} for r, c in ordem_ref],
        'PRECEDENCIA': ('o primeiro ref da lista que contiver o caminho vence. '
                        'Assim o acervo canonico manda, e HEAD so completa.'),
        'COUNT_TOTAL': len(fontes),
        'BY_FAMILY': dict(sorted(__import__('collections').Counter(
            s['FAMILY'] for s in fontes).items())),
        'BY_REF': dict(sorted(__import__('collections').Counter(
            s['REF'] for s in fontes).items())),
        'BYTES_TOTAL': sum(s['BYTES'] for s in fontes),
        'SOURCES': fontes,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('== ACERVO PINADO ==')
    for r, c in ordem_ref:
        print('  %-40s %s' % (r, c[:12]))
    print('  arquivos : %d' % len(fontes))
    for fam, n in corpo['BY_FAMILY'].items():
        print('    %-14s %3d' % (fam, n))
    print('  bytes    : %s' % f'{corpo["BYTES_TOTAL"]:,}')
    print('  gravado  : %s' % SAIDA)


if __name__ == '__main__':
    sys.exit(main())
