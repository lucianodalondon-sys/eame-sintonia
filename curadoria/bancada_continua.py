#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A BANCADA CONTINUA da FILA-PRECISA-DE-IA (D32 (7), continuacao) — sem API paga, sem rede pesada.

O robo refaz a fila a cada volta (ciclo_continuo). A bancada trabalha por LOTES, em tres passos, e
so o PRIMEIRO e o SEGUNDO vao a rede — pelo transporte do robo:

    preparar  o robo escolhe N casos da fila (D29 primeiro) e busca, por caso, a pagina de entrada
              e o item que o canario abriu (no maximo 2), com o portao de egresso de CONSENSO (IT)
              no inicio e de 20 em 20 pedidos, robots pela porta do robo, 2 s por anfitriao,
              no maximo 5 pedidos por DOMINIO por lote (D38). Escreve o LOTE (json) e os bytes.
    extra     o agente pode pedir ate 2 paginas a mais por caso (ex.: a seccao dos boletins); o robo
              busca-as com as mesmas regras e acrescenta-as ao lote.
    ingerir   o agente (a assinatura, nesta maquina) entrega as respostas; cada uma so entra se citar
              paginas DO LOTE (URL + sha256 iguais) e passar a porta de destino:
                RECEITA      -> bancada_ia.propor_receita      (o REPAIR_CONTRACT aplica; canario+regua decidem)
                SEM_RECEITA  -> bancada_ia.responder_sem_receita (o caso sai da fila ate haver prova nova)

UM ESCRITOR POR FICHEIRO: o lote e os bytes sao do robo; as respostas sao do agente; as portas
(PROPOSTAS-DE-RECEITA-V1) sao do agente e o robo so as le. Nenhum livro de estado e escrito aqui.

uso:
  py curadoria/bancada_continua.py preparar --n 30 --rede-autorizada <missao> [--so-janela] [--pasta DIR]
  py curadoria/bancada_continua.py extra <LOTE.json> <pedidos.json> --rede-autorizada <missao>

D41.3: sem --rede-autorizada a bancada recusa ir a rede (uma copia comeca com a rede fechada).
  py curadoria/bancada_continua.py ingerir <LOTE.json> <respostas.json> [--propostas FICHEIRO]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import bancada_ia as BIA   # noqa: E402

PASTA = Path(os.environ.get("SINTONIA_BANCADA_DIR") or RAIZ / "data" / "colheita" / "bancada-ia")
MAX_POR_CASO_PREPARAR = 2
MAX_EXTRA_POR_CASO = 2
MAX_POR_ANFITRIAO = 5
PAUSA_POR_ANFITRIAO_S = 2.0
EGRESSO_DE_N_EM_N = 20
_SHA = re.compile(r"^[0-9a-f]{64}$")


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(p: Path, chave: str) -> list:
    return BIA._json(p, chave)


# ---------------------------------------------------------------------------
# O TRANSPORTE (lado do robo)
# ---------------------------------------------------------------------------
class Transporte:
    """O mesmo `canario.buscar` do robo, com as travas de cortesia de um lote."""

    def __init__(self, buscar=None, robots=None, egresso=None, dormir=time.sleep):
        import canario as CAN            # noqa: PLC0415
        import gate_de_rota as GATE      # noqa: PLC0415
        self._buscar = buscar or CAN.buscar
        self._robots = robots or (lambda host: GATE.robots_de(host)[0])
        self._permitido = GATE.permitido
        self._egresso = egresso or egresso_it
        self._dormir = dormir
        self.pedidos, self.por_host, self.ultimo, self.cache_robots = 0, {}, {}, {}

    def pegar(self, url: str, pasta: Path) -> dict:
        host = url.split("/")[2]
        dominio = dominio_de(host)
        linha = {"URL": url, "LIDO_EM": agora()}
        # D38/D41.3: o teto conta o DOMINIO (www.site e site sao um so), como a cortesia do coletor
        if self.por_host.get(dominio, 0) >= MAX_POR_ANFITRIAO:
            return dict(linha, ESTADO="TETO_POR_DOMINIO")
        if host not in self.cache_robots:
            try:
                self.cache_robots[host] = self._robots(host)
            except Exception:            # noqa: BLE001
                self.cache_robots[host] = None
        rp = self.cache_robots[host]
        if rp is None:
            return dict(linha, ESTADO="ROBOTS_ILEGIVEL")
        if not self._permitido(url, rp):
            return dict(linha, ESTADO="ROBOTS_PROIBE")
        if self.pedidos % EGRESSO_DE_N_EM_N == 0 and not self._egresso():
            raise SystemExit("PARAR: o portao de egresso de consenso nao da PASS IT")
        espera = PAUSA_POR_ANFITRIAO_S - (time.time() - self.ultimo.get(host, 0))
        if espera > 0:
            self._dormir(espera)
        st, b, erro = self._buscar(url)
        self.ultimo[host] = time.time()
        self.pedidos += 1
        self.por_host[dominio] = self.por_host.get(dominio, 0) + 1
        h = hashlib.sha256(b or b"").hexdigest()
        caminho = pasta / ("%s.bin" % h[:20])
        caminho.write_bytes(b or b"")
        return dict(linha, ESTADO="LIDO", HTTP=st, ERRO=erro, BYTES=len(b or b""), SHA256=h,
                    BYTES_EM=str(caminho), EGRESSO="IT (consenso)")


def dominio_de(host: str) -> str:
    h = host.lower().split(":")[0]
    return h[4:] if h.startswith("www.") else h


class RedeNaoAutorizada(SystemExit):
    pass


def exigir_autorizacao(autorizacao: str | None) -> str:
    """D41.3: uma copia comeca com a rede FECHADA; so abre com a missao que a autoriza, por escrito."""
    if not (autorizacao or "").strip():
        raise RedeNaoAutorizada("RECUSA (D41.3): sem --rede-autorizada <missao> a bancada nao vai a rede")
    return autorizacao.strip()


def egresso_it() -> bool:
    r = subprocess.run([sys.executable, str(RAIZ / "superficie" / "rede.py"), "--portao-de-egresso", "IT"],
                       capture_output=True, text=True)
    return '"EGRESS_GATE": "PASS"' in r.stdout


def _alvos_do_ultimo_canario() -> dict[str, str]:
    """{SOURCE_ID: o item que o ultimo canario/reparo abriu} — o ficheiro de provas lido UMA vez."""
    out = {}
    for p in _json(RAIZ / "curadoria" / "LIFECYCLE-EVIDENCE-V1.json", "PROVAS"):
        if p.get("ETAPA") not in ("CANARY", "REVALIDATE", "REPAIR_CONTRACT"):
            continue
        d = p.get("DADOS") or {}
        alvo = d.get("ALVO")
        if not alvo:
            il = d.get("ITEM_LIDO")
            alvo = il.get("URL") if isinstance(il, dict) else il
        if isinstance(alvo, str) and alvo.startswith("http"):
            out[p["SOURCE_ID"]] = alvo            # o ultimo vence
    return out


def _entrada(caso: dict, tabela: dict) -> str | None:
    if caso.get("ENTRADA"):
        return caso["ENTRADA"]
    linha = tabela.get(caso["CASO"]) or {}
    aq = linha.get("ACQUISITION") or {}
    return aq.get("INDEX_URL") or aq.get("URL") or linha.get("CANONICAL_ENTRY_URL")


# ---------------------------------------------------------------------------
# preparar · extra · ingerir
# ---------------------------------------------------------------------------
def preparar(n: int, *, so_janela: bool = False, pasta: Path | None = None, transporte=None,
             fila: dict | None = None, rede_autorizada: str | None = None) -> Path:
    autorizacao = exigir_autorizacao(rede_autorizada)
    pasta = pasta or PASTA
    fila = fila if fila is not None else BIA.construir_do_disco(escrever=True)
    casos = [c for c in fila["CASOS"] if c["PERGUNTA"] == "RECEITA" and (c["JANELA_D29"] or not so_janela)][:n]
    lote_id = "LOTE-%s" % datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dir_lote = pasta / lote_id
    dir_lote.mkdir(parents=True, exist_ok=True)
    tr = transporte or Transporte()
    tabela = {c["SOURCE_ID"]: c for c in _json(RAIZ / "regras" / "italy_contracts_onboarded.json", "FONTES")}
    alvos = _alvos_do_ultimo_canario()
    saida = []
    for c in casos:
        urls = [u for u in (_entrada(c, tabela), alvos.get(c["CASO"])) if u]
        paginas = [dict(tr.pegar(u, dir_lote), PAPEL=papel)
                   for u, papel in list(zip(urls, ("ENTRADA", "ITEM_DO_CANARIO")))[:MAX_POR_CASO_PREPARAR]]
        saida.append(dict(c, PAGINAS=paginas, EXTRA_PEDIDAS=0))
    lote = {"LOTE_ID": lote_id, "CRIADO_EM": agora(), "ESCRITOR": "o robo (bancada_continua.preparar)",
            "SO_JANELA": so_janela, "REDE_AUTORIZADA_POR": autorizacao, "PEDIDOS_A_REDE": tr.pedidos,
            "CASOS": saida}
    p = dir_lote / "LOTE.json"
    p.write_text(json.dumps(lote, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def extra(lote_p: Path, pedidos: dict, *, transporte=None, rede_autorizada: str | None = None) -> dict:
    """pedidos = {CASO: [url, ...]}; no maximo MAX_EXTRA_POR_CASO por caso, no total do lote."""
    exigir_autorizacao(rede_autorizada)
    lote = json.loads(lote_p.read_text(encoding="utf-8"))
    tr = transporte or Transporte()
    for c in lote["CASOS"]:
        for u in pedidos.get(c["CASO"], []):
            if c["EXTRA_PEDIDAS"] >= MAX_EXTRA_POR_CASO:
                c["PAGINAS"].append({"URL": u, "ESTADO": "TETO_DE_EXTRAS", "PAPEL": "EXTRA"})
                continue
            c["PAGINAS"].append(dict(tr.pegar(u, lote_p.parent), PAPEL="EXTRA"))
            c["EXTRA_PEDIDAS"] += 1
    lote["PEDIDOS_A_REDE"] = lote.get("PEDIDOS_A_REDE", 0) + tr.pedidos
    lote_p.write_text(json.dumps(lote, ensure_ascii=False, indent=1), encoding="utf-8")
    return lote


class RespostaInvalida(ValueError):
    pass


def _paginas_do_lote(caso: dict) -> dict[str, str]:
    return {p["URL"]: p["SHA256"] for p in caso["PAGINAS"] if p.get("SHA256")}


def ingerir(lote_p: Path, respostas: list[dict], *, propostas: Path | None = None,
            por: str = "agente (assinatura) — bancada continua") -> dict:
    """Cada resposta: {CASO, RESPOSTA: RECEITA|SEM_RECEITA, PAGINAS_LIDAS: [url...], PORQUE,
    INDEX_URL?, LINK_PATTERN?}. Devolve o que entrou e o que foi recusado (e porque)."""
    lote = json.loads(lote_p.read_text(encoding="utf-8"))
    por_caso = {c["CASO"]: c for c in lote["CASOS"]}
    entrou, recusou = [], []
    for r in respostas:
        try:
            caso = por_caso.get(r.get("CASO"))
            if caso is None:
                raise RespostaInvalida("caso fora do lote")
            lidas = _paginas_do_lote(caso)
            citadas = r.get("PAGINAS_LIDAS") or []
            if not citadas or any(u not in lidas for u in citadas):
                raise RespostaInvalida("cita pagina que nao esta no lote (so conta o que o robo buscou)")
            provas = [{"URL": u, "SHA256": lidas[u]} for u in citadas]
            base = {"SOURCE_ID": caso["CASO"], "PORQUE": r.get("PORQUE") or "", "PROPOSTO_EM": agora(),
                    "PROPOSTO_POR": por, "PAGINAS_LIDAS": provas, "LOTE": lote["LOTE_ID"]}
            if r.get("RESPOSTA") == "RECEITA":
                BIA.propor_receita(dict(base, INDEX_URL=r.get("INDEX_URL"), LINK_PATTERN=r.get("LINK_PATTERN")),
                                   propostas)
            elif r.get("RESPOSTA") == "SEM_RECEITA":
                BIA.responder_sem_receita(base, propostas)
            else:
                raise RespostaInvalida("RESPOSTA tem de ser RECEITA ou SEM_RECEITA")
            entrou.append({"CASO": caso["CASO"], "RESPOSTA": r["RESPOSTA"]})
        except (RespostaInvalida, BIA.PropostaInvalida) as e:
            recusou.append({"CASO": r.get("CASO"), "PORQUE": str(e)})
    return {"LOTE": lote["LOTE_ID"], "ENTROU": entrou, "RECUSOU": recusou}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("preparar"); a1.add_argument("--n", type=int, default=BIA.LOTE_CANARIO)
    a1.add_argument("--so-janela", action="store_true"); a1.add_argument("--pasta", type=Path)
    a1.add_argument("--rede-autorizada", help="a missao que autoriza a rede (D41.3); sem isto, recusa")
    a2 = sub.add_parser("extra"); a2.add_argument("lote", type=Path); a2.add_argument("pedidos", type=Path)
    a2.add_argument("--rede-autorizada", help="a missao que autoriza a rede (D41.3); sem isto, recusa")
    a3 = sub.add_parser("ingerir"); a3.add_argument("lote", type=Path); a3.add_argument("respostas", type=Path)
    a3.add_argument("--propostas", type=Path)
    a = ap.parse_args()
    if a.cmd == "preparar":
        p = preparar(a.n, so_janela=a.so_janela, pasta=a.pasta, rede_autorizada=a.rede_autorizada)
        lote = json.loads(p.read_text(encoding="utf-8"))
        print("LOTE %s · %d casos · %d pedidos a rede · %s" % (lote["LOTE_ID"], len(lote["CASOS"]),
                                                               lote["PEDIDOS_A_REDE"], p))
    elif a.cmd == "extra":
        lote = extra(a.lote, json.loads(a.pedidos.read_text(encoding="utf-8")), rede_autorizada=a.rede_autorizada)
        print("LOTE %s · %d pedidos a rede no total" % (lote["LOTE_ID"], lote["PEDIDOS_A_REDE"]))
    else:
        out = ingerir(a.lote, json.loads(a.respostas.read_text(encoding="utf-8")), propostas=a.propostas)
        print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
