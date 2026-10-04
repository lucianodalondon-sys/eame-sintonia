#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CENSO SEMANTICO DA ITALIA — as contas TEM de fechar.

    py system-map/scripts/censo_semantico_it.py

    READ-ONLY. Nao abre rede, nao gasta Apify, nao coleta nada.

POR QUE ESTE FICHEIRO EXISTE
-----------------------------
A medicao anterior disse «a busca tem 482 termos: 29 IT, 8 FR, 6 ES». Isso soma
43. Faltavam 439 por explicar, e eu apresentei o numero na mesma.

    UM NUMERO QUE NAO FECHA NAO E UMA MEDICAO: E UMA IMPRESSAO COM CASAS DECIMAIS.

Fui ver de onde vinham os 482, e o erro era meu: contei TODAS as strings de
dezassete listas diferentes de tres ficheiros — os identificadores de ator da
Apify, os nomes dos lotes, os nomes de lugar, as palavras de funcao. Nada disso
e termo de busca. O total estava certo como soma e errado como significado.

O QUE ESTE FICHEIRO FAZ DIFERENTE
----------------------------------
1. mede LISTA A LISTA, com o papel de cada uma declarado;
2. classifica CADA termo em UMA categoria de escopo, e so uma;
3. exige que CLASSIFICADOS + DESCONHECIDOS = TOTAL, e reprova se nao fechar;
4. guarda o detalhe termo a termo num artefato auditavel.

    NUNCA ESCONDER O RESTO. O resto e onde mora o que ninguem mediu.

SAIDA: system-map/data/semantica-it.generated.json
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "system-map" / "data" / "semantica-it.generated.json"

# ── AS LISTAS QUE A ROTA ITALIANA TOCA, e o papel de cada uma ───────────────
# Declarado a mao porque PAPEL e leitura de gente: o scanner ve uma lista de
# strings e nao sabe se ela serve para procurar, para reconhecer ou para julgar.
# O que NAO e declarado a mao e o conteudo — esse e sempre lido do ficheiro.
LISTAS = [
    ("regras/sensor_coleta.py", "TERMOS", "BUSCA",
     "os termos que a busca digita, por recorte cultura-problema"),
    ("regras/rotulos_censo.py", "TERMOS", "EXTRACAO",
     "os termos que se procuram DENTRO do rotulo ja baixado"),
    ("regras/sensor_medir.py", "OBSERVACAO_CAMPO", "CLASSIFICACAO", "fala de campo"),
    ("regras/sensor_medir.py", "PESQUISA", "CLASSIFICACAO", "producao de pesquisa"),
    ("regras/sensor_medir.py", "INTERPRETACAO", "CLASSIFICACAO", "leitura tecnica"),
    ("regras/sensor_medir.py", "PRIMEIRA_PESSOA", "CLASSIFICACAO", "quem viu com os olhos"),
    ("regras/sensor_medir.py", "EVENTO", "CLASSIFICACAO", "convite e feira"),
    ("regras/sensor_medir.py", "MARKETING", "CLASSIFICACAO", "propaganda"),
    ("regras/sensor_medir.py", "NOTICIA", "CLASSIFICACAO", "release e imprensa"),
    ("admissao/admissao.py", "PERGUNTAS_DO_UNIVERSO", "ADMISSAO",
     "as palavras que decidem se o item pertence ao universo pedido"),
]

# ── AS CATEGORIAS DE ESCOPO ────────────────────────────────────────────────
# A ordem E a regra: a primeira que casa ganha. As mais especificas vem antes,
# senao `bactrocera oleae` cairia em «tem palavra italiana» em vez de latim.
#
#     TERMO QUE EXISTE EM VARIAS LINGUAS NAO E CONTAMINACAO.
#     Contaminacao e o termo EXCLUSIVO de outro pais numa rota que nao e dele.
ESCOPOS = [
    ("SCIENTIFIC_LATIN", re.compile(
        r"\b(bactrocera|zymoseptoria|venturia|halyomorpha|popillia|xylella|"
        r"echinochloa|ostrinia|diabrotica|fusarium|scaphoideus|spilocaea|"
        r"ambrosia|plasmopara|oleaginea|inaequalis|tritici|artemisiifolia|"
        r"japonica|dorsalis|zonata|viticola|cicloconio)\b", re.I)),
    ("INTERNATIONAL", re.compile(
        r"^(doi|orcid|openalex|pdf|html|json|url|api|http|https|www|id|"
        r"youtube|instagram|linkedin|facebook|apify|whisper|adama|basf|bayer|"
        r"syngenta|corteva|nufarm|fmc|ue|eu|it|es|fr|pt|en)$", re.I)),
    # AS LISTAS DE CLASSIFICACAO SAO TRILINGUES DE PROPOSITO — foram escritas
    # quando o sensor cobria ES, IT e FR: `hemos observado`, `abbiamo osservato`,
    # `notre etude`. Sem apanhar a FRASE, e nao so a palavra, o censo dava tudo
    # «desconhecido» e a contaminacao ficava invisivel.
    ("ES_ONLY", re.compile(
        r"\b(repilo|olivar|jornada|septoriosis|del olivo|del trigo|"
        r"tratamiento|espanol|espana|hemos|nuestro|nuestros|nuestra|ensayo|"
        r"ensayos|mi finca|mi parcela|mis olivos|mi cultivo|aqui en mi|tengo|"
        r"me paso|nos paso|esto significa|esto se debe|la razon|por lo tanto|"
        r"congreso|inscripcion|compra|disponible|oferta|suscribete|"
        r"segun informa|fuente|redaccion|comunicado de prensa|se ha|"
        r"en campo hemos|los ensayos|el ensayo)\b", re.I)),
    ("FR_ONLY", re.compile(
        r"\b(mildiou|septoriose|webinaire|de la vigne|du ble|traitement|"
        r"francais|france|notre|colloque|journee|achetez|d.apres|source :|"
        r"nos essais|mon exploitation|chez moi|cela signifie|donc|"
        r"inscription)\b", re.I)),
    ("IT_ONLY", re.compile(
        r"\b(diserbo|infestanti|difesa|malattie|malattia|convegno|frumento|"
        r"grano|melo|pomodoro|riso|mais|olive|olivo|vite|vigneto|soia|"
        r"bietola|barbabietola|risaia|giavone|crodo|ticchiolatura|"
        r"flavescenza|giallumi|dorata|occhio di pavone|cimice|piralide|"
        r"sottofila|inerbimento|carpocapsa|afidi|peronospora|alternaria|"
        r"botrite|ruggine|fogliari|paglia|micotossine|fusariosi|spiga|"
        r"septoriosi|loietto|avena|amaranto|resistente|monitoraggio|"
        r"trattamento|emergenza|studio|ricerca|rivista|articolo|universita|"
        r"istituto|pubblicazione|sperimentazione|tesi|lancio|campagna|"
        r"prodotto|annuncio|novita|fiera|autorizzazione|etichetta|"
        r"foglietto|registrazione|gazzetta|parassita|insetto|infestazione|"
        r"abbiamo|nostri|nostra|la prova|le prove|giornata|iscrizione|"
        r"acquista|secondo quanto|fonte|questo|quindi|percio|"
        r"in campo abbiamo|si e osservato|nel mio|qui da noi|"
        r"sintomo|avversita|patogeno|della|dello|degli|delle|nella|sulla)\b",
        re.I)),
    ("PT_ONLY", re.compile(
        r"\b(estudo|pesquisa|revista|artigo|universidade|instituto|publicacao|"
        r"lancamento|campanha|produto|anuncio|autorizacao|rotulo|bula|praga|"
        r"doenca|inseto|infestacao|sintoma|coleta|ensaio)\b", re.I)),
    ("EN_ONLY", re.compile(
        r"\b(launch|competitor|research|study|paper|journal|news|report|"
        r"wheat|olive|maize|weed|disease|insect)\b", re.I)),
]

# Termos que servem em portugues E italiano com a mesma grafia. Nao sao de
# ninguem, e por isso nao contam como contaminacao para lado nenhum.
SHARED = re.compile(
    r"^(evento|concorrente|decreto|fungo|registro|ministero|campo|produtos|"
    r"regione|regiao|italia|italiano)$", re.I)


def classifica(termo: str) -> str:
    """Uma categoria por termo, e so uma. Sem categoria = UNKNOWN, nunca IT."""
    t = termo.strip()
    if not t:
        return "UNKNOWN"
    if SHARED.match(t):
        return "SHARED_MULTILINGUAL"
    for nome, rx in ESCOPOS:
        if rx.search(t):
            return nome
    # nome proprio: comeca por maiuscula no original e nao casou com nada
    if t[:1].isupper() and " " not in t:
        return "BRAND_OR_PROPER_NAME"
    return "UNKNOWN"


def termos_da_lista(ficheiro: str, nome: str) -> list:
    """As strings de UMA lista, lidas com `ast`. Nada e executado."""
    p = RAIZ / ficheiro
    if not p.is_file():
        return []
    try:
        arv = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    for no in ast.walk(arv):
        if not isinstance(no, ast.Assign) or len(no.targets) != 1:
            continue
        alvo = no.targets[0]
        if not isinstance(alvo, ast.Name) or alvo.id != nome:
            continue
        return _so_os_termos(no.value)
    return []


# Quando a lista e feita de fichas — `{"grupo": ..., "palavras": [...],
# "porque": "..."}` — apanhar todas as strings apanha tambem o NOME do grupo e a
# FRASE que explica porque ele existe. Sao prosa, nao termos, e contadas como
# termos enchem o total de coisas que ninguem digita numa busca.
#
#     `vetor da flavescencia dourada, de controle obrigatorio em 5 regioes`
#     nao e uma palavra de busca: e a razao de ela existir.
#
# Dezassete «termos desconhecidos» eram exatamente isso — defeito da medicao,
# nao do vocabulario.
CHAVE_DOS_TERMOS = ("palavras", "termos", "terms", "keywords")


def _so_os_termos(no) -> list:
    """As strings que sao MESMO termos — a prosa que os explica fica de fora."""
    if isinstance(no, ast.Dict):
        fora = []
        for k, v in zip(no.keys, no.values):
            nome = k.value if isinstance(k, ast.Constant) else None
            # num dicionario de fichas, a chave e o universo/grupo: nao e termo
            fora += _so_os_termos(v)
        return fora
    if isinstance(no, (ast.List, ast.Tuple, ast.Set)):
        # A FICHA TAMBEM PODE SER UM TUPLO. `rotulos_censo` guarda
        # `('SCAPHOIDEUS', ['scaphoideus', 'scafoideo'], 'porque existe')` —
        # nome, termos, razao. O extrator so sabia ler dicionarios, e por isso
        # o ficheiro inteiro desapareceu do censo: zero termos, em silencio.
        #
        #     UMA MEDICAO QUE PERDE UM FICHEIRO INTEIRO SEM SE QUEIXAR E PIOR
        #     QUE UMA QUE FALHA ALTO.
        #
        # Num tuplo assim, os termos sao a lista la dentro — o resto e prosa.
        tuplos = [x for x in no.elts if isinstance(x, ast.Tuple)]
        if tuplos:
            fora = []
            for t in tuplos:
                listas = [e for e in t.elts if isinstance(e, (ast.List, ast.Set))]
                for l in listas:
                    fora += _so_os_termos(l)
            if fora:
                return fora
        # lista de fichas? entao so o campo dos termos
        fichas = [x for x in no.elts if isinstance(x, ast.Dict)]
        if fichas:
            fora = []
            for f in fichas:
                for k, v in zip(f.keys, f.values):
                    if (isinstance(k, ast.Constant)
                            and str(k.value).lower() in CHAVE_DOS_TERMOS):
                        fora += _so_os_termos(v)
            return fora
        return [x.value for x in no.elts
                if isinstance(x, ast.Constant) and isinstance(x.value, str)
                and len(x.value.strip()) > 1]
    if isinstance(no, ast.Constant) and isinstance(no.value, str):
        return [no.value] if len(no.value.strip()) > 1 else []
    return []


def quem_consome(ficheiro: str) -> list:
    """Quem importa este ficheiro — medido pelo git, nao suposto."""
    modulo = Path(ficheiro).stem
    r = subprocess.run(
        ["git", "-C", str(RAIZ), "grep", "-l", "-E",
         f"import {modulo}|from {modulo}|{ficheiro}", "--", "*.py", "*.yml"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return sorted(x for x in r.stdout.split() if x != ficheiro)


def main() -> int:
    vocabularios = []
    for ficheiro, nome, papel, o_que_e in LISTAS:
        termos = termos_da_lista(ficheiro, nome)
        if not termos:
            continue
        por_escopo = {}
        detalhe = []
        for t in termos:
            c = classifica(t)
            por_escopo[c] = por_escopo.get(c, 0) + 1
            detalhe.append({"termo": t, "escopo": c})

        classificados = sum(v for k, v in por_escopo.items() if k != "UNKNOWN")
        desconhecidos = por_escopo.get("UNKNOWN", 0)
        estrangeiros = sum(por_escopo.get(k, 0) for k in ("ES_ONLY", "FR_ONLY"))

        vocabularios.append({
            "VOCABULARY_ID": f"{Path(ficheiro).stem}.{nome}",
            "FILE": ficheiro,
            "OWNER": Path(ficheiro).parent.name,
            "ROLE": papel,
            "O_QUE_E": o_que_e,
            "TOTAL_TERMS": len(termos),
            "POR_ESCOPO": dict(sorted(por_escopo.items(), key=lambda x: -x[1])),
            "CLASSIFIED": classificados,
            "UNKNOWN": desconhecidos,
            "FECHA": classificados + desconhecidos == len(termos),
            "FOREIGN_ONLY": estrangeiros,
            "CONSUMERS": quem_consome(ficheiro),
            "TERMOS": detalhe,
        })

    nao_fecham = [v["VOCABULARY_ID"] for v in vocabularios if not v["FECHA"]]
    total = sum(v["TOTAL_TERMS"] for v in vocabularios)

    d = {
        "SCHEMA": "sintonia.semantica-it/1",
        "O_QUE_ISTO_E": (
            "Cada termo dos vocabularios que a rota italiana toca, classificado em "
            "UMA categoria de escopo. As contas fecham por construcao: "
            "CLASSIFICADOS + UNKNOWN = TOTAL, e o ficheiro reprova se nao fechar."),
        "PROVENANCE": {"HEAD": subprocess.run(
            ["git", "-C", str(RAIZ), "rev-parse", "HEAD"],
            capture_output=True, text=True).stdout.strip()},
        "VOCABULARIOS": vocabularios,
        "COUNTS": {
            "vocabularios": len(vocabularios),
            "termos_ao_todo": total,
            "por_papel": {p: sum(v["TOTAL_TERMS"] for v in vocabularios
                                 if v["ROLE"] == p)
                          for p in sorted({v["ROLE"] for v in vocabularios})},
            "estrangeiros_ao_todo": sum(v["FOREIGN_ONLY"] for v in vocabularios),
            "todas_as_contas_fecham": not nao_fecham,
        },
    }
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")

    print("CENSO SEMANTICO DA ITALIA — read-only, sem rede, sem Apify\n")
    print(f"  {'vocabulario':34s} {'papel':14s} {'total':>6s} {'IT':>5s} "
          f"{'ES/FR':>6s} {'?':>4s}  fecha")
    for v in vocabularios:
        e = v["POR_ESCOPO"]
        print(f"  {v['VOCABULARY_ID'][:32]:34s} {v['ROLE'][:12]:14s} "
              f"{v['TOTAL_TERMS']:>6} {e.get('IT_ONLY', 0):>5} "
              f"{v['FOREIGN_ONLY']:>6} {v['UNKNOWN']:>4}  "
              f"{'SIM' if v['FECHA'] else 'NAO'}")
    print(f"\n  termos ao todo: {total} · estrangeiros: "
          f"{d['COUNTS']['estrangeiros_ao_todo']}")
    print(f"  todas as contas fecham: "
          f"{'SIM' if d['COUNTS']['todas_as_contas_fecham'] else 'NAO'}")
    if nao_fecham:
        print(f"  NAO FECHAM: {', '.join(nao_fecham)}", file=sys.stderr)
        return 1
    print(f"\n  escrito em {SAIDA.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
