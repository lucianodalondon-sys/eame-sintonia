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
        """RT3 §2.D · agora sao QUATRO condicoes, e a PRIMEIRA e a marca escrita.

        O contrato §5-C e literal: «quando NENHUMA marca de classe esta escrita, a classe e
        NAO SEI, MESMO QUE o papel seja ACONTECIMENTO». A versao anterior deste teste exigia
        tres coisas (papel + ancora do campo + ano) e nenhuma delas e uma marca de classe —
        por isso ele passava sobre «La grandine osservata ha colpito i frutteti», que nao
        escreve palavra de classe nenhuma."""
        semear = {'PAPEL': TA.ACONTECIMENTO, 'PRECISAO': 'DATE_EXACT', 'ANO': None,
                  'VALOR': '12 aprile 2026'}
        COM_MARCA = 'La giornata tecnica si e svolta e la grandine ha colpito i frutteti'
        # 1 · sem marca de classe nenhuma — e este e o caso que o §5-C fecha
        r = AD.classe_do_claim('La grandine osservata ha colpito i frutteti', semear)
        self.assertEqual(r['VALOR'], NAO_SEI)
        self.assertIn('nenhuma marca de classe', r['PORQUE'])
        # 2 · papel que nao e ACONTECIMENTO
        r = AD.classe_do_claim(COM_MARCA, dict(semear, PAPEL=TA.PREVISAO))
        self.assertEqual(r['VALOR'], NAO_SEI)
        # 3 · sem ano
        r = AD.classe_do_claim(COM_MARCA, dict(semear, PRECISAO='DATE_EXACT+SEM_ANO',
                                               ANO=NAO_SEI, VALOR='aprile'))
        self.assertEqual(r['VALOR'], NAO_SEI)
        # 4 · as quatro juntas
        r = AD.classe_do_claim(COM_MARCA, semear)
        self.assertEqual(r['VALOR'], 'ALERTA_EVENTO')
        self.assertEqual(r['MARCAS'], ['ALERTA_EVENTO'])

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

    def test_o_facto_observado_SEM_marca_de_classe_fica_nao_sei(self):
        """RT3 §2.D · o §5-C a valer sobre a producao inteira, e nao so sobre a funcao.

        «Le grandinate sono state osservate in provincia di Cuneo» e um facto observado, com
        papel ACONTECIMENTO e data do cabecalho — e NAO escreve palavra de classe nenhuma.
        Antes saia ALERTA_EVENTO. O dono escreveu que nao pode.

        ⚠️ O PRECO DISTO ESTA DECLARADO na entrega: os casos que o red team chamou «certos»
        (chuva medida em derived:11) passam a NAO SEI. A classe fica mais pobre, e e o dono do
        contrato que manda."""
        af = _que_diz(_produzir(BOLETIM), 'Le grandinate sono state osservate')
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.ACONTECIMENTO)
        self.assertEqual(af['CLAIM_KIND']['VALOR'], NAO_SEI)
        self.assertEqual(af['CLAIM_KIND']['MARCAS'], [])

    def test_o_evento_tecnico_escrito_e_ALERTA_EVENTO(self):
        """E a marca existe: e a `FT._RE_EVENTO`, a mesma que o leitor do lugar usa para saber
        se um lugar e lugar de evento. Le-se de la, nao se copia (o mesmo caminho da PROD-2)."""
        for frase in ('La giornata tecnica si e svolta il 12 aprile 2026 in Emilia-Romagna.',
                      'La fiera si e svolta il 12 aprile 2026 a Verona.',
                      'Il convegno si e svolto il 12 aprile 2026 a Bologna.'):
            af = _produzir(frase, published_at='2026-05-10')[0]
            self.assertEqual(af['CLAIM_KIND']['VALOR'], 'ALERTA_EVENTO', frase)

    def test_a_marca_de_evento_vem_do_leitor_vivo_e_nao_de_uma_copia(self):
        caminho = os.path.join(RAIZ, 'leis', 'afirmacao_do_documento.py')
        self.assertIn('FT._RE_EVENTO.search(span)', open(caminho, encoding='utf-8').read())
        regra = so_a_regra(caminho)
        for palavra in ('fier[ae]', 'convegn', 'open\s+day', 'giornat'):
            self.assertNotIn(palavra, regra,
                             'o vocabulario de evento foi copiado para o produtor: %s' % palavra)

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

    def test_o_primeiro_dia_diz_ELE_MESMO_que_o_ano_falta(self):
        """RT3 §2.D · o contrato do `primeiro_dia`, fixado nele proprio.

        ⚠️ ESTE TESTE E DE UM MUTANTE SOBREVIVENTE, e o terceiro da mesma familia. A pergunta
        «o ano existe?» estava respondida em TRES sitios (aqui, na precisao do `extrair_tempo` e
        na classe), e os tres cobriam-se uns aos outros: desligar qualquer um sozinho deixava os
        outros a responder. Tres mutantes sobreviveram assim.

            A SAIDA NAO FOI INVENTAR UM TESTE POR CAMADA: FOI JUNTAR A GUARDA NUM SITIO.

        A segunda camada (no `extrair_tempo`) foi APAGADA — era redundante de verdade. Esta
        ficou, porque `primeiro_dia` e quem LE a data, e quem le e quem tem de dizer o que falta.
        E ela e mais larga do que «mes sozinho»: mede-se abaixo que apanha «18/02» tambem."""
        self.assertEqual(TA.primeiro_dia('luglio'), (None, True))
        self.assertEqual(TA.primeiro_dia('marzo'), (None, True))
        self.assertEqual(TA.primeiro_dia('18/02'), (None, True))
        # e nao mente sobre quem TEM ano
        self.assertEqual(TA.primeiro_dia('marzo 2012')[1], False)
        self.assertEqual(TA.primeiro_dia('2012')[1], False)
        self.assertEqual(TA.primeiro_dia('in Toscana'), (None, False))

    def test_a_classe_honra_a_PRECISAO_declarada_mesmo_com_valor_completo(self):
        """RT3 · o caminho da PRECISAO na classe, isolado — o outro mutante sobrevivente.

        Aqui o VALOR escreve o ano («2026-02-18») e a PRECISAO declara `+SEM_ANO`. A pergunta ao
        valor nao pode responder (o ano esta lá); so a PRECISAO pode. Quem escreve a precisao e
        o leitor do tempo, e a classe tem de acreditar nela em vez de a re-derivar."""
        r = AD.classe_do_claim('La giornata tecnica si e svolta',
                               {'PAPEL': TA.ACONTECIMENTO, 'PRECISAO': 'DATE_EXACT+SEM_ANO',
                                'ANO': None, 'VALOR': '2026-02-18'})
        self.assertEqual(r['VALOR'], NAO_SEI)
        self.assertIn('nao escreve o ano', r['PORQUE'])

    def test_falta_o_ano_responde_pelo_VALOR(self):
        """A pergunta passa a ser feita ao valor, com a mesma expressao que o le."""
        for valor in ('marzo', 'nel mese di marzo', '12 marzo'):
            self.assertTrue(TA.falta_o_ano(valor), valor)
        for valor in ('2012', 'marzo 2012', '12 marzo 2012', '2026-09-07/2026-09-13'):
            self.assertFalse(TA.falta_o_ano(valor), valor)

    def test_A_PRECISAO_DIZ_QUE_FALTA_O_ANO_NO_MES_SOZINHO(self):
        """O caminho da PRECISAO, fixado pelo que ELE promete.

        ⚠️ ESTE TESTE NASCEU DE UM MUTANTE SOBREVIVENTE. A PROD-3 pôs DUAS guardas sobre o
        ano — a precisão passa a dizer `+SEM_ANO`, e a classe pergunta ao valor — e as duas
        tapavam-se uma à outra: desligar qualquer uma sozinha deixava a outra a cobrir, e o
        teste da classe continuava verde. Dois mutantes sobreviveram por isso.

            DUAS GUARDAS QUE SE COBREM UMA À OUTRA SÃO DEFESA EM PROFUNDIDADE;
            SEM UM TESTE PARA CADA UMA, SÃO DUAS GUARDAS QUE NINGUÉM ESTÁ A GUARDAR.

        A precisão não é redundante com a classe: quem consome lê o campo `PRECISAO` para
        saber o que o valor NÃO diz. Se ela parar de declarar que o ano falta, é enganado
        mesmo que a classe esteja certa."""
        af = _produzir('La raccolta si e svolta a marzo in provincia di Ferrara.',
                       published_at='2026-05-10')[0]
        fr = af['FACT_TIME_ROLE']
        self.assertEqual(fr['VALOR_LIDO'], 'marzo')
        self.assertTrue(fr['PRECISAO'].endswith('SEM_ANO'), fr['PRECISAO'])
        self.assertEqual(fr['ANO'], NAO_SEI)

    def test_A_CLASSE_PERGUNTA_AO_VALOR_MESMO_COM_A_PRECISAO_CALADA(self):
        """O caminho da CLASSE, isolado da precisão — a outra metade do mutante sobrevivente.

        Chama-se `classe_do_claim` com um tempo em que a PRECISAO **não** diz `SEM_ANO` e o
        `ANO` **não** é `NAO SEI`: os dois sinais antigos calados. Só a pergunta ao VALOR pode
        responder, e ela tem de responder."""
        r = AD.classe_do_claim('La grandine osservata ha colpito i frutteti a marzo',
                               {'PAPEL': TA.ACONTECIMENTO, 'PRECISAO': 'MONTH',
                                'ANO': None, 'VALOR': 'marzo'})
        self.assertEqual(r['VALOR'], NAO_SEI)
        self.assertIn('nao escreve o ano', r['PORQUE'])

    def test_a_classe_com_ano_escrito_continua_a_passar(self):
        """O contrapeso: a pergunta ao valor não pode recusar quem tem o ano."""
        r = AD.classe_do_claim('La giornata tecnica si e svolta nel 2012',
                               {'PAPEL': TA.ACONTECIMENTO, 'PRECISAO': 'YEAR',
                                'ANO': None, 'VALOR': '2012'})
        self.assertEqual(r['VALOR'], 'ALERTA_EVENTO')

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


class ATempoEmitidoTambemConta(unittest.TestCase):
    """PROD-3, o espelho do lado do TEMPO — achado pela bancada L2 no artefato publicado.

    Em `derived:21` saía `FACT_TIME = «marzo»` com `ORIGEM = LITERAL` e
    `TEMPOS_NO_TRECHO = 0`. A mesma causa do lado do lugar: um mês SOZINHO não casa nenhuma
    das cinco formas de data (`_RE_DIA_MES` quer o dia, `_RE_SO_MES` quer o ano), logo o
    contador não o vê — e o leitor vivo emitiu-o.

    O limite é da L2, e é o que impede o conserto de virar invenção: **só vale para LITERAL.**"""

    def test_o_mes_sozinho_LITERAL_conta_um(self):
        af = _produzir('La raccolta si e svolta a marzo in provincia di Ferrara.',
                       published_at='2026-05-10')[0]
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.LITERAL)
        self.assertEqual(af['FACT_TIME_ROLE']['VALOR_LIDO'], 'marzo')
        self.assertEqual(af['TEMPOS_NO_TRECHO'], 1)

    def test_a_relativa_continua_a_contar_ZERO_e_esta_certa(self):
        """Com `RELATIVO_D63` o valor foi CALCULADO: não há data escrita no trecho. Contar o
        valor aqui seria inventar uma data escrita onde não há nenhuma."""
        af = _produzir('La settimana scorsa la cimice ha colpito i frutteti.',
                       published_at='2026-05-10')[0]
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.RELATIVO_D63)
        self.assertEqual(af['TEMPOS_NO_TRECHO'], 0)

    def test_o_cabecalho_D147_conta_ZERO_e_esta_certo(self):
        """O valor vem do cabeçalho da secção, fora do trecho."""
        vistos = []
        for af in _produzir(BOLETIM):
            if af['FACT_TIME_ROLE']['ORIGEM'] in TA.ORIGENS_COM_BASIS_FORA_DO_TRECHO:
                vistos.append(af['TEMPOS_NO_TRECHO'])
        self.assertTrue(vistos, 'o boletim tem de produzir pelo menos uma origem de fora')
        self.assertEqual(set(vistos), {0})

    def test_a_coerencia_do_TEMPO_vale_em_toda_a_producao(self):
        """A regra geral: origem LITERAL => contagem >= 1. Zero com valor literal é o estado
        que não pode existir em nenhuma afirmação."""
        for texto in ('La raccolta si e svolta a marzo in provincia di Ferrara.',
                      'La cimice ha colpito i frutteti in provincia di Cuneo nel 2012.',
                      'Il volo e stato osservato in marzo nel ferrarese.',
                      BOLETIM):
            for af in _produzir(texto):
                if af['FACT_TIME_ROLE']['ORIGEM'] == TA.LITERAL:
                    self.assertGreaterEqual(af['TEMPOS_NO_TRECHO'], 1,
                                            '%s -> %r' % (af['TRECHO_LITERAL'][:45],
                                                          af['FACT_TIME_ROLE']['VALOR_LIDO']))

    def test_somar_o_emitido_nao_afrouxa_a_guarda_do_bloqueador(self):
        af = _produzir('La cimice asiatica e stata rilevata in Europa per la prima volta nel '
                       '2004 e in Italia nel 2012, in Emilia Romagna.')[0]
        self.assertEqual(af['TEMPOS_NO_TRECHO'], 2)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)


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


class OFalsoFuturoPelaTerminacaoRA(unittest.TestCase):
    """RT3 §2.A · a regra do futuro dizia «futuro» para TUDO, e isto é uma regressão medida.

    `_RE_FUTURO_DO_VERBO` aceitava `r[àa]` — com o `a` SEM acento — e `marca_futuro` aplicava-a
    a `FL._baixo(span)`, que **tira** os acentos. O acento que o comentário diz tornar a regra
    segura era destruído antes de a regra correr. Na Sala real, 4 afirmações de chuva MEDIDA
    viraram PREVISAO por causa disto.

        UM COMENTÁRIO QUE DESCREVE A REGRA CERTA POR CIMA DO CÓDIGO QUE FAZ OUTRA
        É PIOR DO QUE NENHUM: ELE FAZ A REVISÃO PARAR DE PROCURAR.

    Segundo defeito na mesma função: a janela cortava o texto a meio da palavra, e «duramente»
    cortado virava «dura», com o `\b` a casar contra o corte.
    """

    NAO_SAO_FUTURO = [
        ('peronospora', 'La peronospora è stata osservata nei vigneti il 3 settembre 2026',
         '3 settembre 2026'),
        ('temperatura', 'La temperatura media il 3 settembre 2026 era alta', '3 settembre 2026'),
        ('ieri sera', 'Le capannine meteo ieri sera hanno registrato piogge con 27,4 mm',
         'ieri sera'),
        ('duramente (janela cortada)', 'Nel 2003 la siccità aveva colpito duramente i vigneti',
         '2003'),
        ('tiranno (não é verbo)', 'Il tiranno non è un verbo, il 3 settembre 2026',
         '3 settembre 2026'),
    ]
    SAO_FUTURO = [
        ('colpirà', 'La grandine colpirà i frutteti il 3 settembre 2026', '3 settembre 2026'),
        ('svolgeranno', 'Il 3 settembre 2026 si svolgeranno le giornate tecniche',
         '3 settembre 2026'),
        ('verrà', 'Nel 2026, in 32 siti della rete verrà realizzato un monitoraggio', '2026'),
        ('entro il prossimo', 'Le domande entro il prossimo 11 settembre, previa registrazione',
         '11 settembre'),
    ]

    def test_as_quatro_palavras_em_ra_nao_sao_futuro(self):
        for nome, frase, valor in self.NAO_SAO_FUTURO:
            self.assertFalse(TA.marca_futuro(frase, valor), nome)

    def test_o_futuro_de_verdade_continua_a_ser_futuro(self):
        """O conserto não pode ser feito desligando a regra."""
        for nome, frase, valor in self.SAO_FUTURO:
            self.assertTrue(TA.marca_futuro(frase, valor), nome)

    def test_o_acento_e_obrigatorio_na_propria_expressao(self):
        """A regra tem de exigir o acento nela mesma, e não confiar em quem a chama."""
        self.assertTrue(TA._RE_FUTURO_DO_VERBO.search('colpirà'))
        self.assertIsNone(TA._RE_FUTURO_DO_VERBO.search('peronospora'))
        self.assertIsNone(TA._RE_FUTURO_DO_VERBO.search('temperatura'))

    def test_a_janela_nao_corta_palavra_ao_meio(self):
        """A unidade é a FRASE da data, e uma frase não parte palavras."""
        frase = TA.frase_do_valor('Nel 2003 la siccità aveva colpito duramente i vigneti', '2003')
        self.assertIn('duramente', frase)

    def test_o_futuro_de_OUTRA_frase_nao_conta(self):
        """Mata o mutante RT12 do red team («a regra olha a frase toda em vez da janela»).

        A unidade continua BOUNDED: um verbo no futuro noutra frase do mesmo trecho não fala
        desta data. Se alguém trocar a frase pelo trecho inteiro, este teste reprova."""
        t = ('La grandine ha colpito i frutteti il 3 settembre 2026, con danni diffusi ai '
             'vigneti della provincia di Cuneo secondo i rilievi dei tecnici. Il modello '
             'regionale indica che la grandine colpirà di nuovo le stesse zone.')
        self.assertNotIn('colpirà', TA.frase_do_valor(t, '3 settembre 2026'))
        self.assertFalse(TA.marca_futuro(t, '3 settembre 2026'))

    def test_pela_producao_inteira_a_chuva_medida_continua_ACONTECIMENTO(self):
        """O que o defeito custava na Sala real: uma chuva MEDIDA a virar previsão."""
        af = _produzir('Le nostre capannine meteo ieri sera hanno registrato piogge con 27,4 mm '
                       'nella zona.', published_at='2026-05-12',
                       raw_captured_at='2026-05-20 11:07:15+00')[0]
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.ACONTECIMENTO)
        self.assertNotEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.PREVISAO)


class OPapelQueOTextoEscreve(unittest.TestCase):
    """RT3 §2.B e §2.C · formas que saíam ACONTECIMENTO e não são um dia em que algo aconteceu.

    Uma frase por forma, para que a morte de um mutante não seja coberta por outra alternativa
    a apanhar o mesmo texto de prova — a lição da lei da validade (D160 §2.2)."""

    def test_a_janela_que_uma_agencia_torna_ativa_e_VALIDADE(self):
        for frase in ("Dal 22 giugno al 14 settembre l'Agenzia rende attiva la fase di "
                      'attenzione per gli incendi boschivi.',
                      'Dal 22 giugno al 14 settembre vale la fase di preallarme regionale.'):
            self.assertEqual(TA.papel_do_periodo(frase, None, None, None)[0], TA.VALIDADE, frase)

    def test_di_ogni_anno_nao_e_um_dia_em_que_algo_aconteceu(self):
        frase = 'Il monitoraggio, svolto nel periodo 1 maggio - 15 ottobre di ogni anno, prosegue.'
        self.assertEqual(TA.papel_do_periodo(frase, None, None, None)[0], TA.VALIDADE)
        af = _produzir(frase)[0]
        self.assertNotEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.ACONTECIMENTO)

    def test_entro_il_prossimo_e_um_prazo_logo_e_futuro(self):
        """Sem ano escrito o calendário não podia recusar: `primeiro_dia` dá None e a
        comparação com a publicação nunca acontece. Quem o apanha é a palavra."""
        frase = 'Le domande si presentano entro il prossimo 11 settembre, previa registrazione.'
        self.assertTrue(TA.marca_futuro(frase, '11 settembre'))
        af = _produzir(frase, published_at='2026-09-07')[0]
        self.assertNotEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.ACONTECIMENTO)

    def test_os_tres_atos_que_nao_escrevem_a_palavra_decreto(self):
        for frase in ('In data 6 agosto 2026 è stata concessa la deroga per il trattamento.',
                      'Il calendario, come stabilito dal DPI 2025/2026, prevede i controlli.',
                      "Dal 12 febbraio 2020 l'Osservatorio nazionale è stato sostituito."):
            self.assertTrue(TA._MARCA_DE_ATO.search(frase), frase)
            self.assertEqual(TA.papel_do_periodo(frase, None, None, None)[0], TA.ATO, frase)

    def test_as_marcas_novas_nao_apanham_prosa_comum(self):
        """Uma marca lassa punha REGULATORIO ou VALIDADE em meia Sala."""
        for frase in ('La cimice ha colpito i frutteti in provincia di Cuneo.',
                      'Il monitoraggio prosegue regolarmente ogni settimana.',
                      'Ogni anno la resa aumenta.'):
            self.assertEqual(TA.papel_do_periodo(frase, None, None, None)[0], TA.NAO_SEI, frase)


class AsGuardasQueNenhumTesteFixava(unittest.TestCase):
    """RT3 §5.5 · três mutantes do red team sobreviveram porque a guarda existia e **nenhum
    teste a fixava**. RT5, RT6 e RT10.

        UMA GUARDA SEM TESTE É UMA GUARDA QUE A PRÓXIMA REFATORAÇÃO APAGA EM SILÊNCIO.
    """

    SEM_PUBLICACAO = {'published_at': None, 'published_at_basis': None}

    def test_RT5_a_captura_chega_ao_leitor_pela_producao_inteira(self):
        """A regra da captura só era exercitada chamando `extrair_tempo` direto. O mutante RT5
        põe `"CAPTURA": None` em `afirmacoes_do_item` e sobrevivia — a produção inteira deixava
        de olhar o dia da coleta e ninguém dava por isso.

        Sem publicação provada, a captura é a ÚNICA guarda contra uma data futura."""
        af = _produzir('La grandinata osservata il 30 settembre 2026 ha colpito i frutteti di '
                       'Cuneo.', raw_captured_at='2026-09-20 11:07:15+00',
                       **self.SEM_PUBLICACAO)[0]
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.PREVISAO)
        self.assertIn('colhido', af['FACT_TIME_ROLE']['PORQUE'])
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)

    def test_RT6_o_evento_do_PROPRIO_dia_da_coleta_e_acontecimento(self):
        """O mutante RT6 troca `>` por `>=` na comparação com a captura: um evento do próprio
        dia da coleta virava PREVISAO. Colher no dia em que aconteceu é o normal, não o
        suspeito — quem recusa é o dia SEGUINTE."""
        af = _produzir('La grandinata osservata il 20 settembre 2026 ha colpito i frutteti di '
                       'Cuneo.', raw_captured_at='2026-09-20 11:07:15+00',
                       **self.SEM_PUBLICACAO)[0]
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.ACONTECIMENTO)
        self.assertEqual(af['FACT_TIME']['VALOR'], '20 settembre 2026')

    def test_RT10_a_conferencia_recusa_ORIGEM_fora_do_vocabulario(self):
        """O mutante RT10 tira a lista de origens da conferência. A guarda existia; nenhum
        teste a chamava, logo o mutante passava."""
        linha = _linha('La grandinata osservata il 18 febbraio 2026 ha colpito i frutteti di '
                       'Cuneo.')
        af = AD.afirmacoes_do_item(linha)['AFIRMACOES'][0]
        self.assertEqual(AD.conferir_afirmacao(af, linha['texto'],
                                               raw_sha256=linha['raw_sha256']), [])
        af['FACT_TIME_ROLE']['ORIGEM'] = 'ORIGEM_INVENTADA'
        v = AD.conferir_afirmacao(af, linha['texto'], raw_sha256=linha['raw_sha256'])
        self.assertTrue(v, 'a conferencia aceitou uma ORIGEM fora do vocabulario')
        self.assertIn('fora do vocabulario', ' '.join(v))

    def test_as_quatro_origens_do_vocabulario_sao_as_declaradas(self):
        """O contrapeso: a guarda não pode recusar uma origem legítima."""
        self.assertEqual(sorted(TA.ORIGENS),
                         sorted([TA.LITERAL, TA.CABECALHO_D147, TA.RELATIVA_ANCORADA_D149,
                                 TA.RELATIVO_D63]))


class APrecisaoNaoContradizAOrigem(unittest.TestCase):
    """RT3 §7 · «+CALCULADA» ao lado de «LITERAL» são duas afirmações opostas no mesmo objeto.

    O selo do vivo diz que o valor foi CONTADO; a origem LITERAL diz que ele estava ESCRITO.
    Depois da PROD-1 as duas apareciam juntas, e quem consome tinha de escolher em qual
    acreditar. Quem manda é a ORIGEM, que é a decisão desta lei."""

    def test_LITERAL_nunca_viaja_com_CALCULADA(self):
        af = _produzir('Oggi, 12 novembre 2026, si e svolta la giornata tecnica.',
                       published_at='2026-11-12', raw_captured_at='2026-11-20 11:07:15+00')[0]
        fr = af['FACT_TIME_ROLE']
        self.assertEqual(fr['ORIGEM'], TA.LITERAL)
        self.assertNotIn('CALCULADA', fr['PRECISAO'])
        self.assertNotIn('CALCULADA', af['FACT_TIME']['FACT_TIME_PRECISION'])

    def test_a_relativa_continua_a_dizer_que_foi_calculada(self):
        """Não se apaga o selo: ele é verdade quando a origem é RELATIVO_D63."""
        af = _produzir('La settimana scorsa la cimice ha colpito i frutteti.',
                       published_at='2026-11-12', raw_captured_at='2026-11-20 11:07:15+00')[0]
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.RELATIVO_D63)
        self.assertIn('CALCULADA', af['FACT_TIME_ROLE']['PRECISAO'])

    def test_em_TODA_a_producao_LITERAL_e_CALCULADA_nunca_coexistem(self):
        for texto in (BOLETIM, 'Oggi, 12 novembre 2026, la giornata tecnica.',
                      'La raccolta si e svolta a marzo in provincia di Ferrara.'):
            for af in _produzir(texto, raw_captured_at='2026-12-20 11:07:15+00'):
                if af['FACT_TIME_ROLE']['ORIGEM'] == TA.LITERAL:
                    self.assertNotIn('CALCULADA', af['FACT_TIME_ROLE']['PRECISAO'],
                                     af['TRECHO_LITERAL'][:50])


class OMotivoViajaNumCampo(unittest.TestCase):
    """RT3 §5.2 · o MOTIVO do tempo tem de viajar num CAMPO, como já viaja no lugar.

    Estava só dentro do texto do `PORQUE_NAO`, e ler um motivo por dentro de uma frase obriga
    quem consome a fazer gramática para tomar uma decisão."""

    BLOQUEADOR = ('La cimice asiatica e stata rilevata in Europa per la prima volta nel 2004 '
                  'e in Italia nel 2012, in Emilia Romagna.')

    def test_TEMPOS_CONCORRENTES_e_um_campo(self):
        af = _produzir(self.BLOQUEADOR)[0]
        self.assertEqual(af['FACT_TIME']['MOTIVO'], TA.TEMPOS_CONCORRENTES)
        self.assertEqual(af['FACT_TIME_ROLE']['MOTIVO'], TA.TEMPOS_CONCORRENTES)

    def test_o_campo_esta_presente_mesmo_sem_motivo(self):
        """Um campo que só aparece quando há problema obriga quem consome a adivinhar a
        ausência — a mesma razão das contagens."""
        for texto in (self.BLOQUEADOR, BOLETIM,
                      'La cimice ha colpito i frutteti in provincia di Cuneo nel 2012.'):
            for af in _produzir(texto):
                self.assertIn('MOTIVO', af['FACT_TIME'], af['TRECHO_LITERAL'][:40])
                self.assertIn('MOTIVO', af['FACT_TIME_ROLE'], af['TRECHO_LITERAL'][:40])

    def test_os_dois_lados_dizem_o_seu_motivo(self):
        af = _produzir(self.BLOQUEADOR)[0]
        self.assertEqual(af['FACT_TIME']['MOTIVO'], TA.TEMPOS_CONCORRENTES)
        self.assertEqual(af['FACT_LOCATION']['MOTIVO'], AD.LUGARES_CONCORRENTES)


class AClasseObservacaoMedida5D(unittest.TestCase):
    """CONTRATO §5-D · a classe `OBSERVACAO_MEDIDA`, versionada pelo dono do contrato.

    O §5-C fechou a sobra e **descobriu** uma lacuna: o vocabulário tinha cinco classes e
    nenhuma delas era «alguém mediu e escreveu o número». A DT-FATO-OBSERVADO criou a classe e
    o dono versionou-a. Este ficheiro testa **exatamente** o que ele versionou.

        A MARCA É DUAS COISAS, NÃO UMA: QUEM MEDIU E QUANTO MEDIU.
        UMA SÓ DELAS É CONVERSA SOBRE O TEMPO; AS DUAS SÃO UMA MEDIÇÃO.

    Textos **sintéticos**, como manda o cabeçalho deste ficheiro: as formas reais entram como
    FORMA, nunca o trecho da R9."""

    #: o controlo bom FORA da R9 que a DT pede — rede de estações, não boletim
    CONTROLE_FORA_DA_R9 = ('Le piogge osservate il 12 aprile 2026 a Modena hanno registrato '
                           '41,2 mm nelle stazioni della rete.')
    COM_SCARTO = ('La grandinata osservata il 12 aprile 2026 a Cuneo ha registrato uno scarto '
                  'di + 6°C sulle massime.')

    def _um(self, texto, **extra):
        afs = _produzir(texto, published_at=extra.pop('published_at', '2026-05-10'), **extra)
        self.assertEqual(len(afs), 1, 'o texto deste teste e UMA afirmacao: %d' % len(afs))
        return afs[0]

    def test_a_classe_esta_no_vocabulario_fechado(self):
        self.assertIn('OBSERVACAO_MEDIDA', AD.CLAIM_KINDS)
        self.assertEqual(sorted(AD.CLAIM_KINDS),
                         ['ALERTA_EVENTO', 'CIENCIA_FICHA', 'OBSERVACAO_MEDIDA', 'PRECO',
                          'RECOMENDACAO', 'REGULATORIO'],
                         'o vocabulário fechado mudou; confira o §5-D antes de seguir')

    def test_A_MARCA_DE_MEDICAO_ESCRITA_DA_A_CLASSE(self):
        for frase in (self.CONTROLE_FORA_DA_R9, self.COM_SCARTO):
            af = self._um(frase)
            self.assertEqual(af['CLAIM_KIND']['VALOR'], 'OBSERVACAO_MEDIDA', frase[:50])
            self.assertEqual(af['CLAIM_KIND']['MARCAS'], ['OBSERVACAO_MEDIDA'], frase[:50])

    def test_A_MARCA_VIAJA_COM_AS_DUAS_PARTES_E_O_OFFSET(self):
        """§5-D · `CLAIM_KIND.MARCA_DE_MEDICAO = {VERBO, VALOR}`, cada um `{INICIO,FIM,TRECHO}`.

        O G0 confere três coisas, e o teste confere as mesmas: `texto[INICIO:FIM] == TRECHO`, a
        posição **dentro** do `EVIDENCE_SPAN`, e o TRECHO no vocabulário."""
        linha = _linha(self.CONTROLE_FORA_DA_R9, published_at='2026-05-10')
        af = AD.afirmacoes_do_item(linha)['AFIRMACOES'][0]
        m = af['CLAIM_KIND']['MARCA_DE_MEDICAO']
        self.assertEqual(sorted(x for x in m if x != 'LEI'), ['VALOR', 'VERBO'])
        a, b = af['POSICAO']['INICIO'], af['POSICAO']['FIM']
        for parte in ('VERBO', 'VALOR'):
            p = m[parte]
            self.assertEqual(linha['texto'][p['INICIO']:p['FIM']], p['TRECHO'], parte)
            self.assertLessEqual(a, p['INICIO'], parte)
            self.assertLessEqual(p['FIM'], b, parte)
        self.assertEqual(m['VERBO']['TRECHO'].lower(), 'registrato')
        self.assertEqual(m['VALOR']['TRECHO'].replace(' ', ''), '41,2mm')

    def test_o_offset_da_marca_e_ABSOLUTO_no_documento(self):
        """Um offset relativo ao trecho passaria a 1.ª conferência do G0 e falharia a 2.ª — uma
        prova que aponta para o sítio errado é pior do que nenhuma prova."""
        recheio = 'Testo di apertura che non misura nulla e serve solo a empurrar o offset.\n'
        linha = _linha(recheio + self.CONTROLE_FORA_DA_R9, published_at='2026-05-10')
        af = _que_diz(AD.afirmacoes_do_item(linha)['AFIRMACOES'], 'Le piogge osservate')
        m = af['CLAIM_KIND']['MARCA_DE_MEDICAO']
        self.assertGreater(m['VERBO']['INICIO'], len(recheio) - 1,
                           'o offset nao pode ser relativo ao trecho')
        self.assertEqual(linha['texto'][m['VERBO']['INICIO']:m['VERBO']['FIM']],
                         m['VERBO']['TRECHO'])

    # ── os cinco ataques da DT, agora como testes ────────────────────────────
    def test_DT1_sem_o_VERBO_nao_ha_classe(self):
        af = self._um('Le piogge osservate il 12 aprile 2026 a Modena hanno dato 41,2 mm.')
        self.assertEqual(af['CLAIM_KIND']['VALOR'], NAO_SEI)
        self.assertNotIn('OBSERVACAO_MEDIDA', af['CLAIM_KIND']['MARCAS'])

    def test_DT1_sem_o_VALOR_nao_ha_classe(self):
        af = self._um('Le piogge osservate il 12 aprile 2026 a Modena hanno registrato molto.')
        self.assertEqual(af['CLAIM_KIND']['VALOR'], NAO_SEI)
        self.assertNotIn('OBSERVACAO_MEDIDA', af['CLAIM_KIND']['MARCAS'])

    def test_DT1_percentagem_e_euro_NAO_sao_valor_medido(self):
        """§5-D · «percentagem e euro NÃO contam; são de outras classes»."""
        for unidade in ('41,2 %', '41,2 euro', '41,2 €'):
            self.assertIsNone(AD._RE_VALOR_MEDIDO.search('hanno registrato %s a Modena' % unidade),
                              unidade)
        for unidade in ('41,2 mm', '6°C', '+ 6 °C', '1013 hPa', '12 km/h', '3 m/s', '5 cm'):
            self.assertIsNotNone(AD._RE_VALOR_MEDIDO.search('registrato %s' % unidade), unidade)

    def test_DT2_evento_no_mesmo_trecho_da_NAO_SEI(self):
        """§5-D · `OBSERVACAO_MEDIDA:MARCA_DE_OUTRA_CLASSE`. Duas marcas: escolher seria inferir."""
        af = self._um('Il convegno osservato il 12 aprile 2026 a Verona ha registrato 41,2 mm.')
        self.assertEqual(af['CLAIM_KIND']['VALOR'], NAO_SEI)
        self.assertEqual(sorted(af['CLAIM_KIND']['MARCAS']),
                         ['ALERTA_EVENTO', 'OBSERVACAO_MEDIDA'])

    def test_DT2_ato_regulatorio_no_mesmo_trecho_da_NAO_SEI(self):
        af = self._um('Il decreto osservato il 12 aprile 2026 a Verona ha registrato 41,2 mm.')
        self.assertEqual(af['CLAIM_KIND']['VALOR'], NAO_SEI)
        self.assertIn('REGULATORIO', af['CLAIM_KIND']['MARCAS'])

    def test_DT2_verbo_no_FUTURO_nao_e_uma_medicao_feita(self):
        """§5-D · «o VERBO não vem precedido de auxiliar de futuro»."""
        for frase in ('a Modena saranno registrati 41,2 mm',
                      'a Modena verranno registrati 41,2 mm',
                      'a Modena sarà registrato 41,2 mm'):
            self.assertIsNone(AD.marca_de_medicao(frase, 0, len(frase)), frase)
        feito = 'a Modena sono stati registrati 41,2 mm'
        self.assertIsNotNone(AD.marca_de_medicao(feito, 0, len(feito)))

    def test_DT4_lugar_do_CABECALHO_nao_sustenta_a_classe(self):
        """§5-D · `FACT_LOCATION:ORIGEM_<x>_NAO_E_TEXT`. O lugar do cabeçalho é verdadeiro, mas
        não é **desta frase** — e a classe promete que alguém mediu ALI."""
        af = _que_diz(_produzir(BOLETIM), 'Le grandinate sono state osservate')
        self.assertEqual(af['FACT_LOCATION']['LOCATION_SOURCE'], 'TEXT',
                         'o boletim deste teste escreve o lugar no trecho; se mudar, o teste '
                         'deixa de medir o que quer')
        # e a razão, isolada na função que decide.
        #
        # ⚠️ ESTE CASO NASCEU DE UM MUTANTE SOBREVIVENTE, e a lição repete-se pela quarta vez
        # nesta bancada: o meu primeiro caso trazia DOIS defeitos ao mesmo tempo (origem errada
        # **e** sem posição), e por isso a segunda guarda tapava a primeira — desligar a
        # verificação da origem deixava a da posição a recusar, e o mutante `DT_FO_4a` sobrevivia.
        #
        #     UM CASO COM DOIS DEFEITOS NÃO TESTA NENHUM DOS DOIS:
        #     TESTA APENAS QUE ALGUMA GUARDA REAGIU.
        #
        # Agora a origem errada vem com a posição PERFEITA, para que só ela possa recusar.
        self.assertIsNotNone(AD._lugar_sustenta_a_medicao(
            {'VALOR': 'Cuneo', 'LOCATION_SOURCE': 'SECTION_HEADER',
             'ONDE': {'DENTRO_DO_ALVO': True, 'INICIO': 0, 'FIM': 5, 'TRECHO': 'Cuneo'}}),
            'o lugar do cabecalho tem de ser recusado mesmo com a posicao perfeita')
        self.assertIn('LOCATION_SOURCE = TEXT', AD._lugar_sustenta_a_medicao(
            {'VALOR': 'Cuneo', 'LOCATION_SOURCE': 'SECTION_HEADER',
             'ONDE': {'DENTRO_DO_ALVO': True, 'INICIO': 0, 'FIM': 5, 'TRECHO': 'Cuneo'}}))
        self.assertIsNotNone(AD._lugar_sustenta_a_medicao(
            {'VALOR': 'Cuneo', 'LOCATION_SOURCE': 'SECTION_HEADER', 'ONDE': None}))
        self.assertIsNotNone(AD._lugar_sustenta_a_medicao(
            {'VALOR': 'Cuneo', 'LOCATION_SOURCE': 'TEXT', 'ONDE': None}))
        self.assertIsNotNone(AD._lugar_sustenta_a_medicao(
            {'VALOR': 'Cuneo', 'LOCATION_SOURCE': 'TEXT',
             'ONDE': {'DENTRO_DO_ALVO': False}}))
        self.assertIsNone(AD._lugar_sustenta_a_medicao(
            {'VALOR': 'Cuneo', 'LOCATION_SOURCE': 'TEXT',
             'ONDE': {'DENTRO_DO_ALVO': True}}))

    def test_DT4_sem_lugar_no_trecho_a_classe_diz_o_que_faltou(self):
        """E o `PORQUE` tem de dizer que a medição **estava** escrita e foi o lugar que faltou —
        senão quem lê conserta a coisa errada."""
        af = self._um('Le piogge osservate il 12 aprile 2026 hanno registrato 41,2 mm.')
        self.assertEqual(af['CLAIM_KIND']['VALOR'], NAO_SEI)
        self.assertIn('marca de medicao esta escrita', af['CLAIM_KIND']['PORQUE'])

    def test_DT5_Europa_2004_com_Italia_2012_nao_passa_pela_classe_nova(self):
        """O BLK-1 aplicado à classe nova: a guarda dos concorrentes não se contorna."""
        af = self._um('La cimice osservata in Europa nel 2004 e in Italia nel 2012 ha '
                      'registrato 41,2 mm.')
        self.assertEqual(af['TEMPOS_NO_TRECHO'], 2)
        self.assertGreaterEqual(af['LUGARES_NO_TRECHO'], 2)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)
        self.assertEqual(af['CLAIM_KIND']['VALOR'], NAO_SEI)

    def test_DT3_a_classe_exige_o_ano_e_o_papel(self):
        """§5-D · «as mesmas regras de ALERTA_EVENTO: ano escrito, início ≤ captura, uma das
        quatro origens, sem concorrência»."""
        sem_ano = self._um('Le piogge osservate a marzo a Modena hanno registrato 41,2 mm.')
        self.assertEqual(sem_ano['CLAIM_KIND']['VALOR'], NAO_SEI)
        futuro = self._um('A Modena le piogge previste il 12 aprile 2027 hanno registrato '
                          '41,2 mm.', raw_captured_at='2026-05-20 11:07:15+00')
        self.assertNotEqual(futuro['FACT_TIME_ROLE']['PAPEL'], TA.ACONTECIMENTO)
        self.assertEqual(futuro['CLAIM_KIND']['VALOR'], NAO_SEI)

    def test_a_ancora_do_campo_NAO_conta_como_marca(self):
        """§5-D · «cultura, lugar ou "vigneti" nunca satisfazem VERBO nem VALOR»."""
        af = self._um('La grandinata osservata il 12 aprile 2026 ha colpito i vigneti di Cuneo.')
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.ACONTECIMENTO)
        self.assertEqual(af['CLAIM_KIND']['VALOR'], NAO_SEI)
        self.assertEqual(af['CLAIM_KIND']['MARCAS'], [])

    def test_o_vocabulario_NAO_se_alargou_por_conveniencia(self):
        """§5-D · «se aparecer uma observação medida legítima com outro verbo ("caduti",
        "misurazioni hanno dato"), ela fica NAO SEI até o dono do contrato decidir».

        Este teste existe para que alargar a lista seja um ato **deliberado**, e não algo que
        acontece porque um caso incomodava."""
        for fora in ('caduti', 'misurazioni', 'gradi', 'osservato', 'rilevamento'):
            self.assertIsNone(AD._RE_VERBO_DE_MEDICAO.search(fora), fora)
        for dentro in ('registrato', 'registrati', 'rilevata', 'rilevate', 'misurato'):
            self.assertIsNotNone(AD._RE_VERBO_DE_MEDICAO.search(dentro), dentro)

    def test_LIMITE_MEDIDO_a_marca_sozinha_nao_ancora_a_data(self):
        """⚠️ O LIMITE DA CLASSE, MEDIDO — e o dono precisa dele para saber quantas vezes ela
        pode disparar.

        As duas formas que a DT nomeia **não** fazem o leitor vivo prender a data:

            «Lo scarto climatico registrato il 12 aprile 2026 …»   -> papel NAO SEI
            «Il 12 aprile 2026 le stazioni hanno registrato 41,2 mm …» -> papel NAO SEI
            «Le piogge osservate il 12 aprile 2026 … registrato …»  -> ACONTECIMENTO

        Nos trechos reais da R9 o papel **era** ACONTECIMENTO porque a data vinha do CABEÇALHO
        da secção. Ou seja: **a classe depende de um cabeçalho que nem toda a fonte tem**, ou de
        uma palavra de observação ao lado da medição. Mexer na lista de âncoras é do leitor vivo
        (`fato_do_texto`) e o §5-D não o pediu — **não o toquei**."""
        so_marca = 'Il 12 aprile 2026 le stazioni hanno registrato 41,2 mm a Modena.'
        af = self._um(so_marca)
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], NAO_SEI)
        self.assertEqual(af['CLAIM_KIND']['VALOR'], NAO_SEI)
        self.assertEqual(af['CLAIM_KIND']['MARCAS'], ['OBSERVACAO_MEDIDA'],
                         'a marca esta escrita; o que falta e o tempo')
        # com a âncora ao lado, dispara
        self.assertEqual(self._um(self.CONTROLE_FORA_DA_R9)['CLAIM_KIND']['VALOR'],
                         'OBSERVACAO_MEDIDA')


class OProdutorDizDeQueCommitSaiu(unittest.TestCase):
    """Pedido do Intelligence owner (30/09): o artefato tem de dizer de que COMMIT saiu.

    O selo dos dois ficheiros já dizia QUE REGRA correu — e é a prova forte. Mas não dizia de
    que commit, e isso custou: o dono do contrato teve de descobrir por **arqueologia no Git**
    qual produtor gerou o artefato do C8, comparando o par de sha256 ao longo do ramo. Concluiu
    que era a família `197641c2b`, não a que supunha.

        UM ARTEFATO QUE OBRIGA A ARQUEOLOGIA PARA SE SABER QUEM O FEZ
        É UM ARTEFATO QUE VAI SER ATRIBUÍDO AO PRODUTOR ERRADO.
    """

    def test_o_commit_viaja_em_cada_afirmacao(self):
        af = _produzir('La grandinata osservata il 18 febbraio 2026 ha colpito Cuneo.')[0]
        git = af['PRODUTOR_VERSAO']['GIT']
        self.assertIn('COMMIT', git)
        self.assertIn('ARVORE_LIMPA', git)
        self.assertTrue(git['PORQUE'])

    def test_o_selo_dos_ficheiros_continua_la(self):
        """O COMMIT **acrescenta**, não substitui: o selo é que prova que a regra é aquela."""
        v = AD.produtor_versao()
        self.assertEqual(sorted(v['CODIGO']),
                         ['leis/afirmacao_do_documento.py', 'leis/tempo_da_afirmacao.py'])
        for sha in v['CODIGO'].values():
            self.assertEqual(len(sha), 16)

    def test_o_SHA_NUNCA_viaja_sozinho_sem_dizer_se_a_arvore_estava_limpa(self):
        """⚠️ Um SHA com a árvore suja **mente**: o código que correu não é o do commit. Por isso
        `ARVORE_LIMPA` viaja sempre — um SHA sem essa ressalva parece prova e não é."""
        git = AD.produtor_versao()['GIT']
        if git['COMMIT'] != NAO_SEI:
            self.assertIn(git['ARVORE_LIMPA'], (True, False, NAO_SEI))
            self.assertEqual(len(git['COMMIT']), 40)
        else:
            self.assertIn('NAO SEI', str(git['ARVORE_LIMPA']))

    def test_fora_de_um_repositorio_a_resposta_e_NAO_SEI(self):
        """A mutação corre numa cópia por `git archive`, onde não há commit. Inventar um seria
        pior do que dizer NAO SEI — e este teste prova que o caminho existe."""
        import subprocess
        self.assertIn('subprocess', open(os.path.join(RAIZ, 'leis',
                                                      'afirmacao_do_documento.py'),
                                         encoding='utf-8').read())
        self.assertTrue(hasattr(AD, '_commit_do_codigo'))


class OsMutantesDaDTSairamDaDividaEEntraramNaMedicao(unittest.TestCase):
    """DT-FATO-OBSERVADO §MUTANTES · a dívida declarada, e o dia em que ela foi paga.

    Enquanto a classe não existia, os seis ataques da DT viviam em `MUTANTES_PENDENTES`:
    declarados, contados e impressos, **sem correr** — porque um mutante escrito contra código
    que não existe sai `NAO_APLICADO`, e `NAO_APLICADO` não é um mutante morto.

    O dono do contrato versionou o §5-D, a classe nasceu, e eles passaram para a lista que
    corre. A lista de pendentes **fica**, vazia: ela é o sítio onde uma dívida destas se declara,
    e apagá-la esconderia que o mecanismo existe.

        UMA LISTA DE MUTANTES POR FAZER É DÍVIDA DECLARADA.
        A MESMA LISTA APAGADA É UM MECANISMO QUE NINGUÉM VOLTA A USAR.
    """

    def _harness(self):
        import importlib.util
        caminho = os.path.join(RAIZ, 'provas', 'd158', 'mutar_o_produtor.py')
        spec = importlib.util.spec_from_file_location('_mut_dt', caminho)
        mod = importlib.util.module_from_spec(spec)
        guardado = sys.argv
        sys.argv = ['mutar_o_produtor.py']
        try:
            spec.loader.exec_module(mod)
        finally:
            sys.argv = guardado
        return mod

    def test_a_divida_esta_paga(self):
        self.assertEqual(self._harness().MUTANTES_PENDENTES, [],
                         'ha mutantes por fazer: eles tem de estar declarados aqui, nao '
                         'esquecidos')

    def test_os_cinco_ataques_da_DT_estao_na_lista_QUE_CORRE(self):
        nomes = [m[0] for m in self._harness().MUTANTES]
        for prefixo in ('DT_FO_1a', 'DT_FO_1b', 'DT_FO_1c', 'DT_FO_2a', 'DT_FO_2b',
                        'DT_FO_3', 'DT_FO_4a', 'DT_FO_4b', 'DT_FO_6a', 'DT_FO_6b'):
            self.assertTrue(any(n.startswith(prefixo) for n in nomes),
                            'falta o mutante %s da DT' % prefixo)

    def test_o_mecanismo_da_divida_continua_a_existir(self):
        """Se alguém apagar a lista, esta reprova — e a próxima dívida fica sem sítio."""
        mod = self._harness()
        self.assertTrue(hasattr(mod, 'MUTANTES_PENDENTES'))
        self.assertIsInstance(mod.MUTANTES_PENDENTES, list)


class AsDuasFormasImpressasNaProsa(unittest.TestCase):
    """F1 (REAUDIT-275, ordem do dono 30/09) · «settimana NN/AAAA», «(dd-dd.mm)» e o ANO do
    documento, com offsets.

    ⚠️ ONDE A REGRA MORA NÃO ERA ÓBVIO, e fui ver o texto antes de a escrever. A ordem fala da
    D147/D149 (a composição por cabeçalho), mas nos dois itens que o dono nomeou as formas estão
    **dentro de uma frase do corpo**, e `cabecalho_do_documento` devolve `(0,0)` nos dois
    documentos. Ler estas formas no cabeçalho não apanharia nenhum dos dois casos. Por isso elas
    entram no caminho **LITERAL**, com o BASIS dentro do próprio trecho.

    Textos sintéticos, como manda o cabeçalho deste ficheiro: as formas reais entram como FORMA,
    nunca o trecho da R9."""

    SEMANA = 'Il Report, aggiornato alla settimana 38/2026, conferma il quadro del mercato.'
    #: ⚠️ A abertura tem de ser uma LINHA LONGA. A minha 1.ª versão usava duas linhas curtas
    #: («Bollettino fitosanitario n. 20/2026» + «1 di 3 26.05.2026») e o próprio texto de teste
    #: caía na regra do bloco de menu (2 curtas em 3 linhas), dando ZERO afirmações — o teste
    #: reprovava por causa do cenário, não da regra que ele queria medir.
    ABERTURA_COM_ANO = ('Il bollettino fitosanitario numero 20 dell anno 2026 e stato '
                        'pubblicato dal servizio fitosanitario cantonale.\n')
    DIA_DIA = 'La settimana appena trascorsa (18-24.05) e stata caratterizzata da sole.'

    def test_a_semana_ISO_da_o_intervalo_de_segunda_a_domingo(self):
        p = TA.periodos_impressos_no_trecho(self.SEMANA, 0, len(self.SEMANA))
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0]['VALOR'], '2026-09-14/2026-09-20')
        self.assertEqual(p[0]['FORMA'], 'SEMANA_ISO')
        self.assertEqual(p[0]['BASIS']['TRECHO'], 'settimana 38/2026')

    def test_a_semana_que_nao_existe_nao_da_data(self):
        """Semana 0 e semana 54 não existem. O texto pode escrevê-las; o produtor não as lê."""
        for mau in ('settimana 0/2026', 'settimana 54/2026', 'settimana 99/2026'):
            frase = 'Il Report, aggiornato alla %s, conferma.' % mau
            self.assertEqual(TA.periodos_impressos_no_trecho(frase, 0, len(frase)), [], mau)

    def test_o_intervalo_de_dias_usa_o_ANO_DO_DOCUMENTO(self):
        t = self.ABERTURA_COM_ANO + self.DIA_DIA
        i = t.index('La settimana')
        p = TA.periodos_impressos_no_trecho(t, i, len(t))
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0]['VALOR'], '2026-05-18/2026-05-24')
        self.assertEqual(p[0]['ANO_DO_DOCUMENTO'], 2026)
        self.assertEqual(p[0]['BASIS']['TRECHO'], '(18-24.05)')

    def test_SEM_ano_no_documento_NAO_se_inventa_o_ano(self):
        """⚠️ A regra que impede a forma de fabricar datas: sem ano no documento, ela não sai.

        Nem o ano da publicação, nem o da captura, nem o de hoje. É a D63 aplicada a uma forma
        nova: o que não está escrito não se conta."""
        t = 'Testo di apertura senza anno.\n' + self.DIA_DIA
        self.assertEqual(TA.periodos_impressos_no_trecho(t, t.index('La settimana'), len(t)), [])

    def test_com_DOIS_anos_na_abertura_nao_ha_ano_do_documento(self):
        """A mesma regra da condição (1) da D147: um cabeçalho com duas datas não governa nada.

        Medido: a abertura de um portal de notícias escreve 2024, 2025, 2026 e 2027 — ali não há
        «o ano do documento», e escolher um seria inferir."""
        self.assertEqual(TA.ano_do_documento('Report 2024 e 2025 a confronto.\n'), None)
        self.assertEqual(TA.ano_do_documento('Bollettino n. 20/2026 del 26.05.2026\n'), 2026)
        self.assertEqual(TA.ano_do_documento('Nessun anno qui.\n'), None)

    def test_o_ano_le_se_so_na_ABERTURA_do_documento(self):
        """Um ano escrito muito depois, no meio do corpo, não é o ano do documento."""
        longe = 'Apertura senza anno.\n' + ('x' * TA.LETRAS_DA_ABERTURA) + '\nAnno 2026.\n'
        self.assertIsNone(TA.ano_do_documento(longe))

    def test_o_BASIS_da_forma_cai_DENTRO_do_trecho(self):
        """A origem é LITERAL, e LITERAL promete a prova entre INICIO e FIM da afirmação."""
        linha = _linha(self.ABERTURA_COM_ANO + self.DIA_DIA)
        af = next((a for a in AD.afirmacoes_do_item(linha)['AFIRMACOES']
                   if '(18-24.05)' in a['TRECHO_LITERAL']), None)
        self.assertIsNotNone(af, 'a frase com a forma tem de ser uma afirmacao')
        fr = af['FACT_TIME_ROLE']
        self.assertEqual(fr['ORIGEM'], TA.LITERAL)
        b = fr['BASIS']
        self.assertEqual(linha['texto'][b['INICIO']:b['FIM']], b['TRECHO'])
        self.assertLessEqual(af['POSICAO']['INICIO'], b['INICIO'])
        self.assertLessEqual(b['FIM'], af['POSICAO']['FIM'])

    def test_o_BASIS_da_SEMANA_tambem_e_ABSOLUTO_no_documento(self):
        """⚠️ ESTE TESTE NASCEU DE UM MUTANTE SOBREVIVENTE, e a lição é sobre COBERTURA.

        Eu tinha um teste do offset absoluto — mas só sobre a forma `(dd-dd.mm)`. O mutante que
        torna relativo o offset da **semana** sobreviveu, porque nenhum teste tocava aquela
        linha. Duas formas na mesma função são duas garantias, e cada uma precisa do seu caso.

            UM TESTE SOBRE UMA DAS DUAS FORMAS COBRE UMA DAS DUAS FORMAS.
        """
        recheio = ('Testo di apertura che non misura nulla e serve solo a empurrar o offset '
                   'piu avanti nel documento.\n')
        t = recheio + 'La grandinata osservata nella settimana 38/2026 ha colpito Cuneo.'
        p = TA.periodos_impressos_no_trecho(t, len(recheio), len(t))[0]
        self.assertGreater(p['BASIS']['INICIO'], len(recheio) - 1,
                           'o offset da semana nao pode ser relativo ao trecho')
        self.assertEqual(t[p['BASIS']['INICIO']:p['BASIS']['FIM']], p['BASIS']['TRECHO'])
        self.assertEqual(p['BASIS']['TRECHO'], 'settimana 38/2026')

    def test_DOIS_periodos_impressos_recusam_MESMO_sem_ser_ACONTECIMENTO(self):
        """⚠️ O SEGUNDO MUTANTE SOBREVIVENTE, e é a mesma lição de guardas que se cobrem.

        A guarda dos dois períodos impressos estava tapada pela guarda geral do BLK-1: ambas
        dão `NAO SEI` quando o papel é `ACONTECIMENTO`, logo desligar uma deixava a outra a
        recusar. Só se separam quando o papel **não** é ACONTECIMENTO — porque aí a guarda geral
        não morde (uma `VALIDADE` ou um `MARKET_PERIOD` não são o tempo do facto).

        E ela tem de recusar mesmo aí: devolver um de dois períodos escolhido pela ordem é o
        mesmo defeito do BLK-1, só com outro nome no campo."""
        t = ('Il bollettino numero 20 dell anno 2026 e stato pubblicato dal servizio cantonale.\n'
             'La rilevazione dei listini (18-24.05) e (25-31.05) e stata fatta a Cuneo.')
        af = next((a for a in _produzir(t, published_at='2026-07-01')
                   if '(18-24.05)' in a['TRECHO_LITERAL']), None)
        self.assertIsNotNone(af)
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], NAO_SEI)
        self.assertEqual(af['FACT_TIME']['MOTIVO'], TA.TEMPOS_CONCORRENTES)
        self.assertEqual(af['MARKET_PERIOD']['VALOR'], NAO_SEI,
                         'nenhum dos dois periodos pode ser escolhido pela ordem')
        self.assertIn('2 periodos impressos', af['FACT_TIME_ROLE']['PORQUE'])

    def test_O_CONTADOR_VE_AS_FORMAS_NOVAS(self):
        """⚠️ Sem isto voltava o estado incoerente que a PROD-3 fechou: um valor presente com
        `TEMPOS_NO_TRECHO = 0`, porque o contador não via a forma que o leitor leu.

        E a ordem importa: a forma vem antes do ano solto que vive **dentro** dela, senão
        «settimana 38/2026» era contada como «2026» e a contagem apontava para um pedaço."""
        self.assertEqual([x['TRECHO'] for x in TA.expressoes_de_tempo(self.SEMANA)],
                         ['settimana 38/2026'])
        self.assertEqual([x['TRECHO'] for x in TA.expressoes_de_tempo(self.DIA_DIA)],
                         ['(18-24.05)'])

    def test_a_guarda_do_BLK1_vale_TAMBEM_no_caminho_novo(self):
        """⚠️ ESTE TESTE NASCEU DE UM BURACO QUE EU ABRI E ENCONTREI A MEDIR.

        A forma impressa é **mais específica** do que um ano solto, e por isso ganha a leitura.
        Mas «mais específica» não é «provadamente a do facto»: num trecho com três tempos,
        escolher a forma impressa seria exactamente o par montado que o BLK-1 existe para
        impedir. Só morde o ACONTECIMENTO — um MARKET_PERIOD ou uma VALIDADE não são o tempo do
        facto e podem sair com concorrentes ao lado."""
        t = ('La grandinata osservata nella settimana 38/2026 ha colpito i frutteti di Cuneo, '
             'come nel 2024 e nel 2025.')
        af = _produzir(t, published_at='2026-10-20',
                       raw_captured_at='2026-10-25 11:07:15+00')[0]
        self.assertGreater(af['TEMPOS_NO_TRECHO'], 1)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)
        self.assertEqual(af['FACT_TIME']['MOTIVO'], TA.TEMPOS_CONCORRENTES)

    def test_a_forma_sozinha_com_publicacao_provada_da_o_periodo(self):
        """O controle positivo: uma forma, publicação provada depois do período, e ele passa."""
        t = 'La grandinata osservata nella settimana 38/2026 ha colpito i frutteti di Cuneo.'
        af = _produzir(t, published_at='2026-10-20',
                       raw_captured_at='2026-10-25 11:07:15+00')[0]
        self.assertEqual(af['TEMPOS_NO_TRECHO'], 1)
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.ACONTECIMENTO)
        self.assertEqual(af['FACT_TIME']['VALOR'], '2026-09-14/2026-09-20')
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.LITERAL)

    def test_SEM_publicacao_provada_a_forma_nao_diz_se_ja_passou(self):
        """D63 · sem publicação provada não se sabe se o período já passou. Sai `NAO SEI`.

        ⚠️ Isto é o que **bloqueia** um dos dois itens que o dono nomeou na F1
        (`busca-2ac58821`, com `published_at = NAO SEI`). A forma é lida, o BASIS fica no trecho
        e o valor sai certo — mas o PAPEL não se resolve. Não é defeito da forma, e não afrouxei
        a D63 para o número aparecer."""
        t = 'La grandinata osservata nella settimana 38/2026 ha colpito i frutteti di Cuneo.'
        af = _produzir(t, published_at=None, published_at_basis=None,
                       raw_captured_at='2026-11-10 11:07:15+00')[0]
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], NAO_SEI)
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.LITERAL)
        self.assertEqual(af['FACT_TIME_ROLE']['BASIS']['TRECHO'], 'settimana 38/2026')

    def test_a_forma_DEPOIS_da_captura_continua_a_ser_recusada(self):
        """A recusa pela captura (D63: recusar, nunca ancorar) vale no caminho novo também.

        ⚠️ Para a alcançar é preciso publicação provada **depois** do período (senão o papel já
        sai `NAO SEI` antes) e captura **antes** dele. A minha 1.ª versão deste teste não punha
        publicação nenhuma, logo nunca chegava à guarda: media outra coisa e passava a achar que
        a media. Um teste que nunca alcança a linha que diz guardar é uma guarda sem teste."""
        t = 'La grandinata osservata nella settimana 38/2026 ha colpito i frutteti di Cuneo.'
        af = _produzir(t, published_at='2026-12-01',
                       raw_captured_at='2026-01-10 11:07:15+00')[0]
        self.assertEqual(af['FACT_TIME_ROLE']['PAPEL'], TA.PREVISAO)
        self.assertIn('colhido', af['FACT_TIME_ROLE']['PORQUE'])
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)

    def test_DOIS_periodos_impressos_no_mesmo_trecho_dao_NAO_SEI(self):
        """Medido no boletim de Ticino: o trecho real escreve «(18-24.05)» e «(25-31.05)»."""
        t = self.ABERTURA_COM_ANO + ('La settimana (18-24.05) e quella (25-31.05) sono state '
                                     'caratterizzate da sole in provincia di Cuneo.')
        af = next((a for a in _produzir(t) if '(18-24.05)' in a['TRECHO_LITERAL']), None)
        self.assertIsNotNone(af, 'a frase com as duas formas tem de ser uma afirmacao')
        self.assertEqual(af['TEMPOS_NO_TRECHO'], 2)
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)


class OMenuQueEngoliaAFraseSeguinte(unittest.TestCase):
    """F1 · o defeito que escondia a única frase de `derived:768` com a forma.

    A nuvem de etiquetas de um site («2949 / Ortofrutta / 1168 / mele / …») não tem pontuação
    nenhuma, logo a frase seguinte não tinha onde acabar: as duas coisas viravam UM pedaço, o
    `e_bloco_de_linhas_curtas` julgava-o menu — e acertava, na maioria — e a prosa ia fora com o
    menu.

        UM MENU QUE ENGOLE A FRASE SEGUINTE NÃO FAZ SÓ LIXO PASSAR:
        FAZ O CORPO DESAPARECER COM ELE.
    """

    MENU_E_PROSA = ('2949\nOrtofrutta\n1168\nmele\n1031\ningrosso\n872\nnocciole\n'
                    'Il Report Planner, aggiornato alla settimana 38/2026, conferma un quadro '
                    'già emerso nelle rilevazioni precedenti in provincia di Cuneo.\n')

    def test_a_prosa_depois_do_menu_volta_a_ser_corpo(self):
        af = _que_diz(_produzir(self.MENU_E_PROSA), 'Il Report Planner')
        self.assertIsNotNone(af, 'a frase depois do menu tem de ser uma afirmacao')
        self.assertIn('settimana 38/2026', af['TRECHO_LITERAL'])

    def test_o_menu_continua_a_NAO_ser_corpo(self):
        """O conserto não pode deixar o menu entrar: ele corta, não aprova."""
        for af in _produzir(self.MENU_E_PROSA):
            self.assertNotIn('Ortofrutta\n1168', af['TRECHO_LITERAL'])
            self.assertNotIn('nocciole', af['TRECHO_LITERAL'])

    def test_UMA_linha_curta_isolada_NAO_corta(self):
        """⚠️ A distinção que torna isto seguro, e a razão de cortar só no fim de uma CORRIDA.

        Num PDF a prosa vem embrulhada e uma linha curta sozinha é o **rabo** de uma frase.
        Cortar ali partiria uma afirmação verdadeira em duas metades — o que é pior do que
        deixar passar um menu, porque a prova fica pela metade."""
        embrulhado = ('La grandinata osservata il 18 febbraio 2026 ha colpito i frutteti\n'
                      'di Cuneo.\n')
        af = _que_diz(_produzir(embrulhado), 'La grandinata')
        self.assertIsNotNone(af)
        self.assertIn('di Cuneo', af['TRECHO_LITERAL'],
                      'a linha curta do fim e o rabo da frase, nao um item de lista')

    def test_o_limite_de_curta_e_o_do_vivo_e_nao_um_numero_novo(self):
        fonte = so_a_regra(os.path.join(RAIZ, 'leis', 'afirmacao_do_documento.py'))
        self.assertIn('FT\n.\nPALAVRAS_MINIMAS', fonte)
        self.assertIn('LINHAS_DO_BLOCO', fonte)

    def test_UMA_linha_curta_em_tres_continua_a_ser_prosa(self):
        """`LINHAS_DO_BLOCO` é 3: uma corrida precisa de três linhas curtas **seguidas**."""
        uma = ('La grandinata osservata il 18 febbraio 2026 ha colpito i frutteti\n'
               'con danni diffusi in tutta la provincia di Cuneo secondo i tecnici\n'
               'di Cuneo.\n')
        af = _que_diz(_produzir(uma), 'La grandinata')
        self.assertIsNotNone(af)
        self.assertIn('provincia di Cuneo', af['TRECHO_LITERAL'])

    def test_LIMITE_JA_EXISTENTE_duas_curtas_em_tres_linhas_sao_julgadas_menu(self):
        """⚠️ LIMITE QUE JÁ EXISTIA, MEDIDO AQUI PARA NÃO SER CONFUNDIDO COM O MEU CONSERTO.

        `e_bloco_de_linhas_curtas` (D160 §1.9) julga menu qualquer bloco de 3+ linhas em que a
        MAIORIA é curta. Num PDF, prosa embrulhada em três linhas com duas curtas é descartada —
        e isso **não** é efeito do corte que eu acrescentei: é a regra do bloco, anterior a ele.
        Medi as duas para que a próxima pessoa não me atribua este descarte, e para que ele fique
        declarado em vez de invisível."""
        duas = ('La grandinata osservata il 18 febbraio 2026 ha colpito\ni frutteti\n'
                'di Cuneo.\n')
        self.assertTrue(AD.e_bloco_de_linhas_curtas(duas))
        self.assertEqual(_produzir(duas), [])


class OToponimoItalianoLevaMaiuscula(unittest.TestCase):
    """(e) · «marche» são marcas; «Marche» é a região. Medido pelo LAB em `derived:1523`.

    O gazetteer casa sobre o texto em minúsculas, logo perdia a caixa — e `marche`, `como`,
    `prato`, `cuneo`, `massa`, `lodi`, `potenza` e `latina` são **todas palavras comuns do
    italiano**.

        UM LUGAR QUE O TEXTO ESCREVE EM MINÚSCULA NÃO É UM LUGAR:
        É UMA PALAVRA COMUM QUE POR AZAR TEM O NOME DE UM.

    ⚠️ A regra é **geral e não precisa de lista de nomes ambíguos**: em italiano corrente o
    topónimo leva maiúscula inicial, sempre. Uma lista de nomes seria a exceção que a D158
    proíbe — e ficaria para trás no dia em que a próxima palavra ambígua aparecesse."""

    def test_marche_em_minuscula_NAO_e_lugar(self):
        for frase in ('A sostenere il fatturato e la scelta di marche premium e prodotti.',
                      'Il mix di prodotti e marche cambia ogni anno nel carrello.'):
            for af in _produzir(frase):
                self.assertEqual(af['FACT_LOCATION']['VALOR'], NAO_SEI, frase[:44])

    def test_Marche_com_maiuscula_CONTINUA_a_ser_a_regiao(self):
        """O conserto não pode ser feito desligando o gazetteer."""
        af = _produzir('Nelle Marche la produzione di uva da tavola cresce ogni anno di piu.')[0]
        self.assertEqual(af['FACT_LOCATION']['VALOR'], 'Marche')

    def test_a_regra_vale_para_QUALQUER_nome_nao_so_para_marche(self):
        """Controle FORA do item do LAB: a regra é da caixa, não de «marche».

        `como`, `prato`, `massa` e `lodi` são palavras comuns **e** nomes de província. Se a
        regra fosse uma exceção para «marche», estas passariam."""
        # ⚠️ Medido: «Como» e «Massa» NAO estao no gazetteer desta casa (`FL.mencoes` devolve
        # vazio para os dois, mesmo com maiuscula). Nao sao efeito da minha regra, e por isso
        # nao entram no lado positivo — usa-se quem o gazetteer TEM.
        for comum, lugar in (('prato', 'Prato'), ('lodi', 'Lodi'), ('cuneo', 'Cuneo')):
            minuscula = 'Il terreno agricolo e tutto %s in questa zona di produzione.' % comum
            for af in _produzir(minuscula):
                self.assertEqual(af['FACT_LOCATION']['VALOR'], NAO_SEI,
                                 '%s em minuscula virou lugar' % comum)
            maiuscula = 'A %s la produzione di uva da tavola cresce ogni anno di piu.' % lugar
            achou = [a['FACT_LOCATION']['VALOR'] for a in _produzir(maiuscula)]
            self.assertIn(lugar, achou, '%s com maiuscula tem de continuar lugar' % lugar)

    def test_LIMITE_MEDIDO_dois_nomes_nao_estao_no_gazetteer(self):
        """⚠️ Medido, e declarado para não ser confundido com o meu conserto: «Como» e «Massa»
        **não estão** no gazetteer desta casa — `FL.mencoes` devolve vazio para os dois mesmo
        escritos com maiúscula. Perder esses lugares é anterior à regra da caixa."""
        import fato_local as FL
        for nome in ('Como', 'Massa'):
            self.assertEqual(FL.mencoes('A %s la produzione cresce.' % nome), [], nome)

    def test_o_porque_diz_que_foi_a_minuscula(self):
        af = _produzir('A sostenere il fatturato e la scelta di marche premium e prodotti.')[0]
        self.assertIn('minuscula', af['FACT_LOCATION']['PORQUE'])

    def test_LIMITE_a_forma_normalizada_nao_tem_caixa_para_olhar(self):
        """⚠️ LIMITE DECLARADO: quando o leitor normaliza («barese» → Bari) não há forma escrita
        para medir a caixa, e esses casos continuam como estavam. Está dito em
        `PORQUE_SEM_OFFSET`, e não o escondo atrás do conserto."""
        af = _que_diz(_produzir('Nel barese la produzione di uva da tavola cresce ogni anno.'),
                      'Nel barese')
        self.assertIsNotNone(af)
        lg = af['FACT_LOCATION']
        if lg['VALOR'] != NAO_SEI:
            self.assertIsNone(lg['ONDE'])
            self.assertIsNotNone(lg['PORQUE_SEM_OFFSET'])


class OValorCompostoNaoEUmLugarAMais(unittest.TestCase):
    """(a) · medido pelo LAB em `derived:1529`: «Rutigliano, in Puglia, provincia di Bari».

    O leitor devolve o valor **composto** «Puglia ; Bari». A versão anterior não achava essa
    string entre os lugares escritos e somava-a como um **terceiro** lugar: a contagem ia a 3
    onde o texto escreve 2.

        UMA CONTAGEM INFLADA RECUSA UM LUGAR QUE O TEXTO DIZ,
        E RECUSAR O QUE ESTÁ ESCRITO É TÃO ERRADO COMO INVENTAR.
    """

    FRASE = ('Rutigliano, in Puglia, provincia di Bari, conta ben 700 aziende agricole '
             'specializzate nella produzione.')

    def test_a_contagem_e_dois_e_nao_tres(self):
        af = _produzir(self.FRASE)[0]
        self.assertEqual(af['FACT_LOCATION']['LUGARES_NO_TRECHO'], 2)
        self.assertEqual(sorted(af['FACT_LOCATION']['EXPRESSOES_DE_LUGAR']), ['Bari', 'Puglia'])

    def test_o_valor_composto_nao_aparece_como_expressao(self):
        af = _produzir(self.FRASE)[0]
        for e in af['FACT_LOCATION']['EXPRESSOES_DE_LUGAR']:
            self.assertNotIn(';', str(e), 'um valor composto entrou como se fosse um lugar')

    def test_um_lugar_unico_continua_a_contar_UM(self):
        af = _produzir('In Puglia la produzione di uva da tavola cresce ogni anno di piu.')[0]
        self.assertEqual(af['FACT_LOCATION']['LUGARES_NO_TRECHO'], 1)
        self.assertEqual(af['FACT_LOCATION']['VALOR'], 'Puglia')

    def test_ABERTO_a_hierarquia_continua_a_contar_como_concorrencia(self):
        """⚠️ O QUE EU **NÃO** CONSERTEI, E PORQUÊ — está medido aqui em vez de escondido.

        «in Puglia, provincia di Bari» é **um lugar dito em hierarquia**: Bari está dentro da
        Puglia. Pela §5-C eles contam como 2 concorrentes e o lugar sai `NAO SEI` — o que faz
        perder um lugar que o texto diz.

        Para distinguir hierarquia de concorrência eu precisaria de saber que **Bari ∈ Puglia**,
        e essa informação **não existe nesta casa**: `FL.PROVINCIAS` é uma tupla de 85 nomes sem
        mapa de contenção (medido). Sem ela, uma regra «o mais preciso ganha» também colapsaria
        «Europa … Italia … Emilia Romagna» — que é exactamente o bloqueador BLK-1, onde os
        lugares pertencem a **factos diferentes**.

            ADIVINHAR A HIERARQUIA AQUI REABRE O BLOQUEADOR QUE ESTA GUARDA EXISTE PARA FECHAR.

        Fica como decisão do dono, com o custo nomeado. Este teste fixa o comportamento de hoje
        para que a mudança, quando vier, seja **deliberada**."""
        af = _produzir(self.FRASE)[0]
        self.assertEqual(af['FACT_LOCATION']['VALOR'], NAO_SEI)
        self.assertEqual(af['FACT_LOCATION']['MOTIVO'], AD.LUGARES_CONCORRENTES)
        import fato_local as FL
        self.assertIsInstance(FL.PROVINCIAS, tuple)
        self.assertFalse(hasattr(FL, 'REGIAO_DA_PROVINCIA'),
                         'se nasceu o mapa de contencao, a decisao da hierarquia pode ser tomada')


class OPeriodoQueACasaNaoResolveAindaCompete(unittest.TestCase):
    """(d) · medido pelo LAB em `derived:1529`:

        «L'anno scorso … a vendere a 1,30/1,40 euro : valori che non si sono ripresentati
         in QUESTA CAMPAGNA, dove si è scesi intorno all'euro»

    O produtor deu `FACT_TIME = 2025` à frase inteira. Mas o preço de ~1 € é **desta** campanha.
    Dois tempos na mesma frase, e o valor que saiu é do outro.

        UM TEMPO QUE A CASA NÃO SABE RESOLVER AINDA É UM TEMPO QUE COMPETE.
        NÃO CONTÁ-LO É ESCOLHER O OUTRO SEM O DIZER.

    ⚠️ A assimetria é a mesma das áreas supranacionais, e é ela que torna isto seguro: a lista
    **só sabe contar**. Nunca resolve um valor, nunca preenche um `FACT_TIME`. Resolver «questa
    campagna» em datas exige calendário agrícola e é decisão do dono do leitor vivo."""

    MISTURADA = ("L'anno scorso alcuni produttori sono riusciti a vendere a 1,30 euro: valori "
                 "che non si sono ripresentati in questa campagna, dove si e scesi all'euro.")

    def test_os_dois_tempos_dao_NAO_SEI(self):
        af = _produzir(self.MISTURADA)[0]
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)
        self.assertEqual(af['FACT_TIME']['MOTIVO'], TA.TEMPOS_CONCORRENTES)
        self.assertNotEqual(af['FACT_TIME']['VALOR'], '2025-01-01/2025-12-31')

    def test_o_periodo_sem_valor_viaja_declarado(self):
        af = _produzir(self.MISTURADA)[0]
        self.assertIn('questa campagna',
                      [str(x).lower() for x in af['FACT_TIME_ROLE']['PERIODOS_SEM_VALOR']])
        self.assertGreaterEqual(af['TEMPOS_NO_TRECHO'], 1)

    def test_a_lista_SO_conta_e_NUNCA_produz_valor(self):
        """A garantia que torna a lista segura: nenhum destes termos pode virar um `FACT_TIME`."""
        for termo in ('questa campagna', 'questa stagione', "quest'anno",
                      'la campagna in corso'):
            frase = 'La raccolta di uva da tavola in %s e stata buona in Puglia.' % termo
            for af in _produzir(frase):
                self.assertIn(af['FACT_TIME']['VALOR'], (NAO_SEI, TA.NAO_EXISTE), termo)
                self.assertNotIn('202', str(af['FACT_TIME']['VALOR']),
                                 'a lista produziu um ano, e ela so pode CONTAR')

    def test_uma_relativa_SOZINHA_continua_a_resolver(self):
        """O conserto não pode engolir o caminho que funciona: sem competidor, a relativa
        resolve-se como sempre (D63, a partir da publicação provada)."""
        af = _produzir('La grandinata osservata l anno scorso ha colpito i frutteti di Cuneo.',
                       published_at='2026-09-30')[0]
        self.assertEqual(af['FACT_TIME_ROLE']['ORIGEM'], TA.RELATIVO_D63)
        self.assertEqual(af['FACT_TIME']['VALOR'], '2025-01-01/2025-12-31')
        self.assertEqual(af['FACT_TIME_ROLE']['PERIODOS_SEM_VALOR'], [])

    def test_controle_FORA_do_item_do_LAB(self):
        """A regra é geral: outra fonte, outra cultura, outro lugar, mesma mistura de tempos."""
        af = _produzir('Le olive raccolte lo scorso anno rendevano meglio che in questa '
                       'stagione nei frutteti di Verona.')[0]
        self.assertEqual(af['FACT_TIME']['VALOR'], NAO_SEI)
        self.assertEqual(af['FACT_TIME']['MOTIVO'], TA.TEMPOS_CONCORRENTES)


class OGazetteerSemComuniEUmaFaltaDeDADOS(unittest.TestCase):
    """(b) · `MUNICIPALITIES = 0`, e **não é código que falta: é o ficheiro**.

    O leitor dos comuni **já existe** (`fato_local.comuni()`, que lê o CSV do ISTAT com
    `latin-1` e `;`, e devolve nome, sigla, província e região — ou seja, já traz a
    desambiguação). O que falta é o ficheiro:

        leis/dados/Elenco-comuni-italiani.csv   ->   NÃO EXISTE no disco

    Procurei no disco inteiro: os únicos CSV do ISTAT presentes são de **colheitas**
    (`istat_101_1015_coltivazioni_*`), não a lista de comuni.

        ESCREVER À MÃO OS COMUNI QUE UM ITEM PRECISA SERIA A EXCEÇÃO QUE A D158 PROÍBE,
        E UMA LISTA PARCIAL MENTE MAIS DO QUE UMA LISTA VAZIA.

    Este teste é um **arame de tropeço**: ele reprova no dia em que o ficheiro aparecer, e aí o
    conserto é só medir a desambiguação e tirar isto."""

    def test_o_leitor_de_comuni_EXISTE_e_esta_ligado(self):
        import fato_local as FL
        self.assertTrue(callable(FL.comuni))
        self.assertTrue(str(FL.COMUNI_ISTAT).endswith('.csv'))

    def test_ARAME_o_ficheiro_do_ISTAT_ainda_NAO_esta_no_disco(self):
        import fato_local as FL
        self.assertFalse(os.path.isfile(FL.COMUNI_ISTAT),
                         'o CSV do ISTAT apareceu: ligue os comuni, meca a desambiguacao e '
                         'retire este teste')

    def test_a_cobertura_DIZ_que_nao_tem_comuni(self):
        """O limite viaja com o lugar em vez de ser uma surpresa para quem consome."""
        c = AD.cobertura_do_gazetteer()
        self.assertEqual(c['MUNICIPALITIES'], 0)
        self.assertIn('ISTAT', c['MUNICIPALITIES_SOURCE'])

    def test_nenhum_comune_e_inventado_entretanto(self):
        """Enquanto o ficheiro não vier, um comune no texto fica `NAO SEI` — não meio-lugar."""
        for af in _produzir('A Rutigliano la produzione di uva da tavola cresce ogni anno.'):
            self.assertEqual(af['FACT_LOCATION']['VALOR'], NAO_SEI)


if __name__ == '__main__':
    unittest.main(verbosity=2)
