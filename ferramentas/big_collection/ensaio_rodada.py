# -*- coding: utf-8 -*-
"""ENSAIO A SECO DE UMA RODADA DA 4.a ONDA — o disparador inteiro, sem internet e sem a Sala real.

    py ferramentas/big_collection/ensaio_rodada.py [--rodada=1] [--manter] [--so-cenarios=W,A,B]

O QUE E REAL (o mesmo codigo do dia):
    rodadas.py (plano, janela 24 h, portao, prova-teto, relatorio)
    -> onda_web.py --correr --fontes=<as da rodada> (coorte CONGELADA do commit, livro do teto novo)
    -> micro_coleta.correr -> orquestrador -> italy_executor -> coletor Node (curl)
    -> RAW -> DERIVED -> Admission -> Sala, e `micro_coleta relatorio --estado=` (C1..C9)

O QUE E DE ENSAIO (dito aqui para ninguem ler isto como prova de rede):
  * OS SITES: o servidor de bytes do `scripts/micro_coleta/ensaio_offline.py` (importado, nao
    copiado), mais as paginas que a Sala real ja guarda destas fontes (SELECT so leitura em
    raw_asset: source_url -> ficheiro no armazem). O resto leva 404. Todo o curl vai para ele
    (`connect-to` em :80 e :443, `noproxy "*"` no _curlrc); cada pedido fica no registo.
  * O PYTHON NAO SAI: HTTP(S)_PROXY para 127.0.0.1:9 (porta morta) em todo o ambiente.
  * A VPN: o portao REAL (`rede.py --portao-de-egresso IT --sem-cache`) falha sozinho, porque o
    Python nao sai (cenario A: nada sai). Para a rodada correr (cenario B), a cache do egresso
    (`SINTONIA_EGRESSO_CACHE`) e escrita por este ensaio com 3 votos IT, para ESTE ambiente, e
    refrescada a cada minuto; o portao da rodada e simulado e diz que o e. C1 = PASS aqui e
    SIMULADO, nunca prova de IT.
  * A BASE: Postgres descartavel `sala_italia` numa porta livre, com as migrations pela cadeia.
  * A ARVORE: worktree temporaria de HEAD, com os livros vivos COPIADOS (so leitura do vivo) e a
    fila do robo esvaziada na copia (D41.3).

CENARIOS:
  W  janela 24 h, lida dos livros REAIS das ondas: tentar agora -> PARA JANELA_24H, 0 pedidos
  A  portao real sem rede -> PARA EGRESSO_ANTES, 0 pedidos, Sala igual
  B  a rodada inteira -> prova-teto, relatorio C1..C9, reconciliacao Sala x livros
  R  backup antes de B, restauro depois: md5 das 5 tabelas igual ao antes
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
import ensaio_offline as EO                                       # noqa: E402 — servidor, base, contagens
import micro_coleta as MC                                         # noqa: E402

VIVO = Path.home() / "orca" / "workspaces" / "eame-sintonia" / "source-curator-service-v1"
ONDAS_REAIS = Path.home() / "sintonia-sala-italia" / "ondas"
SALA_REAL_DSN = Path.home() / "sintonia-sala-italia" / "SALA_DSN.txt"
ARMAZEM_REAL = Path.home() / "sintonia-sala-italia" / "armazem"
HISTORICO = [ONDAS_REAIS / "ONDA2-WEB-20260925-0812" / "ONDA-WEB-ESTADO.json",
             ONDAS_REAIS / "ONDA3-WEB-20260925-1934" / "ONDA-WEB-ESTADO.json"]
MORTA = "http://127.0.0.1:9"
# Os verificadores do egresso (superficie/rede.py) tambem vao pelo curl: no ensaio caem no servidor
# local e levam 404. Contam-se A PARTE: nao sao pedidos aos sites.
VERIFICADORES_DE_EGRESSO = {"ipwho.is", "ip-api.com", "ifconfig.co", "ipinfo.io"}


def agora() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def livros_vivos() -> list[str]:
    """Os ficheiros que o vivo tem diferentes do commit (os livros): so `git status`, so leitura."""
    r = subprocess.run(["git", "-C", str(VIVO), "status", "--porcelain"], capture_output=True, text=True)
    return [l[3:].strip() for l in r.stdout.splitlines() if l and not l.startswith("??")]


def paginas_da_sala_real(fontes: list[str]) -> dict:
    """source_url -> ficheiro no armazem real, das fontes dadas. SELECT com transaccao so leitura."""
    dsn = SALA_REAL_DSN.read_text(encoding="utf-8").strip()
    ids = ",".join("'%s'" % s for s in fontes)
    # separador TAB: \x1c..\x1e sao quebras de linha para o str.splitlines() do Python
    r = subprocess.run([str(EO.PG_BIN / "psql.exe"), "-X", "-A", "-t", "-F", "\t", "-c",
                        "select source_id, source_url, storage_path from raw_asset where source_id in (%s) "
                        "and media_type ilike '%%html%%' and preserved" % ids, dsn],
                       capture_output=True, text=True, encoding="utf-8",
                       env=dict(os.environ, PGOPTIONS="-c default_transaction_read_only=on"))
    m = {}
    for l in r.stdout.replace("\r", "").splitlines():
        p = l.split("\t")
        if len(p) == 3 and (ARMAZEM_REAL / p[2]).exists():
            m.setdefault(EO.chave(p[1]), {"FICHEIRO": str(ARMAZEM_REAL / p[2]), "SOURCE_ID": p[0],
                                          "PAPEL": "MATERIA_DA_SALA_REAL", "ORIGEM": "armazem"})
    return m


class CacheIT:
    """A VPN simulada: a cache do egresso com 3 votos IT, para ESTE ambiente, sempre fresca."""

    def __init__(self, arvore: Path, env: dict, ficheiro: Path):
        sys.path.insert(0, str(arvore / "superficie"))
        import rede                                               # noqa: E402 — o dono da regra
        self.R, self.env, self.f, self.parar = rede, env, ficheiro, threading.Event()
        votos = []
        for nome, _url, campo, sucesso in rede.VERIFICADORES:       # o corpo que cada servico daria
            corpo = {campo: "IT"}
            if sucesso:
                corpo[sucesso[0]] = sucesso[1]
            votos.append(rede.voto(nome, (200, json.dumps(corpo)), campo, sucesso))
        self.m = {"VOTOS": votos, "TELEMETRIA": []}
        pais, _ = rede.consenso(self.m["VOTOS"])
        if pais != "IT":
            raise SystemExit("CACHE_IT: o consenso de 3 votos IT deu %s — a simulacao nao vale" % pais)

    def gravar(self):
        self.R.gravar_cache(dict(self.m, MEDIDO_EM_EPOCH=time.time(),
                                 # a chave do ambiente REAL (os.environ): no Windows `http_proxy` e
                                 # `HTTP_PROXY` sao a mesma variavel, num dict nao — a chave saia outra
                                 CHAVE_DO_AMBIENTE=self.R.chave_do_ambiente()), str(self.f))

    def ligar(self):
        self.gravar()

        def laco():
            while not self.parar.wait(60):
                self.gravar()
        threading.Thread(target=laco, daemon=True).start()

    def desligar(self):
        self.parar.set()
        if self.f.exists():
            self.f.unlink()


def aos_sites(registo: list[dict]) -> list[dict]:
    return [r for r in registo if r["HOST"] not in VERIFICADORES_DE_EGRESSO]


def por_dominio(registo: list[dict], PT) -> dict:
    out = {}
    for r in aos_sites(registo):
        d = PT.dominio_registavel(r["HOST"])
        out[d] = out.get(d, 0) + 1
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    n = int(next((a.split("=", 1)[1] for a in argv if a.startswith("--rodada=")), "1"))
    cenarios = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--so-cenarios=")),
                    ["W", "A", "B", "R"])
    manter = "--manter" in argv
    D = Path(os.environ.get("TEMP", "/tmp")) / ("rodada-ensaio-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    D.mkdir(parents=True)
    out = {"ENSAIO": str(D), "INICIO": agora(), "RODADA": n, "HEAD": subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip(),
        "CENARIOS": {}}
    print("ENSAIO em", D, flush=True)

    # ── a arvore, com os livros vivos copiados e a fila esvaziada ──────────
    arvore = D / "arvore"
    subprocess.run(["git", "worktree", "add", "--detach", str(arvore), "HEAD"], cwd=RAIZ, check=True,
                   capture_output=True)
    copiados = {}
    for f in livros_vivos():
        (arvore / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(VIVO / f, arvore / f)
        copiados[f] = __import__("hashlib").sha256((VIVO / f).read_bytes()).hexdigest()
    fila = arvore / "curadoria" / "LIFECYCLE-QUEUE-V1.json"
    if fila.exists():
        q = json.loads(fila.read_text(encoding="utf-8"))
        out["FILA_ESVAZIADA_NA_COPIA"] = len(q.get("TAREFAS") or [])
        q["TAREFAS"] = []
        fila.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")
    out["LIVROS_COPIADOS_DO_VIVO"] = copiados

    # ── o ambiente: Python sem saida, curl para o servidor, Sala descartavel ─
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-subj", "/CN=fixture",
                    "-keyout", str(D / "chave.pem"), "-out", str(D / "cert.pem"), "-days", "2"],
                   check=True, capture_output=True)
    base = EO.Base(D / "pg")
    ph, ps = EO.porto_livre(), EO.porto_livre()
    (D / "curl").mkdir()
    rc = f'connect-to = ":443:127.0.0.1:{ps}"\nconnect-to = ":80:127.0.0.1:{ph}"\ninsecure\nnoproxy = "*"\n'
    for nome in ("_curlrc", ".curlrc"):
        (D / "curl" / nome).write_text(rc, encoding="ascii")
    (D / "ops").mkdir()
    env = {k: v for k, v in os.environ.items() if k not in ("BANCO_DESCARTAVEL_URL", "SUPABASE_DB_URL",
                                                            "SINTONIA_TETO_ONDA", "NO_PROXY", "no_proxy")}
    env.update({"HTTP_PROXY": MORTA, "HTTPS_PROXY": MORTA, "http_proxy": MORTA, "https_proxy": MORTA,
                "ALL_PROXY": MORTA, "CURL_HOME": str(D / "curl"), "ITALY_OPS_ROOT": str(D / "ops"),
                "SINTONIA_COLLECTION_DSN": base.url, "SINTONIA_SALA_DSN": base.url,
                "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_PSQL_EXE": base.exe("psql"),
                "SINTONIA_ARMAZEM_RAIZ": str(D / "armazem"), "SINTONIA_EGRESSO_CACHE": str(D / "egresso.json"),
                "PYTHONUTF8": "1", "PATH": str(EO.PG_BIN) + os.pathsep + os.environ.get("PATH", "")})

    sys.path.insert(0, str(arvore / "ferramentas" / "big_collection"))
    sys.path.insert(0, str(arvore / "provas"))
    srv = cache = None
    try:
        # ── o plano da rodada, na arvore com os livros vivos (sem rede) ─────
        so = D / "so-plano"
        r = subprocess.run([sys.executable, "ferramentas/big_collection/rodadas.py", "--so-plano",
                            "--base=%s" % so, "--historico=" + ",".join(map(str, HISTORICO)),
                            "--livros-do-dia=%s" % ONDAS_REAIS], cwd=arvore, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        plano = json.loads((so / "RODADAS-SO-PLANO.json").read_text(encoding="utf-8"))
        rod = next(x for x in plano["RODADAS"] if x["RODADA"] == n)
        fontes = [f["SOURCE_ID"] for f in rod["FONTES"]]
        out["PLANO"] = {"COORTE_SHA256": plano["COORTE_SHA256"], "COORTE_ESTADO": plano["COORTE_ESTADO"],
                        "N_RODADAS": plano["N_RODADAS"], "RODADA": rod, "SO_PLANO_SAIDA": r.stdout[-1500:]}
        print("rodada %d: %d fontes, %d pedidos previstos" % (n, len(fontes), rod["PEDIDOS_PREVISTOS"]), flush=True)

        # ── os sites de ensaio ───────────────────────────────────────────────
        mapa = EO.mapa_de_fixtures()
        extra = paginas_da_sala_real(fontes)
        for k, v in extra.items():
            mapa.setdefault(k, v)
        srv = EO.Servidor(mapa)
        srv.subir(ph, ps, D / "cert.pem", D / "chave.pem")
        out["FIXTURES"] = {"TOTAL": len(mapa), "DA_SALA_REAL": len(extra)}

        out["BASE"] = base.subir(arvore, env)
        os.environ.clear()
        os.environ.update(env)                                   # daqui em diante, o ensaio E este ambiente
        sha = plano["COORTE_SHA256"]
        import rodadas as RD                                      # noqa: E402 — o da arvore
        import prova_teto_dominio as PT                           # noqa: E402

        def corrida_cli(base_ondas: Path, *extra_args) -> dict:
            antes_reg, antes_sala = len(srv.registo), EO.contagens()
            x = subprocess.run([sys.executable, "ferramentas/big_collection/rodadas.py", "--correr",
                                "--sha256=" + sha, "--base=%s" % (base_ondas / "ONDA4"), "--rodada=%d" % n,
                                "--historico=" + ",".join(map(str, HISTORICO)), *extra_args],
                               cwd=arvore, env=env, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=3600)
            est_f = base_ondas / "ONDA4" / "RODADAS-ESTADO.json"
            est = json.loads(est_f.read_text(encoding="utf-8")) if est_f.exists() else {}
            reg = (est.get("RODADAS") or {}).get(str(n), {})
            novos = srv.registo[antes_reg:]
            return {"CODIGO": x.returncode, "ESTADO": reg.get("ESTADO"), "PORQUE": reg.get("PORQUE"),
                    "PEDIDOS_AOS_VERIFICADORES_DE_EGRESSO": len(novos) - len(aos_sites(novos)),
                    "ABRE_EM": reg.get("ABRE_EM"), "DOMINIOS_NA_JANELA": len(reg.get("DOMINIOS_NA_JANELA") or {}),
                    "EGRESSO_ANTES": reg.get("EGRESSO_ANTES"),
                    "PEDIDOS_AO_SERVIDOR": len(aos_sites(novos)),
                    "SALA_ANTES": antes_sala, "SALA_DEPOIS": EO.contagens(),
                    "SAIDA": (x.stdout + x.stderr)[-800:]}

        if "W" in cenarios:                                       # janela: livros reais, agora
            c = corrida_cli(D / "ondasW", "--livros-do-dia=%s" % ONDAS_REAIS)
            c["PASSA"] = c["PORQUE"] == "JANELA_24H" and c["PEDIDOS_AO_SERVIDOR"] == 0 \
                and c["SALA_ANTES"] == c["SALA_DEPOIS"]
            out["CENARIOS"]["W_JANELA_24H"] = c
            print("W", c["ESTADO"], c["PORQUE"], c["ABRE_EM"], "pedidos", c["PEDIDOS_AO_SERVIDOR"], flush=True)

        if "A" in cenarios:                                       # VPN a falhar: portao real sem rede
            (D / "ondasA").mkdir()
            c = corrida_cli(D / "ondasA", "--livros-do-dia=%s" % (D / "ondasA"))
            c["PASSA"] = c["PORQUE"] == "EGRESSO_ANTES" and c["PEDIDOS_AO_SERVIDOR"] == 0 \
                and c["SALA_ANTES"] == c["SALA_DEPOIS"]
            out["CENARIOS"]["A_VPN_FALHA"] = c
            print("A", c["ESTADO"], c["PORQUE"], "pedidos", c["PEDIDOS_AO_SERVIDOR"], flush=True)

        if "B" in cenarios:                                       # a rodada inteira
            cache = CacheIT(arvore, env, D / "egresso.json")
            cache.ligar()
            if "R" in cenarios:
                foto_antes = EO.fotografia()
                base.backup(D / "PRE-RODADA.dump")
            bB = D / "ondasB" / "ONDA4"
            bB.mkdir(parents=True)
            RD.gravar(bB, RD.PLANO_F, plano)
            antes_reg, sala0 = len(srv.registo), EO.contagens()
            portoes = []

            def portao_simulado():
                v = {"PASSA": True, "PAIS": "IT", "SIMULADO": "cache de egresso escrita pelo ensaio (3 votos IT)"}
                portoes.append(v)
                return v
            t0 = time.time()
            est = RD.correr_rodadas(bB, sha, plano, onda=RD.onda_real, portao=portao_simulado,
                                    relatorio=RD.relatorio_real,
                                    ledger=D / "ops" / "data" / "collection-ledger" / "italy" / "runs.ndjson",
                                    historico=[str(h) for h in HISTORICO], rodada=n)
            seg = round(time.time() - t0)
            reg = est["RODADAS"][str(n)]
            pasta = Path(reg["PASTA"])
            ow = json.loads((pasta / "ONDA-WEB-ESTADO.json").read_text(encoding="utf-8")) \
                if (pasta / "ONDA-WEB-ESTADO.json").exists() else {}
            relf = pasta / "relatorio" / "RELATORIO-PASSAGEM.json"
            rel = json.loads(relf.read_text(encoding="utf-8")) if relf.exists() else {}
            livro = json.loads((pasta / "TETO-ONDA.json").read_text(encoding="utf-8"))["PEDIDOS_POR_DOMINIO"] \
                if (pasta / "TETO-ONDA.json").exists() else {}
            servidor = por_dominio(srv.registo[antes_reg:], PT)
            sala1 = EO.contagens()
            runs = [f.get("RUN_ID") for f in ow.get("FONTES", []) if f.get("RUN_ID")]
            ids = ",".join("'%s'" % x for x in runs) or "''"
            cr = int(MC.sql("select count(*) from collection_run where run_id in (%s)" % ids)[0][0])
            ra = int(MC.sql("select count(*) from raw_asset where run_id in (%s)" % ids)[0][0])
            se = int(MC.sql("select count(*) from sala_de_espera where run_id in (%s)" % ids)[0][0])
            from collections import Counter
            out["CENARIOS"]["B_RODADA"] = {
                "SEGUNDOS": seg, "ESTADO": reg.get("ESTADO"), "PORQUE": reg.get("PORQUE"),
                "PROVA_TETO": reg.get("PROVA_TETO"), "CODIGO_DA_ONDA": reg.get("CODIGO_DA_ONDA"),
                "CODIGO_DO_RELATORIO": reg.get("CODIGO_DO_RELATORIO"), "PORTOES_SIMULADOS": len(portoes),
                "ONDA_PAROU": ow.get("PAROU"),
                "FONTES_POR_STATUS": dict(Counter(f.get("STATUS") or f.get("PORQUE_NAO_CORREU") for f in ow.get("FONTES", []))),
                "PEDIDOS_AO_SERVIDOR_POR_DOMINIO": servidor,
                "MAXIMO_NO_SERVIDOR_POR_DOMINIO": max(servidor.values() or [0]),
                "LIVRO_DO_TETO": livro, "LIVRO_IGUAL_AO_SERVIDOR": livro == servidor,
                "PEDIDOS_404": sum(1 for x in aos_sites(srv.registo[antes_reg:]) if x["ESTADO"] == 404),
                "PEDIDOS_AOS_VERIFICADORES_DE_EGRESSO": len(srv.registo[antes_reg:]) - len(aos_sites(srv.registo[antes_reg:])),
                "RELATORIO": {"PASSOU": rel.get("PASSOU"), "DE": rel.get("DE"),
                              "CRITERIOS": {k: (v.get("ESTADO") or ("PASS" if v.get("PASSA") else "FAIL"))
                                            for k, v in (rel.get("CRITERIOS") or {}).items()}},
                "SALA_ANTES": sala0, "SALA_DEPOIS": sala1,
                "RECONCILIACAO": {"RUN_IDS_NO_ESTADO": len(runs), "COLLECTION_RUN_NA_SALA": cr,
                                  "RAW_NA_SALA": ra, "SALA_DE_ESPERA_DESTAS_CORRIDAS": se,
                                  "SALA_DELTA": sala1["sala_de_espera"] - sala0["sala_de_espera"],
                                  "RAW_DELTA": sala1["raw_asset"] - sala0["raw_asset"],
                                  "BATE": se == sala1["sala_de_espera"] - sala0["sala_de_espera"]
                                  and ra == sala1["raw_asset"] - sala0["raw_asset"]}}
            b = out["CENARIOS"]["B_RODADA"]
            print("B", b["ESTADO"], b["PORQUE"], b["SEGUNDOS"], "s | servidor max", b["MAXIMO_NO_SERVIDOR_POR_DOMINIO"],
                  "| relatorio", b["RELATORIO"]["PASSOU"], "/", b["RELATORIO"]["DE"], "| sala", sala0, "->", sala1, flush=True)
            if "R" in cenarios:
                foto_depois = EO.fotografia()
                rest = base.restaurar(D / "PRE-RODADA.dump")
                foto_reposta = EO.fotografia()
                out["CENARIOS"]["R_BACKUP_RESTAURO"] = {
                    "RESTAURO": rest, "A_RODADA_MUDOU_A_SALA": foto_depois != foto_antes,
                    "IGUAL_AO_ANTES": foto_reposta == foto_antes, "ANTES": foto_antes, "REPOSTA": foto_reposta}
                print("R igual ao antes:", foto_reposta == foto_antes, flush=True)
    finally:
        if cache:
            cache.desligar()
        if srv:
            srv.descer()
        try:
            base.descer()
        except Exception:                                         # noqa: BLE001
            pass
        out["FIM"] = agora()
        (D / "ENSAIO-RODADA.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str),
                                              encoding="utf-8")
        if not manter:
            subprocess.run(["git", "worktree", "remove", "--force", str(arvore)], cwd=RAIZ, capture_output=True)
    print("RESULTADO", D / "ENSAIO-RODADA.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
