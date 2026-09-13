# -*- coding: utf-8 -*-
"""C10.8B-R — o bruto pago não morre no checkout.

    RAW CAPTURADO NO PROCESSO
      != RAW QUE SOBREVIVE AO JOB
      != RAW DEVOLVIDO PARA INVESTIGAÇÃO
      != PRESERVAÇÃO FORWARD CANÔNICA.

Quatro estados. Esta bateria guarda o TERCEIRO — e guarda, com o mesmo peso,
que ele NÃO se promova ao quarto.

    WORKFLOW ARTIFACT != CANONICAL FORWARD STORAGE.
    GUARDAR SEM NUNCA TER IDO BUSCAR NÃO É GUARDAR. É ESPERAR.
"""
import ast
import gzip
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', 'tests', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import social_envelope as env                                     # noqa: E402
import social_matriz as mz                                        # noqa: E402
import social_scrap as ss                                         # noqa: E402

WORKFLOW = '.github/workflows/scrap-evidencia.yml'
RUN = 'C108BR-TESTE-1'
OUTRA = 'C108BR-TESTE-2'


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _sem_comentarios(texto):
    """O YAML SEM a prosa.

    A primeira versão de RT30 procurou `if-no-files-found: warn` no ficheiro
    inteiro e acusou o comentário que explica por que este workflow NÃO usa
    `warn`. RT31 acusou a palavra APIFY na frase que diz que o workflow não
    toca no Apify.

        UMA SONDA QUE LÊ A PROSA ENCONTRA A FRASE QUE EXPLICA A REGRA
        E CHAMA-LHE VIOLAÇÃO DA REGRA.
    """
    fora = []
    for linha in texto.splitlines():
        sem = re.sub(r'(?<!\$)#.*$', '', linha)
        if sem.strip():
            fora.append(sem)
    return '\n'.join(fora)


def _ler_json(caminho):
    with io.open(caminho, encoding='utf-8') as f:
        return json.load(f)


def _funcao(modulo_rel, nome):
    """→ o nó AST da função. Ler a ÁRVORE, e não a prosa que eu escrevi."""
    arvore = ast.parse(_fonte(modulo_rel))
    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name == nome:
            return no
    raise AssertionError('%s não tem %s' % (modulo_rel, nome))


class _ComGaveta(unittest.TestCase):
    """Cada caso nasce com gaveta própria. Nada escapa para a árvore."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='c108br-')
        self.gaveta = os.path.join(self.tmp, 'gaveta')
        self.origem = os.path.join(self.tmp, 'origem')
        os.makedirs(self.origem)
        self._produzidos = env.produzidos()
        env.esquecer_produzidos()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        env.esquecer_produzidos()
        for c in self._produzidos:
            env.registar_produzido(c)

    def _ficheiro(self, nome, dados):
        caminho = os.path.join(self.origem, nome)
        with open(caminho, 'wb') as f:
            f.write(dados)
        return caminho

    def _publicar(self, run=RUN, ficheiros=None, **kw):
        return ss.evidencia_publicar(run, gaveta=self.gaveta,
                                     ficheiros=ficheiros, **kw)


# ══════════════════════════════════════════════════════════════════════════
# RT1–RT6 · A IDENTIDADE DA CORRIDA É A CHAVE, E NÃO «O ÚLTIMO»
# ══════════════════════════════════════════════════════════════════════════
class AIdentidadeDaCorridaEAChave(_ComGaveta):

    def test_rt01_pacote_recuperado_pela_corrida_certa(self):
        self._ficheiro('a.json', b'{"i":1}')
        self._publicar(ficheiros=[os.path.join(self.origem, 'a.json')])
        e = ss.evidencia_recuperar(RUN, de=self.gaveta)
        self.assertEqual(e['RECOVERED'], 'YES')
        self.assertEqual(e['SHA_MATCH'], 'YES')

    def test_rt02_run_id_errado_recusa_e_nao_devolve_o_outro(self):
        """Pedir a corrida B e receber a corrida A é ler os bytes errados.

            UM PACOTE DE OUTRA CORRIDA COM A MESMA CARA NÃO É ESTE PACOTE.
        """
        self._ficheiro('a.json', b'{"i":1}')
        self._publicar(ficheiros=[os.path.join(self.origem, 'a.json')])
        e = ss.evidencia_recuperar(OUTRA, de=self.gaveta)
        self.assertEqual(e['RECOVERED'], 'NO')
        self.assertEqual(e['FILES'], [])
        self.assertIn(OUTRA, e['WHY'])

    def test_rt03_sem_recurso_ao_ultimo_artefato(self):
        """A recuperação NÃO pode ter uma volta que escolhe «o mais recente».

        Uma sonda de prosa leria o meu comentário. Esta lê a ÁRVORE: nenhuma
        chamada a listdir/glob/scandir dentro de `evidencia_recuperar`.
        """
        no = _funcao('coleta/social_scrap.py', 'evidencia_recuperar')
        achadas = set()
        for n in ast.walk(no):
            if isinstance(n, ast.Call):
                alvo = n.func
                nome = (alvo.attr if isinstance(alvo, ast.Attribute)
                        else getattr(alvo, 'id', None))
                if nome in ('listdir', 'glob', 'iglob', 'scandir', 'walk',
                            'getmtime', 'sorted', 'max'):
                    achadas.add(nome)
        self.assertEqual(achadas, set(),
                         'a recuperação varre a gaveta: %s' % sorted(achadas))

    def test_rt04_manifesto_com_outro_run_id_e_recusado(self):
        self._ficheiro('a.json', b'{"i":1}')
        self._publicar(ficheiros=[os.path.join(self.origem, 'a.json')])
        man = os.path.join(self.gaveta, RUN, 'MANIFESTO.json')
        d = _ler_json(man)
        d['RUN_ID'] = OUTRA
        with io.open(man, 'w', encoding='utf-8') as f:
            f.write(json.dumps(d))
        e = ss.evidencia_recuperar(RUN, de=self.gaveta)
        self.assertEqual(e['RECOVERED'], 'NO')
        self.assertEqual(e['SHA_MATCH'], 'NO')

    def test_rt05_pacote_sem_manifesto_nao_e_pacote(self):
        self._ficheiro('a.json', b'{"i":1}')
        self._publicar(ficheiros=[os.path.join(self.origem, 'a.json')])
        os.remove(os.path.join(self.gaveta, RUN, 'MANIFESTO.json'))
        e = ss.evidencia_recuperar(RUN, de=self.gaveta)
        self.assertEqual(e['RECOVERED'], 'NO')
        self.assertIn('MANIFESTO', e['WHY'])

    def test_rt06_gaveta_inexistente_recusa_sem_levantar(self):
        e = ss.evidencia_recuperar(RUN, de=os.path.join(self.tmp, 'nao-existe'))
        self.assertEqual(e['RECOVERED'], 'NO')
        self.assertEqual(e['SHA_MATCH'], 'NOT_APPLICABLE')


# ══════════════════════════════════════════════════════════════════════════
# RT7–RT10 · O SHA DO MANIFESTO É UMA AFIRMAÇÃO; O RECALCULADO É A MEDIDA
# ══════════════════════════════════════════════════════════════════════════
class OShaERecalculado(_ComGaveta):

    def test_rt07_bytes_trocados_depois_do_manifesto_sao_apanhados(self):
        """Aceitar o SHA do manifesto seria confiar na etiqueta do pacote.

            UM SHA QUE SÓ VEM DO MANIFESTO NÃO PROVA OS BYTES.
        """
        self._ficheiro('a.json', b'{"i":1}')
        self._publicar(ficheiros=[os.path.join(self.origem, 'a.json')])
        with open(os.path.join(self.gaveta, RUN, 'a.json'), 'wb') as f:
            f.write(b'{"i":999}')
        e = ss.evidencia_recuperar(RUN, de=self.gaveta)
        self.assertEqual(e['SHA_MATCH'], 'NO')
        self.assertEqual(e['FILES'][0]['RECOVERED'], 'YES')

    def test_rt08_tamanho_igual_e_conteudo_outro_e_apanhado(self):
        """Mesmos bytes de tamanho, conteúdo diferente: só o SHA vê isto."""
        self._ficheiro('a.json', b'{"i":111}')
        self._publicar(ficheiros=[os.path.join(self.origem, 'a.json')])
        with open(os.path.join(self.gaveta, RUN, 'a.json'), 'wb') as f:
            f.write(b'{"i":222}')
        e = ss.evidencia_recuperar(RUN, de=self.gaveta)
        self.assertEqual(e['SHA_MATCH'], 'NO')

    def test_rt09_ficheiro_declarado_e_ausente_nao_desaparece_do_relato(self):
        self._ficheiro('a.json', b'{"i":1}')
        self._publicar(ficheiros=[os.path.join(self.origem, 'a.json')])
        os.remove(os.path.join(self.gaveta, RUN, 'a.json'))
        e = ss.evidencia_recuperar(RUN, de=self.gaveta)
        self.assertEqual(e['SHA_MATCH'], 'NO')
        self.assertEqual(e['FILES'][0]['RECOVERED'], 'NO')

    def test_rt10_o_manifesto_declara_bytes_sha_e_tipo_de_cada_ficheiro(self):
        self._ficheiro('a.json.gz', gzip.compress(b'[{"x":1}]'))
        e = self._publicar(ficheiros=[os.path.join(self.origem, 'a.json.gz')])
        (f,) = e['EVIDENCE_FILES']
        self.assertEqual(f['CONTENT_TYPE'], 'application/json+gzip')
        self.assertEqual(f['RAW_BYTES'], os.path.getsize(
            os.path.join(self.origem, 'a.json.gz')))
        self.assertEqual(len(f['SHA256']), 64)


# ══════════════════════════════════════════════════════════════════════════
# RT11–RT16 · SEGREDO NÃO VIAJA, E A RECUSA NÃO APAGA EVIDÊNCIA
# ══════════════════════════════════════════════════════════════════════════
class SegredoNaoViaja(_ComGaveta):

    def test_rt11_token_no_bruto_levanta_e_nada_e_escrito(self):
        c = self._ficheiro('a.json', b'{"t":"apify_api_ABCDEF"}')
        with self.assertRaises(ss.EvidenciaComSegredo):
            self._publicar(ficheiros=[c])
        self.assertFalse(os.path.exists(os.path.join(self.gaveta, RUN)),
                         'a recusa deixou pacote meio escrito')

    def test_rt12_cada_termo_proibido_e_apanhado(self):
        for termo in ss.PROIBIDO_NA_EVIDENCIA:
            c = self._ficheiro('a.json', b'{"x":"' + termo.encode() + b'zz"}')
            with self.assertRaises(ss.EvidenciaComSegredo, msg=termo):
                self._publicar(ficheiros=[c])

    def test_rt13_segredo_dentro_do_gzip_tambem_e_apanhado(self):
        """O bruto pago nasce COMPRIMIDO.

            UMA SONDA QUE NÃO DESCOMPRIME DÁ VERDE AO QUE NÃO CONSEGUE LER.
        """
        c = self._ficheiro('a.json.gz',
                           gzip.compress(b'{"t":"apify_api_ABCDEF"}'))
        with self.assertRaises(ss.EvidenciaComSegredo):
            self._publicar(ficheiros=[c])

    def test_rt14_gzip_ilegivel_nao_passa_por_limpo(self):
        self.assertEqual(ss._cheira_a_segredo(b'\x1f\x8bLIXO'), 'GZIP_ILEGIVEL')

    def test_rt15_a_recusa_nao_redige_em_silencio(self):
        """Apagar o segredo para o pacote passar destrói a evidência.

            MELHOR FALHAR ALTO DO QUE REDIGIR EM SILÊNCIO.

        A árvore de `evidencia_publicar` não pode ter substituição de texto.
        """
        no = _funcao('coleta/social_scrap.py', 'evidencia_publicar')
        proibidas = set()
        for n in ast.walk(no):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                if n.func.attr in ('replace', 'sub', 'translate', 'strip'):
                    proibidas.add(n.func.attr)
        self.assertEqual(proibidas - {'replace'}, set())
        # o único `replace` permitido é o das barras do caminho
        self.assertNotIn('.replace(termo', _fonte('coleta/social_scrap.py'))

    def test_rt16_gzip_limpo_passa(self):
        c = self._ficheiro('a.json.gz', gzip.compress(b'[{"x":1}]'))
        e = self._publicar(ficheiros=[c])
        self.assertEqual(e['EVIDENCE_TRANSFERRED'], 'STAGED')


# ══════════════════════════════════════════════════════════════════════════
# RT17–RT21 · O PACOTE DIZ O QUE NÃO É
# ══════════════════════════════════════════════════════════════════════════
class OPacoteDizOQueNaoE(_ComGaveta):

    def test_rt17_forward_canonico_e_nao_em_todo_lado(self):
        """Esperado nesta missão, MESMO com o artefato a funcionar."""
        c = self._ficheiro('a.json', b'{"i":1}')
        e = self._publicar(ficheiros=[c])
        self.assertEqual(e['CANONICAL_FORWARD_PRESERVATION'], 'NO')
        man = _ler_json(os.path.join(self.gaveta, RUN, 'MANIFESTO.json'))
        self.assertEqual(man['CANONICAL_FORWARD_PRESERVATION'], 'NO')
        r = ss.evidencia_recuperar(RUN, de=self.gaveta)
        self.assertEqual(r['CANONICAL_FORWARD_PRESERVATION'], 'NO')

    def test_rt18_a_retencao_e_finita_e_declarada(self):
        c = self._ficheiro('a.json', b'{"i":1}')
        e = self._publicar(ficheiros=[c])
        self.assertEqual(e['EVIDENCE_RETENTION'], 'TEMPORARY')
        self.assertEqual(e['EVIDENCE_RETENTION_DAYS'], 30)
        man = _ler_json(os.path.join(self.gaveta, RUN, 'MANIFESTO.json'))
        self.assertEqual(man['EVIDENCE_RETENTION'], 'TEMPORARY')

    def test_rt19_run_id_nao_vira_raw_observation_id(self):
        """RUN_ID != RAW_OBSERVATION_ID. E nem SOURCE_ID nem DOCUMENT_ID
        são fabricados aqui."""
        c = self._ficheiro('a.json', b'{"i":1}')
        self._publicar(ficheiros=[c])
        man = _ler_json(os.path.join(self.gaveta, RUN, 'MANIFESTO.json'))
        for inventado in ('RAW_OBSERVATION_ID', 'SOURCE_ID', 'DOCUMENT_ID'):
            self.assertNotIn(inventado, man)
        self.assertIn('RAW_OBSERVATION_ID', man['NOTA'])

    def test_rt20_o_pacote_nomeia_a_classe_diagnostica(self):
        c = self._ficheiro('a.json', b'{"i":1}')
        self._publicar(ficheiros=[c])
        man = _ler_json(os.path.join(self.gaveta, RUN, 'MANIFESTO.json'))
        self.assertEqual(man['EVIDENCE_CLASS'], 'DIAGNOSTIC_JOB_TO_JOB')

    def test_rt21_nada_produzido_nao_e_pacote_verde_e_vazio(self):
        """Um STAGED com zero ficheiros seria um upload que não subiu nada."""
        e = self._publicar(ficheiros=[])
        self.assertEqual(e['EVIDENCE_TRANSFERRED'], 'NO_RAW_PRODUCED')
        self.assertIsNone(e['EVIDENCE_REFERENCE'])
        self.assertFalse(os.path.exists(os.path.join(self.gaveta, RUN)))


# ══════════════════════════════════════════════════════════════════════════
# RT22–RT26 · O INVENTÁRIO VÊ O BRUTO PAGO
# ══════════════════════════════════════════════════════════════════════════
class OInventarioVeOBrutoPago(unittest.TestCase):

    def setUp(self):
        self._antes = env.produzidos()
        env.esquecer_produzidos()

    def tearDown(self):
        env.esquecer_produzidos()
        for c in self._antes:
            env.registar_produzido(c)

    def test_rt22_a_porta_paga_regista_o_bruto_no_inventario(self):
        """O que o inventário não vê não atravessa a fronteira do job.

        Medido na ÁRVORE de `coletor.executar`, não na prosa.
        """
        no = _funcao('coleta/coletor.py', 'executar')
        chamadas = [n for n in ast.walk(no)
                    if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr == 'registar_produzido']
        self.assertEqual(len(chamadas), 1,
                         'a porta paga não regista o bruto no inventário')

    def test_rt23_registar_nao_copia_nao_comprime_nao_normaliza(self):
        no = _funcao('coleta/social_envelope.py', 'registar_produzido')
        for n in ast.walk(no):
            if isinstance(n, ast.Call):
                nome = (n.func.attr if isinstance(n.func, ast.Attribute)
                        else getattr(n.func, 'id', None))
                self.assertIn(nome, ('append',),
                              'registar_produzido faz %s' % nome)

    def test_rt24_registar_e_idempotente(self):
        env.registar_produzido('/x/a.gz')
        env.registar_produzido('/x/a.gz')
        self.assertEqual(env.produzidos().count('/x/a.gz'), 1)

    def test_rt25_registar_ignora_caminho_vazio(self):
        env.registar_produzido('')
        env.registar_produzido(None)
        self.assertEqual(env.produzidos(), [])

    def test_rt26_publicar_sem_lista_le_o_inventario(self):
        tmp = tempfile.mkdtemp(prefix='c108br-inv-')
        self.addCleanup(shutil.rmtree, tmp, True)
        c = os.path.join(tmp, 'a.json')
        with open(c, 'wb') as f:
            f.write(b'{"i":1}')
        env.registar_produzido(c)
        e = ss.evidencia_publicar(RUN, gaveta=os.path.join(tmp, 'g'))
        self.assertEqual(e['EVIDENCE_TRANSFERRED'], 'STAGED')
        self.assertEqual([f['RAW_FILENAME'] for f in e['EVIDENCE_FILES']],
                         ['a.json'])


# ══════════════════════════════════════════════════════════════════════════
# RT27–RT32 · O GIT NÃO VIRA STORAGE, E O WORKFLOW NÃO VIRA MOTOR
# ══════════════════════════════════════════════════════════════════════════
class OGitNaoViraStorage(unittest.TestCase):

    def test_rt27_o_gitignore_continua_a_ignorar_o_bruto(self):
        """Commitar `.gz` e datasets pagos faria do Git um object store."""
        ig = _fonte('.gitignore')
        self.assertIn('data/samples/**/*.gz', ig)
        self.assertIn('data/samples/**/*.raw.json', ig)

    def test_rt28_a_gaveta_da_evidencia_nao_vive_no_acervo(self):
        self.assertTrue(ss.GAVETA_EVIDENCIA.startswith('.tmp'),
                        'o pacote cairia dentro de data/samples/')

    def test_rt29_o_workflow_recupera_pelo_nome_da_corrida(self):
        y = _sem_comentarios(_fonte(WORKFLOW))
        self.assertIn('actions/download-artifact@v4', y)
        self.assertIn('name: scrap-evidencia-${{ needs.produzir.outputs.run_id }}', y)

    def test_rt30_upload_que_nao_sobe_nada_e_falha(self):
        """UPLOAD STEP SUCCESS != ARTIFACT EXISTS."""
        y = _sem_comentarios(_fonte(WORKFLOW))
        self.assertIn('if-no-files-found: error', y)
        self.assertNotIn('if-no-files-found: warn', y)
        self.assertIn('artifact-id', y)

    def test_rt31_o_workflow_da_evidencia_nao_toca_segredo_nem_provider(self):
        y = _sem_comentarios(_fonte(WORKFLOW))
        for proibido in ('secrets.', 'APIFY', 'apify', 'SUPABASE'):
            self.assertNotIn(proibido, y, 'o workflow toca %s' % proibido)

    def test_rt32_os_dois_jobs_correm_em_maquinas_separadas(self):
        """Um upload e um download no mesmo job não provam fronteira nenhuma."""
        import yaml
        d = yaml.safe_load(_fonte(WORKFLOW))
        jobs = d['jobs']
        self.assertEqual(sorted(jobs), ['produzir', 'recuperar'])
        self.assertEqual(jobs['recuperar']['needs'], 'produzir')
        self.assertEqual(jobs['produzir']['runs-on'], 'ubuntu-latest')
        self.assertEqual(jobs['recuperar']['runs-on'], 'ubuntu-latest')


# ══════════════════════════════════════════════════════════════════════════
# RT33–RT36 · A PROVA DA FRONTEIRA MEDE A FRONTEIRA
# ══════════════════════════════════════════════════════════════════════════
class AProvaMedeAFronteira(unittest.TestCase):

    def test_rt33_o_job_b_recusa_quando_ja_tem_o_ficheiro(self):
        """UM JOB QUE JÁ TEM O FICHEIRO NÃO PROVA QUE O FOI BUSCAR."""
        fonte = _fonte('coleta/social_scrap.py')
        self.assertIn('PROVA_INVALIDA', fonte)
        self.assertIn('WORKSPACE_RAW_BEFORE', fonte)

    def test_rt34_a_fixture_e_real_e_versionada(self):
        """Bytes fabricados para o teste passar provariam o fabrico."""
        alvo = os.path.join(RAIZ, ss.FIXTURE_DA_FRONTEIRA)
        self.assertTrue(os.path.isfile(alvo), ss.FIXTURE_DA_FRONTEIRA)
        import subprocess
        listado = subprocess.run(
            ['git', 'ls-files', '--error-unmatch', ss.FIXTURE_DA_FRONTEIRA],
            cwd=RAIZ, capture_output=True)
        self.assertEqual(listado.returncode, 0, 'a fixture não está versionada')

    def test_rt35_a_recuperacao_nao_abre_rede(self):
        """Zero provider. Medido na árvore das duas funções da evidência."""
        for nome in ('evidencia_publicar', 'evidencia_recuperar'):
            no = _funcao('coleta/social_scrap.py', nome)
            for n in ast.walk(no):
                if isinstance(n, ast.Call):
                    alvo = (n.func.attr if isinstance(n.func, ast.Attribute)
                            else getattr(n.func, 'id', None))
                    self.assertNotIn(alvo, ('urlopen', 'buscar', 'executar',
                                            'run', 'Popen', 'request'),
                                     '%s abre rede: %s' % (nome, alvo))

    def test_rt36_o_bruto_da_prova_nasce_onde_o_checkout_apaga(self):
        """Se nascesse versionado, o job B tê-lo-ia e a fronteira sumia.

        A primeira versão desta sentinela lia `env.RAW_DIR` VIVO — e ficou
        vermelha na suíte inteira porque `test_c3_youtube_cutover` redireciona
        essa gaveta de propósito, para o bruto de teste não cair no acervo.

            UMA SONDA QUE LÊ ESTADO GLOBAL MEDE QUEM CORREU ANTES DELA.

        Por isso mede-se a DECLARAÇÃO: onde a gaveta nasce no ficheiro que a
        declara, e que a prova escreve lá dentro.
        """
        no = _funcao('coleta/social_scrap.py', 'evidencia_publicar_prova')
        self.assertIn('env.RAW_DIR', ast.unparse(no))
        declarado = _fonte('coleta/social_envelope.py')
        self.assertIn("SAIDA = os.path.join(ROOT, 'data', 'samples', 'SOCIAL-IT')",
                      declarado)
        self.assertIn("RAW_DIR = os.path.join(SAIDA, 'raw-free')", declarado)
        # E o `.gitignore` apaga o que nasce lá: é isso que cria a fronteira.
        self.assertIn('data/samples/**/*.gz', _fonte('.gitignore'))


# ══════════════════════════════════════════════════════════════════════════
# RT37–RT40 · O QUE ESTA MISSÃO NÃO PODE TER MEXIDO
# ══════════════════════════════════════════════════════════════════════════
class OQueEstaMissaoNaoMexeu(unittest.TestCase):

    def test_rt37_a_rota_paga_continua_partial(self):
        """Nem promover a PROVED, nem rebaixar. Nada correu no provider."""
        achadas = [r for cap in mz.MATRIZ['YOUTUBE'].values()
                   if isinstance(cap, list)
                   for r in cap if r['ROTA'] == 'apify:transcricao']
        self.assertEqual(len(achadas), 1, 'a rota paga não está na matriz')
        self.assertEqual(achadas[0]['ESTADO'], 'PARTIAL')
        self.assertIn('PARTIAL', mz.ESTADOS)

    def test_rt38_nenhum_modulo_v2_ou_final_concorrente_nasceu(self):
        proibidos = ('scrap_budget_v2.py', 'money_manager_final.py',
                     'paid_executor_v2.py', 'youtube_apify_live.py',
                     'evidencia_v2.py', 'forward_final.py',
                     'raw_storage_v2.py', 'c10_8b_runner.py')
        for nome in proibidos:
            for pasta in ('coleta', 'leis', 'ferramentas', 'medidas'):
                self.assertFalse(
                    os.path.exists(os.path.join(RAIZ, pasta, nome)),
                    '%s/%s nasceu' % (pasta, nome))

    def test_rt39_a_evidencia_vive_no_dono_do_bruto(self):
        """ONE CONCEPT → ONE OWNER: quem já inventaria RAW é quem o embala."""
        fonte = _fonte('coleta/social_scrap.py')
        self.assertIn('def evidencia_publicar', fonte)
        self.assertIn('def _raw_do_piloto', fonte)

    def test_rt40_o_workflow_nao_sabe_actor_id_nem_teto(self):
        """WORKFLOW É DISPARADOR. WORKFLOW NÃO É MOTOR DE COLETA."""
        y = _sem_comentarios(_fonte(WORKFLOW))
        self.assertNotIn('~youtube-transcript-scraper', y)
        self.assertNotIn('TETO', y)
        self.assertNotIn('0.10', y)


if __name__ == '__main__':
    unittest.main(verbosity=2)
