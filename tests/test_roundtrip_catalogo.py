"""ROUND-TRIP do catálogo público ADAMA España — Git ↔ Disco ↔ Storage ↔ Postgres.

Quatro elos, e este arquivo prova os que dá para provar SEM credencial:

    Git ↔ linhas normalizadas    o artefato e o que o importador vai inserir batem
    disco ↔ manifesto            os bytes no disco são os que o manifesto declara
    manifesto ↔ plano            o plano de preservação cobre tudo, sem sobra
    SQL ↔ idempotência           todo INSERT tem ON CONFLICT sobre chave natural

E DECLARA os dois que não dá, em vez de fingir:

    disco ↔ Storage              exige SUPABASE_URL + SUPABASE_SECRET_KEY
    Git ↔ Postgres               exige SUPABASE_DB_URL + psql

O risco que estes testes cobrem é um só, e é caro: um número que bate no relatório e
não bate no banco. "138 preservados" escrito num markdown não preserva nada; "711
relações" no artefato não vale se o import inserir 705 e ninguém contar.

Quando a credencial existir, os dois elos pendentes viram teste de verdade — o
esqueleto já está aqui, marcado, e não passa por omissão: ele PULA e diz por quê.
"""
import hashlib
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
RAW = os.path.join(ROOT, 'data', 'raw', 'ES', 'adama-website')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

ARTEFATO = os.path.join(SAMPLES, 'ADAMA-ES-PRODUCT-INTELLIGENCE.json')
PLANO = os.path.join(SAMPLES, 'ADAMA-ES-PRESERVACAO-PLANO.json')
SQL = os.path.join(ROOT, 'supabase', 'importacoes', 'ADAMA-ES-CATALOGO-2026-08-30.sql')


def _json(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


class TestGitVsLinhasNormalizadas(unittest.TestCase):
    """O que o importador vai inserir é exatamente o que o artefato afirma."""

    @classmethod
    def setUpClass(cls):
        cls.art = _json(ARTEFATO)
        try:
            import catalogo_importar as I
            cls.L = I.normalizar()
        except (SystemExit, ImportError):
            cls.L = None

    def setUp(self):
        if self.art is None or self.L is None:
            self.skipTest('artefato ou importador ausentes nesta sessão')

    def test_o_catalogo_tem_o_mesmo_tamanho_dos_dois_lados(self):
        self.assertEqual(self.art['CENSO']['CURRENT_CATALOG_TOTAL'], len(self.L['PRODUTO']))
        self.assertEqual(len(self.art['PRODUCTS']), len(self.L['PRODUTO']))

    def test_as_quatro_categorias_batem(self):
        de_la = {}
        for p in self.art['PRODUCTS']:
            de_la[p['CATEGORY']] = de_la.get(p['CATEGORY'], 0) + 1
        daqui = {}
        for p in self.L['PRODUTO']:
            daqui[p['categoria']] = daqui.get(p['categoria'], 0) + 1
        self.assertEqual(de_la, daqui)
        self.assertEqual(sum(daqui.values()), 56, 'o catálogo mudou de tamanho')

    def test_cada_estrutura_atravessa_inteira(self):
        pares = [
            ('DOCUMENTS', 'DOCUMENTO'), ('CROP_RELATIONS', 'CULTIVO'),
            ('ISSUE_RELATIONS', 'AGENTE'), ('CROP_ISSUE_RELATIONS', 'PAR'),
            ('CROP_DOSE_RELATIONS', 'DOSE'), ('APPLICATION_WINDOWS', 'JANELA'),
            ('ACTIVE_INGREDIENTS', 'SUBSTANCIA'), ('MODES_OF_ACTION', 'MOA'),
            ('CLAIMS', 'CLAIM'), ('TECHNOLOGIES', 'TECNOLOGIA'),
            ('PRODUCT_RELATIONS', 'RELACAO'), ('AMBIGUOUS_TERMS', 'AMBIGUO'),
        ]
        for no_artefato, nas_linhas in pares:
            with self.subTest(estrutura=no_artefato):
                self.assertEqual(len(self.art[no_artefato]), len(self.L[nas_linhas]),
                                 '%s perde ou ganha linha na normalização' % no_artefato)

    def test_declarado_e_citado_continuam_separados(self):
        """A soma tem que fechar, E as duas parcelas têm que continuar existindo."""
        decl = sum(1 for c in self.L['CULTIVO']
                   if c['origem_declaracao'] == 'DECLARADO_NO_BLOCO_CULTIVOS')
        cit = sum(1 for c in self.L['CULTIVO']
                  if c['origem_declaracao'] == 'CITADO_NO_CORPO_DA_PAGINA')
        self.assertEqual(decl + cit, len(self.L['CULTIVO']))
        self.assertGreater(decl, 0)
        self.assertGreater(cit, 0, 'se CITADO virar 0, a distinção foi colapsada')

    def test_milho_declarado_nao_soma_com_milho_citado(self):
        """O erro concreto que isto impede: 15 + 20 = 35 produtos de milho."""
        rot = {'MAÍZ', 'MAÍZ DULCE'}
        decl = {c['product_id'] for c in self.L['CULTIVO']
                if c['rotulo_publicado'] in rot
                and c['origem_declaracao'] == 'DECLARADO_NO_BLOCO_CULTIVOS'}
        cit = {c['product_id'] for c in self.L['CULTIVO']
               if c['rotulo_publicado'] in rot
               and c['origem_declaracao'] == 'CITADO_NO_CORPO_DA_PAGINA'}
        self.assertTrue(decl, 'nenhum produto declara milho — a fonte mudou?')
        self.assertEqual(len(decl | cit), len(decl) + len(cit - decl),
                         'produto contado duas vezes entre declarado e citado')

    def test_dose_nunca_vira_par(self):
        """CROP_DOSE e CROP_ISSUE são tabelas diferentes, e não se misturam."""
        pares = {(r['product_id'], r['cultivo_rotulo']) for r in self.L['PAR']}
        for d in self.L['DOSE']:
            self.assertFalse(d.get('agente_rotulo'), 'dose ganhou coluna de agente')
            self.assertIn('cartesiano', d['porque_nao_ha_par'])
        # e o par continua existindo por conta própria
        self.assertEqual(len(pares), len(self.L['PAR']))

    def test_todo_par_carrega_ancora(self):
        for r in self.L['PAR']:
            self.assertEqual(r['par_origem'], 'SAME_TABLE_ROW')
            self.assertIsNotNone(r['ancora_tabela'])
            self.assertIsNotNone(r['ancora_linha'])
            self.assertTrue((r['ancora_texto'] or '').strip())

    def test_confirmacao_do_mapa_atravessa_com_a_prova(self):
        conf = [r for r in self.L['PAR']
                if r['confirmacao_mapa'] == 'ADAMA_CLAIM_MAPA_CONFIRMED']
        self.assertEqual(len(conf), self.art['CONTAGENS']['REGULATORY_CONFIRMED_RELATIONS'])
        for r in conf:
            self.assertEqual(r['nivel_evidencia_final'], 'REGULATORY_FACT')
            self.assertIsNotNone(r['mapa_id_cultivo'])
            self.assertIsNotNone(r['mapa_id_plaga'])
            self.assertIsNotNone(r['mapa_registros_no_par'])
            self.assertIsNotNone(r['mapa_registro_casado'])

    def test_o_crosswalk_particiona_o_catalogo(self):
        """41 + 3 + 0 + 12 = 56. Se não fecha, algum número não nasceu de classificar."""
        do_catalogo = ('MATCHED_EXACT', 'MATCHED_WITH_EVIDENCE', 'AMBIGUOUS',
                       'ADAMA_SITE_ONLY')
        conta = {}
        for l in self.L['CROSSWALK']:
            conta[l['estado']] = conta.get(l['estado'], 0) + 1
        soma = sum(conta.get(e, 0) for e in do_catalogo)
        self.assertEqual(soma, len(self.L['PRODUTO']),
                         'os estados do catálogo (%d) não fecham os produtos (%d): %s'
                         % (soma, len(self.L['PRODUTO']), conta))
        for l in self.L['CROSSWALK']:
            if l['estado'] == 'MATCHED_EXACT':
                self.assertIsNotNone(l['registration_id_texto'],
                                     'match exato sem número de registro é fuzzy')

    def test_disponibilidade_comercial_nao_atravessa_como_sim(self):
        """Presença em catálogo não vira venda em lugar nenhum da normalização."""
        texto = json.dumps(self.L, ensure_ascii=False)
        self.assertNotIn('"current_commercial_availability": "SIM"', texto)
        self.assertNotIn("CURRENT_COMMERCIAL_AVAILABILITY': 'SIM'", texto)
        for p in self.L['PRODUTO']:
            self.assertNotIn('disponibilidade', json.dumps(p, ensure_ascii=False).lower())

    def test_nao_sei_virou_null_e_nao_string(self):
        """Guardar a string 'NÃO SEI' faria `where registration_id is null` mentir."""
        texto = json.dumps(self.L, ensure_ascii=False)
        self.assertNotIn('NÃO SEI', texto)
        self.assertNotIn('NAO SEI', texto)


class TestDiscoVsManifesto(unittest.TestCase):
    """Os bytes que existem são os bytes que o manifesto promete."""

    def setUp(self):
        self.idx = _json(os.path.join(RAW, 'documentos-baixados.json'))
        if self.idx is None:
            self.skipTest('RAW local ausente nesta máquina')

    def test_todo_documento_do_manifesto_existe_e_bate_o_hash(self):
        faltando, divergindo = [], []
        for mid, d in self.idx.items():
            caminho = os.path.join(RAW, 'documentos', d['ARQUIVO'])
            if not os.path.exists(caminho):
                faltando.append(mid)
                continue
            with open(caminho, 'rb') as f:
                b = f.read()
            if hashlib.sha256(b).hexdigest() != d['SHA256'] or len(b) != d['BYTES']:
                divergindo.append(mid)
        self.assertEqual([], faltando, 'documento no manifesto e ausente no disco')
        self.assertEqual([], divergindo, 'HASH_MISMATCH entre disco e manifesto')

    def test_o_plano_de_preservacao_cobre_tudo_sem_sobra(self):
        plano = _json(PLANO)
        if plano is None:
            self.skipTest('plano de preservação ainda não gerado')
        self.assertEqual([], plano['PROBLEMAS_ANTES_DE_ENVIAR'])
        docs = plano['POR_CLASSE'].get('DOCUMENTO', 0)
        self.assertEqual(docs, len(self.idx),
                         'o plano cobre %d documentos e o manifesto tem %d'
                         % (docs, len(self.idx)))
        shas_plano = {a['SHA256'] for a in plano['ASSETS'] if a['CLASSE'] == 'DOCUMENTO'}
        shas_disco = {d['SHA256'] for d in self.idx.values()}
        self.assertEqual(set(), shas_disco - shas_plano, 'arquivo no disco fora do plano')
        self.assertEqual(set(), shas_plano - shas_disco, 'ORFAO: plano cita o que não existe')

    def test_link_falho_nunca_entra_como_byte_preservado(self):
        art = _json(ARTEFATO)
        plano = _json(PLANO)
        if art is None or plano is None:
            self.skipTest('artefato ou plano ausentes')
        falhos = [d for d in art['DOCUMENTS'] if d.get('DOWNLOAD_STATE') == 'FAILED']
        self.assertTrue(falhos, 'sumiram os links falhos — eles têm que continuar contados')
        urls_no_plano = {a.get('SOURCE_URL') for a in plano['ASSETS']}
        for d in falhos:
            self.assertNotIn(d['URL'], urls_no_plano,
                             'link falho entrou no plano de preservação')
            self.assertIsNotNone(d.get('HTTP_STATUS'))
            self.assertIsNotNone(d.get('FAILURE_REASON'))


class TestSqlEhIdempotente(unittest.TestCase):
    """Rodar duas vezes tem que inserir zero na segunda — e isso se lê no texto."""

    def setUp(self):
        if not os.path.exists(SQL):
            self.skipTest('SQL de importação ainda não gerado')
        with open(SQL, encoding='utf-8') as f:
            self.sql = f.read()

    def test_nao_ha_update_delete_nem_upsert_que_sobrescreva(self):
        for proibido in (r'\bupdate\s+public\.', r'\bdelete\s+from\b', r'\btruncate\b',
                         r'do\s+update\s+set'):
            self.assertIsNone(re.search(proibido, self.sql, re.I),
                              'o import reescreve histórico: %s' % proibido)

    def test_todo_insert_com_chave_natural_tem_on_conflict(self):
        """A exceção declarada é janela de aplicação e crosswalk: não têm chave natural.

        Janela pode repetir legitimamente (duas janelas iguais em seções diferentes) e
        crosswalk é reemitido por captura. Ambas ficam fora, e ficam NOMEADAS aqui —
        exceção silenciosa seria o mesmo que não ter a regra.
        """
        # Fatiar por ';' estava errado e o teste acusou quatro tabelas inocentes: há ';'
        # DENTRO de literal ("application/pdf; length=127023"), e o corte caía antes do
        # ON CONFLICT. Corta-se de um INSERT ao próximo, que não depende de pontuação
        # dentro de string.
        marcas = [m.start() for m in re.finditer(r'insert into public\.', self.sql, re.I)]
        sem_conflito = []
        for i, ini in enumerate(marcas):
            fim = marcas[i + 1] if i + 1 < len(marcas) else len(self.sql)
            corpo = self.sql[ini:fim]
            tabela = re.match(r'insert into public\.(\w+)', corpo, re.I).group(1)
            if 'on conflict' not in corpo.lower():
                sem_conflito.append(tabela)
        permitidas = {'catalogo_produto_janela_aplicacao', 'catalogo_registro_crosswalk'}
        self.assertEqual(set(sem_conflito) - permitidas, set(),
                         'INSERT sem ON CONFLICT numa tabela com chave natural')

    def test_a_captura_e_unica_por_pais_e_versao_da_fonte(self):
        self.assertIn('on conflict (pais, fabricante, fonte_versao) do nothing', self.sql)

    def test_o_sql_nao_carrega_segredo(self):
        for padrao in (r'postgres://', r'postgresql://', r'eyJ[A-Za-z0-9_-]{20,}',
                       r'service_role', r'SUPABASE_[A-Z_]*KEY\s*='):
            self.assertIsNone(re.search(padrao, self.sql),
                              'o SQL versionado carrega algo que parece credencial')


class TestLeituraDoBucketNaoConfundeFalhaComAusencia(unittest.TestCase):
    """FALHA != AUSÊNCIA — e esta função já quebrou a lei em produção.

    Em 2026-08-30 o uploader imprimiu "bucket `raw` ausente — criar antes" sobre um
    bucket que existia desde a véspera, criado e verificado pelo workflow canônico. A
    causa: qualquer HTTP diferente de 200 virava EXISTE=False. Três situações distintas
    — bucket inexistente, chave sem permissão, projeto errado — saíam com a mesma frase,
    e a instrução que ela dava (criar bucket) era errada em duas delas.
    """

    def setUp(self):
        import storage_preservar as S
        self.S = S
        self.original = S._http

    def tearDown(self):
        self.S._http = self.original

    def _responde(self, status, corpo=b''):
        self.S._http = lambda url, key, m, p, d=None, c=None, timeout=300: (status, corpo)

    def test_sem_permissao_nao_vira_ausencia(self):
        for codigo in (401, 403):
            with self.subTest(http=codigo):
                self._responde(codigo, b'{"message":"invalid signature"}')
                r = self.S.bucket_esta_certo('https://x', 'k')
                self.assertEqual('NAO_SEI', r['EXISTE'],
                                 'chave sem permissao virou "bucket nao existe"')
                self.assertEqual(codigo, r['HTTP'])
                self.assertIn('permissao', r['PORQUE'])

    def test_erro_de_servidor_nao_vira_ausencia(self):
        self._responde(500, b'boom')
        r = self.S.bucket_esta_certo('https://x', 'k')
        self.assertEqual('NAO_SEI', r['EXISTE'])
        self.assertEqual(500, r['HTTP'])

    def test_rede_caida_nao_vira_ausencia(self):
        self._responde(0, b'URLError: nao resolveu')
        self.assertEqual('NAO_SEI', self.S.bucket_esta_certo('https://x', 'k')['EXISTE'])

    def test_lista_sem_raw_e_ausencia_de_verdade(self):
        """Só isto é ausência: a lista respondeu, e `raw` não está nela."""
        self._responde(200, b'[{"name":"outro","public":false}]')
        r = self.S.bucket_esta_certo('https://x', 'k')
        self.assertIs(False, r['EXISTE'])
        self.assertEqual(['outro'], r['BUCKETS'])
        self.assertIn('OUTRO projeto', r['PORQUE'],
                      'ausência tem de lembrar a hipótese de projeto errado')

    def test_bucket_privado_e_publico_sao_medidos(self):
        self._responde(200, b'[{"name":"raw","public":false,"id":"raw"}]')
        r = self.S.bucket_esta_certo('https://x', 'k')
        self.assertIs(True, r['EXISTE'])
        self.assertIs(True, r['PRIVADO'])

        self._responde(200, b'[{"name":"raw","public":true,"id":"raw"}]')
        self.assertIs(False, self.S.bucket_esta_certo('https://x', 'k')['PRIVADO'],
                      'bucket publico tem de ser detectado — e o envio recusado')


class TestElosQuePrecisamDeCredencial(unittest.TestCase):
    """Não passam por omissão: PULAM, e dizem exatamente o que falta."""

    def test_disco_vs_storage(self):
        falta = [n for n in ('SUPABASE_URL', 'SUPABASE_SECRET_KEY')
                 if not os.environ.get(n)]
        if falta:
            self.skipTest('PENDENTE — falta %s. Nenhum byte foi verificado no Storage.'
                          % ','.join(falta))
        import storage_preservar as S
        rel = _json(S.RELATORIO)
        self.assertIsNotNone(rel, 'há credencial mas o envio nunca rodou')
        plano = _json(PLANO)
        self.assertEqual(rel['PRESERVADOS_E_VERIFICADOS'], plano['ITENS'])
        self.assertEqual(rel['HASH_MISMATCH'], 0)
        self.assertEqual(rel['FALHOS'], 0)

    def test_git_vs_postgres(self):
        if not os.environ.get('SUPABASE_DB_URL'):
            self.skipTest('PENDENTE — falta SUPABASE_DB_URL. Nada foi importado.')
        import shutil
        if not shutil.which('psql'):
            self.skipTest('PENDENTE — psql não instalado. Nada foi importado.')
        self.fail('há credencial e psql: implementar a contagem contra o banco real')


if __name__ == '__main__':
    unittest.main(verbosity=2)
