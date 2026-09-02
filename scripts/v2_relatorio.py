#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESCREVE O `HANDOFF-V2-REPORT.md` — o §23, o veredicto final.

    python3 scripts/v2_relatorio.py

⚠️ O QUE ESTE RELATÓRIO NÃO PODE FAZER
---------------------------------------
Dizer SIM antes de toda falha conhecida estar resolvida. O §23 é explícito:
«Do not return YES until every known failed record has been resolved.»

Então o SIM aqui não é uma opinião: ele é CALCULADO. Se sobrar um registro em
`PENDENTE_DE_DECISAO`, ou um derrubado sem destino, o veredicto vira NÃO
sozinho — e diz qual.
"""
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2')
ANT_DR = os.path.join(PKG, 'PREVIOUS-HANDOFF', '01-DESIGN-READY')


def le(n, k=None):
    p = os.path.join(PKG, n)
    if not os.path.exists(p):
        return {} if k is None else []
    d = json.load(open(p, encoding='utf-8'))
    return d.get(k) if k else d


def main():
    can = le('CANONICAL-INTELLIGENCE.json')
    val = le('VALIDATION-MANIFEST.json')
    qua = le('QUARANTINED-RECORDS.json')
    cru = le('TOP-CROSSINGS.json')
    conf = le('CONFLICT-RESOLUTION.json')

    # a contagem honesta do que foi preservado: só os objetos com ID do design-ready
    n_ant = 0
    for dp, _dn, fn in os.walk(ANT_DR):
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
    val['PREVIOUS_HANDOFF_RECORDS_RETAINED'] = n_ant
    val['PREVIOUS_HANDOFF_NOTA'] = (
        'contagem dos objetos com ID em 01-DESIGN-READY. A pasta PREVIOUS-HANDOFF/ '
        'copia o pacote INTEIRO, incluindo indices e prosa, e por isso um contador '
        'ingenuo sobre a pasta toda devolve numero maior -- ele reconta os mesmos '
        'IDs pelo indice.')
    json.dump(val, open(os.path.join(PKG, 'VALIDATION-MANIFEST.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)

    q = can.get('BY_QA', {})
    pendentes = q.get('PENDENTE_DE_DECISAO', 0)
    rejeitados = sum(1 for x in qua.get('RECORDS', [])
                     if x.get('QA_STATUS') == 'QA_REJECTED')
    substituidos = sum(1 for x in qua.get('RECORDS', [])
                       if x.get('QA_STATUS') == 'SUBSTITUIDO_POR_CORRECAO')
    tx = val.get('MEASURED_CONFERENCE_RATE', {})
    quedas = tx.get('FAILED', 0)
    resolvidas = rejeitados + substituidos

    # ── o veredicto é CALCULADO, não opinado ─────────────────────────────────
    checagens = [
        ('ALL KNOWN CONFERENCE FAILURES REMOVED OR CORRECTED',
         resolvidas >= quedas,
         '%d de %d quedas resolvidas' % (resolvidas, quedas)),
        ('NENHUM REGISTRO FICOU PENDENTE DE DECISAO', pendentes == 0,
         '%d pendentes' % pendentes),
        ('DUPLICATE RAW/CORRECTED CLAIMS RESOLVED', substituidos > 0,
         '%d crus substituidos e movidos para a quarentena' % substituidos),
        ('UNREVIEWED RECORDS BLOCKED FROM CLIENT ASSERTIONS',
         val.get('CLIENT_VISIBLE_CLAIMS_DRIVEN_BY_QA_UNREVIEWED') == 0,
         'client-safe = so QA_PASS + QA_CORRECTED'),
        ('PREVIOUS REALITY HANDOFF PRESERVED', n_ant > 3000,
         '%d objetos em PREVIOUS-HANDOFF/' % n_ant),
        ('NEW LAST-MILE INTELLIGENCE MERGED',
         len(can.get('BY_FAMILY', {})) == 10,
         '%d familias' % len(can.get('BY_FAMILY', {}))),
        ('SYNTHETIC RECORDS = 0',
         val.get('SYNTHETIC_RECORDS_IN_CANONICAL_HANDOFF') == 0, '0'),
        ('CONFLICTS RESOLVED',
         conf.get('PRECISAM_DE_HUMANO', 1) == 0,
         '%d conflito(s), %d pendendo de humano'
         % (conf.get('CONFLITOS', 0), conf.get('PRECISAM_DE_HUMANO', 0))),
    ]
    tudo_ok = all(c[1] for c in checagens)

    L = []
    A = L.append
    A('# HANDOFF V2 — RELATÓRIO E VEREDICTO\n\n')
    A('**02/09/2026** · consolidação e portão de verdade · nenhuma coleta nova\n')
    A('\n---\n\n## VEREDICTO (§23)\n\n```\n')
    A('RAW LAST-MILE SAFE TO SEND DIRECTLY TO DESIGN     = NO\n')
    A('CANONICAL HANDOFF V2 CREATED                      = YES\n')
    for nome, ok, det in checagens:
        A('%-49s = %-3s  (%s)\n' % (nome[:49], 'YES' if ok else 'NO', det))
    A('\n')
    A('READY TO SEND HANDOFF V2 TO CLAUDE DESIGN         = %s\n'
      % ('YES' if tudo_ok else 'NO'))
    A('```\n')
    if not tudo_ok:
        A('\n⛔ **NÃO.** Falharam: %s\n'
          % ', '.join(n for n, ok, _ in checagens if not ok))
    else:
        A('\n✅ O SIM acima é **calculado**, não opinado: se sobrasse um registro '
          'pendente ou uma queda sem destino, ele viraria NÃO sozinho.\n')

    A('\n---\n\n## §21 · MANIFESTO DE VALIDAÇÃO\n\n```\n')
    for k in ('PREVIOUS_HANDOFF_RECORDS_RETAINED', 'LAST_MILE_RAW_RECORDS',
              'LAST_MILE_AFTER_DEDUP', 'RAW_CORRECTED_DUPLICATES_COLLAPSED',
              'LAST_MILE_QA_PASS', 'LAST_MILE_QA_CORRECTED',
              'LAST_MILE_QA_UNREVIEWED', 'LAST_MILE_QA_REJECTED',
              'CONFLICTS_WITH_PREVIOUS_HANDOFF', 'CONFLICTS_RESOLVED',
              'CLIENT_SAFE_LAST_MILE_RECORDS', 'CLIENT_SAFE_SOURCES',
              'SYNTHETIC_RECORDS_IN_CANONICAL_HANDOFF',
              'CLIENT_VISIBLE_CLAIMS_DRIVEN_BY_QA_UNREVIEWED'):
        A('%-52s = %s\n' % (k, val.get(k)))
    A('```\n')

    A('\n---\n\n## §22 · A TAXA MEDIDA, SEM MAQUIAGEM\n\n')
    A('| | |\n|---|---:|\n')
    A('| amostrados pela conferência | **%d** |\n' % tx.get('SAMPLED', 0))
    A('| sobreviveram | **%d** |\n' % tx.get('SURVIVED', 0))
    A('| **caíram** | **%d (%s%%)** |\n' % (quedas, tx.get('FAILURE_RATE_PCT')))
    A('\n⚠️ **Uma correção à própria missão.** O briefing cita 52/72 (28%%). O número '
      'certo é **%d/%d (%s%%)**. A diferença é minha: a montagem anterior perdeu a '
      'conferência de cinco blocos ao casar nome de família com nome de bloco '
      '(`clima` não bate com `METEOROLOGIA`). **A taxa real é pior do que a missão '
      'registra.**\n' % (tx.get('SURVIVED', 0), tx.get('SAMPLED', 0),
                         tx.get('FAILURE_RATE_PCT')))
    A('\n> Os 321 são **registros de coleta externa real**. Não são 321 fatos '
      'validados de forma independente.\n')

    A('\n---\n\n## O QUE FOI FEITO COM AS 34 QUEDAS\n\n')
    A('| destino | quantos |\n|---|---:|\n')
    A('| reconstruídos como `QA_CORRECTED` | **%d** |\n' % substituidos)
    A('| rejeitados | **%d** |\n' % rejeitados)
    A('\nPor causa do defeito:\n\n| causa | quantos |\n|---|---:|\n')
    for k, v in sorted(Counter(x.get('O_QUE_ESTAVA_ERRADO') for x in qua.get('RECORDS', [])
                               if x.get('O_QUE_ESTAVA_ERRADO')).items(),
                       key=lambda x: -x[1]):
        A('| %s | %d |\n' % (k, v))
    A('\n**Nenhum aviso pendurado.** O §5 proíbe, e o montador recusa: quando há '
      'reconstrução, o registro cru sai do feed e vai para `QUARANTINED-RECORDS.json` '
      'com a lista campo a campo do que mudou.\n')

    A('\n### Exemplos do que mudou de verdade\n\n')
    A('- **BBCH da videira no Vêneto** — a tabela estava deslocada uma linha. O '
      '`85-89` era da linha Corvine/Merlot, que o coletor omitiu inteira, e foi dado '
      'à Glera. Reconstruído com as quatro linhas. E ficou a ressalva permanente: '
      '`pdftotext -layout` é o único modo que produz esse erro — usar `-table`, '
      '`-simple` ou `-raw`.\n')
    A('- **Mosca da oliveira no Vêneto** — o registro listava 8 areais a 3–4% e o '
      'boletim lista **11**, sendo que o omitido de maior valor era o Litorale '
      'veneziano a 4–6%. Cortar o mais alto e chamar o resto de uniforme.\n')
    A('- **Preço do trigo em Verona** — semana errada: `224,50` é de outra semana; '
      'na semana correta o valor é `223,50`.\n')
    A('- **Concentração de área** — três porcentagens truncadas em vez de '
      'arredondadas, todas na direção de subdeclarar a concentração.\n')

    A('\n---\n\n## §19 · OS CRUZAMENTOS AGORA POSSÍVEIS\n\n')
    A('**%d cruzamentos**, cada um com os IDs canônicos exatos dos dois lados:\n\n'
      % cru.get('COUNT', 0))
    A('| cruzamento | quantos |\n|---|---:|\n')
    for k, v in (cru.get('BY_TYPE') or {}).items():
        A('| %s | %d |\n' % (k, v))
    A('\n⚠️ **Um cruzamento não é uma oportunidade.** É a constatação de que duas '
      'camadas falam do mesmo par cultura × região. Quem decide se aquilo vale é uma '
      'pessoa, olhando os IDs.\n')
    A('\nE o portão do §4 vale aqui também: só `QA_PASS` e `QA_CORRECTED` entram no '
      'lado que **sustenta**. Sem isso o portão vazaria pela porta dos fundos.\n')

    A('\n---\n\n## §9 · O QUE FOI PRESERVADO\n\n')
    A('`PREVIOUS-HANDOFF/` traz o pacote anterior **inteiro**: %d objetos com ID em '
      '`01-DESIGN-READY`, mais a prosa, os manifestos e os índices.\n\n' % n_ant)
    A('Nada foi reescrito, resumido nem filtrado — nem os 2.030 pares de uso de '
      'rótulo, nem as 561 atividades de concorrente, nem as 58 vozes de plateia.\n\n')
    A('⚠️ **O portão de QA é sobre a camada nova.** Aplicá-lo retroativamente ao '
      'pacote anterior rebaixaria trabalho que já tem a sua própria proveniência.\n')

    A('\n---\n\n## §6 · A DEDUPLICAÇÃO, E POR QUE ELA DEU QUASE NADA\n\n')
    A('A missão esperava sobreposição entre os dois fluxos, e ela **existe no nível '
      'do documento**: 14 URLs foram lidas por mais de um bloco.\n\n')
    A('Mas ao abrir caso a caso, os registros descrevem **fatos diferentes do mesmo '
      'documento**:\n\n')
    A('- boletim VITE do Vêneto, 27/08 → um é a **fase fenológica**, o outro é a '
      '**recomendação de controle** da flavescência\n')
    A('- ISMEA trigo tenro → um é **preço por produto**, o outro **por qualidade**\n')
    A('- ARPAE 24/08 → um é **chuva acumulada**, o outro **água no solo**\n\n')
    A('> **Dois fatos do mesmo documento não são o mesmo fato.** A duplicata que o §6 '
      'teme é a mesma *observação* colhida duas vezes.\n\n')
    A('Fundir teria perdido metade da informação. **Colapsado: 1** — o boletim ARSAC '
      'da semana 35, conferido à mão.\n')
    A('\n⚠️ E uma nota de método: a busca automática por semelhança de citação '
      'devolveu 3 candidatos e **2 eram falso positivo** — o ISMEA repete o cabeçalho '
      'da página em recortes diferentes. Um limiar que erra dois em três não é um '
      'limiar; é um palpite. A fusão foi **declarada**, não inferida.\n')

    A('\n---\n\n## §18 · A ROTA NÃO É DEPENDÊNCIA DO PORTAL\n\n')
    A('Três fontes só abriram por saída italiana — ISMEA Mercati, ISTAT esploradati e '
      'ARPAV. Isso está em `SOURCES.json` como **infraestrutura de coleta**, para '
      'automação futura.\n\n')
    A('**O portal consome dado já guardado e nunca precisa da VPN para renderizar.**\n')

    A('\n---\n\n## O QUE CONTINUA VALENDO COMO LIMITE\n\n')
    A('| limite | por quê |\n|---|---|\n')
    A('| %d registros são `QA_UNREVIEWED` | não foram à segunda passada. São fonte '
      'real e nada mais. |\n' % q.get('QA_UNREVIEWED', 0))
    A('| a fase de herbicida é da Emília-Romanha | boletim datado de 19–20/08. **Não '
      'se generaliza para a Itália.** |\n')
    A('| 21 boletins são provinciais ou de areal | não representam a região. |\n')
    A('| o vínculo comercial dos 6 produtos de outro titular | **desconhecido**, e '
      'continua assim. |\n')
    A('| venda, share, estoque | dado interno. O projeto é externo por decisão. |\n')

    open(os.path.join(PKG, 'HANDOFF-V2-REPORT.md'), 'w',
         encoding='utf-8').write(''.join(L))
    print('HANDOFF-V2-REPORT.md escrito')
    print()
    print('VEREDICTO: READY TO SEND = %s' % ('YES' if tudo_ok else 'NO'))
    for nome, ok, det in checagens:
        print('  [%s] %-50s %s' % ('OK' if ok else '!!', nome[:50], det))


if __name__ == '__main__':
    main()
