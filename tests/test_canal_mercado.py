"""O CONTRATO DA FONTE DE VENDA DECLARADA — e os oito jeitos de ela mentir.

Teste que nunca viu vermelho nao e teste. Aqui a fonte e CORROMPIDA de proposito, em
memoria e nunca no disco, e cada corrupcao tem de reprovar pelo motivo certo:

  · HTML devolvido com HTTP 200 no lugar do CSV          -> FAILED
  · lista vazia                                          -> FAILED (nunca «zero vendas»)
  · coluna do contrato removida                          -> FAILED
  · acento no cabecalho (`Quantita` vs `Quantità`)       -> HEALTHY (nao pode reprovar fonte sa)
  · rodape da propria fonte                              -> separado, nao vira dado nem defeito
  · provincia de outra regiao                            -> nao entra como dado
  · decimal com PONTO                                    -> 51401.35, e nunca 51.401.350
  · provincia do Veneto sem nenhuma linha                -> DEGRADED, com o motivo escrito

O defeito do separador decimal nao e hipotetico: a leitura manual anterior a este coletor
tratou o ponto como separador de milhar e inflou o volume do Veneto em mil vezes.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'coleta'))
sys.path.insert(0, ROOT)
import canal_mercado as cm  # noqa: E402

CAB = 'Provincia di vendita,N. Reg. , Prodotto fitosanitario venduto*,"Quantità \n(Kg o litri)"\n'
LINHAS = 'BL,1850,IDRORAME FLOW,8\nVR,14709,ISOMATE A/OFM,51401.35\nTV,1583,MICROTHIOL DISPERSS,651361\n'
RODAPE = ('* non presente se è stato utilizzato il caricamento da file,,,\n'
          '(fonte dati: Autorità regionale competente art. 16 D.Lgs 150/2012),,,\n')


def sao():
    return (CAB + LINHAS + RODAPE).encode('utf-8')


class TestContratoDaFonte(unittest.TestCase):

    def test_a_fonte_sa_passa(self):
        saude, motivos, dados, provincias, rodape = cm.conferir(sao())
        self.assertEqual('DEGRADED', saude, 'amostra de teste so tem 3 provincias: DEGRADED e o certo')
        self.assertTrue(any('sem nenhuma linha' in m for m in motivos))
        self.assertEqual(3, len(dados))
        self.assertEqual(['BL', 'TV', 'VR'], provincias)
        self.assertEqual(2, len(rodape), 'o rodape da fonte tem de ficar separado do dado')

    def test_acento_no_cabecalho_nao_reprova_fonte_sa(self):
        """`Quantità` e `Quantita` sao o mesmo campo. Reprovar aqui seria matar a fonte."""
        corpo = (CAB.replace('Quantità', 'Quantita') + LINHAS).encode('utf-8')
        saude, _, dados, _, _ = cm.conferir(corpo)
        self.assertNotEqual('FAILED', saude)
        self.assertEqual(3, len(dados))

    def test_html_com_200_reprova(self):
        corpo = b'<!doctype html><html><body>Access denied</body></html>'
        saude, motivos, _, _, _ = cm.conferir(corpo)
        self.assertEqual('FAILED', saude)
        self.assertIn('HTML', ' '.join(motivos))

    def test_lista_vazia_e_falha_nunca_zero_vendas(self):
        saude, motivos, dados, _, _ = cm.conferir(CAB.encode('utf-8'))
        self.assertEqual('FAILED', saude)
        self.assertEqual([], dados)
        self.assertTrue(any('vazia' in m for m in motivos))

    def test_coluna_do_contrato_removida_reprova(self):
        sem = 'Provincia di vendita,N. Reg. , Prodotto fitosanitario venduto*\nBL,1850,IDRORAME,8\n'
        saude, motivos, _, _, _ = cm.conferir(sem.encode('utf-8'))
        self.assertEqual('FAILED', saude)
        self.assertTrue(any('campo do contrato ausente' in m for m in motivos))

    def test_provincia_de_outra_regiao_nao_vira_dado(self):
        corpo = (CAB + LINHAS + 'MI,1850,IDRORAME FLOW,10\n').encode('utf-8')
        _, _, dados, provincias, rodape = cm.conferir(corpo)
        self.assertNotIn('MI', provincias)
        self.assertIn('MI', [r[0] for r in rodape])

    def test_rodape_demais_deixa_de_ser_rodape(self):
        corpo = (CAB + LINHAS + RODAPE * 4).encode('utf-8')
        saude, motivos, _, _, _ = cm.conferir(corpo)
        self.assertEqual('DEGRADED', saude)
        self.assertTrue(any('rodape demais' in m for m in motivos))

    def test_o_ponto_e_decimal_e_nao_separador_de_milhar(self):
        self.assertEqual(51401.35, cm._quantidade('51401.35'))
        self.assertEqual(8.0, cm._quantidade('8'))
        self.assertIsNone(cm._quantidade(''))
        self.assertIsNone(cm._quantidade('n/d'))

    def test_todo_descarte_tem_motivo_em_palavras(self):
        for chave, frase in cm.MOTIVO_DA_RECUSA.items():
            self.assertRegex(chave, r'^[A-Z_]+$')
            self.assertGreater(len(frase), 25, '%s: motivo curto demais para explicar nada' % chave)

    def test_os_avisos_viajam_com_o_dado(self):
        """Volume nao e valor, e ausencia nao e ausencia: os dois avisos sao texto obrigatorio."""
        self.assertIn('NAO e quota de mercado', cm.AVISO_VOLUME)
        self.assertIn('sem venda declarada', cm.AVISO_AUSENCIA)


class TestSaidaGravada(unittest.TestCase):
    """As tabelas geradas carregam o aviso e a procedencia — ou nao valem nada."""

    @classmethod
    def setUpClass(cls):
        import json
        cls.dir = os.path.join(ROOT, 'data', 'samples', 'IT-VENETO-CANALE')
        cam = os.path.join(cls.dir, 'MANIFESTO-DAS-TABELAS.json')
        cls.man = json.load(open(cam, encoding='utf-8')) if os.path.exists(cam) else None

    def test_o_manifesto_existe_e_declara_a_fonte(self):
        self.assertIsNotNone(self.man, 'sem MANIFESTO-DAS-TABELAS: rode py coleta/canal_mercado.py')
        self.assertIn('IT-T10-001', self.man['FONTES'])
        self.assertIn('IT-T4-001', self.man['FONTES'])

    def test_a_chave_do_cruzamento_esta_escrita(self):
        self.assertIn('num_registrazione', self.man['CHAVE_DO_CRUZAMENTO'])

    def test_o_que_a_fonte_nao_prova_esta_escrito(self):
        texto = ' '.join(self.man['O_QUE_NAO_PROVA'])
        for proibido in ('quem comprou', 'preco', 'quota em valor'):
            self.assertIn(proibido, texto)

    def test_o_descarte_foi_contado_por_motivo(self):
        self.assertIn('DESCARTE_POR_MOTIVO', self.man['QA'])
        self.assertEqual(self.man['QA']['DESCARTADAS'],
                         sum(self.man['QA']['DESCARTE_POR_MOTIVO'].values()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
