#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O ESQUELETO DE «INTELLIGENCE SCIENTIFICA» — pesquisador, instituicao, tema do casco, estudos.

    MISSAO   nuvem-int-casco-ponte-v1 (ordem da coordenacao 26/09 17:35)
    ESPECIE  PRE-VISUALIZACAO LOCAL de material FORA da Sala. NAO E INTELLIGENCE.
    ESTADO   IMPLEMENTED · sem rede · le ficheiros ja gravados.

    python3 pacote/esqueleto_scientifica.py <CRUZAMENTO-MUR.json> <UNIDADES-T6.json> \
            [<PRE-MEDICAO-CAP-SCI.json>] <saida.json|saida.html>
    python3 -m unittest tests.test_esqueleto_scientifica -v

A PERGUNTA, E MAIS NENHUMA
--------------------------
    PARA CADA TEMA DO CASCO, QUE PESQUISADORES (IDENTIDADE DO MUR) PUBLICARAM
    QUE ESTUDOS — E O QUE CADA ESTUDO DIZ E NAO DIZ?

PORQUE NAO E INTELLIGENCE, E NAO PASSA PELA PONTE
-------------------------------------------------
INT-LAW-010: a Intelligence comeca na Sala de Espera. Estes trabalhos NAO estao
na Sala (a pre-medicao T6 mediu: nenhum DOI nos 94 itens). Por isso nao ha
INTELLIGENCE_RUN, nao ha LINEAGE com G0, e a ponte recusaria cada cartao. O
esqueleto e so a FORMA que a ferramenta tera — com dado de identidade e de
publicacao que ja existe, marcado PRE_SALA.

O QUE ELE NUNCA FAZ
-------------------
    NAO deduz tema pela cultura so: tema = par que esta NA CONSULTA E NO TEXTO.
    NAO liga pessoa a estudo por nome: so pelo OPENALEX_ID que a lista mestra provou.
    NAO liga os SO_NOME (homonimo ou mudanca de universidade: fica fora, dito).
    NAO funde os VARIOS_IDS (ficam os dois ids, como a lista mestra decidiu).
    NAO calcula independencia (INT-LAW-280): mostra a da pre-medicao, com a sua base.
    NAO usa a data de publicacao como data do estudo.
    NAO converte afiliacao em local do estudo (INT-LAW-102).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

# A marca, o NAO SEI, o CSS e a regra do destino sao os da ponte: UMA definicao.
from ponte_intelligence_casco import (                          # noqa: E402
    MARCA, NAO_SEI, CSS_ADAMA, _CSS_PAGINA, destino_permitido, e_ignorancia,
)

CONTRATO = "ESQUELETO_INTELLIGENCE_SCIENTIFICA/v1"
NATUREZA = ("PRE_SALA — material FORA da Sala de Espera; NAO e INTELLIGENCE_RUN "
            "(INT-LAW-010); nada aqui e sinal, achado ou forca de evidencia")
LIGADOS = ("MUR_E_OBRAS", "VARIOS_IDS")


class LeiViolada(Exception):
    """O esqueleto recusou-se, e diz porque."""


def _v(x):
    return NAO_SEI if e_ignorancia(x) else x


def _valores(campo):
    """Lista de VALOR de um campo que vem como [{VALOR..}] ou NAO SEI."""
    if isinstance(campo, list):
        return [c.get("VALOR") for c in campo if isinstance(c, dict) and not e_ignorancia(c.get("VALOR"))]
    return []


def _estudo(u: dict, mesma_obra: dict, ids_mur: dict) -> dict:
    doi = _v(u.get("DOI"))
    return {
        "DOI": doi,
        "OPENALEX_WORK_ID": _v(u.get("OPENALEX_WORK_ID")),
        "TITULO": _v(u.get("TITULO")),
        "TIPO": _v(u.get("TIPO")),
        # A data de PUBLICACAO. A do estudo e outra pergunta, e vem a parte.
        "PUBLICADO_EM": _v(u.get("PUBLICADO_EM")),
        "PERIODO_DO_ESTUDO": _valores(u.get("PERIODO_DO_ESTUDO")) or NAO_SEI,
        "LOCAL_DO_ESTUDO_ESCRITO": _valores(u.get("LOCAL_DO_ESTUDO_ESCRITO")) or NAO_SEI,
        "MOLECULA": _valores(u.get("MOLECULA")) or NAO_SEI,
        "MOLECULA_LEXICO": _v(u.get("MOLECULA_LEXICO")),
        "TRIAL_ID": _v(u.get("TRIAL_ID")),
        "TEMAS": sorted(u.get("NA_CONSULTA_E_NO_TEXTO") or []),
        "PROVAVEL_MESMA_OBRA_QUE": mesma_obra.get(doi, []),
        "AUTORES": [{
            "NOME_NO_INDICE": _v(a.get("NOME")),
            "OPENALEX_ID": _v(a.get("OPENALEX_ID")),
            "PROVA_DA_PESSOA": _v(a.get("PROVA_DA_PESSOA")),
            "MUR": ids_mur.get(a.get("OPENALEX_ID"), NAO_SEI),
        } for a in (u.get("AUTORES") or []) if isinstance(a, dict)],
    }


def montar(cruzamento: dict, unidades: dict, pre_medicao: dict | None = None,
           origens: dict | None = None) -> dict:
    lista = cruzamento.get("LISTA")
    obras = unidades.get("UNIDADES")
    if not isinstance(lista, list) or not isinstance(obras, list):
        raise LeiViolada("faltam LISTA (MUR) ou UNIDADES (T6)")

    ligados = [p for p in lista if isinstance(p, dict) and p.get("ESTADO") in LIGADOS]
    ids_mur = {}
    for p in ligados:
        for i in p.get("OPENALEX_IDS") or []:
            ids_mur[i] = p["MUR_NOME"]

    mesma_obra = {}
    for g in unidades.get("GRUPOS") or []:
        dois = [d for d in (g.get("DOIS") or []) if not e_ignorancia(d)]
        for d in dois:
            mesma_obra[d] = sorted(x for x in dois if x != d)

    temas = {}
    sem_tema = 0
    for u in obras:
        if not isinstance(u, dict):
            continue
        pares = u.get("NA_CONSULTA_E_NO_TEXTO") or []
        if not pares:
            sem_tema += 1
        for t in pares:
            temas.setdefault(t, []).append(u)

    saida_temas = {}
    for t in sorted(temas):
        us = temas[t]
        pessoas = []
        for p in ligados:
            ids = set(p.get("OPENALEX_IDS") or [])
            seus = [u for u in us if ids & {a.get("OPENALEX_ID") for a in (u.get("AUTORES") or [])
                                             if isinstance(a, dict)}]
            if not seus:
                continue
            pessoas.append({
                "MUR_NOME": p["MUR_NOME"], "FASCIA": _v(p.get("FASCIA")),
                "ATENEO": _v(p.get("ATENEO")), "STRUTTURA": _v(p.get("STRUTTURA")),
                "SSD_2024": _v(p.get("SSD_2024")), "SSD_2015": _v(p.get("SSD_2015")),
                "ESTADO_NA_LISTA_MESTRA": p["ESTADO"],
                "OPENALEX_IDS": sorted(ids), "ORCID": p.get("ORCID") or NAO_SEI,
                "PROVA_DA_PESSOA": p.get("PROVA") or NAO_SEI,
                "IRIS": _v(p.get("IRIS")), "IRIS_ESTADO": _v(p.get("IRIS_ESTADO")),
                "ESTUDOS_NESTE_TEMA": sorted(_v(u.get("DOI")) for u in seus),
            })
        pm = ((pre_medicao or {}).get("REPLICACAO_POR_CULTURA_X_PROBLEMA") or {}).get(t)
        saida_temas[t] = {
            "MARCA": MARCA, "NAO_PARA_CLIENTE": True, "TEMA": t,
            "ESTUDOS": [_estudo(u, mesma_obra, ids_mur) for u in
                        sorted(us, key=lambda x: str(x.get("PUBLICADO_EM")), reverse=True)],
            "PESQUISADORES_MUR": sorted(pessoas, key=lambda x: x["MUR_NOME"]),
            # INT-LAW-280: a ferramenta nao infere independencia. Mostra-se a
            # medida que existe, com a base dela — que NAO e a das obras acima.
            "INDEPENDENCIA_DA_PRE_MEDICAO": (dict(pm, BASE=(origens or {}).get("PRE_MEDICAO_BASE", NAO_SEI))
                                            if pm else NAO_SEI),
            "UNIVERSO": {"ESTUDOS": len(us),
                         "LEITURA": "estudos DESTA foto da consulta T6; zero nao prova ausencia"},
        }

    fora = [{"MUR_NOME": p["MUR_NOME"], "ATENEO": _v(p.get("ATENEO")),
             "PORQUE": "SO_NOME: o nome bate, a universidade do MUR nao aparece nas obras — "
                       "pode ser mudanca de universidade ou homonimo; nao se liga",
             "CANDIDATOS": p.get("SO_NOME_COM") or []}
            for p in lista if isinstance(p, dict) and p.get("ESTADO") == "SO_NOME"]
    esq = {
        "SCHEMA": CONTRATO, "MARCA": MARCA, "NAO_PARA_CLIENTE": True, "NATUREZA": NATUREZA,
        "FERRAMENTA": "science", "NOME_IT": "Intelligence Scientifica",
        "ORIGENS": origens or NAO_SEI,
        "MUR": {"DOCENTES": len(lista), "LIGADOS_A_OBRAS": len(ligados),
                "ESTADOS": cruzamento.get("ESTADOS", NAO_SEI)},
        "TEMAS": saida_temas,
        "OBRAS_SEM_TEMA_DO_CASCO_NO_TEXTO": sem_tema,
        "FORA_POR_SO_NOME": fora,
        "O_QUE_FALTA": (pre_medicao or {}).get("DATA_DEMAND", NAO_SEI),
    }
    v = conferir_esqueleto(esq)
    if v:
        raise LeiViolada("esqueleto reprovado: " + "; ".join(v[:5]))
    return esq


def conferir_esqueleto(esq: dict) -> list:
    """O portao de saida. Vazia = passa."""
    v = []
    if esq.get("MARCA") != MARCA or esq.get("NAO_PARA_CLIENTE") is not True:
        v.append("esqueleto sem a marca")
    if "PRE_SALA" not in str(esq.get("NATUREZA")):
        v.append("esqueleto sem a natureza PRE_SALA")
    for t, e in (esq.get("TEMAS") or {}).items():
        if e.get("MARCA") != MARCA or e.get("NAO_PARA_CLIENTE") is not True:
            v.append(f"{t}: tema sem a marca")
        for s in e.get("ESTUDOS") or []:
            if t not in (s.get("TEMAS") or []):
                v.append(f"{t}/{s.get('DOI')}: estudo sem o tema no texto")
            for k in ("DOI", "TITULO", "PUBLICADO_EM", "PERIODO_DO_ESTUDO", "LOCAL_DO_ESTUDO_ESCRITO"):
                if e_ignorancia(s.get(k)) and s.get(k) != NAO_SEI:
                    v.append(f"{t}/{s.get('DOI')}: {k} esconde a ignorancia")
        for p in e.get("PESQUISADORES_MUR") or []:
            if p.get("ESTADO_NA_LISTA_MESTRA") not in LIGADOS:
                v.append(f"{t}/{p.get('MUR_NOME')}: pessoa nao ligada na lista mestra")
            if not p.get("ESTUDOS_NESTE_TEMA"):
                v.append(f"{t}/{p.get('MUR_NOME')}: pessoa sem estudo no tema")
    return v


def como_html(esq: dict, css_href: str | None = None) -> str:
    """Pagina LOCAL. RENDER e EXPLAIN; faixa fixa; todo texto escapado."""
    from html import escape as E
    href = css_href or CSS_ADAMA.resolve().as_uri()

    def val(x):
        s = x if isinstance(x, str) else ", ".join(map(str, x)) if isinstance(x, list) else json.dumps(x, ensure_ascii=False)
        return f'<span class="naosei">{E(s)}</span>' if s == NAO_SEI or s == "" else E(s)

    p = ["<!doctype html><html lang=\"it\"><head><meta charset=\"utf-8\">",
         f"<title>{E(MARCA)} · Intelligence Scientifica (esqueleto)</title>",
         f'<link rel="stylesheet" href="{E(href)}"><style>{_CSS_PAGINA}</style></head><body>',
         f'<div class="faixa" data-marca="1">{E(MARCA)} — PRE_SALA, non è Intelligence · anteprima locale, non pubblicata</div>',
         "<main><h1>Intelligence Scientifica — esqueleto</h1>",
         f"<p>{E(esq['NATUREZA'])}</p>",
         f"<p>MUR: {esq['MUR']['DOCENTES']} docenti · {esq['MUR']['LIGADOS_A_OBRAS']} ligati a opere · "
         f"opere senza tema del casco nel testo: {esq['OBRAS_SEM_TEMA_DO_CASCO_NO_TEXTO']}</p>"]
    for t, e in esq["TEMAS"].items():
        pm = e["INDEPENDENCIA_DA_PRE_MEDICAO"]
        ind = (f"gruppi di autoria (tetto) {E(str(pm.get('GRUPOS_DE_AUTORIA_LIMITE_SUPERIOR_DE_INDEPENDENCIA')))} "
               f"su {E(str(pm.get('OBRAS')))} opere — base: {val(pm.get('BASE'))}" if isinstance(pm, dict) else val(pm))
        p.append(f'<section class="ferramenta" id="{E(t)}"><h2>{E(t)} <span class="marca">{E(MARCA)}</span></h2>'
                 f'<div class="estado">{e["UNIVERSO"]["ESTUDOS"]} studi — {E(e["UNIVERSO"]["LEITURA"])} · '
                 f'indipendenza: {ind}</div><h3>Ricercatori (MUR)</h3><table>'
                 "<tr><th>nome</th><th>fascia</th><th>ateneo · struttura</th><th>SSD</th><th>ORCID · prova</th><th>studi qui</th></tr>")
        for q in e["PESQUISADORES_MUR"]:
            p.append(f"<tr><td>{E(q['MUR_NOME'])}{' · VARIOS_IDS' if q['ESTADO_NA_LISTA_MESTRA'] == 'VARIOS_IDS' else ''}</td>"
                     f"<td>{val(q['FASCIA'])}</td><td>{val(q['ATENEO'])} · {val(q['STRUTTURA'])}</td>"
                     f"<td>{val(q['SSD_2024'])}</td><td>{val(q['ORCID'])} · {val(q['PROVA_DA_PESSOA'])}</td>"
                     f"<td>{len(q['ESTUDOS_NESTE_TEMA'])}</td></tr>")
        p.append("</table><h3>Studi</h3><table><tr><th>DOI · tipo</th><th>titolo</th><th>pubblicato</th>"
                 "<th>periodo dello studio</th><th>luogo scritto</th><th>molecola</th><th>autori (MUR se ligato)</th></tr>")
        for s in e["ESTUDOS"]:
            aut = "; ".join(E(a["NOME_NO_INDICE"]) + (f" <b>[{E(a['MUR'])}]</b>" if a["MUR"] != NAO_SEI else "")
                            for a in s["AUTORES"])
            dup = (" · <i>probabile stessa opera di " + E(", ".join(s["PROVAVEL_MESMA_OBRA_QUE"])) + "</i>"
                   if s["PROVAVEL_MESMA_OBRA_QUE"] else "")
            p.append(f"<tr><td>{val(s['DOI'])} · {val(s['TIPO'])}{dup}</td><td>{val(s['TITULO'])}</td>"
                     f"<td>{val(s['PUBLICADO_EM'])}</td><td>{val(s['PERIODO_DO_ESTUDO'])}</td>"
                     f"<td>{val(s['LOCAL_DO_ESTUDO_ESCRITO'])}</td><td>{val(s['MOLECULA'])}</td><td>{aut}</td></tr>")
        p.append("</table></section>")
    p.append("<h2>Fuori (SO_NOME)</h2><ul>")
    for f in esq["FORA_POR_SO_NOME"]:
        p.append(f"<li>{E(f['MUR_NOME'])} ({val(f['ATENEO'])}): {E(f['PORQUE'])}</li>")
    p.append("</ul></main></body></html>\n")
    return "".join(p)


def main(argv=None) -> int:
    import hashlib
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) not in (3, 4):
        print(__doc__.strip().split("\n\n")[0])
        return 2
    destino = Path(argv[-1])
    if not destino_permitido(destino):
        print("RECUSADO: o destino fica dentro de italia-portale/ — isto e NAO_PARA_CLIENTE e nao e deploy.")
        return 3
    fontes = [Path(a) for a in argv[:-1]]
    dados = [json.loads(f.read_text(encoding="utf-8")) for f in fontes]
    origens = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in fontes}
    pm = dados[2] if len(dados) == 3 else None
    if pm:
        n = ((pm.get("CHAVES_CAP_SCI") or {}).get("UNIDADES"))
        origens["PRE_MEDICAO_BASE"] = (f"pre-medicao sobre {n} unidades (UNIDADES-T6 sha256 "
                                       f"{(pm.get('ENTRADA') or {}).get('SHA256', NAO_SEI)[:16]}), "
                                       f"NAO a foto de {len(dados[1].get('UNIDADES') or [])} obras acima")
    esq = montar(dados[0], dados[1], pm, origens)
    destino.write_text(como_html(esq) if destino.suffix == ".html"
                       else json.dumps(esq, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n_est = sum(e["UNIVERSO"]["ESTUDOS"] for e in esq["TEMAS"].values())
    n_pes = len({q["MUR_NOME"] for e in esq["TEMAS"].values() for q in e["PESQUISADORES_MUR"]})
    print(f"{MARCA} · PRE_SALA · {len(esq['TEMAS'])} temas · {n_est} estudos-no-tema · {n_pes} pesquisadores MUR -> {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
