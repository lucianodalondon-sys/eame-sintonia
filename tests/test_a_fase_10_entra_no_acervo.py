# -*- coding: utf-8 -*-
"""A PROVA DA PASSAGEM DA `027` MEDE O CENARIO, E NAO A ARITMETICA DO DIA.

O DEFEITO QUE ESTAS GUARDAS EXISTEM PARA IMPEDIR
------------------------------------------------
`provas/a_fase_10_entra_no_acervo.py` encena um banco com tudo aplicado menos
a `027`, corre o aplicador canonico e pergunta o que ele fez. Durante um tempo
ela perguntou isso assim:

    _e("AS_ANTERIORES_FORAM_SALTADAS_COM_HASH_A_BATER", len(saltadas), 25)
    _e("NENHUMA_FOI_PULADA",     len(... MIGRATION_ ...), 26)

`25` e `26` eram verdade no dia em que foram escritos. Chegaram a `028`, a
`029` e a `030` — o cenario nao mudou NADA, continuou a haver exactamente uma
migration pendente — e a prova reprovou na contagem, com o CI vermelho.

    O CENARIO E «SO A 027 ESTA PENDENTE».
    NAO E «HA 26 MIGRATIONS».

E o conserto tentador era o pior de todos: trocar `25` por `28` e `26` por
`29`. Isso nao conserta defeito nenhum — apenas o adia ate a `031`, e nessa
altura ja ninguem se lembra porque e que o numero estava la.

    TROCAR O NUMERO NAO E CONSERTAR O NUMERO.
    E MARCAR ENCONTRO COM O MESMO DEFEITO.

O que estas guardas cobram e a forma da pergunta: o destino de cada migration
compara-se por CONJUNTO DE VERSOES, nunca por quantidade, e o universo le-se
do disco a cada corrida. Uma migration nova passa a entrar sozinha.

POR QUE E QUE ELAS LEEM O CODIGO E NAO O TEXTO
----------------------------------------------
Esta docstring EXPLICA o defeito, e escreve os numeros `25`, `26`, `28`, `29`
para os explicar. Uma guarda que procurasse esses numeros no ficheiro leria a
explicacao e reprovaria a cura. Por isso todas elas atravessam a AST.

    PROCURAR O TEXTO DA REGRA NAO E MEDIR A REGRA.
"""
import ast
import io
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROVA = "provas/a_fase_10_entra_no_acervo.py"
MIGRACOES = os.path.join(RAIZ, "supabase", "migrations")

# As perguntas cujo «esperado» NUNCA pode ser um numero escrito a mao: sao
# exactamente as que dizem o que o aplicador fez a cada migration.
DESTINOS = (
    "AS_ANTERIORES_FORAM_SALTADAS_COM_HASH_A_BATER",
    "NENHUM_SKIP_FOI_POR_OBJETO_JA_EXISTIR",
    "A_027_FOI_APLICADA",
    "NENHUMA_OUTRA_FOI_APLICADA",
    "NENHUMA_FOI_PULADA",
    "E_NENHUMA_TEVE_DESTINO_ESTRANHO",
    "O_LIVRO_RAZAO_FECHOU_IGUAL_AO_UNIVERSO",
    "O_CENARIO_TEM_A_027_COMO_UNICA_PENDENTE",
)


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
        return f.read()


def _arvore(rel):
    return ast.parse(_fonte(rel))


def _funcao(arvore, nome):
    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name == nome:
            return no
    return None


def _chamadas_de_assercao(no):
    """Cada `(nome_da_pergunta, funcao_chamada, no_da_chamada)` la dentro."""
    achadas = []
    for c in ast.walk(no):
        if not isinstance(c, ast.Call) or not isinstance(c.func, ast.Name):
            continue
        if c.func.id not in ("_e", "_e_conjunto"):
            continue
        if not c.args or not isinstance(c.args[0], ast.Constant):
            continue
        achadas.append((c.args[0].value, c.func.id, c))
    return achadas


def _numeros_em(no):
    return [x.value for x in ast.walk(no)
            if isinstance(x, ast.Constant) and isinstance(x.value, (int, float))
            and not isinstance(x.value, bool)]


def _migrations_no_disco():
    return sorted(f[:3] for f in os.listdir(MIGRACOES) if f.endswith(".sql"))


class TestODestinoComparaSeConjunto(unittest.TestCase):
    """ATAQUES 9 E 10 — «trocar so 25 por 28» e «trocar so 26 por 29»."""

    def setUp(self):
        self.arvore = _arvore(PROVA)
        self.upgrade = _funcao(self.arvore, "parte_upgrade")
        self.assertIsNotNone(self.upgrade, "parte_upgrade desapareceu")
        self.assercoes = _chamadas_de_assercao(self.upgrade)

    def test_1_as_duas_perguntas_que_reprovavam_continuam_a_ser_feitas(self):
        """Apagar as duas asserções era o caminho mais curto para o verde."""
        feitas = {nome for nome, _, _ in self.assercoes}
        for exigida in ("AS_ANTERIORES_FORAM_SALTADAS_COM_HASH_A_BATER",
                        "NENHUMA_FOI_PULADA"):
            self.assertIn(exigida, feitas,
                          "%s deixou de ser perguntada. O CI fica verde e "
                          "ninguem mede a passagem." % exigida)

    def test_2_nenhum_destino_se_compara_com_numero_escrito_a_mao(self):
        """A GUARDA CENTRAL. Para repor `25` alguem tem de voltar a pôr um
        numero no lado esperado de uma destas perguntas — e e isso que aqui
        reprova, com o nome da pergunta na mensagem."""
        for nome, func, chamada in self.assercoes:
            if nome not in DESTINOS:
                continue
            self.assertEqual(
                func, "_e_conjunto",
                "%s compara-se por `%s`. O destino de uma migration e um "
                "CONJUNTO DE VERSOES; `_e` compara valores e abre a porta a "
                "uma contagem." % (nome, func))
            esperado = chamada.args[2] if len(chamada.args) > 2 else None
            self.assertIsNotNone(esperado, "%s sem lado esperado" % nome)
            self.assertEqual(
                [], _numeros_em(esperado),
                "%s voltou a ter um numero no lado esperado. Um numero ali "
                "caduca na proxima migration — foi assim que este CI ficou "
                "vermelho." % nome)

    def test_3_a_quantidade_de_hoje_nao_esta_escrita_na_medicao(self):
        """Nem o total de hoje, nem o total menos um, nem o que a cadeia
        percorre: se algum deles estiver escrito como literal aqui dentro,
        a prova voltou a saber a resposta de cor."""
        no_disco = _migrations_no_disco()
        proibidos = {len(no_disco), len(no_disco) - 1, len(no_disco) - 2}
        achados = set(_numeros_em(self.upgrade)) & proibidos
        self.assertEqual(
            set(), achados,
            "parte_upgrade escreve %s, que e a contagem de migrations de "
            "hoje (%d ficheiros). Amanha nao e." % (sorted(achados), len(no_disco)))

    def test_4_o_universo_le_se_do_disco_a_cada_corrida(self):
        """Se ele passar a ser uma lista escrita, volta a haver um sitio para
        esquecer de actualizar."""
        uni = _funcao(self.arvore, "universo_da_cadeia")
        self.assertIsNotNone(uni, "universo_da_cadeia desapareceu")
        leu = any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                  and c.func.attr == "listdir" for c in ast.walk(uni))
        self.assertTrue(leu, "universo_da_cadeia deixou de ler o disco")
        self.assertEqual(
            [], [v for v in _numeros_em(uni) if v != 3],
            "universo_da_cadeia ganhou um numero. O universo mede-se, "
            "nao se sabe.")

    def test_5_o_esperado_declara_se_antes_de_a_cadeia_correr(self):
        """Declarar depois de ver a saida seria escrever o gabarito a partir
        da resposta — a prova passaria sempre, e nao mediria nada."""
        corpo = self.upgrade.body
        def linha_de(pred):
            for i, no in enumerate(corpo):
                for c in ast.walk(no):
                    if pred(c):
                        return i
            return None
        declarou = linha_de(
            lambda c: isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
            and c.func.id == "universo_da_cadeia")
        correu = linha_de(
            lambda c: isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
            and c.func.id == "aplicar_pela_cadeia")
        self.assertIsNotNone(declarou)
        self.assertIsNotNone(correu)
        self.assertLess(declarou, correu,
                        "o universo passou a ser lido DEPOIS de a cadeia "
                        "correr. Isso e copiar a resposta.")


class TestUmDonoSoParaCadaPapel(unittest.TestCase):
    """`008` confere · `027` e o assunto · `026` precisa do acervo."""

    def setUp(self):
        self.arvore = _arvore(PROVA)

    def _literais_de_codigo(self):
        """Todas as strings que EXECUTAM — docstrings fora, que e onde a
        explicacao vive."""
        fora = set()
        for no in ast.walk(self.arvore):
            corpo = getattr(no, "body", None)
            if isinstance(corpo, list) and corpo and isinstance(
                    no, (ast.Module, ast.ClassDef, ast.FunctionDef)):
                p = corpo[0]
                if (isinstance(p, ast.Expr) and isinstance(p.value, ast.Constant)
                        and isinstance(p.value.value, str)):
                    fora.add(id(p.value))
        return [x for x in ast.walk(self.arvore)
                if isinstance(x, ast.Constant) and isinstance(x.value, str)
                and id(x) not in fora]

    def test_6_o_008_aparece_no_codigo_uma_vez_so(self):
        """Ele fica de fora do universo porque CONFERE, e nao porque alguem
        se lembrou de o excluir em cada laco."""
        quantos = len([x for x in self._literais_de_codigo() if x.value == "008"])
        self.assertEqual(
            1, quantos,
            "o `008` aparece %d vezes no codigo. Ele tem um dono: "
            "SO_VERIFICA. Duas copias de uma regra sao duas oportunidades "
            "de divergir." % quantos)

    def test_7_a_migration_em_prova_tem_um_dono(self):
        arvore = self.arvore
        tem = any(isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "EM_PROVA"
                          for t in n.targets) for n in ast.walk(arvore))
        self.assertTrue(tem, "EM_PROVA desapareceu")
        upgrade = _funcao(arvore, "parte_upgrade")
        crus = [x for x in ast.walk(upgrade)
                if isinstance(x, ast.Constant) and x.value == "027"]
        self.assertEqual(
            [], crus,
            "parte_upgrade voltou a escrever '027' a mao em vez de usar "
            "EM_PROVA.")


class TestUmaMigrationNovaNaoPedeEdicaoNENHUMA(unittest.TestCase):
    """A PROVA DE QUE O DEFEITO MORREU, e nao apenas de que foi remendado.

    Nao ha banco aqui. O que se mede e a algebra: dada a saida que o
    aplicador daria num universo com uma migration a mais, as mesmas
    comparacoes continuam a dar verdade — sem tocar numa linha da prova.
    """

    def setUp(self):
        import importlib.util as u
        s = u.spec_from_file_location("f10", os.path.join(RAIZ, PROVA))
        self.m = u.module_from_spec(s)
        s.loader.exec_module(self.m)

    def _cenario(self, universo, pendentes):
        """A saida que `motor/cadeia_canonica.sh` daria, no vocabulario dele."""
        return ["MIGRATION_%s=PASS" % n if n in pendentes else
                "MIGRATION_%s=SKIP (ja no livro-razao) HASH=MATCH" % n
                for n in sorted(universo)]

    def _mede(self, universo, ja_aplicadas):
        pendentes = universo - ja_aplicadas
        linhas = self._cenario(universo, pendentes)
        saltadas, ja_existir, aplicadas, outras = self.m.o_que_a_cadeia_disse(linhas)
        return {
            # O CENARIO, PRIMEIRO. Sem esta linha o resto media a cadeia a
            # cumprir um cenario qualquer e chamava-lhe o desta prova — e foi
            # exactamente isso que este proprio teste apanhou na estreia.
            "CENARIO_E_UMA_SO": pendentes == {self.m.EM_PROVA},
            "SALTADAS_BATEM": saltadas == (universo & ja_aplicadas),
            "SEM_SKIP_POR_OBJETO": ja_existir == set(),
            "APLICOU_A_PENDENTE": aplicadas & {self.m.EM_PROVA} == {self.m.EM_PROVA},
            "NENHUMA_OUTRA": aplicadas - pendentes == set(),
            "NENHUMA_PULADA": (saltadas | aplicadas) == universo,
            "SEM_DESTINO_ESTRANHO": outras == set(),
        }

    def test_8_o_universo_de_hoje_passa(self):
        hoje = self.m.universo_da_cadeia()
        r = self._mede(hoje, hoje - {self.m.EM_PROVA})
        self.assertTrue(all(r.values()), r)

    def test_9_o_universo_com_a_031_passa_sem_uma_unica_edicao(self):
        """ATAQUE 9, MORTO POR MEDICAO: com a antiga `25`, este cenario
        reprovava e alguem teria de ir la trocar um numero. Agora nao ha
        numero nenhum para trocar."""
        hoje = self.m.universo_da_cadeia()
        amanha = hoje | {"031"}
        r = self._mede(amanha, amanha - {self.m.EM_PROVA})
        self.assertTrue(all(r.values()),
                        "uma migration nova partiu a prova: %s" % r)

    def test_10_e_com_dez_migrations_novas_tambem(self):
        """ATAQUE 10. Se a resposta dependesse da quantidade, dez de uma vez
        era onde se veria."""
        hoje = self.m.universo_da_cadeia()
        amanha = hoje | {"%03d" % n for n in range(31, 41)}
        r = self._mede(amanha, amanha - {self.m.EM_PROVA})
        self.assertTrue(all(r.values()), r)

    def test_11_mas_uma_segunda_pendente_continua_a_reprovar(self):
        """A guarda so vale se ainda souber dizer NAO. Um universo com duas
        pendentes NAO e o cenario desta prova, e tem de aparecer."""
        hoje = self.m.universo_da_cadeia()
        outra = sorted(hoje - {self.m.EM_PROVA})[-1]
        r = self._mede(hoje, hoje - {self.m.EM_PROVA, outra})
        self.assertFalse(r["CENARIO_E_UMA_SO"],
                         "duas pendentes passaram como se fosse uma")
        # E O RESTO CONTINUA A BATER, de proposito: as outras perguntas medem
        # a CADEIA, e a cadeia portou-se bem — aplicou as duas que estavam
        # pendentes. Quem tem de reclamar e quem e dono do cenario.
        #
        #     UMA GUARDA QUE RECLAMA DE TUDO NAO DIZ DE QUE E QUE RECLAMA.
        self.assertTrue(r["NENHUMA_PULADA"] and r["SALTADAS_BATEM"])

    def test_12_e_uma_migration_que_a_cadeia_nunca_menciona_aparece(self):
        """SILENCIO NAO E PASS. Foi por isto que `NENHUMA_FOI_PULADA` nasceu."""
        hoje = self.m.universo_da_cadeia()
        pendentes = hoje - {self.m.EM_PROVA}
        linhas = [l for l in self._cenario(hoje, hoje - pendentes)
                  if "_030=" not in l]
        saltadas, _, aplicadas, _ = self.m.o_que_a_cadeia_disse(linhas)
        self.assertNotEqual(saltadas | aplicadas, hoje,
                            "uma migration desapareceu do log e ninguem viu")

    def test_13_um_skip_por_objeto_ja_existir_nao_passa_por_skip_normal(self):
        """SALTAR PORQUE O LIVRO SABIA nao e SALTAR PORQUE O BANCO DISSE.
        Tem o mesmo aspecto no log, e significa o contrario."""
        linhas = ["MIGRATION_027=SKIP (objetos ja existem; anotado no livro-razao)"]
        saltadas, ja_existir, aplicadas, _ = self.m.o_que_a_cadeia_disse(linhas)
        self.assertEqual(set(), saltadas)
        self.assertEqual({"027"}, ja_existir)
        self.assertEqual(set(), aplicadas)

    def test_14_e_um_FAIL_nao_e_lido_como_aplicada(self):
        saltadas, _, aplicadas, outras = self.m.o_que_a_cadeia_disse(
            ["MIGRATION_027=FAIL"])
        self.assertEqual(set(), aplicadas)
        self.assertEqual(set(), saltadas)
        self.assertEqual({"027"}, outras)


if __name__ == "__main__":
    unittest.main(verbosity=2)
