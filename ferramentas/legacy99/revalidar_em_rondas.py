# -*- coding: utf-8 -*-
"""LEGACY-99 · revalidar READY_LEGACY pela regua DETAIL/v1, pelo caminho CANONICO, NUMA COPIA.

Caminho canonico (o mesmo do vivo, nada a mao):
    curadoria/ready_split.py `remedir()`  -> CANARY_PENDING + VALIDATE_ROUTE
    curadoria/worker.py VALIDATE_ROUTE -> CANARY (canario_html abre um item e retrata-o)
    promocao pelo worker so com a regua de hoje (ready_split.passos_da_promocao: DETAIL/v1)
Nao corre o reparo de contrato (REPAIR_CONTRACT): revalidar e medir o contrato que ha.

As guardas desta copia (D41.3 e D38), dentro deste processo:
  * `urllib.request.urlopen` embrulhado: com --rede FECHADA qualquer pedido falha logo
    (REDE_FECHADA); com --rede ABERTA cada pedido conta para o dominio registavel e o
    6.o pedido ao mesmo dominio numa rodada e recusado (TETO_D38) — nao se confia so
    na escolha das rodadas, conta-se;
  * rodadas com no maximo UMA fonte por dominio registavel; a fila da copia so tem,
    em cada rodada, as tarefas dessas fontes (as outras ficam guardadas e voltam depois);
  * com rede, o portao de consenso do vivo (superficie/rede.py) antes de cada rodada:
    sem PASS a rodada nao sai e o script para.

Uso: py ferramentas/legacy99/revalidar_em_rondas.py --copia C:/rend/copia-legacy
        --ids IT-..,IT-.. --rede FECHADA|ABERTA --saida X.json [--pausa-entre-rondas 60]
        [--portao <arvore do bot vivo>] [--reparar]
"""
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# o dominio registavel: a regra do coletor da ONDA2-G3 (`dominioRegistavel`), a mesma
# de `curadoria/prova_rota_ciclo.py` (ramo prova-rota-ciclo-v1)
SUFIXOS = frozenset({
    "gov.it", "edu.it", "abruzzo.it", "abr.it", "basilicata.it", "bas.it", "calabria.it", "cal.it",
    "campania.it", "cam.it", "emilia-romagna.it", "emiliaromagna.it", "emr.it", "friuli-venezia-giulia.it",
    "friuli-vgiulia.it", "friulivenezia-giulia.it", "friulivgiulia.it", "fvg.it", "lazio.it", "laz.it",
    "liguria.it", "lig.it", "lombardia.it", "lom.it", "marche.it", "mar.it", "molise.it", "mol.it",
    "piemonte.it", "pmn.it", "puglia.it", "pug.it", "sardegna.it", "sar.it", "sicilia.it", "sic.it",
    "toscana.it", "tos.it", "trentino.it", "trentino-alto-adige.it", "trentinoaltoadige.it", "taa.it",
    "umbria.it", "umb.it", "valledaosta.it", "valle-daosta.it", "vda.it", "vao.it", "veneto.it", "ven.it",
    "co.uk", "org.uk", "ac.uk", "gov.uk", "com.br", "org.br", "gov.br", "com.au", "org.au", "co.jp",
    "com.es", "com.pt", "co.nz", "com.ar", "com.mx"})
TETO_D38 = 5


def dominio(host: str) -> str:
    h = str(host or "").lower()
    h = (h[4:] if h.startswith("www.") else h).rstrip(".")
    p = [x for x in h.split(".") if x]
    if len(p) <= 2:
        return ".".join(p)
    return ".".join(p[-3:]) if ".".join(p[-2:]) in SUFIXOS else ".".join(p[-2:])


class Transporte:
    """Embrulha urlopen: fecha a rede, ou conta e aplica o teto por dominio."""

    def __init__(self, aberta: bool):
        self.aberta, self.pedidos, self.recusados = aberta, Counter(), Counter()
        self._orig = urllib.request.urlopen
        urllib.request.urlopen = self._urlopen

    def nova_rodada(self):
        self.pedidos = Counter()

    def _urlopen(self, req, *a, **kw):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        d = dominio(urlparse(url).hostname)
        if not self.aberta:
            self.recusados["REDE_FECHADA:" + d] += 1
            raise urllib.error.URLError("REDE_FECHADA (D41.3): copia sem rede")
        if self.pedidos[d] >= TETO_D38:
            self.recusados["TETO_D38:" + d] += 1
            raise urllib.error.URLError("TETO_D38: %s ja levou %d pedidos nesta rodada" % (d, TETO_D38))
        self.pedidos[d] += 1
        return self._orig(req, *a, **kw)


def portao(bot: Path) -> tuple[bool, str]:
    try:
        r = subprocess.run([sys.executable, "superficie/rede.py", "--portao-de-egresso", "IT"], cwd=bot,
                           capture_output=True, text=True, timeout=180)
        v = json.loads(r.stdout[r.stdout.index("{"):]).get("EGRESS_GATE")
    except Exception as e:  # noqa: BLE001
        return False, "sem resposta legivel: %r" % e
    return v == "PASS", "EGRESS_GATE=%s" % v


def main(argv):
    a = {k: argv[argv.index(k) + 1] for k in ("--copia", "--ids", "--rede", "--saida", "--pausa-entre-rondas", "--portao")
         if k in argv}
    copia = Path(a["--copia"]).resolve()
    if "source-curator-service-v1" in str(copia).replace("\\", "/"):
        print("RECUSO: a copia aponta para o bot vivo")
        return 2
    aberta = a["--rede"] == "ABERTA"
    bot = Path(a.get("--portao", "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1"))
    ids = [x for x in (Path(a["--ids"]).read_text().split(",") if Path(a["--ids"]).exists()
                       else a["--ids"].split(",")) if x.strip()]
    ids = [x.strip() for x in ids]
    T = Transporte(aberta)
    sys.path.insert(0, str(copia / "curadoria"))
    import fila as F              # noqa: E402
    import lifecycle as LC        # noqa: E402
    import worker as W            # noqa: E402
    import ready_split as RS      # noqa: E402
    import collection_gate as G   # noqa: E402
    import gatilho_discovery as GD  # noqa: E402
    reparar = "--reparar" in argv
    for p in (F.FILA, LC.LIVRO, W.CONTRATOS, W.EVIDENCIA):
        assert Path(p).resolve().is_relative_to(copia), p

    ctx = G._contexto()
    antes = {s: G.avaliar(s, **ctx)["MOTIVO"] for s in ids}
    # --reparar: o passo seguinte do ciclo do robo para as que falharam a revalidacao
    # (gatilho_discovery: CONTRACTED_CANARY_FAILED nunca reparada -> REPAIR_CONTRACT,
    # o reparo da R1), so para estas fontes e na mesma disciplina de rodadas.
    if reparar:
        feitas = []
        orig = GD.candidatas_a_reparar
        GD.requalificar_se_a_prova_mudou = lambda agora: []
    else:
        feitas = RS.remedir(ids, motivo=("LEGACY-99 25/09: revalidar READY_LEGACY pela regua DETAIL/v1 "
                                         "(so na copia)"))
    contratos = W._contratos()
    por_dom = {}
    for s in ids:
        aq = (contratos.get(s) or {}).get("ACQUISITION") or {}
        url = aq.get("INDEX_URL") or (contratos.get(s) or {}).get("CANONICAL_ENTRY_URL") or ""
        por_dom.setdefault(dominio(urlparse(url).hostname) or "?" + s, []).append(s)
    rondas = []
    for d, v in por_dom.items():
        for k, s in enumerate(v):
            while len(rondas) <= k:
                rondas.append([])
            rondas[k].append(s)

    registo = []
    for n, ronda in enumerate(rondas, 1):
        if aberta:
            ok, porque = portao(bot)
            if not ok:
                registo.append({"RONDA": n, "SAIU": False, "PORQUE": porque, "FONTES": ronda})
                print("RONDA %d NAO SAIU: %s" % (n, porque), flush=True)
                break
        T.nova_rodada()
        q = json.loads(Path(F.FILA).read_text(encoding="utf-8"))
        guardadas = [t for t in q["TAREFAS"] if t.get("SOURCE_ID") not in ronda]
        q["TAREFAS"] = [t for t in q["TAREFAS"] if t.get("SOURCE_ID") in ronda]
        Path(F.FILA).write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")
        passos = []
        if reparar:
            GD.candidatas_a_reparar = (lambda r: lambda agora, **kw: [c for c in orig(agora, **kw)
                                                                   if c["SOURCE_ID"] in r])(set(ronda))
        for _ in range(8):
            if reparar:
                GD.reparar_encalhadas(datetime.now(timezone.utc))
            feitos = W.correr(pausa=1.0, verboso=False)
            passos += [{k: f.get(k) for k in ("SOURCE_ID", "TASK_TYPE", "RESULTADO") if k in f} for f in feitos]
            if not feitos:
                break
        q = json.loads(Path(F.FILA).read_text(encoding="utf-8"))
        q["TAREFAS"] = q["TAREFAS"] + guardadas
        Path(F.FILA).write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")
        registo.append({"RONDA": n, "SAIU": True, "FONTES": ronda, "PEDIDOS_POR_DOMINIO": dict(T.pedidos),
                        "PASSOS": passos})
        print("RONDA %d: %d fontes, %d pedidos, maximo por dominio %d" % (
            n, len(ronda), sum(T.pedidos.values()), max(T.pedidos.values() or [0])), flush=True)
        if aberta and n < len(rondas):
            time.sleep(float(a.get("--pausa-entre-rondas", 60)))

    ctx = G._contexto()
    depois = {s: G.avaliar(s, **ctx) for s in ids}
    livro = json.loads(Path(LC.LIVRO).read_text(encoding="utf-8"))["TRANSICOES"]
    ultima = {}
    for t in livro:
        if t.get("SOURCE_ID") in ids:
            ultima[t["SOURCE_ID"]] = t
    fontes = []
    for s in ids:
        l = depois[s]
        u = ultima.get(s) or {}
        if l["COLLECTION_ELIGIBLE"]:
            res = "READY_CURRENT_E_ELEGIVEL"
        elif l["STATE"] == LC.READY_FOR_COLLECTION and l["READY_RULE"] == "DETAIL/v1":
            res = "READY_CURRENT_MAS_FORA:" + l["MOTIVO"]
        elif u.get("NEW_STATE") in (LC.CANARY_PENDING,) and s not in {p["SOURCE_ID"] for r in registo for p in r.get("PASSOS", [])}:
            res = "NAO_SEI:nao correu"
        else:
            res = "FALHOU"
        fontes.append({"SOURCE_ID": s, "ANTES": antes[s], "RESULTADO": res, "ESTADO": l["STATE"],
                       "REGUA": l["READY_RULE"], "MOTIVO_DO_PORTAO": l["MOTIVO"],
                       "ULTIMA_RAZAO": (u.get("REASON") or u.get("MOTIVO") or "")[:240]})
    d = {"DATASET": "LEGACY-99-REVALIDAR-EM-COPIA", "MEDIDO_EM": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "COPIA": str(copia), "REDE": "ABERTA" if aberta else "FECHADA", "MODO": "REPARAR" if reparar else "REVALIDAR", "REMEDIR": feitas,
         "RONDAS": registo, "RECUSADOS_PELO_TRANSPORTE": dict(T.recusados),
         "RESUMO": dict(Counter(f["RESULTADO"].split(":")[0] for f in fontes)), "FONTES": fontes}
    Path(a["--saida"]).write_text(json.dumps(d, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("RESUMO", d["RESUMO"], "| recusados", dict(T.recusados))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
