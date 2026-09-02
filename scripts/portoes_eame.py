#!/usr/bin/env python3
"""OS PORTÕES DO EAME — derivados da matriz, nunca afirmados à mão.

Este arquivo existe por causa de uma contradição que EU publiquei. Na mesma
rodada, o mesmo relatório disse:

    LOCATION_CONTRACT_COMPLETE   = NO   (quatro lacunas abertas)
    EAME_COLLECTION_ENTRY_GATE   = READY

As duas não podem ser verdade juntas. O portão se chama *collection entry
gate* — o portão por onde se passa ANTES de coletar —, e toda coleta que
produza documento produz documento com lugar de fato. Um portão de coleta
não fica READY com o contrato de localização em NO.

O erro não foi de medição: as cicatrizes estavam medidas certo. Foi de
NOME. Um nome só estava fazendo dois trabalhos:

  · a engenharia da IMPORTAÇÃO DO CATÁLOGO, que é registro regulatório,
    é SQL idempotente sobre chave natural, não gasta rota paga, não coleta
    rede social e NÃO tem lugar de fato nenhum; e

  · a entrada da COLETA EM GERAL, que produz conteúdo com lugar de fato.

O primeiro está pronto. O segundo não. Chamar os dois pelo mesmo nome fez
READY significar "o EAME inteiro pode coletar", que é falso.

A correção não é rebaixar nem promover nada: é separar os dois portões e
DERIVAR o estado de cada um das cicatrizes de que ele depende. Um portão
não pode mais ser declarado READY por quem escreve o relatório.

    python3 scripts/portoes_eame.py
    python3 scripts/portoes_eame.py --build
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
from cicatrizes_brasil import monta as monta_cicatrizes           # noqa: E402

SAIDA = os.path.join(RAIZ, 'data', 'samples', 'PORTOES-EAME.json')
RAW_ES = os.path.join(RAIZ, 'data', 'samples', 'RAW-GATE-ES.json')


# ── DE QUE CADA PORTÃO DEPENDE ────────────────────────────────────────
# Por FAMÍLIA de cicatriz, não por ID: assim uma cicatriz nova entra no
# portão certo sozinha, e ninguém precisa lembrar de acrescentá-la.
PORTOES = {
 'CATALOG_IMPORT_ENGINEERING_GATE': {
   'PERGUNTA': 'a engenharia de importar o catálogo regulatório espanhol está pronta?',
   'O_QUE_ELE_COBRE':
     'escrever registro_regulatorio e registro_uso a partir de uma fonte oficial, '
     'de forma idempotente sobre chave natural, sem gastar rota paga e sem coletar '
     'rede social.',
   'O_QUE_ELE_NAO_COBRE':
     'qualquer coleta que produza documento com LUGAR DE FATO. Um registro '
     'regulatório não tem lugar de fato: o país dele é o Estado que registrou, '
     'e isso é lado da FONTE. Por isso as lacunas de localização não o tocam.',
   'FAMILIAS': ['IDENTIDADE', 'PROVENIENCIA', 'TEMPO', 'AUSENCIA',
                'ISOLAMENTO', 'METODO', 'LOCALIZACAO'],
 },
 'EAME_COLLECTION_ENTRY_GATE': {
   'PERGUNTA': 'o EAME pode abrir coleta em geral?',
   'O_QUE_ELE_COBRE':
     'TODA coleta — inclusive a que produz conteúdo com lugar de fato, e a que '
     'gasta rota paga.',
   'O_QUE_ELE_NAO_COBRE':
     'nada da lista. É o portão mais abrangente que existe aqui, e é por isso '
     'que READY nele significa mesmo "o EAME pode coletar".',
   'FAMILIAS': ['IDENTIDADE', 'PROVENIENCIA', 'TEMPO', 'AUSENCIA', 'ISOLAMENTO',
                'METODO', 'LOCALIZACAO', 'LOCALIZACAO_CONFERENCIA',
                'RELEVANCIA', 'UNIDADE_ANALITICA', 'RESILIENCIA'],
 },
}

# ── OS CONTRATOS, TAMBÉM DERIVADOS ────────────────────────────────────
# Um contrato é COMPLETE quando toda cicatriz das famílias dele está PROVED.
# Mesma regra dos portões, e pela mesma razão: enquanto isto era uma frase
# num documento, ele podia dizer YES ao lado de uma lacuna aberta — e disse.
CONTRATOS = {
 'LOCATION_CONTRACT_COMPLETE': ['LOCALIZACAO', 'LOCALIZACAO_CONFERENCIA'],
 'RELEVANCE_CONTRACT_COMPLETE': ['RELEVANCIA'],
 'PROVENANCE_CONTRACT_COMPLETE': ['PROVENIENCIA'],
 'IDENTITY_CONTRACT_COMPLETE': ['IDENTIDADE'],
 'TEMPORAL_CONTRACT_COMPLETE': ['TEMPO'],
 'UNKNOWN_STATE_CONTRACT_COMPLETE': ['AUSENCIA'],
 'COUNTRY_ISOLATION_COMPLETE': ['ISOLAMENTO'],
 'ANALYTICAL_UNIT_CONTRACT_COMPLETE': ['UNIDADE_ANALITICA'],
 'RESILIENCE_CONTRACT_COMPLETE': ['RESILIENCIA'],
 'METHOD_CONTRACT_COMPLETE': ['METODO'],
}

# LOCATION é parte do COLLECTION ENTRY GATE. A resposta está na linha acima
# — LOCALIZACAO_CONFERENCIA está na lista dele —, e não numa frase de
# documento que alguém possa reescrever sem que nada reprove.
LOCATION_IS_PART_OF_COLLECTION_ENTRY_GATE = 'YES'


def estados_por_familia(cic):
    d = {}
    for c in cic:
        d.setdefault(c['FAMILIA'], []).append(c)
    return d


def avalia(porta, familias):
    """READY só quando TODA cicatriz de TODA família dele está PROVED."""
    bloqueadores = []
    for f in porta['FAMILIAS']:
        for c in familias.get(f, []):
            if c['EAME_STATUS'] != 'PROVED':
                bloqueadores.append({
                    'ID': c['ID'], 'FAMILIA': f, 'ESTADO': c['EAME_STATUS'],
                    'GAP': c['GAP'], 'ACAO_MINIMA': c['MINIMAL_ACTION']})
    cobertas = sum(len(familias.get(f, [])) for f in porta['FAMILIAS'])
    return {
        'PERGUNTA': porta['PERGUNTA'],
        'O_QUE_ELE_COBRE': porta['O_QUE_ELE_COBRE'],
        'O_QUE_ELE_NAO_COBRE': porta['O_QUE_ELE_NAO_COBRE'],
        'FAMILIAS': porta['FAMILIAS'],
        'CICATRIZES_COBERTAS': cobertas,
        'CICATRIZES_PROVED': cobertas - len(bloqueadores),
        'ESTADO': 'READY' if not bloqueadores else 'PARTIAL',
        'BLOQUEADORES': bloqueadores,
    }


def raw_es():
    with open(RAW_ES, encoding='utf-8') as f:
        return json.load(f)


def monta():
    cic = monta_cicatrizes()['CICATRIZES']
    fam = estados_por_familia(cic)
    portoes = {k: avalia(v, fam) for k, v in PORTOES.items()}

    contratos = {}
    for nome, familias in CONTRATOS.items():
        abertas = [c['ID'] for f in familias for c in fam.get(f, [])
                   if c['EAME_STATUS'] != 'PROVED']
        contratos[nome] = {
            'COMPLETO': 'YES' if not abertas else 'NO',
            'FAMILIAS': familias,
            'ABERTAS': abertas,
        }
    r = raw_es()

    # O gate do RAW não é derivável daqui: é medição de outra máquina. O que
    # esta função faz é RECUSAR-SE a inventá-lo, e passar adiante o que veio.
    #
    # Mas o artefato traz DUAS coisas que dizem a mesma verdade: os números e
    # o campo ESTADO. Dois donos da mesma afirmação é o defeito que este
    # repositório persegue, e aqui ele teria uma forma particularmente ruim —
    # alguém escrever ESTADO='CLOSED' num arquivo e o portão de importação
    # abrir sem que nenhum número tivesse mudado.
    #
    # Por isso o estado é DERIVADO dos números, e o campo declarado só é
    # aceito quando concorda com eles. Discordância não é resolvida em
    # silêncio: vira DIVERGENTE, e nada abre.
    raw_fechado = (r['ALREADY_PRESENT_VERIFIED'] == r['EXPECTED']
                   and r['FAILED_WITH_REASON'] == 0
                   and r['HASH_MISMATCH'] == 0 and r['CONFLICT'] == 0
                   and r.get('ORFAOS_NO_BUCKET', 0) == 0
                   and r.get('DO_PLANO_AUSENTES', 0) == 0)
    raw_derivado = 'CLOSED' if raw_fechado else 'OPEN_EXTERNAL_REPAIR'

    # PRESENÇA != CONTEÚDO CONFERIDO. O gate acima responde à presença — é o
    # que os números medem. O conteúdo é outra pergunta, e o artefato do
    # handoff a responde separado: dos 196 presentes, 11 tiveram sha256
    # reconferido por download+hash e 1 nunca teve o conteúdo conferido em
    # execução nenhuma — justamente o que recebeu 520.
    #
    # Este segundo gate NÃO entra em IMPORT_CAN_BE_NEXT_MISSION: importar
    # organiza os ponteiros para a evidência, e um ponteiro para bytes ainda
    # não reconferidos continua sendo o ponteiro certo. O que ele bloqueia é
    # AFIRMAR que o round-trip de evidência está provado — e é por isso que
    # ele aparece no relatório em vez de ficar implícito.
    pnc = r.get('PRESENCA_NAO_E_CONTEUDO') or {}
    # O gate do CONTEÚDO também é derivado, e da medição integral — não do
    # campo que o artefato declara. A medição baixou cada objeto de volta e
    # recalculou o sha256.
    mi = r.get('A_MEDICAO_INTEGRAL') or {}
    conteudo_ok = (mi.get('SHA_VERIFIED') == r['EXPECTED']
                   and mi.get('HASH_MISMATCH') == 0
                   and mi.get('NAO_BAIXARAM') == 0
                   and mi.get('DIVERGENTES') == 0)
    conteudo_gate = 'CLOSED' if conteudo_ok else 'OPEN'
    conteudo_declarado = r.get('RAW_CONTENT_INTEGRITY_GATE', 'NAO_MEDIDO')
    if conteudo_declarado != conteudo_gate:
        conteudo_gate = 'DIVERGENTE'
    raw_declarado = r['ESTADO']
    if raw_declarado != raw_derivado:
        # Falha fechada: o portão de importação NÃO abre com o artefato
        # discordando de si mesmo.
        raw_fechado = False
        raw_estado = 'DIVERGENTE'
        raw_porque_divergente = (
            'o artefato declara %s e os números dizem %s — enquanto os dois não '
            'concordarem, nada abre.' % (raw_declarado, raw_derivado))
    else:
        raw_estado = raw_derivado
        raw_porque_divergente = None

    # ── §15 · PRONTIDÃO DA ENTREGA, derivada dos arquivos ─────────────
    # Nenhum destes é digitado. Cada um pergunta ao repositório.
    def existe(*p):
        return os.path.exists(os.path.join(RAIZ, *p))

    def texto(*p):
        with open(os.path.join(RAIZ, *p), encoding='utf-8') as f:
            return f.read()

    prontidao = {}

    # A primeira versão desta verificação contava a expressão "ON CONFLICT"
    # no arquivo inteiro — e achou 3 num arquivo com 2 INSERT, porque uma
    # delas estava num COMENTÁRIO explicando a lei. O gate reprovou o
    # arquivo por causa da prosa que descreve o gate. Sétima vez que este
    # padrão aparece no projeto; a correção é sempre a mesma: medir a
    # ESTRUTURA, não o texto.
    def instrucoes(sql):
        """Comandos SQL, sem comentários de linha."""
        limpo = '\n'.join(l.split('--')[0] for l in sql.splitlines())
        return [c.strip() for c in limpo.split(';') if c.strip()]

    falta = []
    imp_reg = ('supabase', 'importacoes', 'ES-REGULATORIO-ROPF-2026-08-29.sql')
    if not existe(*imp_reg):
        falta.append('a importação regulatória não existe')
    else:
        cmds = instrucoes(texto(*imp_reg))
        for c in cmds:
            baixo = c.lower()
            for proibido in ('update ', 'delete ', 'truncate ', 'drop '):
                if baixo.startswith(proibido):
                    falta.append('a importação regulatória contém %s' % proibido.strip())
            if 'insert into' in baixo and 'on conflict' not in baixo:
                falta.append('há INSERT sem ON CONFLICT declarado')
    if not existe('scripts', 'regulatorio_importar.py'):
        falta.append('o gerador determinístico não existe')
    if not existe('supabase', 'tests', 'regressoes_regulatorio_es.sql'):
        falta.append('a suíte do regulatório não existe')
    prontidao['ES_REGULATORY_IMPORT_GATE'] = {
        'ESTADO': 'READY' if not falta else 'PARTIAL', 'FALTANDO': falta}

    falta = []
    for peca, cam in (('migration do catálogo',
                       ('supabase', 'migrations', '014_catalogo_publico_fabricante.sql')),
                      ('import do catálogo',
                       ('supabase', 'importacoes', 'ADAMA-ES-CATALOGO-2026-08-30.sql')),
                      ('import regulatório', imp_reg),
                      ('a cadeia canônica', ('scripts', 'cadeia_canonica.sh'))):
        if not existe(*cam):
            falta.append('falta %s' % peca)
    prontidao['RECONCILED_IMPORT_PACKAGE_READY'] = {
        'ESTADO': 'YES' if not falta else 'NO', 'FALTANDO': falta}

    falta = []
    wf = ('.github', 'workflows', 'supabase-migrate.yml')
    if not existe(*wf):
        falta.append('o workflow de produção não existe')
    else:
        t = texto(*wf)
        if 'cadeia_canonica.sh' not in t:
            falta.append('o workflow não usa a cadeia canônica — duas ordens')
        if 'inventario_esperado.py' not in t:
            falta.append('o pré-voo ainda não é derivado')
        if 'case "$n" in 0|23|26|30' in t:
            falta.append('o pré-voo ainda tem lista fixa de contagens')
    prontidao['PRODUCTION_MIGRATION_PATH'] = {
        'ESTADO': 'READY' if not falta else 'PARTIAL', 'FALTANDO': falta}

    tudo_pronto = (all(v['ESTADO'] in ('READY', 'YES') for v in prontidao.values())
                   and conteudo_gate == 'CLOSED')

    pode_importar = (portoes['CATALOG_IMPORT_ENGINEERING_GATE']['ESTADO'] == 'READY'
                     and raw_fechado and tudo_pronto)

    return {
        'SOURCE_ID': 'PORTOES-EAME',
        'VERSION': 'V1',
        'captured_at': '2026-08-30',
        'O_QUE_ISTO_E':
            'o estado de cada portão do EAME, DERIVADO das cicatrizes de que ele '
            'depende. Nenhum estado aqui foi digitado por alguém.',
        'O_QUE_ISTO_NAO_E':
            'não é medição do mundo. É a leitura da nossa própria matriz de cicatrizes '
            'e do estado externo do bucket raw. Um portão READY diz que as leis que ele '
            'guarda têm testemunha executável — não que a coleta já aconteceu.',
        'SOURCE_LOCATION': 'interno',
        'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'pt',
        'DERIVADO_DE': ['scripts/cicatrizes_brasil.py',
                        'data/samples/RAW-GATE-ES.json'],
        'PORQUE_EXISTE':
            'um nome estava fazendo dois trabalhos, e por isso o mesmo relatório '
            'publicou LOCATION_CONTRACT_COMPLETE = NO e um portão de COLETA em '
            'READY. Separar os dois portões desfaz a contradição sem mover a régua: '
            'nenhuma cicatriz mudou de estado para isto acontecer.',
        'REGRA': 'READY exige TODA cicatriz das famílias do portão em PROVED. '
                 'Uma única PARTIAL ou ABSENT o deixa em PARTIAL.',
        'LOCATION_IS_PART_OF_COLLECTION_ENTRY_GATE':
            LOCATION_IS_PART_OF_COLLECTION_ENTRY_GATE,
        'PORQUE_LOCATION_E_PARTE':
            'toda coleta que produz documento produz documento com lugar de fato. '
            'O portão se chama entrada da COLETA, e o contrato de localização está '
            'em NO. Dizer que localização não é parte dele seria escolher o escopo '
            'depois de ver o resultado.',
        'PRONTIDAO_DA_ENTREGA': prontidao,
        'CONTRATOS': contratos,
        'PORTOES': portoes,
        'RAW_PRESERVATION_GATE': {
            'ESTADO': raw_estado,
            'ESTADO_DECLARADO_NO_ARTEFATO': raw_declarado,
            'ESTADO_DERIVADO_DOS_NUMEROS': raw_derivado,
            'DIVERGENCIA': raw_porque_divergente,
            'PROVA': r['PROVA'],
            'VERIFICADO_DAQUI': r['VERIFICADO_DAQUI'],
            'ESTA_BRANCH_EXECUTOU_O_UPLOAD': r.get('ESTA_BRANCH_EXECUTOU_O_UPLOAD', 'NO'),
            'DO_PLANO_AUSENTES': r.get('DO_PLANO_AUSENTES'),
            'EXPECTED': r['EXPECTED'],
            'VERIFIED': r['ALREADY_PRESENT_VERIFIED'],
            'FAILED': r['FAILED_WITH_REASON'],
            'HASH_MISMATCH': r['HASH_MISMATCH'],
            'CONFLICT': r['CONFLICT'],
            'FECHADO': 'YES' if raw_fechado else 'NO',
            'RAW_CONTENT_INTEGRITY_GATE': conteudo_gate,
            'SHA_VERIFIED': mi.get('SHA_VERIFIED'),
            'BYTES_VERIFICADOS_REMOTAMENTE': mi.get('BYTES'),
            'A_LEI_QUE_FICA': pnc.get('LEI'),
            'A_RESSALVA_DA_PROVA': mi.get('A_RESSALVA_QUE_O_PROPRIO_HANDOFF_NAO_ARREDONDA'),
            'ORFAOS_NO_BUCKET': r.get('ORFAOS_NO_BUCKET'),
            'DIAGNOSTICO': r.get('DIAGNOSTICO_ISOLADO'),
            'EXTERNAL_DIAGNOSIS_IN_PROGRESS': r['EXTERNAL_DIAGNOSIS_IN_PROGRESS'],
            'NUNCA_ZERO_SENT': r['PORQUE_NUNCA_ZERO_SENT'],
        },
        'IMPORT_CAN_BE_NEXT_MISSION': 'YES' if pode_importar else 'NO',
        'PORQUE_NAO_IMPORTAR':
            None if pode_importar else
            ('a engenharia do catálogo não está READY.'
             if portoes['CATALOG_IMPORT_ENGINEERING_GATE']['ESTADO'] != 'READY'
             else 'o RAW gate não fechou: %s de %s assets ausentes do bucket. '
                  'Importar com o bruto incompleto é importar sem poder voltar à '
                  'evidência.' % (r.get('DO_PLANO_AUSENTES'), r['EXPECTED'])),
        'O_QUE_YES_SIGNIFICA':
            'que a PRÓXIMA missão pode ser a importação. Não que esta rodada deva '
            'importar, e não que a importação já tenha sido feita.',
    }


if __name__ == '__main__':
    d = monta()
    if '--build' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('escrito:', SAIDA)
    print('LOCATION_IS_PART_OF_COLLECTION_ENTRY_GATE =',
          d['LOCATION_IS_PART_OF_COLLECTION_ENTRY_GATE'])
    print()
    for nome, c in d['CONTRATOS'].items():
        print('%-38s %-4s %s' % (nome, c['COMPLETO'],
                                 ('abertas: ' + ', '.join(c['ABERTAS'])) if c['ABERTAS'] else ''))
    print()
    for nome, p in d['PORTOES'].items():
        print('%-33s %-8s  %d/%d cicatrizes PROVED'
              % (nome, p['ESTADO'], p['CICATRIZES_PROVED'], p['CICATRIZES_COBERTAS']))
        for b in p['BLOQUEADORES']:
            print('    bloqueia: %-7s %-24s %s' % (b['ID'], b['FAMILIA'], b['ESTADO']))
    g = d['RAW_PRESERVATION_GATE']
    print()
    print('RAW_PRESERVATION_GATE             %s  (prova %s, verificado daqui: %s)'
          % (g['ESTADO'], g['PROVA'], g['VERIFICADO_DAQUI']))
    if g['DIVERGENCIA']:
        print('    ⚠ ', g['DIVERGENCIA'])
    print('RAW_CONTENT_INTEGRITY_GATE        %s  (%s de %s baixados de volta e com '
          'sha256 reconferido)'
          % (g['RAW_CONTENT_INTEGRITY_GATE'], g['SHA_VERIFIED'], g['EXPECTED']))
    print()
    for k, v in d['PRONTIDAO_DA_ENTREGA'].items():
        print('%-38s %s' % (k, v['ESTADO'] if isinstance(v, dict) else v))
        if isinstance(v, dict) and v.get('FALTANDO'):
            for f in v['FALTANDO']:
                print('    falta: %s' % f)
    print('    EXPECTED=%d  VERIFIED=%d  FAILED=%d  HASH_MISMATCH=%d  CONFLICT=%d'
          % (g['EXPECTED'], g['VERIFIED'], g['FAILED'], g['HASH_MISMATCH'], g['CONFLICT']))
    print()
    print('IMPORT_CAN_BE_NEXT_MISSION =', d['IMPORT_CAN_BE_NEXT_MISSION'])
