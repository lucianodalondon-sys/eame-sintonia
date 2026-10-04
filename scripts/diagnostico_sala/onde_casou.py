"""DIAGNOSTICO-SALA-V1 — onde cada palavra da regua casou: corpo ou moldura.

SO LE. Separa o texto derivado em MOLDURA (menu/cabecalho/rodape do site) e
CORPO (a noticia). O corpo comeca na ULTIMA ocorrencia do titulo antes do
meio do texto e acaba no primeiro marcador de rodape conhecido. Regra
declarada, grosseira de proposito, e por isso o relatorio mostra o trecho.

    py scripts/diagnostico_sala/onde_casou.py <os76.json> <juncao.tsv> <raiz> <saida.json>
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
from admissao import admissao as adm  # noqa: E402

RODAPE = ["Legal Codice etico", "Potrebbe interessarti", "Articoli correlati",
          "Related Posts", "RELATED ARTICLES", "Leggi anche", "MORE STORIES",
          "Condividi", "P.IVA", "Partita IVA", "©"]


def corpo(texto, titulo):
    t = adm._dobrar(texto)
    chave = adm._dobrar(titulo)[:35]
    ini = 0
    pos = [m.start() for m in re.finditer(re.escape(chave), t)] if chave else []
    pos = [p for p in pos if p < len(t) * 0.8]
    if pos:
        ini = pos[-1]
    fim = len(t)
    for r in RODAPE:
        j = t.find(adm._dobrar(r), ini + 200)
        if j != -1:
            fim = min(fim, j)
    return ini, fim


def contexto(t, w, n=60):
    i = t.find(w)
    return t[max(0, i - n): i + len(w) + n].replace("\n", " / ") if i >= 0 else ""


def main(os76, tsv, raiz, saida):
    L = json.loads(Path(os76).read_text(encoding="utf-8"))
    caminho = {int(r.split("\t")[0]): r.split("\t")[4]
               for r in Path(tsv).read_text(encoding="utf-8").splitlines()}
    out = []
    for o in L:
        texto = (Path(raiz) / caminho[o["derived"]]).read_text(encoding="utf-8")
        titulo = texto.split("\n", 1)[0].split(" - ")[0].split(" | ")[0].strip()
        t = adm._dobrar(texto)
        ini, fim = corpo(texto, titulo)
        cp = t[ini:fim]
        palavras = set(o["escrito_palavras"])
        for ws in o["escrito_noutro"].values():
            palavras |= set(ws)
        for u in ("T7",):
            palavras |= set(o["leituras"][u]["palavras"])
        onde = {}
        for w in sorted(palavras):
            wd = adm._dobrar(w)
            onde[w] = {"no_corpo": wd in cp, "na_moldura": wd in (t[:ini] + t[fim:]),
                       "contexto": contexto(cp if wd in cp else t, wd)}
        out.append(dict(derived=o["derived"], source_id=o["source_id"],
                        escrito=o["escrito"], titulo=titulo,
                        corpo_caracteres=fim - ini, corpo_inicio=cp[:400],
                        onde=onde))
    Path(saida).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("itens", len(out))


if __name__ == "__main__":
    main(*sys.argv[1:5])
