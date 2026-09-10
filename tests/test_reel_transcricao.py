"""A FALA DE UM REEL VIRA TEXTO SEM VIRAR MENTIRA.

Estes testes não pedem nada à internet e não gastam um cêntimo. Eles medem o
CONTRATO: os estados, a separação entre legenda e fala, o pai de cada derivado,
e as três confusões que este pipeline foi escrito para não fazer.

    RAW != DERIVED · CAPTION != TRANSCRIPT · SEM TEXTO != SEM FALA

O que eles NÃO provam é que a Instagram responde. Isso não se prova com mock —
só se prova a tentar, e a prova viva está em
`data/samples/REEL-TRANSCRICOES/TRANSCRICOES-REEL.json`, com seis Reels reais.

    MOCK PASSANDO != INSTAGRAM FUNCIONANDO.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import artefato as art               # noqa: E402
import fala_local as fl              # noqa: E402
import reel_transcricao as rt        # noqa: E402
import comunicacao_classificar as cc  # noqa: E402


# ── UM RECONHECEDOR DE MENTIRA, PARA MEDIR O QUE O VERDADEIRO FARIA ─────────
# Não é para fingir que a transcrição funciona: é para poder pôr o pipeline em
# cada um dos estados possíveis sem depender de que áudio existe hoje.
class FalaFalsa:
    def __init__(self, resposta):
        self.resposta = resposta
        self.chamadas = []

    def __call__(self, wav, **kw):
        self.chamadas.append((wav, kw))
        return dict(self.resposta)


def resposta(estado=fl.OK, texto='ha pressao de septoriose no trigo', **extra):
    base = {
        'TRANSCRIPT': texto, 'TRANSCRIPT_STATE': estado,
        'TRANSCRIPT_CHARS': len(texto or ''), 'SEGMENTS':
            [{'start': 0.0, 'end': 3.0, 'text': texto or ''}] if texto else [],
        'LANGUAGE': 'it', 'LANGUAGE_SOURCE': 'DECLARED',
        'LANGUAGE_DETECTED': 'it', 'LANGUAGE_CONFIDENCE': 0.99,
        'LANGUAGE_STATE': 'CONFIAVEL', 'AUDIO_SECONDS': 30.0,
        'MACHINE_SECONDS': 7.0, 'REALTIME_FACTOR': 4.28,
        'VOICED_SEGMENTS': 1, 'NO_SPEECH_PROB_MEAN': 0.05,
        'ASR_ENGINE': 'faster-whisper', 'ASR_ENGINE_VERSION': '1.2.1',
        'ASR_MODEL': 'small', 'TRANSCRIBER_ID': 'ferramentas/fala_local.py',
    }
    base.update(extra)
    return base


class Cadeia(unittest.TestCase):
    """Cada teste corre numa casa de mentira, para não sujar a de verdade."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='reel-teste-')
        self._midia, self._saida = rt.MIDIA, rt.SAIDA
        self._transcrever, self._extrair = fl.transcrever, fl.extrair_audio
        rt.MIDIA = os.path.join(self.tmp, 'raw')
        rt.SAIDA = os.path.join(self.tmp, 'saida')
        os.makedirs(rt.MIDIA)
        os.makedirs(rt.SAIDA)
        # Um «vídeo» com bytes suficientes para valer como ficheiro real.
        self.video = os.path.join(self.tmp, 'video.mp4')
        with open(self.video, 'wb') as f:
            f.write(b'\x00\x00\x00\x18ftypmp42' + b'BYTES-DE-TESTE' * 2000)
        fl.extrair_audio = lambda entrada, wav: (self._wav(wav), None)

    def tearDown(self):
        rt.MIDIA, rt.SAIDA = self._midia, self._saida
        fl.transcrever, fl.extrair_audio = self._transcrever, self._extrair
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _wav(self, wav):
        with open(wav, 'wb') as f:
            f.write(b'RIFF' + b'\x00' * 5000)
        return wav

    def _ident(self, **kw):
        d = rt.identidade_do_url('https://www.instagram.com/syngentaitalia/reel/ABC12345678/')
        d.update({'COUNTRY_SCOPE': 'IT', 'ACCOUNT_ID': 'syngentaitalia',
                  'CAPTION_TEXT': 'Confira nosso dia de campo'})
        d.update(kw)
        return d

    def _correr(self, resp=None, **kw):
        fl.transcrever = FalaFalsa(resp or resposta())
        return rt.transcrever_reel(self._ident(**kw), run_id='RUN-1',
                                   midia_ficheiro=self.video)


# ═══════════════════════════════════════════ 1 · IDENTIDADE NÃO SE INVENTA
class Identidade(unittest.TestCase):

    def test_o_shortcode_sai_do_endereco(self):
        d = rt.identidade_do_url('https://www.instagram.com/syngentaitalia/reel/C-FanW_CYMz/')
        self.assertEqual(d['POST_ID'], 'C-FanW_CYMz')
        self.assertEqual(d['PLATFORM'], 'INSTAGRAM')
        self.assertEqual(d['ACCOUNT_HANDLE_FROM_URL'], 'syngentaitalia')

    def test_endereco_sem_publicacao_nao_ganha_id_inventado(self):
        d = rt.identidade_do_url('https://exemplo.pt/qualquer-coisa')
        self.assertEqual(d['POST_ID'], 'NOT_KNOWN')
        self.assertEqual(d['PLATFORM'], 'NOT_KNOWN')

    def test_o_mesmo_reel_por_dois_enderecos_e_o_mesmo_reel(self):
        a = rt.identidade_do_url('https://www.instagram.com/reel/ABC12345678/')
        b = rt.identidade_do_url('https://www.instagram.com/qualquer/p/ABC12345678/?utm=x')
        self.assertEqual(a['POST_ID'], b['POST_ID'])
        self.assertEqual(a['SOURCE_URL'], b['SOURCE_URL'])

    def test_a_lingua_sai_do_pais_provado_e_nao_de_um_palpite(self):
        self.assertEqual(rt.idioma_provado('IT'), 'it')
        self.assertEqual(rt.idioma_provado('ES'), 'es')
        self.assertEqual(rt.idioma_provado('FR'), 'fr')
        self.assertIsNone(rt.idioma_provado('NOT_KNOWN'))
        self.assertIsNone(rt.idioma_provado(None))


# ═══════════════════════════════════════════════ 2 · RAW E DERIVED, SEPARADOS
class RawEDerivado(Cadeia):

    def test_o_derivado_declara_o_pai_e_o_pai_e_o_video(self):
        r = self._correr()
        self.assertEqual(r['DERIVED']['PARENT_ARTIFACT_ID'], r['RAW']['ARTIFACT_ID'])
        self.assertEqual(r['DERIVED']['PARENT_SHA256'], r['RAW']['SHA256'])
        self.assertEqual(r['DERIVED']['DERIVATION_TYPE'], art.SPEECH_TRANSCRIPTION)

    def test_o_filho_nao_tem_o_nome_do_pai(self):
        r = self._correr()
        self.assertNotEqual(r['DERIVED']['ARTIFACT_ID'], r['RAW']['ARTIFACT_ID'])
        self.assertTrue(r['RAW']['ARTIFACT_ID'].startswith('RAW-'))
        self.assertTrue(r['DERIVED']['ARTIFACT_ID'].startswith('DERIVED-'))

    def test_o_derivado_passa_no_validador_da_casa(self):
        r = self._correr()
        self.assertNotEqual(r['DERIVED']['STATE'], 'CONTRATO_QUEBRADO', r['DERIVED'].get('ERROR'))

    def test_o_raw_nao_ganha_data_de_derivacao_e_o_derivado_nao_ganha_coleta_nova(self):
        r = self._correr()
        self.assertEqual(r['RAW']['DERIVED_AT'], art.NAO_SE_APLICA)
        self.assertEqual(r['DERIVED']['COLLECTED_AT'], r['RAW']['COLLECTED_AT'])
        self.assertNotEqual(r['DERIVED']['DERIVED_AT'], art.NAO_SE_APLICA)

    def test_ninguem_decide_o_lugar_nem_o_tempo_do_fato(self):
        r = self._correr()
        self.assertEqual(r['RAW']['FACT_LOCATION'], art.NAO_SEI)
        self.assertEqual(r['DERIVED']['FACT_LOCATION'], art.NAO_SEI)
        self.assertEqual(r['RAW']['FACT_TIME'], art.NAO_SEI)
        self.assertIn('NOT_KNOWN', r['PROVENANCE']['FACT_LOCATION'])

    def test_o_id_da_observacao_nao_e_o_sha_dos_bytes(self):
        """A lei da fundação: SHA256 identifica conteúdo, nunca observação."""
        r = self._correr()
        self.assertEqual(r['PROVENANCE']['QUAL_RAW_OBSERVATION_ID'], 'NOT_KNOWN')
        self.assertNotEqual(r['PROVENANCE']['QUAL_RAW_OBSERVATION_ID'],
                            r['PROVENANCE']['QUAL_SHA256_DA_MIDIA'])

    def test_o_id_da_observacao_entra_quando_alguem_o_prova(self):
        r = self._correr(RAW_OBSERVATION_ID='raw_asset:9f3c')
        self.assertEqual(r['PROVENANCE']['QUAL_RAW_OBSERVATION_ID'], 'raw_asset:9f3c')
        self.assertEqual(r['DERIVED']['NOTES']['RAW_OBSERVATION_ID'], 'raw_asset:9f3c')


# ══════════════════════════════════════════════ 3 · LEGENDA NÃO É TRANSCRIÇÃO
class LegendaNaoEFala(Cadeia):

    def test_os_dois_textos_vivem_em_campos_diferentes(self):
        r = self._correr()
        self.assertEqual(r['CAPTION_TEXT'], 'Confira nosso dia de campo')
        self.assertEqual(r['TRANSCRIPT_TEXT'], 'ha pressao de septoriose no trigo')
        self.assertNotIn('septoriose', r['CAPTION_TEXT'])

    def test_a_fala_da_plataforma_nao_finge_que_esta_maquina_ouviu(self):
        ident = self._ident()
        r = rt.transcrever_reel(ident, run_id='RUN-1',
                                transcript_da_fonte='texto vindo pronto da fonte')
        self.assertEqual(r['TRANSCRIPT_PROVIDER'], rt.FONTE)
        self.assertEqual(r['PROVENANCE']['QUAL_MOTOR'], art.NAO_SE_APLICA)
        self.assertEqual(r['PROVENANCE']['QUEM_TRANSCREVEU'], art.NAO_SE_APLICA)

    def test_a_nossa_fala_diz_que_e_nossa(self):
        r = self._correr()
        self.assertEqual(r['TRANSCRIPT_PROVIDER'], rt.ASR_LOCAL)
        self.assertEqual(r['PROVENANCE']['FALA_DA_FONTE_OU_NOSSA'], rt.ASR_LOCAL)
        self.assertEqual(r['PROVENANCE']['QUAL_MOTOR'], 'faster-whisper')


# ═════════════════════════════════════════════ 4 · OS ESTADOS, E O QUE NEGAM
class Estados(Cadeia):

    def test_sem_endereco_nenhum_o_estado_diz_isso_e_nao_diz_sem_fala(self):
        fl.transcrever = FalaFalsa(resposta())
        r = rt.transcrever_reel({'PLATFORM': 'TIKTOK', 'POST_ID': 'X1',
                                 'SOURCE_URL': 'NOT_KNOWN'}, run_id='RUN-1')
        self.assertEqual(r['TRANSCRIPT_STATE'], rt.NAO_PEDIDO)
        self.assertIsNone(r['TRANSCRIPT_TEXT'])
        self.assertIn('ninguem chegou a ouvi-lo', r['NAO_SIGNIFICA'])
        self.assertIsNone(r['DERIVED'])

    def test_audio_que_nao_sai_nao_vira_video_sem_fala(self):
        fl.extrair_audio = lambda entrada, wav: (None, 'FFMPEG_AUSENTE')
        fl.transcrever = FalaFalsa(resposta())
        r = rt.transcrever_reel(self._ident(), run_id='RUN-1',
                                midia_ficheiro=self.video)
        self.assertEqual(r['TRANSCRIPT_STATE'], fl.ASR_FALHOU)
        self.assertIn('nao tem fala', r['NAO_SIGNIFICA'])
        self.assertIsNotNone(r['RAW'])       # o byte ficou preservado
        self.assertIsNone(r['DERIVED'])      # e não nasceu texto nenhum

    def test_texto_vazio_e_um_estado_e_nao_um_veredito(self):
        r = self._correr(resposta(estado=fl.REQUESTED_EMPTY, texto=''))
        self.assertEqual(r['TRANSCRIPT_STATE'], fl.REQUESTED_EMPTY)
        self.assertIsNone(r['DERIVED'])

    def test_o_reconhecedor_que_cai_nao_apaga_o_video(self):
        r = self._correr(resposta(estado=fl.ASR_FALHOU, texto=None,
                                  ERROR='RuntimeError: kaput'))
        self.assertEqual(r['TRANSCRIPT_STATE'], fl.ASR_FALHOU)
        self.assertIn('kaput', r['ERROR'])
        self.assertIsNotNone(r['RAW'])

    def test_cada_degrau_de_captura_fica_escrito(self):
        r = self._correr()
        self.assertTrue(r['CAPTURE_ATTEMPTS'])
        self.assertEqual(r['CAPTURE_ATTEMPTS'][0]['RESULT'], rt.MEDIA_OK)


# ═══════════════════════════════════ 5 · ALUCINAÇÃO NÃO PASSA POR TRANSCRIÇÃO
class Alucinacao(unittest.TestCase):
    """Medido em 2026-09-10 num Reel real: sobre música o motor devolveu `...`.

    Sem esta trava, três pontos chegavam à camada de classificação como se
    fossem a fala do vídeo.
    """

    def test_pontuacao_sozinha_nao_e_fala_escrita(self):
        for lixo in ('...', '. . .', '   ', '♪♪♪', '!!!', '-- --'):
            with self.subTest(saida=lixo):
                self.assertFalse(fl._tem_conteudo(lixo))

    def test_fala_de_verdade_passa_em_qualquer_alfabeto(self):
        for bom in ('Buongiorno', 'Ça va', 'año 2026', 'Ήταν', 'Привет', '2026'):
            with self.subTest(saida=bom):
                self.assertTrue(fl._tem_conteudo(bom))


# ══════════════════════════════════════════ 6 · REOBSERVAR NÃO DUPLICA NADA
class Retry(Cadeia):

    def test_duas_corridas_sobre_o_mesmo_video_dao_uma_linha_so(self):
        fl.transcrever = FalaFalsa(resposta())
        ident = self._ident()
        a = rt.transcrever_reel(ident, run_id='RUN-1', midia_ficheiro=self.video)
        b = rt.transcrever_reel(ident, run_id='RUN-2', midia_ficheiro=self.video)
        self.assertEqual(a['RAW']['ARTIFACT_ID'], b['RAW']['ARTIFACT_ID'])
        _, corpo = rt.gravar_lote([a])
        _, corpo = rt.gravar_lote([b])
        self.assertEqual(corpo['ITEM_COUNT'], 1)

    def test_mas_as_duas_corridas_continuam_a_existir(self):
        fl.transcrever = FalaFalsa(resposta())
        ident = self._ident()
        rt.gravar_lote([rt.transcrever_reel(ident, run_id='RUN-1',
                                            midia_ficheiro=self.video)])
        _, corpo = rt.gravar_lote([rt.transcrever_reel(ident, run_id='RUN-2',
                                                       midia_ficheiro=self.video)])
        self.assertEqual(corpo['ITEMS'][0]['TIMES_OBSERVED'], 2)
        self.assertEqual(corpo['ITEMS'][0]['RUN_IDS_SEEN'], ['RUN-1', 'RUN-2'])

    def test_um_resultado_corrigido_substitui_o_antigo_em_vez_de_conviver(self):
        """O defeito real: indexar pelo DERIVADO fazia o texto errado sobreviver."""
        ident = self._ident()
        fl.transcrever = FalaFalsa(resposta(texto='...'))
        rt.gravar_lote([rt.transcrever_reel(ident, run_id='RUN-1',
                                            midia_ficheiro=self.video)])
        fl.transcrever = FalaFalsa(resposta(estado=fl.REQUESTED_EMPTY, texto=''))
        _, corpo = rt.gravar_lote([rt.transcrever_reel(ident, run_id='RUN-2',
                                                       midia_ficheiro=self.video)])
        self.assertEqual(corpo['ITEM_COUNT'], 1)
        self.assertEqual(corpo['ITEMS'][0]['TRANSCRIPT_STATE'], fl.REQUESTED_EMPTY)

    def test_uma_falha_tambem_tem_lugar_no_livro(self):
        fl.transcrever = FalaFalsa(resposta())
        r = rt.transcrever_reel({'PLATFORM': 'TIKTOK', 'POST_ID': 'SEM-MIDIA',
                                 'SOURCE_URL': 'NOT_KNOWN'}, run_id='RUN-1')
        _, corpo = rt.gravar_lote([r])
        self.assertEqual(corpo['ITEM_COUNT'], 1)
        self.assertEqual(corpo['TRANSCRIBED_OK'], 0)


# ════════════════════════════ 7 · A CAMADA DE COMUNICAÇÃO PASSA A OUVIR
class ClassificacaoOuveAFala(unittest.TestCase):

    CAPTION_POBRE = 'Confira nosso dia de campo'
    FALA_RICA = ('Oggi parliamo della pressione di septoria sul frumento in '
                 'Puglia, con una prova di campo')

    def test_antes_da_fala_a_legenda_pobre_nao_dizia_nada(self):
        r = cc.classificar({'TITLE': '', 'TEXT': self.CAPTION_POBRE})
        self.assertEqual(r['ISSUE'], ['NOT_KNOWN'])
        self.assertEqual(r['CROP'], ['NOT_KNOWN'])
        self.assertEqual(r['TRANSCRIPT_AVAILABLE'], 'NO')

    def test_com_a_fala_o_mesmo_item_passa_a_dizer(self):
        r = cc.classificar({'TITLE': '', 'TEXT': self.CAPTION_POBRE,
                            'TRANSCRIPT_TEXT': self.FALA_RICA})
        self.assertIn('SEPTORIA', r['ISSUE'])
        self.assertIn('CEREAL', r['CROP'])
        self.assertEqual(r['TRANSCRIPT_AVAILABLE'], 'YES')

    def test_e_da_para_provar_que_a_evidencia_veio_da_fala(self):
        r = cc.classificar({'TITLE': '', 'TEXT': self.CAPTION_POBRE,
                            'TRANSCRIPT_TEXT': self.FALA_RICA})
        self.assertEqual(r['EVIDENCE_BY_LABEL']['ISSUE']['SEPTORIA'], ['TRANSCRIPT'])
        self.assertIn('SEPTORIA', r['FOUND_ONLY_IN_TRANSCRIPT'])
        self.assertEqual(sorted(r['TEXT_SOURCES']), ['CAPTION', 'TRANSCRIPT'])

    def test_o_lugar_ouvido_diz_que_foi_ouvido(self):
        r = cc.classificar({'TITLE': '', 'TEXT': self.CAPTION_POBRE,
                            'COUNTRY_SCOPE': 'IT',
                            'TRANSCRIPT_TEXT': self.FALA_RICA})
        self.assertEqual(r['COUNTRY_OF_FACT'], 'IT')
        self.assertIn('TRANSCRIPT', r['COUNTRY_OF_FACT_EVIDENCE'])
        self.assertEqual(r['EVIDENCE_BY_LABEL']['COUNTRY_OF_FACT']['IT'], ['TRANSCRIPT'])

    def test_o_que_estava_nos_dois_diz_que_estava_nos_dois(self):
        r = cc.classificar({'TITLE': '', 'TEXT': 'giornata tecnica sul frumento',
                            'TRANSCRIPT_TEXT': 'parliamo di frumento e di septoria'})
        self.assertEqual(r['EVIDENCE_BY_LABEL']['CROP']['CEREAL'],
                         ['CAPTION', 'TRANSCRIPT'])
        self.assertEqual(r['FOUND_ONLY_IN_TRANSCRIPT'], ['SEPTORIA'])

    def test_a_fala_nao_e_somada_a_legenda(self):
        """Se fossem somadas, ninguém saberia de qual das duas veio o rótulo."""
        r = cc.classificar({'TITLE': '', 'TEXT': 'nada de util aqui',
                            'TRANSCRIPT_TEXT': 'repilo no olivar'})
        self.assertEqual(r['EVIDENCE_BY_LABEL']['ISSUE']['REPILO'], ['TRANSCRIPT'])
        self.assertEqual(r['CAPTION_AVAILABLE'], 'YES')

    def test_um_item_sem_fala_pedida_nao_se_confunde_com_um_sem_fala(self):
        pedido = cc.classificar({'TEXT': 'x', 'TRANSCRIPT_STATE': 'NOT_REQUESTED'})
        vazio = cc.classificar({'TEXT': 'x', 'TRANSCRIPT_STATE': 'REQUESTED_EMPTY'})
        self.assertEqual(pedido['TRANSCRIPT_STATE'], 'NOT_REQUESTED')
        self.assertEqual(vazio['TRANSCRIPT_STATE'], 'REQUESTED_EMPTY')
        self.assertEqual(pedido['TRANSCRIPT_AVAILABLE'], 'NO')
        self.assertEqual(vazio['TRANSCRIPT_AVAILABLE'], 'NO')

    def test_os_campos_antigos_continuam_a_existir(self):
        """Quem já lia este artefato não pode acordar com o contrato mudado."""
        r = cc.classificar({'TITLE': 'lancio', 'TEXT': 'nuovo fungicida per il frumento'})
        for campo in ('TEXT_AVAILABLE', 'COMMUNICATION_TYPES', 'CROP', 'ISSUE',
                      'COUNTRY_OF_FACT', 'COUNTRY_OF_FACT_EVIDENCE',
                      'EVIDENCE_CLASS', 'DATASET_OWNER'):
            self.assertIn(campo, r)
        self.assertIn('PRODUCT_COMMUNICATION', r['COMMUNICATION_TYPES'])
        self.assertIn('CEREAL', r['CROP'])


# ═══════════════════════════════════ 8 · O DONO DO RECONHECIMENTO É UM SÓ
class UmDonoSo(unittest.TestCase):

    def test_os_tres_chamadores_usam_o_mesmo_reconhecedor(self):
        import instagram_transcrever as it
        import youtube_transcrever as yt
        with open(it.__file__, encoding='utf-8') as f:
            fonte_it = f.read()
        with open(yt.__file__, encoding='utf-8') as f:
            fonte_yt = f.read()
        for nome, fonte in (('instagram', fonte_it), ('youtube', fonte_yt)):
            with self.subTest(ficheiro=nome):
                self.assertIn('import fala_local', fonte)
                # Ninguém volta a carregar o modelo por sua conta.
                self.assertNotIn('WhisperModel(', fonte)
                self.assertNotIn('BatchedInferencePipeline(', fonte)

    def test_o_carimbo_do_motor_se_diz_inteiro(self):
        c = fl.carimbo('small')
        for campo in ('ASR_ENGINE', 'ASR_ENGINE_VERSION', 'ASR_MODEL', 'ASR_BEAM',
                      'ASR_VAD', 'TRANSCRIBER_ID', 'TRANSCRIBER_VERSION'):
            self.assertIn(campo, c)
        self.assertEqual(c['ASR_VAD'], 'YES')
        self.assertEqual(c['ASR_CONDITION_ON_PREVIOUS_TEXT'], 'NO')

    def test_o_estado_fora_do_vocabulario_e_recusado(self):
        with self.assertRaises(ValueError):
            fl._resposta('INVENTADO', 'small')


# ═══════════════════════════════════ 9 · A PORTA É DO ORQUESTRADOR
class APorta(unittest.TestCase):

    def test_o_pedido_de_transcricao_resolve_no_executor_registado(self):
        from pedido import Pedido
        from receitas import resolver
        p = Pedido(alvo='colete concorrentes',
                   filtros={'fase': 'transcrever', 'plataforma': 'INSTAGRAM'})
        e = resolver(p).executores[0]
        comando = list(e['roda'])
        valores = {**(e.get('filtros_por_omissao') or {}), **p.filtros}
        for nome in e.get('argumentos_de_filtros') or []:
            if valores.get(nome):
                comando.append(str(valores[nome]))
        self.assertEqual(comando, ['coleta/comunicacao_coleta.py', 'transcrever',
                                   'INSTAGRAM'])

    def test_a_coleta_preserva_o_endereco_do_video_para_a_fala_de_depois(self):
        import comunicacao_coleta as cco
        bruto = {'id': 'ABC', 'caption': 'legenda', 'type': 'Video',
                 'videoUrl': 'https://cdn.example/x.mp4', 'videoDuration': 34.1}
        conta = {'ACCOUNT_HANDLE': 'h', 'ACCOUNT_URL': 'u', 'COMPANY': 'c',
                 'COUNTRY': 'IT', 'ACCOUNT_SCOPE': 's'}
        i = cco.normalizar(bruto, conta, 'INSTAGRAM', 30)
        self.assertEqual(i['MEDIA_URL_TEMPORARY'], 'https://cdn.example/x.mp4')
        self.assertEqual(i['IS_VIDEO'], 'YES')
        self.assertEqual(i['TEXT_KIND'], 'CAPTION')
        self.assertEqual(i['TRANSCRIPT_STATE'], 'NOT_REQUESTED')

    def test_o_item_coletado_vira_identidade_sem_perder_a_legenda(self):
        import comunicacao_coleta as cco
        bruto = {'id': 'ABC12345678', 'caption': 'dia de campo', 'type': 'Video',
                 'videoUrl': 'https://cdn.example/x.mp4',
                 'url': 'https://www.instagram.com/reel/ABC12345678/'}
        conta = {'ACCOUNT_HANDLE': 'syngentaitalia', 'ACCOUNT_URL': 'u',
                 'COMPANY': 'SYNGENTA', 'COUNTRY': 'IT', 'ACCOUNT_SCOPE': 's'}
        ident = rt.de_item_de_comunicacao(cco.normalizar(bruto, conta, 'INSTAGRAM', 30))
        self.assertEqual(ident['POST_ID'], 'ABC12345678')
        self.assertEqual(ident['CAPTION_TEXT'], 'dia de campo')
        self.assertEqual(ident['MEDIA_URL'], 'https://cdn.example/x.mp4')
        self.assertEqual(ident['COUNTRY_SCOPE'], 'IT')


# ═════════════════════════════ 10 · A PROVA VIVA, QUANDO ELA EXISTIR
class ProvaViva(unittest.TestCase):
    """Não é mock. Lê o artefato que seis Reels reais produziram.

    Se o ficheiro não existir, o teste diz que não correu — nunca finge que passou.
    """

    CAMINHO = os.path.join(RAIZ, 'data', 'samples', 'REEL-TRANSCRICOES',
                           'TRANSCRICOES-REEL.json')

    def setUp(self):
        if not os.path.exists(self.CAMINHO):
            self.skipTest('ainda nao ha prova viva em %s' % self.CAMINHO)
        with open(self.CAMINHO, encoding='utf-8') as f:
            self.d = json.load(f)

    def test_todo_texto_real_tem_pai_declarado(self):
        for i in self.d['ITEMS']:
            if i.get('TRANSCRIPT_STATE') != 'OK':
                continue
            with self.subTest(reel=i['REEL']['POST_ID']):
                self.assertIsNotNone(i.get('DERIVED'), 'texto sem pai')
                self.assertEqual(i['DERIVED']['PARENT_ARTIFACT_ID'],
                                 i['RAW']['ARTIFACT_ID'])
                self.assertTrue(i['DERIVED']['NOTES']['MEDIA_SHA256'])

    def test_nenhum_texto_real_e_pontuacao_solta(self):
        for i in self.d['ITEMS']:
            if i.get('TRANSCRIPT_STATE') == 'OK':
                with self.subTest(reel=i['REEL']['POST_ID']):
                    self.assertTrue(fl._tem_conteudo(i['TRANSCRIPT_TEXT']))

    def test_nenhum_segredo_entrou_no_artefato(self):
        with open(self.CAMINHO, encoding='utf-8') as f:
            cru = f.read().lower()
        for veneno in ('apify_api_', 'authorization', 'bearer ', 'service_role'):
            self.assertNotIn(veneno, cru)

    def test_a_legenda_nunca_foi_copiada_para_o_campo_da_fala(self):
        for i in self.d['ITEMS']:
            leg, fala = i.get('CAPTION_TEXT'), i.get('TRANSCRIPT_TEXT')
            if leg and fala and leg != 'NOT_KNOWN':
                with self.subTest(reel=i['REEL']['POST_ID']):
                    self.assertNotEqual(leg.strip(), fala.strip())


if __name__ == '__main__':
    unittest.main(verbosity=2)
