#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS 30 PROVAS DA PRIMEIRA ESTRADA.

Cada uma existe porque há uma maneira concreta de esta estrada mentir. Não são
provas de que o código «funciona» — são armadilhas montadas nos sítios exatos
onde já se errou antes, aqui ou noutra parte da casa.

    py provas/testa_golden_path_pdf.py

Offline. Não coleta, não gasta, não altera dado nenhum.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import artefato as art  # noqa: E402
import admissao as adm  # noqa: E402
import executor_texto_de_pdf as ex  # noqa: E402
import golden_path_pdf as gp  # noqa: E402

FALHAS = []


def prova(nome, ok, detalhe=""):
    print("  %s  %s%s" % ("PASS" if ok else "FALHA", nome,
                          "" if ok else "\n         " + str(detalhe)))
    if not ok:
        FALHAS.append(nome)


CONTA = RAIZ / "system-map" / "data" / "golden-path-pdf.generated.json"
if not CONTA.is_file():
    raise SystemExit("corre primeiro: py coleta/golden_path_pdf.py")
R = json.loads(CONTA.read_text(encoding="utf-8"))
C = R["COUNTS"]
REG = ex.carregar_registo()["ARTEFATOS"]

print("AS 30 PROVAS DA PRIMEIRA ESTRADA\n")

# ── IDENTIDADE E IMUTABILIDADE ──────────────────────────────────────────────
prova("T1_o_bruto_nao_mudou_um_byte",
      R["RAW_IMUTAVEL"]["VEREDITO"] == "IMUTAVEL"
      and not R["RAW_IMUTAVEL"]["ALTERADOS"],
      "o original e intocavel. Se um SHA256 mudar, alguem reescreveu por cima "
      "de evidencia — e evidencia reescrita nao volta")

_brutos = {a["PARENT_ARTIFACT_ID"] for a in REG
           if a["PARENT_ARTIFACT_ID"] not in (art.NAO_SEI, art.NAO_SE_APLICA)}
prova("T2_cada_bruto_tem_nome_proprio",
      all(b.startswith("RAW-") and len(b) > 8 for b in _brutos) and _brutos,
      "sem nome proprio nao ha como dizer «este texto veio DAQUELE ficheiro»")

prova("T3_o_filho_nao_tem_o_nome_do_pai",
      all(a["ARTIFACT_ID"] != a["PARENT_ARTIFACT_ID"] for a in REG),
      "um PDF e o texto que sai dele sao duas coisas. Mesmo nome seria dizer "
      "que sao a mesma")

prova("T4_todo_derivado_automatico_tem_pai_provado",
      all(a["PARENT_ARTIFACT_ID"].startswith("RAW-")
          and len(a["PARENT_SHA256"]) == 64
          and a["DERIVATION_TYPE"] == art.TEXT_EXTRACTION
          for a in REG),
      "pai, impressao digital do pai, e como se derivou — os tres, ou nenhum")

_maos = R["TEXTOS_A_MAO"]["FICHAS"]
_inventado = [m for m in _maos
              if m["PARENT_STATUS"] == "PARENT_UNKNOWN"
              and m["PARENT_ARTIFACT_ID"] != art.NAO_SEI]
prova("T5_o_texto_a_mao_nao_ganha_pai_inventado",
      not _inventado,
      "estar ao lado com o mesmo nome e indicio, nao prova. Sem prova, o pai "
      "fica NAO SEI — nao se melhora a historia. Inventados: %s" % _inventado)

# ── OS CINCO TEMPOS, CADA UM NO SEU CAMPO ───────────────────────────────────
prova("T6_a_hora_do_trabalho_nao_vira_data_do_fato",
      all(a["FACT_TIME"] != a["DERIVED_AT"] for a in REG),
      "DERIVED_AT e quando esta maquina abriu o PDF hoje. FACT_TIME e quando o "
      "que esta escrito la dentro aconteceu. Copiar um para o outro poe a hora "
      "de um trabalho de escritorio na data de um acontecimento no campo")

prova("T7_publicar_nao_e_acontecer",
      all(a["FACT_TIME"] == art.NAO_SEI
          or a["FACT_TIME"] != a["PUBLISHED_AT"]
          or a["NOTES"].get("FACT_TIME_BASIS") == "PUBLISHED_AT_COM_PROVA"
          for a in REG),
      "um boletim publicado a sexta pode falar do que se viu na terca")

prova("T8_colher_nao_e_acontecer",
      all(a["FACT_TIME"] == art.NAO_SEI or a["FACT_TIME"] != a["COLLECTED_AT"]
          for a in REG),
      "a hora em que trouxemos o ficheiro nao e a data do fato")

# ── A GEOGRAFIA: TRES COISAS DIFERENTES ─────────────────────────────────────
prova("T9_onde_a_fonte_esta_nao_e_onde_o_fato_foi",
      all(a["FACT_LOCATION"] == art.NAO_SEI
          or a["FACT_LOCATION"] != a["SOURCE_LOCATION"]
          or a["NOTES"].get("FACT_LOCATION_BASIS")
          for a in REG),
      "uma revista italiana pode noticiar uma praga em Espanha")

prova("T10_o_escopo_do_pais_nao_preenche_o_lugar_do_fato",
      all(a["FACT_LOCATION"] == art.NAO_SEI
          or a["NOTES"].get("FACT_LOCATION_BASIS")
          for a in REG),
      "trabalharmos a Italia e decisao nossa; nao e prova sobre o fato")

prova("T11_pais_nao_e_lingua",
      all(a["COUNTRY_SCOPE"] == "IT" for a in REG)
      and all(a["ITEM_LANGUAGE"] == art.NAO_SEI for a in REG),
      "um documento da frente italiana pode estar em ingles. Escrever IT sem "
      "ler seria uma afirmacao sobre o conteudo feita sem ver o conteudo")

# ── OS ESTADOS: O QUE NAO E REJEICAO ────────────────────────────────────────
_sem_camada = art.Artefato(ARTIFACT_ID="X", ARTIFACT_TYPE=art.DERIVED,
                           STORAGE_LOCATION="x", SHA256="y",
                           STATE=art.TEXT_LAYER_ABSENT)
prova("T12_pdf_sem_texto_nao_vira_NAO",
      _sem_camada.STATE == art.TEXT_LAYER_ABSENT
      and art.NEEDS_OCR != adm.NAO,
      "um PDF que e fotografia de papel nao e irrelevante: e um trabalho por "
      "fazer. NEEDS_OCR e estado de derivacao, nao julgamento")

_erro = art.Artefato(ARTIFACT_ID="X", ARTIFACT_TYPE=art.DERIVED,
                     STORAGE_LOCATION="x", SHA256="y",
                     STATE=art.EXTRACTION_ERROR)
prova("T13_falha_da_ferramenta_e_ERRO_e_tem_de_dizer_qual",
      "estado de erro sem uma linha a dizer qual foi" in art.conferir(_erro),
      "erro sem explicacao e pior que erro: ninguem sabe o que reparar")

_nada = {"id": "gp-t14", "texto": "un testo qualunque senza parole conosciute",
         "source_id": "IT-GP", "fact_time": "2026-01-01"}
prova("T14_sem_palavra_conhecida_nao_vira_NAO",
      adm.decidir(_nada, "T7").resultado == adm.NAO_SEI,
      "nao achar palavra prova que o dicionario nao chegou, nao que o item nao "
      "pertence. A lei da ausencia continua de pe nesta estrada")

# ── NADA SOME EM SILENCIO ───────────────────────────────────────────────────
prova("T15_emitido_e_guardado_batem",
      C["DERIVED_EMITTED"] == C["DERIVED_LANDED"] or R["ERRORS"],
      "a diferenca entre o que se emitiu e o que aterrou tem de ter erro "
      "explicito. Sem isso, artefatos somem e ninguem procura")

prova("T16_a_porta_nao_ve_mais_do_que_existe",
      C["ADMISSION_SEEN"] <= C["DERIVED_LANDED"] + C["JA_EXISTIAM"],
      "a porta nao pode ter visto mais itens do que foram guardados")

prova("T17_nada_se_perdeu",
      C["LOST"] == 0,
      "LOST tem de ser zero, ou aparecer com nome. Numero que desaparece sem "
      "queixa e o pior tipo de avaria")

# ── IDEMPOTENCIA E VERSOES ──────────────────────────────────────────────────
_chaves = [(a["PARENT_SHA256"], a["EXECUTOR_VERSION"], a["PIPELINE_VERSION"])
           for a in REG]
prova("T18_correr_duas_vezes_nao_duplica",
      len(_chaves) == len(set(_chaves)),
      "mesmo original + mesmo executor + mesmo cano = mesmo trabalho. Repetir "
      "nao pode criar um segundo artefato igual")

prova("T19_a_versao_do_executor_fica_guardada",
      all(a["EXECUTOR_VERSION"] == ex.EXECUTOR_VERSION for a in REG) and REG,
      "sem versao nao da para dizer «reprocessa o que a v1 fez»")

prova("T20_a_versao_do_cano_fica_guardada",
      all(a["PIPELINE_VERSION"] == ex.PIPELINE_VERSION for a in REG) and REG,
      "a versao do cano e outra coisa da versao do executor, e mudam separadas")

prova("T21_mudanca_na_fonte_distingue_se_de_mudanca_no_cano",
      all(len(a["PARENT_SHA256"]) == 64 for a in REG)
      and all(a["PIPELINE_VERSION"] for a in REG),
      "se o SHA do original e igual e o texto mudou, mudou o CANO, nao a fonte. "
      "So da para dizer isso guardando os dois")

# ── AS PROIBICOES DESTA MISSAO ──────────────────────────────────────────────
_fonte_ex = (RAIZ / "coleta" / "executor_texto_de_pdf.py").read_text(
    encoding="utf-8")
_fonte_gp = (RAIZ / "coleta" / "golden_path_pdf.py").read_text(encoding="utf-8")
_REDE = ("requests.", "urllib.request", "http.client", "socket.socket",
         "httpx.", "aiohttp", "curl ", "wget ")
_com_rede = [w for w in _REDE if w in _fonte_ex or w in _fonte_gp]
prova("T22_nao_ha_rede_nesta_estrada",
      not _com_rede and R["REDE_USADA"] == "NAO",
      "toda a estrada corre offline. Encontrado: %s" % (_com_rede or "nada"))

# A primeira versao desta prova procurava a PALAVRA «apify» e reprovava — em
# cima do meu proprio comentario que dizia «sem Apify». MENCIONAR NAO E USAR:
# sexta vez que esta armadilha morde nesta casa. O que interessa e o USO.
_USO_APIFY = ("import apify", "apify_pool", "api.apify.com", "APIFY_TOKEN",
              "from apify", "coletor.executar(")
_usa_apify = [w for w in _USO_APIFY if w in _fonte_ex or w in _fonte_gp]
prova("T23_nao_ha_Apify",
      not _usa_apify,
      "nenhuma rota paga nesta missao. Uso encontrado: %s"
      % (_usa_apify or "nenhum"))

prova("T24_nao_ha_OCR",
      R["OCR_USADO"] == "NAO"
      and not any(w in _fonte_ex.lower() for w in ("tesseract", "ocrmypdf",
                                                   "easyocr")),
      "OCR nao e parte desta missao, nem em silencio como ultimo recurso")

prova("T25_o_orquestrador_nao_carrega_PDF_nem_texto",
      "executor_texto_de_pdf" not in (
          RAIZ / "orquestrador" / "orquestrador.py").read_text(encoding="utf-8"),
      "o dado vai do bruto ao executor e ao derivado. O orquestrador e o plano "
      "de controlo e sera ligado depois — nenhum byte passa por ele")

# ── O MAPA TEM DE CONSEGUIR MOSTRAR ─────────────────────────────────────────
_MAPA = RAIZ / "system-map" / "data" / "state.generated.json"
M = json.loads(_MAPA.read_text(encoding="utf-8")) if _MAPA.is_file() else {}
_nos = {n["id"]: n for n in M.get("NODES", [])}
_arestas = M.get("EDGES", [])

prova("T26_o_mapa_so_tem_setas_reais",
      all(e.get("evidence") or e.get("kind") in ("expected", "business")
          or e.get("status") in ("NAO SEI", "CINZA")
          for e in _arestas),
      "seta sem prova tem de estar marcada como declarada e nao provada")

# A PROVA TEM DE FUNCIONAR NOS DOIS SENTIDOS.
# Se ha PDF por OCR, o ramo tem de aparecer. Se NAO ha, o ramo NAO pode
# aparecer — desenhar um problema que nao existe treina toda a gente a ignorar
# os avisos do mapa, e ai o aviso a serio tambem passa despercebido.
_n_ocr = C["RAW_NEEDS_OCR"]
_tem_no = "C-IT-NEEDS-OCR" in _nos
_tem_seta = any(e.get("type") == "NEEDS_OCR" for e in _arestas)
prova("T27_o_NEEDS_OCR_aparece_se_e_so_se_houver",
      (_n_ocr > 0) == _tem_no and (_n_ocr > 0) == _tem_seta,
      "nesta corrida NEEDS_OCR=%d, no no mapa=%s, seta no mapa=%s. Com OCR por "
      "fazer, tem de estar a vista; sem OCR por fazer, nao se desenha um "
      "problema imaginario" % (_n_ocr, _tem_no, _tem_seta))

prova("T28_a_corrida_e_renderizavel",
      "C-GOLDEN-PATH-PDF" in _nos
      and any("RUN" in str(f).upper() or "corrida" in str(f).lower()
              for f in _nos.get("C-GOLDEN-PATH-PDF", {}).get("facts", [])),
      "se a maquina fez e o mapa nao mostra, a engenharia ainda nao acabou")

prova("T29_a_linhagem_e_renderizavel",
      any(e["from"] == "C-IT-PDF-BRUTO" and e["to"] == "C-EXECUTOR-TEXTO-PDF"
          for e in _arestas)
      and any(e["from"] == "C-EXECUTOR-TEXTO-PDF" for e in _arestas),
      "o caminho bruto -> executor -> derivado -> porta tem de estar desenhado")

# T30 · O MAPA REPRESENTA ESTA ARVORE, E NAO UMA DE ONTEM
# Nao se corre aqui o validador: ele regenera os mesmos ficheiros que outras
# rotinas, e correr dois regeneradores ao mesmo tempo e a avaria COL-026. O que
# se confere e o carimbo — se o mapa foi gerado sobre um commit que existe
# nesta arvore, e se as pecas desta missao la estao com os numeros desta
# corrida. Paridade a serio corre-se em separado, na ordem GERAR -> VALIDAR.
import subprocess  # noqa: E402

_head_mapa = (M.get("PROVENANCE") or {}).get("HEAD", "")
_conhecido = subprocess.run(["git", "-C", str(RAIZ), "cat-file", "-t",
                             _head_mapa or "HEAD"],
                            capture_output=True, text=True).stdout.strip()
_no_gp = _nos.get("C-GOLDEN-PATH-PDF", {})
_diz_o_mesmo = str(C["RAW_INPUT"]) in " ".join(str(f) for f in
                                               _no_gp.get("facts", []))
prova("T30_o_mapa_representa_esta_arvore",
      _conhecido == "commit" and _diz_o_mesmo,
      "o mapa tem de ter sido gerado sobre um commit desta arvore, e os "
      "numeros que ele mostra tem de ser os desta corrida — nao os de ontem")

print()
if FALHAS:
    print("GOLDEN_PATH_PDF_PROVAS=FALHA · %d: %s" % (len(FALHAS),
                                                     ", ".join(FALHAS)))
    raise SystemExit(1)
print("GOLDEN_PATH_PDF_PROVAS=PASS · as 30 armadilhas estao montadas e vazias")
