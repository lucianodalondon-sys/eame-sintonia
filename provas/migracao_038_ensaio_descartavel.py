#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENSAIO da PROPOSTA 038 numa Sala DESCARTAVEL (myfruit, 28/09). NUNCA a Sala real.

    py provas/migracao_038_ensaio_descartavel.py <saida.json>

1. sobe um Postgres descartavel e corre a cadeia canonica das migrations;
2. poe UM item na Sala pelo caminho real (`admissao.pronto_para_inteligencia` + `sala_de_espera.pousar`),
   com a impressao do conteudo antes de qualquer preco;
3. aplica a proposta `supabase/propostas/038_a_sala_guarda_o_preco.sql` DESTA arvore;
4. escreve dois precos pelo escritor (`admissao/preco_na_sala.registar`): um com o literal italiano
   («€237,00») e uma AUSENCIA (que nao pode escrever nada);
5. confere: a vista le o literal byte a byte com o RAW_SHA256 e o DOCUMENT_ID; o reprocesso nao duplica;
   UPDATE/DELETE/TRUNCATE recusados; PIAZZA sem praca recusado; preco de item inexistente recusado;
   a linha da Sala NAO mudou;
6. desfaz a 038 e confere que a tabela saiu e a Sala ficou igual;
7. escreve o JSON com PASSO/VEREDITO e o sha256 da proposta ensaiada.

Sem os binarios de ~/orca/pgtmp e sem bash, diz por que nao correu — nunca inventa um PASS.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "admissao"))
_spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
import _gavetas                          # noqa: E402,F401
import admissao as adm                   # noqa: E402
import sala_de_espera as espera          # noqa: E402
import preco_na_sala as PS               # noqa: E402

PROPOSTA = next(iter((RAIZ / "supabase" / "migrations").glob("038_*.sql")))
DESFAZER = RAIZ / "supabase" / "desfazer" / "038_desfazer.sql"
SHA = "b" * 64


def _preco(**kw):
    p = {"INDICADOR": "PRECO", "CULTURA": "Riso", "NIVEL": "PIAZZA", "PRACA": "Bologna",
         "VALOR_TEXTO": "€237,00", "VALOR_NUMERICO": "237.00", "UNIDADE": "€/100kg",
         "PERIODO_INICIO": "2026-09-07", "PERIODO_FIM": "2026-09-13", "CLASSE": "CURRENT",
         "CITACAO": "Riso, Bologna: €237,00 / 100 kg",
         "O_QUE_NAO_PROVA": "preco de piazza nao e preco nacional, e preco nao e lucro",
         "RAW_SHA256": SHA, "DOCUMENT_ID": "DOC-1", "ONDE": "tabela 2, linha 7"}
    p.update(kw)
    return p


def main():
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ensaio-038.json")
    fora = {"PROPOSTA": PROPOSTA.name,
            "PROPOSTA_SHA256": hashlib.sha256(PROPOSTA.read_bytes()).hexdigest(),
            "PASSOS": {}}
    if not (E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")).exists() or not shutil.which("bash"):
        fora["VEREDITO"] = "NAO_CORREU: sem Postgres portatil (~/orca/pgtmp) ou sem bash"
        saida.write_text(json.dumps(fora, ensure_ascii=False, indent=2), encoding="utf-8")
        print(fora["VEREDITO"])
        return 1

    pasta = Path(tempfile.mkdtemp(prefix="ensaio-038-"))
    base = E.Base(pasta / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
    amb = dict(os.environ)

    def psql(sql, falhar=True):
        # O SQL vai pela ENTRADA em UTF-8 (o «€» na linha de comando rebenta: 0x80).
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-F", "|",
                            "-v", "ON_ERROR_STOP=1", "-d", base.url, "-f", "-"], input=sql,
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env={**os.environ, "PGCLIENTENCODING": "UTF8"})
        if falhar and r.returncode:
            raise AssertionError(r.stderr)
        return r.stdout.strip(), r.stderr.strip(), r.returncode

    def ficheiro(f):
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1",
                            "--single-transaction", "-f", str(f), base.url],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            raise AssertionError(r.stderr[-600:])

    try:
        r = base.subir(RAIZ, env)
        if r["CODIGO"] != 0:
            raise AssertionError("a cadeia das migrations falhou: %s" % r["ERRO"])
        fora["MIGRATIONS_PASS"] = r["MIGRATIONS_PASS"]

        os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES",
                           "SINTONIA_SALA_DSN": base.url,
                           "SINTONIA_PSQL_EXE": base.exe("psql")})
        psql("insert into collection_run (run_id, platform, started_at, rule_version) "
             "values ('R1', 'teste', now(), 'teste')")
        item = {"id": "derived:myfruit-1", "texto": "Listino prezzi myfruit",
                "source_id": "IT-MYFRUIT", "artifact_type": "DERIVED",
                "parent_sha256": "a" * 64, "raw_asset_id": None,
                "captured_at": "2026-09-28T12:00:00Z"}
        d = adm.Decisao(item=item["id"], universo="T3", resultado=adm.SIM,
                        regra="teste", motivo="teste", corrida="R1")
        espera.pousar("R1", [adm.pronto_para_inteligencia(item, d)])
        impressao = ("select count(*) || ' ' || coalesce(md5(string_agg(t::text, '' "
                     "order by run_id, ordem)), '-') from public.sala_de_espera t")
        fora["PASSOS"]["1_sala_com_o_item"] = "PASS" if psql(impressao)[0].startswith("1 ") else "FAIL"
        antes = psql(impressao)[0]

        ficheiro(PROPOSTA)
        fora["PASSOS"]["2_proposta_aplicada"] = (
            "PASS" if psql("select to_regclass('public.sala_de_espera_preco') is not null")[0] == "t"
            else "FAIL")

        fora["PASSOS"]["3_o_preco_entra"] = PS.registar(
            "R1", [(0, _preco())], dsn=base.url, psql=base.exe("psql"))
        fora["PASSOS"]["4_a_ausencia_nao_escreve_nada"] = PS.registar(
            "R1", [(0, _preco(VALOR_TEXTO="NAO SEI", VALOR_NUMERICO=None)),
                   (0, _preco(PERIODO_INICIO="2026-09-14", PERIODO_FIM="2026-09-20", CLASSE="OUTLOOK",
                              VALOR_TEXTO="NAO SEI"))], dsn=base.url, psql=base.exe("psql"))
        lido = PS.ler("R1", dsn=base.url, psql=base.exe("psql"))
        fora["5_o_que_a_vista_le"] = lido
        fora["PASSOS"]["5_a_vista_le_o_literal_com_a_prova"] = (
            "PASS" if lido and lido[0][2] == "€237,00" and lido[0][4] == SHA and lido[0][5] == "DOC-1"
            else "FAIL")

        PS.registar("R1", [(0, _preco())], dsn=base.url, psql=base.exe("psql"))
        fora["PASSOS"]["6_o_reprocesso_nao_duplica"] = (
            "PASS" if psql("select count(*) from sala_de_espera_preco")[0] == "1" else "FAIL")

        recusas = {}
        for nome, sql in (
                ("update", "update sala_de_espera_preco set valor_texto='€1,00'"),
                ("delete", "delete from sala_de_espera_preco"),
                ("truncate", "truncate sala_de_espera_preco"),
                ("piazza_sem_praca",
                 "insert into sala_de_espera_preco (run_id, ordem, indicador, cultura_literal, nivel, "
                 "valor_texto, unidade, periodo_inicio, periodo_fim, classe, citacao_literal, "
                 "o_que_nao_prova, prova) values ('R1', 0, 'PRECO', 'Riso', 'PIAZZA', '€1,00', 'kg', "
                 "'2026-09-07', '2026-09-13', 'CURRENT', 'x', 'y', "
                 "'{\"RAW_SHA256\": \"%s\", \"ONDE\": \"z\"}')" % SHA),
                ("item_inexistente",
                 "insert into sala_de_espera_preco (run_id, ordem, indicador, cultura_literal, nivel, "
                 "valor_texto, unidade, periodo_inicio, periodo_fim, classe, citacao_literal, "
                 "o_que_nao_prova, prova) values ('R1', 99, 'PRECO', 'Riso', 'NACIONAL', '€1,00', 'kg', "
                 "'2026-09-07', '2026-09-13', 'CURRENT', 'x', 'y', "
                 "'{\"RAW_SHA256\": \"%s\", \"ONDE\": \"z\"}')" % SHA)):
            _, erro, codigo = psql(sql, falhar=False)
            recusas[nome] = "RECUSADO" if codigo else "ACEITOU (era para recusar)"
        fora["7_o_que_o_banco_recusa"] = recusas
        fora["PASSOS"]["7_as_travas_recusam"] = (
            "PASS" if all(v == "RECUSADO" for v in recusas.values()) else "FAIL")

        fora["PASSOS"]["8_a_linha_da_sala_nao_mudou"] = (
            "PASS" if psql(impressao)[0] == antes else "FAIL")

        ficheiro(DESFAZER)
        fora["PASSOS"]["9_o_desfazer_leva_o_preco_e_deixa_a_sala"] = (
            "PASS" if (psql("select to_regclass('public.sala_de_espera_preco') is null")[0] == "t"
                       and psql("select to_regclass('public.sala_de_espera_precos') is null")[0] == "t"
                       and psql(impressao)[0] == antes) else "FAIL")
        # Nem todo o passo bom se chama «PASS»: o escritor responde com o verbo do que fez
        # (REGISTADO / NADA_A_REGISTAR). O veredito compara com o que cada passo DEVE devolver —
        # senao um passo bom contava como falha, e o ensaio mentiria ao contrario.
        esperado = {"3_o_preco_entra": "REGISTADO",
                    "4_a_ausencia_nao_escreve_nada": "NADA_A_REGISTAR"}
        bons = [k for k, v in fora["PASSOS"].items() if v == esperado.get(k, "PASS")]
        fora["VEREDITO"] = ("PASS %d/%d" % (len(bons), len(fora["PASSOS"]))
                            if len(bons) == len(fora["PASSOS"]) else
                            "FALHOU: %s" % [k for k in fora["PASSOS"] if k not in bons])
    except Exception as e:                                          # noqa: BLE001
        fora["VEREDITO"] = "FALHOU: %s" % e
    finally:
        try:
            base.descer()
        finally:
            os.environ.clear()
            os.environ.update(amb)
            shutil.rmtree(pasta, ignore_errors=True)
    saida.write_text(json.dumps(fora, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(fora, ensure_ascii=False, indent=2))
    return 0 if fora["VEREDITO"].startswith("PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
