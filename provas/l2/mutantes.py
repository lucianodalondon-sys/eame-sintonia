#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTACAO DO L2-DISPARADOR — planta UM defeito de cada vez no gatilho, no vigia e na retencao, corre
`tests.test_disparador_intelligence`, e exige que ele REPROVE. Restaura os bytes originais sempre (sem
`git checkout`) e confere no fim que cada ficheiro voltou igual (SHA-256).

    py provas/l2/mutantes.py        # grava provas/l2/MUTANTES.json

Herdado do harness da ESTEIRA-SOZINHA (provas/esteira_sozinha/mutantes.py em f85b4138a): o mesmo
`aplicar()` que aguenta CRLF, e os mutantes do gatilho, do vigia e da retencao que continuam a valer
aqui. Novos (D140): o disparador que ESCREVE na Sala, que MARCA consumido_em, sem trinco (da corrida e
da volta), o pote invalido ENTREGUE, o disparador que escreve sob italia-portale/ (a fronteira: a
Intelligence para na entrega), o ENTITY_SOURCE achatado/escolhido/fora da lei, o corte vigente torto, a
DSN que aparece no resultado. Um mutante que sobrevive e um teste que falta, nao um mutante mau.
Os testes correm com -B (sem .pyc): um mutante do mesmo tamanho nao engana o cache.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = Path(__file__).resolve().parent / "MUTANTES.json"
TESTE = "tests.test_disparador_intelligence"
GI = "admissao/gatilho_da_inteligencia.py"
VIG = "medidas/vigia_da_esteira.py"
PB = "scripts/micro_coleta/provar_backup_da_sala.py"
POTE = "pacote/pote_intelligence_casco.py"
MOT = "motor/motor_das_capacidades.py"
SQL = "motor/r7_export_da_copia.sql"
FIX = "tests/fixtures/pote/CORRIDA-SINTETICA-V2-UNICO.json"

#: (id, ficheiro, o defeito que finge, texto original, texto mutante)
MUTANTES = [
 # ── D140: o disparador so LE a Sala e nunca marca consumido_em ──
 ("L1", GI, "o disparador ESCREVE na Sala (chama um escritor do dono)",
  "    estado[\"INT_ULTIMA_TENTATIVA_EM\"] = agora.isoformat()\n",
  "    estado[\"INT_ULTIMA_TENTATIVA_EM\"] = agora.isoformat()\n    espera.pousar(\"L2-MUTANTE\", [])\n"),
 ("L2", GI, "o disparador MARCA consumido_em (retira da fila)",
  "    estado[\"INT_ULTIMA_TENTATIVA_EM\"] = agora.isoformat()\n",
  "    estado[\"INT_ULTIMA_TENTATIVA_EM\"] = agora.isoformat()\n    espera.retirar(\"R\", \"I\", \"disparador\")\n"),
 ("L3", GI, "o delta vira UPDATE ... consumido_em (escreve na Sala pela consulta)",
  "    linhas = consulta(\"select count(*), min(pousado_em), max(pousado_em) from sala_de_espera\" + onde)",
  "    linhas = consulta(\"update sala_de_espera set consumido_em = now() returning 1, pousado_em, pousado_em\" + onde)"),
 ("L4", GI, "o export da copia sem a trava do banco (PGOPTIONS sem read only)",
  "PGOPTIONS_SO_LEITURA = \"-c default_transaction_read_only=on -c standard_conforming_strings=on\"",
  "PGOPTIONS_SO_LEITURA = \"-c standard_conforming_strings=on\""),
 ("L5", GI, "export sem a transacao so-leitura no comando",
  "\"-c\", \"begin transaction read only\", ", ""),
 ("L6", GI, "export sem READ_ONLY=on serve", "    if exp.get(\"READ_ONLY\") != \"on\":", "    if False:"),
 # ── o trinco: nunca duas corridas / duas voltas ──
 ("L7", GI, "Intelligence sem trinco: duas corridas ao mesmo tempo",
  "        with espera._Trava(str(trinco)):\n            pasta_corrida = ",
  "        with open(os.devnull):\n            pasta_corrida = "),
 ("L8", GI, "volta agendada sem trinco: duas voltas gravam o estado por cima uma da outra",
  "        with espera._Trava(str(trinco_da_volta)):\n            estado = ler_estado(estado_em)",
  "        with open(os.devnull):\n            estado = ler_estado(estado_em)"),
 ("L9", GI, "a volta OCUPADA grava o estado (apaga a marca da outra)",
  "        return {\"ACCAO\": \"OCUPADO\", \"PORQUE\": \"outra volta do disparador esta a decorrer\"}",
  "        gravar_estado({}, estado_em)\n"
  "        return {\"ACCAO\": \"OCUPADO\", \"PORQUE\": \"outra volta do disparador esta a decorrer\"}"),
 # ── o pote invalido entregue, e a fronteira (a Intelligence para na entrega) ──
 ("L10", GI, "pote reprovado vai para a entrega (o fiscal e ignorado)", "    if violacoes:\n        guardado = ",
  "    if False:\n        guardado = "),
 ("L11", GI, "pote reprovado vai para a entrega (antes do fiscal)",
  "    candidato.write_text(json.dumps(pote, ensure_ascii=False, indent=1) + \"\\n\", encoding=\"utf-8\", newline=\"\\n\")\n",
  "    candidato.write_text(json.dumps(pote, ensure_ascii=False, indent=1) + \"\\n\", encoding=\"utf-8\", newline=\"\\n\")\n"
  "    entregar(candidato, pote, entrega, corte)\n"),
 ("L12", GI, "SHA256SUMS com o sha errado", "    (nova / \"SHA256SUMS.txt\").write_text(\"\".join(\"%s *%s\\n\" % (_sha256(nova / n), n)",
  "    (nova / \"SHA256SUMS.txt\").write_text(\"\".join(\"%s *%s\\n\" % (_sha256(nova / \"POTE.json\"), n)"),
 ("L13", GI, "a entrega nao se troca inteira (sobra de outra entrega fica)",
  "    if entrega.exists():\n        os.replace(entrega, velha)\n    os.replace(nova, entrega)",
  "    entrega.mkdir(parents=True, exist_ok=True)\n    for f in nova.iterdir():\n        os.replace(f, entrega / f.name)"),
 ("L42", GI, "o disparador escreve sob italia-portale/ (publica ele mesmo no casco)",
  "    os.replace(nova, entrega)\n",
  "    os.replace(nova, entrega)\n"
  "    shutil.copyfile(entrega / \"POTE.json\", RAIZ / \"italia-portale\" / \"client\" / \".l2-mutante-pote.json\")\n"),
 # ── ENTITY_SOURCE no ponto de montagem (decisao do Intelligence owner) ──
 ("L43", GI, "o mapa do motor e achatado em texto",
  "    return v if isinstance(v, str) and v in LEI_221 else \"UNKNOWN\"",
  "    return json.dumps(v, sort_keys=True) if isinstance(v, dict) else (v if isinstance(v, str) and v in LEI_221 else \"UNKNOWN\")"),
 ("L44", GI, "escolhe-se uma entrada do mapa",
  "    return v if isinstance(v, str) and v in LEI_221 else \"UNKNOWN\"",
  "    return next(iter(v.values())).get(\"ENTITY_SOURCE\", \"UNKNOWN\") if isinstance(v, dict) and v else (v if isinstance(v, str) and v in LEI_221 else \"UNKNOWN\")"),
 ("L45", GI, "texto fora do vocabulario da lei passa",
  "    return v if isinstance(v, str) and v in LEI_221 else \"UNKNOWN\"",
  "    return v if isinstance(v, str) else \"UNKNOWN\""),
 ("L46", GI, "o mapa do motor chega ao pote (montado sem a conversao)",
  "                    dono[\"ENTITY_SOURCE\"] = novo\n", "                    pass\n"),
 ("L47", GI, "a conversao estraga a saida do motor (sem copia)",
  "    entrada = json.loads(json.dumps(saida_motor, ensure_ascii=False, default=list))",
  "    entrada = saida_motor"),
 ("L60", GI, "a entrega volta a sair com o fim de linha do sistema (CRLF no Windows quebra o sha256sum -c)",
  "                                                 for n in (\"POTE.json\", \"MANIFESTO.json\")), encoding=\"utf-8\",\n"
  "                                         newline=\"\\n\")",
  "                                                 for n in (\"POTE.json\", \"MANIFESTO.json\")), encoding=\"utf-8\",\n"
  "                                         newline=\"\\r\\n\")"),
 # ── D-GER-1 · o fiscal do pote: ENTITY_SOURCE so com o vocabulario da COL-LAW-221 ──
 ("L48", POTE, "o fiscal aceita qualquer texto em ENTITY_SOURCE",
  "                if not (isinstance(es, str) and es in ENTITY_SOURCES):",
  "                if not isinstance(es, str):"),
 ("L49", POTE, "o fiscal aceita o mapa do motor",
  "                if not (isinstance(es, str) and es in ENTITY_SOURCES):",
  "                if not (isinstance(es, dict) or (isinstance(es, str) and es in ENTITY_SOURCES)):"),
 ("L50", POTE, "o fiscal aceita «NAO SEI» em ENTITY_SOURCE",
  "                if not (isinstance(es, str) and es in ENTITY_SOURCES):",
  "                if not (isinstance(es, str) and es in ENTITY_SOURCES + (NAO_SEI,)):"),
 ("L51", POTE, "o fiscal aceita o valor da R9 manual (fora da lei)",
  "                if not (isinstance(es, str) and es in ENTITY_SOURCES):",
  "                if not (isinstance(es, str) and es in ENTITY_SOURCES + (\"TRECHO_DA_AFIRMACAO\",)):"),
 ("L52", POTE, "o fiscal aceita ENTITY_SOURCE vazio",
  "                if not (isinstance(es, str) and es in ENTITY_SOURCES):",
  "                if not (isinstance(es, str) and es in ENTITY_SOURCES + (\"\",)):"),
 ("L53", POTE, "o gerador traduz UNKNOWN para «NAO SEI» (segundo vocabulario)",
  "            out[c] = v if c == \"ENTITY_SOURCE\" else _valor(v)",
  "            out[c] = _valor(v)"),
 ("L54", POTE, "o fiscal deixa de conferir ENTITY_SOURCE",
  "            if \"ENTITY_SOURCE\" in o:\n                es = o[\"ENTITY_SOURCE\"]",
  "            if False:\n                es = o[\"ENTITY_SOURCE\"]"),
 ("L61", FIX, "D-GER-1-MIG: a fixture do dono volta a texto livre em ENTITY_SOURCE",
  "    \"ENTITY_SOURCE\": \"UNKNOWN\",", "    \"ENTITY_SOURCE\": \"SINT: registro nacional das culturas\","),
 # ── D-GER-2 · RAW_SHA256 / RAW_STORAGE_PATH: os do raw_asset, ou NAO SEI ──
 ("L55", SQL, "o export nao le o sha256 do raw_asset",
  "         r.sha256             as raw_sha256,\n", ""),
 ("L56", MOT, "a prova calcula o sha a partir do texto da Sala (nao veio do raw_asset)",
  "        \"RAW_SHA256\": _v(r.get(\"RAW_SHA256\")),",
  "        \"RAW_SHA256\": hashlib.sha256(str(ready.get(\"TEXTO\")).encode()).hexdigest(),"),
 ("L57", MOT, "o motor nao le a coluna raw_sha256 do export",
  "                  \"raw_sha256\": \"RAW_SHA256\", \"raw_storage_path\": \"RAW_STORAGE_PATH\"}",
  "                  \"raw_storage_path\": \"RAW_STORAGE_PATH\"}"),
 ("L58", POTE, "o gerador deixa cair o byte da prova (nao o le da prova do motor)",
  "                  \"RAW_SHA256\": (\"RAW_SHA256\",), \"RAW_STORAGE_PATH\": (\"RAW_STORAGE_PATH\",)}",
  "                  \"RAW_SHA256\": (), \"RAW_STORAGE_PATH\": ()}"),
 ("L59", POTE, "o fiscal aceita qualquer RAW_SHA256",
  "                        elif k == \"RAW_SHA256\" and not _SHA256_DO_BANCO.fullmatch(str(p[k])):",
  "                        elif False:"),
 # ── o corte vigente (defeito ITEM_ID repetido) ──
 ("L14", GI, "o corte nao se aplica: o motor recebe o ITEM_ID repetido",
  "        export, corte = cortar_vigente(export)\n", "        corte = cortar_vigente(export)[1]\n"),
 ("L15", GI, "fica a linha MAIS VELHA", "        vig = max(g, key=chave)", "        vig = min(g, key=chave)"),
 ("L16", GI, "hora ilegivel escolhe na mesma",
  "        if any(chave(l)[0] is None for l in g):", "        if False:"),
 ("L17", GI, "ITEM_ID sem identidade entra no corte",
  "        if iid in SEM_IDENTIDADE:\n            sem_id.append(", "        if False:\n            sem_id.append("),
 ("L18", GI, "o defeito da Sala fica calado no corte",
  "             \"DEFEITO_NA_SALA\": bool(repetidos or nao_sei or sem_id),", "             \"DEFEITO_NA_SALA\": False,"),
 ("L19", VIG, "o vigia cala o defeito da Sala", "    if corte.get(\"DEFEITO_NA_SALA\"):", "    if False:"),
 # ── a DSN nunca se imprime ──
 ("L20", GI, "a DSN aparece no resultado da volta",
  "            r = correr_se_devido(estado, **kw)\n",
  "            r = dict(correr_se_devido(estado, **kw), DSN=(ambiente or os.environ).get(\"SINTONIA_SALA_DSN\"))\n"),
 ("L21", GI, "sem DSN a volta corre na mesma", "    if falta:\n        return {\"ACCAO\": \"PRECONDICOES\"",
  "    if False:\n        return {\"ACCAO\": \"PRECONDICOES\""),
 # ── herdados da ESTEIRA-SOZINHA: a regra, o recuo, a copia, PARAR ──
 ("L22", GI, "gatilho corre sem delta",
  "    if n <= 0:\n        return {\"DECISAO\": ESPERAR, \"PORQUE\": \"SEM_DELTA\"}",
  "    if n < 0:\n        return {\"DECISAO\": ESPERAR, \"PORQUE\": \"SEM_DELTA\"}"),
 ("L23", GI, "limiar de 10 vira 1", "    if n >= LIMIAR_NOVOS:", "    if n >= 1:"),
 ("L24", GI, "4 h viram nada", "    if agora - velho >= ESPERA_MAXIMA:", "    if True:"),
 ("L25", GI, "delta nao medido vira zero (ESPERAR em vez de NAO SEI)",
  "        return {\"DECISAO\": NAO_SEI, \"PORQUE\": \"o delta da Sala nao foi medido\"}",
  "        return {\"DECISAO\": ESPERAR, \"PORQUE\": \"SEM_DELTA\"}"),
 ("L26", GI, "a marca nao anda: a mesma Sala corre para sempre",
  "    estado[\"INT_MARCA\"] = delta.get(\"MAIS_NOVO_EM\") or estado.get(\"INT_MARCA\")",
  "    estado[\"INT_MARCA\"] = estado.get(\"INT_MARCA\")"),
 ("L27", GI, "sem recuo depois de falha", "    if falhou and agora - falhou < RECUO:", "    if False:"),
 ("L28", GI, "copia sem PROVA_VALE corre o motor na mesma",
  "        if export is None:\n            estado[\"INT_ULTIMA_FALHA_EM\"]",
  "        if export is None and False:\n            estado[\"INT_ULTIMA_FALHA_EM\"]"),
 ("L29", GI, "gatilho ignora PARAR.flag",
  "    agora = agora or _agora()\n    if parar.exists():\n        return {\"ACCAO\": \"PARAR_FLAG\"}",
  "    agora = agora or _agora()\n    if False:\n        return {\"ACCAO\": \"PARAR_FLAG\"}"),
 ("L30", GI, "a Sala e perguntada a cada volta (sem intervalo)",
  "    if not forcar_medida and medido and agora - medido < INTERVALO_DE_MEDIDA:",
  "    if False:"),
 ("L31", GI, "a Intelligence nao poda",
  "                    estado[\"INT_ULTIMA_PODA\"] = (podar or podar_padrao)(pasta, pasta_corrida)",
  "                    estado[\"INT_ULTIMA_PODA\"] = {}"),
 ("L32", GI, "a poda corre ANTES da corrida (leva a em curso)",
  "            try:\n                return _correr(estado, agora, delta, d, copia, motor, subir, parar, pasta_corrida)",
  "            (podar or podar_padrao)(pasta, pasta_corrida)\n            try:\n"
  "                return _correr(estado, agora, delta, d, copia, motor, subir, parar, pasta_corrida)"),
 # ── herdados: o vigia calado e a retencao ──
 ("L33", VIG, "NAO SEI deixa de ser alerta", "        if linha[\"ESTADO\"] != ANDANDO:",
  "        if linha[\"ESTADO\"] == PARADA:"),
 ("L34", VIG, "o vigia nunca alerta", "\"ALERTA\": bool(alertas)", "\"ALERTA\": False"),
 ("L35", VIG, "marca que rebenta vira «andou agora»",
  "            quando, de_onde = None, \"erro a ler: %s\" % repr(e)[:200]",
  "            quando, de_onde = agora.isoformat(), \"x\""),
 ("L36", VIG, "o vigia nao escreve", "    escrever(r, saude, historico)\n    estado[", "    estado["),
 ("L37", PB, "retencao apaga o backup em curso", "    ficam.add(em_curso.resolve())", "    pass"),
 ("L38", PB, "retencao apaga a ultima PROVA_VALE", "        ficam.add(vale.resolve())", "        pass"),
 ("L39", PB, "retencao apaga o recibo", "PESADO = (\"pg\", \"SALA-ANTES-DA-MICRO.dump\")",
  "PESADO = (\"pg\", \"SALA-ANTES-DA-MICRO.dump\", \"PROVA-BACKUP-SALA.json\")"),
 ("L40", PB, "retencao nao poda nada (o disco cresce)", "        if p.resolve() in ficam:\n            continue",
  "        if True:\n            continue"),
 ("L41", PB, "a prova do backup nao devolve a DSN ao ambiente",
  "        if antes is None:\n            os.environ.pop(\"SINTONIA_SALA_DSN\", None)\n        else:\n"
  "            os.environ[\"SINTONIA_SALA_DSN\"] = antes",
  "        pass"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def aplicar(original: bytes, velho: str, novo: str) -> tuple[bytes | None, int]:
    """-> (os bytes do mutante, quantas vezes o alvo aparece). O alvo procura-se no texto com as
    quebras normalizadas para LF; o mutante escreve-se com as quebras ORIGINAIS (CRLF fica CRLF)."""
    texto = original.decode("utf-8")
    crlf = "\r\n" in texto
    lf = texto.replace("\r\n", "\n") if crlf else texto
    n = lf.count(velho)
    if n != 1:
        return None, n
    mutado = lf.replace(velho, novo)
    return (mutado.replace("\n", "\r\n") if crlf else mutado).encode("utf-8"), 1


def _correr_teste():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-B", "-m", "unittest", TESTE], cwd=RAIZ, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=900, env=env)


def _portal() -> set:
    return {q for q in (RAIZ / "italia-portale").rglob("*") if q.is_file()}


def main() -> int:
    ficheiros = sorted({m[1] for m in MUTANTES})
    antes = {f: sha(RAIZ / f) for f in ficheiros}
    portal = _portal()          # um mutante da fronteira (L42) escreve sob italia-portale/: limpa-se o que ele criou
    base = _correr_teste()
    out = {"TESTE": TESTE, "BASE_VERDE": base.returncode == 0, "MUTANTES": []}
    if base.returncode:
        print(base.stderr[-2000:])
        out["ESTADO"] = "BASE_VERMELHA"
        SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return 1
    for mid, f, finge, velho, novo in MUTANTES:
        p = RAIZ / f
        original = p.read_bytes()
        mutado, n = aplicar(original, velho, novo)
        if n != 1:
            out["MUTANTES"].append({"ID": mid, "FICHEIRO": f, "FINGE": finge, "ESTADO": "ALVO_NAO_UNICO (%d)" % n})
            print(mid, "ALVO_NAO_UNICO", n, finge, flush=True)
            continue
        try:
            p.write_bytes(mutado)
            r = _correr_teste()
            quem = [l.split("(")[0].replace("FAIL: ", "").replace("ERROR: ", "").strip()
                    for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
            out["MUTANTES"].append({"ID": mid, "FICHEIRO": f, "FINGE": finge,
                                    "ESTADO": "MORTO" if r.returncode else "SOBREVIVEU", "APANHADO_POR": quem[:4]})
        finally:
            p.write_bytes(original)
            sobra = sorted(str(q.relative_to(RAIZ)) for q in _portal() - portal)
            for q in sobra:
                (RAIZ / q).unlink(missing_ok=True)
            if sobra:
                out["MUTANTES"][-1]["LIMPOU_SOB_ITALIA_PORTALE"] = sobra
        print(mid, out["MUTANTES"][-1]["ESTADO"], finge, flush=True)
    depois = {f: sha(RAIZ / f) for f in ficheiros}
    out["PORTAL_IGUAL_NO_FIM"] = _portal() == portal
    mortos = sum(1 for m in out["MUTANTES"] if m["ESTADO"] == "MORTO")
    out.update({"MORTOS": mortos, "TOTAL": len(MUTANTES), "RESTAURADOS_IGUAIS": antes == depois,
                "ESTADO": "PASS" if mortos == len(MUTANTES) and antes == depois and out["PORTAL_IGUAL_NO_FIM"] else "FAIL"})
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("MORTOS %d/%d · restaurados iguais: %s" % (mortos, len(MUTANTES), antes == depois))
    return 0 if out["ESTADO"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
