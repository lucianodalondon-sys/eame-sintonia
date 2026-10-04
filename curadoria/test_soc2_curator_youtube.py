#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC2 — o Curator encaminha o YouTube para o Scrap (e o LinkedIn pelo site).

O que estes testes guardam:

  1. uma candidata YouTube com channel_id no endereco deixa de morrer em
     CAPABILITY: se o canal ja tem SOURCE_ID, reusa-o (nunca um segundo); se nao
     tem, segue o circuito normal (territorio -> SOURCE_ID -> BUILD_CONTRACT);
  2. sem channel_id no endereco (@handle, /user/) continua NAO SEI — sem fabricar;
  3. o contrato novo NOMEIA a fase do Scrap, passa a validacao, e a validacao
     reprova-o se o Scrap deixar de declarar a rota;
  4. VALIDATE_ROUTE da rota do Scrap le a matriz dele (nao o robots) e para em
     CANARY_PENDING; o canario do worker nunca promove YouTube;
  5. o bloco 4 do pacote G1 migra so com prova, e a 2.a passagem faz zero;
  6. o coletor JS devolve um resultado por fonte, em vez de rebentar a corrida;
  7. o LinkedIn pelo site so candidata o que a casa nao conhece.

Tudo em ficheiros temporarios: nao toca a lane real.
"""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))
sys.path.insert(0, str(RAIZ / "scripts" / "desbloqueio"))

import fila as F                      # noqa: E402
import fonte_nova as FN               # noqa: E402
import lifecycle as LC                # noqa: E402
import rota_do_scrap_youtube as RSY   # noqa: E402
import validar_contratos as VC        # noqa: E402
import worker as W                    # noqa: E402

CANAL_CONHECIDO = "UC1vKirvt0hzsqE9zQAs9nTw"
CANAL_NOVO = "UCXUG407gp3CnWnfS3ycijhA"
CANAL_DUPLO = "UCCMlh614oidOkq-HNSa9RVA"
DECLARADO = RSY.o_que_o_scrap_declara()


def _linha_tabela(sid, canal, match="YES"):
    return {"SOURCE_ID": sid, "TERRITORY": "T2", "BATCH_ID": "LOTE-YOUTUBE-CANAL",
            "OUTPUT_TYPE": "HTML", "SOURCE_NATIVE_ID": canal,
            "ACQUISITION": {"STRATEGY": "CUSTOM_ADAPTER", "ADAPTER_ID": "CANAL_PUBLICO_YOUTUBE_V1",
                            "CHANNEL_ID": canal, "MAX_TARGETS": 15},
            "SONDAGEM": {"IDENTITY_MATCH": match, "SONDADO_EM": "2026-09-20"}}


def _linha_livro(sid, canal):
    return {"SOURCE_ID": sid, "TERRITORY": "T2", "BATCH_ID": "LOTE-YOUTUBE-FEED",
            "NAME": "Fonte %s — Youtube ufficiale" % sid, "OWNER": "Fonte",
            "CANONICAL_ENTRY_URL": "https://www.youtube.com/channel/%s" % canal,
            "SOURCE_NATIVE_ID": canal, "SOURCE_NATIVE_ID_KIND": "YOUTUBE_CHANNEL_ID",
            "CARACTERIZACAO": {"X": "NAO SEI"},
            "ACQUISITION": {"STRATEGY": "YOUTUBE_CHANNEL_FEED", "CHANNEL_ID": canal,
                            "FEED_URL": "https://www.youtube.com/feeds/videos.xml?channel_id=%s" % canal,
                            "MAX_TARGETS": 15},
            "IDENTITY": {"STRATEGY": "CONTENT_CAPTURE",
                         "CAPTURES": {"video": {"FROM": "FEED", "FIELD": "yt:videoId"}},
                         "DOCUMENT_ID": "%s:YT:{video.videoId}" % sid, "FACT_TIME": "UNKNOWN"},
            "EXPECTED_FAILURES": ["x = FAILED"], "FAIL_CLOSED_RULE": "FAILED",
            "FALLBACK": "nenhum", "NEGATIVE_CONTROL": {"esperado": "FAILED"},
            "ROUTE_POLICY_STATUS": "ROBOTS_DISALLOWED", "SOURCE_CONTRACT_HASH": "velho"}


class _Lane(unittest.TestCase):
    """Redireciona TODO o estado do worker e as leituras do RSY para uma pasta."""

    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="soc2-")))
        alvos = {(F, "FILA"): "fila.json", (LC, "LIVRO"): "livro.json",
                 (W, "ALLOCATION"): "alloc.json", (W, "EVIDENCIA"): "evid.json",
                 (W, "PULSO"): "pulso.json", (W, "CONTRATOS"): "contratos.json",
                 (FN, "FILA"): "candidatas.json", (RSY, "TABELA"): "tabela.json",
                 (RSY, "LIVRO"): "contratos.json", (RSY, "ALLOCATION"): "alloc.json",
                 (RSY, "CONTRATOS_MJS"): "contratos.mjs"}
        for (mod, attr), nome in alvos.items():
            self.addCleanup(setattr, mod, attr, getattr(mod, attr))
            setattr(mod, attr, self.tmp / nome)
        W.ALLOCATION.write_text(json.dumps({"DATASET": "SOURCE-ID-ALLOCATION-V1",
                                            "MAIOR_POR_TERRITORIO_ANTES": {"T7": 14},
                                            "ATRIBUIDOS": 0, "NOVAS": []}), encoding="utf-8")
        RSY.TABELA.write_text(json.dumps({"FONTES": [
            _linha_tabela("IT-T2-025", CANAL_CONHECIDO),
            _linha_tabela("IT-T2-090", CANAL_DUPLO), _linha_tabela("IT-T2-091", CANAL_DUPLO)]}),
            encoding="utf-8")
        W.CONTRATOS.write_text(json.dumps({"FONTES": []}), encoding="utf-8")
        RSY.CONTRATOS_MJS.write_text('export const X = {\n  "IT-T8-001": {\n    SOURCE_NATIVE_ID: "UCUs2Mg7jvUTRt7_MSOFYM5Q",\n  },\n};\n',
                                     encoding="utf-8")

    def _qualify(self, cand, nome, url):
        doc = FN.carregar()
        doc["CANDIDATAS"].append({"CANDIDATA_ID": cand, "TIPO": "YOUTUBE", "NOME": nome,
                                  "URL": url, "PAIS": "IT", "ESTADO": "EM_ANALISE", "SOURCE_ID": None,
                                  # SOC-ONDA2: identidade provada = o site oficial aponta para o canal
                                  "ONDE_VIU": "declarado no site oficial do dono: https://www.vini.example.it/"})
        FN.gravar(doc)
        F.enfileirar(cand, F.QUALIFY, priority=30, motivo="teste")
        return W.correr(max_tarefas=1, pausa=0, verboso=False)[0]

    def _alloc(self):
        return json.loads(W.ALLOCATION.read_text(encoding="utf-8"))["NOVAS"]


class OQualifyDoYoutube(_Lane):
    def test_canal_ja_conhecido_reusa_o_source_id(self):
        r = self._qualify("CAND-Y001", "ARPA Lazio — Youtube",
                          "https://www.youtube.com/channel/%s/videos" % CANAL_CONHECIDO)
        self.assertEqual(r["RESULTADO"], "OK")
        self.assertEqual(self._alloc(), [], "canal com SOURCE_ID nao ganha um segundo")
        self.assertEqual([t for t in F._ler()["TAREFAS"] if t["TASK_TYPE"] == F.BUILD_CONTRACT], [])
        ev = json.loads(W.EVIDENCIA.read_text(encoding="utf-8"))["PROVAS"][-1]["DADOS"]
        self.assertEqual(ev["SOURCE_ID_REAL"], "IT-T2-025")
        self.assertTrue(ev["JA_TINHA_IDENTIDADE"])

    def test_canal_de_contrato_escrito_a_mao_tambem_conta(self):
        self.assertEqual(RSY.canal_conhecido("UCUs2Mg7jvUTRt7_MSOFYM5Q"), ["IT-T8-001"])

    def test_canal_novo_segue_o_circuito_e_guarda_o_canal(self):
        r = self._qualify("CAND-Y002", "Consorzio Tutela Vini — Youtube ufficiale",
                          "https://www.youtube.com/channel/%s" % CANAL_NOVO)
        self.assertEqual(r["RESULTADO"], "OK")
        novas = self._alloc()
        self.assertEqual(len(novas), 1)
        self.assertEqual(novas[0]["FAMILY"], "YOUTUBE")
        self.assertEqual(novas[0]["SOURCE_NATIVE_ID"], CANAL_NOVO)
        sid = novas[0]["SOURCE_ID"]
        bc = [t for t in F._ler()["TAREFAS"] if t["TASK_TYPE"] == F.BUILD_CONTRACT]
        self.assertEqual([t["SOURCE_ID"] for t in bc], [sid])
        self.assertEqual(LC.estado_de(sid), LC.CONTRACT_PENDING)

    def test_territorio_nao_sei_nao_fabrica(self):
        r = self._qualify("CAND-Y003", "Olio Officina — Youtube ufficiale",
                          "https://www.youtube.com/channel/%s" % CANAL_NOVO)
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertEqual(self._alloc(), [])
        self.assertEqual(LC.estado_de("CAND-Y003"), LC.SEMANTIC_REVIEW)

    def test_handle_sem_channel_id_e_nao_sei(self):
        for url in ("https://www.youtube.com/@agri", "https://www.youtube.com/user/agri",
                    "https://www.youtube.com/playlist?list=PL123"):
            self.assertIsNone(RSY.channel_id_da_url(url), url)
        r = self._qualify("CAND-Y004", "Canale Agricoltura", "https://youtube.com/@agri")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertEqual(LC.estado_de("CAND-Y004"), LC.CAPABILITY_BLOCK)
        self.assertIn("NAO SEI", r["PORQUE"])
        self.assertEqual(self._alloc(), [])

    def test_canal_de_duas_fontes_e_colisao(self):
        r = self._qualify("CAND-Y005", "Consorzio Tutela Vini — Youtube",
                          "https://www.youtube.com/channel/%s" % CANAL_DUPLO)
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertEqual(LC.estado_de("CAND-Y005"), LC.SEMANTIC_REVIEW)
        self.assertEqual(self._alloc(), [])

    def test_qualify_nunca_promove_ready(self):
        self._qualify("CAND-Y006", "Consorzio Tutela Vini — Youtube ufficiale",
                      "https://www.youtube.com/channel/%s" % CANAL_NOVO)
        self.assertNotIn(LC.READY_FOR_COLLECTION, LC.snapshot().values())


class OContratoNomeiaOScrap(_Lane):
    def _ate_ao_contrato(self):
        self._qualify("CAND-Y010", "Consorzio Tutela Vini — Youtube ufficiale",
                      "https://www.youtube.com/channel/%s" % CANAL_NOVO)
        sid = self._alloc()[0]["SOURCE_ID"]
        W.correr(max_tarefas=1, pausa=0, verboso=False)          # BUILD_CONTRACT
        return sid

    def test_build_contract_escreve_a_rota_do_scrap_e_valida(self):
        sid = self._ate_ao_contrato()
        c = {x["SOURCE_ID"]: x for x in json.loads(W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}[sid]
        aq = c["ACQUISITION"]
        self.assertEqual(aq["STRATEGY"], "SCRAP_FASE")
        self.assertEqual((aq["EXECUTOR"], aq["FASE"]), ("scrap-colheita", "canal-youtube"))
        self.assertEqual(aq["FILTROS"], {"canal_id": CANAL_NOVO})
        self.assertNotIn("feeds/videos.xml", json.dumps(c))
        ok, mau = VC.validar([c])
        self.assertEqual(mau, [])
        self.assertEqual(LC.estado_de(sid), LC.CANARY_PENDING)

    def test_validate_route_le_a_matriz_e_para_em_canary_pending(self):
        sid = self._ate_ao_contrato()
        r = W.correr(max_tarefas=1, pausa=0, verboso=False)[0]     # VALIDATE_ROUTE
        self.assertEqual((r["TASK_TYPE"], r["RESULTADO"]), (F.VALIDATE_ROUTE, "OK"))
        pend = [t for t in F._ler()["TAREFAS"] if t["STATUS"] == F.PENDING]
        self.assertEqual(pend, [], "a rota do Scrap nao enfileira o canario do worker")
        self.assertEqual(LC.estado_de(sid), LC.CANARY_PENDING)
        self.assertNotIn(LC.READY_FOR_COLLECTION, LC.snapshot().values())

    def test_validate_route_para_se_o_scrap_nao_confere(self):
        aq = RSY.acquisition(CANAL_NOVO, DECLARADO)
        aq["FILTROS"] = {"canal_id": CANAL_CONHECIDO}
        res, det = W.etapa_validate_route("IT-T7-099", {"ACQUISITION": aq})
        self.assertEqual((res, det["CLASSE"], det["PORTAO"]), ("BLOCK", "CAPABILITY", "matriz do Scrap"))

    def test_o_canario_do_worker_nunca_promove_youtube(self):
        c = {"ACQUISITION": RSY.acquisition(CANAL_NOVO, DECLARADO)}
        res, det = W.etapa_canary("IT-T7-099", c)
        self.assertEqual((res, det["CLASSE"]), ("BLOCK", "CAPABILITY"))


class AValidacaoLeOScrapDeHoje(unittest.TestCase):
    def _aq(self, **k):
        aq = RSY.acquisition(CANAL_NOVO, DECLARADO)
        aq.update(k)
        return aq

    def test_rota_certa_confere(self):
        self.assertTrue(RSY.conferir(self._aq(), DECLARADO)[0])

    def test_filtro_de_outro_canal_reprova(self):
        self.assertFalse(RSY.conferir(self._aq(FILTROS={"canal_id": CANAL_CONHECIDO}), DECLARADO)[0])

    def test_matriz_que_deixa_de_permitir_reprova(self):
        d = dict(DECLARADO, DECISAO="ROUTE_NOT_ALLOWED")
        self.assertFalse(RSY.conferir(self._aq(), d)[0])

    def test_fase_que_deixa_de_existir_reprova(self):
        ok, porque = RSY.conferir(self._aq(), {"FASE_EXISTE": False})
        self.assertFalse(ok)
        self.assertIn("deixou de declarar", porque)

    def test_rota_mudada_pelo_scrap_reprova(self):
        self.assertFalse(RSY.conferir(self._aq(ROTA_DECLARADA_PELO_SCRAP="outra"), DECLARADO)[0])

    def test_o_validador_do_curator_reprova_rota_do_scrap_errada(self):
        import escrever_contratos as EC
        n = {"SOURCE_ID": "IT-T7-099", "NOME": "X — Youtube", "TERRITORY": "T7",
             "URL": "https://www.youtube.com/channel/%s" % CANAL_NOVO}
        bom = EC.contrato_youtube_scrap(n, CANAL_NOVO, DECLARADO)
        bom["SOURCE_CONTRACT_VERSION"], bom["SOURCE_CONTRACT_HASH"] = EC.VERSAO, "h"
        self.assertEqual(VC.validar([bom])[1], [])
        mau = copy.deepcopy(bom)
        mau["ACQUISITION"]["FILTROS"] = {"canal_id": CANAL_CONHECIDO}
        falhas = VC.validar([mau])[1]
        self.assertEqual(len(falhas), 1)
        self.assertIn("ROUTE_RESOLVED", falhas[0]["FALHAS"][0])

    def test_o_scrap_declara_a_rota_hoje(self):
        # medido: a fase canal-youtube pede youtube.channel.discovery pela API
        self.assertEqual(DECLARADO["DECISAO"], "ALLOWED")
        # YT-METADADOS (bloco B, 25/09): a fase canal-youtube passou a listar pela
        # PAGINA PUBLICA do canal, sem chave (robots conferido). As duas classes sao
        # rotas permitidas pela matriz; o que este teste guarda e que a rota esta
        # ALLOWED e e uma destas duas — nunca o feed, que continua proibido.
        self.assertIn(DECLARADO["CLASSE"], ("OFFICIAL_API_FREE", "PUBLIC_NATIVE"))


class OBlocoQuatroDoG1(unittest.TestCase):
    def _planear(self, livro, tabela):
        import aplicar_desbloqueio as AD
        L = {c["SOURCE_ID"]: c for c in livro}
        T = {c["SOURCE_ID"]: c for c in tabela}
        nl, nt = copy.deepcopy(L), copy.deepcopy(T)
        acoes, aut = AD.rota_do_scrap(nl, nt, T, DECLARADO)
        AD.invariantes({"FONTES": list(L.values())}, {"FONTES": list(nl.values())},
                       {"FONTES": list(T.values())}, {"FONTES": list(nt.values())},
                       frozenset(), aut)
        return acoes, nl, nt

    def test_duas_passagens_a_segunda_faz_zero(self):
        livro = [_linha_livro("IT-T2-025", CANAL_CONHECIDO)]
        tabela = [_linha_tabela("IT-T2-025", CANAL_CONHECIDO)]
        a1, nl, nt = self._planear(livro, tabela)
        self.assertEqual(sorted(x["ACAO"] for x in a1), ["APLICA", "APLICA"])
        c, t = nl["IT-T2-025"], nt["IT-T2-025"]
        self.assertEqual(c["ACQUISITION"]["STRATEGY"], "SCRAP_FASE")
        self.assertEqual(c["ACQUISITION"]["CHANNEL_ID"], CANAL_CONHECIDO)
        self.assertEqual((c["SOURCE_ID"], c["TERRITORY"], c["BATCH_ID"]),
                         ("IT-T2-025", "T2", "LOTE-YOUTUBE-FEED"))
        self.assertNotEqual(c["SOURCE_CONTRACT_HASH"], "velho")
        self.assertEqual(c["ROTA_DO_SCRAP"]["ANTES"]["ACQUISITION"]["STRATEGY"], "YOUTUBE_CHANNEL_FEED")
        self.assertEqual(t["ACQUISITION"], tabela[0]["ACQUISITION"], "a aquisicao do motor fica")
        self.assertEqual(t["COLETADO_POR"]["FASE"], "canal-youtube")
        a2, _, _ = self._planear(list(nl.values()), list(nt.values()))
        self.assertEqual(sorted(x["ACAO"] for x in a2), ["JA_APLICADA", "JA_APLICADA"])

    def test_sem_identidade_provada_salta(self):
        a, nl, nt = self._planear([_linha_livro("IT-T2-025", CANAL_CONHECIDO)],
                                  [_linha_tabela("IT-T2-025", CANAL_CONHECIDO, match="NO")])
        self.assertEqual([x["ACAO"] for x in a], ["SALTA"])
        self.assertEqual(nl["IT-T2-025"]["ACQUISITION"]["STRATEGY"], "YOUTUBE_CHANNEL_FEED")
        self.assertNotIn("COLETADO_POR", nt["IT-T2-025"])

    def test_canal_diferente_na_tabela_salta(self):
        a, _, _ = self._planear([_linha_livro("IT-T2-025", CANAL_CONHECIDO)],
                                [_linha_tabela("IT-T2-025", CANAL_NOVO)])
        self.assertEqual([x["ACAO"] for x in a], ["SALTA"])

    def test_canal_em_duas_fontes_salta(self):
        a, _, _ = self._planear([_linha_livro("IT-T2-090", CANAL_DUPLO), _linha_livro("IT-T2-091", CANAL_DUPLO)],
                                [_linha_tabela("IT-T2-090", CANAL_DUPLO), _linha_tabela("IT-T2-091", CANAL_DUPLO)])
        self.assertEqual({x["ACAO"] for x in a}, {"SALTA"})

    def test_invariante_morde_se_o_canal_mudar(self):
        import aplicar_desbloqueio as AD
        antes = _linha_livro("IT-T2-025", CANAL_CONHECIDO)
        depois = copy.deepcopy(antes)
        depois["ACQUISITION"]["CHANNEL_ID"] = CANAL_NOVO
        with self.assertRaises(AD.InvarianteQuebrado):
            AD.invariantes({"FONTES": [antes]}, {"FONTES": [depois]}, {"FONTES": []}, {"FONTES": []},
                           frozenset(), {"IT-T2-025"})

    def test_invariante_morde_coletado_por_sem_autorizacao(self):
        import aplicar_desbloqueio as AD
        t = _linha_tabela("IT-T2-025", CANAL_CONHECIDO)
        t2 = dict(t, COLETADO_POR={"FASE": "x"})
        with self.assertRaises(AD.InvarianteQuebrado):
            AD.invariantes({"FONTES": []}, {"FONTES": []}, {"FONTES": [t]}, {"FONTES": [t2]},
                           frozenset(), frozenset())


@unittest.skipUnless(shutil.which("node"), "sem node nesta maquina")
class OColetorJsNaoRebenta(unittest.TestCase):
    def test_fonte_do_scrap_e_resultado_por_fonte(self):
        prog = ("import { CONTRACTS } from './regras/italy_contracts.mjs';"
                "import { alvosDe } from './coleta/italy_pilot_collect.mjs';"
                "const sid = Object.keys(CONTRACTS).find(s => CONTRACTS[s].ACQUISITION"
                " && CONTRACTS[s].ACQUISITION.ADAPTER_ID === 'CANAL_PUBLICO_YOUTUBE_V1');"
                "CONTRACTS[sid].COLETADO_POR = { EXECUTOR: 'scrap-colheita', FASE: 'canal-youtube' };"
                "console.log(JSON.stringify(await alvosDe(sid)));")
        r = subprocess.run(["node", "--input-type=module", "-e", prog], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertTrue(out["erro"].startswith("COLETADO_POR_OUTRO_EXECUTOR: scrap-colheita/canal-youtube"))

    def test_a_marca_passa_da_tabela_para_o_contrato(self):
        txt = (RAIZ / "regras" / "italy_contracts.mjs").read_text(encoding="utf-8")
        self.assertIn("...(linha.COLETADO_POR ? { COLETADO_POR: linha.COLETADO_POR } : {})", txt)


class OLinkedinPeloSite(unittest.TestCase):
    def _medir(self, site, tabela=None, livro=None, atlas=None, outras=()):
        import linkedin_pelo_site as LPS
        cand = {"CANDIDATAS": [{"CANDIDATA_ID": "CAND-L1", "TIPO": "LINKEDIN", "NOME": "Org — Linkedin",
                                "URL": "https://www.linkedin.com/company/org", "PAIS": "IT",
                                "ONDE_VIU": "declarado no site oficial do dono: %s" % site if site else ""}]
                + [{"CANDIDATA_ID": "CAND-X%d" % i, "TIPO": "ORGANIZACAO", "URL": u}
                   for i, u in enumerate(outras)]}
        return LPS, LPS.medir(cand, tabela or {}, livro or {}, atlas or {}, estado_de=lambda s: "X")

    def test_estados(self):
        _, l = self._medir("https://www.org.it/", tabela={"org.it": {"IT-T2-001"}})
        self.assertEqual(l[0]["ESTADO"], "NA_TABELA_DO_COLETOR")
        _, l = self._medir("https://org.it/", livro={"org.it": {"IT-T2-001"}})
        self.assertEqual(l[0]["ESTADO"], "SO_NO_LIVRO_DO_CURATOR")
        _, l = self._medir("https://org.it/", atlas={"org.it": {"IT-T2-001"}}, tabela={"x.it": {"IT-T2-001"}})
        self.assertEqual((l[0]["ESTADO"], l[0]["VIA"]), ("NA_TABELA_DO_COLETOR", "Atlas"))
        _, l = self._medir("https://org.it/", outras=["https://org.it/chi-siamo"])
        self.assertEqual(l[0]["ESTADO"], "JA_CANDIDATA")
        _, l = self._medir(None)
        self.assertEqual(l[0]["ESTADO"], "SEM_SITE_NA_FICHA")

    def test_subdominio_nao_e_o_mesmo_site(self):
        _, l = self._medir("https://appa.provincia.tn.it/", tabela={"provincia.tn.it": {"IT-T2-001"}})
        self.assertEqual(l[0]["ESTADO"], "AUSENTE")
        self.assertEqual(l[0]["PARECIDO_COM"], ["provincia.tn.it"])
        _, l = self._medir("https://news.org.it/", tabela={"org.it": {"IT-T2-001"}})
        self.assertEqual(l[0]["ESTADO"], "AUSENTE", "outro subdominio do mesmo dono nao e o site")

    def test_so_a_ausente_e_candidatada_pela_porta(self):
        LPS, l = self._medir("https://org.it/")
        chamadas = []
        feitas = LPS.candidatar(l + [dict(l[0], ESTADO="NA_TABELA_DO_COLETOR")],
                                registar=lambda *a, **k: chamadas.append((a, k)) or {"CANDIDATA_ID": "CAND-N"})
        self.assertEqual(len(chamadas), 1)
        self.assertEqual(chamadas[0][0][0], "ORGANIZACAO")
        self.assertEqual(chamadas[0][0][3], "https://org.it/")
        self.assertEqual(feitas[0]["CANDIDATA_DO_SITE"], "CAND-N")


if __name__ == "__main__":
    unittest.main(verbosity=2)
