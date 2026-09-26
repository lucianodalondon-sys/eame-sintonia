"""ENSAIO da PROPOSTA 037 numa Sala DESCARTAVEL (MAESTRO-SOCIAL, 26/09). So com a LOCK-PESADO.

    ENS=<copia com os envelopes sociais> py provas/migracao_037_ensaio_descartavel.py <saida.json>

1. sobe um Postgres descartavel (`provas/a_porta_cli_liga_o_banco.Bancada` DA COPIA) e corre as migracoes dela;
2. pousa os DOIS itens reais do canario LinkedIn de 24/09 (ISPRA; ARPA VdA com universo T5 — diagnostico:
   em T2 a Admissao diz NAO, com prova) pelo orquestrador, em processo filho, rede fechada;
3. aplica a proposta `supabase/propostas/037_...sql` DESTA arvore;
4. carimba as duas unidades com `leis/identidade_do_video.marcar` (ISPRA primeiro) e grava-as com
   `admissao/video_na_sala.registar`;
5. confere: a partilha aponta para o primeiro; a vista conta 1 video em 2 itens; `NAO SEI` recusado;
   UPDATE e DELETE recusados; linha sem item na Sala recusada; `sala_de_espera` com as mesmas linhas;
6. desfaz a 037 e confere que a tabela saiu e a Sala ficou; desliga o banco.
"""
import json
import os
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENS = os.environ.get("ENS", r"C:\ens-sm")
PG = os.path.join(os.path.expanduser("~"), "orca", "pgtmp", "pgsql", "bin")
PSQL = os.path.join(PG, "psql.exe")
PROPOSTA = os.path.join(AQUI, "supabase", "propostas", "037_a_sala_diz_qual_video_e_o_mesmo.sql")
DESFAZER = os.path.join(AQUI, "supabase", "propostas", "037_desfazer.sql")
CORRIDAS = [  # (envelope REMONTADO do bruto real de 24/09 na copia, fonte na copia, universo, slug)
    ("IT-T5-2026-09-26-013213-c16b45abc2778073", "IT-T5-193", "T5", "ispra_2"),
    ("IT-T2-2026-09-26-013122-d2a62bb995556b9c", "IT-T2-170", "T5", "arpa-valle-d-aosta"),
]
PROG = ("import sys; sys.path[:0]=['.','orquestrador']; import _gavetas; import orquestrador as O; "
        "from pedido import Pedido; import persistencia, json; "
        "p=Pedido(alvo=%r, filtros={'fase':'video-linkedin','fonte':%r,"
        "'pagina':'https://www.linkedin.com/company/%s/','teto':'1','pais':'IT','universo':%r}); "
        "rt=persistencia.dependencias_do_runtime(); "
        "r=O.correr(p, so_a_porta=True, colheita_da_corrida=%r, memoria=rt.memoria, "
        "banco_do_rastro=rt.banco_do_rastro, raiz_do_armazem=rt.raiz_do_armazem); "
        "print('STATUS', r.get('STATUS'), r.get('RUN_ID'))")


def psql(url, sql, *, falhar=True):
    r = subprocess.run([PSQL, "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-d", url, "-c", sql],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if falhar and r.returncode:
        raise RuntimeError(r.stderr[-500:])
    return r


def main(saida):
    sys.path.insert(0, os.path.join(ENS, "provas"))
    sys.path[:0] = [os.path.join(AQUI, "leis"), os.path.join(AQUI, "admissao")]
    tempfile.tempdir = r"C:\soc2\sala-037"
    os.makedirs(tempfile.tempdir, exist_ok=True)
    import a_porta_cli_liga_o_banco as P                     # noqa: E402 — a Bancada da copia
    import identidade_do_video as IV                         # noqa: E402 — desta arvore
    import video_na_sala as VS                               # noqa: E402 — desta arvore
    fora = {"ENS": ENS, "PROPOSTA": os.path.relpath(PROPOSTA, AQUI)}
    b = P.Bancada()
    url = b.subir()
    try:
        cod, n, _s, _e = P._migrations(url, dict(os.environ))
        fora["MIGRACOES_DA_COPIA"] = n
        env = dict(os.environ, PYTHONUTF8="1", BANCO_DESCARTAVEL_URL=url, SINTONIA_PSQL_EXE=PSQL,
                   SINTONIA_SALA_BACKEND="POSTGRES", SINTONIA_SALA_DSN=url,
                   SINTONIA_ARMAZEM_RAIZ=os.path.join(tempfile.tempdir, "armazem"),
                   HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", NO_PROXY="localhost,127.0.0.1")
        env.pop("SINTONIA_COLLECTION_DSN", None)
        env["PATH"] = PG + os.pathsep + env.get("PATH", "")
        runs = []
        for rid, sid, uni, slug in CORRIDAS:
            x = subprocess.run([sys.executable, "-c", PROG % (uni, sid, slug, uni, rid)], cwd=ENS, env=env,
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
            linha = [l for l in x.stdout.splitlines() if l.startswith("STATUS")]
            runs.append({"ENVELOPE": rid, "SOURCE_ID": sid, "SAIDA": linha[-1] if linha else x.stderr[-300:]})
        fora["CORRIDAS"] = runs
        sala = psql(url, "select run_id||'|'||ordem||'|'||source_id from public.sala_de_espera order by pousado_em;")
        linhas = [l.split("|") for l in sala.stdout.split() if l.strip()]
        fora["SALA_ANTES"] = linhas
        psql(url, open(PROPOSTA, encoding="utf-8").read())
        fora["037_APLICADA"] = True
        # as unidades como o Scrap as carimba, a partir das observacoes REAIS dos envelopes
        registo = os.path.join(tempfile.tempdir, "VIDEOS-SOCIAIS.ndjson")
        if os.path.exists(registo):
            os.remove(registo)
        por_fonte = {s: (r, int(o)) for r, o, s in linhas}
        for rid, sid, _u, _s in CORRIDAS:
            env_json = json.load(open(os.path.join(ENS, "data", "colheita", "scrap", rid, "ENVELOPE.json"),
                                      encoding="utf-8"))
            ob = env_json["COLHEITA"][0]["OBSERVACAO"]
            run_sala, ordem = por_fonte[sid]
            [u] = IV.marcar([{"SOURCE_ID": sid, "RUN_ID": run_sala, "DOCUMENT_ID": "NAO SEI"}], [ob], registo)
            fora.setdefault("UNIDADES", []).append({k: u.get(k) for k in ("SOURCE_ID", "VIDEO_IDENTITY",
                                                                          "MESMO_VIDEO_QUE")})
            fora.setdefault("REGISTOS", []).append(VS.registar(run_sala, [(ordem, u)], dsn=url, psql=PSQL))
        q = psql(url, "select run_id||'|'||ordem||'|'||video_identity||'|'||coalesce(mesmo_video_que::text,'null') "
                      "from public.sala_de_espera_video order by registado_em;")
        fora["SALA_DE_ESPERA_VIDEO"] = [l for l in q.stdout.splitlines() if l.strip()]
        v = psql(url, "select video_identity||'|'||itens||'|'||primeiros from public.sala_de_espera_videos;")
        fora["VISTA_UM_VIDEO"] = [l for l in v.stdout.splitlines() if l.strip()]
        r0, o0 = por_fonte[CORRIDAS[0][1]]
        fora["RECUSA_NAO_SEI"] = psql(url, "insert into public.sala_de_espera_video (run_id, ordem, video_identity, "
                                           "video_identity_basis) values ('x', 0, 'NAO SEI', 'b');", falhar=False).stderr.strip()[:200]
        fora["RECUSA_UPDATE"] = psql(url, "update public.sala_de_espera_video set video_identity_basis='z' "
                                          "where run_id=%s;" % VS._lit(r0), falhar=False).stderr.strip()[:200]
        fora["RECUSA_DELETE"] = psql(url, "delete from public.sala_de_espera_video;", falhar=False).stderr.strip()[:200]
        fora["RECUSA_SEM_ITEM_NA_SALA"] = psql(url, "insert into public.sala_de_espera_video (run_id, ordem, "
                                                    "video_identity, video_identity_basis) values ('nao-existe', 0, "
                                                    "'YOUTUBE:AbCdEfGhIjK', 'b');", falhar=False).stderr.strip()[:200]
        fora["SALA_DEPOIS"] = psql(url, "select count(*) from public.sala_de_espera;").stdout.strip()
        psql(url, open(DESFAZER, encoding="utf-8").read())
        fora["DEPOIS_DE_DESFAZER"] = {
            "TABELA": psql(url, "select to_regclass('public.sala_de_espera_video') is null;").stdout.strip(),
            "VISTA": psql(url, "select to_regclass('public.sala_de_espera_videos') is null;").stdout.strip(),
            "SALA": psql(url, "select count(*) from public.sala_de_espera;").stdout.strip()}
    finally:
        subprocess.run([os.path.join(PG, "pg_ctl.exe"), "-D", b.cluster, "-w", "-m", "fast", "stop"],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        fora["BANCO_DESLIGADO"] = b.cluster
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(fora, f, ensure_ascii=False, indent=1)
    print(json.dumps(fora, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
