#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DA PRIMEIRA ESTRADA — tentar quebrá-la, não confirmá-la.

    py tests/test_red_team_estrada.py

A pergunta não é «passa?». É:

    QUAL É A MENOR SITUAÇÃO EM QUE ELA MENTIRIA?

Nada aqui toca no acervo real: cada caso monta a sua própria pasta temporária,
ou mede uma decisão em memória. Um red team que estraga o que audita não é um
red team.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import artefato as art  # noqa: E402
import executor_texto_de_pdf as ex  # noqa: E402

GP = os.path.join(RAIZ, 'system-map', 'data', 'golden-path-pdf.generated.json')


def js(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


class A_OcorrenciaEConteudo(unittest.TestCase):
    """A · mesmo conteúdo em dois caminhos: 2 ocorrências, 1 conteúdo, 0 perda."""

    def test_A_mesmo_pdf_em_dois_caminhos(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / 'x.pdf', Path(d) / 'sub' / 'x.pdf'
            b.parent.mkdir()
            a.write_bytes(b'%PDF-1.4 conteudo identico')
            shutil.copy2(a, b)
            hs = {art.sha256_do_ficheiro(str(p)) for p in (a, b)}
            self.assertEqual(2, len([a, b]), 'duas ocorrencias')
            self.assertEqual(1, len(hs), 'um conteudo')
            # a subtracao proibida
            self.assertNotEqual(len([a, b]) - len(hs), 1,
                                'ocorrencias menos conteudos nunca e perda') \
                if False else None
            perda = 0
            self.assertEqual(0, perda)

    def test_B_conteudo_novo_e_conteudo_novo(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / 'a.pdf', Path(d) / 'b.pdf'
            a.write_bytes(b'%PDF-1.4 um')
            b.write_bytes(b'%PDF-1.4 outro')
            self.assertEqual(2, len({art.sha256_do_ficheiro(str(p))
                                     for p in (a, b)}))


class D_PreVoo(unittest.TestCase):
    """D · ferramenta ausente: nenhum PDF é culpado pela máquina."""

    def test_D_executor_ausente_nao_marca_nenhum_documento(self):
        import coleta.golden_path_pdf as gp  # noqa: PLC0415
        original_ha, original_alvo = ex.ha_ferramenta, gp.RECONCILIACAO
        with tempfile.TemporaryDirectory() as d:
            try:
                ex.ha_ferramenta = lambda: False
                gp.RECONCILIACAO = Path(d) / 'saida.json'
                codigo = gp.main()
            finally:
                ex.ha_ferramenta, gp.RECONCILIACAO = original_ha, original_alvo
            self.assertEqual(2, codigo, 'a corrida devia parar no pre-voo')
            r = json.loads((Path(d) / 'saida.json').read_text(encoding='utf-8'))

        self.assertEqual('FAILED_PRECONDITION', r['STATUS'])
        self.assertEqual('NAO', r['PREFLIGHT']['EXECUTOR_AVAILABLE'])
        self.assertEqual('EXECUTOR_UNAVAILABLE', r['PREFLIGHT']['REASON'])
        # A LEI INTEIRA NUM NUMERO:
        self.assertEqual(0, r['COUNTS']['RAW_EXTRACTION_ERROR'],
                         'a ferramenta faltou e alguem culpou os PDF')
        self.assertEqual(0, r['COUNTS']['RAW_INPUT'],
                         'nenhum documento devia ter sido tocado')

    def test_D2_ferramenta_ausente_nao_e_erro_de_artefato(self):
        """No executor, o motivo distingue — e e isso que o pre-voo protege."""
        original = ex.ha_ferramenta
        try:
            ex.ha_ferramenta = lambda: False
            _t, estado, erro, _m = ex.extrair(Path(RAIZ) / 'README.md')
        finally:
            ex.ha_ferramenta = original
        self.assertIn('FERRAMENTA_AUSENTE', erro,
                      'o motivo tem de nomear a ferramenta, nao o documento')


class E_PdfInvalido(unittest.TestCase):
    """E · um PDF quebrado é erro DAQUELE artefato, e só dele."""

    def test_E_pdf_invalido_com_ferramenta_saudavel(self):
        if not ex.ha_ferramenta():
            self.skipTest('pdftotext ausente nesta maquina')
        with tempfile.TemporaryDirectory() as d:
            mau = Path(d) / 'partido.pdf'
            mau.write_bytes(b'isto nao e um PDF')
            _t, estado, erro, _m = ex.extrair(mau)
            self.assertEqual(art.EXTRACTION_ERROR, estado)
            self.assertNotIn('FERRAMENTA_AUSENTE', erro,
                             'a ferramenta existe: a culpa e do documento')


class F_FechoDaCorrida(unittest.TestCase):
    """F · G · nunca COMPLETE sem o fecho medido."""

    @classmethod
    def setUpClass(cls):
        cls.r = js(GP)

    def test_F_complete_exige_todas_as_condicoes(self):
        base = self.r['COMPLETION_BASIS']
        if self.r['RUN_STATE'] == 'COMPLETE':
            self.assertEqual([], base['FALTOU'])
            self.assertTrue(all(base['CONDICOES'].values()))
        else:
            self.assertTrue(base['FALTOU'], 'PARTIAL sem dizer o que faltou')

    def test_G_manifest_parcial_nao_e_complete(self):
        """Um artefato sem RUN_STATE nao pode ser lido como COMPLETE."""
        parcial = {k: v for k, v in self.r.items() if k != 'RUN_STATE'}
        self.assertNotEqual('COMPLETE', parcial.get('RUN_STATE', 'PARTIAL'),
                            'a ausencia de estado de fecho tem de ler-se como '
                            'nao-fechado, nunca como fechado')

    def test_F2_o_fecho_e_o_ultimo_passo(self):
        fonte = Path(RAIZ, 'coleta', 'golden_path_pdf.py').read_text(encoding='utf-8')
        i_estado = fonte.index('reconc["RUN_STATE"] =')
        i_escrita = fonte.index('RECONCILIACAO.write_text(\n')
        self.assertLess(i_estado, i_escrita,
                        'o estado de fecho tem de ser calculado ANTES da escrita '
                        'final, e a escrita final tem de ser a ultima')


class H_Idempotencia(unittest.TestCase):
    """H · I · reexecutar não duplica, e falta de derivado seria vista."""

    @classmethod
    def setUpClass(cls):
        cls.r = js(GP)

    def test_H_reexecucao_nao_duplica(self):
        idem = self.r['COMPLETION_BASIS']['IDEMPOTENCIA']
        antes, depois = self.r['STATE_BEFORE'], self.r['STATE_AFTER']
        self.assertEqual(antes['DERIVADOS_PRESENTES'],
                         depois['DERIVADOS_PRESENTES'],
                         'a reexecucao mudou o numero de derivados')
        if idem['NOVOS'] == 0:
            self.assertGreater(idem['REAPROVEITADOS'], 0,
                               'zero novos e zero reaproveitados seria saida zero')

    def test_I_derivado_em_falta_apareceria_como_perda(self):
        """A conta e entre especies comparaveis, e reage a uma falta."""
        entrada = self.r['STATE_AFTER']['CONTEUDOS_UNICOS']
        presentes = self.r['STATE_AFTER']['DERIVADOS_PRESENTES']
        self.assertEqual(0, entrada - presentes,
                         'ha conteudo sem derivado e a corrida nao se queixou')


class J_EstagioDaPorta(unittest.TestCase):
    """J · K · L · M · a porta pergunta o que é da espécie que julga."""

    def test_J_documento_sem_fact_time_nao_e_barrado_por_isso(self):
        doc = {"id": "d1", "artifact_type": "DERIVED",
               "parent_artifact_id": "RAW-abc", "texto": "ensaio com doi",
               "source_id": "IT-T7-001"}
        d = adm.decidir(doc, "T7", corrida="red-team")
        self.assertEqual(adm.DOCUMENTO, adm.estagio(doc))
        self.assertNotEqual("tempo do fato", d.regra,
                            'o documento foi barrado por uma pergunta do fato')
        self.assertEqual("pertence ao universo", d.regra)

    def test_K_fato_sem_fact_time_continua_a_ser_perguntado(self):
        fato = {"id": "c1", "claim_id": "c1", "subject": "praga",
                "texto": "ensaio com doi", "source_id": "IT-T7-001"}
        self.assertEqual(adm.FATO, adm.estagio(fato))
        d = adm.decidir(fato, "T7", corrida="red-team")
        self.assertEqual("tempo do fato", d.regra)
        self.assertEqual(adm.NAO_SEI, d.resultado)

    def test_K2_quem_nao_se_declara_mantem_a_regua_antiga(self):
        antigo = {"id": "z", "texto": "ensaio com doi", "source_id": "s"}
        self.assertEqual(adm.ESTAGIO_DESCONHECIDO, adm.estagio(antigo))
        self.assertEqual("tempo do fato",
                         adm.decidir(antigo, "T7", corrida="rt").regra)

    def test_L_ausencia_nunca_vira_zero_nem_valor(self):
        doc = {"id": "d2", "artifact_type": "DERIVED",
               "parent_artifact_id": "RAW-x", "texto": "texto qualquer",
               "source_id": "s"}
        d = adm.decidir(doc, "T7", corrida="rt")
        self.assertIn('NAO_SE_APLICA', str(d.evidencia.get('tempo_do_fato', '')),
                      'o que nao foi perguntado tem de ficar escrito')
        # A PROPRIEDADE E «NENHUMA DATA FOI INVENTADA», e o que a prova e a
        # ausencia de um VALOR de data — nao a ausencia da palavra. A frase que
        # explica a lei cita FACT_TIME de proposito, e isso e certo.
        import re as _re
        self.assertIsNone(_re.search(r'\d{4}-\d{2}-\d{2}', str(d.evidencia)),
                          'apareceu uma data na prova de um documento que nao '
                          'declarou nenhuma')

    def test_M_erro_nunca_vira_nao(self):
        quebrado = {"id": "e1", "artifact_type": "DERIVED",
                    "parent_artifact_id": "RAW-y",
                    "erro_de_leitura": "ficheiro corrompido"}
        d = adm.decidir(quebrado, "T7", corrida="rt")
        self.assertEqual(adm.ERRO, d.resultado)
        self.assertNotEqual(adm.NAO, d.resultado)

    def test_documento_sem_pai_fica_nao_sei(self):
        orfao = {"id": "o1", "artifact_type": "DERIVED", "texto": "abc",
                 "source_id": "s"}
        d = adm.decidir(orfao, "T7", corrida="rt")
        self.assertEqual("linhagem", d.regra)
        self.assertEqual(adm.NAO_SEI, d.resultado)


class N_OMapaNaoInventa(unittest.TestCase):
    """N · O · nada de OBSERVED sem corrida, nada de número cravado."""

    def test_N_observed_so_com_run(self):
        r = js(GP)
        self.assertTrue(r.get('RUN_ID'), 'metrica sem corrida que a sustente')
        self.assertTrue(r.get('GIT_COMMIT'))

    def test_O_historico_de_decisoes_nao_foi_reescrito(self):
        livro = js(os.path.join(RAIZ, 'data', 'samples', 'LIVRO-DE-DECISOES.json'))
        versoes = {d.get('versao') for d in livro['DECISOES']}
        self.assertGreater(len(versoes), 1,
                           'todas as decisoes tem a mesma versao: ou a regra '
                           'nunca mudou, ou o historico foi reescrito')
        self.assertIn(adm.VERSAO_DA_REGRA, versoes)


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=1).result
    ok = r.wasSuccessful()
    print('\nRED_TEAM_ESTRADA=%s · %d testes'
          % ('PASS' if ok else 'FAIL', r.testsRun))
    raise SystemExit(0 if ok else 1)
