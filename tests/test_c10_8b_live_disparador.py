# -*- coding: utf-8 -*-
"""C10.8B-LIVE — o disparador não é o motor.

    WORKFLOW É DISPARADOR. WORKFLOW NÃO É MOTOR DE COLETA.
    E UM TETO QUE VIVE NO DISPARADOR É UM TETO QUE QUEM DISPARA ESCOLHE.

O que estas sentinelas guardam: o workflow nomeia UMA fase e mais nada; a
autorização, o motivo, o alvo e os dois tetos vivem em Python versionado; e o
comando que o workflow corre atravessa o `COLLECT` como qualquer outro.
"""
import ast
import io
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', 'tests', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import adaptador_youtube as ay                                    # noqa: E402
import coletor as ct                                              # noqa: E402
import scrap_registo as reg                                       # noqa: E402
import social_scrap as ss                                         # noqa: E402
reg.carregar_adaptadores()

FASE = 'yt-legenda-paga'

# ── ESTA SUITE ATRAVESSA A PORTA PAGA, E DECLARA A AUTORIZACAO ─────────────
# A SCRAP-SR-02 fechou a criacao de execucao paga atras de uma guarda. Esta
# suite corre `social_scrap.coletar` — um caminho de PRODUCAO — contra um
# provider falso. O caminho de producao NAO fabrica autorizacao nenhuma, e e
# assim que tem de ser:
#
#     UM SCRIPT QUE ASSINA A PROPRIA AUTORIZACAO NAO E UM SCRIPT AUTORIZADO.
#
# Quem assina e quem mede. Aqui, a suite.
def _ensaio_pago(posts=4):
    import autorizacao_de_gasto as _ag
    return _ag.Autorizacao(
        MODO=_ag.TRIAL, ALVO='C10.8B-LIVE · disparador · %s' % FASE,
        HUMAN_AUTHORIZATION='suite C10.8B-LIVE · provider falso · zero dolar',
        MAX_PROVIDER_RUNS=posts, MAX_START_POSTS=posts, MAX_USD=99.0,
        MAX_ITEMS=10 ** 6)

WORKFLOW = '.github/workflows/sintonia-scrap.yml'
ALVO = 'EAkcA_2FDN8'


_GAVETA_REAL = ss.GAVETA_PAGA


def setUpModule():
    """A bateria escreve registos de fase paga. Eles NÃO entram na árvore.

    Uma suite que deixa artefacto no repositório faz o commit seguinte carregar
    o que ela produziu — e um artefacto de teste dentro do acervo é um facto
    que ninguém colheu.
    """
    import tempfile
    ss.GAVETA_PAGA = tempfile.mkdtemp(prefix='t-c108b-live-')


def tearDownModule():
    import shutil
    shutil.rmtree(ss.GAVETA_PAGA, ignore_errors=True)
    ss.GAVETA_PAGA = _GAVETA_REAL


def _fonte(rel):
    return io.open(os.path.join(RAIZ, rel), encoding='utf-8').read()


def _sem_comentarios(texto):
    """O YAML SEM a prosa. Uma sonda que lê comentários lê o que eu escrevi.

    A primeira versão de `test_4` procurava `0,10` no ficheiro inteiro e acusou
    o comentário que explica por que o teto NÃO vive ali.

        UMA SONDA QUE LÊ A PROSA ENCONTRA A FRASE QUE EXPLICA A REGRA
        E CHAMA-LHE VIOLAÇÃO DA REGRA.
    """
    fora = []
    for linha in texto.splitlines():
        sem = re.sub(r'(?<!\$)#.*$', '', linha)
        if sem.strip():
            fora.append(sem)
    return '\n'.join(fora)


def _yaml():
    import yaml
    d = yaml.safe_load(_fonte(WORKFLOW))
    gatilho = d[next(k for k in d if str(k) in ('on', 'True'))]
    return d, gatilho


class ODisparadorNaoEOMotor(unittest.TestCase):

    def test_1_o_workflow_nao_nomeia_ator_nenhum(self):
        """Aqui lê-se o ficheiro INTEIRO, comentários incluídos — de propósito.

        Para o teto e o alvo, a prosa é explicação legítima e a sonda tem de a
        ignorar. Para o ID do ator não há explicação legítima: um comentário que
        o nomeia vira o sítio de onde as pessoas o leem, e envelhece sozinho.

            UM ATOR NOMEADO NUM COMENTÁRIO É UM ATOR QUE O DISPARADOR CONHECE.
        """
        fonte = _fonte(WORKFLOW)
        self.assertNotIn(ay.ATOR_TRANSCRICAO, fonte)
        self.assertNotIn('pintostudio', fonte)
        self.assertEqual(re.findall(r'[a-z0-9_-]+~[a-z0-9-]+', fonte), [],
                         'entrou um ID de ator no disparador')

    def test_2_o_workflow_nao_fala_com_o_provider(self):
        fonte = _sem_comentarios(_fonte(WORKFLOW))
        for proibido in ('api.apify.com', 'maxTotalChargeUsd', 'usageTotalUsd',
                         'acts/', 'actor-runs'):
            self.assertNotIn(proibido, fonte,
                             'o disparador passou a falar com o provider: %s'
                             % proibido)

    def test_3_a_fase_paga_entra_pela_porta_canonica(self):
        fonte = _fonte(WORKFLOW)
        bloco = fonte.split('%s)' % FASE, 1)
        self.assertEqual(len(bloco), 2, 'a fase paga saiu do disparador')
        corpo = bloco[1].split(';;', 1)[0]
        self.assertIn('coleta/social_scrap.py', corpo)
        self.assertIn('coletar %s' % FASE, corpo)
        for proibido in ('coletor.py', 'adaptador_youtube', 'instagram_coleta',
                         'sensor_coleta'):
            self.assertNotIn(proibido, corpo,
                             'a fase paga passou a chamar um motor directo')

    def test_4_o_disparador_nao_declara_teto_nem_alvo_nem_motivo(self):
        """O que se mede é o RAMO PAGO, e não o ficheiro inteiro.

        `ROUTE_NOT_ALLOWED` aparece noutro ramo, dentro da frase que explica por
        que `timedtext` é recusada. Essa string é uma EXPLICAÇÃO, e não uma
        decisão desta fase — e uma sonda que não distingue as duas reprova a
        documentação.
        """
        fonte = _sem_comentarios(_fonte(WORKFLOW))
        ramo = fonte.split('%s)' % FASE, 1)[1].split(';;', 1)[0]
        for proibido in ('0.10', '0,10', ALVO, 'ROUTE_NOT_ALLOWED', 'TRIAL',
                         'teto_de_gasto', 'teto_de_rede', 'permitir_pago',
                         'motivo_pago'):
            self.assertNotIn(proibido, ramo,
                             'o ramo pago do disparador passou a decidir `%s`'
                             % proibido)
        # e estes nunca podem aparecer em lado nenhum do ficheiro
        for nunca in ('teto_de_gasto', 'teto_de_rede', 'permitir_pago',
                      'motivo_pago', 'FASES_PAGAS'):
            self.assertNotIn(nunca, fonte,
                             'o disparador ganhou vocabulario de orcamento: %s'
                             % nunca)

    def test_5_a_fase_existe_no_menu_e_e_uma_so(self):
        _d, gatilho = _yaml()
        opcoes = gatilho['workflow_dispatch']['inputs']['fase']['options']
        self.assertIn(FASE, opcoes)
        pagas = [o for o in opcoes if o in ss.FASES_PAGAS]
        self.assertEqual(pagas, [FASE],
                         'nasceu uma segunda fase paga no disparador: %s' % pagas)

    def test_6_o_segredo_chega_ao_job_que_corre_a_fase(self):
        d, _g = _yaml()
        job = d['jobs']['coleta']
        self.assertIn('APIFY_TOKEN_POOL', job.get('env', {}),
                      'o job perdeu a credencial paga')
        self.assertIn('secrets.APIFY_TOKEN_POOL',
                      str(job['env']['APIFY_TOKEN_POOL']))

    def test_7_nao_nasceu_um_segundo_runtime(self):
        d, _g = _yaml()
        self.assertEqual(sorted(d['jobs']), ['coleta'],
                         'o disparador ganhou um segundo job')
        for proibido in ('c10_8b_runner', 'paid_executor', 'youtube_apify_live'):
            self.assertNotIn(proibido, _fonte(WORKFLOW))


class OQueTornaAFasePagaViveEmPython(unittest.TestCase):

    def test_8_a_declaracao_esta_na_tabela_e_nao_no_yaml(self):
        d = ss.FASES_PAGAS[FASE]
        self.assertEqual(d['TETO_DE_GASTO_USD'], 0.10)
        self.assertEqual(d['TETO_DE_REDE'], 5)
        self.assertEqual(d['MOTIVO_PAGO'], 'ROUTE_NOT_ALLOWED')
        self.assertEqual(d['MODO'], 'TRIAL')
        self.assertTrue(d['AUTORIZACAO'])
        self.assertTrue(d['ALVO_PORQUE'])

    def test_9_o_teto_declarado_nunca_passa_do_autorizado(self):
        for fase, d in ss.FASES_PAGAS.items():
            with self.subTest(fase=fase):
                self.assertLessEqual(d['TETO_DE_GASTO_USD'], 0.10,
                                     'uma fase paga passou do autorizado')

    def test_10_o_alvo_e_a_sentinela_do_acervo(self):
        _plat, _cap, fixos = ss.FASES_CANONICAS[FASE]
        self.assertEqual(fixos, {'video_id': ALVO})

    def test_11_o_motivo_pertence_ao_vocabulario_canonico(self):
        import social_matriz as mz
        for _fase, d in ss.FASES_PAGAS.items():
            self.assertIn(d['MOTIVO_PAGO'], mz.MOTIVOS_PAGOS)

    def test_12_a_fase_paga_e_canonica_como_as_outras(self):
        for fase in ss.FASES_PAGAS:
            self.assertIn(fase, ss.FASES_CANONICAS,
                          '%s e paga e nao entra pelo boundary' % fase)
            self.assertNotIn(fase, ss.FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY)


class OComandoDoWorkflowAtravessaOBoundary(unittest.TestCase):
    """O que o disparador corre é o que estas sentinelas medem."""

    def test_13_a_cli_passa_os_dois_tetos_e_a_autorizacao(self):
        import scrap_executor as sx
        pedidos = []
        real = sx.COLLECT
        sx.COLLECT = lambda **k: (pedidos.append(k), ([], {'RESULT': 'OK'}))[1]
        try:
            with __import__("autorizacao_de_gasto").autorizacao(_ensaio_pago()):
                ss.coletar(FASE, banco=None)
        finally:
            sx.COLLECT = real
        self.assertEqual(len(pedidos), 1)
        k = pedidos[0]
        self.assertEqual(k['platform'], 'YOUTUBE')
        self.assertEqual(k['capability'], 'youtube.native_caption')
        self.assertEqual(k['video_id'], ALVO)
        self.assertEqual(k['modo'], 'TRIAL')
        self.assertIs(k['permitir_pago'], True)
        self.assertEqual(k['motivo_pago'], 'ROUTE_NOT_ALLOWED')
        self.assertEqual(k['teto_de_gasto'], 0.10)
        self.assertEqual(k['teto_de_rede'], 5)

    def test_14_as_fases_gratuitas_continuam_sem_autorizacao_de_gasto(self):
        import scrap_executor as sx
        real = sx.COLLECT
        for fase in ss.FASES_CANONICAS:
            if fase in ss.FASES_PAGAS:
                continue
            pedidos = []
            sx.COLLECT = lambda **k: (pedidos.append(k), ([], {'RESULT': 'OK'}))[1]
            try:
                with __import__("autorizacao_de_gasto").autorizacao(_ensaio_pago()):
                    ss.coletar(fase, banco=None)
            finally:
                sx.COLLECT = real
            with self.subTest(fase=fase):
                self.assertNotIn('permitir_pago', pedidos[0])
                self.assertNotIn('teto_de_gasto', pedidos[0])

    def test_15_o_comando_inteiro_faz_um_so_POST(self):
        """O caminho REAL do workflow, com só a API do provider falsa."""
        import test_c10_8b_rota_paga_canonica as T
        f = T._Falsa(texto=T._texto_real())
        with __import__("autorizacao_de_gasto").autorizacao(_ensaio_pago()), \
                T._Cenario(f):
            saida = ss.coletar(FASE, banco=None)
        self.assertEqual(len(f.posts), 1, 'o comando do workflow nao fez UM POST')
        self.assertIsNotNone(f.posts[0]['cap'])
        self.assertLessEqual(f.posts[0]['cap'], 0.10)
        self.assertEqual(f.posts[0]['entrada'], {
            'videoUrl': 'https://www.youtube.com/watch?v=%s' % ALVO})
        self.assertEqual(saida, 0, 'o comando devolveu codigo de falha')

    def test_16_sem_credencial_o_comando_nao_gasta(self):
        import apify_pool as ap
        import test_c10_8b_rota_paga_canonica as T
        f = T._Falsa(texto=T._texto_real())
        antes = ap.pool
        ap.pool = lambda env=None: []
        try:
            with T._Cenario(f, com_chave=False):
                with __import__("autorizacao_de_gasto").autorizacao(_ensaio_pago()):
                    ss.coletar(FASE, banco=None)
        finally:
            ap.pool = antes
        self.assertEqual(f.posts, [], 'o comando comprou sem credencial')


class ORegistoQueVoltaAoRepositorio(unittest.TestCase):
    """O bruto fica na máquina. O que volta é o registo, e ele diz isso."""

    def _correr(self):
        import test_c10_8b_rota_paga_canonica as T
        f = T._Falsa(texto=T._texto_real())
        with T._Cenario(f):
            with __import__("autorizacao_de_gasto").autorizacao(_ensaio_pago()):
                ss.coletar(FASE, banco=None)
        with io.open(os.path.join(ss.GAVETA_PAGA, '%s.json' % FASE),
                     encoding='utf-8') as fh:
            return json.load(fh), f

    def test_19_o_registo_distingue_os_tres_estados_do_bruto(self):
        d, _f = self._correr()
        self.assertEqual(d['SCRAP_RAW_CAPTURED_ON_RUNNER'], 'PRESERVED')
        self.assertEqual(d['SCRAP_RAW_RETURNED_TO_REPO'], 'NO')
        self.assertEqual(d['CANONICAL_FORWARD_PRESERVATION'], 'NO')
        self.assertTrue(d['SCRAP_RAW_WHY_NOT_RETURNED'])

    def test_20_o_bruto_e_relido_e_o_sha_bate(self):
        d, _f = self._correr()
        self.assertEqual(d['SCRAP_RAW_READ_BACK'], 'YES')
        self.assertGreater(d['SCRAP_RAW_BYTES'], 0)
        self.assertEqual(d['SCRAP_RAW_SHA256'], d['SCRAP_RAW_SHA256_READ_BACK'])

    def test_20b_a_forma_do_bruto_viaja_mesmo_que_os_bytes_nao(self):
        """Os bytes morrem no `git clean` do checkout seguinte. A forma não.

            RAW CAPTURADO NO PROCESSO != RAW QUE SOBREVIVE AO JOB.
        """
        d, _f = self._correr()
        forma = d['SCRAP_RAW_ITEM_SHAPE']
        self.assertTrue(forma, 'o registo deixou de guardar a forma do bruto')
        chaves = sorted(forma[0])
        self.assertEqual(chaves, ['chars', 'transcript', 'url'])
        for k in chaves:
            self.assertIn('TIPO', forma[0][k])
            self.assertIn('VAZIO', forma[0][k])

    def test_21_o_registo_nao_leva_credencial(self):
        d, _f = self._correr()
        texto = json.dumps(d, ensure_ascii=False)
        self.assertNotIn('apify_api_', texto)
        self.assertNotIn('TOKEN_DE_MENTIRA', texto)

    def test_22_o_custo_lido_nao_se_publica_como_liquidado(self):
        d, _f = self._correr()
        self.assertEqual(d['COST_STATE'], 'READ_NOT_SETTLED')
        self.assertEqual(d['SETTLED_COST_USD'], 'UNKNOWN')

    def test_23_a_reserva_nomeia_o_que_carrega(self):
        d, _f = self._correr()
        t = d['FINANCIAL_ATTEMPTS'][0]
        self.assertEqual(t['ROUTE'], 'apify:transcricao',
                         'o campo ROTA da reserva voltou a levar outra coisa')
        self.assertIn('MISSAO', t)
        self.assertNotIn('MOTIVO_PAGO', t,
                         'a reserva voltou a chamar missao de motivo pago')
        self.assertEqual(d['MOTIVO_PAGO'], 'ROUTE_NOT_ALLOWED')

    def test_24_a_especie_e_o_alvo_ficam_no_registo(self):
        d, _f = self._correr()
        it = d['ITEMS'][0]
        self.assertEqual(it['NATIVE_ID'], ALVO)
        self.assertEqual(it['SPECIES'], 'NOT_DECLARED_BY_PROVIDER')
        self.assertIs(it['TIMESTAMPS'], False)
        self.assertIn(it['LANGUAGE'], ('UNKNOWN', 'NÃO SEI', 'NAO SEI'))


class OSegredoNaoSaiDaquiEmCasoNENHUM(unittest.TestCase):

    def test_25_o_registo_recusa_escrever_credencial(self):
        """A trava é uma TRAVA, e não a esperança de que nada a tenha posto lá.

            UMA TRAVA QUE NUNCA FOI TESTADA É UMA LINHA, NÃO UMA TRAVA.
        """
        # O campo tem de ser um dos que o registo COPIA. A primeira versão
        # deste teste envenenou `ROUTER_RECORD.ERRO`, que o registo nem lê — e
        # a trava não disparou porque não havia o que apanhar.
        #
        #     ENVENENAR O QUE NINGUÉM COPIA NÃO TESTA QUEM COPIA.
        envenenado = {'RESULT': 'OK',
                      'ROUTE': 'apify:transcricao?token=apify_api_SEGREDO',
                      'ROUTER_RECORD': {'MEDIDA': {}}}
        # Gaveta limpa só para este caso: outros testes deste módulo já
        # escreveram o registo, e medir a existência do ficheiro deles provaria
        # o contrário do que se quer.
        import shutil
        import tempfile
        antes, ss.GAVETA_PAGA = ss.GAVETA_PAGA, tempfile.mkdtemp(prefix='t-veneno-')
        try:
            with self.assertRaises(RuntimeError) as e:
                ss._registar_fase_paga(FASE, ss.FASES_PAGAS[FASE], 'run-teste',
                                       [], envenenado)
            self.assertIn('credencial', str(e.exception))
            self.assertEqual(os.listdir(ss.GAVETA_PAGA), [],
                             'o registo envenenado chegou a ser escrito')
        finally:
            shutil.rmtree(ss.GAVETA_PAGA, ignore_errors=True)
            ss.GAVETA_PAGA = antes


class OQueOComandoPublica(unittest.TestCase):

    def test_17_o_comando_nunca_imprime_a_chave(self):
        fonte = _fonte('coleta/social_scrap.py')
        arv = ast.parse(fonte)
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'coletar')
        texto = ast.get_source_segment(fonte, fn) or ''
        for proibido in ('apify_pool', 'APIFY_TOKEN', 'token', 'pool()'):
            self.assertNotIn(proibido, texto,
                             'a CLI passou a tocar na credencial: %s' % proibido)

    def test_18_a_impressao_nao_e_o_portao(self):
        fonte = _fonte('coleta/social_scrap.py')
        arv = ast.parse(fonte)
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'coletar')
        # nenhum `return` entre o CHECK impresso e a chamada ao COLLECT: quem
        # recusa e o CHECK de dentro do COLLECT, e nao esta funcao.
        texto = ast.get_source_segment(fonte, fn) or ''
        antes, _, depois = texto.partition("READY_TO_SPEND")
        self.assertIn('scrap.COLLECT', depois,
                      'a CLI passou a decidir em vez de imprimir')
        self.assertNotIn('return', depois.split('scrap.COLLECT')[0],
                         'nasceu um segundo portao na CLI')


if __name__ == '__main__':
    unittest.main(verbosity=2)
