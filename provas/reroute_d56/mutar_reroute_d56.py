#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REROUTE-D56 · MUTACAO: planta um defeito de cada vez e prova que `tests/test_reroute_d56.py` o apanha.

    python3 provas/reroute_d56/mutar_reroute_d56.py [--saida=provas/reroute_d56/MUTACAO-REROUTE-D56.json]

Cada mutante troca UM trecho (que tem de existir UMA vez), corre o teste, e repoe o ficheiro; o sha256 do
ficheiro reposto e conferido contra o original (se nao bater, para e grita). A copia limpa corre antes e
tem de passar. Sem rede; o banco e o Postgres DESCARTAVEL do proprio teste (binarios de ~/orca/pgtmp) —
sem eles os mutantes da Sala saem SEM_BANCO, e isso fica escrito. (O mecanismo de
provas/chave_problema/mutacao_chave_problema.py.)
"""
import hashlib
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TESTE = "tests.test_reroute_d56"          # varios modulos: separados por espaco (REROUTE-T1T2)
DATASET = "MUTACAO-REROUTE-D56-V1"
SAIDA = os.path.join(RAIZ, "provas", "reroute_d56", "MUTACAO-REROUTE-D56.json")
AD, SE = "admissao/admissao.py", "admissao/sala_de_espera.py"
OQ, RR = "orquestrador/orquestrador.py", "admissao/reprocessar_reroute.py"

MUTANTES = [
    # ── a porta ──
    # REROUTE-T1T2 (D130, DECLARADO): o trecho de M01 mudou — o filtro passou a `_reroute_entra(d)`.
    ("M01", AD, "    sims = [d for d in decisoes[1:] if _reroute_entra(d)]", "    sims = []",
     "o SIM de outro universo nao da item: so o pedido entra (a D56 desligada em silencio)"),
    ("M02", AD, '    corpo = _ft.corpo(str(item.get("texto") or ""))', '    corpo = str(item.get("texto") or "")',
     "o MENU conta: o reroute julga a pagina inteira"),
    ("M03", AD, "    trechos = _trechos(texto, universo, lingua)\n    ev[\"trechos\"] = trechos\n    if not trechos:",
     "    trechos = []\n    ev[\"trechos\"] = trechos\n    if False:",
     "SIM sem trecho passa"),
    ("M04", AD, "    if d0.regra != REGRA_DA_PERTENCA:",
     "    if d0.regra != REGRA_DA_PERTENCA or d0.resultado == NAO_SE_APLICA:",
     "pedido sem regua cala TODOS os universos (NSA deixa de ser so dele)"),
    ("M05", AD, "    if d0.regra != REGRA_DA_PERTENCA:", "    if False:",
     "item parado num portao de prontidao e perguntado as outras reguas"),
    ("M06", AD, '    if universo == "T9":', "    if False:",
     "T9 sem concorrente nomeado (comunicacao de cantina vira concorrencia)"),
    ("M07", AD, 'REROUTE_PROMOVE = frozenset({"T1", "T2", "T3", "T10"})',
     "REROUTE_PROMOVE = frozenset(PERGUNTAS_DO_UNIVERSO)",
     "as reguas sem medida (T4, T5 — 1/6 e 1/8 no replay) passam a promover"),
    ("M08", AD, "                                inicio_de_palavra=True)",
     "                                inicio_de_palavra=False)",
     "o reroute volta a casar pedaco de palavra («revista» dentro de «prevista»)"),
    ("M09", AD, "        achadas = [p for p in palavras if _no_inicio_de_palavra(p, texto)]",
     "        achadas = [p for p in palavras if _dobrar(p) in texto]",
     "o inicio de palavra e ignorado dentro da regua"),
    ("M10", AD, "    for d in [p] + outras:", "    for d in outras:",
     "a gaveta da linha nao viaja: o documento ja na Sala perde a gaveta deste pedido"),
    # ── a Sala ──
    ("M11", SE, "                        where s.item_id = e.item_id\n                          and s.run_id <> e.run_id)",
     "                        where s.item_id = e.item_id and s.universo = e.universo\n"
     "                          and s.run_id <> e.run_id)",
     "o universo volta a identidade: o mesmo item noutro universo ganha 2.a LINHA"),
    ("M12", SE, "   where g.universo <> c.universo\n", "   where true\n",
     "a gaveta da propria linha e escrita (a Sala recusa: universo = origem)"),
    ("M13", SE, '                if g["UNIVERSO"] == u["UNIVERSO"] or k in tem:',
     '                if g["UNIVERSO"] == u["UNIVERSO"]:',
     "FICHEIRO: reprocessar repete a gaveta"),
    ("M14", SE, "     and not exists (select 1 from public.sala_de_espera_gaveta x\n"
                "                      where x.run_id = c.run_id and x.ordem = c.ordem\n"
                "                        and x.universo = g.universo)\n   order by",
     "   order by",
     "POSTGRES: o retry tenta a mesma gaveta outra vez"),
    ("M15", SE, "      on s.run_id = g.run_id and s.ordem = g.ordem and s.universo = g.origem",
     "      on s.run_id = g.run_id and s.ordem = g.ordem",
     "o reprocesso escreve gaveta numa linha cuja origem mudou"),
    # ── a estrada e o reprocesso ──
    ("M16", OQ, "        d = adm.principal(ds)", "        d = ds[0] if ds[0].resultado == adm.SIM else None",
     "pela_porta ignora o reroute (so o pedido pousa)"),
    ("M17", OQ, "        adm.escrever([d for ds in por_item for d in ds])", "        adm.escrever(decisoes)",
     "o livro so guarda o pedido: as decisoes dos outros universos perdem-se"),
    ("M18", RR, "    if not os.path.exists(parar):", "    if False:",
     "--aplicar escreve com o robo a correr (sem PARAR.flag)"),
    ("M19", RR, '    if not isinstance(backup, dict) or backup.get("PROVA_VALE") is not True:', "    if False:",
     "--aplicar escreve sem backup PROVA_VALE"),
    ("M20", RR, "            if u in ja_sao_linha:", '            if u == canonica["UNIVERSO"]:',
     "o seco da gaveta a um universo que ja e LINHA de outra copia do documento"),
]


def _sha(p):
    with open(p, "rb") as h:
        return hashlib.sha256(h.read()).hexdigest()


def _correr():
    r = subprocess.run([sys.executable, "-m", "unittest", *TESTE.split()], cwd=RAIZ, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    out = r.stdout + r.stderr
    falhas = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+)", out, re.M)))
    saltos = len(re.findall(r"skipped", out))
    return r.returncode, falhas, (out.strip().splitlines() or [""])[-1], saltos


def main(argv):
    saida = next((a.split("=", 1)[1] for a in argv if a.startswith("--saida=")), SAIDA)
    rc, falhas, fim, saltos = _correr()
    if rc != 0:
        print("A COPIA LIMPA NAO PASSA: %s %s" % (fim, falhas))
        return 2
    resultados = []
    for mid, rel, antes, depois, porque in MUTANTES:
        f = os.path.join(RAIZ, rel)
        with open(f, encoding="utf-8") as h:
            original = h.read()
        sha = _sha(f)
        n = original.count(antes)
        if n != 1:
            resultados.append({"ID": mid, "FICHEIRO": rel, "ESTADO": "TRECHO_NAO_UNICO", "VEZES": n,
                               "PORQUE": porque})
            continue
        try:
            with open(f, "w", encoding="utf-8", newline="") as h:
                h.write(original.replace(antes, depois))
            rc_m, falhas_m, fim_m, saltos_m = _correr()
        finally:
            with open(f, "w", encoding="utf-8", newline="") as h:
                h.write(original)
        if _sha(f) != sha:
            raise SystemExit("O FICHEIRO %s NAO VOLTOU AO ORIGINAL — pare e confira" % rel)
        estado = "MORTO" if rc_m != 0 else ("SEM_BANCO" if saltos_m else "SOBREVIVEU")
        resultados.append({"ID": mid, "FICHEIRO": rel, "PORQUE": porque, "ESTADO": estado,
                           "TESTES_QUE_APANHARAM": falhas_m[:6], "ULTIMA_LINHA": fim_m})
        print("%s %-10s %s" % (mid, estado, porque))
    mortos = sum(1 for r in resultados if r["ESTADO"] == "MORTO")
    doc = {"DATASET": DATASET, "TESTE": TESTE, "COPIA_LIMPA": fim,
           "SALTOS_NA_COPIA_LIMPA": saltos, "MUTANTES": len(resultados), "MORTOS": mortos,
           "RESULTADOS": resultados}
    with open(saida, "w", encoding="utf-8") as h:
        json.dump(doc, h, ensure_ascii=False, indent=1)
        h.write("\n")
    print("MORTOS %d/%d" % (mortos, len(resultados)))
    return 0 if mortos == len(resultados) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
