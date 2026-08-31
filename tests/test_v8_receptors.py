# -*- coding: utf-8 -*-
"""Provas do CONTRATO DE RECEPCAO do casco V8.

Duas coisas diferentes sao verificadas aqui, e nunca se misturam:

1. O CONTRATO esta completo? Cada receptor declara os onze campos exigidos, os
   guards, os estados de carga, os dois backends de proveniencia e o
   comportamento de falha fechada. Isto passa hoje: o contrato e o produto desta
   rodada.

2. A MEDICAO e honesta? Cada afirmacao CASCO_MEASURED e conferida contra os bytes
   do casco. Se alguem escrever que H8 existe, o teste abre o arquivo e reprova.
   Se alguem apagar um bloqueador para o relatorio ficar bonito, o teste reprova.

O que estes testes NAO fazem: aprovar o casco. O casco implementa 0 de 9
receptores hoje, e isso esta escrito, medido e testado.

Zero rede. Le apenas artefatos deste repositorio.
"""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from v8_receptor_audit import (  # noqa: E402
    desempacotar_casco, chaves_expostas, fatiar_por_tela, medir,
)

IMPL = os.path.join(ROOT, 'data', 'implementation')


def ler(nome):
    with open(os.path.join(IMPL, nome), encoding='utf-8') as f:
        return json.load(f)


MATRIZ = ler('V8-RECEPTOR-MATRIX.json')
COMPONENTES = ler('V8-COMPONENT-DATA-CONTRACTS.json')
ORFAOS = ler('ORPHAN-INTELLIGENCE-OUTPUTS.json')

MARKUP, CAMADA = desempacotar_casco()
EXPOSTAS = chaves_expostas(CAMADA)

RECEPTORES = {r['RECEPTOR_ID']: r for r in MATRIZ['RECEPTORS']}
SUBRECEPTORES = {r['RECEPTOR_ID']: r for r in MATRIZ['SUBRECEPTORS']}
TODOS = dict(RECEPTORES)
TODOS.update(SUBRECEPTORES)
COMPS = {c['COMPONENT_ID']: c for c in COMPONENTES['COMPONENTS']}

CAMPOS_DO_CONTRATO = (
    'RECEPTOR_ID', 'HOSE_ID', 'CANONICAL_PAYLOAD_TYPE', 'COMPONENT_ID',
    'REQUIRED_FIELDS', 'OPTIONAL_FIELDS', 'GUARDS', 'LOAD_STATES',
    'PROVENANCE_FIELDS', 'EVIDENCE_FIELDS', 'FAIL_CLOSED_BEHAVIOR',
)

OITO_ESTADOS = (
    'UNWIRED', 'LOADING', 'READY', 'EMPTY_VALID',
    'NOT_STARTED', 'NOT_AVAILABLE', 'BLOCKED', 'ERROR_FAIL_CLOSED',
)

HOSES = ('H1-TERRITORIAL', 'H2-REGULATORY-DEADLINE', 'H3-COMPETITOR-IDENTITY-CHAIN',
         'H4-META', 'H5-LONGITUDINAL-FIELD', 'H6-CREATOR', 'H7-EXPERT',
         'H8-PUBLIC-COMM', 'H9-MULTILINGUAL')


class Base(unittest.TestCase):
    """Ferramentas compartilhadas."""

    def contrato_completo(self, rid):
        r = TODOS[rid]
        for campo in CAMPOS_DO_CONTRATO:
            self.assertIn(campo, r, '%s nao declara %s' % (rid, campo))
            self.assertTrue(r[campo], '%s declara %s vazio' % (rid, campo))
        for estado in r['LOAD_STATES']:
            self.assertIn(estado, OITO_ESTADOS,
                          '%s usa estado de carga fora do vocabulario: %s' % (rid, estado))
        for obrigatorio in ('UNWIRED', 'LOADING', 'READY', 'EMPTY_VALID', 'ERROR_FAIL_CLOSED'):
            self.assertIn(obrigatorio, r['LOAD_STATES'],
                          '%s nao suporta %s' % (rid, obrigatorio))
        self.assertEqual(set(r['PROVENANCE_FIELDS']['EXPECTED_BACKENDS']),
                         {'GITHUB', 'SUPABASE'},
                         '%s nao aceita os dois backends' % rid)
        self.assertIn('CASCO_MEASURED', r, '%s nao registra a medicao' % rid)
        return r

    def medicao_honesta(self, rid):
        """As chaves declaradas presentes existem mesmo; as ausentes faltam mesmo."""
        m = TODOS[rid]['CASCO_MEASURED']
        for chave in m.get('KEYS_PRESENT_IN_CASCO', []):
            self.assertIn(chave, EXPOSTAS,
                          '%s afirma que o casco expoe "%s" e nao expoe' % (rid, chave))
        for termo in m.get('TERMS_ABSENT_FROM_CASCO', []):
            # assertFalse, nao assertNotIn: o markup tem 302 mil caracteres e a
            # mensagem de falha imprimiria o casco inteiro.
            self.assertFalse(termo in MARKUP,
                             '%s afirma que "%s" esta ausente do casco e ele esta la' % (rid, termo))
        self.assertIn(m['STATE'], ('COMPLETE', 'PARTIAL', 'ABSENT', 'ABSENT_AS_RECEPTOR'))
        if m['STATE'] != 'COMPLETE':
            self.assertTrue(m.get('MISSING_FIELDS') or m.get('MISSING'),
                            '%s nao esta completo e nao diz o que falta' % rid)
        return m


class TestReceptoresDasMangueiras(Base):
    """Uma prova por mangueira. O nome e o do briefing, para ser encontravel."""

    def test_H1_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-H1-TERRITORIAL-OBSERVATION')
        self.assertEqual(r['HOSE_ID'], 'H1-TERRITORIAL')
        self.assertIn('CROP_ISSUE_PAIRING_NOT_PROVEN', r['GUARDS'])
        for campo in ('CROP', 'ISSUE', 'REGION_OF_FACT', 'ISSUE_EVIDENCE_PASSAGE'):
            self.assertIn(campo, r['REQUIRED_FIELDS'])
        self.medicao_honesta('R-H1-TERRITORIAL-OBSERVATION')

    def test_H2_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-H2-REGISTRATION-DEADLINE')
        self.assertIn('STATUS_AS_DECLARED_BY_SOURCE', r['REQUIRED_FIELDS'])
        self.assertIn('EXPIRY_IS_NOT_WITHDRAWAL', r['GUARDS'])
        self.assertIn('ALERT', r['FAIL_CLOSED_BEHAVIOR'],
                      'a proibicao de ALERT precisa continuar escrita')
        self.medicao_honesta('R-H2-REGISTRATION-DEADLINE')

    def test_H3_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-H3-COMPETITOR-IDENTITY-CHAIN')
        self.assertIn('URBOLE_GUARD', r['GUARDS'])
        self.assertIn('DERIVED_DEPENDENCY_ON_META', r['GUARDS'])
        self.assertIn('URBOLE_GUARD_RESULT', r['REQUIRED_FIELDS'],
                      'portao sem resultado registrado e portao sem dentes')
        self.medicao_honesta('R-H3-COMPETITOR-IDENTITY-CHAIN')

    def test_H4_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-H4-OBSERVED-PAID-ACTIVITY')
        self.assertIn('IS_EVIDENCE_NOT_AN_OBJECT_TYPE', r['GUARDS'])
        self.assertIn('PAGE_COUNTRY_SCOPE_IS_NOT_AD_DELIVERY_COUNTRY', r['GUARDS'])
        self.assertIn('META_DASHBOARD', r['FAIL_CLOSED_BEHAVIOR'],
                      'a mangueira Meta nao pode ganhar superficie propria')
        self.medicao_honesta('R-H4-OBSERVED-PAID-ACTIVITY')

    def test_H5_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-H5-FIELD-PRESSURE-SERIES')
        self.assertIn('READING_N_PER_POINT', r['REQUIRED_FIELDS'])
        self.assertIn('BASELINE_STATE', r['REQUIRED_FIELDS'])
        self.assertIn('MEAN_NEVER_TRAVELS_WITHOUT_N', r['GUARDS'])
        self.assertIn('148964', r['LEDGER_NOTE'].replace('.', ''),
                      'o numero canonico do ledger precisa continuar aqui')
        self.medicao_honesta('R-H5-FIELD-PRESSURE-SERIES')

    def test_H6_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-H6-CREATOR-ENTITY')
        self.assertIn('ENTRY_PATH', r['REQUIRED_FIELDS'])
        self.assertEqual(set(r['ENTRY_PATH_VOCABULARY']),
                         {'FROM_ATTENTION_OBJECT', 'FROM_CROP_REGION_SEARCH'})
        self.assertIn('PERSON_CREATOR_IS_NOT_FARM_BUSINESS', r['GUARDS'])
        for campo in ('ROW_COUNT', 'ENTITY_COUNT'):
            self.assertIn(campo, r['REQUIRED_FIELDS'],
                          'linha e entidade viajam sempre juntas')
        self.medicao_honesta('R-H6-CREATOR-ENTITY')

    def test_H7_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-H7-SCIENTIFIC-PERSON')
        self.assertIn('ISSUE_EXPERTISE_PROVED', r['REQUIRED_FIELDS'])
        self.assertIn('IDENTITY_PROVED', r['REQUIRED_FIELDS'])
        self.assertIn('SCIENTIFIC_PERSON_IS_NOT_SCIENTIFIC_PUBLICATION', r['GUARDS'])
        self.assertIn('BLOQUEIA', r['FAIL_CLOSED_BEHAVIOR'],
                      'o portao precisa bloquear renderizacao, nao so avisar')
        self.medicao_honesta('R-H7-SCIENTIFIC-PERSON')

    def test_H8_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-H8-COMPANY-LOCAL-ACCOUNT')
        self.assertIn('CONTENT_COLLECTION_STAGE', r['REQUIRED_FIELDS'])
        self.assertIn('NOT_STARTED', r['CONTENT_COLLECTION_STAGE_VOCABULARY'])
        self.assertIn('NOT_STARTED', r['LOAD_STATES'])
        self.assertEqual(r['REQUIRED_LOAD_STATE_TODAY'], 'NOT_STARTED')
        self.assertIn('ZERO_IS_NO_CONTENT_COLLECTION_EXECUTED_NEVER_COMPANY_NOT_COMMUNICATING',
                      r['GUARDS'])
        self.medicao_honesta('R-H8-COMPANY-LOCAL-ACCOUNT')

    def test_H9_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-H9-TEXT-CONTENT')
        for campo in ('CANONICAL_ENTITY_ID', 'SOURCE_LANGUAGE', 'DISPLAY_LANGUAGE',
                      'ORIGINAL_TEXT', 'TRANSLATED_TEXT', 'TRANSLATION_PROVENANCE'):
            self.assertIn(campo, r['REQUIRED_FIELDS'],
                          'o receptor textual precisa de %s' % campo)
        self.assertEqual(set(r['LANGUAGE_VOCABULARY']),
                         {'pt', 'en', 'es', 'fr', 'it', 'MULTILINGUAL', 'UNKNOWN'})
        self.assertIn('TRANSLATION_NEVER_REPLACES_ORIGINAL', r['GUARDS'])
        self.medicao_honesta('R-H9-TEXT-CONTENT')

    def test_as_nove_mangueiras_tem_receptor_declarado(self):
        declaradas = {r['HOSE_ID'] for r in MATRIZ['RECEPTORS']}
        self.assertEqual(declaradas, set(HOSES))


class TestSubreceptores(Base):
    """Tres coisas que nao podem sumir dentro de outra."""

    def test_SCIENCE_PUBLICATION_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-SUB-SCIENCE-PUBLICATION-EVIDENCE')
        self.assertEqual(r['CANONICAL_PAYLOAD_TYPE'], 'SCIENTIFIC_PUBLICATION')
        self.assertIn('SCIENTIFIC_PERSON_IS_NOT_SCIENTIFIC_PUBLICATION', r['GUARDS'])
        for campo in ('PUBLICATION_ID', 'TITLE', 'AUTHORS', 'PEER_REVIEWED_STATE'):
            self.assertIn(campo, r['REQUIRED_FIELDS'])
        self.medicao_honesta('R-SUB-SCIENCE-PUBLICATION-EVIDENCE')

    def test_science_route_nao_e_h7_automaticamente(self):
        """H7 entrega PESSOA. A camada Ciencia precisa da PUBLICACAO."""
        pessoa = RECEPTORES['R-H7-SCIENTIFIC-PERSON']
        pub = SUBRECEPTORES['R-SUB-SCIENCE-PUBLICATION-EVIDENCE']
        self.assertNotEqual(pessoa['CANONICAL_PAYLOAD_TYPE'], pub['CANONICAL_PAYLOAD_TYPE'])
        self.assertNotEqual(set(pessoa['REQUIRED_FIELDS']), set(pub['REQUIRED_FIELDS']))

    def test_LOCAL_PORTFOLIO_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-SUB-LOCAL-ADAMA-PORTFOLIO-CONTEXT')
        self.assertIn('REGISTERED_RESPONSE_STATE', r['REQUIRED_FIELDS'])
        self.assertIn('REGISTRATION_DEADLINE_IS_NOT_LOCAL_ADAMA_PORTFOLIO_CONTEXT', r['GUARDS'])
        self.medicao_honesta('R-SUB-LOCAL-ADAMA-PORTFOLIO-CONTEXT')

    def test_portfolio_route_nao_e_h2_automaticamente(self):
        """H2 carrega o prazo de um registro qualquer, de qualquer titular."""
        prazo = RECEPTORES['R-H2-REGISTRATION-DEADLINE']
        portfolio = SUBRECEPTORES['R-SUB-LOCAL-ADAMA-PORTFOLIO-CONTEXT']
        self.assertNotEqual(prazo['CANONICAL_PAYLOAD_TYPE'], portfolio['CANONICAL_PAYLOAD_TYPE'])
        self.assertIn('REGISTRATION_DEADLINE_IS_NOT_LOCAL_ADAMA_PORTFOLIO_CONTEXT',
                      prazo['GUARDS'])

    def test_FIELD_VOICE_RECEPTOR_COMPLETE(self):
        r = self.contrato_completo('R-SUB-FIELD-VOICE-OBSERVED')
        for campo in ('OBSERVATION_ID', 'ORIGINAL_TEXT', 'SOURCE_LANGUAGE',
                      'GDPR_TREATMENT_STATE'):
            self.assertIn(campo, r['REQUIRED_FIELDS'])
        self.assertIn('OBSERVED_VOICE_IS_CONTEXT_NOT_PHENOMENON_LEG', r['GUARDS'])
        self.medicao_honesta('R-SUB-FIELD-VOICE-OBSERVED')

    def test_voz_de_campo_separa_entidade_de_observacao(self):
        entidade = RECEPTORES['R-H6-CREATOR-ENTITY']
        obs = SUBRECEPTORES['R-SUB-FIELD-VOICE-OBSERVED']
        self.assertIn('ENTITY_ID', entidade['REQUIRED_FIELDS'])
        self.assertIn('OBSERVATION_ID', obs['REQUIRED_FIELDS'])
        self.assertNotIn('OBSERVATION_ID', entidade['REQUIRED_FIELDS'])


class TestContratosDeComponente(Base):
    """Os cinco componentes que ja existem no casco."""

    def campos(self, cid):
        return COMPS[cid]['REQUIRED_FIELDS']

    def test_CONVERGENCE_COMPONENT_CONTRACT_COMPLETE(self):
        c = COMPS['CONVERGENCE_COMPONENT']
        campos = self.campos('CONVERGENCE_COMPONENT')
        for exigido in ('PROPOSITION_ID', 'CONVERGENCE_KIND'):
            self.assertIn(exigido, campos)
        for exigido in ('SIGNAL_FAMILY', 'EVIDENCE_ID', 'INDEPENDENCE_STATE',
                        'DEPENDENCY_RELATION'):
            self.assertIn(exigido, campos['LEGS'],
                          'a perna precisa carregar %s' % exigido)
        self.assertIn('THREE_CONVERGENCE_KINDS_NEVER_SUMMED', c['GUARDS'])
        self.assertIn('SINGLE_SIGNAL_IS_LEGITIMATE', c['GUARDS'])

    def test_convergencia_usa_o_vocabulario_canonico(self):
        vocab = COMPONENTES['CANONICAL_VOCABULARY']
        self.assertEqual(len(vocab['SIGNAL_FAMILIES']), 8)
        self.assertEqual(len(vocab['DEPENDENCY_TYPES']), 6)
        self.assertEqual(set(vocab['CONVERGENCE_KINDS']),
                         {'PHENOMENON_CONVERGENCE', 'IDENTITY_CONVERGENCE',
                          'CONTEXTUAL_ALIGNMENT'})
        self.assertIn('INDEPENDENT_SOURCE', vocab['DEPENDENCY_TYPES'])

    def test_TIMELINE_COMPONENT_CONTRACT_COMPLETE(self):
        campos = self.campos('OBJECT_TIMELINE')
        for exigido in ('EVENT_ID', 'EVENT_TYPE', 'EVENT_AT', 'SOURCE_ID',
                        'OBSERVATION_ID', 'STATE_BEFORE', 'STATE_AFTER', 'WHAT_CHANGED'):
            self.assertIn(exigido, campos, 'a timeline precisa de %s' % exigido)
        self.assertIn('GAP_IS_AN_EVENT_NOT_AN_ABSENCE_OF_EVENTS',
                      COMPS['OBJECT_TIMELINE']['GUARDS'])

    def test_CROP_MAP_COMPONENT_CONTRACT_COMPLETE(self):
        campos = self.campos('CROP_INTELLIGENCE_MAP')
        for exigido in ('COUNTRY', 'REGION', 'LOCALITY_OR_GEOMETRY', 'GEO_RESOLUTION',
                        'CROP', 'OBJECT_ID', 'OBJECT_TYPE', 'ATTENTION_STATE'):
            self.assertIn(exigido, campos, 'o mapa precisa de %s' % exigido)
        self.assertIn('NO_GEOMETRY_NO_PAINT', COMPS['CROP_INTELLIGENCE_MAP']['GUARDS'])
        self.assertIn('NOT_KNOWN', COMPONENTES['CANONICAL_VOCABULARY']['GEO_RESOLUTIONS'])

    def test_ACTION_MAP_COMPONENT_CONTRACT_COMPLETE(self):
        c = COMPS['ACTION_MAP']
        campos = self.campos('ACTION_MAP')
        for exigido in ('OBJECT_ID', 'DEPARTMENT', 'ACTION_TYPE', 'ACTION_STATE',
                        'ACTION_TEXT', 'EVIDENCE_BASIS'):
            self.assertIn(exigido, campos, 'o mapa de acoes precisa de %s' % exigido)
        self.assertIn('NO_EVIDENCE_NO_BUSINESS_DECISION', c['GUARDS'])
        self.assertEqual(set(COMPONENTES['CANONICAL_VOCABULARY']['ACTION_TYPES']),
                         {'BUSINESS_DECISION', 'SYSTEM_DECISION', 'INVESTIGATION'})

    def test_EVIDENCE_DRAWER_TRACES_ALL_HOSES(self):
        """A gaveta precisa PODER chegar as nove — e declarar que hoje nao chega."""
        c = COMPS['EVIDENCE_DRAWER']
        campos = self.campos('EVIDENCE_DRAWER')
        for exigido in ('HOSE_ID', 'EVIDENCE_ID', 'OBJECT_ID', 'SOURCE_ID', 'PROVENANCE'):
            self.assertIn(exigido, campos, 'sem %s a gaveta nao rastreia' % exigido)
        self.assertIn('MUST_TRACE_ALL_NINE_HOSES', c['GUARDS'])
        self.assertIn('ORIGINAL_TEXT', campos)
        self.assertIn('TRANSLATION_NEVER_REPLACES_ORIGINAL', c['GUARDS'])
        # o veredito medido tem de estar registrado, seja qual for
        self.assertIn(c['CASCO_MEASURED']['TRACES_ALL_HOSES'], ('YES', 'NO'))

    def test_gaveta_global_medida_como_bloqueio(self):
        """A gaveta abre igual venha de que objeto vier — isso esta medido."""
        m = COMPS['EVIDENCE_DRAWER']['CASCO_MEASURED']
        self.assertEqual(m['TRACES_ALL_HOSES'], 'NO')
        self.assertIn('drawerFields', EXPOSTAS)
        # e a medicao confere: openDrawer nao recebe argumento nenhum
        self.assertIn('openDrawer: () => this.set({ drawerOpen: true })', CAMADA)


class TestEnvelopeDeProveniencia(Base):

    def test_GITHUB_PROVENANCE_SUPPORTED(self):
        p = MATRIZ['PROVENANCE_ENVELOPE']
        self.assertEqual(p['DISCRIMINATOR'], 'SOURCE_BACKEND')
        self.assertIn('GITHUB', p['VALUES'])
        for campo in ('REPOSITORY', 'PATH', 'COMMIT_SHA', 'HASH', 'SOURCE_ID', 'AS_OF_DATE'):
            self.assertIn(campo, p['GITHUB'], 'proveniencia GitHub sem %s' % campo)
        self.assertIn('COMMIT_SHA', p['PINNED_READ_RULE'])

    def test_SUPABASE_PROVENANCE_SUPPORTED(self):
        p = MATRIZ['PROVENANCE_ENVELOPE']
        self.assertIn('SUPABASE', p['VALUES'])
        for campo in ('SCHEMA', 'TABLE_OR_VIEW', 'PRIMARY_KEY', 'SNAPSHOT_ID',
                      'CAPTURED_AT', 'SOURCE_ID', 'AS_OF_DATE'):
            self.assertIn(campo, p['SUPABASE'], 'proveniencia Supabase sem %s' % campo)

    def test_uma_ui_so_para_os_dois_backends(self):
        p = MATRIZ['PROVENANCE_ENVELOPE']
        self.assertIn('identica', p['UI_RULE'])
        self.assertIn('UM receptor canonico', MATRIZ['RECEPTOR_ENVELOPE']['RULE'])

    def test_credencial_nunca_no_frontend(self):
        seg = MATRIZ['PROVENANCE_ENVELOPE']['SECURITY']
        for proibido in ('SERVICE_ROLE_KEY', 'secret', 'token'):
            self.assertIn(proibido, seg['NEVER_IN_FRONTEND'])

    def test_o_casco_nao_carrega_nenhum_segredo(self):
        """Prova sobre os bytes, nao sobre a intencao."""
        for proibido in ('SERVICE_ROLE_KEY', 'service_role', 'SUPABASE_KEY',
                         'apikey', 'Bearer '):
            self.assertFalse(proibido in MARKUP, 'o casco contem %r' % proibido)

    def test_todo_receptor_aceita_os_dois_backends(self):
        for rid, r in TODOS.items():
            self.assertEqual(set(r['PROVENANCE_FIELDS']['EXPECTED_BACKENDS']),
                             {'GITHUB', 'SUPABASE'}, rid)


class TestEstadosDeCarga(Base):

    def test_FAIL_CLOSED_STATES_SUPPORTED(self):
        estados = MATRIZ['LOAD_STATES']
        self.assertEqual(set(estados), set(OITO_ESTADOS))
        for chave in OITO_ESTADOS:
            self.assertTrue(estados[chave].strip(), '%s sem definicao' % chave)

    def test_transporte_nunca_vira_dado(self):
        lei = MATRIZ['RECEPTOR_ENVELOPE']['LAW_TRANSPORT_IS_NOT_DATA']
        self.assertIn('UNWIRED', lei)
        self.assertIn('EMPTY_VALID', lei)

    def test_todo_receptor_distingue_vazio_de_nao_ligado(self):
        for rid, r in TODOS.items():
            self.assertIn('UNWIRED', r['LOAD_STATES'], rid)
            self.assertIn('EMPTY_VALID', r['LOAD_STATES'], rid)

    def test_o_casco_hoje_so_tem_booleano(self):
        """Medicao: o casco distingue cheio de vazio, e nada mais.

        Os oito estados NAO podem ser procurados por substring crua: 'READY'
        casa dentro de 'ATTENTION READY', que e estado de atencao e nao de
        transporte; 'BLOCKED' casaria com 'BLOQUEADO'. Confundir mencao com uso
        ja me custou um erro antes. So entram aqui os nomes que nao colidem.
        """
        for par in ('hasObjects', 'noObjects', 'hasChanges', 'noChanges',
                    'hasKnown', 'noKnown', 'objHasHistory', 'objNoHistory'):
            self.assertIn(par, EXPOSTAS)
        for termo in ('LOAD_STATE', 'UNWIRED', 'EMPTY_VALID', 'NOT_AVAILABLE',
                      'ERROR_FAIL_CLOSED', 'NO_DATA_REASON'):
            self.assertFalse(termo in MARKUP,
                             'o casco ja usa %s — a medicao esta velha' % termo)


class TestOrfaos(Base):

    def test_NO_ORPHAN_CANONICAL_INTELLIGENCE(self):
        classes = [o['CLASS'] for o in ORFAOS['OUTPUTS']]
        self.assertNotIn('ORPHAN_INTELLIGENCE_OUTPUT', classes)
        self.assertEqual(ORFAOS['SUMMARY']['ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS'], 0)

    def test_toda_saida_roteada_nomeia_o_receptor(self):
        for o in ORFAOS['OUTPUTS']:
            if o['CLASS'] in ('NOT_CANONICAL', 'DEPRECATED'):
                self.assertTrue(o.get('REASON'),
                                '%s foi descartada sem motivo' % o['OUTPUT'])
            else:
                self.assertTrue(o.get('RECEPTOR'),
                                '%s nao nomeia receptor' % o['OUTPUT'])

    def test_deprecado_nomeia_o_sucessor(self):
        for o in ORFAOS['OUTPUTS']:
            if o['CLASS'] == 'DEPRECATED':
                self.assertTrue(o.get('SUPERSEDED_BY'),
                                '%s foi deprecada sem sucessor' % o['OUTPUT'])

    def test_os_numeros_do_resumo_sao_derivados(self):
        m = medir()
        self.assertEqual(ORFAOS['SUMMARY']['OUTPUTS_INVENTORIED'],
                         m['ORFAOS']['INVENTARIADAS'])
        self.assertEqual(ORFAOS['SUMMARY']['CLASS_COUNTS'], m['ORFAOS']['CLASSES'])
        self.assertEqual(ORFAOS['SUMMARY']['OUTPUTS_WHOSE_RECEPTOR_IS_ABSENT_IN_THE_CASCO'],
                         m['ORFAOS']['RECEPTOR_AUSENTE_NO_CASCO'])

    def test_as_duas_unidades_nao_se_confundem(self):
        """Saidas e receptores sao unidades distintas — nunca somar.

        No index (11) sao 2 saidas apontando para 1 receptor (H6). No index (10)
        eram 10 saidas em 6 receptores. Os dois inventarios ficam no arquivo:
        apagar o anterior apagaria a prova de que o patch mudou alguma coisa.
        """
        saidas = ORFAOS['SUMMARY']['OUTPUTS_WHOSE_RECEPTOR_IS_ABSENT_IN_THE_CASCO']
        receptores = len(ORFAOS['RECEPTORS_ABSENT_IN_CASCO_INDEX11'])
        self.assertNotEqual(saidas, receptores)
        self.assertGreater(len(ORFAOS['RECEPTORS_ABSENT_IN_CASCO_INDEX10']), receptores)
        self.assertIn('UNIT_WARNING', ORFAOS['TWO_DIFFERENT_NUMBERS'])
        self.assertIn('HISTORICO', ORFAOS['TWO_DIFFERENT_NUMBERS'])


class TestMedicaoDoCasco(Base):
    """O casco nao e aprovado aqui. Ele e medido, e a medicao e conferida."""

    def test_a_testemunha_confere(self):
        w = MATRIZ['CASCO_WITNESS']
        caminho = os.path.join(ROOT, w['PATH'])
        import hashlib
        with open(caminho, 'rb') as f:
            dados = f.read()
        self.assertEqual(len(dados), w['BYTES'])
        self.assertEqual(hashlib.sha256(dados).hexdigest(), w['SHA256'])

    def test_o_v7_continua_testemunha(self):
        w = MATRIZ['CASCO_WITNESS']
        self.assertIn('a31ea1848a99e48cbfcdd2574a284eaeba9017110fb6ea107c6e4f39d4187c6a',
                      w['V7_STILL_WITNESS'])
        self.assertTrue(os.path.exists(
            os.path.join(ROOT, 'casco', 'canonical', 'SINTONIA-EAME-PILOT-V7.html')))

    def test_as_nove_telas_do_v8(self):
        self.assertEqual(set(MATRIZ['CASCO_WITNESS']['SCREENS']),
                         set(medir()['CASCO']['TELAS']))

    def test_nenhuma_mangueira_esta_completa_no_casco_hoje(self):
        """Se um dia isto reprovar por excesso, e boa noticia — e exige reler a medicao."""
        m = medir()
        self.assertEqual(m['RECEPTORES']['HOSES_WITH_COMPLETE_RECEIVER'], 0)
        self.assertEqual(m['RECEPTORES']['HOSES_TOTAL'], 9)

    def test_h8_nao_tem_receptor_nenhum_no_casco(self):
        m = RECEPTORES['R-H8-COMPANY-LOCAL-ACCOUNT']['CASCO_MEASURED']
        self.assertEqual(m['STATE'], 'ABSENT')
        self.assertEqual(m['KEYS_PRESENT_IN_CASCO'], [])

    def test_os_botoes_de_traducao_nao_tem_handler(self):
        """Medicao dura: botao desenhado e nao ligado."""
        i = MARKUP.find('EVIDENCE DRAWER')
        gaveta = MARKUP[i:i + 9000]
        j = gaveta.find('</sc-if>')
        gaveta = gaveta[:j] if j > 0 else gaveta
        self.assertIn('Ver original', gaveta)
        self.assertIn('Mostrar tradu', gaveta)
        acoes = re.findall(r'sc-camel-on-click="\{\{\s*([^}]+?)\s*\}\}"', gaveta)
        self.assertEqual(set(acoes), {'closeDrawer'},
                         'a gaveta ganhou handler novo — reler a medicao de H9')

    def test_o_portao_de_expertise_e_prosa_e_nao_campo(self):
        self.assertIn('expertise no problema estiver provada', MARKUP)
        self.assertFalse('ISSUE_EXPERTISE_PROVED' in MARKUP)

    def test_experts_renderiza_fora_do_objeto(self):
        """Desvio de superficie medido: a camada Pessoas devia viver no objeto."""
        m = RECEPTORES['R-H7-SCIENTIFIC-PERSON']['CASCO_MEASURED']
        self.assertIn('SURFACE_DRIFT', m)
        fatias = fatiar_por_tela(MARKUP)
        self.assertIn('list="{{ experts }}"', fatias['radar'])
        self.assertNotIn('list="{{ experts }}"', fatias['obj'])


class TestModoDaRodada(Base):
    """Nada foi ligado, coletado ou implementado."""

    def test_nenhum_dado_real_foi_ligado(self):
        modo = MATRIZ['MODE']
        self.assertEqual(modo['REAL_DATA_WIRED'], 'NO')
        self.assertEqual(modo['COLLECTION_EXECUTED'], 'NO')
        self.assertEqual(modo['CASCO_V7_MODIFIED'], 'NO')
        self.assertEqual(modo['CASCO_V8_MODIFIED'], 'NO')

    def test_o_veredito_visual_foi_aceito_sem_redesenho(self):
        v = COMPONENTES['VISUAL_VERDICT_ACCEPTED']
        self.assertEqual(v['STATE'], 'PASSOU')
        self.assertEqual(len(v['COMPONENTS_CONFIRMED_PRESENT']), 9)

    def test_o_script_de_auditoria_nao_toca_a_rede(self):
        import ast
        caminho = os.path.join(ROOT, 'scripts', 'v8_receptor_audit.py')
        with open(caminho, encoding='utf-8') as f:
            arvore = ast.parse(f.read())
        proibidos = {'requests', 'urllib', 'http', 'socket', 'httpx', 'subprocess'}
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for a in no.names:
                    self.assertNotIn(a.name.split('.')[0], proibidos)
            elif isinstance(no, ast.ImportFrom) and no.module:
                self.assertNotIn(no.module.split('.')[0], proibidos)


if __name__ == '__main__':
    unittest.main()
