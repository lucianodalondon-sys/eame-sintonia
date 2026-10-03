#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOC1 — a matriz de prontidão de LinkedIn, Instagram e YouTube.

O que estes testes guardam é o que a matriz NÃO pode dizer:

    · o valor de uma credencial, em nenhum sítio;
    · LinkedIn/Instagram prontos enquanto a D15 os tem em POLICY_BLOCK;
    · uma rota PAGA ou de CONTA PESSOAL a passar por grátis;
    · «não sei» a virar «bloqueado».

Nenhuma prova aqui precisa de rede.
"""
import contextlib
import io
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
sys.path.insert(0, os.path.join(RAIZ, 'provas'))
sys.path.insert(0, os.path.join(RAIZ, 'curadoria'))
import prontidao_social_v1 as ps   # noqa: E402

ISCA = 'AIzaSyISCA-SOC1-nunca-deve-aparecer-0000000'  # fake: isca com a forma de uma chave Google, nao e segredo

_MEDIDA = {}


def _medida():
    if 'm' not in _MEDIDA:
        _MEDIDA['m'] = ps.medir(ambiente={'YOUTUBE_DATA_API_KEY': ISCA})
    return _MEDIDA['m']


def _linha(**k):
    base = {'PLATFORM': 'YOUTUBE', 'CAPABILITY': 'x', 'ROTAS': [],
            'PORTA_PONTE': 'ENFILAVEL', 'WORKER_QUALIFY': 'OK',
            'EDGE_EXISTS': True, 'CHECK_STATE': 'CAN_COLLECT_NOW', 'CAN': True,
            'FASES': [('f', 'COLHEITA')]}
    base.update(k)
    return base


def _rota(classe, permitida='SIM'):
    return {'ROTA': 'r', 'CLASSE': classe, 'TIPO': ps.TIPO_DA_CLASSE[classe],
            'PERMITIDA_NA_MATRIZ': permitida, 'ESTADO': 'PROVED', 'CREDENCIAL': None,
            'OWNER_AUTHORIZED': None, 'PLATFORM_POLICY_STATUS': None}


class OSegredoNaoSai(unittest.TestCase):
    def test_a_isca_nao_aparece_no_json(self):
        m = _medida()
        self.assertNotIn(ISCA, json.dumps(m, ensure_ascii=False))
        yt = [c for c in m['CREDENCIAIS'] if c['NOME'] == 'YOUTUBE_DATA_API_KEY']
        self.assertEqual(len(yt), 1)
        # A isca estava lá: a presença mede-se, o valor não sai.
        self.assertEqual(yt[0]['LOCAL'], 'PRESENT_LOCAL')

    def test_a_isca_nao_aparece_no_ecra(self):
        antes = os.environ.get('YOUTUBE_DATA_API_KEY')
        os.environ['YOUTUBE_DATA_API_KEY'] = ISCA
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                ps.main([])
        finally:
            if antes is None:
                os.environ.pop('YOUTUBE_DATA_API_KEY', None)
            else:
                os.environ['YOUTUBE_DATA_API_KEY'] = antes
        self.assertNotIn(ISCA, buf.getvalue())
        self.assertIn('YOUTUBE_DATA_API_KEY', buf.getvalue())

    def test_o_nome_da_chave_e_o_que_o_adaptador_le(self):
        import youtube_oficial as yo
        self.assertEqual(ps.CREDENCIAL_DA_ROTA['youtube-data-api-v3'], yo.ENV_CHAVE)


class AD15ContinuaAMandar(unittest.TestCase):
    def test_linkedin_e_instagram_nunca_prontos(self):
        m = _medida()
        li_ig = [l for l in m['LINHAS'] if l['PLATFORM'] in ('LINKEDIN', 'INSTAGRAM')]
        self.assertTrue(li_ig)
        for l in li_ig:
            self.assertEqual(l['PRONTIDAO'], ps.ROUTE_NOT_ALLOWED, l['CAPABILITY'])
            self.assertTrue(any(f.startswith('DONO: D15') for f in l['FALTA']))

    def test_mesmo_quando_o_check_diz_que_consegue(self):
        # O caso real: instagram.profile.discovery dá CAN_COLLECT_NOW no Scrap.
        l = _linha(PLATFORM='INSTAGRAM', PORTA_PONTE='POLICY_BLOCK',
                   ROTAS=[_rota('PUBLIC_BROWSER', 'CONDICIONAL')])
        self.assertEqual(ps.classificar(l), ps.ROUTE_NOT_ALLOWED)

    def test_a_porta_e_medida_no_worker_real(self):
        m = _medida()
        por_plat = {l['PLATFORM']: l['WORKER_QUALIFY'] for l in m['LINHAS']}
        # SOC-ONDA2 (24/09): a D23 abriu o video de pagina de ORGANIZACAO; o
        # QUALIFY ja nao barra o LinkedIn por politica. A sonda (URL vazia, sem
        # `/company/<slug>/`) para agora por falta de alvo que o Scrap leia.
        self.assertEqual(por_plat['LINKEDIN'], 'BLOCK/CAPABILITY')
        self.assertEqual(por_plat['INSTAGRAM'], 'BLOCK/POLICY')
        self.assertEqual(por_plat['YOUTUBE'], 'BLOCK/CAPABILITY')

    def test_a_sonda_devolve_a_ficha_original(self):
        import worker as wk
        original = wk._ficha_candidata
        ps.porta_da_candidata('YOUTUBE')
        self.assertIs(wk._ficha_candidata, original)


class PagoEPessoalNaoSaoGratis(unittest.TestCase):
    def test_so_rota_paga_nao_e_ready(self):
        l = _linha(ROTAS=[_rota('APIFY', 'CONDICIONAL')])
        self.assertNotEqual(ps.classificar(l), ps.READY)

    def test_conta_pessoal_nao_e_gratis(self):
        self.assertEqual(ps.TIPO_DA_CLASSE['LOCAL_SESSION'], 'CONTA_PESSOAL')
        self.assertNotIn('CONTA_PESSOAL', ps.GRATIS)
        l = _linha(ROTAS=[_rota('LOCAL_SESSION')])
        self.assertNotEqual(ps.classificar(l), ps.READY)

    def test_apify_e_api_paga_sao_pagas(self):
        self.assertEqual(ps.TIPO_DA_CLASSE['APIFY'], 'PAGA')
        self.assertEqual(ps.TIPO_DA_CLASSE['OFFICIAL_API_PAID'], 'PAGA')

    def test_a_legenda_paga_do_youtube_nao_tem_rota_gratis(self):
        # Caso real: a única rota de youtube.native_caption que não é NAO é a Apify.
        m = _medida()
        leg = [l for l in m['LINHAS'] if l['CAPABILITY'] == 'youtube.native_caption'][0]
        self.assertIn('NAO_EXISTE rota grátis permitida na matriz', leg['FALTA'])

    def test_toda_classe_da_matriz_tem_tipo(self):
        import social_matriz as mz
        self.assertEqual(set(ps.TIPO_DA_CLASSE), set(mz.CLASSES))

    def test_rota_gratis_permitida_e_ready(self):
        l = _linha(ROTAS=[_rota('OFFICIAL_API_FREE')])
        self.assertEqual(ps.classificar(l), ps.READY)


class NaoSeiContinuaNaoSei(unittest.TestCase):
    def test_can_none_e_unknown(self):
        l = _linha(CAN=None, CHECK_STATE=None, ROTAS=[_rota('OFFICIAL_API_FREE')])
        self.assertEqual(ps.classificar(l), ps.DESCONHECIDO)

    def test_sem_fase_e_proved_but_not_wired(self):
        l = _linha(FASES=[], ROTAS=[_rota('OFFICIAL_API_FREE')])
        self.assertEqual(ps.classificar(l), ps.PROVED_BUT_NOT_WIRED)

    def test_credencial_so_no_runner(self):
        l = _linha(CHECK_STATE='CREDENTIAL_MISSING', CAN=False,
                   ROTAS=[_rota('OFFICIAL_API_FREE')])
        self.assertEqual(ps.classificar(l), ps.READY_PENDING_CREDENTIAL)

    def test_secret_no_github_e_nao_sei(self):
        for c in _medida()['CREDENCIAIS']:
            self.assertEqual(c['SECRET_PREENCHIDO_NO_GITHUB'], 'NAO_SEI')


class OAvisoDoDonoAparece(unittest.TestCase):
    def test_audio_publico_leva_o_aviso(self):
        m = _medida()
        audio = [l for l in m['LINHAS'] if l['CAPABILITY'] == 'youtube.public_audio']
        self.assertEqual(len(audio), 1)
        self.assertTrue(any('DISALLOWED' in a for a in audio[0]['AVISOS']))


if __name__ == '__main__':
    unittest.main()
