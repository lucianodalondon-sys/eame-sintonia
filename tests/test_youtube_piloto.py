#!/usr/bin/env python3
"""
O PILOTO REAL, provado com transporte falso — sem rede e sem chave verdadeira.

Este arquivo nasce de um defeito meu: `PILOT_READY = SIM` foi anunciado sobre um
`youtube_piloto()` que passava no pré-voo e terminava em `return 4`, sem chamar
NADA. O pré-voo passar não é o piloto rodar.

    PREFLIGHT PASSAR NÃO É PILOTO RODAR.
"""
import io
import json
import os
import sys
import unittest
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import falhas                      # noqa: E402
import social_scrap as sc          # noqa: E402
import social_envelope as env      # noqa: E402
import youtube_oficial as yt       # noqa: E402

FALSA = '-'.join(['CHAVE', 'DE', 'TESTE'])


def erro_http(code, reason):
    corpo = json.dumps({'error': {'code': code, 'errors': [{'reason': reason}]}})

    class _F(urllib.error.HTTPError):
        def __init__(self):
            super().__init__('http://x', code, reason, {}, None)
            self._c = corpo.encode()

        def read(self):
            return self._c
    return _F()


def _canal(cid, uploads, titulo='Canale'):
    return {'items': [{'id': cid, 'snippet': {'title': titulo},
                       'contentDetails': {'relatedPlaylists': {'uploads': uploads}}}]}


def _uploads(*vids):
    return {'items': [{'contentDetails': {'videoId': v},
                       'snippet': {'title': 't-%s' % v}} for v in vids]}


def _videos(*vids):
    return {'items': [{'id': v, 'snippet': {'title': 't', 'channelId': 'UCx'},
                       'statistics': {'viewCount': '10'},
                       'contentDetails': {'duration': 'PT1M'}} for v in vids]}


def _thread(cid, texto, respostas=0, trazidas=0):
    reps = [{'id': '%s.r%d' % (cid, i),
             'snippet': {'textOriginal': 'r%d' % i, 'publishedAt': '2026-01-01T00:00:00Z',
                         'authorChannelId': {'value': 'UCa'}}} for i in range(trazidas)]
    return {'snippet': {'channelId': 'UCx', 'totalReplyCount': respostas,
                        'topLevelComment': {
                            'id': cid,
                            'snippet': {'textOriginal': texto, 'textDisplay': texto,
                                        'publishedAt': '2026-01-01T00:00:00Z',
                                        'updatedAt': '2026-01-01T00:00:00Z',
                                        'likeCount': 1, 'authorDisplayName': 'Tizio',
                                        'authorChannelId': {'value': 'UCa'}}}},
            'replies': {'comments': reps} if reps else {}}


class Fita:
    """Um transporte de fita: devolve na ordem, e conta o que foi pedido."""

    def __init__(self, *respostas):
        self.fila = list(respostas)
        self.chamadas = []

    def __call__(self, url):
        metodo = url.split('/youtube/v3/')[1].split('?')[0]
        self.chamadas.append(metodo)
        r = self.fila.pop(0) if self.fila else {'items': []}
        if isinstance(r, BaseException):
            raise r
        return r


def _um_canal(handle_vids=('v1',), comentarios=None, respostas=0, trazidas=0):
    """A fita de UM canal completo: channels + playlistItems + videos + comments."""
    fita = [_canal('UC%s' % handle_vids[0], 'UU1'), _uploads(*handle_vids),
            _videos(*handle_vids)]
    for _ in handle_vids:
        if comentarios is None:
            fita.append({'items': [_thread('c1', 'ciao', respostas, trazidas)]})
        else:
            fita.append(comentarios)
    return fita


class TestOPilotoRealmenteChama(unittest.TestCase):
    """A trava crítica: passar no pré-voo e não chamar nada é FALHA."""

    def setUp(self):
        self._alvos = sc.ALVOS_YOUTUBE_IT
        self._sessao = yt.Sessao
        os.environ['YOUTUBE_DATA_API_KEY'] = FALSA
        self._raw = env.RAW_DIR
        env.RAW_DIR = os.path.join('/tmp', 'raw-teste-piloto')
        # E O RELATORIO TAMBEM SAI DO ACERVO. `youtube_piloto()` grava
        # `YOUTUBE-PILOTO-IT.json`, e sem isto rodar a suite SOBRESCREVIA o
        # relatorio da corrida real 34258433872 com numeros de fixture —
        # um teste apagando a evidencia que ele deveria proteger.
        self._saida = env.SAIDA
        env.SAIDA = os.path.join('/tmp', 'saida-teste-piloto')

    def tearDown(self):
        sc.ALVOS_YOUTUBE_IT = self._alvos
        yt.Sessao = self._sessao
        env.RAW_DIR = self._raw
        env.SAIDA = getattr(self, '_saida', env.SAIDA)
        os.environ.pop('YOUTUBE_DATA_API_KEY', None)
        import shutil
        shutil.rmtree('/tmp/raw-teste-piloto', ignore_errors=True)

    def _montar(self, alvos, *fita):
        sc.ALVOS_YOUTUBE_IT = alvos
        f = Fita(*fita)
        orig = self._sessao

        def falsa(**kw):
            kw.setdefault('api_key', FALSA)
            kw['transporte'] = f
            return orig(**kw)
        yt.Sessao = falsa
        return f

    # ── 14 e 15 ───────────────────────────────────────────────────────────
    def test_14_o_piloto_NAO_retorna_4(self):
        f = self._montar([('@a', 'imprensa')], *_um_canal(('v1',)))
        r = sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        self.assertNotEqual(r, 4, 'o stub voltou: pre-voo passou e nada rodou')
        self.assertEqual(r, 0)

    def test_15_o_piloto_chama_o_transporte_de_verdade(self):
        f = self._montar([('@a', 'imprensa')], *_um_canal(('v1',)))
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        self.assertGreater(len(f.chamadas), 0, 'PREFLIGHT PASSAR NAO E PILOTO RODAR')
        self.assertIn('channels', f.chamadas)

    def test_TRAVA_passar_no_preflight_sem_chamar_nada_e_FALHA(self):
        """A trava que impede um novo PILOT_READY sobre um stub."""
        f = self._montar([('@a', 'imprensa')], *_um_canal(('v1',)))
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        self.assertIn('channels', f.chamadas,
                      'o piloto terminou sem resolver um unico handle')

    # ── 1 a 7 ─────────────────────────────────────────────────────────────
    def test_1_cinco_handles_resolvem(self):
        fita = []
        for i in range(5):
            fita += [_canal('UC%d' % i, 'UU%d' % i), _uploads('v%d' % i),
                     _videos('v%d' % i), {'items': [_thread('c%d' % i, 'ciao')]}]
        f = self._montar([('@h%d' % i, 'n') for i in range(5)], *fita)
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertEqual(rel['CHANNELS_RESOLVED'], 5)
        self.assertEqual(rel['CHANNELS_FAILED'], 0)
        self.assertEqual([c['CHANNEL_ID'] for c in rel['CANAIS']],
                         ['UC%d' % i for i in range(5)])

    def test_2_um_handle_falha_e_os_outros_continuam(self):
        fita = [erro_http(404, 'channelNotFound')]
        for i in (1, 2):
            fita += [_canal('UC%d' % i, 'UU%d' % i), _uploads('v%d' % i),
                     _videos('v%d' % i), {'items': [_thread('c%d' % i, 'ciao')]}]
        self._montar([('@morto', 'n'), ('@b', 'n'), ('@c', 'n')], *fita)
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertEqual(rel['CHANNELS_FAILED'], 1)
        self.assertEqual(rel['CHANNELS_RESOLVED'], 2, 'um canal morto apagou os outros')
        morto = rel['CANAIS'][0]
        self.assertNotEqual(morto['STATE'], 'ZERO_RESULTS',
                            'canal inexistente virou zero')

    def test_3_SEARCH_fica_em_zero(self):
        self._montar([('@a', 'n')], *_um_canal(('v1',)))
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertEqual(rel['SEARCH_CALLS_USED'], 0,
                         'gastou busca tendo handle conhecido')

    def test_4_a_7_os_metodos_contam_no_bucket_GERAL(self):
        self._montar([('@a', 'n')], *_um_canal(('v1',)))
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        por = rel['POR_METODO']
        for metodo in ('channels.list', 'playlistItems.list', 'videos.list',
                       'commentThreads.list'):
            self.assertIn(metodo, por, metodo)
            self.assertEqual(por[metodo]['BUCKET'], 'GENERAL', metodo)
        self.assertEqual(rel['GENERAL_UNITS_USED'], sum(
            d['UNITS'] for d in por.values() if d['BUCKET'] == 'GENERAL'))

    # ── 8, 9, 10 ──────────────────────────────────────────────────────────
    def test_8_comments_disabled_fica_separado(self):
        fita = [_canal('UC1', 'UU1'), _uploads('v1'), _videos('v1'),
                erro_http(403, 'commentsDisabled')]
        self._montar([('@a', 'n')], *fita)
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertEqual(rel['FEATURE_DISABLED'], 1)
        self.assertEqual(rel['ZERO_RESULTS'], 0)

    def test_9_zero_legitimo_fica_separado(self):
        fita = [_canal('UC1', 'UU1'), _uploads('v1'), _videos('v1'), {'items': []}]
        self._montar([('@a', 'n')], *fita)
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertEqual(rel['ZERO_RESULTS'], 1)
        self.assertEqual(rel['FEATURE_DISABLED'], 0)

    def test_TRES_AUSENCIAS_nunca_se_unem(self):
        tres = {falhas.traduzir('ZERO_RESULTS'), falhas.traduzir('FEATURE_DISABLED'),
                falhas.traduzir('SOURCE_UNAVAILABLE')}
        self.assertEqual(len(tres), 3, 'as tres ausencias colapsaram')

    def test_10_thread_incompleta_chama_comments_list(self):
        fita = [_canal('UC1', 'UU1'), _uploads('v1'), _videos('v1'),
                {'items': [_thread('c1', 'topo', respostas=3, trazidas=1)]},
                {'items': [{'id': 'c1.x%d' % i,
                            'snippet': {'textOriginal': 'x%d' % i,
                                        'publishedAt': '2026-01-01T00:00:00Z',
                                        'authorChannelId': {'value': 'UCa'}}}
                           for i in range(3)]}]
        f = self._montar([('@a', 'n')], *fita)
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        self.assertIn('comments', f.chamadas, 'thread incompleta nao foi fechada')
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertEqual(rel['REPLIES'], 4)
        self.assertEqual(rel['TOP_LEVEL'], 1)

    # ── 11, 12, 13 ────────────────────────────────────────────────────────
    def test_11_RAW_e_criado(self):
        self._montar([('@a', 'n')], *_um_canal(('v1',)))
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertGreater(rel['RAW_FILE_COUNT'], 0)
        self.assertGreater(rel['RAW_TOTAL_BYTES'], 0)
        for f in rel['RAW_FILES']:
            self.assertEqual(len(f['SHA256']), 64, 'RAW sem hash nao e prova')

    def test_12_o_relatorio_declara_o_estado_da_prova(self):
        self._montar([('@a', 'n')], *_um_canal(('v1',)))
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertIn('RAW_PROOF_STATE', rel)
        self.assertIn('PILOT_PROOF', rel['RAW_PRESERVATION_NOTE'])
        self.assertNotIn('OPERATIONAL_STORAGE', rel['RAW_PROOF_STATE'])
        self.assertFalse(rel['OPERATIONAL_OBSERVED'])
        self.assertIn('NOT_OBSERVED', rel['CHECKPOINT_USAGE'])

    def test_13_o_segredo_nunca_aparece(self):
        chave = 'AIza' + 'Q' * 35
        os.environ['YOUTUBE_DATA_API_KEY'] = chave
        self._montar([('@a', 'n')], *_um_canal(('v1',)))
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertNotIn(chave, json.dumps(rel))

    def test_geografia_nunca_e_promovida(self):
        self._montar([('@a', 'n')], *_um_canal(('v1',)))
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertEqual(rel['AUTHOR_LOCATION_PROVED_COUNT'], 0)
        self.assertEqual(rel['SOURCE_LOCATION_PROVED_COUNT'], 0)
        self.assertEqual(rel['COUNTRY_SCOPE'], 'IT')

    def test_one_shot_nao_toca_checkpoint(self):
        f = self._montar([('@a', 'n')], *_um_canal(('v1',)))
        sc.youtube_piloto(sc.ONE_SHOT, limite_videos=1, limite_threads=5)
        rel = env.ler('YOUTUBE-PILOTO-IT.json')
        self.assertIn('NOT_OBSERVED', rel['CHECKPOINT_USAGE'])
        self.assertEqual(rel['APIFY_CALLS'], 0)
        self.assertEqual(rel['APIFY_SPEND_USD'], 0.0)
        self.assertEqual(rel['COST_USD'], 0.0)




class TestAProvaNaoPodeMentir(unittest.TestCase):
    """UPLOAD STEP SUCCESS != ARTIFACT EXISTS.

    Nasce de um defeito real: `if-no-files-found: warn` deixava o passo VERDE com
    zero arquivos, e o estado virava PILOT_PROOF sem prova nenhuma.
    """

    def setUp(self):
        self._raw = env.RAW_DIR
        env.RAW_DIR = os.path.join('/tmp', 'raw-prova-teste')
        env.esquecer_produzidos()
        for v in ('GITHUB_RUN_ID', 'SCRAP_ARTIFACT_OUTCOME', 'SCRAP_ARTIFACT_ID',
                  'SCRAP_ARTIFACT_NAME'):
            os.environ.pop(v, None)

    def tearDown(self):
        env.esquecer_produzidos()
        env.RAW_DIR = self._raw
        import shutil
        shutil.rmtree('/tmp/raw-prova-teste', ignore_errors=True)
        for v in ('GITHUB_RUN_ID', 'SCRAP_ARTIFACT_OUTCOME', 'SCRAP_ARTIFACT_ID',
                  'SCRAP_ARTIFACT_NAME'):
            os.environ.pop(v, None)

    def _com_raw(self, n=2):
        # Pelo MESMO caminho da corrida real (`guardar_raw`), nunca escrevendo
        # no diretorio por fora: arquivo que aparece no disco sem a corrida ter
        # colhido e exatamente o caso que estes testes proibem.
        for i in range(n):
            env.guardar_raw('YOUTUBE', 'prova-%d' % i, {'i': i})

    # ── A ─────────────────────────────────────────────────────────────────
    def test_A_zero_arquivos_nunca_e_prova_completa(self):
        os.environ['GITHUB_RUN_ID'] = '123'
        os.environ['SCRAP_ARTIFACT_OUTCOME'] = 'success'
        os.environ['SCRAP_ARTIFACT_ID'] = '999'
        r = sc._raw_do_piloto('R1')
        self.assertEqual(r['RAW_FILE_COUNT'], 0)
        self.assertEqual(r['RAW_PROOF_STATE'], 'NO_RAW_PRODUCED')
        self.assertFalse(r['RAW_PROOF_COMPLETE'],
                         'zero arquivos viraram PILOT_PROOF_COMPLETE')

    # ── B ─────────────────────────────────────────────────────────────────
    def test_B_arquivos_mais_upload_verde_mais_id_e_prova_completa(self):
        self._com_raw()
        os.environ.update({'GITHUB_RUN_ID': '123',
                           'SCRAP_ARTIFACT_OUTCOME': 'success',
                           'SCRAP_ARTIFACT_ID': '4242'})
        r = sc._raw_do_piloto('R1')
        self.assertEqual(r['RAW_PROOF_STATE'], 'PILOT_PROOF_ACTIONS_ARTIFACT')
        self.assertTrue(r['RAW_PROOF_COMPLETE'])
        self.assertEqual(r['ARTIFACT_ID'], '4242')

    # ── C ─────────────────────────────────────────────────────────────────
    def test_C_upload_falhou_e_PARTIAL_mas_a_medicao_sobrevive(self):
        self._com_raw()
        os.environ.update({'GITHUB_RUN_ID': '123',
                           'SCRAP_ARTIFACT_OUTCOME': 'failure',
                           'SCRAP_ARTIFACT_ID': ''})
        r = sc._raw_do_piloto('R1')
        self.assertIn('PARTIAL_PROOF', r['RAW_PROOF_STATE'])
        self.assertFalse(r['RAW_PROOF_COMPLETE'])
        self.assertGreater(r['RAW_FILE_COUNT'], 0, 'a medicao do RAW se perdeu')

    # ── D ─────────────────────────────────────────────────────────────────
    def test_D_artifact_id_vazio_nunca_e_completo(self):
        self._com_raw()
        os.environ.update({'GITHUB_RUN_ID': '123',
                           'SCRAP_ARTIFACT_OUTCOME': 'success',
                           'SCRAP_ARTIFACT_ID': ''})
        r = sc._raw_do_piloto('R1')
        self.assertFalse(r['RAW_PROOF_COMPLETE'],
                         'step verde sem artifact-id virou prova')
        self.assertIsNone(r['ARTIFACT_ID'], 'inventou um ID que o Actions nao deu')

    def test_o_workflow_nao_usa_mais_warn(self):
        wf = io.open(os.path.join(ROOT, '.github', 'workflows', 'scrap-social.yml'),
                     encoding='utf-8').read()
        # So linhas EXECUTAVEIS. O comentario que explica a remocao cita `warn`
        # de proposito — apagar a memoria do erro nao e consertar o erro.
        executaveis = [l for l in wf.splitlines() if not l.strip().startswith('#')]
        self.assertEqual([l for l in executaveis if 'if-no-files-found: warn' in l], [],
                         '`warn` deixa o passo verde com zero arquivos')
        self.assertIn('if-no-files-found: error', wf)
        self.assertIn('continue-on-error: true', wf,
                      'perder o artefato nao pode apagar a medicao da API')


class TestGuardaDeRef(unittest.TestCase):
    """O workflow vai existir na main; o CODIGO do SCRAP nao.

    A trava e pela PRESENCA do codigo necessario, nunca pelo nome da branch.
    """

    def test_o_workflow_confere_o_codigo_antes_do_segredo(self):
        wf = io.open(os.path.join(ROOT, '.github', 'workflows', 'scrap-social.yml'),
                     encoding='utf-8').read()
        self.assertIn('SCRAP_CODE_NOT_PRESENT_ON_SELECTED_REF', wf)
        # A guarda tem de vir ANTES do passo que recebe os secrets.
        self.assertLess(wf.index('SCRAP_CODE_NOT_PRESENT_ON_SELECTED_REF'),
                        wf.index('YOUTUBE_DATA_API_KEY: ${{ secrets'),
                        'a guarda de ref roda depois do segredo entrar')

    def test_os_tres_arquivos_exigidos_existem_nesta_ref(self):
        for f in ('coleta/social_scrap.py', 'guarda/social_guarda.py',
                  'coleta/youtube_oficial.py'):
            self.assertTrue(os.path.exists(os.path.join(ROOT, f)), f)



# ═══════════════════════════════════════════════════════════════════════════
# CHECKOUT NÃO É COLETA  ·  NOT_EXECUTED NÃO É EXECUTED_ZERO_RESULTS
# ═══════════════════════════════════════════════════════════════════════════
# A corrida 34257202987 falhou no guarda, a fase ficou SKIPPED — e mesmo assim
# o relatório saiu com "PARTIAL_PROOF — houve RAW". O RAW era o do checkout: 23
# arquivos versionados de corridas antigas. Estes testes travam as duas metades
# do defeito: o inventário e o selo.
class ChecarQueCheckoutNaoEColeta(unittest.TestCase):

    def setUp(self):
        env.esquecer_produzidos()
        self.ambiente = dict(os.environ)

    def tearDown(self):
        env.esquecer_produzidos()
        os.environ.clear()
        os.environ.update(self.ambiente)

    def test_raw_do_repo_nao_conta_como_coleta_desta_corrida(self):
        """O disco TEM RAW versionado. Quem não colheu inventaria zero."""
        base = os.path.join(env.RAW_DIR, 'YOUTUBE')
        self.assertTrue(os.path.isdir(base), 'a fixture precisa existir')
        no_disco = sum(len(n) for _r, _s, n in os.walk(base))
        self.assertGreater(no_disco, 0, 'sem RAW no disco o teste não prova nada')

        r = sc._raw_do_piloto('corrida-que-nao-colheu')
        self.assertEqual(r['RAW_FILE_COUNT'], 0)
        self.assertEqual(r['RAW_TOTAL_BYTES'], 0)
        self.assertEqual(r['RAW_PROOF_STATE'], 'NO_RAW_PRODUCED')
        self.assertFalse(r['RAW_PROOF_COMPLETE'])

    def test_o_que_esta_corrida_escreveu_entra_no_inventario(self):
        """E o inventário também não pode ficar cego: o que ela escreve, conta."""
        ref = env.guardar_raw('YOUTUBE', 'teste-inventario-desta-corrida',
                              {'ok': True, 'n': 1})
        r = sc._raw_do_piloto('corrida-que-colheu')
        self.assertEqual(r['RAW_FILE_COUNT'], 1)
        self.assertEqual([a['FILE'] for a in r['RAW_FILES']], [ref['PATH']])
        os.remove(os.path.join(env.ROOT, ref['PATH']))

    def test_fase_que_nao_rodou_nunca_vira_prova(self):
        os.environ['GITHUB_RUN_ID'] = '999'
        os.environ['SCRAP_ARTIFACT_OUTCOME'] = 'success'
        os.environ['SCRAP_ARTIFACT_ID'] = '12345'
        rel = {'ACTIONS_RUN_ID': '999', 'RAW_FILE_COUNT': 23}
        selo = sc._selar_prova(rel, fase_rodou=False)
        self.assertEqual(selo['RAW_PROOF_STATE'], 'NOT_EXECUTED')
        self.assertFalse(selo['RAW_PROOF_COMPLETE'])
        self.assertIsNone(selo['ARTIFACT_ID'])
        self.assertFalse(selo['REPORT_IS_FROM_THIS_RUN'])

    def test_relatorio_de_outra_corrida_nao_e_carimbado(self):
        os.environ['GITHUB_RUN_ID'] = '999'
        os.environ['SCRAP_ARTIFACT_OUTCOME'] = 'success'
        os.environ['SCRAP_ARTIFACT_ID'] = '12345'
        rel = {'ACTIONS_RUN_ID': '111', 'RAW_FILE_COUNT': 23}
        selo = sc._selar_prova(rel, fase_rodou=True)
        self.assertEqual(selo['RAW_PROOF_STATE'], 'NOT_EXECUTED')
        self.assertFalse(selo['REPORT_IS_FROM_THIS_RUN'])
        self.assertIn('outra corrida', selo['NOT_EXECUTED_REASON'])

    def test_corrida_propria_com_artefato_confirmado_e_prova(self):
        """A recusa não pode ter comido o caminho legítimo."""
        os.environ['GITHUB_RUN_ID'] = '999'
        os.environ['SCRAP_ARTIFACT_OUTCOME'] = 'success'
        os.environ['SCRAP_ARTIFACT_ID'] = '12345'
        selo = sc._selar_prova({'ACTIONS_RUN_ID': '999', 'RAW_FILE_COUNT': 4}, True)
        self.assertEqual(selo['RAW_PROOF_STATE'], 'PILOT_PROOF_ACTIONS_ARTIFACT')
        self.assertTrue(selo['RAW_PROOF_COMPLETE'])
        self.assertEqual(selo['ARTIFACT_ID'], '12345')

    def test_corrida_propria_sem_artefato_e_parcial_nunca_completa(self):
        os.environ['GITHUB_RUN_ID'] = '999'
        os.environ['SCRAP_ARTIFACT_OUTCOME'] = 'failure'
        os.environ['SCRAP_ARTIFACT_ID'] = ''
        selo = sc._selar_prova({'ACTIONS_RUN_ID': '999', 'RAW_FILE_COUNT': 4}, True)
        self.assertTrue(selo['RAW_PROOF_STATE'].startswith('PARTIAL_PROOF'))
        self.assertFalse(selo['RAW_PROOF_COMPLETE'])
        self.assertIsNone(selo['ARTIFACT_ID'])


class ChecarOWorkflowNaoRecontaNemMascara(unittest.TestCase):
    """Contra a linha EXECUTÁVEL do YAML, nunca contra o comentário."""

    def setUp(self):
        caminho = os.path.join(sc.env.ROOT, '.github', 'workflows', 'scrap-social.yml')
        with open(caminho, encoding='utf-8') as f:
            bruto = f.read()
        self.executavel = '\n'.join(
            l for l in bruto.split('\n') if not l.lstrip().startswith('#'))

    def test_o_guarda_nao_tem_fallback_que_mascara_o_codigo_de_saida(self):
        self.assertNotIn('|| PYTHONIOENCODING=utf-8 py guarda', self.executavel)

    def test_o_artefato_nao_sobe_o_diretorio_do_checkout(self):
        self.assertNotIn('path: data/samples/SOCIAL-IT/raw-free/', self.executavel)
        self.assertIn('path: .tmp/pilot-proof/', self.executavel)

    def test_o_passo_do_selo_sabe_se_a_fase_rodou(self):
        self.assertIn('SCRAP_FASE_RODOU', self.executavel)
        self.assertIn('_selar_prova', self.executavel)

    def test_o_passo_do_selo_nao_reinventaria_o_raw(self):
        self.assertNotIn('_raw_do_piloto', self.executavel)


if __name__ == '__main__':
    unittest.main(verbosity=1)
