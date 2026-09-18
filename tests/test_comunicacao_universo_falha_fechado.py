#!/usr/bin/env python3
"""
O UNIVERSO DO CONCORRENTE FALHA FECHADO SEM O CROSSWALK — e nao escreve nada.

    py tests/test_comunicacao_universo_falha_fechado.py

O DEFEITO QUE ESTAS PROVAS FECHAM (medido em 2026-09-17, know-how §139)
--------------------------------------------------------------------------
`data/samples/COMPETITOR-CROSSWALK.json` NUNCA esteve no Git. Sem ele,
`regras/comunicacao_universo.py` montava um universo com ZERO casas e, corrido pela
linha de comando, escrevia esse vazio por cima do `UNIVERSO-CONTAS-V1.json`
versionado — com `SOURCE_ID`, `DATASET_OWNER` e `EVIDENCE_CLASS` iguais aos do
verdadeiro. Um derivado sem fonte tem de RECUSAR, com a causa escrita, e nao pode
tocar no que ja la esta.

    O QUE SE PROVA AQUI                              COMO
    · ausente        → CrosswalkAusente              montar()/grupos_do_crosswalk()
    · ilegivel       → CrosswalkIlegivel             JSON partido, forma errada, vazio,
                                                     contagens que nao sao inteiros
    · recusa = zero mutacao                          pasta de saida NAO e criada; um
                                                     universo pre-existente fica byte a
                                                     byte igual; nenhum temporario sobra
    · em processo NOVO tambem                        subprocess com main(caminho, destino)
    · a fixture e fixture                            grupos GRUPO-FIXTURE-*, e nao e o
                                                     caminho canonico
    · o caminho canonico continua a ser o padrao     montar() sem argumento le CROSSWALK

Nenhuma prova aqui reconstroi o crosswalk nem escreve no acervo: tudo corre numa
casa de mentira (`tempfile`), e o caminho canonico so e LIDO.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import comunicacao_universo as uni  # noqa: E402

FIXTURE = os.path.join(HERE, 'fixtures', 'comunicacao', 'COMPETITOR-CROSSWALK.fixture.json')


def _arvore(pasta):
    """Todos os caminhos debaixo de `pasta` (ou [] se ela nao existe)."""
    if not os.path.isdir(pasta):
        return []
    fora = []
    for raiz, pastas, ficheiros in os.walk(pasta):
        for n in pastas + ficheiros:
            fora.append(os.path.relpath(os.path.join(raiz, n), pasta))
    return sorted(fora)


class UmaCasaDeMentira(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='universo-fecha-')
        # A pasta de saida NAO existe de proposito: a recusa nao a pode criar.
        self.saida = os.path.join(self.tmp, 'saida')
        self.destino = os.path.join(self.saida, 'UNIVERSO-CONTAS-V1.json')
        self.ausente = os.path.join(self.tmp, 'NAO-EXISTE', 'COMPETITOR-CROSSWALK.json')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _crosswalk(self, corpo, nome='CROSSWALK.json', bruto=None):
        p = os.path.join(self.tmp, nome)
        with io.open(p, 'w', encoding='utf-8') as f:
            f.write(bruto if bruto is not None else json.dumps(corpo))
        return p


class OCrosswalkAusenteRecusa(UmaCasaDeMentira):

    def test_grupos_do_crosswalk_levanta_e_nao_devolve_lista_vazia(self):
        with self.assertRaises(uni.CrosswalkAusente) as cm:
            uni.grupos_do_crosswalk(self.ausente)
        self.assertIn('nada foi derivado', str(cm.exception))
        self.assertIn(self.ausente, str(cm.exception),
                      'a recusa tem de dizer QUE caminho procurou')

    def test_montar_levanta_a_mesma_causa(self):
        with self.assertRaises(uni.CrosswalkAusente):
            uni.montar(self.ausente)

    def test_a_causa_e_uma_folha_da_hierarquia_fechada(self):
        self.assertTrue(issubclass(uni.CrosswalkAusente, uni.CrosswalkIndisponivel))
        self.assertTrue(issubclass(uni.CrosswalkIlegivel, uni.CrosswalkIndisponivel))
        self.assertTrue(issubclass(uni.CrosswalkIndisponivel, RuntimeError))

    def test_a_linha_de_comando_sai_2_e_nao_cria_pasta_nem_ficheiro(self):
        antes = _arvore(self.tmp)
        err = io.StringIO()
        with unittest.mock.patch('sys.stderr', err):
            codigo = uni.main(caminho=self.ausente, destino=self.destino)
        self.assertEqual(2, codigo)
        self.assertIn('UNIVERSO = NAO_DERIVADO', err.getvalue())
        self.assertIn('CrosswalkAusente', err.getvalue())
        self.assertFalse(os.path.exists(self.saida), 'a recusa criou a pasta de saida')
        self.assertFalse(os.path.exists(self.destino), 'a recusa criou o ficheiro')
        self.assertEqual(antes, _arvore(self.tmp), 'a recusa deixou rasto na casa')

    def test_a_recusa_nao_toca_num_universo_que_ja_existia(self):
        os.makedirs(self.saida)
        original = b'{"ISTO": "e o universo verdadeiro, e ninguem lhe toca"}\n'
        with open(self.destino, 'wb') as f:
            f.write(original)
        mtime = os.stat(self.destino).st_mtime_ns
        with unittest.mock.patch('sys.stderr', io.StringIO()):
            codigo = uni.main(caminho=self.ausente, destino=self.destino)
        self.assertEqual(2, codigo)
        with open(self.destino, 'rb') as f:
            self.assertEqual(original, f.read(), 'o universo existente foi reescrito')
        self.assertEqual(mtime, os.stat(self.destino).st_mtime_ns,
                         'o universo existente foi tocado')
        self.assertEqual(['UNIVERSO-CONTAS-V1.json'], os.listdir(self.saida),
                         'sobrou um temporario ao lado do universo')

    def test_em_processo_novo_a_linha_de_comando_tambem_recusa_sem_escrever(self):
        """O `main()` de verdade, noutro interpretador — nao so o chamado daqui."""
        guiao = os.path.join(self.tmp, 'guiao.py')
        with io.open(guiao, 'w', encoding='utf-8') as f:
            f.write(
                'import sys\n'
                'sys.path.insert(0, %r)\n'
                'import _gavetas\n'
                'import comunicacao_universo as uni\n'
                'sys.exit(uni.main(caminho=%r, destino=%r))\n'
                % (ROOT, self.ausente, self.destino))
        r = subprocess.run([sys.executable, guiao], capture_output=True, text=True,
                           timeout=120, cwd=ROOT,
                           env=dict(os.environ, PYTHONIOENCODING='utf-8'))
        self.assertEqual(2, r.returncode, r.stderr[-800:])
        self.assertIn('NAO_DERIVADO', r.stderr)
        self.assertFalse(os.path.exists(self.saida))
        self.assertEqual('', r.stdout.strip(),
                         'a recusa imprimiu um resumo como se tivesse derivado')


class OCrosswalkIlegivelRecusa(UmaCasaDeMentira):

    def test_json_partido(self):
        p = self._crosswalk(None, bruto='{"PROVED_POR_GRUPO": {"A": 1')
        with self.assertRaises(uni.CrosswalkIlegivel):
            uni.montar(p)

    def test_formas_erradas_cada_uma_com_a_sua_recusa(self):
        casos = {
            'lista em vez de objecto': [1, 2, 3],
            'objecto sem PROVED_POR_GRUPO': {'OUTRA_COISA': {'A': 1}},
            'PROVED_POR_GRUPO nao e objecto': {'PROVED_POR_GRUPO': [['A', 1]]},
            'PROVED_POR_GRUPO vazio': {'PROVED_POR_GRUPO': {}},
            'contagem em texto': {'PROVED_POR_GRUPO': {'A': '47'}},
            'contagem booleana': {'PROVED_POR_GRUPO': {'A': True}},
            'contagem negativa': {'PROVED_POR_GRUPO': {'A': -1}},
            'contagem fraccionaria': {'PROVED_POR_GRUPO': {'A': 1.5}},
            'grupo sem nome': {'PROVED_POR_GRUPO': {'': 3}},
            # red team 2026-09-17: todos a zero passava e montava um lote entre iguais a nada
            'todos os grupos a zero': {'PROVED_POR_GRUPO': {'A': 0, 'B': 0, 'C': 0}},
        }
        self.assertEqual(10, len(casos), 'o denominador desta prova mudou sem se dizer')
        for i, (nome, corpo) in enumerate(casos.items()):
            with self.subTest(caso=nome):
                p = self._crosswalk(corpo, nome='caso-%d.json' % i)
                with self.assertRaises(uni.CrosswalkIlegivel):
                    uni.montar(p)

    def test_ilegivel_tambem_nao_escreve(self):
        p = self._crosswalk({'PROVED_POR_GRUPO': {}})
        antes = _arvore(self.tmp)
        with unittest.mock.patch('sys.stderr', io.StringIO()) as err:
            codigo = uni.main(caminho=p, destino=self.destino)
        self.assertEqual(2, codigo)
        self.assertIn('CrosswalkIlegivel', err.getvalue())
        self.assertEqual(antes, _arvore(self.tmp))


class ComUmCrosswalkLegivelMontaEEscreve(UmaCasaDeMentira):

    def test_a_fixture_monta_um_tabuleiro_inteiro(self):
        u = uni.montar(FIXTURE)
        self.assertEqual(uni.TAMANHO_DO_PRIMEIRO_LOTE, len(u['FIRST_BATCH_COMPANIES']))
        self.assertEqual(uni.TAMANHO_DO_PRIMEIRO_LOTE * len(uni.PAISES), u['ANCHOR_CELLS'])
        self.assertEqual(uni.TAMANHO_DO_PRIMEIRO_LOTE * len(uni.PAISES) * len(uni.PLATAFORMAS),
                         u['ACCOUNT_CELLS'])
        self.assertEqual(u['ACCOUNT_CELLS'], len(u['CELLS']))
        self.assertGreater(u['ACCOUNT_CELLS'], 0)

    def test_a_ordem_e_por_pares_e_o_empate_desfaz_se_pelo_nome(self):
        # Na fixture B e C empatam em 7 pares: B vem antes de C, e ambos depois de A (9).
        ordem = uni.grupos_do_crosswalk(FIXTURE)
        self.assertEqual(['GRUPO-FIXTURE-A', 'GRUPO-FIXTURE-B', 'GRUPO-FIXTURE-C'],
                         [g for g, _ in ordem[:3]])
        self.assertEqual(ordem[1][1], ordem[2][1], 'a fixture perdeu o empate que prova a ordem')

    def test_a_linha_de_comando_escreve_o_que_montar_devolve(self):
        """A escrita NAO e atomica de proposito (ver main()): e `open(destino, 'w')`, a
        forma que o scanner do System Map segue. O que se prova e o conteudo e a ausencia
        de rasto — nao a atomicidade."""
        with unittest.mock.patch('sys.stdout', io.StringIO()) as out:
            codigo = uni.main(caminho=FIXTURE, destino=self.destino)
        self.assertEqual(0, codigo)
        self.assertIn('contas autorizadas a coletar: 0', out.getvalue())
        with io.open(self.destino, encoding='utf-8') as f:
            self.assertEqual(uni.montar(FIXTURE), json.load(f))
        self.assertEqual(['UNIVERSO-CONTAS-V1.json'], os.listdir(self.saida))

    def test_a_escrita_vem_DEPOIS_de_montar_e_na_forma_que_o_mapa_le(self):
        """O scanner do System Map segue `destino = os.path.join(SAIDA, 'X.json')` ate
        `open(destino, 'w')`. E a ordem importa: montar primeiro, escrever depois."""
        import ast
        with io.open(os.path.join(ROOT, 'regras', 'comunicacao_universo.py'),
                     encoding='utf-8') as f:
            arvore = ast.parse(f.read())
        main = next(n for n in arvore.body
                    if isinstance(n, ast.FunctionDef) and n.name == 'main')
        linha_montar = linha_open = None
        for no in ast.walk(main):
            if isinstance(no, ast.Call):
                if getattr(no.func, 'id', '') == 'montar':
                    linha_montar = linha_montar or no.lineno
                if (getattr(no.func, 'id', '') == 'open' and no.args
                        and isinstance(no.args[0], ast.Name) and no.args[0].id == 'destino'):
                    linha_open = no.lineno
        self.assertIsNotNone(linha_montar, 'main() deixou de montar')
        self.assertIsNotNone(linha_open, "main() deixou de escrever por open(destino, 'w')")
        self.assertLess(linha_montar, linha_open, 'a escrita passou a frente da montagem')

    def test_a_linha_de_comando_nao_deixa_temporario(self):
        with unittest.mock.patch('sys.stdout', io.StringIO()):
            self.assertEqual(0, uni.main(caminho=FIXTURE, destino=self.destino))
        self.assertEqual(['UNIVERSO-CONTAS-V1.json'], os.listdir(self.saida))


class AFixtureEFixtureEOPadraoContinuaCanonico(unittest.TestCase):

    def test_a_fixture_declara_se_e_nao_e_o_crosswalk(self):
        with io.open(FIXTURE, encoding='utf-8') as f:
            d = json.load(f)
        self.assertIn('FIXTURE', d.get('_O_QUE_ISTO_E', ''))
        self.assertIn('NAO E O COMPETITOR-CROSSWALK CANONICO', d['_O_QUE_ISTO_E'])
        for grupo in d['PROVED_POR_GRUPO']:
            self.assertIn('FIXTURE', grupo,
                          'um grupo da fixture parece uma empresa real: %r' % grupo)
        self.assertNotEqual(os.path.normcase(os.path.abspath(FIXTURE)),
                            os.path.normcase(os.path.abspath(uni.CROSSWALK)))

    def test_o_padrao_do_modulo_continua_a_ser_o_caminho_canonico(self):
        self.assertEqual(os.path.join(uni.SAMPLES, 'COMPETITOR-CROSSWALK.json'), uni.CROSSWALK)
        self.assertTrue(uni.CROSSWALK.startswith(os.path.join(uni.ROOT, 'data', 'samples')))

    def test_sem_o_crosswalk_no_repositorio_o_padrao_recusa(self):
        """No repositorio o crosswalk nao existe (nunca esteve no Git). Se alguem o tiver
        no disco, esta prova nao mede a recusa — e diz isso em vez de passar por vazio."""
        if os.path.exists(uni.CROSSWALK):
            self.skipTest('ha um COMPETITOR-CROSSWALK.json local em %s; a recusa por '
                          'ausencia nao se mede aqui' % uni.CROSSWALK)
        with self.assertRaises(uni.CrosswalkAusente):
            uni.montar()

    def test_o_test_comunicacao_passa_a_fixture_pelo_parametro_caminho(self):
        with io.open(os.path.join(HERE, 'test_comunicacao.py'), encoding='utf-8') as f:
            fonte = f.read()
        self.assertIn('uni.montar(FIXTURE_CROSSWALK)', fonte)
        # So CODIGO conta: a prosa do comentario pode citar `uni.montar()` para explicar
        # o defeito. Uma linha que nao e comentario e chama sem caminho e a regressao.
        codigo = [l for l in fonte.splitlines() if l.strip() and not l.lstrip().startswith('#')]
        chamadas_sem_caminho = [l for l in codigo if re.search(r'uni\.montar\(\s*\)', l)]
        self.assertEqual([], chamadas_sem_caminho,
                         'test_comunicacao voltou a depender do crosswalk do acervo')


if __name__ == '__main__':
    unittest.main(verbosity=2)
