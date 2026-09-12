#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS GUARDAS DA MEDIÇÃO DA LINHAGEM — ela mede, e não implementa.

A medição de valor vive em `provas/a_linhagem_do_reaproveitamento.py`, contra
PostgreSQL descartável e a rota real. Aqui ficam as guardas que não precisam
de banco:

    · a busca da relação é pelo CATÁLOGO, e não pela minha memória;
    · a prova não confunde «mesmos bytes» com «participou da execução»;
    · esta missão RECOMENDA e não implementa.
"""
import ast
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "coleta")):
    if p not in sys.path:
        sys.path.insert(0, p)
import _gavetas                      # noqa: E402,F401

PROVA = os.path.join(RAIZ, "provas", "a_linhagem_do_reaproveitamento.py")
ADR = os.path.join(RAIZ, "docs", "decisoes",
                   "ADR-LINHAGEM-DO-REAPROVEITAMENTO-V1.md")


def _fonte(caminho):
    with io.open(caminho, encoding="utf-8") as f:
        return f.read()


def _casos(caminho):
    """As chamadas a `caso(...)`, lidas por AST."""
    fora = []
    for no in ast.walk(ast.parse(_fonte(caminho))):
        if (isinstance(no, ast.Call)
                and getattr(no.func, "id", None) == "caso" and no.args):
            fora.append(no)
    return fora


class ABuscaEPeloCatalogoENaoPelaMemoria(unittest.TestCase):
    """⚠️ RT · «não existe owner» dito depois de olhar para três tabelas.

    Uma resposta dessas mede a memória de quem procurou, e não o esquema. Quem
    sabe que colunas apontam para cada tabela é o catálogo do Postgres.

        UM CENSO ESTÁ CERTO DENTRO DO UNIVERSO QUE DECLARA.
    """

    def test_a_prova_pergunta_ao_pg_constraint(self):
        s = _fonte(PROVA)
        self.assertIn("pg_constraint", s)
        self.assertIn("confrelid", s)
        for alvo in ("public.raw_asset", "public.derived_artifact"):
            self.assertIn(alvo, s)

    def test_e_nao_traz_uma_lista_de_tabelas_escrita_a_mao(self):
        """Uma lista fixa de candidatas envelhece no dia em que alguém
        acrescentar uma tabela — e a medição diria «nenhuma» sem ter olhado."""
        arvore = ast.parse(_fonte(PROVA))
        for no in ast.walk(arvore):
            if not (isinstance(no, ast.FunctionDef)
                    and no.name == "tabelas_que_ligam_os_dois"):
                continue
            nomes = [n.value for n in ast.walk(no)
                     if isinstance(n, ast.Constant) and isinstance(n.value, str)]
            self.assertNotIn("derivacao_observacao", nomes)
            self.assertNotIn("etapa_da_corrida", nomes)
            return
        self.fail("a funcao que decide as pontes desapareceu")

    def test_a_ponte_exige_os_DOIS_lados(self):
        """Uma tabela que aponta só para `raw_asset` sabe de observações. Só
        quem aponta para os dois pode dizer que ESTA usou AQUELE."""
        s = _fonte(PROVA)
        self.assertIn('{"raw_asset", "derived_artifact"}', s)


class SHANaoEProvaDeParticipacao(unittest.TestCase):
    """CAN INFER != OBSERVED EDGE."""

    def test_o_veredito_NAO_sai_da_consulta_por_sha(self):
        """O veredito tem de vir das pontes encontradas no catálogo. Se saísse
        da consulta das irmãs, ele diria ALREADY_PROVEN sobre uma inferência."""
        arvore = ast.parse(_fonte(PROVA))
        alvo = [n for n in ast.walk(arvore)
                if isinstance(n, ast.Assign)
                and any(getattr(t, "id", None) == "persistido" for t in n.targets)]
        self.assertEqual(len(alvo), 1, "quem decide o veredito mudou de sitio")
        self.assertIn("achou_b", ast.dump(alvo[0].value))
        self.assertNotIn("irmas", ast.dump(alvo[0].value))

    def test_o_caso_das_irmas_esta_declarado_como_NAO_participacao(self):
        """O nome do caso é o contrato dele. Chamar-lhe «o SHA prova» seria
        ensinar a inferência como se fosse aresta.

        ⚠️ E LÊ-SE POR AST, e não por `assertIn` sobre o ficheiro: uma guarda
        de texto passa a morder o parágrafo que explica a regra, e já mordeu
        duas vezes nesta linha de missões.
        """
        nomes = [n.args[0].value for n in _casos(PROVA)
                 if isinstance(n.args[0], ast.Constant)]
        irmas = [n for n in nomes if "SHA" in n]
        self.assertEqual(len(irmas), 1, "o caso das irmas mudou de forma")
        self.assertIn("nao_diz_quem_PARTICIPOU", irmas[0])


class NenhumCasoSeAutoAprova(unittest.TestCase):
    """⚠️ MEDIDO DUAS VEZES NESTA LINHA DE MISSÕES: um caso cuja condição é uma
    constante verdadeira passa sempre, e sobrevive a qualquer mutante."""

    def test_nenhuma_condicao_e_uma_constante_verdadeira(self):
        for no in _casos(PROVA):
            if len(no.args) < 2:
                continue
            cond = no.args[1]
            if isinstance(cond, ast.Constant) and cond.value:
                self.fail("caso auto-aprovado: %s" % no.args[0].value)

    def test_ha_casos_para_conferir(self):
        self.assertGreaterEqual(len(_casos(PROVA)), 8)


class EstaMissaoNaoImplementa(unittest.TestCase):
    """MEDIR != CONSERTAR. DECIDIR != IMPLEMENTAR."""

    def test_nenhuma_migration_nova_entrou(self):
        pasta = os.path.join(RAIZ, "supabase", "migrations")
        numeros = sorted(f.split("_", 1)[0] for f in os.listdir(pasta)
                         if f.endswith(".sql"))
        self.assertEqual(numeros[-1], "028",
                         "esta missao acrescentou migration, e era de decidir")

    def test_a_ADR_declara_que_nao_foi_implementada(self):
        """⚠️ ISTO EXIGIA A PALAVRA `RECOMENDADO`, E ELA MUDOU COM RAZÃO.

        A ADR passou de «recomendado» a «decidido» quando
        `C-DECIDE-DERIVED-PARTICIPATION-GRAIN-V1` fechou o conceito e a
        identidade. A guarda reprovou — e o que ela protege não é a palavra
        que mudou: é a que **não pode** mudar enquanto não houver migration.

            UMA GUARDA QUE PRENDE O ESTADO ERRADO
            REPROVA O PROGRESSO E DEIXA PASSAR O DEFEITO.
        """
        cabecalho = _fonte(ADR).split("---", 1)[0]
        self.assertIn("NÃO IMPLEMENTADO", cabecalho)
        self.assertNotIn("IMPLEMENTADO\n", cabecalho.replace(
            "NÃO IMPLEMENTADO", ""))

    def test_a_prova_nao_escreve_no_esquema(self):
        """Ela constrói estado pela rota real e por `derivacao_forward`. Não
        cria tabela, não altera coluna, não insere linhagem à mão."""
        s = _fonte(PROVA).lower()
        for proibido in ("create table", "alter table", "drop table",
                         "insert into public.derived_artifact",
                         "insert into public.raw_asset"):
            self.assertNotIn(proibido, s)


class ADecisaoDoGraoNaoSeContradiz(unittest.TestCase):
    """⚠️ A VERSÃO ANTERIOR DESTA ADR DIZIA DUAS COISAS SOBRE A MESMA CHAVE.

    O grão incluía «passagem» e a identidade incluía `run_id`; três parágrafos
    abaixo, a entrada do `run_id` na chave estava «em ABERTO». Duas respostas
    para a mesma pergunta, e por isso nenhuma valia.

        ESCOLHER A CHAVE ANTES DO CONCEITO
        É DECIDIR A FORMA ANTES DE SABER O QUE SE ESTÁ A GUARDAR.
    """

    def test_a_chave_natural_e_declarada_UMA_vez_e_sem_run(self):
        s = _fonte(ADR)
        self.assertIn(
            "MATERIAL_LINEAGE_NATURAL_KEY = (raw_asset_id, derived_artifact_id)",
            s)
        self.assertIn("RUN_ID_IN_MATERIAL_LINEAGE_KEY = NO", s)
        self.assertNotIn("(raw_asset_id, derived_artifact_id, run_id)", s)

    def test_cada_campo_da_decisao_tem_valor_fechado(self):
        """A missão do grão existe para fechar. Se um campo voltar a `UNKNOWN`
        ou a «em aberto», quem implementar tem de decidir outra vez.

        ⚠️ ISTO PROCURAVA A PALAVRA «em aberto» NO FICHEIRO INTEIRO, E MORDIA
        A NOTA QUE EXPLICA A CONTRADIÇÃO ANTIGA — ela tem de dizer que a
        pergunta *estava* em aberto para contar o que se corrigiu. É a
        terceira guarda de texto desta linha de missões a confundir a regra
        com o exemplo dela.

            UMA GUARDA LÊ O QUE A DECISÃO **DIZ**, E NÃO O FICHEIRO INTEIRO.

        Agora confere-se campo a campo, e cada um tem de trazer um valor do
        vocabulário fechado.
        """
        s = _fonte(ADR)
        fechados = {
            "PARTICIPATION_CONCEPT": ("TWO_DISTINCT_CONCEPTS",),
            "RUN_ID_IN_MATERIAL_LINEAGE_KEY": ("NO",),
            "ATTEMPT_IN_KEY": ("NOT_APPLICABLE",),
            "RUN_ID_AS_PROVENANCE": ("YES",),
            "INSERTED_REUSED_BELONGS_TO": ("EXECUTION_EVENT",),
        }
        for campo, aceites in fechados.items():
            achados = [l for l in s.splitlines() if l.strip().startswith(campo)]
            self.assertTrue(achados, "o campo %s saiu da ADR" % campo)
            for linha in achados:
                valor = linha.split("=", 1)[1].strip().split()[0]
                self.assertIn(valor, aceites,
                              "%s voltou a ficar sem resposta: %s"
                              % (campo, linha.strip()))

    def test_as_dez_perguntas_ficam_respondidas_num_sitio_so(self):
        bloco = _fonte(ADR)
        bloco = bloco[bloco.index("7.10"):]
        for pergunta in ("CONCEITO", "GRÃO", "IDENTIDADE", "RUN", "TENTATIVA",
                         "RESULTADO", "TEMPO", "RETRY", "REPROCESSO",
                         "DELETE", "BACKFILL", "MIGRATION"):
            self.assertIn(pergunta, bloco,
                          "7.10 deixou de responder %s" % pergunta)

    def test_o_resultado_e_o_tempo_nao_moram_na_aresta(self):
        s = _fonte(ADR)
        self.assertIn("INSERTED_REUSED_BELONGS_TO = EXECUTION_EVENT", s)
        self.assertIn("RUN_ID_AS_PROVENANCE = YES", s)


class OsQuatroCasosCorrem(unittest.TestCase):
    """A decisão do grão sai da medição, e não do argumento."""

    def test_a_prova_tem_os_quatro_casos(self):
        nomes = [n.args[0].value for n in _casos(PROVA)
                 if isinstance(n.args[0], ast.Constant)]
        for g in ("G2_retry", "G3_outra_observacao", "G4_rederivar",
                  "G5_as_duas_contagens", "G6_o_resultado_muda"):
            self.assertTrue(any(n.startswith(g) for n in nomes),
                            "caso em falta: %s" % g)

    def test_o_caso_que_separa_os_conceitos_compara_as_DUAS_contagens(self):
        """G5 é o que decide. Se ele deixasse de comparar arestas com eventos,
        a conclusão «são dois conceitos» ficaria sem prova."""
        for no in _casos(PROVA):
            if (isinstance(no.args[0], ast.Constant)
                    and no.args[0].value.startswith("G5_")):
                dump = ast.dump(no.args[1])
                self.assertIn("arestas", dump)
                self.assertIn("eventos_totais", dump)
                return
        self.fail("G5 desapareceu")


class OFalsoAmigoFicaNomeado(unittest.TestCase):
    """`derivacao_observacao` PARECE a resposta e é de outra camada.

        DOIS NOMES IGUAIS EM CAMADAS DIFERENTES SÃO DOIS CONCEITOS.
    """

    def test_a_ADR_nomeia_a_tabela_que_engana(self):
        s = _fonte(ADR)
        self.assertIn("derivacao_observacao", s)
        self.assertIn("falso amigo", s)

    def test_e_ela_e_mesmo_de_outra_camada(self):
        """Não é opinião: as chaves estrangeiras dela dizem-no."""
        sql = _fonte(os.path.join(
            RAIZ, "supabase", "migrations",
            "005_camada_analitica_observado_vs_derivado.sql"))
        bloco = sql[sql.index("create table public.derivacao_observacao"):]
        bloco = bloco[:bloco.index(");")]
        self.assertIn("public.derivacao(id)", bloco)
        self.assertIn("public.observacao(id)", bloco)
        self.assertNotIn("raw_asset", bloco)
        self.assertNotIn("derived_artifact", bloco)


class ORuntimeConheceAArestaQueNinguemEscreve(unittest.TestCase):
    """RUNTIME SABE != O SISTEMA GUARDA."""

    def test_o_writer_devolve_os_dois_lados_no_reencontro(self):
        s = _fonte(os.path.join(RAIZ, "guarda", "preservar_derivado.py"))
        self.assertIn("TESTEMUNHA_NO_BANCO", s)
        self.assertIn("TESTEMUNHA_DESTA_CHAMADA", s)

    def test_e_nao_escreve_relacao_nenhuma(self):
        """Se um dia ele escrever, esta guarda cai — e cai a dizer que a
        missão de implementar aconteceu, que é o que se quer saber."""
        s = _fonte(os.path.join(RAIZ, "guarda", "preservar_derivado.py")).lower()
        self.assertNotIn("derivacao_de_observacao", s)
        self.assertNotIn("participacao", s)


if __name__ == "__main__":
    unittest.main()
