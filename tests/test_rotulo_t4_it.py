#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O PARSER CANÓNICO DO RÓTULO T4 ITALIANO (coleta/rotulo_t4_it.py).

    cd tests && python -m unittest test_rotulo_t4_it

Sem rede. Duas espécies de prova, e cada teste diz qual usa:

    REAL        ficheiros que já estão no repo: o registo oficial
                (IT-T4-001 PROD_FTS_6_20260907.csv), as frases literais das
                linhas de tabela dos 163 rótulos (IT-DOSES-2026-09-06.json, lidas
                por geometria), as citações dos pares (IT-ROTULOS-PARES.json) e a
                amostra de atos europeus (EU-T4-001)
    SINTETICO   rótulos escritos aqui, marcados SINTETICO no próprio texto.
                Os PDFs dos 163 rótulos NÃO estão no repo (só o _MANIFESTO).
"""
import json
import os
import re
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(ROOT, 'coleta'))
import rotulo_t4_it as R  # noqa: E402

CSV = os.path.join(ROOT, 'data', 'samples', 'IT-SOURCE-SAMPLES', 'IT-T4-001', 'PROD_FTS_6_20260907.csv')
DOSES = os.path.join(ROOT, 'data', 'samples', 'IT-DOSE-ROTULO', 'IT-DOSES-2026-09-06.json')
PARES = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS', 'IT-ROTULOS-PARES.json')

_REG = None


def registo():
    global _REG
    if _REG is None:
        _REG = R.ler_registo(CSV)
    return _REG


SINTETICO = """SINTETICO - rotulo de teste, nao e documento real
PIRIMOR 50
Insetticida aficida in granuli idrodispersibili
Composizione: 100 g di prodotto contengono: Pirimicarb puro g 50
Titolare dell'autorizzazione: ADAMA Italia S.r.l., Via Zanica 19, Grassobbio (BG)
Registrazione Ministero della Salute n. 4701 del 17/03/1982

CAMPI DI IMPIEGO
Coltura            Parassiti                         Dose g/hl
Pesco, nettarine   Myzus persicae, Hyalopterus spp.  50-75       alla comparsa delle prime colonie; max 1 trattamento all'anno
Pomodoro           Macrosiphum euphorbiae             60          solo in serra; ogni 10 giorni
Lattuga            Nasonovia ribisnigri               75          BBCH 14-19

Sospendere i trattamenti 7 giorni prima della raccolta.
ATTENZIONE: da impiegarsi esclusivamente per gli usi e alle condizioni riportate in questa etichetta
Etichetta autorizzata con Decreto Dirigenziale del 22 luglio 2024 valida dal 22 luglio 2024 al 18 novembre 2024
"""

SEM_TABELA = """SINTETICO - rotulo sem tabela de uso legivel
PIRIMOR 50
Registrazione Ministero della Salute n. 4701
Il prodotto va impiegato secondo le buone pratiche agricole e le indicazioni del tecnico.
Conservare in luogo fresco e asciutto, lontano da alimenti e bevande.
"""


def _pdf_minimo(linhas):
    """PDF de uma página com texto — SINTETICO, montado à mão (sem biblioteca)."""
    corpo = 'BT /F1 10 Tf 40 800 Td 12 TL\n' + ''.join(
        '(%s) Tj T*\n' % l.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)') for l in linhas) + 'ET'
    objs = ['<< /Type /Catalog /Pages 2 0 R >>',
            '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R '
            '/Resources << /Font << /F1 5 0 R >> >> >>',
            '<< /Length %d >>\nstream\n%s\nendstream' % (len(corpo), corpo),
            '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    out, offs = '%PDF-1.4\n', []
    for i, o in enumerate(objs, 1):
        offs.append(len(out.encode('latin-1')))
        out += '%d 0 obj\n%s\nendobj\n' % (i, o)
    xref = len(out.encode('latin-1'))
    out += 'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1)
    out += ''.join('%010d 00000 n \n' % o for o in offs)
    out += 'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, xref)
    return out.encode('latin-1')


def _tem_extrator_pdf():
    try:
        R._pdf_para_texto(_pdf_minimo(['teste']))
        return True
    except Exception:
        return False


def _todos_os_valores(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _todos_os_valores(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _todos_os_valores(v)
    else:
        yield obj


# ══════════════════════════════════════════════════════════════════════════════
class ORegistoOficial(unittest.TestCase):
    """REAL — IT-T4-001, CSV do Ministero, snapshot 20260907."""

    def test_pirimor_sai_com_os_campos_do_registo(self):
        f = R.ficha_do_registo(registo(), '004701')
        self.assertTrue(f['NO_REGISTO'])
        self.assertEqual(f['PRODUTO']['VALOR'], 'PIRIMOR 50')
        self.assertEqual(f['TITULAR']['VALOR'], 'ADAMA ITALIA S.R.L.')
        self.assertEqual(f['PRINCIPIOS_ATIVOS']['VALOR'], [{'SUBSTANCIA': 'PIRIMICARB', 'TEOR_POR_100G': '50.0 g'}])
        self.assertEqual(f['FORMULACAO']['VALOR'], {'CODIGO': 'WG', 'DESCRICAO': 'GRANULARE IDRODISPERSIBILE'})
        self.assertEqual(f['VALIDADE_DA_AUTORIZACAO']['VALOR'], {'REGISTADO_EM': '1982-03-17', 'EXPIRA_EM': '2026-10-31'})
        self.assertIs(f['AUTORIZACAO_NACIONAL_VIVA']['VALOR'], True)
        # só o registo disse: é ENCONTRADO, não VERIFICADO
        self.assertEqual(f['TITULAR']['ESTADO'], R.ENCONTRADO)

    def test_numero_sem_zeros_a_esquerda_e_o_mesmo_registo(self):
        self.assertEqual(R.ficha_do_registo(registo(), '4701')['PRODUTO']['VALOR'], 'PIRIMOR 50')

    def test_revogado_e_encontrado_e_nao_vivo(self):
        f = R.ficha_do_registo(registo(), '000001')   # ENOVIT, Revocato
        self.assertEqual(f['ESTADO_ADMINISTRATIVO']['VALOR'], 'Revocato')
        self.assertIs(f['AUTORIZACAO_NACIONAL_VIVA']['VALOR'], False)
        self.assertEqual(f['AUTORIZACAO_NACIONAL_VIVA']['ESTADO'], R.ENCONTRADO)

    def test_os_estados_vivos_do_ministero(self):
        vivos = {r['stato_amministrativo'] for r in registo().values() if R.VIVO.match(r['stato_amministrativo'])}
        mortos = {r['stato_amministrativo'] for r in registo().values()} - vivos
        self.assertEqual(mortos, {'Revocato', 'Scaduto', 'Sospeso'})

    def test_duas_substancias_ficam_alinhadas_com_o_teor(self):
        f = R.ficha_do_registo(registo(), '009757')   # SPYRALE
        self.assertEqual(f['PRINCIPIOS_ATIVOS']['VALOR'],
                         [{'SUBSTANCIA': 'DIFENOCONAZOLE', 'TEOR_POR_100G': '10.1 g'},
                          {'SUBSTANCIA': 'FENPROPIDIN', 'TEOR_POR_100G': '37.8 g'}])

    def test_registo_que_nao_existe_e_nao_conhecido_e_nao_falso(self):
        f = R.ficha_do_registo(registo(), '999999')
        self.assertFalse(f['NO_REGISTO'])
        for k in ('PRODUTO', 'TITULAR', 'PRINCIPIOS_ATIVOS', 'AUTORIZACAO_NACIONAL_VIVA'):
            self.assertEqual(f[k]['ESTADO'], R.NAO_CONHECIDO, k)
            self.assertIsNone(f[k]['VALOR'], k)


# ══════════════════════════════════════════════════════════════════════════════
class OCabecalhoComFrasesReais(unittest.TestCase):
    """REAL — citações dos pares: o número do rótulo bate com o registo do par."""

    @classmethod
    def setUpClass(cls):
        with open(PARES, encoding='utf-8') as fh:
            d = json.load(fh)
        cls.pares = [(p['REGISTRATION_ID'], p.get('CITACAO_DA_LINHA') or '') for p in d['PARES']]

    def test_numero_de_registo_no_rotulo_e_o_do_par(self):
        vistos = 0
        for reg, cit in {(r, c) for r, c in self.pares if 'Registrazione Ministero' in c}:
            cab = R.cabecalho_do_rotulo(cit)
            self.assertEqual(cab['NUMERO_REGISTO_NO_ROTULO']['VALOR'], reg, cit[:120])
            vistos += 1
        self.assertGreaterEqual(vistos, 7)   # medido em 26/09: 7 pares (registo, citação) distintos

    def test_data_do_decreto_sai_das_frases_reais(self):
        cits = {c for _, c in self.pares if re.search(r'Etichetta autorizzata con Decreto', c)}
        self.assertGreaterEqual(len(cits), 11)
        for c in cits:
            v = R.cabecalho_do_rotulo(c)['DATA_DO_DECRETO']
            self.assertEqual(v['ESTADO'], R.ENCONTRADO, c[:160])
            self.assertRegex(v['VALOR'], r'^20\d\d-\d\d-\d\d$')

    def test_decreto_com_mes_por_extenso(self):
        c = [c for _, c in self.pares if 'Decreto Dirigenziale del 22 luglio 2024' in c][0]
        cab = R.cabecalho_do_rotulo(c)
        self.assertEqual(cab['DATA_DO_DECRETO']['VALOR'], '2024-07-22')
        self.assertEqual(cab['VALIDADE_DO_ROTULO']['VALOR'], {'DE': '2024-07-22', 'ATE': '2024-11-18'})


# ══════════════════════════════════════════════════════════════════════════════
class ADoseContraOLeitorGeometrico(unittest.TestCase):
    """REAL — 839 linhas de tabela de 21 rótulos, lidas por posição (IT-DOSES).

    O texto guardado é corrido: perdeu as colunas. A régua é de PRECISÃO: quando
    o parser dá uma dose, tem de ser a do leitor geométrico. Quando não sabe a
    coluna, cala-se (NAO_CONHECIDO) em vez de escolher um número.
    """

    @classmethod
    def setUpClass(cls):
        with open(DOSES, encoding='utf-8') as fh:
            d = json.load(fh)
        cls.linhas = [x for l in d['LABELS'] for x in l.get('ROWS', [])]

    @staticmethod
    def _nums(s):
        return [float(x.replace(',', '.')) for x in re.findall(r'\d+(?:[.,]\d+)?', s or '')]

    def test_quando_da_dose_e_a_do_leitor_geometrico(self):
        iguais, diferentes, calado = 0, [], 0
        for x in self.linhas:
            u = x['DOSE_PER_HECTARE_UNIT']
            if u in ('NOT_PRESENT', 'NOT_PRESERVED') or x['DOSE_CONCENTRATION_UNIT'] != 'NOT_PRESENT':
                continue   # só as tabelas com UMA unidade de dose
            ds = R.doses_da_linha(x['SOURCE_QUOTE'], [u])
            ref = self._nums(x['DOSE_PER_HECTARE'])
            if not ds:
                calado += 1
            elif ref and (ds[0]['MIN'], ds[0]['MAX']) == (ref[0], ref[-1]):
                iguais += 1
            else:
                diferentes.append((x['SOURCE_QUOTE'][:90], ds[0]['LITERAL'], x['DOSE_PER_HECTARE']))
        self.assertEqual(diferentes, [])
        self.assertGreaterEqual(iguais, 54)    # piso medido em 26/09: 54 de 493
        self.assertEqual(iguais + calado, 493)

    def test_duas_unidades_no_cabecalho_e_numero_sem_unidade_nao_se_atribui(self):
        for x in self.linhas:
            if x['DOSE_CONCENTRATION_UNIT'] in ('NOT_PRESENT', 'NOT_PRESERVED'):
                continue
            if x['DOSE_PER_HECTARE_UNIT'] in ('NOT_PRESENT', 'NOT_PRESERVED'):
                continue
            q = x['SOURCE_QUOTE']
            if R.RX_UNIDADE.search(q):
                continue
            self.assertEqual(R.doses_da_linha(q, [x['DOSE_CONCENTRATION_UNIT'], x['DOSE_PER_HECTARE_UNIT']]), [], q)

    def test_numero_de_aplicacoes_e_dias_nao_viram_dose(self):
        q = 'Pomodoro e melanzana Aphis spp. 2 applicazioni a distanza di 7-12 giorni'
        self.assertEqual(R.doses_da_linha(q, ['g/ha']), [])

    def test_bbch_nao_vira_faixa_de_dose(self):
        self.assertEqual([(d['MIN'], d['MAX']) for d in R.doses_da_linha('Lattuga 75 BBCH 14-19', ['g/hl'])],
                         [(75.0, 75.0)])

    def test_dose_com_unidade_na_linha(self):
        ds = R.doses_da_linha('Vite: 1,5 - 2 l/ha oppure 150-200 ml/hl')
        self.assertEqual([(d['MIN'], d['MAX'], d['UNIDADE']) for d in ds],
                         [(1.5, 2.0, 'l/ha'), (150.0, 200.0, 'ml/hl')])
        self.assertFalse(any(d['UNIDADE_HERDADA_DO_CABECALHO'] for d in ds))


# ══════════════════════════════════════════════════════════════════════════════
class ORotuloInteiroSintetico(unittest.TestCase):
    """SINTETICO — o caminho inteiro: documento → cabeçalho → conferência → linhas."""

    def ler(self, texto=SINTETICO, reg='004701', pid='IT-PRD-003'):
        return R.ler_rotulo(texto.encode('utf-8'), R.ficha_do_registo(registo(), reg), product_id=pid)

    def test_quatro_linhas_de_uso_com_todos_os_campos(self):
        r = self.ler()
        self.assertEqual(r['ESTADO_DA_LEITURA'], R.ENCONTRADO)
        pares = [(l['CULTURA']['VALOR']['CANONICA'], l['ALVO']['VALOR']['LITERAL']) for l in r['LINHAS_DE_USO']]
        self.assertEqual(pares, [('PESCO', 'Myzus persicae'), ('PESCO', 'Hyalopterus spp'),
                                 ('POMODORO', 'Macrosiphum euphorbiae'), ('LATTUGA', 'Nasonovia ribisnigri')])
        l0 = r['LINHAS_DE_USO'][0]
        self.assertEqual(l0['PRODUCT_ID'], 'IT-PRD-003')
        self.assertEqual(l0['NUMERO_REGISTO'], '004701')
        self.assertEqual(l0['DOSE']['VALOR'][0]['UNIDADE'], 'g/hl')
        self.assertEqual((l0['DOSE']['VALOR'][0]['MIN'], l0['DOSE']['VALOR'][0]['MAX']), (50.0, 75.0))
        self.assertEqual(l0['EPOCA']['VALOR']['LITERAL'], ['alla comparsa'])
        self.assertEqual(l0['MAX_APLICACOES']['VALOR'], {'N': 1, 'POR': 'anno'})
        self.assertEqual(l0['VERSAO_DO_DOCUMENTO']['DATA_DO_DECRETO'], '2024-07-22')
        self.assertEqual(l0['VERSAO_DO_DOCUMENTO']['SHA256'], r['DOCUMENTO']['SHA256'])
        self.assertEqual(l0['VALIDADE_DA_AUTORIZACAO']['VALOR']['EXPIRA_EM'], '2026-10-31')

    def test_registo_e_rotulo_concordam_logo_verificado(self):
        r = self.ler()
        self.assertEqual(r['CONFERENCIA']['REGISTO']['ESTADO'], R.VERIFICADO)
        self.assertEqual(r['CONFERENCIA']['TITULAR']['ESTADO'], R.VERIFICADO)
        for k in ('NUMERO_REGISTO', 'TITULAR', 'PRINCIPIOS_ATIVOS', 'FORMULACAO'):
            self.assertEqual(r['PRODUTO'][k]['ESTADO'], R.VERIFICADO, k)
        self.assertTrue(all(l['ALVO']['ESTADO'] == R.VERIFICADO for l in r['LINHAS_DE_USO']))

    def test_lei_do_par_restricao_e_carencia_nao_saltam_de_linha(self):
        ls = {l['CULTURA']['VALOR']['CANONICA']: l for l in self.ler()['LINHAS_DE_USO']}
        self.assertEqual(ls['POMODORO']['RESTRICOES']['VALOR'], ['solo in serra'])
        self.assertEqual(ls['POMODORO']['INTERVALO_ENTRE_APLICACOES']['VALOR'], '10 giorni')
        self.assertEqual(ls['PESCO']['RESTRICOES']['ESTADO'], R.NAO_CONHECIDO)
        self.assertEqual(ls['LATTUGA']['RESTRICOES']['ESTADO'], R.NAO_CONHECIDO)
        self.assertEqual(ls['LATTUGA']['EPOCA']['VALOR']['BBCH'], [{'DE': '14', 'ATE': '19'}])
        # «Sospendere … 7 giorni» está FORA da tabela: é do documento, não da alface
        self.assertEqual(ls['LATTUGA']['INTERVALO_DE_SEGURANCA']['ESTADO'], R.NAO_CONHECIDO)

    def test_carencia_fora_da_tabela_fica_no_documento(self):
        cab = self.ler()['CABECALHO']
        self.assertEqual(cab['INTERVALO_DE_SEGURANCA_DO_DOCUMENTO']['VALOR'], {'DIAS': 7, 'ANTES_DE': 'raccolta'})

    def test_rotulo_de_outro_registo_e_erro_e_nao_da_linhas(self):
        r = self.ler(reg='002732')   # a ficha é do GOLTIX; o rótulo diz 4701
        self.assertEqual(r['CONFERENCIA']['REGISTO']['ESTADO'], R.ERRO)
        self.assertEqual(r['ESTADO_DA_LEITURA'], R.ERRO)
        self.assertEqual(r['LINHAS_DE_USO'], [])

    def test_titular_diferente_e_erro_declarado(self):
        r = self.ler(texto=SINTETICO.replace('ADAMA Italia S.r.l.', 'SYNGENTA Italia S.p.A.'))
        self.assertEqual(r['CONFERENCIA']['TITULAR']['ESTADO'], R.ERRO)
        self.assertEqual(r['PRODUTO']['TITULAR']['ESTADO'], R.ERRO)

    def test_produto_fora_do_registo_nunca_e_verificado(self):
        r = self.ler(reg='999999')
        self.assertEqual(r['CONFERENCIA']['REGISTO']['ESTADO'], R.NAO_CONHECIDO)
        self.assertTrue(r['LINHAS_DE_USO'])
        self.assertTrue(all(l['ALVO']['ESTADO'] == R.ENCONTRADO for l in r['LINHAS_DE_USO']))
        self.assertEqual(r['PRODUTO']['AUTORIZACAO_NACIONAL_VIVA']['ESTADO'], R.NAO_CONHECIDO)

    def test_rotulo_sem_numero_e_encontrado_nao_verificado(self):
        r = self.ler(texto=SINTETICO.replace('Registrazione Ministero della Salute n. 4701 del 17/03/1982', ''))
        self.assertEqual(r['CONFERENCIA']['REGISTO']['ESTADO'], R.ENCONTRADO)
        self.assertTrue(all(l['ALVO']['ESTADO'] == R.ENCONTRADO for l in r['LINHAS_DE_USO']))

    def test_versao_muda_quando_o_documento_muda(self):
        a = self.ler()['DOCUMENTO']['SHA256']
        b = self.ler(texto=SINTETICO + ' ')['DOCUMENTO']['SHA256']
        self.assertNotEqual(a, b)


# ══════════════════════════════════════════════════════════════════════════════
class NaoProvadoNaoENaoAutorizado(unittest.TestCase):
    """SINTETICO — os quatro estados, e o quinto que não existe."""

    def test_sem_tabela_e_nao_conhecido_com_a_afirmacao_proibida(self):
        r = R.ler_rotulo(SEM_TABELA.encode(), R.ficha_do_registo(registo(), '004701'))
        self.assertEqual(r['ESTADO_DA_LEITURA'], R.NAO_CONHECIDO)
        self.assertEqual(r['LINHAS_DE_USO'], [])
        self.assertIn('NAO_PROVADO != NAO_AUTORIZADO', r['AFIRMACAO_PROIBIDA'])
        # o produto continua vivo no registo: não ler uso não o desautoriza
        self.assertIs(r['PRODUTO']['AUTORIZACAO_NACIONAL_VIVA']['VALOR'], True)

    def test_nenhum_resultado_diz_nao_autorizado(self):
        for texto in (SINTETICO, SEM_TABELA, ''):
            r = R.ler_rotulo(texto.encode(), R.ficha_do_registo(registo(), '004701'))
            estados = {v for v in _todos_os_valores(r) if isinstance(v, str) and v.isupper() and '_' in v}
            self.assertFalse({e for e in estados if 'NAO_AUTORIZ' in e}, texto[:30])

    def test_vocabulario_fechado(self):
        self.assertEqual(R.ESTADOS, ('VERIFICADO', 'ENCONTRADO', 'NAO_CONHECIDO', 'ERRO'))
        with self.assertRaises(ValueError):
            R.campo(True, 'NAO_AUTORIZADO', 'x')
        self.assertIsNone(R.campo('valor', R.NAO_CONHECIDO, 'x')['VALOR'])

    def test_documento_vazio_e_erro(self):
        r = R.ler_rotulo(b'', R.ficha_do_registo(registo(), '004701'))
        self.assertEqual(r['ESTADO_DA_LEITURA'], R.ERRO)
        self.assertIn('0 bytes', r['DOCUMENTO']['MOTIVO'])

    def test_casca_de_html_e_erro_e_nao_rotulo_vazio(self):
        r = R.ler_rotulo(b'<html><body><script>x()</script>Loading</body></html>',
                         R.ficha_do_registo(registo(), '004701'))
        self.assertEqual(r['DOCUMENTO']['TIPO'], 'HTML')
        self.assertEqual(r['ESTADO_DA_LEITURA'], R.ERRO)

    def test_pdf_partido_e_erro_com_motivo(self):
        r = R.ler_rotulo(b'%PDF-1.4\nisto nao e um pdf', R.ficha_do_registo(registo(), '004701'))
        self.assertEqual(r['ESTADO_DA_LEITURA'], R.ERRO)
        self.assertTrue(r['DOCUMENTO']['MOTIVO'])


# ══════════════════════════════════════════════════════════════════════════════
class AprovacaoUENaoEAutorizacaoNacional(unittest.TestCase):
    """REAL — amostra EU-T4-001 (10 atos de 2026) + registo IT-T4-001."""

    def test_substancia_nomeada_num_ato_e_encontrada_com_o_celex(self):
        c = R.aprovacao_ue('pyrimethanil')
        self.assertEqual(c['ESTADO'], R.ENCONTRADO)
        self.assertIn('32026R0355R(01)', [a['CELEX'] for a in c['VALOR']])

    def test_substancia_sem_ato_na_amostra_e_nao_conhecido_nao_falso(self):
        # GOLTIX (metamitron) está vivo em Itália e não tem ato nesta amostra
        c = R.aprovacao_ue('metamitron')
        self.assertEqual(c['ESTADO'], R.NAO_CONHECIDO)
        self.assertIsNone(c['VALOR'])

    def test_nome_parecido_nao_conta(self):
        # «spinosad» está na amostra; «spinosa» não é a mesma substância
        self.assertEqual(R.aprovacao_ue('spinosa')['ESTADO'], R.NAO_CONHECIDO)

    def test_ue_nao_escreve_na_autorizacao_nacional(self):
        f = R.ficha_do_registo(registo(), '000001')   # revogado
        antes = json.dumps(f, sort_keys=True)
        R.aprovacao_ue('thiophanate-methyl')
        self.assertEqual(json.dumps(f, sort_keys=True), antes)
        r = R.ler_rotulo(SINTETICO.encode(), R.ficha_do_registo(registo(), '004701'))
        self.assertNotIn('APROVACAO_UE', json.dumps(r['PRODUTO']))


# ══════════════════════════════════════════════════════════════════════════════
class AsPortasDoDocumento(unittest.TestCase):
    """SINTETICO — HTML e PDF chegam às mesmas linhas que o texto."""

    def test_html_em_tabela(self):
        h = ('<html><body><p>SINTETICO</p><p>Registrazione Ministero della Salute n. 4701</p>'
             '<p>CAMPI DI IMPIEGO</p><table><tr><th>Coltura</th><th>Parassiti</th><th>Dose g/hl</th></tr>'
             '<tr><td>Pomodoro</td><td>Macrosiphum euphorbiae</td><td>60</td><td>solo in serra</td></tr>'
             '</table><p>ATTENZIONE: leggere</p></body></html>')
        r = R.ler_rotulo(h.encode(), R.ficha_do_registo(registo(), '004701'))
        self.assertEqual(r['DOCUMENTO']['TIPO'], 'HTML')
        self.assertEqual(r['CONFERENCIA']['REGISTO']['ESTADO'], R.VERIFICADO)
        self.assertEqual([(l['CULTURA']['VALOR']['CANONICA'], l['ALVO']['VALOR']['LITERAL'])
                          for l in r['LINHAS_DE_USO']], [('POMODORO', 'Macrosiphum euphorbiae')])
        self.assertEqual(r['LINHAS_DE_USO'][0]['RESTRICOES']['VALOR'], ['solo in serra'])

    @unittest.skipUnless(_tem_extrator_pdf(), 'DEPENDENCIA_EM_FALTA: pdftotext (poppler) e pypdf')
    def test_pdf(self):
        pdf = _pdf_minimo(['SINTETICO', 'Registrazione Ministero della Salute n. 4701',
                           'Etichetta autorizzata con Decreto Dirigenziale del 30.07.2025'])
        r = R.ler_rotulo(pdf, R.ficha_do_registo(registo(), '004701'))
        self.assertEqual(r['DOCUMENTO']['TIPO'], 'PDF')
        self.assertEqual(r['CONFERENCIA']['REGISTO']['ESTADO'], R.VERIFICADO)
        self.assertEqual(r['CABECALHO']['DATA_DO_DECRETO']['VALOR'], '2025-07-30')


if __name__ == '__main__':
    unittest.main()
