# -*- coding: utf-8 -*-
import io, json, os

F = {}

F['STATUS'] = {
 'ACT_NOW':            ("Agire ora", "Act now"),
 'VALIDATE_NOW':       ("Validare ora", "Validate now"),
 'WATCH':              ("Osservare", "Watch"),
 'TO_VALIDATE':        ("Da validare", "To validate"),
 'FUTURE_PREPARATION': ("Preparazione futura", "Future preparation"),
}
F['OPPORTUNITY_STATE'] = {
 'OPPORTUNITY_CONFIRMED': ("Lettura che si regge", "Reading that holds"),
 'OPPORTUNITY_CANDIDATE': ("Lettura candidata", "Candidate reading"),
}
F['COMMERCIAL_PRIORITY'] = {
 'SALES_READY':           ("Pronta per la vendita", "Sales ready"),
 'STRATEGIC_OPPORTUNITY': ("Opportunita strategica", "Strategic opportunity"),
 'COMMERCIAL_WATCH':      ("Osservazione commerciale", "Commercial watch"),
 'TO_VALIDATE':           ("Da validare", "To validate"),
}
F['ARCHETYPE'] = {
 'O1_FIELD_PRESSURE':         ("Pressione in campo", "Field pressure"),
 'O2_MARKET_MOMENT':          ("Momento di mercato", "Market moment"),
 'O3_RESISTANCE_MOA':         ("Resistenza e meccanismo d'azione", "Resistance and mode of action"),
 'O4_COMPETITIVE_OPENING':    ("Apertura competitiva", "Competitive opening"),
 'O5_REGULATORY_PREPARATION': ("Preparazione normativa", "Regulatory preparation"),
 'O6_SCIENCE_TO_FIELD':       ("Dalla scienza al campo", "Science to field"),
}
F['WHY_COMMERCIAL_CODES'] = {
 'ALL_GATES_CLOSE':                ("Tutti i passaggi si chiudono: necessita, prodotto, geografia e tempo", "Every gate closes: need, product, geography and time"),
 'TIME_FROM_SOURCE_RECOMMENDATION':("Il tempo per agire viene dalla raccomandazione corrente della fonte", "Time to act comes from the source's current recommendation"),
 'NEED_CLOSED':                    ("La fonte dichiara la necessita chiusa", "The source declares the need closed"),
 'NEED_NOT_POSITIVE':              ("La necessita non e dichiarata positiva dalla fonte", "The need is not declared positive by the source"),
 'NEITHER_NEED_NOR_OPENING':       ("Ne una necessita dichiarata ne un'apertura competitiva", "Neither a declared need nor a competitive opening"),
 'OPENING_WITHOUT_NEED':           ("Apertura competitiva senza necessita dichiarata in campo", "Competitive opening without a declared field need"),
 'LABEL_WITHOUT_CATALOG':          ("Etichetta ministeriale senza pagina di catalogo che la confermi", "Ministerial label with no catalogue page confirming it"),
 'REGULATORY_BY_NATURE':           ("Il caso e normativo per natura, non agronomico", "The case is regulatory by nature, not agronomic"),
 'REGULATORY_WITHOUT_CATALOG':     ("Scadenza normativa su un attivo senza prodotto a catalogo", "Regulatory date on an active with no catalogue product"),
}
F['EXTERNAL_MATERIAL_READY'] = {
 'YES': ("Puo uscire di casa", "Cleared to leave the building"),
 'NO':  ("Non ancora autorizzata a uscire", "Not yet cleared to leave"),
}
F['EXTERNAL_BLOCKER_CODES'] = {
 'NOT_SALES_READY': ("Non ancora pronta per la vendita", "Not yet sales ready"),
}
F['WHY_NOW_CODES'] = {
 'CADEIA_COMPLETA':          ("Finestra agronomica aperta", "Agronomic window open"),
 'SEM_SINAL_ATUAL':          ("Manca un segnale corrente", "A current signal is missing"),
 'SEM_JANELA_DEFINIDA':      ("Nessuna regola di intervento dichiarata", "No intervention rule declared"),
 'SEM_JANELA_ABERTA_AGORA':  ("Condizione nota; stato attuale non ancora misurato", "Condition known; current state not yet measured"),
 'SEM_VINCULO_COM_PORTFOLIO':("Nessun prodotto del catalogo collegato alla coppia", "No catalogue product linked to the pair"),
 'SEM_TEMPO_PARA_ACAO':      ("La fonte non da un tempo per agire", "The source gives no time to act"),
}
F['CHAIN_LINK'] = {
 'SINAL_ATUAL':          ("Segnale corrente", "Current signal"),
 'JANELA_DEFINIDA':      ("Regola di intervento dichiarata", "Intervention rule declared"),
 'JANELA_ABERTA_AGORA':  ("Condizione soddisfatta ora", "Condition met now"),
 'VINCULO_COM_PORTFOLIO':("Legame con il portafoglio", "Link to the portfolio"),
 'TEMPO_PARA_ACAO':      ("Tempo per agire", "Time to act"),
}
F['SIGNAL_CURRENCY'] = {
 'CURRENT': ("Corrente", "Current"),
 'RECENT':  ("Recente", "Recent"),
 'OLD':     ("Non recente", "Not recent"),
 'UNKNOWN': ("Non noto", "Not known"),
}
F['COMMERCIAL_TIMING_BASIS'] = {
 'CURRENT_SOURCE_RECOMMENDATION': ("Raccomandazione corrente della fonte", "Source's current recommendation"),
 'NONE':                          ("Nessuna base di tempo dichiarata", "No declared basis for timing"),
}
F['WINDOW_TYPE'] = {
 'PHENOLOGY_WINDOW':        ("Finestra definita dallo stadio fenologico", "Window defined by phenological stage"),
 'PREHARVEST_WINDOW':       ("Finestra definita dall'intervallo di pre-raccolta", "Window defined by the pre-harvest interval"),
 'THRESHOLD_WINDOW':        ("Finestra definita da una soglia da misurare", "Window defined by a threshold to be measured"),
 'PEST_STAGE_WINDOW':       ("Finestra definita dallo stadio dell'avversita", "Window defined by the pest's stage"),
 'WEATHER_TRIGGERED_WINDOW':("Finestra aperta da un evento climatico", "Window triggered by a weather event"),
 'RULE_DELEGATED_TO_FARM':  ("La decisione dipende dall'osservazione in campo", "The decision depends on farm-level observation"),
 'CALENDAR_WINDOW':         ("Finestra definita da date di calendario", "Window defined by calendar dates"),
}
F['WINDOW_DEFINED'] = {
 'YES': ("Regola di intervento nota", "Intervention rule known"),
 'NO':  ("Nessuna regola di intervento dichiarata per questa coppia", "No intervention rule declared for this pair"),
}
F['WINDOW_OPEN_NOW'] = {
 'YES':     ("Aperta ora", "Open now"),
 'NO':      ("Non aperta ora", "Not open now"),
 'UNKNOWN': ("Stato attuale non ancora misurato", "Current state not yet measured"),
}
F['WINDOW_OPEN_NOW_METHOD'] = {
 'ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO':      ("Lo stesso documento dichiara lo stadio della coltura", "The same document declares the crop's stage"),
 'FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE':    ("La fonte dichiara la condizione come presente", "The source declares the condition as present"),
 'FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE': ("La fonte non riporta la misura che la condizione richiede", "The source does not report the measurement the condition requires"),
 'NENHUMA_CONDICAO_DECLARADA_PARA_O_PAR':     ("Nessuna condizione dichiarata per questa coppia", "No condition declared for this pair"),
 'REGRA_EXIGE_MEDICAO_DO_POMAR_QUE_NENHUMA_FONTE_REGIONAL_TEM': ("La regola richiede una misura in campo che nessuna fonte regionale possiede", "The rule requires a farm-level measurement no regional source holds"),
 'DOCUMENTO_NAO_CORRENTE':                    ("Il documento che la dichiara non e corrente", "The document declaring it is not current"),
}
F['WINDOW_RULE_STATE'] = {
 'RULE_DECLARED':           ("Regola dichiarata dalla fonte", "Rule declared by the source"),
 'RULE_NOT_DECLARED':       ("Nessuna regola dichiarata", "No rule declared"),
 'RULE_DELEGATED_TO_FARM':  ("La decisione dipende dall'osservazione in campo", "The decision depends on farm-level observation"),
 'RULE_ADMINISTRATIVE_ONLY':("Obbligo amministrativo — non e una finestra agronomica", "Administrative obligation — not an agronomic window"),
}
F['WINDOW_STATE'] = {
 'UNKNOWN':      ("Nessuna data di applicazione dichiarata", "No application date declared"),
 'WINDOW_OPEN':  ("Finestra di applicazione aperta", "Application window open"),
 'WINDOW_CLOSED':("Finestra di applicazione chiusa", "Application window closed"),
}
F['PEST_STAGE_STATE'] = {
 'STAGE_PEAK':        ("Picco del volo dichiarato", "Flight peak declared"),
 'STAGE_DECLINING':   ("Volo in calo", "Flight declining"),
 'STAGE_ENDED':       ("Volo concluso", "Flight ended"),
 'STAGE_NOT_DECLARED':("Stadio non dichiarato dalla fonte", "Stage not declared by the source"),
}
F['ACTION_RECOMMENDATION_STATE'] = {
 'START_RECOMMENDED':          ("La fonte raccomanda di iniziare", "The source recommends starting"),
 'CONTINUE_RECOMMENDED':       ("La fonte raccomanda di proseguire", "The source recommends continuing"),
 'SUSPEND_RECOMMENDED':        ("La fonte raccomanda di sospendere", "The source recommends suspending"),
 'CONCLUDED_DECLARED':         ("La fonte dichiara l'intervento concluso", "The source declares the intervention concluded"),
 'NOT_NEEDED_DECLARED':        ("La fonte dichiara che non sono necessari interventi", "The source declares no intervention is needed"),
 'PROHIBITED_DECLARED':        ("La fonte dichiara il trattamento vietato", "The source declares treatment prohibited"),
 'RECOMMENDATION_NOT_DECLARED':("Nessuna raccomandazione dichiarata", "No recommendation declared"),
}
F['THRESHOLD_STATE'] = {
 'NOT_APPLICABLE': ("Nessuna soglia si applica a questa coppia", "No threshold applies to this pair"),
 'NOT_DECLARED':   ("Soglia non dichiarata dalla fonte", "Threshold not declared by the source"),
}
F['NEED_DIRECTION'] = {
 'POSITIVE_PRESSURE':   ("La fonte dichiara pressione da trattare", "The source declares pressure to treat"),
 'NO_ACTION_RECOMMENDED':("La fonte raccomanda di monitorare, non di attivare", "The source recommends monitoring, not activating"),
 'ACTION_SUSPENDED':    ("La fonte dichiara l'azione sospesa", "The source declares action suspended"),
 'WINDOW_CONCLUDED':    ("La fonte dichiara il ciclo concluso", "The source declares the cycle concluded"),
 'TREATMENT_PROHIBITED':("La fonte dichiara il trattamento vietato", "The source declares treatment prohibited"),
 'NEUTRAL_MENTION':     ("La fonte nomina la coppia senza indicare una direzione", "The source names the pair without giving a direction"),
 'UNKNOWN':             ("Direzione non nota", "Direction not known"),
}
F['NEED_METHOD'] = {
 'PAIR_IN_SAME_CLAUSE':           ("Coltura e avversita nella stessa frase", "Crop and target in the same clause"),
 'PAIR_IN_DOCUMENT_TITLE':        ("Coppia nel titolo del documento", "Pair in the document title"),
 'CROP_FROM_PRECEDING_CLAUSE':    ("Coltura dalla frase precedente", "Crop from the preceding clause"),
 'CROP_FROM_SINGLE_CROP_DOCUMENT':("Documento dedicato a una sola coltura", "Document devoted to a single crop"),
}
F['PRIMARY_MATCH_REASON'] = {
 'UNICO_PRODUTO_DO_CATALOGO_NO_PAR':  ("Unico prodotto del catalogo su questa coppia", "The only catalogue product on this pair"),
 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER':("Nessuna regola difendibile per eleggerne uno", "No defensible rule for electing one"),
}
F['PRODUCT_LINK_STATE'] = {
 'VERIFIED_LABEL_MATCH': ("Etichetta ministeriale verificata sulla coppia", "Ministerial label verified on the pair"),
 'RELATED_PORTFOLIO':    ("Portafoglio collegato, etichetta da confermare", "Related portfolio, label to be confirmed"),
}
F['MODE_OF_ACTION_STATE'] = {
 'CLASSIFIED': ("Meccanismo d'azione classificato", "Mode of action classified"),
 'UNKNOWN':    ("Meccanismo d'azione non classificato", "Mode of action not classified"),
}
F['APPLICATION_STATE'] = {
 'QUOTED_ON_LABEL': ("Impiego citato in etichetta", "Use quoted on the label"),
 'UNKNOWN':         ("Impiego non dichiarato", "Use not declared"),
}
F['WHAT_IS_MISSING'] = {
 'INTENSITY_UNKNOWN':              ("Intensita della pressione non nota", "Pressure intensity not known"),
 'RECURRENCE_UNKNOWN':             ("Ricorrenza negli anni non nota", "Recurrence across years not known"),
 'OFFICIAL_AREA_NOT_CLIENT_SAFE':  ("Superficie ufficiale non pubblicabile in questa lettura", "Official area not publishable in this reading"),
 'DIRECTION_UNKNOWN':              ("Direzione della fonte non nota", "The source's direction is not known"),
 'REGION_NOT_DECLARED':            ("Regione non dichiarata dal documento", "Region not declared by the document"),
 'SIGNAL_NOT_RECENT':              ("Segnale non recente", "Signal not recent"),
 'COMMERCIAL_PRODUCT_MISSING':     ("Nessun prodotto del catalogo su questa coppia", "No catalogue product on this pair"),
 'NO_AGRONOMIC_TARGET':            ("Nessuna avversita agronomica nel caso", "No agronomic target in the case"),
 'WINDOW_RULE_MISSING':            ("Regola di intervento non dichiarata", "Intervention rule not declared"),
 'WINDOW_STATE_UNKNOWN':           ("Stato attuale della finestra non misurato", "Current window state not measured"),
 'WINDOW_RULE_DELEGATED_TO_FARM':  ("La regola rimanda all'osservazione in campo", "The rule defers to farm-level observation"),
 'WINDOW_RULE_ADMINISTRATIVE_ONLY':("La regola e un obbligo amministrativo, non agronomico", "The rule is an administrative obligation, not an agronomic one"),
}
F['PUBLICATION_STATE'] = {
 'PUBLISHABLE':         ("Pubblicabile", "Publishable"),
 'VALIDATION_REQUIRED': ("Richiede validazione prima di uscire", "Requires validation before it goes out"),
}
F['TRAIL_STATE'] = {
 'COMPLETE':   ("Tracciato completo", "Trail complete"),
 'INCOMPLETE': ("Tracciato incompleto", "Trail incomplete"),
}
F['COMMERCIAL_MAGNITUDE'] = {
 'MEASURED_BY_DIMENSION': ("Misurata per dimensione, non stimata", "Measured by dimension, not estimated"),
 'UNKNOWN':               ("Grandezza non misurabile in questa lettura", "Magnitude not measurable in this reading"),
}
F['CONFIDENCE'] = {
 'ALTA':    ("Alta", "High"),
 'MEDIA':   ("Media", "Medium"),
 'BAIXA':   ("Bassa", "Low"),
 'NENHUMA': ("Nessuna", "None"),
}
F['GEOGRAPHIC_SCOPE'] = {
 'PROVINCIAL': ("Provinciale", "Provincial"),
 'REGIONAL':   ("Regionale", "Regional"),
 'NACIONAL':   ("Nazionale", "National"),
 'EUROPEU':    ("Europeo", "European"),
}
F['CROP'] = {
 'CROP_GRAPEVINE':    ("Vite", "Grapevine"),
 'CROP_APPLE':        ("Melo", "Apple"),
 'CROP_MAIZE':        ("Mais", "Maize"),
 'CROP_RICE':         ("Riso", "Rice"),
 'CROP_WHEAT_GENERIC':("Frumento", "Wheat"),
 'CROP_BARLEY':       ("Orzo", "Barley"),
 'CROP_SOYBEAN':      ("Soia", "Soybean"),
 'CROP_SUGAR_BEET':   ("Barbabietola da zucchero", "Sugar beet"),
 'CROP_TOMATO':       ("Pomodoro", "Tomato"),
 'CROP_OLIVE':        ("Olivo", "Olive"),
 'CROP_CITRUS':       ("Agrumi", "Citrus"),
 'CROP_VEGETABLES':   ("Orticole", "Vegetables"),
}
F['TARGET'] = {
 'ISSUE_BOTRYTIS':       ("Botrite", "Botrytis"),
 'ISSUE_DOWNY_MILDEW':   ("Peronospora", "Downy mildew"),
 'ISSUE_POWDERY_MILDEW': ("Oidio", "Powdery mildew"),
 'ISSUE_GRAPE_MOTH':     ("Tignoletta della vite", "Grape moth"),
 'ISSUE_CODLING_MOTH':   ("Carpocapsa", "Codling moth"),
 'ISSUE_CORN_BORER':     ("Piralide del mais", "Corn borer"),
 'ISSUE_DIABROTICA':     ("Diabrotica", "Diabrotica"),
 'ISSUE_ECHINOCHLOA':    ("Giavone", "Echinochloa"),
 'ISSUE_SCAPHOIDEUS':    ("Scafoideo", "Scaphoideus"),
}
F['GEOGRAPHY'] = {
 'REGION_EMILIA_ROMAGNA':        ("Emilia-Romagna", "Emilia-Romagna"),
 'REGION_VENETO':                ("Veneto", "Veneto"),
 'REGION_TOSCANA':               ("Toscana", "Tuscany"),
 'REGION_UMBRIA':                ("Umbria", "Umbria"),
 'REGION_LOMBARDIA':             ("Lombardia", "Lombardy"),
 'REGION_FRIULI_VENEZIA_GIULIA': ("Friuli-Venezia Giulia", "Friuli-Venezia Giulia"),
 'GEO_ITALY':                    ("Italia", "Italy"),
 'GEO_EU':                       ("Unione Europea", "European Union"),
}
F['EVIDENCE_ROLE'] = {
 'SUPPORTS_SIGNAL':           ("Sostiene il segnale", "Supports the signal"),
 'SUPPORTS_WINDOW':           ("Sostiene la finestra", "Supports the window"),
 'SUPPORTS_DIRECTION':        ("Sostiene la direzione", "Supports the direction"),
 'SUPPORTS_PRODUCT_MATCH':    ("Sostiene il legame con il prodotto", "Supports the product link"),
 'SUPPORTS_COMMERCIAL_ACTION':("Sostiene l'azione commerciale", "Supports the commercial action"),
 'SUPPORTS_REGIONAL_CONTEXT': ("Sostiene il contesto regionale", "Supports the regional context"),
 'BACKGROUND_ONLY':           ("Contesto: non decide nulla in questo caso", "Background only: it decides nothing in this case"),
 'WEAKENS':                   ("Questa evidenza riduce l'urgenza commerciale", "This evidence lowers the commercial urgency"),
 'CLOSES':                    ("Il monitoraggio non sostiene un'azione ora", "Monitoring does not support action now"),
 'CONTRADICTS':               ("Questa evidenza contraddice la lettura", "This evidence contradicts the reading"),
}
F['EVIDENCE_WHY_CODE'] = {
 'OBSERVACAO_DE_CAMPO_NA_MESMA_REGIAO': ("Osservazione di campo nella stessa regione", "Field observation in the same region"),
 'ROTULO_MINISTERIAL_NO_PAR':           ("Etichetta ministeriale sulla coppia", "Ministerial label on the pair"),
 'DECLARA_A_CONDICAO_DA_JANELA':        ("Dichiara la condizione della finestra", "Declares the window's condition"),
 'DECLARA_A_REGRA_DO_MOMENTO':          ("Dichiara la regola del momento", "Declares the timing rule"),
 'FRASE_QUE_DECIDIU_A_DIRECAO':         ("La frase che ha deciso la direzione", "The sentence that decided the direction"),
 'CONTEXTO_DE_MERCADO':                 ("Contesto di mercato", "Market context"),
 'MOVIMENTO_DE_CONCORRENTE':            ("Movimento di un concorrente", "A competitor's move"),
 'NAO_DECIDE_NENHUM_ELO':               ("Non decide nessun anello della catena", "It decides no link of the chain"),
}
F['EVIDENCE_ENTITY_TYPE'] = {
 'FIELD_SIGNAL':              ("Segnale di campo", "Field signal"),
 'LABEL_USE_RELATIONSHIP':    ("Impiego autorizzato in etichetta", "Authorised use on the label"),
 'ACTIVE_INGREDIENT':         ("Sostanza attiva", "Active ingredient"),
 'REGULATORY_PRODUCT':        ("Prodotto registrato", "Registered product"),
 'REGULATORY_FUTURE_FACT':    ("Fatto normativo futuro", "Future regulatory fact"),
 'SCIENTIFIC_RECORD':         ("Record scientifico", "Scientific record"),
 'RESISTANCE_RECORD':         ("Record di resistenza", "Resistance record"),
 'MARKET_OBSERVATION':        ("Osservazione di mercato", "Market observation"),
 'COMPETITOR_ACTIVITY':       ("Attivita di un concorrente", "Competitor activity"),
 'CROP_ECONOMIC_WEIGHT_CLAIM':("Peso economico della coltura", "Crop economic weight"),
}
F['DEPARTMENT'] = {
 'MARKET_DEVELOPMENT':   ("Market Development", "Market Development"),
 'COMMERCIAL':           ("Commerciale", "Commercial"),
 'MARKETING':            ("Marketing", "Marketing"),
 'TECHNICAL_SCIENTIFIC': ("Tecnico / Scientifico", "Technical / Scientific"),
 'SUPPLY':               ("Supply", "Supply"),
}
F['ACTION_STATE'] = {
 'ACT':       ("Agisce", "Acts"),
 'VALIDATE':  ("Valida", "Validates"),
 'PREPARE':   ("Prepara", "Prepares"),
 'WATCH':     ("Osserva", "Watches"),
 'NO_ACTION': ("Nessuna azione sostenuta", "No supported action"),
}
F['ACTION'] = {
 'CONTACT_NOW':                    ("Contattare ora", "Contact now"),
 'CONFIRM_RECOMMENDATION_IN_FIELD':("Confermare la raccomandazione in campo", "Confirm the recommendation in the field"),
 'CONFIRM_WINDOW_CONDITION_MET':   ("Confermare che la condizione della finestra e soddisfatta", "Confirm the window condition is met"),
 'CONFIRM_AT_FARM_LEVEL':          ("Confermare con un'osservazione in campo", "Confirm with a farm-level observation"),
 'VALIDATE_AT_FARM_LEVEL':         ("Validare con una misura in campo", "Validate with a farm-level measurement"),
 'VALIDATE_WINDOW_IN_REGION':      ("Validare la finestra nella regione", "Validate the window in the region"),
 'ESTABLISH_WINDOW_CONDITION':     ("Stabilire la condizione della finestra", "Establish the window condition"),
 'MESSAGE_AVAILABLE':              ("Messaggio disponibile", "Message available"),
 'PREPARE':                        ("Preparare", "Prepare"),
 'WATCH_REGULATORY_DATE':          ("Sorvegliare la scadenza normativa", "Watch the regulatory date"),
 'NO_MOVEMENT':                    ("Nessun movimento sostenuto", "No supported movement"),
 'NOT_CONVENED':                   ("Non convocato da questo caso", "Not convened by this case"),
}
F['ACTION_WHY_CODE'] = {
 'CADEIA_COMPLETA':                      ("La catena si chiude interamente", "The chain closes end to end"),
 'SINAL_ATUAL_COM_ALVO':                 ("Segnale corrente con l'avversita nominata", "Current signal naming the target"),
 'CONDICAO_DECLARADA_ESTADO_DESCONHECIDO':("Condizione nota; stato attuale non ancora misurato", "Condition known; current state not yet measured"),
 'REGRA_DELEGADA_AO_POMAR':              ("La decisione dipende dall'osservazione in campo", "The decision depends on farm-level observation"),
 'SEM_CONDICAO_DECLARADA':               ("Nessuna condizione dichiarata", "No condition declared"),
 'SEM_SINAL_ATUAL':                      ("Nessun segnale corrente", "No current signal"),
 'SEM_BASE_FACTUAL':                     ("Nessuna base fattuale per muoversi", "No factual basis to move"),
 'SEM_PRIORIDADE_COMERCIAL':             ("Nessuna priorita commerciale sostenuta", "No supported commercial priority"),
 'PRIORIDADE_COMERCIAL_SEM_TEMPO_PROVADO':("Priorita commerciale senza un tempo provato", "Commercial priority without proven timing"),
 'EXTERNAL_MATERIAL_READY':              ("Il materiale esterno e autorizzato", "External material is cleared"),
 'NAO_AUTORIZADO_A_SAIR':                ("Non ancora autorizzato a uscire", "Not yet cleared to leave"),
 'NADA_A_VALIDAR':                       ("Niente da validare in questa lettura", "Nothing to validate in this reading"),
 'DATA_REGULATORIA_EM_ATIVO_LIGADO':     ("Scadenza normativa su un attivo collegato", "Regulatory date on a linked active"),
}
F['BRIEF_CODE'] = {
 'PRESSAO_RECENTE':                   ("Pressione recente sostenuta da segnali e fonti indipendenti", "Recent pressure backed by field signals and independent sources"),
 'JANELA_ABERTA':                     ("Finestra agronomica aperta", "Agronomic window open"),
 'JANELA_DEFINIDA_ESTADO_DESCONHECIDO':("Condizione nota; stato attuale non ancora misurato", "Condition known; current state not yet measured"),
 'JANELA_DELEGADA_AO_POMAR':          ("La decisione dipende dall'osservazione in campo", "The decision depends on farm-level observation"),
 'SEM_JANELA':                        ("Nessuna regola di intervento dichiarata", "No intervention rule declared"),
 'PORTFOLIO':                         ("Prodotti del catalogo collegati alla coppia", "Catalogue products linked to the pair"),
 'SEM_PORTFOLIO':                     ("Nessun prodotto del catalogo su questa coppia", "No catalogue product on this pair"),
 'FONTE_MANDA_PARAR':                 ("La fonte raccomanda di monitorare, non di attivare", "The source recommends monitoring, not activating"),
 'ACAO_PRINCIPAL':                    ("Azione principale del caso", "The case's leading action"),
}
F['FIT'] = {
 'DECLARED_ON_CATALOG_PAGE':             ("Dichiarato nella pagina di catalogo", "Declared on the catalogue page"),
 'ON_MINISTERIAL_LABEL':                 ("Presente in etichetta ministeriale", "Present on the ministerial label"),
 'NATIONAL_AUTHORIZATION_CONTAINS_REGION':("Autorizzazione nazionale che copre la regione", "National authorisation covering the region"),
 'AUTHORIZATION_LIVE':                   ("Autorizzazione in vigore", "Authorisation in force"),
 'YES':                                  ("Si", "Yes"),
 'NO':                                   ("No", "No"),
 'UNKNOWN':                              ("Non noto", "Not known"),
}
F['VALIDATION_STATE'] = {
 'LABEL_AND_CATALOG': ("Etichetta ministeriale e pagina di catalogo", "Ministerial label and catalogue page"),
 'LABEL_ONLY':        ("Solo etichetta ministeriale", "Ministerial label only"),
}
F['MATCH_REASON'] = {
 'REGISTRATION_NUMBER_JOIN': ("Unione per numero di registrazione", "Joined on registration number"),
}
F['RESTRICTION'] = {
 'EU_APPROVAL_EXPIRES': ("Approvazione UE della sostanza in scadenza", "EU approval of the substance expires"),
}
F['MAGNITUDE_DIM'] = {
 'SINAIS_DE_CAMPO':      ("Segnali di campo", "Field signals"),
 'FONTES_INDEPENDENTES': ("Fonti indipendenti", "Independent sources"),
 'REGIOES_DO_PAR':       ("Regioni della coppia", "Regions of the pair"),
 'AREA_OFICIAL_HA':      ("Superficie ufficiale (ha)", "Official area (ha)"),
 'AREA_OFICIAL_ANO':     ("Anno della superficie ufficiale", "Year of the official area"),
 'AREA_SELECTION_RULE':  ("Regola di scelta della superficie", "Area selection rule"),
 'AREA_EVIDENCE_ID':     ("Evidenza della superficie", "Area evidence"),
}
F['UI'] = {
 'CANONICAL_RADAR':      ("Radar canonico", "Canonical radar"),
 'WHY_COMMERCIAL':       ("Perche e un'opportunita commerciale", "Why this is a commercial opportunity"),
 'WHY_NOW':              ("Perche ora — e perche non ancora", "Why now — and why not yet"),
 'WINDOW':               ("Finestra", "Window"),
 'ACTION_MAP':           ("Mappa delle azioni", "Action map"),
 'EVIDENCE':             ("Evidenze", "Evidence"),
 'PORTFOLIO':            ("Portafoglio", "Portfolio"),
 'WHAT_IS_MISSING':      ("Cosa manca", "What is missing"),
 'NO_PRIMARY':           ("Nessun prodotto e principale: il motore non ha una regola difendibile per eleggerne uno", "No product is primary: the engine has no defensible rule for electing one"),
 'PRIMARY':              ("Prodotto principale", "Primary product"),
 'ALL_MATCHES':          ("Tutti i prodotti collegati", "All linked products"),
 'NO_MATCHES':           ("Nessun prodotto del catalogo collegato a questa coppia", "No catalogue product linked to this pair"),
 'RULE':                 ("Regola", "Rule"),
 'STATE_NOW':            ("Stato ora", "State now"),
 'METHOD':               ("Come lo sappiamo", "How we know"),
 'DEPENDS_ON':           ("Dipende da", "Depends on"),
 'UNLOCKED_BY':          ("Cosa lo sblocca", "What unlocks it"),
 'MISSING_LINKS':        ("Anelli mancanti", "Missing links"),
 'PROVES':               ("Cosa prova", "What it proves"),
 'NOT_PROVES':           ("Cosa NON prova", "What it does NOT prove"),
 'COMMERCIAL_NOT_PROVES':("Cosa NON prova sul piano commerciale", "What it does NOT prove commercially"),
 'SOURCES':              ("Fonti", "Sources"),
 'SIGNAL':               ("Segnale", "Signal"),
 'DIRECTION':            ("Direzione della fonte", "The source's direction"),
 'PEST_STAGE':           ("Stadio dell'avversita", "Pest stage"),
 'RECOMMENDATION':       ("Raccomandazione", "Recommendation"),
 'THRESHOLD':            ("Soglia", "Threshold"),
 'PUBLICATION':          ("Stato di pubblicazione", "Publication state"),
 'MAGNITUDE':            ("Grandezza misurata", "Measured magnitude"),
 'CONFIDENCE':           ("Confidenza", "Confidence"),
 'DECLARED_IN_DOC':      ("Dichiarata nel documento", "Declared in the document"),
 'PT_ONLY_NOTE':         ("La frase originale e nel documento della fonte; non viene riprodotta qui", "The original sentence is in the source document; it is not reproduced here"),
 'CANONICAL_NOTE':       ("Intelligence canonica — 43 casi dal motore", "Canonical intelligence — 43 cases from the engine"),
 'DEMO_NOTE':            ("Casi di presentazione — non contano nell'intelligence canonica", "Presentation cases — not counted in the canonical intelligence"),
 'RESTRICTIONS':         ("Restrizioni", "Restrictions"),
 'ACTIVE_INGREDIENTS':   ("Sostanze attive", "Active ingredients"),
 'MODE_OF_ACTION':       ("Meccanismo d'azione", "Mode of action"),
 'REGISTRATION':         ("Registrazione", "Registration"),
 'NOT_MEASURED':         ("Non misurato", "Not measured"),
 'PRODUCTS_LINKED_N':    ("prodotti collegati alla coppia", "products linked to the pair"),
 'PRODUCT_LINKED_1':     ("prodotto collegato alla coppia", "product linked to the pair"),
 'NO_PRIMARY_SHORT':     ("nessuno e principale", "none is primary"),
 'SINGLE_MATCH':         ("match unico", "single match"),
 'MORE_MATCHES':         ("altri prodotti collegati", "more linked products"),
 'WINDOW_NO_RULE':       ("Nessuna regola di intervento dichiarata per questa coppia", "No intervention rule declared for this pair"),
 'WINDOW_RULE_KNOWN':    ("Regola di intervento nota", "Intervention rule known"),
 'WHY_NOT_YET':          ("Perche non ancora", "Why not yet"),
 'CHAIN':                ("La catena del momento", "The chain of the moment"),
 'DEMO_RADAR':           ("Radar di dimostrazione", "Demonstration radar"),
 'ENGINE_SAYS':          ("Il motore dichiara", "The engine declares"),
 'COMMERCIAL_PRIORITY_T':("Priorita commerciale", "Commercial priority"),
}

lines = []
w = lines.append
w("/* SINTONIA ITALIA · IL DIZIONARIO DELLA SUPERFICIE CANONICA (IT · EN)")
w("   ---------------------------------------------------------------------------")
w("   Il motore parla in CODICI, e i codici sono la ragione per cui due lingue")
w("   possono leggere la stessa intelligence senza tradurre una decisione. Ma un")
w("   codice non e un'etichetta: `RULE_DELEGATED_TO_FARM` su uno schermo italiano")
w("   e un difetto, non un fatto.")
w("")
w("       IL MOTORE DECIDE IN CODICI. LO SCHERMO LEGGE IN LINGUA.")
w("       QUESTO FILE E LA FRONTIERA FRA LE DUE COSE, E NON DECIDE NULLA.")
w("")
w("   Nessuna voce qui dentro calcola, sceglie o ordina. Ogni voce e la stessa")
w("   cosa detta in italiano e in inglese. Un codice che il motore aggiunge")
w("   domani e ASSENTE — visibile come tale — invece di essere reso a caso: il")
w("   gate IT_LABELS_COMPLETE / EN_LABELS_COMPLETE reprova la mancanza.")
w("")
w("   UNKNOWN NON PUO SPARIRE DIETRO UNA COPY BELLA. Dove il motore non sa,")
w("   queste frasi dicono che non si sa, e dicono cosa manca perche si sappia. */")
w("window.MEETING_LABELS = (function () {")
w("  'use strict';")
w("  var F = {};")
for fam in F:
    w("  F[%s] = {" % json.dumps(fam))
    items = list(F[fam].items())
    for i,(code,(it,en)) in enumerate(items):
        comma = "," if i < len(items)-1 else ""
        w("    %s: [%s, %s]%s" % (json.dumps(code), json.dumps(it, ensure_ascii=False), json.dumps(en, ensure_ascii=False), comma))
    w("  };")
w("")
w("  /* Un codice non tradotto non diventa una parola inventata: esce come stringa")
w("     vuota e il gate lo trova. Meglio un vuoto misurabile di un token dipinto. */")
w("  function t(family, code, lang) {")
w("    if (code === null || code === undefined || code === '') return '';")
w("    var f = F[family]; if (!f) return '';")
w("    var e = f[String(code)]; if (!e) return '';")
w("    return lang === 'en' ? e[1] : e[0];")
w("  }")
w("  function has(family, code) {")
w("    var f = F[family]; return !!(f && f[String(code)]);")
w("  }")
w("  function list(family, codes, lang) {")
w("    return (codes || []).map(function (c) { return t(family, c, lang); })")
w("      .filter(function (s) { return !!s; });")
w("  }")
w("  return { families: F, t: t, has: has, list: list };")
w("})();")
io.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'italia-portale','client','meeting-labels.js'),'w',encoding='utf-8').write("\n".join(lines)+"\n")
print("written", sum(len(v) for v in F.values()), "entries in", len(F), "families")
