#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A VARREDURA POR REGRA — para o que a leitura a mao nao alcancou.

A auditoria manual leu 155 linhas. Sobraram ~224 na classe B que ninguem abriu,
e deixa-las como B seria dizer que sao boas sem ninguem ter olhado. Mas inventar
um julgamento para cada uma tambem nao serve.

Entao aqui aplico REGRAS ESCRITAS, cada uma nascida de um caso que eu vi de
verdade na auditoria manual. Regra e auditavel: da-se para discordar dela,
apontar a linha e mudar. Palpite nao.

Cada linha tocada leva a marca AUDITADA_POR_REGRA e o numero da regra — para
que ninguem confunda isto com leitura humana.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

TRABALHO = Path(sys.argv[1] if len(sys.argv) > 1
                else "C:/Users/London1/AppData/Local/Temp/sintonia-italy-deep")

# ── R1 · quinta ou cantina individual ────────────────────────────────────
# Nasceu de: caprili.it, francopacenti.it, ausoniawines.com. Uma empresa
# agricola nao e fonte: ela tem o facto, mas nao o publica.
R1_TITULO = ["brunello di montalcino", "azienda vitivinicola", "azienda agricola",
             "cantina ", "cantine ", "winery", "tenuta ", "viticoltori",
             "vendita diretta vino", "artigiani del brunello", "wine resort"]
R1_HOST = ["montalcino", "vini", "wines", "cantina", "tenuta"]

# ── R2 · midia generalista nacional ──────────────────────────────────────
# Nasceu de: repubblica.it, avvenire.it, adnkronos.com.
R2_HOST = ["corriere.it", "lastampa.it", "lanazione.it", "ilfoglio.it",
           "ilriformista.it", "quotidiano.net", "askanews.it", "ansa.it",
           "ilsole24ore.com", "repubblica.it", "avvenire.it", "adnkronos.com",
           "africaeaffari.it", "esgnews.it", "qualenergia.it", "aostasera.it",
           "eunews.it", "ilrestodelcarlino.it", "lospiffero.com"]

# ── R3 · instituicao fora do assunto agricola ────────────────────────────
# Nasceu de: inail.it, cultura.gov.it, aics.gov.it, calabriasuap.it.
R3_HOST = ["anci.it", "provinceditalia.it", "regioni.it", "lavoro.gov.it",
           "italiasemplice.gov.it", "forumpa.it", "opportunitaly.gov.it",
           "edisu.pv.it", "ecmunipv.it", "sba.unifi.it", "sns.it",
           "corpoeuropeodisolidarieta.net", "foncoop.coop",
           "fondazionecaritro.it", "agcm.it", "ogs.it", "greenpeace.org",
           "legambiente.it", "asvis.it", "ases-ong.org", "generali.it",
           "marcominghetti.com", "aracneeditrice.eu", "consisto.it",
           "batcenter.it", "csrpiemonte.it", "comune.", "in-lombardia.it",
           "agriturismiregionecalabria.it", "parchidelducato.it",
           "saporidivallecamonica.it", "protezionecivilecalabria.it",
           "damatecnopolo.it", "moliseacque.com", "koelnmesse.it",
           "ecosanfra.it", "tecnoedizioni.com", "alimentibevande.it",
           "italianfoodnews.com", "beverfood.com", "vitaevino.org",
           "associazioneflavor.it", "benvenutobrunello.com",
           "autunnopavesedoc.it", "thinkfresh.it", "alimentifunzionali.it"]

# ── R4 · pecuaria e veterinaria, sem cultura vegetal ─────────────────────
# Nasceu de: allevaweb.it, 3tres3.com, aral.lom.it.
R4_HOST = ["izsvenezie.it", "istitutospallanzani.it", "arientigp.it",
           "fratelliborello.com", "agricoleforte.com", "ruminantia.it",
           "produttoriarborea.it", "formaggiosilter.it", "vinideltrentino.com"]
R4_TITULO = ["zootecni", "stalle", "bovine", "mangimi", "allevamento",
             "zooprofilattico", "formaggio", "latte"]

# ── R5 · edicao noutro pais do mesmo dono ────────────────────────────────
# Nasceu de: freshplaza.es/.fr/.com, biogard.es, hortidaily.es.
R5_HOST = ["freshplaza.de", "freshplaza.es", "freshplaza.fr", "freshplaza.com",
           "hortidaily", "agf.nl", "biogard.es"]

# ── R6 · fabricante de maquina ou equipamento ────────────────────────────
# Nasceu de: sormagroup.com, pieralisi.com, affaretrattore.it. Fica em C: e
# util para ler a cadeia, nao para ler o campo.
R6_HOST = ["unitec-group.com", "deatechsrl.it", "etgsrl.it", "tecnelab.it",
           "federunacoma.it", "assomao.it", "comacomp.it", "assoidrotech.it",
           "greenexta.com"]

# ── R7 · feira e evento ──────────────────────────────────────────────────
R7_HOST = ["fieragricola.it", "agrilevante.eu", "macfrut.com", "eima.it",
           "simei.it", "interpoma.it", "sana.it", "tuttofood.it",
           "enovitisincampo.it", "umbriafiere.it", "luvfiera.com",
           "fiereparma.it", "biocontrolconference.com", "cibuslink.it"]

# ── R8 · sitio de projeto, com data de fim ───────────────────────────────
# Nasceu de: adam-disaa.eu, progettonovagro.it. Projeto congela quando o
# financiamento acaba, e um endereco congelado engana quem o herda.
R8_PADRAO = re.compile(r"(^|\.)life[a-z]*\.eu$|progetto|project|^pastoralp|"
                       r"^paluqdp|^soilless|^covercrop|^demo-farm|^omicron|"
                       r"^vitaval|^phen-italy|psrinnovazione|^lifegrace|"
                       r"^lifeprepair", re.I)

# ── R9 · marca ou produto agricola a venda ───────────────────────────────
R9_HOST = ["antonioruggiero.com", "coppolapatate.it", "lanormanna.it",
           "caiarl.com", "melapiu.com", "oleumsicilia.com", "donnalia.com",
           "chiusagrossa.it", "val3ciuta.it", "psbsementi.it",
           "lagnascogroup.it", "solcomaggiore.com", "caviro.com"]

# ── SUBIDAS · fontes que a leitura rapida mostrou serem mais do que B ────
# Cada uma com o motivo, porque subir sem motivo e o mesmo erro ao contrario.
SUBIR_A = {
    "agrea.it": "Agrea Centro Studi: centro privado de pesquisa e experimentacao PARA A PROTECAO DAS PLANTAS, com ensaios proprios. E dono de dado de eficacia — a classe de fonte mais rara e mais util para T3.",
    "lamma.toscana.it": "Consorzio LaMMA: o servico meteorologico da Toscana, com previsao propria e serie de dados. Dono do dado de T2 para uma das regioes agricolas mais importantes.",
    "droughtcentral.it": "Drought Central / Osservatorio Siccita: dado proprio e recorrente sobre seca — T2, e um tema que o acervo italiano quase nao cobria.",
    "www3.beratungsring.org": "as Circolari do Sudtiroler Beratungsring: ~50 por ano so para maca e 15 para vinha. E o conselho tecnico que chega ao produtor do Alto Adige, escrito por quem vai ao campo.",
    "regflor.it": "Istituto Regionale per la Floricoltura (Sanremo): laboratorio oficial de analise fitopatologica E instituto de pesquisa em floricultura. Dono do dado, e cobre uma cultura (flor) que o acervo nao tinha.",
    "caa.cia.it": "Centro Assistenza Agricola da CIA: a rede que preenche o quaderno di campagna do produtor. E o ponto onde o dado administrativo e o dado de campo se encontram — T7 no sentido mais literal.",
    "agrometeorologia.it": "AIAM, Associazione Italiana di AgroMeteorologia: a sociedade cientifica de agrometeorologia italiana, editora do Italian Journal of Agrometeorology.",
}
SUBIR_B_EXPLICITO = {
    "ediacompany.it": "e a casa editora de L Informatore Agrario, a revista tecnica agricola italiana mais antiga. O acervo tem informatoreagrario.it; este e o dominio da editora — mesmo dono.",
    "arsial.it": "ARSIAL: a agencia regional do Lazio, com pagina propria de boletins de difesa integrata. Ja conhecida no acervo.",
    "regione.molise.it": "a pagina de Bollettini e Comunicati fitosanitari do Molise — a rota T3 de uma das regioes mais fracas de Italia. Ja conhecida no acervo como host.",
    "sar.sardegna.it": "Servizio Agrometeorologico Regionale da Sardenha (ARPAS): 300+ estacoes e bollettino fenologico proprio.",
    "nimbus.it": "Nimbus / Societa Meteorologica Italiana: serie climatica propria e analise. T2.",
    "protezionedellepiante.it": "SIPaV, a sociedade italiana de patologia vegetal: congressos, documentos tecnicos oficiais. Ja no acervo.",
    "georgofili.info": "notiziario da Accademia dei Georgofili. Ja no acervo.",
    "soihs.it": "SOI, Societa di Ortoflorofrutticoltura Italiana. Ja no acervo.",
    "sisef.org": "SISEF, sociedade italiana de silvicultura e ecologia florestal.",
    "aissa.it": "AISSA: a associacao que junta TODAS as sociedades cientificas agrarias italianas. Porta de entrada para achar as outras.",
    "peritiagrari.it": "Collegio Nazionale dei Periti Agrari: a outra ordem profissional de campo, ao lado dos agronomos.",
    "phen-italy.it": "Italian Plant Phenotyping Network: rede nacional de fenotipagem. Ciencia aplicada.",
    "spigolatureagronomiche.it": "Spigolature Agronomiche: revista de ciencias agrarias com publicacao propria.",
    "storiaagricoltura.it": "Rivista di Storia dell Agricoltura: serie longa, util para contexto, nao para sinal de campo.",
    "passioneinverde.edagricole.it": "portal tecnico da Edagricole com conteudo de defesa (ex. mosca da azeitona). Mesmo dono de terraevita.edagricole.it.",
    "oipomodorocentrosud.it": "Organizzazione Interprofessionale do tomate do Centro-Sul: acordos de preco e quantidade. T10 com dado proprio.",
    "origin-italia.it": "Origin Italia: a associacao dos consorcios de tutela DOP/IGP. Porta para achar os consorcios um por um.",
    "valoritalia.it": "Valoritalia: o maior organismo de certificacao de vinho DOP/IGP italiano. Sabe quem certifica o que.",
    "apofruit.it": "Apofruit: uma das maiores cooperativas hortofruticolas italianas. Ja no acervo.",
    "apoconerpo.com": "Apoconerpo: OP da Emilia com 1.200 ha de tomate resistente. Ja no acervo.",
    "fondazionecrpa.it": "Fondazione CRPA Studi Ricerche: pesquisa aplicada. Mesmo dono do crpa.it, ja no acervo.",
    "cersaa.it": "CeRSAA Albenga: centro de experimentacao e assistencia agricola da Camera di Commercio de Savona, e laboratorio de autocontrolo.",
    "anbiveneto.it": "ANBI Veneto: uniao regional dos consorcios de bonifica.",
    "erapraveneto.it": "E.R.A.P.R.A. Veneto: ente regional de formacao profissional agricola.",
    "clusterbiologicoveneto.it": "Consorzio BioInnova Veneto: cluster do biologico regional.",
    "clusteragrifood.it": "CL.A.N., o cluster agroalimentar nacional.",
    "agritechcenter.it": "Agritech Center: centro nacional PNRR de pesquisa agricola.",
    "federbioservizi.it": "FederBio Servizi: braco tecnico do biologico italiano.",
    "regione.campania.it": "portal institucional da Campania — a rota agricola util e agricoltura.regione.campania.it, noutra linha.",
    "regione.puglia.it": "portal institucional da Puglia — idem.",
    "regione.umbria.it": "portal da Umbria, com a pagina de bollettini fitosanitari. Ja no acervo.",
    "regione.taa.it": "Regione autonoma Trentino-Alto Adige: nivel regional; as fontes tecnicas reais sao as provincias (Trento e Bolzano).",
}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = TRABALHO / "AUDIT.json"
    audit = json.loads(p.read_text(encoding="utf-8"))
    linhas = json.loads((TRABALHO / "LINHAS-FINAL.json").read_text(encoding="utf-8"))

    alvo = [x for x in linhas
            if x["QUALITY_CLASS"] == "B" and x["RECORD_KIND"] == "SOURCE"
            and not x.get("MANUAL_AUDIT")]
    print(f"B sem leitura humana: {len(alvo)}")

    novas, contagem = {}, Counter()

    def regra(host, titulo):
        h, t = host.lower(), (titulo or "").lower()
        if any(k in h for k in R5_HOST):
            return "REJECT", "R5", ("edicao noutro pais do MESMO dono que o acervo "
                                    "ja tem em .it — URL alternativa nao e fonte nova")
        if any(k in t for k in R1_TITULO) or (
                any(k in h for k in R1_HOST) and "consorzio" not in t and "istituto" not in t):
            return "REJECT", "R1", ("quinta ou cantina individual: tem o facto, nao o "
                                    "publica. Empresa agricola generica nao e fonte")
        if any(h == k or h.endswith("." + k) or k in h for k in R2_HOST):
            return "REJECT", "R2", ("midia generalista nacional: a pagina tem palavras "
                                    "agricolas por acaso, nao redacao tecnica propria")
        if any(k in h for k in R3_HOST):
            return "REJECT", "R3", ("instituicao fora do assunto agricola (autarquia, "
                                    "turismo, banca, ONG generalista, servico publico "
                                    "nao agricola)")
        if any(k in h for k in R4_HOST) or any(k in t for k in R4_TITULO):
            return "C", "R4", ("pecuaria ou veterinaria: fonte possivelmente boa, do "
                               "seu assunto, mas fora do alvo de cultura vegetal")
        if any(k in h for k in R9_HOST):
            return "C", "R9", ("marca ou produto agricola a venda: comunica o produto, "
                               "nao o campo")
        if any(k in h for k in R6_HOST):
            return "C", "R6", ("fabricante de maquina ou equipamento: util para ler a "
                               "cadeia, nao para ler o campo")
        if any(k in h for k in R7_HOST):
            return "C", "R7", ("feira ou evento: T11. Evento nao entrega sinal "
                               "recorrente de campo")
        if R8_PADRAO.search(h):
            return "C", "R8", ("sitio de projeto: tem data de fim. Quando o "
                               "financiamento acaba o endereco congela, e quem o "
                               "herda acredita nele")
        return None, None, None

    for x in alvo:
        host = x["RELATED_OWNER"]
        if host in SUBIR_A:
            novas[host] = {"resultado": "AUDITADA_POR_REGRA · SUBIDA B->A",
                           "classe_final": "A", "nota": SUBIR_A[host]}
            contagem["SUBIDA_A"] += 1
            continue
        if host in SUBIR_B_EXPLICITO:
            novas[host] = {"resultado": "AUDITADA_POR_REGRA · B CONFIRMADA",
                           "classe_final": "B", "nota": SUBIR_B_EXPLICITO[host]}
            contagem["B_CONFIRMADA"] += 1
            continue
        cls, r, motivo = regra(host, x["NAME"])
        if cls:
            novas[host] = {"resultado": f"AUDITADA_POR_REGRA · {r} · B->{cls}",
                           "classe_final": cls,
                           "nota": f"regra {r}: {motivo}"}
            contagem[f"{r}->{cls}"] += 1
        else:
            novas[host] = {"resultado": "AUDITADA_POR_REGRA · nenhuma regra bateu · "
                                        "B MANTIDA SEM LEITURA HUMANA",
                           "nota": ("nenhuma regra de recusa bateu e ninguem abriu esta "
                                    "fonte. A classe B aqui e da MAQUINA, nao de gente. "
                                    "Antes de registar, alguem tem de olhar.")}
            contagem["B_SEM_LEITURA"] += 1

    audit.update(novas)
    p.write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    print(f"regras aplicadas a {len(novas)} hosts")
    for k, v in contagem.most_common():
        print(f"   {k:22s} {v}")
    print(f"AUDIT.json passou a ter {len(audit)} decisoes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
