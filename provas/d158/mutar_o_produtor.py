#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS MUTANTES DO PRODUTOR DE AFIRMACOES (D158) — cada garantia, atacada uma vez.

    py provas/d158/mutar_o_produtor.py [--saida MUTACAO-PRODUTOR-V1.json]

COMO SE MEDE
------------
A arvore commitada sai por `git archive` para uma copia descartavel. Em cada rodada UMA
troca de texto entra na copia — e so uma —, e a bateria do produtor corre LA DENTRO. O
mutante MORRE se a bateria reprovar. Um mutante que SOBREVIVE nao e um erro do mutante: e
uma garantia que ninguem esta a guardar, e sai na entrega com o nome.

O que se ataca (uma linha por garantia):
    1  o trecho deixa de ser texto[inicio:fim]        — a prova deixa de ser prova
    2  o ASSERTION_ID deixa de olhar o offset          — dois trechos, um nome so
    3  o ASSERTION_ID deixa de olhar o byte do RAW     — outro documento, mesmo nome
    4  a conferencia deixa de comparar o trecho        — o portao abre-se
    5  a conferencia deixa de olhar o RAW_SHA256       — documento alterado passa
    6  a conferencia deixa de olhar o BASIS do tempo   — data sem prova passa
    7  qualquer PAPEL vira tempo do facto              — validade/previsao viram facto
    8  o PERIODO_DA_EDICAO vira ACONTECIMENTO          — a edicao vira o facto
    9  o periodo futuro vira ACONTECIMENTO             — previsao vira observacao
   10  a D147 deixa de exigir «sem concorrente»        — compoe na duvida
   11  a D147 deixa de exigir o papel do cabecalho     — herda de qualquer cabecalho
   12  a D147 deixa de recusar conselho e futuro       — recomendacao herda a data
   13  a D149 deixa de comparar impresso x conta       — duas datas, escolhe uma
   14  `desdobrar` aceita qualquer linha               — cabecalho inventado
   15  a virgula que emenda deixa de cortar            — duas afirmacoes num trecho so
   16  a memoria de leitura passa a responder a todos  — um documento responde por outro
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BATERIA = "tests/test_o_produtor_de_afirmacoes.py"

#: (nome, ficheiro, o que estava la, o que passa a estar)
MUTANTES = [
    ("TRECHO_DEIXA_DE_SER_O_TEXTO", "leis/afirmacao_do_documento.py",
     '                "TRECHO_LITERAL": span,', '                "TRECHO_LITERAL": span[1:],'),
    ("ID_NAO_OLHA_O_OFFSET", "leis/afirmacao_do_documento.py",
     'str(int(inicio)), str(int(fim)), str(trecho)])',
     'str(trecho)])'),
    ("ID_NAO_OLHA_O_BYTE_DO_RAW", "leis/afirmacao_do_documento.py",
     'str(raw_sha256 or NAO_SEI),', ''),
    ("CONFERENCIA_NAO_COMPARA_O_TRECHO", "leis/afirmacao_do_documento.py",
     '    if trecho != t[a:b]:', '    if False:'),
    ("CONFERENCIA_NAO_OLHA_O_RAW_SHA256", "leis/afirmacao_do_documento.py",
     '    if raw_sha256 is not None and prov.get("RAW_SHA256") not in (NAO_SEI, raw_sha256):',
     '    if False:'),
    ("CONFERENCIA_NAO_OLHA_O_BASIS", "leis/afirmacao_do_documento.py",
     '        elif basis.get("TRECHO") != t[basis.get("INICIO", -1):basis.get("FIM", -1)]:',
     '        elif False:'),
    ("QUALQUER_PAPEL_E_FACTO", "leis/tempo_da_afirmacao.py",
     'PAPEL_QUE_E_FACTO = (ACONTECIMENTO,)', 'PAPEL_QUE_E_FACTO = PAPEIS'),
    ("EDICAO_VIRA_ACONTECIMENTO", "leis/tempo_da_afirmacao.py",
     '        return PERIODO_DA_EDICAO, "periodo no cabecalho do proprio boletim: diz de que dias a EDICAO fala"',
     '        return ACONTECIMENTO, "periodo no cabecalho do proprio boletim"'),
    ("FUTURO_VIRA_ACONTECIMENTO", "leis/tempo_da_afirmacao.py",
     '        return PREVISAO, "o periodo comeca depois da publicacao provada: ainda nao aconteceu"',
     '        return ACONTECIMENTO, "o periodo comeca depois da publicacao provada"'),
    ("D147_SEM_A_CONDICAO_DO_CONCORRENTE", "leis/tempo_da_afirmacao.py",
     '    if len(periodos) != 1:', '    if not periodos:'),
    ("D147_SEM_O_PAPEL_DO_CABECALHO", "leis/tempo_da_afirmacao.py",
     '    if papel != ACONTECIMENTO:', '    if False:'),
    ("D147_SEM_A_RECUSA_DO_CONSELHO", "leis/tempo_da_afirmacao.py",
     '    conselho = fala_de_acontecimento(span)', '    conselho = None'),
    ("D149_NAO_COMPARA_IMPRESSO_COM_A_CONTA", "leis/tempo_da_afirmacao.py",
     '            if p["VALOR"] == c["fact_time"]:', '            if True:'),
    ("DESDOBRAR_ACEITA_TUDO", "leis/tempo_da_afirmacao.py",
     '        if any(p[i] != p[i + 1] for i in range(0, len(p), 2)):\n            return None',
     '        if False:\n            return None'),
    ("A_VIRGULA_QUE_EMENDA_DEIXA_DE_CORTAR", "leis/afirmacao_do_documento.py",
     '                     | {m.start() + 1 for m in _RE_VIRGULA_QUE_EMENDA.finditer(t, ini, fim)}',
     '                     | set()'),
    # ── os mutantes que o CONTRATO DE CONSUMO da Intelligence exige (§4) ─────
    ("FACT_TIME_VIRA_A_PUBLICACAO", "leis/afirmacao_do_documento.py",
     '            fact_time = (tempo["VALOR"] if e_facto',
     '            fact_time = (prov.get("PUBLISHED_AT") if e_facto'),
    ("FACT_LOCATION_VIRA_O_LUGAR_DA_FONTE", "leis/afirmacao_do_documento.py",
     '    return {"VALOR": NAO_SEI if valor == UNRESOLVED else valor,',
     '    return {"VALOR": "SOURCE_LOCATION" if valor == UNRESOLVED else valor,'),
    ("SPAN_SEM_O_NOME_NO_TRECHO", "leis/afirmacao_do_documento.py",
     '        ok, porque = AF.procedencia_da_entidade(e["ENTITY_SOURCE"], nome_no_trecho=no_trecho)',
     '        ok, porque = AF.procedencia_da_entidade(e["ENTITY_SOURCE"], nome_no_trecho=True)'),
    ("O_PRODUTOR_ESCREVE_LIBERADO", "leis/afirmacao_do_documento.py",
     '                "CONTRATO": CONTRATO,\n                # ── identidade e lineage',
     '                "CONTRATO": CONTRATO,\n                "LIBERACAO": "LIBERADO_PARA_CLIENTE",\n                # ── identidade e lineage'),
    ("CLAIM_ID_DEIXA_DE_SER_O_ASSERTION_ID", "leis/afirmacao_do_documento.py",
     '                "CLAIM_ID": oid,', '                "CLAIM_ID": oid + "-x",'),
    ("EVIDENCE_SPAN_NAO_BATE_COM_O_TEXTO", "leis/afirmacao_do_documento.py",
     '"EVIDENCE_SPAN": {"INICIO": a, "FIM": b, "TRECHO": span, "SHA256": sha_do_trecho(span)},',
     '"EVIDENCE_SPAN": {"INICIO": a, "FIM": b, "TRECHO": span[1:], "SHA256": sha_do_trecho(span)},'),
    ("A_CLASSE_SAI_DO_VOCABULARIO_FECHADO", "leis/afirmacao_do_documento.py",
     '        return {"VALOR": marcas[0], "MARCAS": marcas,',
     '        return {"VALOR": "CLASSE_" + marcas[0], "MARCAS": marcas,'),
    ("A_CLASSE_ESCOLHE_UMA_DE_DUAS", "leis/afirmacao_do_documento.py",
     '    if len(marcas) > 1:', '    if False:'),
    # ── as tres condicoes do Intelligence owner (§5-B: C1, C2, C3) ─────────
    ("A_D149_CHAMA_SE_LITERAL", "leis/tempo_da_afirmacao.py",
     'ORIGEM=RELATIVA_ANCORADA_D149,', 'ORIGEM=LITERAL,'),
    ("O_CABECALHO_CHAMA_SE_LITERAL", "leis/tempo_da_afirmacao.py",
     'ORIGEM=CABECALHO_D147, BASIS=p["BASIS"],', 'ORIGEM=LITERAL, BASIS=p["BASIS"],'),
    ("A_CONFERENCIA_ACEITA_LITERAL_COM_BASIS_DE_FORA", "leis/afirmacao_do_documento.py",
     '        elif origem == TA.LITERAL and not (a <= basis["INICIO"] and basis["FIM"] <= b):',
     '        elif False:'),
    ("O_LUGAR_VIAJA_SEM_PRECISAO", "leis/afirmacao_do_documento.py",
     '            "PRECISAO": l_.get("PRECISAO") or "NOT_KNOWN",', '            "PRECISAO": None,'),
    ("O_LUGAR_VIAJA_SEM_A_COBERTURA", "leis/afirmacao_do_documento.py",
     '            "COBERTURA_DO_GAZETTEER": cobertura_do_gazetteer()}',
     '            "COBERTURA_DO_GAZETTEER": None}'),
    ("O_PRODUTOR_ESCREVE_ESPECIE", "leis/afirmacao_do_documento.py",
     '                "CONTRATO": CONTRATO,
                # ── identidade e lineage',
     '                "CONTRATO": CONTRATO,
                "ESPECIE": "SINAL",
                # ── identidade e lineage'),
    ("MEMORIA_RESPONDE_A_TODOS", "leis/boletim_do_campo.py",
     '        def _envolta(*args):\n            if args in guardadas:',
     '        def _envolta(*args):\n            if guardadas:\n                return next(iter(guardadas.values()))\n            if args in guardadas:'),
]


def copia_da_arvore(destino: Path) -> None:
    """A arvore COMMITADA, por `git archive` — nunca a pasta de trabalho."""
    tar = destino.parent / "arvore.tar"
    with open(tar, "wb") as f:
        subprocess.run(["git", "archive", "HEAD"], cwd=str(RAIZ), stdout=f, check=True)
    destino.mkdir(parents=True, exist_ok=True)
    subprocess.run(["tar", "-xf", str(tar), "-C", str(destino)], check=True)
    tar.unlink()


def correr_a_bateria(raiz: Path):
    r = subprocess.run([sys.executable, BATERIA], cwd=str(raiz), capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
                                PYTHONPATH=os.environ.get("PYTHONPATH", "")))
    return r.returncode, ((r.stderr or "") + (r.stdout or ""))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=str(Path(__file__).resolve().parent / "MUTACAO-PRODUTOR-V1.json"))
    a = ap.parse_args(argv)

    base = Path(tempfile.mkdtemp(prefix="d158-mut-"))
    limpo = base / "limpo"
    copia_da_arvore(limpo)
    codigo, saida = correr_a_bateria(limpo)
    r = {"ARVORE": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(RAIZ), capture_output=True,
                                  text=True).stdout.strip(),
         "BATERIA": BATERIA,
         "SEM_MUTACAO": {"CODIGO": codigo, "VERDE": codigo == 0, "CAUDA": saida.strip()[-400:]},
         "MUTANTES": []}
    if codigo != 0:
        r["AVISO"] = ("a bateria ja reprova na copia LIMPA: nenhum mutante prova nada enquanto isto "
                      "for verdade")
        Path(a.saida).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(r["SEM_MUTACAO"], ensure_ascii=False))
        return 1

    mortos = 0
    for nome, rel, de, para in MUTANTES:
        alvo = base / nome
        if alvo.exists():
            shutil.rmtree(alvo)
        shutil.copytree(limpo, alvo)
        p = alvo / Path(rel)
        fonte = p.read_text(encoding="utf-8")
        if fonte.count(de) != 1:
            r["MUTANTES"].append({"NOME": nome, "FICHEIRO": rel, "ESTADO": "NAO_APLICADO",
                                  "PORQUE": "o texto a trocar aparece %d vezes (tem de aparecer 1)"
                                            % fonte.count(de)})
            continue
        p.write_text(fonte.replace(de, para), encoding="utf-8", newline="\n")
        c, s = correr_a_bateria(alvo)
        morto = c != 0
        mortos += morto
        r["MUTANTES"].append({"NOME": nome, "FICHEIRO": rel, "ESTADO": "MORTO" if morto else "SOBREVIVEU",
                              "CODIGO": c,
                              "QUEM_O_MATOU": [l.strip() for l in s.splitlines()
                                               if l.startswith(("FAIL:", "ERROR:"))][:6]})
        shutil.rmtree(alvo, ignore_errors=True)
    r["TOTAL"] = len(MUTANTES)
    r["MORTOS"] = mortos
    r["SOBREVIVENTES"] = [m["NOME"] for m in r["MUTANTES"] if m["ESTADO"] != "MORTO"]
    Path(a.saida).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.rmtree(base, ignore_errors=True)
    print("MORTOS %d/%d · SOBREVIVENTES: %s" % (mortos, len(MUTANTES), r["SOBREVIVENTES"] or "nenhum"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
