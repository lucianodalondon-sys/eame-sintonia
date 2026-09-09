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

import ast
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
def _gavetas() -> tuple:
    """A lista das gavetas do processo, lida de `_gavetas.py`.

    Uma segunda lista aqui seria uma segunda verdade: bastava alguem criar uma
    gaveta nova e esquecer-se deste ficheiro para o scanner deixar de ver metade
    do repositorio — sem reclamar, porque o que ele nao ve nao existe para ele.
    """
    f = RAIZ / "_gavetas.py"
    if not f.exists():
        return ()
    for no in ast.parse(f.read_text(encoding="utf-8")).body:
        if isinstance(no, ast.Assign) and any(
                getattr(t, "id", "") == "GAVETAS" for t in no.targets):
            return tuple(ast.literal_eval(no.value))
    return ()


GAVETAS = _gavetas()

DIRS_DE_CODIGO = tuple(g + "/" for g in GAVETAS) + (
    "scripts/", "italia-portale/audit/", "tests/", "system-map/",
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
    # Repare no HIFEN dentro dos parenteses retos. Antes estava so `\w`, que nao
    # o inclui — e os dois ficheiros gerados mais recentes chamam-se
    # `censo-da-coleta.generated.json` e `pente-fino.generated.json`. Escapavam
    # por causa do hifen, e o mapa voltava a medir-se a si mesmo.
    #
    # E so falhava no CI, o que tornou a caca mais dificil: aqui o validador nao
    # corre o censo, la corre — e por isso o SHA daqueles dois mudava no meio da
    # verificacao. Uma avaria que so aparece numa maquina custa tres tentativas
    # a encontrar.
    r"^system-map/data/[\w-]+\.generated\.json$|"
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

    MAS O DISCO NAO GUARDA O MESMO EM TODA A MAQUINA.
    Com `core.autocrlf=true` — o valor por omissao do Windows — o git escreve as
    linhas terminadas em CRLF no disco e guarda-as em LF no repositorio. Neste
    repositorio isso sao 858 ficheiros.

    O resultado era invisivel e fatal: o mapa gerado no Windows levava SHAs de
    CRLF, o CI regerava em Linux com SHAs de LF, e o validador acusava drift em
    TODOS eles. Nao havia conserto possivel do lado de quem gerava — regerar
    outra vez dava exatamente o mesmo desencontro.

        UM PORTAO QUE REPROVA POR CAUSA DO SISTEMA OPERATIVO NAO MEDE CONTEUDO.

    Por isso o texto e normalizado para LF antes de ser medido, que e a forma
    como o git o guarda. Assim o SHA passa a ser o mesmo em qualquer maquina — e
    igual ao que `git hash-object` devolve.

    O binario nao se toca: um ficheiro com byte zero nao tem «linhas», e trocar
    bytes la dentro estragaria a medicao em vez de a corrigir.
    """
    dados = (RAIZ / caminho).read_bytes()
    if b"\0" not in dados:                      # texto: normaliza como o git guarda
        dados = dados.replace(b"\r\n", b"\n")
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
# 2b · A CONSTANTE QUE GUARDA UM CAMINHO
# ─────────────────────────────────────────────────────────────────────────────
def escritas_por_constante(caminho: str, unicos: dict) -> list[tuple]:
    """Segue `DEST = os.path.join(SAMPLES, 'X.json')` ate `open(DEST, 'w')`.

    Esta casa escreve assim, e com razao: o caminho fica num sitio so, no topo,
    onde se ve. Mas isso poe o NOME do ficheiro na linha 99 e a ESCRITA na linha
    600, e uma leitura linha-a-linha nunca junta as duas.

        A CONSTANTE ESTAVA A ESCONDER A SETA MAIS IMPORTANTE DO MAPA.

    Sem isto, `corpus_pesquisador.py` parecia nao produzir nada — quando o que ele
    escreve alimenta o pacote, os sensores da coleta e o Ask Sintonia. A peca
    aparecia orfa, e peca orfa e peca que alguem apaga.

    Le com `ast`, sem executar nada. So resolve quando o nome do ficheiro e UNICO
    no repositorio: havendo dois iguais, nao ha como saber qual e, e escolher
    seria inventar.
    """
    try:
        arvore = ast.parse((RAIZ / caminho).read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError):
        return []

    # 1 · constante -> ficheiro do repositorio
    de_nome: dict[str, str] = {}
    linha_de: dict[str, int] = {}
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Assign) or len(no.targets) != 1:
            continue
        alvo = no.targets[0]
        if not isinstance(alvo, ast.Name):
            continue
        for pedaco in ast.walk(no.value):
            if isinstance(pedaco, ast.Constant) and isinstance(pedaco.value, str):
                achado = unicos.get(pedaco.value.split("/")[-1])
                if achado:
                    de_nome[alvo.id] = achado[0]
                    linha_de[alvo.id] = no.lineno

    if not de_nome:
        return []

    # 2 · `open(CONST, 'w')` — e so 'w'/'a'. Sem modo, e leitura.
    saida = []
    for no in ast.walk(arvore):
        if not (isinstance(no, ast.Call) and getattr(no.func, "id", "") == "open"):
            continue
        if not no.args or not isinstance(no.args[0], ast.Name):
            continue
        alvo = de_nome.get(no.args[0].id)
        if not alvo:
            continue
        modo = ""
        if len(no.args) > 1 and isinstance(no.args[1], ast.Constant):
            modo = str(no.args[1].value)
        for kw in no.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                modo = str(kw.value.value)
        tipo = "WRITES" if modo[:1] in ("w", "a") else "READS"
        saida.append((alvo, tipo, no.lineno, no.args[0].id, modo or "leitura"))
    return saida


def escritas_em_pasta(caminho: str, pastas_unicas: dict) -> list[tuple]:
    """`SAIDA = os.path.join(SAMPLES, 'X')` e depois `open(os.path.join(SAIDA, nome), 'w')`.

    O NOME DO FICHEIRO E UMA VARIAVEL, e por isso a medicao anterior nao via nada:
    ela so seguia constantes ate um ficheiro com nome fixo. O resultado era um
    beco sem saida no mapa — «Colher o Instagram» e «Colher o que o concorrente
    publica» apareciam a nao escrever nada, quando escrevem uma pasta inteira.

    Um cartao que diz «nao guarda nada» sobre uma peca que guarda e pior do que
    um cartao vazio: parece uma medicao, e e so um ponto cego.

    O que se consegue saber com honestidade e a PASTA — e a pasta ja responde a
    pergunta que interessa: «o que entra por aqui vai parar onde?».

    NAO GERA ARESTA. Uma pasta nao e um ficheiro, e reivindicar os ficheiros la
    dentro daria a esta peca a posse de coisas que outra pode ter escrito. Fica
    como facto ao lado, para o cartao poder responder.
    """
    try:
        arvore = ast.parse((RAIZ / caminho).read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError):
        return []

    de_pasta: dict[str, str] = {}
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Assign) or len(no.targets) != 1:
            continue
        alvo = no.targets[0]
        if not isinstance(alvo, ast.Name):
            continue
        for pedaco in ast.walk(no.value):
            if isinstance(pedaco, ast.Constant) and isinstance(pedaco.value, str):
                achado = pastas_unicas.get(pedaco.value.strip("/").split("/")[-1])
                if achado:
                    de_pasta[alvo.id] = achado

    if not de_pasta:
        return []

    fora = []
    for no in ast.walk(arvore):
        if not (isinstance(no, ast.Call) and getattr(no.func, "id", "") == "open"):
            continue
        modo = ""
        if len(no.args) > 1 and isinstance(no.args[1], ast.Constant):
            modo = str(no.args[1].value)
        for kw in no.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                modo = str(kw.value.value)
        if modo[:1] not in ("w", "a"):
            continue
        # open(os.path.join(CONST, <o que for>), 'w')
        if not no.args:
            continue
        for pedaco in ast.walk(no.args[0]):
            if isinstance(pedaco, ast.Name) and pedaco.id in de_pasta:
                fora.append((de_pasta[pedaco.id], no.lineno, pedaco.id))
                break
    return fora


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
# Caminho escrito sem aspas nenhumas, como acontece em teste de shell.
RE_CAMINHO_NU = re.compile(r"(?<![\w/'\"-])((?:data|docs|build|supabase)/[\w./-]+\.\w{2,6})")
RE_ESCRITA = re.compile(
    r"open\([^)]*['\"][wa]|json\.dump|write_text|writeFileSync|\.to_csv|"
    r"savefig|mkdir|>\s*[\"']?\$?\w"
)
# `run:` de workflow chamando script do repo
_PASTAS_CHAMAVEIS = "|".join(list(GAVETAS) + [
    "scripts", "tests", "system-map/scripts", "system-map/tests"])
RE_RUN_SCRIPT = re.compile(rf"((?:{_PASTAS_CHAMAVEIS})/[\w./-]+\.(?:py|sh|mjs))")


def modulo_para_ficheiro(mod: str, origem: str, arquivos: dict) -> str | None:
    """`import apify_pool` dentro de scripts/ resolve para ferramentas/apify_pool.py.

    So devolve caminho que EXISTE no censo. Import de biblioteca de terceiro
    (json, pathlib, requests) nao resolve e portanto nao vira aresta — o mapa
    e do SINTONIA, nao do ecossistema Python.
    """
    base = mod.split(".")[0]
    pasta = str(Path(origem).parent).replace("\\", "/")
    # A propria gaveta primeiro; depois as outras, porque `_gavetas.py` poe todas
    # no caminho e por isso o Python tambem as encontraria.
    tentativas = [f"{pasta}/{base}.py", f"scripts/{base}.py", f"{base}.py"]
    tentativas += [f"{g}/{base}.py" for g in GAVETAS]
    for t in tentativas:
        if t in arquivos:
            return t
    return None


def resolver_js(alvo: str, origem: str, arquivos: dict) -> str | None:
    if not alvo.startswith("."):
        return None  # pacote npm — fora do mapa
    caminho = os.path.normpath(os.path.join(str(Path(origem).parent), alvo))
    caminho = caminho.replace("\\", "/")
    return caminho if caminho in arquivos else None


def por_nome_unico(lit: str, indice: dict) -> str | None:
    """`'PUBLIC-COMM-FIRST-BATCH-EAME.json'` -> o unico ficheiro com esse nome.

    So devolve quando o nome e unico no repositorio. Dois ficheiros com o mesmo
    nome nao dao para distinguir a partir do literal, e escolher um seria inventar.
    """
    alvo = indice.get(lit.split("/")[-1])
    return alvo if alvo and len(alvo) == 1 else None


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


def arestas(arquivos: dict) -> tuple[list, dict]:
    saida: list[dict] = []
    vistas: set[tuple] = set()

    # nome do ficheiro -> os caminhos que o tem. So os unicos sao usaveis.
    porNome: dict[str, list] = {}
    for caminho in arquivos:
        porNome.setdefault(caminho.split("/")[-1], []).append(caminho)
    unicos = {n: v for n, v in porNome.items() if len(v) == 1}

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

    # nome de pasta -> caminho, so quando o nome e UNICO. Havendo duas pastas
    # com o mesmo nome, escolher uma seria inventar.
    from collections import Counter
    todas_pastas = {}
    conta_pastas = Counter()
    for c in arquivos:
        partes = c.split("/")
        for k in range(1, len(partes)):
            d = "/".join(partes[:k])
            if d not in todas_pastas:
                conta_pastas[partes[k - 1]] += 1
                todas_pastas[d] = partes[k - 1]
    pastas_unicas = {b: d for d, b in todas_pastas.items() if conta_pastas[b] == 1}

    escritas_de_pasta: dict[str, list] = {}
    for caminho, meta in arquivos.items():
        if not meta["readable"]:
            continue
        if meta["ext"] == ".py":
            for pasta, n, const in escritas_em_pasta(caminho, pastas_unicas):
                escritas_de_pasta.setdefault(caminho, [])
                if not any(x["pasta"] == pasta for x in escritas_de_pasta[caminho]):
                    escritas_de_pasta[caminho].append(
                        {"pasta": pasta, "line": n, "constante": const})
            for alvo, tipo, n, const, modo in escritas_por_constante(caminho, unicos):
                add(caminho, alvo, tipo,
                    prova(caminho, n, f"open({const}, {modo!r})  # {const} = {alvo}"),
                    "artefacto")
        ext = meta["ext"]
        linhas = ler(caminho)
        # Onde acaba o bloco `on:` e comecam os passos. Antes disto, um `.yml`
        # so declara GATILHOS — e um gatilho nao corre nem le nada.
        inicio_dos_jobs = 0
        if caminho.endswith((".yml", ".yaml")):
            for _i, _l in enumerate(linhas, 1):
                if _l.startswith("jobs:"):
                    inicio_dos_jobs = _i
                    break
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
            # ⚠️ UM `paths:` NAO E UMA EXECUCAO.
            #
            # Isto corria sobre QUALQUER linha do `.yml`, e o bloco `on:` de um
            # workflow lista ficheiros — `paths:` diz «acorda quando este
            # ficheiro mudar», nao «este workflow corre este ficheiro». Medido:
            # 48 arestas da arvore tinham como unica prova uma linha de lista
            # dentro do `on:`, e cada uma dessas linhas produzia DUAS falsas:
            #
            #   C-CI-PERSIST -> C-ADMISSAO   RUNS    (o CI nao corre admissao.py)
            #   C-ADMISSAO   -> C-CI-PERSIST READS   (e a direccao ao contrario)
            #
            # ambas apontando para `banco-descartavel.yml:45`, que e
            # `- 'admissao/admissao.py'` dentro do filtro de caminhos.
            #
            #     ACORDAR COM A MUDANCA DE UM FICHEIRO
            #     NAO E EXECUTAR ESSE FICHEIRO.
            #
            # E eu piorei isto na missao anterior: acrescentei dez caminhos ao
            # `paths:` do `banco-descartavel.yml` para o portao acordar quando
            # a estrada mudasse — e sem saber criei dez arestas falsas.
            #
            # A fronteira e estrutural e nao heuristica: em todos os 15
            # workflows desta arvore o `on:` vem antes do `jobs:`, os dois na
            # coluna zero. Tudo o que esta antes de `jobs:` e GATILHO.
            # ⚠️ E UM COMENTARIO TAMBEM NAO E UMA EXECUCAO.
            # Isto lia a linha CRUA, enquanto o ramo do `.sh` logo abaixo ja
            # usava `sem_comentario`. A inconsistencia custou cinco arestas
            # RUNS cuja unica prova era prosa — e tres delas nasceram de
            # comentarios que EU escrevi a explicar o que o passo faz:
            #
            #   C-CI-PERSIST -> C-PROVA-ROTA-M2-ATRAVESSA
            #     prova: «# `provas/a_rota_m2_atravessa.py` e a unica prova...»
            #
            # A aresta ate era VERDADEIRA — o passo 2g corre mesmo esse
            # ficheiro — mas a prova apontava para a frase, nao para o comando.
            # Uma aresta certa com prova errada e uma aresta que ninguem
            # consegue conferir.
            #
            #     EXPLICAR UMA EXECUCAO NAO E EXECUTAR.
            if ext in (".yml", ".yaml") and n > inicio_dos_jobs:
                for alvo in RE_RUN_SCRIPT.findall(sem_comentario):
                    add(caminho, alvo, "RUNS", prova(caminho, n, crua), "execucao")

            # ── shell chamando script ────────────────────────────────────
            if ext == ".sh":
                for alvo in RE_RUN_SCRIPT.findall(sem_comentario):
                    add(caminho, alvo, "RUNS", prova(caminho, n, crua), "execucao")

            # ── literal de caminho: leitura ou escrita ───────────────────
            # So conta literal que aponta para ficheiro que EXISTE. Um literal
            # que nao resolve pode ser caminho de saida futura, nome de coluna,
            # ou lixo — e adivinhar qual e disso seria fabricar aresta.
            # sem aspas tambem conta: `if [ ! -f data/samples/x.json ]` num passo
            # de shell e uma leitura tao real como qualquer outra.
            # A mesma fronteira vale para a leitura: um caminho listado no
            # `paths:` nao e um ficheiro que alguem abriu. Era daqui que saia a
            # aresta ao contrario — `admissao/admissao.py READS o workflow`.
            crus = ([] if (ext in (".yml", ".yaml") and n <= inicio_dos_jobs)
                    else RE_LITERAL.findall(sem_comentario))
            if ext in (".sh", ".yml", ".yaml") and not (
                    ext in (".yml", ".yaml") and n <= inicio_dos_jobs):
                crus += RE_CAMINHO_NU.findall(sem_comentario)
            for lit in crus:
                alvo = lit if lit in arquivos else relativo(lit, caminho, arquivos)
                if not alvo:
                    achado = por_nome_unico(lit, unicos)
                    alvo = achado[0] if achado else None
                if alvo:
                    tipo = "WRITES" if RE_ESCRITA.search(sem_comentario) else "READS"
                    add(caminho, alvo, tipo, prova(caminho, n, crua), "artefacto")

    saida.sort(key=lambda e: (e["from_file"], e["to_file"], e["type"]))
    # a segunda coisa e o que se escreve numa PASTA com nome variavel: nao vira
    # aresta (uma pasta nao e um ficheiro), mas responde «vai parar onde?».
    return saida, escritas_de_pasta


# ─────────────────────────────────────────────────────────────────────────────
# 3 · MONTAR
# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    arquivos = censo()
    if not arquivos:
        print("SCAN=FALHOU · censo vazio (isto e um repositorio git?)", file=sys.stderr)
        return 1

    head = git("rev-parse", "HEAD")
    _arestas, _em_pasta = arestas(arquivos)
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
        "FILE_EDGES": _arestas,
        "ESCRITAS_EM_PASTA": _em_pasta,
        "COUNTS": {
            "files_tracked": len(arquivos),
            "files_readable": sum(1 for f in arquivos.values() if f["readable"]),
            "files_code_dir": sum(1 for f in arquivos.values() if f["code_dir"]),
        },
    }
    fatos["COUNTS"]["file_edges"] = len(fatos["FILE_EDGES"])
    fatos["COUNTS"]["escritas_em_pasta"] = sum(len(v) for v in _em_pasta.values())

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
