#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEDE-FONTES · a sede provavel de cada fonte, tirada de PROVA PUBLICA JA GUARDADA (sem rede).

    py ferramentas/sede_fontes/medir_sede.py <coorte-60.json> <saida.json> <pasta-de-bytes>=<como> [...]

`<como>` = STORE (data/collection-store/italy/<SID>/<item>/<versao>/<ficheiro>) ou INDICE
(<pasta>/<SID>.html, os indices D40 guardados). So leitura.

O que conta como prova: uma MORADA italiana escrita na pagina — CAP de 5 digitos + comune + (SIGLA) —
de preferencia perto de «sede», «sede legale», «indirizzo», «contatti», «dove siamo». Por fonte:
  · junta as moradas de todas as paginas guardadas dela;
  · a candidata e a morada que aparece em MAIS PAGINAS diferentes (o rodape repete-se; o local de um
    evento aparece numa so);
  · SEDE_PROVAVEL so quando a candidata aparece em >= 2 paginas OU vem com a palavra «sede»; senao
    NAO SEI (com as moradas vistas, para quem decidir);
  · o comune e conferido contra o gazetteer de leis/fato_local.py (o mesmo que o contrato usa).
O que NUNCA conta: o REGION do Atlas (e cobertura/amostra, nao morada), o nome da instituicao.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from html import unescape
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
from leis import fato_local as FL  # noqa: E402

RE_TAG = re.compile(r"<script\b.*?</script>|<style\b.*?</style>|<[^>]+>", re.I | re.S)
# CAP + comune (1 a 4 palavras com maiuscula) + (SIGLA) opcional
RE_MORADA = re.compile(
    r"(?<!\d)(\d{5})\s*[-–,]?\s*((?:[A-ZÀ-Ý][A-Za-zÀ-ÿ'’]+)(?:[\s-]+(?:[A-ZÀ-Ý][A-Za-zÀ-ÿ'’]+|d[ie]l?|di|sul|in|a)){0,4})"
    r"\s*(?:\(\s*([A-Z]{2})\s*\))?")
RE_SEDE = re.compile(r"\bsede(?:\s+legale|\s+operativa|\s+centrale|\s+amministrativa)?\b|\bindirizzo\b|\bdove siamo\b|"
                     r"\bcontatti\b|\bheadquarters?\b|\bp\.?\s?iva\b", re.I)


PARAGEM = {"sede", "tel", "tel.", "telefono", "fax", "email", "e-mail", "mail", "pec", "codice", "partita", "p.iva",
           "piva", "c.f.", "cf", "centralino", "italia", "italy", "iscrizione", "registro", "cap", "numero",
           "orari", "contatti", "privacy", "copyright", "tutti", "via", "viale", "piazza", "questo", "in"}


def texto(b: bytes) -> str:
    t = b.decode("utf-8", "replace")
    return re.sub(r"\s+", " ", unescape(RE_TAG.sub(" ", t)))


def paginas(pastas, sid):
    for pasta, como in pastas:
        if como == "INDICE":
            p = pasta / (sid + ".html")
            if p.is_file():
                yield "INDICE:" + p.name, p.read_bytes()
        else:
            base = pasta / sid
            if not base.is_dir():
                continue
            for it in sorted(d for d in base.iterdir() if d.is_dir()):
                vs = sorted(v for v in it.iterdir() if v.is_dir())
                fich = [p for p in vs[-1].iterdir() if p.is_file()] if vs else []
                if fich and fich[0].read_bytes().lstrip()[:1] == b"<":
                    yield "STORE:" + it.name[:80], fich[0].read_bytes()


def main():
    coorte, saida = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")), Path(sys.argv[2])
    pastas = [(Path(a.split("=")[0]), a.split("=")[1]) for a in sys.argv[3:]]
    gaz = {n.lower(): (n, p) for n, p in FL.GAZETTEER}
    out = []
    for f in coorte["FONTES"]:
        sid = f["SOURCE_ID"]
        vistas = defaultdict(set)          # (cap, comune, sigla) -> {pagina}
        trechos, com_sede = {}, Counter()
        npag = 0
        for nome, b in paginas(pastas, sid):
            npag += 1
            t = texto(b)
            for m in RE_MORADA.finditer(t):
                # corta o que vem do rodape a seguir ao comune («Roma Sede», «Modena Tel», «Milano Codice Fiscale»)
                palavras = []
                for w in m.group(2).split():
                    if w.lower().strip(".,:;") in PARAGEM:
                        break
                    palavras.append(w)
                comune = " ".join(palavras).strip(" -")
                # so vale com a SIGLA da provincia entre parentesis, ou com o comune no gazetteer
                if not comune or not (m.group(3) or comune.lower() in gaz):
                    continue
                k = (m.group(1), comune, m.group(3) or "")
                vistas[k].add(nome)
                janela = t[max(0, m.start() - 160): m.end() + 40]
                trechos.setdefault(k, janela.strip())
                if RE_SEDE.search(janela):
                    com_sede[k] += 1
        cands = sorted(vistas, key=lambda k: (-len(vistas[k]), -com_sede[k], k))
        linha = {"SOURCE_ID": sid, "UNIVERSO": f.get("UNIVERSO"), "INDEX_URL": f.get("INDEX_URL"),
                 "PAGINAS_GUARDADAS_LIDAS": npag,
                 "MORADAS_VISTAS": [{"CAP": k[0], "COMUNE": k[1], "SIGLA": k[2] or None, "PAGINAS": len(vistas[k]),
                                     "PERTO_DE_SEDE": com_sede[k]} for k in cands[:5]]}
        if not npag:
            linha.update(SEDE_PROVAVEL="NAO SEI", BASE="NAO SEI — nenhuma pagina desta fonte guardada nesta maquina")
        elif not cands:
            linha.update(SEDE_PROVAVEL="NAO SEI", BASE="NAO SEI — %d paginas guardadas lidas, nenhuma morada com CAP" % npag)
        else:
            k = cands[0]
            forte = len(vistas[k]) >= 2 or com_sede[k] > 0
            empate = len(cands) > 1 and len(vistas[cands[1]]) == len(vistas[k]) and cands[1][1] != k[1] and len(vistas[k]) < 2
            g = gaz.get(k[1].lower())
            if forte and not empate:
                linha.update(SEDE_PROVAVEL="%s%s" % (k[1], " (%s)" % k[2] if k[2] else ""), CAP=k[0],
                             BASE="PAGINA_GUARDADA · morada em %d pagina(s)%s · %s" % (
                                 len(vistas[k]), ", junto de «sede/indirizzo/contatti»" if com_sede[k] else "",
                                 sorted(vistas[k])[0]),
                             TRECHO=trechos[k][-260:],
                             NO_GAZETTEER=("%s (%s)" % g if g else "NAO — o contrato daria NOT_IN_GAZETTEER"))
            else:
                linha.update(SEDE_PROVAVEL="NAO SEI",
                             BASE="NAO SEI — morada vista numa so pagina e sem «sede» perto%s" % (
                                 " (e empatada com outra)" if empate else ""),
                             TRECHO=trechos[k][-260:])
        out.append(linha)
        print(sid, npag, linha["SEDE_PROVAVEL"], "|", linha["BASE"][:90])
    saida.write_text(json.dumps({"DATASET": "SEDE-DAS-FONTES-COORTE-60-V1", "REDE": 0,
                                 "PASTAS": [str(p) + "=" + c for p, c in pastas], "FONTES": out},
                                ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
