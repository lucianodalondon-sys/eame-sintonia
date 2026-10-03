#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BLOQUEADAS-268 — classificar as tarefas BLOCKED e FAILED da fila do robô por MOTIVO. SÓ LEITURA do vivo.

    py curadoria/bloqueadas_268.py [<raiz-do-vivo>]

Lê (nunca escreve): curadoria/LIFECYCLE-QUEUE-V1.json, LIFECYCLE-LEDGER-V1.json, italy_contracts_curator.json,
DECISOES-SEMANTICAS-V1.json e candidatas/FONTES-CANDIDATAS.json do vivo. Sem rede.
Escreve curadoria/BLOQUEADAS-268-V1.json nesta árvore.

Para cada tarefa: MOTIVO (a frase do LAST_ERROR sem o nome próprio), CLASSE_T (do SOURCE_ID, se já houver),
DOMINIO, e uma PROPOSTA — nunca uma decisão:
  PROPOR_RECUSA      só por regra explícita (a regra fica escrita na linha): serviço/redes/turismo/órgão
                     legislativo, ou MOTIVO_DA_RECUSA já anotado na ficha;
  DUPLICADA_DE       o MESMO endereço já é de uma fonte (ou a revisão semântica já o disse);
  MESMO_SITE_*       o site já tem fontes: classe única (herança por decisão do dono) ou mistas; lidas à mão;
  CORRIGIR_URL       a revisão semântica achou identidade trocada (organização real, endereço errado);
  PRECISA_DECISAO    fonte com cara de agro/instituição: território pelo canal DECISOES-SEMANTICAS (prova de rede).
UNKNOWN não funde nem vira fato: uma proposta de recusa é para o dono confirmar pela porta (fonte_nova.recusar).
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
VIVO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
SAIDA = RAIZ / "curadoria" / "BLOQUEADAS-268-V1.json"

# Regras de «não é fonte» — cada uma com o nome que aparece na linha. Casam no NOME ou no URL da candidata.
RECUSA = [
    ("PAGINA_DE_SERVICO", r"accessibilit|dichiarazione di access|obiettivi di access|privacy|cookie|note legali|"
                          r"amministrazione trasparente|whistleblow|avviso per iscrizione|bandi di concorso"),
    ("REDE_SOCIAL_OU_APP", r"whatsapp|spotify|facebook\.com|instagram\.com|twitter\.com|//x\.com|tiktok|t\.me/|"
                           r"linkedin\.com|apps\.apple|play\.google"),
    ("TURISMO", r"\ba trip to\b|\ba journey through\b|calabria straordinaria|turismo|visit ?italy|itinerar"),
    ("ORGAO_LEGISLATIVO_OU_GERAL", r"parlamento europeo|europarl|senato\.it|camera\.it|governo\.it/?$"),
]


def dominio(u: str) -> str:
    h = urlparse(u or "").netloc.lower().removeprefix("www.")
    return h


def norm(u: str) -> str:
    return (u or "").strip().lower().replace("://www.", "://").rstrip("/")


def motivo(e: str) -> str:
    e = re.sub(r"\(.*?\)\)?", "(...)", e or "", count=1)
    e = re.sub(r"https?://\S+", "URL", e)
    e = re.sub(r"\d+", "N", e)
    return e[:120]


# Motivo -> o que destrava, quem, se precisa de rede
ACAO = [
    (r"territorio indeterminado", "DECISAO_SEMANTICA", "dono/Opus pelo canal DECISOES-SEMANTICAS-V1 (prova multipla)", True),
    (r"territorio decidido fora de IT", "DECISAO_DO_DONO", "dono: numeracao fora de IT (o QUALIFY so cunha IT-)", False),
    (r"YouTube exige channel_id", "CAPACIDADE_DE_OUTRO_DONO", "Scrap (YT-METADADOS / canal por channel_id)", True),
    (r"Disallow no robots", "POLITICA_ROBOTS", "nenhum atalho (D39): so outra entrada permitida pelo robots", True),
    (r"robots nao pode ser lido", "REDE_OU_VPN", "coordenador: confirmar portao IT e re-enfileirar", True),
    (r"URLError|cancelamento de uma conex", "REDE_OU_VPN", "coordenador: confirmar portao IT e re-enfileirar", True),
    (r"UnicodeEncodeError", "CODIGO", "conserto de codigo (URL com acento)", False),
    (r"sem contrato nesta arvore", "CODIGO_OU_LIVRO", "contrato por fazer / livro partilhado", False),
    (r"HTTP N|documento inacessivel|nao a esta identidade|destino URL", "FONTE_RESPONDE_MAL",
     "remedir com rede; muitas vezes fonte mudou de endereco", True),
    (r"exige capacidade nova", "CAPACIDADE_DE_OUTRO_DONO", "Scrap engineer", True),
]


# Leitura humana (25/09) das 21 MESMO_SITE_CLASSE_UNICA: nem toda a página do mesmo site é fonte nova.
MAO_MESMO_SITE = {
    "CAND-0270": "HERDA_PLAUSIVEL",   # ISTAT archivio agricoltura: secção própria de estatística agrícola
    "CAND-0570": "DUPLICADA_DA_ORGANIZACAO",  # arquivo da mesma revista que IT-T10-040
    "CAND-0700": "NAO_E_FONTE",       # Abbonati / Rinnova (assinaturas)
    "CAND-0721": "NAO_E_FONTE",       # livraria
    "CAND-0720": "DUPLICADA_DA_ORGANIZACAO",  # casa da Tecniche Nuove (IT-T8-033)
    "CAND-0718": "NAO_E_FONTE",       # loja
    "CAND-0858": "HERDA_PLAUSIVEL",   # SNPA linee guida
    "CAND-0942": "DUPLICADA_DA_ORGANIZACAO",  # casa da ARSARP (IT-T2-149)
    "CAND-0944": "HERDA_PLAUSIVEL",   # ARSARP pubblicazioni (vivai forestali): classe a confirmar
    "CAND-0993": "HERDA_PLAUSIVEL",   # Acta Italus Hortus (atas científicas da SOI)
    "CAND-1023": "DUPLICADA_DA_ORGANIZACAO",  # casa do DSA3 (IT-T8-061)
    "CAND-1025": "DUPLICADA_DA_ORGANIZACAO",  # casa da Agraria Sassari (IT-T8-062)
    "CAND-1027": "HERDA_PLAUSIVEL",   # eventos da Agraria Sassari
    "CAND-1039": "HERDA_PLAUSIVEL",   # ISPRA biodiversità
    "CAND-1040": "HERDA_PLAUSIVEL",   # ISPRA suolo
    "CAND-1041": "HERDA_PLAUSIVEL",   # ISPRA pubblicazioni
    "CAND-1047": "DUPLICADA_DA_ORGANIZACAO",  # casa da SIDEA (IT-T8-065)
    "CAND-1050": "DUPLICADA_DA_ORGANIZACAO",  # casa da SOI (IT-T8-064/066)
    "CAND-1052": "DUPLICADA_DA_ORGANIZACAO",  # casa da Entomologica (IT-T8-067)
    "CAND-1053": "HERDA_PLAUSIVEL",   # eventos da Entomologica
    "CAND-1060": "DUPLICADA_DA_ORGANIZACAO",  # casa da Olivonews (IT-T1-022)
}
# Revisão semântica anterior (DECISOES-SEMANTICAS-V1, Opus/humano) -> proposta
SEMANTICA = {"NAO_E_FONTE": "PROPOR_RECUSA", "FORA_DO_AGRO_APARENTE": "PROPOR_RECUSA", "SEMENTE_ERRADA": "PROPOR_RECUSA",
             "IDENTIDADE_TROCADA": "CORRIGIR_URL", "IDENTIDADE_DUPLICADA_POSSIVEL": "DUPLICADA_DE",
             "PAGINA_DE_OUTRA_FONTE": "DUPLICADA_DE"}
COLDIRETTI = r"coldiretti\.it|anga\.it|unaprol\.it"


def acao(m: str):
    for rx, classe, quem, rede in ACAO:
        if re.search(rx, m):
            return classe, quem, rede
    return "NAO_SEI", "ler a tarefa", None


def main():
    q = json.loads((VIVO / "curadoria" / "LIFECYCLE-QUEUE-V1.json").read_text(encoding="utf-8"))["TAREFAS"]
    cand = {c["CANDIDATA_ID"]: c for c in json.loads(
        (VIVO / "candidatas" / "FONTES-CANDIDATAS.json").read_text(encoding="utf-8"))["CANDIDATAS"]}
    contratos = json.loads((VIVO / "curadoria" / "italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]
    estado = {}
    for t in json.loads((VIVO / "curadoria" / "LIFECYCLE-LEDGER-V1.json").read_text(encoding="utf-8"))["TRANSICOES"]:
        estado[t["SOURCE_ID"]] = t["NEW_STATE"]
    dec = {x["CANDIDATA_ID"]: x for x in json.loads(
        (VIVO / "curadoria" / "DECISOES-SEMANTICAS-V1.json").read_text(encoding="utf-8"))["DECISOES"]}
    dono_do_dominio, dono_do_url = defaultdict(set), defaultdict(set)
    for c in contratos:
        for u in (c.get("CANONICAL_ENTRY_URL"), (c.get("ACQUISITION") or {}).get("INDEX_URL")):
            if u:
                dono_do_dominio[dominio(u)].add(c["SOURCE_ID"])
                dono_do_url[norm(u)].add(c["SOURCE_ID"])
    por_sid = {c["SOURCE_ID"]: c for c in contratos}

    linhas = []
    for t in q:
        if t["STATUS"] not in ("BLOCKED", "FAILED"):
            continue
        sid = t["SOURCE_ID"]
        ficha = cand.get(sid, {})
        url = ficha.get("URL") or (por_sid.get(sid, {}).get("CANONICAL_ENTRY_URL"))
        nome = ficha.get("NOME") or por_sid.get(sid, {}).get("NAME")
        m = motivo(t.get("LAST_ERROR"))
        classe, quem, rede = acao(m)
        dom = dominio(url)
        l = {"TASK_ID": t["TASK_ID"], "STATUS": t["STATUS"], "TASK_TYPE": t["TASK_TYPE"], "ID": sid,
             "CLASSE_T": (re.match(r"IT-(T\d+)-", sid) or [None, None])[1], "NOME": nome, "URL": url,
             "DOMINIO": dom, "MOTIVO": m, "ACAO": classe, "QUEM_DESTRAVA": quem, "PRECISA_REDE": rede,
             "ERRO": (t.get("LAST_ERROR") or "")[:240], "ESTADO_NO_LEDGER": estado.get(sid)}
        if sid.startswith("CAND-"):
            l.update({"TIPO": ficha.get("TIPO"), "PAIS": ficha.get("PAIS"), "ESTADO_DA_FICHA": ficha.get("ESTADO"),
                      "MOTIVO_DA_RECUSA_JA_ANOTADO": ficha.get("MOTIVO_DA_RECUSA"),
                      "DECISAO_SEMANTICA": (dec.get(sid) or {}).get("CATEGORIA") or (dec.get(sid) or {}).get("TERRITORIO")})
            alvo = ("%s %s" % (nome or "", url or "")).lower()
            regra = next((n for n, rx in RECUSA if re.search(rx, alvo)), None)
            gemeas = sorted(dono_do_url.get(norm(url), set())) if url else []
            donos = sorted(dono_do_dominio.get(dom, set())) if dom else []
            classes = sorted({re.match(r"IT-(T\d+)-", s).group(1) for s in donos if re.match(r"IT-(T\d+)-", s)})
            if dom.endswith("youtube.com"):
                l["PROPOSTA"], l["PORQUE"] = "YOUTUBE_CAPACIDADE", ("canal: rota do Scrap (channel_id) e D21 "
                                                                   "(herda do site so com ligacao oficial)")
            elif regra:
                l["PROPOSTA"], l["PORQUE"] = "PROPOR_RECUSA", "regra %s casa no nome/URL" % regra
            elif SEMANTICA.get(l["DECISAO_SEMANTICA"]):
                l["PROPOSTA"] = SEMANTICA[l["DECISAO_SEMANTICA"]]
                l["PORQUE"] = "revisao semantica anterior: %s" % l["DECISAO_SEMANTICA"]
            elif ficha.get("MOTIVO_DA_RECUSA"):
                l["PROPOSTA"], l["PORQUE"] = "PROPOR_RECUSA", "ficha ja anota %s" % ficha["MOTIVO_DA_RECUSA"]
            elif gemeas:
                l["PROPOSTA"], l["PORQUE"] = "DUPLICADA_DE", "o mesmo endereco ja e de %s" % ", ".join(gemeas)
            elif donos and len(classes) == 1:
                l["PROPOSTA"], l["PORQUE"] = "MESMO_SITE_CLASSE_UNICA", (
                    "o site %s ja tem %d fonte(s), todas %s (%s): heranca do mesmo site, por decisao do dono"
                    % (dom, len(donos), classes[0], ", ".join(donos[:4])))
                l["CLASSE_PROPOSTA"] = classes[0]
                l["LEITURA_A_MAO"] = MAO_MESMO_SITE.get(sid, "NAO_LIDA")
            elif donos:
                l["PROPOSTA"], l["PORQUE"] = "MESMO_SITE_CLASSES_MISTAS", (
                    "o site %s ja tem fontes em %s: a classe nao se herda" % (dom, "/".join(classes) or "sem classe"))
            elif classe == "DECISAO_SEMANTICA":
                l["PROPOSTA"], l["PORQUE"] = "PRECISA_DECISAO", "territorio pelo canal semantico (prova de rede)"
            else:
                l["PROPOSTA"], l["PORQUE"] = classe, quem
        else:
            l["PROPOSTA"], l["PORQUE"] = classe, quem
            if classe == "REDE_OU_VPN" and re.search(COLDIRETTI, dom or ""):
                l["PROPOSTA"] = "REDE_COLDIRETTI_RECUSA_A_SAIDA"
                l["PORQUE"] = ("WinError 10054: o site fecha a ligacao da saida VPN (visto antes: 403 -> 000 na "
                               "saida Proton); precisa de outra saida IT, nao de codigo")
            if "UnicodeEncodeError" in l["ERRO"]:
                l["PROPOSTA"], l["PORQUE"] = "CODIGO_CONSERTADO_NESTE_RAMO", "canario.url_segura (link com acento)"
        linhas.append(l)

    # taxa historica: das fontes com contrato, quantas estao READY
    com_contrato = [s for s in por_sid if estado.get(s)]
    ready = sum(1 for s in com_contrato if estado.get(s) == "READY_FOR_COLLECTION")
    out = {"DATASET": "BLOQUEADAS-268-V1", "VIVO": str(VIVO), "N": len(linhas),
           "POR_STATUS": dict(Counter(l["STATUS"] for l in linhas)),
           "POR_ACAO": dict(Counter(l["ACAO"] for l in linhas).most_common()),
           "POR_PROPOSTA": dict(Counter(l["PROPOSTA"] for l in linhas).most_common()),
           "POR_MOTIVO": dict(Counter(l["MOTIVO"] for l in linhas).most_common()),
           "POR_CLASSE_T": dict(Counter(l["CLASSE_T"] or "CAND (sem classe)" for l in linhas).most_common()),
           "POR_DOMINIO_TOP": dict(Counter(l["DOMINIO"] for l in linhas).most_common(25)),
           "TAXA_HISTORICA_READY": {"READY": ready, "COM_CONTRATO_NO_LEDGER": len(com_contrato),
                                    "TAXA": round(ready / len(com_contrato), 3) if com_contrato else None},
           "LINHAS": linhas}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for k in ("N", "POR_STATUS", "POR_ACAO", "POR_PROPOSTA", "POR_CLASSE_T", "TAXA_HISTORICA_READY"):
        print(k, out[k])
    print("DOMINIOS", list(out["POR_DOMINIO_TOP"].items())[:15])


if __name__ == "__main__":
    main()
