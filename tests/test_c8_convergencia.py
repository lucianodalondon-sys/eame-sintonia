#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DA C8 — a linha GPU entrou sem apagar o que veio depois dela.

Duas frentes divergiram na mesma árvore. A C4B/C4C mexeu no reconhecedor, no
trace do ferro e no runtime CUDA. A C5/C6/C7 mexeu na rota da legenda, na
espécie do texto e no lugar do facto.

    HEAD MAIS NOVO NUMA FRENTE != ESTADO GLOBAL MAIS NOVO.

Medido antes de integrar: as duas frentes tocaram CONJUNTOS DISJUNTOS de
ficheiros, e os cinco que a linha GPU alterou estavam idênticos entre a base
comum e a C7. Por isso a integração é semântica e verificável, e não um merge
às cegas — mas continua a precisar de quem a vigie, e é isto.
"""
import ast
import io
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, 'regras'), os.path.join(RAIZ, 'ferramentas'),
          os.path.join(RAIZ, 'leis'), os.path.join(RAIZ, 'provas')):
    sys.path.insert(0, p)
import _gavetas                      # noqa: E402,F401
import proveniencia as pv            # noqa: E402
import sensor_medir as sm            # noqa: E402
import fala_local as fl              # noqa: E402

DONO_DO_ASR = 'ferramentas/fala_local.py'
WORKFLOW = '.github/workflows/scrap-social.yml'


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════════
class T1OsInvariantesDaLinhaC5C6C7(unittest.TestCase):
    """RT5 · RT6 · RT7 — o que veio depois da C4 não pode ter sido apagado."""

    def test_c5_o_vocabulario_da_especie_continua_fechado(self):
        self.assertEqual(
            (pv.NATIVE_CAPTION_ORIGINAL, pv.NATIVE_CAPTION_TRANSLATED,
             pv.ASR_LOCAL, pv.NAO_SEI), pv.ESPECIES_DO_TEXTO)

    def test_c6_o_portao_da_especie_continua_a_fechar(self):
        """Texto traduzido e texto de espécie desconhecida não servem de original."""
        self.assertFalse(pv.serve_para_original(pv.NAO_SEI))
        self.assertFalse(pv.serve_para_original(pv.NATIVE_CAPTION_TRANSLATED))
        self.assertTrue(pv.serve_para_original(pv.ASR_LOCAL))
        self.assertTrue(pv.serve_para_original(pv.NATIVE_CAPTION_ORIGINAL))

    def test_c6_o_medidor_continua_a_perguntar_a_especie(self):
        arv = ast.parse(_fonte('regras/sensor_medir.py'))
        fn = next(n for n in ast.walk(arv)
                  if isinstance(n, ast.FunctionDef) and n.name == 'medir')
        chamadas = {ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call)}
        self.assertIn('pv.serve_para_original', chamadas)

    def test_c7_o_matcher_do_lugar_nao_voltou_ao_fuzzy(self):
        for texto in ('Periodico olivo 1 Maggio 2026', 'calendario fitosanitario',
                      'barbabietole da zucchero', 'beaucoup de pluie',
                      'ho parlato con Francesco'):
            with self.subTest(texto=texto):
                self.assertEqual(sm.NAO_SEI, sm.lugar_do_fato(texto)[0])

    def test_c7_os_positivos_continuam_a_casar(self):
        for texto, pais in (('La Rioja', 'ES'), ('Verona', 'IT'),
                            ('Champagne', 'FR'), ('Alto Adige', 'IT')):
            with self.subTest(texto=texto):
                self.assertEqual(pais, sm.lugar_do_fato(texto)[0])

    def test_c7_a_geografia_nao_chama_o_matcher_de_assunto(self):
        arv = ast.parse(_fonte('regras/sensor_medir.py'))
        fn = next(n for n in ast.walk(arv)
                  if isinstance(n, ast.FunctionDef) and n.name == 'lugar_do_fato')
        chamadas = {ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call)}
        for proibida in ('_tem', '_perto', '_raizes'):
            self.assertNotIn(proibida, chamadas)
        self.assertIn('_nomeia_lugar', chamadas)


# ══════════════════════════════════════════════════════════════════════════
class T2OTraceDaLinhaGpuEntrouInteiro(unittest.TestCase):
    """RT1 · RT2 · RT3 · RT4 — e continua a não mentir."""

    def test_os_tres_tempos_da_decisao_existem(self):
        c = fl.carimbo('small', {'DEVICE_REQUESTED': 'GPU', 'DEVICE_SELECTED': 'GPU',
                                 'ACCELERATOR': 'CUDA', 'WHY_FALLBACK': None}, fl.OK)
        for campo in ('ASR_DEVICE_REQUESTED', 'ASR_DEVICE_SELECTED',
                      'ASR_DEVICE_EXECUTION', 'ASR_DEVICE_USED',
                      'ASR_ACCELERATOR', 'ASR_ACCELERATOR_SELECTED'):
            self.assertIn(campo, c)

    def test_rt4_gpu_escolhida_com_queda_nao_diz_que_a_gpu_correu(self):
        t = {'DEVICE_REQUESTED': 'GPU', 'DEVICE_SELECTED': 'GPU',
             'ACCELERATOR': 'CUDA', 'WHY_FALLBACK': None}
        c = fl.carimbo('small', t, fl.ASR_FALHOU)
        self.assertEqual(c['ASR_DEVICE_EXECUTION'], fl.EXECUCAO_FALHOU)
        self.assertEqual(c['ASR_DEVICE_USED'], fl.NAO_SEI)
        self.assertEqual(c['ASR_ACCELERATOR'], fl.NAO_SEI)

    def test_rt3_a_queda_para_o_processador_nao_se_mascara(self):
        t = {'DEVICE_REQUESTED': 'GPU', 'DEVICE_SELECTED': 'CPU',
             'ACCELERATOR': 'NONE', 'WHY_FALLBACK': fl.GPU_INDISPONIVEL}
        c = fl.carimbo('small', t, fl.OK)
        self.assertEqual(c['ASR_DEVICE_USED'], fl.CPU)
        self.assertEqual(c['ASR_WHY_FALLBACK'], fl.GPU_INDISPONIVEL)

    def test_rt1_sem_placa_o_pedido_gpu_cai_com_nome(self):
        n, _ = fl.cuda_disponivel()
        if n:
            self.skipTest('esta maquina tem placa — o caso negativo nao se reproduz')
        _d, _c, trace = fl.resolver_dispositivo('GPU')
        self.assertEqual(trace['DEVICE_SELECTED'], fl.CPU)
        self.assertEqual(trace['WHY_FALLBACK'], fl.GPU_INDISPONIVEL)

    def test_o_runtime_cuda_e_do_processo_e_nao_da_maquina(self):
        """RT: a solução não instala nada nem escreve PATH global."""
        t = _fonte(DONO_DO_ASR)
        self.assertIn('add_dll_directory', t)
        self.assertIn("os.environ['PATH']", t)
        # ⚠️ Lida da ARVORE. A primeira versao procurava `pip install` no TEXTO
        # e encontrava-o — na docstring que ENSINA uma pessoa a instalar a
        # biblioteca a mao. Isso e documentacao, nao e o codigo a instalar.
        #
        #     UMA SENTINELA ANCORADA NO TEXTO MEDE O TEXTO, NAO A LEI.
        arv = ast.parse(t)
        importados = set()
        for n in ast.walk(arv):
            if isinstance(n, ast.Import):
                importados.update(a.name.split('.')[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom):
                importados.add((n.module or '').split('.')[0])
        self.assertNotIn('winreg', importados,
                         'o dono do ASR nao escreve no registo da maquina')
        # ⚠️ Segunda correccao: a versao anterior proibia QUALQUER processo
        # externo, e o dono chama `ffmpeg`/`ffprobe` — que e USAR uma ferramenta
        # instalada, nao instala-la. A lei e sobre INSTALADORES.
        #
        #     USAR O QUE ESTA NA MAQUINA NAO E ALTERAR A MAQUINA.
        INSTALADORES = ('pip', 'pip3', 'choco', 'winget', 'apt', 'apt-get',
                        'setx', 'msiexec', 'curl', 'wget', 'Invoke-WebRequest')
        for n in ast.walk(arv):
            if not isinstance(n, ast.Call):
                continue
            if ast.unparse(n.func) not in ('subprocess.run', 'subprocess.call',
                                           'subprocess.check_call', 'os.system'):
                continue
            argv = n.args[0] if n.args else None
            nomes = []
            if isinstance(argv, ast.List):
                nomes = [e.value for e in argv.elts if isinstance(e, ast.Constant)][:1]
            elif isinstance(argv, ast.Constant):
                nomes = [str(argv.value).split()[0]]
            for exe in nomes:
                with self.subTest(executavel=exe):
                    self.assertNotIn(str(exe).lower(), INSTALADORES,
                                     'o dono do ASR corre um instalador — '
                                     'ele mede e usa, nao instala')


# ══════════════════════════════════════════════════════════════════════════
class T3NaoNasceuDonoNovoNemCaminhoParalelo(unittest.TestCase):

    def test_rt9_asr_owners_continua_um(self):
        donos = []
        for raiz, _d, fs in os.walk(RAIZ):
            if any(x in raiz for x in ('.git', 'node_modules', '__pycache__', '_libs')):
                continue
            for f in fs:
                if not f.endswith('.py') or f.startswith('test_'):
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), RAIZ).replace('\\', '/')
                try:
                    arv = ast.parse(_fonte(rel))
                except Exception:                               # noqa: BLE001
                    continue
                for no in ast.walk(arv):
                    if isinstance(no, ast.Call) and getattr(no.func, 'id', '') == 'WhisperModel':
                        donos.append(rel)
        self.assertEqual(sorted(set(donos)), [DONO_DO_ASR])

    def test_rt8_nenhum_adaptador_escolhe_ferro(self):
        maus = []
        for raiz, _d, fs in os.walk(os.path.join(RAIZ, 'coleta')):
            for f in fs:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), RAIZ).replace('\\', '/')
                t = _fonte(rel)
                if 'resolver_dispositivo' in t or 'COMPUTE_GPU' in t:
                    maus.append(rel)
        self.assertEqual([], maus)

    def test_rt10_a_fase_da_placa_nao_dispara_o_job_do_scrap(self):
        """A guarda do `scrap` decide por exclusão, e tem de conhecer cada fase."""
        wf = _fonte(WORKFLOW)
        jobs, atual = {}, None
        for linha in wf.splitlines():
            if linha.startswith('  ') and not linha.startswith('   ') and linha.rstrip().endswith(':'):
                atual = linha.strip().rstrip(':')
                jobs.setdefault(atual, [])
            elif atual is not None and linha.startswith('    '):
                jobs[atual].append(linha)
        de_maquina = []
        for job, linhas in jobs.items():
            if job == 'scrap':
                continue
            for ln in linhas:
                t = ln.strip()
                if t.startswith('if: inputs.fase == ') and "'" in t:
                    de_maquina.append(t.split("'")[1])
        self.assertIn('gpu-asr', de_maquina)
        guarda = wf[wf.index('\n  scrap:'):wf.index('steps:', wf.index('\n  scrap:'))]
        for fase in de_maquina:
            with self.subTest(fase=fase):
                self.assertIn("inputs.fase != '%s'" % fase, guarda)


# ══════════════════════════════════════════════════════════════════════════
class T4OQueNaoFoiPortadoNaoEstaCa(unittest.TestCase):
    """§7 — testemunha histórica fica na branch que a produziu."""

    def test_o_censo_do_corpus_legado_nao_entrou(self):
        self.assertFalse(os.path.exists(os.path.join(RAIZ, 'provas/corpus_recuperar.py')),
                         'o censo do corpus legado e testemunha de uma investigacao, '
                         'nao capacidade operacional desta linha')
        self.assertFalse(os.path.exists(os.path.join(RAIZ, 'tests/test_c4c_corpus.py')))

    def test_a_fase_do_banco_legado_nao_entrou(self):
        """`gpu-bench` depende de um corpus que não está na máquina da placa."""
        wf = _fonte(WORKFLOW)
        self.assertNotIn('gpu-bench', wf)
        self.assertNotIn('corpus_recuperar', wf)

    def test_rt13_nenhum_corpus_legado_entrou_no_git(self):
        r = subprocess.run(['git', 'ls-files', 'data/raw'],
                           cwd=RAIZ, capture_output=True, text=True)
        maus = [x for x in r.stdout.split() if x.endswith(('.mp4', '.wav', '.m4a'))]
        self.assertEqual([], maus)


# ══════════════════════════════════════════════════════════════════════════
class T5OQueEstaMissaoNaoPodiaTocar(unittest.TestCase):
    """RT11 · RT14 · RT15 · RT16."""

    def test_rt11_nenhum_segredo_do_youtube_e_lido_pela_prova_da_placa(self):
        t = _fonte('provas/gpu_asr_smoke.py')
        for chave in ('YOUTUBE_DATA_API_KEY', 'APIFY_TOKEN', 'APIFY_API'):
            self.assertNotIn(chave, t)

    def test_rt14_a_collection_nao_foi_tocada(self):
        base = '6ea058d3'
        r = subprocess.run(['git', 'diff', '--name-only', base, 'HEAD', '--',
                            'coleta/ingresso.py', 'orquestrador/', 'supabase/',
                            'leis/retorno_da_coleta.py'],
                           cwd=RAIZ, capture_output=True, text=True)
        if r.returncode:
            self.skipTest('a base comum nao esta alcancavel neste clone')
        self.assertEqual('', r.stdout.strip(),
                         'a convergencia tocou na Collection: %s' % r.stdout)

    def test_rt15_rt16_a_prova_da_placa_nao_adquire_video(self):
        """Precisar de transcrição não autoriza baixar vídeo."""
        arv = ast.parse(_fonte('provas/gpu_asr_smoke.py'))
        imp = set()
        for n in ast.walk(arv):
            if isinstance(n, ast.Import):
                imp.update(a.name.split('.')[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom):
                imp.add((n.module or '').split('.')[0])
        for mau in ('urllib', 'requests', 'yt_dlp', 'http', 'socket', 'apify_client'):
            self.assertNotIn(mau, imp)

    def test_o_modelo_so_e_aceite_se_ja_estiver_na_maquina(self):
        """§11 — se o modelo não está em cache, a prova para."""
        t = _fonte('provas/gpu_asr_smoke.py')
        self.assertIn('local_files_only=True', t)
        self.assertIn('MODEL_NOT_PRESENT', t)


if __name__ == '__main__':
    unittest.main(verbosity=2)
