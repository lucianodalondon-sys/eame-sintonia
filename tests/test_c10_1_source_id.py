#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.1 — O REEL NAO FABRICA SOURCE_ID COM URL.

    SOURCE_ID   identidade canonica da fonte, atribuida por quem a tem
    SOURCE_URL  o endereco por onde se chegou a ela

Ate a C10 a ficha RAW punha o endereco nos dois campos. A C10 acrescentou uma
etiqueta a dizer que era substituto, e uma etiqueta nao transforma um URL em
identidade — pedia desculpa pela mentira sem a desfazer.

O QUE TORNA ISTO GRAVE, E NAO APENAS FEIO
------------------------------------------
`guarda/preservar_coleta._identifica()` e a trava da casa: recusa as confissoes
e aceita tudo o resto. Medido:

    _identifica('https://www.instagram.com/reel/ABC')  ->  True
    _identifica('NAO SEI')                             ->  False

O endereco COMPRAVA um `IDENTITY_STATE` que ninguem provou, exatamente no sitio
onde a casa poe a trava.

    CAN ENTER NAO SE COMPRA COM IDENTIDADE FALSA.

Estes testes existem para reprovar o regresso. A mutacao
`SOURCE_ID = SOURCE_URL` tem de cair aqui.
"""
import io
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('ferramentas', 'leis', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import artefato as art            # noqa: E402
import preservar_coleta as pc     # noqa: E402
import reel_transcricao as rt     # noqa: E402

URL = 'https://www.instagram.com/reel/ABC12345678/'
ID_PROVADO = 'IG-CANAL-0042'


def _ficheiro(pasta, nome='bytes.m4a', corpo=b'x' * 20000):
    caminho = os.path.join(pasta, nome)
    with io.open(caminho, 'wb') as f:
        f.write(corpo)
    return caminho


class ATravaDaCasaReconheceOsDois(unittest.TestCase):
    """A medicao que nomeia o dano. Se isto mudar, o resto perde o sentido."""

    def test_um_endereco_passa_na_trava_e_um_sentinela_nao(self):
        self.assertTrue(pc._identifica(URL),
                        'um URL passa no `_identifica` — e e por isso que po-lo '
                        'em SOURCE_ID comprava identidade')
        self.assertFalse(pc._identifica(art.NAO_SEI))
        self.assertFalse(pc._identifica(None))
        self.assertFalse(pc._identifica('   '))

    def test_o_sentinela_do_contrato_e_uma_das_confissoes_da_casa(self):
        # Se o contrato do artefato e a trava deixassem de falar a mesma lingua,
        # a ficha ficaria com uma palavra que a trava nao reconhece — e voltava
        # a comprar passagem, agora por outra porta.
        self.assertIn(art.NAO_SEI.upper(), pc.SENTINELAS)


class CasoA_SourceIdProvado(unittest.TestCase):
    """Quando a identidade existe, ela e transportada — exatamente."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='c101-a-')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_o_source_id_provado_chega_intacto_e_o_url_fica_no_seu_campo(self):
        ident = {'SOURCE_ID': ID_PROVADO, 'SOURCE_URL': URL,
                 'POST_ID': 'ABC12345678', 'PLATFORM': 'INSTAGRAM'}
        raw = rt._ficha_raw(_ficheiro(self.tmp), ident, run_id='R1',
                            capture_provider=rt.CAPTURA_YTDLP,
                            media_kind=rt.MIDIA_AUDIO)
        self.assertEqual(raw.SOURCE_ID, ID_PROVADO)
        self.assertEqual(raw.SOURCE_URL, URL)
        self.assertNotEqual(raw.SOURCE_ID, raw.SOURCE_URL)
        self.assertTrue(pc._identifica(raw.SOURCE_ID))

    def test_um_source_id_provado_nao_e_reescrito_pelo_endereco(self):
        # O ataque: SOURCE_ID provado e SOURCE_URL DIFERENTE. Se alguem voltar a
        # derivar do endereco, o provado desaparece sem ninguem dar por isso.
        ident = {'SOURCE_ID': ID_PROVADO,
                 'SOURCE_URL': 'https://www.instagram.com/reel/OUTRO/'}
        raw = rt._ficha_raw(_ficheiro(self.tmp, 'b.m4a'), ident, run_id='R1',
                            capture_provider=rt.CAPTURA_YTDLP)
        self.assertEqual(raw.SOURCE_ID, ID_PROVADO)


class CasoB_SoOEndereco(unittest.TestCase):
    """Sem prova, SOURCE_ID fica desconhecido — e desconhecido nao e o URL."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='c101-b-')
        self.ident = rt.identidade_do_url(URL)
        self.raw = rt._ficha_raw(_ficheiro(self.tmp), self.ident, run_id='R1',
                                 capture_provider=rt.CAPTURA_YTDLP,
                                 media_kind=rt.MIDIA_AUDIO)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_o_url_nao_aparece_no_campo_de_identidade(self):
        # ESTE E O TESTE QUE A MUTACAO `SOURCE_ID = SOURCE_URL` TEM DE DERRUBAR.
        self.assertNotEqual(self.raw.SOURCE_ID, self.raw.SOURCE_URL)
        self.assertNotIn('instagram.com', str(self.raw.SOURCE_ID))
        self.assertNotIn('http', str(self.raw.SOURCE_ID))

    def test_o_campo_fica_no_sentinela_que_a_trava_recusa(self):
        self.assertEqual(self.raw.SOURCE_ID, art.NAO_SEI)
        self.assertFalse(pc._identifica(self.raw.SOURCE_ID),
                         'o SOURCE_ID desta ficha compraria identidade')

    def test_o_endereco_continua_preservado_no_campo_do_endereco(self):
        # CORRIGIR IDENTIDADE != PERDER O ENDERECO.
        self.assertIn('instagram.com/reel/ABC12345678', self.raw.SOURCE_URL)

    def test_a_ficha_nao_declara_mais_um_substituto_que_nao_existe(self):
        notas = self.raw.NOTES or {}
        self.assertNotIn('SOURCE_ID_KIND', notas,
                         'o campo descreve um arranjo que deixou de existir')

    def test_nada_de_document_id_fabricado(self):
        for proibido in ('DOCUMENT_ID', 'DOCUMENT_KEY'):
            self.assertFalse(pc._identifica((self.raw.NOTES or {}).get(proibido)),
                             '%s foi fabricado' % proibido)
        self.assertFalse(pc._identifica(getattr(self.raw, 'DOCUMENT_ID', None)))

    def test_o_post_id_nao_virou_identidade_de_fonte(self):
        # POST_ID e metadado da plataforma. Pode existir; nao pode ser promovido.
        self.assertEqual((self.raw.NOTES or {}).get('POST_ID'), 'ABC12345678')
        self.assertNotEqual(self.raw.SOURCE_ID, 'ABC12345678')

    def test_nem_o_sha_nem_o_caminho_viraram_identidade_de_fonte(self):
        self.assertNotEqual(self.raw.SOURCE_ID, self.raw.SHA256)
        self.assertNotEqual(self.raw.SOURCE_ID, self.raw.STORAGE_LOCATION)

    def test_ignorancia_de_fonte_nao_apaga_a_observacao(self):
        # UNKNOWN SOURCE_ID != AUSENCIA DE OBSERVACAO. Tudo o resto fecha.
        self.assertTrue(self.raw.SHA256)
        self.assertTrue(self.raw.STORAGE_LOCATION)
        self.assertEqual(self.raw.RUN_ID, 'R1')
        self.assertTrue(self.raw.ARTIFACT_ID)
        notas = self.raw.NOTES or {}
        self.assertEqual(notas.get('CAPTURE_PROVIDER'), rt.CAPTURA_YTDLP)
        self.assertEqual(notas.get('MEDIA_KIND'), rt.MIDIA_AUDIO)
        self.assertEqual(notas.get('RAW_OBSERVATION_ID'), rt.NOT_KNOWN)

    def test_a_porta_nao_ganha_atalho(self):
        # A trava vai dizer «sem fonte» — e isso e o estado CORRETO de hoje, nao
        # um defeito a contornar. Antes desta missao ela dizia
        # FORWARD_IDENTITY_UNPROVEN, comprado com o endereco.
        id_obs = pc.identidade_da_observacao(
            {'SOURCE_ID': self.raw.SOURCE_ID, 'DOCUMENT_ID': None})
        self.assertIsNone(id_obs['IDENTITY_STATE'])
        self.assertIsNone(id_obs['SOURCE_ID'])
        comprado = pc.identidade_da_observacao(
            {'SOURCE_ID': self.raw.SOURCE_URL, 'DOCUMENT_ID': None})
        self.assertEqual(comprado['IDENTITY_STATE'], pc.FORWARD_IDENTITY_UNPROVEN,
                         'se isto mudar, a medicao que justifica esta missao '
                         'deixou de valer e o teste tem de ser remedido')


class ONinguemDerivaIdentidadeDeEndereco(unittest.TestCase):
    """A sentinela da lei, lida no codigo e nao no texto."""

    def test_a_ficha_raw_nao_le_source_url_para_o_campo_de_identidade(self):
        import ast
        with io.open(os.path.join(RAIZ, 'ferramentas', 'reel_transcricao.py'),
                     encoding='utf-8') as fh:
            arvore = ast.parse(fh.read())
        alvo = [n for n in ast.walk(arvore)
                if isinstance(n, ast.FunctionDef) and n.name == '_ficha_raw']
        self.assertEqual(len(alvo), 1)
        for kw in ast.walk(alvo[0]):
            if not isinstance(kw, ast.keyword) or kw.arg != 'SOURCE_ID':
                continue
            lidos = [a.value for a in ast.walk(kw.value)
                     if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            self.assertNotIn('SOURCE_URL', lidos,
                             'SOURCE_ID voltou a ser lido do endereco')
            self.assertIn('SOURCE_ID', lidos)


if __name__ == '__main__':
    unittest.main(verbosity=2)
