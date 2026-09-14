#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS QUATRO MATRIZES, MAIS A DO RADAR.

O RADAR NAO TEM FAMILIA DE FONTES, E ISSO NAO E' UM DETALHE
-----------------------------------------------------------
O Opportunity Radar e' um CRUZAMENTO das outras camadas. Procurar «fontes para
o Radar» contaria a mesma fonte duas vezes e daria a ilusao de que o Radar tem
materia-prima propria. Nao tem. Por isso aqui nao ha lista de fontes do Radar:
ha uma matriz de ENTRADAS, e cada entrada aponta para a camada que a produz.

Consequencia dura: o Radar nunca e' melhor do que a sua entrada mais fraca. Se
VOICES tem 0 de 17 com regiao, o cruzamento «voz + janela na mesma regiao» nao
pode existir — por mais bem escrito que o Radar esteja.

E A CONTA DE REGIAO NAO E' CONTA DE FONTE
-----------------------------------------
REGION_GAPS pergunta «existe fonte que enche o buraco CRITICO nesta regiao?».
Nao pergunta «quantas fontes tem esta regiao». Dez fontes de imprensa numa
regiao nao enchem uma fase fenologica.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-gap")
DEEP = Path("C:/Users/London1/AppData/Local/Temp/sintonia-italy-deep")

from italy_gap_needs import NECESSIDADES, FERRAMENTAS      # noqa: E402
from italy_gap_auditoria import AUDITORIA                  # noqa: E402
from italy_gap_novas_fontes import TODAS as NOVAS          # noqa: E402

REGIOES = ["Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
           "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche",
           "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana",
           "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"]

# ── AS 10 CULTURAS DAS 29 JANELAS, E A COLISAO DE LINGUA QUE ESTRAGOU A CONTA ──
# Primeira versao contava «Maize = 11» e «Grapevine = 12». O bug: as minhas
# descricoes de fonte estao em PORTUGUES, e as palavras de cultura em ITALIANO.
#   «mais» = milho em italiano, e «mais» = more em portugues -> casou em tudo
#   «riso» = arroz em italiano, e «riso» esta dentro de «precisos»
#   «mela» = maca em italiano, e esta dentro de «problema»
# Correcao: fronteira de palavra obrigatoria, e a busca so nos campos que
# carregam texto italiano (NOME, EXEMPLO_REAL), nunca na minha prosa.
CULTURAS = {"Apple": [r"melo\b", r"mele\b", r"pero\b", r"melo/pero"],
            "Durum Wheat": [r"grano duro", r"frumento duro"],
            "Grapevine": [r"\bvite\b", r"viticol", r"\buva\b", r"vigneto",
                          r"vitigno", r"vendemmia"],
            # ⚠️ «mais» E' INUTILIZAVEL COMO PALAVRA-CHAVE AQUI. Milho em
            # italiano escreve-se «mais», e «mais» em portugues aparece em
            # todo o lado. Com fronteira de palavra e uma lista de excecoes,
            # ainda casou seis vezes — «retoma vegetativa mais tardia», «mais
            # ~300 leituras», «vai mais longe». Fica so o sinonimo sem colisao.
            "Maize": [r"granoturco", r"zea mays"],
            "Olive": [r"olivo", r"olivicol", r"\boliva"],
            "Rice": [r"\briso\b", r"risicol", r"enterisi"],
            "Soybean": [r"\bsoia\b"],
            "Sugar Beet": [r"barbabietol", r"\babsi\b"],
            "Tomato": [r"pomodoro"],
            "Wheat": [r"frumento", r"grano tenero"]}

# ─────────────────────────────────────────────────────────────────────────────
# 1 · MATRIZ DE ENTRADAS DO OPPORTUNITY RADAR
# ─────────────────────────────────────────────────────────────────────────────
# `AVAILABLE` le-se no casco; `SOURCE_COVERAGE` le-se na auditoria; as duas nao
# sao a mesma pergunta e e' por isso que estao em colunas separadas.
RADAR_ENTRADAS = [
 dict(INPUT_LAYER="JANELA DE CULTURA (cultura × problema × regiao × data)",
      CAMADA_DE_ORIGEM="WINDOWS",
      AVAILABLE="PARCIAL — 29 janelas existem, mas 0/29 com fase observada e "
                "0/29 com fonte anotada",
      SOURCE_COVERAGE="STRONG — 4 produtores com BBCH declarado (RRN, Marche, "
                      "CAAR, Veneto)",
      GEOGRAPHIC_COVERAGE="9 de 20 regioes no casco; as fontes novas cobrem "
                          "Veneto, Liguria, Toscana, Marche, Calabria, "
                          "Emilia, Lombardia + nacional",
      FRESHNESS="semanal na campanha",
      GAP="o dado existe sem procedencia e sem observacao. Nao e' falta de "
          "fonte: e' falta de ligar a fonte ao registo."),
 dict(INPUT_LAYER="LIGACAO PRODUTO × PROBLEMA",
      CAMADA_DE_ORIGEM="PORTFOLIO",
      AVAILABLE="NAO — PRODUCT_MATCHES 0/29",
      SOURCE_COVERAGE="NAO_E_GAP_DE_FONTE — os dois lados ja estao em casa "
                      "(219 produtos, 29 janelas)",
      GEOGRAPHIC_COVERAGE="nacional (registo do Ministero)",
      FRESHNESS="diaria no registo",
      GAP="e' um JOIN interno. Nenhuma fonte italiana publica esta ligacao, e "
          "nenhuma coleta a resolve."),
 dict(INPUT_LAYER="SINAL DE CONCORRENTE na mesma cultura/problema",
      CAMADA_DE_ORIGEM="COMPETITORS",
      AVAILABLE="PARCIAL — atividades existem; regiao nao",
      SOURCE_COVERAGE="STRONG para produto, cultura, alvo, pessoa e conteudo "
                      "tecnico; WEAK para regiao",
      GEOGRAPHIC_COVERAGE="Emilia-Romagna e Veneto por evento; o resto exige "
                          "vigiar o sitio de cada empresa",
      FRESHNESS="por evento — 6 eventos datados em 2026",
      GAP="⚠️ o cruzamento «concorrente ativo NESTA regiao» nao e' possivel: "
          "nao existe calendario nacional de jornadas por regiao. O local do "
          "evento nao e' a regiao da atividade."),
 dict(INPUT_LAYER="VOZ DE CAMPO na mesma cultura/problema",
      CAMADA_DE_ORIGEM="VOICES",
      AVAILABLE="NAO — 0/17 com regiao, 0/17 com papel, 0/17 com data",
      SOURCE_COVERAGE="STRONG_MAS_TROCA_A_VOZ — o boletim tecnico assinado tem "
                      "regiao, papel e data; nao e' o produtor a falar",
      GEOGRAPHIC_COVERAGE="por zona homogenea (ARSAC: 8 zonas) e por "
                          "provincia (CAAR, LaMMA)",
      FRESHNESS="semanal na campanha",
      GAP="⚠️ ESTE E' O PONTO MAIS FRACO DO RADAR. Sem regiao nem data nas "
          "vozes, o cruzamento «voz + janela na mesma regiao e no mesmo "
          "momento» e' impossivel por construcao. E encher com boletim "
          "tecnico responde a outra pergunta."),
 dict(INPUT_LAYER="MERCADO da mesma cultura",
      CAMADA_DE_ORIGEM="MARKET",
      AVAILABLE="PARCIAL — preco sim; producao, area, rendimento e stocks nao",
      SOURCE_COVERAGE="STRONG para producao/area/rendimento (ISTAT), "
                      "comercio externo e custo de insumo; WEAK para stocks",
      GEOGRAPHIC_COVERAGE="nacional com regiao, provincia e zona altimetrica",
      FRESHNESS="mensal (ISTAT, ISMEA); semanal nas borse merci",
      GAP="⚠️ a zona altimetrica do ISTAT nao e' a zona agronomica do "
          "boletim. Cruzar mercado com janela exige reconciliar duas "
          "geografias que ninguem reconciliou."),
 dict(INPUT_LAYER="CIENCIA da mesma cultura/problema",
      CAMADA_DE_ORIGEM="SCIENCE",
      AVAILABLE="PARCIAL — identidade, autor e tema sim; local, metodo e "
                "resultado nao",
      SOURCE_COVERAGE="STRONG para identidade/autor/tema; WEAK para local e "
                      "metodo; NO para ensaio de registo",
      GEOGRAPHIC_COVERAGE="nacional e internacional (OpenAlex)",
      FRESHNESS="continua (OpenAlex); anual (atas)",
      GAP="⚠️ o ensaio de campo com resultado NAO E' GAP DE FONTE, e' GAP DE "
          "ACESSO: os dados GEP sao propriedade de quem encomenda e nao sao "
          "publicados."),
 dict(INPUT_LAYER="VOCABULARIO UNICO de cultura entre as camadas",
      CAMADA_DE_ORIGEM="(transversal — nenhuma)",
      AVAILABLE="NAO SEI",
      SOURCE_COVERAGE="NAO_E_GAP_DE_FONTE",
      GEOGRAPHIC_COVERAGE="—",
      FRESHNESS="—",
      GAP="o nome da cultura chega em seis vocabularios que nao se falam (ja "
          "registado na memoria do projeto). Sem um vocabulario, o "
          "cruzamento falha em silencio: «vite» e «Grapevine» nao se "
          "encontram, e o Radar nao acusa erro — acusa ausencia."),
 dict(INPUT_LAYER="IDENTIDADE UNICA de caso entre as camadas",
      CAMADA_DE_ORIGEM="(transversal — nenhuma)",
      AVAILABLE="NAO SEI",
      SOURCE_COVERAGE="NAO_E_GAP_DE_FONTE",
      GEOGRAPHIC_COVERAGE="—",
      FRESHNESS="—",
      GAP="sem identificador comum, duas camadas a falar do mesmo caso nao "
          "sabem que falam do mesmo caso."),
]


def _regioes_de(texto):
    t = (texto or "").lower()
    achadas = set()
    for r in REGIOES:
        if r.lower() in t:
            achadas.add(r)
    # nomes que o texto usa e nao batem com o nome oficial
    for chave, r in (("alto adige", "Trentino-Alto Adige"),
                     ("bolzano", "Trentino-Alto Adige"),
                     ("trento", "Trentino-Alto Adige"),
                     ("brescia", "Lombardia"), ("treviso", "Veneto"),
                     ("belluno", "Veneto"), ("bologna", "Emilia-Romagna"),
                     ("modena", "Emilia-Romagna"), ("reggio emilia", "Emilia-Romagna"),
                     ("emilia", "Emilia-Romagna"), ("siena", "Toscana"),
                     ("livorno", "Toscana"), ("grosseto", "Toscana"),
                     ("locorotondo", "Puglia"), ("friuli", "Friuli-Venezia Giulia")):
        if chave in t:
            achadas.add(r)
    return achadas


def matriz_regiao():
    """Para cada regiao: ha fonte REGIONAL que enche o buraco CRITICO da fenologia?

    ⚠️ FONTE NACIONAL NAO E' COBERTURA REGIONAL, E A PRIMEIRA VERSAO DISTO
    DIZIA QUE ERA. Contando o nacional como se cobrisse cada regiao, as vinte
    regioes sairam «COBERTA» — 20 de 20, incluindo Molise e Valle d'Aosta, onde
    esta missao nao achou nada. E' a mesma familia de erro do matcher generoso:
    encher a coluna e chamar-lhe resultado.

    Agora as duas contas vivem em colunas separadas. O ESTADO decide-se pela
    REGIONAL; a nacional fica escrita ao lado, para nao se perder.
    """
    antes = defaultdict(set)
    p = DEEP / "LINHAS-FINAL.json"
    if not p.exists():
        # Zero silencioso e' pior do que erro. A memoria do projeto tem um
        # registo proprio para isto («o zero que vem com HTTP 200»).
        raise SystemExit(
            f"!! FALTA A BASE DA MISSAO ANTERIOR: {p}\n"
            "   Sem ela, a coluna ANTES sairia 0 em todas as regioes e a "
            "matriz diria que esta missao descobriu tudo. Nao se publica "
            "«antes=0» sem ter medido o antes.")
    for lin in json.loads(p.read_text(encoding="utf-8")):
        if lin.get("QUALITY_CLASS") not in ("A", "B"):
            continue
        txt = " ".join(str(lin.get(k, "")) for k in
                       ("NAME", "OWNER", "TOPICS",
                        "WHAT_CAN_THIS_SOURCE_TELL_SINTONIA", "WHY_USEFUL"))
        # so conta quem fala de fenologia ou de boletim fitossanitario
        if not re.search(r"fenolog|bbch|bollettin|fitosanitar", txt, re.I):
            continue
        # ⚠️ A REGIAO SAI SO DO CAMPO `REGION`, NUNCA DA PROSA. Lendo a prosa,
        # o Lazio aparecia em 32 fontes — porque paginas que MENCIONAM o Lazio
        # entravam como fontes DO Lazio. Uma delas chamava-se «Toscana
        # Notizie». Mencionar nao e' ser de la.
        for r in _regioes_de(str(lin.get("REGION", ""))):
            antes[r].add(lin.get("NAME", "")[:40])

    depois = {r: set(v) for r, v in antes.items()}
    nacionais = []
    for f in NOVAS:
        if not any("FASE FENOLOGICA" in a or "OBSERVACAO DE CAMPO" in a
                   or "Desvio fenologico" in a for a in f["ALIMENTA"]):
            continue
        alvo = _regioes_de(f["AMBITO"] + " " + f["DONO"] + " " + f["EXEMPLO_REAL"])
        if not alvo and "NACIONAL" in f["AMBITO"].upper():
            nacionais.append(f["NOME"][:44])
            continue
        for r in alvo:
            depois.setdefault(r, set()).add(f["NOME"][:40] + " [NOVA]")

    linhas = []
    for r in REGIOES:
        a = len(antes.get(r, ()))
        novas = sorted(x for x in depois.get(r, ()) if x.endswith("[NOVA]"))
        d = a + len(novas)
        linhas.append(dict(
            REGIAO=r, ANTES_REGIONAL=a, NOVAS_REGIONAIS=len(novas),
            DEPOIS_REGIONAL=d,
            FONTES_NACIONAIS_QUE_TAMBEM_SERVEM=len(nacionais),
            ESTADO=("COBERTA" if d >= 2 else "FRACA" if d == 1
                    else "SEM FONTE REGIONAL"),
            FONTES_NOVAS=" · ".join(x.replace(" [NOVA]", "") for x in novas) or "—",
            NOTA=("" if d else
                  "nenhuma fonte REGIONAL de fenologia, antes ou depois. As "
                  f"{len(nacionais)} fontes nacionais falam do pais, nao "
                  "desta regiao — e a fenologia muda com altitude e "
                  "distancia ao mar.")))
    return linhas, nacionais


def matriz_cultura(janelas_por_cultura):
    """Para cada cultura das 29 janelas: ha fonte nova que a NOMEIE em italiano?

    A busca so nos campos com texto italiano — NOME, EXEMPLO_REAL, DONO. A
    prosa portuguesa de PRODUZ fica de fora, porque foi ela que produziu
    «Maize = 11» na primeira versao.
    """
    linhas = []
    for cult, padroes in sorted(CULTURAS.items()):
        quem = []
        for f in NOVAS:
            it = f["NOME"] + " || " + f["EXEMPLO_REAL"] + " || " + f["DONO"]
            if any(re.search(p, it, re.I) for p in padroes):
                quem.append(f["NOME"][:44])
        linhas.append(dict(
            CULTURA=cult,
            JANELAS_NO_CASCO=janelas_por_cultura.get(cult, 0),
            FONTES_NOVAS_QUE_A_NOMEIAM=len(quem),
            QUEM=" · ".join(quem[:4]) or "—",
            ESTADO=("NOMEADA" if quem else "NAO NOMEADA POR NENHUMA FONTE NOVA"),
            NOTA=("" if quem else
                  "⚠️ a busca dirigida NAO cobriu esta cultura — foi a "
                  "vite, ao olivo, aos agrumes e aos frutos de pomo. Isto "
                  "nao e' ausencia de fonte em Italia: e' ausencia de "
                  "busca, e a diferenca importa para quem herdar a lista.")))
    return linhas


def matriz_social():
    """As vozes por regiao — e a conta que mostra por que o Radar nao cruza."""
    ing = TRAB / "DADO-MEDIDO.json"
    med = json.loads(ing.read_text(encoding="utf-8")) if ing.exists() else {}
    v = med.get("ING.VOICES", {})
    campos = v.get("CAMPOS", {})
    linhas = []
    for c in ("REGION", "ROLE", "DATE", "PERSON", "CROP", "ISSUE", "PLATFORM"):
        k = campos.get(c, {})
        linhas.append(dict(
            CAMPO_DA_VOZ=c, REGISTOS=v.get("REGISTOS", 0),
            CHEIO=k.get("cheio", 0), PCT=f'{k.get("pct_cheio", 0)}%',
            NAO_SEI=k.get("NAO_SEI", 0),
            CONSEQUENCIA={
             "REGION": "sem isto, «voz do Veneto» nao existe",
             "ROLE": "sem isto, produtor e amador contam igual",
             "DATE": "sem isto, nao ha «esta semana»",
             "PERSON": "",
             "CROP": "", "ISSUE": "", "PLATFORM": ""}.get(c, "")))
    return linhas


def matriz_pessoas():
    """Pessoas nomeadas que a missao achou — por papel, nao por alcance."""
    return [
     dict(PAPEL="tecnico de empresa concorrente", QUANTAS=7,
          NOMES="Mattia Fumagalli (Syngenta) · Sara Ciofini (Corteva) · "
                "Mirko Valente (BASF) · Silvano Locardi (Bayer) · "
                "Marco Pravisano (Syngenta) · Marco Grandin (Bayer) · "
                "Giorgio Fioretti (BASF)",
          ONDE="convegno de Bolonha 19/02/2026 · Forum Fitoiatrico CondifesaTVB",
          ALIMENTA="COMPETITORS · PESSOA do concorrente (quem fala por ele)",
          NOTA="passou de NO_SOURCE a STRONG. ⚠️ a ADAMA esta na lista de "
               "participantes do Forum — excluir a propria casa do calculo"),
     dict(PAPEL="responsavel de servico publico", QUANTAS=3,
          NOMES="Bruno Faraglia (chefe do Servizio Fitosanitario Centrale) · "
                "Maria Rita Rapagnani (Ministero della Salute) · "
                "Dario Bond (Assessore Agricoltura, Regione Veneto)",
          ONDE="protezionedellepiante.it · convegno de Bolonha · Forum Fitoiatrico",
          ALIMENTA="FUTURE · PRAGA OU DOENCA EMERGENTE (primeira deteccao)",
          NOTA="identidade institucional, verificavel na propria casa"),
     dict(PAPEL="tecnico de associacao / sociedade", QUANTAS=2,
          NOMES="Alessandra Moccia (IBMA Global) · Matteo Colombo "
                "(European Precision Application Task Force, por Corteva)",
          ONDE="convegno de Bolonha · Giornate Fitopatologiche 2026",
          ALIMENTA="COMPETITORS · CONTEUDO TECNICO do concorrente",
          NOTA="fala por associacao, nao por empresa — papel diferente"),
     dict(PAPEL="produtor agricola com regiao e data", QUANTAS=0,
          NOMES="—",
          ONDE="—",
          ALIMENTA="VOICES · REGIAO/PAPEL/DATA da voz de campo",
          NOTA="⚠️ ZERO. A busca dirigida a «agronomo que publica boletim "
               "proprio» devolveu a conclusao de que NAO EXISTE lista central "
               "desses profissionais. E o que se achou foram tecnicos "
               "institucionais, nao produtores. O buraco de VOICES nao "
               "fechou."),
    ]


def _janelas_por_cultura():
    """Le as 29 janelas canonicas e conta quantas por cultura."""
    med = json.loads((TRAB / "DADO-MEDIDO.json").read_text(encoding="utf-8"))
    n = med.get("CAN.windows", {}).get("REGISTOS", 0)
    # a medicao guarda contagem de campos, nao os valores. As culturas foram
    # lidas do casco a mao: 10 culturas em 29 janelas.
    return {"Apple": 3, "Durum Wheat": 3, "Grapevine": 5, "Maize": 3,
            "Olive": 3, "Rice": 2, "Soybean": 2, "Sugar Beet": 2,
            "Tomato": 3, "Wheat": 3} if n == 29 else {}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    regiao, nacionais = matriz_regiao()
    saida = {"RADAR": RADAR_ENTRADAS, "REGION": regiao,
             "REGION_NACIONAIS": nacionais,
             "CROP": matriz_cultura(_janelas_por_cultura()),
             "SOCIAL": matriz_social(), "PEOPLE": matriz_pessoas()}
    (TRAB / "MATRIZES.json").write_text(
        json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")

    print("RADAR — entradas:", len(RADAR_ENTRADAS))
    for e in RADAR_ENTRADAS:
        print(f"  {e['INPUT_LAYER'][:44]:44s} available={e['AVAILABLE'][:16]:16s}"
              f" <- {e['CAMADA_DE_ORIGEM']}")
    print()
    print(f"REGIAO — buraco critico da fenologia  "
          f"(+{len(nacionais)} fontes NACIONAIS, contadas a parte):")
    for l in saida["REGION"]:
        print(f"  {l['REGIAO']:24s} antes={l['ANTES_REGIONAL']:2d} "
              f"novas={l['NOVAS_REGIONAIS']:2d} depois={l['DEPOIS_REGIONAL']:2d}"
              f"  {l['ESTADO']}")
    print("  estado:", dict(Counter(l["ESTADO"] for l in saida["REGION"])))
    print()
    print("CULTURA:")
    for l in saida["CROP"]:
        print(f"  {l['CULTURA']:14s} janelas={l['JANELAS_NO_CASCO']}  "
              f"fontes={l['FONTES_NOVAS_QUE_A_NOMEIAM']:2d}  {l['ESTADO']}")
    print()
    print("SOCIAL — os tres campos que faltam:")
    for l in saida["SOCIAL"][:3]:
        print(f"  {l['CAMPO_DA_VOZ']:8s} {l['CHEIO']}/{l['REGISTOS']} = {l['PCT']}"
              f"   {l['CONSEQUENCIA']}")
    print()
    print("PESSOAS:", {p["PAPEL"]: p["QUANTAS"] for p in saida["PEOPLE"]})
    print(f"\ngravado: {TRAB / 'MATRIZES.json'}")


if __name__ == "__main__":
    main()
