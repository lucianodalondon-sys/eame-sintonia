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


# ─────────────────────────────────────────────────────────────────────────
# O MODO FORWARD — uma unidade canónica, com o pai que existe no banco
# ─────────────────────────────────────────────────────────────────────────
# A primeira ponte que escrevi aqui NÃO levava o `raw_asset_id`. Passava a
# receita e os bytes, e o dono do derivado ficava sem saber QUAL linha de
# `raw_asset` era o pai daquele PDF.
#
#     UM EXECUTOR FORWARD SEM RAW_ASSET_ID REAL NÃO TEM PAI CANÓNICO.
#
# Uma ponte assim não leva a lado nenhum: ela foi removida, e no lugar dela
# entrou esta função, que recebe o pai como CONTEXTO DA UNIDADE DE TRABALHO.
#
# E os dois modos ficam separados, de propósito:
#
#     LEGADO    `correr()` varre os PDF históricos do Git e escreve o
#               REGISTO-DE-ARTEFATOS.json. O writer NÃO entra. Os 43 não têm
#               `raw_asset` canónico que possa ser pai deles, e inventar um
#               seria fabricar a coleta que nunca foi registada.
#
#     FORWARD   `derivar_um()` recebe UM `raw_asset_id` real e o PDF já
#               materializado, e entrega ao dono canónico.
#
# Nunca misturados. O executor continua a NÃO conhecer banco: ele produz o
# texto, e quem persiste é o dono.


def derivar_um(raw_asset_id, pdf, armazem, memoria, relogio=None) -> dict:
    """Um PDF, um pai canónico, um derivado — pelo dono da escrita.

    O que este executor entrega ao dono: a **receita** e os **bytes**. Ele não
    calcula `parent_sha256`, `parameters_hash`, `sha256` do filho, `derived_at`
    nem `storage_path` — esses são do dono, e é isso que impede um executor de
    declarar uma linhagem que não pode provar.

    O `raw_asset_id` vem de fora porque é o **contexto da unidade de
    trabalho**: quem manda derivar já sabe de que bruto se trata. O executor
    não o inventa, e não o adivinha do nome do ficheiro.
    """
    from guarda.preservar_derivado import agora_utc, preservar_derivado

    texto, estado, erro, medidas = extrair(Path(pdf))
    if estado != art.TEXT_LAYER_PRESENT:
        # Sem camada de texto nao ha artefato. Isso e um facto sobre o
        # ORIGINAL, e vai no recibo — nao vira linha de derivado.
        return {"ESTADO": "SEM_DERIVADO", "MOTIVO_DO_EXECUTOR": estado,
                "ERRO": erro, "MEDIDAS": medidas}

    return preservar_derivado(
        {"raw_asset_id": raw_asset_id,
         "kind": "TEXT_EXTRACTION",
         "producer": EXECUTOR_ID,
         "producer_version": EXECUTOR_VERSION,
         "pipeline_version": PIPELINE_VERSION,
         "parameters": None,
         "serie_posicao": None,
         "media_type": "text/plain"},
        texto.encode("utf-8"), armazem, memoria,
        relogio=relogio or agora_utc)


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


def emitir_rastro(banco, run_id, conta, perdidos, erros, inicio,
                  ferramenta_presente=True, source_id=None,
                  route_class_id=None):
    """O que esta corrida fez, dito na língua comum de `rastro_da_coleta`.

    ⚠️ ISTO NÃO INVENTA NÚMERO NENHUM. Cada valor vem de `conta`, que já era
    calculado. A tradução é só de nome, e é ela que faltava: os números
    existiam e ninguém lá fora os conseguia ler.

    Três etapas, porque três foi o que aconteceu de verdade:

        RAW      quantos ficheiros se olharam, e quantos conteúdos distintos
        DERIVED  quantos textos saíram, e por que os outros não saíram
        READY    quantos aterraram no registo

    ⚠️ E O GRÃO MUDA NO MEIO. `RAW` conta em CAMINHO; `DERIVED` conta em
    CONTEÚDO. Não são a mesma unidade, e por isso não se dividem: 49 caminhos
    dão 43 conteúdos porque seis boletins estão guardados duas vezes.

        DUAS CÓPIAS DO MESMO FICHEIRO NÃO SÃO DOIS DOCUMENTOS.

    Por isso as cópias repetidas entram como `reused`, e não como `rejected`:
    ninguém as recusou, elas já cá estavam.
    """
    import rastro_da_coleta as rastro   # noqa: E402  (a gaveta resolve o path)

    # ⚠️ A IDENTIDADE NÃO NASCE AQUI, E POR ISSO NÃO SE INVENTA AQUI.
    # Este ficheiro escrevia `source_id="IT-PDF-ITALIANOS"` e a fronteira
    # escrevia `IT-CORPUS-PDF` — dois nomes para a mesma corrida, e NENHUM dos
    # dois existe no catálogo de fontes. A mesma coleta tinha uma identidade
    # quando corria bem e outra quando o executor morria cedo.
    #
    #     A LOCALIZAÇÃO DA FALHA NÃO PODE MUDAR A IDENTIDADE DA FONTE.
    #
    # E MEDIDO: os 49 PDF atravessam OITO `source_id` reais (IT-T2-001,
    # IT-T2-002, IT-T3-002, IT-T3-008, IT-T3-010, IT-T3-011, IT-T4-001,
    # IT-T5-003) em 23 ficheiros, e os outros 26 não têm `source_id` nenhum
    # derivável do caminho. NÃO HÁ um `source_id` defensável para a corrida
    # inteira, e a `route_class` não está registada por item em lado nenhum:
    # nem no `collection-store`, nem no `collection-ledger`.
    #
    #     UM ID DE RASTREIO INVENTADO É PIOR DO QUE UNKNOWN.
    #
    # `etapa_da_corrida` já aceita NULL nos dois campos — a representação
    # honesta já existia, e era só não a contornar. Quem PROVAR a identidade
    # passa-a por parâmetro; quem não prova deixa vazio.
    comum = {"run_id": run_id, "source_id": source_id,
             "route_class_id": route_class_id, "actor": EXECUTOR_ID,
             "actor_version": EXECUTOR_VERSION,
             "policy_version": PIPELINE_VERSION}

    # RAW · o que se olhou. A entrada é CAMINHO; a saída é CONTEÚDO.
    rastro.registrar(
        banco, etapa="RAW", estado="PASS",
        input_grain="caminho de ficheiro", input_count=conta["RAW_INPUT"],
        output_grain="conteudo distinto",
        output_count=conta["RAW_CONTEUDOS_DISTINTOS"],
        cardinalidade="N:1",
        passed=conta["RAW_CONTEUDOS_DISTINTOS"],
        reused=conta["RAW_COPIAS_REPETIDAS"],
        **comum)

    # DERIVED · o que saiu, e por que o resto não saiu.
    # ⚠️ `JA_EXISTIA` é `reused`, não `rejected`: ninguém o recusou.
    # ⚠️ `NEEDS_OCR` é `rejected`, não `error`: o PDF não tem camada de texto,
    #    e isso é uma propriedade DELE — a ferramenta não falhou.
    entrada_d = conta["RAW_CONTEUDOS_DISTINTOS"]
    houve_erro = conta["EXTRACTION_ERROR"] > 0
    # ⚠️ A PERDA CALCULA-SE AQUI, E NAO SE ACEITA DE FORA.
    # `perdidos` chegava por parametro e podia DISCORDAR do recibo: um chamador
    # que dissesse 0 com 34 emitidos e 0 aterrados abria um buraco de 34 na
    # contabilidade sem ninguem reclamar. Os dois numeros estao aqui — entao a
    # conta faz-se aqui, e ninguem a pode contradizer.
    perdidos = conta["DERIVED_EMITTED"] - conta["DERIVED_LANDED"]
    rastro.registrar(
        banco, etapa="DERIVED",
        estado=("FAIL" if houve_erro
                else ("PARTIAL" if perdidos else "PASS")),
        edge_from="RAW",
        input_grain="conteudo distinto", input_count=entrada_d,
        # ⚠️ PASSOU E O QUE ATERROU, NÃO O QUE FOI EMITIDO.
        # Um texto emitido que não chegou ao registo não passou — sumiu. Ele
        # entra em `unknown` («mediu-se e não se sabe onde foi»), que é o que
        # impede a perda de se diluir num número de sucesso. Isto vivia numa
        # etapa `READY` à parte; ver a nota abaixo sobre por que ela saiu.
        output_grain="texto derivado", output_count=conta["DERIVED_LANDED"],
        passed=conta["DERIVED_LANDED"],
        rejected=conta["NEEDS_OCR"],
        error=conta["EXTRACTION_ERROR"],
        unknown=conta["RAW_UNKNOWN"] + perdidos,
        reused=conta["JA_EXISTIA"],
        # ⚠️ `ERROR` NAO E UM ESTADO CANONICO. A primeira versao escrevia
        # `canonical_state="ERROR"`, e `ERROR` nao existe em `falhas.py` — e um
        # DESTINO DE ITEM, de `telemetria.py`, e o O8C separou as duas coisas
        # exatamente para isto nao acontecer. O leitor via um estado que o dono
        # nunca declarou, e nenhuma trava reclamava.
        #
        #     FAILURE STATE VEM DO DONO, OU NAO E FAILURE STATE.
        #
        # A ferramenta em falta e `EXECUTOR_UNAVAILABLE`, camada EXECUTOR:
        # defeito NOSSO, e nao uma afirmacao sobre a fonte. Os PDF continuam
        # bons — ROTA CAIDA NAO E FONTE CAIDA.
        canonical_state=(("UNKNOWN_ERROR" if ferramenta_presente
                          else "EXECUTOR_UNAVAILABLE") if houve_erro else
                         ("ITEM_ERROR" if perdidos else None)),
        diagnostic_code=(None if houve_erro else
                         ("FLOW_UNACCOUNTED_INPUT" if perdidos else None)),
        last_good_artifact=("RAW" if houve_erro else
                            ("RAW" if perdidos else None)),
        error_class="EXTRACTION_ERROR" if houve_erro else None,
        error_message=(erros[0].get("ERRO") if erros else None),
        **comum)

    # ─────────────────────────────────────────────────────────────────────
    # ⚠️ NÃO SE EMITE `READY` AQUI, E ISTO É UMA LEI E NÃO UMA OMISSÃO.
    #
    # Este ficheiro emitia uma etapa `READY` e chamava-lhe «o que aterrou no
    # registo». Mas `READY` já tem dono, e é a COL-LAW-043:
    #
    #     `READY_FOR_INTELIGENCIA` significa que os CONTRATOS OBRIGATÓRIOS da
    #     coleta e da preparação foram satisfeitos. NÃO DEVE significar «o
    #     ficheiro existe» nem «o workflow terminou».
    #
    # E o contrato de saída de READY exige `ADMITIDO_POR` — e a admissão é de
    # outro dono, que este executor declara em voz alta não ser. A COL-LAW-044
    # separa os estados: RAW · DERIVED · ADMITTED · READY. Chamar READY a um
    # texto guardado saltava DOIS estados de uma vez.
    #
    #     DERIVED PERSISTED != READY.
    #
    # E não se inventou uma etapa `DERIVED_PERSISTED` para a substituir: o que
    # aterrou é `passed` de DERIVED, e o que se emitiu e não aterrou é
    # `unknown`. A informação não se perdeu — deixou de ter um nome que
    # prometia mais do que ela é.
    #
    # Enquanto ninguém atravessar STRUCTURED e ADMISSION, este caminho termina
    # em DERIVED. E terminar em DERIVED é a verdade.

def correr(seco: bool = False, run_id: str = "", rastro=None,
           source_id=None, route_class_id=None) -> dict:
    """A corrida de derivação. Devolve o recibo, sempre — mesmo se falhar.

    `rastro` é um banco onde escrever a telemetria, ou `None` para não emitir.
    A seco, passa-se `medidas/banco_no_seco.BancoNoSeco()`."""
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

    # ── O RASTRO: A CORRIDA PASSA A CONTAR-SE ───────────────────────────────
    # ⚠️ INSTRUMENTAR NAO E FAZER ETAPA NOVA.
    #
    # Nada aqui muda o que este executor FAZ. Ele já contava tudo isto em
    # `conta`; o que faltava era dizê-lo em voz alta, na língua comum, para o
    # scanner poder ler. O contrato já existia — e nenhum executor o falava.
    #
    #     MODULE WORKS != EDGE WORKS != FLOW WORKS.
    #
    # O `banco` é injectado: a seco vai para memória, ao vivo iria para o
    # Postgres pelo dono canónico. Instrumentar NÃO pode exigir escrever em
    # produção — senão só se saberia se funciona no dia em que já fosse tarde.
    if rastro is not None:
        emitir_rastro(rastro, run_id, conta, perdidos, erros, inicio,
                      ferramenta_presente=ha_ferramenta(),
                      source_id=source_id,
                      route_class_id=route_class_id)

    return {
        "RUN_ID": run_id,
        "STATUS": "SUCCESS" if not erros else "PARTIAL",
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
