# -*- coding: utf-8 -*-
"""UM CODIGO T, UM SIGNIFICADO — em todo o codigo vivo desta casa.

Cada teste aqui existe por um defeito MEDIDO em 14/09/2026, nao por simetria:

  · `T5` significava SCIENCE no atlas e "Preco e mercado" em `pedido/pedido.py`;
  · `T7` significava TECHNICAL NETWORK no atlas e "Ciencia e ensaio" no pedido —
    logo «colete materiais de pesquisadores» mandava buscar consultores;
  · `T11` significava EVENTS no atlas e "Solo e agua" no pedido e no scanner;
  · `T12` significava POLICY no atlas e "Substancia ativa" nos dois;
  · `T6` nao existia na lista do pedido, e T6 e' RESEARCHERS;
  · `T13` era "Outro" no pedido, e no atlas e' DISTRIBUTION.

O `INDICE-DE-FONTES.md`, que e gerado, imprimia por isso
«EU-T10-001 · T10 · Politica e subsidio» para a rota de PRECOS DE CEREAIS.

    O ROTULO ESTAVA ERRADO. A IDENTIDADE, NAO. Nenhum SOURCE_ID mudou.

A DEFESA CONTRA O TESTE QUE MENTE
---------------------------------
Um teste que importasse a lista do mesmo sitio que o codigo passaria sempre,
inclusive se os dois estivessem errados juntos. Por isso `test_atlas_*` NAO
importa `_territorios`: ele tem o seu proprio leitor do atlas, escrito aqui, e
compara os dois resultados. Se alguem meter uma copia dentro de
`_territorios.py`, este ficheiro reprova.

E `ESPERADO_EM_2026_09_14` e uma testemunha congelada: se o atlas mudar de
verdade, este teste cai e alguem tem de olhar. Taxonomia nao muda em silencio.
"""
import csv
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import _territorios as T  # noqa: E402

ATLAS = os.path.join(ROOT, 'docs', 'fontes', 'ATLAS-DE-FONTES-EAME.md')

# A testemunha congelada: os 12 significados como o atlas os escrevia em
# 2026-09-14. Isto NAO e uma segunda lista de trabalho — nenhum codigo a le.
# E uma tranca: taxonomia so muda quando um humano vier aqui mudar tambem.
ESPERADO_EM_2026_09_14 = {
    'T1': 'CROP & PRODUCTION',
    'T2': 'CLIMATE / WATER / SOIL',
    'T3': 'PEST / DISEASE / WEEDS',
    'T4': 'REGULATORY',
    'T5': 'SCIENCE',
    'T6': 'RESEARCHERS',
    'T7': 'TECHNICAL NETWORK',
    'T8': 'FARMERS & INFLUENCERS',
    'T9': 'COMPETITORS',
    'T10': 'MARKET / TRADE / INDUSTRY',
    'T11': 'EVENTS',
    'T12': 'POLICY / AGRICULTURAL ENVIRONMENT',
}

# Os nomes da lista que derivou. Nenhum deles pode voltar ao codigo vivo.
NOMES_DA_DERIVA = (
    'Preco e mercado', 'Comercio e distribuicao', 'Ciencia e ensaio',
    'Voz do campo', 'Politica e subsidio', 'Solo e agua', 'Substancia ativa',
)

# Ficheiros de codigo VIVO. Gerado, teste, historico e dado nao entram: um
# relatorio antigo que usava a lista velha nao precisa de ser reescrito.
#
# `--others --exclude-standard` inclui o que AINDA NAO foi commitado, e isso
# nao e detalhe: o red team desta correcao criou um ficheiro novo com uma lista
# paralela e o teste NAO o viu, porque `git ls-files` sozinho so lista o que ja
# esta no indice. Um defeito que so aparece depois do commit e um defeito que
# chega tarde.
def _codigo_vivo():
    saida = subprocess.run(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
        cwd=ROOT, capture_output=True).stdout.decode('utf-8').splitlines()
    fora = ('tests/', 'system-map/tests/', 'system-map/data/', 'build/',
            'research/', 'handoff/', 'prototype/', 'data/samples/',
            'italia-portale/', 'docs/', 'provas/', 'pacote/', 'medidas/',
            'generated')
    vistos, out = set(), []
    for f in saida:
        if not f.endswith(('.py', '.mjs', '.js', '.sh')):
            continue
        if any(x in f for x in fora) or f in vistos:
            continue
        if not os.path.exists(os.path.join(ROOT, f)):
            continue
        vistos.add(f)
        out.append(f)
    return out


class TestAtlasEOUnicoDono(unittest.TestCase):
    """Estes tres NAO importam a lista de `_territorios`: leem o atlas sozinhos."""

    def _ler_o_atlas_por_conta_propria(self):
        with open(ATLAS, encoding='utf-8') as fh:
            txt = fh.read()
        marca = '## OS 12 TERRITÓRIOS'
        self.assertIn(marca, txt,
                      'o atlas perdeu a secao que define os territorios')
        bloco = txt.split(marca, 1)[1].split('###', 1)[0]
        linha = re.compile(r'^\|\s*\*\*(T\d{1,2})\*\*\s*\|\s*([^|]+?)\s*\|',
                           re.M)
        return {c: n.strip() for c, n in linha.findall(bloco)}

    def test_o_atlas_define_exatamente_doze_territorios(self):
        do_atlas = self._ler_o_atlas_por_conta_propria()
        self.assertEqual(12, len(do_atlas))
        self.assertEqual([f'T{i}' for i in range(1, 13)],
                         sorted(do_atlas, key=lambda c: int(c[1:])))

    def test_o_dono_em_codigo_bate_com_o_atlas_lido_aqui(self):
        do_atlas = self._ler_o_atlas_por_conta_propria()
        self.assertEqual(do_atlas, dict(T.TERRITORIOS),
                         '`_territorios.py` divergiu do atlas — ou guardou copia')

    def test_o_atlas_nao_mudou_em_silencio(self):
        do_atlas = self._ler_o_atlas_por_conta_propria()
        self.assertEqual(ESPERADO_EM_2026_09_14, do_atlas,
                         'o atlas mudou a taxonomia. Isso pode estar certo — mas '
                         'exige decisao humana, e atualizar esta testemunha')


class TestOsDozeSignificados(unittest.TestCase):

    def test_cada_codigo_tem_o_significado_oficial(self):
        for codigo, nome in ESPERADO_EM_2026_09_14.items():
            with self.subTest(codigo=codigo):
                self.assertEqual(nome, T.nome_de(codigo))

    def test_todo_codigo_tem_escopo_escrito(self):
        for codigo in T.CODIGOS:
            with self.subTest(codigo=codigo):
                self.assertTrue(T.ESCOPO[codigo].strip(),
                                f'{codigo} sem escopo: um codigo sem escopo '
                                f'volta a ser interpretado por adivinhacao')

    def test_substancia_ativa_pertence_a_regulatorio_e_nao_e_territorio(self):
        # A deriva tinha T12 = "Substancia ativa". O atlas poe substancia ativa
        # DENTRO de T4, e escreve a separacao de camadas em T4.
        self.assertEqual('T4', T.codigo_de('substancia ativa'))
        self.assertEqual('POLICY / AGRICULTURAL ENVIRONMENT', T.nome_de('T12'))
        self.assertIn('substâncias ativas', T.ESCOPO['T4'].lower())

    def test_solo_e_agua_nao_sao_um_territorio_proprio(self):
        # A deriva tinha T11 = "Solo e agua". No atlas, solo e agua sao parte de
        # T2 (CLIMATE / WATER / SOIL), e T11 e' EVENTS.
        self.assertEqual('T2', T.codigo_de('solo'))
        self.assertEqual('T2', T.codigo_de('agua'))
        self.assertEqual('EVENTS', T.nome_de('T11'))


class TestUmaListaUmDono(unittest.TestCase):

    def test_nenhum_ficheiro_vivo_guarda_uma_segunda_lista(self):
        definidor = re.compile(r'"T\d{1,2}"\s*:\s*"[^"]+"')
        culpados = []
        for rel in _codigo_vivo():
            if rel == '_territorios.py':
                continue
            with open(os.path.join(ROOT, rel), encoding='utf-8',
                      errors='replace') as fh:
                txt = fh.read()
            if len(definidor.findall(txt)) >= 3:
                culpados.append(rel)
        self.assertEqual([], culpados,
                         'estes ficheiros vivos definem uma lista de territorios '
                         'propria. O dono e `_territorios.py`, que le o atlas')

    # O que este teste procura e' UM CODIGO T LIGADO A UM NOME DA DERIVA.
    # Nao procura a PALAVRA: as palavras sao legitimas e algumas sao
    # obrigatorias. «Substancia ativa» esta na lista da deriva porque a deriva
    # fazia dela um TERRITORIO; mas a substancia ativa existe de verdade, e' uma
    # CAMADA dentro de T4, e nomeia materia-prima em ficheiros que nada tem a
    # ver com taxonomia.
    #
    # ⚠️ A PRIMEIRA VERSAO DESTE TESTE ACUSAVA A PALAVRA. Em 14/09/2026 apanhou
    # `candidatas/italy_gap_auditoria.py`, na linha
    #     "PORTFOLIO · Substancia ativa do produto": (
    # que e' uma chave de dicionario a nomear uma necessidade de materia-prima —
    # sem nenhum codigo T. Renomear o dado para o teste passar teria piorado o
    # dado para salvar o teste. Afiou-se o teste, e prova-se aqui que ele
    # continua a apanhar o ataque verdadeiro.
    _LIGACAO = re.compile(r'T\d{1,2}')

    def _culpa(self, linha):
        """Culpado = nome da deriva LIGADO a um codigo T, na mesma linha."""
        if linha.lstrip().startswith('#'):
            return False
        if ':' not in linha or '"' not in linha and "'" not in linha:
            return False
        return (any(n in linha for n in NOMES_DA_DERIVA)
                and bool(self._LIGACAO.search(linha)))

    def test_nenhum_nome_da_deriva_voltou_ao_codigo_vivo(self):
        # ── CONTROLE POSITIVO: sem isto, «0 culpados» pode ser detector cego ──
        ataques = ('    "T4": "Substancia ativa",',
                   "    'T10': 'Preco e mercado',",
                   '    T7: "Voz do campo"  # sem aspas no codigo',
                   '    "T11": "Solo e agua",')
        for a in ataques:
            self.assertTrue(self._culpa(a),
                            f'o detector NAO apanhou o ataque real: {a!r}')
        # ── CONTROLE NEGATIVO: o uso legitimo tem de passar ──
        legitimos = ('    "PORTFOLIO · Substancia ativa do produto": (',
                     '    # a deriva tinha T11 = "Solo e agua"',
                     '  PRODUZ="substancia ativa, cultura e alvo nomeados",')
        for l in legitimos:
            self.assertFalse(self._culpa(l),
                             f'o detector acusou uso legitimo: {l!r}')

        culpados = []
        for rel in _codigo_vivo():
            if rel in ('_territorios.py', os.path.join('tests',
                                                       'test_territorios.py')):
                continue
            with open(os.path.join(ROOT, rel), encoding='utf-8',
                      errors='replace') as fh:
                txt = fh.read()
            for linha in txt.splitlines():
                if self._culpa(linha):
                    culpados.append(f'{rel}: {linha.strip()[:80]}')
        self.assertEqual([], culpados,
                         'um nome da lista que derivou voltou ao codigo vivo '
                         'LIGADO a um codigo T')

    def test_o_scanner_do_mapa_le_a_taxonomia_e_nao_a_possui(self):
        with open(os.path.join(ROOT, 'system-map', 'scripts',
                               'scan_sources.py'), encoding='utf-8') as fh:
            txt = fh.read()
        self.assertIn('import _territorios', txt,
                      'o scanner do mapa tem de LER o dono da taxonomia')
        sys.path.insert(0, os.path.join(ROOT, 'system-map', 'scripts'))
        import scan_sources as ss  # noqa
        for codigo, nome in ESPERADO_EM_2026_09_14.items():
            with self.subTest(codigo=codigo):
                self.assertEqual(nome, ss.TERRITORIO[codigo])

    def test_o_pedido_le_a_taxonomia_e_nao_a_possui(self):
        with open(os.path.join(ROOT, 'pedido', 'pedido.py'),
                  encoding='utf-8') as fh:
            txt = fh.read()
        self.assertIn('import _territorios', txt)
        sys.path.insert(0, os.path.join(ROOT, 'pedido'))
        import pedido as P  # noqa
        self.assertEqual(ESPERADO_EM_2026_09_14, dict(P.ALVOS))


class TestPalavraHumana(unittest.TestCase):
    """O que uma pessoa escreve tem de cair no territorio certo.

    A tabela abaixo e a prova do defeito: a coluna ANTES e para onde a deriva
    mandava, e ela esta aqui para que ninguem a reintroduza por engano.
    """

    ESPERADO = {
        'pesquisadores': ('T6', 'T7'),
        'pesquisador': ('T6', 'T7'),
        'materiais de pesquisadores': ('T6', 'T7'),
        'ciencia': ('T5', 'T7'),
        'artigos cientificos': ('T5', 'T7'),
        'ensaio': ('T5', 'T7'),
        'mercado': ('T10', 'T5'),
        'preco': ('T10', 'T5'),
        'precos': ('T10', 'T5'),
        'solo': ('T2', 'T11'),
        'agua': ('T2', 'T11'),
        'substancia ativa': ('T4', 'T12'),
        'moa': ('T4', 'T12'),
        'politica': ('T12', 'T10'),
        'subsidio': ('T12', 'T10'),
        'eventos': ('T11', None),
        'feira': ('T11', None),
        'produtores': ('T8', None),
        'agronomos': ('T7', None),
        'cooperativa': ('T7', None),
        'pragas': ('T3', 'T3'),
        'clima': ('T2', 'T2'),
        'concorrentes': ('T9', 'T9'),
        'rotulos': ('T4', 'T4'),
        'cultura': ('T1', 'T1'),
    }

    def test_cada_palavra_cai_no_territorio_oficial(self):
        sys.path.insert(0, os.path.join(ROOT, 'pedido'))
        import pedido as P  # noqa
        for palavra, (certo, _antes) in self.ESPERADO.items():
            with self.subTest(palavra=palavra):
                self.assertEqual(certo, T.codigo_de(palavra))
                self.assertEqual(certo, P.alvo_de(palavra),
                                 'o pedido e o dono da taxonomia discordam')

    def test_a_deriva_mandava_seis_palavras_para_o_lugar_errado(self):
        # Prova positiva de que o defeito era real, e nao uma limpeza cosmetica.
        erradas = [p for p, (certo, antes) in self.ESPERADO.items()
                   if antes and antes != certo]
        self.assertGreaterEqual(len(erradas), 6,
                                'se isto cair, a tabela de prova foi diluida')

    def test_palavra_ambigua_avisa_em_vez_de_escolher_calada(self):
        sys.path.insert(0, os.path.join(ROOT, 'pedido'))
        import pedido as P  # noqa
        self.assertIsNotNone(P.aviso_do_alvo('producao'))
        self.assertIsNotNone(P.aviso_do_alvo('substancia ativa'))
        self.assertIsNone(P.aviso_do_alvo('pesquisadores'))

    def test_alvo_desconhecido_e_recusado_com_a_lista(self):
        sys.path.insert(0, os.path.join(ROOT, 'pedido'))
        import pedido as P  # noqa
        with self.assertRaises(P.PedidoInvalido) as e:
            P.alvo_de('xpto')
        self.assertIn('T6', str(e.exception),
                      'a recusa tem de mostrar o que existe')


class TestT13(unittest.TestCase):
    """T13 e ocupante legado do atlas, nao territorio — e nao e "Outro"."""

    def test_t13_nao_e_territorio_valido(self):
        self.assertFalse(T.valido('T13'))
        for c in T.CODIGOS:
            self.assertTrue(T.valido(c))

    def test_t13_nao_pode_ser_pedido(self):
        sys.path.insert(0, os.path.join(ROOT, 'pedido'))
        import pedido as P  # noqa
        with self.assertRaises(P.PedidoInvalido):
            P.alvo_de('T13')
        with self.assertRaises(P.PedidoInvalido):
            P.alvo_de('outro')

    def test_t13_esta_declarado_como_excecao_com_os_ids_que_existem(self):
        e = T.EXCECOES['T13']
        self.assertEqual('DISTRIBUTION', e['NOME_NO_ATLAS'])
        self.assertTrue(e['PRESERVAR'])
        self.assertEqual({'FR-T13-001', 'ES-T13-001', 'IT-T13-001'},
                         set(e['IDS_EMITIDOS']))

    def test_os_tres_ids_de_t13_continuam_a_existir(self):
        with open(ATLAS, encoding='utf-8') as fh:
            atlas = fh.read()
        for sid in ('FR-T13-001', 'ES-T13-001', 'IT-T13-001'):
            with self.subTest(sid=sid):
                self.assertIn(sid, atlas,
                              'SOURCE_ID e identidade: nao se apaga nem se '
                              'renomeia por causa de uma arrumacao de lista')

    def test_o_mapa_sabe_nomear_t13_sem_o_canonizar(self):
        sys.path.insert(0, os.path.join(ROOT, 'system-map', 'scripts'))
        import scan_sources as ss  # noqa
        self.assertIn('T13', ss.TERRITORIO)
        self.assertIn('legado', ss.TERRITORIO['T13'].lower())
        self.assertNotIn('T13', T.CODIGOS)


class TestIdentidadePreservada(unittest.TestCase):

    def test_nenhum_source_id_do_atlas_foi_renomeado(self):
        # A lista congelada em 14/09/2026, ANTES da correcao de taxonomia.
        # Se uma arrumacao de lista mexer numa identidade, isto cai.
        congelados = {
            'ES-T1-001', 'ES-T13-001', 'ES-T3-001', 'ES-T4-001', 'ES-T4-002',
            'ES-T4-003', 'ES-T4-005', 'ES-T5-002', 'ES-T7-001', 'ES-T8-001',
            'ES-T8-002', 'ES-T8-003', 'ES-T9-001', 'EU-T1-001', 'EU-T1-002',
            'EU-T10-001', 'EU-T10-002', 'EU-T10-003', 'EU-T12-001',
            'EU-T2-001', 'EU-T2-002', 'EU-T2-003', 'EU-T3-001', 'EU-T4-001',
            'EU-T4-002', 'EU-T5-001', 'EU-T8-001', 'EU-T9-002', 'FR-T1-001',
            'FR-T11-001', 'FR-T13-001', 'FR-T3-001', 'FR-T3-002', 'FR-T4-001',
            'FR-T9-001', 'IT-T1-001', 'IT-T11-001', 'IT-T12-001',
            'IT-T13-001', 'IT-T3-001', 'IT-T4-001', 'IT-T9-001',
        }
        with open(ATLAS, encoding='utf-8') as fh:
            atlas = fh.read()
        achados = set(re.findall(r'\b(?:EU|FR|ES|IT)-T\d{1,2}-\d{3}\b', atlas))
        self.assertEqual(set(), congelados - achados,
                         'um SOURCE_ID desapareceu do atlas')


class TestDadoJaGravado(unittest.TestCase):
    """O que ja esta gravado com a lista velha, medido e NAO reescrito.

    Arrumar a lista nao autoriza reescrever o passado. Um `RUN-MANIFEST` e um
    LOG: diz o que foi pedido naquele dia, com as palavras daquele dia. Mudar o
    log para ele parecer sempre certo apagaria a prova de que a deriva existiu.

    Destes tres registos, UM ficou com significado errado. Ele fica aqui fixado
    para que ninguem o "descubra" depois e o corrija em silencio.
    """

    MANIFESTO = os.path.join(ROOT, 'data', 'samples', 'RUN-MANIFEST.json')

    def _runs(self):
        # O manifesto e um documento com metadados no topo e a lista de
        # execucoes em `RUNS`. A primeira versao deste teste procurou as
        # corridas nas chaves de topo, encontrou zero, e reprovou por isso —
        # um teste a medir o sitio errado acusa um defeito que nao existe.
        with open(self.MANIFESTO, encoding='utf-8') as fh:
            d = json.load(fh)
        return {r.get('RUN_ID'): r for r in d.get('RUNS', [])
                if isinstance(r, dict) and r.get('RUN_ID')}

    def test_so_tres_corridas_carregam_alvo_de_territorio(self):
        com_alvo = [r for r in self._runs().values()
                    if (r.get('PEDIDO') or {}).get('alvo')]
        self.assertEqual(3, len(com_alvo),
                         'mudou o numero de corridas com alvo: remedir a '
                         'classificacao semantica antes de confiar nela')

    def test_duas_corridas_estao_semanticamente_certas(self):
        runs = self._runs()
        for rid, esperado in (('XX-T4-2026-09-07-193647', 'T4'),
                              ('XX-T9-2026-09-07-193647', 'T9')):
            with self.subTest(rid=rid):
                r = runs.get(rid)
                self.assertIsNotNone(r, f'{rid} desapareceu do manifesto')
                alvo = r['PEDIDO']['alvo']
                self.assertEqual(esperado, alvo)
                self.assertEqual(alvo, T.codigo_de(r['MISSION']),
                                 'o codigo gravado e a intencao gravada '
                                 'deixaram de concordar')

    def test_a_corrida_errada_continua_intacta_e_reconhecivel(self):
        # `coleta/corpus_pesquisador.py` foi buscar OpenAlex e ORCID — CIENCIA,
        # que no atlas e T5 (e os autores sao T6). Ficou gravada como T7, que no
        # atlas e REDE TECNICA, porque a lista da deriva chamava T7 de
        # "Ciencia e ensaio".
        r = self._runs().get('XX-T7-2026-09-07-193646')
        self.assertIsNotNone(r, 'o registo com a deriva foi apagado — '
                                'isso apaga a prova de que o defeito existiu')
        self.assertEqual('T7', r['PEDIDO']['alvo'],
                         'o RUN_ID e o alvo sao identidade de proveniencia: '
                         'nao se reescrevem por causa de uma arrumacao de lista')
        self.assertEqual('Ciencia e ensaio', r['MISSION'],
                         'o campo MISSION e o que torna a intencao recuperavel')
        # a prova de que esta errado, medida e nao afirmada:
        self.assertEqual('T5', T.codigo_de(r['MISSION']))
        self.assertNotEqual(T.codigo_de(r['MISSION']), r['PEDIDO']['alvo'])
        # RISCO RESIDUAL, escrito: quem filtrar "corridas de T7" esperando REDE
        # TECNICA vai apanhar esta corrida de ciencia.
        self.assertEqual('TECHNICAL NETWORK', T.nome_de('T7'))


class TestArtefatosDasDuzentasEDezessete(unittest.TestCase):
    """Os artefatos da missao de descoberta ja usavam a lista oficial."""

    CSV = os.path.join(ROOT, 'candidatas',
                       'ITALY-DEEP-SOURCE-IMPORT-READY-2026-09-14.csv')

    def test_o_csv_nao_cita_nenhum_codigo_fora_dos_doze(self):
        if not os.path.exists(self.CSV):
            self.skipTest('artefato da missao de descoberta ausente')
        with open(self.CSV, encoding='utf-8-sig', newline='') as fh:
            linhas = list(csv.DictReader(fh))
        usados = set()
        for r in linhas:
            usados |= set(re.findall(r'\bT\d{1,2}\b',
                                     r['PARA_QUE_SERVE'] + ' ' + r['NOTA']))
        self.assertTrue(usados, 'o CSV nao cita territorio nenhum')
        self.assertEqual(set(), usados - set(T.CODIGOS),
                         'o CSV cita codigo fora dos 12 do atlas')

    def test_o_gerador_da_planilha_le_o_dono(self):
        for nome in ('italy_deep_workbook.py', 'italy_deep_xlsx.py'):
            caminho = os.path.join(ROOT, 'candidatas', nome)
            if not os.path.exists(caminho):
                self.skipTest(f'{nome} ausente')
            with open(caminho, encoding='utf-8') as fh:
                self.assertIn('import _territorios', fh.read(),
                              f'{nome} tem de LER a taxonomia, nao copia-la')


if __name__ == '__main__':
    unittest.main(verbosity=2)
