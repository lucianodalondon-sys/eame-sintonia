#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.4B — UMA CAPACIDADE, UM CAMINHO VIVO.

Há duas implementações de «obter fala de Reel do Instagram» neste repositório:

    ferramentas/reel_transcricao.py        pede `-f bestaudio`; VIDEO_BYTES = 0
    ferramentas/instagram_transcrever.py   baixa o MP4 INTEIRO e faz `ffmpeg -vn`

A segunda é o que a lei da C8 proíbe: `TRANSCRIPTION NEED != VIDEO DOWNLOAD`.
A pergunta da C10.4B não foi «ela existe?» — foi «ela é ALCANÇÁVEL?».

O QUE O CENSO MEDIU
---------------------
Pelo pedido canônico — executor, roteador, registo, portão, adaptador — a velha
NÃO é alcançada: uma armadilha nas suas funções públicas ficou muda nas seis
entradas, e disparou quando chamada de propósito.

    UMA ARMADILHA QUE NUNCA DISPARA SÓ PROVA ALGUMA COISA SE A MESMA
    ARMADILHA DISPARAR QUANDO ALGUÉM A CHAMA DE PROPÓSITO.

Mas nenhum `import` mostra a porta que ela tem:

    .github/workflows/sintonia-scrap.yml
        fase=transcrever  ->  ferramentas/instagram_transcrever.py rodar

É `workflow_dispatch`. Não é teste, não é histórico, não é comentário: é
despacho de produção.

    UMA PORTA QUE NENHUM IMPORT MOSTRA CONTINUA A SER UMA PORTA.

E ela não perguntava nada a ninguém — a decisão humana da C10.5D não a
alcançava.

    UMA DECISÃO QUE UMA PORTA NÃO CONHECE NÃO É UMA DECISÃO. É UM DESEJO.
"""
import ast
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('ferramentas', 'leis', 'coleta', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import social_matriz as mz              # noqa: E402
import reel_transcricao as rt           # noqa: E402
import instagram_transcrever as velho   # noqa: E402

NOVA_REL = 'ferramentas/reel_transcricao.py'
VELHA_REL = 'ferramentas/instagram_transcrever.py'
WORKFLOW = '.github/workflows/sintonia-scrap.yml'


def _fonte(rel):
    return io.open(os.path.join(RAIZ, rel), encoding='utf-8').read()


def _modulos_python():
    for raiz, dirs, fich in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in
                   ('node_modules', '.git', '__pycache__', 'BASELINE', 'data')]
        for f in fich:
            if f.endswith('.py'):
                yield os.path.relpath(os.path.join(raiz, f), RAIZ).replace(os.sep, '/')


def _quem_importa(modulo):
    """Os ficheiros que importam `modulo`, com a classe de cada um."""
    fora = []
    for rel in _modulos_python():
        if rel == VELHA_REL or rel == NOVA_REL:
            continue
        try:
            arv = ast.parse(io.open(os.path.join(RAIZ, rel), encoding='utf-8').read(), rel)
        except Exception:
            continue
        for n in ast.walk(arv):
            nomes = ([a.name for a in n.names] if isinstance(n, ast.Import)
                     else ([n.module or ''] if isinstance(n, ast.ImportFrom) else []))
            if any(modulo == (x or '').split('.')[-1] for x in nomes):
                fora.append(rel)
    return sorted(set(fora))


class ACadeiaNovaNaoConheceAVelha(unittest.TestCase):

    def test_a_nova_nao_importa_a_velha_em_lado_nenhum(self):
        # ESTA É A MUTAÇÃO OBRIGATÓRIA DO §8. Um `import instagram_transcrever`
        # dentro da cadeia nova seria a queda silenciosa para vídeo inteiro,
        # exactamente o que a C8 proibiu.
        arv = ast.parse(_fonte(NOVA_REL))
        importados = []
        for n in ast.walk(arv):
            if isinstance(n, ast.Import):
                importados += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                importados.append(n.module or '')
        self.assertNotIn('instagram_transcrever', importados,
                         'a cadeia audio-only ganhou uma queda para o caminho '
                         'de video inteiro')

    def test_nem_o_adaptador_nem_a_fase_de_fala_a_conhecem(self):
        """Medido no AST, nunca no texto.

        A primeira versao deste teste procurava a palavra no ficheiro inteiro e
        falhava — porque o `reel_transcrever` do adaptador EXPLICA, em prosa, que
        a matriz nomeia o ficheiro velho. Um comentario que fala do caminho
        velho nao e um caminho para ele.

            UMA SENTINELA ANCORADA NO TEXTO MEDE O TEXTO, NAO A LEI.
        """
        for rel in ('coleta/adaptador_instagram.py', 'coleta/comunicacao_coleta.py'):
            arv = ast.parse(_fonte(rel))
            importados = []
            for n in ast.walk(arv):
                if isinstance(n, ast.Import):
                    importados += [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom):
                    importados.append(n.module or '')
            self.assertNotIn('instagram_transcrever', importados,
                             '%s passou a IMPORTAR o caminho velho' % rel)

    def test_ninguem_em_producao_importa_a_velha(self):
        donos = _quem_importa('instagram_transcrever')
        producao = [d for d in donos if not d.startswith(('tests/', 'provas/',
                                                          'system-map/', 'docs/'))]
        self.assertEqual(producao, [],
                         'a implementacao velha ganhou chamador de producao: %s' % producao)
        # e a sonda tem de estar a ver alguma coisa — zero aqui mediria a sonda
        self.assertTrue(donos, 'a busca por quem importa deixou de encontrar seja o que for')

    def test_a_nova_continua_a_ser_alcancada_pelo_registo(self):
        import scrap_registo as reg
        import scrap_capacidades as cap
        reg.carregar_adaptadores()
        r = reg.adaptador_de('INSTAGRAM', 'instagram.reel.transcribe')
        self.assertIsNotNone(r['ROTA'])
        self.assertEqual(cap.da_matriz('instagram.reel.transcribe'), 'FETCH_TRANSCRIPT')
        self.assertIn('reel_transcricao', _fonte('coleta/adaptador_instagram.py'))


class APortaQueNenhumImportMostra(unittest.TestCase):
    """O `workflow_dispatch` era despacho de produção, e nenhum `import` o revelava.

    ACTUALIZADO NA C10.4C. A versão original desta classe media a porta ABERTA:
    exigia que a fase `transcrever` continuasse no workflow, que a rota velha
    perguntasse à política antes de sair, e que as suas duas saídas de rede
    estivessem cobertas. Era a medição certa para um mundo onde a porta existia.

    A C10.4C fechou a porta — que é a decisão de gente que a C10.4B disse que
    faltava. Estas sentinelas passam a medir o mundo NOVO. O que elas mediam
    antes fica escrito aqui e em `docs/sintonia-scrap/C10-4B-UM-CAMINHO-SO.md`;
    o que elas medem agora é que a porta não voltou.

        UMA SENTINELA QUE CONTINUA A MEDIR UM MUNDO QUE ACABOU MEDE O PASSADO.
    """

    def test_a_porta_do_workflow_foi_fechada_na_c10_4c(self):
        # Medido no comando, nunca no texto: o `run:` do workflow carrega hoje
        # um comentário que EXPLICA a aposentadoria e nomeia o ficheiro velho.
        # Prosa não é chamada.
        import yaml
        doc = yaml.safe_load(_fonte(WORKFLOW))
        vivas = []

        def varre(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == 'run' and isinstance(v, str):
                        vivas.extend(ln for ln in v.splitlines()
                                     if not ln.strip().startswith('#'))
                    varre(v)
            elif isinstance(o, list):
                for v in o:
                    varre(v)
        varre(doc)
        self.assertTrue(vivas, 'a sonda nao leu comando nenhum')
        for ln in vivas:
            self.assertNotIn('instagram_transcrever.py', ln,
                             'a fase de video inteiro voltou ao workflow: %s' % ln.strip())
        disparo = doc.get('on') or doc.get(True) or {}
        opcoes = disparo['workflow_dispatch']['inputs']['fase']['options']
        self.assertNotIn('transcrever', opcoes)
        self.assertNotIn('transcrever-alvos', opcoes)

    def test_o_que_essa_porta_corria_deixou_de_correr(self):
        """A pergunta de política saiu daqui — e saiu porque não há saída.

        Enquanto a rota adquiria, o portão era a única coisa entre ela e a CDN
        da Meta. Aposentada, ela não adquire: um portão à frente de uma função
        que levanta seria cerimónia, e cerimónia parece capacidade.
        """
        arv = ast.parse(_fonte(VELHA_REL))
        self.assertFalse([n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                          and n.name == 'politica_da_aquisicao'])
        self.assertFalse(hasattr(velho, 'politica_da_aquisicao'))
        # e ela deixou de carregar o dono do reconhecedor: um aposentado que
        # importa o ASR continua a parecer, a todos os censos, um transcritor
        importados = []
        for n in ast.walk(arv):
            if isinstance(n, ast.Import):
                importados += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                importados.append(n.module or '')
        self.assertNotIn('fala_local', importados)

    def test_a_velha_nao_adquire_seja_qual_for_a_decisao(self):
        """Antes recusava por política. Hoje recusa por não ser mais uma rota.

            BLOCKED != RETIRED — e esta é a diferença, em duas linhas.
        """
        alvo = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'nao-deve-nascer.mp4')
        with self.assertRaises(velho.RotaAposentada):
            velho._baixar('https://scontent.cdninstagram.com/nada.mp4', alvo)
        self.assertFalse(os.path.exists(alvo), 'a velha escreveu apesar da recusa')
        # a decisao de politica continua NAO, e continua a nao ser desta missao
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')['DECISAO'],
                         mz.NAO_PERMITIDA)

    def test_o_embed_da_velha_tambem_deixou_de_abrir(self):
        # Gratis nao era permitido: abrir o embed subia navegador e tocava o
        # host. Hoje nem sobe.
        with self.assertRaises(velho.RotaAposentada):
            velho._url_nova('QUALQUER')

    def test_a_velha_deixou_de_ter_pontos_de_rede(self):
        """A cobertura do portao virou ausencia de saida — que e mais forte.

        A sonda mede o que mediu sempre: chamadas `urlopen`/`abrir` na arvore.
        Antes exigia que cada uma tivesse portao. Agora exige que nao haja
        nenhuma — e prova, no mesmo passo, que a sonda continua a ver, correndo
        a mesma busca sobre o dono canonico, onde ela TEM de encontrar saida.
        """
        def saidas(rel):
            arv = ast.parse(_fonte(rel))
            return [n for n in ast.walk(arv) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr in ('urlopen', 'abrir', 'run', 'Popen')]
        self.assertEqual(saidas(VELHA_REL), [],
                         'a rota aposentada ganhou saida de rede outra vez')
        self.assertTrue(saidas(NOVA_REL),
                        'a sonda deixou de encontrar saida onde ela existe — '
                        'zero aqui mediria a sonda, nao a casa')


class UmaDecisaoTodasAsPortas(unittest.TestCase):

    def test_as_duas_implementacoes_perguntam_a_MESMA_capacidade(self):
        self.assertEqual(velho.CAPACIDADE_NA_MATRIZ, rt.CAPACIDADE_NA_MATRIZ)
        self.assertEqual(velho.PLATAFORMA, 'INSTAGRAM')

    def test_a_politica_nao_foi_alterada_por_esta_missao(self):
        # A C10.4B nao e missao de politica. Se a decisao mudar, foi outra coisa.
        rotas = mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT']
        self.assertEqual(len(rotas), 1)
        self.assertEqual(rotas[0]['PERMITIDA'], 'NAO')
        self.assertEqual(rotas[0]['ESTADO'], 'ROUTE_NOT_ALLOWED')

    def test_o_reconhecedor_continua_a_ter_um_dono_so(self):
        donos = []
        for rel in _modulos_python():
            if rel.startswith('tests/'):
                continue
            if 'WhisperModel(' in io.open(os.path.join(RAIZ, rel),
                                          encoding='utf-8').read():
                donos.append(rel)
        self.assertEqual(donos, ['ferramentas/fala_local.py'])

    def test_so_a_nova_pede_alguma_coisa_a_rede(self):
        """ACTUALIZADO NA C10.4C.

        A versao original comparava DOIS pedidos: `-vn` sobre o ficheiro inteiro
        contra `-f bestaudio`. Hoje so ha um pedido no repositorio, porque a
        rota que baixava o ficheiro inteiro deixou de pedir seja o que for.
        """
        nova_arv = ast.parse(_fonte(NOVA_REL))
        seletor = [n.value for n in ast.walk(nova_arv)
                   if isinstance(n, ast.Constant) and n.value == 'bestaudio']
        self.assertTrue(seletor, 'a nova deixou de pedir so o som')
        self.assertEqual(rt.SELETOR_SO_AUDIO, 'bestaudio')

        # e a velha nao monta argv nenhum: medido na arvore, porque `-vn` e
        # `bestaudio` aparecem na PROSA das duas e prosa nao e comando
        velha_arv = ast.parse(_fonte(VELHA_REL))
        self.assertEqual([n.value for n in ast.walk(velha_arv)
                          if isinstance(n, ast.Constant) and n.value in
                          ('-vn', '-i', 'ffmpeg', 'bestaudio')], [],
                         'a rota aposentada voltou a montar um comando de media')

        # a decisao de politica continua NAO — e continua a nao ser desta missao
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')['DECISAO'],
                         mz.NAO_PERMITIDA)


if __name__ == '__main__':
    unittest.main(verbosity=2)
