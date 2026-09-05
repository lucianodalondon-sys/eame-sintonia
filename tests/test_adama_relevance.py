#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A LEI DE RELEVANCIA ADAMA, medida contra os 43 e contra sondas.

    python3 -m unittest tests.test_adama_relevance -v

Um teste que so confirma a populacao de hoje prova que a lei concorda consigo
propria. Por isso metade destes testes sao CONTROLOS NEGATIVOS: constroem o
caso que NAO deve subir e exigem que a lei o recuse.

    UMA LEI QUE NUNCA RECUSOU NAO E UMA LEI: E UMA ETIQUETA.
"""
import io
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
from adama_relevance import (classificar, contar, produto_que_prova,   # noqa: E402
                             problema_evidenciado, restricoes_separadas,
                             SUPERFICIE, CONTRATO)

SNAP = json.load(io.open(os.path.join(
    RAIZ, 'italia-portale', 'client', 'meeting-intelligence-snapshot.json'), encoding='utf-8'))
CASOS = SNAP['CASES']


def caso(**kw):
    """Um caso minimo que PASSA, para depois se lhe partir um elo de cada vez."""
    base = {
        'ID': 'SONDA', 'CROP': 'CROP_GRAPEVINE', 'TARGET': 'ISSUE_BOTRYTIS',
        'MATCHED_COMMERCIAL_PRODUCT_IDS': ['CATPRD_X'],
        'PORTFOLIO_MATCHES': [{
            'PRODUCT_ID': 'CATPRD_X', 'PRODUCT_NAME': 'X', 'REGISTRATION_NUMBER': '000001',
            'ACTIVE_INGREDIENTS': ['AI1'], 'CROP_FIT': 'DECLARED_ON_CATALOG_PAGE',
            'TARGET_FIT': 'ON_MINISTERIAL_LABEL', 'REGULATORY_FIT': 'AUTHORIZATION_LIVE'}],
        'EVIDENCE_ROLES': [{'ROLE': 'SUPPORTS_SIGNAL', 'ENTITY_TYPE': 'FIELD_SIGNAL'}],
    }
    base.update(kw)
    return base



class LeiDeRelevanciaADAMA(unittest.TestCase):
    # ── A POPULACAO MEDIDA ──────────────────────────────────────────────────────

    def test_a_populacao_e_43_e_nada_desaparece(self):
        c = contar(CASOS)
        self.assertTrue(sum(c.values()) == 43 == len(CASOS), c)
        self.assertTrue(c == {'A': 13, 'B': 21, 'C': 8, 'D': 1, 'E': 0}, c)


    def test_so_A_publica_como_oportunidade(self):
        for x in CASOS:
            k, _ = classificar(x)
            self.assertTrue(SUPERFICIE[k] == ('OPPORTUNITA' if k == 'A' else SUPERFICIE[k]))
            if SUPERFICIE[k] == 'OPPORTUNITA':
                self.assertTrue(k == 'A', (x['ID'], k))


    def test_o_caso_D_e_o_medido(self):
        d = [x['ID'] for x in CASOS if classificar(x)[0] == 'D']
        self.assertTrue(d == ['OPP_4C39CCC05EEB'], d)


    def test_todo_A_nomeia_o_produto_que_o_prova(self):
        for x in CASOS:
            if classificar(x)[0] != 'A':
                continue
            m = produto_que_prova(x)
            self.assertTrue(m and m['PRODUCT_NAME'] and m['REGISTRATION_NUMBER'], x['ID'])


    # ── CONTROLOS NEGATIVOS · a lei tem de RECUSAR ──────────────────────────────

    def test_sem_alvo_nao_sobe(self):
        self.assertTrue(classificar(caso(TARGET=None))[0] == 'B')


    def test_cultura_nao_declarada_no_catalogo_e_erro_nao_oportunidade(self):
        c = caso()
        c['PORTFOLIO_MATCHES'][0]['CROP_FIT'] = 'UNKNOWN'
        self.assertTrue(classificar(c)[0] == 'D')


    def test_alvo_fora_do_rotulo_ministerial_nao_sobe(self):
        c = caso()
        c['PORTFOLIO_MATCHES'][0]['TARGET_FIT'] = 'RELATED'
        self.assertTrue(classificar(c)[0] == 'D')


    def test_autorizacao_nao_viva_nao_sobe(self):
        c = caso()
        c['PORTFOLIO_MATCHES'][0]['REGULATORY_FIT'] = 'EXPIRED'
        self.assertTrue(classificar(c)[0] == 'D')


    def test_sem_numero_de_registo_nao_sobe(self):
        c = caso()
        c['PORTFOLIO_MATCHES'][0]['REGISTRATION_NUMBER'] = None
        self.assertTrue(classificar(c)[0] == 'D')


    def test_produto_fora_do_catalogo_comercial_nao_sobe(self):
        c = caso(MATCHED_COMMERCIAL_PRODUCT_IDS=[])
        self.assertTrue(classificar(c)[0] == 'C')


    def test_mesmo_ingrediente_nao_basta(self):
        """Dois produtos com o mesmo activo, nenhum com a cultura declarada."""
        c = caso()
        c['PORTFOLIO_MATCHES'] = [dict(c['PORTFOLIO_MATCHES'][0], CROP_FIT='UNKNOWN'),
                                  dict(c['PORTFOLIO_MATCHES'][0], PRODUCT_ID='CATPRD_Y',
                                       CROP_FIT='UNKNOWN')]
        c['MATCHED_COMMERCIAL_PRODUCT_IDS'] = ['CATPRD_X', 'CATPRD_Y']
        self.assertTrue(classificar(c)[0] == 'D')


    def test_basta_UM_produto_a_fechar_a_cadeia(self):
        """OPP_75C37DED9160 tem Lamdex (fecha) e MAVRIK (nao). Continua A."""
        c = caso()
        c['PORTFOLIO_MATCHES'] = [dict(c['PORTFOLIO_MATCHES'][0], PRODUCT_ID='CATPRD_Y',
                                       CROP_FIT='UNKNOWN'),
                                  c['PORTFOLIO_MATCHES'][0]]
        c['MATCHED_COMMERCIAL_PRODUCT_IDS'] = ['CATPRD_X', 'CATPRD_Y']
        self.assertTrue(classificar(c)[0] == 'A')
        real = [x for x in CASOS if x['ID'] == 'OPP_75C37DED9160'][0]
        self.assertTrue(classificar(real)[0] == 'A')


    def test_expiracao_europeia_nao_gera_oportunidade(self):
        """APPROVAL_EXPIRY != RISCO_DE_NAO_RENOVACAO.

        Um caso que so tem facto regulatorio — sem cultura, sem alvo, sem produto
        a catalogo — nunca e oportunidade, por mais proxima que seja a data.
        """
        c = {'ID': 'SONDA_REG', 'CROP': 'CROP_BARLEY', 'TARGET': None,
             'MATCHED_COMMERCIAL_PRODUCT_IDS': [], 'PORTFOLIO_MATCHES': [],
             'EVIDENCE_ROLES': [{'ENTITY_TYPE': 'REGULATORY_PRODUCT'},
                                {'ENTITY_TYPE': 'REGULATORY_FUTURE_FACT'}]}
        k, porque = classificar(c)
        self.assertTrue(k == 'B' and porque == 'RELEVANCE_B_NAMED_ASSET_NO_RISK')
        # e nos 43: nenhum caso com facto regulatorio subiu a A por causa dele
        for x in CASOS:
            tipos = {e.get('ENTITY_TYPE') for e in (x.get('EVIDENCE_ROLES') or [])}
            if 'REGULATORY_FUTURE_FACT' in tipos and classificar(x)[0] == 'A':
                self.assertTrue(produto_que_prova(x) is not None, x['ID'])


    def test_preencher_um_campo_nao_promove_21_para_A(self):
        """A promessa que a missao pediu: nao transformar 13 em 30 por campo cheio.

        Dar alvo a um caso B sem tocar em CROP_FIT/TARGET_FIT nao o faz subir a A —
        faz-lhe cair a ligacao, que e a resposta honesta.
        """
        b = [x for x in CASOS if classificar(x)[0] == 'B' and x.get('MATCHED_COMMERCIAL_PRODUCT_IDS')]
        self.assertTrue(b, 'nao ha B com produto para sondar')
        subiram = [x['ID'] for x in b if classificar(dict(x, TARGET='ISSUE_BOTRYTIS'))[0] == 'A']
        # Sem a exigencia de problema OBSERVADO subiam 10. Com ela sobe UM — e
        # esse traz 4 sinais de campo e 4 evidencias de sinal: subiria por ter
        # facto, nao por ter campo cheio. E a proxima missao que o julga.
        self.assertEqual(subiram, ['OPP_00C5B6E15185'], subiram)
        alvo = [x for x in CASOS if x['ID'] == 'OPP_00C5B6E15185'][0]
        self.assertTrue(problema_evidenciado(alvo))
        self.assertTrue(alvo['COMMERCIAL_MAGNITUDE_DIMENSIONS']['SINAIS_DE_CAMPO'] >= 4)

    def test_alvo_escrito_sem_fonte_que_o_observou_nao_sobe(self):
        """O CONTROLO que impede a promocao por preenchimento."""
        c = caso(EVIDENCE_ROLES=[])
        self.assertEqual(classificar(c)[0], 'D')
        c2 = caso(EVIDENCE_ROLES=[{'ROLE': 'SUPPORTS_PRODUCT_MATCH'}])
        self.assertEqual(classificar(c2)[0], 'D')
        c3 = caso(EVIDENCE_ROLES=[{'ROLE': 'SUPPORTS_SIGNAL'}])
        self.assertEqual(classificar(c3)[0], 'A')

    def test_target_fit_e_constante_e_por_isso_nao_e_prova(self):
        fits = {m['TARGET_FIT'] for x in CASOS for m in (x.get('PORTFOLIO_MATCHES') or [])}
        self.assertEqual(fits, {'ON_MINISTERIAL_LABEL'}, fits)


    # ── AS RESTRICOES, SEPARADAS NA ORIGEM ──────────────────────────────────────

    def test_restricoes_separadas_somam_as_do_motor(self):
        tot = nossas = outras = 0
        for x in CASOS:
            a, b = restricoes_separadas(x)
            nossas += len(a)
            outras += len(b)
            tot += len(x.get('PRODUCT_RESTRICTIONS') or [])
        self.assertTrue(nossas + outras == tot == 114, (nossas, outras, tot))
        self.assertTrue((nossas, outras) == (74, 40), (nossas, outras))


    def test_nenhuma_restricao_de_outro_activo_entra_na_lista_do_produto(self):
        for x in CASOS:
            nossos = {a for m in (x.get('PORTFOLIO_MATCHES') or [])
                      for a in (m.get('ACTIVE_INGREDIENTS') or [])}
            minhas, _ = restricoes_separadas(x)
            for r in minhas:
                self.assertTrue(r['ACTIVE_INGREDIENT'] in nossos, (x['ID'], r))


    def test_o_contrato_diz_o_que_nao_aceita(self):
        self.assertTrue(CONTRATO['SO_A_PUBLICA'] is True)
        for proibido in ('correspondencia lexical', 'mesmo ingrediente activo',
                         'template', 'proximidade de data de expiracao europeia'):
            self.assertTrue(proibido in CONTRATO['NAO_ACEITE'], proibido)


if __name__ == '__main__':
    unittest.main(verbosity=2)
