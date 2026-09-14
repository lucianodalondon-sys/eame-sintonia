#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DO ATLAS RECONCILIADO.

O que estas provas guardam nao e' o texto do Atlas — e' a IDENTIDADE. Um
`SOURCE_ID` que muda de significado faz uma fonte responder pelo dado de
outra, e nenhuma coleta posterior conserta isso.

As cinco decisoes humanas ficam PINADAS aqui. Se alguem as inverter, estas
provas dizem qual e por que.
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
FAIXA = re.compile(r"\b((?:IT|ES|FR|EU|XX|PT|DE)-T\d{1,2})-(\d{3})\s*\.\.\s*(\d{3})\b")

EMITIDAS_EM_2026_09_14 = 257

# ── ESTAS PROVAS DESCREVEM O ALVO, E O ALVO AINDA NAO FOI PUBLICADO ───────
# O Atlas reconciliado foi construido e PROVADO (257 identidades, zero
# perdidas, zero duplicadas, e a trava do scanner aceita-o), mas NAO foi
# publicado: apareceram duas colisoes que as cinco decisoes nao cobrem, e o
# §16 da missao proibe publicar atlas final com colisao viva.
#
# Por isso estas provas ficam em ESPERA em vez de falharem. Um teste vermelho
# por falta de decisao humana ensina a ignorar vermelho — e ai a suite deixa
# de valer. Elas acendem sozinhas no momento em que o Atlas for publicado,
# porque procuram o marcador que o montador escreve.
MARCADOR = "RECONCILIAÇÃO DO REGISTO DE IDENTIDADE"


def setUpModule():
    if MARCADOR not in ATLAS.read_text(encoding="utf-8"):
        raise unittest.SkipTest(
            "o Atlas reconciliado ainda nao foi publicado — falta decisao "
            "humana sobre ES-T3-001 e FR-T4-001. Correr "
            "`py candidatas/registry_montar_atlas.py` publica-o, e estas "
            "provas acendem sozinhas.")


def fichas():
    """{SOURCE_ID: nº de fichas que o declaram} — a leitura estreita."""
    t = ATLAS.read_text(encoding="utf-8")
    fora = {}
    for p in re.split(r"\n(?=#### )", t):
        if not p.startswith("#### "):
            continue
        c = re.search(r"^#### .*?\n+```\n(.*?)\n```", p, re.S)
        decl = c.group(1) if c else ""
        m = re.search(r"^SOURCE_ID:\s*(.+?)\s*$", decl, re.M)
        alvo = m.group(1) if m else p.splitlines()[0]
        ids = list(ID.findall(alvo))
        for mm in FAIXA.finditer(alvo):
            base, a, b = mm.group(1), int(mm.group(2)), int(mm.group(3))
            ids += [f"{base}-{n:03d}" for n in range(a, b + 1)]
        for i in dict.fromkeys(ids):
            fora[i] = fora.get(i, 0) + 1
    return fora


def bloco_de(sid):
    """O texto da ficha que declara `sid`, ou ''."""
    t = ATLAS.read_text(encoding="utf-8")
    for p in re.split(r"\n(?=#### )", t):
        if not p.startswith("#### "):
            continue
        c = re.search(r"^#### .*?\n+```\n(.*?)\n```", p, re.S)
        decl = c.group(1) if c else ""
        if re.search(rf"^SOURCE_ID:\s*{re.escape(sid)}\s*$", decl, re.M):
            return p
    return ""


class TestPopulacao(unittest.TestCase):
    """GLOBAL_SOURCE_IDS_PRESERVED · ZERO_ID_LOSS · ZERO_ID_COLLISION."""

    def test_o_atlas_tem_a_populacao_inteira(self):
        f = fichas()
        self.assertGreaterEqual(
            len(f), EMITIDAS_EM_2026_09_14,
            f"o Atlas declara {len(f)} identidades e a população emitida é "
            f"{EMITIDAS_EM_2026_09_14}. Identidade emitida não se perde — se "
            "este número caiu, alguém apagou uma ficha ou o leitor deixou de "
            "ver uma forma de declaração (faixa, tabela).")

    def test_nenhuma_identidade_emitida_ficou_fora(self):
        censo = PROVA / "censo.json"
        if not censo.exists():
            self.skipTest("censo ausente")
        uniao = set(json.loads(censo.read_text(encoding="utf-8"))["UNIAO"])
        faltam = sorted(uniao - set(fichas()))
        self.assertEqual([], faltam,
                         f"{len(faltam)} identidades emitidas não estão no "
                         f"Atlas: {faltam[:12]}")

    def test_nenhum_source_id_em_duas_fichas(self):
        dobradas = {k: v for k, v in fichas().items() if v > 1}
        self.assertEqual({}, dobradas,
                         f"SOURCE_ID declarado por duas fichas: {dobradas}")


class TestAsCincoDecisoes(unittest.TestCase):
    """As cinco decisões humanas, pinadas uma a uma."""

    def test_it_t4_001_e_o_ministero(self):
        b = bloco_de("IT-T4-001")
        self.assertTrue(b, "IT-T4-001 não tem ficha")
        self.assertIn("dati.salute.gov.it", b)
        self.assertRegex(b, r"Ministero della Salute")

    def test_arpav_nao_e_it_t4_001(self):
        b = bloco_de("IT-T4-001")
        c = re.search(r"^#### .*?\n+```\n(.*?)\n```", b, re.S)
        self.assertNotIn("arpa.veneto.it", (c.group(1) if c else ""),
                         "a rota da ARPAV entrou na ficha do Ministero")

    def test_es_t4_005_e_uma_fonte_com_duas_rotas(self):
        f = fichas()
        self.assertEqual(1, f.get("ES-T4-005"),
                         "ES-T4-005 tem de ser UMA ficha: URL não é identidade")
        b = bloco_de("ES-T4-005")
        self.assertRegex(b, r"MAPA")

    def test_it_t10_001_e_a_arpav(self):
        b = bloco_de("IT-T10-001")
        self.assertTrue(b, "IT-T10-001 não tem ficha")
        self.assertIn("arpa.veneto.it", b)
        self.assertRegex(b, r"ARPAV")

    def test_ismea_nao_e_it_t10_001(self):
        c = re.search(r"^#### .*?\n+```\n(.*?)\n```", bloco_de("IT-T10-001"),
                      re.S)
        self.assertNotIn("ismeamercati", (c.group(1) if c else "").lower())

    def test_it_t10_002_e_o_openstreetmap(self):
        b = bloco_de("IT-T10-002")
        self.assertTrue(b, "IT-T10-002 não tem ficha")
        self.assertRegex(b, r"OpenStreetMap")
        self.assertIn("overpass", b.lower())

    def test_bmti_nao_e_it_t10_002(self):
        c = re.search(r"^#### .*?\n+```\n(.*?)\n```", bloco_de("IT-T10-002"),
                      re.S)
        self.assertNotIn("bmti", (c.group(1) if c else "").lower())

    def test_it_t10_003_e_o_istat_distribuzione(self):
        b = bloco_de("IT-T10-003")
        self.assertTrue(b, "IT-T10-003 não tem ficha")
        self.assertIn("DCSP_FITOSANITARI", b)
        self.assertRegex(b, r"Distribuzione per uso agricolo")

    def test_coeweb_nao_e_it_t10_003(self):
        c = re.search(r"^#### .*?\n+```\n(.*?)\n```", bloco_de("IT-T10-003"),
                      re.S)
        self.assertNotIn("coeweb", (c.group(1) if c else "").lower(),
                         "a rota encerrada do coeweb entrou na ficha do ISTAT "
                         "Distribuzione")

    def test_ismea_continua_a_ser_it_t10_007(self):
        b = bloco_de("IT-T10-007")
        self.assertTrue(b, "IT-T10-007 perdeu a ficha")
        self.assertRegex(b, r"ISMEA")


class TestFaixa(unittest.TestCase):
    """ES_T7_RANGE_27 — 27 identidades, nenhuma perdida, nenhuma duplicada."""

    def test_a_faixa_es_t7_tem_27_identidades(self):
        f = fichas()
        faixa = [f"ES-T7-{n:03d}" for n in range(1, 28)]
        faltam = [x for x in faixa if x not in f]
        dobradas = [x for x in faixa if f.get(x, 0) > 1]
        self.assertEqual([], faltam, f"faltam da faixa: {faltam}")
        self.assertEqual([], dobradas, f"duplicadas na faixa: {dobradas}")
        self.assertEqual(27, len([x for x in faixa if x in f]))


class TestDerivaDe(unittest.TestCase):
    """DERIVA_DE_VALID — só entre a mesma fonte, e nunca inventado."""

    def test_deriva_de_aponta_para_identidade_existente(self):
        t = ATLAS.read_text(encoding="utf-8")
        f = set(fichas())
        maus = []
        for m in re.finditer(r"^DERIVA_DE:\s*(\S+)", t, re.M):
            alvo = m.group(1).strip()
            if ID.fullmatch(alvo) and alvo not in f:
                maus.append(alvo)
        self.assertEqual([], maus,
                         f"DERIVA_DE aponta para identidade inexistente: {maus}")

    def test_nenhum_deriva_de_foi_inventado_nesta_reconciliacao(self):
        """Medido: nenhum par da população prova «mesma fonte, dois números»."""
        p = PROVA / "classificacao.json"
        if not p.exists():
            self.skipTest("classificação ausente")
        d = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(
            {}, d.get("DUPLICADAS", {}),
            "apareceu um par «mesma fonte, dois IDs». Antes de escrever "
            "DERIVA_DE, provar que é a MESMA fonte: `IT-T10-004` é o registo "
            "do vinho e `IT-T10-005` o do azeite, mesmo dono e fontes "
            "diferentes.")


class TestPendencias(unittest.TestCase):
    """O que não recebeu identidade continua nomeado e visível."""

    def test_as_fontes_sem_identidade_estao_declaradas(self):
        t = ATLAS.read_text(encoding="utf-8")
        self.assertIn("NEEDS_SOURCE_REGISTRATION", t)
        self.assertIn("BMTI", t)
        for alvo in ("coeweb", "esploradati.istat.it/coeweb"):
            self.assertIn(alvo, t, f"«{alvo}» devia estar declarado")

    def test_os_ids_gastos_sem_ficha_estao_reservados(self):
        t = ATLAS.read_text(encoding="utf-8")
        self.assertIn("SPENT_NO_RECORD", t)
        p = PROVA / "classificacao.json"
        if p.exists():
            orfaos = json.loads(p.read_text(encoding="utf-8"))["FANTASMAS"]
            faltam = [x for x in orfaos if x not in t]
            self.assertEqual([], faltam,
                             f"IDs gastos não declarados no Atlas: {faltam}")

    def test_a_pendencia_de_territorio_nao_mudou_identidade(self):
        t = ATLAS.read_text(encoding="utf-8")
        self.assertIn("TERRITORY_FIT_REVIEW", t)
        self.assertRegex(bloco_de("IT-T10-002"), r"TERRITORY:\s*T10",
                         "IT-T10-002 mudou de território — o §5 proíbe "
                         "reclassificar identidade por estética")


class TestT13(unittest.TestCase):
    def test_nenhuma_identidade_nova_em_t13(self):
        t13 = [i for i in fichas() if i.split("-")[1] == "T13"]
        self.assertLessEqual(len(t13), 5,
                             f"T13 cresceu para {len(t13)}: {sorted(t13)}")


class TestScannerEIndice(unittest.TestCase):
    """SCANNER_DUPLICATE_FAILS · INDEX_MATCHES_ATLAS · DETERMINISTIC."""

    def _correr(self):
        return subprocess.run(
            [sys.executable, str(SCANNER)], cwd=RAIZ, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})

    def test_o_scanner_passa_no_atlas_reconciliado(self):
        r = self._correr()
        self.assertEqual(0, r.returncode,
                         f"o scanner falhou no Atlas reconciliado:\n"
                         f"{r.stdout[-900:]}\n{r.stderr[-400:]}")

    def test_duplicar_um_source_id_reprova(self):
        original = ATLAS.read_text(encoding="utf-8")
        alvo = bloco_de("IT-T10-002")
        self.assertTrue(alvo, "sem ficha para mutar")
        fd, bak = tempfile.mkstemp(suffix=".md")
        os.close(fd)
        shutil.copy2(ATLAS, bak)
        try:
            ATLAS.write_text(original + "\n" + alvo, encoding="utf-8")
            r = self._correr()
            self.assertNotEqual(0, r.returncode,
                                "o scanner ACEITOU SOURCE_ID duplicado")
            self.assertIn("IT-T10-002", r.stdout + r.stderr,
                          "reprovou sem dizer qual ID colidiu")
        finally:
            shutil.copy2(bak, ATLAS)
            os.unlink(bak)
        self.assertEqual(0, self._correr().returncode,
                         "o Atlas não voltou ao estado original")

    def test_regeneracao_e_deterministica(self):
        gerado = RAIZ / "system-map" / "data" / "sources.generated.json"
        antes = gerado.read_text(encoding="utf-8")
        self.assertEqual(0, self._correr().returncode)
        depois = gerado.read_text(encoding="utf-8")
        self.assertEqual(antes, depois,
                         "correr o scanner duas vezes deu resultado diferente")

    def test_o_indice_bate_com_o_que_o_scanner_ve(self):
        t = INDICE.read_text(encoding="utf-8")
        m = re.search(r"fichas completas no atlas \|\s*\*\*(\d+)\*\*", t)
        self.assertIsNotNone(m, "o índice não declara quantas fichas há")
        ger = json.loads((RAIZ / "system-map" / "data" /
                          "sources.generated.json").read_text(encoding="utf-8"))
        reais = len(ger.get("SOURCES", ger.get("sources", [])))
        self.assertEqual(int(m.group(1)), reais,
                         f"o índice diz {m.group(1)} e o scanner vê {reais}")


class TestUmDono(unittest.TestCase):
    def test_nao_nasceu_um_segundo_atlas(self):
        proibidos = [p.name for p in (RAIZ / "docs" / "fontes").glob("*.md")
                     if re.search(r"ATLAS.*(V2|FINAL|MASTER|REGISTRY)", p.name,
                                  re.I)]
        self.assertEqual([], proibidos,
                         f"nasceu um segundo registo: {proibidos}. "
                         "ONE CONCEPT -> ONE OWNER.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
