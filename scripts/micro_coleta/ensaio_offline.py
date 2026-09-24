"""ENSAIO OFFLINE DA MICRO-COLETA — o caminho inteiro, sem internet e sem a Sala real.

    py scripts/micro_coleta/ensaio_offline.py [--fontes=IT-T10-018,IT-T7-033] [--manter]

O QUE CORRE, E O QUE E DE MENTIRA (dito aqui, para ninguem ler isto como prova de rede)
--------------------------------------------------------------------------------------
REAL, e o mesmo codigo da corrida verdadeira:
    orquestrador -> italy_executor -> coletor Node -> ingresso -> preservar_coleta
    -> derivacao -> Admission (regua L1) -> Sala, pela porta canonica
    (o comando e `micro_coleta.comando(SOURCE_ID)`, o mesmo que `correr` lanca),
    e o relatorio de passagem e `micro_coleta.relatorio` (C1..C9), sem copia.

DE ENSAIO:
  * A REDE. O coletor baixa tudo com `curl`. Um `_curlrc` em CURL_HOME manda
    TODA ligacao (:443 e :80, qualquer host) para um servidor em 127.0.0.1, que
    serve os BYTES JA GUARDADOS dos gabaritos (detector-capa-gabarito,
    receitas-paginas) pelo host+caminho original, e da 404 ao resto. Cada
    pedido fica no registo do servidor. O `ipinfo.io` tambem cai aqui e leva
    404: o EGRESSO fica NAO SEI — nunca um «IT» fingido.
  * A BASE. Um Postgres descartavel num directorio temporario, com o nome
    `sala_italia` (o unico que o modo operacional aceita) numa porta livre,
    com as migrations pela cadeia canonica. A Sala de verdade (54330) nao e
    tocada: nenhuma variavel do ensaio aponta para ela.
  * A ARVORE. Uma worktree temporaria (git worktree --detach), para o livro
    de decisoes, o armazem e o ledger do ensaio nao sujarem o repositorio. O
    ledger do coletor (ITALY_OPS_ROOT) comeca VAZIO: com o livro versionado, as
    materias gravadas seriam puladas como «ja conhecidas».

⚠️ ARMADILHA MEDIDA: sem aspas, `connect-to = :443:...` no _curlrc e ignorado
calado (o `:` do inicio conta como separador). Com aspas funciona.

Python fica instrumentado por `medidas/corrida_sem_rede.py` (egresso Python
bloqueado e contado; loopback contado a parte). O Node e os `curl` dele ficam
provados pelo registo do servidor: pedido que nao aparece la nao existiu,
porque nao ha outro caminho (connect-to em todas as portas usadas).
"""
from __future__ import annotations

import http.server
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
import micro_coleta as MC  # noqa: E402

GABARITOS = [Path.home() / "detector-capa-gabarito", Path.home() / "receitas-paginas"]
# As materias que o lote-76 guardou (22/09, egresso IT): 97 paginas da coorte,
# incluindo os 10 itens do GABARITO-MICRO-V1. Sem elas so ha 1 materia por
# fonte, e o resto do indice da 404 — o ensaio nunca chegaria a Sala.
LIVROS_EXTRA = [Path.home() / "orca" / "workspaces" / "eame-sintonia" / "lote-76-v1"]
COORTE_G1 = ["IT-T10-018", "IT-T10-021", "IT-T10-022", "IT-T2-051",
             "IT-T7-017", "IT-T7-033", "IT-T7-041", "IT-T7-043"]
PG_BIN = Path.home() / "orca" / "pgtmp" / "pgsql" / "bin"
AUSENCIA = "NAO SEI"


def agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def porto_livre() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


# ── O SERVIDOR DE BYTES GUARDADOS ────────────────────────────────────────────
def chave(url: str) -> str:
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    caminho = p.path or "/"
    return host + caminho + (("?" + p.query) if p.query else "")


def mapa_de_fixtures(pastas=GABARITOS, livros=LIVROS_EXTRA) -> dict:
    m = {}
    for raiz in livros:
        led = raiz / "data" / "collection-ledger" / "italy" / "observations.ndjson"
        if not led.exists():
            continue
        for l in led.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            o = json.loads(l)
            f = raiz / (o.get("RAW_PATH") or "")
            if o.get("RAW_PATH") and f.exists() and str(o.get("CONTENT_TYPE", "")).startswith("text/html"):
                m.setdefault(chave(o["SOURCE_URL"]), {"FICHEIRO": str(f), "SOURCE_ID": o.get("SOURCE_ID"),
                                                       "PAPEL": "MATERIA_LOTE76", "ORIGEM": raiz.name})
    for pasta in pastas:
        man = pasta / "MANIFESTO.json"
        if not man.exists():
            continue
        for pg in json.loads(man.read_text(encoding="utf-8"))["PAGINAS"]:
            f = pasta / pg["FICHEIRO"].replace("\\", "/")
            if f.exists() and int(pg.get("HTTP") or 0) == 200:
                m.setdefault(chave(pg["URL"]), {"FICHEIRO": str(f), "SOURCE_ID": pg["SOURCE_ID"],
                                                 "PAPEL": pg.get("PAPEL_CANDIDATO"),
                                                 "ORIGEM": pasta.name})
    return m


class Servidor:
    def __init__(self, mapa: dict):
        self.mapa = mapa
        self.registo: list[dict] = []
        self.trinco = threading.Lock()
        self.servidores = []

    def _handler(self):
        srv = self

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):  # silencio no terminal; o registo e o nosso
                pass

            def _responder(self, corpo: bool):
                host = (self.headers.get("Host") or "").split(":")[0].lower()
                k = host + self.path
                alvo = srv.mapa.get(k) or srv.mapa.get(k.rstrip("/")) or srv.mapa.get(k + "/")
                estado = 200 if alvo else 404
                with srv.trinco:
                    srv.registo.append({"QUANDO": agora(), "METODO": self.command, "HOST": host,
                                        "CAMINHO": self.path, "ESTADO": estado,
                                        "SOURCE_ID": (alvo or {}).get("SOURCE_ID"),
                                        "PAPEL": (alvo or {}).get("PAPEL")})
                dados = Path(alvo["FICHEIRO"]).read_bytes() if alvo else b"fixture ausente"
                self.send_response(estado)
                self.send_header("Content-Type", "text/html; charset=utf-8" if alvo else "text/plain")
                self.send_header("Content-Length", str(len(dados)))
                self.end_headers()
                if corpo:
                    self.wfile.write(dados)

            def do_GET(self):
                self._responder(True)

            def do_HEAD(self):
                self._responder(False)

        return H

    def subir(self, porto_http: int, porto_https: int, cert: Path, chave_tls: Path):
        h = http.server.ThreadingHTTPServer(("127.0.0.1", porto_http), self._handler())
        s = http.server.ThreadingHTTPServer(("127.0.0.1", porto_https), self._handler())
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(str(cert), str(chave_tls))
        s.socket = ctx.wrap_socket(s.socket, server_side=True)
        for x in (h, s):
            threading.Thread(target=x.serve_forever, daemon=True).start()
            self.servidores.append(x)

    def descer(self):
        for x in self.servidores:
            x.shutdown()


# ── A BASE DESCARTAVEL ────────────────────────────────────────────────────
class Base:
    def __init__(self, pasta: Path):
        self.pasta = pasta
        self.porto = porto_livre()
        self.url = f"postgresql://postgres@127.0.0.1:{self.porto}/sala_italia"

    def exe(self, n):
        return str(PG_BIN / (n + ".exe" if os.name == "nt" else n))

    def subir(self, arvore: Path, env: dict):
        subprocess.run([self.exe("initdb"), "-D", str(self.pasta), "-U", "postgres",
                        "--auth=trust", "-E", "UTF8", "--no-sync"], check=True,
                       capture_output=True)
        # sem capture_output: o postmaster herda os pipes e o run() pendura
        subprocess.run([self.exe("pg_ctl"), "-D", str(self.pasta), "-o",
                        f"-p {self.porto} -h 127.0.0.1", "-l", str(self.pasta / "servidor.log"),
                        "-w", "start"], check=True, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([self.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1", "-c",
                        "create database sala_italia;",
                        f"postgresql://postgres@127.0.0.1:{self.porto}/postgres"],
                       check=True, capture_output=True)
        r = subprocess.run([shutil.which("bash") or "bash", "motor/cadeia_canonica.sh",
                            "migrations", self.url], cwd=str(arvore), env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        passes = [l for l in r.stdout.splitlines() if l.startswith("MIGRATION_") and "=PASS" in l]
        return {"CODIGO": r.returncode, "MIGRATIONS_PASS": len(passes),
                "SAIDA": r.stdout[-600:], "ERRO": r.stderr[-400:]}

    def backup(self, ficheiro: Path):
        """O mesmo comando do backup_sala.cmd (pg_dump -Fc -Z 6 --no-owner --no-privileges)."""
        subprocess.run([self.exe("pg_dump"), "-Fc", "-Z", "6", "--no-owner", "--no-privileges",
                        "-f", str(ficheiro), self.url], check=True, capture_output=True)

    def restaurar(self, ficheiro: Path) -> dict:
        """Rollback: base apagada e recriada, e o dump de antes reposto.
        Exige ninguem ligado — na Sala real, com o servico parado."""
        admin = f"postgresql://postgres@127.0.0.1:{self.porto}/postgres"
        passos = []
        for cmd in ([self.exe("dropdb"), "--if-exists", "--maintenance-db=" + admin, "sala_italia"],
                    [self.exe("createdb"), "--maintenance-db=" + admin, "sala_italia"],
                    [self.exe("pg_restore"), "--no-owner", "--no-privileges", "-d", self.url,
                     str(ficheiro)]):
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            passos.append({"CMD": " ".join(Path(cmd[0]).name if i == 0 else c for i, c in enumerate(cmd)
                                           if "postgresql://" not in c),
                           "CODIGO": r.returncode, "ERRO": r.stderr[-300:]})
        return {"PASSOS": passos, "OK": all(x["CODIGO"] == 0 for x in passos)}

    def descer(self):
        subprocess.run([self.exe("pg_ctl"), "-D", str(self.pasta), "-m", "fast", "stop"],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)


TABELAS = ("sala_de_espera", "raw_asset", "storage_object", "derived_artifact", "collection_run")


def impressao(t: str) -> str:
    """md5 do conteudo inteiro da tabela (linhas ordenadas) — contagem igual nao e conteudo igual."""
    return MC.sql(f"select md5(coalesce(string_agg(x::text, '|' order by x::text), '')) from {t} x")[0][0]


def fotografia() -> dict:
    return {t: {"LINHAS": int(MC.sql(f"select count(*) from {t}")[0][0]), "MD5": impressao(t)}
            for t in TABELAS}


def contagens() -> dict:
    """SALA_BEFORE/AFTER e as tabelas da cadeia, so SELECT, pelo cliente do instrumento."""
    out = {}
    for t in ("sala_de_espera", "raw_asset", "storage_object", "derived_artifact", "collection_run"):
        out[t] = int(MC.sql(f"select count(*) from {t}")[0][0])
    return out


# ── OS CAMPOS DO MANDATO (§22) ──────────────────────────────────────────────
def ler_ndjson(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def e_registo_de_falha(armazem: Path, storage_path: str, media_type: str) -> bool:
    """O raw e o REGISTO de uma colheita falhada. A regra e a do instrumento — uma so."""
    return MC.e_tentativa_falhada(armazem, storage_path, media_type) is not None


def cadeia_dos_documentos(run_ids) -> dict:
    """RAW separado em DOCUMENTO e REGISTO DE FALHA, e a cadeia so dos documentos.

    Medido no 1.o ensaio: cada materia que falha (404, transporte) vira uma
    OBSERVACAO de falha em JSON, guardada como raw_asset (pasta OBSERVATION).
    Contar linhas de raw_asset mistura as duas coisas, e as falhas — que nunca
    tem derivado — aparecem como «falhas de proveniencia» que nao existem.
    """
    if not run_ids:
        return {}
    em = MC._em(run_ids)
    linhas = MC.sql("select r.id, r.storage_path, r.media_type, coalesce(d.id::text,'')"
                    " from raw_asset r left join derived_artifact d on d.raw_asset_id = r.id"
                    f" where r.run_id in ({em})")
    # ⚠️ NAO E A PASTA: todo raw (documento ou falha) fica em .../OBSERVATION/.
    # O que distingue e o PROPRIO registo guardado: um JSON do coletor que diz
    # HEALTH_STATE=FAILED e SHA256 vazio (nenhum byte da fonte). Um JSON de
    # verdade (fonte de API) nao traz isso e continua documento.
    armazem = MC._armazem()
    falha = [l for l in linhas if e_registo_de_falha(armazem, l[1], l[2])]
    docs = [l for l in linhas if l not in falha]
    return {"RAW_LINHAS": len(linhas), "RAW_DOCUMENTOS": len(docs), "RAW_REGISTOS_DE_FALHA": len(falha),
            "DOCUMENTOS_SEM_DERIVADO": [l[0] for l in docs if not l[3]],
            "DERIVADOS_DE_DOCUMENTO": sorted({l[3] for l in docs if l[3]})}


def segunda_passagem(obs1: list[dict], obs2: list[dict], runs2: list[dict],
                     registo2: list[dict], antes2: dict, depois2: dict) -> dict:
    """REFETCH e FALSO-MUDOU medidos a serio: a mesma coorte, a mesma base, o mesmo
    livro do coletor, e o servidor serve EXACTAMENTE os mesmos bytes. Qualquer
    «mudou» ou «novo» para um URL cujo sha e igual ao da 1.a passagem e falso."""
    sha1 = {}
    for o in obs1:
        if o.get("RAW_SHA256"):
            sha1[o.get("SOURCE_URL")] = o["RAW_SHA256"]
    falso_mudou, falso_novo, resultados = [], [], {}
    for o in obs2:
        r = str(o.get("OBSERVATION_RESULT") or AUSENCIA)
        resultados[r] = resultados.get(r, 0) + 1
        igual = o.get("RAW_SHA256") and sha1.get(o.get("SOURCE_URL")) == o.get("RAW_SHA256")
        if igual and "CHANGED" in r:
            falso_mudou.append(o.get("SOURCE_URL"))
        if igual and r in ("NEW_DOCUMENT", "BASELINE_DOCUMENT"):
            falso_novo.append(o.get("SOURCE_URL"))

    def soma(k):
        return sum(int((x.get("contadores") or x).get(k) or 0) for x in runs2)
    return {
        "UNNECESSARY_REFETCHES": soma("UNNECESSARY_REFETCHES"),
        "FALSE_DOCUMENT_CHANGED": len(falso_mudou),
        "FALSO_NOVO_DOCUMENTO": len(falso_novo),
        "SKIPPED_KNOWN": soma("SKIPPED_KNOWN"), "REVALIDATED": soma("REVALIDATED"),
        "DETAIL_REQUESTS": soma("DETAIL_REQUESTS"), "INDEX_REQUESTS": soma("INDEX_REQUESTS"),
        "OBSERVACOES": len(obs2), "RESULTADOS": resultados,
        "PEDIDOS_AO_SERVIDOR": len(registo2),
        "RAW_NOVOS_NA_BASE": depois2["raw_asset"] - antes2["raw_asset"],
        "SALA_DELTA": depois2["sala_de_espera"] - antes2["sala_de_espera"],
        "EXEMPLOS_FALSO_MUDOU": falso_mudou[:10], "EXEMPLOS_FALSO_NOVO": falso_novo[:10]}


def campos(corridas, rel, antes, depois, runs, observacoes, registo, rede_py, cad=None) -> dict:
    """Cada campo com o VALOR, a PECA que o produziu e o ESTADO da rota ate ao instrumento."""
    ids = {c.get("RUN_ID") for c in corridas}
    rs = [r for r in runs if r.get("RUN_ID") in ids]
    obs = [o for o in observacoes if o.get("RUN_ID") in ids]
    C = rel["CRITERIOS"] if rel else {}
    adm = {}
    for f in (C.get("C7_PROPORCAO_POR_FONTE_E_CLASSE", {}).get("POR_FONTE") or {}).values():
        for k, n in f.items():
            adm[k] = adm.get(k, 0) + n

    def soma(k):
        return sum(int((r.get("contadores") or r).get(k) or 0) for r in rs) if rs else AUSENCIA

    falso_mudou = sum(1 for o in obs if str(o.get("OBSERVATION_RESULT", "")).endswith("CHANGED_IN_PLACE")
                      and o.get("MATERIAL_DIFF") is False)
    saude = {}
    for r in rs:
        for k in ("HEALTHY", "DEGRADED", "FAILED"):
            saude[k] = saude.get(k, 0) + int((r.get("contadores") or r).get(k) or 0)
    return {
        "SOURCES_ATTEMPTED": {"VALOR": len(corridas), "PECA": "micro_coleta.correr (uma corrida por fonte)",
                              "ROTA": "READ_BY_INSTRUMENT"},
        "SOURCES_SUCCESS": {"VALOR": saude.get("HEALTHY", AUSENCIA) if rs else AUSENCIA,
                            "PROCESSO_RC0": sum(1 for c in corridas if c.get("CODIGO") == 0),
                            "SAUDE": saude,
                            "PECA": "italy_pilot_collect.mjs cont[HEALTHY/DEGRADED/FAILED] -> runs.ndjson",
                            "ROTA": "HAS_OWNER_NOT_READ (o instrumento so ve o codigo de saida)"},
        "DETAIL_DOCUMENTS": {"VALOR": soma("DETAIL_NEW"), "PEDIDOS_DE_DETALHE": soma("DETAIL_REQUESTS"),
                             "PECA": "italy_pilot_collect.mjs cont.DETAIL_NEW -> runs.ndjson",
                             "ROTA": "HAS_OWNER_NOT_READ"},
        "LISTINGS_REJECTED": {"VALOR": AUSENCIA,
                              "CAPAS_DO_JUIZ_DEPOIS": len((C.get("C2_MATERIA_NAO_CAPA") or {}).get("CAPAS_DO_JUIZ") or []),
                              "PECA": "nenhuma: regras/motor_de_rota.mjs ligacoesDoIndice descarta sem contar",
                              "ROTA": "MISSING_ROUTE"},
        "RAW_CREATED": {"VALOR": (cad or {}).get("RAW_DOCUMENTOS", AUSENCIA),
                        "RAW_LINHAS_TOTAL": depois["raw_asset"] - antes["raw_asset"],
                        "RAW_REGISTOS_DE_FALHA": (cad or {}).get("RAW_REGISTOS_DE_FALHA"),
                        "OBSERVACOES_DO_RELATORIO": (C.get("C4_PROVENIENCIA_COMPLETA") or {}).get("OBSERVACOES"),
                        "PECA": "guarda/preservar_coleta.py sql_da_memoria (raw_asset)",
                        "ROTA": "READ_BY_INSTRUMENT"},
        "DERIVED_CREATED": {"VALOR": depois["derived_artifact"] - antes["derived_artifact"],
                            "PECA": "guarda/preservar_derivado.py (derived_artifact)",
                            "ROTA": "READ_BY_INSTRUMENT"},
        "ADMISSION_SIM": {"VALOR": adm.get("SIM", 0), "PECA": "admissao/admissao.py -> LIVRO-DE-DECISOES",
                          "ROTA": "READ_BY_INSTRUMENT"},
        "ADMISSION_NAO": {"VALOR": adm.get("NAO", 0), "PECA": "admissao/admissao.py", "ROTA": "READ_BY_INSTRUMENT"},
        "ADMISSION_NAO_SEI": {"VALOR": adm.get("NAO_SEI", 0), "PECA": "admissao/admissao.py",
                              "ROTA": "READ_BY_INSTRUMENT",
                              "OUTRAS": {k: v for k, v in adm.items() if k not in ("SIM", "NAO", "NAO_SEI")}},
        "SALA_BEFORE": {"VALOR": antes["sala_de_espera"], "PECA": "select count(*) from sala_de_espera",
                        "ROTA": "MISSING_ROUTE no instrumento (medido por este ensaio)"},
        "SALA_AFTER": {"VALOR": depois["sala_de_espera"], "PECA": "idem", "ROTA": "idem"},
        "SALA_DELTA": {"VALOR": depois["sala_de_espera"] - antes["sala_de_espera"],
                       "LINHAS_DA_CORRIDA_NO_RELATORIO": (C.get("C4_PROVENIENCIA_COMPLETA") or {}).get("SALA_LINHAS"),
                       "PECA": "admissao/sala_de_espera.py pousar", "ROTA": "READ_BY_INSTRUMENT (por run_id)"},
        "UNNECESSARY_REFETCHES": {"VALOR": soma("UNNECESSARY_REFETCHES"),
                                  "PECA": "italy_pilot_collect.mjs + regras/incrementalidade.mjs -> runs.ndjson",
                                  "ROTA": "HAS_OWNER_NOT_READ"},
        "FALSE_DOCUMENT_CHANGED": {"VALOR": falso_mudou if obs else AUSENCIA,
                                   "COMO": "observacoes da corrida com *CHANGED_IN_PLACE e MATERIAL_DIFF=false",
                                   "PECA": "derivado aqui do observations.ndjson; nenhum contador no codigo",
                                   "ROTA": "MISSING_ROUTE"},
        "PROVENANCE_FAILURES": {"VALOR": (len((cad or {}).get("DOCUMENTOS_SEM_DERIVADO") or [])
                                          + ((C["C4_PROVENIENCIA_COMPLETA"]["SALA_LINHAS"]
                                              - C["C4_PROVENIENCIA_COMPLETA"]["SALA_COM_CADEIA_INTEIRA"]) if C else 0)),
                                "SO_DOCUMENTOS": True,
                                "COMO_O_INSTRUMENTO_CONTA": (None if not C else
                                          (C["C4_PROVENIENCIA_COMPLETA"]["OBSERVACOES"]
                                           - C["C4_PROVENIENCIA_COMPLETA"]["COM_DECISAO"])
                                          + (C["C4_PROVENIENCIA_COMPLETA"]["SALA_LINHAS"]
                                             - C["C4_PROVENIENCIA_COMPLETA"]["SALA_COM_CADEIA_INTEIRA"])),
                                "PECA": "micro_coleta.relatorio C4 (cadeia raw->storage->derived->decisao->sala)",
                                "ROTA": "READ_BY_INSTRUMENT"},
        "NETWORK_REQUESTS": {"VALOR": soma("NETWORK_REQUESTS") if rs and "NETWORK_REQUESTS" in rs[0] else len(registo),
                             "NO_REGISTO_DO_SERVIDOR": len(registo),
                             "IPINFO": sum(1 for x in registo if x["HOST"].endswith("ipinfo.io")),
                             "EGRESSO_EXTERNO_PYTHON": rede_py.get("EGRESSO"),
                             "PECA": "italy_pilot_collect.mjs REDE.total -> runs.ndjson",
                             "ROTA": "HAS_OWNER_NOT_READ"},
        "PAID_USD": {"VALOR": 0, "COMO": "declarado pela receita (custo=gratuito); nao medido",
                     "PECA": "orquestrador.py COST_USD; collection_run.cost_usd fica NULL",
                     "ROTA": "HAS_OWNER (declarado, nao medido)"},
    }


# ── A CORRIDA ─────────────────────────────────────────────────────────────
def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    fontes = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--fontes=")), None)
    duas = "--duas-passagens" in argv
    plano_do_portao = None
    if fontes is None:
        # A coorte e a do instrumento: o que o PORTAO elege e a capacidade deixa correr.
        plano_do_portao = MC.plano()
        fontes = [l["SOURCE_ID"] for l in plano_do_portao["LINHAS"] if l["ESTADO"] == "PRONTA"]
    manter = "--manter" in argv
    provar_rollback = "--provar-rollback" in argv
    D = Path(os.environ.get("TEMP", "/tmp")) / ("micro-ensaio-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    D.mkdir(parents=True)
    saida = D / "saida"
    saida.mkdir()
    print("ENSAIO em", D, flush=True)

    # certificado local (so para o HTTPS do servidor de bytes)
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-subj", "/CN=fixture",
                    "-keyout", str(D / "chave.pem"), "-out", str(D / "cert.pem"), "-days", "2"],
                   check=True, capture_output=True)
    mapa = mapa_de_fixtures()
    srv = Servidor(mapa)
    ph, ps = porto_livre(), porto_livre()
    srv.subir(ph, ps, D / "cert.pem", D / "chave.pem")
    (D / "curl").mkdir()
    rc = f'connect-to = ":443:127.0.0.1:{ps}"\nconnect-to = ":80:127.0.0.1:{ph}"\ninsecure\n'
    for n in ("_curlrc", ".curlrc"):
        (D / "curl" / n).write_text(rc, encoding="ascii")

    arvore = D / "arvore"
    subprocess.run(["git", "worktree", "add", "--detach", str(arvore), "HEAD"], cwd=RAIZ,
                   check=True, capture_output=True)
    base = Base(D / "pg")
    env = {k: v for k, v in os.environ.items()
           if k not in ("BANCO_DESCARTAVEL_URL", "SUPABASE_DB_URL", "HTTPS_PROXY", "HTTP_PROXY")}
    env.update({"CURL_HOME": str(D / "curl"), "ITALY_OPS_ROOT": str(D / "ops"),
                "SINTONIA_COLLECTION_DSN": base.url, "SINTONIA_SALA_DSN": base.url,
                "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_PSQL_EXE": base.exe("psql"),
                # ⚠️ FORA da arvore: a bancada e OPERACIONAL (SINTONIA_COLLECTION_DSN),
                # e raiz_do_armazem_local recusa armazem operacional dentro do repo (BC4).
                "SINTONIA_ARMAZEM_RAIZ": str(D / "armazem"), "PYTHONUTF8": "1",
                "PATH": str(PG_BIN) + os.pathsep + os.environ.get("PATH", "")})
    (D / "ops").mkdir()
    resultado = {"ENSAIO": str(D), "INICIO": agora(), "FONTES": fontes,
                 "COORTE": (plano_do_portao or {}).get("COORTE", "ARGUMENTO --fontes"),
                 "BLOQUEADAS_PELA_CAPACIDADE": [{"SOURCE_ID": l["SOURCE_ID"], "FALTA": l["FALTA"]}
                                                for l in (plano_do_portao or {}).get("LINHAS", [])
                                                if l["ESTADO"] != "PRONTA"],
                 "G1_FORA_DO_PORTAO": (plano_do_portao or {}).get("G1_FORA_DO_PORTAO"),
                 "FIXTURES": len(mapa), "PORTOS": {"HTTP": ph, "HTTPS": ps, "PG": base.porto}}
    try:
        resultado["BASE"] = base.subir(arvore, env)
        os.environ.update({k: env[k] for k in ("SINTONIA_SALA_DSN", "SINTONIA_PSQL_EXE",
                                               "SINTONIA_ARMAZEM_RAIZ")})
        antes = contagens()
        corridas = []
        # ⚠️ ROLLBACK PROVADO SOBRE UMA BASE CHEIA. Repor uma base vazia prova
        # pouco; a Sala real tem linhas antes da micro. Com duas ou mais fontes,
        # a PRIMEIRA enche a base e o backup e tirado so depois dela.
        ponto_do_backup = 1 if (provar_rollback and len(fontes) > 1) else 0
        for i, s in enumerate(fontes):
            if provar_rollback and i == ponto_do_backup:
                foto_antes = fotografia()
                base.backup(D / "PRE-ENSAIO.dump")
            cmd = MC.comando(s)
            medida = saida / f"rede-{s}.json"
            lanc = [sys.executable, "medidas/corrida_sem_rede.py", f"--saida={medida}", "--"] + cmd[2:]
            t0 = time.time()
            os.environ.update({k: env[k] for k in ("ITALY_OPS_ROOT",)})
            try:
                gate = MC.GATE.avaliar(s, **MC.GATE._contexto())["MOTIVO"]
            except Exception as ex:                                    # noqa: BLE001
                gate = "ERRO:%s" % type(ex).__name__
            x = subprocess.run(lanc, cwd=str(arvore), env=env, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=1800)
            (saida / f"saida-{s}.txt").write_text(x.stdout + "\n--- ERR\n" + x.stderr, encoding="utf-8")
            m = re.search(r"CORRIDA (\S+) · (\S+)", x.stdout)
            rede = json.loads(medida.read_text(encoding="utf-8")) if medida.exists() else {}
            corridas.append({"SOURCE_ID": s, "CORREU": True, "CODIGO": x.returncode,
                             "STATUS": m.group(1) if m else AUSENCIA,
                             "RUN_ID": m.group(2) if m else AUSENCIA,
                             "SEGUNDOS": round(time.time() - t0, 1),
                             "EGRESSO_ANTES": {"PAIS": AUSENCIA}, "EGRESSO_DEPOIS": {"PAIS": AUSENCIA},
                             "GATE_NO_INSTANTE": gate,
                             "REDE_PYTHON": {k: rede.get(k) for k in ("EGRESSO", "LOOPBACK", "FILHOS")
                                             if k in rede}})
            print(s, corridas[-1]["STATUS"], corridas[-1]["RUN_ID"], "rc", x.returncode, flush=True)
        depois = contagens()
        runs = [c["RUN_ID"] for c in corridas if c["RUN_ID"] != AUSENCIA]
        if provar_rollback:
            foto_depois = fotografia()
            rest = base.restaurar(D / "PRE-ENSAIO.dump")
            foto_reposta = fotografia()
            resultado["ROLLBACK"] = {
                "METODO": "pg_dump -Fc antes; dropdb + createdb + pg_restore do dump",
                "BACKUP_DEPOIS_DE": fontes[:ponto_do_backup],
                "ANTES": foto_antes, "DEPOIS_DA_CORRIDA": foto_depois, "DEPOIS_DO_ROLLBACK": foto_reposta,
                "RESTAURO": rest,
                "IGUAL_AO_ANTES": foto_reposta == foto_antes,
                "A_CORRIDA_MUDOU_ALGO": foto_depois != foto_antes}
            print("ROLLBACK igual ao antes:", foto_reposta == foto_antes,
                  "| corrida mudou algo:", foto_depois != foto_antes, flush=True)
        # Com --provar-rollback a base ja foi reposta: nao ha corrida para o
        # relatorio ler. Os campos do mandato saem da corrida sem essa opcao.
        rel = MC.relatorio(runs, corridas=corridas,
                           livro=arvore / "data" / "samples" / "LIVRO-DE-DECISOES.json",
                           armazem=D / "armazem", saida=saida) if runs and not provar_rollback else None
        led = D / "ops" / "data" / "collection-ledger" / "italy"
        registo_da_1a = list(srv.registo)     # os campos sao da 1.a passagem; a 2.a conta a parte
        if duas:
            obs1 = ler_ndjson(led / "observations.ndjson")
            n_reg, antes2 = len(srv.registo), contagens()
            corridas2 = []
            for s in fontes:
                x = subprocess.run([sys.executable, "medidas/corrida_sem_rede.py",
                                    f"--saida={saida / ('rede2-' + s + '.json')}", "--"] + MC.comando(s)[2:],
                                   cwd=str(arvore), env=env, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=1800)
                (saida / f"saida2-{s}.txt").write_text(x.stdout + "\n--- ERR\n" + x.stderr,
                                                       encoding="utf-8")
                m = re.search(r"CORRIDA (\S+) · (\S+)", x.stdout)
                corridas2.append({"SOURCE_ID": s, "CODIGO": x.returncode,
                                  "STATUS": m.group(1) if m else AUSENCIA,
                                  "RUN_ID": m.group(2) if m else AUSENCIA})
                print("2a", s, corridas2[-1]["STATUS"], corridas2[-1]["RUN_ID"], flush=True)
            ids2 = {c["RUN_ID"] for c in corridas2}
            obs_todas = ler_ndjson(led / "observations.ndjson")
            resultado["SEGUNDA_PASSAGEM"] = {
                "CORRIDAS": corridas2,
                **segunda_passagem(obs1, [o for o in obs_todas if o.get("RUN_ID") in ids2],
                                   [r for r in ler_ndjson(led / "runs.ndjson") if r.get("RUN_ID") in ids2],
                                   srv.registo[n_reg:], antes2, contagens()),
                "SALA_ITENS_EM_MAIS_DE_UMA_CORRIDA": [x[0] for x in MC.sql(
                    "select item_id from sala_de_espera group by item_id"
                    " having count(distinct run_id) > 1 order by 1")]}
        rede_py = {"EGRESSO": sum(len(c["REDE_PYTHON"].get("EGRESSO") or [])
                                  if isinstance(c["REDE_PYTHON"].get("EGRESSO"), list)
                                  else int(c["REDE_PYTHON"].get("EGRESSO") or 0) for c in corridas)}
        resultado.update({
            "SALA_E_TABELAS_ANTES": antes, "SALA_E_TABELAS_DEPOIS": depois,
            "CORRIDAS": corridas,
            "PEDIDOS_AO_SERVIDOR": len(srv.registo),
            "PEDIDOS_POR_ESTADO": {str(k): sum(1 for r in srv.registo if r["ESTADO"] == k) for k in (200, 404)},
            "CAMPOS": campos(corridas, rel, antes, depois,
                             ler_ndjson(D / "ops" / "data" / "collection-ledger" / "italy" / "runs.ndjson"),
                             ler_ndjson(D / "ops" / "data" / "collection-ledger" / "italy" / "observations.ndjson"),
                             registo_da_1a, rede_py, cadeia_dos_documentos(runs)),
            "RELATORIO_C1_C9": ({k: (v.get("ESTADO") or ("PASS" if v["PASSA"] else "FAIL"))
                                 for k, v in rel["CRITERIOS"].items()} if rel else None),
        })
    finally:
        (saida / "PEDIDOS-AO-SERVIDOR.json").write_text(json.dumps(srv.registo, ensure_ascii=False, indent=1),
                                                        encoding="utf-8")
        srv.descer()
        base.descer()
        if not manter:
            subprocess.run(["git", "worktree", "remove", "--force", str(arvore)], cwd=RAIZ,
                           capture_output=True)
        resultado["FIM"] = agora()
        (saida / "ENSAIO-OFFLINE.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1,
                                                              default=str), encoding="utf-8")
        print("escrito:", saida / "ENSAIO-OFFLINE.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
