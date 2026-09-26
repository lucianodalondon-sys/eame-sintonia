#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUATRO-CHAVES-NA-SALA (D58) — as quatro chaves atravessam o contrato e pousam.

D29 pede CULTURA × REGIÃO DO FATO × FASE × JANELA. A régua T1 já lê cultura e
fase (51/51 boletins de referência) e as duas morriam na fronteira: o READY
tinha 19 campos e a Sala 19 sítios, nenhum para isto. A D58 acrescenta:

  · `JANELA_DECLARADA` no READY (dono: `admissao.janela_declarada()`), com a
    proveniência de cada chave (`VEIO_DE`, `BASE`);
  · a coluna `sala_de_espera.janela_declarada`, que vive na 033 ÚNICA da
    produção (`033_a_sala_guarda_a_base_as_chaves_e_as_revisoes.sql`, já na
    Sala real) — esta linha só a lê e escreve, e o registo «não medido» do dono
    tem de bater byte a byte com o default dela.

Duas baterias:

  1. `OContratoLevaAsQuatroChaves` — sem banco, corre em qualquer lado.
  2. `ASalaGuardaAsQuatroChaves` — contra um PostgreSQL 16 DESCARTÁVEL, que nasce
     num `initdb` próprio numa pasta temporária e numa porta livre, e morre no
     fim (o mesmo `ensaio_offline.Base` de `test_sala_idempotente_por_documento`).
     As migrations entram pela cadeia canónica (`motor/cadeia_canonica.sh`).
     NUNCA a Sala real: o endereço é conferido antes de qualquer escrita.

Sem binários do Postgres, a 2.ª bateria SALTA e diz qual falta — um teste que
precisa de banco e não o tem não é um teste que passa. Com
`QUATRO_CHAVES_EXIGIR_BANCO=1` (o CI), faltar o banco REPROVA.

Os binários procuram-se por esta ordem: `SINTONIA_PG_BIN`; o Postgres portátil
do dono (`~/orca/pgtmp/pgsql/bin`); `pg_config --bindir`;
`/usr/lib/postgresql/<versão>/bin`. ⚠️ `initdb` recusa correr como root.
"""
import glob
import hashlib
import importlib.util
import io
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
for g in (str(RAIZ), str(RAIZ / "admissao")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas                          # noqa: E402,F401
import admissao as A                     # noqa: E402
import sala_de_espera as espera          # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

#: A 033 UNICA da producao (bancada MIGRACAO-SALA), ja aplicada na Sala real.
#: Esta linha NAO tem migration propria: a coluna `janela_declarada` e dela.
MIGRATION = RAIZ / "supabase" / "migrations" / "033_a_sala_guarda_a_base_as_chaves_e_as_revisoes.sql"
NAO_SEI = A.AUSENCIA  # «NAO SEI», a ausência do contrato de saída

BOLETIM_T1 = (
    "Bollettino tecnico vite. Fase di fioritura in corso nei vigneti di collina. "
    "Superata la soglia di intervento per infestazione di tignoletta: si consiglia "
    "il trattamento fitosanitario entro la settimana.")


def _achar_pg_bin():
    """A pasta dos binários do Postgres, ou `None` com o motivo."""
    ext = ".exe" if os.name == "nt" else ""
    candidatos = []
    if os.environ.get("SINTONIA_PG_BIN"):
        candidatos.append(Path(os.environ["SINTONIA_PG_BIN"]))
    candidatos.append(E.PG_BIN)
    try:
        r = subprocess.run(["pg_config", "--bindir"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            candidatos.append(Path(r.stdout.strip()))
    except OSError:
        pass
    candidatos += [Path(p) for p in sorted(glob.glob("/usr/lib/postgresql/*/bin"), reverse=True)]
    for c in candidatos:
        if all((c / (n + ext)).exists() for n in ("initdb", "pg_ctl", "psql")):
            return c, ""
    return None, ("FALTA: binarios do PostgreSQL (initdb, pg_ctl, psql). Procurados em: %s"
                  % ", ".join(str(c) for c in candidatos))


PG_BIN, PORQUE_SEM_PG = _achar_pg_bin()
if PG_BIN is not None:
    E.PG_BIN = PG_BIN        # `Base.exe()` le o global do modulo na hora
if PG_BIN is not None and not shutil.which("bash"):
    PG_BIN, PORQUE_SEM_PG = None, "FALTA: bash (a cadeia canonica e um script bash)"
if PG_BIN is not None and hasattr(os, "geteuid") and os.geteuid() == 0:
    PG_BIN, PORQUE_SEM_PG = None, ("initdb recusa correr como root: correr este "
                                   "teste com um utilizador sem privilegios")
EXIGIR = os.environ.get("QUATRO_CHAVES_EXIGIR_BANCO") == "1"


class _BaseComSocketProprio(E.Base):
    """`ensaio_offline.Base`, com o socket unix na pasta do PROPRIO banco.

    Medido no CI (run 36135906165): o `initdb` passou e o `pg_ctl start` caiu —
    o socket por omissao do Postgres do Debian/Ubuntu e `/var/run/postgresql`,
    que so o utilizador `postgres` escreve. Reproduzido aqui com um utilizador
    sem privilegios. O `Base` partilhado nao se muda: e dos outros testes.
    """

    def subir(self, arvore, env):
        subprocess.run([self.exe("initdb"), "-D", str(self.pasta), "-U", "postgres",
                        "--auth=trust", "-E", "UTF8", "--no-sync"], check=True,
                       capture_output=True)
        # a diferenca para o `Base`: `-k` poe o socket ao lado dos dados
        subprocess.run([self.exe("pg_ctl"), "-D", str(self.pasta), "-o",
                        "-p %d -h 127.0.0.1 -k %s" % (self.porto, self.pasta.parent),
                        "-l", str(self.pasta.parent / "servidor.log"), "-w", "start"],
                       check=True, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([self.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1", "-c",
                        "create database sala_italia;",
                        "postgresql://postgres@127.0.0.1:%d/postgres" % self.porto],
                       check=True, capture_output=True)
        r = subprocess.run([shutil.which("bash") or "bash", "motor/cadeia_canonica.sh",
                            "migrations", self.url], cwd=str(arvore), env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        passes = [l for l in r.stdout.splitlines() if l.startswith("MIGRATION_") and "=PASS" in l]
        return {"CODIGO": r.returncode, "MIGRATIONS_PASS": len(passes),
                "SAIDA": r.stdout[-600:], "ERRO": r.stderr[-400:]}


def _decidido(texto=BOLETIM_T1, universo="T1", **extra):
    item = {"texto": texto, "source_id": "IT-T1-900", "id": "derived:qc-1",
            "artifact_type": "DERIVED", "parent_sha256": "a" * 64}
    item.update(extra)
    return item, A.decidir(item, universo, corrida="RUN-QC")


def _default_da_migration():
    s = MIGRATION.read_text(encoding="utf-8")
    m = re.search(r"add column if not exists janela_declarada json not null\s+"
                  r"default '(.*?)'::json;", s, re.S)
    return m.group(1) if m else None


# ═════════════════════════════════════════════════════════════════════════
# 1 · SEM BANCO — o contrato
# ═════════════════════════════════════════════════════════════════════════
class OContratoLevaAsQuatroChaves(unittest.TestCase):

    def test_o_ready_leva_a_janela_declarada(self):
        item, d = _decidido(fact_location="Valpolicella",
                            fact_location_basis="declarado no boletim")
        u = A.pronto_para_inteligencia(item, d)
        self.assertIn("JANELA_DECLARADA", u)
        self.assertEqual(tuple(u), espera.CAMPOS_READY)
        self.assertEqual(u["JANELA_DECLARADA"], A.janela_para_o_ready(item, d))

    def test_cada_chave_diz_de_onde_veio(self):
        item, d = _decidido(fact_location="Valpolicella",
                            fact_location_basis="declarado no boletim")
        j = A.pronto_para_inteligencia(item, d)["JANELA_DECLARADA"]
        self.assertEqual(set(j), set(A.QUATRO_CHAVES) | {"PRECISAO", "TEMPO_RELATIVO", "ORIGEM"})
        for c in A.QUATRO_CHAVES:
            self.assertTrue({"VALOR", "VEIO_DE", "BASE"} <= set(j[c]), c)
        self.assertIn("vite", j["CULTURA"]["VALOR"])
        self.assertIn("decisao.evidencia.cultura", j["CULTURA"]["VEIO_DE"])
        self.assertIn("T1", j["CULTURA"]["BASE"])
        self.assertEqual(j["FASE"]["VEIO_DE"], "decisao.evidencia.palavras")
        self.assertEqual(j["REGIAO_DO_FATO"]["VALOR"], "Valpolicella")
        self.assertEqual(j["REGIAO_DO_FATO"]["VEIO_DE"], "item.fact_location")
        self.assertEqual(j["REGIAO_DO_FATO"]["BASE"], "declarado no boletim")
        self.assertEqual(j["JANELA"]["VALOR"], NAO_SEI)
        self.assertEqual(j["ORIGEM"]["UNIVERSO"], "T1")

    def test_os_tempos_nao_viajam_duas_vezes(self):
        item, d = _decidido(published_at="2026-05-10")
        u = A.pronto_para_inteligencia(item, d)
        self.assertNotIn("TEMPOS", u["JANELA_DECLARADA"])
        self.assertEqual(u["PUBLISHED_AT"], "2026-05-10")

    def test_a_regiao_da_fonte_nao_vira_regiao_do_fato(self):
        item, d = _decidido(source_location="Veneto")
        u = A.pronto_para_inteligencia(item, d)
        self.assertEqual(u["SOURCE_LOCATION"], "Veneto")
        self.assertEqual(u["JANELA_DECLARADA"]["REGIAO_DO_FATO"]["VALOR"], NAO_SEI)
        self.assertEqual(u["JANELA_DECLARADA"]["REGIAO_DO_FATO"]["VEIO_DE"], NAO_SEI)

    def test_a_ausencia_e_a_do_contrato_e_nao_o_resultado_da_porta(self):
        """`NAO_SEI` (com _) é um RESULTADO da porta; a Sala guardá-lo-ia como valor."""
        item = {"texto": "Ensaio de campo publicado con DOI", "id": "derived:qc-9",
                "source_id": "IT-T10-022", "fact_time": "2026-05-02"}
        d = A.decidir(item, "T5", corrida="RUN-QC")
        self.assertEqual(d.resultado, A.SIM, d.motivo)
        j = A.pronto_para_inteligencia(item, d)["JANELA_DECLARADA"]
        for c in A.QUATRO_CHAVES:
            for campo in ("VALOR", "VEIO_DE", "BASE"):
                self.assertEqual(j[c][campo], NAO_SEI, (c, campo))
                self.assertNotEqual(j[c][campo], A.NAO_SEI, (c, campo))

    # ── D62 · nada e obrigatorio; a precisao conta; data relativa nao vira fato ──
    def test_d62_a_precisao_conta_o_que_ha_e_nao_julga(self):
        item, d = _decidido(fact_location="Valpolicella",
                            fact_location_basis="declarado no boletim",
                            published_at="2026-05-10")
        p = A.pronto_para_inteligencia(item, d)["JANELA_DECLARADA"]["PRECISAO"]
        self.assertEqual(p, {"CHAVES_COM_VALOR": 3, "FACT_TIME": NAO_SEI,
                             "PUBLISHED_AT": "DECLARADO"})
        item, d = _decidido(fact_time="2026-05-08")
        p = A.pronto_para_inteligencia(item, d)["JANELA_DECLARADA"]["PRECISAO"]
        self.assertEqual((p["CHAVES_COM_VALOR"], p["FACT_TIME"], p["PUBLISHED_AT"]),
                         (2, "DECLARADO", NAO_SEI))

    def test_d62_sem_data_nem_lugar_o_item_continua_pronto(self):
        """Falta de dado nunca reprova: o READY sai, com a precisao em baixo."""
        item, d = _decidido()
        u = A.pronto_para_inteligencia(item, d)
        self.assertEqual(u["FACT_TIME"], NAO_SEI)
        self.assertEqual(u["PUBLISHED_AT"], NAO_SEI)
        self.assertEqual(u["JANELA_DECLARADA"]["PRECISAO"]["FACT_TIME"], NAO_SEI)

    # ── DA-6: FACT_TIME a partir do texto tem UM dono, o extrator lugar-fato-v1 ──
    def _da6(self, frase, **extra):
        base = {"published_at": "2026-05-13", "published_at_basis": "cabecalho do boletim"}
        base.update(extra)
        item, d = _decidido(texto=BOLETIM_T1 + " " + frase, **base)
        return A.pronto_para_inteligencia(item, d)

    def test_da6_data_relativa_fica_evidencia_e_nao_escreve_fact_time(self):
        for frase in ("Ieri le catture sono aumentate.",
                      "L'altro ieri le catture sono aumentate.",
                      "La settimana scorsa le catture sono aumentate.",
                      "Il mese scorso le catture sono aumentate.",
                      "Oggi le catture sono aumentate."):
            u = self._da6(frase)
            self.assertEqual((u["FACT_TIME"], u["FACT_TIME_BASIS"]), (NAO_SEI, NAO_SEI), frase)
            self.assertEqual(u["PUBLISHED_AT"], "2026-05-13")
            j = u["JANELA_DECLARADA"]
            self.assertEqual(j["PRECISAO"]["FACT_TIME"], NAO_SEI, frase)
            self.assertNotEqual(j["TEMPO_RELATIVO"]["EXPRESSOES"], NAO_SEI, frase)
            # `CONTA` existe (o default vivo da 033 unica tem-na) e e SEMPRE NAO SEI
            # aqui: a conta e do extrator (TEMPO_LUGAR_EVIDENCIA.FACT_TIME_CALCULO)
            self.assertEqual(j["TEMPO_RELATIVO"]["CONTA"], NAO_SEI, frase)
            self.assertIn("lugar-fato-v1", j["TEMPO_RELATIVO"]["LEI"])

    def test_da6_o_fact_time_do_extrator_passa_tal_e_qual(self):
        """O que o dono (lugar-fato-v1) pos no item atravessa sem ser tocado."""
        u = self._da6("Ieri le catture sono aumentate.", fact_time="2026-05-12",
                      fact_time_basis="lugar-fato-v1: 'ieri' sobre a publicacao")
        self.assertEqual((u["FACT_TIME"], u["FACT_TIME_BASIS"]),
                         ("2026-05-12", "lugar-fato-v1: 'ieri' sobre a publicacao"))
        self.assertEqual(u["JANELA_DECLARADA"]["PRECISAO"]["FACT_TIME"], "DECLARADO")

    def test_da6_so_o_extrator_do_fato_escreve_fact_time(self):
        """Prova ESTRUTURAL: no contrato, FACT_TIME e FACT_TIME_BASIS so vem do
        proprio item (`fact_time`/`fact_time_basis`), e nenhum codigo desta porta
        nem da Sala escreve `fact_time` num item. Quem o escreve e o extrator."""
        import ast
        fonte = (RAIZ / "admissao" / "admissao.py").read_text(encoding="utf-8")
        arv = ast.parse(fonte)
        f = next(n for n in arv.body if isinstance(n, ast.FunctionDef)
                 and n.name == "pronto_para_inteligencia")
        d = next(n for n in ast.walk(f) if isinstance(n, ast.Dict)
                 and any(isinstance(k, ast.Constant) and k.value == "FACT_TIME" for k in n.keys))
        valores = {k.value: ast.unparse(v) for k, v in zip(d.keys, d.values)
                   if isinstance(k, ast.Constant)}
        self.assertEqual(valores["FACT_TIME"], "item.get('fact_time') or AUSENCIA")
        self.assertEqual(valores["FACT_TIME_BASIS"], "_ou_nao_sei('fact_time_basis')")
        # e nenhuma ESCRITA de `fact_time` com valor (fora do exemplo do __main__):
        # `x["fact_time"] = ...`, `.setdefault/.update("fact_time")`, `fact_time=...`,
        # ou um dict com `"fact_time": <algo que nao seja NAO SEI>`
        for rel in ("admissao/admissao.py", "admissao/sala_de_espera.py"):
            s = (RAIZ / rel).read_text(encoding="utf-8")
            # (`RELATIVA_A_PUBLICACAO` pode aparecer: a completude da producao LE
            # a base que o extrator escreveu. Ler nao e escrever — a prova e a
            # de baixo, sobre ESCRITAS.)
            arv = ast.parse(s)
            demo = [n for n in arv.body if isinstance(n, ast.If)
                    and "__main__" in ast.unparse(n.test)]
            # `CAMPOS_REVISIVEIS` (Sala, 033 unica) e um mapa de NOMES DE COLUNA
            # (campo -> coluna da base): diz o que se pode rever, nao escreve nada.
            revisiveis = [n for n in arv.body if isinstance(n, ast.Assign)
                          and any(getattr(t, "id", "") == "CAMPOS_REVISIVEIS" for t in n.targets)]
            no_demo = {id(x) for n in demo + revisiveis for x in ast.walk(n)}
            escritas = []
            for n in ast.walk(arv):
                if id(n) in no_demo:
                    continue
                if (isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store)
                        and ast.unparse(n.slice).strip("'\"") == "fact_time"):
                    escritas.append(ast.unparse(n))
                if isinstance(n, ast.Call) and any(k.arg == "fact_time" for k in n.keywords):
                    escritas.append(ast.unparse(n))
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and n.func.attr in ("setdefault", "update") and n.args
                        and isinstance(n.args[0], ast.Constant) and n.args[0].value == "fact_time"):
                    escritas.append(ast.unparse(n))
                if isinstance(n, ast.Dict):
                    for k, v in zip(n.keys, n.values):
                        if (isinstance(k, ast.Constant) and k.value == "fact_time"
                                and not (isinstance(v, ast.Constant) and v.value == NAO_SEI)):
                            escritas.append(ast.unparse(n)[:120])
            self.assertEqual([], escritas, "%s escreve fact_time" % rel)

    def test_d62_sem_expressao_relativa_fica_nao_sei(self):
        item, d = _decidido()
        t = A.pronto_para_inteligencia(item, d)["JANELA_DECLARADA"]["TEMPO_RELATIVO"]
        self.assertEqual((t["EXPRESSOES"], t["VEIO_DE"]), (NAO_SEI, NAO_SEI))

    def test_o_default_da_033_e_o_registo_do_dono_byte_a_byte(self):
        self.assertEqual(
            _default_da_migration(),
            json.dumps(A.JANELA_NAO_MEDIDA, ensure_ascii=False, sort_keys=True))

    def test_o_registo_nao_medido_diz_nao_sei_nas_quatro(self):
        for c in A.QUATRO_CHAVES:
            self.assertEqual(A.JANELA_NAO_MEDIDA[c],
                             {"VALOR": NAO_SEI, "VEIO_DE": NAO_SEI, "BASE": NAO_SEI})
        self.assertIn("033", A.JANELA_NAO_MEDIDA["ORIGEM"]["PORQUE"])
        # D62: nos antigos a precisao e NAO SEI — nunca 0, que diria «mediu-se»
        self.assertEqual(set(A.JANELA_NAO_MEDIDA["PRECISAO"].values()), {NAO_SEI})
        self.assertEqual(A.JANELA_NAO_MEDIDA["TEMPO_RELATIVO"]["EXPRESSOES"], NAO_SEI)

# ═════════════════════════════════════════════════════════════════════════
# 2 · CONTRA UM POSTGRES DESCARTÁVEL
# ═════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(PG_BIN is not None or EXIGIR, PORQUE_SEM_PG)
class ASalaGuardaAsQuatroChaves(unittest.TestCase):

    RUNS = ("QC-R1", "QC-R2", "QC-R3", "QC-R4", "QC-R5", "QC-R6", "QC-R7", "QC-R9")

    @classmethod
    def setUpClass(cls):
        if PG_BIN is None:
            raise AssertionError("QUATRO_CHAVES_EXIGIR_BANCO=1 e " + PORQUE_SEM_PG)
        cls.pasta = Path(tempfile.mkdtemp(prefix="quatro-chaves-sala-"))
        cls.base = _BaseComSocketProprio(cls.pasta / "pg")
        cls._amb = dict(os.environ)
        cls.env = {**os.environ, "PATH": str(PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
        # ⚠️ NUNCA A SALA REAL. O endereco e o do postmaster que ESTE teste
        # levanta, numa porta livre, com os dados numa pasta temporaria.
        assert cls.base.url == "postgresql://postgres@127.0.0.1:%d/sala_italia" % cls.base.porto
        assert str(cls.base.pasta).startswith(tempfile.gettempdir())
        try:
            r = cls.base.subir(RAIZ, cls.env)
            cls.subida = r
            if r["CODIGO"] != 0:
                raise AssertionError("a cadeia de migrations falhou: %s %s"
                                     % (r["SAIDA"], r["ERRO"]))
            for nome in ("SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL"):
                os.environ.pop(nome, None)
            os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES",
                               "SINTONIA_SALA_DSN": cls.base.url,
                               "SINTONIA_PSQL_EXE": cls.base.exe("psql")})
            for run in cls.RUNS:
                cls.sql("insert into collection_run (run_id, platform, started_at, "
                        "rule_version) values ('%s', 'teste', now(), 'teste')" % run)
        except BaseException:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        os.environ.clear()
        os.environ.update(cls._amb)
        cls.base.descer()
        shutil.rmtree(cls.pasta, ignore_errors=True)

    # ── ferramentas ────────────────────────────────────────────────────
    @classmethod
    def sql(cls, q, falhar=True):
        r = subprocess.run([cls.base.exe("psql"), "-X", "-q", "-At", "-F", "\x1f",
                            "-v", "ON_ERROR_STOP=1", "-c", q, cls.base.url],
                           capture_output=True, text=True, encoding="utf-8")
        if falhar and r.returncode != 0:
            raise AssertionError("psql falhou: %s" % r.stderr)
        return r

    def linhas(self, q):
        return [l.split("\x1f") for l in self.sql(q).stdout.splitlines() if l.strip()]

    def cadeia(self):
        return subprocess.run(["bash", "motor/cadeia_canonica.sh", "migrations", self.base.url],
                              cwd=str(RAIZ), env=self.env, capture_output=True, text=True)

    def colunas(self):
        return {l[0]: l for l in self.linhas(
            "select column_name, data_type, is_nullable from information_schema.columns "
            "where table_schema='public' and table_name='sala_de_espera'")}

    def unidade(self, texto=BOLETIM_T1, universo="T1", item_id="derived:qc-1",
                corrida="RUN-QC", **extra):
        item = {"texto": texto, "source_id": "IT-T1-900", "id": item_id,
                "artifact_type": "DERIVED", "parent_sha256": "a" * 64}
        item.update(extra)
        d = A.decidir(item, universo, corrida=corrida)
        self.assertEqual(d.resultado, A.SIM, d.motivo)
        return A.pronto_para_inteligencia(item, d)

    # ── 1 · subiu ──────────────────────────────────────────────────────
    def test_1_a_033_subiu_pela_cadeia(self):
        col = self.colunas()["janela_declarada"]
        self.assertEqual((col[1], col[2]), ("json", "NO"))
        self.assertEqual(self.linhas(
            "select count(*) from pg_constraint where conname = "
            "'janela_declara_as_quatro_chaves'"), [["1"]])
        sha = hashlib.sha256(MIGRATION.read_bytes()).hexdigest()
        self.assertEqual(self.linhas(
            "select resultado, sha256 from schema_migracao where versao = '033'"),
            [["APLICADA", sha]])

    def test_2_a_cadeia_outra_vez_nao_estraga(self):
        r = self.cadeia()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("MIGRATION_033=SKIP (ja no livro-razao) HASH=MATCH", r.stdout)

    # ── 3 · as quatro chaves gravam e leem ─────────────────────────────
    def test_3_item_com_as_quatro_chaves_grava_e_le(self):
        # (a) o caminho real: a porta T1 le cultura e fase; o coletor trouxe a regiao
        # (a CORRIDA do READY volta do `run_id`: por isso a corrida e a do pouso)
        real = self.unidade(item_id="derived:qc-real", corrida="QC-R1",
                            fact_location="Valpolicella",
                            fact_location_basis="declarado no boletim")
        # (b) as QUATRO preenchidas. A regua hoje nao extrai JANELA; isto prova que
        #     a SALA a guarda quando alguem a trouxer — guardar nao e extrair.
        cheia = self.unidade(item_id="derived:qc-cheia", corrida="QC-R1",
                             fact_location="Trentino",
                             fact_location_basis="declarado no boletim")
        cheia["JANELA_DECLARADA"]["JANELA"] = {
            "VALOR": {"INICIO": "2026-05-20", "FIM": "2026-06-10", "SAFRA": "2026"},
            "VEIO_DE": "teste: registo escrito a mao", "BASE": "teste"}
        r = espera.pousar("QC-R1", [real, cheia])
        self.assertEqual((r["ESTADO"], r["INSERIDAS"]), (espera.POUSOU, 2))
        lido = espera.ler("QC-R1")["ITENS"]
        self.assertEqual(lido, [real, cheia])
        self.assertEqual(tuple(lido[0]), espera.CAMPOS_READY)
        j = lido[0]["JANELA_DECLARADA"]
        self.assertIn("vite", j["CULTURA"]["VALOR"])
        self.assertNotEqual(j["FASE"]["VALOR"], NAO_SEI)
        self.assertEqual(j["REGIAO_DO_FATO"]["VALOR"], "Valpolicella")
        # e o banco responde por SQL, sem passar pelo dono
        self.assertEqual(self.linhas(
            "select janela_declarada #>> '{REGIAO_DO_FATO,VALOR}', "
            "janela_declarada #>> '{JANELA,VALOR,SAFRA}' from sala_de_espera "
            "where run_id = 'QC-R1' order by ordem"),
            [["Valpolicella", ""], ["Trentino", "2026"]])

    def test_4_item_sem_chaves_fica_nao_sei(self):
        u = self.unidade(texto="Ensaio de campo publicado con DOI", universo="T5",
                         item_id="derived:qc-t5", fact_time="2026-05-02")
        espera.pousar("QC-R2", [u])
        j = espera.ler("QC-R2")["ITENS"][0]["JANELA_DECLARADA"]
        for c in A.QUATRO_CHAVES:
            self.assertEqual(j[c]["VALOR"], NAO_SEI, c)
            self.assertEqual(j[c]["VEIO_DE"], NAO_SEI, c)

    def test_5_a_regiao_da_fonte_nao_entra_como_regiao_do_fato(self):
        u = self.unidade(item_id="derived:qc-veneto", source_location="Veneto")
        espera.pousar("QC-R3", [u])
        l = espera.ler("QC-R3")["ITENS"][0]
        self.assertEqual(l["SOURCE_LOCATION"], "Veneto")
        self.assertEqual(l["JANELA_DECLARADA"]["REGIAO_DO_FATO"]["VALOR"], NAO_SEI)
        self.assertEqual(self.linhas(
            "select count(*) from sala_de_espera where run_id = 'QC-R3' and "
            "janela_declarada #>> '{REGIAO_DO_FATO,VALOR}' = source_location"), [["0"]])

    def test_5b_da6_data_relativa_pousa_sem_fact_time(self):
        u = self.unidade(texto=BOLETIM_T1 + " Ieri le catture sono aumentate.",
                         item_id="derived:qc-ieri", corrida="QC-R7",
                         published_at="2026-05-13", published_at_basis="cabecalho")
        espera.pousar("QC-R7", [u])
        l = espera.ler("QC-R7")["ITENS"][0]
        self.assertEqual((l["FACT_TIME"], l["PUBLISHED_AT"]), (NAO_SEI, "2026-05-13"))
        self.assertEqual(l["JANELA_DECLARADA"]["TEMPO_RELATIVO"]["EXPRESSOES"], ["ieri"])

    # ── 6 · idempotencia ───────────────────────────────────────────────
    def test_6_o_mesmo_item_duas_vezes_e_um_registo(self):
        u = self.unidade(item_id="derived:qc-idem", fact_location="Langhe",
                         fact_location_basis="declarado no boletim")
        a = espera.pousar("QC-R4", [u])
        b = espera.pousar("QC-R4", [u])            # retry da mesma corrida
        c = espera.pousar("QC-R5", [u])            # o mesmo documento noutra corrida
        self.assertEqual(a["ESTADO"], espera.POUSOU)
        self.assertEqual(b["ESTADO"], espera.JA_ESTAVA)
        self.assertEqual((c["ESTADO"], c["JA_NA_SALA_POR_OUTRA_CORRIDA"]), (espera.JA_ESTAVA, 1))
        self.assertEqual(self.linhas(
            "select count(*) from sala_de_espera where item_id = 'derived:qc-idem'"), [["1"]])
        # e a MESMA corrida com a janela diferente e conflito, nao sobrescrita
        outra = json.loads(json.dumps(u))
        outra["JANELA_DECLARADA"]["REGIAO_DO_FATO"]["VALOR"] = "Roero"
        with self.assertRaises(espera.ConflitoDeCorrida):
            espera.pousar("QC-R4", [outra])
        self.assertEqual(self.linhas(
            "select janela_declarada #>> '{REGIAO_DO_FATO,VALOR}' from sala_de_espera "
            "where item_id = 'derived:qc-idem'"), [["Langhe"]])

    # ── 7 · a trava da forma ───────────────────────────────────────────
    def test_7_a_trava_recusa_chave_em_falta_ou_vazia(self):
        base = json.loads(json.dumps(A.JANELA_NAO_MEDIDA))
        cols = ("run_id, ordem, item_id, universo, texto, source_id, source_location, "
                "fact_location, fact_time, captured_at, admitido_por, corrida_sha256, "
                "janela_declarada")

        def inserir(ordem, janela):
            j = json.dumps(janela, ensure_ascii=False).replace("'", "''")
            return self.sql(
                "insert into sala_de_espera (%s) values ('QC-R9', %d, 'qc-trava-%d', 'T1', "
                "'x', 'IT-T1-900', 'NAO SEI', 'NAO SEI', 'NAO SEI', 'NAO SEI', 'teste', "
                "'%s', '%s'::json)" % (cols, ordem, ordem, "0" * 64, j), falhar=False)

        maus = []
        for c in A.QUATRO_CHAVES:
            sem = json.loads(json.dumps(base)); del sem[c]; maus.append(("sem " + c, sem))
            for vazio in ("", [], None):
                v = json.loads(json.dumps(base)); v[c]["VALOR"] = vazio
                maus.append(("%s VALOR=%r" % (c, vazio), v))
            sp = json.loads(json.dumps(base)); del sp[c]["VEIO_DE"]
            maus.append(("%s sem VEIO_DE" % c, sp))
        maus.append(("nao e objeto", "NAO SEI"))
        for i, (nome, janela) in enumerate(maus):
            r = inserir(100 + i, janela)
            self.assertNotEqual(r.returncode, 0, "a trava deixou passar: " + nome)
            self.assertIn("janela_declara_as_quatro_chaves", r.stderr, nome)
        self.assertEqual(inserir(99, base).returncode, 0)

    # ── 8 · o escritor que nao conhece a coluna ────────────────────────
    def test_8_escritor_antigo_fica_nao_sei_nas_quatro(self):
        """Uma linha escrita sem nomear `janela_declarada` le-se com o default da
        033 unica — e o dono le-o como `JANELA_NAO_MEDIDA`, sem inventar nada."""
        self.sql("insert into sala_de_espera (run_id, ordem, item_id, universo, texto, "
                 "source_id, source_location, fact_location, fact_time, captured_at, "
                 "admitido_por, corrida_sha256) values ('QC-R6', 0, 'derived:qc-antigo', "
                 "'T1', 'linha escrita sem a coluna', 'IT-T1-900', 'Veneto', 'NAO SEI', "
                 "'NAO SEI', 'NAO SEI', 'teste', '%s')" % ("0" * 64))
        antigo = espera.ler("QC-R6")["ITENS"][0]
        self.assertEqual(antigo["JANELA_DECLARADA"], A.JANELA_NAO_MEDIDA)
        self.assertEqual(antigo["SOURCE_LOCATION"], "Veneto")
        self.assertEqual(antigo["JANELA_DECLARADA"]["REGIAO_DO_FATO"]["VALOR"], NAO_SEI)

if __name__ == "__main__":
    unittest.main(verbosity=2)
