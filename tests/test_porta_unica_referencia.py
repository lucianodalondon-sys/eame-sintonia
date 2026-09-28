#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PORTA-UNICA-REFERENCIA — o contrato da porta (motor/porta_da_referencia.py) e dos seus consumidores.

    python3 -m unittest tests.test_porta_unica_referencia -v

D116 do dono: bulas e portfolio sao UMA biblioteca de referencia, versionada; toda capacidade que fala
de produto consulta a MESMA edicao; proibido duplicar a tabela-mestra. D117: 14 dias sem checagem ->
PODE_ESTAR_DESATUALIZADO; 30 -> autorizacao A CONFIRMAR.

    A  varredura: nenhum modulo de motor/, leis/, coleta/ abre a referencia por fora da porta
    B  cada consumidor carimba a EDICAO que usou (a mesma da porta)
    C  edicao misturada -> NAO SEI inteira
    D  catalogo nao e autorizacao
    E  frescor (D117), contado da ultima checagem que deu certo
    F  a checagem e MEDIDA pelo construtor, e os livros commitados sao os que ele produz
    G  bula nao lida -> A_CONFIRMAR, nunca «nao autoriza»
    H  o carimbo leva o hash dos livros

Casos C/D/E mexem numa COPIA da referencia, numa pasta temporaria. O repositorio nao e tocado.
"""
import ast
import copy
import csv
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import porta_da_referencia as P          # noqa: E402
import adama_referencia as CONSTRUTOR    # noqa: E402
import capacidade_cientifica as SCI      # noqa: E402
import cap_win as WIN                    # noqa: E402
import corrida_da_inteligencia as CI     # noqa: E402
import cruzamentos_max as XM             # noqa: E402
import boletim_do_campo as BOL           # noqa: E402
import concorrencia_meta as META         # noqa: E402

CASA = RAIZ / "referencia" / "adama"
HOJE = date(2026, 9, 27)

# ═══════════════════════════════════════════════════════════════════════════
# A · a varredura
# ═══════════════════════════════════════════════════════════════════════════
#: O que so a porta pode abrir. Casado contra constantes de texto do CODIGO (docstring e comentario
#: nao contam) e contra os pedacos de um caminho montado (`os.path.join(..)`, `Path / ".." / ".."`).
PROIBIDO = re.compile(r"referencia/adama|IT-ROTULOS|PROD_FTS|COMMERCIAL-CATALOG", re.I)
PASTAS = ("motor", "leis", "coleta")
A_PORTA = "motor/porta_da_referencia.py"
#: Os consumidores religados NESTA missao. Nenhum pode estar nas excecoes.
RELIGADOS = ("motor/capacidade_cientifica.py", "motor/motor_das_capacidades.py", "motor/cap_win.py",
             "motor/cruzamentos_max.py", "coleta/concorrencia_meta.py", "leis/boletim_do_campo.py")
#: ⚠️ EXCECOES DECLARADAS, uma a uma, com o porque. A lista so pode ENCOLHER: um ficheiro novo que
#: leia por fora reprova; uma excecao que deixou de ler por fora tambem reprova (lista velha nao guarda).
EXCECOES = {
    "coleta/rotulos_baixar.py": "PRODUTOR — baixa os PDF crus (data/raw/IT-ROTULOS). Nao e consumidor.",
    "coleta/rotulos_ler.py": "PRODUTOR — escreve IT-ROTULOS-PARES.json, que o CONSTRUTOR da referencia le.",
    # AJUSTE DECLARADO (LOTE7-INTEGRA, juncao com claude/reference-maintenance-collection-8s2lwy, D117):
    # a peca nasceu no outro ramo, sem ver esta varredura. Nomeia PROD_FTS so para reconhecer a EDICAO
    # BRUTA do Ministero (l.97 regex do nome; l.380 texto de proveniencia). Nao abre referencia/adama.
    "coleta/it/edicoes_do_registro.py": "PRODUTOR — compara edicoes BRUTAS do CSV do Ministero "
                                        "(IT-T4-001) e emite EVENTO_REGULATORIO; nao consome a referencia.",
    "coleta/cruzar_regua_rotulo.py": "DIVIDA DECLARADA — le IT-ROTULOS-PARES direto (regua x rotulo). "
                                     "Fora do escopo desta missao; religar e a proxima.",
    "coleta/pesquisadores_t6.py": "DIVIDA DECLARADA — le ACTIVE-INGREDIENTS e o CSV PROD_FTS 0907 para o "
                                  "lexico de moleculas (todas as empresas). Fora do escopo.",
    "motor/pacote_convergencia.py": "DIVIDA DECLARADA — le IT-ROTULOS-PARES e IT-CENSO-DE-TERMOS (pacote "
                                    "de convergencia). Fora do escopo.",
    "motor/normalize_substance.py": "DIVIDA DECLARADA (LEGADO V2) — CSV PROD_FTS 0824 bruto.",
    "motor/v2_cruzamentos.py": "DIVIDA DECLARADA (LEGADO V2) — V2/COMMERCIAL-CATALOG.json.",
    "motor/v2_montar_handoff.py": "DIVIDA DECLARADA (LEGADO V2) — nomeia COMMERCIAL-CATALOG.json no handoff.",
    "motor/v21_ingest.py": "MENCAO — texto de proveniencia com o nome da foto; nao abre ficheiro.",
    "motor/pacote_normalizar.py": "MENCAO — texto de proveniencia com o nome da foto; nao abre ficheiro.",
    "leis/data_clock.py": "DIVIDA DECLARADA — registo de relogio das fontes aponta o CSV 0824 bruto.",
}


def _docstrings(arv):
    ids = set()
    for no in ast.walk(arv):
        if isinstance(no, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            corpo = getattr(no, "body", [])
            if corpo and isinstance(corpo[0], ast.Expr) and isinstance(getattr(corpo[0], "value", None), ast.Constant):
                ids.add(id(corpo[0].value))
    return ids


def _pedacos(no):
    """As constantes de texto de um caminho montado: join(a, b, c) e a / b / c."""
    if isinstance(no, ast.Constant) and isinstance(no.value, str):
        return [no.value]
    if isinstance(no, ast.BinOp) and isinstance(no.op, ast.Div):
        return _pedacos(no.left) + _pedacos(no.right)
    if isinstance(no, ast.Call):
        return [x for a in no.args for x in _pedacos(a)]
    return []


def leituras_por_fora(texto: str, nome="?") -> list:
    """Linhas de CODIGO que nomeiam o que so a porta abre."""
    arv = ast.parse(texto, filename=nome)
    docs = _docstrings(arv)
    achados = set()
    for no in ast.walk(arv):
        if isinstance(no, ast.Constant) and isinstance(no.value, str) and id(no) not in docs:
            if PROIBIDO.search(no.value):
                achados.add(no.lineno)
        elif isinstance(no, (ast.Call, ast.BinOp)):
            if PROIBIDO.search("/".join(_pedacos(no))):
                achados.add(no.lineno)
    return sorted(achados)


def varrer(raiz=RAIZ) -> dict:
    out = {}
    for pasta in PASTAS:
        for p in sorted((raiz / pasta).rglob("*.py")):
            rel = p.relative_to(raiz).as_posix()
            if rel == A_PORTA or "__pycache__" in rel:
                continue
            linhas = leituras_por_fora(p.read_text(encoding="utf-8", errors="replace"), rel)
            if linhas:
                out[rel] = linhas
    return out


class A_Varredura(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.achados = varrer()

    def test_A1_ninguem_le_por_fora_alem_das_excecoes_declaradas(self):
        novos = {f: l for f, l in self.achados.items() if f not in EXCECOES}
        self.assertEqual({}, novos, "abrem a referencia por fora da porta: %s" % novos)

    def test_A2_nenhum_religado_esta_nas_excecoes_nem_le_por_fora(self):
        for f in RELIGADOS:
            self.assertNotIn(f, EXCECOES)
            self.assertNotIn(f, self.achados, "%s voltou a ler por fora: linhas %s" % (f, self.achados.get(f)))

    def test_A3_excecao_velha_reprova(self):
        velhas = [f for f in EXCECOES if f not in self.achados]
        self.assertEqual([], velhas, "excecao que ja nao le por fora: tire-a da lista")

    def test_A4_os_religados_importam_a_porta(self):
        for f in RELIGADOS:
            txt = (RAIZ / f).read_text(encoding="utf-8")
            self.assertRegex(txt, r"import porta_da_referencia", f)

    def test_A5_o_detetor_apanha_as_tres_formas(self):
        self.assertTrue(leituras_por_fora('X = os.path.join(R, "referencia", "adama", "PORTFOLIO.json")\n'))
        self.assertTrue(leituras_por_fora('X = R / "referencia" / "adama" / "REGISTRATIONS.json"\n'))
        self.assertTrue(leituras_por_fora('X = open("data/samples/IT-ROTULOS/IT-ROTULOS-PARES.json")\n'))
        self.assertTrue(leituras_por_fora('X = "PROD_FTS_6_20260907.csv"\n'))
        self.assertFalse(leituras_por_fora('"""fala de referencia/adama e de PROD_FTS"""\n# IT-ROTULOS\nx = 1\n'))

    def test_A6_so_a_porta_nomeia_a_casa(self):
        txt = (RAIZ / A_PORTA).read_text(encoding="utf-8")
        self.assertTrue(leituras_por_fora(txt), "a porta tem de ser quem nomeia a casa")


# ═══════════════════════════════════════════════════════════════════════════
# B · o carimbo da edicao, em cada consumidor
# ═══════════════════════════════════════════════════════════════════════════
TEXTO_DE_JANELA = "Peronospora: intervenire alla comparsa dei sintomi."


def _problema_do_texto(problema):
    import boletim_do_campo as BC
    p = BC.problema_do_boletim(TEXTO_DE_JANELA)
    assert p["VALOR"] == problema, p
    return p


def _item_de_janela(cultura, problema):
    campo = lambda v: {"VALOR": v, "BASE": "SINTETICO", "VEIO_DE": "SINTETICO"}  # noqa: E731
    return {"MARCA": "SINTETICO", "ITEM_ID": "SINT-PORTA-1", "RAW_OBSERVATION_ID": "RAW-SINT-PORTA-1",
            "SOURCE_ID": "SRC-sint", "URL": "https://sint.example/b", "CAPTURED_AT": "2026-09-25T10:00:00Z",
            "PUBLISHED_AT": "2026-09-25", "FACT_TIME": "2026-09-20/2026-09-24", "FACT_TIME_BASIS": "SINTETICO",
            "TEXTO": TEXTO_DE_JANELA,
            # CHAVE-PROBLEMA (27/09) — AJUSTE DECLARADO: o PROBLEMA sai no contrato PROBLEMA/v1, pelo
            # produtor unico da Collection sobre o proprio texto (antes: VEIO_DE = SINTETICO, fora do contrato)
            "JANELA_DECLARADA": {"CULTURA": campo(cultura), "PROBLEMA": _problema_do_texto(problema),
                                 "REGIAO_DO_FATO": campo("IT-VEN"),
                                 "FASE": {"VALOR": "NAO SEI", "BASE": "NAO SEI"},
                                 "JANELA": {"VALOR": "NAO SEI", "BASE": "NAO SEI"}}}


class B_Carimbo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = P.abrir(hoje=HOJE)
        cls.ed = cls.ref["REGISTRO"]["EDICAO"]

    def test_B0_a_porta_abre_com_as_duas_edicoes(self):
        r = self.ref
        self.assertEqual(r["ESTADO"], "LIDA")
        self.assertEqual(r["REGISTRO"]["EDICAO"], "PROD_FTS_6_20260831")
        self.assertEqual(r["REGISTRO"]["DATA_DA_EDICAO"], "2026-08-31")
        self.assertEqual(r["REGISTRO"]["ULTIMA_CHECAGEM_OK"], "2026-09-07")
        self.assertEqual(r["CATALOGO"]["EDICAO"], "CAT_ADAMA_IT_20260915")
        self.assertNotEqual(r["REGISTRO"]["EDICAO"], r["CATALOGO"]["EDICAO"])

    def test_B1_cap_sci(self):
        ref = SCI.carregar_referencia(hoje=HOJE)
        self.assertEqual(ref["CARIMBO"]["EDICAO_REGISTRO"], self.ed)
        self.assertEqual(len(ref["SHA256"]), 4)

    def test_B2_cap_win_carimba_e_responde_produtos(self):
        itens = [_item_de_janela("vite", "peronospora")]
        livro = CI.correr("porta", itens, universo={"ITENS_NO_CORTE": 1})
        cw = WIN.julgar(livro, itens, HOJE, referencia=self.ref)
        self.assertEqual(cw["REFERENCIA_ADAMA"]["EDICAO_REGISTRO"], self.ed)
        (j,) = cw["CROP_WINDOWS"]
        self.assertEqual(j["PRODUTOS_ADAMA"]["EDICAO_REGISTRO"], self.ed)
        self.assertEqual(j["PRODUTOS_ADAMA"]["ESTADO"], P.AUTORIZADO_NA_BULA_LIDA)
        self.assertIn("012878", {p["REGISTRATION_NUMBER"] for p in j["PRODUTOS_ADAMA"]["PRODUTOS"]})

    def test_B3_motor_usa_UMA_referencia_para_as_duas_capacidades(self):
        import motor_das_capacidades as M
        e = M.entrada_do_export(json.loads((RAIZ / "tests" / "dados" / "int-r7" /
                                            "SINTETICO-R7-SALA-EXPORT.json").read_text(encoding="utf-8")))
        with tempfile.TemporaryDirectory() as d:
            copia = Path(d) / "adama"
            shutil.copytree(CASA, copia)
            _mexer(copia, "PORTFOLIO", lambda x: x.update(NOTA="copia do teste"))   # outra impressao
            ref = P.abrir(copia, hoje=HOJE)
            s = M.rodar(e, HOJE, "SINT", referencia=ref)
        imp = ref["CARIMBO"]["IMPRESSAO_DOS_LIVROS"]
        self.assertNotEqual(imp, self.ref["CARIMBO"]["IMPRESSAO_DOS_LIVROS"])
        self.assertEqual(s["REFERENCIA_ADAMA"]["IMPRESSAO_DOS_LIVROS"], imp)
        self.assertEqual(s["CAP_WIN"]["REFERENCIA_ADAMA"]["IMPRESSAO_DOS_LIVROS"], imp)
        self.assertEqual(s["CAP_SCI"]["REFERENCIA"]["CARIMBO"]["IMPRESSAO_DOS_LIVROS"], imp)

    def test_B4_cruzamentos_max(self):
        out = XM.correr(hoje=HOJE, referencia=self.ref)
        self.assertEqual(out["REFERENCIA_ADAMA"]["EDICAO_REGISTRO"], self.ed)
        self.assertNotIn("PARES", out["INSUMOS"])
        self.assertNotIn("CADASTRO", out["INSUMOS"])

    def test_B5_boletim(self):
        leitura = {"SECOES": [{"CULTURA": "vigneto", "PROBLEMAS": [{"NOME": "peronospora", "ESTADO": "PRESENTE"},
                                                                  {"NOME": "oidio", "ESTADO": "AUSENTE"}]},
                              {"CULTURA": None, "PROBLEMAS": [{"NOME": "afidi", "ESTADO": "CITADA"}]}]}
        r = BOL.produtos_adama_do_boletim(leitura, self.ref)
        self.assertEqual(r["REFERENCIA_ADAMA"]["EDICAO_REGISTRO"], self.ed)
        self.assertEqual([(p["CULTURA"], p["PRAGA"]) for p in r["PARES"]], [("vite", "peronospora")])
        self.assertEqual(r["PARES"][0]["PRODUTOS_ADAMA"]["ESTADO"], P.AUTORIZADO_NA_BULA_LIDA)

    def test_B6_concorrencia_meta_so_por_substancia_e_alvo(self):
        col = [{"OBSERVACAO": {"META_AD_LIBRARY_ID": "SINT-1", "COMPANY": "SINT",
                               "CREATIVE_TEXT": "Nuovo fungicida con Folpet contro la peronospora"}},
               {"OBSERVACAO": {"META_AD_LIBRARY_ID": "SINT-2", "COMPANY": "SINT", "CREATIVE_TEXT": "Vieni in fiera"}}]
        r = META.adama_no_anuncio(col, self.ref)
        self.assertEqual(r["REFERENCIA_ADAMA"]["EDICAO_REGISTRO"], self.ed)
        a, b = r["ANUNCIOS"]
        self.assertEqual([x["SUBSTANCIA"] for x in a["SUBSTANCIAS_NO_CRIATIVO"]], ["FOLPET"])
        self.assertEqual(a["SUBSTANCIAS_NO_CRIATIVO"][0]["ADAMA"]["ESTADO"], P.REGISTRADO_COM_A_SUBSTANCIA)
        self.assertEqual(a["CULTURA_DO_ANUNCIO"], P.NAO_SEI)
        self.assertEqual([x["ALVO"] for x in a["ALVOS_NO_CRIATIVO"]], ["PERONOSPORA"])
        self.assertIn("NAO SEI", b["PORQUE"])
        self.assertNotIn("nao tem", b["PORQUE"].replace("«a ADAMA nao tem»", ""))


# ═══════════════════════════════════════════════════════════════════════════
# C · edicao misturada   D · catalogo nao e autorizacao   E · frescor   G · bula nao lida
# ═══════════════════════════════════════════════════════════════════════════
def _mexer(pasta: Path, livro: str, f):
    p = pasta / (livro + ".json")
    d = json.loads(p.read_text(encoding="utf-8"))
    f(d)
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


class _Copia(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.copia = Path(self._d.name) / "adama"
        shutil.copytree(CASA, self.copia)

    def tearDown(self):
        self._d.cleanup()


class C_EdicaoMisturada(_Copia):
    def test_C1_um_livro_de_outra_edicao_derruba_a_referencia_inteira(self):
        _mexer(self.copia, "AUTHORIZED-USES", lambda d: d.update(CURRENT_SNAPSHOT="PROD_FTS_6_20260914"))
        r = P.abrir(self.copia, hoje=HOJE)
        self.assertEqual(r["ESTADO"], P.NAO_SEI)
        self.assertIn("EDICAO_MISTURADA", r["PORQUE"])
        self.assertEqual(P.autorizados(r, "vite", "peronospora")["ESTADO"], P.NAO_SEI)
        self.assertEqual(P.carimbo(r)["EDICAO_REGISTRO"], P.NAO_SEI)

    def test_C2_duas_fotos_correntes(self):
        def dois(d):
            for x in d["RECORDS"]:
                x["CURRENT"] = True
        _mexer(self.copia, "SNAPSHOTS", dois)
        self.assertEqual(P.abrir(self.copia, hoje=HOJE)["ESTADO"], P.NAO_SEI)

    def test_C3_catalogo_misturado(self):
        _mexer(self.copia, "PORTFOLIO-OBSERVATIONS", lambda d: d.update(CURRENT_SNAPSHOT="CAT_ADAMA_IT_20260830"))
        self.assertIn("catalogo", P.abrir(self.copia, hoje=HOJE)["PORQUE"])

    def test_C4_livro_ausente_e_nao_sei_nunca_vazio(self):
        (self.copia / "LABEL-READINGS.json").unlink()
        r = P.abrir(self.copia, hoje=HOJE)
        self.assertEqual(r["ESTADO"], P.NAO_SEI)
        self.assertEqual(SCI.da_porta(r)["ESTADO"], SCI.NAO_SEI)


class D_CatalogoNaoEAutorizacao(_Copia):
    def test_D1_na_vitrine_com_registo_inativo_nao_e_autorizado(self):
        # FOLPAN GOLD (012878) esta no PORTFOLIO e tem vite x peronospora na bula lida.
        port = json.loads((self.copia / "PORTFOLIO.json").read_text(encoding="utf-8"))["RECORDS"]
        self.assertIn("012878", {p["REGISTRATION_NUMBER"] for p in port})

        def revogar(d):
            for r in d["RECORDS"]:
                if r["REGISTRATION_NUMBER"] == "012878":
                    r["ADMIN_ACTIVE"], r["ADMIN_STATUS"] = False, "Revocato"
        _mexer(self.copia, "REGISTRATIONS", revogar)
        r = P.abrir(self.copia, hoje=HOJE)
        regs = {p["REGISTRATION_NUMBER"] for p in P.autorizados(r, "vite", "peronospora")["PRODUTOS"]}
        self.assertNotIn("012878", regs)
        self.assertEqual(P.no_catalogo(r, "ADAMA-P-0010")["MEMBERSHIP_STATE"], "PRESENT_IN_CATALOG_SNAPSHOT")

    def test_D2_apagar_o_catalogo_nao_muda_nenhuma_autorizacao(self):
        antes = P.autorizados(P.abrir(self.copia, hoje=HOJE), "vite", "peronospora")
        _mexer(self.copia, "PORTFOLIO", lambda d: d.update(RECORDS=[]))
        _mexer(self.copia, "PRODUCT-MASTER", lambda d: d.update(PRODUCTS=[]))
        depois = P.autorizados(P.abrir(self.copia, hoje=HOJE), "vite", "peronospora")
        self.assertEqual(antes["PRODUTOS"], depois["PRODUTOS"])

    def test_D3_as_metades_nao_se_misturam(self):
        r = P.abrir(self.copia, hoje=HOJE)
        self.assertEqual(set(r["REGISTRO"]["LIVROS"]), set(P.LIVROS_DO_REGISTRO))
        self.assertEqual(set(r["CATALOGO"]["LIVROS"]), set(P.LIVROS_DO_CATALOGO))
        self.assertFalse(set(P.LIVROS_DO_REGISTRO) & set(P.LIVROS_DO_CATALOGO))
        self.assertIn("NAO E AUTORIZACAO", r["CATALOGO"]["PAPEL"])


class E_Frescor(unittest.TestCase):
    CHECK = date(2026, 9, 7)

    def test_E1_os_tres_degraus_do_d117(self):
        for dias, esperado in ((0, P.FRESCA), (13, P.FRESCA), (14, P.PODE_ESTAR_DESATUALIZADO),
                               (29, P.PODE_ESTAR_DESATUALIZADO), (30, P.AUTORIZACAO_A_CONFIRMAR),
                               (400, P.AUTORIZACAO_A_CONFIRMAR)):
            r = P.abrir(hoje=self.CHECK + timedelta(days=dias))
            self.assertEqual(r["REGISTRO"]["ESTADO_FRESCOR"], esperado, dias)

    def test_E2_sem_data_de_checagem_e_a_confirmar(self):
        self.assertEqual(P.estado_frescor(None), P.AUTORIZACAO_A_CONFIRMAR)

    def test_E3_aos_30_dias_nenhuma_autorizacao_sai_afirmada(self):
        r = P.abrir(hoje=self.CHECK + timedelta(days=30))
        a = P.autorizados(r, "vite", "peronospora")
        self.assertEqual(a["ESTADO"], P.A_CONFIRMAR)
        self.assertTrue(a["PRODUTOS"])
        self.assertEqual({p["ESTADO"] for p in a["PRODUTOS"]}, {P.A_CONFIRMAR})
        self.assertEqual(P.por_substancia(r, "FOLPET")["ESTADO"], P.A_CONFIRMAR)
        self.assertEqual(P.por_alvo(r, "PERONOSPORA")["ESTADO"], P.A_CONFIRMAR)

    def test_E4_aos_14_a_resposta_sai_com_aviso(self):
        a = P.autorizados(P.abrir(hoje=self.CHECK + timedelta(days=20)), "vite", "peronospora")
        self.assertEqual(a["ESTADO"], P.AUTORIZADO_NA_BULA_LIDA)
        self.assertIn(P.PODE_ESTAR_DESATUALIZADO, a["AVISO_DE_FRESCOR"])

    def test_E5_cap_sci_marca_a_ligacao_a_confirmar(self):
        ref = SCI.carregar_referencia(hoje=self.CHECK + timedelta(days=31))
        e = {"ITEM_ID": "SINT", "DOI": "SINT", "CULTURA": "vite", "PROBLEMA": "peronospora",
             "MOLECULA": ["FOLPET"], "LOCAL_DO_ESTUDO": {"ESTADO": "PROVADO"},
             "PERIODO_DO_ESTUDO": {"ESTADO": "PROVADO"},
             "APLICABILIDADE": {"PROVADO": {"LOCAL": True, "PERIODO": True}}}
        (m,) = SCI.ligar_ao_produto(e, ref)["POR_MOLECULA"]
        self.assertEqual(m["AUTORIZACAO"], P.A_CONFIRMAR)
        (m,) = SCI.ligar_ao_produto(e, SCI.carregar_referencia(hoje=HOJE))["POR_MOLECULA"]
        self.assertEqual(m["AUTORIZACAO"], P.AUTORIZADO_NA_BULA_LIDA)

    def test_E6_cruzamentos_nao_confirma_com_referencia_velha(self):
        sys.path.insert(0, str(RAIZ / "tests"))
        import test_cruzamentos_max as TX
        for dias, esperado in ((31, XM.YES_A_CONFIRMAR), (1, XM.CONFIRMED_YES)):
            ref = TX.referencia()
            ref.carimbo = {"ESTADO": "LIDA", "ESTADO_FRESCOR": P.estado_frescor(dias)}
            c = TX.cruzamento("TAUFLUVALINATE", ["SINT-TAU"], ["vite"], "BOLLETTINO FITOSANITARIO VITE: "
                              "tau-fluvalinate", estado=XM.YES_A_CONFIRMAR, x3h=["vite"])
            self.assertEqual(XM.confirmar(XM.refazer(c, ref), c, ref)["ESTADO"], esperado, dias)

    def test_E7_hoje_do_relogio_fica_escrito(self):
        self.assertEqual(P.abrir()["HOJE_VEIO_DE"], "RELOGIO_DO_SISTEMA")
        self.assertEqual(P.abrir(hoje=HOJE)["HOJE_VEIO_DE"], "DECLARADO")


class G_BulaNaoLida(unittest.TestCase):
    def test_G1_sem_uso_lido_e_com_bula_ativa_nao_lida_e_a_confirmar(self):
        r = P.abrir(hoje=HOJE)
        # TABACCO esta nas bulas, mas nenhuma bula lida o liga a PERONOSPORA
        a = P.autorizados(r, "tabacco", "peronospora")
        self.assertEqual(a["PRODUTOS"], [])
        self.assertEqual(a["ESTADO"], P.A_CONFIRMAR)
        self.assertGreater(a["A_CONFIRMAR"]["N_BULAS_ATIVAS_NAO_LIDAS"], 0)
        self.assertIn("NA NOSSA LEITURA", a["PORQUE"])

    def test_G2_cultura_fora_do_vocabulario_e_nao_sei(self):
        a = P.autorizados(P.abrir(hoje=HOJE), "mirtillo", "afidi")
        self.assertEqual(a["ESTADO"], P.NAO_SEI)
        self.assertIn("NAO quer dizer", a["PORQUE"])

    def test_G3_a_frase_proibida_nao_sai_da_porta(self):
        r = P.abrir(hoje=HOJE)
        for x in (P.autorizados(r, "tabacco", "peronospora"), P.autorizados(r, "mirtillo"),
                  P.por_substancia(r, "SINT-NADA"), P.por_alvo(r, "SINT-NADA")):
            self.assertNotIn("A ADAMA NAO TEM", json.dumps(x, ensure_ascii=False).upper())


# ═══════════════════════════════════════════════════════════════════════════
# F · o construtor: checagem medida, livros commitados = livros produzidos   H · hash
# ═══════════════════════════════════════════════════════════════════════════
class F_Construtor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saida = CONSTRUTOR.montar(escrever=False)

    def test_F1_os_livros_commitados_sao_os_que_o_construtor_produz(self):
        for nome in ("SNAPSHOTS.json", "AUTHORIZED-USES.json", "LABEL-READINGS.json", "REGISTRATIONS.json"):
            commitado = json.loads((CASA / nome).read_text(encoding="utf-8"))
            self.assertEqual(commitado, json.loads(json.dumps(self.saida[nome], ensure_ascii=False)), nome)

    def test_F2_a_checagem_e_medida_contra_o_bruto(self):
        snaps = self.saida["SNAPSHOTS.json"]
        self.assertEqual(snaps["LAST_CHECK_OK"], "2026-09-07")
        (f,) = [x for x in snaps["RECORDS"] if x.get("CHECK")]
        self.assertEqual(f["CHECK"]["RESULT"], "CONFIRMA_A_EDICAO")
        self.assertEqual((f["CHECK"]["ADAMA_IN_RAW"], f["CHECK"]["ADAMA_IN_EDITION"]), (602, 602))

    def test_F3_bruto_divergente_nao_confirma(self):
        regs = self.saida["REGISTRATIONS.json"]["RECORDS"]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.csv"
            with open(p, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(["num_registrazione", "ragione_sociale", "stato_amministrativo"])
                for r in regs:
                    w.writerow([r["REGISTRATION_NUMBER"], r["HOLDER"], r["ADMIN_STATUS"]])
                w.writerow(["999999", "ADAMA SINT", "Autorizzato"])
            c = CONSTRUTOR.conferir_contra_o_bruto(regs, str(p))
        self.assertEqual(c["RESULT"], "DIVERGE_DA_EDICAO")
        self.assertEqual(c["ENTRIES"], ["999999"])
        self.assertEqual(CONSTRUTOR.conferir_contra_o_bruto(regs, "/nao/existe.csv")["RESULT"], "NAO_CONFERIDO")

    def test_F4_os_pares_trazem_a_citacao_e_as_bulas_a_leitura(self):
        usos = self.saida["AUTHORIZED-USES.json"]["RECORDS"]
        self.assertEqual(len(usos), 2030)
        self.assertTrue(all(u.get("LINK_LEVEL") in ("LINHA_DA_TABELA", "BLOCO_DA_CULTURA",
                                                     "DECLARACAO_DE_PRODUTO") for u in usos))
        self.assertTrue(all("LINE_QUOTE" in u and "CROPS_QUOTE" in u for u in usos))
        leit = self.saida["LABEL-READINGS.json"]["RECORDS"]
        self.assertEqual(len(leit), 163)
        self.assertEqual(sum(1 for x in leit if x["LABEL_WAS_READ"]), 102)

    def test_F5_uma_edicao_so_em_todos_os_livros_do_registro(self):
        eds = {n: self.saida[n + ".json"]["CURRENT_SNAPSHOT"] for n in P.LIVROS_DO_REGISTRO}
        self.assertEqual(set(eds.values()), {CONSTRUTOR.SNAPSHOT_ATUAL}, eds)


class H_Hash(_Copia):
    def test_H1_o_carimbo_e_o_sha_do_ficheiro(self):
        r = P.abrir(self.copia, hoje=HOJE)
        for n in P.LIVROS_DO_REGISTRO:
            self.assertEqual(r["CARIMBO"]["SHA256"][n],
                             hashlib.sha256((self.copia / (n + ".json")).read_bytes()).hexdigest())

    def test_H2_mexer_num_livro_muda_a_impressao(self):
        antes = P.abrir(self.copia, hoje=HOJE)["CARIMBO"]["IMPRESSAO_DOS_LIVROS"]
        _mexer(self.copia, "DOSES", lambda d: d.update(NOTA="x"))
        self.assertNotEqual(antes, P.abrir(self.copia, hoje=HOJE)["CARIMBO"]["IMPRESSAO_DOS_LIVROS"])


# ═══════════════════════════════════════════════════════════════════════════
# I · o GRAO do uso (LOTE7-INTEGRA; achado do LAB, PESQUISA-CRUZAMENTOS F.2-1)
#     so LINHA_DA_TABELA / BLOCO_DA_CULTURA autorizam; DECLARACAO_DE_PRODUTO = A_CONFIRMAR.
#     A regra mora NA PORTA, uma vez so; os consumidores herdam.
# ═══════════════════════════════════════════════════════════════════════════
class I_Grao(_Copia):
    def test_I1_a_regra_unica(self):
        for nivel, esperado in ((P.LINHA_DA_TABELA, P.AUTORIZADO_NA_BULA_LIDA),
                                (P.BLOCO_DA_CULTURA, P.AUTORIZADO_NA_BULA_LIDA),
                                (P.DECLARACAO_DE_PRODUTO, P.A_CONFIRMAR),
                                (P.NAO_SEI, P.A_CONFIRMAR), (None, P.A_CONFIRMAR)):
            est, porque = P.autorizacao_do_uso({"LINK_LEVEL": nivel}, P.FRESCA)
            self.assertEqual(est, esperado, nivel)
            if est == P.A_CONFIRMAR:
                self.assertIn("GRAO", porque)
        self.assertEqual(P.autorizacao_do_uso({}, P.FRESCA)[0], P.A_CONFIRMAR)
        # o frescor (D117) continua a mandar por cima do grao
        self.assertEqual(P.autorizacao_do_uso({"LINK_LEVEL": P.LINHA_DA_TABELA}, P.AUTORIZACAO_A_CONFIRMAR)[0],
                         P.A_CONFIRMAR)
        self.assertEqual(P.NIVEIS_QUE_AUTORIZAM, (P.LINHA_DA_TABELA, P.BLOCO_DA_CULTURA))

    def test_I2_nenhum_autorizado_da_porta_vem_de_declaracao(self):
        r = P.abrir(hoje=HOJE)
        pares = sorted({(u["CROP_ON_LABEL"], u["TARGET_ON_LABEL"]) for u in P.livro(r, "AUTHORIZED-USES")})
        vistos = {P.AUTORIZADO_NA_BULA_LIDA: 0, P.A_CONFIRMAR: 0}
        for c, a in pares:
            x = P.autorizados(r, c, a)
            for p in x["PRODUTOS"]:
                vistos[p["ESTADO"]] += 1
                self.assertEqual(p["ESTADO"] == P.AUTORIZADO_NA_BULA_LIDA,
                                 p["LINK_LEVEL"] in P.NIVEIS_QUE_AUTORIZAM, (c, a, p["USE_ID"]))
            fortes = [p for p in x["PRODUTOS"] if p["LINK_LEVEL"] in P.NIVEIS_QUE_AUTORIZAM]
            self.assertEqual(x["ESTADO"] == P.AUTORIZADO_NA_BULA_LIDA, bool(fortes), (c, a))
        self.assertGreater(vistos[P.A_CONFIRMAR], 0)       # ha declaracoes na edicao, e elas caem
        self.assertGreater(vistos[P.AUTORIZADO_NA_BULA_LIDA], 0)

    def test_I3_par_so_de_declaracao_sai_a_confirmar_com_o_porque(self):
        r = P.abrir(hoje=HOJE)
        usos = P.livro(r, "AUTHORIZED-USES")
        niveis = {}
        for u in usos:
            niveis.setdefault((u["CROP_ON_LABEL"], u["TARGET_ON_LABEL"]), set()).add(u["LINK_LEVEL"])
        so_decl = sorted(k for k, v in niveis.items() if v == {P.DECLARACAO_DE_PRODUTO})
        self.assertTrue(so_decl)
        x = P.autorizados(r, *so_decl[0])
        self.assertTrue(x["PRODUTOS"])
        self.assertEqual(x["ESTADO"], P.A_CONFIRMAR)
        self.assertIn("DECLARACAO_DE_PRODUTO", x["PORQUE"])

    def _tudo_declaracao(self):
        def f(d):
            for u in d["RECORDS"]:
                u["LINK_LEVEL"] = P.DECLARACAO_DE_PRODUTO
        _mexer(self.copia, "AUTHORIZED-USES", f)
        return P.abrir(self.copia, hoje=HOJE)

    def test_I4_os_consumidores_herdam_da_porta(self):
        r = self._tudo_declaracao()
        self.assertEqual(r["ESTADO"], "LIDA")
        a = P.autorizados(r, "vite", "peronospora")
        self.assertTrue(a["PRODUTOS"])
        self.assertEqual(a["ESTADO"], P.A_CONFIRMAR)
        # CAP-WIN
        self.assertEqual(WIN.produtos_adama(r, "vite", "peronospora")["ESTADO"], P.A_CONFIRMAR)
        # boletim
        leitura = {"SECOES": [{"CULTURA": "vigneto", "PROBLEMAS": [{"NOME": "peronospora", "ESTADO": "PRESENTE"}]}]}
        b = BOL.produtos_adama_do_boletim(leitura, r)
        self.assertEqual(b["PARES"][0]["PRODUTOS_ADAMA"]["ESTADO"], P.A_CONFIRMAR)
        # concorrencia (por alvo)
        self.assertEqual(P.por_alvo(r, "PERONOSPORA")["ESTADO"], P.A_CONFIRMAR)
        # CAP-SCI
        e = {"ITEM_ID": "SINT", "DOI": "SINT", "CULTURA": "vite", "PROBLEMA": "peronospora",
             "MOLECULA": ["FOLPET"], "LOCAL_DO_ESTUDO": {"ESTADO": "PROVADO"},
             "PERIODO_DO_ESTUDO": {"ESTADO": "PROVADO"},
             "APLICABILIDADE": {"PROVADO": {"LOCAL": True, "PERIODO": True}}}
        (m,) = SCI.ligar_ao_produto(e, SCI.da_porta(r))["POR_MOLECULA"]
        self.assertTrue(m["PRODUTOS"])
        self.assertEqual(m["AUTORIZACAO"], P.A_CONFIRMAR)
        self.assertIn("GRAO", m["AUTORIZACAO_PORQUE"])
        (m,) = SCI.ligar_ao_produto(e, SCI.carregar_referencia(hoje=HOJE))["POR_MOLECULA"]
        self.assertEqual(m["AUTORIZACAO"], P.AUTORIZADO_NA_BULA_LIDA)

    def test_I5_por_alvo_so_diz_cultura_na_bula_quando_o_grao_une(self):
        r = P.abrir(hoje=HOJE)
        usos = P.livro(r, "AUTHORIZED-USES")
        x = P.por_alvo(r, "PERONOSPORA")
        for reg in x["REGISTOS"]:
            fortes = {u["CROP_ON_LABEL"] for u in usos if u["REGISTRATION_NUMBER"] == reg["REGISTRATION_NUMBER"]
                      and u["TARGET_ON_LABEL"] == "PERONOSPORA" and u["LINK_LEVEL"] in P.NIVEIS_QUE_AUTORIZAM}
            self.assertEqual(set(reg["CULTURAS_NA_BULA"]), fortes, reg["REGISTRATION_NUMBER"])
            self.assertEqual(reg["ESTADO"] == P.AUTORIZADO_NA_BULA_LIDA, bool(fortes))
        r2 = self._tudo_declaracao()
        for reg in P.por_alvo(r2, "PERONOSPORA")["REGISTOS"]:
            self.assertEqual(reg["CULTURAS_NA_BULA"], [])
            self.assertTrue(reg["CULTURAS_SO_DECLARADAS"])
            self.assertEqual(reg["ESTADO"], P.A_CONFIRMAR)

    def test_I6_a_regra_mora_so_na_porta(self):
        """cruzamentos_max le os niveis da porta; nenhum religado escreve a sua lista de niveis."""
        self.assertIs(XM.NIVEIS_FORTES, P.NIVEIS_QUE_AUTORIZAM)
        for rel in RELIGADOS:
            arv = ast.parse((RAIZ / rel).read_text(encoding="utf-8"))
            docs = _docstrings(arv)
            lit = [n.lineno for n in ast.walk(arv) if isinstance(n, ast.Constant) and id(n) not in docs
                   and n.value in (P.LINHA_DA_TABELA, P.BLOCO_DA_CULTURA)]
            self.assertEqual(lit, [], "%s reescreve os niveis que autorizam: linhas %s" % (rel, lit))


if __name__ == "__main__":
    unittest.main()
