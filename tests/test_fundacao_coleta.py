#!/usr/bin/env python3
"""Provas de que a fundacao da coleta nao fecha por edicao de escopo.

O teste que importa aqui nao e o que confere o resultado de hoje. E o que
impede a saida facil de amanha: tirar o pilar que incomoda da lista e colher
SIM sem que nenhuma familia tenha atravessado a ingestao.

Mesmo formato, e pela mesma razao, de tests/test_portoes_eame.py — que fecha
a saida equivalente no portao da entrada.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import fundacao_coleta as F                                       # noqa: E402


class TestASaidaFacilEstaFechada(unittest.TestCase):

    def test_a_travessia_e_pilar_da_fundacao(self):
        """Bastaria tirar TRAVESSIA da lista para a fundacao virar SIM.

        Sem esse pilar, COLLECTION_FOUNDATION_CLOSED responderia apenas
        «podemos comecar a coletar» — e o que a missao pergunta e se o que
        se coleta chega. Esta edicao reprova.
        """
        self.assertIn('TRAVESSIA', F.PILARES,
                      'tirar TRAVESSIA seria escolher o escopo depois de ver '
                      'o resultado')

    def test_a_entrada_e_pilar_da_fundacao(self):
        """A travessia sozinha tambem nao basta.

        Um funil que entrega, alimentado por coleta que nao sabe provar
        origem, identidade nem lugar de fato, entrega dividas mais depressa.
        """
        self.assertIn('ENTRADA', F.PILARES)

    def test_a_preservacao_e_pilar_da_fundacao(self):
        self.assertIn('PRESERVACAO', F.PILARES)

    def test_todo_pilar_diz_de_que_medidor_deriva(self):
        """Um pilar sem medidor nomeado e uma frase, e frases nao medem."""
        for nome, p in F.PILARES.items():
            with self.subTest(pilar=nome):
                self.assertTrue(p.get('MEDIDOR'), '%s nao nomeia medidor' % nome)
                self.assertTrue(p.get('DERIVA_DE'), '%s nao diz o que le' % nome)
                caminho = os.path.join(RAIZ, p['MEDIDOR'])
                self.assertTrue(os.path.exists(caminho),
                                'o medidor de %s nao existe: %s' % (nome, p['MEDIDOR']))


class TestNaoMedidoNaoFecha(unittest.TestCase):
    """NAO MEDIDO nao e zero, e NAO MEDIDO nao e fechado.

    A linhagem ja publicou ZERO no lugar de NAO MEDIDO DAQUI uma vez
    (RELATORIO-PORTAO-DE-ENTRADA-DA-COLETA, seccao I). A versao para cima
    do mesmo erro seria contar um pilar nao medido como fechado.
    """

    @classmethod
    def setUpClass(cls):
        cls.d = F.monta()

    def test_sim_exige_todo_pilar_fechado(self):
        fechada = self.d['COLLECTION_FOUNDATION_CLOSED'] == 'SIM'
        abertos = [n for n, p in self.d['PILARES'].items()
                   if p['ESTADO'] != 'FECHADO']
        self.assertEqual(fechada, not abertos,
                         'a conjuncao discorda dos pilares: %s' % abertos)

    def test_pilar_nao_medido_nao_conta_como_fechado(self):
        for nome, p in self.d['PILARES'].items():
            with self.subTest(pilar=nome):
                if p['MEDIDO'] == 'NAO':
                    self.assertNotEqual(
                        'FECHADO', p['ESTADO'],
                        '%s foi dado por fechado sem ter sido medido' % nome)

    def test_todo_pilar_aberto_diz_o_que_o_bloqueia(self):
        for nome, p in self.d['PILARES'].items():
            with self.subTest(pilar=nome):
                if p['ESTADO'] != 'FECHADO':
                    self.assertTrue(p['BLOQUEADORES'],
                                    '%s aberto sem dizer o que o bloqueia' % nome)
                else:
                    self.assertEqual([], p['BLOQUEADORES'],
                                     '%s fechado com bloqueador' % nome)

    def test_o_que_falta_nomeia_dono(self):
        """Uma lacuna sem dono nao e trabalho de ninguem."""
        for a in self.d['O_QUE_FALTA_PARA_SIM']:
            with self.subTest(pilar=a['PILAR']):
                self.assertTrue(a['DONO'])


class TestAFronteiraNaoInventaOLadoQueNaoMede(unittest.TestCase):
    """O artefato da fronteira nao pode declarar medido o que nao mediu."""

    @classmethod
    def setUpClass(cls):
        import json
        caminho = os.path.join(RAIZ, 'data', 'samples',
                               'FRONTEIRA-ACERVO-PACOTE.json')
        if not os.path.exists(caminho):
            raise unittest.SkipTest('artefato da fronteira ausente')
        with open(caminho, encoding='utf-8') as h:
            cls.f = json.load(h)

    def test_o_lado_do_acervo_entra_como_alegacao(self):
        """O acervo nao esta neste repositorio. Nenhum numero dele e medicao.

        Se um dia entrar, este teste reprova — e reprova certo: quem trouxer
        o acervo para ca tem de trocar tambem a origem da alegacao por um
        medidor, em vez de deixar o numero antigo passar por medido.
        """
        for fam in self.f['FAMILIAS']:
            with self.subTest(familia=fam['FAMILIA']):
                self.assertEqual('NAO', fam['PARTIU']['MEDIDO_DAQUI'])
                self.assertTrue(fam['PARTIU']['ORIGEM_DA_ALEGACAO'],
                                'alegacao sem origem escrita')
                self.assertTrue(fam['PARTIU']['PORQUE_NAO'])

    def test_perda_so_e_quantificavel_com_os_dois_lados_medidos(self):
        for fam in self.f['FAMILIAS']:
            with self.subTest(familia=fam['FAMILIA']):
                dois = (fam['PARTIU']['MEDIDO_DAQUI'] == 'SIM'
                        and fam['CHEGOU']['MEDIDO_DAQUI'] == 'SIM')
                self.assertEqual(fam['PERDA_QUANTIFICAVEL'] == 'SIM', dois,
                                 'subtrair medicao de alegacao produz um numero '
                                 'com cara de facto')

    def test_toda_familia_aberta_tem_acao_minima_e_dono(self):
        for fam in self.f['FAMILIAS']:
            with self.subTest(familia=fam['FAMILIA']):
                if fam['ESTADO'] != 'FECHADA':
                    self.assertTrue(fam['ACAO_MINIMA'])
                    self.assertTrue(fam['DONO_DA_ACAO'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
