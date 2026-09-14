#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COBERTURA — para cada necessidade de materia-prima, existe fonte que a entregue?

TRES CONTAS DIFERENTES, E JUNTA-LAS ESCONDE O PROBLEMA
------------------------------------------------------
    1 · o CASCO TEM o dado hoje?          (medido em DADO-MEDIDO.json)
    2 · existe FONTE REGISTADA que o da?  (atlas · 23 fichas)
    3 · existe CANDIDATA que o daria?     (as 217 A/B de 2026-09-14)

Uma necessidade pode ter fonte e nao ter dado (ninguem coletou), ou ter dado e
nao ter fonte rastreavel (as 29 janelas canonicas tem `SOURCE_IDS = []`). Sao
problemas opostos e pedem accoes opostas.

O QUE NAO SE FAZ AQUI
---------------------
Nao se conta numero bruto de fontes. Cinco fontes que republicam o mesmo
comunicado nao sao cinco capacidades — por isso a contagem e por DONO distinto,
e a coluna diz quantos donos distintos, nao quantas linhas.

E o casamento fonte→necessidade e por PALAVRA, o que e' fraco de proposito:
sai uma proposta, marcada `AUTOMATICO`, que a leitura humana confirma ou
derruba. Um modelo a dizer «parece relevante» nao deixa rasto auditavel.
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
import _territorios as _T          # noqa: E402
from italy_gap_needs import NECESSIDADES, FERRAMENTAS  # noqa: E402

TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-gap")
DEEP = Path("C:/Users/London1/AppData/Local/Temp/sintonia-italy-deep")
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"

# ── as palavras que provam que uma fonte entrega aquela materia-prima ─────
# Cada chave e um pedaco de RAW_NEED; os valores sao termos que, aparecendo no
# que a fonte diz produzir, sustentam a proposta de casamento.
PALAVRAS = {
    "fase fenologica": ["fenolog", "bbch", "stadio", "fase", "germogliamento",
                        "fioritura", "invaiatura", "maturazione", "spigatura"],
    "fase do problema": ["monitoraggio", "cattur", "trappol", "volo", "infestazione",
                         "generazione", "soglia"],
    "observacao de campo": ["monitoraggio", "rilievo", "bollettino", "cattur",
                            "osservazione", "rete di monitoraggio", "utm"],
    "janela de monitoriz": ["monitoraggio", "bollettino", "avviso", "allerta"],
    "infestante": ["diserb", "infestant", "malerb", "weed"],
    "ato regulatorio": ["lotta obbligatoria", "ordinanza", "decreto", "disciplinare",
                        "deroga", "prescrizione", "normativa"],
    "produto registado": ["registro", "autorizzat", "fitosanitari", "etichetta",
                          "prodotti fitosanitari"],
    "rastreabilidade": ["bollettino", "registro", "open data", "dati aperti"],
    "area/hectares": ["superfici", "ettari", "produzione", "statistic", "istat",
                      "censimento"],
    "desvio fenologico": ["agrometeo", "fenolog", "stazioni meteo", "gradi giorno"],
    "preco": ["prezz", "quotazion", "listino", "borsa merci", "mercuriale", "cun"],
    "serie de preco": ["listino", "archivio", "serie", "storico", "quotazion"],
    "producao, area": ["produzione", "superfici", "resa", "raccolto", "statistic",
                       "istat", "stima"],
    "stocks": ["giacenz", "stock", "scorte"],
    "importacao": ["import", "export", "commercio estero", "coeweb", "scambi"],
    "custo de insumo": ["costi", "input", "mezzi tecnici", "prezzi dei mezzi"],
    "clima de confianca": ["clima di fiducia", "fiducia", "sentiment", "indagine"],
    "tomate": ["pomodoro", "barbabietol", "melo", "mela"],
    "uva/vinho": ["vino", "uva", "vendemmia", "vitivinicol"],
    "condicao de cultura": ["agrometeo", "meteo", "siccita", "clima", "condizioni"],
    "substancia ativa": ["sostanza attiva", "principio attivo", "substancia"],
    "dose": ["dose", "etichetta", "impiego", "dosaggio"],
    "intervalo de seguranca": ["tempo di carenza", "carenza", "phi", "intervallo"],
    "momento de aplicacao": ["epoca", "impiego", "applicazione", "timing"],
    "mecanismo de acao": ["frac", "hrac", "irac", "meccanismo", "moa", "resistenz"],
    "documento oficial": ["etichetta", "pdf", "documento", "gazzetta", "decreto"],
    "alteracao de autoriz": ["revoca", "modifica", "estensione", "ritiro",
                             "aggiornamento", "autorizzazione"],
    "autorizacao excecional": ["deroga", "eccezional", "articolo 53", "emergenza"],
    "trabalho cientifico": ["ricerca", "pubblicazion", "paper", "rivista",
                            "openalex", "doi", "convegno", "atti"],
    "autor e instituicao": ["ricercator", "docent", "dipartimento", "universit",
                            "orcid", "istituto"],
    "local do estudo": ["prova", "campo sperimentale", "azienda sperimentale",
                        "localita", "parcella"],
    "metodo e resultado": ["prova", "efficacia", "risultati", "sperimentazione",
                           "tesi", "confronto"],
    "resistencia": ["resistenz", "gire", "sirfi", "hrac", "monitoraggio resistenza"],
    "ensaio de campo": ["prove sperimentali", "campo sperimentale", "sperimentazione",
                        "ensaio", "trial", "confronto varietale"],
    "projeto de investig": ["progetto", "gruppo operativo", "psr", "horizon",
                            "pei-agri", "innovarurale"],
    "atividade publica do conc": ["syngenta", "bayer", "basf", "corteva", "fmc",
                                  "upl", "nufarm", "sipcam", "adama", "ascenza",
                                  "concorrente", "agrofarmac"],
    "cultura da atividade": ["coltura", "colture", "crop"],
    "problema/alvo": ["avversita", "target", "parassit", "malatti"],
    "conteudo tecnico do conc": ["webinar", "giornata tecnica", "prova", "field day",
                                 "convegno", "podcast", "video tecnico"],
    "pessoa do concorrente": ["linkedin", "responsabile", "technical manager"],
    "voz de campo": ["agricoltor", "produttor", "youtube", "instagram", "tiktok",
                     "canale", "vlog", "testimonianza"],
    "regiao da voz": ["regione", "provincia", "territorio", "locale"],
    "papel de quem fala": ["agronomo", "tecnico", "consulente", "agricoltore",
                           "dottore agronomo"],
    "canal com exemplo": ["youtube", "instagram", "facebook", "linkedin", "podcast",
                          "canale", "newsletter"],
    "sinal novo": ["nuovo", "prima segnalazione", "emergente", "allerta", "avviso"],
    "praga ou doenca emergente": ["nuovo organismo", "quarantena", "eppo",
                                  "prima segnalazione", "organismo nocivo",
                                  "emergenza fitosanitaria"],
    "pipeline regulatorio": ["efsa", "rinnovo", "valutazione", "approvazione",
                             "sostanza attiva"],
    "mudanca de politica": ["consultazione", "pac", "psr", "green deal", "politica",
                            "strategia"],
    "deslocacao climatica": ["cambiamento climatico", "anomalia", "siccita",
                             "serie climatica", "agrometeo"],
    "relato da rede comercial": ["rete commerciale", "forza vendita", "tsr"],
    "identidade do tecnico": ["tecnico", "agronomo", "consulente", "albo", "ordine"],
    "vocabulario unico": ["catalogo", "nomenclatura", "vocabolario", "sinonimo"],
    "identidade unica de caso": ["identificativo", "id"],
    "entrada:": [],   # as entradas do radar herdam da ferramenta de origem

    # ── VOCABULARIO QUE FALTAVA, e o buraco que ele tapou ──────────────────
    # 17 das 72 necessidades nao casavam com nenhuma chave acima. E a linha
    # `bate = [...] if chaves else []` deixava passar TODA a fonte do
    # territorio quando a lista vinha vazia: «Datas de inicio e fim da janela»
    # recebia 67 donos fortes, entre eles o E-Phy frances e o MAPA espanhol.
    # Lista vazia nao pode significar «serve tudo». Aqui completa-se o que da
    # para completar; o que nao da fica declarado em SEM_PALAVRA_PORQUE.
    "cultura e regiao": ["coltura", "colture", "regione", "provincia",
                         "bollettino", "comprensorio", "zona"],
    "datas de inicio e fim": ["calendario", "periodo", "epoca", "settiman",
                              "bollettino", "validit", "dal .. al"],
    "produto, registo e titular": ["registro", "autorizzazione", "titolare",
                                   "fitosanitari", "etichetta", "n. di registrazione"],
    "cultura e alvo autorizados": ["impiego", "coltura", "avversita", "etichetta",
                                   "autorizzat", "estensione d'impiego"],
    "cultura e problema do trabalho": ["coltura", "avversita", "parassit",
                                       "malatti", "ricerca", "sperimentazione"],
    "produto do concorrente": ["syngenta", "bayer", "basf", "corteva", "fmc",
                               "upl", "nufarm", "sipcam", "adama", "agrofarmac"],
    "regiao da atividade do concorrente": ["regione", "provincia", "giornata tecnica",
                                           "convegno", "field day", "agrofarmac"],
    "registo oficial do produto do concorrente": ["registro", "autorizzat",
                                                  "fitosanitari", "etichetta"],
    "cultura e problema relatados": ["coltura", "avversita", "agricoltor",
                                     "produttor", "canale", "testimonianza"],
}

# ── TRES MOTIVOS DIFERENTES PARA NAO HAVER PALAVRA, E NAO SAO O MESMO ──────
# Juntar os tres daria «sem cobertura» a coisas que nao sao gap de fonte.
SEM_PALAVRA_PORQUE = {
    "Ligacao produto x janela de cultura":
        ("NAO_E_GAP_DE_FONTE", "e um JOIN entre dois dados que a casa ja tem "
         "(219 produtos, 29 janelas). Nenhuma fonte externa resolve: resolve-se "
         "ligando cultura+alvo do rotulo a cultura+problema da janela."),
    "Volume de vozes suficiente para ler um territorio":
        ("NAO_E_PERGUNTA_DE_PALAVRA", "e uma pergunta de QUANTIDADE por regiao, "
         "nao de topico. Responde-se contando vozes por regiao depois de as "
         "qualificar, e a contagem esta em SOCIAL_GAPS."),
    "Volume de sinais suficiente para ser um arquivo":
        ("NAO_E_PERGUNTA_DE_PALAVRA", "idem: quantidade ao longo do tempo. "
         "Um arquivo de sinais mede-se em series, nao em palavras-chave."),
    "IDENTIDADE UNICA de caso entre as camadas":
        ("NAO_E_GAP_DE_FONTE", "e identidade interna do sistema. Nenhum italiano "
         "publica o identificador de caso do SINTONIA."),
    "VOCABULARIO UNICO de cultura entre as camadas":
        ("NAO_E_GAP_DE_FONTE", "e trabalho de vocabulario interno. Ha catalogos "
         "externos que ajudam (EPPO, ISTAT), mas a decisao de qual manda e' da casa."),
}


def chaves_da_necessidade(rn: str):
    r = rn.lower()
    for k, v in PALAVRAS.items():
        if k in r:
            return v
    return []


def porque_sem_palavra(n: dict):
    """Diz por que esta necessidade nao tem palavra-chave — e nunca 'serve tudo'."""
    if n["RAW_NEED"].lower().startswith("entrada:"):
        return ("HERDADO", "entrada do Radar: a materia-prima e' a da ferramenta "
                "de origem, medida na linha dela. Procurar fonte «para o Radar» "
                "seria contar a mesma fonte duas vezes.")
    if n["RAW_NEED"] in SEM_PALAVRA_PORQUE:
        return SEM_PALAVRA_PORQUE[n["RAW_NEED"]]
    return ("MATCHER_MUDO", "nenhuma palavra-chave declarada para esta "
            "necessidade: o casamento automatico nao opina. Precisa de leitura.")


def carregar_atlas():
    """As fichas do atlas: SOURCE_ID, nome, territorio, tipo, verdict."""
    txt = ATLAS.read_text(encoding="utf-8")
    fichas = []
    for m in re.finditer(r"^SOURCE_ID:\s+(\S+)", txt, re.M):
        ini = m.start()
        fim = txt.find("SOURCE_ID:", m.end())
        bloco = txt[ini:fim if fim > 0 else ini + 3000]
        def campo(nome):
            mm = re.search(r"^%s:\s*(.+)$" % nome, bloco, re.M)
            return mm.group(1).strip() if mm else ""
        fichas.append({
            "SOURCE_ID": m.group(1), "NAME": campo("SOURCE_NAME"),
            "OWNER": campo("SOURCE_OWNER"), "TERRITORY": campo("TERRITORY"),
            "COUNTRY": campo("COUNTRY"), "FREQ": campo("UPDATE_FREQUENCY"),
            "VERDICT": campo("VERDICT"), "TOPICS": campo("TOPICS"),
            "CROPS": campo("CROPS"), "URL": campo("URL"),
            "TEXTO": bloco[:2500], "FONTE_DO_POOL": "ATLAS",
        })
    return fichas


def carregar_candidatas():
    p = DEEP / "LINHAS-FINAL.json"
    if not p.exists():
        return []
    L = json.loads(p.read_text(encoding="utf-8"))
    out = []
    for x in L:
        if x.get("QUALITY_CLASS") not in ("A", "B"):
            continue
        out.append({
            "SOURCE_ID": "", "NAME": x.get("NAME", ""),
            "OWNER": x.get("OWNER", ""), "TERRITORY": x.get("TERRITORIES", ""),
            "COUNTRY": x.get("COUNTRY", ""),
            "FREQ": x.get("RECURRING_INFORMATION_POTENTIAL", ""),
            "VERDICT": x.get("QUALITY_CLASS", ""), "TOPICS": x.get("TOPICS", ""),
            "CROPS": x.get("CROPS", ""), "URL": x.get("URL_FINAL") or x.get("URL_DISCOVERED", ""),
            "REGION": x.get("REGION", ""),
            "PROX": x.get("INFORMATION_PROXIMITY", ""),
            "RECORD_KIND": x.get("RECORD_KIND", ""),
            "TEXTO": " ".join(str(x.get(k, "")) for k in
                              ("NAME", "OWNER", "TOPICS", "CROPS", "WHY_USEFUL",
                               "WHAT_CAN_THIS_SOURCE_TELL_SINTONIA", "EVIDENCE")),
            "FONTE_DO_POOL": "CANDIDATA_217",
        })
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    dado = json.loads((TRAB / "DADO-MEDIDO.json").read_text(encoding="utf-8"))
    pool = carregar_atlas() + carregar_candidatas()
    print(f"POOL DE FONTES = {len(pool)}  "
          f"(atlas: {sum(1 for p in pool if p['FONTE_DO_POOL']=='ATLAS')} · "
          f"candidatas A/B: {sum(1 for p in pool if p['FONTE_DO_POOL']=='CANDIDATA_217')})")

    linhas = []
    for n in NECESSIDADES:
        chaves = chaves_da_necessidade(n["RAW_NEED"])
        # FALHA FECHADA: sem palavra, o matcher cala-se — nao aceita tudo.
        motivo_mudo, explica_mudo = (None, "")
        if not chaves:
            motivo_mudo, explica_mudo = porque_sem_palavra(n)
        terr = set(n["TERR"])
        fortes, fracas = [], []
        for p in (pool if chaves else []):
            pterr = set(re.findall(r"T\d{1,2}", p.get("TERRITORY") or ""))
            if not (pterr & terr):
                continue
            t = (p.get("TEXTO") or "").lower()
            bate = [c for c in chaves if c in t]
            if not bate:
                continue
            prox = p.get("PROX") or ("PRIMARY" if p["FONTE_DO_POOL"] == "ATLAS" else "")
            rec = (p.get("FREQ") or "").upper()
            forte = (prox in ("PRIMARY", "NEAR_PRIMARY")
                     and (p["VERDICT"] in ("A", "GREEN", "🟢 GREEN")
                          or "HIGH" in rec or "diar" in rec.lower()
                          or "settiman" in rec.lower()))
            alvo = fortes if forte else fracas
            alvo.append({"NAME": p["NAME"][:70], "OWNER": (p.get("OWNER") or "")[:50],
                         "URL": p.get("URL", "")[:90], "POOL": p["FONTE_DO_POOL"],
                         "PALAVRAS_QUE_BATERAM": bate[:4],
                         "REGION": p.get("REGION", ""), "PROX": prox})
        donos_fortes = len({f["OWNER"] or f["NAME"] for f in fortes})
        donos_fracas = len({f["OWNER"] or f["NAME"] for f in fracas})

        # ── O DADO QUE O CASCO TEM HOJE, lido da medicao e nao de um sim/nao ──
        # A primeira versao disto perguntava «tem dado?» com um regex por `0/N`.
        # Resultado: «OBSERVACAO DE CAMPO · 2/7» respondia SIM, e a necessidade
        # aparecia LOW quando o contrato diz «0/29 have an observed stage».
        # Duas de sete nao e cobertura: e uma amostra.
        medido = n["MEDIDO"]
        # ATENCAO AOS DOIS ZEROS FALSOS, e os dois estavam aqui:
        #   `0%`   casa dentro de `100%`   -> "100% cheios" era lido como vazio
        #   `0/\d+` casa dentro de `10/163` -> "10/163" era lido como zero
        # Com os dois bugs, a contagem de buracos vinha inflada. O lookbehind
        # exige que o zero NAO venha depois de um digito.
        if re.search(r"\bausente\b|zero dado real|SYNTHETIC_DEMO|nao existe|"
                     r"nao tem (coluna|o campo)|(?<!\d)0/\d+|(?<!\d)0%", medido, re.I):
            enchimento = "NENHUM"
        else:
            fracoes = [(int(a), int(b)) for a, b in
                       re.findall(r"(\d+)/(\d+)", medido) if int(b) > 0]
            if fracoes:
                pior = min(a / b for a, b in fracoes)
                enchimento = ("CHEIO" if pior >= 0.9 else
                              "PARCIAL" if pior >= 0.1 else "NENHUM")
            else:
                enchimento = "NAO_SEI"
        tem_dado = {"CHEIO": "SIM", "PARCIAL": "PARCIAL",
                    "NENHUM": "NAO", "NAO_SEI": "NAO SEI"}[enchimento]

        # ── A COBERTURA POR FONTE E' UMA PROPOSTA, NAO UM VEREDITO ──
        # Casar por palavra prova que a fonte FALA do assunto, nunca que ela
        # ENTREGA o campo. Um boletim fitossanitario fala de monitorizacao e
        # pode nao publicar data de observacao nenhuma. Por isso o automatico
        # nunca escreve STRONG: escreve CANDIDATA_A_CONFIRMAR, e a decisao final
        # entra por `AUDITORIA` (leitura humana), ficheiro AUDIT-GAP.json.
        if motivo_mudo:
            # O matcher nao opinou. Dizer NO_SOURCE aqui seria mentir para o
            # lado do alarme; dizer CANDIDATA seria mentir para o lado do
            # conforto. Diz-se o motivo, que e' a unica coisa verdadeira.
            cob = motivo_mudo
        elif donos_fortes >= 1:
            cob = "CANDIDATA_A_CONFIRMAR"
        elif donos_fracas >= 1:
            cob = "CANDIDATA_FRACA_A_CONFIRMAR"
        else:
            cob = "NO_SOURCE"

        # gravidade: o que a ferramenta perde
        central = any(k in n["RAW_NEED"].upper() for k in (
            "FASE FENOLOGICA", "OBSERVACAO DE CAMPO", "PRODUCAO, AREA",
            "DOSE", "INTERVALO DE SEGURANCA", "REGIAO DA VOZ",
            "PAPEL DE QUEM FALA", "DATA DA OBSERVACAO", "ALTERACAO",
            "PRAGA OU DOENCA EMERGENTE", "RASTREABILIDADE",
            "LIGACAO PRODUTO X JANELA", "RELATO DA REDE"))
        # ── A GRAVIDADE SAI DO DADO MEDIDO, nao da contagem de candidatas ──
        # O que decide se a ferramenta consegue responder e o CAMPO preenchido.
        # Ter candidata e' promessa; ter campo e' capacidade.
        if enchimento == "NENHUM" and central:
            sev = "CRITICAL"
        elif enchimento == "NENHUM":
            sev = "HIGH"
        elif enchimento == "PARCIAL" and central:
            sev = "HIGH"
        elif enchimento == "PARCIAL":
            sev = "MEDIUM"
        elif enchimento == "NAO_SEI":
            sev = "MEDIUM"
        else:
            sev = "LOW"
        # e uma necessidade sem NENHUMA candidata sobe um degrau, porque nem
        # promessa existe
        if cob == "NO_SOURCE" and sev in ("MEDIUM", "LOW"):
            sev = "HIGH"
        # o que NAO e' gap de fonte nao entra na fila de procurar fonte: fica
        # com a gravidade do dado, mas com a accao escrita noutro sitio
        if cob == "NAO_E_GAP_DE_FONTE":
            sev = sev if sev == "CRITICAL" else "HIGH"

        linhas.append({**n, "CHAVES": chaves[:6],
                       "MATCHER": cob if motivo_mudo else "PALAVRA",
                       "MATCHER_PORQUE": explica_mudo,
                       "ENCHIMENTO_NO_CASCO": enchimento,
                       "CASCO_TEM_O_DADO": tem_dado,
                       "DONOS_FORTES": donos_fortes, "DONOS_FRACAS": donos_fracas,
                       "COBERTURA": cob, "GAP_SEVERITY": sev,
                       "FONTES_FORTES": fortes[:6], "FONTES_FRACAS": fracas[:4]})

    # ── as ENTRADAS do radar herdam da ferramenta de origem ───────────────
    # Medir a entrada do radar por conta propria daria «NAO SEI» em tudo, e
    # esconderia o que importa: o radar nao e pior nem melhor que a camada que
    # o alimenta. A gravidade dele E' a da pior entrada.
    de_onde = {"janela de cultura": "WINDOWS", "ligacao produto": "PORTFOLIO",
               "sinal de concorrente": "COMPETITORS", "voz de campo": "VOICES",
               "mercado da mesma": "MARKET", "ciencia da mesma": "SCIENCE"}
    ORDEM = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    for l in linhas:
        if l["TOOL"] != "RADAR":
            continue
        alvo = next((t for k, t in de_onde.items() if k in l["RAW_NEED"].lower()), None)
        if not alvo:
            continue
        piores = [x["GAP_SEVERITY"] for x in linhas if x["TOOL"] == alvo]
        if piores:
            pior = max(piores, key=ORDEM.index)
            l["GAP_SEVERITY"] = pior
            l["HERDADA_DE"] = alvo
            l["CASCO_TEM_O_DADO"] = "HERDADO"

    json.dump(linhas, open(TRAB / "COBERTURA.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print()
    print("%-12s %-54s %-22s %-9s %s" % ("TOOL", "RAW_NEED", "COBERTURA",
                                         "GAP", "casco?"))
    for l in linhas:
        print("%-12s %-54s %-22s %-9s %s" % (
            l["TOOL"], l["RAW_NEED"][:54], l["COBERTURA"], l["GAP_SEVERITY"],
            l["CASCO_TEM_O_DADO"]))
    print()
    print("COBERTURA:", dict(Counter(l["COBERTURA"] for l in linhas)))
    print("GRAVIDADE:", dict(Counter(l["GAP_SEVERITY"] for l in linhas)))
    print()
    por_tool = defaultdict(Counter)
    for l in linhas:
        por_tool[l["TOOL"]][l["GAP_SEVERITY"]] += 1
        por_tool[l["TOOL"]]["_n"] += 1
        por_tool[l["TOOL"]]["ench_" + l["ENCHIMENTO_NO_CASCO"]] += 1
    print("%-12s %-4s %s" % ("TOOL", "n", "gravidade  ·  enchimento do dado no casco"))
    for t in FERRAMENTAS:
        c = por_tool[t]
        print("  %-12s %-3d CRITICAL=%d HIGH=%d MEDIUM=%d LOW=%d  ·  "
              "cheio=%d parcial=%d nenhum=%d naosei=%d" % (
                  t, c["_n"], c["CRITICAL"], c["HIGH"], c["MEDIUM"], c["LOW"],
                  c["ench_CHEIO"], c["ench_PARCIAL"], c["ench_NENHUM"],
                  c["ench_NAO_SEI"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
