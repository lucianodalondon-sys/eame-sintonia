#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DA CATRACA UNIVERSAL — depois da reconciliação de linhagem.

⚠️ ESTE ARQUIVO PERDEU METADE DO QUE TINHA, E ISSO FOI UM CONSERTO.

A missão da trilha universal partiu de `0ddf52d`. Enquanto ela rodava, a mesma
branch avançou quatro commits (`caa6937` → `e7c154c`) e construiu, DENTRO do
motor, o contrato do cartão: `STATUS` com cadeia de quatro elos, `WINDOW_TYPE` /
`WINDOW_DEFINED` / `WINDOW_OPEN_NOW`, `PORTFOLIO_MATCHES`, `PRIMARY_MATCH`,
`ACTION_BY_DEPARTMENT`, `EVIDENCE_ROLES`, `INTELLIGENCE_BRIEF`,
`WHAT_IS_MISSING`.

A camada `v21_briefing.py` desta missão calculava as MESMAS coisas por fora — e
calculava PIOR: sem conhecer a janela agronômica, devolvia `VALIDATE_NOW` onde o
motor, com os quatro elos fechados, devolve `ACT_NOW`. Foi apagada na
reconciliação, e com ela os testes que a provavam.

    DUAS RESPOSTAS PARA A MESMA PERGUNTA NÃO SÃO REDUNDÂNCIA:
    SÃO UM BUG ESPERANDO A HORA DE APARECER NA TELA.

O que sobrevive aqui é o que NÃO tem dono na outra linha: a catraca, o censo da
porta, a aceitação que reprova, o fim do bypass no CI e a testemunha universal.

    U1–U4   a catraca SÓ SEGURA: nunca promove.
    U5–U7   material incompleto fica visível; falha não sustenta publicável.
    U8–U9   censo da porta: buraco declarado é declarado, buraco novo para.
    U10     a catraca NÃO é dona de nenhum campo do cartão.
    U11–U14 o que a linhagem nova trouxe não pode regredir.
    U15–U17 aceitação, ordem da cadeia e CI.
    U18     a testemunha universal atravessou.

    UM TESTE QUE NÃO NASCEU DE UM ERRO MEDIDO É UM TESTE QUE PASSA POR SORTE.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_catraca as CAT      # noqa: E402

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
        """A propriedade que faz desta camada uma catraca, e não um motor."""
        for o in _recs('OPPORTUNITIES.json'):
            de_fora = CAT.DE_EXTERNO.get(o.get('EXTERNAL_MATERIAL_READY'),
                                         CAT.GATE_UNKNOWN)
            self.assertGreaterEqual(
                CAT.PERMISSIVIDADE[o['PUBLICATION_STATE']],
                CAT.PERMISSIVIDADE[de_fora],
                '%s: a catraca PROMOVEU (de %s para %s)'
                % (o['ID'], de_fora, o['PUBLICATION_STATE']))

    def test_U2_publicavel_exige_external_yes(self):
        for o in _recs('OPPORTUNITIES.json'):
            if o['PUBLICATION_STATE'] == CAT.PUBLISHABLE:
                self.assertEqual('YES', o['EXTERNAL_MATERIAL_READY'], o['ID'])

    def test_U3_o_gate_declara_os_quatro_estados(self):
        d = _pacote('PUBLICATION-GATE.json')
        self.assertEqual(['PUBLISHABLE', 'VALIDATION_REQUIRED', 'UNKNOWN',
                          'QUARANTINED'], d['PUBLICATION_STATES'])

    def test_U4_evidencia_quarentenada_rebaixa(self):
        """Prova pela função: hoje não há material em quarentena no pacote."""
        censo = {'EV_OK': {'MATERIAL_STATE': CAT.MATERIAL_PASSED},
                 'EV_RUIM': {'MATERIAL_STATE': CAT.MATERIAL_QUARANTINED}}
        o = {'EXTERNAL_MATERIAL_READY': 'YES', 'EVIDENCE_IDS': ['EV_OK']}
        self.assertEqual((CAT.PUBLISHABLE, 'COMPLETE'),
                         CAT.estado_de_publicacao(o, censo)[:2])
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
             'REGION_IDS': [], 'GEOGRAPHIC_SCOPE': 'NACIONAL', 'WHAT_IT_IS': 'x'})
        self.assertEqual(CAT.FAILED, et['CLASSIFICATION'])
        self.assertIn('NO_QA_STATUS', mot)
        self.assertEqual(CAT.MATERIAL_QUARANTINED, CAT.estado_do_material(et))

    def test_U6_os_quatro_boletins_mudos_ganharam_texto(self):
        """⚠️ ESTE TESTE FOI INVERTIDO PELA RECONCILIAÇÃO, E ISSO É UMA VITÓRIA.

        Na linha de `0ddf52d`, `IT-CAN-71D68FCB7D`, `IT-CAN-6EFC8DC91A`,
        `IT-CAN-EB63AEC4AA` e `IT-CAN-49BA29FF51` chegavam ao motor SEM texto —
        `promover_research` era tudo-ou-nada — e o teste original pinava esse
        silêncio para que ninguém o mudasse sem medir.

        A linhagem `e7c154c` consertou: `v21_ingest_b.py` passou a promover a
        prosa desses registros. O teste não some — ele muda de lado, e agora
        impede a REGRESSÃO.

            UM TESTE QUE PINA UM DEFEITO VIRA UM TESTE QUE PINA O CONSERTO.
            O QUE NÃO PODE É SUMIR NA HORA EM QUE O DEFEITO SUMIU.
        """
        gate = _pacote('PUBLICATION-GATE.json')
        mudos = {r['RECORD_ID'] for r in gate['RECORDS']
                 if 'NO_TEXT_FOR_PAIR_EXTRACTION' in r['REASON_CODES']}
        for rid in ('IT-CAN-71D68FCB7D', 'IT-CAN-6EFC8DC91A',
                    'IT-CAN-EB63AEC4AA', 'IT-CAN-49BA29FF51'):
            self.assertNotIn(rid, mudos,
                             '%s voltou a chegar MUDO ao motor: a promocao de '
                             'RESEARCH regrediu' % rid)

    def test_U7_localizacao_e_UNKNOWN_nao_falha(self):
        """Lacuna de tradução não é falha de inteligência."""
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
        d = _pacote('PUBLICATION-GATE.json')
        censo = d['DOOR_CENSUS']
        for fam in ('COMMERCIAL_CATALOG', 'HERBICIDE_CURRENT_CONTEXT'):
            self.assertIn(fam, censo)
            self.assertEqual(0, censo[fam]['NO_PACOTE'], fam)
            self.assertTrue(censo[fam]['DECLARADA_COMO_NAO_INGERIDA'], fam)
            self.assertTrue(censo[fam]['WHY'], fam)
        for fam, v in censo.items():
            if fam in CAT.FAMILIA_NAO_INGERIDA:
                continue
            self.assertEqual(0, v['SUMIRAM'],
                             '%s passou a perder registro na porta' % fam)

    def test_U9_buraco_novo_para_a_cadeia(self):
        d = _pacote('PUBLICATION-GATE.json')
        self.assertEqual(
            [], d['VIOLATIONS']['V5_FAMILIA_SUMIU_NA_PORTA_SEM_DECLARACAO'])
        self.assertEqual(0, d['VIOLATION_COUNT'])


# ═══════════════════════════════════════════════════════════════════════════
# U10 · A CATRACA NÃO É DONA DE NENHUM CAMPO DO CARTÃO
# ═══════════════════════════════════════════════════════════════════════════
class SemSegundoDono(unittest.TestCase):

    # Os campos do contrato do cartão, todos de `v21_oportunidades.py`.
    DO_MOTOR = ('STATUS', 'ACTION_CHAIN_LINKS', 'WHY_NOW_CHAIN', 'WHY_NOW_CODES',
                'WINDOW_TYPE', 'WINDOW_DEFINED', 'WINDOW_OPEN_NOW',
                'PEST_STAGE_STATE', 'ACTION_RECOMMENDATION_STATE',
                'THRESHOLD_STATE', 'WINDOW_RULE_STATE',
                'PORTFOLIO_MATCHES', 'PRIMARY_MATCH', 'ACTION_BY_DEPARTMENT',
                'EVIDENCE_ROLES', 'INTELLIGENCE_BRIEF', 'WHAT_IS_MISSING',
                'COMMERCIAL_MAGNITUDE', 'SIGNAL_CURRENCY')

    def test_U10_a_catraca_nao_escreve_campo_do_cartao(self):
        """A regra que a reconciliação de linhagem custou para aprender."""
        fonte = open(os.path.join(ROOT, 'scripts', 'v21_catraca.py'),
                     encoding='utf-8').read()
        for campo in self.DO_MOTOR:
            self.assertNotIn("['%s'] =" % campo, fonte,
                             'a catraca voltou a escrever %s — isso e do motor'
                             % campo)
        # E os únicos campos que ela escreve no cartão são os dela.
        escritos = {'PUBLICATION_STATE', 'TRAIL_STATE',
                    'TRAIL_QUARANTINED_EVIDENCE_IDS',
                    'TRAIL_INCOMPLETE_EVIDENCE_IDS',
                    'TRAIL_MISSING_EVIDENCE_IDS', 'PUBLICATION_STATE_FROM',
                    'PUBLICATION_GATE_LAW'}
        import re
        achados = set(re.findall(r"o\['([A-Z_]+)'\] =", fonte))
        self.assertEqual(escritos, achados,
                         'a catraca mudou o conjunto de campos que escreve')

    def test_U10b_o_briefing_paralelo_nao_voltou(self):
        """`v21_briefing.py` foi apagado por ser segundo dono. Não pode voltar."""
        for nome in ('v21_briefing.py', 'v21_ler_briefing.py'):
            self.assertFalse(
                os.path.exists(os.path.join(ROOT, 'scripts', nome)),
                '%s voltou: ele recalcula o contrato do cartao por fora do motor'
                % nome)
        cad = open(os.path.join(ROOT, 'scripts', 'v21_cadeia.sh'),
                   encoding='utf-8').read()
        self.assertNotIn('v21_briefing', cad)


# ═══════════════════════════════════════════════════════════════════════════
# U11–U14 · O QUE A LINHAGEM NOVA TROUXE NÃO PODE REGREDIR
# ═══════════════════════════════════════════════════════════════════════════
class InteligenciaNovaPreservada(unittest.TestCase):
    """Estes testes não são meus por invenção: são a fronteira da reconciliação.

    Eles existem para que a catraca — que entrou por cima — não possa ter
    apagado nada da linhagem `e7c154c` sem ninguém ver.
    """

    def test_U11_a_janela_agronomica_existe_e_decide(self):
        import v21_janelas as JAN
        self.assertIn(JAN.PREHARVEST_WINDOW, JAN.TIPOS)
        recs = _recs('OPPORTUNITIES.json')
        com_janela = [o for o in recs if o.get('WINDOW_DEFINED') == 'YES']
        self.assertTrue(com_janela, 'nenhuma janela agronomica sobreviveu')
        for o in com_janela:
            self.assertIn(o.get('WINDOW_TYPE'), JAN.TIPOS, o['ID'])
            self.assertTrue(o.get('WINDOW_EVIDENCE_ID'), o['ID'])

    def test_U12_act_now_exige_a_cadeia_de_quatro_elos(self):
        for o in _recs('OPPORTUNITIES.json'):
            if o.get('STATUS') != 'ACT_NOW':
                continue
            elos = o.get('ACTION_CHAIN_LINKS') or {}
            self.assertTrue(elos.get('JANELA_DEFINIDA'), o['ID'])
            self.assertTrue(elos.get('JANELA_ABERTA_AGORA'), o['ID'])
            self.assertTrue(elos.get('SINAL_ATUAL'), o['ID'])
            self.assertTrue(elos.get('VINCULO_COM_PORTFOLIO'), o['ID'])

    def test_U13_regra_delegada_ao_pomar_nao_abre_janela(self):
        for o in _recs('OPPORTUNITIES.json'):
            if o.get('WINDOW_RULE_STATE') == 'RULE_DELEGATED_TO_FARM':
                self.assertNotEqual('ACT_NOW', o.get('STATUS'), o['ID'])

    def test_U14_os_papeis_negativos_da_evidencia_continuam(self):
        papeis = {e['ROLE'] for o in _recs('OPPORTUNITIES.json')
                  for e in (o.get('EVIDENCE_ROLES') or [])}
        self.assertTrue(papeis, 'EVIDENCE_ROLES sumiu do cartao')
        negativos = papeis & {'WEAKENS', 'CONTRADICTS', 'CLOSES',
                              'BACKGROUND_ONLY'}
        self.assertTrue(negativos,
                        'nenhuma evidencia negativa sobreviveu: %s' % sorted(papeis))


# ═══════════════════════════════════════════════════════════════════════════
# U15–U17 · ACEITAÇÃO, ORDEM E CI
# ═══════════════════════════════════════════════════════════════════════════
class PortaoOrdemECI(unittest.TestCase):

    def test_U15_a_aceitacao_e_portao(self):
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

    def test_U16_a_catraca_roda_depois_da_traducao(self):
        """A etapa LOCALIZATION só é mensurável depois de a tradução entrar."""
        cad = open(os.path.join(ROOT, 'scripts', 'v21_cadeia.sh'),
                   encoding='utf-8').read()
        i_motor = cad.index('scripts/v21_oportunidades.py')
        i_trad = cad.index('v21_traducao_trava.py --aplicar')
        i_cat = cad.index('scripts/v21_catraca.py')
        i_fim = cad.index('scripts/v21_fechar.py')
        self.assertLess(i_motor, i_trad)
        self.assertLess(i_trad, i_cat, 'a catraca voltou para antes da traducao')
        self.assertLess(i_cat, i_fim, 'o fechamento roda antes da catraca')
        self.assertEqual(1, cad.count('scripts/v21_catraca.py'))

    def test_U17_a_lacuna_de_traducao_nao_e_o_estado_normal(self):
        d = _pacote('PUBLICATION-GATE.json')
        n = d['BY_REASON_CODE'].get('READING_ONLY_IN_PORTUGUESE', 0)
        self.assertLess(n, 100,
                        'READING_ONLY_IN_PORTUGUESE=%d — a catraca esta medindo '
                        'a traducao antes de ela entrar' % n)

    def test_U17b_o_ci_nao_commita_por_cima_de_inteligencia_falhada(self):
        wf = open(os.path.join(ROOT, '.github', 'workflows',
                               'comunicacao-publica.yml'), encoding='utf-8').read()
        self.assertNotIn('comunicacao_classificar.py || true', wf)
        self.assertNotIn('comunicacao_medir.py || true', wf)
        self.assertIn('INTELIGENCIA_FALHOU', wf)
        self.assertIn('VALIDATION_REQUIRED', wf)


# ═══════════════════════════════════════════════════════════════════════════
# U18 · A TESTEMUNHA UNIVERSAL
# ═══════════════════════════════════════════════════════════════════════════
class TestemunhaUniversal(unittest.TestCase):

    def test_U18_a_testemunha_universal_atravessou(self):
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
        self.assertGreaterEqual(len(d['OPORTUNIDADES_QUE_MUDARAM']), 2)


# ── U19 a U21 · A FRONTEIRA DA SEGUNDA RECONCILIAÇÃO ───────────────────────
#
# A primeira reconciliação juntou a catraca com a inteligência até `e7c154c`.
# Esta juntou o que veio depois — `85df96f`, o fechamento das regras de janela.
# Estes três provam que a junção não custou nada a nenhum dos dois lados.
#
#     UMA CAMADA POR CIMA QUE MUDA UM NÚMERO DE BAIXO NÃO É CAMADA: É DONO.
class TestReconciliacaoUniversal(unittest.TestCase):

    def _witness(self):
        p = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                         'V117-RECONCILIACAO-UNIVERSAL.json')
        if not os.path.exists(p):
            raise unittest.SkipTest(
                'rode scripts/v21_reconciliacao_universal.py')
        with open(p, encoding='utf-8') as f:
            return json.load(f)

    def test_U19_a_reconciliacao_nao_mexeu_em_campo_nenhum_do_cartao(self):
        d = self._witness()
        self.assertEqual([], d['FALHAS'])
        self.assertEqual('PASS', d['UNIVERSAL_INTELLIGENCE_RECONCILIATION'])
        bf = d['BACKFILL']
        self.assertEqual(bf['CASOS_ANTES'], bf['CASOS_DEPOIS'])
        self.assertEqual({}, bf['CAMPOS_QUE_MUDARAM'],
                         'a catraca mexeu num campo que tem outro dono')
        # e o que ela ACRESCENTOU existe: antes nenhum cartao tinha estado
        self.assertEqual({'None': bf['CASOS_ANTES']},
                         bf['PUBLICATION_STATE_ANTES'])
        self.assertNotIn('None', bf['PUBLICATION_STATE_DEPOIS'])

    def test_U20_publicavel_nunca_contradiz_o_cartao(self):
        """A catraca pode REBAIXAR. Ela nunca pode promover contra o motor.

        Se um cartão diz que o material não sai da ADAMA e a catraca o declara
        publicável, são dois donos discordando sobre a mesma pergunta — e é o
        cartão que responde por ela.
        """
        for r in _recs('OPPORTUNITIES.json'):
            if r.get('PUBLICATION_STATE') == 'PUBLISHABLE':
                self.assertEqual('YES', r.get('EXTERNAL_MATERIAL_READY'),
                                 r['ID'])
            self.assertIn(r.get('PUBLICATION_STATE'),
                          ('PUBLISHABLE', 'VALIDATION_REQUIRED', 'BLOCKED'),
                          r['ID'])

    def test_U21_a_area_oficial_escolhe_por_criterio_e_nao_por_ordem(self):
        """`area[0]` era a ordem do arquivo, que não é critério nenhum.

        Hoje não dispara — nenhuma linha ISTAT é client-safe. O dia em que o
        carimbo entrar, 2024 e 2025 ficam elegíveis juntos, e um número que muda
        de significado pela ordem do JSON é um número sem dono.
        """
        fonte = open(os.path.join(ROOT, 'scripts', 'v21_oportunidades.py'),
                     encoding='utf-8').read()
        self.assertIn('area.sort(', fonte, 'a area voltou a sair por ordem')
        for r in _recs('OPPORTUNITIES.json'):
            dim = r.get('COMMERCIAL_MAGNITUDE_DIMENSIONS') or {}
            self.assertIn('AREA_OFICIAL_ANO', dim, r['ID'])
            self.assertIn('AREA_SELECTION_RULE', dim, r['ID'])
            if dim.get('AREA_OFICIAL_HA') is not None:
                self.assertIsNotNone(dim.get('AREA_OFICIAL_ANO'), r['ID'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
