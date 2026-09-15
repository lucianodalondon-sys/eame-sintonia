#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM DA REFERÊNCIA ADAMA — catorze ataques, por mutação real.

    py provas/red_team_adama_referencia.py

    UM TESTE QUE PASSA COM O DEFEITO POSTO DE VOLTA NÃO ESTAVA A MEDIR NADA.

Cada ataque **põe o defeito dentro** — nos dados escritos, não numa cópia em
memória — e exige que `tests/test_adama_referencia.py` **REPROVE**. Se a suite
continuar verde com o defeito lá, o ataque SOBREVIVEU e a trava é decorativa.

⚠️ A árvore é restaurada ao fim de cada ataque, mesmo que ele rebente.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASA = os.path.join(RAIZ, "referencia", "adama")
SUITE = os.path.join(RAIZ, "tests", "test_adama_referencia.py")


def ler(nome):
    with io.open(os.path.join(CASA, nome), encoding="utf-8") as fh:
        return json.load(fh)


def escrever(nome, obj):
    with io.open(os.path.join(CASA, nome), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def suite_reprova():
    """True quando a suite REPROVA. É isso que um ataque tem de provocar."""
    amb = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, SUITE], cwd=RAIZ, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=amb)
    return r.returncode != 0


# ── os ataques ────────────────────────────────────────────────────────────
# Cada um recebe o objecto já lido, devolve o objecto estragado.

def a01_fundir_dois_produtos_com_mesmo_nome(m):
    """`Highcard®` e `Max-Ace®` partilham a autorizacao 017995. Fundi-los é a
    tentação óbvia — e apaga um produto do catálogo."""
    m["PRODUCTS"] = m["PRODUCTS"][:-1]
    return m


def a02_o_r_corrompido_vira_produto_proprio(m):
    """`APYZAR WG` ganha entrada própria: um produto fantasma que se lê como
    real."""
    for p in m["PRODUCTS"]:
        for n in p["OBSERVED_NAMES"]:
            if n["NAME_STATE"] == "SIMBOLO_REGISTADO_LIDO_COMO_LETRA_R":
                novo = dict(p)
                novo["ADAMA_PRODUCT_ID"] = "ADAMA-P-9001"
                novo["CANONICAL_NAME"] = n["OBSERVED_NAME"]
                novo["IDENTITY_ANCHORS"] = ["URL:fantasma"]
                m["PRODUCTS"].append(novo)
                return m
    return m


def a03_o_registo_partilhado_escolhe_um_lado(r):
    """`017995` deixa de dizer MULTIPLE e escolhe um dos dois. O outro produto
    passa a não ter autorização, sem que nada acuse."""
    for x in r["RECORDS"]:
        if len(x["ADAMA_PRODUCT_IDS"]) > 1:
            x["ADAMA_PRODUCT_ID"] = x["ADAMA_PRODUCT_IDS"][0]
            x["ADAMA_PRODUCT_IDS"] = x["ADAMA_PRODUCT_IDS"][:1]
    return r


def a04_a_foto_nova_apaga_a_antiga(s):
    """A de 24/08 sai. Os 2030 usos passam a ser afirmações sem data."""
    s["RECORDS"] = [x for x in s["RECORDS"] if x["SNAPSHOT_ID"] != "PROD_FTS_6_20260824"]
    return s


def a05_regenerar_muda_a_identidade(m):
    """O ataque mais silencioso: os IDs andam uma casa."""
    ids = [p["ADAMA_PRODUCT_ID"] for p in m["PRODUCTS"]]
    for p, novo in zip(m["PRODUCTS"], ids[1:] + ids[:1]):
        p["ADAMA_PRODUCT_ID"] = novo
    return m


def a06_o_registo_vira_product_id(m):
    """`ADAMA-P-0045` passa a ser `ADAMA-P-017995`. Parece arrumação e amarra a
    nossa identidade ao número do Ministero."""
    for p in m["PRODUCTS"]:
        p["ADAMA_PRODUCT_ID"] = "ADAMA-P-017995"
        break
    return m


def a07_o_uso_perde_o_documento_de_origem(u):
    """Sem registo, o par cultura × alvo é uma frase sem papel por trás."""
    for x in u["RECORDS"][:40]:
        x["REGISTRATION_NUMBER"] = "999999"
    return u


def a08_dose_sem_prova_entra_como_verdade(d):
    """Um dos 142 rótulos que não deu tabela ganha uma linha inventada."""
    for x in d["RECORDS"]:
        if not x["ROW_COUNT"]:
            x["PARSE_STATE"] = "USE_TABLE_READ"
            x["ROW_COUNT"] = 1
            x["ROWS"] = [{"CROP": "VITE", "TARGET": "PERONOSPORA",
                          "DOSE_PER_HECTARE": 1.5}]   # sem SOURCE_QUOTE
            return d
    return d


def a09_as_560_sem_catalogo_sao_descartadas(r):
    """«Não estão no catálogo, não servem.» Servem: são o registo italiano."""
    r["RECORDS"] = [x for x in r["RECORDS"] if x["ADAMA_PRODUCT_ID"] != "UNKNOWN"]
    return r


def a10_os_titulares_adama_sao_fundidos(r):
    """Cinco entidades legais viram uma «ADAMA». Apaga quem responde."""
    for x in r["RECORDS"]:
        if x["HOLDER"] != "NAO SEI":
            x["HOLDER"] = "ADAMA"
    return r


def a11_o_vencimento_volta_a_ser_data_de_observacao(r):
    """O defeito original: `REFERENCE_DATE == EXPIRY` em 163 de 163."""
    for x in r["RECORDS"]:
        if x["EXPIRY_DATE"] != "NAO SEI":
            x["OBSERVED_AT"] = x["EXPIRY_DATE"]
    return r


def a12_o_id_italiano_vira_regra_eame(m):
    """`ADAMA-P-0001` volta a ser `IT-PRODUCT-0001`."""
    for p in m["PRODUCTS"]:
        p["ADAMA_PRODUCT_ID"] = "ADAMA-P-IT" + p["ADAMA_PRODUCT_ID"][-4:]
        p["COUNTRY_SCOPE"] = []
    return m


def a13_o_source_id_legado_volta_a_ser_canonico(r):
    """`SRC_FITOSANITARI_SALUTE_GOV_IT` reaparece como canónico, e a referência
    deixa de falar com o Atlas."""
    for x in r["RECORDS"]:
        x["PROVENANCE"]["SOURCE_IDS"] = ["SRC_FITOSANITARI_SALUTE_GOV_IT"]
    return r


def a14_o_consumidor_volta_a_escolher(_):
    """O contrato deixa de nomear autoridade: some um ficheiro da casa."""
    return None   # tratado à parte: apaga o ficheiro


ATAQUES = [
    ("01", "dois produtos com mesmo nome sao fundidos", "PRODUCT-MASTER.json", a01_fundir_dois_produtos_com_mesmo_nome),
    ("02", "R corrompido cria produto fantasma", "PRODUCT-MASTER.json", a02_o_r_corrompido_vira_produto_proprio),
    ("03", "017995 funde entidades sem prova", "REGISTRATIONS.json", a03_o_registo_partilhado_escolhe_um_lado),
    ("04", "snapshot novo apaga o historico", "SNAPSHOTS.json", a04_a_foto_nova_apaga_a_antiga),
    ("05", "regeneracao muda ADAMA_PRODUCT_ID", "PRODUCT-MASTER.json", a05_regenerar_muda_a_identidade),
    ("06", "registo e usado como PRODUCT_ID", "PRODUCT-MASTER.json", a06_o_registo_vira_product_id),
    ("07", "uso autorizado perde o registo de origem", "AUTHORIZED-USES.json", a07_o_uso_perde_o_documento_de_origem),
    ("08", "dose sem prova entra como verdade", "DOSES.json", a08_dose_sem_prova_entra_como_verdade),
    ("09", "560 registos sem catalogo sao descartados", "REGISTRATIONS.json", a09_as_560_sem_catalogo_sao_descartadas),
    ("10", "titulares ADAMA diferentes sao fundidos", "REGISTRATIONS.json", a10_os_titulares_adama_sao_fundidos),
    ("11", "EXPIRY volta a ser data de observacao", "REGISTRATIONS.json", a11_o_vencimento_volta_a_ser_data_de_observacao),
    ("12", "ID italiano vira regra EAME", "PRODUCT-MASTER.json", a12_o_id_italiano_vira_regra_eame),
    ("13", "SOURCE_ID legado volta a ser canonico", "PORTFOLIO.json", a13_o_source_id_legado_volta_a_ser_canonico),
    ("14", "consumidor volta a escolher (autoridade some)", "DOSES.json", a14_o_consumidor_volta_a_escolher),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not os.path.isdir(CASA):
        print("referencia/adama/ nao existe — corre fontes/adama_referencia.py")
        return 1
    guardado = tempfile.mkdtemp(prefix="adama-ref-")
    shutil.rmtree(guardado)
    shutil.copytree(CASA, guardado)
    print("  #   ataque                                          resultado")
    print("  " + "-" * 74)
    vivos = 0
    try:
        for num, titulo, ficheiro, fn in ATAQUES:
            try:
                if fn is a14_o_consumidor_volta_a_escolher:
                    os.remove(os.path.join(CASA, ficheiro))
                else:
                    escrever(ficheiro, fn(ler(ficheiro)))
                morreu = suite_reprova()
            finally:
                shutil.rmtree(CASA)
                shutil.copytree(guardado, CASA)
            if not morreu:
                vivos += 1
            print("  %-3s %-48s %s" % (num, titulo[:48],
                                       "MORREU" if morreu else "*** SOBREVIVEU ***"))
    finally:
        shutil.rmtree(guardado, ignore_errors=True)
    print("  " + "-" * 74)
    print("  RED_TEAM_ATTACKS   = %d" % len(ATAQUES))
    print("  RED_TEAM_SURVIVORS = %d" % vivos)
    return 1 if vivos else 0


if __name__ == "__main__":
    raise SystemExit(main())
