#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTES DO KNOW HOW VIVO v1 — escritos ANTES do programa.

Especificacao: KNOW-HOW-VIVO-ARQUITETURA-v1 (coordenador, 30/09/2026), §8.

    OS QUATRO DO PRONTO          PRONTO_1 … PRONTO_4
    OS CINCO CONTROLOS NEGATIVOS NEG_1 … NEG_5
    UM TESTE POR K               K1 … K8 (cada K tem de matar o seu mutante)

Corre com:   py know-how/vivo/test_knowhow.py
Mutantes:    py know-how/vivo/mutantes_knowhow.py

`KNOWHOW_ALVO` aponta para o ficheiro a testar. Por omissao e o `knowhow.py`
ao lado deste; o corredor de mutantes aponta-o para uma copia desligada.

Nenhum teste escreve no repositorio, no HANDOFF-VIVO real nem na pasta do LAB:
cada um trabalha numa raiz temporaria. O Know How legado e as leis sao LIDOS da
arvore real (so leitura), e o teste final confere que o legado ficou intacto.
"""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(AQUI))
ALVO = os.environ.get("KNOWHOW_ALVO") or os.path.join(AQUI, "knowhow.py")
LEGADO = os.path.join(REPO, "SINTONIA-EAME-KNOW-HOW.md")
LAB_JSONL = os.path.expanduser(
    "~/AppData/Local/hermes/profiles/sintonia-lab/lab/estudos/"
    "2026-09-30-KNOWHOW-MEMORIA/EVENTOS-LAB.jsonl")
EVENTOS_DO_RAMO = os.path.join(AQUI, "eventos")

sys.dont_write_bytecode = True


def _carregar(caminho):
    spec = importlib.util.spec_from_file_location("knowhow_sob_teste", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


KH = _carregar(ALVO)

# Os tres candidatos do dono (§8). O texto e o do proponente, como a
# arquitetura manda (§4): o titulo vem do §8, o corpo vem do LAB
# (MAPA-E-CANDIDATOS.md §4) ou, no KH-C2, da frase inteira do §8.
C1 = {"ID": "KH-C1", "TITULO": "Pronto no ramo não é funcionando",
      "TEXTO": "Capacidade só é operacional quando está na árvore que roda E "
               "ligada ao consumidor; PASS_TECNICO em ramo não conta.",
      "EVENTOS": ["MEM-LAB-20260930-03", "MEM-LAB-20260930-04"],
      "PROPOSTO_POR": "sintonia-lab",
      # a checagem de duplicata do LAB (MAPA-E-CANDIDATOS.md §4): «COMPLEMENTA
      # §222.2 e §216». O K5 so a aceita se a medida a puser acima do limiar.
      "ALVO_PROPOSTO": ["LEG-§222.2", "LEG-§216"]}
C2 = {"ID": "KH-C2", "TITULO": "Consertar o erro não garante recuperar o valor",
      "TEXTO": "Consertar o erro não garante recuperar o valor; meça a "
               "recuperação no mesmo universo antes de instalar.",
      "EVENTOS": ["MEM-LAB-20260930-01", "MEM-LAB-20260928-01",
                  "MEM-LAB-20260928-03"],
      "PROPOSTO_POR": "coordenador"}
C3 = {"ID": "KH-C3", "TITULO": "Data escrita no texto não é data do fato",
      "TEXTO": "Data no texto ≠ data do fato: tipar publicação/validade/ato/"
               "evento antes de contar.",
      "EVENTOS": ["MEM-LAB-20260928-02", "MEM-LAB-20260928-03"],
      "PROPOSTO_POR": "sintonia-lab"}


def _sha_ficheiro(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _evento(**kw):
    ev = {"SCHEMA": "MEMORY_EVENT/1", "DATA": "2026-09-30T18:00:00-03:00",
          "AGENTE_ORIGEM": "teste", "AREA": "KNOW_HOW", "TAGS": ["teste"],
          "ESPECIE": "FATO_MEDIDO", "FATO": "um facto de teste",
          "EVIDENCIA": ["git rev-parse HEAD"], "CONFIANCA": "GIT_MEDIDO",
          "STATUS": "ABERTO"}
    ev.update(kw)
    return ev


class Base(unittest.TestCase):
    """Uma raiz temporaria com a gaveta `know-how/vivo/` vazia."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="khv-")
        self.raiz = self.tmp
        os.makedirs(os.path.join(self.raiz, "know-how", "vivo"))
        self.handoff = os.path.join(self.tmp, "HANDOFF-TESTE.md")
        self.cfg = KH.Config(raiz=self.raiz, repo=REPO, legado=LEGADO,
                             handoff=self.handoff)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def vivo(self, *p):
        return os.path.join(self.raiz, "know-how", "vivo", *p)

    def cli(self, *args, entrada=None):
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1",
                   PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run(
            [sys.executable, ALVO, *args, "--raiz", self.raiz,
             "--repo", REPO, "--legado", LEGADO, "--handoff", self.handoff],
            capture_output=True, text=True, encoding="utf-8", env=env,
            input=entrada, timeout=300)

    def escrever(self, nome, obj):
        p = os.path.join(self.tmp, nome)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, ensure_ascii=False)
        return p

    def gravar_evento(self, ev):
        """Evento sintetico gravado pela porta oficial (validacao incluida)."""
        return KH.registrar(self.cfg, ev)

    def importar_lab(self):
        if os.path.exists(LAB_JSONL):
            KH.importar(self.cfg, LAB_JSONL)
        elif os.path.isdir(EVENTOS_DO_RAMO):
            os.makedirs(self.vivo("eventos"), exist_ok=True)
            for n in os.listdir(EVENTOS_DO_RAMO):
                shutil.copy(os.path.join(EVENTOS_DO_RAMO, n), self.vivo("eventos", n))
        else:
            self.skipTest("sem os eventos do LAB nesta maquina")
        # a evidencia dos eventos do LAB vive nesta maquina; sem ela o K3
        # bloqueia (e isso e o comportamento certo, nao um defeito)
        if not os.path.isdir(os.path.expanduser(
                "~/AppData/Local/hermes/profiles/sintonia-lab/lab/estudos")):
            self.skipTest("sem a evidencia do LAB nesta maquina")

    def consolidar(self, cand):
        return KH.consolidar_candidato(self.cfg, dict(cand))


# ════════════════════════════════════════════════════════════════════════════
# PRONTO 1 — registrar
# ════════════════════════════════════════════════════════════════════════════
class Pronto1Registrar(Base):

    def test_PRONTO_1a_registrar_arquivo_cria_evento_valido(self):
        ev = _evento(AGENTE_ORIGEM="sintonia-lab")
        ev.pop("SCHEMA")
        r = self.cli("registrar", "--arquivo", self.escrever("ev.json", ev))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        nomes = os.listdir(self.vivo("eventos"))
        self.assertEqual(len(nomes), 1)
        self.assertRegex(nomes[0], r"^MEM-LAB-\d{8}-\d{2}\.json$")
        with open(self.vivo("eventos", nomes[0]), encoding="utf-8") as f:
            gravado = json.load(f)
        self.assertEqual(gravado["SCHEMA"], "MEMORY_EVENT/1")
        self.assertEqual(gravado["ID"], nomes[0][:-5])
        self.assertEqual(KH.validar_evento(gravado), [])

    def test_PRONTO_1b_registrar_por_flags(self):
        r = self.cli("registrar", "--agente", "coordenador", "--area", "OPERACAO",
                     "--tags", "ramo,servico", "--especie", "FATO_MEDIDO",
                     "--fato", "o ramo X nao e ancestral da linha",
                     "--evidencia", "git merge-base --is-ancestor X Y",
                     "--confianca", "GIT_MEDIDO", "--status", "ABERTO")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertRegex(os.listdir(self.vivo("eventos"))[0],
                         r"^MEM-COORDENADOR-\d{8}-01\.json$")

    def test_PRONTO_1c_invalido_recusado_e_diz_o_campo(self):
        ev = _evento()
        ev.pop("CONFIANCA")
        r = self.cli("registrar", "--arquivo", self.escrever("ev.json", ev))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("CONFIANCA", r.stdout + r.stderr)
        self.assertFalse(os.path.isdir(self.vivo("eventos"))
                         and os.listdir(self.vivo("eventos")))

    def test_PRONTO_1d_area_fora_do_vocabulario_recusada(self):
        self.assertIn("AREA", " ".join(KH.validar_evento(_evento(AREA="COZINHA"))))
        self.assertIn("DATA", " ".join(KH.validar_evento(
            _evento(DATA="2026-09-30T18:00:00"))))  # sem fuso
        self.assertIn("EVIDENCIA", " ".join(KH.validar_evento(_evento(EVIDENCIA=[]))))

    def test_PRONTO_1e_dois_processos_nunca_se_sobrescrevem(self):
        n = 8
        procs = []
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
        for i in range(n):
            p = self.escrever(f"ev{i}.json", _evento(AGENTE_ORIGEM="sintonia-lab",
                                                     FATO=f"escritor numero {i}"))
            procs.append(subprocess.Popen(
                [sys.executable, ALVO, "registrar", "--arquivo", p, "--raiz", self.raiz,
                 "--repo", REPO], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env))
        rcs = [p.communicate(timeout=120) and p.returncode for p in procs]
        self.assertEqual(rcs, [0] * n)
        nomes = sorted(os.listdir(self.vivo("eventos")))
        self.assertEqual(len(nomes), n)
        fatos = set()
        for nm in nomes:
            with open(self.vivo("eventos", nm), encoding="utf-8") as f:
                fatos.add(json.load(f)["FATO"])
        self.assertEqual(fatos, {f"escritor numero {i}" for i in range(n)})

    def test_PRONTO_1f_mesmo_id_dois_processos_um_so_ganha(self):
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
        procs = []
        for i in range(4):
            p = self.escrever(f"ev{i}.json", _evento(ID="MEM-TESTE-20260930-07",
                                                     FATO=f"versao {i}"))
            procs.append(subprocess.Popen(
                [sys.executable, ALVO, "registrar", "--arquivo", p, "--raiz", self.raiz,
                 "--repo", REPO], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env))
        rcs = [p.communicate(timeout=120) and p.returncode for p in procs]
        self.assertEqual(sorted(rcs).count(0), 1, rcs)
        self.assertEqual(os.listdir(self.vivo("eventos")), ["MEM-TESTE-20260930-07.json"])

    def test_PRONTO_1g_importar_os_7_do_lab_sem_reescrever(self):
        if not os.path.exists(LAB_JSONL):
            self.skipTest("EVENTOS-LAB.jsonl nao existe nesta maquina")
        KH.importar(self.cfg, LAB_JSONL)
        with open(LAB_JSONL, "rb") as f:
            linhas = [l for l in f.read().split(b"\n") if l.strip()]
        self.assertEqual(len(linhas), 7)
        for i, bruto in enumerate(linhas, 1):
            original = json.loads(bruto.decode("utf-8"))
            with open(self.vivo("eventos", original["ID"] + ".json"), encoding="utf-8") as f:
                gravado = json.load(f)
            for k, v in original.items():          # nada reescrito, nada perdido
                self.assertEqual(gravado[k], v, f"{original['ID']}.{k}")
            extra = set(gravado) - set(original)
            self.assertTrue(extra <= {"SCHEMA", "IMPORTADO_DE", "TAGS", "AREA"}, extra)
            self.assertEqual(gravado["IMPORTADO_DE"]["SHA256_DA_LINHA"],
                             hashlib.sha256(bruto.rstrip(b"\r")).hexdigest())
            self.assertEqual(gravado["IMPORTADO_DE"]["LINHA"], i)
            self.assertEqual(KH.validar_evento(gravado), [])
        # idempotente: importar outra vez nao escreve nem falha
        antes = {n: _sha_ficheiro(self.vivo("eventos", n)) for n in os.listdir(self.vivo("eventos"))}
        KH.importar(self.cfg, LAB_JSONL)
        depois = {n: _sha_ficheiro(self.vivo("eventos", n)) for n in os.listdir(self.vivo("eventos"))}
        self.assertEqual(antes, depois)


# ════════════════════════════════════════════════════════════════════════════
# PRONTO 2 — buscar
# ════════════════════════════════════════════════════════════════════════════
def _texto_da_secao(item):
    """Oraculo do teste, independente do programa: as linhas do legado."""
    caminho = item["CAMINHO"]
    ini, fim = [int(x) for x in caminho.rsplit(":", 1)[1].split("-")]
    with open(LEGADO, encoding="utf-8") as f:
        linhas = f.read().split("\n")
    return "\n".join(linhas[ini - 1:fim]).lower()


DATAS = ("published_at", "published_time", "publication_time", "fact_time",
         "data de publica", "data da publica", "data do fato", "data do facto")


class Pronto2Buscar(Base):

    def setUp(self):
        super().setUp()
        self.importar_lab()
        self.r1 = self.consolidar(C1)
        KH.indexar(self.cfg)

    def buscar(self, termos, *extra):
        r = self.cli("buscar", termos, "--json", *extra)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return json.loads(r.stdout)

    def test_PRONTO_2a_arvores_branches_operacionais(self):
        res = self.buscar("árvores branches operacionais")
        ids = [x["ID"] for x in res]
        self.assertIn("LEG-§216", ids)
        self.assertIn("LEG-§222.2", ids)
        alvo = next(x for x in res if x["ID"] == "LEG-§222.2")
        self.assertIn("KH-C1", json.dumps(alvo.get("REFORCOS", []), ensure_ascii=False))
        for x in res:  # nada de datas
            self.assertFalse(any(d in x["TITULO"].lower() for d in
                                 ("data", "publica", "fact_time")), x["TITULO"])
            if x["ID"].startswith("LEG-"):
                t = _texto_da_secao(x)
                self.assertLess(sum(t.count(d) for d in DATAS), 2, x["ID"])

    def test_PRONTO_2b_data_publicacao_so_datas(self):
        res = self.buscar("data publicação")
        self.assertTrue(res)
        ids = [x["ID"] for x in res]
        for fora in ("LEG-§216", "LEG-§222.2", "LEG-§222.5", "LEG-§222"):
            self.assertNotIn(fora, ids)
        for x in res:
            if x["ID"].startswith("LEG-"):
                t = _texto_da_secao(x)
                self.assertGreaterEqual(sum(t.count(d) for d in DATAS), 2,
                                        f"{x['ID']} {x['TITULO']} nao e do tema datas")

    def test_PRONTO_2c_saida_curta_e_nunca_o_ficheiro(self):
        r = self.cli("buscar", "data publicação")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLess(len(r.stdout), 12000)
        self.assertIn("SINTONIA-EAME-KNOW-HOW.md:", r.stdout)
        r = self.cli("buscar", "data publicação", "--max", "2", "--json")
        self.assertLessEqual(len(json.loads(r.stdout)), 2)

    def test_PRONTO_2d_filtro_de_area(self):
        KH.consolidar_candidato(self.cfg, dict(C2))
        KH.indexar(self.cfg)
        res = self.buscar("consertar recuperar valor", "--area", "INTELLIGENCE")
        self.assertTrue(res)
        self.assertTrue(all(x["AREA"] == "INTELLIGENCE" for x in res))
        self.assertEqual(res[0]["ID"], "KH-0001")


# ════════════════════════════════════════════════════════════════════════════
# PRONTO 3 e 4 — os tres candidatos do dono
# ════════════════════════════════════════════════════════════════════════════
class Pronto34Candidatos(Base):

    def setUp(self):
        super().setUp()
        self.importar_lab()

    def test_PRONTO_3_kh_c1_reforca_o_legado(self):
        r = self.consolidar(C1)
        self.assertEqual(r["RESULTADO"], "REFORCO", r["K"])
        self.assertIn(r["ALVO"], ("LEG-§222.2", "LEG-§216"))
        self.assertEqual(r["K"]["K5"]["VEREDITO"], "DUPLICADO")
        self.assertFalse(os.path.isdir(self.vivo("conhecimento"))
                         and os.listdir(self.vivo("conhecimento")))
        KH.indexar(self.cfg)
        with open(self.vivo("legado", "SECOES.json"), encoding="utf-8") as f:
            sec = {s["ID"]: s for s in json.load(f)["SECOES"]}
        ref = sec[r["ALVO"]]["REFORCOS"]
        self.assertEqual(ref[0]["CANDIDATO"], "KH-C1")
        self.assertEqual(ref[0]["EVENTOS"], C1["EVENTOS"])

    def test_PRONTO_4a_kh_c2_vira_active_sem_mao_humana(self):
        r = self.consolidar(C2)
        self.assertEqual(r["RESULTADO"], "ACTIVE", r["K"])
        for k in ("K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8"):
            self.assertEqual(r["K"][k]["VEREDITO"], "PASS", (k, r["K"][k]))
        self.assertEqual(r["KH"], "KH-0001")
        with open(self.vivo("conhecimento", "KH-0001.json"), encoding="utf-8") as f:
            kh = json.load(f)
        self.assertEqual(kh["STATUS"], "ACTIVE")
        self.assertEqual(kh["TEXTO"], C2["TEXTO"])
        self.assertEqual(kh["ORIGEM"]["EVENTOS"], C2["EVENTOS"])
        self.assertEqual(kh["ORIGEM"]["CANDIDATO"], "KH-C2")

    def test_PRONTO_4b_kh_c3_relacionado_a_autoridade(self):
        r = self.consolidar(C3)
        self.assertEqual(r["RESULTADO"], "RELACIONADO_A_AUTORIDADE", r["K"])
        self.assertEqual(r["K"]["K7"]["VEREDITO"], "COBERTO")
        fontes = " ".join(a["FONTE"] for a in r["AUTORIDADE"])
        self.assertIn("AGENTS.md", fontes)
        self.assertFalse(os.path.isdir(self.vivo("conhecimento"))
                         and os.listdir(self.vivo("conhecimento")))

    def test_PRONTO_4c_ordem_dos_tres_nao_muda_o_resultado(self):
        res = [self.consolidar(c)["RESULTADO"] for c in (C3, C2, C1)]
        self.assertEqual(res, ["RELACIONADO_A_AUTORIDADE", "ACTIVE", "REFORCO"])

    def test_PRONTO_4e_pista_de_alvo_nao_forca_reforco(self):
        c = dict(C2, ALVO_PROPOSTO=["LEG-§222.2", "LEG-§216"])
        r = self.consolidar(c)
        self.assertEqual(r["RESULTADO"], "ACTIVE", r["K"]["K5"])
        sem = dict(C1)
        sem.pop("ALVO_PROPOSTO")
        sem["ID"] = "KH-C11"
        r = self.consolidar(sem)            # sem pista continua a perceber que existe
        self.assertEqual(r["RESULTADO"], "REFORCO", r["K"])

    def test_PRONTO_4d_candidato_ja_consolidado_nao_se_reescreve(self):
        self.consolidar(C2)
        with self.assertRaises(KH.Recusa):
            self.consolidar(C2)


# ════════════════════════════════════════════════════════════════════════════
# OS CINCO CONTROLOS NEGATIVOS (§8)
# ════════════════════════════════════════════════════════════════════════════
class Negativos(Base):

    def setUp(self):
        super().setUp()
        self.importar_lab()

    def test_NEG_1_so_relato_bloqueado(self):
        r = self.consolidar({"ID": "KH-C91", "TITULO": "Ramo que roda nao e o publicado",
                             "TEXTO": "Nunca trate a árvore publicada como a árvore que roda.",
                             "EVENTOS": ["MEM-LAB-20260930-04"], "PROPOSTO_POR": "teste"})
        self.assertEqual(r["RESULTADO"], "BLOQUEADO")
        self.assertEqual(r["K"]["K2"]["VEREDITO"], "FAIL")

    def test_NEG_2_lock_ocupada_as_1320_bloqueado_por_k4(self):
        r = self.consolidar({"ID": "KH-C92", "TITULO": "LOCK-PESADO ocupada",
                             "TEXTO": "LOCK-PESADO ocupada às 13:20",
                             "EVENTOS": ["MEM-LAB-20260930-03"], "PROPOSTO_POR": "teste"})
        self.assertEqual(r["RESULTADO"], "BLOQUEADO")
        self.assertEqual(r["K"]["K4"]["VEREDITO"], "FAIL")

    def test_NEG_3_contraria_publicacao_nao_vira_fact_time(self):
        r = self.consolidar({"ID": "KH-C93", "TITULO": "Publicação serve de data do fato",
                             "TEXTO": "A data de publicação vira fact time quando o texto "
                                      "não traz outra data.",
                             "EVENTOS": ["MEM-LAB-20260928-02"], "PROPOSTO_POR": "teste"})
        self.assertEqual(r["RESULTADO"], "CONFLITO_DE_AUTORIDADE", r["K"])
        self.assertEqual(r["K"]["K7"]["VEREDITO"], "CONTRARIA")
        with open(self.handoff, encoding="utf-8") as f:
            linha = f.read()
        self.assertIn("CONFLITO_DE_AUTORIDADE", linha)
        self.assertIn("KH-C93", linha)
        self.assertTrue(os.path.exists(self.vivo("candidatos", "KH-C93.json")))

    def test_NEG_4_nega_o_kh_0001(self):
        self.assertEqual(self.consolidar(C2)["KH"], "KH-0001")
        r = self.consolidar({"ID": "KH-C94", "TITULO": "Consertar o erro garante recuperar o valor",
                             "TEXTO": "Consertar o erro garante recuperar o valor; não é "
                                      "preciso medir a recuperação antes de instalar.",
                             "EVENTOS": ["MEM-LAB-20260930-01"], "PROPOSTO_POR": "teste"})
        self.assertEqual(r["RESULTADO"], "CONFLITO_KNOW_HOW", r["K"])
        self.assertEqual(r["K"]["K6"]["VEREDITO"], "FAIL")
        self.assertEqual(r["ALVO"], "KH-0001")
        with open(self.vivo("conhecimento", "KH-0001.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["STATUS"], "ACTIVE")   # nao sobrescreve
        with open(self.handoff, encoding="utf-8") as f:
            self.assertIn("CONFLITO_KNOW_HOW", f.read())

    def test_NEG_5_evento_sem_especie_recusado(self):
        ev = _evento()
        ev.pop("ESPECIE")
        antes = sorted(os.listdir(self.vivo("eventos")))
        r = self.cli("registrar", "--arquivo", self.escrever("ev.json", ev))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ESPECIE", r.stdout + r.stderr)
        self.assertEqual(sorted(os.listdir(self.vivo("eventos"))), antes)
        with self.assertRaises(KH.Recusa):
            KH.registrar(self.cfg, ev)
        self.assertIn("ESPECIE", " ".join(KH.validar_evento(_evento(ESPECIE=""))))
        self.assertIn("ESPECIE", " ".join(KH.validar_evento(_evento(ESPECIE="PALPITE"))))


# ════════════════════════════════════════════════════════════════════════════
# UM TESTE POR K (sinteticos, sem depender da evidencia do LAB)
# ════════════════════════════════════════════════════════════════════════════
class PorK(Base):

    def setUp(self):
        super().setUp()
        self.prova = os.path.join(self.tmp, "prova.txt")
        with open(self.prova, "w", encoding="utf-8") as f:
            f.write("prova\n")
        self.cfg.raizes_evidencia = [self.tmp]
        self.ev_bom = self.gravar_evento(_evento(
            AGENTE_ORIGEM="sintonia-lab", EVIDENCIA=[self.prova.replace("\\", "/")]))

    def cand(self, texto, eventos, cid):
        return self.consolidar({"ID": cid, "TITULO": texto[:60], "TEXTO": texto,
                                "EVENTOS": eventos, "PROPOSTO_POR": "teste"})

    REGRA = "Meça o universo inteiro antes de declarar o conserto; nunca confie no relatório."

    def test_K0_controlo_regra_boa_passa(self):
        r = self.cand(self.REGRA, [self.ev_bom], "KH-C80")
        self.assertEqual(r["RESULTADO"], "ACTIVE", r["K"])

    def test_K1_evento_citado_que_nao_existe(self):
        r = self.cand(self.REGRA, [self.ev_bom, "MEM-FANTASMA-20260930-01"], "KH-C81")
        self.assertEqual(r["RESULTADO"], "BLOQUEADO")
        self.assertEqual(r["K"]["K1"]["VEREDITO"], "FAIL")
        r = self.cand(self.REGRA, [], "KH-C82")
        self.assertEqual(r["K"]["K1"]["VEREDITO"], "FAIL")

    def test_K2_decisao_so_conta_do_dono_ou_coordenador_com_Dn(self):
        dec_bot = self.gravar_evento(_evento(AGENTE_ORIGEM="bot-luciano", ESPECIE="DECISAO",
                                             FATO="decidido D200", EVIDENCIA=[self.prova]))
        r = self.cand(self.REGRA, [dec_bot], "KH-C83")
        self.assertEqual(r["K"]["K2"]["VEREDITO"], "FAIL")
        dec_coord = self.gravar_evento(_evento(AGENTE_ORIGEM="coordenador", ESPECIE="DECISAO",
                                               FATO="decidido na D200", EVIDENCIA=[self.prova]))
        r = self.cand(self.REGRA, [dec_coord], "KH-C84")
        self.assertEqual(r["K"]["K2"]["VEREDITO"], "PASS", r["K"]["K2"])
        hip = self.gravar_evento(_evento(ESPECIE="HIPOTESE", EVIDENCIA=[self.prova]))
        r = self.cand(self.REGRA, [hip], "KH-C85")
        self.assertEqual((r["RESULTADO"], r["K"]["K2"]["VEREDITO"]), ("BLOQUEADO", "FAIL"))

    def test_K3_caminho_que_nao_existe_bloqueia(self):
        ev = self.gravar_evento(_evento(EVIDENCIA=[self.prova, "provas/nao/existe/NADA.md"]))
        r = self.cand(self.REGRA, [ev], "KH-C86")
        self.assertEqual((r["RESULTADO"], r["K"]["K3"]["VEREDITO"]), ("BLOQUEADO", "FAIL"))
        self.assertIn("NADA.md", r["K"]["K3"]["MOTIVO"])
        fraco = self.gravar_evento(_evento(EVIDENCIA=["alguém me disse"]))
        r = self.cand(self.REGRA, [fraco], "KH-C87")
        self.assertEqual(r["K"]["K3"]["VEREDITO"], "FAIL")
        sha = self.gravar_evento(_evento(EVIDENCIA=["commit 852ec0f0b"]))
        r = self.cand(self.REGRA, [sha], "KH-C88")
        self.assertEqual(r["K"]["K3"]["VEREDITO"], "PASS", r["K"]["K3"])

    def test_K4_estado_momentaneo_sem_regra_geral(self):
        r = self.cand("Espere a LOCK-PESADO ocupada agora soltar.", [self.ev_bom], "KH-C89")
        self.assertEqual(r["K"]["K8"]["VEREDITO"], "PASS", r["K"]["K8"])  # tem forma de regra
        self.assertEqual((r["RESULTADO"], r["K"]["K4"]["VEREDITO"]), ("BLOQUEADO", "FAIL"))
        r = self.cand("Sempre que a LOCK-PESADO estiver ocupada, espere; nunca a declare órfã.",
                      [self.ev_bom], "KH-C90")
        self.assertEqual(r["K"]["K4"]["VEREDITO"], "PASS", r["K"]["K4"])

    def test_K5_duplicado_reforca_em_vez_de_criar(self):
        self.assertEqual(self.cand(self.REGRA, [self.ev_bom], "KH-C95")["KH"], "KH-0001")
        ev2 = self.gravar_evento(_evento(EVIDENCIA=[self.prova], FATO="outra medida"))
        r = self.cand(self.REGRA, [ev2], "KH-C96")
        self.assertEqual((r["RESULTADO"], r["ALVO"]), ("REFORCO", "KH-0001"), r["K"])
        with open(self.vivo("conhecimento", "KH-0001.json"), encoding="utf-8") as f:
            kh = json.load(f)
        self.assertEqual(kh["REFORCOS"][0]["EVENTOS"], [ev2])
        self.assertEqual(sorted(os.listdir(self.vivo("conhecimento"))), ["KH-0001.json"])

    def test_K6_negacao_de_kh_active(self):
        self.cand(self.REGRA, [self.ev_bom], "KH-C97")
        r = self.cand("Não meça o universo inteiro antes de declarar o conserto; "
                      "sempre confie no relatório.", [self.ev_bom], "KH-C98")
        self.assertEqual((r["RESULTADO"], r["K"]["K6"]["VEREDITO"]),
                         ("CONFLITO_KNOW_HOW", "FAIL"), r["K"])

    def test_K7_autoridade(self):
        r = self.cand("Fonte do documento não vira local do fato: tipar o lugar antes de contar.",
                      [self.ev_bom], "KH-C99")
        self.assertEqual(r["K"]["K7"]["VEREDITO"], "COBERTO", r["K"]["K7"])
        r = self.cand("Publicação vira fact time sempre que faltar outra data.",
                      [self.ev_bom], "KH-C100")
        self.assertEqual(r["K"]["K7"]["VEREDITO"], "CONTRARIA", r["K"]["K7"])

    def test_K7_sem_fonte_de_autoridade_e_nao_sei(self):
        self.cfg.decisoes = os.path.join(self.tmp, "nao-existe.md")
        r = self.cand(self.REGRA, [self.ev_bom], "KH-C101")
        self.assertEqual((r["RESULTADO"], r["K"]["K7"]["VEREDITO"]), ("BLOQUEADO", "NAO_SEI"))

    def test_K8_narracao_nao_e_aprendizado(self):
        r = self.cand("O Scrap commitou c38610e0c direto na worktree de serviço em 30/09.",
                      [self.ev_bom], "KH-C102")
        self.assertEqual(r["K"]["K4"]["VEREDITO"], "PASS", r["K"]["K4"])
        self.assertEqual((r["RESULTADO"], r["K"]["K8"]["VEREDITO"]), ("BLOQUEADO", "FAIL"))

    def test_consolidar_sem_argumentos_so_usa_aprendizado_proposto(self):
        self.gravar_evento(_evento(EVIDENCIA=[self.prova], APRENDIZADO_PROPOSTO=self.REGRA))
        feitos = KH.consolidar(self.cfg)
        self.assertEqual(len(feitos), 1)       # o ev_bom nao traz texto: nao gera candidato
        self.assertEqual(feitos[0]["RESULTADO"], "ACTIVE", feitos[0]["K"])
        self.assertEqual(KH.consolidar(self.cfg), [])   # evento com candidato nao volta

    def test_substituir_exige_decisao_e_nunca_apaga(self):
        a = self.cand(self.REGRA, [self.ev_bom], "KH-C103")["KH"]
        ev = self.gravar_evento(_evento(EVIDENCIA=[self.prova], FATO="outra coisa medida"))
        b = self.cand("Nunca reaproveite o rótulo de um frasco da bancada; guarde cada "
                      "frasco com o seu.", [ev], "KH-C104")["KH"]
        with self.assertRaises(KH.Recusa):
            KH.substituir(self.cfg, a, b, self.ev_bom)       # FATO_MEDIDO nao decide
        dec = self.gravar_evento(_evento(AGENTE_ORIGEM="coordenador", ESPECIE="DECISAO",
                                         FATO="D201: a regra B substitui a A",
                                         EVIDENCIA=[self.prova]))
        KH.substituir(self.cfg, a, b, dec)
        with open(self.vivo("conhecimento", a + ".json"), encoding="utf-8") as f:
            ka = json.load(f)
        with open(self.vivo("conhecimento", b + ".json"), encoding="utf-8") as f:
            kb = json.load(f)
        self.assertEqual((ka["STATUS"], ka["SUBSTITUIDO_POR"]), ("SUPERSEDED", b))
        self.assertEqual((kb["STATUS"], kb["SUBSTITUI"]), ("ACTIVE", a))
        self.assertEqual(ka["TEXTO"], self.REGRA)


# ════════════════════════════════════════════════════════════════════════════
# O INDICE E O LEGADO
# ════════════════════════════════════════════════════════════════════════════
class Indice(Base):

    def test_inventario_das_secoes_do_legado(self):
        KH.indexar(self.cfg)
        with open(self.vivo("legado", "SECOES.json"), encoding="utf-8") as f:
            d = json.load(f)
        sec = d["SECOES"]
        ids = [s["ID"] for s in sec]
        self.assertEqual(len(ids), len(set(ids)))
        # «## 2026-09-09» e uma data dentro do §40, nao a seccao 2026.09
        self.assertEqual([i for i in ids if not re.match(r"^LEG-§\d{1,3}(\.\d+)?$", i)], [])
        topo = [s for s in sec if "." not in s["ID"]]
        self.assertEqual(len(topo), 218)
        por_id = {s["ID"]: s for s in sec}
        self.assertTrue(por_id["LEG-§222.2"]["TITULO"].startswith("Motor pronto"))
        self.assertIn("§216 ·", por_id["LEG-§216"]["TITULO_ORIGINAL"])
        with open(LEGADO, encoding="utf-8") as f:
            linhas = f.read().split("\n")
        for s in (por_id["LEG-§216"], por_id["LEG-§222.2"], sec[0], sec[-1]):
            texto = "\n".join(linhas[s["LINHA_INICIO"] - 1:s["LINHA_FIM"]])
            self.assertEqual(hashlib.sha256(texto.encode("utf-8")).hexdigest(), s["SHA256"])
        self.assertTrue(all(s["STATUS"] in ("ACTIVE", "SUPERSEDED") for s in sec))
        self.assertTrue(any(s.get("SUPERSEDED_INFERIDO") for s in sec))

    def test_indice_e_regeravel_byte_a_byte(self):
        KH.indexar(self.cfg)
        a = _sha_ficheiro(self.vivo("INDICE.json")), _sha_ficheiro(self.vivo("legado", "SECOES.json"))
        os.remove(self.vivo("INDICE.json"))
        KH.indexar(self.cfg)
        b = _sha_ficheiro(self.vivo("INDICE.json")), _sha_ficheiro(self.vivo("legado", "SECOES.json"))
        self.assertEqual(a, b)
        with open(self.vivo("INDICE.json"), encoding="utf-8") as f:
            it = json.load(f)["ITENS"][0]
        for campo in ("ID", "TITULO", "AREA", "TAGS", "ENTIDADES", "STATUS", "VALIDADE",
                      "ORIGEM", "RELACOES", "CAMINHO"):
            self.assertIn(campo, it)

    def test_zz_legado_intacto(self):
        antes = _sha_ficheiro(LEGADO)
        KH.indexar(self.cfg)
        self.assertEqual(_sha_ficheiro(LEGADO), antes)
        out = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--",
                              "SINTONIA-EAME-KNOW-HOW.md"], capture_output=True, text=True)
        self.assertEqual(out.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
