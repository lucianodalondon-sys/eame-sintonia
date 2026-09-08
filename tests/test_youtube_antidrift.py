#!/usr/bin/env python3
"""
ANTI-DRIFT — as travas que impedem os defeitos JÁ COMETIDOS de voltarem.

Cada teste aqui existe porque a coisa que ele proíbe aconteceu de verdade nesta
casa. Não são hipóteses: são cicatrizes.
"""
import io
import os
import re
import sys
import unittest
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import falhas                     # noqa: E402
import social_matriz as mz        # noqa: E402
import youtube_oficial as yt      # noqa: E402

FALSA = '-'.join(['CHAVE', 'DE', 'TESTE'])


def _t(*r):
    fila = list(r)

    def f(url):
        x = fila.pop(0) if fila else {'items': []}
        if isinstance(x, BaseException):
            raise x
        return x
    return f


class TestUmDonoDaQuota(unittest.TestCase):
    """A matriz sabia o modelo certo e o executor mantinha outro numero."""

    def test_o_executor_nao_declara_quota_propria(self):
        """`QUOTA` do adaptador tem de ser a matriz LIDA, nao uma segunda tabela."""
        self.assertEqual(yt.QUOTA, mz.QUOTA_METODO['YOUTUBE'])
        self.assertEqual(yt.LIMITE_PADRAO, mz.LIMITE_PADRAO_PROJETO['YOUTUBE'])
        self.assertEqual(yt.QUOTA_MODEL_VERSION, mz.QUOTA_MODEL_VERSION)

    def test_a_chamada_pergunta_ao_dono_na_hora(self):
        """Nao basta o espelho bater no import: a decisao que gasta consulta a matriz."""
        original = dict(mz.QUOTA_METODO['YOUTUBE'])
        try:
            mz.QUOTA_METODO['YOUTUBE']['videos.list'] = ('SEARCH', 7)
            s = yt.Sessao(**{'api_key': FALSA}, teto_search=99, teto_geral=99,
                          transporte=_t({'items': []}))
            s.chamar('videos.list', {'id': 'x'})
            self.assertEqual(s.usado[yt.SEARCH], 7,
                             'o executor ignorou a matriz e usou tabela propria')
        finally:
            mz.QUOTA_METODO['YOUTUBE'] = original

    def test_search_nunca_volta_a_custar_100_unidades_gerais(self):
        bucket, custo = mz.quota_de('YOUTUBE', 'search.list')
        self.assertEqual(bucket, 'SEARCH')
        self.assertEqual(custo, 1)

    def test_metodo_sem_regra_nao_pode_ser_chamado(self):
        with self.assertRaises(KeyError):
            mz.quota_de('YOUTUBE', 'videos.insert')

    def test_nenhuma_fonte_declara_100_unidades_como_custo_atual(self):
        """Varre codigo e docs. Narrativa historica e permitida; declaracao nao."""
        alvos = []
        for base in ('leis', 'coleta', 'guarda', 'ferramentas', 'docs'):
            for raiz, _d, arqs in os.walk(os.path.join(ROOT, base)):
                if '__pycache__' in raiz:
                    continue
                for a in arqs:
                    if a.endswith(('.py', '.md')):
                        alvos.append(os.path.join(raiz, a))
        # A frase proibida e a que AFIRMA no presente. "a versao anterior dizia X"
        # continua valendo — apagar a memoria do erro nao e consertar o erro.
        proibido = re.compile(
            r'(?i)search\.list[^.\n]{0,40}(custa|cost[a]?|=)\s*100\s*(unidade|unit)')
        ruins = []
        for f in alvos:
            txt = io.open(f, encoding='utf-8', errors='replace').read()
            for m in proibido.finditer(txt):
                trecho = txt[max(0, m.start() - 120):m.start()]
                # A marca do texto HISTORICO e o passado: "declarava", "mantinha",
                # "a versao anterior". Um texto que volte a DECLARAR o modelo velho
                # estaria no presente, e nao casa com nenhum destes.
                if any(p in trecho.lower() for p in
                       ('versão anterior', 'versao anterior', 'estava desatualizado',
                        'a primeira versão', 'a primeira versao', 'declarava',
                        'mantinha', 'já dizia', 'ja dizia', 'proibid', 'e dizia')):
                    continue
                ruins.append((os.path.relpath(f, ROOT), m.group(0)[:60]))
        self.assertEqual(ruins, [], 'modelo antigo de quota declarado como atual: %s'
                         % ruins)


class TestUCUUNuncaViraOficial(unittest.TestCase):
    """FALHA DA ROTA OFICIAL NAO TRANSFORMA HEURISTICA EM FATO."""

    def _sessao_que_falha(self, exc):
        return yt.Sessao(**{'api_key': FALSA}, transporte=_t(exc))

    def test_1_sucesso_e_OFICIAL(self):
        s = yt.Sessao(**{'api_key': FALSA}, transporte=_t(
            {'items': [{'contentDetails': {'relatedPlaylists': {'uploads': 'UUof'}}}]}))
        pl, proc = yt.uploads_playlist(channel_id='UCabc', sessao=s)
        self.assertEqual(pl, 'UUof')
        self.assertEqual(proc['PROVENANCE'], yt.OFICIAL)

    def test_2_canal_inexistente_nao_vira_palpite(self):
        s = yt.Sessao(**{'api_key': FALSA}, transporte=_t({'items': []}))
        with self.assertRaises(yt.CanalNaoEncontrado):
            yt.uploads_playlist(channel_id='UCsumiu', sessao=s)

    def test_3_timeout_nao_vira_palpite(self):
        with self.assertRaises(urllib.error.URLError):
            yt.uploads_playlist(channel_id='UCabc',
                                sessao=self._sessao_que_falha(
                                    urllib.error.URLError('timeout')))

    def test_4_parser_drift_nao_vira_palpite(self):
        s = yt.Sessao(**{'api_key': FALSA},
                      transporte=_t({'items': [{'contentDetails': 'ISTO E STRING'}]}))
        with self.assertRaises((AttributeError, TypeError)):
            yt.uploads_playlist(channel_id='UCabc', sessao=s)

    def test_5_quota_estourada_nao_vira_palpite(self):
        s = yt.Sessao(**{'api_key': FALSA}, teto_geral=0, transporte=_t({'items': []}))
        with self.assertRaises(yt.TetoDaExecucao):
            yt.uploads_playlist(channel_id='UCabc', sessao=s)

    def test_6_credencial_ausente_nao_vira_palpite(self):
        s = yt.Sessao(**{'api_key': None}, transporte=_t({'items': []}))
        with self.assertRaises(yt.SemCredencial):
            yt.uploads_playlist(channel_id='UCabc', sessao=s)

    def test_7_hint_explicito_continua_marcado_como_hint(self):
        pl, proc = yt.uploads_hint(
            channel_id='UCabc',
            porque='levantamento exploratorio descartavel que nao entra no acervo')
        self.assertEqual(pl, 'UUabc')
        self.assertEqual(proc['PROVENANCE'], yt.DERIVED_HINT)
        self.assertIn('WHY_DERIVED_HINT_USED', proc)
        self.assertNotEqual(proc['PROVENANCE'], yt.OFICIAL)

    def test_7b_api_falhou_nao_e_justificativa(self):
        for desculpa in ('a API falhou', 'timeout', 'channels.list falhou',
                         'deu erro na api oficial e eu precisava do id'):
            with self.assertRaises(ValueError, msg=desculpa):
                yt.uploads_hint(channel_id='UCabc', porque=desculpa)

    def test_8_oficial_vence_o_derivado_quando_divergem(self):
        s = yt.Sessao(**{'api_key': FALSA}, transporte=_t(
            {'items': [{'contentDetails':
                        {'relatedPlaylists': {'uploads': 'UU_DIFERENTE'}}}]}))
        pl, _ = yt.uploads_playlist(channel_id='UCabc', sessao=s)
        self.assertNotEqual(pl, yt.uploads_derivado('UCabc'))
        self.assertEqual(pl, 'UU_DIFERENTE')

    def test_nao_existe_caminho_automatico_para_o_palpite(self):
        import inspect
        self.assertNotIn('permitir_derivado',
                         inspect.signature(yt.uploads_playlist).parameters)
        self.assertNotIn('permitir_derivado',
                         inspect.signature(yt.uploads_recentes).parameters)

    def test_palpite_nao_sobrevive_a_execucao(self):
        """Nao ha onde um palpite dormir: o cache morre com o processo."""
        self.assertEqual(yt.cache_da_execucao(), {})
        self.assertFalse(hasattr(yt, 'cache_de_playlists'),
                         'voltou um cache duravel de playlists')


class TestCheckpointTemUmDono(unittest.TestCase):
    """REUTILIZAR UMA FUNCAO DO CHECKPOINT CANONICO
    NAO E REUTILIZAR O CHECKPOINT CANONICO."""

    def test_identidade_obedece_a_lei_canonica(self):
        import coleta_checkpoint as cc
        ok, ruins = cc.identidade_valida(yt.CAMPOS_DA_IDENTIDADE)
        self.assertTrue(ok, 'identidade com campo proibido: %s' % ruins)
        for proibido in ('TOKEN', 'RUN_ID', 'DATASET_ID', 'CAPTURED_AT'):
            self.assertNotIn(proibido, yt.CAMPOS_DA_IDENTIDADE)

    def test_identidade_e_estavel_entre_execucoes(self):
        self.assertEqual(yt._identidade('UCabc'), yt._identidade('UCabc'))
        self.assertNotEqual(yt._identidade('UCabc'), yt._identidade('UCdef'))

    def test_sem_DSN_o_checkpoint_e_declarado_NOT_LIVE(self):
        estado, banco = yt.checkpoint_disponivel(env_={})
        self.assertEqual(estado, yt.CHECKPOINT_NOT_LIVE)
        self.assertIsNone(banco, 'inventou um banco que nao existe')

    def test_com_DSN_o_dono_e_o_canonico(self):
        import coleta_checkpoint as cc
        estado, banco = yt.checkpoint_disponivel(
            env_={yt.ENV_DSN: 'postgresql://exemplo/nao-conectado'})
        self.assertEqual(estado, yt.CHECKPOINT_LIVE)
        self.assertIsInstance(banco, cc.Banco,
                              'a durabilidade tem de ser do dono canonico')

    def test_o_modulo_nao_tem_MAIS_um_checkpoint_proprio(self):
        """A regressao concreta: gravar estado duravel em JSON ao lado do dono."""
        for proibido in ('checkpoint_ler', 'checkpoint_gravar', 'checkpoint_atualizar',
                         'ARQUIVO_CHECKPOINT', 'YOUTUBE-CHECKPOINT'):
            self.assertFalse(hasattr(yt, proibido),
                             '%s voltou: segundo dono duravel' % proibido)
        # A narrativa que EXPLICA o defeito removido continua permitida — apagar
        # a memoria do erro nao e consertar o erro. O que se proibe e o ATO:
        # gravar ou ler um estado duravel proprio.
        txt = io.open(os.path.join(ROOT, 'coleta', 'youtube_oficial.py'),
                      encoding='utf-8').read()
        for ato in ("env.gravar('YOUTUBE-CHECKPOINT", "env.ler('YOUTUBE-CHECKPOINT",
                    "env.gravar(ARQUIVO_CHECKPOINT", "env.ler(ARQUIVO_CHECKPOINT"):
            self.assertNotIn(ato, txt, 'o modulo voltou a ser dono duravel: %s' % ato)


class TestGitNaoEBancoOperacional(unittest.TestCase):
    """A trava bloqueadora: nada em data/samples/SOCIAL-IT decide a proxima coleta."""

    def test_nenhum_ficheiro_de_SOCIAL_IT_e_autoridade_de_checkpoint(self):
        alvo = os.path.join('data', 'samples', 'SOCIAL-IT')
        suspeitos = []
        for base in ('coleta', 'leis', 'guarda', 'ferramentas'):
            d = os.path.join(ROOT, base)
            if not os.path.isdir(d):
                continue
            for raiz, _sub, arqs in os.walk(d):
                if '__pycache__' in raiz:
                    continue
                for a in arqs:
                    if not a.endswith('.py'):
                        continue
                    caminho = os.path.join(raiz, a)
                    txt = io.open(caminho, encoding='utf-8', errors='replace').read()
                    # Ler amostra e permitido. LER PARA DECIDIR O QUE COLETAR nao e.
                    # Por isso a busca e pelo ATO — uma chamada que grava ou le um
                    # ficheiro de checkpoint —, nunca pela palavra num comentario.
                    for ato in ('env.gravar(ARQUIVO_CHECKPOINT',
                                'env.ler(ARQUIVO_CHECKPOINT',
                                "env.gravar('YOUTUBE-CHECKPOINT",
                                "env.ler('YOUTUBE-CHECKPOINT",
                                "gravar('CHECKPOINT", "ler('CHECKPOINT"):
                        if ato in txt:
                            suspeitos.append(os.path.relpath(caminho, ROOT))
        self.assertEqual(sorted(set(suspeitos)), [],
                         'ficheiro do Git usado como autoridade de checkpoint: %s'
                         % sorted(set(suspeitos)))

    def test_o_workflow_nao_commita_checkpoint(self):
        wf = os.path.join(ROOT, '.github', 'workflows', 'scrap-social.yml')
        txt = io.open(wf, encoding='utf-8').read()
        # So linhas EXECUTAVEIS contam. O comentario que explica o defeito
        # removido cita a frase proibida de proposito — apagar a memoria do erro
        # nao e consertar o erro.
        executaveis = [l for l in txt.splitlines() if not l.strip().startswith('#')]
        ofensivas = [l.strip() for l in executaveis if 'git add -A data/samples' in l]
        self.assertEqual(ofensivas, [],
                         'o workflow voltou a commitar a pasta inteira: `-A` leva o '
                         'que alguem puser la amanha, e e assim que checkpoint volta')
        # E tem de existir a trava de EXECUCAO, nao so a de texto.
        self.assertIn('RECUSADO: checkpoint no indice', txt,
                      'o workflow nao recusa checkpoint no indice em tempo de corrida')


class TestCacheNaoSeDescreveComoPersistente(unittest.TestCase):
    def test_o_modulo_diz_a_diferenca(self):
        txt = io.open(os.path.join(ROOT, 'coleta', 'youtube_oficial.py'),
                      encoding='utf-8').read()
        self.assertIn('CACHE EM RAM NÃO É CHECKPOINT PERSISTENTE', txt)


class TestCommentsDisabledNuncaVoltaAZero(unittest.TestCase):
    def test_o_mapa_de_razoes_nao_regride(self):
        self.assertEqual(yt.RAZOES['commentsDisabled'], 'FEATURE_DISABLED')

    def test_os_tres_estados_continuam_distintos(self):
        tres = {falhas.traduzir('FEATURE_DISABLED'),
                falhas.traduzir('ZERO_RESULTS'),
                falhas.traduzir('NOT_APPLICABLE')}
        self.assertEqual(len(tres), 3)


if __name__ == '__main__':
    unittest.main(verbosity=1)
