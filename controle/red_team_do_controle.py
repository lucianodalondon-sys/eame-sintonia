#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM DO CONTROL PLANE — os doze ataques conhecidos, contra o portao real.

    py controle/red_team_do_controle.py

UM PORTAO QUE NUNCA FOI ATACADO NAO PROVOU QUE FECHA.

Cada ataque abaixo ja aconteceu, ou e trivialmente possivel de fazer sem querer.
Nenhum deles e hipotetico:

    RT01  desenhar uma seta GOVERNS sem referencia nenhuma
    RT02  carimbar um cartao de OBSERVED so porque o ficheiro existe
    RT03  pôr uma segunda Biblia CANONICAL para o mesmo departamento
    RT04  duplicar o know-how
    RT05  apagar uma autoridade registada
    RT06  quebrar o caminho da Biblia
    RT07  deixar a versao velha numa branch e faze-la parecer atual
    RT08  trocar o dono do conceito sem atualizar o registo
    RT09  fazer uma aresta escrita a mao sobrepor-se a aresta medida
    RT10  dar por provado um fluxo a partir de uma mencao qualquer
    RT11  fazer um HANDOFF aparecer como autoridade
    RT12  fazer o SYSTEM MAP aparecer como dono da arquitetura

    O RT01 NAO E HIPOTETICO NEM PARA MIM. O primeiro censo que escrevi nesta
    missao cometeu-o: quando a autoridade nao estava na arvore, a busca da prova
    caia para o mundo inteiro, e `BIBLIA-CANONICA-DA-COLETA.md` — que nao existe
    em `main` — aparecia a GOVERNAR `admissao/admissao.py`, com prova OBSERVED
    apontando para dentro de outro ficheiro. Este teste existe porque eu proprio
    precisei dele.

COMO OS ATAQUES CORREM
-----------------------
Sobre o CODIGO REAL — `censo_do_controle.py` e `portao_do_controle.py`, como
subprocessos — e sobre FICHEIROS TEMPORARIOS. As variaveis de ambiente
`SINTONIA_CONTROLE_*` desviam a leitura e a escrita para uma pasta descartavel.

    UM TESTE QUE ESTRAGA O QUE TESTA NAO SE CORRE DUAS VEZES.

O registo do repositorio nao e tocado por nenhum destes doze.

O QUE CONTA COMO DEFESA
------------------------
Nem todo ataque tem de dar FAIL. Alguns tem de dar **classificacao explicita** —
que e a defesa correta quando o estado atacado e um estado real que a casa pode
ter. Um ataque «defendido por classificacao» e um em que o sistema diz em voz
alta o que aconteceu, em vez de o esconder atras de um verde.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REGISTO_REAL = RAIZ / "controle" / "AUTORIDADES-CANONICAS.json"
CHAO_REAL = RAIZ / "controle" / "CHAO-DO-CONTROLE.json"

resultados: list[tuple[str, str, bool, str]] = []


def correr(registo: dict, pasta: Path, com_chao: bool = True) -> tuple[dict, int, str]:
    """Corre censo + portao reais sobre este registo, numa pasta descartavel."""
    p_reg = pasta / "registo.json"
    p_censo = pasta / "censo.json"
    p_sala = pasta / "sala.md"
    p_chao = pasta / "chao.json"
    p_reg.write_text(json.dumps(registo, ensure_ascii=False), encoding="utf-8")
    if com_chao and CHAO_REAL.exists():
        shutil.copyfile(CHAO_REAL, p_chao)

    env = {**os.environ,
           "SINTONIA_CONTROLE_REGISTO": str(p_reg),
           "SINTONIA_CONTROLE_CENSO": str(p_censo),
           "SINTONIA_CONTROLE_SALA": str(p_sala),
           "SINTONIA_CONTROLE_CHAO": str(p_chao)}

    c = subprocess.run([sys.executable, str(RAIZ / "controle" / "censo_do_controle.py")],
                       capture_output=True, text=True, env=env)
    if c.returncode != 0:
        return {}, c.returncode, c.stdout + c.stderr
    g = subprocess.run([sys.executable, str(RAIZ / "controle" / "portao_do_controle.py")],
                       capture_output=True, text=True, env=env)
    censo = json.loads(p_censo.read_text(encoding="utf-8"))
    return censo, g.returncode, g.stdout + g.stderr


def ataque(id_: str, oque: str):
    """Decorador: regista o veredito de um ataque."""
    def envolver(fn):
        with tempfile.TemporaryDirectory() as td:
            base = json.loads(REGISTO_REAL.read_text(encoding="utf-8"))
            try:
                defendido, como = fn(base, Path(td))
            except Exception as erro:                      # noqa: BLE001
                defendido, como = False, f"o ataque rebentou o medidor: {erro!r}"
        resultados.append((id_, oque, defendido, como))
        return fn
    return envolver


def achar(reg: dict, cid: str) -> dict:
    return next(a for a in reg["AUTHORITIES"] if a["CARD_ID"] == cid)


def falhou(saida: str, nome: str) -> bool:
    """O portao reprovou esta prova pelo nome?"""
    return f"FAIL  {nome}" in saida


# ══ RT01 ════════════════════════════════════════════════════════════════════
@ataque("RT01", "desenhar uma seta GOVERNS sem referencia real")
def rt01(reg, td):
    # AGENTS.md nao nomeia `motor/v21_cadeia.sh` em lado nenhum. Declarar que o
    # governa nao pode bastar para a seta nascer provada.
    achar(reg, "A-AGENTS")["GOVERNS"].append("motor/v21_cadeia.sh")
    censo, _, _ = correr(reg, td)
    e = next(x for x in censo["GOVERNANCE_EDGES"]
             if x["FROM"] == "A-AGENTS" and x["TO_PATH"] == "motor/v21_cadeia.sh")
    return (e["EDGE_STATE"] == "DECLARED",
            f"a seta ficou {e['EDGE_STATE']} com prova {e['PROOF_KIND']} — "
            "desenhar nao prova")


# ══ RT02 ════════════════════════════════════════════════════════════════════
@ataque("RT02", "carimbar OBSERVED so porque o ficheiro existe")
def rt02(reg, td):
    # O atacante escreve os campos medidos a mao, dentro do ficheiro declarado.
    a = achar(reg, "A-BIBLIA-INTELIGENCIA")
    a["OBSERVED_STATE"] = "PRESENT_AND_POINTED"
    a["PROOF"] = "confie em mim"
    a["LIVES_AT"] = "HEAD"
    censo, _, _ = correr(reg, td)
    c = next(x for x in censo["CARDS"] if x["CARD_ID"] == "A-BIBLIA-INTELIGENCIA")
    return (c["OBSERVED_STATE"] != "PRESENT_AND_POINTED",
            f"o censo remediu e escreveu {c['OBSERVED_STATE']} — o campo medido "
            "nao se aceita do ficheiro declarado")


# ══ RT03 ════════════════════════════════════════════════════════════════════
@ataque("RT03", "pôr uma segunda Biblia CANONICAL para o mesmo departamento")
def rt03(reg, td):
    gemea = dict(achar(reg, "A-BIBLIA-COLETA"))
    gemea["CARD_ID"] = "A-BIBLIA-COLETA-2"
    gemea["NAME"] = "Biblia da coleta (a minha versao)"
    gemea["CANONICAL_PATH"] = "docs/biblia/BIBLIA-DA-COLETA-V2.md"
    gemea["LIFECYCLE"] = "CANONICAL"
    reg["AUTHORITIES"].append(gemea)
    _, rc, saida = correr(reg, td)
    return (rc != 0 and falhou(saida, "DUPLICATE_CONCEPT_OWNER"),
            "DUPLICATE_CONCEPT_OWNER reprovou: LEI_DA_COLETA com dois donos")


# ══ RT04 ════════════════════════════════════════════════════════════════════
@ataque("RT04", "duplicar o know-how")
def rt04(reg, td):
    outro = dict(achar(reg, "A-KNOWHOW"))
    outro["CARD_ID"] = "A-KNOWHOW-2"
    outro["CONCEPT_OWNER"] = "KNOW_HOW_NOVO"      # esconde-se do teste do conceito
    outro["CANONICAL_PATH"] = "KNOW-HOW-2.md"
    reg["AUTHORITIES"].append(outro)
    _, rc, saida = correr(reg, td)
    return (rc != 0 and falhou(saida, "KNOW_HOW_DUPLICATED"),
            "KNOW_HOW_DUPLICATED reprovou mesmo com o conceito renomeado — a "
            "regra olha a ESPECIE, e nao o nome que o atacante escolheu")


# ══ RT05 ════════════════════════════════════════════════════════════════════
@ataque("RT05", "apagar uma autoridade registada")
def rt05(reg, td):
    reg["AUTHORITIES"] = [a for a in reg["AUTHORITIES"] if a["CARD_ID"] != "A-CLAUDE"]
    _, rc, saida = correr(reg, td)
    return (rc != 0 and falhou(saida, "UNREGISTERED_CANONICAL_DOCUMENT"),
            "UNREGISTERED_CANONICAL_DOCUMENT subiu acima do teto: CLAUDE.md "
            "continua a dizer-se dono e ja nao esta no registo")


# ══ RT06 ════════════════════════════════════════════════════════════════════
@ataque("RT06", "quebrar o caminho da Biblia")
def rt06(reg, td):
    a = achar(reg, "A-BIBLIA-COLETA")
    a["CANONICAL_PATH"] = "docs/biblia/CAMINHO-QUE-NAO-EXISTE.md"
    a["CANONICAL_REF"] = "IN_TREE"
    censo, rc, saida = correr(reg, td)
    c = next(x for x in censo["CARDS"] if x["CARD_ID"] == "A-BIBLIA-COLETA")
    return (c["OBSERVED_STATE"] == "ABSENT" and rc != 0,
            f"classificada {c['OBSERVED_STATE']} e o portao reprovou: uma lei "
            "canonica sem caminho nenhum nao passa em silencio")


# ══ RT07 ════════════════════════════════════════════════════════════════════
@ataque("RT07", "deixar a versao velha numa branch e faze-la parecer atual")
def rt07(reg, td):
    a = achar(reg, "A-KNOWHOW")
    a["DECLARED_STATE"] = "Esta atualissima, pode confiar."
    a["VERSION"] = "a mais recente de todas"
    censo, _, saida = correr(reg, td)
    c = next(x for x in censo["CARDS"] if x["CARD_ID"] == "A-KNOWHOW")
    # A defesa e por CLASSIFICACAO: o estado medido contradiz a frase declarada,
    # e o portao conta-a como STALE_AUTHORITY por regra objetiva — a ref
    # canonica nao e antepassada deste HEAD.
    return (c["OBSERVED_STATE"] == "ABSENT_FROM_SNAPSHOT"
            and "STALE_AUTHORITY" in saida,
            "o texto declarado nao move o estado medido: continua "
            "ABSENT_FROM_SNAPSHOT e contado em STALE_AUTHORITY")


# ══ RT08 ════════════════════════════════════════════════════════════════════
@ataque("RT08", "trocar o dono do conceito sem atualizar o registo")
def rt08(reg, td):
    # O atacante quer que o CONTRATO DE DESIGN passe a mandar no que a lei do
    # mapa manda, e reivindica o conceito dela sem lhe tirar o dono.
    achar(reg, "A-CONTRATO-DESIGN")["CONCEPT_OWNER"] = "LEI_DO_SYSTEM_MAP"
    _, rc, saida = correr(reg, td)
    return (rc != 0 and falhou(saida, "DUPLICATE_CONCEPT_OWNER"),
            "DUPLICATE_CONCEPT_OWNER reprovou: dois donos para LEI_DO_SYSTEM_MAP")


# ══ RT09 ════════════════════════════════════════════════════════════════════
@ataque("RT09", "fazer uma aresta escrita a mao sobrepor-se a aresta medida")
def rt09(reg, td):
    a = achar(reg, "A-CONTRATO-DESIGN")
    # `superficie/ask_sintonia.py` e uma GOVERNS que hoje esta DECLARED, porque
    # o contrato nao nomeia o ficheiro. O atacante escreve o resultado a mao.
    a["EDGE_STATE"] = "OBSERVED"
    a["PROOF_LOCATION"] = "docs/design/CONTRATO-DE-DESIGN-SINTONIA.md:1"
    a["PROOF_KIND"] = "TEXT_POINTER"
    censo, _, _ = correr(reg, td)
    e = next(x for x in censo["GOVERNANCE_EDGES"]
             if x["FROM"] == "A-CONTRATO-DESIGN"
             and x["TO_PATH"] == "superficie/ask_sintonia.py")
    return (e["EDGE_STATE"] == "DECLARED",
            "o censo ignorou o carimbo escrito a mao e remediu: "
            f"{e['EDGE_STATE']} / {e['PROOF_KIND']}")


# ══ RT10 ════════════════════════════════════════════════════════════════════
@ataque("RT10", "dar por provado um fluxo a partir de uma mencao qualquer")
def rt10(reg, td):
    # A AUTORIDADE ATACANTE TEM DE ESTAR NA ARVORE, senao este teste nao testa
    # nada: uma lei ausente ja e recusada por outro motivo (`AUTHORITY_ABSENT`),
    # e o ataque passaria por uma defesa que nao e a que se quer medir. Escrevi-o
    # assim a primeira vez, e o veredito vinha verde pela razao errada.
    #
    # `docs/design/CONTRATO-DE-DESIGN-SINTONIA.md` esta ca, e nao nomeia
    # `_gavetas.py`. Mas MEIA ARVORE nomeia `_gavetas.py` — AGENTS.md, o scanner
    # do mapa, noventa ficheiros de coleta. Se a prova pudesse vir de qualquer
    # lado, esta seta nascia provada.
    alvo = "_gavetas.py"
    achar(reg, "A-CONTRATO-DESIGN")["GOVERNS"].append(alvo)
    censo, _, _ = correr(reg, td)
    e = next(x for x in censo["GOVERNANCE_EDGES"]
             if x["FROM"] == "A-CONTRATO-DESIGN" and x["TO_PATH"] == alvo)
    return (e["EDGE_STATE"] == "DECLARED" and e["PROOF_KIND"] == "PATH_EXISTS",
            f"ficou {e['EDGE_STATE']} / {e['PROOF_KIND']} — a autoridade esta na "
            "arvore, o alvo existe, meia arvore nomeia o alvo, e mesmo assim nao "
            "ha prova: quem prova o governo e o texto de QUEM GOVERNA")


# ══ RT11 ════════════════════════════════════════════════════════════════════
@ataque("RT11", "fazer um HANDOFF aparecer como autoridade")
def rt11(reg, td):
    h = achar(reg, "H-BUILD-REUNIAO")
    h["GOVERNS"] = ["superficie/ask_sintonia.py"]
    h["LIFECYCLE"] = "CANONICAL"
    h["CONCEPT_OWNER"] = "LEI_DA_REUNIAO"
    _, rc, saida = correr(reg, td)
    return (rc != 0 and falhou(saida, "HANDOFF_AS_AUTHORITY"),
            "HANDOFF_AS_AUTHORITY reprovou: memoria de sessao nao governa")


# ══ RT12 ════════════════════════════════════════════════════════════════════
@ataque("RT12", "fazer o SYSTEM MAP aparecer como dono da arquitetura")
def rt12(reg, td):
    g = achar(reg, "O-GERADOR")
    g["GOVERNS"] = ["motor/v21_cadeia.sh", "admissao/admissao.py"]
    _, rc, saida = correr(reg, td)
    return (rc != 0 and falhou(saida, "SYSTEM_MAP_IS_AUTHORITY"),
            "SYSTEM_MAP_IS_AUTHORITY reprovou: o mapa mede e reprova, nunca governa")


def main() -> int:
    print("=" * 74)
    print("RED TEAM DO CONTROL PLANE — doze ataques contra o portao real")
    print("=" * 74)
    for id_, oque, ok, como in resultados:
        print(f"  {'DEFENDIDO' if ok else 'PASSOU   '}  {id_}  {oque}")
        print(f"             {como}")
    passaram = [r for r in resultados if not r[2]]
    print()
    print("=" * 74)
    if passaram:
        print(f"RED_TEAM=FAIL · {len(passaram)} de {len(resultados)} ataque(s) "
              "atravessaram o portao")
        print("=" * 74)
        return 1
    print(f"RED_TEAM=PASS · os {len(resultados)} ataques falharam ou foram "
          "classificados em voz alta")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
