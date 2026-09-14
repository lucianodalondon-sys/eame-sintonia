#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OS TERRITORIOS T1-T12 — UMA LISTA, UM DONO, E O DONO NAO E ESTE FICHEIRO.

O dono e o atlas:

    docs/fontes/ATLAS-DE-FONTES-EAME.md · secao "OS 12 TERRITORIOS"

Este ficheiro nao guarda a lista: ele LE a tabela do atlas. A diferenca nao e
estilo — e a unica maneira de a lista nao poder divergir. Guardar uma copia aqui
criaria a terceira verdade, e a casa ja pagou pelo problema de ter duas:

    ANTES DESTE FICHEIRO, T5 SIGNIFICAVA DUAS COISAS AO MESMO TEMPO.

    atlas            T5 = SCIENCE
    pedido/pedido.py T5 = "Preco e mercado"

    E o mais grave: o comentario do proprio `pedido.py` dizia
    «Sao os territorios que o atlas de fontes ja usa». Dizia, e nao eram.
    Um ficheiro que se declara fiel a uma lei e a contradiz e pior do que um
    ficheiro que inventa a sua: quem le acredita nele.

Seis codigos de doze significavam coisa diferente nas duas listas — T5, T6, T7,
T10, T11 e T12. Dizer «T7» podia querer dizer REDE TECNICA ou CIENCIA E ENSAIO,
dependendo de quem estava a falar.

POR QUE O ATLAS E QUE MANDA, E NAO O CODIGO MAIS RECENTE
---------------------------------------------------------
1 · `AGENTS.md` (linhas 354-361) poe o atlas como a morada de uma fonte
    REGISTADA: e la que a ficha nasce, e a ficha traz o campo `TERRITORY`.
2 · O atlas e o unico sitio que da a cada codigo um NOME **e um ESCOPO**, e o
    unico que declara a convencao de `SOURCE_ID`: `T1..T12`.
3 · Os dois ficheiros divergentes declaram-se, no proprio comentario, copias do
    atlas (`pedido/pedido.py:61-64`; `scan_sources.py:49` chega a apontar para o
    caminho do atlas). Nenhum deles se apresenta como taxonomia nova — logo sao
    deriva, nao revisao.
4 · Os `SOURCE_ID` ja emitidos foram cunhados com o significado do ATLAS, e isso
    foi medido ficha a ficha:
        EU-T10-001 = precos de cereais do Agri-food Data Portal  -> MERCADO
        ES-T7-001..027 = imprensa tecnica e associacoes agrarias  -> REDE TECNICA
        IT-T11-001 = feira EIMA · FR-T11-001 = Vinitech-SIFEL     -> EVENTOS
        EU-T12-001 = CELLAR, camada de politica agricola          -> POLITICA
        EU-T5-001 / ES-T5-002 = OpenAlex                          -> CIENCIA
    Se a lista da deriva valesse, estas cinco identidades estariam todas erradas.

    NENHUM SOURCE_ID PRECISA MUDAR. A DERIVA ESTAVA NO ROTULO, NAO NA IDENTIDADE.

SUBSTANCIA ATIVA NAO E UM TERRITORIO
------------------------------------
A deriva tinha `T12 = "Substancia ativa"`. O atlas poe substancia ativa DENTRO
de T4, e ate escreve a separacao obrigatoria: *EU ACTIVE SUBSTANCE* e *NATIONAL
PRODUCT AUTHORIZATION* sao duas camadas de T4, nunca misturadas. T12 e POLITICA.
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
SECAO = "## OS 12 TERRITÓRIOS"

_LINHA = re.compile(r"^\|\s*\*\*(T\d{1,2})\*\*\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*$",
                    re.M)


class TaxonomiaIndisponivel(RuntimeError):
    """O atlas nao pode ser lido.

    Levanta de proposito, e nao devolve uma copia de emergencia: uma copia de
    emergencia e exatamente como nasce a segunda verdade que este ficheiro
    existe para matar.
    """


def _ler_atlas():
    if not ATLAS.exists():
        raise TaxonomiaIndisponivel(f"atlas nao encontrado em {ATLAS}")
    txt = ATLAS.read_text(encoding="utf-8")
    if SECAO not in txt:
        raise TaxonomiaIndisponivel(
            f"a secao '{SECAO}' desapareceu de {ATLAS.name} — "
            f"a taxonomia perdeu o dono")
    dentro = txt.split(SECAO, 1)[1]
    dentro = dentro.split("###", 1)[0]          # a tabela vem antes da 1a subsecao
    achados = _LINHA.findall(dentro)
    if len(achados) != 12:
        raise TaxonomiaIndisponivel(
            f"a tabela de territorios do atlas devolveu {len(achados)} linhas, "
            f"e nao 12. Ou a tabela mudou de forma, ou mudou de conteudo — "
            f"nos dois casos alguem tem de olhar, e nao adivinhar")
    nomes, escopos = {}, {}
    for codigo, nome, escopo in achados:
        nomes[codigo] = nome.strip()
        escopos[codigo] = escopo.strip()
    esperados = [f"T{i}" for i in range(1, 13)]
    if sorted(nomes, key=lambda c: int(c[1:])) != esperados:
        raise TaxonomiaIndisponivel(
            f"o atlas listou {sorted(nomes)} e nao T1..T12")
    return nomes, escopos


TERRITORIOS, ESCOPO = _ler_atlas()
CODIGOS = tuple(f"T{i}" for i in range(1, 13))

# ── A EXCECAO, DECLARADA · T13 ────────────────────────────────────────────
# O atlas contradiz-se, e a contradicao e real: o cabecalho diz "OS 12
# TERRITORIOS" e a convencao de SOURCE_ID diz `T1..T12`, mas o CORPO do atlas
# tem a secao "T13 · DISTRIBUTION — FRANCE" com uma ficha completa.
#
# Nao se apaga T13 e nao se renomeia o ID: `SOURCE_ID` e identidade, e
# identidade emitida nao se recicla (convencao de SOURCE_ID, no proprio atlas).
# Fica registado como o que e: um ocupante sem definicao na lista.
#
# ATENCAO: a deriva tinha `T13 = "Outro"`. No atlas T13 e DISTRIBUTION. Sao
# significados diferentes, e por isso "outro" NAO e um alvo aceitavel.
EXCECOES = {
    "T13": {
        "NOME_NO_ATLAS": "DISTRIBUTION",
        "ESTADO": "OCUPANTE SEM DEFINICAO NA LISTA — nao e territorio canonico",
        "ONDE": "docs/fontes/ATLAS-DE-FONTES-EAME.md, secao 'T13 · DISTRIBUTION — FRANCE'",
        "IDS_EMITIDOS": ("FR-T13-001", "ES-T13-001", "IT-T13-001"),
        "IDS_COM_FICHA_E_EVIDENCIA": ("FR-T13-001",),
        "IDS_EM_NAO_SEI": ("ES-T13-001", "IT-T13-001"),
        "PRESERVAR": True,
        "POR_QUE_NAO_MIGRAR_AGORA": (
            "renomear FR-T13-001 quebra a convencao de SOURCE_ID do proprio atlas "
            "e mexe em tres ficheiros de teste que travam a contagem "
            "(tests/test_handoff.py:112 assert SOURCE_ID_COUNT == 37). "
            "A migracao e uma missao propria, com dono de decisao: Luciano."),
        "NAO_CONFUNDIR_COM": "a deriva chamava T13 de 'Outro'. Nao e.",
    }
}

# ── OS APELIDOS · a palavra que uma pessoa diz ────────────────────────────
# Uma pessoa nao pede «T6»: pede «pesquisadores». Cada apelido abaixo vem do
# ESCOPO que o proprio atlas escreve para aquele codigo — a coluna de escopo da
# tabela e a fonte, nao o gosto de quem escreve isto.
#
# Isto nao e uma segunda lista de assuntos: e um dicionario de traducao para a
# lista unica. Os codigos sao validados contra TERRITORIOS no fim do ficheiro.
APELIDOS = {
    # T1 · escopo: area plantada, producao, produtividade, calendario agricola,
    #      desenvolvimento da cultura, previsao de safra, regioes produtoras
    "cultura": "T1", "culturas": "T1", "producao": "T1", "produtividade": "T1",
    "safra": "T1", "colheita": "T1", "area plantada": "T1", "cereais": "T1",
    "calendario agricola": "T1", "previsao de safra": "T1",
    # T2 · escopo: chuva, temperatura, seca, geada, ondas de calor, umidade do
    #      solo, estresse hidrico, eventos extremos
    "clima": "T2", "tempo": "T2", "chuva": "T2", "temperatura": "T2",
    "seca": "T2", "geada": "T2", "agua": "T2", "solo": "T2",
    "irrigacao": "T2", "agrometeo": "T2", "estresse hidrico": "T2",
    # T3 · escopo: doencas, insetos, plantas daninhas, alertas, intensidade,
    #      geografia, evolucao temporal, resistencia
    "praga": "T3", "pragas": "T3", "doenca": "T3", "doencas": "T3",
    "inseto": "T3", "insetos": "T3", "daninha": "T3", "daninhas": "T3",
    "infestante": "T3", "infestantes": "T3", "erva": "T3",
    "alerta": "T3", "alertas": "T3", "fitossanitario": "T3",
    # T4 · escopo: produtos, registros, culturas autorizadas, alvos,
    #      SUBSTANCIAS ATIVAS, empresas, validade, autorizacoes, retiradas
    "regulatorio": "T4", "registro": "T4", "rotulo": "T4", "rotulos": "T4",
    "autorizacao": "T4", "autorizacoes": "T4", "substancia ativa": "T4",
    "substancias ativas": "T4", "moa": "T4", "revogacao": "T4",
    # T5 · escopo: papers, estudos, trials, institutos, universidades,
    #      projetos, tecnologias, novas praticas, inovacao agronomica
    "ciencia": "T5", "artigo": "T5", "artigos": "T5",
    "artigos cientificos": "T5", "paper": "T5", "papers": "T5",
    "estudo": "T5", "estudos": "T5", "ensaio": "T5", "ensaios": "T5",
    "trial": "T5", "universidade": "T5", "inovacao": "T5",
    # T6 · escopo: pesquisadores por cultura, problema, instituicao,
    #      territorio, especialidade
    "pesquisador": "T6", "pesquisadores": "T6",
    "materiais de pesquisadores": "T6", "investigador": "T6",
    "investigadores": "T6", "especialista": "T6", "especialistas": "T6",
    # T7 · escopo: agronomos, advisors, crop specialists, consultores,
    #      extensao, institutos tecnicos, cooperativas, associacoes
    "agronomo": "T7", "agronomos": "T7", "tecnico": "T7", "tecnicos": "T7",
    "consultor": "T7", "consultores": "T7", "cooperativa": "T7",
    "cooperativas": "T7", "associacao": "T7", "associacoes": "T7",
    "consorcio": "T7", "consorcios": "T7", "extensao": "T7",
    "rede tecnica": "T7", "assistencia tecnica": "T7",
    # T8 · escopo: agricultores, creators, YouTube, Instagram, TikTok,
    #      LinkedIn, podcasts, newsletters
    "produtor": "T8", "produtores": "T8", "agricultor": "T8",
    "agricultores": "T8", "creator": "T8", "creators": "T8",
    "influenciador": "T8", "influenciadores": "T8", "voz do campo": "T8",
    "youtube": "T8", "instagram": "T8", "tiktok": "T8", "linkedin": "T8",
    "podcast": "T8", "newsletter": "T8",
    # T9 · escopo: BASF, Bayer, Syngenta, Corteva, FMC, UPL, Nufarm + outros
    "concorrente": "T9", "concorrentes": "T9", "competidor": "T9",
    "competidores": "T9", "basf": "T9", "bayer": "T9", "syngenta": "T9",
    "corteva": "T9", "fmc": "T9", "upl": "T9", "nufarm": "T9",
    # T10 · escopo: commodities, producao, precos confiaveis, importacoes,
    #       exportacoes, industria, ingredientes ativos, movimentos de mercado
    "mercado": "T10", "preco": "T10", "precos": "T10", "cotacao": "T10",
    "cotacoes": "T10", "commodity": "T10", "commodities": "T10",
    "importacao": "T10", "exportacao": "T10", "industria": "T10",
    "comercio": "T10",
    # T11 · escopo: feiras, congressos, field days, webinars, eventos
    #       cientificos, pesquisadores participantes, temas, empresas presentes
    "evento": "T11", "eventos": "T11", "feira": "T11", "feiras": "T11",
    "congresso": "T11", "congressos": "T11", "webinar": "T11",
    "webinars": "T11", "field day": "T11", "jornada": "T11",
    # T12 · escopo: CAP, politicas agricolas, sustentabilidade, reducao de
    #       insumos, agricultura regenerativa, restricoes
    "politica": "T12", "politicas": "T12", "politica agricola": "T12",
    "pac": "T12", "cap": "T12", "psr": "T12", "subsidio": "T12",
    "subsidios": "T12", "sustentabilidade": "T12", "regenerativa": "T12",
    "ambiente agricola": "T12",
}

# ── OS AMBIGUOS, DECLARADOS ───────────────────────────────────────────────
# Palavras que aparecem no escopo de MAIS DE UM territorio no atlas. Escolher em
# silencio seria o mesmo erro da deriva, so mais pequeno. O apelido cai no
# primeiro, e quem chamar leva o aviso de que havia outra leitura possivel.
AMBIGUOS = {
    "producao": ("T1", "T10", "o atlas cita 'producao' no escopo de T1 "
                              "(area/produtividade) e de T10 (commodities)"),
    "resistencia": ("T3", "T5", "o atlas cita 'resistencia' no escopo de T3 "
                                "(evolucao no campo) e de T5 (investigacao)"),
    "substancia ativa": ("T4", "T10", "o atlas poe substancias ativas no escopo "
                                      "de T4 e 'ingredientes ativos' no de T10"),
}


class TerritorioInvalido(ValueError):
    """O que se pediu nao e um territorio desta casa."""


def valido(codigo: str) -> bool:
    """T1..T12. T13 NAO e valido — e ocupante legado, nao territorio."""
    return (codigo or "").strip().upper() in CODIGOS


def _limpa(texto: str) -> str:
    t = (texto or "").strip().lower()
    for de, para in (("á", "a"), ("â", "a"), ("ã", "a"), ("à", "a"),
                     ("é", "e"), ("ê", "e"), ("í", "i"), ("ó", "o"),
                     ("ô", "o"), ("õ", "o"), ("ú", "u"), ("ç", "c")):
        t = t.replace(de, para)
    return re.sub(r"\s+", " ", t)


def codigo_de(texto: str) -> str:
    """A palavra de uma pessoa -> o codigo do atlas. Nunca adivinha.

    Levanta `TerritorioInvalido` com a lista do que existe. Adivinhar aqui
    significaria coletar o assunto errado e descobrir depois de gastar maquina.
    """
    t = _limpa(texto)
    if not t:
        raise TerritorioInvalido("alvo vazio")
    alto = t.upper()
    if alto in CODIGOS:
        return alto
    if alto in EXCECOES:
        raise TerritorioInvalido(
            f"{alto} nao e territorio canonico: {EXCECOES[alto]['ESTADO']}. "
            f"Ele existe apenas nos SOURCE_ID ja emitidos "
            f"({', '.join(EXCECOES[alto]['IDS_EMITIDOS'])}) e nao se pede.")
    if t in APELIDOS:
        return APELIDOS[t]
    for codigo, nome in TERRITORIOS.items():          # o nome oficial inteiro
        if _limpa(nome) == t:
            return codigo
    for ap in sorted(APELIDOS, key=len, reverse=True):  # o apelido dentro da frase
        if ap in t:
            return APELIDOS[ap]
    raise TerritorioInvalido(
        "alvo desconhecido: " + repr(texto) + ". Os territorios sao: "
        + " · ".join(f"{c} ({TERRITORIOS[c]})" for c in CODIGOS))


def nome_de(codigo: str) -> str:
    c = (codigo or "").strip().upper()
    if c in TERRITORIOS:
        return TERRITORIOS[c]
    if c in EXCECOES:
        return EXCECOES[c]["NOME_NO_ATLAS"] + " (ocupante legado)"
    raise TerritorioInvalido(f"codigo desconhecido: {codigo!r}")


def aviso_de_ambiguidade(texto: str):
    """Devolve o aviso se a palavra pedida for ambigua no atlas, ou None."""
    t = _limpa(texto)
    if t in AMBIGUOS:
        a, b, porque = AMBIGUOS[t]
        return (f"'{t}' cai em {a} ({TERRITORIOS[a]}), mas tambem podia ser "
                f"{b} ({TERRITORIOS[b]}): {porque}")
    return None


# ── auto-verificacao no import ────────────────────────────────────────────
# Um apelido a apontar para um codigo que nao existe e uma bomba de efeito
# retardado: passa no import e explode num pedido, meses depois.
for _ap, _c in APELIDOS.items():
    if _c not in TERRITORIOS:
        raise TaxonomiaIndisponivel(
            f"o apelido {_ap!r} aponta para {_c}, que o atlas nao define")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"DONO = {ATLAS.relative_to(RAIZ).as_posix()} · secao {SECAO!r}")
    print()
    for c in CODIGOS:
        print(f"  {c:4s} {TERRITORIOS[c]}")
        print(f"       escopo: {ESCOPO[c][:96]}")
    print()
    print("EXCECOES (ocupante legado, nao territorio):")
    for c, e in EXCECOES.items():
        print(f"  {c:4s} {e['NOME_NO_ATLAS']} · {e['ESTADO']}")
        print(f"       IDs emitidos: {', '.join(e['IDS_EMITIDOS'])}")
    print()
    print(f"APELIDOS = {len(APELIDOS)} palavras · AMBIGUOS declarados = {len(AMBIGUOS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
