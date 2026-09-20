#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS SEIS PROVAS DA NOVA DIVISAO — e a setima, do backoff.

    SOURCE CURATOR PREPARA. COLLECTION COLETA.

    A. o SOURCE CURATOR promove uma fonte DEPOIS dos gates (rota + canario)
    B. a COLLECTION consome a lista READY sem onboarding pesado (zero rede)
    C. a COLLECTION NAO consegue promover fonte a READY          <- fail-closed
    D. fonte READY que degrada gera SOURCE_REPAIR_NEEDED
    E. a COLLECTION segue para a fonte seguinte SEM iniciar reparo
    F. o SOURCE CURATOR recebe o reparo, corre NOVO canario, e so entao devolve READY
    G. um 429 em A adia A — e B, C, D sao trabalhadas DURANTE a espera de A

TODA SONDA TEM UM CASO QUE A FAZ FALHAR. Uma prova de que «a Collection nao
promove» so vale com a contraprova: tenta-se promover e mostra-se a recusa
PELO NOME. Uma prova de que «o Curator promove» so vale se, com o gate a dizer
nao, ele NAO promover.

FAKE ACIMA DO PORTAO MEDE O FAKE. Aqui substitui-se a primitiva mais funda —
a que toca a rede (`worker.PORTAO`, `worker.SONDA`) — e deixa-se o motor
inteiro a correr de verdade: livro, fila, worker, interface. Nada e simulado
acima disso. E nao ha rede: a missao proibiu-a, e uma prova que dependesse dela
nao seria repetivel.

Tudo corre sobre ficheiros proprios num diretorio temporario. O livro da casa
nao e tocado.
"""
from __future__ import annotations

import importlib
import json
import sys
import tempfile
import time
from datetime import timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CUR = RAIZ / "curadoria"
sys.path.insert(0, str(CUR))

import evidencia as EV                # noqa: E402
import fila as F                      # noqa: E402
import interface_collection as IC     # noqa: E402
import lifecycle as LC                # noqa: E402
import worker as W                    # noqa: E402

SAIDA = CUR / "LIFECYCLE-PROOF-V1.json"

FONTES = {
    "IT-PROVA-A": {"SOURCE_ID": "IT-PROVA-A", "TERRITORY": "T2", "ROUTE": "https://prova.invalid/a/",
                   "STRATEGY": "HTML_LINK_DISCOVERY", "ADAPTER_ID": None, "ROUTE_TYPE": "DISCOVERED_ROUTE"},
    "IT-PROVA-B": {"SOURCE_ID": "IT-PROVA-B", "TERRITORY": "T2", "ROUTE": "https://prova.invalid/b/",
                   "STRATEGY": "HTML_LINK_DISCOVERY", "ADAPTER_ID": None, "ROUTE_TYPE": "DISCOVERED_ROUTE"},
    "IT-PROVA-C": {"SOURCE_ID": "IT-PROVA-C", "TERRITORY": "T7", "ROUTE": "https://prova.invalid/c/",
                   "STRATEGY": "CUSTOM_ADAPTER", "ADAPTER_ID": "CANAL_PUBLICO_YOUTUBE_V1", "ROUTE_TYPE": "APPLICATION_ROUTE"},
    "IT-PROVA-D": {"SOURCE_ID": "IT-PROVA-D", "TERRITORY": "T5", "ROUTE": "https://prova.invalid/d/",
                   "STRATEGY": "STATIC_ENDPOINT", "ADAPTER_ID": None, "ROUTE_TYPE": "STATIC_ROUTE"},
}


class Rede:
    """A primitiva mais funda, contada. Cada chamada fica registada, para se
    poder provar que a Collection NAO foi a rede quando pediu a lista READY."""

    def __init__(self):
        self.portao_chamadas = []
        self.sonda_chamadas = []
        self.portao = {}   # sid -> (bool, motivo) | Exception
        self.sonda = {}    # sid -> dict | Exception

    def PORTAO(self, url):
        sid = next((s for s, f in FONTES.items() if f["ROUTE"] == url), url)
        self.portao_chamadas.append(sid)
        r = self.portao.get(sid, (True, "robots.txt do host permite este caminho"))
        if isinstance(r, Exception):
            raise r
        return r

    def SONDA(self, fonte):
        sid = fonte["SOURCE_ID"]
        self.sonda_chamadas.append(sid)
        r = self.sonda.get(sid, {"PASS": True, "HTTP": 200, "ALVOS": 3, "PORQUE": ""})
        if isinstance(r, Exception):
            raise r
        return dict(r)


def isolar(tmp: Path, rede: Rede):
    """Ficheiros proprios + primitivas de rede substituidas. Nada mais."""
    for m in (LC, F, EV, IC, W):
        importlib.reload(m)
    LC.LIVRO = tmp / "LEDGER.json"
    F.FILA = tmp / "QUEUE.json"
    EV.EVIDENCIA = tmp / "EVIDENCE.json"
    estado = tmp / "ESTADO.json"
    estado.write_text(json.dumps({"HEAD": "prova", "FONTES": list(FONTES.values())}), encoding="utf-8")
    IC.ESTADO_ACTUAL = estado
    IC.LC, IC.F = LC, F
    W.LC, W.F, W.EV = LC, F, EV
    W.PORTAO = rede.PORTAO
    W.SONDA = rede.SONDA


def caso(nome, titulo, ok, **det):
    d = {"CASO": nome, "TITULO": titulo, "PASS": bool(ok), "REDE_REAL": False, **det}
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", nome, titulo))
    return d


def main() -> int:
    tmpd = tempfile.TemporaryDirectory()
    tmp = Path(tmpd.name)
    rede = Rede()
    isolar(tmp, rede)
    casos = []

    # ── A · o Curator promove APOS os gates ───────────────────────────────
    F.enfileirar("IT-PROVA-A", F.VALIDATE_ROUTE)
    feitos = W.correr(pausa=0, verboso=False, contratos=FONTES)
    a_estado = LC.estado_de("IT-PROVA-A")
    a_hist = [t["NEW_STATE"] for t in LC.historia("IT-PROVA-A")]
    a_ref = LC.historia("IT-PROVA-A")[-1]["EVIDENCE_REF"]
    a_prova = EV.por_ref(a_ref)
    # contraprova 1: gate de rota diz NAO -> nao promove, e diz porque
    rede.portao["IT-PROVA-B"] = (False, "robots.txt do host barra este caminho para SintoniaScrap")
    F.enfileirar("IT-PROVA-B", F.VALIDATE_ROUTE)
    W.correr(pausa=0, verboso=False, contratos=FONTES)
    b_estado = LC.estado_de("IT-PROVA-B")
    # contraprova 2: rota permitida, canario FALHA -> nao promove
    rede.sonda["IT-PROVA-D"] = {"PASS": False, "HTTP": 200, "PORQUE": "o motor resolveu e nao saiu nenhum alvo", "CLASSE": "SOURCE"}
    F.enfileirar("IT-PROVA-D", F.VALIDATE_ROUTE)
    W.correr(pausa=0, verboso=False, contratos=FONTES)
    d_estado = LC.estado_de("IT-PROVA-D")
    casos.append(caso("A", "o Curator promove so depois de rota + canario",
                      a_estado == LC.READY_FOR_COLLECTION
                      and a_hist == [LC.CANARY_PENDING, LC.READY_FOR_COLLECTION]
                      and a_prova is not None and a_prova["ETAPA"] == F.CANARY
                      and rede.sonda_chamadas.count("IT-PROVA-A") == 1
                      and b_estado == LC.CONTRACT_READY_ROUTE_BLOCKED
                      and "IT-PROVA-B" not in rede.sonda_chamadas
                      and d_estado == LC.CONTRACTED_CANARY_FAILED,
                      ESTADO_A=a_estado, HISTORIA_A=a_hist, EVIDENCE_REF_A=a_ref,
                      ETAPA_DA_PROVA=a_prova["ETAPA"] if a_prova else None,
                      CONTRAPROVA_ROTA_BARRADA={"SOURCE_ID": "IT-PROVA-B", "ESTADO": b_estado,
                                                "CANARIO_CHAMADO": "IT-PROVA-B" in rede.sonda_chamadas},
                      CONTRAPROVA_CANARIO_FALHOU={"SOURCE_ID": "IT-PROVA-D", "ESTADO": d_estado},
                      TAREFAS_EXECUTADAS=len(feitos)))

    # ── B · a Collection consome a lista READY sem ir a rede ──────────────
    antes = (len(rede.portao_chamadas), len(rede.sonda_chamadas))
    lista = IC.ready_sources()
    depois = (len(rede.portao_chamadas), len(rede.sonda_chamadas))
    ids = [r["SOURCE_ID"] for r in lista]
    ficha = lista[0] if lista else {}
    casos.append(caso("B", "a Collection consome READY sem onboarding pesado",
                      ids == ["IT-PROVA-A"] and antes == depois
                      and ficha.get("ROUTE") == FONTES["IT-PROVA-A"]["ROUTE"]
                      and ficha.get("EVIDENCE_REF") == a_ref
                      and ficha.get("CAPABILITY") == "HTML_LINK_DISCOVERY",
                      READY_IDS=ids, CHAMADAS_DE_REDE_DURANTE={"antes": antes, "depois": depois},
                      FICHA_ENTREGUE={k: ficha.get(k) for k in ("SOURCE_ID", "CAPABILITY", "ROUTE", "EVIDENCE_REF", "STATUS")}))

    # ── C · a Collection NAO promove — recusa pelo nome ───────────────────
    recusas = {}
    for anterior_sid, prep in (("IT-PROVA-C", [LC.CANARY_PENDING]),):
        for e in prep:
            LC.registar(anterior_sid, e, "preparada pelo curator")
    tentativas = [
        ("CANARY_PENDING->READY", "IT-PROVA-C"),
    ]
    for nome, sid in tentativas:
        try:
            LC.registar(sid, LC.READY_FOR_COLLECTION, "colhi e correu bem",
                        owner=LC.OWNER_COLLECTION, evidence_ref="RUN-COLLECTION-1")
            recusas[nome] = "PROMOVEU — DEFEITO"
        except ValueError as ex:
            recusas[nome] = str(ex)
    # ... e tambem nao promove de DEGRADED nem de REPAIRING
    LC.registar("IT-PROVA-C", LC.READY_FOR_COLLECTION, "canario", evidence_ref="EV-C-1")
    LC.registar("IT-PROVA-C", LC.DEGRADED, "quebrou", owner=LC.OWNER_COLLECTION, evidence_ref="RUN-2")
    try:
        LC.registar("IT-PROVA-C", LC.READY_FOR_COLLECTION, "ja esta boa",
                    owner=LC.OWNER_COLLECTION, evidence_ref="RUN-3")
        recusas["DEGRADED->READY"] = "PROMOVEU — DEFEITO"
    except ValueError as ex:
        recusas["DEGRADED->READY"] = str(ex)
    # controlo positivo: o MESMO guarda deixa o Curator passar
    LC.registar("IT-PROVA-C", LC.REPAIRING, "curator assume")
    try:
        LC.registar("IT-PROVA-C", LC.READY_FOR_COLLECTION, "ja esta boa",
                    owner=LC.OWNER_COLLECTION, evidence_ref="RUN-4")
        recusas["REPAIRING->READY"] = "PROMOVEU — DEFEITO"
    except ValueError as ex:
        recusas["REPAIRING->READY"] = str(ex)
    LC.registar("IT-PROVA-C", LC.READY_FOR_COLLECTION, "novo canario", evidence_ref="EV-C-2")
    curator_passou = LC.estado_de("IT-PROVA-C") == LC.READY_FOR_COLLECTION
    casos.append(caso("C", "a Collection NAO consegue promover para READY (fail-closed)",
                      all("Collection" in v and "DEFEITO" not in v for v in recusas.values())
                      and curator_passou,
                      RECUSAS_PELO_NOME={k: v[:140] for k, v in recusas.items()},
                      CONTROLO_POSITIVO_CURATOR_PROMOVE=curator_passou))

    # ── D · READY degradada gera SOURCE_REPAIR_NEEDED ─────────────────────
    ready_antes = IC.ready_ids()
    r_d = IC.source_repair_needed("IT-PROVA-A", "HTTP_404", run_id="IT-T2-RUN-PROVA-D",
                                  route=FONTES["IT-PROVA-A"]["ROUTE"])
    ready_depois = IC.ready_ids()
    tarefa = next((t for t in F.elegiveis() if t["TASK_ID"] == r_d.get("TASK_ID")), None)
    # contraprova: reportar quebra de fonte que NAO estava READY e recusado
    r_d2 = IC.source_repair_needed("IT-PROVA-B", "HTTP_500", run_id="RUN-X")
    tarefas_b = [t for t in F.elegiveis() if t["SOURCE_ID"] == "IT-PROVA-B" and t["TASK_TYPE"] == F.REPAIR]
    casos.append(caso("D", "fonte READY degradada gera SOURCE_REPAIR_NEEDED",
                      r_d.get("ACEITE") is True and LC.estado_de("IT-PROVA-A") == LC.DEGRADED
                      and "IT-PROVA-A" in ready_antes and "IT-PROVA-A" not in ready_depois
                      and tarefa is not None and tarefa["TASK_TYPE"] == F.REPAIR
                      and LC.historia("IT-PROVA-A")[-1]["OWNER"] == LC.OWNER_COLLECTION
                      and r_d2.get("ACEITE") is False and not tarefas_b,
                      RESPOSTA={k: r_d.get(k) for k in ("ACEITE", "NOVO_ESTADO", "TASK_ID", "FAILURE_TYPE", "RUN_ID")},
                      READY_ANTES=ready_antes, READY_DEPOIS=ready_depois,
                      TAREFA_NA_FILA_DO_CURATOR={k: tarefa.get(k) for k in ("TASK_ID", "TASK_TYPE", "STATUS", "PRIORITY")} if tarefa else None,
                      CONTRAPROVA_NAO_READY={"SOURCE_ID": "IT-PROVA-B", "ACEITE": r_d2.get("ACEITE"),
                                             "PORQUE": r_d2.get("PORQUE", "")[:120], "REPAIR_CRIADO": bool(tarefas_b)}))

    # ── E · a Collection segue para a proxima SEM iniciar reparo ──────────
    # Repoe duas READY para a Collection ter uma lista de tres.
    for sid in ("IT-PROVA-B", "IT-PROVA-D"):
        LC.registar(sid, LC.CANARY_PENDING, "reposta para a prova E")
        LC.registar(sid, LC.READY_FOR_COLLECTION, "canario", evidence_ref="EV-%s" % sid)
    LC.registar("IT-PROVA-A", LC.REPAIRING, "curator assume (limpa a prova D)")
    LC.registar("IT-PROVA-A", LC.READY_FOR_COLLECTION, "novo canario", evidence_ref="EV-A-2")
    lista_e = IC.ready_ids()
    sonda_antes = len(rede.sonda_chamadas)
    visitadas, reportadas = [], []

    def a_collection_colhe(sid):
        # A Collection desta prova: colhe A e D; B falha com 404.
        return sid != "IT-PROVA-B"

    for sid in lista_e:
        visitadas.append(sid)
        if not a_collection_colhe(sid):
            reportadas.append(IC.source_repair_needed(sid, "HTTP_404", run_id="RUN-E")["TASK_ID"])
            continue   # <- segue para a proxima. Nao repara. Nao canaria.
    tarefas_pendentes = [t for t in F.elegiveis() if t["TASK_ID"] in reportadas]
    casos.append(caso("E", "a Collection segue para a proxima fonte sem iniciar reparo",
                      visitadas == lista_e and len(lista_e) >= 3
                      and visitadas.index("IT-PROVA-B") < len(visitadas) - 1
                      and LC.estado_de("IT-PROVA-B") == LC.DEGRADED
                      and len(rede.sonda_chamadas) == sonda_antes
                      and len(tarefas_pendentes) == 1 and tarefas_pendentes[0]["STATUS"] == F.PENDING,
                      LISTA_READY=lista_e, VISITADAS=visitadas,
                      DEGRADADA="IT-PROVA-B", ESTADO_DA_DEGRADADA=LC.estado_de("IT-PROVA-B"),
                      CANARIOS_CHAMADOS_PELA_COLLECTION=len(rede.sonda_chamadas) - sonda_antes,
                      REPAIR_FICOU_PENDENTE_PARA_O_CURATOR=[t["TASK_ID"] for t in tarefas_pendentes]))

    # ── F · o Curator recebe o reparo, canario NOVO, e so entao READY ─────
    ref_velho = [t for t in LC.historia("IT-PROVA-B") if t["NEW_STATE"] == LC.READY_FOR_COLLECTION][-1]["EVIDENCE_REF"]
    # decreto: DEGRADED -> READY sem canario e recusado pelo nome
    try:
        LC.registar("IT-PROVA-B", LC.READY_FOR_COLLECTION, "ja deve estar boa", evidence_ref=ref_velho)
        decreto = "PROMOVEU — DEFEITO"
    except ValueError as ex:
        decreto = str(ex)
    # o worker do Curator pega o REPAIR: contraprova primeiro (canario ainda falha)
    rede.sonda["IT-PROVA-B"] = {"PASS": False, "HTTP": 404, "PORQUE": "indice inacessivel: 404", "CLASSE": "SOURCE"}
    W.correr(pausa=0, verboso=False, contratos=FONTES)
    estado_apos_falha = LC.estado_de("IT-PROVA-B")
    # o Curator volta a por REPAIR (segunda tentativa), e agora o canario passa
    LC.registar("IT-PROVA-B", LC.DEGRADED, "continua degradada; curator reagenda o reparo", evidence_ref="EV-F-0")
    F.enfileirar("IT-PROVA-B", F.REPAIR, priority=80, motivo="segunda tentativa de reparo")
    rede.sonda["IT-PROVA-B"] = {"PASS": True, "HTTP": 200, "ALVOS": 2, "PORQUE": ""}
    W.correr(pausa=0, verboso=False, contratos=FONTES)
    hist_f = [t["NEW_STATE"] for t in LC.historia("IT-PROVA-B")]
    ref_novo = LC.historia("IT-PROVA-B")[-1]["EVIDENCE_REF"]
    ficha_f = next((r for r in IC.ready_sources() if r["SOURCE_ID"] == "IT-PROVA-B"), {})
    casos.append(caso("F", "o Curator recebe o reparo, faz NOVO canario e so entao devolve READY",
                      "REPAIRING" in decreto and "DEFEITO" not in decreto
                      and estado_apos_falha != LC.READY_FOR_COLLECTION
                      and hist_f[-3:] == [LC.DEGRADED, LC.REPAIRING, LC.READY_FOR_COLLECTION]
                      and ref_novo != ref_velho and EV.por_ref(ref_novo)["ETAPA"] == F.REPAIR
                      and ficha_f.get("EVIDENCE_REF") == ref_novo,
                      DECRETO_RECUSADO=decreto[:140],
                      CONTRAPROVA_CANARIO_DO_REPARO_FALHOU={"ESTADO": estado_apos_falha},
                      HISTORIA_FINAL=hist_f[-4:], EVIDENCE_REF_VELHO=ref_velho, EVIDENCE_REF_NOVO=ref_novo,
                      A_INTERFACE_ENTREGA_A_PROVA_NOVA=ficha_f.get("EVIDENCE_REF") == ref_novo))

    # ── G · backoff: 429 em A adia A; B, C, D correm DURANTE a espera ─────
    tmp2 = tempfile.TemporaryDirectory()
    rede2 = Rede()
    isolar(Path(tmp2.name), rede2)
    for sid in ("IT-PROVA-A", "IT-PROVA-B", "IT-PROVA-C", "IT-PROVA-D"):
        LC.registar(sid, LC.CANARY_PENDING, "rota validada")
        F.enfileirar(sid, F.CANARY, priority={"IT-PROVA-A": 99}.get(sid, 50))
    rede2.sonda["IT-PROVA-A"] = {"PASS": False, "HTTP": 429, "RETRY_AFTER_S": 3600,
                                 "PORQUE": "HTTP 429 (a plataforma pediu 3600 s)"}
    t0 = F.agora_utc()
    relogio = {"agora": t0}
    inicio = time.monotonic()
    feitos_g = W.correr(pausa=0, verboso=False, contratos=FONTES, agora_fn=lambda: relogio["agora"])
    duracao = time.monotonic() - inicio
    ordem = [r["SOURCE_ID"] for r in feitos_g]
    q = json.loads(F.FILA.read_text(encoding="utf-8"))["TAREFAS"]
    por_sid = {t["SOURCE_ID"]: t for t in q}
    a_task = por_sid["IT-PROVA-A"]
    trabalhadas_durante = [s for s in ("IT-PROVA-B", "IT-PROVA-C", "IT-PROVA-D")
                           if por_sid[s]["STATUS"] == F.DONE
                           and por_sid[s]["UPDATED_AT"] < a_task["NEXT_ATTEMPT_AT"]]
    eleg_59 = [t["SOURCE_ID"] for t in F.elegiveis(t0 + timedelta(minutes=59))]
    eleg_61 = [t["SOURCE_ID"] for t in F.elegiveis(t0 + timedelta(minutes=61))]
    # o relogio anda; A volta sozinha e agora passa
    rede2.sonda["IT-PROVA-A"] = {"PASS": True, "HTTP": 200, "ALVOS": 1, "PORQUE": ""}
    relogio["agora"] = t0 + timedelta(minutes=61)
    feitos_g2 = W.correr(pausa=0, verboso=False, contratos=FONTES, agora_fn=lambda: relogio["agora"])
    estados_g = {s: LC.estado_de(s) for s in ("IT-PROVA-A", "IT-PROVA-B", "IT-PROVA-C", "IT-PROVA-D")}
    casos.append(caso("G", "429 em A -> RETRY_AFTER; B, C, D trabalhadas durante a espera; A volta sozinha",
                      ordem[0] == "IT-PROVA-A" and ordem[1:] == ["IT-PROVA-B", "IT-PROVA-C", "IT-PROVA-D"]
                      and a_task["STATUS"] == F.WAITING_RETRY
                      and F._parse(a_task["NEXT_ATTEMPT_AT"]) == t0 + timedelta(seconds=3600)
                      and trabalhadas_durante == ["IT-PROVA-B", "IT-PROVA-C", "IT-PROVA-D"]
                      and duracao < 5.0
                      and eleg_59 == [] and eleg_61 == ["IT-PROVA-A"]
                      and [r["SOURCE_ID"] for r in feitos_g2] == ["IT-PROVA-A"]
                      and estados_g == {s: LC.READY_FOR_COLLECTION for s in estados_g},
                      ORDEM_DE_EXECUCAO=ordem, ESTADO_DA_TAREFA_A=a_task["STATUS"],
                      NEXT_ATTEMPT_AT_A=a_task["NEXT_ATTEMPT_AT"],
                      TRABALHADAS_DURANTE_A_ESPERA_DE_A=trabalhadas_durante,
                      SEGUNDOS_DE_PAREDE=round(duracao, 3),
                      ELEGIVEIS_AOS_59_MIN=eleg_59, ELEGIVEIS_AOS_61_MIN=eleg_61,
                      SEGUNDA_VOLTA=[r["SOURCE_ID"] for r in feitos_g2], ESTADOS_FINAIS=estados_g,
                      ESTADO_DE_A_DURANTE_A_ESPERA=[t["NEW_STATE"] for t in LC.historia("IT-PROVA-A")]))

    d = {"DATASET": "LIFECYCLE-PROOF-V1",
         "LEI": ("sete provas isoladas da divisao SOURCE CURATOR prepara / COLLECTION coleta. "
                 "Rede substituida na primitiva mais funda (worker.PORTAO / worker.SONDA); "
                 "livro, fila, worker e interface correm de verdade sobre ficheiros proprios. "
                 "Nao se inventa PASS: cada prova tem a sua contraprova."),
         "GERADO_EM": LC.agora(), "CASOS": casos,
         "PASS_TOTAL": sum(1 for c in casos if c["PASS"]), "CASOS_TOTAL": len(casos),
         "LIVRO_DA_CASA_TOCADO": False}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\nPASS %d/%d" % (d["PASS_TOTAL"], d["CASOS_TOTAL"]))
    tmpd.cleanup()
    tmp2.cleanup()
    return 0 if d["PASS_TOTAL"] == d["CASOS_TOTAL"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
