#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENSAIO T6 NUMA COPIA DA SALA — quantos trabalhos T6 entrariam, medido no banco, sem tocar a Sala.

    py provas/ensaio_t6_na_copia_da_sala.py --saida=<pasta> [--universo=T5]

PESADO: so com a LOCK-PESADO na mao e >= 5 GB livres (quem chama confere).

1. COPIA DA SALA REAL, so leitura: o mesmo pg_dump do backup_sala.cmd
   (`scripts/micro_coleta/provar_backup_da_sala.comando_de_backup`), com a fotografia da
   Sala real antes e depois (se mudou durante o dump, o ensaio diz-lo).
2. Um Postgres DESCARTAVEL (`sala_italia` numa porta livre, `ensaio_offline.Base`), com o
   dump reposto. A Sala real nunca e o alvo: nenhuma variavel aponta para ela.
3. O botao canonico (`provas/o_pedido_t6_atravessa.py`) DUAS vezes sobre a copia, com a
   Sala em POSTGRES: a 1.a mede quantos entram; a 2.a mede que nao entram outra vez.
4. Conta por SQL, antes e depois, na copia: sala_de_espera (por universo e por fonte),
   raw_asset, collection_run. Desce o banco e apaga o cluster.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
import ensaio_offline as E            # noqa: E402
import micro_coleta as MC             # noqa: E402
import provar_backup_da_sala as PB    # noqa: E402

CONTAR = {
    "SALA": "select count(*) from public.sala_de_espera",
    "SALA_T5": "select count(*) from public.sala_de_espera where universo = 'T5'",
    "SALA_T6": "select count(*) from public.sala_de_espera where universo = 'T6'",
    "SALA_EU_T5_001": "select count(*) from public.sala_de_espera where source_id = 'EU-T5-001'",
    "RAW": "select count(*) from public.raw_asset",
    "RUNS": "select count(*) from public.collection_run",
}


def contar() -> dict:
    return {k: int(MC.sql(q)[0][0]) for k, q in CONTAR.items()}


def main(argv) -> int:
    opt = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    saida = Path(opt["saida"]).resolve()
    universo = opt.get("universo", "T5")
    saida.mkdir(parents=True, exist_ok=True)
    os.environ.pop("SINTONIA_SALA_DSN", None)                 # 1: a leitura real vem do SALA_DSN.txt
    real_antes = E.fotografia()
    dump = saida / "SALA-COPIA.dump"
    r = subprocess.run(PB.comando_de_backup(MC._dsn(), dump), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    real_depois = E.fotografia()
    res = {"UNIVERSO": universo, "PG_DUMP_CODIGO": r.returncode, "DUMP_BYTES": dump.stat().st_size if dump.exists() else 0,
           "SALA_REAL_LINHAS": {t: v["LINHAS"] for t, v in real_antes.items()},
           "SALA_REAL_MUDOU_DURANTE_O_DUMP": real_antes != real_depois}
    base = E.Base(saida / "pg")
    try:
        subprocess.run([base.exe("initdb"), "-D", str(base.pasta), "-U", "postgres", "--auth=trust",
                        "-E", "UTF8", "--no-sync"], check=True, capture_output=True)
        subprocess.run([base.exe("pg_ctl"), "-D", str(base.pasta), "-o", f"-p {base.porto} -h 127.0.0.1",
                        "-l", str(base.pasta / "servidor.log"), "-w", "start"], check=True,
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        res["RESTAURO"] = base.restaurar(dump)
        os.environ["SINTONIA_SALA_DSN"] = base.url            # daqui para baixo: SO a copia
        res["COPIA_IGUAL_A_REAL"] = E.fotografia() == real_antes
        res["ANTES"] = contar()
        env = dict(os.environ, SINTONIA_SALA_BACKEND="POSTGRES", SINTONIA_SALA_DSN=base.url,
                   SINTONIA_COLLECTION_DSN=base.url, SINTONIA_PSQL_EXE=MC._psql(),
                   PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
                   HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
        for n in (1, 2):
            sala_f = saida / ("sala-ficheiro-%d" % n)
            sala_f.mkdir(exist_ok=True)
            p = subprocess.run([sys.executable, "provas/o_pedido_t6_atravessa.py", "--universo=" + universo,
                                "--sala=" + str(sala_f), "--banco=" + base.url],
                               cwd=str(RAIZ), env=env, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=3600)
            (saida / ("PASSAGEM-%d.txt" % n)).write_text(p.stdout + "\n--- stderr ---\n" + p.stderr[-4000:],
                                                          encoding="utf-8")
            try:
                recibo = json.loads(p.stdout[p.stdout.index("{"):])
            except ValueError:
                recibo = {"ERRO_A_LER_A_SAIDA": p.stdout[-800:], "STDERR": p.stderr[-800:]}
            res["PASSAGEM_%d" % n] = {"CODIGO": p.returncode, "ADMISSAO": recibo.get("ADMISSAO"),
                                      "COLHEITA": recibo.get("COLHEITA_ENCONTRADA"),
                                      "PORTA": recibo.get("PORTA"), "INGRESSO": recibo.get("INGRESSO"),
                                      "ERRO": recibo.get("ERRO") or recibo.get("ERRO_A_LER_A_SAIDA")}
            res["DEPOIS_%d" % n] = contar()
            if n == 1:
                # «COM QUE CAMPOS»: cada coluna de texto da Sala, preenchida (≠ NAO SEI) nas linhas novas
                cols = [c[0] for c in MC.sql(
                    "select column_name from information_schema.columns where table_schema = 'public' "
                    "and table_name = 'sala_de_espera' and data_type in ('text', 'character varying', 'jsonb', 'json') "
                    "order by ordinal_position")]
                campos = {}
                for c in cols:
                    campos[c] = int(MC.sql(
                        "select count(*) from public.sala_de_espera where source_id = 'EU-T5-001' "
                        "and %s is not null and %s::text not in ('NAO SEI', '\"NAO SEI\"', '')" % (c, c))[0][0])
                res["CAMPOS_PREENCHIDOS_NAS_LINHAS_NOVAS"] = campos
                res["UMA_LINHA_NOVA"] = MC.sql(
                    "select row_to_json(s)::text from public.sala_de_espera s where source_id = 'EU-T5-001' "
                    "order by 1 limit 1")[0][0][:3000]
    finally:
        os.environ.pop("SINTONIA_SALA_DSN", None)
        base.descer()
    a, d1, d2 = res.get("ANTES", {}), res.get("DEPOIS_1", {}), res.get("DEPOIS_2", {})
    res["ENTRARAM_NA_1A"] = {k: d1.get(k, 0) - a.get(k, 0) for k in CONTAR} if d1 else None
    res["ENTRARAM_NA_2A"] = {k: d2.get(k, 0) - d1.get(k, 0) for k in CONTAR} if d2 else None
    (saida / "ENSAIO-T6-COPIA-SALA.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str),
                                                    encoding="utf-8")
    shutil.rmtree(saida / "pg", ignore_errors=True)
    print(json.dumps({k: res.get(k) for k in ("PG_DUMP_CODIGO", "SALA_REAL_MUDOU_DURANTE_O_DUMP",
                                               "COPIA_IGUAL_A_REAL", "ANTES", "ENTRARAM_NA_1A",
                                               "ENTRARAM_NA_2A")}, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
