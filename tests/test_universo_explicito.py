#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O UNIVERSO VEM DO PEDIDO — e nunca de um default silencioso.

    py -m unittest test_universo_explicito

A PERGUNTA
----------
`SOURCE TERRITORY != ADMISSION UNIVERSE.`

Uma fonte tem **território**; um documento responde a uma **pergunta** (item,
universo). São duas coisas diferentes com o mesmo nome, e a casa já o escreveu
antes desta missão (know-how §50.7). O defeito era outro: a rota partilhada
`coleta/rota_forward_documento.py` trazia `UNIVERSO_PADRAO = 'T3'`, e quem a
chamasse sem declarar universo recebia **T3** — uma decisão de negócio tomada
por omissão, dentro de um caminho partilhado.

MEDIDO, e é o que obriga esta suíte: um vídeo público do LinkedIn, trazido por
uma fonte do território T8, foi julgado contra **T3**. A porta respondeu
`NAO_SEI` — «nao encontrei nada de «T3»» — e o relatório leu-se como se o
conteúdo tivesse falhado. Não falhou nada: **a pergunta nunca foi feita.**

    A AUTORIDADE JÁ DIZIA O CERTO ANTES DESTA CORREÇÃO
    `ADMISSION_REMAINS_UNIVERSE_OWNER = YES` · `BIBLE_CHANGE_REQUIRED = NO`
    «o orquestrador pergunta UM universo por corrida (`pela_porta(itens,
    universo, run_id)`, o `alvo` do pedido)» — know-how §51.5.

    O DONO DA RÉGUA É A ADMISSÃO. O DECLARANTE DO UNIVERSO É O PEDIDO.

Estes testes não tocam rede, banco nem disco: medem a DECLARAÇÃO, que é onde a
decisão vive.
"""
import os
import sys
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao as adm                                          # noqa: E402
import orquestrador as orq                                      # noqa: E402
from coleta import rota_forward_documento as m2                  # noqa: E402
from pedido import Pedido, PedidoInvalido                      # noqa: E402

#: Um documento LEGÍVEL, com origem e linhagem — para que a única pergunta que
#: possa falhar seja «pertence ao universo?», e não os portões de antes.
DOC = {
    'id': 'TESTE-UNIVERSO-1',
    'texto': ('boletim agrometeorologico com avversita e sintomo de peronospora '
              'na cultura do olivo'),
    'artifact_type': 'DERIVED',
    'source_id': 'IT-T3-001',
    'parent_sha256': 'a' * 64,
    'parent_artifact_id': 1,
    'url': 'https://exemplo.invalid/documento',
    'captured_at': '2026-09-18T00:00:00Z',
}


def _decisao_real(item, universo):
    """A porta a decidir de verdade — pura, sem livro e sem Sala."""
    return adm.decidir(dict(item), universo, corrida='TESTE-UNIVERSO')


def _universo_que_a_porta_recebeu(universo, item=None):
    """O que o ORQUESTRADOR entrega à porta — medido com um espião.

    `pela_porta` escreve no livro e pousa na Sala; um teste não suja nenhum dos
    dois. O que se mede aqui é o valor que ATRAVESSA, que é exactamente o que a
    missão manda provar.
    """
    visto = []

    def espiar(it, u, corrida='NAO SEI'):
        visto.append(u)
        return adm.Decisao(item='ESPIADO', universo=u,
                           resultado=adm.NAO_SE_APLICA, regra='espiado',
                           motivo='espiado', evidencia={}, corrida=corrida)

    with mock.patch.object(adm, 'decidir', espiar), \
            mock.patch.object(adm, 'escrever', lambda *a, **k: 0), \
            mock.patch.object(orq.espera, 'pousar',
                              lambda *a, **k: {'FICHEIRO': 'TESTE.json',
                                               'ESTADO': 'PASSED'}):
        orq.pela_porta([dict(item or DOC)], universo, 'RUN-TESTE-UNIVERSO')
    return visto[0] if visto else None


class OSilencioFoiEliminado(unittest.TestCase):

    def test_1_o_default_silencioso_deixou_de_existir(self):
        """`UNIVERSO_PADRAO = 'T3'` era a causa. Não pode voltar por descuido."""
        self.assertFalse(
            hasattr(m2, 'UNIVERSO_PADRAO'),
            'a rota voltou a ter um universo por omissão — e um default '
            'silencioso é uma decisão de negócio que ninguém tomou')

    def test_2_admitir_sem_universo_nao_compila_em_T3(self):
        """`universo` é palavra-chave OBRIGATÓRIA: não há por onde herdar T3."""
        with self.assertRaises(TypeError) as ctx:
            m2.admitir(object(), unidade={}, run_id='R', conteudo_id=1)
        self.assertIn('universo', str(ctx.exception))

    def test_3_universo_vazio_placeholders_e_ausencia_levantam_com_nome(self):
        """`''`, `NAO SEI` e `None` não são universos — e têm um nome só."""
        for vazio in (None, '', '   ', 'NAO SEI', 'NÃO SEI', 'NOT_KNOWN'):
            with self.subTest(universo=repr(vazio)):
                with self.assertRaises(m2.UniversoNaoDeclarado):
                    m2.universo_declarado(vazio)

    def test_4_universo_declarado_normaliza_sem_inventar(self):
        self.assertEqual(m2.universo_declarado('t3'), 'T3')
        self.assertEqual(m2.universo_declarado(' T9 '), 'T9')


class OPedidoEscolheOUniverso(unittest.TestCase):
    """A cadeia real: `Pedido.alvo` → `pela_porta(p.alvo)` → `decidir(item, u)`."""

    def test_5_pedido_T3_a_porta_recebe_T3(self):
        self.assertEqual(_universo_que_a_porta_recebeu('T3'), 'T3')

    def test_6_pedido_T9_a_porta_recebe_T9(self):
        self.assertEqual(_universo_que_a_porta_recebeu('T9'), 'T9')

    def test_7_pedido_T8_a_porta_recebe_T8(self):
        """T8 não tem régua — mas o universo CHEGA lá, e é isso que se mede.

        O que NÃO pode acontecer é chegar T3: seria a pergunta errada com ar de
        resposta.
        """
        self.assertEqual(_universo_que_a_porta_recebeu('T8'), 'T8')

    def test_8_pedido_sem_universo_nao_recebe_T3(self):
        """Ninguém declara → ninguém herda: o orquestrador entrega o que recebeu."""
        self.assertIsNone(_universo_que_a_porta_recebeu(None))

    def test_9_a_porta_com_universo_ausente_diz_o_nome_da_falta(self):
        d = _decisao_real(DOC, None)
        self.assertEqual(d.resultado, adm.NAO_SE_APLICA)
        self.assertIn('UNIVERSO_NAO_DECLARADO', d.motivo)
        self.assertNotEqual(d.resultado, adm.SIM)

    def test_10_um_pedido_nao_existe_sem_alvo(self):
        """A porta fechada mais a montante: sem assunto não há pedido."""
        for sem_alvo in ('', '   ', 'assunto que nao existe em territorio nenhum'):
            with self.subTest(alvo=repr(sem_alvo)):
                with self.assertRaises(PedidoInvalido):
                    Pedido(alvo=sem_alvo)

    def test_11_o_alvo_do_pedido_e_o_universo_que_a_porta_recebe(self):
        for alvo in ('T3', 'T4', 'T5', 'T7', 'T9'):
            with self.subTest(alvo=alvo):
                p = Pedido(alvo=alvo)
                self.assertEqual(p.alvo, alvo)
                self.assertEqual(_universo_que_a_porta_recebeu(p.alvo), alvo)


class ATerritorioDaFonteNaoEscolheOUniverso(unittest.TestCase):
    """O erro que originou esta missão, virado em quatro testes."""

    def test_12_fonte_T8_com_pedido_T3_continua_T3(self):
        d = _decisao_real(dict(DOC, source_id='ES-T8-002'), 'T3')
        self.assertEqual(d.universo, 'T3',
                         'a fonte passou a escolher o universo — é exactamente '
                         'o defeito que esta missão corrige')

    def test_13_fonte_T9_com_pedido_T3_continua_T3(self):
        self.assertEqual(_decisao_real(dict(DOC, source_id='IT-T9-001'),
                                       'T3').universo, 'T3')

    def test_14_fonte_T3_com_pedido_T9_continua_T9(self):
        d = _decisao_real(dict(DOC, source_id='IT-T3-001'), 'T9')
        self.assertEqual(d.universo, 'T9',
                         'o território da fonte não promove nem rebaixa o pedido')

    def test_15_a_decisao_guarda_o_universo_que_lhe_foi_pedido(self):
        """COL-LAW-042: a decisão é por par (item, universo) — e diz qual."""
        for u in ('T3', 'T8', 'T9', 'ZZ'):
            with self.subTest(universo=u):
                self.assertEqual(_decisao_real(DOC, u).universo, u)

    def test_16_nada_fora_do_pedido_alimenta_o_universo(self):
        """Red team no CÓDIGO: a rota não pode derivar universo de outro sítio.

        O scan é feito sobre CÓDIGO, não sobre prosa: um comentário que explica
        o defeito antigo («aqui esteve UNIVERSO_PADRAO = T3») é documentação
        honesta, e um teste que reprovasse por causa dela seria um teste que
        proíbe a casa de contar a sua própria história.
        """
        import ast
        fonte = open(os.path.join(RAIZ, 'coleta', 'rota_forward_documento.py'),
                     encoding='utf-8').read()
        arvore = ast.parse(fonte)
        for no in ast.walk(arvore):                     # tira docstrings
            if isinstance(no, (ast.Module, ast.FunctionDef, ast.ClassDef,
                               ast.AsyncFunctionDef)):
                corpo = no.body
                if (corpo and isinstance(corpo[0], ast.Expr)
                        and isinstance(corpo[0].value, ast.Constant)
                        and isinstance(corpo[0].value.value, str)):
                    corpo.pop(0)
        codigo = ast.unparse(arvore)
        self.assertNotIn('UNIVERSO_PADRAO', codigo,
                         'a rota voltou a ter universo por omissão')
        for derivacao in ('universo = unidade.get', 'universo = platform',
                          'universo = item.get', 'universo = source_id',
                          'universo = SOURCE_ID'):
            self.assertNotIn(derivacao, codigo,
                             'o universo passou a ser derivado de fora do pedido')


class OCanarioPodeSerMaisDeUmaPergunta(unittest.TestCase):
    """Um item, vários universos — o modelo suporta, e tem de continuar a suportar."""

    def test_17_o_mesmo_item_responde_diferente_por_universo(self):
        item = dict(DOC, texto='praga e doenca com sintoma de peronospora')
        respostas = {u: _decisao_real(item, u).resultado
                     for u in ('T3', 'T5', 'T9')}
        self.assertEqual(respostas['T3'], adm.SIM,
                         'o texto é claramente de praga e doença')
        self.assertTrue(
            any(v != respostas['T3'] for v in respostas.values()),
            'nenhum universo discordou — então o par (item, universo) não está '
            'a ser respeitado')


if __name__ == '__main__':
    unittest.main(verbosity=2)
