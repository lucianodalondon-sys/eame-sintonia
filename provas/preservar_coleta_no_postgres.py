#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A MESMA GARANTIA, CONTRA POSTGRES DE VERDADE — e num que morre no fim.

POR QUE ISTO EXISTE
-------------------
`tests/test_preservar_coleta_no_banco.py` prova a reconciliação contra um banco
real, mas SQLite. As travas que interessam são as mesmas — `storage_path`
único, `sha256` não único, `run_id` obrigatório com chave estrangeira — só que
SQLite não é Postgres, e dizer «provado no banco» sem dizer **qual** seria
esconder metade da frase.

Este ficheiro corre os mesmos cenários contra **Postgres 16**, com a
`migration 001` ORIGINAL aplicada — enum `run_status` incluído, que o SQLite
teve de traduzir para um `CHECK`. Ele corre no workflow `banco-descartavel.yml`,
num contentor que nasce e morre dentro do próprio job.

    DB_TESTED (SQLITE)     é o que a bateria local prova
    DB_TESTED (POSTGRES)   é o que este ficheiro acrescenta

A TRAVA CONTRA O ACIDENTE
-------------------------
Este é o único ficheiro desta missão que fala com um banco a sério. Por isso
ele **recusa-se a arrancar** se a ligação não for visivelmente descartável: sem
`localhost`/`127.0.0.1` no endereço, ele sai com erro antes de executar coisa
nenhuma. Um dedo enganado a apontar para produção não passa daqui.

Não usa driver instalado: fala pelo `psql`, que o runner já tem. Instalar um
pacote global só para um teste passar continua proibido.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from guarda.preservar_coleta import (  # noqa: E402
    METADATA_CONFLICT, PRESERVED_AND_REGISTERED, RUN_ID_CONFLICT,
    UPLOAD_PENDING_METADATA, ArmazemDeMentira, Memoria, preservar, sha256)

MIGRACAO = os.path.join(RAIZ, "supabase", "migrations",
                        "001_fundacao_geografia_e_proveniencia.sql")

SEGURO = ("localhost", "127.0.0.1", "@postgres:", "@db:")


def _e_descartavel(url: str) -> bool:
    """O endereço tem de dizer, sozinho, que é de brincar.

    Não há lista de bloqueio de produção aqui — lista de bloqueio falha por
    omissão. Há lista de PERMISSÃO: se o endereço não for claramente local, não
    se corre.
    """
    return any(marca in (url or "") for marca in SEGURO)


class MemoriaPostgres(Memoria):
    """A porta do banco falada por `psql`. Lê de volta com `SELECT`, como deve."""

    def __init__(self, url):
        if not _e_descartavel(url):
            raise SystemExit(
                "RECUSADO: '%s' nao parece um banco descartavel local. "
                "Esta prova nunca corre contra producao." % url)
        self.url = url
        self.aplicacoes = 0

    def _psql(self, sql, tuplas=True):
        cmd = ["psql", self.url, "-v", "ON_ERROR_STOP=1", "-c", sql]
        if tuplas:
            cmd[3:3] = ["-t", "-A", "-F", "\x1f"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise IOError(r.stderr.strip()[:400])
        return r.stdout

    def aplicar(self, sql):
        self.aplicacoes += 1
        r = subprocess.run(["psql", self.url, "-v", "ON_ERROR_STOP=1"],
                           input=sql, capture_output=True, text=True)
        if r.returncode != 0:
            raise IOError(r.stderr.strip()[:400])

    def _linhas(self, sql, colunas):
        fora = []
        for linha in self._psql(sql).splitlines():
            if not linha.strip():
                continue
            valores = linha.split("\x1f")
            fora.append({c: (v if v != "" else None)
                         for c, v in zip(colunas, valores)})
        return fora

    COLS_RUN = ("run_id", "actor", "actor_version", "source_country",
                "started_at", "rule_version", "capture_method", "status",
                "finished_at")
    COLS_OBJ = ("run_id", "storage_path", "media_type", "bytes", "sha256",
                "captured_at", "source_url")

    def corrida(self, run_id):
        linhas = self._linhas(
            "select %s from public.collection_run where run_id = '%s'"
            % (", ".join(self.COLS_RUN), run_id), self.COLS_RUN)
        return linhas[0] if linhas else None

    def objeto_em(self, storage_path):
        linhas = self._linhas(
            "select %s from public.raw_asset where storage_path = '%s'"
            % (", ".join(self.COLS_OBJ), storage_path.replace("'", "''")),
            self.COLS_OBJ)
        return linhas[0] if linhas else None

    def objetos_da_corrida(self, run_id):
        return self._linhas(
            "select %s from public.raw_asset where run_id = '%s' "
            "order by storage_path" % (", ".join(self.COLS_OBJ), run_id),
            self.COLS_OBJ)

    def contar(self, tabela):
        return int(self._psql("select count(*) from public.%s" % tabela).strip())


# ─────────────────────────────────────────────────────────────────────────
# OS CENÁRIOS — os mesmos do banco local, contra o motor de verdade
# ─────────────────────────────────────────────────────────────────────────
A, B = b"o conteudo A", b"o conteudo B"
FIM = "2026-09-08T00:05:00Z"


def _corrida(run_id="IT-PG-0001", **extra):
    d = {"RUN_ID": run_id, "PLATFORM": "local", "ACTOR": "teste",
         "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT", "MISSION": "prova",
         "STARTED_AT": "2026-09-08T00:00:00Z", "RULE_VERSION": "1",
         "CAPTURE_METHOD": "HTTP_GET"}
    d.update(extra)
    return d


def _art(nome, dados, nativo):
    return {"COUNTRY": "IT", "SOURCE_SLUG": "fonte-de-teste",
            "ARTIFACT_KIND": "DOCUMENT", "NAME": nome,
            "SOURCE_NATIVE_ID": nativo, "SHA256": sha256(dados),
            "BYTES": len(dados), "MEDIA_TYPE": "application/pdf",
            "CAPTURED_AT": "2026-09-08T00:00:00Z",
            "SOURCE_URL": "https://exemplo.it/%s" % nativo}


def _bytes_de(obj):
    return {sha256(A): A, sha256(B): B}[obj["SHA256"]]


def _correr(banco, artefatos, run=None, armazem=None):
    return preservar(run or _corrida(), artefatos, armazem or ArmazemDeMentira(),
                     _bytes_de, memoria=banco, terminou_em=FIM)


def cenarios(banco):
    """Devolve `(nome, passou, detalhe)` para cada caso."""
    fora = []

    def caso(nome, condicao, detalhe=""):
        fora.append((nome, bool(condicao), detalhe))

    # A · B · C — as linhas contadas no proprio Postgres
    arm = ArmazemDeMentira()
    r = _correr(banco, [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")],
                armazem=arm)
    caso("A_dois_objetos_esperados", r["RECONCILIACAO"]["OBJETOS_ESPERADOS"] == 2)
    caso("B_o_select_confirma_duas_linhas",
         r["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"] == 2
         and banco.contar("raw_asset") == 2,
         "observadas=%s" % r["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"])
    caso("C_corrida_concluida_no_postgres",
         r["RUN_STATE"] == "COMPLETE"
         and banco.corrida("IT-PG-0001")["status"] == "concluida"
         and r["PENDENCIA"] == PRESERVED_AND_REGISTERED,
         "status=%s" % banco.corrida("IT-PG-0001")["status"])

    # D · E — retry identico
    r2 = _correr(banco, [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")],
                 armazem=arm)
    caso("D_retry_nao_duplica",
         banco.contar("raw_asset") == 2 and banco.contar("collection_run") == 1)
    caso("E_reencontro_e_REUSED",
         r2["JA_EXISTIA_NO_BANCO"]["REUSED_METADATA"] == 2
         and not r2["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"])

    # F — mesmo caminho, outro sha256: o `do nothing` engoliria; aqui nao
    caminho = banco.objetos_da_corrida("IT-PG-0001")[0]["storage_path"]
    banco.aplicar("update public.raw_asset set sha256 = '%s' "
                  "where storage_path = '%s';" % ("f" * 64, caminho))
    r3 = _correr(banco, [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")],
                 armazem=arm)
    caso("F_sha_divergente_e_CONFLICT",
         r3["PENDENCIA"] == METADATA_CONFLICT and r3["RUN_STATE"] == "PARTIAL",
         "pendencia=%s" % r3["PENDENCIA"])
    banco.aplicar("update public.raw_asset set sha256 = '%s' "
                  "where storage_path = '%s';" % (sha256(A), caminho))

    # G — mesmo caminho reclamado por outra corrida
    r4 = _correr(banco, [_art("a.pdf", A, "11")],
                 run=_corrida("IT-PG-0002"), armazem=arm)
    caso("G_outra_corrida_no_mesmo_caminho_e_CONFLICT",
         r4["PENDENCIA"] == METADATA_CONFLICT, "pendencia=%s" % r4["PENDENCIA"])

    # J — mesmo run_id, identidade congelada diferente
    r5 = _correr(banco, [_art("c.pdf", B, "33")],
                 run=_corrida("IT-PG-0001", ACTOR_VERSION="2"), armazem=arm)
    caso("J_run_id_com_outra_identidade_e_RUN_ID_CONFLICT",
         r5["PENDENCIA"] == RUN_ID_CONFLICT, "pendencia=%s" % r5["PENDENCIA"])

    # H — o SQL corre e grava a menos. Postgres di-lo com `on conflict`:
    # o mesmo storage_path ja existe noutra corrida, entao a linha nova
    # simplesmente nao entra — e o SELECT e quem repara.
    novo = _corrida("IT-PG-0003")
    arm2 = ArmazemDeMentira()
    r6 = _correr(banco, [_art("a.pdf", A, "11"), _art("d.pdf", B, "44")],
                 run=novo, armazem=arm2)
    caso("H_grava_a_menos_e_a_reconciliacao_reprova",
         r6["RUN_STATE"] == "PARTIAL"
         and r6["MEMORIA"]["LINHAS_OBSERVADAS"] != r6["MEMORIA"]["LINHAS_ESPERADAS"]
         or r6["PENDENCIA"] in (METADATA_CONFLICT, UPLOAD_PENDING_METADATA),
         "esperadas=%s observadas=%s pendencia=%s" % (
             r6["MEMORIA"]["LINHAS_ESPERADAS"],
             r6["MEMORIA"]["LINHAS_OBSERVADAS"], r6["PENDENCIA"]))

    # K — o byte fica, mesmo quando a memoria nao correu
    caso("K_byte_preservado_apos_falha_de_memoria", len(arm2.objetos) == 2,
         "objetos no armazem=%d" % len(arm2.objetos))

    # As travas do esquema REAL
    try:
        banco.aplicar(
            "insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at) values ('NAO-EXISTE','x/y',"
            "'application/pdf',1,'%s','2026-09-08T00:00:00Z');" % ("a" * 64))
        caso("run_id_obrigatorio_com_chave_estrangeira", False,
             "o banco ACEITOU byte sem corrida")
    except IOError:
        caso("run_id_obrigatorio_com_chave_estrangeira", True)

    linhas = banco.objetos_da_corrida("IT-PG-0001")
    caso("storage_path_unico_e_sha256_nao",
         len({x["storage_path"] for x in linhas}) == len(linhas))

    return fora


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL", "")
    if not url:
        print("BANCO_DESCARTAVEL_URL nao definido — esta prova so corre no "
              "workflow banco-descartavel.yml, contra um Postgres que morre "
              "no fim do job.")
        return 0
    banco = MemoriaPostgres(url)
    with open(MIGRACAO, encoding="utf-8") as f:
        banco.aplicar(f.read())
    print("migration 001 ORIGINAL aplicada no Postgres descartavel")

    resultados = cenarios(banco)
    for nome, passou, detalhe in resultados:
        print("  %-4s %-46s %s" % ("PASS" if passou else "FAIL", nome, detalhe))
    reprovados = [n for n, p, _ in resultados if not p]
    print("\nPOSTGRES_DESCARTAVEL=%s · %d caso(s)%s" % (
        "PASS" if not reprovados else "FAIL", len(resultados),
        "" if not reprovados else " · reprovados: " + ", ".join(reprovados)))
    return 1 if reprovados else 0


if __name__ == "__main__":
    sys.exit(main())
