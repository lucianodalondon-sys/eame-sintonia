#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CENSO DA COLETA — o retrato do que existe HOJE, antes de mexer em nada.

    NUMERO DE MEMORIA NAO E FACTO. Este ficheiro existe para nao herdar «44
    coletores» de uma conversa antiga e construir uma arquitetura inteira em
    cima de um numero que ja nao e verdade.

E READ-ONLY. Nao move, nao apaga, nao reescreve: le a arvore e conta. Pode
correr as vezes que forem precisas, e deve dar o mesmo resultado enquanto o
repositorio nao mudar.

O QUE ELE PROCURA, E PORQUE
---------------------------
A missao pergunta doze coisas. Cada uma vira uma medicao com nome:

    PONTOS DE ENTRADA    de quantas maneiras diferentes se comeca uma coleta?
                         Se forem oitenta, nao ha «uma coleta»: ha oitenta.
    EXECUTORES           quem realmente sai para fora e traz alguma coisa
    FERRAMENTAS          com que se viaja (Apify, navegador, transcricao, PDF)
    VEICULOS             por onde se vai (YouTube, Instagram, HTTP...)
    REGRAS               e a pergunta mais importante delas: cada uma BARRA
                         ou apenas MEDE? Uma regua que mede nao e um filtro,
                         e chamar as duas de «regra» esconde que nao ha peneira
    ONDE GRAVA           git, banco, ou ficheiro solto na maquina de alguem
    DESCARTES            quem deita fora, e quem escreve porque deitou fora
    DECISOES ESCONDIDAS  `if` de relevancia dentro do coletor — cada um destes
                         e uma lei privada que ninguem consegue ler de fora
    ORFAOS               codigo que ninguem chama e nenhum workflow corre

O QUE ELE NAO FAZ
-----------------
Nao decide o que remover. «Ninguem chama» NAO e o mesmo que «e lixo»: metade
dos ficheiros sem chamador sao ferramentas de mao, feitas para uma pessoa
correr quando precisa. Este ficheiro poe a lista na mesa; quem decide e gente.

SAIDA: system-map/data/censo-da-coleta.generated.json
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "system-map" / "data" / "censo-da-coleta.generated.json"

# As gavetas que formam o departamento de coleta, da porta ate a sala de espera.
# `pedido/` e `admissao/` entraram depois — e tem de ser contadas, senao o censo
# mede o mundo antigo e diz que nada mudou.
GAVETAS = ("pedido", "candidatas", "fontes", "ferramentas", "coleta", "regras",
           "admissao", "guarda")
CODIGO = (".py", ".mjs", ".js", ".sh")

# ── o que faz de um ficheiro cada coisa ─────────────────────────────────────
# Sair para a rede e o que uma ACAO faz. Nao confundir com ser um veiculo: o
# veiculo e o sitio, a acao e o verbo. Ja errei isto uma vez.
SAI_PARA_FORA = re.compile(
    r"\brequests\.(get|post|put)|httpx\.|urllib\.request|aiohttp|fetch\("
    r"|yt_dlp|playwright|selenium|feedparser", re.I)

VEICULOS = {
    "YOUTUBE": r"youtube|yt_dlp|youtu\.be",
    "INSTAGRAM": r"instagram",
    "LINKEDIN": r"linkedin",
    "FACEBOOK": r"facebook",
    "HTTP DIRETO": r"\brequests\.|httpx|urllib\.request|aiohttp",
}

FERRAMENTAS = {
    "APIFY (rota paga)": r"apify",
    "NAVEGADOR (rota gratis)": r"playwright|selenium",
    "TRANSCRICAO": r"whisper|transcri",
    "LEITOR DE PDF/HTML": r"pdfplumber|PyPDF|BeautifulSoup|html2text|pdf_peek|html_text",
}

# Um `if` que decide se o item presta. Cada um destes e uma lei privada.
DECISAO_ESCONDIDA = re.compile(
    r"^\s*(?:if|elif)\b[^\n]*\b(relevan|irrelevan|descart|discard|rejeit"
    r"|skip|ignora|lixo|spam|ruido)", re.I | re.M)

DESCARTA = re.compile(r"descart|discard|rejeit|drop_|excluir", re.I)
# Deitar fora e uma coisa; ESCREVER PORQUE se deitou fora e outra, e e a que
# faz a coleta aprender. Sem motivo guardado, gasta-se maquina para redescobrir
# amanha que aquela fonte entrega lixo.
ESCREVE_O_MOTIVO = re.compile(
    r"motivo|reason|porque|why|justific|DESCARTE\w*\s*=|\"motivo\"|'motivo'", re.I)

GRAVA_NO_BANCO = re.compile(
    r"(?:^|\s)(?:import|from)\s+(?:supabase|psycopg)"
    r"|require\(\s*['\"]@?supabase"
    r"|create_client\s*\("
    r"|(?:os\.environ|os\.getenv|process\.env)[^\n]{0,24}SUPABASE", re.I)

ESCREVE_FICHEIRO = re.compile(
    r"open\([^)]*['\"][wa]|\.write_text\(|\.write_bytes\(|json\.dump\("
    r"|writeFileSync|fs\.writeFile", re.I)

TEM_ENTRADA = re.compile(
    r"if\s+__name__\s*==\s*['\"]__main__['\"]|argparse|process\.argv|sys\.argv", re.I)


def git(*a) -> str:
    r = subprocess.run(["git", "-C", str(RAIZ), *a], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.stdout if r.returncode == 0 else ""


def ficheiros() -> list:
    fora = []
    for g in GAVETAS:
        d = RAIZ / g
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if (p.is_file() and p.suffix in CODIGO
                    and "__pycache__" not in p.as_posix()):
                fora.append(p.relative_to(RAIZ).as_posix())
    return fora


def _linhas_de_comando(t: str, arv=None) -> str:
    """O texto MENOS a prosa: comentarios e docstrings.

    Uma linha cujo primeiro caractere nao-branco e `#` nao corre — nem em
    Python, nem em YAML, nem em shell. Um docstring tambem nao: ele e um valor
    que ninguem le em tempo de execucao.

    Contar prosa como chamada foi o defeito que a C10.4C apanhou aqui. O censo
    declarou que um modulo APOSENTADO chamava tres modulos vivos, e que dois
    deles corriam no CI — tudo a partir do docstring que EXPLICA a
    aposentadoria e do comentario do workflow que a anuncia.

        UMA SENTINELA ANCORADA NO TEXTO MEDE O TEXTO, NAO A LEI.

    O docstring apaga-se por LINHA, na arvore: procurar o texto dele dentro do
    ficheiro daria um casamento por acaso sempre que uma frase se repetisse.
    """
    linhas = t.splitlines()
    if arv is not None:
        prosa = set()
        for no in ast.walk(arv):
            if isinstance(no, ast.Expr) and isinstance(no.value, ast.Constant) \
                    and isinstance(no.value.value, str):
                fim = getattr(no, "end_lineno", no.lineno) or no.lineno
                prosa.update(range(no.lineno, fim + 1))
        linhas = ["" if i in prosa else ln for i, ln in enumerate(linhas, 1)]
    return "\n".join(ln for ln in linhas if not ln.lstrip().startswith("#"))


def _lanca_processo(arv) -> bool:
    """Este ficheiro chega a lancar algum processo? Medido na arvore."""
    FAMILIA = {"run", "Popen", "call", "check_call", "check_output", "system",
               "execv", "execvp", "spawnv", "import_module", "run_module",
               "run_path", "__import__"}
    for no in ast.walk(arv):
        if isinstance(no, ast.Call):
            nome = getattr(no.func, "attr", None) or getattr(no.func, "id", None)
            if nome in FAMILIA:
                return True
    return False


def quem_chama(todos: list) -> dict:
    """Quem importa ou corre quem, e — a parte — quem apenas FALA de quem.

    Sao duas perguntas, e junta-las apagava a diferenca entre uma aresta e uma
    frase:

        chamado_por   `import` medido na arvore, ou o caminho numa linha que a
                      maquina executa (argv de subprocesso, `run:` de workflow).
        citado_por    o caminho aparece no ficheiro, mas em prosa. NAO e aresta.
                      Continua registado porque uma instrucao operacional escrita
                      num documento e, ela propria, uma porta — a C10.4C mediu
                      cinco assim.
    """
    chamado_por: dict[str, set] = {f: set() for f in todos}
    citado_por: dict[str, set] = {f: set() for f in todos}
    nome = {Path(f).stem: f for f in todos}

    for f in todos:
        t = (RAIZ / f).read_text(encoding="utf-8", errors="replace")
        arv = None
        if f.endswith(".py"):
            try:
                arv = ast.parse(t)
            except SyntaxError:
                arv = None
            if arv is not None:
                for no in ast.walk(arv):
                    alvos = []
                    if isinstance(no, ast.Import):
                        alvos = [a.name.split(".")[-1] for a in no.names]
                    elif isinstance(no, ast.ImportFrom) and no.module:
                        alvos = [no.module.split(".")[-1]]
                    for a in alvos:
                        if a in nome and nome[a] != f:
                            chamado_por[nome[a]].add(f)
        vivo = _linhas_de_comando(t, arv)
        # Um ficheiro que NUNCA lanca processo e nunca importa nada nao pode
        # estar a correr outro pelo caminho, por mais vezes que o nomeie. A
        # C10.4C mediu isto: a rota aposentada importa `sys` e mais nada, e o
        # censo declarava-a a chamar tres modulos vivos — por causa da mensagem
        # de recusa, que NOMEIA o dono canonico para quem a ler.
        #
        #     UM NOME DENTRO DE UMA FRASE NAO E UM ARGV.
        pode_lancar = (not f.endswith(".py")) or arv is None or _lanca_processo(arv)
        for outro in todos:
            if outro == f or outro not in t:
                continue
            if outro in vivo and pode_lancar:
                chamado_por[outro].add(f)
            else:
                citado_por[outro].add(f)
    return ({k: sorted(v) for k, v in chamado_por.items()},
            {k: sorted(v) for k, v in citado_por.items()})


def nos_workflows(todos: list) -> dict:
    """Corre no CI — medido nas linhas que a Action executa, nao nos comentarios."""
    wf = RAIZ / ".github" / "workflows"
    texto = ""
    if wf.is_dir():
        for p in sorted(wf.glob("*.yml")):
            texto += _linhas_de_comando(
                p.read_text(encoding="utf-8", errors="replace")) + "\n"
    return {f: (f in texto) for f in todos}


def medir() -> dict:
    todos = ficheiros()
    chamado, citado = quem_chama(todos)
    em_ci = nos_workflows(todos)

    fichas = []
    for f in todos:
        t = (RAIZ / f).read_text(encoding="utf-8", errors="replace")
        veic = sorted(k for k, rx in VEICULOS.items() if re.search(rx, t, re.I))
        ferr = sorted(k for k, rx in FERRAMENTAS.items() if re.search(rx, t, re.I))
        escondidas = [m.group(0).strip()[:110]
                      for m in DECISAO_ESCONDIDA.finditer(t)]
        descarta = bool(DESCARTA.search(t))
        fichas.append({
            "ficheiro": f,
            "gaveta": f.split("/")[0],
            "linhas": t.count("\n") + 1,
            "e_ponto_de_entrada": bool(TEM_ENTRADA.search(t)),
            "sai_para_fora": bool(SAI_PARA_FORA.search(t)),
            "veiculos": veic,
            "ferramentas": ferr,
            "descarta": descarta,
            "escreve_o_motivo_do_descarte": bool(descarta and ESCREVE_O_MOTIVO.search(t)),
            "decisoes_escondidas": escondidas,
            "grava_no_banco": bool(GRAVA_NO_BANCO.search(t)),
            "escreve_ficheiro": bool(ESCREVE_FICHEIRO.search(t)),
            "chamado_por": chamado[f],
            "citado_por": citado[f],
            "no_ci": em_ci[f],
        })

    def conta(cond) -> list:
        return [x["ficheiro"] for x in fichas if cond(x)]

    # ORFAO = ninguem o chama, ninguem o corre no CI e ninguem sequer o NOMEIA.
    # `citado_por` entra aqui de proposito: um ficheiro citado numa instrucao
    # operacional nao esta esquecido — esta a ser apontado a gente, que e a
    # forma de porta que a C10.4C mediu cinco vezes. Separar chamada de citacao
    # afinou a ARESTA sem mexer no que conta como esquecido.
    orfaos = conta(lambda x: not x["chamado_por"] and not x["citado_por"]
                   and not x["no_ci"])
    #: O numero mais apertado: sem ARESTA medida, ainda que alguem o nomeie.
    sem_aresta = conta(lambda x: not x["chamado_por"] and not x["no_ci"])
    executores = conta(lambda x: x["sai_para_fora"])
    entradas = conta(lambda x: x["e_ponto_de_entrada"])
    deita_fora = conta(lambda x: x["descarta"])
    sem_motivo = conta(lambda x: x["descarta"] and not x["escreve_o_motivo_do_descarte"])
    escondidas = [(x["ficheiro"], x["decisoes_escondidas"])
                  for x in fichas if x["decisoes_escondidas"]]

    return {
        "SCHEMA": "sintonia.censo-da-coleta/1",
        "PROVENANCE": {"HEAD": git("rev-parse", "HEAD").strip(),
                       "GAVETAS": list(GAVETAS)},
        "FICHEIROS": fichas,
        "RESUMO": {
            "ficheiros_de_codigo": len(todos),
            "pontos_de_entrada": len(entradas),
            "executores_que_saem_para_fora": len(executores),
            "sem_chamador_e_fora_do_ci": len(orfaos),
            "sem_aresta_medida_e_fora_do_ci": len(sem_aresta),
            "gravam_no_banco": len(conta(lambda x: x["grava_no_banco"])),
            "escrevem_ficheiro": len(conta(lambda x: x["escreve_ficheiro"])),
            "deitam_fora_alguma_coisa": len(deita_fora),
            "deitam_fora_SEM_escrever_o_motivo": len(sem_motivo),
            "ficheiros_com_decisao_escondida": len(escondidas),
            "decisoes_escondidas_ao_todo": sum(len(d) for _, d in escondidas),
        },
        "LISTAS": {
            "pontos_de_entrada": entradas,
            "executores": executores,
            "orfaos": orfaos,
            "sem_aresta_medida": sem_aresta,
            "deitam_fora_sem_motivo": sem_motivo,
            "decisoes_escondidas": [{"ficheiro": f, "linhas": d} for f, d in escondidas],
        },
    }


def main() -> int:
    d = medir()
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    r = d["RESUMO"]
    print("CENSO DA COLETA — o que existe hoje\n")
    for k, v in r.items():
        print(f"  {str(v).rjust(4)}  {k.replace('_', ' ')}")
    print(f"\n  escrito em {SAIDA.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
