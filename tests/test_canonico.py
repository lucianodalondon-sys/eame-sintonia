#!/usr/bin/env python3
"""
Provas de consistência dos documentos canônicos.

Um estado antigo não pode sobreviver num documento canônico e contradizer o estado
final. Estes testes comparam o que os documentos DECLARAM com o que eles CONTÊM.
"""
import os, re, unittest
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'docs')

def rd(*p):
    with open(os.path.join(D, *p), encoding='utf-8') as f:
        return f.read()

FONTES = rd('fontes', 'ATLAS-DE-FONTES-EAME.md')
CAPS = rd('capacidades', 'ATLAS-DE-CAPACIDADES-EAME.md')
CRUZ = rd('cruzamentos', 'MATRIZ-DE-CRUZAMENTOS-EAME.md')
FERR = rd('ferramentas', 'CATALOGO-DE-FERRAMENTAS-EAME.md')
CASOS = rd('apresentacao', 'CASOS-PARA-APRESENTACAO.md')

SOURCE_ID = re.compile(r'^SOURCE_ID:\s+(\S[^\n#]*)', re.M)


def source_ids():
    """Todos os SOURCE_IDs reais, expandindo fichas que cobrem mais de uma fonte."""
    ids = set()
    for m in SOURCE_ID.finditer(FONTES):
        raw = m.group(1).strip()
        if raw.startswith('#') or '<' in raw:      # linha de template
            continue
        raw = re.sub(r'\(.*?\)', '', raw)
        for part in re.split(r'[·/]', raw):
            part = part.strip()
            if re.fullmatch(r'(EU|FR|ES|IT)-T\d{1,2}-\d{3}', part):
                ids.add(part)
    # fontes testadas que só aparecem em tabela de "não alcançadas"
    for m in re.finditer(r'\|\s*((?:EU|FR|ES|IT)-T\d{1,2}-\d{3})\s*\|', FONTES):
        ids.add(m.group(1))
    return ids


class TestContagens(unittest.TestCase):
    """O número declarado tem de ser o número real."""

    def test_fontes_placar_bate_com_o_declarado(self):
        topo = re.search(r'\*\*(\d+) fontes registradas\*\* \((\d+) GREEN, (\d+) YELLOW, (\d+) NÃO SEI\)', FONTES)
        self.assertIsNotNone(topo, 'cabeçalho do atlas de fontes sem contagem declarada')
        tot = re.search(r'\| \*\*Total\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|', FONTES)
        self.assertIsNotNone(tot, 'placar sem linha de Total')
        g, y, r, ns, t = (int(x) for x in tot.groups())
        self.assertEqual(int(topo.group(1)), t, 'cabeçalho e placar discordam no total')
        self.assertEqual(int(topo.group(2)), g, 'cabeçalho e placar discordam em GREEN')
        self.assertEqual(int(topo.group(3)), y, 'cabeçalho e placar discordam em YELLOW')
        self.assertEqual(int(topo.group(4)), ns, 'cabeçalho e placar discordam em NÃO SEI')
        self.assertEqual(g + y + r + ns, t, 'as parcelas do placar não somam o total')

    def test_total_de_fontes_bate_com_os_source_ids_reais(self):
        self.assertEqual(len(source_ids()),
                         int(re.search(r'\| \*\*Total\*\* \| .*?\| \*\*(\d+)\*\* \|$', FONTES, re.M).group(1)),
                         'o total declarado não bate com os SOURCE_IDs presentes no documento')

    def test_capacidades_declaradas_batem_com_as_fichas(self):
        secoes = re.findall(r'^### (CAP-\d+)', CAPS, re.M)
        comprovadas = len(re.findall(r'^CONFIDENCE:\s+COMPROVADO', CAPS, re.M))
        declarado = int(re.search(r'\*\*(\d+) capacidades COMPROVADAS\*\*', CAPS).group(1))
        placar = int(re.search(r'\| COMPROVADO \| (\d+) \|', CAPS).group(1))
        self.assertEqual(len(secoes), len(set(secoes)), 'há CAP duplicado')
        self.assertEqual(declarado, placar, 'cabeçalho e placar de capacidades discordam')
        self.assertEqual(declarado, comprovadas,
                         'o número declarado não bate com as fichas CONFIDENCE: COMPROVADO')

    def test_casos_declarados_batem_com_as_secoes_e_a_tabela(self):
        secoes = re.findall(r'^### (CASE-\d+)', CASOS, re.M)
        linhas = re.findall(r'^\| (CASE-\d+)', CASOS, re.M)
        declarado = int(re.search(r'\*\*(\d+) casos registrados\*\*', CASOS).group(1))
        self.assertEqual(sorted(secoes), sorted(linhas),
                         'a tabela de casos e as seções não listam os mesmos CASE_ID')
        self.assertEqual(declarado, len(secoes), 'número de casos declarado ≠ seções existentes')

    def test_ferramentas_declaradas_batem_com_as_fichas(self):
        fichas = re.findall(r'^### (.+?) — `(.+?)`', FERR, re.M)
        declarado = int(re.search(r'\*\*(\d+) fichas\*\*', FERR).group(1))
        self.assertEqual(declarado, len(fichas), 'número de fichas de ferramenta declarado ≠ real')


class TestCruzamentos(unittest.TestCase):
    """A tabela de candidatos não pode contradizer a ficha do cruzamento."""

    def classes(self):
        out = {}
        for m in re.finditer(r'^### (X-\d+)[^\n]*\n(.*?)(?=^### |\Z)', CRUZ, re.M | re.S):
            c = re.search(r'^CLASS:\s+(.+)$', m.group(2), re.M)
            if c:
                out.setdefault(m.group(1), []).append(
                    re.sub(r'[*`]', '', c.group(1)).split('—')[0].split('(')[0].strip())
        return out

    def test_placar_de_cruzamentos_bate(self):
        cl = {k: v[0] for k, v in self.classes().items()}
        cont = Counter(cl.values())
        for classe, chave in [('COMPROVADO', 'COMPROVADO'), ('PARCIAL', 'PARCIAL'),
                              ('NÃO COMPÕE', 'NÃO COMPÕE')]:
            m = re.search(rf'\| {re.escape(chave)} \| (\d+) \|', CRUZ)
            self.assertIsNotNone(m, f'placar sem linha para {chave}')
            self.assertEqual(cont[classe], int(m.group(1)),
                             f'placar de {chave} não bate com as fichas CLASS:')

    def test_tabela_de_candidatos_nao_contradiz_a_ficha(self):
        cl = {k: v[0] for k, v in self.classes().items()}
        for m in re.finditer(r'^\| (X-\d+) \| [^|]+ \| (.+?) \|$', CRUZ, re.M):
            xid, txt = m.group(1), re.sub(r'[*]', '', m.group(2))
            if xid not in cl:
                continue
            with self.subTest(cruzamento=xid):
                self.assertIn(cl[xid].split()[0], txt,
                              f'{xid}: a tabela diz "{txt}" mas a ficha diz "{cl[xid]}"')

    def test_x001_nao_afirma_mais_que_falta_disease_alert(self):
        """O componente DISEASE existe desde T3; o motivo antigo não pode sobreviver."""
        linha = re.search(r'^\| X-001 \|.*$', CRUZ, re.M).group(0)
        self.assertNotIn('falta DISEASE ALERT', linha,
                         'estado antigo de X-001 sobreviveu na tabela de candidatos')


if __name__ == '__main__':
    unittest.main(verbosity=2)
