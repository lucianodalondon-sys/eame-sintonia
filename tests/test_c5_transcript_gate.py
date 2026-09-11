#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DA C5 — funcionar não é poder, e tradução não é transcrição.

A pergunta desta missão era se existe HOJE uma rota de produção que traga a
legenda de um vídeo de terceiro. A resposta foi não, e estas provas existem para
que o «não» não seja reaberto por conveniência, e para que o que ficou no lugar
não continue a mentir sobre o que entrega.

    TECHNICAL != POLICY != AUTHORIZATION.

Três eixos. Uma rota que passa no primeiro e falha nos outros dois continua
fora — e a maior parte destas provas existe para impedir que alguém os funda.
"""
import ast
import glob
import io
import json
import os
import re
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, 'coleta'), os.path.join(RAIZ, 'leis'),
          os.path.join(RAIZ, 'regras'), os.path.join(RAIZ, 'ferramentas')):
    sys.path.insert(0, p)
import _gavetas          # noqa: E402,F401
import social_matriz as mz   # noqa: E402

#: Os dois Actors de legenda. A C5 NÃO retira nenhum.
ATORES_DE_LEGENDA = ('pintostudio~youtube-transcript-scraper',
                     'starvibe~youtube-video-transcript')

#: As rotas de legenda do YouTube que nenhuma missão pode promover sem prova nova.
FORA_DE_PRODUCAO = ('timedtext', 'yt-dlp')


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _rotas(capacidade, plataforma='YOUTUBE'):
    return (mz.MATRIZ.get(plataforma) or {}).get(capacidade) or []


# ══════════════════════════════════════════════════════════════════════════
class T1NenhumaRotaProibidaViraPadrao(unittest.TestCase):
    """T1 · uma rota `PERMITIDA=NAO` não pode ser a escolhida por omissão."""

    def test_a_rota_padrao_de_legenda_nunca_e_uma_proibida(self):
        escolhida = mz._rota_padrao(_rotas('FETCH_TRANSCRIPT'))
        if escolhida is not None:
            self.assertNotEqual(escolhida['PERMITIDA'], 'NAO',
                                'a rota padrao de legenda esta proibida: %s'
                                % escolhida['ROTA'])

    def test_timedtext_e_ytdlp_continuam_fora(self):
        for cap in ('FETCH_TRANSCRIPT', 'FETCH_VIDEO_METADATA', 'SEARCH_KEYWORD'):
            for r in _rotas(cap):
                if any(n in r['ROTA'] for n in FORA_DE_PRODUCAO):
                    self.assertEqual(r['PERMITIDA'], 'NAO',
                                     '%s foi promovida em %s' % (r['ROTA'], cap))

    def test_nenhum_estado_fora_do_vocabulario(self):
        """A trava que faltava: a C5 escreveu dois estados novos e NADA reprovou.

        `ESTADOS` era uma tupla fechada sem quem a fizesse valer. Uma lista
        fechada que ninguem confere e uma lista aberta com outro nome.
        """
        fora = []
        for plat, caps in mz.MATRIZ.items():
            for cap, rotas in caps.items():
                if cap.startswith('_'):
                    continue
                for r in rotas:
                    if r['ESTADO'] not in mz.ESTADOS:
                        fora.append('%s/%s/%s=%s' % (plat, cap, r['ROTA'], r['ESTADO']))
        self.assertEqual(fora, [], 'estado fora do vocabulario: %s' % fora)


# ══════════════════════════════════════════════════════════════════════════
class T2e3ChaveNaoEPermissaoDeDono(unittest.TestCase):
    """T2 · T3 · RT2 — `captions.download` de terceiro não fica disponível sozinho."""

    def test_captions_download_declara_que_precisa_do_dono(self):
        alvo = [r for r in _rotas('FETCH_TRANSCRIPT')
                if 'captions.download' in r['ROTA']]
        self.assertTrue(alvo, 'a rota oficial de legenda sumiu da matriz')
        r = alvo[0]
        self.assertEqual(r['PERMITIDA'], 'NAO')
        self.assertEqual(r['ESTADO'], 'REQUIRES_OWNER_PERMISSION',
                         'permissao do dono virou «eu escolhi nao» — sao coisas '
                         'diferentes, e a diferenca e quem tem a chave da porta')
        self.assertIn('permission to edit', r['NOTA'],
                      'a nota perdeu a frase literal da documentacao')

    def test_captions_list_pede_credencial_mais_forte_e_nao_e_a_mesma_pergunta(self):
        alvo = [r for r in _rotas('FETCH_TRANSCRIPT') if 'captions.list' in r['ROTA']]
        self.assertTrue(alvo, 'listar e baixar sao perguntas diferentes e a matriz '
                              'so tinha uma linha')
        r = alvo[0]
        self.assertEqual(r['ESTADO'], 'REQUIRES_AUTHORIZATION')
        self.assertNotEqual(r['ESTADO'], 'REQUIRES_OWNER_PERMISSION',
                            'OAuth em falta nao e permissao de dono em falta')

    def test_a_chave_de_api_nao_e_apresentada_como_oauth(self):
        """RT: `YOUTUBE_DATA_API_KEY` resolve o publico, e so o publico."""
        t = _fonte('coleta/youtube_oficial.py')
        self.assertNotIn('oauth', t.lower(),
                         'o modulo da API oficial passou a falar de OAuth sem que '
                         'nenhuma missao o tenha provado')

    def test_os_dois_estados_nao_sao_sinonimos(self):
        self.assertIn('REQUIRES_OWNER_PERMISSION', mz.ESTADOS)
        self.assertIn('REQUIRES_AUTHORIZATION', mz.ESTADOS)
        self.assertIn('ROUTE_NOT_ALLOWED', mz.ESTADOS)
        self.assertEqual(len({'REQUIRES_OWNER_PERMISSION', 'REQUIRES_AUTHORIZATION',
                              'ROUTE_NOT_ALLOWED'}), 3)


# ══════════════════════════════════════════════════════════════════════════
class T4TresEixosNaoSeFundem(unittest.TestCase):
    """T4 · RT1 · RT3 · RT4 — técnico, política e autorização são três colunas."""

    def test_a_nota_do_timedtext_cita_a_autoridade_certa(self):
        """RT3 · a `baseUrl` real cai em `Disallow: /api/`, não em `/timedtext_video`."""
        r = [x for x in _rotas('FETCH_TRANSCRIPT') if x['ROTA'] == 'timedtext'][0]
        self.assertIn('/api/', r['NOTA'],
                      'a nota voltou a citar o Disallow errado')
        self.assertIn('t/terms', str(r['EVIDENCIA']),
                      'a nota nao cita os Termos, que sao a autoridade acima do robots')

    def test_funcionar_nao_promove(self):
        """RT4 · a matriz guarda rotas que FUNCIONAM e continuam proibidas."""
        proibidas_que_funcionam = [
            r for cap in mz.MATRIZ['YOUTUBE']
            if not cap.startswith('_')
            for r in _rotas(cap)
            if r['PERMITIDA'] == 'NAO' and 'zero' in str(r['CUSTO'])]
        self.assertTrue(proibidas_que_funcionam,
                        'a matriz deixou de registar rota tecnicamente viavel e '
                        'proibida — e e exatamente essa que precisa de registo')

    def test_navegador_local_nao_aparece_como_autorizacao(self):
        """RT3 · «roda no Chrome real» não é o mesmo que «rota autorizada»."""
        for cap in ('FETCH_TRANSCRIPT',):
            for r in _rotas(cap):
                nota = str(r['NOTA']).lower()
                if 'navegador' in nota or 'chrome' in nota:
                    self.assertNotEqual(
                        r['PERMITIDA'], 'SIM',
                        '%s foi autorizada por causa do navegador' % r['ROTA'])


# ══════════════════════════════════════════════════════════════════════════
class T5e6OAdapterContinuaDono(unittest.TestCase):
    """T5 · T6 — a semântica do YouTube é do adapter; ninguém salta para o provider."""

    def test_so_o_adaptador_conhece_as_rotas_do_youtube(self):
        t = _fonte('coleta/adaptador_youtube.py')
        self.assertIn('PLATAFORMA = ', t)
        self.assertIn("'YOUTUBE'", t)

    def test_o_sensor_nao_chama_provider_direto(self):
        """O caller pede CAPACIDADE. Quem escolhe rota é a cadeia canônica.

        ⚠️ Correção a mim próprio: a primeira versão procurava o texto cru e
        reprovava o COMENTÁRIO que explica por que o ator fica. Um comentário que
        cita uma rota não chama rota nenhuma.

            UMA SENTINELA QUE LÊ TEXTO REPROVA A EXPLICAÇÃO JUNTO COM O DEFEITO.

        Agora lê a árvore: importações e literais que EXECUTAM. Comentários não
        viram nós, e por isso saem sozinhos da conta.
        """
        arvore = ast.parse(_fonte('regras/sensor_coleta.py'))
        maus = []
        for no in ast.walk(arvore):
            if isinstance(no, (ast.Import, ast.ImportFrom)):
                nome = getattr(no, 'module', '') or ''
                nomes = [a.name for a in (no.names or [])] + [nome]
                for x in nomes:
                    if any(m in str(x) for m in ('yt_dlp', 'youtube_dl')):
                        maus.append('import %s:%d' % (x, no.lineno))
            if isinstance(no, ast.Constant) and isinstance(no.value, str):
                for m in ('timedtext', 'captions.download', 'ytInitialPlayerResponse'):
                    if m in no.value:
                        maus.append('literal %r:%d' % (m, no.lineno))
        self.assertEqual(maus, [], 'o sensor passou a nomear rota de provider: %s' % maus)

    def test_o_roteador_continua_sem_conhecer_plataformas(self):
        arvore = ast.parse(_fonte('coleta/social_rotas.py'))
        nomes = [n.value for n in ast.walk(arvore)
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        for p in ('YOUTUBE', 'INSTAGRAM', 'LINKEDIN'):
            self.assertNotIn(p, nomes,
                             'o roteador voltou a conhecer o nome %s' % p)


# ══════════════════════════════════════════════════════════════════════════
class T7OAtorNaoSomeSemSubstituto(unittest.TestCase):
    """T7 · RT6 — o Actor falha 43% das corridas, e mesmo assim fica."""

    def test_os_dois_atores_continuam_declarados(self):
        t = _fonte('regras/sensor_coleta.py')
        for a in ATORES_DE_LEGENDA:
            self.assertIn(a, t, 'o ator %s foi retirado — e nao ha substituto' % a)

    def test_a_rota_paga_continua_a_unica_condicional(self):
        cond = [r for r in _rotas('FETCH_TRANSCRIPT') if r['PERMITIDA'] == 'CONDICIONAL']
        self.assertEqual(len(cond), 1,
                         'a escada de legenda deixou de ter exatamente uma rota '
                         'condicional — ou perdeu a unica, ou ganhou uma sem prova')
        self.assertIn('apify', cond[0]['ROTA'])

    def test_ator_que_falha_nao_prova_ausencia_de_capacidade(self):
        """RT6 · 19 corridas FAILED não dizem «não existe legenda neste vídeo»."""
        t = _fonte('regras/sensor_coleta.py')
        self.assertIn('REQUESTED_EMPTY', t,
                      'o estado que separa «pedi e veio vazio» de «nao ha» sumiu')


# ══════════════════════════════════════════════════════════════════════════
class T8TraducaoNaoETranscricao(unittest.TestCase):
    """T8 · RT7 · RT8 — três espécies de texto, e o campo diz qual é.

    Medido na C5: onze dos 28 textos preservados são INGLÊS vindo de vídeo
    NÃO-inglês. O vídeo `RisRARQSFAg` — canal AIPO Verona, título «Periodico
    olivo 1° Maggio 2026» — guardou «Olive growers, welcome back to issue 18».

        ISSO NÃO É A FALA DO VÍDEO. É UMA TRADUÇÃO DELA.
    """

    def test_o_vocabulario_das_especies_e_fechado(self):
        import sensor_coleta as sc                              # noqa: PLC0415
        self.assertEqual(len(sc.ESPECIES_DE_TEXTO), 4)
        self.assertIn(sc.NATIVE_CAPTION_ORIGINAL, sc.ESPECIES_DE_TEXTO)
        self.assertIn(sc.NATIVE_CAPTION_TRANSLATED, sc.ESPECIES_DE_TEXTO)
        self.assertIn(sc.ASR_LOCAL, sc.ESPECIES_DE_TEXTO)

    def test_original_e_traduzida_nao_sao_a_mesma_especie(self):
        import sensor_coleta as sc                              # noqa: PLC0415
        self.assertNotEqual(sc.NATIVE_CAPTION_ORIGINAL, sc.NATIVE_CAPTION_TRANSLATED)
        self.assertNotEqual(sc.NATIVE_CAPTION_ORIGINAL, sc.ASR_LOCAL)

    def test_provedor_calado_devolve_NAO_SEI_e_nao_um_palpite(self):
        import sensor_coleta as sc                              # noqa: PLC0415
        self.assertEqual(sc.especie_do_texto({'text': 'qualquer coisa'}), sc.pv.NAO_SEI)
        self.assertEqual(sc.especie_do_texto({}), sc.pv.NAO_SEI)
        self.assertEqual(sc.especie_do_texto(None), sc.pv.NAO_SEI)

    def test_a_especie_nao_e_inferida_do_conteudo(self):
        """Ler o texto para adivinhar a espécie seria adivinhar duas vezes."""
        import sensor_coleta as sc                              # noqa: PLC0415
        i = _fonte('regras/sensor_coleta.py').index('def especie_do_texto')
        corpo = _fonte('regras/sensor_coleta.py')[i:i + 900]
        for mau in ('.lower()', 'langdetect', 're.search', 'detect'):
            self.assertNotIn(mau, corpo,
                             'a especie passou a ser adivinhada a partir do texto')
        self.assertEqual(sc.especie_do_texto({'trackKind': 'asr'}),
                         sc.NATIVE_CAPTION_ORIGINAL)
        self.assertEqual(sc.especie_do_texto({'isTranslated': True}),
                         sc.NATIVE_CAPTION_TRANSLATED)

    def test_a_especie_devolvida_esta_sempre_no_vocabulario(self):
        import sensor_coleta as sc                              # noqa: PLC0415
        for entrada in ({}, {'trackKind': 'asr'}, {'isTranslated': True},
                        {'translatedFrom': 'it'}, {'kind': 'asr'}):
            self.assertIn(sc.especie_do_texto(entrada), sc.ESPECIES_DE_TEXTO)

    def test_lingua_declarada_pelo_provedor_e_lingua_ausente_tem_nomes_diferentes(self):
        t = _fonte('regras/sensor_coleta.py')
        self.assertIn('DECLARED_BY_PROVIDER', t)
        self.assertIn('NOT_DECLARED_BY_PROVIDER', t,
                      '«o provedor nao disse» virou indistinguivel de «nao sei»')

    def test_o_corpus_preservado_continua_a_provar_o_defeito(self):
        """A prova viva: o artefato real ainda tem o caso italiano dentro.

        Se um dia alguém reescrever o corpus, esta prova avisa — e reescrever o
        histórico para esconder o defeito seria pior do que o defeito.
        """
        achou = None
        for f in glob.glob(os.path.join(RAIZ, 'data', 'samples', 'SENSOR-PILOT',
                                        'TRANSCRICOES-*.json')):
            with io.open(f, encoding='utf-8') as fh:
                for i in json.load(fh).get('ITEMS') or []:
                    if 'RisRARQSFAg' in str(i.get('SOURCE_URL') or ''):
                        achou = i
        if achou is None:
            self.skipTest('o caso italiano nao esta neste ambiente')
        self.assertTrue(achou.get('TRANSCRIPT'))
        self.assertIn('Olive growers', achou['TRANSCRIPT'][:120],
                      'o texto preservado mudou — e ele e a prova do defeito')
        self.assertEqual(achou.get('TRANSCRIPT_LANGUAGE'), 'NÃO SEI',
                         'o ator passou a declarar lingua sem que ninguem o medisse')


# ══════════════════════════════════════════════════════════════════════════
class T9RawDeTesteVaiParaTemp(unittest.TestCase):
    """T9 — lei da casa desde a C2."""

    def test_a_suite_nao_deixou_nada_no_acervo(self):
        r = subprocess.run(['git', 'status', '--short'], cwd=RAIZ,
                           capture_output=True, text=True)
        sujos = [ln for ln in r.stdout.splitlines()
                 if ln.startswith('??') and ('data/samples' in ln or 'data/raw' in ln)]
        self.assertEqual(sujos, [], 'teste deixou lixo no acervo: %s' % sujos)

    def test_esta_prova_nao_adquire_nada(self):
        """A C5 não toca na rede — e a prova disso não podia ser um `grep` em si mesma.

        ⚠️ Correção a mim próprio: a primeira versão procurava `urllib.request`
        no próprio ficheiro, e encontrava-o — na lista do que procurava.

            UMA SENTINELA QUE SE LÊ A SI PRÓPRIA ENCONTRA-SE SEMPRE.

        A pergunta certa é sobre IMPORTAÇÕES, e essas estão na árvore.
        """
        arvore = ast.parse(_fonte('tests/test_c5_transcript_gate.py'))
        importados = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                importados.update(a.name.split('.')[0] for a in no.names)
            elif isinstance(no, ast.ImportFrom):
                importados.add((no.module or '').split('.')[0])
        for mau in ('urllib', 'requests', 'yt_dlp', 'http', 'socket'):
            self.assertNotIn(mau, importados,
                             'a prova da C5 importa %r — ela nao toca na rede' % mau)


# ══════════════════════════════════════════════════════════════════════════
class T10AsMissoesAnterioresNaoRegrediram(unittest.TestCase):
    """T10 — C1 a C4 continuam de pé."""

    def test_c3_as_quatro_capacidades_continuam_oficiais(self):
        for cap, rota in (('SEARCH_KEYWORD', 'search.list'),
                          ('INCREMENTAL', 'playlistItems.list'),
                          ('FETCH_VIDEO_METADATA', 'videos.list'),
                          ('FETCH_COMMENTS', 'commentThreads.list')):
            padrao = mz._rota_padrao(_rotas(cap))
            self.assertIsNotNone(padrao, 'a capacidade %s ficou sem rota' % cap)
            self.assertIn(rota, padrao['ROTA'],
                          '%s deixou de sair pela API oficial' % cap)
            self.assertEqual(padrao['PERMITIDA'], 'SIM')

    def test_c3_os_dois_atores_aposentados_continuam_sem_caller(self):
        for a in ('streamers~youtube-scraper', 'streamers~youtube-comments-scraper'):
            for rel in ('regras/sensor_coleta.py', 'coleta/comunicacao_coleta.py'):
                self.assertNotIn(a, _fonte(rel),
                                 'o ator aposentado %s voltou a %s' % (a, rel))

    def test_c4_o_dono_do_asr_continua_unico_e_com_padrao_cpu(self):
        import fala_local as fl                                 # noqa: PLC0415
        if not os.environ.get('SINTONIA_ASR_DEVICE'):
            self.assertEqual(fl.DISPOSITIVO_PADRAO, fl.CPU)
        self.assertEqual(fl.modelo_de('reel'), 'medium')
        self.assertEqual(fl.modelo_de('youtube'), 'small')

    def test_c4_a_c5_nao_ligou_a_gpu_nem_mudou_modelo(self):
        t = _fonte('regras/sensor_coleta.py')
        for mau in ('cuda', 'device=', 'compute_type=', 'large-v3'):
            self.assertNotIn(mau, t,
                             'a C5 mexeu no ferro do reconhecedor (%r)' % mau)


# ══════════════════════════════════════════════════════════════════════════
class T11MidiaEAsrSaoDoisConceitos(unittest.TestCase):
    """§14 · RT: `CAN_TRANSCRIBE_AUDIO` != `CAN_ACQUIRE_YOUTUBE_AUDIO`."""

    def test_a_capacidade_de_midia_do_youtube_continua_bloqueada(self):
        import scrap_capacidades as cap                         # noqa: PLC0415
        d = cap.DECLARADAS['youtube.media']
        self.assertEqual(d[1], 'BLOCKED',
                         'a midia do YouTube foi promovida — e a C5 so podia censar')

    def test_o_reconhecedor_nao_aprendeu_a_adquirir(self):
        t = _fonte('ferramentas/fala_local.py')
        for mau in ('yt_dlp', 'yt-dlp', 'urllib.request', 'youtube.com'):
            self.assertNotIn(mau, t,
                             'o dono do ASR passou a buscar midia — sao duas missoes')


if __name__ == '__main__':
    unittest.main(verbosity=2)
