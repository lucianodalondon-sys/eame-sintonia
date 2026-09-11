#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.4 — A AQUISICAO DO INSTAGRAM ATRAVESSA O PORTAO CANONICO DE ROTAS.

A C9 mediu que a cadeia de Reel nao passava pelo mesmo portao que as outras
plataformas. A C10 estreitou a aquisicao — video inteiro virou so som — mas nao
tocou no encanamento: a cadeia continuava a entrar pela porta de servico.

    CAPACIDADE PROVADA NAO E CAPACIDADE AUTORIZADA. Quem prova que CONSEGUE
    nao respondeu ainda se PODE, e essas duas perguntas tem donos diferentes.

O QUE MUDOU, EM UMA LINHA
---------------------------
`instagram.reel.transcribe` deixou de se registar com `executa` e passou a
registar-se com `rota`. Na lingua desta casa isso nao e cosmetica:

    executa   nao ha porta a atravessar; a funcao monta o proprio trace.
    rota      ha porta; o roteador mede o portao ANTES de chamar seja o que for,
              e o trace nasce do registo que ele sela.

Ate aqui a nota que justificava `executa` era verdadeira — a matriz nao conhecia
nenhuma das tres capacidades de Reel. Agora conhece esta, porque o acto que ela
executa ja estava declarado e PERMITIDO sob outro nome: FETCH_TRANSCRIPT.

    UMA PORTA QUE EXISTIA POR NAO HAVER PORTAO NAO SOBREVIVE AO PORTAO.

TRES PALAVRAS QUE NAO SAO SINONIMOS
-------------------------------------
    NOT_DECLARED       ninguem mediu esta capacidade nesta plataforma.
    ROUTE_NOT_ALLOWED  mediram, e nenhuma rota viavel sobrou.
    ALLOWED            ha rota declarada, permitida e viavel.

Colapsar a primeira na segunda faz a casa dizer «nao pode» onde a verdade e
«ninguem sabe». Colapsar ao contrario e pior: transforma uma ausencia de
medicao numa autorizacao que ninguem deu.

O QUE ESTES TESTES MEDEM
-------------------------
O OBJETO e o ARGV, nunca o texto do ficheiro. Uma sentinela ancorada no texto
mede o texto, nao a lei.
"""
import ast
import io
import os
import shutil
import socket
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('ferramentas', 'leis', 'coleta', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import social_matriz as mz          # noqa: E402
import scrap_capacidades as cap     # noqa: E402
import scrap_registo as reg         # noqa: E402
import scrap_executor as scrap      # noqa: E402
import scrap_fornecedores as forn   # noqa: E402
import adaptador_instagram as ai    # noqa: E402
import reel_transcricao as rt       # noqa: E402

reg.carregar_adaptadores()

CAPACIDADE = 'instagram.reel.transcribe'
GROSSA = 'FETCH_TRANSCRIPT'
REEL = 'https://www.instagram.com/reel/DW6X5lZkU41/'
#: UM REEL SEM BYTES NO DISCO DESTA CASA.
#
# A cadeia reusa o que ja esta preservado — e bem, porque REUSAR != ADQUIRIR.
# Mas quem quer medir o PEDIDO tem de pedir algo que ainda nao esta ca: com o
# ficheiro em casa nao se chega a pedir nada, e o teste passaria a medir a
# gaveta em vez da rota.
REEL_SEM_BYTES = 'https://www.instagram.com/reel/C10AUDIOONLY4/' 


def _fonte(caminho):
    return io.open(os.path.join(RAIZ, caminho), encoding='utf-8').read()


class _SemRede:
    """Arma uma trava real no socket. Sair para a rede levanta, nao avisa."""

    def __init__(self):
        self.tentativas = []

    def __enter__(self):
        self._orig = socket.socket.connect
        tentativas = self.tentativas

        def _nao(sock, *a, **k):
            tentativas.append(a)
            raise AssertionError('a rota saiu para a rede: %r' % (a,))
        socket.socket.connect = _nao
        return self

    def __exit__(self, *_):
        socket.socket.connect = self._orig
        return False


class _PoliticaNegativa:
    """Poe a decisao em NAO sem escrever uma linha de politica no disco.

    Mexer no ficheiro para o teste passar seria o teste a escrever a lei que
    diz medir. Isto e um andaime de memoria, e o teardown desfaz.
    """

    def __init__(self, permitida='NAO', estado='ROUTE_NOT_ALLOWED'):
        self.permitida, self.estado = permitida, estado

    def __enter__(self):
        self._orig = mz.MATRIZ['INSTAGRAM'][GROSSA]
        mz.MATRIZ['INSTAGRAM'][GROSSA] = [
            dict(r, PERMITIDA=self.permitida, ESTADO=self.estado) for r in self._orig]
        return self

    def __exit__(self, *_):
        mz.MATRIZ['INSTAGRAM'][GROSSA] = self._orig
        return False


class _PoliticaPermissiva:
    """Poe a decisao em SIM sem escrever politica no disco.

    A C10.5D fechou a decisao humana: a aquisicao remota do Instagram esta
    RECUSADA. Os testes que medem o CAMINHO PERMITIDO nao deixaram de valer por
    isso — o que eles medem e se a capacidade tecnica continua inteira quando a
    lei diz sim.

        UM TESTE QUE DEIXA DE CORRER PORQUE A POLITICA MUDOU NAO MEDE A
        CAPACIDADE. MEDE A POLITICA, QUE JA TEM DONO.

    Por isso injectam SIM aqui, em memoria, e o ficheiro de politica continua a
    dizer NAO.
    """

    def __enter__(self):
        self._orig = mz.MATRIZ['INSTAGRAM'][GROSSA]
        mz.MATRIZ['INSTAGRAM'][GROSSA] = [
            dict(r, PERMITIDA='SIM', ESTADO='PROVED') for r in self._orig]
        return self

    def __exit__(self, *_):
        mz.MATRIZ['INSTAGRAM'][GROSSA] = self._orig
        return False


class _EspiaYtdlp:
    """Regista cada argv e nunca chama coisa nenhuma."""

    def __init__(self):
        self.chamadas = []

    def __call__(self, args, timeout=300):
        self.chamadas.append(list(args))

        class _R:
            returncode, stdout, stderr = 1, '', 'ERROR: espia'
        return _R


def _quem_escreve_permitida():
    """Os ficheiros que escrevem `PERMITIDA` — em qualquer das tres formas.

    Atribuicao (`PERMITIDA = ...`), argumento nomeado (`PERMITIDA=...`) e
    CHAVE DE DICIONARIO (`{'PERMITIDA': ...}`), que e a forma que a matriz usa
    e a que uma sonda distraida nao ve.
    """
    donos = []
    for raiz, dirs, fich in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in
                   ('node_modules', '.git', '__pycache__', 'BASELINE', 'data')]
        for f in fich:
            if not f.endswith('.py'):
                continue
            caminho = os.path.join(raiz, f)
            rel = os.path.relpath(caminho, RAIZ).replace(os.sep, '/')
            if rel.startswith('tests/'):
                continue
            try:
                arvore = ast.parse(io.open(caminho, encoding='utf-8').read(), caminho)
            except Exception:
                continue
            for n in ast.walk(arvore):
                alvos = ([n.target] if isinstance(n, ast.AnnAssign)
                         else list(getattr(n, 'targets', [])))
                if any(isinstance(t, ast.Name) and t.id == 'PERMITIDA' for t in alvos):
                    donos.append(rel)
                if isinstance(n, ast.keyword) and n.arg == 'PERMITIDA':
                    donos.append(rel)
                if isinstance(n, ast.Dict):
                    for k in n.keys:
                        if isinstance(k, ast.Constant) and k.value == 'PERMITIDA':
                            donos.append(rel)
    return sorted(set(donos))


# ══════════════════════════════════════════════════════════════════════════
# A DECISAO DE POLITICA — LIDA, NUNCA ESCRITA
# ══════════════════════════════════════════════════════════════════════════
class ODonoDaPoliticaEUmSo(unittest.TestCase):

    def test_a_decisao_do_instagram_esta_tomada_e_e_nao(self):
        # C10.5D · decisao humana. Ate aqui esta linha dizia SIM, e o teste
        # media isso. O que mudou nao foi a capacidade: foi a leitura do
        # `robots.txt` vivo de instagram.com.
        d = mz.decisao('INSTAGRAM', GROSSA)
        self.assertEqual(d['DECISAO'], mz.NAO_PERMITIDA)
        rotas = mz.MATRIZ['INSTAGRAM'][GROSSA]
        self.assertEqual(len(rotas), 1, 'nasceu rota nova em FETCH_TRANSCRIPT')
        self.assertEqual(rotas[0]['PERMITIDA'], 'NAO')
        self.assertEqual(rotas[0]['ESTADO'], 'ROUTE_NOT_ALLOWED')
        self.assertEqual(rotas[0]['CLASSE'], 'LOCAL_EXECUTOR')

    def test_a_decisao_e_de_rota_e_nao_rebaixa_a_capacidade(self):
        # O erro que esta casa nao pode cometer: transformar «nao podes sair»
        # em «nao sabes fazer». Sao donos diferentes e ficheiros diferentes.
        self.assertEqual(cap.estado('instagram.reel.transcribe'), 'PROVEN')
        self.assertTrue(cap.promete_resultado('instagram.reel.transcribe'))
        self.assertEqual(mz.decisao('INSTAGRAM', GROSSA)['DECISAO'], mz.NAO_PERMITIDA)

    def test_buscar_bytes_de_video_continua_por_declarar(self):
        # A cadeia mediu VIDEO_BYTES_DOWNLOADED = 0. Pedir autorizacao para o
        # que nao se faz seria alargar a superficie no papel.
        d = mz.decisao('INSTAGRAM', 'FETCH_VIDEO_BYTES')
        self.assertEqual(d['DECISAO'], mz.NAO_DECLARADA)
        self.assertNotIn('FETCH_VIDEO_BYTES', mz.MATRIZ['INSTAGRAM'])

    def test_as_tres_palavras_nao_se_confundem(self):
        self.assertNotEqual(mz.NAO_DECLARADA, mz.NAO_PERMITIDA)
        self.assertNotEqual(mz.NAO_PERMITIDA, mz.PERMITIDA_SIM)
        self.assertNotEqual(mz.NAO_DECLARADA, mz.PERMITIDA_SIM)
        # e cada uma tem um caso vivo na matriz, medido, nao inventado
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_VIDEO_BYTES')['DECISAO'],
                         mz.NAO_DECLARADA)
        self.assertEqual(mz.decisao('LINKEDIN', 'FETCH_POST')['DECISAO'],
                         mz.NAO_PERMITIDA)
        with _PoliticaPermissiva():
            self.assertEqual(mz.decisao('INSTAGRAM', GROSSA)['DECISAO'],
                             mz.PERMITIDA_SIM)

    def test_ler_a_decisao_nao_escreve_decisao(self):
        antes = [dict(r) for r in mz.MATRIZ['INSTAGRAM'][GROSSA]]
        for _ in range(3):
            mz.decisao('INSTAGRAM', GROSSA)
            mz.decisao('INSTAGRAM', 'FETCH_VIDEO_BYTES')
        self.assertEqual([dict(r) for r in mz.MATRIZ['INSTAGRAM'][GROSSA]], antes)

    def test_so_a_matriz_declara_permitida(self):
        # Um segundo lugar a responder «pode?» seria um segundo portao.
        #
        # E A SONDA TEM DE ENCONTRAR O DONO. A primeira versao desta busca
        # procurava `PERMITIDA` como alvo de atribuicao e como argumento
        # nomeado, e na matriz `PERMITIDA` e CHAVE DE DICIONARIO — logo
        # encontrava zero, incluindo o proprio dono, e chamava a isso um
        # passe.
        #
        #     UMA SONDA QUE ENCONTRA ZERO E DIZ «LIMPO» MEDE A SONDA.
        #
        # Por isso o teste exige o dono na lista: se a busca deixar de o ver,
        # falha aqui em vez de aprovar o vazio.
        donos = _quem_escreve_permitida()
        self.assertIn('leis/social_matriz.py', donos,
                      'a sonda deixou de encontrar o proprio dono da politica')
        self.assertEqual(donos, ['leis/social_matriz.py'],
                         'PERMITIDA passou a ser escrita fora do dono da politica')

# ══════════════════════════════════════════════════════════════════════════
# O ENCANAMENTO — A CAPACIDADE ENTRA PELO CAMINHO CANONICO
# ══════════════════════════════════════════════════════════════════════════
class OCaminhoCanonico(unittest.TestCase):

    def test_a_capacidade_fala_a_lingua_da_matriz(self):
        self.assertEqual(cap.da_matriz(CAPACIDADE), GROSSA)
        self.assertEqual(cap.pela_matriz('INSTAGRAM', GROSSA), CAPACIDADE)

    def test_a_capacidade_registou_se_com_rota_e_nao_com_executa(self):
        r = reg.adaptador_de('INSTAGRAM', CAPACIDADE)
        self.assertIsNotNone(r['ROTA'], 'sem `rota` o roteador nunca a despacha')
        self.assertIsNone(r['EXECUTA'],
                          '`executa` ao lado de `rota` e a porta de servico a '
                          'continuar aberta ao lado do portao')

    def test_o_executor_nao_encontra_atalho_e_vai_pelo_roteador(self):
        # `COLLECT` so desvia do roteador quando ha `executa`. Se isto voltar a
        # devolver funcao, o desvio voltou.
        self.assertIsNone(reg.executor_de('INSTAGRAM', CAPACIDADE))
        self.assertIsNotNone(reg.rota_de('INSTAGRAM', CAPACIDADE))
        self.assertTrue(reg.tem_caminho('INSTAGRAM', CAPACIDADE))

    def test_o_check_conhece_a_capacidade_da_matriz(self):
        v = scrap.CHECK('INSTAGRAM', CAPACIDADE)
        self.assertTrue(v['CAN'])
        self.assertEqual(v['MATRIZ_CAPABILITY'], GROSSA)
        self.assertEqual(v['ADAPTER'], 'adaptador_instagram')
        self.assertEqual(v['COST_TO_CHECK_USD'], 0.0)

    def test_o_adaptador_pergunta_ao_dono_e_nao_a_uma_tabela_propria(self):
        arvore = ast.parse(_fonte('coleta/adaptador_instagram.py'))
        chamadas = [n for n in ast.walk(arvore) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr == 'decisao']
        self.assertTrue(chamadas, 'o adaptador deixou de perguntar ao dono')
        self.assertTrue(all(isinstance(c.func.value, ast.Name)
                            and c.func.value.id == 'mz' for c in chamadas))

    def test_nao_nasceu_segundo_dono_de_politica_nem_segundo_roteador(self):
        proibidos = ('instagram_policy.py', 'scrap_policy_v2.py',
                     'route_gate_new.py', 'social_rotas_v2.py',
                     'scrap_executor_v2.py', 'social_matriz_v2.py')
        for nome in proibidos:
            for pasta in ('coleta', 'leis', 'guarda', 'ferramentas'):
                self.assertFalse(os.path.exists(os.path.join(RAIZ, pasta, nome)),
                                 '%s/%s nasceu' % (pasta, nome))


# ══════════════════════════════════════════════════════════════════════════
# A PROVA NEGATIVA — POLITICA DIZ NAO, E NADA SE MOVE
# ══════════════════════════════════════════════════════════════════════════
class PoliticaNegativaParaTudo(unittest.TestCase):
    """A recusa so morde quem ia mesmo sair.

    ESTES TESTES USAM `REEL_SEM_BYTES`, E ISSO NAO E DETALHE. Com a sentinela
    preservada, o degrau 0 encontra os bytes no disco e devolve `MEDIA_OK` sem
    tocar em rede nenhuma — o que e o comportamento CERTO e o que faria estes
    testes medirem a gaveta em vez do portao.

        UMA PROVA DE RECUSA QUE NUNCA CHEGA A PEDIR NAO MEDE A RECUSA.
    """

    def setUp(self):
        self.espia = _EspiaYtdlp()
        self._orig_ytdlp = rt._ytdlp
        rt._ytdlp = self.espia

    def tearDown(self):
        rt._ytdlp = self._orig_ytdlp

    def test_o_executor_recusa_sem_tocar_a_rede(self):
        with _PoliticaNegativa(), _SemRede() as rede:
            objetos, trace = scrap.COLLECT(
                platform='INSTAGRAM', capability=CAPACIDADE,
                run_id='C10-4-NEG', url=REEL)
        self.assertEqual(objetos, [])
        self.assertEqual(trace['RESULT'], 'ROUTE_NOT_ALLOWED')
        self.assertEqual(rede.tentativas, [])
        self.assertEqual(self.espia.chamadas, [], 'o yt-dlp correu apos um NAO')
        self.assertFalse(trace.get('PAID_PROVIDER_USED'))

    def test_a_recusa_nao_e_erro_nem_rejeicao_nem_desconhecido(self):
        # ERROR != REJECTED != UNKNOWN != NOT_RUN != ROUTE_NOT_ALLOWED.
        with _PoliticaNegativa(), _SemRede():
            _o, trace = scrap.COLLECT(platform='INSTAGRAM', capability=CAPACIDADE,
                                      run_id='C10-4-NEG-2', url=REEL)
        self.assertNotIn(trace['RESULT'], ('ERROR', 'REJECTED', 'UNKNOWN',
                                           'NOT_RUN', 'OK'))

    def test_chamar_o_adaptador_direto_tambem_bate_no_portao(self):
        # A porta de tras. Se so o roteador perguntasse, bastava nao usar o
        # roteador para a politica deixar de existir.
        #
        # O QUE MUDOU NA C10.5D: o adaptador deixou de PRE-RECUSAR. Ele delega,
        # e quem recusa e o portao que vive no ponto onde o socket abre. O
        # resultado observavel e o mesmo — zero rede, zero yt-dlp, a palavra
        # certa no trace — e o que se ganhou foi deixar de recusar quem trazia
        # os proprios bytes e nao ia sair.
        with _PoliticaNegativa(), _SemRede() as rede:
            objetos, trace = ai.capturar_reel(url=REEL_SEM_BYTES, run_id='C10-4-DIRETO',
                                              guardar=False)
        self.assertEqual(trace['RESULT'], mz.NAO_PERMITIDA)
        self.assertEqual(trace['POLICY_DECISION'], mz.NAO_PERMITIDA)
        self.assertFalse(trace['REMOTE_ACQUISITION_ALLOWED'])
        self.assertEqual(trace['POLICY_OWNER'], 'leis/social_matriz.py')
        self.assertEqual(rede.tentativas, [])
        self.assertEqual(self.espia.chamadas, [])
        # e a recusa nao veio disfarcada de transcricao vazia
        for o in objetos:
            self.assertEqual(o.get('MEDIA_STATE'), mz.NAO_PERMITIDA)
            self.assertIsNone(o.get('TRANSCRIPT_TEXT'))

    def test_a_recusa_diz_qual_das_tres_palavras_foi(self):
        with _PoliticaNegativa(), _SemRede():
            _o, t1 = ai.capturar_reel(url=REEL_SEM_BYTES, run_id='C10-4-P1')
        self.assertEqual(t1['RESULT'], mz.NAO_PERMITIDA)
        guardado = mz.MATRIZ['INSTAGRAM'].pop(GROSSA)
        try:
            with _SemRede():
                _o, t2 = ai.capturar_reel(url=REEL_SEM_BYTES, run_id='C10-4-P2')
        finally:
            mz.MATRIZ['INSTAGRAM'][GROSSA] = guardado
        self.assertEqual(t2['RESULT'], mz.NAO_DECLARADA)
        self.assertNotEqual(t1['RESULT'], t2['RESULT'],
                            'a casa passou a dizer a mesma palavra para «nao '
                            'pode» e para «ninguem mediu»')

    def test_o_adaptador_nao_pre_recusa_quem_talvez_nao_va_sair(self):
        # A C10.4 recusava aqui, antes do import da cadeia. A C10.5D mediu o
        # preco: um pedido que TRAZ os proprios bytes era recusado na mesma.
        #
        #     O PORTAO QUE RECUSA ANTES DE SABER SE VAI SAIR RECUSA TAMBEM
        #     QUEM NAO IA SAIR.
        #
        # Este teste fixa a correccao: com a politica em NAO, um pedido que
        # traz ficheiro proprio atravessa, sem rede nenhuma.
        tmp = tempfile.mkdtemp(prefix='c10-4-bytes-')
        try:
            proprio = os.path.join(tmp, 'proprio.m4a')
            io.open(proprio, 'wb').write(b'\x00' * 64)
            with _PoliticaNegativa(), _SemRede() as rede:
                objetos, trace = ai.capturar_reel(
                    ident={'PLATFORM': 'INSTAGRAM', 'POST_ID': 'PROPRIO',
                           'SOURCE_URL': 'https://www.instagram.com/reel/PROPRIO/'},
                    run_id='C10-4-BYTES', midia_ficheiro=proprio, guardar=False)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(len(objetos), 1,
                         'a politica de ROTA recusou trabalho que nao usa rota')
        self.assertEqual(objetos[0]['MEDIA_STATE'], 'MEDIA_OK')
        self.assertEqual(rede.tentativas, [])
        self.assertEqual(self.espia.chamadas, [])
        self.assertEqual(trace['POLICY_DECISION'], mz.NAO_PERMITIDA)

    def _retirado_test_o_portao_corre_antes_de_a_cadeia_sequer_ser_carregada(self):
        # Um portao que corre depois da rede nao e um portao: e um relatorio.
        # `reel_transcricao` traz o yt-dlp e o reconhecedor atras dele, logo o
        # proprio import ja e um compromisso — e por isso o que se mede aqui e
        # a ORDEM, no corpo da funcao, entre perguntar e carregar.
        arvore = ast.parse(_fonte('coleta/adaptador_instagram.py'))
        fn = next(n for n in ast.walk(arvore) if isinstance(n, ast.FunctionDef)
                  and n.name == 'capturar_reel')
        pergunta = carga = None
        for n in ast.walk(fn):
            linha = getattr(n, 'lineno', None)
            if linha is None:
                continue
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == 'politica' and pergunta is None):
                pergunta = linha
            if (isinstance(n, ast.Import)
                    and any(a.name == 'reel_transcricao' for a in n.names)
                    and carga is None):
                carga = linha
        self.assertIsNotNone(pergunta, 'o portao saiu de `capturar_reel`')
        self.assertIsNotNone(carga, 'a cadeia deixou de ser carregada aqui')
        self.assertLess(pergunta, carga,
                        'a cadeia e importada antes de a politica responder')

    def test_quem_responde_a_pergunta_e_o_dono_da_politica(self):
        arvore = ast.parse(_fonte('coleta/adaptador_instagram.py'))
        fn = next(n for n in ast.walk(arvore) if isinstance(n, ast.FunctionDef)
                  and n.name == 'politica')
        chamadas = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr == 'decisao'
                    and isinstance(n.func.value, ast.Name)
                    and n.func.value.id == 'mz']
        self.assertEqual(len(chamadas), 1,
                         '`politica()` deixou de perguntar ao dono da matriz')


# ══════════════════════════════════════════════════════════════════════════
# A PROVA POSITIVA — A ROTA PERMITIDA CHEGA, E CHEGA SO COM SOM
# ══════════════════════════════════════════════════════════════════════════
class RotaPermitidaChegaAoAdaptador(unittest.TestCase):

    def setUp(self):
        self.espia = _EspiaYtdlp()
        self._orig_ytdlp = rt._ytdlp
        rt._ytdlp = self.espia
        self.tmp = tempfile.mkdtemp(prefix='c10-4-')

    def tearDown(self):
        rt._ytdlp = self._orig_ytdlp
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a_rota_permitida_atravessa_e_o_registo_nomeia_quem_correu(self):
        with _PoliticaPermissiva(), _SemRede():
            objetos, trace = scrap.COLLECT(
                platform='INSTAGRAM', capability=CAPACIDADE, run_id='C10-4-POS',
                url=REEL, midia_ficheiro=os.path.join(self.tmp, 'nao-existe.m4a'),
                guardar=False)
        # o ficheiro nao existe de proposito: o que se mede aqui e o PERCURSO,
        # nao o resultado da transcricao.
        self.assertEqual(trace['CAPABILITY'], CAPACIDADE)
        medida = (trace.get('ROUTER_RECORD') or {}).get('MEDIDA') or {}
        self.assertEqual(medida.get('POLICY_OWNER'), 'leis/social_matriz.py')
        self.assertEqual(medida.get('IMPLEMENTACAO'),
                         'ferramentas/reel_transcricao.py')
        self.assertEqual(medida.get('ASR_OWNER'), 'ferramentas/fala_local.py')
        self.assertEqual(trace.get('COST_USD', 0.0), 0.0)
        self.assertFalse(trace.get('PAID_PROVIDER_USED'))
        self.assertEqual(len(objetos), 1)

    def test_depois_do_portao_o_pedido_continua_a_ser_so_de_som(self):
        with _PoliticaPermissiva(), _SemRede():
            scrap.COLLECT(platform='INSTAGRAM', capability=CAPACIDADE,
                          run_id='C10-4-AUDIO', url=REEL_SEM_BYTES, guardar=False)
        # `-J` e o pedido de METADADOS e nao traz byte de media nenhum. O que
        # esta lei mede e o pedido de MIDIA, que e o que carrega `-o`.
        midia = [a for a in self.espia.chamadas if '-o' in a]
        self.assertTrue(midia, 'a rota permitida nao chegou a pedir midia nenhuma')
        for argv in midia:
            self.assertIn('-f', argv, 'pedido sem seletor: o padrao traz video')
            self.assertEqual(argv[argv.index('-f') + 1], rt.SELETOR_SO_AUDIO)
        for argv in self.espia.chamadas:
            self.assertNotIn('bestvideo', ' '.join(argv))

    def test_falhar_o_audio_nao_autoriza_pedir_video(self):
        with _PoliticaPermissiva(), _SemRede():
            scrap.COLLECT(platform='INSTAGRAM', capability=CAPACIDADE,
                          run_id='C10-4-SEM-QUEDA', url=REEL_SEM_BYTES, guardar=False)
        for argv in [a for a in self.espia.chamadas if '-o' in a]:
            self.assertEqual(argv[argv.index('-f') + 1], rt.SELETOR_SO_AUDIO,
                             'houve pedido de midia com outro formato depois de '
                             'o audio falhar. Isso e a queda silenciosa para video.')


# ══════════════════════════════════════════════════════════════════════════
# O QUE O PORTAO NAO PODE TER MUDADO
# ══════════════════════════════════════════════════════════════════════════
class OPortaoNaoMudaOsOutrosContratos(unittest.TestCase):

    def test_o_reconhecedor_continua_a_ter_um_dono_so(self):
        donos = []
        for raiz, dirs, fich in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('node_modules', '.git', '__pycache__', 'BASELINE', 'data')]
            for f in fich:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), RAIZ)
                if rel.startswith('tests' + os.sep):
                    continue
                if 'WhisperModel(' in io.open(os.path.join(raiz, f),
                                              encoding='utf-8').read():
                    donos.append(rel)
        self.assertEqual(donos, ['ferramentas/fala_local.py'])

    def test_nenhum_fornecedor_pago_entra_nesta_rota(self):
        d = mz.decisao('INSTAGRAM', GROSSA)
        self.assertNotIn(d['CLASSE'], ('APIFY', 'OFFICIAL_API_PAID'))
        self.assertNotIn('apify', (d['ROTA'] or '').lower())
        self.assertEqual(forn.PAGOS, ('APIFY',))

    def test_o_adaptador_nao_julga_relevancia(self):
        # Portao de ROTA nao e portao TEMATICO. O SCRAP adquire e prova
        # procedencia; quem julga assunto e outra camada, e roda de graca
        # sobre o artefato.
        fonte = _fonte('coleta/adaptador_instagram.py').upper()
        for palavra in ('T3', 'T5', 'T9', 'RELEVANC', 'SOURCE_SCORE',
                        'AUTORIDADE', 'INFLUENC'):
            self.assertNotIn(palavra, fonte,
                             'o adaptador comecou a julgar: %s' % palavra)

    def test_as_outras_duas_capacidades_de_reel_continuam_sem_nome_na_matriz(self):
        # Traduzi-las tambem faria o registo nomear uma rota que nao e a delas,
        # e um trace que nomeia a rota errada mente com precisao de relojoeiro.
        self.assertIsNone(cap.da_matriz('instagram.reel.capture'))
        self.assertIsNone(cap.da_matriz('instagram.reel.audio'))

    def test_mas_elas_tambem_batem_no_portao(self):
        with _PoliticaNegativa(), _SemRede() as rede:
            objetos, trace = scrap.COLLECT(platform='INSTAGRAM',
                                           capability='instagram.reel.capture',
                                           run_id='C10-4-CAPTURE', url=REEL_SEM_BYTES,
                                           guardar=False)
        self.assertEqual(trace['RESULT'], mz.NAO_PERMITIDA)
        self.assertEqual(rede.tentativas, [])
        for o in objetos:
            self.assertEqual(o.get('MEDIA_STATE'), mz.NAO_PERMITIDA)


if __name__ == '__main__':
    unittest.main(verbosity=2)
