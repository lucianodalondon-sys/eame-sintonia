#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PONTE DE MÍDIA ATRAVESSA? — a metade que NÃO precisa de banco.

    py provas/a_ponte_de_midia_atravessa.py

O QUE ESTA PROVA MEDE, E ONDE ELA PARA DE PROPÓSITO
----------------------------------------------------
    ESPÉCIE DECLARADA -> ESCOLHA DO EXECUTOR -> ÁUDIO -> ASR -> TRANSCRIPT

Tudo isto corre sem PostgreSQL, sem rede e sem escrever no banco. O que vem a
seguir — `DERIVED` na tabela, `STRUCTURED`, `ADMISSION`, `READY`, `SALA` —
**exige banco**, e nesta máquina não há:

    psql · pg_ctl · initdb · docker · psycopg   ->  TODOS AUSENTES, medido
    guarda/memoria_descartavel.py               ->  SQLite, e o proprio
                                                    ficheiro escreve que NAO
                                                    substitui Postgres

Por isso esta prova NÃO tenta. Fingir que um SQLite prova semântica de Postgres
seria a mesma família de defeito que esta casa persegue há missões:

    SKIP != PASS.  E SQLITE != POSTGRES.

⚠️ E ELA NÃO ADQUIRE NADA
--------------------------
O canário é um ficheiro que já estava preservado nesta casa desde 2026-09-02.
Nenhum byte novo, nenhuma rede de conteúdo, nenhum dólar.

    NEW_MEDIA_ACQUISITION = NO · RUN_TYPE = REPROCESS.

E ele NÃO é canário por ser do Instagram, nem por ser da Bayer: é canário por
ter bytes reais com fala real. A ponte não sabe de onde ele veio, e esta prova
não lhe conta.
"""
import io
import json
import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
import ingresso as ing                             # noqa: E402
import executor_transcricao_midia as midia         # noqa: E402
import executor_texto_de_pdf as pdf                # noqa: E402
import proveniencia as pv                          # noqa: E402

SAIDA = os.path.join(RAIZ, "system-map", "data", "ponte-de-midia.generated.json")

#: O canário. Fora do Git e fora deste worktree — e por isso o caminho é
#: procurado, não afirmado. Um caminho absoluto escrito à mão numa prova é um
#: literal que morre na primeira máquina diferente.
CANDIDATOS = (
    os.path.join("C:/eame-sintonia", "data", "samples", "INSTAGRAM-TRANSCRICOES",
                 "audio-cache", "DcNkh7LCW4u.mp4"),
    os.path.join(RAIZ, "data", "samples", "INSTAGRAM-TRANSCRICOES",
                 "audio-cache", "DcNkh7LCW4u.mp4"),
)

FALHAS, PASSOU, NAO_EXERCITADO = [], [], []
achados = {}


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def N(nome, porque):
    """NÃO EXERCITADO. Não é PASS e não é FALHA — e tem de aparecer."""
    NAO_EXERCITADO.append(nome)
    print("  ----  %s\n        NOT_EXERCISED: %s" % (nome, porque))


def _mede(nome, valor, porque=""):
    achados[nome] = {"VALOR": valor, "PORQUE": porque}
    print("  %-32s = %-22s %s" % (nome, valor, porque[:52]))
    return valor


print("A PONTE DE MIDIA ATRAVESSA?")
print()

# ── 1 · A ESCOLHA DO EXECUTOR, POR ESPÉCIE DECLARADA ──────────────────────
print("  A ESCOLHA")
ESPERADO = (
    ("application/pdf", pdf.EXECUTOR_ID),
    ("video/mp4", midia.EXECUTOR_ID),
    ("video/quicktime", midia.EXECUTOR_ID),
    ("video/webm", midia.EXECUTOR_ID),
    ("audio/mpeg", midia.EXECUTOR_ID),
    ("audio/x-m4a", midia.EXECUTOR_ID),
    ("audio/flac", midia.EXECUTOR_ID),
    # Com parâmetros no tipo — `video/mp4; codecs=avc1` é um `media_type`
    # legítimo, e um `==` cru falharia aqui em silêncio.
    ("video/mp4; codecs=\"avc1.4d401e\"", midia.EXECUTOR_ID),
    # Espécies que NENHUM executor de derivação abre. `None` é a resposta
    # certa e quer dizer NOT_APPLICABLE — nunca FAIL.
    ("text/html", None),
    ("application/json", None),
)
erros = []
for tipo, quem in ESPERADO:
    mod = ing.executor_para(tipo)
    obtido = getattr(mod, "EXECUTOR_ID", None)
    if obtido != quem:
        erros.append("%s -> %s (esperado %s)" % (tipo, obtido, quem))
T("cada especie declarada vai ao executor que a declara", not erros,
  " · ".join(erros))

# ⚠️ O ATAQUE PRINCIPAL DESTA MISSÃO, E ELE TEM DE FALHAR.
foi_ao_pdf = [t for t, _ in ESPERADO
              if t.split("/")[0] in ("video", "audio")
              and getattr(ing.executor_para(t), "EXECUTOR_ID", None) == pdf.EXECUTOR_ID]
_mede("PDF_EXECUTOR_SELECTED_FOR_VIDEO", "NO" if not foi_ao_pdf else "YES",
      "nenhuma especie de midia foi encaminhada ao extrator de PDF"
      if not foi_ao_pdf else "FOI: %s" % foi_ao_pdf)
T("nenhum video ou audio chega ao pdftotext", not foi_ao_pdf, str(foi_ao_pdf))

# ── 2 · A ESPÉCIE DECLARADA VENCE A EXTENSÃO ──────────────────────────────
# A lei é de `leis/artefato.py` e não se reescreve aqui: esta prova só confirma
# que ela CHEGA à escolha. Um ficheiro chamado `.pdf` cujos bytes foram
# observados como `video/mp4` tem de ir ao executor de mídia.
#
#     DECLARADO PELO OBSERVADOR > DEDUZIDO DO NOME > NAO SEI.
pela_declaracao = getattr(ing.executor_para("video/mp4"), "EXECUTOR_ID", None)
T("a especie declarada decide, e o nome do ficheiro nao entra na conta",
  pela_declaracao == midia.EXECUTOR_ID,
  "`video/mp4` foi para %s" % pela_declaracao)

# E o outro lado da mesma lei: sem espécie declarada, a porta deixa TENTAR.
T("sem especie declarada a porta nao encolhe a coleta",
  ing._quem_deriva_aceita(None) is True and ing.executor_para(None) is None,
  "ausencia de evidencia virou evidencia de ausencia")

# ── 3 · O CANÁRIO EXISTE, E É MEDIDO E NÃO AFIRMADO ───────────────────────
print()
print("  O CANARIO")
canario = next((c for c in CANDIDATOS if os.path.isfile(c)), None)
if not canario:
    _mede("CANARIO", "AUSENTE", "nenhum dos caminhos conhecidos tem o ficheiro")
    N("a ponte transcreve midia real", "o canario nao esta nesta maquina")
    N("TEXT_KIND sai TRANSCRIPT", "sem canario nao ha o que transcrever")
else:
    seco = midia._seco(canario)
    _mede("CANARIO_BYTES", str(seco["BYTES"]), os.path.basename(canario))
    _mede("CANARIO_DURACAO_S", str(seco["DURACAO_S"]), "medido por ffprobe")
    _mede("CANARIO_FLUXOS", "imagem=%s som=%s" % (seco["FLUXOS_IMAGEM"],
                                                  seco["FLUXOS_SOM"]),
          "um contentor de video COM faixa de som")
    T("o canario tem faixa de som, medida e nao suposta",
      seco["TEM_FAIXA_DE_AUDIO"] is True, seco["PORQUE"])

    # ── 4 · A TRAVESSIA REAL ──────────────────────────────────────────────
    print()
    print("  A TRAVESSIA")
    if not (seco["FFMPEG_PRESENTE"] and seco["ASR_DISPONIVEL"]):
        N("a ponte transcreve midia real",
          "ffmpeg=%s asr=%s — ferramenta que falta NAO e documento quebrado"
          % (seco["FFMPEG_PRESENTE"], seco["ASR_DISPONIVEL"]))
    else:
        t0 = time.time()
        r = midia.transcrever_ficheiro(canario)
        gasto = round(time.time() - t0, 2)
        estado = r.get("TRANSCRIPT_STATE")
        texto = r.get("TRANSCRIPT") or ""
        _mede("AUDIO_DERIVATION_EXECUTED",
              "PROVEN" if r.get("AUDIO_EXTRACTED_BYTES") else "NOT_PROVEN",
              "%s bytes de WAV 16kHz mono" % r.get("AUDIO_EXTRACTED_BYTES"))
        _mede("ASR_EXECUTED", "PROVEN" if estado == "OK" else estado,
              "pelo dono unico: %s" % midia.CAPACIDADE["ASR_OWNER"])
        _mede("TRANSCRIPT_CHARS", str(len(texto)), "caracteres de fala real")
        _mede("ASR_DEVICE_USED", str(r.get("ASR_DEVICE_USED")),
              "quem decidiu foi o dono do ASR, nao esta ponte")
        _mede("ASR_MODEL", str(r.get("ASR_MODEL")), "")
        _mede("WALL_SECONDS", str(gasto), "relogio de parede desta prova")

        T("a ponte tira audio do video e transcreve",
          estado == "OK" and len(texto) > 0,
          "estado=%s chars=%d" % (estado, len(texto)))

        # ── 5 · O CONTRATO DO TEXTO ───────────────────────────────────────
        print()
        print("  O CONTRATO DO TEXTO")
        _mede("TEXT_KIND", midia.TEXT_KIND, "produzido por ASR desta casa")
        _mede("TEXT_RELATION", midia.TEXT_RELATION, "nao foi traduzido")
        _mede("LANGUAGE", str(r.get("LANGUAGE")), "")
        _mede("LANGUAGE_SOURCE", str(r.get("LANGUAGE_SOURCE")),
              "DETECTED = a maquina ouviu; DECLARED = alguem provou antes")
        _mede("LANGUAGE_CONFIDENCE", str(r.get("LANGUAGE_CONFIDENCE")), "")

        T("o que sai e TRANSCRIPT, e nunca CAPTION",
          midia.TEXT_KIND == pv.TRANSCRIPT
          and midia.TEXT_KIND != pv.NATIVE_CAPTION,
          "TEXT_KIND=%s" % midia.TEXT_KIND)
        T("a relacao e ORIGINAL — esta missao nao traduz",
          midia.TEXT_RELATION == pv.ORIGINAL, midia.TEXT_RELATION)
        T("a lingua vem do reconhecedor, e diz de onde veio",
          bool(r.get("LANGUAGE")) and r.get("LANGUAGE") != midia.fl.NAO_SEI
          and r.get("LANGUAGE_SOURCE") in ("DETECTED", "DECLARED"),
          "LANGUAGE=%s SOURCE=%s" % (r.get("LANGUAGE"), r.get("LANGUAGE_SOURCE")))

        # ⚠️ A LÍNGUA NÃO PODE VIR DO PAÍS, E ESTE É O CONTROLO.
        # O canário é de uma conta italiana. Se esta ponte inferisse língua por
        # país, o campo sairia `it` mesmo com o áudio em inglês — e ninguém
        # notava. A prova de que não infere é que `LANGUAGE_SOURCE` diz
        # `DETECTED` e traz confiança medida ao lado.
        T("a lingua NAO foi inferida por pais, conta ou caminho",
          r.get("LANGUAGE_SOURCE") == "DETECTED"
          and isinstance(r.get("LANGUAGE_CONFIDENCE"), (int, float)),
          "sem confianca medida nao se distingue detectado de adivinhado")

        achados["TRANSCRIPT_AMOSTRA"] = {"VALOR": texto[:180], "PORQUE":
                                         "primeiros 180 caracteres, para conferir a olho"}

# ── 6 · O QUE ESTA PROVA NAO EXERCITA, E DIZ QUE NAO EXERCITA ─────────────
print()
print("  O QUE FICA POR EXERCITAR AQUI")
for etapa, porque in (
        ("DERIVED_CREATED", "escrever a linha exige banco; nao ha Postgres nesta maquina"),
        ("STRUCTURED_CREATED", "depende de DERIVED no banco"),
        ("ADMISSION_EXECUTED", "depende de STRUCTURED; e `admissao` importa `fcntl`, ausente no Windows"),
        ("READY_HANDLING", "depende de ADMISSION"),
        ("WAITING_ROOM_HANDLING", "depende de READY"),
        ("RETRY_NAO_DUPLICA", "duas corridas so se distinguem com banco")):
    N(etapa, porque)
    _mede(etapa, "NOT_EXERCISED", porque)

estado_final = {
    "O_QUE_ISTO_E": ("Se a ponte generica de midia escolhe o executor certo pela "
                     "especie DECLARADA e transcreve midia real — sem banco, sem "
                     "rede e sem adquirir nada."),
    "COMO_REFAZER": "py provas/a_ponte_de_midia_atravessa.py",
    "A_LEI": ("DECLARADO PELO OBSERVADOR > DEDUZIDO DO NOME > NAO SEI · "
              "CAPTION != TRANSCRIPT · SKIP != PASS · SQLITE != POSTGRES"),
    "NEW_MEDIA_ACQUISITION": "NO",
    "RUN_TYPE": "REPROCESS",
    "CANARIO": canario,
    "MEDIDO": achados,
    "NAO_EXERCITADO": NAO_EXERCITADO,
    "ONDE_A_ESTRADA_CONTINUA": (
        "coleta/rota_forward_documento.py leva DERIVED -> STRUCTURED -> "
        "ADMISSION -> READY -> SALA, e ja existia. O que faltava era quem "
        "produzisse o DERIVED a partir de midia, e e isso que esta ponte faz."),
}
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with io.open(SAIDA, "w", encoding="utf-8") as f:
    json.dump(estado_final, f, ensure_ascii=False, indent=1)
    f.write("\n")

print()
print("  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
print()
print("PONTE_DE_MIDIA = %s · %d passaram · %d falharam · %d nao exercitados"
      % ("MEDIDO" if not FALHAS else "FALHOU", len(PASSOU), len(FALHAS),
         len(NAO_EXERCITADO)))
raise SystemExit(1 if FALHAS else 0)
