# -*- coding: utf-8 -*-
"""SCRAP-SR-02 — nenhuma compra sem autorização.

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


def sim(sid=FONTE, prop=PROP):
    """O veredito que o dono da relevância devolveria. Construído AQUI —
    e é essa a prova de que esta linhagem não o calcula."""
    return {'VEREDITO': az.AUTORIZA, 'SOURCE_ID': sid, 'PROPOSITO': prop,
            'ESTADO_DA_RELEVANCIA': az.SIM, 'VERSAO_DO_PORTAO': '1',
            'CONTRATO': 'RELEVANCIA_DA_FONTE/v1',
            'DECISAO': {'EVIDENCIA': {'F': 'LIVRO'}}}


LIMITES = {'AUTORIZACAO_HUMANA': 'bateria SR-02', 'MAX_PROVIDER_RUNS': 1,
           'MAX_START_POSTS': 1, 'MAX_USD': 0.10}
LIMITES_PROBE = dict(LIMITES, MAX_ITEMS=10)


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
# RT1–RT8 · TER NÃO É PODER
# ══════════════════════════════════════════════════════════════════════════
class TerNaoEPoder(_SemCompra):

    def test_rt01_chamada_directa_sem_autorizacao(self):
        """Um script que chama a primitiva não compra por chamar."""
        self.nada(az.SEM_AUTORIZACAO)

    def test_rt02_workflow_sem_autorizacao(self):
        """Nenhum workflow constrói autorização no YAML.

        Se construísse, o teto e a permissão viviam num campo de formulário —
        e um teto que vive no disparador é um teto que quem dispara escolhe.

        ⚠️ A primeira versão leu o ficheiro inteiro e acusou `system-map.yml`,
        cujo comentário em português usa a palavra «veredito» a falar das
        provas do mapa.

            UMA SONDA QUE LÊ A PROSA ENCONTRA A PALAVRA ONDE ELA NÃO DECIDE NADA.

        Lê-se o DOCUMENTO, sem comentários.
        """
        import glob
        import re
        for w in sorted(glob.glob(os.path.join(RAIZ, '.github/workflows/*.yml'))):
            bruto = _fonte(os.path.relpath(w, RAIZ))
            y = '\n'.join(re.sub(r'(?<!\$)#.*$', '', l) for l in bruto.splitlines())
            for inventado in ('VEREDITO', 'ESTADO_DA_RELEVANCIA',
                              'AUTORIZACAO_HUMANA', 'MAX_USD',
                              'MAX_PROVIDER_RUNS'):
                self.assertNotIn(inventado, y,
                                 '%s fabrica autorização' % os.path.basename(w))

    def test_rt03_token_presente_nao_autoriza(self):
        """TOKEN_OWNER != SPEND_OWNER. Ter a chave não é ter licença."""
        import apify_pool as ap
        self.assertTrue(hasattr(ap, 'pool'))
        self.nada(az.SEM_AUTORIZACAO)      # token existe; compra não nasce

    def test_rt04_orcamento_presente_nao_autoriza(self):
        """BUDGET_PRESENT != SPEND_AUTHORIZED. Os dois tetos estão abertos."""
        estado = self.nada()
        self.assertEqual(estado, az.SEM_AUTORIZACAO)

    def test_rt05_politica_permitida_sem_relevancia(self):
        """ROUTE_ALLOWED != SPEND_AUTHORIZED."""
        self.nada(az.SEM_AUTORIZACAO, modo=az.NORMAL, source_id=FONTE,
                  proposito=PROP)

    def test_rt06_relevancia_sim_ainda_atravessa_os_outros_portoes(self):
        """A autorização não substitui nada: ela vem ANTES de todos."""
        falsa = _Falsa()
        real, curl = subprocess.run, ct._curl
        subprocess.run = falsa
        ct._curl = ct._CURL_DA_CASA
        try:
            with http.orcamento_de_rede(0):
                with self.assertRaises(http.SemOrcamentoDeRede):
                    ct.executar(ATOR, {'q': 1}, token='F', run_id='t',
                                platform='YOUTUBE', country='IT', mission='m',
                                query='q', source_version='v',
                                evidence_path='/dev/null', wait=60,
                                salvar_raw=False, modo=az.NORMAL,
                                autorizacao=sim(), source_id=FONTE,
                                proposito=PROP)
        finally:
            subprocess.run, ct._curl = real, curl
        self.assertEqual(len(falsa.posts), 0)

    def test_rt07_sim_de_t3_usado_em_t9(self):
        self.nada(az.PROPOSITO_ERRADO, modo=az.NORMAL, autorizacao=sim(),
                  source_id=FONTE, proposito='T9')

    def test_rt08_autorizacao_da_fonte_a_usada_na_fonte_b(self):
        self.nada(az.FONTE_ERRADA, modo=az.NORMAL, autorizacao=sim(),
                  source_id='IT-T3-999', proposito=PROP)


# ══════════════════════════════════════════════════════════════════════════
# RT9–RT16 · AS AUSÊNCIAS NÃO VIRAM «SIM», E NÃO VIRAM «NÃO»
# ══════════════════════════════════════════════════════════════════════════
class AsAusenciasNaoViramSim(_SemCompra):

    def _com(self, estado_rel, veredito=az.EXIGE_AVALIACAO):
        return dict(modo=az.NORMAL, source_id=FONTE, proposito=PROP,
                    autorizacao=dict(sim(), VEREDITO=veredito,
                                     ESTADO_DA_RELEVANCIA=estado_rel))

    def test_rt09_autorizacao_sem_proposito_no_pedido(self):
        self.nada(az.PROPOSITO_ERRADO, modo=az.NORMAL, autorizacao=sim(),
                  source_id=FONTE, proposito=None)

    def test_rt10_nao_sei_nao_vira_allowed(self):
        self.nada(az.RELEVANCIA_INCERTA, **self._com(az.NAO_SEI))

    def test_rt11_erro_nao_vira_allowed(self):
        self.nada(az.RELEVANCIA_COM_ERRO, **self._com(az.ERRO))

    def test_rt12_nao_avaliada_nao_vira_allowed(self):
        self.nada(az.RELEVANCIA_POR_AVALIAR, **self._com(az.NAO_AVALIADA))

    def test_rt12b_as_quatro_ausencias_nao_colapsam_num_nome_so(self):
        """NOT_MEASURED != NOT_RELEVANT. Quatro confissões, quatro nomes."""
        nomes = {self.nada(**self._com(e))
                 for e in (az.NAO_SEI, az.ERRO, az.NAO_AVALIADA)}
        nomes.add(self.nada(**self._com(az.NAO, veredito=az.BARRA)))
        self.assertEqual(len(nomes), 4, 'duas ausências deram o mesmo nome')
        self.assertIn(az.RELEVANCIA_BARRADA, nomes)

    def test_rt13_url_vira_source_id(self):
        self.nada(az.SOURCE_ID_E_URL, modo=az.NORMAL,
                  autorizacao=sim(sid='https://arpa.it'),
                  source_id='https://arpa.it', proposito=PROP)

    def test_rt13b_source_id_ausente(self):
        self.nada(az.SOURCE_ID_AUSENTE, modo=az.NORMAL, autorizacao=sim(),
                  source_id=None, proposito=PROP)

    def test_rt14_veredito_autoriza_com_estado_que_nao_e_sim(self):
        """O ataque mais fino: carimbar AUTORIZA sobre NAO_AVALIADA."""
        self.nada(az.RELEVANCIA_POR_AVALIAR, modo=az.NORMAL, source_id=FONTE,
                  proposito=PROP,
                  autorizacao=dict(sim(), ESTADO_DA_RELEVANCIA=az.NAO_AVALIADA))

    def test_rt15_estado_sim_com_veredito_que_nao_autoriza(self):
        self.nada(modo=az.NORMAL, source_id=FONTE, proposito=PROP,
                  autorizacao=dict(sim(), VEREDITO=az.BARRA))

    def test_rt16_autorizacao_sem_os_campos_do_contrato(self):
        for campo in az.CAMPOS_DA_AUTORIZACAO:
            magra = {k: v for k, v in sim().items() if k != campo}
            self.nada(az.CONTRATO_ERRADO, modo=az.NORMAL, autorizacao=magra,
                      source_id=FONTE, proposito=PROP)


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
                if nome == 'pode_comprar' and linha_guarda is None:
                    linha_guarda = n.lineno
                if nome == 'reservar' and linha_reserva is None:
                    linha_reserva = n.lineno
        self.assertIsNotNone(linha_guarda, 'a guarda desapareceu da primitiva')
        self.assertIsNotNone(linha_reserva)
        self.assertLess(linha_guarda, linha_reserva)


# ══════════════════════════════════════════════════════════════════════════
# RT23–RT30 · PROBE É LIMITADO, E NÃO PROMOVE NADA
# ══════════════════════════════════════════════════════════════════════════
class OProbeELimitado(_SemCompra):

    def test_rt23_probe_autorizado_corre_uma_vez(self):
        posts, estado = comprar(modo=az.PROBE, autorizacao=LIMITES_PROBE)
        self.assertEqual((posts, estado), (1, 'EXECUTOU'))

    def test_rt24_probe_sem_autorizacao_humana(self):
        magro = {k: v for k, v in LIMITES_PROBE.items()
                 if k != 'AUTORIZACAO_HUMANA'}
        self.nada(az.LIMITE_AUSENTE, modo=az.PROBE, autorizacao=magro)

    def test_rt25_probe_sem_max_usd(self):
        magro = {k: v for k, v in LIMITES_PROBE.items() if k != 'MAX_USD'}
        self.nada(az.LIMITE_AUSENTE, modo=az.PROBE, autorizacao=magro)

    def test_rt26_probe_sem_max_provider_runs(self):
        magro = {k: v for k, v in LIMITES_PROBE.items()
                 if k != 'MAX_PROVIDER_RUNS'}
        self.nada(az.LIMITE_AUSENTE, modo=az.PROBE, autorizacao=magro)

    def test_rt27_probe_sem_max_items(self):
        magro = {k: v for k, v in LIMITES_PROBE.items() if k != 'MAX_ITEMS'}
        self.nada(az.LIMITE_AUSENTE, modo=az.PROBE, autorizacao=magro)

    def test_rt27b_probe_sem_max_start_posts(self):
        magro = {k: v for k, v in LIMITES_PROBE.items()
                 if k != 'MAX_START_POSTS'}
        self.nada(az.LIMITE_AUSENTE, modo=az.PROBE, autorizacao=magro)

    def test_rt28_limite_zero_nao_e_ilimitado(self):
        """Zero não é «sem teto». É «não pode»."""
        for campo in ('MAX_USD', 'MAX_PROVIDER_RUNS', 'MAX_ITEMS'):
            self.nada(az.LIMITE_AUSENTE, modo=az.PROBE,
                      autorizacao=dict(LIMITES_PROBE, **{campo: 0}))

    def test_rt29_probe_nao_promove_relevancia(self):
        """PROBE != DECISION. Quem escreve no livro é o dono do livro."""
        recibo = az.pode_comprar(modo=az.PROBE, autorizacao=LIMITES_PROBE)
        self.assertIs(recibo['PROMOTES_RELEVANCE'], False)
        self.assertIs(recibo['SOURCE_RELEVANCE_CONSULTED'], False)
        fonte = _fonte('leis/autorizacao_de_gasto.py')
        for escrita in ('registar(', 'ler_livro(', 'open(LIVRO'):
            self.assertNotIn(escrita, fonte, 'a guarda escreve no livro')

    def test_rt30_a_guarda_nao_le_livro_nenhum(self):
        """O spend boundary não abre o LIVRO-DE-RELEVANCIA."""
        arv = ast.parse(_fonte('leis/autorizacao_de_gasto.py'))
        for no in ast.walk(arv):
            if isinstance(no, ast.Call):
                nome = (no.func.attr if isinstance(no.func, ast.Attribute)
                        else getattr(no.func, 'id', None))
                self.assertNotIn(nome, ('open', 'load', 'loads', 'urlopen',
                                        'run', 'listdir'),
                                 'a guarda foi ler alguma coisa: %s' % nome)


# ══════════════════════════════════════════════════════════════════════════
# RT31–RT36 · NORMAL NÃO SE VESTE DE OUTRA COISA
# ══════════════════════════════════════════════════════════════════════════
class NormalNaoSeVesteDeOutraCoisa(_SemCompra):

    def test_rt31_normal_muda_para_trial_sem_limites(self):
        self.nada(az.LIMITE_AUSENTE, modo=az.TRIAL, autorizacao=sim(),
                  source_id=FONTE, proposito=PROP)

    def test_rt32_normal_muda_para_probe_sem_limites(self):
        self.nada(az.LIMITE_AUSENTE, modo=az.PROBE, autorizacao=sim(),
                  source_id=FONTE, proposito=PROP)

    def test_rt33_modo_inventado_nao_passa(self):
        self.nada(az.SEM_AUTORIZACAO, modo='LIVRE', autorizacao=LIMITES)

    def test_rt34_trial_sem_autorizacao_humana(self):
        self.nada(az.SEM_AUTORIZACAO, modo=az.TRIAL, autorizacao=None)

    def test_rt35_trial_continua_a_nao_autorizar_gasto_sozinho(self):
        """A lei antiga dizia TRIAL NÃO AUTORIZA GASTO. Continua a dizer."""
        self.assertIn('TRIAL NÃO AUTORIZA GASTO',
                      _fonte('coleta/scrap_executor.py'))

    def test_rt36_os_tres_modos_sao_tres_e_tem_um_dono(self):
        """ONE CONCEPT → ONE OWNER: uma lista, num sítio."""
        self.assertEqual(az.MODOS, ('NORMAL', 'TRIAL', 'PROBE'))
        self.assertIs(sx.MODOS, az.MODOS)
        arv = ast.parse(_fonte('coleta/scrap_executor.py'))
        literais = [n for n in ast.walk(arv)
                    if isinstance(n, ast.Assign)
                    and any(getattr(t, 'id', None) == 'MODOS' for t in n.targets)]
        self.assertEqual(literais, [], 'o executor voltou a declarar MODOS')


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
        posts, estado = comprar()
        self.assertEqual((posts, estado), (0, az.SEM_AUTORIZACAO))

    def test_rt39_a_cli_directa_nao_compra_sem_autorizacao(self):
        """A CLI canónica só carrega autorização para fases declaradas."""
        import social_scrap as ss
        for fase, paga in ss.FASES_PAGAS.items():
            self.assertIn('AUTORIZACAO_DE_GASTO', paga,
                          'fase paga %s sem autorização' % fase)
            for campo in az.CAMPOS_DO_LIMITE:
                self.assertIn(campo, paga['AUTORIZACAO_DE_GASTO'],
                              '%s sem %s' % (fase, campo))

    def test_rt40_o_subprocesso_curl_nao_salta_a_guarda(self):
        """O POST sai por `subprocess`, e a guarda está acima dele."""
        no = _funcao('coleta/coletor.py', 'executar')
        corpo = ast.unparse(no)
        self.assertLess(corpo.index('pode_comprar'), corpo.index('_curl'),
                        'o curl passou a correr antes da guarda')

    def test_rt41_a_recusa_e_da_casa_e_nao_da_fonte(self):
        """Um teto que devolve FAILED faz o manifesto culpar a Apify."""
        self.assertIn(az.SemAutorizacaoDeGasto, ct._recusas_nossas())

    def test_rt42_o_recibo_viaja_no_manifesto(self):
        """CAN DO != DID DO — e quem audita não tem de acreditar."""
        falsa = _Falsa()
        real, curl = subprocess.run, ct._curl
        subprocess.run = falsa
        ct._curl = ct._CURL_DA_CASA
        try:
            with http.orcamento_de_rede(5), ct.orcamento_financeiro(1.0):
                _i, man = ct.executar(
                    ATOR, {'q': 1}, token='F', run_id='t', platform='YOUTUBE',
                    country='IT', mission='m', query='q', source_version='v',
                    evidence_path='/dev/null', wait=60, salvar_raw=False,
                    modo=az.NORMAL, autorizacao=sim(), source_id=FONTE,
                    proposito=PROP)
        finally:
            subprocess.run, ct._curl = real, curl
        recibo = man.get('SPEND_AUTHORIZATION') or {}
        self.assertEqual(recibo.get('BASIS'), 'SOURCE_RELEVANCE')
        self.assertEqual(recibo.get('SOURCE_ID'), FONTE)
        self.assertEqual(recibo.get('PROPOSITO'), PROP)
        self.assertIs(recibo.get('PROMOTES_RELEVANCE'), False)


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
