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
        s = _fonte(ADR)
        self.assertIn("RECOMENDADO, NÃO IMPLEMENTADO", s)
        self.assertIn("MIGRATION_REQUIRED       = YES", s)

    def test_a_prova_nao_escreve_no_esquema(self):
        """Ela constrói estado pela rota real e por `derivacao_forward`. Não
        cria tabela, não altera coluna, não insere linhagem à mão."""
        s = _fonte(PROVA).lower()
        for proibido in ("create table", "alter table", "drop table",
                         "insert into public.derived_artifact",
                         "insert into public.raw_asset"):
            self.assertNotIn(proibido, s)


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
