#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTACAO DO MOTOR DAS CAPACIDADES (INT-R7-CAPS) — planta UM defeito de cada vez
em `motor/motor_das_capacidades.py` (e nos dois ganchos de triagem das
capacidades), corre `tests.test_motor_das_capacidades`, e exige que ele
REPROVE. Restaura os bytes originais sempre (sem `git checkout`) e confere no
fim que cada ficheiro voltou igual (SHA-256).

    python3 provas/int_r7/mutantes.py          # grava provas/int_r7/MUTANTES.json

Um mutante que sobrevive e um teste que falta, nao um mutante mau.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MOTOR = "motor/motor_das_capacidades.py"
WIN = "motor/cap_win.py"
SCI = "motor/capacidade_cientifica.py"
SAIDA = Path(__file__).resolve().parent / "MUTANTES.json"
TESTE = "tests.test_motor_das_capacidades"

#: (id, ficheiro, o que o defeito finge, texto original, texto mutante)
MUTANTES = [
 ("M1", MOTOR, "D112a: lugar DA_FONTE passa a sustentar o fato",
  "ok, porque = LUGAR.sustenta_fato(origem, LUGAR.FACT)",
  "ok, porque = LUGAR.sustenta_fato('ESCRITO', LUGAR.FACT)"),
 ("M2", MOTOR, "D112a: lugar sem base passa",
  "    if CI.base_ignorante(base):\n        return {\"SUSTENTADO\": False",
  "    if False:\n        return {\"SUSTENTADO\": False"),
 ("M3", MOTOR, "D112a: a regiao recusada continua a chegar a CAP-WIN",
  "            jd[campo] = dict(bloco, VALOR=NAO_SEI, D112=r[\"PORQUE\"])", "            pass"),
 ("M4", MOTOR, "D112a: o local recusado continua a chegar a CAP-SCI",
  "        ready[\"FACT_LOCATION_BASIS\"] = NAO_SEI + \" — \" + rel[\"FACT_LOCATION\"][\"PORQUE\"]",
  "        pass"),
 ("M5", MOTOR, "triagem: estudo vai tambem a CAP-WIN (estudo vira observacao de janela)",
  # ajuste declarado (PORTA-UNICA-REFERENCIA): a linha ganhou `referencia=ref`; o defeito e o mesmo
  "    win = WIN.julgar(livro, itens_win, hoje, fora=para_win, referencia=ref)",
  "    win = WIN.julgar(livro, itens_win, hoje, fora={}, referencia=ref)"),
 ("M6", MOTOR, "triagem: a classe declarada pela fonte passa a decidir o estudo",
  "    if achado:\n        return True",
  "    if achado or ready.get(\"SOURCE_DECLARED_EVIDENCE_CLASS\") == \"SCIENTIFIC_RESULT\":\n        return True"),
 ("M7", MOTOR, "D112e: mesma redacao em N territorios conta N instituicoes",
  "                \"INSTITUICOES\": 1,", "                \"INSTITUICOES\": len(i[\"TERRITORIOS\"]),"),
 ("M8", MOTOR, "D112e: territorio nao sustentado conta como aplicacao",
  "\"APLICACOES\": (len(i[\"TERRITORIOS\"]) if not i[\"SEM_TERRITORIO\"] else NAO_SEI),",
  "\"APLICACOES\": len(i[\"TERRITORIOS\"]),"),
 ("M9", MOTOR, "D112f: limites diferentes deixam de ser DIVERGENT",
  "    if len(por_limite) > 1:", "    if len(por_limite) > 99:"),
 ("M10", MOTOR, "D112f: a divergencia sai RESOLVIDA (o sistema escolhe)",
  "\"TIPO\": DIVERGENT, \"PAR\": par, \"CONTRADICAO\": UNRESOLVED,",
  "\"TIPO\": DIVERGENT, \"PAR\": par, \"CONTRADICAO\": \"RESOLVED_BY_MAJORITY\","),
 ("M11", MOTOR, "D112f: DIVERGENT deixa agir agora",
  "    if divergentes and resultado == WIN.ACT_NOW:", "    if False:"),
 ("M12", MOTOR, "D112g: tempos que se tocam viram «antes e depois»",
  "            if a[\"TIME_WINDOW\"][\"FIM\"] >= b[\"TIME_WINDOW\"][\"INICIO\"]:\n                continue",
  "            if False:\n                continue"),
 ("M13", MOTOR, "D112g: TEMPORAL_CHANGE passa a provar mudanca no campo",
  "\"NAO_PROVA\": \"MUDANCA_NO_CAMPO — a recomendacao", "\"PROVA\": \"MUDANCA_NO_CAMPO — a recomendacao"),
 ("M14", MOTOR, "D112g: territorios diferentes viram mudanca no tempo",
  "        grupos.setdefault((i[\"INSTITUICAO\"], i[\"TERRITORIOS\"]), []).append(i)",
  "        grupos.setdefault((i[\"INSTITUICAO\"], ()), []).append(i)"),
 ("M15", MOTOR, "D112b: entidade com valor sai sem procedencia",
  "    return dict({\"VALOR\": valor, \"ENTITY_SOURCE\": fonte, \"POR_ITEM\": por_item}, **(extra or {}))",
  "    return dict({\"VALOR\": valor, \"ENTITY_SOURCE\": NAO_SEI, \"POR_ITEM\": por_item}, **(extra or {}))"),
 ("M16", MOTOR, "D112d: o juizo entra no bloco da fonte",
  "        \"A_FONTE_MANDA_NAO_TRATAR\": j[\"SOURCE_SAYS_DO_NOT_TREAT\"],",
  "        \"A_FONTE_MANDA_NAO_TRATAR\": j[\"SOURCE_SAYS_DO_NOT_TREAT\"], \"RESULT\": j[\"RESULT\"],"),
 ("M17", MOTOR, "prova: a publicacao vira tempo do facto",
  "        \"FACT_TIME\": _v(linha.get(\"FACT_TIME\")),\n    }",
  "        \"FACT_TIME\": pub,\n    }"),
 ("M18", MOTOR, "prova: URL deixa de vir do RAW",
  "        \"URL\": _v(r.get(\"URL\")),", "        \"URL\": NAO_SEI,"),
 ("M19", MOTOR, "prova: DOCUMENT_ID cunhado quando o RAW nao o tem",
  "        \"DOCUMENT_ID\": _v(r.get(\"DOCUMENT_ID\")),",
  "        \"DOCUMENT_ID\": (\"DOC-\" + str(ready[\"ITEM_ID\"])) if _ign(r.get(\"DOCUMENT_ID\")) "
  "else r[\"DOCUMENT_ID\"],"),
 ("M20", MOTOR, "prova: item bloqueado em G0 entra na prova da janela",
  "        if _admite(linha, SINAL):\n            provas.append",
  "        if True:\n            provas.append"),
 ("M21", MOTOR, "INTELLIGENCE_RUN_ID sai do topo",
  "        \"INTELLIGENCE_RUN_ID\": run_id,\n        \"SCHEMA\": CONTRATO,",
  "        \"SCHEMA\": CONTRATO,\n        \"INTELLIGENCE_RUN_ID\": run_id,"),
 ("M22", MOTOR, "portao: estudo numa janela passa",
  "                if comp == \"windows\" and str(p.get(\"ITEM_ID\")) in estudos:",
  "                if False:"),
 ("M23", MOTOR, "portao: PUBLISHED_AT divergente passa",
  "                if p.get(\"PUBLISHED_AT\") != p.get(\"PUBLICADO_EM\"):", "                if False:"),
 ("M24", MOTOR, "portao: especie OPORTUNIDADE passa",
  "            if o.get(\"ESPECIE\") not in ESPECIES_EMITIDAS:", "            if False:"),
 ("M25", MOTOR, "portao: prova fora da LINEAGE passa",
  "                if l is None:\n                    v.append", "                if False:\n                    v.append"),
 ("M26", MOTOR, "portao: leitura proibida passa",
  "        if p in texto:\n            v.append(\"leitura proibida", "        if False:\n            v.append(\"leitura proibida"),
 ("M27", MOTOR, "entrada: campo de fora do READY passa",
  "        sobra = sorted(set(r) - {\"READY\"})",
  "        sobra = []"),
 ("M28", MOTOR, "duas corridas: a CAP-SCI corre num livro proprio (contador duplicado)",
  # ajuste declarado (PORTA-UNICA-REFERENCIA): a SCI recebe `ref` (a da porta); o defeito e o mesmo
  "    sci = SCI.julgar(livro, ready_cap, ref, triados_fora=para_sci)",
  "    sci = SCI.julgar(CI.correr(PERGUNTA + ' (SCI)', ready_cap), ready_cap, ref, triados_fora=para_sci)"),
 ("M29", MOTOR, "rendimento: prova sem DOCUMENT_ID entra (o pote recusa a fonte inteira)",
  "        com_doc = [l for l in passaram if not _ign(", "        com_doc = [l for l in passaram if True or not _ign("),
 ("M30", MOTOR, "futuro: item bloqueado por mais do que o futuro prova o futuro",
  "        return linha.get(\"G0\") == \"BLOQUEADO_EM_G0\" and linha.get(\"G0_FALTA\") == [G0_FUTURO_POR_DESENHO]",
  "        return linha.get(\"G0\") == \"BLOQUEADO_EM_G0\""),
 ("M31", WIN, "CAP-WIN ignora a triagem do motor",
  "        if linha.get(\"ITEM_ID\") in fora:", "        if False:"),
 ("M32", SCI, "CAP-SCI ignora a triagem do motor (boletim julgado como estudo)",
  "        if it[\"ITEM_ID\"] in (triados_fora or {}):", "        if False:"),
]


def main() -> int:
    originais = {f: (RAIZ / f).read_bytes() for f in {m[1] for m in MUTANTES}}
    shas = {f: hashlib.sha256(b).hexdigest() for f, b in originais.items()}
    fora = []
    try:
        for mid, alvo, finge, velho, novo in MUTANTES:
            texto = originais[alvo].decode("utf-8")
            n = texto.count(velho)
            if n != 1:
                fora.append({"ID": mid, "ALVO": alvo, "FINGE": finge,
                             "ESTADO": f"NAO_PLANTADO (casou {n}x)"})
                continue
            (RAIZ / alvo).write_text(texto.replace(velho, novo), encoding="utf-8")
            p = subprocess.run([sys.executable, "-m", "unittest", TESTE],
                               cwd=RAIZ, capture_output=True, text=True, timeout=600)
            morto = p.returncode != 0
            quem = sorted({l.split()[1] for l in p.stderr.splitlines()
                           if l.startswith(("FAIL:", "ERROR:"))})
            fora.append({"ID": mid, "ALVO": alvo, "FINGE": finge,
                         "ESTADO": "MORTO" if morto else "SOBREVIVEU", "APANHADO_POR": quem[:6]})
            (RAIZ / alvo).write_bytes(originais[alvo])
    finally:
        for f, b in originais.items():
            (RAIZ / f).write_bytes(b)
    for f, s in shas.items():
        assert hashlib.sha256((RAIZ / f).read_bytes()).hexdigest() == s, f + " nao voltou igual"
    mortos = sum(1 for m in fora if m["ESTADO"] == "MORTO")
    res = {"ALVOS_SHA256": shas, "TESTE": TESTE, "PLANTADOS": len(fora), "MORTOS": mortos,
           "MUTANTES": fora}
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for m in fora:
        print(f'{m["ID"]:4} {m["ESTADO"]:12} {m["FINGE"]}')
    print(f"\n{mortos}/{len(fora)} mortos")
    return 0 if mortos == len(fora) else 1


if __name__ == "__main__":
    sys.exit(main())
