#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CENSO DO CONTROL PLANE — mede o que o registo declara, e nunca acredita nele.

    O REGISTO DIZ QUEM MANDA. ESTE FICHEIRO DIZ SE ISSO E VERDADE HOJE.

`controle/AUTORIDADES-CANONICAS.json` e escrito por gente: ele carrega o que a
maquina nao consegue saber — que um documento e uma LEI e nao uma lembranca, que
conceito ele possui, quem ele diz governar. Nada nele e prova de nada.

Este censo mede, ficheiro a ficheiro, aresta a aresta:

    o caminho existe nesta arvore?          -> git ls-files
    que SHA tem, e quando mudou?            -> git log
    quem aponta para ele?                   -> varredura do texto de toda a arvore
    a aresta declarada tem prova?           -> o caminho do alvo aparece no texto
                                               da autoridade, com linha?

E escreve `system-map/data/controle.generated.json`, que o gerador do mapa le.

────────────────────────────────────────────────────────────────────────────
A REGRA QUE ESTE FICHEIRO EXISTE PARA CUMPRIR

    DECLARED != OBSERVED

Uma aresta GOVERNS desenhada no registo nasce DECLARED. Ela so passa a OBSERVED
quando o texto da propria autoridade nomeia o caminho do alvo — e a prova
guardada e `ficheiro:linha`, apontavel, nao um booleano.

E o inverso, que e o erro caro:

    O FICHEIRO EXISTIR NAO PROVA QUE ELE AINDA MANDA.

Por isso `PATH_EXISTS` nunca sozinho promove nada. Uma autoridade cujo caminho
existe mas para a qual ninguem aponta fica `ORPHAN_IN_TREE` — esta la, e nao
governa ninguem que se consiga medir.

────────────────────────────────────────────────────────────────────────────
E A AUTORIDADE QUE NAO ESTA NESTA ARVORE?

Fica `ABSENT_FROM_SNAPSHOT`, e todas as arestas dela ficam DECLARED. Nao e um
erro do censo: e o defeito que esta missao existe para tornar visivel. A lei da
coleta e o know-how deste projeto vivem em branches laterais, e um agente que
clone `main` e mandado consultar ficheiros que ali nao estao.

Quando o registo declara `CANONICAL_REF` (uma branch), o censo vai la medir —
com `git rev-parse <ref>:<caminho>` — e diz onde a autoridade REALMENTE vive.
Medir noutra ref nao a traz para ca. So diz onde ela esta.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# OS CAMINHOS SAO SUBSTITUIVEIS, e existe uma razao so para isso: o red team.
# Atacar um portao editando o ficheiro real do repositorio e deixar o ataque
# gravado se o teste morrer a meio — e um teste que estraga o que testa nao se
# corre duas vezes. Com estas variaveis, os doze ataques correm o CODIGO REAL
# sobre ficheiros temporarios, e o repositorio nao e tocado.
def _caminho(env: str, omissao: Path) -> Path:
    v = os.environ.get(env)
    return Path(v) if v else omissao


REGISTO = _caminho("SINTONIA_CONTROLE_REGISTO",
                   RAIZ / "controle" / "AUTORIDADES-CANONICAS.json")
SAIDA = _caminho("SINTONIA_CONTROLE_CENSO",
                 RAIZ / "system-map" / "data" / "controle.generated.json")
SALA = _caminho("SINTONIA_CONTROLE_SALA", RAIZ / "SALA-DE-CONTROLE-SINTONIA.md")
MAPA_DECLARADO = RAIZ / "system-map" / "data" / "architecture.declared.json"

# Onde faz sentido procurar um ponteiro para uma autoridade. Nao e a arvore
# inteira: `data/` tem amostras com caminhos la dentro que nao sao referencias
# a nada, e `build/` guarda copias antigas de handoffs. Contar essas como
# «alguem aponta para esta lei» daria vida artificial a documentos mortos.
ONDE_SE_APONTA = re.compile(
    r"^(AGENTS\.md|CLAUDE\.md|README\.md|SALA-DE-CONTROLE-SINTONIA\.md"
    r"|[A-Z0-9-]+\.md"
    r"|\.github/|docs/|controle/|system-map/|tests/|provas/|medidas/|regras/"
    r"|admissao/|candidatas/|coleta/|ferramentas/|fontes/|guarda/|leis/|motor/"
    r"|pacote/|pedido/|portoes/|superficie/)"
)

# Saidas da propria cadeia. Um ponteiro que vive num ficheiro gerado nao e um
# ponteiro humano: e o eco do que este censo acabou de escrever, e conta-lo
# faria a prova apoiar-se em si mesma.
NAO_CONTA_COMO_PONTEIRO = re.compile(
    r"^system-map/data/[\w-]+\.generated\.json$"
    r"|^italia-portale/client/system-map/"
    r"|^regras/LEIA-ANTES-DE-COLETAR\.md$"
    r"|^docs/fontes/INDICE-DE-FONTES\.md$"
    r"|^SALA-DE-CONTROLE-SINTONIA\.md$"
)

TEXTO = {".md", ".py", ".mjs", ".js", ".json", ".yml", ".yaml", ".html", ".sh", ".css"}


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *args],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.rstrip("\n")


def rastreados() -> list:
    return [p for p in git("ls-files").split("\n") if p]


def carregar_textos(paths: list) -> dict:
    """O texto de cada ficheiro onde faz sentido procurar um ponteiro.

    Le-se uma vez e guarda-se em memoria: procurar 34 autoridades vezes 1.100
    ficheiros abrindo o disco em cada par daria 37 mil aberturas para responder
    a uma pergunta que uma passagem responde.
    """
    textos = {}
    for p in paths:
        if not ONDE_SE_APONTA.match(p) or NAO_CONTA_COMO_PONTEIRO.match(p):
            continue
        if Path(p).suffix not in TEXTO:
            continue
        f = RAIZ / p
        try:
            if f.stat().st_size > 4_000_000:
                continue
            textos[p] = f.read_text(encoding="utf-8", errors="replace").split("\n")
        except OSError:
            continue
    return textos


def procurar_dentro(textos: dict, dentro: str, alvo: str) -> str:
    """A linha da AUTORIDADE `dentro` que nomeia `alvo`. '' quando nenhuma.

    A BUSCA E SEMPRE DENTRO DE UM FICHEIRO SO, E ESSE FICHEIRO E SEMPRE A
    AUTORIDADE. Ja escrevi isto errado uma vez, nesta mesma missao: quando a
    autoridade nao estava na arvore eu deixava a busca cair para o mundo
    inteiro, e entao `BIBLIA-CANONICA-DA-COLETA.md` — que nao existe em `main` —
    aparecia a GOVERNAR `admissao/admissao.py` com prova OBSERVED apontando para
    dentro de `architecture.declared.json`.

        UMA LEI AUSENTE A GOVERNAR UMA PECA, COM PROVA TIRADA DE OUTRO FICHEIRO.

    E o ataque RT01 inteiro, cometido pelo proprio medidor. Quem prova uma
    relacao de governo e o texto de quem governa — nao o mundo a mencionar o
    governado.
    """
    linhas = textos.get(dentro)
    if not linhas:
        return ""
    for i, linha in enumerate(linhas, 1):
        if alvo in linha:
            return f"{dentro}:{i}"
    return ""


def medir_no_git(caminho: str, ref: str) -> dict:
    """O que o git sabe sobre este caminho, nesta ref.

    O SHA DA ARVORE DE TRABALHO, E NAO O DE `HEAD:<caminho>`.

    `git rev-parse HEAD:<caminho>` devolve o SHA da versao JA COMMITADA. Para um
    ficheiro que esta a ser alterado agora, isso e o conteudo antigo — e o valor
    muda sozinho no instante do commit, sem ninguem tocar em nada.

        O COMMIT NAO PODE CONHECER O SEU PROPRIO SHA.

    Esta casa ja pagou por isso uma vez. Um carimbo que muda ao commitar faz o
    mapa nascer um commit atras de si mesmo, e a verificacao anti-drift reprova
    o proprio commit que acabou de a satisfazer. `git hash-object` mede o
    CONTEUDO que esta aqui, e por isso da o mesmo valor antes e depois — que e a
    unica propriedade que serve para uma prova que atravessa um commit.
    """
    if ref in ("", "IN_TREE"):
        existe = caminho in RASTREADOS and (RAIZ / caminho).exists()
        sha = git("hash-object", caminho) if existe else ""
        log = git("log", "-1", "--format=%H|%cI|%s", "--", caminho) if existe else ""
    else:
        sha = git("rev-parse", f"{ref}:{caminho}")
        existe = bool(sha)
        log = git("log", "-1", "--format=%H|%cI|%s", ref, "--", caminho) if existe else ""
    commit, data, assunto = (log.split("|", 2) + ["", "", ""])[:3] if log else ("", "", "")
    return {"sha": sha[:10], "existe": existe, "last_commit": commit[:10],
            "last_change": data, "last_subject": assunto}


def dono_do_ficheiro() -> dict:
    """Que peca do System Map reivindica cada ficheiro.

    Le-se do ficheiro DECLARADO, e nao do gerado, de proposito: o gerado e a
    saida da cadeia, e o censo do controlo corre ANTES do gerador. Depender da
    saida faria a primeira corrida num clone limpo medir um mapa que ainda nao
    existe.
    """
    try:
        D = json.loads(MAPA_DECLARADO.read_text(encoding="utf-8"))
    except OSError:
        return {}
    dono = {}
    for c in D.get("COMPONENTS", []):
        for f in c.get("files", []):
            if "*" in f:                       # padrao, nao caminho
                continue
            dono[f] = c["id"]
    return dono


def resolver_peca(alvo: str, dono: dict) -> str:
    """Que peca do mapa este caminho toca. '' quando nenhuma o reivindica."""
    if alvo in dono:
        return dono[alvo]
    # Um caminho dentro de uma pasta que uma peca reivindica por padrao.
    for f, cid in dono.items():
        if f.endswith("/") and alvo.startswith(f):
            return cid
    return ""


# O QUE CADA TIPO DE ARESTA EXIGE PARA SER OBSERVADA, E O QUE O ALVO DELA E,
# LIDOS DO REGISTO — nunca copiados para aqui.
#
# Isto ja esteve escrito duas vezes: um dicionario `PROMOVE` aqui e o campo
# `observed_needs` la. Duas copias da mesma lei divergem, e no dia em que
# divergissem o censo media uma coisa e o portao cobrava outra.
def exigencias(reg: dict) -> tuple:
    tipos = reg["EDGE_TYPES"]
    return ({t: d["observed_needs"] for t, d in tipos.items()},
            {t for t, d in tipos.items() if d.get("target") == "AUTHORITY_ID"})


MARCA = {"PRESENT_AND_POINTED": "🟢", "PRESENT_ENTRY_POINT": "🟢",
         "ORPHAN_IN_TREE": "🟡", "ABSENT_FROM_SNAPSHOT": "🔴", "ABSENT": "⚪"}
DIZ = {"PRESENT_AND_POINTED": "está aqui, e alguém aponta para ela",
       "PRESENT_ENTRY_POINT": "está aqui — é porta, entra-se nela de fora",
       "ORPHAN_IN_TREE": "está aqui, e ninguém aponta para ela",
       "ABSENT_FROM_SNAPSHOT": "NÃO ESTÁ NESTA ÁRVORE — vive noutra linha",
       "ABSENT": "não existe em lado nenhum"}


def sala_de_controle(cartoes: list, arestas: list, resumo: dict,
                     sala_canonica: str) -> None:
    """Escreve `SALA-DE-CONTROLE-SINTONIA.md` — a porta humana do Control Plane.

    GERADA, e nao escrita a mao, pela mesma razao que `LEIA-ANTES-DE-COLETAR.md`
    e gerada: uma porta de entrada desatualizada e pior do que nenhuma, porque
    quem a le acredita nela. Autoridade nova aparece aqui sozinha; autoridade que
    sai do registo desaparece daqui, e nao fica paragrafo orfao a mandar em
    ninguem.

    ELA NAO REPETE LEI NENHUMA. Responde a onde a lei vive e se ela ainda manda.
    """
    por_id = {c["CARD_ID"]: c for c in cartoes}
    de = {}
    for e in arestas:
        de.setdefault(e["FROM"], []).append(e)

    L: list[str] = []
    w = L.append

    w("# SALA DE CONTROLE — SINTONIA EAME")
    w("")
    w("> **Este ficheiro é gerado.** Não o edite à mão: edite")
    w("> [`controle/AUTORIDADES-CANONICAS.json`](controle/AUTORIDADES-CANONICAS.json)")
    w("> e corra `py controle/censo_do_controle.py`.")
    w("")
    w("Esta é a porta do **CONTROL PLANE**: quem governa cada parte da máquina,")
    w("onde essa autoridade vive, e se ela ainda manda hoje.")
    w("")
    w("**Ela não repete lei nenhuma.** A lei do mapa vive em [`AGENTS.md`](AGENTS.md);")
    w("as instruções permanentes em [`CLAUDE.md`](CLAUDE.md); o método em")
    w("[`README.md`](README.md). Uma lei escrita em dois sítios diverge, e a partir")
    w("daí nenhuma das duas vale.")
    w("")
    w("---")
    w("")
    w("## OS TRÊS PLANOS")
    w("")
    w("```")
    w("CONTROL PLANE      quem manda        governa, referencia, valida, observa")
    w("      ↓ governa (nunca dado)")
    w("OPERATIONAL PLANE  a máquina         COLETA → ESPERA → INTELIGÊNCIA → ENTREGA")
    w("      ↑ prova")
    w("EVIDENCE PLANE     o que comprova    git · código · banco · runtime · testes")
    w("```")
    w("")
    w("O Control Plane **não é uma quarta etapa do dado**. Não existe")
    w("`DADO → CONTROL PLANE`: nenhum dado atravessa este plano. Ele governa a")
    w("máquina; a máquina é que corre.")
    w("")
    w("O System Map atravessa os três. **Não é pai de nenhum** — é derivado deles.")
    w("")
    w("---")
    w("")
    w("## QUEM COMANDA CADA PARTE")
    w("")
    w("| parte da máquina | autoridade | onde vive hoje | manda? |")
    w("|---|---|---|---|")
    for dominio, rotulo in (("COLETA", "COLETA"), ("INTELIGENCIA", "INTELIGÊNCIA"),
                            ("ENTREGA", "ENTREGA / CASCO")):
        donos = [c for c in cartoes if c["DOMAIN"] == dominio and c["KIND"] == "BIBLE"]
        if not donos:
            w(f"| **{rotulo}** | — | — | ⚪ NÃO SEI |")
            continue
        for c in donos:
            onde = "nesta árvore" if c["IN_TREE"] else f"`{c['LIVES_AT']}`"
            w(f"| **{rotulo}** | {c['NAME']} | {onde} | "
              f"{MARCA[c['OBSERVED_STATE']]} {c['LIFECYCLE']} |")
    w("")
    w("A leitura desta tabela é o resultado principal desta missão:")
    w("**nenhuma das três bíblias está nesta árvore.**")
    w("")
    w("---")
    w("")
    w("## O CATÁLOGO")
    w("")
    ordem = ["INSTRUCTION", "BIBLE", "CONTRACT", "DECISION", "KNOW_HOW",
             "REGISTRY", "VALIDATOR", "POLICY", "OBSERVER", "HANDOFF"]
    titulo = {"INSTRUCTION": "INSTRUÇÕES", "BIBLE": "BÍBLIAS", "CONTRACT": "CONTRATOS",
              "DECISION": "DECISÕES", "KNOW_HOW": "KNOW-HOW", "REGISTRY": "REGISTO",
              "VALIDATOR": "PORTÕES DE GOVERNANÇA", "POLICY": "POLÍTICA",
              "OBSERVER": "OBSERVADORES",
              "HANDOFF": "HANDOFFS — memória, **não** autoridade"}
    for kind in ordem:
        meus = [c for c in cartoes if c["KIND"] == kind]
        if not meus:
            continue
        w(f"### {titulo[kind]}")
        w("")
        for c in meus:
            w(f"#### {MARCA[c['OBSERVED_STATE']]} {c['NAME']}")
            w("")
            w(f"- **conceito que possui** — "
              f"{('`' + c['CONCEPT_OWNER'] + '`') if c['CONCEPT_OWNER'] else '*nenhum — é ponteiro*'}")
            w(f"- **para que serve** — {c['PURPOSE']}")
            w(f"- **até onde vale** — {c['SCOPE']}")
            caminho = c["CANONICAL_PATH"]
            if c["IN_TREE"]:
                w(f"- **onde vive** — [`{caminho}`]({caminho})")
            else:
                w(f"- **onde vive** — `{caminho}` — **não nesta árvore**; em `{c['LIVES_AT']}`")
            w(f"- **estado declarado** — `{c['LIFECYCLE']}`")
            w(f"- **estado medido** — `{c['OBSERVED_STATE']}` · {DIZ[c['OBSERVED_STATE']]}")
            # A DATA DO ULTIMO COMMIT NAO ENTRA AQUI, e nao e esquecimento.
            # Ela muda sozinha no instante em que este ficheiro e commitado, e
            # um documento gerado que muda por ser commitado nunca fecha a
            # verificacao anti-drift. Ela vive em `controle.generated.json`, que
            # nao entra nessa comparacao. O que entra aqui e o SHA do CONTEUDO,
            # que e o mesmo antes e depois do commit.
            #
            # COM UMA EXCECAO, E E ESTE FICHEIRO. Escrever aqui dentro a
            # impressao DESTE ficheiro e escrever o hash de uma coisa que muda
            # por eu o escrever: cada corrida mede o texto anterior, grava-o, e
            # com isso produz um texto novo para a corrida seguinte medir.
            #
            #     UM HASH DE SI PROPRIO NUNCA CHEGA A PONTO FIXO.
            #
            # A cadeia nunca fechava, e o mapa acusava drift para sempre. Fica
            # dito em vez de medido — que e a unica resposta honesta aqui.
            if c["CANONICAL_PATH"] == sala_canonica:
                w("- **impressão do conteúdo medido** — *não se mede a si própria: "
                  "o valor mudaria por ser escrito aqui*")
            elif c["SHA"]:
                w(f"- **impressão do conteúdo medido** — `{c['SHA']}`")
            if c["PROOF"]:
                w(f"- **prova** — `{c['PROOF']}`")
            if c["REFERENCED_BY"]:
                amostra = ", ".join(f"`{p}`" for p in c["REFERENCED_BY"][:4])
                mais = f" *(+{len(c['REFERENCED_BY']) - 4})*" if len(c["REFERENCED_BY"]) > 4 else ""
                w(f"- **quem aponta para ela** — {amostra}{mais}")
            if c["DIVERGENT_COPIES"]:
                w(f"- **cópias divergentes medidas** — {len(c['DIVERGENT_COPIES'])}: "
                  + ", ".join(f"`{r}`" for r in c["DIVERGENT_COPIES"]))
            if c["SUPERSEDED_BY"]:
                w(f"- **substituída por** — {', '.join(c['SUPERSEDED_BY'])}")
            w(f"- **o que ela diz de si** — {c['DECLARED_STATE']}")
            if c["NOTE"]:
                w(f"- **nota** — {c['NOTE']}")
            meus_arcos = de.get(c["CARD_ID"], [])
            if meus_arcos:
                w("")
                w("  | relação | alvo | estado | prova |")
                w("  |---|---|---|---|")
                for e in meus_arcos:
                    loc = f"`{e['PROOF_LOCATION']}`" if e["PROOF_LOCATION"] else \
                          f"*{e['PROOF_KIND'].lower()}*"
                    w(f"  | `{e['EDGE_TYPE']}` | `{e['TO_PATH']}` | "
                      f"**{e['EDGE_STATE']}** | {loc} |")
            w("")

    w("---")
    w("")
    w("## O QUE ESTÁ EM FALTA, DITO NA CARA")
    w("")
    faltam = [c for c in cartoes if not c["IN_TREE"]]
    if faltam:
        w("| autoridade | estado | vive em |")
        w("|---|---|---|")
        for c in faltam:
            w(f"| {c['NAME']} | `{c['LIFECYCLE']}` / `{c['OBSERVED_STATE']}` | "
              f"`{c['LIVES_AT']}` |")
    else:
        w("Nenhuma. Todas as autoridades registadas vivem nesta árvore.")
    w("")
    w("**Um ficheiro existir não prova que ele ainda manda — e não estar aqui não")
    w("prova que ele não existe.** As linhas acima foram medidas no git, não")
    w("presumidas: cada uma diz a ref onde a autoridade realmente está.")
    w("")
    w("---")
    w("")
    w("## DECLARADO ≠ OBSERVADO")
    w("")
    w(f"O censo mediu **{resumo['edges']}** relações de governo declaradas neste")
    w(f"registo. Delas, **{resumo['edges_observed']}** têm prova apontável")
    w(f"(ficheiro e linha dentro do texto da própria autoridade) e")
    w(f"**{resumo['edges_declared']}** continuam apenas declaradas.")
    w("")
    w("Uma relação declarada **não passa a observada por estar desenhada**. Quem")
    w("prova que uma lei governa uma peça é o texto da lei a nomear a peça — não o")
    w("mundo a mencionar a peça, e não o ficheiro existir.")
    w("")
    w("---")
    w("")
    w("## COMO A INTEGRIDADE DISTO É VALIDADA")
    w("")
    w("```bash")
    w("py controle/censo_do_controle.py     # mede o registo contra a árvore")
    w("py controle/portao_do_controle.py    # reprova quem mentir")
    w("```")
    w("")
    w("O portão corre no CI, no mesmo workflow do mapa. **Texto não reprova nada;")
    w("portão reprova.**")

    SALA.write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> int:
    global RASTREADOS, PROMOVE, ALVO_E_IDENTIDADE, POR_ID_DECLARADO
    RASTREADOS = set(rastreados())
    reg = json.loads(REGISTO.read_text(encoding="utf-8"))
    PROMOVE, ALVO_E_IDENTIDADE = exigencias(reg)
    POR_ID_DECLARADO = {a["CARD_ID"]: a for a in reg["AUTHORITIES"]}
    textos = carregar_textos(sorted(RASTREADOS))
    dono = dono_do_ficheiro()

    cartoes, arestas = [], []
    for a in reg["AUTHORITIES"]:
        caminho = a["CANONICAL_PATH"]
        ref = a.get("CANONICAL_REF", "IN_TREE")

        na_arvore = medir_no_git(caminho, "IN_TREE")
        # Uma autoridade que declara viver noutra linha e medida LA — para a
        # resposta ser «onde ela esta», e nao «ela nao existe».
        fora = medir_no_git(caminho, ref) if ref not in ("", "IN_TREE") else None

        # QUEM APONTA PARA ELA. Isto e o que separa uma lei viva de um ficheiro
        # que ficou. Nao conta o proprio ficheiro a nomear-se.
        aponta = sorted({f for f, linhas in textos.items()
                         if f != caminho and any(caminho in ln for ln in linhas)})

        if not na_arvore["existe"]:
            observado = "ABSENT_FROM_SNAPSHOT" if (fora and fora["existe"]) else "ABSENT"
        elif aponta:
            observado = "PRESENT_AND_POINTED"
        elif a.get("ENTRY_POINT"):
            # UMA PORTA NAO E ORFA POR NINGUEM APONTAR PARA ELA. Entra-se nela
            # de fora do repositorio — o GitHub abre `.github/copilot-
            # instructions.md` sozinho. Chamar-lhe orfa era transformar o
            # trabalho que ela faz num defeito.
            observado = "PRESENT_ENTRY_POINT"
        else:
            observado = "ORPHAN_IN_TREE"

        prova = ("git:HEAD:" + caminho) if na_arvore["existe"] else (
            f"git:{ref}:{caminho}" if (fora and fora["existe"]) else "")

        cartoes.append({
            "CARD_ID": a["CARD_ID"], "KIND": a["KIND"], "NAME": a["NAME"],
            "DOMAIN": a["DOMAIN"], "CONCEPT_OWNER": a["CONCEPT_OWNER"],
            "IS_POINTER": a.get("IS_POINTER", False),
            "PURPOSE": a["PURPOSE"], "SCOPE": a["SCOPE"],
            "CANONICAL_PATH": caminho, "CANONICAL_REF": ref,
            "VERSION": a["VERSION"], "LIFECYCLE": a["LIFECYCLE"],
            "DECLARED_STATE": a["DECLARED_STATE"], "NOTE": a.get("NOTE", ""),
            "SUPERSEDES": a.get("SUPERSEDES", []),
            "SUPERSEDED_BY": a.get("SUPERSEDED_BY", []),
            "DIVERGENT_COPIES": a.get("DIVERGENT_COPIES", []),
            # ── tudo abaixo daqui foi MEDIDO ─────────────────────────────────
            "OBSERVED_STATE": observado,
            "IN_TREE": na_arvore["existe"],
            "SHA": na_arvore["sha"] or (fora or {}).get("sha", ""),
            "LAST_VERIFIED": na_arvore["last_change"] or (fora or {}).get("last_change", ""),
            "LAST_COMMIT": na_arvore["last_commit"] or (fora or {}).get("last_commit", ""),
            "LAST_SUBJECT": na_arvore["last_subject"] or (fora or {}).get("last_subject", ""),
            "LIVES_AT": "HEAD" if na_arvore["existe"] else (
                ref if (fora and fora["existe"]) else "NOWHERE"),
            "PROOF": prova,
            "REFERENCED_BY": aponta,
            "REFERENCED_BY_COUNT": len(aponta),
        })

        for tipo in ("GOVERNS", "CONSTRAINS", "REFERENCES", "VALIDATES",
                     "OBSERVES", "GENERATES", "IMPLEMENTS", "SUPERSEDES"):
            for alvo in a.get(tipo, []):
                exige = PROMOVE[tipo]

                # ── ARESTA DE IDENTIDADE ─────────────────────────────────────
                # O alvo e um CARD_ID, e a resolucao dele nao passa pelo disco.
                #
                #     IDENTIDADE != MORADA.
                #
                # Mandar um CARD_ID pelo laco de caminho abaixo daria
                # `PROOF_KIND=ABSENT` — «ponteiro quebrado» — para a unica
                # coisa que uma supersessao quase sempre e: uma lei que ja nao
                # vive aqui, substituida por outra que vive. O defeito estava
                # no medidor, nao na relacao.
                if tipo in ALVO_E_IDENTIDADE:
                    alvo_card = POR_ID_DECLARADO.get(alvo)
                    if alvo_card is None:
                        prova_kind, prova_loc = "UNKNOWN_AUTHORITY_ID", ""
                    elif a["CARD_ID"] in alvo_card.get("SUPERSEDED_BY", []):
                        # A OUTRA PONTA CONFIRMA. Uma declaracao nao se prova a
                        # si propria: quem prova que A substituiu B e B a
                        # dizer que foi substituida por A, escrito noutro sitio.
                        prova_kind = "REGISTRY_RECIPROCAL"
                        prova_loc = f"registo:{alvo}.SUPERSEDED_BY"
                    else:
                        prova_kind, prova_loc = "MISSING_RECIPROCAL", ""
                    arestas.append({
                        "FROM": a["CARD_ID"], "TO_PATH": alvo,
                        "TO_KIND": "AUTHORITY_ID",
                        "TO_COMPONENT": "",
                        "TO_IN_TREE": bool(alvo_card) and alvo_card["CANONICAL_PATH"] in RASTREADOS,
                        "EDGE_TYPE": tipo,
                        "EDGE_PLANE": reg["EDGE_TYPES"][tipo]["plane"],
                        "EDGE_STATE": "OBSERVED" if prova_kind == exige else "DECLARED",
                        "PROOF_KIND": prova_kind, "PROOF_LOCATION": prova_loc,
                    })
                    continue

                alvo_existe = alvo in RASTREADOS
                peca = resolver_peca(alvo, dono)

                # A PROVA. Procurada DENTRO da autoridade, nunca no mundo: uma
                # lei que nao nomeia o que governa nao o governa de forma
                # medivel, por mais obvio que pareca a quem a escreveu.
                prova_kind, prova_loc = "ABSENT", ""
                if caminho not in textos:
                    # A AUTORIDADE NAO ESTA LEGIVEL NESTA ARVORE. Nao ha texto
                    # dela para conter prova nenhuma, e por isso nenhuma aresta
                    # que saia dela pode ser observada aqui. Continua declarada,
                    # e diz porque.
                    prova_kind = "AUTHORITY_ABSENT"
                elif not alvo_existe:
                    prova_kind = "ABSENT"
                elif exige == "MAP_OWNERSHIP":
                    prova_kind, prova_loc = ("MAP_OWNERSHIP", f"map:{peca}") if peca \
                        else ("PATH_EXISTS", "")
                else:
                    loc = procurar_dentro(textos, caminho, alvo)
                    if loc:
                        prova_kind, prova_loc = exige, loc
                    else:
                        prova_kind = "PATH_EXISTS"

                estado = "OBSERVED" if prova_kind == exige else "DECLARED"
                arestas.append({
                    "FROM": a["CARD_ID"], "TO_PATH": alvo,
                    "TO_KIND": "PATH",
                    "TO_COMPONENT": peca,
                    "EDGE_TYPE": tipo,
                    "EDGE_PLANE": reg["EDGE_TYPES"][tipo]["plane"],
                    "EDGE_STATE": estado,
                    "PROOF_KIND": prova_kind, "PROOF_LOCATION": prova_loc,
                })

    resumo = {
        "authorities": len(cartoes),
        "in_tree": sum(1 for c in cartoes if c["IN_TREE"]),
        "absent_from_snapshot": sum(1 for c in cartoes
                                    if c["OBSERVED_STATE"] == "ABSENT_FROM_SNAPSHOT"),
        "orphan_in_tree": sum(1 for c in cartoes if c["OBSERVED_STATE"] == "ORPHAN_IN_TREE"),
        "edges": len(arestas),
        "edges_observed": sum(1 for e in arestas if e["EDGE_STATE"] == "OBSERVED"),
        "edges_declared": sum(1 for e in arestas if e["EDGE_STATE"] == "DECLARED"),
    }

    SAIDA.write_text(json.dumps({
        "SCHEMA": "sintonia.control-plane.generated/1",
        "PROVENANCE": {"HEAD": git("rev-parse", "HEAD"),
                       "BRANCH": git("rev-parse", "--abbrev-ref", "HEAD")},
        "PLANES": reg["PLANES"],
        "EDGE_TYPES": reg["EDGE_TYPES"],
        "EVIDENCE_KINDS": reg["EVIDENCE_KINDS"],
        "CARDS": cartoes,
        "GOVERNANCE_EDGES": arestas,
        "COUNTS": resumo,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # QUAL CARTAO E A PROPRIA PORTA — perguntado ao registo, e nao ao nome do
    # ficheiro de saida. O portao regenera a sala para um caminho temporario
    # para a comparar com a commitada; se a resposta viesse do nome do ficheiro,
    # a regeneracao produzia um texto diferente e a comparacao acusava drift
    # que nao existe. Escrevi-o assim a primeira vez, e foi o proprio portao que
    # apanhou o erro.
    entradas = [a["CANONICAL_PATH"] for a in reg["AUTHORITIES"]
                if a["KIND"] == "REGISTRY" and a["CANONICAL_PATH"].endswith(".md")]
    sala_de_controle(cartoes, arestas, resumo, entradas[0] if entradas else "")

    print(f"CENSO_DO_CONTROLE=OK · autoridades={resumo['authorities']} "
          f"(na arvore {resumo['in_tree']} · ausentes desta foto "
          f"{resumo['absent_from_snapshot']} · sem quem aponte "
          f"{resumo['orphan_in_tree']}) · arestas={resumo['edges']} "
          f"(observadas {resumo['edges_observed']} · declaradas "
          f"{resumo['edges_declared']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
