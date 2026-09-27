# -*- coding: utf-8 -*-
"""LACUNAS-PARA-FONTES · que perfis publicos cada fonte JA COLHIDA liga no seu proprio site. SEM REDE.

    py ferramentas/lacunas/varrer_sociais.py --saida=<SOCIAIS-NO-ARMAZEM.json>

Le (so leitura) as observacoes HTML guardadas no armazem (`raw_asset` com preserved) e tira os links para
YouTube (canal), Instagram, LinkedIn (company/school/showcase), Facebook, X/Twitter, Telegram, TikTok e
Spotify (programa). A prova de identidade de cada perfil e a propria pagina da fonte que o liga: endereco da
pagina + sha256 dos bytes guardados. Botoes de partilha (sharer, intent, share.php) nao sao perfil.
Demora (1.322 paginas; ~25 min nesta maquina).
"""
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ler_sala as LS                                                 # noqa: E402

ARMAZEM = os.path.expanduser("~/sintonia-sala-italia/armazem")
SOC = re.compile(r'href="(https?://(?:www\.|it\.)?(?:youtube\.com/(?:@[\w.-]+|channel/[\w-]+|c/[\w.-]+|user/[\w.-]+)|'
                 r'instagram\.com/[\w.]+|linkedin\.com/(?:company|school|showcase)/[\w%-]+|facebook\.com/[\w.%-]+|'
                 r'(?:twitter|x)\.com/[\w]+|t\.me/[\w]+|tiktok\.com/@[\w.]+|open\.spotify\.com/show/\w+))/?[^"]*"', re.I)
PARTILHA = re.compile(r"(sharer|share\?|intent/|/plugins/|dialog/|/embed)", re.I)


def varrer() -> dict:
    rows = LS.consultar("select source_id, source_url, storage_path, sha256 from public.raw_asset "
                        "where media_type like 'text/html%' and preserved")
    por = defaultdict(lambda: defaultdict(set))
    faltam = 0
    for linha in rows:
        sid, url, sp, sha = [x.strip() for x in linha.split(LS.SEP)]
        p = os.path.join(ARMAZEM, sp)
        if not os.path.exists(p):
            faltam += 1
            continue
        t = open(p, encoding="utf-8", errors="replace").read()
        for m in SOC.finditer(t):
            h = m.group(1).rstrip("/")
            if PARTILHA.search(h):
                continue
            por[sid][h].add((url, sha))
    return {"PAGINAS_HTML": len(rows), "FICHEIRO_EM_FALTA": faltam,
            "POR_FONTE": {sid: {h: sorted(v)[0] for h, v in d.items()} for sid, d in por.items()}}


if __name__ == "__main__":
    arg = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    r = varrer()
    Path(arg["saida"]).write_text(json.dumps(r, ensure_ascii=False, indent=0) + "\n", encoding="utf-8", newline="\n")
    print(r["PAGINAS_HTML"], "paginas;", r["FICHEIRO_EM_FALTA"], "sem ficheiro;", len(r["POR_FONTE"]), "fontes com perfis")
