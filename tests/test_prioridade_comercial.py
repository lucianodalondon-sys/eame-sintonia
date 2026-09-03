#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS DOZE PROVAS DA CAMADA COMERCIAL · V1.1.

Cada teste aqui é um defeito medido, não uma hipótese. T1 e T2 provam o conserto
do red team que acusava a própria advertência; T3 e T4, o da geografia que
tratava a autorização nacional como contradição; T5 a T7, a direção do texto;
T8 e T9, a separação entre os 163 do registro e os 51 do catálogo; T10, o fim do
par cartesiano; T11 e T12, que a régua comercial não conta famílias no escuro.

    UM TESTE QUE NÃO NASCEU DE UM ERRO MEDIDO É UM TESTE QUE PASSA POR SORTE.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_comercial as CM  # noqa: E402
import v21_necessidade as NE  # noqa: E402
import v21_oportunidades as OP  # noqa: E402

ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')


def _pacote(arq):
    p = os.path.join(ING, arq)
    if not os.path.exists(p):
        raise unittest.SkipTest('pacote nao construido: rode scripts/v21_cadeia.sh')
    return json.load(open(p, encoding='utf-8'))['RECORDS']


# ── T1 e T2 · O RED TEAM NÃO PODE ACUSAR A PRÓPRIA ADVERTÊNCIA ───────────────
class TestRedTeamDeShare(unittest.TestCase):
    """D1 · a regex rodava sobre `json.dumps(o)` e casava com o texto FIXO do
    arquétipo O4 — «COMUNICACAO NAO E PARTICIPACAO DE MERCADO... nem share».
    Nenhum dos nove casos O4 podia ser confirmado, e nenhum por mérito.

        O AVISO CONTRA UM ERRO NÃO É O ERRO.
    """

    def _caso(self, **kw):
        o = {'ARCHETYPE': 'O4_COMPETITIVE_OPENING', 'CROP': 'CROP_TOMATO',
             'TARGET': None, 'GEOGRAPHY': 'GEO_ITALY', 'STATUS': 'PREPARE_NOW',
             'GEOGRAPHY_SCOPE': 'NACIONAL',
             'PRODUCT_LINK_STATE': 'VERIFIED_LABEL_MATCH',
             'PRODUCT_RELATIONSHIPS': ['PIRIMOR 50'],
             'WHY_NOW': 'ha pecas correntes de comunicacao de concorrente.',
             'ADAMA_RELEVANCE': 'a ADAMA tem produto autorizado na cultura.',
             'WHAT_IT_PROVES': 'que houve comunicacao publica de concorrente.',
             'WHAT_IT_DOES_NOT_PROVE': OP.TEXTO['O4_COMPETITIVE_OPENING']['NAO_PROVA'],
             'OPPORTUNITY_STATE': OP.CANDIDATA}
        o.update(kw)
        return o

    EV = [{'ID': 'IT-COMP-ACT-002', 'ENTITY_TYPE': 'COMPETITOR_ACTIVITY',
           'CLIENT_SAFE': True, 'SOURCE_DOCUMENT_ID': 'DOC_A', 'REGION_IDS': ['GEO_ITALY']},
          {'ID': 'IT-LBL-016', 'ENTITY_TYPE': 'LABEL_USE_RELATIONSHIP',
           'CLIENT_SAFE': True, 'SOURCE_DOCUMENT_ID': 'DOC_B', 'REGION_IDS': ['GEO_ITALY']},
          {'ID': 'IT-LBL-017', 'ENTITY_TYPE': 'LABEL_USE_RELATIONSHIP',
           'CLIENT_SAFE': True, 'SOURCE_DOCUMENT_ID': 'DOC_C', 'REGION_IDS': ['GEO_ITALY']}]

    def test_T1_advertencia_nao_dispara_o_proprio_red_team(self):
        """A frase fixa do arquétipo contém «PARTICIPACAO» e «share»."""
        o = self._caso()
        self.assertIn('PARTICIPACAO', o['WHAT_IT_DOES_NOT_PROVE'])
        self.assertIn('share', o['WHAT_IT_DOES_NOT_PROVE'])
        achados = OP.red_team(o, self.EV)
        self.assertNotIn('comunicacao de concorrente virou participacao de mercado',
                         achados,
                         'T1: a advertencia contra o erro voltou a ser lida como o erro')

    def test_T2_afirmacao_indevida_de_share_dispara(self):
        """Se o CASO afirmar participação de mercado, a regra tem de acusar."""
        o = self._caso(WHY_NOW='o concorrente ganhou share nesta cultura.')
        achados = OP.red_team(o, self.EV)
        self.assertIn('comunicacao de concorrente virou participacao de mercado',
                      achados,
                      'T2: extrapolacao de participacao de mercado passou sem acusacao')

    def test_T2b_afirmacao_em_qualquer_campo_afirmado_dispara(self):
        o = self._caso(WHAT_IT_PROVES='que a quota de mercado do concorrente subiu.')
        self.assertIn('comunicacao de concorrente virou participacao de mercado',
                      OP.red_team(o, self.EV))

    def test_o_disclaimer_nao_esta_na_lista_do_que_o_caso_afirma(self):
        self.assertNotIn('WHAT_IT_DOES_NOT_PROVE', OP.CAMPOS_AFIRMADOS)


# ── T3 e T4 · A GEOGRAFIA DA AFIRMAÇÃO NÃO É A DA AUTORIZAÇÃO ────────────────
class TestGeografiaDaAfirmacao(unittest.TestCase):
    """D2 · o portão A somava os REGION_IDS de todos os apoios. O rótulo
    ministerial é GEO_ITALY porque a autorização vale no país inteiro, e isso
    derrubava sete casos regionais e provinciais.

        RÓTULO NACIONAL CONTÉM A REGIÃO. CONTER NÃO É CONTRADIZER.
    """

    SINAL_VENETO = {'ID': 'IT-CAN-D9582B1FD6', 'ENTITY_TYPE': 'FIELD_SIGNAL',
                    'CLIENT_SAFE': True, 'REGION_IDS': ['REGION_VENETO'],
                    'GEOGRAPHIC_SCOPE': 'REGIONAL', 'CROP_IDS': ['CROP_APPLE'],
                    'SOURCE_DOCUMENT_ID': 'DOC_VENETO', 'SOURCE_URLS': ['x']}
    ROTULO_ITALIA = {'ID': 'IT-LBL-999', 'ENTITY_TYPE': 'LABEL_USE_RELATIONSHIP',
                     'CLIENT_SAFE': True, 'REGION_IDS': ['GEO_ITALY'],
                     'CROP_IDS': ['CROP_APPLE'], 'SOURCE_DOCUMENT_ID': 'DOC_MIN',
                     'SOURCE_URLS': ['y']}
    SINAL_LOMBARDIA = {'ID': 'IT-PHEN-022', 'ENTITY_TYPE': 'FIELD_SIGNAL',
                       'CLIENT_SAFE': True, 'REGION_IDS': ['REGION_LOMBARDIA'],
                       'GEOGRAPHIC_SCOPE': 'REGIONAL', 'CROP_IDS': ['CROP_APPLE'],
                       'SOURCE_DOCUMENT_ID': 'DOC_LOMB', 'SOURCE_URLS': ['z']}

    def _o(self):
        return {'ARCHETYPE': 'O1_FIELD_PRESSURE', 'CROP': 'CROP_APPLE',
                'TARGET': 'ISSUE_CODLING_MOTH', 'GEOGRAPHY': 'REGION_VENETO',
                'GEOGRAPHY_SCOPE': 'REGIONAL', 'WINDOW_STATE': 'UNKNOWN',
                'SIGNAL_AGE_DAYS': 7, 'PRODUCT_LINK_STATE': 'VERIFIED_LABEL_MATCH',
                'OPPORTUNITY_STATE': OP.CANDIDATA}

    def test_T3_veneto_mais_rotulo_nacional_nao_e_conflito(self):
        falhas = OP.portoes(self._o(), [self.SINAL_VENETO, self.ROTULO_ITALIA])
        geo = [f for f in falhas if f.startswith('A_GEOGRAFIA')]
        self.assertEqual([], geo,
                         'T3: a autorizacao nacional voltou a derrubar o caso regional')

    def test_T4_rotulo_nacional_nao_promove_o_sinal_a_italia(self):
        """A autorização não muda a geografia da afirmação: ela continua Veneto."""
        o = self._o()
        self.assertEqual('REGION_VENETO', o['GEOGRAPHY'])
        # e duas regiões de OBSERVAÇÃO continuam sendo conflito
        falhas = OP.portoes(o, [self.SINAL_VENETO, self.SINAL_LOMBARDIA,
                                self.ROTULO_ITALIA])
        self.assertTrue([f for f in falhas if f.startswith('A_GEOGRAFIA')],
                        'T4: duas geografias de observacao deixaram de ser conflito')

    def test_o_rotulo_nao_esta_entre_os_tipos_que_observam(self):
        self.assertNotIn('LABEL_USE_RELATIONSHIP', OP.TIPOS_QUE_OBSERVAM)
        self.assertIn('LABEL_USE_RELATIONSHIP', OP.TIPOS_DE_AUTORIZACAO)

    def test_o_caso_testemunha_separa_as_tres_geografias(self):
        r = [x for x in _pacote('OPPORTUNITIES.json') if x['ID'] == 'OPP_75C37DED9160']
        if not r:
            self.skipTest('testemunha ausente do pacote construido')
        r = r[0]
        self.assertEqual('REGION_VENETO', r['CLAIM_GEOGRAPHY'])
        self.assertEqual(['REGION_VENETO'], r['FIELD_GEOGRAPHY'])
        self.assertEqual(['GEO_ITALY'], r['PRODUCT_AUTHORIZATION_GEOGRAPHY'])
        self.assertTrue(r['CLAIM_GEOGRAPHY_HOLDS'])


# ── T5, T6, T7 · A DIREÇÃO DO TEXTO ──────────────────────────────────────────
class TestDirecaoDaNecessidade(unittest.TestCase):
    """As frases são as que a auditoria mediu, copiadas dos boletins."""

    def test_T5_non_necessari_interventi_nao_e_pressao_positiva(self):
        d, _ = NE.direcao('Peronospora: «In generale non necessari interventi.»')
        self.assertEqual(NE.NO_ACTION_RECOMMENDED, d)
        self.assertNotEqual(NE.POSITIVE_PRESSURE, d)

    def test_T5b_suspensao_nao_e_pressao_positiva(self):
        d, _ = NE.direcao('Defesa antiperonosporica pode ser suspensa nas vinhas '
                          'com invaiatura completa')
        self.assertEqual(NE.ACTION_SUSPENDED, d)

    def test_T5c_janela_concluida_nao_e_act_now(self):
        d, _ = NE.direcao('a defesa contra Scaphoideus titanus pode considerar-se '
                          'concluida')
        self.assertEqual(NE.WINDOW_CONCLUDED, d)

    def test_T6_danni_in_aumento_gera_pressao_positiva(self):
        d, _ = NE.direcao(
            'O boletim frutticolo do Veneto declara terminada a colheita das '
            'variedades do grupo Gala e reporta terceiro voo de Cydia pomonella '
            'terminado com danos em aumento tambem em pomares de manejo integrado.')
        self.assertEqual(NE.POSITIVE_PRESSURE, d,
                         'T6: «danos em aumento» deixou de ser necessidade positiva')

    def test_T6b_voo_terminado_nao_e_janela_concluida(self):
        """Palavra solta não classifica: o que terminou foi o voo, não a defesa."""
        d, _ = NE.direcao('terceiro voo de Cydia pomonella terminado')
        self.assertNotEqual(NE.WINDOW_CONCLUDED, d)

    def test_T7_proibicao_nao_vira_act_now_comercial(self):
        d, _ = NE.direcao('durante a floracao VIGORA A PROIBICAO de intervencao '
                          'fitoiatrica com inseticidas, para tutela das abelhas')
        self.assertEqual(NE.TREATMENT_PROHIBITED, d)
        pri, _ = CM.prioridade({
            'ARCHETYPE': 'O1_FIELD_PRESSURE', 'TARGET': 'ISSUE_DIABROTICA',
            'NEED_DIRECTION': d, 'COMMERCIAL_PRODUCT_COUNT': 3,
            'PRODUCT_LINK_STATE': 'VERIFIED_LABEL_MATCH',
            'CLAIM_GEOGRAPHY_HOLDS': True, 'COMMERCIAL_WINDOW': 'ACT_NOW'})
        self.assertEqual(CM.TO_VALIDATE, pri,
                         'T7: uma proibicao de tratar voltou a virar oportunidade')

    def test_a_que_manda_parar_vence_a_que_manda_agir(self):
        self.assertEqual(NE.ACTION_SUSPENDED,
                         NE._mais_restritiva([NE.POSITIVE_PRESSURE,
                                              NE.ACTION_SUSPENDED]))

    def test_o_trecho_original_viaja_com_a_classificacao(self):
        for r in _pacote('OPPORTUNITIES.json'):
            if r['NEED_DIRECTION'] != NE.UNKNOWN:
                self.assertTrue(r['NEED_EXCERPT'],
                                '%s classifica sem guardar a frase' % r['ID'])
                self.assertTrue(r['NEED_EVIDENCE_ID'],
                                '%s classifica sem citar o apoio' % r['ID'])


# ── T8 e T9 · OS 163 NÃO SÃO OS 51 ───────────────────────────────────────────
class TestCatalogoComercial(unittest.TestCase):

    def setUp(self):
        self.com = _pacote('PRODUCTS-COMMERCIAL.json')
        self.ix = CM.indice_comercial(self.com)

    def test_T8_produto_regulatorio_nao_vira_comercial_automaticamente(self):
        reg = _pacote('PRODUCTS-REGULATORY.json')
        self.assertGreater(len(reg), len(self.com))
        so_registro = [p for p in reg
                       if CM.num(p.get('REGISTRATION_NUMBER')) not in self.ix]
        self.assertTrue(so_registro,
                        'T8: todo produto do registro passou a contar como comercial')
        casados = CM.casar([{'REGISTRATION_NUMBER': so_registro[0]['REGISTRATION_NUMBER']}],
                           self.ix)
        self.assertEqual(0, casados['COMMERCIAL_PRODUCT_COUNT'])

    def test_T9_produto_do_catalogo_comercial_e_reconhecido(self):
        alvo = next(p for p in self.com if p.get('MATCHED_REGULATORY_ID'))
        casados = CM.casar([{'REGISTRATION_NUMBER': alvo['MATCHED_REGULATORY_ID']}],
                           self.ix)
        self.assertEqual(1, casados['COMMERCIAL_PRODUCT_COUNT'])
        self.assertIn(alvo['NAME'], casados['MATCHED_COMMERCIAL_PRODUCT_NAMES'])
        self.assertIn(alvo['ID'], casados['MATCHED_COMMERCIAL_PRODUCT_IDS'])

    def test_o_casamento_e_por_numero_e_nunca_por_nome(self):
        """`Lamdex® Extra`, `LAMDEX EXTRA` e `Lamdex Extra` sao a mesma coisa."""
        alvo = next(p for p in self.com if p.get('MATCHED_REGULATORY_ID'))
        n = alvo['MATCHED_REGULATORY_ID']
        self.assertEqual(CM.casar([{'REGISTRATION_NUMBER': n}], self.ix),
                         CM.casar([{'REGISTRATION_NUMBER': ' %s ' % n}], self.ix))
        self.assertEqual(0, CM.casar([{'PRODUCT_NAME': alvo['NAME']}],
                                     self.ix)['COMMERCIAL_PRODUCT_COUNT'])

    def test_o_catalogo_comercial_entra_de_fato_na_decisao(self):
        regs = _pacote('OPPORTUNITIES.json')
        self.assertTrue(any(r['COMMERCIAL_PRODUCT_COUNT'] for r in regs),
                        'o catalogo comercial voltou a ser carregado e ignorado')
        for r in regs:
            self.assertIn('MATCHED_COMMERCIAL_PRODUCT_IDS', r)


# ── T10 · O PAR NÃO É PRODUTO CARTESIANO ─────────────────────────────────────
class TestParObservado(unittest.TestCase):

    def test_T10_lista_de_culturas_x_lista_de_alvos_nao_faz_par(self):
        """Um boletim de dez culturas com um alvo não produz dez pares."""
        sinal = {'ID': 'IT-PHEN-TESTE',
                 'CROP_IDS': ['CROP_PEAR', 'CROP_APPLE', 'CROP_SUGAR_BEET',
                              'CROP_SOYBEAN', 'CROP_GRAPEVINE'],
                 'ISSUE_IDS': ['ISSUE_SCAB'],
                 'PESTS_AND_DISEASES_CITED': ['Ticchiolatura', 'Maculatura bruna'],
                 'INTERVENTION_GUIDANCE':
                     'Vite/botrite: intervir em pre-colheita com Fenhexamid.'}
        pares = {(p['CROP_ID'], p['ISSUE_ID']) for p in NE.pares_observados(sinal)}
        self.assertEqual({('CROP_GRAPEVINE', 'ISSUE_BOTRYTIS')}, pares,
                         'T10: o par voltou a sair do cruzamento de duas listas')
        self.assertNotIn(('CROP_SUGAR_BEET', 'ISSUE_SCAB'), pares)
        self.assertNotIn(('CROP_SOYBEAN', 'ISSUE_SCAB'), pares)

    def test_T10b_o_alvo_nunca_vem_do_cabecalho_do_documento(self):
        sinal = {'ID': 'X', 'CROP_IDS': ['CROP_PEAR'], 'ISSUE_IDS': ['ISSUE_SCAB'],
                 'INTERVENTION_GUIDANCE': 'Pero: fase fenologica de maturacao.'}
        self.assertEqual([], NE.pares_observados(sinal))

    def test_T10c_sem_cultura_declarada_nao_ha_par(self):
        """Ler prosa para adivinhar a cultura foi o erro do V2."""
        sinal = {'ID': 'Y', 'CROP_IDS': [], 'ISSUE_IDS': ['ISSUE_POWDERY_MILDEW'],
                 'INTERVENTION_GUIDANCE':
                     'intervir SO em presenca de condicoes favoraveis a peronospora, '
                     'pelas estacoes agrometeorologicas mais proximas'}
        self.assertEqual([], NE.pares_observados(sinal),
                         'T10c: «mais proximas» voltou a virar CROP_MAIZE')

    def test_o_titulo_do_boletim_declara_o_par(self):
        sinal = {'ID': 'Z', 'CROP_IDS': ['CROP_MAIZE'],
                 'BULLETIN_TITLE': 'Bollettino di difesa integrata COLTURE ERBACEE '
                                   '— Piralide del mais (ERSA FVG)',
                 'INTERVENTION_GUIDANCE': 'Limiar declarado: tratamento insecticida '
                                          'justificado quando se observarem posturas '
                                          'superiores a 3 por cada 100 plantas.'}
        pares = {(p['CROP_ID'], p['ISSUE_ID']): p for p in NE.pares_observados(sinal)}
        self.assertIn(('CROP_MAIZE', 'ISSUE_CORN_BORER'), pares)
        p = pares[('CROP_MAIZE', 'ISSUE_CORN_BORER')]
        self.assertEqual('PAIR_IN_DOCUMENT_TITLE', p['NEED_METHOD'])
        self.assertEqual(NE.POSITIVE_PRESSURE, p['NEED_DIRECTION'])

    def test_nenhum_par_do_pacote_sai_sem_metodo_declarado(self):
        for r in _pacote('OPPORTUNITIES.json'):
            if r['ARCHETYPE'] == 'O1_FIELD_PRESSURE':
                self.assertIn(r['NEED_METHOD'], NE.FORCA_DO_METODO,
                              '%s tem par sem metodo de atribuicao' % r['ID'])


# ── T11 e T12 · CORROBORAÇÃO É AMPLIFICADOR, NÃO CONTADOR CEGO ───────────────
class TestReguaComercial(unittest.TestCase):

    FORTE = {'ARCHETYPE': 'O1_FIELD_PRESSURE', 'TARGET': 'ISSUE_CODLING_MOTH',
             'NEED_DIRECTION': NE.POSITIVE_PRESSURE, 'COMMERCIAL_PRODUCT_COUNT': 2,
             'PRODUCT_LINK_STATE': 'VERIFIED_LABEL_MATCH',
             'CLAIM_GEOGRAPHY_HOLDS': True, 'COMMERCIAL_WINDOW': 'ACT_NOW'}

    def test_T11_uma_fonte_oficial_forte_basta_para_sales_ready(self):
        """Sem exigir três famílias externas, se os demais portões fecham."""
        pri, _ = CM.prioridade(dict(self.FORTE))
        self.assertEqual(CM.SALES_READY, pri)

    def test_T11b_o_caso_testemunha_e_sales_ready_com_uma_familia(self):
        r = [x for x in _pacote('OPPORTUNITIES.json') if x['ID'] == 'OPP_75C37DED9160']
        if not r:
            self.skipTest('testemunha ausente do pacote construido')
        r = r[0]
        self.assertEqual(CM.SALES_READY, r['COMMERCIAL_PRIORITY'])
        externas = [f for f in r['EVIDENCE_FAMILIES']
                    if f not in OP.TIPOS_DE_AUTORIZACAO]
        self.assertEqual(1, len(externas),
                         'a testemunha deixou de ser o caso de familia unica')

    def test_T12_muitas_familias_fracas_nao_geram_sales_ready(self):
        fraco = {'ARCHETYPE': 'O4_COMPETITIVE_OPENING', 'TARGET': None,
                 'NEED_DIRECTION': NE.UNKNOWN, 'COMMERCIAL_PRODUCT_COUNT': 9,
                 'PRODUCT_LINK_STATE': 'VERIFIED_LABEL_MATCH',
                 'CLAIM_GEOGRAPHY_HOLDS': True, 'COMMERCIAL_WINDOW': 'ACT_NOW',
                 'EVIDENCE_FAMILIES': ['COMPETITOR_ACTIVITY', 'MARKET_OBSERVATION',
                                       'SCIENTIFIC_RECORD', 'PUBLIC_VOICE']}
        pri, _ = CM.prioridade(fraco)
        self.assertNotEqual(CM.SALES_READY, pri)
        self.assertEqual(CM.COMMERCIAL_WATCH, pri)

    def test_T12b_necessidade_fechada_nao_vende_por_muito_produto(self):
        o = dict(self.FORTE, NEED_DIRECTION=NE.ACTION_SUSPENDED,
                 COMMERCIAL_PRODUCT_COUNT=25)
        self.assertEqual(CM.TO_VALIDATE, CM.prioridade(o)[0])

    def test_score_alto_nao_promove_de_categoria(self):
        regs = _pacote('OPPORTUNITIES.json')
        altos = [r for r in regs if r['OPPORTUNITY_SCORE'] >= 10
                 and r['NEED_DIRECTION'] in CM.NECESSIDADE_FECHADA]
        for r in altos:
            self.assertEqual(CM.TO_VALIDATE, r['COMMERCIAL_PRIORITY'],
                             '%s subiu de categoria pelo score' % r['ID'])

    def test_a_prioridade_nao_substitui_o_estado(self):
        """São duas perguntas: uma pode ser CONFIRMADA e não vender."""
        regs = _pacote('OPPORTUNITIES.json')
        for r in regs:
            self.assertIn(r['COMMERCIAL_PRIORITY'], CM.PRIORIDADES)
            self.assertIn(r['OPPORTUNITY_STATE'], (OP.CONFIRMADA, OP.CANDIDATA))
        confirmadas_que_nao_vendem = [
            r for r in regs if r['OPPORTUNITY_STATE'] == OP.CONFIRMADA
            and r['COMMERCIAL_PRIORITY'] != CM.SALES_READY]
        self.assertTrue(confirmadas_que_nao_vendem,
                        'as duas colunas viraram a mesma coluna')


# ── INVARIANTES · o que nenhuma versão pode passar a dizer ───────────────────
class TestInvariantes(unittest.TestCase):

    PROIBIDO = ('sell-in', 'sell in', 'sell-out', 'sell out', 'demanda de revenda',
                'estoque disponivel', 'pedido colocado', 'intencao de compra',
                'pipeline de vendas')

    def test_nenhum_campo_infere_demanda_interna(self):
        for r in _pacote('OPPORTUNITIES.json'):
            texto = json.dumps(r, ensure_ascii=False).lower()
            for termo in self.PROIBIDO:
                # o termo só pode aparecer dentro de uma NEGAÇÃO declarada
                if termo in texto:
                    self.assertIn('nao prova', texto,
                                  '%s cita «%s» fora de uma negacao' % (r['ID'], termo))

    def test_toda_oportunidade_declara_o_que_nao_prova_comercialmente(self):
        for r in _pacote('OPPORTUNITIES.json'):
            self.assertEqual(CM.NAO_PROVA, r['COMMERCIAL_DOES_NOT_PROVE'])

    def test_client_safe_continua_falso_em_todas(self):
        for r in _pacote('OPPORTUNITIES.json'):
            self.assertFalse(r['CLIENT_SAFE'],
                             'a lei do client-safe foi afrouxada em %s' % r['ID'])


if __name__ == '__main__':
    unittest.main(verbosity=2)


# ── T13-T18 · SALES_READY NÃO AUTORIZA SAÍDA EXTERNA ─────────────────────────
class TestMaterialExterno(unittest.TestCase):
    """`SALES_READY` responde «isto vende?». Enviar a um revendedor ou a um RTV
    é outra pergunta, e ela é pública.

        VENDER É UMA DECISÃO INTERNA. ENVIAR É UMA AFIRMAÇÃO PÚBLICA.
    """

    PRONTO = {'COMMERCIAL_PRIORITY': CM.SALES_READY, 'CROP': 'CROP_APPLE',
              'BLOCKING_GATES': [], 'RED_TEAM_FINDINGS': [],
              'NEED_EXCERPT': 'danos em aumento', 'WINDOW_KIND': None}
    CATALOGO = [{'NAME': 'MAVRIK SMART',
                 'CROPS_DECLARED_ON_SITE': ['CEREALI', 'POMACEE', 'VITE']}]

    def test_T13_sales_ready_sem_pendencia_pode_sair(self):
        e, b = CM.externo(dict(self.PRONTO), self.CATALOGO)
        self.assertEqual(CM.EXTERNAL_YES, e)
        self.assertEqual([], b)

    def test_T14_sales_ready_com_portao_aberto_nao_sai(self):
        """E continua SALES_READY internamente: as duas colunas não se fundem."""
        o = dict(self.PRONTO, BLOCKING_GATES=['A_GEOGRAFIA · apoios em geografias'])
        e, b = CM.externo(o, self.CATALOGO)
        self.assertEqual(CM.EXTERNAL_VALIDATION_REQUIRED, e)
        self.assertIn('EVIDENCE_GATE_OPEN', b)
        self.assertEqual(CM.SALES_READY, o['COMMERCIAL_PRIORITY'],
                         'a coluna interna foi rebaixada pela externa')

    def test_T15_data_de_ato_nao_pode_ir_como_janela(self):
        o = dict(self.PRONTO, WINDOW_KIND='PREPARATION')
        e, b = CM.externo(o, self.CATALOGO)
        self.assertEqual(CM.EXTERNAL_VALIDATION_REQUIRED, e)
        self.assertIn('WINDOW_IS_ADMINISTRATIVE', b)

    def test_T16_catalogo_que_nao_declara_a_cultura_bloqueia(self):
        """Medido: `Lamdex® Extra` tem rótulo em MELO × CARPOCAPSA, e a página
        de catálogo dele declara MAIS, POMODORO e VITE — macieira não está lá."""
        so_lamdex = [{'NAME': 'Lamdex® Extra',
                      'CROPS_DECLARED_ON_SITE': ['MAIS', 'POMODORO', 'VITE']}]
        e, b = CM.externo(dict(self.PRONTO), so_lamdex)
        self.assertEqual(CM.EXTERNAL_VALIDATION_REQUIRED, e)
        self.assertIn('CATALOG_DOES_NOT_DECLARE_CROP', b)
        # e o mesmo caso passa quando um produto do catálogo declara POMACEE
        self.assertEqual(CM.EXTERNAL_YES,
                         CM.externo(dict(self.PRONTO), so_lamdex + self.CATALOGO)[0])

    def test_T17_recomendacao_sem_frase_da_fonte_nao_sai(self):
        e, b = CM.externo(dict(self.PRONTO, NEED_EXCERPT=''), self.CATALOGO)
        self.assertIn('NO_SOURCE_SENTENCE', b)

    def test_T18_o_que_nao_vende_internamente_nunca_sai(self):
        for pri in (CM.SALES_PREPARE, CM.COMMERCIAL_WATCH,
                    CM.STRATEGIC_OPPORTUNITY, CM.TO_VALIDATE):
            e, b = CM.externo(dict(self.PRONTO, COMMERCIAL_PRIORITY=pri),
                              self.CATALOGO)
            self.assertEqual(CM.EXTERNAL_NO, e, pri)
            self.assertEqual(['NOT_SALES_READY'], b)

    def test_red_team_aberto_bloqueia_saida(self):
        e, b = CM.externo(dict(self.PRONTO, RED_TEAM_FINDINGS=['x']), self.CATALOGO)
        self.assertIn('RED_TEAM_FINDING', b)

    def test_no_pacote_a_saida_externa_nunca_excede_a_interna(self):
        for r in _pacote('OPPORTUNITIES.json'):
            self.assertIn(r['EXTERNAL_MATERIAL_READY'],
                          (CM.EXTERNAL_YES, CM.EXTERNAL_VALIDATION_REQUIRED,
                           CM.EXTERNAL_NO))
            if r['COMMERCIAL_PRIORITY'] != CM.SALES_READY:
                self.assertEqual(CM.EXTERNAL_NO, r['EXTERNAL_MATERIAL_READY'],
                                 '%s sai sem ser SALES_READY' % r['ID'])
            if r['EXTERNAL_MATERIAL_READY'] == CM.EXTERNAL_YES:
                self.assertEqual([], r['BLOCKING_GATES'], r['ID'])
                self.assertEqual([], r['RED_TEAM_FINDINGS'], r['ID'])
                self.assertTrue(r['NEED_EXCERPT'], r['ID'])
                self.assertNotEqual('PREPARATION', r['WINDOW_KIND'], r['ID'])
