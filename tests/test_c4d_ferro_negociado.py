#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DA C4D — a placa estava la, e o artefato dizia que nao havia placa.

A C4B provou que esta casa consegue transcrever na GPU. Provou-o **pelo
workflow**, com `SINTONIA_ASR_COMPUTE=int8_float32` declarado no job. Esta
missao foi correr a mesma coisa **na maquina, a mao**, sem esse declarado — e
encontrou o buraco entre as duas situacoes:

    resolver_dispositivo('GPU')  ->  cuda/float16
    WhisperModel(...)            ->  ValueError: Requested float16 compute type,
                                     but the target device or backend do not
                                     support efficient float16 computation
    o apanha-tudo da carga       ->  cai para o processador
    o carimbo                    ->  ASR_WHY_FALLBACK = GPU_UNAVAILABLE

numa maquina com `CUDA_DEVICE_COUNT = 1`.

    «NAO HA PLACA» E «ESTA PLACA NAO FAZ ESTA ARITMETICA» SAO DIAGNOSTICOS
    DIFERENTES. O PRIMEIRO MANDA COMPRAR HARDWARE QUE JA ESTA NA MAQUINA.

O que estas provas guardam: a negociacao pergunta a biblioteca, o pedido
explicito nao se troca por baixo de quem o fez, o carimbo diz a aritmetica que
CORREU, e a contraprova do processador deixou de reprovar por ter corrido no
processador que ela propria pediu.
"""
import ast
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
sys.path.insert(0, os.path.join(RAIZ, 'provas'))
import fala_local as fl                                        # noqa: E402

DONO_DO_ASR = 'ferramentas/fala_local.py'


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _corpo_de(rel, nome):
    """O CODIGO de uma funcao — sem comentario e sem docstring. → str.

    ⚠️ ESTAS PROVAS APANHARAM-SE A ELAS PROPRIAS, E TINHAM RAZAO EM FALHAR.
    A primeira versao procurava a palavra `pascal` no texto cru de
    `computes_suportados`, para garantir que nenhuma tabela de geracoes de
    placa vivia la dentro. Reprovou — porque a DOCSTRING diz, como exemplo do
    que nao fazer, «uma tabela de "Pascal nao faz float16" escrita aqui dentro
    seria uma segunda verdade».

        PROCURAR A PALAVRA NO FICHEIRO INTEIRO MEDE O QUE ESTA ESCRITO.
        A PERGUNTA ERA SOBRE O QUE EXECUTA.

    `ast.unparse` deita fora comentarios por construcao; a docstring sai a
    mao. O que fica e o codigo, e so sobre ele e que estas sentinelas falam.
    """
    for no in ast.walk(ast.parse(_fonte(rel))):
        if not isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if no.name != nome:
            continue
        corpo = list(no.body)
        if (corpo and isinstance(corpo[0], ast.Expr)
                and isinstance(corpo[0].value, ast.Constant)
                and isinstance(corpo[0].value.value, str)):
            corpo = corpo[1:]
        return '\n'.join(ast.unparse(x) for x in corpo)
    raise AssertionError('a funcao %r nao existe em %s' % (nome, rel))


def _py_do_repo():
    for pasta, dirs, fs in os.walk(RAIZ):
        dirs[:] = [d for d in dirs
                   if d not in ('__pycache__', '.git', 'node_modules', 'system-map')]
        for f in fs:
            if f.endswith('.py'):
                yield os.path.relpath(os.path.join(pasta, f), RAIZ).replace(os.sep, '/')


class _ComputeFixo:
    """Finge ser o `ctranslate2` a declarar uma lista fechada de tipos."""

    def __init__(self, suportados, levanta=False):
        self._s = suportados
        self._levanta = levanta

    def get_supported_compute_types(self, device):
        if self._levanta:
            raise RuntimeError('a biblioteca nao soube responder')
        return set(self._s)


def _com_computes(suportados, levanta=False):
    """Troca o que `computes_suportados` ve, sem tocar na maquina."""
    real = fl.computes_suportados

    def _falso(device):
        if levanta:
            return (), 'o ctranslate2 nao soube responder'
        return tuple(sorted(suportados)), ''
    return real, _falso


# ══════════════════════════════════════════════════════════════════════════
class T1ANegociacaoPerguntaABiblioteca(unittest.TestCase):
    """RT1 — a lista de tipos vem de quem os implementa, nao de uma tabela."""

    def test_o_dono_pergunta_ao_ctranslate2_e_nao_a_geracao_da_placa(self):
        bloco = _corpo_de(DONO_DO_ASR, 'computes_suportados')
        self.assertIn('get_supported_compute_types', bloco,
                      'a pergunta tem de ser a biblioteca')
        for palpite in ('pascal', 'turing', 'ampere', 'compute_capability',
                        'gtx', 'sm_61'):
            self.assertNotIn(palpite, bloco.lower(),
                             'uma tabela de hardware aqui dentro seria uma '
                             'segunda verdade sobre placas: %r' % palpite)

    def test_a_lista_vazia_e_nao_sei_e_nunca_nao_suporta(self):
        """RT2 — sem resposta da biblioteca NAO se degrada nada."""
        real, falso = _com_computes((), levanta=True)
        fl.computes_suportados = falso
        try:
            escolhido, trace = fl.negociar_compute('cuda')
        finally:
            fl.computes_suportados = real
        self.assertEqual(escolhido, fl.COMPUTE_GPU,
                         'sem saber o que ha, tenta-se o padrao e deixa-se a '
                         'carga falar — degradar as cegas seria inventar')
        self.assertEqual(trace['COMPUTE_SUPPORT'], fl.NAO_SEI)
        self.assertIsNone(trace['WHY_COMPUTE_FALLBACK'],
                          'nao houve queda: houve ausencia de resposta')


# ══════════════════════════════════════════════════════════════════════════
class T2OPedidoExplicitoNaoSeTroca(unittest.TestCase):
    """RT3 — um padrao negoceia-se; uma promessa cumpre-se ou reporta-se."""

    def test_o_padrao_da_casa_degrada_para_o_que_a_placa_declara(self):
        real, falso = _com_computes(('int8', 'int8_float32', 'float32'))
        fl.computes_suportados = falso
        try:
            escolhido, trace = fl.negociar_compute('cuda')
        finally:
            fl.computes_suportados = real
        self.assertEqual(trace['COMPUTE_REQUESTED'], fl.COMPUTE_GPU)
        self.assertEqual(escolhido, 'int8_float32')
        self.assertEqual(trace['COMPUTE_SELECTED'], 'int8_float32')
        self.assertEqual(trace['COMPUTE_SOURCE'], fl.COMPUTE_DA_CASA)
        self.assertEqual(trace['WHY_COMPUTE_FALLBACK'], fl.COMPUTE_NAO_SUPORTADO)

    def test_quem_declara_o_tipo_recebe_o_tipo_que_declarou(self):
        real, falso = _com_computes(('int8', 'float32'))
        fl.computes_suportados = falso
        try:
            escolhido, trace = fl.negociar_compute('cuda', pedido='float16')
        finally:
            fl.computes_suportados = real
        self.assertEqual(escolhido, 'float16',
                         'trocar por baixo de um pedido explicito produziria '
                         'texto de outra aritmetica com a etiqueta do pedinte')
        self.assertEqual(trace['COMPUTE_SOURCE'], fl.COMPUTE_EXPLICITO)
        self.assertIsNone(trace['WHY_COMPUTE_FALLBACK'])

    def test_o_tipo_que_a_placa_faz_passa_intacto(self):
        real, falso = _com_computes(('float16', 'int8', 'float32'))
        fl.computes_suportados = falso
        try:
            escolhido, trace = fl.negociar_compute('cuda')
        finally:
            fl.computes_suportados = real
        self.assertEqual(escolhido, fl.COMPUTE_GPU)
        self.assertIsNone(trace['WHY_COMPUTE_FALLBACK'],
                          'sem troca, o motivo e None — e nunca NOT_KNOWN')


# ══════════════════════════════════════════════════════════════════════════
class T3AQuedaTEMONOMECERTO(unittest.TestCase):
    """RT4 · RT5 — o defeito que esta missao veio consertar."""

    def test_aritmetica_recusada_nao_e_placa_ausente(self):
        erro = ValueError('Requested float16 compute type, but the target device '
                          'or backend do not support efficient float16 computation.')
        self.assertTrue(fl._parece_compute_incompativel(erro))
        self.assertFalse(fl._parece_sem_memoria(erro),
                         'isto nao e memoria cheia, e confundi-las manda '
                         'diminuir o modelo quando bastava trocar o tipo')

    def test_memoria_cheia_continua_a_ter_o_nome_dela(self):
        erro = RuntimeError('CUDA failed with error out of memory')
        self.assertTrue(fl._parece_sem_memoria(erro))
        self.assertFalse(fl._parece_compute_incompativel(erro))

    def test_um_erro_qualquer_nao_vira_nenhum_dos_dois(self):
        erro = RuntimeError('o disco acabou')
        self.assertFalse(fl._parece_sem_memoria(erro))
        self.assertFalse(fl._parece_compute_incompativel(erro))

    def test_os_tres_motivos_de_queda_sao_palavras_diferentes(self):
        motivos = {fl.GPU_INDISPONIVEL, fl.GPU_SEM_MEMORIA, fl.COMPUTE_NAO_SUPORTADO}
        self.assertEqual(len(motivos), 3,
                         'dois motivos com a mesma palavra sao um motivo so')


# ══════════════════════════════════════════════════════════════════════════
class T4AGuardaDeReentradaNaoECodigoMorto(unittest.TestCase):
    """RT6 — uma condicao que nunca e verdade finge que protege."""

    def test_o_literal_impossivel_saiu_do_apanha_tudo(self):
        bloco = _corpo_de(DONO_DO_ASR, 'modelo')
        self.assertNotIn("DEVICE_REQUESTED'] == GPU_SEM_MEMORIA", bloco,
                         'DEVICE_REQUESTED so pode ser AUTO, CPU ou GPU — a '
                         'comparacao com GPU_OOM era sempre falsa')

    def test_o_pedido_e_sempre_um_dos_tres_e_nunca_um_motivo_de_queda(self):
        for pedido in fl.DISPOSITIVOS:
            _d, _c, trace = fl.resolver_dispositivo(pedido)
            self.assertIn(trace['DEVICE_REQUESTED'], fl.DISPOSITIVOS)
            self.assertNotIn(trace['DEVICE_REQUESTED'],
                             (fl.GPU_SEM_MEMORIA, fl.GPU_INDISPONIVEL,
                              fl.COMPUTE_NAO_SUPORTADO))


# ══════════════════════════════════════════════════════════════════════════
class T5OCarimboDizAAritmeticaQueCORREU(unittest.TestCase):
    """RT7 — o literal a voltar por uma porta nova."""

    def test_o_ferro_do_carimbo_usa_o_compute_do_trace(self):
        trace = {'DEVICE_SELECTED': fl.GPU, 'ACCELERATOR': 'CUDA',
                 'COMPUTE_REQUESTED': 'float16', 'COMPUTE_SELECTED': 'int8_float32',
                 'COMPUTE_SOURCE': fl.COMPUTE_DA_CASA,
                 'WHY_COMPUTE_FALLBACK': fl.COMPUTE_NAO_SUPORTADO}
        c = fl.carimbo('small', trace, fl.OK)
        self.assertEqual(c['ASR_DEVICE'], 'cuda/int8_float32')
        self.assertNotIn('float16', c['ASR_DEVICE'],
                         'o carimbo estaria a jurar uma aritmetica que nao '
                         'produziu este texto')

    def test_os_tres_campos_da_aritmetica_existem_sempre(self):
        for pedido in fl.DISPOSITIVOS:
            _d, _c, trace = fl.resolver_dispositivo(pedido)
            c = fl.carimbo('small', trace, fl.OK)
            for campo in ('ASR_COMPUTE_REQUESTED', 'ASR_COMPUTE_SELECTED',
                          'ASR_COMPUTE_SOURCE'):
                self.assertIn(campo, c)
                self.assertNotEqual(c[campo], None)

    def test_sem_troca_o_motivo_e_None_e_nunca_NOT_KNOWN(self):
        _d, _c, trace = fl.resolver_dispositivo(fl.CPU)
        c = fl.carimbo('small', trace, fl.OK)
        self.assertIsNone(c['ASR_WHY_COMPUTE_FALLBACK'],
                          '`None` quer dizer «nao houve troca». `NOT_KNOWN` '
                          'diria «pode ter havido e nao sei» — sao coisas '
                          'diferentes, e colapsa-las esconde a troca')

    def test_sem_trace_o_carimbo_confessa_a_aritmetica_tambem(self):
        c = fl.carimbo('small')
        self.assertEqual(c['ASR_COMPUTE_SELECTED'], fl.NAO_SEI)
        self.assertEqual(c['ASR_DEVICE'], fl.NAO_SEI)


# ══════════════════════════════════════════════════════════════════════════
class T6OPedidoNaPLACANaoSEAPAGAAOCAIR(unittest.TestCase):
    """RT8 — a queda tem de continuar legivel depois de acontecer."""

    def test_o_apanha_tudo_preserva_o_compute_pedido(self):
        corpo = _fonte(DONO_DO_ASR)
        i = corpo.index('def modelo(')
        bloco = corpo[i:corpo.index('\ndef ', i + 10)]
        self.assertIn("tc.pop('COMPUTE_REQUESTED', None)", bloco,
                      'sem isto o artefato diria «pedi int8 e corri int8» '
                      'depois de ter pedido float16 a uma placa')


# ══════════════════════════════════════════════════════════════════════════
class T7OModeloNAOSETROCASOZINHO(unittest.TestCase):
    """RT9 — `MODEL_REQUESTED` e `MODEL_USED` so divergem se houver queda."""

    def test_nao_existe_degradacao_silenciosa_de_modelo(self):
        corpo = _fonte(DONO_DO_ASR)
        i = corpo.index('def modelo(')
        bloco = corpo[i:corpo.index('\ndef ', i + 10)]
        # O apanha-tudo da carga troca o DISPOSITIVO. Se algum dia trocar
        # tambem o MODELO, tem de o registar — e esta prova reprova ate isso
        # existir, para a troca nao entrar em silencio.
        self.assertNotIn('nome = ', bloco.split('except Exception')[1],
                         'o modelo mudou dentro do apanha-tudo, e o carimbo so '
                         'tem um campo `ASR_MODEL` para o dizer')

    def test_o_carimbo_nomeia_o_modelo_que_foi_pedido(self):
        _d, _c, trace = fl.resolver_dispositivo(fl.CPU)
        c = fl.carimbo('base', trace, fl.OK)
        self.assertEqual(c['ASR_MODEL'], 'base')


# ══════════════════════════════════════════════════════════════════════════
class T8ADECISAONAOFOITOMADAAQUI(unittest.TestCase):
    """RT10 — a capacidade entra; o padrao continua a ser decisao do dono da casa."""

    def test_o_dispositivo_padrao_continua_o_processador(self):
        self.assertEqual(fl.DISPOSITIVO_PADRAO, fl.CPU,
                         'medido a 2026-09-14: o texto da placa difere do texto '
                         'do processador em 4 de 6 pecas com texto. Qual esta '
                         'certo e NOT_MEASURED — e trocar o padrao sem essa '
                         'medicao seria mudar o texto de toda a coleta futura')

    def test_as_constantes_da_aritmetica_nao_mudaram(self):
        self.assertEqual(fl.COMPUTE_GPU, 'float16')
        self.assertEqual(fl.COMPUTE_CPU, 'int8')

    def test_a_ordem_de_degradacao_e_declarada_e_nao_adivinhada(self):
        self.assertIn('cuda', fl.COMPUTE_DEGRADACAO)
        self.assertIn('cpu', fl.COMPUTE_DEGRADACAO)
        self.assertEqual(fl.COMPUTE_DEGRADACAO['cuda'][0], fl.COMPUTE_GPU,
                         'o primeiro degrau tem de ser o padrao da casa')
        self.assertEqual(fl.COMPUTE_DEGRADACAO['cpu'][0], fl.COMPUTE_CPU)


# ══════════════════════════════════════════════════════════════════════════
class T9ACONTRAPROVADOPROCESSADORDEIXOUDEREPROVAR(unittest.TestCase):
    """RT11 — uma prova que reprova o que ela propria pediu nao mede nada."""

    def test_o_veredito_do_smoke_deriva_do_pedido(self):
        corpo = _fonte('provas/gpu_asr_smoke.py')
        i = corpo.index('def medir(')
        bloco = corpo[i:corpo.index('\ndef ', i + 10)]
        self.assertIn('DEVICE_EXPECTED', bloco)
        self.assertNotIn("r.get('ASR_DEVICE_USED') == fl.GPU", bloco,
                         'o esperado nao pode estar cravado em GPU: a '
                         'contraprova do processador sairia FAIL sem nada '
                         'ter falhado')

    def test_auto_exige_coerencia_e_nao_nomeia_ferro_de_antemao(self):
        corpo = _fonte('provas/gpu_asr_smoke.py')
        self.assertIn("ASR_DEVICE_SELECTED", corpo,
                      'em AUTO o esperado e o que o resolvedor escolheu')


# ══════════════════════════════════════════════════════════════════════════
class T10DOISVAZIOSNAOSAOUMACORDO(unittest.TestCase):
    """RT12 — a manchete contava duas ausencias como concordancia."""

    def test_o_banco_separa_comparavel_de_vazio(self):
        corpo = _fonte('provas/asr_banco.py')
        i = corpo.index('def ferro_a_ferro')
        bloco = corpo[i:corpo.index('\ndef ', i + 10)]
        self.assertIn("'COMPARABLE'", bloco)
        self.assertIn("'BOTH_EMPTY'", bloco)

    def test_a_semelhanca_nao_se_calcula_sobre_o_nada(self):
        corpo = _fonte('provas/asr_banco.py')
        i = corpo.index('def ferro_a_ferro')
        bloco = corpo[i:corpo.index('\ndef ', i + 10)]
        self.assertIn('if (t_cpu and t_gpu) else NAO_SE_APLICA', bloco,
                      'semelhanca 1.0 entre dois vazios e aritmetica verdadeira '
                      'a responder a pergunta errada')

    def test_o_total_conta_so_os_pares_comparaveis(self):
        corpo = _fonte('provas/asr_banco.py')
        self.assertIn("len(comparaveis)", corpo)


# ══════════════════════════════════════════════════════════════════════════
class T11SEMVERDADENAOSELEACERTO(unittest.TestCase):
    """RT13 — a porta que aceita audio sem verdade nao pode publicar qualidade."""

    def test_a_amostra_sem_verdade_declarada_sai_NOT_MEASURED(self):
        import asr_banco as ab                                 # noqa: PLC0415
        corpo = _fonte('provas/asr_banco.py')
        i = corpo.index('def amostras(')
        bloco = corpo[i:corpo.index('\ndef ', i + 10)]
        self.assertIn("'QUALITY': NAO_MEDIDO", bloco)
        self.assertIn("'TERMOS': []", bloco,
                      'inventar termos esperados seria produzir a verdade que '
                      'se queria medir')
        self.assertTrue(hasattr(ab, 'ferro_a_ferro'))

    def test_sem_lingua_declarada_nao_ha_deriva_para_medir(self):
        corpo = _fonte('provas/asr_banco.py')
        self.assertIn("'NOT_DECLARED'", corpo,
                      'comparar o detectado com None dava DRIFT em toda a '
                      'linha — deriva publicada sem ponto de partida')

    def test_o_banco_nao_baixa_midia_em_caminho_nenhum(self):
        corpo = _fonte('provas/asr_banco.py')
        for rota in ('yt_dlp', 'requests.get', 'urllib.request.urlopen',
                     'apify', 'snapshot_download'):
            self.assertNotIn(rota, corpo,
                             'medir o ferro nao autoriza adquirir conteudo: %r' % rota)


# ══════════════════════════════════════════════════════════════════════════
class T12NADADESTAMAQUINAENTRANOGIT(unittest.TestCase):
    """RT14 · RT15 — caminho pessoal, segredo e nome de maquina ficam fora."""

    ALVOS = (DONO_DO_ASR, 'provas/asr_banco.py', 'provas/gpu_asr_smoke.py',
             'provas/hardware_local.py', 'tests/test_c4d_ferro_negociado.py')

    def test_nenhum_perfil_pessoal_esta_escrito_nestes_ficheiros(self):
        perfil = os.path.basename(os.environ.get('USERPROFILE')
                                  or os.path.expanduser('~'))
        for rel in self.ALVOS:
            t = _fonte(rel)
            self.assertNotIn('C:\\Users\\%s' % perfil, t)
            self.assertNotIn('/Users/%s' % perfil, t)
            if len(perfil) > 3:
                self.assertNotIn(perfil.lower(), t.lower(),
                                 '%s traz o nome do dono do perfil' % rel)

    def test_nenhum_caminho_absoluto_de_midia_desta_maquina(self):
        # O alvo monta-se em pedacos DE PROPOSITO: escrito inteiro, esta prova
        # apanhava-se a si propria e reprovava por existir.
        agulha = 'INSTAGRAM-' + 'TRANSCRICOES/audio-' + 'cache'
        for rel in self.ALVOS:
            if rel.startswith('tests/'):
                continue
            t = _fonte(rel)
            self.assertNotIn(agulha, t,
                             '%s cravou a pasta de uma maquina: a pasta e '
                             'argumento, nunca constante' % rel)

    def test_a_configuracao_de_cuda_continua_conferida_e_nao_cravada(self):
        corpo = _fonte(DONO_DO_ASR)
        i = corpo.index('def _pastas_de_dll')
        bloco = corpo[i:corpo.index('\ndef ', i + 10)]
        self.assertIn('os.path.isdir', bloco,
                      'cada pasta de DLL e conferida no disco antes de entrar')
        self.assertIn('SINTONIA_CUDA_BIN', corpo,
                      'quem tiver o toolkit noutro sitio declara-o por ambiente')

    def test_o_dono_nao_escreve_nada_no_acervo(self):
        corpo = _fonte(DONO_DO_ASR)
        self.assertNotIn("data/samples", corpo)
        self.assertNotIn("data\\samples", corpo)

    def test_a_execucao_local_nao_criou_uma_segunda_collection(self):
        """RT15 — nenhum orquestrador, fila ou RAW nasceu nesta missao."""
        novos = [r for r in _py_do_repo()
                 if os.path.basename(r).startswith(('runner_local', 'gpu_',
                                                    'fila_local', 'collection_local'))
                 and r != 'provas/gpu_asr_smoke.py']
        self.assertEqual(novos, [], 'nasceu uma segunda Collection: %s' % novos)


# ══════════════════════════════════════════════════════════════════════════
class T13OQUEESTAGAVETANUNCADECIDE(unittest.TestCase):
    """RT16 — legenda, transcricao e traducao continuam coisas diferentes."""

    def test_o_reconhecedor_nunca_pede_traducao_ao_motor(self):
        """`task='translate'` faria o whisper devolver ingles no lugar do original.

        A prova olha para as CHAMADAS, e nao para o texto: o ficheiro diz por
        extenso «NUNCA CLASSIFICA, NAO RESUME, NAO TRADUZ» — procurar a palavra
        reprovaria a frase que promete o contrario do defeito.
        """
        for no in ast.walk(ast.parse(_fonte(DONO_DO_ASR))):
            if not isinstance(no, ast.Call):
                continue
            for kw in no.keywords or []:
                self.assertNotEqual(
                    kw.arg, 'task',
                    'a traducao nunca substitui o original: linha %d' % no.lineno)
        self.assertNotIn("'translate'", _fonte(DONO_DO_ASR))

    def test_o_texto_nasce_com_o_tipo_por_classificar(self):
        _d, _c, trace = fl.resolver_dispositivo(fl.CPU)
        c = fl.carimbo('small', trace, fl.OK)
        self.assertEqual(c['TRANSCRIBER_ID'], DONO_DO_ASR)

    def test_a_ausencia_de_texto_continua_a_nao_ser_ausencia_de_fala(self):
        self.assertIn(fl.REQUESTED_EMPTY, fl.ESTADOS)
        self.assertNotEqual(fl.REQUESTED_EMPTY, fl.OK)


if __name__ == '__main__':
    unittest.main(verbosity=2)
