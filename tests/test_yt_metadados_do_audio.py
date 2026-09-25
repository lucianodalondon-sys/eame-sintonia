#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YT-METADADOS · O ITEM DE AUDIO CONTA O QUE A PLATAFORMA DECLARA.

O QUE ESTES TESTES GUARDAM, e por que cada um existe
----------------------------------------------------
A SOC-ONDA2 mediu 11 canais: 11/11 trouxeram audio e transcricao e **0** ficaram
PRONTOS. O motivo era do Scrap e tinha nome: o objeto do audio chegava a Sala
**sem `PUBLISHED_AT`**, **sem dizer de que canal veio** e **sem o carimbo do
dono** (D17.4/D22-D24). A regua (`curadoria/regua_social.py`) exige:

    CAMPOS_DO_ITEM = (NATIVE_ID, PUBLISHED_AT, OWNER_AUTHORIZED,
                      PLATFORM_POLICY_STATUS)

...e `OWNER_AUTHORIZED == "SIM"`, e o autor do item tem de casar com a fonte.

    O SOM PROVA QUE ALGUEM DISSE AQUILO. NAO PROVA QUANDO, NEM ONDE.

ESTES TESTES NAO TOCAM A REDE. A aquisicao tem cache em disco: o `.wav` e o
`.info.json` sao escritos numa pasta temporaria, e `ytv.MEDIA` passa a apontar
para ela. Assim mede-se o LEITOR de metadados a serio — e nao um duble que faz
de conta que le.

    UM DUBLE QUE SUBSTITUI O DONO NAO PROVA O DONO.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _g in ('coleta', 'leis', 'regras', 'guarda', 'pedido', 'superficie', 'ferramentas', ''):
    sys.path.insert(0, os.path.join(RAIZ, _g) if _g else RAIZ)
import _gavetas  # noqa: E402,F401
import adaptador_youtube as ay     # noqa: E402
import fala_local as fl            # noqa: E402
import social_matriz as mz         # noqa: E402
import youtube_transcrever as ytv  # noqa: E402

VID = 'ehjdygGJJqQ'

#: O que a PLATAFORMA declara, medido num video real dos 11 canais (2026-09-24).
#: Este dicionario e a forma exata que o `yt-dlp` devolveu — nao e inventado.
DECLARADO = {
    'id': VID, 'title': 'Calathea',
    'upload_date': '20260211', 'release_date': None,
    'timestamp': 1770822151,
    'uploader': 'Cifo Giardinaggio', 'uploader_id': '@cifogiardinaggio',
    'uploader_url': 'https://www.youtube.com/@cifogiardinaggio',
    'channel': 'Cifo Giardinaggio',
    'channel_id': 'UC4A5UdkaIvcbaA7z1mz-YdA',
    'channel_url': 'https://www.youtube.com/channel/UC4A5UdkaIvcbaA7z1mz-YdA',
    'duration': 93, 'view_count': 705, 'availability': 'public',
    'live_status': 'not_live',
}
CANAL = 'UC4A5UdkaIvcbaA7z1mz-YdA'


class AquisicaoOffline(unittest.TestCase):
    """Base comum: pasta temporaria com o `.wav` e o `.info.json` ja em cache."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='ytmd-')
        self._media = ytv.MEDIA
        ytv.MEDIA = self.tmp
        with open(os.path.join(self.tmp, VID + '.wav'), 'wb') as f:
            f.write(b'\x00' * 8000)
        self._escreve_declarado(DECLARADO)
        self._fluxos = fl.fluxos
        self._duracao = fl.duracao
        fl.fluxos = lambda _p: (0, 1, None)      # 0 de imagem, 1 de som
        fl.duracao = lambda _p: 92.74
        self._matriz = None

    def tearDown(self):
        ytv.MEDIA = self._media
        fl.fluxos = self._fluxos
        fl.duracao = self._duracao
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _escreve_declarado(self, md):
        with io.open(os.path.join(self.tmp, VID + '.info.json'), 'w',
                     encoding='utf-8') as f:
            json.dump(md, f, ensure_ascii=False)

    def objeto(self, **kw):
        objs = ay.youtube_audio_publico(run_id='TESTE-YT-MD', country_scope='IT',
                                        video_id=VID, **kw)
        self.assertEqual(len(objs), 1)
        return objs[0]


class OContratoDaRegua(AquisicaoOffline):
    """Os quatro campos que `CAMPOS_DO_ITEM` exige — o motivo do READY = 0."""

    def test_os_quatro_campos_do_contrato_viajam_no_objeto(self):
        o = self.objeto()
        for campo in ('NATIVE_ID', 'PUBLISHED_AT', 'OWNER_AUTHORIZED',
                      'PLATFORM_POLICY_STATUS'):
            self.assertTrue(o.get(campo) and o.get(campo) != 'NAO SEI',
                            'o item chega a Sala sem %s' % campo)

    def test_a_identidade_nativa_e_o_id_da_publicacao(self):
        self.assertEqual(self.objeto()['NATIVE_ID'], VID)

    def test_o_dono_autorizou_e_a_plataforma_proibe_as_duas_frases(self):
        o = self.objeto()
        self.assertEqual(o['OWNER_AUTHORIZED'], 'SIM')
        self.assertEqual(o['PLATFORM_POLICY_STATUS'], 'DISALLOWED')

    def test_o_carimbo_e_copiado_da_matriz_e_nao_escrito_aqui(self):
        """⚠️ O TESTE QUE IMPEDE UMA SEGUNDA LEI.

        Se o adaptador escrevesse `SIM` por conta propria, mexer na matriz nao
        mudava nada — e a politica deixaria de ter um dono so. Com a matriz a
        RECUSAR, o objeto tem de deixar de trazer o carimbo: os valores seguem a
        matriz, e nao a memoria de quem os viu uma vez.

        Medido: `mz.decisao` com a rota recusada devolve `DECISAO=ROUTE_NOT_ALLOWED`
        e NAO devolve as chaves do carimbo — por isso a resposta certa aqui e
        `None`, e nao a palavra `NAO`. Ausencia de carimbo nao e um carimbo.
        """
        original = list(mz.MATRIZ['YOUTUBE']['FETCH_AUDIO_BYTES'])
        try:
            mz.MATRIZ['YOUTUBE']['FETCH_AUDIO_BYTES'] = [
                dict(r, OWNER_AUTHORIZED='NAO', PLATFORM_POLICY_STATUS='NOT_MEASURED')
                for r in original]
            o = self.objeto()
            self.assertIsNone(o['OWNER_AUTHORIZED'],
                              'o objeto inventou um carimbo que a matriz nao deu')
            self.assertIsNone(o['PLATFORM_POLICY_STATUS'])
            decisao = mz.decisao('YOUTUBE', 'FETCH_AUDIO_BYTES')
            self.assertEqual(decisao.get('OWNER_AUTHORIZED'), o['OWNER_AUTHORIZED'])
        finally:
            mz.MATRIZ['YOUTUBE']['FETCH_AUDIO_BYTES'] = original

    def test_o_carimbo_volta_quando_a_matriz_o_volta_a_dar(self):
        """A contraprova: restaurada a matriz, o carimbo volta sozinho."""
        o = self.objeto()
        self.assertEqual(o['OWNER_AUTHORIZED'], 'SIM')

    def test_diz_de_qual_documento_vem_o_carimbo(self):
        self.assertEqual(self.objeto()['AUTORIZACAO_DE'], 'leis/social_matriz.py')

    def test_o_limite_e_o_do_audio_e_vem_da_matriz(self):
        """⚠️ PROVA QUE FALTAVA, E O MUTANTE APANHOU-A.

        O primeiro mutante a sobreviver foi este: trocar o `LIMITE` do audio pelo
        de video de pessoa nao fazia cair prova nenhuma — ou seja, nada guardava a
        fronteira desta rota. A resposta nao foi apagar o mutante: foi escrever a
        prova.
        """
        o = self.objeto()
        self.assertEqual(o['LIMITE'], 'PUBLIC_AUDIO_ONLY')
        self.assertEqual(o['LIMITE'],
                         mz.decisao('YOUTUBE', 'FETCH_AUDIO_BYTES').get('LIMITE'))


class OsTresTempos(AquisicaoOffline):
    """FACT_TIME != PUBLISHED_AT != COLLECTED_AT."""

    def test_sao_tres_valores_e_nenhum_se_deduz_do_outro(self):
        o = self.objeto()
        tempos = (o.get('FACT_TIME'), o.get('PUBLISHED_AT'), o.get('COLLECTED_AT'))
        self.assertTrue(all(tempos), 'faltou um dos tres tempos: %r' % (tempos,))
        self.assertEqual(len(set(tempos)), 3, 'dois tempos colapsaram: %r' % (tempos,))

    def test_publicacao_nao_vira_fact_time(self):
        o = self.objeto()
        self.assertEqual(o['FACT_TIME'], 'NAO SEI')
        self.assertNotEqual(o['FACT_TIME'], o['PUBLISHED_AT'])
        self.assertTrue(o.get('FACT_TIME_PORQUE'), 'o NAO SEI saiu sem motivo')

    def test_a_publicacao_e_a_da_plataforma_com_a_precisao_dita(self):
        o = self.objeto()
        self.assertEqual(o['PUBLISHED_AT'], '2026-02-11T15:02:31Z')
        self.assertEqual(o['PUBLISHED_AT_PRECISION'], 'SECOND')
        self.assertIn('yt-dlp', o['PUBLISHED_AT_SOURCE'])

    def test_so_o_dia_quando_a_plataforma_so_da_o_dia(self):
        """Sem `timestamp`, a data sai com precisao de DIA — nao a meio-dia."""
        md = dict(DECLARADO, timestamp=None)
        self.assertEqual(ytv.declarado_em(md), ('2026-02-11T00:00:00Z', 'DAY'))

    def test_sem_data_nenhuma_a_resposta_e_nao_sei(self):
        self.assertEqual(ytv.declarado_em({}), ('NAO SEI', 'NAO DECLARADA'))
        self.assertEqual(ytv.declarado_em({'upload_date': 'ontem'}),
                         ('NAO SEI', 'NAO DECLARADA'))


class OCanalDeOndeVeio(AquisicaoOffline):
    """Sem isto, a regua nao pode conferir se quem publicou e a propria fonte."""

    def test_o_canal_viaja_com_id_nome_e_endereco(self):
        o = self.objeto()
        self.assertEqual(o['CHANNEL_ID'], CANAL)
        self.assertEqual(o['CHANNEL_NAME'], 'Cifo Giardinaggio')
        self.assertIn(CANAL, o['CHANNEL_URL'])

    def test_o_raw_diz_o_autor_no_sitio_onde_a_regua_le(self):
        raw = self.objeto().get('RAW') or {}
        self.assertEqual(raw.get('CREATOR_URL'), DECLARADO['channel_url'])
        self.assertTrue(raw.get('CREATOR_NAME'))

    def test_sem_canal_declarado_a_estado_e_nao_sei(self):
        self._escreve_declarado({k: v for k, v in DECLARADO.items()
                                 if not k.startswith('channel')})
        o = self.objeto()
        self.assertIsNone(o.get('CHANNEL_ID'))
        self.assertEqual(o['CHANNEL_ID_ESTADO'], 'NAO SEI')


class SemMetadadosNaoSeInventa(AquisicaoOffline):
    """O yt-dlp sem resposta nao autoriza uma data aproximada."""

    def test_sem_declarado_o_objeto_sai_nao_sei_e_com_motivo(self):
        """⚠️ O `.info.json` VAZIO NAO SERVE PARA ESTE TESTE, e foi medido.

        `metadados()` so aceita cache com mais de 2 bytes; um ficheiro vazio faz
        a funcao ir a REDE — e o teste mediria a rede em vez da lei. O declarado
        aqui tem conteudo e simplesmente NAO TEM DATA, que e o caso a testar.
        """
        self._escreve_declarado({'id': VID, 'title': 'sem data nenhuma'})
        o = self.objeto()
        self.assertEqual(o['PUBLISHED_AT'], 'NAO SEI')
        self.assertEqual(o['PUBLISHED_AT_PRECISION'], 'NAO DECLARADA')
        self.assertIsNone(o.get('CHANNEL_ID'))
        self.assertEqual(o['CHANNEL_ID_ESTADO'], 'NAO SEI')

    def test_o_leitor_de_metadados_corta_o_que_ninguem_leu(self):
        """A lista de campos e FECHADA: o dicionario inteiro do yt-dlp nao entra."""
        bruto = dict(DECLARADO, campo_inventado='x', formats=[1, 2, 3])
        self._escreve_declarado(bruto)
        md, motivo = ytv.metadados(VID)
        self.assertEqual(motivo, 'CACHE')
        self.assertNotIn('campo_inventado', md)
        self.assertNotIn('formats', md)
        self.assertEqual(md['channel_id'], CANAL)


if __name__ == '__main__':
    unittest.main(verbosity=2)
