# -*- coding: utf-8 -*-
"""LINHA-BUSCA · 1) as CONSULTAS — assunto-primeiro, a partir do que o casco e a Intelligence pedem. SEM REDE.

Duas origens, as duas declaradas em cada consulta (campo ORIGEM):
  CASCO   as ferramentas do casco (auditoria-madrugada/FERRAMENTAS-DO-CASCO.md) cruzam
          cultura x problema x regiao x janela. Os pares cultura x problema vem do vocabulario do
          DONO (`motor/matriz_recorte.py`: CROPS x ISSUES), com os termos de busca em italiano;
          a BUSCA-LOTE-0 (27/09) acrescentou dois pares que a matriz ainda nao tem (cimice
          asiatica, mosca delle olive — esta ja e OLIVE_PESTS) e que deram paginas de ouro.
  R3      as lacunas da Intelligence R3 (`LACUNAS-PARA-A-COLETA-R3.json`): familias nunca
          amostradas (T1, T4, T6, T8, T11, T12) viram consultas de familia.
Cada consulta leva a ferramenta, o universo (T) em que a pagina vai a Admission e o mes/ano da
janela (o mes corrente por omissao: o que o dono quer e o que esta a acontecer).
"""
import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "motor"))

MESES = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre",
         "ottobre", "novembre", "dicembre"]
REGIOES = ["Piemonte", "Valle d'Aosta", "Lombardia", "Trentino-Alto Adige", "Veneto", "Friuli Venezia Giulia",
           "Liguria", "Emilia-Romagna", "Toscana", "Umbria", "Marche", "Lazio", "Abruzzo", "Molise",
           "Campania", "Puglia", "Basilicata", "Calabria", "Sicilia", "Sardegna"]

# cultura (chave do dono) -> termo italiano de busca
CULTURA_IT = {"VINE": "vite", "OLIVE": "olivo", "CEREAL": "frumento", "DURUM_WHEAT": "grano duro",
              "MAIZE": "mais", "FRUTTA": "frutta"}
# problema (chave do dono) -> termo italiano de busca
PROBLEMA_IT = {"DOWNY_MILDEW": "peronospora", "FLAVESCENCE": "flavescenza dorata", "OLIVE_PESTS": "mosca delle olive",
               "XYLELLA": "xylella", "REPILO": "occhio di pavone", "SEPTORIA": "septoria",
               "FUSARIUM": "fusariosi", "RUST": "ruggine", "CIMICE": "cimice asiatica"}
# os pares que fazem sentido agronomico (a matriz do dono nao diz quais: escolhidos aqui e declarados)
PARES = [("VINE", "DOWNY_MILDEW"), ("VINE", "FLAVESCENCE"), ("OLIVE", "OLIVE_PESTS"), ("OLIVE", "XYLELLA"),
         ("OLIVE", "REPILO"), ("CEREAL", "SEPTORIA"), ("CEREAL", "FUSARIUM"), ("CEREAL", "RUST"),
         ("DURUM_WHEAT", "FUSARIUM"), ("MAIZE", "FUSARIUM"), ("FRUTTA", "CIMICE")]
PAR_FORA_DA_MATRIZ = {("FRUTTA", "CIMICE"): "BUSCA-LOTE-0 (27/09): rede cimice Campania; a matriz do dono nao tem CIMICE"}

# as formas que a pagina de ouro tem (medido na BUSCA-LOTE-0: boletim, catture, soglia)
FORMAS = [("bollettino fitosanitario {cultura} {problema} {mes} {ano}", "T3", "Finestre Colturali"),
          ("{problema} {cultura} catture trappole {regiao} {ano}", "T3", "Radar delle Opportunita"),
          ("{problema} {cultura} {regiao} {mes} {ano} bollettino", "T3", "Finestre Colturali")]

# R3: familias nunca amostradas -> consulta de familia (sem par; a regiao entra quando faz sentido)
FAMILIAS_R3 = {
    "T1": ("fase fenologica {cultura} {regiao} {mes} {ano}", "Finestre Colturali"),
    "T4": ("etichetta registrata prodotto fitosanitario {problema} {cultura}", "Label Intelligence"),
    "T6": ("ricercatore {problema} {cultura} sperimentazione {ano}", "Intelligence Scientifica"),
    "T8": ("agronomo tecnico {problema} {cultura} video {mes} {ano}", "Voci dal Campo"),
    "T11": ("convegno giornata tecnica {problema} {cultura} {ano}", "Radar Futuro"),
    "T12": ("decreto regione {problema} {cultura} {ano} misure", "Radar Futuro"),
}


def _matriz():
    try:
        import matriz_recorte as M                                    # o vocabulario do dono
        return set(M.CROPS), set(M.ISSUES)
    except Exception:                                                 # noqa: BLE001
        return set(), set()


def gerar(mes: int = None, ano: int = None, regioes: list = None, familias_r3: list = None) -> list:
    hoje = date.today()
    mes, ano = mes or hoje.month, ano or hoje.year
    regioes = regioes or REGIOES
    culturas_dono, problemas_dono = _matriz()
    out = []

    def add(texto, t, ferramenta, origem, par, regiao):
        texto = " ".join(texto.split())
        if any(q["CONSULTA"] == texto for q in out):          # a mesma consulta nao se gasta duas vezes
            return
        cid = "Q%04d" % (len(out) + 1)
        out.append({"CONSULTA_ID": cid, "CONSULTA": texto, "UNIVERSO": t,
                    "FERRAMENTA": ferramenta, "ORIGEM": origem, "PAR": par, "REGIAO": regiao,
                    "JANELA": "%04d-%02d" % (ano, mes)})
    for (c, p) in PARES:
        origem = "CASCO (matriz do dono: %s x %s)" % (c, p) if (c in culturas_dono and p in problemas_dono) \
            else "CASCO (%s)" % PAR_FORA_DA_MATRIZ.get((c, p), "par declarado aqui")
        for forma, t, ferr in FORMAS:
            regs = [None] if "{regiao}" not in forma else regioes
            for r in regs:
                add(forma.format(cultura=CULTURA_IT[c], problema=PROBLEMA_IT[p], mes=MESES[mes - 1], ano=ano,
                                 regiao=r or ""), t, ferr, origem, "%s x %s" % (c, p), r)
    for t in (familias_r3 or []):
        forma, ferr = FAMILIAS_R3[t]
        for (c, p) in PARES[:4]:
            # familia R3 vai nacional (sem regiao): e para ACHAR a familia, nao para a mapear
            add(forma.format(cultura=CULTURA_IT[c], problema=PROBLEMA_IT[p], mes=MESES[mes - 1], ano=ano,
                             regiao=""), t, ferr, "R3 (familia %s nunca amostrada)" % t, "%s x %s" % (c, p), None)
    return out


def familias_da_r3(caminho: Path) -> list:
    d = json.loads(Path(caminho).read_text(encoding="utf-8"))
    return sorted({l["T"] for l in d["LACUNAS"] if l.get("TIPO") == "FAMILIA_NUNCA_AMOSTRADA" and l.get("T") in FAMILIAS_R3})


def prioridade(consultas: list) -> list:
    """Ordem de gasto (o motor de busca tambem tem teto de 5 pedidos/24 h): primeiro o boletim nacional de
    cada par (1 consulta cobre as 20 regioes), depois as familias R3, e so depois as regionais."""
    def chave(q):
        return (0 if q["REGIAO"] is None and q["ORIGEM"].startswith("CASCO") else
                1 if q["ORIGEM"].startswith("R3") else 2, q["CONSULTA_ID"])
    return sorted(consultas, key=chave)
