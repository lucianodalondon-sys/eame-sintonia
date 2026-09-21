#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DAS DUAS PORTAS — o codigo NOVO primeiro, e cada ataque provado.

    UM TESTE QUE PASSA NAO PROVA QUE ELE GUARDA ALGUMA COISA.
    SO O MUTANTE MORTO PROVA.

Cada ataque aqui:

    1. mede a BASE      os matadores tem de estar VERDES antes da mutacao.
                        Um matador que ja esta vermelho «mata» tudo, e nao
                        guarda nada. `VERIFICACAO QUE PASSA POR VAZIO`.
    2. aplica a MUTACAO uma troca de texto num ficheiro rastreado, e o
                        `git diff` prova que ela entrou. Sem o diff, «apliquei
                        a mutacao» e uma afirmacao minha sobre mim proprio.
    3. corre os MATADORES  pelo menos um tem de ficar VERMELHO.
    4. RESTAURA         `git checkout --` e o sha256 conferido. Um ataque
                        morto a meio deixa o defeito no repositorio, e a
                        cadeia inteira para com «ciclo nomeado».

⚠️ ZERO REDE. O unico ataque que TENTA sair e o `M10`, e ele existe para
provar que o instrumento o apanha — a ligacao e travada, nunca completada.

⚠️ NENHUM MATADOR ITERA A ESTRUTURA QUE JULGA. Tres vezes na noite de
2026-09-21 o sobrevivente foi um teste tautologico. Os valores esperados dos
matadores estao escritos a mao em `tests/test_a_regra_de_t10.py` e
`tests/test_a_rota_do_html.py`.

    py provas/red_team_duas_portas.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "provas", "RED-TEAM-DUAS-PORTAS-V1.json")

HTML = "coleta/executor_texto_de_html.py"
ADM = "admissao/admissao.py"
ING = "coleta/ingresso.py"

#: Um matador e um comando. `None` no fim quer dizer «exit 0 = verde».
def unittest_(alvo):
    return ["py", "-m", "unittest", "-q", alvo]


def script_(caminho):
    return ["py", caminho]


MUTANTES = [
    {
        "ID": "M01-ROTA-HTML-DESLIGADA",
        "ATAQUE": "tirar o executor de HTML da lista de donos da derivacao. "
                  "A ficha CAPACIDADE fica intacta — e este e o ponto: "
                  "DECLARAR NAO E LIGAR.",
        "ALVO": ING,
        "DE": '"executor_texto_de_html")',
        "PARA": ')',
        "MATADORES": [
            unittest_("tests.test_a_rota_do_html.AEscolhaDoExecutorEPorEspecieDeclarada"),
            script_("provas/a_rota_do_html_atravessa.py"),
        ],
    },
    {
        "ID": "M02-VAZIO-PASSA-POR-EXTRACAO",
        "ATAQUE": "fazer o executor chamar «extracao feita» a um documento de "
                  "que nao saiu uma unica letra. PRODUZIR FICHEIRO VAZIO NAO "
                  "E SUCESSO.",
        "ALVO": HTML,
        "DE": "if sem_brancos == 0:",
        "PARA": "if False:",
        "MATADORES": [
            unittest_("tests.test_a_rota_do_html.OVazioNaoPassaPorExtracaoFeita"),
        ],
    },
    {
        "ID": "M03-UNIVERSO-SEM-REGUA-ENTRA",
        "ATAQUE": "um universo para o qual ninguem escreveu regua passa a "
                  "responder SIM. E a porta a inventar a lei que ela propria "
                  "diz nao inventar.",
        "ALVO": ADM,
        "DE": "if not palavras:",
        "PARA": "if not palavras and False:",
        "MATADORES": [
            unittest_("tests.test_a_regra_de_t10.OMaterialInvalidoNaoEntra"),
            unittest_("tests.test_a_regra_de_t2.APortaNaoGanhouRegraDeT2"),
        ],
    },
    {
        "ID": "M04-SIM-AUTOMATICO",
        "ATAQUE": "a regua de universo passa a dizer SIM a tudo o que lhe "
                  "chega. UMA REGRA QUE SO SABE DIZER SIM NAO E REGRA.",
        "ALVO": ADM,
        "DE": "if len(achadas) >= SINAIS_MINIMOS:",
        "PARA": "if True:",
        "MATADORES": [
            unittest_("tests.test_a_regra_de_t10.OMaterialValidoPodeSerSim"),
            unittest_("tests.test_a_regra_de_t10.OMaterialInsuficienteDaNaoSei"),
        ],
    },
    {
        "ID": "M05-UMA-PALAVRA-PROMOVE",
        "ATAQUE": "baixar os sinais minimos de dois para um. Uma palavra solta "
                  "pode ser acidente de substring, citacao de passagem ou "
                  "cabecalho — e passava a promover.",
        "ALVO": ADM,
        "DE": "SINAIS_MINIMOS = 2",
        "PARA": "SINAIS_MINIMOS = 1",
        "MATADORES": [
            unittest_("tests.test_a_regra_de_t10.OMaterialInsuficienteDaNaoSei"),
            unittest_("tests.test_a_regra_de_t10.OLexicoNaoApodrece"),
        ],
    },
    {
        "ID": "M06-PROVENIENCIA-DESAPARECE",
        "ATAQUE": "o texto sai sem dizer com que ferramenta foi feito. Um "
                  "texto de maquina sem maquina declarada nao se confere nem "
                  "se repete.",
        "ALVO": HTML,
        "DE": "tool=FERRAMENTA)",
        "PARA": "tool=None)",
        "MATADORES": [
            script_("provas/a_rota_do_html_atravessa.py"),
        ],
    },
    {
        "ID": "M07-RAW-SALTA-A-ADMISSAO",
        "ATAQUE": "o contrato de saida deixa de exigir SIM e passa a emitir "
                  "unidade para quem a porta recusou. ADMISSION SIM != READY, "
                  "e um NAO_SEI nao e um sim envergonhado.",
        "ALVO": ADM,
        "DE": "if decisao.resultado != SIM:",
        "PARA": "if False:",
        "MATADORES": [
            unittest_("tests.test_a_rota_do_html.OContratoDeSaidaRecusaSemSim"),
        ],
    },
    {
        "ID": "M08-HTML-MAU-ENTRA-COMO-MATERIA",
        "ATAQUE": "tirar a guarda dos bytes. Um PDF declarado `text/html` "
                  "passava a ser aberto pelo extractor de HTML, e a linha do "
                  "derivado saia carimbada `texto-de-html`.",
        "ALVO": HTML,
        "DE": "if dados[:5] == ASSINATURA_PDF:",
        "PARA": "if False:",
        "MATADORES": [
            unittest_("tests.test_a_rota_do_html.OsBytesQueNaoSaoHtmlNaoEntramAqui"),
        ],
    },
    {
        "ID": "M09-FACT-TIME-VIRA-PUBLISHED-AT",
        "ATAQUE": "encher o tempo do fato com a data em que a fonte publicou. "
                  "Enche a estatistica e apaga a pergunta.",
        "ALVO": ADM,
        "DE": '"FACT_TIME": item.get("fact_time") or AUSENCIA,',
        "PARA": '"FACT_TIME": item.get("fact_time") or _ou_nao_sei("published_at"),',
        "MATADORES": [
            unittest_("tests.test_a_rota_do_html.OTempoEOLugarNaoSePreenchem"),
        ],
    },
    {
        "ID": "M10-FACT-LOCATION-VIRA-SOURCE-LOCATION",
        "ATAQUE": "encher o lugar do fato com o lugar de quem publica. Onde "
                  "esta a redaccao nao e onde o fato aconteceu.",
        "ALVO": ADM,
        "DE": '"FACT_LOCATION": item.get("fact_location", AUSENCIA),',
        "PARA": '"FACT_LOCATION": item.get("fact_location") or item.get("source_location", AUSENCIA),',
        "MATADORES": [
            unittest_("tests.test_a_rota_do_html.OTempoEOLugarNaoSePreenchem"),
        ],
    },
    {
        "ID": "M11-A-DERIVACAO-VAI-A-REDE",
        "ATAQUE": "a extracao abre uma ligacao para fora a meio do "
                  "reprocessamento. Ligacao a um IP literal, para o ataque "
                  "bater no remendo do socket e nao no DNS.",
        "ALVO": HTML,
        "DE": '    sem_brancos = len("".join(texto.split()))',
        "PARA": ('    __import__("socket").create_connection('
                 '("93.184.216.34", 80), 2); '
                 'sem_brancos = len("".join(texto.split()))'),
        "MATADORES": [
            script_("provas/a_rota_do_html_nao_vai_a_rede.py"),
        ],
    },
    {
        "ID": "M12-A-ROTA-DO-HTML-ROUBA-O-PDF",
        "ATAQUE": "o executor de HTML declara tambem `application/pdf`. Dois "
                  "donos da mesma especie, e o segundo ganha por acidente de "
                  "ordem de importacao.",
        "ALVO": HTML,
        "DE": 'ACEITA = ("text/html", "application/xhtml+xml")',
        "PARA": 'ACEITA = ("text/html", "application/xhtml+xml", "application/pdf")',
        "MATADORES": [
            unittest_("tests.test_a_rota_do_html.AEscolhaDoExecutorEPorEspecieDeclarada"),
            script_("provas/a_rota_do_html_atravessa.py"),
        ],
    },
    {
        "ID": "M13-SOCI-VOLTA-A-T7",
        "ATAQUE": "devolver a T7 o termo que casa dentro de «sociale», "
                  "«social» e «association» — e que produzia 26 NAO falsos.",
        "ALVO": ADM,
        "DE": '"divulgazione tecnica"],',
        "PARA": '"divulgazione tecnica", "soci"],',
        "MATADORES": [
            unittest_("tests.test_a_regra_de_t10.OLexicoNaoApodrece"),
            unittest_("tests.test_a_regra_de_t2.APortaNaoGanhouRegraDeT2"),
        ],
    },
    {
        "ID": "M14-DUAS-FORMAS-DA-MESMA-PALAVRA",
        "ATAQUE": "acrescentar a T10 uma forma que contem outra da lista. Uma "
                  "unica ocorrencia de «importazione» passava a valer DOIS "
                  "sinais, e a regua dos SINAIS_MINIMOS deixava de valer sem "
                  "ninguem dar por isso.",
        "ALVO": ADM,
        "DE": '"exportacao", "exportacoes"],',
        "PARA": '"exportacao", "exportacoes", "importazione"],',
        "MATADORES": [
            unittest_("tests.test_a_regra_de_t10.OLexicoNaoApodrece"),
            unittest_("tests.test_a_regra_de_t2.APortaNaoGanhouRegraDeT2"),
        ],
    },
]


def _sha(caminho):
    with open(os.path.join(RAIZ, caminho), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _correr(cmd):
    """Um matador, em interpretador LIMPO. Devolve (verde, cauda da saida).

    ⚠️ SUBPROCESSO DE PROPOSITO. Correr os matadores neste processo deixaria
    o modulo mutado em `sys.modules`, e o `importlib.reload` nao resolve: a
    porta importa `admissao` por tres caminhos diferentes. Um interpretador
    novo le o ficheiro do disco, que e onde a mutacao esta.
    """
    # ⚠️ `PYTHONDONTWRITEBYTECODE` NAO CHEGOU, E O PORQUE FICA ESCRITO.
    # O `M05` trocava `SINAIS_MINIMOS = 2` por `= 1`: MESMO TAMANHO, e escrito
    # no mesmo segundo do import anterior. O `.pyc` guarda (mtime em segundos,
    # tamanho) e valida-se por esses dois — nenhum dos dois mudou, e o
    # interpretador novo carregou o ficheiro ANTIGO do cache. O ataque foi
    # aplicado (o `git diff` prova-o) e o matador nunca o chegou a ver.
    #
    #     UM MUTANTE QUE NAO MUDA O TAMANHO E QUE CABE NO MESMO SEGUNDO
    #     E INVISIVEL PARA O IMPORT. ELE «SOBREVIVE» SEM NUNCA TER CORRIDO.
    #
    # Esta variavel impede de ESCREVER cache novo; nao impede de LER o velho.
    # Por isso o cache do alvo e apagado em `aplicar()`.
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    # Nenhum matador escreve na Sala; e a variavel da Sala sai do ambiente
    # para que nenhum deles a possa alcancar por acidente.
    for v in ("SINTONIA_SALA_BACKEND", "SINTONIA_SALA_DSN",
              "SINTONIA_COLLECTION_DSN", "BANCO_DESCARTAVEL_URL"):
        env.pop(v, None)
    r = subprocess.run(cmd, cwd=RAIZ, env=env, capture_output=True, timeout=600)
    saida = (r.stdout + r.stderr).decode("utf-8", "replace")
    return r.returncode == 0, saida.strip()[-400:]


def _git_diff(caminho):
    r = subprocess.run(["git", "diff", "-U0", "--", caminho],
                       cwd=RAIZ, capture_output=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


def _apagar_cache(caminho):
    """O `.pyc` do alvo, fora do caminho. Ver a nota em `_correr`."""
    pasta = os.path.join(RAIZ, os.path.dirname(caminho), "__pycache__")
    base = os.path.basename(caminho)[:-3] + "."
    if not os.path.isdir(pasta):
        return []
    fora = []
    for nome in os.listdir(pasta):
        if nome.startswith(base) and nome.endswith(".pyc"):
            try:
                os.remove(os.path.join(pasta, nome))
                fora.append(nome)
            except OSError:
                pass
    return fora


def _restaurar(caminho):
    subprocess.run(["git", "checkout", "--", caminho], cwd=RAIZ,
                   capture_output=True, timeout=120)
    _apagar_cache(caminho)


def aplicar(m):
    """Troca o texto no ficheiro. Devolve o sha ANTES, ou levanta."""
    alvo = os.path.join(RAIZ, m["ALVO"])
    antes = _sha(m["ALVO"])
    with open(alvo, "rb") as fh:
        bruto = fh.read()
    de = m["DE"].encode("utf-8")
    quantas = bruto.count(de)
    if quantas != 1:
        raise RuntimeError("a ancora de %s aparece %d vezes em %s (tem de ser "
                           "1): %r" % (m["ID"], quantas, m["ALVO"], m["DE"]))
    with open(alvo, "wb") as fh:
        fh.write(bruto.replace(de, m["PARA"].encode("utf-8"), 1))
    # O cache do alvo sai daqui. Sem isto, um mutante do MESMO TAMANHO escrito
    # no mesmo segundo do import anterior e carregado do `.pyc` velho.
    _apagar_cache(m["ALVO"])
    return antes


def atacar(m):
    fora = {"ID": m["ID"], "ATAQUE": m["ATAQUE"], "ALVO": m["ALVO"],
            "DE": m["DE"], "PARA": m["PARA"]}

    # ── 1 · A BASE. Um matador ja vermelho nao guarda nada. ────────────────
    base = []
    for cmd in m["MATADORES"]:
        verde, cauda = _correr(cmd)
        base.append({"MATADOR": " ".join(cmd), "VERDE_ANTES": verde,
                     "CAUDA": "" if verde else cauda})
    fora["BASE"] = base
    if not all(b["VERDE_ANTES"] for b in base):
        fora["MUTANT_APPLIED"] = False
        fora["MUTANT_KILLED"] = False
        fora["VEREDICTO"] = ("INVALIDO: um matador ja estava vermelho antes "
                             "da mutacao. Um teste que ja falha «mata» "
                             "qualquer coisa.")
        return fora

    # ── 2 · A MUTACAO, e o `git diff` a prova-la ───────────────────────────
    antes = None
    try:
        antes = aplicar(m)
        diff = _git_diff(m["ALVO"])
        fora["MUTANT_APPLIED"] = bool(diff.strip())
        fora["GIT_DIFF"] = [l for l in diff.splitlines()
                            if l.startswith(("+", "-")) and
                            not l.startswith(("+++", "---"))][:6]
        fora["SHA_ANTES"] = antes
        fora["SHA_MUTADO"] = _sha(m["ALVO"])

        # ── 3 · OS MATADORES ────────────────────────────────────────────
        depois = []
        for cmd in m["MATADORES"]:
            verde, cauda = _correr(cmd)
            depois.append({"MATADOR": " ".join(cmd), "VERDE_DEPOIS": verde,
                           "CAUDA": "" if verde else cauda})
        fora["DEPOIS"] = depois
        fora["MUTANT_KILLED"] = any(not d["VERDE_DEPOIS"] for d in depois)
        fora["QUEM_MATOU"] = [d["MATADOR"] for d in depois
                              if not d["VERDE_DEPOIS"]]
    finally:
        # ── 4 · O RESTAURO, CONFERIDO ───────────────────────────────────
        _restaurar(m["ALVO"])
        fora["SHA_RESTAURADO"] = _sha(m["ALVO"])
        fora["RESTAURADO"] = (antes is None or
                              fora["SHA_RESTAURADO"] == antes)

    fora["VEREDICTO"] = ("MUTANT_KILLED" if fora.get("MUTANT_KILLED")
                         else "SURVIVOR")
    return fora


def main(argv):
    # A arvore tem de estar limpa: um ataque sobre um ficheiro ja alterado
    # nao se consegue restaurar com `git checkout`.
    sujo = subprocess.run(["git", "status", "--porcelain", "--",
                           HTML, ADM, ING],
                          cwd=RAIZ, capture_output=True, timeout=120)
    if sujo.stdout.strip():
        print("RECUSADO: os alvos nao estao limpos no Git. `git checkout --` "
              "nao os saberia restaurar.\n"
              + sujo.stdout.decode("utf-8", "replace"))
        return 2

    so = [a for a in argv if a.startswith("M")]
    lista = [m for m in MUTANTES if not so or m["ID"].split("-")[0] in so]

    resultados = []
    for m in lista:
        print("\n" + "=" * 70)
        print("%s · %s" % (m["ID"], m["ALVO"]))
        r = atacar(m)
        resultados.append(r)
        print("  APPLIED=%s  KILLED=%s  RESTAURADO=%s  %s"
              % (r.get("MUTANT_APPLIED"), r.get("MUTANT_KILLED"),
                 r.get("RESTAURADO"), r["VEREDICTO"]))
        for q in r.get("QUEM_MATOU") or []:
            print("    morto por: %s" % q)

    sobreviventes = [r["ID"] for r in resultados if not r.get("MUTANT_KILLED")]
    nao_restaurados = [r["ID"] for r in resultados if not r.get("RESTAURADO")]
    censo = {
        "PROVA": "provas/red_team_duas_portas.py",
        "MUTANTES": len(resultados),
        "MUTANT_APPLIED_TODOS": all(r.get("MUTANT_APPLIED")
                                    for r in resultados),
        "MUTANT_KILLED": sum(1 for r in resultados if r.get("MUTANT_KILLED")),
        "SURVIVORS": len(sobreviventes),
        "QUEM_SOBREVIVEU": sobreviventes,
        "NAO_RESTAURADOS": nao_restaurados,
        "ARVORE_LIMPA_NO_FIM": not subprocess.run(
            ["git", "status", "--porcelain", "--", HTML, ADM, ING],
            cwd=RAIZ, capture_output=True, timeout=120).stdout.strip(),
        "RESULTADOS": resultados,
    }
    with open(SAIDA, "w", encoding="utf-8") as fh:
        json.dump(censo, fh, indent=1, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("MUTANTES              %d" % censo["MUTANTES"])
    print("MUTANT_KILLED         %d" % censo["MUTANT_KILLED"])
    print("SURVIVORS             %d %s" % (censo["SURVIVORS"],
                                           censo["QUEM_SOBREVIVEU"] or ""))
    print("ARVORE_LIMPA_NO_FIM   %s" % censo["ARVORE_LIMPA_NO_FIM"])
    print("  escrito: %s" % SAIDA)
    return 0 if (censo["SURVIVORS"] == 0
                 and censo["ARVORE_LIMPA_NO_FIM"]
                 and not nao_restaurados) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
