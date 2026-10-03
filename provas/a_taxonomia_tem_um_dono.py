#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A TAXONOMIA TEM UM DONO — e esta prova recusa o dia em que tiver dois.

    python3 provas/a_taxonomia_tem_um_dono.py

O QUE SE MEDIU ANTES DESTA PROVA EXISTIR
-----------------------------------------
`T7` queria dizer tres coisas em tres ficheiros, ao mesmo tempo:

    docs/fontes/ATLAS-DE-FONTES-EAME.md     T7 = TECHNICAL NETWORK
    pedido/pedido.py::ALVOS                 T7 = «Ciencia e ensaio»
    system-map/scripts/scan_sources.py      T7 = «Ciencia e ensaio»

E `T5`, `T10`, `T11` e `T12` estavam na mesma situacao. Consequencia medida com
selecao real, e nao com um teste de texto:

    «colete ciencia da italia»  ->  IT-T7-001..012, doze COOPERATIVAS

Esta prova nao confere que a tabela esta «certa»: confere que **so existe uma**,
e que quem a consome le mesmo dela. Um alias novo nao a engana, porque ela nao
compara palavras — compara OBJECTOS.

    DUAS TABELAS PARA O MESMO CONCEITO NAO SAO UMA REDUNDANCIA:
    SAO DUAS VERDADES, E A PARTIR DAI NENHUMA DELAS VALE.
"""
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
import territorios as terr                         # noqa: E402

FALHAS = []
PASSOU = []


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


print("A TAXONOMIA TEM UM DONO")
print()

# ── 1 · O DONO LE A AUTORIDADE, E A AUTORIDADE E O ATLAS ───────────────────
atlas = os.path.join(RAIZ, terr.ATLAS)
T("o Atlas existe e e a autoridade declarada", os.path.isfile(atlas), terr.ATLAS)
T("o dono devolve os doze territorios canonicos", len(terr.CANONICOS) == 12,
  "CANONICOS=%d" % len(terr.CANONICOS))

# ── 2 · NENHUM CODIGO FICA SEM NOME, E NENHUM NOME E «OUTRO» ──────────────
sem_nome = [c for c in terr.TERRITORIOS if not terr.TERRITORIOS[c]["NOME"]]
T("nenhum territorio fica sem nome", not sem_nome, str(sem_nome))
outros = [c for c in terr.TERRITORIOS
          if terr.TERRITORIOS[c]["NOME"].strip().lower() in ("outro", "outros")]
T("nenhum territorio se chama «Outro»", not outros,
  "«Outro» apaga o nome que o Atlas deu e a divida que o codigo e: %s" % outros)

# ── 3 · A DIVIDA DIZ QUE E DIVIDA ──────────────────────────────────────────
T("T13 existe e esta declarado EM DIVIDA",
  "T13" in terr.TERRITORIOS and terr.TERRITORIOS["T13"]["ESTADO"] == "EM_DIVIDA",
  "o Atlas usa T13 em registo e nao o declara na tabela dos doze")

# ── 4 · QUEM CONSOME LE DO DONO — E ISTO COMPARA OBJECTOS, NAO PALAVRAS ───
# ⚠️ `is` E NAO `==`. Uma copia com os mesmos valores passaria num `==` e
# voltaria a divergir no dia seguinte. O que esta prova exige e que seja O
# MESMO OBJECTO — ou seja, que nao haja copia nenhuma para divergir.
sys.path.insert(0, os.path.join(RAIZ, "pedido"))
import pedido as ped                               # noqa: E402

T("pedido.APELIDOS E o dicionario do dono (nao uma copia)",
  ped.APELIDOS is terr.APELIDOS,
  "uma copia com os mesmos valores passa hoje e diverge amanha")
T("pedido.ALVOS tem exactamente os codigos do dono",
  set(ped.ALVOS) == set(terr.TERRITORIOS),
  "pedido=%s dono=%s" % (sorted(set(ped.ALVOS) - set(terr.TERRITORIOS)),
                         sorted(set(terr.TERRITORIOS) - set(ped.ALVOS))))
T("pedido.ALVOS tem exactamente os nomes do dono",
  all(ped.ALVOS[c] == terr.TERRITORIOS[c]["NOME"] for c in ped.ALVOS),
  "algum nome divergiu do Atlas")

# ── 5 · NENHUMA QUARTA TABELA NASCEU EM SILENCIO ───────────────────────────
# Procura, na arvore inteira, literais que declarem T-codigos com nome. Quem
# quiser declarar uma tabela nova tem de passar por aqui primeiro.
SUSPEITO = re.compile(r'["\']T(?:[1-9]|1[0-3])["\']\s*:\s*["\'][^"\']{3,}["\']')
PERMITIDOS = {
    os.path.join("leis", "territorios.py"),          # o dono
    os.path.join("provas", "a_taxonomia_tem_um_dono.py"),  # esta prova
}
IGNORAR_PASTAS = {".git", "node_modules", "build", "data", "research",
                  "supabase", "italia-portale", "prototype", "docs",
                  "candidatas", "handoff", "tests"}
quartas = []
for base, pastas, ficheiros in os.walk(RAIZ):
    pastas[:] = [d for d in pastas if d not in IGNORAR_PASTAS
                 and not d.startswith(".")]
    for f in ficheiros:
        if not f.endswith((".py", ".mjs", ".js")):
            continue
        rel = os.path.relpath(os.path.join(base, f), RAIZ)
        if rel in PERMITIDOS:
            continue
        try:
            with open(os.path.join(base, f), encoding="utf-8",
                      errors="replace") as fh:
                texto = fh.read()
        except OSError:
            continue
        # ⚠️ A VARREDURA LE CODIGO, E NAO PROSA.
        # A primeira versao lia o ficheiro inteiro e acendeu no COMENTARIO que
        # explicava porque aquele ficheiro NAO tem uma taxonomia — o exemplo da
        # forma errada, citado para o leitor a reconhecer, contava como tres
        # declaracoes.
        #
        #     PROIBIR A PALAVRA NAO E PROIBIR O ACTO.
        #     E UMA GUARDA QUE OBRIGA A APAGAR A EXPLICACAO
        #     COBRA O CONSERTO EM CLAREZA.
        #
        # E o mesmo conserto que `provas/nada_some_em_silencio.py` ja tinha
        # precisado de fazer, pela mesma razao, no mesmo dia.
        codigo = "\n".join(l for l in texto.splitlines()
                           if not l.lstrip().startswith(("#", "//")))
        achados = SUSPEITO.findall(codigo)
        # Duas ou mais na MESMA linha de codigo e uma tabela; uma so pode ser
        # um caso legitimo (um filtro por omissao, um exemplo). Conta-se por
        # ficheiro: tres ou mais e uma tabela, e nao um acaso.
        if len(achados) >= 3:
            quartas.append("%s (%d declaracoes)" % (rel, len(achados)))
T("nenhuma outra tabela T1..T13 com nomes vive na arvore de codigo",
  not quartas,
  "estes ficheiros declaram uma taxonomia propria: %s" % "; ".join(quartas))

# ── 6 · OS APELIDOS APONTAM PARA O QUE O ATLAS DIZ ─────────────────────────
# ⚠️ ISTO NAO E UM TESTE DE TEXTO SOBRE OS APELIDOS: e o texto do PROPRIO
# Atlas a arbitrar. Cada palavra abaixo tem de aparecer no ESCOPO do
# territorio para onde o apelido aponta. Se alguem mudar o apelido sem que o
# Atlas o sustente, isto reprova.
AMOSTRA = {
    "ciencia": ("T5", ("papers", "estudos", "trials")),
    "pesquisadores": ("T6", ("pesquisadores",)),
    "cooperativa": ("T7", ("cooperativas",)),
    "concorrentes": ("T9", ("BASF", "Bayer")),
    "preco": ("T10", ("preços", "precos", "commodities")),
    "evento": ("T11", ("feiras", "congressos")),
    "politica": ("T12", ("políticas", "politicas", "CAP")),
    "regulatorio": ("T4", ("registros", "autorizações", "autorizacoes")),
}
for palavra, (esperado, marcas) in AMOSTRA.items():
    achou = terr.do_apelido(palavra)
    escopo = (terr.TERRITORIOS.get(achou) or {}).get("ESCOPO", "")
    sustentado = any(m.lower() in escopo.lower() for m in marcas)
    T("«%s» -> %s, e o escopo do Atlas sustenta-o" % (palavra, esperado),
      achou == esperado and sustentado,
      "apontou para %r; escopo=%r" % (achou, escopo[:90]))

# ── 7 · O QUE O ATLAS CLASSIFICA CONTINUA A SER ENCONTRAVEL ───────────────
# A prova final e de SELECCAO, e nao de tabela: pedir ciencia tem de trazer
# fontes cuja ficha diz SCIENCE, e nenhuma cuja ficha diz outra coisa.
import json                                        # noqa: E402
FONTES = os.path.join(RAIZ, "system-map", "data", "sources.generated.json")
if os.path.isfile(FONTES):
    with open(FONTES, encoding="utf-8") as fh:
        S = json.load(fh)
    fontes = list(S.get("SOURCES") or []) + list(S.get("MASTER_ITALIANO") or [])
    rotulo_errado = [
        "%s: territory=%s territory_name=%r" % (s.get("source_id"),
                                                s.get("territory"),
                                                s.get("territory_name"))
        for s in fontes
        if s.get("territory")
        and s.get("territory_name")
        and s.get("territory_name") != terr.nome(s["territory"])]
    T("nenhuma ficha gerada carrega um nome de territorio que nao e o do Atlas",
      not rotulo_errado, "; ".join(rotulo_errado[:4]))

    from pedido import de_uma_frase                 # noqa: E402
    from receitas import resolver                   # noqa: E402
    plano = resolver(de_uma_frase("colete ciencia da italia"))
    ids = [f.get("source_id") for f in plano.fontes_do_assunto]
    T("«ciencia» selecciona fontes SCIENCE e nenhuma outra",
      bool(ids) and all(str(i).split("-")[1] == "T5" for i in ids if i),
      "seleccionou: %s" % ids[:14])

    plano9 = resolver(de_uma_frase("colete concorrencia da italia"))
    ids9 = [f.get("source_id") for f in plano9.fontes_do_assunto]
    T("«concorrencia» selecciona T9 e nenhuma outra",
      bool(ids9) and all(str(i).split("-")[1] == "T9" for i in ids9 if i),
      "seleccionou: %s" % ids9[:14])

    plano4 = resolver(de_uma_frase("colete regulatorio da italia"))
    ids4 = [f.get("source_id") for f in plano4.fontes_do_assunto]
    T("«regulatorio» selecciona T4 e nenhuma outra",
      bool(ids4) and all(str(i).split("-")[1] == "T4" for i in ids4 if i),
      "seleccionou: %s" % ids4[:14])

print()
print("TAXONOMY_SINGLE_OWNER = %s · %d passaram · %d falharam"
      % ("PASS" if not FALHAS else "FAIL", len(PASSOU), len(FALHAS)))
raise SystemExit(1 if FALHAS else 0)
