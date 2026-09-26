#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao da LUGAR-DO-PUBLICADOR: cada mutante tem de pôr tests/test_lugar_do_publicador.py vermelho. Repoe sempre."""
import json, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTE = "tests/test_lugar_do_publicador.py"
MUTANTES = {
    "M1_sem_a_sigla_PD": ("curadoria/sede_da_fonte.py", '"PD": "Padova", ', ""),
    "M2_sigla_para_provincia_fora_do_gazetteer": ("curadoria/sede_da_fonte.py", '"CR": "Cremona"', '"CR": "Casalmaggiore"'),
    "M3_so_tabela_pisa_a_regra_que_existe": ("ferramentas/sede37/escrever_sede.py",
                                            '            if sid in pt and not pt[sid].get("SOURCE_LOCATION_RULE"):\n',
                                            '            if sid in pt:\n'),
    "M4_fora_do_curator_salta": ("ferramentas/sede37/escrever_sede.py",
                                 '                acoes.append(dict(a, ACAO="APLICA", TABELA="SOURCE_LOCATION_RULE (so a tabela: fora do Curator)")); continue\n',
                                 '                pt[sid].pop("SOURCE_LOCATION_RULE"); continue\n'),
    "M5_operacional_na_regra": ("ferramentas/sede37/escrever_sede.py",
                                '                fora[l["SOURCE_ID"]]["SOURCE_LOCATION_BASIS"] += " · " + SEDE_OPERACIONAL[l["SOURCE_ID"]]\n',
                                '                fora[l["SOURCE_ID"]]["SOURCE_LOCATION_RULE"] += " · " + SEDE_OPERACIONAL[l["SOURCE_ID"]]\n'),
    "M6_sala_pisa_a_sede_que_existe": ("ferramentas/lugar_publicador/preencher_sede_na_sala.py",
                                       '    if u["SOURCE_LOCATION"] not in VAZIOS:\n', '    if False:\n'),
    "M7_completude_nao_acompanha": ("ferramentas/lugar_publicador/preencher_sede_na_sala.py",
                                    '    fora["LOCAL_DA_FONTE"] = adm.COMPLETUDE_PROVADA if tem_sede else adm.AUSENCIA\n', ''),
    "M8_nao_sei_do_contrato_entra": ("ferramentas/lugar_publicador/preencher_sede_na_sala.py",
                                     '    if r["VALOR"] in VAZIOS:\n', '    if r["VALOR"] is None:\n'),
    "M9_le_o_envelope_como_lista": ("ferramentas/lugar_publicador/preencher_sede_na_sala.py",
                                    '        for u in (espera.ler_atual(run) or {}).get("ITENS") or []:\n',
                                    '        for u in espera.ler_atual(run) or []:\n'),
}


def main():
    res = {}
    for nome, (rel, a, b) in MUTANTES.items():
        alvo = RAIZ / rel
        original = alvo.read_bytes()
        texto = original.decode("utf-8")
        nl = "\r\n" if "\r\n" in texto else "\n"
        try:
            a2, b2 = a.replace("\n", nl), b.replace("\n", nl)
            assert texto.count(a2) == 1, nome
            alvo.write_bytes(texto.replace(a2, b2).encode("utf-8"))
            r = subprocess.run([sys.executable, "-B", TESTE], cwd=RAIZ, capture_output=True, text=True)
            res[nome] = "MORTO" if r.returncode else "SOBREVIVEU"
        finally:
            alvo.write_bytes(original)
    print(json.dumps({"MUTANTES": res, "MORTOS": sum(v == "MORTO" for v in res.values()), "DE": len(res)}, indent=1))
    return 0 if all(v == "MORTO" for v in res.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
