#!/usr/bin/env python3
"""
Provas do PASSAPORTE DA INFORMAÇÃO.

Um contrato que não é exercido contra o incidente que o gerou é uma promessa. Estes testes
exercem: os 1.005.157 caracteres de transcrição, a duplicata que atravessou duas missões,
a porta que precisa recusar, e o item que precisa poder alimentar três capacidades sem
nunca virar oportunidade.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import passaporte as pp                # noqa: E402
import passaporte_backfill as bf       # noqa: E402
import passaporte_portao as pt         # noqa: E402
import passaporte_painel as pn         # noqa: E402

REG = pp.Registro.carregar()
PS = REG.passaportes()
RECONSTRUIDO, SEM_SNAPSHOT = bf.backfill()
PORTOES = pt.avaliar(REG)


class Schema(unittest.TestCase):
    def test_todo_passaporte_tem_os_quinze_estados(self):
        for p in PS.values():
            for campo in pp.CAMPOS_DE_ESTADO:
                self.assertIn(campo, p, '%s sem %s' % (p['ITEM_ID'], campo))

    def test_todo_estado_esta_no_vocabulario_fechado(self):
        for p in PS.values():
            for campo, (permitidos, _) in pp.ESTADOS.items():
                self.assertIn(p[campo], permitidos,
                              '%s tem %s=%r fora do vocabulário'
                              % (p['ITEM_ID'], campo, p[campo]))

    def test_campos_de_identidade_e_origem_nunca_vazios(self):
        for p in PS.values():
            for campo in ('ITEM_ID', 'COLLECTION_ID', 'SOURCE_ID', 'SOURCE_FAMILY',
                          'SOURCE_REFERENCE', 'CAPTURED_AT', 'CONTENT_TYPE'):
                self.assertTrue(p[campo], '%s sem %s' % (p['ITEM_ID'], campo))

    def test_derivado_sempre_aponta_para_um_pai_que_existe(self):
        derivados = [p for p in PS.values() if p['DERIVED_FROM']]
        self.assertGreater(len(derivados), 1000)
        for p in derivados:
            self.assertTrue(p['PARENT_ITEM_ID'], '%s derivado sem pai' % p['ITEM_ID'])
            self.assertIn(p['PARENT_ITEM_ID'], PS,
                          '%s aponta para pai inexistente' % p['ITEM_ID'])

    def test_id_e_derivado_da_base_e_nao_do_caminho(self):
        for p in list(PS.values())[:200]:
            self.assertEqual(p['ITEM_ID'], pp.item_id(p['IDENTITY_BASIS']))
            self.assertFalse(p['ITEM_ID'].startswith('data/'))

    def test_as_dezesseis_capacidades_existem_e_opportunity_e_uma_delas(self):
        self.assertEqual(len(pp.CAPACIDADES), 16)
        self.assertIn('OPPORTUNITY', pp.CAPACIDADES)
        self.assertIn('ASK_SINTONIA', pp.CAPACIDADES)

    def test_todo_motivo_tem_proxima_acao(self):
        for motivo, acao in pp.MOTIVOS.items():
            self.assertTrue(acao, 'motivo %s sem NEXT_ACTION' % motivo)


class PortaFechada(unittest.TestCase):
    """REJECT_PIPELINE, nunca WARN_AND_CONTINUE."""

    def test_onze_entradas_invalidas_sao_recusadas(self):
        for nome, resultado in pt._fail_closed():
            self.assertEqual(resultado, 'RECUSADO', 'porta aberta: %s' % nome)

    def test_item_sem_identidade_nao_entra(self):
        reg = pp.Registro([], caminho=os.devnull)
        with self.assertRaises(pp.PassaporteRecusado):
            reg.admitir(identity_basis='', collection_id='C', source_id='S',
                        source_family='F', source_reference='r',
                        captured_at='2026-09-05', content_type='T', actor='t')

    def test_consumo_exige_prova(self):
        reg = pp.Registro([], caminho=os.devnull)
        iid = reg.admitir(identity_basis='X:1', collection_id='C', source_id='S',
                          source_family='F', source_reference='r',
                          captured_at='2026-09-05', content_type='T', actor='t')
        cid = reg.extrair_claims(iid, ['a'], actor='t', timestamp='2026-09-05',
                                 evidence_reference='e')[0]
        reg.rotear(iid, cid, 'SCIENCE', 'DIRECT', actor='t', timestamp='2026-09-05',
                   why='relevante')
        with self.assertRaises(pp.PassaporteRecusado):
            reg.consumir(iid, cid, 'SCIENCE', actor='t', timestamp='2026-09-05',
                         evidence_reference='')


class HistoricoImutavel(unittest.TestCase):
    def test_selo_novo_nao_apaga_selo_antigo(self):
        """Os candidatos a canal têm DOIS selos de identidade. Os dois ficam."""
        alvo = None
        for p in PS.values():
            if p['ITEM_CLASS'] == 'ORIGIN_CANDIDATE' and p['IDENTITY_STATE'] == 'PROVED':
                alvo = p
                break
        self.assertIsNotNone(alvo, 'nenhum candidato provado no acervo')
        selos = [e for e in REG.eventos_de(alvo['ITEM_ID'])
                 if e['EVENT_TYPE'] in ('IDENTITY_PROVED', 'IDENTITY_NOT_PROVED')]
        self.assertGreaterEqual(len(selos), 2)
        self.assertEqual(selos[0]['TO_STATE'], 'NOT_PROVED')   # o selo da coleta
        self.assertEqual(selos[-1]['TO_STATE'], 'PROVED')      # o selo da prova
        self.assertEqual(alvo['IDENTITY_STATE'], 'PROVED')

    def test_event_id_nunca_se_repete(self):
        ids = [e['EVENT_ID'] for e in REG.eventos]
        self.assertEqual(len(ids), len(set(ids)))

    def test_todo_evento_tem_os_dez_campos_do_modelo(self):
        for e in REG.eventos[:5000]:
            for campo in pp.CAMPOS_EVENTO:
                self.assertIn(campo, e, 'evento %s sem %s' % (e['EVENT_ID'], campo))
            self.assertEqual(e['RULE_VERSION'], pp.RULE_VERSION)

    def test_nenhum_evento_escreve_campo_que_nao_e_dele(self):
        for e in REG.eventos:
            self.assertIn(e['EVENT_TYPE'], pp.ESCRITA)

    def test_backfill_e_deterministico(self):
        outro, _ = bf.backfill()
        self.assertEqual(outro.eventos, RECONSTRUIDO.eventos)

    def test_log_gravado_contem_o_backfill_como_prefixo(self):
        n = len(RECONSTRUIDO.eventos)
        self.assertGreaterEqual(len(REG.eventos), n)
        self.assertEqual(REG.eventos[:n], RECONSTRUIDO.eventos)


class ContabilidadeFechada(unittest.TestCase):
    def test_o_total_fecha_no_acervo_inteiro(self):
        c = pp.contabilidade(PS)
        self.assertEqual(c['TOTAL_ENTERED'], sum(c['LIFECYCLE'].values()))
        self.assertEqual(c['GATE'], 'PASS')

    def test_o_total_fecha_em_cada_colecao(self):
        for k in sorted({p['COLLECTION_ID'] for p in PS.values()}):
            c = pp.contabilidade(PS, k)
            self.assertEqual(c['TOTAL_ENTERED'], sum(c['LIFECYCLE'].values()), k)
            self.assertEqual(c['GATE'], 'PASS', k)

    def test_cada_estagio_fecha(self):
        c = pp.contabilidade(PS)
        for nome, e in c['STAGES'].items():
            self.assertEqual(
                e['INPUT_TO_STAGE'],
                e['PASSED'] + e['STOPPED_WITH_REASON'] + e['PENDING'] + e['ERROR'], nome)

    def test_quem_entra_num_estagio_e_quem_passou_no_anterior(self):
        c = pp.contabilidade(PS)
        for i in range(1, len(pp.ESTAGIOS)):
            ant, atual = pp.ESTAGIOS[i - 1], pp.ESTAGIOS[i]
            self.assertEqual(c['STAGES'][atual]['INPUT_TO_STAGE'],
                             c['STAGES'][ant]['PASSED'], atual)

    def test_nenhuma_queda_sem_motivo(self):
        self.assertEqual(pp.contabilidade(PS)['UNEXPLAINED_STAGE_DROPS'], [])

    def test_item_que_nao_concluiu_tem_motivo_e_proxima_acao(self):
        for p in PS.values():
            if p['LIFECYCLE'] == 'COMPLETED':
                continue
            self.assertTrue(p['REASON_CODE'], '%s parou sem motivo' % p['ITEM_ID'])
            self.assertTrue(p['NEXT_ACTION'], '%s sem próxima ação' % p['ITEM_ID'])
            self.assertIn(p['REASON_CODE'], pp.MOTIVOS)


class Canarios(unittest.TestCase):
    def test_canario_um_os_1005157_caracteres_aparecem_e_nao_somem(self):
        tr = [p for p in PS.values() if p['CONTENT_TYPE'] == 'TRANSCRIPT']
        self.assertEqual(len(tr), 30)
        self.assertEqual(sum(p['CONTENT_CHARS'] for p in tr), 1005157)
        for p in tr:
            self.assertEqual(p['CONTENT_STATE'], 'AVAILABLE')
            self.assertNotEqual(p['CONTENT_READ_STATE'], 'READ')
            self.assertEqual(p['CURRENT_STAGE'], 'INTELLIGENCE_READING')
            self.assertEqual(p['STAGE_VERDICT'], 'PENDING')
            self.assertIn('CONTENT_NOT_PROCESSED', p['BLOCKER_CODES'])
            self.assertEqual(p['LIFECYCLE'], 'ACTIVE')

    def test_canario_um_a_divida_lista_as_trinta(self):
        f = pp.filas_de_divida(PS)
        self.assertEqual(len(f['TRANSCRIPT_AVAILABLE_NOT_READ']), 30)

    def test_canario_dois_multicapacidade_sem_funil_de_oportunidade(self):
        m = pt.canario_multicapacidade()
        self.assertEqual(m['CONTENT_READ'], 'READ')
        self.assertEqual(m['CLAIM_STATE'], 'EXTRACTED')
        self.assertIn(m['SCIENCE'], ('DIRECT', 'SUPPORTING'))
        self.assertIn(m['COMPETITOR'], ('DIRECT', 'SUPPORTING'))
        self.assertIn(m['MARKET_DEVELOPMENT'], ('DIRECT', 'SUPPORTING'))
        self.assertIn(m['OPPORTUNITY'], ('BLOCKED', 'NOT_APPLICABLE'))
        self.assertGreaterEqual(len(m['CONSUMED_BY']), 1)
        self.assertEqual(m['ORPHAN_INTELLIGENCE'], 'NO')

    def test_canario_dois_o_mesmo_padrao_existe_em_dado_real(self):
        """A sonda prova a máquina; o acervo prova que a máquina já se comporta assim."""
        reais = [p for p in PS.values()
                 if {r['CAPABILITY_ID'] for r in p['ROUTES'] if r['STATE'] == 'CONSUMED'}
                 and any(r['CAPABILITY_ID'] == 'OPPORTUNITY' and r['RELEVANCE'] == 'BLOCKED'
                         for r in p['ROUTES'])]
        self.assertGreaterEqual(len(reais), 1)
        for p in reais:
            consumidas = {r['CAPABILITY_ID'] for r in p['ROUTES'] if r['STATE'] == 'CONSUMED'}
            self.assertNotIn('OPPORTUNITY', consumidas)

    def test_a_sonda_nunca_entra_no_acervo(self):
        pt.canario_multicapacidade()
        for p in PS.values():
            self.assertNotEqual(p['COLLECTION_ID'], 'SONDA_DE_CONTRATO')
            self.assertNotEqual(p['SOURCE_FAMILY'], 'SYNTHETIC')


class ClassificadorNaoELeitura(unittest.TestCase):
    def test_varredura_lexical_nunca_conta_como_leitura(self):
        varridos = [p for p in PS.values()
                    if p['CONTENT_READ_STATE'] == 'LEXICALLY_SCANNED']
        self.assertGreater(len(varridos), 1500)
        for p in varridos:
            self.assertNotEqual(p['CURRENT_STAGE'], 'CLAIM_EXTRACTION')
            self.assertEqual(p['CLAIM_STATE'], pp.PENDING)

    def test_o_painel_separa_lido_de_varrido(self):
        r = pn.painel(PS)
        self.assertNotEqual(r['INTELIGENCIA']['CONTENT_READ'],
                            r['INTELIGENCIA']['CONTENT_LEXICALLY_SCANNED_ONLY'])
        self.assertGreater(r['INTELIGENCIA']['CONTENT_LEXICALLY_SCANNED_ONLY'],
                           r['INTELIGENCIA']['CONTENT_READ'])


class DuplicataEntreColecoes(unittest.TestCase):
    def test_o_mesmo_video_em_duas_missoes_e_um_item_com_reencontro(self):
        """48 vídeos e 79 comentários foram coletados duas vezes, por duas missões
        diferentes, e ninguém sabia. Um ITEM_ID global torna isso visível."""
        rec = [p for p in PS.values() if p['RECOLLECTED']]
        self.assertGreater(len(rec), 100)
        videos = [p for p in rec if p['CONTENT_TYPE'] == 'VIDEO'
                  and p['COLLECTION_ID'] == 'VOICE_ES']
        coments = [p for p in rec if p['CONTENT_TYPE'] == 'COMMENT'
                   and p['COLLECTION_ID'] == 'VOICE_ES']
        self.assertEqual(len(videos), 48)
        self.assertEqual(len(coments), 79)

    def test_reencontro_nao_cria_item_novo(self):
        for p in PS.values():
            capturas = [e for e in REG.eventos_de(p['ITEM_ID'])
                        if e['EVENT_TYPE'] == 'ITEM_CAPTURED']
            self.assertEqual(len(capturas), p['RECOLLECTED'] + 1, p['ITEM_ID'])


class Divida(unittest.TestCase):
    def test_as_seis_filas_existem_e_sao_derivadas(self):
        f = pp.filas_de_divida(PS)
        self.assertEqual(sorted(f), sorted([
            'CLAIMS_WITHOUT_ROUTING', 'CONTENT_AVAILABLE_NOT_READ', 'ORPHAN_INTELLIGENCE',
            'READ_WITHOUT_CLAIM', 'ROUTED_NOT_CONSUMED',
            'TRANSCRIPT_AVAILABLE_NOT_READ']))

    def test_inteligencia_valida_sem_consumidor_aparece_como_orfa(self):
        f = pp.filas_de_divida(PS)
        self.assertGreater(len(f['ORPHAN_INTELLIGENCE']), 0)
        for iid in f['ORPHAN_INTELLIGENCE']:
            self.assertEqual(PS[iid]['CONSUMPTION_STATE'], 'ORPHAN_INTELLIGENCE')
            self.assertNotEqual(PS[iid]['LIFECYCLE'], 'COMPLETED')

    def test_nenhuma_inteligencia_valida_tem_consumo_desconhecido(self):
        for p in PS.values():
            if p['CLAIM_STATE'] == 'EXTRACTED':
                self.assertNotIn(p['CONSUMPTION_STATE'], (pp.UNKNOWN, pp.PENDING))


class Painel(unittest.TestCase):
    def test_responde_onde_estao_as_informacoes_que_entraram_num_dia(self):
        r = pn.painel(PS, em='2026-08-30')
        self.assertGreater(r['COLETA']['TOTAL'], 0)
        self.assertEqual(r['COLETA']['TOTAL'],
                         r['COLETA']['PASS'] + r['COLETA']['DEFER']
                         + r['COLETA']['REJECT'] + r['COLETA']['ERROR'])
        self.assertEqual(sum(r['ONDE_ESTAO'].values()), r['COLETA']['TOTAL'])

    def test_o_painel_gravado_bate_com_o_derivado_agora(self):
        caminho = os.path.join(ROOT, 'data', 'passaporte', 'PAINEL.json')
        self.assertTrue(os.path.exists(caminho), 'painel nunca foi gerado')
        with open(caminho, encoding='utf-8') as f:
            gravado = json.load(f)
        self.assertEqual(gravado['COLETA'], pn.painel(PS)['COLETA'])
        self.assertEqual(gravado['CONSUMO'], pn.painel(PS)['CONSUMO'])


class Portoes(unittest.TestCase):
    def test_todos_os_portoes_passam(self):
        for nome, r in PORTOES.items():
            if nome.startswith('_'):
                continue
            self.assertTrue(r['PROVED'], '%s FAIL — %s' % (nome, r.get('BLOQUEIO')))

    def test_as_quatro_provas_da_missao_sao_zero(self):
        self.assertEqual(PORTOES['ITEMS_WITHOUT_PASSPORT']['VALOR'], 0)
        self.assertEqual(PORTOES['UNEXPLAINED_STAGE_DROPS']['VALOR'], 0)
        self.assertEqual(PORTOES['TRANSCRIPT_AVAILABLE_BUT_UNTRACKED']['VALOR'], 0)
        self.assertEqual(
            PORTOES['VALID_INTELLIGENCE_WITH_UNKNOWN_CONSUMPTION_STATE']['VALOR'], 0)

    def test_passport_enforcement_ativo(self):
        self.assertEqual(pt.veredito(PORTOES), 'PASS')

    def test_todo_arquivo_do_acervo_esta_declarado(self):
        classificados, orfaos = bf.inventario_do_acervo()
        self.assertEqual(orfaos, [])
        self.assertGreater(len(classificados), 150)

    def test_arquivo_novo_nao_declarado_derruba_o_portao(self):
        """A prova de que a porta é fechada: um arquivo que ninguém declarou reprova."""
        novo = os.path.join(bf.SAMPLES, 'PROVA-DE-PORTAO-NAO-DECLARADO.json')
        with open(novo, 'w', encoding='utf-8') as f:
            json.dump({'x': 1}, f)
        try:
            _, orfaos = bf.inventario_do_acervo()
            self.assertIn('data/samples/PROVA-DE-PORTAO-NAO-DECLARADO.json', orfaos)
        finally:
            os.remove(novo)


if __name__ == '__main__':
    unittest.main()
