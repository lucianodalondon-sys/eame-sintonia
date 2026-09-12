#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.6 — MORRER A MEIO, E SABER O QUE SOBROU.

Uma execucao pode falhar. A pergunta nao e se falha: e o que ela deixa para
tras, e o que a seguinte faz com isso.

    CRASH -> PROCESSO NOVO -> RECUPERA?

Nao «a excepcao foi apanhada?», que e uma pergunta sobre a RAM de um processo
que ainda esta vivo. Aqui o processo morre de verdade — `os._exit()`, que nao
desenrola pilha, nao corre `finally` e nao corre `atexit` — e a resposta e dada
por OUTRO processo, que so ve o disco.

O QUE A C10.6 MEDIU E CORRIGIU
--------------------------------
1 · O laco de tentativas nao perguntava a ninguem se valia a pena repetir. Um
    `403` levava quatro tentativas; um `404` tambem. A casa ja tinha a resposta
    escrita em `leis/falhas.py`, onde os dois sao `retentavel=False`.

        QUATRO TENTATIVAS SOBRE UM NAO DEFINITIVO NAO SAO PERSISTENCIA.
        SAO MARTELADAS.

2 · Dois processos a fechar o mesmo lote perdiam uma observacao: em seis
    execucoes, duas ficaram so com um dos dois `RUN_ID`. O ficheiro nao
    corrompia — o ultimo a escrever apagava a fusao do outro.

        UMA OBSERVACAO QUE ACONTECEU E DESAPARECEU E PIOR QUE UM ERRO:
        UM ERRO DEIXA TESTEMUNHA.

3 · `guardar=False` nao cobria a oficina, e o WAV intermedio caia na gaveta
    real. Uma suite de crash sujaria o bruto da casa a cada corrida.

O QUE CONTINUA POR FAZER, E ESTA REGISTADO NO DOCUMENTO
---------------------------------------------------------
Nao ha estado de corrida duravel entre processos: sem `attempts`, sem
`last_error`, sem `replayable` do lado de fora da RAM. O processo novo ve os
bytes e o lote — e mais nada. Isso e conflito estrutural, nao defeito de linha,
e nao se resolve inventando esquema aqui.
"""
import ast
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('ferramentas', 'leis', 'coleta', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import falhas as fx                 # noqa: E402
import fala_local as fl             # noqa: E402
import social_matriz as mz          # noqa: E402
import reel_transcricao as rt       # noqa: E402
import adaptador_instagram as ai    # noqa: E402

GROSSA = 'FETCH_TRANSCRIPT'
IDENT = {'PLATFORM': 'INSTAGRAM', 'POST_ID': 'C106TESTE',
         'SOURCE_URL': 'https://www.instagram.com/reel/C106TESTE/'}


def _som(destino, nome='fixture.m4a'):
    """Um segundo de silencio real. Bytes que nao sao som provam que a midia
    chegou, nao que ela serve."""
    caminho = os.path.join(destino, nome)
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi',
                        '-i', 'anullsrc=r=16000:cl=mono', '-t', '1',
                        '-c:a', 'aac', caminho], capture_output=True, timeout=120)
    if r.returncode != 0 or not os.path.exists(caminho):
        raise unittest.SkipTest('ffmpeg nao produziu som nesta maquina')
    return caminho


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


class _PoliticaPermissiva:
    """Injecta SIM em memoria; o ficheiro continua a dizer NAO (C10.5D)."""

    def __enter__(self):
        self._orig = mz.MATRIZ['INSTAGRAM'][GROSSA]
        mz.MATRIZ['INSTAGRAM'][GROSSA] = [
            dict(r, PERMITIDA='SIM', ESTADO='PROVED') for r in self._orig]
        return self

    def __exit__(self, *_):
        mz.MATRIZ['INSTAGRAM'][GROSSA] = self._orig
        return False


class _Ytdlp:
    """Transporte falso que responde SEMPRE o mesmo erro, e conta as tentativas."""

    def __init__(self, stderr):
        self.chamadas = []
        self.stderr = stderr

    def __call__(self, args, timeout=300):
        self.chamadas.append(list(args))
        err = self.stderr

        class _R:
            returncode, stdout, stderr = 1, '', err
        return _R


class _Relogio:
    """O relogio injectado. Nenhum teste espera minutos reais."""

    def __init__(self):
        self.dormiu = []
        self._orig = rt._dormir
        rt._dormir = self.dormiu.append

    def desligar(self):
        rt._dormir = self._orig


# ══════════════════════════════════════════════════════════════════════════
# O CRASH E REAL, E QUEM RESPONDE E OUTRO PROCESSO
# ══════════════════════════════════════════════════════════════════════════
FILHO = r'''
import os, sys, json
RAIZ = %r
os.chdir(RAIZ)
for d in ('leis','coleta','ferramentas','guarda'):
    sys.path.insert(0, os.path.join(RAIZ, d))
FASE, OFICINA, SAIDA, FIXTURE, MARCAS = sys.argv[1:6]
import fala_local as fl, reel_transcricao as rt
rt.SAIDA = SAIDA
os.makedirs(SAIDA, exist_ok=True)

def marca(nome, **e):
    d = dict(e); d['MARCA'] = nome
    open(MARCAS, 'a', encoding='utf-8').write(json.dumps(d, default=str) + '\n')

def morrer(p):
    marca('MORTE', PONTO=p); sys.stdout.flush(); os._exit(97)

def asr(wav, **k):
    marca('ASR_ENTROU')
    if FASE == 'F3':
        morrer('dentro do ASR')
    return fl._resposta(fl.OK, 'prova', texto='a fala desta prova', maquina_s=0.01,
                        audio_s=1.0, segmentos=[{'INICIO':0.0,'FIM':1.0,'TEXTO':'a fala desta prova'}],
                        idioma_detectado='it', confianca=0.9, voiced=1, no_speech=0.01)
fl.transcrever = asr

_f = rt._ficha_raw
def ficha(*a, **k):
    raw = _f(*a, **k)
    marca('RAW_FICHADO', SHA256=getattr(raw, 'SHA256', None),
          ARTIFACT_ID=getattr(raw, 'ARTIFACT_ID', None))
    if FASE == 'F1':
        morrer('logo depois do RAW')
    return raw
rt._ficha_raw = ficha

if FASE == 'F0':
    morrer('antes de qualquer preservacao')
r = rt.transcrever_reel({'PLATFORM':'INSTAGRAM','POST_ID':'C106TESTE',
                         'SOURCE_URL':'https://www.instagram.com/reel/C106TESTE/'},
                        run_id='C106-' + FASE, midia_ficheiro=FIXTURE,
                        guardar=True, oficina=OFICINA)
caminho, _c = rt.gravar_lote([r])
marca('RUN_FECHADO', TRANSCRIPT_STATE=r.get('TRANSCRIPT_STATE'))
''' % RAIZ


class OCrashERealEOutroProcessoResponde(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='c106-crash-')
        self.filho = os.path.join(self.tmp, 'filho.py')
        io.open(self.filho, 'w', encoding='utf-8').write(FILHO)
        self.of = os.path.join(self.tmp, 'oficina')
        self.sa = os.path.join(self.tmp, 'saida')
        os.makedirs(self.of)
        os.makedirs(self.sa)
        self.fix = _som(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _correr(self, fase):
        marcas = os.path.join(self.tmp, 'm-%s.jsonl' % fase)
        r = subprocess.run([sys.executable, self.filho, fase, self.of, self.sa,
                            self.fix, marcas],
                           capture_output=True, text=True, timeout=600, cwd=RAIZ,
                           env=dict(os.environ, HF_HUB_OFFLINE='1'))
        ms = ([json.loads(l) for l in io.open(marcas, encoding='utf-8')]
              if os.path.exists(marcas) else [])
        return r.returncode, ms

    def test_P1_o_processo_morre_mesmo(self):
        # 97 e o codigo de `os._exit`. Um `raise` apanhado devolveria 0 ou 1, e
        # provaria que a excepcao foi tratada — nao que o processo morreu.
        for fase in ('F0', 'F1', 'F3'):
            codigo, marcas = self._correr(fase)
            self.assertEqual(codigo, 97, '%s nao morreu de verdade' % fase)
            self.assertTrue(any(m['MARCA'] == 'MORTE' for m in marcas))

    def test_P2_o_que_foi_preservado_antes_do_crash_sobrevive(self):
        antes = os.path.getsize(self.fix)
        codigo, marcas = self._correr('F1')
        self.assertEqual(codigo, 97)
        self.assertTrue(any(m['MARCA'] == 'RAW_FICHADO' for m in marcas),
                        'o RAW nem chegou a ser fichado; a fase esta mal posta')
        self.assertTrue(os.path.exists(self.fix), 'os bytes sumiram com o processo')
        self.assertEqual(os.path.getsize(self.fix), antes)

    def test_P4_transcript_parcial_nunca_vira_completo(self):
        # Morte DENTRO do ASR. Nada de texto pode aparecer na entrega.
        codigo, marcas = self._correr('F3')
        self.assertEqual(codigo, 97)
        self.assertTrue(any(m['MARCA'] == 'ASR_ENTROU' for m in marcas))
        self.assertNotIn('TRANSCRICOES-REEL.json', os.listdir(self.sa))
        self.assertEqual([f for f in os.listdir(self.sa) if f.endswith('.txt')], [])

    def test_P3_o_processo_novo_retoma_sem_voltar_a_adquirir(self):
        self._correr('F1')
        chamou = {'n': 0}
        orig = rt._ytdlp

        def espia(a, timeout=300):
            chamou['n'] += 1
            return orig(a, timeout=timeout)
        rt._ytdlp = espia
        saida_real, rt.SAIDA = rt.SAIDA, self.sa
        asr_real, fl.transcrever = fl.transcrever, lambda w, **k: fl._resposta(
            fl.OK, 'prova', texto='a fala desta prova', maquina_s=0.01, audio_s=1.0,
            segmentos=[{'INICIO': 0.0, 'FIM': 1.0, 'TEXTO': 'a fala desta prova'}],
            idioma_detectado='it', confianca=0.9, voiced=1, no_speech=0.01)
        try:
            with _SemRede() as rede:
                r = rt.transcrever_reel(dict(IDENT), run_id='C106-RETOMA',
                                        midia_ficheiro=self.fix, guardar=True,
                                        oficina=self.of)
        finally:
            rt._ytdlp = orig
            rt.SAIDA = saida_real
            fl.transcrever = asr_real
        self.assertEqual(chamou['n'], 0, 'a retoma voltou a chamar o yt-dlp')
        self.assertEqual(rede.tentativas, [], 'a retoma saiu para a rede')
        self.assertEqual(r['TRANSCRIPT_STATE'], fl.OK)


# ══════════════════════════════════════════════════════════════════════════
# REPETIR SO QUANDO REPETIR ADIANTA
# ══════════════════════════════════════════════════════════════════════════
class OLacoPerguntaAntesDeRepetir(unittest.TestCase):

    def setUp(self):
        self.relogio = _Relogio()
        self.tmp = tempfile.mkdtemp(prefix='c106-retry-')
        self._orig = rt._ytdlp

    def tearDown(self):
        self.relogio.desligar()
        rt._ytdlp = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _tentar(self, stderr, nome='t.m4a'):
        espia = _Ytdlp(stderr)
        rt._ytdlp = espia
        relato = {}
        with _PoliticaPermissiva():
            rt.midia_por_ytdlp('https://www.instagram.com/reel/T/',
                               os.path.join(self.tmp, nome), kind=rt.MIDIA_AUDIO,
                               plataforma='INSTAGRAM', relato=relato)
        return espia, relato

    def test_P5_permanente_e_transiente_nao_se_comportam_igual(self):
        perm, r_perm = self._tentar('ERROR: HTTP Error 403: Forbidden', 'a.m4a')
        tran, r_tran = self._tentar('ERROR: read operation timed out', 'b.m4a')
        self.assertEqual(r_perm['LAST_ERROR_STATE'], 'BLOCKED')
        self.assertEqual(r_tran['LAST_ERROR_STATE'], 'TRANSIENT_NETWORK_ERROR')
        self.assertFalse(fx.retentavel(r_perm['LAST_ERROR_STATE']))
        self.assertTrue(fx.retentavel(r_tran['LAST_ERROR_STATE']))
        self.assertEqual(len(perm.chamadas), 1, 'martelou um NAO definitivo')
        self.assertGreater(len(tran.chamadas), 1, 'desistiu de um erro passageiro')

    def test_P6_o_retry_tem_teto_e_o_teto_e_observavel(self):
        espia, relato = self._tentar('ERROR: HTTP Error 500: Server Error')
        self.assertEqual(len(espia.chamadas), rt.YTDLP_TENTATIVAS)
        self.assertEqual(relato['ATTEMPTS'], relato['ATTEMPT_LIMIT'])
        self.assertTrue(relato['RETRY_EXHAUSTED'])
        self.assertEqual(relato['STOPPED_BECAUSE'], 'TENTATIVAS_ESGOTADAS')

    def test_P8_o_erro_final_nao_some(self):
        espia, relato = self._tentar('ERROR: HTTP Error 404: Not Found')
        for campo in ('ATTEMPTS', 'ATTEMPT_LIMIT', 'LAST_ERROR',
                      'LAST_ERROR_STATE', 'RETRY_EXHAUSTED', 'STOPPED_BECAUSE'):
            self.assertIn(campo, relato)
        self.assertNotEqual(relato['LAST_ERROR'], rt.NOT_KNOWN)
        self.assertEqual(relato['STOPPED_BECAUSE'], 'NAO_RETENTAVEL')

    def test_o_retry_after_da_plataforma_manda_no_relogio(self):
        _e, relato = self._tentar(
            'ERROR: HTTP Error 429: Too Many Requests. Retry-After: 7')
        self.assertEqual(relato['RETRY_AFTER'], 7)
        self.assertEqual(self.relogio.dormiu, [7, 7, 7])

    def test_sem_retry_after_a_espera_e_a_desta_casa_e_e_limitada(self):
        _e, relato = self._tentar('ERROR: HTTP Error 429: Too Many Requests')
        self.assertEqual(relato['RETRY_AFTER'], rt.NAO_SEI,
                         'ausencia virou zero; sao coisas diferentes')
        self.assertEqual(self.relogio.dormiu, list(rt.ESPERA_ENTRE_TENTATIVAS))
        self.assertLessEqual(sum(self.relogio.dormiu), 60,
                             'a espera deixou de ser limitada')

    def test_o_que_nao_se_entende_nao_se_repete(self):
        espia, relato = self._tentar('ERROR: uma coisa que esta casa nunca viu')
        self.assertEqual(relato['LAST_ERROR_STATE'], 'UNKNOWN_ERROR')
        self.assertEqual(len(espia.chamadas), 1,
                         'repetiu o que nao entendeu: isso e martelar no escuro')

    def test_P7_politica_NAO_nao_e_retentavel(self):
        espia = _Ytdlp('nunca chega a ser lido')
        rt._ytdlp = espia
        relato = {}
        with _SemRede() as rede:
            _c, motivo = rt.midia_por_ytdlp(
                'https://www.instagram.com/reel/T/', os.path.join(self.tmp, 'p.m4a'),
                kind=rt.MIDIA_AUDIO, plataforma='INSTAGRAM', relato=relato)
        self.assertEqual(espia.chamadas, [], 'a politica NAO foi tentada na rede')
        self.assertEqual(rede.tentativas, [])
        self.assertEqual(self.relogio.dormiu, [], 'esperou para repetir um NAO')
        self.assertTrue(motivo.startswith(mz.NAO_PERMITIDA), motivo)
        self.assertFalse(fx.retentavel('ROUTE_NOT_ALLOWED'))

    def test_a_cadeia_pergunta_ao_dono_e_nao_a_uma_tabela_propria(self):
        arv = ast.parse(io.open(os.path.join(RAIZ, 'ferramentas',
                                             'reel_transcricao.py'),
                                encoding='utf-8').read())
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == '_laco_do_ytdlp')
        pergunta = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr == 'retentavel'
                    and isinstance(n.func.value, ast.Name)
                    and n.func.value.id == 'fx']
        self.assertTrue(pergunta, 'o laco deixou de perguntar a `leis/falhas.py`')


# ══════════════════════════════════════════════════════════════════════════
# REPETIR NAO CRIA LIXO, NEM IDENTIDADE
# ══════════════════════════════════════════════════════════════════════════
class RepetirNaoDuplicaNemFabrica(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='c106-idem-')
        self.sa = os.path.join(self.tmp, 'saida')
        self.of = os.path.join(self.tmp, 'oficina')
        os.makedirs(self.sa)
        os.makedirs(self.of)
        self.fix = _som(self.tmp)
        self._saida, rt.SAIDA = rt.SAIDA, self.sa
        self._asr, fl.transcrever = fl.transcrever, lambda w, **k: fl._resposta(
            fl.OK, 'prova', texto='a fala desta prova', maquina_s=0.01, audio_s=1.0,
            segmentos=[{'INICIO': 0.0, 'FIM': 1.0, 'TEXTO': 'a fala desta prova'}],
            idioma_detectado='it', confianca=0.9, voiced=1, no_speech=0.01)

    def tearDown(self):
        rt.SAIDA = self._saida
        fl.transcrever = self._asr
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _uma_vez(self, run_id):
        r = rt.transcrever_reel(dict(IDENT), run_id=run_id,
                                midia_ficheiro=self.fix, guardar=True,
                                oficina=self.of)
        caminho, corpo = rt.gravar_lote([r])
        return r, corpo

    def test_P10_a_identidade_nao_e_fabricada_e_nao_muda_no_retry(self):
        a, _ = self._uma_vez('C106-1')
        b, _ = self._uma_vez('C106-2')
        self.assertEqual(a['RAW']['SHA256'], b['RAW']['SHA256'],
                         'os mesmos bytes mudaram de SHA entre tentativas')
        self.assertEqual(a['RAW']['ARTIFACT_ID'], b['RAW']['ARTIFACT_ID'])
        # e nada nasceu do endereco nem do caminho
        self.assertEqual(a['RAW']['SOURCE_ID'], rt.NAO_SEI)
        self.assertEqual([k for k in a['RAW'] if 'DOCUMENT_ID' in k.upper()], [])

    def test_repetir_nao_cria_um_segundo_registo_duravel(self):
        self._uma_vez('C106-1')
        _b, corpo = self._uma_vez('C106-2')
        self.assertEqual(corpo['ITEM_COUNT'], 1, 'nasceu um registo duplicado')
        item = corpo['ITEMS'][0]
        self.assertEqual(sorted(item['RUN_IDS_SEEN']), ['C106-1', 'C106-2'],
                         'uma observacao desapareceu')
        self.assertEqual(item['TIMES_OBSERVED'], 2)

    def test_a_mesma_corrida_repetida_nao_infla_a_contagem(self):
        self._uma_vez('C106-MESMA')
        _b, corpo = self._uma_vez('C106-MESMA')
        self.assertEqual(corpo['ITEMS'][0]['TIMES_OBSERVED'], 1,
                         'a mesma corrida contou como duas observacoes')


# ══════════════════════════════════════════════════════════════════════════
# A OFICINA NAO E A GAVETA
# ══════════════════════════════════════════════════════════════════════════
class UmaCorridaQueNaoGuardaNaoSujaAGaveta(unittest.TestCase):

    def test_P11_guardar_false_nao_deixa_nada_no_bruto_real(self):
        gaveta = os.path.join(RAIZ, 'data', 'raw', 'REEL-MIDIA')
        if not os.path.isdir(gaveta):
            self.skipTest('a gaveta de midia nao esta nesta arvore')
        antes = {f: os.path.getsize(os.path.join(gaveta, f))
                 for f in os.listdir(gaveta)}
        self.assertTrue(antes, 'a gaveta veio vazia; a sonda mediria zero por engano')
        tmp = tempfile.mkdtemp(prefix='c106-gaveta-')
        asr, fl.transcrever = fl.transcrever, lambda w, **k: fl._resposta(
            fl.OK, 'prova', texto='x', maquina_s=0.01, audio_s=1.0, segmentos=[],
            idioma_detectado='it', confianca=0.9, voiced=1, no_speech=0.01)
        try:
            with _SemRede():
                objetos, _t = ai.capturar_reel(
                    ident=dict(IDENT), run_id='C106-GAVETA',
                    midia_ficheiro=_som(tmp), guardar=False)
        finally:
            fl.transcrever = asr
            shutil.rmtree(tmp, ignore_errors=True)
        depois = {f: os.path.getsize(os.path.join(gaveta, f))
                  for f in os.listdir(gaveta)}
        self.assertEqual(antes, depois,
                         'uma corrida `guardar=False` deixou lixo na gaveta real')
        self.assertFalse(objetos[0]['OFICINA_E_A_GAVETA'])

    def test_quem_guarda_continua_a_trabalhar_na_gaveta(self):
        # O contraponto. Sem ele, o teste de cima passaria com a oficina sempre
        # temporaria — e a producao deixaria de preservar.
        arv = ast.parse(io.open(os.path.join(RAIZ, 'ferramentas',
                                             'reel_transcricao.py'),
                                encoding='utf-8').read())
        fonte = io.open(os.path.join(RAIZ, 'ferramentas',
                                     'reel_transcricao.py'), encoding='utf-8').read()
        self.assertIn('MIDIA if guardar else', fonte,
                      'a oficina deixou de ser a gaveta quando se guarda')
        self.assertTrue(any(isinstance(n, ast.FunctionDef)
                            and n.name == 'transcrever_reel' for n in ast.walk(arv)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
