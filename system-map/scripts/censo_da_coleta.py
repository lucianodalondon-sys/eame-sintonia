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
sys.path.insert(0, str(Path(__file__).resolve().parent))
import impressao_da_arvore as IMPRESSAO          # noqa: E402
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


def quem_chama(todos: list) -> dict:
    """Quem importa ou corre quem. Medido, nao suposto."""
    chamado_por: dict[str, set] = {f: set() for f in todos}
    nome = {Path(f).stem: f for f in todos}

    for f in todos:
        t = (RAIZ / f).read_text(encoding="utf-8", errors="replace")
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
        # e quem e citado pelo caminho inteiro (subprocess, workflow, doc)
        for outro in todos:
            if outro != f and outro in t:
                chamado_por[outro].add(f)
    return {k: sorted(v) for k, v in chamado_por.items()}


def nos_workflows(todos: list) -> dict:
    wf = RAIZ / ".github" / "workflows"
    texto = ""
    if wf.is_dir():
        for p in sorted(wf.glob("*.yml")):
            texto += p.read_text(encoding="utf-8", errors="replace")
    return {f: (f in texto) for f in todos}


def medir() -> dict:
    todos = ficheiros()
    chamado = quem_chama(todos)
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
            "no_ci": em_ci[f],
        })

    def conta(cond) -> list:
        return [x["ficheiro"] for x in fichas if cond(x)]

    orfaos = conta(lambda x: not x["chamado_por"] and not x["no_ci"])
    executores = conta(lambda x: x["sai_para_fora"])
    entradas = conta(lambda x: x["e_ponto_de_entrada"])
    deita_fora = conta(lambda x: x["descarta"])
    sem_motivo = conta(lambda x: x["descarta"] and not x["escreve_o_motivo_do_descarte"])
    escondidas = [(x["ficheiro"], x["decisoes_escondidas"])
                  for x in fichas if x["decisoes_escondidas"]]

    return {
        "SCHEMA": "sintonia.censo-da-coleta/1",
        # As entradas deste censo sao os ficheiros de codigo das gavetas — a
        # lista sai da propria medicao, e nao de um palpite sobre o que ele le.
        "PROVENANCE": dict(
            IMPRESSAO.carimbo("system-map/scripts/censo_da_coleta.py",
                              [(f, IMPRESSAO.FONTE, "medir() · read_text")
                               for f in sorted(todos)]),
            GAVETAS=list(GAVETAS)),
        "FICHEIROS": fichas,
        "RESUMO": {
            "ficheiros_de_codigo": len(todos),
            "pontos_de_entrada": len(entradas),
            "executores_que_saem_para_fora": len(executores),
            "sem_chamador_e_fora_do_ci": len(orfaos),
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
