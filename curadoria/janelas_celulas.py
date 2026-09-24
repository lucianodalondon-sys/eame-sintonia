# -*- coding: utf-8 -*-
"""Celulas da tabela regiao x (FITO, AGROMETEO, CONSORZIO) — P1g, 24/09/2026.

Cada endereco veio de um link numa pagina oficial explorada nesta missao ou nas
anteriores (provas em curadoria/provas-janelas/ e curadoria/provas-pesquisadores/).
REGIOES_SEM_FONTE diz, por celula, o que se procurou e nao se achou.
"""

_SFN = "https://www.protezionedellepiante.it/servizi-fitosanitari-regionali/"
_ASN = "https://www.asnacodi.it/le-sedi-condifesa/"


def _f(regiao, nome, url, de, para_que="bollettini e avvisi di difesa integrata"):
    return {"regiao": regiao, "coluna": "FITO", "nome": nome, "url": url, "de": de, "para_que": para_que}


def _a(regiao, nome, url, de, para_que="bollettini agrometeorologici e fenologia"):
    return {"regiao": regiao, "coluna": "AGROMETEO", "nome": nome, "url": url, "de": de, "para_que": para_que}


def _k(regiao, nome, url):
    return {"regiao": regiao, "coluna": "CONSORZIO", "nome": nome, "url": url, "de": _ASN,
            "para_que": "consorzio di difesa: avvisi agli agricoltori", "tipo": "ORGANIZACAO"}


CELULAS = [
    # Abruzzo
    _f("Abruzzo", "Abruzzo — Servizio fitosanitario", "https://www.regione.abruzzo.it/content/fitosanitario", _SFN),
    _a("Abruzzo", "Abruzzo — Agrometeorologia e agroambiente", "https://www.regione.abruzzo.it/content/agrometeorologia-agroambiente-0", "https://www.regione.abruzzo.it/agricoltura"),
    _k("Abruzzo", "CODIPE — Consorzio di difesa (Abruzzo)", "https://www.codipe.it/"),
    # Basilicata
    _f("Basilicata", "Basilicata — Ufficio fitosanitario regionale", "https://www.regione.basilicata.it/giunta/site/giunta/department.jsp?dep=100049&area=104835&level=1", _SFN),
    _a("Basilicata", "ALSIA Basilicata — agrometeo e assistenza tecnica", "https://www.alsia.it/", "https://www.alsia.it/"),
    _k("Basilicata", "Condifesa Basilicata", "https://www.condifesa-basilicata.it/"),
    # Calabria
    _f("Calabria", "ARSAC — Bollettino agrometeorologico e fitosanitario (agrumi, olivo, vite)", "https://www.arsacweb.it/bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-e-vite/", "https://www.regione.calabria.it/website/organizzazione/dipartimento8/subsite/fitosanitario/"),
    _a("Calabria", "ARSAC — Bollettino agrometeorologico e fitosanitario (agrumi, olivo, vite)", "https://www.arsacweb.it/bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-e-vite/", "https://www.regione.calabria.it/website/organizzazione/dipartimento8/subsite/fitosanitario/"),
    _k("Calabria", "CODIPACAL — Consorzio di difesa Calabria", "https://codipacal.it/"),
    # Campania
    _f("Campania", "Campania — Bollettini fitosanitari 2026", "http://www.agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026.html", "http://www.agricoltura.regione.campania.it/difesa/difesa.html"),
    _f("Campania", "Campania — SIMFITO monitoraggio fitosanitario", "https://simfito.regione.campania.it/", "http://www.agricoltura.regione.campania.it/difesa/difesa.html"),
    _a("Campania", "Campania — Agrometeorologia", "https://agricoltura.regione.campania.it/meteo/agrometeo.htm", "http://www.agricoltura.regione.campania.it/difesa/difesa.html"),
    # Emilia-Romagna
    _f("Emilia-Romagna", "Emilia-Romagna — Bollettini di produzione integrata e biologica", "https://agricoltura.regione.emilia-romagna.it/fitosanitario/difesa-sostenibile/bollettini", "https://agricoltura.regione.emilia-romagna.it/fitosanitario"),
    _a("Emilia-Romagna", "ARPAE — Previsioni agrometeo", "https://www.arpae.it/it/temi-ambientali/meteo/previsioni-meteo/previsioni-agrometeo", "https://www.arpae.it/it/temi-ambientali/meteo"),
    _a("Emilia-Romagna", "ARPAE — Mappe agrometeo settimanali", "https://www.arpae.it/it/temi-ambientali/meteo/dati-e-osservazioni/mappe-settimanali", "https://www.arpae.it/it/temi-ambientali/meteo"),
    _k("Emilia-Romagna", "Condifesa Modena", "https://www.condifesamodena.it/"),
    _k("Emilia-Romagna", "Condifesa Ravenna", "https://www.condifesa.ra.it/"),
    _k("Emilia-Romagna", "Condifesa Emilia", "https://condifesa-emilia.it/"),
    _k("Emilia-Romagna", "Condifesa (condifesa.it)", "https://www.condifesa.it/"),
    # Friuli Venezia Giulia
    _f("Friuli Venezia Giulia", "ERSA FVG — Bollettini di difesa integrata e biologica", "http://www.ersa.fvg.it/cms/aziende/in-formazione/Bollettini/index.html", "https://www.ersa.fvg.it/cms/hp/"),
    _f("Friuli Venezia Giulia", "ERSA FVG — Avvisi e comunicazioni", "http://www.ersa.fvg.it/cms/aziende/in-formazione/Avvisi-Comunicazioni/index.html", "https://www.ersa.fvg.it/cms/hp/"),
    _a("Friuli Venezia Giulia", "OSMER FVG", "https://www.osmer.fvg.it/", "https://www.osmer.fvg.it/"),
    _k("Friuli Venezia Giulia", "Condifesa FVG", "https://www.condifesafvg.it/"),
    # Lazio
    _f("Lazio", "Lazio — Servizio fitosanitario regionale", "https://www.regione.lazio.it/cittadini/agricoltura/servizio-fitosanitario-regionale", _SFN),
    _a("Lazio", "SIARL — Agrometeorologia Lazio (ARSIAL)", "https://siarl.arsial.it/", "https://www.arsial.it/"),
    # Liguria
    _f("Liguria", "Liguria — Sorveglianza e monitoraggio organismi nocivi", "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/servizio-fitosanitario-regionale/sorveglianza-del-territorio-carte-di-diffusione-e-monitoraggio-degli-organismi-nocivi.html", "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/servizio-fitosanitario-regionale.html"),
    _f("Liguria", "Liguria — Bollettini (Agriligurianet)", "https://www.agriligurianet.it/it/impresa/bandi/publiccompetitions/cloud/BOLLETTINI/all.html?view=publiccompetitions&task=cloud&tipocloud=all&tag=BOLLETTINI", "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/servizio-fitosanitario-regionale.html"),
    _a("Liguria", "Liguria — Centro di agrometeorologia (CAAR)", "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/agrometeo-caar.html", "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/servizio-fitosanitario-regionale.html"),
    # Lombardia
    _f("Lombardia", "Lombardia — Servizio fitosanitario regionale", "https://fitosanitario.regione.lombardia.it/wps/portal/site/sfr", _SFN),
    _a("Lombardia", "ARPA Lombardia — Bollettino agrometeo", "https://www.arpalombardia.it/temi-ambientali/meteo-e-clima/bollettini-meteorologici/agrometeo/", "https://www.arpalombardia.it/bollettini/"),
    _a("Lombardia", "ARPA Lombardia — Archivio bollettini agrometeo", "https://www.arpalombardia.it/archivio-bollettini-agrometeo/", "https://www.arpalombardia.it/bollettini/"),
    _k("Lombardia", "Condifesa Lombardia (federazione)", "https://www.condifesalombardia.it/"),
    _k("Lombardia", "Condifesa Brescia", "https://www.condifesabrescia.it/"),
    _k("Lombardia", "CODIMA Mantova", "https://www.codima.info/"),
    _k("Lombardia", "Condifesa Milano Lodi", "https://www.condifesa-mi-lo.it/"),
    _k("Lombardia", "COPROVI", "https://www.coprovi.it/"),
    _k("Lombardia", "Condifesa Lombardia Nord-Est", "https://www.condifesalombardianordest.it/"),
    # Marche
    _f("Marche", "AMAP Marche — Servizio fitosanitario", "https://www.amap.marche.it/servizi/fitosanitario", _SFN),
    _a("Marche", "AMAP Marche — Agrometeorologia", "https://www.amap.marche.it/servizi/agrometeorologia", "https://www.amap.marche.it/"),
    _a("Marche", "Regione Marche — Notiziari meteo e agrometeo", "https://meteo.regione.marche.it/Notiziari", "https://www.amap.marche.it/servizi/agrometeorologia"),
    _a("Marche", "AMAP Marche — Pubblicazioni di agrometeorologia", "https://www.amap.marche.it/pubblicazioni/agrometeorologia", "https://www.amap.marche.it/"),
    _k("Marche", "Condifesa Ancona Macerata", "https://www.condifesaanmc.it/"),
    # Molise
    _f("Molise", "Molise — Bollettini e comunicati fitosanitari", "https://www.regione.molise.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/18077", "https://www.regione.molise.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/4130"),
    _a("Molise", "ARSARP Molise — Agrometeorologia", "https://www.arsarp.it/category/agrometeorologia-2/", "https://www.arsarp.it/"),
    # Piemonte
    _f("Piemonte", "Piemonte — Bacheca dei bollettini fitosanitari", "https://www.regione.piemonte.it/web/temi/agricoltura/servizi-fitosanitari-pan/bacheca-dei-bollettini", "https://www.regione.piemonte.it/web/temi/agricoltura/servizi-fitosanitari-pan"),
    _k("Piemonte", "Condifesa Cuneo", "https://www.condifesacuneo.it/"),
    _k("Piemonte", "Condifesa Novara", "https://www.condifesanovara.it/"),
    _k("Piemonte", "COSMAN Piemonte", "https://www.cosmanpiemonte.it/"),
    _k("Piemonte", "Condifesa Vercelli Biella", "https://www.condifesa-vcbi.it/"),
    _k("Piemonte", "Condifesa Piemonte", "https://www.condifesapiemonte.com/"),
    # Puglia
    _f("Puglia", "Puglia — Emergenza Xylella (comunicati fitosanitari)", "http://www.emergenzaxylella.it/portal/portale_gestione_agricoltura", "https://www.regione.puglia.it/web/agricoltura"),
    _f("Puglia", "Puglia — Servizio fitosanitario (SIT Puglia)", "http://www.sit.puglia.it/portal/sit_portal", _SFN),
    _a("Puglia", "Agrometeo Puglia — Bollettini", "https://www.agrometeopuglia.it/bollettini", "https://www.regione.puglia.it/web/agricoltura"),
    _k("Puglia", "Condifesa Foggia", "http://www.condifesafoggia.it/"),
    _k("Puglia", "Agridifesa del Mediterraneo", "https://agridifesadelmediterraneo.eu/"),
    # Sardegna
    _f("Sardegna", "Sardegna Agricoltura — servizio fitosanitario", "https://www.sardegnaagricoltura.it/", _SFN),
    _a("Sardegna", "ARPAS Sardegna — Bollettino fenologico", "http://www.sar.sardegna.it/servizi/agro/bollfenologico.asp", "https://www.sar.sardegna.it/"),
    _a("Sardegna", "ARPAS Sardegna — Bollettino decadale di siccita", "http://www.sar.sardegna.it/servizi/agro/monit_siccita.asp", "https://www.sar.sardegna.it/"),
    _k("Sardegna", "Condifesa Cagliari", "https://www.condifesaca.it/home.html"),
    _k("Sardegna", "Condifesa Oristano", "https://www.condifesaor.it/"),
    _k("Sardegna", "Condifesa Sassari", "http://www.condifesa.sassari.it/"),
    # Sicilia
    _f("Sicilia", "Sicilia — Difesa fitosanitaria", "https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-agricoltura-sviluppo-rurale-pesca-mediterranea/dipartimento-agricoltura/difesa-fitosanitaria", "https://www.regione.sicilia.it/"),
    _a("Sicilia", "SIAS — Servizio Informativo Agrometeorologico Siciliano", "https://www.sias.regione.sicilia.it/", "https://www.sias.regione.sicilia.it/"),
    _k("Sicilia", "Condifesa Catania", "https://www.condifesacatania.it/"),
    # Toscana
    _f("Toscana", "Toscana — Servizio fitosanitario regionale", "https://www.regione.toscana.it/speciali/servizio-fitosanitario-regionale", _SFN),
    _a("Toscana", "LaMMA — Bollettino agrometeo", "https://www.lamma.toscana.it/agrometeo/firenze", "https://www.lamma.toscana.it/"),
    _k("Toscana", "CODIPRA Toscano", "https://www.codipratoscano.it/"),
    # Trentino-Alto Adige
    _f("Trentino-Alto Adige", "FEM — Bollettini tecnici (Trentino)", "https://www.fmach.it/Servizi/Bollettini-tecnici", "https://www.fmach.it/"),
    _f("Trentino-Alto Adige", "FEM — Emergenze fitosanitarie", "https://fitoemergenze.fmach.it/", "https://www.fmach.it/Servizi/Bollettini-tecnici"),
    _f("Trentino-Alto Adige", "Beratungsring (Alto Adige) — consulenza frutti-viticola", "https://www.beratungsring.org/", "https://www.beratungsring.org/"),
    _a("Trentino-Alto Adige", "Meteotrentino — bollettino ufficiale", "https://www.meteotrentino.it/previsioni/bollettino-meteorologico-ufficiale-per-il-trentino/", "https://www.meteotrentino.it/"),
    _a("Trentino-Alto Adige", "Meteo Provincia di Bolzano", "https://meteo.provincia.bz.it/", "https://meteo.provincia.bz.it/"),
    _k("Trentino-Alto Adige", "CODIPRA Trento", "https://www.codipratn.it/"),
    _k("Trentino-Alto Adige", "CODIPRA (codipra.it)", "https://www.codipra.it/"),
    _k("Trentino-Alto Adige", "Hagelschutzkonsortium (Alto Adige)", "https://www.hagelschutzkonsortium.com/"),
    # Umbria
    _f("Umbria", "Umbria — Bollettini fitosanitari 2026", "https://www.regione.umbria.it/agricoltura/servizio-fitosanitario-regionale/in-evidenza/-/asset_publisher/PONvICXXT7f8/content/bollettini-fitosanitari-2026", "https://www.regione.umbria.it/agricoltura/servizio-fitosanitario-regionale"),
    _k("Umbria", "Condifesa Umbria", "https://www.condifesaumbria.it/"),
    # Valle d'Aosta
    _f("Valle d'Aosta", "Valle d'Aosta — Avvisi fitosanitari per frutticoltori", "https://www.regione.vda.it/agricoltura/per_gli_agricoltori/fitosanitario/avvisi/frutticoltura_i.asp", "https://www.regione.vda.it/agricoltura/per_gli_agricoltori/fitosanitario/default_i.asp"),
    _f("Valle d'Aosta", "Valle d'Aosta — Avvisi fitosanitari per viticoltori", "https://www.regione.vda.it/agricoltura/per_gli_agricoltori/fitosanitario/avvisi/viticoltura_i.asp", "https://www.regione.vda.it/agricoltura/per_gli_agricoltori/fitosanitario/default_i.asp"),
    _a("Valle d'Aosta", "Meteo Valle d'Aosta", "http://meteo.regione.vda.it/", "https://www.regione.vda.it/agricoltura/"),
    _a("Valle d'Aosta", "Institut Agricole Regional", "https://www.iaraosta.it/", "https://www.iaraosta.it/"),
    # Veneto
    _f("Veneto", "Veneto — Bollettini fitosanitari 2026", "https://www.regione.veneto.it/web/fitosanitario/bollettini-fitosanitari-2026", "https://www.regione.veneto.it/web/fitosanitario"),
    _f("Veneto", "Veneto — Difesa delle colture", "https://www.regione.veneto.it/web/fitosanitario/difesa-colture", "https://www.regione.veneto.it/web/fitosanitario"),
    _a("Veneto", "ARPAV — Agrometeo", "https://www.arpa.veneto.it/temi-ambientali/agrometeo", "https://www.arpa.veneto.it/"),
    _k("Veneto", "Condifesa TVB", "https://www.condifesatvb.it/"),
    _k("Veneto", "Condifesa Veneto Est", "https://condifesavenetoest.it/"),
    _k("Veneto", "CODIVE", "https://www.codive.it/"),
]

REGIOES_SEM_FONTE = {
    ("Campania", "CONSORZIO"): "a lista Asnacodi nao tem consorzio da Campania",
    ("Lazio", "CONSORZIO"): "a lista Asnacodi nao tem consorzio do Lazio",
    ("Liguria", "CONSORZIO"): "a lista Asnacodi nao tem consorzio da Liguria",
    ("Molise", "CONSORZIO"): "a lista Asnacodi nao tem consorzio do Molise",
    ("Valle d'Aosta", "CONSORZIO"): "a lista Asnacodi nao tem consorzio do Valle d'Aosta",
    ("Piemonte", "AGROMETEO"): "a pagina de agricultura da Regione nao liga servico agrometeo (procurado 24/09)",
    ("Umbria", "AGROMETEO"): "a pagina de agricultura da Regione nao liga servico agrometeo (procurado 24/09)",
}
