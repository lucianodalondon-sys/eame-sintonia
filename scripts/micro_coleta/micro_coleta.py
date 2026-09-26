"""MICRO-COLETA WEB — o instrumento unico (missao 6-PREP).

Tres verbos, e so um deles vai a rede:

    py scripts/micro_coleta/micro_coleta.py plano
        Sem rede, sem banco. A coorte e o PORTAO no instante
        (collection_gate.elegiveis), nao uma lista; para cada fonte pergunta, no
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

    py scripts/micro_coleta/micro_coleta.py relatorio --run-id=<R> [--run-id=...] [--estado=<ONDA-WEB-ESTADO.json>]
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
                     "SINTONIA_SALA_BACKEND", "SINTONIA_PSQL_EXE",
                     # ⚠️ BC4 (24/09/2026): sem ela, a micro real pousou na Sala real
                     # 4 materias com os bytes em <arvore do bot>/XX/ (residuo que a
                     # suite apaga). O orquestrador tambem recusa; aqui recusa-se
                     # antes da rede. Dono: guarda/preservar_coleta.raiz_do_armazem_local.
                     "SINTONIA_ARMAZEM_RAIZ")
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


_SOURCE_ID_DO_ATLAS = re.compile(r"^([A-Z]{2})-T\d+-\d+$")


def pais_de(source_id) -> str | None:
    """O pais DECLARADO da fonte: o prefixo do SOURCE_ID, pela regra do Atlas
    (`IT-T<territorio>-<seq>`, a mesma que o QUALIFY usa ao alocar).

    ⚠️ MEDIDO NA BC4 (24/09/2026): o comando nao punha pais no pedido e as tres
    corridas da micro real nasceram `XX-T..`, com `source_country = NAO_SEI` na
    Sala, embora a fonte fosse italiana. O pais vem da IDENTIDADE — nunca do
    egresso: o egresso medido fica registado ao lado (o coletor escreve
    VPN_COUNTRY e EGRESS_IP), e VPN_LOCATION != SOURCE_LOCATION != FACT_LOCATION.
    Sem identidade valida (candidata, `XX`, minusculas) nao se inventa: None.
    """
    m = _SOURCE_ID_DO_ATLAS.match(source_id or "")
    return m.group(1) if m and m.group(1) != "XX" else None


def comando(source_id: str) -> list[str]:
    u = universo_de(source_id)
    cmd = [sys.executable, "orquestrador/orquestrador.py", apelido_de(u) or u,
           "--filtro", f"fonte={source_id}", "--filtro", f"universo={u}"]
    pais = pais_de(source_id)
    if pais:
        cmd += ["--filtro", f"pais={pais}"]
    return cmd


# ── FILTROS DE OUTRAS MISSOES ───────────────────────────────────────────────
# ⚠️ ESTE BLOCO JA MENTIU, E CALADO. A 6-PREP lia «curadoria/RELEVANCIA-POR-
# FONTE-V1.json» com a forma {"LINHAS": [...]}, e tratava ficheiro AUSENTE como
# «sem opiniao». Nome e forma eram palpite meu; a 3b real escreveu outro ficheiro
# com outra forma. Resultado medido pelo coordenador: filtro da 3b = nenhum, sem
# aviso. O filtro da M3 tinha o mesmo buraco (ficheiro que nao existe nesta linha).
#
#     FILTRO DECLARADO E AUSENTE = FALHA ALTA. NUNCA «SEM OPINIAO».
#
# Cada filtro le-se da BRANCH DO DONO por `git show` (sem merge), pelo NOME DA
# BRANCH e nao por um hash fixo — um REF fixo mata o filtro futuro em silencio.
# O hash resolvido fica no plano. Um filtro so BLOQUEIA; nunca promove.
class FiltroAusente(Exception):
    """Um filtro declarado nao se conseguiu ler. Nao e «sem opiniao»."""


FILTROS = [
    {"ID": "M3-ROTAS", "ATIVO": True, "REF": "origin/rotas-elegiveis-v1",
     "DADOS": "curadoria/ROTAS-ELEGIVEIS-V1.json"},
    {"ID": "M3b-RELEVANCIA", "ATIVO": True, "REF": "origin/relevancia-elegiveis-v1",
     "DADOS": "curadoria/RELEVANCIA-ELEGIVEIS-V1.json",
     "DECISAO": "RELATORIO-RELEVANCIA-ELEGIVEIS.md"},
    # A 3c (regua T2/T12) ainda nao publicou. O ponto de leitura existe e esta
    # DESLIGADO de proposito: o nome da branch e do ficheiro vem do coordenador
    # ou da branch publicada — nao se adivinha outra vez. Ligar = pôr ATIVO,
    # REF, DADOS e escrever o leitor; ate la o plano diz que ela falta.
    {"ID": "M3c-REGUA-T2-T12", "ATIVO": False, "REF": None, "DADOS": None,
     "NOTA": "aguarda publicacao da missao 3c; nome por confirmar"},
]
ENTRA_3B = "ENTRA_NA_MICRO"
_LINHA_3B = re.compile(r"^\|\s*(IT-T\d+-\d+)\b[^|]*\|.*\|\s*\*\*([A-Z_]+)\*\*\s*\|[^|]*\|\s*$")


def git_show(ref: str, caminho: str) -> tuple[str, str]:
    """(texto, hash) de `ref:caminho`. Qualquer falha e FiltroAusente."""
    try:
        h = subprocess.run(["git", "rev-parse", "--short", ref], cwd=RAIZ,
                           capture_output=True, text=True, timeout=30)
        r = subprocess.run(["git", "show", f"{ref}:{caminho}"], cwd=RAIZ,
                           capture_output=True, timeout=60)
    except Exception as ex:                                    # noqa: BLE001
        raise FiltroAusente(f"{ref}:{caminho}: {type(ex).__name__}: {ex}") from ex
    if h.returncode != 0 or r.returncode != 0:
        raise FiltroAusente(f"{ref}:{caminho}: " + (r.stderr or b"").decode("utf-8", "replace")[-200:].strip())
    return r.stdout.decode("utf-8"), h.stdout.strip()


def ler_rotas(ler=git_show) -> dict:
    f = FILTROS[0]
    txt, h = ler(f["REF"], f["DADOS"])
    try:
        linhas = json.loads(txt)["LINHAS"]
        vered = {l["SOURCE_ID"]: l["VEREDITO"] for l in linhas}
    except (ValueError, KeyError, TypeError) as ex:
        raise FiltroAusente(f"{f['ID']}: forma inesperada ({type(ex).__name__}: {ex})") from ex
    if not vered:
        raise FiltroAusente(f"{f['ID']}: zero linhas — vazio nao e «tudo aprovado»")
    return {"HASH": h, "POR_FONTE": vered}


def ler_relevancia(ler=git_show) -> dict:
    """A decisao por fonte da 3b, com regra escrita.

    O JSON da 3b NAO tem veredito de coorte: tem AMOSTRAS com o DECIDIR de cada
    uma. A decisao e do DONO da 3b e esta na coluna «coorte» do relatorio dela
    (ex.: a myfruit ENTRA com as duas amostras NAO_SEI, pelo historico 5/9 na
    Sala; a feira escolar FICA_FORA contra dois SIM). Derivar das amostras
    daria outra coorte — e seria a minha decisao a passar por cima da dele.

    REGRA: ENTRA_NA_MICRO passa; qualquer outra decisao bloqueia; fonte que o
    JSON mediu e o relatorio nao decide (ou o inverso) = FiltroAusente.
    Fonte que a 3b nao mediu de todo bloqueia com RELEVANCIA_NAO_MEDIDA.
    As contagens das amostras vao ao lado, para quem quiser ver a divergencia.
    """
    f = FILTROS[1]
    dados, h = ler(f["REF"], f["DADOS"])
    rel, _ = ler(f["REF"], f["DECISAO"])
    try:
        fontes = json.loads(dados)["FONTES"]
        amostras = {x["SOURCE_ID"]: [a["DECIDIR"]["RESULTADO"] for a in x.get("AMOSTRAS") or []]
                    for x in fontes}
    except (ValueError, KeyError, TypeError) as ex:
        raise FiltroAusente(f"{f['ID']}: forma inesperada ({type(ex).__name__}: {ex})") from ex
    decisao = {}
    for linha in rel.splitlines():
        m = _LINHA_3B.match(linha.strip())
        if m:
            decisao[m.group(1)] = m.group(2)
    if not amostras or set(decisao) != set(amostras):
        raise FiltroAusente(
            f"{f['ID']}: o relatorio decide {sorted(set(decisao) - set(amostras))} a mais e "
            f"{sorted(set(amostras) - set(decisao))} a menos do que o JSON mediu")
    return {"HASH": h, "POR_FONTE": decisao, "AMOSTRAS": amostras}


def filtros_externos(ler=git_show) -> dict:
    """Le TODOS os filtros ativos, ou rebenta. Nao ha meio-termo."""
    return {"M3-ROTAS": ler_rotas(ler), "M3b-RELEVANCIA": ler_relevancia(ler),
            "DESLIGADOS": [x["ID"] for x in FILTROS if not x["ATIVO"]]}


# ── A COORTE VEM DO PORTAO ──────────────────────────────────────────────────
# ⚠️ NAO USAR LISTA FIXA (lei do mandato). Ate a A2 a coorte era o ficheiro
# COORTE-PROPOSTA.json (14 fontes) e so 1 das 8 do funil G1 passava: a lista
# e o filtro 3b ficaram atras da decisao D8 do dono. A coorte e agora o que o
# portao canonico (curadoria/collection_gate.elegiveis) diz NO INSTANTE, e
# cada fonte READY que ele recusa aparece com o motivo dele.
G1 = RAIZ / "scripts" / "desbloqueio" / "FUNIL-APOS-ENSAIO-G1.json"


def coorte_do_portao(ctx: dict) -> tuple[list[str], list[dict]]:
    """(elegiveis, fora): a coorte e o porque de cada READY que ficou de fora."""
    inv = GATE.inventario(ctx=ctx)
    ids = [l["SOURCE_ID"] for l in inv if l["COLLECTION_ELIGIBLE"]]
    fora = [{"SOURCE_ID": l["SOURCE_ID"], "STATE": l["STATE"], "MOTIVO": l["MOTIVO"],
             "PORQUE": l["PORQUE"]} for l in inv if not l["COLLECTION_ELIGIBLE"]]
    return ids, fora


def g1_fora_do_portao(ids: list[str], ctx: dict) -> list[dict]:
    """Comparacao, nao coorte: as fontes que o funil G1 passou e o portao de hoje nao elege."""
    if not G1.exists():
        return [{"SOURCE_ID": AUSENCIA, "PORQUE": "funil G1 ausente nesta arvore"}]
    g1 = json.loads(G1.read_text(encoding="utf-8")).get("PASSAM_TUDO") or []
    out = []
    for s in g1:
        if s not in ids:
            v = GATE.avaliar(s, **ctx)
            out.append({"SOURCE_ID": s, "STATE": v["STATE"], "MOTIVO": v["MOTIVO"],
                        "PORQUE": v["PORQUE"]})
    return out


def plano(ids: list[str] | None = None, *, ctx: dict | None = None,
          ler=git_show) -> dict:
    ctx = ctx if ctx is not None else GATE._contexto()
    do_portao, fora_do_portao = coorte_do_portao(ctx)
    origem = "ARGUMENTO" if ids else "PORTAO (collection_gate.elegiveis)"
    ids = ids or do_portao
    contratos = {f["SOURCE_ID"]: f for f in
                 json.loads(CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}
    fx = filtros_externos(ler)                      # rebenta se faltar um
    rotas = fx["M3-ROTAS"]["POR_FONTE"]
    relevancia = fx["M3b-RELEVANCIA"]["POR_FONTE"]
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
        rv = rotas.get(s)
        if rv and rv not in ("ROUTE_PROVEN",):
            falta.append(f"ROTA:{rv}")
        # ⚠️ A RELEVANCIA NAO BARRA A FONTE (D2 + D8 do dono, 23/09): Riunite,
        # Chianti e Balsamico FICAM; a Admission recusa o marketing e a noticia
        # util segue por REROUTE. Decidir relevancia por fonte seria descartar
        # sem ler. A 3b fica ao lado, lida com o mesmo rigor, para quem quiser ver.
        rl = relevancia.get(s)
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
                       "ROTA_M3": rotas.get(s, "NAO_MEDIDA"),
                       "RELEVANCIA_3b": rl or "NAO_MEDIDA",
                       "AMOSTRAS_3b": fx["M3b-RELEVANCIA"]["AMOSTRAS"].get(s),
                       "ESTADO": "PRONTA" if not falta else "BLOQUEADA",
                       "FALTA": falta,
                       "COMANDO": " ".join(comando(s)[1:])})
    return {"GERADO_EM": agora(), "GATE": GATE.CONTRATO,
            "PAINEL_DO_GATE": GATE.painel(ctx=ctx),
            "COORTE": origem,
            "FORA_DO_PORTAO": fora_do_portao,
            "G1_FORA_DO_PORTAO": g1_fora_do_portao(ids, ctx),
            "RELEVANCIA": "informativa: D2/D8 — decide-se por item na Admission (REROUTE), nao por fonte",
            "FILTROS": {"M3-ROTAS": fx["M3-ROTAS"]["HASH"],
                        "M3b-RELEVANCIA": fx["M3b-RELEVANCIA"]["HASH"],
                        "DESLIGADOS": fx["DESLIGADOS"]},
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
    """EGR (24/09): o pais pelo DONO — superficie/rede.py, consenso de 3 verificadores
    com cache de 3 min. Nenhum consumidor pergunta a um servico diretamente (o
    ipinfo.io em 429 parou tudo das 13:05 as 15:05). O IP nao sai do dono."""
    import importlib.util as _u, os as _os
    _s = _u.spec_from_file_location("rede_egresso", _os.path.join(str(RAIZ), "superficie", "rede.py"))
    _r = _u.module_from_spec(_s)
    _s.loader.exec_module(_r)
    e = _r.egresso()
    pais = e["EGRESS_COUNTRY_CODE"] if e["EGRESS_COUNTRY_CODE"] != "UNKNOWN" else None
    return {"PAIS": pais or AUSENCIA, "VOTOS": e["VOTOS"], "QUANDO": agora()}


def precondicoes(ambiente=None) -> list[str]:
    env = os.environ if ambiente is None else ambiente
    falta = [v for v in VARIAVEIS_DA_SALA if not env.get(v)]
    if env.get("SINTONIA_SALA_BACKEND") and env["SINTONIA_SALA_BACKEND"] != "POSTGRES":
        falta.append("SINTONIA_SALA_BACKEND!=POSTGRES (a Sala cairia em FICHEIRO)")
    if env.get("BANCO_DESCARTAVEL_URL"):
        falta.append("BANCO_DESCARTAVEL_URL presente (ModosEmConflito)")
    return falta


def correr(ids=None, *, autorizado=False, lancar=None, egresso=medir_egresso,
           ambiente=None, consulta=sql, saida: Path | None = None,
           ler=git_show) -> dict:
    if not autorizado:
        return {"CORREU": False, "PORQUE": "falta --autorizado-pelo-dono"}
    falta = precondicoes(ambiente)
    if falta:
        return {"CORREU": False, "PORQUE": "precondicoes", "FALTA": falta}
    p = plano(ids, ler=ler)                  # FiltroAusente sobe: nada se lanca
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


GABARITO = AQUI / "GABARITO-MICRO-V1.json"
_PALAVRAS = {
    "en": {"the", "and", "of", "to", "is", "for", "with", "that", "are", "on"},
    "it": {"il", "della", "di", "che", "per", "con", "sono", "gli", "nel", "delle"},
    "pt": {"o", "da", "do", "que", "para", "com", "os", "das", "dos", "uma"},
}


# C9-IDIOMA (25/09): o limiar era so `>= 20`. No MICRO-V3 duas noticias italianas da ARPAE
# (RAW 1436: 17 palavras «it» contra 1; RAW 1437: 9 contra 0) sairam NAO SEI e o C9 contou-as
# como «estrangeiro sem sinal». Medido nos 758 textos extraidos do armazem (25/09): quem passa
# de 20 fica igual; abaixo, ha um VAO — nenhum texto entre 5 e 8 — e por baixo dele so restos de
# 30-40 palavras (menus, cabecalhos). A banda curta conta so com DOMINIO CLARO: pelo menos
# IDIOMA_MINIMO_CURTO palavras da lingua e IDIOMA_DOMINIO vezes a segunda. 11 contra 6 continua
# NAO SEI; 4 contra 0 tambem. A regra C9 nao muda: muda so o que o detector consegue ler.
IDIOMA_MINIMO = 20
IDIOMA_MINIMO_CURTO = 8
IDIOMA_DOMINIO = 3


def idioma(texto: str) -> str:
    """Leitura grosseira e declarada: a lingua cujas dez palavras mais comuns
    aparecem mais. Serve para CONTAR (C9), nunca para decidir entrada."""
    pal = re.findall(r"[a-zà-ú]+", texto.lower())
    conta = {lg: sum(1 for p in pal if p in ws) for lg, ws in _PALAVRAS.items()}
    lg = max(conta, key=conta.get)
    if conta[lg] >= IDIOMA_MINIMO:
        return lg
    segunda = max(v for k, v in conta.items() if k != lg)
    if conta[lg] >= IDIOMA_MINIMO_CURTO and conta[lg] >= IDIOMA_DOMINIO * segunda:
        return lg
    return AUSENCIA


def _armazem() -> Path:
    r = os.environ.get("SINTONIA_ARMAZEM_RAIZ")
    return Path(r) if r else Path.home() / "sintonia-sala-italia" / "armazem"


# ── DOCUMENTO != TENTATIVA FALHADA ─────────────────────────────────────────
# ⚠️ Medido no ensaio offline (A1): cada materia que falha (404, transporte)
# vira um REGISTO da tentativa, em JSON, guardado como raw_asset na MESMA pasta
# (OBSERVATION) dos documentos, e sem derivado. Contar linhas de raw_asset deu
# «30 RAW» para 1 documento e «29 falhas de proveniencia» que nao existem.
# O que distingue e o PROPRIO registo: o coletor escreve HEALTH_STATE=FAILED e
# SHA256 vazio (nenhum byte da fonte). Nada se apaga: conta-se a parte, com motivo.
def e_tentativa_falhada(armazem: Path, storage_path: str, media_type: str) -> dict | None:
    """O motivo, se o raw e o registo de uma colheita falhada; None se e documento."""
    if "json" not in (media_type or ""):
        return None
    try:
        o = json.loads((Path(armazem) / storage_path).read_text(encoding="utf-8"))
    except Exception:                                          # noqa: BLE001
        return None
    if isinstance(o, dict) and o.get("HEALTH_STATE") == "FAILED" and not o.get("SHA256"):
        return {"RESULTADO": o.get("OBSERVATION_RESULT") or AUSENCIA,
                "MOTIVO": str(o.get("motivo") or AUSENCIA)[:120],
                "URL": o.get("SOURCE_URL") or AUSENCIA}
    return None


# ── OS CONTADORES DO COLETOR ───────────────────────────────────────────────
# O coletor Node conta o que so ele ve (saude real da fonte, detalhes, refetch,
# pedidos a rede) e escreve-o em runs.ndjson — o italy_executor so devolve o
# codigo de saida. Sem isto, SUCCESS = «o processo saiu com 0», e uma fonte
# FAILED no coletor sai SUCCESS (medido na A1).
def ledger_do_coletor() -> Path:
    return Path(os.environ.get("ITALY_OPS_ROOT") or RAIZ) / "data" / "collection-ledger" / "italy"


def contadores_do_coletor(run_ids: list[str], pasta: Path | None = None) -> dict:
    p = (pasta or ledger_do_coletor()) / "runs.ndjson"
    somas: dict = {}
    achados = set()
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            r = json.loads(l)
            if r.get("RUN_ID") in run_ids:
                achados.add(r["RUN_ID"])
                for k, v in (r.get("contadores") or {}).items():
                    if isinstance(v, (int, float)):
                        somas[k] = somas.get(k, 0) + v
    return {"RUNS_NO_LEDGER": len(achados), "RUNS_SEM_LEDGER": sorted(set(run_ids) - achados),
            "SOURCES_SUCCESS": somas.get("HEALTHY", 0), "SOURCES_DEGRADED": somas.get("DEGRADED", 0),
            "SOURCES_FAILED": somas.get("FAILED", 0), "DETAIL_DOCUMENTS": somas.get("DETAIL_NEW", 0),
            "DETAIL_REQUESTS": somas.get("DETAIL_REQUESTS", 0),
            "NETWORK_REQUESTS": somas.get("DETAIL_REQUESTS", 0) + somas.get("INDEX_REQUESTS", 0),
            "UNNECESSARY_REFETCHES": somas.get("UNNECESSARY_REFETCHES", 0),
            "SKIPPED_KNOWN": somas.get("SKIPPED_KNOWN", 0), "LEDGER": str(p)}


def relatorio(run_ids: list[str], *, corridas: list | None = None,
              consulta=sql, livro: Path = LIVRO, armazem: Path | None = None,
              saida: Path | None = None, ledger: Path | None = None) -> dict:
    em = _em(run_ids)
    armazem = armazem or _armazem()
    obs = consulta(
        "select r.id, r.source_id, r.media_type, r.storage_path, r.storage_object_id,"
        " coalesce(d.id::text,''), r.captured_at::text, r.run_id,"
        " coalesce(r.source_url,''), coalesce(d.storage_path,'')"
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
    # ⚠️ O MESMO ITEM DUAS VEZES NA SALA. Medido na 2.a passagem do ensaio (A2):
    # uma materia REVALIDADA e igual (SEEN_AGAIN) atravessou a Admission outra vez
    # e pousou de novo, com outra observacao e outro run_id — 4 itens em dobro.
    # A Sala real ja tem itens do lote-76; conta-se aqui, sem corrigir (a Sala e
    # a Admission tem outro dono).
    ja_na_sala = consulta(
        "select s.item_id, count(distinct s.run_id) from sala_de_espera s"
        f" where s.item_id in (select item_id from sala_de_espera where run_id in ({em}))"
        f" and s.run_id not in ({em}) group by s.item_id")
    decisoes = [d for d in json.loads(Path(livro).read_text(encoding="utf-8"))["DECISOES"]
                if d.get("corrida") in run_ids]
    por_item = {d["item"]: d for d in decisoes}

    falhadas = []
    for o in list(obs):
        f = e_tentativa_falhada(armazem, o[3], o[2])
        if f:
            falhadas.append({"RAW": o[0], "SOURCE_ID": o[1], **f})
    ids_falhados = {x["RAW"] for x in falhadas}
    todas_as_linhas = len(obs)
    obs = [o for o in obs if o[0] not in ids_falhados]      # daqui em diante: so DOCUMENTOS

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
            "TENTATIVAS_FALHADAS_A_PARTE": len(falhadas),
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
    # ── C8 · AS DUAS PERGUNTAS (lei D2 do dono, 2026-09-23) ──────────────────
    # A Admission so responde UNIVERSE_MATCH. SINTONIA_RELEVANT e outra
    # pergunta: mede-se contra o gabarito validado (por URL) e, para o resto,
    # fica na folha CLASSES.tsv para uma pessoa. As duas nunca se somam.
    gab = {g["DOCUMENTO"]: g for g in json.loads(GABARITO.read_text(encoding="utf-8"))["ITENS"]}
    no_gab = []
    for o in obs:
        g = gab.get(o[8] if len(o) > 8 else "")
        if g:
            v = por_item.get(f"derived:{o[5]}", {}).get("resultado", AUSENCIA)
            no_gab.append({"N": g["N"], "SOURCE_ID": o[1], "ADMISSION": v,
                           "ESPERADO": g["ESPERADO"], "UNIVERSE_MATCH": g["UNIVERSE_MATCH"],
                           "SINTONIA_RELEVANT": g["SINTONIA_RELEVANT"], "ACTION": g["ACTION"],
                           "UNIVERSO_ACERTA": (v == "SIM") == (g["UNIVERSE_MATCH"] == "YES"),
                           "SIM_ERRADO": v == "SIM" and g["UNIVERSE_MATCH"] == "NO",
                           "RELEVANTE_PERDIDO": v != "SIM" and g["SINTONIA_RELEVANT"] == "YES"})
    C["C8_DUAS_PERGUNTAS"] = {
        "ITENS_DO_GABARITO": no_gab,
        # binario ENTRA/NAO ENTRA (NAO_SEI conta como NAO ENTRA) e estrito
        # (NAO_SEI conta como pergunta nao respondida). Os dois, lado a lado.
        "UNIVERSE_MATCH_ACERTOS_ENTRA_OU_NAO": f"{sum(x['UNIVERSO_ACERTA'] for x in no_gab)}/{len(no_gab)}",
        "UNIVERSE_MATCH_ACERTOS_ESTRITO": f"{sum(1 for x in no_gab if x['ADMISSION'] == ('SIM' if x['UNIVERSE_MATCH'] == 'YES' else 'NAO'))}/{len(no_gab)}",
        "SIM_ERRADO": sum(x["SIM_ERRADO"] for x in no_gab),
        "RELEVANTE_AO_SINTONIA_FORA_DA_SALA": [x["N"] for x in no_gab if x["RELEVANTE_PERDIDO"]],
        "REROUTE": [(x["N"], x["ACTION"]) for x in no_gab if x["ACTION"].startswith("REROUTE")],
        "ESTADO": "PASS" if no_gab and not any(x["SIM_ERRADO"] for x in no_gab)
                  else "NAO_SE_APLICA" if not no_gab else "FAIL",
        "PASSA": bool(no_gab) and not any(x["SIM_ERRADO"] for x in no_gab)}

    # ── C9 · IDIOMA (lei D3): idioma sozinho nao pode dar NAO_SEI ─────────────
    # Contado A PARTE. Um item em lingua estrangeira que ficou NAO_SEI sem
    # nenhum sinal e uma violacao a contar — mesmo que a Admission nao mude.
    idiomas, violacoes = {}, []
    for o in obs:
        dp = o[9] if len(o) > 9 else ""
        f = armazem / dp if dp else None
        if not f or not f.exists():
            continue
        lg = idioma(f.read_text(encoding="utf-8", errors="replace"))
        idiomas[lg] = idiomas.get(lg, 0) + 1
        d = por_item.get(f"derived:{o[5]}", {})
        if lg not in ("it", "pt") and d.get("resultado") == "NAO_SEI"                 and not (d.get("evidencia") or {}).get("palavras"):
            violacoes.append({"RAW": o[0], "SOURCE_ID": o[1], "IDIOMA": lg})
    C["C9_IDIOMA_NAO_DA_NAO_SEI"] = {
        "IDIOMAS": idiomas, "NAO_SEI_ESTRANGEIRO_SEM_SINAL": violacoes,
        "CONTADOS": len(violacoes), "PASSA": not violacoes}

    motivos: dict = {}
    for x in falhadas:
        motivos[x["RESULTADO"]] = motivos.get(x["RESULTADO"], 0) + 1
    rel = {"GERADO_EM": agora(), "RUN_IDS": run_ids, "CRITERIOS": C,
           "CONTAGENS": {"RAW_LINHAS": todas_as_linhas, "RAW_CREATED": len(obs),
                         "TENTATIVAS_FALHADAS": len(falhadas),
                         "TENTATIVAS_POR_RESULTADO": motivos,
                         "TENTATIVAS": falhadas[:200],
                         "COLETOR": contadores_do_coletor(run_ids, ledger),
                         "SALA_ITENS_JA_NA_SALA_POR_OUTRA_CORRIDA": len(ja_na_sala),
                         "SALA_DUPLICADOS_EXEMPLOS": [x[0] for x in ja_na_sala][:20]},
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


def corridas_do_estado(estado: dict, ids: list[str] | None = None) -> list[dict]:
    """As corridas no formato que `relatorio` le (C1: EGRESSO_ANTES/DEPOIS; C3: GATE_NO_INSTANTE),
    a partir do que o condutor da onda grava por fonte (`ferramentas/big_collection/onda_web.py`:
    GATE, EGRESSO [antes, depois]).

    C9-IDIOMA (25/09): o MICRO-V3 teve C1 e C3 FAIL no relatorio da onda com as 6 corridas a IT,IT
    e ELIGIBLE no estado — o relatorio pedido pela linha de comando nao recebia as corridas e media
    uma lista vazia. Isto so traduz; nao inventa: o que o estado nao diz fica None, e o criterio,
    que e o mesmo, reprova."""
    out = []
    for f in estado.get("FONTES", []):
        if not f.get("RUN_ID") or (ids is not None and f["RUN_ID"] not in ids):
            continue
        eg = f.get("EGRESSO") or [None, None]
        out.append({"SOURCE_ID": f.get("SOURCE_ID"), "RUN_ID": f["RUN_ID"], "CORREU": f.get("CORREU"),
                    "STATUS": f.get("STATUS"), "GATE_NO_INSTANTE": f.get("GATE"),
                    "EGRESSO_ANTES": {"PAIS": eg[0] if len(eg) > 0 else None},
                    "EGRESSO_DEPOIS": {"PAIS": eg[1] if len(eg) > 1 else None}})
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    verbo = argv[0] if argv else "plano"
    saida = next((Path(a.split("=", 1)[1]) for a in argv if a.startswith("--saida=")),
                 Path(os.environ.get("TEMP", "/tmp")) / "micro-coleta")
    if verbo == "plano":
        try:
            p = plano()
        except FiltroAusente as ex:
            print(f"FILTRO_AUSENTE — o plano NAO corre sem ele: {ex}", file=sys.stderr)
            return 3
        print(json.dumps(p, ensure_ascii=False, indent=1))
        return 0
    if verbo == "correr":
        try:
            r = correr(autorizado="--autorizado-pelo-dono" in argv, saida=saida)
        except FiltroAusente as ex:
            print(f"FILTRO_AUSENTE — nada foi lancado: {ex}", file=sys.stderr)
            return 3
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r.get("CORREU") else 2
    if verbo == "relatorio":
        ids = [a.split("=", 1)[1] for a in argv if a.startswith("--run-id=")]
        estado = next((Path(a.split("=", 1)[1]) for a in argv if a.startswith("--estado=")), None)
        corridas = None
        if estado:
            corridas = corridas_do_estado(json.loads(estado.read_text(encoding="utf-8")), ids or None)
            ids = ids or [c["RUN_ID"] for c in corridas]
        if not ids:
            print("uso: relatorio --run-id=<RUN_ID> [...] [--estado=<ONDA-WEB-ESTADO.json>]", file=sys.stderr)
            return 2
        r = relatorio(ids, corridas=corridas, saida=saida)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"escrito em {saida}", file=sys.stderr)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
