#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PORTA LE ITALIANO — positivos, negativos, ambiguos e mutacoes, sobre documento REAL.

    python3 provas/a_porta_le_italiano.py

⚠️ O QUE ESTA PROVA MEDE, E O QUE ELA RECUSA MEDIR
---------------------------------------------------
Ela NAO conta palavras do lexico. Contar palavras foi exactamente o erro que
esta casa cometeu antes: `system-map/data/recall-porta-it.generated.json`
publicava «85.7% de acerto» nos itens italianos, e a medicao que fechou este
assunto mostrou de onde vinha esse numero —

    42 dos 49 itens eram admitidos a CIENCIA por UMA palavra, `prova`,
    e ela casava dentro de «ap-PROV-al» e «ap-PROV-ing», em titulos de
    regulamento da UE escritos em INGLES.

Nenhum dos 42 era ciencia. Um lexico maior teria feito o numero subir.

    UM NUMERO QUE SOBE COM O LEXICO MEDE O LEXICO, E NAO A PORTA.

Por isso aqui julga-se DOCUMENTO REAL, preservado nesta arvore, com SHA no
ledger — e exige-se as quatro coisas que uma peneira honesta tem de fazer:

    POSITIVO    o boletim italiano de praga entra
    NEGATIVO    o documento italiano que NAO e de praga nao entra
    AMBIGUO     um unico indicio nao promove — e tambem nao rejeita
    MUTACAO     o acento nao muda a resposta; o ruido nao a inventa
"""
import io
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
import admissao as adm                             # noqa: E402

FALHAS, PASSOU = [], []
LOJA = os.path.join(RAIZ, "data", "collection-store", "italy")

#: Documentos REAIS desta arvore. Cada um tem SHA no ledger italiano.
DOCS = {
    "IT-T3-010": (LOJA + "/IT-T3-010/APOL_2026_N9_BR-COLLINA/v1_59da05274359/"
                  "Bollettino_Mosca_dellOlivo_n_9_del_07_09_2026.pdf"),
    "IT-T3-002": (LOJA + "/IT-T3-002/CAMPANIA_SA_02-09-2026/v1_0c2723e66201/"
                  "SA-02-09.pdf"),
    "IT-T3-008": (LOJA + "/IT-T3-008/ARIF_SETTIMANALE_2026_N36/v1_e612807928b5/"
                  "Notiziario_Agrometeorologico_N36_02-09-2026.pdf"),
    "IT-T2-004": (LOJA + "/IT-T2-004/SIAS_PRECIPITAZIONE_GIORNALIERA_WINDOW_END_"
                  "2026-09-05/v1_6c71cc191272/NHEOWL0530_00.html"),
    "IT-T4-001": (LOJA + "/IT-T4-001/MINSALUTE_FTS6_20260907/v1_9cd4d156369f/"
                  "PROD_FTS_6_20260907.csv"),
}


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def texto_de(caminho):
    """O texto do documento real. PDF pelo extractor da casa; o resto, bytes."""
    if not os.path.isfile(caminho):
        return None
    if caminho.lower().endswith(".pdf"):
        saida = caminho + ".prova.txt"
        try:
            subprocess.run(["pdftotext", caminho, saida],
                           capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            return None
        with io.open(saida, encoding="utf-8", errors="replace") as f:
            t = f.read()
        os.unlink(saida)
        return t
    with io.open(caminho, encoding="utf-8", errors="replace") as f:
        return f.read()


def julgar(texto, universo="T3", ident="prova"):
    """O item chega como DOCUMENTO, que e o estagio real de um derivado."""
    return adm.decidir({"id": ident, "texto": texto, "source_id": "IT-PROVA",
                        "artifact_type": "DERIVED", "parent_sha256": "a" * 64},
                       universo, corrida="prova-italiano")


print("A PORTA LE ITALIANO — regra v%s" % adm.VERSAO_DA_REGRA)
print()

textos = {k: texto_de(v) for k, v in DOCS.items()}
faltam = [k for k, v in textos.items() if not v]
T("os documentos reais estao nesta arvore e leem-se", not faltam,
  "sem estes bytes nao ha o que medir: %s" % faltam)
if faltam:
    print("\nADMISSION_FALSE_NEGATIVES_KNOWN_CASES = NAO MEDIDO")
    raise SystemExit(1)

# ── 1 · POSITIVOS — o boletim italiano de praga TEM de entrar ─────────────
print("\n  POSITIVOS")
for fonte in ("IT-T3-010", "IT-T3-002", "IT-T3-008"):
    d = julgar(textos[fonte], "T3", fonte)
    T("%s (boletim italiano de praga) -> SIM em T3" % fonte,
      d.resultado == adm.SIM,
      "deu %s · %s" % (d.resultado, d.motivo[:120]))

# ── 2 · NEGATIVOS — documento italiano que NAO e de praga nao entra ───────
print("\n  NEGATIVOS")
d = julgar(textos["IT-T2-004"], "T3", "IT-T2-004")
T("IT-T2-004 (pagina de dados de precipitacao) NAO entra em T3",
  d.resultado != adm.SIM,
  "deu SIM por %s" % str(d.evidencia.get("palavras"))[:120])

MERCADO = ("I prezzi del grano duro sulla piazza di Foggia risultano stabili "
           "rispetto alla scorsa settimana; il mercato registra volumi in "
           "lieve aumento e le esportazioni tengono.")
d = julgar(MERCADO, "T3", "mercado")
T("texto italiano de preco e mercado NAO entra em T3",
  d.resultado != adm.SIM, "deu %s" % d.resultado)

# ⚠️ UM NEGATIVO QUE EU ESCOLHI MAL, E QUE FICA REGISTADO EM VEZ DE DESAPARECER.
# `IT-T4-001` e o catalogo do Ministero della Salute: 17.696 registos de
# PRODUTOS FITOSSANITARIOS. Escolhi-o como negativo de T3 por a ficha da fonte
# dizer T4 — e a porta respondeu SIM a T3, com `fungo`, `larva`, `parassita`,
# `oidio`, `infestante`, `diserbo`, `erbicida`.
#
# A porta tem razao e eu nao tinha. Um catalogo de produtos fitossanitarios
# ENUMERA pragas, doencas e daninhas, porque e isso que cada rotulo declara
# combater. O documento fala mesmo de T3.
#
#     SOURCE TERRITORY != ITEM UNIVERSE.
#     A FICHA CLASSIFICA A FONTE. A PORTA JULGA O ITEM.
#
# E a porta decide por PAR `(item, universo)` — nunca um universo por item —
# portanto pertencer a T4 nao exclui pertencer a T3. Qual dos dois «ganha» e
# uma pergunta de PRECEDENCIA que esta casa nao respondeu, e que eu NAO vou
# inventar aqui para fazer um teste meu passar.
#
#     APERTAR A REGUA ATE ELA DAR A RESPOSTA QUE EU QUERIA
#     NAO E MEDIR: E ESCREVER O RESULTADO ANTES DA MEDICAO.
#
# Fica medido, com nome, como divida declarada.
d3 = julgar(textos["IT-T4-001"], "T3", "IT-T4-001")
d4 = julgar(textos["IT-T4-001"], "T4", "IT-T4-001")
T("IT-T4-001 (catalogo de produtos) responde SIM aos DOIS universos, e isso "
  "e o que ele e",
  d3.resultado == adm.SIM and d4.resultado == adm.SIM,
  "T3=%s T4=%s — se um deles mudar, a divida de precedencia mudou de forma"
  % (d3.resultado, d4.resultado))

# ── 3 · AMBIGUO — um indicio so nao promove, e tambem nao rejeita ─────────
print("\n  AMBIGUOS")
UM_SO = ("Il presente bollettino riporta le condizioni meteorologiche della "
         "settimana e la disponibilita idrica dei suoli. Si segnala la presenza "
         "di una malattia fogliare in un singolo appezzamento.")
d = julgar(UM_SO, "T3", "um-indicio")
T("um unico termo de T3 devolve NAO_SEI — nem SIM nem NAO",
  d.resultado == adm.NAO_SEI,
  "deu %s com %s" % (d.resultado, d.evidencia.get("palavras")))
T("e o motivo diz que e indicio, e nao ausencia",
  "indicio" in d.motivo.lower(), d.motivo[:140])

# ⚠️ O CASO QUE MAIS IMPORTA: `sintoma` (pt) vive dentro de `sintomatologia`
# (it). Sozinho, ele NAO pode promover — era assim que uma palavra portuguesa
# dentro de uma palavra italiana admitia um documento inteiro.
SUBSTRING = ("La sintomatologia osservata nelle ultime settimane risulta "
             "coerente con le previsioni stagionali del comparto.")
d = julgar(SUBSTRING, "T3", "substring")
T("«sintoma» dentro de «sintomatologia» NAO promove sozinho",
  d.resultado != adm.SIM,
  "deu SIM por %s" % str(d.evidencia.get("palavras")))

# ── 4 · MUTACOES — o acento nao muda a resposta ───────────────────────────
print("\n  MUTACOES")
COM_ACENTO = ("Si segnalano avversità delle colture e la presenza di insetti "
              "dannosi nelle trappole a feromoni installate in campo.")
SEM_ACENTO = COM_ACENTO.replace("avversità", "avversita")
a, b = julgar(COM_ACENTO, "T3", "acento"), julgar(SEM_ACENTO, "T3", "sem-acento")
T("«avversità» e «avversita» dao a MESMA resposta",
  a.resultado == b.resultado == adm.SIM,
  "com acento=%s · sem acento=%s" % (a.resultado, b.resultado))

# O texto italiano que fala de OUTRO universo continua a poder levar NAO.
OUTRO = ("Il decreto ministeriale aggiorna la registrazione e l'autorizzazione "
         "del prodotto, con la nuova etichetta pubblicata in Gazzetta Ufficiale.")
d = julgar(OUTRO, "T3", "outro-universo")
T("texto italiano claramente de T4 nao entra em T3",
  d.resultado != adm.SIM, "deu %s" % d.resultado)
T("e esse mesmo texto entra em T4", julgar(OUTRO, "T4", "t4").resultado == adm.SIM,
  "o lexico de T4 nao chegou")

# Ruido puro nao inventa pertenca.
RUIDO = "aaaa bbbb cccc dddd eeee ffff gggg hhhh iiii jjjj kkkk llll mmmm"
d = julgar(RUIDO, "T3", "ruido")
T("ruido sem palavra nenhuma devolve NAO_SEI, e nunca SIM",
  d.resultado == adm.NAO_SEI, "deu %s" % d.resultado)

# ── 5 · A REGUA NAO DEPENDE DO PORTUGUES ──────────────────────────────────
print("\n  INDEPENDENCIA DE LINGUA")
so_italiano = [p for p in adm.PERGUNTAS_DO_UNIVERSO["T3"]
               if p in ("parassita", "malattia", "insetto", "infestazione",
                        "sintomo", "avversita", "patogeno", "fitosanitario",
                        "trappola", "trappole", "infestante", "diserbo")]
T("T3 tem vocabulario italiano proprio, e nao so traducao de emergencia",
  len(so_italiano) >= 10, "so %d termos italianos" % len(so_italiano))
d = julgar(COM_ACENTO, "T3", "puro-italiano")
T("um texto SEM uma unica palavra portuguesa e reconhecido",
  d.resultado == adm.SIM, "deu %s" % d.resultado)

# ── 6 · O UNIVERSO CONTINUA A SER O CONCEITO, E NAO A FONTE ──────────────
print("\n  O CONCEITO PRESERVADO")
# ⚠️ ISTO NAO E UM DESVIO: e a lei. Um documento de uma fonte classificada T2
# pode CONTER facto de T3, e a porta julga o ITEM e nao a ficha da fonte.
#     SOURCE TERRITORY != ITEM UNIVERSE.
T("o dono da regua e um so, e as chaves dele sao as do Atlas",
  set(adm.PERGUNTAS_DO_UNIVERSO) <= set(__import__("territorios").TERRITORIOS),
  "ha chave que o dono da taxonomia nao conhece")

conhecidos = sum(1 for f in ("IT-T3-010", "IT-T3-002", "IT-T3-008")
                 if julgar(textos[f], "T3", f).resultado != adm.SIM)
print()
print("ADMISSION_FALSE_NEGATIVES_KNOWN_CASES = %d" % conhecidos)
print("T3_ITALIAN_RULE = %s · %d passaram · %d falharam"
      % ("PASS" if not FALHAS else "FAIL", len(PASSOU), len(FALHAS)))
raise SystemExit(1 if FALHAS else 0)
