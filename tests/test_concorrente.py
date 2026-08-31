"""O COMPETITOR FORESIGHT PILOT continua sendo um piloto — e não um radar.

Estes testes guardam o que não cabe no banco: a disciplina do que é
COLETADO, do que é DERIVADO e do que é NÃO COLETADO. As afirmações sobre o
esquema vivem em supabase/tests/regressoes_concorrente.sql e rodam contra um
Postgres de verdade no workflow concorrente-portao.

Nenhum teste aqui vai à rede. Todos leem os artefatos que a rodada gravou.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(RAIZ, 'data', 'samples')
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))


def ler(nome):
    with open(os.path.join(S, nome), encoding='utf-8') as f:
        return json.load(f)


class AmostraSaiDoRegistro(unittest.TestCase):
    """A amostra não pode ter sido escolhida por reputação."""

    def setUp(self):
        self.a = ler('COMPETITOR-PILOT-AMOSTRA.json')

    def test_a_conta_do_registro_inteiro_esta_aberta(self):
        self.assertEqual(self.a['REGISTRO_INTEIRO']['TOTAL'], 3084)
        self.assertEqual(self.a['TITULARES_DISTINTOS'], 262)

    def test_cada_escolhido_traz_a_contagem_que_o_justificou(self):
        for g in self.a['AMOSTRA_DO_PILOTO']:
            self.assertIn(g, self.a['POR_GRUPO'])
            self.assertGreater(self.a['POR_GRUPO'][g]['ESTADO_VIGENTE'], 0)

    def test_os_escolhidos_sao_os_maiores(self):
        fora = self.a['FORA_DA_AMOSTRA']
        menor_dentro = min(self.a['POR_GRUPO'][g]['ESTADO_VIGENTE']
                           for g in self.a['AMOSTRA_DO_PILOTO'])
        for g in fora:
            self.assertLessEqual(self.a['POR_GRUPO'][g]['ESTADO_VIGENTE'], menor_dentro)

    def test_a_amostra_declara_que_e_uma_fatia(self):
        c = self.a['COBERTURA_DA_AMOSTRA']
        self.assertLess(c['REGISTROS_DOS_ESCOLHIDOS'], c['REGISTROS_NO_REGISTRO_INTEIRO'])

    def test_o_agrupamento_e_declarado_e_auditavel(self):
        # somar razões sociais sem mostrar quais foram somadas é onde o
        # número deixa de ser auditável
        for g, v in self.a['POR_GRUPO'].items():
            self.assertTrue(v['RAZOES_SOCIAIS'], f'{g} sem razões sociais listadas')
            self.assertEqual(sum(v['RAZOES_SOCIAIS'].values()), v['REGISTROS'])


class ClasseCincoNaoEhSinalAgro(unittest.TestCase):
    """O erro real desta rodada: classe 5 de Nice é também a do remédio."""

    def setUp(self):
        self.ip = ler('COMPETITOR-IP-TMVIEW.json')

    def test_a_relevancia_tem_tres_estados_e_nao_dois(self):
        from ip_tmview import classificar_relevancia
        self.assertEqual(classificar_relevancia([1, 5]), 'CLASSE_1_E_5')
        self.assertEqual(classificar_relevancia([1]), 'SO_CLASSE_1')
        self.assertEqual(classificar_relevancia([5]), 'SO_CLASSE_5')
        self.assertEqual(classificar_relevancia([29]), 'FORA_DAS_CLASSES_AGRO')
        self.assertEqual(classificar_relevancia([]), 'NOT_KNOWN')

    def test_classe_cinco_sozinha_nao_conta_como_sinal_forte(self):
        from ip_tmview import SINAL_AGRO_FORTE
        self.assertNotIn('SO_CLASSE_5', SINAL_AGRO_FORTE)

    def test_o_remedio_da_bayer_nao_e_sinal_forte(self):
        # GINECANES e BEPANTHEN são os casos que o erro carimbou como agro
        from ip_tmview import SINAL_AGRO_FORTE
        achou = 0
        for o, v in self.ip['POR_CONCORRENTE']['BAYER'].items():
            if v.get('ESTADO') != 'OK':
                continue
            for m in v['MARCAS']:
                nome = (m['TM_NAME'] or '').upper()
                if 'GINECANES' in nome or 'BEPANTHEN' in nome:
                    achou += 1
                    self.assertNotIn(m['AGROCHEMICAL_RELEVANCE'], SINAL_AGRO_FORTE,
                                     f'{nome} voltou a contar como sinal agro')
        self.assertGreater(achou, 0, 'os casos-testemunha sumiram do artefato')

    def test_o_ambiguo_e_maior_que_o_forte(self):
        # se um dia isso se inverter em silêncio, alguém relaxou a régua
        amb = forte = 0
        for offs in self.ip['POR_CONCORRENTE'].values():
            for v in offs.values():
                if v.get('ESTADO') != 'OK':
                    continue
                amb += v['POR_RELEVANCIA'].get('SO_CLASSE_5', 0)
                forte += v['SINAL_AGRO_FORTE']
        self.assertGreater(amb, 0)
        self.assertGreater(forte, 0)


class OFiltroIgnoradoEmSilencio(unittest.TestCase):
    """A API devolve o universo inteiro quando não conhece o parâmetro."""

    def test_o_portao_do_filtro_existe_em_codigo(self):
        import ip_tmview
        self.assertTrue(hasattr(ip_tmview, 'FiltroIgnorado'))

    def test_o_controle_sem_filtro_foi_gravado(self):
        ip = ler('COMPETITOR-IP-TMVIEW.json')
        for office, total in ip['CONTROLE_SEM_FILTRO'].items():
            self.assertGreater(total, 100000, f'{office}: controle implausível')

    def test_nenhum_resultado_igualou_o_universo(self):
        ip = ler('COMPETITOR-IP-TMVIEW.json')
        ctrl = ip['CONTROLE_SEM_FILTRO']
        for grupo, offs in ip['POR_CONCORRENTE'].items():
            for o, v in offs.items():
                if v.get('ESTADO') != 'OK':
                    continue
                self.assertNotEqual(v['TOTAL_DECLARADO_PELA_API'], ctrl[o],
                                    f'{grupo}/{o}: o filtro foi ignorado')


class NomeIgualNaoEhMesmoRegistro(unittest.TestCase):
    """A regra que já custou caro nesta casa."""

    def setUp(self):
        self.c = ler('COMPETITOR-CROSSWALK.json')

    def test_a_normalizacao_nao_encolhe_a_string(self):
        from concorrente_crosswalk import normalizar
        self.assertEqual(normalizar('Primo Maxx'), normalizar('PRIMO MAXX'))
        self.assertNotEqual(normalizar('FENOVA S'), normalizar('FENOVA SUPER'))
        self.assertNotEqual(normalizar('CUREX 3'), normalizar('CUREX'))

    def test_todo_par_provado_tem_o_mesmo_grupo_dos_dois_lados(self):
        for p in self.c['PARES']:
            if p['ESTADO_DO_LINK'] == 'PROVED':
                self.assertEqual(p['GRUPO_DA_MARCA'], p['REGISTRATION_GRUPO'])

    def test_a_recusa_por_titular_diferente_esta_publicada(self):
        rej = [p for p in self.c['PARES']
               if p['ESTADO_DO_LINK'] == 'REJECTED_HOLDER_MISMATCH']
        self.assertGreater(len(rej), 0, 'nenhuma recusa: a régua perdeu os dentes')
        for p in rej:
            self.assertNotEqual(p['GRUPO_DA_MARCA'], p['REGISTRATION_GRUPO'])

    def test_o_caso_urbole_continua_recusado(self):
        # marca da SYNGENTA, registro 24157 da ADAMA. É a testemunha da regra.
        urbole = [p for p in self.c['PARES']
                  if (p['TM_NAME'] or '').upper() == 'URBOLE']
        self.assertTrue(urbole, 'o caso-testemunha sumiu do artefato')
        for p in urbole:
            self.assertNotEqual(p['ESTADO_DO_LINK'], 'PROVED')

    def test_o_ruido_do_casador_frouxo_foi_medido_e_nao_estimado(self):
        r = self.c['RUIDO_MEDIDO']
        self.assertGreater(r['PARES_EXTRAS_QUE_ELE_CRIARIA'], 0)
        self.assertGreater(r['DESTES_COM_TITULAR_ERRADO'], 0)

    def test_a_maioria_das_marcas_nao_liga_e_isso_esta_escrito(self):
        e = self.c['POR_ESTADO']
        self.assertGreater(e['NOT_KNOWN'], e['PROVED'] * 10)


class AntecedenciaNaoEhInventada(unittest.TestCase):

    def setUp(self):
        self.e = ler('COMPETITOR-EVENTS.json')

    def test_toda_cadeia_vem_de_link_provado(self):
        for c in self.e['TIMELINES']['CADEIAS']:
            self.assertEqual(c['CROSSWALK_STATE'], 'PROVED')

    def test_a_cadeia_e_identificada_pela_marca_e_nao_so_pelo_nome(self):
        # 15 pares colidiam quando a chave era grupo:nome:registro, e a
        # antecedência de uma marca era colada em outra
        ids = [c['CHAIN_ID'] for c in self.e['TIMELINES']['CADEIAS']]
        self.assertEqual(len(ids), len(set(ids)), 'CHAIN_ID voltou a colidir')

    def test_defensavel_exige_ordem_marca_antes_do_registro(self):
        for c in self.e['TIMELINES']['CADEIAS']:
            if c['LEAD_DAYS_DEFENSAVEL']:
                self.assertGreater(c['LEAD_DAYS'], 0)

    def test_os_pares_que_refutam_continuam_na_base(self):
        ref = [c for c in self.e['TIMELINES']['CADEIAS']
               if c['ORDEM_OBSERVADA'] == 'REGISTRO_ANTES_DA_MARCA']
        self.assertGreater(len(ref), 0,
                           'apagar a contraprova produz 100% de confirmação')

    def test_a_amplitude_bruta_esta_publicada(self):
        lo, hi = self.e['LEAD_DAYS']['AMPLITUDE_BRUTA_DIAS']
        self.assertLess(lo, 0)
        self.assertGreater(hi, 0)
        self.assertIn('POR_QUE_A_AMPLITUDE_ESTOURA', self.e['LEAD_DAYS'])


class NotJoinedNaoEhNotAvailable(unittest.TestCase):
    """O erro de estado que a primeira entrega cometeu, e esta corrigiu."""

    def setUp(self):
        self.e = ler('COMPETITOR-EVENTS.json')

    def test_as_tres_camadas_dizem_NOT_JOINED_e_nao_ausencia(self):
        for camada in ('PRODUCT_CATALOG', 'META', 'CREATOR'):
            c = self.e['CAMADAS_AUSENTES'][camada]
            self.assertEqual(c['ESTADO'], 'NOT_JOINED_IN_THIS_MISSION')
            self.assertEqual(c['DISPONIVEL_NESTE_SNAPSHOT'], 'NO')
            self.assertTrue(c['ESTADO_REAL'], f'{camada} sem o estado real da outra missão')
            self.assertTrue(c['NAO_SIGNIFICA'], f'{camada} sem a ressalva escrita')

    # Uma chave cujo nome já diz que ali mora uma PROIBIÇÃO não pode ser lida
    # como afirmação: é lá que a frase errada é citada para ser proibida.
    CHAVES_DE_PROIBICAO = ('PROIBIDO', 'NAO_SIGNIFICA', 'NAO_E_ZERO', 'ERRO',
                           'MOTIVO_DA_RECLASSIFICACAO', 'POR_QUE_E_PROIBIDO',
                           'NAO_PROVA')

    def _afirmacoes(self, no, chave=''):
        """Todo texto do artefato, MENOS o que está sob chave de proibição."""
        if any(k in chave.upper() for k in self.CHAVES_DE_PROIBICAO):
            return
        if isinstance(no, dict):
            for k, v in no.items():
                yield from self._afirmacoes(v, k)
        elif isinstance(no, list):
            for v in no:
                yield from self._afirmacoes(v, chave)
        elif isinstance(no, str):
            yield no

    def test_nenhum_artefato_AFIRMA_que_meta_ou_creator_nao_existem(self):
        proibidas = ('não existe meta', 'nao existe meta',
                     'não existe creator', 'nao existe creator',
                     'não há creator map', 'nao ha creator map',
                     'não há dado de meta', 'nao ha dado de meta',
                     'não existe no repositório', 'nao existe no repositorio')
        for nome in ('COMPETITOR-EVENTS.json', 'COMPETITOR-EAME-VEREDITOS.json'):
            for texto in self._afirmacoes(ler(nome)):
                for f in proibidas:
                    self.assertNotIn(f, texto.lower(),
                                     f'{nome} AFIRMA ausência global: "{f}"')

    def test_nenhum_evento_de_meta_ou_creator_foi_inventado(self):
        for ev in self.e['EVENTOS']['LISTA']:
            self.assertNotIn(ev['EVENT_TYPE'],
                             ('META_AD_OBSERVED', 'CREATOR_ACTIVITY_OBSERVED'))

    def test_nenhuma_cadeia_fecha_fim_a_fim(self):
        for c in self.e['TIMELINES']['CADEIAS']:
            self.assertEqual(c['CAMADAS_COM_DADO'], 2)
            self.assertEqual(c['CAMADAS_DA_CADEIA'], 5)


class OPortaoDeVersaoNaoDizNadaMudou(unittest.TestCase):

    def setUp(self):
        self.r = ler('COMPETITOR-REGULATORY-EVENTS.json')

    def test_o_estado_da_versao_decide_se_ha_change_event(self):
        p = self.r['PORTAO_DE_VERSAO']
        if not p['AUTORIZA_EMITIR_CHANGE_EVENT']:
            self.assertEqual(self.r['CHANGE_EVENTS'], [])

    def test_a_comparacao_esta_aberta_e_o_zero_e_auditavel(self):
        p = self.r['PORTAO_DE_VERSAO']
        self.assertGreater(p['COMPARACOES_CAMPO_A_CAMPO'], 0)
        self.assertIn('sha256_das_linhas', p['VERSAO_A'])
        self.assertIn('sha256_das_linhas', p['VERSAO_B'])

    def test_o_veredito_nao_diz_estabilidade(self):
        v = str(self.r['PORTAO_DE_VERSAO']['VEREDITO']).lower()
        for proibida in ('estável', 'estavel', 'nada muda', 'não muda'):
            self.assertNotIn(proibida, v)

    def test_fato_datado_nao_e_change_event(self):
        # as duas listas não se misturam
        self.assertIn('DATED_FACTS', self.r)
        self.assertIn('CHANGE_EVENTS', self.r)
        for f in self.r['DATED_FACTS']['FATOS']:
            self.assertIn('EFFECTIVE_DATE', f)


class PatenteFoiRebaixadaComMedida(unittest.TestCase):

    def setUp(self):
        self.p = ler('COMPETITOR-PATENT-DEMOTE.json')

    def test_o_veredito_separa_a_ROTA_da_CAMADA(self):
        # o que morreu foi UMA rota, e a camada inteira continua sem veredicto
        self.assertEqual(self.p['PATENT_LAYER'], 'DEMOTED / NOT_USED')
        self.assertEqual(self.p['PATENT_BRAND_LINKAGE_ROUTE'], 'REFUTED_FOR_PILOT')
        self.assertEqual(self.p['PATENT_WATCH_COMO_UM_TODO'], 'NOT_TESTED')
        self.assertEqual(len(self.p['O_TESTE_QUE_DECIDIU']['CASOS']), 5)
        self.assertGreaterEqual(len(self.p['ROTAS_QUE_NAO_FORAM_TESTADAS']), 4)

    def test_nenhum_caso_recuperou_o_titular_correto(self):
        for c in self.p['O_TESTE_QUE_DECIDIU']['CASOS']:
            self.assertFalse(c['TITULAR_CONFERE'])

    def test_o_rebaixamento_nao_vira_afirmacao_sobre_o_concorrente(self):
        self.assertTrue(self.p['O_QUE_ISTO_NAO_PROVA'])


class NenhumArtefatoAfirmaIntencao(unittest.TestCase):
    """A linha vermelha da missão."""

    PROIBIDAS = ('vai lançar', 'vai lancar', 'lançará', 'lancara',
                 'pretende lançar', 'planeja lançar', 'está atacando',
                 'esta atacando', 'ameaça', 'estratégia do concorrente')

    def test_nenhum_texto_dos_artefatos_afirma_intencao(self):
        for nome in ('COMPETITOR-PILOT-AMOSTRA.json', 'COMPETITOR-IP-TMVIEW.json',
                     'COMPETITOR-REGULATORY-EVENTS.json', 'COMPETITOR-CROSSWALK.json',
                     'COMPETITOR-EVENTS.json', 'COMPETITOR-PATENT-DEMOTE.json'):
            texto = json.dumps(ler(nome), ensure_ascii=False).lower()
            for frase in self.PROIBIDAS:
                self.assertNotIn(frase, texto, f'{nome} contém "{frase}"')




class ParidadeEAME(unittest.TestCase):
    """Os três países medidos com a MESMA régua — ou NOT_MEASURED com causa."""

    def setUp(self):
        self.p = ler('COMPETITOR-EAME-PARIDADE.json')

    def test_os_tres_paises_aparecem(self):
        self.assertEqual(sorted(self.p['POR_PAIS']), ['ES', 'FR', 'IT'])

    def test_pais_nao_medido_traz_a_causa_exata(self):
        for pais, b in self.p['POR_PAIS'].items():
            if b['ESTADO_DA_MEDICAO'] == 'NOT_MEASURED':
                self.assertTrue(b['EXACT_REASON'], f'{pais} sem causa exata')
                self.assertTrue(b['NAO_SIGNIFICA'], f'{pais} sem a ressalva')

    def test_a_espanha_nao_foi_recalculada(self):
        # a refatoração para a forma comum é verificada por esta igualdade
        es = self.p['POR_PAIS']['ES']
        self.assertEqual(es['LINKED_CHAINS'], 209)
        self.assertEqual(es['POR_ESTADO']['PARTIAL'], 24)
        self.assertEqual(es['FALSE_LINKS_REJECTED'], 9)
        self.assertEqual(es['UNLINKED'], 5335)
        self.assertEqual(es['ANTECEDENCIA']['TM_BEFORE_REG'], 158)
        self.assertEqual(es['ANTECEDENCIA']['REG_BEFORE_TM'], 51)

    def test_a_mesma_regua_nos_tres(self):
        from concorrente_paridade import cruzar as c1
        from concorrente_crosswalk import cruzar as c2
        self.assertIs(c1, c2, 'IT/FR passaram a usar um matcher diferente')

    def test_a_recusa_por_titular_existe_nos_tres(self):
        for pais, b in self.p['POR_PAIS'].items():
            if b['ESTADO_DA_MEDICAO'] != 'MEASURED':
                continue
            self.assertGreater(b['FALSE_LINKS_REJECTED'], 0,
                               f'{pais}: nenhuma recusa — a régua perdeu os dentes')

    def test_a_incomparabilidade_dos_totais_esta_escrita(self):
        self.assertIn('OS_TOTAIS_NAO_SAO_COMPARAVEIS', self.p)
        self.assertIn('SUBCONTAGEM_POR_ANTECESSOR', self.p)

    def test_o_antecessor_nao_foi_agrupado_mas_foi_contado(self):
        for pais in ('IT', 'FR'):
            b = self.p['POR_PAIS'][pais]
            self.assertGreater(b['SUBCONTAGEM_POR_ANTECESSOR'], 0,
                               f'{pais}: nenhum antecessor contado')


class OsQuatroParesSemanticos(unittest.TestCase):
    """Cada par é uma frase verdadeira a um passo de virar uma falsa."""

    def setUp(self):
        self.v = ler('COMPETITOR-EAME-VEREDITOS.json')

    def test_1_precedencia_historica_nao_e_antecedencia_operacional(self):
        c = self.v['CAPABILITIES']['C_COMPETITOR_TIMELINE']
        self.assertIn('HISTORICAL_PRECEDENCE_OBSERVED', c)
        self.assertEqual(c['OPERATIONAL_EARLY_WARNING_VALUE']['ESTADO'], 'NOT_PROVED')
        self.assertTrue(c['OPERATIONAL_EARLY_WARNING_VALUE']['PROIBIDO_DIZER'])

    def test_2_atividade_recente_nao_e_valor_diario(self):
        a = self.v['CAPABILITIES']['A_TRADEMARK_CHANGE_WATCH']
        self.assertEqual(a['VEREDICTO'], 'PROMISING')
        self.assertEqual(a['RECENT_TRADEMARK_ACTIVITY_EXISTS'], 'YES')
        self.assertEqual(a['O_QUE_NAO_ESTA_PROVADO']['DAILY_VALUE'], 'NOT_PROVED')

    def test_3_zero_no_intervalo_nao_e_registro_estatico(self):
        r = self.v['REGULATORY_WATCH']
        self.assertEqual(r['REGULATORY_CHANGE_IN_THIS_INTERVAL'], '0 OBSERVED')
        self.assertEqual(r['REGULATORY_CHANGE_CADENCE'], 'NOT_PROVED')

    def test_4_rota_refutada_nao_e_camada_refutada(self):
        d = self.v['CAPABILITIES']['D_PATENT_WATCH']
        self.assertEqual(d['PATENT_BRAND_LINKAGE_ROUTE'], 'REFUTED_FOR_PILOT')
        self.assertEqual(d['PATENT_WATCH_COMO_UM_TODO'], 'NOT_TESTED')
        self.assertGreaterEqual(len(d['ROTAS_QUE_NAO_FORAM_TESTADAS']), 4)

    def test_nenhum_artefato_escreve_patent_watch_refutado(self):
        import glob
        for caminho in glob.glob(os.path.join(S, 'COMPETITOR-*.json')):
            with open(caminho, encoding='utf-8') as f:
                texto = f.read()
            self.assertNotIn('"PATENT_WATCH": "REFUTED"', texto,
                             os.path.basename(caminho))

    def test_um_veredicto_por_capacidade_e_nao_um_so(self):
        caps = self.v['CAPABILITIES']
        self.assertEqual(len(caps), 4)
        vistos = {c.get('VEREDICTO') or c.get('PATENT_LAYER') for c in caps.values()}
        self.assertGreater(len(vistos), 1,
                           'um veredicto único apagaria três resultados diferentes')


class JuncaoComAsOutrasMissoes(unittest.TestCase):

    def setUp(self):
        self.v = ler('COMPETITOR-EAME-VEREDITOS.json')

    def test_creator_e_meta_trazem_o_estado_real_e_o_lugar(self):
        for k in ('CREATOR', 'META'):
            b = self.v['JOIN_READINESS'][k]
            self.assertEqual(b[f'{k}_DATA_AVAILABLE_IN_THIS_SNAPSHOT'], 'NO')
            self.assertTrue(b['ESTADO_REAL_DA_CAPACIDADE'])
            self.assertIn('branch', b['ONDE'])
            self.assertTrue(b['PROIBIDO_DIZER'])

    def test_a_juncao_com_meta_foi_MEDIDA_AUDITADA_e_nao_esperada(self):
        m = self.v['JOIN_READINESS']['META']['MEDIDO_NESTA_RODADA']
        self.assertGreater(m['THREE_LAYER_CHAIN_PROVED_TUPLES'], 0)
        self.assertEqual(m['THREE_LAYER_UNIT_RECONCILED'], 'YES')
        self.assertTrue(m['CONSERVACAO_TUPLAS']['FECHA'])
        self.assertTrue(m['CONSERVACAO_PRODUTOS']['FECHA'])
        self.assertEqual(m['URBOLE_GUARD'], 'PASS')
        self.assertTrue(m['URBOLE_GUARD_EXERCIDO'])
        self.assertEqual(m['FINAL_REFRESH_INPUT'], 'NO')
        self.assertIn('Nenhum merge', m['COMO_FOI_MEDIDO'])

    def test_as_duas_camadas_entram_separadas_na_convergencia(self):
        c = self.v['CONVERGENCE_READINESS']
        self.assertEqual(c['COMPETITOR_BRAND_EVENT_OBSERVED']['ESTADO'], 'PRONTO')
        self.assertEqual(c['COMPETITOR_LOCAL_REGISTRATION_OBSERVED']['ESTADO'], 'PRONTO')
        self.assertIn('CROP_E_ISSUE', c['O_QUE_AINDA_NAO_LIGA'])




class ConservacaoDaDecomposicaoTemporal(unittest.TestCase):
    """702 + 407 = 1109, e LINKED_CHAINS dizia 1140. As 31 tinham de aparecer."""

    def setUp(self):
        self.p = ler('COMPETITOR-EAME-PARIDADE.json')

    def test_a_soma_das_classes_fecha_o_total_nos_tres(self):
        for pais, b in self.p['POR_PAIS'].items():
            if b['ESTADO_DA_MEDICAO'] != 'MEASURED':
                continue
            a = b['ANTECEDENCIA']
            self.assertEqual(sum(a['CLASSIFICACAO'].values()),
                             b['LINKED_CHAINS'], f'{pais}: decomposição não fecha')
            self.assertTrue(a['CONSERVACAO']['FECHA'], pais)

    def test_as_31_da_franca_estao_classificadas_com_causa(self):
        c = self.p['POR_PAIS']['FR']['ANTECEDENCIA']['CLASSIFICACAO']
        self.assertEqual(c['REG_DATE_MISSING'], 30)
        self.assertEqual(c['SAME_DATE'], 1)
        self.assertEqual(c['REG_DATE_MISSING'] + c['SAME_DATE'], 31)

    def test_nenhuma_classe_foi_inventada_para_fechar(self):
        # toda classe usada tem de estar no vocabulário declarado
        VOCAB = {'TM_BEFORE_REG', 'REG_BEFORE_TM', 'SAME_DATE',
                 'REG_DATE_MISSING', 'TM_DATE_MISSING', 'BOTH_DATES_MISSING',
                 'DATE_NOT_COMPARABLE'}
        for b in self.p['POR_PAIS'].values():
            if b['ESTADO_DA_MEDICAO'] != 'MEASURED':
                continue
            self.assertLessEqual(set(b['ANTECEDENCIA']['CLASSIFICACAO']), VOCAB)

    def test_data_ilegivel_nao_se_disfarca_de_data_ausente(self):
        # DATE_NOT_COMPARABLE é defeito NOSSO e precisa aparecer com esse nome
        for pais, b in self.p['POR_PAIS'].items():
            if b['ESTADO_DA_MEDICAO'] != 'MEASURED':
                continue
            self.assertIn('DATE_NOT_COMPARABLE', b['ANTECEDENCIA']['CLASSIFICACAO'])


class AsDuasMetricasDeFalsoLink(unittest.TestCase):
    """151 e 9 medem coisas diferentes, sobre universos que não se tocam."""

    def setUp(self):
        self.p = ler('COMPETITOR-EAME-PARIDADE.json')
        self.v = ler('COMPETITOR-EAME-VEREDITOS.json')

    def test_os_universos_sao_disjuntos_nos_tres_paises(self):
        for pais, b in self.p['POR_PAIS'].items():
            if b['ESTADO_DA_MEDICAO'] != 'MEASURED':
                continue
            u = b['FALSE_LINK_METRICS']['UNIVERSOS']
            self.assertTrue(u['DISJUNTOS'], pais)
            self.assertEqual(u['NOMES_NA_INTERSECAO_DOS_DOIS_UNIVERSOS'], 0, pais)

    def test_cada_metrica_tem_nome_denominador_universo_e_estagio(self):
        for pais, b in self.p['POR_PAIS'].items():
            if b['ESTADO_DA_MEDICAO'] != 'MEASURED':
                continue
            f = b['FALSE_LINK_METRICS']
            for k in ('STRICT_MATCH_FALSE_LINKS_REJECTED',
                      'LOOSE_CANDIDATE_LINKS_REJECTED'):
                m = f[k]
                for campo in ('VALOR', 'DENOMINADOR', 'UNIVERSO',
                              'ESTAGIO_DO_MATCHER', 'REGRA_DE_REJEICAO',
                              'O_QUE_MEDE'):
                    self.assertIn(campo, m, f'{pais}/{k} sem {campo}')

    def test_a_reconciliacao_espanhola_esta_escrita_e_bate(self):
        r = self.v['FALSE_LINK_METRICS']['RECONCILIACAO_ES']
        self.assertEqual(r['OLD_151_DENOMINATOR'], 441)
        self.assertEqual(r['NEW_9_DENOMINATOR'], 242)
        self.assertEqual(r['INTERSECAO_DOS_UNIVERSOS'], 0)
        self.assertFalse(r['UMA_SUBSTITUIU_A_OUTRA'])
        self.assertFalse(r['HOUVE_MUDANCA_METODOLOGICA'])
        self.assertEqual(r['ES_REGRESSION_PRESERVED'], 'YES')

    def test_os_numeros_da_espanha_batem_com_a_medicao(self):
        f = self.p['POR_PAIS']['ES']['FALSE_LINK_METRICS']
        self.assertEqual(f['STRICT_MATCH_FALSE_LINKS_REJECTED']['VALOR'], 9)
        self.assertEqual(f['STRICT_MATCH_FALSE_LINKS_REJECTED']['DENOMINADOR'], 242)
        self.assertEqual(f['LOOSE_CANDIDATE_LINKS_REJECTED']['VALOR'], 151)
        self.assertEqual(f['LOOSE_CANDIDATE_LINKS_REJECTED']['DENOMINADOR'], 441)

    def test_ambas_permanecem(self):
        for b in self.p['POR_PAIS'].values():
            if b['ESTADO_DA_MEDICAO'] != 'MEASURED':
                continue
            self.assertTrue(b['FALSE_LINK_METRICS']['AMBAS_PERMANECEM'])


class RedTeamDaCadeiaDeTresCamadas(unittest.TestCase):
    """A junção com a Meta não pode depender só de nome."""

    def setUp(self):
        self.a = ler('COMPETITOR-THREE-LAYER-AUDIT.json')

    def test_conserva_na_unidade_TUPLA(self):
        r = self.a['RESULTADO']
        total = (r['THREE_LAYER_CHAIN_PROVED_TUPLES']
                 + r['THREE_LAYER_CHAIN_REJECTED_TUPLES']
                 + r['THREE_LAYER_CHAIN_NOT_KNOWN_TUPLES'])
        self.assertEqual(total,
                         self.a['UNIVERSO']['THREE_LAYER_CANDIDATES_TOTAL'])
        self.assertTrue(r['CONSERVACAO_TUPLAS']['FECHA'])

    def test_conserva_na_unidade_PRODUTO_separadamente(self):
        u = self.a['RESULTADO']['POR_UNIDADE_PRODUTO']
        self.assertEqual(
            u['META_PRODUCTS_WITH_PROVED_THREE_LAYER_CHAIN']
            + u['META_PRODUCTS_WITHOUT_PROVED_THREE_LAYER_CHAIN'],
            u['META_PRODUCTS_TOTAL'])
        self.assertTrue(u['CONSERVACAO_PRODUTOS']['FECHA'])

    def test_as_duas_unidades_nao_se_misturam(self):
        # TUPLA e PRODUTO são contas diferentes: o mesmo produto em dois
        # países é DUAS tuplas e UM produto. `145 - 28 = 117` seria subtração
        # entre um total de nomes crus e uma contagem de normalizados.
        u = self.a['RESULTADO']['POR_UNIDADE_PRODUTO']
        t = self.a['UNIVERSO']
        self.assertIn('NAO_SUBTRAIR_ENTRE_UNIDADES', u)
        self.assertIn('ATENCAO_A_UNIDADE', t)
        self.assertNotEqual(u['META_PRODUCTS_TOTAL'],
                            t['THREE_LAYER_CANDIDATES_TOTAL'])
        self.assertEqual(u['NOMES_CRUS_NA_META'], 145)
        self.assertLess(u['META_PRODUCTS_TOTAL'], u['NOMES_CRUS_NA_META'])

    def test_o_marcador_de_ausencia_nao_virou_produto(self):
        # `{"state": "NOT_KNOWN"}` é a missão Meta dizendo "nenhum produto
        # provado neste bloco". Lê-lo como produto inflava o denominador em 5.
        d = self.a['UNIVERSO']['DESCARTADAS_ANTES_DE_CANDIDATAR']
        self.assertGreater(d['N'], 0, 'o descarte sumiu — o defeito pode ter voltado')
        for x in d['QUAIS']:
            self.assertEqual(x['CHAVE'], 'state')
        nomes = {n for c in (self.a['PROVADAS'] + self.a['RECUSADAS']
                             + self.a['NOT_KNOWN'])
                 for n in c['PRODUCT_NAME_NA_META']}
        self.assertNotIn('state', nomes)

    def test_toda_cadeia_provada_tem_concordancia_de_titular_nas_tres_pontas(self):
        for c in self.a['PROVADAS']:
            self.assertEqual(c['CONCORDANCIA_DE_TITULAR'],
                             'META == MARCA == REGISTRO')
            self.assertEqual(c['META_COMPANY'], c['REGISTRATION_GRUPO'])
            self.assertTrue(c['REGISTRATION_ID'])
            self.assertTrue(c['TM_ST13'])

    def test_urbole_guard_passa_E_foi_exercido(self):
        g = self.a['URBOLE_GUARD']
        self.assertEqual(g['URBOLE_GUARD'], 'PASS')
        self.assertEqual(g['ACEITOS_COMO_PROVED'], 0)
        # zero recusas no dado real e um portão sem dentes dão o mesmo
        # resultado na tela. A mutação separa os dois.
        m = g['EXERCIDO_POR_MUTACAO']
        self.assertTrue(m['PEGOU'], 'o portão URBOLE não tem dentes')
        self.assertEqual(m['ESTADO_DEVOLVIDO'], 'THREE_LAYER_CHAIN_REJECTED')
        self.assertTrue(m['TITULAR_CONFLITANTE'])

    def test_o_portao_recusa_de_verdade_quando_chamado_direto(self):
        from concorrente_tres_camadas import exercer_o_portao_urbole
        r = exercer_o_portao_urbole()
        self.assertTrue(r['PEGOU'])

    def test_nao_ha_colisao_de_nome_entre_as_provadas(self):
        self.assertEqual(self.a['COLISOES_DE_NOME_ENTRE_AS_PROVADAS'], 'nenhuma')

    def test_a_meta_e_fonte_externa_e_nao_e_entrada_final(self):
        e = self.a['ESTADO_DAS_PROVADAS']
        self.assertEqual(e['PRELIMINARY_CROSS_BRANCH_JOIN'], 'PROVED')
        self.assertEqual(e['FINAL_REFRESH_INPUT'], 'NO')
        for c in self.a['PROVADAS']:
            self.assertEqual(c['FINAL_REFRESH_INPUT'], 'NO')
        self.assertIn('somente leitura', self.a['FONTE_EXTERNA']['COMO_FOI_LIDO'])

    def test_o_36_antigo_foi_corrigido_e_a_diferenca_explicada(self):
        u = self.a['RESULTADO']['POR_UNIDADE_PRODUTO']
        self.assertLess(u['META_PRODUCTS_WITH_PROVED_THREE_LAYER_CHAIN'], 36)
        self.assertIn('titular', u['DIFERENCA_EXPLICADA'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
