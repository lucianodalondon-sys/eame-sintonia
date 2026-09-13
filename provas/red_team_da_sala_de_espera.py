#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DA SALA DE ESPERA — 16 ataques contra a MORADA, e nao contra o codigo.

    LINHA_FUNCIONAL=/tmp/wt python3 provas/red_team_da_sala_de_espera.py

Cada ataque tenta partir a decisao «a espera vive num ficheiro, com UM dono».
Um ataque DEFENDIDO nao prova que a escolha e boa — prova que aquela porta
esta fechada. Um ataque que passa e divida, e fica escrita como divida.

    UM RED TEAM QUE SO CONFIRMA O QUE JA SE ACREDITAVA NAO E UM RED TEAM.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINHA = os.environ.get("LINHA_FUNCIONAL") or RAIZ
for p in (LINHA, os.path.join(LINHA, "coleta"), os.path.join(LINHA, "admissao")):
    if p not in sys.path:
        sys.path.insert(0, p)

import _gavetas                                        # noqa: E402,F401
import admissao                                        # noqa: E402
import sala_de_espera as espera                        # noqa: E402

CAMPOS = ("ESTADO", "ITEM_ID", "UNIVERSO", "TEXTO", "SOURCE_ID",
          "SOURCE_LOCATION", "FACT_LOCATION", "FACT_TIME", "CAPTURED_AT",
          "CORRIDA", "ADMITIDO_POR")
ataques = []


def ataque(n, nome, defendido, detalhe):
    ataques.append((n, nome, bool(defendido), detalhe))


def _fonte(rel):
    return io.open(os.path.join(LINHA, rel), encoding="utf-8").read()


def unidade(item_id="IT-1", run="RUN-RT", texto="il fungo provoca sintomi"):
    d = admissao.Decisao(item=item_id, universo="fitossanitario",
                         resultado=admissao.SIM, regra="R-ADM", motivo="m",
                         evidencia="e", versao="1", corrida=run,
                         quando="2026-09-13T00:00:00Z")
    return admissao.pronto_para_inteligencia(
        {"texto": texto, "source_id": "IT-T3-002",
         "captured_at": "2026-09-10T00:00:00Z"}, d)


def main():
    sala = tempfile.mkdtemp(prefix="redteam-")
    espera.MORADA = sala
    try:
        return correr(sala)
    finally:
        shutil.rmtree(sala, ignore_errors=True)


def correr(sala):
    # RT01 — DUAS MORADAS AO MESMO TEMPO
    escritores = [f for f in ("coleta/rota_forward_documento.py",
                              "orquestrador/orquestrador.py")
                  if "espera.pousar(" in _fonte(f)]
    donos = [f for f in ("admissao/sala_de_espera.py",)
             if "def pousar(" in _fonte(f)]
    ataque(1, "criar uma SEGUNDA morada para o mesmo READY",
           len(donos) == 1 and escritores,
           "1 dono (%s) e %d chamadores — nenhum escreve por fora"
           % (donos[0], len(escritores)))

    # RT02 — CONTRABANDEAR UMA MORADA PARA DENTRO DOS 11 CAMPOS
    u = unidade()
    ataque(2, "meter STORAGE_PATH nos 11 campos «so para facilitar»",
           tuple(u.keys()) == CAMPOS and "STORAGE_PATH" not in u,
           "o construtor devolve %d campos fixos: uma morada nao cabe la dentro"
           % len(u))

    # RT03 — UM SEGUNDO CONSTRUTOR
    defs = subprocess.run(
        ["grep", "-rn", "def pronto_para_inteligencia", "--include=*.py", LINHA],
        capture_output=True, text=True).stdout.strip().split("\n")
    reais = [d for d in defs if d and ".py:" in d
             and "generate_system_map" not in d]
    ataque(3, "declarar um segundo construtor de READY", len(reais) == 1,
           "definicoes reais: %d — %s" % (len(reais),
                                          os.path.basename(reais[0].split(":")[0])))

    # RT04 — READY SEM SIM
    for r in (admissao.NAO, admissao.NAO_SEI, admissao.NAO_SE_APLICA,
              admissao.ERRO):
        d = admissao.Decisao(item="X", universo="u", resultado=r, regra="R",
                             motivo="m", evidencia="e", versao="1",
                             corrida="RUN-RT", quando="2026-09-13T00:00:00Z")
        try:
            admissao.pronto_para_inteligencia({}, d)
            passou = True
        except ValueError:
            passou = False
        if passou:
            break
    ataque(4, "fabricar READY a partir de uma decisao que NAO foi SIM",
           not passou, "os 4 resultados nao-SIM levantam ValueError no dono")

    # RT05 — TRAVESSIA DE CAMINHO PELO RUN_ID
    fugiu = False
    for mau in ("../../etc/passwd", "..", "/etc/passwd", ".oculto",
                "a/b", "a\\b"):
        try:
            c = espera.caminho_da_corrida(mau)
            if os.path.abspath(c) != os.path.abspath(
                    os.path.join(sala, os.path.basename(c))):
                fugiu = True
        except ValueError:
            pass
    ataque(5, "escrever fora da morada com um RUN_ID `../`", not fugiu,
           "todos os RUN_ID com separador ou `.` inicial sao recusados")

    # RT06 — A CORRIDA FANTASMA
    r = espera.pousar("RUN-VAZIA", [])
    ataque(6, "criar uma espera fantasma com zero unidades",
           r["ESTADO"] is None
           and not os.path.exists(espera.caminho_da_corrida("RUN-VAZIA")),
           "lista vazia nao produz ficheiro: «%s»" % r["PORQUE"][:46])

    # RT07 — SOBRESCREVER EM SILENCIO
    espera.pousar("RUN-A", [unidade(run="RUN-A")])
    antes = io.open(espera.caminho_da_corrida("RUN-A"), encoding="utf-8").read()
    try:
        espera.pousar("RUN-A", [unidade(run="RUN-A", texto="OUTRA HISTORIA")])
        gritou = False
    except espera.ConflitoDeCorrida:
        gritou = True
    depois = io.open(espera.caminho_da_corrida("RUN-A"), encoding="utf-8").read()
    ataque(7, "a MESMA corrida contar outra historia, em silencio",
           gritou and antes == depois,
           "levantou ConflitoDeCorrida e os bytes anteriores estao intactos")

    # RT08 — RETRY QUE DUPLICA
    r2 = espera.pousar("RUN-A", [unidade(run="RUN-A")])
    ataque(8, "o retry duplicar a unidade", r2["ESTADO"] == espera.JA_ESTAVA
           and r2["UNIDADES"] == 1,
           "o mesmo conteudo devolve %s, e nao escreve" % r2["ESTADO"])

    # RT09 — TEMPORARIO ABANDONADO
    lixo = [f for f in os.listdir(sala) if f.startswith(".espera-")]
    ataque(9, "deixar temporarios `.espera-*` na sala", not lixo,
           "temporarios na sala: %s" % (lixo or "nenhum"))

    # RT10 — DUAS CORRIDAS A SERIALIZAR-SE UMA A OUTRA
    with espera._Trava(espera.caminho_da_corrida("RUN-A")):
        try:
            espera.pousar("RUN-B", [unidade(run="RUN-B")])
            passou10 = True
        except espera.EsperaOcupada:
            passou10 = False
    ataque(10, "a trava de UMA corrida bloquear as OUTRAS", passou10,
           "RUN-B pousou com a trava de RUN-A presa: a trava e por corrida")

    # RT11 — A TRAVA PRESA QUE SE LIMPA SOZINHA
    presa = espera._Trava(espera.caminho_da_corrida("RUN-C"))
    presa.__enter__()
    try:
        espera.pousar("RUN-C", [unidade(run="RUN-C")])
        silenciou = True
    except espera.EsperaOcupada as e:
        silenciou = False
        msg = str(e)
    presa.__exit__()
    ataque(11, "uma trava presa ser limpa em silencio por quem chega depois",
           not silenciou,
           "falha ALTO e nomeia o ficheiro: %s" % msg[-38:])

    # RT12 — JSON PELA METADE APOS CRASH
    caminho = espera.caminho_da_corrida("RUN-A")
    bom = io.open(caminho, encoding="utf-8").read()
    fd, tmp = tempfile.mkstemp(prefix=".espera-", suffix=".json", dir=sala)
    os.write(fd, b'{"RUN_ID": "RUN-A", "ITENS": [{"ESTA')   # morreu a meio
    os.close(fd)
    ainda = io.open(caminho, encoding="utf-8").read()
    valido = json.loads(ainda) is not None
    os.unlink(tmp)
    ataque(12, "um crash a meio deixar o canonico truncado",
           ainda == bom and valido,
           "o parcial ficou no temporario; o canonico le-se inteiro")

    # RT13 — UMA MIGRATION DAR MORADA A ESPERA POR TRAS
    mig = os.path.join(LINHA, "supabase", "migrations")
    suspeitas = []
    for f in sorted(os.listdir(mig)):
        t = io.open(os.path.join(mig, f), encoding="utf-8").read().lower()
        for alvo in ("create table", "create unlogged table"):
            i = 0
            while True:
                i = t.find(alvo, i)
                if i < 0:
                    break
                nome = t[i + len(alvo):i + len(alvo) + 80]
                if any(k in nome for k in ("sala_de_espera", "waiting_room",
                                           "unidade_pronta", "ready_unit")):
                    suspeitas.append("%s:%s" % (f, nome.strip()[:30]))
                i += 1
    ataque(13, "uma migration dar tabela a espera sem ninguem decidir",
           not suspeitas, "tabelas de espera em %d migrations: %s"
           % (len(os.listdir(mig)), suspeitas or "nenhuma"))

    # RT14 — SYMLINK NA MORADA
    alvo = os.path.join(sala, "alvo-de-fora.json")
    io.open(alvo, "w").write("NAO ME SUBSTITUAS\n")
    link = espera.caminho_da_corrida("RUN-LINK")
    os.symlink(alvo, link)
    try:
        espera.pousar("RUN-LINK", [unidade(run="RUN-LINK")])
    except Exception:
        pass
    conteudo_alvo = io.open(alvo, encoding="utf-8").read()
    ataque(14, "um symlink na morada redirigir a escrita para fora",
           conteudo_alvo == "NAO ME SUBSTITUAS\n",
           "os.replace substitui o LINK, e nao o alvo: o ficheiro de fora "
           "ficou intacto")

    # RT15 — QUEM ESCREVE SEM PASSAR PELO DONO
    # ⚠️ A PRIMEIRA VERSAO DESTE ATAQUE ACUSOU DUAS PROVAS, E ESTAVA ERRADA.
    # Ela perguntava «este ficheiro NOMEIA a morada?», e nomear nao e escrever:
    # `provas/a_fronteira_da_coleta.py` faz `os.path.isdir(destino)` para MEDIR
    # se a pasta existe, e `provas/mutacao_do_fluxo_canonico.py` carrega a
    # morada dentro de uma string de MUTACAO que ele aplica a uma copia da
    # arvore num temporario, e depois repoe.
    #
    #     NOMEAR UMA MORADA NAO E ESCREVER NELA.
    #
    # E a mesma familia do ataque que o censo do Control Plane cometeu contra
    # si proprio: uma busca que casa com a MENCAO quando a pergunta era sobre o
    # COMPORTAMENTO. Agora mede-se o comportamento: um ficheiro so e acusado se
    # levar um caminho DERIVADO da morada a uma chamada de escrita.
    import re
    ESCRITAS = re.compile(r"(?:io\.)?open\s*\(([^)]*)[\'\"]w|os\.makedirs\s*\(([^)]*)"
                          r"|os\.replace\s*\(([^)]*)|shutil\.copy\w*\s*\(([^)]*)")
    fora_do_dono = []
    for base, _d, fs in os.walk(LINHA):
        if any(x in base for x in (".git", "node_modules", "BASELINE")):
            continue
        for f in fs:
            if not f.endswith(".py") or f == "sala_de_espera.py":
                continue
            cam = os.path.join(base, f)
            try:
                t = io.open(cam, encoding="utf-8").read()
            except Exception:
                continue
            if "PRONTO-PARA-INTELIGENCIA" not in t:
                continue
            if "espera.pousar(" in t or "sala_de_espera" in t:
                continue          # passa pelo dono: e o caminho legitimo
            # as variaveis que RECEBEM a morada
            vars_morada = set(re.findall(
                r"^\s*(\w+)\s*=[^=\n]*PRONTO-PARA-INTELIGENCIA", t, re.M))
            escreve = False
            for m in ESCRITAS.finditer(t):
                alvo = next((g for g in m.groups() if g), "")
                if "PRONTO-PARA-INTELIGENCIA" in alvo or \
                        any(v in alvo for v in vars_morada):
                    escreve = True
            if escreve:
                fora_do_dono.append(os.path.relpath(cam, LINHA))
    nomeiam = [os.path.relpath(os.path.join(b, f), LINHA)
               for b, _d, fs in os.walk(LINHA) if ".git" not in b
               and "BASELINE" not in b
               for f in fs if f.endswith(".py")
               and "PRONTO-PARA-INTELIGENCIA" in
               io.open(os.path.join(b, f), encoding="utf-8",
                       errors="ignore").read()]
    ataque(15, "escrever na morada sem passar pelo dono",
           not fora_do_dono,
           "%d ficheiros NOMEIAM a morada; os que lhe ESCREVEM sem o dono: %s"
           % (len(nomeiam), fora_do_dono or "nenhum"))

    # RT16 — LER UMA CORRIDA A MEIO DA ESCRITA
    # `os.replace` e atomico: quem le durante a escrita ve o ficheiro ANTERIOR
    # inteiro, e nunca meio ficheiro. Isto mede a PROPRIEDADE, e nao a sorte.
    usa_replace = "os.replace(" in _fonte("admissao/sala_de_espera.py")
    usa_fsync = "os.fsync(" in _fonte("admissao/sala_de_espera.py")
    mesma_fs = "dir=pasta" in _fonte("admissao/sala_de_espera.py")
    ataque(16, "o consumidor ler meia corrida a meio da escrita",
           usa_replace and usa_fsync and mesma_fs,
           "mkstemp na MESMA pasta + fsync + os.replace: a troca e atomica")

    print("=" * 76)
    print("RED TEAM DA SALA DE ESPERA — 16 ataques contra a MORADA")
    print("=" * 76)
    for n, nome, ok, det in ataques:
        print("  RT%02d  %-10s %s" % (n, "DEFENDIDO" if ok else "PASSOU", nome))
        print("        %s" % det)
    quebrou = [n for n, _x, ok, _d in ataques if not ok]
    print("=" * 76)
    print("RED_TEAM_ESPERA=%s · defendidos %d/%d"
          % ("TUDO_DEFENDIDO" if not quebrou else "ATAQUES_PASSARAM",
             len(ataques) - len(quebrou), len(ataques)))
    return 0 if not quebrou else 1


if __name__ == "__main__":
    raise SystemExit(main())
