#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PRODUTOR DE AFIRMACOES (D158) — as garantias, uma a uma.

Todos os textos deste ficheiro sao SINTETICOS e escritos aqui para medir UMA regra cada
um. Nenhum e trecho de um documento real, nenhum e a R9: a prova de que o produtor acha
os trechos reais esta noutro sitio (`provas/d158/r9_pelo_caminho_canonico.py`), e corre
sobre a copia da Sala, nao sobre constantes no codigo.

As perguntas, por ordem:

    i    o trecho e a prova            — TRECHO_LITERAL == texto[INICIO:FIM], sempre
    ii   o ID e deterministico          — mesma entrada, mesmo ASSERTION_ID; byte diferente, ID diferente
    iii  os TESTES NEGATIVOS            — um por caso, cada um com o seu texto
    iv   a fronteira da Collection      — o produtor nao decide relevancia nem liberacao
    v    nenhuma frase da R9 no codigo  — o grep que reprova se alguem a escrever

Sem rede, sem banco, sem modelo.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import unittest
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (RAIZ, os.path.join(RAIZ, 'leis'), os.path.join(RAIZ, 'admissao')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import afirmacao_do_documento as AD            # noqa: E402
import tempo_da_afirmacao as TA                # noqa: E402
import afirmacao_da_fonte as AF                # noqa: E402
import boletim_do_campo as BC                  # noqa: E402

NAO_SEI = AD.NAO_SEI
PUB = ('2026-09-16', 'meta article:published_time')


def _linha(texto, **extra):
    """Uma linha da Sala, sintetica, com a forma que o contrato READY tem."""
    d = {'item_id': 'derived:0', 'run_id': 'XX-T0-0000-00-00-000000-0', 'ordem': 0,
         'source_id': 'XX-T0-000', 'universo': 'T0', 'raw_observation_id': 1,
         'raw_sha256': 'f' * 64, 'raw_storage_path': 'XX/x/DOCUMENT/x.pdf',
         'raw_document_key': 'XX:DOC:1', 'raw_source_url': 'https://exemplo.invalid/x',
         'published_at': PUB[0], 'published_at_basis': PUB[1],
         'raw_captured_at': '2026-09-20 11:07:15+00', 'texto': texto}
    d.update(extra)
    return d


def _produzir(texto, **extra):
    return AD.afirmacoes_do_item(_linha(texto, **extra))['AFIRMACOES']


def _que_diz(afs, comeco):
    return next((a for a in afs if a['TRECHO_LITERAL'].startswith(comeco)), None)


# ── um boletim sintetico: cabecalho de edicao + seccao com periodo passado ───────────────
BOLETIM = (
    "Bollettino settimanale N. 3 Anno I\n"
    "\n"
    "16 - 22 settembre 2026\n"
    "\f"
    "SEZIONE PRECEDENTE Dal 07-09-2026 al 13-09-2026\n"
    "Le grandinate sono state osservate in provincia di Cuneo con danni diffusi ai frutteti.\n"
    "\f"
    "SEZIONE SUCCESSIVA Dal 21-09-2026 al 27-09-2026\n"
    "Le grandinate sono previste in provincia di Asti secondo il modello regionale utilizzato.\n"
)


class TrechoEProva(unittest.TestCase):
    """i · o trecho e a prova: o que o produtor devolve tem de estar no texto, onde ele diz."""

    def test_o_trecho_e_exactamente_texto_inicio_fim(self):
        for af in _produzir(BOLETIM):
            self.assertEqual(af['TRECHO_LITERAL'], BOLETIM[af['POSICAO']['INICIO']:af['POSICAO']['FIM']])

    def test_a_conferencia_aprova_o_que_o_produtor_produz(self):
        for af in _produzir(BOLETIM):
            self.assertEqual(AD.conferir_afirmacao(af, BOLETIM, raw_sha256='f' * 64), [])

    def test_o_basis_do_tempo_esta_no_texto_onde_diz_estar(self):
        for af in _produzir(BOLETIM):
            b = af['FACT_TIME_ROLE']['BASIS']
            if b:
                self.assertEqual(b['TRECHO'], BOLETIM[b['INICIO']:b['FIM']])

    def test_o_trecho_com_o_facto_observado_traz_a_data_da_seccao(self):
        af = _que_diz(_produzir(BOLETIM), 'Le grandinate sono state osservate')
        self.assertIsNotNone(af)
        self.assertEqual(af['FACT_TIME']['VALOR'], '2026-09-07/2026-09-13')
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.ACONTECIMENTO)
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.CABECALHO_D147)
        # D147/D153: os DOIS trechos ficam registados
        c = af['FACT_TIME_ROLE']['COMPOSICAO']
        self.assertIn('Dal 07-09-2026 al 13-09-2026', c['TRECHO_DO_CABECALHO'])
        self.assertIn('osservate', c['TRECHO_DO_ALVO'])

    def test_a_procedencia_chega_ate_ao_raw(self):
        af = _produzir(BOLETIM)[0]
        p = af['PROVENIENCIA']
        self.assertEqual(p['RAW_SHA256'], 'f' * 64)
        self.assertEqual(p['RAW_OBSERVATION_ID'], 1)
        self.assertIn('RAW_ASSET', p['CAMINHO'])


class OIdentificador(unittest.TestCase):
    """ii · deterministico, e sensivel ao byte."""

    def test_a_mesma_entrada_da_o_mesmo_id(self):
        self.assertEqual([a['ASSERTION_ID'] for a in _produzir(BOLETIM)],
                         [a['ASSERTION_ID'] for a in _produzir(BOLETIM)])

    def test_outro_raw_da_outro_id(self):
        a = _produzir(BOLETIM)[0]['ASSERTION_ID']
        b = _produzir(BOLETIM, raw_sha256='e' * 64)[0]['ASSERTION_ID']
        self.assertNotEqual(a, b)

    def test_outro_offset_da_outro_id(self):
        um = AD.assertion_id('S', 'a' * 64, 10, 20, 'x')
        outro = AD.assertion_id('S', 'a' * 64, 11, 20, 'x')
        self.assertNotEqual(um, outro)


class TestesNegativos(unittest.TestCase):
    """iii · um texto por caso. O que nao se prova NAO passa a ser opiniao."""

    def test_publicacao_nao_e_fato(self):
        """A data de publicacao sozinha nunca preenche FACT_TIME — em nenhum trecho."""
        t = ("Pubblicato il 16 settembre 2026 dal servizio fitosanitario regionale competente.\n"
             "La presenza del fungo e stata riscontrata nei campi della zona pianeggiante.\n")
        afs = _produzir(t)
        self.assertTrue(afs)
        for af in afs:
            self.assertNotEqual(af['FACT_TIME']['VALOR'], '2026-09-16')
            self.assertNotIn(TA.PUBLICACAO, TA.PAPEL_QUE_E_FACTO)

    def test_validade_nao_e_fato(self):
        """«validita dal … al …» tem papel VALIDADE, e VALIDADE nunca vira FACT_TIME."""
        papel, _ = TA.papel_do_periodo('Autorizzazione con validita dal 01-03-2026 al 28-06-2026',
                                       None, None, None)
        self.assertEqual(papel, TA.VALIDADE)
        self.assertNotIn(TA.VALIDADE, TA.PAPEL_QUE_E_FACTO)
        t = ("VALIDITA DAL 01-03-2026 AL 28-06-2026\n"
             "La deroga riguarda i trattamenti autorizzati nelle aziende agricole della provincia.\n")
        for af in _produzir(t):
            self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)

    def test_previsao_nao_e_acontecimento_observado(self):
        """O periodo que comeca depois da publicacao PROVADA e previsao, nunca facto."""
        af = _que_diz(_produzir(BOLETIM), 'Le grandinate sono previste')
        self.assertIsNotNone(af)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)
        self.assertIsNotNone(af['FACT_TIME']['PORQUE_NAO'])

    def test_ato_e_mercado_tem_papel_proprio(self):
        self.assertEqual(TA.papel_do_periodo('Decreto n. 12 del 03-02-2026 al 04-02-2026',
                                             None, None, None)[0], TA.ATO)
        self.assertEqual(TA.papel_do_periodo('Rilevazione dal 01-09-2026 al 07-09-2026',
                                             None, None, None)[0], TA.MARKET_PERIOD)
        for p in (TA.ATO, TA.MARKET_PERIOD, TA.PUBLICACAO, TA.PERIODO_DA_EDICAO, TA.PREVISAO):
            self.assertNotIn(p, TA.PAPEL_QUE_E_FACTO)

    def test_periodo_da_edicao_nao_e_fato(self):
        """«16 - 22 settembre 2026» no cabecalho do boletim diz de que dias a EDICAO fala."""
        ps = TA.periodos_do_cabecalho(BOLETIM, 0, len(BOLETIM), None,
                                      cabecalho_do_documento=TA.cabecalho_do_documento(BOLETIM))
        da_edicao = [p for p in ps if p['PAPEL'] == TA.PERIODO_DA_EDICAO]
        self.assertEqual(len(da_edicao), 1)
        self.assertEqual(da_edicao[0]['VALOR'], '2026-09-16/2026-09-22')

    def test_data_ambigua_fica_nao_sei(self):
        """D149/D153: a conta relativa diz uma coisa e o periodo impresso diz outra.

        «la settimana scorsa», com a publicacao de 16-09-2026 PROVADA, da a semana
        07-13/09. O cabecalho da seccao imprime outra semana. Duas respostas para a mesma
        afirmacao = concorrente = NAO SEI, com os dois valores escritos."""
        t = ("Bollettino n. 9\n"
             "\f"
             "SEZIONE Dal 24-08-2026 al 30-08-2026\n"
             "Le grandinate sono state osservate la settimana scorsa in provincia di Cuneo.\n")
        af = _que_diz(_produzir(t), 'Le grandinate sono state osservate')
        self.assertIsNotNone(af)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)
        self.assertIn('concorrente', af['FACT_TIME_ROLE']['PORQUE'])
        c = af['FACT_TIME_ROLE']['COMPOSICAO']
        self.assertEqual(c['CONTA_DO_VIVO'], '2026-09-07/2026-09-13')
        self.assertEqual(c['IMPRESSO'], '2026-08-24/2026-08-30')

    def test_dois_periodos_no_mesmo_cabecalho_ficam_nao_sei(self):
        """A condicao (1) da D147: um cabecalho com DOIS periodos nao governa nada."""
        t = ("Bollettino n. 10\n"
             "\f"
             "SEZIONE DAL 07-09-2026 AL 13-09-2026 E DAL 01-08-2026 AL 07-08-2026\n"
             "Le grandinate sono state osservate in provincia di Cuneo con danni ai frutteti.\n")
        af = _que_diz(_produzir(t), 'Le grandinate sono state osservate')
        self.assertIsNotNone(af)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)

    def test_local_inexistente_fica_nao_sei(self):
        """Um nome que o gazetteer nao conhece nao vira lugar do facto."""
        t = ("Bollettino n. 4\n"
             "\f"
             "SEZIONE Dal 07-09-2026 al 13-09-2026\n"
             "Le grandinate sono state osservate a Xqzzyville con danni diffusi ai frutteti locali.\n")
        af = _que_diz(_produzir(t), 'Le grandinate sono state osservate')
        self.assertIsNotNone(af)
        self.assertEqual(af['FACT_LOCATION']['VALOR'], NAO_SEI)
        self.assertFalse(af['FACT_LOCATION']['PONTO_NO_MAPA'])

    def test_trecho_inexistente_reprova(self):
        af = dict(_produzir(BOLETIM)[0])
        af['TRECHO_LITERAL'] = af['TRECHO_LITERAL'] + ' (frase que o documento nao tem)'
        v = AD.conferir_afirmacao(af, BOLETIM, raw_sha256='f' * 64)
        self.assertTrue(any('TRECHO_LITERAL' in x for x in v), v)

    def test_documento_alterado_reprova(self):
        """RAW_SHA256 diferente do registado: o byte mudou, a ancora deixou de valer."""
        af = _produzir(BOLETIM)[0]
        v = AD.conferir_afirmacao(af, BOLETIM, raw_sha256='0' * 64)
        self.assertTrue(any('documento alterado' in x for x in v), v)

    def test_o_trecho_diferente_de_texto_inicio_fim_reprova_por_isso(self):
        """A violacao tem de ser ESTA, e nao outra que passe por ela.

        Achado pela mutacao: com a comparacao desligada, a mensagem do EVIDENCE_SPAN
        continha «TRECHO_LITERAL» e o teste antigo dava-se por satisfeito."""
        af = json.loads(json.dumps(_produzir(BOLETIM)[0]))
        af['TRECHO_LITERAL'] = af['TRECHO_LITERAL'][1:]
        v = AD.conferir_afirmacao(af, BOLETIM, raw_sha256='f' * 64)
        self.assertTrue(any('nao e texto[' in x for x in v), v)

    def test_o_basis_do_tempo_fora_do_sitio_reprova(self):
        af = json.loads(json.dumps(_que_diz(_produzir(BOLETIM), 'Le grandinate sono state osservate')))
        af['FACT_TIME_ROLE']['BASIS'] = dict(af['FACT_TIME_ROLE']['BASIS'], INICIO=0, FIM=5)
        v = AD.conferir_afirmacao(af, BOLETIM, raw_sha256='f' * 64)
        self.assertTrue(any('BASIS do FACT_TIME' in x for x in v), v)

    def test_um_periodo_futuro_nunca_tem_o_papel_de_acontecimento(self):
        """A regra sozinha, sem depender da marca de futuro na frase."""
        papel, porque = TA.papel_do_periodo('SEZIONE DAL 21-09-2026 AL 27-09-2026',
                                            date(2026, 9, 21), date(2026, 9, 27), date(2026, 9, 16))
        self.assertEqual(papel, TA.PREVISAO)
        self.assertNotIn(TA.PREVISAO, TA.PAPEL_QUE_E_FACTO)

    def test_a_seccao_futura_nao_da_data_a_um_facto_sem_marca_de_futuro(self):
        """O trecho nao escreve «previsto» nenhum: quem o barra e o calendario, nao a palavra."""
        t = ("Bollettino n. 11\n"
             "\f"
             "SEZIONE DAL 21-09-2026 AL 27-09-2026\n"
             "Le grandinate sono state osservate in provincia di Cuneo con danni ai frutteti.\n")
        af = _que_diz(_produzir(t), 'Le grandinate sono state osservate')
        self.assertIsNotNone(af)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)

    def test_texto_alterado_desloca_a_ancora_e_reprova(self):
        af = _produzir(BOLETIM)[0]
        v = AD.conferir_afirmacao(af, 'XXXX' + BOLETIM, raw_sha256='f' * 64)
        self.assertTrue(v)

    def test_offset_invalido_reprova(self):
        af = dict(_produzir(BOLETIM)[0])
        af['POSICAO'] = dict(af['POSICAO'], INICIO=10 ** 9, FIM=10 ** 9 + 5)
        self.assertTrue(any('offset invalido' in x for x in AD.conferir_afirmacao(af, BOLETIM)))

    def test_dado_sem_fact_time_legitimo_sai_nao_sei_ou_nao_existe(self):
        """Um texto sem nenhuma data: NAO_EXISTE, e nunca a data da publicacao."""
        t = ("Le trappole cromotropiche sono state controllate nei campi sperimentali della zona.\n"
             "I tecnici hanno verificato lo stato delle piante durante il consueto sopralluogo.\n")
        afs = _produzir(t)
        self.assertTrue(afs)
        for af in afs:
            self.assertIn(af['FACT_TIME']['VALOR'], (NAO_SEI, TA.NAO_EXISTE))
        self.assertTrue(any(af['FACT_TIME']['VALOR'] == TA.NAO_EXISTE for af in afs))

    def test_conselho_nao_herda_a_data_da_seccao(self):
        t = ("Bollettino n. 5\n"
             "\f"
             "SEZIONE Dal 07-09-2026 al 13-09-2026\n"
             "Si consiglia di intervenire sulle piante colpite con i prodotti autorizzati in etichetta.\n")
        af = _que_diz(_produzir(t), 'Si consiglia')
        self.assertIsNotNone(af)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)


class ONDE_UMA_FRASE_ACABA(unittest.TestCase):
    """Um trecho que mistura DUAS afirmacoes e uma prova pior. Onde se corta, e onde nao."""

    def test_o_ponto_decimal_nao_acaba_a_frase(self):
        t = ("Bollettino n. 6\n"
             "\f"
             "SEZIONE Dal 07-09-2026 al 13-09-2026\n"
             "Gli accumuli osservati sono stati registrati con 46.8 mm nella zona collinare.\n")
        af = _que_diz(_produzir(t), 'Gli accumuli osservati')
        self.assertIsNotNone(af)
        self.assertTrue(af['TRECHO_LITERAL'].endswith('collinare.'), af['TRECHO_LITERAL'])

    def test_a_virgula_que_emenda_duas_frases_corta(self):
        """«… nella zona, Gli accumuli …»: o ponto que o compositor perdeu."""
        t = ("Bollettino n. 7\n"
             "\f"
             "SEZIONE Dal 07-09-2026 al 13-09-2026\n"
             "Le piogge sono cadute sabato nella zona collinare, Gli accumuli osservati "
             "sono stati registrati con 46.8 mm.\n")
        afs = _produzir(t)
        self.assertIsNotNone(_que_diz(afs, 'Le piogge sono cadute'))
        self.assertIsNotNone(_que_diz(afs, 'Gli accumuli osservati'))

    def test_o_nome_proprio_com_artigo_nao_corta(self):
        """«La Spezia» e «Le Marche» tem maiuscula depois do artigo: nao sao frase nova."""
        t = ("Bollettino n. 8\n"
             "\f"
             "SEZIONE Dal 07-09-2026 al 13-09-2026\n"
             "Le grandinate sono state osservate nelle province settentrionali, La Spezia "
             "e Le Marche comprese, con danni ai frutteti.\n")
        afs = _produzir(t)
        af = _que_diz(afs, 'Le grandinate sono state osservate')
        self.assertIsNotNone(af)
        self.assertIn('La Spezia', af['TRECHO_LITERAL'])


class AMemoriaDeLeitura(unittest.TestCase):
    """A memoria posta em `boletim_do_campo` acelera; nao pode mudar UMA resposta."""

    TEXTOS = (BOLETIM,
              "COMPRENSORIO - LE - PIANURA\nLa mosca dell'olivo e presente negli oliveti della zona.\n",
              "OLIVO\nNessuna segnalazione di mosca delle olive nelle trappole controllate.\n")

    def test_a_resposta_com_memoria_e_a_mesma_de_sem_memoria(self):
        for t in self.TEXTOS:
            self.assertEqual(BC.secoes_territoriais(t), BC.secoes_territoriais.sem_memoria(t))
            self.assertEqual(BC._titulo_do_documento(t, None),
                             BC._titulo_do_documento.sem_memoria(t, None))
            self.assertEqual(BC.sem_vizinhos(t), BC.sem_vizinhos.sem_memoria(t))

    def test_textos_diferentes_nao_partilham_a_resposta(self):
        a, b = self.TEXTOS[1], self.TEXTOS[2]
        self.assertNotEqual(BC.secoes_territoriais(a), BC.secoes_territoriais(b))
        self.assertEqual(BC.secoes_territoriais(a), BC.secoes_territoriais.sem_memoria(a))

    def test_quem_recebe_a_lista_nao_estraga_a_memoria(self):
        t = self.TEXTOS[1]
        primeira = BC.secoes_territoriais(t)
        primeira.append({'INVASOR': True})
        self.assertEqual(BC.secoes_territoriais(t), BC.secoes_territoriais.sem_memoria(t))


class OQueAindaNaoAconteceu(unittest.TestCase):
    """D160 §2.1 e §2.3 — os defeitos que o red team mediu, cada um com o seu teste.

    O caminho que falhava era o do LEITOR VIVO (uma data escrita no proprio trecho), nao o
    do cabecalho: `_primeiro_dia` so lia «AAAA-MM-DD», e «12 novembre 2026» devolvia None."""

    def test_a_data_le_se_em_qualquer_forma_que_o_vivo_escreva(self):
        for valor, esperado, sem_ano in (
                ('2026-09-07/2026-09-13', date(2026, 9, 7), False),
                ('12 novembre 2026', date(2026, 11, 12), False),
                ('6-8 ottobre 2026', date(2026, 10, 6), False),
                ('16/09/2026', date(2026, 9, 16), False),
                ('ottobre 2026', date(2026, 10, 1), False),
                ('2003', date(2003, 1, 1), False),
                ('18 febbraio', None, True)):
            self.assertEqual(TA.primeiro_dia(valor), (esperado, sem_ano), valor)

    def test_evento_futuro_com_data_por_extenso_nao_e_acontecimento(self):
        """RT3: «si terrà il 12 novembre 2026», publicado a 16/09. Era ACONTECIMENTO."""
        t = ("Il convegno regionale sulla difesa integrata si terrà il 12 novembre 2026 "
             "presso la sede della Regione.\n")
        af = _que_diz(_produzir(t), 'Il convegno regionale')
        self.assertIsNotNone(af)
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.PREVISAO)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)

    def test_a_data_depois_da_publicacao_provada_nao_e_acontecimento(self):
        papel, _ = TA._papel_do_vivo({'fact_time': '12 novembre 2026', 'fact_time_kind': 'EVENTO'},
                                     'La riunione del 12 novembre 2026 in provincia di Cuneo.',
                                     date(2026, 9, 16))
        self.assertEqual(papel, TA.PREVISAO)

    def test_a_data_depois_da_captura_nao_e_acontecimento(self):
        """Sem publicacao provada, quem recusa e a captura — a mesma regra do G0, por
        afirmacao. Isto NAO ancora nada na coleta (D63): so recusa."""
        papel, porque = TA._papel_do_vivo(
            {'fact_time': '30 settembre 2026', 'fact_time_kind': 'CAMPO'},
            'La grandine osservata il 30 settembre 2026 in provincia di Cuneo.',
            None, date(2026, 9, 25))
        self.assertEqual(papel, TA.PREVISAO)
        self.assertIn('colhido', porque)

    def test_o_futuro_do_verbo_italiano_e_futuro(self):
        for frase in ('La grandine colpirà la zona il 12 novembre 2026',
                      'Le riunioni si terranno il 12 novembre 2026',
                      'La giornata sarà organizzata il 12 novembre 2026',
                      'Incontro in programma il 12 novembre 2026'):
            self.assertTrue(TA.marca_futuro(frase, '12 novembre 2026'), frase)

    def test_a_palavra_com_acento_que_nao_e_verbo_nao_e_futuro(self):
        """«città», «libertà», «papà» acabam em -tà e -pà, nunca em -rà."""
        for frase in ('La città di Cuneo il 12 novembre 2026',
                      'La libertà di scelta il 12 novembre 2026'):
            self.assertFalse(TA.marca_futuro(frase, '12 novembre 2026'), frase)

    def test_janela_de_uso_permitido_e_validade_nao_facto(self):
        """D160 §2.2, com a forma real medida em derived:busca-3ae87b2ee6c08d80."""
        papel, _ = TA.papel_do_periodo(
            'impiego consentito a partire dal 1 aprile 2026 fino al 29 luglio 2026',
            None, None, None)
        self.assertEqual(papel, TA.VALIDADE)
        t = ("Per questo prodotto l'impiego consentito a partire dal 1 aprile 2026 fino al "
             "29 luglio 2026 nelle aziende della provincia.\n")
        for af in _produzir(t):
            self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)

    def test_as_tres_formas_de_validade_cada_uma_sozinha(self):
        """Uma frase por FORMA, escolhida para que SO aquela alternativa a apanhe — senao
        uma cobre a outra e o mutante da que falta sobrevive (foi o que aconteceu)."""
        casos = {
            # so «impiego consentito» (o «consentito» nao vem seguido de «dal»)
            'impiego': "L'impiego consentito riguarda il periodo 01-03-2026 al 28-06-2026",
            # so «autorizzato dal»
            'autorizzato': 'Prodotto autorizzato dal 01-03-2026 al 28-06-2026',
            # so «vale dal» / «decorre dal»
            'vale': 'La deroga vale dal 01-03-2026 al 28-06-2026',
            'decorre': 'Il termine decorre dal 01-03-2026 al 28-06-2026',
        }
        for nome, frase in casos.items():
            self.assertEqual(TA.papel_do_periodo(frase, None, None, None)[0], TA.VALIDADE, nome)

    def test_alerta_evento_nao_e_o_que_sobra(self):
        """RT4: a classe exige as TRES coisas, e nao so o papel."""
        semear = {'PAPEL': TA.ACONTECIMENTO, 'PRECISAO': 'DATE_EXACT', 'ANO': None}
        # sem ancora de acontecimento no texto
        r = AD.classe_do_claim('come scrissi, nel 2003, nella nota introduttiva del volume', semear)
        self.assertEqual(r['VALOR'], NAO_SEI)
        # papel que nao e ACONTECIMENTO
        r = AD.classe_do_claim('La grandine osservata ha colpito i frutteti',
                               {'PAPEL': TA.PREVISAO, 'PRECISAO': 'DATE_EXACT', 'ANO': None})
        self.assertEqual(r['VALOR'], NAO_SEI)
        # sem ano
        r = AD.classe_do_claim('La grandine osservata ha colpito i frutteti',
                               {'PAPEL': TA.ACONTECIMENTO, 'PRECISAO': 'DATE_EXACT+SEM_ANO',
                                'ANO': NAO_SEI})
        self.assertEqual(r['VALOR'], NAO_SEI)
        # as tres juntas
        r = AD.classe_do_claim('La grandine osservata ha colpito i frutteti', semear)
        self.assertEqual(r['VALOR'], 'ALERTA_EVENTO')

    def test_a_precisao_diz_quando_o_ano_falta(self):
        t = ("La grandinata osservata il 18 febbraio ha colpito i frutteti della provincia "
             "di Cuneo con danni diffusi.\n")
        af = _que_diz(_produzir(t), 'La grandinata osservata')
        self.assertIsNotNone(af)
        self.assertTrue(af['FACT_TIME_ROLE']['PRECISAO'].endswith('SEM_ANO'),
                        af['FACT_TIME_ROLE']['PRECISAO'])
        self.assertEqual(af['FACT_TIME_ROLE']['ANO'], NAO_SEI)


class AIdentidadeNaoSeRebaixa(unittest.TestCase):
    """D160 §1.6-H · contrato de consumo §3: NAO SEI na identidade RECUSA."""

    def test_o_vocabulario_de_ignorancia_e_o_do_dono(self):
        """A copia local nao pode divergir de `motor/corrida_da_inteligencia`."""
        sys.path.insert(0, os.path.join(RAIZ, 'motor'))
        import corrida_da_inteligencia as CI      # noqa: PLC0415
        self.assertEqual(AD.PALAVRAS_DE_IGNORANCIA, CI.PALAVRAS_DE_IGNORANCIA)

    def test_nao_sei_na_identidade_recusa(self):
        for campo in ('ITEM_ID', 'RAW_OBSERVATION_ID', 'RAW_SHA256', 'SOURCE_ID'):
            for como in ('NAO SEI', 'UNKNOWN', 'NOT_KNOWN', ''):
                af = json.loads(json.dumps(_produzir(BOLETIM)[0]))
                af[campo] = como
                v = AD.conferir_afirmacao(af, BOLETIM, raw_sha256='f' * 64)
                self.assertTrue(any(campo in x for x in v), (campo, como, v))

    def test_uma_linha_da_sala_sem_raw_nao_produz_afirmacao_que_passe(self):
        """A porta que estava aberta: sem `raw_sha256`, `raw_observation_id` e `source_id`,
        a afirmacao saia com NAO SEI nos tres e a conferencia devolvia []."""
        linha = _linha(BOLETIM)
        for c in ('raw_sha256', 'raw_observation_id', 'source_id'):
            linha[c] = None
        for af in AD.afirmacoes_do_item(linha)['AFIRMACOES']:
            self.assertTrue(AD.conferir_afirmacao(af, BOLETIM), af['CLAIM_ID'])


class OBlocoDeMenuNaoEUmaFrase(unittest.TestCase):
    """D160 §1.9 · 700 trechos com 3+ quebras de linha: o menu de uma pagina web engolido
    numa «frase» so, porque nenhuma daquelas linhas acaba em ponto."""

    MENU = "Home\nNotizie\nTemi ambientali\nPubblicazioni\nContatti\nArea riservata\n"

    def test_um_bloco_de_linhas_curtas_nao_e_corpo(self):
        self.assertTrue(AD.e_bloco_de_linhas_curtas(self.MENU))
        self.assertFalse(AD.e_corpo(self.MENU))

    def test_um_paragrafo_de_verdade_continua_a_ser_corpo(self):
        p = ("Le grandinate sono state osservate in provincia di Cuneo con danni diffusi\n"
             "ai frutteti e alle colture orticole della zona pianeggiante.\n")
        self.assertFalse(AD.e_bloco_de_linhas_curtas(p))
        self.assertTrue(AD.e_corpo(p))

    def test_o_menu_nao_vira_afirmacao(self):
        for af in _produzir(self.MENU + BOLETIM):
            self.assertNotIn('Area riservata', af['TRECHO_LITERAL'])


class OLugarTemOffset(unittest.TestCase):
    """D160 §2.6 · o lugar nao tinha onde, so o nome."""

    def test_o_lugar_escrito_no_trecho_traz_o_offset(self):
        af = _que_diz(_produzir(BOLETIM), 'Le grandinate sono state osservate')
        onde = af['FACT_LOCATION']['ONDE']
        self.assertIsNotNone(onde)
        self.assertEqual(onde['TRECHO'], BOLETIM[onde['INICIO']:onde['FIM']])
        self.assertTrue(onde['DENTRO_DO_ALVO'])

    def test_a_expressao_que_atravessa_uma_linha_nao_e_um_lugar(self):
        """D160 §1.5 · «zone cuscinetto» na linha de TITULO e «Il monitoraggio» na frase
        seguinte davam o lugar «zone cuscinetto Il monitoraggio». Duas metades de linhas
        diferentes nao sao o nome de um lugar."""
        t = ("Bollettino n. 15\n"
             "\f"
             "SEZIONE DAL 07-09-2026 AL 13-09-2026\n"
             "Monitoraggio nelle zone cuscinetto\n"
             "Il monitoraggio degli adulti e stato eseguito dai tecnici della provincia.\n")
        afs = [x for x in _produzir(t) if 'zone cuscinetto' in x['TRECHO_LITERAL']]
        self.assertTrue(afs, 'o texto de prova nao produziu o trecho que atravessa a linha')
        for af in afs:
            loc = af['FACT_LOCATION']
            self.assertEqual(loc['VALOR'], NAO_SEI, af['TRECHO_LITERAL'])
            self.assertFalse(loc['PONTO_NO_MAPA'])
            self.assertIn('atravessa uma quebra de linha', loc['PORQUE'] or '')

    def test_nenhum_lugar_publicado_atravessa_uma_linha(self):
        for af in _produzir(BOLETIM):
            onde = af['FACT_LOCATION']['ONDE']
            if onde:
                self.assertFalse(onde['ATRAVESSA_LINHA'], onde)

    def test_sem_offset_o_porque_esta_escrito(self):
        """«barese» -> Bari: a forma escrita nao e a normalizada, e isso diz-se."""
        for af in _produzir(BOLETIM):
            loc = af['FACT_LOCATION']
            if loc['VALOR'] != NAO_SEI and loc['ONDE'] is None:
                self.assertTrue(loc['PORQUE_SEM_OFFSET'])


class ALeituraDoCabecalhoDobrado(unittest.TestCase):
    """As letras dobradas do PDF — a regra, e o que ela recusa."""

    def test_desdobra_o_que_esta_dobrado(self):
        self.assertEqual(TA.desdobrar('SSEEZZIIOONNEE DDaall 0077--0099--22002266'),
                         'SEZIONE Dal 07-09-2026')

    def test_nao_desdobra_texto_normal(self):
        for l in ('La settimana scorsa e iniziata', 'SEZIONE Dal 07-09-2026', 'aa bb', '',
                  # todos os pedacos com comprimento PAR, e nenhum dobrado: a regra tem de
                  # olhar os PARES de caracteres, nao so o comprimento (achado pela mutacao)
                  'ANNO 2026 DATA TEST'):
            self.assertIsNone(TA.desdobrar(l), l)

    def test_o_periodo_dobrado_e_o_mesmo_periodo(self):
        dobrado = TA.periodo_escrito('SSEEZZIIOONNEE DDaall 0077--0099--22002266 aall 1133--0099--22002266')
        normal = TA.periodo_escrito('SEZIONE Dal 07-09-2026 al 13-09-2026')
        self.assertIsNotNone(dobrado)
        self.assertEqual(dobrado['VALOR'], normal['VALOR'])


class AFronteiraDaCollection(unittest.TestCase):
    """iv · a Collection nao vira Intelligence."""

    def test_o_produtor_nao_decide_nada_disso(self):
        proibidos = ('RELEVANCIA', 'OPORTUNIDADE', 'LIGACAO_ADAMA', 'RECOMENDACAO',
                     'PRIORIDADE', 'LIBERACAO', 'PRODUTO', 'SCORE')
        for af in _produzir(BOLETIM):
            for k in proibidos:
                self.assertNotIn(k, af, '%s nao e campo de uma afirmacao' % k)

    def test_o_vocabulario_vem_dos_donos_das_leis(self):
        for af in _produzir(BOLETIM):
            for e in af['ENTIDADES']:
                self.assertIn(e['ENTITY_SOURCE'], AF.ENTITY_SOURCES)
            self.assertIn(af['FACT_LOCATION']['LOCATION_SOURCE'], BC.LOCATION_SOURCES)
            self.assertIn(af['FACT_TIME_ROLE']['PAPEL'], tuple(TA.PAPEIS) + (NAO_SEI,))
            self.assertIn(af['CLAIM_KIND']['VALOR'], tuple(AD.CLAIM_KINDS) + (NAO_SEI,))

    def test_so_acontecimento_vira_fact_time(self):
        self.assertEqual(tuple(TA.PAPEL_QUE_E_FACTO), (TA.ACONTECIMENTO,))

    def test_o_leitor_temporal_esta_atras_da_interface(self):
        """O produtor nunca fala com o leitor vivo pelas costas da interface."""
        fonte = open(os.path.join(RAIZ, 'leis', 'afirmacao_do_documento.py'), encoding='utf-8').read()
        self.assertNotIn('campos_do_fato', fonte)
        self.assertIn('TA.extrair_tempo', fonte)

    def test_sem_llm_e_sem_rede(self):
        for nome in ('afirmacao_do_documento.py', 'tempo_da_afirmacao.py'):
            fonte = open(os.path.join(RAIZ, 'leis', nome), encoding='utf-8').read()
            for proibido in ('requests', 'urllib', 'httpx', 'openai', 'anthropic', 'socket',
                             'psycopg', 'sqlite3'):
                self.assertNotIn(proibido, fonte, '%s importa %s' % (nome, proibido))


def so_a_regra(caminho):
    """O ficheiro sem COMENTARIOS e sem DOCSTRINGS: o que sobra e o que corre.

    Uma string literal que NAO seja docstring fica — uma frase da R9 escrita como literal e
    exactamente o que este teste tem de apanhar."""
    import ast
    import io
    import tokenize
    fonte = io.open(caminho, encoding='utf-8').read()
    linhas_de_docstring = set()
    for no in ast.walk(ast.parse(fonte)):
        if isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            corpo = getattr(no, 'body', None)
            if corpo and isinstance(corpo[0], ast.Expr) and isinstance(corpo[0].value, ast.Constant) \
                    and isinstance(corpo[0].value.value, str):
                linhas_de_docstring.add(corpo[0].value.lineno)
    fora = []
    with io.open(caminho, encoding='utf-8') as f:
        for tok in tokenize.generate_tokens(f.readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING and tok.start[0] in linhas_de_docstring:
                continue
            fora.append(tok.string)
    return '\n'.join(fora)


class OContratoDeConsumoDaIntelligence(unittest.TestCase):
    """O que o dono da Intelligence exige para consumir uma afirmacao (D158).

    Fonte: `CONTRATO-CONSUMO-AFIRMACOES.md` (proposta do dono, fora do Git). Este ficheiro
    nao a copia: mede o que ela pede."""

    EXIGIDOS = ('CLAIM_ID', 'ITEM_ID', 'RAW_OBSERVATION_ID', 'RAW_SHA256', 'SOURCE_ID',
                'PRODUTOR_VERSAO', 'EVIDENCE_SPAN', 'CLAIM_KIND', 'SUBJECT', 'PREDICATE',
                'OBJECT', 'ENTIDADES', 'FACT_TIME', 'FACT_LOCATION', 'VALIDITY',
                'MARKET_PERIOD', 'STUDY_PERIOD', 'PUBLISHED_AT', 'OBSERVED_AT', 'COLLECTED_AT')

    def test_todos_os_campos_do_paragrafo_1_estao_presentes(self):
        for af in _produzir(BOLETIM):
            for c in self.EXIGIDOS:
                self.assertIn(c, af, c)

    def test_o_evidence_span_e_literal_e_confere(self):
        for af in _produzir(BOLETIM):
            s = af['EVIDENCE_SPAN']
            self.assertEqual(s['TRECHO'], BOLETIM[s['INICIO']:s['FIM']])
            self.assertEqual(s['TRECHO'], af['TRECHO_LITERAL'])

    def test_claim_id_e_assertion_id_sao_o_mesmo_valor(self):
        for af in _produzir(BOLETIM):
            self.assertEqual(af['CLAIM_ID'], af['ASSERTION_ID'])

    def test_o_produtor_versao_diz_que_regra_extraiu(self):
        af = _produzir(BOLETIM)[0]
        self.assertEqual(af['PRODUTOR_VERSAO']['DECISAO'], 'D158')
        self.assertTrue(af['PRODUTOR_VERSAO']['CODIGO']['leis/afirmacao_do_documento.py'])
        self.assertTrue(af['PRODUTOR_VERSAO']['SEM_LLM'])

    def test_a_classe_do_facto_observado_e_alerta_evento(self):
        af = _que_diz(_produzir(BOLETIM), 'Le grandinate sono state osservate')
        self.assertEqual(af['CLAIM_KIND']['VALOR'], 'ALERTA_EVENTO')

    def test_a_classe_com_duas_marcas_fica_nao_sei(self):
        """Marca de REGULATORIO e de PRECO no mesmo trecho: escolher uma seria inferir."""
        r = AD.classe_do_claim('Il decreto fissa il prezzo di 12,50 euro al quintale per la campagna.',
                               {'PAPEL': TA.ACONTECIMENTO})
        self.assertEqual(r['VALOR'], NAO_SEI)
        self.assertEqual(sorted(r['MARCAS']), ['PRECO', 'REGULATORIO'])

    def test_o_produtor_nunca_escreve_liberacao(self):
        for af in _produzir(BOLETIM):
            for c in AD.CAMPOS_PROIBIDOS:
                self.assertNotIn(c, af, c)

    def test_a_conferencia_recusa_quem_escreveu_liberacao(self):
        af = dict(_produzir(BOLETIM)[0])
        af['LIBERACAO'] = 'LIBERADO_PARA_CLIENTE'
        v = AD.conferir_afirmacao(af, BOLETIM, raw_sha256='f' * 64)
        self.assertTrue(any('PRODUTOR_DECIDIU_LIBERACAO' in x for x in v), v)

    def test_a_conferencia_recusa_span_com_nome_fora_do_trecho(self):
        """COL-LAW-221: ENTITY_SOURCE = SPAN exige o nome DENTRO do EVIDENCE_SPAN."""
        af = json.loads(json.dumps(_produzir(BOLETIM)[0]))
        af['ENTIDADES'] = [{'TIPO': 'CULTURA', 'NOME_ORIGINAL': 'olivo',
                            'VALOR_NORMALIZADO': 'olivo', 'ENTITY_SOURCE': 'SPAN'}]
        v = AD.conferir_afirmacao(af, BOLETIM, raw_sha256='f' * 64)
        self.assertTrue(any('COL-LAW-221' in x for x in v), v)

    def test_a_conferencia_recusa_fact_time_igual_a_publicacao_sem_base(self):
        af = json.loads(json.dumps(_que_diz(_produzir(BOLETIM), 'Le grandinate sono state osservate')))
        af['FACT_TIME']['VALOR'] = PUB[0]
        af['FACT_TIME_ROLE']['ORIGEM'] = None
        af['FACT_TIME_ROLE']['BASIS'] = None
        v = AD.conferir_afirmacao(af, BOLETIM, raw_sha256='f' * 64)
        self.assertTrue(any('PUBLISHED_AT' in x for x in v), v)

    def test_a_conferencia_recusa_claim_sem_identidade(self):
        for campo in ('ITEM_ID', 'RAW_SHA256', 'SOURCE_ID', 'RAW_OBSERVATION_ID'):
            af = json.loads(json.dumps(_produzir(BOLETIM)[0]))
            af[campo] = ''
            v = AD.conferir_afirmacao(af, BOLETIM, raw_sha256='f' * 64)
            self.assertTrue(any(campo in x for x in v), (campo, v))

    # ── C1 · as quatro origens sao distinguiveis, e LITERAL promete o que cumpre ──
    def test_as_quatro_origens_sao_distintas(self):
        self.assertEqual(TA.ORIGENS, (TA.LITERAL, TA.CABECALHO_D147,
                                      TA.RELATIVA_ANCORADA_D149, TA.RELATIVO_D63))
        self.assertEqual(len(set(TA.ORIGENS)), 4)
        self.assertNotIn(TA.LITERAL, TA.ORIGENS_COM_BASIS_FORA_DO_TRECHO)

    def test_literal_exige_o_basis_dentro_do_trecho(self):
        """Toda afirmacao com ORIGEM = LITERAL tem a prova entre INICIO e FIM."""
        for af in _produzir(BOLETIM):
            if af['FACT_TIME_ROLE']['ORIGEM'] == TA.LITERAL:
                b, p = af['FACT_TIME_ROLE']['BASIS'], af['POSICAO']
                self.assertTrue(p['INICIO'] <= b['INICIO'] and b['FIM'] <= p['FIM'],
                                (b, p))

    def test_a_conferencia_recusa_literal_com_o_basis_no_cabecalho(self):
        af = json.loads(json.dumps(_que_diz(_produzir(BOLETIM), 'Le grandinate sono state osservate')))
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.CABECALHO_D147)
        af['FACT_TIME_ROLE']['ORIGEM'] = TA.LITERAL          # mentir sobre onde esta a prova
        v = AD.conferir_afirmacao(af, BOLETIM, raw_sha256='f' * 64)
        self.assertTrue(any('LITERAL promete a prova dentro do trecho' in x for x in v), v)

    def test_a_relativa_ancorada_no_impresso_diz_o_proprio_nome(self):
        """D149: o valor vem do cabecalho impresso, e por isso NAO se chama LITERAL."""
        t = ("Bollettino n. 12\n"
             "\f"
             "SEZIONE DAL 07-09-2026 AL 13-09-2026\n"
             "Le grandinate sono state osservate la settimana scorsa in provincia di Cuneo.\n")
        af = _que_diz(_produzir(t), 'Le grandinate sono state osservate')
        self.assertIsNotNone(af)
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.RELATIVA_ANCORADA_D149)
        b, p = af['FACT_TIME_ROLE']['BASIS'], af['POSICAO']
        self.assertFalse(p['INICIO'] <= b['INICIO'] and b['FIM'] <= p['FIM'])

    # ── C2 · o lugar viaja com a precisao e com o limite de quem o leu ───────
    def test_o_lugar_viaja_com_a_precisao_e_com_a_cobertura(self):
        for af in _produzir(BOLETIM):
            loc = af['FACT_LOCATION']
            self.assertTrue(loc['PRECISAO'])
            self.assertIn('MUNICIPALITIES', loc['COBERTURA_DO_GAZETTEER'])

    def test_o_gazetteer_declara_que_nao_tem_municipios(self):
        """O limite e do dono do gazetteer, e viaja com o lugar em vez de ficar escondido."""
        c = AD.cobertura_do_gazetteer()
        self.assertEqual(c['MUNICIPALITIES'], 0)
        self.assertIn('ISTAT', c['MUNICIPALITIES_SOURCE'])

    def test_nenhum_municipio_e_inventado(self):
        """Um nome de comune que o gazetteer nao tem nao vira lugar, e nao vira precisao."""
        t = ("Bollettino n. 13\n"
             "\f"
             "SEZIONE DAL 07-09-2026 AL 13-09-2026\n"
             "Le grandinate sono state osservate a Xqzzyville con danni diffusi ai frutteti.\n")
        af = _que_diz(_produzir(t), 'Le grandinate sono state osservate')
        self.assertEqual(af['FACT_LOCATION']['VALOR'], NAO_SEI)
        self.assertEqual(af['FACT_LOCATION']['PRECISAO'], 'NOT_KNOWN')

    # ── C3 · nada do produtor escreve ESPECIE ────────────────────────────────
    def test_o_produtor_nunca_escreve_especie(self):
        self.assertIn('ESPECIE', AD.CAMPOS_PROIBIDOS)
        for af in _produzir(BOLETIM):
            self.assertNotIn('ESPECIE', json.dumps(af, ensure_ascii=False))

    def test_a_classe_marcada_sai_no_vocabulario_fechado(self):
        """Pela producao inteira, nao so pela funcao: um conselho sai RECOMENDACAO."""
        t = ("Bollettino n. 14\n"
             "\f"
             "SEZIONE DAL 07-09-2026 AL 13-09-2026\n"
             "Si consiglia di intervenire sulle piante colpite con i prodotti autorizzati.\n")
        af = _que_diz(_produzir(t), 'Si consiglia')
        self.assertIsNotNone(af)
        self.assertEqual(af['CLAIM_KIND']['VALOR'], 'RECOMENDACAO')
        self.assertIn(af['CLAIM_KIND']['VALOR'], AD.CLAIM_KINDS)

    def test_a_publicacao_viaja_ao_lado_e_nunca_no_lugar(self):
        for af in _produzir(BOLETIM):
            self.assertEqual(af['PUBLISHED_AT']['VALOR'], PUB[0])
            self.assertNotEqual(af['FACT_TIME']['VALOR'], PUB[0])


class NadaDaR9NoCodigo(unittest.TestCase):
    """v · o codigo de producao NAO pode SABER quais sao os 2 objetos da R9.

    «Saber» tem um sentido mecanico: nenhuma REGRA pode depender de um ID, de um trecho ou
    de uma data da R9. Por isso o teste mede o ficheiro sem os comentarios e sem as
    docstrings — o que sobra e o que corre. Uma marca da R9 dentro de uma string literal
    reprova, porque uma string literal e codigo."""

    #: IDs, trechos e datas da corrida R9.
    MARCAS_DA_R9 = ('derived:11', 'derived:911', 'SG-a5d48c8cb6f73f24', 'TRECHO_DA_AFIRMACAO',
                    '07-09-2026', '13-09-2026', 'Dal 07', 'SITUAZIONE PRECEDENTE',
                    'SSIITTUUAAZZIIOONNEE', 'scarto climatico', 'Gli accumuli settimanali',
                    'Nociglia', 'Otranto', 'IT-T3-008', 'ARIF:SETTIMANALE', 'montar_r9',
                    '85cb86ebd6582997', 'PARA-O-CASCO', 'EXPD78')
    #: o que a D158 escreveu: aqui nem em comentario a R9 pode aparecer
    ESCRITO_NA_D158 = ('leis/afirmacao_do_documento.py', 'leis/tempo_da_afirmacao.py',
                       'admissao/produtor_de_afirmacoes.py')
    #: o que ja existia e o produtor reusa: a regra nao pode conhecer a R9; a prosa das
    #: notas de medicao anteriores fica, e e MEDIDA em `test_o_que_ja_existia_so_a_cita_em_prosa`
    JA_EXISTIA = ('leis/boletim_do_campo.py', 'leis/fato_do_texto.py', 'leis/fato_local.py',
                  'leis/afirmacao_da_fonte.py')

    def _caminho(self, rel):
        return os.path.join(RAIZ, *rel.split('/'))

    def test_nenhuma_regra_de_producao_conhece_a_r9(self):
        achados = []
        for rel in self.ESCRITO_NA_D158 + self.JA_EXISTIA:
            regra = so_a_regra(self._caminho(rel))
            achados += ['%s: %s' % (rel, m) for m in self.MARCAS_DA_R9 if m in regra]
        self.assertEqual(achados, [], 'a R9 entrou numa regra: %s' % achados)

    def test_o_medidor_do_grep_nao_e_cego(self):
        """A propria medicao tem de apanhar uma marca escondida numa string literal."""
        import tempfile
        fonte = ('"""docstring com derived:11, que e prosa."""\n'
                 '# comentario com derived:11, que e prosa\n'
                 'ALVO = "derived:11"\n')
        d = tempfile.mkdtemp()
        p = os.path.join(d, 'falso.py')
        open(p, 'w', encoding='utf-8').write(fonte)
        regra = so_a_regra(p)
        self.assertEqual(regra.count('derived:11'), 1, regra)

    def test_o_que_a_d158_escreveu_nao_cita_a_r9_nem_em_comentario(self):
        achados = []
        for rel in self.ESCRITO_NA_D158:
            fonte = open(self._caminho(rel), encoding='utf-8').read()
            achados += ['%s: %s' % (rel, m) for m in self.MARCAS_DA_R9 if m in fonte]
        self.assertEqual(achados, [], 'a R9 entrou no que a D158 escreveu: %s' % achados)

    def test_o_que_ja_existia_so_a_cita_em_prosa(self):
        """As mencoes que ja existiam antes da D158 estao em prosa, e sao estas — medidas,
        nao escondidas. Se alguma passar para o codigo, o teste de cima reprova."""
        medido = {}
        for rel in self.JA_EXISTIA:
            fonte = open(self._caminho(rel), encoding='utf-8').read()
            achadas = [m for m in self.MARCAS_DA_R9 if m in fonte]
            if achadas:
                medido[rel] = achadas
        self.assertEqual(medido, {'leis/boletim_do_campo.py': ['IT-T3-008'],
                                  'leis/fato_do_texto.py': ['scarto climatico', 'IT-T3-008'],
                                  'leis/fato_local.py': ['IT-T3-008']},
                         'a lista das mencoes em prosa mudou: %s' % medido)


class DoisFactosNumaFraseSo(unittest.TestCase):
    """BLK-1 · o bloqueador do Intelligence owner (REVISAO-...-G0-AFIRMACAO §3).

    A frase que ele encontrou nas RECUSADAS, e nao nas que passaram:

        «rilevata in Europa per la prima volta nel 2004 e in Italia nel 2012, in Emilia Romagna»

    O produtor devolvia FACT_TIME = 2004 e FACT_LOCATION = Italia. O texto diz o contrario:
    2004 e a Europa; a Italia e 2012. Um par montado de dois factos diferentes e um facto
    FALSO — e so nao chegou ao pote porque faltava DOCUMENT_ID. No dia em que a linha de
    busca gravar DOCUMENT_ID, entrava."""

    BLOQUEADOR = ('La cimice asiatica e stata rilevata in Europa per la prima volta nel 2004 '
                  'e in Italia nel 2012, in Emilia Romagna.')

    def _a(self, texto, **extra):
        afs = _produzir(texto, **extra)
        self.assertEqual(len(afs), 1, 'o texto deste teste e UMA afirmacao: %d' % len(afs))
        return afs[0]

    def test_o_bloqueador_nao_devolve_mais_o_par_falso(self):
        af = self._a(self.BLOQUEADOR)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)
        self.assertEqual(af['FACT_LOCATION']['VALOR'], NAO_SEI)
        self.assertNotEqual(af['FACT_TIME']['VALOR'], '2004')
        self.assertNotEqual(af['FACT_LOCATION']['VALOR'], 'Italia')

    def test_as_duas_contagens_viajam_na_afirmacao(self):
        """§5-C: a Intelligence defende-se SEM LER TEXTO, e para isso precisa dos numeros."""
        af = self._a(self.BLOQUEADOR)
        self.assertEqual(af['TEMPOS_NO_TRECHO'], 2)
        self.assertEqual(af['LUGARES_NO_TRECHO'], 3)

    def test_os_dois_campos_estao_em_TODAS_as_afirmacoes(self):
        """O dono recusa tambem quando o campo FALTA (PRODUTOR_SEM_CONTAGEM_DE_CONCORRENTES).
        Um campo que aparece «quando ha problema» obriga quem consome a adivinhar a ausencia."""
        for texto in (self.BLOQUEADOR, BOLETIM,
                      'La cimice ha colpito i frutteti in provincia di Cuneo nel 2012.',
                      'Il prodotto non e ancora disponibile.'):
            for af in _produzir(texto):
                self.assertIn('TEMPOS_NO_TRECHO', af, af['TRECHO_LITERAL'][:60])
                self.assertIn('LUGARES_NO_TRECHO', af, af['TRECHO_LITERAL'][:60])
                self.assertIsInstance(af['TEMPOS_NO_TRECHO'], int)
                self.assertIsInstance(af['LUGARES_NO_TRECHO'], int)

    def test_o_motivo_esta_escrito_nos_dois_lados(self):
        af = self._a(self.BLOQUEADOR)
        self.assertIn('§5-C', af['FACT_TIME']['PORQUE_NAO'])
        self.assertEqual(af['FACT_LOCATION']['MOTIVO'], AD.LUGARES_CONCORRENTES)
        self.assertIn('Europa', af['FACT_LOCATION']['PORQUE'])

    def test_um_tempo_e_um_lugar_continuam_a_passar(self):
        """A regra aperta o que e ambiguo; nao pode apagar o que e claro."""
        af = self._a('La cimice ha colpito i frutteti in provincia di Cuneo nel 2012.')
        self.assertEqual(af['TEMPOS_NO_TRECHO'], 1)
        self.assertEqual(af['LUGARES_NO_TRECHO'], 1)
        self.assertEqual(af['FACT_TIME']['VALOR'], '2012')
        self.assertEqual(af['FACT_LOCATION']['VALOR'], 'Cuneo')

    def test_o_INTERVALO_de_datas_e_UM_tempo_e_nao_dois(self):
        """«dal X fino al Y» tem duas pontas DE PROPOSITO. Contar duas mataria a janela de
        validade que o red team D160 §2.2 acabou de fazer nascer."""
        self.assertEqual(TA.tempos_no_trecho(
            'Impiego consentito dal 1 gennaio 2020 fino al 31 dicembre 2025.'), 1)
        self.assertEqual(TA.tempos_no_trecho('Rilevazione della settimana 12/02/2020 - 18/02/2020.'), 1)

    def test_a_mesma_data_escrita_duas_vezes_e_UMA_data(self):
        self.assertEqual(TA.tempos_no_trecho('Nel 2012 e ancora nel 2012 la stessa cosa.'), 1)

    def test_o_mesmo_lugar_nomeado_duas_vezes_e_UM_lugar(self):
        self.assertEqual(AD.lugares_no_trecho('In Emilia-Romagna, e sempre in Emilia-Romagna.'), 1)

    def test_HIFEN_E_ESPACO_SAO_O_MESMO_LUGAR(self):
        """O gazetteer escreve «Emilia-Romagna» e o jornal escreve «Emilia Romagna». Sem esta
        tolerancia o bloqueador contava 2 lugares em vez de 3 — e um concorrente que nao se
        conta e uma guarda que nao dispara."""
        self.assertEqual(AD.lugares_no_trecho('in Emilia Romagna'), 1)
        self.assertEqual(AD.lugares_no_trecho('in Emilia-Romagna'), 1)

    def test_A_AREA_SUPRANACIONAL_CONTA_MAS_NUNCA_RESOLVE(self):
        """A assimetria que torna a lista segura: «Europa» pode fazer o lugar sair NAO SEI,
        e NUNCA pode virar um FACT_LOCATION."""
        self.assertEqual(AD.lugares_no_trecho('rilevata in Europa nel 2004'), 1)
        for af in _produzir('Il fungo e stato rilevato in Europa nel 2004.'):
            self.assertNotEqual(af['FACT_LOCATION']['VALOR'], 'Europa')

    def test_o_limite_da_contagem_de_lugares_esta_declarado(self):
        """Ele CONTA DE MENOS quando o gazetteer nao tem o nome, e isso fica escrito na
        propria afirmacao em vez de ser uma surpresa para quem consome."""
        af = self._a(self.BLOQUEADOR)
        self.assertIn('MUNICIPALITIES = 0', af['FACT_LOCATION']['LIMITE_DA_CONTAGEM'])


class AOrigemDaDataEscrita(unittest.TestCase):
    """PROD-1 · «uma data escrita por extenso dentro do trecho e LITERAL, mesmo que venha
    acompanhada de "oggi" ou "ieri"» (contrato §5-C, «Origem»).

    RELATIVO_D63 promete a quem consome que o valor foi CALCULADO a partir da publicacao.
    Prometia isso sobre uma data que estava ali, escrita, para ser lida.

    ⚠️ A CAPTURA TEM DE VIR DEPOIS DO FACTO, e a primeira versao destes testes esqueceu-o: o
    `_linha` colhe a 2026-09-20 e eu datei o facto em novembro, logo a D63 recusava-o por ser
    posterior a colheita — e recusava bem. O teste media a regra errada."""

    COLHIDO = '2026-11-20 11:07:15+00'

    def test_a_data_escrita_com_oggi_ao_lado_e_LITERAL(self):
        afs = _produzir('Oggi, 12 novembre 2026, si e svolta la giornata tecnica in Emilia-Romagna.',
                        published_at='2026-11-12', raw_captured_at=self.COLHIDO)
        af = afs[0]
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.LITERAL)
        self.assertNotEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.RELATIVO_D63)
        self.assertEqual(af['FACT_TIME']['VALOR'], '2026-11-12')

    def test_a_relativa_PURA_continua_RELATIVO_D63(self):
        """O conserto nao pode engolir a origem que existe para ser dita: sem data escrita,
        a conta a partir da publicacao continua a chamar-se pelo nome dela."""
        afs = _produzir('La settimana scorsa la cimice ha colpito i frutteti.',
                        published_at='2026-11-12', raw_captured_at=self.COLHIDO)
        self.assertEqual(afs[0]['FACT_TIME_ROLE']['ORIGEM'], TA.RELATIVO_D63)

    def test_LITERAL_continua_a_ter_o_BASIS_DENTRO_do_trecho(self):
        """A condicao C1 do dono: LITERAL promete BASIS dentro do trecho. Mudar a origem sem
        mudar a promessa seria trocar um rotulo errado por outro."""
        afs = _produzir('Oggi, 12 novembre 2026, si e svolta la giornata tecnica.',
                        published_at='2026-11-12', raw_captured_at=self.COLHIDO)
        af = afs[0]
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.LITERAL)
        basis = af['FACT_TIME_ROLE']['BASIS']
        self.assertIsNotNone(basis)
        self.assertLessEqual(af['POSICAO']['INICIO'], basis['INICIO'])
        self.assertLessEqual(basis['FIM'], af['POSICAO']['FIM'])

    def test_compara_se_pelo_DIA_e_nao_pelo_texto(self):
        """«12 novembre 2026» e «2026-11-12» sao a mesma data e nenhuma string contem a
        outra. Comparar texto com texto nunca acertaria neste caso."""
        escritos = TA.expressoes_de_tempo('Oggi, 12 novembre 2026, la giornata')
        self.assertEqual(TA._escreve_este_dia(escritos, '2026-11-12'), '12 novembre 2026')
        self.assertIsNone(TA._escreve_este_dia(escritos, '2020-01-01'))


class ALojaEMercadoEmTodaACasa(unittest.TestCase):
    """PROD-2 · «uma leitura ja estabelecida na casa prevalece sobre a omissao»
    (contrato §5-C, «Classe»). Medido pelo dono em derived:911 (myfruit).

    O `_RE_LOJA` do leitor vivo ja decidia MERCADO no lugar do fato desde o ensaio
    IT-T10-018. A classe do claim lia a mesma frase e dizia ALERTA_EVENTO. Duas partes da
    casa a discordar sobre a mesma frase e o defeito."""

    def test_a_visita_a_pontos_de_venda_nao_e_ALERTA_EVENTO(self):
        afs = _produzir('La visita ai punti vendita di Firenze si e svolta il 12 novembre 2026.',
                        published_at='2026-11-20')
        af = afs[0]
        self.assertEqual(af['CLAIM_KIND']['VALOR'], 'PRECO')
        self.assertNotEqual(af['CLAIM_KIND']['VALOR'], 'ALERTA_EVENTO')

    def test_as_outras_palavras_de_loja_dizem_o_mesmo(self):
        for palavra in ('punti di vendita', 'grande distribuzione', 'supermercati', 'ipermercati'):
            classe = AD.classe_do_claim('Rilevazione nei %s della citta.' % palavra,
                                        {'PAPEL': TA.ACONTECIMENTO, 'PRECISAO': 'DAY'})
            self.assertEqual(classe['VALOR'], 'PRECO', palavra)

    def test_a_marca_vem_do_leitor_vivo_e_nao_de_uma_segunda_lista(self):
        """Se alguem REDEFINIR a lista de palavras de loja dentro do produtor, as duas
        divergem no primeiro dia em que uma delas mudar.

        Mede-se o CODIGO, nao a prosa: um comentario que cite «supermercati» para explicar
        de onde vem a marca e documentacao, e a primeira versao deste teste reprovava por
        causa do proprio comentario que escrevi acima. O que nao pode existir e um segundo
        `re.compile` com o mesmo vocabulario."""
        caminho = os.path.join(RAIZ, 'leis', 'afirmacao_do_documento.py')
        # a chamada e CODIGO e le-se no ficheiro como esta escrita
        self.assertIn('FT._RE_LOJA.search(span)', open(caminho, encoding='utf-8').read())
        # o vocabulario e que nao pode ser redefinido — e ai a prosa nao conta
        regra = so_a_regra(caminho)
        self.assertNotIn('_RE_LOJA\n=', regra, 'o produtor redefiniu a marca de loja')
        for palavra in ('punt[oi]', 'distribuzione', 'supermercat', 'ipermercat'):
            self.assertNotIn(palavra, regra,
                             'o vocabulario de loja foi copiado para o produtor: %s' % palavra)

    def test_ALERTA_EVENTO_continua_a_nao_ser_o_que_sobra(self):
        """O conserto do red team D160 §2.3 nao pode ser desfeito por este."""
        classe = AD.classe_do_claim('Il monitoraggio prosegue regolarmente.',
                                    {'PAPEL': 'NAO SEI', 'PRECISAO': 'NOT_KNOWN'})
        self.assertEqual(classe['VALOR'], NAO_SEI)


class OMesSozinhoNaoTemAno(unittest.TestCase):
    """PROD-3 · a classe contra a regra do PROPRIO produtor (MEDICAO-CONJUNTA-BLK1 §PROD-3).

    «il suo ciclo iniziava con la semina nel mese di marzo» (derived:21) saia com
    CLAIM_KIND = ALERTA_EVENTO e sem ano — e a regra escrita no proprio `classe_do_claim` diz
    «sem ano, NAO SEI». A regra estava certa; o SINAL que ela lia e que era cego.

    O `sem_ano` do `primeiro_dia` so acende no caso «dia + mes sem ano». Um mes SOZINHO nao
    casa nenhuma das duas expressoes, logo devolvia False — e False era lido como «tem ano»."""

    TRECHO = 'Nel ferrarese il suo ciclo iniziava con la semina nel mese di marzo.'

    def test_o_mes_sozinho_nao_da_ALERTA_EVENTO(self):
        af = _produzir(self.TRECHO)[0]
        self.assertEqual(af['CLAIM_KIND']['VALOR'], NAO_SEI)
        self.assertNotEqual(af['CLAIM_KIND']['VALOR'], 'ALERTA_EVENTO')

    def test_falta_o_ano_responde_pelo_VALOR(self):
        """A pergunta passa a ser feita ao valor, com a mesma expressao que o le."""
        for valor in ('marzo', 'nel mese di marzo', '12 marzo'):
            self.assertTrue(TA.falta_o_ano(valor), valor)
        for valor in ('2012', 'marzo 2012', '12 marzo 2012', '2026-09-07/2026-09-13'):
            self.assertFalse(TA.falta_o_ano(valor), valor)

    def test_um_texto_sem_tempo_nenhum_nao_diz_que_falta_o_ano(self):
        """`falta_o_ano` nao pode virar «true por omissao»: sem mes e sem algarismo, nao ha
        ano a faltar — ha ausencia de data, que e outra coisa e tem outro nome."""
        for valor in ('', None, 'NAO SEI', 'in Toscana'):
            self.assertFalse(TA.falta_o_ano(valor), repr(valor))

    def test_A_CONTAGEM_NAO_PODE_SER_ZERO_COM_UM_LUGAR_PRESENTE(self):
        """O estado incoerente que o dono apanhou: LUGARES_NO_TRECHO = 0 e FACT_LOCATION =
        Ferrara, lido de «ferrarese». Quem consome nao tem como saber qual dos dois acreditar."""
        af = _produzir(self.TRECHO)[0]
        self.assertEqual(af['FACT_LOCATION']['VALOR'], 'Ferrara')
        self.assertGreaterEqual(af['LUGARES_NO_TRECHO'], 1)
        self.assertIn('Ferrara', [str(x) for x in af['FACT_LOCATION']['EXPRESSOES_DE_LUGAR']])

    def test_a_coerencia_vale_em_TODA_a_producao(self):
        """A regra em geral, e nao so neste trecho: valor presente => contagem >= 1. Zero com
        valor e o estado que nao pode existir em nenhuma afirmacao."""
        for texto in (self.TRECHO, BOLETIM,
                      'La cimice ha colpito i frutteti in provincia di Cuneo nel 2012.',
                      'Nel barese la raccolta e finita.',
                      'La cimice asiatica e stata rilevata in Europa nel 2004 e in Italia nel 2012.'):
            for af in _produzir(texto):
                if af['FACT_LOCATION']['VALOR'] != NAO_SEI:
                    self.assertGreaterEqual(af['LUGARES_NO_TRECHO'], 1,
                                            '%s -> %s' % (af['TRECHO_LITERAL'][:50],
                                                          af['FACT_LOCATION']['VALOR']))

    def test_somar_o_emitido_nao_afrouxa_a_guarda_dos_concorrentes(self):
        """Somar o lugar emitido so pode SUBIR a contagem. O bloqueador continua a 3."""
        af = _produzir('La cimice asiatica e stata rilevata in Europa per la prima volta nel '
                       '2004 e in Italia nel 2012, in Emilia Romagna.')[0]
        self.assertEqual(af['LUGARES_NO_TRECHO'], 3)
        self.assertEqual(af['FACT_LOCATION']['VALOR'], NAO_SEI)


class OAtoCitadoPeloNumero(unittest.TestCase):
    """PROD-4 · um ATO classificado como acontecimento (MEDICAO-CONJUNTA-BLK1 §PROD-4).

    «8810 del 24 aprile 2026, recante il Piano di azione … lotta obbligatoria … in Toscana»
    e um ato e saia ALERTA_EVENTO. As palavras `decreto|determina|delibera` ja estavam na
    marca — e NENHUMA esta naquele trecho. O que esta ali e a forma como um ato se CITA.

    O dono exige isto fechado ANTES de a linha de busca passar a gravar DOCUMENT_ID: sem
    isso, um ato entra no pote classificado como alerta de evento."""

    TRECHO = ('8810 del 24 aprile 2026, recante il Piano di azione per la lotta obbligatoria '
              'in Toscana.')

    def test_o_ato_citado_pelo_numero_e_REGULATORIO(self):
        af = _produzir(self.TRECHO, published_at='2026-05-10')[0]
        self.assertEqual(af['CLAIM_KIND']['VALOR'], 'REGULATORIO')
        self.assertNotEqual(af['CLAIM_KIND']['VALOR'], 'ALERTA_EVENTO')

    def test_cada_forma_de_citacao_sozinha(self):
        """Uma frase por FORMA nova, para que a morte de um mutante nao seja coberta por
        outra alternativa a apanhar o mesmo texto — foi o que aconteceu na validade (D160)."""
        casos = {'recante': 'Il provvedimento recante il Piano regionale.',
                 'n_del': 'Il n. 8810 del 24 aprile 2026 entra in vigore.',
                 'lotta_obbligatoria': 'La lotta obbligatoria e stata disposta.'}
        for nome, frase in casos.items():
            self.assertTrue(TA._MARCA_DE_ATO.search(frase), nome)

    def test_as_palavras_que_ja_existiam_continuam(self):
        for palavra in ('decreto', 'determinazione', 'ordinanza', 'deliberazione'):
            self.assertTrue(TA._MARCA_DE_ATO.search('Il %s regionale.' % palavra), palavra)

    def test_a_marca_nova_nao_apanha_prosa_comum(self):
        """`n. <numero> del` tem de exigir o numero: «del campo», «nel mese del raccolto» e
        prosa, e uma marca que as apanhasse punha REGULATORIO em meia Sala."""
        for frase in ('Il ciclo del campo inizia a marzo.',
                      'Nel mese del raccolto la resa e maggiore.',
                      'La cimice ha colpito i frutteti.',
                      'Il numero delle trappole e aumentato.'):
            self.assertIsNone(TA._MARCA_DE_ATO.search(frase), frase)


if __name__ == '__main__':
    unittest.main(verbosity=2)
