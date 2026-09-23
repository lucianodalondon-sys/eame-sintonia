#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.5D — A DECISAO DO INSTAGRAM, E AS TRES VERDADES QUE ELA NAO PODE COLAPSAR.

    INSTAGRAM_REMOTE_ACQUISITION = ALLOWED (D22, 2026-09-23)  ← MUDOU
    INSTAGRAM_LOCAL_ASR          = PROVEN
    REUSE_OF_PRESERVED_MEDIA     = ALLOWED

As tres sao verdadeiras ao mesmo tempo. Escrever «Instagram = bloqueado» juntava
as tres numa so e perdia duas.

⚠️ O QUE MUDOU NA TERCEIRA LINHA, E PORQUE NAO E UM AFROUXAMENTO (D22)
---------------------------------------------------------------------
Esta secao dizia `INSTAGRAM_REMOTE_ACQUISITION = NOT_ALLOWED`, por decisao humana
da C10.5D tomada sobre o `robots.txt` vivo de instagram.com (`Disallow: /`).

    A LEITURA NAO MUDOU. MUDOU QUEM ASSUME O RISCO.

O dono do projeto autorizou nomeadamente a coleta de REELS do Instagram POR URL
DIRECTA, sem login, sem conta e sem rota paga, com o risco assumido por ele (D22,
2026-09-23) — como a D17.4 fez com o som do YouTube. A rota passou a declarar os
tres eixos (`OWNER_AUTHORIZED = SIM`, `PLATFORM_POLICY_STATUS = DISALLOWED` — a
medicao continua escrita — e `LIMITE = PUBLIC_REEL_BY_URL_ONLY`).

    MEDIR A POLITICA NAO E OBEDECER-LHE: E SABER O QUE SE ASSUME.

E o que estes testes passam a medir NAO e «a lei diz sim»: e que o PORTAO decide
nos DOIS sentidos, que as tres verdades continuam separadas, e que a recusa nao
se disfarca de falta de midia nem a falta de midia de recusa.

    CAN DO != MAY DO != DID DO.   REUSAR != ADQUIRIR.

O QUE ESTA MISSAO CORRIGIU NA C10.4
-------------------------------------
A C10.4 recusava no adaptador, antes do import da cadeia. Medido aqui: isso
recusava tambem um pedido que TRAZIA os proprios bytes e nao ia sair para lado
nenhum.

    O PORTAO QUE RECUSA ANTES DE SABER SE VAI SAIR RECUSA TAMBEM QUEM NAO IA
    SAIR.

Quem decide e o portao que vive no ponto onde o socket abre. E ele nao mudou de
regra ao mudar de altitude: mudou de momento.

UMA NOTA SOBRE ESTES TESTES
-----------------------------
Os que medem RECUSA usam um Reel SEM bytes nesta casa. Com a sentinela
preservada o degrau 0 encontra-a no disco e devolve `MEDIA_OK` sem rede
nenhuma — comportamento certo, e que faria o teste medir a gaveta.

    UMA PROVA DE RECUSA QUE NUNCA CHEGA A PEDIR NAO MEDE A RECUSA.
"""
import ast
import io
import os
import socket
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('ferramentas', 'leis', 'coleta', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import social_matriz as mz          # noqa: E402
import scrap_capacidades as cap     # noqa: E402
import scrap_fornecedores as forn   # noqa: E402
import fala_local as fl             # noqa: E402
import reel_transcricao as rt       # noqa: E402
import adaptador_instagram as ai    # noqa: E402

GROSSA = 'FETCH_TRANSCRIPT'
#: Um Reel que NAO tem bytes nesta casa. Ver a nota do modulo.
SEM_BYTES = {'PLATFORM': 'INSTAGRAM', 'POST_ID': 'C105DSENTINELA',
             'SOURCE_URL': 'https://www.instagram.com/reel/C105DSENTINELA/'}


class _SemRede:
    def __enter__(self):
        self.tentativas = []
        self._orig = socket.socket.connect
        tent = self.tentativas

        def _nao(sock, *a, **k):
            tent.append(a)
            raise AssertionError('saiu para a rede: %r' % (a,))
        socket.socket.connect = _nao
        return self

    def __exit__(self, *_):
        socket.socket.connect = self._orig
        return False


class _EspiaYtdlp:
    def __init__(self):
        self.chamadas = []

    def __call__(self, args, timeout=300):
        self.chamadas.append(list(args))

        class _R:
            returncode, stdout, stderr = 1, '', 'ERROR: espia'
        return _R


class _EspiaASR:
    """Intercepta o DONO do reconhecimento. Medir que o ASR correu sem esperar
    pelo modelo — o que se afirma e que a cadeia CHEGA la, e isso e um facto
    sobre o caminho, nao sobre a qualidade do texto."""

    def __init__(self):
        self.chamadas = []

    def __call__(self, *a, **k):
        self.chamadas.append((a, k))
        return {'ESTADO': fl.OK, 'TEXTO': 'texto de espia', 'SEGMENTOS': [],
                'IDIOMA': 'it', 'MODELO': 'espia'}


def _ficheiro(tmp, nome='bytes.m4a'):
    """Um ficheiro de som REAL e minusculo, feito aqui.

    A primeira versao escrevia 96 bytes de zeros. A cadeia dava `MEDIA_OK` — ela
    recebeu mesmo o ficheiro — e depois morria a extrair o audio, portanto o
    reconhecedor nunca era chamado e o teste do reuso media meio caminho.

        BYTES QUE NAO SAO SOM PROVAM QUE A MIDIA CHEGOU, NAO QUE ELA SERVE.

    Um segundo de silencio e suficiente e nao depende de gaveta nenhuma.
    """
    import subprocess
    caminho = os.path.join(tmp, nome)
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi',
                        '-i', 'anullsrc=r=16000:cl=mono', '-t', '1',
                        '-c:a', 'aac', caminho],
                       capture_output=True, timeout=120)
    if r.returncode != 0 or not os.path.exists(caminho):
        raise unittest.SkipTest('ffmpeg nao produziu som nesta maquina')
    return caminho


class _RotaRecusada:
    """A MESMA rota, com a lei de volta a RECUSAR — injectada em MEMORIA.

    ⚠️ Um portao so se prova a decidir se for exercido nos DOIS sentidos: o que
    ele faz quando a lei permite (D22, hoje) e o que ele faz quando a lei recusa
    (o estado de ontem, e o de amanha se a decisao mudar).

        UM PORTAO QUE SO FOI VISTO ABERTO NAO SE PROVOU PORTAO.

    A recusa entra AQUI, na memoria do processo, e sai no `__exit__` — o ficheiro
    da lei NAO se escreve para um teste passar. E o mesmo padrao que
    `tests/test_c13_route_gate.py` ja usa.
    """

    def __enter__(self):
        self.orig = mz.MATRIZ['INSTAGRAM'][GROSSA]
        mz.MATRIZ['INSTAGRAM'][GROSSA] = [
            dict(r, PERMITIDA='NAO', ESTADO='ROUTE_NOT_ALLOWED')
            for r in self.orig]
        return self

    def __exit__(self, *_):
        mz.MATRIZ['INSTAGRAM'][GROSSA] = self.orig
        return False


# ══════════════════════════════════════════════════════════════════════════
# T1 · T2 · T3 — A DECISAO VALE NO PONTO ONDE O SOCKET ABRE
# ══════════════════════════════════════════════════════════════════════════
class ADecisaoEstaTomadaEValeNoSocket(unittest.TestCase):

    def setUp(self):
        self.espia = _EspiaYtdlp()
        self._orig = rt._ytdlp
        rt._ytdlp = self.espia

    def tearDown(self):
        rt._ytdlp = self._orig

    def test_T0_a_decisao_esta_tomada_e_nomeia_os_tres_eixos(self):
        """⚠️ DIZIA `..._E_NAO`. MUDOU EM 2026-09-23, POR DECISAO (D22).

        O que esta prova fixa NAO e o valor `SIM` — e que a decisao esta TOMADA,
        e EXPLICITA, e COMPLETA: a rota que atravessa, e os tres eixos, cada um
        com o seu dono. Quem mexer na rota sem prova morre aqui.

            UMA PORTA ABERTA TEM DE DIZER QUEM A ABRIU.
        """
        d = mz.decisao('INSTAGRAM', GROSSA)
        self.assertEqual(d['DECISAO'], mz.PERMITIDA_SIM)
        rotas = mz.MATRIZ['INSTAGRAM'][GROSSA]
        self.assertEqual([r['PERMITIDA'] for r in rotas], ['SIM'])
        self.assertEqual([r['ESTADO'] for r in rotas], ['PROVED'])
        self.assertEqual(rotas[0]['ROTA'],
                         'instagram_transcrever.py:faster-whisper')
        self.assertEqual(rotas[0]['OWNER_AUTHORIZED'], 'SIM')       # D22
        self.assertEqual(rotas[0]['PLATFORM_POLICY_STATUS'], 'DISALLOWED')
        self.assertEqual(rotas[0]['LIMITE'], 'PUBLIC_REEL_BY_URL_ONLY')
        # e com a lei de volta a recusar, a mesma pergunta responde o contrario
        with _RotaRecusada():
            self.assertEqual(mz.decisao('INSTAGRAM', GROSSA)['DECISAO'],
                             mz.NAO_PERMITIDA)

    def test_T1_o_portao_decide_nos_dois_sentidos(self):
        """⚠️ DIZIA «politica_nao_produz_zero_sockets», e a politica mudou (D22).

        O que a prova media era o efeito de UMA decisao. O que passa a medir e o
        PORTAO — e um portao prova-se nos dois sentidos:

            a RECUSAR: nada e pedido — nem socket, nem `yt-dlp`;
            a PERMITIR: a cadeia PEDE, e quem decidiu foi a lei, nao o acaso.

        Sem o segundo sentido, este teste passaria a medir a sorte.
        """
        with _RotaRecusada():
            with _SemRede() as rede:
                rt.obter_midia(dict(SEM_BYTES))
        self.assertEqual(rede.tentativas, [], 'recusada: nao podia sair')
        self.assertEqual(self.espia.chamadas, [],
                         'recusada: nao podia chamar o yt-dlp')
        # ── e agora com a lei a permitir (D22) ────────────────────────────
        self.espia.chamadas[:] = []
        with _SemRede():
            rt.obter_midia(dict(SEM_BYTES))
        self.assertTrue(self.espia.chamadas,
                        'a rota autorizada nao pediu nada: o portao deixou de '
                        'ser o que decide')

    def test_T2_os_metadados_tambem_ficam_atras_do_portao(self):
        # Pedir metadados e tocar a plataforma: abre socket, gasta pedido e
        # aparece no log do host. A regra NAO mudou com a D22 — o que mudou foi
        # a resposta da lei; o portao e o mesmo, e nos dois sentidos.
        with _RotaRecusada():
            with _SemRede() as rede:
                meta, porque = rt.metadados_ytdlp(SEM_BYTES['SOURCE_URL'],
                                                  plataforma='INSTAGRAM')
        self.assertIsNone(meta, 'recusada: nao podia trazer metadados')
        self.assertTrue(porque.startswith(mz.NAO_PERMITIDA), porque)
        self.assertEqual(rede.tentativas, [])
        self.assertEqual(self.espia.chamadas, [])
        # ── e com a lei a permitir (D22), a cadeia PEDE os metadados ──────
        with _SemRede():
            rt.metadados_ytdlp(SEM_BYTES['SOURCE_URL'], plataforma='INSTAGRAM')
        self.assertTrue(self.espia.chamadas,
                        'os metadados deixaram de bater ao portao')

    def test_T3_o_estado_diz_a_causa_certa(self):
        """A recusa de rota nao se disfarca de falta de midia — NEM O CONTRARIO."""
        with _RotaRecusada():
            with _SemRede():
                _c, _p, estado, porque, degraus = rt.obter_midia(dict(SEM_BYTES))
        self.assertEqual(estado, mz.NAO_PERMITIDA)
        self.assertNotEqual(estado, rt.MEDIA_SEM_AUDIO_SO,
                            'a recusa saiu disfarcada de audio indisponivel. O '
                            'som esta la; o que falta e autorizacao.')
        self.assertIn('FETCH_TRANSCRIPT', porque)
        self.assertTrue(degraus and degraus[-1]['RESULT'] == mz.NAO_PERMITIDA)
        # ── e com a lei a permitir (D22), o estado NAO pode ser a politica:
        #        se a midia falhar, a causa e a MIDIA.
        with _SemRede():
            _c, _p, estado2, _pq, _d = rt.obter_midia(dict(SEM_BYTES))
        self.assertNotEqual(estado2, mz.NAO_PERMITIDA,
                           'a falta de midia saiu disfarcada de recusa de rota')


# ══════════════════════════════════════════════════════════════════════════
# T4 · T5 — O QUE JA ESTA EM CASA CONTINUA A PODER SER TRABALHADO
# ══════════════════════════════════════════════════════════════════════════
class ReusarNaoEAdquirir(unittest.TestCase):

    def setUp(self):
        self.espia = _EspiaYtdlp()
        self._orig_yt = rt._ytdlp
        rt._ytdlp = self.espia
        self.asr = _EspiaASR()
        self._orig_asr = fl.transcrever
        fl.transcrever = self.asr
        self.tmp = tempfile.mkdtemp(prefix='c105d-')

    def tearDown(self):
        rt._ytdlp = self._orig_yt
        fl.transcrever = self._orig_asr
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_T4_bytes_entregues_chegam_ao_reconhecedor(self):
        with _SemRede():
            objetos, trace = ai.capturar_reel(
                ident=dict(SEM_BYTES), run_id='C105D-T4',
                midia_ficheiro=_ficheiro(self.tmp), guardar=False)
        self.assertEqual(len(objetos), 1,
                         'a politica de ROTA recusou trabalho que nao usa rota')
        self.assertEqual(objetos[0]['MEDIA_STATE'], 'MEDIA_OK')
        self.assertTrue(self.asr.chamadas, 'o reconhecedor nao foi chamado')

    def test_T5_reusar_nao_adquire_midia_nem_com_a_rota_aberta(self):
        """⚠️ DIZIA «e nao se abriu um socket para isso». Mudou por MEDICAO.

        Com a rota autorizada (D22), a cadeia passou a PEDIR OS METADADOS
        (`yt-dlp -J`) mesmo quando os bytes ja estao em casa — e isso e tocar a
        plataforma. O que **não** acontece, e e a fronteira que este teste
        guarda, e a AQUISICAO DA MIDIA:

            REUSAR != ADQUIRIR.

        A prova separa as duas coisas em vez de as somar, porque somadas uma
        escondia a outra: o pedido de metadados e declarado (`DECLARADO`), e o
        pedido de midia e PROIBIDO enquanto houver bytes em casa.
        """
        self.espia.chamadas[:] = []
        with _SemRede() as rede:
            ai.capturar_reel(ident=dict(SEM_BYTES), run_id='C105D-T5',
                             midia_ficheiro=_ficheiro(self.tmp, 'b.m4a'),
                             guardar=False)
        self.assertEqual(rede.tentativas, [], 'NETWORK_CALLS tem de ser 0')
        de_midia = [c for c in self.espia.chamadas
                    if '-f' in c and rt.SELETOR_SO_AUDIO in c]
        self.assertEqual(de_midia, [],
                         'a cadeia PEDIU A MIDIA com os bytes em casa')
        self.assertEqual(self.trace_de_metadados(), 'DECLARADO',
                         'o pedido de metadados da rota autorizada nao esta '
                         'declarado nesta prova')

    def trace_de_metadados(self):
        pedidos = [' '.join(c) for c in self.espia.chamadas if '-J' in c]
        return 'DECLARADO' if pedidos else 'NAO_PEDIDOS'

    def test_T5b_sem_endereco_para_consultar_nada_sai(self):
        """Com a legenda ja conhecida, o degrau dos metadados nem corre —
        e entao NADA sai, nem para a plataforma nem para o extractor."""
        ident = dict(SEM_BYTES)
        ident['CAPTION_TEXT'] = 'legenda ja em casa — nada a perguntar'
        self.espia.chamadas[:] = []
        with _SemRede() as rede:
            ai.capturar_reel(ident=ident, run_id='C105D-T5B',
                             midia_ficheiro=_ficheiro(self.tmp, 'b2.m4a'),
                             guardar=False)
        self.assertEqual(rede.tentativas, [])
        self.assertEqual(self.espia.chamadas, [],
                         'pediu-se algo a plataforma sem haver o que perguntar')

    def test_a_decisao_sobe_no_trace_mesmo_quando_deixou_passar(self):
        # Um artefato que so menciona a lei quando ela recusa nao deixa auditar
        # o que passou.
        with _SemRede():
            _o, trace = ai.capturar_reel(
                ident=dict(SEM_BYTES), run_id='C105D-TRACE',
                midia_ficheiro=_ficheiro(self.tmp, 'c.m4a'), guardar=False)
        # ⚠️ ESTAS DUAS LINHAS DIZIAM `NAO_PERMITIDA` / `False`. MUDOU POR
        # DECISAO (D22) — e o que a prova guarda continua a ser o mesmo: a
        # decisao sobe no trace MESMO quando deixou passar.
        self.assertEqual(trace['POLICY_DECISION'], mz.PERMITIDA_SIM)
        self.assertTrue(trace['REMOTE_ACQUISITION_ALLOWED'])
        self.assertEqual(trace['POLICY_OWNER'], 'leis/social_matriz.py')


# ══════════════════════════════════════════════════════════════════════════
# T6 · T7 · T8 — TRES DONOS, TRES RESPOSTAS, E NENHUMA MANDA NA OUTRA
# ══════════════════════════════════════════════════════════════════════════
class NenhumaDasTresVerdadesMenteSobreAOutra(unittest.TestCase):

    def test_T6_a_capacidade_local_continua_PROVEN(self):
        self.assertEqual(cap.estado('instagram.reel.transcribe'), 'PROVEN')
        self.assertTrue(cap.promete_resultado('instagram.reel.transcribe'))
        for n in ('instagram.reel.capture', 'instagram.reel.audio'):
            self.assertEqual(cap.estado(n), 'PROVEN')

    def test_T7_recusa_de_rota_nao_vira_bloqueio_tecnico(self):
        """BLOCKED = a plataforma impediu-me tecnicamente.
        ROUTE_NOT_ALLOWED = eu podia, e decidi (ou o dono decidiu) nao fazer.

        Colapsa-las poria a culpa na plataforma por uma decisao desta casa — e a
        D22 nao mudou isso: mudou a ROTA, nao o vocabulario. Os dois estados
        continuam a existir, e a rota do Reel nao esta em nenhum dos dois.

        ⚠️ ESTA LINHA DIZIA `['ROUTE_NOT_ALLOWED']`. MUDOU PARA `['PROVED']`, e a
        prova passa a medir o que sempre quis medir: que o estado da rota e
        JULGADO, nao colapsado no estado da plataforma.
        """
        rotas = mz.MATRIZ['INSTAGRAM'][GROSSA]
        self.assertNotIn('BLOCKED', [r['ESTADO'] for r in rotas])
        self.assertEqual([r['ESTADO'] for r in rotas], ['PROVED'])
        self.assertIn('ROUTE_NOT_ALLOWED', mz.ESTADOS)
        self.assertIn('BLOCKED', mz.ESTADOS)
        with _RotaRecusada():
            self.assertEqual([r['ESTADO'] for r in
                              mz.MATRIZ['INSTAGRAM'][GROSSA]],
                             ['ROUTE_NOT_ALLOWED'])
            self.assertNotIn('BLOCKED', [r['ESTADO'] for r in
                                         mz.MATRIZ['INSTAGRAM'][GROSSA]])

    def test_T8_capacidade_provada_nao_autoriza_rota(self):
        """⚠️ ESTE TESTE DIZIA «a capacidade e PROVEN e a rota e NAO».

        Isso media o VALOR da decisao. Com a D22 os dois ficaram iguais, e a
        prova teria deixado de provar o que existe para provar — que a
        autorizacao vem dos EIXOS DA ROTA, nunca do estado da capacidade.

        A versao que fica e mais forte, e vale nos dois dias: tira-se o eixo do
        dono EM MEMORIA e a rota FECHA com a capacidade intacta.
        """
        self.assertEqual(cap.estado('instagram.reel.transcribe'), 'PROVEN')
        self.assertEqual(mz.decisao('INSTAGRAM', GROSSA)['DECISAO'],
                         mz.PERMITIDA_SIM)          # hoje, com os eixos (D22)
        sem_dono = dict(mz.MATRIZ['INSTAGRAM'][GROSSA][0])
        sem_dono.pop('OWNER_AUTHORIZED')
        self.assertFalse(mz._autorizada_pelo_projeto(sem_dono),
                         'a rota ficou viavel sem o dono autorizar')
        # e o dono de cada resposta e um ficheiro diferente
        self.assertNotEqual('coleta/scrap_capacidades.py', 'leis/social_matriz.py')

    def test_o_reconhecedor_continua_a_ter_um_dono_so(self):
        donos = []
        for raiz, dirs, fich in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('node_modules', '.git', '__pycache__', 'BASELINE', 'data')]
            for f in fich:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), RAIZ).replace(os.sep, '/')
                if rel.startswith('tests/'):
                    continue
                if 'WhisperModel(' in io.open(os.path.join(raiz, f),
                                              encoding='utf-8').read():
                    donos.append(rel)
        self.assertEqual(donos, ['ferramentas/fala_local.py'])


# ══════════════════════════════════════════════════════════════════════════
# T9 · T10 · T11 · T12 · T13 — O QUE ESTA DECISAO NAO PODE TER TRAZIDO
# ══════════════════════════════════════════════════════════════════════════
class ADecisaoNaoTrouxeNadaAtrasDela(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='c105d-x-')

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_T9_nenhum_fornecedor_pago_entra_nesta_rota(self):
        for r in mz.MATRIZ['INSTAGRAM'][GROSSA]:
            self.assertNotIn(r['CLASSE'], ('APIFY', 'OFFICIAL_API_PAID'))
            self.assertNotIn('apify', r['ROTA'].lower())
        self.assertEqual(forn.PAGOS, ('APIFY',))

    def test_T10_o_bruto_historico_nao_foi_tocado(self):
        """Nenhum byte que ja estava em casa muda por causa desta missao.

        O QUE ESTE TESTE APANHOU AO SER ESCRITO: `guardar=False` NAO cobre o WAV
        intermedio. A cadeia calcula sempre `data/raw/REEL-MIDIA/<nome>.wav`, e
        escreve la mesmo quando o chamador pediu para nao guardar nada.

            `guardar=False` COBRE O ARTEFATO. NAO COBRE A OFICINA.

        Isso e divida medida e registada, nao corrigida aqui — corrigi-la mexe
        na cadeia, e esta missao e sobre a decisao de politica. O que o teste
        exige e o que a lei exige: que o BRUTO HISTORICO nao mude.
        """
        gaveta = os.path.join(RAIZ, 'data', 'raw', 'REEL-MIDIA')
        if not os.path.isdir(gaveta):
            self.skipTest('a gaveta de midia nao esta nesta arvore')
        antes = {f: os.path.getsize(os.path.join(gaveta, f))
                 for f in os.listdir(gaveta)}
        self.assertTrue(antes, 'a gaveta veio vazia; a sonda mediria zero por engano')
        espia = _EspiaYtdlp()
        orig = rt._ytdlp
        rt._ytdlp = espia
        try:
            with _SemRede():
                ai.capturar_reel(ident=dict(SEM_BYTES), run_id='C105D-T10',
                                 midia_ficheiro=_ficheiro(self.tmp), guardar=False)
        finally:
            rt._ytdlp = orig
        depois = {f: os.path.getsize(os.path.join(gaveta, f))
                  for f in os.listdir(gaveta)}
        # 1 · nenhum ficheiro que ja existia mudou de tamanho, e nenhum sumiu
        for nome, tamanho in antes.items():
            self.assertIn(nome, depois, 'o bruto historico perdeu %s' % nome)
            self.assertEqual(depois[nome], tamanho,
                             'o bruto historico mudou: %s' % nome)
        # 2 · o que a oficina deixou para tras nao fica a sujar a casa
        for nome in set(depois) - set(antes):
            os.remove(os.path.join(gaveta, nome))

    def test_T11_nenhuma_identidade_e_fabricada(self):
        espia = _EspiaYtdlp()
        orig = rt._ytdlp
        rt._ytdlp = espia
        asr, orig_asr = _EspiaASR(), fl.transcrever
        fl.transcrever = asr
        try:
            with _SemRede():
                objetos, _t = ai.capturar_reel(
                    ident=dict(SEM_BYTES), run_id='C105D-T11',
                    midia_ficheiro=_ficheiro(self.tmp, 'id.m4a'), guardar=False)
        finally:
            rt._ytdlp = orig
            fl.transcrever = orig_asr
        raw = (objetos[0] if objetos else {}).get('RAW') or {}
        if hasattr(raw, '__dict__'):
            raw = dict(raw.__dict__)
        self.assertEqual(raw.get('SOURCE_ID'), rt.NAO_SEI,
                         'o endereco comprou uma identidade')
        self.assertEqual(raw.get('SOURCE_URL'), SEM_BYTES['SOURCE_URL'])
        inventados = [k for k in raw if 'DOCUMENT_ID' in k.upper()]
        self.assertEqual(inventados, [], 'nasceu um DOCUMENT_ID nesta cadeia')

    def test_T12_nenhum_classificador_tematico_entrou(self):
        for ficheiro in ('coleta/adaptador_instagram.py',
                         'ferramentas/reel_transcricao.py',
                         'leis/social_matriz.py'):
            fonte = io.open(os.path.join(RAIZ, ficheiro), encoding='utf-8').read()
            for palavra in ('RELEVANC', 'SOURCE_SCORE', 'SEMANTIC_ADMISSION'):
                self.assertNotIn(palavra, fonte.upper(),
                                 '%s ganhou juizo tematico: %s' % (ficheiro, palavra))

    def test_T13_o_X_ficou_exactamente_como_a_C12_o_mediu(self):
        for n in ('x.direct_post', 'x.media', 'x.metrics'):
            self.assertEqual(cap.estado(n), 'PROVEN')
            self.assertIsNone(cap.da_matriz(n))
        self.assertEqual(cap.estado('x.native_caption'), 'PARTIAL')
        self.assertEqual(cap.estado('x.discovery'), 'UNKNOWN')
        self.assertEqual(mz.decisao('X', 'SEARCH_KEYWORD')['DECISAO'], mz.PERMITIDA_SIM)
        self.assertEqual(mz.decisao('X', 'FETCH_VIDEO_BYTES')['DECISAO'], mz.NAO_DECLARADA)


if __name__ == '__main__':
    unittest.main(verbosity=2)
