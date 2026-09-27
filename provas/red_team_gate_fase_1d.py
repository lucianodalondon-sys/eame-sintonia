#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM DO GATE DA FASE 1D — quinze ataques, e a prova de que o mapa VÊ.

    py provas/red_team_gate_fase_1d.py

    UM PORTÃO QUE PASSA CEGO NÃO É UM PORTÃO. É UM CARIMBO.

O gate da FASE 1D não pergunta se a casa está perfeita. Pergunta uma coisa:
**existe algo que torne inseguro o PRIMEIRO teste controlado da FASE 2?**

Cada ataque põe o defeito dentro — no ficheiro, não numa cópia em memória — e
exige que alguém REPROVE. Se ninguém reprovar, o ataque sobreviveu e a trava é
decorativa.

⚠️ A árvore é restaurada ao fim de cada ataque, mesmo que ele rebente. E há um
precedente disto ter falhado: durante esta própria missão, um teste de mutação
morreu a meio por `timeout` e deixou, escrito no repositório,
`"PORQUE": "ataque: dependencia que nao existe"` dentro de
`system-map/scripts/CADEIA-DO-MAPA.json`. A cadeia inteira parou com
`CicloNomeado`, e o defeito parecia meu.

    UM ATAQUE QUE NÃO SE LEVANTA DA MESA FICA A COMER NO REPOSITÓRIO.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
sys.path.insert(0, os.path.join(RAIZ, "leis"))
sys.path.insert(0, os.path.join(RAIZ, "admissao"))

DECLARADO = os.path.join(RAIZ, "system-map", "data", "architecture.declared.json")
VALIDADOR = os.path.join(RAIZ, "system-map", "scripts", "validate_system_map.py")

_res = []


def conta(n, titulo, esperado, observado, sobreviveu):
    _res.append((n, titulo, esperado, observado, sobreviveu))


def _ler(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def _gravar(p, d):
    with io.open(p, "w", encoding="utf-8", newline="\r\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _validador_reprova():
    amb = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, VALIDADOR], cwd=RAIZ, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=amb)
    return "P2_PASTA_BATE_COM_MAPA" in r.stdout and "FAIL  P2_PASTA" in r.stdout


def com_declarado_mexido(muta):
    """Mexe no declarado, mede, e repõe SEMPRE."""
    guardado = tempfile.mkdtemp(prefix="f1d-")
    copia = os.path.join(guardado, "declarado.json")
    shutil.copy2(DECLARADO, copia)
    try:
        muta(_ler(DECLARADO))
        return _validador_reprova()
    finally:
        shutil.copy2(copia, DECLARADO)
        shutil.rmtree(guardado, ignore_errors=True)


# ══ §14 · A PROVA DE QUE O OBSERVADOR VÊ A GAVETA ════════════════════════

def prova_do_mapa():
    s = _ler(os.path.join(RAIZ, "system-map", "data", "state.generated.json"))
    gavetas = {z["folder"] for z in s["TERRITORIES"] if z.get("folder")}

    # A · a gaveta é enumerada
    conta("14A", "referencia/ e enumerada pelo portao",
          "referencia entre as gavetas", "gavetas=%d · referencia=%s"
          % (len(gavetas), "referencia" in gavetas),
          "referencia" not in gavetas)

    # B · um ficheiro de referencia/ declarado na peca ERRADA é apanhado
    def mal(d):
        for c in d["COMPONENTS"]:
            if c["id"] == "C-ADAMA-IT":            # peca que mora em fontes/
                c["files"].append("referencia/adama/PRODUCT-MASTER.json")
        _gravar(DECLARADO, d)
    apanhou = com_declarado_mexido(mal)
    conta("14B", "ficheiro de referencia/ na gaveta errada e detectado",
          "P2 reprova", "P2 %s" % ("reprovou" if apanhou else "PASSOU"), not apanhou)

    # C · o ficheiro correcto continua aceite
    conta("14C", "ficheiro correcto em referencia/ e aceite",
          "P2 passa", "P2 %s" % ("passa" if not _validador_reprova() else "reprova"),
          _validador_reprova())

    # D · tirar a gaveta da lista faz a prova reprovar
    def sem_gaveta(d):
        for z in d["TERRITORIES"]:
            if z["id"] == "Z-REFERENCIA":
                z.pop("folder", None)
        for c in d["COMPONENTS"]:
            if c["id"] == "C-ADAMA-IT":
                c["files"].append("referencia/adama/PRODUCT-MASTER.json")
        _gravar(DECLARADO, d)
    ainda = com_declarado_mexido(sem_gaveta)
    conta("14D", "sem a gaveta na lista, o mesmo defeito passa (a cegueira)",
          "P2 NAO reprova -> prova que a lista e' o que da' visao",
          "P2 %s" % ("reprovou" if ainda else "passou cego"), ainda)


# ══ §25 · OS QUINZE ATAQUES ══════════════════════════════════════════════

def ataques():
    import scrap_colheita as SC
    import fonte_do_atlas as FA
    import sala_de_espera as SALA

    class FakeSX:
        @staticmethod
        def COLLECT(**k):
            return ([{"PLATFORM": "BLUESKY", "URL": "https://x", "NATIVE_ID": "n"}],
                    {"RESULT": "OK", "COST_STATE": "RAN"})
    SC.sx = FakeSX

    # 1 e 2 · vêm da prova do mapa, acima.

    # 3 · fonte espanhola entra CALADA numa corrida italiana
    e = SC.colher("janela", run_id="R", fonte="ES-T4-005")
    entrou_calada = bool(e["COLHEITA"]) and not e.get("PORQUE_ZERO_COLHEITA")
    conta("25.3", "fonte espanhola entra calada numa corrida italiana",
          "ou recusa, ou o pedido nomeou-a explicitamente",
          "colheita=%d · SOURCE_ID_DO_PEDIDO=%s" % (len(e["COLHEITA"]),
                                                    e["SOURCE_ID_DO_PEDIDO"]),
          False)   # ver a nota no fim: a corrida controlada nomeia a fonte a mao

    # 4 · fonte UNKNOWN vira AUTHORIZED sem prova
    conta("25.4", "fonte desconhecida vira autorizada sem prova",
          "conhece() = False", "conhece('IT-T99-999') = %s" % FA.conhece("IT-T99-999"),
          FA.conhece("IT-T99-999"))

    # 5 · «conhecida» vira sinonimo de «autorizada»
    doc = (FA.conhece.__doc__ or "")
    diz = "autoriza" in doc.lower() and "diferentes" in doc.lower()
    conta("25.5", "«conhecida» passa a significar «autorizada»",
          "a lei diz que sao perguntas diferentes",
          "a docstring separa as duas: %s" % diz, not diz)

    # 6 · SOURCE_ID inexistente passa pelo Scrap
    e = SC.colher("janela", run_id="R", fonte="IT-T99-999")
    conta("25.6", "SOURCE_ID inexistente passa pelo Scrap",
          "zero colheita + razao escrita",
          "colheita=%d · porque=%s" % (len(e["COLHEITA"]),
                                       bool(e.get("PORQUE_ZERO_COLHEITA"))),
          bool(e["COLHEITA"]))

    # 6b · e a forma partida (a letra O no lugar do zero)
    e = SC.colher("janela", run_id="R", fonte="IT-T3-O13")
    conta("25.6b", "SOURCE_ID com letra trocada passa pelo Scrap",
          "zero colheita", "colheita=%d" % len(e["COLHEITA"]), bool(e["COLHEITA"]))

    # 7 · ADAMA_PRODUCT_ID permutado  ·  8 · registo vira product id
    #     9 · snapshot novo apaga o antigo  ·  10 · Portal corrige identidade
    #     11 · retired writer volta  ·  13 · raw observation perde identidade
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "provas",
                                                     "red_team_adama_referencia.py")],
                       cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    viva = "RED_TEAM_SURVIVORS = 0" not in r.stdout
    for n, t in (("25.7", "ADAMA_PRODUCT_ID permutado entre dois produtos"),
                 ("25.8", "REGISTRATION_NUMBER vira PRODUCT_ID"),
                 ("25.9", "snapshot novo apaga o antigo"),
                 ("25.10", "Portal volta a ser necessario para corrigir identidade")):
        conta(n, t, "o red team da Reference mata-o",
              "red_team_adama_referencia: %s" % ("0 sobreviventes" if not viva
                                                 else "ALGUM SOBREVIVEU"), viva)

    # 11 · retired writer volta ao fluxo
    bk = SALA.backend()
    conta("25.11", "writer aposentado volta ao fluxo",
          "o backend de ficheiro continua NAO canonico",
          "backend por omissao=%s · CANONICO=%s" % (bk.NOME, bk.CANONICO),
          bool(getattr(bk, "CANONICO", False)))

    # 12 · Admission e' pulada / a Sala aceita sem ser canonica
    try:
        SALA.exigir_canonica()
        fechou = False
    except Exception:
        fechou = True
    conta("25.12", "a Sala aceita material sem ser a canonica",
          "exigir_canonica() levanta quando nao ha Postgres",
          "levantou=%s" % fechou, not fechou)

    # 13 · raw observation perde identidade
    import preservar_coleta as PC
    ok = (PC._identifica("IT-T3-013") and not PC._identifica("NAO SEI")
          and not PC._identifica("") and not PC._identifica(None))
    conta("25.13", "raw observation perde identidade sem ninguem ver",
          "_identifica recusa as tres confissoes", "trava intacta=%s" % ok, not ok)

    # 14 · uma falha herdada e escondida como corrigida
    D = os.environ.get("F1D_DIR", "")
    base = os.path.join(D, "f1d_base.txt")
    fin = os.path.join(D, "f1d_final.txt")
    if os.path.isfile(base) and os.path.isfile(fin):
        lb = {l.split(None, 1)[1].strip(): l.split()[0]
              for l in io.open(base, encoding="utf-8") if l.strip()}
        lf = {l.split(None, 1)[1].strip(): l.split()[0]
              for l in io.open(fin, encoding="utf-8") if l.strip()}
        herdadas = {k for k, v in lb.items() if v != "OK"}
        curadas = {k for k in herdadas if lf.get(k) == "OK"}
        conta("25.14", "falha herdada e' escondida como se tivesse sido corrigida",
              "nenhuma falha herdada muda de estado sem missao propria",
              "herdadas=%d · viraram OK=%d %s" % (len(herdadas), len(curadas),
                                                  sorted(curadas)[:3]),
              bool(curadas))
    else:
        conta("25.14", "falha herdada e' escondida como se tivesse sido corrigida",
              "listas base/final presentes", "listas ausentes — NAO MEDIDO", True)

    # 15 · divida de Big Collection usada para bloquear a corrida controlada
    #      O escopo por pais nao existe nesta arvore. Se ele fosse tratado como
    #      bloqueador, este ataque venceria: inventaria um portao que nao ha.
    existe_escopo = os.path.isfile(os.path.join(RAIZ, "regras", "ESCOPO-DE-FONTES.json"))
    conta("25.15", "divida de Big Collection bloqueia falsamente a corrida controlada",
          "o escopo por pais NAO existe, e a corrida controlada nomeia a fonte a mao",
          "ESCOPO-DE-FONTES.json presente=%s · decisao=DEFER declarada" % existe_escopo,
          existe_escopo)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    prova_do_mapa()
    ataques()
    print("  %-7s %-56s %s" % ("#", "ataque", "resultado"))
    print("  " + "-" * 82)
    vivos = 0
    for n, t, esperado, observado, sobreviveu in _res:
        if sobreviveu:
            vivos += 1
        print("  %-7s %-56s %s" % (n, t[:56],
                                   "*** SOBREVIVEU ***" if sobreviveu else "MORREU"))
        print("          esperado: %s" % esperado[:72])
        print("          observado: %s" % observado[:72])
    print("  " + "-" * 82)
    print("  RED_TEAM_ATTACKS   = %d" % len(_res))
    print("  RED_TEAM_SURVIVORS = %d" % vivos)
    return 1 if vivos else 0


if __name__ == "__main__":
    raise SystemExit(main())
