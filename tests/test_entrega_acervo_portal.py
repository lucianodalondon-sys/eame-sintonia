#!/usr/bin/env python3
"""Provas de que a ENTREGA nao volta a ser chamada de FUNDACAO DA COLETA.

Este ficheiro nasceu como tests/test_fundacao_coleta.py e guardava um portao
com o nome errado: media a entrega ate ao portal e publicava
COLLECTION_FOUNDATION_CLOSED. As provas de escopo continuam todas aqui — o que
mudou foi de que pergunta elas guardam — e juntaram-se seis novas (T1..T6) que
fecham o acoplamento que causou o erro.

    ACERVO -> PACOTE -> TELA NAO E COLLECTION FOUNDATION.
    E DELIVERY / LINEAGE / OBSERVABILITY.
"""
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import entrega_acervo_portal as E                                 # noqa: E402

FRONTEIRA = os.path.join(RAIZ, 'data', 'samples', 'FRONTEIRA-ACERVO-PACOTE.json')
BIBLIA = os.path.join(RAIZ, 'docs', 'biblia', 'BIBLIA-DA-INTELIGENCIA-EAME.md')

# As camadas que a fundacao da coleta NAO pode ter como dependencia. A coleta
# termina em ADMISSION/READY; tudo abaixo disto e a jusante dela.
A_JUSANTE = ('PORTAL', 'PACOTE', 'PACKAGE', 'TELA', 'SCREEN', 'UI',
             'PRODUTO_DE_INTELIGENCIA', 'INTELLIGENCE')


class T1_ACollectionFoundationNaoDependeDoPortal(unittest.TestCase):
    """T1 · COLLECTION_FOUNDATION nao depende de portal, pacote ou tela.

    O erro original nao foi de medicao: foi de nome. Um portao de entrega
    chamado fundacao da coleta faria um portal incompleto impedir a coleta de
    fechar — invertendo a ordem que o projeto exige de proposito.
    """

    @classmethod
    def setUpClass(cls):
        cls.d = E.monta()

    def test_este_ficheiro_nao_e_dono_de_collection_foundation_closed(self):
        self.assertEqual('NAO',
                         E.DONO_CANONICO_DA_FUNDACAO_DA_COLETA['ESTE_ARQUIVO_E_DONO'])
        self.assertNotIn('COLLECTION_FOUNDATION_CLOSED', self.d,
                         'o veredito deste portao nao pode chamar-se assim')

    def test_o_veredito_publicado_e_o_da_entrega(self):
        self.assertIn('ACERVO_TO_PORTAL_DELIVERY_READY', self.d)
        self.assertIn(self.d['ACERVO_TO_PORTAL_DELIVERY_READY'], ('SIM', 'NAO'))

    def test_o_dono_canonico_esta_nomeado_com_ficheiros(self):
        """Dizer «o dono e outro» sem dizer QUEM e adiar o problema."""
        dono = E.DONO_CANONICO_DA_FUNDACAO_DA_COLETA
        self.assertTrue(dono['LINHA'])
        self.assertIn('leis/fundacao_da_coleta.py', dono['ARQUIVOS'])
        self.assertEqual('ADMISSION / READY', dono['ONDE_A_COLETA_TERMINA'])
        for camada in ('PORTAL', 'PACOTE', 'TELA', 'UI'):
            self.assertIn(camada, dono['NAO_DEPENDE_DE'])

    def test_a_fundacao_da_coleta_e_lida_nunca_derivada(self):
        """Nao ter o dono a mao nao autoriza responder por ele."""
        c = self.d['CONTEXTO_A_MONTANTE']['FUNDACAO_DA_COLETA']['ESTADO_LIDO']
        self.assertIn(c['VALOR'], ('SIM', 'NAO', 'NAO_DISPONIVEL_NESTA_BRANCH'))
        if c['VALOR'] == 'NAO_DISPONIVEL_NESTA_BRANCH':
            self.assertIsNone(c['LIDO_DE'])
        else:
            self.assertEqual('leis/fundacao_da_coleta.py', c['LIDO_DE'])


class T2_AEntregaAbertaNaoMoveAColeta(unittest.TestCase):
    """T2 · a fronteira de entrega pode estar aberta sem alterar a coleta.

    A saida facil de amanha e a mesma de ontem ao contrario: voltar a somar o
    portao da coleta aos pilares deste, «para dar contexto». Reprova.
    """

    @classmethod
    def setUpClass(cls):
        cls.d = E.monta()

    def test_a_montante_nao_e_pilar(self):
        for nome, c in E.CONTEXTO_A_MONTANTE.items():
            with self.subTest(contexto=nome):
                self.assertEqual('NAO', c['E_PILAR_DESTE_PORTAO'])
                self.assertNotIn(nome, E.PILARES)

    def test_o_unico_pilar_e_a_travessia(self):
        self.assertEqual(['TRAVESSIA'], list(E.PILARES))

    def test_o_veredito_so_olha_para_os_pilares(self):
        pronto = self.d['ACERVO_TO_PORTAL_DELIVERY_READY'] == 'SIM'
        abertos = [n for n, p in self.d['PILARES'].items()
                   if p['ESTADO'] != 'FECHADO']
        self.assertEqual(pronto, not abertos)

    def test_um_nao_aqui_declara_o_que_nao_significa(self):
        """Um NAO que nao diz o que nao significa vira bloqueio emprestado."""
        texto = self.d['O_QUE_UM_NAO_AQUI_NAO_SIGNIFICA']
        self.assertIn('coleta', texto.lower())
        self.assertTrue(self.d['O_QUE_ISTO_NAO_E'])

    def test_o_estado_da_coleta_nao_entra_no_veredito(self):
        """A prova com dentes: mexer no contexto nao pode mexer no resultado.

        Reavalia com o contexto a montante forcado ao pior estado possivel. Se
        o veredito mudar, houve acoplamento.
        """
        antes = self.d['ACERVO_TO_PORTAL_DELIVERY_READY']
        guardado = dict(E.CONTEXTO_A_MONTANTE['ENTRADA_DA_COLETA'])
        try:
            E.CONTEXTO_A_MONTANTE['ENTRADA_DA_COLETA']['ESTADO_LIDO'] = 'PARTIAL'
            depois = E.monta()['ACERVO_TO_PORTAL_DELIVERY_READY']
        finally:
            E.CONTEXTO_A_MONTANTE['ENTRADA_DA_COLETA'] = guardado
        self.assertEqual(antes, depois,
                         'o estado da coleta mudou o veredito da entrega')


class T3_UmLadoNaoEReconciliacao(unittest.TestCase):
    """T3 · ONE_SIDED_MEASUREMENT nao vira reconciliacao completa."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(FRONTEIRA):
            raise unittest.SkipTest('artefato da fronteira ausente')
        with open(FRONTEIRA, encoding='utf-8') as h:
            cls.f = json.load(h)

    def test_reconciliacao_exige_os_dois_lados_medidos(self):
        for fam in self.f['FAMILIAS']:
            with self.subTest(familia=fam['FAMILIA']):
                m = fam['ESTADO_DE_MEDICAO']
                dois = m['PARTIU'] == 'MEASURED' and m['CHEGOU'] == 'MEASURED'
                self.assertEqual(
                    m['RECONCILIACAO'] == 'RECONCILIATION_COMPLETE', dois,
                    'subtrair medicao de alegacao produz um numero com cara de facto')

    def test_o_lado_do_acervo_entra_como_alegacao(self):
        """Se o acervo um dia entrar aqui, este teste reprova — e reprova certo."""
        for fam in self.f['FAMILIAS']:
            with self.subTest(familia=fam['FAMILIA']):
                self.assertEqual('NAO', fam['PARTIU']['MEDIDO_DAQUI'])
                self.assertTrue(fam['PARTIU']['ORIGEM_DA_ALEGACAO'])
                self.assertTrue(fam['PARTIU']['PORQUE_NAO'])

    def test_perda_quantificavel_acompanha_a_reconciliacao(self):
        for fam in self.f['FAMILIAS']:
            with self.subTest(familia=fam['FAMILIA']):
                completa = (fam['ESTADO_DE_MEDICAO']['RECONCILIACAO']
                            == 'RECONCILIATION_COMPLETE')
                self.assertEqual(fam['PERDA_QUANTIFICAVEL'] == 'SIM', completa)

    def test_quantos_lados_sao_medidos_neste_ambiente(self):
        """Um. E o artefato tem de dizer isso, nao deixar deduzir."""
        for fam in self.f['FAMILIAS']:
            with self.subTest(familia=fam['FAMILIA']):
                medidos = [k for k in ('PARTIU', 'CHEGOU')
                           if fam['ESTADO_DE_MEDICAO'][k] == 'MEASURED']
                self.assertEqual(['CHEGOU'], medidos)


class T4_AEscadaDaTranscricaoNaoColapsa(unittest.TestCase):
    """T4 · TRANSCRIPT_INCLUDED nao vira TRANSCRIPT_USED_AS_EVIDENCE.

    184 registos no pacote nao sao 184 usados em Inteligencia. Sao duas
    perguntas, e continuam separadas.
    """

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(FRONTEIRA):
            raise unittest.SkipTest('artefato da fronteira ausente')
        with open(FRONTEIRA, encoding='utf-8') as h:
            cls.f = json.load(h)
        cls.escada = next(
            (fam['CHEGOU'].get('ESCADA') for fam in cls.f['FAMILIAS']
             if fam['CHEGOU'].get('ESCADA')), None)

    def test_os_cinco_degraus_sao_publicados_separados(self):
        self.assertIsNotNone(self.escada, 'nenhuma escada publicada')
        for degrau in ('VIDEO_EXISTS', 'TRANSCRIPT_EXISTS', 'TRANSCRIPT_USABLE',
                       'TRANSCRIPT_INCLUDED_IN_PACKAGE',
                       'TRANSCRIPT_USED_AS_EVIDENCE'):
            with self.subTest(degrau=degrau):
                self.assertIn(degrau, self.escada)
                self.assertIsInstance(self.escada[degrau], int)

    def test_incluido_no_pacote_nao_implica_usado_como_evidencia(self):
        """A afirmacao forte nunca pode ser derivada da fraca."""
        incluido = self.escada['TRANSCRIPT_INCLUDED_IN_PACKAGE']
        usado = self.escada['TRANSCRIPT_USED_AS_EVIDENCE']
        self.assertLessEqual(usado, incluido)
        self.assertNotEqual(
            'derivado', str(self.escada.get('TRANSCRIPT_USED_AS_EVIDENCE_ORIGEM', '')))

    def test_o_zero_do_ultimo_degrau_e_publicado_exatamente(self):
        """Se e falso em 184/184, e isso que se publica — nao se arredonda."""
        if self.escada['TRANSCRIPT_USED_AS_EVIDENCE'] != 0:
            self.skipTest('o degrau virou; a medicao mudou e este teste sai do caminho')
        fam = next(f for f in self.f['FAMILIAS'] if f['CHEGOU'].get('ESCADA'))
        self.assertIn('184/184', fam['O_DEGRAU_QUE_FALTA'].replace(' ', ''))
        self.assertTrue(fam['DONO_DA_ACAO'])

    def test_fronteira_declarada_nao_afirma_pronto(self):
        """O estado responde UMA pergunta: deliberado ou perda silenciosa?"""
        for fam in self.f['FAMILIAS']:
            if fam['ESTADO'] != 'FECHADA_COM_FRONTEIRA_DECLARADA':
                continue
            with self.subTest(familia=fam['FAMILIA']):
                t = fam['O_QUE_ESTE_ESTADO_NAO_AFIRMA']
                for proibida in ('INTELLIGENCE_READY',
                                 'COLLECTION_FOUNDATION_CLOSED',
                                 'PORTAL_COMPLETE'):
                    self.assertIn(proibida, t)

    def test_fronteira_declarada_exige_vestigio_medivel(self):
        """Escrever a frase nao fecha familia nenhuma."""
        for fam in self.f['FAMILIAS']:
            if fam['ESTADO'] != 'FECHADA_COM_FRONTEIRA_DECLARADA':
                continue
            with self.subTest(familia=fam['FAMILIA']):
                e = fam['CHEGOU'].get('ESCADA') or {}
                self.assertTrue(fam.get('O_TEXTO_NAO_ATRAVESSA_POR_DECISAO'))
                self.assertGreater(e.get('REGISTOS', 0), 0)
                self.assertEqual(5, len(e.get('CAMPOS_DE_ESTADO_ENCONTRADOS', [])))
                self.assertGreater(e.get('COM_TEXT_SHA256', 0), 0)
                self.assertGreater(
                    fam['CHEGOU'].get('CHARS_DECLARADOS_PELA_ORIGEM', 0), 0)

    def test_rotulo_de_estado_nunca_conta_como_texto(self):
        """A confusao que este medidor ja cometeu, fechada."""
        for fam in self.f['FAMILIAS']:
            e = fam['CHEGOU'].get('ESCADA')
            if not e:
                continue
            with self.subTest(familia=fam['FAMILIA']):
                for campo in fam['CHEGOU'].get('CAMPOS_DE_TEXTO_ENCONTRADOS', []):
                    self.assertNotIn(campo.split('.')[-1],
                                     e.get('CAMPOS_DE_ESTADO_ENCONTRADOS', []))


class T5_ABibliaNaoSeDeclaraCompleta(unittest.TestCase):
    """T5 · o documento atual e inventario de leis, nao a Biblia fechada."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(BIBLIA):
            raise unittest.SkipTest('documento ausente')
        with open(BIBLIA, encoding='utf-8') as h:
            cls.t = h.read()

    def test_declara_se_como_rascunho_e_inventario(self):
        self.assertIn('DRAFT', self.t)
        self.assertIn('INVENTARIO_DE_LEIS', self.t.replace('Á', 'A').replace('Ã', 'A'))
        self.assertIn('INPUT_TO_INTELLIGENCE_BIBLE', self.t)

    def test_nao_se_declara_fechada(self):
        # As frases sao montadas por concatenacao de proposito: escritas
        # inteiras, este ficheiro passaria a conter uma ATRIBUICAO da constante
        # e T6 o apanharia — corretamente. Uma prova nao pode exigir excecao
        # para si propria no varredor da prova irma.
        afirma = ' = SIM'
        for proibida in ('BIBLIA_DA_INTELIGENCIA_CLOSED' + afirma,
                         'CANONICAL_COMPLETE' + afirma,
                         'RESEARCH_COMPLETE' + afirma,
                         'IMPLEMENTATION_COMPLETE' + afirma):
            with self.subTest(afirmacao=proibida):
                self.assertNotIn(proibida, self.t)

    def test_publica_o_que_ainda_nao_cobre(self):
        """Um inventario que nao diz o que falta parece um censo."""
        for tema in ('KIT', 'KIQ', 'CALIBRATION', 'CONTRARY_EVIDENCE',
                     'DECISION_TELEMETRY', 'EVALS'):
            with self.subTest(tema=tema):
                self.assertIn(tema, self.t)


class T6_ODesenhoNaoPoeOPortalDentroDaColeta(unittest.TestCase):
    """T6 · nenhum artefato desta linha representa entrega-ate-o-portal como
    pilar da coleta.

    O System Map canonico vive na outra linha e nao e editado daqui. O que se
    prova aqui e a paridade: nada nesta arvore afirma a dependencia invertida.
    """

    def test_o_artefato_da_entrega_declara_a_sua_classe(self):
        d = E.monta()
        self.assertEqual('DELIVERY / LINEAGE / OBSERVABILITY', d['CLASSE'])
        self.assertTrue(d['PRECURSOR_DE'])

    def test_o_medidor_declara_que_nao_e_fundacao_de_coleta(self):
        with open(FRONTEIRA, encoding='utf-8') as h:
            f = json.load(h)
        self.assertEqual('DELIVERY / LINEAGE / OBSERVABILITY', f['CLASSE'])
        self.assertIn('COLLECTION FOUNDATION', f['NAO_E'])

    def test_nenhum_artefato_desta_linha_publica_collection_foundation_closed(self):
        """A constante tem um dono, e ele nao esta nesta arvore.

        Procura em codigo e artefatos — nao em prosa, que precisa poder citar
        a constante para explicar de quem ela e.
        """
        CONSTANTE = 'COLLECTION_FOUNDATION' + '_CLOSED'
        alvos = []
        for base, _, ficheiros in os.walk(RAIZ):
            if any(x in base for x in ('/.git', '__pycache__', '/build', '/node_modules')):
                continue
            for f in ficheiros:
                if f.endswith(('.py', '.mjs', '.js')) or (
                        f.endswith('.json') and '/data/samples' in base):
                    alvos.append(os.path.join(base, f))
        donos = []
        for caminho in alvos:
            with open(caminho, encoding='utf-8', errors='ignore') as h:
                texto = h.read()
            for linha in texto.splitlines():
                if CONSTANTE not in linha:
                    continue
                # citar e permitido; ATRIBUIR valor nao, fora do dono canonico.
                # Os padroes montam-se por concatenacao porque um varredor que
                # escreve o proprio padrao inteiro apanha-se a si mesmo — e a
                # saida seria isenta-lo, que e a saida que este teste existe
                # para fechar.
                atribui = any(CONSTANTE + sufixo in linha
                              for sufixo in (' =', "':", '":'))
                if atribui and 'leis/fundacao_da_coleta.py' not in caminho:
                    donos.append(os.path.relpath(caminho, RAIZ))
        self.assertEqual([], sorted(set(donos)),
                         'segundo dono de COLLECTION_FOUNDATION_CLOSED')


class TestOArtefatoContinuaReprodutivel(unittest.TestCase):
    """O medidor tem de sair byte-identico quando as entradas nao mudam."""

    def test_duas_corridas_dao_o_mesmo_ficheiro(self):
        medidor = os.path.join(RAIZ, 'italia-portale', 'audit',
                               'fronteira-acervo-pacote.mjs')
        try:
            a = subprocess.run(['node', medidor, '--json'], capture_output=True,
                               text=True, timeout=300, cwd=RAIZ)
            b = subprocess.run(['node', medidor, '--json'], capture_output=True,
                               text=True, timeout=300, cwd=RAIZ)
        except (OSError, subprocess.SubprocessError) as e:
            self.skipTest('node indisponivel: %s' % e)
        self.assertEqual(0, a.returncode, a.stderr[:300])
        self.assertEqual(a.stdout, b.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
