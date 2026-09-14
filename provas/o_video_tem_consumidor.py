#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O VIDEO TEM CONSUMIDOR? — e a rota social, existe? Medido, e nao declarado.

    python3 provas/o_video_tem_consumidor.py

A LEI QUE ESTA PROVA APLICA
---------------------------
    FILE_WRITTEN != FLOW_EXISTS.
    BOTAO EXISTE != ROTA EXISTE.

Declarar `larga_em` diz ONDE um executor larga. Nao diz que alguem VAI LA
BUSCAR. `leis/retorno_da_coleta.py` ja separa as duas coisas, e e explicito
sobre o que atravessa:

    ENTRAM_NO_INGRESSO = (COLHEITA,)
    SO A COLHEITA ATRAVESSA A PORTA. As outras leem-se.

Entao a pergunta certa nao e «o executor escreve?» — e:

    O QUE ELE ESCREVE E DECLARADO COMO COLHEITA,
    NUM SITIO QUE O ORQUESTRADOR VAI LER?

⚠️ ESTA PROVA NAO CONSERTA NADA, E ISSO E UMA ESCOLHA
------------------------------------------------------
Nesta sessao a politica de egresso responde `403 CONNECT` a todos os
hospedeiros externos, e nao ha um unico byte de video nesta arvore. Escrever
aqui a declaracao que faria o video atravessar seria encanamento que ninguem
pode exercitar — e esta casa tem nome para isso:

    CAN DO != DID DO.

Uma rota declarada e nunca corrida e exactamente o defeito que a prova de fogo
encontrou no workflow social. Repeti-lo com boas intencoes continua a ser
repeti-lo. O que esta prova faz e MEDIR e NOMEAR o bloqueio exacto.
"""
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
import retorno_da_coleta as rdc                    # noqa: E402
from receitas import EXECUTORES                    # noqa: E402

SAIDA = os.path.join(RAIZ, "system-map", "data", "rotas-reais.generated.json")

#: Onde o dono da transcricao larga o que produz. Lido do proprio dono.
DONO_DO_VIDEO = os.path.join("ferramentas", "reel_transcricao.py")

FALHAS, PASSOU = [], []
achados = {}


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def _mede(nome, valor, porque):
    achados[nome] = {"VALOR": valor, "PORQUE": porque}
    print("  %-34s = %-8s %s" % (nome, valor, porque[:70]))
    return valor


print("O VIDEO TEM CONSUMIDOR?")
print()

# ── 1 · ONDE O DONO DA TRANSCRICAO LARGA ──────────────────────────────────
fonte = io.open(os.path.join(RAIZ, DONO_DO_VIDEO), encoding="utf-8").read()
larga_declarado = "data/samples/REEL-TRANSCRICOES"
T("o dono da transcricao existe e declara onde larga",
  larga_declarado.replace("/", os.sep) in fonte.replace("/", os.sep)
  or "REEL-TRANSCRICOES" in fonte,
  "%s nao nomeia %s" % (DONO_DO_VIDEO, larga_declarado))

# ── 2 · A RECEITA DECLARA ESSE SITIO EM `larga_em`? ───────────────────────
t9 = {e["id"]: e for e in EXECUTORES.get("T9", [])}
comm = t9.get("comunicacao-publica") or {}
em_larga = larga_declarado in (comm.get("larga_em") or [])
_mede("VIDEO_LARGA_EM_DECLARADO", "YES" if em_larga else "NO",
      "a receita de `comunicacao-publica` nomeia %s em `larga_em`"
      % larga_declarado)

# ── 3 · E `retorno` — QUE E O QUE O ORQUESTRADOR LE — NOMEIA-O? ───────────
# ⚠️ ESTA E A PERGUNTA QUE SEPARA DECLARACAO DE FLUXO.
# `larga_em` e intencao. `retorno` e o que a corrida DEVOLVEU, e e dele que
# `orquestrador.a_colheita()` tira o que vai a porta.
retorno = comm.get("retorno") or {}
alvos_do_retorno = []
for especie, valor in retorno.items():
    if isinstance(valor, dict):
        alvos_do_retorno.extend(valor.keys())
    else:
        alvos_do_retorno.append(valor)
no_retorno = [c for c in alvos_do_retorno if "REEL-TRANSCRICOES" in str(c)]
_mede("VIDEO_NO_RETORNO", "YES" if no_retorno else "NO",
      "nenhum dos %d alvos declarados em `retorno` esta em REEL-TRANSCRICOES"
      % len(alvos_do_retorno) if not no_retorno else str(no_retorno))

# ── 4 · E A ESPECIE DECLARADA ATRAVESSA A PORTA? ──────────────────────────
# `LEGADO` so pode declarar SUPORTE, e SUPORTE nao atravessa — a propria
# receita escreve isso: «DECLARAR SUPORTE E INOFENSIVO MESMO QUANDO ERRADO:
# SUPORTE NAO ATRAVESSA».
especies = set()
for especie, valor in retorno.items():
    if isinstance(valor, dict):
        especies.update(valor.values())
    else:
        especies.add(especie)
atravessam = [e for e in especies if e in rdc.ENTRAM_NO_INGRESSO]
_mede("VIDEO_ESPECIE_ATRAVESSA", "YES" if atravessam else "NO",
      "as especies declaradas sao %s, e so %s atravessa a porta"
      % (sorted(especies), rdc.ENTRAM_NO_INGRESSO))

consumidor = bool(no_retorno) and bool(atravessam)
_mede("VIDEO_OUTPUT_HAS_CONSUMER", "YES" if consumidor else "NO",
      "o ficheiro e escrito e NINGUEM o le como colheita: `larga_em` diz onde, "
      "e o orquestrador le `retorno`" if not consumidor else "ha consumidor")

# ⚠️ A TRAVA. Esta prova AFIRMA o estado medido. No dia em que alguem ligar a
# rota do video, ela reprova aqui e obriga a actualizar a verdade escrita —
# que e como uma medicao deixa de apodrecer.
T("o estado do consumidor de video esta medido e declarado",
  consumidor is False,
  "o video passou a ter consumidor: actualize esta prova e o relatorio")

# ── 5 · HA BYTES DE VIDEO NESTA ARVORE? ───────────────────────────────────
videos = []
for base, pastas, ficheiros in os.walk(RAIZ):
    pastas[:] = [d for d in pastas if d not in (".git", "node_modules")]
    for f in ficheiros:
        if f.lower().endswith((".mp4", ".m4a", ".webm", ".mp3", ".wav", ".mov")):
            videos.append(os.path.relpath(os.path.join(base, f), RAIZ))
_mede("VIDEO_BYTES_NESTA_ARVORE", str(len(videos)),
      "sem bytes e sem rede, a aquisicao de video nao e exercitavel aqui")

# ── 6 · A ROTA SOCIAL — O WORKFLOW E ORFAO NESTA ARVORE? ─────────────────
print()
print("  A ROTA SOCIAL")
CHAMADOS = ("coleta/social_scrap.py", "guarda/social_guarda.py",
            "coleta/youtube_oficial.py")
faltam = [c for c in CHAMADOS if not os.path.isfile(os.path.join(RAIZ, c))]
_mede("SCRAP_SOCIAL_CODE_PRESENT", "YES" if not faltam else "NO",
      "os tres coletores que `.github/workflows/scrap-social.yml` invoca %s"
      % ("existem nesta arvore" if not faltam else "faltam: %s" % faltam))
T("o workflow social NAO e orfao nesta linha funcional", not faltam,
  "faltam %s" % faltam)

# A rota CANONICA — a que passa pelo orquestrador — existe?
scrap = t9.get("scrap-colheita") or {}
rota_canonica = (scrap.get("recebe_run_id") is True
                 and "ENVELOPE" in (scrap.get("retorno") or {}))
_mede("SOCIAL_ROTA_CANONICA", "YES" if rota_canonica else "NO",
      "`scrap-colheita` recebe a corrida do orquestrador e devolve ENVELOPE — "
      "a especie que atravessa" if rota_canonica else "nao ha rota canonica")
T("a rota social canonica existe e declara ENVELOPE", rota_canonica,
  "scrap-colheita: recebe_run_id=%s retorno=%s"
  % (scrap.get("recebe_run_id"), scrap.get("retorno")))

# ── 7 · E A AQUISICAO, NESTA SESSAO ──────────────────────────────────────
print()
print("  A AQUISICAO, NESTE AMBIENTE")
_mede("EGRESSO", "BLOCKED",
      "a politica desta sessao responde 403 CONNECT a todos os hospedeiros "
      "externos medidos (eur-lex, arpa.veneto, youtube, openalex, orcid, "
      "crossref, ipinfo). Isto e o AMBIENTE, e nao uma fonte morta.")
_mede("SOCIAL_TO_WAITING_ROOM", "BLOCKED_BY_REAL_EXTERNAL_CONDITION",
      "sem egresso nao ha janela publica para observar")
_mede("VIDEO_TO_WAITING_ROOM", "BLOCKED_BY_REAL_EXTERNAL_CONDITION",
      "sem bytes de video nesta arvore e sem egresso, e sem consumidor "
      "declarado do lado de la")

estado = {
    "O_QUE_ISTO_E": ("Se as rotas de video e social EXISTEM de facto — nao se "
                     "estao declaradas."),
    "COMO_REFAZER": "python3 provas/o_video_tem_consumidor.py",
    "A_LEI": "FILE_WRITTEN != FLOW_EXISTS · BOTAO EXISTE != ROTA EXISTE",
    "MEDIDO": achados,
    "O_BLOQUEIO_EXACTO_DO_VIDEO": (
        "`ferramentas/reel_transcricao.py` escreve em "
        "`data/samples/REEL-TRANSCRICOES`; `pedido/receitas.py` nomeia essa "
        "pasta em `larga_em`; e o `retorno` do mesmo executor declara SEIS "
        "ficheiros, NENHUM deles nessa pasta, e todos da especie LEGADO — que "
        "`leis/retorno_da_coleta.ENTRAM_NO_INGRESSO` nao deixa atravessar. O "
        "ficheiro e escrito e ninguem o le como colheita."),
    "O_QUE_FALTA_PARA_O_VIDEO_ATRAVESSAR": (
        "o dono da transcricao declarar um ENVELOPE com unidades de especie "
        "COLHEITA, e a receita nomear esse envelope em `retorno`. NAO foi "
        "escrito aqui de proposito: sem bytes de video e sem egresso, seria "
        "encanamento por exercitar — CAN DO != DID DO, que e o defeito que "
        "esta missao veio fechar e nao repetir."),
}
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with io.open(SAIDA, "w", encoding="utf-8") as f:
    json.dump(estado, f, ensure_ascii=False, indent=1)
    f.write("\n")

print()
print("  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
print()
print("ROTAS_REAIS = %s · %d passaram · %d falharam"
      % ("MEDIDO" if not FALHAS else "FALHOU", len(PASSOU), len(FALHAS)))
raise SystemExit(1 if FALHAS else 0)
