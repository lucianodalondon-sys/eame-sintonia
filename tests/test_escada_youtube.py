#!/usr/bin/env python3
"""
Provas da ESCADA do texto do YouTube — título → legenda → whisper.

POR QUE ESTAS PROVAS EXISTEM, E POR QUE SEM REDE
==================================================
A escada decide gastar hora de máquina. As duas decisões que ela toma são caras de
maneiras opostas:

    rodar o whisper num vídeo LEGENDADO  → paga-se hora de máquina por nada
    NÃO rodar num vídeo sem legenda      → perde-se o texto que justificava a missão

Nenhuma das duas denuncia a si mesma em produção: a primeira só aparece na conta de
tempo no fim do lote, e a segunda aparece como "este vídeo não tinha nada a dizer".
Por isso a decisão vive numa função PURA — `estado_da_legenda()` — e por isso ela é
provada aqui, sem rede, sem navegador e sem modelo.

    DECISÃO QUE SÓ PODE SER PROVADA COM REDE NÃO É PROVADA NUNCA.

E há um ramo que esta casa ainda não conseguiu observar ao vivo: em 2026-09-04, deste
contêiner, a página do vídeo respondeu HTTP 429 e o `timedtext` também — nenhuma
legenda real pôde ser lida. O ramo "legenda presente ⇒ o whisper NÃO roda" é provado
aqui com um LEGENDAS.json de mentira, num diretório temporário, contra a escada de
verdade. Fixture é mentira declarada; não medir é mentira por omissão.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import asr_local  # noqa: E402
import youtube_janela as yj  # noqa: E402
import youtube_transcrever as yt  # noqa: E402
import youtube_microteste as mt  # noqa: E402


def _item(estado, **extra):
    d = {'VIDEO_ID': 'vid', 'CAPTION_STATE': estado}
    d.update(extra)
    return d


class TestEstadoDaLegenda(unittest.TestCase):
    """A tradução dos seis estados do dono da legenda para os desta escada."""

    def test_A_presente_com_texto_e_utilizavel(self):
        e, _p, _r = yt.estado_da_legenda(
            _item('PRESENTE', TRANSCRICAO=[{'T_MS': 0, 'DUR_MS': 900, 'TEXTO': 'olá'}]))
        self.assertEqual(yt.CAPTION_OK, e)

    def test_B_ausente_e_o_unico_caso_que_afirma(self):
        """`AUSENTE` é a única porta para NO_CAPTION_CONFIRMED. Nenhuma falha vira essa."""
        e, _p, retentar = yt.estado_da_legenda(_item('AUSENTE', CAPTION_TRACKS=[]))
        self.assertEqual(yt.NO_CAPTION_CONFIRMED, e)
        self.assertFalse(retentar)

    def test_C_porta_fechada_nunca_vira_ausencia_de_legenda(self):
        """429 e CAPTCHA são sobre a REDE. Escrevê-los como 'sem legenda' é a falha-mor."""
        for estado in ('PORTA_NAO_ABRIU', 'PLAYER_RESPONSE_AUSENTE'):
            with self.subTest(estado=estado):
                e, _p, retentar = yt.estado_da_legenda(_item(estado, POR_QUE='429'))
                self.assertEqual(yt.CAPTION_ENVIRONMENT_FAILURE, e)
                self.assertNotEqual(yt.NO_CAPTION_CONFIRMED, e)
                self.assertTrue(retentar)

    def test_D_erro_de_rede_no_timedtext_e_FETCH_e_nao_PARSE(self):
        for tipo in ('HTTPError', 'URLError', 'TimeoutError', 'ConnectionResetError'):
            with self.subTest(tipo=tipo):
                e, _p, retentar = yt.estado_da_legenda(_item(
                    'DECLARADA_MAS_VAZIA', TIMEDTEXT_ERRO_TIPO=tipo,
                    TIMEDTEXT_ERRO='%s: 429' % tipo))
                self.assertEqual(yt.CAPTION_FETCH_FAILURE, e)
                self.assertTrue(retentar)

    def test_E_erro_de_leitura_e_PARSE_e_nao_se_conserta_tentando_de_novo(self):
        e, _p, retentar = yt.estado_da_legenda(_item(
            'DECLARADA_MAS_VAZIA', TIMEDTEXT_ERRO_TIPO='JSONDecodeError',
            TIMEDTEXT_ERRO='JSONDecodeError: linha 1'))
        self.assertEqual(yt.CAPTION_PARSE_FAILURE, e)
        self.assertFalse(retentar)

    def test_F_corpo_vazio_e_corpo_sem_trechos_sao_estados_DIFERENTES(self):
        """0 byte é falha de entrega; JSON sem texto é legenda vazia. Não são o mesmo fato."""
        vazio, _p, retentar_vazio = yt.estado_da_legenda(
            _item('DECLARADA_MAS_VAZIA', TIMEDTEXT_VAZIO_POR_QUE='CORPO_VAZIO'))
        sem, _p2, retentar_sem = yt.estado_da_legenda(
            _item('DECLARADA_MAS_VAZIA', TIMEDTEXT_VAZIO_POR_QUE='SEM_TRECHOS'))
        self.assertEqual(yt.CAPTION_FETCH_FAILURE, vazio)
        self.assertEqual(yt.CAPTION_DELIVERED_EMPTY, sem)
        self.assertNotEqual(vazio, sem)
        self.assertTrue(retentar_vazio)
        self.assertFalse(retentar_sem)

    def test_G_sem_pergunta_nao_e_sem_resposta(self):
        for item in (None, _item('NOT_TESTED')):
            with self.subTest(item=item):
                e, _p, _r = yt.estado_da_legenda(item)
                self.assertEqual(yt.CAPTION_NOT_TESTED, e)

    def test_H_estado_novo_do_dono_nao_vira_silencio(self):
        """Se o dono da legenda inventar um estado, ele chega aqui como falha declarada."""
        e, por_que, _r = yt.estado_da_legenda(_item('ALGO_QUE_AINDA_NAO_EXISTE'))
        self.assertEqual(yt.CAPTION_PARSE_FAILURE, e)
        self.assertIn('ALGO_QUE_AINDA_NAO_EXISTE', por_que)

    def test_I_nenhuma_falha_tecnica_vira_NO_CAPTION_CONFIRMED(self):
        """A prova que resume o arquivo inteiro."""
        falhas = ('PORTA_NAO_ABRIU', 'PLAYER_RESPONSE_AUSENTE', 'DECLARADA_MAS_VAZIA',
                  'NOT_TESTED', 'ESTADO_DESCONHECIDO')
        for estado in falhas:
            with self.subTest(estado=estado):
                e, _p, _r = yt.estado_da_legenda(_item(estado))
                self.assertNotEqual(yt.NO_CAPTION_CONFIRMED, e)


class TestTraducaoDeTempo(unittest.TestCase):
    """A legenda chega em milissegundos e com DURAÇÃO; a escada guarda segundos e FIM."""

    def test_ms_vira_segundos_e_duracao_vira_fim(self):
        texto, segs = yt.texto_da_legenda(_item('PRESENTE', TRANSCRICAO=[
            {'T_MS': 1500, 'DUR_MS': 2000, 'TEXTO': 'primeiro'},
            {'T_MS': 3500, 'DUR_MS': 1000, 'TEXTO': 'segundo'}]))
        self.assertEqual('primeiro segundo', texto)
        self.assertEqual(1.5, segs[0]['START_S'])
        self.assertEqual(3.5, segs[0]['END_S'])      # 1500 + 2000 ms, não 2000
        self.assertEqual(4.5, segs[1]['END_S'])

    def test_tempo_ausente_vira_NOT_KNOWN_e_nao_zero(self):
        """Zero é um instante do vídeo. Ausência não é o instante zero."""
        _t, segs = yt.texto_da_legenda(_item('PRESENTE', TRANSCRICAO=[
            {'T_MS': None, 'DUR_MS': None, 'TEXTO': 'sem tempo'}]))
        self.assertEqual('NOT_KNOWN', segs[0]['START_S'])
        self.assertEqual('NOT_KNOWN', segs[0]['END_S'])


class TestChaveDoCache(unittest.TestCase):
    """A chave mínima: o que muda o TEXTO entra; o que muda só o TEMPO não entra."""

    def test_modelo_diferente_e_chave_diferente(self):
        a = asr_local.chave('vid', asr_local.config(modelo='small'), 'es')
        b = asr_local.chave('vid', asr_local.config(modelo='base'), 'es')
        self.assertNotEqual(a, b)

    def test_idioma_diferente_e_chave_diferente(self):
        cfg = asr_local.config(modelo='small')
        self.assertNotEqual(asr_local.chave('vid', cfg, 'es'),
                            asr_local.chave('vid', cfg, 'it'))

    def test_nucleos_e_beam_NAO_mudam_a_chave(self):
        """Trocar de máquina não pode significar transcrever tudo de novo."""
        a = asr_local.chave('vid', asr_local.config(modelo='small', beam=1, nucleos=4), 'es')
        b = asr_local.chave('vid', asr_local.config(modelo='small', beam=5, nucleos=64), 'es')
        self.assertEqual(a, b)

    def test_idioma_ausente_nao_colide_com_idioma_declarado(self):
        cfg = asr_local.config(modelo='small')
        self.assertNotEqual(asr_local.chave('vid', cfg, None),
                            asr_local.chave('vid', cfg, 'es'))


class TestLeiDoIdioma(unittest.TestCase):
    """O idioma vem do PAÍS, e escopo não é país."""

    def test_pais_conhecido_declara_o_idioma(self):
        self.assertEqual('es', asr_local.idioma_do_pais('ES'))
        self.assertEqual('it', asr_local.idioma_do_pais('IT'))
        self.assertEqual('fr', asr_local.idioma_do_pais('FR'))

    def test_escopo_nao_e_pais(self):
        """`LOCAL_COUNTRY_PROVED` é um ESCOPO. Passá-lo aqui devolvia None em silêncio."""
        self.assertIsNone(asr_local.idioma_do_pais('LOCAL_COUNTRY_PROVED'))
        self.assertIsNone(asr_local.idioma_do_pais(None))

    def test_o_lote_congelado_da_pais_a_todo_handle_da_coleta(self):
        """Se isto falhar, a lei do idioma voltou a ser autodetecção — em silêncio."""
        lote = yt.paises_do_lote()
        self.assertTrue(lote, 'o lote congelado não foi lido')
        for handle, d in lote.items():
            with self.subTest(handle=handle):
                self.assertIsNotNone(asr_local.idioma_do_pais(d['COUNTRY']),
                                     'sem idioma para %s (COUNTRY=%s)'
                                     % (handle, d['COUNTRY']))


class TestEscadaComLegendaPresente(unittest.TestCase):
    """O ramo que este contêiner não alcança ao vivo: legenda presente ⇒ whisper NÃO roda.

    A escada de verdade roda contra artefatos de mentira, num diretório temporário. O
    motor NÃO é carregado: se ele fosse chamado, o teste levaria dezenas de segundos e
    baixaria áudio — e é exatamente isso que a prova existe para impedir.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='escada-')
        self.janela = os.path.join(self.tmp, 'YOUTUBE-JANELA')
        self.saida = os.path.join(self.tmp, 'YOUTUBE-TRANSCRICOES')
        os.makedirs(self.janela)
        os.makedirs(self.saida)
        self._guardado = (yt.JANELA, yt.SAIDA, yt.MEDIA)
        yt.JANELA, yt.SAIDA = self.janela, self.saida
        yt.MEDIA = os.path.join(self.saida, 'audio-cache')
        # `_gravar` grava em SAIDA; o módulo o resolve na chamada, então basta trocar.

        handle = sorted(yt.paises_do_lote())[0]
        with open(os.path.join(self.janela, 'OBJETOS.json'), 'w', encoding='utf-8') as f:
            json.dump({'ITEMS': [
                {'VIDEO_ID': 'COM_LEGENDA', 'ACCOUNT_HANDLE': handle, 'TITLE': 'com',
                 'DURATION_S': 60, 'VIDEO_URL': 'https://www.youtube.com/watch?v=COM_LEGENDA',
                 'COUNTRY_SCOPE': 'LOCAL_COUNTRY_PROVED'},
                {'VIDEO_ID': 'SEM_PERGUNTA', 'ACCOUNT_HANDLE': handle, 'TITLE': 'sem',
                 'DURATION_S': 60, 'VIDEO_URL': 'https://www.youtube.com/watch?v=SEM_PERGUNTA',
                 'COUNTRY_SCOPE': 'LOCAL_COUNTRY_PROVED'}]}, f)
        with open(os.path.join(self.janela, 'LEGENDAS.json'), 'w', encoding='utf-8') as f:
            json.dump({'ITEMS': [{
                'VIDEO_ID': 'COM_LEGENDA', 'CAPTION_STATE': 'PRESENTE',
                'CAPTION_LANG': 'es', 'CAPTION_KIND': 'asr',
                'TRANSCRICAO': [{'T_MS': 0, 'DUR_MS': 1000, 'TEXTO': 'el ensayo de campo'},
                                {'T_MS': 1000, 'DUR_MS': 1000, 'TEXTO': 'con dosis alta'}]}]}, f)

    def tearDown(self):
        yt.JANELA, yt.SAIDA, yt.MEDIA = self._guardado
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _carregar_seria_erro(self, *a, **k):
        raise AssertionError('a escada carregou o motor com legenda presente — '
                             'é pagar hora de máquina por som que já veio escrito')

    def test_legenda_presente_nao_carrega_o_motor_e_usa_a_legenda(self):
        original = asr_local.carregar
        asr_local.carregar = self._carregar_seria_erro
        try:
            self.assertEqual(0, yt.escada(ids=['COM_LEGENDA']))
        finally:
            asr_local.carregar = original
        with open(os.path.join(self.saida, 'TEXTO.json'), encoding='utf-8') as f:
            d = json.load(f)
        i = d['ITEMS'][0]
        self.assertEqual(yt.YOUTUBE_CAPTION, i['TEXT_SOURCE'])
        self.assertEqual(yt.WHISPER_NOT_NEEDED, i['WHISPER_STATE'])
        self.assertEqual('el ensayo de campo con dosis alta', i['TRANSCRIPT'])
        self.assertEqual(0, i['MACHINE_SECONDS'])
        self.assertEqual(1, d['CAPTION_HITS'])
        self.assertEqual(0, d['WHISPER_FALLBACKS'])

    def test_legenda_nao_perguntada_nao_chama_o_whisper(self):
        """Pular a legenda para gastar hora de máquina seria inverter a ordem — e a ordem é lei."""
        original = asr_local.carregar
        asr_local.carregar = self._carregar_seria_erro
        try:
            self.assertEqual(0, yt.escada(ids=['SEM_PERGUNTA']))
        finally:
            asr_local.carregar = original
        with open(os.path.join(self.saida, 'TEXTO.json'), encoding='utf-8') as f:
            d = json.load(f)
        i = d['ITEMS'][0]
        self.assertEqual(yt.CAPTION_NOT_TESTED, i['CAPTION_STATE'])
        self.assertEqual(yt.WHISPER_NOT_TRIED, i['WHISPER_STATE'])
        self.assertEqual(yt.TITLE_ONLY, i['TEXT_SOURCE'])

    def test_o_documento_carrega_identidade_do_lote_e_nao_da_fala(self):
        yt.escada(ids=['COM_LEGENDA'])
        with open(os.path.join(self.saida, 'TEXTO.json'), encoding='utf-8') as f:
            d = json.load(f)
        for k in ('IDENTITY_ERRORS', 'NEW_ENTITIES_FROM_CONTENT', 'ROLE_FROM_CONTENT',
                  'DOCUMENT_WITHOUT_SOURCE_ID'):
            with self.subTest(k=k):
                self.assertEqual(0, d[k])
        self.assertTrue(d['ITEMS'][0]['SOURCE_ID'])
        self.assertTrue(d['ITEMS'][0]['SOURCE_URL'])


class TestCacheDeTranscricao(unittest.TestCase):
    """A segunda execução não pode baixar áudio nem carregar o motor de novo.

    O ramo do cache também não pôde ser observado ao vivo neste contêiner: sem áudio,
    nada chegou a ser transcrito, e um cache que nunca guardou nada nunca acerta. Aqui
    a entrada é posta à mão e a escada de verdade é obrigada a usá-la.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='cache-')
        self.janela = os.path.join(self.tmp, 'YOUTUBE-JANELA')
        self.saida = os.path.join(self.tmp, 'YOUTUBE-TRANSCRICOES')
        os.makedirs(self.janela)
        os.makedirs(self.saida)
        self._guardado = (yt.JANELA, yt.SAIDA, yt.MEDIA)
        yt.JANELA, yt.SAIDA = self.janela, self.saida
        yt.MEDIA = os.path.join(self.saida, 'audio-cache')

        self.handle = sorted(yt.paises_do_lote())[0]
        self.pais = yt.paises_do_lote()[self.handle]['COUNTRY']
        self.idioma = asr_local.idioma_do_pais(self.pais)
        with open(os.path.join(self.janela, 'OBJETOS.json'), 'w', encoding='utf-8') as f:
            json.dump({'ITEMS': [
                {'VIDEO_ID': 'SEM_LEGENDA', 'ACCOUNT_HANDLE': self.handle,
                 'TITLE': 'sin subtitulos', 'DURATION_S': 60,
                 'VIDEO_URL': 'https://www.youtube.com/watch?v=SEM_LEGENDA'}]}, f)
        with open(os.path.join(self.janela, 'LEGENDAS.json'), 'w', encoding='utf-8') as f:
            json.dump({'ITEMS': [{'VIDEO_ID': 'SEM_LEGENDA', 'CAPTION_STATE': 'AUSENTE',
                                  'CAPTION_TRACKS': []}]}, f)

    def tearDown(self):
        yt.JANELA, yt.SAIDA, yt.MEDIA = self._guardado
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _semear_cache(self, modelo='small'):
        chave = asr_local.chave('SEM_LEGENDA', asr_local.config(modelo=modelo), self.idioma)
        with open(os.path.join(self.saida, 'ASR-CACHE.json'), 'w', encoding='utf-8') as f:
            json.dump({'ITEMS': [{
                'ASR_CACHE_KEY': chave, 'VIDEO_ID': 'SEM_LEGENDA',
                'TRANSCRIPT': 'hemos observado los primeros sintomas en campo',
                'TRANSCRIPT_SEGMENTS': [{'START_S': 0.0, 'END_S': 3.0,
                                         'TEXT': 'hemos observado los primeros sintomas en campo'}],
                'TRANSCRIPT_CHARS': 46, 'ASR_ENGINE': 'faster-whisper',
                'ASR_MODEL': modelo, 'ASR_LANGUAGE': self.idioma,
                'MACHINE_SECONDS': 12.5, 'AUDIO_SECONDS': 60.0}]}, f)
        return chave

    def _explodir(self, *a, **k):
        raise AssertionError('a escada foi buscar áudio / carregar o motor com o cache '
                             'quente — é pagar duas vezes pelo mesmo item')

    def test_cache_quente_nao_baixa_audio_nem_carrega_motor(self):
        self._semear_cache()
        audio_original, carregar_original = yt.audio, asr_local.carregar
        yt.audio, asr_local.carregar = self._explodir, self._explodir
        try:
            self.assertEqual(0, yt.escada(ids=['SEM_LEGENDA']))
        finally:
            yt.audio, asr_local.carregar = audio_original, carregar_original
        with open(os.path.join(self.saida, 'TEXTO.json'), encoding='utf-8') as f:
            d = json.load(f)
        i = d['ITEMS'][0]
        self.assertEqual('YES', i['CACHE_HIT'])
        self.assertEqual(yt.WHISPER_OK, i['WHISPER_STATE'])
        self.assertEqual(yt.WHISPER_LOCAL, i['TEXT_SOURCE'])
        self.assertEqual(1, d['CACHE_HITS'])
        self.assertEqual(0, i['MACHINE_SECONDS'])
        self.assertEqual(12.5, i['MACHINE_SECONDS_ORIGINAL'])

    def test_trocar_de_modelo_nao_devolve_o_texto_do_modelo_antigo(self):
        """O defeito exato da versão anterior: a chave era só o VIDEO_ID."""
        antigo = self._semear_cache(modelo='small')
        chamou = []

        def falso_audio(video_id):
            chamou.append(video_id)
            return None, 'NENHUMA', 'sonda: a escada foi buscar áudio, que é o certo aqui'

        audio_original = yt.audio
        yt.audio = falso_audio
        try:
            yt.escada(ids=['SEM_LEGENDA'], modelo='base')
        finally:
            yt.audio = audio_original
        self.assertEqual(['SEM_LEGENDA'], chamou,
                         'trocar de modelo devolveu o texto do modelo antigo')
        with open(os.path.join(self.saida, 'ASR-CACHE.json'), encoding='utf-8') as f:
            cache = json.load(f)
        chaves = [i['ASR_CACHE_KEY'] for i in cache['ITEMS']]
        self.assertIn(antigo, chaves,
                      'o resultado do modelo anterior foi apagado em silêncio')


class TestMedicaoAntesDepois(unittest.TestCase):
    """A medição do §7 — TITLE_ONLY contra CAPTION_OR_WHISPER — sobre texto conhecido.

    Neste contêiner o YouTube respondeu 429 na página do vídeo e no `timedtext`, e o
    áudio não foi entregue: o ganho REAL de texto ficou em zero, e por isso a medição
    ao vivo mostrou NÃO SEI 10 → 10. Isso mede o AMBIENTE, não a máquina de medir.
    Esta prova mede a máquina: com texto de verdade na mão, ela move os números?
    """

    def setUp(self):
        import youtube_microteste as ym
        self.ym = ym
        self.tmp = tempfile.mkdtemp(prefix='medir-')
        self._guardado = ym.SAIDA
        ym.SAIDA = self.tmp
        # Fala espanhola com marcadores do léxico DECLARADO em `sensor_medir.py`, longa o
        # bastante para passar do piso de 200 caracteres da própria régua.
        fala = ('en la parcela de ensayo hemos observado los primeros sintomas de repilo '
                'sobre las hojas mas bajas del olivar, y detectamos que la presion sube '
                'despues de las lluvias de octubre. esto significa que el umbral de '
                'tratamiento se alcanza antes de lo previsto, y por lo tanto recomendamos '
                'adelantar la aplicacion en las parcelas de suelo humedo.')
        with open(os.path.join(self.tmp, 'TEXTO.json'), 'w', encoding='utf-8') as f:
            json.dump({'TOTAL_AUDIO_MINUTES': 1.0, 'TOTAL_MACHINE_SECONDS': 11.0,
                       'ITEMS': [
                           {'VIDEO_ID': 'COM_TEXTO', 'SOURCE_ID': 'x/COM_TEXTO',
                            'SOURCE_URL': 'https://www.youtube.com/watch?v=COM_TEXTO',
                            'TITLE': 'Olivar 2026', 'TRANSCRIPT': fala,
                            'CAPTION_STATE': 'NO_CAPTION_CONFIRMED',
                            'WHISPER_STATE': 'WHISPER_OK', 'TEXT_SOURCE': 'WHISPER_LOCAL'},
                           {'VIDEO_ID': 'SEM_TEXTO', 'SOURCE_ID': 'x/SEM_TEXTO',
                            'SOURCE_URL': 'https://www.youtube.com/watch?v=SEM_TEXTO',
                            'TITLE': 'Novedades 2026', 'TRANSCRIPT': None,
                            'CAPTION_STATE': 'CAPTION_ENVIRONMENT_FAILURE',
                            'WHISPER_STATE': 'WHISPER_AUDIO_FAILURE',
                            'TEXT_SOURCE': 'TITLE_ONLY'}]}, f)

    def tearDown(self):
        self.ym.SAIDA = self._guardado
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_o_texto_a_mais_tira_um_video_do_NAO_SEI_e_revela_o_campo(self):
        self.assertEqual(0, self.ym.medir())
        with open(os.path.join(self.tmp, 'MICROTESTE.json'), encoding='utf-8') as f:
            d = json.load(f)
        self.assertEqual(2, d['NAO_SEI_BEFORE'], 'título sozinho nunca classifica')
        self.assertEqual(1, d['NAO_SEI_AFTER'])
        self.assertEqual(0, d['FIELD_SIGNAL_BEFORE'])
        self.assertEqual(1, d['FIELD_SIGNAL_AFTER'])
        self.assertEqual(1, d['AG_RELEVANT_AFTER'])

    def test_o_video_sem_texto_continua_NAO_SEI_e_diz_de_qual_degrau_faltou(self):
        self.ym.medir()
        with open(os.path.join(self.tmp, 'MICROTESTE.json'), encoding='utf-8') as f:
            d = json.load(f)
        continua = d['CINCO_EXEMPLOS']['CONTINUOU_NAO_SEI']
        self.assertIsNotNone(continua)
        self.assertEqual('SEM_TEXTO', continua['VIDEO_ID'])
        self.assertEqual('CAPTION_ENVIRONMENT_FAILURE', continua['CAPTION_STATE'])
        self.assertEqual('WHISPER_AUDIO_FAILURE', continua['WHISPER_STATE'])

    def test_todo_tipo_que_a_regua_devolve_cai_em_algum_grupo(self):
        """Um tipo fora de todos os grupos sumiria da contagem sem ninguém notar."""
        conhecidos = (self.ym.NAO_SEI_TIPOS | self.ym.AG_RELEVANT_TIPOS
                      | self.ym.OFF_TOPIC_TIPOS | self.ym.FIELD_SIGNAL_TIPOS)
        devolvidos = {'NOT_ENOUGH_TEXT', 'MARKETING', 'NEWS_REPOST', 'FIELD_OBSERVATION',
                      'RESEARCH_COMMUNICATION', 'TECHNICAL_INTERPRETATION',
                      'EVENT_PROMOTION', 'NOISE'}
        self.assertEqual(set(), devolvidos - conhecidos,
                         'a régua devolve um tipo que a medição não conta')


class TestPortaoFechadoNaoViraPortaoAberto(unittest.TestCase):
    """`rodar` obedece a fila. Fila vazia significa NINGUÉM, nunca "então todo mundo"."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='fila-')
        self.janela = os.path.join(self.tmp, 'YOUTUBE-JANELA')
        self.relev = os.path.join(self.tmp, 'YOUTUBE-RELEVANCIA')
        os.makedirs(self.janela)
        os.makedirs(self.relev)
        self._guardado = (yt.JANELA, yt.RELEVANCIA)
        yt.JANELA, yt.RELEVANCIA = self.janela, self.relev
        with open(os.path.join(self.janela, 'OBJETOS.json'), 'w', encoding='utf-8') as f:
            json.dump({'ITEMS': [{'VIDEO_ID': 'v%d' % n, 'TITLE': 't', 'DURATION_S': 30,
                                  'ACCOUNT_HANDLE': 'h'} for n in range(240)]}, f)
        with open(os.path.join(self.relev, 'FILA-WHISPER.json'), 'w', encoding='utf-8') as f:
            json.dump({'QUEUE': [], 'QUAL_CRITERIO_REALMENTE_FILTRA': 'LEGENDA_NAO_TESTADA'}, f)

    def tearDown(self):
        yt.JANELA, yt.RELEVANCIA = self._guardado
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_fila_vazia_nao_derrama_para_o_acervo_inteiro(self):
        alvos, avisos = yt.universo(so_da_fila=True)
        self.assertEqual([], alvos,
                         'a fila vazia virou 240 vídeos — horas de máquina que ninguém pediu')
        self.assertTrue(any('FILA_VAZIA' in a for a in avisos))

    def test_escada_sem_fila_continua_podendo_rodar_sobre_o_acervo(self):
        """A recusa é de `rodar`, não de `escada`: quem pede sem portão, recebe."""
        alvos, _avisos = yt.universo(so_da_fila=False, teto=5)
        self.assertEqual(5, len(alvos))


class TestReleituraNaoApagaLegendaLida(unittest.TestCase):
    """Um 429 de hoje não pode apagar a legenda que veio inteira ontem."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='merge-')
        self._guardado = yj.SAIDA
        yj.SAIDA = self.tmp
        with open(os.path.join(self.tmp, 'OBJETOS.json'), 'w', encoding='utf-8') as f:
            json.dump({'ITEMS': [
                {'VIDEO_ID': 'JA_LIDO', 'VIDEO_URL': 'https://www.youtube.com/watch?v=JA_LIDO',
                 'TITLE': 'lido ontem', 'ACCOUNT_HANDLE': 'h'}]}, f)
        with open(os.path.join(self.tmp, 'LEGENDAS.json'), 'w', encoding='utf-8') as f:
            json.dump({'ITEMS': [{
                'VIDEO_ID': 'JA_LIDO', 'CAPTION_STATE': 'PRESENTE', 'CAPTION_SEGMENTS': 2,
                'TRANSCRICAO': [{'T_MS': 0, 'DUR_MS': 900, 'TEXTO': 'texto caro'}]}]}, f)

    def tearDown(self):
        yj.SAIDA = self._guardado
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_porta_fechada_hoje_preserva_a_legenda_de_ontem(self):
        # `_abrir` devolvendo porta fechada é exatamente o 429 desta casa.
        original = yj._abrir
        yj._abrir = lambda *a, **k: (None, 'NENHUMA', 'NAVEGADOR_NAO_ALCANCADO')
        try:
            yj.fase_legendas(ids=['JA_LIDO'])
        finally:
            yj._abrir = original
        with open(os.path.join(self.tmp, 'LEGENDAS.json'), encoding='utf-8') as f:
            d = json.load(f)
        i = d['ITEMS'][0]
        self.assertEqual('PRESENTE', i['CAPTION_STATE'],
                         'a releitura falha apagou uma legenda já lida de graça')
        self.assertEqual('texto caro', i['TRANSCRICAO'][0]['TEXTO'])
        self.assertEqual('PORTA_NAO_ABRIU', i['RELEITURA_FALHOU_COM'])
        self.assertEqual(1, d['LEGENDAS_RESGATADAS_DE_RELEITURA_FALHA'])


class TestAuditoriaDeIdentidadeAcusa(unittest.TestCase):
    """Um contador que não pode dar diferente de zero não mede nada."""

    def test_handle_fora_do_lote_e_acusado(self):
        a = yt.auditar_identidade(
            [{'VIDEO_ID': 'v1', 'SOURCE_ID': 'x', 'ACCOUNT_HANDLE': 'INVENTADO_NA_FALA',
              'COUNTRY': 'ES'}],
            objetos=[{'VIDEO_ID': 'v1', 'ACCOUNT_HANDLE': 'INVENTADO_NA_FALA'}])
        self.assertEqual(1, a['NEW_ENTITIES_FROM_CONTENT'])
        self.assertGreaterEqual(a['IDENTITY_ERRORS'], 1)

    def test_papel_diferente_do_lote_e_acusado(self):
        handle = sorted(yt.paises_do_lote())[0]
        a = yt.auditar_identidade(
            [{'VIDEO_ID': 'v1', 'SOURCE_ID': 'x', 'ACCOUNT_HANDLE': handle,
              'PAGE_ROLE': 'INFLUENCER_INVENTADO'}],
            objetos=[{'VIDEO_ID': 'v1', 'ACCOUNT_HANDLE': handle}])
        self.assertEqual(1, a['ROLE_FROM_CONTENT'])

    def test_pais_diferente_do_lote_e_acusado(self):
        handle = sorted(yt.paises_do_lote())[0]
        a = yt.auditar_identidade(
            [{'VIDEO_ID': 'v1', 'SOURCE_ID': 'x', 'ACCOUNT_HANDLE': handle,
              'COUNTRY': 'ZZ'}],
            objetos=[{'VIDEO_ID': 'v1', 'ACCOUNT_HANDLE': handle}])
        self.assertGreaterEqual(a['IDENTITY_ERRORS'], 1)

    def test_documento_sem_source_id_e_acusado(self):
        a = yt.auditar_identidade([{'VIDEO_ID': 'v1'}], objetos=[])
        self.assertEqual(1, a['DOCUMENT_WITHOUT_SOURCE_ID'])


class TestAudioSuspeito(unittest.TestCase):
    """Sobras de download não são áudio, e meio áudio não é transcrição completa."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='audio-')
        self._guardado = yt.MEDIA
        yt.MEDIA = self.tmp

    def tearDown(self):
        yt.MEDIA = self._guardado
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _escrever(self, nome, n=5000):
        with open(os.path.join(self.tmp, nome), 'wb') as f:
            f.write(b'\0' * n)

    def test_arquivo_part_nao_e_aceito_como_audio_pronto(self):
        """Um `.part` de 4 MB é grande, legítimo aos olhos de getsize — e meio vídeo."""
        self._escrever('VID12345678.m4a.part')
        self.assertIsNone(yt._audio_em_cache('VID12345678'))

    def test_arquivo_ytdl_nao_e_aceito(self):
        self._escrever('VID12345678.ytdl')
        self.assertIsNone(yt._audio_em_cache('VID12345678'))

    def test_o_arquivo_inteiro_e_aceito(self):
        self._escrever('VID12345678.m4a')
        self.assertTrue(yt._audio_em_cache('VID12345678').endswith('.m4a'))

    def test_o_seletor_do_yt_dlp_nao_autoriza_video(self):
        """`best` sozinho traria um MP4 com imagem para dentro do cache de ÁUDIO."""
        fonte = open(os.path.join(ROOT, 'scripts', 'youtube_transcrever.py'),
                     encoding='utf-8').read()
        self.assertIn('vcodec=none', fonte)
        self.assertNotIn("'bestaudio/best'", fonte)


class TestVereditoDaMissao(unittest.TestCase):
    """A taxa que decide a missão, e o denominador que pode transformá-la em mentira.

    RECOVERY_RATE responde "de quantos vídeos sem legenda o whisper resgatou o texto?".
    Ela só responde isso quando o denominador é feito de vídeos SEM LEGENDA. Neste
    contêiner, em 2026-09-04 e de novo em 2026-09-05, os dez vídeos do microteste
    chegaram ao whisper por HTTP 429 — e uma taxa lida sobre esse denominador diria
    "o YouTube dos concorrentes não tem legenda" quando o fato é "a minha rede não
    abriu a porta".

        A MESMA FRAÇÃO, COM O MESMO VALOR, RESPONDE DUAS PERGUNTAS DIFERENTES.
    """

    def _texto(self, **kw):
        base = {'CAPTION_HITS': 0, 'WHISPER_FALLBACKS': 0, 'WHISPER_SUCCESS': 0,
                'POR_ESTADO_DE_LEGENDA': {}, 'TOTAL_MACHINE_SECONDS': 0}
        base.update(kw)
        return base

    def _linhas(self, *fontes):
        return [{'TEXT_SOURCE': f, 'VIDEO_ID': 'v%d' % n} for n, f in enumerate(fontes)]

    def test_denominador_de_ausencia_confirmada_e_uma_taxa_de_legenda(self):
        v = mt._veredito_da_missao(
            self._linhas('WHISPER_LOCAL', 'WHISPER_LOCAL', 'TITLE_ONLY', 'YOUTUBE_CAPTION'),
            self._texto(CAPTION_HITS=1, WHISPER_FALLBACKS=3, WHISPER_SUCCESS=2,
                        POR_ESTADO_DE_LEGENDA={yt.NO_CAPTION_CONFIRMED: 3},
                        TOTAL_MACHINE_SECONDS=120.0))
        self.assertEqual(v['RECOVERY_RATE'], round(2 / 3, 3))
        self.assertEqual(v['RECOVERY_RATE_MEDE_A_LEGENDA'], 'SIM')
        self.assertEqual(v['CAPTION_INCONCLUSIVE'], 0)

    def test_denominador_de_429_nao_e_uma_taxa_de_legenda(self):
        """O caso real deste contêiner: dez vídeos, dez 429, zero fato sobre legenda."""
        v = mt._veredito_da_missao(
            self._linhas(*(['TITLE_ONLY'] * 10)),
            self._texto(WHISPER_FALLBACKS=10, WHISPER_SUCCESS=0,
                        POR_ESTADO_DE_LEGENDA={yt.CAPTION_ENVIRONMENT_FAILURE: 10}))
        self.assertEqual(v['RECOVERY_RATE'], 0.0)
        self.assertTrue(v['RECOVERY_RATE_MEDE_A_LEGENDA'].startswith('NAO'))
        self.assertEqual(v['CAPTION_ABSENT_CONFIRMED'], 0)
        self.assertEqual(v['CAPTION_INCONCLUSIVE'], 10)
        self.assertIn('minha rede', v['O_QUE_O_DENOMINADOR_TEM_DENTRO'])

    def test_denominador_zero_nao_vira_zero_por_cento(self):
        """0/0 não é "o whisper resgatou 0%%". É "ninguém perguntou"."""
        v = mt._veredito_da_missao(self._linhas('YOUTUBE_CAPTION'),
                                   self._texto(CAPTION_HITS=1))
        self.assertEqual(v['RECOVERY_RATE'], yt.NAO_SEI)
        self.assertIn('NAO_SE_APLICA', v['RECOVERY_RATE_MEDE_A_LEGENDA'])

    def test_cobertura_conta_videos_e_nao_caracteres(self):
        """Dobrar o texto de quem já falava não cobre quem calava."""
        v = mt._veredito_da_missao(
            self._linhas('WHISPER_LOCAL', 'TITLE_ONLY', 'YOUTUBE_CAPTION'),
            self._texto(CAPTION_HITS=1, WHISPER_FALLBACKS=2, WHISPER_SUCCESS=1,
                        POR_ESTADO_DE_LEGENDA={yt.NO_CAPTION_CONFIRMED: 2}))
        self.assertEqual(v['COVERAGE_AFTER'], 2)
        self.assertEqual(v['VIDEOS_TESTADOS'], 3)
        self.assertIn('2/3', v['COVERAGE_GAIN'])

    def test_custo_medio_sai_do_acumulado_e_nao_da_rodada_em_cache(self):
        """A segunda passada do microteste é toda em cache. Ela não torna o lote grátis."""
        v = mt._veredito_da_missao(
            self._linhas('WHISPER_LOCAL', 'WHISPER_LOCAL'),
            self._texto(WHISPER_FALLBACKS=2, WHISPER_SUCCESS=2,
                        POR_ESTADO_DE_LEGENDA={yt.NO_CAPTION_CONFIRMED: 2},
                        TOTAL_MACHINE_SECONDS=0.0,
                        TOTAL_MACHINE_SECONDS_ACUMULADO=99.0))
        self.assertEqual(v['AVG_MACHINE_SECONDS_PER_TRANSCRIPTION'], 49.5)
        self.assertEqual(v['ESTIMATED_COST_USD'], 0)

    def test_sem_transcricao_o_custo_medio_e_NOT_KNOWN_e_nao_zero(self):
        v = mt._veredito_da_missao(self._linhas('TITLE_ONLY'),
                                   self._texto(WHISPER_FALLBACKS=1))
        self.assertEqual(v['AVG_MACHINE_SECONDS_PER_TRANSCRIPTION'], yt.NAO_SEI)


if __name__ == '__main__':
    unittest.main(verbosity=2)
