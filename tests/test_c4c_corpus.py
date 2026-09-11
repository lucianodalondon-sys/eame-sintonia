#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DA C4C — recuperar não é recolher.

A C4B escreveu `SEM_CORPUS` depois de procurar `C-FanW_CYMz.wav` e não o
encontrar. O `.wav` é DERIVADO: quem está preservado com hash no manifesto é o
`.mp4`.

    PROCURAR O ARTEFATO ERRADO DA UMA RESPOSTA VERDADEIRA SOBRE OUTRA COISA.

E a lei que governa a missão inteira:

    PATH != IDENTIDADE. SHA != OBSERVACAO.
    AUSENCIA DE CORPUS NAO E AUTORIZACAO DE RECOLHER.
"""
import ast
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, 'provas'), os.path.join(RAIZ, 'ferramentas')):
    sys.path.insert(0, p)
import _gavetas                      # noqa: E402,F401
import fala_local as fl              # noqa: E402
import corpus_recuperar as cr        # noqa: E402

CENSO = 'provas/corpus_recuperar.py'
SENTINELA = 'C-FanW_CYMz'


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _manifesto():
    with io.open(os.path.join(RAIZ, cr.MANIFESTO), encoding='utf-8') as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════════
class T1OHashEQuemDecide(unittest.TestCase):
    """RT1 · RT3 — o caminho aponta; só o hash prova."""

    def test_nome_igual_com_bytes_diferentes_nao_passa(self):
        decl = None
        for it in _manifesto()['ITEMS']:
            r = it.get('RAW') or {}
            if str(r.get('STORAGE_LOCATION', '')).endswith('%s.mp4' % SENTINELA):
                decl = r['SHA256']
        self.assertIsNotNone(decl, 'o sentinela saiu do manifesto')
        tmp = tempfile.mkdtemp()
        falso = os.path.join(tmp, '%s.mp4' % SENTINELA)
        with io.open(falso, 'wb') as f:
            f.write(b'nao sou o mesmo video')
        h = hashlib.sha256(io.open(falso, 'rb').read()).hexdigest()
        self.assertNotEqual(h, decl,
                            'um ficheiro com o nome certo e bytes errados tem '
                            'de ser denunciado pelo hash')

    def test_o_vocabulario_separa_ausencia_de_divergencia(self):
        """`NOT_FOUND` e `HASH_MISMATCH` são coisas diferentes."""
        self.assertNotEqual(cr.NAO_ESTA, cr.HASH_DIFERENTE)
        for v in (cr.RECUPERADO, cr.NAO_ESTA, cr.HASH_DIFERENTE, cr.SEM_MANIFESTO):
            self.assertIsInstance(v, str)


# ══════════════════════════════════════════════════════════════════════════
class T2NaoHaAquisicaoNenhuma(unittest.TestCase):
    """RT6 — nenhum download escondido, e a lei está no vocabulário."""

    def test_o_censo_nao_importa_rede(self):
        arv = ast.parse(_fonte(CENSO))
        imp = set()
        for n in ast.walk(arv):
            if isinstance(n, ast.Import):
                imp.update(a.name.split('.')[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom):
                imp.add((n.module or '').split('.')[0])
        for mau in ('urllib', 'requests', 'yt_dlp', 'http', 'socket', 'apify_client'):
            self.assertNotIn(mau, imp, 'o censo importa %r — ele nao vai a rede' % mau)

    def test_nenhuma_chave_de_provedor_e_lida(self):
        t = _fonte(CENSO)
        for chave in ('YOUTUBE_DATA_API_KEY', 'APIFY_TOKEN', 'APIFY_API'):
            self.assertNotIn(chave, t)

    def test_o_censo_diz_que_not_found_nao_autoriza(self):
        """A regra tem de viajar com a resposta, não só na cabeça de quem lê."""
        d = cr.censo()
        self.assertIn('nao autoriza', d['O_QUE_ISTO_NAO_E'])


# ══════════════════════════════════════════════════════════════════════════
class T3ORawNaoEntraNoGit(unittest.TestCase):
    """RT5 — o bruto fica fora, e há quem confira."""

    def test_nenhum_media_rastreado(self):
        r = subprocess.run(['git', 'ls-files', 'data/raw'],
                           cwd=RAIZ, capture_output=True, text=True)
        maus = [x for x in r.stdout.split() if x.endswith(('.mp4', '.wav', '.m4a'))]
        self.assertEqual([], maus, 'media rastreada no Git: %s' % maus)

    def test_a_missao_nao_sujou_o_acervo(self):
        r = subprocess.run(['git', 'status', '--short', '--', 'data/raw'],
                           cwd=RAIZ, capture_output=True, text=True)
        self.assertEqual('', r.stdout.strip())


# ══════════════════════════════════════════════════════════════════════════
class T4AElegibilidadeExigeVerdade(unittest.TestCase):
    """RT2 · RT4 — bytes sem verdade de referência não são amostra de qualidade."""

    def test_amostra_sem_termos_nao_e_elegivel(self):
        d = cr.censo()
        com = [x for x in d['ITEMS']
               if x['RESULT'] == cr.RECUPERADO and (x['GROUND_TRUTH_TERMOS'] or 0) > 0]
        self.assertEqual(d['TOTAL_ELEGIVEIS'], len(com))
        self.assertLess(d['TOTAL_ELEGIVEIS'], d['TOTAL_DECLARADOS'],
                        'se tudo fosse elegivel, a verdade nao estaria a filtrar nada')

    def test_o_audio_sintetico_do_smoke_nao_entra_no_censo(self):
        """O smoke da C4B fabrica uma frase; ela nunca é corpus."""
        nomes = {os.path.basename(x['STORAGE_LOCATION']) for x in cr.censo()['ITEMS']}
        self.assertNotIn('frase.wav', nomes)


# ══════════════════════════════════════════════════════════════════════════
class T5OTraceNaoMenteSobreOFerro(unittest.TestCase):
    """RT7 · RT8 — herdado da C4B, e agora exercido sobre o banco."""

    def test_gpu_escolhida_com_queda_nao_diz_que_a_gpu_correu(self):
        t = {'DEVICE_REQUESTED': 'GPU', 'DEVICE_SELECTED': 'GPU',
             'ACCELERATOR': 'CUDA', 'WHY_FALLBACK': None}
        c = fl.carimbo('medium', t, fl.ASR_FALHOU)
        self.assertEqual(c['ASR_DEVICE_USED'], fl.NAO_SEI)
        self.assertEqual(c['ASR_DEVICE_EXECUTION'], fl.EXECUCAO_FALHOU)

    def test_queda_para_o_processador_nao_se_mascara(self):
        t = {'DEVICE_REQUESTED': 'GPU', 'DEVICE_SELECTED': 'CPU',
             'ACCELERATOR': 'NONE', 'WHY_FALLBACK': fl.GPU_INDISPONIVEL}
        c = fl.carimbo('medium', t, fl.OK)
        self.assertEqual(c['ASR_DEVICE_USED'], fl.CPU)
        self.assertEqual(c['ASR_WHY_FALLBACK'], fl.GPU_INDISPONIVEL)


# ══════════════════════════════════════════════════════════════════════════
class T6OBancoNaoSeDeixaComparar(unittest.TestCase):
    """RT10 · RT11 · RT12 — comparar exige as mesmas condições."""

    def test_o_banco_publica_o_modelo_de_cada_linha(self):
        """Sem o modelo na linha, dois dispositivos podem correr modelos diferentes."""
        t = _fonte('provas/asr_banco.py')
        self.assertIn("'ASR_MODEL': r.get('ASR_MODEL')", t)

    def test_preparar_o_modelo_nao_conta_como_ouvir(self):
        """RT12 — a cicatriz da C4: 204 s de download saíram como timeout do áudio."""
        t = _fonte('ferramentas/fala_local.py')
        self.assertIn('MODEL_PREPARE_SECONDS', t)
        i, j = t.index('t_prep = time.time()'), t.index('t0 = time.time()')
        self.assertLess(i, j, 'o relogio da inferencia tem de arrancar DEPOIS '
                              'de o modelo estar pronto')

    def test_o_banco_le_a_execucao_e_nao_so_a_escolha(self):
        t = _fonte('provas/asr_banco.py')
        self.assertIn("'DEVICE_EXECUTION'", t)


# ══════════════════════════════════════════════════════════════════════════
class T7UmaAmostraNaoEUmBenchmark(unittest.TestCase):
    """RT13 — o limite tem de estar escrito onde alguém o leia."""

    DOC = 'docs/sintonia-scrap/C4-RUNNER-LOCAL-GPU-ASR.md'

    def test_o_documento_nao_promove_amostra_a_corpus(self):
        d = _fonte(self.DOC)
        self.assertIn('GPU_QUALITY_BENCHMARK = NOT_RUN', d)
        self.assertIn('UMA AMOSTRA E UMA AMOSTRA', d)

    def test_o_speedup_nao_foi_inventado(self):
        d = _fonte(self.DOC)
        self.assertIn('GPU_SPEEDUP_VS_CPU   NOT_MEASURED', d)

    def test_asr_owners_continua_um(self):
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
        self.assertEqual(sorted(set(donos)), ['ferramentas/fala_local.py'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
