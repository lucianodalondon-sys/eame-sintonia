#!/usr/bin/env python3
"""M2 — a primeira rota forward: DERIVED → STRUCTURED → ADMISSION.

    A ROTA NASCE INSTRUMENTADA, OU NAO NASCE.

Estas provas correm contra PostgreSQL 16 descartavel com a migration 024, e
usam texto derivado REAL do corpo italiano preservado. Nada e fabricado: nem
`raw_asset`, nem `collection_run`, nem `source_id`, nem `captured_at`.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                       # noqa: E402,F401
import admissao                       # noqa: E402
import coleta_checkpoint as cc        # noqa: E402
import diagnostico as dg              # noqa: E402
import falhas                         # noqa: E402
import rastro_da_coleta as rastro     # noqa: E402
import rota_forward_documento as m2   # noqa: E402
import social_persistencia as sp      # noqa: E402
import executor_texto_de_pdf as ex    # noqa: E402
# ⚠️ OS DOIS DONOS QUE A PROVA PASSA A USAR EM VEZ DE OS IMITAR:
#     leis/artefato.py      como o EXECUTOR entrega
#     coleta/ingresso.py    como isso vira a lingua do ARMAZEM
# Imitar um contrato a mao e ter uma segunda copia dele que nao e conferida
# por ninguem — e foi assim que esta prova envelheceu sem dar erro.
from leis import artefato as _art     # noqa: E402
from coleta import ingresso as _ing   # noqa: E402
from guarda.preservar_coleta import (ArmazemDeMentira, preservar,  # noqa: E402
                                     sha256)

import importlib.util as _u           # noqa: E402
_spec = _u.spec_from_file_location(
    'prova_pg', os.path.join(RAIZ, 'provas', 'preservar_coleta_no_postgres.py'))
_pg = _u.module_from_spec(_spec)
_spec.loader.exec_module(_pg)

LOJA = os.path.join(RAIZ, 'data', 'collection-store', 'italy', 'IT-T2-002')

DSN = os.environ.get('BANCO_DESCARTAVEL_URL', '')
TEXTOS = os.path.join(RAIZ, 'data', 'derivados', 'texto')


def _tem_banco():
    if not DSN:
        return False, 'BANCO_DESCARTAVEL_URL nao definida'
    try:
        b = cc.Banco(DSN)
        b.executa('select 1 from public.etapa_da_corrida limit 1')
        b.executa('select 1 from public.conteudo limit 1')
        return True, ''
    except Exception as e:
        return False, str(e)[:110]


TEM, PORQUE = _tem_banco()


def _texto_real(precisa=None):
    """Um texto derivado REAL da arvore. Nao se inventa corpo."""
    for nome in sorted(os.listdir(TEXTOS)):
        if not nome.endswith('.txt'):
            continue
        t = open(os.path.join(TEXTOS, nome), encoding='utf-8',
                 errors='ignore').read()
        if precisa is None or precisa.lower() in t.lower():
            return nome[:-4], t
    raise AssertionError('nenhum texto derivado real com %r' % precisa)


@unittest.skipUnless(TEM, 'sem PostgreSQL descartavel: %s' % PORQUE)
class Base(unittest.TestCase):
    RUN = 'RUN-M2-1'
    PREFIXO = 'RUN-M2'

    @classmethod
    def setUpClass(cls):
        cls.banco = cc.Banco(DSN)

    @classmethod
    def tearDownClass(cls):
        """⚠️ UMA SUITE QUE SUJA O BANCO QUEBRA QUEM CORRER A SEGUIR.

        Esta deixava `raw_asset` para tras — o `setUp` limpava ao ENTRAR, e nao
        ao SAIR. A suite seguinte apagava `collection_run` e batia na chave
        estrangeira: 40 erros noutro ficheiro, causados por este.

        A ordem e a das dependencias, e nao a alfabetica.
        """
        for sql in (
            "delete from public.etapa_da_corrida where run_id like '%s%%'",
            "delete from public.conteudo_visto_em where run_id like '%s%%'",
            "delete from public.conteudo where run_id like '%s%%'",
            "delete from public.derived_artifact where raw_asset_id in"
            " (select id from public.raw_asset where run_id like '%s%%')",
            "delete from public.raw_asset where run_id like '%s%%'",
            "delete from public.collection_run where run_id like '%s%%'",
        ):
            try:
                cls.banco.executa(sql % cls.PREFIXO)
            except Exception:                                # noqa: BLE001
                pass

        # ⚠️ A FIXTURA DE IDENTIDADE TAMBEM E SUJIDADE.
        # `provas/a_autoridade_da_fonte.py` (AU8) mede que MEDIR a autoridade
        # nao escreve identidade nenhuma. Se esta suite correr antes e deixar
        # canal/origem/organizacao para tras, AU8 le linhas que nao sao dela e
        # da FAIL — nao por defeito do codigo, mas por lixo deste ficheiro.
        # A ordem e a das dependencias: canal -> origem -> organizacao.
        for sql in (
            "delete from public.canal where plataforma = 'web'"
            " and channel_id = 'IT-T2-002'",
            "delete from public.origem where rotulo = 'IT-OWN-003'",
            "delete from public.organizacao where nome_canonico like 'ARPAV%'",
        ):
            try:
                cls.banco.executa(sql)
            except Exception:                                # noqa: BLE001
                pass

    def setUp(self):
        """⚠️ A CORRIDA NASCE DO DONO DO BRUTO, e nao deste teste.

        A travessia comeca ANTES do bruto: quem escreve `raw_asset` e
        `guarda/preservar_coleta.py`, e e ele que abre o `collection_run`.
        Criar a linha aqui fazia o dono encontrar a corrida ja aberta, e a
        preservacao nao acontecia — foi assim que esta prova falhou primeiro.
        """
        self._limpar()
        self.canal_id = self._canal()

    def _canal(self):
        """A PRE-CONDICAO DE IDENTIDADE, resolvida EXPLICITAMENTE.

        ⚠️ ACHADO REAL DA M2, e a casa esta certa a recusar. `exigir_canal`
        devolve `CHANNEL_IDENTITY_NOT_RESOLVED` porque criar um canal exige
        decidir DE QUEM ele e — `origem` tem constraint que exige pessoa OU
        organizacao, e o writer nao tem autoridade para a escolher:

            CHANNEL_ID PROVA O CANAL, NAO PROVA A ORIGEM.

        Nenhum dono forward resolve isto hoje. Fica declarado como GAP no
        ledger. Aqui a identidade e resolvida NO BANCO DESCARTAVEL, com dados
        REAIS do catalogo — `IT-T2-002` e a ARPAV, `OWNER_ID: IT-OWN-003`, em
        `candidatas/ITALY-SOURCE-MASTER-V1.json`. Nao se inventa organizacao;
        escreve-se a que o catalogo ja nomeia.
        """
        b = self.banco
        # ⚠️ `on conflict do nothing` NAO DEDUPLICA SEM CONSTRAINT UNICA.
        # Nao ha unique em `organizacao.nome_canonico` nem em `origem.rotulo`,
        # entao a clausula nunca dispara e cada metodo inseria outra linha:
        # medido, 23 organizacoes e 23 origens ao fim da suite. A deduplicacao
        # tem de ser explicita — `where not exists`.
        org = b.executa(
            "with novo as (insert into public.organizacao (nome_canonico, tipo)"
            " select 'ARPAV — Agenzia Regionale per la Prevenzione e"
            " Protezione Ambientale del Veneto', 'orgao_publico'"
            " where not exists (select 1 from public.organizacao"
            "   where nome_canonico like 'ARPAV%') returning id)"
            " select coalesce((select id from novo),"
            "  (select id from public.organizacao where nome_canonico like 'ARPAV%'))")
        org_id = int(org[0][0])
        ori = b.executa(
            "with novo as (insert into public.origem (organizacao_id, rotulo)"
            " select %d, 'IT-OWN-003' where not exists"
            "  (select 1 from public.origem where rotulo = 'IT-OWN-003')"
            " returning id)"
            " select coalesce((select id from novo),"
            "  (select id from public.origem where rotulo = 'IT-OWN-003'))"
            % org_id)
        origem_id = int(ori[0][0])
        can = b.executa(
            "with novo as (insert into public.canal"
            " (origem_id, plataforma, channel_id, url)"
            " values (%d, 'web', 'IT-T2-002', 'https://www.arpa.veneto.it/')"
            " on conflict (plataforma, channel_id) do nothing returning id)"
            " select coalesce((select id from novo),"
            "  (select id from public.canal where plataforma='web'"
            "     and channel_id='IT-T2-002'))" % origem_id)
        return int(can[0][0])

    def _pdf_real(self):
        """Um PDF REAL do armazem da coleta, fonte IT-T2-002 (ARPAV)."""
        for base, _d, ficheiros in os.walk(LOJA):
            for f in sorted(ficheiros):
                if f.endswith('.pdf'):
                    return os.path.join(base, f)
        raise AssertionError('nenhum PDF real de IT-T2-002 no armazem')

    def _bruto_real(self, run_id):
        """O bruto entra pelo DONO CANONICO, e o id vem do banco.

        ⚠️ NAO se escreve `insert into raw_asset` aqui. Uma prova que escreve a
        linha a mao prova o SQL dela propria — nao o caminho que a casa corre.
        """
        caminho = self._pdf_real()
        dados = open(caminho, 'rb').read()
        corrida = {'RUN_ID': run_id, 'PLATFORM': 'local', 'ACTOR': 'm2r',
                   'ACTOR_VERSION': '1', 'SOURCE_COUNTRY': 'IT',
                   'MISSION': 'M2R end-to-end',
                   'STARTED_AT': '2026-09-08T00:00:00Z',
                   'RULE_VERSION': '1', 'CAPTURE_METHOD': 'HTTP_GET'}

        # ── A FICHA DO ARMAZEM VEM DO TRADUTOR DA PRODUCAO ──────────────
        # ⚠️ ISTO ERA UM DICIONARIO ESCRITO A MAO, E ELE ENVELHECEU. Ele
        # entregava `SOURCE_SLUG` e NAO entregava `SOURCE_ID`; depois da B5B o
        # dono do RAW recusa observacao sem fonte real, e esta prova deixou de
        # correr — 21 erros contra PostgreSQL real. Medido em
        # `C-REMEASURE-COLLECTION-V1-CLOSE-GATES` como `G-E2E-01`.
        #
        # A ESTRADA NAO ESTAVA PARTIDA: a producao ja carregava `SOURCE_ID`
        # por `ingresso.para_o_dono_do_raw`. Era o RETRATO que estava velho.
        #
        #     UM FIXTURE QUE ENTREGA MENOS DO QUE A PRODUCAO ENTREGA
        #     REPROVA A ESTRADA POR UM DEFEITO QUE E DELE.
        #
        # Remendar os campos em falta a mao consertaria hoje e voltaria a
        # envelhecer amanha. Agora a prova fala pelo MESMO tradutor que a
        # producao fala — se o contrato mudar, ela segue sozinha.
        #
        #     PRODUCTION CONTRACT -> TEST FOLLOWS,
        #     e nunca STALE TEST -> PRODUCTION WEAKENED.
        #
        # A fonte NAO e deduzida do caminho: e declarada aqui, e `LOJA` so
        # percorre o armazem de IT-T2-002 — a declaracao e verdadeira sobre o
        # ficheiro que ela escolhe.
        ficha = _art.raw_do_disco(
            caminho, RAIZ,
            COUNTRY_SCOPE='IT',
            SOURCE_ID='IT-T2-002',
            SOURCE_URL='https://www.arpa.veneto.it/%s'
                       % os.path.basename(caminho),
            COLLECTED_AT='2026-09-02T15:20:48Z')
        art = _ing.para_o_dono_do_raw(ficha, {})

        memoria = _pg.MemoriaPostgres(DSN)
        armazem = ArmazemDeMentira()
        preservar(corrida, [art], armazem, lambda o: dados, memoria=memoria,
                  terminou_em='2026-09-08T00:05:00Z')
        raw_id = int(memoria._valor(
            "select id from public.raw_asset where run_id = '%s'"
            " and sha256 = '%s'" % (run_id, sha256(dados))))
        return raw_id, caminho, armazem, memoria

    def _unidade(self, precisa='parassita'):
        cid, texto = _texto_real(precisa)
        return {
            'CONTENT_ID': cid,
            'TEXTO': texto,
            'TIPO': 'nota_tecnica',
            # A identidade e da UNIDADE, e ela prova-a: o bruto veio de
            # data/collection-store/italy/IT-T2-002/, e IT-T2-002 existe no
            # catalogo. RC-1 e a classe por onde ele entrou.
            'SOURCE_ID': 'IT-T2-002',
            'ROUTE_CLASS_ID': 'RC-1',
            'RAW_ASSET_ID': 1,
            'CAPTURED_AT': '2026-09-02T15:20:48Z',
            'URL': 'https://www.arpa.veneto.it/bollettini/agro_24.pdf',
        }

    def _passagens(self, run_id=None):
        return rastro.passagens(self.banco, run_id=run_id or self.RUN)

    def _limpar(self):
        b = self.banco
        for sql in (
            "delete from public.etapa_da_corrida where run_id like '%s%%'",
            "delete from public.conteudo_visto_em where run_id like '%s%%'",
            "delete from public.conteudo where run_id like '%s%%'",
            "delete from public.derived_artifact where raw_asset_id in"
            " (select id from public.raw_asset where run_id like '%s%%')",
            "delete from public.raw_asset where run_id like '%s%%'",
            "delete from public.collection_run where run_id like '%s%%'",
        ):
            b.executa(sql % self.PREFIXO)

    def _travessia(self, universo=m2.UNIVERSO_PADRAO, unidade_extra=None):
        """A travessia REAL, do bruto preservado ate a porta.

        Partilhada pelas classes de falha para que o defeito nasca DENTRO da
        mesma cadeia end-to-end, e nao num atalho que comeca a meio.
        """
        if not ex.ha_ferramenta():
            self.skipTest('pdftotext nao esta nesta maquina')
        raw_id, pdf, armazem, memoria = self._bruto_real(self.RUN)
        unidade = {
            'RAW_ASSET_ID': raw_id, 'PDF': pdf, 'TIPO': 'nota_tecnica',
            'SOURCE_ID': 'IT-T2-002', 'ROUTE_CLASS_ID': 'RC-1',
            'CAPTURED_AT': '2026-09-02T15:20:48Z',
            'URL': 'https://www.arpa.veneto.it/bollettini/',
        }
        unidade.update(unidade_extra or {})
        return unidade, m2.atravessar(
            self.banco, unidade=unidade, run_id=self.RUN, armazem=armazem,
            memoria=memoria, canal_id=self.canal_id, universo=universo)


class M2_TravessiaUnica(Base):
    """A pergunta da M2R, e ela e uma so.

        PEGAMOS UMA UNIDADE REAL E VIMO-LA PASSAR, NA MESMA VIAGEM, POR
        DERIVED -> STRUCTURED -> ADMISSION?

    Se a resposta vier de juntar duas provas: NAO. Estas provas correm UMA
    execucao e perguntam ao banco o que ela deixou.
    """

    RUN = 'RUN-M2-E2E'

    def _correr(self, universo=m2.UNIVERSO_PADRAO):
        return self._travessia(universo=universo)
        raw_id, pdf, armazem, memoria = self._bruto_real(self.RUN)
        unidade = {
            'RAW_ASSET_ID': raw_id,
            'PDF': pdf,
            'TIPO': 'nota_tecnica',
            # A identidade e da UNIDADE e ela prova-a: o bruto veio de
            # data/collection-store/italy/IT-T2-002/, e IT-T2-002 esta no
            # catalogo (ARPAV). RC-1 e a classe por onde ele entrou.
            'SOURCE_ID': 'IT-T2-002',
            'ROUTE_CLASS_ID': 'RC-1',
            'CAPTURED_AT': '2026-09-02T15:20:48Z',
            'URL': 'https://www.arpa.veneto.it/bollettini/',
        }
        return unidade, m2.atravessar(
            self.banco, unidade=unidade, run_id=self.RUN, armazem=armazem,
            memoria=memoria, canal_id=self.canal_id, universo=universo)

    def test_as_TRES_etapas_estao_no_banco_para_o_MESMO_run(self):
        """A prova que torna impossivel o falso verde de duas corridas."""
        self._correr()
        etapas = [p['ETAPA'] for p in self._passagens()]
        self.assertEqual(['DERIVED', 'STRUCTURED', 'ADMISSION'], etapas,
                         'a travessia nao deixou as tres no mesmo run')

    def test_a_derivacao_foi_MESMO_chamada_nesta_execucao(self):
        """PRELOADED DERIVED CONTENT != DERIVATION EXECUTED IN THIS FLOW."""
        _u, r = self._correr()
        d = r['DERIVED']
        self.assertIsNotNone(d, 'DERIVED nao correu')
        self.assertTrue(d.get('RESULTADOS'), 'a derivacao nao produziu recibo')
        porta = d['RESULTADOS'][0]['PORTA']
        self.assertIn(porta, ('PASSED', 'REUSED'),
                      'a derivacao nao entregou: %s' % porta)
        p = [x for x in self._passagens() if x['ETAPA'] == 'DERIVED'][0]
        self.assertEqual('RAW', p['EDGE_FROM'])

    def test_o_texto_de_STRUCTURED_veio_da_derivacao_desta_execucao(self):
        """⚠️ ESTA E A ARESTA REAL, e nao o rotulo `edge_from`.

            EDGE LABEL != DATA DEPENDENCY.

        O texto e lido do armazem pelo `storage_path` da linha que o dono do
        derivado escreveu NESTA execucao. Se a derivacao nao tivesse
        produzido, nao haveria o que ler — e a cadeia parava em DERIVED.
        """
        _u, r = self._correr()
        caminho = r.get('TEXTO_VEIO_DE')
        self.assertTrue(caminho, 'STRUCTURED nao disse de onde veio o texto')
        self.assertEqual(r['DERIVED']['RESULTADOS'][0]['STORAGE_PATH'],
                         caminho,
                         'o texto nao veio do artefato derivado desta corrida')

    def test_a_identidade_do_conteudo_e_o_sha_do_derivado(self):
        """A unidade que segue e a que SAIU, e nao a que entrou."""
        _u, r = self._correr()
        linha = r['DERIVED']['RESULTADOS'][0]['LINHA'] or {}
        sha = linha.get('sha256')
        self.assertTrue(sha, 'o derivado nao trouxe sha')
        n = self.banco.executa(
            "select count(*) from public.conteudo where run_id = '%s'"
            " and content_id = '%s'" % (self.RUN, sha))
        self.assertEqual('1', n[0][0],
                         'o conteudo estruturado nao e identificado pelo '
                         'artefato derivado que o originou')

    def test_a_linhagem_fecha_no_banco(self):
        """derived_artifact aponta para o raw_asset que a corrida preservou."""
        unidade, _r = self._correr()
        l = self.banco.executa(
            "select d.raw_asset_id, r.run_id from public.derived_artifact d"
            " join public.raw_asset r on r.id = d.raw_asset_id"
            " where d.raw_asset_id = %d" % unidade['RAW_ASSET_ID'])
        self.assertTrue(l, 'nao ha derived_artifact para este bruto')
        self.assertEqual(str(unidade['RAW_ASSET_ID']), l[0][0])
        self.assertEqual(self.RUN, l[0][1],
                         'o bruto derivado nao e o desta corrida')

    def test_mesmo_SOURCE_ID_e_ROUTE_CLASS_nas_tres_etapas(self):
        self._correr()
        vistas = self.banco.executa(
            "select distinct coalesce(source_id,'<NULL>'),"
            " coalesce(route_class_id,'<NULL>')"
            " from public.etapa_da_corrida where run_id = '%s'" % self.RUN)
        self.assertEqual([['IT-T2-002', 'RC-1']], [list(v) for v in vistas])

    def test_a_contabilidade_fecha_nas_tres(self):
        self._correr()
        ps = self._passagens()
        self.assertEqual(3, len(ps))
        for p in ps:
            self.assertEqual(0, p['UNACCOUNTED'], p['ETAPA'])
            self.assertEqual(p['INPUT_COUNT'], p['ACCOUNTED'], p['ETAPA'])

    def test_o_grao_muda_e_nao_se_publica_rendimento(self):
        self._correr()
        for p in self._passagens():
            self.assertNotEqual('-', p['INPUT_GRAIN'], p['ETAPA'])
            self.assertIsNone(rastro.rendimento(p).get('YIELD'), p['ETAPA'])

    def test_os_artefatos_existem_mesmo_e_nao_so_a_telemetria(self):
        """TELEMETRY SAYS PASS != ARTIFACT EXISTS. Pergunta-se ao banco."""
        unidade, r = self._correr()
        d = self.banco.executa(
            "select count(*) from public.derived_artifact"
            " where raw_asset_id = %d" % unidade['RAW_ASSET_ID'])
        self.assertEqual('1', d[0][0], 'derived_artifact nao existe')
        c = self.banco.executa(
            "select count(*), max(tipo::text) from public.conteudo"
            " where run_id = '%s'" % self.RUN)
        self.assertEqual('1', c[0][0], 'conteudo estruturado nao existe')
        self.assertEqual('nota_tecnica', c[0][1])
        self.assertIsNotNone(r['ADMISSION'], 'nao houve decisao de admissao')
        self.assertIn(r['ADMISSION'].resultado, admissao.RESULTADOS)

    def test_a_ordem_e_a_da_rota(self):
        self._correr()
        ordem = self.banco.executa(
            "select etapa::text from public.etapa_da_corrida"
            " where run_id = '%s' order by id" % self.RUN)
        self.assertEqual(['DERIVED', 'STRUCTURED', 'ADMISSION'],
                         [o[0] for o in ordem])

    def test_nenhum_READY_nesta_travessia(self):
        self._correr()
        n = self.banco.executa(
            "select count(*) from public.etapa_da_corrida"
            " where run_id = '%s' and etapa = 'READY'" % self.RUN)
        self.assertEqual('0', n[0][0], 'ADMISSION PASS virou READY PASS')

    def test_o_SOURCE_ID_que_ATERRA_no_raw_e_o_do_canario(self):
        """⚠️ VALOR, E NAO ESTRUTURA: LER DO BANCO A FONTE QUE FICOU.

        Um defeito que devolve o valor CERTO so a estrutura denuncia. Um que
        devolve OUTRO valor so o banco denuncia — e nenhum teste de texto o
        apanha. Esta pergunta ao `raw_asset` qual fonte aterrou, e compara-a
        com o canario declarado em `system-map/data/estradas-it.model.json`.

        A comparacao e contra uma fonte de FORA deste ficheiro. Um numero
        conferido contra ele proprio nao e uma conferencia: e um eco.

        ⚠️ ESTA PROVA VIVE AQUI, E NAO NO FICHEIRO DE GUARDAS, PORQUE E AQUI
        QUE AS LINHAS EXISTEM. A `tearDownClass` limpa o banco ao sair, entao
        uma prova noutro modulo encontrava a tabela vazia e SALTAVA — em
        silencio, em todas as corridas. SKIP != PASS.
        """
        self._correr()
        with open(os.path.join(RAIZ, 'system-map', 'data',
                               'estradas-it.model.json'), encoding='utf-8') as f:
            canario = json.load(f)['CANARIO']['SOURCE_ID']
        fontes = self.banco.executa(
            "select distinct coalesce(source_id,'<NULL>')"
            " from public.raw_asset where run_id like '%s%%'" % self.PREFIXO)
        self.assertEqual([[canario]], [list(x) for x in fontes],
                         'aterrou no raw_asset uma fonte que nao e a do'
                         ' canario declarado')

    def test_se_a_derivacao_nao_entregar_a_cadeia_para_em_DERIVED(self):
        """A cadeia diz a verdade sobre onde parou — nao inventa STRUCTURED."""
        raw_id, pdf, armazem, memoria = self._bruto_real(self.RUN)
        unidade = {'RAW_ASSET_ID': raw_id, 'PDF': pdf,
                   'SOURCE_ID': 'IT-T2-002', 'ROUTE_CLASS_ID': 'RC-1'}

        def nao_entrega(raw_asset_id, pdf_, armazem_, memoria_, relogio=None):
            return {'ESTADO': 'SEM_DERIVADO',
                    'MOTIVO_DO_EXECUTOR': 'NEEDS_OCR'}

        import derivacao_forward as fwd
        original, fwd.ex.derivar_um = fwd.ex.derivar_um, nao_entrega
        try:
            saida = m2.atravessar(self.banco, unidade=unidade, run_id=self.RUN,
                                  armazem=ArmazemDeMentira(), memoria=memoria,
                                  canal_id=self.canal_id)
        finally:
            fwd.ex.derivar_um = original
        self.assertIsNone(saida['STRUCTURED'])
        self.assertIsNone(saida['ADMISSION'])
        self.assertIn('nao entregou', saida['PORQUE_PAROU'])
        etapas = [p['ETAPA'] for p in self._passagens()]
        self.assertEqual(['DERIVED'], etapas,
                         'a cadeia inventou etapas sem derivado')


class M2_FalhaEmStructured(Base):
    """FALHA 1 — STRUCTURED quebra DENTRO da cadeia end-to-end.

    O defeito nasce depois de DERIVED ter sido realmente chamado: a derivacao
    entrega, e e a estruturacao que nao passa.
    """

    RUN = 'RUN-M2-FALHA-S'

    def test_a_falha_fica_em_STRUCTURED_e_ADMISSION_nao_corre(self):
        # ⚠️ A PRE-CONDICAO DA CADEIA E QUE O BRUTO TENHA DURADO. Sem
        # `RAW_ASSET_ID` o dono de `conteudo` RECUSA — e essa recusa e o
        # defeito controlado, depois de DERIVED ter corrido.
        _u, r = self._travessia(unidade_extra=None)
        # a derivacao correu de verdade
        self.assertIsNotNone(r['DERIVED'])
        por = {p['ETAPA']: p for p in self._passagens()}
        self.assertIn('DERIVED', por)

        # agora a mesma cadeia, com a estruturacao a nao poder prosseguir
        self._limpar(); self.canal_id = self._canal()
        raw_id, pdf, armazem, memoria = self._bruto_real(self.RUN)
        unidade = {'RAW_ASSET_ID': raw_id, 'PDF': pdf, 'TIPO': 'nota_tecnica',
                   'SOURCE_ID': 'IT-T2-002', 'ROUTE_CLASS_ID': 'RC-1'}
        original = sp.persistir_video
        try:
            sp.persistir_video = lambda *a, **k: {
                'STATE': sp.RAW_NAO_DUROU, 'CONTENT_ID': k.get('content_id'),
                'PORQUE': 'defeito controlado da M2R'}
            m2.atravessar(self.banco, unidade=unidade, run_id=self.RUN,
                          armazem=armazem, memoria=memoria,
                          canal_id=self.canal_id)
        finally:
            sp.persistir_video = original

        por = {p['ETAPA']: p for p in self._passagens()}
        self.assertIn('DERIVED', por, 'a cadeia nem chegou a derivar')
        self.assertIn('STRUCTURED', por)
        self.assertIn('ADMISSION', por)
        self.assertEqual('NOT_RUN', por['ADMISSION']['ESTADO'],
                         'a porta virou erro porque a de cima nao passou')
        self.assertEqual(0, por['ADMISSION']['ERROR'],
                         'ERROR em cascata: um defeito a parecer dois')
        self.assertEqual(1, por['ADMISSION']['NOT_RUN'])
        self.assertEqual(dg.UPSTREAM_NOT_RUN, por['ADMISSION']['DIAGNOSTIC_CODE'])
        self.assertEqual('DERIVED', por['ADMISSION']['LAST_GOOD_ARTIFACT'])

    def test_a_quebra_de_verdade_da_FAIL_com_estado_canonico(self):
        """Uma excecao real dentro do dono, e nao uma recusa de contrato."""
        raw_id, pdf, armazem, memoria = self._bruto_real(self.RUN)
        unidade = {'RAW_ASSET_ID': raw_id, 'PDF': pdf, 'TIPO': 'nota_tecnica',
                   'SOURCE_ID': 'IT-T2-002', 'ROUTE_CLASS_ID': 'RC-1',
                   'TEXTO': 'x', 'CONTENT_ID': None}
        with self.assertRaises(Exception):
            m2.estruturar(self.banco, unidade=unidade, run_id=self.RUN,
                          canal_id=self.canal_id)
        s_ = [p for p in self._passagens() if p['ETAPA'] == 'STRUCTURED']
        self.assertTrue(s_, 'a quebra nao deixou linha')
        self.assertEqual('FAIL', s_[-1]['ESTADO'])
        self.assertIn(s_[-1]['CANONICAL_STATE'], falhas.ESTADOS)
        self.assertEqual(dg.STRUCTURED_NOT_CONNECTED, s_[-1]['DIAGNOSTIC_CODE'])
        self.assertEqual('DERIVED', s_[-1]['LAST_GOOD_ARTIFACT'])


class M2_PortaRecusa(Base):
    """FALHA 2 — a porta diz NAO. E uma decisao, e nao um defeito."""

    RUN = 'RUN-M2-RECUSA'

    def test_um_NAO_da_porta_sai_por_REJECTED_e_nao_por_ERROR(self):
        # Um boletim de praga julgado contra o universo do CONCORRENTE: a
        # porta olha, e diz que nao serve PARA ESTE universo. E o trabalho dela.
        self._travessia(universo='T9')
        a = [p for p in self._passagens() if p['ETAPA'] == 'ADMISSION'][0]
        self.assertEqual('PASS', a['ESTADO'],
                         'a porta a funcionar apareceu como etapa falhada')
        self.assertEqual(0, a['ERROR'], 'uma recusa virou falha tecnica')
        self.assertEqual(1, a['REJECTED'] + a['UNKNOWN'])
        self.assertEqual(0, a['UNACCOUNTED'])

    def test_a_recusa_deixa_testemunha(self):
        _u, r = self._travessia(universo='T9')
        d = r['ADMISSION']
        self.assertIsNotNone(d)
        self.assertIn(d.resultado, admissao.RESULTADOS)
        self.assertTrue(d.motivo, 'a porta recusou sem dizer porque')
        self.assertTrue(d.regra)
        self.assertEqual(self.RUN, d.corrida)

    def test_o_item_recusado_continua_contado(self):
        self._travessia(universo='T9')
        a = [p for p in self._passagens() if p['ETAPA'] == 'ADMISSION'][0]
        self.assertEqual(a['INPUT_COUNT'], a['ACCOUNTED'])


class M2_ReadyProvaNegativa(Base):
    """A M2 nao produz READY. Perguntado AO BANCO, e nao ao ficheiro."""

    RUN = 'RUN-M2-READY'

    def test_nenhum_READY_foi_emitido_por_esta_rota(self):
        self._travessia()
        n = self.banco.executa(
            "select count(*) from public.etapa_da_corrida"
            " where run_id = '%s' and etapa = 'READY'" % self.RUN)
        self.assertEqual('0', n[0][0],
                         'ADMISSION PASS virou READY PASS')

    def test_e_nenhum_READY_PASS_existe_sem_a_lei_de_READY(self):
        self._travessia()
        n = self.banco.executa(
            "select count(*) from public.etapa_da_corrida r"
            " where r.etapa = 'READY' and r.estado = 'PASS'"
            " and not exists (select 1 from public.etapa_da_corrida a"
            "                 where a.run_id = r.run_id"
            "                   and a.etapa = 'ADMISSION'"
            "                   and a.estado = 'PASS')")
        self.assertEqual('0', n[0][0])


class M2_E2E2_LinhagemCruzada(Base):
    """E2E-2 — derivado A, conteudo construido de B. O sistema recusa?

    MEDIDO ANTES DE DECIDIR: `public.conteudo` NAO tem chave estrangeira para
    `derived_artifact`. As colunas que existem sao `raw_asset_id`,
    `content_id` e `hash_conteudo`.

    A linhagem E verificavel — a costura escreve `content_id` = sha256 do
    artefato derivado, e `hash_conteudo` = hash do texto — mas isso e uma
    CONVENCAO DA COSTURA, e nao uma trava do banco. Um writer que escrevesse
    outra coisa nao seria recusado pelo Postgres.

        LINEAGE_PROOF_GAP: ha como CONFERIR, nao ha como IMPEDIR.

    Nao se inventou mecanismo para a mutacao passar. Provou-se o que existe, e
    declarou-se o que falta.
    """

    RUN = 'RUN-M2-E2E2'

    def test_o_conteudo_e_identificado_pelo_derivado_desta_execucao(self):
        """A conferencia que a costura torna possivel."""
        _u, r = self._travessia()
        sha = (r['DERIVED']['RESULTADOS'][0]['LINHA'] or {}).get('sha256')
        cruz = self.banco.executa(
            "select count(*) from public.conteudo c"
            " join public.derived_artifact d on d.sha256 = c.content_id"
            " where c.run_id = '%s'" % self.RUN)
        self.assertEqual('1', cruz[0][0],
                         'o conteudo estruturado nao casa com nenhum derivado')
        n = self.banco.executa(
            "select content_id from public.conteudo where run_id='%s'" % self.RUN)
        self.assertEqual(sha, n[0][0])

    def test_conteudo_de_OUTRO_derivado_e_detetavel(self):
        """A MUTACAO: estruturar com o texto de B declarando o derivado A."""
        if not ex.ha_ferramenta():
            self.skipTest('pdftotext nao esta nesta maquina')
        raw_id, pdf, armazem, memoria = self._bruto_real(self.RUN)
        unidade = {'RAW_ASSET_ID': raw_id, 'PDF': pdf, 'TIPO': 'nota_tecnica',
                   'SOURCE_ID': 'IT-T2-002', 'ROUTE_CLASS_ID': 'RC-1'}
        r = m2.derivar(self.banco, unidade=unidade, run_id=self.RUN,
                       armazem=armazem, memoria=memoria)
        sha_a = (r['RESULTADOS'][0]['LINHA'] or {}).get('sha256')

        # o conteudo e construido de OUTRO texto, mas continua a declarar A
        forjada = dict(unidade)
        forjada['TEXTO'] = 'texto que NAO saiu do derivado A'
        forjada['CONTENT_ID'] = sha_a
        m2.estruturar(self.banco, unidade=forjada, run_id=self.RUN,
                      canal_id=self.canal_id)

        # ⚠️ O CRUZAMENTO PASSA — e e por isso que ha um gap.
        # `content_id` continua a ser o sha de A, porque foi escrito a mao.
        cruz = self.banco.executa(
            "select count(*) from public.conteudo c"
            " join public.derived_artifact d on d.sha256 = c.content_id"
            " where c.run_id = '%s'" % self.RUN)
        self.assertEqual('1', cruz[0][0])

        # O que DETETA e comparar o corpo: `hash_conteudo` e o hash do TEXTO,
        # e ele nao bate com os bytes do derivado A.
        import social_persistencia as _sp
        h = self.banco.executa(
            "select hash_conteudo from public.conteudo where run_id='%s'"
            % self.RUN)[0][0]
        caminho = r['RESULTADOS'][0]['STORAGE_PATH']
        bytes_a = armazem.objetos[caminho][0]
        h_verdadeiro = _sp.hash_do_texto(bytes_a.decode('utf-8', 'replace'))
        self.assertNotEqual(h, h_verdadeiro,
                            'a forja nao foi detetavel: o hash do corpo bateu')

    def test_o_gap_esta_declarado_e_nao_fechado_com_uma_linha_bonita(self):
        """O banco NAO impede — e isso fica escrito, nao escondido."""
        cols = self.banco.executa(
            "select count(*) from information_schema.columns"
            " where table_name = 'conteudo' and column_name like '%deriv%'")
        self.assertEqual('0', cols[0][0],
                         'apareceu coluna de derivado em conteudo: o gap mudou '
                         'e o ledger tem de mudar com ele')
        led = json.load(open(os.path.join(RAIZ, 'system-map', 'data',
                                          'provas-de-execucao.json'),
                             encoding='utf-8'))
        r = led['PROVADOS']['coleta/rota_forward_documento.py']
        self.assertIn('LINEAGE_PROOF_GAP', json.dumps(r, ensure_ascii=False))



class M2_NaoCriouSegundoDono(unittest.TestCase):
    """A M2 COSE. Ela nao reimplementa nenhuma das tres decisoes."""

    def test_a_costura_nao_escreve_conteudo_por_si(self):
        fonte = open(os.path.join(RAIZ, 'coleta',
                                  'rota_forward_documento.py'),
                     encoding='utf-8').read()
        self.assertNotIn('insert into public.conteudo', fonte)
        self.assertNotIn('insert into public.derived_artifact', fonte)

    def test_a_costura_nao_reimplementa_a_peneira(self):
        fonte = open(os.path.join(RAIZ, 'coleta',
                                  'rota_forward_documento.py'),
                     encoding='utf-8').read()
        for regra in ('PERGUNTAS_DO_UNIVERSO', 'def decidir', 'def estagio'):
            self.assertNotIn(regra, fonte)

    def test_ela_chama_os_donos_canonicos(self):
        import ast
        fonte = open(os.path.join(RAIZ, 'coleta',
                                  'rota_forward_documento.py'),
                     encoding='utf-8').read()
        imports = set()
        for no in ast.walk(ast.parse(fonte)):
            if isinstance(no, ast.Import):
                imports |= {a.name.split('.')[0] for a in no.names}
            elif isinstance(no, ast.ImportFrom) and no.module:
                imports.add(no.module.split('.')[0])
        self.assertIn('social_persistencia', imports)
        self.assertIn('admissao', imports)
        self.assertIn('rastro_da_coleta', imports)


if __name__ == '__main__':
    unittest.main(verbosity=2)
