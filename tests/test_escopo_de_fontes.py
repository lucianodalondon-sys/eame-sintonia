#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O ESCOPO OPERACIONAL DAS FONTES — a Italia corre sozinha, e prova-se.

    CATALOGO GLOBAL  !=  REGISTO OPERACIONAL DO PAIS
    SOURCE_LOCATION  !=  FACT_LOCATION
    EU SOURCE        !=  ITALY SOURCE automaticamente
    CELULA DO LOTE   !=  IDENTIDADE DE CANAL

⚠️ ESTES TESTES NAO CONGELAM O NUMERO DE FONTES DE HOJE.
Um teste que fixa «55 fontes italianas» proibe a 56.ª e reprova quem escrever a
ficha nova. O que se exige aqui e a RELACAO: que nenhuma fonte de outro pais
consiga ser CHAMADA pela operacao italiana, e que nada tenha sido apagado para
o conseguir. Acrescentar uma fonte italiana passa; acrescentar uma espanhola ao
caminho italiano reprova.
"""
import io
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import escopo_de_fontes as esc  # noqa: E402


def _ler(caminho: str) -> str:
    with io.open(caminho, encoding='utf-8') as f:
        return f.read()


def _node(js: str):
    """Corre uma expressao no lado Node e devolve o JSON que ela imprimir."""
    r = subprocess.run(['node', '--input-type=module', '-e', js],
                       cwd=RAIZ, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError('node falhou: %s' % (r.stderr or r.stdout)[:800])
    return json.loads(r.stdout)


class ORegistoEDono(unittest.TestCase):
    """A lei mora num sitio, e os dois lados leem-na de la."""

    def test_o_pais_ativo_vem_do_registo_e_nao_de_uma_string_no_codigo(self):
        with io.open(os.path.join(RAIZ, 'regras', 'ESCOPO-DE-FONTES.json'),
                     encoding='utf-8') as f:
            reg = json.load(f)
        self.assertEqual(esc.PAIS_OPERACIONAL_ATIVO, reg['PAIS_OPERACIONAL_ATIVO'])
        import sensor_coleta as sc
        self.assertEqual(sc.PAIS_DA_ROTA, reg['PAIS_OPERACIONAL_ATIVO'],
                         'o sensor tem de ler o pais do registo, nao ter o seu')

    def test_os_dois_lados_dao_o_mesmo_veredito(self):
        """Duas implementacoes sem esta prova sao duas verdades a espera."""
        ids = [f['SOURCE_ID'] for f in esc.censo()['FONTES']]
        ids += ['EU-T4-002', 'ES-T4-005', 'FR-T3-002', 'XX-T1-001',
                'https://www.fitosanitari.salute.gov.it/', 'IT', '', 'it-t3-002']
        py = {i: esc.veredito(i).permitido for i in ids}
        js = _node(
            'import * as e from "./regras/escopo_de_fontes.mjs";'
            'const ids=%s;'
            'console.log(JSON.stringify(Object.fromEntries('
            '  ids.map(i=>[i, e.veredito(i).permitido]))));' % json.dumps(ids))
        self.assertEqual(py, js, 'Python e Node divergiram sobre quem pode correr')


class OsQuatroGrupos(unittest.TestCase):
    """§4 — toda fonte conhecida cai em exactamente um grupo."""

    def setUp(self):
        self.censo = esc.censo()

    def test_cada_fonte_cai_num_grupo_e_num_so(self):
        for f in self.censo['FONTES']:
            self.assertIn(f['GRUPO'], esc.GRUPOS, f['SOURCE_ID'])

    def test_nenhuma_fonte_ficou_sem_ser_censeada(self):
        """O censo tem de cobrir o que o proprio mapa ja mediu."""
        medido = os.path.join(RAIZ, 'system-map', 'data', 'sources.generated.json')
        with io.open(medido, encoding='utf-8') as f:
            S = json.load(f)
        esperados = {x['source_id'] for x in S.get('SOURCES', []) if x.get('source_id')}
        esperados |= {x['source_id'] for x in S.get('MASTER_ITALIANO', [])
                      if x.get('source_id')}
        censeadas = {f['SOURCE_ID'] for f in self.censo['FONTES']}
        self.assertEqual(esperados - censeadas, set(),
                         'ha fonte medida pelo mapa e ausente do censo de escopo')

    def test_as_contas_sao_censeadas_por_linha_e_nao_por_celula(self):
        """8 celulas levam duas contas. Contar celulas perdia oito contas."""
        with io.open(os.path.join(RAIZ, 'data', 'samples',
                                  'COMPETITOR-PUBLIC-COMM', 'CONTAS-V1.json'),
                     encoding='utf-8') as f:
            linhas = json.load(f)['ACCOUNTS']
        self.assertEqual(len(self.censo['CONTAS']), len(linhas))

    def test_entidade_e_canal_contam_se_separados(self):
        """54 canais nao sao 54 organizacoes — e o censo nao os soma."""
        c = self.censo['CONTAGENS']
        for rotulo in ('ITALY', 'SPAIN', 'FRANCE', 'EU_SHARED'):
            self.assertIn('%s_OWNER_COUNT' % rotulo, c)
            self.assertIn('%s_SOURCE_CHANNEL_COUNT' % rotulo, c)
            self.assertLessEqual(c['%s_OWNER_COUNT' % rotulo],
                                 c['%s_SOURCE_CHANNEL_COUNT' % rotulo],
                                 'ha mais organizacoes do que canais em %s' % rotulo)


class ATravaNaoDependeDeNinguemSeLembrar(unittest.TestCase):
    """§15 — o preflight esta no seletor, e fecha por omissao."""

    def _plano(self, frase, **filtros):
        sys.path.insert(0, os.path.join(RAIZ, 'pedido'))
        import receitas
        import pedido as pd
        p = pd.de_uma_frase(frase)
        p.filtros.update(filtros)
        return receitas.resolver(p)

    def test_pedido_sem_pais_nao_traz_fonte_estrangeira(self):
        """O defeito medido: `if pais:` so filtrava quando alguem escrevia o pais."""
        for frase in ('colete regulatorio', 'colete boletins de praga',
                      'colete ciencia', 'colete clima',
                      'colete materiais de pesquisadores'):
            pl = self._plano(frase)
            for f in pl.fontes_do_assunto:
                v = esc.veredito(f.get('source_id'))
                self.assertTrue(v.permitido,
                                '%r trouxe %s: %s' % (frase, f.get('source_id'), v.motivo))

    def test_pedir_espanha_numa_operacao_italiana_nao_abre_espanha(self):
        """O filtro do pedido so ESTREITA. Nunca alarga."""
        pl = self._plano('colete regulatorio', pais='ES')
        self.assertEqual([f.get('source_id') for f in pl.fontes_do_assunto], [])

    def test_o_que_foi_barrado_viaja_no_plano_e_nao_desaparece(self):
        pl = self._plano('colete regulatorio')
        self.assertTrue(pl.fora_do_escopo, 'o plano calou o que barrou')
        for x in pl.fora_do_escopo:
            self.assertTrue(x['veredito']['MOTIVO'], 'recusa sem motivo escrito')


class OTesteDeContaminacao(unittest.TestCase):
    """§17 — a prova seca: o que o seletor italiano PODERIA executar."""

    def setUp(self):
        self.censo = esc.censo()
        self.ativos = ([f for f in self.censo['FONTES'] if f['ATIVO_NA_ITALIA']]
                       + [c for c in self.censo['CONTAS'] if c['ATIVO_NA_ITALIA']]
                       + [r for r in self.censo['RECORTES'] if r['ATIVO_NA_ITALIA']])

    def test_ES_ACTIVE_IN_ITALY_e_zero(self):
        self.assertEqual([x for x in self.ativos if x['COUNTRY_SCOPE'] == 'ES'], [])

    def test_FR_ACTIVE_IN_ITALY_e_zero(self):
        self.assertEqual([x for x in self.ativos if x['COUNTRY_SCOPE'] == 'FR'], [])

    def test_UNKNOWN_ACTIVE_IN_ITALY_e_zero(self):
        self.assertEqual([x for x in self.ativos
                          if x['COUNTRY_SCOPE'] == esc.NAO_SEI], [])

    def test_EU_UNAPPROVED_ACTIVE_IN_ITALY_e_zero(self):
        fora = [x for x in self.ativos if x['COUNTRY_SCOPE'] == 'EU'
                and x['SOURCE_ID'] not in esc.ALLOWLIST]
        self.assertEqual(fora, [])

    def test_toda_fonte_ativa_tem_IT_ou_autorizacao_com_prova(self):
        for f in self.censo['FONTES']:
            if not f['ATIVO_NA_ITALIA']:
                continue
            if f['COUNTRY_SCOPE'] == 'IT':
                continue
            aut = esc.ALLOWLIST.get(f['SOURCE_ID'])
            self.assertIsNotNone(aut, '%s ativa sem autorizacao' % f['SOURCE_ID'])
            self.assertEqual(aut['ITALY_USE_ALLOWED'], 'YES')
            self.assertTrue(aut.get('PROVA_CONTRATO'), 'autorizacao sem contrato citado')
            self.assertTrue(aut.get('PROVA_CHAMADOR'), 'autorizacao sem chamador citado')


class AProvaSeca(unittest.TestCase):
    """§17 — perguntado AO SELETOR, e nao ao registo.

    Perguntar ao registo «quem esta autorizado?» devolve a lei. Perguntar ao
    seletor «o que e que tu me davas?» devolve o que a maquina faria — e as
    duas so batem se a trava estiver mesmo no caminho.
    """

    def setUp(self):
        self.r = esc.prova_seca()

    def test_o_seletor_varre_todos_os_alvos(self):
        self.assertGreaterEqual(len(self.r['ALVOS_VARRIDOS']), 10)

    def test_nenhum_dos_quatro_contadores_de_contaminacao_e_maior_que_zero(self):
        for k in ('ES_ACTIVE_IN_ITALY', 'FR_ACTIVE_IN_ITALY',
                  'UNKNOWN_ACTIVE_IN_ITALY', 'EU_UNAPPROVED_ACTIVE_IN_ITALY'):
            self.assertEqual(self.r[k], 0, '%s = %d' % (k, self.r[k]))

    def test_o_seletor_continua_a_devolver_fontes_italianas(self):
        """A trava nao pode ter-se transformado em «nao devolve nada»."""
        pais = self.r['EXECUTAVEIS_POR_PAIS']
        self.assertGreater(pais.get('IT', 0), 0, 'a Italia ficou sem fontes')

    def test_o_que_foi_barrado_tem_motivo_escrito(self):
        self.assertTrue(self.r['BARRADAS'])
        for sid, v in self.r['BARRADAS'].items():
            self.assertTrue(v['MOTIVO'].strip(), sid)


class NadaFoiApagado(unittest.TestCase):
    """§10 — Espanha e Franca continuam inteiras, e pesquisaveis por gente."""

    def test_as_fichas_estrangeiras_continuam_no_atlas(self):
        atlas = _ler(os.path.join(RAIZ, 'docs', 'fontes', 'ATLAS-DE-FONTES-EAME.md'))
        for sid in ('ES-T3-001', 'ES-T4-005', 'FR-T4-001', 'FR-T3-001'):
            self.assertIn(sid, atlas, '%s desapareceu do atlas' % sid)

    def test_os_recortes_estrangeiros_continuam_declarados(self):
        import sensor_coleta as sc
        for g in ('ES-OLIVE-REPILO', 'ES-CEREAL-SEPTORIA',
                  'FR-VINE-DOWNY_MILDEW', 'FR-CEREAL-SEPTORIA'):
            self.assertIn(g, sc.TERMOS, '%s foi apagado em vez de desativado' % g)

    def test_as_contas_estrangeiras_continuam_no_cadastro(self):
        n = len([c for c in esc.censo()['CONTAS']
                 if c['COUNTRY_SCOPE'] in ('ES', 'FR')])
        self.assertGreater(n, 0, 'as contas ES/FR sumiram do cadastro')

    def test_os_ficheiros_de_espanha_e_franca_continuam_no_disco(self):
        for rel in ('coleta/es/corpus_es.py', 'guarda/es/adama_es_gate.py',
                    'docs/fontes/SOURCE-PACK-ESPANHA-CIENCIA-E-VOZ.md',
                    'coleta/ephy.sh'):
            self.assertTrue(os.path.isfile(os.path.join(RAIZ, rel)), rel)

    def test_onde_estao_guardadas_esta_escrito(self):
        with io.open(os.path.join(RAIZ, 'regras', 'ESCOPO-DE-FONTES.json'),
                     encoding='utf-8') as f:
            reg = json.load(f)
        onde = reg['ONDE_ESPANHA_E_FRANCA_FICAM_GUARDADAS']
        self.assertTrue(onde['ES'] and onde['FR'])


class ORedTeam(unittest.TestCase):
    """§18 — vinte ataques. RED_TEAM_SURVIVORS tem de ser 0."""

    def test_01_source_id_ES_nao_entra_na_corrida_italiana(self):
        self.assertFalse(esc.veredito('ES-T3-001').permitido)
        with self.assertRaises(esc.FonteForaDoEscopo):
            esc.exigir('ES-T3-001')

    def test_02_source_id_FR_nao_entra(self):
        self.assertFalse(esc.veredito('FR-T4-001').permitido)
        with self.assertRaises(esc.FonteForaDoEscopo):
            esc.exigir('FR-T4-001')

    def test_03_conta_instagram_espanhola_com_texto_italiano_bloqueia(self):
        """A lingua do post nao e um campo desta decisao — nem chega ca."""
        v = esc.veredito_de_conta('SYNGENTA|ES|INSTAGRAM')
        self.assertFalse(v.permitido)
        self.assertEqual(v.pais, 'ES')

    def test_04_conta_francesa_falando_da_italia_continua_FR(self):
        v = esc.veredito_de_conta('SYNGENTA|FR|FACEBOOK',
                                  url='https://www.facebook.com/SyngentaFrance')
        self.assertFalse(v.permitido)
        self.assertEqual(v.grupo, esc.FRANCE_FUTURE)

    def test_05_fonte_italiana_que_publica_facto_frances_continua_IT(self):
        """O portao e de ESCOPO, nao de geografia do facto.

        Ele nao recebe FACT_LOCATION, nao o le e nao o pode alterar — e a prova
        disso e que a assinatura nao tem por onde o receber.
        """
        self.assertTrue(esc.veredito('IT-T3-002').permitido)
        import inspect
        for fn in (esc.veredito, esc.exigir, esc.veredito_do_pedido):
            self.assertNotIn('fact_location',
                             [p.lower() for p in inspect.signature(fn).parameters])

    def test_06_fonte_EU_sem_autorizacao_bloqueia(self):
        v = esc.veredito('EU-T4-002')
        self.assertFalse(v.permitido)
        self.assertEqual(v.italy_use_allowed, 'UNKNOWN')

    def test_07_fonte_EU_com_autorizacao_explicita_aceita(self):
        v = esc.veredito('EU-T4-001')
        self.assertTrue(v.permitido)
        self.assertTrue(esc.ALLOWLIST['EU-T4-001'].get('PROVA_CHAMADOR'))

    def test_08_country_scope_UNKNOWN_bloqueia(self):
        self.assertFalse(esc.veredito_do_pedido(country_scope=None).permitido)
        self.assertFalse(esc.veredito_do_pedido(country_scope='').permitido)
        self.assertFalse(esc.veredito('XX-T9-001').permitido)

    def test_09_url_ponto_it_sem_identidade_nao_vira_fonte_italiana(self):
        for u in ('https://www.fitosanitari.salute.gov.it/',
                  'agricoltura.regione.campania.it', 'qualquercoisa.it'):
            v = esc.veredito(u)
            self.assertFalse(v.permitido, u)
            self.assertEqual(v.pais, esc.NAO_SEI, u)

    def test_10_texto_italiano_numa_fonte_ES_nao_muda_o_pais(self):
        """Nao ha por onde: a funcao nao recebe texto nem lingua."""
        import inspect
        params = [p.lower() for p in inspect.signature(esc.veredito).parameters]
        for proibido in ('texto', 'lingua', 'language', 'idioma', 'conteudo'):
            self.assertNotIn(proibido, params)
        self.assertFalse(esc.veredito('ES-T5-002').permitido)

    def test_11_owner_italiano_com_canal_global_nao_vira_canal_italiano(self):
        """`basf_global` foi encontrada na celula BASF|IT. Continua global."""
        v = esc.veredito_de_conta('BASF|IT|INSTAGRAM')
        self.assertFalse(v.permitido)
        self.assertEqual(v.pais, esc.NAO_SEI,
                         'o pais da celula do lote nao e o pais da conta')

    def test_12_collector_generico_serve_varios_paises_e_a_selecao_continua_isolada(self):
        """A FERRAMENTA e partilhada; a FONTE e que e decidida."""
        import scrap_http, scrap_executor  # noqa: F401
        fonte = _ler(os.path.join(RAIZ, 'coleta', 'scrap_http.py'))
        self.assertNotIn("PAIS = 'IT'", fonte)
        self.assertFalse(esc.veredito_do_pedido(country_scope='ES').permitido)
        self.assertTrue(esc.veredito_do_pedido(country_scope='IT').permitido)

    def test_13_termo_de_busca_ES_nao_e_carregado_pelo_runner_italiano(self):
        import sensor_coleta as sc
        for lote in sc.LOTES:
            dentro, _ = sc.recortes_no_escopo(lote)
            self.assertEqual([c for c in dentro if c.startswith('ES-')], [], lote)

    def test_14_termo_de_busca_FR_nao_e_carregado_pelo_runner_italiano(self):
        import sensor_coleta as sc
        for lote in sc.LOTES:
            dentro, _ = sc.recortes_no_escopo(lote)
            self.assertEqual([c for c in dentro if c.startswith('FR-')], [], lote)

    def test_15_source_pack_espanhol_preservado_nao_entra_na_lista_italiana(self):
        pack = os.path.join(RAIZ, 'docs', 'fontes',
                            'SOURCE-PACK-ESPANHA-CIENCIA-E-VOZ.md')
        self.assertTrue(os.path.isfile(pack), 'o source pack foi apagado')
        ativos = {f['SOURCE_ID'] for f in esc.censo()['FONTES']
                  if f['ATIVO_NA_ITALIA']}
        self.assertEqual({s for s in ativos if s.startswith('ES-')}, set())

    def test_16_atlas_global_continua_com_ES_e_FR_e_a_selecao_continua_limpa(self):
        censo = esc.censo()
        conhecidas = {f['COUNTRY_SCOPE'] for f in censo['FONTES']}
        self.assertTrue({'ES', 'FR'} <= conhecidas, 'o catalogo esqueceu paises')
        ativas = {f['COUNTRY_SCOPE'] for f in censo['FONTES'] if f['ATIVO_NA_ITALIA']}
        self.assertEqual(ativas - {'IT', 'EU'}, set())

    def test_17_ficheiro_futuro_ES_FR_nao_e_lido_pelo_runner_italiano(self):
        """O coletor documental italiano nomeia so fontes que o portao deixa."""
        fonte = _ler(os.path.join(RAIZ, 'coleta', 'italy_pilot_collect.mjs'))
        import re
        for sid in re.findall(r'"((?:ES|FR)-T\d{1,2}-\d{3})"', fonte):
            self.fail('o coletor italiano nomeia %s' % sid)

    def test_18_ficheiro_GERADO_alterado_a_mao_e_corrigido_pela_regeneracao(self):
        """O censo e derivado: mexer na saida nao muda a resposta."""
        antes = esc.censo()['CONTAGENS']
        depois = esc.censo()['CONTAGENS']
        self.assertEqual(antes, depois)
        indice = os.path.join(RAIZ, 'docs', 'fontes', 'INDICE-DE-FONTES.md')
        self.assertIn('Este ficheiro é gerado', _ler(indice))

    def test_19_SOURCE_LOCATION_nao_altera_FACT_LOCATION(self):
        """O dono do lugar do facto nao foi tocado por esta missao."""
        import lugar_do_fato  # noqa: F401
        fonte = _ler(os.path.join(RAIZ, 'leis', 'lugar_do_fato.py'))
        self.assertNotIn('escopo_de_fontes', fonte,
                         'o portao de escopo entrou no dono do lugar do facto')

    def test_20_SOURCE_ID_nunca_e_recriado_pelo_movimento(self):
        """Separar nao renomeia. O censo devolve o ID que leu, tal e qual."""
        medido = os.path.join(RAIZ, 'system-map', 'data', 'sources.generated.json')
        with io.open(medido, encoding='utf-8') as f:
            S = json.load(f)
        originais = {x['source_id'] for x in S.get('SOURCES', [])
                     if x.get('source_id')}
        originais |= {x['source_id'] for x in S.get('MASTER_ITALIANO', [])
                      if x.get('source_id')}
        censeadas = {f['SOURCE_ID'] for f in esc.censo()['FONTES']}
        self.assertEqual(censeadas - originais, set(),
                         'apareceu um SOURCE_ID que nao existia antes')
        # e nenhum foi cunhado a partir de URL, host ou nome
        for f in esc.censo()['FONTES']:
            self.assertNotIn('://', f['SOURCE_ID'])

    def test_21_contas_sem_identidade_provada_nao_correm(self):
        """Extra: a celula ambigua tambem fecha."""
        v = esc.veredito_de_conta('BAYER|ES|YOUTUBE')
        self.assertFalse(v.permitido)
        self.assertIn('AMBIGUA', v.motivo)

    def test_22_o_despacho_social_recusa_escopo_estrangeiro_antes_da_rota(self):
        """Extra: a recusa tem nome, e chega antes de qualquer rede."""
        import social_rotas as sr
        objetos, registo = sr._executar(platform='MASTODON', capability='SEARCH_HASHTAG',
                                        run_id='RT-22', country_scope='ES',
                                        query='agricultura')
        self.assertEqual(objetos, [])
        self.assertEqual(registo['ESTADO'], sr.ESCOPO_NAO_PERMITIDO)
        self.assertIsNone(registo['ROTA_ESCOLHIDA'],
                          'escolheu rota antes de medir o escopo')


if __name__ == '__main__':
    unittest.main(verbosity=2)
