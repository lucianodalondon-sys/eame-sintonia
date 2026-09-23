#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A PORTA GROSSA DO AUDIO PUBLICO — os treze portoes e os oito ataques.

A rota `yt-dlp:public_audio` e a primeira desta matriz que declara os TRES eixos
separados, porque e a primeira onde eles divergem: o dono autorizou por escrito
e a plataforma continua a proibir.

Este ficheiro existe para que essa separacao nao se desfaça por conveniencia —
nem por uma migracao futura que "simplifique" os tres campos num so.

Nenhuma prova aqui precisa de rede.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import scrap_capacidades as cap    # noqa: E402
import social_matriz as mz         # noqa: E402

FINAS = 'youtube.public_audio'
GROSSA = 'FETCH_AUDIO_BYTES'
ROTA = 'yt-dlp:public_audio'
MEDIA = 'youtube.media'
CAPTION = 'youtube.native_caption'

#: As 32 decisoes que ja existiam ANTES desta rota, com o que cada uma
#: respondia. E a ancora do ataque H: mexer na rota nova nao pode mexer em
#: nenhuma destas. Ancorar num facto envelhece com o facto — e por isso esta
#: lista so muda quando alguem muda a politica, de proposito e com prova.
DECISOES_ANTIGAS = {
    'BLUESKY/DISCOVER_ACCOUNT': ('ALLOWED', 'bsky:app.bsky.actor.searchActors', 'SIM', 'PROVED'),
    'BLUESKY/FETCH_PROFILE': ('ALLOWED', 'bsky:app.bsky.actor.getProfile', 'SIM', 'POSSIBLE_NOT_PROVED'),
    'BLUESKY/INCREMENTAL': ('ALLOWED', 'bsky:app.bsky.feed.getAuthorFeed', 'SIM', 'POSSIBLE_NOT_PROVED'),
    'BLUESKY/SEARCH_KEYWORD': ('ALLOWED', 'bsky:app.bsky.feed.searchPosts', 'SIM', 'BLOCKED'),
    'FACEBOOK/DISCOVER_ACCOUNT': ('ALLOWED', 'graph:/pages/search', 'CONDICIONAL', 'CREDENTIAL_MISSING'),
    'FACEBOOK/FETCH_POST': ('ALLOWED', 'graph:/{page-id}/posts', 'CONDICIONAL', 'CREDENTIAL_MISSING'),
    'FACEBOOK/FETCH_PROFILE': ('ALLOWED', 'graph:/{page-id}?fields=...', 'CONDICIONAL', 'CREDENTIAL_MISSING'),
    'FACEBOOK/FETCH_VIDEO_METADATA': ('ALLOWED', 'graph:/{page-id}/videos', 'CONDICIONAL', 'CREDENTIAL_MISSING'),
    'INSTAGRAM/FETCH_COMMENTS': ('ALLOWED', 'apify:comments', 'CONDICIONAL', 'PROVED'),
    'INSTAGRAM/FETCH_POST': ('ALLOWED', 'instagram_janela.py:embed', 'CONDICIONAL', 'PROVED'),
    'INSTAGRAM/FETCH_PROFILE': ('ALLOWED', 'graph:business_discovery', 'CONDICIONAL', 'CREDENTIAL_MISSING'),
    # ── MUDOU EM 2026-09-23, DE PROPÓSITO E COM PROVA (D22) ─────────────────
    # Esta linha dizia `('ROUTE_NOT_ALLOWED', None, None, None)` desde a C10.5D,
    # quando se leu o `robots.txt` vivo de instagram.com (`Disallow: /`).
    #
    # A LEITURA NÃO MUDOU. Mudou quem assume o risco: o dono do projeto
    # autorizou nomeadamente a coleta de REELS do Instagram POR URL DIRECTA,
    # sem login, sem conta e sem rota paga (D22, 2026-09-23), com o risco
    # assumido por ele — como a D17.4 fez com o som do YouTube. A rota passou a
    # declarar os três eixos, e é isso que ela diz agora:
    #
    #     OWNER_AUTHORIZED = SIM          D22 (decisão do PROJETO)
    #     PLATFORM_POLICY_STATUS = DISALLOWED   (medição da PLATAFORMA)
    #     LIMITE = PUBLIC_REEL_BY_URL_ONLY
    #
    #     MEDIR A POLÍTICA NÃO É OBEDECER-LHE: É SABER O QUE SE ASSUME.
    #
    # ── E ESTA É A ÚNICA LINHA QUE MUDOU. As outras 31 continuam congeladas, e
    # este teste continua a MORRER se qualquer uma delas mudar — é para isso que
    # ele existe. Prova por mutação: `tests/mutacao_do_scrap_portas.py`, caso
    # M7, mexe na rota do REDDIT (outra plataforma, outro dono) e exige vermelho
    # AQUI.
    'INSTAGRAM/FETCH_TRANSCRIPT': ('ALLOWED', 'instagram_transcrever.py:faster-whisper', 'SIM', 'PROVED'),
    # ── MUDOU NA C14-C, DE PROPÓSITO E COM PROVA ────────────────────────────
    # Esta linha dizia `('ALLOWED', 'instagram_janela.py:grade', 'CONDICIONAL',
    # 'PROVED')`. Era a ÚNICA capacidade remota do Instagram que chegava a
    # `ALLOWED` sem declarar os três eixos — e medido: um
    # `COLLECT(instagram.profile.discovery)` lançava o navegador num
    # SUBPROCESSO, fora do alcance de qualquer bloqueio de socket.
    #
    # O dono autorizou a DESCOBERTA de perfis públicos (`OWNER_AUTHORIZED =
    # SIM`, `LIMITE = PUBLIC_PROFILE_DISCOVERY_ONLY`), e a política da
    # plataforma continua por medir (`NOT_MEASURED`). Enquanto ninguém a
    # medir, a rota fica fechada:
    #
    #     AUTORIZAR NÃO É MEDIR. E SEM MEDIR, NÃO SAI.
    #
    # Prova em `tests/test_c14c_permissao_instagram.py`: SUBPROCESS_CALLS = 0,
    # NETWORK_CALLS = 0, REMOTE_CAPABILITIES_WITHOUT_GATE = 0.
    'INSTAGRAM/INCREMENTAL': ('ROUTE_NOT_ALLOWED', None, None, None),
    'LINKEDIN/DISCOVER_ACCOUNT': ('ALLOWED', 'descoberta-indireta:site-da-organizacao', 'SIM', 'POSSIBLE_NOT_PROVED'),
    'LINKEDIN/FETCH_POST': ('ROUTE_NOT_ALLOWED', None, None, None),
    'MASTODON/FETCH_PROFILE': ('ALLOWED', 'mastodon:/api/v1/accounts/lookup', 'SIM', 'POSSIBLE_NOT_PROVED'),
    'MASTODON/INCREMENTAL': ('ALLOWED', 'mastodon:/api/v1/accounts/{id}/statuses', 'SIM', 'POSSIBLE_NOT_PROVED'),
    'MASTODON/SEARCH_HASHTAG': ('ALLOWED', 'mastodon:/api/v1/timelines/tag', 'SIM', 'PROVED'),
    'MASTODON/SEARCH_KEYWORD': ('ALLOWED', 'mastodon:/api/v2/search', 'SIM', 'POSSIBLE_NOT_PROVED'),
    'REDDIT/SEARCH_KEYWORD': ('ALLOWED', 'reddit:OAuth Data API', 'CONDICIONAL', 'CREDENTIAL_MISSING'),
    'TELEGRAM/INCREMENTAL': ('ALLOWED', 'telegram:t.me/s/{canal}', 'SIM', 'PROVED'),
    'THREADS/SEARCH_HASHTAG': ('ALLOWED', 'threads:/v1.0/keyword_search?search_mode=TAG', 'CONDICIONAL', 'CREDENTIAL_MISSING'),
    'THREADS/SEARCH_KEYWORD': ('ALLOWED', 'threads:/v1.0/keyword_search', 'CONDICIONAL', 'CREDENTIAL_MISSING'),
    'TIKTOK/DISCOVER_ACCOUNT': ('ROUTE_NOT_ALLOWED', None, None, None),
    'TIKTOK/FETCH_VIDEO_BYTES': ('ALLOWED', 'marcar:MEDIA_FETCH_UNAVAILABLE', 'SIM', 'NOT_APPLICABLE'),
    'TIKTOK/FETCH_VIDEO_METADATA': ('ALLOWED', 'tiktok:oembed', 'CONDICIONAL', 'POSSIBLE_NOT_PROVED'),
    'X/SEARCH_KEYWORD': ('ALLOWED', 'x-api:recent-search', 'SIM', 'CREDENTIAL_MISSING'),
    'YOUTUBE/FETCH_COMMENTS': ('ALLOWED', 'youtube-data-api-v3:commentThreads.list', 'SIM', 'CREDENTIAL_MISSING'),
    'YOUTUBE/FETCH_TRANSCRIPT': ('ALLOWED', 'apify:transcricao', 'CONDICIONAL', 'PARTIAL'),
    'YOUTUBE/FETCH_VIDEO_METADATA': ('ALLOWED', 'youtube-data-api-v3:videos.list', 'SIM', 'CREDENTIAL_MISSING'),
    'YOUTUBE/INCREMENTAL': ('ALLOWED', 'youtube-data-api-v3:playlistItems.list', 'SIM', 'CREDENTIAL_MISSING'),
    'YOUTUBE/SEARCH_KEYWORD': ('ALLOWED', 'youtube-data-api-v3:search.list', 'SIM', 'CREDENTIAL_MISSING'),
}


def _decisoes(ignorar=None):
    saida = {}
    for plat, caps in mz.MATRIZ.items():
        if plat.startswith('_'):
            continue
        for cap in caps:
            if cap.startswith('_') or cap == ignorar:
                continue
            d = mz.decisao(plat, cap)
            saida['%s/%s' % (plat, cap)] = (d['DECISAO'], d['ROTA'],
                                            d['PERMITIDA'], d['ESTADO'])
    return saida


class _RotaTorta:
    """Poe uma rota invalida em memoria, sem escrever lei no disco.

    Mexer no ficheiro para o teste passar seria o teste a escrever a lei que
    diz medir. O teardown desfaz.
    """

    def __init__(self, **troca):
        self.troca = troca

    def __enter__(self):
        self._orig = mz.MATRIZ['YOUTUBE'][GROSSA]
        mz.MATRIZ['YOUTUBE'][GROSSA] = [dict(r, **self.troca) for r in self._orig]
        return self

    def __exit__(self, *_):
        mz.MATRIZ['YOUTUBE'][GROSSA] = self._orig
        return False


# ══════════════════════════════════════════════════════════════════════════
class AUmaPortaSoParaOAudio(unittest.TestCase):

    def test_1_a_capability_fina_tem_exatamente_um_owner_no_registry(self):
        self.assertTrue(cap.existe(FINAS))
        self.assertEqual(cap.estado(FINAS), cap.PROVEN)
        self.assertEqual(cap.prova(FINAS),
                         'docs/sintonia-scrap/C13-YOUTUBE-PUBLIC-AUDIO.md')

    def test_2_o_registry_aponta_para_exatamente_uma_capability_grossa(self):
        self.assertEqual(cap.da_matriz(FINAS), GROSSA)
        self.assertEqual(len([n for n in cap.DECLARADAS if cap.da_matriz(n) == GROSSA]),
                         1, 'duas capacidades finas reivindicam a mesma porta grossa')

    def test_3_a_matriz_declara_a_capability_de_audio(self):
        self.assertIn(GROSSA, mz.CAPACIDADES)
        self.assertIn(GROSSA, mz.MATRIZ['YOUTUBE'])
        self.assertEqual(len(mz.MATRIZ['YOUTUBE'][GROSSA]), 1)
        self.assertEqual(mz.MATRIZ['YOUTUBE'][GROSSA][0]['ROTA'], ROTA)

    def test_4_a_rota_nao_e_NOT_DECLARED(self):
        d = mz.decisao('YOUTUBE', GROSSA)
        self.assertNotEqual(d['DECISAO'], mz.NAO_DECLARADA)
        self.assertEqual(d['DECISAO'], mz.PERMITIDA_SIM)
        self.assertEqual(d['ROTA'], ROTA)


class OsTresEixosSobrevivemSeparados(unittest.TestCase):

    def test_5_technically_works_continua_YES(self):
        self.assertEqual(cap.estado(FINAS), cap.PROVEN)
        self.assertTrue(cap.promete_resultado(FINAS))

    def test_6_owner_authorized_continua_YES(self):
        d = mz.decisao('YOUTUBE', GROSSA)
        self.assertEqual(d['OWNER_AUTHORIZED'], 'SIM')
        self.assertIn(d['OWNER_AUTHORIZED'], mz.OWNER_AUTHORIZED)

    def test_7_platform_policy_continua_DISALLOWED(self):
        d = mz.decisao('YOUTUBE', GROSSA)
        self.assertEqual(d['PLATFORM_POLICY_STATUS'], 'DISALLOWED')
        self.assertIn(d['PLATFORM_POLICY_STATUS'], mz.PLATFORM_POLICY_STATUS)
        # E a proibicao esta escrita na propria nota da rota, com a clausula.
        nota = mz.MATRIZ['YOUTUBE'][GROSSA][0]['NOTA']
        self.assertIn('III.E.1.a', nota)
        self.assertIn('III.I.7', nota)

    def test_8_o_limite_continua_public_only(self):
        d = mz.decisao('YOUTUBE', GROSSA)
        self.assertEqual(d['LIMITE'], 'PUBLIC_AUDIO_ONLY')
        self.assertIn(d['LIMITE'], mz.LIMITES)
        self.assertEqual(d['AUTH_MODE'], 'PUBLIC',
                         'a rota deixou de correr sem sessao')


class AsVizinhasNaoSeMovem(unittest.TestCase):

    def test_9_media_continua_BLOCKED(self):
        self.assertEqual(cap.estado(MEDIA), cap.BLOCKED)
        self.assertFalse(cap.promete_resultado(MEDIA))

    def test_10_caption_continua_PARTIAL(self):
        self.assertEqual(cap.estado(CAPTION), cap.PARTIAL)

    def test_11_audio_nao_implica_video(self):
        """A porta grossa e de BYTES DE SOM, e o nome di-lo."""
        self.assertNotEqual(GROSSA, 'FETCH_VIDEO_BYTES')
        self.assertNotIn('FETCH_VIDEO_BYTES', mz.MATRIZ['YOUTUBE'],
                         'o audio abriu a porta do video')
        self.assertEqual(cap.estado(MEDIA), cap.BLOCKED)

    def test_12_audio_nao_implica_caption(self):
        self.assertNotEqual(GROSSA, 'FETCH_TRANSCRIPT')
        d = mz.decisao('YOUTUBE', 'FETCH_TRANSCRIPT')
        self.assertEqual(d['ROTA'], 'apify:transcricao')
        self.assertNotEqual(d['ROTA'], ROTA)


class NenhumaRotaAntigaMuda(unittest.TestCase):

    def test_13_as_32_decisoes_antigas_estao_intactas(self):
        agora = _decisoes(ignorar=GROSSA)
        self.assertEqual(len(agora), len(DECISOES_ANTIGAS))
        for chave, esperado in sorted(DECISOES_ANTIGAS.items()):
            with self.subTest(decisao=chave):
                self.assertEqual(agora.get(chave), esperado)

    def test_13b_nenhuma_decisao_antiga_carregou_eixos(self):
        """Os campos novos so existem onde foram declarados."""
        for chave, d in _decisoes(ignorar=GROSSA).items():
            for eixo in mz.EIXOS:
                self.assertNotIn(eixo, d, '%s ganhou %s por arrasto' % (chave, eixo))


# ══════════════════════════════════════════════════════════════════════════
class RedTeamDaRota(unittest.TestCase):
    """Os oito ataques. Todos tem de FALHAR."""

    def test_A_prova_de_audio_nao_promove_media(self):
        self.assertEqual(cap.estado(FINAS), cap.PROVEN)
        self.assertEqual(cap.estado(MEDIA), cap.BLOCKED)

    def test_B_prova_de_audio_nao_promove_caption(self):
        self.assertEqual(cap.estado(FINAS), cap.PROVEN)
        self.assertEqual(cap.estado(CAPTION), cap.PARTIAL)

    def test_C_dono_autorizado_nao_vira_plataforma_permitida(self):
        d = mz.decisao('YOUTUBE', GROSSA)
        self.assertEqual(d['OWNER_AUTHORIZED'], 'SIM')
        self.assertEqual(d['PLATFORM_POLICY_STATUS'], 'DISALLOWED')

    def test_D_plataforma_proibida_nao_bloqueia_a_capacidade_tecnica(self):
        self.assertEqual(mz.decisao('YOUTUBE', GROSSA)['PLATFORM_POLICY_STATUS'],
                         'DISALLOWED')
        self.assertEqual(cap.estado(FINAS), cap.PROVEN)

    def test_E_alvo_autenticado_nao_cabe_no_limite_publico(self):
        """Sessao logada dentro de um limite de alvo publico e recusada."""
        with _RotaTorta(CLASSE='LOCAL_SESSION'):
            with self.assertRaises(mz.RotaInvalida):
                mz.conferir_matriz()
        # e sem a torta, a lei volta a passar
        self.assertTrue(mz.conferir_matriz())

    def test_E2_proibicao_sem_autorizacao_do_dono_e_recusada(self):
        with _RotaTorta(OWNER_AUTHORIZED='NAO'):
            with self.assertRaises(mz.RotaInvalida):
                mz.conferir_matriz()
        self.assertTrue(mz.conferir_matriz())

    def test_E3_declaracao_parcial_dos_eixos_e_recusada(self):
        with _RotaTorta():
            orig = mz.MATRIZ['YOUTUBE'][GROSSA]
            torta = dict(orig[0])
            torta.pop('LIMITE')
            mz.MATRIZ['YOUTUBE'][GROSSA] = [torta]
            try:
                with self.assertRaises(mz.RotaInvalida):
                    mz.conferir_matriz()
            finally:
                mz.MATRIZ['YOUTUBE'][GROSSA] = orig
        self.assertTrue(mz.conferir_matriz())

    def test_E4_silencio_do_dono_nao_autoriza(self):
        """Fail-closed: sem OWNER_AUTHORIZED a rota nao e viavel."""
        rota = dict(mz.MATRIZ['YOUTUBE'][GROSSA][0])
        rota.pop('OWNER_AUTHORIZED')
        self.assertFalse(mz._autorizada_pelo_projeto(rota))

    def test_F_capability_nao_declarada_nao_vira_autorizacao_por_silencio(self):
        d = mz.decisao('YOUTUBE', 'FETCH_MEDIA')
        self.assertEqual(d['DECISAO'], mz.NAO_DECLARADA)
        self.assertNotEqual(d['DECISAO'], mz.PERMITIDA_SIM)
        self.assertNotEqual(mz.NAO_DECLARADA, mz.PERMITIDA_SIM)

    def test_G_nao_ha_sinonimo_concorrente_de_audio(self):
        finas = [n for n in cap.DECLARADAS if n.startswith('youtube.') and 'audio' in n]
        self.assertEqual(finas, [FINAS])
        grossas = [c for c in mz.CAPACIDADES if 'AUDIO' in c]
        self.assertEqual(grossas, [GROSSA])
        self.assertNotIn('FETCH_AUDIO', mz.CAPACIDADES)

    def test_H_mexer_na_rota_nova_nao_mexe_nas_antigas(self):
        antes = _decisoes(ignorar=GROSSA)
        with _RotaTorta(PERMITIDA='NAO', ESTADO='ROUTE_NOT_ALLOWED'):
            depois = _decisoes(ignorar=GROSSA)
        self.assertEqual(antes, depois,
                         'mexer na rota de audio mexeu em rota de outra plataforma')
        self.assertEqual(_decisoes(ignorar=GROSSA), DECISOES_ANTIGAS)


if __name__ == '__main__':
    unittest.main(verbosity=2)
