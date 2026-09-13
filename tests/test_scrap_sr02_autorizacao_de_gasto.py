# -*- coding: utf-8 -*-
"""SCRAP-SR-02 — a topologia da compra, e quem não se autoriza a si próprio.

⚠️ ESTA BATERIA ENCOLHEU NA SCRAP-OWNER-01, E A RAZÃO ESTÁ ESCRITA.

Ela media um modelo de autorização que era um DICIONÁRIO validado. Esse modelo
perdeu a convergência para o desta casa — selado, consumível, e a perguntar ao
dono da relevância. As sentinelas que mediam a FORMA do dicionário mediriam
hoje uma coisa que não existe, e por isso saíram; quem as substitui é
`tests/test_autorizacao_de_gasto.py`, a bateria do dono único.

    UMA SENTINELA QUE MEDE UM MODELO MORTO NÃO GUARDA NADA.
    ELA SÓ FAZ A SUÍTE DEMORAR MAIS.

O que fica aqui é o que NÃO dependia do modelo: a topologia (uma porta só),
quem fabrica autorização (ninguém), e as leis que moram no transporte.

    CREDENTIAL_PRESENT != SPEND_AUTHORIZED
    ROUTE_ALLOWED      != SPEND_AUTHORIZED
    BUDGET_PRESENT     != SPEND_AUTHORIZED
    TOKEN_OWNER        != SPEND_OWNER
    SOURCE_RELEVANCE_OWNER != SPEND_ENFORCER

Quarenta ataques. Todos têm de morrer, e cada recusa tem de chegar com o NOME
certo: achatar `NAO_AVALIADA` em `NOT_RELEVANT` inventaria um julgamento que
ninguém fez.

    FALTA DE AUTORIZAÇÃO É FALTA DE AUTORIZAÇÃO.
"""
import ast
import io
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', 'tests', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import autorizacao_de_gasto as az                                 # noqa: E402
import coletor as ct                                              # noqa: E402
import scrap_executor as sx                                       # noqa: E402
import scrap_http as http                                         # noqa: E402

ATOR = 'pintostudio~youtube-transcript-scraper'
FONTE = 'IT-T3-002'
PROP = 'T3'


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _funcao(rel, nome):
    for no in ast.walk(ast.parse(_fonte(rel))):
        if isinstance(no, ast.FunctionDef) and no.name == nome:
            return no
    raise AssertionError('%s não tem %s' % (rel, nome))


def _autorizacao(n=1):
    """Pede-se ao dono, como toda a gente."""
    return az.autorizar(
        motivo=az.TRIAL_DE_CAPACIDADE, proposito=PROP, max_execucoes=n,
        max_usd=0.10, quem_autorizou='bateria da topologia',
        porque='medir a porta contra um provider falso',
        condicao_de_paragem='as execucoes autorizadas')


class _Resultado(object):
    def __init__(self, corpo):
        self.returncode, self.stdout, self.stderr = 0, corpo, ''


class _Falsa(object):
    """`subprocess.run` do coletor — a camada mais funda. Conta os POSTs."""

    def __init__(self):
        self.posts = []

    def __call__(self, cmd, **k):
        url = cmd[-1]
        if '-X' in cmd and cmd[cmd.index('-X') + 1].upper() == 'POST':
            self.posts.append(url)
            return _Resultado(json.dumps({'data': {
                'id': 'R1', 'status': 'SUCCEEDED',
                'startedAt': '2026-09-12T00:00:00.000Z',
                'finishedAt': '2026-09-12T00:00:01.000Z',
                'defaultDatasetId': 'DS', 'usageTotalUsd': 0.01}}))
        if '/datasets/' in url:
            return _Resultado(json.dumps([{'url': 'u', 'transcript': 't',
                                           'chars': 1}]))
        return _Resultado(json.dumps({'data': {'id': 'R1',
                                               'status': 'SUCCEEDED',
                                               'usageTotalUsd': 0.01}}))


def comprar(**kw):
    """Corre a primitiva paga pelo caminho real. → (posts, estado).

    ⚠️ O `_curl` é REPOSTO ao da casa antes de cada compra, e a razão é um
    achado desta missão: `regras/sensor_coleta.py` substitui `coletor._curl`
    NO IMPORT. Basta uma bateria anterior importá-lo para o transporte mudar
    debaixo desta — e o falso, que finge `subprocess`, deixa de ser chamado.

        UMA SONDA QUE NÃO FIXA O TRANSPORTE MEDE QUEM IMPORTOU ANTES DELA.
    """
    falsa = _Falsa()
    real, curl = subprocess.run, ct._curl
    subprocess.run = falsa
    ct._curl = ct._CURL_DA_CASA
    try:
        with http.orcamento_de_rede(5), ct.orcamento_financeiro(1.0):
            ct.executar(ATOR, {'q': 1}, token='FALSO', run_id='t-sr02',
                        platform='YOUTUBE', country='IT', mission='SR-02',
                        query='q', source_version='v', evidence_path='/dev/null',
                        wait=60, salvar_raw=False, **kw)
        return len(falsa.posts), 'EXECUTOU'
    except az.SemAutorizacaoDeGasto as e:
        return len(falsa.posts), e.estado
    except Exception as e:                                        # noqa: BLE001
        return len(falsa.posts), type(e).__name__
    finally:
        subprocess.run, ct._curl = real, curl


class _SemCompra(unittest.TestCase):
    def nada(self, esperado=None, **kw):
        posts, estado = comprar(**kw)
        self.assertEqual(posts, 0, 'UMA COMPRA NASCEU: %s' % estado)
        if esperado:
            self.assertEqual(estado, esperado)
        return estado


# ══════════════════════════════════════════════════════════════════════════
# RT17–RT22 · NINGUÉM FABRICA A PRÓPRIA AUTORIZAÇÃO
# ══════════════════════════════════════════════════════════════════════════
class NinguemSeAutorizaASiProprio(unittest.TestCase):

    ONDE = ('coleta/adaptador_youtube.py', 'coleta/coletor.py',
            'ferramentas/apify_pool.py', 'coleta/social_rotas.py',
            'coleta/scrap_executor.py')

    def test_rt17_o_coletor_nao_julga_relevancia(self):
        """SOURCE_RELEVANCE_OWNER != SPEND_ENFORCER. Medido na ÁRVORE."""
        arv = ast.parse(_fonte('coleta/coletor.py'))
        for no in ast.walk(arv):
            if isinstance(no, (ast.Import, ast.ImportFrom)):
                nomes = ([a.name for a in no.names] if isinstance(no, ast.Import)
                         else [no.module or ''])
                for m in nomes:
                    self.assertNotIn((m or '').split('.')[0],
                                     ('relevancia_da_fonte', 'admissao'),
                                     'o dono do dinheiro importou o da relevância')
            if isinstance(no, ast.Call):
                nome = (no.func.attr if isinstance(no.func, ast.Attribute)
                        else getattr(no.func, 'id', None))
                self.assertNotIn(nome, ('portao', 'ler_livro', 'classificar'))

    def test_rt18_o_pool_de_chaves_nao_julga_nem_autoriza(self):
        """TOKEN_OWNER != SPEND_OWNER, medido e não presumido."""
        fonte = _fonte('ferramentas/apify_pool.py')
        for proibido in ('VEREDITO', 'AUTORIZA', 'relevancia', 'pode_comprar'):
            self.assertNotIn(proibido, fonte,
                             'o pool de chaves passou a decidir gasto: %s' % proibido)

    def test_rt19_nenhum_modulo_constroi_o_proprio_veredito(self):
        """Quem PEDE a compra não é quem a AUTORIZA."""
        for rel in self.ONDE:
            for no in ast.walk(ast.parse(_fonte(rel))):
                if not isinstance(no, ast.Dict):
                    continue
                chaves = {k.value for k in no.keys
                          if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                self.assertFalse(
                    {'VEREDITO', 'ESTADO_DA_RELEVANCIA'} <= chaves,
                    '%s fabrica um veredito de relevância' % rel)

    def test_rt20_o_adaptador_recebe_a_autorizacao_e_nao_a_inventa(self):
        no = _funcao('coleta/adaptador_youtube.py', 'youtube_legenda_paga')
        nomes = {a.arg for a in no.args.kwonlyargs}
        self.assertIn('autorizacao', nomes, 'o adaptador deixou de a receber')
        corpo = ast.unparse(no)
        self.assertNotIn("'VEREDITO'", corpo)
        self.assertNotIn('AUTORIZACAO_HUMANA', corpo)

    def test_rt21_o_default_da_primitiva_recusa(self):
        """FAIL CLOSED. Um chamador novo que não saiba desta lei não compra."""
        no = _funcao('coleta/coletor.py', 'executar')
        padrao = {a.arg: d for a, d in
                  zip(no.args.kwonlyargs, no.args.kw_defaults)}
        self.assertIn('autorizacao', padrao)
        self.assertIsInstance(padrao['autorizacao'], ast.Constant)
        self.assertIsNone(padrao['autorizacao'].value,
                          'o default da autorização deixou de ser None')

    def test_rt22_a_guarda_vem_antes_da_reserva_financeira(self):
        """Reservar antes comprometeria dinheiro por uma compra impensável.

        E uma reserva que ninguém liquidou não volta ao bolso.
        """
        no = _funcao('coleta/coletor.py', 'executar')
        linha_guarda = linha_reserva = None
        for n in ast.walk(no):
            if isinstance(n, ast.Call):
                nome = (n.func.attr if isinstance(n.func, ast.Attribute)
                        else getattr(n.func, 'id', None))
                if nome == 'conferir_e_consumir' and linha_guarda is None:
                    linha_guarda = n.lineno
                if nome == 'reservar' and linha_reserva is None:
                    linha_reserva = n.lineno
        self.assertIsNotNone(linha_guarda, 'a guarda desapareceu da primitiva')
        self.assertIsNotNone(linha_reserva)
        self.assertLess(linha_guarda, linha_reserva)


# ══════════════════════════════════════════════════════════════════════════
# RT37–RT42 · AS PORTAS TRASEIRAS
# ══════════════════════════════════════════════════════════════════════════
class AsPortasTraseiras(unittest.TestCase):

    def test_rt37_existe_uma_so_primitiva_de_criacao_paga(self):
        """Duas portas seriam duas guardas, e a segunda envelhecia calada."""
        achados = []
        for base, dirs, nomes in os.walk(RAIZ):
            dirs[:] = [d for d in dirs
                       if d not in {'.git', 'node_modules', 'italia-portale',
                                    '__pycache__', '.tmp', 'build', 'data',
                                    'handoff', 'tests', 'provas'}]
            for n in nomes:
                if not n.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(base, n), RAIZ)
                try:
                    arv = ast.parse(_fonte(rel))
                except SyntaxError:
                    continue
                for no in ast.walk(arv):
                    if isinstance(no, ast.Call) and any(
                            k.arg == 'metodo' and isinstance(k.value, ast.Constant)
                            and str(k.value.value).upper() == 'POST'
                            for k in no.keywords):
                        achados.append('%s:%d' % (rel.replace('\\', '/'), no.lineno))
        self.assertEqual(len(achados), 1,
                         'nasceu uma segunda porta de compra: %s' % achados)
        self.assertTrue(achados[0].startswith('coleta/coletor.py'), achados)

    def test_rt38_um_ajudante_de_teste_nao_compra_sem_autorizacao(self):
        """Este próprio ficheiro não consegue comprar por ser um teste."""
        with self.assertRaises(az.GastoRecusado) as c:
            ct.executar(ATOR, {'q': 1}, token='F', run_id='t',
                        platform='YOUTUBE', country='IT', mission='m',
                        query='q', source_version='v',
                        evidence_path='/dev/null', salvar_raw=False)
        self.assertEqual(c.exception.causa, 'AUTORIZACAO_AUSENTE')

    def test_rt39_a_cli_directa_pede_a_autorizacao_ao_dono(self):
        """A CLI não concede: ela traz o PEDIDO e leva-o a `autorizar()`."""
        import social_scrap as ss
        for fase, paga in ss.FASES_PAGAS.items():
            self.assertIn('PEDIDO_DE_AUTORIZACAO', paga,
                          'fase paga %s sem pedido de autorização' % fase)
            pedido = paga['PEDIDO_DE_AUTORIZACAO']
            for campo in ('motivo', 'max_execucoes', 'max_usd',
                          'quem_autorizou', 'porque', 'condicao_de_paragem'):
                self.assertIn(campo, pedido, '%s sem %s' % (fase, campo))
            # e o que sai de lá é selado, não um dicionário
            self.assertIsInstance(ss._autorizacao_da_fase(paga), az.Autorizacao)

    def test_rt40_o_subprocesso_curl_nao_salta_a_guarda(self):
        """O POST sai por `subprocess`, e a guarda está acima dele."""
        no = _funcao('coleta/coletor.py', 'executar')
        corpo = ast.unparse(no)
        self.assertLess(corpo.index('conferir_e_consumir'), corpo.index('_curl'),
                        'o curl passou a correr antes da guarda')

    def test_rt41_a_recusa_e_da_casa_e_nao_da_fonte(self):
        """Um teto que devolve FAILED faz o manifesto culpar a Apify."""
        self.assertIn(az.GastoRecusado, ct._recusas_nossas())

    def test_rt42_o_recibo_viaja_no_manifesto(self):
        """CAN DO != DID DO — e quem audita não tem de acreditar."""
        falsa = _Falsa()
        real, curl = subprocess.run, ct._curl
        subprocess.run = falsa
        ct._curl = ct._CURL_DA_CASA
        try:
            # ⚠️ O ORÇAMENTO É 0,10 E NÃO 1,00, E ISSO É LEI DESDE A RC-01.
            # `FINANCIAL_BUDGET.AUTHORIZED <= AUTORIZACAO.MAX_USD`: declarar
            # que esta execução pode comprometer um dólar sob uma autorização
            # de dez cêntimos é pedir nove vezes o que a pessoa concedeu.
            # O assunto deste teste é o recibo viajar no manifesto; o tamanho
            # do orçamento era incidental, e estava acima do autorizado.
            with http.orcamento_de_rede(5), ct.orcamento_financeiro(0.10):
                _i, man = ct.executar(
                    ATOR, {'q': 1}, token='F', run_id='t', platform='YOUTUBE',
                    country='IT', mission='m', query='q', source_version='v',
                    evidence_path='/dev/null', wait=60, salvar_raw=False,
                    autorizacao=_autorizacao(), proposito=PROP,
                    # O modo declara o MOTIVO, e a autorização é de TRIAL.
                    # Declarar NORMAL aqui seria pedir uma compra que ninguém
                    # autorizou — e a guarda recusa, que é o ponto.
                    modo=az.TRIAL, teto_usd=0.10)
        finally:
            subprocess.run, ct._curl = real, curl
        recibo = man.get('AUTORIZACAO_DE_GASTO') or {}
        self.assertEqual(recibo.get('VEREDITO'), az.AUTORIZADO)
        self.assertEqual(recibo.get('MOTIVO_DO_GASTO'), az.TRIAL_DE_CAPACIDADE)
        self.assertEqual(recibo.get('PROPOSITO'), PROP)
        self.assertEqual(recibo.get('CONTRATO'), az.CONTRATO)
        # E ele diz quantas execuções já se gastaram: o recibo de uma
        # autorização que não se gasta não prova que ela foi usada.
        self.assertEqual(recibo.get('EXECUCOES_GASTAS'), 1)


# ══════════════════════════════════════════════════════════════════════════
# RT43–RT45 · QUEM TROCA O TRANSPORTE LEVA AS LEIS COM ELE
# ══════════════════════════════════════════════════════════════════════════
class QuemTrocaOTransporteLevaAsLeis(unittest.TestCase):
    """Achado da SCRAP-SR-02, e é o mais silencioso de todos.

    `regras/sensor_coleta.py` faz `coletor._curl = _curl_robusto` NO IMPORT.
    A troca é legítima — o proxy deste ambiente derruba conexões e urllib
    sobrevive onde o subprocesso não sobrevive. O que não era legítimo é o que
    ela levava consigo: o teto de rede vive DENTRO de `_curl`, e a regra «o
    POST vai uma vez só» também. Bastava `import sensor_coleta` em qualquer
    ponto do processo para as duas sumirem da única porta que gasta dinheiro.

        UMA TROCA DE TRANSPORTE LEVA COM ELA AS LEIS QUE MORAVAM NO TRANSPORTE.

    E o `maxTotalChargeUsd` não cobria o buraco: ele limita CADA execução,
    nunca a soma das execuções que ninguém sabe que existem.
    """

    def _substituicoes(self):
        """→ os sítios que atribuem a `coletor._curl`, pela ÁRVORE."""
        fora = []
        for base, dirs, nomes in os.walk(RAIZ):
            dirs[:] = [d for d in dirs
                       if d not in {'.git', 'node_modules', 'italia-portale',
                                    '__pycache__', '.tmp', 'build', 'data'}]
            for n in nomes:
                if not n.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(base, n), RAIZ)
                try:
                    arv = ast.parse(_fonte(rel))
                except SyntaxError:
                    continue
                for no in ast.walk(arv):
                    if not isinstance(no, ast.Assign):
                        continue
                    for t in no.targets:
                        if (isinstance(t, ast.Attribute) and t.attr == '_curl'
                                and getattr(t.value, 'id', None) in ('coletor', 'ct')):
                            fora.append((rel.replace('\\', '/'),
                                         getattr(no.value, 'id', None)))
        return fora

    def test_rt43_toda_troca_de_transporte_e_conhecida(self):
        trocas = [t for t in self._substituicoes()
                  if not t[0].startswith(('tests/', 'provas/'))]
        self.assertEqual(trocas, [('regras/sensor_coleta.py', '_curl_robusto')],
                         'nasceu uma troca de transporte que ninguém mediu: %s'
                         % trocas)

    def test_rt44_o_transporte_trocado_reserva_do_teto_de_rede(self):
        """UM TETO QUE UM IMPORT APAGA NÃO É UM TETO."""
        no = _funcao('regras/sensor_coleta.py', '_curl_robusto')
        corpo = ast.unparse(no)
        self.assertIn('reservar', corpo,
                      'o transporte trocado deixou de contar para o teto de rede')
        self.assertIn('_orcamento_de_rede', corpo)

    def test_rt45_o_transporte_trocado_nao_repete_o_post(self):
        """REPETIR UM GET É BARATO. REPETIR UM POST É COMPRAR DE NOVO."""
        no = _funcao('regras/sensor_coleta.py', '_curl_robusto')
        corpo = ast.unparse(no)
        self.assertIn("'POST'", corpo,
                      'o transporte trocado voltou a tratar POST como GET')
        self.assertIn('PostTalvezCriado', corpo,
                      'um POST perdido deixou de avisar que pode ter nascido')
        # e o original continua a dizer o mesmo, com nome
        self.assertTrue(hasattr(ct, '_CURL_DA_CASA'),
                        'o coletor deixou de guardar o próprio transporte')


# ══════════════════════════════════════════════════════════════════════════
# RT46–RT52 · O QUE A MUTAÇÃO ENCONTROU SEM GUARDA
# ══════════════════════════════════════════════════════════════════════════
class OQueAMutacaoEncontrou(unittest.TestCase):
    """⚠️ ESTA CLASSE NASCEU DE CINCO MUTANTES QUE SOBREVIVERAM.

    Trocar o mapa entre os dois eixos, deixar um dicionário passar por
    autorização, voltar a chamar o contrato `v1` — nenhuma dessas mudanças
    partia uma sentinela, e todas partiam uma lei.

        UM MUTANTE QUE SOBREVIVE NÃO ACUSA O CÓDIGO: ACUSA A BATERIA.
    """

    def test_rt46_o_mapa_entre_os_dois_eixos_e_este_e_nao_outro(self):
        """O único sítio onde o modo vira motivo. Trocar uma linha aqui faria
        uma coleta normal comprar com autorização de ensaio."""
        self.assertEqual(az.MOTIVO_DO_MODO, {
            az.NORMAL: az.COLETA_NORMAL,
            az.PROBE: az.PROVA_DE_RELEVANCIA,
            az.TRIAL: az.TRIAL_DE_CAPACIDADE,
        })
        # e a tradução é bijectiva: dois modos com o mesmo motivo fariam um
        # deles herdar as excepções do outro.
        self.assertEqual(len(set(az.MOTIVO_DO_MODO.values())), len(az.MODOS))

    def test_rt47_cada_modo_traduz_para_o_seu_e_so_o_seu(self):
        for modo, motivo in az.MOTIVO_DO_MODO.items():
            self.assertEqual(az.motivo_do_modo(modo), motivo)
        with self.assertRaises(az.AutorizacaoInvalida):
            az.motivo_do_modo('LIVRE')

    def test_rt48_um_dicionario_nao_e_uma_autorizacao(self):
        """CAMPO PREENCHIDO PELO CHAMADOR != AUTORIZACAO."""
        forjada = {'MOTIVO_DO_GASTO': az.TRIAL_DE_CAPACIDADE, 'PROPOSITO': PROP,
                   'SOURCE_ID': FONTE, 'MAX_EXECUCOES': 99, 'MAX_USD': 99.0,
                   'VEREDITO': az.AUTORIZADO}
        with self.assertRaises(az.GastoRecusado) as c:
            az.conferir_e_consumir(forjada, motivo=az.TRIAL_DE_CAPACIDADE,
                                   proposito=PROP, teto_usd=0.10)
        self.assertEqual(c.exception.causa, 'AUTORIZACAO_FABRICADA')

    def test_rt48b_e_a_PORTA_tambem_recusa_o_dicionario(self):
        """⚠️ RT48 media a LEI. Este mede a PORTA.

        O mutante que repunha a API antiga acrescentava um ramo em
        `coletor.executar` — «se for dicionário, aceita» — e sobrevivia, porque
        nenhuma sentinela atravessava a porta com um dicionário na mão.

            MEDIR A LEI NÃO É MEDIR QUEM A CHAMA.
        """
        forjada = {'MOTIVO_DO_GASTO': az.TRIAL_DE_CAPACIDADE, 'PROPOSITO': PROP,
                   'MAX_EXECUCOES': 99, 'MAX_USD': 99.0,
                   'VEREDITO': az.AUTORIZADO}
        with self.assertRaises(az.GastoRecusado) as c:
            ct.executar(ATOR, {'q': 1}, token='F', run_id='t',
                        platform='YOUTUBE', country='IT', mission='m',
                        query='q', source_version='v', evidence_path='/dev/null',
                        salvar_raw=False, autorizacao=forjada, proposito=PROP,
                        modo=az.TRIAL, teto_usd=0.10)
        self.assertEqual(c.exception.causa, 'AUTORIZACAO_FABRICADA')

    def test_rt49_nem_um_objecto_com_a_mesma_forma(self):
        """Um sósia com os mesmos campos também não passa."""
        class Sosia(object):
            motivo = az.TRIAL_DE_CAPACIDADE
            proposito = PROP
            source_id = None
            max_usd = 99.0
            restantes = 99
            _selo = object()
            _gastas = 0
        with self.assertRaises(az.GastoRecusado) as c:
            az.conferir_e_consumir(Sosia(), motivo=az.TRIAL_DE_CAPACIDADE,
                                   proposito=PROP, teto_usd=0.10)
        self.assertEqual(c.exception.causa, 'AUTORIZACAO_FABRICADA')

    def test_rt50_nem_uma_copia_serializada(self):
        """Passar por JSON tira-lhe o selo, e o selo é o que a torna dela."""
        import copy
        import json
        a = _autorizacao()
        plano = json.loads(json.dumps(a.para_o_manifesto()))
        with self.assertRaises(az.GastoRecusado):
            az.conferir_e_consumir(plano, motivo=az.TRIAL_DE_CAPACIDADE,
                                   proposito=PROP, teto_usd=0.10)
        # e uma cópia profunda CONTINUA a ser a mesma autorização — ela não
        # multiplica execuções por ser copiada, porque o saldo vai com ela.
        b = copy.deepcopy(a)
        self.assertEqual(b.restantes, a.restantes)

    def test_rt51_o_contrato_tem_UM_nome_e_ele_nao_e_o_ambiguo(self):
        """`v1` nomeou dois comportamentos incompatíveis nesta casa."""
        self.assertEqual(az.CONTRATO, 'AUTORIZACAO_DE_GASTO/v2')
        self.assertNotEqual(az.CONTRATO, az.CONTRATO_AMBIGUO_ANTERIOR)
        self.assertEqual(az.CONTRATO_AMBIGUO_ANTERIOR, 'AUTORIZACAO_DE_GASTO/v1')

    def test_rt52_existe_um_so_dono_do_conceito(self):
        """SPEND_AUTH_OWNER_COUNT = 1, medido na árvore."""
        donos = []
        for base, dirs, nomes in os.walk(RAIZ):
            dirs[:] = [d for d in dirs
                       if d not in {'.git', 'node_modules', 'italia-portale',
                                    '__pycache__', '.tmp', 'build', 'data'}]
            for n in nomes:
                if not n.endswith('.py'):
                    continue
                rel_ = os.path.relpath(os.path.join(base, n), RAIZ)
                if rel_.startswith(('tests/', 'provas/')):
                    continue
                t = _fonte(rel_)
                if 'def conferir_e_consumir' in t or 'def pode_comprar' in t:
                    donos.append(rel_.replace('\\', '/'))
        self.assertEqual(donos, ['leis/autorizacao_de_gasto.py'],
                         'SPEND_AUTH_OWNER_COUNT != 1: %s' % donos)


if __name__ == '__main__':
    unittest.main(verbosity=2)
