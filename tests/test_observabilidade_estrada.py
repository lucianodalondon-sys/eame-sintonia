#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-20 — A PLACA DE VÍDEO DA PRIMEIRA ESTRADA.

    py tests/test_observabilidade_estrada.py

A pergunta que estes testes fazem não é «o número está certo?». É:

    O MAPA MOSTRA O QUE A MÁQUINA SABE — E MOSTRA DERIVADO?

Um número certo escrito à mão no gerador passaria em qualquer teste de valor e
mentiria no dia seguinte, quando o acervo mudasse. Por isso aqui se testa a
LIGAÇÃO: o que está no mapa tem de ser o que a medição diz, e tem de mudar
sozinho quando ela mudar.

    MÉTRICA ESCRITA À MÃO É UMA FOTOGRAFIA COM CARA DE TERMÓMETRO.
"""
from __future__ import annotations

import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

DADOS = os.path.join(RAIZ, 'system-map', 'data')
STATE = os.path.join(DADOS, 'state.generated.json')
CORPUS = os.path.join(DADOS, 'corpus-it.generated.json')
GP = os.path.join(DADOS, 'golden-path-pdf.generated.json')
GERADOR = os.path.join(RAIZ, 'system-map', 'scripts', 'generate_system_map.py')
CENSO = os.path.join(RAIZ, 'system-map', 'scripts', 'censo_do_corpus_it.py')


def ler(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def js(p):
    return json.loads(ler(p))


def peca(estado, pid):
    for n in estado['NODES']:
        if n['id'] == pid:
            return n
    raise AssertionError(f'{pid} nao existe no mapa')


def texto_da_peca(n):
    """Tudo o que uma pessoa consegue LER nesta peça, num sítio só."""
    return ' \n '.join([n.get('what', ''), n.get('status_reason', ''),
                        n.get('why_here', '')] + list(n.get('facts') or []))


class AMedicaoChegaAoMapa(unittest.TestCase):
    """T2 a T11 — o que a máquina mediu aparece, e vem da medição."""

    @classmethod
    def setUpClass(cls):
        cls.S = js(STATE)
        cls.OC = js(CORPUS)['OCORRENCIA_E_CONTEUDO']
        cls.C = js(GP)['COUNTS']
        cls.bruto = peca(cls.S, 'C-IT-PDF-BRUTO')
        cls.corrida = peca(cls.S, 'C-GOLDEN-PATH-PDF')
        cls.t_bruto = texto_da_peca(cls.bruto)
        cls.t_run = texto_da_peca(cls.corrida)

    # ── T2 · T3 · T4 ─────────────────────────────────────────────────────
    def test_T2_ocorrencias_aparecem(self):
        n = self.OC['OCORRENCIAS']
        self.assertIn(str(n), self.t_bruto, 'as ocorrencias nao aparecem no mapa')
        self.assertIn(str(n), self.t_run)
        self.assertRegex(self.t_bruto.upper(), r'OCORR[EÊ]NCIA')

    def test_T3_conteudos_unicos_aparecem_e_sao_por_impressao_digital(self):
        n = self.OC['CONTEUDOS_UNICOS']
        self.assertIn(str(n), self.t_bruto)
        self.assertRegex(self.t_bruto.lower(), r'impress[aã]o digital|sha')

    def test_T4_repeticao_aparece_nomeada(self):
        rep = self.OC['OCORRENCIAS_DE_CONTEUDO_REPETIDO']
        self.assertGreater(rep, 0, 'sem repeticao este teste nao mede nada')
        self.assertIn(str(rep), self.t_bruto)
        # e nao basta o numero: os caminhos tem de estar nomeados
        caminhos = [c for r in self.OC['ONDE_SE_REPETE'] for c in r['CAMINHOS']]
        achados = sum(1 for c in caminhos if c in self.t_bruto)
        self.assertGreaterEqual(achados, 2,
                                'a repeticao esta contada mas nao NOMEADA — um '
                                'numero sozinho nao impede ninguem de concluir '
                                '«sumiram seis»')

    # ── T5 · a lei inteira num teste ─────────────────────────────────────
    def test_T5_49_menos_43_NAO_vira_perda(self):
        oc, un = self.OC['OCORRENCIAS'], self.OC['CONTEUDOS_UNICOS']
        diferenca = oc - un
        self.assertGreater(diferenca, 0)
        self.assertEqual(0, self.OC['PERDA'])
        self.assertEqual(0, self.C['LOST'])
        # o mapa tem de DIZER que nao e perda, nao so mostrar zero
        for t, onde in ((self.t_bruto, 'bruto'), (self.t_run, 'corrida')):
            self.assertRegex(t.upper(), r'N[AÃ]O [EÉ] PERDA|N[AÃ]O PERDA',
                             f'a peca «{onde}» mostra a diferenca e nao explica '
                             f'que ela nao e perda')

    def test_T6_lost_e_medido_entre_etapas_comparaveis(self):
        self.assertRegex(self.t_run.lower(),
                         r'etapas compar[aá]veis|nunca ocorr[eê]ncias menos',
                         'o mapa nao diz COMO o perdido foi medido — e sem isso '
                         'alguem vai refazer a subtracao errada')

    # ── T7 · T8 ──────────────────────────────────────────────────────────
    def test_T7_entrada_da_derivacao_e_visivel(self):
        self.assertRegex(self.t_run.upper(), r'ENTRADA DA DERIVA[CÇ][AÃ]O')
        self.assertIn(str(self.OC['CONTEUDOS_UNICOS']), self.t_run)

    def test_T8_derivados_existentes_sao_visiveis(self):
        total = self.C['DERIVED_LANDED'] + self.C.get('JA_EXISTIAM', 0)
        self.assertIn(str(total), self.t_run)
        self.assertRegex(self.t_run.upper(), r'DERIVADOS QUE EXISTEM')

    # ── T9 · T10 ─────────────────────────────────────────────────────────
    def test_T9_needs_ocr_e_inspecionavel_mesmo_quando_zero(self):
        self.assertRegex(self.t_run.lower(), r'ocr',
                         'com OCR=0 o mapa nao pode ficar mudo: se amanha for '
                         '>0, ninguem descobre por acaso')
        self.assertIn(f"OCR: {self.C['RAW_NEEDS_OCR']}", self.t_run)

    def test_T10_erro_de_extracao_e_inspecionavel(self):
        self.assertIn(str(self.C['RAW_EXTRACTION_ERROR']), self.t_run)
        self.assertRegex(self.t_run.lower(), r'erro de extra[cç][aã]o')

    # ── T11 · T12 · T13 ──────────────────────────────────────────────────
    def test_T11_estado_da_corrida_e_visivel(self):
        self.assertRegex(self.t_run.lower(), r'estado que a corrida declara')
        self.assertRegex(self.t_run, r'COL-LAW-210')

    def test_T12_partial_nao_aparece_como_complete(self):
        self.assertIn('PARTIAL', self.t_run)
        self.assertNotEqual('green', self.corrida['ui_status'],
                            'a corrida esta PARTIAL e o cartao esta verde')
        self.assertRegex(self.t_run.lower(),
                         r'reconcilia[cç][aã]o sem perda n[aã]o [eé] fecho',
                         'LOST=0 nao pode ser lido como corrida fechada')

    def test_T13_zero_emitido_por_idempotencia_nao_parece_perda(self):
        if self.C['DERIVED_EMITTED'] == 0:
            self.assertIn(str(self.C.get('JA_EXISTIAM', 0)), self.t_run)
            self.assertRegex(self.t_run.lower(), r'j[aá] existiam',
                             'emitiu zero e o mapa nao explica que os textos ja '
                             'existiam — isso le-se como perda')


class NadaFoiEscritoAMao(unittest.TestCase):
    """T1 · T15 · T16 · T22 — a métrica nasce da medição, não do teclado."""

    @classmethod
    def setUpClass(cls):
        cls.S = js(STATE)
        cls.OC = js(CORPUS)['OCORRENCIA_E_CONTEUDO']
        cls.fonte = ler(GERADOR) + ler(CENSO)

    def test_T1_numeros_da_estrada_nao_estao_cravados_no_codigo(self):
        """Os valores de hoje NAO podem aparecer como literal no gerador."""
        proibidos = [self.OC['OCORRENCIAS'], self.OC['CONTEUDOS_UNICOS']]
        # tira comentarios e docstrings: explicar «49 - 43 = 6» em prosa e
        # legitimo; o que nao pode e um numero desses virar VALOR.
        codigo = '\n'.join(l for l in self.fonte.splitlines()
                           if not l.lstrip().startswith('#'))
        codigo = re.sub(r'"""[\s\S]*?"""', '', codigo)
        for n in proibidos:
            self.assertNotRegex(
                codigo, r'[:=]\s*%d\b' % n,
                f'o numero {n} aparece como valor no codigo do mapa. Hoje esta '
                f'certo; amanha o acervo muda e ele continua igual')

    def test_T1b_o_mapa_le_a_medicao(self):
        """Se o mapa mostra, tem de ser porque a medicao disse."""
        self.assertIn('OCORRENCIA_E_CONTEUDO', ler(GERADOR),
                      'o gerador nao le a medicao de ocorrencia x conteudo')
        n = peca(self.S, 'C-IT-PDF-BRUTO')
        self.assertIn('corpus-it.generated.json', n.get('evidence_text', ''),
                      'a peca nao diz de que medicao os numeros dela vieram')

    def test_T15_T16_contagem_de_caracteres_nao_e_canonizada(self):
        estado = ler(STATE)
        for n in ('703.022', '703022', '843.906', '843906', '859.142', '859142'):
            self.assertNotIn(n, estado,
                             f'{n} entrou no mapa como metrica. Nao ha regra de '
                             f'contagem escrita: a mesma pasta da contas '
                             f'diferentes conforme a quebra de linha')
        t = texto_da_peca(peca(self.S, 'C-GOLDEN-PATH-PDF'))
        self.assertRegex(t.lower(), r'caracteres.*n[aã]o can[oó]nic',
                         'o mapa devia DIZER que o numero de caracteres nao tem '
                         'contrato, em vez de simplesmente omitir')

    def test_custo_nao_e_inventado(self):
        """MUNDO ANTIGO: o mapa dizia so «custo monetario: NAO CANONICO».

        Era verdade e era pouco: escondia o numero em vez de o explicar. A
        redacao nova mostra o valor, a BASE do valor, e diz que contabilidade
        monetaria nao se aplica — o que e mais forte, porque um leitor consegue
        discordar da base. Uma frase que so nega nao se consegue contestar.
        """
        t = texto_da_peca(peca(self.S, 'C-GOLDEN-PATH-PDF')).lower()
        self.assertRegex(t, r'contabilidade monet[aá]ria',
                         'ausencia de servico pago nao e contabilidade, e o '
                         'mapa tem de dizer isso ao lado do numero')
        self.assertRegex(t, r'base:', 'o custo aparece sem base')

    def test_T21_nenhuma_credencial_no_estado(self):
        estado = ler(STATE)
        for padrao in (r'apify_api_[A-Za-z0-9]{10,}', r'eyJ[A-Za-z0-9_-]{20,}',
                       r'postgresql://\S+', r'SUPABASE_[A-Z_]*KEY\s*[:=]\s*["\'][^"\']{16,}'):
            self.assertIsNone(re.search(padrao, estado),
                              f'padrao de credencial no estado publicado: {padrao}')

    def test_T22_o_estado_traz_a_marca_de_quem_o_gerou(self):
        """Estado editado a mao nao teria proveniencia coerente."""
        p = self.S['PROVENANCE']
        for k in ('REPO', 'BRANCH', 'HEAD', 'GENERATED_AT'):
            self.assertTrue(p.get(k), f'PROVENANCE.{k} vazio')
        self.assertRegex(p['HEAD'], r'^[0-9a-f]{40}$')


class OQueNaoSeMexeu(unittest.TestCase):
    """T17 · T18 · T19 · T20 — os vermelhos e os gaps ficam onde estavam."""

    def test_T17_G36_continua_registado_e_nao_foi_mascarado(self):
        chao = js(os.path.join(RAIZ, 'data', 'samples',
                               'PADRAO-DA-COLETA-CHAO.json'))['FIXADO_EM']
        # o chao NAO pode ter sido subido para esconder o vermelho herdado
        self.assertEqual(26, len(chao['coletores_SEM_data']),
                         'o chao foi subido: G-36 mascarado')
        self.assertEqual(20, len(chao['coletores_SEM_lugar']))
        self.assertEqual(30, len(chao['coletores_SEM_descarte']))
        conf = ler(os.path.join(RAIZ, 'docs', 'biblia', 'CONFORMIDADE-ITALIA.md'))
        self.assertIn('G-36', conf, 'G-36 sumiu da matriz de conformidade')

    def test_T18_a_porta_nao_foi_alterada(self):
        """G-22 e a PROXIMA missao. A pergunta da porta continua a mesma."""
        porta = ler(os.path.join(RAIZ, 'admissao', 'admissao.py'))
        self.assertIn('published_at', porta,
                      'a pergunta da porta mudou — G-22 nao era desta missao')
        self.assertIn('tempo do fato', porta)

    def test_T19_T20_nada_foi_movido_para_o_supabase(self):
        """P-011 / G-02 continuam abertos: o ledger e os bytes ficam onde estao."""
        for caminho in ('data/collection-ledger/italy/runs.ndjson',
                        'data/collection-ledger/italy/observations.ndjson'):
            self.assertTrue(os.path.isfile(os.path.join(RAIZ, caminho)),
                            f'{caminho} saiu do Git — isto nao era desta missao')
        colector = ler(os.path.join(RAIZ, 'coleta', 'italy_recurrent_collect.mjs'))
        self.assertIn('collection-store', colector,
                      'o coletor italiano foi alterado')
        self.assertNotIn('raw_asset', colector,
                         'o coletor passou a escrever no Supabase — G-02 era '
                         'para ficar intocado')


class AsCincoArmadilhas(unittest.TestCase):
    """As cinco situações que NÃO podem voltar.

    Nenhuma delas congela 49, 43 ou 6: todas conferem CONSISTÊNCIA entre campos
    e entre fontes. O acervo pode crescer à vontade — o que não pode é a
    descrição contradizer a medição, nem um número aparecer sem quem o sustente.
    """

    @classmethod
    def setUpClass(cls):
        cls.B = js(CORPUS)['ACERVO_EM_PDF']
        cls.OC = js(CORPUS)['OCORRENCIA_E_CONTEUDO']
        cls.R = js(GP)
        cls.S = js(STATE)
        cls.t_run = texto_da_peca(peca(cls.S, 'C-GOLDEN-PATH-PDF'))
        cls.t_bruto = texto_da_peca(peca(cls.S, 'C-IT-PDF-BRUTO'))

    # ── 1 ────────────────────────────────────────────────────────────────
    def test_A1_a_descricao_nao_pode_negar_a_medicao(self):
        """«TEXT_DERIVATION_EXISTS=NAO» com zero ocorrências sem derivação."""
        sem = self.B['OCORRENCIAS_SEM_DERIVACAO']
        texto = self.B['O_QUE_E'].upper()
        if sem == 0:
            self.assertNotIn('TEXT_DERIVATION_EXISTS=NAO', texto,
                             'a descricao nega a derivacao e a medicao diz que '
                             'nao ha nenhuma ocorrencia sem ela')
            self.assertNotIn('NAO FOI DERIVADO', texto)
        else:
            self.assertNotIn('TEXT_DERIVATION_EXISTS=SIM', texto,
                             f'ha {sem} ocorrencias sem derivacao e a descricao '
                             f'afirma que todas tem')

    def test_A1b_as_ocorrencias_fecham(self):
        self.assertEqual(
            self.B['OCORRENCIAS'],
            self.B['OCORRENCIAS_COM_DERIVACAO'] + self.B['OCORRENCIAS_SEM_DERIVACAO'],
            'com + sem tem de dar o total; se nao der, alguma ocorrencia sumiu '
            'da conta sem se queixar')

    def test_A1c_o_nome_do_bloco_nao_pode_voltar_a_mentir(self):
        """«BRUTO POR LER» descrevia um mundo em que nada tinha sido lido."""
        bruto_dados = js(CORPUS)
        self.assertNotIn('BRUTO_POR_LER', bruto_dados,
                         'o nome antigo voltou. Ele afirma que o acervo esta por '
                         'ler, e a medicao diz o contrario')

    # ── 2 · 3 ────────────────────────────────────────────────────────────
    def test_A2_custo_zero_so_com_base_declarada(self):
        custo = self.R.get('COST_USD')
        if isinstance(custo, (int, float)):
            self.assertTrue(self.R.get('COST_BASIS'),
                            'ha um valor de custo e nao ha base: um zero sem '
                            'base le-se como conta fechada')
            self.assertEqual('NAO_SE_APLICA', self.R.get('COST_ACCOUNTING'),
                             'se houve contabilidade monetaria, ela tem de ser '
                             'nomeada; se nao houve, tem de dizer que nao se aplica')
            self.assertIn(self.R.get('ROTA_PAGA_USADA'), ('NAO', 'SIM'),
                          'o facto observado — rota paga usada ou nao — tem de '
                          'estar preservado ao lado do numero')

    def test_A3_o_mapa_nunca_mostra_valor_monetario_sem_base(self):
        self.assertRegex(self.t_run.lower(), r'contabilidade monet[aá]ria',
                         'o mapa mostra custo e nao diz se houve contabilidade')
        self.assertNotRegex(
            self.t_run, r'(?i)custo[^\n]{0,20}(USD|US\$|€|EUR)\s*0[.,]0*\b',
            'o mapa apresentou o zero como cifra fechada')

    # ── 4 ────────────────────────────────────────────────────────────────
    def test_A4_ocorrencia_menos_conteudo_nunca_e_perda(self):
        oc, un = self.OC['OCORRENCIAS'], self.OC['CONTEUDOS_UNICOS']
        self.assertGreaterEqual(oc, un, 'ha mais conteudos do que caminhos')
        self.assertEqual(oc - un, self.OC['OCORRENCIAS_DE_CONTEUDO_REPETIDO'],
                         'a diferenca tem de ser exatamente a repeticao medida')
        # e o LOST publicado nao pode ser essa diferenca quando ela e > 0
        if oc != un:
            self.assertNotEqual(
                oc - un, self.R['COUNTS']['LOST'],
                'o perdido publicado e exatamente ocorrencias menos conteudos — '
                'e essa e a subtracao errada que a COL-LAW-501 proibe')

    # ── 5 ────────────────────────────────────────────────────────────────
    def test_A5_nenhum_numero_da_estrada_e_apresentado_a_mao(self):
        """Nem no gerador, nem no censo, nem na app publicada."""
        # SO NUMEROS COM DOIS DIGITOS OU MAIS. Um numero de um digito colide
        # com tudo — `[:6]`, `linha 6`, `parents[2]` — e um teste que reprova
        # por causa de uma fatia de lista ensina toda a gente a ignora-lo.
        alvos = [n for n in (self.OC['OCORRENCIAS'],
                             self.OC['CONTEUDOS_UNICOS'],
                             self.OC['OCORRENCIAS_DE_CONTEUDO_REPETIDO'])
                 if n >= 10]
        fontes = {
            'gerador': ler(GERADOR),
            'censo': ler(CENSO),
            'app': ler(os.path.join(RAIZ, 'italia-portale', 'client',
                                    'system-map', 'map.js')),
        }
        for nome, src in fontes.items():
            codigo = '\n'.join(l for l in src.splitlines()
                               if not l.lstrip().startswith(('#', '//')))
            codigo = re.sub(r'"""[\s\S]*?"""', '', codigo)
            for n in alvos:
                self.assertNotRegex(
                    codigo, r'[:=]\s*%d\b' % n,
                    f'{nome}: o valor {n} esta cravado. Hoje coincide; amanha o '
                    f'acervo cresce e ele fica igual, com cara de medicao')


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=1).result
    ok = r.wasSuccessful()
    print('\nTESTES_OBSERVABILIDADE=%s · %d testes'
          % ('PASS' if ok else 'FAIL', r.testsRun))
    raise SystemExit(0 if ok else 1)

