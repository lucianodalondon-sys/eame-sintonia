# -*- coding: utf-8 -*-
"""UM SÓ TRADUTOR ENTRE O QUE SE COLHE E O QUE SE JULGA.

    O COLETOR OBSERVA. A PORTA PRESERVA. A ADMISSAO JULGA.

O contrato comum (`leis/artefato.py`) fala em MAIÚSCULAS — `SOURCE_ID`,
`FACT_TIME`, `SOURCE_LOCATION`. A admissão lê minúsculas — `source_id`,
`fact_time`, `source_location`. São dois nomes para o mesmo conceito, e medido
em 2026-09-11 há **dez** deles.

O defeito não era «a admissão lê minúsculas». Era que a tradução **já existia,
duas vezes, escrita à mão**:

    coleta/golden_path_pdf.py        traduz 6 campos, à mão
    coleta/rota_forward_documento.py traduz 6 campos, à mão, outro subconjunto
    orquestrador/orquestrador.py     NÃO traduz — e é a rota canónica

```
UMA TRADUCAO SEM DONO NAO E UMA TRADUCAO: SAO TRES.
```

E o remendo óbvio seria o pior de todos:

    item.get("SOURCE_ID") or item.get("source_id") or item.get("fonte")

espalhado por cada leitor. Isso não dá um dono à tradução — dá-lhe um por
ficheiro, e eles divergem no dia em que alguém acrescentar um alias a um só.

Esta trava prende UM tradutor, na fronteira, e o valor tem de atravessar
**exactamente igual**.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import ingresso as ing  # noqa: E402


class HaUmSoTradutor(unittest.TestCase):

    def test_o_tradutor_existe_e_vive_na_fronteira(self):
        self.assertTrue(
            hasattr(ing, "para_a_porta"),
            "não há tradutor canónico. Sem ele, cada leitor inventa o seu "
            "`or` e a casa fica com um dono por ficheiro.")

    def test_o_mapa_de_nomes_e_declarado_e_nao_adivinhado(self):
        self.assertTrue(hasattr(ing, "PARA_A_PORTA"))
        self.assertIn("SOURCE_ID", ing.PARA_A_PORTA)
        self.assertEqual(ing.PARA_A_PORTA["SOURCE_ID"], "source_id")


class OValorAtravessaIntacto(unittest.TestCase):
    """Traduzir é mudar o nome. Mudar o valor seria outra coisa, e é proibida."""

    def test_o_source_id_chega_igual(self):
        fora = ing.para_a_porta({"SOURCE_ID": "IT-T2-002", "texto": "prosa"})
        self.assertEqual(fora["source_id"], "IT-T2-002")

    def test_nenhum_valor_e_reescrito(self):
        dentro = {"SOURCE_ID": "IT-T2-002", "FACT_TIME": "2026-09-02",
                  "SOURCE_LOCATION": "IT", "texto": "prosa"}
        fora = ing.para_a_porta(dentro)
        self.assertEqual(fora["source_id"], "IT-T2-002")
        self.assertEqual(fora["fact_time"], "2026-09-02")
        self.assertEqual(fora["source_location"], "IT")

    def test_o_que_ja_estava_na_lingua_da_porta_fica(self):
        fora = ing.para_a_porta({"source_id": "IT-T3-005", "texto": "prosa"})
        self.assertEqual(fora["source_id"], "IT-T3-005")

    def test_a_saida_fala_uma_lingua_so(self):
        """Renomear, e não duplicar: dois nomes na saída é a própria doença."""
        fora = ing.para_a_porta({"SOURCE_ID": "IT-T2-002", "texto": "prosa"})
        self.assertIn("source_id", fora)
        self.assertNotIn("SOURCE_ID", fora,
                         "o item saiu a falar duas linguas ao mesmo tempo")

    def test_campo_desconhecido_viaja_sem_ser_tocado(self):
        fora = ing.para_a_porta({"DOCUMENT_ID": "ARPAV_Z24", "texto": "prosa"})
        self.assertEqual(fora["DOCUMENT_ID"], "ARPAV_Z24")

    def test_ausente_nao_vira_vazio(self):
        """`NAO SEI` não se fabrica aqui, e ausência não vira string vazia."""
        fora = ing.para_a_porta({"texto": "prosa"})
        self.assertNotIn("source_id", fora)


class ODoisNomesComDoisValores(unittest.TestCase):
    """O caso que não pode ser resolvido em silêncio."""

    def test_iguais_nao_sao_conflito(self):
        fora = ing.para_a_porta({"SOURCE_ID": "IT-T2-002",
                                 "source_id": "IT-T2-002", "texto": "p"})
        self.assertEqual(fora["source_id"], "IT-T2-002")

    def test_diferentes_nao_se_escolhem_em_silencio(self):
        with self.assertRaises(ing.AliasEmConflito):
            ing.para_a_porta({"SOURCE_ID": "IT-T2-002",
                              "source_id": "IT-T9-999", "texto": "p"})

    def test_o_conflito_diz_os_dois_valores(self):
        try:
            ing.para_a_porta({"FACT_TIME": "2026-09-02", "fact_time": "1999-01-01"})
        except ing.AliasEmConflito as ex:
            self.assertIn("2026-09-02", str(ex))
            self.assertIn("1999-01-01", str(ex))
        else:
            self.fail("dois valores diferentes passaram sem queixa")


class ADecisaoDaPortaMudaDeVerdade(unittest.TestCase):
    """A prova do seam: o mesmo valor, a mesma porta, outra resposta."""

    def test_source_id_deixa_de_parecer_ausente(self):
        cru = {"id": "x", "texto": "Bollettino agrometeorologico con dati.",
               "SOURCE_ID": "IT-T2-002"}
        antes = adm.decidir(cru, "T2", corrida="SEAM")
        depois = adm.decidir(ing.para_a_porta(cru), "T2", corrida="SEAM")
        self.assertIn("de onde este item veio", antes.motivo)
        self.assertNotIn("de onde este item veio", depois.motivo,
                         "a origem continua a parecer ausente depois de traduzir")

    def test_a_semantica_da_porta_nao_mudou(self):
        """Traduzir move a porta para a PRÓXIMA pergunta — não a faz dizer SIM."""
        cru = {"id": "x", "texto": "Bollettino agrometeorologico con dati.",
               "SOURCE_ID": "IT-T2-002"}
        d = adm.decidir(ing.para_a_porta(cru), "T2", corrida="SEAM")
        self.assertIn(d.resultado, adm.RESULTADOS)
        self.assertNotEqual(d.resultado, adm.SIM,
                            "se isto virou SIM, alguma regra foi relaxada")


if __name__ == "__main__":
    unittest.main()


class OsDezAtaques(unittest.TestCase):
    """Red team do tradutor. O valor é sagrado; o nome é que muda."""

    def d(self, item):
        return ing.para_a_porta(item)

    def test_1_so_maiusculo(self):
        self.assertEqual(self.d({"SOURCE_ID": "IT-T2-002"})["source_id"], "IT-T2-002")

    def test_2_so_minusculo_legado(self):
        fora = self.d({"source_id": "IT-T2-002"})
        self.assertEqual(fora["source_id"], "IT-T2-002")

    def test_3_os_dois_iguais(self):
        fora = self.d({"SOURCE_ID": "IT-T2-002", "source_id": "IT-T2-002"})
        self.assertEqual(fora["source_id"], "IT-T2-002")
        self.assertNotIn("SOURCE_ID", fora)

    def test_4_os_dois_diferentes(self):
        with self.assertRaises(ing.AliasEmConflito):
            self.d({"SOURCE_ID": "IT-T2-002", "source_id": "IT-T9-999"})

    def test_5_vazio_e_vazio_e_nao_desaparece(self):
        """Vazio declarado não é o mesmo que ausente — e não se promove a `NAO SEI`."""
        fora = self.d({"SOURCE_ID": ""})
        self.assertIn("source_id", fora)
        self.assertEqual(fora["source_id"], "")

    def test_6_unknown_atravessa_como_unknown(self):
        fora = self.d({"SOURCE_ID": "NAO SEI"})
        self.assertEqual(fora["source_id"], "NAO SEI",
                         "UNKNOWN PERMANECE UNKNOWN: nao se converte em ausencia")

    def test_7_fact_time(self):
        self.assertEqual(self.d({"FACT_TIME": "2026-09-02"})["fact_time"], "2026-09-02")
        with self.assertRaises(ing.AliasEmConflito):
            self.d({"FACT_TIME": "2026-09-02", "fact_time": "1999-01-01"})

    def test_8_published_at(self):
        self.assertEqual(self.d({"PUBLISHED_AT": "2026-09-01"})["published_at"],
                         "2026-09-01")

    def test_9_campo_desconhecido_nao_e_inventado_nem_apagado(self):
        fora = self.d({"CAMPO_QUE_NINGUEM_CONHECE": "x", "texto": "p"})
        self.assertEqual(fora["CAMPO_QUE_NINGUEM_CONHECE"], "x")
        self.assertEqual(len([k for k in fora if k.lower() == "campo_que_ninguem_conhece"]), 1)

    def test_10_nenhum_valor_e_alterado_em_todo_o_mapa(self):
        """Percorre o mapa inteiro: cada valor sai bit a bit igual ao que entrou."""
        dentro = {de: "valor-de-%s" % de for de in ing.PARA_A_PORTA}
        fora = self.d(dentro)
        for de, para in ing.PARA_A_PORTA.items():
            with self.subTest(campo=de):
                self.assertEqual(fora[para], dentro[de])
                self.assertNotIn(de, fora)


class ORuntimeUsaOTradutorEUmSo(unittest.TestCase):
    """A trava contra o `or` espalhado voltar por distracção."""

    ROTAS = ("orquestrador/orquestrador.py", "coleta/golden_path_pdf.py",
             "coleta/rota_forward_documento.py")

    def corpo(self, f):
        import ast
        with open(os.path.join(RAIZ, f), encoding="utf-8") as fh:
            arvore = ast.parse(fh.read())
        for no in ast.walk(arvore):
            if isinstance(no, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                               ast.ClassDef)) and ast.get_docstring(no):
                no.body = no.body[1:]
        return ast.unparse(arvore)

    def test_toda_rota_que_julga_passa_pelo_tradutor(self):
        for f in self.ROTAS:
            with self.subTest(rota=f):
                self.assertIn("para_a_porta", self.corpo(f),
                              "%s entrega a admissao sem atravessar a fronteira" % f)

    def test_nenhuma_rota_monta_o_item_da_porta_a_mao(self):
        """O item que vai a julgamento não nasce de um mapa escrito à mão.

        ⚠️ ESTA TRAVA JA FOI LARGA DEMAIS, e apanhou uma coisa legítima:
        `rota_forward_documento._identidade()` também mapeia `SOURCE_ID` para
        `source_id` — mas para a TELEMETRIA (`rastro_da_coleta`), que tem
        vocabulário próprio e não é a porta. Forçá-la pelo tradutor da porta
        seria fazer o tradutor conhecer um terceiro contrato.

            NEM TODO MAPA DE NOMES E O MESMO MAPA. O QUE IMPORTA E O DESTINO.

        Por isso a trava olha para o item que vai a `decidir()`, e não para
        qualquer par de nomes no ficheiro.
        """
        for f in self.ROTAS:
            c = self.corpo(f)
            with self.subTest(rota=f):
                self.assertNotIn('"source_id": a["SOURCE_ID"]', c)
                self.assertNotIn("item = {'id': unidade['CONTENT_ID']", c)

    def test_o_mapa_da_porta_vive_num_sitio_so(self):
        """Um mapa por destino. Este teste conta os do DESTINO «porta»."""
        import re
        donos = []
        for raiz_dir in ("coleta", "admissao", "orquestrador", "leis", "guarda"):
            for base, _, fs in os.walk(os.path.join(RAIZ, raiz_dir)):
                for f in sorted(fs):
                    if not f.endswith(".py"):
                        continue
                    caminho = os.path.join(base, f)
                    with open(caminho, encoding="utf-8") as fh:
                        if re.search(r"^PARA_A_PORTA\s*=\s*\{", fh.read(), re.M):
                            donos.append(os.path.relpath(caminho, RAIZ))
        self.assertEqual(donos, ["coleta/ingresso.py"],
                         "o mapa da porta tem %d donos: %s" % (len(donos), donos))


class UmItemQueSeContradizNaoRebentaACorrida(unittest.TestCase):
    """A mutação encontrou este buraco: nada prendia o que a rota faz no conflito.

        RECUSA NA PORTA != REJEITADO NA ADMISSAO != ERRO != NAO CORREU.

    Um item que se contradiz sobre a própria origem não é uma rejeição e não é
    uma corrida falhada: é um item que **não se consegue ler**. A porta já tem
    palavra para isso — `ERRO`, por `erro_de_leitura` — e é essa que se usa,
    sem inventar estado novo e sem derrubar as outras unidades da corrida.
    """

    def setUp(self):
        import orquestrador as orq
        self.orq = orq
        # ⚠️ `pela_porta` CHAMA `adm.escrever(decisoes)`, E O LIVRO E VERSIONADO.
        # A primeira versao desta trava despejou 417 linhas de decisoes de teste
        # dentro de `data/samples/LIVRO-DE-DECISOES.json`.
        #
        #     UM TESTE QUE ESCREVE NO ACERVO NAO ESTA A TESTAR O SISTEMA:
        #     ESTA A ALTERA-LO.
        #
        # O livro fica intocado: guarda-se o conteudo e repoe-se no fim.
        import admissao
        self.livro = admissao.LIVRO
        try:
            with open(self.livro, encoding="utf-8") as f:
                antes = f.read()
        except OSError:
            antes = None
        self.addCleanup(self._repor, antes)

    def _repor(self, antes):
        if antes is None:
            if os.path.exists(self.livro):
                os.remove(self.livro)
        else:
            with open(self.livro, "w", encoding="utf-8") as f:
                f.write(antes)

    def test_o_conflito_nao_levanta_e_nao_para_os_outros(self):
        bons = {"id": "bom", "texto": "Bollettino con dati di campo.",
                "SOURCE_ID": "IT-T2-002"}
        mau = {"id": "mau", "texto": "Bollettino con dati di campo.",
               "SOURCE_ID": "IT-T2-002", "source_id": "IT-T9-999"}
        r = self.orq.pela_porta([bons, mau], "T2", "RUN-CONFLITO")
        self.assertEqual(r["itens"], 2, "uma unidade ma levou as outras")
        self.assertEqual(r["por_resultado"].get(adm.ERRO), 1,
                         "o item que se contradiz devia sair ERRO: %s"
                         % r["por_resultado"])

    def test_o_erro_nao_e_rejeicao(self):
        mau = {"id": "mau", "texto": "prosa",
               "SOURCE_ID": "IT-T2-002", "source_id": "IT-T9-999"}
        r = self.orq.pela_porta([mau], "T2", "RUN-CONFLITO")
        self.assertEqual(r["por_resultado"].get(adm.NAO), None,
                         "um item ilegivel nao pode sair REJEITADO")

    def test_o_motivo_diz_os_dois_valores(self):
        mau = {"id": "mau", "texto": "prosa",
               "SOURCE_ID": "IT-T2-002", "source_id": "IT-T9-999"}
        item = dict(mau)
        try:
            ing.para_a_porta(item)
        except ing.AliasEmConflito as ex:
            d = adm.decidir(dict(mau, erro_de_leitura=str(ex)), "T2", corrida="x")
            self.assertEqual(d.resultado, adm.ERRO)
            self.assertIn("IT-T9-999", str(d.evidencia))
