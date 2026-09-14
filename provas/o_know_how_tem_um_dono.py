#!/usr/bin/env python3
"""O KNOW-HOW TEM UM DONO — a trava contra a divergencia da memoria duravel.

    python3 provas/o_know_how_tem_um_dono.py
    python3 provas/o_know_how_tem_um_dono.py --autoteste

    UM CONTADOR PARTILHADO DE QUE NINGUEM E DONO
    NAO E UM CONTADOR: SAO N CONTADORES COM O MESMO NOME.

O QUE ACONTECEU, E QUE ESTA GUARDA EXISTE PARA IMPEDIR
------------------------------------------------------
Medido em 2026-09-14: `SINTONIA-EAME-KNOW-HOW.md` existia em **20 referencias**
do git, com **15 conteudos distintos**. A partir do `§61`, e depois em bloco a
partir do `§91` e do `§111`, linhas diferentes escreveram **conhecimentos
diferentes no mesmo endereco**. O `§118` chegou a nomear TRES coisas sem
relacao nenhuma, e as tres estavam certas — cada uma no seu proprio ficheiro.

A causa nao foi descuido. Foi estrutural:

    MEDIR A CAUDA NA MINHA ARVORE RESPONDE «QUAL E O MEU PROXIMO NUMERO».
    NAO RESPONDE «QUAL E O PROXIMO NUMERO».

A lei esta escrita no `§141` do proprio know-how. Esta guarda e o lado
executavel dela.

O QUE ELA MEDE
--------------
    1 · UM_SO_FICHEIRO   nenhum segundo know-how concorrente na arvore
    2 · SEM_DUPLICADOS   nenhum numero de seccao repetido
    3 · SEMPRE_A_SUBIR   nenhuma numeracao regressiva
    4 · SEM_BURACO       nenhum buraco nao declarado em NUMEROS_QUEIMADOS
    5 · SUB_BATE         `## N.x` vive dentro do `§N` que o contem
    6 · DELTA_NAO_ALOCA  nenhum delta pendente cita um § que ja e de outro dono
    7 · DELTA_NAO_REPETE nenhum delta ja aplicado continua a pedir integracao

O QUE ELA **NAO** MEDE, DITO EM VOZ ALTA
----------------------------------------
NAO impede que uma missao edite o ficheiro numa branch dela: o git nao tem dono
por ficheiro. A trava do ACTO e social e vive no `§141`. Esta guarda apanha o
RESULTADO — colisao, duplicado, segundo ficheiro, delta a alocar sozinho.

NAO decide qual de dois conhecimentos em conflito e o verdadeiro. Isso exige
prova, e prova nao se automatiza aqui.

    UMA GUARDA QUE PROMETE MAIS DO QUE MEDE ENSINA A CONFIAR NO VERDE.

Nao vai a rede, nao toca banco, nao escreve na arvore.
"""
import os
import re
import sys
import glob

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANONICO = "SINTONIA-EAME-KNOW-HOW.md"

# Numeros que ja foram de alguem noutra linha e NAO voltam ao stock.
# Um buraco na numeracao e mais barato do que um endereco com dois passados.
NUMEROS_QUEIMADOS = {
    120: "usado por «A COLLECTION MEDIU CERTO CONTRA A FOTOGRAFIA DELA» na linha "
         "claude/intelligence-pilot-v1; reendereçado para §137 em 2026-09-14",
}

# Um segundo know-how nunca se chama «know-how 2». Chama-se uma destas.
SUFIXOS_CONCORRENTES = ("V2", "V3", "MASTER", "FINAL", "NEW", "MERGED", "COPY",
                        "CONSOLIDADO", "UNIFICADO")

# Ficheiros de handoff que NAO sao deltas, e que nao devem ser lidos como tal.
NAO_E_DELTA = re.compile(r"KNOW-HOW-(RECONCILIATION|RECONCILIACAO)", re.I)

CAB_SECCAO = re.compile(r"^# §(\d+)\s*[·—\-:.]?\s*(.*)$")
CAB_SUB = re.compile(r"^#{2,4}\s*(\d+)\.(\d+)")
# Num delta a lei pode ainda nao ter numero: «\u00a7<PROXIMO LIVRE>», «\u00a7NEXT».
CAB_DELTA = re.compile(r"^# \u00a7(?:(\d+)|<[^>]*>|NEXT|N)\s*[\u00b7\u2014\-:.]?\s*(.*)$")


def _ler(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return fh.read().split("\n")


def _seccoes(linhas):
    """Devolve [(numero, titulo, indice_da_linha)] pela ordem em que aparecem."""
    fora = []
    for i, linha in enumerate(linhas):
        m = CAB_SECCAO.match(linha)
        if m:
            fora.append((int(m.group(1)), m.group(2).strip(), i))
    return fora


def _ficheiros_rastreados(raiz):
    """Lista o que o git rastreia. Sem git, cai para a varredura do disco."""
    import subprocess
    try:
        saida = subprocess.run(["git", "-C", raiz, "ls-files"],
                               capture_output=True, text=True, timeout=30)
        if saida.returncode == 0 and saida.stdout.strip():
            return saida.stdout.strip().split("\n")
    except Exception:
        pass
    fora = []
    for base, _dirs, ficheiros in os.walk(raiz):
        if ".git" in base:
            continue
        for f in ficheiros:
            fora.append(os.path.relpath(os.path.join(base, f), raiz))
    return fora


# --------------------------------------------------------------------------
# as sete perguntas
# --------------------------------------------------------------------------

def c1_um_so_ficheiro(raiz, _linhas):
    falhas = []
    for caminho in _ficheiros_rastreados(raiz):
        nome = os.path.basename(caminho).upper()
        if caminho == CANONICO:
            continue
        if not nome.startswith("SINTONIA-EAME-KNOW-HOW"):
            continue
        falhas.append(
            "segundo know-how concorrente: %s  (o dono canonico e %s)"
            % (caminho, CANONICO))
    # e a forma disfarcada: KNOW-HOW-<SUFIXO>.md solto na raiz
    for caminho in _ficheiros_rastreados(raiz):
        nome = os.path.basename(caminho).upper()
        if caminho == CANONICO or "/" in caminho:
            continue
        if "KNOW-HOW" in nome and any(s in nome for s in SUFIXOS_CONCORRENTES):
            falhas.append("know-how concorrente disfarcado na raiz: %s" % caminho)
    return falhas


def c2_sem_duplicados(_raiz, linhas):
    vistos = {}
    falhas = []
    for num, titulo, _i in _seccoes(linhas):
        if num in vistos:
            falhas.append(
                "§%d aparece duas vezes:\n      1) %s\n      2) %s"
                % (num, vistos[num][:70], titulo[:70]))
        else:
            vistos[num] = titulo
    return falhas


def c3_sempre_a_subir(_raiz, linhas):
    falhas = []
    anterior = None
    for num, titulo, _i in _seccoes(linhas):
        if anterior is not None and num <= anterior:
            falhas.append("numeracao regressiva: §%d vem depois de §%d  (%s)"
                          % (num, anterior, titulo[:60]))
        anterior = num
    return falhas


def c4_sem_buraco(_raiz, linhas):
    nums = sorted({n for n, _t, _i in _seccoes(linhas)})
    falhas = []
    for esperado in range(nums[0], nums[-1] + 1):
        if esperado in nums:
            continue
        if esperado in NUMEROS_QUEIMADOS:
            continue
        falhas.append("buraco nao declarado na numeracao: §%d nao existe "
                      "e nao esta em NUMEROS_QUEIMADOS" % esperado)
    return falhas


def c5_sub_bate(_raiz, linhas):
    seccoes = _seccoes(linhas)
    falhas = []
    for pos, (num, _titulo, inicio) in enumerate(seccoes):
        fim = seccoes[pos + 1][2] if pos + 1 < len(seccoes) else len(linhas)
        dentro_de_citacao = False
        for i in range(inicio + 1, fim):
            linha = linhas[i]
            # blocos `>` guardam registo historico de outra linha: nao se medem
            if linha.startswith(">"):
                dentro_de_citacao = True
                continue
            dentro_de_citacao = False
            m = CAB_SUB.match(linha)
            if m and int(m.group(1)) != num:
                falhas.append(
                    "sub-numeracao fora de casa: `%s` dentro do §%d"
                    % (linha.strip()[:60], num))
    return falhas


def _deltas(raiz):
    fora = []
    for caminho in sorted(glob.glob(os.path.join(raiz, "handoff", "*.md"))):
        nome = os.path.basename(caminho)
        if "KNOW-HOW" not in nome.upper():
            continue
        if NAO_E_DELTA.search(nome):
            continue
        fora.append(caminho)
    return fora


def c6_delta_nao_aloca(raiz, linhas):
    """Um delta pode PROPOR. Nao pode ALOCAR um numero que ja e de outro dono."""
    donos = {n: t for n, t, _i in _seccoes(linhas)}
    falhas = []
    for caminho in _deltas(raiz):
        texto = _ler(caminho)
        nome = os.path.relpath(caminho, raiz)
        aplicado = any("APLICADO_EM" in l for l in texto)
        for linha in texto:
            m = CAB_SECCAO.match(linha)
            if not m:
                continue
            num, titulo = int(m.group(1)), m.group(2).strip()
            if num not in donos:
                continue
            if _mesma_lei(titulo, donos[num]):
                continue          # ja integrado nesse endereco: c7 trata disto
            if aplicado:
                continue          # o delta ja declarou onde aterrou
            falhas.append(
                "%s aloca §%d sozinho, e §%d ja e de outro dono:\n"
                "      delta:    %s\n      canonico: %s"
                % (nome, num, num, titulo[:66], donos[num][:66]))
    return falhas


def c7_delta_nao_repete(raiz, linhas):
    """Um delta cuja lei ja esta no canonico tem de o declarar, ou sera aplicado
    duas vezes pela proxima pessoa que abrir a pasta."""
    titulos = [t for _n, t, _i in _seccoes(linhas)]
    falhas = []
    for caminho in _deltas(raiz):
        texto = _ler(caminho)
        nome = os.path.relpath(caminho, raiz)
        if any("APLICADO_EM" in l for l in texto):
            continue
        for linha in texto:
            m = CAB_DELTA.match(linha)
            if not m:
                continue
            titulo = m.group(2).strip()
            if not titulo:
                continue
            for canonico in titulos:
                if _mesma_lei(titulo, canonico):
                    falhas.append(
                        "%s ja foi aplicado e continua a pedir integracao:\n"
                        "      a lei «%s»\n      ja vive no canonico. Falta "
                        "`APLICADO_EM` no cabecalho do delta."
                        % (nome, titulo[:66]))
                    break
    return falhas


def _mesma_lei(a, b):
    norm = lambda s: re.sub(r"[^A-Z0-9]", "", s.upper())[:60]
    na, nb = norm(a), norm(b)
    return bool(na) and na == nb


PERGUNTAS = [
    ("UM_SO_FICHEIRO", c1_um_so_ficheiro),
    ("SEM_DUPLICADOS", c2_sem_duplicados),
    ("SEMPRE_A_SUBIR", c3_sempre_a_subir),
    ("SEM_BURACO", c4_sem_buraco),
    ("SUB_BATE", c5_sub_bate),
    ("DELTA_NAO_ALOCA", c6_delta_nao_aloca),
    ("DELTA_NAO_REPETE", c7_delta_nao_repete),
]


def correr(raiz):
    caminho = os.path.join(raiz, CANONICO)
    if not os.path.exists(caminho):
        print("FALHA  o know-how canonico nao existe: %s" % CANONICO)
        return 1
    linhas = _ler(caminho)
    seccoes = _seccoes(linhas)
    print("KNOW_HOW_GUARD  %s" % CANONICO)
    print("  seccoes medidas : %d   (§%d .. §%d)"
          % (len(seccoes), seccoes[0][0], seccoes[-1][0]))
    print("  deltas em handoff: %d" % len(_deltas(raiz)))
    print("")
    mau = 0
    for nome, fn in PERGUNTAS:
        falhas = fn(raiz, linhas)
        if falhas:
            mau += len(falhas)
            print("  FALHA  %s" % nome)
            for f in falhas:
                print("      %s" % f)
        else:
            print("  ok     %s" % nome)
    print("")
    print("KNOW_HOW_GUARD = %s" % ("PASS" if mau == 0 else "FAIL"))
    return 0 if mau == 0 else 1


# --------------------------------------------------------------------------
# autoteste: a guarda tem de MORDER, e morder no sitio certo
# --------------------------------------------------------------------------

def autoteste():
    import shutil
    import tempfile
    base = os.path.join(RAIZ, CANONICO)
    original = _ler(base)
    ultimo = _seccoes(original)[-1][0]

    casos = []

    def caso(nome, pergunta, mutacao):
        casos.append((nome, pergunta, mutacao))

    # Um duplicado E, por forca, uma numeracao que nao sobe: as duas acendem,
    # e exigir so uma seria exigir que a guarda mentisse.
    caso("seccao duplicada", {"SEM_DUPLICADOS", "SEMPRE_A_SUBIR"},
         lambda l, d: l + ["", "# §%d · UM NUMERO ROUBADO A SI PROPRIO" % ultimo])
    # §120 esta queimado: nao existe no ficheiro, logo desce sem duplicar.
    caso("numeracao regressiva", {"SEMPRE_A_SUBIR"},
         lambda l, d: l + ["", "# §120 · UMA SECCAO QUE DESCE"])
    caso("buraco na numeracao", {"SEM_BURACO"},
         lambda l, d: l + ["", "# §%d · UM SALTO POR CIMA DE TRES" % (ultimo + 4)])
    caso("sub-numeracao fora de casa", {"SUB_BATE"},
         lambda l, d: l + ["", "# §%d · UMA SECCAO SA" % (ultimo + 1),
                           "", "## %d.1 · O FILHO DE OUTRA MAE" % (ultimo - 9)])

    def segundo_ficheiro(l, d):
        with open(os.path.join(d, "SINTONIA-EAME-KNOW-HOW-V2.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("# um segundo dono\n")
        return l
    caso("segundo know-how na arvore", {"UM_SO_FICHEIRO"}, segundo_ficheiro)

    def delta_aloca(l, d):
        os.makedirs(os.path.join(d, "handoff"), exist_ok=True)
        with open(os.path.join(d, "handoff", "KNOW-HOW-DELTA-ZZ-PROVA.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("# DELTA\n\n# §%d · UMA LEI QUE ESCOLHEU O NUMERO "
                     "SOZINHA\n" % (ultimo - 1))
        return l
    caso("delta aloca numero de outro dono", {"DELTA_NAO_ALOCA"}, delta_aloca)

    def delta_repete(l, d):
        titulo = _seccoes(l)[-1][1]
        os.makedirs(os.path.join(d, "handoff"), exist_ok=True)
        with open(os.path.join(d, "handoff", "KNOW-HOW-DELTA-ZZ-REPETE.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("# DELTA\n\n# §<PROXIMO LIVRE> · %s\n" % titulo)
        return l
    caso("delta ja aplicado ainda a pedir", {"DELTA_NAO_REPETE"}, delta_repete)

    print("AUTOTESTE — a guarda tem de reprovar cada um destes, e so este\n")
    maus = 0
    for nome, pergunta, mutacao in casos:
        tmp = tempfile.mkdtemp(prefix="kh_guard_")
        try:
            os.makedirs(os.path.join(tmp, "handoff"), exist_ok=True)
            linhas = mutacao(list(original), tmp)
            with open(os.path.join(tmp, CANONICO), "w", encoding="utf-8") as fh:
                fh.write("\n".join(linhas))
            conteudo = _ler(os.path.join(tmp, CANONICO))
            apanhadas = {n for n, fn in PERGUNTAS if fn(tmp, conteudo)}
            if apanhadas == pergunta:
                print("  ok     %-34s -> %s"
                      % (nome, " + ".join(sorted(pergunta))))
            else:
                maus += 1
                print("  FALHA  %-34s esperado %s, veio %s"
                      % (nome, sorted(pergunta), sorted(apanhadas)))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # e o controlo positivo: uma arvore limpa nao pode acender nada
    tmp = tempfile.mkdtemp(prefix="kh_guard_")
    try:
        os.makedirs(os.path.join(tmp, "handoff"), exist_ok=True)
        shutil.copy(base, os.path.join(tmp, CANONICO))
        for f in _deltas(RAIZ):
            shutil.copy(f, os.path.join(tmp, "handoff", os.path.basename(f)))
        conteudo = _ler(os.path.join(tmp, CANONICO))
        acesas = [n for n, fn in PERGUNTAS if fn(tmp, conteudo)]
        if acesas:
            maus += 1
            print("  FALHA  %-34s arvore limpa acendeu %s"
                  % ("controlo positivo", acesas))
        else:
            print("  ok     %-34s nada acendeu" % "controlo positivo")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("AUTOTESTE = %s" % ("PASS" if maus == 0 else "FAIL"))
    return 0 if maus == 0 else 1


if __name__ == "__main__":
    if "--autoteste" in sys.argv:
        sys.exit(autoteste())
    sys.exit(correr(RAIZ))
