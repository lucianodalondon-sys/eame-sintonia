"""LOTE5-INTEGRA: mutacao dos PONTOS DE JUNCAO dos tres ramos. uso: python3 <este> <commit> <saida.txt>

Corre numa worktree DESTACADA do <commit> (a arvore de trabalho nao e tocada). Cada mutante troca UMA ancora
(tem de existir exatamente uma vez), corre o assassino e devolve o ficheiro. Vivo = o assassino passou.
Antes dos mutantes, cada assassino corre na arvore limpa e TEM de passar (senao a morte nao prova nada).

Juncoes:
  J1 coleta/linha_busca.py      busca-no-actions (--sem-portao-it, tesoura, transporte da API) x linha-busca (RAW)
  J2 architecture.declared.json comentarios (pecas C-*-COMENTARIO) x lote 4 x pecas novas da linha-busca
  J3 porta RAW -> Sala          linha_busca_raw.repousar num Postgres descartavel (a sala_de_espera_run_id_fkey)
  J4 gerados do mapa            os 15 conflitos resolvidos por REGERAR (gerado velho tem de reprovar)
"""
import json, subprocess, sys, tempfile
from pathlib import Path

COMMIT, SAIDA = sys.argv[1], Path(sys.argv[2])
REPO = Path(__file__).resolve().parents[2]
PY = sys.executable
T_LB = [PY, "tests/test_linha_busca.py"]
T_BA = [PY, "tests/test_busca_no_actions.py"]
PG = [PY, "provas/linha_busca_raw_no_postgres_descartavel.py", "/tmp/lote5-mutacao-pg"]
MAPA = ["bash", "-c", "%s system-map/scripts/generate_system_map.py >/dev/null && "
        "%s system-map/scripts/validate_system_map.py" % (PY, PY)]
VALIDA = [PY, "system-map/scripts/validate_system_map.py"]
LB, LR, DECL = "coleta/linha_busca.py", "coleta/linha_busca_raw.py", "system-map/data/architecture.declared.json"


def sem_peca(pid):
    def f(txt):
        d = json.loads(txt)
        antes = len(d["COMPONENTS"])
        d["COMPONENTS"] = [c for c in d["COMPONENTS"] if c["id"] != pid]
        assert len(d["COMPONENTS"]) == antes - 1, pid
        return json.dumps(d, ensure_ascii=False, indent=1) + "\n"
    return f


MUTANTES = [
    ("J1-a", LB, "colher --pousar volta a pousar direto na Sala (sem collection_run/raw_asset)",
     "recibo = LR.repousar([saida], corrida=corrida, pousar=True)",
     "import sala_de_espera as SE; SE.exigir_canonica(); recibo = SE.pousar(corrida, prontos)", T_LB),
    ("J1-b", LB, "--sem-portao-it deixa de se restringir a API oficial",
     "if sem_portao and not (", "if False and (", T_BA),
    ("J1-c", LB, "a tesoura da chave sai do erro da busca",
     '"ERRO": API.redigir("%s: %s" % (type(e).__name__, str(e)[:200]))',
     '"ERRO": "%s: %s" % (type(e).__name__, str(e)[:200])', T_BA),
    ("J1-d", LB, "--buscar com motor API volta ao transporte de paginas",
     'buscar = API.transporte() if ("--buscar" in argv and motor_api) else transporte_real(saida)',
     "buscar = transporte_real(saida)", T_BA),
    ("J1-e", LB, "admitir ignora o raw_asset_id real (READY sem linhagem)",
     '"RAW_ASSET_ID": raw_asset_id,', '"RAW_ASSET_ID": None,', T_LB),
    ("J3-a", LR, "pousa noutra corrida (a que nao nasceu em collection_run)",
     "pousado = pousar_fn(corrida, prontos)", 'pousado = pousar_fn(corrida + "-OUTRA", prontos)', PG),
    ("J3-b", LR, "salta o dono do RAW e inventa o id (o defeito original: run_id_fkey)",
     "recibo = preservar(run, [artefato(p) for p in paginas], lambda o: por_sha[o[\"SHA256\"]][\"DADOS\"])",
     "recibo = {\"RAW_OBSERVATIONS\": [{\"RUN_ID\": corrida, \"SHA256\": p[\"RAW\"][\"SHA256\"], "
     "\"RAW_OBSERVATION_ID\": 1} for p in paginas]}", PG),
    ("J2-a", DECL, "a peca C-PROVA-COMENTARIOS some do mapa", sem_peca("C-PROVA-COMENTARIOS"), None, MAPA),
    ("J2-b", DECL, "a peca C-LINHA-BUSCA some do mapa", sem_peca("C-LINHA-BUSCA"), None, MAPA),
    ("J4-a", "system-map/data/state.generated.json", "gerado velho (o da base 18461b92) fica no lugar",
     ("GIT", "18461b92"), None, VALIDA),
]


def corre(wt, cmd):
    r = subprocess.run(cmd, cwd=wt, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]


def main():
    wt = Path(tempfile.mkdtemp(prefix="lote5-mut-"))
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(wt), COMMIT], cwd=REPO, check=True)
    linhas, vivos = ["MUTACAO LOTE5-INTEGRA sobre %s" % COMMIT], 0
    try:
        for cmd in {tuple(m[5]) for m in MUTANTES}:
            rc, fim = corre(wt, list(cmd))
            linhas.append("LIMPO rc=%s %s :: %s" % (rc, " ".join(cmd[-2:]), fim[0][:120]))
            if rc != 0:
                raise SystemExit("o assassino falha na arvore limpa: %s" % (cmd,))
        for mid, rel, nome, ancora, troca, cmd in MUTANTES:
            f = wt / rel
            orig = f.read_text(encoding="utf-8")
            if isinstance(ancora, tuple):
                novo = subprocess.run(["git", "show", "%s:%s" % (ancora[1], rel)], cwd=REPO, capture_output=True,
                                      text=True, encoding="utf-8", check=True).stdout
            elif callable(ancora):
                novo = ancora(orig)
            else:
                assert orig.count(ancora) == 1, (mid, "ancora nao e unica/ausente")
                novo = orig.replace(ancora, troca)
            assert novo != orig, mid
            f.write_text(novo, encoding="utf-8")
            try:
                rc, fim = corre(wt, cmd)
            finally:
                f.write_text(orig, encoding="utf-8")
                subprocess.run(["git", "checkout", "-q", "--", "."], cwd=wt)
                subprocess.run(["git", "clean", "-qfd"], cwd=wt)
            morto = rc != 0
            vivos += not morto
            linhas.append("%s %-6s %s | %s | rc=%s :: %s" % ("MORTO" if morto else "VIVO ", mid, rel, nome, rc,
                                                             fim[0][:140]))
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=REPO)
    linhas.append("RESULTADO %d/%d mortos" % (len(MUTANTES) - vivos, len(MUTANTES)))
    SAIDA.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))
    return 1 if vivos else 0


if __name__ == "__main__":
    sys.exit(main())
