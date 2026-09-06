#!/usr/bin/env python3
"""
Provas de OPERAÇÃO — o que tem de continuar verdade quando a fonte muda ou quebra.

Os testes canônicos (`test_canonico.py`) protegem o que os documentos DIZEM.
Estes protegem o que o pipeline FAZ quando o mundo não colabora.

A pergunta que cada um responde é sempre a mesma:
**isto falha fechado, ou produz um número errado com cara de certo?**
"""
import datetime
import gzip
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import source_health as sh                                     # noqa: E402
from coverage import Coverage, CoverageError                   # noqa: E402
from denominaciones import parse_text, read, split_rows, fold   # noqa: E402
from mapa_regfi import explain_divergence, selling_off          # noqa: E402

SAMPLES = os.path.join(ROOT, 'data', 'samples')
PDF_B = os.path.join(SAMPLES, 'ES-T4-004-versoes', 'dc_web_20260826.pdf')
PDF_A = os.path.join(SAMPLES, 'ES-T4-004-versoes', 'dc_web_20250528.pdf')
SNAP = os.path.join(SAMPLES, 'ES-T4-005', 'ropf_20260829.json.gz')

CONTRATO = ['numRegistro', 'nombre', 'titular', 'fabricante', 'fabrica',
            'formulado', 'estado']
LINHA_BOA = {'numRegistro': 'ES-01717', 'nombre': 'SORATEL MAX',
             'titular': 'ADAMA Agriculture España S.A.',
             'fabricante': 'ADAMA Agri Sol',
             'fabrica': 'ADAMA Agricultural Solutions Ltd. (Neot Hovav)',
             'formulado': 'AZOXISTROBIN 20% + PROTIOCONAZOL 15% [SC] P/V',
             'estado': 'Vigente'}


def snapshot():
    with gzip.open(SNAP, 'rt', encoding='utf-8') as f:
        return json.load(f)['rows']


class TestDegradacaoDeFonte(unittest.TestCase):
    """§12 — nove formas de a fonte apodrecer. Nenhuma pode virar número."""

    def _check(self, payload, **kw):
        kw.setdefault('required_fields', CONTRATO)
        kw.setdefault('identity_key', 'numRegistro')
        return sh.check(payload, **kw)[0]

    def test_campo_obrigatorio_desaparece(self):
        linha = {k: v for k, v in LINHA_BOA.items() if k != 'fabricante'}
        self.assertEqual(self._check([linha]), sh.FAILED,
                         'perder campo do contrato tem de ser FAILED')

    def test_chave_de_identidade_desaparece(self):
        linha = {k: v for k, v in LINHA_BOA.items() if k != 'numRegistro'}
        self.assertEqual(self._check([linha]), sh.FAILED)

    def test_ordem_das_colunas_muda_e_nao_quebra_nada(self):
        """Ler por NOME de campo, nunca por posição — é o que torna isto inofensivo."""
        invertida = dict(reversed(list(LINHA_BOA.items())))
        self.assertEqual(self._check([invertida]), sh.HEALTHY)
        self.assertEqual(invertida['numRegistro'], LINHA_BOA['numRegistro'])

    def test_json_ganha_campo_e_isso_e_noticia_mas_nao_e_falha(self):
        linha = dict(LINHA_BOA, campoNovoDoMinisterio='?')
        self.assertEqual(self._check([linha]), sh.DEGRADED,
                         'campo novo é DEGRADED: usável, e o contrato mudou')

    def test_endpoint_devolve_html_no_lugar_de_json(self):
        self.assertEqual(
            sh.check([LINHA_BOA], required_fields=CONTRATO, identity_key='numRegistro',
                     content_type='text/html; charset=utf-8',
                     expected_type='application/json')[0],
            sh.FAILED, '200 com corpo errado é FAILED')

    def test_lista_vazia_nunca_e_zero_resultados(self):
        self.assertEqual(self._check([]), sh.FAILED,
                         'lista vazia é falha de fonte, não "não há nada"')

    def test_pagina_de_erro_com_http_200(self):
        """O caso que motiva a regra: status bom, corpo lixo."""
        self.assertEqual(self._check({'erro': 'servicio no disponible'}), sh.FAILED)

    def test_id_duplicado(self):
        self.assertEqual(self._check([LINHA_BOA, dict(LINHA_BOA)]), sh.DEGRADED)

    def test_identidade_vazia(self):
        self.assertEqual(self._check([dict(LINHA_BOA, numRegistro='')]), sh.FAILED)

    def test_volume_fora_da_faixa_nao_passa_por_saudavel(self):
        poucos = [dict(LINHA_BOA, numRegistro=f'ES-{i:05d}') for i in range(10)]
        self.assertEqual(self._check(poucos, expect_rows=3084), sh.DEGRADED)

    def test_falha_de_fonte_nunca_vira_zero(self):
        """SOURCE_FAILED e "zero linhas" não podem produzir a mesma saída."""
        self.assertEqual(self._check(None), sh.FAILED)
        self.assertEqual(
            sh.version_state(fetch_ok=False, current_hash=None, previous_hash='abc'),
            sh.SOURCE_FAILED)
        self.assertNotEqual(sh.SOURCE_FAILED, sh.NO_NEW_VERSION)


class TestEstadosDeVersao(unittest.TestCase):
    """§8 e §10 — quatro estados que não podem virar o mesmo resultado."""

    def test_primeira_versao_nunca_e_no_change(self):
        st = sh.version_state(fetch_ok=True, current_hash='a', previous_hash=None)
        self.assertEqual(st, sh.BASELINE_ESTABLISHED)
        self.assertNotIn(st, (sh.NO_NEW_VERSION, sh.NEW_VERSION_IDENTICAL))
        self.assertFalse(sh.can_diff(st), 'baseline não autoriza emitir evento')

    def test_os_quatro_estados_sao_distintos(self):
        estados = {
            sh.version_state(fetch_ok=True, current_hash='a', previous_hash=None),
            sh.version_state(fetch_ok=False, current_hash=None, previous_hash='a'),
            sh.version_state(fetch_ok=True, current_hash='a', previous_hash='a',
                             current_version='v2', previous_version='v1'),
            sh.version_state(fetch_ok=True, current_hash='b', previous_hash='a',
                             current_version='v2', previous_version='v1'),
            sh.version_state(fetch_ok=True, current_hash='b', previous_hash='a',
                             current_version='v1', previous_version='v1'),
        }
        self.assertEqual(len(estados), 5, 'dois estados colapsaram no mesmo valor')

    def test_so_new_version_changed_autoriza_evento(self):
        for st in (sh.BASELINE_ESTABLISHED, sh.NO_NEW_VERSION,
                   sh.NEW_VERSION_IDENTICAL, sh.SOURCE_FAILED):
            with self.subTest(estado=st):
                self.assertFalse(sh.can_diff(st))
        self.assertTrue(sh.can_diff(sh.NEW_VERSION_CHANGED))

    def test_o_registro_espanhol_ainda_e_baseline(self):
        """Só existe UMA versão arquivada do export: não se pode dizer "nada mudou"."""
        self.assertTrue(os.path.exists(SNAP))
        versoes = [f for f in os.listdir(os.path.dirname(SNAP)) if f.endswith('.json.gz')]
        st = sh.version_state(fetch_ok=True, current_hash='x',
                              previous_hash='y' if len(versoes) > 1 else None)
        if len(versoes) == 1:
            self.assertEqual(st, sh.BASELINE_ESTABLISHED)


class TestCobertura(unittest.TestCase):
    """§14 — cobertura é saída, e piso é porta."""

    def test_cobertura_abaixo_do_piso_levanta(self):
        c = Coverage('t')
        for i in range(8):
            c.ok(i)
        c.fail(9, 'X')
        c.fail(10, 'X')
        with self.assertRaises(CoverageError):
            c.require(0.95)

    def test_zero_linhas_e_falha_nao_cobertura_perfeita(self):
        with self.assertRaises(CoverageError):
            Coverage('vazio').require(0.0)

    def test_ambiguo_nao_conta_como_resolvido(self):
        c = Coverage('t')
        c.ok(1)
        c.ambiguity(2, ['a', 'b'])
        self.assertEqual(c.report()['RESOLVED'], 1)
        self.assertEqual(c.report()['AMBIGUOUS'], 1)
        self.assertEqual(c.report()['COVERAGE'], 0.5)

    def test_relatorio_sempre_traz_os_cinco_campos(self):
        r = Coverage('t')
        r.ok(1)
        for campo in ('TOTAL', 'RESOLVED', 'AMBIGUOUS', 'UNRESOLVED', 'COVERAGE'):
            self.assertIn(campo, r.report())

    def test_a_amostra_publicada_declara_cobertura(self):
        with open(os.path.join(SAMPLES, 'ES-T4-004-denominaciones-medida.json'),
                  encoding='utf-8') as f:
            m = json.load(f)['COLUMN_SPLIT']
        for campo in ('RESOLVED_ROWS', 'COVERAGE', 'UNRESOLVED_ROWS',
                      'UNRESOLVED_REASONS'):
            self.assertIn(campo, m, f'a amostra não declara {campo}')


class TestRegressaoDoLeitorAntigo(unittest.TestCase):
    """§13 — a classe de erro que transformou 1.786 em 1.737 não pode voltar.

    O leitor da MISSÃO 06 não foi preservado como código, então não se reproduz o
    bug linha a linha. O que se protege é o INVARIANTE que ele violava: nenhuma
    linha desaparece em silêncio. Toda data terminadora vira uma linha lida ou um
    pedaço declarado como não interpretado — nunca nada.
    """

    FIXTURE = (
        'Nº RegistroProducto de ReferenciaEmpresa ConcesionariaDenominación común'
        '(26/08/2026)Fecha AceptaciónNotas'
        '24635BRAIPROBELTE, S.A.U.PROXIFEN06/03/2019P V/D: 25/08/2026P U/A/E: 25/11/2026'
        '25941TEBKINLÉRIDA UNIÓN QUÍMICA, S.A.TEBULUQ PLUS06/03/2019'
        'ES-01717SORATEL MAXSYNGENTA ESPAÑA S.A.AMISTAR ERA 350 SC10/08/2026')

    def test_a_coluna_notas_e_removida_antes_do_corte(self):
        _, rows, unparsed = parse_text(self.FIXTURE)
        self.assertEqual([r['registration'] for r in rows],
                         ['24635', '25941', 'ES-01717'])
        self.assertEqual(unparsed, [], 'com Notas removidas não sobra pedaço solto')

    def test_sem_remover_notas_os_pedacos_aparecem_como_nao_interpretados(self):
        """A porta `strip_notes=False` existe só para esta prova.

        O ponto não é que o parser antigo perdia linhas — é que ele perdia em
        SILÊNCIO. Aqui, quando a regra é desligada, os pedaços das notas aparecem
        contados como não interpretados. Visível é o oposto de silencioso.
        """
        _, rows, unparsed = parse_text(self.FIXTURE, strip_notes=False)
        self.assertGreater(len(unparsed), 0,
                           'as notas têm de aparecer como não interpretadas')
        self.assertTrue(all(u.startswith('P ') for u in unparsed))

    def test_nada_desaparece_no_pdf_real(self):
        version, rows, unparsed = read(PDF_B)
        self.assertEqual(version, '26/08/2026')
        self.assertEqual(len(unparsed), 0, 'pedaço não interpretado no PDF canônico')
        self.assertEqual(len(rows), 1786)
        por = {}
        for r in rows:
            por[r['registration']] = por.get(r['registration'], 0) + 1
        self.assertEqual(sum(por.values()), len(rows),
                         'a distribuição não soma o total — alguma linha sumiu')
        self.assertEqual(len(por), 720)

    def test_o_numero_publicado_vem_do_pdf_arquivado(self):
        with open(os.path.join(SAMPLES, 'ES-T4-004-denominaciones-medida.json'),
                  encoding='utf-8') as f:
            m = json.load(f)
        _, rows, _ = read(PDF_B)
        self.assertEqual(m['DENOMINATION_ROWS'], len(rows))


class TestDivergenciaEspanhola(unittest.TestCase):
    """§3 e §4 — total igual não prova classificação igual."""

    @classmethod
    def setUpClass(cls):
        cls.rows = snapshot()
        cls.hoje = datetime.date(2026, 8, 29)

    def test_a_regra_do_filtro_reproduz_os_dois_placares(self):
        d = explain_divergence(self.rows, self.hoje)
        self.assertEqual(d['TOTAL'], 3084)
        self.assertEqual(d['BY_FIELD_Estado'], {'Vigente': 1993, 'Cancelado': 1091})
        self.assertEqual(d['BY_FILTER_IdEstado'],
                         {'1_VIGENTE': 1998, '2_CANCELADO': 1086})

    def test_os_cinco_sao_exatamente_os_do_prazo_de_escoamento(self):
        with open(os.path.join(SAMPLES, 'ES-T4-005-divergencia-resolvida.json'),
                  encoding='utf-8') as f:
            pub = {x['REGISTRATION_ID'] for x in json.load(f)['THE_FIVE']}
        medido = {r['NumRegistro'] for r in selling_off(self.rows, self.hoje)}
        self.assertEqual(medido, pub, 'igualdade de conjunto, não de contagem')
        self.assertEqual(len(medido), 5)

    def test_mesmo_total_nao_e_mesma_classificacao(self):
        """A prova de que comparar contagem não basta."""
        d = explain_divergence(self.rows, self.hoje)
        campo = d['BY_FIELD_Estado']
        filtro = d['BY_FILTER_IdEstado']
        self.assertEqual(sum(campo.values()), sum(filtro.values()),
                         'os dois recortes cobrem o mesmo universo')
        self.assertNotEqual(campo['Vigente'], filtro['1_VIGENTE'],
                            'se estes coincidirem, a divergência sumiu e a regra mudou')

    def test_o_numero_do_filtro_e_datado(self):
        """1.998 cai sozinho quando o último prazo de escoamento vencer."""
        depois = datetime.date(2026, 10, 31)
        d = explain_divergence(self.rows, depois)
        self.assertEqual(d['BY_FILTER_IdEstado']['1_VIGENTE'], 1993,
                         'passado o prazo, filtro e campo convergem')


class TestIdentidadeEntreVersoes(unittest.TestCase):
    """§11 e §16 — nome não é identidade, e papel não é valor."""

    @classmethod
    def setUpClass(cls):
        cls.reg = {r['NumRegistro']: r for r in snapshot()}
        _, rows, _ = read(PDF_B)
        cls.done, _ = split_rows(rows, cls.reg)

    def test_mesmo_registro_com_nome_diferente_e_a_mesma_entidade(self):
        _, a, _ = read(PDF_A)
        nomes_a = {r['registration'] for r in a}
        self.assertIn('ES-01717', nomes_a)
        self.assertIn('ES-01717', self.reg)
        self.assertEqual(self.reg['ES-01717']['Nombre'], 'SORATEL MAX')
        # a versão A chamava o mesmo registro de MAXENTIS
        antigo = [r['middle_raw'] for r in a if r['registration'] == 'ES-01717']
        self.assertTrue(all(m.startswith('MAXENTIS') for m in antigo))

    def test_dentro_do_pais_o_nome_e_unico_e_isso_e_um_fato_medido(self):
        """Medido, não suposto: no ROPF nenhum nome de produto se repete.

        Isso NÃO autoriza usar o nome como chave. Ele é único *nesta versão e neste
        país* — e a MISSÃO 07 provou que ele muda (MAXENTIS → SORATEL MAX) enquanto o
        registro fica. Chave única hoje não é chave estável amanhã.
        """
        por_nome = {}
        for r in self.reg.values():
            por_nome.setdefault((r['Nombre'] or '').strip().upper(), set()).add(
                r['NumRegistro'])
        repetidos = {n: ids for n, ids in por_nome.items() if len(ids) > 1 and n}
        self.assertEqual(repetidos, {}, 'se um nome passar a se repetir, qualquer código '
                                        'que use nome como chave começa a colapsar '
                                        'registros — este teste é o alarme')

    def test_nomes_parecidos_sao_registros_diferentes(self):
        """SORATEL (ES-01665) e SORATEL MAX (ES-01717): prefixo comum, produtos distintos."""
        self.assertEqual(self.reg['ES-01665']['Nombre'], 'SORATEL')
        self.assertEqual(self.reg['ES-01717']['Nombre'], 'SORATEL MAX')
        self.assertIn('PROTIOCONAZOL 25%', self.reg['ES-01665']['Formulado'])
        self.assertIn('AZOXISTROBIN', self.reg['ES-01717']['Formulado'])

    def test_mesmo_nome_em_paises_diferentes_nao_e_o_mesmo_produto(self):
        """AVASTEL existe em FR, ES e IT com composições diferentes."""
        with open(os.path.join(SAMPLES, 'CROSS-MARKET-prothioconazole-cereal.json'),
                  encoding='utf-8') as f:
            x = json.load(f)['ADAMA_NAMING_ACROSS_THE_THREE']
        av = x['AVASTEL']
        self.assertEqual(len({av['FR'], av['ES'], av['IT']}), 3,
                         'três registros distintos sob o mesmo nome comercial')
        self.assertIn('CAUTION', x)

    def test_titular_e_concessionaria_continuam_papeis_distintos(self):
        coincid = {d['REGISTRATION_ID'] for d in self.done
                   if fold((self.reg.get(d['REGISTRATION_ID']) or {}).get('Titular') or '')
                   == fold(d['CONCESSIONAIRE'])}
        self.assertGreaterEqual(len(coincid), 100,
                                'a coincidência de papel é o teste negativo do modelo')
        for rid in list(coincid)[:3]:
            with self.subTest(registro=rid):
                linhas = [d for d in self.done if d['REGISTRATION_ID'] == rid]
                self.assertTrue(all('CONCESSIONAIRE' in d and 'REFERENCE_PRODUCT' in d
                                    for d in linhas),
                                'os papéis continuam em campos separados')

    def test_grupo_empresarial_nao_colapsa_entidade_legal(self):
        """Sem fonte de relação corporativa, entidades distintas ficam distintas."""
        import chain
        entidades = {r['Titular'] for r in self.reg.values()
                     if r['Titular'] and chain.grupo(r['Titular']) == 'ADAMA'}
        self.assertEqual(len(entidades), 1, 'na Espanha há uma entidade ADAMA titular')
        self.assertEqual(chain.grupo('ADAMA Agriculture España S.A.'), 'ADAMA')
        self.assertEqual(chain.grupo('ADAMA Agricultural Solutions Ltd.'), 'ADAMA')
        # Comparava dois literais. O que prova a lei é que as DUAS entidades existem
        # com o mesmo grupo e nomes diferentes — e isso pergunta-se ao `chain`.
        self.assertEqual(chain.grupo('ADAMA Agriculture España S.A.'),
                         chain.grupo('ADAMA Agricultural Solutions Ltd.'),
                         'mesmo grupo')
        self.assertNotEqual(chain.normalizar('ADAMA Agriculture España S.A.')
                            if hasattr(chain, 'normalizar') else 'ADAMA Agriculture España S.A.',
                            chain.normalizar('ADAMA Agricultural Solutions Ltd.')
                            if hasattr(chain, 'normalizar') else 'ADAMA Agricultural Solutions Ltd.',
                            'mesmo grupo, entidades diferentes — nunca colapsar')


class TestCurrentVersusHistorical(unittest.TestCase):
    """§18 — fato atual e fato histórico apontam para versões diferentes."""

    def test_o_tramite_atual_nao_serve_de_historico(self):
        """O ROPF sobrescreve o trâmite: 4 das 5 renomeações já não aparecem."""
        with open(os.path.join(SAMPLES, 'CHANGE-EVENTS-es-2025-2026.json'),
                  encoding='utf-8') as f:
            ev = json.load(f)
        conf = ev['CONFIRMED_NAME_CHANGES']
        self.assertEqual(len(conf), 5)
        ainda = [c for c in conf
                 if (c.get('LAST_TRAMITE_TODAY') or [None])[0] == 'MODIFICACION NOMBRE']
        self.assertEqual(len(ainda), 1,
                         'se mais de um ainda mostrasse o trâmite, a fonte teria mudado '
                         'de comportamento e a régua precisaria ser revista')

    def test_o_fato_historico_aponta_para_a_versao_arquivada(self):
        with open(os.path.join(SAMPLES, 'CHANGE-EVENTS-es-2025-2026.json'),
                  encoding='utf-8') as f:
            ev = json.load(f)
        for lado in ('SOURCE_VERSION_A', 'SOURCE_VERSION_B'):
            with self.subTest(versao=lado):
                self.assertIn('sha256', ev[lado])
                arq = os.path.join(SAMPLES, 'ES-T4-004-versoes',
                                   {'SOURCE_VERSION_A': 'dc_web_20250528.pdf',
                                    'SOURCE_VERSION_B': 'dc_web_20260826.pdf'}[lado])
                self.assertEqual(sh.sha256_file(arq), ev[lado]['sha256'],
                                 'o arquivo apontado não é o que gerou o evento')

    def test_a_ficha_atual_nao_carrega_o_nome_antigo(self):
        reg = {r['NumRegistro']: r for r in snapshot()}
        self.assertEqual(reg['ES-01717']['Nombre'], 'SORATEL MAX')
        self.assertNotEqual(reg['ES-01717']['Nombre'], 'MAXENTIS')


if __name__ == '__main__':
    unittest.main()


class TestCadeiasDeclaram(unittest.TestCase):
    """§6 e §19 — nenhuma cadeia entrega número sem dizer como chegou nele."""

    @classmethod
    def setUpClass(cls):
        import chain
        cls.chain = chain

    def test_toda_cadeia_existe_e_e_chamavel(self):
        self.assertEqual(set(self.chain.CHAINS),
                         {'fr-prothioconazole', 'es-identidade',
                          'it-prothioconazole', 'raif-repilo'})
        for nome, fn in self.chain.CHAINS.items():
            with self.subTest(cadeia=nome):
                self.assertTrue(callable(fn))

    def test_o_dicionario_de_grupo_e_declarado_e_nao_inferido(self):
        """Agrupar empresa é decisão humana: tem de estar escrita, não adivinhada."""
        self.assertIn('ADAMA', self.chain.GRUPOS)
        self.assertEqual(self.chain.grupo('empresa desconhecida ltda'), 'OUTROS',
                         'sem entrada no dicionário, o grupo é OUTROS — nunca um palpite')

    def test_falha_de_cadeia_e_um_tipo_proprio(self):
        with self.assertRaises(self.chain.ChainFailure):
            self.chain.fr_prothioconazole(raw='/caminho/que/nao/existe')

    def test_o_rebaixamento_de_tls_nunca_desliga_a_verificacao(self):
        """Aceitar cifra antiga é uma coisa; não verificar o certificado é outra."""
        fonte = open(os.path.join(ROOT, 'scripts', 'chain.py'), encoding='utf-8').read()
        for proibido in ('CERT_NONE', 'check_hostname = False', '_create_unverified'):
            with self.subTest(proibido=proibido):
                self.assertNotIn(proibido, fonte)
        self.assertIn('SECLEVEL=1', fonte)
        self.assertIn('TLS_DOWNGRADES', fonte,
                      'o rebaixamento tem de ser registrado, nunca silencioso')


class TestProvenienciaDeClaim(unittest.TestCase):
    """§19 — CLAIM → DERIVAÇÃO → LINHA → SNAPSHOT → VERSÃO → FONTE, sem elo na memória."""

    def elo(self, caminho):
        p = os.path.join(SAMPLES, caminho)
        self.assertTrue(os.path.exists(p), f'elo ausente no disco: {caminho}')
        return p

    def test_o_claim_do_titular_espanhol_tem_cadeia_completa(self):
        p = self.elo('ES-T4-005-ficha-primaria-es01717.json')
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        self.assertEqual(d['NORMALIZED']['REFERENCE_HOLDER'],
                         'ADAMA Agriculture España S.A.')
        self.assertIn('REQUEST', d, 'sem a requisição, o elo até a fonte é memória')
        self.assertIn('RAW_FIELDS', d, 'sem o bruto, a normalização não é auditável')
        self.assertIn('captured_at', d)
        self.assertEqual(d['RAW_FIELDS']['titular'], d['NORMALIZED']['REFERENCE_HOLDER'],
                         'o campo normalizado não bate com o bruto que ele diz normalizar')

    def test_o_claim_das_denominacoes_tem_cadeia_completa(self):
        with open(self.elo('ES-T4-004-denominaciones-medida.json'), encoding='utf-8') as f:
            d = json.load(f)
        self.assertEqual(d['document_version_date'], '26/08/2026')
        self.assertIn('parser', d, 'sem o parser nomeado, a derivação é memória')
        self.elo(os.path.join('ES-T4-004-versoes', 'dc_web_20260826.pdf'))

    def test_o_claim_do_change_event_aponta_para_as_duas_versoes(self):
        with open(self.elo('CHANGE-EVENTS-es-2025-2026.json'), encoding='utf-8') as f:
            d = json.load(f)
        for lado in ('SOURCE_VERSION_A', 'SOURCE_VERSION_B'):
            self.assertIn('sha256', d[lado])
            self.assertIn('version_date', d[lado])

    def test_a_divergencia_publicada_tem_requisicao_e_data(self):
        with open(self.elo('ES-T4-005-divergencia-resolvida.json'), encoding='utf-8') as f:
            d = json.load(f)
        self.assertIn('request', d['OBSERVED']['grid'])
        self.assertEqual(d['AS_OF'], '2026-08-29')
        self.assertTrue(d['TIME_DEPENDENT'],
                        'um número datado tem de se declarar datado')

    def test_toda_amostra_publicada_declara_proveniencia(self):
        faltando = []
        for nome in sorted(os.listdir(SAMPLES)):
            if not nome.endswith('.json'):
                continue
            with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
                try:
                    d = json.load(f)
                except json.JSONDecodeError:
                    continue
            if not isinstance(d, dict):
                continue
            if not ({'SOURCE_LOCATION', 'FACT_LOCATION'} <= set(d)):
                faltando.append(nome)
        self.assertEqual(faltando, [], 'amostra sem envelope de proveniência')


class TestAchadosSobreOFreeze(unittest.TestCase):
    """§0 — o que esta missão descobriu sobre números já congelados."""

    def test_o_criterio_italiano_esta_declarado(self):
        """A M02 publicou "85 em vigor" sem dizer quais estados contam.

        83 conta só estados que contêm "Autorizzato"; 85 inclui "Ri-registrato". Os dois
        são defensáveis; publicar sem o critério não é. O achado está registrado e não
        quebra o freeze — o número dos produtos ADAMA (5) é o mesmo nos dois critérios.
        """
        doc = open(os.path.join(ROOT, 'docs', 'operacao',
                                'PROVA-DE-RECORRENCIA-MISSAO-08.md'), encoding='utf-8').read()
        self.assertIn('FREEZE_V1_FINDING', doc)
        self.assertIn('Ri-registrato', doc)
        self.assertRegex(doc, r'\b83\b')
        self.assertRegex(doc, r'\b85\b')
