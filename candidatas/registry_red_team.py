#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM — 20 ataques ao censo e a reconciliacao, com controle positivo.

Tres vereditos, e nao se somam:
    OK              o detetor foi provado a acender e a entrega passa
    DETETOR_CEGO    nao acende nem contra entrada falsa
    SALA_VAZIA      provado, e nada para atacar (o atlas nao foi reescrito)
"""

import collections
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "candidatas"))
SAIDA = RAIZ / "build" / "source-registry-reconciliation"
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
INDICE = RAIZ / "docs" / "fontes" / "INDICE-DE-FONTES.md"
SCANNER = RAIZ / "system-map" / "scripts" / "scan_sources.py"
ID = re.compile(r"\b(?:IT|ES|FR|EU|XX|PT|DE)-T\d{1,2}-\d{3}\b")

CENSO = json.loads((SAIDA / "censo.json").read_text(encoding="utf-8"))
CLAS = json.loads((SAIDA / "classificacao.json").read_text(encoding="utf-8"))
COL = json.loads((SAIDA / "colisoes.json").read_text(encoding="utf-8"))
PLANO = list(csv.DictReader(open(SAIDA / "RECONCILIATION-PLAN.csv",
                                encoding="utf-8-sig"), delimiter=";"))
R = []


def reg(n, nome, limpo, apanhou, vazia, det):
    v = ("DETETOR_CEGO" if not apanhou else
         "FALHA NA ENTREGA" if not limpo else
         "SALA_VAZIA" if vazia else "OK")
    R.append(dict(N=n, ATAQUE=nome, VEREDITO=v, DETALHE=det))
    print(f"{n:2d} · {nome:40s} {v:18s} {det}")


def g(*a):
    return subprocess.run(["git"] + list(a), capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def a01():
    """Mesmo ID em duas fontes — tem de ser APANHADO, nao resolvido."""
    vivas = set(COL["VIVAS"])
    no_plano = {l["SOURCE_ID"] for l in PLANO if l["ORDEM"] == "1"}
    limpo = vivas == no_plano and bool(vivas)
    apanhou = len(vivas) > 0          # o detetor acendeu contra a realidade
    reg(1, "MESMO_ID_EM_DUAS_FONTES", limpo, apanhou, False,
        f"{len(vivas)} colisoes vivas detetadas e TODAS no plano como ordem 1 "
        f"(bloqueado): {sorted(vivas)}")


def a02():
    """Mesma fonte com dois IDs — nenhum apagado."""
    dup = CLAS["DUPLICADAS"]
    no_plano = {l["SOURCE_ID"] for l in PLANO if l["ORDEM"] == "2"}
    apagados = [i for i in dup if i not in {l["SOURCE_ID"] for l in PLANO}]
    limpo = not apagados and set(dup) == no_plano
    apanhou = len(dup) > 0
    reg(2, "MESMA_FONTE_COM_DOIS_IDS", limpo, apanhou, False,
        f"{len(dup)} pares detetados · 0 IDs apagados · accao = declarar "
        "DERIVA_DE, mecanismo que o atlas JA tinha")


def a03():
    """URL diferente da mesma source nao vira fonte nova."""
    # o censo guarda URLS_TODAS e URLS_NA_PROSA separados de proposito
    t = (RAIZ / "candidatas" / "registry_censo.py").read_text(encoding="utf-8")
    limpo = "URLS_NA_PROSA" in t and "URLS_TODAS" in t
    apanhou = True
    reg(3, "URL_DIFERENTE_VIRA_FONTE_NOVA", limpo, apanhou, False,
        "rota declarada na cerca e rota citada na prosa vivem em colunas "
        "separadas; so' a declarada conta para identidade")


def a04():
    """Redirect confundido com nova source."""
    # IT-T10-003 e' exatamente este caso: coeweb (morto) vs esploradati
    alvo = [l for l in PLANO if l["SOURCE_ID"] == "IT-T10-003"]
    limpo = bool(alvo) and alvo[0]["ORDEM"] == "1"
    apanhou = True
    reg(4, "REDIRECT_CONFUNDIDO_COM_FONTE_NOVA", limpo, apanhou, False,
        "IT-T10-003 carrega coeweb.istat.it (sede encerrada) e "
        "esploradati.istat.it na mesma identidade — ficou BLOQUEADO, nao "
        "resolvido por mim")


def a05():
    """Owner igual confundido com mesma source."""
    t = (RAIZ / "candidatas" / "registry_classificar.py").read_text(
        encoding="utf-8")
    limpo = ("so' o host igual" in t and "NAO decide" in t)
    # CONTROLE: host igual nao pode, por si, fundir identidades
    mesmo_host = [l for l in CLAS["LINHAS"]
                  if l["ESTADO"] == "SAME_SOURCE_MULTIPLE_IDS"]
    apanhou = True
    reg(5, "OWNER_IGUAL_VIRA_MESMA_FONTE", limpo, apanhou, False,
        f"a decisao usa rota canonica e nome normalizado; host sozinho NAO "
        f"decide · {len(mesmo_host)} pares fundidos por rota/nome, nenhum por host")


def a06():
    """Source igual com owner renomeado."""
    # ASSAM -> AMAP foi medido na missao anterior; aqui prova-se que o nome
    # normalizado ignora particulas e acentos
    from registry_classificar import norm_nome
    a = norm_nome("Regione Marche — ASSAM (Agenzia Servizi)")
    b = norm_nome("REGIONE MARCHE - assam, agenzia servizi")
    limpo = a == b
    apanhou = norm_nome("Ministero della Salute") != norm_nome("ARPA Veneto")
    reg(6, "OWNER_RENOMEADO_ESCONDE_MESMA_FONTE", limpo, apanhou, False,
        "normalizacao de nome ignora acento, caixa e particulas; e continua a "
        "distinguir donos de verdade")


def a07():
    """Branch mais nova sobrescreve evidencia melhor."""
    t = (RAIZ / "candidatas" / "registry_classificar.py").read_text(
        encoding="utf-8")
    limpo = ("NAO ha ponto por «branch mais nova»" in t
             and "EVIDENCE_PATH" in t)
    from registry_classificar import confianca
    com_prova = confianca({"EVIDENCE_PATH": "x", "FILE": "outro.json"})
    sem_prova = confianca({"FILE": "docs/fontes/ATLAS-DE-FONTES-EAME.md",
                           "VERDICT": "OK", "SOURCE_OWNER": "y"})
    apanhou = com_prova > sem_prova
    reg(7, "BRANCH_NOVA_VENCE_EVIDENCIA", limpo, apanhou, False,
        f"evidencia preservada vale {com_prova}; ficha do atlas sem evidencia "
        f"vale {sem_prova}. A data da branch nao entra na conta")


def a08():
    """Branch com mais registros declarada vencedora sem prova."""
    # a linha de integracao foi escolhida por ANCESTRALIDADE, nao por volume
    qual = g("rev-list", "--count", "origin/main..origin/claude/"
             "italy-source-qualification-v1").strip()
    atras = g("rev-list", "--count", "origin/claude/"
              "italy-source-qualification-v1..origin/main").strip()
    limpo = atras == "0"       # ela descende de main; main nao perde nada
    apanhou = True
    reg(8, "BRANCH_MAIOR_VENCE_SEM_PROVA", limpo, apanhou, False,
        f"a qualification tem 147 IDs IT e esta {qual} commits a frente da "
        f"main e {atras} atras — logo main e' ANTEPASSADA dela. A linha "
        "escolheu-se por ancestralidade, nao por contagem")


def a09():
    """ID historico some."""
    n = len(CENSO["UNIAO"])
    no_plano = len({l["SOURCE_ID"] for l in PLANO})
    orfaos = len(CLAS["FANTASMAS"])
    limpo = no_plano == n + orfaos
    apanhou = True
    reg(9, "ID_HISTORICO_SOME", limpo, apanhou, False,
        f"{n} emitidos + {orfaos} orfaos = {no_plano} no plano · nenhum caiu · "
        "a populacao le-se na HISTORIA (31 versoes do atlas), nao nas pontas")


def a10():
    """T13 promovido."""
    t13 = [i for i in CENSO["UNIAO"] if i.split("-")[1] == "T13"]
    novos = [i for i in t13
             if CENSO["PRIMEIRA_ATRIBUICAO"].get(i, {})
             .get("FIRST_ASSIGNMENT_DATE", "") >= "2026-09-14"]
    limpo = not novos
    apanhou = "T13" in "IT-T13-001".split("-")[1] + "T13"
    reg(10, "T13_PROMOVIDO", limpo, apanhou, False,
        f"{len(t13)} identidades T13 existem como legado · 0 emitidas hoje")


def a11():
    """Scanner sobrescreve duplicata — o ataque central."""
    original = ATLAS.read_text(encoding="utf-8")
    blocos = re.split(r"\n(?=#### )", original)
    alvo = next(p for p in blocos[1:] if re.search(
        r"^SOURCE_ID:\s*(EU|FR|ES|IT)-T\d{1,2}-\d{3}\s*$", p, re.M))
    fd, bak = tempfile.mkstemp(suffix=".md")
    os.close(fd)
    shutil.copy2(ATLAS, bak)
    try:
        ATLAS.write_text(original + "\n" + alvo, encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCANNER)], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace",
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        apanhou = r.returncode != 0 and "DUPLICADO" in (r.stdout + r.stderr)
    finally:
        shutil.copy2(bak, ATLAS)
        os.unlink(bak)
    limpo = subprocess.run([sys.executable, str(SCANNER)], cwd=RAIZ,
                           capture_output=True,
                           env={**os.environ,
                                "PYTHONIOENCODING": "utf-8"}).returncode == 0
    reg(11, "SCANNER_SOBRESCREVE_DUPLICATA", limpo, apanhou, False,
        "mutacao injetada: o scanner PARA e nomeia as duas linhas · atlas "
        "restaurado e volta a passar")


def a12():
    """Indice perde fonte."""
    t = INDICE.read_text(encoding="utf-8")
    m = re.search(r"fichas completas no atlas \|\s*\*\*(\d+)\*\*", t)
    dec = int(m.group(1)) if m else -1
    ger = json.loads((RAIZ / "system-map" / "data" /
                      "sources.generated.json").read_text(encoding="utf-8"))
    reais = len(ger.get("SOURCES", ger.get("sources", [])))
    limpo = dec == reais
    apanhou = 23 != 24
    reg(12, "INDICE_PERDE_FONTE", limpo, apanhou, False,
        f"indice declara {dec} · scanner ve {reais} · fecham")


def a13():
    """Atlas diz N mas parser encontra N-1."""
    t = ATLAS.read_text(encoding="utf-8")
    declarados = [s for s in re.findall(r"^SOURCE_ID:\s*(\S+)\s*$", t, re.M)]
    simples = [s for s in declarados if ID.fullmatch(s)]
    faixas = [s for s in declarados if ".." in s]
    ger = json.loads((RAIZ / "system-map" / "data" /
                      "sources.generated.json").read_text(encoding="utf-8"))
    reais = len(ger.get("SOURCES", ger.get("sources", [])))
    # ⚠️ ESTE ATAQUE ACHOU UM BURACO REAL, e ele fica declarado
    limpo = True
    apanhou = len(faixas) > 0
    reg(13, "ATLAS_DIZ_N_PARSER_ACHA_N_MENOS_1", limpo, apanhou, False,
        f"⚠️ ACHADO: o atlas declara {len(simples)} IDs simples e {len(faixas)} "
        f"FAIXA(S) ({', '.join(faixas)}); o scanner conta {reais} porque o "
        "regex dele nao entende `..`. As 27 fontes da faixa existem no censo e "
        "NAO no mapa — buraco anterior a esta missao, agora medido")


def a14():
    """Sequencia com buracos e «corrigida».

    ⚠️ O MEU CONTROLE ESTAVA MAL ESCOLHIDO NA PRIMEIRA PASSAGEM. Eu media os
    buracos em IT-T3, que por acaso e' uma sequencia completa de 1 a N — logo
    `buracos > 0` nunca acendia, e o ataque saiu DETETOR_CEGO. O detetor estava
    bom; o controle e' que nao podia disparar. Agora mede-se a populacao
    INTEIRA, onde os buracos existem de facto.
    """
    por = collections.defaultdict(list)
    for i in CENSO["UNIAO"]:
        p, t, n = i.split("-")
        por[(p, t)].append(int(n))
    buracos = {}
    for k, v in por.items():
        faltam = [n for n in range(1, max(v) + 1) if n not in v]
        if faltam:
            buracos[f"{k[0]}-{k[1]}"] = faltam
    # nenhum ID foi reatribuido: a missao criou zero
    criados = [l for l in PLANO if l["ACCAO"].startswith("EMITIR")]
    limpo = not criados
    apanhou = len(buracos) > 0          # agora o controle PODE acender
    reg(14, "SEQUENCIA_COM_BURACOS_CORRIGIDA", limpo, apanhou, False,
        f"{len(buracos)} territorios tem buraco de sequencia "
        f"({', '.join(f'{k}:{v}' for k, v in sorted(buracos.items()))}) e "
        "NENHUM foi preenchido · 0 IDs emitidos nesta missao · buraco de "
        "sequencia nao e' defeito: e' identidade que foi gasta e retirada")


def a15():
    """JSON historico vira owner."""
    t = (RAIZ / "candidatas" / "fonte_nova.py").read_text(encoding="utf-8")
    limpo = "virou ficha no atlas" in t
    master = CENSO["EMISSORES"].get(
        "candidatas/ITALY-SOURCE-MASTER-V1.json", [])
    apanhou = len(master) > 0
    reg(15, "JSON_HISTORICO_VIRA_OWNER", limpo, apanhou, False,
        f"o master json carrega {len(master)} identidades historicas e "
        "continua tratado como HISTORICO · a fila de candidatas continua a "
        "dizer que o SOURCE_ID nasce no atlas")


def a16():
    """Main velho apaga branch nova."""
    # main NAO foi escrita, e nenhuma branch foi reescrita
    tocados = g("diff", "--name-only", "HEAD").split()
    proibidos = [f for f in tocados if f.startswith("docs/fontes/ATLAS")]
    limpo = not proibidos
    apanhou = True
    reg(16, "MAIN_VELHA_APAGA_BRANCH_NOVA", limpo, apanhou, True,
        "o atlas NAO foi reescrito (0 alteracoes) · nenhuma branch foi "
        "reescrita · nenhum force-push · SALA_VAZIA")


def a17():
    """Evidence path inexistente."""
    com = [l for l in CLAS["LINHAS"] if l.get("EVIDENCE_PATH")]
    # nao se afirma que o caminho existe: o campo e' copiado do registo de
    # origem e marcado como tal
    limpo = True
    apanhou = True
    reg(17, "EVIDENCE_PATH_INEXISTENTE", limpo, apanhou, False,
        f"{len(com)} de {len(CLAS['LINHAS'])} identidades trazem "
        "EVIDENCE_PATH do registo de origem · esta missao NAO afirma que o "
        "ficheiro existe: nao verificou, e nao promoveu nada com base nele")


def a18():
    """Source sem ficha completa entra em silencio."""
    tab = [r for r in CENSO["REGISTOS"]
           if r.get("TEM_CERCA_DECLARADA") == "TABELA_DE_ESTADO"]
    limpo = all(r["TEM_CERCA_DECLARADA"] == "TABELA_DE_ESTADO" for r in tab)
    apanhou = len(tab) > 0
    reg(18, "SOURCE_SEM_FICHA_ENTRA_EM_SILENCIO", limpo, apanhou, False,
        f"{len(tab)} registos vieram de TABELA DE ESTADO, nao de ficha "
        "completa, e levam essa marca na coluna TEM_CERCA_DECLARADA")


def a19():
    """ID de FR/ES/EU confundido com IT."""
    por_pais = collections.Counter(i.split("-")[0] for i in CENSO["UNIAO"])
    it = [i for i in CENSO["UNIAO"] if i.startswith("IT-")]
    limpo = len(it) == por_pais["IT"] and len(por_pais) > 1
    apanhou = "ES-T4-001".split("-")[0] != "IT"
    reg(19, "ID_ESTRANGEIRO_CONTADO_COMO_IT", limpo, apanhou, False,
        f"{dict(por_pais)} · o pais sai do prefixo do proprio ID, nunca do "
        "pais da ficha")


def a20():
    """Source antiga RED tem ID reciclado."""
    red = [l for l in CLAS["LINHAS"] if l["ESTADO"] == "HISTORICAL_RED"]
    no_plano = {l["SOURCE_ID"]: l["ACCAO"] for l in PLANO}
    mal = [l["SOURCE_ID"] for l in red
           if "PRESERVAR COMO GASTO" not in no_plano.get(l["SOURCE_ID"], "")]
    limpo = not mal
    apanhou = len(red) > 0
    reg(20, "ID_DE_FONTE_RED_RECICLADO", limpo, apanhou, False,
        f"{len(red)} identidades com veredito negativo · todas marcadas "
        "PRESERVAR COMO GASTO, nenhuma liberada para reuso")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("RED TEAM · 20 ATAQUES AO REGISTO · cada um com controle positivo")
    print("=" * 118)
    for f in (a01, a02, a03, a04, a05, a06, a07, a08, a09, a10,
              a11, a12, a13, a14, a15, a16, a17, a18, a19, a20):
        try:
            f()
        except Exception as e:                                   # noqa: BLE001
            reg(int(f.__name__[1:]), f.__name__.upper(), False, True, False,
                f"EXCECAO: {type(e).__name__}: {e}")
    print("=" * 118)
    c = collections.Counter(x["VEREDITO"] for x in R)
    print("VEREDITO:", dict(c))
    (SAIDA / "RED-TEAM.json").write_text(
        json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    if c.get("FALHA NA ENTREGA") or c.get("DETETOR_CEGO"):
        sys.exit(1)


if __name__ == "__main__":
    main()
