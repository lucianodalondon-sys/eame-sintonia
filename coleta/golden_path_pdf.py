#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PRIMEIRA ESTRADA COMPLETA — do PDF guardado até à porta da inteligência.

    PDF GUARDADO  →  FICHA DE BRUTO  →  EXECUTOR  →  TEXTO COM PAI
                  →  PORTA DE ADMISSÃO  →  PRONTO / NÃO SEI / ERRO

POR QUE ISTO É UM FICHEIRO SEPARADO DO EXECUTOR
-----------------------------------------------
Porque o executor não julga. Ele abre e conta; quem decide se um item entra é a
porta de admissão, que já existe e não se toca. Se as duas coisas vivessem no
mesmo ficheiro, um dia alguém juntava-as sem reparar — e a partir daí ninguém
conseguiria distinguir «ficou de fora porque não serve» de «ficou de fora
porque a ferramenta falhou».

O QUE ESTE FICHEIRO FAZ, POR ORDEM
----------------------------------
1. tira a impressão digital dos 49 PDF ANTES de tudo
2. manda o executor derivar o texto
3. tira a impressão digital dos 49 PDF DEPOIS, e compara
4. audita os 6 textos antigos, feitos à mão, e vê se dá para provar o pai
5. leva cada texto derivado à porta de admissão
6. faz as contas baterem, e diz alto se não baterem
7. deixa o recibo no manifesto de corridas que a casa já usa

A REGRA QUE MANDA EM TUDO ISTO
------------------------------
    NADA SOME EM SILÊNCIO.

Emitido menos aterrado tem de dar zero. Aterrado menos visto pela porta tem de
dar zero. Se não der, o número aparece com nome, e não escondido numa frase
simpática no fim do relatório.

CORRER
------
    py coleta/golden_path_pdf.py

Offline. Sem rede, sem Apify, sem OCR, sem gastar um cêntimo.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import artefato as art  # noqa: E402
import admissao as adm  # noqa: E402
import executor_texto_de_pdf as ex  # noqa: E402

MANIFESTO = RAIZ / "data" / "samples" / "RUN-MANIFEST.json"
RECONCILIACAO = RAIZ / "system-map" / "data" / "golden-path-pdf.generated.json"
UNIVERSO = "T7"


def impressoes_dos_brutos() -> dict:
    """A impressão digital de cada PDF, agora."""
    return {p.relative_to(RAIZ).as_posix(): art.sha256_do_ficheiro(str(p))
            for p in ex.os_pdf_italianos()}


def auditar_os_manuais() -> list:
    """Os seis textos tirados à mão: dá mesmo para provar de que PDF vieram?

    A tentação aqui é grande: o ficheiro chama-se `vite_20_270826.txt` e está
    na mesma pasta que `vite_20_270826.pdf`. Parece óbvio.

    Mas «estar ao lado com o mesmo nome» é um indício, não uma prova. O texto
    pode ter sido tirado de outra versão do PDF, ou de outro documento, ou
    escrito à mão a partir do que alguém leu. Ninguém guardou nada que o diga.

        NÃO SE MELHORA A HISTÓRIA PARA ELA FICAR MAIS BONITA.

    Então mede-se: se o texto do ficheiro à mão aparece de facto dentro do PDF,
    isso é prova — o pai fica PROVEN. Se não aparece, fica UNKNOWN, e o
    ficheiro continua guardado a dizer que não se sabe.
    """
    fichas = []
    for pdf in ex.os_pdf_italianos():
        irmao = pdf.with_suffix(".txt")
        if not irmao.is_file():
            continue

        pai = art.raw_do_disco(str(pdf), str(RAIZ), COUNTRY_SCOPE="IT")
        manual = irmao.read_text(encoding="utf-8", errors="replace")
        do_pdf, estado, _erro, _m = ex.extrair(pdf)

        # A prova: um pedaço reconhecível do texto à mão tem de existir dentro
        # do PDF. Compara-se sem espaços, porque a quebra de linha muda entre
        # ferramentas e isso não é diferença de conteúdo.
        def _limpo(s):
            return "".join(s.split()).lower()

        amostra = _limpo(manual)[:400]
        provado = bool(amostra) and amostra in _limpo(do_pdf)

        f = art.raw_do_disco(str(irmao), str(RAIZ), COUNTRY_SCOPE="IT")
        f.ARTIFACT_TYPE = art.DERIVED
        f.DERIVATION_TYPE = art.MANUAL_LEGACY
        f.EXECUTOR_ID = "PESSOA"
        f.EXECUTOR_VERSION = art.NAO_SEI
        f.PIPELINE_VERSION = art.NAO_SEI
        f.DERIVED_AT = art.NAO_SEI          # ninguém registou quando
        f.STATE = art.TEXT_LAYER_PRESENT
        if provado:
            f.PARENT_ARTIFACT_ID = pai.ARTIFACT_ID
            f.PARENT_SHA256 = pai.SHA256
            f.NOTES = {"PARENT_BASIS": "PARENT_PROVEN",
                       "COMO": "o texto do ficheiro a mao existe dentro do PDF"}
        else:
            # Pai desconhecido. E, pela lei do contrato, «pai pela metade» é
            # proibido: ou se sabe tudo sobre o pai, ou não se sabe nada.
            f.PARENT_ARTIFACT_ID = art.NAO_SEI
            f.PARENT_SHA256 = art.NAO_SEI
            f.DERIVATION_TYPE = art.NAO_SEI
            f.NOTES = {"PARENT_BASIS": "PARENT_UNKNOWN",
                       "COMO": "estar ao lado com o mesmo nome e indicio, nao "
                               "prova. Ninguem guardou de onde este texto veio",
                       "PDF_VIZINHO": pdf.relative_to(RAIZ).as_posix()}
        fichas.append({**f.para_json(),
                       "PARENT_STATUS": "PARENT_PROVEN" if provado
                                        else "PARENT_UNKNOWN"})
    return fichas


def pela_porta(artefatos: list, run_id: str) -> dict:
    """Leva cada texto derivado à porta de admissão que já existe.

    O item que a porta recebe é montado a partir da ficha do artefato, e **só**
    do que a ficha prova. Repare no que NÃO se faz aqui:

      · não se põe `fact_time` a partir de `DERIVED_AT`. A hora em que esta
        máquina abriu o PDF não é a data do que está escrito lá dentro.
      · não se põe `fact_location` a partir de `COUNTRY_SCOPE`. Trabalharmos a
        Itália não prova que o fato aconteceu em Itália.
      · não se declara língua. Um documento da frente italiana pode estar em
        inglês, e escrever IT sem ler seria uma afirmação sobre o conteúdo.

    A consequência é previsível e está certa: sem data conhecida, a porta
    responde NÃO_SEI. Isso não é a estrada a falhar — é a estrada a dizer, com
    precisão, qual é o degrau que falta.
    """
    itens, decisoes = [], []
    for a in artefatos:
        caminho = RAIZ / a["STORAGE_LOCATION"]
        texto = caminho.read_text(encoding="utf-8", errors="replace") \
            if caminho.is_file() else ""
        item = {
            "id": a["ARTIFACT_ID"],
            # A ESPECIE E DECLARADA, NAO ADIVINHADA. Sem isto a porta nao sabe
            # que esta a julgar um documento, e volta a cobrar-lhe o tempo de
            # um fato que ainda nao foi extraido (COL-LAW-502).
            "artifact_type": a["ARTIFACT_TYPE"],
            "parent_artifact_id": a["PARENT_ARTIFACT_ID"],
            "texto": texto[:20000],
            "source_id": (a["SOURCE_ID"] if a["SOURCE_ID"] != art.NAO_SEI
                          else a["PARENT_ARTIFACT_ID"]),
            "fact_time": (a["FACT_TIME"]
                          if a["FACT_TIME"] not in (art.NAO_SEI, art.NAO_SE_APLICA)
                          else ""),
            "source_location": a["SOURCE_LOCATION"],
            "fact_location": a["FACT_LOCATION"],
            "captured_at": a["DERIVED_AT"],
        }
        itens.append(item)
        decisoes.append(adm.decidir(item, UNIVERSO, corrida=run_id))

    if decisoes:
        adm.escrever(decisoes)

    conta = {}
    porques = {}
    for d in decisoes:
        conta[d.resultado] = conta.get(d.resultado, 0) + 1
        porques.setdefault(d.resultado, []).append(
            {"item": d.item, "regra": d.regra, "motivo": d.motivo[:200],
             "prova": d.evidencia})
    return {"vistos": len(itens), "por_resultado": conta,
            "porques": {k: v[:3] for k, v in porques.items()},
            "decisoes": decisoes, "itens": itens}


def versao_da_engenharia() -> dict:
    """Que código produziu esta corrida? (COL-LAW-307)

    Medido, nunca inferido: se o git não responder, fica NÃO SEI. E o commit
    prova que aquele código EXISTIA — não que a corrida o usou; quem prova isso
    é a corrida ter-se registado a si própria com ele.
    """
    import subprocess
    def git(*a):
        r = subprocess.run(["git", "-C", str(RAIZ), *a], capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        return r.stdout.strip() if r.returncode == 0 else art.NAO_SEI
    sujo = git("status", "--porcelain")
    biblia = art.NAO_SEI
    try:
        biblia = json.loads((RAIZ / "docs" / "biblia" / "leis.json")
                            .read_text(encoding="utf-8")).get("VERSION", art.NAO_SEI)
    except (OSError, ValueError):
        pass
    return {
        "GIT_COMMIT": git("rev-parse", "HEAD") or art.NAO_SEI,
        "GIT_BRANCH": git("rev-parse", "--abbrev-ref", "HEAD") or art.NAO_SEI,
        # ARVORE SUJA E UM FACTO SOBRE A CORRIDA. Um commit limpo nao prova que
        # o codigo que correu era o do commit, se havia alteracoes por commitar.
        "GIT_TREE_CLEAN": "NAO" if sujo and sujo != art.NAO_SEI else "SIM",
        "BIBLE_VERSION": biblia,
    }


def estado_do_acervo() -> dict:
    """O estado material que prova incrementalidade — nem mais, nem menos.

    Nao e um snapshot do mundo: sao as tres contagens de que a idempotencia
    depende. Um STATE_BEFORE grande demais nunca se compara; um pequeno demais
    nao prova nada.
    """
    pdfs = ex.os_pdf_italianos()
    conteudos = {art.sha256_do_ficheiro(str(p)) for p in pdfs}
    try:
        registo = ex.carregar_registo()["ARTEFATOS"]
    except Exception:                                          # noqa: BLE001
        registo = []
    return {
        "OCORRENCIAS": len(pdfs),
        "CONTEUDOS_UNICOS": len(conteudos),
        "DERIVADOS_PRESENTES": len({a.get("PARENT_SHA256") for a in registo
                                    if a.get("PARENT_SHA256")}),
    }


def main() -> int:
    print("A PRIMEIRA ESTRADA: PDF GUARDADO -> TEXTO -> PORTA\n")

    # ── 0 · PRE-VOO: a capacidade existe? (G-34 · COL-LAW-503) ──────────────
    # Antes de tocar num unico documento. Se a ferramenta falta, a corrida para
    # AQUI — e nenhum PDF e marcado como defeituoso por causa da nossa maquina.
    if not ex.ha_ferramenta():
        falha = {
            "O_QUE_ISTO_E": "A corrida parou no PRE-VOO. Nenhum documento foi tocado.",
            "RUN_ID": "PREFLIGHT-" + art.agora().replace(":", "").replace("-", ""),
            "STATUS": "FAILED_PRECONDITION",
            "COMPLETION_BASIS": ("nao houve execucao: a capacidade exigida nao "
                                 "existe nesta maquina"),
            "PREFLIGHT": {
                "EXECUTOR_AVAILABLE": "NAO",
                "CAPACIDADE": "pdftotext",
                "REASON": "EXECUTOR_UNAVAILABLE",
                "NAO_E": ("ARTIFACT_EXTRACTION_ERROR — nenhum PDF esta "
                          "defeituoso; a ferramenta e que falta (COL-LAW-503)"),
            },
            "COUNTS": {"RAW_INPUT": 0, "RAW_EXTRACTION_ERROR": 0,
                       "DERIVED_EMITTED": 0, "DERIVED_LANDED": 0,
                       "ADMISSION_SEEN": 0, "LOST": 0},
        }
        RECONCILIACAO.parent.mkdir(parents=True, exist_ok=True)
        RECONCILIACAO.write_text(json.dumps(falha, ensure_ascii=False, indent=1)
                                 + "\n", encoding="utf-8")
        print("  0 · PRE-VOO REPROVOU · EXECUTOR_UNAVAILABLE: pdftotext")
        print("      nenhum documento foi tocado. Isto NAO e erro dos PDF.")
        print("\nGOLDEN_PATH_PDF=FAILED_PRECONDITION")
        return 2
    print("  0 · pre-voo: pdftotext presente")

    engenharia = versao_da_engenharia()
    antes_do_acervo = estado_do_acervo()

    # ── 1 · a impressão digital de cada bruto, ANTES ─────────────────────────
    antes = impressoes_dos_brutos()
    print("  1 · %d PDF italianos, impressao digital tirada antes" % len(antes))

    # ── 2 · o executor deriva ───────────────────────────────────────────────
    recibo = ex.correr()
    c = recibo["COUNTS"]
    print("  2 · executor %s v%s · com texto %d · precisa OCR %d · erro %d"
          % (recibo["EXECUTOR_ID"], recibo["EXECUTOR_VERSION"],
             c["TEXT_LAYER_PRESENT"], c["NEEDS_OCR"], c["EXTRACTION_ERROR"]))

    # ── 3 · e DEPOIS. O bruto é intocável, e prova-se ────────────────────────
    depois = impressoes_dos_brutos()
    mexidos = [k for k in antes if antes[k] != depois.get(k)]
    sumiram = [k for k in antes if k not in depois]
    print("  3 · brutos alterados: %d · desaparecidos: %d"
          % (len(mexidos), len(sumiram)))

    # ── 4 · os seis textos antigos ──────────────────────────────────────────
    manuais = auditar_os_manuais()
    provados = [m for m in manuais if m["PARENT_STATUS"] == "PARENT_PROVEN"]
    print("  4 · textos feitos a mao: %d · com pai provado: %d"
          % (len(manuais), len(provados)))

    # ── 5 · a porta ─────────────────────────────────────────────────────────
    registo = ex.carregar_registo()["ARTEFATOS"]
    desta = [a for a in registo if a["RUN_ID"] == recibo["RUN_ID"]] or registo
    porta = pela_porta(desta, recibo["RUN_ID"])
    print("  5 · a porta viu %d · %s"
          % (porta["vistos"],
             " · ".join("%s %d" % (k, v)
                        for k, v in sorted(porta["por_resultado"].items()))))

    # ── 6 · as contas ───────────────────────────────────────────────────────
    emitidos = c["DERIVED_EMITTED"]
    aterrados = c["DERIVED_LANDED"]
    vistos = porta["vistos"]
    perdidos = (emitidos - aterrados) + max(0, aterrados - vistos)

    reconc = {
        "O_QUE_ISTO_E": ("A conta desta corrida, do PDF guardado ate a porta. "
                         "Cada numero e medido; nenhum e esperado."),
        "COMO_REFAZER": "py coleta/golden_path_pdf.py",
        "RUN_ID": recibo["RUN_ID"],
        "STATUS": recibo["STATUS"],
        # ── O CONTRATO DE FECHO (G-38 · COL-LAW-210 · 211 · 307) ────────────
        # `SUCCESS` diz que o executor terminou. `RUN_STATE` diz outra coisa:
        # se a corrida FECHOU — outputs + reconciliacao + erros + manifesto.
        # Sao dois factos, e ate aqui so existia o primeiro.
        "RUN_STATE": None,          # preenchido no fecho, e so la
        "COMPLETION_BASIS": None,   # idem
        "ROUTE": "LOCAL_EXECUTOR",  # nao houve HTTP, browser nem Apify
        "PREFLIGHT": {"EXECUTOR_AVAILABLE": "SIM", "CAPACIDADE": "pdftotext"},
        "STATE_BEFORE": antes_do_acervo,
        "STATE_AFTER": None,        # medido depois de o trabalho acabar
        **engenharia,
        "EXECUTOR_ID": recibo["EXECUTOR_ID"],
        "EXECUTOR_VERSION": recibo["EXECUTOR_VERSION"],
        "PIPELINE_VERSION": recibo["PIPELINE_VERSION"],
        "STARTED_AT": recibo["STARTED_AT"],
        "FINISHED_AT": recibo["FINISHED_AT"],
        "COUNTS": {
            "RAW_INPUT": c["RAW_INPUT"],
            "RAW_TEXT_LAYER_PRESENT": c["TEXT_LAYER_PRESENT"],
            "RAW_NEEDS_OCR": c["NEEDS_OCR"],
            "RAW_EXTRACTION_ERROR": c["EXTRACTION_ERROR"],
            "RAW_UNKNOWN": c["RAW_UNKNOWN"],
            "DERIVED_EMITTED": emitidos,
            "DERIVED_LANDED": aterrados,
            "JA_EXISTIAM": c["JA_EXISTIA"],
            "ADMISSION_SEEN": vistos,
            **{("ADMISSION_" + k): v for k, v in porta["por_resultado"].items()},
            "LOST": perdidos,
        },
        "RAW_IMUTAVEL": {
            "PDF_CONFERIDOS": len(antes),
            "ALTERADOS": mexidos,
            "DESAPARECIDOS": sumiram,
            "VEREDITO": "IMUTAVEL" if not mexidos and not sumiram else "VIOLADO",
        },
        "TEXTOS_A_MAO": {
            "TOTAL": len(manuais),
            "PARENT_PROVEN": len(provados),
            "PARENT_UNKNOWN": len(manuais) - len(provados),
            "FICHAS": manuais,
        },
        "PORQUES_DA_PORTA": porta["porques"],
        "PRECISION": ("UNKNOWN — nao ha gabarito humano. Contar quantos "
                      "passaram e COBERTURA; dizer que estao certos exigiria "
                      "alguem que leia italiano a marcar a mao o que devia "
                      "passar, e essa lista nao existe."),
        "ERRORS": recibo["ERRORS"],
        # ── O CUSTO, E O QUE O ZERO QUER DIZER ──────────────────────────────
        # `COST_USD: 0.0` sozinho nao diz POR QUE e zero. Zero por rota gratuita
        # provada e zero por ninguem ter olhado escrevem-se igual — e leem-se
        # igual. Por isso o zero passa a vir acompanhado da BASE.
        #
        # O valor continua 0 porque a lei desta casa ja decidiu isso, e esta
        # escrita em `orquestrador/orquestrador.py`:
        #
        #   «Custo ZERO quando o executor nao foi chamado (...). Escrever
        #    «NAO SEI» aqui seria pior que impreciso — o portao do padrao conta
        #    os «NAO SEI» como divida, e eu estaria a inventar divida sobre uma
        #    corrida que nao gastou nada.»
        #
        # O que faltava nao era trocar o numero: era dizer que ele NAO e uma
        # contabilidade. Ausencia provada de rota paga nao e a mesma coisa que
        # uma conta fechada, e agora o artefato diz as duas coisas separadas.
        "COST_USD": 0.0,
        "COST_BASIS": ("ROTA_GRATUITA_PROVADA — o zero vem da ausencia medida "
                       "de rota paga e de rede, NAO de contabilidade monetaria. "
                       "Nenhuma plataforma foi chamada, entao nao ha fatura para "
                       "conferir."),
        "COST_ACCOUNTING": "NAO_SE_APLICA",
        "ROTA_PAGA_USADA": "NAO",
        "REDE_USADA": "NAO",
        "OCR_USADO": "NAO",
    }
    # ── O FECHO ATÓMICO, E ELE É O ÚLTIMO PASSO ─────────────────────────────
    # COL-LAW-210: `COMPLETE` exige outputs + reconciliação + erros + manifesto.
    # Cada condição é MEDIDA aqui; nenhuma é assumida. Se o processo morrer
    # antes desta linha, o ficheiro na pasta nunca chega a dizer COMPLETE — e
    # é isso que impede «há ficheiros» de se ler como «a corrida acabou».
    reconc["STATE_AFTER"] = estado_do_acervo()
    condicoes = {
        "executor_terminou": recibo["STATUS"] in ("SUCCESS", "PARTIAL"),
        "outputs_aterrados": aterrados == emitidos,
        "reconciliacao_feita": perdidos == 0,
        "erros_contabilizados": isinstance(c["EXTRACTION_ERROR"], int),
        "bruto_intacto": not mexidos and not sumiram,
        "estado_antes_e_depois": bool(reconc["STATE_BEFORE"]
                                      and reconc["STATE_AFTER"]),
    }
    faltou = sorted(k for k, v in condicoes.items() if not v)
    reconc["RUN_STATE"] = "COMPLETE" if not faltou else "PARTIAL"
    reconc["COMPLETION_BASIS"] = {
        "CONDICOES": condicoes,
        "FALTOU": faltou,
        "PORQUE": ("todas as condições de fecho foram medidas e cumpridas"
                   if not faltou else
                   "fecho incompleto: " + ", ".join(faltou)),
        "IDEMPOTENCIA": {
            "NOVOS": emitidos,
            "REAPROVEITADOS": c["JA_EXISTIA"],
            "NOTA": ("NOVOS=0 com REAPROVEITADOS>0 é a corrida a não refazer "
                     "trabalho. Não é saída zero, e não é perda."),
        },
    }

    RECONCILIACAO.parent.mkdir(parents=True, exist_ok=True)
    RECONCILIACAO.write_text(
        json.dumps(reconc, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")

    # ── 7 · o recibo entra no manifesto que a casa ja usa ────────────────────
    d = {"RUNS": []}
    if MANIFESTO.is_file():
        try:
            d = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    ja = {r.get("RUN_ID") for r in d.get("RUNS", [])}
    if recibo["RUN_ID"] not in ja:
        d.setdefault("RUNS", []).append({
            "RUN_ID": recibo["RUN_ID"],
            "PLATFORM": "LOCAL",
            "ACTOR": recibo["EXECUTOR_ID"],
            "ACTOR_VERSION": recibo["EXECUTOR_VERSION"],
            "STARTED_AT": recibo["STARTED_AT"],
            "FINISHED_AT": recibo["FINISHED_AT"],
            "COUNTRY": "IT",
            "MISSION": recibo["MISSION"],
            "STATUS": recibo["STATUS"],
            # O ESTADO DE FECHO VIAJA COM O RECIBO. Sem ele, quem le o
            # manifesto so sabe que o executor terminou.
            "RUN_STATE": reconc["RUN_STATE"],
            "ROUTE": reconc["ROUTE"],
            "GIT_COMMIT": reconc["GIT_COMMIT"],
            "BIBLE_VERSION": reconc["BIBLE_VERSION"],
            "PIPELINE_VERSION": recibo["PIPELINE_VERSION"],
            "ERROR": "",
            "CAPTURE_METHOD": "DERIVATION_RUN",
            "ITEM_COUNT_RAW": c["RAW_INPUT"],
            "ITEM_COUNT_NORMALIZED": aterrados,
            "COST_USD": 0.0,
            "EVIDENCE_PATH": RECONCILIACAO.relative_to(RAIZ).as_posix(),
            "OUTPUT_WRITTEN_AT": art.agora(),
        })
        MANIFESTO.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")

    print("  6 · emitidos %d · guardados %d · vistos pela porta %d · PERDIDOS %d"
          % (emitidos, aterrados, vistos, perdidos))
    print("  7 · recibo no RUN-MANIFEST · conta em %s"
          % RECONCILIACAO.relative_to(RAIZ).as_posix())
    print()
    if mexidos or sumiram:
        print("PARAGEM: um bruto mudou. O original e intocavel.")
        return 1
    if perdidos:
        print("PARAGEM: %d artefatos sumiram pelo caminho." % perdidos)
        return 1
    print("GOLDEN_PATH_PDF=OK · nada se perdeu, nenhum bruto mudou")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
