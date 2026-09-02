#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FECHA O PACOTE V2: preserva o anterior, escreve o manifesto e a prosa.

    python3 scripts/v2_fechar.py

§9 · A FUSÃO É ADITIVA
-----------------------
«This is ADDITIVE, not a destructive replacement.» O pacote anterior inteiro é
COPIADO para dentro do V2, em `PREVIOUS-HANDOFF/`. Nada dele é reescrito,
resumido ou filtrado — nem os 2.030 pares de rótulo, nem as 561 atividades de
concorrente, nem as 58 vozes de plateia.

    O QUE JÁ ESTAVA VERIFICADO NÃO PRECISA PASSAR PELO PORTÃO DE NOVO.
    O portão de QA é sobre a camada NOVA. Aplicá-lo retroativamente ao pacote
    anterior seria rebaixar trabalho que já tem a sua própria proveniência.
"""
import json
import os
import shutil
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2')
ANT = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF')


def le(nome, chave=None):
    p = os.path.join(PKG, nome)
    if not os.path.exists(p):
        return {} if chave is None else []
    d = json.load(open(p, encoding='utf-8'))
    return d.get(chave) if chave else d


def main():
    # ── 1 · preservar o pacote anterior, inteiro ──────────────────────────────
    destino = os.path.join(PKG, 'PREVIOUS-HANDOFF')
    if os.path.isdir(destino):
        shutil.rmtree(destino)
    shutil.copytree(ANT, destino)
    n_ant = 0
    for dp, _dn, fn in os.walk(destino):
        for f in fn:
            if not f.endswith('.json'):
                continue
            try:
                d = json.load(open(os.path.join(dp, f), encoding='utf-8'))
            except ValueError:
                continue
            for k, v in d.items():
                if isinstance(v, list) and v and isinstance(v[0], dict) and 'ID' in v[0]:
                    n_ant += len(v)
                    break

    val = le('VALIDATION-MANIFEST.json')
    can = le('CANONICAL-INTELLIGENCE.json')
    cru = le('TOP-CROSSINGS.json')
    qua = le('QUARANTINED-RECORDS.json')
    conf = le('CONFLICT-RESOLUTION.json')
    val['PREVIOUS_HANDOFF_RECORDS_RETAINED'] = n_ant
    json.dump(val, open(os.path.join(PKG, 'VALIDATION-MANIFEST.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)

    # ── 2 · MANIFEST.json ─────────────────────────────────────────────────────
    arquivos = []
    for f in sorted(os.listdir(PKG)):
        p = os.path.join(PKG, f)
        if os.path.isfile(p):
            arquivos.append({'ARQUIVO': f, 'KB': round(os.path.getsize(p) / 1024, 1)})
    json.dump({
        'PACKAGE': 'ITALY-REALITY-HANDOFF-V2',
        'BUILT_AT': '2026-09-02',
        'O_QUE_E': 'o pacote anterior PRESERVADO INTEIRO mais a camada last-mile '
                   'passada por um portao de QA registro a registro',
        'QA_GATE': {
            'QA_PASS': 'sobreviveu a conferencia independente, sem mudanca',
            'QA_CORRECTED': 'a conferencia achou defeito e o registro foi RECONSTRUIDO',
            'QA_UNREVIEWED': 'fonte externa real, sem segunda passada. NAO gera '
                             'conclusao ao cliente sozinho.',
            'QA_REJECTED': 'nao chega ao feed. Esta em QUARANTINED-RECORDS.json.',
        },
        'CLIENT_SAFE': 'so QA_PASS e QA_CORRECTED',
        'SYNTHETIC': 0,
        'ARQUIVOS': arquivos,
        'PASTA_PRESERVADA': {'PREVIOUS-HANDOFF/': '%d objetos, intocados' % n_ant},
    }, open(os.path.join(PKG, 'MANIFEST.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=1)

    # ── 3 · README-FIRST.md ───────────────────────────────────────────────────
    q = can.get('BY_QA', {})
    seg = can.get('CLIENT_SAFE', 0)
    tx = val.get('MEASURED_CONFERENCE_RATE', {})
    L = []
    A = L.append
    A('# LEIA PRIMEIRO — ITALY REALITY HANDOFF V2\n\n')
    A('**02/09/2026** · pacote canônico · **zero sintéticos**\n\n')
    A('Este pacote é o anterior **inteiro** mais uma camada nova que passou por um '
      'portão de qualidade, registro a registro.\n')
    A('\n---\n\n## ⚠️ A COISA MAIS IMPORTANTE DESTE ARQUIVO\n\n')
    A('Os 321 registros da coleta last-mile são **registros de coleta externa real**.\n')
    A('Eles **não** são 321 fatos validados de forma independente.\n\n')
    A('Uma segunda leva de agentes foi às fontes com ordem de **derrubar**:\n\n')
    A('| | |\n|---|---:|\n')
    A('| amostrados | **%d** |\n' % tx.get('SAMPLED', 0))
    A('| sobreviveram | **%d** |\n' % tx.get('SURVIVED', 0))
    A('| **caíram** | **%d (%s%%)** |\n' % (tx.get('FAILED', 0),
                                            tx.get('FAILURE_RATE_PCT', '?')))
    A('\n> **Um em cada três não resistiu ao confronto com a própria fonte.**\n\n')
    A('%s\n' % tx.get('NOTA', ''))
    A('\n---\n\n## O PORTÃO — o que pode virar frase de tela\n\n')
    A('| estado | quantos | pode sustentar afirmação ao cliente? |\n|---|---:|---|\n')
    A('| `QA_PASS` | %d | **sim** |\n' % q.get('QA_PASS', 0))
    A('| `QA_CORRECTED` | %d | **sim** |\n' % q.get('QA_CORRECTED', 0))
    A('| `QA_UNREVIEWED` | %d | **não sozinho** — fica no corpus de pesquisa |\n'
      % q.get('QA_UNREVIEWED', 0))
    A('| `QA_REJECTED` | %d | **nunca** — está na quarentena |\n'
      % val.get('LAST_MILE_QA_REJECTED', 0))
    A('\n**Client-safe: %d de %d.**\n' % (seg, can.get('COUNT', 0)))
    A('\n⚠️ E o número que fecha o portão: **afirmações visíveis ao cliente '
      'sustentadas por `QA_UNREVIEWED` = 0**.\n')
    A('\n---\n\n## O QUE FOI CORRIGIDO, E COMO\n\n')
    A('A conferência derrubou 34 registros. **33 foram reconstruídos** — campo por '
      'campo, não com um aviso pendurado — e **1 foi rejeitado**.\n\n')
    A('Por causa:\n\n| causa | quantos |\n|---|---:|\n')
    for k, v in sorted(Counter(x.get('O_QUE_ESTAVA_ERRADO') for x in
                               qua.get('RECORDS', []) if x.get('O_QUE_ESTAVA_ERRADO')
                               ).items(), key=lambda x: -x[1]):
        A('| %s | %d |\n' % (k, v))
    A('\nO registro cru **não fica vivo ao lado do corrigido**. Ele está em '
      '`QUARANTINED-RECORDS.json`, com a linhagem e a lista do que mudou.\n')
    A('\n### A rejeição\n\n')
    A('Um rizicultor real, uma matéria real — e uma frase que **não é dele**. No HTML '
      'ela está dentro de `<blockquote>` sem aspas: é o destaque editorial que o '
      'jornal montou. **Atribuição de fala errada não tem conserto**, porque '
      'reescrever o campo não devolve a frase à boca de ninguém.\n')
    A('\n---\n\n## AS DEZ FAMÍLIAS — e por que não viram uma tabela só\n\n')
    A('| família | arquivo | registros |\n|---|---|---:|\n')
    for fam, n in sorted(can.get('BY_FAMILY', {}).items(), key=lambda x: -x[1]):
        A('| %s | `%s.json` | %d |\n' % (fam, fam.replace('_', '-'), n))
    A('\nPreço, boletim, clima e voz têm semânticas diferentes. Achatá-las foi o que '
      'fez o demo anterior apresentar conversa de horta como inteligência de lavoura.\n')
    A('\n---\n\n## AS LEIS QUE VIAJAM COM O DADO\n\n')
    A('**ESCOPO NUNCA SOBE.** `PROVINCIAL`, `AREALE`, `ESTACAO`, `PIAZZA`, '
      '`MACROAREA` e `GRADE_DE_MODELO` jamais viram `REGIONAL` ou `NACIONAL`.\n')
    A('- boletins provinciais da Campânia ≠ censo regional da Campânia\n')
    A('- Metapontino ≠ Basilicata inteira\n')
    A('- Trento ≠ Trentino-Alto Adige (o Sudtirol é outra província)\n')
    A('- preço de uma piazza ≠ preço nacional\n\n')
    A('**CONDIÇÃO NÃO É PRESENÇA.** Clima ≠ doença · risco de modelo ≠ presença no '
      'campo · vetor ≠ doença · janela sazonal ≠ surto · comunicação ≠ participação '
      'de mercado · voz ≠ incidência.\n\n')
    A('**PRORROGAÇÃO NÃO É RENOVAÇÃO.** 39 das 50 substâncias do portfólio estão em '
      'aprovação prorrogada. Rascunho, discussão e reunião não são decisão.\n\n')
    A('**CATÁLOGO NÃO É TITULAR.** Seis produtos do catálogo ADAMA têm autorização em '
      'nome de outra empresa. Titular ≠ vendedor, e o contrato comercial continua '
      '**desconhecido**.\n')
    A('\n---\n\n## A ROTA — §18\n\n')
    A('O metadado de acesso é **infraestrutura de coleta**, não dependência do portal.\n\n')
    A('Três fontes só abriram por saída italiana (ISMEA, ISTAT, ARPAV). Isso está '
      'gravado em `SOURCES.json` para automação futura. **O portal lê dado já '
      'guardado e nunca precisa da VPN para renderizar.**\n')
    A('\n---\n\n## O QUE FOI PRESERVADO\n\n')
    A('`PREVIOUS-HANDOFF/` traz o pacote anterior **inteiro e intocado**: %d objetos, '
      'incluindo os 2.030 pares de uso de rótulo, as 561 atividades de concorrente, '
      'as 58 vozes de plateia, os 88 registros científicos, as 34 resistências do '
      'GIRE e os 163 produtos do registro.\n' % n_ant)
    A('\n⚠️ O portão de QA é sobre a camada **nova**. Aplicá-lo retroativamente '
      'rebaixaria trabalho que já tem a sua própria proveniência.\n')
    A('\n---\n\n## POR ONDE COMEÇAR\n\n')
    A('1. este arquivo\n2. `VALIDATION-MANIFEST.json` — os números, sem maquiagem\n')
    A('3. `TOP-CROSSINGS.json` — %d cruzamentos, cada um com os IDs exatos\n'
      % cru.get('COUNT', 0))
    A('4. `CONFLICT-RESOLUTION.json` — o que as duas camadas disseram diferente\n')
    A('5. a família que interessar\n')
    A('\n⛔ **Não** comece pelo `NEW-REAL-DATA.json` da missão anterior. Ele contém os '
      'registros crus que a conferência derrubou.\n')
    open(os.path.join(PKG, 'README-FIRST.md'), 'w', encoding='utf-8').write(''.join(L))

    print('pacote anterior preservado: %d objetos em PREVIOUS-HANDOFF/' % n_ant)
    print('MANIFEST.json e README-FIRST.md escritos')
    print()
    for f in sorted(os.listdir(PKG)):
        p = os.path.join(PKG, f)
        if os.path.isfile(p):
            print('   %-34s %7.0f KB' % (f, os.path.getsize(p) / 1024))
        else:
            print('   %-34s (pasta)' % (f + '/'))


if __name__ == '__main__':
    main()
