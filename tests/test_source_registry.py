#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DO REGISTO DE IDENTIDADE.

O `SOURCE_ID` e a unica coisa deste projeto que nao se pode consertar depois.
Um numero trocado faz uma fonte responder pelo dado de outra, e o pior e' que
a troca nao aparece: quem indexa por `dict[SOURCE_ID]` fica com a ultima ficha
e perde a primeira em silencio.

Estas provas guardam quatro coisas:
  1 · o scanner FALHA em duplicata, em vez de escolher a ultima
  2 · a populacao emitida e conhecida e nao encolhe
  3 · a proveniencia de cada ID e rastreavel
  4 · T1..T12 valido, e T13 nao recebe identidade nova

A medicao que as motiva esta em `build/source-registry-reconciliation/`.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
INDICE = RAIZ / "docs" / "fontes" / "INDICE-DE-FONTES.md"
SCANNER = RAIZ / "system-map" / "scripts" / "scan_sources.py"
PROVA = RAIZ / "build" / "source-registry-reconciliation"
ID = re.compile(r"\b(?:IT|ES|FR|EU|XX|PT|DE)-T\d{1,2}-\d{3}\b")

# ── A POPULACAO MEDIDA EM 14/09/2026, congelada como testemunha ───────────
# Nao e' um alvo a bater: e' o retrato do dia em que se mediu. Se a populacao
# encolher, alguem perdeu identidade — e isso e' o que este numero apanha.
EMITIDOS_EM_2026_09_14 = 255
# As TRES colisoes de identidade REAIS, decididas por gente em 14/09/2026:
#   IT-T10-001 -> ARPAV          (nao ISMEA, que ja' e' IT-T10-007)
#   IT-T10-002 -> OpenStreetMap  (nao BMTI)
#   IT-T10-003 -> ISTAT Distribuzione (nao o coeweb, encerrado)
COLISOES_DECIDIDAS = {"IT-T10-001", "IT-T10-002", "IT-T10-003"}

# ⚠️ E DUAS QUE O DETETOR CHAMA DE COLISAO E NAO SAO — diagnostico medido:
# sao a MESMA fonte descrita em DOIS ficheiros, um pela pagina e outro pela
# API. `ES-T3-001` e' o RAIF da Andaluzia (atlas: pagina do dataset;
# contratos: endpoint da API) e `FR-T4-001` e' o E-Phy da ANSES (idem). O
# padrao e' o do `ES-T4-005`: SAME_SOURCE_MULTIPLE_ROUTES. O classificador
# compara nome+rota e conta «nomes diferentes» quando um ficheiro usa o titulo
# do dataset e o outro o nome do dono.
#
# Ficam aqui LISTADAS, e nao apagadas: a proxima missao afina o classificador
# para as reclassificar, e ate la' o teste continua a guardar contra uma
# SEXTA aparecer.
FALSOS_POSITIVOS_A_RECLASSIFICAR = {"ES-T3-001", "FR-T4-001"}

# `IT-T4-001` e `ES-T4-005` sairam da lista: medido que NUNCA estiveram em
# disputa — eram defeitos do leitor (ID mencionado na ficha alheia, e campo
# `SUPERSEDED_BY` lido como declaracao).
COLISOES_VIVAS_CONHECIDAS = COLISOES_DECIDIDAS | FALSOS_POSITIVOS_A_RECLASSIFICAR


def _censo():
    p = PROVA / "censo.json"
    if not p.exists():
        raise unittest.SkipTest(
            "censo ausente — correr candidatas/registry_censo.py")
    return json.loads(p.read_text(encoding="utf-8"))


class TestScannerFalhaEmDuplicata(unittest.TestCase):
    """SCANNER_FAILS_ON_DUPLICATE — a prova mais importante deste ficheiro."""

    def test_o_scanner_corre_no_atlas_limpo(self):
        # CONTROLE NEGATIVO: sem isto, um scanner que falha SEMPRE passaria
        # o teste de mutacao e ninguem notaria.
        r = subprocess.run([sys.executable, str(SCANNER)], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace",
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        self.assertEqual(0, r.returncode,
                         f"o scanner falhou no atlas LIMPO:\n{r.stdout}\n{r.stderr}")

    def test_duplicar_um_source_id_reprova(self):
        """MUTACAO: duas fichas com o mesmo numero tem de parar o scanner."""
        original = ATLAS.read_text(encoding="utf-8")
        blocos = re.split(r"\n(?=#### )", original)
        alvo = next((p for p in blocos[1:]
                     if re.search(r"^SOURCE_ID:\s*(EU|FR|ES|IT)-T\d{1,2}-\d{3}\s*$",
                                  p, re.M)), None)
        self.assertIsNotNone(alvo, "nao achei ficha com SOURCE_ID simples")
        sid = re.search(r"^SOURCE_ID:\s*(\S+)", alvo, re.M).group(1)
        # `mkstemp` devolve um DESCRITOR ABERTO, e no Windows um ficheiro
        # aberto nao se apaga — o `os.unlink` do fim rebentava com WinError 32.
        fd, guardado = tempfile.mkstemp(suffix=".md")
        os.close(fd)
        shutil.copy2(ATLAS, guardado)
        try:
            ATLAS.write_text(original + "\n" + alvo, encoding="utf-8")
            r = subprocess.run([sys.executable, str(SCANNER)], cwd=RAIZ,
                               capture_output=True, text=True,
                               encoding="utf-8", errors="replace",
                               env={**os.environ,
                                    "PYTHONIOENCODING": "utf-8"})
            self.assertNotEqual(
                0, r.returncode,
                "o scanner ACEITOU um SOURCE_ID duplicado. Isto e' a falha "
                "silenciosa que faz uma fonte desaparecer do mapa sem erro.")
            self.assertIn(sid, r.stdout + r.stderr,
                          "o scanner reprovou mas NAO disse qual ID colidiu — "
                          "uma falha sem nome nao se conserta")
        finally:
            shutil.copy2(guardado, ATLAS)
            os.unlink(guardado)
        # e depois de restaurar, tem de voltar a passar
        r2 = subprocess.run([sys.executable, str(SCANNER)], cwd=RAIZ,
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace",
                            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        self.assertEqual(0, r2.returncode,
                         "o atlas nao voltou ao estado original")


class TestPopulacaoGlobal(unittest.TestCase):
    """GLOBAL_POPULATION_COMPLETE e ZERO_ID_LOSS."""

    def test_a_populacao_emitida_nao_encolheu(self):
        c = _censo()
        n = len(c["UNIAO"])
        self.assertGreaterEqual(
            n, EMITIDOS_EM_2026_09_14,
            f"a populacao emitida caiu de {EMITIDOS_EM_2026_09_14} para {n}. "
            "Identidade emitida nao se perde: ou alguem apagou um registo, ou "
            "o leitor do censo deixou de ver uma forma de declaracao "
            "(ja aconteceu com a faixa `ES-T7-001..027` e com as tabelas de "
            "estado).")

    def test_a_faixa_de_ids_e_expandida(self):
        """`ES-T7-001..027` sao 27 identidades, nao duas."""
        c = _censo()
        faixa = [f"ES-T7-{n:03d}" for n in range(1, 28)]
        faltam = [x for x in faixa if x not in set(c["UNIAO"])]
        self.assertEqual(
            [], faltam,
            f"{len(faltam)} IDs da faixa ES-T7-001..027 nao entraram no censo. "
            "Um atlas reconciliado sem eles perderia fontes sem acusar nada.")

    def test_toda_identidade_tem_proveniencia(self):
        """FIRST_ASSIGNMENT_TRACEABLE."""
        c = _censo()
        sem = [i for i in c["UNIAO"] if i not in c["PRIMEIRA_ATRIBUICAO"]]
        self.assertEqual(
            [], sem[:12],
            f"{len(sem)} IDs sem primeira atribuicao conhecida. Sem "
            "proveniencia nao se resolve colisao: «qual apareceu primeiro» "
            "deixa de ter resposta.")


class TestColisoes(unittest.TestCase):
    """ZERO_ID_COLLISION — e as que hoje existem estao NOMEADAS."""

    def test_nenhuma_colisao_nova_apareceu(self):
        p = PROVA / "colisoes.json"
        if not p.exists():
            self.skipTest("dossie de colisoes ausente")
        vivas = set(json.loads(p.read_text(encoding="utf-8"))["VIVAS"])
        novas = vivas - COLISOES_VIVAS_CONHECIDAS
        self.assertEqual(
            set(), novas,
            f"colisao de identidade NOVA: {sorted(novas)}. As cinco conhecidas "
            "estao registadas e bloqueadas; uma sexta significa que alguem "
            "emitiu numero contra um registo parcial.")

    def test_o_atlas_desta_linha_nao_tem_duplicata(self):
        """DUPLICATE_SOURCE_ID = 0 no ficheiro que esta linha governa."""
        t = ATLAS.read_text(encoding="utf-8")
        declarados = re.findall(r"^SOURCE_ID:\s*(\S+)\s*$", t, re.M)
        simples = [s for s in declarados if ID.fullmatch(s)]
        dobrados = {s for s in simples if simples.count(s) > 1}
        self.assertEqual(set(), dobrados,
                         f"SOURCE_ID declarado duas vezes no atlas: {dobrados}")


class TestTaxonomia(unittest.TestCase):
    """T1_T12_VALID e T13_NOT_NEW."""

    def test_todo_territorio_de_id_esta_entre_t1_e_t12_ou_e_legado(self):
        c = _censo()
        fora, t13 = [], []
        for i in c["UNIAO"]:
            t = i.split("-")[1]
            n = int(t[1:])
            if n == 13:
                t13.append(i)
            elif not 1 <= n <= 12:
                fora.append(i)
        self.assertEqual([], fora, f"IDs fora de T1..T12 e nao-T13: {fora}")
        # T13 existe como ocupante legado e NAO cresce
        self.assertLessEqual(
            len(t13), 5,
            f"T13 passou a ter {len(t13)} identidades. T13 nao e' canonico e "
            "nao recebe identidade nova — so' preserva as historicas.")

    def test_nenhuma_identidade_nova_de_t13_nesta_missao(self):
        """T13_NOT_NEW, medido contra a primeira atribuicao."""
        c = _censo()
        novos = [i for i in c["UNIAO"] if i.split("-")[1] == "T13"
                 and c["PRIMEIRA_ATRIBUICAO"].get(i, {})
                 .get("FIRST_ASSIGNMENT_DATE", "") >= "2026-09-14"]
        self.assertEqual([], novos,
                         f"T13 recebeu identidade em 14/09/2026: {novos}")


class TestIndiceBateComAtlas(unittest.TestCase):
    """INDEX_MATCHES_ATLAS."""

    def test_o_indice_e_gerado_e_declara_de_onde_vem(self):
        t = INDICE.read_text(encoding="utf-8")
        self.assertIn("Este ficheiro é gerado", t,
                      "o indice tem de dizer que e' gerado, senao alguem "
                      "edita-o a mao e as duas contas divergem")
        self.assertIn("ATLAS-DE-FONTES-EAME.md", t,
                      "o indice tem de apontar para o seu dono")

    def test_o_numero_do_indice_bate_com_o_que_o_scanner_ve(self):
        t = INDICE.read_text(encoding="utf-8")
        m = re.search(r"fichas completas no atlas \|\s*\*\*(\d+)\*\*", t)
        self.assertIsNotNone(m, "o indice nao declara quantas fichas ha")
        declarado = int(m.group(1))
        gerado = json.loads(
            (RAIZ / "system-map" / "data" / "sources.generated.json")
            .read_text(encoding="utf-8"))
        reais = len(gerado.get("SOURCES", gerado.get("sources", [])))
        self.assertEqual(
            declarado, reais,
            f"o indice diz {declarado} fichas e o scanner ve {reais}. "
            "Atlas e indice tem de fechar, senao o numero publicado e' "
            "decorativo.")


class TestMasterJsonNaoEDono(unittest.TestCase):
    """O JSON historico nao vira owner de identidade."""

    def test_o_master_json_nao_se_declara_registo_canonico(self):
        p = RAIZ / "candidatas" / "ITALY-SOURCE-MASTER-V1.json"
        if not p.exists():
            self.skipTest("master json ausente nesta linha")
        c = _censo()
        no_master = set(c["EMISSORES"].get(
            "candidatas/ITALY-SOURCE-MASTER-V1.json", []))
        no_atlas = set(ID.findall(ATLAS.read_text(encoding="utf-8")))
        # o JSON pode conter identidades que o atlas nao tem — e' historico.
        # O que NAO pode e' alguem trata-lo como dono: o dono e' o atlas.
        self.assertTrue(
            no_master,
            "se o master json deixou de ter IDs, ele deixou de ser fonte "
            "historica de identidade — reveja CAN_RETIRE_AS_IDENTITY_OWNER")
        self.assertTrue(
            (RAIZ / "candidatas" / "fonte_nova.py").read_text(encoding="utf-8")
            .find("virou ficha no atlas") > 0,
            "a fila de candidatas tem de continuar a dizer que o SOURCE_ID "
            "nasce no ATLAS, e nao noutro sitio")


if __name__ == "__main__":
    unittest.main(verbosity=2)
