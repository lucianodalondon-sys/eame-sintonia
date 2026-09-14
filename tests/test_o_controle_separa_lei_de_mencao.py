#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DE C-CTRL-INT-NIGHT-02 — o detector, a supersessao e o chao.

    python3 -m unittest tests.test_o_controle_separa_lei_de_mencao -v

Tres defeitos do Control Plane mantinham o portao reprovado, e nenhum dos tres
era o que o nome dele dizia:

    UNREGISTERED_CANONICAL_DOCUMENT = 10   eram dez MENCOES, zero autoridades
    BROKEN_POINTER = 1                     era um CARD_ID lido como caminho
    o chao                                 media outra arvore

    MENCIONAR UMA LEI NAO E PROMULGAR UMA.
    IDENTIDADE NAO E MORADA.
    UMA FOTOGRAFIA DE DIVIDA DE OUTRA LINHA NAO MEDE ESTA.

O que estas provas guardam e a separacao. O que elas NAO provam e que a
Intelligence funciona.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "controle"))

import portao_do_controle as PORTAO          # noqa: E402

REGISTO_REAL = RAIZ / "controle" / "AUTORIDADES-CANONICAS.json"
CHAO_REAL = RAIZ / "controle" / "CHAO-DO-CONTROLE.json"


def declara(texto: str, caminho: str = "docs/operacao/QUALQUER.md"):
    """O veredito do detector real sobre este texto."""
    return PORTAO.declara_se_lei(caminho, texto.split("\n"))


def correr(registo: dict, pasta: Path):
    """Censo + portao REAIS sobre um registo descartavel.

    O repositorio nao e tocado: as variaveis `SINTONIA_CONTROLE_*` desviam
    leitura e escrita. Um teste que estraga o que testa nao se corre duas vezes.
    """
    p_reg, p_censo = pasta / "registo.json", pasta / "censo.json"
    p_sala, p_chao = pasta / "sala.md", pasta / "chao.json"
    p_reg.write_text(json.dumps(registo, ensure_ascii=False), encoding="utf-8")
    shutil.copyfile(CHAO_REAL, p_chao)
    env = {**os.environ,
           "SINTONIA_CONTROLE_REGISTO": str(p_reg),
           "SINTONIA_CONTROLE_CENSO": str(p_censo),
           "SINTONIA_CONTROLE_SALA": str(p_sala),
           "SINTONIA_CONTROLE_CHAO": str(p_chao)}
    c = subprocess.run([sys.executable, str(RAIZ / "controle" / "censo_do_controle.py")],
                       capture_output=True, text=True, env=env)
    if c.returncode != 0:
        raise AssertionError("o censo rebentou: " + c.stdout + c.stderr)
    g = subprocess.run([sys.executable, str(RAIZ / "controle" / "portao_do_controle.py")],
                       capture_output=True, text=True, env=env)
    return json.loads(p_censo.read_text(encoding="utf-8")), g.stdout + g.stderr


def base():
    return json.loads(REGISTO_REAL.read_text(encoding="utf-8"))


def achar(reg, cid):
    return next(a for a in reg["AUTHORITIES"] if a["CARD_ID"] == cid)


def aresta(censo, de, para):
    return next(e for e in censo["GOVERNANCE_EDGES"]
                if e["FROM"] == de and e["TO_PATH"] == para)


# ══════════════════════════════════════════════════════════════════════════════
class D_ODetectorSeparaPromulgacaoDeMencao(unittest.TestCase):
    """D1–D6 · o detector de documento-que-se-diz-lei, atacado.

    O objetivo declarado da missao: REDUZIR FALSO POSITIVO SEM CRIAR FALSO
    NEGATIVO. Cada par abaixo e uma mencao e a promulgacao correspondente — se o
    detector nao distinguir os dois, uma das duas provas cai.
    """

    def test_D1_uma_autoridade_real_nao_registada_continua_a_ser_apanhada(self):
        # A forma exacta de `BIBLIA-CANONICA-DA-COLETA.md:9`, que e uma lei real.
        v = declara("# UMA LEI QUALQUER\n\n```text\nCANONICAL_OWNER   este ficheiro\n```\n")
        self.assertTrue(v, "uma promulgacao real tem de ser apanhada")
        self.assertEqual(v[0], "LEGISLA")

    def test_D2_dizer_que_o_dono_e_outro_ficheiro_nao_torna_este_uma_lei(self):
        v = declara("O canonical owner deste conceito e `guarda/preservar_coleta.py`,\n"
                    "e nao este relatorio.\n")
        self.assertEqual(v, (), "apontar para o dono nao e ser o dono")

    def test_D3_um_handoff_que_cita_a_palavra_nao_vira_autoridade(self):
        v = declara("| `generate_system_map.py` | `CANONICAL_OWNERS` (topologia) |\n",
                    "handoff/S2A-R-RECONCILIACAO.md")
        self.assertEqual(v, (), "citar num handoff nao promulga nada")

    def test_D4_a_declaracao_em_cabecalho_e_apanhada(self):
        v = declara("DESIGN_SOURCE_OF_TRUTH = ADAMA_DESIGN_SYSTEM\n")
        self.assertTrue(v)
        self.assertEqual(v[0], "LEGISLA")

    def test_D5_uma_copia_historica_de_uma_lei_nao_cria_segunda_autoridade(self):
        # O historico cita a lei INTEIRA, mas a citacao esta enquadrada como
        # citacao: a linha fala do documento antigo, nunca de si propria.
        v = declara("## O que a lei antiga dizia\n\n"
                    "> a Biblia da coleta dizia que o dono canonico era ela propria\n",
                    "know-how/daily/2026-09-10.md")
        self.assertEqual(v, (), "um historico a citar nao e uma segunda lei")

    def test_D6_uma_lei_verdadeira_escondida_em_docs_operacao_e_apanhada(self):
        v = declara("# CONTRATO X\n\nEste documento e o dono canonico do conceito Y.\n",
                    "docs/operacao/CONTRATO-X.md")
        self.assertTrue(v, "esconder uma lei numa pasta nao a torna invisivel")
        self.assertEqual(v[0], "RECLAMA_SE")

    # ── o que provocou os dez falsos positivos, um a um ─────────────────────
    def test_D7_um_nome_de_metrica_nao_e_uma_declaracao(self):
        for linha in ("DUPLICATE_CANONICAL_OWNERS = 0",
                      "REGISTRO_REGULATORIO_CANONICAL_OWNER = MISSING",
                      "CANONICAL_OWNER_FOUND?   SIM",
                      "STRUCTURED_CANONICAL_OWNER_EXISTS = NO",
                      "`CANONICAL_OWNER_VIOLATIONS = MULTIPLE_CANONICAL_WRITERS`"):
            with self.subTest(linha=linha):
                self.assertEqual(declara(linha + "\n"), (),
                                 "a chave tem de ser a palavra inteira")

    def test_D8_prosa_sobre_o_dono_de_outra_coisa_nao_e_declaracao(self):
        for linha in ("o executor produz o artefato, o **dono canónico** persiste",
                      "O3  catalogo_importar escreve raw_asset fora do dono canónico",
                      "FORWARD   derivar_um()  -> um raw_asset real -> o dono canónico"):
            with self.subTest(linha=linha):
                self.assertEqual(declara(linha + "\n"), ())

    def test_D9_os_dez_acusados_desta_arvore_estao_todos_inocentes(self):
        """A prova que fecha a hipotese da missao anterior.

        Ela disse que registar os dez exigia decidir um `CONCEPT_OWNER` da
        Collection. Nenhum dos dez e uma autoridade: a decisao nunca foi precisa.
        """
        dez = ["docs/operacao/A-CASA-DO-DERIVADO.md",
               "docs/operacao/CIRURGIA-OBJETO-E-OBSERVACAO.md",
               "docs/operacao/CONTRATO-DOS-STRUCTURED-TARGETS.md",
               "docs/operacao/ENCANAMENTO-DA-COLETA.md",
               "docs/operacao/IDENTIDADE-DA-OBSERVACAO-RAW.md",
               "docs/operacao/STRUCTURED-POR-ESPECIE-E-NOT-APPLICABLE.md",
               "docs/operacao/TOPOLOGIA-DA-COLETA.md",
               "docs/sintonia-scrap/C7-LUGAR-DO-FATO.md",
               "handoff/S2A-R-RECONCILIACAO.md",
               "know-how/daily/2026-09-10.md"]
        for p in dez:
            with self.subTest(doc=p):
                f = RAIZ / p
                self.assertTrue(f.exists(), f"{p} saiu da arvore")
                v = PORTAO.declara_se_lei(
                    p, f.read_text(encoding="utf-8", errors="replace").split("\n"))
                self.assertEqual(v, (), f"{p} nao promulga nada: {v}")

    def test_D10_as_autoridades_reais_desta_arvore_continuam_visiveis(self):
        """O falso negativo seria pior que o falso positivo: a lei desaparecia."""
        for p, forma in (("AGENTS.md", "RECLAMA_SE"),
                         ("CLAUDE.md", "LEGISLA"),
                         ("BIBLIA-CANONICA-DA-COLETA.md", "LEGISLA")):
            with self.subTest(doc=p):
                v = PORTAO.declara_se_lei(
                    p, (RAIZ / p).read_text(encoding="utf-8").split("\n"))
                self.assertTrue(v, f"{p} promulga e o detector ficou cego")
                self.assertEqual(v[0], forma)

    def test_D11_nao_existe_lista_de_excecoes_por_nome_de_ficheiro(self):
        """A correcao tinha de ser estrutural.

        Um `if caminho == 'docs/operacao/X.md': ignorar` passa o portao de hoje e
        cria o defeito de amanha com outro nome.
        """
        fonte = (RAIZ / "controle" / "portao_do_controle.py").read_text(encoding="utf-8")
        for proibido in ("A-CASA-DO-DERIVADO", "ENCANAMENTO-DA-COLETA",
                         "TOPOLOGIA-DA-COLETA", "C7-LUGAR-DO-FATO",
                         "S2A-R-RECONCILIACAO", "2026-09-10"):
            self.assertNotIn(proibido, fonte,
                             "o portao nao pode conhecer um ficheiro pelo nome")


# ══════════════════════════════════════════════════════════════════════════════
class S_UmaSupersessaoLigaIdentidadesNaoMoradas(unittest.TestCase):
    """S1–S6 · o modelo de supersessao, atacado.

        AUTHORITY_ID != CANONICAL_PATH

    Uma lei substituida quase sempre ja nao vive aqui — e essa a razao de alguem
    a ter substituido. Exigir o caminho dela torna a historia indeclaravel.
    """

    def test_S0_o_registo_declara_que_o_alvo_e_uma_identidade(self):
        R = base()
        self.assertEqual(R["EDGE_TYPES"]["SUPERSEDES"]["target"], "AUTHORITY_ID")
        for t in ("GOVERNS", "CONSTRAINS", "REFERENCES", "IMPLEMENTS",
                  "VALIDATES", "OBSERVES", "GENERATES"):
            self.assertEqual(R["EDGE_TYPES"][t]["target"], "PATH", t)

    def test_S1_A_substitui_B_com_as_duas_na_arvore(self):
        reg = base()
        a = achar(reg, "A-BIBLIA-ENG-INTELIGENCIA")
        a["SUPERSEDES"] = ["A-MOTOR-V2-REQUISITOS"]
        achar(reg, "A-MOTOR-V2-REQUISITOS")["SUPERSEDED_BY"] = ["A-BIBLIA-ENG-INTELIGENCIA"]
        achar(reg, "A-BIBLIA-INTELIGENCIA")["SUPERSEDED_BY"] = []
        with tempfile.TemporaryDirectory() as td:
            censo, _ = correr(reg, Path(td))
        e = aresta(censo, "A-BIBLIA-ENG-INTELIGENCIA", "A-MOTOR-V2-REQUISITOS")
        self.assertEqual(e["EDGE_STATE"], "OBSERVED")
        self.assertEqual(e["PROOF_KIND"], "REGISTRY_RECIPROCAL")

    def test_S2_A_substitui_B_e_B_ja_nao_tem_ficheiro_nesta_arvore(self):
        """O caso real. Continua valido, e diz em voz alta que o alvo nao esta ca."""
        with tempfile.TemporaryDirectory() as td:
            censo, saida = correr(base(), Path(td))
        e = aresta(censo, "A-BIBLIA-ENG-INTELIGENCIA", "A-BIBLIA-INTELIGENCIA")
        self.assertEqual(e["TO_KIND"], "AUTHORITY_ID")
        self.assertFalse(e["TO_IN_TREE"], "o alvo nao vive nesta arvore, e diz-se")
        self.assertEqual(e["EDGE_STATE"], "OBSERVED")
        self.assertNotIn("FAIL  BROKEN_POINTER", saida)

    def test_S3_um_CARD_ID_que_nao_existe_reprova(self):
        reg = base()
        achar(reg, "A-BIBLIA-ENG-INTELIGENCIA")["SUPERSEDES"] = ["A-LEI-QUE-NUNCA-EXISTIU"]
        with tempfile.TemporaryDirectory() as td:
            censo, saida = correr(reg, Path(td))
        e = aresta(censo, "A-BIBLIA-ENG-INTELIGENCIA", "A-LEI-QUE-NUNCA-EXISTIU")
        self.assertEqual(e["PROOF_KIND"], "UNKNOWN_AUTHORITY_ID")
        self.assertEqual(e["EDGE_STATE"], "DECLARED")
        self.assertIn("FAIL  UNKNOWN_AUTHORITY_ID", saida)

    def test_S4_um_caminho_inexistente_num_campo_que_exige_caminho_reprova(self):
        """A prova que garante que nao amoleci o `BROKEN_POINTER` ao separa-lo."""
        reg = base()
        achar(reg, "A-AGENTS")["GOVERNS"].append("motor/ficheiro_que_nao_existe.py")
        with tempfile.TemporaryDirectory() as td:
            censo, saida = correr(reg, Path(td))
        e = aresta(censo, "A-AGENTS", "motor/ficheiro_que_nao_existe.py")
        self.assertEqual(e["TO_KIND"], "PATH")
        self.assertEqual(e["PROOF_KIND"], "ABSENT")
        self.assertIn("FAIL  BROKEN_POINTER", saida)

    def test_S5_uma_lei_substituida_nao_continua_canonica(self):
        reg = base()
        achar(reg, "A-BIBLIA-INTELIGENCIA")["LIFECYCLE"] = "CANONICAL"
        with tempfile.TemporaryDirectory() as td:
            _, saida = correr(reg, Path(td))
        self.assertIn("FAIL  SUPERSEDED_MARKED_CANONICAL", saida)

    def test_S6_duas_leis_nao_reivindicam_o_mesmo_conceito(self):
        reg = base()
        gemea = dict(achar(reg, "A-BIBLIA-COLETA"))
        gemea["CARD_ID"] = "A-BIBLIA-COLETA-GEMEA"
        gemea["CANONICAL_PATH"] = "docs/biblia/BIBLIA-DA-COLETA-GEMEA.md"
        reg["AUTHORITIES"].append(gemea)
        with tempfile.TemporaryDirectory() as td:
            _, saida = correr(reg, Path(td))
        self.assertIn("FAIL  DUPLICATE_CONCEPT_OWNER", saida)

    def test_S7_meia_supersessao_reprova(self):
        """Uma declaracao nao se prova a si propria: a outra ponta tem de confirmar."""
        reg = base()
        achar(reg, "A-BIBLIA-INTELIGENCIA")["SUPERSEDED_BY"] = []
        with tempfile.TemporaryDirectory() as td:
            censo, saida = correr(reg, Path(td))
        e = aresta(censo, "A-BIBLIA-ENG-INTELIGENCIA", "A-BIBLIA-INTELIGENCIA")
        self.assertEqual(e["PROOF_KIND"], "MISSING_RECIPROCAL")
        self.assertEqual(e["EDGE_STATE"], "DECLARED")
        self.assertIn("FAIL  SUPERSESSION_RECIPROCAL", saida)

    def test_S8_a_exigencia_de_prova_vem_do_registo_e_nao_de_uma_copia(self):
        """A lei estava escrita em dois sitios, e duas copias divergem."""
        fonte = (RAIZ / "controle" / "censo_do_controle.py").read_text(encoding="utf-8")
        self.assertNotIn('"GOVERNS": "TEXT_POINTER"', fonte,
                         "o censo nao pode carregar a sua propria copia de observed_needs")


# ══════════════════════════════════════════════════════════════════════════════
class C_OChaoMedeEstaArvoreOuNaoVale(unittest.TestCase):
    """O chao da divida: linhagem provada e membros comparados, nao so contagens."""

    def test_C1_o_chao_declara_onde_foi_medido(self):
        C = json.loads(CHAO_REAL.read_text(encoding="utf-8"))
        self.assertIn("MEDIDO_EM", C)
        self.assertTrue(C["MEDIDO_EM"].get("HEAD"))

    def test_C2_a_arvore_do_chao_esta_atras_desta(self):
        C = json.loads(CHAO_REAL.read_text(encoding="utf-8"))
        cabeca = C["MEDIDO_EM"]["HEAD"]
        r = subprocess.run(["git", "-C", str(RAIZ), "merge-base",
                            "--is-ancestor", cabeca, "HEAD"], capture_output=True)
        self.assertEqual(r.returncode, 0,
                         f"{cabeca} nao e antepassado de HEAD: o chao mede outra arvore")

    def test_C3_a_migracao_guarda_a_prova_membro_a_membro(self):
        C = json.loads(CHAO_REAL.read_text(encoding="utf-8"))
        mig = C["MEDIDO_EM"].get("MIGRADO_DE")
        self.assertTrue(mig, "um chao migrado sem prova e um tecto sem dono")
        self.assertTrue(mig.get("PORQUE"))
        for cat, p in mig["PROVA"].items():
            with self.subTest(categoria=cat):
                self.assertEqual(p["NOVOS"], [],
                                 "migrar nao pode trazer divida nova")
                self.assertLessEqual(p["HOJE"], p["TETO_ANTIGO"])

    def test_C4_nenhum_teto_subiu_na_migracao(self):
        C = json.loads(CHAO_REAL.read_text(encoding="utf-8"))
        for cat, p in C["MEDIDO_EM"]["MIGRADO_DE"]["PROVA"].items():
            with self.subTest(categoria=cat):
                self.assertLessEqual(C["TETO"][cat], p["TETO_ANTIGO"],
                                     "teto nao sobe — nunca")

    def test_C5_a_razao_de_um_defeito_nao_vive_dentro_da_identidade_dele(self):
        """`A-DIARIO (6)` fazia o numero de copias fazer parte de QUEM o defeito e."""
        C = json.loads(CHAO_REAL.read_text(encoding="utf-8"))
        for cat, membros in C["MEMBROS"].items():
            for m in membros:
                with self.subTest(membro=m):
                    self.assertNotIn(" (", m, "a razao mora na coluna PORQUE")

    def test_C6_um_mesmo_membro_em_duas_categorias_guarda_duas_razoes(self):
        C = json.loads(CHAO_REAL.read_text(encoding="utf-8"))
        duplos = [m for m in C["MEMBROS"]["DIVERGENT_CANONICAL_COPY"]
                  if m in C["MEMBROS"]["STALE_AUTHORITY"]]
        self.assertTrue(duplos, "esta prova precisa de um membro em duas categorias")
        for m in duplos:
            a = C["PORQUE"].get(f"DIVERGENT_CANONICAL_COPY/{m}", "")
            b = C["PORQUE"].get(f"STALE_AUTHORITY/{m}", "")
            self.assertTrue(a and b and a != b,
                            f"{m}: uma razao apagou a outra")


if __name__ == "__main__":
    unittest.main(verbosity=2)
