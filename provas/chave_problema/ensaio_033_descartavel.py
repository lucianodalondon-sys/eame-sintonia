#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHAVE-PROBLEMA · ENSAIO numa Sala DESCARTAVEL: a 033 guarda a chave PROBLEMA sem migracao nova.

    PG_BIN=/usr/lib/postgresql/16/bin python3 provas/chave_problema/ensaio_033_descartavel.py <saida.json>

(Sem PG_BIN, os binarios portateis de ~/orca/pgtmp, como scripts/micro_coleta/ensaio_offline.py.)
`initdb` recusa correr como root: num contentor, corra-o como o utilizador `postgres`.

1. sobe um Postgres DESCARTAVEL (porta livre, initdb proprio) e corre TODAS as migracoes pela cadeia canonica;
2. pousa DOIS itens T3 pela porta `sala_de_espera.pousar`: um com a janela de HOJE (PROBLEMA/v1 dentro — prova
   que a trava `janela_declara_as_quatro_chaves` aceita a quinta chave) e um ANTIGO (a janela `JANELA_NAO_MEDIDA`,
   sem PROBLEMA — o que a Sala real tem);
3. exporta a COPIA pela vista `sala_de_espera_atual` (o comando do CHAVE-PROBLEMA.md), corre o reprocesso SECO,
   APLICA pela porta `rever`, e aplica outra vez (tem de dar 0 inseridas);
4. le pela vista (`ler_atual`) e passa o item antigo pela CAP-WIN (`par_em_campo`): a chave vira ISSUE_ID;
5. confere: `sala_de_espera` com o MESMO conteudo (md5) antes e depois; UPDATE e DELETE na revisao recusados;
6. desliga e apaga o banco. Nunca a Sala real (porta 54330 recusada).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for p in ("", "admissao", "leis", "motor", "coleta", "orquestrador"):
    sys.path.insert(0, str(RAIZ / p))
import _gavetas  # noqa: E402,F401
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
if os.environ.get("PG_BIN"):
    E.PG_BIN = Path(os.environ["PG_BIN"])

import admissao as adm  # noqa: E402
import reprocessar_problema as RP  # noqa: E402

TEXTO = ("Bollettino fitosanitario n. 38 [SINTETICO]\nOLIVO\n"
         "Si registrano catture di mosca delle olive (Bactrocera oleae) in aumento nelle trappole.\n")


def _ready(i, **kw):
    item = {"id": "derived:%d" % i, "texto": TEXTO, "source_id": "IT-T3-002", "artifact_type": "DERIVED",
            "parent_sha256": "a" * 64, "raw_asset_id": None, "captured_at": "2026-09-18T17:19:15Z"}
    item.update(kw)
    d = adm.Decisao(item=item["id"], universo="T3", resultado=adm.SIM, regra="ensaio", motivo="ensaio",
                    corrida="R1")
    return adm.pronto_para_inteligencia(item, d)


def main(saida):
    import sala_de_espera as espera
    import cap_win as W
    import afirmacao_da_fonte as AF
    pasta = Path(tempfile.mkdtemp(prefix="chave-problema-"))
    base = E.Base(pasta / "pg")
    if ":54330/" in base.url:
        raise SystemExit("isto e a Sala real")
    env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
    fora = {"PG_BIN": str(E.PG_BIN), "PASSOS": {}}
    amb = dict(os.environ)

    def sql(c):
        r = subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-c", c, base.url],
                           capture_output=True, text=True, encoding="utf-8")
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    try:
        r = base.subir(RAIZ, env)
        fora["PASSOS"]["1_MIGRACOES"] = {"CODIGO": r["CODIGO"], "PASS": r["MIGRATIONS_PASS"]}
        if r["CODIGO"] != 0:
            raise RuntimeError("migracoes falharam: " + r["ERRO"])
        os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": base.url,
                           "SINTONIA_PSQL_EXE": base.exe("psql")})
        sql("insert into collection_run (run_id, platform, started_at, rule_version) "
            "values ('R1', 'ensaio', now(), 'ensaio')")
        novo, antigo = _ready(1), _ready(2)
        antigo["JANELA_DECLARADA"] = adm.JANELA_NAO_MEDIDA           # o que a Sala real tem: sem PROBLEMA
        espera.pousar("R1", [novo, antigo])
        c, n, _e = sql("select count(*) from sala_de_espera where janela_declarada::jsonb ? 'PROBLEMA'")
        fora["PASSOS"]["2_POUSAR"] = {"LINHAS_COM_PROBLEMA_NA_033": int(n), "ESPERADO": 1}
        md5 = "select md5(string_agg(t::text, '|' order by run_id, ordem)) from sala_de_espera t"
        antes = sql(md5)[1]
        # 3 · a COPIA, pela vista (o mesmo select do CHAVE-PROBLEMA.md)
        c, copia, e = sql("select json_agg(json_build_object('run_id', run_id, 'ordem', ordem, 'item_id', item_id, "
                          "'universo', universo, 'texto', texto, 'janela_declarada', janela_declarada) "
                          "order by run_id, ordem) from public.sala_de_espera_atual")
        antes_do_reprocesso = next(u for u in espera.ler_atual("R1")["ITENS"] if u["ITEM_ID"] == "derived:2")
        _par, falta_antes = W.par_em_campo({"TEXTO": antes_do_reprocesso["TEXTO"],
                                            "JANELA_DECLARADA": antes_do_reprocesso["JANELA_DECLARADA"]})
        seco = RP.reprocessar(json.loads(copia))
        rec1 = RP.aplicar(seco)
        rec2 = RP.aplicar(RP.reprocessar(json.loads(sql(
            "select json_agg(json_build_object('run_id', run_id, 'ordem', ordem, 'item_id', item_id, "
            "'universo', universo, 'texto', texto, 'janela_declarada', janela_declarada) "
            "order by run_id, ordem) from public.sala_de_espera_atual")[1])))
        fora["PASSOS"]["3_REPROCESSO"] = {"CONTA_SECO": seco["CONTA"], "APLICAR_1": rec1, "APLICAR_2": rec2}
        # 4 · pela vista, e pela CAP-WIN
        atual = espera.ler_atual("R1")
        it = next(u for u in atual["ITENS"] if u["ITEM_ID"] == "derived:2")    # o ANTIGO
        par, falta = W.par_em_campo({"TEXTO": it["TEXTO"], "JANELA_DECLARADA": it["JANELA_DECLARADA"]})
        fora["PASSOS"]["4_LEITURA"] = {"PROBLEMA": it["JANELA_DECLARADA"]["PROBLEMA"]["VALOR"],
                                       "VEIO_DE": it["JANELA_DECLARADA"]["PROBLEMA"]["VEIO_DE"],
                                       "CODIGO": it["JANELA_DECLARADA"]["PROBLEMA"]["CODIGO"]["VALOR"],
                                       "PROBLEMA_LIDO_PELO_CONTRATO": AF.problema_da_chave(
                                           it["JANELA_DECLARADA"]["PROBLEMA"], it["TEXTO"])[0],
                                       "FALTA_NA_CAP_WIN_ANTES": falta_antes,
                                       "FALTA_NA_CAP_WIN_DEPOIS": falta,
                                       "NOTA": ("o item antigo continua sem CULTURA e REGIAO_DO_FATO (e a verdade "
                                                "da Sala): o par so fecha com as tres; o PROBLEMA saiu da falta"),
                                       "REVISOES_DA_LINHA": it["REVISOES"]}
        # 5 · a linha nao mudou; a revisao nao se edita nem se apaga
        depois = sql(md5)[1]
        up = sql("update sala_de_espera_revisao set valor = 'x'")
        de = sql("delete from sala_de_espera_revisao")
        fora["PASSOS"]["5_TRAVAS"] = {"SALA_IGUAL": antes == depois and bool(antes),
                                      "UPDATE_RECUSADO": up[0] != 0 and "SALA_REVISAO_SO_ACRESCENTA" in up[2],
                                      "DELETE_RECUSADO": de[0] != 0 and "SALA_REVISAO_SO_ACRESCENTA" in de[2]}
        p = fora["PASSOS"]
        fora["VEREDITO"] = "PASS" if (
            p["1_MIGRACOES"]["CODIGO"] == 0 and p["2_POUSAR"]["LINHAS_COM_PROBLEMA_NA_033"] == 1
            and rec1["INSERIDAS"] == 1 and rec2["INSERIDAS"] == 0
            and p["4_LEITURA"]["PROBLEMA_LIDO_PELO_CONTRATO"] == "mosca dell'olivo"
            and any("PROBLEMA" in f for f in p["4_LEITURA"]["FALTA_NA_CAP_WIN_ANTES"])
            and not any("PROBLEMA" in f for f in p["4_LEITURA"]["FALTA_NA_CAP_WIN_DEPOIS"])
            and all(p["5_TRAVAS"].values())) else "FAIL"
    finally:
        os.environ.clear()
        os.environ.update(amb)
        base.descer()
        shutil.rmtree(pasta, ignore_errors=True)
    fora["CODIGO"] = {"VERSAO_DO_EXTRATOR": RP.versao_do_codigo(),
                      "SHA256_DA_033": hashlib.sha256(next((RAIZ / "supabase" / "migrations").glob("033_*.sql"))
                                                      .read_bytes()).hexdigest()}
    with open(saida, "w", encoding="utf-8", newline="\n") as h:
        json.dump(fora, h, ensure_ascii=False, indent=1)
    print(json.dumps({"VEREDITO": fora["VEREDITO"], "PASSOS": {k: v for k, v in fora["PASSOS"].items()
                                                              if k != "3_REPROCESSO"}}, ensure_ascii=False, indent=1))
    return 0 if fora["VEREDITO"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "ENSAIO-033-CHAVE-PROBLEMA.json"))
