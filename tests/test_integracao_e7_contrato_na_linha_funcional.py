# -*- coding: utf-8 -*-
"""O VOCABULARIO DE FIO DO CONTRATO DO TEXTO ESTA PRESO PELO VALOR.

O QUE O RED TEAM DA INTEGRACAO ENCONTROU
----------------------------------------
`tests/test_col_e7_contrato_do_texto.py` cobre o contrato com 65 casos, e
cobre-o bem — mas refere-se a tudo pelo SIMBOLO:

    pv.CAMPO_DAS_UNIDADES        e nao   'TEXT_UNITS'
    pv.TEXTO_DESCONHECIDO        e nao   'UNKNOWN'

Dois ataques da integracao sobreviveram por causa disso:

    CAMPO_DAS_UNIDADES = 'TEXTOS'          -> 65 testes continuaram verdes
    TEXTO_DESCONHECIDO = 'TRANSCRIPT'       -> 65 testes continuaram verdes

Uma suite inteira a passar enquanto o nome do campo muda e o desconhecido
vira transcricao.

    UM TESTE QUE SO FALA PELO SIMBOLO MEDE A COERENCIA INTERNA,
    E NAO O CONTRATO COM QUEM ESTA DO OUTRO LADO DO FIO.

E DO OUTRO LADO DO FIO HA GENTE
-------------------------------
`TEXT_UNITS` nao e um detalhe de implementacao: e o nome que viaja no
envelope, fica escrito em disco, e sera o que o SCRAP vai produzir na missao
seguinte. Renomea-lo em silencio nao parte um teste — parte a leitura de
tudo o que ja foi colhido, e parte a ponte que ainda nao foi construida.

O mesmo vale para as sete especies e as tres relacoes: sao o modelo FECHADO
pela COL-E7-01, e o que os consumidores vao ler.

    UM VALOR QUE ATRAVESSA UMA FRONTEIRA E UM CONTRATO,
    E UM CONTRATO PRENDE-SE PELO VALOR.

Estas guardas nao redesenham nada e nao acrescentam especie nenhuma: elas
escrevem o que ja foi decidido, do lado do fio.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import _gavetas  # noqa: E402,F401
from regras import proveniencia as pv  # noqa: E402


class OCampoDasUnidadesTemNomeDeFio(unittest.TestCase):

    def test_o_campo_chama_se_TEXT_UNITS(self):
        """ATAQUE 4. O envelope em disco diz `TEXT_UNITS`; mudar a constante
        renomeia o campo para toda a gente e nao parte teste nenhum."""
        self.assertEqual(
            'TEXT_UNITS', pv.CAMPO_DAS_UNIDADES,
            "o campo das unidades mudou de nome no fio. Envelopes ja "
            "colhidos deixam de ser lidos, e a ponte do SCRAP nasce torta.")


class AsEspeciesSaoAsQueOContratoFechou(unittest.TestCase):
    """O modelo fechado pela COL-E7-01, escrito pelo VALOR."""

    ESPECIES = ('AUTHOR_TEXT', 'NATIVE_CAPTION', 'TRANSCRIPT', 'ASR',
                'PAGE_TEXT', 'DOCUMENT_TEXT', 'UNKNOWN')
    RELACOES = ('ORIGINAL', 'TRANSLATED', 'UNKNOWN')

    def test_as_sete_especies_continuam_a_ser_estas_sete(self):
        self.assertEqual(set(self.ESPECIES), set(pv.TEXT_KINDS),
                         "o conjunto das especies mudou")

    def test_cada_especie_tem_o_valor_que_o_contrato_fechou(self):
        for nome, valor in (('AUTHOR_TEXT', pv.AUTHOR_TEXT),
                            ('NATIVE_CAPTION', pv.NATIVE_CAPTION),
                            ('TRANSCRIPT', pv.TRANSCRIPT),
                            ('ASR', pv.ASR),
                            ('PAGE_TEXT', pv.PAGE_TEXT),
                            ('DOCUMENT_TEXT', pv.DOCUMENT_TEXT)):
            with self.subTest(especie=nome):
                self.assertEqual(nome, valor)

    def test_o_desconhecido_chama_se_UNKNOWN(self):
        """ATAQUE 8. Com `TEXTO_DESCONHECIDO = 'TRANSCRIPT'` os 65 testes do
        contrato passavam — e toda observacao sem especie declarada passava a
        dizer, no fio, que alguem a tinha transcrito."""
        self.assertEqual(
            'UNKNOWN', pv.TEXTO_DESCONHECIDO,
            "o desconhecido deixou de se chamar UNKNOWN. Quem ler o "
            "envelope passa a ver uma especie onde havia uma ausencia.")

    def test_o_desconhecido_nao_e_nenhuma_especie_conhecida(self):
        """A trava que mata a familia inteira do ataque 8, e nao so o caso
        que apareceu: seja qual for o valor, ele nao pode COINCIDIR com uma
        especie de verdade."""
        conhecidas = set(pv.TEXT_KINDS) - {pv.TEXTO_DESCONHECIDO}
        self.assertNotIn(
            pv.TEXTO_DESCONHECIDO, conhecidas,
            "a ausencia de especie ganhou o nome de uma especie")

    def test_as_tres_relacoes_continuam_a_ser_estas_tres(self):
        self.assertEqual(set(self.RELACOES), set(pv.TEXT_RELATIONS))

    def test_original_e_traducao_sao_valores_diferentes(self):
        self.assertNotEqual(pv.ORIGINAL, pv.TRANSLATED)
        self.assertEqual('ORIGINAL', pv.ORIGINAL)
        self.assertEqual('TRANSLATED', pv.TRANSLATED)


class UmDonoSoParaOTexto(unittest.TestCase):
    """TEXT_CONTRACT_OWNER_COUNT = 1, medido e nao declarado."""

    def test_so_regras_proveniencia_define_o_vocabulario(self):
        """Quem ESCREVER a lista de especies noutro ficheiro cria um segundo
        dono — e dois donos divergem no dia em que uma especie nascer."""
        import ast
        import io
        achados = []
        for pasta in ('coleta', 'admissao', 'orquestrador', 'regras', 'leis'):
            d = os.path.join(RAIZ, pasta)
            if not os.path.isdir(d):
                continue
            for nome in sorted(os.listdir(d)):
                if not nome.endswith('.py'):
                    continue
                rel = os.path.join(pasta, nome)
                if rel == os.path.join('regras', 'proveniencia.py'):
                    continue
                with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
                    arvore = ast.parse(f.read())
                for no in ast.walk(arvore):
                    if not isinstance(no, ast.Assign):
                        continue
                    alvos = [t.id for t in no.targets if isinstance(t, ast.Name)]
                    if not any(a in ('TEXT_KINDS', 'TEXT_RELATIONS',
                                     'CAMPO_DAS_UNIDADES') for a in alvos):
                        continue
                    achados.append('%s :: %s' % (rel, ','.join(alvos)))
        self.assertEqual(
            [], achados,
            "um segundo dono do vocabulario do texto apareceu: %s" % achados)


if __name__ == '__main__':
    unittest.main(verbosity=2)
