#!/usr/bin/env python3
"""
Provas de que o NÚMERO PUBLICADO é o NÚMERO DERIVADO.

`tests/test_canonico.py` compara documentos entre si. Este compara documento contra
**dono**: `scripts/metricas_canonicas.py` deriva o valor da evidência, e cada documento
que publica aquele número tem de publicar exatamente esse valor.

O que isto impede, e já aconteceu três vezes: a suíte crescer de 25 para 91 provas e três
documentos continuarem dizendo 25; o atlas ir a 35 SOURCE_IDs e dois documentos ficarem em
31; a amostra cega dar 62,2%/77,8% e um documento publicar 62,5%/77,4%.

**Documento histórico não entra aqui.** Uma frase como *"na MISSÃO 06 havia 37 provas"* é
registro, não afirmação corrente — e reescrevê-la seria apagar a história. Os arquivos
listados em `HISTORICOS` são poupados.
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from metricas_canonicas import build, Ledger                    # noqa: E402

DOCS = os.path.join(ROOT, 'docs')

# Documentos que registram o passado. Um número antigo neles é evidência, não erro.
HISTORICOS = {
    'descoberta/FREEZE-DA-BASE-DO-PILOTO.md',
    'decisoes/DIARIO-DE-DECISOES.md',
    'descoberta/MISSAO-EAME-01.md',
    'descoberta/SEGUNDA-PASSAGEM-E-PRIORIZACAO.md',
    'descoberta/LACUNAS-E-VEREDITO-MISSAO-03.md',
    'operacao/PROVA-DE-RECORRENCIA-MISSAO-08.md',
}


def br(v):
    """Formata como os documentos escrevem: milhar com ponto, decimal com vírgula.

    Preserva a precisão que o dono guardou — 1,17 não pode virar 1,2 no caminho, senão
    o teste passa a exigir do documento um número que a evidência não tem.
    """
    if isinstance(v, float):
        return ('%g' % v).replace('.', ',')
    return f'{v:,}'.replace(',', '.')


# METRIC_ID -> documentos que publicam aquele número como afirmação CORRENTE
BINDINGS = {
    'TEST_COUNT_CURRENT': ['piloto/O-QUE-PODEMOS-DIZER.md',
                           'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md',
                           'apresentacao/PILOTO-CLASSIFICACAO.md',
                           'ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md'],
    'SOURCE_ID_COUNT': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md',
                        'piloto/SOURCE-PACK-PILOTO.md',
                        'apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md',
                        'apresentacao/MATRIZ-DE-PROVA-EAME.md'],
    'PILOT_SOURCE_COUNT': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md',
                           'piloto/SOURCE-PACK-PILOTO.md'],
    'CRITICAL_SOURCE_COUNT': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md',
                              'piloto/SOURCE-PACK-PILOTO.md'],
    'X006_USE_COVERAGE': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md',
                          'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md',
                          'apresentacao/PILOTO-CLASSIFICACAO.md',
                          'apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md'],
    'X006_BLIND_SPELLING': ['apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md'],
    'X006_BLIND_USE': ['apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md'],
    'X007_USE_COVERAGE': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md',
                          'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md',
                          'apresentacao/PILOTO-CLASSIFICACAO.md'],
    'ES_ROPF_TOTAL': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md'],
    'ES_ROPF_ACTIVE': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md'],
    'ES_ADAMA_ACTIVE': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md'],
    'ASK_QUESTION_COUNT': ['piloto/ASK-SINTONIA-BENCHMARK.md',
                           'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md',
                           'piloto/ENTRADA-PARA-CLAUDE-DESIGN.md'],
    'ASK_ANSWERABLE': ['piloto/ASK-SINTONIA-BENCHMARK.md',
                       'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md'],
    'ASK_REFUSAL': ['piloto/ASK-SINTONIA-BENCHMARK.md',
                    'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md'],
    'RAIF_HUELVA_COHORT_2023': ['apresentacao/CASOS-PARA-APRESENTACAO.md'],
    'RAIF_HUELVA_COHORT_2026': ['apresentacao/CASOS-PARA-APRESENTACAO.md'],
    'RAIF_CADIZ_COHORT_2026': ['apresentacao/CASOS-PARA-APRESENTACAO.md'],
    'RAIF_SEASONS_AVAILABLE': ['apresentacao/CASOS-PARA-APRESENTACAO.md'],
}


class TestDocumentoBateComODono(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.L = build()
        cls.cache = {}

    def doc(self, rel):
        if rel not in self.cache:
            with open(os.path.join(DOCS, rel), encoding='utf-8') as f:
                self.cache[rel] = f.read()
        return self.cache[rel]

    def test_todo_numero_publicado_vem_do_dono(self):
        for metric, docs in BINDINGS.items():
            valor = self.L[metric]['VALUE']
            alvo = br(valor)
            for rel in docs:
                with self.subTest(metrica=metric, documento=rel, valor=alvo):
                    self.assertNotIn(rel, HISTORICOS,
                                     'documento histórico não deve ser amarrado a valor corrente')
                    self.assertIn(alvo, self.doc(rel),
                                  f'{rel} não publica {metric} = {alvo} '
                                  f'(dono: {self.L[metric]["SOURCE"]})')

    def test_o_ledger_declara_dono_e_derivacao_para_toda_metrica(self):
        for mid, m in self.L.items():
            with self.subTest(metrica=mid):
                for campo in ('VALUE', 'UNIT', 'SOURCE', 'DERIVATION'):
                    self.assertIsNotNone(m[campo], f'{mid} sem {campo}')
                self.assertTrue(m['DERIVATION'].strip(), f'{mid} com derivação vazia')

    def test_metricas_espanholas_carregam_data_de_referencia(self):
        """Contagem de janela sem data de referência é número sem validade declarada."""
        for mid, m in self.L.items():
            if mid.startswith('ES_'):
                with self.subTest(metrica=mid):
                    self.assertEqual(m['REFERENCE_DATE'], '2026-08-29')

    def test_o_placar_da_matriz_de_prova_bate_com_a_propria_lista(self):
        matriz = self.doc('apresentacao/MATRIZ-DE-PROVA-EAME.md')
        for estado, mid in (('PROVED', 'DECK_PROVED'), ('PARTIAL', 'DECK_PARTIAL'),
                            ('UNPROVED', 'DECK_UNPROVED'),
                            ('NOT TESTABLE YET', 'DECK_NOT_TESTABLE')):
            linha = next((l for l in matriz.split('\n')
                          if l.startswith(f'| **{estado}**')), None)
            with self.subTest(estado=estado):
                self.assertIsNotNone(linha, f'linha {estado} sumiu do placar')
                declarado = int(re.sub(r'\D', '', linha.split('|')[2]))
                self.assertEqual(declarado, self.L[mid]['VALUE'],
                                 f'{estado}: o placar diz {declarado} e a lista ao lado '
                                 f'tem {self.L[mid]["VALUE"]} claims')

    def test_es_t4_005_esta_no_resumo_de_fontes_criticas(self):
        """A ficha marca CRITICAL; o resumo tem de listar a mesma coisa."""
        pack = self.doc('piloto/SOURCE-PACK-PILOTO.md')
        resumo = next((l for l in pack.split('\n') if l.startswith('**5 CRITICAL')
                       or re.match(r'\*\*\d+ CRITICAL', l)), '')
        for sid in self.L['CRITICAL_SOURCE_IDS']['VALUE']:
            with self.subTest(fonte=sid):
                self.assertIn(sid, resumo,
                              f'{sid} é CRITICAL na ficha e não aparece no resumo')

    def test_documentos_historicos_nao_sao_reescritos(self):
        """O passado fica. Estes documentos precisam continuar dizendo o que diziam."""
        freeze = self.doc('descoberta/FREEZE-DA-BASE-DO-PILOTO.md')
        self.assertIn('43', freeze, 'o total de provas da v1 sumiu do congelamento')
        self.assertIn('37/37', freeze, 'a reconciliação 37 vs 38 sumiu')



class TestNumeroCorrenteTemDono(unittest.TestCase):
    """MISSAO 10C — o numero publicado num documento CORRENTE nao pode ficar sem dono.

    Dois defeitos medidos, a mesma classe:
      · o handoff publicava "26 fichas" e o dono derivava 25. Passou porque `--sync` so
        andava por `docs/` e o handoff mora na RAIZ;
      · a porta canonica (`ARQUITETURA-DE-PRODUTO-ATUAL.md`) — o documento que vence
        qualquer conflito — carregava 486, 1.004, 36, 61 e 34 sem marcador nenhum.
        Estavam certos naquele dia; nada os impediria de envelhecer em silencio.
    """

    def test_nenhum_marcador_esta_desatualizado(self):
        """O teste reprova, o `--sync` conserta. Sem isto o marcador e decorativo."""
        from metricas_canonicas import sync
        fora = sync(check_only=True)
        self.assertEqual([], fora,
                         'documento publica valor diferente do dono: %s — '
                         'rode python3 scripts/metricas_canonicas.py --sync' % fora)

    def test_o_sync_alcanca_os_documentos_da_raiz(self):
        """O handoff mora na raiz. Enquanto o sync so via docs/, ele nao tinha dono."""
        from metricas_canonicas import documentos_com_numero
        alcancados = {os.path.basename(d) for d in documentos_com_numero()}
        self.assertIn('HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md', alcancados)

    def test_a_porta_canonica_amarra_seus_numeros_ao_dono(self):
        with open(os.path.join(DOCS, 'piloto', 'ARQUITETURA-DE-PRODUTO-ATUAL.md'),
                  encoding='utf-8') as f:
            porta = f.read()
        for mid in ('ES_EXPIRING_6M', 'ES_EXPIRING_12M', 'ES_ADAMA_EXPIRING_6M',
                    'ES_ADAMA_EXPIRING_12M', 'ES_ACTIVE_WITH_PAST_EXPIRY',
                    'X006_USE_COVERAGE', 'X007_USE_COVERAGE'):
            with self.subTest(metrica=mid):
                self.assertIn('<!--M:%s-->' % mid, porta,
                              'a porta que vence conflitos publica %s sem dono' % mid)

    def test_o_handoff_amarra_a_contagem_de_fontes_ao_dono(self):
        with open(os.path.join(ROOT, 'HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md'),
                  encoding='utf-8') as f:
            h = f.read()
        for mid in ('SOURCE_ID_COUNT', 'SOURCE_FICHA_COUNT', 'TEST_COUNT_CURRENT'):
            with self.subTest(metrica=mid):
                self.assertIn('<!--M:%s-->' % mid, h)

    def test_o_rotulo_do_benchmark_declara_o_tamanho_real(self):
        """Publicava "20 perguntas" com 35 no arquivo."""
        import json
        with open(os.path.join(ROOT, 'data', 'samples', 'ASK-SINTONIA-benchmark.json'),
                  encoding='utf-8') as f:
            b = json.load(f)
        rotulo = re.search(r'(\d+) perguntas', b['source'])
        self.assertIsNotNone(rotulo, 'o rotulo do benchmark nao declara tamanho')
        self.assertEqual(len(b['questions']), int(rotulo.group(1)),
                         'o rotulo do benchmark nao bate com o numero de perguntas')
        self.assertEqual(len(b['questions']), sum(b['totals'].values()) + b['wrong_answers'])


class TestAskSintoniaNaoSeVendeComoMedicao(unittest.TestCase):
    """§22 — 5 perguntas executam; 35 são contrato escrito à mão. Não confundir."""

    def test_o_documento_declara_a_diferenca(self):
        with open(os.path.join(DOCS, 'piloto', 'ASK-SINTONIA-BENCHMARK.md'),
                  encoding='utf-8') as f:
            doc = f.read()
        self.assertIn('LABELLED ACCEPTANCE CONTRACT', doc,
                      'o documento não declara que o veredito é escrito à mão')
        self.assertIn('EXECUTED ANSWER', doc)
        self.assertRegex(doc, r'(?i)o placar diz o que o sistema TEM DE fazer')

    def test_o_script_avisa_antes_de_imprimir_o_placar(self):
        with open(os.path.join(ROOT, 'scripts', 'ask_sintonia.py'), encoding='utf-8') as f:
            src = f.read()
        self.assertIn('CONTRATO DE ACEITAÇÃO', src)
        self.assertIn('veredito ESCRITO À MÃO', src)

    def test_as_perguntas_executadas_sao_cinco(self):
        with open(os.path.join(ROOT, 'scripts', 'ask_sintonia.py'), encoding='utf-8') as f:
            src = f.read()
        executadas = re.findall(r'^def (q\d+)\(\):', src, re.M)
        self.assertEqual(len(executadas), 5,
                         'mudou o número de perguntas realmente executadas — '
                         'o documento tem de mudar junto')


class TestV2Reconciliada(unittest.TestCase):
    """§1 — nenhum documento CORRENTE pode contradizer a V2. O histórico fica.

    Documentos históricos preservam o que se sabia; se um deles disser "11 safras",
    isso é registro. O que não pode é um documento corrente afirmar o número velho.
    """

    HISTORICOS = ('FREEZE-DA-BASE', 'DIARIO-DE-DECISOES', 'MISSAO-EAME-01',
                  'SEGUNDA-PASSAGEM', 'LACUNAS-E-VEREDITO',
                  'PROVA-DE-RECORRENCIA-MISSAO-08', 'PROTOCOLO-BENCHMARK')

    def correntes(self):
        for dp, _, fs in os.walk(DOCS):
            for f in fs:
                if f.endswith('.md') and not any(h in f for h in self.HISTORICOS):
                    p = os.path.join(dp, f)
                    with open(p, encoding='utf-8') as fh:
                        yield os.path.relpath(p, DOCS), fh.read()

    def test_nenhum_documento_corrente_afirma_11_safras(self):
        alvo = re.compile(r'(?i)\b11 safras\b')
        for rel, txt in self.correntes():
            for linha in (re.findall(r'^#{1,6} .*$', txt, re.M)
                          + re.findall(r'^\|.*$', txt, re.M)):
                if re.search(r'(?i)(era|antes|corrigid|MISSÃO 0[2-9]|retirad|histórico)', linha):
                    continue          # linha que registra a correção, não a afirma
                with self.subTest(documento=rel, linha=linha[:60]):
                    self.assertNotRegex(linha, alvo,
                                        'documento corrente ainda afirma 11 safras')

    def test_o_numero_de_safras_vem_do_dono(self):
        L = build()
        self.assertEqual(L['RAIF_SEASONS_AVAILABLE']['VALUE'], 23)
        with open(os.path.join(DOCS, 'apresentacao', 'CASOS-PARA-APRESENTACAO.md'),
                  encoding='utf-8') as f:
            casos = f.read()
        self.assertIn('23 safras', casos)
        self.assertIn('148.964', casos)

    def test_a_porta_unica_de_arquitetura_existe_e_e_apontada(self):
        porta = os.path.join(DOCS, 'piloto', 'ARQUITETURA-DE-PRODUTO-ATUAL.md')
        self.assertTrue(os.path.exists(porta))
        for rel in ('ferramentas/CATALOGO-DE-FERRAMENTAS-EAME.md',
                    'ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md',
                    'piloto/ENTRADA-PARA-CLAUDE-DESIGN.md'):
            with self.subTest(documento=rel):
                with open(os.path.join(DOCS, rel), encoding='utf-8') as f:
                    self.assertIn('ARQUITETURA-DE-PRODUTO-ATUAL', f.read(),
                                  'documento antigo não aponta para a porta única')

    def test_o_design_nao_pode_prometer_previsao(self):
        with open(os.path.join(DOCS, 'piloto', 'ARQUITETURA-DE-PRODUTO-ATUAL.md'),
                  encoding='utf-8') as f:
            arq = f.read()
        self.assertRegex(arq, r'(?i)predictive early warning',
                         'a proibição de vender previsão sumiu do handoff')
        self.assertRegex(arq, r'(?i)RELATIVE EXPOSURE INDEX|índice de exposição relativa')
        self.assertIn('ACTIVATION QUESTION', arq)


class TestPercentualNaoSaiSemDenominador(unittest.TestCase):
    """Percentual publicado sem dizer "de quantos" e o defeito que este arquivo existe
    para impedir — e ele estava passando.

    Medido em 2026-08-29: das 63 metricas do ledger, 26 saiam com DENOMINATOR=None, e
    DUAS eram percentuais publicados (X006_USE_COVERAGE = 82,1 e X006_BLIND_USE = 77,8).
    O contrato geral nao pegava porque `test_o_ledger_declara_dono_e_derivacao_para_toda_metrica`
    percorre so ('VALUE','UNIT','SOURCE','DERIVATION') — DENOMINATOR estava de fora.

    NOT_PRESERVED e resposta valida: o total de usos nunca foi gravado em X-006. O que
    nao e valido e o None calado, porque ele nao distingue "nao guardamos" de
    "esquecemos de declarar".
    """

    @classmethod
    def setUpClass(cls):
        cls.L = build()

    def test_toda_metrica_percentual_declara_denominador(self):
        for mid, m in self.L.items():
            if m.get('UNIT') != 'pct':
                continue
            with self.subTest(metrica=mid):
                d = m.get('DENOMINATOR')
                self.assertIsNotNone(d, f'{mid} publica {m["VALUE"]}% sem denominador')
                self.assertNotEqual('', d, f'{mid} com denominador vazio')

    def test_denominador_ausente_diz_por_que_na_derivacao(self):
        """NOT_PRESERVED sem explicacao e so um None com nome melhor."""
        for mid, m in self.L.items():
            if m.get('DENOMINATOR') != Ledger.DENOMINADOR_NAO_PRESERVADO:
                continue
            with self.subTest(metrica=mid):
                self.assertIn('nao foi preservado', m.get('DERIVATION', ''),
                              f'{mid} declara NOT_PRESERVED sem dizer o que faltou')

    def test_o_marcador_existe_e_e_unico(self):
        self.assertEqual('NOT_PRESERVED',
                         Ledger.DENOMINADOR_NAO_PRESERVADO)
