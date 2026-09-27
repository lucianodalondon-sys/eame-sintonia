#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COMENTARIOS-V1 (D106 + D107) — o comentário nasce PUBLIC_ASSERTION, com o pai nomeado, a
elegibilidade do pai decide-se no pedido, a amostra marca sem apagar, o LinkedIn tem a rota
gratuita candidata, o Instagram fecha pelo GASTO e não pelo jurídico, e o workflow apelida T5/T7.

    py -m unittest tests.test_comentarios_v1

Sem rede, sem banco. Os textos marcados SINTETICO foram escritos aqui para isolar uma lei.
"""
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import social_envelope as env  # noqa: E402
import youtube_oficial as yt  # noqa: E402
import elegibilidade_comentario as el  # noqa: E402
import social_matriz as mz  # noqa: E402
import adaptador_linkedin as al  # noqa: E402
import instagram_pessoal as ip  # noqa: E402
import pedido as pd  # noqa: E402

POST = ('https://it.linkedin.com/posts/horta-s-r-l-_peronospora-vite-vendemmia-'
        'activity-7114944753380507649-EPmo')


def comentario_yt(texto='SINTETICO: la peronospora sulla vite quest anno e terribile', likes=3,
                  data='2026-09-20T10:00:00Z', cid='Ug-SINT-1'):
    c = {'id': cid, 'snippet': {'textOriginal': texto, 'textDisplay': texto, 'publishedAt': data,
                                'likeCount': likes, 'authorDisplayName': 'x',
                                'authorChannelId': {'value': 'UC-SINT'}}}
    return yt._comentario(c, video_id='vid00000001', parent_id=None, run_id='SINT', country_scope='IT',
                          raw_ref=None, canal='UC-CANAL')


class EnvelopeDoComentario(unittest.TestCase):

    def test_comentario_nasce_assercao_publica_nunca_facto(self):
        o = comentario_yt()
        self.assertEqual(o['CLAIM_KIND'], 'PUBLIC_ASSERTION')
        self.assertEqual(o['EVIDENCE_CLASS'], 'FIELD_VOICE_OBSERVED')
        self.assertEqual((o['ORIGIN_STATUS'], o['AUTHOR_ROLE']), ('UNVERIFIED', 'UNKNOWN'))
        self.assertIn('Voz não é incidência', o['NAO_E'])

    def test_o_pai_e_nomeado_e_o_lugar_nao_se_inventa(self):
        o = comentario_yt()
        self.assertEqual(o['PARENT_CONTENT_ID'], 'YOUTUBE:vid00000001')
        self.assertEqual(o['FACT_LOCATION'], 'UNKNOWN')
        self.assertTrue(o['FACT_LOCATION_BASIS'].startswith('O_PAI_NAO_TRAZ_LUGAR'))
        self.assertEqual(o['COMMENT_AUTHOR_LOCATION'], 'NAO_SE_COLETA')

    def test_d107_nasce_nao_avaliado_e_sem_regiao_de_quem_fala(self):
        o = comentario_yt()
        self.assertEqual((o['AGRONOMIC_SIGNAL'], o['LINGUISTIC_SIGNAL']), ('NAO_AVALIADO', 'NAO_AVALIADO'))
        self.assertEqual((o['REGIONAL_LANGUAGE_EVIDENCE'], o['SPEAKER_LANGUAGE_LOCATION']), ('UNKNOWN', 'UNKNOWN'))

    def test_comentario_sem_pai_nao_se_monta(self):
        with self.assertRaises(ValueError):
            env.envelope(platform='YOUTUBE', native_id='x', url='u', content_type='COMMENT', route='r',
                         executor='e', run_id='SINT', country_scope='IT', text='t')

    def test_lugar_herdado_so_quando_o_pai_o_prova(self):
        a = env.assercao_do_comentario(parent_content_id='YOUTUBE:v', parent_fact_location='Ravenna',
                                       parent_fact_location_basis='leis/fato_local ancora riscontrati')
        self.assertEqual(a['FACT_LOCATION'], 'Ravenna')
        self.assertTrue(a['FACT_LOCATION_BASIS'].startswith('HERDADO_DO_PAI YOUTUBE:v'))
        self.assertEqual(a['SPEAKER_LANGUAGE_LOCATION'], 'UNKNOWN')      # IAB §5: o lugar do post nao e da fala

    def test_objetos_que_nao_sao_comentario_nao_ganham_assercao(self):
        o = env.envelope(platform='YOUTUBE', native_id='v', url='u', content_type='VIDEO', route='r',
                         executor='e', run_id='SINT', country_scope='IT')
        self.assertNotIn('CLAIM_KIND', o)


class AmostraESinais(unittest.TestCase):
    """SINTETICO: 12 comentários para ver os baldes, o controlo e os sinais."""

    def setUp(self):
        textos = ['la peronospora sulla vite e arrivata presto quest anno davvero',
                  'bello', 'qui in Puglia la mosca delle olive ha fatto danni enormi quest anno',
                  'non sono d\'accordo, il rame non funziona piu come prima nei nostri campi',
                  'grazie mille per il video molto utile e chiaro davvero complimenti']
        self.objs = [comentario_yt(texto=textos[i % len(textos)], likes=i, cid='Ug-SINT-%02d' % i,
                                   data='2026-09-%02dT10:00:00Z' % (i + 1)) for i in range(12)]
        self.pai = {'TITLE': 'Difesa della vite dalla peronospora', 'FACT_LOCATION': 'Veneto'}
        self.rel = el.marcar(self.objs, pai=self.pai)

    def test_nada_e_apagado(self):
        self.assertEqual(len(self.objs), 12)
        self.assertEqual(self.rel['APAGADOS'], 0)
        for o in self.objs:
            self.assertIsInstance(o['SAMPLE_BUCKETS'], list)

    def test_ha_controlo_cru_escolhido_sem_olhar_o_texto(self):
        ctrl = [o for o in self.objs if 'CONTROLE' in o['SAMPLE_BUCKETS']]
        self.assertTrue(ctrl)
        self.assertEqual(ctrl, [o for o in self.objs if el._estavel(o['NATIVE_ID']) % el.FRACAO_CONTROLE == 0])

    def test_os_cinco_baldes_existem(self):
        self.assertEqual(set(self.rel['POR_BALDE']), set(el.BALDES))
        self.assertTrue(self.rel['POR_BALDE']['DISCORDANTE'] >= 1)

    def test_sinais_d107(self):
        por_texto = {o['TEXT']: o for o in self.objs}
        self.assertEqual(por_texto['bello']['LINGUISTIC_SIGNAL'], 'NO')
        agrad = por_texto['grazie mille per il video molto utile e chiaro davvero complimenti']
        self.assertEqual((agrad['AGRONOMIC_SIGNAL'], agrad['LINGUISTIC_SIGNAL']), ('NO', 'YES'))  # sem facto, com lingua
        pero = por_texto['la peronospora sulla vite e arrivata presto quest anno davvero']
        self.assertEqual(pero['AGRONOMIC_SIGNAL'], 'YES')
        self.assertIn('VINE', pero['CANONICAL_ENTITIES'])

    def test_regiao_so_quando_a_fala_a_diz(self):
        por_texto = {o['TEXT']: o for o in self.objs}
        pug = por_texto['qui in Puglia la mosca delle olive ha fatto danni enormi quest anno']
        self.assertEqual((pug['REGIONAL_LANGUAGE_EVIDENCE'], pug['REGION_IF_PROVEN']), ('EXPLICIT', 'Puglia'))
        self.assertEqual(pug['SPEAKER_LANGUAGE_LOCATION'], 'Puglia')
        for o in self.objs:
            self.assertNotEqual(o['SPEAKER_LANGUAGE_LOCATION'], 'Veneto')   # o lugar do PAI nunca vira o de quem fala


class Elegibilidade(unittest.TestCase):

    def test_high_com_fonte_registada_tema_e_entidade(self):
        # o pai REAL do acervo (SENSOR-PILOT, IT-T8-006 · w87w51fSWAw), com a descricao que a fonte publicou
        pai = el._pais_do_acervo()['w87w51fSWAw']
        e = el.elegibilidade(pai, 'T8', fonte_registada=True, comentarios_declarados=1)
        self.assertEqual(e['COMMENT_COLLECTION_ELIGIBILITY'], 'HIGH', e)
        self.assertTrue(e['VAI_COLHER'])

    def test_candidata_nao_passa_de_medium(self):
        pai = {'TITLE': 'Le strategie di diserbo a Mais Domani',
               'DESCRIPTION': 'SINTETICO: infestanti del mais, diserbo in pre e post emergenza, resistenza delle malerbe'}
        e = el.elegibilidade(pai, 'T8', fonte_registada=False, comentarios_declarados=4)
        self.assertEqual(e['COMMENT_COLLECTION_ELIGIBILITY'], 'MEDIUM')

    def test_lacuna_de_vocabulario_e_nao_sei_e_nao_no(self):
        pai = {'TITLE': "L'innovazione nella difesa dalla maculatura bruna"}
        e = el.elegibilidade(pai, 'T8', fonte_registada=True, comentarios_declarados=3)
        self.assertEqual(e['COMMENT_COLLECTION_ELIGIBILITY'], 'NAO_SEI')
        self.assertIn('LACUNA_DE_VOCABULARIO', e['PORQUE'])
        self.assertFalse(e['VAI_COLHER'])

    def test_zero_declarado_nao_colhe_e_diz_porque(self):
        pai = {'TITLE': 'Difesa del frumento da fusarium e septoria'}
        e = el.elegibilidade(pai, 'T9', fonte_registada=True, comentarios_declarados=0)
        self.assertFalse(e['VAI_COLHER'])
        self.assertIn('ZERO_DECLARADO', e['SE_NAO_COLHE'] or '')

    def test_comentarios_desligados_e_no(self):
        pai = {'TITLE': 'Difesa del frumento da fusarium e septoria'}
        e = el.elegibilidade(pai, 'T9', fonte_registada=True, comentarios_desligados=True)
        self.assertEqual(e['COMMENT_COLLECTION_ELIGIBILITY'], 'NO')

    def test_o_piloto_da_fase1_so_colhe_o_elegivel(self):
        linhas = el.piloto()
        self.assertEqual(len(linhas), 12)
        for l in linhas:
            if 'COMANDO' in l:
                self.assertTrue(l['VAI_COLHER'])
                self.assertIn(l['COMMENT_COLLECTION_ELIGIBILITY'], ('HIGH', 'MEDIUM'))
                self.assertIn('fase=comentarios-youtube', l['COMANDO'])
        self.assertTrue(any('COMANDO' in l for l in linhas))


class MatrizELinkedin(unittest.TestCase):

    def test_linkedin_tem_rota_gratuita_candidata_nao_provada(self):
        d = mz.decisao('LINKEDIN', 'FETCH_COMMENTS')
        self.assertEqual((d['DECISAO'], d['ROTA'], d['ESTADO']),
                         ('ALLOWED', 'linkedin:post-publico:jsonld-comment', 'POSSIBLE_NOT_PROVED'))
        rota = mz.MATRIZ['LINKEDIN']['FETCH_COMMENTS'][0]
        self.assertEqual((rota['OWNER_AUTHORIZED'], rota['PLATFORM_POLICY_STATUS'], rota['LIMITE']),
                         ('SIM', 'DISALLOWED', 'PUBLIC_POST_COMMENTS_MINIMIZED'))
        self.assertEqual(rota['CUSTO'], 'zero')
        self.assertIn('PUBLIC_POST_COMMENTS_MINIMIZED', mz.LIMITES)

    def test_instagram_continua_condicional_e_diz_a_d106(self):
        rota = mz.MATRIZ['INSTAGRAM']['FETCH_COMMENTS'][0]
        self.assertEqual((rota['CLASSE'], rota['PERMITIDA']), ('APIFY', 'CONDICIONAL'))
        self.assertIn('D106', rota['NOTA'])

    def test_leitor_do_jsonld_minimiza_e_nomeia_o_pai(self):
        html = ('<script type="application/ld+json">{"@type":"SocialMediaPosting","comment":['
                '{"@type":"Comment","text":"SINTETICO: da noi in Veneto la peronospora e ovunque",'
                '"datePublished":"2026-09-20","author":{"@type":"Person","name":"Mario Rossi",'
                '"url":"https://www.linkedin.com/in/mario-rossi"}},'
                '{"@type":"Comment","text":"SINTETICO: da noi in Veneto la peronospora e ovunque",'
                '"datePublished":"2026-09-20","author":{"@type":"Person","name":"Mario Rossi"}}]}</script>')
        objs = al.comentarios_do_jsonld(html, post_url=POST, run_id='SINT', pseudonimo=lambda k: 'LIP-teste')
        self.assertEqual(len(objs), 1)                                   # o repetido funde
        o = objs[0]
        self.assertEqual(o['PARENT_CONTENT_ID'], 'LINKEDIN:7114944753380507649')
        self.assertEqual(o['CLAIM_KIND'], 'PUBLIC_ASSERTION')
        self.assertEqual(o['SOURCE_ACCOUNT'], 'LIP-teste')
        despejo = json.dumps(o, ensure_ascii=False)
        self.assertNotIn('Mario Rossi', despejo)
        self.assertNotIn('linkedin.com/in/', despejo)
        self.assertEqual(o['RAW']['AUTHOR_AVATAR_URL'], 'REDACTED_BY_POLICY')

    def test_pagina_sem_jsonld_devolve_vazio(self):
        self.assertEqual(al.comentarios_do_jsonld('<html></html>', post_url=POST, run_id='SINT',
                                                  pseudonimo=lambda k: 'x'), [])

    def test_leitor_so_aceita_post_publico(self):
        with self.assertRaises(Exception):
            al.comentarios_do_jsonld('<html></html>', post_url='https://www.linkedin.com/in/pessoa/',
                                     run_id='SINT', pseudonimo=lambda k: 'x')

    def test_listagem_de_comentarios_e_porta_trocada(self):
        with self.assertRaises(ValueError) as c:
            al._alvo_e_post_publico('https://www.linkedin.com/feed/update/urn:li:activity:1234567890123456/comments/')
        self.assertIn('ALVO_TROCADO_DE_PORTA', str(c.exception))


class InstagramEWorkflow(unittest.TestCase):

    def test_portao_do_instagram_fecha_pelo_gasto_e_nao_pelo_juridico(self):
        pode, motivo = ip.pode_coletar(env={})
        self.assertFalse(pode)
        self.assertIn('GASTO', motivo)
        self.assertIn('D106', motivo)
        pode, motivo = ip.pode_coletar(env={ip.AUTORIZADO: '1'})
        self.assertTrue(pode)
        self.assertIn('GASTO', motivo)

    def test_workflow_apelida_t5_e_t7_com_os_apelidos_do_dono(self):
        with open(os.path.join(RAIZ, '.github', 'workflows', 'sintonia-scrap.yml'), encoding='utf-8') as fh:
            y = fh.read()
        bloco = y[y.index('assunto_do_alvo_da_fonte() {'):]
        bloco = bloco[:bloco.index('esac')]
        casos = dict(re.findall(r"(IT-T\d+)-\*\) echo '([^']+)'", bloco))
        self.assertEqual(casos, {'IT-T5': 'colete ciencia', 'IT-T7': 'colete agronomos',
                                 'IT-T8': 'colete agricultores', 'IT-T9': 'colete concorrentes'})
        for prefixo, frase in casos.items():
            self.assertEqual(pd.alvo_de(frase), prefixo.split('-')[1])


if __name__ == '__main__':
    unittest.main()
