"""Ensaio do conserto D24 da ponte numa COPIA fiel do vivo. Nunca toca no vivo."""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path

VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
REPO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/ponte-d24-v1")
NOVO = sys.argv[1]
FILA = "candidatas/FONTES-CANDIDATAS.json"
TOCADOS_PELA_PONTE = {FILA, "curadoria/BRIDGE-LEDGER-V1.json", "curadoria/LIFECYCLE-LEDGER-V1.json",
                      "curadoria/LIFECYCLE-QUEUE-V1.json"}
E = Path(tempfile.gettempdir()) / "pd24-ensaio-copia"
_PROVA = re.compile(r"(PROVA_IDENTIDADE=|IDENTIDADE: a pagina oficial da pessoa )https?://\S+")


def git(cwd, *a, check=True):
    return subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True, check=check, encoding="utf-8").stdout


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_conteudo(p):
    return hashlib.sha256(Path(p).read_bytes().replace(bytes([13, 10]), bytes([10]))).hexdigest()


def rastreados(raiz):
    return {f: sha_conteudo(Path(raiz) / f) for f in git(raiz, "ls-files").splitlines() if (Path(raiz) / f).is_file()}


def fila(p):
    return {c["CANDIDATA_ID"]: c for c in json.loads((Path(p) / FILA).read_text(encoding="utf-8"))["CANDIDATAS"]}


PROD = git(VIVO, "rev-parse", "--short", "HEAD").strip()
print("ENSAIO PONTE D24 — copia fiel do vivo %s; NOVO = %s" % (PROD, NOVO))
livros = [l[3:] for l in git(VIVO, "status", "--porcelain").splitlines() if l.startswith(" M ")]
foto = Path(tempfile.mkdtemp(prefix="pd24-livros-"))
for f in livros:
    (foto / f).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(VIVO / f, foto / f)
vivo_sha = rastreados(VIVO)
if E.exists():
    git(REPO, "worktree", "remove", "--force", str(E), check=False)
git(REPO, "worktree", "add", "--detach", str(E), PROD)
for f in livros:
    shutil.copy2(foto / f, E / f)
copia = rastreados(E)
dif = [f for f in vivo_sha if vivo_sha[f] != copia.get(f) and f not in livros] + \
      [f for f in livros if sha(foto / f) != sha(E / f)]
antes = fila(E)
pb_antes = {k for k, c in antes.items() if c["ESTADO"] == "POLICY_BLOCK"}
d24_bloq = {k for k in pb_antes if _PROVA.search(antes[k].get("NOTA") or "")}
print("1 COPIA FIEL: %d ficheiros, %d diferentes do vivo | livros %d | POLICY_BLOCK %d (dos quais com prova D24: %d)"
      % (len(copia), len(dif), len(livros), len(pb_antes), len(d24_bloq)))

# 2. instalar e correr a ponte UMA vez na copia (o que o robo faria na volta seguinte)
git(E, "checkout", "-f", "--detach", NOVO)
for f in livros:
    shutil.copy2(foto / f, E / f)
env = dict(os.environ, HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", PYTHONUTF8="1")
r = subprocess.run(["py", "curadoria/ponte_candidatas.py"], cwd=str(E), capture_output=True, text=True, env=env, encoding="utf-8")
m = json.loads(r.stdout[r.stdout.index("{"):])
depois = fila(E)
pb_depois = {k for k, c in depois.items() if c["ESTADO"] == "POLICY_BLOCK"}
sem_motivo = [k for k in pb_depois if not (depois[k].get("MOTIVO_DO_BLOQUEIO") or "").strip()]
outros = [f for f in livros if f not in TOCADOS_PELA_PONTE and sha(E / f) != sha(foto / f)]
mudaram = {k for k in antes if antes[k] != depois.get(k)}
q = json.loads((E / "curadoria/LIFECYCLE-QUEUE-V1.json").read_text(encoding="utf-8"))["TAREFAS"]
novas_q = [t for t in q if t["SOURCE_ID"] in d24_bloq and t["TASK_TYPE"] == "QUALIFY"]
print("2 INSTALAR + 1 volta da ponte: D24_REAVALIADAS=%s | POLICY_BLOCK %d -> %d | sem motivo %d | candidatas alteradas %d (%s)"
      % (m.get("D24_REAVALIADAS"), len(pb_antes), len(pb_depois), len(sem_motivo), len(mudaram),
         "so as D24" if mudaram <= d24_bloq else "OUTRAS TAMBEM"))
print("  estado das 25 na porta:", dict(Counter(depois[k]["ESTADO"] for k in d24_bloq)),
      "| tarefas QUALIFY delas:", len(novas_q), "| livros fora da ponte alterados:", len(outros), outros[:3])
t = subprocess.run(["py", "-m", "unittest",
                    "tests.test_fila_italia_decisoes.TestOsTermosProibemEProvamSe",
                    "tests.test_fila_italia_decisoes"],
                   cwd=str(E), capture_output=True, text=True, env=env, encoding="utf-8")
falhas = [l for l in t.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
print("  testes da fila na copia instalada:", (t.stderr.strip().splitlines() or ["?"])[-1],
      "| test_nova_sem_nota em falha:", sum("test_nova_sem_nota" in l for l in falhas), "| falhas:", falhas[:4])
r2 = subprocess.run(["py", "curadoria/ponte_candidatas.py"], cwd=str(E), capture_output=True, text=True, env=env, encoding="utf-8")
m2 = json.loads(r2.stdout[r2.stdout.index("{"):])
print("  segunda volta da ponte: D24_REAVALIADAS=%s TAREFAS_CRIADAS=%s (idempotente se 0/0)" % (m2.get("D24_REAVALIADAS"), m2.get("TAREFAS_CRIADAS")))

# 3. desfazer
git(E, "checkout", "-f", "--detach", PROD)
for f in livros:
    shutil.copy2(foto / f, E / f)
volta = rastreados(E)
dif2 = [f for f in copia if copia[f] != volta.get(f)]
print("3 DESFAZER: ficheiros diferentes da copia fiel de antes: %d %s" % (len(dif2), dif2[:3]))
git(REPO, "worktree", "remove", "--force", str(E))
shutil.rmtree(foto, ignore_errors=True)
ok = (not dif and m.get("D24_REAVALIADAS") == len(d24_bloq) and len(pb_depois) == len(pb_antes) - len(d24_bloq)
      and not sem_motivo and mudaram <= d24_bloq and not outros and len(novas_q) == len(d24_bloq)
      and not any("test_nova_sem_nota" in l for l in falhas) and m2.get("D24_REAVALIADAS") == 0
      and m2.get("TAREFAS_CRIADAS") == 0 and not dif2)
print("RESULTADO:", "PASS" if ok else "FAIL")
