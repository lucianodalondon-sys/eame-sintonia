#!/usr/bin/env python3
"""
Provas do RAW francês — presença não é preservação.

O erro que estes testes existem para impedir é o mais confortável de todos:
olhar um bucket com N objetos, contar N, e escrever "preservado". Um upload
truncado, um retry que gravou por cima e um arquivo com o nome certo e o
conteúdo de outro passam TODOS por essa contagem.

    RAW PRESENCE ≠ RAW CONTENT VERIFIED
    HTTP_5XX     ≠ OBJECT_NOT_PRESERVED
"""
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import adama_fr_raw as raw                                       # noqa: E402


def numeros(**mudanca):
    """Um lote perfeito de 25, com o que o teste quiser estragar."""
    base = dict(RAW_EXPECTED=25, REMOTE_PRESENT=25, REMOTE_ABSENT=0, ORPHANS=0,
                FAILED=0, CONTENT_HASH_CHECKED=25, SHA_VERIFIED=25,
                HASH_MISMATCH=0)
    base.update(mudanca)
    return base


class Portao(unittest.TestCase):

    def test_fecha_quando_tudo_foi_conferido(self):
        g = raw.gate(**numeros())
        self.assertEqual(g['RAW_PRESERVATION_GATE_FR'], 'CLOSED')

    def test_presenca_sem_hash_nao_fecha(self):
        """O erro confortável: 25 objetos existem, e ninguém conferiu os bytes."""
        g = raw.gate(**numeros(CONTENT_HASH_CHECKED=0, SHA_VERIFIED=0))
        self.assertEqual(g['RAW_PRESERVATION_GATE_FR'], 'OPEN')
        self.assertIn('SHA_VERIFIED_EQ_EXPECTED', g['MISSING'])

    def test_um_hash_divergente_derruba_o_lote(self):
        g = raw.gate(**numeros(SHA_VERIFIED=24, HASH_MISMATCH=1))
        self.assertEqual(g['RAW_PRESERVATION_GATE_FR'], 'OPEN')
        self.assertIn('HASH_MISMATCH_ZERO', g['MISSING'])

    def test_lote_vazio_nunca_fecha(self):
        """Zero esperado com zero conferido satisfaria toda igualdade. E é vazio."""
        g = raw.gate(**numeros(RAW_EXPECTED=0, REMOTE_PRESENT=0,
                               CONTENT_HASH_CHECKED=0, SHA_VERIFIED=0))
        self.assertEqual(g['RAW_PRESERVATION_GATE_FR'], 'OPEN')
        self.assertIn('EXPECTED_POSITIVE', g['MISSING'])

    def test_orfao_derruba(self):
        g = raw.gate(**numeros(ORPHANS=1))
        self.assertIn('ORPHANS_ZERO', g['MISSING'])

    def test_ausente_derruba_mesmo_com_o_resto_conferido(self):
        g = raw.gate(**numeros(REMOTE_PRESENT=24, REMOTE_ABSENT=1,
                               CONTENT_HASH_CHECKED=24, SHA_VERIFIED=24))
        self.assertIn('REMOTE_ABSENT_ZERO', g['MISSING'])


class RespostaAmbigua(unittest.TestCase):

    def test_5xx_nao_e_falha(self):
        """Ambíguo não é negativo. Tratar 5xx como falha faria reenviar às cegas."""
        for st in (500, 502, 503, 599):
            with self.subTest(status=st):
                r = raw.apos_resposta_ambigua(st)
                self.assertEqual(r['STATE'], raw.UNKNOWN_MUST_VERIFY)
                self.assertNotEqual(r['STATE'], raw.FAILED)

    def test_5xx_manda_inventariar_e_nao_reenviar(self):
        r = raw.apos_resposta_ambigua(503)
        self.assertIn('inventário', r['NEXT'])
        self.assertIn('cegas', r['DO_NOT'])

    def test_4xx_e_falha_mesmo(self):
        r = raw.apos_resposta_ambigua(400)
        self.assertEqual(r['STATE'], raw.FAILED)


class Transporte(unittest.TestCase):
    """A queda do run 33333878608, virada teste.

    Um `TimeoutError` subiu de dentro de `_http` e derrubou o lote inteiro de
    234 objetos. Pior do que a queda: o processo morreu sem escrever relatorio,
    entao parte tinha subido, parte nao, e ninguem sabia qual era qual.
    """

    def test_falha_de_transporte_nao_levanta_e_vira_status_ambiguo(self):
        def sempre_estoura(*a, **k):
            raise TimeoutError('The read operation timed out')
        original, raw.urllib.request.urlopen = raw.urllib.request.urlopen, sempre_estoura
        try:
            st, body = raw._http('POST', 'https://x/y', 'k', b'z',
                                 tentativas=2, dormir=lambda s: None)
        finally:
            raw.urllib.request.urlopen = original
        self.assertEqual(st, raw.TRANSPORTE_AMBIGUO)
        self.assertIn(b'timed out', body)

    def test_transporte_tenta_de_novo_antes_de_desistir(self):
        tentativas = []

        def estoura(*a, **k):
            tentativas.append(1)
            raise OSError('conexao caiu')
        original, raw.urllib.request.urlopen = raw.urllib.request.urlopen, estoura
        try:
            raw._http('GET', 'https://x/y', 'k', tentativas=3, dormir=lambda s: None)
        finally:
            raw.urllib.request.urlopen = original
        self.assertEqual(len(tentativas), 3)

    def test_resposta_do_servidor_nao_e_repetida_as_cegas(self):
        """403 é resposta, não falha de transporte. Repetir não muda a resposta."""
        chamadas = []

        def http_erro(*a, **k):
            chamadas.append(1)
            raise raw.urllib.error.HTTPError('u', 403, 'no', {}, None)
        original, raw.urllib.request.urlopen = raw.urllib.request.urlopen, http_erro
        try:
            st, _ = raw._http('GET', 'https://x/y', 'k', tentativas=3,
                              dormir=lambda s: None)
        finally:
            raw.urllib.request.urlopen = original
        self.assertEqual(st, 403)
        self.assertEqual(len(chamadas), 1)

    def test_timeout_nao_e_objeto_ausente(self):
        r = raw.apos_resposta_ambigua(raw.TRANSPORTE_AMBIGUO)
        self.assertEqual(r['STATE'], raw.UNKNOWN_MUST_VERIFY)
        self.assertNotEqual(r['STATE'], raw.FAILED)
        self.assertIn('cegas', r['DO_NOT'])


class EnvioRepetivel(unittest.TestCase):
    """Reexecutar depois de uma queda não pode custar o lote inteiro de novo."""

    def setUp(self):
        os.environ['SUPABASE_URL'] = 'https://exemplo.invalid'
        os.environ['SUPABASE_SECRET_KEY'] = 'x'
        self.addCleanup(os.environ.pop, 'SUPABASE_URL', None)
        self.addCleanup(os.environ.pop, 'SUPABASE_SECRET_KEY', None)
        self.tmp = tempfile.mkdtemp(prefix='sintonia-envio-')
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def item(self, chave, corpo=b'abc'):
        """Um item com arquivo DE VERDADE em disco.

        A primeira versão deste teste apontava para um caminho inventado, e o
        envio saía FAILED por não conseguir ler o arquivo — provando outra coisa
        que não a que o teste dizia provar.
        """
        import hashlib
        caminho = os.path.join(self.tmp, chave.replace('/', '_'))
        with open(caminho, 'wb') as fh:
            fh.write(corpo)
        return {'LOCAL_PATH': os.path.relpath(caminho, ROOT),
                'STORAGE_KEY': chave, 'BYTES': len(corpo),
                'SHA256_LOCAL': hashlib.sha256(corpo).hexdigest(),
                'STATE': raw.LOCAL_ONLY, 'CONTENT_TYPE': 'application/pdf'}

    def _com_http(self, resposta):
        original = raw._http
        raw._http = resposta
        self.addCleanup(lambda: setattr(raw, '_http', original))

    def test_objeto_ja_conferido_nao_e_reenviado(self):
        """A chave é endereçada por conteúdo: se está lá e bate, É o objeto certo."""
        item = self.item('FR/a/b.pdf', b'abc')
        metodos = []

        def http(metodo, url, key, dados=None, ctype=None, **k):
            metodos.append(metodo)
            if url.endswith('/bucket/raw'):
                return 200, b'{"name":"raw","file_size_limit":209715200}'
            return 200, b'abc'

        self._com_http(http)
        r = raw.enviar(p={'ITEMS': [item], 'RAW_EXPECTED': 1,
                          'EXCEEDS_BUCKET_LIMIT': False, 'KEY_COLLISIONS': []})
        self.assertEqual(r['SHA_VERIFIED'], 1)
        self.assertNotIn('POST', metodos)

    def test_um_objeto_com_problema_nao_derruba_os_outros(self):
        bom = self.item('FR/a/bom.pdf', b'ok')
        ruim = self.item('FR/a/ruim.pdf', b'zz')

        def http(metodo, url, key, dados=None, ctype=None, **k):
            if url.endswith('/bucket/raw'):
                return 200, b'{"name":"raw"}'
            if 'ruim' in url:
                return raw.TRANSPORTE_AMBIGUO, b'timeout'
            return 200, b'ok'

        self._com_http(http)
        r = raw.enviar(p={'ITEMS': [bom, ruim], 'RAW_EXPECTED': 2,
                          'EXCEEDS_BUCKET_LIMIT': False, 'KEY_COLLISIONS': []})
        self.assertEqual(r['SHA_VERIFIED'], 1)
        self.assertEqual(r['UNKNOWN_MUST_VERIFY'], 1)
        self.assertEqual(r['FAILED'], 0)
        self.assertEqual(r['GATE']['RAW_PRESERVATION_GATE_FR'], 'OPEN')

    def test_o_relatorio_sai_mesmo_quando_ha_problema(self):
        """O pior do run que caiu não foi cair: foi cair sem relatório."""
        def http(metodo, url, key, dados=None, ctype=None, **k):
            if url.endswith('/bucket/raw'):
                return 200, b'{"name":"raw"}'
            return raw.TRANSPORTE_AMBIGUO, b'timeout'

        self._com_http(http)
        r = raw.enviar(p={'ITEMS': [self.item('FR/a/x.pdf')], 'RAW_EXPECTED': 1,
                          'EXCEEDS_BUCKET_LIMIT': False, 'KEY_COLLISIONS': []})
        self.assertIn('GATE', r)
        self.assertIn('BYTES_VERIFIED_REMOTELY', r)
        self.assertEqual(r['BYTES_VERIFIED_REMOTELY'], 0)

    def test_arquivo_local_ilegivel_vira_FAILED_e_nao_derruba_o_lote(self):
        """Ler o disco também pode falhar, e isso é FAILED — não ambíguo."""
        bom = self.item('FR/a/bom.pdf', b'ok')
        sumido = dict(self.item('FR/a/sumido.pdf'), LOCAL_PATH='nao/existe.pdf')

        def http(metodo, url, key, dados=None, ctype=None, **k):
            if url.endswith('/bucket/raw'):
                return 200, b'{"name":"raw"}'
            if 'sumido' in url:
                return 404, b''
            return 200, b'ok'

        self._com_http(http)
        r = raw.enviar(p={'ITEMS': [bom, sumido], 'RAW_EXPECTED': 2,
                          'EXCEEDS_BUCKET_LIMIT': False, 'KEY_COLLISIONS': []})
        self.assertEqual(r['SHA_VERIFIED'], 1)
        self.assertEqual(r['FAILED'], 1)


class Credencial(unittest.TestCase):

    def setUp(self):
        self.antes = {k: os.environ.get(k)
                      for k in ('SUPABASE_URL', 'SUPABASE_SECRET_KEY')}
        for k in self.antes:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self.antes.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_sem_credencial_recusa_e_diz_o_que_falta(self):
        r = raw.enviar(p={'ITEMS': [], 'RAW_EXPECTED': 0,
                          'EXCEEDS_BUCKET_LIMIT': False})
        self.assertEqual(r['STATE'], 'NO_CREDENTIALS')
        self.assertEqual(sorted(r['MISSING']),
                         ['SUPABASE_SECRET_KEY', 'SUPABASE_URL'])

    def test_meia_credencial_tambem_recusa(self):
        os.environ['SUPABASE_URL'] = 'https://exemplo.invalid'
        r = raw.enviar(p={'ITEMS': [], 'RAW_EXPECTED': 0,
                          'EXCEEDS_BUCKET_LIMIT': False})
        self.assertEqual(r['STATE'], 'NO_CREDENTIALS')
        self.assertEqual(r['MISSING'], ['SUPABASE_SECRET_KEY'])


class ArquivoGrande(unittest.TestCase):

    def test_asset_acima_do_limite_para_o_lote_sem_tocar_a_rede(self):
        """Comprimir evidência original para caber mudaria o que ela É.

        E a recusa acontece ANTES de qualquer requisição: um lote já
        desqualificado pelo tamanho não precisa de rede para ser recusado. Este
        teste roda com credencial de mentira de propósito — se alguém inverter a
        ordem e o código sair para a rede, ele quebra aqui e não em produção.
        """
        os.environ['SUPABASE_URL'] = 'https://exemplo.invalid'
        os.environ['SUPABASE_SECRET_KEY'] = 'chave-de-teste'
        try:
            r = raw.enviar(p={'ITEMS': [], 'RAW_EXPECTED': 1,
                              'EXCEEDS_BUCKET_LIMIT': True,
                              'LARGEST_ASSET_BYTES': 300 * 1024 * 1024})
            self.assertEqual(r['STATE'], 'ASSET_TOO_LARGE')
            self.assertIn('não é comprimida', r['WHY'])
        finally:
            os.environ.pop('SUPABASE_URL', None)
            os.environ.pop('SUPABASE_SECRET_KEY', None)

    def test_o_limite_do_bucket_esta_escrito_e_nao_e_adivinhado(self):
        self.assertEqual(raw.LIMITE_BUCKET_BYTES, 200 * 1024 * 1024)


class Canario(unittest.TestCase):
    """A prova de leitura que vem antes de escrever qualquer byte."""

    def setUp(self):
        self.antes = {k: os.environ.get(k)
                      for k in ('SUPABASE_URL', 'SUPABASE_SECRET_KEY')}
        for k in self.antes:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self.antes.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_sem_credencial_o_canario_reprova_e_nao_tenta_upload(self):
        c = raw.canario()
        self.assertEqual(c['SUPABASE_AUTH_CANARY'], 'FAIL')
        self.assertEqual(c['UPLOAD_ATTEMPTS'], 0)

    def test_canario_reprovado_impede_o_envio(self):
        r = raw.enviar(p={'ITEMS': [], 'RAW_EXPECTED': 1,
                          'EXCEEDS_BUCKET_LIMIT': False})
        self.assertEqual(r['STATE'], 'NO_CREDENTIALS')

    def test_limite_por_objeto_nao_e_quota_total(self):
        """200 MB é por arquivo. A quota do projeto é outra coisa, e não se sabe."""
        os.environ['SUPABASE_URL'] = 'https://exemplo.invalid'
        os.environ['SUPABASE_SECRET_KEY'] = 'x'
        chamadas = []

        def falso(metodo, url, key, dados=None, ctype=None):
            chamadas.append((metodo, url))
            return 200, b'{"name":"raw","public":false,"file_size_limit":209715200}'

        original, raw._http = raw._http, falso
        try:
            c = raw.canario()
        finally:
            raw._http = original
        self.assertEqual(c['SUPABASE_AUTH_CANARY'], 'PASS')
        self.assertEqual(c['RAW_BUCKET_ACCESS'], 'PASS')
        self.assertEqual(c['PER_OBJECT_LIMIT_BYTES'], 209715200)
        self.assertEqual(c['TOTAL_STORAGE_QUOTA'], 'NOT_KNOWN')
        self.assertEqual([m for m, _ in chamadas], ['GET'])

    def test_403_no_bucket_reprova_e_zera_tentativas(self):
        os.environ['SUPABASE_URL'] = 'https://exemplo.invalid'
        os.environ['SUPABASE_SECRET_KEY'] = 'x'
        original, raw._http = raw._http, lambda *a, **k: (403, b'{}')
        try:
            c = raw.canario()
        finally:
            raw._http = original
        self.assertEqual(c['SUPABASE_AUTH_CANARY'], 'FAIL')
        self.assertEqual(c['UPLOAD_ATTEMPTS'], 0)


class PlanoDoDisco(unittest.TestCase):

    @unittest.skipUnless(os.path.isfile(raw.MANIFESTO_CATALOGO),
                         'catálogo não coletado nesta máquina')
    def test_o_plano_nao_tem_chave_repetida_com_conteudo_diferente(self):
        """Duas chaves iguais e bytes diferentes sobrescreveriam em silêncio."""
        p = raw.plano()
        self.assertEqual(p['KEY_COLLISIONS'], [])

    @unittest.skipUnless(os.path.isfile(raw.MANIFESTO_CATALOGO),
                         'catálogo não coletado nesta máquina')
    def test_toda_chave_comeca_por_FR(self):
        """Namespace de país no caminho. FR nunca se mistura com ES nem com IT."""
        p = raw.plano()
        self.assertTrue(p['ITEMS'])
        for it in p['ITEMS']:
            self.assertTrue(it['STORAGE_KEY'].startswith('FR/'), it['STORAGE_KEY'])

    @unittest.skipUnless(os.path.isfile(raw.MANIFESTO_CATALOGO),
                         'catálogo não coletado nesta máquina')
    def test_todo_item_nasce_com_sha_e_bytes(self):
        """O plano nasce COM a medição. Medir depois é medir outra coisa."""
        for it in raw.plano()['ITEMS']:
            self.assertEqual(len(it['SHA256_LOCAL']), 64)
            self.assertGreater(it['BYTES'], 0)
            self.assertEqual(it['STATE'], raw.LOCAL_ONLY)
            self.assertIsNone(it['SHA256_REMOTE'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
