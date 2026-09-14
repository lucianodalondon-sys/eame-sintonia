#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O PORTAO DO CONTROL PLANE — os dentes do registo das autoridades.

    py controle/portao_do_controle.py           mede e compara com o chao
    py controle/portao_do_controle.py --fixar   grava o estado de hoje como chao
    py controle/portao_do_controle.py --migrar  traz o chao para esta linhagem, com prova

POR QUE ESTE FICHEIRO EXISTE
-----------------------------
`controle/AUTORIDADES-CANONICAS.json` diz quem manda. Sem este portao, essa frase
seria um pedido por favor: qualquer missao podia apagar uma autoridade, pôr uma
segunda Biblia canonica, duplicar o know-how, trocar o dono de um conceito sem
avisar ninguem — e nada reprovava.

    TEXTO NAO REPROVA NADA. PORTAO REPROVA.

DUAS FAMILIAS DE PROVA, E A DIFERENCA IMPORTA
----------------------------------------------
**INTEGRIDADE** — defeitos que nunca podem existir, nem hoje nem amanha. Dois
cartoes com o mesmo id. Dois donos para o mesmo conceito. Um handoff a governar.
O System Map a aparecer como dono da arquitetura. Uma aresta declarada pintada de
observada. Estes reprovam sempre, e nao ha chao que os desculpe.

**DIVIDA** — defeitos que a casa TEM hoje, medidos e contados: autoridades que
vivem fora desta arvore, copias divergentes, documentos que se dizem lei e nao
estao no registo. Exigir zero hoje reprovaria o repositorio inteiro na primeira
corrida, e a primeira coisa que alguem faria era desligar o portao.

    «ESTA TUDO CERTO» NAO E EXECUTAVEL HOJE. «NAO PIOROU» E.

O estado de hoje fica gravado em `controle/CHAO-DO-CONTROLE.json`. A partir daqui,
uma autoridade nova que desaparece faz o numero subir, e o portao reprova. Quando
alguem pagar a divida, `--fixar` desce o teto — e ele nunca mais sobe.

    A DIVIDA FICA A VISTA, COM NOME E NUMERO, EM VEZ DE VIRAR SILENCIO.

O QUE ESTE PORTAO NAO FAZ
--------------------------
Nao decide o que e lei. Isso esta no registo, escrito por gente. Ele so recusa
que o registo minta sobre si mesmo, e conta o que dói.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


# Substituiveis pela mesma razao que no censo: o red team ataca o codigo real
# sobre ficheiros temporarios, e nunca sobre o registo do repositorio.
def _caminho(env: str, omissao: Path) -> Path:
    v = os.environ.get(env)
    return Path(v) if v else omissao


REGISTO = _caminho("SINTONIA_CONTROLE_REGISTO",
                   RAIZ / "controle" / "AUTORIDADES-CANONICAS.json")
CENSO = _caminho("SINTONIA_CONTROLE_CENSO",
                 RAIZ / "system-map" / "data" / "controle.generated.json")
CHAO = _caminho("SINTONIA_CONTROLE_CHAO", RAIZ / "controle" / "CHAO-DO-CONTROLE.json")

# ══ QUANDO E QUE UM DOCUMENTO SE DECLARA LEI ════════════════════════════════
#
# Este detector ja foi uma procura de subcadeia: se o texto continha
# «CANONICAL_OWNER» em qualquer sitio, o documento era acusado de ser uma
# autoridade nao registada. Ele acusou dez, e os dez estavam inocentes:
#
#     DUPLICATE_CANONICAL_OWNERS = 0            um nome de metrica
#     CANONICAL_OWNER_FOUND?  SIM               uma pergunta respondida
#     o executor produz, o dono canonico persiste    prosa sobre OUTRO ficheiro
#     O3 escreve raw_asset fora do dono canonico     uma linha de red team
#
#     MENCIONAR UMA LEI NAO E PROMULGAR UMA.
#
# Um portao que conta mencoes cobra divida que nao existe, e a divida falsa
# esconde a verdadeira. A separacao tem de ser estrutural — nunca uma lista de
# ficheiros a ignorar, que so faz o defeito mudar de nome no dia seguinte.
#
# Tres formas contam, e todas as tres foram tiradas das autoridades REAIS deste
# repositorio, nao inventadas:
#
#   1 · RECLAMA-SE          a linha nomeia a chave E fala de si propria
#                           AGENTS.md:5  «Este ficheiro e o dono canonico das...»
#   2 · LEGISLA             a chave e o SUJEITO da linha, com valor a seguir
#                           BIBLIA-CANONICA-DA-COLETA.md:9  «CANONICAL_OWNER  este ficheiro»
#                           CLAUDE.md:33  «DESIGN_SOURCE_OF_TRUTH = ADAMA_...»
#   3 · NOMEIA-SE           a linha nomeia a chave E o proprio caminho do
#                           documento — o caso da tabela que se aponta a si
#
# E a palavra tem de ser a PALAVRA INTEIRA. `DUPLICATE_CANONICAL_OWNERS` nao
# contem a chave `CANONICAL_OWNER`: contem um identificador diferente que a
# carrega dentro. Foi assim que cinco dos dez entraram.
CHAVES_DE_LEI = (r"(?:CANONICAL_OWNER|DESIGN_SOURCE_OF_TRUTH|SOURCE_OF_TRUTH"
                 r"|dono can[oó]nico)")
PALAVRA_DE_LEI = re.compile(r"(?<![A-Za-z0-9_])" + CHAVES_DE_LEI + r"(?![A-Za-z0-9_])")
LEGISLA = re.compile(r"^[\s>*#_`-]*" + CHAVES_DE_LEI + r"(?![A-Za-z0-9_])\s*[:=]?\s+\S")
FALA_DE_SI = re.compile(
    r"est[ea]s? (?:ficheiro|documento|arquivo|lei|b[ií]blia|contrato|registo|registro)"
    r"|this (?:file|document)", re.I)


def declara_se_lei(caminho: str, linhas: list) -> tuple:
    """A linha em que este documento se promulga lei. `()` quando nenhuma.

    Devolve `(forma, numero_da_linha, trecho)` — e nunca um booleano, de
    proposito: quem for acusado por este portao tem direito a ver a linha.
    """
    nome = caminho.rsplit("/", 1)[-1]
    for i, ln in enumerate(linhas, 1):
        if not PALAVRA_DE_LEI.search(ln):
            continue
        if LEGISLA.match(ln):
            return ("LEGISLA", i, ln.strip()[:120])
        if FALA_DE_SI.search(ln):
            return ("RECLAMA_SE", i, ln.strip()[:120])
        if caminho in ln or nome in ln:
            return ("NOMEIA_SE", i, ln.strip()[:120])
    return ()

# O mapa e um CONSUMIDOR da arquitetura, nunca o dono dela.
#
# A regra NAO e sobre a palavra «arquitetura» aparecer no nome do conceito: o
# gerador possui legitimamente a PROJECAO da arquitetura, e proibir-lhe a palavra
# so o ensinaria a chamar-lhe outra coisa. Um portao que se contorna mudando um
# nome nao mede nada.
#
# A regra e sobre o VERBO. Uma peca do mapa pode MEDIR (OBSERVES) e pode REPROVAR
# (VALIDATES) — sao os dois trabalhos dela. O que ela nunca pode e GOVERNAR:
#
#     agente -> implementacao -> testes -> commit -> CI -> mapa regenerado
#
# no dia em que o mapa governasse uma peca, a seta passava a correr ao contrario,
# e o mapa virava a segunda verdade arquitetural que AGENTS.md proibe.
PASTAS_DO_MAPA = ("system-map/",)
VERBOS_DE_GOVERNO = ("GOVERNS", "CONSTRAINS")

falhas: list[tuple[str, str, list]] = []
oks: list[str] = []


def prova(nome: str, descricao: str, passou: bool, detalhe: list | None = None) -> None:
    if passou:
        oks.append(f"  PASS  {nome:<34} {descricao}")
    else:
        falhas.append((nome, descricao, detalhe or []))


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout.strip()


def main() -> int:
    fixar = "--fixar" in sys.argv

    if not CENSO.exists():
        print("PORTAO_DO_CONTROLE=FAIL · o censo nao existe.\n"
              "  Corra primeiro: python3 controle/censo_do_controle.py")
        return 1

    R = json.loads(REGISTO.read_text(encoding="utf-8"))
    C = json.loads(CENSO.read_text(encoding="utf-8"))
    cartoes = C["CARDS"]
    arestas = C["GOVERNANCE_EDGES"]
    por_id = {c["CARD_ID"]: c for c in cartoes}
    rastreados = set(git("ls-files").split("\n"))

    # ══ INTEGRIDADE — nunca pode existir ═══════════════════════════════════

    # ── 1 · dois cartoes com o mesmo id ──────────────────────────────────────
    ids = [a["CARD_ID"] for a in R["AUTHORITIES"]]
    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    prova("DUPLICATE_AUTHORITY_ID", "nenhum cartao com id repetido",
          not repetidos, repetidos)

    # ── 2 · UM CONCEITO, UM DONO ─────────────────────────────────────────────
    # A lei inteira desta missao numa linha. Dois documentos canonicos a
    # reivindicar o mesmo conceito e o estado em que nenhum dos dois vale.
    donos: dict[str, list] = {}
    for a in R["AUTHORITIES"]:
        co = a.get("CONCEPT_OWNER", "")
        if co and a["LIFECYCLE"] == "CANONICAL" and not a.get("IS_POINTER"):
            donos.setdefault(co, []).append(a["CARD_ID"])
    colisao = [f"{co}: {' e '.join(v)}" for co, v in sorted(donos.items()) if len(v) > 1]
    prova("DUPLICATE_CONCEPT_OWNER", "nenhum conceito com dois donos canonicos",
          not colisao, colisao)

    # ── 3 · UM SO KNOW-HOW ───────────────────────────────────────────────────
    kh = [a["CARD_ID"] for a in R["AUTHORITIES"]
          if a["KIND"] == "KNOW_HOW" and a["LIFECYCLE"] == "CANONICAL"]
    prova("KNOW_HOW_DUPLICATED", "existe exatamente um know-how canonico",
          len(kh) == 1, kh if len(kh) != 1 else [])

    # ── 4 · superseded nao volta a ser lei ───────────────────────────────────
    zumbis = [a["CARD_ID"] for a in R["AUTHORITIES"]
              if a["LIFECYCLE"] == "CANONICAL" and a.get("SUPERSEDED_BY")]
    prova("SUPERSEDED_MARKED_CANONICAL", "nada substituido continua carimbado de canonico",
          not zumbis, zumbis)

    # ── 5 · HANDOFF NAO E AUTORIDADE ─────────────────────────────────────────
    # Um handoff conta o que aconteceu. No dia em que ele governar alguem, a
    # memoria de uma sessao passa a mandar no repositorio inteiro.
    mandoes = [f"{a['CARD_ID']} governa {len(a.get('GOVERNS', []) + a.get('CONSTRAINS', []))}"
               for a in R["AUTHORITIES"]
               if a["KIND"] == "HANDOFF" and (a.get("GOVERNS") or a.get("CONSTRAINS"))]
    prova("HANDOFF_AS_AUTHORITY", "nenhum handoff governa nada", not mandoes, mandoes)

    # ── 6 · O MAPA NAO E DONO DA ARQUITETURA ─────────────────────────────────
    usurpa = [f"{a['CARD_ID']} governa {len(a.get(v, []))} ({v})"
              for a in R["AUTHORITIES"]
              if a["CANONICAL_PATH"].startswith(PASTAS_DO_MAPA)
              for v in VERBOS_DE_GOVERNO if a.get(v)]
    prova("SYSTEM_MAP_IS_AUTHORITY", "nenhuma peca do mapa governa — mede e reprova, so",
          not usurpa, usurpa)

    # ── 7 · DECLARADA NAO SE PINTA DE OBSERVADA ──────────────────────────────
    # A prova tem de ser do TIPO que aquele tipo de aresta exige. Uma GOVERNS
    # observada com prova `PATH_EXISTS` seria «o ficheiro existe, logo a lei
    # manda nele» — que e exatamente o que esta lei recusa.
    mentiras = [f"{e['FROM']}->{e['TO_PATH']} ({e['EDGE_TYPE']} observada com "
                f"prova {e['PROOF_KIND']})"
                for e in arestas
                if e["EDGE_STATE"] == "OBSERVED"
                and e["PROOF_KIND"] != R["EDGE_TYPES"][e["EDGE_TYPE"]]["observed_needs"]]
    prova("DECLARED_EDGE_RENDERED_AS_OBSERVED",
          "nenhuma aresta declarada aparece como observada", not mentiras, mentiras)

    # ── 8 · toda aresta observada aponta para uma linha que existe ───────────
    sem_linha = [f"{e['FROM']}->{e['TO_PATH']}" for e in arestas
                 if e["EDGE_STATE"] == "OBSERVED" and not e["PROOF_LOCATION"]]
    prova("OBSERVED_EDGE_HAS_LOCATION", "toda aresta observada diz ficheiro e linha",
          not sem_linha, sem_linha)

    # ── 9 · PONTEIRO QUEBRADO — E SO O QUE E MESMO UM CAMINHO ────────────────
    # So conta para autoridade que ESTA nesta arvore: cobrar o alvo de uma lei
    # que nem ca esta seria cobrar duas vezes o mesmo defeito.
    #
    # E so conta para aresta cujo ALVO E UM CAMINHO. Esta prova ja reprovou uma
    # supersessao — `A-BIBLIA-ENG-INTELIGENCIA SUPERSEDES A-BIBLIA-INTELIGENCIA`
    # — por «ponteiro quebrado», quando o alvo nunca foi um ponteiro: e o id de
    # uma autoridade. O censo mandava-o pelo laco dos caminhos, nao encontrava
    # ficheiro nenhum com aquele nome, e chamava defeito aquilo que era a forma
    # certa de dizer «substitui uma lei que ja nao vive aqui».
    #
    #     IDENTIDADE != MORADA. AUTHORITY_ID != CANONICAL_PATH.
    #
    # Tres coisas diferentes estavam com o mesmo nome, e por isso nenhuma delas
    # se conseguia consertar. Agora sao tres provas:
    #
    #     BROKEN_POINTER          um CAMINHO declarado que nao existe
    #     UNKNOWN_AUTHORITY_ID    um ID declarado que o registo nao conhece
    #     SUPERSESSION_RECIPROCAL uma metade de supersessao sem a outra metade
    quebrados = [f"{e['FROM']} -> {e['TO_PATH']}" for e in arestas
                 if e["PROOF_KIND"] == "ABSENT"
                 and e.get("TO_KIND", "PATH") == "PATH"
                 and por_id[e["FROM"]]["IN_TREE"]]
    prova("BROKEN_POINTER", "nenhuma autoridade presente aponta para caminho inexistente",
          not quebrados, quebrados)

    # ── 9b · UM ID QUE O REGISTO NAO CONHECE ─────────────────────────────────
    # Isto e um defeito real, e o unico que a confusao anterior escondia: uma
    # aresta de identidade a nomear um cartao que nao existe em lado nenhum.
    fantasmas = [f"{e['FROM']} -{e['EDGE_TYPE']}-> {e['TO_PATH']}" for e in arestas
                 if e["PROOF_KIND"] == "UNKNOWN_AUTHORITY_ID"]
    prova("UNKNOWN_AUTHORITY_ID", "nenhuma aresta de identidade nomeia cartao inexistente",
          not fantasmas, fantasmas)

    # ── 9c · AS DUAS METADES DE UMA SUPERSESSAO TEM DE COINCIDIR ─────────────
    # `A SUPERSEDES B` escrito so num lado e uma declaracao a provar-se a si
    # propria. B tem de dizer `SUPERSEDED_BY: A` — e o inverso tambem: um cartao
    # que se diz substituido por alguem que nao o reivindica fica sem historia.
    sup = {a["CARD_ID"]: set(a.get("SUPERSEDES", [])) for a in R["AUTHORITIES"]}
    por_quem = {a["CARD_ID"]: set(a.get("SUPERSEDED_BY", [])) for a in R["AUTHORITIES"]}
    mancas = [f"{x} diz SUPERSEDES {y}, e {y} nao diz SUPERSEDED_BY {x}"
              for x, alvos in sup.items() for y in alvos
              if y in por_quem and x not in por_quem[y]]
    mancas += [f"{y} diz SUPERSEDED_BY {x}, e {x} nao diz SUPERSEDES {y}"
               for y, quem in por_quem.items() for x in quem
               if x in sup and y not in sup[x]]
    prova("SUPERSESSION_RECIPROCAL", "toda supersessao esta escrita nas duas pontas",
          not mancas, mancas)

    # ── 9d · A LEI E O REGISTO TEM DE CONTAR A MESMA HISTORIA ────────────────
    #
    #     PROMOVER NO REGISTO E NAO PROMOVER NO TEXTO DA LEI — OU AO CONTRARIO —
    #     DEIXA DUAS VERDADES, E A PARTIR DAI NENHUMA DAS DUAS VALE.
    #
    # Uma Biblia carrega o estado no proprio cabecalho. Quem le a lei le o
    # cabecalho; quem consulta o Control Plane le o registo. Se os dois
    # discordarem, cada leitor sai com uma resposta diferente e ninguem sabe
    # qual manda. A prova nao inventa estado nenhum: so exige que os dois
    # coincidam quando o documento se pronuncia.
    #
    # So vale para lei que ESTA nesta arvore e que DIZ o seu estado. Uma que nao
    # declare nada nao e acusada — o silencio nao e uma contradicao.
    ESTADO_NO_CABECALHO = re.compile(r"^STATUS\s*[:=]?\s+([A-Z_]+)\s*$", re.M)
    discordias = []
    for a in R["AUTHORITIES"]:
        if a["KIND"] != "BIBLE" or a["CANONICAL_PATH"] not in rastreados:
            continue
        try:
            cabeca = (RAIZ / a["CANONICAL_PATH"]).read_text(
                encoding="utf-8", errors="replace")[:2000]
        except OSError:
            continue
        m = ESTADO_NO_CABECALHO.search(cabeca)
        if not m:
            continue
        dito, registado = m.group(1), a["LIFECYCLE"]
        # `CANDIDATE_FOR_CANONICAL_REVIEW` e `CANDIDATE` sao a mesma coisa dita
        # com mais palavras. Igualar pelo prefixo, e nunca por uma tabela de
        # sinonimos que alguem aumenta para calar o portao.
        if not (dito == registado or dito.startswith(registado + "_")):
            discordias.append(f"{a['CARD_ID']}: o texto diz {dito}, o registo diz {registado}")
    prova("BIBLE_STATUS_MATCHES_REGISTRY",
          "nenhuma lei carimba no texto um estado diferente do registado",
          not discordias, discordias)

    # ── 10 · o censo esta atual ──────────────────────────────────────────────
    drift = [a["CARD_ID"] for a in R["AUTHORITIES"] if a["CARD_ID"] not in por_id]
    drift += [c["CARD_ID"] for c in cartoes if c["CARD_ID"] not in set(ids)]
    prova("CONTROL_PLANE_REGISTRY_DRIFT", "o censo corresponde ao registo de hoje",
          not drift, sorted(set(drift)))

    # ── 11 · UM SO PONTO DE ENTRADA DO CONTROL PLANE ─────────────────────────
    entradas = [a["CARD_ID"] for a in R["AUTHORITIES"]
                if a["KIND"] == "REGISTRY" and a["CANONICAL_PATH"].endswith(".md")]
    prova("CANONICAL_CONTROL_ENTRYPOINTS", "existe exatamente uma sala de controle",
          len(entradas) == 1, entradas if len(entradas) != 1 else [])

    # ── 12 · A PORTA COMMITADA E A QUE O CENSO DE HOJE PRODUZ ────────────────
    # `SALA-DE-CONTROLE-SINTONIA.md` e gerada, e o validador do mapa nao a
    # confere — ele confere o indice de fontes e a porta da coleta, que ja
    # existiam quando foi escrito. Sem esta prova, alguem podia mudar o registo,
    # regerar tudo menos ela, e commitar uma porta que descreve um Control Plane
    # que ja nao existe.
    #
    #     UMA PORTA DE ENTRADA DESATUALIZADA E PIOR QUE NENHUMA:
    #     QUEM A LE ACREDITA NELA.
    sala = RAIZ / "SALA-DE-CONTROLE-SINTONIA.md"
    with tempfile.TemporaryDirectory() as td:
        nova = Path(td) / "sala.md"
        r = subprocess.run(
            [sys.executable, str(RAIZ / "controle" / "censo_do_controle.py")],
            capture_output=True, text=True,
            env={**os.environ, "SINTONIA_CONTROLE_SALA": str(nova),
                 "SINTONIA_CONTROLE_CENSO": str(Path(td) / "censo.json")})
        igual = (r.returncode == 0 and nova.exists() and sala.exists()
                 and nova.read_text(encoding="utf-8") == sala.read_text(encoding="utf-8"))
    prova("SALA_DE_CONTROLE_ATUAL",
          "a sala de controle commitada e a que o censo de hoje produz", igual,
          ["regenere: python3 controle/censo_do_controle.py"] if not igual else [])

    # ══ DIVIDA — medida, contada, e com teto que nao sobe ══════════════════

    # A EXPLICACAO ANDA AO LADO DO MEMBRO, E NUNCA DENTRO DELE.
    #
    # Os membros ja foram cadeias como «A-DIARIO (6)» e «A-KNOWHOW (canonica em
    # origin/..., fora deste HEAD)». Isso torna a IDENTIDADE do defeito refem de
    # um numero e de um nome de ramo: o dia em que `A-DIARIO` passasse a ter 7
    # copias, o membro antigo desaparecia e nascia um «novo» — e uma comparacao
    # de conjuntos via divida nova onde so havia a mesma divida a mudar de
    # tamanho. Pior: o inverso tambem, e ai a divida nova passava despercebida.
    #
    #     O MEMBRO E QUEM. O PORQUE E OUTRA COLUNA.
    #
    # E A CHAVE E O PAR, NUNCA SO O MEMBRO. `A-KNOWHOW` esta em duas categorias
    # ao mesmo tempo — tem copias divergentes E e canonica fora deste HEAD — e
    # com o membro sozinho por chave a segunda explicacao apagava a primeira. A
    # saida imprimia, debaixo de DIVERGENT_CANONICAL_COPY, a razao do STALE.
    #
    #     UM CONCEITO, UM DONO: a razao pertence ao PAR (categoria, membro).
    porques: dict = {}

    ausentes = sorted(c["CARD_ID"] for c in cartoes
                      if c["LIFECYCLE"] == "CANONICAL"
                      and c["OBSERVED_STATE"] in ("ABSENT_FROM_SNAPSHOT", "ABSENT"))
    # Uma autoridade canonica que nao existe em lado nenhum e outra coisa, e
    # muito pior: nem branch lateral a guarda.
    perdidas = sorted(c["CARD_ID"] for c in cartoes
                      if c["LIFECYCLE"] == "CANONICAL" and c["OBSERVED_STATE"] == "ABSENT")
    divergentes = sorted(c["CARD_ID"] for c in cartoes if c["DIVERGENT_COPIES"])
    for c in cartoes:
        if c["DIVERGENT_COPIES"]:
            porques[("DIVERGENT_CANONICAL_COPY", c["CARD_ID"])] = \
                f"{len(c['DIVERGENT_COPIES'])} copia(s) divergente(s)"
    orfas = sorted(c["CARD_ID"] for c in cartoes
                   if c["OBSERVED_STATE"] == "ORPHAN_IN_TREE")

    # STALE — por regra objetiva, nunca por idade. Uma autoridade e velha nesta
    # foto quando a versao canonica dela vive numa ref que NAO e antepassada do
    # HEAD: o que esta arvore carrega nao e o que o registo diz ser canonico.
    stale = []
    for c in cartoes:
        ref = c.get("CANONICAL_REF", "IN_TREE")
        if ref in ("", "IN_TREE"):
            continue
        alvo = git("rev-parse", "--verify", f"{ref}^{{commit}}")
        if not alvo:
            continue
        antepassado = subprocess.run(
            ["git", "-C", str(RAIZ), "merge-base", "--is-ancestor", alvo, "HEAD"],
            capture_output=True).returncode == 0
        if not antepassado:
            stale.append(c["CARD_ID"])
            porques[("STALE_AUTHORITY", c["CARD_ID"])] = \
                f"canonica em {ref}, fora deste HEAD"

    # Documento que se diz lei e nao esta no registo.
    registados = {a["CANONICAL_PATH"] for a in R["AUTHORITIES"]}
    nao_registados = []
    for p in sorted(rastreados):
        if not p.endswith(".md") or p in registados:
            continue
        if p.startswith(("build/", "research/", "data/", "italia-portale/BASELINE/")):
            continue
        try:
            linhas = (RAIZ / p).read_text(encoding="utf-8", errors="replace").split("\n")
        except OSError:
            continue
        onde = declara_se_lei(p, linhas)
        if onde:
            nao_registados.append(p)
            porques[("UNREGISTERED_CANONICAL_DOCUMENT", p)] = \
                f"{onde[0]} L{onde[1]}: {onde[2]}"

    medido = {
        "CANONICAL_AUTHORITY_MISSING": len(ausentes),
        "CANONICAL_AUTHORITY_LOST": len(perdidas),
        "DIVERGENT_CANONICAL_COPY": len(divergentes),
        "STALE_AUTHORITY": len(stale),
        "UNREGISTERED_CANONICAL_DOCUMENT": len(nao_registados),
        "ORPHAN_AUTHORITY": len(orfas),
    }
    detalhes = {
        "CANONICAL_AUTHORITY_MISSING": ausentes,
        "CANONICAL_AUTHORITY_LOST": perdidas,
        "DIVERGENT_CANONICAL_COPY": divergentes,
        "STALE_AUTHORITY": stale,
        "UNREGISTERED_CANONICAL_DOCUMENT": nao_registados,
        "ORPHAN_AUTHORITY": orfas,
    }

    # ── O CHAO, E A LINHAGEM DELE ────────────────────────────────────────────
    #
    # UMA FOTOGRAFIA DE DIVIDA TIRADA NOUTRA LINHA NAO MEDE ESTA ARVORE.
    #
    # O chao desta casa foi fixado em `a885769c54`, que vive so em
    # `origin/claude/funny-hypatia-y7ho5s` e NAO e antepassado deste HEAD. Durante
    # uma missao inteira o portao comparou os defeitos de hoje com o tecto de um
    # snapshot que nunca esteve aqui — e o tecto `UNREGISTERED_CANONICAL_DOCUMENT
    # = 0` era verdade la, onde aqueles dez documentos da Collection nem existiam.
    #
    #     UM NUMERO CERTO LIDO CONTRA A FOTOGRAFIA ERRADA.
    #
    # Um chao so vale se a arvore onde ele foi medido estiver ATRAS desta. Quando
    # nao estiver, ele tem de dizer de onde veio e porque continua a valer — e
    # isso e uma frase escrita por gente, nao um campo que o `--fixar` preenche
    # sozinho.
    antepassado_do_chao = None
    if CHAO.exists():
        C_ = json.loads(CHAO.read_text(encoding="utf-8"))
        chao_head = (C_.get("MEDIDO_EM") or {}).get("HEAD") or C_.get("HEAD", "")
        migrado = (C_.get("MEDIDO_EM") or {}).get("MIGRADO_DE")
        if chao_head:
            antepassado_do_chao = subprocess.run(
                ["git", "-C", str(RAIZ), "merge-base", "--is-ancestor", chao_head, "HEAD"],
                capture_output=True).returncode == 0
        prova("CHAO_DA_LINHAGEM",
              f"o chao foi medido numa arvore atras desta ({chao_head})",
              bool(antepassado_do_chao) or bool(migrado),
              [f"{chao_head} nao e antepassado de HEAD, e o chao nao declara "
               "MEDIDO_EM.MIGRADO_DE com a razao de continuar a valer"]
              if not antepassado_do_chao else [])

    # ── MEMBROS, E NAO SO CONTAGENS ──────────────────────────────────────────
    #
    #     TRES DEFEITOS ANTIGOS DESAPARECEM, TRES NOVOS APARECEM,
    #     A CONTAGEM NAO MEXE, E NADA REPROVA.
    #
    # Era o buraco desta divida: o tecto e um numero, e um numero nao ve
    # substituicao. Quem entra tem de ser alguem que ja la estava.
    chao_membros = {}
    if CHAO.exists():
        C_ = json.loads(CHAO.read_text(encoding="utf-8"))
        chao_membros = C_.get("MEMBROS") or C_.get("QUEM") or {}
    novos = []
    for k, quem in detalhes.items():
        antes = set(chao_membros.get(k, []))
        for m in quem:
            if m not in antes:
                razao = porques.get((k, m), "")
                novos.append(f"{k}: {m}" + (f"  ({razao})" if razao else ""))

    # ── MIGRAR O CHAO PARA ESTA LINHAGEM, COM PROVA ──────────────────────────
    #
    #     UMA FOTOGRAFIA DE DIVIDA PODE MUDAR DE LINHA. NAO PODE MUDAR SOZINHA.
    #
    # `--fixar` grava o estado de hoje. Nao serve aqui: o chao de `a885769c54`
    # nao mede esta arvore, e re-fixar por cima apagava a comparacao — ficava um
    # tecto novo sem ninguem provar que ele nao e pior do que o antigo.
    #
    # `--migrar` faz a unica coisa que legitima trocar de fotografia: compara,
    # CATEGORIA A CATEGORIA E MEMBRO A MEMBRO, e so entao grava. Ele recusa
    # quando qualquer contagem subiu ou quando entrou um membro que nao estava
    # la — que e exatamente o caso que a contagem sozinha nao ve.
    #
    # A unica normalizacao que ele faz e documentada e estreita: os membros do
    # chao antigo traziam a razao colada ao nome — `A-DIARIO (6)` — e a razao
    # passou a viver noutra coluna. `A-DIARIO (6)` e `A-DIARIO` sao o MESMO
    # defeito com a mesma identidade, e o parentesis cai. Nada mais e tocado: um
    # membro que nao tenha correspondente antigo depois disto e divida nova, e
    # divida nova nao migra.
    if "--migrar" in sys.argv:
        if not CHAO.exists():
            print("CHAO_MIGRADO=RECUSADO · nao ha chao para migrar")
            return 1
        C_ = json.loads(CHAO.read_text(encoding="utf-8"))
        antigo_teto = C_.get("TETO", {})
        antigo_membros = C_.get("MEMBROS") or C_.get("QUEM") or {}
        antigo_head = (C_.get("MEDIDO_EM") or {}).get("HEAD") or C_.get("HEAD", "")

        def sem_parentesis(m: str) -> str:
            return m.split("  (")[0].split(" (")[0].strip()

        equivalencia, recusas = {}, []
        for k in medido:
            antes = {sem_parentesis(m) for m in antigo_membros.get(k, [])}
            equivalencia[k] = {
                "TETO_ANTIGO": antigo_teto.get(k, 0), "HOJE": medido[k],
                "MEMBROS_ANTES": sorted(antes),
                "MEMBROS_HOJE": sorted(detalhes[k]),
                "PAGOS": sorted(antes - set(detalhes[k])),
                "NOVOS": sorted(set(detalhes[k]) - antes),
            }
            if medido[k] > antigo_teto.get(k, 0):
                recusas.append(f"{k}: hoje {medido[k]}, teto antigo {antigo_teto.get(k, 0)}")
            for m in equivalencia[k]["NOVOS"]:
                recusas.append(f"{k}: membro novo `{m}` nao existia no chao antigo")
        # Toda a integridade tem de estar verde — MENOS `CHAO_DA_LINHAGEM`, que e
        # exatamente o defeito que esta migracao existe para pagar. Exigi-lo aqui
        # fazia o conserto depender de ja estar consertado, e o chao ficava preso
        # noutra linhagem para sempre.
        recusas += [f"integridade reprovada: {n}" for n, _, _ in falhas
                    if n != "CHAO_DA_LINHAGEM"]

        if recusas:
            print("CHAO_MIGRADO=RECUSADO · a divida de hoje nao e igual nem melhor")
            for x in recusas[:12]:
                print(f"    · {x}")
            return 1

        CHAO.write_text(json.dumps({
            "NOTA": ["O TETO DA DIVIDA DO CONTROL PLANE. Nao e meta: e teto.",
                     "Um numero que sobe reprova, e um MEMBRO novo reprova mesmo",
                     "que o numero nao suba.",
                     "",
                     "MEDIDO_EM diz em que arvore isto foi medido. Um chao cuja",
                     "arvore nao esta atras desta nao mede esta."],
            "MEDIDO_EM": {
                "HEAD": git("rev-parse", "HEAD"),
                "BRANCH": git("rev-parse", "--abbrev-ref", "HEAD"),
                "MIGRADO_DE": {
                    "HEAD": antigo_head,
                    "PORQUE": [
                        f"`{antigo_head}` nao e antepassado deste HEAD: foi medido"
                        " noutra linha, e um tecto de outra fotografia nao mede esta.",
                        "A migracao so passou porque nenhuma categoria subiu e",
                        "nenhum membro novo entrou — provado membro a membro abaixo.",
                        "A unica normalizacao aplicada: a razao deixou de viver",
                        "colada ao nome do membro (`A-DIARIO (6)` -> `A-DIARIO`).",
                    ],
                    "PROVA": equivalencia,
                },
            },
            "TETO": medido,
            "MEMBROS": detalhes,
            "PORQUE": {f"{k}/{m}": porques[(k, m)] for k in detalhes
                       for m in detalhes[k] if (k, m) in porques},
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"CHAO_MIGRADO=OK · de {antigo_head} para {git('rev-parse', 'HEAD')[:10]}")
        for k, v in medido.items():
            print(f"    {k:<34} {v:>3}  (teto antigo {antigo_teto.get(k, 0)}"
                  f" · pagos {len(equivalencia[k]['PAGOS'])})")
        return 0

    migrado_antes = None
    if CHAO.exists():
        migrado_antes = (json.loads(CHAO.read_text(encoding="utf-8"))
                         .get("MEDIDO_EM") or {}).get("MIGRADO_DE")

    if fixar or not CHAO.exists():
        # `--fixar` NAO E UM BOTAO DE PASSAR. Ele grava o estado de hoje como
        # tecto, e por isso so pode correr quando hoje ja e melhor ou igual: se
        # ele aceitasse um numero pior, «teto que nunca sobe» virava uma frase.
        #
        #     FIXAR UM DEFEITO COMO NOVO NORMAL != CORRIGIR O DEFEITO.
        if CHAO.exists():
            teto_ = json.loads(CHAO.read_text(encoding="utf-8")).get("TETO", {})
            piores = [f"{k}: hoje {v}, teto {teto_.get(k, 0)}"
                      for k, v in medido.items() if v > teto_.get(k, 0)]
            if piores or novos or falhas:
                print("CHAO_FIXADO=RECUSADO · o chao nao desce sobre divida por pagar")
                for x in piores:
                    print(f"    PIOROU          {x}")
                for x in novos[:8]:
                    print(f"    MEMBRO NOVO     {x}")
                for nome, _, _ in falhas:
                    print(f"    INTEGRIDADE     {nome}")
                return 1
        CHAO.write_text(json.dumps({
            "NOTA": ["O TETO DA DIVIDA DO CONTROL PLANE. Nao e meta: e teto.",
                     "Um numero que sobe reprova, e um MEMBRO novo reprova mesmo",
                     "que o numero nao suba. Quando alguem pagar a divida,",
                     "`--fixar` desce o teto — e ele nunca mais sobe.",
                     "",
                     "MEDIDO_EM diz em que arvore isto foi medido. Um chao cuja",
                     "arvore nao esta atras desta nao mede esta: ou e re-fixado",
                     "aqui, ou declara MIGRADO_DE com a razao de continuar a valer."],
            # A HISTORIA DA MIGRACAO NAO SE PERDE POR O CHAO DESCER DEPOIS.
            # Baixar o tecto e outro acto; apagar de onde este chao veio era
            # apagar a unica prova de que a troca de linhagem foi legitima.
            "MEDIDO_EM": {"HEAD": git("rev-parse", "HEAD"),
                          "BRANCH": git("rev-parse", "--abbrev-ref", "HEAD"),
                          **({"MIGRADO_DE": migrado_antes} if migrado_antes else {})},
            "TETO": medido,
            "MEMBROS": detalhes,
            "PORQUE": {f"{k}/{m}": porques[(k, m)] for k in detalhes
                       for m in detalhes[k] if (k, m) in porques},
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("CHAO_FIXADO=OK · controle/CHAO-DO-CONTROLE.json")
        for k, v in medido.items():
            print(f"    {k:<34} {v}")
        return 0

    teto = json.loads(CHAO.read_text(encoding="utf-8"))["TETO"]
    for k, v in medido.items():
        limite = teto.get(k, 0)
        prova(k, f"nao piorou desde o chao (teto {limite}, hoje {v})",
              v <= limite, detalhes[k] if v > limite else [])
    prova("MEMBRO_NOVO_NAO_EXPLICADO",
          "nenhum defeito novo entrou por baixo de uma contagem que nao mexeu",
          not novos, novos)

    # ── impressao ────────────────────────────────────────────────────────────
    print("=" * 70)
    print("PORTAO DO CONTROL PLANE")
    print("=" * 70)
    for linha in oks:
        print(linha)
    for nome, desc, det in falhas:
        print(f"  FAIL  {nome:<34} {desc}")
        for d in det[:8]:
            print(f"        {d}")

    print()
    print("A DIVIDA DE HOJE, com nome e numero:")
    for k, v in medido.items():
        print(f"    {k:<34} {v:>3}   (teto {teto.get(k, 0)})")
        for d in detalhes[k][:4]:
            razao = porques.get((k, d), "")
            print(f"        · {d}" + (f"   — {razao}" if razao else ""))

    print()
    print("=" * 70)
    if falhas:
        print(f"PORTAO_DO_CONTROLE=FAIL · {len(falhas)} prova(s) reprovada(s)")
        print("=" * 70)
        print("Um conceito, um dono. Um dono, muitos ponteiros.")
        print("Leia SALA-DE-CONTROLE-SINTONIA.md antes de mexer.")
        return 1
    print(f"PORTAO_DO_CONTROLE=PASS · {len(oks)} prova(s)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
