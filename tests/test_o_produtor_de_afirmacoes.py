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


if __name__ == '__main__':
    unittest.main(verbosity=2)
