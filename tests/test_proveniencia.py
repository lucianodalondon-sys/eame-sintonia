# -*- coding: utf-8 -*-
"""P0, P1, P5 e P6 — o que a coleta precisa saber provar antes de escalar.

Cada teste aqui existe por um defeito medido, nao por simetria:
  · RUN_ID que nao resolvia para nada fora do repositorio;
  · execucao passada sem hora, sustentando afirmacao de ordem;
  · SUCCEEDED da plataforma com zero itens contado como sucesso;
  · auditoria lendo arvore em movimento.
"""
import json, os, re, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import proveniencia as pv   # noqa: E402
import auditoria as au      # noqa: E402

SAMPLES = os.path.join(ROOT, 'data', 'samples')


def amostra(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


class TestRunManifest(unittest.TestCase):

    def setUp(self):
        self.runs = pv.carregar()

    def test_existe_manifesto_com_execucoes(self):
        self.assertGreater(len(self.runs), 0)

    def test_todo_run_tem_todos_os_campos_do_contrato(self):
        for rid, r in self.runs.items():
            self.assertEqual(set(), set(pv.CAMPOS_RUN) - set(r), f'{rid} incompleto')

    def test_campo_desconhecido_e_not_preserved_e_nunca_ausente(self):
        for rid, r in self.runs.items():
            for c in pv.CAMPOS_RUN:
                self.assertIsNot(r[c], None, f'{rid}.{c} virou None em vez de NOT_PRESERVED')

    def test_o_run_id_resolve(self):
        # o defeito que este arquivo fecha: o rotulo agrupava e nao resolvia
        for rid in self.runs:
            m = pv.resolver(rid)
            self.assertIsNotNone(m)
            self.assertEqual(rid, m['RUN_ID'])

    def test_content_chega_ao_manifesto_pelo_run_id(self):
        v = amostra('ES-T8-001-videos.json')
        rid = v['VIDEOS'][0]['RUN_ID']
        m = pv.resolver(rid)
        self.assertIsNotNone(m, 'o RUN_ID de um video nao resolve para manifesto')
        for c in ('ACTOR', 'INPUT', 'EVIDENCE_PATH', 'RAW_EVIDENCE_STATE'):
            self.assertIn(c, m)

    def test_nenhum_token_no_manifesto(self):
        bruto = json.dumps(self.runs, ensure_ascii=False)
        self.assertIsNone(pv.TOKEN.search(bruto), 'credencial gravada no manifesto')

    def test_status_e_raw_state_dentro_do_contrato(self):
        for rid, r in self.runs.items():
            self.assertIn(r['STATUS'], pv.STATUS_RUN, rid)
            self.assertIn(r['RAW_EVIDENCE_STATE'], pv.ESTADOS_RAW, rid)

    def test_gravar_recusa_status_fora_do_contrato(self):
        r = pv.novo_run('X', STATUS='OTIMO', RAW_EVIDENCE_STATE='PRESERVED')
        with self.assertRaises(ValueError):
            pv.gravar([r], captured_at='2026-08-29')

    def test_novo_run_recusa_campo_fora_do_contrato(self):
        with self.assertRaises(KeyError):
            pv.novo_run('X', CAMPO_INVENTADO=1)

    def test_checar_token_barra_credencial(self):
        with self.assertRaises(ValueError):
            pv.novo_run('X', QUERY='apify_api_' + 'a' * 30)


class TestSucessoComZeroItensNaoEhSucesso(unittest.TestCase):
    """Medido: o ator devolveu SUCCEEDED, exitCode limpo e ZERO itens, com
    statusMessage 'free user run limit reached'."""

    def test_a_execucao_degradada_esta_registrada_como_partial(self):
        runs = pv.carregar()
        zero = [r for r in runs.values()
                if r['ITEM_COUNT_RAW'] == 0 and r['RAW_EVIDENCE_STATE'] == 'PRESERVED']
        self.assertTrue(zero, 'nenhuma execucao de zero item registrada — o caso some do registro')
        for r in zero:
            self.assertEqual('PARTIAL', r['STATUS'],
                             'SUCCEEDED com zero itens nao pode virar SUCCESS')
            self.assertIn('ZERO', str(r['ERROR']))

    def test_dataset_vazio_ainda_e_evidencia(self):
        runs = pv.carregar()
        for r in runs.values():
            if r['ITEM_COUNT_RAW'] == 0 and r['STATUS'] != 'FAILED':
                self.assertEqual('PRESERVED', r['RAW_EVIDENCE_STATE'],
                                 'vazio preservado prova que a rota devolveu nada; '
                                 'NOT_PRESERVED diria que perdemos o bruto')


class TestOrdemExigeHoraMedida(unittest.TestCase):
    """P6 — a auditoria derrubou 'o YouTube veio antes do LinkedIn'."""

    def test_execucoes_passadas_nao_sustentam_ordem(self):
        runs = pv.carregar()
        a = runs.get('ES-T8-001-2026-08-29-a')
        b = runs.get('ES-T8-002-2026-08-29-a')
        estado, motivo = pv.ordem(a, b)
        self.assertEqual('NAO_DIZIVEL', estado,
                         'sem STARTED_AT/FINISHED_AT medidos, ordem nao e afirmavel')
        self.assertTrue(motivo)

    # A LEI NÃO MUDOU. MUDOU O ATALHO QUE IDENTIFICAVA A PORTA ANTIGA.
    #
    # A versão anterior separava execução velha de nova por PREFIXO DO NOME:
    # `not RUN_ID.startswith('GATE-TEST')`. Funcionava porque, naquele momento, as únicas
    # execuções vindas da porta nova se chamavam `GATE-TEST-*`.
    #
    # As 12 execuções do piloto de sensores vieram da MESMA porta nova — capturam
    # `startedAt` da plataforma E gravam `OUTPUT_WRITTEN_AT` — e não se chamam GATE-TEST.
    # O atalho as classificou como antigas, e o teste quebrou apontando para dado correto.
    #
    #     CONVENÇÃO DE NOME NÃO É PROPRIEDADE DO DADO.
    #
    # O discriminador real já existe e o portão já o usa: `CAPTURE_METHOD`. A lei segue
    # idêntica e segue asseverada — hora de escrita nunca vira hora de execução na porta
    # ANTIGA, que é onde a hora de execução nunca foi medida. E entra a asserção inversa,
    # que antes não existia.
    PORTA_NOVA = 'POST /acts/{actor}/runs?waitForFinish'

    def test_hora_de_escrita_nao_e_hora_de_execucao(self):
        runs = pv.carregar()
        antigas = [r for r in runs.values()
                   if self.PORTA_NOVA not in str(r['CAPTURE_METHOD'])]
        com_escrita = [r for r in antigas if r['OUTPUT_WRITTEN_AT'] != pv.NOT_PRESERVED]
        self.assertTrue(com_escrita, 'a hora de escrita foi medida e precisa estar guardada')
        for r in com_escrita:
            self.assertEqual(pv.NOT_PRESERVED, r['STARTED_AT'],
                             'hora de escrita nao pode ser promovida a hora de execucao')

    def test_porta_nova_mede_as_duas_horas_de_fontes_diferentes(self):
        """O contraponto: quem passa pela porta nova TEM as duas, e elas não se confundem.

        Sem esta asserção, o teste acima passaria num sistema que simplesmente parasse de
        gravar `STARTED_AT` — o jeito mais fácil de nunca promover hora de escrita é não
        ter hora de execução nenhuma.
        """
        runs = pv.carregar()
        novas = [r for r in runs.values()
                 if self.PORTA_NOVA in str(r['CAPTURE_METHOD'])
                 and r['STATUS'] != 'FAILED']
        self.assertTrue(novas, 'nenhuma execucao pela porta nova para verificar')
        for r in novas:
            self.assertNotEqual(pv.NOT_PRESERVED, r['OUTPUT_WRITTEN_AT'],
                                'porta nova sem hora de escrita: %s' % r['RUN_ID'])
            self.assertNotEqual(r['STARTED_AT'], r['OUTPUT_WRITTEN_AT'],
                                'as duas horas ficaram identicas em %s — sinal de que uma '
                                'foi copiada da outra' % r['RUN_ID'])

    def test_execucao_nova_sustenta_ordem(self):
        runs = pv.carregar()
        novas = [r for r in runs.values()
                 if r['STARTED_AT'] != pv.NOT_PRESERVED and r['FINISHED_AT'] != pv.NOT_PRESERVED]
        self.assertGreaterEqual(len(novas), 2,
                                'sem duas execucoes com hora medida, o portao de timestamp '
                                'nao foi provado — so afirmado')
        novas.sort(key=lambda r: r['STARTED_AT'])
        ok, motivo = pv.pode_afirmar_ordem(novas[0], novas[-1])
        self.assertTrue(ok, motivo)
        self.assertIn(pv.ordem(novas[0], novas[-1])[0], ('BEFORE', 'AFTER', 'OVERLAPS'))

    def test_ordem_recusa_execucao_sem_manifesto(self):
        ok, motivo = pv.pode_afirmar_ordem(None, {'RUN_ID': 'x'})
        self.assertFalse(ok)


class TestRawEvidence(unittest.TestCase):
    """P5 — RAW nunca e substituido pelo normalizado."""

    def test_toda_rota_paga_declara_estado_do_bruto(self):
        for rid, r in pv.carregar().items():
            self.assertIn(r['RAW_EVIDENCE_STATE'], pv.ESTADOS_RAW, rid)

    def test_o_bruto_declarado_como_preservado_existe(self):
        for rid, r in pv.carregar().items():
            if r['RAW_EVIDENCE_STATE'] != 'PRESERVED':
                continue
            caminhos = r['RAW_EVIDENCE_PATH']
            caminhos = caminhos if isinstance(caminhos, list) else [caminhos]
            for caminho in caminhos:
                caminho = str(caminho).split(' (')[0].strip()
                if not caminho or caminho == pv.NOT_PRESERVED:
                    continue
                self.assertTrue(os.path.exists(os.path.join(ROOT, caminho)),
                                f'{rid} diz PRESERVED e o arquivo nao existe: {caminho}')

    def test_o_pipeline_leu_o_bruto_e_nao_o_normalizado(self):
        d = amostra('ES-T8-001-videos.json')
        self.assertIn('raw-paid', d['PIPELINE']['ENTRADA'])
        self.assertTrue(os.path.exists(os.path.join(ROOT, d['PIPELINE']['ENTRADA'])))

    def test_rota_gratuita_nao_finge_preservacao(self):
        r = pv.resolver('ES-T5-002-2026-08-29-a')
        self.assertEqual('NOT_APPLICABLE', r['RAW_EVIDENCE_STATE'],
                         'rota replicavel nao precisa versionar bruto, e nao deve fingir que versionou')


class TestAuditoriaContraAlvoCongelado(unittest.TestCase):
    """P0 — impedir a recorrencia do defeito de metodo."""

    def test_sem_sha_declarado_a_auditoria_e_invalida(self):
        ok, motivo = au.validar({'SNAPSHOT_PATH': ROOT})
        self.assertFalse(ok)
        self.assertIn('AUDIT_TARGET_SHA', motivo)

    def test_sem_snapshot_a_auditoria_e_invalida(self):
        ok, motivo = au.validar({'AUDIT_TARGET_SHA': 'a' * 40, 'SNAPSHOT_PATH': '/tmp/nao-existe-xyz'})
        self.assertFalse(ok)
        self.assertIn('nao foi congelada', motivo.replace('ã', 'a').replace('á', 'a'))

    def test_sha_divergente_invalida(self):
        reg = {'AUDIT_TARGET_SHA': '0' * 40, 'SNAPSHOT_PATH': ROOT}
        ok, motivo = au.validar(reg)
        self.assertFalse(ok)
        self.assertIn('mudou', motivo)

    def test_o_contrato_tem_os_campos_que_a_missao_exige(self):
        for c in ('AUDIT_TARGET_SHA', 'AUDIT_STARTED_AT', 'AUDIT_FINISHED_AT', 'SCRIPT_VERSION'):
            self.assertIn(c, au.CAMPOS_AUDITORIA)

    def test_invalida_e_invalida_e_nao_ressalva(self):
        reg = au.fechar({'AUDIT_TARGET_SHA': '0' * 40, 'SNAPSHOT_PATH': ROOT})
        self.assertIs(False, reg['VALID'])
        self.assertTrue(reg['INVALID_REASON'])


if __name__ == '__main__':
    unittest.main()
