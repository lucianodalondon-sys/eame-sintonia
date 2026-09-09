#!/usr/bin/env python3
"""O QUE O BROWSER RECEBE E NUNCA LE.

    DISPLAY INPUT != COMPUTATION INPUT.

O SINTONIA nao corre o motor no browser: medido em 2026-09-09, nao ha uma unica
funcao de pontuacao, peso ou limiar no cliente publicado. O que viaja e o
CORPUS que produziu a resposta — e, dentro dele, os campos internos do metodo:
como uma proveniencia foi recuperada, porque uma evidencia conta, o que uma
ligacao significa. Sao esses que ensinam a receita.

Este modulo compara os campos que existem nos pacotes publicados com os campos
que o codigo de interface efectivamente le, e devolve a diferenca.

    UM CAMPO QUE NINGUEM LE NAO E APRESENTACAO. E EXPORTACAO.

Nao apaga nada: mede. A poda faz-se no gerador que escreve o pacote, que e onde
a decisao tem dono.

Uso:
    python3 security/projeccao.py            # relatorio
    python3 security/projeccao.py --json     # dados
    python3 security/projeccao.py --congelar # regrava a divida conhecida
"""
import json, os, pathlib, re, sys
from collections import Counter

RAIZ = pathlib.Path(os.environ.get("SINTONIA_RATCHET_RAIZ") or
                    pathlib.Path(__file__).resolve().parent.parent)
CONGELADO = pathlib.Path(__file__).resolve().parent / "projeccao-baseline.json"

# Pacotes de DADOS: transportam, nao decidem. Sao estes que se medem.
# O resto do cliente e codigo de interface, e e nele que se procura quem le.
PACOTES = re.compile(
    r"/(italy-v21|italy-handoff-v21|italy-ingested|italy-casa|italy-demo-data|"
    r"italy-real-intelligence|italy-canonical-windows|italy-catalog|"
    r"adama-relevance|italy-label-intelligence|italy-label-verdicts|"
    r"meeting-intelligence-snapshot)\.js$")
VENDOR = re.compile(r"/vendor/|/_ds/")


def campos_de(texto, limite=6000):
    """Os nomes de campo dentro de um pacote `window.X = {...}`."""
    # `window.X =` pode ser seguido de espaco, nova linha ou indentacao antes
    # do `{`. A primeira versao exigia que o `{` viesse colado, e por isso
    # declarou "ilegivel" o maior pacote de todos — 11 MB — sem que nada
    # falhasse. Um medidor que nao consegue ler o maior caso e um medidor que
    # da uma resposta tranquilizadora e errada.
    #
    #     NAO CONSEGUI LER != NAO HA NADA PARA LER.
    m = re.search(r"window\.[A-Za-z_0-9]+\s*=\s*", texto)
    if not m:
        return None
    resto = texto[m.end():].lstrip()
    # Quatro formas diferentes de embrulhar a mesma coisa, e todas tem de ser
    # lidas — senao o maior pacote de todos fica de fora do censo em silencio.
    #   {...}      JSON puro
    #   R({...})   JSON dentro de uma chamada
    #   { a, B }   literal de JavaScript, com atalhos e chaves sem aspas
    envolto = resto.startswith("R(")
    if envolto:
        resto = resto[2:].lstrip()
    if resto[:1] not in ("{", "["):
        return None, "sem carga reconhecivel"
    desl = m.end() + (len(texto[m.end():]) - len(resto))
    fim = texto.rfind("}" if resto[0] == "{" else "]")
    fs = Counter()
    try:
        d = json.loads(texto[desl:fim + 1])
        como = "json"

        def anda(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    fs[k] += 1
                    anda(v)
            elif isinstance(o, list):
                for v in o[:limite]:
                    anda(v)
        anda(d)
    except Exception:
        # Literal de JavaScript: nao se interpreta, contam-se as chaves. E menos
        # exacto do que analisar, e e muito melhor do que declarar ilegivel.
        #
        #     NAO CONSEGUI LER != NAO HA NADA PARA LER.
        como = "chaves"
        # Nestes ficheiros o `window.X = { a, B, C }` e so um atalho: os registos
        # vivem em `const` declarados ACIMA. Cortar a partir do `window` via
        # oito nomes e nenhum campo — e dava a resposta mais tranquilizadora
        # possivel, que era zero.
        #
        #     O QUE E SERVIDO E O FICHEIRO INTEIRO, E NAO A LINHA DO `window`.
        for k in re.findall(r'["\']?([A-Za-z_][A-Za-z_0-9]{2,})["\']?\s*:', texto):
            fs[k] += 1
    return fs, como


def medir(raiz=RAIZ):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from superficie_publica import superficie
    pub = superficie(raiz)["ficheiros"]

    pacotes = [f for f in pub if PACOTES.search(f)]
    # O codigo de interface e tudo o que e servido, e nao e pacote nem vendor.
    # Comentarios fora: um campo citado num comentario nao e um campo lido.
    codigo = []
    for f in pub:
        if PACOTES.search(f) or VENDOR.search(f) or not f.endswith((".js", ".html")):
            continue
        t = (raiz / f).read_text(encoding="utf-8", errors="replace")
        t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
        t = re.sub(r"^\s*//.*$", "", t, flags=re.M)
        codigo.append(t)
    codigo = "".join(codigo)

    out = {"pacotes": {}, "bytes_codigo_interface": len(codigo)}
    for f in sorted(pacotes):
        fs, como = campos_de((raiz / f).read_text(encoding="utf-8", errors="replace"))
        if fs is None:
            out["pacotes"][f] = {"erro": como}
            continue
        # UM IDENTIFICADOR NAO E UM CAMPO.
        # `OPP_75C37DED9160` e uma chave que aparece UMA vez; `PROVENANCE_STATE`
        # e um campo que aparece em cada registo. Contar identificadores como
        # campos inflava o numero e, pior, faria o portao gritar sempre que um
        # caso novo entrasse no pacote — o caminho mais curto para o desligarem.
        #
        #     UM CAMPO DE ESQUEMA REPETE-SE. UM IDENTIFICADOR NAO.
        fs = Counter({k: n for k, n in fs.items() if n >= 2})
        nao = sorted((k for k in fs if not re.search(r"[\"'.\[]" + re.escape(k) + r"\b", codigo)),
                     key=lambda k: -fs[k])
        out["pacotes"][f] = {"lido_como": como, "campos": len(fs), "lidos": len(fs) - len(nao),
                             "nao_lidos": nao,
                             "ocorrencias_nao_lidas": sum(fs[k] for k in nao),
                             "ocorrencias_totais": sum(fs.values())}
    return out


def chaves(m):
    return {f"{f}|{c}" for f, d in m["pacotes"].items() for c in d.get("nao_lidos", [])}


def main():
    m = medir()
    if "--json" in sys.argv:
        print(json.dumps(m, ensure_ascii=False, indent=2)); return 0
    if "--congelar" in sys.argv:
        CONGELADO.write_text(json.dumps(
            {"COMENTARIO": "Campos transportados ao browser e nao lidos por nenhuma linha de "
                           "interface. Estar aqui nao e aceite: e nao bloquear hoje. A poda "
                           "faz-se no gerador que escreve o pacote.",
             "CONGELADO_EM": "2026-09-09",
             "chaves": sorted(chaves(m))}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"congelado: {len(chaves(m))} campos transportados e nao lidos")
        return 0

    tot_n = tot_c = 0
    print(f"{'PACOTE':40} {'COMO':>7} {'CAMPOS':>7} {'LIDOS':>7} {'NAO LIDOS':>10}")
    for f, d in m["pacotes"].items():
        if "erro" in d:
            print(f"{f.split('/')[-1]:40} {d['erro']}"); continue
        tot_n += len(d["nao_lidos"]); tot_c += d["campos"]
        print(f"{f.split('/')[-1]:40} {d['lido_como']:>7} {d['campos']:7} {d['lidos']:7} {len(d['nao_lidos']):10}")
    print(f"\n{tot_n} de {tot_c} campos publicados nao sao lidos por nenhuma linha de interface.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
