# -*- coding: utf-8 -*-
"""A COLETA CONTINUA — o servico do vivo que agenda por FONTE, nao por rodada (D86, 26/09/2026).

    py ferramentas/big_collection/coleta_continua.py --um-ciclo  --base=<pasta> --sha256=<coorte congelada>
          --teto-24h=<TETO-24H.json> [--plano=<RODADAS-PLANO.json>] [--estado-rodadas=<RODADAS-ESTADO.json>]
          [--historico=a.json,b.json] [--livros-do-dia=<pasta das ondas>] [--recibos=<pasta,pasta>]
          [--max-fontes=N] [--paralelo] [--janela-24h]   (D124: a janela D79 so se ligada)
    py ferramentas/big_collection/coleta_continua.py --servico   (os mesmos) [--intervalo-min=30]
    py ferramentas/big_collection/coleta_continua.py --ensaio-a-seco (os mesmos) [--agora=<ISO>]   0 rede, 0 Sala
    py ferramentas/big_collection/coleta_continua.py --estado  --base=<pasta>
    py ferramentas/big_collection/coleta_continua.py --rearmar --base=<pasta> --porque="<quem leu e o que viu>"

Porque existe (NOITE-20260927-2023, medido): o disparador (`rodadas.py`) agrupa as fontes em RODADAS fixas e
so corre uma rodada quando TODOS os dominios dela estao livres ha 24 h (D79). Da R4 a R15 todas tem
edagricole.it: a R3 fechou e as outras 12 ficaram presas ate 28/09 20:24 — tambem as fontes delas que NAO sao
de edagricole/cia. Na pratica 1 rodada por dia. E nada relancava o disparador sozinho.

O QUE MUDA: a unidade e a FONTE. A cada ciclo escolhe-se, pela ORDEM DO PLANO (a justa/rendimento que o
`rodadas.planear` ja fez: rodada 1 primeiro, T5 no fim), as fontes cujos dominios estao TODOS livres:
  · D79 (so com --janela-24h; D124 desligou-a por omissao, como em `rodadas.py`): nenhum pedido ao dominio
    nas ultimas 24 h (livros das ondas + recibos: `rodadas.ultima_visita_por_dominio`);
  · D90/D124: o livro da cortesia adaptativa (`coleta/cortesia_adaptativa.py`, o contador multicanal de 24 h
    agora adaptativo) tem lugar para os pedidos previstos no ORCAMENTO VIGENTE do dominio, e o dominio nao
    esta em pausa de 24 h nem em Retry-After;
  · somando TODAS as linhas do ciclo e o gasto de 24 h, nenhum dominio passa do orcamento vigente.
Fonte de dominio fechado ESPERA (com a hora em que abre); as outras seguem. O FREIO NAO MUDA.

D124-REBASE (verificador independente, 28/09): este ficheiro usava `rodadas.TETO` e `reserva_24h._ler/gasto/
ate_quando`, que a D124 removeu — `import coleta_continua` rebentava e a tarefa SINTONIA-COLETA-CONTINUA
parava. Agora o teto de cada dominio e o da politica (ou SINTONIA_TETO_POR_HOST, manual); o livro de 24 h e o
da cortesia, e o livro ANTIGO ({"RESERVAS": [...]}, `--teto-24h=%SI%\TETO-24H.json`) le-se e migra-se sozinho
(`cortesia_adaptativa.migrar_livro_antigo`). A linha SITES prova-se LIGADA pelo COMPORTAMENTO do transporte
(`sonda_ligacao_sites.mjs`: sem reserva o pedido nao sai), nunca por um texto no ficheiro.

O QUE NAO MUDA (reuso, nada de coletor novo): cada linha corre numa onda propria pelo MESMO
`onda_web.py --correr --fontes=... --saida=<base>/CICLO-NNNN/<LINHA>` (`rodadas.onda_real`), entre o MESMO
portao de egresso IT antes/depois (`rodadas.portao_real`), fechada pela MESMA PROVA-TETO independente
(`provas/prova_teto_dominio.py`, sobre `runs.ndjson`) — aqui sobre TODAS as corridas do ciclo juntas E sobre
as das ultimas 24 h do servico — com o relatorio do runbook (`rodadas.relatorio_real`) e a reconciliacao da
Sala do roteiro (passo 8: `collection_run`/`raw_asset`/`sala_de_espera` destas corridas, so SELECT).

O ROBO (o supervisor do Source Curator): so se para quando HA fontes a correr (quando se vai gravar na Sala):
`curadoria/PARAR.flag`, confirma no SO que parou, e no fim — corra bem ou mal — tira a flag e relanca-o,
confirmando no SO que voltou. Se a flag ja la estava (outro a parou), nao se toca nela. Sem fontes elegiveis,
o robo nao e tocado.

PARA SOZINHO (e fica PARADO ate `--rearmar`): RAM livre < 5 GB (a regra da LOCK-PESADO) ou NAO SEI a RAM ·
portao IT falha (antes ou depois) · backup da Sala sem PROVA_VALE · PROVA-TETO FAIL ou NAO_SEI · livro de
24 h ilegivel · onda com codigo != 0 ou disjuntor · reconciliacao da Sala que nao bate (ou NAO SEI) · o robo
nao parou / nao voltou · o portao da Collection nao responde. `<base>/PARAR-COLETA.flag` desliga-o sem erro (e o
interruptor do coordenador).

ADENDO-PARADA (01/10, medido no ciclo 146): o agendador so oferece a onda a fonte que o portao da Collection
admite AGORA (`collection_gate.avaliar`, o mesmo que a onda usa); a recusada ESPERA com PORQUE=FONTE_NAO_READY e o
estado lido. E um ciclo SEM corrida e SEM pedido (estado da onda gravado, nenhuma fonte CORREU, livro da onda a 0)
nao tem nada a provar: PROVA_TETO_CICLO=NADA_A_PROVAR e o servico segue. Com uma corrida, um pedido ou uma duvida
que seja, a prova corre como antes e para.

O LIVRO DE CICLOS (`<base>/CICLOS.ndjson`), uma linha por ciclo: quando, por linha as fontes, os pedidos,
os documentos novos, a Sala antes/depois, as que esperam e o proximo dominio a abrir.

AS LINHAS (D86-b/c): cada uma com o seu contador; TODAS partilham o orcamento do dominio no ciclo e o livro
de 24 h. So corre uma linha LIGADA ao contador multicanal (a chamada de reserva medida no transporte dela);
as outras ficam ESPERA_LIGACAO, com o ficheiro onde falta a linha (CONTADOR-24H.md). A ordem das linhas roda
de ciclo para ciclo. `--paralelo` corre as ondas das linhas ao mesmo tempo (o orcamento ja foi repartido, e
o livro de 24 h reserva cada pedido sob trinco).

    O AGENDADOR ESCOLHE; O TRANSPORTE CORTA; A PROVA CONFERE. TRES DONOS, NENHUM CONFIA NO OUTRO.
"""
from __future__ import annotations

import json
import os
import secrets
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "coleta"))
import rodadas as R                                                # noqa: E402 — plano, janela, portao, onda, prova
import reserva_24h as R24                                          # noqa: E402 — o contador multicanal (D90)
import cortesia_adaptativa as CA                                   # noqa: E402 — o dono unico do teto (D124)

PT = R.PT
SONDA_SITES = AQUI / "sonda_ligacao_sites.mjs"
RAM_MINIMA_GB = 5.0                                                # a regra da LOCK-PESADO: >= 5 GB livres
ESTADO_F = "COLETA-CONTINUA-ESTADO.json"
CICLOS_F = "CICLOS.ndjson"
DESLIGAR_F = "PARAR-COLETA.flag"
TRINCO_F = "COLETA-CONTINUA.trinco"

# ── as linhas (D86-b): o transporte de cada uma e a CHAMADA que prova que ela reserva no livro de 24 h ─
# LIGADA e MEDIDA no codigo (a chamada existe no ficheiro), nunca declarada. Sem ela, a linha NAO corre:
# «ate cada linha estar ligada a este livro, so UMA linha de rede de cada vez» (CONTADOR-24H.md).
# D124-REBASE: a SITES tem SONDA — a ligacao mede-se pelo que o transporte FAZ (contra um servidor local,
# sem rede), e nao pelo texto da chamada: a D124 mudou `reservar24h(host, 1)` para `reservar24h(host, 1, {...})`
# e o texto deixava a linha em ESPERA_LIGACAO com o transporte ligado (verificador independente, 28/09).
# FEEDER-4-LINHAS (01/10): "ONDA" = a linha tem onda no ciclo. So a SITES tem: `pecas["onda"]` e
# `onda_web.py --correr`, que so aceita a coorte congelada. Linha sem ONDA nunca la vai (BLOQUEADA_CAPACIDADE).
LINHAS = [
    {"LINHA": "SITES", "FAMILIA": "sites e boletins (T2/T3/T5/T7/T8/T9/T10/T12), pela coorte congelada",
     "TRANSPORTE": "coleta/italy_pilot_collect.mjs", "SONDA": "ferramentas/big_collection/sonda_ligacao_sites.mjs",
     "ONDA": "ferramentas/big_collection/onda_web.py --correr (so a coorte congelada)"},
    # LIGACAO-4-LINHAS (30/09): as quatro linhas Python deixaram de ser medidas por TEXTO. O texto mentia nos
    # dois sentidos: a BUSCA e a SOCIAL reservam no MESMO livro por outra porta (scrap_http -> teto_da_onda ->
    # cortesia_adaptativa) e ficavam ESPERA_LIGACAO; e o inverso (o texto la, a chamada morta) tambem passava.
    # Agora mede-se o COMPORTAMENTO, como a D124 ja fazia para a SITES: o transporte corre contra um livro
    # temporario e um egresso fechado; LIGADA = escreveu a RESERVA antes do pedido E nao reserva com o dominio
    # pausado. A CIENCIA e a PESQUISADORES ganharam a reserva que nao tinham (coleta/pesquisadores_t6.py,
    # ferramentas/seguir_pesquisadores/seguir.py) — no MESMO livro, sem segundo contador.
    {"LINHA": "BUSCA", "FAMILIA": "paginas de busca (linha_busca)",
     "TRANSPORTE": "coleta/linha_busca.py", "SONDA_PY": "ferramentas/big_collection/sonda_ligacao_linha.py"},
    {"LINHA": "CIENCIA", "FAMILIA": "APIs cientificas OpenAlex/Crossref/ORCID (excecao de robots D91)",
     "TRANSPORTE": "coleta/pesquisadores_t6.py", "SONDA_PY": "ferramentas/big_collection/sonda_ligacao_linha.py"},
    {"LINHA": "SOCIAL", "FAMILIA": "YouTube/social (so o que o freio social ja libera)",
     "TRANSPORTE": "coleta/teto_da_onda.py", "SONDA_PY": "ferramentas/big_collection/sonda_ligacao_linha.py"},
    {"LINHA": "PESQUISADORES", "FAMILIA": "paginas de pesquisadores T6",
     "TRANSPORTE": "ferramentas/seguir_pesquisadores/seguir.py",
     "SONDA_PY": "ferramentas/big_collection/sonda_ligacao_linha.py"},
]


def agora_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sondar_ligacao(linha: dict, raiz: Path = RAIZ, timeout_s: float = 120.0) -> dict:
    """A SONDA do transporte (so para linhas com "SONDA"): corre-o contra um servidor LOCAL com um livro da
    cortesia temporario e mede. {"LIGADA": bool, "PORQUE": texto, "MEDIDO": {...}}. Falha da sonda = NAO LIGADA."""
    sonda, transporte = raiz / linha["SONDA"], raiz / linha["TRANSPORTE"]
    try:
        r = subprocess.run(["node", str(sonda), "--transporte=" + str(transporte)], cwd=raiz, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=timeout_s,
                           env={k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")})
        ultima = (r.stdout.strip().splitlines() or [""])[-1]
        m = json.loads(ultima)
    except (OSError, ValueError, subprocess.TimeoutExpired) as ex:
        return {"LIGADA": False, "PORQUE": "SONDA_NAO_CORREU: %s: %s" % (linha["SONDA"], str(ex)[:200])}
    if not isinstance(m, dict) or m.get("LIGADA") is not True:
        return {"LIGADA": False, "PORQUE": "SONDA: %s" % (m.get("PORQUE") if isinstance(m, dict) else m),
                "MEDIDO": m.get("MEDIDO") if isinstance(m, dict) else None}
    return {"LIGADA": True, "PORQUE": "SONDA: %s" % m.get("PORQUE"), "MEDIDO": m.get("MEDIDO")}


def sondar_ligacao_py(linha: dict, raiz: Path = RAIZ, timeout_s: float = 180.0) -> dict:
    """A SONDA de comportamento de uma linha Python (LIGACAO-4-LINHAS, 30/09): o transporte corre contra um
    egresso FECHADO e um livro da cortesia TEMPORARIO (dentro da sonda), e mede-se o livro — nao o texto.
    {"LIGADA": bool, "PORQUE": texto, "MEDIDO": {...}}. Sonda que nao corre = NAO LIGADA."""
    sonda = raiz / linha["SONDA_PY"]
    try:
        r = subprocess.run([sys.executable, str(sonda), "--linha=" + linha["LINHA"]], cwd=raiz,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout_s,
                           env={k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")})
        ultima = (r.stdout.strip().splitlines() or [""])[-1]
        m = json.loads(ultima)
    except (OSError, ValueError, subprocess.TimeoutExpired) as ex:
        return {"LIGADA": False, "PORQUE": "SONDA_NAO_CORREU: %s: %s" % (linha["SONDA_PY"], str(ex)[:200])}
    if not isinstance(m, dict) or m.get("LIGADA") is not True:
        return {"LIGADA": False, "PORQUE": "SONDA: %s" % (m.get("PORQUE") if isinstance(m, dict) else m),
                "MEDIDO": m.get("MEDIDO") if isinstance(m, dict) else None}
    return {"LIGADA": True, "PORQUE": "SONDA: %s" % m.get("PORQUE"), "MEDIDO": m.get("MEDIDO")}


def medir_ligacao(linha: dict, raiz: Path = RAIZ) -> dict:
    """{"LIGADA": bool, "PORQUE": texto}: o transporte da linha existe E reserva no livro de 24 h.
    Com "SONDA"/"SONDA_PY": medido pelo comportamento. Sem ela: a chamada tem de estar no codigo (medida de texto)."""
    f = raiz / linha["TRANSPORTE"]
    if not f.exists():
        return {"LIGADA": False, "PORQUE": "TRANSPORTE_NAO_EXISTE_NESTA_ARVORE: %s" % linha["TRANSPORTE"]}
    if linha.get("SONDA"):
        return sondar_ligacao(linha, raiz)
    if linha.get("SONDA_PY"):
        return sondar_ligacao_py(linha, raiz)
    if linha["CHAMADA"] not in f.read_text(encoding="utf-8", errors="replace"):
        return {"LIGADA": False, "PORQUE": "SEM_RESERVA_24H: %s nao chama %s (CONTADOR-24H.md)"
                % (linha["TRANSPORTE"], linha["CHAMADA"])}
    return {"LIGADA": True, "PORQUE": "%s chama %s" % (linha["TRANSPORTE"], linha["CHAMADA"])}


def ordem_das_linhas(nomes: list, n_ciclo: int) -> list:
    """O rodizio (D86-b): a linha que abre o ciclo muda a cada ciclo."""
    if not nomes:
        return []
    k = n_ciclo % len(nomes)
    return list(nomes[k:]) + list(nomes[:k])


# ── 1. as candidatas: o plano JA ORDENADO (justa/rendimento), achatado ────────
def candidatas_do_plano(plano: dict, linha: str = "SITES") -> list:
    out = []
    for r in plano.get("RODADAS", []):
        for f in r["FONTES"]:
            out.append({"SOURCE_ID": f["SOURCE_ID"], "DOMINIO": f["DOMINIO"], "PREVISTOS": int(f["PREVISTOS"]),
                        "DOMINIOS": list(f.get("DOMINIOS") or [PT.dominio_registavel(f["DOMINIO"])]),
                        "RODADA_DO_PLANO": r["RODADA"], "CLASSE_PRIORIDADE": f.get("CLASSE_PRIORIDADE"),
                        "LINHA": linha})
    return out


# ── 1b. o alimentador por linha (FEEDER-4-LINHAS, 01/10) ─────────────────────
# Medido nos ciclos 127-135: `main` dava [] as quatro linhas Python e elas saiam NADA_ELEGIVEL com FONTES=[] —
# rota em falta a passar por zero real. Agora cada linha le o catalogo GOVERNADO que ja existe nesta arvore
# (nada de fonte inventada nem catalogo novo) e, se nao pode correr, diz PORQUE com nome proprio.
# NADA_ELEGIVEL fica so para "ha fontes e nenhuma cabe agora" (cadencia/teto). A ordem e a precedencia:
# o primeiro motivo que se aplica da o ESTADO; os outros ficam em MOTIVOS.
ESTADOS_DE_BLOQUEIO = ("SEM_CATALOGO", "BLOQUEADA_POLITICA", "BLOQUEADA_ROBOTS", "BLOQUEADA_PERMISSAO_SOCIAL",
                       "BLOQUEADA_CAPACIDADE")
SEM_ONDA = ("a coleta continua so tem a onda dos SITES (onda_web.py --correr), que so aceita a coorte congelada: "
            "uma fonte desta linha la dentro e FONTE_FORA_DA_COORTE, a onda sai != 0 e o servico PARA")


def _json(raiz: Path, rel: str):
    return json.loads((raiz / rel).read_text(encoding="utf-8"))


def _catalogo_busca(raiz: Path) -> dict:
    rel = "data/derivados/LINHA-BUSCA/CONSULTAS.json"                  # o que `linha_busca.py --plano` gera (D93)
    n = len(_json(raiz, rel))
    return {"CATALOGO": rel, "UNIDADE": "consulta (assunto-primeiro, D93)", "UNIDADES_GOVERNADAS": n, "MOTIVOS": [],
            "COMO_CORRE": "por CONSULTA (linha_busca.py --buscar/--colher --autorizado, o coordenador)"}


def _catalogo_ciencia(raiz: Path) -> dict:
    rel, contrato = "data/derivados/PESQUISADORES-T6/PLANO.json", "docs/fontes/CONTRATO-FONTE-T6-PESQUISADOR-V1.json"
    n = len(_json(raiz, rel).get("CONSULTAS") or [])
    estado = str(_json(raiz, contrato).get("ESTADO") or "")
    m = [] if estado.upper().startswith("INSTALADO") else [
        ("BLOQUEADA_POLITICA", "o contrato da fonte T6 nao esta instalado (%s: ESTADO=%r)" % (contrato, estado))]
    return {"CATALOGO": rel, "UNIDADE": "par cultura x problema (consulta OpenAlex; pesquisadores_t6.py)",
            "UNIDADES_GOVERNADAS": n, "MOTIVOS": m,
            "COMO_CORRE": "por RODADA sobre o seu ESTADO.json (pesquisadores_t6.py --rede --rodada=N)"}


def _catalogo_social(raiz: Path) -> dict:
    # T9 SOCIAL-CATALOGO-AUTORIZADO (01/10): a porta (`plano_onda_social.triagem_social`) aceita so o contrato com
    # rastro, dentro do ambito, e diz o MOTIVO de cada recusa. O estado vem do livro do ciclo de vida DESTA raiz.
    rel, coorte = "curadoria/italy_contracts_curator.json", "ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json"
    sys.path.insert(0, str(raiz / "curadoria"))
    import plano_onda_social as POS                                    # noqa: PLC0415 — a regra da porta social
    import lifecycle as LC                                             # noqa: PLC0415
    contratos = {c["SOURCE_ID"]: c for c in _json(raiz, rel)["FONTES"]}
    livro: dict = {}

    def estado_de(s):
        if not livro:
            f = raiz / "curadoria" / "LIFECYCLE-LEDGER-V1.json"
            livro.update(json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"TRANSICOES": []})
        return LC.estado_de(s, livro)
    tri = POS.triagem_social(contratos, estado_de=estado_de)
    sociais = tri["ACEITES"]
    por_motivo: dict = {}
    for r in tri["RECUSADAS"]:
        por_motivo.setdefault(r["MOTIVO"], []).append(r["SOURCE_ID"])
    ready = ((_json(raiz, coorte).get("PLANO") or {}).get("PAINEL_DO_GATE") or {}).get("READY_SOCIAL_TOTAL")
    m = [] if sociais else [
        ("SEM_CATALOGO", "0 fontes aceites na porta social (plano_onda_social.triagem_social) em %s: %d recusadas "
                         "com motivo (%s); %d contratos nao sociais" % (
                             rel, len(tri["RECUSADAS"]),
                             ", ".join("%s=%d" % (k, len(v)) for k, v in sorted(por_motivo.items())) or "nenhuma",
                             tri["NAO_SOCIAIS"]))]
    return {"CATALOGO": rel, "UNIDADE": "fonte social aceite na porta (rastro + ambito do T9)",
            "UNIDADES_GOVERNADAS": len(sociais),
            "PORTA_SOCIAL": {"ACEITES": sociais, "RECUSADAS": dict(sorted(por_motivo.items())),
                             "POR_PLATAFORMA": tri["POR_PLATAFORMA"]},
            "MOTIVOS": m + [
                ("BLOQUEADA_PERMISSAO_SOCIAL", "correr fontes sociais exige --autorizado-pelo-dono "
                                               "(ferramentas/maestro_social/maestro_social.py); a coorte declara "
                                               "READY_SOCIAL_TOTAL=%s (%s)" % (ready, coorte))],
            "COMO_CORRE": "pelo maestro_social (--correr --autorizado-pelo-dono --fontes=)"}


def _catalogo_pesquisadores(raiz: Path) -> dict:
    rel = "data/derivados/LISTA-MESTRA/CRUZAMENTO-MUR-AGRI05.json"     # a identidade MUR que pessoas.py segue (D85)
    lista = _json(raiz, rel).get("LISTA") or []
    n = sum(1 for p in lista if isinstance(p.get("ORCID"), list) and len(p["ORCID"]) == 1)
    return {"CATALOGO": rel, "UNIDADE": "pessoa MUR AGRI-05 com UM ORCID (seguir.py/orcid_lote.py)",
            "UNIDADES_GOVERNADAS": n, "MOTIVOS": [
                ("BLOQUEADA_ROBOTS", "robots.txt de pub.orcid.org = 'User-agent: * / Disallow: /' (lido a 26/09 "
                                     "22:58Z; ferramentas/seguir_pesquisadores/SEGUIR-PESQUISADORES.md; o canario do "
                                     "orcid_lote.py PARA por ROBOTS). Declarado, nao re-medido aqui (0 rede)")],
            "COMO_CORRE": "por LOTE de pessoas (orcid_lote.py --autorizado; seguir.py --rodada SUBSTITUIDO, D90 3.4)"}


CATALOGOS = {"BUSCA": _catalogo_busca, "CIENCIA": _catalogo_ciencia, "SOCIAL": _catalogo_social,
             "PESQUISADORES": _catalogo_pesquisadores}


def alimentar_linhas(plano: dict, raiz: Path = RAIZ) -> dict:
    """{linha: {"CANDIDATAS": [...], "ESTADO": None | um de ESTADOS_DE_BLOQUEIO, "PORQUE", "CATALOGO",
    "UNIDADE", "UNIDADES_GOVERNADAS", "MOTIVOS"}}. So leitura, 0 rede. So recebe CANDIDATAS a linha com ONDA no
    ciclo (hoje a SITES, pelo plano); as outras dizem o que o catalogo delas tem e porque nao correm."""
    out = {}
    for l in LINHAS:
        nome = l["LINHA"]
        if nome == "SITES":
            c = candidatas_do_plano(plano)
            out[nome] = {"CANDIDATAS": c, "ESTADO": None, "PORQUE": None, "CATALOGO": "RODADAS-PLANO (--plano)",
                         "UNIDADE": "fonte da coorte congelada", "UNIDADES_GOVERNADAS": len(c), "MOTIVOS": []}
            continue
        try:
            f = CATALOGOS[nome](raiz) if nome in CATALOGOS else {"CATALOGO": None, "MOTIVOS": [
                ("SEM_CATALOGO", "nenhum catalogo governado declarado para a linha %s" % nome)]}
        except (OSError, ValueError, KeyError, TypeError, AttributeError, ImportError) as ex:
            f = {"CATALOGO": None, "MOTIVOS": [("SEM_CATALOGO", "catalogo ilegivel: %s" % str(ex)[:200])]}
        motivos = list(f["MOTIVOS"])
        if not l.get("ONDA"):
            motivos.append(("BLOQUEADA_CAPACIDADE", SEM_ONDA + ("; o transporte da linha corre " + f["COMO_CORRE"]
                                                                if f.get("COMO_CORRE") else "")))
        motivos = [{"ESTADO": e, "PORQUE": p} for e, p in sorted(motivos, key=lambda m: ESTADOS_DE_BLOQUEIO.index(m[0]))]
        out[nome] = {"CANDIDATAS": [], "ESTADO": motivos[0]["ESTADO"] if motivos else None,
                     "PORQUE": motivos[0]["PORQUE"] if motivos else None,
                     "CATALOGO": f.get("CATALOGO"), "UNIDADE": f.get("UNIDADE"),
                     "UNIDADES_GOVERNADAS": f.get("UNIDADES_GOVERNADAS", 0), "MOTIVOS": motivos}
        if "PORTA_SOCIAL" in f:                                        # T9: o porque de cada recusa vai ao ciclo
            out[nome]["PORTA_SOCIAL"] = f["PORTA_SOCIAL"]
    return out


def feitas_das_rodadas(estado_rodadas: dict) -> list:
    """O que o disparador por rodada JA correu (FEITAS de cada rodada, e as FONTES das FECHADAS)."""
    out = []
    for reg in (estado_rodadas or {}).get("RODADAS", {}).values():
        for s in list(reg.get("FEITAS") or []) + (list(reg.get("FONTES") or []) if reg.get("ESTADO") == "FECHADA" else []):
            if s not in out:
                out.append(s)
    return out


# ── 2. o livro de 24 h (so leitura; ilegivel = NAO SEI) ─────────────────────
def reservas_24h(livro: Path | None) -> list:
    """Os EVENTOS do livro da cortesia (D124; o livro antigo D90 {"RESERVAS": [...]} le-se convertido).
    Ausente = []; ilegivel levanta (LivroIlegivel e ValueError: quem chama PARA)."""
    if livro is None:
        raise ValueError("SEM_LIVRO_24H: a coleta continua exige --teto-24h (D90: todas as linhas partilham)")
    return CA.ler_eventos(Path(livro))


def teto_manual() -> int | None:
    """SINTONIA_TETO_POR_HOST: o teto MANUAL declarado pelo operador (o mesmo nome do transporte)."""
    v = os.environ.get("SINTONIA_TETO_POR_HOST")
    return int(v) if v else None


def quando_cabem(eventos: list, dom: str, p: int, nivel: int, agora: float) -> float:
    """O primeiro instante em que `p` pedidos cabem em `nivel` (vao saindo as reservas mais antigas da
    janela). `p` maior que o nivel: nunca cabe neste nivel — daqui a uma janela (o nivel pode mudar)."""
    J = float(CA.politica()["JANELA_S"])
    vivas = sorted(float(e["EM"]) for e in eventos
                   if e["TIPO"] == "RESERVA" and e["DOMINIO"] == dom and float(e["EM"]) > agora - J)
    k = len(vivas) + p - nivel
    if k <= 0:
        return agora
    if p > nivel or k > len(vivas):
        return agora + J
    return vivas[k - 1] + J


# ── 3. escolher: PURO ─────────────────────────────────────────────────────────
def escolher(candidatas: list, *, feitas, ultima: dict, reservas: list, agora_utc: datetime,
             orcamento: dict, teto: int | None = None, janela_h: int | None = 24,
             max_fontes: int | None = None) -> dict:
    """{"CORREM": [...], "ESPERAM": [...]}. `orcamento` (dominio -> previstos neste ciclo) e PARTILHADO entre
    as linhas do ciclo: e mutado aqui. Uma fonte so corre se TODOS os seus dominios estao livres.
    `reservas`: os EVENTOS do livro da cortesia. `teto`: None = o orcamento vigente de cada dominio (D124), ou
    SINTONIA_TETO_POR_HOST; int = teto manual. `janela_h`: None = sem a janela D79."""
    t = agora_utc.timestamp()
    teto = teto if teto is not None else teto_manual()
    pol = CA.politica()
    correm, esperam = [], []
    feitas = set(feitas)
    for c in candidatas:
        if c["SOURCE_ID"] in feitas:
            continue
        p = int(c["PREVISTOS"])
        fechados = {}
        for d in c["DOMINIOS"]:
            v = ultima.get(d)
            if janela_h and v and agora_utc < v + timedelta(hours=janela_h):     # D79 (so se ligada)
                fechados[d] = {"PORQUE": "JANELA_24H", "ABRE_EM": (v + timedelta(hours=janela_h)).isoformat(timespec="seconds")}
                continue
            dd = CA.dominio(d)
            e = CA.dobrar_eventos(reservas, dd, t, pol)                          # D90/D124: o livro da cortesia
            nivel = teto if teto is not None else e["ORCAMENTO_24H"]
            g = e["GASTO_24H"]
            bloq = max(e["PAUSADO_ATE"] or 0, e["RETRY_ATE"] or 0)
            if bloq > t:                                                         # D124: o site pediu para esperar
                fechados[d] = {"PORQUE": "PAUSA_24H" if (e["PAUSADO_ATE"] or 0) >= bloq else "RETRY_AFTER",
                               "SITUACAO": e["SITUACAO"], "ABRE_EM": datetime.fromtimestamp(bloq, timezone.utc)
                               .isoformat(timespec="seconds")}
                continue
            if g + p > nivel:
                fechados[d] = {"PORQUE": "TETO_24H", "GASTO_24H": g, "ORCAMENTO_24H": nivel,
                               "ABRE_EM": datetime.fromtimestamp(quando_cabem(reservas, dd, p, nivel, t),
                                                                 timezone.utc).isoformat(timespec="seconds")}
                continue
            if g + orcamento.get(dd, 0) + p > nivel:                             # somando as linhas do ciclo
                fechados[d] = {"PORQUE": "TETO_NO_CICLO", "NO_CICLO": orcamento.get(dd, 0), "ORCAMENTO_24H": nivel,
                               "ABRE_EM": (agora_utc + timedelta(hours=janela_h or 24)).isoformat(timespec="seconds")}
        if not fechados and max_fontes is not None and len(correm) >= max_fontes:
            esperam.append(dict(c, PORQUE="MAX_FONTES_NO_CICLO", ABRE_EM=None))
            continue
        if fechados:
            esperam.append(dict(c, PORQUE="DOMINIO_FECHADO", DOMINIOS_FECHADOS=fechados,
                                ABRE_EM=max(x["ABRE_EM"] for x in fechados.values())))
            continue
        correm.append(c)
        for d in {CA.dominio(x) for x in c["DOMINIOS"]}:
            orcamento[d] = orcamento.get(d, 0) + p
    return {"CORREM": correm, "ESPERAM": esperam}


def proximo_a_abrir(esperam: list) -> dict | None:
    """O proximo dominio fechado a abrir, e quantas fontes ele solta."""
    abre = {}
    for e in esperam:
        for d, x in (e.get("DOMINIOS_FECHADOS") or {}).items():
            abre.setdefault(d, [x["ABRE_EM"], 0])
            abre[d][1] += 1
    if not abre:
        return None
    d, (quando, n) = min(abre.items(), key=lambda kv: kv[1][0])
    return {"DOMINIO": d, "ABRE_EM": quando, "FONTES_A_ESPERA": n}


# ── 4. as pecas de fora (injectaveis: os testes trocam-nas; o CLI usa estas) ─
def ram_livre_gb_real() -> float | None:
    """GB de RAM livre, do SO. None = NAO SEI (e o servico PARA)."""
    try:
        if os.name == "nt":
            import ctypes

            class _M(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = _M()
            m.dwLength = ctypes.sizeof(_M)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                return None
            return m.ullAvailPhys / 2 ** 30
        for l in Path("/proc/meminfo").read_text().splitlines():
            if l.startswith("MemAvailable:"):
                return int(l.split()[1]) / 2 ** 20
    except Exception:                                                  # noqa: BLE001
        return None
    return None


def backup_real(pasta: Path) -> dict:
    """`provar_backup_da_sala.py` (o passo 2 do roteiro). So PROVA_VALE=true deixa gravar."""
    pasta.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "micro_coleta" / "provar_backup_da_sala.py"),
                        "--saida=" + str(pasta)], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=3600)
    f = pasta / "PROVA-BACKUP-SALA.json"
    d = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    return {"PROVA_VALE": d.get("PROVA_VALE") is True and r.returncode == 0, "CODIGO": r.returncode,
            "DUMP": d.get("DUMP"), "SALA_REAL_ANTES": d.get("SALA_REAL_ANTES"),
            # o motivo fica no registo: um PARA sem causa obriga a rearmar as cegas
            "PROVA_SAIDA": (r.stdout or "")[-400:], "PROVA_ERRO": (r.stderr or "")[-400:]}


def _supervisor():
    sys.path.insert(0, str(RAIZ / "curadoria"))
    import supervisor as S                                             # noqa: E402 — o dono do robo
    return S


class RoboReal:
    """O robo de fontes (curadoria/supervisor.py). A vida vem do SO (`ler_estado_servico`), nunca do ficheiro."""

    ESPERA_S = 120

    def estado(self) -> dict:
        s = _supervisor().ler_estado_servico()
        nao_sei = s.get("PID_CHECK_NAO_SEI") or []
        return {"VIVO": None if nao_sei else bool(s.get("SUPERVISOR_ALIVE") or s.get("WORKER_ALIVE")),
                "FLAG": _supervisor().PARAR.exists(), "SUPERVISOR_STATE": s.get("SUPERVISOR_STATE")}

    def parar(self) -> None:
        _supervisor().PARAR.write_text("COLETA-CONTINUA %s: a gravar na Sala" % agora_iso(), encoding="utf-8")

    def tirar_flag(self) -> None:
        _supervisor().PARAR.unlink(missing_ok=True)

    def lancar(self) -> None:
        kw = {"cwd": RAIZ, "stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        if os.name == "nt":
            kw["creationflags"] = 0x00000008 | 0x00000200                # DETACHED_PROCESS | NEW_PROCESS_GROUP
        else:
            kw["start_new_session"] = True
        subprocess.Popen([sys.executable, str(RAIZ / "curadoria" / "supervisor.py")], **kw)

    def esperar(self, vivo: bool) -> bool:
        fim = time.monotonic() + self.ESPERA_S
        while time.monotonic() < fim:
            if self.estado()["VIVO"] is vivo:
                return True
            time.sleep(3)
        return False


def reconciliar_real(run_ids: list, sala_antes: dict | None, sala_depois: dict | None) -> dict:
    """O passo 8 do roteiro, so SELECT: as linhas das corridas do ciclo contra o delta da Sala."""
    sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
    import micro_coleta as MC                                          # noqa: E402
    if not run_ids:
        return {"ESTADO": "PASS", "NOTA": "nenhuma corrida", "DOCS_NOVOS": 0}
    ids = ",".join("'%s'" % r.replace("'", "") for r in run_ids)
    try:
        n = {t: int(MC.sql("select count(*) from %s where run_id in (%s)" % (t, ids))[0][0])
             for t in ("collection_run", "raw_asset", "sala_de_espera")}
    except Exception as ex:                                            # noqa: BLE001 — sem medida nao ha PASS
        return {"ESTADO": "NAO_SEI", "PORQUE": str(ex)[:300]}
    return comparar_sala(n, sala_antes, sala_depois)


def comparar_sala(n: dict, sala_antes: dict | None, sala_depois: dict | None) -> dict:
    """Puro. Cada tabela: o delta da Sala tem de ser o numero de linhas destas corridas."""
    if not sala_antes or not sala_depois:
        return {"ESTADO": "NAO_SEI", "PORQUE": "sem fotografia da Sala antes/depois", "LINHAS_DAS_CORRIDAS": n}
    delta = {t: int(sala_depois[t]) - int(sala_antes[t]) for t in n if t in sala_antes and t in sala_depois}
    falta = [t for t in n if t not in delta]
    nao_bate = {t: {"DELTA_SALA": delta[t], "DAS_CORRIDAS": n[t]} for t in delta if delta[t] != n[t]}
    return {"ESTADO": "NAO_SEI" if falta else ("FAIL" if nao_bate else "PASS"), "LINHAS_DAS_CORRIDAS": n,
            "DELTA_SALA": delta, "NAO_BATE": nao_bate, "SEM_FOTO": falta, "DOCS_NOVOS": n.get("raw_asset")}


def portao_da_fonte_real(ids: list) -> dict:
    """{SOURCE_ID: veredito} do PORTAO DA COLLECTION — o MESMO que a onda dos SITES usa (`onda_web.py --correr`
    -> `micro_coleta.correr` -> `plano` -> `collection_gate.avaliar`, que recusa com GATE:<MOTIVO>). Le o livro
    canonico AGORA, uma vez por chamada. A regra nao se repete aqui: so se pergunta."""
    sys.path.insert(0, str(RAIZ / "curadoria"))
    import collection_gate as GATE                                     # noqa: PLC0415
    ctx = GATE._contexto()
    return {s: GATE.avaliar(s, **ctx) for s in ids}


def pecas_reais() -> dict:
    return {"portao": R.portao_real, "onda": R.onda_real, "relatorio": R.relatorio_real, "ledger": R.ledger_real(),
            "ram": ram_livre_gb_real, "backup": backup_real, "robo": RoboReal(), "reconciliar": reconciliar_real,
            "fonte": portao_da_fonte_real}


# ── 5. o estado e o livro de ciclos ──────────────────────────────────────────
def ler_estado(base: Path) -> dict:
    f = base / ESTADO_F
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"N_CICLO": 0, "LINHAS": {}, "PAROU": None}


def anotar_ciclo(base: Path, linha: dict) -> None:
    with open(base / CICLOS_F, "a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False, default=str) + "\n")


def run_ids_das_ultimas_24h(base: Path, agora_utc: datetime) -> list:
    """As corridas que o servico fez nas ultimas 24 h, do livro de ciclos (para a PROVA-TETO de 24 h)."""
    f = base / CICLOS_F
    out = []
    for l in (f.read_text(encoding="utf-8").splitlines() if f.exists() else []):
        c = json.loads(l)
        fim = c.get("FIM_UTC")
        if fim and datetime.fromisoformat(fim) > agora_utc - timedelta(hours=24):
            out += c.get("RUN_IDS") or []
    return out


def _sala_de(estado_onda: dict, chave: str) -> dict | None:
    s = estado_onda.get(chave)
    return {t: (v["LINHAS"] if isinstance(v, dict) else v) for t, v in s.items()} if isinstance(s, dict) else None


def _juntar(a: dict | None, b: dict | None, f) -> dict | None:
    if a is None or b is None:
        return a if b is None else b
    return {t: f(a[t], b[t]) for t in a if t in b}


# ── 6. UM ciclo ──────────────────────────────────────────────────────────────
def ciclo(base: Path, sha: str, candidatas_por_linha: dict, *, pecas: dict, historico: list | None = None,
          livros: Path | None = None, recibos: tuple = (), livro_24h: Path | None = None,
          agora_utc: datetime | None = None, max_fontes: int | None = None, paralelo: bool = False,
          ligacao=medir_ligacao, a_seco: bool = False, janela_h: int | None = None,
          bloqueios: dict | None = None) -> dict:
    """Um ciclo inteiro. Devolve a linha do livro de ciclos. `PARA` != None = o servico para (fica PARADO).
    `bloqueios`: {linha: {"ESTADO": um de ESTADOS_DE_BLOQUEIO, "PORQUE": ...}} (o `alimentar_linhas`)."""
    base.mkdir(parents=True, exist_ok=True)
    estado = ler_estado(base)
    agora_u = agora_utc or datetime.now(timezone.utc)
    reg = {"CICLO": estado.get("N_CICLO", 0) + 1, "INICIO": agora_iso(), "AGORA_UTC": agora_u.isoformat(timespec="seconds"),
           "A_SECO": a_seco, "PARA": None, "LINHAS": {}, "ESPERAM": [], "RUN_IDS": []}

    def fim(para=None, **extra):
        reg.update(PARA=para, FIM=agora_iso(), FIM_UTC=datetime.now(timezone.utc).isoformat(timespec="seconds"), **extra)
        if not a_seco:
            estado["N_CICLO"] = reg["CICLO"]
            if para:
                estado["PAROU"] = {"PORQUE": para, "CICLO": reg["CICLO"], "QUANDO": reg["FIM"]}
            (base / ESTADO_F).write_text(json.dumps(estado, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
            anotar_ciclo(base, reg)
        return reg

    if estado.get("PAROU") and not a_seco:
        reg["JA_PARADO"] = estado["PAROU"]
        return dict(reg, PARA="JA_PARADO: %s (so --rearmar o liberta)" % estado["PAROU"]["PORQUE"], FIM=agora_iso())
    if (base / DESLIGAR_F).exists():
        return dict(reg, DESLIGADO=True, FIM=agora_iso())             # o interruptor: nao e falha, nao grava
    # 1. RAM (a regra da LOCK-PESADO)
    ram = pecas["ram"]()
    reg["RAM_LIVRE_GB"] = None if ram is None else round(ram, 2)
    if ram is None:
        return fim("RAM_NAO_SEI")
    if ram < RAM_MINIMA_GB:
        return fim("RAM_ABAIXO_DE_5GB")
    # 2. o agendador por fonte: as linhas pela ordem do rodizio, a partilhar o orcamento do dominio
    try:
        reservas = reservas_24h(livro_24h)
    except (ValueError, KeyError, TypeError, OSError) as ex:
        return fim("LIVRO_24H_NAO_SEI", ERRO=str(ex)[:300])
    reg["JANELA_24H"] = janela_h
    reg["TETO_VEM_DE"] = "SINTONIA_TETO_POR_HOST (manual)" if teto_manual() is not None else "orcamento vigente (D124)"
    ultima = R.ultima_visita_por_dominio(livros or base.parent, recibos)
    orcamento: dict = {}
    escolha = {}
    for nome in ordem_das_linhas(list(candidatas_por_linha), reg["CICLO"]):
        decl = next((l for l in LINHAS if l["LINHA"] == nome), None)
        cands = candidatas_por_linha[nome]
        # FEEDER-4-LINHAS: linha que nao pode correr tem nome proprio, e nunca NADA_ELEGIVEL (que e: ha fontes
        # e nenhuma cabe). Decide-se antes da sonda: uma linha que nao corre nao precisa de prova de ligacao.
        bl = (bloqueios or {}).get(nome)
        if not bl and decl is not None and not decl.get("ONDA") and cands:
            bl = {"ESTADO": "BLOQUEADA_CAPACIDADE", "PORQUE": SEM_ONDA}
        if not bl and not cands:
            bl = {"ESTADO": "SEM_CATALOGO", "PORQUE": "a linha nao recebeu nenhuma candidata: rota em falta, "
                                                      "nao zero real"}
        if bl:
            reg["LINHAS"][nome] = dict({k: v for k, v in bl.items() if k != "CANDIDATAS"}, FONTES=[],
                                       PEDIDOS_PREVISTOS=0, CANDIDATAS_RECEBIDAS=len(cands))
            continue
        lig = ligacao(decl or {"LINHA": nome, "TRANSPORTE": "?", "CHAMADA": "?"})
        # ADENDO-PARADA (ciclo 146): a onda recusa a fonte que o portao da Collection nao admite (GATE:<MOTIVO>),
        # e a fonte so la ia para sair 0 corridas. O agendador pergunta ao MESMO portao, agora, e nao a oferece:
        # ela ESPERA com nome proprio. Sem portao injectado, o real (nunca um que admite tudo).
        porta = pecas.get("fonte") or portao_da_fonte_real
        try:
            vered = porta(sorted({c["SOURCE_ID"] for c in cands}))
        except Exception as ex:                                        # noqa: BLE001 — sem veredito nao se oferece
            return fim("PORTAO_DA_FONTE_NAO_SEI", ERRO=str(ex)[:300])
        admitida = {s for s, v in vered.items() if v.get("COLLECTION_ELIGIBLE") is True}
        recusadas = [c for c in cands if c["SOURCE_ID"] not in admitida]
        cands = [c for c in cands if c["SOURCE_ID"] in admitida]
        feitas = ((estado.get("LINHAS") or {}).get(nome) or {}).get("FEITAS_NA_PASSAGEM") or []
        if cands and all(c["SOURCE_ID"] in set(feitas) for c in cands) and not a_seco:
            feitas = []                                             # a coorte da linha acabou: nova passagem
            ln = estado.setdefault("LINHAS", {}).setdefault(nome, {})
            ln["PASSAGEM"] = ln.get("PASSAGEM", 1) + 1
            ln["FEITAS_NA_PASSAGEM"] = []
        if not lig["LIGADA"]:
            reg["LINHAS"][nome] = {"ESTADO": "ESPERA_LIGACAO", "PORQUE": lig["PORQUE"], "FONTES": []}
            continue
        e = escolher(cands, feitas=feitas, ultima=ultima, reservas=reservas, agora_utc=agora_u,
                     orcamento=orcamento, max_fontes=max_fontes, janela_h=janela_h)
        escolha[nome] = e["CORREM"]
        reg["ESPERAM"] += [dict(x, LINHA=nome) for x in e["ESPERAM"]]
        reg["ESPERAM"] += [dict(c, LINHA=nome, PORQUE="FONTE_NAO_READY",
                                ESTADO_LIDO=(vered.get(c["SOURCE_ID"]) or {}).get("STATE", "NAO SEI"),
                                MOTIVO_DO_PORTAO=(vered.get(c["SOURCE_ID"]) or {}).get("MOTIVO"),
                                PORQUE_DO_PORTAO=(vered.get(c["SOURCE_ID"]) or {}).get("PORQUE"), ABRE_EM=None)
                           for c in recusadas if c["SOURCE_ID"] not in set(feitas)]
        reg["LINHAS"][nome] = {"ESTADO": "A_CORRER" if e["CORREM"] else "NADA_ELEGIVEL",
                               "FONTES": [c["SOURCE_ID"] for c in e["CORREM"]],
                               "PEDIDOS_PREVISTOS": sum(c["PREVISTOS"] for c in e["CORREM"])}
    reg["ORCAMENTO_DO_CICLO"] = orcamento
    reg["PROXIMO_A_ABRIR"] = proximo_a_abrir(reg["ESPERAM"])
    correm = {n: fs for n, fs in escolha.items() if fs}
    if a_seco or not correm:
        return fim(None, NADA_A_CORRER=not correm)                 # o robo NAO e tocado
    # 3. portao IT antes (nada saiu ainda)
    reg["EGRESSO_ANTES"] = pecas["portao"]()
    if not reg["EGRESSO_ANTES"].get("PASSA"):
        return fim("EGRESSO_ANTES")
    # 4. backup da Sala com PROVA_VALE (vai-se gravar)
    reg["BACKUP"] = pecas["backup"](base / ("CICLO-%04d" % reg["CICLO"]) / "backup")
    if not reg["BACKUP"].get("PROVA_VALE"):
        return fim("BACKUP_SEM_PROVA_VALE")
    # 5. o robo: parar SO agora (vai-se gravar); no fim, deixa-lo como estava
    robo = pecas["robo"]
    r0 = robo.estado()
    reg["ROBO_ANTES"] = r0
    if r0["VIVO"] is None:
        return fim("ROBO_NAO_SEI")
    parei = False
    if not r0["FLAG"]:
        robo.parar()
        parei = True
        if r0["VIVO"] and not robo.esperar(False):
            robo.tirar_flag()
            return fim("ROBO_NAO_PAROU")
    para = None
    try:
        para = _ondas(base, sha, reg, correm, pecas, historico, livro_24h, paralelo, agora_u)
    except Exception as ex:                                            # noqa: BLE001 — erro tambem PARA
        para = "ERRO_NO_CICLO: %r" % (ex,)
    finally:
        if parei:
            robo.tirar_flag()
            if r0["VIVO"]:
                robo.lancar()
                if not robo.esperar(True):
                    para = para or "ROBO_NAO_VOLTOU"
        reg["ROBO_DEPOIS"] = robo.estado()
        reg["ROBO_RELIGADO"] = bool(parei and r0["VIVO"])
    # 6. contadores por linha (so o que CORREU conta como feito)
    for nome, fs in correm.items():
        ln = estado.setdefault("LINHAS", {}).setdefault(nome, {"PASSAGEM": 1, "FEITAS_NA_PASSAGEM": []})
        corridas = reg["LINHAS"][nome].get("CORRERAM") or []
        ln["FEITAS_NA_PASSAGEM"] = list(dict.fromkeys((ln.get("FEITAS_NA_PASSAGEM") or []) + corridas))
        ln["CICLOS"] = ln.get("CICLOS", 0) + 1
        ln["FONTES_TOTAL"] = ln.get("FONTES_TOTAL", 0) + len(corridas)
        ln["PEDIDOS_TOTAL"] = ln.get("PEDIDOS_TOTAL", 0) + int(reg["LINHAS"][nome].get("PEDIDOS") or 0)
        ln["ULTIMO_CICLO"] = reg["CICLO"]
    return fim(para)


def nada_a_provar(run_ids: list, pastas) -> dict | None:
    """ADENDO-PARADA (ciclo 146). A prova-teto diz NAO_SEI sobre uma lista vazia de corridas, de proposito: contar
    zero deixaria uma onda cega passar. Mas uma onda que recusou todas as fontes nao e cega, e vazia — e parar o
    servico por isso deixava-o PARADO ate alguem rearmar. So e NADA_A_PROVAR se TUDO o diz: nenhum RUN_ID nas
    ondas, o estado de cada onda gravado e nenhuma fonte CORREU, e o livro de cada onda (o contador do transporte,
    SINTONIA_TETO_ONDA) ausente ou com 0 pedidos. Qualquer duvida (estado em falta, livro ilegivel, um pedido que
    seja) = None, e a prova corre como sempre — e para."""
    pastas = list(pastas)
    if run_ids or not pastas:
        return None
    for pasta in pastas:
        f = pasta / "ONDA-WEB-ESTADO.json"
        if not f.exists():
            return None
        livro = pasta / "TETO-ONDA.json"
        try:
            e = json.loads(f.read_text(encoding="utf-8"))
            ped = json.loads(livro.read_text(encoding="utf-8"))["PEDIDOS_POR_DOMINIO"] if livro.exists() else {}
            n = sum(int(v) for v in ped.values())
        except (ValueError, KeyError, TypeError, AttributeError, OSError):
            return None
        if n or any(x.get("CORREU") for x in e.get("FONTES") or []):
            return None
    return {"ESTADO": "NADA_A_PROVAR", "CORRIDAS_DA_ONDA": 0, "PEDIDOS_NOS_LIVROS_DAS_ONDAS": 0, "PEDIDOS_NA_ONDA": 0,
            "DOMINIOS_ACIMA_DO_TETO": {}, "CORRIDAS_SEM_LINHA_NO_LIVRO": [], "CORRIDAS_SEM_PEDIDOS_POR_HOST": [],
            "PORQUE": "nenhuma corrida e nenhum pedido em %d onda(s): estado gravado, nenhuma fonte CORREU, livro da "
                      "onda ausente ou a 0" % len(pastas)}


def _ondas(base, sha, reg, correm, pecas, historico, livro_24h, paralelo, agora_u) -> str | None:
    """As ondas das linhas, a prova-teto (do ciclo e das 24 h), o relatorio e a reconciliacao."""
    if livro_24h is not None:
        # herdado pela onda (D90). D124: o livro da cortesia le SINTONIA_CORTESIA_LIVRO ANTES do nome antigo —
        # os dois apontam para o MESMO ficheiro, senao um ambiente com o nome novo partia o contador em dois.
        os.environ["SINTONIA_TETO_24H"] = str(livro_24h)
        os.environ["SINTONIA_CORTESIA_LIVRO"] = str(livro_24h)
    pastas = {n: base / ("CICLO-%04d" % reg["CICLO"]) / n for n in correm}

    def uma(n):
        return n, pecas["onda"](sha, [c["SOURCE_ID"] for c in correm[n]], pastas[n], list(historico or []), False)
    if paralelo and len(correm) > 1:
        with ThreadPoolExecutor(len(correm)) as ex:
            codigos = dict(ex.map(uma, list(correm)))
    else:
        codigos = dict(uma(n) for n in correm)
    reg["EGRESSO_DEPOIS"] = pecas["portao"]()
    if not reg["EGRESSO_DEPOIS"].get("PASSA"):
        return "EGRESSO_DEPOIS"
    sala_antes = sala_depois = None
    parou = None
    for n, pasta in pastas.items():
        f = pasta / "ONDA-WEB-ESTADO.json"
        e = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        ids = PT.run_ids_da_onda(f.read_text(encoding="utf-8")) if f.exists() else []
        reg["RUN_IDS"] += ids
        foi = [x for x in e.get("FONTES", []) if x.get("CORREU")]
        reg["LINHAS"][n].update(CODIGO_DA_ONDA=codigos[n], PASTA=str(pasta), RUN_IDS=ids, DISJUNTOR=e.get("PAROU"),
                                CORRERAM=[x["SOURCE_ID"] for x in foi],
                                PEDIDOS=sum(sum((x.get("PEDIDOS_POR_DOMINIO") or {}).values()) for x in foi))
        # linhas em paralelo: a Sala so cresce, logo o INICIO mais baixo e anterior a toda a escrita do ciclo
        # e o FIM mais alto e posterior a ela (tabela a tabela)
        sala_antes = _juntar(sala_antes, _sala_de(e, "SALA_INICIO"), min)
        sala_depois = _juntar(sala_depois, _sala_de(e, "SALA_FIM"), max)
        if codigos[n] != 0 or e.get("PAROU"):
            parou = parou or "ONDA_PAROU_%s" % n
    # a PROVA-TETO independente: TODAS as corridas do ciclo juntas (duas linhas no mesmo dominio somam)
    linhas = pecas["ledger"].read_text(encoding="utf-8").splitlines() if pecas["ledger"].exists() else []
    livro = PT.ler_livro(linhas)
    # D124: o teto da prova e o orcamento que ESTEVE em vigor (reproduzido do livro da cortesia), ou o manual.
    try:
        eventos = CA.ler_eventos(Path(livro_24h)) if livro_24h is not None else None
    except (ValueError, OSError) as ex:
        reg["PROVA_TETO_CICLO"] = {"ESTADO": "NAO_SEI", "PORQUE": "livro da cortesia ilegivel: %s" % str(ex)[:200]}
        return "PROVA_TETO_NAO_SEI"
    nada = nada_a_provar(reg["RUN_IDS"], pastas.values())
    if nada:
        reg["PROVA_TETO_CICLO"] = nada
    else:
        p = PT.verificar(sorted(set(reg["RUN_IDS"])), livro, teto_manual(), eventos)
        reg["PROVA_TETO_CICLO"] = {k: p[k] for k in ("ESTADO", "PEDIDOS_NA_ONDA", "DOMINIOS_ACIMA_DO_TETO",
                                                    "CORRIDAS_SEM_LINHA_NO_LIVRO", "CORRIDAS_SEM_PEDIDOS_POR_HOST")}
        if p["ESTADO"] != "PASS":
            return "PROVA_TETO_%s" % p["ESTADO"]
    # e a de 24 h: as corridas deste servico nas ultimas 24 h + as deste ciclo (janela movel, D79/D90). Um ciclo
    # vazio NAO a dispensa: so ha nada a provar nas 24 h se tambem nao houve corrida nenhuma nelas.
    ids_24h = sorted(set(run_ids_das_ultimas_24h(base, agora_u) + reg["RUN_IDS"]))
    if nada and not ids_24h:
        reg["PROVA_TETO_24H"] = {"ESTADO": "NADA_A_PROVAR", "DOMINIOS_ACIMA_DO_TETO": {}}
    else:
        p24 = PT.verificar(ids_24h, livro, teto_manual(), eventos)
        reg["PROVA_TETO_24H"] = {k: p24[k] for k in ("ESTADO", "DOMINIOS_ACIMA_DO_TETO")}
        if p24["ESTADO"] != "PASS":
            return "PROVA_TETO_24H_%s" % p24["ESTADO"]
    for n, pasta in pastas.items():
        if (pasta / "ONDA-WEB-ESTADO.json").exists():
            reg["LINHAS"][n]["CODIGO_DO_RELATORIO"] = pecas["relatorio"](pasta / "ONDA-WEB-ESTADO.json", pasta / "relatorio")
    if parou:
        return parou
    rec = pecas["reconciliar"](reg["RUN_IDS"], sala_antes, sala_depois)
    reg.update(RECONCILIACAO=rec, SALA_ANTES=sala_antes, SALA_DEPOIS=sala_depois, DOCS_NOVOS=rec.get("DOCS_NOVOS"))
    if rec.get("ESTADO") != "PASS":
        return "RECONCILIACAO_%s" % rec.get("ESTADO")
    return None


# ── 7. o servico ─────────────────────────────────────────────────────────────
def _pid_vivo(pid: int) -> bool:
    """O PID ainda existe? Serve so para separar conflito (outro servico a correr) de sobra de um ciclo morto.

    Na duvida, VIVO: dar um vivo como morto poe dois servicos na mesma base; dar um morto como vivo so para.
    No Windows um processo que saiu continua abrivel enquanto alguem segurar o handle dele (medido pelo
    auditor a 30/09): morto e GetExitCodeProcess != 259 (STILL_ACTIVE). Se nem abre: erro 87 (nao ha
    processo com este PID) = morto; outro erro — 5, ACESSO NEGADO: existe e nao nos deixa olhar — = vivo.
    """
    if not 0 < pid <= 0xFFFFFFFF:
        return True
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.OpenProcess.restype = wintypes.HANDLE
        k.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        k.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        k.CloseHandle.argtypes = (wintypes.HANDLE,)
        h = k.OpenProcess(0x1000, False, pid)                              # QUERY_LIMITED_INFORMATION
        if not h:
            return ctypes.get_last_error() != 87
        try:
            codigo = wintypes.DWORD()
            if not k.GetExitCodeProcess(h, ctypes.byref(codigo)):
                return True
            return codigo.value == 259
        finally:
            k.CloseHandle(h)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except OSError:                                                    # EPERM: existe e e de outro utilizador
        return True


def _trinco_de_dono_morto(t: Path) -> bool:
    """True so quando o DONO.json nomeia um PID que ja nao existe. Sem dono legivel nao se toca (pode ser conflito).

    O servico escreve sempre um PID inteiro > 0: 0, negativo, booleano ou texto e DONO corrompido, nao morte.
    """
    try:
        pid = json.loads((t / "DONO.json").read_text(encoding="utf-8"))["PID"]
    except Exception:                                                  # noqa: BLE001 — sem dono, nao e sobra
        return False
    if type(pid) is not int or pid <= 0:
        return False
    return not _pid_vivo(pid)


def _vez_de_tomar(base: Path):
    """A vez de tomar um trinco morto: um trinco do SISTEMA num ficheiro ao lado (msvcrt/fcntl), que o sistema
    solta sozinho se o processo morrer — um processo morto a meio da tomada nao prende a coleta. Devolve o
    ficheiro aberto (a vez e minha) ou None (outro arranque esta a tomar o mesmo trinco agora)."""
    f = open(base / (TRINCO_F + ".tomada"), "a+b")
    try:
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return f
    except OSError:
        f.close()
        return None


def _largar_a_vez(f) -> None:
    try:
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
    except OSError:
        pass                                                           # fechar o ficheiro solta-a de qualquer modo
    finally:
        f.close()


def _escrever_dono(t: Path):
    try:
        (t / "DONO.json").write_text(json.dumps({"PID": os.getpid(), "DESDE": agora_iso()}), encoding="utf-8")
        return t
    except OSError:
        shutil.rmtree(t, ignore_errors=True)                           # trinco sem dono prendia a base para sempre
        return None


def trinco(base: Path):
    """Um servico de cada vez na mesma base: mkdir e atomico. Devolve o caminho ou None (outro a correr).

    Trinco cujo dono morreu (kill, queda, ciclo interrompido) NAO e conflito — e sobra: liberta-se,
    senao a coleta fica parada para sempre a espera de um servico que ja nao existe.

    SERVICO-TRINCO (30/09, auditor: 2-3 donos ao mesmo tempo em 12/20 rodadas no c38610e0c). A tomada:
      1. so com a VEZ (_vez_de_tomar): dois arranques nunca tomam ao mesmo tempo;
      2. com a vez, o dono e RELIDO: o que se leu antes dela pode ja ser o trinco novo de outro;
      3. os.rename do trinco morto para um nome unico: sai inteiro, de uma vez (atomico); so depois mkdir,
         que continua a decidir sozinho contra um arranque normal que chegue nesse instante.
    trinco() nunca lanca: qualquer erro e None (nao e meu), nunca dois donos.
    """
    t = base / TRINCO_F
    try:
        try:
            os.mkdir(t)
            return _escrever_dono(t)
        except FileExistsError:
            pass
        if not _trinco_de_dono_morto(t):
            return None
        vez = _vez_de_tomar(base)
        if vez is None:
            return None
        morto = None
        try:
            if not _trinco_de_dono_morto(t):
                return None
            morto = base / ("%s.morto-%d-%s" % (TRINCO_F, os.getpid(), secrets.token_hex(4)))
            os.rename(t, morto)
            os.mkdir(t)
            return _escrever_dono(t)
        finally:
            _largar_a_vez(vez)
            if morto is not None:
                shutil.rmtree(morto, ignore_errors=True)
    except Exception:                                                  # noqa: BLE001 — nunca lanca; na duvida, nao e meu
        return None


def soltar(t: Path) -> None:
    (t / "DONO.json").unlink(missing_ok=True)
    os.rmdir(t)


def rearmar(base: Path, porque: str) -> dict:
    if not porque.strip():
        raise SystemExit("--rearmar exige --porque=<quem leu o PAROU e o que viu>")
    e = ler_estado(base)
    e.setdefault("REARMES", []).append({"PAROU": e.get("PAROU"), "PORQUE": porque, "QUANDO": agora_iso()})
    e["PAROU"] = None
    (base / ESTADO_F).write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return e


def _carregar(arg: dict) -> tuple:
    base = Path(arg["base"])
    historico = [x for x in arg.get("historico", "").split(",") if x]
    fp = Path(arg["plano"]) if arg.get("plano") else base.parent / "ONDA4-RODADAS" / R.PLANO_F
    if not fp.exists():
        raise SystemExit("SEM_PLANO: %s (gerar com rodadas.py --so-plano, ou dar --plano=)" % fp)
    plano = json.loads(fp.read_text(encoding="utf-8"))
    if arg.get("sha256") and plano.get("COORTE_SHA256") != arg["sha256"]:
        raise SystemExit("PLANO_DE_OUTRA_COORTE: plano %s, pedida %s" % (plano.get("COORTE_SHA256"), arg["sha256"]))
    fe = Path(arg["estado-rodadas"]) if arg.get("estado-rodadas") else fp.parent / R.ESTADO_F
    er = json.loads(fe.read_text(encoding="utf-8")) if fe.exists() else {}
    return base, historico, plano, er


def semear(base: Path, estado_rodadas: dict) -> None:
    """Na 1.a vez, as fontes que o disparador por rodada ja correu contam como feitas (nao se repetem)."""
    e = ler_estado(base)
    if "SITES" not in (e.get("LINHAS") or {}):
        e.setdefault("LINHAS", {})["SITES"] = {"PASSAGEM": 1, "FEITAS_NA_PASSAGEM": feitas_das_rodadas(estado_rodadas),
                                               "SEMEADA_DE": "RODADAS-ESTADO.json"}
        base.mkdir(parents=True, exist_ok=True)
        (base / ESTADO_F).write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    if "base" not in arg:
        print(__doc__)
        return 2
    base = Path(arg["base"])
    if "--estado" in argv:
        print(json.dumps(ler_estado(base), ensure_ascii=False, indent=1, default=str))
        return 0
    if "--rearmar" in argv:
        print(json.dumps(rearmar(base, arg.get("porque", "")).get("REARMES")[-1], ensure_ascii=False, indent=1))
        return 0
    base, historico, plano, er = _carregar(arg)
    livros = Path(arg.get("livros-do-dia") or base.parent)
    recibos = tuple(Path(x) for x in arg.get("recibos", "").split(",") if x)
    livro_24h = Path(arg["teto-24h"]) if arg.get("teto-24h") else None
    max_f = int(arg["max-fontes"]) if arg.get("max-fontes") else None
    alim = alimentar_linhas(plano)                                     # FEEDER-4-LINHAS: cada linha pelo seu catalogo
    cands = {n: a["CANDIDATAS"] for n, a in alim.items()}
    kw = dict(historico=historico, livros=livros, recibos=recibos, livro_24h=livro_24h, max_fontes=max_f,
              paralelo="--paralelo" in argv, janela_h=24 if "--janela-24h" in argv else None,
              bloqueios={n: a for n, a in alim.items() if a["ESTADO"]})
    if "--ensaio-a-seco" in argv:
        # 0 rede, 0 Sala, 0 robo: so o agendador, com as feitas do disparador e os livros de hoje
        ag = datetime.fromisoformat(arg["agora"]).astimezone(timezone.utc) if arg.get("agora") else None
        e = {"LINHAS": {"SITES": {"FEITAS_NA_PASSAGEM": feitas_das_rodadas(er)}}}
        tmp = base / "_ensaio"
        tmp.mkdir(parents=True, exist_ok=True)
        (tmp / ESTADO_F).write_text(json.dumps(e), encoding="utf-8")
        reg = ciclo(tmp, arg.get("sha256", ""), cands, pecas={"ram": lambda: RAM_MINIMA_GB}, agora_utc=ag,
                    a_seco=True, **kw)
        print(json.dumps(reg, ensure_ascii=False, indent=1, default=str))
        return 0
    if not arg.get("sha256"):
        raise SystemExit("--um-ciclo/--servico exigem --sha256=<da coorte congelada>")
    if livro_24h is None:
        raise SystemExit("SEM_LIVRO_24H: --teto-24h=<ficheiro> e obrigatorio (D90)")
    if not plano.get("PODE_CORRER", True):
        raise SystemExit("COORTE_NAO_CONGELADA")
    t = trinco(base)
    if t is None:
        print(json.dumps({"OUTRO_SERVICO_A_CORRER": str(base / TRINCO_F)}))
        return 3
    try:
        semear(base, er)
        while True:
            reg = ciclo(base, arg["sha256"], cands, pecas=pecas_reais(), **kw)
            print(json.dumps({k: reg.get(k) for k in ("CICLO", "PARA", "LINHAS", "PROXIMO_A_ABRIR", "DOCS_NOVOS")},
                             ensure_ascii=False, default=str), flush=True)
            if reg.get("PARA") or reg.get("DESLIGADO") or "--servico" not in argv:
                return 1 if reg.get("PARA") else 0
            time.sleep(60 * float(arg.get("intervalo-min") or 30))
    finally:
        soltar(t)


if __name__ == "__main__":
    raise SystemExit(main())
