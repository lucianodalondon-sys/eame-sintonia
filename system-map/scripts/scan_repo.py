#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · SCANNER

Le o repositorio e devolve FATOS. Nao devolve opiniao, nao devolve arquitetura
desejada, nao devolve nome bonito. So o que esta escrito no codigo e pode ser
apontado com dedo: arquivo, linha, trecho.

    O MAPA E DERIVADO DO REPO. O REPO NAO E DERIVADO DO MAPA.

Tres regras que este ficheiro nunca quebra:

  1. NAO INVENTA LIGACAO. Uma aresta so nasce de um import, de uma chamada, de
     um literal de caminho, de um `run:` de workflow. Se nao ha linha para
     apontar, nao ha aresta. "Parece logico" nao e evidencia.

  2. E DETERMINISTICO. Mesma arvore + mesmo HEAD = byte a byte o mesmo JSON.
     Por isso GENERATED_AT e a data do COMMIT, nunca `datetime.now()`: um
     relogio dentro do artefacto faria o CI acusar drift a cada minuto e a
     lei perderia os dentes em uma semana.

  3. GRAVA O SHA DE CADA ARQUIVO. E o unico jeito honesto de responder
     "isto mudou desde que foi provado?". Sem isso, verde velho sobrevive
     para sempre, que e exatamente o que esta missao existe para impedir.

SAIDA: system-map/data/architecture.generated.json
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "system-map" / "data" / "architecture.generated.json"

# Extensoes que o scanner sabe LER de verdade (extrair import, chamada, caminho).
# Estar aqui significa "eu consigo provar coisas sobre este ficheiro".
LEGIVEIS = {".py", ".mjs", ".js", ".sh", ".yml", ".yaml", ".html"}

# Diretorios de codigo: mexer aqui e mexer na arquitetura. Um ficheiro novo
# nestes caminhos que ninguem declarou faz o validador reprovar. E de proposito.
DIRS_DE_CODIGO = ("scripts/", "italia-portale/audit/", "tests/", "system-map/",
                  ".github/workflows/", "italia-portale/client/")

# Ruido que nao e arquitetura: dependencia de terceiro, fonte, binario.
# `italia-portale/client/system-map/` e COPIA da app, gerada pelo build para a
# Vercel poder servir. Escanea-la faria a app aparecer duas vezes no mapa, com
# dois donos para a mesma linha. Copia derivada nao e componente.
# `system-map/data/*.generated.json` sao a SAIDA deste proprio scanner. Media-los
# e um gato a morder o rabo: cada corrida muda o conteudo deles, o que muda o SHA,
# o que muda a saida da corrida seguinte — e o censo nunca chega a um ponto fixo.
# O ficheiro DECLARADO fica: esse e escrito por gente, e uma entrada, nao uma saida.
IGNORAR = re.compile(
    r"^system-map/data/\w+\.generated\.json$|"
    r"^italia-portale/client/system-map/|"
    r"(^|/)(vendor|node_modules|__pycache__|\.venv)/|"
    r"\.(png|jpg|jpeg|gif|pdf|otf|ttf|woff2?|gz|zip|ase)$"
)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(RAIZ), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.rstrip("\n")


# ─────────────────────────────────────────────────────────────────────────────
# 1 · O CENSO — que ficheiros existem, e com que conteudo exato
# ─────────────────────────────────────────────────────────────────────────────
def sha_do_disco(caminho: str) -> str:
    """SHA-1 no formato de blob do git, calculado sobre o ficheiro EM DISCO.

    NAO uso o SHA do indice (`git ls-files -s`). O indice so muda no `git add`,
    e isso fazia o scanner medir uma versao que ja nao existe: editar um ficheiro
    e regerar dava um mapa carimbado com o conteudo ANTIGO, e o validador acusava
    drift sobre trabalho ja feito — um portao a reprovar por causa do relogio,
    nao por causa do conteudo.

    Nao uso data de modificacao pela razao oposta: `git checkout` reescreve mtime
    e faria tudo parecer alterado sem nada ter mudado.

    Conteudo em disco e a unica medida que so mente se o conteudo mentir.
    """
    dados = (RAIZ / caminho).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(dados) + dados).hexdigest()


def censo():
    """A LISTA vem do git (o que esta rastreado); o CONTEUDO vem do disco."""
    arquivos = {}
    for caminho in git("ls-files").splitlines():
        if IGNORAR.search(caminho):
            continue
        try:
            sha = sha_do_disco(caminho)
        except OSError:
            continue  # rastreado e ausente do disco — nao da para medir
        arquivos[caminho] = {
            "path": caminho,
            "sha": sha,
            "ext": Path(caminho).suffix,
            "readable": Path(caminho).suffix in LEGIVEIS,
            "code_dir": caminho.startswith(DIRS_DE_CODIGO),
        }
    return dict(sorted(arquivos.items()))


def ler(caminho: str) -> list[str]:
    try:
        return (RAIZ / caminho).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def prova(caminho: str, n: int, linha: str) -> dict:
    """Toda aresta carrega uma destas. Sem isto, a aresta nao existe."""
    return {"file": caminho, "line": n, "snippet": linha.strip()[:160]}


# ─────────────────────────────────────────────────────────────────────────────
# 3 · O QUE FOI DECLARADO E NAO ESTA AQUI — mas existe noutro sitio
# ─────────────────────────────────────────────────────────────────────────────
def onde_mais(declarados: set[str], presentes: set[str]) -> dict:
    """Para cada ficheiro declarado no mapa e ausente desta arvore, procura em que
    branches remotas ele existe.

    Isto muda o significado do vermelho. Sem esta medicao, uma peca ausente diz
    apenas "nao existe" — e quem le conclui que foi apagada, ou que nunca foi
    feita. Com ela, o mapa consegue dizer a verdade inteira:

        NAO ESTA AQUI. ESTA ALI. E ALI NAO E O SITIO DE ONDE SE PUBLICA.

    Que e um problema completamente diferente, e muito mais caro: significa que a
    ferramenta foi construida, funciona, e mesmo assim nao corre — porque o botao
    ficou noutra gaveta.

    So le `git ls-tree`. Nao faz checkout, nao mistura arvores, nao traz nada para
    ca. Medir onde uma coisa esta nao e o mesmo que traze-la, e a decisao de a
    trazer e de gente.
    """
    faltam = sorted(declarados - presentes)
    if not faltam:
        return {}
    ramos = [b.strip() for b in git("branch", "-r", "--format=%(refname:short)").splitlines()
             if b.strip() and "->" not in b]
    achados: dict[str, list] = {}
    for ramo in ramos:
        arvore = set(git("ls-tree", "-r", "--name-only", ramo).splitlines())
        for f in faltam:
            if f in arvore:
                achados.setdefault(f, []).append(ramo)
    return {f: sorted(r) for f, r in sorted(achados.items())}


# ─────────────────────────────────────────────────────────────────────────────
# 2 · AS ARESTAS — cada uma nasce de uma linha que da para apontar
# ─────────────────────────────────────────────────────────────────────────────

RE_PY_IMPORT = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))")
RE_JS_IMPORT = re.compile(r"""(?:from|import)\s+['"]([^'"]+)['"]""")
RE_LITERAL = re.compile(r"""['"]([A-Za-z0-9_./-]+\.[A-Za-z0-9]{1,6})['"]""")
RE_ESCRITA = re.compile(
    r"open\([^)]*['\"][wa]|json\.dump|write_text|writeFileSync|\.to_csv|"
    r"savefig|mkdir|>\s*[\"']?\$?\w"
)
# `run:` de workflow chamando script do repo
RE_RUN_SCRIPT = re.compile(
    r"((?:scripts|tests|system-map/scripts|system-map/tests)/[\w./-]+\.(?:py|sh|mjs))")


def modulo_para_ficheiro(mod: str, origem: str, arquivos: dict) -> str | None:
    """`import apify_pool` dentro de scripts/ resolve para scripts/apify_pool.py.

    So devolve caminho que EXISTE no censo. Import de biblioteca de terceiro
    (json, pathlib, requests) nao resolve e portanto nao vira aresta — o mapa
    e do SINTONIA, nao do ecossistema Python.
    """
    base = mod.split(".")[0]
    pasta = str(Path(origem).parent).replace("\\", "/")
    for tentativa in (f"{pasta}/{base}.py", f"scripts/{base}.py", f"{base}.py"):
        if tentativa in arquivos:
            return tentativa
    return None


def resolver_js(alvo: str, origem: str, arquivos: dict) -> str | None:
    if not alvo.startswith("."):
        return None  # pacote npm — fora do mapa
    caminho = os.path.normpath(os.path.join(str(Path(origem).parent), alvo))
    caminho = caminho.replace("\\", "/")
    return caminho if caminho in arquivos else None


def relativo(lit: str, origem: str, arquivos: dict) -> str | None:
    """`<script src="italy-v21.js">` e um caminho relativo a propria pasta.

    So devolve caminho que EXISTE. Um literal que nao resolve continua sem virar
    aresta — inventar destino a partir de nome parecido seria fabricar ligacao,
    que e exatamente o que este mapa existe para nao fazer.
    """
    if lit.startswith("/") or "://" in lit:
        return None
    alvo = os.path.normpath(os.path.join(str(Path(origem).parent), lit)).replace("\\", "/")
    return alvo if alvo in arquivos else None


def arestas(arquivos: dict) -> list[dict]:
    saida: list[dict] = []
    vistas: set[tuple] = set()

    def add(de: str, para: str, tipo: str, ev: dict, carga: str = ""):
        if de == para or para not in arquivos:
            return
        chave = (de, para, tipo)
        if chave in vistas:
            return
        vistas.add(chave)
        saida.append({
            "from_file": de, "to_file": para, "type": tipo,
            "payload": carga, "evidence": ev,
        })

    for caminho, meta in arquivos.items():
        if not meta["readable"]:
            continue
        ext = meta["ext"]
        linhas = ler(caminho)
        for n, linha in enumerate(linhas, 1):
            crua = linha.rstrip()
            if ext in (".py", ".sh", ".yml", ".yaml"):
                sem_comentario = crua.split("#")[0]
            elif ext in (".js", ".mjs"):
                # `// scripts/foo.py` e prosa, nao chamada. Contar comentario
                # como prova era o buraco mais facil de abrir neste scanner.
                sem_comentario = crua.split("//")[0] if not crua.lstrip().startswith("*") else ""
            else:
                sem_comentario = crua

            # ── import Python ────────────────────────────────────────────
            if ext == ".py":
                m = RE_PY_IMPORT.match(crua)
                if m:
                    alvo = modulo_para_ficheiro(m.group(1) or m.group(2), caminho, arquivos)
                    if alvo:
                        add(caminho, alvo, "IMPORTS", prova(caminho, n, crua), "codigo")

            # ── import JS/MJS ────────────────────────────────────────────
            if ext in (".mjs", ".js"):
                for alvo_bruto in RE_JS_IMPORT.findall(crua):
                    alvo = resolver_js(alvo_bruto, caminho, arquivos)
                    if alvo:
                        add(caminho, alvo, "IMPORTS", prova(caminho, n, crua), "codigo")

            # ── workflow chamando script ─────────────────────────────────
            if ext in (".yml", ".yaml"):
                for alvo in RE_RUN_SCRIPT.findall(crua):
                    add(caminho, alvo, "RUNS", prova(caminho, n, crua), "execucao")

            # ── shell chamando script ────────────────────────────────────
            if ext == ".sh":
                for alvo in RE_RUN_SCRIPT.findall(sem_comentario):
                    add(caminho, alvo, "RUNS", prova(caminho, n, crua), "execucao")

            # ── literal de caminho: leitura ou escrita ───────────────────
            # So conta literal que aponta para ficheiro que EXISTE. Um literal
            # que nao resolve pode ser caminho de saida futura, nome de coluna,
            # ou lixo — e adivinhar qual e disso seria fabricar aresta.
            for lit in RE_LITERAL.findall(sem_comentario):
                alvo = lit if lit in arquivos else relativo(lit, caminho, arquivos)
                if alvo:
                    tipo = "WRITES" if RE_ESCRITA.search(sem_comentario) else "READS"
                    add(caminho, alvo, tipo, prova(caminho, n, crua), "artefacto")

    saida.sort(key=lambda e: (e["from_file"], e["to_file"], e["type"]))
    return saida


# ─────────────────────────────────────────────────────────────────────────────
# 3 · MONTAR
# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    arquivos = censo()
    if not arquivos:
        print("SCAN=FALHOU · censo vazio (isto e um repositorio git?)", file=sys.stderr)
        return 1

    head = git("rev-parse", "HEAD")
    fatos = {
        "SCHEMA": "sintonia.system-map.generated/1",
        # PROVENIENCIA vive num bloco a parte, e o validador IGNORA-O ao medir
        # drift. Tem de ser assim: HEAD muda a cada commit e BRANCH muda a cada
        # ramo. Se estes campos entrassem na comparacao, o CI acusaria drift em
        # TODA a gente, sempre — inclusive no commit que acabou de regerar o mapa.
        #
        #     UM PORTAO QUE REPROVA TODA A GENTE NAO MEDE NADA.
        #
        # O que e comparado e a ARQUITETURA. Isto aqui e so o carimbo de quem
        # correu, quando, e sobre que arvore.
        "PROVENANCE": {
            "REPO": "lucianodalondon-sys/eame-sintonia",
            "BRANCH": git("rev-parse", "--abbrev-ref", "HEAD"),
            "HEAD": head,
            # Data do COMMIT, nao do relogio. Ver regra 2 no cabecalho.
            "GENERATED_AT": git("show", "-s", "--format=%cI", head),
        },
        "FILES": list(arquivos.values()),
        "FILE_EDGES": arestas(arquivos),
        "COUNTS": {
            "files_tracked": len(arquivos),
            "files_readable": sum(1 for f in arquivos.values() if f["readable"]),
            "files_code_dir": sum(1 for f in arquivos.values() if f["code_dir"]),
        },
    }
    fatos["COUNTS"]["file_edges"] = len(fatos["FILE_EDGES"])

    # O mapa declara ficheiros; alguns podem nao estar nesta arvore. Medir onde
    # eles estao e barato e responde a pergunta que o vermelho sozinho nao responde.
    decl = RAIZ / "system-map" / "data" / "architecture.declared.json"
    if decl.exists():
        D = json.loads(decl.read_text(encoding="utf-8"))
        pedidos = {f for c in D.get("COMPONENTS", []) for f in c["files"]
                   if not any(ch in f for ch in "*?[")}
        fatos["ELSEWHERE"] = onde_mais(pedidos, set(arquivos))
        fatos["COUNTS"]["declared_missing_here"] = len(fatos["ELSEWHERE"])

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(
        json.dumps(fatos, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    c = fatos["COUNTS"]
    print(f"SCAN=OK · HEAD={head[:8]} · arquivos={c['files_tracked']} "
          f"· legiveis={c['files_readable']} · arestas_de_ficheiro={c['file_edges']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
