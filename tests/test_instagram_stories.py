#!/usr/bin/env python3
"""STORY — a classe, e as duas portas que sobreviveram à troca de rota.

A Apify saiu de Stories em 2026-09-09. O que ficou deste trabalho é o que nunca
foi da Apify: a porta de TIPO e a porta do ZERO. Elas valem para qualquer rota —
foi um ator PAGO que serviu Reel chamando de Story, e nada impede que uma rota
gratuita erre igual.

    ENUM EXISTE != CAPACIDADE FUNCIONA.
    ZERO LINHA DE ROTA QUE FALHOU NÃO É «NÃO POSTOU».
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
sys.path.insert(0, os.path.join(RAIZ, 'leis'))
import _gavetas  # noqa: E402,F401
import instagram_stories as ist   # noqa: E402
import social_envelope as env     # noqa: E402

AGORA = 1789000000
DEPOIS = AGORA + 86400

# A FORMA REAL, medida em 2026-09-09. A fixture inventada da R2 não tinha
# `product_type` nem `caption_is_edited`, e por isso a porta passava nos testes
# enquanto teria recusado 100% dos Stories verdadeiros.
#
#     UMA TRAVA CALIBRADA EM CIMA DE FIXTURE INVENTADA MEDE A FIXTURE.
STORY_IMAGEM = {
    'pk': '3210000000000000001', 'id': '3210000000000000001_999',
    'media_type': 1, 'taken_at': AGORA, 'expiring_at': DEPOIS,
    'product_type': 'story', 'is_reel_media': True,
    'caption_is_edited': False, 'code': 'CxYzStory', 'caption': None,
    'like_and_view_counts_disabled': True, 'has_liked': False,
    'user': {'username': 'conta_publica_exemplo', 'id': '999'},
    'image_versions2': {'candidates': [{'url': 'https://cdn.example/i.jpg?sig=abc'}]},
    'original_width': 1080, 'original_height': 1920,
}
STORY_VIDEO = dict(STORY_IMAGEM, pk='3210000000000000002', media_type=2,
                   video_versions=[{'url': 'https://cdn.example/v.mp4?sig=abc'}])
REEL_DISFARCADO = dict(STORY_IMAGEM, pk='3210000000000000009',
                       product_type='clips', play_count=12345, shortcode='CxYzAbC')


def _norm(item, u='conta_publica_exemplo'):
    return ist.normalizar(item, username=u, run_id='TEST-STORY',
                          country_scope='IT', route='local:cdp')


class APortaDeTipo(unittest.TestCase):
    """§132 — Reel continua sendo recusado, venha de onde vier."""

    def test_o_story_real_passa(self):
        self.assertEqual(_norm(STORY_IMAGEM)['CONTENT_TYPE'], 'STORY')

    def test_reel_disfarcado_e_recusado(self):
        with self.assertRaises(ist.NaoEStory):
            _norm(REEL_DISFARCADO)

    def test_is_reel_media_TRUE_nao_e_prova_de_reel(self):
        """Armadilha de nome: no vocabulário do Instagram, «reel media» é a
        BANDEJA DE STORIES. Um Story tem is_reel_media=true. Ler esse campo como
        prova de Reel inverteria a porta e recusaria tudo o que é certo."""
        self.assertTrue(STORY_IMAGEM['is_reel_media'])
        self.assertEqual(_norm(STORY_IMAGEM)['CONTENT_TYPE'], 'STORY')

    def test_highlight_nao_e_story(self):
        """§232 — sem backfill. Highlight é permanente; Story expira."""
        with self.assertRaises(ist.NaoEStory):
            _norm(dict(STORY_IMAGEM, is_highlight=True, highlight_id='h1'))

    def test_classe_desconhecida_nao_entra_por_omissao(self):
        with self.assertRaises(ist.NaoEStory):
            _norm(dict(STORY_IMAGEM, product_type='coisa_nova'))

    def test_sem_prazo_de_expiracao_nao_prova_ser_efemero(self):
        item = {k: v for k, v in STORY_IMAGEM.items() if k != 'expiring_at'}
        with self.assertRaises(ist.NaoEStory):
            _norm(item)


class APortaDoZero(unittest.TestCase):
    """§133, §172-§175 — falha de rota nunca vira «a conta não postou»."""

    def test_zero_para_todos_e_unknown(self):
        e = ist.classificar({'STATUS': 'SUCCESS'}, [], ['a', 'b'])
        self.assertEqual({v['ESTADO'] for v in e.values()}, {'UNKNOWN_ERROR'})

    def test_zero_para_um_quando_outro_respondeu_e_no_active_stories(self):
        e = ist.classificar({'STATUS': 'SUCCESS'}, [STORY_IMAGEM],
                            ['conta_publica_exemplo', 'sem_story'])
        self.assertEqual(e['sem_story']['ESTADO'], 'NO_ACTIVE_STORIES')

    def test_privado_e_bloqueio_e_nao_vazio(self):
        e = ist.classificar({'STATUS': 'SUCCESS'}, [dict(STORY_IMAGEM, is_private=True)],
                            ['conta_publica_exemplo'])
        self.assertEqual(e['conta_publica_exemplo']['ESTADO'], 'PRIVATE_PROFILE')

    def test_os_quatro_estados_continuam_distinguiveis(self):
        import falhas
        canon = {n: falhas.traduzir(n) for n in
                 ('NO_ACTIVE_STORIES', 'PRIVATE_PROFILE', 'LOGIN_REQUIRED', 'ACTOR_FAILED')}
        self.assertEqual(len(set(canon.values())), 4, canon)


class OQueOScrapNaoPreenche(unittest.TestCase):

    def test_publicacao_nao_vira_fato(self):
        o = _norm(STORY_IMAGEM)
        self.assertEqual(o['FACT_TIME'], 'UNKNOWN')
        self.assertNotEqual(o['PUBLISHED_AT'], o['FACT_TIME'])

    def test_conta_nao_vira_lugar_do_fato(self):
        o = _norm(STORY_IMAGEM)
        self.assertEqual(o['FACT_LOCATION'], 'UNKNOWN')
        self.assertEqual(o['ACCOUNT_LOCATION'], 'UNKNOWN')

    def test_expiracao_vem_da_plataforma(self):
        self.assertEqual(_norm(STORY_IMAGEM)['EXPIRES_AT_SOURCE'], 'PLATFORM')


class UmStoryVistoTresVezesEUmStory(unittest.TestCase):

    def test_a_mesma_story_em_duas_varreduras_funde(self):
        objs, rel = env.dedupe([_norm(STORY_IMAGEM), _norm(STORY_VIDEO)] * 2)
        self.assertEqual(len(objs), 2)
        self.assertEqual(rel['FUNDIDOS'], 2)

    def test_a_identidade_e_o_id_e_nao_a_imagem(self):
        gemea = dict(STORY_IMAGEM, pk='3210000000000000004')
        objs, _r = env.dedupe([_norm(STORY_IMAGEM), _norm(gemea)])
        self.assertEqual(len(objs), 2)


if __name__ == '__main__':
    unittest.main()
