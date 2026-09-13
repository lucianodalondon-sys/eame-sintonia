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

#: O `urlopen` verdadeiro, guardado ANTES de qualquer troca, e devolvido ao
#: lugar em `tearDownModule`.
#:
#: ⚠️ ESTA BATERIA INSTALAVA O FALSO NO IMPORT E NUNCA O TIRAVA. Medido na suíte
#: inteira: o carregador importa TODOS os módulos antes de correr o primeiro
#: teste, então o socket ficava falso para o processo todo — e uma bateria do
#: LinkedIn que levanta um servidor em `127.0.0.1`, para provar que um
#: redirecionamento pede licença outra vez, recebia `URLError` de um mundo falso
#: que nunca ouviu falar de `127.0.0.1`.
#:
#:     UM FALSO INSTALADO NO IMPORT VIVE ENQUANTO O PROCESSO VIVER.
#:     E O QUE ELE MEDE DEPOIS JÁ NÃO É O QUE ALGUÉM PEDIU PARA MEDIR.
_URLOPEN_VERDADEIRO = mundo.urllib.request.urlopen


def tearDownModule():
    """Devolve o mundo a quem vier a seguir."""
    mundo.urllib.request.urlopen = _URLOPEN_VERDADEIRO


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
        """CAPABILITY DECLARADA != ARESTA EXISTE.

        ⚠️ ERA `linkedin.recent.discovery`, E ELA MUDOU DE ESTADO. A
        LINKEDIN-OP-01 passou-a de `PROVEN` a `BLOCKED` — uma rota que funciona
        nao e uma rota permitida — e desde entao o `CHECK` recusa-a mais cedo,
        no portao epistemologico, sem chegar a perguntar pela rota. A sentinela
        media a mesma lei atraves de uma capacidade que deixou de a alcancar.

            UMA SONDA ANCORADA NUM ESTADO MEDE ATE O ESTADO MUDAR.

        `x.direct_post` esta `PROVEN` e continua sem rota ligada nesta
        linhagem: promete resultado, e portanto chega ao portao da rota.
        """
        pronto = sx.CHECK('X', 'x.direct_post')
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


class OLinkedInEntraSoPelaIdentidade(unittest.TestCase):
    """IDENTITY != CONTENT. E CATALOG != COLHEITA."""

    HTML = ('<html><body><a href="https://www.linkedin.com/company/exemplo-org/">'
            'LinkedIn</a></body></html>')

    def _envelope(self):
        import adaptador_linkedin as li
        import scrap_registo as reg
        pinar_o_banco()
        orig = li.identidade_pelo_site

        def com_html(**kw):
            kw.setdefault('transporte', lambda url, **k: self.HTML)
            return orig(**kw)

        reg.registar('LINKEDIN', 'linkedin.identity.discovery',
                     adaptador='adaptador_linkedin', rota=com_html)
        try:
            return sc.colher('identidade-linkedin', run_id='RC01-LI',
                             fonte=FONTE, site_url='https://exemplo.invalido/')
        finally:
            reg.registar('LINKEDIN', 'linkedin.identity.discovery',
                         adaptador='adaptador_linkedin', rota=orig)

    def test_rt41_a_fase_de_identidade_declara_CATALOG(self):
        """UMA ESPÉCIE POR OMISSÃO É UMA DECISÃO QUE NINGUÉM TOMOU."""
        self.assertEqual(sc.FASES['identidade-linkedin'][3], rc.CATALOG)
        for fase, linha in sc.FASES.items():
            self.assertEqual(len(linha), 4, fase)
            self.assertIn(linha[3], rc.ESPECIES, fase)

    def test_rt42_o_catalogo_nao_atravessa_o_ingresso(self):
        """ENTRAM_NO_INGRESSO = (COLHEITA,). Catálogo fica no envelope."""
        env = self._envelope()
        self.assertEqual(env['ESPECIE_DA_FASE'], rc.CATALOG)
        self.assertEqual(env['COLHEITA'], [])
        especies = {x.get('ESPECIE') for x in env['SUPORTE']}
        self.assertIn(rc.CATALOG, especies)
        self.assertNotIn(rc.CATALOG, rc.ENTRAM_NO_INGRESSO)

    def test_rt43_e_ele_respeita_o_contrato_de_retorno(self):
        self.assertEqual(rc.conferir(self._envelope(), RAIZ), [])

    def test_rt44_o_conteudo_do_linkedin_nao_corre(self):
        """UMA ROTA QUE FUNCIONA NÃO É UMA ROTA PERMITIDA."""
        for capacidade in ('linkedin.direct_post', 'linkedin.native_video',
                           'linkedin.native_caption', 'linkedin.recent.discovery'):
            pronto = sx.CHECK('LINKEDIN', capacidade)
            self.assertFalse(pronto['CAN'], capacidade)

    def test_rt44b_o_conteudo_do_linkedin_e_DECLARADO_bloqueado(self):
        """TECHNICALLY_PROVEN_HISTORY != CURRENT_ALLOWED_ROUTE.

        ⚠️ NASCEU DE UM MUTANTE QUE SOBREVIVEU. Pôr `linkedin.direct_post` de
        volta em `PROVEN` não fazia a máquina correr — o `CHECK` continuava a
        recusar, e a superfície continuava `FAIL_CLOSED`. O que mudava era o
        que a casa DIZ: que uma rota proibida pela política está provada.

            UMA ROTA QUE FUNCIONA NÃO É UMA ROTA PERMITIDA.
            E UM MUTANTE QUE SÓ MUDA O QUE A CASA DIZ AINDA MUDA ALGUMA COISA:
            MUDA AQUILO EM QUE A PRÓXIMA MISSÃO VAI ACREDITAR.

        A história técnica não se perde: ela vive no relatório da C11, com os
        372 posts e as datas. O que não fica é a promessa operacional.
        """
        for capacidade in ('linkedin.direct_post', 'linkedin.native_video',
                           'linkedin.native_caption', 'linkedin.recent.discovery'):
            self.assertEqual(cap.estado(capacidade), 'BLOCKED', capacidade)
            self.assertFalse(cap.promete_resultado(capacidade), capacidade)

    def test_rt45_nao_ha_fase_nenhuma_para_conteudo_do_linkedin(self):
        """A ausência da fase é a declaração."""
        for _p, capacidade, _f, _e in sc.FASES.values():
            self.assertNotIn(capacidade, ('linkedin.direct_post',
                                          'linkedin.native_video',
                                          'linkedin.native_caption',
                                          'linkedin.recent.discovery'))


class OLimiteHumanoEUmLimite(unittest.TestCase):
    """As propriedades que a SCRAP-CV-02 provou, medidas nesta árvore.

        LIMITE HUMANO != LEDGER OPERACIONAL. E UM NOME NÃO É UMA SOMA.
    """

    def _bater(self, aut, *, teto=0.10, orcamento=0.10, run='cv'):
        import coletor as ct
        import nenhuma_compra_sem_autorizacao as sr02
        import scrap_http as http
        import subprocess
        falsa = sr02.FalsaApify(sr02.itens_reais())
        real = subprocess.run
        subprocess.run = falsa
        try:
            with http.orcamento_de_rede(5), ct.orcamento_financeiro(orcamento):
                ct.executar(sr02.ATOR, {'videoUrl': 'https://youtu.be/X'},
                            token='F', run_id=run, platform='YOUTUBE',
                            country='IT', mission='RC01', query='X',
                            source_version='p', evidence_path='/dev/null',
                            wait=60, salvar_raw=False, autorizacao=aut,
                            teto_usd=teto)
            return len(falsa.posts), 'EXECUTOU'
        except Exception as e:                                    # noqa: BLE001
            return len(falsa.posts), getattr(e, 'causa', type(e).__name__)
        finally:
            subprocess.run = real

    def _autorizacao(self, **kw):
        import autorizacao_de_gasto as az
        import nenhuma_compra_sem_autorizacao as sr02
        import relevancia_da_fonte as rl
        kw.setdefault('max_execucoes', 1)
        kw.setdefault('max_usd', 0.10)
        return az.autorizar(motivo=az.COLETA_NORMAL, proposito=sr02.PROPOSITO,
                            source_id=sr02.FONTE,
                            livro=sr02.livro_com(rl.SIM), **kw)

    def test_rt50_o_orcamento_nao_pode_exceder_a_autorizacao(self):
        """FINANCIAL_BUDGET.AUTHORIZED <= AUTORIZACAO.MAX_USD."""
        posts, causa = self._bater(self._autorizacao(), orcamento=99.0,
                                   run='rt50')
        self.assertEqual(posts, 0)
        self.assertEqual(causa, 'ORCAMENTO_ACIMA_DA_AUTORIZACAO')

    def test_rt51_uma_autorizacao_vale_dentro_de_UM_ledger(self):
        """UM LIMITE CONFERIDO CONTRA UM LEDGER QUE MUDA NÃO FOI CONFERIDO."""
        aut = self._autorizacao(max_execucoes=2)
        p1, _ = self._bater(aut, run='rt51a')
        p2, causa = self._bater(aut, run='rt51b')
        self.assertEqual((p1, p2), (1, 0))
        self.assertEqual(causa, 'AUTORIZACAO_DE_OUTRO_LEDGER')

    def test_rt52_uma_autorizacao_concedida_nao_se_reescreve(self):
        """UMA AUTORIZAÇÃO QUE MUDA DEPOIS DE CONCEDIDA NÃO FOI CONFERIDA."""
        import autorizacao_de_gasto as az
        aut = self._autorizacao()
        for campo, valor in (('max_usd', 99.0), ('max_execucoes', 99),
                             ('source_id', 'OUTRA'), ('motivo', az.TRIAL_DE_CAPACIDADE)):
            with self.assertRaises(az.AutorizacaoSelada, msg=campo):
                setattr(aut, campo, valor)

    def test_rt53_uma_copia_nao_e_uma_autorizacao_nova(self):
        """COPIAR UMA AUTORIZAÇÃO NÃO É RECEBER UMA AUTORIZAÇÃO."""
        import copy
        import coletor as ct
        aut = self._autorizacao()
        orc = ct.OrcamentoFinanceiro(0.10)
        p1, _ = self._bater(aut, orcamento=orc, run='rt53a')
        p2, causa = self._bater(copy.copy(aut), orcamento=orc, run='rt53b')
        self.assertEqual((p1, p2), (1, 0))
        self.assertEqual(causa, 'AUTORIZACAO_ESGOTADA')

    def test_rt54_cada_ledger_tem_identidade_propria(self):
        """UMA IDENTIDADE QUE O ALOCADOR PODE REUTILIZAR NÃO É UMA IDENTIDADE."""
        import coletor as ct
        vistos = set()
        for _ in range(20):
            vistos.add(ct.OrcamentoFinanceiro(1.0).identidade)
        self.assertEqual(len(vistos), 20)


class OTetoDeItensDesce(unittest.TestCase):
    """MIGRAR UM CAMINHO É MUDAR POR ONDE ELE PASSA, NÃO O QUE ELE LEVA."""

    def _espiar(self, *args):
        import adaptador_instagram as ai
        import scrap_registo as reg
        pinar_o_banco()
        visto = {}
        orig = ai.janela

        def espia(**kw):
            visto.clear()
            visto.update(kw)
            return []

        reg.registar('INSTAGRAM', 'instagram.profile.discovery',
                     adaptador='adaptador_instagram', rota=espia)
        try:
            sc.main(list(args))
        finally:
            reg.registar('INSTAGRAM', 'instagram.profile.discovery',
                         adaptador='adaptador_instagram', rota=orig)
        return visto

    def test_rt55_o_teto_do_pedido_chega_a_rota(self):
        visto = self._espiar('--run-id=rt55', '--teto=5', 'janela-perfis', FONTE)
        self.assertEqual(str(visto.get('teto')), '5')

    def test_rt56_sem_teto_nada_de_teto(self):
        """Vazio = sem teto, e isso é um valor — não um cinco por omissão."""
        visto = self._espiar('--run-id=rt56', 'janela-perfis', FONTE)
        self.assertNotIn('teto', visto)

    def test_rt57_o_teto_e_filtro_nomeado_e_nao_um_terceiro_posicional(self):
        e = _receita()
        self.assertIn('teto', e['filtros_nomeados'])
        self.assertNotIn('teto', e['argumentos_de_filtros'])


class ODinheiroNaoAbreRotaProibida(unittest.TestCase):
    """SPEND_AUTHORIZATION != ROUTE_POLICY."""

    def test_rt46_a_matriz_responde_pelo_ator_proibido(self):
        import social_matriz as mz
        proibido, porque = mz.actor_proibido(
            'LINKEDIN', 'harvestapi~linkedin-profile-search-by-name')
        self.assertTrue(proibido)
        self.assertIn('PERMITIDA = NAO', porque)

    def test_rt47_um_ator_que_a_matriz_nao_nomeia_nao_e_proibido(self):
        """O SILÊNCIO DA MATRIZ NÃO PROÍBE, E TAMBÉM NÃO AUTORIZA."""
        import social_matriz as mz
        proibido, _ = mz.actor_proibido(
            'YOUTUBE', 'pintostudio~youtube-transcript-scraper')
        self.assertFalse(proibido)

    def test_rt48_a_porta_paga_recusa_a_rota_proibida(self):
        """ROUTE_NOT_ALLOWED + auth + budget + token = POST 0."""
        import coletor as ct
        import autorizacao_de_gasto as az
        import nenhuma_compra_sem_autorizacao as sr02
        import relevancia_da_fonte as rl
        import scrap_http as http
        import subprocess
        livro = [rl.Decisao(source_id=FONTE, proposito='T9', resultado=rl.SIM,
                            motivo='medido', metodo='PROVA',
                            evidencia={'file': 'x', 'line': 1}).para_livro()]
        aut = az.autorizar(motivo=az.COLETA_NORMAL, proposito='T9',
                           source_id=FONTE, max_execucoes=1, max_usd=0.50,
                           livro=livro)
        falsa = sr02.FalsaApify([])
        real = subprocess.run
        subprocess.run = falsa
        try:
            with self.assertRaises(ct.RotaNaoPermitida):
                with http.orcamento_de_rede(5), ct.orcamento_financeiro(0.50):
                    ct.executar('harvestapi~linkedin-profile-search-by-name',
                                {'firstName': 'x'}, token='apify_api_VALIDO',
                                run_id='rt48', platform='LINKEDIN', country='IT',
                                mission='RC01', query='q', source_version='p',
                                evidence_path='/dev/null', wait=60,
                                salvar_raw=False, autorizacao=aut, teto_usd=0.50)
        finally:
            subprocess.run = real
        self.assertEqual(falsa.posts, [])
        # E A AUTORIZAÇÃO NEM FOI TOCADA: a política parou antes do dinheiro.
        self.assertEqual(aut.gastas, 0)

    def test_rt49_a_recusa_de_politica_nao_se_veste_de_recusa_de_gasto(self):
        import autorizacao_de_gasto as az
        import coletor as ct
        self.assertFalse(issubclass(ct.RotaNaoPermitida, az.GastoRecusado))
        self.assertIn(ct.RotaNaoPermitida, ct._recusas_nossas())


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
                if e['ESTADO'] == ent.BYPASS]
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
        self.assertEqual(canario[0]['ESTADO'], ent.CANONICAL_V1)

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
        """TRIAL PASSADO != CAPACIDADE PROVADA.

        ⚠️ ESTA SENTINELA ERA CEGA, E FOI A MUTAÇÃO DA NIGHT-SHIFT-01 QUE O
        DISSE. Ela comparava BEFORE com AFTER e mais nada — e o canário é
        `bluesky.author.incremental`, que o dono já declara `PROVEN`. Um
        mutante que escrevesse `'PROVEN'` em `CAPABILITY_STATE_AFTER` não
        mudava número nenhum AQUI, e passava verde.

            UMA SENTINELA QUE VIGIA UM CAMPO CUJO VALOR JÁ É O DA MUTAÇÃO
            NÃO VIGIA NADA.

        A pergunta certa não é «os dois são iguais?» — é «o depois é o que o
        DONO diz?». `scrap_capacidades` é quem declara o estado, e este
        ficheiro não lhe escreve.
        """
        self.assertEqual(self.trace['CAPABILITY_STATE_BEFORE'],
                         self.trace['CAPABILITY_STATE_AFTER'])
        self.assertEqual(self.trace['CAPABILITY_STATE_AFTER'],
                         cap.estado(CAPACIDADE))

    def test_rt32b_e_nem_uma_capacidade_QUE_NAO_E_PROVEN_se_promove(self):
        """A prova só vale se puder falhar.

        O canário está `PROVEN`: sobre ele, «não promoveu» e «promoveu para
        PROVEN» são a mesma linha. A identidade do LinkedIn está `PARTIAL` —
        nela, uma promoção é visível.

            UMA PROVA QUE SÓ CORRE ONDE O ERRO É INVISÍVEL NÃO É UMA PROVA.
        """
        pinar_o_banco()
        _o, trace = sx.COLLECT(platform='LINKEDIN',
                               capability='linkedin.identity.discovery',
                               run_id='RC01-RT32B',
                               site_url='https://exemplo.invalido/')
        self.assertNotEqual(cap.estado('linkedin.identity.discovery'), 'PROVEN',
                            'esta prova escolheu a capacidade errada: ela já '
                            'está PROVEN e voltou a ser cega')
        self.assertEqual(trace['CAPABILITY_STATE_AFTER'],
                         cap.estado('linkedin.identity.discovery'))
        self.assertEqual(trace['CAPABILITY_STATE_BEFORE'],
                         trace['CAPABILITY_STATE_AFTER'])



# ══════════════════════════════════════════════════════════════════════════
# NS1–NS7 · UMA ROTA QUE NÃO CORREU NÃO OBSERVOU NADA
# ══════════════════════════════════════════════════════════════════════════
class UmaRotaQueNaoCorreuNaoObservouNada(unittest.TestCase):
    """⚠️ DEFEITO MEDIDO NA NIGHT-SHIFT-01 §6, E REPRODUZIDO ANTES DE CORRIGIDO.

    `instagram.reel.capture` é recusada pela política — `RESULT =
    ROUTE_NOT_ALLOWED`, `PROVIDER_USED = None`, `COST_STATE = NOT_RUN` — e
    mesmo assim devolve UM objeto: um esqueleto de REEL com todos os campos em
    `NOT_KNOWN`. Ele nasce de propósito LÁ EM BAIXO, porque a cadeia de Reel
    distingue REUSAR de ADQUIRIR e devolve o que sabe mesmo quando a aquisição
    é recusada. O erro estava AQUI EM CIMA: quem decide o que é COLHEITA é
    `scrap_colheita`, e ele carimbava o esqueleto com um `SOURCE_ID`
    verdadeiro. O contrato deixava passar sem um único reparo.

        UMA ROTA QUE NÃO CORREU NÃO OBSERVOU NADA.
        UM ESQUELETO COM SOURCE_ID É UMA OBSERVAÇÃO FABRICADA.

    O par `(objetos, trace)` desta bateria NÃO é escrito à mão: é o que a
    cadeia real devolve AGORA, medido em `setUpClass` pelo caminho real.

        UM TRACE INVENTADO PROVA UMA SITUAÇÃO INVENTADA.
    """

    @classmethod
    def setUpClass(cls):
        pinar_o_banco()
        cls.objetos, cls.trace = sx.COLLECT(
            platform='INSTAGRAM', capability='instagram.reel.capture',
            run_id='NS01-ROTA-RECUSADA',
            url='https://www.instagram.com/reel/EXEMPLO/')

    def _colher_com(self, objetos, trace):
        """Corre o DONO DA COLHEITA sobre um par que a cadeia real produziu.

        Troca-se `COLLECT` e mais nada: o que está sob prova é a decisão de
        `scrap_colheita` — e essa decisão é a que estava errada.
        """
        real = sx.COLLECT
        sx.COLLECT = lambda **_k: (objetos, trace)
        try:
            return sc.colher(FASE, run_id='NS01', fonte=FONTE, handle=HANDLE)
        finally:
            sx.COLLECT = real

    def test_ns1_a_rota_recusada_devolve_mesmo_um_objeto(self):
        """A PREMISSA DESTA BATERIA É MEDIDA, E NÃO SUPOSTA.

        Se a cadeia deixar de devolver o esqueleto, as sentinelas abaixo
        passariam a provar o vazio. Então mede-se a premissa primeiro.
        """
        self.assertEqual(self.trace['RESULT'], 'ROUTE_NOT_ALLOWED')
        self.assertEqual(len(self.objetos), 1)

    def test_ns2_e_o_dono_do_custo_diz_que_ela_nao_correu(self):
        """NOT_RUN != COST 0. O SINAL É DO DONO DO CUSTO, NÃO DO ESTADO DE FALHA."""
        self.assertEqual(self.trace['COST_STATE'], sc.NAO_CORREU)
        self.assertIsNone(self.trace['PROVIDER_USED'])
        self.assertFalse(self.trace['PAID_PROVIDER_USED'])

    def test_ns3_o_esqueleto_nao_traz_nada_que_se_tenha_observado(self):
        reel = self.objetos[0]['REEL']
        sabidos = [k for k, v in reel.items()
                   if v not in ('NOT_KNOWN', None, '', [])
                   and k not in ('PLATFORM', 'POST_ID', 'SOURCE_URL')]
        self.assertEqual(sabidos, [],
                         'a rota nao correu e ainda assim sabe %s' % sabidos)

    def test_ns4_nada_disso_vira_colheita(self):
        self.assertEqual(self._colher_com(self.objetos, self.trace)['COLHEITA'], [])

    def test_ns5_mas_tambem_nao_desaparece(self):
        """NÃO DESTRUIR EVIDÊNCIA SILENCIOSAMENTE: sai por SUPORTE, contado."""
        env = self._colher_com(self.objetos, self.trace)
        desconhecido = [s for s in env['SUPORTE']
                        if s['ESPECIE'] == rc.ESPECIE_DESCONHECIDA]
        self.assertEqual(len(desconhecido), 1)
        self.assertEqual(desconhecido[0]['QUANTOS'], len(self.objetos))
        self.assertIn(rc.RUN_RECEIPT, [s['ESPECIE'] for s in env['SUPORTE']])

    def test_ns6_e_o_envelope_diz_porque_o_zero_e_zero(self):
        """UM ZERO SEM MOTIVO ESCRITO LÊ-SE COMO FALHA DA FONTE."""
        env = self._colher_com(self.objetos, self.trace)
        porque = env['PORQUE_ZERO_COLHEITA']
        self.assertIn(sc.NAO_CORREU, porque)
        self.assertIn('ROUTE_NOT_ALLOWED', porque)
        self.assertEqual(env['ESTADO'], rc.PARTIAL)
        self.assertEqual(rc.conferir(env, RAIZ), [])

    def test_ns7_e_uma_rota_QUE_CORREU_continua_a_colher(self):
        """A GUARDA NÃO PODE FECHAR A PORTA A QUEM ENTROU PELA PORTA.

        O canário corre a sério contra o mundo falso: se a guarda lesse o
        estado de falha em vez do estado do custo, este zero apareceria aqui.
        """
        pinar_o_banco()
        env = sc.colher(FASE, run_id='NS01-CORREU', fonte=FONTE, handle=HANDLE)
        self.assertEqual(env['ESTADO'], rc.SUCCESS)
        self.assertEqual(len(env['COLHEITA']), 1)
        self.assertEqual(env['COLHEITA'][0]['SOURCE_ID'], FONTE)
        self.assertNotIn('PORQUE_ZERO_COLHEITA', env)



# ══════════════════════════════════════════════════════════════════════════
# NS8–NS15 · UMA FALHA QUE SABE NÃO PODE CHEGAR COMO UMA FALHA QUE NÃO SABE
# ══════════════════════════════════════════════════════════════════════════
class UmaFalhaQueSabeChegaComNome(unittest.TestCase):
    """⚠️ MEDIDO NA NIGHT-SHIFT-01 §9, NUM RUNNER SEM CHROME.

        instagram.profile.discovery -> RESULT = UNKNOWN_ERROR
        ROUTER_RECORD.ERRO = «sem Chrome nesta máquina: nenhum Chrome ou
                              Chromium encontrado no PATH nem nos caminhos
                              padrão»

    A frase sabia exactamente o que tinha acontecido. O ESTADO dizia «não
    classificado». De manhã, `UNKNOWN_ERROR` sobre Instagram manda alguém
    depurar o Instagram — quando o que falta é um navegador.

        UMA MENSAGEM QUE SABE E UM ESTADO QUE NÃO SABE VALEM MENOS QUE NENHUM
        DOS DOIS: QUEM LÊ POR MÁQUINA LÊ O ESTADO.

    Nada disto é vocabulário novo: `leis/falhas.py` já tinha
    `EXECUTOR_UNAVAILABLE` e já listava `BROWSER_NOT_REACHED` como nome nativo
    dele. Faltava quem o dissesse — e o dono é `cdp`, que a própria
    `falhas.classificar` nomeia entre quem «deve classificar por conta
    própria».

        FAILURE STATE VEM DO DONO, OU NÃO É FAILURE STATE.

    O QUE É FALSO AQUI
    -------------------
    A FERRAMENTA, e só ela: `instagram_janela.perfis` é trocada por uma que
    levanta o que o `cdp` levanta. Não se chama `perfis()` a sério porque, numa
    máquina COM Chrome, ela subia um Chrome e ia à internet — e a prova
    passaria a medir a internet.
    """

    def _correr(self, excecao):
        """Corre o caminho real — portão, roteador, política, selo — e devolve
        o par (objetos, trace). Só a ferramenta é falsa."""
        import instagram_janela as ij
        real = ij.perfis

        def rebenta(*_a, **_k):
            raise excecao
        ij.perfis = rebenta
        try:
            pinar_o_banco()
            return sx.COLLECT(platform='INSTAGRAM',
                              capability='instagram.profile.discovery',
                              run_id='NS01-SEM-CHROME', camada='perfis')
        finally:
            ij.perfis = real

    def test_ns08_o_dono_da_ferramenta_declara_o_estado(self):
        """`cdp` sabe que não alcançou o navegador, e passa a dizê-lo.

        Porta local fechada, sem uma única ida à internet.
        """
        import cdp
        with self.assertRaises(cdp.Erro) as c:
            cdp.abas(1, timeout=1)
        self.assertEqual(c.exception.estado, cdp.BROWSER_NOT_REACHED)

    def test_ns09_e_a_casa_ja_sabia_traduzir_esse_nome(self):
        """O estado não é inventado nesta missão: já estava na taxonomia."""
        import cdp
        import falhas
        self.assertEqual(falhas.traduzir(cdp.BROWSER_NOT_REACHED),
                         'EXECUTOR_UNAVAILABLE')

    def test_ns10_o_que_o_dono_nao_declara_continua_a_ser_nao_sei(self):
        """NÃO SEI CONTINUA A SER UMA RESPOSTA.

        Um erro de JavaScript na página não é o navegador em falta. Carimbá-lo
        com o mesmo nome seria trocar um balde por outro.
        """
        import cdp
        _o, trace = self._correr(cdp.Erro('o JavaScript da página lançou'))
        self.assertEqual(trace['RESULT'], 'UNKNOWN_ERROR')

    def test_ns11_sem_navegador_o_estado_diz_qual_e(self):
        import cdp
        _o, trace = self._correr(
            cdp.Erro('sem Chrome nesta máquina: nenhum Chrome no PATH',
                     cdp.BROWSER_NOT_REACHED))
        self.assertEqual(trace['RESULT'], 'EXECUTOR_UNAVAILABLE')
        self.assertEqual(trace['NATIVE_REASON'], cdp.BROWSER_NOT_REACHED)

    def test_ns12_e_a_frase_nao_se_perde_pelo_caminho(self):
        """UM ESTADO SEM A FRASE MANDA A PESSOA CERTA PARA O SÍTIO ERRADO.

        O nome vai em `NATIVE_REASON`, que é campo de máquina. A frase vai em
        `DETALHE` e chega a `ERRO`. UM NOME E UMA FRASE NÃO CABEM NO MESMO CAMPO.
        """
        import cdp
        _o, trace = self._correr(
            cdp.Erro('sem Chrome nesta máquina: nenhum Chrome no PATH',
                     cdp.BROWSER_NOT_REACHED))
        self.assertIn('sem Chrome nesta máquina',
                      trace['ROUTER_RECORD']['ERRO'])

    def test_ns13_a_culpa_fica_na_camada_certa(self):
        """ROTA CAÍDA NÃO É FONTE CAÍDA. Nada foi medido sobre o Instagram."""
        import cdp
        objetos, trace = self._correr(
            cdp.Erro('sem Chrome', cdp.BROWSER_NOT_REACHED))
        r = trace['ROUTER_RECORD']
        self.assertEqual(objetos, [])
        self.assertEqual(trace['FAILURE_LAYER'], 'EXECUTOR')
        self.assertEqual(r['EXECUTOR_HEALTH'], 'BROKEN')
        self.assertEqual(r['SOURCE_HEALTH'], 'HEALTHY')
        self.assertFalse(r['DEGRADES_SOURCE'])

    def test_ns14_e_o_trace_diz_o_que_fazer_a_seguir(self):
        """UMA CHAVE ESCRITA A None NÃO É UMA CHAVE AUSENTE.

        O roteador escrevia `RECOVERY_ACTION = None` mesmo quando ninguém a
        declarara, e `selar()` deriva-a com `setdefault` — que olha para a
        PRESENÇA da chave, não para o valor. A derivação nunca corria.
        """
        import cdp
        _o, trace = self._correr(
            cdp.Erro('sem Chrome', cdp.BROWSER_NOT_REACHED))
        self.assertEqual(trace['RECOVERY_ACTION'], 'NEEDS_HUMAN_FIX')

    def test_ns15_e_isso_vale_para_qualquer_adaptador_nao_so_este(self):
        """O buraco do `setdefault` não era do Instagram: era do roteador.

        Qualquer dono que declare o estado e não declare a recuperação —
        o ramo de `HTTPError` do YouTube, hoje — perdia-a da mesma maneira.
        """
        import scrap_http as _http
        _o, trace = self._correr(
            _http.EstadoDaApi({'STATE': 'ROUTE_UNAVAILABLE',
                               'NATIVE_REASON': 'ATOR_NAO_ALCANCADO'}))
        self.assertEqual(trace['RESULT'], 'ROUTE_UNAVAILABLE')
        self.assertEqual(trace['RECOVERY_ACTION'], 'CHANGE_ROUTE')


if __name__ == '__main__':
    unittest.main(verbosity=2)
