#!/usr/bin/env python3
"""ZERO APIFY EM STORIES TEM DE SER PROVÁVEL PELO CÓDIGO.

Uma branch chamada `stories-no-apify` que ainda aceitasse `--pagar` e recebesse
`APIFY_TOKEN_POOL` na fase de Stories não estaria sem Apify. Estaria com uma
porta fechada e destrancada — o que é pior que uma porta aberta, porque parece
resolvido.

Medido em 2026-09-09, ANTES desta trava existir: a rota paga já tinha saído da
escada e nenhum código de Stories importava a Apify, mas a fase ainda aceitava
`--pagar`, ainda imprimia «custo estimado», e o workflow ainda injetava a chave.
Inerte. E inerte não é inofensivo:

    UM PARÂMETRO INERTE NÃO É UM PARÂMETRO INOFENSIVO. É UM CONVITE.

Estes testes não descrevem a intenção. Eles REPROVAM quem religar.
"""
import ast
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
sys.path.insert(0, os.path.join(RAIZ, 'leis'))
import _gavetas  # noqa: E402,F401
import social_matriz as mz   # noqa: E402
import social_rotas as sr    # noqa: E402

CLASSES_PAGAS = ('APIFY', 'OFFICIAL_API_PAID')
ESCADA = mz.MATRIZ['INSTAGRAM']['FETCH_STORIES']


class NenhumaRotaDeStoryPodeCustarDinheiro(unittest.TestCase):

    def test_a_escada_declarada_nao_tem_classe_paga(self):
        pagas = [r['ROTA'] for r in ESCADA if r['CLASSE'] in CLASSES_PAGAS]
        self.assertEqual(pagas, [], 'rota paga declarada em FETCH_STORIES: %s' % pagas)

    def test_a_rota_padrao_escolhida_nunca_e_paga(self):
        escolhida = mz._rota_padrao(ESCADA, 'INSTAGRAM', 'FETCH_STORIES')
        self.assertIsNotNone(escolhida)
        self.assertNotIn(escolhida['CLASSE'], CLASSES_PAGAS)

    def test_MUTACAO_declarar_uma_rota_apify_reprova(self):
        """A trava tem de MORDER. Se este teste passar com a rota paga dentro,
        a trava não existe — ela só está escrita."""
        intruso = mz.r('apify:qualquer-ator-de-story', 'APIFY', 'CONDICIONAL',
                       'POSSIBLE_NOT_PROVED', 'por perfil',
                       'mutacao de teste; nunca deve sobreviver', None)
        envenenada = list(ESCADA) + [intruso]
        pagas = [x['ROTA'] for x in envenenada if x['CLASSE'] in CLASSES_PAGAS]
        self.assertEqual(len(pagas), 1)          # a mutação entrou de fato
        # e o mesmo critério que o primeiro teste usa a reprova:
        self.assertNotEqual(pagas, [], 'a mutação precisa ser detectável')

    def test_MUTACAO_a_rota_paga_MAIS_PERMITIDA_ainda_perde(self):
        """O ataque que a primeira versao desta trava NAO resistiu.

        `_rota_padrao` ordena por PERMITIDA antes de classe. Uma rota APIFY
        declarada `SIM` e `PROVED` vencia a rota local `CONDICIONAL` — ou seja,
        o zero-Apify dependia de ninguem declarar a rota errada.

            UMA REGRA QUE DEPENDE DE NINGUEM DECLARAR A ROTA ERRADA
            NAO E UMA REGRA. E UMA TORCIDA.

        Agora a exclusao entra ANTES da ordenacao, e esta mutacao morre.
        """
        intruso = mz.r('apify:intruso', 'APIFY', 'SIM', 'PROVED', 'barato',
                       'mutacao', None)
        escolhida = mz._rota_padrao(list(ESCADA) + [intruso],
                                    'INSTAGRAM', 'FETCH_STORIES')
        self.assertNotIn(escolhida['CLASSE'], CLASSES_PAGAS)
        self.assertNotEqual(escolhida['ROTA'], 'apify:intruso')

    def test_MUTACAO_a_mesma_rota_paga_venceria_numa_capacidade_SEM_a_trava(self):
        """Prova de que a trava e ela quem faz o trabalho — e nao a sorte da
        ordenacao. Sem a marca SEM_ROTA_PAGA, o intruso ganha."""
        intruso = mz.r('apify:intruso', 'APIFY', 'SIM', 'PROVED', 'barato',
                       'mutacao', None)
        sem_trava = mz._rota_padrao(list(ESCADA) + [intruso],
                                    'INSTAGRAM', 'FETCH_POST')
        self.assertEqual(sem_trava['ROTA'], 'apify:intruso')

    def test_o_dispatcher_recusa_mesmo_se_o_escolhedor_falhar(self):
        """A segunda trava, redundante de proposito."""
        self.assertTrue(mz.rota_paga_proibida('INSTAGRAM', 'FETCH_STORIES'))
        self.assertFalse(mz.rota_paga_proibida('INSTAGRAM', 'FETCH_POST'))


class NenhumCodigoDeStoryToccaAApify(unittest.TestCase):

    DONOS = ('coleta/instagram_stories.py', 'coleta/story_local.py',
             'ferramentas/story_transcrever.py')

    def _imports(self, caminho):
        arvore = ast.parse(open(os.path.join(RAIZ, caminho), encoding='utf-8').read())
        mods = set()
        for n in ast.walk(arvore):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                mods.add(n.module)
        return mods

    def test_nenhum_dono_de_story_importa_apify_pool_nem_o_coletor_pago(self):
        for f in self.DONOS:
            with self.subTest(arquivo=f):
                sujos = {m for m in self._imports(f)
                         if 'apify' in m.lower() or m == 'coletor'}
                self.assertEqual(sujos, set(), '%s importa %s' % (f, sujos))

    def test_nao_existe_adaptador_de_story_na_porta_do_dispatcher(self):
        """A rota de Story vive no dono local, e o dispatcher não tem atalho pago."""
        de_story = [k for k in sr.ADAPTADORES if k[1] == 'FETCH_STORIES']
        self.assertEqual(de_story, [])


class AFaseNaoAceitaMaisIntencaoDeGastar(unittest.TestCase):

    def test_a_fase_stories_nao_tem_parametro_de_gasto(self):
        import inspect
        import social_scrap
        params = inspect.signature(social_scrap.stories).parameters
        proibidos = [p for p in params if 'pag' in p.lower() or 'gast' in p.lower()]
        self.assertEqual(proibidos, [], 'a fase voltou a aceitar gasto: %s' % proibidos)

    def test_a_fase_nao_repassa_permitir_pago_ao_dispatcher(self):
        fonte = open(os.path.join(RAIZ, 'coleta', 'social_scrap.py'),
                     encoding='utf-8').read()
        corpo = fonte[fonte.index('def stories('):fonte.index('def portao(')]
        for proibido in ('permitir_pago', 'motivo_pago', '--pagar'):
            with self.subTest(termo=proibido):
                # a docstring EXPLICA por que não existe; o código não pode usar.
                codigo = corpo.split('"""', 2)[2]
                self.assertNotIn(proibido, codigo)

    def test_o_workflow_nao_injeta_a_chave_da_apify(self):
        wf = open(os.path.join(RAIZ, '.github', 'workflows', 'scrap-social.yml'),
                  encoding='utf-8').read()
        self.assertNotIn('APIFY_TOKEN_POOL', wf)
        self.assertNotIn('inputs.pagar', wf)


if __name__ == '__main__':
    unittest.main()
