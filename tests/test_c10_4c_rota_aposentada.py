#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.4C — A ROTA LEGADA DE TRANSCRIÇÃO ESTÁ APOSENTADA, NÃO SÓ TRAVADA.

A C10.4B mediu que `ferramentas/instagram_transcrever.py` continuava alcançável
por CINCO portas operacionais, e travou-a pela política. Travar não é aposentar:

    BLOCKED != RETIRED.  DISABLED != RETIRED.

Uma porta travada continua à espera de que a decisão mude. A C10.4C fecha as
portas.

    workflow_dispatch · opção `transcrever`            fechada
    workflow_dispatch · opção `transcrever-alvos`      fechada
    workflow `run:`   · `instagram_transcrever.py rodar`   removido
    workflow `run:`   · `instagram_transcrever.py alvos`   removido
    CLI `__main__`    · qualquer argumento             recusa, código 2

E recusa ALTO. Um script aposentado que sai 0 em silêncio é pior do que uma
porta aberta: quem o chamasse veria sucesso.

    UM SCRIPT QUE SAI 0 SEM FAZER NADA DIZ QUE CORREU.

O QUE FICOU DE PÉ, E PORQUÊ
-----------------------------
A fase `janela` NÃO foi tocada. Medido: `coleta/instagram_janela.py` não importa
`fala_local`, não importa a rota velha, não menciona `WhisperModel` nem `ffmpeg`.
Ela faz descoberta, perfil e metadados — capacidade distinta e legítima.

    CORPUS DIFERENTE NÃO É CONCEITO DIFERENTE — mas DESCOBERTA não é
    TRANSCRIÇÃO, e essa é uma diferença de conceito, não de pasta.
"""
import ast
import io
import os
import subprocess
import sys
import unittest

import yaml

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('ferramentas', 'leis', 'coleta', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import instagram_transcrever as velho   # noqa: E402
import social_matriz as mz              # noqa: E402

VELHA_REL = 'ferramentas/instagram_transcrever.py'
JANELA_REL = 'coleta/instagram_janela.py'
WORKFLOW = '.github/workflows/sintonia-scrap.yml'
CANONICO = 'ferramentas/reel_transcricao.py'


def _fonte(rel):
    return io.open(os.path.join(RAIZ, rel), encoding='utf-8').read()


def _workflow():
    return yaml.safe_load(_fonte(WORKFLOW))


def _opcoes_de_fase():
    d = _workflow()
    disparo = d.get('on') or d.get(True) or {}
    return list(disparo['workflow_dispatch']['inputs']['fase']['options'])


def _runs_de(doc):
    """Todos os `run:` de um documento de workflow — parseado, nao grep."""
    fora = []

    def varre(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == 'run' and isinstance(v, str):
                    fora.append(v)
                varre(v)
        elif isinstance(o, list):
            for v in o:
                varre(v)
    varre(doc)
    return fora


def _linhas_vivas(run):
    """As linhas de um bloco `run:` que a shell EXECUTA.

    Uma linha cujo primeiro caractere nao-branco e `#` e prosa: a shell le-a e
    nao faz nada. Medir prosa como se fosse chamada e o defeito que a C10.4B ja
    pagou duas vezes:

        UMA SENTINELA ANCORADA NO TEXTO MEDE O TEXTO, NAO A LEI.

    O filtro corta SO a linha inteira de comentario. Um `#` no fim de uma linha
    de comando fica — cortar ali seria afrouxar a sentinela, e a direcao segura
    de um filtro de prova e deixar de MAIS, nunca de menos.
    """
    return [ln for ln in run.splitlines() if not ln.strip().startswith('#')]


def _comandos_do_workflow():
    return _runs_de(_workflow())


class AsPortasEstaoFechadas(unittest.TestCase):

    def test_1_o_dispatch_nao_oferece_mais_a_fase_legada(self):
        opcoes = _opcoes_de_fase()
        self.assertTrue(opcoes, 'a sonda nao leu opcao nenhuma; mediria zero por engano')
        self.assertNotIn('transcrever', opcoes)
        self.assertNotIn('transcrever-alvos', opcoes)
        # e o contraponto: as fases que NAO sao desta missao continuam la
        self.assertIn('janela', opcoes)
        self.assertIn('yt-transcrever', opcoes)

    def test_2_nenhum_workflow_chama_a_aquisicao_legada(self):
        vistos, linhas_medidas = [], 0
        for raiz, _dd, fich in os.walk(os.path.join(RAIZ, '.github')):
            for f in fich:
                if not f.endswith(('.yml', '.yaml')):
                    continue
                caminho = os.path.join(raiz, f)
                try:
                    doc = yaml.safe_load(io.open(caminho, encoding='utf-8').read())
                except Exception:
                    continue
                vistos.append(f)
                for c in _runs_de(doc):
                    for ln in _linhas_vivas(c):
                        linhas_medidas += 1
                        self.assertNotIn('instagram_transcrever.py', ln,
                                         '%s ainda corre a rota legada: %s'
                                         % (f, ln.strip()))
        # a sonda tem de ter medido alguma coisa: uma sonda que encontra zero e
        # diz «limpo» mede a sonda, nao a casa
        self.assertIn('sintonia-scrap.yml', vistos)
        self.assertGreater(linhas_medidas, 100)

    def test_2d_nenhuma_condicao_do_workflow_espera_a_fase_retirada(self):
        """Um `if:` que ainda nomeia a fase diz que a fase existe.

        Não é chamada — `type: choice` impede o valor de chegar. Mas as duas
        guardas do workflow (o portão do navegador e o pré-voo da transcrição)
        nomeavam `transcrever` numa lista, e quem lesse o workflow leria ali que
        a fase continuava de pé. Uma retirada que deixa as guardas à espera não
        está contada.

            APAGAR A PORTA E DEIXAR O PORTEIRO NÃO FECHA A CASA.
        """
        alvo = ('"transcrever"', "'transcrever'", '"transcrever-alvos"',
                "'transcrever-alvos'")
        condicoes = []

        def varre(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == 'if' and isinstance(v, str):
                        condicoes.append(v)
                    varre(v)
            elif isinstance(o, list):
                for v in o:
                    varre(v)
        varre(_workflow())
        self.assertTrue(condicoes, 'a sonda nao leu condicao nenhuma')
        for c in condicoes:
            for a in alvo:
                self.assertNotIn(a, c,
                                 'uma guarda do workflow ainda espera a fase '
                                 'retirada: %s' % c)
        # controlo positivo: a guarda da transcricao do YouTube continua la
        self.assertTrue(any('yt-transcrever' in c for c in condicoes),
                        'a sonda deixou de ver as guardas que existem')

    def test_2b_o_filtro_de_prosa_nao_e_cego(self):
        """Controlo positivo do filtro: ele corta comentario, nao comando."""
        bloco = ('\n'.join((
            '            # `ferramentas/instagram_transcrever.py` corria aqui',
            '            #     e este comentario fala dela de novo',
            '            transcrever) $PY ferramentas/instagram_transcrever.py rodar ;;',
            '            janela) $PY coleta/instagram_janela.py tudo ;;')))
        vivas = _linhas_vivas(bloco)
        self.assertEqual(len(vivas), 2, 'o filtro cortou linha a mais ou a menos')
        self.assertTrue(any('instagram_transcrever.py' in ln for ln in vivas),
                        'o filtro engoliu uma CHAMADA viva — seria uma sonda cega')
        self.assertTrue(any('instagram_janela.py' in ln for ln in vivas))
        # e no workflow real ele deixa as chamadas vivas de pe
        vivo = '\n'.join(ln for c in _comandos_do_workflow()
                          for ln in _linhas_vivas(c))
        self.assertIn('coleta/instagram_janela.py', vivo)
        self.assertIn('ferramentas/youtube_transcrever.py', vivo)

    def test_2c_a_fase_e_escolha_fechada_nao_texto_livre(self):
        """Se `fase` fosse texto livre, tirar a opcao nao fecharia a porta.

        O ramo `*)` do `case` existe e cai em `instagram_coleta.py`. Com
        `type: choice` o GitHub so aceita valor da lista — a porta fecha no
        despacho, antes de qualquer shell.
        """
        d = _workflow()
        campo = (d.get('on') or d.get(True))['workflow_dispatch']['inputs']['fase']
        self.assertEqual(campo.get('type'), 'choice')
        self.assertNotIn(campo.get('default'), ('transcrever', 'transcrever-alvos'))

    def test_3_nenhum_agendador_a_chama(self):
        for raiz, _dd, fich in os.walk(os.path.join(RAIZ, '.github')):
            for f in fich:
                if not f.endswith(('.yml', '.yaml')):
                    continue
                doc = yaml.safe_load(_fonte(os.path.relpath(
                    os.path.join(raiz, f), RAIZ).replace(os.sep, '/')))
                disparo = (doc.get('on') or doc.get(True) or {}) if doc else {}
                if not (isinstance(disparo, dict) and 'schedule' in disparo):
                    continue
                self.assertNotIn('instagram_transcrever',
                                 io.open(os.path.join(raiz, f), encoding='utf-8').read(),
                                 '%s e agendado e menciona a rota legada' % f)

    def test_4_o_CLI_recusa_alto_seja_qual_for_o_argumento(self):
        for arg in ([], ['rodar'], ['alvos'], ['qualquer'], ['rodar', 'small', '5']):
            r = subprocess.run([sys.executable, os.path.join(RAIZ, VELHA_REL)] + arg,
                               capture_output=True, text=True, timeout=120, cwd=RAIZ)
            self.assertEqual(r.returncode, 2,
                             'argumento %r saiu com %d — um aposentado que sai 0 '
                             'diz que correu' % (arg, r.returncode))
            self.assertIn('ROTA_APOSENTADA', r.stderr + r.stdout)

    def test_5_o_router_e_o_registo_nao_a_conhecem(self):
        import scrap_registo as reg
        reg.carregar_adaptadores()
        for n in ('instagram.reel.capture', 'instagram.reel.audio',
                  'instagram.reel.transcribe'):
            r = reg.adaptador_de('INSTAGRAM', n)
            fn = r['EXECUTA'] or r['ROTA']
            self.assertIsNotNone(fn, '%s perdeu o caminho' % n)
            self.assertNotIn('instagram_transcrever', getattr(fn, '__module__', ''))
        for rel in ('coleta/scrap_executor.py', 'coleta/social_rotas.py'):
            arv = ast.parse(_fonte(rel))
            imp = []
            for n in ast.walk(arv):
                if isinstance(n, ast.Import):
                    imp += [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom):
                    imp.append(n.module or '')
            self.assertNotIn('instagram_transcrever', imp)


class NadaAResuscita(unittest.TestCase):

    def test_6_falha_da_rota_canonica_nao_aciona_a_antiga(self):
        arv = ast.parse(_fonte(CANONICO))
        imp = []
        for n in ast.walk(arv):
            if isinstance(n, ast.Import):
                imp += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                imp.append(n.module or '')
        self.assertNotIn('instagram_transcrever', imp)

    def test_7_e_8_o_que_ela_fazia_deixou_de_correr(self):
        # AUDIO_ONLY_UNAVAILABLE e politica negativa nao tem por onde cair: as
        # funcoes que adquiriam levantam, nao adquirem.
        for nome, args in (('_baixar', ('u', '/tmp/nao-nasce.mp4')),
                           ('_url_nova', ('X',)),
                           ('_audio', ('X', 'u')),
                           ('fase_rodar', (None, None))):
            with self.subTest(funcao=nome):
                with self.assertRaises(velho.RotaAposentada):
                    getattr(velho, nome)(*args)
        self.assertFalse(os.path.exists('/tmp/nao-nasce.mp4'))

    def test_9_importar_nao_e_executar(self):
        # O modulo continua importavel — um teste historico le a fonte dele — e
        # importar nao corre nada.
        import importlib
        importlib.reload(velho)
        self.assertTrue(hasattr(velho, 'APOSENTADO'))
        self.assertTrue(issubclass(velho.RotaAposentada, RuntimeError))
        # e ele deixou de carregar o dono da politica: quem nao adquire nao
        # precisa de autorizacao para adquirir
        self.assertFalse(hasattr(velho, 'politica_da_aquisicao'))

    def test_a_velha_nao_virou_delegador(self):
        # Um wrapper que delega continua a ser um nome pelo qual a capacidade
        # atende — e seria o segundo owner outra vez, com outra roupa.
        arv = ast.parse(_fonte(VELHA_REL))
        imp = []
        for n in ast.walk(arv):
            if isinstance(n, ast.Import):
                imp += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                imp.append(n.module or '')
        self.assertNotIn('reel_transcricao', imp,
                         'a rota aposentada passou a delegar; isso e o segundo '
                         'owner outra vez')


class NemPelaPortaDosFundos(unittest.TestCase):
    """Um `import` não é a única forma de chamar um ficheiro.

    `subprocess`, `importlib.import_module`, `exec`, `runpy` — todos alcançam um
    módulo sem que nenhum `import` o mostre. A C10.4B já pagou por acreditar em
    `import`:

        UMA PORTA QUE NENHUM IMPORT MOSTRA CONTINUA A SER UMA PORTA.
    """

    CADEIA = ('ferramentas/reel_transcricao.py', 'coleta/adaptador_instagram.py',
              'coleta/scrap_executor.py', 'coleta/social_rotas.py',
              'coleta/scrap_registo.py', 'ferramentas/fala_local.py',
              'coleta/instagram_janela.py')

    def test_11_a_cadeia_viva_nao_nomeia_a_rota_velha_em_literal_nenhum(self):
        """Medido nas CONSTANTES da árvore, que é onde um argv de `subprocess`
        ou um nome de `import_module` teria de aparecer. Docstrings ficam de
        fora de propósito: uma delas EXPLICA a matriz, e prosa não é chamada.
        """
        for rel in self.CADEIA:
            arv = ast.parse(_fonte(rel))
            prosa = set()
            for n in ast.walk(arv):
                if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef)):
                    d = ast.get_docstring(n, clean=False)
                    if d:
                        prosa.add(d)
            maus = [n.value for n in ast.walk(arv)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and 'instagram_transcrever' in n.value and n.value not in prosa]
            self.assertEqual(maus, [], '%s nomeia a rota velha num literal '
                                       'executável: %s' % (rel, maus))

    def test_12_a_sonda_de_literal_nao_e_cega(self):
        """Controlo positivo: a mesma sonda TEM de encontrar o que existe."""
        arv = ast.parse("import subprocess\n"
                        "subprocess.run(['py', 'ferramentas/instagram_transcrever.py'])\n")
        achou = [n.value for n in ast.walk(arv)
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)
                 and 'instagram_transcrever' in n.value]
        self.assertEqual(len(achou), 1, 'a sonda de literal ficou cega')

    def test_13_a_transcricao_tem_um_registo_so_e_nao_e_a_velha(self):
        """M6 — dois owners registrados para TRANSCRIPTION.

        O registo já recusa dois donos da mesma `(plataforma, capacidade)`. O
        que ele não vê sozinho é um segundo dono a entrar por OUTRO nome de
        capacidade que signifique a mesma coisa. Aqui conta-se: quantas
        entradas registradas traduzem para `FETCH_TRANSCRIPT` do Instagram.
        """
        import scrap_registo as reg
        import scrap_capacidades as cap
        reg.carregar_adaptadores()
        donos = []
        for (plat, capac), r in reg.registados().items():
            if plat != 'INSTAGRAM':
                continue
            if cap.da_matriz(capac) != 'FETCH_TRANSCRIPT':
                continue
            fn = r['EXECUTA'] or r['ROTA']
            donos.append((capac, r['ADAPTADOR'], getattr(fn, '__module__', None)))
        self.assertEqual(len(donos), 1,
                         'TRANSCRIPTION do Instagram tem %d donos registrados: %s'
                         % (len(donos), donos))
        capac, adaptador, modulo = donos[0]
        self.assertEqual(capac, 'instagram.reel.transcribe')
        self.assertNotIn('instagram_transcrever', modulo or '')


class OMapaNaoDeclaraUmaArestaQueNaoExiste(unittest.TestCase):
    """O censo da coleta contava PROSA como chamada.

    Com a rota aposentada, o censo declarou que ela chamava
    `reel_transcricao`, `adaptador_instagram` e `youtube_transcrever`, e que
    dois deles corriam no CI. Nada disso era verdade: a fonte de todas essas
    arestas era o docstring que EXPLICA a aposentadoria e o comentário do
    workflow que a anuncia. Um módulo que importa `sys` e mais nada não chama
    ninguém.

        UM NOME DENTRO DE UMA FRASE NÃO É UM ARGV.

    O censo passa a separar `chamado_por` de `citado_por`. A citação continua
    registada — uma instrução operacional escrita num documento É uma porta, e
    esta missão fechou cinco delas — mas deixou de se disfarçar de aresta.
    """

    CENSO = 'system-map/data/censo-da-coleta.generated.json'

    def _ficha(self, caminho):
        import json
        d = json.loads(_fonte(self.CENSO))
        por = {x['ficheiro']: x for x in d['FICHEIROS']}
        self.assertIn(caminho, por, 'o censo deixou de ver %s' % caminho)
        return por[caminho]

    def test_14_o_censo_nao_declara_a_aposentada_a_chamar_ninguem(self):
        ficha = self._ficha(VELHA_REL)
        self.assertEqual(ficha['chamado_por'], [])
        self.assertFalse(ficha['sai_para_fora'],
                         'o censo ainda diz que a rota aposentada sai para fora')
        self.assertFalse(ficha['no_ci'],
                         'o censo ainda diz que a rota aposentada corre no CI')
        # a aresta caiu, a citacao ficou: fala_local nomeia-a na sua prosa de
        # proveniencia, e isso e um facto sobre o repositorio
        self.assertIn('citado_por', ficha, 'o censo perdeu a coluna da citacao')

    def test_15_e_o_censo_continua_a_ver_as_arestas_que_existem(self):
        """Controlo positivo: cortar prosa nao pode cortar codigo."""
        asr = self._ficha('ferramentas/fala_local.py')
        self.assertIn(CANONICO, asr['chamado_por'],
                      'o censo deixou de ver quem IMPORTA o reconhecedor')
        janela = self._ficha(JANELA_REL)
        self.assertTrue(janela['chamado_por'],
                        'o censo deixou de ver quem chama a janela')
        self.assertTrue(janela['no_ci'],
                        'o censo deixou de ver a janela no CI — ela continua '
                        'a ser uma fase do workflow')


class AJanelaFicouDePe(unittest.TestCase):

    def test_10_a_janela_nao_transcreve_e_continua_oferecida(self):
        fonte = _fonte(JANELA_REL)
        arv = ast.parse(fonte)
        imp = []
        for n in ast.walk(arv):
            if isinstance(n, ast.Import):
                imp += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                imp.append(n.module or '')
        self.assertNotIn('fala_local', imp, 'a janela ganhou reconhecedor')
        self.assertNotIn('instagram_transcrever', imp)
        self.assertNotIn('WhisperModel(', fonte)
        # e continua a ser oferecida, porque descoberta nao e transcricao
        opcoes = _opcoes_de_fase()
        self.assertEqual([o for o in opcoes if o.startswith('janela')],
                         ['janela', 'janela-perfis', 'janela-objetos'])

    def test_a_janela_continua_a_ser_chamada_pelo_workflow(self):
        comandos = ' '.join(_comandos_do_workflow())
        self.assertIn('instagram_janela.py', comandos,
                      'a janela deixou de ser chamada; isto nao era desta missao')


class UmOwnerSo(unittest.TestCase):

    def test_a_politica_nao_mudou_nesta_missao(self):
        rotas = mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT']
        self.assertEqual(len(rotas), 1)
        self.assertEqual(rotas[0]['PERMITIDA'], 'NAO')
        self.assertEqual(rotas[0]['ESTADO'], 'ROUTE_NOT_ALLOWED')

    def test_o_reconhecedor_continua_a_ter_um_dono_so(self):
        donos = []
        for raiz, dirs, fich in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('node_modules', '.git', '__pycache__', 'BASELINE', 'data')]
            for f in fich:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), RAIZ).replace(os.sep, '/')
                if rel.startswith('tests/'):
                    continue
                if 'WhisperModel(' in io.open(os.path.join(raiz, f),
                                              encoding='utf-8').read():
                    donos.append(rel)
        self.assertEqual(donos, ['ferramentas/fala_local.py'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
