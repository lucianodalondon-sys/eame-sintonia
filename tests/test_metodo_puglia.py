#!/usr/bin/env python3
"""MÉTODO PUGLIA (D112) — o gold humano do dono, medido contra a lei e contra o código.

O fixture `tests/fixtures/puglia/GOLD-FIXTURE-PUGLIA-V1.json` é dado REAL de
boletins públicos com as respostas HUMANAS do dono (D111). Nada aqui o altera:
o esperado é a régua, e o código é que se mede contra ele.

Três perguntas diferentes, e não se misturam:

    1. o gold está íntegro?             (trecho ↔ SPAN_SHA256, ficheiro selado)
    2. a LEI concorda com o dono?       (COL-LAW-032/221/222/223, INT-LAW-078/079)
    3. o CÓDIGO de hoje cumpre a lei?   (os extratores que existem — secção iv)

Onde o código atual contradiz o gold, o teste está marcado `expectedFailure`
com o motivo: é o BACKLOG MEDIDO, não uma falha escondida. Se um dia o código
passar a cumprir, o `expectedFailure` vira «unexpected success» e reprova — e
obriga quem consertou a tirar a marca, em vez de ela mentir ao contrário.

Sem rede. Sem modelo.
"""
import hashlib
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import lugar_do_fato as L                                          # noqa: E402
import afirmacao_da_fonte as A                                     # noqa: E402
import fato_local as IT                                            # noqa: E402
import fato_do_texto as FT                                         # noqa: E402

GOLD = os.path.join(RAIZ, 'tests', 'fixtures', 'puglia', 'GOLD-FIXTURE-PUGLIA-V1.json')
# O selo do ficheiro. Mudar uma resposta ou um esperado do dono sem decisão
# dele muda este número, e o teste reprova. Atualizar o selo é decisão do dono.
GOLD_SHA256 = 'c2554525a8f9512c41249f9aeab0e1657cc9709063cc1b9933eafb485c06ac40'
BIBLIA = os.path.join(RAIZ, 'BIBLIA-CANONICA-DA-COLETA.md')
BIBLIA_INT = os.path.join(RAIZ, 'BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md')


def _ler(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


GOLD_DADOS = json.loads(_ler(GOLD))
CASOS = {c['CASO']: c for c in GOLD_DADOS['CASOS']}


def lei(texto, lid):
    """O corpo de uma lei, do cabeçalho dela até ao próximo cabeçalho."""
    m = re.search(r'^## %s · .*?(?=^## |\Z)' % re.escape(lid), texto, re.M | re.S)
    return m.group(0) if m else ''


def fonte_do_lugar(esperado):
    """«VISUAL_HEADER_CANDIDATE (+ nota)» → «VISUAL_HEADER_CANDIDATE»."""
    return re.match(r'[A-Z_]+', esperado).group(0)


def fonte_da_entidade(valor):
    """«SPAN (pelo nome …)» / «SPAN/PARAGRAPH_CONTEXT» → a primeira etiqueta."""
    return re.match(r'[A-Z_]+', valor).group(0)


def chaves_no(texto, especie):
    """As chaves de superfície de uma espécie (PEST:…) que aparecem no texto."""
    baixo = texto.lower()
    return {k for n, k in A.NOMES_DE_SUPERFICIE.items() if n in baixo}


# ─────────────────────────────────────────────────────────────────────────────
class T1_OGoldEstaIntegro(unittest.TestCase):

    def test_o_ficheiro_esta_selado(self):
        with open(GOLD, 'rb') as f:
            self.assertEqual(GOLD_SHA256, hashlib.sha256(f.read()).hexdigest(),
                             'o gold humano mudou sem decisão do dono')

    def test_i_todo_trecho_bate_com_o_span_sha256(self):
        n = 0
        for c in GOLD_DADOS['CASOS']:
            for f in c['FICHAS']:
                n += 1
                self.assertEqual(f['SPAN_SHA256'],
                                 hashlib.sha256(f['TRECHO'].encode('utf-8')).hexdigest(),
                                 '%s %s: trecho não bate com o SHA' % (c['CASO'], f['ASSERTION_ID']))
        self.assertEqual(12, n, 'o gold tem 12 fichas em 10 casos')
        self.assertEqual(10, len(CASOS))


# ─────────────────────────────────────────────────────────────────────────────
class T2_OLugarDoFato(unittest.TestCase):
    """COL-LAW-032 · LOCATION_SOURCE."""

    def test_ii_cabecalho_so_na_imagem_da_unresolved(self):
        vistos = []
        for cid, c in CASOS.items():
            e = c['ESPERADO']
            if not e.get('LOCATION_SOURCE', '').startswith('VISUAL_HEADER_CANDIDATE'):
                continue
            vistos.append(cid)
            self.assertEqual('UNRESOLVED', e['FACT_LOCATION'], cid)
            cand = c['FICHAS'][0]['FICHA_GRAVADA']['FACT_LOCATION']['CANDIDATO_VISUAL']['ENTIDADE']
            valor, porque = L.fact_location('VISUAL_HEADER_CANDIDATE', cand)
            self.assertEqual(L.UNRESOLVED, valor,
                             '%s: o cabeçalho só-na-imagem virou FACT_LOCATION (%s)' % (cid, porque))
        self.assertEqual(['C01', 'C05', 'C06'], sorted(vistos))

    def test_a_lei_devolve_o_lugar_que_o_dono_esperava(self):
        n = 0
        for cid, c in CASOS.items():
            e = c['ESPERADO']
            if 'LOCATION_SOURCE' not in e:
                continue
            n += 1
            fonte = fonte_do_lugar(e['LOCATION_SOURCE'])
            gravada = c['FICHAS'][0]['FICHA_GRAVADA']['FACT_LOCATION']
            if fonte == 'VISUAL_HEADER_CANDIDATE':
                lugar = gravada['CANDIDATO_VISUAL']['ENTIDADE']
            elif e['FACT_LOCATION'] == 'UNRESOLVED':
                lugar = None          # C08: expressão sem lugar resolvido
            else:
                lugar = e['FACT_LOCATION']
            self.assertEqual(e['FACT_LOCATION'], L.fact_location(fonte, lugar)[0], cid)
        self.assertEqual(8, n)

    def test_expressao_territorial_nao_vira_ponto(self):
        e = CASOS['C08']['ESPERADO']
        self.assertEqual('TEXT', e['LOCATION_SOURCE'])
        self.assertFalse(e['PONTO_NO_MAPA'])
        self.assertEqual(L.UNRESOLVED, L.fact_location('TEXT', None)[0])
        self.assertIn(e['LOCATION_EXPRESSION_RAW'], CASOS['C08']['FICHAS'][0]['TRECHO'])

    def test_vocabulario_fora_nao_sustenta(self):
        self.assertEqual(L.UNRESOLVED, L.fact_location('DEDUZIDO_DO_LAYOUT', 'X')[0])
        self.assertEqual(L.UNRESOLVED, L.fact_location('UNRESOLVED', 'X')[0])

    def test_a_biblia_e_o_codigo_dizem_o_mesmo_vocabulario(self):
        corpo = lei(_ler(BIBLIA), 'COL-LAW-032')
        for v in L.LOCATION_SOURCES + ('LOCATION_EXPRESSION_RAW',):
            self.assertIn(v, corpo, 'COL-LAW-032 não nomeia %s' % v)
        self.assertEqual({'TEXT', 'SECTION_HEADER'}, set(L.LOCATION_SOURCES_QUE_SUSTENTAM_FATO))


# ─────────────────────────────────────────────────────────────────────────────
class T3_AProcedenciaDaEntidade(unittest.TestCase):
    """COL-LAW-221 · ENTITY_SOURCE."""

    def _pares(self):
        """(caso, ficha, espécie, ENTITY_SOURCE esperado) de todo o gold."""
        for cid, c in CASOS.items():
            e = c['ESPERADO']
            for especie in ('PEST', 'CROP'):
                k = especie + '_ENTITY_SOURCE'
                if k in e:
                    yield cid, c['FICHAS'][0], especie, fonte_da_entidade(e[k])
            if isinstance(e.get('ENTITY_SOURCE'), dict):
                for f in c['FICHAS']:
                    yield cid, f, 'PEST', e['ENTITY_SOURCE'][f['ASSERTION_ID']]

    def test_o_gold_obedece_a_lei(self):
        nomes = {'PEST': ("bactrocera oleae", "mosca dell'olivo", "mosca delle olive"),
                 'CROP': ('olivo', 'olive', 'oliv')}
        n = 0
        for cid, f, especie, fonte in self._pares():
            n += 1
            no_trecho = any(x in f['TRECHO'].lower() for x in nomes[especie])
            ok, porque = A.procedencia_da_entidade(fonte, nome_no_trecho=no_trecho)
            self.assertTrue(ok, '%s %s %s=%s: %s' % (cid, f['ASSERTION_ID'], especie, fonte, porque))
        self.assertEqual(9, n)

    def test_c04_entidade_concorrente_obriga_unknown(self):
        c = CASOS['C04']
        f = c['FICHAS'][0]
        self.assertEqual('UNKNOWN', c['ESPERADO']['PEST'])
        concorrentes = chaves_no(f['CONTEXTO_ANTES'], 'PEST')
        self.assertGreaterEqual(len(concorrentes), 2, concorrentes)
        self.assertTrue(A.procedencia_da_entidade('UNKNOWN', nome_no_trecho=False,
                                                  concorrente=True)[0])
        for herdada in ('PARAGRAPH_CONTEXT', 'SECTION_TITLE', 'DOCUMENT_TITLE'):
            self.assertFalse(A.procedencia_da_entidade(herdada, nome_no_trecho=False,
                                                       concorrente=True, troca_de_secao=True)[0],
                             '%s aceite com praga concorrente' % herdada)

    def test_span_sem_nome_no_trecho_reprova(self):
        # C02: a ficha gravada pôs PEST:DACUOL como se viesse do trecho.
        f = CASOS['C02']['FICHAS'][0]
        self.assertNotIn('oleae', f['TRECHO'].lower())
        self.assertFalse(A.procedencia_da_entidade('SPAN', nome_no_trecho=False)[0])

    def test_a_biblia_e_o_codigo_dizem_o_mesmo_vocabulario(self):
        corpo = lei(_ler(BIBLIA), 'COL-LAW-221')
        self.assertTrue(corpo, 'COL-LAW-221 não existe na Bíblia')
        for v in A.ENTITY_SOURCES:
            self.assertIn(v, corpo, 'COL-LAW-221 não nomeia %s' % v)
        self.assertEqual(('SPAN', 'PARAGRAPH_CONTEXT', 'SECTION_TITLE',
                          'DOCUMENT_TITLE', 'UNKNOWN'), A.ENTITY_SOURCES)


# ─────────────────────────────────────────────────────────────────────────────
class T4_AFidelidadeDaAfirmacao(unittest.TestCase):
    """COL-LAW-222 · o lint determinístico."""

    def _lint(self, cid, i=0):
        f = CASOS[cid]['FICHAS'][i]
        return A.fidelidade(f['TRECHO'], f['TRADUCAO_DA_FICHA_IA'], f['FICHA_GRAVADA'])

    def test_iii_reprova_c05_acrescenta_e_omite_entidade(self):
        r = self._lint('C05')
        self.assertFalse(r['FIEL'])
        self.assertFalse(CASOS['C05']['ESPERADO']['FICHA_FIEL'])
        self.assertTrue(any(e.startswith('ACRESCENTA_COLCHETE') for e in r['ERROS']), r)
        self.assertIn('OMITE_ENTIDADE: margaronia', r['ERROS'])

    def test_iii_reprova_c06_omite_a_excecao(self):
        r = self._lint('C06')
        self.assertFalse(r['FIEL'])
        self.assertFalse(CASOS['C06']['ESPERADO']['FICHA_FIEL'])
        self.assertTrue(any(e.startswith('OMITE_QUALIFICADOR_NA_TRADUCAO') for e in r['ERROS']), r)
        self.assertIn('OMITE_QUALIFICADOR_NA_FICHA', r['ERROS'])

    def test_iii_aprova_c02_c08_c10(self):
        for cid in ('C02', 'C08', 'C10'):
            for i in range(len(CASOS[cid]['FICHAS'])):
                r = self._lint(cid, i)
                self.assertTrue(r['FIEL'], '%s[%d]: %s' % (cid, i, r['ERROS']))

    def test_o_lint_concorda_com_o_q1_do_dono(self):
        n = 0
        for cid, c in CASOS.items():
            q1 = c['RESPOSTAS_DO_DONO'].get('Q1')
            if q1 not in ('SIM', 'NÃO'):
                continue
            for i in range(len(c['FICHAS'])):
                n += 1
                self.assertEqual(q1 == 'SIM', self._lint(cid, i)['FIEL'], cid)
        self.assertEqual(9, n)

    def test_a_biblia_diz_fonte_versus_interpretacao(self):
        corpo = lei(_ler(BIBLIA), 'COL-LAW-222')
        self.assertTrue(corpo, 'COL-LAW-222 não existe na Bíblia')
        for v in ('INTERPRETACAO_DO_SISTEMA', 'nunca evidência', 'leis/afirmacao_da_fonte.py'):
            self.assertIn(v, corpo)


# ─────────────────────────────────────────────────────────────────────────────
class T5_AEspecieDaAfirmacao(unittest.TestCase):
    """COL-LAW-223 · PREVISÃO ≠ FATO OBSERVADO ≠ RECOMENDAÇÃO."""

    def test_previsao_nao_prova_ocorrencia(self):
        e = CASOS['C03']['ESPERADO']
        self.assertEqual('PREVISAO', e['CLASSE'])
        self.assertFalse(e['USAVEL_COMO_FATO_OBSERVADO'])
        self.assertFalse(A.usavel_como_fato_observado('PREVISAO'))
        self.assertFalse(A.usavel_como_fato_observado('RECOMENDACAO'))
        self.assertTrue(A.usavel_como_fato_observado('FATO_OBSERVADO'))

    def test_a_biblia_separa_as_tres(self):
        corpo = lei(_ler(BIBLIA), 'COL-LAW-223')
        for v in A.ESPECIES_DA_AFIRMACAO:
            self.assertIn(v, corpo)


# ─────────────────────────────────────────────────────────────────────────────
class T6_AsRelacoes(unittest.TestCase):
    """INT-LAW-078 / INT-LAW-079 — da Intelligence."""

    @staticmethod
    def _af(f, territorio=None):
        g = f['FICHA_GRAVADA']
        return {'PUBLISHER': f['PUBLISHER'], 'SPAN_SHA256': f['SPAN_SHA256'],
                'TERRITORIO': territorio or g['FACT_LOCATION'].get('TEXTO'),
                'VALIDADE': (g['TIME']['WORLD_TIME'].get('VALIDADE_DO_BOLETIM') or {}).get('LITERAL'),
                'VALOR': g['OBJETO']}

    def test_c07_mesma_redacao_em_tres_territorios_e_uma_instituicao(self):
        e = CASOS['C07']['ESPERADO']
        f = CASOS['C07']['FICHAS'][0]
        # os três territórios nomeados pelo dono no comentário do C07
        terr = ['Collina Litoranea', 'Pianura Salentina Nord', 'Pianura Salentina Sud']
        for t in terr:
            self.assertIn(t, CASOS['C07']['COMENTARIO_DO_DONO'])
        apl = [self._af(f, t) for t in terr]
        for x in apl[1:]:
            r = A.relacao(apl[0], x)
            self.assertEqual('SAME_CLAIM_TERRITORIAL_APPLICATION', r['RELATION'])
            self.assertEqual(e['INSTITUICOES_INDEPENDENTES'], r['INSTITUICOES_INDEPENDENTES'])
        self.assertEqual(e['APLICACOES_TERRITORIAIS'], len(apl))

    def test_c09_limites_diferentes_sao_divergencia_nao_resolvida(self):
        e = CASOS['C09']['ESPERADO']
        a, b = (self._af(f) for f in CASOS['C09']['FICHAS'])
        r = A.relacao(a, b)
        self.assertEqual(e['RELATION'], r['RELATION'])
        self.assertEqual(e['CONTRADICTION_STATUS'], r['CONTRADICTION_STATUS'])

    def test_c10_mudanca_temporal_nao_e_contradicao_nem_prova_de_campo(self):
        e = CASOS['C10']['ESPERADO']
        a, b = (self._af(f) for f in CASOS['C10']['FICHAS'])
        r = A.relacao(a, b)
        self.assertEqual(e['RELATION'], r['RELATION'])
        self.assertEqual(e['CONTRADICTION'], r['CONTRADICTION_STATUS'] != 'NO')
        self.assertEqual(e['CONCLUIR_MUDANCA_DO_CAMPO'], r['CONCLUIR_MUDANCA_DO_CAMPO'])

    def test_a_biblia_da_intelligence_tem_as_duas_leis(self):
        t = _ler(BIBLIA_INT)
        for lid in ('INT-LAW-078', 'INT-LAW-079'):
            self.assertRegex(t, r'(?m)^## %s — ' % lid)
        for v in ('DIVERGENT_RECOMMENDATIONS', 'TEMPORAL_CHANGE_IN_RECOMMENDATION',
                  'CONTRADICTION_STATUS = UNRESOLVED'):
            self.assertIn(v, t)
        self.assertIn('INT-LAW-078', _ler(BIBLIA), 'a Coleta não aponta para a Intelligence')


# ─────────────────────────────────────────────────────────────────────────────
# (iv) O CÓDIGO DE HOJE contra o gold. Os extratores de lugar que existem são
# `leis/fato_local.py` (leitor italiano) e `leis/fato_do_texto.py` (tempo e
# lugar do texto). Extrator de ENTIDADE: não existe.

def lugar_do_codigo(f):
    """O FACT_LOCATION que o código atual dá ao trecho com o contexto que o gold traz."""
    texto = f['CONTEXTO_ANTES'] + f['TRECHO'] + f['CONTEXTO_DEPOIS']
    aceitas, _ = IT.localizacoes_do_fato(texto)
    ft = FT.campos_do_fato(texto)
    return {'FATO_LOCAL': [a['FACT_LOCATION'] for a in aceitas],
            'FATO_DO_TEXTO': ft.get('fact_location'), 'CAMPOS': ft}


def codigo_resolve(f, esperado):
    alvo = ' '.join(esperado.lower().split()[:2])
    r = lugar_do_codigo(f)
    achados = r['FATO_LOCAL'] + [r['FATO_DO_TEXTO'] or '']
    return any(alvo in (x or '').lower() for x in achados)


def codigo_nao_resolve_nada(f):
    r = lugar_do_codigo(f)
    return not r['FATO_LOCAL'] and str(r['FATO_DO_TEXTO']).startswith('NAO SEI')


class T7_OCodigoAtualContraOGold(unittest.TestCase):

    def test_iv_o_codigo_nao_promove_lugar_nao_resolvido(self):
        """CUMPRE: nos 4 casos UNRESOLVED o código de hoje não inventa lugar."""
        for cid in ('C01', 'C05', 'C06', 'C08'):
            self.assertEqual('UNRESOLVED', CASOS[cid]['ESPERADO']['FACT_LOCATION'])
            self.assertTrue(codigo_nao_resolve_nada(CASOS[cid]['FICHAS'][0]), cid)

    # ── BACKLOG MEDIDO — falhas conhecidas DECLARADAS (não alterar o esperado) ──

    @unittest.expectedFailure
    def test_iv_backlog_c04_lugar_escrito_no_texto(self):
        """NÃO CUMPRE: «zona costiera del Gargano» está na frase; o código dá NAO SEI."""
        c = CASOS['C04']
        self.assertTrue(codigo_resolve(c['FICHAS'][0], c['ESPERADO']['FACT_LOCATION']))

    @unittest.expectedFailure
    def test_iv_backlog_c02_c03_c07_cabecalho_de_seccao(self):
        """NÃO CUMPRE: não há conceito de SECTION_HEADER no código; os três dão NAO SEI."""
        for cid in ('C02', 'C03', 'C07'):
            c = CASOS[cid]
            self.assertTrue(codigo_resolve(c['FICHAS'][0], c['ESPERADO']['FACT_LOCATION']), cid)

    @unittest.expectedFailure
    def test_iv_backlog_location_source_na_saida(self):
        """NÃO CUMPRE: a saída dos extratores não tem LOCATION_SOURCE."""
        r = lugar_do_codigo(CASOS['C04']['FICHAS'][0])
        self.assertTrue(any('location_source' in k.lower() for k in r['CAMPOS']))

    @unittest.expectedFailure
    def test_iv_backlog_c08_expressao_bruta_preservada(self):
        """NÃO CUMPRE: nenhum extrator guarda LOCATION_EXPRESSION_RAW."""
        c = CASOS['C08']
        r = lugar_do_codigo(c['FICHAS'][0])
        self.assertIn(c['ESPERADO']['LOCATION_EXPRESSION_RAW'], json.dumps(r['CAMPOS'], ensure_ascii=False))

    @unittest.expectedFailure
    def test_iv_backlog_extrator_de_entidade_com_entity_source(self):
        """NÃO CUMPRE: nenhum código de extração emite ENTITY_SOURCE."""
        achados = []
        for gaveta in ('leis', 'motor', 'coleta', 'regras', 'admissao', 'guarda'):
            pasta = os.path.join(RAIZ, gaveta)
            for raiz, _, nomes in os.walk(pasta):
                for n in nomes:
                    p = os.path.join(raiz, n)
                    if n.endswith('.py') and p != A.__file__ and 'ENTITY_SOURCE' in _ler(p):
                        achados.append(os.path.relpath(p, RAIZ))
        self.assertTrue(achados, 'nenhum extrator de entidade com ENTITY_SOURCE')


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=2).result
    ok = r.wasSuccessful()
    print('\nMETODO_PUGLIA=%s · %d testes · %d falhas conhecidas declaradas'
          % ('PASS' if ok else 'FAIL', r.testsRun, len(r.expectedFailures)))
    raise SystemExit(0 if ok else 1)
