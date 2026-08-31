# -*- coding: utf-8 -*-
"""Preview do CASCO V8 FINAL na Vercel.

O CLOSEOUT provou que o casco esta pronto por dentro. Estas provas medem outra
coisa: se ele ABRE. A testemunha commitada era incompleta — o index.html do
export pede 20 arquivos (_ds/ e assets/) que nao estavam no repositorio, e nada
denunciava isso porque nenhum teste seguia as referencias do HTML.

Nao reimplementam o build. Medem o que ele promete:

  1  a testemunha nao foi tocada (os quatro SHAs do CLOSEOUT continuam de pe)
  2  toda referencia do index.html tem arquivo correspondente
  3  todo arquivo em disco tem SHA registrado no manifesto, e bate
  4  nenhum segredo, nenhum caminho de Windows
  5  o casco continua tendo UMA copia — nao existe deploy/ paralelo
  6  o build confere SHA e falha quando divergir

Zero rede.
"""
import gzip
import hashlib
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPLOY = os.path.join(ROOT, 'casco', 'canonical', 'deploy-v8-closeout')

# SHAs publicados em docs/implementation/V8-RECEPTOR-CLOSEOUT.md, secoes 1 e 9.
TESTEMUNHA = {
    'index.html': ('d28f6b5876e2fa28720eb555a8b99a275e56c229ed0ac5c4b07edf89f4e81328', 372425),
    'support.js': ('8fe7df74405f3c55f49b7249c74ea1397e65d07dea2b1bd3b4a489bec2e28cbe', 69150),
    'crop-map.js': ('a55c6011e6aadb014b2617c8f5b302d9d2fb4bbfb1ee3e444cad345bbb1614c8', 10156),
}

# Termos que nao podem existir em nada servido ao navegador.
SEGREDOS = re.compile(
    r'service_role|SUPABASE_(?:URL|ANON_KEY|SERVICE)|sk-[A-Za-z0-9]{16}'
    r'|apify_api_[A-Za-z0-9]{8}|ghp_[A-Za-z0-9]{16}|eyJhbGciOi[A-Za-z0-9]{10}',
    re.I,
)
CAMINHO_WINDOWS = re.compile(r'[A-Za-z]:\\\\|[A-Za-z]:\\[A-Za-z0-9_]|file:///')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def ler(*partes):
    with open(os.path.join(DEPLOY, *partes), 'rb') as f:
        return f.read()


def index_bytes():
    return gzip.decompress(ler('deploy-index.html.gz'))


def manifesto():
    return json.loads(ler('ASSETS-SHA256.json').decode('utf-8'))


class TestemunhaIntacta(unittest.TestCase):
    """Adicionar ativos nao pode ter mexido em um byte do casco."""

    def test_index_gzipado_devolve_o_sha_do_closeout(self):
        b = index_bytes()
        esperado, tamanho = TESTEMUNHA['index.html']
        self.assertEqual(len(b), tamanho)
        self.assertEqual(sha(b), esperado)

    def test_support_e_crop_map_intactos(self):
        for nome in ('support.js', 'crop-map.js'):
            b = ler(nome)
            esperado, tamanho = TESTEMUNHA[nome]
            self.assertEqual(len(b), tamanho, nome)
            self.assertEqual(sha(b), esperado, nome)

    def test_vercel_json_nao_foi_tocado(self):
        b = ler('vercel.json')
        self.assertEqual(len(b), 23)
        self.assertEqual(sha(b), 'b7790313601a6aa7f38753ce99ec631e840e629d9268569c7fd964c4bf745842')
        self.assertEqual(json.loads(b.decode('utf-8')), {'cleanUrls': True})

    def test_gitattributes_protege_a_pasta(self):
        """core.autocrlf esta ligado: sem esta regra as fontes e PNGs corrompem no checkout."""
        with open(os.path.join(ROOT, '.gitattributes'), encoding='utf-8') as f:
            self.assertIn('casco/canonical/** -text -diff', f.read())


class ReferenciasResolvem(unittest.TestCase):
    """A falha que passou batido: HTML pedindo arquivo que ninguem commitou."""

    def setUp(self):
        self.html = index_bytes().decode('utf-8', 'replace')
        self.man = manifesto()

    def refs(self):
        achados = set()
        for m in re.finditer(r'(?:src|href)="([^"]+)"', self.html):
            u = m.group(1)
            if u.startswith(('http:', 'https:', 'data:', '#')):
                continue
            achados.add(u[2:] if u.startswith('./') else u)
        return achados

    def test_toda_referencia_local_tem_arquivo(self):
        proprios = set(TESTEMUNHA)
        for ref in self.refs():
            if ref in proprios:
                continue
            self.assertIn(ref, self.man, 'referencia do index.html sem arquivo: %s' % ref)

    def test_o_index_referencia_o_design_system_e_as_imagens(self):
        """Guarda contra um export futuro que embuta tudo e torne o manifesto mentiroso."""
        refs = self.refs()
        self.assertTrue(any(r.startswith('_ds/') for r in refs))
        self.assertTrue(any(r.startswith('assets/') for r in refs))

    def test_support_js_e_carregado_pelo_index(self):
        self.assertIn('src="./support.js"', self.html)

    def test_crop_map_js_e_carregado(self):
        self.assertIn('crop-map.js', self.html)


class ManifestoConfere(unittest.TestCase):

    def setUp(self):
        self.man = manifesto()

    def caminho_em_disco(self, rel, meta):
        alvo = meta['stored_as'] if meta.get('stored') == 'gzip' else rel
        return os.path.join(DEPLOY, *alvo.split('/'))

    def test_todo_ativo_do_manifesto_existe_e_bate(self):
        for rel, meta in self.man.items():
            with open(self.caminho_em_disco(rel, meta), 'rb') as f:
                b = f.read()
            if meta.get('stored') == 'gzip':
                b = gzip.decompress(b)
            self.assertEqual(len(b), meta['bytes'], rel)
            self.assertEqual(sha(b), meta['sha256'], rel)

    def test_nenhum_ativo_em_disco_fica_de_fora_do_manifesto(self):
        no_disco = set()
        for raiz in ('_ds', 'assets'):
            for base, _, arquivos in os.walk(os.path.join(DEPLOY, raiz)):
                for a in arquivos:
                    p = os.path.relpath(os.path.join(base, a), DEPLOY).replace(os.sep, '/')
                    no_disco.add(p[:-3] if p.endswith('.gz') else p)
        self.assertEqual(no_disco - set(self.man), set())
        self.assertEqual(set(self.man) - no_disco, set())

    def test_o_gzip_e_declarado_e_justificado(self):
        """O antivirus deste ambiente remove .js do disco; quem guardar assim precisa dizer por que."""
        for rel, meta in self.man.items():
            if meta.get('stored') == 'gzip':
                self.assertTrue(meta['stored_as'].endswith('.gz'), rel)
                self.assertIn('antivirus', meta.get('motivo', ''), rel)


class NadaVazaParaONavegador(unittest.TestCase):

    def servidos(self):
        yield 'index.html', index_bytes()
        for nome in ('support.js', 'crop-map.js'):
            yield nome, ler(nome)
        for rel, meta in manifesto().items():
            if not rel.endswith(('.js', '.css', '.json', '.md', '.svg')):
                continue
            alvo = meta['stored_as'] if meta.get('stored') == 'gzip' else rel
            b = ler(*alvo.split('/'))
            yield rel, gzip.decompress(b) if meta.get('stored') == 'gzip' else b

    def test_nenhum_segredo(self):
        for nome, b in self.servidos():
            achado = SEGREDOS.search(b.decode('utf-8', 'replace'))
            self.assertIsNone(achado, '%s: %s' % (nome, achado.group(0) if achado else ''))

    def test_nenhum_caminho_local_de_windows(self):
        for nome, b in self.servidos():
            achado = CAMINHO_WINDOWS.search(b.decode('utf-8', 'replace'))
            self.assertIsNone(achado, '%s: %s' % (nome, achado.group(0) if achado else ''))

    def test_o_casco_nao_navega_por_url(self):
        """Se um dia passar a navegar, o refresh direto quebra e o Preview precisa de rewrite."""
        texto = (index_bytes() + ler('support.js') + ler('crop-map.js')).decode('utf-8', 'replace')
        for api in ('pushState', 'replaceState', 'popstate'):
            self.assertNotIn(api, texto)


class UmaCopiaSo(unittest.TestCase):

    def test_nao_existe_pasta_deploy_paralela_na_raiz(self):
        self.assertFalse(os.path.isdir(os.path.join(ROOT, 'deploy')))

    def test_a_saida_do_build_nao_e_versionada(self):
        with open(os.path.join(ROOT, '.gitignore'), encoding='utf-8') as f:
            self.assertIn('casco/canonical/deploy-v8-closeout/public/', f.read())

    def test_nao_existe_index_html_solto_ao_lado_da_testemunha(self):
        """A testemunha e o .gz. Um .html irmao seria a segunda copia."""
        self.assertFalse(os.path.exists(os.path.join(DEPLOY, 'index.html')))


class OBuildSeDefende(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(DEPLOY, 'build-preview.mjs'), encoding='utf-8') as f:
            self.src = f.read()

    def test_o_build_carrega_os_sha_do_closeout(self):
        for esperado, _ in TESTEMUNHA.values():
            self.assertIn(esperado, self.src)

    def test_o_build_falha_quando_o_sha_diverge(self):
        self.assertIn('SHA-256 divergente', self.src)

    def test_o_build_reprova_ativo_de_carona_e_ativo_faltando(self):
        self.assertIn('ativo fora do manifesto', self.src)
        self.assertIn('ativos do manifesto que nao sairam', self.src)

    def test_o_build_nao_tem_dependencia(self):
        pkg = json.loads(ler('package.json').decode('utf-8'))
        self.assertNotIn('dependencies', pkg)
        self.assertNotIn('devDependencies', pkg)
        self.assertEqual(pkg['scripts']['build'], 'node build-preview.mjs')

    def test_o_build_so_usa_biblioteca_padrao_do_node(self):
        for m in re.finditer(r"from '([^']+)'", self.src):
            self.assertTrue(m.group(1).startswith('node:'), m.group(1))


class DocumentacaoDeVercel(unittest.TestCase):
    """O briefing pediu sete campos por nome. Nenhum pode sumir numa edicao futura."""

    def setUp(self):
        with open(os.path.join(ROOT, 'docs', 'implementation', 'VERCEL-PREVIEW-V8.md'), encoding='utf-8') as f:
            self.doc = f.read()

    def test_os_sete_campos_estao_declarados(self):
        for campo in ('VERCEL_PROJECT_EXPECTED', 'ROOT_DIRECTORY', 'BUILD_COMMAND',
                      'OUTPUT_DIRECTORY', 'FRAMEWORK_PRESET',
                      'REQUIRED_ENV_VARS_NOW', 'REQUIRED_ENV_VARS_LATER'):
            self.assertIn(campo, self.doc)

    def test_o_root_directory_aponta_para_a_testemunha(self):
        self.assertIn('ROOT_DIRECTORY   = casco/canonical/deploy-v8-closeout', self.doc)
        self.assertIn('OUTPUT_DIRECTORY = public', self.doc)

    def test_a_proibicao_do_service_role_esta_escrita(self):
        self.assertIn('SUPABASE_SERVICE_ROLE_KEY', self.doc)
        self.assertIn('NUNCA no frontend', self.doc)

    def test_o_estado_de_nao_ligado_esta_declarado(self):
        for linha in ('SUPABASE_CONNECTED = NO', 'REAL_DATA_WIRED    = NO',
                      'PRODUCTION_DEPLOY  = NO', 'MAIN_MERGED        = NO'):
            self.assertIn(linha, self.doc)

    def test_as_ressalvas_nao_bloqueadoras_continuam_no_documento(self):
        self.assertIn('_ds_bundle.js', self.doc)
        self.assertIn('unpkg.com', self.doc)
        self.assertIn('cdn.jsdelivr.net', self.doc)


if __name__ == '__main__':
    unittest.main(verbosity=2)
