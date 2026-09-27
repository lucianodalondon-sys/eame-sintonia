#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACERVO-ORGANIZADO (D114 + correcao do dono 27/09 16:50) — atacado.

    python3 -m unittest -v tests.test_acervo_organizado

Prova que:
  S  o sha do POTE-R7 contra o manifesto confere SO de duas formas (byte a byte, ou
     trocando LF por CRLF num ficheiro sem CR), e qualquer outro byte mudado da DIFERENTE;
  L  o pote da Label Intelligence e a saida selada da ferramenta, sem um numero mudado:
     selo recalculado, 166/210/54, cada registo byte a byte, o payload reconstruido do pote
     da o MESMO selo, PRODUZIDO_POR = a ferramenta, e o leitor do casco aceita-o;
  I  o inventario classifica cada conjunto numa das cinco classes, com motivo; demo,
     oportunidade e CLIENT_SAFE=false ficam FORA; a ENTRADA da Intelligence so tem itens
     coletados do conjunto canonico, com a data do proprio registo, e nao vai ao casco;
  D  a auditoria D97 commitada e a que o portao mede hoje.
"""
import copy
import hashlib
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import publicar_pote_aprovado as PUB  # noqa: E402
import pote_ferramenta_label as LI  # noqa: E402


def _j(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as fh:
        return json.load(fh)


def _ler(caminho, modo='r'):
    with open(caminho, modo, **({} if 'b' in modo else {'encoding': 'utf-8'})) as fh:
        return fh.read()


def _node(args):
    return subprocess.run(['node'] + args, cwd=ROOT, capture_output=True, text=True)


class S_ShaDoManifesto(unittest.TestCase):
    """Item 6: o aviso «SHA256 do pote NAO CORRESPONDE ao manifesto»."""

    @classmethod
    def setUpClass(cls):
        cls.bruto = _ler(os.path.join(ROOT, 'docs/casco/r7/POTE-R7.json'), 'rb')
        cls.declarado = _j('docs/casco/r7/MANIFESTO-R7.json')['SHA256']['POTE-R7.json']

    def test_o_pote_no_git_nao_tem_cr(self):
        self.assertNotIn(b'\r', self.bruto)

    def test_a_causa_medida_e_o_fim_de_linha_crlf(self):
        c = PUB.conferir_sha_do_manifesto(self.bruto, self.declarado)
        self.assertEqual(c['MODO'], 'IGUAL_APOS_FIM_DE_LINHA_CRLF')
        self.assertNotEqual(c['SHA256_BYTES'], self.declarado)
        self.assertEqual(c['SHA256_BYTES_EM_CRLF'], self.declarado)

    def test_um_byte_mudado_da_diferente(self):
        i = self.bruto.index(b'"READY": 242')
        mexido = self.bruto[:i] + b'"READY": 243' + self.bruto[i + len(b'"READY": 242'):]
        self.assertEqual(PUB.conferir_sha_do_manifesto(mexido, self.declarado)['MODO'], 'DIFERENTE')

    def test_um_espaco_a_mais_da_diferente(self):
        self.assertEqual(PUB.conferir_sha_do_manifesto(self.bruto + b' ', self.declarado)['MODO'], 'DIFERENTE')

    def test_ficheiro_ja_em_crlf_confere_byte_a_byte_e_nao_pela_troca(self):
        crlf = self.bruto.replace(b'\n', b'\r\n')
        c = PUB.conferir_sha_do_manifesto(crlf, self.declarado)
        self.assertEqual(c['MODO'], 'IGUAL_BYTE_A_BYTE')
        self.assertIsNone(c['SHA256_BYTES_EM_CRLF'], 'com CR no ficheiro a troca nao se aplica')

    def test_crlf_misturado_nao_passa(self):
        """Um ficheiro com ALGUNS CR nao pode confere pela troca — a troca seria ambigua."""
        misto = self.bruto.replace(b'\n', b'\r\n', 1)
        self.assertEqual(PUB.conferir_sha_do_manifesto(misto, self.declarado)['MODO'], 'DIFERENTE')

    def test_sem_sha_declarado_nao_confere(self):
        self.assertEqual(PUB.conferir_sha_do_manifesto(self.bruto, None)['MODO'], 'DIFERENTE')
        self.assertEqual(PUB.conferir_sha_do_manifesto(self.bruto, '')['MODO'], 'DIFERENTE')

    def test_o_publicado_commitado_e_o_do_publicador(self):
        r = subprocess.run([sys.executable, 'pacote/publicar_pote_aprovado.py', '--conferir'], cwd=ROOT,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_gitattributes_tranca_os_bytes_do_casco(self):
        r = subprocess.run(['git', 'check-attr', 'text', 'docs/casco/r7/POTE-R7.json'], cwd=ROOT,
                           capture_output=True, text=True)
        self.assertIn('text: unset', r.stdout, 'docs/casco/** tem de ser -text: sem isso o Windows troca os bytes')


class L_PoteDaLabelIntelligence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.texto = _ler(LI.FONTE)
        cls.P = LI.ler_payload(cls.texto)
        cls.molde = _j('docs/casco/r7/POTE-R7.json')
        cls.pote = _j('docs/casco/ferramentas/POTE-FERRAMENTA-LABEL-INTELLIGENCE.json')
        cls.objs = cls.pote['COMPARTIMENTOS']['portfolio']['OBJETOS']

    def test_o_selo_da_ferramenta_bate(self):
        self.assertEqual(LI.selo(self.P), self.P['PRODUCED_BY']['CONTENT_SHA256'])
        self.assertEqual(self.pote['PRODUZIDO_POR']['CONTENT_SHA256_RECALCULADO'],
                         self.pote['PRODUZIDO_POR']['CONTENT_SHA256_DECLARADO'])

    def test_os_numeros_nao_mudaram(self):
        self.assertEqual(self.pote['CONTAGENS'], {'products': 166, 'objects': 210, 'versions': 54})
        self.assertEqual(len([o for o in self.objs if o['OBJETO_ID'].startswith('LI-PROD-')]), len(self.P['products']))
        self.assertEqual(len([o for o in self.objs if o['OBJETO_ID'].startswith('LI-OBJ-')]), len(self.P['objects']))
        self.assertEqual(len(self.pote['FERRAMENTA']['VERSOES']), 54)
        self.assertEqual(self.pote['FERRAMENTA']['AGREGADOS']['history']['distinct'], 54)
        self.assertEqual(self.pote['FERRAMENTA']['AGREGADOS']['by_proof'], self.P['by_proof'])

    def test_cada_registo_e_byte_a_byte_o_da_ferramenta_na_mesma_ordem(self):
        prods = [o['REGISTRO_DA_FERRAMENTA'] for o in self.objs if o['OBJETO_ID'].startswith('LI-PROD-')]
        regs = [o['REGISTRO_DA_FERRAMENTA'] for o in self.objs if o['OBJETO_ID'].startswith('LI-OBJ-')]
        self.assertEqual([LI.canonico(x) for x in prods], [LI.canonico(x) for x in self.P['products']])
        self.assertEqual([LI.canonico(x) for x in regs], [LI.canonico(x) for x in self.P['objects']])

    def test_o_payload_reconstruido_do_pote_da_o_mesmo_selo(self):
        de_volta = LI.reconstruir_payload(self.pote)
        self.assertEqual(LI.canonico(de_volta), LI.canonico(self.P))
        self.assertEqual(LI.selo(de_volta), self.P['PRODUCED_BY']['CONTENT_SHA256'])

    def test_datas_e_snapshot_preservados(self):
        S = self.pote['SNAPSHOT']
        for k in ('BUILT_AT', 'DATA_DATE', 'DATA_SNAPSHOT_ID', 'COLLECTED_AT', 'NEWEST_CHANGE_AT'):
            self.assertEqual(S[k], self.P[k], k)
        self.assertEqual(S['DATA_SNAPSHOT_ID'], 'PROD_FTS_6_20260831')

    def test_o_hash_do_ficheiro_de_origem_viaja(self):
        sha = hashlib.sha256(_ler(LI.FONTE, 'rb')).hexdigest()
        self.assertEqual(self.pote['ORIGEM']['FICHEIRO_SHA256'], sha)
        self.assertEqual(self.pote['SOURCE_HEAD']['FICHEIRO_SHA256'], sha)

    def test_produzido_pela_ferramenta_e_nao_pela_intelligence_r7(self):
        self.assertTrue(self.pote['INTELLIGENCE_RUN_ID'].startswith('FERRAMENTA:pilot-label-intelligence@'))
        self.assertEqual(self.pote['ENTRADA'], 'SAIDA_DE_INTELLIGENCE_TOOL')
        for o in self.objs:
            self.assertTrue(o['PRODUZIDO_POR'].startswith('pilot-label-intelligence'), o['OBJETO_ID'])
            self.assertEqual(o['ESPECIE_DITA_POR'], 'FERRAMENTA pilot-label-intelligence')
        bruto = json.dumps(self.pote, ensure_ascii=False)
        self.assertNotIn('IR-e09acab6365032523d6e', bruto, 'a corrida R7 nao pode aparecer como autora')
        self.assertNotIn('Intelligence R7', bruto)

    def test_toda_prova_tem_url_e_documento(self):
        for o in self.objs:
            self.assertTrue(o['PROVA'], o['OBJETO_ID'])
            for q in o['PROVA']:
                self.assertTrue(q['DOCUMENT_ID'] and q['DOCUMENT_ID'] != 'NAO SEI', o['OBJETO_ID'])
                self.assertEqual(q['INTELLIGENCE_RUN_ID'], self.pote['INTELLIGENCE_RUN_ID'])

    def test_o_commitado_e_o_que_o_adaptador_produz_e_e_deterministico(self):
        self.assertEqual(LI.texto(), LI.texto())
        r = subprocess.run([sys.executable, 'pacote/pote_ferramenta_label.py', '--conferir'], cwd=ROOT,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_um_payload_editado_e_recusado(self):
        mexido = copy.deepcopy(self.P)
        mexido['products'][0]['expiry'] = '2099-12-31'
        texto = 'window.ITALY_LABEL_INTELLIGENCE = ' + json.dumps(mexido, ensure_ascii=False) + ';'
        with self.assertRaises(LI.Recusado):
            LI.construir(texto, self.molde)

    def test_uma_contagem_editada_e_recusada(self):
        mexido = copy.deepcopy(self.P)
        mexido['by_proof']['PROVED'] += 1
        texto = 'window.ITALY_LABEL_INTELLIGENCE = ' + json.dumps(mexido, ensure_ascii=False) + ';'
        with self.assertRaises(LI.Recusado):
            LI.construir(texto, self.molde)

    def test_o_leitor_do_casco_aceita_o_pote_da_ferramenta(self):
        js = ("const fs=require('fs'),vm=require('vm');const c={window:{location:{search:''}},document:{write(){}}};"
              "vm.createContext(c);vm.runInContext(fs.readFileSync('italia-portale/client/sintonia-pote-casco.js','utf8'),c);"
              "const P=JSON.parse(fs.readFileSync('docs/casco/ferramentas/POTE-FERRAMENTA-LABEL-INTELLIGENCE.json','utf8'));"
              "const C=c.window.SINTONIA_POTE_CASCO;const v=C.vm(P,'etichette','it');"
              "console.log(JSON.stringify({f:C.conferir(P),n:v.objetos.length,k:v.comp.codigo}))")
        r = subprocess.run(['node', '-e', js], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, 'node e preciso para este teste: ' + r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out, {'f': [], 'n': 376, 'k': 'portfolio'})


class I_Inventario(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.inv = _j('docs/acervo/INVENTARIO-ACERVO.json')
        cls.ent = _j('docs/intelligence/acervo/ENTRADA-INTELLIGENCE-ACERVO.json')
        cls.ins = _j('docs/intelligence/acervo/INSUMOS-DECLARADOS-ACERVO.json')
        cls.por_id = {c['ID']: c for c in cls.inv['CONJUNTOS']}

    def test_os_commitados_sao_os_do_gerador(self):
        r = _node(['pacote/acervo_inventario.mjs', '--conferir'])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_toda_classe_e_uma_das_cinco_e_tem_motivo(self):
        for c in self.inv['CONJUNTOS']:
            self.assertIn(c['CLASSE'], ('a', 'b', 'c', 'd', 'NAO_SEI'), c['ID'])
            self.assertTrue(c['MOTIVO'].strip(), c['ID'])
        self.assertNotIn('UNKNOWN', json.dumps([c['CLASSE'] for c in self.inv['CONJUNTOS']]))

    def test_a_label_intelligence_e_saida_de_ferramenta_e_so_ela(self):
        a = [c['ID'] for c in self.inv['CONJUNTOS'] if c['CLASSE'] == 'a']
        self.assertTrue(a and all(x.startswith('italy-label-intelligence.js::') for x in a), a)
        self.assertEqual(self.inv['CONTAGEM_POR_CLASSE']['SEM_COPIAS']['a']['REGISTOS'], 166 + 210 + 54 + 76 + 49)

    def test_demo_oportunidade_e_client_safe_false_ficam_fora(self):
        for c in self.inv['CONJUNTOS']:
            if c['FICHEIRO'] == 'italy-demo-data.js':
                self.assertEqual(c['CLASSE'], 'd', c['ID'])
        for i in ('italy-handoff-v21.js::opportunities', 'italy-handoff-v21.js::clientSafeCrossings',
                  'italy-handoff-v21.js::relationships', 'meeting-intelligence-snapshot.js::CASES',
                  'italy-ingested.js::OPPORTUNITIES'):
            self.assertEqual(self.por_id[i]['CLASSE'], 'd', i)
        for c in self.inv['CONJUNTOS']:
            cs = c.get('CLIENT_SAFE') or {}
            if cs and set(cs) == {'false'}:
                self.assertIn(c['CLASSE'], ('d',), '%s: todo CLIENT_SAFE=false e nao esta FORA' % c['ID'])

    def test_as_copias_sao_medidas_e_nao_supostas(self):
        for c in self.inv['CONJUNTOS']:
            d = c.get('DUPLICADO_DE')
            if d and d['TODOS']:
                self.assertEqual(d['MESMO_ID_LA'], d['DE_N'], c['ID'])
                self.assertIn(d['DE'], self.por_id, c['ID'])

    def test_a_entrada_so_tem_coletados_do_conjunto_canonico(self):
        self.assertTrue(self.ent['NAO_VAI_AO_CASCO'])
        esperados = sum(c['N'] for c in self.inv['CONJUNTOS']
                        if c['CLASSE'] == 'c' and not (c.get('DUPLICADO_DE') or {}).get('TODOS'))
        self.assertEqual(self.ent['ITENS'], esperados)
        self.assertEqual(len(self.ent['LISTA']), esperados)
        ids = [x['ACERVO_ID'] for x in self.ent['LISTA']]
        self.assertEqual(len(ids), len(set(ids)), 'item repetido na ENTRADA')
        self.assertTrue(all(x.startswith('italy-handoff-v21.js::') for x in ids))
        self.assertFalse(any('::futureEvents::' in x for x in ids), 'futureEvents e recorte de events')

    def test_a_data_real_diz_de_que_campo_veio(self):
        sha = self.ent['ORIGEM']['SHA256']
        for x in self.ent['LISTA']:
            d = x['DATA_REAL']
            self.assertTrue(d['CAMPO'], x['ACERVO_ID'])
            if d['CAMPO'] == 'NAO SEI':
                self.assertEqual(d['VALOR'], 'NAO SEI', x['ACERVO_ID'])
            self.assertNotIn(str(d['VALOR']), ('NOT_ESTABLISHED', 'NOT_KNOWN'), 'data que diz nao sei nao e data')
            self.assertEqual(x['ORIGEM_SHA256'], sha)

    def test_nada_da_entrada_esta_no_casco(self):
        pub = _ler(os.path.join(ROOT, 'italia-portale/client/sintonia-pote-publicado.js'))
        self.assertNotIn('ENTRADA_INTELLIGENCE_ACERVO', pub)
        self.assertNotIn('italy-handoff-v21.js::', pub)

    def test_todo_leitor_declarado_foi_encontrado_numa_linha(self):
        for x in self.ins['INSUMOS'] + self.ins['INSUMOS_FORA_DO_PORTAL']:
            for l in x['LEITORES_EXISTENTES']:
                self.assertNotIn('NAO ENCONTRADO', l, x['ID'])

    def test_o_portfolio_cultura_alvo_e_o_registro_completo_estao_declarados(self):
        ids = {x['ID'] for x in self.ins['INSUMOS']} | {x['ID'] for x in self.ins['INSUMOS_FORA_DO_PORTAL']}
        self.assertIn('italy-handoff-v21.js::productRelationships', ids)
        self.assertIn('registro-completo-ministero', ids)
        reg = [x for x in self.ins['INSUMOS_FORA_DO_PORTAL'] if x['ID'] == 'registro-completo-ministero'][0]
        self.assertIn('NAO SEI', reg['LIMITE'], 'concorrentes pelo mesmo ALVO nao se respondem com o registro')


class D_AuditoriaD97(unittest.TestCase):

    def test_a_auditoria_commitada_e_a_de_hoje(self):
        r = _node(['italia-portale/audit/casco/d97-auditoria.mjs', '--json'])
        self.assertIn(r.returncode, (0, 1), r.stderr)
        self.assertEqual(json.loads(r.stdout), _j('docs/acervo/AUDITORIA-D97-R7.json'))

    def test_a_auditoria_apanha_objeto_sem_documento_ou_sem_intelligence(self):
        """O pote real nao tem objeto fora da lei — por isso a regua prova-se com um pote plantado."""
        js = ("import fs from 'node:fs';import {objetos} from './italia-portale/audit/casco/d97-auditoria.mjs';"
              "const t=fs.readFileSync('docs/casco/r7/POTE-R7.json','utf8');const p=JSON.parse(t);"
              "const o=p.COMPARTIMENTOS.market.OBJETOS;o[0].PROVA[0].DOCUMENT_ID='NAO SEI';"
              "o[1].ESPECIE_DITA_POR='CASCO';o[2].PROVA[0].URL='ftp://x';o[3].PROVA[0].INTELLIGENCE_RUN_ID='IR-outra';"
              "const r=objetos(p,t);console.log(JSON.stringify(r.FORA_DA_INTELLIGENCE_OU_SEM_PROVA.map(x=>x.PORQUE)))")
        r = subprocess.run(['node', '--input-type=module', '-e', js], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), [['PROVA.DOCUMENT_ID vazio'], ['ESPECIE_DITA_POR=CASCO'],
                                                ['PROVA.URL nao navegavel'], ['PROVA de outra corrida']])

    def test_os_numeros_da_auditoria(self):
        A = _j('docs/acervo/AUDITORIA-D97-R7.json')
        self.assertEqual(A['OBJETOS']['TOTAL'], 47)
        self.assertEqual(A['OBJETOS']['FORA_DA_INTELLIGENCE_OU_SEM_PROVA'], [])
        self.assertEqual(A['CRUZAMENTOS']['POR_DESTINO'],
                         {'OBJETO_DO_POTE': 2, 'RECUSADO_PELO_POTE': 80, 'AUSENTE_DO_POTE': 4})
        self.assertEqual(len(A['CRUZAMENTOS']['SEM_A_PROVA_QUE_O_POTE_EXIGE']), 84)
        self.assertIn('search', [r['ROTA'] for r in A['ROTAS']['ROTAS_DE_LEGADO_COM_O_POTE']])


if __name__ == '__main__':
    unittest.main()
