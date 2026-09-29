# -*- coding: utf-8 -*-
"""A ONDA DE UMA LINHA NAO-WEB — YOUTUBE, INSTAGRAM, LINKEDIN, ate RAW e a Sala (RELIGA-MULTICANAL, D155).

    py ferramentas/big_collection/onda_linha.py --correr --linha=YOUTUBE --fontes=<candidatas.json>
          --saida=<pasta da onda> [--max-alvos=N] [--sem-sala]

PORQUE EXISTE: `onda_web.py` corre a COORTE CONGELADA pelo `micro_coleta`, e so sabe fontes que estao
nela. As linhas nao-web nao tem coorte — tem rota propria e alvos proprios. Faltava o EXECUTOR DE CICLO
delas, e era esse o buraco verdadeiro (nao o contador de 24 h).

    O AGENDADOR ESCOLHE; O TRANSPORTE CORTA; A PROVA CONFERE. Esta peca e so o transporte da linha.

O QUE ELA FAZ, E POR QUE ORDEM:
  1. DESCOBRE os alvos pela rota PROVADA da linha (`coleta/rotas_multicanal.py`);
  2. COLHE os bytes de cada alvo pela MESMA porta (`coleta/scrap_http.buscar_bytes`: robots vivo, portao
     de egresso, reserva no livro de 24 h antes do pedido e registo da resposta depois);
  3. PRESERVA pelo DONO DO RAW (`guarda/preservar_coleta.preservar`), numa corrida propria em
     `collection_run` — a mesma forma que `coleta/linha_busca_raw.py` ja usa;
  4. passa cada unidade pela ADMISSION NORMAL, com o RAW_OBSERVATION_ID REAL que o banco devolveu;
  5. poe os PRONTOS na Sala canonica (`sala_de_espera.pousar`), na mesma corrida que acabou de nascer.

    UMA UNIDADE QUE NAO TEM RAW NO BANCO NAO E POUSADA. Sem linhagem nao ha Sala: e por isso que o
    passo 3 vem antes do 4, e nao ao contrario.

ESCREVE `ONDA-WEB-ESTADO.json` com a MESMA FORMA que a onda web — nao por preguica, mas porque o
`coleta_continua._ondas()` le esse ficheiro para contar pedidos, RUN_IDs e o delta da Sala. Duas formas
para a mesma coisa obrigariam o ciclo a saber de que linha veio cada ficheiro, e e exactamente essa
adivinhacao que esta casa ja pagou uma vez.

O QUE ESTA PECA NAO FAZ: nao escolhe fontes (o Curator escolhe), nao julga relevancia (a Admission
julga), nao baixa bytes de video do LinkedIn (ver `URL_MP4_DESCOBERTA` em `rotas_multicanal`), e nao
toca em Apify — proibida nesta instalacao pela D155.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.parse
import uuid
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — as gavetas do processo no caminho (`orquestrador` e um MODULO, nao a pasta)
sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))

RULE_VERSION = "RELIGA-MULTICANAL/v1 (D155)"
VISTOS_F = "ALVOS-JA-COLHIDOS.ndjson"
#: Linhas cujas fontes podem legitimamente nao ter territorio (uma consulta de busca nao e de um
#: territorio; uma conta de dataset ainda nao tem ficha). Nas outras, a falta e defeito e PARA.
SEM_TERRITORIO_E_NORMAL = frozenset({"BUSCA", "CIENCIA", "INSTAGRAM"})
JANELA_VISTO_S = 24 * 3600
ESTADO_F = "ONDA-WEB-ESTADO.json"
RAW_F = "RAW-LINHA.jsonl"
LIVRO_F = "LIVRO-LINHA.jsonl"

# O ACTOR de cada linha: o ficheiro que REALMENTE fez o pedido. Nao um nome bonito — o caminho, para
# quem ler o `collection_run` daqui a um mes saber onde esta o codigo que produziu aquela linha.
ACTOR = {
    "YOUTUBE": "coleta/rotas_multicanal.py::youtube_videos_do_canal",
    "INSTAGRAM": "coleta/rotas_multicanal.py::instagram_reels_da_conta",
    "LINKEDIN": "coleta/rotas_multicanal.py::linkedin_posts_da_organizacao",
    "BUSCA": "coleta/linha_busca.py::buscar_consultas",
    "CIENCIA": "coleta/corpus_pesquisador.py::_get (OpenAlex works)",
}
PLATAFORMA = {"YOUTUBE": "YOUTUBE", "INSTAGRAM": "INSTAGRAM", "LINKEDIN": "LINKEDIN",
              "BUSCA": "HTTP direto", "CIENCIA": "HTTP direto"}


# ══════════════════════════════════════════════════════════════════════════════
# O QUE JA SE COLHEU — para nao se voltar a pedir
# ══════════════════════════════════════════════════════════════════════════════
# MEDIDO PELO LAB (29/09): 31 dos 45 RAW do canario (69%) eram o MESMO video ou post, regravado ate
# SEIS vezes. Nenhuma dessas gravacoes estava errada — cada captura e uma observacao, e apaga-las
# antes de preservar seria violar a D157. O que estava errado era voltar a PEDIR o mesmo alvo.
#
#     O DESPERDICIO NAO E O FICHEIRO A MAIS: E O PEDIDO A MAIS.
#     Ele gasta orcamento de 24 h que uma fonte nova nao vai ter.
#
# Este livro e append-only, por LINHA e por ALVO, com o RUN_ID que o colheu. Quem ja foi colhido
# dentro da janela nao e pedido outra vez: sai `VISTO_ANTES`, com a corrida anterior nomeada — que e
# informacao, e nao um silencio.
def ler_vistos(base: Path, janela_s: float = JANELA_VISTO_S, agora: float = None) -> dict:
    """(LINHA, URL) -> {RUN_ID, EM} do que foi colhido dentro da janela. Ausente = {}."""
    f = Path(base) / VISTOS_F
    if not f.exists():
        return {}
    t = time.time() if agora is None else agora
    fora = {}
    for l in f.read_text(encoding="utf-8", errors="replace").splitlines():
        if not l.strip():
            continue
        try:
            e = json.loads(l)
        except ValueError:
            continue                                               # uma linha estragada nao apaga o livro
        if float(e.get("EM") or 0) > t - janela_s:
            fora[(e.get("LINHA"), e.get("URL"))] = {"RUN_ID": e.get("RUN_ID"), "EM": e.get("EM")}
    return fora


def anotar_visto(base: Path, linha: str, url: str, run_id: str, agora: float = None) -> None:
    Path(base).mkdir(parents=True, exist_ok=True)
    with open(Path(base) / VISTOS_F, "a", encoding="utf-8") as f:
        f.write(json.dumps({"LINHA": linha, "URL": url, "RUN_ID": run_id,
                            "EM": time.time() if agora is None else agora}, ensure_ascii=False) + "\n")


def agora_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class TerritorioNaoDeclarado(ValueError):
    """Nao ha territorio para carimbar esta corrida, e nao se inventa um."""


SEM_TERRITORIO = "T0"          # nao e um territorio: e a ausencia declarada de um (T1..T13 sao os reais)


def run_id(source_id: str | None, territorio: str | None = None,
           aceitar_sem_territorio: bool = False) -> str:
    """O RUN_ID no formato que a PROVA-TETO le (`provas/prova_teto_dominio.RE_RUN_ID`):
    (IT|XX)-T<n>-AAAA-MM-DD-HHMMSS-<16 hex>. Um formato proprio ficaria invisivel para a prova.

    ⚠️ O TERRITORIO NAO SE INVENTA. Este codigo caia num T9 por omissao quando o SOURCE_ID nao o
    trazia — e T9 e COMPETITORS, um universo real com dono. Uma corrida de uma fonte sem territorio
    ficava carimbada como sendo de concorrentes, e a partir dai ninguem conseguia distinguir a que
    foi mesmo de T9 da que so nao tinha territorio nenhum.

        UM CARIMBO POR OMISSAO NAO E UM CARIMBO DESCONHECIDO: E UM CARIMBO ERRADO,
        E ELE VIAJA COM A OBSERVACAO PARA SEMPRE.

    Sem territorio declarado nem legivel no SOURCE_ID, levanta `TerritorioNaoDeclarado`. Quem chama
    decide o que fazer com a fonte — o que NAO se faz e escolher um territorio por ela."""
    t = territorio
    if not t:
        p = str(source_id or "").split("-")
        t = p[1] if len(p) > 2 and p[1].startswith("T") and p[1][1:].isdigit() else None
    if not t and not aceitar_sem_territorio:
        raise TerritorioNaoDeclarado(
            "TERRITORIO_NAO_DECLARADO: o SOURCE_ID %r nao traz territorio e nenhum foi declarado. "
            "O RUN_ID carimba o territorio na observacao e ele nao se adivinha." % (source_id,))
    if not t:
        # ⚠️ T0 NAO E UM TERRITORIO: e a AUSENCIA declarada de um.
        #
        # Ha fontes que legitimamente nao tem territorio — uma consulta de busca, um alvo de dataset
        # sem ficha. Recusa-las todas travaria tres linhas inteiras por uma questao de formato; e
        # carimba-las com um territorio real (era T9, COMPETITORS) escrevia uma mentira que viaja com
        # a observacao para sempre.
        #
        #     NAO_SEI DITO NUM LUGAR RESERVADO E HONESTO. NAO_SEI DISFARCADO DE T9 NAO E.
        #
        # T0 nao existe em `leis/territorios.TERRITORIOS` (T1..T13) e nao colide com nenhum. A corrida
        # continua a ser LEGIVEL pela PROVA-TETO — o que importa, porque uma corrida que a prova nao ve
        # e uma corrida que ninguem confere.
        t = SEM_TERRITORIO
    pais = "IT" if str(source_id or "").startswith("IT-") else "XX"
    quando = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    salga = hashlib.sha256(("%s|%s|%s" % (source_id, t, time.time())).encode("utf-8")).hexdigest()[:16]
    return "%s-%s-%s-%s" % (pais, t, quando, salga)


# ══════════════════════════════════════════════════════════════════════════════
# 1. A DESCOBERTA E A COLHEITA, POR LINHA
# ══════════════════════════════════════════════════════════════════════════════
def alvos_da_fonte(linha: str, cand: dict, buscar, *, max_alvos=None) -> dict:
    """→ {"ALVOS": [...], "PEDIDOS": n, "ROTA": ..., "RAW_DA_DESCOBERTA": bytes|None} ou {"ERRO": ...}."""
    import rotas_multicanal as RM                                  # noqa: PLC0415
    alvo = cand.get("ALVO") or {}
    if linha == "YOUTUBE":
        r = RM.youtube_videos_do_canal(channel_id=alvo.get("CHANNEL_ID"), buscar=buscar, max_alvos=max_alvos)
        if r.get("ERRO"):
            return r
        return {"ALVOS": r["ALVOS"], "PEDIDOS": r["PEDIDOS"], "ROTA": r["ROTA"], "URL": r["URL"],
                "RAW_DA_DESCOBERTA": r.get("HTML"), "IDENTIDADE_CONFERIDA": r.get("IDENTIDADE_CONFERIDA"),
                "ALVOS_NA_PAGINA": r.get("VIDEOS_NA_PAGINA")}
    if linha == "INSTAGRAM":
        # Os Reels que o Curator JA provou entram primeiro, por URL DIRECTA (D22) — eles nao dependem da
        # listagem. A listagem por /embed/ (rota provada a 23/09) acrescenta o que a conta servir hoje.
        conhecidos = [{"URL": u, "NOME": (u.rstrip("/").rsplit("/", 1) or [""])[-1],
                       "NATIVE_ID": (u.rstrip("/").rsplit("/", 1) or [""])[-1],
                       "DESCOBERTO_POR": "CURATOR_REELS_JA_NO_REPOSITORIO",
                       "CONTA": alvo.get("HANDLE") or RM.handle_do_endereco(alvo.get("URL_DA_CONTA"))}
                      for u in (alvo.get("REELS_CONHECIDOS") or [])]
        # ⚠️ SO_URL_DIRETA_SEM_LISTAGEM (red team D157). A D22 abre o REEL por URL directa, e so isso:
        # a CONTA continua POLICY_BLOCK pela D19, e a listagem `/<conta>/embed/` NAO e pedida — nem
        # quando o robots a deixasse passar. Os alvos sao os Reels que o Curator PROVOU, e mais nenhum.
        #
        #     AMPLIAR UMA AUTORIZACAO PORQUE ELA ESTAVA PERTO E COMO TRATA-LA COMO PERMISSAO GERAL.
        if not conhecidos:
            return {"ERRO": ("SEM_REEL_CONHECIDO: a D22 abre o Reel por URL directa e esta conta nao tem "
                             "nenhum provado pelo Curator. A listagem da conta nao e pedida (D19)."),
                    "PEDIDOS": 0, "ROTA": RM.ROTA_IG_REEL}
        return {"ALVOS": conhecidos[:max_alvos] if max_alvos else conhecidos, "PEDIDOS": 0,
                "ROTA": RM.ROTA_IG_REEL, "RAW_DA_DESCOBERTA": None,
                "REELS_CONHECIDOS": len(conhecidos), "ROTA_LISTAGEM": "NAO_PEDIDA (D19)",
                "DECISAO_DO_DONO": RM.DECISAO_DO_DONO_IG}
    if linha == "LINKEDIN":
        r = RM.linkedin_posts_da_organizacao(pagina_url=alvo.get("PAGINA"), run_id=cand.get("_RUN_ID") or "LI",
                                             buscar=buscar, teto=max_alvos)
        if r.get("ERRO"):
            return r
        return {"ALVOS": [dict(c, URL=c.get("URL_DO_POST")) for c in r["CARTOES"] if c.get("URL_DO_POST")],
                "PEDIDOS": r["PEDIDOS"], "ROTA": r["ROTA"], "URL": alvo.get("PAGINA"),
                "RAW_DA_DESCOBERTA": None, "VIDEO_BYTES_ACQUIRED": False,
                "FETCH_POST": r.get("FETCH_POST"), "CARTOES_COM_VIDEO": r.get("CARTOES_COM_VIDEO")}
    if linha == "BUSCA":
        # D93 (LINHA-BUSCA): a consulta vai ao motor e cada RESULTADO e um alvo — uma pagina por
        # resultado. Quem sabe falar com os motores e `coleta/linha_busca.py`; nao se refaz aqui.
        import linha_busca as LB                                    # noqa: PLC0415
        import motores as MO                                        # noqa: PLC0415
        # ⚠️ O NOME DO MOTOR E DO VIVO, E NAO UM QUE EU ACHE BONITO. Eu tinha escrito
        # "DUCKDUCKGO_HTML" por omissao, e o dicionario do vivo chama-lhe `DDG_HTML`: as 5 consultas do
        # canario morreram todas com KeyError, e o erro so apareceu na rede real.
        #
        #     UM NOME INVENTADO NUM DICIONARIO ALHEIO NAO DA «NAO ENCONTRADO»: DA KeyError,
        #     e KeyError nao diz a ninguem qual era o nome certo.
        #
        # Por isso o motor desconhecido falha com a LISTA dos que existem, e o padrao e o 1.o motor
        # sem chave do dono (rota HTML livre), lido do proprio dicionario.
        motor = os.environ.get("SINTONIA_BUSCA_MOTOR") or "DDG_HTML"
        if motor not in MO.MOTORES:
            return {"ERRO": "MOTOR_DESCONHECIDO: %r. Os que existem: %s"
                    % (motor, ", ".join(sorted(MO.MOTORES))), "PEDIDOS": 0}
        saida = Path(os.environ.get("SINTONIA_BUSCA_SAIDA") or ".")
        q = {"CONSULTA_ID": cand.get("SOURCE_ID"), "CONSULTA": alvo.get("CONSULTA"),
             "UNIVERSO": cand.get("UNIVERSO")}
        try:
            achados = LB.buscar_consultas(motor, [q], LB.transporte_real(saida), saida)
        except Exception as ex:                                     # noqa: BLE001
            return {"ERRO": "BUSCA: %s: %s" % (type(ex).__name__, str(ex)[:160]), "PEDIDOS": 1}
        erro = next((x["ERRO"] for x in achados if x.get("ERRO")), None)
        if erro:
            return {"ERRO": "BUSCA: %s" % erro, "PEDIDOS": 1, "ROTA": "busca:%s" % motor}
        alvos = [{"URL": x["URL"], "NOME": x.get("CONSULTA_ID"), "NATIVE_ID": x.get("SERP_SHA256"),
                  "POSICAO": x.get("POSICAO"), "DESCOBERTO_POR": "ACHADO_POR_BUSCA",
                  "CONSULTA": x.get("CONSULTA"), "MOTOR": x.get("MOTOR")}
                 for x in achados if x.get("URL")]
        return {"ALVOS": alvos[:max_alvos] if max_alvos else alvos, "PEDIDOS": 1,
                "ROTA": "busca:%s" % motor, "RAW_DA_DESCOBERTA": None, "ALVOS_NA_PAGINA": len(alvos)}
    if linha == "CIENCIA":
        # A consulta do Curator tem a MESMA forma que `pesquisadores_t6.consultas()` monta: o filtro e de
        # AFILIACAO italiana (a pessoa), nunca do lugar do estudo. Um pedido, uma pagina de obras.
        import urllib.parse as U                                    # noqa: PLC0415
        import corpus_pesquisador as CP                             # noqa: PLC0415
        import pesquisadores_t6 as T6                               # noqa: PLC0415
        filtro = alvo.get("FILTRO") or "institutions.country_code:it"
        q = U.urlencode({"filter": "%s,from_publication_date:%s,title_and_abstract.search:%s"
                         % (filtro, T6.DESDE, alvo.get("CONSULTA_OPENALEX") or ""),
                         "per-page": T6.POR_PAGINA, "sort": "publication_date:desc",
                         "select": T6.CAMPOS_OPENALEX, "mailto": CP.MAILTO})
        url = T6.OPENALEX + "?" + q
        d, erro = CP._get(url)
        if erro:
            return {"ERRO": "CIENCIA: %s" % erro, "PEDIDOS": 1, "URL": url, "ROTA": "openalex:works"}
        obras = (d or {}).get("results") or []
        alvos = [{"URL": w.get("id"), "NOME": (w.get("title") or "")[:60], "NATIVE_ID": w.get("id"),
                  "DESCOBERTO_POR": "openalex:works", "OBRA": w} for w in obras if w.get("id")]
        return {"ALVOS": alvos[:max_alvos] if max_alvos else alvos, "PEDIDOS": 1, "URL": url,
                "ROTA": "openalex:works", "RAW_DA_DESCOBERTA": None, "ALVOS_NA_PAGINA": len(obras)}
    return {"ERRO": "LINHA_SEM_ROTA_NESTE_EXECUTOR: %s" % linha, "PEDIDOS": 0}


def colher_alvo(linha: str, a: dict, buscar) -> dict:
    """Os bytes de UM alvo, pela porta. → {"BYTES", "URL", "MEDIA_TYPE", "PEDIDOS"} ou {"ERRO"}."""
    import rotas_multicanal as RM                                  # noqa: PLC0415
    if linha == "YOUTUBE":
        # METADADOS/DESCRICAO, como a missao manda — da pagina publica do video, que o robots APROVA.
        # A transcricao NAO entra aqui: `yt-dlp:public_audio` esta PROVED mas e PROCESSO FILHO, e o
        # registo de rotas desta casa proibe processo filho. Fica declarado como capacidade por ligar.
        r = RM.youtube_metadados_do_video(url=a["URL"], buscar=buscar)
        if r.get("ERRO"):
            return r
        return {"BYTES": r["BYTES"], "URL": r["URL"], "MEDIA_TYPE": r["MEDIA_TYPE"],
                "PEDIDOS": r["PEDIDOS"], "ROTA": r["ROTA"], "REGISTO": r["REGISTO"]}
    if linha == "INSTAGRAM":
        r = RM.instagram_reel(url=a["URL"], buscar=buscar)
        if r.get("ERRO"):
            return r
        # ⚠️ A UNIDADE DO REEL E O REGISTO, E NAO A PAGINA — a mesma forma que o YouTube ja usa.
        #
        # A pagina do Reel e HTML, logo ganhava retrato do detector, e o juiz de capa/materia respondia
        # QUARENTENA (D11) a uma pergunta que nao se aplica: um Reel nao e uma materia nem uma pagina de
        # entrada. Medido no canario de 29/09 — 3 Reels com RAW e 0 na Sala, todos por capa.
        #
        #     A PAGINA CONTINUA A SER JULGADA COMO PAGINA. O QUE MUDA E QUE A UNIDADE DO REEL
        #     NAO E A PAGINA. E isto NAO declara que «social nao passa pelo juiz»: uma pagina de
        #     materia comum continua a passar por ele, como sempre.
        html = r["BYTES"]
        registo = RM.instagram_metadados_do_reel(
            html.decode("utf-8", "replace"), url=r["URL_PUBLICA"], native_id=r["NATIVE_ID"],
            conta=(a or {}).get("CONTA"))
        registo["FONTE_SHA256"] = hashlib.sha256(html).hexdigest()   # a pagina de onde isto saiu
        return {"BYTES": json.dumps(registo, ensure_ascii=False, sort_keys=True).encode("utf-8"),
                "URL": r["URL_PUBLICA"], "MEDIA_TYPE": "application/json",
                "PEDIDOS": r["PEDIDOS"], "ROTA": r["ROTA"], "REGISTO": registo,
                # A PAGINA ORIGINAL continua preservada como observacao — e a prova do que a
                # plataforma serviu, e ela NAO se deita fora por o item ser outro.
                "_FONTE": {"BYTES": html, "URL": r["URL_PUBLICA"], "MEDIA_TYPE": "text/html",
                           "ROTA": r["ROTA"], "PEDIDOS": 0, "ADMITIR": False,
                           "PORQUE_NAO_ADMITIR": ("bytes de ORIGEM do Reel: preservados como observacao; "
                                                  "a unidade julgada e o registo de metadados")}}
    if linha == "LINKEDIN":
        # ⚠️ O post individual NAO se pede: `FETCH_POST` esta ROUTE_NOT_ALLOWED na matriz e continua
        # fechado. O que existe e o que a PAGINA PUBLICA ja serviu na descoberta — o texto publico do
        # cartao. Zero pedidos novos, e zero bytes de video.
        # A unidade do LinkedIn e A DESCOBERTA DO POST, com a midia DECLARADA pela pagina — nao o texto
        # do post (o cartao publico nao o traz) e nao os bytes do video (nao se baixam).
        registo = {k: a.get(k) for k in ("URL_DO_POST", "NATIVE_ID", "LIGACAO", "URL_MP4_DESCOBERTA",
                                         "CAPTION_URL", "ASSET_URN", "DECLARED_LANGUAGE", "POSTER_URL",
                                         "ASPECT_RATIO", "RENDICOES")}
        registo["VIDEO_BYTES_ACQUIRED"] = False
        registo["FETCH_POST"] = "ROUTE_NOT_ALLOWED (matriz social; o post individual nao se pede)"
        if not registo.get("URL_DO_POST") and not registo.get("NATIVE_ID"):
            return {"ERRO": "CARTAO_SEM_IDENTIDADE_DO_POST", "PEDIDOS": 0}
        # A LEGENDA NATIVA (D156: a D23 autoriza «videos (e legenda/transcricao)» de organizacoes).
        # E daqui que vem o TEXTO deste item: o cartao publico traz identidade e midia, NUNCA o texto do
        # post. Sem legenda o item entra na mesma, com a ausencia DECLARADA — nao se inventa um texto.
        pedidos = 0
        if registo.get("CAPTION_URL"):
            leg = RM.linkedin_legenda(caption_url=registo["CAPTION_URL"],
                                      run_id=os.environ.get("SINTONIA_RUN_ID") or "LI", buscar=buscar)
            pedidos += int(leg.get("PEDIDOS") or 0)
            if leg.get("ERRO"):
                registo["TEXTO_ORIGEM"] = "LEGENDA_NATIVA_LINKEDIN_FALHOU"
                registo["TEXTO_PORQUE_NAO"] = leg["ERRO"][:200]
            else:
                registo["TEXTO"] = leg["TEXTO"]
                registo["TEXTO_ORIGEM"] = "LEGENDA_NATIVA_LINKEDIN"
                registo["TEXTO_FORMATO"] = leg.get("FORMATO")
                registo["TEXTO_ROTA"] = leg["ROTA"]
        else:
            registo["TEXTO_ORIGEM"] = "SEM_LEGENDA_DECLARADA_NO_CARTAO"
        corpo = json.dumps(registo, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return {"BYTES": corpo, "URL": a.get("URL_DO_POST"), "MEDIA_TYPE": "application/json",
                "PEDIDOS": pedidos, "ROTA": "linkedin:descoberta-do-post-publico",
                "VIDEO_BYTES_ACQUIRED": False, "TEXTO_ORIGEM": registo.get("TEXTO_ORIGEM")}
    if linha == "BUSCA":
        # A pagina achada, pela MESMA porta (robots vivo, teto, contador).
        r = buscar(a["URL"], "text/html,application/pdf,*/*;q=0.5")
        if r.get("ERRO") or r.get("STATUS") != 200:
            return {"ERRO": "a pagina achada nao respondeu 200 (status %s%s)"
                    % (r.get("STATUS") or 0, ", " + r["ERRO"] if r.get("ERRO") else ""),
                    "PEDIDOS": 1, "URL": a["URL"], "QUEM_DISSE_NAO": r.get("QUEM_DISSE_NAO")}
        mt = (r.get("CONTENT_TYPE") or "text/html").split(";")[0].strip().lower()
        return {"BYTES": r["BYTES"], "URL": a["URL"], "MEDIA_TYPE": mt, "PEDIDOS": 1,
                "ROTA": "ACHADO_POR_BUSCA"}
    if linha == "CIENCIA":
        # A obra JA VEIO na resposta da consulta: nao se pede outra vez. Guarda-se o que o OpenAlex
        # declarou — titulo, resumo (reconstruido do indice invertido), autores, data e DOI.
        #
        #     PEDIR DE NOVO O QUE JA SE TEM E GASTAR ORCAMENTO POR NADA.
        import corpus_pesquisador as CP                             # noqa: PLC0415
        w = a.get("OBRA") or {}
        registo = {"OPENALEX_ID": w.get("id"), "DOI": w.get("doi"), "TITLE": w.get("title"),
                   "PUBLISHED_AT": w.get("publication_date"), "TYPE": w.get("type"),
                   "ABSTRACT": CP._resumo_do_indice(w.get("abstract_inverted_index")),
                   "AUTHORS": [(x.get("author") or {}).get("display_name")
                               for x in (w.get("authorships") or [])],
                   "ROTA": "openalex:works", "TEXTO_ORIGEM": "OPENALEX_TITLE_E_ABSTRACT"}
        if not (registo["TITLE"] or registo["ABSTRACT"]):
            return {"ERRO": "OBRA_SEM_TITULO_NEM_RESUMO", "PEDIDOS": 0, "URL": w.get("id")}
        return {"BYTES": json.dumps(registo, ensure_ascii=False, sort_keys=True).encode("utf-8"),
                "URL": w.get("id"), "MEDIA_TYPE": "application/json", "PEDIDOS": 0,
                "ROTA": "openalex:works"}
    return {"ERRO": "LINHA_SEM_COLHEITA: %s" % linha, "PEDIDOS": 0}


# ══════════════════════════════════════════════════════════════════════════════
# 2. RAW e SALA — a porta canonica, a mesma de `coleta/linha_busca_raw.py`
# ══════════════════════════════════════════════════════════════════════════════
def _slug(v: str) -> str:
    from coleta import ingresso as ing                             # noqa: PLC0415
    return ing._slug(v)


def artefato(linha: str, cand: dict, colhido: dict, capturado: str) -> dict:
    """A ficha na lingua do DONO DO RAW. `SOURCE_ID` vai como o Curator o deu — ou None, declarado."""
    url = colhido["URL"]
    mt = colhido.get("MEDIA_TYPE") or "text/html"
    nome = _slug(os.path.basename(urllib.parse.urlsplit(url).path.rstrip("/")) or "item")[:60] or "item"
    return {
        "COUNTRY": "IT",
        "SOURCE_SLUG": _slug(str(cand.get("SOURCE_ID") or cand.get("NOME") or linha)),
        "ARTIFACT_KIND": "OBSERVATION",
        "NAME": nome + (".json" if mt == "application/json" else ".html"),
        "SOURCE_NATIVE_ID": "u" + hashlib.sha256(url.split("#")[0].encode("utf-8")).hexdigest()[:16],
        "SHA256": hashlib.sha256(colhido["BYTES"]).hexdigest(),
        "BYTES": len(colhido["BYTES"]), "MEDIA_TYPE": mt,
        "CAPTURED_AT": capturado, "SOURCE_URL": url, "USED_BY": None,
        "SOURCE_ID": cand.get("SOURCE_ID"),
        # Nao se inventa DOCUMENT_ID: a observacao fica FORWARD_IDENTITY_UNPROVEN, que e a verdade.
        "DOCUMENT_ID": None,
    }


def a_corrida(linha: str, corrida: str, cand: dict, descoberta: dict) -> dict:
    return {"RUN_ID": corrida, "PLATFORM": PLATAFORMA.get(linha, "HTTP direto"), "ACTOR": ACTOR.get(linha, linha),
            "ACTOR_VERSION": "religa-multicanal-v1", "SOURCE_COUNTRY": "IT",
            "STARTED_AT": _utc(), "RULE_VERSION": RULE_VERSION,
            "MISSION": ("RELIGA-MULTICANAL (D155): linha %s, fonte %s, rota %s; rota publica provada, sem "
                        "login, sem chave, sem rota paga" % (linha, cand.get("SOURCE_ID") or "SEM_SOURCE_ID",
                                                             descoberta.get("ROTA")))[:500],
            "CAPTURE_METHOD": "%s + coleta/scrap_http.buscar_bytes (robots vivo, teto_da_onda -> livro de 24 h)"
                              % descoberta.get("ROTA")}


def admitir_pedidos(dados: bytes, media_type: str, url: str, source_id: str, universos: list,
                    sha: str, capturado: str, corrida: str, raw_asset_id: int = None) -> list:
    """UMA DECISAO POR UNIVERSO PEDIDO (D156). → [{UNIVERSO, ORIGEM, RESULTADO, ..., READY}].

    O mesmo item pode levar duas perguntas explicitas — T8 («quem fala e o campo?») e T3 («fala de
    praga?») — e elas nao se anulam: T8 e TRANSVERSAL. Cada pergunta tem decisao propria, e a origem
    da declaracao viaja com ela, para que se saiba mais tarde QUEM perguntou aquilo.

    Sem universo declarado devolve UMA entrada `UNIVERSO_NAO_DECLARADO`. Isso PARA o item — e e o
    estado certo: falta o pedido, nao falta a regua."""
    if not universos:
        return [{"UNIVERSO": None, "ORIGEM": None, "RESULTADO": "UNIVERSO_NAO_DECLARADO",
                 "REGRA": "pertence ao universo", "READY": None,
                 "MOTIVO": ("o universo vem do PEDIDO e nenhum foi declarado para esta fonte. Esta "
                            "porta nao escolhe um, e nao o deriva do territorio nem da plataforma.")}]
    fora = []
    for u in universos:
        d = admitir(dados, media_type, url, source_id, u["UNIVERSO"], sha, capturado, corrida,
                    raw_asset_id=raw_asset_id)
        d["UNIVERSO"], d["ORIGEM"] = u["UNIVERSO"], u.get("ORIGEM")
        fora.append(d)
    return fora


def admitir(dados: bytes, media_type: str, url: str, source_id: str, universo: str, sha: str,
            capturado: str, corrida: str, raw_asset_id: int = None) -> dict:
    """A ADMISSION NORMAL para uma unidade destas linhas. A MESMA porta de `coleta/linha_busca.admitir`
    (`admissao.decidir` sobre `item_documental_para_a_porta`) — o que muda e UMA coisa, e ela importa:

    ⚠️ O RETRATO DO DETECTOR SO SE CALCULA PARA HTML.

    `linha_busca.texto_de` devolve `"text/html"` para TUDO o que nao e PDF, porque a linha BUSCA so colhe
    paginas. Usada tal e qual aqui, ela punha um `RETRATO_DO_DETECTOR` por cima do JSON do oembed de um
    video — e o juiz de capa/materia, que pergunta «isto e materia ou e pagina de entrada?», respondia
    QUARENTENA (D11) a uma pergunta que nao se aplica. Medido no canario de 29/09: 4 videos com RAW no
    banco e 0 na Sala, todos com REGRA=materia.

        UMA PERGUNTA FEITA A QUEM NAO A PODE RESPONDER NAO DA «NAO SEI»: DA UMA RECUSA COM AR DE MEDIDA.

    A propria Admission ja diz isto (`admissao._e_materia`): «sem retrato do detector (nao e HTML): a
    pergunta nao se aplica». Aqui so se deixa de fabricar o retrato onde ele nao existe. Nada do juizo
    e contornado: para HTML o retrato vai, e o juiz decide como sempre.
    """
    import admissao as adm                                          # noqa: PLC0415
    import executor_texto_de_html as H                              # noqa: PLC0415
    import extratores_de_texto as XT                                # noqa: PLC0415
    import italy_executor as ex                                     # noqa: PLC0415
    import orquestrador as ORQ                                      # noqa: PLC0415
    mt = (media_type or "").split(";")[0].strip().lower()
    if mt == "application/json":
        texto, especie = _texto_do_json(dados), "application/json"
    elif dados[:5] == b"%PDF-" or "pdf" in mt:
        texto, _, _ = XT._de_pdf(dados, "application/pdf")
        texto, especie = texto or "", "application/pdf"
    else:
        t, estado, erro, _ = H.extrair(dados, mt or "text/html")
        texto, especie = (t or ""), "text/html"
    if not texto.strip():
        return {"RESULTADO": "NAO_SEI", "REGRA": "legivel", "MOTIVO": "sem texto legivel (%s)" % especie,
                "READY": None}
    obs = {"SOURCE_ID": source_id, "SOURCE_URL": url, "CAPTURED_AT": capturado}
    est = {"SOURCE_ID": source_id, "TEXTO": texto, "DERIVED_ARTIFACT_ID": "religa-%s" % sha[:16],
           "RAW_ASSET_ID": raw_asset_id, "PARENT_SHA256": sha, "CAPTURED_AT": capturado,
           "TEMPO_E_LUGAR": ex.tempo_e_lugar(obs, dados), "SOURCE_URL": url}
    if especie == "text/html":
        est["RETRATO_DO_DETECTOR"] = H._retrato(dados)              # so aqui a pergunta da capa se aplica
    item = ORQ.item_documental_para_a_porta(est, source_id=source_id)
    d = adm.decidir(item, universo, corrida=corrida)
    out = {"RESULTADO": d.resultado, "REGRA": d.regra, "MOTIVO": d.motivo, "ITEM_ID": d.item, "READY": None}
    # O carimbo de uma regua que ainda nao foi validada por humano viaja COM a decisao — e nao so no
    # relatorio. Sem ele, daqui a um mes um SIM de T8 le-se como um SIM validado.
    carimbo = adm.carimbo_da_regua(universo) if hasattr(adm, "carimbo_da_regua") else {}
    if carimbo:
        out["CARIMBO_DA_REGUA"] = carimbo
    if d.resultado == adm.SIM:
        out["READY"] = adm.pronto_para_inteligencia(item, d)
    return out


def _texto_do_json(dados: bytes) -> str:
    """O texto de um JSON de metadados (o oembed de um video: titulo + autor). Os VALORES de texto, pela
    ordem em que vem — nao as chaves, que sao vocabulario da API e nao conteudo da fonte."""
    try:
        d = json.loads(dados.decode("utf-8", "replace"))
    except ValueError:
        return ""
    fora = []

    def anda(v):
        if isinstance(v, str):
            if v.strip() and not v.startswith(("http://", "https://", "<")):
                fora.append(v.strip())
        elif isinstance(v, dict):
            for x in v.values():
                anda(x)
        elif isinstance(v, list):
            for x in v:
                anda(x)
    anda(d)
    return "\n".join(fora)


def _riqueza(pronto: dict) -> int:
    """Quanto conteudo esta unidade traz. E a medida que decide qual VARIANTE do mesmo documento vai
    para a Sala — a que ve mais. Nao e qualidade nem relevancia: e quantidade de texto, que e a unica
    coisa que se pode comparar entre duas vistas do mesmo documento sem julgar nenhuma."""
    for k in ("TEXTO", "texto", "TEXT", "CONTEUDO"):
        v = pronto.get(k)
        if isinstance(v, str):
            return len(v)
    return len(json.dumps(pronto, ensure_ascii=False, default=str))


def para_a_sala(linha: str, cand: dict, colhidos: list, corrida: str, *, persistencia, pousar: bool) -> dict:
    """PRESERVA -> ADMISSION com o RAW real -> Sala. Devolve o relato, sem levantar por item mau."""
    from guarda import preservar_coleta as PC                      # noqa: PLC0415
    armazem = PC.ArmazemLocal(persistencia.raiz_do_armazem)
    capturado = _utc()

    # ⚠️ DUAS CAPTURAS DOS MESMOS BYTES SAO DUAS OBSERVACOES (COL-LAW-204/311).
    #
    # Este codigo descartava por `sha256` antes de preservar, e depois casava o `RAW_OBSERVATION_ID`
    # tambem pelo `sha256`. Os dois passos estavam errados pela mesma razao: dois enderecos diferentes
    # — ou o mesmo endereco em dois momentos — que devolvam o MESMO byte sao duas OBSERVACOES do mundo,
    # e nao uma. Um canal que republica o mesmo boletim em duas paginas perdia uma das duas, calado; e
    # com o casamento por sha, a que sobrevivesse podia receber o id da outra.
    #
    #     O SHA IDENTIFICA O CONTEUDO. NAO IDENTIFICA A OBSERVACAO.
    #
    # A ligacao certa ja existe nesta casa e e de TRANSPORTE, nao de descoberta: a ALCA (`PASSAGEM_ID`)
    # que se ata a cada artefato e que `preservar()` devolve emparelhada com o id que o banco cunhou
    # (`OBSERVACOES_CONFERIDAS`). E o mesmo metro que `coleta/ingresso.py` usa.
    #
    #     A PONTE NAO PROCURA A OBSERVACAO: ELA RECEBE-A.
    fichas, por_alca = [], {}
    for c in colhidos:
        alca = uuid.uuid4().hex
        f = dict(artefato(linha, cand, c, capturado), **{PC.PASSAGEM: alca})
        por_alca[alca] = c
        fichas.append(f)
    if not fichas:
        return {"RAW": None, "PRONTOS": [], "ITENS": 0, "RELATO": []}
    run = a_corrida(linha, corrida, cand, colhidos[0].get("_DESCOBERTA") or {})
    bytes_por_alca = {a: c["BYTES"] for a, c in por_alca.items()}
    recibo = PC.preservar(run, fichas, armazem, lambda ob: bytes_por_alca[ob[PC.PASSAGEM]],
                          memoria=persistencia.memoria)
    # ⚠️ O PAR VEM EM `RAW_OBSERVATIONS`, e cada observacao ja traz as ALCAS que lhe foram atadas.
    # Eu lia `OBSERVACOES_CONFERIDAS` no topo do recibo, e ele vive DENTRO de
    # `CONFERENCIA_POS_ESCRITA` — a leitura devolvia sempre vazio, e todas as capturas saiam
    # `SEM_RAW_CANONICO`. Medido no canario: o elo partia-se aqui, calado.
    #
    #     UMA CHAVE QUE NAO EXISTE NAO DA ERRO: DA LISTA VAZIA, E A LISTA VAZIA PARECE «NADA ENTROU».
    ids = {}
    for obs in recibo.get("RAW_OBSERVATIONS") or []:
        rid = obs.get("RAW_OBSERVATION_ID")
        if not isinstance(rid, int) or obs.get("RUN_ID") != corrida:
            continue
        for alca in obs.get(PC.PASSAGENS) or []:
            ids[alca] = rid
    prontos, relato = [], []
    for f in fichas:
        alca = f[PC.PASSAGEM]
        c = por_alca[alca]
        rid = ids.get(alca)
        l = {"SHA256": f["SHA256"], "URL": f["SOURCE_URL"], "SOURCE_ID": cand.get("SOURCE_ID"),
             "SOURCE_STATUS": cand.get("SOURCE_STATUS"), "RAW_OBSERVATION_ID": rid, "ROTA": c.get("ROTA"),
             "PASSAGEM": alca, "TEXTO_ORIGEM": c.get("TEXTO_ORIGEM")}
        if rid is None:
            l["ESTADO"] = "SEM_RAW_CANONICO"                       # nao se pousa sem linhagem
            relato.append(l)
            continue
        if c.get("ADMITIR") is False:
            # PRESERVADA, COM LINHAGEM, E NAO JULGADA. Preservar nao e admitir: esta observacao e a
            # prova dos bytes que a plataforma serviu, e a unidade que responde as perguntas e outra.
            l["ESTADO"] = "PRESERVADA_SEM_JULGAMENTO"
            l["PORQUE"] = c.get("PORQUE_NAO_ADMITIR")
            relato.append(l)
            continue
        decisoes = admitir_pedidos(c["BYTES"], f["MEDIA_TYPE"], f["SOURCE_URL"],
                                   cand.get("SOURCE_ID") or "SEM_SOURCE_ID",
                                   cand.get("UNIVERSOS_DO_PEDIDO") or [],
                                   f["SHA256"], capturado, corrida, raw_asset_id=rid)
        l["ADMISSION"] = [{k: d.get(k) for k in ("UNIVERSO", "ORIGEM", "RESULTADO", "REGRA", "MOTIVO",
                                                 "CARIMBO_DA_REGUA")} for d in decisoes]
        aceites = [d for d in decisoes if d.get("READY")]
        for d in aceites:
            prontos.append(d["READY"])
        l["ESTADO"] = ("PRONTO_COM_RAW" if aceites else
                       "ADMISSION_" + "/".join(sorted({str(d["RESULTADO"]) for d in decisoes})))
        relato.append(l)
    # ⚠️ TRES UNIDADES DIFERENTES, E SO UMA DELAS E DESPERDICIO.
    #
    # O LAB mediu no canario: 45 RAW = 21 SHA distintos = 14 DOCUMENTOS. Ler isso como «69% de
    # duplicados» junta tres coisas que nao sao a mesma:
    #
    #     CAPTURAS                       45   toda captura e uma observacao e FICA (D157)
    #     CAPTURAS_REPETIDAS_BYTES       24   o MESMO byte do MESMO alvo na MESMA janela  <- desperdicio
    #     VARIANTES_DO_MESMO_DOCUMENTO    7   rendicoes DIFERENTES do mesmo documento     <- nao e duplicado
    #     DOCUMENTOS                     14   o que a Intelligence tem mesmo para ler
    #
    # As 7 variantes sao o oEmbed (so titulo) e a pagina /watch (com a descricao inteira) do MESMO
    # video: bytes diferentes, conteudo diferente, documento o mesmo. Apagar uma delas seria perder
    # informacao real.
    #
    #     UMA VARIANTE POBRE E UMA VARIANTE RICA DO MESMO DOCUMENTO NAO SAO UM DUPLICADO:
    #     SAO DUAS VISTAS, E UMA DELAS VE MAIS.
    #
    # Por isso a Sala fica com UM item por documento, e escolhe a variante RICA — a de conteudo mais
    # completo. As outras continuam preservadas no RAW como observacoes do mesmo documento; nenhuma e
    # apagada. O desperdicio ataca-se onde ele nasce, que e o PEDIDO repetido (ver `ler_vistos`).
    por_item, ordem = {}, []
    variantes_do_mesmo_doc = 0
    for x in prontos:
        iid = x.get("ITEM_ID")
        if not iid:
            ordem.append(x)
            continue
        if iid not in por_item:
            por_item[iid] = x
            ordem.append(iid)
            continue
        variantes_do_mesmo_doc += 1
        if _riqueza(x) > _riqueza(por_item[iid]):
            por_item[iid] = x                                      # a que ve mais fica
    prontos = [por_item[x] if isinstance(x, str) else x for x in ordem]
    pousado = None
    if pousar and prontos:
        import sala_de_espera as SE                                # noqa: PLC0415
        SE.exigir_canonica()                                       # Sala canonica ou nada; nunca ficheiro
        pousado = SE.pousar(corrida, prontos)
    # AS TRES UNIDADES, SEPARADAS — para que ninguem volte a ler «69% de duplicados» de uma soma que
    # mistura recaptura do mesmo byte com variante do mesmo documento.
    return {"RAW": {"RUN_STATE": recibo.get("RUN_STATE"), "OBSERVACOES": len(ids),
                    "CAPTURAS": len(fichas),
                    "SHA_DISTINTOS": len({f["SHA256"] for f in fichas}),
                    "CAPTURAS_REPETIDAS_BYTES": len(fichas) - len({f["SHA256"] for f in fichas})},
            "PRONTOS": prontos, "ITENS": len({x["ITEM_ID"] for x in prontos if x.get("ITEM_ID")}),
            "DOCUMENTOS": len({x["ITEM_ID"] for x in prontos if x.get("ITEM_ID")}),
            "VARIANTES_DO_MESMO_DOCUMENTO": variantes_do_mesmo_doc,
            "POUSADO": pousado, "RELATO": relato}


# ══════════════════════════════════════════════════════════════════════════════
# 3. A ONDA
# ══════════════════════════════════════════════════════════════════════════════
def correr(linha: str, candidatas: list, saida: Path, *, max_alvos=None, pousar=True,
           buscar=None, persistencia=None) -> int:
    saida.mkdir(parents=True, exist_ok=True)
    livro_onda = saida / "TETO-ONDA.json"
    os.environ["SINTONIA_TETO_ONDA"] = str(livro_onda)
    os.environ["SINTONIA_LINHA"] = linha
    if buscar is None:
        import rotas_multicanal as RM                              # noqa: PLC0415
        buscar = RM.transporte()
    if persistencia is None and pousar:
        from orquestrador import persistencia as PERS              # noqa: PLC0415
        persistencia = PERS.dependencias_do_runtime()
        if persistencia.memoria is None:
            raise SystemExit("RECUSADO: sem memoria canonica (%s). Sem collection_run/raw_asset nao ha RAW, "
                             "e sem RAW a Sala recusa. Declare BANCO_DESCARTAVEL_URL (ensaio) ou "
                             "SINTONIA_COLLECTION_DSN (operacional)." % persistencia.ESTADO)
    foto = _fotografia if pousar else (lambda: None)
    estado = {"INICIO": agora_iso(), "LINHA": linha, "EXECUTOR": "ferramentas/big_collection/onda_linha.py",
              "LIVRO_DA_ONDA": str(livro_onda), "SALA_INICIO": foto(), "FONTES": [], "PAROU": None}

    def grava():
        (saida / ESTADO_F).write_text(json.dumps(estado, ensure_ascii=False, indent=1, default=str),
                                      encoding="utf-8")
    grava()
    # O livro do que ja se colheu vive ACIMA da pasta da onda: uma onda nova nao pode nascer sem
    # memoria do que a anterior ja trouxe — era exactamente assim que o mesmo video vinha seis vezes.
    vistos = ler_vistos(saida.parent)
    estado["ALVOS_JA_COLHIDOS_NA_JANELA"] = len(vistos)
    raw_jsonl, livro_jsonl = saida / RAW_F, saida / LIVRO_F
    for i, cand in enumerate(candidatas, 1):
        t0 = time.time()
        try:
            # A LINHA diz se a ausencia de territorio e normal nesta familia de fontes. Para SITES e
            # YOUTUBE (fontes catalogadas) a falta e um defeito e para; para BUSCA, CIENCIA e as contas
            # de dataset, e um facto — e entra como T0, declarado.
            corrida = run_id(cand.get("SOURCE_ID"), cand.get("TERRITORIO"),
                             aceitar_sem_territorio=linha in SEM_TERRITORIO_E_NORMAL)
        except TerritorioNaoDeclarado as ex:
            estado["FONTES"].append({"N": i, "SOURCE_ID": cand.get("SOURCE_ID"), "HORA": agora_iso(),
                                     "CORREU": False, "STATUS": "FAILED", "PORQUE_NAO_CORREU": str(ex),
                                     "PEDIDOS_POR_DOMINIO": {}, "ALVOS_DESCOBERTOS": 0,
                                     "ALVOS_COLHIDOS": 0, "SEGUNDOS": 0})
            grava()
            print("%02d %s %s FAILED %s" % (i, linha, cand.get("SOURCE_ID"), str(ex)[:110]), flush=True)
            continue
        os.environ["SINTONIA_RUN_ID"] = corrida
        cand["_RUN_ID"] = corrida
        antes = foto()
        linha_reg = {"N": i, "SOURCE_ID": cand.get("SOURCE_ID"), "SOURCE_STATUS": cand.get("SOURCE_STATUS"),
                     "HORA": agora_iso(), "RUN_ID": corrida, "CORREU": False, "DOMINIO": cand.get("DOMINIO"),
                     "ALVOS_DESCOBERTOS": 0, "ALVOS_COLHIDOS": 0, "PEDIDOS_POR_DOMINIO": {}}
        d = alvos_da_fonte(linha, cand, buscar, max_alvos=max_alvos)
        pedidos = int(d.get("PEDIDOS") or 0)
        dom = cand.get("DOMINIO") or ""
        if d.get("ERRO"):
            linha_reg.update(STATUS="FAILED", PORQUE_NAO_CORREU=d["ERRO"], SEGUNDOS=round(time.time() - t0),
                             PEDIDOS_POR_DOMINIO={dom: pedidos} if pedidos else {},
                             QUEM_DISSE_NAO=d.get("QUEM_DISSE_NAO"))
            estado["FONTES"].append(linha_reg)
            grava()
            print("%02d %s %s FAILED %s" % (i, linha, cand.get("SOURCE_ID"), d["ERRO"][:120]), flush=True)
            continue
        alvos = d.get("ALVOS") or []
        linha_reg["ALVOS_DESCOBERTOS"] = len(alvos)
        linha_reg["ROTA"] = d.get("ROTA")
        for k in ("IDENTIDADE_CONFERIDA", "ALVOS_NA_PAGINA", "REELS_CONHECIDOS", "LISTAGEM_FALHOU",
                  "VIDEO_BYTES_ACQUIRED", "FETCH_POST", "CARTOES_COM_VIDEO"):
            if d.get(k) is not None:
                linha_reg[k] = d[k]
        colhidos = []
        repetidos = []
        for a in alvos[:max_alvos] if max_alvos else alvos:
            ja = vistos.get((linha, a.get("URL")))
            if ja:
                # NAO se pede outra vez. Regista-se que ja se tinha, e com que corrida.
                repetidos.append({"URL": a.get("URL"), "VISTO_ANTES_EM": ja["EM"],
                                  "RUN_ID_ANTERIOR": ja["RUN_ID"]})
                with open(livro_jsonl, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"ESTADO": "VISTO_ANTES", "URL": a.get("URL"), "LINHA": linha,
                                         "RUN_ID_ANTERIOR": ja["RUN_ID"], "CORRIDA": corrida},
                                        ensure_ascii=False) + "\n")
                continue
            c = colher_alvo(linha, a, buscar)
            pedidos += int(c.get("PEDIDOS") or 0)
            if c.get("ERRO"):
                with open(livro_jsonl, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"ESTADO": "FALHOU", "URL": a.get("URL"), "PORQUE": c["ERRO"],
                                         "LINHA": linha, "CORRIDA": corrida}, ensure_ascii=False) + "\n")
                continue
            c["_DESCOBERTA"] = d
            c["_ALVO"] = a
            colhidos.append(c)
            # A captura de ORIGEM, quando a rota a separa do item: duas capturas, DUAS observacoes
            # (COL-LAW-204/311) — e so uma delas e julgada.
            fonte = c.pop("_FONTE", None)
            if fonte:
                colhidos.append(dict(fonte, _DESCOBERTA=d, _ALVO=a))
            anotar_visto(saida.parent, linha, a.get("URL"), corrida)
            with open(raw_jsonl, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"SHA256": hashlib.sha256(c["BYTES"]).hexdigest(), "SOURCE_URL": c["URL"],
                                     "SOURCE_ID": cand.get("SOURCE_ID"), "MEDIA_TYPE": c.get("MEDIA_TYPE"),
                                     "BYTES": len(c["BYTES"]), "CORRIDA": corrida, "LINHA": linha,
                                     "ROTA": c.get("ROTA"), "CAPTURED_AT": _utc(),
                                     "PROVENIENCIA": dict(cand.get("PROVENIENCIA") or {},
                                                          DESCOBERTO_POR=a.get("DESCOBERTO_POR") or d.get("ROTA"),
                                                          CONTA=a.get("CONTA"))},
                                    ensure_ascii=False) + "\n")
        linha_reg["ALVOS_COLHIDOS"] = len(colhidos)
        linha_reg["ALVOS_VISTOS_ANTES"] = len(repetidos)
        if repetidos:
            linha_reg["VISTO_ANTES"] = repetidos
        linha_reg["PEDIDOS_POR_DOMINIO"] = {dom: pedidos} if dom else {}
        if colhidos and pousar:
            try:
                r = para_a_sala(linha, cand, colhidos, corrida, persistencia=persistencia, pousar=True)
                linha_reg.update(RAW=r["RAW"], ITENS_NA_SALA=r["ITENS"], POUSADO=r.get("POUSADO"),
                                 RELATO=r["RELATO"], CORREU=True, STATUS="OK")
            except Exception as ex:                                # noqa: BLE001 — a falha da Sala tem nome
                linha_reg.update(STATUS="FAILED", PORQUE_NAO_CORREU="SALA: %s: %s" % (type(ex).__name__, ex))
        else:
            linha_reg.update(CORREU=bool(colhidos), STATUS="OK" if colhidos else "ZERO",
                             PORQUE_NAO_CORREU=None if colhidos else "ZERO_ALVOS_COLHIDOS")
        linha_reg["SEGUNDOS"] = round(time.time() - t0)
        linha_reg["SALA_ANTES"], linha_reg["SALA_DEPOIS"] = antes, foto()
        estado["FONTES"].append(linha_reg)
        grava()
        print("%02d %s %s %s alvos=%d colhidos=%d pedidos=%d" % (i, linha, cand.get("SOURCE_ID"),
              linha_reg["STATUS"], len(alvos), len(colhidos), pedidos), flush=True)
    estado["FIM"] = agora_iso()
    estado["SALA_FIM"] = foto()
    grava()
    return 0


def _fotografia():
    import ensaio_offline as E                                     # noqa: PLC0415
    return {k: v["LINHAS"] for k, v in E.fotografia().items()}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    if "--correr" not in argv or "linha" not in arg or "fontes" not in arg or "saida" not in arg:
        print(__doc__)
        return 2
    cands = json.loads(Path(arg["fontes"]).read_text(encoding="utf-8"))
    if isinstance(cands, dict):
        cands = cands.get("CANDIDATAS", cands).get(arg["linha"], [])
    return correr(arg["linha"], cands, Path(arg["saida"]),
                  max_alvos=int(arg["max-alvos"]) if arg.get("max-alvos") else None,
                  pousar="--sem-sala" not in argv)


if __name__ == "__main__":
    raise SystemExit(main())
