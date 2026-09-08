# -*- coding: utf-8 -*-
"""CENSO DO CONGELAMENTO — o que a trava da inteligência tem de segurar.

O QUE ESTAVA ERRADO
-------------------
A primeira trava procurava **pastas com certos nomes** — `inteligencia`,
`opportunity`, `scoring` — não encontrava nenhuma, e daí eu escrevi:

    «zero áreas de inteligência implementadas»

**A afirmação era maior do que a prova.** Não havia pasta com esses nomes; havia
artefatos espalhados por outros sítios. `tests/test_radar_futuro.py` fala de
`SCIENTIFIC_SIGNAL`, `WATCHLIST_PRIORITY`, `PROMOTED_TO_RADAR`. Isso não torna a
inteligência ativa — torna a minha frase falsa.

A SEMÂNTICA CERTA
-----------------
Não se prova que a inteligência **não existe**. Prova-se que

    A INTELIGÊNCIA QUE JÁ EXISTIA NO MOMENTO DO CONGELAMENTO
    NÃO AVANÇOU.

Por isso este censo tira uma fotografia: cada artefato com o seu `sha256` de
blob do Git. Enquanto a coleta não fechar, essa fotografia não muda.

E ESPÉCIE NÃO É `grep`
----------------------
Um ficheiro de coleta que menciona «signal» num comentário não é inteligência.
Um JSON de amostra também não. O que se congela por espécie:

    IMPLEMENTATION   código operacional que calcula sinal, nota ou recomendação
    CONTRACT         o contrato que essa implementação promete cumprir
    TEST             a prova de um dos dois acima
    DATA_SAMPLE      dado congelado, resultado de um cálculo antigo
    DOCUMENTATION    prosa
    PORTAL_UI        tela
    MENCAO_FRACA     a palavra aparece, mas o ficheiro nao calcula nada
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# As marcas que denunciam inteligência. Não são todas iguais: `PROMOTED_TO_RADAR`
# e `WATCHLIST_PRIORITY` são de decisão; `SIGNAL` sozinho aparece em coleta.
MARCAS_FORTES = ("PROMOTED_TO_RADAR", "WATCHLIST_PRIORITY", "FIELD_VOICE",
                 "OPPORTUNITY_SCORE", "RECOMMENDATION")
MARCAS_FRACAS = ("OPPORTUNITY", "WATCHLIST", "SCORING", "SCIENTIFIC_SIGNAL",
                 "RESEARCHER_SIGNAL", "FIELD_SIGNAL", "RECOMMENDATIONS",
                 # ⚠️ ESTAS DUAS FALTAVAM, E A LEI JÁ AS PROIBIA.
                 # `leis/fundacao_da_coleta.py` congela seis áreas por nome.
                 # O censo procurava marcas para quatro delas. `SIGNALS` e
                 # `PORTAL_INTELLIGENCE_WIRING` estavam proibidas no papel e
                 # invisíveis na medição — uma trava com dois pontos cegos.
                 # Ficam FRACAS de propósito: «signal» aparece em ficheiro de
                 # coleta, e lá só conta se houver marca FORTE junto.
                 "SIGNAL", "PORTAL_INTELLIGENCE", "INTELLIGENCE_WIRING")
TODAS = MARCAS_FORTES + MARCAS_FRACAS

EXTS = (".py", ".js", ".mjs", ".ts", ".json", ".sql", ".yml", ".yaml")

# As gavetas que decidem a espécie quando o ficheiro é ambíguo.
DE_COLETA = ("coleta/", "fontes/", "guarda/", "candidatas/", "regras/",
             "leis/", "medidas/", "admissao/", "pedido/", "orquestrador/",
             "provas/", "system-map/", "motor/", "portoes/")
DE_PORTAL = ("italia-portale/", "superficie/", "pacote/")
DE_DADO = ("data/", "build/", "handoff/", "research/")


def _conteudo(rel):
    """Lê do DISCO, não do último commit.

    ⚠️ Se lesse do commit, um ficheiro de inteligência novo e ainda não
    commitado seria invisível — e é exatamente esse o caso que a trava tem de
    apanhar."""
    try:
        with open(os.path.join(RAIZ, rel), "rb") as f:
            return f.read()
    except OSError:
        return b""


def _ficheiros():
    """Rastreados **mais** os novos que ainda não entraram — sem os ignorados."""
    r = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=RAIZ, capture_output=True, text=True)
    return sorted(set(r.stdout.splitlines()))


def sha_do_blob(rel):
    """⚠️ QUEM MEDE É O GIT, NÃO EU.

    Tentei duas maneiras antes desta, e as duas estavam erradas:

    1. `sha256` do ficheiro neste disco — dá CRLF, e o Git guarda LF. Já
       publiquei um sha errado assim, numa migration.
    2. `sha256` do que sai de `git show HEAD:...` — corrige o CRLF, mas amarra a
       medida ao último *commit*. Como este censo é ele próprio commitado, o
       HEAD mudava a cada corrida e a medida andava atrás do próprio rabo.

    `git hash-object` resolve as duas: mede a árvore de trabalho **passando
    pelos mesmos filtros** que o Git aplicaria ao guardar. É o `GIT_BLOB_SHA` na
    acepção literal — o nome do objeto que o Git daria a este ficheiro."""
    r = subprocess.run(["git", "hash-object", "--", rel], cwd=RAIZ,
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


# ⚠️ O INSTRUMENTO DE MEDIDA NÃO É A COISA MEDIDA.
# Este censo e o teste da trava escrevem as marcas por extenso — é assim que as
# procuram. Sem esta linha, o censo encontrava-se a si próprio e declarava-se
# inteligência nova. Já caí nisto no guarda do System Map, quando o meu próprio
# censo contava como consumidor de `receitas.py`.
# Isto é uma lista curta, DECLARADA e visível. Não é uma porta: qualquer nome a
# mais aqui aparece no diff.
INSTRUMENTOS = ("system-map/scripts/censo_do_congelamento.py",
                "tests/test_trava_da_inteligencia.py",
                "provas/trava_da_inteligencia_morde.py",
                # ⚠️ A LEI DA FUNDAÇÃO NÃO É INTELIGÊNCIA — É QUEM A TRAVA.
                # `leis/fundacao_da_coleta.py` nomeia FIELD_VOICES, SCORING e
                # RECOMMENDATIONS **para os bloquear**. Congelá-la seria trancar
                # a própria fechadura: os 14 critérios de destrave deixariam de
                # poder ser corrigidos, e a fundação nunca poderia fechar.
                "leis/fundacao_da_coleta.py")


def _especie(rel, texto):
    """A espécie sai da gaveta e do que o ficheiro FAZ — não da palavra."""
    baixo = rel.lower()
    if rel in INSTRUMENTOS:
        return "INSTRUMENT"
    if baixo.startswith("tests/") or "/test_" in baixo or baixo.endswith(".md"):
        return "TEST" if baixo.startswith("tests/") else "DOCUMENTATION"
    if ".generated.json" in baixo or baixo.startswith("build/"):
        # ⚠️ NAO CONGELAR O QUE A PROPRIA CADEIA REESCREVE.
        # Estes ficheiros sao SAIDA: a cadeia canonica gera-os a cada corrida.
        # Congelar a saida faria a trava reprovar sempre que alguem medisse o
        # sistema — e uma trava que morde o trabalho certo e desligada.
        # Quem fica congelado e o GERADOR, que e codigo-fonte.
        return "GENERATED_OUTPUT"
    if baixo.endswith(".json"):
        # Um JSON pode ser contrato ou amostra. Contrato declara SCHEMA e
        # regras; amostra carrega resultado.
        return "CONTRACT" if '"SCHEMA"' in texto[:2000] else "DATA_SAMPLE"
    if any(baixo.startswith(p) for p in DE_PORTAL):
        # ⚠️ AQUI A REGRA É MAIS LARGA DO QUE NO CÓDIGO, E DE PROPÓSITO.
        #
        # No código de coleta, «signal» e «opportunity» são palavras de
        # passagem: descrevem o dado que está a ser transportado. Por isso lá
        # exijo marca FORTE.
        #
        # No portal é ao contrário: «opportunity», «market pulse», «future» não
        # são ambiente — são o PRODUTO que a tela mostra. `future-ruler.mjs` e
        # `italy-market-pulse.js` não têm marca forte e são inteligência à
        # mesma.
        #
        # Cheguei a exigir marca forte aqui também, e isso descongelou 23
        # ficheiros de tela que são exactamente o que a trava existe para
        # segurar. A mesma régua nos dois sítios dava a resposta errada num
        # deles — porque a palavra não vale o mesmo nos dois.
        return "PORTAL_UI"
    if any(baixo.startswith(p) for p in DE_DADO):
        return "DATA_SAMPLE"

    # ⚠️ SEM MARCA FORTE, NUNCA É IMPLEMENTAÇÃO — em gaveta nenhuma.
    #
    # Isto era o contrário, e o contrário estava errado: o que eu não sabia
    # arrumar caía em `IMPLEMENTATION` por omissão. Quando acrescentei a marca
    # `SIGNAL`, essa omissão congelou sete ficheiros `.sql` — migrations e
    # testes — que só têm a palavra lá dentro, de passagem.
    #
    # Congelar uma migration aplicada sob a trava da inteligência é misturar
    # duas leis: ela já é imutável por ser migration, e não é inteligência
    # nenhuma. E uma trava que prende o que não devia é uma trava que alguém
    # desliga.
    #
    # A pergunta certa não é «em que pasta mora?» — é «este ficheiro CALCULA
    # sinal, nota ou recomendação?». Só a marca forte responde isso.
    forte = any(m in texto for m in MARCAS_FORTES)
    if not forte:
        return "MENCAO_FRACA_APENAS"
    return "IMPLEMENTATION"


def censo():
    achados = []
    for rel in _ficheiros():
        if not rel.endswith(EXTS):
            continue
        dados = _conteudo(rel)
        if not dados:
            continue
        try:
            texto = dados.decode("utf-8", "replace")
        except Exception:                              # noqa: BLE001
            continue
        if not any(m in texto for m in TODAS):
            continue
        achados.append({
            "PATH": rel,
            "SPECIES": _especie(rel, texto),
            "GIT_BLOB_SHA": sha_do_blob(rel),
            "MARCAS_FORTES": sorted(m for m in MARCAS_FORTES if m in texto),
        })

    por_especie = {}
    for a in achados:
        por_especie[a["SPECIES"]] = por_especie.get(a["SPECIES"], 0) + 1

    cabeca = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ,
                            capture_output=True, text=True).stdout.strip()
    return {
        "O_QUE_E": (
            "A fotografia da inteligencia que JA EXISTIA. A trava nao prova que "
            "ela nao existe — prova que ela nao avancou enquanto a coleta nao "
            "fechar."),
        "PORQUE_A_TRAVA_ANTIGA_NAO_BASTAVA": (
            "ela procurava PASTAS com certos nomes, nao encontrava nenhuma, e "
            "dai eu escrevi «zero areas implementadas». A afirmacao era maior "
            "do que a prova: nao havia pasta, havia artefatos espalhados."),
        "FROZEN_AT_HEAD": cabeca,
        "O_QUE_FROZEN_AT_HEAD_E": (
            "a marca historica: o ponto em que a fotografia foi tirada. NAO e o "
            "ponto em que se mede — mede-se sempre a arvore de trabalho de "
            "agora, contra os sha que essa fotografia guardou."),
        "ARTEFATOS": len(achados),
        "POR_ESPECIE": dict(sorted(por_especie.items())),
        "O_QUE_A_TRAVA_SEGURA": ["IMPLEMENTATION", "CONTRACT", "PORTAL_UI"],
        "PORQUE_SO_ESSAS": (
            "TEST e DOCUMENTATION descrevem; DATA_SAMPLE e resultado congelado; "
            "GENERATED_OUTPUT e reescrito pela propria cadeia canonica — "
            "congela-se o gerador, nao a saida; COLLECTION_ONLY e coleta com a "
            "palavra dentro. Congelar tudo impediria consertar coleta, e uma "
            "trava que impede o trabalho certo e desligada na primeira semana."),
        "FROZEN_INTELLIGENCE_ARTIFACTS": sorted(
            (a for a in achados
             if a["SPECIES"] in ("IMPLEMENTATION", "CONTRACT", "PORTAL_UI")),
            key=lambda x: x["PATH"]),
        "OUTROS_ARTEFATOS": sorted(
            ({"PATH": a["PATH"], "SPECIES": a["SPECIES"]} for a in achados
             if a["SPECIES"] not in ("IMPLEMENTATION", "CONTRACT", "PORTAL_UI")),
            key=lambda x: x["PATH"]),
    }


def main():
    fora = censo()
    destino = os.path.join(RAIZ, "system-map", "data",
                           "congelamento.generated.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(fora, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("artefatos=%d · por especie=%s · congelados=%d · HEAD=%s" % (
        fora["ARTEFATOS"], fora["POR_ESPECIE"],
        len(fora["FROZEN_INTELLIGENCE_ARTIFACTS"]), fora["FROZEN_AT_HEAD"][:8]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
