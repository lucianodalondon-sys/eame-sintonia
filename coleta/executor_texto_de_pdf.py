#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PRIMEIRO EXECUTOR A FALAR A LÍNGUA COMUM — texto a partir de PDF.

ATENÇÃO AO QUE ISTO É, E AO QUE NÃO É
-------------------------------------
Isto **não** é «o extrator de PDF do SINTONIA». É o primeiro executor real a
provar o contrato de `leis/artefato.py`. Se o contrato só existir no papel, não
vale nada; alguém tem de o usar a sério, com ficheiros a sério, e mostrar que
aguenta.

O PDF foi escolhido porque é o buraco mais caro que a casa tem medido: 43 dos
49 documentos italianos estão guardados e fechados. Mas o desenho aqui não tem
nada de especial para PDF — amanhã, o executor de HTTP, o de Instagram e o do
navegador preenchem a mesma folha, com os mesmos campos.

    NÃO SE FAZ UM CANO ESPECIAL PARA 49 FICHEIROS.
    FAZ-SE A PRIMEIRA ESTRADA, E ESTES 49 SÃO OS PRIMEIROS A PASSAR NELA.

O EXECUTOR NÃO JULGA
--------------------
Este ficheiro não decide se um documento é relevante, se serve, se interessa.
Essa é a função da porta de admissão, e é dela que continua a ser. Aqui só se
responde a quatro perguntas técnicas:

    consegui abrir?      de qual original?      quanto texto saiu?      houve erro?

Misturar as duas coisas foi o erro que já se pagou noutro sítio: quando quem
colhe também julga, não há como saber se um item ficou de fora por não servir
ou por a ferramenta ter falhado.

COMO SE ABRE O PDF
------------------
Com `pdftotext`, que já está nesta máquina e não precisa de rede, de conta nem
de instalação. A Regra Zero mandou medir antes de escolher: procurou-se por
`pypdf`, `PyPDF2`, `pdfminer`, `fitz` e `pdfplumber` — nenhuma instalada — e
por `pdftotext`, `mutool`, `qpdf` e `gs`. Só o `pdftotext` respondeu.

⚠️ ISTO TEM UM PREÇO, E ELE FICA ESCRITO: `pdftotext` é uma ferramenta de fora
do Python. Se a máquina não a tiver, este executor devolve estado
`FERRAMENTA_AUSENTE` para todos os ficheiros — **não** finge que os PDF estão
vazios. Um executor que confunde «não tenho ferramenta» com «não há texto»
mente sobre o acervo, e a mentira fica guardada.

SEM REDE, SEM OCR
-----------------
Não abre ligação nenhuma. Não tenta OCR — nem em silêncio, nem como último
recurso. Um PDF que é fotografia de papel sai daqui com `NEEDS_OCR`, que é um
trabalho por fazer e **não** uma rejeição.

CORRER
------
    py coleta/executor_texto_de_pdf.py                 # a corrida a sério
    py coleta/executor_texto_de_pdf.py --seco          # só olha e conta
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import artefato as art  # noqa: E402

# ── A FICHA DE CAPACIDADE ───────────────────────────────────────────────────
# Todo executor tem de conseguir dizer, ANTES de correr, o que sabe fazer. Sem
# isto, o orquestrador teria de descobrir por tentativa — e descobrir por
# tentativa, numa rota paga, descobre-se com a fatura.
EXECUTOR_ID = "texto-de-pdf"
EXECUTOR_VERSION = "1"
PIPELINE_VERSION = "1"

CAPACIDADE = {
    "EXECUTOR_ID": EXECUTOR_ID,
    "VERSION": EXECUTOR_VERSION,
    "SUPPORTS": ["PDF_RAW"],
    "PRODUCES": ["TEXT_EXTRACTED"],
    "NETWORK_REQUIRED": "NO",
    "OCR": "NO",
    "CHECKPOINT": art.NAO_SE_APLICA,
    "COST_CLASS": "LOCAL",
    "FERRAMENTA_EXTERNA": "pdftotext (poppler/xpdf)",
}

# ── ONDE VIVEM AS COISAS ────────────────────────────────────────────────────
# O texto derivado NÃO fica ao lado do PDF. Fica em pasta própria, e a razão é
# a regra «armazenamento não é estado»: uma pasta é um sítio, não um selo de
# qualidade. Ao lado do PDF já vivem os seis ficheiros feitos à mão, sem ficha
# nenhuma — misturar os novos com aqueles apagaria a única diferença que
# interessa entre eles, que é ter ou não ter pai declarado.
DERIVADOS = RAIZ / "data" / "derivados" / "texto"
REGISTO = RAIZ / "data" / "derivados" / "REGISTO-DE-ARTEFATOS.json"

# Só Itália. O escopo desta frente é absoluto.
PASTAS_IT = ["data/samples", "data/collection-store/italy", "data/raw"]


def ha_ferramenta() -> bool:
    return shutil.which("pdftotext") is not None


def _e_italiano(caminho: str) -> bool:
    """Mesma regra do censo do corpo: pelo caminho, nunca pelo conteúdo."""
    p = caminho.replace("\\", "/").upper()
    for seg in p.split("/"):
        if seg.startswith("IT-") or "ITALY" in seg or "ITALIA" in seg:
            return True
    return any(r in p for r in ("PIEMONTE", "VENETO", "ARPAV", "LOMBARDIA",
                                "EMILIA", "TOSCANA", "PUGLIA", "SICILIA",
                                "ISTAT", "ISMEA"))


def os_pdf_italianos() -> list[Path]:
    achados = []
    for pasta in PASTAS_IT:
        base = RAIZ / pasta
        if not base.is_dir():
            continue
        for p in base.rglob("*.pdf"):
            rel = p.relative_to(RAIZ).as_posix()
            if _e_italiano(rel):
                achados.append(p)
    return sorted(set(achados))


def extrair(pdf: Path) -> tuple[str, str, str, dict]:
    """Tenta tirar o texto. Devolve (texto, estado, erro, medidas).

    Três saídas possíveis, e nenhuma delas é «não serve»:

      TEXT_LAYER_PRESENT  o PDF trazia texto por dentro, e saiu
      TEXT_LAYER_ABSENT   abriu bem, e não havia texto: é imagem → NEEDS_OCR
      EXTRACTION_ERROR    a ferramenta falhou — problema nosso, não do documento
    """
    if not ha_ferramenta():
        return "", art.EXTRACTION_ERROR, "FERRAMENTA_AUSENTE: pdftotext", {}
    try:
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                           capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return "", art.EXTRACTION_ERROR, "pdftotext demorou mais de 120s", {}
    except OSError as e:
        return "", art.EXTRACTION_ERROR, f"nao consegui correr pdftotext: {e}", {}

    if r.returncode != 0:
        err = (r.stderr or b"").decode("utf-8", "replace").strip()[:300]
        return "", art.EXTRACTION_ERROR, err or f"codigo {r.returncode}", {}

    texto = (r.stdout or b"").decode("utf-8", "replace")
    # PRODUZIR FICHEIRO VAZIO NÃO É SUCESSO. Um PDF que abre e não dá letra
    # nenhuma é uma fotografia de papel, e dizer «extraí com sucesso, zero
    # caracteres» seria contar um trabalho que não aconteceu.
    sem_brancos = len("".join(texto.split()))
    medidas = {"CHARACTERS": len(texto),
               "NON_WHITESPACE_CHARACTERS": sem_brancos}
    if sem_brancos == 0:
        return texto, art.TEXT_LAYER_ABSENT, "", medidas
    return texto, art.TEXT_LAYER_PRESENT, "", medidas


def carregar_registo() -> dict:
    if REGISTO.is_file():
        try:
            return json.loads(REGISTO.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"ARTEFATOS": []}


# ─────────────────────────────────────────────────────────────────────────
# A PONTE PARA O DONO CANÓNICO DA ESCRITA — desligada por omissão
# ─────────────────────────────────────────────────────────────────────────
# Este executor produz o texto. Ele NÃO escreve no banco, e não vai passar a
# escrever: a doutrina é que o executor produz o artefato e o DONO CANÓNICO o
# persiste. Nenhum executor grava só porque conhece a `SUPABASE_URL`.
#
# O que esta ponte faz é deixar o dono ser CHAMADO, quando alguém lho passar —
# `entregar_ao_dono` é `None` por omissão, e enquanto for `None` nada muda: o
# caminho antigo continua a escrever o `REGISTO-DE-ARTEFATOS.json`, como
# sempre. É o modo forward, testável, e desligado.
#
# ⚠️ E O LEGADO NÃO SE MEXE. Os 43 derivados históricos não têm `raw_asset`
# canónico que possa ser pai deles — são
# LEGACY_DERIVATION_WITHOUT_CANONICAL_RAW_PARENT. Esta ponte serve o que vier
# a seguir, e não repinta o que ficou para trás.


def correr(seco: bool = False, run_id: str = "",
           entregar_ao_dono=None) -> dict:
    """A corrida de derivação. Devolve o recibo, sempre — mesmo se falhar."""
    inicio = art.agora()
    run_id = run_id or f"DERIV-PDF-{inicio.replace(':', '').replace('-', '')}"

    ja = carregar_registo()
    # IDEMPOTÊNCIA: a chave é o que define o trabalho, não quando ele correu.
    # Mesmo original + mesmo executor + mesmo cano = mesmo resultado, e não faz
    # sentido guardá-lo duas vezes. Se qualquer um dos três mudar, é trabalho
    # novo e merece artefato novo.
    feitos = {(a.get("PARENT_SHA256"), a.get("EXECUTOR_VERSION"),
               a.get("PIPELINE_VERSION")) for a in ja["ARTEFATOS"]}

    conta = {"RAW_INPUT": 0, "RAW_CONTEUDOS_DISTINTOS": 0,
             "RAW_COPIAS_REPETIDAS": 0,
             "TEXT_LAYER_PRESENT": 0, "NEEDS_OCR": 0,
             "EXTRACTION_ERROR": 0, "RAW_UNKNOWN": 0,
             "DERIVED_EMITTED": 0, "DERIVED_LANDED": 0, "JA_EXISTIA": 0}
    novos, erros = [], []

    # O ARTEFATO É O CONTEÚDO, NÃO O CAMINHO.
    #
    # Descoberto ao correr isto pela primeira vez: seis dos PDF italianos
    # existem DUAS VEZES em disco — o mesmo documento guardado em
    # `data/collection-store/` e outra vez em `data/samples/`. São 49 caminhos
    # e 43 conteúdos diferentes.
    #
    # Se o artefato fosse o caminho, o mesmo boletim entraria duas vezes com
    # dois nomes, e mais à frente alguém contaria dois documentos onde há um.
    # Sendo o conteúdo, o artefato é um só e os dois caminhos ficam registados
    # como o que são: duas cópias da mesma coisa.
    #
    #     DUAS CÓPIAS DO MESMO FICHEIRO NÃO SÃO DOIS DOCUMENTOS.
    por_conteudo: dict = {}
    for pdf in os_pdf_italianos():
        conta["RAW_INPUT"] += 1
        pai = art.raw_do_disco(str(pdf), str(RAIZ), COUNTRY_SCOPE="IT")
        if pai.SHA256 in por_conteudo:
            por_conteudo[pai.SHA256][1].append(
                pdf.relative_to(RAIZ).as_posix())
            conta["RAW_COPIAS_REPETIDAS"] += 1
            continue
        por_conteudo[pai.SHA256] = (pdf, [pdf.relative_to(RAIZ).as_posix()],
                                    pai)
    conta["RAW_CONTEUDOS_DISTINTOS"] = len(por_conteudo)

    entregas = []
    for _sha, (pdf, caminhos, pai) in por_conteudo.items():
        # O escopo é nosso e sabemo-lo. Tudo o resto — quando, onde, em que
        # língua — continua NAO SEI, porque ninguém o provou.
        chave = (pai.SHA256, EXECUTOR_VERSION, PIPELINE_VERSION)
        if chave in feitos:
            conta["JA_EXISTIA"] += 1
            continue

        texto, estado, erro, medidas = extrair(pdf)

        if estado == art.TEXT_LAYER_PRESENT:
            conta["TEXT_LAYER_PRESENT"] += 1
        elif estado == art.TEXT_LAYER_ABSENT:
            conta["NEEDS_OCR"] += 1
        elif estado == art.EXTRACTION_ERROR:
            conta["EXTRACTION_ERROR"] += 1
            erros.append({"PDF": caminhos[0],
                          "ERRO": erro})
        else:
            conta["RAW_UNKNOWN"] += 1

        # Só nasce ficheiro quando há texto. Um NEEDS_OCR não produz derivado —
        # produz um facto sobre o original, e esse facto vai para o recibo.
        if estado != art.TEXT_LAYER_PRESENT:
            continue

        conta["DERIVED_EMITTED"] += 1
        if seco:
            continue

        DERIVADOS.mkdir(parents=True, exist_ok=True)
        alvo = DERIVADOS / (art.artifact_id(pai.SHA256, art.RAW) + ".txt")
        alvo.write_text(texto, encoding="utf-8")

        filho = art.derivado_de(
            pai, str(alvo), str(RAIZ),
            derivacao=art.TEXT_EXTRACTION,
            executor=EXECUTOR_ID, executor_versao=EXECUTOR_VERSION,
            pipeline_versao=PIPELINE_VERSION, run_id=run_id,
            estado=art.TEXT_LAYER_PRESENT,
            notas={**medidas, "PARENT_STORAGE_LOCATIONS": caminhos})

        quebras = art.conferir(filho)
        if quebras:
            # A LEI TEM DE MORDER. Se o artefato viola o contrato, não entra no
            # registo — e o motivo fica escrito, em vez de o artefato entrar
            # torto e o defeito aparecer três camadas à frente.
            erros.append({"PDF": caminhos[0],
                          "ERRO": "contrato quebrado: " + "; ".join(quebras)})
            alvo.unlink(missing_ok=True)
            continue

        novos.append(filho.para_json())
        conta["DERIVED_LANDED"] += 1

        # A PONTE. Se ninguem a ligou, isto nao acontece — e e assim que ela
        # fica desligada em producao sem precisar de uma bandeira a mais.
        if entregar_ao_dono is not None:
            entregas.append(entregar_ao_dono({
                "kind": "TEXT_EXTRACTION",
                "producer": EXECUTOR_ID,
                "producer_version": EXECUTOR_VERSION,
                "pipeline_version": PIPELINE_VERSION,
                "parameters": None,
                "serie_posicao": None,
                "media_type": "text/plain",
                "country": "IT",
                # O SHA256 DO PAI NAO VIAJA AQUI, e nem sequer como informacao.
                # Quem o le e o dono, da linha de `raw_asset`. Um campo que
                # ninguem usa e um campo que um dia alguem usa mal — e este
                # seria usado para declarar um pai que o executor nao pode
                # provar. O mesmo vale para o hash do filho, o momento da
                # derivacao e o caminho no armazem.
            }, texto.encode("utf-8")))

    if not seco and novos:
        ja["ARTEFATOS"].extend(novos)
        REGISTO.parent.mkdir(parents=True, exist_ok=True)
        REGISTO.write_text(json.dumps(ja, ensure_ascii=False, indent=1) + "\n",
                           encoding="utf-8")

    # ── A RECONCILIAÇÃO: NADA SOME EM SILÊNCIO ──────────────────────────────
    # Emitido menos aterrado tem de dar zero. Se não der, a diferença aparece
    # aqui com nome — porque um número que desaparece sem queixa é o pior tipo
    # de avaria: ninguém vai procurá-lo.
    perdidos = conta["DERIVED_EMITTED"] - conta["DERIVED_LANDED"]
    return {
        "RUN_ID": run_id,
        "STATUS": "SUCCESS" if not erros else "PARTIAL",
        # A PONTE, se alguem a ligou. Lista vazia quando esta desligada — que e
        # o estado de producao, e continua a ser.
        "ENTREGAS_AO_DONO": entregas,
        "EXECUTOR_ID": EXECUTOR_ID,
        "EXECUTOR_VERSION": EXECUTOR_VERSION,
        "PIPELINE_VERSION": PIPELINE_VERSION,
        "STARTED_AT": inicio,
        "FINISHED_AT": art.agora(),
        "COUNTRY": "IT",
        "MISSION": "derivacao de texto a partir de PDF italiano",
        "SECO": seco,
        "COUNTS": conta,
        "LOST": perdidos if not seco else 0,
        "ERRORS": erros,
        "COST_USD": 0.0,
        "COST_CLASS": "LOCAL",
        "FERRAMENTA": "pdftotext" if ha_ferramenta() else "AUSENTE",
    }


if __name__ == "__main__":
    seco = "--seco" in sys.argv
    if not ha_ferramenta():
        print("AVISO: pdftotext nao esta nesta maquina. Todos os PDF vao sair")
        print("       com EXTRACTION_ERROR — que e a verdade, e nao «vazios».")
    recibo = correr(seco=seco)
    c = recibo["COUNTS"]
    print("DERIVACAO DE TEXTO A PARTIR DE PDF · %s" % recibo["RUN_ID"])
    print("  PDF italianos olhados ..... %d" % c["RAW_INPUT"])
    print("  com camada de texto ....... %d" % c["TEXT_LAYER_PRESENT"])
    print("  precisam de OCR ........... %d" % c["NEEDS_OCR"])
    print("  erro tecnico .............. %d" % c["EXTRACTION_ERROR"])
    print("  ja tinham sido feitos ..... %d" % c["JA_EXISTIA"])
    print("  textos emitidos ........... %d" % c["DERIVED_EMITTED"])
    print("  textos guardados .......... %d" % c["DERIVED_LANDED"])
    print("  PERDIDOS .................. %d" % recibo["LOST"])
    for e in recibo["ERRORS"][:5]:
        print("    · %s — %s" % (e["PDF"], e["ERRO"][:80]))
    raise SystemExit(0 if recibo["LOST"] == 0 else 1)
