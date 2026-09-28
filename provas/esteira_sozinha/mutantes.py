#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTACAO DA ESTEIRA-SOZINHA — planta UM defeito de cada vez na passagem, no gatilho, no vigia e no
gancho do supervisor, corre `tests.test_esteira_sozinha`, e exige que ele REPROVE. Restaura os bytes
originais sempre (sem `git checkout`) e confere no fim que cada ficheiro voltou igual (SHA-256).

    python3 provas/esteira_sozinha/mutantes.py        # grava provas/esteira_sozinha/MUTANTES.json

Um mutante que sobrevive e um teste que falta, nao um mutante mau.

CRLF (FECHO 28/09): com `core.autocrlf=true` (Windows) os ficheiros vem com CRLF e os alvos de varias
linhas (escritos com \n) nao batiam -> ALVO_NAO_UNICO (0). `aplicar()` procura sobre o texto em LF e
devolve o mutante com as quebras de linha ORIGINAIS do ficheiro; o restauro continua a ser os bytes
originais, conferidos por SHA-256.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = Path(__file__).resolve().parent / "MUTANTES.json"
TESTE = "tests.test_esteira_sozinha"
PAS = "admissao/passagem_para_a_sala.py"
GI = "admissao/gatilho_da_inteligencia.py"
VIG = "medidas/vigia_da_esteira.py"
SUP = "curadoria/supervisor.py"
PB = "scripts/micro_coleta/provar_backup_da_sala.py"

#: (id, ficheiro, o defeito que finge, texto original, texto mutante)
MUTANTES = [
 # ── duas corridas sobrepostas ──
 ("E1", GI, "Intelligence sem trinco: duas corridas ao mesmo tempo",
  "        with espera._Trava(str(trinco)):\n            pasta_corrida = ",
  "        with open(os.devnull):\n            pasta_corrida = "),
 ("E2", PAS, "passagem sem trinco: dois escritores na Sala",
  "        with espera._Trava(str(trinco)):\n            em_curso = ",
  "        with open(os.devnull):\n            em_curso = "),
 # ── Admission sem backup ──
 ("E3", PAS, "Admission grava sem PROVA_VALE",
  "    if not b.get(\"PROVA_VALE\"):", "    if False:"),
 ("E4", PAS, "Admission nem chama o backup",
  "    b = (backup or backup_padrao)(em_curso / \"backup\")",
  "    b = {\"PROVA_VALE\": True}"),
 # ── gatilho sem delta / regra torta ──
 ("E5", GI, "gatilho corre sem delta",
  "    if n <= 0:\n        return {\"DECISAO\": ESPERAR, \"PORQUE\": \"SEM_DELTA\"}",
  "    if n < 0:\n        return {\"DECISAO\": ESPERAR, \"PORQUE\": \"SEM_DELTA\"}"),
 ("E6", GI, "limiar de 10 vira 1", "    if n >= LIMIAR_NOVOS:", "    if n >= 1:"),
 ("E7", GI, "4 h viram nada", "    if agora - velho >= ESPERA_MAXIMA:", "    if True:"),
 ("E8", GI, "delta nao medido vira zero (ESPERAR em vez de NAO SEI)",
  "        return {\"DECISAO\": NAO_SEI, \"PORQUE\": \"o delta da Sala nao foi medido\"}",
  "        return {\"DECISAO\": ESPERAR, \"PORQUE\": \"SEM_DELTA\"}"),
 ("E9", GI, "a marca nao anda: a mesma Sala corre para sempre",
  "    estado[\"INT_MARCA\"] = delta.get(\"MAIS_NOVO_EM\") or estado.get(\"INT_MARCA\")",
  "    estado[\"INT_MARCA\"] = estado.get(\"INT_MARCA\")"),
 ("E10", GI, "sem recuo depois de falha (a copia refaz-se de 15 em 15 s)",
  "    if falhou and agora - falhou < RECUO:", "    if False:"),
 # ── o pote que falha sobe ──
 ("E11", GI, "pote reprovado sobe", "    if violacoes:\n        pasta.mkdir(", "    if False:\n        pasta.mkdir("),
 ("E12", GI, "export sem READ_ONLY=on serve", "    if exp.get(\"READ_ONLY\") != \"on\":", "    if False:"),
 ("E13", GI, "copia sem PROVA_VALE corre o motor na mesma",
  "        if export is None:\n            estado[\"INT_ULTIMA_FALHA_EM\"]",
  "        if export is None and False:\n            estado[\"INT_ULTIMA_FALHA_EM\"]"),
 # ── PARAR.flag ──
 ("E14", GI, "gatilho ignora PARAR.flag",
  "    agora = agora or _agora()\n    if parar.exists():\n        return {\"ACCAO\": \"PARAR_FLAG\"}",
  "    agora = agora or _agora()\n    if False:\n        return {\"ACCAO\": \"PARAR_FLAG\"}"),
 ("E15", PAS, "passagem ignora PARAR.flag",
  "    agora = agora or _agora()\n    if parar.exists():\n        return {\"ACCAO\": \"PARAR_FLAG\"}",
  "    agora = agora or _agora()\n    if False:\n        return {\"ACCAO\": \"PARAR_FLAG\"}"),
 # ── a passagem que passa o que nao deve ──
 ("E16", PAS, "universo sem regua vai a porta (NAO_SE_APLICA garantido)",
  "            if u not in adm.PERGUNTAS_DO_UNIVERSO:", "            if False:"),
 ("E17", PAS, "corrida ja levada passa outra vez", "        if run in feitas:\n            continue",
  "        if False:\n            continue"),
 ("E18", PAS, "o passado atravessa sozinho na primeira volta",
  "    estado.setdefault(\"PAS_DESDE\", agora.isoformat())", "    pass"),
 ("E19", PAS, "corrida com varias fontes vai a porta com UM universo",
  "        elif len(fontes) > 1:", "        elif False:"),
 # ── o vigia calado ──
 ("E20", VIG, "NAO SEI deixa de ser alerta", "        if linha[\"ESTADO\"] != ANDANDO:",
  "        if linha[\"ESTADO\"] == PARADA:"),
 ("E21", VIG, "o vigia nunca alerta", "\"ALERTA\": bool(alertas)", "\"ALERTA\": False"),
 ("E22", VIG, "marca que rebenta vira «andou agora»",
  "            quando, de_onde = None, \"erro a ler: %s\" % repr(e)[:200]",
  "            quando, de_onde = agora.isoformat(), \"x\""),
 ("E23", VIG, "o vigia nao escreve", "    escrever(r, saude, historico)\n    estado[", "    estado["),
 # ── extensao do supervisor, e nao segundo orquestrador ──
 ("E24", SUP, "o servico nao chama a esteira", "            _hook_esteira()\n", "\n"),
 ("E25", SUP, "a esteira liga-se em qualquer _loop (testes escrevem na Sala)",
  "    passos_da_esteira = _passos_da_esteira() if esteira else ()",
  "    passos_da_esteira = _passos_da_esteira()"),
 # ── FECHO 28/09: a porta que falha, a retencao, e o READ_ONLY em qualquer SO ──
 ("E27", PAS, "porta falha (CODIGO!=0) e e marcada passada", "        if passou_pela_porta(r):",
  "        if True:"),
 ("E28", PAS, "passou = qualquer recibo (ignora CODIGO e a linha CORRIDA)",
  "    return recibo.get(\"CODIGO\") == 0 and recibo.get(\"CORRIDA_DA_PORTA\") not in (None, \"NAO SEI\")",
  "    return True"),
 ("E29", PAS, "falha da porta nao grava PAS_ULTIMA_FALHA_EM (sem recuo: loop apertado)",
  "    if falharam:\n        estado[\"PAS_ULTIMA_FALHA_EM\"]", "    if False:\n        estado[\"PAS_ULTIMA_FALHA_EM\"]"),
 ("E30", PAS, "a falha nao fica registada com a causa",
  "            falhas[run] = {\"EM\": agora.isoformat(),", "            {\"EM\": agora.isoformat(),"),
 ("E31", PAS, "corrida falhada nunca volta a ser tentada",
  "            falhas.pop(run, None)\n        else:", "            falhas.pop(run, None)\n        else:\n            feitas[run] = r"),
 ("E32", PAS, "sem recuo por corrida", "            if quando and agora - quando < recuo_da_corrida(falhou):",
  "            if False:"),
 ("E33", PAS, "recuo por corrida sem teto", "    return min(RECUO * (2 ** min(n - 1, 16)), RECUO_MAXIMO)",
  "    return RECUO * (2 ** min(n - 1, 16))"),
 ("E34", PAS, "porta que rebenta derruba a volta (e nao fica registada)",
  "        except Exception as e:  # noqa: BLE001 — a porta que rebenta tambem nao passou",
  "        except ZeroDivisionError as e:  # noqa"),
 ("E35", PB, "retencao apaga o backup em curso", "    ficam.add(em_curso.resolve())", "    pass"),
 ("E36", PB, "retencao apaga a ultima PROVA_VALE", "        ficam.add(vale.resolve())", "        pass"),
 ("E37", PB, "retencao apaga o recibo (a prova de que houve backup)",
  "PESADO = (\"pg\", \"SALA-ANTES-DA-MICRO.dump\")",
  "PESADO = (\"pg\", \"SALA-ANTES-DA-MICRO.dump\", \"PROVA-BACKUP-SALA.json\")"),
 ("E38", PB, "retencao nao poda nada (o disco cresce)", "        if p.resolve() in ficam:\n            continue",
  "        if True:\n            continue"),
 ("E39", PB, "retencao guarda N-1", "    ficam = {p.resolve() for p in corridas[-guardar:]} if guardar > 0 else set()",
  "    ficam = {p.resolve() for p in corridas[-guardar + 1:]} if guardar > 1 else set()"),
 ("E40", PAS, "a passagem nao poda", "                    estado[\"PAS_ULTIMA_PODA\"] = (podar or podar_padrao)(pasta, em_curso)",
  "                    estado[\"PAS_ULTIMA_PODA\"] = {}"),
 ("E41", GI, "a Intelligence nao poda",
  "                    estado[\"INT_ULTIMA_PODA\"] = (podar or podar_padrao)(pasta, pasta_corrida)",
  "                    estado[\"INT_ULTIMA_PODA\"] = {}"),
 ("E42", GI, "a poda da Intelligence corre ANTES da corrida (leva a em curso)",
  "            try:\n                return _correr(estado, agora, delta, d, copia, motor, subir, parar, pasta_corrida)",
  "            (podar or podar_padrao)(pasta, pasta_corrida)\n            try:\n"
  "                return _correr(estado, agora, delta, d, copia, motor, subir, parar, pasta_corrida)"),
 ("E43", GI, "export sem a transacao so-leitura no comando",
  "\"-c\", \"begin transaction read only\", ", ""),
 ("E44", VIG, "o vigia cala a porta que falha", "    if falhas:\n        alertas.append(", "    if False:\n        alertas.append("),
 ("E26", SUP, "um passo que rebenta derruba o supervisor",
  "            except Exception as e:  # noqa: BLE001 — o supervisor nao morre por isto\n"
  "                _anotar({\"EVENTO\": \"ESTEIRA_ERRO\"",
  "            except ZeroDivisionError as e:  # noqa\n                raise\n"
  "                _anotar({\"EVENTO\": \"ESTEIRA_ERRO\""),
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


def main() -> int:
    ficheiros = sorted({m[1] for m in MUTANTES})
    antes = {f: sha(RAIZ / f) for f in ficheiros}
    base = subprocess.run([sys.executable, "-m", "unittest", TESTE], cwd=RAIZ, capture_output=True, text=True)
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
            continue
        try:
            p.write_bytes(mutado)
            r = subprocess.run([sys.executable, "-m", "unittest", TESTE], cwd=RAIZ, capture_output=True,
                               text=True, timeout=600)
            quem = [l.split("(")[0].replace("FAIL: ", "").replace("ERROR: ", "").strip()
                    for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
            out["MUTANTES"].append({"ID": mid, "FICHEIRO": f, "FINGE": finge,
                                    "ESTADO": "MORTO" if r.returncode else "SOBREVIVEU", "APANHADO_POR": quem[:4]})
        finally:
            p.write_bytes(original)
        print(mid, out["MUTANTES"][-1]["ESTADO"], finge, flush=True)
    depois = {f: sha(RAIZ / f) for f in ficheiros}
    mortos = sum(1 for m in out["MUTANTES"] if m["ESTADO"] == "MORTO")
    out.update({"MORTOS": mortos, "TOTAL": len(MUTANTES), "RESTAURADOS_IGUAIS": antes == depois,
                "ESTADO": "PASS" if mortos == len(MUTANTES) and antes == depois else "FAIL"})
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("MORTOS %d/%d · restaurados iguais: %s" % (mortos, len(MUTANTES), antes == depois))
    return 0 if out["ESTADO"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
