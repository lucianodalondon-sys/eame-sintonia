# -*- coding: utf-8 -*-
"""SCRAP-RC-01 — a Release Candidate V1 do SINTONIA SCRAP, atacada.

    SUPPORTED != TODO O MUNDO. READY != TODAS AS CAPACIDADES EXISTEM.
    FAIL_CLOSED É UM ESTADO VÁLIDO.
    LEGACY EXISTS != ACTIVE V1 ENTRYPOINT.

O que NÃO pode existir: uma capacidade que diz BLOCKED e um fallback escondido
que executa.
"""
import atexit
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('provas', 'orquestrador', 'pedido', 'coleta', 'leis', 'regras',
           'ferramentas', 'medidas', 'guarda', 'tests', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

# ⚠️ O BANCO ABRE ANTES DO MUNDO FALSO: `_rc01_mundo_falso` lê `RC01_MARCA` no
# momento em que é importado, e uma bateria que escreve no acervo mede o que
# ela própria pôs lá.
BANCO = tempfile.mkdtemp(prefix='rc01-bateria-')
atexit.register(shutil.rmtree, BANCO, True)
os.environ['RC01_MARCA'] = BANCO

import _rc01_mundo_falso as mundo                                 # noqa: E402
import entradas_do_scrap_v1 as ent                                # noqa: E402
import pedido as pd                                               # noqa: E402
import receitas as rec                                            # noqa: E402
import relevancia_da_fonte as rl                                  # noqa: E402
import retorno_da_coleta as rc                                    # noqa: E402
import scrap_capacidades as cap                                   # noqa: E402
import scrap_colheita as sc                                       # noqa: E402
import scrap_executor as sx                                       # noqa: E402
import social_envelope as envelope                                # noqa: E402
import superficie_do_scrap_v1 as sup                              # noqa: E402

mundo.instalar()


def pinar_o_banco():
    """Aponta o bruto para o banco desta bateria, AGORA.

    ⚠️ E chama-se ANTES DE CADA CORRIDA, e não uma vez no topo do módulo.
    Medido na suíte inteira: `social_envelope.RAW_DIR` é uma variável de
    módulo, outra bateria reaponta-a para o acervo verdadeiro, e a partir daí
    esta escreve lá — uma observação FABRICADA, com handle inventado, dentro de
    `data/samples/`.

        UM REDIRECIONAMENTO FEITO NO IMPORT VALE ATÉ ALGUÉM IMPORTAR OUTRA COISA.
    """
    envelope.RAW_DIR = os.path.join(BANCO, 'raw-free')
    os.environ['RC01_MARCA'] = BANCO
    mundo.MARCA = BANCO
    mundo.IDAS = os.path.join(BANCO, 'IDAS-AO-MUNDO.json')
    mundo.instalar()


pinar_o_banco()

WORKFLOW = '.github/workflows/sintonia-scrap.yml'
FASE = 'canario-bluesky'
CAPACIDADE = 'bluesky.author.incremental'
FONTE = 'IT-T9-001'
HANDLE = mundo.FEED['feed'][0]['post']['author']['handle']


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _sem_comentarios(texto):
    return '\n'.join(re.sub(r'(?<!\$)#.*$', '', l) for l in texto.splitlines())


def _receita():
    p = pd.de_uma_frase('colete concorrentes')
    p.filtros.update({'fase': FASE, 'fonte': FONTE, 'handle': HANDLE})
    return rec.resolver(p).executores[0]


# ══════════════════════════════════════════════════════════════════════════
# RT1–RT6 · A SUPERFÍCIE V1 É MEDIDA NO RUNTIME, NÃO ESCRITA À MÃO
# ══════════════════════════════════════════════════════════════════════════
class ASuperficieEMedida(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.linhas = sup.medir()

    def test_rt01_toda_capacidade_declarada_aparece(self):
        """Uma superfície que esquece uma capacidade esconde-a."""
        self.assertEqual(len(self.linhas), len(cap.DECLARADAS))

    def test_rt02_nenhuma_READY_sem_aresta(self):
        """CAPABILITY DECLARADA != ARESTA EXISTE."""
        sem = [l['CAPABILITY'] for l in self.linhas
               if l['V1'] == sup.READY and not l['EDGE_EXISTS']]
        self.assertEqual(sem, [], 'READY sem adaptador registado: %s' % sem)

    def test_rt03_UNKNOWN_nao_vira_BLOCKED(self):
        """NÃO TRANSFORMAR UNKNOWN EM BLOCKED."""
        for l in self.linhas:
            if l['DECLARED_STATE'] == cap.UNKNOWN:
                self.assertNotEqual(l['V1'], sup.READY, l['CAPABILITY'])

    def test_rt04_os_estados_sao_os_cinco_da_missao(self):
        """⚠️ AS CINCO PALAVRAS ESTÃO AQUI EM LITERAL, E NÃO EM `sup.READY`.

        A primeira versão comparava contra as constantes do próprio módulo —
        e então trocar o VALOR de `READY` para outra palavra qualquer deixava
        a sentinela verde, porque os dois lados mudavam juntos.

            MEDIR A LEI CONTRA A PRÓPRIA LEI É MEDIR UMA TAUTOLOGIA.
        """
        estados = {l['V1'] for l in self.linhas}
        self.assertTrue(estados <= {'READY', 'READY_PENDING_CREDENTIAL',
                                    'FAIL_CLOSED', 'NOT_IN_V1', 'UNKNOWN'},
                        estados)
        self.assertIn('READY', estados)

    def test_rt05_a_lista_de_plataformas_e_derivada(self):
        """UMA SUPERFÍCIE ESCRITA À MÃO É A MEMÓRIA DE QUEM A ESCREVEU."""
        codigo = _fonte('provas/superficie_do_scrap_v1.py')
        self.assertIn('def plataformas_v1', codigo)
        self.assertNotIn('PLATAFORMAS_V1 = (', codigo)

    def test_rt06_o_canario_esta_READY(self):
        linha = [l for l in self.linhas if l['CAPABILITY'] == CAPACIDADE][0]
        self.assertEqual(linha['V1'], sup.READY)
        self.assertEqual(linha['DECLARED_STATE'], 'PROVEN')


class OPortaoRecusaPeloMotivoCerto(unittest.TestCase):
    """Um portão que recusa pelo motivo errado recusa hoje e engana amanhã."""

    def test_rt33_capacidade_nao_declarada_diz_que_nao_e_declarada(self):
        """UNKNOWN NÃO VIRA SUCESSO — e também não vira outra razão."""
        pronto = sx.CHECK('BLUESKY', 'bluesky.nao.existe')
        self.assertFalse(pronto['CAN'])
        self.assertEqual(pronto['STATE'], 'CAPABILITY_NOT_DECLARED')
        self.assertEqual(pronto['CAPABILITY_STATE'], cap.UNKNOWN)

    def test_rt34_estado_que_nao_promete_nao_colhe_em_normal(self):
        """DECLARADA != PROVADA. Ter adaptador não a torna sucesso."""
        pronto = sx.CHECK('MASTODON', 'mastodon.account.incremental')
        self.assertFalse(pronto['CAN'])
        self.assertEqual(pronto['STATE'], 'CAPABILITY_STATE_PROMISES_NOTHING')

    def test_rt35_declarada_sem_rota_nao_pode_correr(self):
        """CAPABILITY DECLARADA != ARESTA EXISTE."""
        pronto = sx.CHECK('LINKEDIN', 'linkedin.recent.discovery')
        self.assertFalse(pronto['CAN'])
        self.assertEqual(pronto['STATE'], 'DECLARED_WITHOUT_ROUTE')

    def test_rt36_o_portao_nao_promove_o_estado_da_capacidade(self):
        """TRIAL PASSADO != CAPACIDADE PROVADA."""
        pinar_o_banco()
        _o, trace = sx.COLLECT(platform='MASTODON',
                               capability='mastodon.account.incremental',
                               run_id='RC01-RT36', instancia='x', conta='y',
                               limit=1)
        self.assertEqual(trace['CAPABILITY_STATE_AFTER'],
                         cap.estado('mastodon.account.incremental'))
        self.assertNotEqual(trace['CAPABILITY_STATE_AFTER'], 'PROVEN')

    def test_rt37_rota_nao_permitida_nunca_e_a_rota_padrao(self):
        """A política escolhe a rota. PERMITIDA -> BARATA -> CAPAZ."""
        import social_matriz as mz
        for plat, caps in mz.MATRIZ.items():
            for capg, rotas in caps.items():
                if capg.startswith('_') or not isinstance(rotas, list):
                    continue
                escolhida = mz._rota_padrao(rotas)
                if escolhida is None:
                    continue
                self.assertIn(escolhida['PERMITIDA'], ('SIM', 'CONDICIONAL'),
                              '%s/%s escolheu %s' % (plat, capg,
                                                     escolhida['ROTA']))


class AAutorizacaoSoNasceDoDono(unittest.TestCase):

    def test_rt38_autorizacao_escrita_a_mao_nao_nasce(self):
        """CAMPO PREENCHIDO PELO CHAMADOR != AUTORIZAÇÃO."""
        import autorizacao_de_gasto as az
        with self.assertRaises(az.AutorizacaoInvalida):
            az.Autorizacao(motivo=az.COLETA_NORMAL, proposito='T9',
                           source_id=FONTE, max_execucoes=9, max_usd=99.0,
                           quem_autorizou='EU', porque='porque sim',
                           condicao_de_paragem='nenhuma')

    def test_rt39_coleta_normal_sem_livro_nao_autoriza(self):
        """SEM O SIM DA RELEVÂNCIA, A COMPRA NORMAL NÃO NASCE."""
        import autorizacao_de_gasto as az
        with self.assertRaises(az.AutorizacaoInvalida):
            az.autorizar(motivo=az.COLETA_NORMAL, proposito='T9',
                         source_id=FONTE, max_execucoes=1, max_usd=0.10,
                         livro=[])

    def test_rt40_sem_fonte_provada_o_alvo_nao_vira_fonte(self):
        """HANDLE NÃO É SOURCE_ID — nem quando é a única coisa à mão."""
        pinar_o_banco()
        env = sc.colher(FASE, run_id='RC01-RT40', fonte=None, handle=HANDLE)
        self.assertEqual(env['COLHEITA'], [])
        self.assertTrue(env['PORQUE_ZERO_COLHEITA'])
        self.assertNotIn(HANDLE, json_do(env['SUPORTE']))


def json_do(x):
    import json as _j
    return _j.dumps(x, ensure_ascii=False, default=str)


# ══════════════════════════════════════════════════════════════════════════
# RT7–RT13 · O CANÁRIO ENTRA PELO CAMINHO CANÔNICO
# ══════════════════════════════════════════════════════════════════════════
class OCanarioEntraPelaPortaCerta(unittest.TestCase):

    def test_rt07_a_receita_serve_a_fase_do_canario(self):
        e = _receita()
        self.assertEqual(e['id'], 'scrap-colheita')
        self.assertIn(FASE, e['serve_fases'])

    def test_rt08_a_fase_existe_no_adapter(self):
        """UMA RECEITA QUE SERVE UMA FASE QUE NÃO EXISTE PROMETE O QUE NÃO TEM."""
        e = _receita()
        for fase in e['serve_fases']:
            self.assertIn(fase, sc.FASES, fase)

    def test_rt09_a_fase_do_canario_pede_a_capacidade_do_canario(self):
        self.assertEqual(sc.FASES[FASE][1], CAPACIDADE)

    def test_rt10_o_alvo_desce_como_filtro_nomeado(self):
        e = _receita()
        self.assertIn('handle', e['filtros_nomeados'])
        self.assertNotIn('handle', e['argumentos_de_filtros'])

    def test_rt11_o_handle_nao_e_a_fonte(self):
        """HANDLE NÃO É SOURCE_ID."""
        u = sc.unidade({'URL': 'https://bsky.app/profile/%s' % HANDLE},
                       run_id='R', fonte=FONTE)
        self.assertEqual(u['SOURCE_ID'], FONTE)
        self.assertNotIn(HANDLE, str(u['SOURCE_ID']))
        self.assertEqual(u['DOCUMENT_ID'], rc.NAO_SEI)

    def test_rt12_um_filtro_fora_da_lista_da_fase_recusa(self):
        """UM ARGUMENTO QUE A ROTA ENGOLE SEM USAR É UMA ARMADILHA."""
        codigo = sc.main(['--run-id=R', '--handle=x', '--teto=5', FASE, FONTE])
        self.assertEqual(codigo, 2)

    def test_rt13_sem_o_alvo_a_fase_do_canario_nao_comeca(self):
        codigo = sc.main(['--run-id=R', FASE, FONTE])
        self.assertEqual(codigo, 2)

    def test_rt14_o_disparador_do_canario_chama_o_orquestrador(self):
        """WORKFLOW É DISPARADOR. WORKFLOW NÃO É MOTOR."""
        y = _sem_comentarios(_fonte(WORKFLOW))
        ramo = y[y.index('%s)' % FASE):]
        ramo = ramo[:ramo.index(';;')]
        self.assertIn('orquestrador/orquestrador.py', ramo)
        for proibido in ('adaptador_', 'bsky', 'scrap_executor', 'COLLECT',
                         'social_scrap.py', 'public.api'):
            self.assertNotIn(proibido, ramo, proibido)


# ══════════════════════════════════════════════════════════════════════════
# RT15–RT20 · A RELEVÂNCIA GUARDA O GASTO, NÃO A OBSERVAÇÃO
# ══════════════════════════════════════════════════════════════════════════
class ARelevanciaGuardaOGasto(unittest.TestCase):

    def setUp(self):
        self.livro = rl.ler_livro(RAIZ)

    def _portao(self, **kw):
        kw.setdefault('custo', rl.CUSTO_DECLARADO_GRATUITO)
        kw.setdefault('acionamento', 'PONTUAL')
        kw.setdefault('escopo', 'PONTUAL')
        return rl.portao(FONTE, 'T9', self.livro, **kw)

    def test_rt15_gratis_e_pontual_nao_bloqueia(self):
        """O PORTÃO GUARDA O GASTO, NÃO A OBSERVAÇÃO. (COL-LAW-018)"""
        self.assertFalse(self._portao()['BLOQUEIA_A_CORRIDA'])

    def test_rt16_mas_continua_a_nao_autorizar_gasto(self):
        self.assertFalse(self._portao()['PODE_GASTAR'])

    def test_rt17_pago_bloqueia(self):
        self.assertTrue(self._portao(custo='pago')['BLOQUEIA_A_CORRIDA'])

    def test_rt18_agendado_bloqueia(self):
        """RECORRÊNCIA É FORMA DE GASTO."""
        self.assertTrue(self._portao(acionamento='AGENDADO')['BLOQUEIA_A_CORRIDA'])

    def test_rt19_escopo_total_bloqueia(self):
        self.assertTrue(self._portao(escopo='TOTAL')['BLOQUEIA_A_CORRIDA'])

    def test_rt20_o_livro_esta_vazio_e_diz_se(self):
        """NÃO FABRICAR SIM. O livro vazio é um facto, não um bug."""
        self.assertEqual(self.livro, [])


# ══════════════════════════════════════════════════════════════════════════
# RT21–RT25 · AS ENTRADAS DA V1, E O QUE ELAS ALCANÇAM
# ══════════════════════════════════════════════════════════════════════════
class AsEntradasDaV1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.desvios = {}
        cls.entradas = ent.medir(cls.desvios)

    def test_rt21_nenhum_bypass_ativo_na_v1(self):
        """ACTIVE_V1_BYPASSES = 0."""
        maus = [(e['WORKFLOW'], e['FASE']) for e in self.entradas
                if e['ESTADO'] == 'ACTIVE_V1_BYPASS']
        self.assertEqual(maus, [])

    def test_rt22_nenhum_fallback_escondido_na_v1(self):
        """ACTIVE_V1_HIDDEN_FALLBACKS = 0."""
        maus = [(e['WORKFLOW'], e['FASE']) for e in self.entradas
                if e['V1'] and not e['CANONICO']]
        self.assertEqual(maus, [])

    def test_rt23_ha_pelo_menos_uma_entrada_v1(self):
        """Uma release sem entrada nenhuma não é uma release."""
        self.assertTrue([e for e in self.entradas if e['V1']])

    def test_rt24_o_canario_e_uma_entrada_canonica(self):
        canario = [e for e in self.entradas if e['FASE'] == FASE]
        self.assertTrue(canario)
        self.assertEqual(canario[0]['ESTADO'], 'ACTIVE_V1_CANONICAL')

    def test_rt25_os_desvios_que_adquirem_estao_declarados(self):
        """UM DESVIO DECLARADO É UMA MEDIÇÃO. UM DESVIO CALADO É UM BURACO."""
        import social_scrap as ss
        self.assertTrue(ss.FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY)
        for ds in self.desvios.values():
            for porque in ds.values():
                self.assertTrue(str(porque).strip())

    def test_rt26_a_sonda_nao_le_a_prosa_do_yaml(self):
        """UMA SONDA QUE LÊ A PROSA CHAMA-LHE VIOLAÇÃO DA REGRA."""
        bruto = _fonte(WORKFLOW)
        self.assertIn('social_scrap.py', bruto)
        limpo = ent.sem_comentarios(bruto)
        ramo = limpo[limpo.index('%s)' % FASE):]
        self.assertNotIn('social_scrap.py', ramo[:ramo.index(';;')])


# ══════════════════════════════════════════════════════════════════════════
# RT27–RT31 · E A ROTA DO CANÁRIO CORRE MESMO — NÃO SÓ NA ÁRVORE
# ══════════════════════════════════════════════════════════════════════════
class OCanarioCorreMesmo(unittest.TestCase):
    """⚠️ AS SENTINELAS ACIMA LEEM A ÁRVORE, E A ÁRVORE NÃO SABE SE ANDA."""

    @classmethod
    def setUpClass(cls):
        pinar_o_banco()
        cls.objetos, cls.trace = sx.COLLECT(
            platform='BLUESKY', capability=CAPACIDADE,
            run_id='RC01-BATERIA', handle=HANDLE, limit=1)

    def test_rt27_a_rota_do_canario_devolve_objeto(self):
        self.assertEqual(len(self.objetos or []), 1)

    def test_rt28_e_o_portao_deixou_passar(self):
        self.assertTrue(self.trace['CHECK']['CAN'])
        self.assertEqual(self.trace['CHECK']['STATE'], 'CAN_COLLECT_NOW')

    def test_rt29_a_rota_e_gratuita_por_politica(self):
        """FREE_ROUTE_DOES_NOT_REQUIRE_SPEND_AUTH."""
        self.assertEqual(self.trace['COST_STATE'], 'FREE_ROUTE_BY_POLICY')
        self.assertFalse(self.trace['PAID_PROVIDER_USED'])
        self.assertEqual(self.trace['ACTUAL_COST_USD'], 0.0)

    def test_rt30_o_bruto_fica_no_disco_antes_de_normalizar(self):
        """RAW BEFORE NORMALIZATION."""
        raw = self.objetos[0]['RAW_REFERENCE']
        self.assertTrue(raw['SHA256'])
        self.assertTrue(os.path.isfile(os.path.join(RAIZ, raw['PATH'])))
        self.assertIn(BANCO, os.path.realpath(os.path.join(RAIZ, raw['PATH'])),
                      'o bruto desta bateria caiu fora do banco da prova')

    def test_rt31_e_ele_diz_que_ainda_nao_esta_preservado(self):
        """RAW_REFERENCE PARA ARQUIVO QUE SOME NÃO É PROVENIÊNCIA."""
        raw = self.objetos[0]['RAW_REFERENCE']
        self.assertEqual(raw['PRESERVATION'], 'NOT_PRESERVED')
        self.assertTrue(raw['PRESERVATION_OWNER'])

    def test_rt32_o_estado_da_capacidade_nao_se_promove_sozinho(self):
        """TRIAL PASSADO != CAPACIDADE PROVADA."""
        self.assertEqual(self.trace['CAPABILITY_STATE_BEFORE'],
                         self.trace['CAPABILITY_STATE_AFTER'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
