# -*- coding: utf-8 -*-
"""A guarda que `scripts/fato_local.py` promete no cabeçalho e que não existia.

O cabeçalho diz, literalmente: «Os dois arquivos NÃO podem discordar, e há um teste
que compara os dois vocabulários e reprova se divergirem». Esse teste não existia.
`tests/test_lugar_do_fato.py` importa `fato_local as IT` mas só o usa em asserções de
comportamento (`IT.PLACE_MENTION_ONLY`, `IT.TERRITORIAL_LIST`); o único teste de
vocabulário compara o NÚCLEO com o banco, nunca o núcleo com o leitor italiano.

Sem guarda, a divergência entrou e cresceu em silêncio:

  antes do PASSO 03   núcleo tinha INCIDENCE_MEASUREMENT que o leitor IT não tinha
  depois do PASSO 03  o leitor IT ganha MODELLED_RISK que o núcleo não tem

Este ficheiro não decide qual das duas listas está certa — isso é decisão de
significado e não cabe a um teste. Ele PRENDE a divergência conhecida: qualquer
mudança em qualquer dos dois lados quebra aqui e obriga a decidir em voz alta,
em vez de alargar o buraco outra vez sem ninguém ver.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import fato_local as IT        # noqa: E402
import lugar_do_fato as L      # noqa: E402

# A divergência MEDIDA, não a desejada. Mexer num dos lados obriga a mexer aqui.
SO_NO_NUCLEO = {'INCIDENCE_MEASUREMENT'}
SO_NO_LEITOR_IT = {'MODELLED_RISK'}


class TestOsDoisVocabulariosDeEvidencia(unittest.TestCase):

    def setUp(self):
        self.nucleo = set(L.TIPOS_DE_EVIDENCIA)
        self.it = set(IT.TIPOS_DE_EVIDENCIA)

    def test_a_divergencia_e_exatamente_a_registada(self):
        self.assertEqual(
            SO_NO_NUCLEO, self.nucleo - self.it,
            'o núcleo ganhou ou perdeu uma espécie que o leitor italiano não acompanha; '
            'decida em voz alta e atualize SO_NO_NUCLEO')
        self.assertEqual(
            SO_NO_LEITOR_IT, self.it - self.nucleo,
            'o leitor italiano ganhou ou perdeu uma espécie que o núcleo não conhece; '
            'decida em voz alta e atualize SO_NO_LEITOR_IT')

    def test_o_tronco_comum_continua_intacto(self):
        comum = self.nucleo & self.it
        self.assertEqual(
            {'FIELD_OBSERVATION', 'DIAGNOSTIC_SAMPLE', 'OFFICIAL_OCCURRENCE',
             'CONFIRMED_FOCUS', 'REGIONAL_STATEMENT', 'OTHER'}, comum,
            'o tronco comum das espécies de evidência mudou')

    # ── o lado SQL, lido do CONSTRAINT e não por substring ────────────────────
    # A primeira versão destes dois testes fazia `assertIn("'ESPECIE'", corpo)` sobre
    # os 34 KB da migração inteira. Um nome dentro de um comentário satisfazia a
    # asserção tão bem como um constraint, e só a migração 018 entrava no âmbito —
    # uma 022 que alargasse o CHECK passava despercebida. Achado da revisão
    # adversarial do PASSO 03, reproduzido e corrigido aqui.

    @staticmethod
    def _check_do_banco():
        """Devolve o conjunto de espécies que o CHECK vigente aceita, ou None.

        Varre TODAS as migrações por ordem: a última que define o CHECK de
        `tipo_de_evidencia` é a que vale.
        """
        import glob
        import re
        vigente = None
        for sql in sorted(glob.glob(os.path.join(ROOT, 'supabase', 'migrations', '*.sql'))):
            with open(sql, encoding='utf-8') as f:
                corpo = f.read()
            # comentários fora: o que conta é DDL
            corpo = re.sub(r'--[^\n]*', '', corpo)
            for m in re.finditer(
                    r"check\s*\(\s*tipo_de_evidencia\s+in\s*\((?P<lista>[^)]*)\)\s*\)",
                    corpo, re.I | re.S):
                vigente = set(re.findall(r"'([A-Z_]+)'", m.group('lista')))
        return vigente

    def test_o_check_do_banco_existe_e_e_legivel(self):
        """Sem esta, as duas asserções abaixo passariam com o CHECK apagado."""
        self.assertIsNotNone(
            self._check_do_banco(),
            'nenhuma migração define um CHECK para conteudo_lugar.tipo_de_evidencia — '
            'a coluna aceitaria qualquer string, MODELLED_RISK incluído')

    def test_o_que_so_o_leitor_it_tem_nao_chega_ao_banco(self):
        """MODELLED_RISK não pode entrar em conteudo_lugar pela porta do leitor."""
        vigente = self._check_do_banco()
        if vigente is None:
            self.fail('CHECK ausente — ver test_o_check_do_banco_existe_e_e_legivel')
        for especie in SO_NO_LEITOR_IT:
            self.assertNotIn(
                especie, vigente,
                '%s entrou no CHECK do banco sem passar pelo núcleo' % especie)

    def test_o_nucleo_e_quem_manda_no_banco(self):
        """A lista do núcleo é EXATAMENTE a que o CHECK aceita — igualdade, não inclusão."""
        vigente = self._check_do_banco()
        if vigente is None:
            self.fail('CHECK ausente — ver test_o_check_do_banco_existe_e_e_legivel')
        self.assertEqual(
            self.nucleo, vigente,
            'o CHECK do banco e o vocabulário do núcleo divergiram')


if __name__ == '__main__':
    unittest.main()
