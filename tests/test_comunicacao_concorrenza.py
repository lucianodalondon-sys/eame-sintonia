#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONCORRENZA-V1 — o extrator da ferramenta Concorrenza e a gaveta errada da Didacta.

    py -m unittest tests.test_comunicacao_concorrenza -v

Dois assuntos, um ficheiro, porque os dois respondem a mesma pergunta da
ferramenta: «isto e um concorrente, e o que ele disse?».

1. A CLASSIFICACAO DA FONTE. A candidata CAND-0412 («Scopri l'evento»,
   fieradidacta.indire.it — uma feira escolar do INDIRE) recebeu T9 (COMPETITORS)
   porque a regra do nome lia o CAMINHO do endereco e achou «italia» em
   `visita-didacta-italia-edizione-abruzzo`. A mesma regra deu T9 ao
   «SpazioRegione» porque «Spa» casava dentro de «Spazio».

2. O EXTRATOR. Empresa, produto, cultura/problema, lugar, tempo e tipo — com a
   alegacao da empresa separada do facto regulatorio (CAP-COMP).

Os textos marcados SINTETICO sao inventados para o caso; os outros sao copia
literal de atividades do repo (build/ITALY-REALITY-HANDOFF-V2/.../competitor-activities.json).
Nenhum dado da Sala: ela nao existe na nuvem.
"""
import ast
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'curadoria'))
import _gavetas  # noqa: E402,F401

import atribuir_source_id as ASI  # noqa: E402
import comunicacao_classificar as cl  # noqa: E402
import comunicacao_concorrenza as C  # noqa: E402

NS = C.NAO_SEI


# ═══════════════════════════════════════════════ 1 · A GAVETA DA FONTE
class T1GavetaDaFonte(unittest.TestCase):

    def test_didacta_nao_e_concorrente(self):
        # CAND-0412, copia literal do livro de candidatas
        t, porque = ASI.territorio_de({
            'NOME': "Scopri l'evento",
            'URL': 'https://fieradidacta.indire.it/it/visita-didacta-italia-edizione-abruzzo/'})
        self.assertNotEqual(t, 'T9', porque)
        self.assertEqual(t, 'NAO SEI', porque)

    def test_spa_so_como_palavra_inteira(self):
        # IT-T9-022: «Spa» dentro de «SpazioRegione»
        t, porque = ASI.territorio_de({
            'NOME': 'SpazioRegione - prenota online',
            'URL': 'https://spazioregioneprenota.kioskbuk.it/intro.aspx'})
        self.assertNotEqual(t, 'T9', porque)

    def test_empresa_de_verdade_continua_t9(self):
        for nome, url in (('Sipcam Italia', 'https://www.sipcamitalia.it/'),
                          ('ADAMA Italia S.r.l.', 'https://www.adama.com/italia/'),
                          ('Syngenta S.p.A.', 'https://www.syngenta.it/'),
                          ('Gruppo Esempio', 'https://esempio.it/')):  # SINTETICO
            self.assertEqual(ASI.territorio_de({'NOME': nome, 'URL': url})[0], 'T9', nome)

    def test_a_casa_do_endereco_continua_a_contar(self):
        # IT-T12-124: o nome nao diz nada, a casa (assam.marche.it) diz
        t, _ = ASI.territorio_de({'NOME': 'Sedi e Uffici',
                                  'URL': 'https://www.assam.marche.it/agenzia/sedi-e-uffici'})
        self.assertEqual(t, 'T12')

    def test_o_caminho_nao_decide(self):
        # IT-T5-065: «/ricerca?» e a caixa de busca da Regione, nao pesquisa cientifica
        t, _ = ASI.territorio_de({'NOME': '#Bandi',
                                  'URL': 'https://www.regione.lombardia.it/ricerca?q=Bandi'})
        self.assertEqual(t, 'T12')
        # SINTETICO: uma pagina qualquer com «italia» no caminho de um site sem sinal
        t, _ = ASI.territorio_de({'NOME': 'Programma',
                                  'URL': 'https://esempio.org/eventi/tour-italia-2026/'})
        self.assertEqual(t, 'NAO SEI')


# ═══════════════════════════════════════════════ 2 · PRODUTO
class T2Produto(unittest.TestCase):

    def test_marca_de_substancia_nao_e_produto(self):
        # literal, BASF, PAID
        m = C.marcas_do_texto('Con Belanty®, il fungicida BASF a base di Revysol®, proteggi')
        self.assertEqual(m['PRODUTOS'], ['Belanty'])
        self.assertEqual(m['MARCAS_DE_SUBSTANCIA'], ['Revysol'])

    def test_duas_substancias_ligadas_por_e(self):
        m = C.marcas_do_texto('Dagonis®, a base di Xemium® e F500® protegge')  # SINTETICO
        self.assertEqual(m['PRODUTOS'], ['Dagonis'])
        self.assertEqual(m['MARCAS_DE_SUBSTANCIA'], ['Xemium', 'F500'])

    def test_virgula_e_aposto_nao_ponte(self):
        # literal, FMC: Exirel e o produto, Cyazypyr a substancia
        m = C.marcas_do_texto("Grazie all'innovativo principio attivo Cyazypyr®, Exirel® protegge")
        self.assertEqual(m['PRODUTOS'], ['Exirel'])
        self.assertEqual(m['MARCAS_DE_SUBSTANCIA'], ['Cyazypyr'])

    def test_palavra_depois_da_marca(self):
        m = C.marcas_do_texto('Introduction of Inatreq™ active at Cereals')  # literal, CORTEVA
        self.assertEqual(m['PRODUTOS'], [])
        self.assertEqual(m['MARCAS_DE_SUBSTANCIA'], ['Inatreq'])

    def test_nome_da_empresa_com_marca_nao_e_produto(self):
        m = C.marcas_do_texto('Lead for Corteva Agriscience™, discusses')  # literal
        self.assertEqual(m['PRODUTOS'], [])
        m = C.marcas_do_texto('BASF® presenta Cabrio® WG')  # SINTETICO
        self.assertEqual(m['PRODUTOS'], ['Cabrio'])

    def test_sem_marca_sem_produto(self):
        m = C.marcas_do_texto('RESA ALTA con DIFESA TOTALE per il tuo mais')  # SINTETICO
        self.assertEqual(m['PRODUTOS'], [])

    def test_mesma_marca_em_duas_grafias_e_uma(self):
        m = C.marcas_do_texto('OMNERA® LQM®: il nuovo erbicida. Omnera® LQM® e una novita')  # literal
        self.assertEqual([p.upper() for p in m['PRODUTOS']].count('OMNERA'), 1)


# ═══════════════════════════════════════════════ 3 · EMPRESA E TIPO
ANUNCIO = {  # literal, BASF, PAID (texto cortado)
    'ID': 'IT-COMP-ACT-X', 'ACTIVITY_TYPE': 'PAID', 'PLATFORM': 'META_ADS_LIBRARY',
    'COMPANY': 'BASF', 'COUNTRY_REACHED': 'IT', 'START_DATE': '2025-11-14',
    'CREATIVE_TEXT': ('Le malattie fungine possono compromettere la resa e la qualità del mais. '
                      'Con Belanty®, il fungicida BASF a base di Revysol®, proteggi la coltura '
                      'in modo efficace e duraturo. Applicato in fase di fioritura, controlla la '
                      'fusariosi e riduce il rischio di micotossine DON.')}


class T3EmpresaETipo(unittest.TestCase):

    def test_empresa_vem_do_canal_declarado(self):
        r = C.extrair(ANUNCIO)
        self.assertEqual(r['COMPANY'], 'BASF')
        self.assertEqual(r['COMPANY_ROLE'], 'CONCORRENTE')

    def test_empresa_citada_por_terceiro_nao_e_quem_fala(self):
        # SINTETICO: uma revista que fala da BASF nao e a BASF a falar
        r = C.extrair({'TITLE': 'BASF lancia Cabrio® WG su vite', 'URL': 'https://rivista.example/news/x'})
        self.assertEqual(r['COMPANY'], NS)
        self.assertEqual(r['EMPRESAS_NOMEADAS_NO_TEXTO'], ['BASF'])
        self.assertEqual(r['TIPO_DE_COMUNICACAO'], NS)

    def test_adama_nao_e_concorrente(self):
        r = C.extrair({'COMPANY': 'ADAMA Italia', 'ACTIVITY_TYPE': 'PAID', 'TEXT': 'x'})  # SINTETICO
        self.assertEqual(r['COMPANY_ROLE'], 'ADAMA_PROPRIA')

    def test_quatro_tipos(self):
        self.assertEqual(C.extrair(ANUNCIO)['TIPO_DE_COMUNICACAO'], C.ANUNCIO_PAGO)
        self.assertEqual(C.extrair({'COMPANY': 'FMC', 'ACTIVITY_TYPE': 'ORGANIC_VIDEO',
                                    'PLATFORM': 'YOUTUBE'})['TIPO_DE_COMUNICACAO'], C.ORGANICO)
        # SINTETICO: sala de imprensa no canal da propria empresa
        self.assertEqual(C.extrair({'CHANNEL': 'Syngenta Italia',
                                    'URL': 'https://www.syngenta.it/press/nuovo-fungicida'})
                         ['TIPO_DE_COMUNICACAO'], C.COMUNICADO)
        self.assertEqual(C.extrair({'ITEM_KIND': 'REGISTRATION', 'NOME_PRODOTTO': 'X'})
                         ['TIPO_DE_COMUNICACAO'], C.REGISTO)

    def test_endereco_de_imprensa_sem_empresa_nao_e_comunicado(self):
        r = C.extrair({'URL': 'https://jornal.example/press/basf-lancia'})  # SINTETICO
        self.assertEqual(r['TIPO_DE_COMUNICACAO'], NS)


# ═══════════════════════════════════════════════ 4 · ALEGACAO x FACTO
class RegistoSintetico(C.RegistoEmMemoria):
    """SINTETICO: tres linhas inventadas no formato do contrato. Nao e o registo italiano."""
    def __init__(self):
        super().__init__([
            {'NUMERO_REGISTRAZIONE': '099901', 'NOME_PRODOTTO': 'BELANTY',
             'TITOLARE': 'BASF Italia S.p.A.', 'SOSTANZE_ATTIVE': ['mefentrifluconazolo'],
             'STATO': 'AUTORIZZATO', 'SNAPSHOT': 'SINTETICO'},
            {'NUMERO_REGISTRAZIONE': '099902', 'NOME_PRODOTTO': 'ENERVIN SC',
             'TITOLARE': 'Distributore Esempio S.r.l.', 'SOSTANZE_ATTIVE': ['ametoctradin'],
             'STATO': 'AUTORIZZATO', 'SNAPSHOT': 'SINTETICO'},
            {'NUMERO_REGISTRAZIONE': '099903', 'NOME_PRODOTTO': 'ENERVIN TOP',
             'TITOLARE': 'BASF Italia S.p.A.', 'SOSTANZE_ATTIVE': ['ametoctradin'],
             'STATO': 'AUTORIZZATO', 'SNAPSHOT': 'SINTETICO'},
        ], fonte='SINTETICO-T4')


class T4AlegacaoEFacto(unittest.TestCase):

    def test_anuncio_so_tem_alegacoes(self):
        r = C.extrair(ANUNCIO)
        self.assertEqual(r['CLAIM_DOMAIN'], 'COMPANY_CLAIM')
        self.assertGreaterEqual(r['CONTAGEM']['ALEGACOES'], 2)
        self.assertEqual(r['FACTOS_REGULATORIOS'], [])
        self.assertTrue(all(a['CAMADA'] == 'COMUNICACAO' for a in r['ALEGACOES']))

    def test_empresa_dizer_que_e_autorizado_e_alegacao(self):
        r = C.extrair({'COMPANY': 'BASF', 'ACTIVITY_TYPE': 'PAID',  # literal (Efficon, BASF)
                       'TEXT': "È stata concessa un’autorizzazione emergenziale per Efficon® Orange."})
        self.assertEqual(r['FACTOS_REGULATORIOS'], [])
        self.assertIn('ALEGACAO_REGULATORIA', r['ALEGACOES'][0]['TIPOS'])

    def test_sem_registo_e_nao_sei_e_nao_falso(self):
        v = C.extrair(ANUNCIO)['VALIDACAO_T4'][0]
        self.assertEqual(v['ESTADO'], 'REGISTO_NAO_LIGADO')
        self.assertEqual(v['VALIDADO'], NS)

    def test_registo_confirma_o_mesmo_titular(self):
        r = C.extrair(ANUNCIO, RegistoSintetico())
        v = r['VALIDACAO_T4'][0]
        self.assertEqual((v['ESTADO'], v['VALIDADO'], v['PRODUCT_ID']),
                         ('ENCONTRADO_MESMO_TITULAR', True, '099901'))
        self.assertEqual(r['CONTAGEM']['FACTOS_REGULATORIOS'], 1)
        self.assertTrue(all(f['CAMADA'] == 'REGULATORIO' for f in r['FACTOS_REGULATORIOS']))
        # as duas contagens nao se somam nem se contaminam
        self.assertEqual(r['CONTAGEM']['ALEGACOES'], C.extrair(ANUNCIO)['CONTAGEM']['ALEGACOES'])
        self.assertIn('venda', r['FACTOS_REGULATORIOS'][0]['NAO_DIZ'])

    def test_marca_mais_sufixo_e_titulares_diferentes(self):
        v = C.validar_no_registo('Enervin', 'BASF', RegistoSintetico())
        self.assertEqual(v['ESTADO'], 'AMBIGUO_TITULARES_DIFERENTES')
        self.assertEqual(v['PRODUCT_ID'], NS)
        v = C.validar_no_registo('Enervin', NS, RegistoSintetico())
        self.assertEqual(v['VALIDADO'], NS)

    def test_nao_encontrado_nao_prova_inexistencia(self):
        v = C.validar_no_registo('Revysol', 'BASF', RegistoSintetico())
        self.assertEqual(v['ESTADO'], 'NAO_ENCONTRADO_NO_REGISTO')
        self.assertIn('INT-LAW-112', v['PORQUE'])

    def test_item_de_registo_e_facto_sem_alegacao(self):
        r = C.extrair({'ITEM_KIND': 'REGISTRATION', 'SOURCE_ID': 'IT-T4-001',  # SINTETICO
                       'NOME_PRODOTTO': 'BELANTY', 'NUMERO_REGISTRAZIONE': '099901',
                       'TITOLARE': 'BASF Italia S.p.A.', 'TEXT': 'efficace e autorizzato'})
        self.assertEqual(r['CLAIM_DOMAIN'], 'REGULATORY_FACT')
        self.assertEqual(r['CONTAGEM'], {'ALEGACOES': 0, 'FACTOS_REGULATORIOS': 1})


# ═══════════════════════════════════════════════ 5 · LUGAR, TEMPO, CULTURA
class T5LugarTempoCultura(unittest.TestCase):

    def test_data_do_anuncio_nao_e_data_do_facto(self):
        r = C.extrair(ANUNCIO)
        self.assertEqual(r['COMMUNICATION_TIME'], '2025-11-14')
        self.assertEqual(r['FACT_TIME'], NS)

    def test_alcance_nao_vira_lugar_do_facto(self):
        r = C.extrair(ANUNCIO)
        self.assertEqual(r['COUNTRY_REACHED'], 'IT')
        self.assertEqual(r['COUNTRY_OF_FACT'], NS)
        r = C.extrair(dict(ANUNCIO, CREATIVE_TEXT='Difesa della vite in Veneto con Cabrio®'))
        self.assertEqual((r['COUNTRY_OF_FACT'], r['REGION_OF_FACT']), ('IT', ['veneto']))

    def test_cultura_e_problema(self):
        r = C.extrair(ANUNCIO)
        self.assertIn('MAIZE', r['CROP_TERMS'])
        self.assertIn('FUSARIUM', r['ISSUE_TERMS'])
        r = C.extrair({'TEXT': "c'e un nuovo alleato nella difesa del melo contro la ticchiolatura"})
        self.assertEqual((r['CROP_TERMS'], r['ISSUE_TERMS']), (['POME_FRUIT'], ['SCAB']))

    def test_pero_espanhol_nao_e_pereira(self):
        r = C.extrair({'TEXT': 'Es eficaz, pero hay que aplicarlo bien'})  # SINTETICO
        self.assertEqual(r['CROP_TERMS'], [NS])


# ═══════════════════════════════════════════════ 6 · UM DONO, E O CORPUS DO REPO
class T6DonoECorpus(unittest.TestCase):

    def test_lista_de_marcas_igual_a_do_pacote(self):
        with open(os.path.join(ROOT, 'pacote', 'pacote_camadas.py'), encoding='utf-8') as f:
            src = f.read()
        for no in ast.walk(ast.parse(src)):
            if isinstance(no, ast.Assign) and any(getattr(t, 'id', '') == 'MARCAS' for t in no.targets):
                self.assertEqual(ast.literal_eval(no.value), C.MARCAS)
                return
        self.fail('MARCAS sumiu de pacote_camadas.py')

    def test_usa_as_tabelas_do_classificador(self):
        self.assertIs(C.cl, cl)

    def test_561_atividades_do_repo(self):
        with open(C.FONTE_DO_REPO, encoding='utf-8') as f:
            atividades = json.load(f)['ACTIVITIES']
        m = C.medir(atividades)
        self.assertEqual(m['ITENS'], 561)
        self.assertEqual(m['FACTOS_REGULATORIOS'], 0)   # nenhum registo foi ligado
        regs = [C.extrair(a) for a in atividades]
        prods = {p for r in regs for p in r['PRODUCTS_PROVED']}
        for subst in ('Revysol', 'F500', 'Xemium', 'Cyazypyr', 'Inatreq'):
            self.assertNotIn(subst, prods)
        self.assertIn('Exirel', prods)
        self.assertNotIn('Agriscience', prods)


if __name__ == '__main__':
    unittest.main(verbosity=2)
