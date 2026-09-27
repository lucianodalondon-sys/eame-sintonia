"""PROVA DO BACKUP DA SALA — o dump que desfaz a micro, provado com os dados verdadeiros.

    py scripts/micro_coleta/provar_backup_da_sala.py [--saida=DIR]

1. Fotografa a Sala REAL (contagem e md5 do conteudo das 5 tabelas), so SELECT com
   default_transaction_read_only (o cliente do micro_coleta).
2. Faz o backup com o MESMO comando do ~/sintonia-sala-italia/backup_sala.cmd:
       pg_dump -Fc -Z 6 --no-owner --no-privileges -f <ficheiro> <DSN>
   O pg_dump so le. O ficheiro vai para a pasta de saida (por omissao, TEMP).
3. Fotografa outra vez: se mudou durante o dump, a prova nao vale e diz-se.
4. Repoe o dump num Postgres DESCARTAVEL (sala_italia numa porta livre) e fotografa.
5. IGUAL = o backup esta completo e e restauravel: e o rollback da micro, provado
   com os dados de verdade. O dropdb da Sala real (com o servico parado) nao e
   exercido aqui — esse passo foi provado no ensaio offline (--provar-rollback).

Nada e escrito na Sala real.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import ensaio_offline as E  # noqa: E402
import micro_coleta as MC   # noqa: E402


def comando_de_backup(dsn: str, ficheiro: Path) -> list[str]:
    """O comando exacto do backup_sala.cmd — o que se corre IMEDIATAMENTE antes da micro."""
    return [str(E.PG_BIN / ("pg_dump.exe" if os.name == "nt" else "pg_dump")), "-Fc", "-Z", "6",
            "--no-owner", "--no-privileges", "-f", str(ficheiro), dsn]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    saida = next((Path(a.split("=", 1)[1]) for a in argv if a.startswith("--saida=")),
                 Path(os.environ.get("TEMP", "/tmp")) / ("prova-backup-sala-" +
                                                         datetime.now().strftime("%Y%m%d-%H%M%S")))
    saida.mkdir(parents=True, exist_ok=True)
    dsn_real = MC._dsn()
    os.environ.pop("SINTONIA_SALA_DSN", None)            # a leitura real vem do SALA_DSN.txt
    foto_real_antes = E.fotografia()
    dump = saida / "SALA-ANTES-DA-MICRO.dump"
    r = subprocess.run(comando_de_backup(dsn_real, dump), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    foto_real_depois = E.fotografia()
    lista = subprocess.run([str(E.PG_BIN / "pg_restore.exe"), "-l", str(dump)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    base = E.Base(saida / "pg")
    resultado = {"QUANDO": E.agora(), "DUMP": str(dump), "PG_DUMP_CODIGO": r.returncode,
                 "PG_DUMP_ERRO": r.stderr[-300:], "BYTES": dump.stat().st_size if dump.exists() else 0,
                 "INDICE_TEM_SALA_DE_ESPERA": "sala_de_espera" in lista.stdout,
                 "SALA_REAL_ANTES": foto_real_antes, "SALA_REAL_DEPOIS_DO_DUMP": foto_real_depois,
                 "SALA_REAL_MUDOU_DURANTE_O_DUMP": foto_real_antes != foto_real_depois}
    try:
        subprocess.run([base.exe("initdb"), "-D", str(base.pasta), "-U", "postgres",
                        "--auth=trust", "-E", "UTF8", "--no-sync"], check=True, capture_output=True)
        subprocess.run([base.exe("pg_ctl"), "-D", str(base.pasta), "-o",
                        f"-p {base.porto} -h 127.0.0.1", "-l", str(base.pasta / "servidor.log"),
                        "-w", "start"], check=True, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        resultado["RESTAURO"] = base.restaurar(dump)
        os.environ["SINTONIA_SALA_DSN"] = base.url
        resultado["COPIA_RESTAURADA"] = E.fotografia()
        resultado["IGUAL_A_SALA_REAL"] = resultado["COPIA_RESTAURADA"] == foto_real_antes
    finally:
        os.environ.pop("SINTONIA_SALA_DSN", None)
        base.descer()
    resultado["PROVA_VALE"] = (r.returncode == 0 and not resultado["SALA_REAL_MUDOU_DURANTE_O_DUMP"]
                               and resultado.get("IGUAL_A_SALA_REAL") is True)
    (saida / "PROVA-BACKUP-SALA.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1),
                                                  encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in ("PG_DUMP_CODIGO", "BYTES", "INDICE_TEM_SALA_DE_ESPERA",
                                                  "SALA_REAL_MUDOU_DURANTE_O_DUMP", "IGUAL_A_SALA_REAL",
                                                  "PROVA_VALE") if k in resultado},
                     ensure_ascii=False), flush=True)
    print("escrito:", saida / "PROVA-BACKUP-SALA.json", flush=True)
    return 0 if resultado["PROVA_VALE"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
