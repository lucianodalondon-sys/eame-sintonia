# -*- coding: utf-8 -*-
"""Provas dos artefatos de ARBITRAGEM.

Uma especificacao que nao se verifica e prosa. Estes testes nao implementam o V8: eles
garantem que o modelo de objeto, a maquina de estados e o mapa de mangueiras sejam
internamente consistentes e que as decisoes duras nao se percam numa edicao futura.

Zero rede. Le apenas os artefatos desta pasta e commits congelados.
"""
import json
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARB = os.path.join(ROOT, 'data', 'arbitration')


def ler(nome):
    with open(os.path.join(ARB, nome), encoding='utf-8') as f:
        return json.load(f)


SCHEMA = ler('ATTENTION-OBJECT-SCHEMA.json')
MAQUINA = ler('ATTENTION-STATE-MACHINE.json')
HOSES = ler('FINAL-HOSE-MAP-EAME.json')

TIPOS = ('PHENOMENON_CASE', 'REGULATORY_DEADLINE',
         'COMPETITOR_IDENTITY_CHAIN', 'LONGITUDINAL_FIELD_PRESSURE')


class TestModeloDeObjeto(unittest.TestCase):
    """A unidade superior deixou de ser CASE."""

    def test_a_unidade_superior_e_attention_object(self):
        self.assertEqual(SCHEMA['TOP_LEVEL_PRODUCT_UNIT'], 'ATTENTION_OBJECT')

    def test_os_quatro_tipos_existem_e_case_continua_um_deles(self):
        self.assertEqual(set(SCHEMA['OBJECT_TYPES']), set(TIPOS))
        self.assertIn('PHENOMENON_CASE', SCHEMA['OBJECT_TYPES'])

    def test_cada_tipo_declara_unidade_pergunta_e_gatilho(self):
        for t, v in SCHEMA['OBJECT_TYPES'].items():
            for campo in ('UNIT', 'DECISION_QUESTION', 'OBJECT_SPECIFIC_TRIGGER', 'REQUIRED'):
                self.assertIn(campo, v, '%s sem %s' % (t, campo))

    def test_crop_e_issue_nao_sao_inventados_onde_nao_existem(self):
        """Objetos cuja unidade nao tem cultura e problema declaram NOT_APPLICABLE."""
        for t in ('REGULATORY_DEADLINE', 'COMPETITOR_IDENTITY_CHAIN'):
            na = SCHEMA['OBJECT_TYPES'][t].get('NOT_APPLICABLE', [])
            self.assertIn('CROP', na, '%s precisa declarar CROP NOT_APPLICABLE' % t)
            self.assertIn('ISSUE', na)
            self.assertNotIn('CROP', SCHEMA['OBJECT_TYPES'][t]['REQUIRED'])

    def test_so_o_caso_de_fenomeno_carrega_as_dimensoes_de_fenomeno(self):
        dims = set(SCHEMA['OBJECT_TYPES']['PHENOMENON_CASE']['DIMENSIONS'])
        self.assertTrue({'FIELD', 'SCIENCE', 'PEOPLE'} <= dims)
        for t in ('REGULATORY_DEADLINE', 'COMPETITOR_IDENTITY_CHAIN'):
            outras = set(SCHEMA['OBJECT_TYPES'][t]['DIMENSIONS'])
            self.assertFalse(outras & {'FIELD', 'SCIENCE', 'PEOPLE'},
                             '%s nao pode fingir ter dimensoes de fenomeno' % t)

    def test_not_applicable_e_estado_de_primeira_classe(self):
        self.assertIn('NOT_APPLICABLE', SCHEMA['CAMPOS_DE_ESTADO_PERMITIDOS'])

    def test_o_id_do_objeto_e_neutro_de_idioma(self):
        self.assertEqual(SCHEMA['MULTILINGUAL']['ATTENTION_OBJECT_ID'], 'LANGUAGE_NEUTRAL')
        self.assertEqual(SCHEMA['MULTILINGUAL']['CONTRACT_COMMIT'],
                         '1443f6435d4297a4563f25d83473142fc12e1f0d')


class TestGramaticaDeAtencao(unittest.TestCase):
    """Convergencia deixou de ser requisito universal."""

    def test_multi_sinal_nao_e_obrigatorio(self):
        self.assertEqual(MAQUINA['DECISAO_QUE_MUDA_TUDO'],
                         'MULTI_SIGNAL_REQUIRED_FOR_ATTENTION = NO')
        self.assertFalse(MAQUINA['ATTENTION_READINESS_GATE']['CONVERGENCIA']['OBRIGATORIA'])

    def test_o_portao_tem_os_cinco_requisitos(self):
        nomes = [r['NOME'] for r in MAQUINA['ATTENTION_READINESS_GATE']['REQUISITOS']]
        self.assertEqual(nomes, ['VALID_EVIDENCE', 'OBJECT_SPECIFIC_TRIGGER',
                                 'TIME_RELEVANCE', 'DECISION_QUESTION', 'DECISION_OWNER'])

    def test_cada_requisito_diz_quando_falha(self):
        for r in MAQUINA['ATTENTION_READINESS_GATE']['REQUISITOS']:
            self.assertIn('FALHA_SE', r)
            self.assertTrue(r['FALHA_SE'])

    def test_a_regra_de_convergencia_sobrevive(self):
        c = MAQUINA['ATTENTION_READINESS_GATE']['CONVERGENCIA']
        self.assertEqual(c['REGRA'],
                         'CONVERGENCE_REQUIRES = SAME_PROPOSITION + INDEPENDENT_EVIDENCE')
        self.assertIn('CONTEXTUAL_ALIGNMENT', c['NAO_CONTA'])
        self.assertTrue(c['NUNCA_SOMAR_OS_TRES'])

    def test_os_tres_tipos_de_convergencia_continuam_separados(self):
        t = MAQUINA['ATTENTION_READINESS_GATE']['CONVERGENCIA']['TIPOS']
        for k in ('PHENOMENON_CONVERGENCE', 'IDENTITY_CONVERGENCE', 'CONTEXTUAL_ALIGNMENT'):
            self.assertIn(k, t)


class TestMaquinaDeEstados(unittest.TestCase):

    def test_os_cinco_estados_existem(self):
        estados = set(s['STATE'] for s in MAQUINA['STATES'])
        self.assertEqual(estados, {'NEEDS_EVIDENCE', 'VALID_EVIDENCE_NOT_ATTENTION_READY',
                                   'ATTENTION_CANDIDATE_TEST', 'ATTENTION_READY',
                                   'ARCHIVED_HISTORICAL'})

    def test_toda_transicao_liga_estados_que_existem(self):
        estados = set(s['STATE'] for s in MAQUINA['STATES'])
        for t in MAQUINA['TRANSITIONS']:
            self.assertIn(t['FROM'], estados)
            self.assertIn(t['TO'], estados)
            self.assertTrue(t['WHEN'])

    def test_rebaixar_e_possivel_e_nao_e_retrocesso(self):
        volta = [t for t in MAQUINA['TRANSITIONS']
                 if t['FROM'] == 'ATTENTION_READY'
                 and t['TO'] == 'VALID_EVIDENCE_NOT_ATTENTION_READY']
        self.assertTrue(volta, 'o modelo precisa permitir rebaixamento')
        self.assertIn('nunca e retrocesso', volta[0]['NOTA'])

    def test_a_home_so_mostra_pronto_ou_teste_rotulado(self):
        h = MAQUINA['HOME_RULE']
        self.assertEqual(h['MOSTRA_PRIORITARIAMENTE'], 'ATTENTION_READY')
        self.assertIn('rotulo explicito', h['PODE_MOSTRAR'])
        self.assertIn('VALID_EVIDENCE_NOT_ATTENTION_READY', h['NUNCA_MOSTRA'])

    def test_fila_vazia_e_resultado_e_nao_falha(self):
        self.assertIn('Fila vazia e resultado', MAQUINA['HOME_RULE']['SE_A_FILA_ESTIVER_VAZIA'])

    def test_o_estado_medido_hoje_bate_com_o_refresh_corrigido(self):
        e = MAQUINA['ESTADO_MEDIDO_HOJE']
        self.assertEqual(e['ATTENTION_READY'], 0)
        self.assertEqual(e['ATTENTION_CANDIDATE_TEST'], 3)
        self.assertEqual(e['VALID_EVIDENCE_NOT_ATTENTION_READY'], 6)

    def test_unknown_e_transversal_e_nao_ferramenta(self):
        t = MAQUINA['TRANSVERSAL']
        self.assertIn('nunca ferramenta', t['WHAT_IS_STILL_UNKNOWN'])
        self.assertEqual(t['DO_NOT_BUILD'], 'audit dashboard')


class TestMapaDeMangueiras(unittest.TestCase):

    def test_nada_esta_ligado(self):
        self.assertEqual(HOSES['REAL_DATA_WIRED'], 'NO')
        self.assertEqual(HOSES['V8_IMPLEMENTATION_STARTED'], 'NO')
        self.assertEqual(HOSES['CASCO_V7_MODIFIED'], 'NO')

    def test_cada_mangueira_declara_os_oito_campos(self):
        for h in HOSES['HOSES']:
            for campo in ('HOSE_ID', 'SOURCE_COMMIT', 'INPUT_SCHEMA', 'ADAPTER',
                          'CANONICAL_OBJECT', 'OBJECT_TYPE', 'GUARDS',
                          'SURFACE_CONSUMERS', 'FAIL_CLOSED_BEHAVIOR'):
                self.assertIn(campo, h, '%s sem %s' % (h.get('HOSE_ID'), campo))

    def test_toda_mangueira_tem_ao_menos_um_guard(self):
        for h in HOSES['HOSES']:
            self.assertTrue(h['GUARDS'], '%s sem guard' % h['HOSE_ID'])

    def test_os_commits_fixados_existem(self):
        for h in HOSES['HOSES']:
            c = h['SOURCE_COMMIT']
            if c.startswith('in-tree'):
                continue
            o = subprocess.run(['git', 'cat-file', '-t', c], cwd=ROOT,
                               capture_output=True)
            self.assertEqual(o.stdout.decode().strip(), 'commit',
                             '%s aponta para %s, que nao resolve' % (h['HOSE_ID'], c))

    def test_meta_nao_tem_superficie_propria(self):
        m = [h for h in HOSES['HOSES'] if h['HOSE_ID'] == 'H4-META'][0]
        self.assertEqual(m['DO_NOT_BUILD'], 'META_DASHBOARD')
        self.assertIn('NAO e OBJECT_TYPE proprio', m['OBJECT_TYPE'])

    def test_creator_nao_tem_navegacao_propria_no_v8_inicial(self):
        c = [h for h in HOSES['HOSES'] if h['HOSE_ID'] == 'H6-CREATOR'][0]
        self.assertEqual(c['STATE'], 'TEST_AS_CAPABILITY')
        self.assertIn('ENTRY_PATH = FROM_ATTENTION_OBJECT', c['INSTRUMENTAR'])

    def test_expert_exige_portao_de_expertise(self):
        e = [h for h in HOSES['HOSES'] if h['HOSE_ID'] == 'H7-EXPERT'][0]
        self.assertTrue(any('ISSUE_EXPERTISE_PROVED' in g for g in e['GUARDS']))
        self.assertEqual(e['DO_NOT_BUILD'], 'ranking de recorrencia')

    def test_a_ordem_sugerida_cobre_mangueiras_que_existem(self):
        ids = set(h['HOSE_ID'] for h in HOSES['HOSES'])
        for o in HOSES['ORDEM_DE_LIGACAO_SUGERIDA']:
            self.assertIn(o['HOSE'], ids)
            self.assertTrue(o['POR_QUE'])

    def test_a_ordem_e_sugestao_e_nao_instrucao(self):
        self.assertIn('sugestao, nao instrucao', HOSES['NOTA_SOBRE_A_ORDEM'])


class TestDecisoesQueNaoPodemSePerder(unittest.TestCase):
    """As proibicoes duras, uma a uma."""

    def test_a_lista_de_nao_construir_cobre_os_cinco(self):
        d = ' '.join(SCHEMA['DO_NOT_BUILD']).upper()
        for proibido in ('META_DASHBOARD', 'DASHBOARD REGULATORIO', 'AUDIT DASHBOARD',
                         'RANKING DE ESPECIALISTA', 'SCORE'):
            self.assertIn(proibido, d)

    def test_nao_ha_quatro_radares(self):
        d = ' '.join(SCHEMA['DO_NOT_BUILD'])
        self.assertIn('quatro superficies', d)

    def test_expiry_nao_e_withdrawal(self):
        leis = SCHEMA['OBJECT_TYPES']['REGULATORY_DEADLINE']['LAWS']
        self.assertIn('EXPIRY != WITHDRAWAL', leis)
        self.assertIn('EXPIRY_DATE_REACHED != PRODUCT_DISCONTINUED', leis)

    def test_identidade_nao_e_fenomeno(self):
        g = SCHEMA['OBJECT_TYPES']['COMPETITOR_IDENTITY_CHAIN']['GUARDS']
        self.assertTrue(any('IDENTITY_CONVERGENCE != PHENOMENON_CONVERGENCE' in x for x in g))

    def test_raif_nao_vira_segunda_perna_sozinho(self):
        v = SCHEMA['OBJECT_TYPES']['LONGITUDINAL_FIELD_PRESSURE']
        self.assertEqual(v['INDEPENDENCE_FROM_TERRITORIAL_RAIF'],
                         'NOT_PROVED — nao contar como segunda perna sem linhagem parcela-a-parcela')

    def test_os_sete_relogios_nunca_se_fundem(self):
        c = SCHEMA['TIME_BLOCK']['CAMPOS_QUE_NUNCA_SE_FUNDEM']
        self.assertEqual(len(c), 7)
        self.assertIn('STAGE_AT_OBSERVATION', c)
        self.assertIn('CURRENT_CROP_STAGE', c)
        self.assertIn('LABEL_USE_STAGE', c)

    def test_nao_fabricar_calendario(self):
        self.assertIn('Nao fabricar calendario', SCHEMA['TIME_BLOCK']['REGRA'])

    def test_o_icone_oficial_existe_fora_e_nao_se_substitui(self):
        a = SCHEMA['ADAMA_DESIGN']
        self.assertEqual(a['OFFICIAL_ADAMA_DISEASE_ICON_ASSET'],
                         'EXISTS_EXTERNALLY_IN_DESIGN_SYSTEM')
        self.assertEqual(a['DISEASE_ICON_CROSSWALK'], 'NOT_MEASURED')
        self.assertIn('nao criar substituto generico', a['REGRA'])


if __name__ == '__main__':
    unittest.main()
