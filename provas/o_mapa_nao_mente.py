#!/usr/bin/env python3
"""O MAPA NAO MENTE SOBRE EXISTENCIA — a prova de que a guarda morde.

    python3 provas/o_mapa_nao_mente.py

    SYSTEM_MAP_CHECK=PASS NAO BASTA
    SE ELE SO PROVA QUE O GERADOR CONCORDA CONSIGO PROPRIO.

O QUE ACONTECEU, E QUE ESTA PROVA EXISTE PARA IMPEDIR
------------------------------------------------------
Em 08/09/2026 o mapa publicou — e commitou — que
`system-map/scripts/censo_da_observabilidade.py` **nao existia no
repositorio**. O ficheiro estava no disco. E o `SYSTEM_MAP_CHECK` deu `PASS`
na mesma.

A cadeia da mentira, medida:

    scan_repo.py lista com `git ls-files`   ->  so o que ja foi `git add`ado
    ficheiro novo ainda nao rastreado       ->  fora do inventario
    generate_system_map: `_files` vazia     ->  VERMELHO
    a frase publicada: «nao existe no repositorio»

E a `P4_FICHEIROS_REAIS` nao apanhou, por duas cegueiras empilhadas: ela
compara o gerado com o gerado (o inventario tambem sai do `git ls-files`), e
itera a lista RESOLVIDA — que numa peca acusada de inexistente esta VAZIA. Zero
ficheiros iterados, prova passa.

    EXISTE NO DISCO  !=  RASTREADO PELO GIT  !=  NAO EXISTE.

E o pior: curou-se sozinho no commit seguinte. Uma mentira que desaparece
antes de alguem a investigar e a mais dificil de apanhar — por isso a guarda,
e por isso esta prova.

O QUE ELA FAZ
-------------
Injecta situacoes de propósito, exige a resposta certa em cada uma, e desfaz.
Nao vai a rede, nao toca producao, e confere no fim que a arvore ficou como
estava.
"""
import json
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECLARADO = os.path.join(RAIZ, "system-map", "data",
                         "architecture.declared.json")
ESTADO = os.path.join(RAIZ, "system-map", "data", "state.generated.json")
GERADOR = os.path.join(RAIZ, "system-map", "scripts", "generate_system_map.py")
VALIDADOR = os.path.join(RAIZ, "system-map", "scripts",
                         "validate_system_map.py")

# O ficheiro de mentira vive numa gaveta ja declarada, para nao mexer em P2.
REAL_MAS_NAO_RASTREADO = os.path.join(RAIZ, "provas", "zz_prova_temporaria.py")
NUNCA_EXISTIU = "provas/zz_ficheiro_que_nunca_existiu.py"

PECA_REAL = {
    "id": "C-ZZ-PROVA-REAL",
    "name": "Peca de mentira que aponta para ficheiro REAL",
    "territory": "Z-PROVA", "kind": "engine", "icon": "?",
    "what": "existe so durante esta prova",
    "why_here": "existe so durante esta prova",
    "departments": ["ENGENHARIA"],
    "files": ["provas/zz_prova_temporaria.py"],
    "views": ["audit"],
}
PECA_FANTASMA = {
    "id": "C-ZZ-PROVA-FANTASMA",
    "name": "Peca de mentira que aponta para ficheiro que NAO existe",
    "territory": "Z-PROVA", "kind": "engine", "icon": "?",
    "what": "existe so durante esta prova",
    "why_here": "existe so durante esta prova",
    "departments": ["ENGENHARIA"],
    "files": [NUNCA_EXISTIU],
    "views": ["audit"],
}


def _ambiente():
    e = dict(os.environ)
    e["PYTHONIOENCODING"] = "utf-8"
    return e


def _correr(*args):
    return subprocess.run(list(args), cwd=RAIZ, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          env=_ambiente())


def _gerar():
    return _correr(sys.executable, GERADOR)


def _validar():
    return _correr(sys.executable, VALIDADOR)


def _status_de(peca_id):
    with open(ESTADO, encoding="utf-8") as f:
        for n in json.load(f)["NODES"]:
            if n["id"] == peca_id:
                return n.get("status"), str(n.get("status_reason") or "")
    return None, ""


def _declarar(pecas):
    with open(DECLARADO, encoding="utf-8") as f:
        d = json.load(f)
    ids = {c["id"] for c in d["COMPONENTS"]}
    for p in pecas:
        if p["id"] not in ids:
            d["COMPONENTS"].append(p)
    with open(DECLARADO, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")


def cenario_1_real_mas_nao_rastreado():
    """SM1 · um caminho que EXISTE no disco nunca pode virar BROKEN."""
    with open(REAL_MAS_NAO_RASTREADO, "w", encoding="utf-8",
              newline="\n") as f:
        f.write("# ficheiro de mentira, apagado no fim desta prova\nX = 1\n")
    rastreado = _correr("git", "ls-files", "--error-unmatch",
                        "provas/zz_prova_temporaria.py").returncode == 0
    _declarar([PECA_REAL])
    _gerar()
    estado, razao = _status_de("C-ZZ-PROVA-REAL")
    print("  no disco: SIM · rastreado pelo Git: %s"
          % ("SIM  <-- a prova perde o sentido" if rastreado else "NAO"))
    print("  status  : %s" % estado)
    bom = estado != "BROKEN" and not rastreado
    print("  %s ficheiro real fora do inventario %s"
          % ("OK  " if bom else "FALHA",
             "nao virou BROKEN" if bom else "VIROU BROKEN <-- mentira"))
    if estado == "UNKNOWN":
        diz_a_verdade = "rastreado" in razao.lower() and "disco" in razao.lower()
        print("  %s a razao explica que e do Git, e nao inexistencia"
              % ("OK  " if diz_a_verdade else "FALHA"))
        bom = bom and diz_a_verdade
    return bom


def cenario_2_nunca_existiu():
    """SM2 · um caminho que NAO existe continua BROKEN. Sem afrouxar."""
    _declarar([PECA_FANTASMA])
    _gerar()
    estado, _r = _status_de("C-ZZ-PROVA-FANTASMA")
    bom = estado == "BROKEN"
    print("  status  : %s" % estado)
    print("  %s ficheiro inexistente continua BROKEN%s"
          % ("OK  " if bom else "FALHA",
             "" if bom else "  <-- a guarda afrouxou demais"))
    return bom


def cenario_3_a_guarda_reprova_a_mentira():
    """SM7 · a guarda tem de REPROVAR se o estado afirmar inexistencia de um
    ficheiro que esta no disco.

    ⚠️ E AQUI HOUVE UMA ARMADILHA QUE VALE A PENA CONTAR.

    A primeira versao desta prova injectava a mentira dentro de
    `state.generated.json` e corria o validador inteiro. Deu `PASS` — e eu
    quase escrevi que a guarda nao mordia.

    O validador REGENERA o estado antes de o validar (e a P1, anti-drift).
    A regeneracao apagava a injecção antes de a guarda chegar a ve-la.

        UMA GUARDA QUE SO PODE SER EXERCITADA
        PELO CAMINHO QUE A APAGA
        E UMA GUARDA QUE NINGUEM CONSEGUE PROVAR QUE MORDE.

    Por isso a guarda foi extraida para uma funcao pura, e e chamada aqui com
    um estado SINTETICO — sem tocar em ficheiro nenhum."""
    sys.path.insert(0, os.path.join(RAIZ, "system-map", "scripts"))
    import validate_system_map as v

    declarado = {"COMPONENTS": [
        {"id": "C-ZZ-MENTIRA", "files": ["provas/o_mapa_nao_mente.py"]},
        {"id": "C-ZZ-VERDADE", "files": [NUNCA_EXISTIU]},
    ]}
    nos = {
        # diz BROKEN, e o ficheiro ESTA no disco -> tem de ser apanhado
        "C-ZZ-MENTIRA": {"status": "BROKEN"},
        # diz BROKEN, e o ficheiro NAO existe -> legitimo, nao se apanha
        "C-ZZ-VERDADE": {"status": "BROKEN"},
    }
    achadas = v.mentiras_sobre_existencia(declarado, nos, RAIZ)
    apanhou = any("C-ZZ-MENTIRA" in m for m in achadas)
    poupou = not any("C-ZZ-VERDADE" in m for m in achadas)

    print("  estado sintetico: uma mentira e um BROKEN legitimo")
    print("  %s apanhou a mentira%s"
          % ("OK  " if apanhou else "FALHA",
             "" if apanhou else "  <-- guarda cega"))
    print("  %s poupou o BROKEN legitimo%s"
          % ("OK  " if poupou else "FALHA",
             "" if poupou else "  <-- guarda dispara a esmo"))

    # E a peca sem BROKEN nenhum nao pode ser acusada.
    calados = v.mentiras_sobre_existencia(
        declarado, {"C-ZZ-MENTIRA": {"status": "PROVEN"}}, RAIZ)
    quieta = not calados
    print("  %s nao acusa quem nao esta BROKEN" % ("OK  " if quieta else "FALHA"))
    return apanhou and poupou and quieta


def limpar():
    """Desfazer tudo, e conferir que desfez."""
    with open(DECLARADO, encoding="utf-8") as f:
        d = json.load(f)
    antes = len(d["COMPONENTS"])
    d["COMPONENTS"] = [c for c in d["COMPONENTS"]
                       if not c["id"].startswith("C-ZZ-PROVA")]
    with open(DECLARADO, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    if os.path.exists(REAL_MAS_NAO_RASTREADO):
        os.remove(REAL_MAS_NAO_RASTREADO)
    _gerar()
    sujo = _correr("git", "status", "--porcelain").stdout
    resto = [l for l in sujo.splitlines() if "zz_prova" in l]
    print("  pecas de mentira removidas: %d" % (antes - len(d["COMPONENTS"])))
    print("  %s nenhum residuo da prova na arvore"
          % ("OK  " if not resto else "FALHA <-- %s" % resto))
    return not resto


def main():
    print("PROVA — O MAPA MENTE SOBRE EXISTENCIA?")
    print("")
    print("SM1 — caminho REAL, ainda nao rastreado pelo Git")
    um = cenario_1_real_mas_nao_rastreado()
    print("")
    print("SM2 — caminho que nunca existiu")
    dois = cenario_2_nunca_existiu()
    print("")
    print("SM7 — a guarda reprova uma mentira injectada?")
    tres = cenario_3_a_guarda_reprova_a_mentira()
    print("")
    print("LIMPEZA")
    limpo = limpar()
    print("")

    r = _validar()
    voltou = "SYSTEM_MAP_CHECK=PASS" in ((r.stdout or "") + (r.stderr or ""))
    print("com tudo desfeito, o mapa volta a validar: %s"
          % ("SIM" if voltou else "NAO <-- ficou sujeira"))
    print("")
    bom = um and dois and tres and limpo
    print("MAPA_NAO_MENTE=%s" % ("PASS" if bom else "FAIL"))
    print("  o que isto prova: EXISTE NO DISCO != RASTREADO PELO GIT !=")
    print("  NAO EXISTE — e a guarda reprova quando o estado afirma")
    print("  inexistencia de um ficheiro que esta la.")
    return 0 if bom else 1


if __name__ == "__main__":
    sys.exit(main())
