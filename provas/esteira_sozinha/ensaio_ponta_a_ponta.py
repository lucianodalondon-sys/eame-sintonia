#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESTEIRA-SOZINHA — o ensaio de ponta a ponta, sem rede: coleta -> Sala -> Intelligence -> pote -> vigia.

    python3 provas/esteira_sozinha/ensaio_ponta_a_ponta.py [saida.json]

O QUE E REAL (o mesmo codigo que o supervisor chama)
    admissao/passagem_para_a_sala.passar_se_devido   -> backup PROVA_VALE (pg_dump + restauro + md5)
        -> italy_executor.colher (o envelope refeito pelo dono) -> orquestrador --so-a-porta
        -> RAW -> DERIVED -> STRUCTURED -> Admission -> sala_de_espera.pousar
    admissao/gatilho_da_inteligencia.correr_se_devido -> backup + copia + export read-only (RUNBOOK-R7)
        -> motor_das_capacidades -> pote -> validar_pote_v2 -> sobe ou nao sobe
    medidas/vigia_da_esteira.vigiar_se_devido        -> ESTEIRA-SAUDE.json
    O banco: PostgreSQL 16 descartavel, numa porta livre, com a cadeia `migrations` inteira.

O QUE E DE ENSAIO (dito para ninguem ler isto como prova de producao)
  * A COLETA nao sai para a rede: e a colheita REAL que ja esta no repositorio — linhas verbatim de
    data/collection-ledger/italy/runs.ndjson e observations.ndjson, bytes em data/collection-store/.
    O livro de corridas da COPIA fica so com essas linhas; nada no repositorio e tocado.
  * A ARVORE e uma copia (git ls-files -co) numa pasta temporaria: o livro de decisoes, os envelopes,
    o estado e o pote escrevem-se la.
  * O «AGORA» da Intelligence e declarado: primeiro agora (espera), depois agora + 4 h (a regra).
  * PASSADO: o ensaio poe PAS_DESDE antes das corridas de 21/09, como o coordenador faria com --desde.
  * FECHO 28/09 — A PORTA QUE FALHA: a primeira passagem real corre com a porta a ver uma Sala MORTA
    (SINTONIA_SALA_DSN numa porta fechada SO no subprocesso da porta; o backup ve a Sala viva). Tem de
    dar FALHOU, nada em PAS_PASSAGENS, a causa em PAS_FALHAS; a passagem seguinte (agora + RECUO + 1
    min, a Sala de volta) leva as mesmas corridas e a Sala sobe.
    So falha quem precisava da Sala: uma corrida sem SIM (so NAO/NAO_SEI) nao pousa nada e passa.
    Cada tentativa deixa o seu RAW e a sua collection_run no armazem (os bytes deduplicam-se no
    storage_object): e o rasto verdadeiro da tentativa, nao lixo.
  * FECHO 28/09 — A RETENCAO: o ensaio declara GUARDAR_BACKUPS = 1 para a poda ter o que podar em
    duas passagens; a da falha perde o pesado (pg/, dump), a em curso fica inteira.
  * Como root o postgres recusa arrancar: initdb/pg_ctl correm por `runuser -u postgres`.

Sem Postgres (SINTONIA_PG_BIN ou `pg_config --bindir`): sai 4 e NAO SEI — nunca PASS.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

AQUI = Path(__file__).resolve()
RAIZ = AQUI.parents[2]
SAIDA_PADRAO = AQUI.parent / "ENSAIO-PONTA-A-PONTA.json"
CORRIDAS = ("IT-T10-2026-09-21-192602-b9c48c5e22f8a0a0",   # IT-T10-018 myfruit · 30 observacoes
            "IT-T7-2026-09-21-193046-344a587db4870ed8",    # IT-T7-043 federchimica · 2 observacoes
            "OPS_forward-only-live_20260922185447_a9d037")  # a tarefa ForwardOnly · varias fontes
MORTA = "http://127.0.0.1:9"


def _bin_do_postgres() -> Path | None:
    if os.environ.get("SINTONIA_PG_BIN"):
        return Path(os.environ["SINTONIA_PG_BIN"])
    try:
        return Path(subprocess.run(["pg_config", "--bindir"], capture_output=True, text=True,
                                   check=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return None


def _embrulhar_como_postgres(real: Path, pasta: Path) -> Path:
    """Como root: initdb e pg_ctl por `runuser -u postgres`; o resto (clientes) direto."""
    pasta.mkdir(parents=True, exist_ok=True)
    for f in real.iterdir():
        alvo = pasta / f.name
        if f.name in ("initdb", "pg_ctl", "postgres"):
            alvo.write_text('#!/bin/sh\nexec runuser -u postgres -- "%s" "$@"\n' % f, encoding="utf-8")
            alvo.chmod(0o755)
        else:
            alvo.symlink_to(f)
    return pasta


def fora(saida: Path) -> int:
    real = _bin_do_postgres()
    if real is None or not (real / "initdb").exists():
        saida.write_text(json.dumps({"ESTADO": "NAO SEI", "PORQUE": "sem binarios do Postgres"}), encoding="utf-8")
        print("NAO SEI: sem binarios do Postgres (SINTONIA_PG_BIN)")
        return 4
    t = Path(tempfile.mkdtemp(prefix="esteira-e2e-"))
    os.chmod(t, 0o777)
    try:
        pg_bin = _embrulhar_como_postgres(real, t / "pgbin") if os.geteuid() == 0 else real
        arvore = t / "arvore"
        nomes = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=RAIZ,
                               capture_output=True, check=True).stdout.decode().split("\0")
        for n in filter(None, nomes):
            src = RAIZ / n
            if src.is_file():
                (arvore / n).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, arvore / n)
        livro = arvore / "data" / "collection-ledger" / "italy" / "runs.ndjson"
        linhas = [l for l in livro.read_text(encoding="utf-8").splitlines()
                  if l.strip() and json.loads(l).get("RUN_ID") in CORRIDAS]
        livro.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        (arvore / "curadoria" / "PARAR.flag").unlink(missing_ok=True)
        subprocess.run(["chmod", "-R", "a+rwX", str(t)], check=True)
        env = {k: v for k, v in os.environ.items()
               if k not in ("SINTONIA_COLLECTION_DSN", "SINTONIA_SALA_DSN", "SUPABASE_DB_URL",
                            "BANCO_DESCARTAVEL_URL", "ITALY_OPS_ROOT")}
        env.update({"SINTONIA_PG_BIN": str(pg_bin), "HTTP_PROXY": MORTA, "HTTPS_PROXY": MORTA,
                    "http_proxy": MORTA, "https_proxy": MORTA, "ALL_PROXY": MORTA,
                    "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost",
                    "PYTHONDONTWRITEBYTECODE": "1"})
        r = subprocess.run([sys.executable, str(arvore / AQUI.relative_to(RAIZ)), "--dentro",
                            "--saida=%s" % saida, "--tmp=%s" % t], cwd=arvore, env=env, timeout=3600)
        return r.returncode
    finally:
        shutil.rmtree(t, ignore_errors=True)


def dentro(saida: Path, t: Path) -> int:
    os.umask(0)                                  # o utilizador postgres escreve nas pastas que criamos
    sys.path.insert(0, str(RAIZ))
    sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
    sys.path.insert(0, str(RAIZ / "curadoria"))
    import _gavetas  # noqa: F401
    import ensaio_offline as E
    out = {"QUANDO": datetime.now(timezone.utc).isoformat(), "CORRIDAS_DA_COLETA": list(CORRIDAS),
           "PASSOS": {}}
    base = E.Base(t / "pg-sala")
    try:
        r = base.subir(RAIZ, dict(os.environ, PATH=str(E.PG_BIN) + os.pathsep + os.environ["PATH"]))
        out["PASSOS"]["0_MIGRATIONS"] = {"CODIGO": r["CODIGO"], "PASS": r["MIGRATIONS_PASS"]}
        if r["CODIGO"] != 0:
            out["ESTADO"], out["ERRO"] = "FAIL", r["ERRO"] or r["SAIDA"]
            return 1
        armazem = t / "armazem"
        armazem.mkdir()
        os.environ.update({"SINTONIA_COLLECTION_DSN": base.url, "SINTONIA_SALA_DSN": base.url,
                           "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_PSQL_EXE": base.exe("psql"),
                           "SINTONIA_ARMAZEM_RAIZ": str(armazem)})
        import passagem_para_a_sala as PAS
        import gatilho_da_inteligencia as GI
        import vigia_da_esteira as VIG
        import sala_de_espera as espera
        foto = lambda: {k: v["LINHAS"] for k, v in E.fotografia().items()}    # noqa: E731
        estado = {"PAS_DESDE": "2026-09-21T00:00:00+00:00"}
        out["PASSOS"]["1_ARMAZEM_E_SALA_ANTES"] = foto()

        # 2 · A PASSAGEM (primeiro com a trava presa por outro escritor: tem de recusar)
        with espera._Trava(str(PAS.TRINCO)):
            out["PASSOS"]["2a_PASSAGEM_COM_OUTRO_ESCRITOR"] = PAS.passar_se_devido(estado, forcar=True)["ACCAO"]
        PAS.GUARDAR_BACKUPS = 1

        def porta_com_a_sala_morta(cmd):
            viva = os.environ["SINTONIA_SALA_DSN"]
            os.environ["SINTONIA_SALA_DSN"] = "postgresql://postgres@127.0.0.1:9/sala_morta?connect_timeout=2"
            try:
                return PAS.lancar_padrao(cmd)
            finally:
                os.environ["SINTONIA_SALA_DSN"] = viva
        t0 = datetime.now(timezone.utc)
        f = PAS.passar_se_devido(estado, agora=t0, forcar=True, lancar=porta_com_a_sala_morta)
        pasta_da_falha = PAS.PASTA / t0.strftime("%Y%m%dT%H%M%SZ")
        out["PASSOS"]["2a2_PORTA_COM_A_SALA_MORTA"] = {
            "ACCAO": f["ACCAO"], "FALHARAM": f.get("FALHARAM"),
            "CODIGOS": {c.get("COLHEITA_DA_CORRIDA"): c.get("CODIGO") for c in f.get("CORRIDAS", [])},
            "EM_PAS_PASSAGENS": sorted(estado.get("PAS_PASSAGENS") or {}),
            "PAS_FALHAS": {k: {"TENTATIVAS": v["TENTATIVAS"], "CAUSA": v["CAUSA"][-160:]}
                           for k, v in (estado.get("PAS_FALHAS") or {}).items()},
            "PAS_ULTIMA_FALHA_EM": estado.get("PAS_ULTIMA_FALHA_EM"),
            "SALA": foto()["sala_de_espera"]}
        out["PASSOS"]["2a3_LOGO_A_SEGUIR_RECUO"] = PAS.passar_se_devido(
            estado, agora=t0 + timedelta(minutes=6))["ACCAO"]
        t1 = t0 + PAS.RECUO + timedelta(minutes=1)
        p = PAS.passar_se_devido(estado, agora=t1, forcar=True)
        pasta_em_curso = PAS.PASTA / t1.strftime("%Y%m%dT%H%M%SZ")
        out["PASSOS"]["2b_PASSAGEM"] = {"ACCAO": p["ACCAO"], "BACKUP_PROVA_VALE": bool(p.get("BACKUP")),
                                        "PLANO": estado.get("PAS_ULTIMO_PLANO"),
                                        "CORRIDAS": [{k: c.get(k) for k in ("COLHEITA_DA_CORRIDA", "FONTE",
                                                                             "UNIVERSO", "OBSERVACOES", "STATUS",
                                                                             "CORRIDA_DA_PORTA", "POR_RESULTADO",
                                                                             "CODIGO", "ERRO")}
                                                     for c in p.get("CORRIDAS", [])]}
        depois = foto()
        out["PASSOS"]["2c_ARMAZEM_E_SALA_DEPOIS"] = depois
        out["PASSOS"]["2d_DE_NOVO_NAO_REPETE"] = PAS.passar_se_devido(estado, agora=t1, forcar=True)["ACCAO"]

        def bytes_de(x: Path) -> int:
            return sum(q.stat().st_size for q in x.rglob("*") if q.is_file()) if x.exists() else 0
        out["PASSOS"]["2e_RETENCAO"] = {
            "PODA": estado.get("PAS_ULTIMA_PODA"),
            "FALHA_PG_EXISTE": (pasta_da_falha / "backup" / "pg").exists(),
            "FALHA_DUMP_EXISTE": (pasta_da_falha / "backup" / "SALA-ANTES-DA-MICRO.dump").exists(),
            "FALHA_RECIBO_EXISTE": (pasta_da_falha / "backup" / "PROVA-BACKUP-SALA.json").exists(),
            "EM_CURSO_DUMP_EXISTE": (pasta_em_curso / "backup" / "SALA-ANTES-DA-MICRO.dump").exists(),
            "EM_CURSO_PG_EXISTE": (pasta_em_curso / "backup" / "pg").exists(),
            "BYTES_EM_CURSO": bytes_de(pasta_em_curso), "BYTES_DA_FALHA_DEPOIS": bytes_de(pasta_da_falha)}

        # 3 · A INTELLIGENCE: agora (espera ou corre, pela regra) e agora + 4 h
        agora = datetime.now(timezone.utc)
        r0 = GI.correr_se_devido(estado, agora=agora, forcar_medida=True)
        out["PASSOS"]["3a_GATILHO_AGORA"] = {k: r0.get(k) for k in ("ACCAO", "DECISAO", "PORQUE", "NOVOS")}
        with espera._Trava(str(GI.TRINCO)):
            r1 = GI.correr_se_devido(dict(estado), agora=agora + timedelta(hours=4), forcar_medida=True)
        out["PASSOS"]["3b_DUAS_CORRIDAS_SOBREPOSTAS"] = r1["ACCAO"]
        if r0.get("ACCAO", "").startswith("POTE_") or r0.get("ACCAO") in ("MOTOR_ERRO", "COPIA_NAO_VALE"):
            r2 = r0
        else:
            r2 = GI.correr_se_devido(estado, agora=agora + timedelta(hours=4), forcar_medida=True)
        out["PASSOS"]["3c_GATILHO_4H"] = {k: r2.get(k) for k in ("ACCAO", "GATILHO", "SUBIU", "PORQUE",
                                                                 "CORRIDA", "VIOLACOES", "PRIMEIRAS")}
        out["PASSOS"]["3d_POTE_NO_CASCO_EXISTE"] = GI.POTE_NO_CASCO.exists()
        out["PASSOS"]["3e_SEM_DELTA_DEPOIS"] = GI.correr_se_devido(
            estado, agora=agora + timedelta(hours=9), forcar_medida=True).get("PORQUE")

        # 4 · O VIGIA
        v = VIG.vigiar_se_devido(estado)
        saude = json.loads(VIG.SAUDE.read_text(encoding="utf-8"))
        out["PASSOS"]["4_VIGIA"] = {"ACCAO": v["ACCAO"], "ALERTA": saude["ALERTA"],
                                    "ETAPAS": {k: (x["ESTADO"], x["ULTIMA_VEZ"]) for k, x in saude["ETAPAS"].items()}}

        P = out["PASSOS"]
        sala_subiu = depois["sala_de_espera"] > P["1_ARMAZEM_E_SALA_ANTES"]["sala_de_espera"]
        pote = P["3c_GATILHO_4H"]
        F, R = P["2a2_PORTA_COM_A_SALA_MORTA"], P["2e_RETENCAO"]
        # A T10 tem SIM -> precisa da Sala -> tem de FALHAR. A T7 so tem NAO/NAO_SEI: a porta decide,
        # escreve o livro e nao pousa nada, logo passa mesmo com a Sala morta — e isso e verdade, nao defeito.
        t10 = CORRIDAS[0]
        falha_certa = (F["ACCAO"] in ("FALHOU", "PASSOU_COM_FALHAS") and t10 in (F["FALHARAM"] or [])
                       and t10 not in F["EM_PAS_PASSAGENS"] and set(F["PAS_FALHAS"]) == set(F["FALHARAM"])
                       and not set(F["FALHARAM"]) & set(F["EM_PAS_PASSAGENS"])
                       and F["PAS_ULTIMA_FALHA_EM"] and F["SALA"] == P["1_ARMAZEM_E_SALA_ANTES"]["sala_de_espera"]
                       and P["2a3_LOGO_A_SEGUIR_RECUO"] == "RECUO_DEPOIS_DE_FALHA"
                       and set(F["FALHARAM"]) <= set(estado.get("PAS_PASSAGENS") or {})
                       and not estado.get("PAS_FALHAS"))
        retencao_certa = (not R["FALHA_PG_EXISTE"] and not R["FALHA_DUMP_EXISTE"] and R["FALHA_RECIBO_EXISTE"]
                          and R["EM_CURSO_DUMP_EXISTE"] and R["EM_CURSO_PG_EXISTE"])
        out["FALHA_DA_PORTA_CERTA"], out["RETENCAO_CERTA"] = bool(falha_certa), bool(retencao_certa)
        ok = (P["2a_PASSAGEM_COM_OUTRO_ESCRITOR"] == "OCUPADO" and p["ACCAO"] == "PASSOU" and sala_subiu
              and falha_certa and retencao_certa
              and P["2d_DE_NOVO_NAO_REPETE"] == "NADA_A_PASSAR"
              and P["3b_DUAS_CORRIDAS_SOBREPOSTAS"] == "OCUPADO"
              and pote.get("ACCAO") in ("POTE_SUBIU", "POTE_NAO_SUBIU")
              # o fiscal manda: subiu <=> existe no casco
              and (pote.get("SUBIU") is True) == P["3d_POTE_NO_CASCO_EXISTE"]
              and P["3e_SEM_DELTA_DEPOIS"] == "SEM_DELTA"
              and P["4_VIGIA"]["ACCAO"] == "ESCREVEU")
        out["ESTADO"] = "PASS" if ok else "FAIL"
        return 0 if ok else 1
    except Exception as e:  # noqa: BLE001
        import traceback
        out["ESTADO"], out["ERRO"] = "FAIL", traceback.format_exc()[-2000:]
        print(out["ERRO"])
        return 1
    finally:
        base.descer()
        saida.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps({"ESTADO": out.get("ESTADO")}, ensure_ascii=False))


if __name__ == "__main__":
    a = sys.argv[1:]
    saida = Path(next((x.split("=", 1)[1] for x in a if x.startswith("--saida=")),
                      next((x for x in a if not x.startswith("--")), SAIDA_PADRAO)))
    if "--dentro" in a:
        raise SystemExit(dentro(saida.resolve(), Path(next(x.split("=", 1)[1] for x in a
                                                           if x.startswith("--tmp=")))))
    raise SystemExit(fora(saida.resolve()))
