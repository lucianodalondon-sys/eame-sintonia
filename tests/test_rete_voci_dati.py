#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RETE-VOCI-DATI, ATACADA — o dado ja coletado no contrato do pote v2.

    python3 -m unittest tests.test_rete_voci_dati -v

Le os ficheiros REAIS rastreados (nao ha fixture sintetica aqui, excepto a corrida
sintetica do pote para provar a junta, e os casos-regra montados a mao em S*).
Sem rede.
"""
import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "pacote", RAIZ / "motor", RAIZ / "leis", RAIZ / "curadoria"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import rete_voci_dati as R                                    # noqa: E402
import pote_intelligence_casco as POTE                        # noqa: E402
from corrida_da_inteligencia import portao_g0, e_ignorancia   # noqa: E402

NAO_SEI = R.NAO_SEI
CONTAGEM_COMMITADA = RAIZ / "data" / "derivados" / "RETE-VOCI-DATI" / "CONTAGEM.json"
CORRIDA_SINTETICA = RAIZ / "tests" / "fixtures" / "pote" / "CORRIDA-SINTETICA-POTE.json"
_EXTRA = None


def extra():
    global _EXTRA
    if _EXTRA is None:
        _EXTRA = R.montar(RAIZ)
    return copy.deepcopy(_EXTRA)


def objs(e, comp):
    return e["ITENS_POR_FERRAMENTA"][comp]


def linhagem(e):
    return {(x["CORRIDA_UPSTREAM"], x["ITEM_ID"]): x for x in e["LINEAGE"]}


class A_AEntradaExtra(unittest.TestCase):

    def test_A1_deterministica(self):
        self.assertEqual(json.dumps(R.montar(RAIZ), sort_keys=True), json.dumps(extra(), sort_keys=True))

    def test_A2_a_contagem_commitada_e_a_que_a_arvore_produz(self):
        self.assertEqual(json.loads(CONTAGEM_COMMITADA.read_text(encoding="utf-8")), extra()["CONTAGEM"],
                         "regere: python3 pacote/rete_voci_dati.py --contagem " + str(CONTAGEM_COMMITADA))

    def test_A3_as_seis_gavetas_e_todas_com_objetos(self):
        e = extra()
        self.assertEqual(list(e["ITENS_POR_FERRAMENTA"]), list(R.COMPARTIMENTOS))
        for c in R.COMPARTIMENTOS:
            self.assertTrue(objs(e, c), c)

    def test_A4_o_pote_aceita_tudo_sem_recusar_nada(self):
        e = extra()
        pote = POTE.adaptar(e)
        self.assertEqual(pote["RECUSADOS"], [])
        for c in R.COMPARTIMENTOS:
            self.assertEqual(len(pote["COMPARTIMENTOS"][c]["OBJETOS"]), len(objs(e, c)), c)
        self.assertEqual(POTE.conferir_pote(pote), [])

    def test_A5_ficheiros_lidos_sao_rastreados_e_o_blob_bate(self):
        rastreados = set(subprocess.run(["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True).stdout.split())
        if not rastreados:
            self.skipTest("sem git")
        for f in extra()["FICHEIROS_LIDOS"]:
            self.assertIn(f["CAMINHO"], rastreados)
            b = subprocess.run(["git", "hash-object", f["CAMINHO"]], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
            self.assertEqual(b, f["GIT_BLOB"])


class B_ProvaEPortao(unittest.TestCase):

    def test_B1_toda_prova_esta_na_linhagem_e_passou_g0(self):
        e = extra()
        lin = linhagem(e)
        for c in R.COMPARTIMENTOS:
            for o in objs(e, c):
                for p in o["PROVA"]:
                    x = lin[(p["CORRIDA_UPSTREAM"], p["ITEM_ID"])]
                    self.assertEqual(x["G0"], "PASSOU", o["OBJETO_ID"])
                    for k in ("SOURCE_ID", "RAW_OBSERVATION_ID"):
                        self.assertEqual(x[k], p[k])

    def test_B2_o_veredito_de_g0_e_o_do_motor_recalculado(self):
        for x in extra()["LINEAGE"]:
            cap = x["COLHIDO_EM"] if not e_ignorancia(x["COLHIDO_EM"]) else None
            if cap is None and x["CAPTURA_PARA_G0"] == "LIMITE_INFERIOR=PUBLICADO_EM":
                cap = x["PUBLICADO_EM"]
            if cap is None and x["CAPTURA_PARA_G0"] == "LIMITE_INFERIOR=ULTIMO_TRABALHO_CONTADO":
                cap = x["FACT_TIME"].split("/")[-1]
            passou, falta = portao_g0({"ITEM_ID": x["ITEM_ID"], "SOURCE_ID": x["SOURCE_ID"],
                                       "RAW_OBSERVATION_ID": x["RAW_OBSERVATION_ID"], "FACT_TIME": x["FACT_TIME"],
                                       "FACT_TIME_BASIS": x["FACT_TIME_BASIS"], "CAPTURED_AT": cap})
            self.assertEqual(x["G0"], "PASSOU" if passou else "BLOQUEADO_EM_G0", x["ITEM_ID"])
            self.assertEqual(x["G0_FALTA"], sorted(falta))

    def test_B3_bloqueado_em_g0_vira_lacuna_contada_e_nao_objeto(self):
        e = extra()
        bloq = {x["ITEM_ID"] for x in e["LINEAGE"] if x["G0"] != "PASSOU"}
        self.assertTrue(bloq)
        self.assertEqual(bloq, {g["ITEM_ID"] for g in e["GAPS"] if g.get("MOTIVO") == "BLOQUEADO_EM_G0"})
        usados = {p["ITEM_ID"] for c in R.COMPARTIMENTOS for o in objs(e, c) for p in o["PROVA"]}
        self.assertFalse(bloq & usados)

    def test_B4_marca_do_tipo_em_todo_objeto(self):
        for c in R.COMPARTIMENTOS:
            for o in objs(extra(), c):
                self.assertIn(o["CHAVES"]["TIPO_DO_DADO"], R.TIPOS_DO_DADO)
                self.assertEqual(o["ESTADO"], "EXPERIMENTAL_CANDIDATE")

    def test_B5_nao_sei_por_extenso_nunca_vazio(self):
        for c in R.COMPARTIMENTOS:
            for o in objs(extra(), c):
                for k, v in list(o["CHAVES"].items()) + [(k, v) for p in o["PROVA"] for k, v in p.items()]:
                    if e_ignorancia(v):
                        self.assertEqual(v, NAO_SEI, f"{o['OBJETO_ID']}.{k} = {v!r}")

    def test_B6_captura_limite_inferior_so_bloqueia_a_mais(self):
        L = R.Livro(RAIZ)
        # facto que comeca DEPOIS da publicacao: sem captura real, bloqueia
        p = L.item("voices", "VOZES", "x1", source_id="IT-T1-014", document_id="d", url="https://x.it/a",
                   publicado="2026-06-01", colhido=NAO_SEI, fact_time="2026-07-01", base="b",
                   captura_g0="2026-06-01", base_captura="LIMITE_INFERIOR=PUBLICADO_EM")
        self.assertIsNone(p)
        self.assertIn("FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA", L.linhagem[-1]["G0_FALTA"])
        self.assertEqual(L.linhagem[-1]["COLHIDO_EM"], NAO_SEI)
        # e sem limite nenhum, NAO SEI bloqueia (nunca passa)
        self.assertIsNone(L.item("voices", "VOZES", "x2", source_id="IT-T1-014", document_id="d", url="u",
                                 publicado=NAO_SEI, colhido=NAO_SEI, fact_time="2026-07-01", base="b"))


class C_Gavetas(unittest.TestCase):

    def test_C1_meta_observado_em_31_08_nunca_hoje(self):
        meta = [o for o in objs(extra(), "competitors") if o["OBJETO_ID"].startswith("RVD-META-")]
        self.assertGreater(len(meta), 380)
        for o in meta:
            self.assertEqual(o["CHAVES"]["OBSERVADO_EM"], "observado em 31/08/2026")
            est = o["CHAVES"]["ESTADO_NA_OBSERVACAO"]
            self.assertTrue(est == NAO_SEI or est.startswith(("ATIVO (observado em 31/08/2026",
                                                              "INATIVO (observado em 31/08/2026")), est)
            self.assertTrue(o["PROVA"][0]["COLHIDO_EM"].startswith("2026-08-31"))
            self.assertNotIn("hoje", R._NEGA_HOJE.sub("", json.dumps(o, ensure_ascii=False).lower()))

    def test_C2_pagina_fora_do_agro_fica_de_fora_e_contada(self):
        e = extra()
        self.assertFalse([o for o in objs(e, "competitors") if o["CHAVES"].get("PAGE_ID") == "101167338588947"])
        self.assertEqual(sum(1 for r in e["RECUSADOS_PELO_ADAPTADOR"] if r["MOTIVO"].startswith("PAGINA_FORA_DO_AGRO")), 11)

    def test_C3_serie_so_com_dois_pontos_e_mesma_unidade(self):
        series = [o for o in objs(extra(), "market") if o["CHAVES"]["TIPO_DO_DADO"] == "SERIE"]
        self.assertTrue(series)
        for o in series:
            pts = o["CHAVES"]["PONTOS"]
            self.assertGreaterEqual(len(pts), 2)
            self.assertEqual(len({p["UNIDADE"] for p in pts}), 1)
            self.assertEqual(len({p["PERIODO"] for p in pts}), len(pts))
            self.assertEqual(o["CHAVES"]["UNIT"], pts[0]["UNIDADE"])

    def test_C4_series_regra_isolada(self):
        def livro(pontos):
            L = R.Livro(RAIZ)
            prova = {"ITEM_ID": "i"}
            for (unid, per, fim) in pontos:
                R._ponto(L, "OLIVO", "Bari", "PRODUTOR", unid, per, 1.0, prova, fim=fim)
            R.series(L)
            return [o for o in L.itens["market"] if o["CHAVES"]["TIPO_DO_DADO"] == "SERIE"]
        self.assertEqual(livro([("EUR/kg", "a", "2026-01-01")]), [])
        self.assertEqual(livro([("EUR/kg", "a", "2026-01-01"), ("EUR/t", "b", "2026-02-01")]), [])
        self.assertEqual(livro([("EUR/kg", "a", "2026-01-01"), ("EUR/kg", "a", "2026-01-01")]), [])
        s = livro([("EUR/kg", "b", "2026-02-01"), ("EUR/kg", "a", "2026-01-01")])
        self.assertEqual(len(s), 1)
        self.assertEqual([p["PERIODO"] for p in s[0]["CHAVES"]["PONTOS"]], ["a", "b"])

    def test_C5_ismea_entra_com_a_regua_da_casa_e_o_source_id_do_registo(self):
        ismea = [o for o in objs(extra(), "market") if o["OBJETO_ID"].startswith("RVD-ISMEA-")]
        self.assertGreaterEqual(len(ismea), 15)
        d = json.loads((RAIZ / R.FICHEIROS["MERCADO_CURADO"]).read_text(encoding="utf-8"))
        pub = {r["CANONICAL_RECORD_ID"]: r["publication_date"] for r in d["RECORDS"]}
        lidos = 0
        for o in ismea:
            self.assertEqual(o["PROVA"][0]["SOURCE_ID"], "IT-T10-001")
            self.assertIn(o["CHAVES"]["UNIT"], ("EUR/kg", "EUR/t", "EUR/q", "EUR/hl", "EUR/l"))
            if "lido nesta data" in pub[o["OBJETO_ID"].split("-", 2)[2].rsplit("-", 1)[0]]:
                # «lido nesta data» e leitura, nao publicacao
                lidos += 1
                self.assertEqual(o["PROVA"][0]["PUBLICADO_EM"], NAO_SEI)
                self.assertEqual(o["PROVA"][0]["COLHIDO_EM"], "2026-09-02")
        self.assertGreater(lidos, 0)

    def test_C6_publicacao_nao_vira_tempo_do_facto_nas_vozes(self):
        d = json.loads((RAIZ / R.FICHEIROS["VOZES"]).read_text(encoding="utf-8"))
        per = {r["CANONICAL_RECORD_ID"]: r for r in d["RECORDS"]}
        for o in objs(extra(), "voices"):
            r = per[o["OBJETO_ID"].replace("RVD-VOZ-", "")]
            self.assertEqual(o["CHAVES"]["FACT_TIME"], r["periodo"])
            self.assertEqual(o["PROVA"][0]["FACT_TIME"], r["periodo"])

    def test_C7_ciencia_o_facto_e_a_publicacao_e_o_estudo_fica_como_veio(self):
        t6 = [o for o in objs(extra(), "science") if o["OBJETO_ID"].startswith("RVD-T6-")]
        self.assertTrue(t6)
        lin = linhagem(extra())
        ens = json.loads((RAIZ / R.FICHEIROS["T6_TRABALHOS"]).read_text(encoding="utf-8"))
        unidades = {u["DOI"]: u for u in ens["UNIDADES"]}
        for o in t6:
            x = lin[(o["PROVA"][0]["CORRIDA_UPSTREAM"], o["PROVA"][0]["ITEM_ID"])]
            self.assertIn("PUBLICACAO", x["FACT_TIME_BASIS"])
            self.assertEqual(o["CHAVES"]["STUDY_PERIOD"], R._v(unidades[o["CHAVES"]["DOI"]]["PERIODO_DO_ESTUDO"]))
            self.assertNotEqual(o["CHAVES"]["STUDY_PERIOD"], o["PROVA"][0]["PUBLICADO_EM"])

    def test_C8_mur_sem_data_bloqueia_e_so_enriquece(self):
        e = extra()
        mur = [x for x in e["LINEAGE"] if x["ITEM_ID"].startswith("RVD:MUR:")]
        self.assertEqual(len(mur), 278)
        self.assertTrue(all(x["G0"] == "BLOQUEADO_EM_G0" for x in mur))
        ligados = [a for o in objs(e, "science") for a in (o["CHAVES"].get("PESQUISADORES") or
                   o["CHAVES"].get("AUTORES_COM_AFILIACAO_ITALIANA") or []) if a["MUR"] != NAO_SEI]
        self.assertTrue(ligados)
        self.assertEqual(set(ligados[0]["MUR"]), {"NOME_NO_MUR", "FASCIA", "ATENEO", "SSD_2024", "LIGACAO"})

    def test_C9_rendimento_provado_so_pela_propria_fonte_e_contado_da_linhagem(self):
        e = extra()
        for o in objs(e, "sources"):
            sid = o["CHAVES"]["SOURCE_ID"]
            self.assertEqual(o["ESPECIE"], "RENDIMENTO_DE_FONTE")
            self.assertTrue(all(p["SOURCE_ID"] == sid for p in o["PROVA"]))
            lin = [x for x in e["LINEAGE"] if x["SOURCE_ID"] == sid]
            self.assertEqual(o["CHAVES"]["ITENS_LIDOS"], len(lin))
            self.assertEqual(o["CHAVES"]["ITENS_QUE_PASSARAM_G0"], sum(1 for x in lin if x["G0"] == "PASSOU"))

    def test_C10_archive_e_o_que_esta_entrada_produziu_sem_mudar_especie(self):
        e = extra()
        gerais = {o["OBJETO_ID"]: o for c in R.GERAIS for o in objs(e, c)}
        self.assertEqual(len(objs(e, "archive")), len(gerais))
        for a in objs(e, "archive"):
            o = gerais[a["CHAVES"]["OBJETO_DE_ORIGEM"]]
            self.assertEqual((a["ESPECIE"], a["PROVA"], a["CHAVES"]["TIPO_DO_DADO"]),
                             (o["ESPECIE"], o["PROVA"], o["CHAVES"]["TIPO_DO_DADO"]))


class D_DadoPessoalEFonte(unittest.TestCase):

    def test_D1_nenhum_contacto_nenhum_resumo_nenhum_canal_pessoal(self):
        texto = json.dumps(extra(), ensure_ascii=False)
        self.assertIsNone(R._CONTATO.search(texto))
        for proibido in ('"ABSTRACT"', "PUBLIC_CHANNELS_DECLARED", "twitter.com", "EGRESS_IP", "@gmail"):
            self.assertNotIn(proibido, texto)

    def test_D2_voz_sem_pessoa_e_agricultor_sem_texto_do_curador(self):
        for o in objs(extra(), "voices"):
            self.assertEqual(o["CHAVES"]["SPEAKER_ID"], NAO_SEI)
        r = {"tipo": "VOZ_AGRICULTOR_IDENTIFICADO", "o_que_prova": "Que Fulano, agricultor de Ravalle..."}
        self.assertNotIn("Fulano", R._porque_da_voz(r))

    def test_D3_source_id_vem_do_atlas_ou_e_nao_sei(self):
        conhecidos = {f["SOURCE_ID"] for f in R._identidades(RAIZ)}
        for x in extra()["LINEAGE"]:
            self.assertTrue(x["SOURCE_ID"] == NAO_SEI or x["SOURCE_ID"] in conhecidos, x["SOURCE_ID"])
            self.assertFalse(str(x["SOURCE_ID"]).startswith("IT-SRC-"))

    def test_D4_dominio_com_varias_fichas_escolhe_pelo_caminho_ou_nao_sei(self):
        L = R.Livro(RAIZ)
        R._ATLAS_CACHE[str(RAIZ) + "#teste"] = None
        fichas = [{"SOURCE_ID": "A", "URL": "https://x.eu/agri/precos", "NATIVE_ID": "", "NAME": ""},
                  {"SOURCE_ID": "B", "URL": "https://x.eu/saude", "NATIVE_ID": "", "NAME": ""}]
        velho = R._ATLAS_CACHE.get(str(RAIZ))
        try:
            R._ATLAS_CACHE[str(RAIZ)] = fichas
            self.assertEqual(R._source_id_do_atlas(L, "https://www.x.eu/agri/precos?y=1"), "A")
            self.assertEqual(R._source_id_do_atlas(L, "https://x.eu/outra/coisa"), NAO_SEI)
            self.assertEqual(R._source_id_do_atlas(L, "https://www.youtube.com/watch?v=abc"), NAO_SEI)
            self.assertEqual(R._source_id_do_atlas(L, "nao e url"), NAO_SEI)
        finally:
            if velho is None:
                R._ATLAS_CACHE.pop(str(RAIZ), None)
            else:
                R._ATLAS_CACHE[str(RAIZ)] = velho
            R._ATLAS_CACHE.pop(str(RAIZ) + "#teste", None)

    def test_D5_publicacao_curada(self):
        self.assertEqual(R._publicacao("2026-09-02 (lido nesta data; a fonte nao data)"), (NAO_SEI, "2026-09-02"))
        self.assertEqual(R._publicacao("2026-08-27"), ("2026-08-27", NAO_SEI))
        self.assertEqual(R._publicacao("NAO_SEI — pagina sem data"), (NAO_SEI, NAO_SEI))


class E_PortaoDeSaidaEJunta(unittest.TestCase):

    def _um(self, e, comp, pref):
        return next(o for o in objs(e, comp) if o["OBJETO_ID"].startswith(pref))

    def test_E1_conferir_apanha_serie_de_um_ponto_hoje_contacto_tipo_e_prova_bloqueada(self):
        e = extra()
        self.assertEqual(R.conferir(e), [])
        s = self._um(e, "market", "RVD-SERIE-")
        s["CHAVES"]["PONTOS"] = s["CHAVES"]["PONTOS"][:1]
        m = self._um(e, "competitors", "RVD-META-")
        m["CHAVES"]["ESTADO_NA_OBSERVACAO"] = "ATIVO hoje"
        v = self._um(e, "voices", "RVD-VOZ-")
        v["CHAVES"]["CONTATO"] = "fulano@exemplo.it"
        t = self._um(e, "science", "RVD-T6-")
        t["CHAVES"]["TIPO_DO_DADO"] = "OPINIAO"
        bloq = next(x for x in e["LINEAGE"] if x["G0"] != "PASSOU")
        f = self._um(e, "market", "RVD-EU_")
        f["PROVA"] = [dict(f["PROVA"][0], ITEM_ID=bloq["ITEM_ID"], CORRIDA_UPSTREAM=bloq["CORRIDA_UPSTREAM"])]
        txt = " | ".join(R.conferir(e))
        for alvo in ("serie com menos de 2 pontos", "diz «hoje»", "contacto pessoal", "sem marca do tipo",
                     "bloqueada em G0"):
            self.assertIn(alvo, txt)

    def test_E2_juntar_a_corrida_manda_no_cabecalho_e_so_acrescenta(self):
        corrida = json.loads(CORRIDA_SINTETICA.read_text(encoding="utf-8"))
        e = extra()
        j = R.juntar(corrida, e)
        for k in ("INTELLIGENCE_RUN_ID", "SOURCE_HEAD", "CORTE", "RESULT_STATE"):
            self.assertEqual(j[k], corrida[k])
        self.assertEqual(len(j["LINEAGE"]), len(corrida["LINEAGE"]) + len(e["LINEAGE"]))
        pote = POTE.adaptar(j)
        so = POTE.adaptar(corrida)
        self.assertEqual(len(pote["RECUSADOS"]), len(so["RECUSADOS"]))
        for c in R.COMPARTIMENTOS:
            self.assertEqual(len(pote["COMPARTIMENTOS"][c]["OBJETOS"]),
                             len(so["COMPARTIMENTOS"][c]["OBJETOS"]) + len(objs(e, c)), c)
        self.assertTrue(all(p["INTELLIGENCE_RUN_ID"] == corrida["INTELLIGENCE_RUN_ID"]
                            for o in pote["COMPARTIMENTOS"]["voices"]["OBJETOS"] for p in o["PROVA"]))

    def test_E3_juntar_recusa_duplicado_payload_v1_e_extra_reprovada(self):
        corrida = json.loads(CORRIDA_SINTETICA.read_text(encoding="utf-8"))
        e = extra()
        j = R.juntar(corrida, e)
        with self.assertRaises(R.LeiViolada):
            R.juntar(j, e)
        with self.assertRaises(R.LeiViolada):
            R.juntar({"SCHEMA": POTE.V1.CONTRATO, "INTELLIGENCE_RUN_ID": "x"}, e)
        ruim = copy.deepcopy(e)
        objs(ruim, "voices")[0]["CHAVES"]["TIPO_DO_DADO"] = "X"
        with self.assertRaises(R.LeiViolada):
            R.juntar(corrida, ruim)

    def test_E4_o_script_unico_escreve_e_recusa_o_portal(self):
        with tempfile.TemporaryDirectory() as d:
            saida, pote = Path(d) / "EXTRA.json", Path(d) / "pote.json"
            r = subprocess.run([sys.executable, str(RAIZ / "pacote" / "rete_voci_dati.py"), "--saida", str(saida),
                                "--juntar", str(CORRIDA_SINTETICA), "--pote", str(pote)],
                               capture_output=True, text=True, cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(saida.read_text(encoding="utf-8"))["SCHEMA"], R.CONTRATO)
            self.assertEqual(json.loads(pote.read_text(encoding="utf-8"))["SCHEMA"], POTE.CONTRATO)
            for args in (["--pote", str(RAIZ / "italia-portale" / "client" / "outro.js")],
                         ["--saida", str(RAIZ / "italia-portale" / "client" / "sintonia-pote.js")]):
                r = subprocess.run([sys.executable, str(RAIZ / "pacote" / "rete_voci_dati.py")] + args,
                                   capture_output=True, text=True, cwd=d)
                self.assertEqual(r.returncode, 3, args)
            self.assertFalse((RAIZ / "italia-portale" / "client" / "outro.js").exists())


if __name__ == "__main__":
    unittest.main()
