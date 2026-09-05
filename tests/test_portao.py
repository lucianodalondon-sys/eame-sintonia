# -*- coding: utf-8 -*-
"""P7, P8 e o portao de saida.

O portao so vale se ele PUDER barrar. Um portao que passa sempre e decoracao, entao
metade destes testes verifica que ele reprova quando deve.
"""
import json, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import portao, filas, voz          # noqa: E402
import proveniencia as pv          # noqa: E402

SAMPLES = os.path.join(ROOT, 'data', 'samples')
SEIS = ['RUN_MANIFEST', 'PIPELINE_DEDUPE', 'VIDEO_TAXONOMY_APPLIED',
        'VIDEO_ORIGINALITY', 'PAID_RAW_POLICY', 'COLLECTION_TIMESTAMPS']


def amostra(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


class TestPortao(unittest.TestCase):

    def setUp(self):
        self.v = portao.veredito()

    def test_os_seis_portoes_da_missao_existem(self):
        self.assertEqual(set(SEIS), set(self.v['PORTOES']))

    def test_todo_portao_traz_medida(self):
        for k, d in self.v['PORTOES'].items():
            self.assertTrue(d['MEDIDA'], f'{k} sem medida — estado afirmado, não derivado')

    def test_o_veredito_e_derivado_dos_portoes(self):
        """Tres estados, nao dois.

        `NO`  = algum portao barrou.
        `YES` = os seis passam por AUTO-AVALIACAO — o portao dizendo que ele mesmo passa.
        `ADVERSARIALLY_VERIFIED` = alem disso, alguem tentou REFUTAR cada portao e falhou,
        e a implementacao nao mudou desde entao.
        """
        todos = all(d['PROVED'] for d in self.v['PORTOES'].values())
        adv = self.v['VERIFICACAO_ADVERSARIAL']['ESTADO']
        if not todos:
            esperado = 'NO'
        elif adv == 'ADVERSARIALLY_VERIFIED':
            esperado = 'ADVERSARIALLY_VERIFIED'
        else:
            esperado = 'YES'
        self.assertEqual(esperado, self.v['READY_FOR_NEXT_ES_COLLECTION'])
        self.assertEqual(sorted(k for k, d in self.v['PORTOES'].items() if not d['PROVED']),
                         sorted(self.v['BLOQUEADO_POR']))

    def test_portao_bloqueado_nomeia_o_bloqueio(self):
        for k, d in self.v['PORTOES'].items():
            if not d['PROVED']:
                self.assertTrue(d['BLOQUEIO'], f'{k} bloqueado sem dizer por quê')
            else:
                self.assertIsNone(d['BLOQUEIO'])

    def test_o_portao_de_dedupe_exerce_o_dedupe(self):
        # o portao nao pode passar so porque DUPLICATE_COUNT=0
        u, c = voz.dedupe([{'PLATFORM': 'X', 'EXTERNAL_ID': 'a'},
                           {'PLATFORM': 'X', 'EXTERNAL_ID': 'a'},
                           {'PLATFORM': 'X', 'EXTERNAL_ID': 'b'}])
        self.assertEqual((2, 1), (len(u), c))

    def test_o_portao_de_taxonomia_recusa_tipo_fora_do_contrato(self):
        validos = set(voz.TIPOS_VIDEO) | {voz.NAO_SEI}
        for v in amostra('ES-T8-001-videos.json')['VIDEOS']:
            self.assertIn(v['CONTENT_TYPE'], validos)

    def test_o_portao_de_timestamp_olha_a_porta_nova_e_nao_um_limiar(self):
        m = self.v['PORTOES']['COLLECTION_TIMESTAMPS']['MEDIDA']
        self.assertIn('porta nova', m)
        self.assertIn('sem fingir', m)


class TestFilaDePesquisadores(unittest.TestCase):

    def setUp(self):
        self.f = amostra('RESEARCHER-PUBLIC-VOICE-QUEUE-ES.json')

    def test_a_meta_e_vinte(self):
        self.assertEqual(20, len(self.f['QUEUE']))
        self.assertEqual(self.f['NA_FILA'], len(self.f['QUEUE']))

    def test_todo_selecionado_tem_os_campos_que_a_missao_pediu(self):
        for p in self.f['QUEUE']:
            for c in ('PERSON_ID', 'NAME', 'INSTITUTION', 'CROP', 'ISSUE', 'WHY_SELECTED',
                      'PUBLIC_LINKEDIN_STATUS', 'PUBLIC_YOUTUBE_STATUS'):
                self.assertIn(c, p)
                self.assertTrue(p[c] not in (None, '', []), f"{p.get('NAME')}.{c} vazio")

    def test_nada_foi_coletado_nesta_missao(self):
        for p in self.f['QUEUE']:
            self.assertEqual('NOT_TESTED', p['PUBLIC_LINKEDIN_STATUS'])
            self.assertEqual('NOT_TESTED', p['PUBLIC_YOUTUBE_STATUS'])

    def test_todo_selecionado_passa_nos_criterios_declarados(self):
        for p in self.f['QUEUE']:
            self.assertIn('OLIVE', p['CROP'])
            self.assertTrue(set(p['ISSUE']) & filas.ISSUES_ANCORA)
            self.assertGreaterEqual(p['LAST_KNOWN_ACTIVITY'], filas.ANO_MINIMO)
            self.assertTrue(p['ORCID'].startswith('https://orcid.org/'))

    def test_nenhum_conflacionado_entra(self):
        for p in self.f['QUEUE']:
            self.assertLessEqual(p['ALL_INSTITUTIONS_COUNT'], 20,
                                 f"{p['NAME']}: organizações demais, verificar conflação")

    def test_o_excluido_do_quadro_nao_reaparece_na_fila(self):
        nomes = {p['NAME'] for p in self.f['QUEUE']}
        for e in amostra('ES-RESEARCHERS-OLIVE.json')['EXCLUSOES_APLICADAS']:
            self.assertNotIn(e['NAME'], nomes)

    def test_a_fila_e_reproduzivel_pelo_script(self):
        q, _, _, _ = filas.selecionar_pesquisadores()
        self.assertEqual([p['PERSON_ID'] for p in self.f['QUEUE']],
                         [p['PERSON_ID'] for p in q],
                         'a fila publicada não é a que o script produz')

    def test_qual_criterio_filtra_esta_declarado(self):
        self.assertIn('13 dos 152', self.f['QUAL_CRITERIO_REALMENTE_FILTRA'])
        self.assertIn('GUARDA', self.f['QUAL_CRITERIO_REALMENTE_FILTRA'])


class TestFilaDeVozesTecnicas(unittest.TestCase):

    def setUp(self):
        self.f = amostra('PUBLIC-TECHNICAL-VOICE-QUEUE-ES.json')

    def test_a_meta_de_vinte_e_atingida_sem_completar_cota(self):
        self.assertGreaterEqual(len(self.f['QUEUE']), 20)
        self.assertGreater(self.f['ELEGIVEIS'], len(self.f['QUEUE']),
                           'se elegíveis == fila, a fila é a cota e não um recorte')

    def test_alcance_nao_entra_em_nenhum_criterio(self):
        bruto = json.dumps(self.f['CRITERIOS'], ensure_ascii=False).lower()
        for palavra in ('follower', 'seguidor', 'alcance', 'views'):
            self.assertNotIn(palavra, bruto)
        for o in self.f['QUEUE']:
            self.assertNotIn('FOLLOWERS', o)

    def test_todo_papel_e_verificavel_e_vem_de_campo_declarado(self):
        for o in self.f['QUEUE']:
            self.assertIn(o['ROLE_BASIS'], ('COMPANY_TYPE+INDUSTRY', 'HEADLINE+CURRENT_POSITION'))
            self.assertTrue(o['ROLE_EVIDENCE'])
            self.assertIn(o['DECLARED_ROLE'], self.f['CRITERIOS']['PRIORIDADE_DE_PAPEL'])

    def test_nada_foi_coletado(self):
        for o in self.f['QUEUE']:
            self.assertEqual('NOT_TESTED', o['PUBLIC_CONTENT_STATUS'])

    def test_o_vies_geografico_esta_declarado(self):
        self.assertIn('desenho da consulta', self.f['VIES_DECLARADO'])

    def test_a_fila_e_reproduzivel_pelo_script(self):
        v, _ = filas.selecionar_vozes_tecnicas()
        self.assertEqual([o['ORIGIN_ID'] for o in self.f['QUEUE']],
                         [o['ORIGIN_ID'] for o in v])



class TestRefutacaoAdversarial10C(unittest.TestCase):
    """MISSAO 10C — cada teste aqui e um CONTRAEXEMPLO que passou pelo portao.

    Nenhum e hipotetico: todos foram construidos, rodados, e o portao (ou a lei) disse
    PROVED com a propriedade real quebrada. O teste existe para que nao volte.
    """

    # ---------------------------------------------------------------- P2
    def test_registros_sem_id_estrutural_nao_colapsam(self):
        """P2 REFUTADO: tres videos distintos sem `id` viravam um.

        `normalizar_video` grava EXTERNAL_ID = NAO SEI quando a rota nao devolve id.
        Com a chave antiga todos compartilhavam ('YOUTUBE','NÃO SEI'): RAW 3 -> UNICOS 1,
        DUPLICATE_COUNT 2, a aritmetica FECHAVA e o portao dizia PROVED enquanto dois
        videos reais desapareciam como "duplicata" de um registro sem identidade.
        """
        brutos = [{'title': 'El repilo del olivo en Jaen', 'channelId': 'C1'},
                  {'title': 'Poda mecanizada del olivar', 'channelId': 'C2'},
                  {'title': 'Verticilosis manejo integrado', 'channelId': 'C3'}]
        unicos, rel = voz.pipeline_video(brutos, source_id='S', run_id='R',
                                         capture_date='2026-08-29')
        self.assertEqual(3, rel['UNIQUE_CONTENT_COUNT'],
                         'ausencia de identidade virou identidade compartilhada')
        self.assertEqual(0, rel['DUPLICATE_COUNT'])
        self.assertEqual(3, rel['WITHOUT_STRUCTURAL_ID_COUNT'],
                         'a contagem sem id tem de ser publicada, nunca implicita')
        self.assertEqual({b['title'] for b in brutos}, {u['TITLE'] for u in unicos})

    def test_id_repetido_continua_colapsando(self):
        """A correcao nao pode desligar o dedupe de verdade."""
        regs = [{'PLATFORM': 'X', 'EXTERNAL_ID': 'a', 'TITLE': 'um'},
                {'PLATFORM': 'X', 'EXTERNAL_ID': 'a', 'TITLE': 'dois'},
                {'PLATFORM': 'X', 'EXTERNAL_ID': 'b', 'TITLE': 'um'}]
        unicos, colapsados = voz.dedupe(regs)
        self.assertEqual(2, len(unicos))
        self.assertEqual(1, colapsados)

    def test_mesmo_id_em_plataformas_diferentes_nao_colapsa(self):
        regs = [{'PLATFORM': 'YOUTUBE', 'EXTERNAL_ID': '123'},
                {'PLATFORM': 'LINKEDIN', 'EXTERNAL_ID': '123'}]
        self.assertEqual(2, len(voz.dedupe(regs)[0]))

    # ---------------------------------------------------------------- P6
    def test_ordem_respeita_fuso_horario(self):
        """P6 REFUTADO: comparacao de STRING dava AFTER onde a verdade e BEFORE.

        C = 09:00+02:00 (07:00 UTC) termina antes de D = 08:00Z comecar.
        O repositorio JA mistura os formatos: o export do ROPF traz +02:00.
        """
        def run(rid, ini, fim):
            r = pv.run_vazio(); r['RUN_ID'] = rid
            r['STARTED_AT'], r['FINISHED_AT'] = ini, fim
            return r
        c = run('C', '2026-08-29T09:00:00+02:00', '2026-08-29T09:30:00+02:00')
        d = run('D', '2026-08-29T08:00:00Z', '2026-08-29T08:30:00Z')
        self.assertEqual('BEFORE', pv.ordem(c, d)[0],
                         'ordem por comparacao de string ignora o fuso')

    def test_carimbo_invalido_falha_fechado(self):
        """P6 REFUTADO: a guarda era uma lista de 4 valores proibidos, nao validacao."""
        def run(v):
            r = pv.run_vazio(); r['RUN_ID'] = 'A'
            r['STARTED_AT'], r['FINISHED_AT'] = v, v
            return r
        bom = pv.run_vazio(); bom['RUN_ID'] = 'B'
        bom['STARTED_AT'] = '2026-08-29T10:00:00Z'
        bom['FINISHED_AT'] = '2026-08-29T11:00:00Z'
        for lixo in ('desconhecido', 'ontem', '2026-08-29', 'NOT_MEASURED', 0, 3.5,
                     '2026-08-29T10:00:00'):
            with self.subTest(valor=lixo):
                self.assertEqual('NAO_DIZIVEL', pv.ordem(run(lixo), bom)[0],
                                 'carimbo invalido sustentou afirmacao de ordem')

    def test_execucao_legada_continua_nao_dizivel(self):
        runs = pv.carregar()
        legados = [r for r in runs.values() if r['STARTED_AT'] == pv.NOT_PRESERVED]
        self.assertGreaterEqual(len(legados), 2)
        self.assertEqual('NAO_DIZIVEL', pv.ordem(legados[0], legados[1])[0])

    # ---------------------------------------------------------------- P1
    def test_run_id_duplicado_e_denunciado(self):
        """P1 REFUTADO: carregar() indexa por RUN_ID e o segundo sobrescrevia o primeiro."""
        import tempfile
        d = json.load(open(os.path.join(SAMPLES, 'RUN-MANIFEST.json'), encoding='utf-8'))
        d['RUNS'] = d['RUNS'] + [dict(d['RUNS'][0], STATUS='FAILED')]
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False,
                                         encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False)
            tmp = f.name
        try:
            self.assertEqual([d['RUNS'][0]['RUN_ID']], pv.runs_duplicados(tmp))
        finally:
            os.unlink(tmp)
        self.assertEqual([], pv.runs_duplicados(), 'o manifesto real tem RUN_ID repetido')

    def test_o_portao_varre_todos_os_artefatos_com_run_id(self):
        """P1 REFUTADO: o portao lia 3 arquivos escolhidos a dedo; ha 6 com RUN_ID."""
        import portao
        portao.avaliar()
        self.assertGreaterEqual(len(portao._ARTEFATOS_COM_RUN_ID), 6,
                                'a varredura de RUN_ID encolheu')

    # ---------------------------------------------------------------- P4
    def test_nao_sei_nao_e_evidencia(self):
        """P4 REFUTADO: ORIGINALITY_EVIDENCE='NÃO SEI' passava como prova."""
        import portao
        self.assertFalse(portao._evidencia_valida('NÃO SEI'))
        self.assertFalse(portao._evidencia_valida(''))
        self.assertFalse(portao._evidencia_valida(None))
        self.assertTrue(portao._evidencia_valida('mesmo titulo em 2 canais distintos'))

    def test_original_nao_tem_caminho_de_codigo(self):
        """Nenhuma rota prova autoria: a funcao nunca pode emitir ORIGINAL."""
        regs = [{'TITLE': 'Nuestro ensayo propio en finca', 'CHANNEL_ID': 'ADAMA',
                 'DESCRIPTION': 'contenido original de nuestro equipo'}]
        voz.marcar_originalidade(regs)
        self.assertEqual('UNKNOWN', regs[0]['ORIGINALITY'])

    def test_a_distribuicao_do_portao_e_derivada_dos_registros(self):
        """P4 REFUTADO: a MEDIDA vinha do bloco DECLARADO no arquivo.

        Os 252 podiam virar ORIGINAL e o portao seguia imprimindo {UNKNOWN: 241}.
        """
        import portao
        vids = json.load(open(os.path.join(SAMPLES, 'ES-T8-001-videos.json'),
                              encoding='utf-8'))
        derivada = portao._distribuicao(vids['VIDEOS'], 'ORIGINALITY')
        declarada = vids['ORIGINALITY']['DISTRIBUICAO']
        self.assertEqual(dict(declarada), derivada,
                         'o bloco declarado no arquivo divergiu dos registros')
        forjado = [dict(v, ORIGINALITY='ORIGINAL') for v in vids['VIDEOS']]
        self.assertNotEqual(dict(declarada), portao._distribuicao(forjado, 'ORIGINALITY'))

    # ---------------------------------------------------------------- P5
    def test_o_portao_confere_a_integridade_do_bruto(self):
        """P5 REFUTADO: o bruto podia ser TROCADO e o portao dizia PROVED.

        O SHA-256 existia no relogio de dados e nada o conferia: existencia nao e
        integridade, e para rota paga o bruto e a UNICA copia da evidencia.
        """
        import portao
        self.assertEqual([], portao._bruto_corrompido(),
                         'bruto de producao com SHA-256 diferente do relogio')

    def test_a_entrada_do_pipeline_e_arquivo_que_existe(self):
        """P5 REFUTADO: bastava a STRING conter 'raw-paid'. Mencao nao e leitura."""
        vids = json.load(open(os.path.join(SAMPLES, 'ES-T8-001-videos.json'),
                              encoding='utf-8'))
        entrada = vids['PIPELINE']['ENTRADA']
        self.assertTrue(entrada.startswith(pv.RAW_PAID_REL + '/'))
        self.assertTrue(os.path.exists(os.path.join(ROOT, entrada)),
                        'PIPELINE.ENTRADA aponta para bruto inexistente')

    # ---------------------------------------------------------------- P0
    def test_branch_vivo_nao_e_alvo_congelado(self):
        """P0 LIMITE FECHADO: validar() aceitava o repositorio de trabalho como snapshot."""
        import auditoria as au
        ok, motivo = au.validar({'AUDIT_TARGET_SHA': au.sha_atual(), 'SNAPSHOT_PATH': ROOT})
        self.assertFalse(ok, 'branch vivo aceito como alvo congelado')



class TestVerificacaoAdversarialRegistrada(unittest.TestCase):
    """MISSAO 11 — o veredito da 10C existia so no relatorio.

    Veredito que vive fora do Git nao existe para a proxima conta. E `YES` nao e a mesma
    coisa que `ADVERSARIALLY_VERIFIED`: o primeiro e o portao dizendo que ele mesmo passa.
    """

    def setUp(self):
        self.v = portao.verificacao_adversarial()

    def test_a_verificacao_esta_registrada_no_repositorio(self):
        caminho = os.path.join(SAMPLES, 'VERIFICACAO-ADVERSARIAL-PORTOES.json')
        self.assertTrue(os.path.exists(caminho), 'o veredito nao foi externalizado')

    def test_os_sete_portoes_tem_resultado_declarado(self):
        d = amostra('VERIFICACAO-ADVERSARIAL-PORTOES.json')
        r = d['RESULTADO_POR_PORTAO']
        self.assertEqual(7, len(r), 'faltou portao no registro da verificacao')
        for k, x in r.items():
            with self.subTest(portao=k):
                self.assertIn(x['RESULT'],
                              ('SURVIVED_ADVERSARIAL_CHECK', 'REFUTED', 'NOT_TESTABLE'))

    def test_o_limite_aberto_do_p3_nao_pode_ser_apagado(self):
        d = amostra('VERIFICACAO-ADVERSARIAL-PORTOES.json')
        limite = d['RESULTADO_POR_PORTAO']['P3_VIDEO_TAXONOMY']['LIMITE_DECLARADO_E_ABERTO']
        self.assertIn('NOT_TESTABLE', limite)
        self.assertIn('lexical', limite)

    def test_o_estado_e_derivado_e_detecta_obsolescencia(self):
        """Um portao reverificado e depois reescrito nao esta mais verificado."""
        self.assertIn(self.v['ESTADO'],
                      ('ADVERSARIALLY_VERIFIED', 'VERIFICATION_STALE',
                       'REFUTED', 'NOT_VERIFIED', 'UNKNOWN'))
        self.assertIn('AUDIT_TARGET_SHA', self.v)

    def test_yes_nao_e_adversarially_verified(self):
        """O veredito so sobe quando a verificacao registrada estiver valida."""
        v = portao.veredito()
        if v['VERIFICACAO_ADVERSARIAL']['ESTADO'] != 'ADVERSARIALLY_VERIFIED':
            self.assertNotEqual('ADVERSARIALLY_VERIFIED',
                                v['READY_FOR_NEXT_ES_COLLECTION'],
                                'o portao subiu o veredito sem verificacao valida')

if __name__ == '__main__':
    unittest.main()
