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
    """O `workflow_dispatch` é despacho de produção, e nenhum `import` o revela."""

    def test_a_porta_do_workflow_continua_a_existir_e_esta_medida(self):
        # Este teste NAO exige que a porta desapareca — apagar uma entrada
        # operacional e decisao de gente. O que ele exige e que ela nao mude de
        # sitio em silencio: se mudar, a medicao da C10.4B fica velha e alguem
        # tem de a refazer.
        wf = _fonte(WORKFLOW)
        self.assertIn('instagram_transcrever.py rodar', wf,
                      'a fase `transcrever` do workflow mudou; a C10.4B tem de '
                      'ser remedida antes de se confiar no veredito dela')

    def test_o_que_essa_porta_corre_pergunta_a_politica(self):
        self.assertIn('social_matriz', _fonte(VELHA_REL),
                      'a porta do workflow voltou a nao conhecer a decisao')
        arv = ast.parse(_fonte(VELHA_REL))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'politica_da_aquisicao')
        chamadas = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute) and n.func.attr == 'decisao'
                    and isinstance(n.func.value, ast.Name) and n.func.value.id == 'mz']
        self.assertEqual(len(chamadas), 1,
                         'a velha deixou de perguntar ao dono da politica')

    def test_a_velha_recusa_a_rede_sob_a_decisao_actual(self):
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')['DECISAO'],
                         mz.NAO_PERMITIDA)
        alvo = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'nao-deve-nascer.mp4')
        with self.assertRaises(PermissionError):
            velho._baixar('https://scontent.cdninstagram.com/nada.mp4', alvo)
        self.assertFalse(os.path.exists(alvo), 'a velha escreveu apesar da recusa')

    def test_o_embed_da_velha_tambem_bate_no_portao(self):
        # Gratis nao e permitido: abrir o embed sobe navegador e toca o host.
        with self.assertRaises(PermissionError):
            velho._url_nova('QUALQUER')

    def test_os_dois_pontos_de_rede_da_velha_estao_cobertos(self):
        arv = ast.parse(_fonte(VELHA_REL))

        def dono(no):
            for f in ast.walk(arv):
                if isinstance(f, ast.FunctionDef) and no in ast.walk(f):
                    return f.name
            return None

        saidas = {dono(n) for n in ast.walk(arv) if isinstance(n, ast.Call)
                  and isinstance(n.func, ast.Attribute)
                  and n.func.attr in ('urlopen', 'abrir')}
        saidas.discard(None)
        guardadas = set()
        for nome in saidas:
            fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                      and n.name == nome)
            if any(isinstance(n, ast.Call) and getattr(n.func, 'id', None)
                   == 'politica_da_aquisicao' for n in ast.walk(fn)):
                guardadas.add(nome)
        self.assertTrue(saidas, 'a sonda nao encontrou saida de rede nenhuma')
        self.assertEqual(saidas, guardadas,
                         'saida de rede sem portao na velha: %s' % sorted(saidas - guardadas))


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

    def test_so_a_velha_pede_o_ficheiro_inteiro(self):
        """As duas fazem coisas diferentes COM A REDE, e mede-se no argv.

        `-vn` aparece na prosa das duas — a nova EXPLICA no cabecalho porque
        deixou de o fazer. O que separa uma da outra e o comando que cada uma
        monta, e isso le-se na arvore, nao no texto.
        """
        velha_arv = ast.parse(_fonte(VELHA_REL))
        argv_velha = [n.value for n in ast.walk(velha_arv)
                      if isinstance(n, ast.Constant) and n.value == '-vn']
        self.assertTrue(argv_velha, 'a velha deixou de cortar a imagem depois de a baixar')

        nova_arv = ast.parse(_fonte(NOVA_REL))
        seletor = [n.value for n in ast.walk(nova_arv)
                   if isinstance(n, ast.Constant) and n.value == 'bestaudio']
        self.assertTrue(seletor, 'a nova deixou de pedir so o som')
        self.assertEqual(rt.SELETOR_SO_AUDIO, 'bestaudio')

        # e a velha, que pede o ficheiro inteiro, esta travada pela decisao
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')['DECISAO'],
                         mz.NAO_PERMITIDA)
        fn = next(n for n in ast.walk(velha_arv) if isinstance(n, ast.FunctionDef)
                  and n.name == '_baixar')
        self.assertTrue([n for n in ast.walk(fn) if isinstance(n, ast.Call)
                         and getattr(n.func, 'id', None) == 'politica_da_aquisicao'],
                        'o descarregador da velha perdeu o portao')


if __name__ == '__main__':
    unittest.main(verbosity=2)
