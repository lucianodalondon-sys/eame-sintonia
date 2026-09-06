# -*- coding: utf-8 -*-
"""O handoff so vale se ele nao envelhecer em silencio.

Estes testes existem porque um documento de handoff com numero errado e PIOR que nenhum:
ele passa confianca falsa para quem nao tem como conferir.
"""
import json, os, re, subprocess, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

HANDOFF = os.path.join(ROOT, 'HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md')
PROMPT = os.path.join(ROOT, 'PROMPT-PARA-NOVA-CONTA-CLAUDE.md')
SAMPLES = os.path.join(ROOT, 'data', 'samples')


MARCADOR = re.compile(r'<!--/?M:?[A-Z0-9_]*-->')


def texto(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def sem_marcador(p):
    """O documento como quem o lê o vê.

    `<!--M:NOME-->280<!--/M-->` e andaime de `metricas_canonicas.py --sync`: para o leitor
    o que esta ali e o numero. Quem compara numero publicado le por aqui.
    """
    return MARCADOR.sub('', texto(p))


def amostra(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


class TestHandoffExiste(unittest.TestCase):

    def test_os_dois_documentos_existem(self):
        self.assertTrue(os.path.exists(HANDOFF))
        self.assertTrue(os.path.exists(PROMPT))

    def test_o_handoff_cobre_as_secoes_obrigatorias(self):
        t = texto(HANDOFF)
        for s in ('IDENTIDADE DO ESTADO', 'O QUE É O SINTONIA EAME',
                  'PORTA CANÔNICA DE ARQUITETURA', 'ESTADO DA ESPANHA',
                  'LEIS EPISTÊMICAS', 'DEDUPE', 'DATA CLOCK', 'APIFY',
                  'AUDITORIA ADVERSARIAL', 'BACKLOG DOS 47', 'MAPA DE ARQUIVOS',
                  'COMANDOS', 'DEPENDÊNCIAS EXTERNAS', 'PRÓXIMA MISSÃO'):
            self.assertIn(s, t, f'seção ausente no handoff: {s}')

    def test_o_prompt_obriga_medir_antes_de_confiar(self):
        t = texto(PROMPT)
        for s in ('git rev-parse HEAD', 'git status --short',
                  'HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md',
                  'python3 -m unittest discover -s tests',
                  'HANDOFF ACCEPTANCE REPORT'):
            self.assertIn(s, t)

    def test_o_prompt_proibe_alterar_e_coletar(self):
        t = texto(PROMPT)
        self.assertIn('NÃO ALTERE NADA', t)
        self.assertIn('gastar chave Apify', t)


class TestNenhumSegredoNoHandoff(unittest.TestCase):

    TOKEN = re.compile(r'apify_api_[A-Za-z0-9]{10,}|Bearer\s+[A-Za-z0-9._\-]{20,}')

    def test_nenhum_token_nos_documentos_de_handoff(self):
        for p in (HANDOFF, PROMPT):
            self.assertIsNone(self.TOKEN.search(texto(p)), f'credencial em {p}')

    def test_nenhum_token_em_todo_o_repositorio(self):
        achados = []
        for base, dirs, arqs in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules')]
            for a in arqs:
                p = os.path.join(base, a)
                try:
                    with open(p, encoding='utf-8', errors='ignore') as f:
                        if self.TOKEN.search(f.read()):
                            achados.append(os.path.relpath(p, ROOT))
                except OSError:
                    continue
        self.assertEqual([], achados, f'credencial versionada em: {achados}')


class TestSentinelasDoHandoffBatemComOLedger(unittest.TestCase):
    """As sentinelas que o prompt manda a nova conta conferir precisam ser verdade HOJE."""

    @classmethod
    def setUpClass(cls):
        import metricas_canonicas as mc
        cls.L = mc.build()

    def test_as_sentinelas_do_prompt_existem_no_ledger(self):
        t = texto(PROMPT)
        for m in ('TEST_COUNT_CURRENT', 'SOURCE_ID_COUNT', 'RAIF_SEASONS_AVAILABLE',
                  'RAIF_READINGS_TOTAL', 'ES_EXPIRING_6M', 'ES_EXPIRING_12M',
                  'ES_ACTIVE_WITH_PAST_EXPIRY', 'VOICE_ES_RESEARCHERS',
                  'VOICE_ES_VIDEO_CONTENTS', 'VIDEO_COUNT_CLASSIFIED',
                  'VIDEO_ORIGINALITY_UNKNOWN', 'QUEUE_RESEARCHERS_ES', 'ASK_WRONG'):
            self.assertIn(m, t, f'{m} sumiu do prompt de bootstrap')
            self.assertIn(m, self.L, f'{m} sumiu do ledger')

    def test_os_valores_das_sentinelas_batem(self):
        t = texto(PROMPT)
        for m, esperado in [('SOURCE_ID_COUNT', 40), ('RAIF_SEASONS_AVAILABLE', 23),
                            ('RAIF_READINGS_TOTAL', 148964), ('ES_EXPIRING_6M', 486),
                            ('ES_EXPIRING_12M', 1004), ('ES_ACTIVE_WITH_PAST_EXPIRY', 34),
                            ('VOICE_ES_RESEARCHERS', 152), ('VOICE_ES_VIDEO_CONTENTS', 252),
                            ('VIDEO_COUNT_CLASSIFIED', 252), ('VIDEO_ORIGINALITY_UNKNOWN', 241),
                            ('QUEUE_RESEARCHERS_ES', 20), ('ASK_WRONG', 0)]:
            self.assertEqual(esperado, self.L[m]['VALUE'],
                             f'{m}: o ledger mudou e o prompt de bootstrap nao acompanhou')
            self.assertRegex(t, rf'{m}\s*=\s*{esperado}\b',
                             f'{m}: o valor no prompt diverge do ledger')

    def test_o_handoff_nao_promete_um_verde_que_nao_existe(self):
        """Publicava «0 falhas, 0 erros, 0 pulados» ao lado do comando que imprime 10.

        O número de testes era o único campo guardado, então o resto da linha podia
        dizer qualquer coisa. Um handoff que promete verde e entrega vermelho é pior
        que um handoff sem número: a conta nova gasta a primeira missão a descobrir
        que a régua mente.
        """
        linhas = [l for l in sem_marcador(HANDOFF).split('\n') if '**TESTS**' in l]
        self.assertEqual(1, len(linhas), 'a linha TESTS do handoff sumiu ou duplicou')
        linha = linhas[0]
        # `\b` obrigatorio: sem ele, «10 falhas» contem «0 falhas» e o teste reprova a
        # propria correcao. O numero que interessa e o zero SOZINHO.
        self.assertNotRegex(
            linha, r'\b0 (?:falhas|erros|pulados)',
            'o handoff volta a prometer suíte limpa; se ela ficou limpa, apague também '
            'a lista de vermelhos do ledger e este teste')
        self.assertIn('INTEGRACAO-PROGRESSIVA-03', linha,
                      'a linha TESTS não diz onde os vermelhos estão nomeados')

    def test_os_vermelhos_herdados_estao_nomeados_um_a_um(self):
        ledger = os.path.join(ROOT, 'docs', 'organizacao',
                              'INTEGRACAO-PROGRESSIVA-03.md')
        if not os.path.exists(ledger):
            self.skipTest('ledger do PASSO 03 ausente')
        with open(ledger, encoding='utf-8') as f:
            doc = f.read()
        for nome in ('test_adama_es_gate', 'test_evidence', 'test_migrations',
                     'test_proveniencia'):
            with self.subTest(modulo=nome):
                self.assertIn(nome, doc,
                              'módulo vermelho não nomeado no ledger — vermelho sem nome '
                              'é vermelho escondido')

    def test_a_contagem_de_testes_do_handoff_bate(self):
        # O documento escreve o milhar com ponto — e o `--sync` escreve assim. Comparar
        # contra `1309` cru reprovava um handoff CERTO, que publicava `1.309`: o teste
        # exigia um formato que o dono do numero nunca produz. `FORMATO != VALOR`.
        n = self.L['TEST_COUNT_CURRENT']['VALUE']
        self.assertRegex(sem_marcador(HANDOFF), rf'\*\*{n:,}'.replace(',', r'\.') + r' testes',
                         'o handoff publica uma contagem de testes que nao e a atual')
        self.assertRegex(texto(PROMPT), rf'Esperado: {n} testes')


class TestInventarioDoScratchpad(unittest.TestCase):
    """Nada importante pode ter sumido em silencio na troca de conta."""

    def setUp(self):
        self.inv = amostra('INVENTARIO-SCRATCHPAD-HANDOFF.json')

    def test_todo_item_preservado_existe_de_fato(self):
        for item in self.inv['PRESERVED']:
            caminho = item['AGORA_EM'].split(' (')[0].strip()
            self.assertTrue(os.path.exists(os.path.join(ROOT, caminho)),
                            f"{item['SCRATCH']} diz preservado em {caminho}, que nao existe")

    def test_todo_descarte_tem_motivo(self):
        for item in self.inv['DISCARDED_WITH_REASON']:
            self.assertTrue(len(item['MOTIVO']) > 40,
                            f"{item['SCRATCH']} descartado sem motivo suficiente")

    def test_o_alerta_da_classificacao_errada_sobrevive(self):
        a = self.inv['ALERTA_PARA_A_PROXIMA_CONTA']
        self.assertIn('ftalimida', a)
        self.assertIn('NAO reuse', a)


class TestBrutoPagoSobrevive(unittest.TestCase):
    """A razao de ser do handoff: rota paga nao se replica quando a chave morre."""

    def test_todo_bruto_do_manifesto_existe(self):
        import proveniencia as pv
        for rid, r in pv.carregar().items():
            if r['RAW_EVIDENCE_STATE'] != 'PRESERVED':
                continue
            caminhos = r['RAW_EVIDENCE_PATH']
            for c in (caminhos if isinstance(caminhos, list) else [caminhos]):
                c = str(c).split(' (')[0].strip()
                if c and c != pv.NOT_PRESERVED:
                    self.assertTrue(os.path.exists(os.path.join(ROOT, c)),
                                    f'{rid}: bruto declarado e ausente: {c}')

    def test_o_bruto_esta_no_relogio_de_dados(self):
        d = amostra('DATA-CLOCK-manifest.json')
        vigiados = {f['FILE'] for f in d['files']}
        raw = {'data/samples/raw-paid/' + f
               for f in os.listdir(os.path.join(SAMPLES, 'raw-paid'))
               if not f.startswith('GATE-TEST')}
        self.assertEqual(set(), raw - vigiados,
                         'bruto de rota paga fora do relogio de dados')


if __name__ == '__main__':
    unittest.main()
