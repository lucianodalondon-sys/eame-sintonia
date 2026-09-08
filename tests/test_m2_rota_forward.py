#!/usr/bin/env python3
"""M2 — a primeira rota forward: DERIVED → STRUCTURED → ADMISSION.

    A ROTA NASCE INSTRUMENTADA, OU NAO NASCE.

Estas provas correm contra PostgreSQL 16 descartavel com a migration 024, e
usam texto derivado REAL do corpo italiano preservado. Nada e fabricado: nem
`raw_asset`, nem `collection_run`, nem `source_id`, nem `captured_at`.
"""
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

    def setUp(self):
        b = self.banco
        b.executa("delete from public.etapa_da_corrida where run_id like '%s%%'"
                  % self.PREFIXO)
        b.executa("delete from public.conteudo_visto_em where run_id like '%s%%'"
                  % self.PREFIXO)
        b.executa("delete from public.conteudo where run_id like '%s%%'"
                  % self.PREFIXO)
        b.executa("delete from public.collection_run where run_id like '%s%%'"
                  % self.PREFIXO)
        b.executa(
            "insert into public.collection_run (run_id, platform,"
            " source_country, started_at, status, rule_version)"
            " values ('%s','web','IT',now(),'rodando','v1')" % self.RUN)
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
        org = b.executa(
            "with novo as (insert into public.organizacao (nome_canonico, tipo)"
            " values ('ARPAV — Agenzia Regionale per la Prevenzione e"
            " Protezione Ambientale del Veneto', 'orgao_publico')"
            " on conflict do nothing returning id)"
            " select coalesce((select id from novo),"
            "  (select id from public.organizacao where nome_canonico like 'ARPAV%'))")
        org_id = int(org[0][0])
        ori = b.executa(
            "with novo as (insert into public.origem (organizacao_id, rotulo)"
            " values (%d, 'IT-OWN-003') on conflict do nothing returning id)"
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


class M2_CaminhoBom(Base):
    """A rota inteira, com uma unidade real."""

    def test_as_duas_etapas_da_M2_correram(self):
        m2.atravessar(self.banco, unidade=self._unidade(), run_id=self.RUN,
                      canal_id=self.canal_id)
        etapas = [p['ETAPA'] for p in self._passagens()]
        self.assertEqual(['STRUCTURED', 'ADMISSION'], etapas)

    def test_a_aresta_DERIVED_para_STRUCTURED_foi_observada(self):
        m2.atravessar(self.banco, unidade=self._unidade(), run_id=self.RUN,
                      canal_id=self.canal_id)
        s = [p for p in self._passagens() if p['ETAPA'] == 'STRUCTURED'][0]
        self.assertEqual('DERIVED', s['EDGE_FROM'])
        self.assertEqual('PASS', s['ESTADO'])

    def test_a_aresta_STRUCTURED_para_ADMISSION_foi_observada(self):
        m2.atravessar(self.banco, unidade=self._unidade(), run_id=self.RUN,
                      canal_id=self.canal_id)
        a = [p for p in self._passagens() if p['ETAPA'] == 'ADMISSION'][0]
        self.assertEqual('STRUCTURED', a['EDGE_FROM'])

    def test_o_registo_estruturado_existe_mesmo_no_banco(self):
        """Nao basta a telemetria dizer que passou: a linha tem de estar la."""
        m2.atravessar(self.banco, unidade=self._unidade(), run_id=self.RUN,
                      canal_id=self.canal_id)
        n = self.banco.executa(
            "select count(*), max(tipo::text) from public.conteudo"
            " where run_id = '%s'" % self.RUN)
        self.assertEqual('1', n[0][0])
        self.assertEqual('nota_tecnica', n[0][1],
                         'um boletim entrou no banco como outra especie')

    def test_a_contabilidade_fecha_nas_duas_etapas(self):
        m2.atravessar(self.banco, unidade=self._unidade(), run_id=self.RUN,
                      canal_id=self.canal_id)
        for p in self._passagens():
            self.assertEqual(0, p['UNACCOUNTED'], p['ETAPA'])
            self.assertEqual(p['INPUT_COUNT'], p['ACCOUNTED'], p['ETAPA'])

    def test_o_grao_muda_e_nao_se_publica_rendimento(self):
        m2.atravessar(self.banco, unidade=self._unidade(), run_id=self.RUN,
                      canal_id=self.canal_id)
        for p in self._passagens():
            self.assertNotEqual('-', p['INPUT_GRAIN'], p['ETAPA'])
            y = rastro.rendimento(p)
            self.assertIsNone(y.get('YIELD'),
                              '%s publicou rendimento entre graos' % p['ETAPA'])

    def test_a_identidade_da_unidade_viaja_com_ela(self):
        m2.atravessar(self.banco, unidade=self._unidade(), run_id=self.RUN,
                      canal_id=self.canal_id)
        vistas = self.banco.executa(
            "select distinct coalesce(source_id,'<NULL>'),"
            " coalesce(route_class_id,'<NULL>')"
            " from public.etapa_da_corrida where run_id = '%s'" % self.RUN)
        self.assertEqual([['IT-T2-002', 'RC-1']], [list(v) for v in vistas])

    def test_a_duracao_e_medida_e_o_custo_nao_e_inventado(self):
        m2.atravessar(self.banco, unidade=self._unidade(), run_id=self.RUN,
                      canal_id=self.canal_id)
        for p in self._passagens():
            self.assertGreaterEqual(p['DURACAO_MS'], 0)

    def test_reencontrar_a_mesma_unidade_e_REUSED_e_nao_PASSED_novo(self):
        u = self._unidade()
        m2.atravessar(self.banco, unidade=u, run_id=self.RUN,
                      canal_id=self.canal_id)
        m2.estruturar(self.banco, unidade=u, run_id=self.RUN,
                      canal_id=self.canal_id)
        s = [p for p in self._passagens() if p['ETAPA'] == 'STRUCTURED']
        self.assertEqual(2, len(s), 'a segunda passagem nao deixou linha')
        self.assertEqual(1, s[-1]['REUSED'])
        self.assertEqual(0, s[-1]['PASSED'])


class M2_FalhaEmStructured(Base):
    """FALHA 1 — STRUCTURED quebra. ADMISSION nao pode virar erro por isso."""

    RUN = 'RUN-M2-FALHA-S'

    def test_a_falha_fica_em_STRUCTURED_e_ADMISSION_nao_corre(self):
        u = self._unidade()
        # ⚠️ A PRE-CONDICAO DA CADEIA E QUE O BRUTO TENHA DURADO. Sem
        # `RAW_ASSET_ID` o dono RECUSA — e essa recusa e o defeito controlado.
        u['RAW_ASSET_ID'] = None
        m2.atravessar(self.banco, unidade=u, run_id=self.RUN,
                      canal_id=self.canal_id)
        por = {p['ETAPA']: p for p in self._passagens()}
        self.assertIn('STRUCTURED', por)
        self.assertIn('ADMISSION', por)
        self.assertEqual('NOT_RUN', por['ADMISSION']['ESTADO'],
                         'a porta virou erro porque a etapa de cima nao passou')
        self.assertEqual(0, por['ADMISSION']['ERROR'],
                         'ERROR em cascata: um defeito a parecer dois')
        self.assertEqual(1, por['ADMISSION']['NOT_RUN'])

    def test_a_etapa_que_nao_correu_diz_que_a_de_cima_nao_correu(self):
        u = self._unidade(); u['RAW_ASSET_ID'] = None
        m2.atravessar(self.banco, unidade=u, run_id=self.RUN,
                      canal_id=self.canal_id)
        a = [p for p in self._passagens() if p['ETAPA'] == 'ADMISSION'][0]
        self.assertEqual(dg.UPSTREAM_NOT_RUN, a['DIAGNOSTIC_CODE'])
        self.assertEqual('DERIVED', a['LAST_GOOD_ARTIFACT'])

    def test_a_quebra_de_verdade_da_FAIL_com_estado_canonico(self):
        """Uma excecao real dentro do dono, e nao uma recusa de contrato."""
        u = self._unidade()
        u['CONTENT_ID'] = None      # o writer vai rebentar a serializar
        with self.assertRaises(Exception):
            m2.estruturar(self.banco, unidade=u, run_id=self.RUN,
                          canal_id=self.canal_id)
        s = [p for p in self._passagens() if p['ETAPA'] == 'STRUCTURED']
        self.assertTrue(s, 'a quebra nao deixou linha')
        self.assertEqual('FAIL', s[-1]['ESTADO'])
        self.assertIn(s[-1]['CANONICAL_STATE'], falhas.ESTADOS)
        self.assertEqual(dg.STRUCTURED_NOT_CONNECTED, s[-1]['DIAGNOSTIC_CODE'])
        self.assertEqual('DERIVED', s[-1]['LAST_GOOD_ARTIFACT'])


class M2_PortaRecusa(Base):
    """FALHA 2 — a porta diz NAO. Isso e uma decisao, e nao um defeito."""

    RUN = 'RUN-M2-RECUSA'

    def test_um_NAO_da_porta_sai_por_REJECTED_e_nao_por_ERROR(self):
        # Um boletim de praga julgado contra o universo REGULATORIO: a porta
        # olha, e diz que nao serve PARA ESTE universo. E o trabalho dela.
        u = self._unidade('parassita')
        r = m2.atravessar(self.banco, unidade=u, run_id=self.RUN,
                          canal_id=self.canal_id, universo='T9')
        a = [p for p in self._passagens() if p['ETAPA'] == 'ADMISSION'][0]
        self.assertEqual('PASS', a['ESTADO'],
                         'a porta a funcionar apareceu como etapa falhada')
        self.assertEqual(0, a['ERROR'], 'uma recusa virou falha tecnica')
        self.assertEqual(1, a['REJECTED'] + a['UNKNOWN'])
        self.assertEqual(0, a['UNACCOUNTED'])

    def test_a_recusa_deixa_testemunha(self):
        u = self._unidade('parassita')
        r = m2.atravessar(self.banco, unidade=u, run_id=self.RUN,
                          canal_id=self.canal_id, universo='T9')
        d = r['ADMISSION']
        self.assertIsNotNone(d)
        self.assertIn(d.resultado, admissao.RESULTADOS)
        self.assertTrue(d.motivo, 'a porta recusou sem dizer porque')
        self.assertTrue(d.regra)
        self.assertEqual(self.RUN, d.corrida)

    def test_o_item_recusado_continua_contado(self):
        u = self._unidade('parassita')
        m2.atravessar(self.banco, unidade=u, run_id=self.RUN,
                      canal_id=self.canal_id, universo='T9')
        a = [p for p in self._passagens() if p['ETAPA'] == 'ADMISSION'][0]
        self.assertEqual(a['INPUT_COUNT'], a['ACCOUNTED'])


class M2_ReadyProvaNegativa(Base):
    """A M2 nao produz READY. Perguntado AO BANCO, e nao ao ficheiro."""

    RUN = 'RUN-M2-READY'

    def test_nenhum_READY_foi_emitido_por_esta_rota(self):
        m2.atravessar(self.banco, unidade=self._unidade(), run_id=self.RUN,
                      canal_id=self.canal_id)
        n = self.banco.executa(
            "select count(*) from public.etapa_da_corrida"
            " where run_id = '%s' and etapa = 'READY'" % self.RUN)
        self.assertEqual('0', n[0][0],
                         'ADMISSION PASS virou READY PASS')

    def test_e_nenhum_READY_PASS_existe_sem_a_lei_de_READY(self):
        m2.atravessar(self.banco, unidade=self._unidade(), run_id=self.RUN,
                      canal_id=self.canal_id)
        n = self.banco.executa(
            "select count(*) from public.etapa_da_corrida r"
            " where r.etapa = 'READY' and r.estado = 'PASS'"
            " and not exists (select 1 from public.etapa_da_corrida a"
            "                 where a.run_id = r.run_id"
            "                   and a.etapa = 'ADMISSION'"
            "                   and a.estado = 'PASS')")
        self.assertEqual('0', n[0][0])


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
