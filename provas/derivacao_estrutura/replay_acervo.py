#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPLAY DO ACERVO, ANTES × DEPOIS — DERIVACAO-ESTRUTURA (28/09).

Para cada página HTML guardada no armazém (`<armazem>/**/OBSERVATION/*.html`), mede:

    ANTES   `limpar()` do commit base (CÓPIA LITERAL, marcada abaixo)
            `tempo_de_publicacao()` do commit base (lido do git, em memória)
    DEPOIS  `limpar()` e `tempo_de_publicacao()` desta árvore

e, para os dois textos, o `corpo()` VIVO (`leis/fato_do_texto.py`, não mexido).

MEDIDA DE CONTEÚDO (V2): por página, `PALAVRAS_PERDIDAS_DO_TEXTO` = palavras de conteúdo
(>= 4 letras) do `corpo()` ANTES que não aparecem em NENHUM lugar do TEXTO DEPOIS; no
RESUMO, `PAGINAS_COM_PERDA_NO_TEXTO` e `MELHORARAM / IGUAIS / PIORARAM` (critério escrito
em `CRITERIO_DO_VEREDITO`).

    py provas/derivacao_estrutura/replay_acervo.py --armazem <pasta> --saida <pasta>

SÓ LEITURA. SEM REDE. NADA ESCRITO FORA DE `--saida`:
  · `sys.dont_write_bytecode` — nem `__pycache__` nasce;
  · `socket.socket` trocado por uma armadilha antes de importar o que quer que seja
    da casa: uma tentativa de rede rebenta, não passa em silêncio;
  · o executor base lê-se com `git show <BASE>:<ficheiro>` (leitura do repositório
    local) ou de `--executor-base <ficheiro>`; sem nenhum dos dois, o script PÁRA —
    não inventa o «antes».

Saída: `<saida>/REPLAY-DERIVACAO-ESTRUTURA.json` (uma linha por página + RESUMO), e o
RESUMO impresso.
"""
import sys

sys.dont_write_bytecode = True

import socket  # noqa: E402


class _SemRede(socket.socket):
    def __init__(self, *a, **k):
        raise RuntimeError("REDE PROIBIDA: o replay e so leitura, sem rede")


socket.socket = _SemRede

import argparse  # noqa: E402
import datetime  # noqa: E402
import html  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402
import types  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for g in (RAIZ, os.path.join(RAIZ, "leis")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas  # noqa: E402,F401
from coleta import executor_texto_de_html as DEPOIS  # noqa: E402
from coleta.texto_fonte import limpar as limpar_depois  # noqa: E402
import fato_do_texto as FT  # noqa: E402

BASE = "e24139702b8216ad54127cf63a14b550bcd4aeab"   # servico-20260923-0923 (o vivo)
FICHEIRO_EXECUTOR = "coleta/executor_texto_de_html.py"
FICHEIRO_LIMPAR = "coleta/texto_fonte.py"
PALAVRAS_MINIMAS_DO_CORPO = 20


# ═══ CÓPIA LITERAL — `coleta/texto_fonte.py::limpar` @ e24139702 (linhas 64-73) ═══
# NÃO EDITAR. O script confere-a contra o git quando pode (COPIA_LITERAL_CONFERIDA).
def _pdf_antes(dados):
    from coleta.texto_fonte import _pdf  # o ramo PDF nao mudou
    return _pdf(dados)


def limpar_antes(dados, ctype=''):
    if 'pdf' in ctype.lower() or dados[:5] == b'%PDF-':
        return _pdf_antes(dados)
    t = dados.decode('utf-8', errors='replace')
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'[ \t\xa0]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return '\n'.join(l.strip() for l in t.split('\n') if l.strip())
# ═══ FIM DA CÓPIA LITERAL ═══════════════════════════════════════════════════════

_CORPO_DA_COPIA = [
    "    t = dados.decode('utf-8', errors='replace')",
    "    t = re.sub(r'<(script|style)\\b.*?</\\1>', ' ', t, flags=re.S | re.I)",
    "    t = re.sub(r'<[^>]+>', ' ', t)",
    "    t = html.unescape(t)",
    "    t = re.sub(r'[ \\t\\xa0]+', ' ', t)",
    "    t = re.sub(r'\\n\\s*\\n+', '\\n', t)",
    "    return '\\n'.join(l.strip() for l in t.split('\\n') if l.strip())",
]


def _git_show(caminho):
    try:
        r = subprocess.run(["git", "show", "%s:%s" % (BASE, caminho)], cwd=RAIZ,
                           capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def conferir_copia():
    src = _git_show(FICHEIRO_LIMPAR)
    if src is None:
        return "NAO SEI (git show %s:%s indisponivel)" % (BASE[:9], FICHEIRO_LIMPAR)
    m = re.search(r"^def limpar\(dados, ctype=''\):\n(.*?)(?=^\S)", src, re.S | re.M)
    if not m:
        return "NAO SEI (limpar() nao encontrada no base)"
    linhas = [l for l in m.group(1).rstrip("\n").split("\n") if l.strip()][2:]
    return "SIM" if linhas == _CORPO_DA_COPIA else "NAO — a copia diverge do base"


def carregar_executor_base(caminho=None):
    if caminho:
        with open(caminho, encoding="utf-8") as fh:
            src, origem = fh.read(), caminho
    else:
        src, origem = _git_show(FICHEIRO_EXECUTOR), "git show %s:%s" % (BASE[:9], FICHEIRO_EXECUTOR)
    if not src:
        raise SystemExit("PARADO: sem o executor base nao ha «antes» (use --executor-base <ficheiro> "
                         "com %s @ %s)" % (FICHEIRO_EXECUTOR, BASE[:9]))
    mod = types.ModuleType("executor_texto_de_html_base")
    mod.__file__ = os.path.join(RAIZ, FICHEIRO_EXECUTOR)
    exec(compile(src, origem, "exec"), mod.__dict__)
    return mod, origem


def paginas(armazem, qualquer_html=False):
    for d, _sub, fs in os.walk(armazem):
        if not qualquer_html and os.path.basename(d) != "OBSERVATION":
            continue
        for f in sorted(fs):
            if f.lower().endswith((".html", ".htm")):
                yield os.path.join(d, f)


def _palavras(t):
    return len(re.findall(r"[A-Za-zÀ-ÿ']+", t))


#: Datas em prosa italiana (dia · mês · ano) — só para CONTAR as que o `corpo()` deixa cair.
#: Não é régua de nada: é um alarme para o elo 4 (tempo do facto), que este ramo não toca.
_RE_DATA_PROSA = re.compile(
    r"\b\d{1,2}\s*(?:[–-]\s*\d{1,2}\s+)?(?:%s)\.?\s+\d{4}\b"
    % "|".join(sorted(DEPOIS.MESES_IT, key=len, reverse=True)), re.I)


#: MEDIDA DE CONTEÚDO (a do coordenador, 28/09 — DERIVACAO-ESTRUTURA-V2). Não é tamanho:
#: é «palavra de conteúdo que o leitor via e deixou de existir». Palavra de conteúdo =
#: sequência de 4 ou mais LETRAS (sem algarismo nem `_`), comparada em minúsculas.
_RE_PALAVRA_DE_CONTEUDO = re.compile(r"[^\W\d_]{4,}")
CRITERIO_DO_VEREDITO = (
    "PIOROU = alguma palavra de conteudo (>=4 letras, minusculas) do corpo() ANTES nao aparece "
    "em NENHUM lugar do TEXTO DEPOIS (perdeu conteudo do TEXTO, nao so do corpo); "
    "MELHOROU = nao piorou e o corpo() DEPOIS tem palavras de conteudo que o corpo() ANTES nao "
    "tinha (o filtro por linha passou a ver texto que ja existia); IGUAL = o resto. Palavra que sai "
    "do corpo() mas continua no TEXTO nao e piora desta mudanca: e o filtro do elo 4, contada a parte "
    "em PAGINAS_EM_QUE_SO_O_CORPO_LARGA_PALAVRAS.")


def _palavras_de_conteudo(t):
    return {w.lower() for w in _RE_PALAVRA_DE_CONTEUDO.findall(t)}


def _datas_em_prosa(t):
    return {" ".join(m.group(0).lower().split()) for m in _RE_DATA_PROSA.finditer(t)}


def medir(caminho, base_mod):
    with open(caminho, "rb") as fh:
        dados = fh.read()
    antes, depois = limpar_antes(dados, "text/html"), limpar_depois(dados, "text/html")
    ca, cd = FT.corpo(antes), FT.corpo(depois)
    pa, pd = base_mod.tempo_de_publicacao(dados), DEPOIS.tempo_de_publicacao(dados)
    wca, wcd, wtd = _palavras_de_conteudo(ca), _palavras_de_conteudo(cd), _palavras_de_conteudo(depois)
    perdidas = sorted(wca - wtd)
    ganho_no_corpo = sorted(wcd - wca)
    veredito = "PIOROU" if perdidas else ("MELHOROU" if ganho_no_corpo else "IGUAL")
    return {
        "LINHAS_ANTES": len(antes.split("\n")) if antes else 0,
        "LINHAS_DEPOIS": len(depois.split("\n")) if depois else 0,
        "CHARS_ANTES": len(antes), "CHARS_DEPOIS": len(depois),
        "CORPO_ANTES": len(ca), "CORPO_DEPOIS": len(cd),
        "CORPO_PALAVRAS_ANTES": _palavras(ca), "CORPO_PALAVRAS_DEPOIS": _palavras(cd),
        "PUBLISHED_AT_ANTES": pa["VALOR"], "PUBLISHED_AT_BASE_ANTES": pa["BASE"],
        "PUBLISHED_AT_DEPOIS": pd["VALOR"], "PUBLISHED_AT_BASE_DEPOIS": pd["BASE"],
        "PUBLISHED_AT_PRECISAO_DEPOIS": pd["PRECISAO"],
        "PUBLISHED_AT_ORIGINAL_DEPOIS": pd["ORIGINAL"],
        "PORQUE_DEPOIS": pd["PORQUE"][-240:],
        "PALAVRAS_PERDIDAS_DO_TEXTO": perdidas,
        "PALAVRAS_QUE_SO_SAEM_DO_CORPO": sorted((wca - wcd) & wtd),
        "PALAVRAS_NOVAS_NO_CORPO": len(ganho_no_corpo),
        "VEREDITO": veredito,
        "DATAS_EM_PROSA_QUE_SAEM_DO_CORPO": sorted(_datas_em_prosa(ca) - _datas_em_prosa(cd)),
        "DATAS_EM_PROSA_QUE_ENTRAM_NO_CORPO": sorted(_datas_em_prosa(cd) - _datas_em_prosa(ca)),
    }


def resumir(linhas):
    ok = {k: v for k, v in linhas.items() if "ERRO" not in v}
    n = "NAO SEI"
    respondia = {k: v for k, v in ok.items() if v["PUBLISHED_AT_ANTES"] != n}
    muda = sorted(k for k, v in respondia.items()
                  if (v["PUBLISHED_AT_ANTES"], v["PUBLISHED_AT_BASE_ANTES"])
                  != (v["PUBLISHED_AT_DEPOIS"], v["PUBLISHED_AT_BASE_DEPOIS"]))
    ganha = sorted(k for k, v in ok.items()
                   if v["PUBLISHED_AT_ANTES"] == n and v["PUBLISHED_AT_DEPOIS"] != n)
    perde = sorted(k for k, v in ok.items()
                   if v["PUBLISHED_AT_ANTES"] != n and v["PUBLISHED_AT_DEPOIS"] == n)
    med = (lambda xs: statistics.median(xs) if xs else None)
    return {
        "PAGINAS": len(linhas), "ERROS": sorted(k for k in linhas if "ERRO" in linhas[k]),
        "SAEM_DE_1_LINHA": sum(1 for v in ok.values()
                               if v["LINHAS_ANTES"] == 1 and v["LINHAS_DEPOIS"] > 1),
        "UMA_LINHA_ANTES": sum(1 for v in ok.values() if v["LINHAS_ANTES"] == 1),
        "UMA_LINHA_DEPOIS": sum(1 for v in ok.values() if v["LINHAS_DEPOIS"] == 1),
        "MEDIANA_LINHAS_ANTES": med([v["LINHAS_ANTES"] for v in ok.values()]),
        "MEDIANA_LINHAS_DEPOIS": med([v["LINHAS_DEPOIS"] for v in ok.values()]),
        "CORPO_VAZIO_ANTES": sum(1 for v in ok.values() if v["CORPO_ANTES"] == 0),
        "CORPO_VAZIO_DEPOIS": sum(1 for v in ok.values() if v["CORPO_DEPOIS"] == 0),
        "CORPO_CRESCE": sum(1 for v in ok.values() if v["CORPO_DEPOIS"] > v["CORPO_ANTES"]),
        "CORPO_ENCOLHE": sum(1 for v in ok.values() if v["CORPO_DEPOIS"] < v["CORPO_ANTES"]),
        "CORPO_IGUAL": sum(1 for v in ok.values() if v["CORPO_DEPOIS"] == v["CORPO_ANTES"]),
        "CORPO_MENOS_DE_%d_PALAVRAS_DEPOIS" % PALAVRAS_MINIMAS_DO_CORPO: sorted(
            (k, v["CORPO_PALAVRAS_ANTES"], v["CORPO_PALAVRAS_DEPOIS"]) for k, v in ok.items()
            if v["CORPO_PALAVRAS_DEPOIS"] < PALAVRAS_MINIMAS_DO_CORPO),
        # MEDIDA DE CONTEUDO: tem de ficar so lixo de servidor, ou vazio
        "PAGINAS_COM_PERDA_NO_TEXTO": sorted(
            (k, v["PALAVRAS_PERDIDAS_DO_TEXTO"]) for k, v in ok.items()
            if v["PALAVRAS_PERDIDAS_DO_TEXTO"]),
        "CRITERIO_DO_VEREDITO": CRITERIO_DO_VEREDITO,
        "MELHORARAM": sum(1 for v in ok.values() if v["VEREDITO"] == "MELHOROU"),
        "IGUAIS": sum(1 for v in ok.values() if v["VEREDITO"] == "IGUAL"),
        "PIORARAM": sum(1 for v in ok.values() if v["VEREDITO"] == "PIOROU"),
        # alarme para o ELO 4: palavra que continua no TEXTO mas o corpo() larga
        "PAGINAS_EM_QUE_SO_O_CORPO_LARGA_PALAVRAS": sum(
            1 for v in ok.values() if v["PALAVRAS_QUE_SO_SAEM_DO_CORPO"]),
        "PUBLISHED_AT_RESPONDIA_ANTES": len(respondia),
        "PUBLISHED_AT_MUDA_ENTRE_AS_QUE_RESPONDIAM": muda,           # TEM DE SER []
        "PUBLISHED_AT_PERDE": perde,                                  # TEM DE SER []
        "PUBLISHED_AT_GANHA": [(k, ok[k]["PUBLISHED_AT_DEPOIS"], ok[k]["PUBLISHED_AT_BASE_DEPOIS"],
                                ok[k]["PUBLISHED_AT_ORIGINAL_DEPOIS"]) for k in ganha],
        "PUBLISHED_AT_GANHA_POR_BASE": {b: sum(1 for k in ganha
                                               if ok[k]["PUBLISHED_AT_BASE_DEPOIS"] == b)
                                        for b in sorted({ok[k]["PUBLISHED_AT_BASE_DEPOIS"]
                                                         for k in ganha})},
        # alarme para o ELO 4 (nao e desta mudanca decidir): linha curta com data que andava
        # colada numa linha longa achatada, e que o `corpo()` (filtro por linha) agora deixa cair
        "PAGINAS_COM_DATA_EM_PROSA_QUE_SAI_DO_CORPO": sorted(
            (k, v["DATAS_EM_PROSA_QUE_SAEM_DO_CORPO"]) for k, v in ok.items()
            if v["DATAS_EM_PROSA_QUE_SAEM_DO_CORPO"]),
        "PAGINAS_COM_DATA_EM_PROSA_QUE_ENTRA_NO_CORPO": sum(
            1 for v in ok.values() if v["DATAS_EM_PROSA_QUE_ENTRAM_NO_CORPO"]),
        "CONTROLO_NEGATIVO": "PASSA" if not muda and not perde else "FALHA",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--armazem", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--executor-base", default=None)
    ap.add_argument("--qualquer-html", action="store_true",
                    help="aceita .html em qualquer pasta (nao so OBSERVATION/) — para acervos de teste")
    a = ap.parse_args(argv)
    base_mod, origem = carregar_executor_base(a.executor_base)
    t0 = datetime.datetime.now(datetime.timezone.utc)
    linhas = {}
    for p in paginas(a.armazem, a.qualquer_html):
        k = os.path.relpath(p, a.armazem).replace(os.sep, "/")
        try:
            linhas[k] = medir(p, base_mod)
        except Exception as e:                                   # noqa: BLE001
            linhas[k] = {"ERRO": "%s: %s" % (type(e).__name__, str(e)[:200])}
    resumo = resumir(linhas)
    fora = {
        "O_QUE_E": "replay offline antes x depois da DERIVACAO-ESTRUTURA (B1 limpar + B2 content-date) "
                   "+ V2 (limpar/3: etiqueta nao atravessa outro <) + medida de CONTEUDO",
        "BASE": BASE, "EXECUTOR_BASE_DE": origem, "COPIA_LITERAL_CONFERIDA": conferir_copia(),
        "EXECUTOR_VERSION_DEPOIS": DEPOIS.EXECUTOR_VERSION,
        "ARMAZEM": a.armazem, "INICIO_UTC": t0.isoformat(),
        "SEGUNDOS": round((datetime.datetime.now(datetime.timezone.utc) - t0).total_seconds(), 1),
        "RESUMO": resumo, "PAGINAS": linhas,
    }
    os.makedirs(a.saida, exist_ok=True)
    destino = os.path.join(a.saida, "REPLAY-DERIVACAO-ESTRUTURA.json")
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    curto = {k: (v if not isinstance(v, list) or len(v) <= 40 else v[:40] + ["… +%d" % (len(v) - 40)])
             for k, v in resumo.items()}
    print(json.dumps({"COPIA_LITERAL_CONFERIDA": fora["COPIA_LITERAL_CONFERIDA"],
                      "EXECUTOR_BASE_DE": origem, "SEGUNDOS": fora["SEGUNDOS"], "RESUMO": curto},
                     ensure_ascii=False, indent=1))
    print("gravado:", destino)
    return 0 if resumo["CONTROLO_NEGATIVO"] == "PASSA" and not resumo["ERROS"] else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                            # noqa: BLE001
        pass
    raise SystemExit(main())
