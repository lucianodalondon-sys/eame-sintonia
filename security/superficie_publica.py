#!/usr/bin/env python3
"""QUE FICHEIROS O DEPLOY PUBLICA? — o dono desta pergunta.

Antes disto, tres coisas sabiam responder a meio: `vercel.json` dizia o
directorio, `.vercelignore` dizia as exclusoes, e a prova era um `curl` contra
o site depois do deploy. Nenhuma delas respondia ANTES.

    BUILD INPUT != PUBLIC OUTPUT.
    E quem nao sabe calcular a diferenca so descobre depois de publicar.

Este modulo calcula a superficie publicada a partir das duas unicas fontes que
mandam — `outputDirectory` do vercel.json e as regras do .vercelignore — e
devolve-a como dados. Todos os ratchets de exposicao consomem daqui. Nenhum
deles mantem a sua propria lista de ficheiros.

    ONE CONCEPT -> ONE OWNER.

Semantica do .vercelignore, igual a do .gitignore: a ULTIMA regra que casa
decide, `!` re-inclui, `/` inicial ancora na raiz, `/` final so casa
directorios. A ordem importa, e por isso as regras sao avaliadas por ordem e
nao como um conjunto.

Uso:
    python3 security/superficie_publica.py            # lista os caminhos
    python3 security/superficie_publica.py --json     # + bytes e totais
"""
import json, os, re, subprocess, sys, pathlib

# A raiz e substituivel para que as provas possam construir um repositorio
# minimo e atacar o calculo. Um dono da fronteira publicada que so sabe
# responder sobre a sua propria arvore nao pode ser posto a prova.
RAIZ = pathlib.Path(os.environ.get("SINTONIA_RATCHET_RAIZ") or
                    pathlib.Path(__file__).resolve().parent.parent)


def _regex(padrao):
    """Traduz um padrao estilo gitignore para regex, sem depender de fnmatch:
    `*` nao pode atravessar `/`, e `**` pode."""
    i, out = 0, []
    while i < len(padrao):
        c = padrao[i]
        if padrao.startswith("**/", i):
            out.append("(?:.*/)?"); i += 3
        elif padrao.startswith("**", i):
            out.append(".*"); i += 2
        elif c == "*":
            out.append("[^/]*"); i += 1
        elif c == "?":
            out.append("[^/]"); i += 1
        else:
            out.append(re.escape(c)); i += 1
    return "".join(out)


def regras(texto):
    """Le o .vercelignore e devolve (regex, negada, so_directorio), por ordem."""
    saida = []
    for linha in texto.splitlines():
        linha = linha.rstrip()
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        negada = linha.startswith("!")
        if negada:
            linha = linha[1:]
        so_dir = linha.endswith("/")
        linha = linha.rstrip("/")
        ancorada = linha.startswith("/")
        corpo = _regex(linha.lstrip("/"))
        # Ancorado: casa a partir da raiz. Nao ancorado: casa em qualquer nivel.
        prefixo = "" if ancorada else "(?:.*/)?"
        saida.append((re.compile(f"^{prefixo}{corpo}(?:/.*)?$"), negada, so_dir))
    return saida


def ignorado(caminho, rs):
    """A ULTIMA regra que casa decide. Sem isto, `!` dentro de um directorio
    excluido pareceria funcionar quando nao funciona."""
    veredito = False
    for rx, negada, _so_dir in rs:
        if rx.match(caminho):
            veredito = not negada
    return veredito


def rastreados(raiz):
    """Os ficheiros que o deploy veria. Num repositorio, e o que o Git rastreia:
    o Vercel envia a arvore versionada, nao os rascunhos locais. Fora de um
    repositorio — nas provas — cai para a arvore de ficheiros."""
    out = subprocess.run(["git", "ls-files", "-z"], cwd=raiz,
                         capture_output=True, text=True)
    if out.returncode == 0 and out.stdout:
        return [p for p in out.stdout.split("\0") if p]
    return sorted(str(f.relative_to(raiz)) for f in raiz.rglob("*")
                  if f.is_file() and ".git/" not in str(f.relative_to(raiz)))


def superficie(raiz=RAIZ):
    cfg = json.loads((raiz / "vercel.json").read_text(encoding="utf-8"))
    saida = cfg.get("outputDirectory", "").strip("/")
    if not saida:
        raise SystemExit("vercel.json sem outputDirectory: a superficie publica e indefinivel.")
    vi = raiz / ".vercelignore"
    rs = regras(vi.read_text(encoding="utf-8")) if vi.exists() else []
    publicados = []
    for p in rastreados(raiz):
        if not p.startswith(saida + "/"):
            continue          # fora do outputDirectory: nunca e servido
        if ignorado(p, rs):
            continue          # excluido antes de chegar ao contentor
        publicados.append(p)
    return {"output_directory": saida, "regras_vercelignore": len(rs),
            "ficheiros": sorted(publicados)}


def main():
    s = superficie()
    if "--json" in sys.argv:
        s["bytes"] = {f: (RAIZ / f).stat().st_size for f in s["ficheiros"] if (RAIZ / f).exists()}
        s["total_ficheiros"] = len(s["ficheiros"])
        s["total_bytes"] = sum(s["bytes"].values())
        print(json.dumps(s, ensure_ascii=False, indent=2))
    else:
        for f in s["ficheiros"]:
            print(f)
        print(f"\n{len(s['ficheiros'])} ficheiros publicados a partir de {s['output_directory']}/",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
