#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GATILHO DA INTELLIGENCE (D90-5) — quando a Sala tem READY novo, o motor corre sozinho.

    MISSAO   ESTEIRA-SOZINHA (28/09/2026) · dono 27/09 21:35: «o que falta pro sintonia rodar
             todo sozinho?»
    QUEM CHAMA  o supervisor (`curadoria/supervisor.py::_hook_esteira`), a cada volta. Nao ha
             segundo orquestrador: isto e um passo do servico que ja existe.

    python3 admissao/gatilho_da_inteligencia.py --medir      # so mede o delta e diz o que faria

A REGRA, E ELA E ESTA E MAIS NENHUMA
------------------------------------
    CORRE quando   10 READY novos                          (LIMIAR_NOVOS)
              OU   >= 1 READY novo que ja espera ha 4 h    (ESPERA_MAXIMA)
    «novo»       = pousado na Sala (`sala_de_espera.pousado_em`) DEPOIS da ultima tentativa.
    ⚠️ O texto de D90-5 nao esta no repositorio. «+ 4 h» foi lido como «o READY novo mais velho
       ja espera 4 h» (um READY sozinho nunca fica parado mais de 4 h). Se D90-5 quiser «4 h desde
       a ultima corrida», muda-se `decidir()` e so ela. NAO SEI ate o dono confirmar.

O QUE ELE CHAMA — O MOTOR QUE JA EXISTE, NAO OUTRO
--------------------------------------------------
    1 copia    `scripts/micro_coleta/provar_backup_da_sala.provar`: o backup da Sala, reposto num
               Postgres descartavel e conferido (PROVA_VALE). A Intelligence le DA COPIA, nunca da
               Sala (RUNBOOK-R7 §1) — e a copia so existe se o backup provou que volta.
    2 export   `motor/r7_export_da_copia.sql`, exactamente como o RUNBOOK-R7 §2 manda: psql,
               PGOPTIONS=default_transaction_read_only, `begin transaction read only`. READ_ONLY
               tem de voltar `on`, senao o export nao serve.
    3 motor    `motor/motor_das_capacidades.rodar` (G0/v4 + CAP-WIN + CAP-SCI).
    4 pote     `pacote/pote_intelligence_casco.ler_entrada` -> candidato ao lado do destino.
    5 fiscal   `pacote/validar_pote_v2.validar` sobre o FICHEIRO candidato (forma + lei).
               REPROVADO -> nao sobe: o candidato vai para a pasta da esteira, com as violacoes.
               PASSA -> `os.replace` para `italia-portale/client/sintonia-pote.js` (atomico).

    UM POTE QUE O FISCAL REPROVA NAO SOBE. NEM «SO DESTA VEZ».

AS TRAVAS
---------
    TRINCO     `sala_de_espera._Trava` (flock/msvcrt, o mesmo dono da trava da Sala): morre com o
               processo, entao nunca fica preso. Segunda corrida ao mesmo tempo -> OCUPADO.
    PARAR      `curadoria/PARAR.flag` antes de medir e antes de subir.
    RECUO      falhou (copia nao vale, motor rebentou)? nao se tenta outra vez antes de RECUO.
    MEDIDA     a Sala e perguntada no maximo de INTERVALO_DE_MEDIDA em INTERVALO_DE_MEDIDA.
    RETENCAO   (FECHO, 28/09) cada corrida deixa ~50 MB (backup, Postgres descartavel, export da
               copia). `provar_backup_da_sala.podar` corre DEPOIS da corrida, dentro do trinco:
               ficam as GUARDAR_BACKUPS ultimas e a ultima com PROVA_VALE; a em curso nunca sai.

O POTE DE HOJE NAO SOBE, E ISSO NAO SE MUDA AQUI
------------------------------------------------
    O motor escreve ENTITY_SOURCE como OBJETO (D112) e o contrato POTE_INTELLIGENCE_CASCO-v2 pede
    STRING. O fiscal reprova e o gatilho obedece: POTE_REPROVADO, nada sobe. Quem decide o contrato
    e o dono do pote (pedido ja feito); nem o motor nem o schema se tocam na esteira.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import sala_de_espera as espera                  # noqa: E402 — dono da trava
import motor_das_capacidades as M                # noqa: E402 — o motor que ja existe
import pote_intelligence_casco as P              # noqa: E402 — o gerador do pote
import validar_pote_v2 as VP                     # noqa: E402 — o fiscal do pote

LIMIAR_NOVOS = 10
ESPERA_MAXIMA = timedelta(hours=4)
RECUO = timedelta(minutes=30)
INTERVALO_DE_MEDIDA = timedelta(minutes=5)
GUARDAR_BACKUPS = 3

CURADORIA = RAIZ / "curadoria"
PARAR = CURADORIA / "PARAR.flag"
TRINCO = CURADORIA / "ESTEIRA-INTELLIGENCE"          # a trava e TRINCO + ".lock"
PASTA = CURADORIA / "esteira" / "intelligence"       # runtime, fora do Git (curadoria/.gitignore)
POTE_NO_CASCO = RAIZ / "italia-portale" / "client" / "sintonia-pote.js"
SQL_EXPORT = RAIZ / "motor" / "r7_export_da_copia.sql"
PGOPTIONS_SO_LEITURA = "-c default_transaction_read_only=on -c standard_conforming_strings=on"

CORRER, ESPERAR, NAO_SEI = "CORRER", "ESPERAR", "NAO SEI"


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _quando(v) -> datetime | None:
    """ISO do Python ou timestamptz do psql («2026-09-28 10:00:00.1+00») -> datetime aware."""
    if not v:
        return None
    s = str(v).strip().replace(" ", "T", 1)
    if len(s) >= 3 and s[-3] in "+-" and s[-3:].lstrip("+-").isdigit():
        s += ":00"
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


# ── 1 · o delta, so SELECT ───────────────────────────────────────────────────
def _consulta_padrao(sql: str) -> list:
    """O cliente so-leitura que a coleta ja usa (duas travas: a nossa e a do banco)."""
    sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
    import micro_coleta as MC                                   # noqa: PLC0415
    return MC.sql(sql)


def medir_delta(consulta, marca: str | None) -> dict:
    """Quantos READY pousaram na Sala depois da `marca`, e ha quanto tempo o mais velho espera."""
    onde = ""
    if marca is not None:
        m = _quando(marca)
        if m is None:
            raise ValueError("marca ilegivel: %r" % (marca,))
        onde = " where pousado_em > '%s'::timestamptz" % m.isoformat()
    linhas = consulta("select count(*), min(pousado_em), max(pousado_em) from sala_de_espera" + onde)
    n, mais_velho, mais_novo = (linhas[0] + [None, None, None])[:3] if linhas else (None, None, None)
    return {"NOVOS": int(n) if n not in (None, "") else None,
            "MAIS_VELHO_EM": _quando(mais_velho).isoformat() if _quando(mais_velho) else None,
            "MAIS_NOVO_EM": _quando(mais_novo).isoformat() if _quando(mais_novo) else None,
            "DESDE": marca}


def decidir(delta: dict, agora: datetime, estado: dict | None = None) -> dict:
    """A regra de D90-5, pura. -> {"DECISAO": CORRER|ESPERAR|NAO SEI, "PORQUE": ...}"""
    estado = estado or {}
    n = delta.get("NOVOS")
    if n is None:
        return {"DECISAO": NAO_SEI, "PORQUE": "o delta da Sala nao foi medido"}
    falhou = _quando(estado.get("INT_ULTIMA_FALHA_EM"))
    if falhou and agora - falhou < RECUO:
        return {"DECISAO": ESPERAR, "PORQUE": "RECUO_DEPOIS_DE_FALHA",
                "ABRE_EM": (falhou + RECUO).isoformat()}
    if n <= 0:
        return {"DECISAO": ESPERAR, "PORQUE": "SEM_DELTA"}
    if n >= LIMIAR_NOVOS:
        return {"DECISAO": CORRER, "PORQUE": "DEZ_OU_MAIS_NOVOS (%d)" % n}
    velho = _quando(delta.get("MAIS_VELHO_EM"))
    if velho is None:
        return {"DECISAO": NAO_SEI, "PORQUE": "%d novos sem hora de pouso legivel" % n}
    if agora - velho >= ESPERA_MAXIMA:
        return {"DECISAO": CORRER, "PORQUE": "NOVO_A_ESPERA_HA_4H (%d novos)" % n}
    return {"DECISAO": ESPERAR, "PORQUE": "POUCOS_E_RECENTES (%d novos)" % n,
            "ABRE_EM": (velho + ESPERA_MAXIMA).isoformat()}


# ── 2 · a copia provada e o export, como o RUNBOOK-R7 manda ──────────────────
def _psql() -> str:
    from guarda.cliente_postgres import resolver_psql       # noqa: PLC0415
    return resolver_psql()


def exportar(url: str, destino: Path, psql: str | None = None) -> dict:
    """RUNBOOK-R7 §2, byte a byte: opcoes primeiro, DSN por ultimo, `-o` e nao `>`."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PGOPTIONS=PGOPTIONS_SO_LEITURA, PGCLIENTENCODING="UTF8")
    r = subprocess.run([psql or _psql(), "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                        "-c", "begin transaction read only", "-f", str(SQL_EXPORT), "-c", "commit",
                        "-o", str(destino), url],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode != 0:
        raise RuntimeError("export falhou: %s" % r.stderr.strip()[-300:])
    exp = json.loads(destino.read_text(encoding="utf-8"))
    if exp.get("READ_ONLY") != "on":
        # O proprio banco diz se a transacao era so de leitura. Se nao era, o export nao serve.
        raise RuntimeError("export sem READ_ONLY=on: %r" % exp.get("READ_ONLY"))
    return exp


def copia_provada(pasta: Path) -> dict | None:
    """Backup da Sala -> copia descartavel (PROVA_VALE) -> export read-only DA COPIA."""
    sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
    import provar_backup_da_sala as PB                          # noqa: PLC0415
    dsn = os.environ.get("SINTONIA_SALA_DSN")
    if not dsn:
        raise RuntimeError("SINTONIA_SALA_DSN ausente: sem Sala nao ha copia")
    r = PB.provar(dsn, pasta / "backup", ler_real_do_ficheiro=False,
                  com_a_copia=lambda url: exportar(url, pasta / "EXPORT-DA-COPIA.json"))
    return r.get("COM_A_COPIA") if r.get("PROVA_VALE") else None


def _cabeca() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True,
                              text=True, timeout=10).stdout.strip() or NAO_SEI
    except (OSError, subprocess.SubprocessError):
        return NAO_SEI


def correr_o_motor(export: dict, hoje: date, source_head: str) -> dict:
    return M.rodar(M.entrada_do_export(export), hoje, source_head)


# ── 3 · o pote: candidato, fiscal, e so entao sobe ───────────────────────────
def subir_o_pote(saida_motor: dict, destino: Path = POTE_NO_CASCO, pasta: Path = PASTA,
                 parar: Path = PARAR) -> dict:
    pote = P.ler_entrada(saida_motor)
    run = pote.get("INTELLIGENCE_RUN_ID", NAO_SEI)
    destino.parent.mkdir(parents=True, exist_ok=True)
    candidato = destino.parent / ".sintonia-pote.candidato.js"
    candidato.write_text(P.como_js(pote), encoding="utf-8")
    # O fiscal le o FICHEIRO que vai subir, e nao o dicionario em memoria: o que se confere e o
    # que se publica, byte a byte.
    violacoes = VP.validar(VP.ler_ficheiro(candidato))
    if violacoes:
        pasta.mkdir(parents=True, exist_ok=True)
        guardado = pasta / ("POTE-REPROVADO-%s.js" % run)
        os.replace(candidato, guardado)
        return {"SUBIU": False, "PORQUE": "POTE_REPROVADO", "CORRIDA": run,
                "VIOLACOES": len(violacoes), "PRIMEIRAS": violacoes[:10], "GUARDADO_EM": str(guardado)}
    if parar.exists():
        candidato.unlink(missing_ok=True)
        return {"SUBIU": False, "PORQUE": "PARAR_FLAG_ANTES_DE_SUBIR", "CORRIDA": run}
    os.replace(candidato, destino)
    return {"SUBIU": True, "CORRIDA": run, "DESTINO": str(destino)}


# ── 4 · uma volta ────────────────────────────────────────────────────────────
def correr_se_devido(estado: dict, *, agora: datetime | None = None, consulta=None, copia=None,
                     motor=None, subir=None, parar: Path = PARAR, trinco: Path = TRINCO,
                     pasta: Path = PASTA, forcar_medida: bool = False, podar=None) -> dict:
    """Uma volta do gatilho. Devolve o que fez; guarda em `estado` as marcas (INT_*)."""
    agora = agora or _agora()
    if parar.exists():
        return {"ACCAO": "PARAR_FLAG"}
    medido = _quando(estado.get("INT_MEDIDO_EM"))
    if not forcar_medida and medido and agora - medido < INTERVALO_DE_MEDIDA:
        return {"ACCAO": "NADA"}
    estado["INT_MEDIDO_EM"] = agora.isoformat()
    try:
        delta = medir_delta(consulta or _consulta_padrao, estado.get("INT_MARCA"))
    except Exception as e:  # noqa: BLE001 — nao medir e NAO SEI, nunca «zero»
        return {"ACCAO": "NAO_SEI", "PORQUE": "delta nao medido: %s" % repr(e)[:200]}
    d = decidir(delta, agora, estado)
    estado["INT_ULTIMO_DELTA"] = dict(delta, **d)
    if d["DECISAO"] != CORRER:
        return {"ACCAO": "ESPERA" if d["DECISAO"] == ESPERAR else "NAO_SEI", **delta, **d}
    try:
        with espera._Trava(str(trinco)):
            pasta_corrida = pasta / agora.strftime("%Y%m%dT%H%M%SZ")
            try:
                return _correr(estado, agora, delta, d, copia, motor, subir, parar, pasta_corrida)
            finally:
                # Dentro do trinco e DEPOIS da corrida: a corrida em curso nunca e podada.
                try:
                    estado["INT_ULTIMA_PODA"] = (podar or podar_padrao)(pasta, pasta_corrida)
                except Exception as e:  # noqa: BLE001 — a poda nao desfaz a corrida; fica escrita
                    estado["INT_ULTIMA_PODA"] = {"ERRO": repr(e)[:300]}
    except espera.EsperaOcupada:
        return {"ACCAO": "OCUPADO", "PORQUE": "outra corrida da Intelligence esta a decorrer"}


def podar_padrao(pasta: Path, em_curso: Path) -> dict:
    sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
    import provar_backup_da_sala as PB                          # noqa: PLC0415
    return PB.podar(pasta, em_curso, guardar=GUARDAR_BACKUPS)


def _correr(estado, agora, delta, d, copia, motor, subir, parar, pasta_corrida) -> dict:
    estado["INT_ULTIMA_TENTATIVA_EM"] = agora.isoformat()
    try:
        export = (copia or copia_provada)(pasta_corrida)
        if export is None:
            estado["INT_ULTIMA_FALHA_EM"] = agora.isoformat()
            return {"ACCAO": "COPIA_NAO_VALE", "PORQUE": "backup sem PROVA_VALE: a Intelligence nao le a Sala"}
        saida = (motor or correr_o_motor)(export, agora.date(), _cabeca())
    except Exception as e:  # noqa: BLE001 — ERROR != REJEITADO: os READY ficam onde estao
        estado["INT_ULTIMA_FALHA_EM"] = agora.isoformat()
        return {"ACCAO": "MOTOR_ERRO", "PORQUE": repr(e)[:300]}
    pasta_corrida.mkdir(parents=True, exist_ok=True)
    (pasta_corrida / "MOTOR.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n",
                                              encoding="utf-8")
    # O motor correu sobre estes READY: a marca anda, suba o pote ou nao. Um pote reprovado nao
    # melhora a correr outra vez sobre a mesma Sala; o que o muda e READY novo ou codigo novo.
    estado["INT_MARCA"] = delta.get("MAIS_NOVO_EM") or estado.get("INT_MARCA")
    estado["INT_ULTIMA_CORRIDA_EM"] = agora.isoformat()
    estado["INT_ULTIMA_CORRIDA_ID"] = saida.get("INTELLIGENCE_RUN_ID")
    if parar.exists():
        return {"ACCAO": "PARAR_FLAG_ANTES_DO_POTE", "CORRIDA": saida.get("INTELLIGENCE_RUN_ID")}
    try:
        pote = (subir or subir_o_pote)(saida, pasta=pasta_corrida, parar=parar)
    except Exception as e:  # noqa: BLE001 — um gerador que rebenta tambem nao sobe
        pote = {"SUBIU": False, "PORQUE": "POTE_ERRO", "ERRO": repr(e)[:300]}
    estado["INT_ULTIMO_POTE"] = {k: pote.get(k) for k in ("SUBIU", "PORQUE", "CORRIDA", "VIOLACOES")}
    if pote.get("SUBIU"):
        estado["INT_ULTIMA_SUBIDA_EM"] = agora.isoformat()
        return {"ACCAO": "POTE_SUBIU", "GATILHO": d["PORQUE"], **pote}
    return {"ACCAO": "POTE_NAO_SUBIU", "GATILHO": d["PORQUE"], **pote}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--medir" not in argv:
        print(__doc__.strip().split("\n\n")[0])
        print("\n  uso: python3 admissao/gatilho_da_inteligencia.py --medir   (so SELECT; nao corre o motor)")
        return 2
    delta = medir_delta(_consulta_padrao, next((a.split("=", 1)[1] for a in argv
                                                if a.startswith("--desde=")), None))
    print(json.dumps(dict(delta, **decidir(delta, _agora())), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
