"""MICRO-COLETA WEB — o instrumento unico (missao 6-PREP).

Tres verbos, e so um deles vai a rede:

    py scripts/micro_coleta/micro_coleta.py plano
        Sem rede, sem banco. Para cada fonte da coorte proposta pergunta, no
        instante, ao gate canonico (curadoria/collection_gate.py), se ha
        contrato de coleta (regras/italy_contracts_onboarded.json) e se ha
        receita que leve o universo ao italy_executor (pedido/receitas.py).
        Imprime o comando exacto que `correr` lancaria.

    py scripts/micro_coleta/micro_coleta.py correr --autorizado-pelo-dono
        A UNICA porta para a rede. Recusa sem a bandeira, sem as quatro
        variaveis da Sala operacional, com BANCO_DESCARTAVEL_URL presente, ou
        com egresso que nao seja IT — medido ANTES e DEPOIS de cada corrida.
        Cada fonte corre pela porta canonica:
            orquestrador -> italy_executor -> ingresso -> preservar_coleta
        e no fim chama `relatorio` sobre os RUN_ID que nasceram.

    py scripts/micro_coleta/micro_coleta.py relatorio --run-id=<R> [--run-id=...]
        So SELECT, e com a ligacao posta em `default_transaction_read_only`
        pelo proprio Postgres: uma escrita seria recusada pelo banco, nao pela
        nossa boa vontade. Mede os criterios de passagem (ver CRITERIOS) e
        escreve RELATORIO-PASSAGEM.{json,md} fora do repositorio.

LEIS QUE ESTE FICHEIRO NAO REPETE: a regra de elegibilidade (collection_gate),
o juiz de capa (curadoria/retrato_html.py), a regua da Admission
(admissao/admissao.py). Sao importados; nenhum limiar e copiado.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "curadoria"))
import _gavetas  # noqa: E402,F401

import collection_gate as GATE        # noqa: E402
import retrato_html as RETRATO        # noqa: E402
from leis import territorios as TERR  # noqa: E402
import receitas as REC                 # noqa: E402  (a gaveta pedido/ esta no caminho)
from pedido import de_uma_frase        # noqa: E402

AQUI = Path(__file__).resolve().parent
COORTE = AQUI / "COORTE-PROPOSTA.json"
CONTRATOS = RAIZ / "regras" / "italy_contracts_onboarded.json"
LIVRO = RAIZ / "data" / "samples" / "LIVRO-DE-DECISOES.json"
EXECUTOR = "coleta/italy_executor.py"

VARIAVEIS_DA_SALA = ("SINTONIA_COLLECTION_DSN", "SINTONIA_SALA_DSN",
                     "SINTONIA_SALA_BACKEND", "SINTONIA_PSQL_EXE")
AUSENCIA = "NAO SEI"


def agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── PLANO ─────────────────────────────────────────────────────────────────
def ler_coorte(caminho: Path = COORTE) -> dict:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def universo_de(source_id: str) -> str:
    return source_id.split("-")[1]


def apelido_de(universo: str) -> str | None:
    """A palavra que faz a frase do pedido resolver o territorio.

    ⚠️ O orquestrador junta na frase todo argumento que nao comece por `--` —
    e o valor de `--filtro fonte=X` nao comeca. A frase so resolve porque
    `alvo_de` procura um apelido la dentro. Uma so palavra, a primeira que o
    dono (`leis/territorios.APELIDOS`) declara para o universo.
    """
    for palavra, cod in TERR.APELIDOS.items():
        if cod == universo and " " not in palavra:
            return palavra
    return None


def receita_web(universo: str) -> dict | None:
    for r in REC.EXECUTORES.get(universo) or []:
        if EXECUTOR in (r.get("roda") or []):
            return r
    return None


def comando(source_id: str) -> list[str]:
    u = universo_de(source_id)
    return [sys.executable, "orquestrador/orquestrador.py", apelido_de(u) or u,
            "--filtro", f"fonte={source_id}", "--filtro", f"universo={u}"]


def plano(ids: list[str] | None = None, *, ctx: dict | None = None) -> dict:
    coorte = ler_coorte()
    ids = ids or [f["SOURCE_ID"] for f in coorte["PROPOSTAS"]]
    ctx = ctx if ctx is not None else GATE._contexto()
    contratos = {f["SOURCE_ID"]: f for f in
                 json.loads(CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}
    linhas = []
    for s in ids:
        g = GATE.avaliar(s, **ctx)
        u = universo_de(s)
        falta = []
        if not g["COLLECTION_ELIGIBLE"]:
            falta.append(f"GATE:{g['MOTIVO']}")
        if s not in contratos:
            falta.append("SEM_CONTRATO_DE_COLETA")
        if receita_web(u) is None:
            falta.append(f"SEM_RECEITA_WEB_PARA_{u}")
        if apelido_de(u) is None:
            falta.append(f"SEM_APELIDO_PARA_{u}")
        # A frase que o orquestrador vai montar, resolvida AQUI e sem rede:
        # alvo certo e executor web. Foi a frase que parou a canonical-micro.
        cmd = comando(s)
        try:
            ped = de_uma_frase(" ".join(a for a in cmd[2:] if not a.startswith("--")))
            ped.filtros.update({"fonte": s, "universo": u})
            pl = REC.resolver(ped)
            frase_ok = ped.alvo == u and any(EXECUTOR in (e.get("roda") or [])
                                             for e in pl.executores)
        except Exception as ex:                                # noqa: BLE001
            frase_ok = False
            falta.append(f"FRASE_RECUSADA:{type(ex).__name__}")
        if not frase_ok and not any(f.startswith("SEM_RECEITA") for f in falta):
            falta.append("FRASE_NAO_RESOLVE_PARA_O_EXECUTOR_WEB")
        linhas.append({"SOURCE_ID": s, "UNIVERSO": u,
                       "GATE": g["MOTIVO"], "READY_RULE": g["READY_RULE"],
                       "CONTRATO": s in contratos,
                       "RECEITA_WEB": receita_web(u) is not None,
                       "FRASE_RESOLVE": frase_ok,
                       "ESTADO": "PRONTA" if not falta else "BLOQUEADA",
                       "FALTA": falta,
                       "COMANDO": " ".join(comando(s)[1:])})
    return {"GERADO_EM": agora(), "GATE": GATE.CONTRATO,
            "PAINEL_DO_GATE": GATE.painel(ctx=ctx),
            "EXCLUIDAS": coorte.get("EXCLUIDAS", []),
            "PRONTAS": sum(1 for l in linhas if l["ESTADO"] == "PRONTA"),
            "BLOQUEADAS": sum(1 for l in linhas if l["ESTADO"] != "PRONTA"),
            "LINHAS": linhas}


# ── BANCO, SO LEITURA ─────────────────────────────────────────────────────
class EscritaRecusada(Exception):
    pass


def _dsn() -> str:
    d = os.environ.get("SINTONIA_SALA_DSN")
    if d:
        return d
    f = Path.home() / "sintonia-sala-italia" / "SALA_DSN.txt"
    return f.read_text(encoding="utf-8").strip()


def _psql() -> str:
    return os.environ.get("SINTONIA_PSQL_EXE") or str(
        Path.home() / "orca" / "pgtmp" / "pgsql" / "bin" / "psql.exe")


def sql(consulta: str) -> list[list[str]]:
    """SELECT e nada mais — duas travas, uma nossa e uma do banco."""
    if not re.match(r"^\s*(select|with)\b", consulta, re.I) or ";" in consulta.strip().rstrip(";"):
        raise EscritaRecusada(consulta[:80])
    env = {**os.environ, "PGOPTIONS": "-c default_transaction_read_only=on"}
    # psql no Windows nao permuta opcoes: todas antes da DSN.
    r = subprocess.run([_psql(), "-X", "-At", "-F", "\t", "-v", "ON_ERROR_STOP=1",
                        "-c", consulta, _dsn()], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[-300:])
    return [l.rstrip("\r").split("\t") for l in r.stdout.splitlines() if l.strip()]


# ── CORRER (a unica porta para a rede) ────────────────────────────────────
def medir_egresso() -> dict:
    r = subprocess.run(["curl", "-s", "-m", "15", "https://ipinfo.io/json"],
                       capture_output=True, text=True, timeout=30)
    try:
        d = json.loads(r.stdout)
        return {"PAIS": d.get("country", AUSENCIA), "IP": d.get("ip", AUSENCIA),
                "CIDADE": d.get("city", AUSENCIA), "QUANDO": agora()}
    except ValueError:
        return {"PAIS": AUSENCIA, "QUANDO": agora()}


def precondicoes(ambiente=None) -> list[str]:
    env = os.environ if ambiente is None else ambiente
    falta = [v for v in VARIAVEIS_DA_SALA if not env.get(v)]
    if env.get("SINTONIA_SALA_BACKEND") and env["SINTONIA_SALA_BACKEND"] != "POSTGRES":
        falta.append("SINTONIA_SALA_BACKEND!=POSTGRES (a Sala cairia em FICHEIRO)")
    if env.get("BANCO_DESCARTAVEL_URL"):
        falta.append("BANCO_DESCARTAVEL_URL presente (ModosEmConflito)")
    return falta


def correr(ids=None, *, autorizado=False, lancar=None, egresso=medir_egresso,
           ambiente=None, consulta=sql, saida: Path | None = None) -> dict:
    if not autorizado:
        return {"CORREU": False, "PORQUE": "falta --autorizado-pelo-dono"}
    falta = precondicoes(ambiente)
    if falta:
        return {"CORREU": False, "PORQUE": "precondicoes", "FALTA": falta}
    p = plano(ids)
    corridas = []
    for l in p["LINHAS"]:
        if l["ESTADO"] != "PRONTA":
            corridas.append({"SOURCE_ID": l["SOURCE_ID"], "CORREU": False,
                             "PORQUE": l["FALTA"]})
            continue
        antes = egresso()
        if antes.get("PAIS") != "IT":
            corridas.append({"SOURCE_ID": l["SOURCE_ID"], "CORREU": False,
                             "PORQUE": "EGRESSO_NAO_IT", "EGRESSO_ANTES": antes})
            continue
        # O veredito do gate no INSTANTE da corrida fica no relatorio: e a prova
        # de que a decisao do bot atravessou em runtime, nao por fotografia.
        g = GATE.avaliar(l["SOURCE_ID"], **GATE._contexto())
        cmd = comando(l["SOURCE_ID"])
        if lancar is not None:
            r = lancar(cmd)
        else:
            x = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=1800)
            r = {"CODIGO": x.returncode, "SAIDA": x.stdout[-4000:], "ERRO": x.stderr[-1500:]}
        m = re.search(r"CORRIDA (\S+) · (\S+)", r.get("SAIDA", ""))
        corridas.append({"SOURCE_ID": l["SOURCE_ID"], "CORREU": True,
                         "STATUS": m.group(1) if m else AUSENCIA,
                         "RUN_ID": m.group(2) if m else AUSENCIA,
                         "GATE_NO_INSTANTE": g["MOTIVO"],
                         "EGRESSO_ANTES": antes, "EGRESSO_DEPOIS": egresso(),
                         "CODIGO": r.get("CODIGO")})
    runs = [c for c in corridas if c.get("RUN_ID") not in (None, AUSENCIA)]
    rel = relatorio([c["RUN_ID"] for c in runs], corridas=corridas,
                    consulta=consulta, saida=saida) if runs else None
    return {"CORREU": True, "CORRIDAS": corridas, "RELATORIO": rel}


# ── RELATORIO DE PASSAGEM ─────────────────────────────────────────────────
def _em(run_ids: list[str]) -> str:
    for r in run_ids:
        if not re.fullmatch(r"[A-Za-z0-9_.:-]+", r):
            raise ValueError(f"RUN_ID com caracteres fora da forma: {r!r}")
    return ",".join(f"'{r}'" for r in run_ids)


def controlo_negativo_de_capa() -> dict:
    """O juiz de capa tem de reprovar uma listagem e aprovar uma materia.
    Se nao distinguir as duas aqui, o `0 capas` do relatorio nao vale nada."""
    listagem = ("<html><body>" + "".join(
        f'<a href="/news/n{i}">Notizia {i}</a> ' for i in range(120)) + "</body></html>").encode()
    materia = ("<html><body><h1>Titolo</h1>" + "<p>" + ("Il prezzo delle pere "
               "e salito del dieci per cento sui mercati all'ingrosso. " * 40)
               + "</p></body></html>").encode()
    a = RETRATO.retrato_do_html(listagem)["CAPA_OU_MATERIA"]
    b = RETRATO.retrato_do_html(materia)["CAPA_OU_MATERIA"]
    return {"LISTAGEM": a, "MATERIA": b,
            "PASSA": a == "CAPA_PROVAVEL" and b == "MATERIA_PROVAVEL"}


def _armazem() -> Path:
    r = os.environ.get("SINTONIA_ARMAZEM_RAIZ")
    return Path(r) if r else Path.home() / "sintonia-sala-italia" / "armazem"


def relatorio(run_ids: list[str], *, corridas: list | None = None,
              consulta=sql, livro: Path = LIVRO, armazem: Path | None = None,
              saida: Path | None = None) -> dict:
    em = _em(run_ids)
    armazem = armazem or _armazem()
    obs = consulta(
        "select r.id, r.source_id, r.media_type, r.storage_path, r.storage_object_id,"
        " coalesce(d.id::text,''), r.captured_at::text, r.run_id"
        " from raw_asset r left join derived_artifact d on d.raw_asset_id = r.id"
        f" where r.run_id in ({em}) order by r.id")
    sala = consulta(
        "select s.item_id, s.raw_observation_id, s.source_id, s.fact_time,"
        " s.fact_location, s.captured_at::text, s.run_id,"
        " (select count(*) from raw_asset r join storage_object so on so.id = r.storage_object_id"
        "   join derived_artifact d on d.raw_asset_id = r.id"
        "   join collection_run c on c.run_id = r.run_id"
        "  where r.id::text = s.raw_observation_id::text and 'derived:' || d.id = s.item_id)"
        f" from sala_de_espera s where s.run_id in ({em})")
    decisoes = [d for d in json.loads(Path(livro).read_text(encoding="utf-8"))["DECISOES"]
                if d.get("corrida") in run_ids]
    por_item = {d["item"]: d for d in decisoes}

    # C2 — materia individual, pelo juiz canonico, sobre os BYTES brutos
    capas, sem_bytes, julgados = [], 0, 0
    for o in obs:
        if "html" not in (o[2] or ""):
            continue
        f = armazem / o[3]
        if not f.exists():
            sem_bytes += 1
            continue
        julgados += 1
        if RETRATO.retrato_do_html(f.read_bytes())["CAPA_OU_MATERIA"] == "CAPA_PROVAVEL":
            capas.append(o[0])
    neg = controlo_negativo_de_capa()

    # C7 — proporcao por fonte
    por_fonte: dict = {}
    for o in obs:
        v = por_item.get(f"derived:{o[5]}", {}).get("resultado", "SEM_DECISAO") if o[5] else "SEM_DERIVADO"
        por_fonte.setdefault(o[1], {}).setdefault(v, 0)
        por_fonte[o[1]][v] += 1

    sala_sem_sim = [s[0] for s in sala if por_item.get(s[0], {}).get("resultado") != "SIM"]
    sim_fora_da_sala = [i for i, d in por_item.items()
                        if d["resultado"] == "SIM" and i not in {s[0] for s in sala}]
    fact_time_unknown = sum(1 for s in sala if s[3] in (AUSENCIA, "", "UNKNOWN"))
    fact_loc_unknown = sum(1 for s in sala if s[4] in (AUSENCIA, "", "UNKNOWN"))
    fact_time_fabricado = sum(1 for s in sala if s[3] and s[3] == s[5])
    egressos = [c for c in (corridas or []) if c.get("CORREU")]

    C = {
        "C1_EGRESSO_IT_POR_CORRIDA": {
            "MEDIDO": [(c["SOURCE_ID"], c["EGRESSO_ANTES"].get("PAIS"),
                        c["EGRESSO_DEPOIS"].get("PAIS")) for c in egressos],
            "PASSA": bool(egressos) and all(c["EGRESSO_ANTES"].get("PAIS") == "IT" and
                                            c["EGRESSO_DEPOIS"].get("PAIS") == "IT"
                                            for c in egressos)},
        # ⚠️ O juiz canonico (CAPA_NAO_E_MATERIA/v1) mede ESTRUTURA, e reprova
        # noticia curta com menu grande: no lote-76 apontou 6 de 76, e os 6
        # sao noticias individuais com data (RELATORIO-MICRO-PREP). Por isso
        # uma capa apontada nao reprova sozinha: vai para CAPAS-A-CONFIRMAR.tsv
        # e o criterio fica PENDENTE_HUMANO ate uma pessoa ler.
        "C2_MATERIA_NAO_CAPA": {
            "HTML_JULGADOS": julgados, "CAPAS_DO_JUIZ": capas, "SEM_BYTES": sem_bytes,
            "CONTROLO_NEGATIVO": neg,
            "ESTADO": ("FAIL" if not neg["PASSA"] or julgados == 0 or sem_bytes
                       else "PENDENTE_HUMANO" if capas else "PASS"),
            "PASSA": neg["PASSA"] and julgados > 0 and not capas and sem_bytes == 0},
        "C3_PONTE_EM_RUNTIME": {
            "GATE_NO_INSTANTE": [(c["SOURCE_ID"], c.get("GATE_NO_INSTANTE")) for c in egressos],
            "FONTES_NOS_RAW": sorted(por_fonte),
            "PASSA": bool(egressos) and all(c.get("GATE_NO_INSTANTE") == "ELIGIBLE" for c in egressos)
                     and set(por_fonte) <= {c["SOURCE_ID"] for c in egressos}},
        "C4_PROVENIENCIA_COMPLETA": {
            "SALA_LINHAS": len(sala),
            "SALA_COM_CADEIA_INTEIRA": sum(1 for s in sala if s[7] == "1"),
            "OBSERVACOES": len(obs),
            "COM_STORAGE": sum(1 for o in obs if o[4]),
            "COM_DERIVADO": sum(1 for o in obs if o[5]),
            "COM_DECISAO": sum(1 for o in obs if f"derived:{o[5]}" in por_item),
            "PASSA": len(sala) > 0 and all(s[7] == "1" for s in sala)
                     and all(o[4] and o[5] and f"derived:{o[5]}" in por_item for o in obs)},
        "C5_FACT_TIME_LOCATION": {
            "SALA": len(sala), "FACT_TIME_UNKNOWN": fact_time_unknown,
            "FACT_LOCATION_UNKNOWN": fact_loc_unknown,
            "FACT_TIME_IGUAL_A_CAPTURED_AT": fact_time_fabricado,
            "PASSA": fact_time_fabricado == 0},
        "C6_ZERO_BYPASS": {
            "SALA_SEM_SIM_NO_LIVRO": sala_sem_sim, "SIM_FORA_DA_SALA": sim_fora_da_sala,
            "PASSA": not sala_sem_sim and not sim_fora_da_sala},
        "C7_PROPORCAO_POR_FONTE_E_CLASSE": {
            "POR_FONTE": por_fonte,
            "CLASSE_POR_ITEM": "folha CLASSES.tsv — preenchida por pessoa (FONTE/ROTA/REGUA/TEMA/UNKNOWN)",
            "PASSA": bool(por_fonte) and not any(
                k in v for v in por_fonte.values() for k in ("SEM_DECISAO", "SEM_DERIVADO"))},
    }
    rel = {"GERADO_EM": agora(), "RUN_IDS": run_ids, "CRITERIOS": C,
           "PASSOU": sum(1 for c in C.values() if c["PASSA"]), "DE": len(C),
           "LEI": "so SELECT; default_transaction_read_only=on na ligacao"}
    if saida:
        saida = Path(saida)
        saida.mkdir(parents=True, exist_ok=True)
        (saida / "RELATORIO-PASSAGEM.json").write_text(
            json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
        folha = ["derived\tsource_id\tveredito\tCLASSE\tporque"]
        for o in obs:
            v = por_item.get(f"derived:{o[5]}", {}).get("resultado", AUSENCIA)
            if v != "SIM":
                folha.append(f"{o[5]}\t{o[1]}\t{v}\t\t")
        (saida / "CLASSES.tsv").write_text("\n".join(folha) + "\n", encoding="utf-8")
        (saida / "CAPAS-A-CONFIRMAR.tsv").write_text(
            "raw_id\tsource_id\tstorage_path\tE_CAPA(SIM/NAO)\tporque\n" + "".join(
                f"{o[0]}\t{o[1]}\t{o[3]}\t\t\n" for o in obs if o[0] in capas),
            encoding="utf-8")
        md = [f"# RELATORIO DE PASSAGEM — {', '.join(run_ids)}", "",
              f"PASSOU {rel['PASSOU']} de {rel['DE']}", ""]
        for k, c in C.items():
            md.append(f"- **{k}** = {c.get('ESTADO') or ('PASS' if c['PASSA'] else 'FAIL')}")
        (saida / "RELATORIO-PASSAGEM.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rel


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    verbo = argv[0] if argv else "plano"
    saida = next((Path(a.split("=", 1)[1]) for a in argv if a.startswith("--saida=")),
                 Path(os.environ.get("TEMP", "/tmp")) / "micro-coleta")
    if verbo == "plano":
        p = plano()
        print(json.dumps(p, ensure_ascii=False, indent=1))
        return 0
    if verbo == "correr":
        r = correr(autorizado="--autorizado-pelo-dono" in argv, saida=saida)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r.get("CORREU") else 2
    if verbo == "relatorio":
        ids = [a.split("=", 1)[1] for a in argv if a.startswith("--run-id=")]
        if not ids:
            print("uso: relatorio --run-id=<RUN_ID> [...]", file=sys.stderr)
            return 2
        r = relatorio(ids, saida=saida)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"escrito em {saida}", file=sys.stderr)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
