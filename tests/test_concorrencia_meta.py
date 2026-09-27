#!/usr/bin/env python3
"""
A LINHA RECORRENTE DA META — cada teste tenta QUEBRAR uma separação.

    python3 tests/test_concorrencia_meta.py

FIXTURE DECLARADA: `tests/dados/concorrencia_meta/` é o recorte IT da captura
REAL de 31/08/2026 (ramo `claude/eame-meta-competitor`, a2fad2d0), convertido
para a forma de snapshot da linha — cada ficheiro diz isso no cabeçalho, com o
blob de origem. NÃO é coleta de hoje, e nenhum teste o trata como tal.

Rede fechada: nenhum teste daqui abre navegador. A visita é feita por um
leitor falso injetado (`ler=`), que devolve o que a página devolveria.
"""
import copy
import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import concorrencia_meta as cm  # noqa: E402
import concorrencia_frentes as fr  # noqa: E402
import meta_biblioteca as bib  # noqa: E402
import meta_identidade as ident  # noqa: E402
import meta_anunciante as anun  # noqa: E402
from leis import retorno_da_coleta as rc  # noqa: E402

DADOS = os.path.join(RAIZ, 'tests', 'dados', 'concorrencia_meta')


def _fixture(nome):
    with open(os.path.join(DADOS, nome), encoding='utf-8') as f:
        return json.load(f)


S1 = _fixture('SNAPSHOT-S1-IT-31-08.json')
S2 = _fixture('SNAPSHOT-S2-IT-31-08.json')
ESPERADA = _fixture('COMPARACAO-ESPERADA-IT-31-08.json')
LISTA = json.load(open(cm.LISTA, encoding='utf-8'))


def cartao(lid, texto='Nuova campagna: il prodotto per la vite. Scopri il lancio!',
           estado='Active', inicio='Sep 20, 2026', grupo=1):
    return {'library_id': lid, 'ads_neste_cartao': grupo, 'links': [],
            'texto': '%s\nLibrary ID: %s\nStarted running on %s\nPagina\nSponsored\n%s'
                     % (estado, lid, inicio, texto)}


def leitor(por_pagina, declarado=None, logado=bib.NAO_LOGADO):
    """Um leitor falso: `por_pagina[page_id]` = lista de cartões, ou uma exceção."""
    def ler(url):
        pid = url.split('view_all_page_id=')[1].split('&')[0]
        v = por_pagina.get(pid, [])
        if isinstance(v, Exception):
            raise v
        n = sum(c.get('ads_neste_cartao', 1) for c in v)
        return {'cabecalho': {'logado': logado, 'url': url,
                              'resultados_declarados': (declarado if declarado is not None
                                                        else (str(n) if n else None)),
                              'sem_resultados': n == 0},
                'cartoes': v, 'rolagens': 3, 'parou_sem_crescer': True,
                'url_final': url}
    return ler


class Bancada(unittest.TestCase):
    def setUp(self):
        self.estado = tempfile.mkdtemp(prefix='meta-linha-')
        self.addCleanup(shutil.rmtree, self.estado, True)

    def correr(self, ler, run_id='RUN-T', teto=None, lista=None):
        return cm.correr(run_id, lista=lista or LISTA, estado=self.estado, ler=ler,
                         raiz=self.estado, teto=teto)


# ── 1. a regra de comparação reproduz 31/08 ─────────────────────────────────
class AComparacaoReproduzOTrintaEUm(unittest.TestCase):
    """A regra não é desta linha: é a de 31/08. Tem de dar o MESMO resultado."""

    def test_cada_recorte_IT_bate_com_a_comparacao_antiga(self):
        c = cm.comparar(S1, S2)
        esp = {x['page_id']: x for x in ESPERADA['RECORTES']}
        self.assertEqual(len(c['RECORTES']), len(esp))
        for l in c['RECORTES']:
            x = esp[l['page_id']]
            for k in ('both_ends_complete', 'read_depth_comparable', 'slice_transition'):
                self.assertEqual(l[k], x[k], '%s %s' % (l['page_name'], k))
            for k in ('present_both', 'newly_observed', 'no_longer_observed',
                      'absent_but_not_claimable'):
                self.assertEqual(len(l[k]), x[k], '%s %s' % (l['page_name'], k))

    def test_ler_mais_fundo_nao_vira_anuncio_novo(self):
        """Os 101 cartões a mais de 31/08 em IT são profundidade, não mercado."""
        c = cm.comparar(S1, S2)
        self.assertEqual(c['totals_unit_card_read_depth_comparable'][cm.NEWLY_OBSERVED], 0)
        self.assertEqual(c['read_depth_confounded']['slices'], 4)
        self.assertEqual(c['read_depth_confounded']['cards_gained_by_deeper_reading'], 101)
        self.assertEqual(c['change_observed'], 'NO')

    def test_o_414_de_31_08_sao_cartoes_e_nao_anuncios(self):
        self.assertEqual(sum(r['cards'] for r in S1['RECORTES']), 414)
        self.assertEqual(sum(r['ads_represented'] or 0 for r in S1['RECORTES']), 601)

    def test_sem_anterior_e_linha_de_base_e_nao_nada_mudou(self):
        c = cm.comparar(None, S2)
        self.assertEqual(c['change_observed'], cm.BASELINE_ONLY)
        self.assertNotEqual(c['change_observed'], 'NO')

    def test_ausencia_em_lista_incompleta_nao_e_terminado(self):
        a, b = copy.deepcopy(S1), copy.deepcopy(S2)
        r = next(x for x in b['RECORTES'] if x['page_name'] == 'UPL-Ltd')
        r['ads'] = r['ads'][:2]
        r['cards'] = 2
        r['completeness'] = bib.AQUEM_DA_FONTE
        l = next(x for x in cm.comparar(a, b)['RECORTES'] if x['page_name'] == 'UPL-Ltd')
        self.assertEqual(l['no_longer_observed'], [])
        self.assertEqual(len(l['absent_but_not_claimable']), 2)

    def test_com_as_duas_pontas_fechadas_o_terminado_se_afirma(self):
        a, b = copy.deepcopy(S1), copy.deepcopy(S2)
        r = next(x for x in b['RECORTES'] if x['page_name'] == 'UPL-Ltd')
        r['ads'] = r['ads'][:2]
        r['cards'] = 2
        c = cm.comparar(a, b)
        l = next(x for x in c['RECORTES'] if x['page_name'] == 'UPL-Ltd')
        self.assertEqual(len(l['no_longer_observed']), 2)
        self.assertEqual(c['change_observed'], 'YES')

    def test_zero_revisitado_mostra_zero_para_ativo(self):
        a, b = copy.deepcopy(S1), copy.deepcopy(S2)
        r = next(x for x in b['RECORTES'] if x['page_name'] == 'Nufarm Brasil')
        r['ads'], r['cards'] = [{'library_id': '999999999'}], 1
        r['completeness'] = bib.COMPLETA_BATE_COM_A_FONTE
        c = cm.comparar(a, b)
        self.assertEqual(c['slice_transitions_unit_slice'][cm.ZERO_TO_ACTIVE], 1)
        self.assertEqual(c['change_observed'], 'YES')

    def test_recorte_que_falhou_nao_entra_na_comparacao(self):
        b = copy.deepcopy(S2)
        b['RECORTES'][1]['slice_state'] = cm.SLICE_FAILED
        c = cm.comparar(S1, b)
        self.assertEqual(len(c['slices_not_comparable']), 1)


# ── 2. a lista: PAGE_ID provado pela Meta, guarda de identidade ─────────────
class AListaSoLevaPaginaProvada(unittest.TestCase):

    def test_o_instituto_polaco_nao_e_visitado(self):
        visitar, fora = cm.paginas_da_linha(LISTA)
        nomes = [p['page_name'] for p in visitar]
        self.assertNotIn('Instytut Adama Mickiewicza', nomes)
        self.assertIn('ADAMA Ltd.', nomes)
        motivo = next(f['MOTIVO'] for f in fora if f['page_name'].startswith('Instytut'))
        self.assertEqual(motivo, ident.IDENTIDADE_RECUSADA)

    def test_fmc_moto_fica_fora_com_motivo_escrito(self):
        _, fora = cm.paginas_da_linha(LISTA)
        m = next(f for f in fora if f['page_name'] == 'FMC Moto Srl')
        self.assertIn('NAO_AGRO', m['MOTIVO'])

    def test_page_id_sem_prova_da_meta_nao_entra(self):
        lista = {'PAGINAS': [{'company': 'Syngenta', 'page_name': 'Syngenta Italia',
                              'page_id': '2007689772789481', 'identity_proof': None,
                              'EM_LINHA': True}]}
        visitar, fora = cm.paginas_da_linha(lista)
        self.assertEqual(visitar, [])
        self.assertEqual(fora[0]['MOTIVO'], ident.PAGE_ID_NAO_PROVADO)

    def test_nome_com_pais_nao_vira_pagina_local(self):
        e = ident.escopo_de_pais({'page_name': 'Bayer Crop Science Italia'})
        self.assertEqual(e['page_country_scope'], ident.SCOPE_NOT_PROVED)
        self.assertEqual(ident.escopo_de_pais(
            {'country_label_by_meta': 'Italy'})['country_code'], 'IT')

    def test_toda_pagina_da_lista_tem_prova_ou_motivo(self):
        visitar, fora = cm.paginas_da_linha(LISTA)
        self.assertEqual(len(visitar) + len(fora), len(LISTA['PAGINAS']))
        self.assertEqual(len(visitar), 23)


# ── 3. a rodada: uma visita, snapshot datado, RAW, proveniência ─────────────
class ARodada(Bancada):

    def test_uma_visita_por_pagina_por_rodada(self):
        visitas = []
        base = leitor({})

        def ler(url):
            visitas.append(url)
            return base(url)
        lista = copy.deepcopy(LISTA)
        lista['PAGINAS'].append(dict(lista['PAGINAS'][1]))      # página repetida
        self.correr(ler, lista=lista)
        self.assertEqual(len(visitas), len(set(visitas)))
        self.assertEqual(len(visitas), 23)

    def test_snapshot_datado_e_raw_com_sha(self):
        env, comp, _ = self.correr(leitor({'100452355885332': [cartao('1234567')]}))
        snaps = os.listdir(os.path.join(self.estado, 'SNAPSHOTS'))
        self.assertEqual(len(snaps), 1)
        s = json.load(open(os.path.join(self.estado, 'SNAPSHOTS', snaps[0])))
        self.assertTrue(s['OBSERVED_AT_INICIO'] and s['OBSERVED_AT_FIM'])
        r = next(x for x in s['RECORTES'] if x['page_id'] == '100452355885332')
        self.assertTrue(r['observed_at'])
        import hashlib
        with open(os.path.join(cm.RAIZ, r['raw']['path']), 'rb') as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), r['raw']['sha256'])
        self.assertEqual(comp['change_observed'], cm.BASELINE_ONLY)

    def test_a_unidade_carrega_a_proveniencia(self):
        env, _, _ = self.correr(leitor({'100452355885332': [cartao('1234567')]}))
        u = env['COLHEITA'][0]
        o = u['OBSERVACAO']
        self.assertEqual(u['SOURCE_ID'], 'EU-T9-002')
        self.assertEqual(o['META_ROUTE'], 'META_ADS_LIBRARY_UI_CHROME_COM_JANELA')
        self.assertEqual(o['COUNTRY_REACHED'], 'IT')
        self.assertEqual(o['TARGET_LOCATION_STATE'], 'NOT_PROVED')
        self.assertEqual(o['LOGIN_STATE'], bib.NAO_LOGADO)
        self.assertTrue(o['RAW_PAGINA']['sha256'])
        self.assertIsNone(o['SPEND'])
        self.assertEqual(u['DOCUMENT_ID'], rc.NAO_SEI)
        self.assertEqual(u['PUBLISHED_AT'], '2026-09-20')

    def test_ferramenta_caida_nao_e_pagina_sem_anuncio(self):
        class Caiu(Exception):
            estado = 'BROWSER_NOT_REACHED'
        ler = leitor({p['page_id']: Caiu('porta 9224 recusou')
                      for p in LISTA['PAGINAS']})
        env, _, _ = self.correr(ler)
        self.assertEqual(env['ESTADO'], rc.FAILED)
        self.assertEqual(env['COLHEITA'], [])
        self.assertTrue(all(e['failure_state'] == 'BROWSER_NOT_REACHED'
                            for e in env['ERROS']))
        self.assertEqual(rc.conferir(env, self.estado), [])

    def test_login_na_pagina_para_a_rodada(self):
        env, _, _ = self.correr(leitor({}, logado='INDEFINIDO'))
        s = json.load(open(os.path.join(
            self.estado, 'SNAPSHOTS', os.listdir(os.path.join(self.estado, 'SNAPSHOTS'))[0])))
        self.assertEqual(len(s['RECORTES']), 1, 'D88: a rodada tem de parar na 1.a')
        self.assertEqual(s['RECORTES'][0]['slice_state'], cm.LOGIN_DETECTADO)
        self.assertEqual(env['COLHEITA'], [])

    def test_segunda_rodada_compara_e_nao_reenvia_o_mesmo_anuncio(self):
        self.correr(leitor({'100452355885332': [cartao('1234567')]}), run_id='R1')
        env, comp, _ = self.correr(leitor({'100452355885332': [cartao('1234567'),
                                                               cartao('7654321')]}),
                                   run_id='R2')
        ids = [u['OBSERVACAO']['META_AD_LIBRARY_ID'] for u in env['COLHEITA']]
        self.assertEqual(ids, ['7654321'])
        self.assertEqual(env['COLHEITA'][0]['OBSERVACAO']['NOVIDADE'],
                         cm.NOVO_NAO_AFIRMAVEL, 'leu 2 cartoes onde antes leu 1: '
                         'profundidade, nao mercado')
        self.assertEqual(comp['change_observed'], 'NO')

    def test_rodada_que_caiu_nao_vira_linha_de_base(self):
        self.correr(leitor({'100452355885332': [cartao('1234567')]}), run_id='R1')
        self.correr(leitor({p['page_id']: RuntimeError('caiu') for p in LISTA['PAGINAS']}),
                    run_id='R2')
        _, comp, _ = self.correr(leitor({'100452355885332': [cartao('1234567')]}),
                                 run_id='R3')
        l = next(x for x in comp['RECORTES'] if x['page_id'] == '100452355885332')
        self.assertEqual(l['present_both'], ['1234567'])


# ── 4. a saída: envelope -> ingresso (RAW) -> Admissão T9 ───────────────────
class ASaidaPelaAdmissaoNormal(Bancada):

    CORRIDA = {'RUN_ID': 'RUN-T', 'PLATFORM': 'Meta Ads Library',
               'ACTOR': 'coleta/concorrencia_meta.py', 'ACTOR_VERSION': '1',
               'SOURCE_COUNTRY': 'IT', 'STARTED_AT': '2026-09-27T00:00:00Z'}

    def test_o_envelope_cumpre_a_col_law_505(self):
        env, _, destino = self.correr(leitor({'100452355885332': [cartao('1234567')]}))
        self.assertEqual(rc.conferir(env, self.estado), [])
        self.assertTrue(destino.endswith(os.path.join('RUN-T', 'ENVELOPE.json')))

    def test_atravessa_o_ingresso_e_a_admissao_responde_t9(self):
        import admissao as adm
        import ingresso as ing
        env, _, _ = self.correr(leitor({'100452355885332': [cartao('1234567')]}))
        r = ing.receber(rc.so_o_que_entra(env), corrida=dict(self.CORRIDA),
                        armazem=ing.ArmazemLocal(self.estado), memoria=None,
                        raiz=self.estado)
        self.assertEqual(r['RECUSAS'], [])
        u = r['PARA_A_PORTA'][0]
        self.assertIn('lancio', u['texto'])
        d = adm.decidir(u, 'T9', corrida='RUN-T')
        self.assertEqual(d.resultado, adm.SIM, d.motivo)
        pronto = adm.pronto_para_inteligencia(u, d)
        self.assertEqual(pronto['UNIVERSO'], 'T9')
        self.assertEqual(pronto['SOURCE_ID'], 'EU-T9-002')
        self.assertEqual(pronto['ITEM_ID'], 'META_AD_LIBRARY:1234567')

    def test_a_receita_t9_abre_a_linha_so_na_fase_dela(self):
        import receitas
        from pedido import Pedido
        com = receitas.resolver(Pedido(alvo='T9', filtros={
            'fase': 'meta-anuncios', 'universo': 'T9', 'pais': 'IT'})).executores
        sem = receitas.resolver(Pedido(alvo='T9', filtros={})).executores
        self.assertEqual(com[0]['id'], 'concorrencia-meta')
        self.assertNotEqual(sem[0]['id'], 'concorrencia-meta')


# ── 5. a ferramenta: completude vem da fonte ────────────────────────────────
class ACompletudeVemDaFonte(unittest.TestCase):

    def test_parou_de_crescer_nao_e_completa(self):
        self.assertEqual(bib.completude(29, '230')['state'], bib.AQUEM_DA_FONTE)

    def test_cartao_nao_e_anuncio(self):
        cartoes = [{'ads_neste_cartao': 1}] * 11 + [{'ads_neste_cartao': 2}] * 2
        self.assertEqual(bib.completude(bib.anuncios_em(cartoes), '15')['state'],
                         bib.COMPLETA_BATE_COM_A_FONTE)
        self.assertEqual(bib.completude(len(cartoes), '15')['state'], bib.AQUEM_DA_FONTE)

    def test_zero_provado_nao_e_zero_por_falta_de_leitura(self):
        self.assertEqual(bib.completude(0, None, sem_resultados=True)['state'],
                         bib.ZERO_DECLARADO)
        self.assertEqual(bib.completude(0, None)['state'], bib.FONTE_NAO_DECLARA)

    def test_url_leva_locale_e_pais_como_coisas_separadas(self):
        u = bib.url_da_pagina('123456', 'IT')
        self.assertIn('locale=en_US', u)
        self.assertIn('country=IT', u)


# ── 6. descoberta: a guarda corre na hora em que a página é achada ──────────
class ADescobertaSoPropoe(unittest.TestCase):

    def test_identidade_com_token_no_meio_nao_vira_candidata(self):
        class Porta:
            def ler(self, url, espera=15, com_cartoes=True):
                if 'id=' in url and 'q=' not in url:
                    return {'logado': 'NAO_LOGADO',
                            'url': 'https://x/?view_all_page_id=1720702718165314'}, []
                c1 = {'library_id': '1', 'links': [], 'texto':
                      'Active\nLibrary ID: 1\nInstytut Adama Mickiewicza\nSponsored\nx'}
                c2 = {'library_id': '2', 'links': [], 'texto':
                      'Active\nLibrary ID: 2\nADAMA Ltd.\nSponsored\ny'}
                return {'logado': 'NAO_LOGADO', 'resultados_declarados': '2'}, [c1, c2]
        r = anun.resolver('ADAMA', Porta())
        nomes = [p['page_name'] for p in r['pages']]
        self.assertEqual(nomes, ['ADAMA Ltd.'])
        self.assertEqual(r['pages'][0]['page_id'], '1720702718165314')
        self.assertFalse(r['pages'][0]['EM_LINHA'], 'descoberta PROPOE; nao poe na linha')


# ── 7. as frentes: medido dos livros, e o versionado bate ───────────────────
class AsFrentes(unittest.TestCase):

    def test_o_quadro_versionado_e_o_que_os_livros_produzem(self):
        with open(os.path.join(RAIZ, fr.SAIDA), encoding='utf-8') as f:
            self.assertEqual(f.read(), fr._json(fr.medir()))

    def test_doze_empresas_cinco_frentes(self):
        q = fr.medir()
        self.assertEqual(len(q['QUADRO']), 12)
        self.assertTrue(all(len(l['frentes']) == 5 for l in q['QUADRO']))

    def test_pagina_recusada_pela_guarda_nao_conta_como_na_linha(self):
        q = fr.medir()
        adama = next(l for l in q['QUADRO'] if l['empresa'] == 'ADAMA')
        ev = adama['frentes']['META_ADS']['evidencias']
        inst = next(x for x in ev if x['nome'].startswith('Instytut'))
        self.assertNotEqual(inst['degrau'], fr.NA_LINHA)

    def test_pagina_de_facebook_nao_vira_pagina_da_biblioteca(self):
        q = fr.medir()
        syn = next(l for l in q['QUADRO'] if l['empresa'] == 'Syngenta')
        cand = [x for x in syn['frentes']['META_ADS']['evidencias']
                if x.get('page_id_candidato') == '2007689772789481']
        self.assertEqual(len(cand), 1)
        self.assertEqual(cand[0]['degrau'], fr.NA_FILA)


if __name__ == '__main__':
    unittest.main()
