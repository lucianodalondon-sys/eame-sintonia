#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GATILHO DA INTELLIGENCE (D90-5) — quando a Sala tem READY novo, o motor corre sozinho.

    MISSAO   ESTEIRA-SOZINHA (28/09/2026) · dono 27/09 21:35: «o que falta pro sintonia rodar
             todo sozinho?»
             L2-DISPARADOR-INTELLIGENCE (D140, 28/09): portado SELETIVAMENTE para cima da producao
             fd8c94698 — so este gatilho, o vigia e a retencao. A passagem armazem -> Sala ficou de
             fora (ESCREVE na Sala; a coleta continua da producao ja leva cada corrida pela porta).
    QUEM CHAMA  o Agendador de Tarefas, por um .cmd que le SALA_DSN.txt no arranque do processo
             (o mesmo metodo do `coleta_continua.cmd`; sem setx). Uma volta por chamada:

    python3 admissao/gatilho_da_inteligencia.py --medir      # so mede o delta e diz o que faria
    python3 admissao/gatilho_da_inteligencia.py --uma-volta  # uma volta: mede, e se for devido, corre

SO LE A SALA (D140) — E NUNCA MARCA consumido_em
------------------------------------------------
    A Sala e perguntada so com SELECT (`micro_coleta.sql`, duas travas) e copiada por pg_dump. Todo
    o resto corre sobre a COPIA descartavel. Este ficheiro nao chama `pousar`, `rever` nem `retirar`
    (os escritores de `sala_de_espera`) e nao escreve `consumido_em`: retirar da fila e outra
    decisao (D140), e nao se mistura com esta.

O CORTE VIGENTE — ITEM_ID REPETIDO NA SALA (defeito medido, e declarado, nao escondido)
--------------------------------------------------------------------------------------
    A vista `sala_de_espera_atual` tem uma linha por (run_id, ordem). O mesmo ITEM_ID pode pousar
    em duas corridas (medido na Sala real: derived:6/56/57/60/62/66, duas linhas cada), e o motor
    recusa o corte inteiro com «ITEM_ID repetido no corte». `cortar_vigente` leva ao motor UMA linha
    por ITEM_ID — a de `pousado_em` mais recente (desempate: run_id, ordem) — e declara as outras
    em CORTE-VIGENTE.json, em INT_ULTIMO_CORTE e no vigia. ITEM_ID sem identidade («?», vazio,
    NAO SEI) nao e endereco (migration 031): sai do corte e e declarado. Hora de pouso ilegivel num
    repetido -> nenhuma das linhas dele entra (NAO SEI qual e a vigente). Nada disto muda a Sala.

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
    4 pote     `montar_o_pote`: `pacote/pote_intelligence_casco.ler_entrada` e a conversao explicita
               do ENTITY_SOURCE (valor da lei COL-LAW-221, senao UNKNOWN; o mapa do motor nunca se
               achata nem se escolhe uma entrada) -> candidato na pasta da corrida.
    5 fiscal   `pacote/validar_pote_v2.validar` sobre o FICHEIRO candidato (forma + lei).
               REPROVADO -> nao sobe: fica POTE-REPROVADO-<RUN>.json na pasta da corrida.
               PASSA -> a entrega `curadoria/esteira/intelligence/PARA-O-CASCO/` (POTE.json +
               MANIFESTO.json + SHA256SUMS.txt, a pasta troca-se inteira). E A FRONTEIRA: o
               disparador PARA na entrega. Quem a le e publica na tela e o casco (casco-owner);
               este ficheiro nunca escreve sob a arvore do portal (correcao do coordenador, 28/09).
               Formato e lugar: provas/l2/PARA-O-CASCO.md.
    «cruzamentos»  sao os que ESTE motor produz (D112 RELACOES, janelas CAP-WIN x estudos CAP-SCI).
               `pacote/pote_cruzamentos_max.py` NAO entra: le docs/intelligence/r7/ANALISE-R7.json
               (um estudo fixo com CROSSINGS), e o motor de hoje nao escreve CROSSINGS. Ligar isso e
               motor novo — decisao do dono, nao desta missao.

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
    O motor escreve ENTITY_SOURCE como MAPA (D112) e o contrato POTE_INTELLIGENCE_CASCO-v2 pede
    STRING. A decisao do Intelligence owner (28/09) e aplicada em `montar_o_pote`: mapa -> UNKNOWN,
    salvo valor da lei COL-LAW-221. Medido: todo objeto do motor traz o mapa, logo todos viram
    UNKNOWN — e o fiscal le UNKNOWN como «ENTITY_SOURCE esconde a ignorancia» (so «NAO SEI» e a
    ignorancia escrita). O pote continua REPROVADO e nada vai para a entrega. Nem o motor, nem o
    schema, nem o fiscal se tocam aqui: isso e do dono do pote.
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
from afirmacao_da_fonte import ENTITY_SOURCES as LEI_221   # noqa: E402 — COL-LAW-221 (dono: leis/)

LIMIAR_NOVOS = 10
ESPERA_MAXIMA = timedelta(hours=4)
RECUO = timedelta(minutes=30)
INTERVALO_DE_MEDIDA = timedelta(minutes=5)
GUARDAR_BACKUPS = 3

CURADORIA = RAIZ / "curadoria"
PARAR = CURADORIA / "PARAR.flag"
TRINCO = CURADORIA / "ESTEIRA-INTELLIGENCE"          # a trava e TRINCO + ".lock"
TRINCO_DA_VOLTA = CURADORIA / "ESTEIRA-INTELLIGENCE-VOLTA"   # --uma-volta: ler/gravar o estado a uma mao
ESTADO = CURADORIA / "ESTEIRA-INTELLIGENCE-ESTADO.json"      # runtime (curadoria/.gitignore)
PASTA = CURADORIA / "esteira" / "intelligence"       # runtime, fora do Git (curadoria/.gitignore)
ENTREGA = PASTA / "PARA-O-CASCO"                     # POTE.json + MANIFESTO.json + SHA256SUMS.txt
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


SQL_POUSOS = "select run_id, ordem, item_id, pousado_em from sala_de_espera_atual order by run_id, ordem"


def ler_pousos(url: str, psql: str | None = None) -> list:
    """A hora de pouso de cada linha DA COPIA — so SELECT, na mesma sessao so-leitura do export.

    O export do motor (`r7_export_da_copia.sql`, dono: o motor) nao traz `pousado_em`, e o SQL do
    motor nao se muda aqui. Sem esta hora nao ha como dizer qual das linhas repetidas e a vigente."""
    env = dict(os.environ, PGOPTIONS=PGOPTIONS_SO_LEITURA, PGCLIENTENCODING="UTF8")
    r = subprocess.run([psql or _psql(), "-X", "-q", "-A", "-t", "-F", "\t", "-v", "ON_ERROR_STOP=1",
                        "-c", SQL_POUSOS, url],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode != 0:
        raise RuntimeError("pousos da copia nao lidos: %s" % r.stderr.strip()[-300:])
    out = []
    for l in r.stdout.splitlines():
        c = l.rstrip("\r").split("\t")
        if len(c) == 4:
            out.append({"run_id": c[0], "ordem": int(c[1]), "item_id": c[2], "pousado_em": c[3] or None})
    return out


def copia_provada(pasta: Path) -> dict | None:
    """Backup da Sala -> copia descartavel (PROVA_VALE) -> export read-only DA COPIA.

    O export volta com POUSOS_DA_COPIA ao lado (a hora de pouso de cada linha), para o corte vigente."""
    sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
    import provar_backup_da_sala as PB                          # noqa: PLC0415
    dsn = os.environ.get("SINTONIA_SALA_DSN")
    if not dsn:
        raise RuntimeError("SINTONIA_SALA_DSN ausente: sem Sala nao ha copia")

    def com_a_copia(url):
        return dict(exportar(url, pasta / "EXPORT-DA-COPIA.json"), POUSOS_DA_COPIA=ler_pousos(url))
    r = PB.provar(dsn, pasta / "backup", ler_real_do_ficheiro=False, com_a_copia=com_a_copia)
    return r.get("COM_A_COPIA") if r.get("PROVA_VALE") else None


SEM_IDENTIDADE = (None, "", "?", NAO_SEI)


def cortar_vigente(export: dict) -> tuple[dict, dict]:
    """UMA linha por ITEM_ID para o motor, e a declaracao do que ficou de fora. -> (export, corte)

    Regra (declarada, e so esta): fica a linha de `pousado_em` mais recente; empate -> maior
    (run_id, ordem). ITEM_ID sem identidade sai. Hora ilegivel num repetido -> sai o grupo inteiro.
    Sem POUSOS_DA_COPIA e com repetidos -> nada se escolhe: o grupo inteiro sai (NAO SEI)."""
    linhas = [l for l in export.get("LINHAS") or [] if isinstance(l, dict)]
    pouso = {(str(p["run_id"]), int(p["ordem"])): p.get("pousado_em")
             for p in export.get("POUSOS_DA_COPIA") or []}
    grupos: dict = {}
    sem_id = []
    for l in linhas:
        iid = l.get("item_id")
        if iid in SEM_IDENTIDADE:
            sem_id.append({"RUN_ID": l.get("run_id"), "ORDEM": l.get("ordem"), "ITEM_ID": iid})
            continue
        grupos.setdefault(str(iid), []).append(l)
    ficam, repetidos, nao_sei = [], {}, {}

    def chave(l):
        return (_quando(pouso.get((str(l.get("run_id")), int(l.get("ordem") or 0)))),
                str(l.get("run_id")), int(l.get("ordem") or 0))

    for iid, g in grupos.items():
        if len(g) == 1:
            ficam.append(g[0])
            continue
        linha = [{"RUN_ID": l.get("run_id"), "ORDEM": l.get("ordem"),
                  "POUSADO_EM": pouso.get((str(l.get("run_id")), int(l.get("ordem") or 0)))} for l in g]
        if any(chave(l)[0] is None for l in g):
            nao_sei[iid] = linha
            continue
        vig = max(g, key=chave)
        ficam.append(vig)
        repetidos[iid] = {"FICA": {"RUN_ID": vig.get("run_id"), "ORDEM": vig.get("ordem"),
                                   "POUSADO_EM": pouso.get((str(vig.get("run_id")), int(vig.get("ordem"))))},
                          "FORA": [x for x, l in zip(linha, g) if l is not vig]}
    ficam.sort(key=lambda l: (str(l.get("run_id")), int(l.get("ordem") or 0)))
    corte = {"LINHAS_NO_EXPORT": len(linhas), "LINHAS_NO_CORTE": len(ficam),
             "ITEM_ID_REPETIDO": repetidos, "REPETIDO_SEM_HORA_LEGIVEL": nao_sei,
             "ITEM_ID_SEM_IDENTIDADE": sem_id,
             "DEFEITO_NA_SALA": bool(repetidos or nao_sei or sem_id),
             "REGRA": "uma linha por ITEM_ID: a de pousado_em mais recente (desempate run_id, ordem); "
                      "sem identidade ou sem hora legivel -> fora. Declarado; a Sala nao muda."}
    limpo = {k: v for k, v in export.items() if k != "POUSOS_DA_COPIA"}
    limpo["LINHAS"] = ficam
    return limpo, corte


def _cabeca() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True,
                              text=True, timeout=10).stdout.strip() or NAO_SEI
    except (OSError, subprocess.SubprocessError):
        return NAO_SEI


def correr_o_motor(export: dict, hoje: date, source_head: str) -> dict:
    return M.rodar(M.entrada_do_export(export), hoje, source_head)


# ── 3 · o pote: montar, candidato, fiscal, e so entao a entrega ─────────────
def _sha256(p: Path) -> str:
    import hashlib                                              # noqa: PLC0415
    return hashlib.sha256(p.read_bytes()).hexdigest()


def entity_source_da_lei(v) -> str:
    """ENTITY_SOURCE no pote (decisao do Intelligence owner, 28/09): o valor da lei COL-LAW-221 quando
    o bloco o tiver; senao UNKNOWN. O MAPA do motor (D112: {chave: {VALOR, ENTITY_SOURCE, POR_ITEM}})
    NAO se achata em texto e NAO se escolhe uma entrada dele: vira UNKNOWN. O mapa continua inteiro
    em MOTOR.json, na pasta da corrida. Um texto fora do vocabulario da lei tambem vira UNKNOWN."""
    return v if isinstance(v, str) and v in LEI_221 else "UNKNOWN"


def montar_o_pote(saida_motor: dict) -> tuple[dict, int]:
    """O PONTO DE MONTAGEM do pote do disparador: o gerador do dono (`ler_entrada`) e, depois dele,
    a conversao explicita do ENTITY_SOURCE de cada objeto. -> (pote, quantos objetos convertidos).

    ⚠️ So aqui, e nao no gerador partilhado: la, o acervo ja escreve ENTITY_SOURCE achatado em texto
    e ha teste que o exige (tests/test_acervo_na_intelligence.py::test_B11); mudar o gerador para
    todos e decisao do dono do pote. O fiscal (validar_pote_v2) NAO muda: hoje ele reprova
    «ENTITY_SOURCE esconde a ignorancia» porque le UNKNOWN como ignorancia fora de «NAO SEI»
    (pacote/pote_intelligence_casco.py::conferir_pote) — e isso fica escrito, nao contornado."""
    pote = json.loads(json.dumps(P.ler_entrada(saida_motor), ensure_ascii=False))
    n = 0
    for e in (pote.get("COMPARTIMENTOS") or {}).values():
        for o in e.get("OBJETOS") or []:
            if "ENTITY_SOURCE" in o:
                novo = entity_source_da_lei(o["ENTITY_SOURCE"])
                n += novo != o["ENTITY_SOURCE"]
                o["ENTITY_SOURCE"] = novo
    return pote, n


def entregar(candidato: Path, pote: dict, entrega: Path, corte: dict | None = None) -> dict:
    """A entrega (provas/l2/PARA-O-CASCO.md): POTE.json + MANIFESTO.json + SHA256SUMS.txt. E A
    FRONTEIRA DA INTELLIGENCE: o disparador para aqui. Quem le a entrega e publica na tela e o casco
    (casco-owner); este ficheiro nunca escreve sob a arvore do portal.

    So se chama com um pote que o fiscal APROVOU; POTE.json sao os bytes do candidato que o fiscal
    leu. A pasta nasce ao lado e troca-se inteira: nunca ha meia entrega."""
    import shutil                                               # noqa: PLC0415
    nova = entrega.with_name(entrega.name + ".nova")
    shutil.rmtree(nova, ignore_errors=True)
    nova.mkdir(parents=True)
    shutil.copyfile(candidato, nova / "POTE.json")
    manifesto = {
        "INTELLIGENCE_RUN_ID": pote.get("INTELLIGENCE_RUN_ID", NAO_SEI),
        "RESULT_STATE": pote.get("RESULT_STATE", NAO_SEI),
        "CORRIDA_SINTETICA": pote.get("CORRIDA_SINTETICA", NAO_SEI),
        "SOURCE_HEAD": pote.get("SOURCE_HEAD", NAO_SEI),
        "CORTE": pote.get("CORTE", NAO_SEI),
        "GERADO_EM": _agora().isoformat(),
        "GERADO_POR": "admissao/gatilho_da_inteligencia.py (L2-DISPARADOR)",
        "POTE": {"ARQUIVO": "POTE.json", "SHA256_ARQUIVO": _sha256(nova / "POTE.json"),
                 "CONTRATO": pote.get("SCHEMA", NAO_SEI)},
        "VALIDAR_POTE_V2": "PASSA",
        "CORTE_VIGENTE": {k: (corte or {}).get(k, NAO_SEI)
                          for k in ("LINHAS_NO_EXPORT", "LINHAS_NO_CORTE", "DEFEITO_NA_SALA")},
    }
    (nova / "MANIFESTO.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=1) + "\n",
                                         encoding="utf-8")
    (nova / "SHA256SUMS.txt").write_text("".join("%s *%s\n" % (_sha256(nova / n), n)
                                                 for n in ("POTE.json", "MANIFESTO.json")), encoding="utf-8")
    velha = entrega.with_name(entrega.name + ".velha")
    shutil.rmtree(velha, ignore_errors=True)
    if entrega.exists():
        os.replace(entrega, velha)
    os.replace(nova, entrega)
    shutil.rmtree(velha, ignore_errors=True)
    return manifesto


def subir_o_pote(saida_motor: dict, pasta: Path = PASTA, parar: Path = PARAR,
                 entrega: Path | None = None, corte: dict | None = None) -> dict:
    # A entrega le-se na CHAMADA (nao na definicao): o ensaio aponta-a para uma pasta temporaria.
    entrega = entrega or ENTREGA
    pote, convertidos = montar_o_pote(saida_motor)
    run = pote.get("INTELLIGENCE_RUN_ID", NAO_SEI)
    pasta.mkdir(parents=True, exist_ok=True)
    candidato = pasta / ".POTE.candidato.json"
    candidato.write_text(json.dumps(pote, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    # O fiscal le o FICHEIRO que vai para a entrega, e nao o dicionario em memoria: o que se confere
    # e o que se entrega, byte a byte.
    violacoes = VP.validar(VP.ler_ficheiro(candidato))
    base = {"CORRIDA": run, "ENTITY_SOURCE_CONVERTIDOS": convertidos}
    if violacoes:
        guardado = pasta / ("POTE-REPROVADO-%s.json" % run)
        os.replace(candidato, guardado)
        return dict(base, SUBIU=False, PORQUE="POTE_REPROVADO", VIOLACOES=len(violacoes),
                    PRIMEIRAS=violacoes[:10], GUARDADO_EM=str(guardado))
    if parar.exists():
        candidato.unlink(missing_ok=True)
        return dict(base, SUBIU=False, PORQUE="PARAR_FLAG_ANTES_DE_SUBIR")
    entregar(candidato, pote, entrega, corte)
    candidato.unlink(missing_ok=True)
    return dict(base, SUBIU=True, ENTREGA=str(entrega))


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
        # O corte vigente (defeito ITEM_ID repetido): declarado ANTES do motor, e fica escrito mesmo
        # que o motor rebente depois.
        export, corte = cortar_vigente(export)
        estado["INT_ULTIMO_CORTE"] = {k: corte[k] for k in ("LINHAS_NO_EXPORT", "LINHAS_NO_CORTE",
                                                             "DEFEITO_NA_SALA")}
        estado["INT_ULTIMO_CORTE"].update(
            ITEM_ID_REPETIDO=sorted(corte["ITEM_ID_REPETIDO"]),
            REPETIDO_SEM_HORA_LEGIVEL=sorted(corte["REPETIDO_SEM_HORA_LEGIVEL"]),
            ITEM_ID_SEM_IDENTIDADE=len(corte["ITEM_ID_SEM_IDENTIDADE"]))
        pasta_corrida.mkdir(parents=True, exist_ok=True)
        (pasta_corrida / "CORTE-VIGENTE.json").write_text(
            json.dumps(corte, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
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
        pote = (subir or (lambda s, pasta, parar: subir_o_pote(s, pasta=pasta, parar=parar, corte=corte)))(
            saida, pasta=pasta_corrida, parar=parar)
    except Exception as e:  # noqa: BLE001 — um gerador que rebenta tambem nao sobe
        pote = {"SUBIU": False, "PORQUE": "POTE_ERRO", "ERRO": repr(e)[:300]}
    estado["INT_ULTIMO_POTE"] = {k: pote.get(k) for k in ("SUBIU", "PORQUE", "CORRIDA", "VIOLACOES")}
    if pote.get("SUBIU"):
        estado["INT_ULTIMA_SUBIDA_EM"] = agora.isoformat()
        return {"ACCAO": "POTE_SUBIU", "GATILHO": d["PORQUE"], "CORTE": estado["INT_ULTIMO_CORTE"], **pote}
    return {"ACCAO": "POTE_NAO_SUBIU", "GATILHO": d["PORQUE"], "CORTE": estado["INT_ULTIMO_CORTE"], **pote}


PRECISA_NO_AMBIENTE = ("SINTONIA_SALA_DSN",)


def precondicoes(ambiente=None) -> list:
    """O que falta para uma volta. Diz o NOME da variavel, nunca o valor (a DSN nao se imprime)."""
    amb = os.environ if ambiente is None else ambiente
    return ["%s ausente (o .cmd le SALA_DSN.txt no arranque: set /p)" % v
            for v in PRECISA_NO_AMBIENTE if not amb.get(v)]


def ler_estado(caminho: Path = ESTADO) -> dict:
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def gravar_estado(estado: dict, caminho: Path = ESTADO) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_name(caminho.name + ".tmp")
    tmp.write_text(json.dumps(estado, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    os.replace(tmp, caminho)


def uma_volta(*, estado_em: Path = ESTADO, trinco_da_volta: Path = TRINCO_DA_VOLTA, ambiente=None,
              **kw) -> dict:
    """UMA volta do processo agendado: le o estado, corre `correr_se_devido`, grava o estado.

    Tudo dentro de TRINCO_DA_VOLTA: duas chamadas do agendador nunca leem e gravam o estado ao mesmo
    tempo (uma volta velha nao apaga a marca de uma nova). A segunda sai OCUPADO e nao grava nada."""
    falta = precondicoes(ambiente)
    if falta:
        return {"ACCAO": "PRECONDICOES", "FALTA": falta}
    try:
        with espera._Trava(str(trinco_da_volta)):
            estado = ler_estado(estado_em)
            r = correr_se_devido(estado, **kw)
            estado["INT_ULTIMA_VOLTA"] = {"EM": _agora().isoformat(), "ACCAO": r.get("ACCAO")}
            gravar_estado(estado, estado_em)
            return r
    except espera.EsperaOcupada:
        return {"ACCAO": "OCUPADO", "PORQUE": "outra volta do disparador esta a decorrer"}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--uma-volta" in argv:
        r = uma_volta()
        # O que se imprime e o resultado da volta; a DSN nunca esta nele (so o nome da variavel).
        print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
        return {"PRECONDICOES": 4, "OCUPADO": 3}.get(r.get("ACCAO"), 1 if r.get("ACCAO") in (
            "MOTOR_ERRO", "COPIA_NAO_VALE", "NAO_SEI") else 0)
    if "--medir" not in argv:
        print(__doc__.strip().split("\n\n")[0])
        print("\n  uso: python3 admissao/gatilho_da_inteligencia.py --medir | --uma-volta")
        return 2
    delta = medir_delta(_consulta_padrao, next((a.split("=", 1)[1] for a in argv
                                                if a.startswith("--desde=")), None))
    print(json.dumps(dict(delta, **decidir(delta, _agora())), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
