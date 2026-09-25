"""SOC-ONDA2 · A ROTA DO SCRAP PARA UMA CONTA SOCIAL, VISTA DO LADO DO CURATOR.

Irmão de `rota_do_scrap_youtube.py` (SOC2), para as plataformas que a SOC2 não
cobria. A lei é a mesma e não se repete aqui:

    O CURATOR NOMEIA A ROTA; O SCRAP É QUE A CORRE; A MATRIZ É QUE A PERMITE.

LINKEDIN (D23) — a fase `video-linkedin` (`linkedin.org.video`) lê a PÁGINA
PÚBLICA DE UMA ORGANIZAÇÃO (`/company/<slug>/`) e traz os vídeos e as legendas
dela. Perfil de pessoa fica fora (D23; D24 só abre o POST de pessoa por URL), e
`/showcase/` não é alvo que o adaptador aceite hoje — nomear essa rota seria um
contrato que passa na validação e reprova sempre no Scrap.

INSTAGRAM (D22) — o Scrap só colhe o Reel por URL DIRECTA. Listar os Reels de
uma conta é `instagram.profile.discovery` (fase `janela`), e a matriz dá-lhe
ROUTE_NOT_ALLOWED. Uma conta Instagram não tem, portanto, rota que a colha: fica
bloqueada com o nome do buraco, e não com «recusada».

`conferir(aq)` é o ÚNICO ponto que a validação e o VALIDATE_ROUTE chamam para
uma aquisição `SCRAP_FASE`: despacha pela FASE para o conferidor da plataforma.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import rota_do_scrap_youtube as RSY  # noqa: E402

STRATEGY = RSY.STRATEGY
EXECUTOR = RSY.EXECUTOR

# ── LINKEDIN ────────────────────────────────────────────────────────────────
LI_FASE = "video-linkedin"
LI_PLATAFORMA = "LINKEDIN"
LI_CAPACIDADE = "linkedin.org.video"
LI_FILTRO = "pagina"
LI_TETO = 2                  # canário: 1–2 itens por conta (regra da casa)
LI_AUTORIZACAO = ("D23 (DECISOES-DONO-2026-09-23): video de pagina publica de "
                  "ORGANIZACAO no LinkedIn, risco assumido pelo dono")
LI_KIND = "LINKEDIN_ORG_SLUG"

# O MESMO desenho do adaptador (`coleta/adaptador_linkedin._PAGINA_ORGANIZACAO`):
# o que ele recusa, o Curator não contrata.
#
# Uma cauda de secção (`/admin/dashboard`, `/posts`, `/about`) cai: medido em
# 24/09, duas organizações publicam no site o link do PAINEL de administrador da
# própria página (`/company/15179878/admin/dashboard`). A página é a mesma — o
# número está no endereço que a organização publicou; só a secção é que não é
# pública. O que se contrata é sempre `/company/<slug>/`, que é o que o adaptador lê.
RE_LI_ORG = re.compile(r"^https?://(?:[a-z]{2,3}\.)?linkedin\.com/company/"
                       r"([A-Za-z0-9\-_%\.]{2,100})(?:/(?:admin|posts|about|mycompany|"
                       r"videos|life|jobs)(?:/[^?#]*)?)?/?(?:[?#].*)?$", re.I)
RE_LI_SHOWCASE = re.compile(r"linkedin\.com/showcase/", re.I)
RE_LI_PESSOA = re.compile(r"linkedin\.com/(?:in|pub)/", re.I)

# ── INSTAGRAM ───────────────────────────────────────────────────────────────
IG_FASE_LISTAR = "janela"    # instagram.profile.discovery — a matriz diz o que vale


def slug_linkedin(url: str) -> tuple[str | None, str]:
    """→ (slug da organização, "") ou (None, porquê). Sem rede."""
    u = (url or "").strip()
    if RE_LI_PESSOA.search(u):
        return None, "PERFIL_DE_PESSOA"
    if RE_LI_SHOWCASE.search(u):
        return None, "SHOWCASE_NAO_E_ALVO_DO_SCRAP"
    m = RE_LI_ORG.match(u)
    if not m:
        return None, "URL_LINKEDIN_SEM_PAGINA_DE_ORGANIZACAO"
    return m.group(1).lower(), ""


def pagina_linkedin(slug: str) -> str:
    """O endereço canónico que o adaptador aceita."""
    return "https://www.linkedin.com/company/%s/" % slug


def _declarado(fase: str) -> dict:
    RSY._caminhos()
    import scrap_colheita as sc
    import scrap_capacidades as cap
    import social_matriz as mz
    linha = sc.FASES.get(fase)
    if not linha:
        return {"FASE_EXISTE": False}
    plat, capac = linha[0], linha[1]
    d = mz.decisao(plat, cap.da_matriz(capac) or "")
    return {"FASE_EXISTE": True, "PLATAFORMA": plat, "CAPACIDADE": capac,
            "FILTROS": dict(sc.NOMEADOS.get(fase) or {}),
            "DECISAO": d.get("DECISAO"), "ROTA": d.get("ROTA"), "CLASSE": d.get("CLASSE")}


def o_que_o_scrap_declara_linkedin() -> dict:
    return _declarado(LI_FASE)


def instagram_listar_permitido() -> tuple[bool, str]:
    """A matriz deixa listar os Reels de uma conta? (hoje: não)"""
    d = _declarado(IG_FASE_LISTAR)
    if not d.get("FASE_EXISTE"):
        return False, "o Scrap nao declara a fase %s" % IG_FASE_LISTAR
    return d.get("DECISAO") == "ALLOWED", "%s/%s: %s" % (
        d.get("PLATAFORMA"), d.get("CAPACIDADE"), d.get("DECISAO"))


def acquisition_linkedin(slug: str, declarado: dict | None = None) -> dict:
    declarado = o_que_o_scrap_declara_linkedin() if declarado is None else declarado
    pagina = pagina_linkedin(slug)
    return {
        "STRATEGY": STRATEGY,
        "EXECUTOR": EXECUTOR,
        "FASE": LI_FASE,
        "PLATFORM": LI_PLATAFORMA,
        "CAPACIDADE": LI_CAPACIDADE,
        "LINKEDIN_SLUG": slug,
        "FILTROS": {LI_FILTRO: pagina, "teto": LI_TETO},
        "ROTA_DECLARADA_PELO_SCRAP": declarado.get("ROTA"),
        "AUTORIZACAO": LI_AUTORIZACAO,
    }


def conferir_linkedin(aq: dict, declarado: dict | None = None) -> tuple[bool, str]:
    """O bloco ainda bate com o Scrap de HOJE? Sem rede, sem gasto."""
    if (aq or {}).get("STRATEGY") != STRATEGY:
        return False, "STRATEGY nao e %s" % STRATEGY
    slug = aq.get("LINKEDIN_SLUG") or ""
    pagina = (aq.get("FILTROS") or {}).get(LI_FILTRO) or ""
    s2, porque = slug_linkedin(pagina)
    if not slug or s2 != slug:
        return False, "FILTROS.%s nao e a pagina de organizacao do contrato (%s)" % (
            LI_FILTRO, porque or pagina)
    if aq.get("EXECUTOR") != EXECUTOR or aq.get("FASE") != LI_FASE:
        return False, "executor/fase fora da rota do Scrap: %s/%s" % (
            aq.get("EXECUTOR"), aq.get("FASE"))
    d = o_que_o_scrap_declara_linkedin() if declarado is None else declarado
    if not d.get("FASE_EXISTE"):
        return False, "o Scrap deixou de declarar a fase %s" % LI_FASE
    if (d.get("PLATAFORMA"), d.get("CAPACIDADE")) != (LI_PLATAFORMA, LI_CAPACIDADE):
        return False, "a fase %s pede %s/%s, nao %s/%s" % (
            LI_FASE, d.get("PLATAFORMA"), d.get("CAPACIDADE"), LI_PLATAFORMA, LI_CAPACIDADE)
    if LI_FILTRO not in (d.get("FILTROS") or {}):
        return False, "a fase %s ja nao recebe o filtro %s" % (LI_FASE, LI_FILTRO)
    if d.get("DECISAO") != "ALLOWED":
        return False, "a matriz do Scrap diz %s para esta rota" % d.get("DECISAO")
    if aq.get("ROTA_DECLARADA_PELO_SCRAP") != d.get("ROTA"):
        return False, ("o Scrap declara hoje a rota %s e o contrato foi escrito para %s"
                       % (d.get("ROTA"), aq.get("ROTA_DECLARADA_PELO_SCRAP")))
    return True, "rota do Scrap: %s · %s · ALLOWED" % (LI_FASE, d.get("ROTA"))


def conferir(aq: dict) -> tuple[bool, str]:
    """Despacha pela FASE. Uma fase sem conferidor não passa."""
    fase = (aq or {}).get("FASE")
    if fase == RSY.FASE:
        return RSY.conferir(aq)
    if fase == LI_FASE:
        return conferir_linkedin(aq)
    return False, "fase do Scrap sem conferidor no Curator: %r" % fase


def pagina_conhecida(slug: str, *, tabela=None, livro=None, alloc=None) -> list[str]:
    """→ os SOURCE_ID que já ligam esta página LinkedIn. Mais de um é colisão."""
    tabela = RSY._ler(RSY.TABELA) if tabela is None else tabela
    livro = RSY._ler(RSY.LIVRO) if livro is None else livro
    alloc = RSY._ler(RSY.ALLOCATION) if alloc is None else alloc
    achados = set()
    for c in (tabela.get("FONTES") or []) + (livro.get("FONTES") or []):
        aq = c.get("ACQUISITION") or {}
        if slug in ((aq.get("LINKEDIN_SLUG") or "").lower(),
                    (c.get("SOURCE_NATIVE_ID") or "").lower()) \
                and c.get("SOURCE_NATIVE_ID_KIND", LI_KIND) == LI_KIND:
            achados.add(c["SOURCE_ID"])
    for n in alloc.get("NOVAS") or []:
        if n.get("SOURCE_NATIVE_ID_KIND") == LI_KIND and (n.get("SOURCE_NATIVE_ID") or "").lower() == slug:
            achados.add(n["SOURCE_ID"])
    return sorted(achados)
