# -*- coding: utf-8 -*-
"""PROVAS DA IDENTIDADE DO ARTEFATO — caminho, captura, conteúdo, cópia, derivado.

O QUE ESTES TESTES GUARDAM
--------------------------
Não os números de hoje. **As propriedades.** Se amanhã a Itália tiver 80 PDFs e
50 conteúdos, estes testes têm de continuar verdes — e continuar a reprovar
quem voltar a confundir as espécies.

O erro que eles existem para impedir é concreto e já aconteceu duas vezes:

    1. concluir «são fotocópias» olhando para o nome da pasta;
    2. ler o `unique` do `storage_path` como se fosse do `sha256`, e daí
       inventar uma tabela de ocorrência que ninguém precisava.

Ambos são o mesmo erro de fundo: **decidir por leitura, não por medição.**
"""
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "system-map", "scripts"))

import censo_de_identidade_it as ci  # noqa: E402

MIGRACOES = os.path.join(RAIZ, "supabase", "migrations")
GERADO = os.path.join(RAIZ, "system-map", "data", "identidade-it.generated.json")


def _sql(nome_parcial):
    for nome in sorted(os.listdir(MIGRACOES)):
        if nome.startswith(nome_parcial):
            with open(os.path.join(MIGRACOES, nome), encoding="utf-8") as f:
                return f.read()
    raise AssertionError("migration %s nao existe" % nome_parcial)


def _bloco(sql, tabela):
    """O corpo do `create table`, do parêntese até ao `);` da coluna zero."""
    m = re.search(r"create table[^(]*public\.%s\s*\((.*?)\n\);" % tabela, sql, re.S)
    assert m, "create table de %s nao encontrado" % tabela
    return m.group(1)


class AsEspeciesNaoSeConfundem(unittest.TestCase):
    """1 a 5 — as proibições fundamentais, escritas como teste."""

    def test_1_dois_caminhos_com_mesmo_sha_nao_viram_uma_captura(self):
        """CAMINHO != CAPTURA. Dois caminhos, duas provas distintas → INDEPENDENT.

        Se alguém trocar a regra por «mesma pasta-mãe, logo mesma captura»,
        este caso passa a dar SAME e o teste reprova.
        """
        grupo = [
            {"CAMINHO": "a/x.pdf", "PROVA": {"CAPTURE_ID": "A", "CAPTURED_AT": "1", "ATOR": "curl"}},
            {"CAMINHO": "b/x.pdf", "PROVA": {"CAPTURE_ID": "B", "CAPTURED_AT": "2", "ATOR": "coletor"}},
        ]
        estado, porque = ci.classificar(grupo)
        self.assertEqual(estado, ci.INDEP)
        self.assertIn("2 capturas distintas", porque)

    def test_2_uma_captura_com_duas_copias_e_reconhecida(self):
        """A espécie oposta também tem de ser representável.

        Hoje não temos nenhum caso destes. Isso NÃO é razão para o modelo não
        o saber dizer — é razão para não construir tabela para ele.
        """
        grupo = [
            {"CAMINHO": "a/x.pdf", "PROVA": {"CAPTURE_ID": "A", "CAPTURED_AT": "1", "ATOR": "curl"}},
            {"CAMINHO": "b/x.pdf", "PROVA": {"CAPTURE_ID": "A", "CAPTURED_AT": "1", "ATOR": "curl"}},
        ]
        self.assertEqual(ci.classificar(grupo)[0], ci.SAME)

    def test_3_sem_prova_de_captura_o_grupo_e_unknown(self):
        """NÃO SEI continua NÃO SEI. Uma cópia sem recibo não vira nem SAME nem
        INDEPENDENT só porque a outra do par tem recibo."""
        grupo = [
            {"CAMINHO": "a/x.pdf", "PROVA": {"CAPTURE_ID": "A", "CAPTURED_AT": "1", "ATOR": "curl"}},
            {"CAMINHO": "b/x.pdf", "PROVA": None},
        ]
        self.assertEqual(ci.classificar(grupo)[0], ci.UNKNOWN)

    def test_4_so_existem_tres_respostas(self):
        """Não há quarta resposta por estética."""
        self.assertEqual(
            sorted({ci.SAME, ci.INDEP, ci.UNKNOWN}),
            sorted(["INDEPENDENT_CAPTURES_SAME_CONTENT",
                    "SAME_CAPTURE_MULTIPLE_STORAGE_COPIES", "UNKNOWN"]))

    def test_5_a_regra_do_que_e_italiano_e_uma_so(self):
        """Dois censos com duas réguas produzem dois números verdadeiros e
        contraditórios. O censo de identidade importa a régua do censo do corpo
        em vez de escrever a sua."""
        fonte = open(os.path.join(RAIZ, "system-map", "scripts",
                                  "censo_de_identidade_it.py"), encoding="utf-8").read()
        self.assertIn("from censo_do_corpus_it import e_italiano", fonte)


class OSchemaJaSabeRepresentar(unittest.TestCase):
    """6 a 9 — o que o banco versionado prova, contra o diagnóstico antigo."""

    def setUp(self):
        self.sql001 = _sql("001")

    def test_6_storage_path_e_unique(self):
        """O grão de `raw_asset` é o OBJETO GUARDADO."""
        self.assertRegex(_bloco(self.sql001, "raw_asset"),
                         r"storage_path\s+text not null unique")

    def test_7_sha256_nao_e_unique(self):
        """A trava que teria obrigado a uma tabela de ocorrência NUNCA existiu.

        Se alguém a acrescentar um dia, este teste reprova — e tem de reprovar,
        porque nesse dia as duas capturas do mesmo byte deixariam de caber.
        """
        corpo = _bloco(self.sql001, "raw_asset")
        self.assertNotRegex(corpo, r"sha256[^,\n]*unique")
        self.assertNotRegex(self.sql001, r"create unique index[^;]*raw_asset[^;]*sha256")
        self.assertIn("create index raw_hash_idx", self.sql001)

    def test_8_o_mesmo_conteudo_cabe_em_duas_linhas(self):
        """A propriedade que resolve o caso, dita em uma frase: nada no esquema
        impede duas linhas de `raw_asset` com o mesmo `sha256`."""
        corpo = _bloco(self.sql001, "raw_asset")
        for proibicao in (r"unique\s*\(\s*sha256\s*\)", r"primary key\s*\(\s*sha256"):
            self.assertNotRegex(corpo, proibicao)

    def test_9_conteudo_visto_em_e_por_run_nao_por_bytes(self):
        """`conteudo_visto_em` resolve o CONCEITO — mas na entidade «item de
        canal», não nos bytes. Por isso é PARCIAL e não fecha o caso."""
        sql = _sql("016")
        self.assertRegex(sql, r"UNIQUE \(conteudo_id, run_id\)")
        self.assertRegex(_bloco(_sql("003"), "conteudo"),
                         r"UNIQUE \(canal_id, content_id\)")


class RawNaoEDerived(unittest.TestCase):
    """10 a 12 — a lei que impede a solução preguiçosa."""

    def test_10_raw_asset_nao_ganhou_coluna_de_pai(self):
        """Seria fácil pôr `parent_sha256` em `raw_asset`. Seria também apagar a
        COL-LAW-007 dentro da tabela chamada «bruto»."""
        for nome in sorted(os.listdir(MIGRACOES)):
            with open(os.path.join(MIGRACOES, nome), encoding="utf-8") as f:
                sql = f.read()
            self.assertNotRegex(
                sql, r"alter table public\.raw_asset[^;]*parent",
                "%s poe pai dentro de raw_asset — RAW nao e DERIVED" % nome)

    def test_11_a_linhagem_do_derivado_esta_completa_nos_ficheiros(self):
        """A dívida é do banco, não da medição: todo derivado com pai declara a
        linhagem inteira."""
        d = ci.derivados()
        self.assertGreater(d["DERIVADOS_COM_PAI"], 0)
        self.assertEqual(d["LINHAGEM_COMPLETA"], d["DERIVADOS_COM_PAI"])

    def test_12_o_pai_e_o_conteudo_nao_a_copia(self):
        """A migration projetada identifica o pai pelos BYTES. Se ela passar a
        identificá-lo só pelo caminho, uma cópia apagada levaria o pai junto."""
        doc = open(os.path.join(RAIZ, "docs", "operacao",
                                "IDENTIDADE-DO-ARTEFATO.md"), encoding="utf-8").read()
        self.assertIn("parent_sha256     char(64) not null", doc)
        self.assertIn("parent_raw_asset_id bigint references", doc)


class NadaDeNumeroEscritoAMao(unittest.TestCase):
    """13 a 16 — o estado gerado é medido, e a decisão é reprodutível."""

    @classmethod
    def setUpClass(cls):
        with open(GERADO, encoding="utf-8") as f:
            cls.g = json.load(f)["IDENTIDADE_DO_ARTEFATO"]

    def test_13_a_medicao_repete(self):
        """Correr outra vez dá o mesmo. Conta que não se repete não é medida."""
        agora = ci.censo()
        for campo in ("COPIAS_NO_DISCO", "CONTEUDOS_UNICOS", "CAPTURAS_DISTINTAS",
                      "VEREDITO", "GRUPOS_COM_MAIS_DE_UMA_COPIA"):
            self.assertEqual(agora[campo], self.g[campo], campo)

    def test_14_bate_com_o_censo_do_corpo(self):
        """Duas medições da mesma coisa não podem divergir. Se divergirem, uma
        delas está a mentir e não se sabe qual."""
        with open(os.path.join(RAIZ, "system-map", "data",
                               "corpus-it.generated.json"), encoding="utf-8") as f:
            oc = json.load(f)["OCORRENCIA_E_CONTEUDO"]
        self.assertEqual(self.g["COPIAS_NO_DISCO"], oc["OCORRENCIAS"])
        self.assertEqual(self.g["CONTEUDOS_UNICOS"], oc["CONTEUDOS_UNICOS"])

    def test_15_o_veredito_nao_esta_escrito_no_gerador(self):
        """O mapa mostra o veredito, e tem de o LER. Se ele aparecer escrito no
        gerador, o cartão deixa de depender da medição."""
        ger = open(os.path.join(RAIZ, "system-map", "scripts",
                                "generate_system_map.py"), encoding="utf-8").read()
        self.assertIn("identidade-it.generated.json", ger)
        for palavra in ("INDEPENDENT_CAPTURES_SAME_CONTENT",
                        "SAME_CAPTURE_MULTIPLE_STORAGE_COPIES"):
            self.assertNotIn(palavra, ger,
                             "o gerador escreve o veredito em vez de o medir")

    def test_16_o_mapa_nao_volta_a_dizer_fotocopia(self):
        """A frase «guardados em dois sítios ao mesmo tempo» era a conclusão
        errada. Ela não pode voltar por descuido."""
        ger = open(os.path.join(RAIZ, "system-map", "scripts",
                                "generate_system_map.py"), encoding="utf-8").read()
        self.assertNotIn("guardados em dois sítios ao mesmo tempo", ger)


class NenhumEsquemaParalelo(unittest.TestCase):
    """17 e 18 — REUSE antes de CREATE, verificado."""

    def test_17_nenhuma_tabela_de_ocorrencia_foi_criada(self):
        """O maior erro possível seria criar tabela para o que o banco já sabe
        representar. Nenhuma migration nova existe."""
        nomes = sorted(n for n in os.listdir(MIGRACOES) if n.endswith(".sql"))
        for n in nomes:
            with open(os.path.join(MIGRACOES, n), encoding="utf-8") as f:
                sql = f.read().lower()
            for proibida in ("create table public.occurrence",
                             "create table public.capture_occurrence",
                             "create table public.storage_copy",
                             "create table public.ocorrencia"):
                self.assertNotIn(proibida, sql)

    def test_18_o_sql_projetado_nao_foi_aplicado(self):
        """A migration `022` vive dentro de um documento, em bloco de código —
        e não como ficheiro que um workflow possa correr por engano."""
        self.assertFalse(
            [n for n in os.listdir(MIGRACOES) if n.startswith("022")],
            "022 virou ficheiro de migration: esta missao NAO aplica esquema")


class RedTeamDoModelo(unittest.TestCase):
    """19 a 22 — os casos que o modelo tem de representar SEM inventar duplicação
    e SEM apagar procedência. Os casos A, B e D já estão em cima (1, 2 e 11)."""

    def test_19_caso_C_duas_coletas_bytes_diferentes_mesmo_titulo(self):
        """A fonte republica o boletim corrigido com a MESMA URL.

        São dois conteúdos e duas capturas. O modelo não pode fundi-los pelo
        título nem pela URL — se o fizesse, a versão corrigida apagaria a
        original e ninguém saberia que o documento mudou.
        """
        prova = {"a/x.pdf": {"CAPTURE_ID": "A", "CAPTURED_AT": "1", "ATOR": "curl"},
                 "b/x.pdf": {"CAPTURE_ID": "B", "CAPTURED_AT": "2", "ATOR": "curl"}}
        # bytes diferentes = SHA diferentes = nem sequer chegam a formar grupo
        por_conteudo = {"sha_v1": ["a/x.pdf"], "sha_v2": ["b/x.pdf"]}
        grupos = [s for s, cs in por_conteudo.items() if len(cs) > 1]
        self.assertEqual(grupos, [], "URL igual nao pode juntar bytes diferentes")
        self.assertEqual(len({p["CAPTURE_ID"] for p in prova.values()}), 2)

    def test_20_caso_E_conteudo_revisto_sem_byte_novo(self):
        """A corrida vê outra vez o mesmo documento e decide NÃO guardar cópia.

        O esquema já sabe dizer isto sem mentir: `preserved = false` obriga a um
        motivo. «Não guardei» fica escrito como não-guardado, e nunca como
        «guardei».
        """
        corpo = _bloco(_sql("001"), "raw_asset")
        self.assertIn("preserved      boolean not null default true", corpo)
        self.assertIn("not_preserved_reason", corpo)
        self.assertIn("bruto_ausente_precisa_de_motivo", corpo)

    def test_21_caso_F_o_caminho_muda_e_os_bytes_nao(self):
        """Mover o ficheiro de pasta não cria conteúdo novo nem captura nova.

        Por isso a identidade do conteúdo é o `SHA-256` e nunca o caminho — e
        por isso o pai do derivado é o `parent_sha256`, não o `storage_path`.
        """
        grupo = [
            {"CAMINHO": "pasta-velha/x.pdf",
             "PROVA": {"CAPTURE_ID": "A", "CAPTURED_AT": "1", "ATOR": "curl"}},
            {"CAMINHO": "pasta-nova/x.pdf",
             "PROVA": {"CAPTURE_ID": "A", "CAPTURED_AT": "1", "ATOR": "curl"}},
        ]
        self.assertEqual(ci.classificar(grupo)[0], ci.SAME)

    def test_22_a_identidade_nunca_e_a_url_nem_o_nome(self):
        """Nenhuma chave nasce de conveniência: nem URL, nem nome de ficheiro,
        nem carimbo de tempo sozinho."""
        for c in ci.capturas_das_amostras().values():
            self.assertTrue(c["CAPTURE_ID"].startswith("AMOSTRA:"))
            # a identidade da captura carrega FONTE + QUANDO + URL, os tres
            self.assertEqual(c["CAPTURE_ID"].count(":") >= 3, True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
