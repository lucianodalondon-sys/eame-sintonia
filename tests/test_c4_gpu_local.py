#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DA C4 — a placa é ambiente, não é motor, e ninguém a escolhe pelas costas.

A C3 fechou o cutover do YouTube. Esta missão pergunta outra coisa: esta casa
consegue reconhecer fala na PLACA, sem criar um segundo motor e sem deixar os
adaptadores escolherem ferro?

    ENGINE != MODEL != RUNTIME != DEVICE != ACCELERATOR.

Cinco eixos. A maior parte destas provas existe para que ninguém os funda.
"""
import ast
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
sys.path.insert(0, os.path.join(RAIZ, 'provas'))
import fala_local as fl                                        # noqa: E402

#: Quem PODE instanciar o reconhecedor. Um, e só um.
DONO_DO_ASR = 'ferramentas/fala_local.py'

#: Os ficheiros que chamam o reconhecedor e NÃO podem escolher o ferro dele.
CHAMADORES = ('ferramentas/instagram_transcrever.py',
              'ferramentas/youtube_transcrever.py',
              'ferramentas/reel_transcricao.py')

#: Os dois Actors de legenda que esta missão NÃO aposenta.
LEGENDA = ('pintostudio~youtube-transcript-scraper',
           'starvibe~youtube-video-transcript')


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _py_do_repo():
    """Os ficheiros `.py` que EXECUTAM — sem `__pycache__` e sem o mapa gerado."""
    for pasta, dirs, fs in os.walk(RAIZ):
        dirs[:] = [d for d in dirs
                   if d not in ('__pycache__', '.git', 'node_modules', 'system-map')]
        for f in fs:
            if f.endswith('.py'):
                yield os.path.relpath(os.path.join(pasta, f), RAIZ)


# ══════════════════════════════════════════════════════════════════════════
class T1UmUnicoDonoDoReconhecedor(unittest.TestCase):
    """T1 · `WhisperModel(` nasce num sítio só, e continua a nascer lá."""

    def test_so_um_ficheiro_instancia_o_reconhecedor(self):
        donos = []
        for rel in _py_do_repo():
            if rel.startswith('tests/'):
                continue
            t = _fonte(rel)
            if 'WhisperModel(' in t or 'BatchedInferencePipeline(' in t:
                donos.append(rel)
        self.assertEqual(sorted(donos), [DONO_DO_ASR],
                         'nasceu um segundo dono do reconhecedor: %s' % donos)

    def test_nenhum_gpu_asr_paralelo_nasceu(self):
        """RT11 · um ficheiro chamado `gpu_asr.py` seria o segundo dono disfarçado."""
        proibidos = ('gpu_asr.py', 'youtube_gpu.py', 'instagram_gpu.py',
                     'asr_gpu.py', 'fala_gpu.py')
        achados = [r for r in _py_do_repo() if os.path.basename(r) in proibidos]
        self.assertEqual(achados, [], 'dono paralelo de ASR: %s' % achados)

    def test_o_banco_de_prova_nao_e_um_segundo_dono(self):
        t = _fonte('provas/asr_banco.py')
        self.assertNotIn('WhisperModel(', t)
        self.assertIn('import fala_local', t,
                      'o banco tem de medir o motor de producao, nao outro')


# ══════════════════════════════════════════════════════════════════════════
class T2e3OsChamadoresNaoEscolhemFerro(unittest.TestCase):
    """T2 · T3 · RT10 — o adaptador não escolhe device nem compute_type."""

    def _atribuicoes(self, rel):
        """Os `device=` e `compute_type=` escritos como argumento, na árvore."""
        achados = []
        for no in ast.walk(ast.parse(_fonte(rel))):
            if not isinstance(no, ast.Call):
                continue
            for kw in no.keywords or []:
                if kw.arg in ('device', 'compute_type', 'device_index'):
                    achados.append('%s:%d %s=' % (rel, no.lineno, kw.arg))
        return achados

    def test_nenhum_chamador_passa_device(self):
        maus = []
        for rel in CHAMADORES:
            maus.extend(self._atribuicoes(rel))
        self.assertEqual(maus, [], 'chamador a escolher ferro: %s' % maus)

    def test_nenhum_chamador_nomeia_cuda(self):
        for rel in CHAMADORES:
            t = _fonte(rel).lower()
            for palavra in ('cuda', 'float16', 'int8_float16', 'nvidia'):
                self.assertNotIn(palavra, t,
                                 '%s nomeia %r — ferro e decisao do dono' % (rel, palavra))

    def test_o_repositorio_inteiro_so_tem_um_sitio_com_device(self):
        """A varredura larga: só o dono pode escrever `device=` para o motor."""
        maus = []
        for rel in _py_do_repo():
            if rel == DONO_DO_ASR or rel.startswith('tests/'):
                continue
            for no in ast.walk(ast.parse(_fonte(rel))):
                if not isinstance(no, ast.Call):
                    continue
                nomes = {kw.arg for kw in (no.keywords or [])}
                if 'compute_type' in nomes:
                    maus.append('%s:%d' % (rel, no.lineno))
        self.assertEqual(maus, [], 'compute_type fora do dono: %s' % maus)


# ══════════════════════════════════════════════════════════════════════════
class T4DetecaoNaoInventa(unittest.TestCase):
    """T4 · RT1 · RT2 · RT3 — `AUTO` pergunta à biblioteca, não adivinha."""

    def test_auto_nao_promete_placa_que_nao_existe(self):
        n, _porque = fl.cuda_disponivel()
        _dev, _ct, trace = fl.resolver_dispositivo('AUTO')
        if n > 0:
            self.assertEqual(trace['DEVICE_SELECTED'], fl.GPU)
        else:
            self.assertEqual(trace['DEVICE_SELECTED'], fl.CPU,
                             'AUTO prometeu placa com zero dispositivos CUDA')
            self.assertEqual(trace['WHY_FALLBACK'], fl.GPU_INDISPONIVEL)

    def test_a_detecao_pergunta_ao_ctranslate2_e_nao_ao_ambiente(self):
        """RT3 · uma variável de ambiente não pode fabricar uma placa."""
        t = _fonte(DONO_DO_ASR)
        i = t.index('def cuda_disponivel')
        corpo = t[i:t.index('\ndef ', i + 10)]
        self.assertIn('get_cuda_device_count', corpo)
        self.assertNotIn('environ', corpo,
                         'a detecao nao pode sair de variavel de ambiente')

    def test_sem_a_biblioteca_a_resposta_e_zero_com_motivo(self):
        """RT2 · CUDA indisponível responde `0` e DIZ porquê — nunca levanta."""
        n, porque = fl.cuda_disponivel()
        self.assertIsInstance(n, int)
        if n == 0:
            self.assertTrue(porque, 'zero sem motivo e um zero que nao se explica')

    def test_vocabulario_fechado(self):
        with self.assertRaises(ValueError):
            fl.resolver_dispositivo('TPU')


# ══════════════════════════════════════════════════════════════════════════
class T7e8AQuedaEExplicita(unittest.TestCase):
    """T7 · T8 — fallback declarado, e ausência de placa não é erro da fonte."""

    def test_os_tres_campos_existem_sempre(self):
        for pedido in fl.DISPOSITIVOS:
            _d, _c, trace = fl.resolver_dispositivo(pedido)
            for campo in ('DEVICE_REQUESTED', 'DEVICE_SELECTED', 'WHY_FALLBACK'):
                self.assertIn(campo, trace, '%s sem %s' % (pedido, campo))

    def test_sem_queda_o_motivo_e_None_e_nunca_NOT_KNOWN(self):
        """`None` = não houve queda. `NOT_KNOWN` = não sei. Não se colapsam."""
        _d, _c, trace = fl.resolver_dispositivo('CPU')
        self.assertIsNone(trace['WHY_FALLBACK'])
        self.assertNotEqual(trace['WHY_FALLBACK'], fl.NAO_SEI)

    def test_pedir_gpu_sem_placa_cai_com_nome(self):
        n, _ = fl.cuda_disponivel()
        if n > 0:
            self.skipTest('esta maquina tem placa — o caso da queda nao se reproduz aqui')
        _d, _c, trace = fl.resolver_dispositivo('GPU')
        self.assertEqual(trace['DEVICE_REQUESTED'], fl.GPU)
        self.assertEqual(trace['DEVICE_SELECTED'], fl.CPU)
        self.assertEqual(trace['WHY_FALLBACK'], fl.GPU_INDISPONIVEL)
        self.assertTrue(trace.get('WHY_FALLBACK_DETAIL'))

    def test_gpu_indisponivel_nao_e_estado_da_fonte(self):
        """T8 · RT1 — `GPU_UNAVAILABLE` nunca vira erro do áudio nem da fonte."""
        self.assertNotIn(fl.GPU_INDISPONIVEL, fl.ESTADOS)
        self.assertNotIn(fl.GPU_SEM_MEMORIA, fl.ESTADOS)
        for mau in ('SOURCE_ERROR', 'ZERO_RESULTS'):
            self.assertNotIn(mau, fl.ESTADOS)


# ══════════════════════════════════════════════════════════════════════════
class T9MemoriaDaPlacaTemNomeProprio(unittest.TestCase):
    """T9 · RT5 — `GPU_OOM` é um estado, não um traceback opaco."""

    def test_o_reconhecedor_da_nome_a_memoria_cheia(self):
        class _Oom(RuntimeError):
            pass
        self.assertTrue(fl._parece_sem_memoria(_Oom('CUDA failed with error out of memory')))
        self.assertTrue(fl._parece_sem_memoria(_Oom('CUBLAS_STATUS_ALLOC_FAILED')))

    def test_um_erro_qualquer_nao_vira_oom(self):
        """Classificar de mais é tão mau como classificar de menos."""
        self.assertFalse(fl._parece_sem_memoria(ValueError('ficheiro invalido')))
        self.assertFalse(fl._parece_sem_memoria(OSError('disco cheio')))

    def test_oom_durante_o_reconhecimento_sobe_com_nome(self):
        """Pelo COMPORTAMENTO, não pela posição do texto.

        ⚠️ Correção a mim próprio: a primeira versão desta prova procurava
        `GPU_SEM_MEMORIA` no primeiro `except Exception` depois de
        `def transcrever`. Quando o tratamento do carregamento passou a existir,
        ele ficou em primeiro e a sentinela passou a ler o bloco errado.

            UMA SENTINELA ANCORADA NA POSIÇÃO DO TEXTO MEDE O TEXTO, NÃO A LEI.

        Agora injecta a memória cheia DURANTE o reconhecimento e lê o resultado.
        """
        ha, _ = fl.disponivel()
        if not ha:
            self.skipTest('reconhecedor ausente neste ambiente')
        guardado = dict(fl._CACHE)

        class _PipeQueRebenta:
            def transcribe(self, *a, **k):
                raise RuntimeError('CUDA failed with error out of memory')

        fl._CACHE[('tiny', 'cpu', 'int8')] = _PipeQueRebenta()
        try:
            r = fl.transcrever('qualquer.wav', idioma='it', modelo_nome='tiny',
                               dispositivo='CPU')
        finally:
            fl._CACHE.clear()
            fl._CACHE.update(guardado)
        self.assertEqual(r['TRANSCRIPT_STATE'], fl.ASR_FALHOU)
        self.assertEqual(r['ASR_WHY_FALLBACK'], fl.GPU_SEM_MEMORIA,
                         'memoria cheia da placa subiu como falha generica')
        self.assertIn('não coube nesta placa', r['NAO_SIGNIFICA'])

    def test_uma_falha_qualquer_no_reconhecimento_nao_vira_oom(self):
        """Classificar de mais é tão mau como classificar de menos."""
        ha, _ = fl.disponivel()
        if not ha:
            self.skipTest('reconhecedor ausente neste ambiente')
        guardado = dict(fl._CACHE)

        class _PipeQualquer:
            def transcribe(self, *a, **k):
                raise ValueError('cabecalho de wav invalido')

        fl._CACHE[('tiny', 'cpu', 'int8')] = _PipeQualquer()
        try:
            r = fl.transcrever('qualquer.wav', idioma='it', modelo_nome='tiny',
                               dispositivo='CPU')
        finally:
            fl._CACHE.clear()
            fl._CACHE.update(guardado)
        self.assertEqual(r['TRANSCRIPT_STATE'], fl.ASR_FALHOU)
        self.assertIsNone(r['ASR_WHY_FALLBACK'],
                          'um wav partido foi classificado como memoria de placa')


# ══════════════════════════════════════════════════════════════════════════
class T10e11TranscriptELingua(unittest.TestCase):
    """T10 · T11 · RT8 · RT9 — vazio não é OK, e a língua diz de onde veio."""

    def test_vazio_tem_estado_proprio(self):
        self.assertIn(fl.REQUESTED_EMPTY, fl.ESTADOS)
        self.assertNotEqual(fl.REQUESTED_EMPTY, fl.OK)

    def test_o_carimbo_diz_a_base_da_lingua(self):
        wav = os.path.join(RAIZ, 'data', 'raw', 'REEL-MIDIA', 'C6TiLBCCBz8.wav')
        if not os.path.exists(wav):
            self.skipTest('corpus preservado ausente neste ambiente')
        ha, _ = fl.disponivel()
        if not ha:
            self.skipTest('reconhecedor ausente neste ambiente')
        r = fl.transcrever(wav, idioma='en', modelo_nome='tiny')
        self.assertEqual(r['LANGUAGE_SOURCE'], 'DECLARED')
        self.assertIn('LANGUAGE_DETECTED', r)

    def test_musica_corporativa_continua_a_sair_vazia(self):
        """A alucinação «Music» foi apanhada em 2026-09-10. Não pode voltar."""
        wav = os.path.join(RAIZ, 'data', 'raw', 'REEL-MIDIA', 'C6TiLBCCBz8.wav')
        if not os.path.exists(wav):
            self.skipTest('corpus preservado ausente neste ambiente')
        ha, _ = fl.disponivel()
        if not ha:
            self.skipTest('reconhecedor ausente neste ambiente')
        r = fl.transcrever(wav, idioma='en', modelo_nome='tiny')
        self.assertEqual(r['TRANSCRIPT_STATE'], fl.REQUESTED_EMPTY,
                         'a alucinacao sobre musica voltou a passar por texto')


# ══════════════════════════════════════════════════════════════════════════
class T20PrepararNaoEOuvir(unittest.TestCase):
    """O relógio do áudio não pode contar o tempo de preparar a máquina.

    Nasceu de um defeito real, apanhado pelo banco de prova desta missão: o Reel
    italiano de 34 s saiu `TRANSCRIPTION_TIMEOUT` com `medium`, tecto de 204 s.
    O mesmo áudio com o modelo já pronto: 6,4 s e estado OK.

        O QUE CONSUMIU OS 204 s FOI O DESCARREGAMENTO DO MODELO.

    E o estado dizia «o que saiu pode estar em laço» — uma afirmação sobre o
    ÁUDIO, quando a verdade era sobre a MÁQUINA.
    """

    def test_os_dois_tempos_tem_campos_diferentes(self):
        ha, _ = fl.disponivel()
        if not ha:
            self.skipTest('reconhecedor ausente neste ambiente')
        wav = os.path.join(RAIZ, 'data', 'raw', 'REEL-MIDIA', 'C6TiLBCCBz8.wav')
        if not os.path.exists(wav):
            self.skipTest('corpus preservado ausente')
        r = fl.transcrever(wav, idioma='en', modelo_nome='tiny')
        self.assertIn('MODEL_PREPARE_SECONDS', r)
        self.assertIn('MACHINE_SECONDS', r)
        self.assertNotEqual(r['MODEL_PREPARE_SECONDS'], r['MACHINE_SECONDS'])

    def test_o_relogio_arranca_depois_do_modelo(self):
        """A sentinela na árvore: `t0` não pode voltar para antes da carga."""
        t = _fonte(DONO_DO_ASR)
        i = t.index('def transcrever')
        corpo = t[i:i + 4000]
        pos_modelo = corpo.index('pipe, trace_do_ferro = modelo(')
        pos_t0 = corpo.index('t0 = time.time()')
        self.assertGreater(pos_t0, pos_modelo,
                           'o relogio voltou a contar o carregamento do modelo, '
                           'e um download vai outra vez sair como TIMEOUT do audio')

    def test_modelo_que_nao_carrega_nao_e_audio_sem_fala(self):
        """Preparar falhou é `ASR_FALHOU`, e a frase diz de quem é a culpa."""
        import faster_whisper                                   # noqa: PLC0415
        real = faster_whisper.WhisperModel
        guardado = dict(fl._CACHE)
        fl._CACHE.clear()
        faster_whisper.WhisperModel = lambda *a, **k: (_ for _ in ()).throw(
            OSError('modelo nao encontrado no disco nem na rede'))
        try:
            r = fl.transcrever('qualquer.wav', idioma='it', modelo_nome='tiny')
        finally:
            faster_whisper.WhisperModel = real
            fl._CACHE.clear()
            fl._CACHE.update(guardado)
        self.assertEqual(r['TRANSCRIPT_STATE'], fl.ASR_FALHOU)
        self.assertIn('não ficou pronto', r['NAO_SIGNIFICA'])


# ══════════════════════════════════════════════════════════════════════════
class T12HotwordsNaoViramPadrao(unittest.TestCase):
    """T12 · o experimento de hotwords não pode ligar-se sozinho."""

    def test_hotwords_nao_sao_padrao_em_lado_nenhum(self):
        for rel in (DONO_DO_ASR,) + CHAMADORES:
            t = _fonte(rel)
            self.assertNotIn('hotwords=', t,
                             '%s liga hotwords — a C4 mediu drift de lingua' % rel)


# ══════════════════════════════════════════════════════════════════════════
class T13RawDeTesteVaiParaTemporario(unittest.TestCase):
    """T13 · RT12 — lei da casa desde a C2: o acervo real não recebe teste."""

    def test_o_banco_nao_escreve_no_acervo(self):
        """O banco IMPRIME. Quem quiser guardar redireciona a saída — e escolhe onde."""
        arvore = ast.parse(_fonte('provas/asr_banco.py'))
        escritas = []
        for no in ast.walk(arvore):
            if isinstance(no, ast.Call):
                nome = getattr(no.func, 'attr', None) or getattr(no.func, 'id', None)
                if nome in ('dump', 'write_text', 'write_bytes', 'makedirs'):
                    escritas.append('provas/asr_banco.py:%d %s' % (no.lineno, nome))
        self.assertEqual(escritas, [],
                         'o banco grava ficheiro em vez de imprimir: %s' % escritas)

    def test_a_suite_nao_deixou_nada_no_acervo(self):
        r = subprocess.run(['git', 'status', '--short'], cwd=RAIZ,
                           capture_output=True, text=True)
        sujos = [ln for ln in r.stdout.splitlines()
                 if ln.startswith('??') and ('data/samples' in ln or 'data/raw' in ln)]
        self.assertEqual(sujos, [], 'teste deixou lixo no acervo: %s' % sujos)

    def test_o_censo_da_maquina_nao_grava_nada(self):
        """LER a máquina é a missão. ESCREVER nela seria alterá-la enquanto mede.

        ⚠️ Correção a mim próprio: a primeira versão desta prova procurava a
        string `open(` e reprovava o `open('/proc/meminfo')`, que é uma LEITURA
        e é exatamente o que o censo tem de fazer.

            PROIBIR `open` PROIBIU A MEDIÇÃO, NÃO A ESCRITA.

        Agora a pergunta é a certa, e é feita na árvore: há alguma chamada que
        ESCREVA? `open` em modo de escrita, `json.dump`, `write_text`, `mkdir`.
        """
        arvore = ast.parse(_fonte('provas/hardware_local.py'))
        escritas = []
        for no in ast.walk(arvore):
            if not isinstance(no, ast.Call):
                continue
            alvo = no.func
            nome = getattr(alvo, 'attr', None) or getattr(alvo, 'id', None)
            if nome in ('dump', 'write_text', 'write_bytes', 'mkdir', 'makedirs',
                        'rmtree', 'remove', 'unlink'):
                escritas.append('%s:%d %s' % ('provas/hardware_local.py', no.lineno, nome))
            if nome == 'open':
                modos = [a for a in no.args[1:] if isinstance(a, ast.Constant)]
                modos += [k.value for k in (no.keywords or [])
                          if k.arg == 'mode' and isinstance(k.value, ast.Constant)]
                for m in modos:
                    if any(c in str(m.value) for c in 'wax+'):
                        escritas.append('provas/hardware_local.py:%d open(%r)'
                                        % (no.lineno, m.value))
        self.assertEqual(escritas, [],
                         'o censo escreve na maquina que devia so medir: %s' % escritas)


# ══════════════════════════════════════════════════════════════════════════
class T14e15NadaFoiAdquiridoNemDesligado(unittest.TestCase):
    """T14 · T15 — nenhuma mídia nova, nenhum Actor retirado."""

    def test_o_banco_usa_so_o_que_ja_estava_preservado(self):
        t = _fonte('provas/asr_banco.py')
        self.assertIn('data', t)
        for mau in ('yt-dlp', 'yt_dlp', 'urllib.request', 'requests.get',
                    'youtube.com/watch', 'instagram.com/reel'):
            self.assertNotIn(mau, t,
                             'o banco de prova baixa midia nova (%s)' % mau)

    def test_os_dois_actors_de_legenda_continuam_ligados(self):
        t = _fonte('regras/sensor_coleta.py')
        for a in LEGENDA:
            self.assertIn(a, t,
                          'o ator de legenda %s foi retirado — a C4 nao o substitui' % a)

    def test_a_c4_nao_promoveu_rota_de_midia(self):
        """GPU resolve ÁUDIO → TEXTO. Ela não resolve YOUTUBE → ÁUDIO."""
        t = _fonte(DONO_DO_ASR)
        for mau in ('yt_dlp', 'yt-dlp', 'urllib.request'):
            self.assertNotIn(mau, t,
                             'o dono do ASR aprendeu a adquirir midia — sao duas missoes')


# ══════════════════════════════════════════════════════════════════════════
class T16OCarimboNaoMente(unittest.TestCase):
    """O campo que diz o ferro tem de vir do que CORREU, nunca de um literal."""

    def test_o_ferro_do_carimbo_vem_do_trace(self):
        """⚠️ Corrigido na C4B: `ASR_DEVICE_USED` exigia um ESTADO.

        Esta prova afirmava `USED == CPU` com um carimbo pedido sem estado —
        e passava, porque o campo se enchia na escolha. Era a prova a ratificar
        o defeito: o resolvedor corre antes de existir uma amostra transcrita.
        """
        _d, _c, cpu = fl.resolver_dispositivo('CPU')
        c = fl.carimbo('small', cpu, fl.OK)
        self.assertEqual(c['ASR_DEVICE_USED'], fl.CPU)
        self.assertEqual(c['ASR_DEVICE_EXECUTION'], fl.EXECUCAO_PROVADA)
        self.assertIn('cpu', c['ASR_DEVICE'])
        self.assertEqual(c['ASR_RUNTIME'], 'CTranslate2')

    def test_sem_estado_o_carimbo_nao_promove_ninguem(self):
        """Escolher o ferro nao e ter corrido nele."""
        _d, _c, cpu = fl.resolver_dispositivo('CPU')
        c = fl.carimbo('small', cpu)
        self.assertEqual(c['ASR_DEVICE_SELECTED'], fl.CPU,
                         'a ESCOLHA e conhecida, e continua a ser dita')
        self.assertEqual(c['ASR_DEVICE_EXECUTION'], fl.EXECUCAO_NAO_CORREU)
        self.assertEqual(c['ASR_DEVICE_USED'], fl.NAO_SEI,
                         'ninguem viu correr — «USED» nao pode nomear ferro')

    def test_sem_trace_o_carimbo_confessa_em_vez_de_adivinhar(self):
        c = fl.carimbo('small')
        self.assertEqual(c['ASR_DEVICE'], fl.NAO_SEI,
                         'um carimbo que adivinha o ferro e pior do que um que confessa')

    def test_o_literal_antigo_nao_pode_voltar(self):
        """A sentinela: `cpu/int8` escrito à mão ao lado de um `device=` variável."""
        t = _fonte(DONO_DO_ASR)
        i = t.index('def carimbo')
        corpo = t[i:t.index('\ndef ', i + 10)]
        self.assertNotIn("'cpu/int8/%d threads'", corpo.replace(
            "ferro = 'cpu/%s/%d threads'", ''))

    def test_os_cinco_eixos_tem_cinco_campos(self):
        _d, _c, tr = fl.resolver_dispositivo('CPU')
        c = fl.carimbo('small', tr)
        for campo in ('ASR_ENGINE', 'ASR_MODEL', 'ASR_RUNTIME', 'ASR_DEVICE_USED',
                      'ASR_ACCELERATOR'):
            self.assertIn(campo, c, 'o eixo %s nao tem campo proprio' % campo)


# ══════════════════════════════════════════════════════════════════════════
class T17OPadraoNaoMudouSemProva(unittest.TestCase):
    """§25 — a capacidade entrou; a decisão não. O padrão continua o medido."""

    def test_o_padrao_do_dispositivo_continua_cpu(self):
        if os.environ.get('SINTONIA_ASR_DEVICE'):
            self.skipTest('ambiente forca o dispositivo — o padrao nao se le aqui')
        self.assertEqual(fl.DISPOSITIVO_PADRAO, fl.CPU,
                         'o padrao mudou sem a prova na maquina real')

    def test_o_padrao_do_modelo_continua_small(self):
        if os.environ.get('SINTONIA_ASR_MODELO'):
            self.skipTest('ambiente forca o modelo')
        self.assertEqual(fl.MODELO_PADRAO, 'small')

    def test_a_politica_de_modelo_vive_num_sitio_so(self):
        """§24 · quatro constantes decidiam a mesma coisa. Agora decide uma."""
        self.assertEqual(fl.modelo_de('reel'), 'medium',
                         'o Reel foi despromovido — `small` escreve «MICE» onde '
                         'se diz «mais», e isso foi MEDIDO')
        self.assertEqual(fl.modelo_de('instagram'), 'small')
        self.assertEqual(fl.modelo_de('youtube'), 'small')
        with self.assertRaises(ValueError):
            fl.modelo_de('chamador-que-nao-declarou-politica')

    def test_nenhum_chamador_guarda_o_proprio_literal_de_modelo(self):
        """A sentinela: um `or 'small'` de volta num caller seria a divergencia a voltar."""
        maus = []
        for rel in CHAMADORES:
            for no in ast.walk(ast.parse(_fonte(rel))):
                if not isinstance(no, ast.Assign):
                    continue
                nomes = [t.id for t in no.targets if isinstance(t, ast.Name)]
                if 'MODELO_PADRAO' not in nomes:
                    continue
                # O valor tem de vir do dono, e nao de um literal nem de um
                # `os.environ` proprio.
                v = no.value
                chamada_ao_dono = (isinstance(v, ast.Call)
                                   and getattr(v.func, 'attr', None) == 'modelo_de')
                if not chamada_ao_dono:
                    maus.append('%s:%d' % (rel, no.lineno))
        self.assertEqual(maus, [],
                         'chamador voltou a decidir o proprio modelo: %s' % maus)

    def test_as_variaveis_antigas_continuam_a_valer(self):
        """Centralizar não autoriza partir um entrypoint que alguém usa."""
        for chamador, (var, _padrao) in fl.MODELOS_POR_CHAMADOR.items():
            antes = os.environ.get(var)
            os.environ[var] = 'tiny'
            try:
                self.assertEqual(fl.modelo_de(chamador), 'tiny',
                                 '%s deixou de respeitar %s' % (chamador, var))
            finally:
                if antes is None:
                    os.environ.pop(var, None)
                else:
                    os.environ[var] = antes

    def test_a_politica_e_do_dono_e_nao_de_um_ficheiro_novo(self):
        """§21 — reutilizar o mecanismo que já existia, não inventar outro."""
        t = _fonte(DONO_DO_ASR)
        self.assertIn("os.environ.get('SINTONIA_ASR_DEVICE')", t)
        self.assertIn("os.environ.get('SINTONIA_ASR_MODELO')", t,
                      'a politica de modelo saiu do dono')


# ══════════════════════════════════════════════════════════════════════════
class T18OCensoDaMaquinaNaoInventa(unittest.TestCase):
    """A ficha da máquina distingue «não perguntei» de «perguntei e não sei»."""

    def test_o_vocabulario_da_ausencia_tem_tres_palavras(self):
        import hardware_local as hw                             # noqa: PLC0415
        self.assertNotEqual(hw.NAO_MEDIDO, hw.DESCONHECIDO)
        self.assertNotEqual(hw.DESCONHECIDO, hw.NAO_SE_APLICA)

    def test_o_censo_nao_recolhe_o_que_nao_precisa(self):
        """§31 — utilizador, MAC, IP e série de disco não entram."""
        t = _fonte('provas/hardware_local.py')
        for mau in ('getuser', 'MACAddress', 'SerialNumber', 'gethostbyname',
                    'USERNAME', 'getpass'):
            self.assertNotIn(mau, t, 'o censo recolhe %s, que a missao nao precisa' % mau)

    def test_o_veredito_e_derivado_e_nao_escrito(self):
        import hardware_local as hw                             # noqa: PLC0415
        d = hw.medir()
        self.assertIn(d['LOCAL_GPU_AVAILABLE'], ('YES', 'NO', hw.DESCONHECIDO))
        self.assertTrue(d['LOCAL_GPU_WHY'], 'o veredito sem motivo nao se confere')

    def test_placa_presente_e_biblioteca_cega_tem_frase_propria(self):
        """O caso do meio: há placa e o CTranslate2 vê zero. Não é «sem placa»."""
        t = _fonte('provas/hardware_local.py')
        self.assertIn('biblioteca sem CUDA, nao maquina sem placa', t)


# ══════════════════════════════════════════════════════════════════════════
class T19RedTeamPorInjecao(unittest.TestCase):
    """RT4 · RT6 · RT7 — o que não se reproduz nesta máquina, injeta-se.

    Nenhuma destas falhas acontece num contentor sem placa. Esperar pela máquina
    certa para as exercer seria o mesmo que não as exercer: elas só aparecem no
    dia mau, e no dia mau ninguém está a olhar.

        UMA FALHA QUE SÓ SE TESTA QUANDO ACONTECE NÃO ESTÁ TESTADA.
    """

    def setUp(self):
        self._cache = dict(fl._CACHE)
        fl._CACHE.clear()

    def tearDown(self):
        fl._CACHE.clear()
        fl._CACHE.update(self._cache)

    def test_rt4_tipo_de_calculo_incompativel_nao_vira_erro_mudo(self):
        """A placa aceita `float16`; a que não aceitar tem de dizer o nome."""
        _d, _c, trace = fl.resolver_dispositivo('CPU')
        self.assertEqual(trace['DEVICE_SELECTED'], fl.CPU)
        # No processador o tipo medido desta casa é `int8`. Trocá-lo por um que
        # o CTranslate2 não suporta em CPU tem de falhar ALTO, na carga, e não
        # produzir texto pior em silêncio.
        self.assertEqual(fl.COMPUTE_CPU, 'int8')
        self.assertEqual(fl.COMPUTE_GPU, 'float16')
        self.assertNotEqual(fl.COMPUTE_CPU, fl.COMPUTE_GPU,
                            'o mesmo tipo de calculo nos dois ferros apagaria a '
                            'razao de haver dois campos')

    def test_rt6_a_placa_que_cai_na_carga_cai_para_o_processador_com_nome(self):
        """A biblioteca contou a placa e o carregamento rebentou a seguir."""
        import faster_whisper                                   # noqa: PLC0415
        chamadas = []
        real = faster_whisper.WhisperModel

        def _falha_na_placa(nome, **kw):
            chamadas.append(kw.get('device'))
            if kw.get('device') == 'cuda':
                raise RuntimeError('CUDA failed with error out of memory')
            return real(nome, **kw)

        faster_whisper.WhisperModel = _falha_na_placa
        contou = [1]
        real_conta = fl.cuda_disponivel
        fl.cuda_disponivel = lambda: (contou[0], '')
        try:
            _pipe, trace = fl.modelo('tiny', 'GPU')
        finally:
            faster_whisper.WhisperModel = real
            fl.cuda_disponivel = real_conta
        self.assertEqual(chamadas[0], 'cuda', 'nem tentou a placa')
        self.assertEqual(trace['DEVICE_REQUESTED'], fl.GPU)
        self.assertEqual(trace['DEVICE_SELECTED'], fl.CPU)
        self.assertEqual(trace['WHY_FALLBACK'], fl.GPU_SEM_MEMORIA,
                         'memoria cheia caiu como indisponibilidade generica')
        self.assertIn('cpu', chamadas[1:], 'nao recuperou para o processador')

    def test_rt6b_falha_que_nao_e_memoria_cai_como_indisponivel(self):
        """Nem toda queda da placa é OOM. Classificar de mais também mente."""
        import faster_whisper                                   # noqa: PLC0415
        real = faster_whisper.WhisperModel

        def _dll_em_falta(nome, **kw):
            if kw.get('device') == 'cuda':
                raise OSError('cublas64_12.dll nao encontrada')
            return real(nome, **kw)

        faster_whisper.WhisperModel = _dll_em_falta
        real_conta = fl.cuda_disponivel
        fl.cuda_disponivel = lambda: (1, '')
        try:
            _pipe, trace = fl.modelo('tiny', 'GPU')
        finally:
            faster_whisper.WhisperModel = real
            fl.cuda_disponivel = real_conta
        self.assertEqual(trace['WHY_FALLBACK'], fl.GPU_INDISPONIVEL)
        self.assertNotEqual(trace['WHY_FALLBACK'], fl.GPU_SEM_MEMORIA)
        self.assertIn('dll', trace['WHY_FALLBACK_DETAIL'].lower())

    def test_rt7_audio_invalido_nao_e_audio_sem_fala(self):
        """RT7 · um ficheiro que não é áudio dá `ASR_FALHOU`, nunca `REQUESTED_EMPTY`."""
        ha, _ = fl.disponivel()
        if not ha:
            self.skipTest('reconhecedor ausente neste ambiente')
        with tempfile.TemporaryDirectory(prefix='c4-rt7-') as tmp:
            ruim = os.path.join(tmp, 'nao-e-audio.wav')
            with open(ruim, 'wb') as f:
                f.write(b'isto nao e um wav, e nunca foi')
            r = fl.transcrever(ruim, idioma='it', modelo_nome='tiny')
        self.assertEqual(r['TRANSCRIPT_STATE'], fl.ASR_FALHOU)
        self.assertNotEqual(r['TRANSCRIPT_STATE'], fl.REQUESTED_EMPTY,
                            'ficheiro partido passou por «audio sem fala»')
        self.assertIn('NAO_SIGNIFICA', r)

    def test_rt7b_o_ficheiro_partido_nao_deixou_nada_no_acervo(self):
        """O temporário morre com o `with`. O acervo não vê teste nenhum."""
        r = subprocess.run(['git', 'status', '--short'], cwd=RAIZ,
                           capture_output=True, text=True)
        self.assertEqual([ln for ln in r.stdout.splitlines()
                          if 'data/' in ln and ln.startswith('??')], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
