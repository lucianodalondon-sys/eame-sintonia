# -*- coding: utf-8 -*-
"""PROVAS DO ARMAZÉM ITALIANO — bytes guardados não são procedência.

O QUE ESTES TESTES GUARDAM
--------------------------
Não os 195 de hoje. **As propriedades.** A pior coisa que pode acontecer a este
achado é alguém, daqui a três meses, olhar para «195 objetos preservados» e
concluir que o caminho italiano está saudável.

    UM ARMAZÉM CHEIO COM O LIVRO DE ENTRADA EM BRANCO
    PARECE SAÚDE E É O CONTRÁRIO.

E há um segundo erro, mais silencioso: transformar a leitura do coordenador em
observação nossa. Esta sessão não tem credencial do banco. Se um dia o mapa
disser `OBSERVED` sobre um número que ninguém aqui mediu, estes testes reprovam.
"""
import json
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GERADO = os.path.join(RAIZ, "system-map", "data", "armazem-it.generated.json")
ESTADO = os.path.join(RAIZ, "system-map", "data", "state.generated.json")
GERADOR = os.path.join(RAIZ, "system-map", "scripts", "generate_system_map.py")
MEDICAO = os.path.join(RAIZ, "data", "samples", "SUPABASE-LIVE-MEDICAO-EXTERNA.json")


def _json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _texto(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read()


class BytesNaoSaoProcedencia(unittest.TestCase):
    """1 a 4 — as espécies não se confundem no armazém, tal como no disco."""

    @classmethod
    def setUpClass(cls):
        cls.A = _json(GERADO)
        cls.L = cls.A["LACUNA_DO_ARMAZEM"]

    def test_1_objeto_no_storage_nao_implica_raw_asset(self):
        """A propriedade central, medida: há objetos e não há linhas.

        Se um dia houver linhas, este teste continua a valer — ele exige que a
        lacuna seja CALCULADA, não que ela exista para sempre.
        """
        objetos = self.L["ITALY_STORAGE_OBJETOS"]
        linhas = self.L["ITALY_RAW_ASSET_LINHAS"]
        self.assertIsInstance(objetos, int)
        self.assertIsInstance(linhas, int)
        self.assertEqual(self.L["OBJETOS_SEM_DONO_DECLARADO"], objetos - linhas)

    def test_2_raw_asset_vazio_nao_implica_corrida_inexistente(self):
        """São duas ausências separadas, e são contadas separadas.

        Colapsá-las num «a Itália não está lá» foi exatamente o erro que este
        censo veio corrigir.
        """
        self.assertIn("ITALY_RAW_ASSET_LINHAS", self.L)
        self.assertIn("ITALY_COLLECTION_RUN_LINHAS", self.L)

    def test_3_prefixo_IT_nao_prova_corrida_italiana(self):
        """O nome da chave não é procedência. `IT/` diz onde o objeto está, não
        quem o pôs lá — e a chave italiana nem sequer carrega a corrida."""
        self.assertEqual(self.L["RUN_HISTORICA"].split(" ")[0], "RUN_NOT_PROVABLE")

    def test_4_recuperavel_nao_autoriza_inventar(self):
        """O documento sabe de onde veio; a corrida não existiu.

        Sem esta trava escrita, «a procedência é recuperável» viraria licença
        para inserir uma corrida histórica que ninguém viveu.
        """
        self.assertIn("NAO_RETROCRIAR", self.L)
        self.assertIn("INVENTADA", self.L["NAO_RETROCRIAR"].upper())


class OQueEsteBancoNaoViu(unittest.TestCase):
    """5 a 7 — medição externa não vira observação nossa."""

    def test_5_a_medicao_diz_quem_a_fez(self):
        m = _json(MEDICAO)
        self.assertEqual(m["SCHEMA"], "EXTERNAL_LIVE_MEASUREMENT/1")
        self.assertEqual(m["MODO"], "READ_ONLY")
        self.assertEqual(m["ESCRITAS"], 0)
        self.assertTrue(m["MEDIDO_POR"])

    def test_6_o_censo_carrega_o_estado_da_medicao(self):
        L = _json(GERADO)["LACUNA_DO_ARMAZEM"]
        self.assertEqual(L["ESTADO_DA_MEDICAO"], "EXTERNAL_LIVE_MEASUREMENT")
        self.assertTrue(L["PORQUE_NAO_E_OBSERVED"])

    def test_7_o_mapa_nunca_chama_isto_de_observed(self):
        """Se o cartão do armazém passar a dizer OBSERVED, o mapa passa a
        afirmar que esta casa foi ao banco e viu. Não foi."""
        estado = _texto(ESTADO)
        i = estado.find("C-ARMAZEM-IT-SEM-LIVRO")
        self.assertGreater(i, -1, "o cartao do armazem sumiu do mapa")
        cartao = estado[i:i + 6000]
        self.assertIn("EXTERNAL_LIVE_MEASUREMENT", cartao)
        self.assertNotIn('"proof": "observed"', cartao)


class OArmazemOrfaoNaoSeEsconde(unittest.TestCase):
    """8 a 10 — a lacuna aparece, e não aparece pintada de saúde."""

    def test_8_o_cartao_existe_e_nao_e_verde(self):
        """Nenhum caminho pode levar este cartão a verde enquanto houver objeto
        sem linha que o reclame."""
        d = _json(ESTADO)
        no = [n for n in d["NODES"] if n["id"] == "C-ARMAZEM-IT-SEM-LIVRO"]
        self.assertEqual(len(no), 1)
        self.assertNotEqual(no[0]["status"], "PROVEN")
        self.assertNotEqual(no[0]["ui_status"], "green")

    def test_9_o_cartao_mostra_as_tres_ausencias(self):
        d = _json(ESTADO)
        no = [n for n in d["NODES"] if n["id"] == "C-ARMAZEM-IT-SEM-LIVRO"][0]
        junto = " ".join(no["facts"])
        for exigido in ("STORAGE IT", "RAW_ASSET IT", "COLLECTION_RUN IT", "G-42"):
            self.assertIn(exigido, junto)

    def test_10_a_divergencia_de_contagem_nao_e_arredondada(self):
        """Três números diferentes ficam os três escritos, com a causa de cada
        diferença ao lado.

        ASSERÇÃO ANTIGA: exigia `ESTADO == NAO_RECONCILIADO`. Ficou velha no dia
        em que a conta fechou — e um teste que exige que um problema continue
        aberto impede quem o resolve. O que se guarda agora é a propriedade que
        dura: **as três contagens continuam visíveis, e a conta é explicada, não
        arredondada.**
        """
        t = _json(GERADO)["LACUNA_DO_ARMAZEM"]["TRES_CONTAGENS"]
        valores = [t["DOCUMENTOS_NO_MANIFESTO"], t["CONTEUDOS_UNICOS_NO_MANIFESTO"],
                   t["OBJETOS_DOCUMENT_NO_ARMAZEM"]]
        self.assertTrue(all(isinstance(v, int) for v in valores))
        if len(set(valores)) > 1:
            self.assertTrue(t["COMO_SE_EXPLICAM"],
                            "contagens que divergem exigem explicacao escrita")

    def test_10b_a_conta_fecha_por_causa_e_nao_por_coincidencia(self):
        """A soma tem de vir das URLs de cada grupo, não de um número escrito.

        Se alguém trocar a regra por «os objetos são os conteúdos + 1», este
        teste continua verde por acaso hoje e reprova no primeiro dia em que
        houver dois duplicados. Por isso ele recalcula grupo a grupo.
        """
        C = _json(GERADO)["A_CONTA_FECHA"]
        self.assertEqual(C["FORCA_DA_PROVA"], "PREFIX_MATCH")
        self.assertIn("nao e identidade", C["PORQUE_NAO_E_FULL_SHA256_MATCH"]
                      .replace("é", "e").replace("ã", "a").lower()
                      .replace("endereco, nao identidade", "nao e identidade"))
        extra = sum(g["OBJETOS_PREVISTOS"] - 1 for g in C["GRUPOS_REPETIDOS"])
        self.assertEqual(C["OBJETOS_PREVISTOS_PELO_MANIFESTO"],
                         C["CONTEUDOS_UNICOS"] + extra)
        if C["OBJETOS_MEDIDOS_NO_ARMAZEM"] is not None:
            self.assertEqual(C["OBJETOS_PREVISTOS_PELO_MANIFESTO"],
                             C["OBJETOS_MEDIDOS_NO_ARMAZEM"])

    def test_10c_a_divida_historica_nao_recebe_corrida_inventada(self):
        """`RUN_NOT_PROVABLE` fica `RUN_NOT_PROVABLE`. Nenhum nome de corrida de
        mentira pode entrar no repositório para tapar o buraco dos 195."""
        L = _json(GERADO)["LACUNA_DO_ARMAZEM"]
        self.assertTrue(L["RUN_HISTORICA"].startswith("RUN_NOT_PROVABLE"))
        for nome in ("LEGACY-IT", "UNKNOWN-RUN", "BACKFILL-RUN", "MIGRATION-RUN"):
            self.assertNotIn(nome, _texto(GERADO))


class DoisAcervosNaoSeSomam(unittest.TestCase):
    """11 e 12 — a interseção é medida, nunca inferida pelo nome."""

    def test_11_a_comparacao_e_por_impressao_digital(self):
        D = _json(GERADO)["DOIS_ACERVOS"]
        self.assertEqual(
            D["JA_NO_ARMAZEM"] + D["FORA_DO_ARMAZEM"], D["GOLDEN_PATH_CONTEUDOS"])
        self.assertEqual(D["DESCONHECIDO"], 0)
        self.assertTrue(D["RESSALVA"])

    def test_12_o_mesmo_conteudo_pode_viver_em_caminhos_distintos(self):
        """A conclusão da missão anterior continua de pé: `sha256` não é
        `UNIQUE` em `raw_asset`, e por isso duas capturas do mesmo byte cabem."""
        sql = _texto(os.path.join(RAIZ, "supabase", "migrations",
                                  "001_fundacao_geografia_e_proveniencia.sql"))
        self.assertIn("create index raw_hash_idx", sql)
        self.assertNotIn("unique (sha256)", sql.lower())


class NadaFoiEscrito(unittest.TestCase):
    """13 a 15 — a missão termina antes da primeira escrita italiana."""

    def test_13_derived_artifact_existe_mas_nao_chegou_a_producao(self):
        """ASSERÇÃO ANTIGA: exigia que a `022` não existisse.

        Ficou velha quando a missão seguinte a escreveu e a provou num Postgres
        descartável — e era a asserção errada desde o início: guardava o escopo
        daquela missão, não uma propriedade do sistema.

        O QUE SE GUARDA AGORA: escrever uma migration **não pode aplicá-la**. O
        workflow que toca em produção corre só à mão, e nunca por causa de um
        ficheiro novo em `supabase/migrations/`.
        """
        gatilho = _texto(os.path.join(RAIZ, ".github", "workflows",
                                      "supabase-migrate.yml"))
        cabeca = gatilho[gatilho.index("on:"):gatilho.index("permissions:")]
        self.assertIn("workflow_dispatch:", cabeca)
        self.assertNotIn("supabase/migrations/", cabeca,
                         "migration nova passaria a aplicar-se sozinha")

    def test_14_nenhum_importador_italiano_do_bruto_foi_criado(self):
        """A missão MEDIU que ele não existe. Medir não é construir."""
        pasta = os.path.join(RAIZ, "supabase", "importacoes")
        for nome in os.listdir(pasta):
            if nome.startswith("IT-"):
                sql = _texto(os.path.join(pasta, nome))
                self.assertNotIn("raw_asset", sql)
                self.assertNotIn("collection_run", sql)

    def test_15_o_censo_nao_tem_como_escrever_no_banco(self):
        """Nem por engano: o censo do armazém não importa cliente nenhum, não
        abre ligação e não conhece verbo de escrita."""
        fonte = _texto(os.path.join(RAIZ, "system-map", "scripts",
                                    "censo_do_armazem_it.py"))
        # A palavra «Supabase» aparece na prosa deste ficheiro, e tem de
        # aparecer — ele explica o Supabase. O que nao pode existir e MAO: uma
        # biblioteca de cliente, uma ligacao, ou um verbo de escrita.
        for verbo in ("insert into", "update set", "delete from", "psycopg",
                      "import requests", "urlopen", "create_client", "subprocess"):
            self.assertNotIn(verbo, fonte.lower(),
                             "o censo devia ser READ-ONLY e cego para o banco")
        # e nao ha `import` de nada que fale rede
        for linha in fonte.splitlines():
            if linha.startswith(("import ", "from ")):
                self.assertNotIn("http", linha.lower())
                self.assertNotIn("socket", linha.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
