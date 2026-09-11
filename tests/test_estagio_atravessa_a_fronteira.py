# -*- coding: utf-8 -*-
"""O QUE O INGRESSO APURA TEM DE CHEGAR A QUEM JULGA.

    COL-LAW-502 · DOCUMENTO PRONTO NAO E FATO PRONTO.

A lei existe, a porta implementa-a — `estagio()` lê `artifact_type`, e um RAW é
um DOCUMENTO a quem não se pergunta o tempo do FATO. E mesmo assim a unidade
italiana ouvia «o item não diz quando o fato aconteceu».

Medido em 2026-09-11: o ingresso produz um `Artefato` de 29 campos com
`ARTIFACT_TYPE = RAW`, e `orquestrador.pela_entrada` devolve

    "PRESERVADOS": len(r["ACEITES"])

— **conta as unidades canónicas e deita-as fora**. A linha seguinte entrega à
porta o item ORIGINAL, de 6 campos, sem estágio nenhum.

```
CONTAR UMA COISA NAO E GUARDA-LA.
```

O bloqueio nunca foi `FACT_TIME`. Era a perda do estágio: sem ele a porta não
sabe que está a julgar um documento, e volta a cobrar-lhe o tempo de um facto
que ainda não foi extraído.

A ARMADILHA QUE ESTE TESTE TAMBÉM PRENDE
-----------------------------------------
A ficha preenche o que o coletor não disse com `NAO SEI`. Juntá-la ao item sem
cuidado poria `fact_time = "NAO SEI"` — e `_tem_quando` lê isso como **valor**,
não como confissão. A porta passaria a achar que sabe quando o facto aconteceu.

```
A CONFISSAO DE IGNORANCIA NAO E UM VALOR.
JUNTA-LA COMO SE FOSSE E MENTIR COM A PALAVRA CERTA.
```
"""
import dataclasses
import os
import shutil
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import artefato as art  # noqa: E402
import ingresso as ing  # noqa: E402

CORRIDA = {"RUN_ID": "ESTAGIO-1", "PLATFORM": "HTTP",
           "ACTOR": "coleta/italy_executor.py", "ACTOR_VERSION": "adapter-v1",
           "SOURCE_COUNTRY": "IT", "STARTED_AT": "2026-09-11T00:00:00Z"}


def _payload():
    loja = os.path.join(RAIZ, "data", "collection-store", "italy")
    for base, _, fs in os.walk(loja):
        for f in sorted(fs):
            if not f.endswith(".json"):
                return os.path.relpath(os.path.join(base, f), RAIZ).replace(os.sep, "/")
    return None


class Bancada(unittest.TestCase):

    def setUp(self):
        self.pay = _payload()
        if not self.pay:
            self.skipTest("sem byte real no armazem")
        self.addCleanup(shutil.rmtree, os.path.join(RAIZ, "XX"), True)

    def unidade(self, **kw):
        base = {"id": "e-1", "texto": "Bollettino agrometeorologico con dati.",
                "SOURCE_ID": "IT-T2-002", "DOCUMENT_ID": "ARPAV_PROVA",
                "STORAGE_LOCATION": self.pay, "RUN_ID": CORRIDA["RUN_ID"]}
        base.update(kw)
        return base

    def recebe(self, item):
        return ing.receber([dict(item)], corrida=dict(CORRIDA),
                           armazem=ing.ArmazemLocal(RAIZ), memoria=None, raiz=RAIZ)


class OIngressoDevolveAUnidadeQueApurou(Bancada):

    def test_receber_devolve_a_unidade_pronta_para_a_porta(self):
        r = self.recebe(self.unidade())
        self.assertIn("PARA_A_PORTA", r,
                      "`receber` conta os ACEITES e nao os entrega: a unidade "
                      "canonica morre aqui")
        self.assertEqual(len(r["PARA_A_PORTA"]), 1)

    def test_o_estagio_viaja(self):
        u = self.recebe(self.unidade())["PARA_A_PORTA"][0]
        self.assertEqual(u.get("artifact_type"), art.RAW)

    def test_o_conteudo_original_sobrevive(self):
        u = self.recebe(self.unidade())["PARA_A_PORTA"][0]
        self.assertIn("Bollettino", u.get("texto", ""),
                      "juntar metadata nao pode apagar o conteudo")

    def test_a_identidade_sobrevive_intacta(self):
        u = self.recebe(self.unidade())["PARA_A_PORTA"][0]
        self.assertEqual(u.get("source_id"), "IT-T2-002")
        self.assertEqual(u.get("DOCUMENT_ID"), "ARPAV_PROVA")

    def test_a_confissao_de_ignorancia_nao_viaja_como_valor(self):
        u = self.recebe(self.unidade())["PARA_A_PORTA"][0]
        self.assertNotEqual(u.get("fact_time"), art.NAO_SEI,
                            "«NAO SEI» chegou a porta como se fosse uma data")
        self.assertFalse(u.get("fact_time"),
                         "o item nao declarou tempo: a porta tem de o ver ausente")

    def test_o_recusado_nao_aparece_como_aceite(self):
        """⚠️ A primeira versao deste teste usava `{"id": "mau"}` e assumia
        que a porta o recusaria. Nao recusa: uma observacao sem ficheiro E o
        proprio item, e o ingresso assina o JSON dela. A recusa verdadeira vem
        de quebrar o CONTRATO — aqui, declarar `FACT_LOCATION` sem a base que
        `leis/artefato.py` exige.

            SUPOR QUE UM ITEM E RECUSADO NAO E O MESMO QUE O VER RECUSADO.
        """
        r = self.recebe(self.unidade(FACT_LOCATION="IT-VEN"))
        self.assertTrue(r["RECUSAS"], "o item devia ter quebrado o contrato")
        self.assertEqual(r["PARA_A_PORTA"], [],
                         "um recusado atravessou a fronteira como aceite")

    def test_dois_itens_nao_trocam_metadata(self):
        """Duas unidades na mesma corrida, cada uma com a sua identidade."""
        r = ing.receber([self.unidade(id="a", SOURCE_ID="IT-T2-002"),
                         self.unidade(id="b", SOURCE_ID="IT-T3-005")],
                        corrida=dict(CORRIDA), armazem=ing.ArmazemLocal(RAIZ),
                        memoria=None, raiz=RAIZ)
        fontes = [u.get("source_id") for u in r["PARA_A_PORTA"]]
        self.assertEqual(sorted(fontes), ["IT-T2-002", "IT-T3-005"])


class OEstagioMudaAPerguntaENaoAResposta(Bancada):

    def test_sem_estagio_a_porta_cobra_o_tempo_do_fato(self):
        d = adm.decidir(ing.para_a_porta(self.unidade()), "T2", corrida="x")
        self.assertEqual(d.regra, "tempo do fato")

    def test_com_estagio_a_porta_nao_cobra_o_tempo_do_fato(self):
        u = self.recebe(self.unidade())["PARA_A_PORTA"][0]
        d = adm.decidir(u, "T2", corrida="x")
        self.assertNotEqual(d.regra, "tempo do fato",
                            "um DOCUMENTO continua a ser medido pela regua do FATO")
        self.assertNotIn("quando o fato aconteceu", d.motivo)

    def test_a_semantica_da_porta_nao_mudou(self):
        """Preservar o estágio move a porta para a próxima pergunta — não a
        faz dizer SIM. Se isto virasse SIM, alguma regra teria sido relaxada."""
        u = self.recebe(self.unidade())["PARA_A_PORTA"][0]
        d = adm.decidir(u, "T2", corrida="x")
        self.assertIn(d.resultado, adm.RESULTADOS)
        self.assertNotEqual(d.resultado, adm.SIM)


if __name__ == "__main__":
    unittest.main()


class OsDezAtaques(Bancada):
    """A regra essencial, e ela tem dois lados:

        DOCUMENTO SEM FACT_TIME nao pode reprovar por falta de FACT_TIME.
        FATO SEM FACT_TIME continua a poder responder NAO_SEI.

    Relaxar o segundo para conseguir o primeiro seria trocar um defeito por
    outro maior — e o maior é o que passa despercebido.
    """

    def porta(self, **kw):
        return adm.decidir(ing.para_a_porta(dict(kw)), "T2", corrida="ataque")

    def test_1_RAW_sem_fact_time_nao_reprova_por_tempo(self):
        d = self.porta(id="a", texto="prosa", SOURCE_ID="IT-T2-002",
                       ARTIFACT_TYPE=art.RAW)
        self.assertNotIn("quando o fato aconteceu", d.motivo)

    def test_2_DERIVED_sem_fact_time_nao_reprova_por_tempo(self):
        d = self.porta(id="a", texto="prosa", SOURCE_ID="IT-T2-002",
                       ARTIFACT_TYPE=art.DERIVED, PARENT_ARTIFACT_ID="RAW-1")
        self.assertNotIn("quando o fato aconteceu", d.motivo)

    def test_3_FATO_sem_fact_time_continua_NAO_SEI(self):
        """O outro lado da regra: um FATO sem tempo continua a ser NAO_SEI."""
        d = self.porta(id="a", texto="prosa", SOURCE_ID="IT-T2-002",
                       CROP="VINE")
        self.assertEqual(d.resultado, adm.NAO_SEI)
        self.assertIn("quando o fato aconteceu", d.motivo)

    def test_4_estagio_desconhecido_sem_fact_time_continua_NAO_SEI(self):
        """Quem não se declara continua medido pela régua antiga."""
        d = self.porta(id="a", texto="prosa", SOURCE_ID="IT-T2-002")
        self.assertIn("quando o fato aconteceu", d.motivo)

    def test_5_RAW_com_fact_time_nao_e_estragado(self):
        d = self.porta(id="a", texto="prosa", SOURCE_ID="IT-T2-002",
                       ARTIFACT_TYPE=art.RAW, FACT_TIME="2026-09-02")
        self.assertNotEqual(d.resultado, adm.ERRO)

    def test_6_o_conteudo_nao_some_ao_juntar_metadata(self):
        r = self.recebe(self.unidade())
        self.assertIn("Bollettino", r["PARA_A_PORTA"][0]["texto"])

    def test_7_o_source_id_permanece_intacto(self):
        r = self.recebe(self.unidade())
        self.assertEqual(r["PARA_A_PORTA"][0]["source_id"], "IT-T2-002")

    def test_8_o_document_id_nao_e_fabricado(self):
        """Sem `DOCUMENT_ID` declarado, ninguém o inventa do sha nem do caminho."""
        u = self.unidade()
        u.pop("DOCUMENT_ID")
        pronta = self.recebe(u)["PARA_A_PORTA"][0]
        self.assertIn(pronta.get("DOCUMENT_ID"), (None, "", art.NAO_SEI))

    def test_9_o_recusado_nao_chega_como_aceite(self):
        r = self.recebe(self.unidade(FACT_LOCATION="IT-VEN"))
        self.assertTrue(r["RECUSAS"])
        self.assertEqual(r["PARA_A_PORTA"], [])

    def test_10_dois_itens_na_mesma_corrida_nao_trocam_metadata(self):
        r = ing.receber([self.unidade(id="a", SOURCE_ID="IT-T2-002"),
                         self.unidade(id="b", SOURCE_ID="IT-T3-005")],
                        corrida=dict(CORRIDA), armazem=ing.ArmazemLocal(RAIZ),
                        memoria=None, raiz=RAIZ)
        por_id = {u["id"]: u for u in r["PARA_A_PORTA"]}
        self.assertEqual(por_id["a"]["source_id"], "IT-T2-002")
        self.assertEqual(por_id["b"]["source_id"], "IT-T3-005")


class ARotaCanonicaJulgaOQueAFronteiraAceitou(Bancada):
    """A trava contra o orquestrador voltar a entregar o item original."""

    def test_o_orquestrador_le_PARA_A_PORTA(self):
        import ast
        with open(os.path.join(RAIZ, "orquestrador", "orquestrador.py"),
                  encoding="utf-8") as f:
            arvore = ast.parse(f.read())
        for no in ast.walk(arvore):
            if isinstance(no, (ast.Module, ast.FunctionDef, ast.ClassDef)) \
                    and ast.get_docstring(no):
                no.body = no.body[1:]
        codigo = ast.unparse(arvore)
        self.assertIn("PARA_A_PORTA", codigo)
        self.assertNotIn("pela_porta(itens,", codigo,
                         "a rota voltou a julgar o item que entrou, e nao o "
                         "que a fronteira aceitou")


class OsBuracosQueAMutacaoEncontrou(Bancada):
    """Quatro mutações sobreviveram à primeira versão destas travas.

        UMA MUTACAO QUE SOBREVIVE NAO DIZ QUE O CODIGO ESTA CERTO:
        DIZ QUE NINGUEM ESTAVA A OLHAR PARA AQUELA LINHA.
    """

    class _Ficha:
        """Uma ficha onde TUDO é confissão de ignorância."""
        ARTIFACT_TYPE = art.NAO_SEI
        PARENT_ARTIFACT_ID = "NAO_SE_APLICA"
        PARENT_SHA256 = ""

    def test_M1_nenhuma_confissao_de_ignorancia_atravessa(self):
        """`NAO SEI`, `NAO_SE_APLICA` e vazio não são valores."""
        u = ing.unidade_para_a_porta({"id": "x", "texto": "prosa"}, self._Ficha())
        for campo in ("artifact_type", "parent_artifact_id", "parent_sha256"):
            with self.subTest(campo=campo):
                self.assertNotIn(campo, u,
                                 "a confissao de ignorancia atravessou como valor")

    def test_M3_a_ficha_nao_esmaga_o_que_o_item_ja_afirma(self):
        """O item manda no que ele próprio declarou. A ficha só preenche o vazio."""
        class Outra:
            ARTIFACT_TYPE = art.RAW
            PARENT_ARTIFACT_ID = "RAW-DA-FICHA"
            PARENT_SHA256 = ""
        u = ing.unidade_para_a_porta(
            {"id": "x", "texto": "p", "ARTIFACT_TYPE": art.DERIVED,
             "PARENT_ARTIFACT_ID": "RAW-DO-ITEM"}, Outra())
        self.assertEqual(u["artifact_type"], art.DERIVED)
        self.assertEqual(u["parent_artifact_id"], "RAW-DO-ITEM")


class ARotaCanonicaProvadaACorrer(Bancada):
    """M6 e M7 sobreviveram porque nenhuma trava CORRIA a rota.

    Ler o código prova que a linha existe. Só correr prova que ela manda.
    """

    def setUp(self):
        super().setUp()
        import orquestrador as orq
        self.orq = orq
        # O livro de decisoes e versionado: `pela_porta` escreve nele.
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

    def test_pela_entrada_entrega_a_unidade_e_nao_so_a_contagem(self):
        r = self.orq.pela_entrada([self.unidade()], dict(CORRIDA))
        self.assertEqual(r["PRESERVADOS"], 1)
        self.assertEqual(len(r["PARA_A_PORTA"]), 1,
                         "a fronteira contou e nao entregou")
        self.assertEqual(r["PARA_A_PORTA"][0].get("artifact_type"), art.RAW)

    def test_a_rota_julga_a_unidade_da_fronteira_e_nao_o_item_original(self):
        entrada = self.orq.pela_entrada([self.unidade()], dict(CORRIDA))
        r = self.orq.pela_porta(entrada["PARA_A_PORTA"], "T2", CORRIDA["RUN_ID"])
        self.assertEqual(r["itens"], 1)
        # com estagio preservado, a porta NAO cobra o tempo do FATO
        self.assertNotIn(adm.NAO_SEI, r["por_resultado"],
                         "a porta voltou a cobrar o tempo do fato: %s"
                         % r["por_resultado"])

    def test_o_item_original_sem_estagio_reprova_por_tempo(self):
        """O contraponto: sem a fronteira, a mesma unidade cai no degrau errado."""
        r = self.orq.pela_porta([self.unidade()], "T2", CORRIDA["RUN_ID"])
        self.assertIn(adm.NAO_SEI, r["por_resultado"])


class ACorridaInteiraProvadaACorrer(unittest.TestCase):
    """M6 sobreviveu a tudo o resto: ninguém corria `correr()`.

    `pela_entrada` e `pela_porta` provados em separado não provam que a rota os
    liga na ordem certa. Só `correr()` prova isso, e é por isso que esta trava
    monta um livro de corrida temporário e corre a rota inteira, sem rede.

        PROVAR AS PECAS EM SEPARADO NAO PROVA A MONTAGEM.
    """

    def setUp(self):
        import json
        import tempfile
        import admissao
        import italy_executor as adapter
        import orquestrador as orq
        from pedido import de_uma_frase
        self.orq, self.adapter, self.frase = orq, adapter, de_uma_frase
        self.pay = _payload()
        if not self.pay:
            self.skipTest("sem byte real no armazem")

        self.ops = tempfile.mkdtemp(prefix=".corrida-v2-",
                                    dir=os.path.join(RAIZ, "data"))
        self.addCleanup(shutil.rmtree, self.ops, True)
        antes = os.environ.get("ITALY_OPS_ROOT")
        os.environ["ITALY_OPS_ROOT"] = self.ops
        self.addCleanup(lambda: os.environ.__setitem__("ITALY_OPS_ROOT", antes)
                        if antes else os.environ.pop("ITALY_OPS_ROOT", None))
        self.addCleanup(shutil.rmtree, os.path.join(RAIZ, adapter.BALCAO), True)
        self.addCleanup(shutil.rmtree, os.path.join(RAIZ, "XX"), True)

        self.livro = admissao.LIVRO
        try:
            with open(self.livro, encoding="utf-8") as f:
                conteudo = f.read()
        except OSError:
            conteudo = None
        self.addCleanup(self._repor, conteudo)

        self.run_id = "CORRIDA-V2-0001"
        caminho = os.path.join(self.ops, adapter.LIVRO)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "RUN_ID": self.run_id, "SOURCE_ID": "IT-T2-002",
                "DOCUMENT_ID": "ARPAV_CORRIDA", "RAW_PATH": self.pay,
                "CAPTURED_AT": "2026-09-11T00:00:00Z",
                "texto": "Bollettino agrometeorologico con dati di campo."}) + "\n")
        adapter.colher(self.run_id, ops_root=self.ops)

    def _repor(self, conteudo):
        if conteudo is None:
            if os.path.exists(self.livro):
                os.remove(self.livro)
        else:
            with open(self.livro, "w", encoding="utf-8") as f:
                f.write(conteudo)

    def test_correr_julga_a_unidade_da_fronteira(self):
        recibo = self.orq.correr(self.frase("colete clima e tempo"),
                                 so_a_porta=True)
        self.assertEqual(recibo["INGRESSO"]["PRESERVADOS"], 1, recibo["INGRESSO"])
        a = recibo["ADMISSAO"]
        self.assertEqual(a["itens"], 1)
        self.assertNotIn(
            adm.NAO_SEI, a["por_resultado"],
            "a corrida inteira voltou a julgar o item sem estagio: %s"
            % a["por_resultado"])
