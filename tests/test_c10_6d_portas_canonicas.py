#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.6D — AS PORTAS OPERACIONAIS ENTRAM PELA CASA CERTA.

A C10.6C mediu o boundary comum e encontrou portas que o contornavam. A C10.6D
censou-as estruturalmente e mediu a coisa que decide tudo:

    NENHUMA das seis implementações que os workflows corriam direto importa
    `leis/social_matriz.py`.

    UMA DECISÃO QUE UMA PORTA NÃO CONHECE NÃO É UMA DECISÃO. É UM DESEJO.

E mediu a segunda, que é a que dói:

    `yt-legendas` corria `_timedtext`, e a matriz declara essa rota
    `ROUTE_NOT_ALLOWED` desde a C5 — por ToS, por `Disallow: /api/` e pelas
    Developer Policies.

        UMA ROTA QUE FUNCIONA NÃO É UMA ROTA PERMITIDA.

O QUE NÃO SE FEZ, E É METADE DO TRABALHO
------------------------------------------
Não se fabricou Collection para o número de bypasses baixar. `yt-relevancia`
pergunta «vale a pena esta fonte?» — é JULGAMENTO, e registá-la como capacidade
de aquisição poria juízo temático dentro da coleta.

    COLETAR != ADMITIR != JULGAR.
"""
import ast
import io
import os
import re
import sys
import unittest

import yaml

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import social_matriz as mz        # noqa: E402
import scrap_registo as reg       # noqa: E402
import social_scrap as ss         # noqa: E402

reg.carregar_adaptadores()

WF = '.github/workflows/sintonia-scrap.yml'

#: As implementações que nenhuma fase de Collection pode chamar direto.
IMPLEMENTACOES = ('instagram_janela.py', 'instagram_diario.py',
                  'youtube_janela.py', 'youtube_transcrever.py',
                  'instagram_transcrever.py', 'reel_transcricao.py',
                  'youtube_oficial.py')
CANONICAS = ('janela', 'janela-perfis', 'janela-objetos')
BLOQUEADAS = ('diario', 'yt-canais', 'yt-objetos', 'yt-legendas', 'yt-alvos',
              'yt-transcrever', 'bio', 'posts', 'reels', 'comentarios')
#: Fases que NÃO são Collection e que por isso continuam com CLI própria.
FORA_DA_COLLECTION = ('diario-fila', 'diario-noticia', 'portao-pessoal',
                      'yt-relevancia', 'yt-calibrar', 'contratos', 'plano',
                      'semaforo', 'liquidar')


def _fonte(rel):
    return io.open(os.path.join(RAIZ, rel), encoding='utf-8').read()


def _por_fase():
    """O comando de cada fase, lido do `case` do YAML. Parseado, nunca grep."""
    doc = yaml.safe_load(_fonte(WF))
    runs = []

    def varre(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == 'run' and isinstance(v, str):
                    runs.append(v)
                varre(v)
        elif isinstance(o, list):
            for v in o:
                varre(v)
    varre(doc)
    fora, fase = {}, None
    for bloco in runs:
        if 'case "${{ inputs.fase }}"' not in bloco:
            continue
        for linha in bloco.splitlines():
            nu = linha.strip()
            if not nu or nu.startswith('#'):
                continue
            m = re.match(r'([\w|*-]+)\)\s*(.*)$', nu)
            if m:
                fase, resto = m.group(1), m.group(2)
                for f in fase.split('|'):
                    fora.setdefault(f, [])
                    if resto:
                        fora[f].append(resto)
                continue
            if fase:
                for f in fase.split('|'):
                    fora.setdefault(f, []).append(nu)
    return fora


class NenhumaFaseDeCollectionChamaImplementacao(unittest.TestCase):

    def test_1_as_fases_canonicas_entram_pela_entrada_canonica(self):
        por = _por_fase()
        for f in CANONICAS:
            with self.subTest(fase=f):
                cmds = ' '.join(por.get(f) or [])
                self.assertIn('social_scrap.py', cmds,
                              '%s deixou de entrar pela entrada canônica' % f)
                self.assertIn('coletar', cmds)
                for i in IMPLEMENTACOES:
                    self.assertNotIn(i, cmds,
                                     '%s voltou a correr %s direto' % (f, i))

    def test_2_as_fases_sem_rota_canonica_recusam(self):
        por = _por_fase()
        for f in BLOQUEADAS:
            with self.subTest(fase=f):
                cmds = ' '.join(por.get(f) or [])
                self.assertIn('recusar', cmds, '%s deixou de recusar' % f)
                for i in IMPLEMENTACOES:
                    self.assertNotIn(i, cmds,
                                     '%s voltou a correr %s' % (f, i))

    def test_3_nenhuma_fase_cai_num_ramo_que_ninguem_reclama(self):
        """O ramo `*)` mandava fase não nomeada para um orquestrador com fases pagas."""
        doc = yaml.safe_load(_fonte(WF))
        opcoes = ((doc.get('on') or doc.get(True))['workflow_dispatch']
                  ['inputs']['fase']['options'])
        por = _por_fase()
        orfas = [o for o in opcoes if o not in por]
        self.assertEqual(orfas, [],
                         'fases sem ramo próprio caem no `*`: %s' % orfas)
        self.assertTrue(opcoes, 'a sonda nao leu opcao nenhuma')

    def test_4_o_ramo_de_omissao_nao_corre_nada(self):
        por = _por_fase()
        cmds = ' '.join(por.get('*') or [])
        self.assertTrue(cmds, 'o ramo de omissao sumiu; uma fase nova cairia no vazio')
        for i in IMPLEMENTACOES + ('instagram_coleta.py',):
            self.assertNotIn(i, cmds, 'o ramo de omissao voltou a correr %s' % i)
        self.assertIn('exit 2', cmds, 'o ramo de omissao deixou de recusar alto')


class NaoSeFabricaCollection(unittest.TestCase):

    def test_5_julgamento_nao_virou_capacidade_de_aquisicao(self):
        """`yt-relevancia` pergunta «vale a pena esta fonte?». Isso não é coleta."""
        self.assertNotIn('yt-relevancia', ss.FASES_CANONICAS)
        self.assertNotIn('yt-calibrar', ss.FASES_CANONICAS)
        # e nenhuma capacidade registada aponta para o ficheiro do julgamento
        for (_p, _c), r in reg.registados().items():
            fn = r['EXECUTA'] or r['ROTA']
            self.assertNotIn('youtube_relevancia', getattr(fn, '__module__', '') or '',
                             'o julgamento entrou no registo do SCRAP')

    def test_6_so_fase_com_rota_canonica_esta_na_tabela(self):
        for fase, (plat, capac, _fix) in ss.FASES_CANONICAS.items():
            with self.subTest(fase=fase):
                r = reg.adaptador_de(plat, capac)
                self.assertIsNotNone(r, '%s aponta para capacidade inexistente' % fase)
                self.assertTrue(r['EXECUTA'] or r['ROTA'],
                                '%s aponta para capacidade SEM rota' % fase)

    def test_7_as_fases_que_nao_sao_collection_continuam_com_cli_propria(self):
        """Não se empurra ferramenta para dentro do COLLECT só pela métrica."""
        por = _por_fase()
        for f in FORA_DA_COLLECTION:
            with self.subTest(fase=f):
                cmds = ' '.join(por.get(f) or [])
                self.assertTrue(cmds, '%s perdeu o seu ramo' % f)
                self.assertNotIn('social_scrap.py coletar', cmds,
                                 '%s foi fabricada como Collection' % f)


class AFasePEDIDAEAFaseCORRIDA(unittest.TestCase):
    """M12 — uma CLI que reescreve o pedido em silencio e outra coisa.

    `coletar('janela-perfis')` tem de pedir a camada `perfis`. Trocar a camada
    por dentro faria o operador pedir uma coisa e a casa fazer outra, com o
    rasto a registar a que ela fez.

        UM PEDIDO REESCRITO EM SILENCIO E UM PEDIDO QUE NINGUEM FEZ.
    """

    def test_15_cada_fase_pede_exactamente_o_que_o_nome_dela_diz(self):
        pedidos = []

        def espia(*, platform, capability, run_id, banco=None, **kw):
            pedidos.append((platform, capability, kw))
            return [], {'RESULT': 'OK'}

        import scrap_executor as sx
        original = sx.COLLECT
        sx.COLLECT = espia
        try:
            for fase, (plat, capac, fixos) in sorted(ss.FASES_CANONICAS.items()):
                pedidos[:] = []
                ss.coletar(fase, banco=None)
                self.assertEqual(len(pedidos), 1,
                                 '%s nao fez exactamente um pedido' % fase)
                p_plat, p_cap, p_kw = pedidos[0]
                self.assertEqual(p_plat, plat)
                self.assertEqual(p_cap, capac)
                for chave, valor in fixos.items():
                    self.assertEqual(p_kw.get(chave), valor,
                                     '%s pediu %s=%r, e a tabela diz %r'
                                     % (fase, chave, p_kw.get(chave), valor))
        finally:
            sx.COLLECT = original

    def test_16_o_run_id_diz_a_fase_que_foi_pedida(self):
        vistos = []

        def espia(*, platform, capability, run_id, banco=None, **kw):
            vistos.append(run_id)
            return [], {'RESULT': 'OK'}

        import scrap_executor as sx
        original = sx.COLLECT
        sx.COLLECT = espia
        try:
            ss.coletar('janela-objetos', banco=None)
        finally:
            sx.COLLECT = original
        self.assertTrue(vistos)
        self.assertIn('janela-objetos', vistos[0],
                      'o `run_id` nao nomeia a fase pedida: %s' % vistos[0])


class CheckpointSoOndeHaUnidadeRetomavel(unittest.TestCase):
    """M10 — fabricar retomada onde nao ha metade feita tranca a porta."""

    def test_17_uma_unidade_so_existe_onde_ha_um_objecto_identificado(self):
        """O alvo tem de MUDAR quando o objecto muda.

        Esta e a lei que M10 quebra. Quem fabrica retomada para uma rota sem
        metade feita nao consegue formar um alvo por objecto — a janela le o
        LOTE CONGELADO inteiro, nao ha «o Reel X» ali — entao o alvo sai
        CONSTANTE. E um alvo constante e uma armadilha de sentido unico:

            UM ALVO QUE NAO MUDA COM O OBJECTO ACEITA UM `CONCLUIDO` SO,
            E DEPOIS RECUSA TUDO PARA SEMPRE.

        Um `CONCLUIDO` nesse alvo devolveria `JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES`
        a TODAS as corridas seguintes daquela capacidade, e a porta fechava-se
        sozinha sem nunca falhar — o pior modo de morrer que existe nesta casa.

        E NAO se exige aqui uma unidade por capacidade. `instagram.reel.capture`,
        `instagram.reel.audio` e `instagram.reel.transcribe` declaram a MESMA
        unidade porque sao TRES PEDIDOS SOBRE O MESMO REEL — isso e desenho da
        C10.6C, escrito no commit dela, e nao um emprestimo. O que se mede e
        outra coisa: que a unidade nomeie ESTA casa (`PLATFORM`), um acto que a
        POLITICA conhece (`CAPABILITY` na matriz da plataforma) e UM OBJECTO
        (`EXTERNAL_ID` que anda com o pedido).
        """
        for (plat, capac), r in reg.registados().items():
            decl = r.get('UNIDADE')
            if decl is None:
                continue
            with self.subTest(capacidade=capac):
                a1, e1, campos = decl(ident={'PLATFORM': plat, 'POST_ID': 'AAA'})
                a2, e2, _c = decl(ident={'PLATFORM': plat, 'POST_ID': 'BBB'})
                self.assertNotEqual(
                    a1, a2,
                    '%s declara uma unidade de alvo CONSTANTE (%r). Um '
                    '`CONCLUIDO` ali tranca a capacidade inteira para sempre.'
                    % (capac, a1))
                self.assertEqual(e1.get('EXTERNAL_ID'), 'AAA',
                                 '%s nao leva o objecto na entrada' % capac)
                self.assertNotEqual(e1.get('EXTERNAL_ID'), e2.get('EXTERNAL_ID'))
                self.assertEqual(e1.get('PLATFORM'), plat,
                                 '%s declara unidade de outra plataforma: %s'
                                 % (capac, e1.get('PLATFORM')))
                self.assertIn(
                    e1.get('CAPABILITY'), mz.MATRIZ.get(plat, {}),
                    '%s declara uma unidade cujo acto a POLITICA nao conhece '
                    'em %s: %s' % (capac, plat, e1.get('CAPABILITY')))
                for obrigatorio in ('PLATFORM', 'EXTERNAL_ID', 'CAPABILITY'):
                    self.assertIn(obrigatorio, campos,
                                  '%s nao poe %s na identidade do checkpoint'
                                  % (capac, obrigatorio))

    def test_18_a_janela_nao_tem_unidade_retomavel(self):
        """Ela le o LOTE CONGELADO inteiro a cada corrida. Nao ha metade feita."""
        r = reg.adaptador_de('INSTAGRAM', 'instagram.profile.discovery')
        self.assertIsNone(r.get('UNIDADE'),
                          'a janela ganhou checkpoint; ela nao tem unidade '
                          'retomavel e um CONCLUIDO trancava-a para sempre')


class APoliticaContinuaDona(unittest.TestCase):

    def test_8_a_rota_da_janela_e_a_que_a_matriz_nomeia(self):
        d = mz.decisao('INSTAGRAM', 'INCREMENTAL')
        self.assertEqual(d['DECISAO'], mz.PERMITIDA_SIM)
        self.assertEqual(d['ROTA'], 'instagram_janela.py:grade')
        self.assertEqual(d['CLASSE'], 'PUBLIC_BROWSER')
        r = reg.adaptador_de('INSTAGRAM', 'instagram.profile.discovery')
        self.assertIsNotNone(r['ROTA'],
                             'a capacidade que a matriz nomeia voltou a ficar sem rota')

    def test_9_timedtext_continua_proibida_e_ninguem_a_corre(self):
        rotas = mz.MATRIZ['YOUTUBE']['FETCH_TRANSCRIPT']
        tt = next(r for r in rotas if r['ROTA'] == 'timedtext')
        self.assertEqual(tt['PERMITIDA'], 'NAO')
        self.assertEqual(tt['ESTADO'], 'ROUTE_NOT_ALLOWED')
        por = _por_fase()
        self.assertNotIn('youtube_janela.py',
                         ' '.join(por.get('yt-legendas') or []),
                         'a fase que corre `timedtext` voltou ao workflow')

    def test_10_a_politica_nao_mudou_nesta_missao(self):
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')['DECISAO'],
                         mz.NAO_PERMITIDA)
        for cap in ('INCREMENTAL', 'FETCH_TRANSCRIPT'):
            self.assertIn(cap, mz.MATRIZ['YOUTUBE'])


class ACLIEFinaENaoUmMotor(unittest.TestCase):

    def test_11_a_cli_nao_sabe_nada_de_plataforma(self):
        arv = ast.parse(_fonte('coleta/social_scrap.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'coletar')
        texto = ast.dump(fn)
        for proibido in ('cdp', 'yt_dlp', 'urlopen', 'instagram_janela',
                         'youtube_janela', 'apify'):
            self.assertNotIn(proibido, texto,
                             'a CLI passou a conhecer a plataforma: %s' % proibido)
        self.assertIn('COLLECT', texto, 'a CLI deixou de chamar o executor')

    def test_12_o_workflow_nao_escolhe_ferramenta(self):
        t = _fonte(WF)
        for proibido in ('force_apify', 'force_browser', 'force_ytdlp',
                         'PROVIDER=', 'provider='):
            self.assertNotIn(proibido, t,
                             'o workflow passou a escolher ferramenta: %s' % proibido)

    def test_13_sem_dsn_a_cli_nao_inventa_durabilidade(self):
        anterior = os.environ.pop('SUPABASE_DB_URL', None)
        try:
            self.assertIsNone(ss._banco_se_houver())
        finally:
            if anterior is not None:
                os.environ['SUPABASE_DB_URL'] = anterior


class ONaoDeixaEtapaPendurada(unittest.TestCase):

    def test_14_a_rota_da_janela_fecha_a_etapa_mesmo_a_rebentar(self):
        """`social_rotas` apanha a exceção — o `except` do boundary nunca corre."""
        arv = ast.parse(_fonte('coleta/adaptador_instagram.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == '_janela')
        handlers = [h for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler)]
        self.assertTrue(handlers, 'a rota deixou de apanhar a falha da implementação')
        fecha = [n for h in handlers for n in ast.walk(h)
                 if isinstance(n, ast.Call)
                 and getattr(n.func, 'attr', None) == 'fechar']
        self.assertTrue(fecha, 'a rota rebenta e deixa a etapa em RUNNING')


class APoliticaEPERGUNTADAAntesDeGastar(unittest.TestCase):
    """A segunda porta que o censo desta missao encontrou, fora do `sintonia-scrap`.

    `comunicacao-publica.yml` corre `orquestrador.py`, que corre
    `coleta/comunicacao_coleta.py`. Para o YouTube isso ja entrava pelo
    `scrap_executor.COLLECT`. Para INSTAGRAM, FACEBOOK e LINKEDIN ia direto ao
    ator PAGO — e `LINKEDIN/FETCH_POST` esta `ROUTE_NOT_ALLOWED` nas DUAS rotas
    declaradas.

        UMA ROTA QUE FUNCIONA NAO E UMA ROTA PERMITIDA.
    """

    def _correr(self, plataforma):
        """Corre a fase com conta de mentira e a gaveta desviada. → (saida, ficheiros).

        Duas razoes para cada desvio:

        · O lote congelado real nao tem conta LinkedIn hoje, e sem conta a
          funcao devolve ANTES do portao. Um teste que passa porque a lista
          esta vazia mede a lista, nao o portao.

        · A fase PERMITIDA grava de verdade. Sem desviar `SAIDA`, o controlo
          positivo deixava lixo de teste no acervo — e o acervo desta casa tem
          guardas que contam ficheiros.
        """
        import shutil
        import tempfile
        import comunicacao_coleta as cc
        gaveta = tempfile.mkdtemp(prefix='c106d-')
        anterior_saida, anterior_contas = cc.SAIDA, cc.contas_autorizadas
        cc.SAIDA = gaveta
        cc.contas_autorizadas = lambda p=None: [
            {'ACCOUNT_HANDLE': 'x', 'ACCOUNT_URL': 'https://exemplo/x',
             'COMPANY': 'EXEMPLO', 'COUNTRY': 'IT'}]
        try:
            saida = cc.fase_posts(plataforma)
            return saida, sorted(os.listdir(gaveta))
        finally:
            cc.SAIDA, cc.contas_autorizadas = anterior_saida, anterior_contas
            shutil.rmtree(gaveta, ignore_errors=True)

    def test_19_a_rota_proibida_nao_corre_nem_com_conta_na_lista(self):
        d = mz.decisao('LINKEDIN', 'FETCH_POST')
        self.assertEqual(d['DECISAO'], mz.NAO_PERMITIDA,
                         'a politica mudou; este teste media a politica de 2026-09')
        saida, ficheiros = self._correr('LINKEDIN')
        self.assertIsNone(saida, 'a fase proibida devolveu artefato')
        self.assertEqual(ficheiros, [],
                         'a rota proibida gravou: %s' % ficheiros)

    def test_19b_a_rota_permitida_continua_a_correr(self):
        """O controlo positivo. Um portao que recusa tudo nao e um portao."""
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_POST')['DECISAO'],
                         mz.PERMITIDA_SIM)
        saida, ficheiros = self._correr('INSTAGRAM')
        self.assertIsNotNone(saida,
                             'o portao passou a recusar tambem o que e PERMITIDO')
        self.assertTrue(ficheiros, 'a fase permitida deixou de produzir artefato')

    def test_20_o_portao_pergunta_antes_de_escolher_o_ator(self):
        """Perguntar com o ator ja escolhido e conferir o bilhete depois da viagem."""
        arv = ast.parse(_fonte('coleta/comunicacao_coleta.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'fase_posts')
        corpo = list(ast.walk(fn))
        pergunta = [n.lineno for n in corpo if isinstance(n, ast.Call)
                    and getattr(n.func, 'attr', None) == 'decisao']
        ator = [n.lineno for n in corpo if isinstance(n, ast.Subscript)
                and getattr(n.value, 'id', None) == 'ATORES']
        self.assertTrue(pergunta, '`fase_posts` deixou de perguntar a politica')
        self.assertTrue(ator, 'a sonda perdeu a linha do ator; ela mede o ficheiro errado')
        self.assertLess(min(pergunta), min(ator),
                        'a politica passou a ser perguntada DEPOIS de escolher o ator')


class ODesvioEDeclarado(unittest.TestCase):
    """UM DESVIO DECLARADO E UMA MEDICAO. UM DESVIO CALADO E UM BURACO."""

    def test_21_nenhuma_fase_canonica_esta_na_lista_de_desvio(self):
        for fase in ss.FASES_CANONICAS:
            self.assertNotIn(fase, ss.FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY,
                             '%s esta nas duas tabelas ao mesmo tempo' % fase)

    def test_22_a_fase_que_salta_o_boundary_diz_que_saltou(self):
        for fase in ss.FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY:
            with self.subTest(fase=fase):
                self.assertTrue(ss._avisar_se_salta_o_boundary(fase),
                                '%s salta o boundary em silencio' % fase)
        # controlo negativo: uma fase canonica NAO avisa, senao o aviso nao
        # distingue nada e vira ruido que ninguem le.
        self.assertFalse(ss._avisar_se_salta_o_boundary('coletar'))

    def test_23_a_lista_de_desvio_corresponde_ao_despacho_medido(self):
        """A tabela nao pode nomear uma fase que a CLI nao oferece.

        Uma lista que nomeia fases inexistentes parece cobertura e nao e: no dia
        em que a fase for renomeada, o aviso cala-se e a tabela continua a dizer
        que ele existe.
        """
        arv = ast.parse(_fonte('coleta/social_scrap.py'))
        principal = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                         and n.name == 'main')
        oferecidas = set()
        for n in ast.walk(principal):
            if not isinstance(n, ast.Compare) or not n.comparators:
                continue
            c0 = n.comparators[0]
            if isinstance(c0, ast.Constant) and isinstance(c0.value, str):
                oferecidas.add(c0.value)
            elif isinstance(c0, ast.Tuple):
                oferecidas.update(e.value for e in c0.elts
                                  if isinstance(e, ast.Constant)
                                  and isinstance(e.value, str))
        self.assertTrue(oferecidas, 'a sonda nao leu fase nenhuma do despacho')
        for fase in ss.FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY:
            self.assertIn(fase, oferecidas,
                          '%s esta na lista de desvio e a CLI nao a oferece' % fase)


if __name__ == '__main__':
    unittest.main(verbosity=2)
