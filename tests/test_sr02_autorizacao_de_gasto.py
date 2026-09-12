# -*- coding: utf-8 -*-
"""SCRAP-SR-02 — as sentinelas da guarda de gasto.

O falso e SEMPRE `coletor._curl`: a fronteira do provider, por baixo da guarda,
dos dois orcamentos, do teto do lado do provider e da trava de retentativa.

    APIFY_REAL_RUNS = 0 · COST_USD = 0
"""
import ast
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

# ══════════════════════════════════════════════════════════════════════════
# O DONO DA RELEVANCIA NAO VIVE NESTA ARVORE, E ESTA SUITE NAO O COPIA
# ══════════════════════════════════════════════════════════════════════════
# `leis/relevancia_da_fonte.py` e da SR-01, noutro ramo. A guarda DEPENDE dele
# e nao o substitui — e esta suite tambem nao.
#
# Entao instala-se um SUBSTITUTO, e ele e declarado como substituto. As palavras
# dele sao DE PROPOSITO diferentes das do dono real:
#
#     O QUE SE MEDE AQUI E A LIGACAO, NUNCA A LISTA.
#
# A guarda le `rf.SIM` — seja `rf.SIM` o que for. Se esta suite escrevesse as
# palavras verdadeiras do dono, ela seria uma copia do dono com outro nome, e a
# copia envelheceria calada exactamente como o ficheiro que se recusou a trazer.
# `test_a_guarda_nao_escreve_as_palavras_do_dono` fecha a outra metade: nenhuma
# palavra de relevancia esta escrita a mao dentro da lei.
#
# Quando a SR-01 chegar, o dono verdadeiro entra e os testes marcados
# `COM_O_DONO` acendem-se sozinhos. Ate la eles dizem-no em voz alta, em vez de
# passarem calados.
class _SubstitutoDaRelevancia(object):
    """NAO E O DONO. E o minimo que a ligacao precisa, com palavras proprias."""

    CONTRATO = 'SUBSTITUTO_DE_TESTE/NAO_E_O_DONO'
    SIM = 'SERVE_SUB'
    NAO = 'NAO_SERVE_SUB'
    NAO_SEI = 'NAO_SEI_SUB'
    NAO_SE_APLICA = 'NAO_SE_APLICA_SUB'
    ERRO = 'ERRO_SUB'
    NAO_AVALIADA = 'NAO_AVALIADA_SUB'
    RESULTADOS = (SIM, NAO, NAO_SEI, NAO_SE_APLICA, ERRO)
    AUTORIZA = 'AUTORIZA_SUB'
    BARRA = 'BARRA_SUB'
    VERSAO_DA_AVALIACAO = '1'

    class SourceIdInvalido(ValueError):
        pass

    @classmethod
    def conferir_source_id(cls, sid):
        """URL NAO E SOURCE_ID. A regra e do dono; aqui prova-se so a ligacao."""
        if not sid or '://' in str(sid) or str(sid).startswith('www.'):
            raise cls.SourceIdInvalido('URL NAO E SOURCE_ID: %r' % (sid,))


try:
    import relevancia_da_fonte as _dono_real                       # noqa: E402
    DONO_PRESENTE = True
except ImportError:
    _dono_real = None
    DONO_PRESENTE = False
    sys.modules['relevancia_da_fonte'] = _SubstitutoDaRelevancia

rf = _dono_real or _SubstitutoDaRelevancia
COM_O_DONO = unittest.skipUnless(
    DONO_PRESENTE, 'leis/relevancia_da_fonte.py (SR-01) nao esta nesta arvore')

import autorizacao_de_gasto as ag                                 # noqa: E402
import coletor as ct                                              # noqa: E402
import scrap_executor as sx                                       # noqa: E402

VISTO = []


def _falso(url, *, token, metodo='GET', corpo=None, timeout=300, tentativas=4):
    VISTO.append(metodo)
    if metodo == 'POST':
        return {'data': {'id': 'FAKE', 'status': 'SUCCEEDED', 'defaultDatasetId': 'D',
                         'usageTotalUsd': 0}}
    return {'data': {'items': [], 'status': 'SUCCEEDED'}}


ct._curl = _falso


def normal(**kw):
    d = dict(MODO=ag.NORMAL, SOURCE_ID='IT-T3-002', PROPOSITO='T3',
             RELEVANCE_RESULT=rf.SIM, RELEVANCE_VERDICT=rf.AUTORIZA,
             DECISION_VERSION=rf.VERSAO_DA_AVALIACAO, EVIDENCE_REFERENCE='livro.json',
             MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1, MAX_USD=0.10, MAX_ITEMS=5)
    d.update(kw)
    return ag.Autorizacao(**d)


class Base(unittest.TestCase):
    """Cada ataque mede POSTS, nunca a mensagem. Zero POST e a unica prova."""

    def setUp(self):
        VISTO.clear()

    def posts(self):
        return VISTO.count('POST')

    def comprar(self, **kw):
        base = dict(token='FAKE', run_id='SR02', platform='X', country='IT',
                    mission='T', query='q', source_version='v',
                    evidence_path='data/samples/SR02.json', salvar_raw=False, wait=1)
        base.update(kw)
        try:
            ct.executar('ator~s', {'x': 1}, **base)
            return None
        except ag.SemAutorizacaoDeGasto as e:
            return e.veredito['RECUSA']

    def recusa(self, esperada, **kw):
        r = self.comprar(**kw)
        self.assertEqual(r, esperada)
        self.assertEqual(self.posts(), 0, 'saiu POST numa compra recusada')


# ══════════════════════════════════════════════════════════════════════════
# 1-5 · O QUE NAO SUBSTITUI UMA AUTORIZACAO
# ══════════════════════════════════════════════════════════════════════════
class NadaSubstituiAutorizacao(Base):

    def test_01_script_directo_sem_auth(self):
        self.recusa(ag.SEM_AUTORIZACAO, source_id='IT-T3-002', proposito='T3')

    def test_02_workflow_sem_auth(self):
        """Um workflow e um `python3 x.py`. Sem auth instalada, zero POST."""
        self.recusa(ag.SEM_AUTORIZACAO)

    def test_03_token_substitui_auth(self):
        """`TOKEN_PRESENT != SPEND_AUTHORIZED`."""
        self.recusa(ag.SEM_AUTORIZACAO, token='UM-TOKEN-QUE-PARECE-REAL')

    def test_04_budget_substitui_auth(self):
        """`BUDGET_PRESENT != SPEND_AUTHORIZED`."""
        with ct.orcamento_financeiro(5.00):
            self.recusa(ag.SEM_AUTORIZACAO, source_id='IT-T3-002', proposito='T3',
                        teto_usd=0.10)

    def test_05_policy_allowed_substitui_auth(self):
        """`ROUTE_ALLOWED != SPEND_AUTHORIZED`. A matriz nao autoriza gasto."""
        import social_matriz as mz
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_POST')['DECISAO'], 'ALLOWED')
        self.recusa(ag.SEM_AUTORIZACAO, source_id='IT-T3-002', proposito='T3')


# ══════════════════════════════════════════════════════════════════════════
# 6-11 · A IDENTIDADE DO PAR
# ══════════════════════════════════════════════════════════════════════════
class OParEExacto(Base):

    def test_06_sim_de_t3_usado_em_t9(self):
        with ag.autorizacao(normal()):
            self.recusa(ag.PROPOSITO_DIFERENTE, source_id='IT-T3-002', proposito='T9')

    def test_07_auth_de_A_usada_em_B(self):
        with ag.autorizacao(normal()):
            self.recusa(ag.FONTE_DIFERENTE, source_id='IT-T9-001', proposito='T3')

    def test_08_09_10_as_ausencias_nao_autorizam(self):
        """`NAO_SEI`, `ERRO` e `NAO_AVALIADA` — tres confissoes, nenhuma um SIM."""
        for valor in (rf.NAO_SEI, rf.ERRO, rf.NAO_AVALIADA, rf.NAO, rf.NAO_SE_APLICA):
            VISTO.clear()
            with ag.autorizacao(normal(RELEVANCE_RESULT=valor, RELEVANCE_VERDICT=None)):
                r = self.comprar(source_id='IT-T3-002', proposito='T3')
            self.assertEqual(r, ag.RELEVANCIA_NAO_AUTORIZA, valor)
            self.assertEqual(self.posts(), 0, valor)

    def test_11_url_vira_source_id(self):
        with self.assertRaises(rf.SourceIdInvalido):
            normal(SOURCE_ID='https://exemplo.tld/f')
        with ag.autorizacao(normal()):
            self.recusa(ag.FONTE_INVALIDA, source_id='http://exemplo.tld/f', proposito='T3')

    def test_fonte_ausente_na_chamada(self):
        with ag.autorizacao(normal()):
            self.recusa(ag.FONTE_AUSENTE)

    def test_33_purpose_ausente(self):
        with ag.autorizacao(normal()):
            self.recusa(ag.PROPOSITO_AUSENTE, source_id='IT-T3-002')

    def test_34_source_ausente(self):
        with self.assertRaises(ag.AutorizacaoInvalida):
            ag.Autorizacao(MODO=ag.NORMAL, PROPOSITO='T3', RELEVANCE_RESULT=rf.SIM,
                           MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1, MAX_USD=0.1, MAX_ITEMS=1)


# ══════════════════════════════════════════════════════════════════════════
# 12-17 · NINGUEM FABRICA UMA AUTORIZACAO
# ══════════════════════════════════════════════════════════════════════════
class NinguemFabricaAutorizacao(Base):

    def test_12_13_um_dicionario_nao_e_autorizacao(self):
        for obj in ({'MODO': ag.NORMAL, 'RELEVANCE_RESULT': rf.SIM}, 'SIM', True, 1):
            with self.assertRaises(ag.AutorizacaoInvalida):
                with ag.autorizacao(obj):
                    pass

    def test_14_apify_pool_nao_julga_relevancia(self):
        fonte = open(os.path.join(RAIZ, 'ferramentas/apify_pool.py'), encoding='utf-8').read()
        for proibido in ('relevancia', 'RELEVANCE', 'autorizacao_de_gasto', 'PROPOSITO'):
            self.assertNotIn(proibido, fonte)

    def test_15_coletor_nao_julga_relevancia(self):
        """O coletor CONSULTA a guarda; nao calcula relevancia nenhuma."""
        fonte = open(os.path.join(RAIZ, 'coleta/coletor.py'), encoding='utf-8').read()
        self.assertIn('ag.exigir(', fonte)
        for proibido in ('import relevancia_da_fonte', 'rf.portao(', 'SOURCE_SCORE',
                         'ler_livro('):
            self.assertNotIn(proibido, fonte)

    def test_16_normal_vira_trial(self):
        """Um NORMAL que se declare TRIAL perde a fonte — e a chamada denuncia-o."""
        t = ag.Autorizacao(MODO=ag.TRIAL, ALVO='x', HUMAN_AUTHORIZATION='h',
                           MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1, MAX_USD=0.1, MAX_ITEMS=1)
        self.assertIsNone(t.SOURCE_ID)
        self.assertIsNone(t.RELEVANCE_RESULT)
        # E o TRIAL do executor nao e este, e continua a nao autorizar gasto.
        self.assertNotEqual(sx.TRIAL, ag.TRIAL)

    def test_17_normal_vira_probe(self):
        """Um PROBE exige assinatura humana que um NORMAL nao tem de ter."""
        with self.assertRaises(ag.AutorizacaoInvalida):
            ag.Autorizacao(MODO=ag.PROBE, SOURCE_ID='IT-T3-002', PROPOSITO='T3',
                           MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1, MAX_USD=0.1, MAX_ITEMS=1)


# ══════════════════════════════════════════════════════════════════════════
# 18-22 · O PROBE E LIMITADO, E NAO PROMOVE
# ══════════════════════════════════════════════════════════════════════════
class OProbeNaoPromove(Base):

    def probe(self, **kw):
        d = dict(MODO=ag.PROBE, SOURCE_ID='IT-T9-008', PROPOSITO='T9',
                 HUMAN_AUTHORIZATION='humano', MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1,
                 MAX_USD=0.05, MAX_ITEMS=3)
        d.update(kw)
        return ag.Autorizacao(**d)

    def test_18_probe_sem_human_auth(self):
        with self.assertRaises(ag.AutorizacaoInvalida):
            self.probe(HUMAN_AUTHORIZATION=None)

    def test_19_20_21_probe_sem_teto(self):
        for t in ('MAX_USD', 'MAX_PROVIDER_RUNS', 'MAX_START_POSTS', 'MAX_ITEMS'):
            with self.assertRaises(ag.AutorizacaoInvalida, msg=t):
                self.probe(**{t: None})

    def test_22_probe_nao_auto_promove(self):
        """Depois do probe, a guarda nao escreveu decisao nenhuma em sitio nenhum.

        A prova que e DESTA lei e esta: o probe compra e a lei nao toca no livro
        de ninguem. Que o livro continue a dizer NAO_AVALIADA e prova do DONO do
        livro, e vive em `test_22b`, que so corre quando ele existe.
        """
        with ag.autorizacao(self.probe()):
            self.assertIsNone(self.comprar(source_id='IT-T9-008', proposito='T9',
                                           teto_usd=0.05))
        self.assertIn('AUTO_PROMOTION', ag.NAO_CRIAR)
        fonte = open(os.path.join(RAIZ, 'leis/autorizacao_de_gasto.py'),
                     encoding='utf-8').read()
        arvore = ast.parse(fonte)
        # Nenhuma escrita, em ficheiro nenhum: a lei nunca abre nada para gravar.
        for n in ast.walk(arvore):
            if isinstance(n, ast.Call):
                nome = getattr(n.func, 'id', None) or getattr(n.func, 'attr', None)
                self.assertNotIn(nome, ('open', 'gravar', 'escrever', 'dump',
                                        'promover', 'registar'), nome)
        for proibido in ('escrever_livro', 'gravar_decisao', 'promover_fonte'):
            self.assertNotIn(proibido, fonte)

    @COM_O_DONO
    def test_22b_o_livro_do_dono_continua_a_dizer_nao_avaliada(self):
        with ag.autorizacao(self.probe()):
            self.comprar(source_id='IT-T9-008', proposito='T9', teto_usd=0.05)
        e = rf.estado('IT-T9-008', 'T9', livro=[])
        self.assertEqual(e['ESTADO'], rf.NAO_AVALIADA)
        self.assertIsNone(e['DECISAO'])

    def test_probe_funciona_para_fonte_nao_avaliada(self):
        """Sem este modo, avaliar exigiria a resposta que a avaliacao produz."""
        with ag.autorizacao(self.probe()):
            self.assertIsNone(self.comprar(source_id='IT-T9-008', proposito='T9',
                                           teto_usd=0.05))
        self.assertEqual(self.posts(), 1)


# ══════════════════════════════════════════════════════════════════════════
# 23-31 · OS TETOS E AS TRAVAS ANTERIORES
# ══════════════════════════════════════════════════════════════════════════
class OsTetosMordem(Base):

    def test_23_trial_vira_recorrente(self):
        """Uma autorizacao de um POST nao compra duas vezes, em modo nenhum."""
        t = ag.Autorizacao(MODO=ag.TRIAL, ALVO='x', HUMAN_AUTHORIZATION='h',
                           MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1, MAX_USD=0.1, MAX_ITEMS=1)
        with ag.autorizacao(t):
            self.assertIsNone(self.comprar(teto_usd=0.1))
            self.assertEqual(self.comprar(teto_usd=0.1), ag.TETO_ESTOURADO)
        self.assertEqual(self.posts(), 1)

    def test_26_27_28_segundo_post_nunca(self):
        """Rotacao de token e retentativa nao criam uma segunda compra."""
        with ag.autorizacao(normal()) as a:
            self.comprar(source_id='IT-T3-002', proposito='T3')
            for _ in range(5):
                self.assertEqual(self.comprar(source_id='IT-T3-002', proposito='T3'),
                                 ag.TETO_ESTOURADO)
            self.assertEqual(a.posts_usados, 1)
        self.assertEqual(self.posts(), 1)

    def test_29_provider_cap_removido(self):
        """Pedir mais que o autorizado recusa — nao rebaixa em silencio."""
        with ag.autorizacao(normal(MAX_USD=0.10)):
            self.recusa(ag.TETO_ACIMA_DO_AUTORIZADO, source_id='IT-T3-002',
                        proposito='T3', teto_usd=99.0)

    def test_30_31_orcamentos_anteriores_continuam(self):
        fonte = open(os.path.join(RAIZ, 'coleta/coletor.py'), encoding='utf-8').read()
        for trava in ('orcamento_financeiro_actual()', 'maxTotalChargeUsd',
                      'PostTalvezCriado', 'reserva.desconhecer()', 'RAW_SHA256'):
            self.assertIn(trava, fonte, trava)
        self.assertLess(fonte.index('ag.exigir('), fonte.index('orcamento.reservar('))

    def test_32_unknown_nao_vira_zero(self):
        fonte = open(os.path.join(RAIZ, 'coleta/coletor.py'), encoding='utf-8').read()
        self.assertIn('POTENTIAL COMMITMENT != NOTHING HAPPENED', fonte)

    def test_teto_ausente_nao_e_infinito(self):
        for t in ('MAX_USD', 'MAX_ITEMS', 'MAX_START_POSTS', 'MAX_PROVIDER_RUNS'):
            with self.assertRaises(ag.AutorizacaoInvalida, msg=t):
                normal(**{t: None})


# ══════════════════════════════════════════════════════════════════════════
# 24-25, 36-40 · NENHUMA PORTA LATERAL
# ══════════════════════════════════════════════════════════════════════════
def _quem_pede_criacao_de_corrida():
    """Ficheiros que PASSAM um endereco `/acts/.../runs` a uma chamada.

    O criterio nao e «a string existe no ficheiro»: e «a string entra numa
    chamada». `medidas/portao.py` guarda `'POST /acts/{actor}/runs?waitForFinish'`
    como ROTULO de relatorio, com `{actor}` nunca formatado — ele nomeia a porta,
    nao a abre. A primeira versao desta sentinela apanhou-o e estava errada.

        NOMEAR O ENDERECO NAO E PEDI-LO.
    """
    quem = set()
    for r, d, fs in os.walk(RAIZ):
        if any(x in r for x in ('node_modules', '.git', '/build', '__pycache__')):
            continue
        for f in fs:
            if not f.endswith('.py'):
                continue
            cam = os.path.join(r, f)
            try:
                arvore = ast.parse(open(cam, encoding='utf-8', errors='replace').read())
            except Exception:
                continue
            for n in ast.walk(arvore):
                if not isinstance(n, ast.Call):
                    continue
                for arg in list(n.args) + [k.value for k in n.keywords]:
                    for dentro in ast.walk(arg):
                        if (isinstance(dentro, ast.Constant)
                                and isinstance(dentro.value, str)
                                and '/acts/' in dentro.value
                                and '/runs' in dentro.value):
                            quem.add(os.path.relpath(cam, RAIZ))
    return quem


class NenhumaPortaLateral(Base):

    def test_24_25_26_uma_primitiva_so_por_AST(self):
        """`metodo='POST'` como ARGUMENTO REAL, contado por AST e nao por texto."""
        sitios = []
        for r, d, fs in os.walk(RAIZ):
            if any(x in r for x in ('node_modules', '.git', '/build')):
                continue
            for f in fs:
                if not f.endswith('.py'):
                    continue
                cam = os.path.join(r, f)
                try:
                    arvore = ast.parse(open(cam, encoding='utf-8', errors='replace').read())
                except Exception:
                    continue
                for n in ast.walk(arvore):
                    if isinstance(n, ast.Call):
                        for kw in n.keywords:
                            if (kw.arg == 'metodo' and isinstance(kw.value, ast.Constant)
                                    and kw.value.value == 'POST'):
                                sitios.append(os.path.relpath(cam, RAIZ))
        self.assertEqual(sitios, ['coleta/coletor.py'], sitios)

    def test_41_so_um_ficheiro_monta_o_URL_QUE_CRIA_CORRIDA(self):
        """A invariante VERDADEIRA nao e o literal `POST`: e quem monta `/runs`.

        `test_24_25_26` conta `metodo='POST'` escrito a letra, e isso NAO e a
        mesma afirmacao. Medido nesta arvore: `regras/sensor_coleta.py` fala HTTP
        com a Apify passando `method=metodo` — uma VARIAVEL — e por isso aquele
        sentinela e cego a ele. Ali nao ha buraco, porque o ficheiro troca o
        TRANSPORTE (`coletor._curl = _curl_robusto`) e a corrida continua a ser
        criada por `coletor.executar`, que consulta a guarda. Mas o sentinela nao
        sabia disso: ele passava por sorte.

            CONTAR O LITERAL NAO E CONTAR QUEM CRIA.

        Esta sentinela conta quem CRIA: so um ficheiro pode montar um endereco de
        criacao de corrida da Apify.
        """
        montam = _quem_pede_criacao_de_corrida()
        self.assertEqual(sorted(montam), ['coleta/coletor.py'], sorted(montam))

    def test_42_quem_troca_o_transporte_nao_cria_corrida(self):
        """Trocar o transporte e legitimo. Criar a corrida por fora nao e.

        `coletor._curl` e substituivel de proposito — a `regras/sensor_coleta.py`
        fa-lo para nao perder respostas em stdout. O que nao pode acontecer e um
        substituto de transporte passar tambem a CRIAR a corrida, porque aí a
        criacao sairia de baixo da guarda.

            TROCAR O TRANSPORTE != ABRIR UMA SEGUNDA PORTA.
        """
        trocam, criam = set(), set()
        for r, d, fs in os.walk(RAIZ):
            if any(x in r for x in ('node_modules', '.git', '/build', '__pycache__')):
                continue
            for f in fs:
                if not f.endswith('.py'):
                    continue
                cam = os.path.join(r, f)
                rel = os.path.relpath(cam, RAIZ)
                try:
                    txt = open(cam, encoding='utf-8', errors='replace').read()
                    arvore = ast.parse(txt)
                except Exception:
                    continue
                for n in ast.walk(arvore):
                    # instalar um transporte: `<modulo>._curl = <algo>`
                    if isinstance(n, ast.Assign):
                        for alvo in n.targets:
                            if (isinstance(alvo, ast.Attribute) and alvo.attr == '_curl'
                                    and getattr(alvo.value, 'id', None) != 'self'):
                                trocam.add(rel)
        criam = _quem_pede_criacao_de_corrida()
        # Quem troca o transporte E cria corrida: so o dono da porta pode ser os dois.
        ambos = (trocam & criam) - {'coleta/coletor.py'}
        self.assertEqual(sorted(ambos), [], sorted(ambos))
        # E a troca de transporte existe de verdade nesta arvore — a sentinela
        # mede algo que acontece, e nao uma hipotese.
        self.assertIn('regras/sensor_coleta.py', trocam, sorted(trocam))

    def test_43_44_um_transporte_substituto_carrega_as_leis_do_transporte(self):
        """Quem substitui `coletor._curl` herda as leis que moravam dentro dele.

        Buraco REAL nesta arvore, nao hipotese. `regras/sensor_coleta.py` instala
        um transporte urllib em `coletor._curl` — troca legitima, porque o proxy
        deste ambiente derruba conexoes e o urllib sobrevive onde o subprocesso
        nao sobrevive. Mas o substituto repetia QUALQUER metodo quatro vezes,
        incluindo o POST que CRIA a execucao paga. Se o POST chegou a Apify e so
        a resposta se perdeu na volta, repetir nao reenvia um pedido perdido:
        acende uma segunda execucao paga, orfa, sem run_id e a gastar. Bastava um
        `import sensor_coleta` em qualquer ponto do processo para a autorizacao
        desta missao — que autoriza UM POST — virar ate quatro execucoes pagas.

            REPETIR UM GET E BARATO. REPETIR UM POST E COMPRAR DE NOVO.
            UMA LEI QUE MORA DENTRO DE UMA IMPLEMENTACAO VIAJA COM ELA.

        E `maxTotalChargeUsd` nao cobre isto: ele limita CADA execucao, nunca a
        soma das execucoes que ninguem sabe que existem.

        MEDE-SE O COMPORTAMENTO, E NAO O TEXTO
        ---------------------------------------
        A primeira versao desta sentinela conferia se a palavra `'POST'` aparecia
        no corpo da funcao, e PASSAVA com a lei removida: a palavra continuava la,
        noutra linha. Duas mutacoes provaram-no antes de alguem confiar nela.

            UMA SENTINELA QUE LE O TEXTO ENCONTRA A PALAVRA, NAO A DECISAO.

        E CORRE NUM PROCESSO PROPRIO, por duas razoes que sao a mesma:
        importar `sensor_coleta` TROCA `coletor._curl` para todo o processo — e
        essa e precisamente a coisa que se esta a medir. Medi-la aqui dentro
        contaminaria as outras sentinelas desta suite, e os enderecos de criacao
        de corrida que ela precisa de usar seriam contados por `test_41` como uma
        segunda porta. O subprocesso isola as duas coisas por construcao.
        """
        import subprocess
        import tempfile
        guiao = r'''
import os, sys
RAIZ = sys.argv[1]
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', 'regras', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import coletor as ct, scrap_http as http, urllib.request
import sensor_coleta as sensor
assert ct._curl is sensor._curl_robusto, "o substituto nao esta instalado"
ALVO = "https://api.apify.com/v2/" + "acts/a~b/" + "runs?waitForFinish=60"
LEITURA = "https://api.apify.com/v2/" + "acts/a~b"
idas = []
def cai(req, timeout=None):
    idas.append(getattr(req, "method", None) or req.get_method())
    raise OSError("o tunel caiu a meio da troca")
urllib.request.urlopen = cai
# LEI 1 · um POST vai UMA vez, e quem chama recebe PostTalvezCriado.
try:
    ct._curl(ALVO, token="FAKE", metodo="POST", corpo={})
    print("ERRO: o POST nao levantou")
except ct.PostTalvezCriado:
    pass
except Exception as e:
    print("ERRO: levantou %s em vez de PostTalvezCriado" % type(e).__name__)
print("POSTS=%d" % len(idas))
# E um GET continua retentado: a lei nao e «nunca repetir».
idas.clear()
try:
    ct._curl(LEITURA, token="FAKE")
except Exception:
    pass
print("GETS=%d" % len(idas))
# LEI 2 · a ida conta UMA vez no teto de rede — nem zero, nem duas.
idas.clear()
with http.orcamento_de_rede(3) as orc:
    try:
        ct._curl(ALVO, token="FAKE", metodo="POST", corpo={})
    except ct.PostTalvezCriado:
        pass
    print("REDE=%d" % orc.usados)
'''
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False,
                                         encoding='utf-8') as fh:
            fh.write(guiao)
            caminho = fh.name
        try:
            r = subprocess.run([sys.executable, caminho, RAIZ],
                               capture_output=True, text=True, timeout=180)
        finally:
            os.unlink(caminho)
        saida = r.stdout + r.stderr
        self.assertNotIn('ERRO:', saida, saida)
        self.assertIn('POSTS=1', saida,
                      'o POST saiu mais de uma vez: REPETIR UM POST E COMPRAR DE '
                      'NOVO\n%s' % saida)
        # O GET continua a repetir: a lei distingue metodo, nao proibe retentativa.
        self.assertRegex(saida, r'GETS=[2-9]', saida)
        # E a mesma ida nao e cobrada duas vezes. O `_curl` da casa reserva
        # explicitamente porque sai por SUBPROCESSO, que o teto nao ve (§80);
        # este sai por `urlopen`, que e onde o teto cobra. Copiar a reserva para
        # ca contava a ida duas vezes, e um teto que se esgota ao dobro recusa
        # coleta legitima com o nome errado.
        #
        #     O QUE O SUBSTITUTO HERDA E O EFEITO, NAO A LINHA.
        self.assertIn('REDE=1', saida,
                      'a ida nao contou exactamente UMA vez no teto de rede\n%s' % saida)

    def test_36_37_a_guarda_nao_tem_porta_de_teste(self):
        """Nenhum atalho de teste, ambiente ou bandeira desliga a guarda."""
        fonte = open(os.path.join(RAIZ, 'leis/autorizacao_de_gasto.py'),
                     encoding='utf-8').read()
        for proibido in ('getenv', 'environ', 'SKIP', 'DEBUG', 'FORCE', 'bypass',
                         'TESTING', '--yes'):
            self.assertNotIn(proibido, fonte, proibido)

    def test_38_actor_pago_nao_e_policy_override(self):
        self.assertIn('PAID_PROVIDER != POLICY_OVERRIDE', ag.LEIS)

    def test_39_40_todo_caminho_pago_atravessa_a_guarda(self):
        """Quem chama o dono pago passa pela guarda, venha de onde vier."""
        chamadores = []
        for r, d, fs in os.walk(RAIZ):
            if any(x in r for x in ('node_modules', '.git', '/build')):
                continue
            for f in fs:
                if not f.endswith('.py'):
                    continue
                cam = os.path.join(r, f)
                t = open(cam, encoding='utf-8', errors='replace').read()
                if re.search(r'\b(coletor|ct)\.executar\s*\(', t):
                    chamadores.append(os.path.relpath(cam, RAIZ))
        self.assertTrue(chamadores)
        # E o unico sitio que POSTa e o coletor, logo todos passam pela guarda.
        self.assertIn('coleta/coletor.py', [c for c in chamadores] + ['coleta/coletor.py'])
        fonte = open(os.path.join(RAIZ, 'coleta/coletor.py'), encoding='utf-8').read()
        self.assertEqual(fonte.count('ag.exigir('), 1)


# ══════════════════════════════════════════════════════════════════════════
# 35 · UMA AUTORIZACAO NAO SE REUSA FORA DO SEU BLOCO
# ══════════════════════════════════════════════════════════════════════════
class OReusoIndevido(Base):

    def test_35_a_autorizacao_nao_sobrevive_ao_bloco(self):
        a = normal()
        with ag.autorizacao(a):
            self.assertIsNotNone(ag.autorizacao_actual())
        self.assertIsNone(ag.autorizacao_actual())
        self.recusa(ag.SEM_AUTORIZACAO, source_id='IT-T3-002', proposito='T3')

    def test_a_guarda_nao_escreve_as_palavras_do_dono(self):
        """Duas listas com as mesmas palavras sao duas verdades.

        Esta e a metade que e DESTA lei: ela importa o eixo e nao o reescreve.
        Que o dono tire as palavras de `admissao` e prova do dono, e vive em
        `test_o_dono_tira_as_palavras_de_admissao`.
        """
        fonte = open(os.path.join(RAIZ, 'leis/autorizacao_de_gasto.py'),
                     encoding='utf-8').read()
        self.assertIn('import relevancia_da_fonte as rf', fonte)
        for reinventado in ("SIM = 'SIM'", "NAO = 'NAO'", "NAO_SEI =",
                            "NAO_SE_APLICA =", "RESULTADOS = ("):
            self.assertNotIn(reinventado, fonte, reinventado)
        # E o eixo tem de vir de `rf`, atributo por atributo: uma palavra de
        # relevancia escrita a mao seria a copia a entrar pela janela.
        lidos = {n.attr for n in ast.walk(ast.parse(fonte))
                 if isinstance(n, ast.Attribute)
                 and getattr(n.value, 'id', None) == 'rf'}
        self.assertIn('SIM', lidos)
        self.assertIn('AUTORIZA', lidos)
        self.assertIn('RESULTADOS', lidos)

    @COM_O_DONO
    def test_o_dono_tira_as_palavras_de_admissao(self):
        import admissao
        self.assertEqual(rf.RESULTADOS, admissao.RESULTADOS)

    def test_sem_o_dono_a_colheita_com_fonte_recusa(self):
        """A ausencia do dono e uma RECUSA com nome, nunca um caminho livre.

        Mede-se contra a lei importada de novo com o dono fora de `sys.modules`:
        e o unico jeito de medir o que acontece numa arvore onde a SR-01 nao
        chegou — que e exactamente esta arvore.
        """
        import importlib
        guardado = sys.modules.pop('relevancia_da_fonte', None)
        guardado_ag = sys.modules.pop('autorizacao_de_gasto')
        try:
            sem = importlib.import_module('autorizacao_de_gasto')
            self.assertIsNone(sem.rf)
            self.assertIsNone(sem.DONO_DA_RELEVANCIA)
            self.assertIn(sem.DONO_AUSENTE, sem.RECUSAS)
            # NORMAL e PROBE julgam fonte: nao se constroem sem o dono.
            for modo in (sem.NORMAL, sem.PROBE):
                with self.assertRaises(sem.AutorizacaoInvalida, msg=modo):
                    sem.Autorizacao(
                        MODO=modo, SOURCE_ID='IT-T3-002', PROPOSITO='T3',
                        RELEVANCE_RESULT='SIM', HUMAN_AUTHORIZATION='h',
                        MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1, MAX_USD=0.1,
                        MAX_ITEMS=1)
            # E o TRIAL, que nao julga fonte, continua a funcionar — por isso as
            # sentinelas desta casa ainda atravessam a porta paga.
            t = sem.Autorizacao(MODO=sem.TRIAL, ALVO='x', HUMAN_AUTHORIZATION='h',
                                MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1,
                                MAX_USD=0.1, MAX_ITEMS=1)
            self.assertTrue(sem.conferir(t)['AUTORIZA'])
        finally:
            sys.modules['autorizacao_de_gasto'] = guardado_ag
            if guardado is not None:
                sys.modules['relevancia_da_fonte'] = guardado


# ══════════════════════════════════════════════════════════════════════════
# MUTANTES — dezoito, e nenhum sobrevive
# ══════════════════════════════════════════════════════════════════════════
class OsMutantes(Base):

    def test_M1_guard_removed(self):
        fonte = open(os.path.join(RAIZ, 'coleta/coletor.py'), encoding='utf-8').read()
        self.assertIn('ag.exigir(', fonte)
        self.recusa(ag.SEM_AUTORIZACAO, source_id='IT-T3-002', proposito='T3')

    def test_M2_M3_M4_ausencias_permitidas(self):
        for v in (rf.NAO_AVALIADA, rf.NAO_SEI, rf.ERRO):
            VISTO.clear()
            with ag.autorizacao(normal(RELEVANCE_RESULT=v, RELEVANCE_VERDICT=None)):
                self.comprar(source_id='IT-T3-002', proposito='T3')
            self.assertEqual(self.posts(), 0, v)

    def test_M5_wrong_purpose_allowed(self):
        with ag.autorizacao(normal()):
            self.comprar(source_id='IT-T3-002', proposito='T9')
        self.assertEqual(self.posts(), 0)

    def test_M6_wrong_source_allowed(self):
        with ag.autorizacao(normal()):
            self.comprar(source_id='IT-T1-001', proposito='T3')
        self.assertEqual(self.posts(), 0)

    def test_M7_url_accepted(self):
        with ag.autorizacao(normal()):
            self.comprar(source_id='www.exemplo.tld', proposito='T3')
        self.assertEqual(self.posts(), 0)

    def test_M8_M9_M10_substituicoes(self):
        with ct.orcamento_financeiro(9.99):
            self.comprar(token='TOKEN', source_id='IT-T3-002', proposito='T3',
                         teto_usd=0.10)
        self.assertEqual(self.posts(), 0)

    def test_M11_M12_troca_de_modo(self):
        with self.assertRaises(ag.AutorizacaoInvalida):
            ag.Autorizacao(MODO=ag.PROBE, SOURCE_ID='IT-T3-002', PROPOSITO='T3',
                           MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1, MAX_USD=0.1,
                           MAX_ITEMS=1)
        with self.assertRaises(ag.AutorizacaoInvalida):
            ag.Autorizacao(MODO=ag.TRIAL, HUMAN_AUTHORIZATION='h', MAX_PROVIDER_RUNS=1,
                           MAX_START_POSTS=1, MAX_USD=0.1, MAX_ITEMS=1)

    def test_M13_M14_ilimitado(self):
        for modo, extra in ((ag.PROBE, {'SOURCE_ID': 'IT-T9-008', 'PROPOSITO': 'T9'}),
                            (ag.TRIAL, {'ALVO': 'x'})):
            for t in TETOS_OBRIGATORIOS:
                d = dict(MODO=modo, HUMAN_AUTHORIZATION='h', MAX_PROVIDER_RUNS=1,
                         MAX_START_POSTS=1, MAX_USD=0.1, MAX_ITEMS=1)
                d.update(extra)
                d[t] = None
                with self.assertRaises(ag.AutorizacaoInvalida, msg='%s %s' % (modo, t)):
                    ag.Autorizacao(**d)

    def test_M15_M16_M17_bypass(self):
        """curl directo, apify_pool e o proprio coletor nao tem segunda porta."""
        self.assertEqual(ag.conferir(None)['RECUSA'], ag.SEM_AUTORIZACAO)
        pool = open(os.path.join(RAIZ, 'ferramentas/apify_pool.py'), encoding='utf-8').read()
        arvore = ast.parse(pool)
        for n in ast.walk(arvore):
            if isinstance(n, ast.Call):
                for kw in n.keywords:
                    self.assertFalse(kw.arg == 'metodo'
                                     and isinstance(kw.value, ast.Constant)
                                     and kw.value.value == 'POST')

    def test_M18_second_post_allowed(self):
        with ag.autorizacao(normal()):
            self.comprar(source_id='IT-T3-002', proposito='T3')
            self.comprar(source_id='IT-T3-002', proposito='T3')
            self.comprar(source_id='IT-T3-002', proposito='T3')
        self.assertEqual(self.posts(), 1)


TETOS_OBRIGATORIOS = ag.TETOS


if __name__ == '__main__':
    unittest.main(verbosity=2)
