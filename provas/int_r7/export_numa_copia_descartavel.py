"""A RODADA 7, ponta a ponta, numa COPIA DESCARTAVEL da Sala — nunca a Sala.

    python3 provas/int_r7/export_numa_copia_descartavel.py <saida.json>

Num Postgres novo, em pasta temporaria (o mesmo `Base` do ensaio da 033):

    1  sobe o banco e corre a cadeia `migrations` (001..033) — o esquema real
    2  semeia a fixture SINTETICA de tests/dados/int-r7: collection_run, raw_asset
       (source_url, document_key) e os READY pelo DONO da Sala (`pousar`), e a
       janela declarada por `rever` (revisao 033) — nenhum INSERT a mao na Sala
    3  corre motor/r7_export_da_copia.sql EXATAMENTE como o RUNBOOK-R7 manda:
       psql, PGOPTIONS=default_transaction_read_only=on, `begin transaction
       read only`, `commit`
    4  prova as travas: a mesma sessao read-only recusa um INSERT
    5  o export -> motor/motor_das_capacidades.py -> (se o commit existir) o
       gerador do pote ce775ff5
    6  o export tem de dar a MESMA resposta das capacidades que a fixture da

Sem os binarios do Postgres (PG_BIN do ensaio, ou SINTONIA_PG_BIN), ou a
correr como root (o postgres recusa), sai com codigo 4 e NAO SEI — nunca PASS.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for p in ("", "admissao", "motor", "leis", "provas/int_r7"):
    sys.path.insert(0, str(RAIZ / p))
import _gavetas                            # noqa: E402,F401
import sala_de_espera as espera            # noqa: E402
import motor_das_capacidades as M          # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
if os.environ.get("SINTONIA_PG_BIN"):
    E.PG_BIN = Path(os.environ["SINTONIA_PG_BIN"])

FIXTURE = RAIZ / "tests" / "dados" / "int-r7" / "SINTETICO-R7-SALA-EXPORT.json"
SQL = RAIZ / "motor" / "r7_export_da_copia.sql"
HOJE = date(2026, 9, 27)
PGOPTIONS = "-c default_transaction_read_only=on -c standard_conforming_strings=on"


def _lit(v):
    return espera._lit(v)


def correr(saida: Path) -> dict:
    initdb = E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")
    if not initdb.exists() or (hasattr(os, "geteuid") and os.geteuid() == 0):
        return {"ESTADO": "NAO SEI", "PORQUE": "sem Postgres em %s, ou a correr como root" % E.PG_BIN}
    pasta = Path(tempfile.mkdtemp(prefix="r7-copia-"))
    base = E.Base(pasta / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
    for v in ("SINTONIA_COLLECTION_DSN", "SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL"):
        env.pop(v, None)
    amb = dict(os.environ)
    out = {"PASSOS": {}}
    try:
        r = base.subir(RAIZ, env)
        out["PASSOS"]["1_MIGRATIONS"] = {"CODIGO": r["CODIGO"], "PASS": r["MIGRATIONS_PASS"]}
        if r["CODIGO"] != 0:
            out["ESTADO"] = "FAIL"
            out["ERRO"] = r["ERRO"]
            return out
        os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": base.url,
                           "SINTONIA_PSQL_EXE": base.exe("psql")})

        def sql(c, opcoes=None):
            e = dict(env, PGOPTIONS=opcoes or "-c standard_conforming_strings=on")
            return subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                                   "-c", c, base.url], capture_output=True, text=True,
                                  encoding="utf-8", env=e)

        # 2 · semear (SINTETICO) pelos donos
        fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
        entrada = M.entrada_do_export(fx)
        runs = sorted({l["run_id"] for l in fx["LINHAS"]})
        r = sql("insert into collection_run (run_id, platform, started_at, rule_version) values "
                + ", ".join("(%s, 'SINTETICO', now(), 'SINTETICO')" % _lit(x) for x in runs))
        assert r.returncode == 0, r.stderr
        vistos = set()
        for l in fx["LINHAS"]:
            rid = l["raw_observation_id"]
            if rid in vistos:
                continue
            vistos.add(rid)
            r = sql("insert into raw_asset (id, run_id, storage_path, media_type, bytes, sha256, "
                    "captured_at, source_url, source_id, document_key, document_key_basis, "
                    "identity_state, preserved, not_preserved_reason) values "
                    "(%d, %s, %s, 'text/html', 1, %s, %s, %s, %s, %s, %s, %s, false, "
                    "'SINTETICO: fixture INT-R7-CAPS, sem bytes')"
                    % (rid, _lit(l["run_id"]), _lit("SINTETICO/%d" % rid), _lit("%064x" % rid),
                       _lit(l["captured_at"]), _lit(l["raw_source_url"]), _lit(l["source_id"]),
                       _lit(l["raw_document_key"]), _lit(l["raw_document_key_basis"]),
                       _lit("FORWARD_IDENTIFIED" if l["raw_document_key"] else "FORWARD_IDENTITY_UNPROVEN")))
            assert r.returncode == 0, r.stderr
        por_run = {}
        for reg, l in zip(entrada["ITENS"], fx["LINHAS"]):
            u = dict(reg["READY"])
            por_run.setdefault(l["run_id"], []).append((l["ordem"], u, l["janela_declarada"]))
        for run, us in por_run.items():
            us.sort(key=lambda x: x[0])
            recibo = espera.pousar(run, [u for _o, u, _j in us])
            out["PASSOS"].setdefault("2_POUSAR", {})[run] = {k: recibo[k] for k in recibo
                                                            if k in ("ESTADO", "INSERIDAS")}
            atual = espera.ler_atual(run)["ITENS"]
            for (_o, u, jd), linha in zip(us, atual):
                assert linha["ITEM_ID"] == u["ITEM_ID"]
                if isinstance(jd, dict):
                    espera.rever(run, linha["ORDEM"], [{"CAMPO": "janela_declarada",
                                                        "VALOR": json.dumps(jd, ensure_ascii=False, sort_keys=True),
                                                        "BASE": "SINTETICO · fixture INT-R7-CAPS"}],
                                 extrator="SINTETICO-R7", versao="1", motivo="fixture SINTETICA INT-R7-CAPS")

        # 3 · o export, como o RUNBOOK manda
        destino = pasta / "sala-r7.json"
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                            "-c", "begin transaction read only", "-f", str(SQL), "-c", "commit",
                            "-o", str(destino), base.url],
                           capture_output=True, text=True, encoding="utf-8",
                           env=dict(env, PGOPTIONS=PGOPTIONS, PGCLIENTENCODING="UTF8"))
        out["PASSOS"]["3_EXPORT"] = {"CODIGO": r.returncode, "ERRO": r.stderr[-400:]}
        exp = json.loads(destino.read_text(encoding="utf-8"))
        out["PASSOS"]["3_EXPORT"].update({"LINHAS": len(exp["LINHAS"]), "READ_ONLY": exp["READ_ONLY"]})

        # 4 · as travas: a mesma forma de sessao recusa escrever
        r = sql("insert into collection_run (run_id, platform, started_at, rule_version) "
                "values ('ESCRITA-PROIBIDA', 'x', now(), 'x')", PGOPTIONS)
        out["PASSOS"]["4_ESCRITA_RECUSADA"] = {"CODIGO": r.returncode,
                                               "ERRO": r.stderr.strip().splitlines()[-1] if r.stderr else ""}

        # 5 · o motor sobre o export da copia
        exp["SINTETICO"] = True   # a copia foi semeada so com a fixture SINTETICA
        saida_motor = M.rodar(M.entrada_do_export(exp), HOJE, "SINT-HEAD")
        s_fx = M.rodar(entrada, HOJE, "SINT-HEAD")

        def resposta(s):
            j = s["CAP_WIN"]["CROP_WINDOWS"]
            return {"JANELAS": [(x["CROP_ID"], x["ISSUE_ID"], x["REGION_ID"], x["WINDOW_OPEN_NOW"],
                                 x["RESULT"]) for x in j],
                    "NOT_POSSIBLE": sorted(x["ITEM_ID"] for x in s["CAP_WIN"]["NOT_POSSIBLE"]),
                    "ESTUDOS": sorted((e["ITEM_ID"], e["ESPECIE"], e["FORCA"]["NIVEL"],
                                       e["APLICABILIDADE"]["ESTADO"]) for e in s["CAP_SCI"]["ESTUDOS"]),
                    "RELACOES": sorted(r["TIPO"] for r in s["D112"]["RELACOES"]),
                    "OBJETOS": {k: len(v) for k, v in s["ITENS_POR_FERRAMENTA"].items()}}
        out["PASSOS"]["5_MOTOR"] = resposta(saida_motor)
        out["PASSOS"]["6_IGUAL_A_FIXTURE"] = resposta(saida_motor) == resposta(s_fx)
        caminho = pasta / "motor-r7.json"
        caminho.write_text(json.dumps(saida_motor, ensure_ascii=False), encoding="utf-8")
        import aceite_pelo_gerador as G
        if G.blob_existe():
            pote = G.correr_gerador(str(caminho))
            out["PASSOS"]["5_POTE_V2"] = {c: len(e["OBJETOS"]) for c, e in pote["COMPARTIMENTOS"].items()
                                          if e["OBJETOS"]}
            out["PASSOS"]["5_POTE_V2_RECUSADOS"] = [(x["COMPARTIMENTO"], x["MOTIVO"], x["DETALHE"])
                                                    for x in pote["RECUSADOS"]]
        else:
            out["PASSOS"]["5_POTE_V2"] = "NAO SEI: commit ce775ff5 ausente neste clone"
        ok = (out["PASSOS"]["3_EXPORT"]["CODIGO"] == 0 and exp["READ_ONLY"] == "on"
              and out["PASSOS"]["4_ESCRITA_RECUSADA"]["CODIGO"] != 0
              and "read-only" in out["PASSOS"]["4_ESCRITA_RECUSADA"]["ERRO"]
              and out["PASSOS"]["6_IGUAL_A_FIXTURE"])
        out["ESTADO"] = "PASS" if ok else "FAIL"
        return out
    finally:
        os.environ.clear()
        os.environ.update(amb)
        base.descer()
        shutil.rmtree(pasta, ignore_errors=True)
        Path(saida).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    res = correr(Path(sys.argv[1]))
    print(json.dumps(res, ensure_ascii=False, indent=1))
    sys.exit(0 if res.get("ESTADO") == "PASS" else 4 if res.get("ESTADO") == "NAO SEI" else 1)
