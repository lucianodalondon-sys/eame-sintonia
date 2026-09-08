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

    def test_fronteira_declarada_exige_vestigio_medivel(self):
        """O estado FECHADA_COM_FRONTEIRA_DECLARADA nao pode virar porta.

        Seria a saida mais elegante que existe: escrever uma frase a explicar
        por que o conteudo nao atravessa, e colher fechado. Nao e, porque o
        estado nao deriva da frase — deriva da assinatura mecanica de uma
        fronteira deliberada. Este teste exige os quatro vestigios.

            UMA FRONTEIRA DELIBERADA DEIXA VESTIGIO MEDIVEL.
            UM ESQUECIMENTO DEIXA SO SILENCIO.
        """
        for fam in self.f['FAMILIAS']:
            if fam['ESTADO'] != 'FECHADA_COM_FRONTEIRA_DECLARADA':
                continue
            with self.subTest(familia=fam['FAMILIA']):
                e = fam['CHEGOU'].get('ESCADA') or {}
                self.assertTrue(fam.get('O_TEXTO_NAO_ATRAVESSA_POR_DECISAO'),
                                'fechada por decisao sem a decisao escrita')
                self.assertGreater(e.get('REGISTOS', 0), 0,
                                   'nenhum registo chegou: nao ha fronteira, ha silencio')
                self.assertEqual(5, len(e.get('CAMPOS_DE_ESTADO_ENCONTRADOS', [])),
                                 'a escada tem cinco degraus e todos tem de atravessar')
                self.assertGreater(e.get('COM_TEXT_SHA256', 0), 0,
                                   'sem SHA nao ha como voltar ao texto que ficou')
                self.assertGreater(
                    fam['CHEGOU'].get('CHARS_DECLARADOS_PELA_ORIGEM', 0), 0,
                    'sem a contagem da origem, o que nao atravessou nao tem tamanho')

    def test_rotulo_de_estado_nunca_conta_como_texto(self):
        """A confusao que este medidor ja cometeu, fechada.

        A primeira versao contou «true» e «INCLUDED» como fala transcrita e
        publicou 809 caracteres de texto que nao existia. E a propria lei do
        repositorio: TRANSCRIPT_EXISTS nao e TRANSCRIPT_USED_AS_EVIDENCE.
        """
        for fam in self.f['FAMILIAS']:
            e = fam['CHEGOU'].get('ESCADA')
            if not e:
                continue
            with self.subTest(familia=fam['FAMILIA']):
                for campo in fam['CHEGOU'].get('CAMPOS_DE_TEXTO_ENCONTRADOS', []):
                    self.assertNotIn(campo.split('.')[-1],
                                     e.get('CAMPOS_DE_ESTADO_ENCONTRADOS', []),
                                     'campo de estado contado como campo de texto')

    def test_degrau_aberto_nao_bloqueia_a_fronteira(self):
        """Duas perguntas, nao uma.

        A fronteira pergunta se o que se coletou chega. O degrau pergunta se o
        que chegou e usado. Colapsa-las faria a coleta refem do motor.
        """
        abertas = set(self.f['FAMILIAS_ABERTAS'])
        for g in self.f.get('DEGRAUS_ABERTOS', []):
            with self.subTest(familia=g['FAMILIA']):
                self.assertTrue(g['DONO'], 'degrau aberto sem dono')
                if g['FAMILIA'] not in abertas:
                    self.assertTrue(g['DEGRAU'],
                                    'degrau aberto sem dizer qual e')

    def test_toda_familia_aberta_tem_acao_minima_e_dono(self):
        for fam in self.f['FAMILIAS']:
            with self.subTest(familia=fam['FAMILIA']):
                if not fam['ESTADO'].startswith('FECHADA'):
                    self.assertTrue(fam['ACAO_MINIMA'])
                    self.assertTrue(fam['DONO_DA_ACAO'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
