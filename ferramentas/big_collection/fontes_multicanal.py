# -*- coding: utf-8 -*-
"""AS CANDIDATAS DE CADA LINHA — a alimentacao, opcao (a) (RELIGA-MULTICANAL, D155, 29/09/2026).

    from fontes_multicanal import candidatas_por_linha
    cands = candidatas_por_linha(Path("CURATOR-FONTES-CANARIO-MULTICANAL.json"))
    cands["YOUTUBE"]  ->  [{"SOURCE_ID", "LINHA", "DOMINIO", "DOMINIOS", "PREVISTOS", "ALVO": {...}}, ...]

O BURACO QUE ISTO FECHA (medido, e e o buraco verdadeiro desta campanha):

    ferramentas/big_collection/coleta_continua.py:666-667
        cands = {l["LINHA"]: [] for l in LINHAS}
        cands["SITES"] = candidatas_do_plano(plano)

De todas as linhas, SO a SITES recebia candidatas. As outras nasciam com a lista vazia e nunca eram
alimentadas: `LINHAS` tinha 5 entradas e o alimentador conhecia uma. Nenhuma delas correu por isso — e
NAO por causa do contador de 24 h, que e onde o diagnostico anterior tinha parado.

    O COLETOR NAO SABIA ALIMENTAR AS LINHAS NAO-WEB. ERA ARQUITECTURA DO CICLO, NAO CONTADOR.

A OPCAO (a), que e a que o coordenador escolheu: cada linha recebe as candidatas da saida do SEU PROPRIO
transporte/lista, com o campo LINHA. Sem fila-mestra nova, sem scheduler novo, sem segunda coorte.

QUEM ESCOLHE AS FONTES NAO E ESTE FICHEIRO. E o Source Curator, e ele entrega-as num so sitio
(`CURATOR-FONTES-CANARIO-MULTICANAL.json`). Aqui so se LE e se traduz para a lingua do agendador.

    ⚠️ AS LISTAS `*_FORA` E `DIVERGENCIAS_*` DO CURADOR NAO SAO ALIMENTACAO — SAO O QUE ELE EXCLUIU.
    Ler uma delas por engano poria no ar uma fonte que o curador recusou com motivo escrito. Este
    ficheiro le, por nome, SO as listas do canario, e ignora tudo o resto do documento.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "coleta"))

# SO estas. O que nao estiver aqui nao alimenta linha nenhuma.
LISTAS_DO_CANARIO = {
    "YOUTUBE": ["YOUTUBE"],
    "INSTAGRAM": ["INSTAGRAM"],
    "LINKEDIN": ["LINKEDIN"],            # as PESSOAS sao opcionais e entram so se pedidas (ver `com_pessoas`)
    "SITES": ["WEB"],
    "BUSCA": ["BUSCA"],
    "CIENCIA": ["CIENCIA"],
}
LISTAS_EXCLUIDAS = ("YOUTUBE_FORA", "CIENCIA_FORA", "DIVERGENCIAS_FORA_DO_CANARIO")

# Quantos pedidos cada alvo custa ao orcamento do dominio. Medido, nao arredondado para cima «por
# seguranca»: um numero inflacionado aqui tranca fontes que cabiam.
PREVISTOS = {
    "YOUTUBE": 1,        # 1 pedido: a pagina publica do canal (os videos sao alvos, nao pedidos desta fase)
    "INSTAGRAM": 1,      # 1 pedido: a pagina /embed/ da conta (cada Reel conta a parte, ao ser colhido)
    "LINKEDIN": 1,       # 1 pedido: a pagina publica da organizacao
    "SITES": 3,          # robots + indice + 1..3 materias (~2,4 medidos nas ondas; 3 e o arredondado medido)
    "BUSCA": 2,          # a pagina de busca + a pagina do resultado (D93: uma pagina por resultado)
    "CIENCIA": 1,        # 1 chamada a API por consulta
}


def _dominio_de(url: str) -> str:
    import dominio_registavel as DR                                # noqa: PLC0415
    h = urllib.parse.urlsplit(str(url or "")).hostname or ""
    return DR.dominio_registavel(h)


def _ler(f: Path) -> dict:
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    if not isinstance(d, dict):
        raise ValueError("A lista do Curator nao e um objecto: %s" % f)
    return d


def candidatas_por_linha(ficheiro: Path, *, com_pessoas: bool = False, so_linhas=None) -> dict:
    """LINHA -> [candidata]. Linha sem lista no documento fica com [] (e isso e um facto, nao um erro)."""
    d = _ler(ficheiro)
    out = {}
    for linha, chaves in LISTAS_DO_CANARIO.items():
        if so_linhas and linha not in so_linhas:
            continue
        itens = []
        for k in chaves:
            itens += [x for x in (d.get(k) or []) if isinstance(x, dict)]
        if linha == "LINKEDIN" and com_pessoas:
            # D24: as pessoas sao CANDIDATAS em POLICY_BLOCK sem SOURCE_ID. So entram se pedidas.
            itens += [x for x in (d.get("LINKEDIN_PESSOAS_OPCIONAIS") or []) if isinstance(x, dict)]
        out[linha] = [c for c in (_traduzir(linha, x, i) for i, x in enumerate(itens, 1)) if c]
    return out


def _traduzir(linha: str, x: dict, n: int) -> dict | None:
    """Um item do Curator na lingua do agendador. None = o item nao tem o minimo para ser um alvo."""
    p = PREVISTOS.get(linha, 1)
    if linha == "BUSCA":
        cid, consulta = x.get("CONSULTA_ID"), x.get("CONSULTA")
        if not consulta:
            return None
        # A BUSCA nao tem dominio proprio: o dominio e o do motor, e quem o sabe e `coleta/linha_busca.py`.
        # Declarar um aqui seria adivinhar de quem e o orcamento.
        return {"SOURCE_ID": cid or "BUSCA-%03d" % n, "LINHA": linha, "DOMINIO": None, "DOMINIOS": [],
                "PREVISTOS": p, "ALVO": {"CONSULTA": consulta, "UNIVERSO": x.get("UNIVERSO"),
                                         "PAR": x.get("PAR"), "JANELA": x.get("JANELA")},
                "PROVENIENCIA": {"ORIGEM": x.get("ORIGEM"), "DECISAO": x.get("DECISAO_QUE_AUTORIZA")}}
    if linha == "CIENCIA":
        sid = x.get("SOURCE_ID")
        if not sid or not x.get("CONSULTA_OPENALEX"):
            return None
        return {"SOURCE_ID": sid, "LINHA": linha, "DOMINIO": "openalex.org", "DOMINIOS": ["openalex.org"],
                "PREVISTOS": p, "ALVO": {"CONSULTA_OPENALEX": x["CONSULTA_OPENALEX"], "FILTRO": x.get("FILTRO"),
                                         "ALVO_ID": x.get("ALVO_ID")},
                "PROVENIENCIA": {"ORIGEM": x.get("ORIGEM"), "DECISAO": x.get("DECISAO_QUE_AUTORIZA")}}

    url = x.get("URL")
    if not url:
        return None
    dom = _dominio_de(url)
    base = {"SOURCE_ID": x.get("SOURCE_ID"), "LINHA": linha, "DOMINIO": dom, "DOMINIOS": [dom],
            "PREVISTOS": p, "NOME": x.get("NOME"), "URL": url,
            "PROVENIENCIA": {"ATLAS": x.get("ATLAS"), "ESTADO_NO_LIVRO": x.get("ESTADO_NO_LIVRO"),
                             "DECISAO": x.get("DECISAO_QUE_AUTORIZA"),
                             "LOCATION_SOURCE": x.get("LOCATION_SOURCE")}}

    # ⚠️ SOURCE_ID AUSENTE E UM FACTO DECLARADO, NUNCA UM SOURCE_ID INVENTADO.
    # As contas de dataset (COMPETITOR-PUBLIC-COMM: Syngenta, Bayer) nao estao no livro do Curator. Elas
    # podem ser colhidas — a identidade delas esta PROVADA pelo site oficial — mas chegam a Sala SEM fonte
    # registada ate a porta canonica lhes dar SOURCE_ID. Fabricar um aqui faria a Sala declarar uma
    # procedencia que nao existe, e ninguem depois saberia distinguir a inventada da real.
    sid = base["SOURCE_ID"]
    if not sid or "/" in str(sid) or "#" in str(sid):
        base["SOURCE_ID"] = sid                                    # fica como o Curator o escreveu, ou None
        base["SOURCE_STATUS"] = "NAO_REGISTRADA_PENDENTE_PORTA_CANONICA"
        base["PROVENIENCIA"]["IDENTIDADE"] = x.get("IDENTIDADE")
    else:
        base["SOURCE_STATUS"] = "REGISTRADA"

    if linha == "YOUTUBE":
        cid = x.get("NATIVE_ID")
        if not cid:
            return None                                            # sem CHANNEL_ID nao ha rota: nao se adivinha
        base["ALVO"] = {"CHANNEL_ID": cid, "URL_DO_CANAL": url}
    elif linha == "INSTAGRAM":
        base["ALVO"] = {"HANDLE": x.get("HANDLE"), "URL_DA_CONTA": url,
                        # Os Reels que o Curator JA provou existirem, com a ligacao conta->reel provada.
                        # Nao sao um palpite: cada um tem PROVA_DOS_REELS no documento dele.
                        "REELS_CONHECIDOS": [r for r in (x.get("REELS_JA_NO_REPOSITORIO") or [])
                                             if isinstance(r, str)],
                        "PROVA_DOS_REELS": x.get("PROVA_DOS_REELS"),
                        "LIGACAO_REEL_CONTA": x.get("LIGACAO_REEL_CONTA")}
        if x.get("EXCLUIDO"):
            base["ALVO"]["EXCLUIDO_PELO_CURATOR"] = x["EXCLUIDO"]
    elif linha == "LINKEDIN":
        base["ALVO"] = {"PAGINA": url, "SLUG": x.get("NATIVE_ID"),
                        "E_PESSOA": "/in/" in str(url)}
    else:                                                          # SITES
        base["ALVO"] = {"INDEX_URL": url}
    return base


def resumo(cands: dict) -> dict:
    return {l: len(v) for l, v in sorted(cands.items())}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    if "fontes" not in arg:
        print(__doc__)
        return 2
    c = candidatas_por_linha(Path(arg["fontes"]), com_pessoas="--com-pessoas" in argv)
    print(json.dumps({"RESUMO": resumo(c), "CANDIDATAS": c}, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
