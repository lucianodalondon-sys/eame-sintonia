#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MICRO SOCIAL — o condutor de UMA noite de coleta social (LinkedIn / YouTube), por rodadas.

Quatro verbos, e so um vai a rede:

    py ferramentas/micro_social/micro_social.py plano    --lote=<LOTE.json>
        Sem rede, sem banco. Para cada item: o portao de coleta NO INSTANTE
        (curadoria/collection_gate.py), a fase (so LinkedIn/YouTube, as que o
        Scrap conta), o alvo (pagina / video) e a duracao declarada do video.
        Imprime o pedido exacto que `rodada` lancaria.

    py ferramentas/micro_social/micro_social.py rodada   --lote=<LOTE.json> --n=<K>
                                                         --estado=<ESTADO.json> --autorizado-pelo-dono
        A UNICA porta para a rede. Recusa, ANTES de qualquer pedido:
          - sem --autorizado-pelo-dono;
          - com PARAR-MICRO-SOCIAL.flag ao lado do estado (a parada automatica de
            uma rodada anterior);
          - com o robo a correr (sem curadoria/PARAR.flag, ou com processo
            supervisor|worker|ponte_automatica vivo);
          - sem as variaveis da Sala operacional (as mesmas da micro web);
          - com o egresso que nao seja IT pelo portao de consenso (superficie/rede.py).
        Cada item corre pela porta canonica (orquestrador -> scrap-colheita), com o
        Pedido montado em processo (a frase da linha de comando polui o alvo). Depois
        da rodada: egresso outra vez e a PROVA-TETO sobre TODAS as corridas da noite
        (D38 e por onda). Prova != PASS -> escreve PARAR-MICRO-SOCIAL.flag e sai 3.

    py ferramentas/micro_social/micro_social.py sala     --estado=<ESTADO.json>
        So SELECT (default_transaction_read_only na ligacao). Mostra, por item da
        Sala destas corridas, data e lugar com a BASE e a PRECISAO, e reprova valor
        sem base e fact_time igual a captured_at.

    py ferramentas/micro_social/micro_social.py relatorio --estado=<ESTADO.json>
        Chama o relatorio que ja existe (scripts/micro_coleta/micro_coleta.py
        relatorio --run-id=... --estado=...). O ESTADO sai na forma que ele le.

O LOTE (escrito pelo coordenador; o condutor nao escolhe fontes):
    {"RODADAS": [
       {"N": 1, "ITENS": [
          {"SOURCE_ID": "IT-T7-171", "FASE": "video-linkedin",
           "PAGINA": "https://www.linkedin.com/company/<slug>/", "TETO": 1}, ...]},
       {"N": 3, "ITENS": [
          {"SOURCE_ID": "IT-T8-006", "FASE": "audio-youtube",
           "VIDEO": "<11 caracteres>", "DURACAO_S": 480}]}]}

LEIS QUE ESTE FICHEIRO NAO REPETE: a elegibilidade (collection_gate), o egresso
(superficie/rede.py), o teto e a sua prova (provas/prova_teto_dominio.py), as
variaveis da Sala (scripts/micro_coleta/micro_coleta.py). Sao importados.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _p in ("", "curadoria", "scripts/micro_coleta", "provas"):
    sys.path.insert(0, str(RAIZ / _p) if _p else str(RAIZ))
import _gavetas  # noqa: E402,F401

FASES_SOCIAIS = {"video-linkedin": "pagina", "audio-youtube": "video"}
DURACAO_MAXIMA_S = 9 * 60 + 30          # "<= ~9 min", com meia folga declarada
PROCESSOS_DO_ROBO = "supervisor|worker|ponte_automatica"
FLAG_DE_PARADA = "PARAR-MICRO-SOCIAL.flag"
AUSENCIA = "NAO SEI"


def agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _modulo(nome: str, caminho: Path):
    s = importlib.util.spec_from_file_location(nome, str(caminho))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def ler_json(p) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def universo_de(sid: str) -> str:
    return sid.split("-")[1]


# ── PLANO (sem rede) ─────────────────────────────────────────────────────────
def conferir_item(it: dict, gate=None) -> list[str]:
    """O que impede este item de correr. Lista vazia = pronto."""
    falta = []
    sid, fase = it.get("SOURCE_ID") or "", it.get("FASE") or ""
    if not re.fullmatch(r"IT-T\d+-\d+", sid):
        falta.append("SOURCE_ID invalido: %r" % sid)
    if fase not in FASES_SOCIAIS:
        falta.append("FASE %r fora da MICRO social (so %s)" % (fase, ", ".join(FASES_SOCIAIS)))
    if fase == "video-linkedin":
        if not str(it.get("PAGINA", "")).startswith("https://www.linkedin.com/company/"):
            falta.append("PAGINA tem de ser https://www.linkedin.com/company/<slug>/")
        if int(it.get("TETO") or 0) != 1:
            falta.append("TETO tem de ser 1 (1 video por conta)")
    if fase == "audio-youtube":
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", str(it.get("VIDEO", ""))):
            falta.append("VIDEO tem de ser o id de 11 caracteres")
        d = it.get("DURACAO_S")
        if not isinstance(d, (int, float)) or d <= 0:
            falta.append("DURACAO_S em falta: a duracao le-se na pagina do video, antes")
        elif d > DURACAO_MAXIMA_S:
            falta.append("DURACAO_S %s > %s (video longo demais para a MICRO)" % (d, DURACAO_MAXIMA_S))
    if gate is not None and not falta:
        g = gate(sid)
        if not g.get("COLLECTION_ELIGIBLE"):
            falta.append("portao de coleta: %s — %s" % (g.get("MOTIVO"), str(g.get("PORQUE"))[:160]))
    return falta


def gate_canonico(sid: str) -> dict:
    import collection_gate as GATE  # noqa: PLC0415
    return GATE.avaliar(sid, **GATE._contexto())


def pedido_de(it: dict) -> dict:
    """Os filtros do Pedido, exactamente como o orquestrador os recebe."""
    u = universo_de(it["SOURCE_ID"])
    f = {"fase": it["FASE"], "fonte": it["SOURCE_ID"], "pais": "IT", "universo": u}
    if it["FASE"] == "video-linkedin":
        f.update(pagina=it["PAGINA"], teto=str(it.get("TETO", 1)))
    else:
        f["video"] = it["VIDEO"]
    return {"alvo": u, "filtros": f}


def comando_de(it: dict) -> list[str]:
    p = pedido_de(it)
    codigo = ("import sys, json; sys.path[:0] = ['.', 'orquestrador']; import _gavetas; "
              "import orquestrador as O; from pedido import Pedido; "
              "r = O.correr(Pedido(alvo=%r, filtros=%r)); "
              "print('CORRIDA %%s · %%s' %% (r.get('STATUS'), r.get('RUN_ID')))"
              % (p["alvo"], p["filtros"]))
    return [sys.executable, "-c", codigo]


def plano(lote: dict, *, gate=gate_canonico) -> dict:
    linhas = []
    for r in lote.get("RODADAS", []):
        for it in r.get("ITENS", []):
            falta = conferir_item(it, gate)
            linhas.append({"RODADA": r.get("N"), "SOURCE_ID": it.get("SOURCE_ID"),
                           "FASE": it.get("FASE"), "ESTADO": "PRONTA" if not falta else "BLOQUEADA",
                           "FALTA": falta, "PEDIDO": pedido_de(it) if not falta else None})
    return {"GERADO_EM": agora(), "LINHAS": linhas,
            "PRONTAS": sum(1 for l in linhas if l["ESTADO"] == "PRONTA"), "DE": len(linhas)}


# ── AS TRAVAS DE `rodada` ───────────────────────────────────────────────────
def robo_parado(raiz: Path = RAIZ, processos=None) -> tuple[bool, str]:
    if not (raiz / "curadoria" / "PARAR.flag").exists():
        return False, "curadoria/PARAR.flag nao existe: o robo nao foi mandado parar"
    vivos = processos() if processos else _processos_do_robo()
    if vivos is None:
        return False, "NAO SEI se o robo parou (a lista de processos nao respondeu)"
    if vivos:
        return False, "processos do robo ainda vivos: %s" % "; ".join(vivos)[:300]
    return True, "PARAR.flag presente e nenhum processo %s" % PROCESSOS_DO_ROBO


def _processos_do_robo():
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe' or Name='py.exe'\" | "
          "Where-Object { $_.CommandLine -match '%s' -and $_.CommandLine -notmatch 'micro_social' } | "
          "ForEach-Object { '{0} {1}' -f $_.ProcessId, $_.CommandLine }" % PROCESSOS_DO_ROBO)
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=60)
    except Exception:                                               # noqa: BLE001
        return None
    if r.returncode != 0:
        return None
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def egresso_it() -> dict:
    rede = _modulo("rede_egresso", RAIZ / "superficie" / "rede.py")
    try:
        v = rede.portao_de_egresso("IT", cache=False)
    except Exception as e:                                          # noqa: BLE001
        return {"PAIS": AUSENCIA, "GATE": "BLOCKED", "PORQUE": "%s: %s" % (type(e).__name__, e)}
    return {"PAIS": v.get("EGRESS_COUNTRY_CODE", AUSENCIA), "GATE": v.get("EGRESS_GATE"),
            "PORQUE": v.get("PORQUE_BLOQUEADO") or v.get("PORQUE"), "QUANDO": agora()}


def lote_1_instalado(raiz: Path = RAIZ) -> list[str]:
    """A MICRO social so e provavel com a PROVA-TETO-SOCIAL instalada (lote 1 do INTEGRA-NOITE).

    Sem o contador do Scrap nao ha PEDIDOS_POR_HOST (a prova diria NAO_SEI a tudo); sem a
    D41 na prova, youtube.com e googlevideo.com contam a parte e 3 + 3 passaria como PASS.
    Le-se o CODIGO (texto), sem importar: importar o scrap_http instala o abridor dele."""
    falta = []
    def _tem(rel, marca):
        p = raiz / rel
        return p.exists() and marca in p.read_text(encoding="utf-8", errors="replace")
    if not _tem("coleta/scrap_http.py", "def contar_pedido"):
        falta.append("coleta/scrap_http.py sem o contador de pedidos (PROVA-TETO-SOCIAL)")
    if not _tem("coleta/scrap_colheita.py", "def escrever_linha"):
        falta.append("coleta/scrap_colheita.py nao escreve a linha no livro de corridas")
    if not _tem("provas/prova_teto_dominio.py", '"googlevideo.com": "youtube.com"'):
        falta.append("provas/prova_teto_dominio.py sem a D41 (googlevideo.com paga em youtube.com)")
    if not _tem("ferramentas/youtube_transcrever.py", "--print-traffic"):
        falta.append("ferramentas/youtube_transcrever.py sem --print-traffic (yt-dlp por contar)")
    return falta


def yt_dlp_abre() -> tuple[bool, str]:
    """O audio corre `sys.executable -m yt_dlp` (ferramentas/youtube_transcrever.py::_audio).

    ⚠️ MEDIDO NO ENSAIO A SECO (26/09): `shutil.which('yt-dlp')` acha um executavel de OUTRO
    projeto, a sonda do adaptador diz «pronto», e o `py` nao tem o modulo: AUDIO_NAO_OBTIDO
    com zero pedidos. Pergunta-se ao mesmo interpretador que o audio vai usar. Sem rede."""
    try:
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--version"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=120)
    except Exception as e:                                          # noqa: BLE001
        return False, "%s: %s" % (type(e).__name__, e)
    if r.returncode != 0:
        return False, ((r.stderr or r.stdout).strip().splitlines() or ["sem mensagem"])[-1][:200]
    return True, r.stdout.strip()


def precondicoes_da_sala(ambiente=None) -> list[str]:
    import micro_coleta as MC  # noqa: PLC0415
    return MC.precondicoes(ambiente)


def livro_de_corridas() -> Path:
    return Path(os.environ.get("ITALY_OPS_ROOT") or RAIZ) / "data" / "collection-ledger" / "italy" / "runs.ndjson"


def prova_teto(run_ids: list[str], pasta: Path, livro: Path | None = None) -> dict:
    ptd = _modulo("prova_teto_dominio", RAIZ / "provas" / "prova_teto_dominio.py")
    livro = Path(livro or livro_de_corridas())
    corridas = ptd.ler_livro(livro.read_text(encoding="utf-8").splitlines()) if livro.exists() else {}
    r = ptd.verificar(run_ids, corridas)
    (pasta / "PROVA-TETO-DA-NOITE.json").write_text(json.dumps(r, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")
    return r


# ── RODADA (a unica porta para a rede) ──────────────────────────────────────
def rodada(lote: dict, n: int, estado_p: Path, *, autorizado=False, gate=gate_canonico,
           parado=robo_parado, egresso=egresso_it, sala=precondicoes_da_sala,
           lancar=None, teto=prova_teto, instalado=lote_1_instalado, yt_dlp=yt_dlp_abre) -> dict:
    estado_p = Path(estado_p)
    pasta = estado_p.parent
    flag = pasta / FLAG_DE_PARADA
    if not autorizado:
        return {"CORREU": False, "PORQUE": "falta --autorizado-pelo-dono"}
    falta_lote = instalado()
    if falta_lote:
        return {"CORREU": False, "PORQUE": "LOTE_1_NAO_INSTALADO", "FALTA": falta_lote}
    if flag.exists():
        return {"CORREU": False, "PORQUE": "PARADA AUTOMATICA anterior: %s"
                % flag.read_text(encoding="utf-8").strip()[:300]}
    ok, porque = parado()
    if not ok:
        return {"CORREU": False, "PORQUE": "ROBO_NAO_PARADO: " + porque}
    falta = sala()
    if falta:
        return {"CORREU": False, "PORQUE": "precondicoes da Sala", "FALTA": falta}
    rodadas = [r for r in lote.get("RODADAS", []) if r.get("N") == n]
    if not rodadas:
        return {"CORREU": False, "PORQUE": "rodada %s nao esta no lote" % n}
    if any(it.get("FASE") == "audio-youtube" for it in rodadas[0].get("ITENS", [])):
        ok_yt, porque_yt = yt_dlp()
        if not ok_yt:
            return {"CORREU": False, "PORQUE": "YT_DLP_NAO_ABRE no interpretador do audio: " + porque_yt}
    antes = egresso()
    if antes.get("GATE") != "PASS":
        return {"CORREU": False, "PORQUE": "EGRESSO_NAO_IT", "EGRESSO_ANTES": antes}

    estado = ler_json(estado_p) if estado_p.exists() else {"FONTES": [], "RODADAS": []}
    corridas = []
    for it in rodadas[0].get("ITENS", []):
        falta = conferir_item(it, gate)
        if falta:
            corridas.append({"SOURCE_ID": it.get("SOURCE_ID"), "CORREU": False, "FALTA": falta})
            continue
        g = gate(it["SOURCE_ID"])
        cmd = comando_de(it)
        if lancar is not None:
            r = lancar(cmd)
        else:
            x = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=1800)
            r = {"CODIGO": x.returncode, "SAIDA": x.stdout[-4000:], "ERRO": x.stderr[-1500:]}
        m = re.search(r"CORRIDA (\S+) · (\S+)", r.get("SAIDA", ""))
        corridas.append({"SOURCE_ID": it["SOURCE_ID"], "FASE": it["FASE"], "CORREU": True,
                         "STATUS": m.group(1) if m else AUSENCIA,
                         "RUN_ID": m.group(2) if m else AUSENCIA,
                         "GATE": g.get("MOTIVO"), "CODIGO": r.get("CODIGO"),
                         "ERRO": (r.get("ERRO") or "")[-300:]})
    depois = egresso()
    for c in corridas:
        if c.get("CORREU"):
            c["EGRESSO"] = [antes.get("PAIS"), depois.get("PAIS")]
    estado["FONTES"] += [c for c in corridas if c.get("RUN_ID") not in (None, AUSENCIA)]
    estado["RODADAS"].append({"N": n, "QUANDO": agora(), "CORRIDAS": corridas,
                              "EGRESSO_ANTES": antes, "EGRESSO_DEPOIS": depois})
    # ── A PROVA-TETO, SOBRE A NOITE INTEIRA (D38 e por onda, nao por rodada) ──
    ids = [f["RUN_ID"] for f in estado["FONTES"]]
    corridas_falhadas = [c for c in corridas if c.get("CORREU") and c.get("RUN_ID") in (None, AUSENCIA)]
    prova = teto(ids, pasta) if ids else {"ESTADO": "NAO_SEI", "PORQUE": "nenhuma corrida com RUN_ID"}
    estado["RODADAS"][-1]["PROVA_TETO"] = {k: prova.get(k) for k in
                                           ("ESTADO", "DOMINIOS_ACIMA_DO_TETO", "PEDIDOS_NA_ONDA",
                                            "CORRIDAS_SEM_LINHA_NO_LIVRO", "CORRIDAS_SEM_PEDIDOS_POR_HOST")}
    parar = []
    if prova.get("ESTADO") != "PASS":
        parar.append("PROVA-TETO=%s %s" % (prova.get("ESTADO"), prova.get("DOMINIOS_ACIMA_DO_TETO") or ""))
    if depois.get("GATE") != "PASS":
        parar.append("EGRESSO DEPOIS=%s" % depois.get("PAIS"))
    if corridas_falhadas:
        parar.append("corrida sem RUN_ID: %s" % [c["SOURCE_ID"] for c in corridas_falhadas])
    estado_p.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
    if parar:
        flag.write_text("%s rodada %s: %s\n" % (agora(), n, " · ".join(parar)), encoding="utf-8")
    return {"CORREU": True, "RODADA": n, "CORRIDAS": corridas, "PROVA_TETO": prova.get("ESTADO"),
            "PARADA_AUTOMATICA": parar}


# ── SALA (so leitura) ───────────────────────────────────────────────────────
CAMPOS_DA_SALA = (
    "source_id", "item_id", "captured_at::text",
    "published_at", "published_at_basis", "tempo_lugar_evidencia->>'PUBLISHED_AT_PRECISION'",
    "source_location", "source_location_basis", "tempo_lugar_evidencia->>'SOURCE_LOCATION_PRECISION'",
    "fact_time", "fact_time_basis", "tempo_lugar_evidencia->>'FACT_TIME_PRECISION'",
    "fact_location", "fact_location_basis", "tempo_lugar_evidencia->>'FACT_LOCATION_PRECISION'")
NOMES = ("SOURCE_ID", "ITEM", "CAPTURED_AT", "PUBLISHED_AT", "PUBLISHED_AT_BASIS",
         "PUBLISHED_AT_PRECISION", "SOURCE_LOCATION", "SOURCE_LOCATION_BASIS",
         "SOURCE_LOCATION_PRECISION", "FACT_TIME", "FACT_TIME_BASIS", "FACT_TIME_PRECISION",
         "FACT_LOCATION", "FACT_LOCATION_BASIS", "FACT_LOCATION_PRECISION")
DESCONHECIDO = {"", "NAO SEI", "UNKNOWN", "NÃO SEI", "NOT_KNOWN", None}


def conferir_sala(linhas: list[dict]) -> list[str]:
    """Valor sem base, e fact_time copiado do captured_at: os dois erros que reprovam."""
    mal = []
    for l in linhas:
        for c in ("PUBLISHED_AT", "SOURCE_LOCATION", "FACT_TIME", "FACT_LOCATION"):
            if l.get(c) not in DESCONHECIDO and l.get(c + "_BASIS") in DESCONHECIDO:
                mal.append("%s %s: %s=%r sem base" % (l["SOURCE_ID"], l["ITEM"], c, l[c]))
        if l.get("FACT_TIME") not in DESCONHECIDO and l.get("FACT_TIME") == l.get("CAPTURED_AT"):
            mal.append("%s %s: FACT_TIME igual a CAPTURED_AT (fabricado)" % (l["SOURCE_ID"], l["ITEM"]))
    return mal


def sala(estado: dict, consulta=None) -> dict:
    ids = [f["RUN_ID"] for f in estado.get("FONTES", []) if f.get("RUN_ID")]
    if not ids:
        return {"LINHAS": [], "MAL": [], "PASSA": False, "PORQUE": "nenhuma corrida no estado"}
    for i in ids:
        if not re.fullmatch(r"[A-Z]{2}-T\d+-[0-9-]+-[0-9a-f]{16}", i):
            raise ValueError("RUN_ID com forma inesperada: %r" % i)
    if consulta is None:
        import micro_coleta as MC  # noqa: PLC0415
        consulta = MC.sql
    em = ",".join("'%s'" % i for i in ids)
    brutas = consulta("select %s from sala_de_espera_atual where run_id in (%s) order by run_id, ordem"
                      % (", ".join(CAMPOS_DA_SALA), em))
    linhas = [dict(zip(NOMES, b)) for b in brutas]
    mal = conferir_sala(linhas)
    return {"LINHAS": linhas, "MAL": mal, "PASSA": bool(linhas) and not mal}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    verbo = argv[0] if argv else ""
    opc = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    if verbo == "plano":
        p = plano(ler_json(opc["lote"]))
        print(json.dumps(p, ensure_ascii=False, indent=1))
        return 0 if p["PRONTAS"] == p["DE"] else 1
    if verbo == "rodada":
        r = rodada(ler_json(opc["lote"]), int(opc["n"]), Path(opc["estado"]),
                   autorizado="--autorizado-pelo-dono" in argv)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        if not r.get("CORREU"):
            return 2
        return 3 if r.get("PARADA_AUTOMATICA") else 0
    if verbo == "sala":
        s = sala(ler_json(opc["estado"]))
        print(json.dumps(s, ensure_ascii=False, indent=1))
        return 0 if s["PASSA"] else 1
    if verbo == "relatorio":
        est = ler_json(opc["estado"])
        ids = ["--run-id=%s" % f["RUN_ID"] for f in est.get("FONTES", []) if f.get("RUN_ID")]
        cmd = [sys.executable, str(RAIZ / "scripts" / "micro_coleta" / "micro_coleta.py"),
               "relatorio", *ids, "--estado=%s" % opc["estado"]]
        if "saida" in opc:
            cmd.append("--saida=%s" % opc["saida"])
        return subprocess.call(cmd, cwd=RAIZ)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
