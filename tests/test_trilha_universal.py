#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DA TRILHA UNIVERSAL E DO CONTRATO COMERCIAL.

Cada teste aqui nasceu de uma coisa medida nesta missão, não de uma hipótese
sobre o que poderia dar errado.

    U1–U4   a catraca SÓ SEGURA: nunca promove, e o que ela promete é o que
            `v21_comercial.externo()` já decidiu.
    U5–U7   o material que não completou etapa obrigatória fica visível, e o
            que falhou não sustenta publicável.
    U8–U9   o censo da porta: buraco declarado é declarado, buraco novo para.
    U10–U13 WHY_NOW é estritamente mais conservador que COMMERCIAL_WINDOW, e
            ACT_NOW não nasce de janela UNKNOWN.
    U14–U17 o portfólio traz TODOS os que cabem no par, e PRIMARY_MATCH só sai
            com regra defensável.
    U18–U20 a evidência negativa continua podendo esfriar oportunidade.
    U21–U23 nenhuma oportunidade nasceu da camada nova, e nenhum produto foi
            promovido para preencher tela.
    U24     a aceitação virou portão de verdade.
    U25     a testemunha universal atravessou.

    UM TESTE QUE NÃO NASCEU DE UM ERRO MEDIDO É UM TESTE QUE PASSA POR SORTE.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_briefing as BR      # noqa: E402
import v21_catraca as CAT      # noqa: E402
import v21_comercial as CM     # noqa: E402

ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')


def _pacote(arq):
    p = os.path.join(ING, arq)
    if not os.path.exists(p):
        raise unittest.SkipTest('pacote nao construido: rode scripts/v21_cadeia.sh')
    return json.load(open(p, encoding='utf-8'))


def _recs(arq):
    return _pacote(arq)['RECORDS']


# ═══════════════════════════════════════════════════════════════════════════
# U1–U4 · A CATRACA SÓ SEGURA
# ═══════════════════════════════════════════════════════════════════════════
class CatracaNuncaPromove(unittest.TestCase):

    def test_U1_catraca_nunca_promove(self):
        """A propriedade que faz desta camada uma catraca, e não um motor.

        Se algum dia `PUBLICATION_STATE` ficar MAIS permissivo que
        `EXTERNAL_MATERIAL_READY`, esta camada virou um segundo dono da decisão
        de publicar — que é exatamente o que a missão proíbe.
        """
        for o in _recs('OPPORTUNITIES.json'):
            de_fora = CAT.DE_EXTERNO.get(o.get('EXTERNAL_MATERIAL_READY'),
                                         CAT.GATE_UNKNOWN)
            self.assertGreaterEqual(
                CAT.PERMISSIVIDADE[o['PUBLICATION_STATE']],
                CAT.PERMISSIVIDADE[de_fora],
                '%s: a catraca PROMOVEU (de %s para %s)'
                % (o['ID'], de_fora, o['PUBLICATION_STATE']))

    def test_U2_publicavel_exige_external_yes(self):
        """PUBLISHABLE não nasce em lugar nenhum além do YES da régua comercial."""
        for o in _recs('OPPORTUNITIES.json'):
            if o['PUBLICATION_STATE'] == CAT.PUBLISHABLE:
                self.assertEqual('YES', o['EXTERNAL_MATERIAL_READY'], o['ID'])

    def test_U3_o_gate_declara_os_quatro_estados(self):
        d = _pacote('PUBLICATION-GATE.json')
        self.assertEqual(['PUBLISHABLE', 'VALIDATION_REQUIRED', 'UNKNOWN',
                          'QUARANTINED'], d['PUBLICATION_STATES'])

    def test_U4_evidencia_quarentenada_rebaixa(self):
        """Prova pela função, não pelo dado: hoje não há material em quarentena.

        Um teste que só olhasse o pacote diria «passou» num pacote onde a regra
        nunca é exercida. Este exercita a regra.
        """
        censo = {'EV_OK': {'MATERIAL_STATE': CAT.MATERIAL_PASSED},
                 'EV_RUIM': {'MATERIAL_STATE': CAT.MATERIAL_QUARANTINED}}
        o = {'EXTERNAL_MATERIAL_READY': 'YES', 'EVIDENCE_IDS': ['EV_OK']}
        est, trilha, _q, _i, _a = CAT.estado_de_publicacao(o, censo)
        self.assertEqual((CAT.PUBLISHABLE, 'COMPLETE'), (est, trilha))

        o['EVIDENCE_IDS'] = ['EV_OK', 'EV_RUIM']
        est, trilha, quar, _i, _a = CAT.estado_de_publicacao(o, censo)
        self.assertEqual((CAT.QUARANTINED, 'BROKEN'), (est, trilha))
        self.assertEqual(['EV_RUIM'], quar)

        o['EVIDENCE_IDS'] = ['EV_OK', 'EV_QUE_NAO_EXISTE']
        est, trilha, _q, _i, aus = CAT.estado_de_publicacao(o, censo)
        self.assertEqual((CAT.QUARANTINED, 'BROKEN'), (est, trilha))
        self.assertEqual(['EV_QUE_NAO_EXISTE'], aus)


# ═══════════════════════════════════════════════════════════════════════════
# U5–U7 · O QUE NÃO COMPLETOU A TRILHA FICA VISÍVEL
# ═══════════════════════════════════════════════════════════════════════════
class MaterialVisivel(unittest.TestCase):

    def test_U5_registro_sem_qa_status_e_quarentena(self):
        et, mot = CAT.etapas_do_registro(
            {'ID': 'X', 'ENTITY_TYPE': 'FIELD_SIGNAL', 'PROVENANCE': 'REAL_SOURCE',
             'SOURCE_URLS': ['http://x'], 'CROP_IDS': [], 'ISSUE_IDS': [],
             'REGION_IDS': [], 'GEOGRAPHIC_SCOPE': 'NACIONAL',
             'WHAT_IT_IS': 'x'})
        self.assertEqual(CAT.FAILED, et['CLASSIFICATION'])
        self.assertIn('NO_QA_STATUS', mot)
        self.assertEqual(CAT.MATERIAL_QUARANTINED, CAT.estado_do_material(et))

    def test_U6_boletim_sem_texto_fica_UNKNOWN_e_nao_some(self):
        """Os quatro boletins reais que chegavam ao motor MUDOS.

        `IT-CAN-71D68FCB7D`, `IT-CAN-6EFC8DC91A`, `IT-CAN-EB63AEC4AA` e
        `IT-CAN-49BA29FF51` têm a leitura só em `RESEARCH.o_que`, e
        `promover_research` é tudo-ou-nada. Antes desta camada eles eram
        ignorados em silêncio. O comportamento NÃO mudou — o silêncio, sim.
        """
        gate = _pacote('PUBLICATION-GATE.json')
        mudos = {r['RECORD_ID'] for r in gate['RECORDS']
                 if 'NO_TEXT_FOR_PAIR_EXTRACTION' in r['REASON_CODES']}
        for rid in ('IT-CAN-71D68FCB7D', 'IT-CAN-6EFC8DC91A',
                    'IT-CAN-EB63AEC4AA', 'IT-CAN-49BA29FF51'):
            self.assertIn(rid, mudos, '%s voltou a sumir em silencio' % rid)
        self.assertGreater(gate['BY_REASON_CODE'].get(
            'NO_TEXT_FOR_PAIR_EXTRACTION', 0), 0)

    def test_U7_localizacao_e_UNKNOWN_nao_falha(self):
        """Lacuna de tradução não é falha de inteligência.

        A primeira versão desta missão pôs `AINDA_SO_EM_PORTUGUES` na lista
        fatal da aceitação, e a testemunha universal mostrou o efeito: um
        boletim novo qualquer parava a cadeia inteira. A consequência passou a
        ser do REGISTRO, e o estado é UNKNOWN — nunca FAILED.
        """
        et, mot = CAT.etapas_do_registro(
            {'ID': 'X', 'ENTITY_TYPE': 'FIELD_SIGNAL', 'PROVENANCE': 'REAL_SOURCE',
             'SOURCE_URLS': ['http://x'], 'QA_STATUS': 'QA_PASS',
             'CLIENT_SAFE': True, 'CROP_IDS': [], 'ISSUE_IDS': [],
             'REGION_IDS': [], 'GEOGRAPHIC_SCOPE': 'NACIONAL',
             'WHAT_IT_IS': 'o boletim registra que a doenca foi observada nesta '
                           'cultura e nao prova incidencia'})
        self.assertEqual(CAT.UNKNOWN, et['LOCALIZATION'])
        self.assertIn('READING_ONLY_IN_PORTUGUESE', mot)
        self.assertEqual(CAT.MATERIAL_INCOMPLETE, CAT.estado_do_material(et))


# ═══════════════════════════════════════════════════════════════════════════
# U8–U9 · O CENSO DA PORTA
# ═══════════════════════════════════════════════════════════════════════════
class CensoDaPorta(unittest.TestCase):

    def test_U8_as_duas_familias_que_nao_entram_estao_declaradas(self):
        """Foi a testemunha universal que as achou. Agora têm nome e motivo."""
        d = _pacote('PUBLICATION-GATE.json')
        censo = d['DOOR_CENSUS']
        for fam in ('COMMERCIAL_CATALOG', 'HERBICIDE_CURRENT_CONTEXT'):
            self.assertIn(fam, censo)
            self.assertEqual(0, censo[fam]['NO_PACOTE'], fam)
            self.assertTrue(censo[fam]['DECLARADA_COMO_NAO_INGERIDA'], fam)
            self.assertTrue(censo[fam]['WHY'], fam)
        # E as outras oito entram inteiras.
        for fam, v in censo.items():
            if fam in CAT.FAMILIA_NAO_INGERIDA:
                continue
            self.assertEqual(0, v['SUMIRAM'],
                             '%s passou a perder registro na porta' % fam)

    def test_U9_buraco_novo_para_a_cadeia(self):
        """Uma família não declarada que sume é violação, não nota de rodapé."""
        d = _pacote('PUBLICATION-GATE.json')
        self.assertEqual([], d['VIOLATIONS']['V5_FAMILIA_SUMIU_NA_PORTA_SEM_DECLARACAO'])
        self.assertEqual(0, d['VIOLATION_COUNT'])


# ═══════════════════════════════════════════════════════════════════════════
# U10–U13 · WHY_NOW NUNCA INFLA
# ═══════════════════════════════════════════════════════════════════════════
class PorQueAgora(unittest.TestCase):

    def test_U10_why_now_nunca_infla(self):
        """A camada nova não pode criar urgência que a régua não deu.

            ACT_NOW POR COPY É A MENTIRA MAIS BARATA QUE UM PORTAL PODE CONTAR.
        """
        opp = {o['ID']: o for o in _recs('OPPORTUNITIES.json')}
        brf = _recs('OPPORTUNITY-BRIEFINGS.json')
        n_act = sum(1 for b in brf if b['WHY_NOW'] == BR.ACT_NOW)
        n_janela = sum(1 for o in opp.values()
                       if o.get('COMMERCIAL_WINDOW') == 'ACT_NOW')
        self.assertLessEqual(n_act, n_janela,
                             'WHY_NOW=ACT_NOW passou COMMERCIAL_WINDOW=ACT_NOW')

    def test_U11_act_now_exige_janela_de_aplicacao(self):
        for b in _recs('OPPORTUNITY-BRIEFINGS.json'):
            if b['WHY_NOW'] != BR.ACT_NOW:
                continue
            self.assertEqual('APPLICATION', b['WINDOW']['KIND'], b['ID'])
            self.assertNotEqual('UNKNOWN', b['WINDOW']['STATE'], b['ID'])

    def test_U12_janela_unknown_com_venda_pronta_e_VALIDATE_NOW(self):
        """A regra pela função, para valer mesmo se o pacote mudar."""
        base = {'NEED_DIRECTION': 'POSITIVE_PRESSURE',
                'COMMERCIAL_PRIORITY': CM.SALES_READY,
                'COMMERCIAL_WINDOW': 'ACT_NOW',
                'WINDOW_STATE': 'UNKNOWN', 'WINDOW_KIND': None}
        self.assertEqual((BR.VALIDATE_NOW, ['WN_NO_APPLICATION_WINDOW']),
                         BR.por_que_agora(base))
        com_janela = dict(base, WINDOW_STATE='EXACT', WINDOW_KIND='APPLICATION')
        self.assertEqual((BR.ACT_NOW, ['WN_APPLICATION_WINDOW_OPEN']),
                         BR.por_que_agora(com_janela))

    def test_U13_fonte_que_manda_parar_fecha(self):
        for d in CM.NECESSIDADE_FECHADA:
            estado, cod = BR.por_que_agora(
                {'NEED_DIRECTION': d, 'COMMERCIAL_PRIORITY': CM.SALES_READY,
                 'WINDOW_STATE': 'EXACT', 'WINDOW_KIND': 'APPLICATION',
                 'COMMERCIAL_WINDOW': 'ACT_NOW'})
            self.assertEqual((BR.CLOSED, ['WN_SOURCE_SAYS_STOP']), (estado, cod),
                             '%s deixou de fechar a porta' % d)


# ═══════════════════════════════════════════════════════════════════════════
# U14–U17 · O PORTFÓLIO
# ═══════════════════════════════════════════════════════════════════════════
class Portfolio(unittest.TestCase):

    def test_U14_todos_os_matches_do_par_e_nao_so_o_primeiro(self):
        """Botrite × videira: três produtos com par de rótulo verificado."""
        b = self._botrite()
        nomes = sorted(m['PRODUCT_NAME'] for m in b['PORTFOLIO_MATCHES'])
        self.assertEqual(['AGHARTA', 'BANJO', 'EMBRACE'], nomes)
        for m in b['PORTFOLIO_MATCHES']:
            self.assertEqual(BR.M_VERIFIED, m['MATCH_STATE'])
            self.assertTrue(m['ACTIVE_SUBSTANCES'], m['PRODUCT_NAME'])
            self.assertTrue(m['TARGET_FIT']['EVIDENCE_IDS'], m['PRODUCT_NAME'])

    def test_U15_cobertura_de_cultura_nao_vira_match_de_alvo(self):
        """22 produtos têm videira no rótulo e não têm botrite. Ficam fora — e contados."""
        b = self._botrite()
        self.assertEqual(3, b['PORTFOLIO_MATCH_COUNT'])
        self.assertGreater(b['CROP_LEVEL_ONLY_COUNT'], 0)
        for m in b['PORTFOLIO_MATCHES']:
            self.assertEqual('ISSUE_BOTRYTIS', m['TARGET_FIT']['ISSUE_ID'])

    def test_U16_primary_match_so_com_regra_defensavel(self):
        for b in _recs('OPPORTUNITY-BRIEFINGS.json'):
            regra, pm = b['PRIMARY_MATCH_RULE'], b['PRIMARY_MATCH']
            if regra == 'PM_SINGLE_EXTERNALLY_NAMEABLE':
                self.assertIsNotNone(pm, b['ID'])
                fortes = [m for m in b['PORTFOLIO_MATCHES']
                          if m['VALIDATION_STATE'] == 'READY_TO_NAME_EXTERNALLY']
                self.assertEqual(1, len(fortes), b['ID'])
                self.assertEqual(fortes[0]['PRODUCT_ID'], pm, b['ID'])
            else:
                self.assertIsNone(pm, '%s escolheu principal sem regra' % b['ID'])

    def test_U17_nenhum_produto_promovido_para_encher_tela(self):
        """Todo match nomeado tem par de rótulo declarado pela fonte."""
        pares = {r['ID'] for r in _recs('PRODUCT-RELATIONSHIPS.json')}
        for b in _recs('OPPORTUNITY-BRIEFINGS.json'):
            for m in b['PORTFOLIO_MATCHES']:
                self.assertTrue(m['EVIDENCE_IDS'],
                                '%s · %s sem evidencia' % (b['ID'], m['PRODUCT_NAME']))
                for e in m['EVIDENCE_IDS']:
                    self.assertIn(e, pares, '%s · %s' % (b['ID'], e))

    def _botrite(self):
        b = [x for x in _recs('OPPORTUNITY-BRIEFINGS.json')
             if x['WHAT_IS_HAPPENING']['ISSUE_ID'] == 'ISSUE_BOTRYTIS'
             and x['WHAT_IS_HAPPENING']['REGION_ID'] == 'REGION_EMILIA_ROMAGNA']
        self.assertEqual(1, len(b), 'a testemunha botrite sumiu do pacote')
        return b[0]


# ═══════════════════════════════════════════════════════════════════════════
# U18–U20 · A EVIDÊNCIA NEGATIVA
# ═══════════════════════════════════════════════════════════════════════════
class EvidenciaNegativa(unittest.TestCase):

    def test_U18_papeis_negativos_existem_no_pacote(self):
        d = _pacote('OPPORTUNITY-BRIEFINGS.json')
        por_papel = d['BY_EVIDENCE_ROLE']
        self.assertGreater(por_papel.get(BR.R_CLOSES, 0), 0,
                           'nenhuma evidencia FECHA caso nenhum')
        self.assertGreater(por_papel.get(BR.R_WEAKENS, 0), 0,
                           'nenhuma evidencia ENFRAQUECE caso nenhum')

    def test_U19_evidencia_que_fecha_esfria_a_implicacao(self):
        for b in _recs('OPPORTUNITY-BRIEFINGS.json'):
            for e in b['EVIDENCES']:
                if e['EVIDENCE_ROLE'] in (BR.R_CLOSES, BR.R_CONTRADICTS,
                                          BR.R_WEAKENS):
                    self.assertEqual('CI_COOLS_OPPORTUNITY',
                                     e['COMMERCIAL_IMPLICATION_CODE'], b['ID'])

    def test_U20_presenca_nao_vira_implicacao_comercial(self):
        """A fonte que só prova presença não sustenta conclusão comercial.

            NÃO RESUMIR «COMERCIALMENTE» O QUE A FONTE NÃO PERMITE CONCLUIR.
        """
        self.assertEqual('UNKNOWN', BR.IMPLICACAO_DO_PAPEL[BR.R_SIGNAL])
        for b in _recs('OPPORTUNITY-BRIEFINGS.json'):
            for e in b['EVIDENCES']:
                if e['EVIDENCE_ROLE'] == BR.R_SIGNAL:
                    self.assertEqual('UNKNOWN', e['COMMERCIAL_IMPLICATION_CODE'])


# ═══════════════════════════════════════════════════════════════════════════
# U21–U23 · A CAMADA NOVA NÃO CRIOU NADA
# ═══════════════════════════════════════════════════════════════════════════
class NadaNasceuDaCamadaNova(unittest.TestCase):

    def test_U21_uma_ficha_por_oportunidade_e_nenhuma_a_mais(self):
        opp = {o['ID'] for o in _recs('OPPORTUNITIES.json')}
        brf = [b['OPPORTUNITY_ID'] for b in _recs('OPPORTUNITY-BRIEFINGS.json')]
        self.assertEqual(sorted(opp), sorted(brf),
                         'o briefing criou ou perdeu oportunidade')

    def test_U22_a_razao_comercial_so_e_PROVEN_com_a_cadeia_inteira(self):
        for b in _recs('OPPORTUNITY-BRIEFINGS.json'):
            w = b['WHY_THIS_IS_A_COMMERCIAL_OPPORTUNITY']
            if w['COMMERCIAL_REASON_STATE'] == BR.REASON_PROVEN:
                self.assertEqual([], w['MISSING_LINKS'], b['ID'])
                for elo in BR.ELOS:
                    self.assertNotEqual('UNKNOWN', w['CHAIN'][elo]['STATE'],
                                        '%s · %s' % (b['ID'], elo))
            else:
                self.assertEqual('UNKNOWN', w['COMMERCIAL_REASON_STATE'], b['ID'])
                self.assertTrue(w['MISSING_LINKS'], b['ID'])

    def test_U23_nenhum_registro_do_briefing_carrega_prosa_nova(self):
        """Frase com variável dentro nunca fica traduzida — então não há frase.

        Os campos de lei são texto FIXO e declarado; o resto é código, ID ou
        número. `SOURCE_EXCERPT` é a palavra da fonte, que já viaja assim em
        `NEED_EXCERPT` e não se traduz.
        """
        d = _pacote('OPPORTUNITY-BRIEFINGS.json')
        self.assertEqual([], d['LOCALIZED_FIELDS'])
        fixos = {'WHY_NOW_LAW', 'PRIMARY_MATCH_LAW', 'ACTION_MAP_LAW',
                 'EVIDENCE_ROLE_LAW', 'BRIEFING_DOES_NOT_PROVE',
                 'WHY_NOT_CLIENT_SAFE', 'CROP_LEVEL_ONLY_LAW'}
        primeiro = d['RECORDS'][0]
        for b in d['RECORDS']:
            for k in fixos:
                self.assertEqual(primeiro.get(k), b.get(k),
                                 '%s: %s nao e frase fixa' % (b['ID'], k))


# ═══════════════════════════════════════════════════════════════════════════
# U24–U25 · O PORTÃO E A TESTEMUNHA
# ═══════════════════════════════════════════════════════════════════════════
class PortaoETestemunha(unittest.TestCase):

    def test_U24_a_aceitacao_e_portao(self):
        """Ela media violação e devolvia 0 sempre. Etapa que não reprova não é etapa."""
        fonte = open(os.path.join(ROOT, 'scripts', 'v21_aceitacao.py'),
                     encoding='utf-8').read()
        self.assertIn('PARADO NA ACEITACAO', fonte)
        self.assertIn('quebrou = [(k, v) for k, v in reprova if v]', fonte)
        rel = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                           'ACCEPTANCE-REPORT.json')
        if not os.path.exists(rel):
            raise unittest.SkipTest('rode scripts/v21_cadeia.sh')
        r = json.load(open(rel, encoding='utf-8'))
        self.assertEqual(0, r['QA_GATE']['VIOLACOES'])
        self.assertEqual(0, r['QA_GATE']['SEM_QA_STATUS'])

    def test_U25_a_testemunha_universal_atravessou(self):
        p = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                         'TRILHA-UNIVERSAL-TESTEMUNHA.json')
        if not os.path.exists(p):
            raise unittest.SkipTest('rode scripts/v21_testemunha_universal.py')
        d = json.load(open(p, encoding='utf-8'))
        self.assertEqual([], d['FALHAS'])
        self.assertEqual('YES', d['AUTOMATIC_NEW_INGEST'])
        self.assertEqual('YES', d['UNIVERSAL_GATE'])
        self.assertEqual('YES', d['BACKFILL'])
        self.assertEqual(d['BASELINE_BUILD_ID'], d['BUILD_ID_RESTAURADO'],
                         'a travessia deixou residuo')
        self.assertNotEqual(d['BASELINE_BUILD_ID'], d['BUILD_ID_COM_FIXTURES'],
                            'a porta nao esta sendo lida')
        # As fixtures que ENTRARAM mudaram oportunidade de fato — e por origens
        # diferentes, não só pela do boletim.
        self.assertGreaterEqual(len(d['OPORTUNIDADES_QUE_MUDARAM']), 2)

    def test_U26_o_ci_nao_commita_por_cima_de_inteligencia_falhada(self):
        """`classificar || true` + `medir || true` + commit era o padrão proibido."""
        wf = open(os.path.join(ROOT, '.github', 'workflows',
                               'comunicacao-publica.yml'), encoding='utf-8').read()
        self.assertNotIn('comunicacao_classificar.py || true', wf)
        self.assertNotIn('comunicacao_medir.py || true', wf)
        self.assertIn('INTELIGENCIA_FALHOU', wf)
        self.assertIn('VALIDATION_REQUIRED', wf)


if __name__ == '__main__':
    unittest.main(verbosity=2)
