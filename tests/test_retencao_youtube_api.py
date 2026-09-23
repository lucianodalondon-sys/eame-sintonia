#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D20 · A RETENÇÃO DE 30 DIAS — o ensaio 29/30/31 num PostgreSQL que nasce e morre aqui.

    O BYTE SAI. A LINHA FICA. A LÁPIDE DIZ O QUE SAIU.

O banco é um cluster portátil (`provas/a_porta_cli_liga_o_banco.Bancada`) com as
migrações pela cadeia canónica, incluindo a 033. O armazém é uma pasta temporária.
Nenhum serviço vivo é tocado. Sem Postgres portátil nesta máquina, a parte com banco
salta — e diz porquê; a parte sem banco corre sempre.
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
for p in ("guarda", "provas"):
    sys.path.insert(0, os.path.join(RAIZ, p))
import retencao_youtube_api as RT  # noqa: E402

AGORA = datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc)


def _obs(rota, video, extra=None):
    """O envelope como o Scrap o deixa na porta: a rota vive DENTRO do byte."""
    o = {"OBSERVACAO": {"ROUTE": rota, "DISCOVERY_ROUTES": [rota], "NATIVE_ID": video,
                        "TEXT": "Titolo del video %s" % video}, "SOURCE_ID": "IT-T2-025"}
    o.update(extra or {})
    return json.dumps(o, sort_keys=True).encode("utf-8")


class ARotaLeSeNoByte(unittest.TestCase):
    def test_so_api_e_api(self):
        self.assertEqual(RT.classificar(_obs("youtube-data-api-v3:videos.list", "a"))[0], RT.API)

    def test_audio_local_nao_e_api(self):
        self.assertEqual(RT.classificar(_obs("yt-dlp:public_audio", "a"))[0], RT.NAO_E_DA_API)

    def test_rota_mista_e_nao_sei(self):
        b = _obs("youtube-data-api-v3:videos.list", "a",
                 {"ROUTE": "yt-dlp:public_audio"})
        self.assertEqual(RT.classificar(b)[0], RT.NAO_SEI)

    def test_sem_rota_ou_nao_json_e_nao_sei(self):
        self.assertEqual(RT.classificar(b"{}")[0], RT.NAO_SEI)
        self.assertEqual(RT.classificar(b"\x89PNG")[0], RT.NAO_SEI)

    def test_aplicar_em_banco_que_nao_e_descartavel_e_recusado(self):
        antes = RT.varrer
        RT.varrer = lambda *a, **k: []
        try:
            r = RT.main(["--url=postgresql://u@db.exemplo.supabase.co:5432/postgres", "--aplicar"])
        finally:
            RT.varrer = antes
        self.assertEqual(r, 4)


def _bancada():
    try:
        import a_porta_cli_liga_o_banco as P
    except Exception:  # noqa: BLE001
        return None, None
    if not P.Bancada.binarios():
        return None, None
    return P, P.Bancada()


P, BANCADA = _bancada()


@unittest.skipUnless(BANCADA, "sem Postgres portatil (SINTONIA_PG_PORTATIL / initdb) — nao se finge banco")
class OEnsaioDos29_30_31Dias(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A ronda de mutacao sobe UM banco e passa-o aqui (ja migrado): um cluster
        # por mutante custaria minutos por ataque. So se aceita se for descartavel.
        cls.seq = 0
        reuso = os.environ.get("SOC3_BANCO_JA_MIGRADO")
        if reuso:
            import banco_descartavel as BD
            cls.url = BD.exigir_descartavel(reuso)
            cls.n_migracoes = int(os.environ.get("SOC3_MIGRACOES", "0"))
            cls.proprio = False
            return
        cls.proprio = True
        cls.url = BANCADA.subir()
        cod, n, saida, erro = P._migrations(cls.url, dict(os.environ))
        if cod != 0:
            BANCADA.destruir()
            raise RuntimeError("migracoes falharam: %s %s" % (saida[-400:], erro[-300:]))
        cls.n_migracoes = n
        cls.seq = 0

    @classmethod
    def tearDownClass(cls):
        if cls.proprio:
            cls.fim = BANCADA.destruir()

    def setUp(self):
        self.raiz = tempfile.mkdtemp(prefix="retencao-armazem-")
        self.addCleanup(shutil.rmtree, self.raiz, True)
        type(self).seq += 1
        self.run = "SOC3-ENSAIO-%03d-%s" % (self.seq, os.urandom(4).hex())
        RT._psql(self.url, "insert into public.collection_run (run_id, platform, started_at, rule_version) "
                           "values ('%s', 'YOUTUBE', now(), 'soc3-ensaio');" % self.run)

    # ── fixtures ───────────────────────────────────────────────────────────
    def _guardar(self, dados, media, dias, doc, *, sem_byte=False, caminho=None):
        sha = hashlib.sha256(dados).hexdigest()
        caminho = caminho or "XX/youtube/OBSERVATION/%s-%s.%s" % (self.run, doc, "wav" if "audio" in media else "json")
        if not sem_byte:
            alvo = os.path.join(self.raiz, *caminho.split("/"))
            os.makedirs(os.path.dirname(alvo), exist_ok=True)
            with open(alvo, "wb") as fh:
                fh.write(dados)
        quando = RT._instante(AGORA - timedelta(days=dias))
        so = RT._psql(self.url, "insert into public.storage_object (storage_path, media_type, bytes, sha256) "
                                "values (%s, %s, %d, %s) on conflict (storage_path) do update set bytes = excluded.bytes "
                                "returning id;" % (RT._lit(caminho), RT._lit(media), len(dados), RT._lit(sha)))[0][0]
        rid = RT._psql(self.url, (
            "insert into public.raw_asset (run_id, storage_path, media_type, bytes, sha256, captured_at, "
            "storage_object_id, identity_state, source_id, document_key, document_key_basis) values "
            "(%s, %s, %s, %d, %s, %s::timestamptz, %s, 'FORWARD_IDENTIFIED', 'IT-T2-025', %s, "
            "'SOURCE_DOCUMENT_ID') returning id;")
            % (RT._lit(self.run), RT._lit(caminho), RT._lit(media), len(dados), RT._lit(sha),
               RT._lit(quando), so, RT._lit("IT-T2-025:YT:" + doc)))[0][0]
        return int(rid), caminho

    def _estado(self, rid):
        l = RT._psql(self.url, "select preserved, coalesce(not_preserved_reason,''), sha256 "
                               "from public.raw_asset where id = %d;" % rid)[0]
        return l[0] == "t", l[1], l[2].strip()

    def _existe(self, caminho):
        return os.path.isfile(os.path.join(self.raiz, *caminho.split("/")))

    def _tres(self):
        api = "youtube-data-api-v3:videos.list"
        return {d: self._guardar(_obs(api, "%s%d" % (self.run, d)), "application/json", d, "v%d" % d)
                for d in (29, 30, 31)}

    # ── o ensaio ───────────────────────────────────────────────────────────
    def test_a_migracao_033_foi_aplicada(self):
        self.assertGreaterEqual(self.n_migracoes, 32)
        self.assertEqual(RT._psql(self.url, "select to_regclass('public.lapide_de_retencao') is not null;")[0][0], "t")

    def test_so_o_de_31_dias_vira_lapide(self):
        ids = self._tres()
        vs = [v for v in RT.varrer(self.url, self.raiz, AGORA) if v["ID"] in {i for i, _ in ids.values()}]
        self.assertEqual([(v["ID"], v["VEREDICTO"]) for v in vs], [(ids[31][0], RT.API)])
        r = RT.aplicar(self.url, vs, self.raiz, AGORA)
        self.assertEqual([x["RAW_ASSET_ID"] for x in r["LAPIDES"]], [ids[31][0]])
        preservado, motivo, sha = self._estado(ids[31][0])
        self.assertFalse(preservado)
        self.assertIn(RT.REGRA, motivo)
        self.assertFalse(self._existe(ids[31][1]), "o byte do de 31 dias saiu")
        for d in (29, 30):
            self.assertTrue(self._estado(ids[d][0])[0], "%d dias ainda esta no prazo" % d)
            self.assertTrue(self._existe(ids[d][1]))
        lap = RT._psql(self.url, "select raw_asset_id, sha256, motivo, rota from public.lapide_de_retencao "
                                 "where raw_asset_id = %d;" % ids[31][0])
        self.assertEqual(lap, [[str(ids[31][0]), sha, "PRAZO_VENCIDO", "youtube-data-api-v3:videos.list"]])

    def test_audio_local_e_rota_que_nao_e_da_api_ficam(self):
        wav = self._guardar(b"RIFF....WAVEfmt ", "audio/wav", 31, "audio")
        json_dlp = self._guardar(_obs("yt-dlp:public_audio", "x"), "application/json", 31, "dlp")
        sem_byte = self._guardar(_obs("youtube-data-api-v3:videos.list", "y"), "application/json", 31,
                                 "sem", sem_byte=True)
        vs = {v["ID"]: v["VEREDICTO"] for v in RT.varrer(self.url, self.raiz, AGORA)}
        self.assertNotIn(wav[0], vs, "audio/wav nem e candidato")
        self.assertEqual(vs[json_dlp[0]], RT.NAO_E_DA_API)
        self.assertEqual(vs[sem_byte[0]], RT.NAO_SEI)
        RT.aplicar(self.url, RT.varrer(self.url, self.raiz, AGORA), self.raiz, AGORA)
        for rid, cam in (wav, json_dlp):
            self.assertTrue(self._estado(rid)[0])
            self.assertTrue(self._existe(cam))
        self.assertTrue(self._estado(sem_byte[0])[0], "nao saber nao autoriza apagar")
        self.assertEqual(RT.checar(self.url, self.raiz, AGORA)["RETENCAO_30D"], "NAO_SEI")
        RT._psql(self.url, "update public.raw_asset set preserved = false, not_preserved_reason = 'limpeza do ensaio' "
                           "where id = %d;" % sem_byte[0])

    def test_o_texto_na_sala_e_nas_tabelas_sociais_sai_com_o_byte(self):
        rid, cam = self._guardar(_obs("youtube-data-api-v3:videos.list", "s"), "application/json", 31, "sala")
        RT._psql(self.url, (
            "insert into public.sala_de_espera (run_id, ordem, item_id, raw_observation_id, universo, texto, "
            "source_id, source_location, fact_location, fact_time, captured_at, admitido_por, corrida_sha256) "
            "values (%s, 0, 'obs:%d', %d, 'T2', 'Titolo segreto', 'IT-T2-025', 'NAO SEI', 'NAO SEI', 'NAO SEI', "
            "'2026-08-23', 'ensaio', %s);") % (RT._lit(self.run), rid, rid, RT._lit("a" * 64)))
        dsha = hashlib.sha256(b"derivado").hexdigest()
        dcam = "XX/derivados/%s.txt" % self.run
        os.makedirs(os.path.join(self.raiz, "XX", "derivados"), exist_ok=True)
        with open(os.path.join(self.raiz, "XX", "derivados", "%s.txt" % self.run), "wb") as fh:
            fh.write(b"derivado")
        psha = self._estado(rid)[2]
        RT._psql(self.url, (
            "insert into public.derived_artifact (raw_asset_id, parent_sha256, kind, producer, producer_version, "
            "parameters_hash, sha256, bytes, media_type, storage_path, derived_at) values "
            "(%d, %s, 'TEXT_EXTRACTION', 'ensaio', '1', %s, %s, 8, 'text/plain', %s, now());")
            % (rid, RT._lit(psha), RT._lit("b" * 64), RT._lit(dsha), RT._lit(dcam)))
        vs = [v for v in RT.varrer(self.url, self.raiz, AGORA) if v["ID"] == rid]
        RT.aplicar(self.url, vs, self.raiz, AGORA)
        texto = RT._psql(self.url, "select texto from public.sala_de_espera where raw_observation_id = %d;" % rid)[0][0]
        self.assertNotIn("segreto", texto)
        self.assertIn("30 DIAS", texto)
        self.assertFalse(os.path.isfile(os.path.join(self.raiz, "XX", "derivados", "%s.txt" % self.run)))
        lap = RT._psql(self.url, "select count(*) from public.lapide_de_retencao where raw_asset_id = %d;" % rid)
        self.assertEqual(lap[0][0], "2", "uma lapide pelo raw e outra pelo derivado")

    def test_titulo_descricao_e_comentario_sociais_saem_com_o_byte(self):
        rid, cam = self._guardar(_obs("youtube-data-api-v3:videos.list", "soc"), "application/json", 31, "soc")
        org = RT._psql(self.url, "insert into public.organizacao (nome_canonico) values ('Org %s') "
                                 "returning id;" % self.run)[0][0]
        origem = RT._psql(self.url, "insert into public.origem (organizacao_id, rotulo) values (%s, 'ensaio') "
                                    "returning id;" % org)[0][0]
        canal = RT._psql(self.url, "insert into public.canal (origem_id, plataforma, channel_id) values "
                                   "(%s, 'youtube', %s) returning id;" % (origem, RT._lit("UC" + self.run)))[0][0]
        cid = RT._psql(self.url, (
            "insert into public.conteudo (canal_id, run_id, raw_asset_id, tipo, content_id, titulo, descricao, "
            "hash_conteudo, rule_version) values (%s, %s, %d, 'video', 'vid', 'Titolo segreto', "
            "'Descrizione segreta', %s, 'soc3-ensaio') "
            "returning id;") % (canal, RT._lit(self.run), rid, RT._lit("d" * 64)))[0][0]
        RT._psql(self.url, "insert into public.comentario (conteudo_id, run_id, externo_id, texto, hash_conteudo) values "
                           "(%s, %s, 'c1', 'Commento segreto', %s);" % (cid, RT._lit(self.run), RT._lit("e" * 64)))
        RT.aplicar(self.url, [v for v in RT.varrer(self.url, self.raiz, AGORA) if v["ID"] == rid], self.raiz, AGORA)
        t, d = RT._psql(self.url, "select coalesce(titulo,''), coalesce(descricao,'') from public.conteudo "
                                  "where id = %s;" % cid)[0]
        self.assertEqual((t, d), ("", ""))
        c = RT._psql(self.url, "select texto from public.comentario where conteudo_id = %s;" % cid)[0][0]
        self.assertNotIn("segreto", c)

    def test_byte_trocado_e_nao_sei(self):
        rid, cam = self._guardar(_obs("youtube-data-api-v3:videos.list", "t"), "application/json", 31, "troca")
        with open(os.path.join(self.raiz, *cam.split("/")), "ab") as fh:
            fh.write(b" ")
        v = [x for x in RT.varrer(self.url, self.raiz, AGORA) if x["ID"] == rid][0]
        self.assertEqual(v["VEREDICTO"], RT.NAO_SEI)
        RT.aplicar(self.url, [v], self.raiz, AGORA)
        self.assertTrue(self._estado(rid)[0], "sha diferente: nao se apaga o que nao se provou ser aquilo")
        RT._psql(self.url, "update public.raw_asset set preserved = false, not_preserved_reason = 'limpeza do ensaio' "
                           "where id = %d;" % rid)

    def test_renovar_repoe_e_a_segunda_passagem_faz_zero(self):
        velho = self._guardar(_obs("youtube-data-api-v3:videos.list", "r1"), "application/json", 31, "ren")
        novo = self._guardar(_obs("youtube-data-api-v3:videos.list", "r2"), "application/json", 0, "ren",
                             caminho="XX/youtube/OBSERVATION/%s-ren-novo.json" % self.run)
        vs = [v for v in RT.varrer(self.url, self.raiz, AGORA) if v["ID"] == velho[0]]
        self.assertEqual(vs[0]["MOTIVO"], "RENOVADA")
        RT.aplicar(self.url, vs, self.raiz, AGORA)
        self.assertFalse(self._estado(velho[0])[0])
        self.assertTrue(self._estado(novo[0])[0], "a copia renovada fica")
        self.assertTrue(self._existe(novo[1]))
        segunda = RT.aplicar(self.url, RT.varrer(self.url, self.raiz, AGORA), self.raiz, AGORA)
        self.assertEqual(segunda["LAPIDES"], [])

    def test_a_mesma_copia_de_uma_observacao_no_prazo_nao_se_apaga(self):
        dados = _obs("youtube-data-api-v3:videos.list", "partilhado")
        velho = self._guardar(dados, "application/json", 31, "par")
        novo = self._guardar(dados, "application/json", 1, "par2", caminho=velho[1])
        v = [x for x in RT.varrer(self.url, self.raiz, AGORA) if x["ID"] == velho[0]][0]
        self.assertEqual(v["VEREDICTO"], RT.EM_USO_NO_PRAZO)
        RT.aplicar(self.url, [v], self.raiz, AGORA)
        self.assertTrue(self._existe(velho[1]))
        self.assertTrue(self._estado(novo[0])[0])

    def test_a_checagem_diaria_falha_antes_e_passa_depois(self):
        self._guardar(_obs("youtube-data-api-v3:videos.list", "c"), "application/json", 31, "chk")
        self.assertEqual(RT.checar(self.url, self.raiz, AGORA)["RETENCAO_30D"], "FAIL")
        RT.aplicar(self.url, RT.varrer(self.url, self.raiz, AGORA), self.raiz, AGORA)
        c = RT.checar(self.url, self.raiz, AGORA)
        self.assertEqual(c["RETENCAO_30D"], "PASS", c)

    def test_lapide_escrita_com_byte_vivo_e_falha_visivel(self):
        rid, cam = self._guardar(_obs("youtube-data-api-v3:videos.list", "v"), "application/json", 31, "viva")

        def recusa(_p):
            raise OSError("disco recusou")
        vs = [v for v in RT.varrer(self.url, self.raiz, AGORA) if v["ID"] == rid]
        r = RT.aplicar(self.url, vs, self.raiz, AGORA, apagar=recusa)
        self.assertEqual(len(r["FALHAS_AO_APAGAR"]), 1)
        c = RT.checar(self.url, self.raiz, AGORA)
        self.assertEqual(c["RETENCAO_30D"], "FAIL")
        self.assertIn(cam, c["LAPIDE_COM_BYTE_VIVO"])
        os.remove(os.path.join(self.raiz, *cam.split("/")))

    def test_a_lapide_so_aceita_rota_da_api(self):
        rid, cam = self._guardar(_obs("youtube-data-api-v3:videos.list", "k"), "application/json", 1, "k")
        with self.assertRaises(RuntimeError):
            RT._psql(self.url, "insert into public.lapide_de_retencao (raw_asset_id, storage_path, sha256, regra, "
                               "motivo, rota, captured_at, prova) values (%d, 'x', %s, %s, 'PRAZO_VENCIDO', "
                               "'yt-dlp:public_audio', now(), 'p');" % (rid, RT._lit("c" * 64), RT._lit(RT.REGRA)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
