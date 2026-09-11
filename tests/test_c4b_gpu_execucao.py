#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DA C4B — escolher o ferro não é ter corrido nele.

Medido na máquina local a 2026-09-11, com a GTX 1080 a responder e o cuBLAS
em falta:

    TRANSCRIPT_STATE  = ASR_FALHOU
    ASR_DEVICE_USED   = GPU          <- e nada correu na placa
    ASR_ACCELERATOR   = CUDA

O modelo carregou na placa; a inferência é que caiu. O campo dizia `GPU` porque
o RESOLVEDOR tinha escolhido GPU — e o resolvedor corre antes de existir uma
única amostra transcrita.

    DEVICE SELECTED != DEVICE EXECUTION PROVEN.
    GPU TECHNICAL SMOKE != GPU QUALITY BENCHMARK.
"""
import ast
import io
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, 'ferramentas'), os.path.join(RAIZ, 'provas'),
          os.path.join(RAIZ, 'regras'), os.path.join(RAIZ, 'leis')):
    sys.path.insert(0, p)
import _gavetas                     # noqa: E402,F401
import fala_local as fl             # noqa: E402

DONO_DO_ASR = 'ferramentas/fala_local.py'
SMOKE = 'provas/gpu_asr_smoke.py'

#: o trace tal como a máquina local o produziu: placa escolhida, modelo carregado
TRACE_GPU = {'DEVICE_REQUESTED': 'GPU', 'DEVICE_SELECTED': 'GPU',
             'ACCELERATOR': 'CUDA', 'CUDA_DEVICE_COUNT': 1, 'WHY_FALLBACK': None}


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════════
class T1OCasoMedidoNaoPodeVoltar(unittest.TestCase):
    """RT3 · RT4 · RT7 · RT10 — o contraexemplo que abriu a missão."""

    def test_gpu_escolhida_e_inferencia_caida_nao_diz_que_a_gpu_correu(self):
        c = fl.carimbo('small', TRACE_GPU, fl.ASR_FALHOU)
        self.assertEqual(c['ASR_DEVICE_EXECUTION'], fl.EXECUCAO_FALHOU)
        self.assertEqual(c['ASR_DEVICE_USED'], fl.NAO_SEI,
                         'a inferencia caiu — nenhum campo pode nomear o ferro '
                         'que «correu», porque nao correu')
        self.assertEqual(c['ASR_ACCELERATOR'], fl.NAO_SEI)

    def test_mas_a_escolha_continua_a_ser_dita(self):
        """Apagar a escolha seria o defeito oposto: perder o diagnóstico.

        É exactamente no caso em que falha que se precisa de saber onde estava.
        """
        c = fl.carimbo('small', TRACE_GPU, fl.ASR_FALHOU)
        self.assertEqual(c['ASR_DEVICE_SELECTED'], fl.GPU)
        self.assertEqual(c['ASR_ACCELERATOR_SELECTED'], 'CUDA')
        self.assertIn('cuda', c['ASR_DEVICE'])

    def test_rt8_a_transcricao_que_acaba_na_placa_diz_que_acabou(self):
        c = fl.carimbo('small', TRACE_GPU, fl.OK)
        self.assertEqual(c['ASR_DEVICE_EXECUTION'], fl.EXECUCAO_PROVADA)
        self.assertEqual(c['ASR_DEVICE_USED'], fl.GPU)
        self.assertEqual(c['ASR_ACCELERATOR'], 'CUDA')


# ══════════════════════════════════════════════════════════════════════════
class T2OVocabularioEFechadoEValidado(unittest.TestCase):

    def test_tres_estados_e_nao_mais(self):
        self.assertEqual((fl.EXECUCAO_PROVADA, fl.EXECUCAO_FALHOU,
                          fl.EXECUCAO_NAO_CORREU), fl.EXECUCOES)

    def test_todo_estado_do_reconhecedor_tem_execucao_dentro_do_vocabulario(self):
        """Uma lista fechada que ninguém confere é uma lista aberta — lição da C5."""
        for estado in fl.ESTADOS:
            for trace in (TRACE_GPU, {}):
                with self.subTest(estado=estado, tem_trace=bool(trace)):
                    self.assertIn(fl.execucao_do_estado(estado, trace), fl.EXECUCOES)

    def test_sem_dispositivo_escolhido_nunca_houve_tentativa(self):
        """RT3 — o modelo que nem chega a carregar não tem device nenhum."""
        for estado in fl.ESTADOS:
            with self.subTest(estado=estado):
                self.assertEqual(fl.execucao_do_estado(estado, {}),
                                 fl.EXECUCAO_NAO_CORREU)

    def test_a_biblioteca_ausente_e_not_run_e_nao_failed(self):
        """RT1/RT2 — sem reconhecedor não houve tentativa em ferro nenhum."""
        self.assertEqual(fl.execucao_do_estado(fl.ASR_INDISPONIVEL, TRACE_GPU),
                         fl.EXECUCAO_NAO_CORREU)

    def test_audio_sem_fala_e_tecto_de_tempo_sao_afirmacoes_sobre_o_audio(self):
        """Nos dois a inferência CORREU e devolveu trechos."""
        for estado in (fl.REQUESTED_EMPTY, fl.TRANSCRIPTION_TIMEOUT):
            with self.subTest(estado=estado):
                self.assertEqual(fl.execucao_do_estado(estado, TRACE_GPU),
                                 fl.EXECUCAO_PROVADA)


# ══════════════════════════════════════════════════════════════════════════
class T3ACadeiaRealDoReconhecedor(unittest.TestCase):
    """RT1 · RT2 · RT6 — sem placa nenhuma, que é o caso deste contentor."""

    def test_sem_placa_o_pedido_gpu_cai_com_nome_e_sem_mentir(self):
        _d, _c, trace = fl.resolver_dispositivo('GPU')
        n, _ = fl.cuda_disponivel()
        if n:
            self.skipTest('esta maquina tem placa — o caso negativo nao se reproduz aqui')
        self.assertEqual(trace['DEVICE_REQUESTED'], fl.GPU)
        self.assertEqual(trace['DEVICE_SELECTED'], fl.CPU)
        self.assertEqual(trace['WHY_FALLBACK'], fl.GPU_INDISPONIVEL)
        c = fl.carimbo('small', trace, fl.OK)
        self.assertEqual(c['ASR_DEVICE_USED'], fl.CPU,
                         'correu no processador, e e isso que tem de sair')
        self.assertNotEqual(c['ASR_DEVICE_USED'], fl.GPU)

    def test_rt5_o_resolvedor_nunca_devolve_device_used(self):
        """A chave antiga saiu do resolvedor — ele não tem como a saber."""
        _d, _c, trace = fl.resolver_dispositivo('CPU')
        self.assertNotIn('DEVICE_USED', trace,
                         'o resolvedor corre ANTES da inferencia: nao pode '
                         'declarar o que correu')
        self.assertIn('DEVICE_SELECTED', trace)


# ══════════════════════════════════════════════════════════════════════════
class T4OSmokeNaoViraBenchmark(unittest.TestCase):
    """RT9 — áudio sintético não pode afirmar qualidade."""

    def test_o_artefato_declara_que_nao_e_benchmark(self):
        d = __import__('gpu_asr_smoke').medir(device=fl.CPU, modelo='small')
        self.assertEqual(d['QUALITY_BENCHMARK'], 'NOT_RUN')
        self.assertIn('nao e benchmark', d['O_QUE_ISTO_NAO_E'])

    def test_o_smoke_nao_mede_termo_nem_marca(self):
        """O banco de qualidade tem outro dono, e ele exige verdade declarada."""
        t = _fonte(SMOKE)
        for proibido in ('TERM_ACCURACY', 'BRAND_ACCURACY', 'verdade()'):
            self.assertNotIn(proibido, t,
                             '%s e do banco de qualidade, nao do smoke' % proibido)


# ══════════════════════════════════════════════════════════════════════════
class T5NaoHaSegundoDonoNemDownloadNovo(unittest.TestCase):
    """RT11 · RT12 · RT13 — um dono do reconhecedor, e nenhuma mídia nova."""

    def test_asr_owners_e_um(self):
        donos = []
        for raiz, _d, fs in os.walk(RAIZ):
            if any(x in raiz for x in ('.git', 'node_modules', '__pycache__', '_libs')):
                continue
            for f in fs:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), RAIZ).replace('\\', '/')
                try:
                    arv = ast.parse(_fonte(rel))
                except Exception:                               # noqa: BLE001
                    continue
                for no in ast.walk(arv):
                    if isinstance(no, ast.Call) and getattr(no.func, 'id', '') == 'WhisperModel':
                        donos.append(rel)
        self.assertEqual(sorted(set(donos)), [DONO_DO_ASR],
                         'o WhisperModel nasce num sitio so: %s' % sorted(set(donos)))

    def test_o_smoke_nao_instancia_reconhecedor_proprio(self):
        arv = ast.parse(_fonte(SMOKE))
        nomes = {getattr(n.func, 'id', '') for n in ast.walk(arv) if isinstance(n, ast.Call)}
        self.assertNotIn('WhisperModel', nomes)
        self.assertNotIn('BatchedInferencePipeline', nomes)

    def test_rt13_o_smoke_nao_adquire_midia(self):
        arv = ast.parse(_fonte(SMOKE))
        importados = set()
        for no in ast.walk(arv):
            if isinstance(no, ast.Import):
                importados.update(a.name.split('.')[0] for a in no.names)
            elif isinstance(no, ast.ImportFrom):
                importados.add((no.module or '').split('.')[0])
        for mau in ('urllib', 'requests', 'yt_dlp', 'http', 'socket', 'apify_client'):
            self.assertNotIn(mau, importados,
                             'o smoke importa %r — ele nao vai a rede' % mau)

    def test_o_modelo_so_e_aceite_se_ja_estiver_na_maquina(self):
        """Um banco que descarrega 1,5 GB mede a rede, não a placa."""
        t = _fonte(SMOKE)
        self.assertIn('local_files_only=True', t,
                      'a pergunta ao cache tem de recusar ir a rede')
        d = __import__('gpu_asr_smoke').medir(device=fl.CPU, modelo='modelo-que-nao-existe-c4b')
        self.assertEqual(d['RESULT'], 'MODEL_NOT_PRESENT')
        self.assertEqual(d['MODEL_PRESENT'], 'NO')


# ══════════════════════════════════════════════════════════════════════════
class T6OPadraoDeComputeNaoMudou(unittest.TestCase):
    """§6 — uma GTX 1080 não é regra universal para todo hardware futuro."""

    def test_o_compute_da_placa_continua_o_que_era(self):
        self.assertEqual(fl.COMPUTE_GPU, 'float16',
                         'o padrao produtivo nao muda sem benchmark de qualidade')
        self.assertEqual(fl.COMPUTE_CPU, 'int8')

    def test_o_dispositivo_padrao_continua_o_processador(self):
        """§25 da C4: a capacidade entrou, a decisão não."""
        self.assertEqual(fl.DISPOSITIVO_PADRAO, fl.CPU)

    def test_int8_float32_e_override_explicito_e_nao_padrao(self):
        """Ele vive no workflow, declarado, e não no código como regra."""
        self.assertNotIn("COMPUTE_GPU = 'int8_float32'", _fonte(DONO_DO_ASR))
        wf = _fonte('.github/workflows/scrap-social.yml')
        self.assertIn('SINTONIA_ASR_COMPUTE: int8_float32', wf,
                      'a prova declara o tipo de calculo que usa, em vez de o esconder')


# ══════════════════════════════════════════════════════════════════════════
class T7AProvaEDuravelEPassaPeloWorkflow(unittest.TestCase):

    def test_a_fase_existe_e_corre_no_runner_local(self):
        wf = _fonte('.github/workflows/scrap-social.yml')
        self.assertIn('gpu-asr]', wf, 'a fase tem de estar nas opcoes do despacho')
        i = wf.index('\n  gpu-asr:')
        corpo = wf[i:wf.index('\n  scrap:', i)]
        self.assertIn('eame-sintonia-local', corpo)
        self.assertIn('provas/gpu_asr_smoke.py', corpo)

    def test_as_fases_de_maquina_nao_disparam_o_job_do_scrap(self):
        """⚠️ Apanhado na PRIMEIRA corrida real, e por isso existe.

        O job `scrap` decidia por exclusao — `fase != 'hardware'`. Ao nascer
        `gpu-asr`, ele passou a disparar tambem para ela: dois jobs a arrancar, e
        o `scrap` a receber uma fase que o seu despacho nao conhece.

            UMA LISTA DE EXCLUSAO NAO SABE O QUE AINDA NAO NASCEU.

        Esta prova varre os jobs que correm no runner local e exige que cada um
        esteja excluido do `scrap`.
        """
        wf = _fonte('.github/workflows/scrap-social.yml')
        # ⚠️ A primeira versao desta prova lia TODAS as linhas `if: inputs.fase ==`
        # e apanhava condicoes de PASSO dentro do proprio `scrap`. Media linhas,
        # nao jobs — e reprovava o ficheiro certo.
        #
        #     UM DETECTOR QUE NAO SABE ONDE ESTA MEDE OUTRA COISA.
        #
        # Agora percorre os JOBS (chave a dois espacos) e le o `if:` de cada um.
        jobs, atual = {}, None
        for linha in wf.splitlines():
            if linha.startswith('  ') and not linha.startswith('   ') and linha.rstrip().endswith(':'):
                atual = linha.strip().rstrip(':')
                jobs.setdefault(atual, [])
            elif atual is not None and linha.startswith('    '):
                jobs[atual].append(linha)
        fases_de_maquina = []
        for job, linhas in jobs.items():
            if job == 'scrap':
                continue
            for ln in linhas:
                t = ln.strip()
                if t.startswith('if: inputs.fase == ') and "'" in t:
                    fases_de_maquina.append(t.split("'")[1])
        self.assertIn('gpu-asr', fases_de_maquina,
                      'a fase da placa tem de ser um JOB proprio')
        self.assertIn('hardware', fases_de_maquina)
        i = wf.index('\n  scrap:')
        guarda = wf[i:wf.index('steps:', i)]
        for fase in fases_de_maquina:
            with self.subTest(fase=fase):
                self.assertIn("inputs.fase != '%s'" % fase, guarda,
                              'a fase %r corre no runner local e o job `scrap` '
                              'nao a exclui — os dois vao disparar' % fase)

    def test_a_fase_nao_instala_nada_na_maquina(self):
        """CUDA/cuBLAS/cuDNN foram postos à mão. A prova só mede."""
        wf = _fonte('.github/workflows/scrap-social.yml')
        i = wf.index('\n  gpu-asr:')
        corpo = wf[i:wf.index('\n  scrap:', i)]
        for proibido in ('pip install', 'choco install', 'winget install',
                         'setup-python', 'Invoke-WebRequest', 'curl '):
            self.assertNotIn(proibido, corpo,
                             'uma prova que altera a maquina que mede deixou de medir')

    def test_rt14_a_prova_nao_grava_no_acervo(self):
        r = subprocess.run(['git', 'status', '--short', '--', 'data/raw', 'data/samples'],
                           cwd=RAIZ, capture_output=True, text=True)
        sujo = [ln for ln in r.stdout.splitlines() if ln.startswith('??')]
        self.assertEqual([], sujo, 'a prova deixou lixo no acervo: %s' % sujo)


# ══════════════════════════════════════════════════════════════════════════
class T8OQueACQuatroBDeixouEmPaz(unittest.TestCase):

    def test_os_estados_do_reconhecedor_nao_mudaram(self):
        self.assertEqual((fl.OK, fl.REQUESTED_EMPTY, fl.ASR_FALHOU,
                          fl.TRANSCRIPTION_TIMEOUT, fl.ASR_INDISPONIVEL), fl.ESTADOS)

    def test_nenhum_adaptador_escolhe_ferro(self):
        """RT11 — a política de dispositivo tem um dono, e não é o adapter."""
        maus = []
        for raiz, _d, fs in os.walk(os.path.join(RAIZ, 'coleta')):
            for f in fs:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), RAIZ).replace('\\', '/')
                t = _fonte(rel)
                if 'resolver_dispositivo' in t or 'COMPUTE_GPU' in t:
                    maus.append(rel)
        self.assertEqual([], maus, 'adaptador a mexer em politica de ferro: %s' % maus)

    def test_o_literal_do_ferro_nao_voltou_a_nenhum_transcritor(self):
        """Ele estava em DOIS sítios, e os dois carimbavam registos sem execução."""
        for rel in ('ferramentas/youtube_transcrever.py',
                    'ferramentas/instagram_transcrever.py'):
            with self.subTest(ficheiro=rel):
                self.assertNotIn("'cpu/int8/%d threads' % nucleos", _fonte(rel),
                                 'ficha de ferro escrita a mao num registo que '
                                 'pode nunca ter corrido')


if __name__ == '__main__':
    unittest.main(verbosity=2)
