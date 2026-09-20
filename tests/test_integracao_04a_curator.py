# -*- coding: utf-8 -*-
"""INTEGRAÇÃO-04A — as 18 fontes HTML do SOURCE CURATOR entram; as 50 do YouTube não
pelo feed. (BIG-COLLECTION-RELEASE, 2026-09-20: as 50 entraram pela rota do canal.)

O que este ficheiro prova, e por que cada prova existe:

  * a tabela que o motor lê (`regras/italy_contracts_onboarded.json`) tem as 18
    com a forma do curator — o registo da curadoria
    (`curadoria/italy_contracts_curator.json`) fica como registo, nunca como
    segunda fonte de verdade;
  * nenhuma das 50 fontes YouTube entra pelo FEED (`ROBOTS_DISALLOWED_ROUTE`):
    não há executor `YOUTUBE_CHANNEL_FEED`, a tabela não tem essa estratégia nem
    `feeds/videos.xml`, e o dono do contrato não lê o ficheiro da curadoria.
    Desde o BIG-COLLECTION-RELEASE (2026-09-20) as 50 estão na tabela pela rota
    do CANAL (`CUSTOM_ADAPTER` · `CANAL_PUBLICO_YOUTUBE_V1`, `/channel/<ID>/videos`),
    que o MESMO portão de robots aprova — com o CHANNEL_ID do curator, sem
    alteração, e zero código por SOURCE_ID;
  * a evidência das 18 foi promovida para o caminho canónico e os bytes batem
    com o sha256 do manifesto;
  * o Atlas carrega as 84 fichas, cada uma com `ESTADO_04A:` medido — 18
    READY, 50 bloqueadas, 9 com canário FAIL, 7 sem contrato.

    INTEGRAR FONTE != COLETAR FONTE. Nada aqui corre coleta.
"""
import io
import json
import os
import re
import shutil
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONBOARDED = os.path.join(RAIZ, "regras", "italy_contracts_onboarded.json")
DONO = os.path.join(RAIZ, "regras", "italy_contracts.mjs")
MOTOR = os.path.join(RAIZ, "regras", "motor_de_rota.mjs")
CURATOR = os.path.join(RAIZ, "curadoria", "italy_contracts_curator.json")
READY = os.path.join(RAIZ, "curadoria", "READY-FOR-COLLECTION-V1.json")
ATLAS = os.path.join(RAIZ, "docs", "fontes", "ATLAS-DE-FONTES-EAME.md")
SAMPLES = os.path.join(RAIZ, "data", "samples", "IT-SOURCE-SAMPLES")

AS_18 = (
    "IT-T5-039", "IT-T7-017", "IT-T7-021", "IT-T12-009", "IT-T7-031", "IT-T10-018",
    "IT-T12-013", "IT-T5-049", "IT-T7-033", "IT-T10-020", "IT-T10-021", "IT-T8-008",
    "IT-T10-022", "IT-T7-040", "IT-T7-041", "IT-T7-042", "IT-T2-030", "IT-T7-043",
)


def _texto(p):
    with io.open(p, encoding="utf-8") as fh:
        return fh.read()


def _json(p):
    return json.loads(_texto(p))


def _fichas_do_bloco_04a():
    """As fichas do bloco do curator, por SOURCE_ID, com os campos `CHAVE: valor`."""
    t = _texto(ATLAS)
    i = t.index("## ONDA SOURCE CURATOR")
    fichas, atual = {}, None
    for l in t[i:].split("\n"):
        m = re.match(r"^([A-Z_0-9]{3,32}):\s*(.*)$", l)
        if not m:
            continue
        if m.group(1) == "SOURCE_ID":
            atual = m.group(2).strip()
            fichas[atual] = {}
        elif atual:
            fichas[atual][m.group(1)] = m.group(2).strip()
    return fichas


class ATabelaDoDonoTemAs18ESoAs18(unittest.TestCase):

    def setUp(self):
        self.onb = _json(ONBOARDED)
        self.por_id = {r["SOURCE_ID"]: r for r in self.onb["FONTES"]}
        self.cur = _json(CURATOR)
        self.ready = _json(READY)

    def test_o_registo_da_curadoria_diz_18_ready_e_sao_estas(self):
        ready = sorted(f["SOURCE_ID"] for f in self.ready["FONTES"]
                       if f["STATE"] == "READY_FOR_COLLECTION")
        self.assertEqual(sorted(AS_18), ready)
        self.assertEqual(len(self.ready["FONTES"]), 77)

    def test_as_18_estao_na_tabela_com_a_forma_que_o_motor_expande(self):
        for sid in AS_18:
            with self.subTest(source_id=sid):
                r = self.por_id.get(sid)
                self.assertIsNotNone(r, "%s nao esta na tabela onboarded" % sid)
                self.assertEqual("HTML", r["OUTPUT_TYPE"])
                self.assertEqual("LOTE-HTML-ARTIGO", r["BATCH_ID"])
                self.assertEqual("HTML_LINK_DISCOVERY", r["ACQUISITION"]["STRATEGY"])
                self.assertEqual("URL", r["ACQUISITION"]["MATCH"])
                self.assertEqual({"STRATEGY", "MATCH", "INDEX_URL", "LINK_PATTERN", "MAX_TARGETS"},
                                 set(r["ACQUISITION"]))
                re.compile(r["ACQUISITION"]["LINK_PATTERN"])
                self.assertEqual("data/samples/IT-SOURCE-SAMPLES/%s/MANIFEST.json" % sid, r["EVIDENCE"])
                self.assertIn("SOURCE-CURATOR", r["ONBOARDED_BY"])
                self.assertEqual("NAO SEI", r["SONDAGEM"]["ENTRADA_BYTES"],
                                 "o canario nao mediu os bytes da entrada — nao se inventa")
                self.assertTrue(r["SONDAGEM"]["DOCUMENT_ID"].startswith(sid + ":URL:"))

    def test_a_aquisicao_e_a_do_curator_sem_alteracao(self):
        cur = {c["SOURCE_ID"]: c for c in self.cur["FONTES"]}
        for sid in AS_18:
            with self.subTest(source_id=sid):
                self.assertEqual(cur[sid]["ACQUISITION"], self.por_id[sid]["ACQUISITION"])
                self.assertEqual(cur[sid]["CARACTERIZACAO"], self.por_id[sid]["CARACTERIZACAO"],
                                 "a caracterizacao (com os NAO SEI) tem de chegar inteira")

    def test_a_tabela_tem_105_mais_18_mais_50(self):
        self.assertEqual(173, len(self.onb["FONTES"]))
        self.assertEqual(173, len(self.por_id), "SOURCE_ID repetido na tabela")

    def test_as_50_youtube_entram_pela_rota_do_canal_e_nunca_pelo_feed(self):
        cur = {c["SOURCE_ID"]: c for c in self.cur["FONTES"] if c["BATCH_ID"] == "LOTE-YOUTUBE-FEED"}
        self.assertEqual(50, len(cur))
        # o registo do curator continua a dizer o que mediu: a rota do FEED esta barrada
        bloqueadas = [f for f in self.ready["FONTES"] if f["STATE"] == "CONTRACT_READY_ROUTE_BLOCKED"]
        self.assertEqual(50, len(bloqueadas))
        self.assertEqual({"ROBOTS_DISALLOWED_ROUTE"}, {f["BLOCK_REASON"] for f in bloqueadas})
        self.assertEqual(set(cur), {f["SOURCE_ID"] for f in bloqueadas})
        # e a tabela do motor tem as 50 pela rota do CANAL, com o CHANNEL_ID do curator
        self.assertEqual([], [sid for sid in cur if sid not in self.por_id])
        for sid, c in cur.items():
            with self.subTest(source_id=sid):
                r = self.por_id[sid]
                self.assertEqual("LOTE-YOUTUBE-CANAL", r["BATCH_ID"])
                self.assertEqual("HTML", r["OUTPUT_TYPE"])
                self.assertEqual("CUSTOM_ADAPTER", r["ACQUISITION"]["STRATEGY"])
                self.assertEqual("CANAL_PUBLICO_YOUTUBE_V1", r["ACQUISITION"]["ADAPTER_ID"])
                self.assertEqual(c["ACQUISITION"]["CHANNEL_ID"], r["ACQUISITION"]["CHANNEL_ID"])
                self.assertEqual(c["SOURCE_NATIVE_ID"], r["SOURCE_NATIVE_ID"])
                self.assertEqual(c["CARACTERIZACAO"], r["CARACTERIZACAO"],
                                 "a caracterizacao (com os NAO SEI) tem de chegar inteira")
                self.assertEqual("ALLOWED", r["SONDAGEM"]["ROBOTS_GATE"])
                self.assertEqual("YES", r["SONDAGEM"]["IDENTITY_MATCH"])
                self.assertGreater(r["SONDAGEM"]["ALVOS_DESCOBERTOS"], 0)
                self.assertIn("BIG-COLLECTION-RELEASE", r["ONBOARDED_BY"])
                self.assertNotIn("feeds/videos.xml", json.dumps(r["ACQUISITION"]))
                # a identidade e a do curator: videoId nativo, nunca o endereco com `?`
                self.assertEqual("PLATFORM_NATIVE_ID", r["IDENTITY_KIND"])
                self.assertEqual(sid + ":YT:{video.1}", r["IDENTITY"]["DOCUMENT_ID"])
                self.assertEqual("URL", r["IDENTITY"]["CAPTURES"]["video"]["FROM"])
                self.assertRegex(r["SONDAGEM"]["DOCUMENT_ID"], r"^" + re.escape(sid) + r":YT:[A-Za-z0-9_-]{11}$")

    def test_nem_as_9_com_canario_fail_nem_as_7_sem_contrato(self):
        fail = [f["SOURCE_ID"] for f in self.ready["FONTES"] if f["STATE"] == "CONTRACTED_CANARY_FAILED"]
        sem = [s["SOURCE_ID"] for s in self.cur["SEM_CONTRATO"]]
        self.assertEqual(9, len(fail))
        self.assertEqual(7, len(sem))
        self.assertEqual([], [sid for sid in fail + sem if sid in self.por_id])

    def test_a_tabela_nao_tem_estrategia_nem_tipo_de_youtube(self):
        for r in self.onb["FONTES"]:
            self.assertNotEqual("YOUTUBE_CHANNEL_FEED", r["ACQUISITION"]["STRATEGY"], r["SOURCE_ID"])
            self.assertNotEqual("VIDEO_METADATA", r["OUTPUT_TYPE"], r["SOURCE_ID"])
            self.assertNotIn("youtube.com/feeds", json.dumps(r["ACQUISITION"]), r["SOURCE_ID"])


class OMotorNaoAlcancaAs50PeloFeed(unittest.TestCase):

    def test_o_dono_nao_le_o_ficheiro_da_curadoria(self):
        for p in (DONO, MOTOR):
            with self.subTest(ficheiro=os.path.basename(p)):
                t = _texto(p)
                self.assertNotIn("italy_contracts_curator", t,
                                 "o ficheiro da curadoria e registo, nao configuracao lida pelo dono")
                self.assertNotIn("YOUTUBE_CHANNEL_FEED", t, "nao existe executor para o feed")

    def test_a_pasta_coleta_nao_tem_executor_para_o_feed(self):
        pasta = os.path.join(RAIZ, "coleta")
        achados = []
        for nome in sorted(os.listdir(pasta)):
            p = os.path.join(pasta, nome)
            if os.path.isfile(p) and nome.endswith((".mjs", ".py", ".js")):
                if "YOUTUBE_CHANNEL_FEED" in _texto(p) or "italy_contracts_curator" in _texto(p):
                    achados.append(nome)
        self.assertEqual([], achados)

    @unittest.skipUnless(shutil.which("node"), "sem node nesta maquina")
    def test_o_dono_expande_as_18_e_as_50_pela_rota_do_canal(self):
        yt = [c["SOURCE_ID"] for c in _json(CURATOR)["FONTES"] if c["BATCH_ID"] == "LOTE-YOUTUBE-FEED"]
        prog = (
            "import { CONTRACTS, ONBOARDED_IDS } from './regras/italy_contracts.mjs';"
            "import { conferirAquisicao, conferirIdentidade, identidadeDoContrato } from './regras/motor_de_rota.mjs';"
            "const as18 = %s; const yt = %s;"
            "const out = { faltam: as18.filter(i => !CONTRACTS[i] || CONTRACTS[i].ACQUISITION.STRATEGY !== 'HTML_LINK_DISCOVERY'),"
            "  yt_fora: yt.filter(i => !CONTRACTS[i] || !ONBOARDED_IDS.includes(i)),"
            "  yt_pelo_canal: yt.filter(i => CONTRACTS[i] && CONTRACTS[i].ACQUISITION.STRATEGY === 'CUSTOM_ADAPTER' && CONTRACTS[i].ACQUISITION.ADAPTER_ID === 'CANAL_PUBLICO_YOUTUBE_V1' && CONTRACTS[i].ROUTE_TYPE === 'APPLICATION_ROUTE' && CONTRACTS[i].EXPECTED_SIGNATURE === '<' && CONTRACTS[i].IDENTITY_KIND === 'PLATFORM_NATIVE_ID' && identidadeDoContrato(i, CONTRACTS[i], { url: 'https://www.youtube.com/watch?v=abcdefghijk', nome: 'abcdefghijk' }).DOCUMENT_ID === i + ':YT:abcdefghijk'),"
            "  yt_invalidos: yt.filter(i => { try { conferirAquisicao(i, CONTRACTS[i].ACQUISITION); conferirIdentidade(i, CONTRACTS[i].IDENTITY); return false; } catch (e) { return true; } }),"
            "  onboarded: ONBOARDED_IDS.length,"
            "  onboarded_by: as18.map(i => CONTRACTS[i].ONBOARDED_BY),"
            "  yt_onboarded_by: yt.map(i => CONTRACTS[i] ? CONTRACTS[i].ONBOARDED_BY : '') };"
            "console.log(JSON.stringify(out));" % (json.dumps(list(AS_18)), json.dumps(yt)))
        r = subprocess.run(["node", "--input-type=module", "-e", prog], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(0, r.returncode, r.stderr)
        out = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual([], out["faltam"])
        self.assertEqual([], out["yt_fora"])
        self.assertEqual(50, len(out["yt_pelo_canal"]))
        self.assertEqual([], out["yt_invalidos"], "as 50 passam conferirAquisicao + conferirIdentidade")
        self.assertEqual(173, out["onboarded"])
        for ob in out["onboarded_by"]:
            self.assertIn("SOURCE-CURATOR", ob, "o contrato expandido tem de dizer de onde veio")
        for ob in out["yt_onboarded_by"]:
            self.assertIn("BIG-COLLECTION-RELEASE", ob)
            self.assertIn("376c0d9b", ob, "a identidade veio do curator; a rota, da lane YouTube")


class AEvidenciaDas18TemManifestoNoCaminhoCanonico(unittest.TestCase):
    """O manifesto (sha256) foi promovido; os bytes ficaram fora do Git, de propósito.

    Os bytes entrariam no frame de revisão T3 (`provas/amostragem_neutra_t3.py`
    conta todo corpo em `data/samples/IT-SOURCE-SAMPLES/*/*`), que é uma
    população congelada com veredito humano. Promovê-los é passo separado.
    O sha256 do manifesto promovido tem de ser o do manifesto do curator —
    dois registos versionados a dizer o mesmo número.
    """

    def setUp(self):
        self.curator = {e["CANDIDATE_ID"]: e
                        for e in _json(os.path.join(RAIZ, "curadoria", "REAL-EXAMPLE-MANIFEST-V1.json"))["FILES"]}

    def test_manifesto_sem_bytes_e_com_o_sha_do_curator(self):
        for sid in AS_18:
            with self.subTest(source_id=sid):
                pasta = os.path.join(SAMPLES, sid)
                self.assertEqual(["MANIFEST.json"], sorted(os.listdir(pasta)),
                                 "apareceram bytes na pasta — isso muda o frame T3 e e passo separado")
                man = _json(os.path.join(pasta, "MANIFEST.json"))
                self.assertEqual(sid, man["SOURCE_ID"])
                self.assertEqual("SHA256_VERIFIED_BYTES_NOT_IN_GIT", man["RAW_EVIDENCE_STATE"])
                self.assertNotIn("OWNER_ID", man, "a curadoria nao mediu chave de dono — nao se inventa")
                f = man["FILES"][0]
                self.assertIsNone(f["RAW_FILE"])
                self.assertFalse(f["BYTES_IN_GIT"])
                self.assertRegex(f["SHA256"], r"^[0-9a-f]{64}$")
                e = self.curator[man["PROVENIENCIA"]["CANDIDATE_ID"]]
                self.assertEqual(e["SHA256"], f["SHA256"], "o sha promovido nao e o do curator")
                self.assertEqual(e["BYTES"], f["BYTES"])
                self.assertEqual(sid + ":URL:", man["CANARIO"]["DOCUMENT_ID"][:len(sid) + 5])
                self.assertEqual("ALLOWED", man["ROBOTS_GATE"]["RESULT"])


class ACuradoriaERegistoNaoFerramenta(unittest.TestCase):
    """`curadoria/` traz o registo da missão (JSON, MD); as ferramentas ficaram na branch.

    Medido na primeira bateria: `curadoria/gate_de_rota.py` era um segundo
    leitor de `robots.txt`, e `OPortaoDeTransporteTemUmDonoSo` só admite
    `coleta/scrap_http.py`. As ferramentas vivem em
    `claude/bot-de-fontes-v2-plano @ 376c0d9b`.
    """

    def test_nenhum_ficheiro_de_codigo_em_curadoria(self):
        pasta = os.path.join(RAIZ, "curadoria")
        codigo = sorted(n for n in os.listdir(pasta) if n.endswith((".py", ".mjs", ".js", ".sh")))
        self.assertEqual([], codigo)

    def test_o_registo_essencial_esta_la(self):
        for nome in ("italy_contracts_curator.json", "READY-FOR-COLLECTION-V1.json",
                     "REAL-EXAMPLE-MANIFEST-V1.json", "CANARY-LOTE-HTML-ARTIGO.json",
                     "CANARY-LOTE-YOUTUBE-FEED.json", "SOURCE-ID-ALLOCATION-V1.json",
                     "HANDOFF-INTEGRACAO-04.md"):
            self.assertTrue(os.path.exists(os.path.join(RAIZ, "curadoria", nome)), nome)


class OAtlasCarregaAs84ComEstadoMedido(unittest.TestCase):

    def setUp(self):
        self.fichas = _fichas_do_bloco_04a()

    def test_84_fichas_cada_uma_com_estado(self):
        self.assertEqual(84, len(self.fichas))
        self.assertEqual([], [sid for sid, f in self.fichas.items() if "ESTADO_04A" not in f])

    def test_a_contagem_por_estado_e_18_50_9_7(self):
        estados = {}
        for f in self.fichas.values():
            e = f["ESTADO_04A"].split(" ")[0]
            estados[e] = estados.get(e, 0) + 1
        self.assertEqual({"READY_FOR_COLLECTION": 18, "CONTRACT_READY_ROUTE_BLOCKED": 50,
                          "CONTRACTED_CANARY_FAILED": 9, "SEM_CONTRATO": 7}, estados)
        for sid in AS_18:
            self.assertTrue(self.fichas[sid]["ESTADO_04A"].startswith("READY_FOR_COLLECTION"), sid)
            self.assertIn("data/samples/IT-SOURCE-SAMPLES/%s/" % sid, self.fichas[sid]["EVIDENCE"])

    def test_as_50_dizem_a_razao_do_bloqueio(self):
        for sid, f in self.fichas.items():
            if f["ESTADO_04A"].startswith("CONTRACT_READY_ROUTE_BLOCKED"):
                self.assertIn("ROBOTS_DISALLOWED_ROUTE", f["ESTADO_04A"], sid)
                self.assertIn("PLATFORM_NATIVE_ID", f, "a caracterizacao do canal foi apagada")

    def test_nenhum_source_id_do_bloco_se_repete_no_resto_do_atlas(self):
        t = _texto(ATLAS)
        antes = t[:t.index("## ONDA SOURCE CURATOR")]
        repetidos = [sid for sid in self.fichas if re.search(r"^SOURCE_ID:\s+%s\b" % re.escape(sid), antes, re.M)]
        self.assertEqual([], repetidos)


if __name__ == "__main__":
    unittest.main()
