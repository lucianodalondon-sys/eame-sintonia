# -*- coding: utf-8 -*-
"""O contador de pedidos por DOMINIO numa janela de 24 h (D90 §3.1/§3.4), partilhado pelas tres
ferramentas desta pasta (seguir.py, orcid_lote.py, listas_oficiais.py).

    orcid.org          <= 5 pedidos por 24 h (D90: «<=5 pedidos orcid.org/24 h»)
    qualquer outro     <= 5 pedidos por 24 h (as paginas das universidades «espalhadas por dias»)

Cada pedido que sai e escrito no ficheiro ANTES de sair (quem cai a meio nao devolve o pedido: conta
contra nos, nunca a favor). Quem nao cabe recebe ADIADO_ATE (quando o pedido mais antigo da janela sai
dela) e NAO pede.

Guarda tambem o robots.txt lido de cada host por 24 h: o 2.o dia nao gasta um dos 5 pedidos a relê-lo.

⚠️ NAO e o «contador multicanal atomico» da D90 §2: e um ficheiro, sem trava entre processos. Vale
porque a D90 manda uma linha de rede de cada vez. Duas destas ferramentas a correr ao mesmo tempo
podem passar o teto.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

JANELA = timedelta(hours=24)
TETO_24H = {"orcid.org": 5}
TETO_24H_PADRAO = 5
CONTADOR_PADRAO = Path("C:/Users/London1/sintonia-sala-italia/seguir-pesquisadores/CONTADOR-24H.json")


def _iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).isoformat(timespec="seconds")


class Contador24h:
    def __init__(self, arq: Path, agora=None):
        self.arq = Path(arq)
        self._agora = agora or (lambda: datetime.now(timezone.utc))
        d = json.loads(self.arq.read_text(encoding="utf-8")) if self.arq.exists() else {}
        self.pedidos = d.get("PEDIDOS") or []
        self.robots = d.get("ROBOTS") or {}

    def _gravar(self):
        self.arq.parent.mkdir(parents=True, exist_ok=True)
        corte = self._agora() - JANELA * 7                  # guarda uma semana de historia, nao para sempre
        self.pedidos = [p for p in self.pedidos if datetime.fromisoformat(p["EM"]) >= corte]
        self.arq.write_text(json.dumps({"JANELA_H": 24, "TETO_24H": TETO_24H, "TETO_24H_PADRAO": TETO_24H_PADRAO,
                                        "PEDIDOS": self.pedidos, "ROBOTS": self.robots},
                                       ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    def teto(self, dominio: str) -> int:
        return TETO_24H.get(dominio, TETO_24H_PADRAO)

    def na_janela(self, dominio: str) -> list:
        desde = self._agora() - JANELA
        return sorted(datetime.fromisoformat(p["EM"]) for p in self.pedidos
                      if p["DOMINIO"] == dominio and datetime.fromisoformat(p["EM"]) > desde)

    def livres(self, dominio: str) -> int:
        return max(0, self.teto(dominio) - len(self.na_janela(dominio)))

    def proximo_livre(self, dominio: str):
        """Quando volta a haver um pedido livre (ISO), ou None se ja ha."""
        usados = self.na_janela(dominio)
        if len(usados) < self.teto(dominio):
            return None
        return _iso(usados[len(usados) - self.teto(dominio)] + JANELA)

    def reservar(self, dominio: str, url: str):
        """(True, None) e o pedido fica escrito; ou (False, ADIADO_ATE) e nao se pede."""
        usados = self.na_janela(dominio)
        if len(usados) >= self.teto(dominio):
            return False, self.proximo_livre(dominio)
        self.pedidos.append({"DOMINIO": dominio, "URL": url, "EM": _iso(self._agora())})
        self._gravar()
        return True, None

    def marcar_gasto(self, dominio: str, ate: datetime, porque: str) -> int:
        """Pedidos feitos FORA deste contador (outra linha, outro dia): enche o teto ate `ate`, para que nada
        daqui peca antes disso. Devolve quantas linhas escreveu."""
        # so conta o que ainda estara na janela em `ate`: um pedido que sai antes nao pode abrir vaga mais cedo
        n = max(0, self.teto(dominio) - sum(1 for u in self.na_janela(dominio) if u >= ate - JANELA))
        for _ in range(n):
            self.pedidos.append({"DOMINIO": dominio, "URL": "EXTERNO", "EM": _iso(ate - JANELA), "PORQUE": porque})
        if n:
            self._gravar()
        return n

    def robots_de(self, host: str):
        """O robots guardado ha menos de 24 h: (http, texto) ou None."""
        r = self.robots.get(host)
        if r and self._agora() - datetime.fromisoformat(r["EM"]) < JANELA:
            return r["HTTP"], r["TEXTO"]
        return None

    def guardar_robots(self, host: str, http, texto):
        self.robots[host] = {"HTTP": http, "TEXTO": texto, "EM": _iso(self._agora())}
        self._gravar()


if __name__ == "__main__":
    import sys
    a = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    if "--marcar-gasto" in sys.argv:
        c = Contador24h(Path(a.get("contador") or CONTADOR_PADRAO))
        n = c.marcar_gasto(a["dominio"], datetime.fromisoformat(a["ate"]), a.get("porque", "externo"))
        print("linhas EXTERNO escritas:", n, "| livres agora em", a["dominio"], "=", c.livres(a["dominio"]),
              "| proximo livre:", c.proximo_livre(a["dominio"]))
