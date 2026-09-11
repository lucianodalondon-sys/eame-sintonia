#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS DOZE PROVAS DA CONVERGENCIA C1.

Cada uma existe porque um defeito concreto ja aconteceu nesta casa, ou porque
o benchmark provou que ele pode acontecer. Nenhuma e decorativa.

    UM TESTE QUE SO PASSA NAO E UM TESTE. Cada um destes reprova alguma coisa
    que alguem faria de boa-fe daqui a tres meses.
"""
import ast
import collections
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import scrap_capacidades as cap    # noqa: E402
import scrap_registo as reg        # noqa: E402
import scrap_fornecedores as forn  # noqa: E402
import scrap_executor as scrap     # noqa: E402
import social_rotas as sr          # noqa: E402


def _fonte(rel):
    with open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


class T1UmRoteador(unittest.TestCase):
    """PLATAFORMA/CAPACIDADE -> ADAPTADOR tem exatamente um dono."""

    def test_o_dono_do_mapa_e_o_registo(self):
        reg.carregar_adaptadores()
        self.assertGreater(len(reg.registados()), 20)

    def test_o_roteador_nao_guarda_mapa_proprio_em_producao(self):
        # A costura de teste existe e TEM de estar vazia quando ninguem injeta.
        # E esta a diferenca entre uma costura e um segundo dono: o segundo dono
        # enche-se sozinho com o tempo e ninguem repara.
        self.assertEqual(sr.ADAPTADORES, {},
                         'o roteador voltou a ter tabela propria — segundo dono')

    def test_dois_adaptadores_para_a_mesma_capacidade_reprovam(self):
        reg.registar('X', 'x.media', adaptador='adaptador_x')  # idempotente
        with self.assertRaises(reg.RegistoDuplicado):
            reg.registar('X', 'x.media', adaptador='outro_qualquer')


class T2NaoMonolito(unittest.TestCase):
    """Adaptadores registados individualmente, e o roteador nao os conhece."""

    def test_cada_adaptador_e_um_modulo(self):
        reg.carregar_adaptadores()
        self.assertGreaterEqual(len(reg.adaptadores()), 5)
        for nome in reg.adaptadores():
            self.assertTrue(os.path.exists(os.path.join(RAIZ, 'coleta', nome + '.py')),
                            '%s nao e um modulo proprio' % nome)

    def test_o_roteador_nao_nomeia_plataformas(self):
        # O que se proibe nao e o condicional pequeno: e o roteador passar a
        # conter o conhecimento de todas as plataformas.
        fonte = _fonte('coleta/social_rotas.py')
        corpo = '\n'.join(l for l in fonte.split('\n') if not l.strip().startswith('#'))
        corpo = corpo.split('"""', 2)[-1]     # fora do docstring de topo
        for plat in ('INSTAGRAM', 'LINKEDIN', 'FACEBOOK', 'MASTODON', 'BLUESKY'):
            self.assertNotIn("'%s'" % plat, corpo,
                             'o roteador voltou a conhecer %s pelo nome' % plat)

    def test_acrescentar_plataforma_nao_toca_no_roteador(self):
        antes = _fonte('coleta/social_rotas.py')
        reg.registar('TELEGRAM', 'telegram.channel.incremental',
                     adaptador='adaptador_aberto')
        self.assertEqual(antes, _fonte('coleta/social_rotas.py'))


class T3UmDonoDeASR(unittest.TestCase):
    """Nenhuma implementacao executavel instancia motor fora do dono canonico."""

    DONO = 'ferramentas/fala_local.py'

    def _modulos_executaveis(self):
        for gaveta in _gavetas.GAVETAS:
            base = os.path.join(RAIZ, gaveta)
            if not os.path.isdir(base):
                continue
            for pasta, _d, ficheiros in os.walk(base):
                for f in ficheiros:
                    if f.endswith('.py'):
                        yield os.path.relpath(os.path.join(pasta, f), RAIZ)

    def test_so_um_ficheiro_abre_motor(self):
        donos = []
        for rel in self._modulos_executaveis():
            fonte = _fonte(rel)
            if 'WhisperModel(' in fonte or 'BatchedInferencePipeline(' in fonte:
                donos.append(rel)
        self.assertEqual(sorted(donos), [self.DONO],
                         'nasceu um segundo motor de ASR: %s' % donos)

    def test_nenhum_adaptador_abre_motor(self):
        reg.carregar_adaptadores()
        for nome in reg.adaptadores():
            fonte = _fonte(os.path.join('coleta', nome + '.py'))
            self.assertNotIn('WhisperModel(', fonte)
            self.assertNotIn('faster_whisper', fonte)

    def test_o_adaptador_nao_escolhe_modelo(self):
        # Ele pode PASSAR uma sugestao; nao pode DECIDIR. A decisao e do dono do
        # ASR, e fecha-se quando o hardware do runner local for medido.
        fonte = _fonte('coleta/adaptador_instagram.py')
        self.assertIn('model_hint', fonte)
        # So o CORPO. A prosa do topo explica os dois padroes que existem
        # hoje, e explicar nao e cravar.
        corpo = fonte.split('"""', 2)[-1]
        for literal in ("'small'", '"small"', "'medium'", '"medium"'):
            self.assertNotIn(literal, corpo,
                             'o adaptador cravou um modelo: %s' % literal)


class T4FallbackVisivel(unittest.TestCase):
    """Troca de fornecedor sem `WHY_FALLBACK` reprova. Nao avisa: recusa."""

    def test_troca_sem_motivo_reprova(self):
        mau = {'CAPABILITY': 'instagram.reel.capture',
               'PROVIDER_REQUESTED': forn.YTDLP, 'PROVIDER_USED': forn.EMBED,
               'WHY_FALLBACK': None, 'PROVIDER_STEPS': []}
        with self.assertRaises(forn.TraceIncompleto):
            forn.conferir(mau)

    def test_troca_com_motivo_passa_e_fica_legivel(self):
        p = forn.Percurso('instagram.reel.capture', pedido=forn.YTDLP)
        p.degrau(forn.YTDLP, 'MEDIA_DOWNLOAD_FAILED', 'HTTP 403 do CDN')
        p.degrau(forn.EMBED, 'MEDIA_OK', 'baixou 3257414 bytes')
        t = p.selar()
        self.assertTrue(forn.houve_fallback(t))
        self.assertEqual(t['PROVIDER_USED'], forn.EMBED)
        self.assertIn('403', t['WHY_FALLBACK'])

    def test_sem_troca_nao_exige_motivo(self):
        p = forn.Percurso('instagram.reel.capture', pedido=forn.YTDLP)
        p.degrau(forn.YTDLP, 'MEDIA_OK', 'baixou 5158474 bytes')
        t = p.selar()
        self.assertFalse(forn.houve_fallback(t))
        self.assertIsNone(t['WHY_FALLBACK'])

    def test_fornecedor_inventado_reprova(self):
        with self.assertRaises(forn.FornecedorDesconhecido):
            forn.Percurso('x', pedido='ferramenta_magica')

    def test_a_cadeia_de_reels_ja_produz_o_trace(self):
        # Os `degraus` que a cadeia grava desde que nasceu viram trace canonico
        # sem que ela precise de mudar uma linha.
        degraus = [{'PROVIDER': 'LOCAL_YTDLP', 'RESULT': 'MEDIA_OK',
                    'WHY': 'baixou 5158474 bytes'}]
        t = forn.de_degraus('instagram.reel.capture', degraus)
        self.assertEqual(t['PROVIDER_USED'], forn.YTDLP)


class T5AmbienteDeExecucao(unittest.TestCase):
    """A capacidade declara onde corre, e isso nao se deduz do fornecedor."""

    def test_todo_alvo_esta_no_vocabulario(self):
        for nome, v in cap.DECLARADAS.items():
            self.assertIn(v[2], cap.AMBIENTES, nome)

    def test_local_sem_porque_reprova(self):
        with self.assertRaises(cap.CapacidadeInvalida):
            cap.DECLARADAS['teste.local.sem.porque'] = (
                'TESTE', cap.PROVEN, cap.LOCAL, None, 'x', None)
            try:
                cap.conferir('teste.local.sem.porque')
            finally:
                del cap.DECLARADAS['teste.local.sem.porque']

    def test_gpu_nao_se_promete_em_maquina_nao_medida(self):
        self.assertEqual(cap.LOCAL_HARDWARE_STATUS, 'NOT_MEASURED')
        with self.assertRaises(cap.CapacidadeInvalida):
            cap.DECLARADAS['teste.gpu'] = ('TESTE', cap.PROVEN, cap.LOCAL,
                                           cap.GPU_REQUIRED, 'x', None)
            try:
                cap.conferir('teste.gpu')
            finally:
                del cap.DECLARADAS['teste.gpu']

    def test_mesmo_fornecedor_em_ambientes_diferentes(self):
        # `yt-dlp` traz metadados ONLINE e leva 403 nos bytes. Mesmo fornecedor,
        # capacidades diferentes, ambientes diferentes.
        self.assertEqual(cap.onde('youtube.video.metadata')[0], cap.ONLINE)
        self.assertEqual(cap.onde('youtube.media'), (cap.LOCAL, cap.DATACENTER_BLOCKED))

    def test_o_check_devolve_o_ambiente(self):
        v = scrap.CHECK('YOUTUBE', 'youtube.media')
        self.assertEqual(v['EXECUTION_TARGET'], cap.LOCAL)
        self.assertEqual(v['WHY_LOCAL'], cap.DATACENTER_BLOCKED)


class T6NaoSegundoCerebro(unittest.TestCase):
    """O SCRAP nao cria pedido, nao admite e nao substitui o orquestrador."""

    FICHEIROS = ('coleta/scrap_executor.py', 'coleta/scrap_registo.py',
                 'coleta/scrap_capacidades.py', 'coleta/scrap_fornecedores.py',
                 'coleta/social_rotas.py')

    def test_nao_fabrica_collection_request(self):
        for rel in self.FICHEIROS:
            fonte = _fonte(rel)
            corpo = fonte.split('"""', 2)[-1]
            self.assertNotIn('COLLECTION_REQUEST(', corpo, rel)
            self.assertNotIn('Pedido(', corpo, rel)

    def test_nao_decide_admissao(self):
        for rel in self.FICHEIROS:
            corpo = _fonte(rel).split('"""', 2)[-1]
            for proibido in ('def admitir', 'def julgar', 'ADMISSION ='):
                self.assertNotIn(proibido, corpo, '%s: %s' % (rel, proibido))

    def test_nao_importa_o_orquestrador(self):
        for rel in self.FICHEIROS:
            corpo = _fonte(rel).split('"""', 2)[-1]
            self.assertNotIn('import orquestrador', corpo, rel)

    def test_conhece_so_os_tres_escopos(self):
        self.assertEqual(scrap.ESCOPOS, ('PONTUAL', 'INCREMENTAL', 'TOTAL'))
        with self.assertRaises(ValueError):
            scrap.COLLECT(platform='YOUTUBE', capability='youtube.search',
                          run_id='R', scope='TUDO_O_QUE_HOUVER')

    def test_o_cursor_e_interno(self):
        st = scrap.STATE()
        self.assertTrue(st['CURSOR_SEMANTICS_ARE_INTERNAL'])
        self.assertEqual(st['SCOPES_KNOWN_BY_ORCHESTRATOR'], scrap.ESCOPOS)


class T7CapacidadeHonesta(unittest.TestCase):
    """BLOCKED e UNKNOWN nao viram sucesso porque existe adaptador."""

    def test_bloqueada_nao_promete(self):
        for nome in ('facebook.content', 'facebook.media', 'youtube.media'):
            self.assertFalse(cap.promete_resultado(nome), nome)
            self.assertFalse(scrap.CHECK(cap.plataforma(nome), nome)['CAN'], nome)

    def test_desconhecida_nao_promete(self):
        for nome in ('linkedin.history.discovery', 'x.discovery', 'linkedin.comments'):
            self.assertFalse(cap.promete_resultado(nome), nome)

    def test_coletar_bloqueada_devolve_estado_e_nao_sucesso(self):
        objetos, trace = scrap.COLLECT(platform='FACEBOOK',
                                       capability='facebook.content', run_id='R1')
        self.assertEqual(objetos, [])
        self.assertEqual(trace['RESULT'], scrap.SEM_PROMESSA)
        self.assertFalse(trace['CHECK']['CAN'])

    def test_capacidade_nao_declarada_nao_e_sucesso(self):
        v = scrap.CHECK('TIKTOK', 'tiktok.qualquer.coisa')
        self.assertFalse(v['CAN'])
        self.assertEqual(v['STATE'], scrap.NAO_DECLARADA)

    def test_registar_o_que_ninguem_mediu_reprova(self):
        with self.assertRaises(reg.CapacidadeNaoDeclarada):
            reg.registar('TIKTOK', 'tiktok.inventada', adaptador='qualquer')

    def test_todo_estado_cita_prova(self):
        for nome in cap.DECLARADAS:
            self.assertTrue(cap.prova(nome), '%s sem documento de prova' % nome)


class T8Reels(unittest.TestCase):
    """A cadeia ja provada continua a funcionar, e entra pelo adaptador."""

    def test_o_adaptador_alcanca_a_cadeia(self):
        self.assertIsNotNone(reg.executor_de('INSTAGRAM', 'instagram.reel.transcribe'))
        self.assertTrue(scrap.CHECK('INSTAGRAM', 'instagram.reel.transcribe')['CAN'])

    def test_a_cadeia_continua_a_ser_o_modulo_especializado(self):
        import reel_transcricao as rt
        self.assertEqual(rt.PIPELINE, 'REEL-TRANSCRICAO-V1')
        # a cadeia delega o reconhecimento; nao o faz
        self.assertNotIn('WhisperModel(', _fonte('ferramentas/reel_transcricao.py'))

    def test_identidade_continua_a_recusar_endereco_sem_publicacao(self):
        import reel_transcricao as rt
        self.assertEqual(rt.identidade_do_url('https://exemplo.tld/nada')['POST_ID'],
                         rt.NOT_KNOWN)

    def test_legenda_nao_e_transcricao(self):
        import comunicacao_classificar as cc
        fontes = dict(cc.FONTES_DE_TEXTO)
        self.assertIn('CAPTION', fontes)
        self.assertIn('TRANSCRIPT', fontes)
        self.assertNotEqual(fontes['CAPTION'], fontes['TRANSCRIPT'])


class T9Stories(unittest.TestCase):
    """Se a capacidade de Story for portada, vem sem motor proprio."""

    def test_a_capacidade_esta_declarada_com_o_estado_medido(self):
        self.assertEqual(cap.estado('instagram.story.capture'), cap.UNKNOWN)
        self.assertEqual(cap.estado('instagram.story.transcribe'), cap.NOT_EXECUTED)

    def test_nao_promete_resultado(self):
        self.assertFalse(cap.promete_resultado('instagram.story.capture'))
        self.assertFalse(cap.promete_resultado('instagram.story.transcribe'))

    def test_se_alguem_portar_o_terceiro_motor_o_T3_apanha(self):
        # Esta e a prova durable: o defeito nao esta no HEAD, e o teste que o
        # impediria de voltar esta. `test_so_um_ficheiro_abre_motor` reprova
        # qualquer ficheiro novo que instancie motor.
        self.assertFalse(os.path.exists(
            os.path.join(RAIZ, 'ferramentas', 'story_transcrever.py')),
            'o terceiro motor entrou: passar por fala_local antes de portar')


class T10Redacao(unittest.TestCase):
    """URL e DSN com segredo saem redigidas — e o resto sobrevive."""

    def test_senha_dentro_da_dsn_sai(self):
        import social_sessao as ss
        saida = ss.redigir('postgresql://utilizador:SenhaSecreta123@servidor:5432/base')
        self.assertNotIn('SenhaSecreta123', saida)
        self.assertIn('<REDIGIDO>', saida)

    def test_o_diagnostico_sobrevive_a_redacao(self):
        import social_sessao as ss
        saida = ss.redigir('postgres://u:MinhaSenha@servidor.interno:5432/basedados')
        for pedaco in ('postgres://', 'servidor.interno', 'basedados'):
            self.assertIn(pedaco, saida)

    def test_token_com_rotulo_e_com_forma_continuam_a_sair(self):
        import social_sessao as ss
        # O token falso e MONTADO, nunca escrito. Escreve-lo por extenso faz
        # este ficheiro cair no varredor de segredos da casa — e o varredor
        # tem razao: ele nao sabe, nem deve saber, que este e de mentira.
        falso = 'apify' + '_api_' + 'ABCDEFGHIJ0123456789'
        self.assertNotIn(falso, ss.redigir('?token=' + falso))

    def test_texto_sem_segredo_nao_e_estragado(self):
        import social_sessao as ss
        for limpo in ('https://exemplo.tld/a?b=1', 'nada de especial', 'HTTP 403'):
            self.assertEqual(ss.redigir(limpo), limpo)

    def test_o_vazamento_vivo_continua_NOT_REPRODUCED(self):
        # O que esta corrigido e o GUARDA. Dizer que se corrigiu um vazamento
        # que nunca foi reproduzido seria afirmar prova que nao existe.
        self.assertIn('LIVE_PASSWORD_LEAK = NOT_REPRODUCED',
                      _fonte('guarda/social_sessao.py'))


class T11ImportDeterministico(unittest.TestCase):
    """Nenhum comportamento depende da ordem em que `_gavetas` poe o caminho."""

    def _nomes_curtos(self):
        nomes = collections.defaultdict(list)
        for g in _gavetas.GAVETAS:
            base = os.path.join(RAIZ, g)
            if not os.path.isdir(base):
                continue
            pastas = [base] + [os.path.join(base, s) for s in sorted(os.listdir(base))
                               if os.path.isdir(os.path.join(base, s))
                               and not s.startswith(('_', '.'))]
            for p in pastas:
                for f in sorted(os.listdir(p)):
                    if f.endswith('.py') and not f.startswith('_'):
                        nomes[f[:-3]].append(os.path.relpath(os.path.join(p, f), RAIZ))
        return nomes

    def test_zero_colisoes_de_nome_curto(self):
        colisoes = {k: v for k, v in self._nomes_curtos().items() if len(v) > 1}
        self.assertEqual(colisoes, {},
                         'nome curto em duas gavetas: quem ganha depende da '
                         'ordem do sys.path, e isso nao e um comportamento')

    def test_os_modulos_novos_nao_colidem(self):
        nomes = self._nomes_curtos()
        for novo in ('scrap_capacidades', 'scrap_registo', 'scrap_fornecedores',
                     'scrap_executor', 'scrap_http', 'adaptador_instagram',
                     'adaptador_linkedin', 'adaptador_youtube', 'adaptador_x',
                     'adaptador_facebook', 'adaptador_aberto'):
            self.assertEqual(len(nomes.get(novo, [])), 1, novo)

    def test_todo_ficheiro_novo_compila(self):
        for rel in ('coleta/scrap_capacidades.py', 'coleta/scrap_registo.py',
                    'coleta/scrap_fornecedores.py', 'coleta/scrap_executor.py',
                    'coleta/scrap_http.py', 'coleta/social_rotas.py'):
            ast.parse(_fonte(rel))


class T12NadaVerdeQuebrouEmSilencio(unittest.TestCase):
    """A superficie que o codigo vivo usava continua a atender."""

    def test_o_roteador_mantem_a_porta_antiga(self):
        for nome in ('executar', 'selar', 'permitido', 'ADAPTADORES',
                     'RotaNaoPermitida', 'RotaBloqueada', '_get', 'AGENTE'):
            self.assertTrue(hasattr(sr, nome), 'social_rotas perdeu %s' % nome)

    def test_o_portao_continua_a_ser_o_mesmo(self):
        import scrap_http as http
        self.assertIs(sr.permitido, http.permitido)
        self.assertEqual(sr.AGENTE, http.AGENTE)

    def test_o_dono_do_estado_da_api_e_unico(self):
        import scrap_http as http
        import adaptador_youtube as ay
        self.assertIs(sr._EstadoDaApi, http.EstadoDaApi)
        self.assertIs(ay._EstadoDaApi, http.EstadoDaApi)

    def test_a_traducao_ausente_nunca_copia_o_original(self):
        saida = scrap.OUTPUT()
        self.assertEqual(saida['TRANSLATION'], 'NOT_RUN')
        self.assertIn('CAPTION', saida['TEXT_KINDS'])
        self.assertIn('TRANSCRIPT', saida['TEXT_KINDS'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
