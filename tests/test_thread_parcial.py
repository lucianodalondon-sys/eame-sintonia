#!/usr/bin/env python3
"""
THREAD PARCIAL NAO PODE SER OK.

O caso que abre esta suite nao e inventado: e o video `ezRyN8vLVvc` do canal
`@viticolturariccardocastaldi`, medido na corrida 34258433872. As fixtures em
`tests/fixtures/YT-RUN-34258433872/` sao os BYTES REAIS que a API devolveu.

O YouTube declarou `totalReplyCount = 1`, entregou zero respostas no envelope,
e quando `comments.list` foi chamado para completar a thread ele respondeu
HTTP 200 com `items: []`. Faltou uma resposta, e o relatorio disse `STATE = OK`.

    ALGUM CONTEUDO RECUPERADO NAO SIGNIFICA CONVERSA COMPLETA.
    THREAD_COMPLETE NAO E THREAD_PARTIAL.
"""
import json
import os
import sys
import tempfile
import unittest
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401

import falhas                     # noqa: E402
import youtube_oficial as yt      # noqa: E402

import social_envelope as env      # noqa: E402

FIXTURES = os.path.join(HERE, 'fixtures', 'YT-RUN-34258433872')

# ── ESTA SUITE NAO ESCREVE NO ACERVO ──────────────────────────────────────
# `comentarios()` grava o RAW de cada resposta, e sem isto ele cairia dentro de
# `data/samples/SOCIAL-IT/raw-free/` — no repositorio. Rodar os testes passaria
# a versionar bruto de fixture, que e precisamente o defeito que esta missao
# fechou do outro lado: CHECKOUT NAO E COLETA. Um teste que suja o acervo cria o
# proximo falso positivo sozinho.
env.RAW_DIR = os.path.join(tempfile.gettempdir(), 'sintonia-raw-thread-parcial')


def corpo(nome):
    with open(os.path.join(FIXTURES, nome), encoding='utf-8') as f:
        return json.load(f)


def erro_http(code, reason):
    corpo_erro = json.dumps({'error': {'code': code, 'errors': [{'reason': reason}]}})

    class _Falso(urllib.error.HTTPError):
        def __init__(self):
            super().__init__('http://x', code, reason, {}, None)
            self._corpo = corpo_erro.encode()

        def read(self):
            return self._corpo
    return _Falso()


def transporte(*respostas):
    """Devolve as respostas em ordem; levanta as que forem excecao."""
    fila = list(respostas)

    def _t(url):
        r = fila.pop(0) if fila else {'items': []}
        if isinstance(r, Exception):
            raise r
        return r
    return _t


# Curta de PROPOSITO: `guarda/social_guarda.py` acusa
# `api_key = "<8+ caracteres>"` como chave literal, e esta acusacao esta certa —
# ela nao tem como saber que a nossa e de mentira. Encurtar o valor de teste
# custa nada; por na lista de excecoes do guarda custaria a proxima chave de
# verdade que alguem escrevesse num teste.
#
#     CONSERTAR O ARQUIVO, NUNCA AFROUXAR O GUARDA.
CHAVE_FALSA = 'TESTE'


def sessao(*respostas):
    return yt.Sessao(api_key=CHAVE_FALSA, transporte=transporte(*respostas))


class ReproduzirOCasoReal(unittest.TestCase):
    """FASE 1 — reproduzir antes de corrigir, com os bytes da corrida real."""

    def test_a_fixture_e_mesmo_o_caso_declarado(self):
        """Se a fixture nao tiver o defeito, o resto desta suite nao prova nada."""
        d = corpo('commentThreads-ezRyN8vLVvc.json')
        threads = d['items']
        self.assertEqual(len(threads), 2)
        sn = threads[1]['snippet']
        self.assertEqual(int(sn['totalReplyCount']), 1)
        self.assertEqual(len((threads[1].get('replies') or {}).get('comments') or []), 0)
        # E `comments.list` respondeu 200 com lista vazia — nao recusou.
        self.assertEqual(corpo('comments-UgxoP_4_qUyfVrsKV6V4AaABAg.json')['items'], [])

    def test_o_video_real_produz_falta_de_uma_resposta(self):
        _obj, _s, rel = yt.comentarios(
            video_id='ezRyN8vLVvc', run_id='REPRO',
            sessao=sessao(corpo('commentThreads-ezRyN8vLVvc.json'),
                          corpo('comments-UgxoP_4_qUyfVrsKV6V4AaABAg.json')))
        self.assertEqual(rel['THREADS'], 2)
        self.assertEqual(rel['COMMENTS'], 2)
        self.assertEqual(rel['REPLIES'], 0)
        self.assertEqual(rel['REPLIES_MISSING'], 1)

    def test_thread_parcial_nao_pode_terminar_OK(self):
        """O DEFEITO. Contra o codigo de hoje este teste FALHA — e deve falhar."""
        _obj, _s, rel = yt.comentarios(
            video_id='ezRyN8vLVvc', run_id='REPRO',
            sessao=sessao(corpo('commentThreads-ezRyN8vLVvc.json'),
                          corpo('comments-UgxoP_4_qUyfVrsKV6V4AaABAg.json')))
        self.assertGreater(rel['REPLIES_MISSING'], 0, 'a fixture perdeu o defeito')
        self.assertNotEqual(
            rel['STATE'], 'OK',
            'faltou 1 resposta declarada pela API e o estado ficou OK: '
            'ALGUM CONTEUDO RECUPERADO NAO SIGNIFICA CONVERSA COMPLETA')

    def test_tentativa_nao_pode_se_chamar_completada(self):
        """`REPLIES_COMPLETED` sobe mesmo quando a thread continuou incompleta."""
        _obj, _s, rel = yt.comentarios(
            video_id='ezRyN8vLVvc', run_id='REPRO',
            sessao=sessao(corpo('commentThreads-ezRyN8vLVvc.json'),
                          corpo('comments-UgxoP_4_qUyfVrsKV6V4AaABAg.json')))
        completas = rel.get('THREADS_COMPLETED', rel.get('REPLIES_COMPLETED'))
        self.assertEqual(
            completas, 0,
            'uma TENTATIVA que nao completou nada foi contada como COMPLETED')



def thread(cid, texto, respostas=0, trazidas=0):
    """Uma thread como `commentThreads.list` a devolve: declarada e entregue."""
    return {'snippet': {
        'channelId': 'UCcanal', 'totalReplyCount': respostas,
        'topLevelComment': {'id': cid, 'snippet': {
            'textOriginal': texto, 'publishedAt': '2026-01-01T00:00:00Z',
            'authorChannelId': {'value': 'UCautor'}}}},
        'replies': {'comments': [
            {'id': '%s.r%d' % (cid, i), 'snippet': {
                'textOriginal': 'resposta %d' % i,
                'publishedAt': '2026-01-01T00:00:00Z',
                'authorChannelId': {'value': 'UCoutro'}}}
            for i in range(trazidas)]} if trazidas else {}}


class OsOitoCasosDaCompletude(unittest.TestCase):
    """T1..T8 — a completude tem de sobreviver a cada um deles."""

    # ── T1 ────────────────────────────────────────────────────────────────
    def test_T1_duas_threads_sem_falta_e_completo(self):
        _o, _s, rel = yt.comentarios(
            video_id='v', run_id='T1',
            sessao=sessao({'items': [thread('c1', 'a'), thread('c2', 'b')]}))
        self.assertEqual(rel['STATE'], 'OK')
        self.assertEqual(rel['THREADS_TOTAL'], 2)
        self.assertEqual(rel['THREADS_COMPLETE'], 2)
        self.assertEqual(rel['THREADS_PARTIAL'], 0)
        self.assertEqual(rel['REPLIES_MISSING'], 0)

    # ── T2 ────────────────────────────────────────────────────────────────
    def test_T2_declarou_uma_entregou_zero_e_PARCIAL_nao_OK(self):
        _o, _s, rel = yt.comentarios(
            video_id='v', run_id='T2',
            sessao=sessao({'items': [thread('c1', 'a', respostas=1)]},
                          {'items': []}))
        self.assertEqual(rel['STATE'], 'PARTIAL_RESULTS')
        self.assertEqual(rel['REPLIES_DECLARED'], 1)
        self.assertEqual(rel['REPLIES_OBSERVED'], 0)
        self.assertEqual(rel['REPLIES_MISSING'], 1)
        self.assertEqual(rel['THREADS_PARTIAL'], 1)
        # 200 com menos do que declarou e DISCREPANCIA OBSERVADA, nao causa.
        self.assertEqual(rel['PARTIAL_CAUSE'],
                         ['API_RETURNED_FEWER_REPLIES_THAN_DECLARED'])
        self.assertTrue(rel['PARTIAL_CAUSE_IS_OBSERVED_DISCREPANCY'])
        self.assertEqual(rel['COMPLETION_ERRORS'], [],
                         'a API respondeu 200 — nao houve erro operacional')

    def test_T2b_nao_se_infere_causa_que_ninguem_observou(self):
        _o, _s, rel = yt.comentarios(
            video_id='v', run_id='T2b',
            sessao=sessao({'items': [thread('c1', 'a', respostas=1)]},
                          {'items': []}))
        texto = json.dumps(rel, ensure_ascii=False).lower()
        for palpite in ('deleted', 'moderated', 'hidden', 'removed', 'spam'):
            self.assertNotIn(palpite, texto,
                             'inferiu «%s» sem ter observado nada disso' % palpite)

    # ── T3 ────────────────────────────────────────────────────────────────
    def test_T3_403_no_complemento_preserva_razao_nativa(self):
        _o, _s, rel = yt.comentarios(
            video_id='v', run_id='T3',
            sessao=sessao({'items': [thread('c1', 'a', respostas=2)]},
                          erro_http(403, 'forbidden')))
        self.assertEqual(rel['STATE'], 'PARTIAL_RESULTS')
        self.assertEqual(len(rel['COMPLETION_ERRORS']), 1)
        e = rel['COMPLETION_ERRORS'][0]
        self.assertEqual(e['NATIVE_REASON'], 'forbidden')
        self.assertEqual(e['API_METHOD'], 'comments.list')
        self.assertEqual(e['PARENT_ID'], 'c1')
        self.assertIn(e['CANONICAL_STATE'], falhas.NOMES)
        self.assertNotEqual(e['CANONICAL_STATE'], 'OK')

    # ── T4 ────────────────────────────────────────────────────────────────
    def test_T4_quota_durante_o_complemento_e_PARCIAL_com_causa(self):
        _o, _s, rel = yt.comentarios(
            video_id='v', run_id='T4',
            sessao=sessao({'items': [thread('c1', 'a', respostas=2)]},
                          erro_http(403, 'quotaExceeded')))
        self.assertEqual(rel['STATE'], 'PARTIAL_RESULTS')
        e = rel['COMPLETION_ERRORS'][0]
        self.assertEqual(e['CANONICAL_STATE'], 'QUOTA_EXHAUSTED')
        self.assertEqual(e['NATIVE_REASON'], 'quotaExceeded')
        # Quota NUNCA pode ter virado "faltou resposta sem motivo".
        self.assertEqual(rel['PARTIAL_CAUSE'], ['QUOTA_EXHAUSTED'])
        self.assertFalse(rel['PARTIAL_CAUSE_IS_OBSERVED_DISCREPANCY'])

    def test_T4b_teto_da_casa_nao_e_quota_da_plataforma(self):
        s = yt.Sessao(api_key=CHAVE_FALSA, teto_geral=1,
                      transporte=transporte({'items': [thread('c1', 'a', respostas=2)]},
                                            {'items': []}))
        _o, _s, rel = yt.comentarios(video_id='v', run_id='T4b', sessao=s)
        self.assertEqual(rel['STATE'], 'PARTIAL_RESULTS')
        e = rel['COMPLETION_ERRORS'][0]
        self.assertEqual(e['CANONICAL_STATE'], 'BUDGET_EXHAUSTED',
                         'teto da CASA virou quota da PLATAFORMA')

    # ── T5 ────────────────────────────────────────────────────────────────
    def test_T5_erro_de_backend_no_complemento_e_PARCIAL_com_causa(self):
        _o, _s, rel = yt.comentarios(
            video_id='v', run_id='T5',
            sessao=sessao({'items': [thread('c1', 'a', respostas=2)]},
                          erro_http(500, 'backendError')))
        self.assertEqual(rel['STATE'], 'PARTIAL_RESULTS')
        e = rel['COMPLETION_ERRORS'][0]
        self.assertEqual(e['NATIVE_REASON'], 'backendError')
        self.assertTrue(falhas.e_falha(e['CANONICAL_STATE']))
        self.assertIsNotNone(e['RECOVERY_ACTION'])

    # ── T6 ────────────────────────────────────────────────────────────────
    def test_T6_feature_disabled_continua_separado(self):
        _o, _s, rel = yt.comentarios(
            video_id='v', run_id='T6',
            sessao=sessao(erro_http(403, 'commentsDisabled')))
        self.assertEqual(rel['STATE'], 'FEATURE_DISABLED')
        self.assertTrue(rel.get('COMMENTS_DISABLED'))
        self.assertNotEqual(rel['STATE'], 'PARTIAL_RESULTS')
        self.assertNotEqual(rel['STATE'], 'ZERO_RESULTS')

    # ── T7 ────────────────────────────────────────────────────────────────
    def test_T7_zero_results_continua_separado(self):
        _o, _s, rel = yt.comentarios(
            video_id='v', run_id='T7', sessao=sessao({'items': []}))
        self.assertEqual(rel['STATE'], 'ZERO_RESULTS')
        self.assertTrue(rel.get('ZERO_LEGITIMATE'))
        self.assertNotEqual(rel['STATE'], 'PARTIAL_RESULTS')

    # ── T8 ────────────────────────────────────────────────────────────────
    def test_T8_attempt_nao_vira_completed(self):
        """Uma tentativa que nao fechou a thread nao pode contar como fechada."""
        _o, _s, rel = yt.comentarios(
            video_id='v', run_id='T8',
            sessao=sessao({'items': [thread('c1', 'a', respostas=3)]},
                          {'items': []}))
        self.assertEqual(rel['COMPLETION_ATTEMPTS'], 1)
        self.assertEqual(rel['THREADS_COMPLETED'], 0)
        self.assertNotIn('REPLIES_COMPLETED', rel,
                         'o contador que chamava ATTEMPT de COMPLETED voltou')

    def test_T8b_o_caso_feliz_conta_nos_dois(self):
        """A separacao nao pode ter matado o caminho legitimo."""
        _o, _s, rel = yt.comentarios(
            video_id='v', run_id='T8b',
            sessao=sessao({'items': [thread('c1', 'a', respostas=2)]},
                          {'items': [{'id': 'c1.x%d' % i, 'snippet': {
                              'textOriginal': 'r%d' % i,
                              'publishedAt': '2026-01-01T00:00:00Z',
                              'authorChannelId': {'value': 'UCa'}}} for i in range(2)]}))
        self.assertEqual(rel['COMPLETION_ATTEMPTS'], 1)
        self.assertEqual(rel['THREADS_COMPLETED'], 1)
        self.assertEqual(rel['REPLIES_MISSING'], 0)
        self.assertEqual(rel['STATE'], 'OK')


if __name__ == '__main__':
    unittest.main(verbosity=2)
