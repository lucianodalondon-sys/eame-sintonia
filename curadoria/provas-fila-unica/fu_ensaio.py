"""Ensaio da instalacao da fila unica numa COPIA fiel do vivo. Nunca toca no vivo."""
import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
REPO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/fila-unica-v1")
PROD, NOVO = "5ba9647e", sys.argv[1]
BASE_SHA = "16fd6077111a058065e71dec30c3456681246276104c312b7b67e5db50e98872"
FILA = "candidatas/FONTES-CANDIDATAS.json"
E = Path(tempfile.gettempdir()) / "fu-ensaio-copia"


def git(cwd, *a, check=True):
    return subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True, check=check,
                          encoding="utf-8").stdout


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_conteudo(p):
    # conteudo sem o fim de linha: o vivo tem ficheiros em CRLF que o git conta como iguais ao LF
    return hashlib.sha256(Path(p).read_bytes().replace(bytes([13, 10]), bytes([10]))).hexdigest()


def hashes_rastreados(raiz):
    return {f: sha_conteudo(Path(raiz) / f) for f in git(raiz, "ls-files").splitlines() if (Path(raiz) / f).is_file()}


def fila(p):
    return json.loads((Path(p) / FILA).read_text(encoding="utf-8"))["CANDIDATAS"]


print("ENSAIO FILA UNICA — copia fiel do vivo; NOVO =", NOVO)
assert git(VIVO, "rev-parse", "--short", "HEAD").strip() == PROD, "o vivo nao esta em %s" % PROD
livros = [l[3:] for l in git(VIVO, "status", "--porcelain").splitlines() if l.startswith(" M ")]
nao_rastreados = [l[3:] for l in git(VIVO, "status", "--porcelain").splitlines() if l.startswith("??")]
print("livros do vivo (rastreados e alterados):", len(livros), "| pastas nao rastreadas (dados colhidos, nao mexidas):", len(nao_rastreados))
foto = Path(tempfile.mkdtemp(prefix="fu-livros-"))
for f in livros:
    (foto / f).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(VIVO / f, foto / f)
foto_sha = {f: sha(foto / f) for f in livros}
vivo_sha = hashes_rastreados(VIVO)

# 1. copia fiel
if E.exists():
    git(REPO, "worktree", "remove", "--force", str(E), check=False)
git(REPO, "worktree", "add", "--detach", str(E), PROD)
for f in livros:
    shutil.copy2(foto / f, E / f)
copia_sha = hashes_rastreados(E)
dif = [f for f in vivo_sha if vivo_sha[f] != copia_sha.get(f) and f not in livros] + \
      [f for f in livros if sha(foto / f) != sha(E / f)]
print("1 COPIA FIEL: ficheiros rastreados", len(copia_sha), "| diferentes do vivo no conteudo (fim de linha nao conta; livros byte a byte):", len(dif), dif[:5])
antes = fila(E)
print("  fila ANTES:", len(antes), "| sha256 da fila", sha(E / FILA)[:16], "== fotografia" if sha(E / FILA) == BASE_SHA else "!= fotografia")

# 2. instalar (na copia)
assert sha(E / FILA) == BASE_SHA, "a fila viva mudou desde a fotografia: correr juntar_filas.py sobre ela"
git(E, "checkout", "-f", "--detach", NOVO)
for f in livros:
    if f != FILA:
        shutil.copy2(foto / f, E / f)
depois = fila(E)
A = {c["CANDIDATA_ID"]: c for c in antes}
D = {c["CANDIDATA_ID"]: c for c in depois}
ids = [c["CANDIDATA_ID"] for c in depois]
sys.path.insert(0, str(E / "candidatas"))
from fonte_nova import normalizar  # noqa: E402
urls = [normalizar(c["URL"]) for c in depois]
iguais = [f for f in livros if f != FILA and sha(E / f) == foto_sha[f]]
print("2 INSTALAR: livros iguais ao vivo", len(iguais), "de", len(livros) - 1,
      "| fila DEPOIS", len(depois), "(+%d)" % (len(depois) - len(antes)),
      "| antigas alteradas", sum(1 for k in A if A[k] != D.get(k)),
      "| CAND repetido", len(ids) - len(set(ids)), "| URL repetido", len(urls) - len(set(urls)))
env = dict(os.environ, HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", PYTHONUTF8="1")
t = subprocess.run(["py", "-m", "unittest", "tests.test_fila_italia_decisoes.TestOsTermosProibemEProvamSe"],
                   cwd=str(E), capture_output=True, text=True, env=env, encoding="utf-8")
print("  guarda D24 na copia instalada:", (t.stderr.strip().splitlines() or ["?"])[-1],
      "|", [l for l in t.stdout.splitlines() if "PROXIMA_EXPANSAO" in l][-1:])

# 3. desfazer
git(E, "checkout", "-f", "--detach", PROD)
for f in livros:
    shutil.copy2(foto / f, E / f)
volta = hashes_rastreados(E)
dif2 = [f for f in copia_sha if copia_sha[f] != volta.get(f)]
print("3 DESFAZER: ficheiros diferentes da copia fiel de antes:", len(dif2), dif2[:5],
      "| fila", len(fila(E)), "| sha256", sha(E / FILA)[:16])
git(REPO, "worktree", "remove", "--force", str(E))
shutil.rmtree(foto, ignore_errors=True)
ok = not dif and len(iguais) == len(livros) - 1 and not dif2 and len(ids) == len(set(ids)) \
    and len(urls) == len(set(urls)) and t.returncode == 0
print("RESULTADO:", "PASS" if ok else "FAIL")
