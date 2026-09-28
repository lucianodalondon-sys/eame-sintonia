#!/usr/bin/env python3
"""REROUTE-T1T2 §3 · POR QUE `leis/fato_do_texto.corpo()` DEVOLVE 0 CARACTERES NAS PAGINAS CREA — so MEDIR.

SO LE. Nao muda o extrator nem o corpo: a correcao proposta e aplicada SO dentro deste script (uma funcao
local), para medir o que ela faria. Sem rede, sem banco.

Mede:
  A · no export da Sala (180 T5): quantos textos sao UMA LINHA so, e quantos desses dao corpo < 200
  B · no canario derived:1149: o que o `RODAPE` casa na linha unica (e por isso a deita fora inteira)
  C · o caminho do extrator (`coleta/texto_fonte.limpar`): HTML minificado (sem \\n entre tags) -> 1 linha
      -> corpo 0; o MESMO HTML com quebras de linha -> corpo com as frases
  D · a proposta (tags de bloco viram \\n ANTES de tirar as tags) sobre o HTML minificado

    py provas/reroute_t1t2/medir_corpo_vazio.py  -> provas/reroute_t1t2/MEDIDA-CORPO-VAZIO.json
"""
import collections
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

from coleta.texto_fonte import limpar  # noqa: E402
from leis import fato_do_texto as ft  # noqa: E402

AQUI = Path(__file__).resolve().parent
MINIMO = 200          # admissao.CORPO_MINIMO_DO_REROUTE

# Uma pagina no desenho das do CREA (menu, noticia, rodape institucional), minificada: nenhum \n.
PARTES = [
    "<header><nav><ul><li><a href='/'>Home</a></li><li><a href='/ricerca'>Barra di ricerca</a></li>"
    "<li>Il CREA</li><li>Seguici su</li></ul></nav></header>",
    "<main><h1>Xylella fastidiosa: dalla ricerca CREA nuove strategie per l'olivicoltura</h1>",
    "<p>Il progetto ha presentato i risultati finali attesi ed evidenziato le nuove varieta di olivo "
    "tolleranti alla malattia negli oliveti pugliesi.</p>",
    "<p>I ricercatori hanno seguito per tre anni la diffusione dell'insetto vettore e la risposta delle "
    "piante nei campi sperimentali della regione.</p></main>",
    "<footer><p>Via della Navicella 2, 00184 Roma - Partita IVA 08183101008 - C.F. 97231970589 - "
    "PEC crea@pec.crea.gov.it</p></footer>",
]
MINIFICADO = "<html><body>" + "".join(PARTES) + "</body></html>"
COM_QUEBRAS = "<html><body>\n" + "\n".join(PARTES) + "\n</body></html>"

#: A PROPOSTA (nao aplicada no repositorio): quebra de linha no fim de cada bloco, antes de tirar as tags.
BLOCOS = re.compile(r"<(?:br\s*/?|/(?:p|div|li|h[1-6]|tr|section|article|header|footer|nav|ul|ol|main|"
                    r"aside|blockquote|dd|dt|table|figcaption))\b[^>]*>", re.I)


def limpar_com_blocos(dados: bytes, ctype: str = "text/html") -> str:
    t = dados.decode("utf-8", errors="replace")
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    t = BLOCOS.sub("\n", t)
    return limpar(t.encode("utf-8"), ctype)


def medir(html: str, extrator) -> dict:
    texto = extrator(html.encode("utf-8"), "text/html")
    c = ft.corpo(texto)
    return {"LINHAS_DO_TEXTO": len(texto.splitlines()), "CARACTERES_DO_TEXTO": len(texto),
            "CARACTERES_DO_CORPO": len(c.strip()), "CORPO_SEPARAVEL": len(c.strip()) >= MINIMO,
            "CORPO": c[:400]}


def main() -> int:
    sala = json.loads((RAIZ / "docs" / "lab-insumos" / "reroute-prova" / "SALA-T5-EXPORT.json")
                      .read_text(encoding="utf-8"))
    por_fonte = collections.defaultdict(lambda: {"ITENS": 0, "UMA_LINHA": 0, "CORPO_MENOR_QUE_200": 0,
                                                 "UMA_LINHA_E_CORPO_VAZIO": 0})
    for x in sala:
        f = x["source_id"] if x["source_id"].startswith("IT-") else "EU-T5"
        uma = len(x["texto"].splitlines()) == 1
        vazio = len(ft.corpo(x["texto"]).strip()) < MINIMO
        g = por_fonte[f]
        g["ITENS"] += 1
        g["UMA_LINHA"] += uma
        g["CORPO_MENOR_QUE_200"] += vazio
        g["UMA_LINHA_E_CORPO_VAZIO"] += uma and vazio
    so_cegas = {k: v for k, v in sorted(por_fonte.items()) if v["CORPO_MENOR_QUE_200"]}
    canario = next(x for x in sala if x["item_id"] == "derived:1149")["texto"]
    out = {
        "MEDIDA": "MEDIDA-CORPO-VAZIO",
        "A_EXPORT_DA_SALA": {"ITENS": len(sala), "FONTES_COM_CORPO_MENOR_QUE_200": so_cegas},
        "B_CANARIO_1149": {"LINHAS": len(canario.splitlines()), "CARACTERES": len(canario),
                           "TITULO": ft.titulo(canario), "CORPO": ft.corpo(canario),
                           "RODAPE_CASA": sorted({m.group(0) for m in ft.RODAPE.finditer(canario)}),
                           "SEPARADORES_DE_MENU": len(ft._RE_SEPARADOR_DE_MENU.findall(canario))},
        "C_EXTRATOR_DE_HOJE": {"HTML_MINIFICADO": medir(MINIFICADO, limpar),
                               "O_MESMO_HTML_COM_QUEBRAS": medir(COM_QUEBRAS, limpar)},
        "D_PROPOSTA_BLOCOS_VIRAM_LINHA": {"HTML_MINIFICADO": medir(MINIFICADO, limpar_com_blocos),
                                          "O_MESMO_HTML_COM_QUEBRAS": medir(COM_QUEBRAS, limpar_com_blocos)},
        "NAO_SEI": ["os bytes HTML das paginas CREA/zootecnica NAO estao nesta arvore (o export traz so o texto): "
                    "que elas sao minificadas e INFERENCIA do codigo (limpar() so da 1 linha se nao houver \\n "
                    "entre os textos), nao medida nos bytes",
                    "zootecnica (IT-T10-022, 4 de 20): nao ha texto dela no export T5 — a causa e a mesma por "
                    "hipotese, nao medida"],
    }
    (AQUI / "MEDIDA-CORPO-VAZIO.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("A_EXPORT_DA_SALA", "C_EXTRATOR_DE_HOJE",
                                          "D_PROPOSTA_BLOCOS_VIRAM_LINHA")}, ensure_ascii=False, indent=1)[:4000])
    print(json.dumps({k: v for k, v in out["B_CANARIO_1149"].items() if k != "CORPO"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
