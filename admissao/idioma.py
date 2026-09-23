"""EM QUE LINGUA ESTA O TEXTO — para a porta aplicar a MESMA regua na lingua do texto.

D3 do dono (23/09/2026): conteudo legivel em lingua estrangeira NAO pode, sozinho,
produzir NAO_SEI. A porta so conhecia palavras em italiano e portugues; um texto
inteiro em ingles nunca casava nada e caia em NAO_SEI «por idioma».

Este leitor nao decide nada: so diz a lingua, ou NAO SEI. E grosseiro de
proposito e declarado: conta as palavras-funcao mais frequentes de cada lingua
(artigos, preposicoes, conjuncoes) — as que nenhum menu, marca ou nome proprio
consegue imitar em quantidade.

    DECIDE SO COM MARGEM: >= MINIMO_DE_SINAIS palavras-funcao da lingua vencedora
    e pelo menos MARGEM vezes as da segunda. Senao, NAO_SEI — e a porta fica
    exactamente como estava antes deste ficheiro existir.
"""
from __future__ import annotations

import re

NAO_SEI = "NAO_SEI"

# Palavras-funcao, curtas e muito frequentes, sem colisao grave entre as linguas
# desta casa. Palavras que duas linguas partilham (`a`, `e`, `de`, `la`, `en`,
# `no`, `se`, `da`, `do`) ficam DE FORA: contavam para as duas e so baralhavam.
FUNCAO = {
    "it": {"il", "della", "delle", "dei", "degli", "nel", "nella", "che", "per", "con",
           "sono", "gli", "questo", "questa", "anche", "alla", "dalla", "non", "piu", "del"},
    "en": {"the", "and", "of", "to", "is", "for", "with", "that", "are", "on",
           "this", "from", "by", "was", "were", "have", "has", "which", "their", "its"},
    "pt": {"o", "os", "uma", "para", "com", "que", "nao", "pelo", "pela", "dos",
           "das", "foi", "sao", "mais", "tambem", "ao", "aos", "isso", "esta", "seu"},
    "fr": {"le", "les", "des", "du", "une", "est", "pour", "dans", "sur", "avec",
           "qui", "pas", "sont", "ces", "cette", "aux", "leur", "ont", "mais", "ou"},
    "es": {"el", "los", "las", "del", "una", "para", "con", "por", "que", "es",
           "son", "esta", "este", "como", "pero", "sus", "fue", "han", "hay", "muy"},
    "de": {"der", "die", "das", "und", "ist", "mit", "den", "von", "zu", "auf",
           "fur", "nicht", "eine", "sich", "dem", "des", "im", "auch", "wird", "sind"},
}
MINIMO_DE_SINAIS = 20
MARGEM = 1.5

# As linguas em que a porta TEM regua. Qualquer outra, detectada com margem, e
# IDIOMA_NAO_SUPORTADO — dito, nao silencioso. Nao se finge suporte.
SUPORTADAS = ("it", "pt", "en")


def _dobrar(texto: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", str(texto).lower())
                   if not unicodedata.combining(c))


def contagem(texto: str) -> dict:
    pal = re.findall(r"[a-z]+", _dobrar(texto))
    return {lg: sum(1 for p in pal if p in ws) for lg, ws in FUNCAO.items()}


def idioma(texto: str) -> str:
    """'it' | 'en' | 'pt' | 'fr' | 'es' | 'de' | NAO_SEI."""
    c = contagem(texto)
    ordem = sorted(c, key=c.get, reverse=True)
    a, b = c[ordem[0]], c[ordem[1]]
    if a >= MINIMO_DE_SINAIS and a >= MARGEM * max(b, 1):
        return ordem[0]
    return NAO_SEI


def _texto_de(f) -> str:
    b = f.read_bytes().decode("utf-8", "replace")
    if f.suffix.lower() in (".html", ".htm"):
        b = re.sub(r"<(script|style)\b.*?</\1\s*>", " ", b, flags=re.I | re.S)
        b = re.sub(r"<[^>]+>", " ", b)
    return b


def medir(pastas: list) -> dict:
    """Conta a lingua de cada ficheiro .txt/.html das pastas. So le."""
    from collections import Counter
    from pathlib import Path
    out = {}
    for p in pastas:
        fs = [f for f in Path(p).rglob("*") if f.suffix.lower() in (".txt", ".html", ".htm")]
        out[str(p)] = dict(Counter(idioma(_texto_de(f)) for f in fs))
    return out


if __name__ == "__main__":
    import json
    import sys
    print(json.dumps(medir(sys.argv[1:]), ensure_ascii=False, indent=1))
