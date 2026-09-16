#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM — vinte e oito ataques a estrada que acabou de levar material a Sala.

    BANCO_DESCARTAVEL_URL=postgresql://postgres:descartavel@localhost:5432/descartavel \\
        python3 provas/red_team_collection_ate_a_sala.py

A REGRA DESTE FICHEIRO
----------------------
Cada ataque tenta fazer o sistema ACEITAR uma coisa falsa. Um ataque que passa e
um SOBREVIVENTE, e sobrevivente e defeito — nao curiosidade.

    RED_TEAM_SURVIVORS = 0, ou a missao nao fecha.

⚠️ E NENHUM ATAQUE E CONTRA UM SIMULACRO. Onde ha banco, e o Postgres real com
a cadeia canonica aplicada; onde ha porta, e `admissao.decidir()`; onde ha Sala,
e `sala_de_espera` com o backend canonico. Atacar uma reimplementacao amiga
mede a reimplementacao.
"""
import io
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
import admissao as adm                             # noqa: E402
import artefato as art                             # noqa: E402
import ingresso as ing                             # noqa: E402
import retorno_da_coleta as rdc                    # noqa: E402
import sala_de_espera as espera                    # noqa: E402
import territorios as terr                         # noqa: E402

SAIDA = os.path.join(RAIZ, "system-map", "data", "red-team-sala.generated.json")

SOBREVIVENTES, MORTOS = [], []


def ataque(n, nome, morreu, detalhe=""):
    """`morreu = True` quer dizer que o sistema RECUSOU o ataque."""
    (MORTOS if morreu else SOBREVIVENTES).append({"N": n, "NOME": nome,
                                                  "DETALHE": detalhe})
    print("  %s  %2d · %s%s" % ("morto    " if morreu else "SOBREVIVEU",
                                n, nome,
                                ("" if morreu else "\n           " + detalhe)))


def _psql(url, sql):
    r = subprocess.run(["psql", "-X", "-q", "-A", "-t", "-F", "\x1f",
                        "-v", "ON_ERROR_STOP=1", "-c", sql, url],
                       capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


url = os.environ.get("BANCO_DESCARTAVEL_URL")
print("RED TEAM — COLLECTION ATE A SALA")
print()

# ═══════════════════════════════════════════════════════════════════════
# OS TEMPOS
# ═══════════════════════════════════════════════════════════════════════
d = adm._tem_quando({"published_at": "2026-09-10"})
ataque(1, "published_at tentando virar FACT_TIME",
       d[2].get("que_tempo") == "PUBLICATION_TIME"
       and d[2].get("fact_time") == "NAO SEI",
       "a porta aceitou a data de publicacao como tempo do fato: %s" % (d,))

item = {"id": "x", "texto": "malattia e insetto nelle trappole", "source_id": "S",
        "published_at": "2026-09-10", "artifact_type": "DERIVED",
        "parent_sha256": "a" * 64}
dec = adm.decidir(item, "T3")
pronto = adm.pronto_para_inteligencia(item, dec) if dec.resultado == adm.SIM else {}
ataque(2, "published_at atravessando ate FACT_TIME no contrato READY",
       pronto.get("FACT_TIME") == "NAO SEI",
       "FACT_TIME saiu %r" % pronto.get("FACT_TIME"))

a = art.Artefato(ARTIFACT_ID="x", ARTIFACT_TYPE=art.RAW,
                 STORAGE_LOCATION="x/y.pdf", SHA256="a" * 64,
                 FACT_TIME="2026-09-10", COLLECTED_AT="2026-09-10")
ataque(3, "FACT_TIME igual a COLLECTED_AT sem prova",
       any("FACT_TIME == COLLECTED_AT" in q for q in art.conferir(a)),
       "o contrato comum deixou passar: %s" % art.conferir(a))

ataque(4, "collected_time / captured_at com nomes divergentes",
       "COLLECTED_AT" in ing.PARA_A_PORTA
       and ing.PARA_A_PORTA["COLLECTED_AT"] == "captured_at"
       and "COLLECTED_AT" in ing.DO_COLETOR,
       "a fronteira nao tem um nome so para o tempo da colheita")

r = ing.conferir_fronteira({"SOURCE_ID": "S", "ARTIFACT_TYPE": "DERIVED"})
ataque(5, "a fronteira calando um campo ausente",
       "COLLECTED_AT" in r["AUSENTES"],
       "a fronteira nao acusou COLLECTED_AT ausente: %s" % r)

# ═══════════════════════════════════════════════════════════════════════
# A LINHAGEM
# ═══════════════════════════════════════════════════════════════════════
i2 = {"id": "v", "texto": "malattia e insetto nelle trappole", "source_id": "S",
      "fact_time": "2026-05-02"}
d2 = adm.decidir(i2, "T3")
p2 = adm.pronto_para_inteligencia(i2, d2)
ataque(6, "READY sem raw_observation_id fingindo ter um",
       p2["RAW_OBSERVATION_ID"] == "NAO SEI",
       "fabricou %r" % p2["RAW_OBSERVATION_ID"])

i3 = dict(i2, raw_asset_id=0)
p3 = adm.pronto_para_inteligencia(i3, adm.decidir(i3, "T3"))
ataque(7, "id falsy virando NAO SEI em silencio (o `or` que apaga o zero)",
       p3["RAW_OBSERVATION_ID"] == 0,
       "o id 0 virou %r" % p3["RAW_OBSERVATION_ID"])

i4 = dict(i2, sha256="b" * 64, url="http://x/y.pdf")
p4 = adm.pronto_para_inteligencia(i4, adm.decidir(i4, "T3"))
ataque(8, "raw_observation_id derivado do sha256 ou da URL",
       p4["RAW_OBSERVATION_ID"] == "NAO SEI",
       "derivou %r de sha/url" % p4["RAW_OBSERVATION_ID"])

ataque(9, "video STRUCTURED sem lineage entrando como colheita",
       rdc.ENTRAM_NO_INGRESSO == (rdc.COLHEITA,),
       "outra especie alem de COLHEITA atravessa: %s" % (rdc.ENTRAM_NO_INGRESSO,))

# ═══════════════════════════════════════════════════════════════════════
# OS ESTADOS QUE NAO SE COLAPSAM
# ═══════════════════════════════════════════════════════════════════════
ataque(10, "UNKNOWN virando NO na porta",
       adm.NAO_SEI != adm.NAO
       and adm._do_universo({"texto": "aaaa bbbb"}, "T3",
                            adm.PERGUNTAS_DO_UNIVERSO["T3"])[0] == adm.NAO_SEI,
       "texto sem vocabulario nenhum devolveu NAO em vez de NAO_SEI")

ataque(11, "um indicio solto sendo promovido a SIM",
       adm._do_universo({"texto": "una malattia fogliare isolata"}, "T3",
                        adm.PERGUNTAS_DO_UNIVERSO["T3"])[0] == adm.NAO_SEI,
       "uma palavra so promoveu o item")

import pedido as ped                               # noqa: E402
ataque(12, "ERROR e REJECTED no mesmo balde",
       ped.ERRO != ped.REJEITADO and ped.NAO_SEI != ped.REJEITADO,
       "os estados colapsaram")

import telemetria as tel                           # noqa: E402
ataque(13, "REUSED virando PRODUCED",
       espera.POUSOU != espera.JA_ESTAVA
       and espera.JA_ESTAVA in tel.DESTINOS_DO_ITEM,
       "pousou e ja-estava sao a mesma palavra")

# ═══════════════════════════════════════════════════════════════════════
# A GEOGRAFIA
# ═══════════════════════════════════════════════════════════════════════
a2 = art.Artefato(ARTIFACT_ID="x", ARTIFACT_TYPE=art.RAW,
                  STORAGE_LOCATION="x/y.pdf", SHA256="a" * 64,
                  SOURCE_LOCATION="IT", FACT_LOCATION="IT")
ataque(14, "SOURCE_LOCATION virando FACT_LOCATION",
       any("FACT_LOCATION" in q for q in art.conferir(a2)),
       "o contrato deixou copiar o lugar da fonte para o lugar do fato: %s"
       % art.conferir(a2))

i5 = dict(i2, source_location="IT")
p5 = adm.pronto_para_inteligencia(i5, adm.decidir(i5, "T3"))
ataque(15, "FACT_LOCATION herdando o SOURCE_LOCATION no READY",
       p5["FACT_LOCATION"] == "NAO SEI",
       "FACT_LOCATION saiu %r" % p5["FACT_LOCATION"])

# ═══════════════════════════════════════════════════════════════════════
# A TAXONOMIA
# ═══════════════════════════════════════════════════════════════════════
ataque(16, "T7 «ciencia» seleccionando cooperativa",
       terr.do_apelido("ciencia") == "T5"
       and terr.nome("T7") == "TECHNICAL NETWORK",
       "ciencia aponta para %s" % terr.do_apelido("ciencia"))

ataque(17, "uma quarta tabela de territorios nascendo nas chaves da admissao",
       set(adm.PERGUNTAS_DO_UNIVERSO) <= set(terr.TERRITORIOS),
       "chaves que o dono nao conhece: %s"
       % sorted(set(adm.PERGUNTAS_DO_UNIVERSO) - set(terr.TERRITORIOS)))

ataque(18, "T13 sendo renomeado para «Outro» e perdendo a divida",
       terr.TERRITORIOS.get("T13", {}).get("ESTADO") == "EM_DIVIDA"
       and terr.nome("T13") == "DISTRIBUTION",
       "T13 saiu como %r" % terr.nome("T13"))

# ═══════════════════════════════════════════════════════════════════════
# O TEXTO
# ═══════════════════════════════════════════════════════════════════════
fonte_gp = io.open(os.path.join(RAIZ, "coleta", "golden_path_pdf.py"),
                   encoding="utf-8").read()
codigo_gp = "\n".join(l for l in fonte_gp.splitlines()
                      if not l.lstrip().startswith("#"))
import re                                          # noqa: E402
ataque(19, "corte silencioso de texto antes da porta",
       not re.search(r'item\s*\[\s*["\']texto["\']\s*\]\s*=\s*texto\s*\[',
                     codigo_gp),
       "o caminho da porta voltou a fatiar o texto")

grande = "malattia " * 3000 + "trappole e infestazione"
dg = adm.decidir({"id": "g", "texto": grande, "source_id": "S",
                  "artifact_type": "DERIVED", "parent_sha256": "a" * 64}, "T3")
ataque(20, "documento longo sendo julgado so pelo principio",
       dg.resultado == adm.SIM,
       "documento de %d caracteres saiu %s" % (len(grande), dg.resultado))

# ═══════════════════════════════════════════════════════════════════════
# A SALA
# ═══════════════════════════════════════════════════════════════════════
ataque(21, "READY sendo tratado como Sala",
       espera.PRONTO != espera.A_ESPERA and espera.A_ESPERA == "WAITING",
       "o estado do contrato e o da fila tem o mesmo nome")

try:
    espera._conferir_unidades([{"ESTADO": espera.PRONTO, "ITEM_ID": "x"}])
    recusou = False
except ValueError:
    recusou = True
ataque(22, "ficheiro na Sala sem chave nem linhagem",
       recusou, "a sala aceitou uma unidade fora do contrato READY")

try:
    espera._conferir_unidades([{c: "x" for c in espera.CAMPOS_READY}])
    recusou_estado = False
except ValueError:
    recusou_estado = True
ataque(23, "item REJEITADO tentando entrar na Sala como PRONTO",
       recusou_estado, "a sala aceitou uma unidade cujo ESTADO nao e PRONTO")

# ⚠️ UM CAMPO A MAIS E CONTRABANDO, E NAO GENEROSIDADE. A Sala guarda DOZE
# campos (COL-LAW-043). Aceitar um decimo terceiro poria no banco um dado que
# nenhum leitor sabe ler e que nenhum contrato governa.
_extra = {c: "x" for c in espera.CAMPOS_READY}
_extra["ESTADO"] = espera.PRONTO
_extra["CONTRABANDO"] = "um campo que o contrato nao tem"
try:
    espera._conferir_unidades([_extra])
    _recusou_extra = False
except ValueError:
    _recusou_extra = True
ataque(24, "unidade com campo a mais entrando na Sala",
       _recusou_extra, "a sala aceitou um campo fora do contrato READY")

# ═══════════════════════════════════════════════════════════════════════
# O BANCO — so quando ha banco
# ═══════════════════════════════════════════════════════════════════════
if url:
    cod, _o, err = _psql(url, "insert into public.sala_de_espera "
                              "(run_id, ordem, item_id, universo, texto, "
                              "source_id, source_location, fact_location, "
                              "fact_time, captured_at, admitido_por, "
                              "corrida_sha256) values "
                              "('NAO-EXISTE', 0, 'x', 'T3', 't', 'S', 'a', "
                              "'b', 'c', 'd', 'e', "
                              "'%s')" % ("0" * 64))
    ataque(25, "pousar na Sala uma corrida que nao existe",
           cod != 0 and "foreign key" in err.lower(),
           "o banco aceitou uma corrida inexistente")

    cod, _o, err = _psql(url, "update public.sala_de_espera set "
                              "estado_da_fila = 'CONSUMED' where true")
    ataque(26, "retirar da Sala sem dizer quem nem quando",
           cod != 0 and "consumo_diz_quem_e_quando" in err,
           "a fila deixou consumir sem autor nem hora")

    cod, _o, err = _psql(url, "insert into public.raw_asset "
                              "(run_id, storage_path, media_type, bytes, "
                              "sha256, captured_at) values "
                              "('NAO-EXISTE','p','application/pdf',1,"
                              "'%s', now())" % ("c" * 64))
    ataque(27, "RAW apontando para uma corrida que nao existe",
           cod != 0, "o banco aceitou RAW sem corrida")

    linhas = _psql(url, "select count(*) from public.sala_de_espera s "
                        "left join public.raw_asset a "
                        "on a.id = s.raw_observation_id "
                        "where s.raw_observation_id is not null "
                        "and a.id is null")[1].strip()
    ataque(28, "item na Sala apontando para observacao inexistente",
           linhas in ("0", ""), "ha %s item(ns) orfao(s) na Sala" % linhas)
else:
    print("  (25-28 precisam de BANCO_DESCARTAVEL_URL — NAO MEDIDOS)")

estado = {
    "O_QUE_ISTO_E": "Ataques a estrada que leva material real a Sala de Espera.",
    "COMO_REFAZER": ("BANCO_DESCARTAVEL_URL=... python3 "
                     "provas/red_team_collection_ate_a_sala.py"),
    "ATAQUES": len(MORTOS) + len(SOBREVIVENTES),
    "MORTOS": len(MORTOS),
    "RED_TEAM_SURVIVORS": len(SOBREVIVENTES),
    "SOBREVIVENTES": SOBREVIVENTES,
    "BANCO_MEDIDO": bool(url),
}
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with io.open(SAIDA, "w", encoding="utf-8") as f:
    json.dump(estado, f, ensure_ascii=False, indent=1)
    f.write("\n")

print()
print("  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
print()
print("ATAQUES = %d · MORTOS = %d · RED_TEAM_SURVIVORS = %d"
      % (len(MORTOS) + len(SOBREVIVENTES), len(MORTOS), len(SOBREVIVENTES)))
raise SystemExit(1 if SOBREVIVENTES else 0)
