#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C6-REPETIDO — o SQL novo do C6 contra o ESQUEMA REAL, num Postgres DESCARTÁVEL.

Nunca a Sala. Sobe um Postgres novo numa pasta temporária, aplica as migrations
pela cadeia canónica (`motor/cadeia_canonica.sh migrations`), pousa pela porta
da Sala (`espera.pousar`, a DEDUP-DOC de verdade) e corre `micro_coleta.relatorio`
com a consulta real (`MC.sql`, psql, só SELECT, read-only).

    python3 provas/c6_repetido/prova_sql_c6.py --pg-bin /usr/lib/postgresql/16/bin --saida out.json   (--saida - : so no ecra)

Casos: o real reconstruído (58/1243, mesmo document_key) = PASS; mesmo documento
noutro universo = FAIL; bruto sem identidade provada = FAIL; SIM que não pousou = FAIL.
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for g in (str(RAIZ), str(RAIZ / "admissao")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas                          # noqa: E402,F401
import admissao                          # noqa: E402
import sala_de_espera as espera          # noqa: E402


def carregar(nome, caminho):
    s = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


E = carregar("ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
MC = carregar("micro_coleta", RAIZ / "scripts" / "micro_coleta" / "micro_coleta.py")

CHAVE = "IT-T5-025:URL:it/news/progetto-innoflorenerg"
R20, R24, R28 = "IT-T5-025-2026-09-20-A", "IT-T5-025-2026-09-24-B", "IT-T5-025-2026-09-28-C"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pg-bin", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    E.PG_BIN = Path(a.pg_bin)
    pasta = Path(tempfile.mkdtemp(prefix="c6-repetido-"))
    base = E.Base(pasta / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
    fora = {"PG_BIN": a.pg_bin, "CASOS": {}}
    amb = dict(os.environ)
    try:
        sub = base.subir(RAIZ, env)
        fora["MIGRATIONS"] = {"CODIGO": sub["CODIGO"], "PASS": sub["MIGRATIONS_PASS"]}
        if sub["CODIGO"] != 0:
            raise SystemExit("migrations falharam: %s" % sub["ERRO"])
        os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": base.url,
                           "SINTONIA_PSQL_EXE": base.exe("psql")})

        def sql(c):
            r = subprocess.run([base.exe("psql"), "-X", "-At", "-v", "ON_ERROR_STOP=1", "-c", c,
                                base.url], capture_output=True, text=True)
            if r.returncode:
                raise SystemExit("psql: %s\n%s" % (c[:200], r.stderr))
            return r.stdout.strip()

        n = [0]

        def bruto(run, chave, estado="FORWARD_IDENTIFIED"):
            n[0] += 1
            k = "null" if chave is None else "'%s'" % chave
            b = "null" if chave is None else "'SOURCE_DOCUMENT_ID'"
            return int(sql(
                "insert into raw_asset (run_id, storage_path, media_type, bytes, sha256, captured_at, "
                "preserved, not_preserved_reason, source_id, document_key, document_key_basis, "
                "identity_state) values ('%s', 'prova/%d', 'text/html', 1, '%s', now(), false, "
                "'prova sem copia', 'IT-T5-025', %s, %s, '%s') returning id"
                % (run, n[0], ("%x" % n[0] * 64)[:64], k, b, estado)).splitlines()[0])

        def derivado(raw):
            n[0] += 1
            return "derived:" + sql(
                "insert into derived_artifact (raw_asset_id, parent_sha256, kind, producer, "
                "producer_version, parameters_hash, sha256, bytes, media_type, storage_path, "
                "derived_at) values (%d, '%s', 'TEXT_EXTRACTION', 'texto-de-html', '1', '%s', '%s', 1, "
                "'text/plain', 'der/%d', now()) returning id"
                % (raw, sql("select sha256 from raw_asset where id = %d" % raw), "e" * 64,
                   ("%x" % (n[0] + 7) * 64)[:64], n[0])).splitlines()[0]

        def unidade(item_id, raw_id, universo="T5"):
            item = {"id": item_id, "texto": "Ensaio de campo publicado com DOI " + item_id,
                    "source_id": "IT-T5-025", "fact_time": "2026-05-02"}
            u = admissao.pronto_para_inteligencia(item, admissao.decidir(item, "T5", corrida="R"))
            return dict(u, ITEM_ID=item_id, UNIVERSO=universo, RAW_OBSERVATION_ID=raw_id,
                        SOURCE_ID="IT-T5-025")

        def c6(run, decisoes):
            livro = pasta / ("livro-%s.json" % run)
            livro.write_text(json.dumps({"DECISOES": decisoes}), encoding="utf-8")
            r = MC.relatorio([run], consulta=MC.sql, livro=livro, armazem=pasta)
            c = r["CRITERIOS"]["C6_ZERO_BYPASS"]
            return {"PASSA": c["PASSA"], "SIM_FORA_DA_SALA": c["SIM_FORA_DA_SALA"],
                    "FUNDIDO_POR_DOCUMENTO": c["FUNDIDO_POR_DOCUMENTO"],
                    "FUNDIDO_POR_ITEM": c["FUNDIDO_POR_ITEM"],
                    "SIM_FORA_DA_SALA_PORQUE": c["SIM_FORA_DA_SALA_PORQUE"],
                    "JA_NA_SALA": r["CONTAGENS"]["SALA_ITENS_JA_NA_SALA_POR_OUTRA_CORRIDA"],
                    "PARCELAS": r["CONTAGENS"]["SALA_JA_NA_SALA_PARCELAS"]}

        corridas = [R20, R24, R28] + ["IT-T5-025-2026-09-28-D%d" % i for i in range(1, 5)]
        sql("insert into collection_run (run_id, platform, started_at, rule_version) values "
            + ", ".join("('%s', 'prova', now(), 'prova')" % c for c in corridas))

        # O caso real: raw 166 (20/09) -> derived:58 na Sala; raw 299 (24/09) o mesmo
        # documento; raw 2375 (28/09) -> derived:1243, SIM, a Sala funde pelo DOCUMENTO.
        r166, r299, r2375 = bruto(R20, CHAVE), bruto(R24, CHAVE), bruto(R28, CHAVE)
        d58, d1243 = derivado(r166), derivado(r2375)
        derivado(r299)
        p20 = espera.pousar(R20, [unidade(d58, r166)])
        p28 = espera.pousar(R28, [unidade(d1243, r2375)])
        fora["POUSOS"] = {"R20": {k: p20.get(k) for k in ("ESTADO", "INSERIDAS")},
                          "R28": {k: p28.get(k) for k in ("ESTADO", "INSERIDAS", "JA_NA_SALA_POR_OUTRA_CORRIDA")}}
        fora["IDS"] = {"derived58": d58, "derived1243": d1243, "raw166": r166, "raw2375": r2375}
        fora["CASOS"]["REAL_58_1243"] = c6(R28, [
            {"item": d1243, "universo": "T5", "resultado": "SIM", "corrida": R28}])

        # Mesmo documento, OUTRO universo (T7): nao pousou, nao pode contar como fundido.
        run = corridas[3]
        r = bruto(run, CHAVE)
        d = derivado(r)
        fora["CASOS"]["MESMO_DOC_OUTRO_UNIVERSO"] = c6(run, [
            {"item": d, "universo": "T7", "resultado": "SIM", "corrida": run}])

        # Bruto SEM identidade provada: NAO SEI nunca funde.
        run = corridas[4]
        r = bruto(run, None, "FORWARD_IDENTITY_UNPROVEN")
        d = derivado(r)
        fora["CASOS"]["RAW_NAO_FORWARD_IDENTIFIED"] = c6(run, [
            {"item": d, "universo": "T5", "resultado": "SIM", "corrida": run}])

        # O mais afiado: bruto NAO provado mas com o MESMO document_key do raw 166.
        # Na Sala real o ESQUEMA ja o recusa (026: forward_sem_prova_nao_finge_chave);
        # regista-se a recusa. O caso fica provado no teste com banco falso.
        try:
            bruto(corridas[6], CHAVE, "FORWARD_IDENTITY_UNPROVEN")
            fora["NAO_PROVADO_COM_CHAVE"] = "ACEITE_PELO_ESQUEMA"
        except SystemExit as ex:
            fora["NAO_PROVADO_COM_CHAVE"] = ("RECUSADO_PELO_ESQUEMA forward_sem_prova_nao_finge_chave"
                                             if "forward_sem_prova_nao_finge_chave" in str(ex)
                                             else "ERRO " + str(ex)[-200:])

        # SIM que simplesmente nao pousou (outro documento).
        run = corridas[5]
        r = bruto(run, "IT-T5-025:URL:it/news/outra-noticia")
        d = derivado(r)
        fora["CASOS"]["SIM_NAO_POUSOU"] = c6(run, [
            {"item": d, "universo": "T5", "resultado": "SIM", "corrida": run}])

        esperado = {"REAL_58_1243": True, "MESMO_DOC_OUTRO_UNIVERSO": False,
                    "RAW_NAO_FORWARD_IDENTIFIED": False, "SIM_NAO_POUSOU": False}
        fora["VEREDITO"] = ("PASS" if all(fora["CASOS"][k]["PASSA"] is v for k, v in esperado.items())
                            and p28.get("INSERIDAS") == 0 else "FAIL")
    finally:
        os.environ.clear()
        os.environ.update(amb)
        base.descer()
        shutil.rmtree(pasta, ignore_errors=True)
    if a.saida != "-":
        Path(a.saida).write_text(json.dumps(fora, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(fora, ensure_ascii=False, indent=1))
    return 0 if fora["VEREDITO"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
