#!/usr/bin/env python3
"""IT-T4-001 — portfolio italiano do grupo ADAMA a partir do registro oficial.

O site institucional `adama.com/italia/it` devolve 403 (Akamai) em toda rota de
saida de datacenter testada — inclusive `robots.txt`, o que indica bloqueio de
borda por IP, nao geo-bloqueio de conteudo. Portanto o portfolio, as bulas e as
substancias ativas nao vem do site da empresa: vem do registro do Ministero
della Salute, que e a fonte que a propria empresa tem de alimentar por lei.

    ./scripts/adama_italia.py baixar     -> resolve e baixa o CSV mais recente
    ./scripts/adama_italia.py extrair    -> gera o recorte ADAMA em JSON

Limitacao herdada da fonte (ver ATLAS IT-T4-001): o arquivo NAO traz cultura nem
alvo. Cultura e alvo estao na etichetta de cada produto, que nao faz parte deste
dataset. Nada aqui infere cultura.
"""
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import date, datetime

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
DATASET = "https://www.dati.salute.gov.it/it/dataset/fitosanitari/"
BASE = "https://www.dati.salute.gov.it/sites/default/files/opendata/"
RAW = "data/raw/IT-T4-001"
OUT = "data/samples/IT-T4-001"

# Estados que significam "vivo hoje". Tudo que nao esta aqui e historico.
VIVOS = ("Autorizzato", "Ri-registrato", "Rinnovato")


def _curl(url, dest=None):
    """curl com 4 tentativas — o cold start ja deu reset em outras fontes."""
    cmd = ["curl", "-sSL", "-m", "300", "-A", UA, "--retry", "4",
           "--retry-delay", "2", "--retry-connrefused", url]
    if dest:
        cmd += ["-o", dest]
        subprocess.run(cmd, check=True)
        return None
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def resolver():
    """O nome do arquivo e datado e muda a cada publicacao — descobrir, nao fixar."""
    pagina = _curl(DATASET)
    nomes = sorted(set(re.findall(r"PROD_FTS_6_\d{8}\.csv", pagina)))
    if not nomes:
        sys.exit("nenhum PROD_FTS_6_*.csv encontrado na pagina do dataset")
    return nomes[-1]


def baixar():
    nome = resolver()
    os.makedirs(RAW, exist_ok=True)
    destino = os.path.join(RAW, nome)
    if os.path.exists(destino):
        print(f"ja existe: {destino}")
    else:
        _curl(BASE + nome, destino)
        print(f"baixado: {destino}")
    return destino


def _mais_recente():
    arquivos = sorted(f for f in os.listdir(RAW) if f.startswith("PROD_FTS_6_"))
    if not arquivos:
        sys.exit(f"nenhum CSV em {RAW} — rode `{sys.argv[0]} baixar` antes")
    return os.path.join(RAW, arquivos[-1])


def _data(s):
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        return None


def extrair():
    origem = _mais_recente()
    versao = re.search(r"(\d{8})", origem).group(1)
    with open(origem, encoding="utf-8-sig") as fh:
        linhas = list(csv.DictReader(fh, delimiter=";"))

    grupo = [r for r in linhas if "ADAMA" in r["ragione_sociale"].upper()]
    hoje = date.today()
    produtos = []
    for r in grupo:
        venc = _data(r["data_scadenza_autorizzazione"])
        vivo = r["stato_amministrativo"].startswith(VIVOS)
        produtos.append({
            "num_registrazione": r["num_registrazione"],
            "produto": r["denominazione_prodotto"],
            "titular": r["ragione_sociale"],
            "estado_administrativo": r["stato_amministrativo"],
            "vivo": vivo,
            "data_registrazione": r["data_registrazione"],
            "data_scadenza": r["data_scadenza_autorizzazione"],
            "dias_ate_vencimento": (venc - hoje).days if venc and vivo else None,
            "formulacao": r["descrizione_formulazione"],
            "codice_formulazione": r["codice_formulazione"],
            "substancias_ativas": [s.strip() for s in r["sostanze_attive"].split("+") if s.strip() and s.strip() != "-"],
            "contenuto_per_100g": r["contenuto_per_100g_di_prodotto"],
            "indicazioni_di_pericolo": r["indicazioni_di_pericolo"],
            "importazione_parallela": r["importazione_parallela"],
            "PFnPO": r["PFnPO"],
            "PFnPE": r["PFnPE"],
            "motivo_revoca": r["motivo_della revoca"],
            "data_decreto_revoca": r["data_decreto_revoca"],
            "data_decorrenza_revoca": r["data_decorrenza_revoca"],
            "sede_legale_comune": r["comune_sede_legale"],
            "sede_legale_provincia": r["provincia_sede_legale"],
        })
    produtos.sort(key=lambda p: (not p["vivo"], p["produto"]))

    vivos = [p for p in produtos if p["vivo"]]
    ativas = Counter(s for p in vivos for s in p["substancias_ativas"])
    pacote = {
        "source_id": "IT-T4-001",
        "source_name": "Ministero della Salute — Banca dati dei prodotti fitosanitari",
        "source_url": DATASET,
        "arquivo_origem": os.path.basename(origem),
        "versao_do_dado": versao,
        "coletado_em": hoje.isoformat(),
        "camada": "REGISTERED PRESENCE",
        "nao_sei": [
            "cultura e alvo — nao estao neste dataset, estao na etichetta de cada produto",
            "volume, preco, share e prioridade interna — nenhuma fonte publica sustenta",
        ],
        "totais": {
            "linhas_no_registro": len(linhas),
            "registros_grupo_adama": len(produtos),
            "vivos": len(vivos),
            "por_titular": dict(Counter(p["titular"] for p in produtos)),
            "vivos_por_titular": dict(Counter(p["titular"] for p in vivos)),
            "por_estado": dict(Counter(p["estado_administrativo"] for p in produtos)),
        },
        "substancias_ativas_vivas": ativas.most_common(),
        "vencendo_em_180_dias": sorted(
            ({"produto": p["produto"], "num_registrazione": p["num_registrazione"],
              "data_scadenza": p["data_scadenza"], "dias": p["dias_ate_vencimento"]}
             for p in vivos if p["dias_ate_vencimento"] is not None
             and 0 <= p["dias_ate_vencimento"] <= 180),
            key=lambda x: x["dias"]),
        "produtos": produtos,
    }

    os.makedirs(OUT, exist_ok=True)
    destino = os.path.join(OUT, "IT-T4-001-adama-portfolio.json")
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(pacote, fh, ensure_ascii=False, indent=2)
    print(f"gerado: {destino}")
    print(f"  {len(produtos)} registros do grupo ADAMA, {len(vivos)} vivos")
    print(f"  {len(pacote['vencendo_em_180_dias'])} vencendo nos proximos 180 dias")
    return pacote


if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else "extrair"
    if acao == "baixar":
        baixar()
    elif acao == "extrair":
        extrair()
    else:
        sys.exit(f"uso: {sys.argv[0]} baixar|extrair")
