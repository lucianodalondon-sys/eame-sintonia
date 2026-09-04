/* SINTONIA · MEETING LABELS — IT / EN
   ===========================================================================
   IL MOTORE DECIDE IN CODICI. LO SCHERMO PARLA IN PAROLE.

   Questo file e un DIZIONARIO, non una fonte. Non contiene un fatto, un
   numero, una data, una regola ne un verdetto: solo il nome umano di ogni
   gettone che MEETING-INTELLIGENCE-SNAPSHOT porta gia deciso.

       NESSUN GETTONE INTERNO PUO ARRIVARE SULLO SCHERMO.
       NESSUNA ETICHETTA PUO CAMBIARE CIO CHE IL GETTONE SIGNIFICA.

   DOVE VIVE, E PERCHE QUI E NON IN italy-i18n.js
   `italy-i18n.js` e il dizionario del portale (94 KB) e appartiene alla base
   visiva congelata. Il vocabolario della riunione e un insieme CHIUSO e
   MISURATO, che nasce e muore con lo snapshot: tenerlo in un file proprio,
   caricato DOPO l'i18n, lascia le due cose separabili e rende verificabile in
   un colpo solo che ogni gettone dei 43 casi abbia un nome nelle due lingue.
   Non tocca, non sovrascrive e non estende `SINTONIA_I18N`.

   COMPLETEZZA
   Ogni famiglia qui sotto e stata MISURATA sui 43 casi dello snapshot. Il
   guardiano `audit/meeting-gate.mjs` rilegge lo snapshot e fallisce se un solo
   gettone presente nei dati non trova la sua frase in IT e in EN.

   UNKNOWN NON SPARISCE DIETRO UNA FRASE GENTILE: quando il motore dice
   «non lo so», l'etichetta lo dice.
   =========================================================================== */
(function () {
  'use strict';

  /* ── STATO TEMPORALE DEL CASO ─────────────────────────────────────────── */
  var STATUS = {
    ACT_NOW:            ['AGIRE ORA', 'ACT NOW'],
    VALIDATE_NOW:       ['VALIDARE ORA', 'VALIDATE NOW'],
    WATCH:              ['OSSERVARE', 'WATCH'],
    TO_VALIDATE:        ['DA VALIDARE', 'TO VALIDATE'],
    FUTURE_PREPARATION: ['PREPARAZIONE FUTURA', 'FUTURE PREPARATION'],
  };

  /* ── PRIORITA COMMERCIALE ─────────────────────────────────────────────── */
  var COMMERCIAL_PRIORITY = {
    SALES_READY:           ['PRONTA PER LA VENDITA', 'SALES READY'],
    STRATEGIC_OPPORTUNITY: ['OPPORTUNITA STRATEGICA', 'STRATEGIC OPPORTUNITY'],
    COMMERCIAL_WATCH:      ['OSSERVAZIONE COMMERCIALE', 'COMMERCIAL WATCH'],
    TO_VALIDATE:           ['DA VALIDARE', 'TO VALIDATE'],
  };
  var COMMERCIAL_PRIORITY_WHY = {
    SALES_READY:           ['La catena regge fino al prodotto: si puo parlare con il cliente.',
                            'The chain holds all the way to the product: the customer conversation can happen.'],
    STRATEGIC_OPPORTUNITY: ['Vale come posizione, non come vendita immediata.',
                            'It matters as a position, not as an immediate sale.'],
    COMMERCIAL_WATCH:      ['Da tenere sotto osservazione: manca ancora un elo per agire.',
                            'Keep it under observation: one link is still missing before acting.'],
    TO_VALIDATE:           ['La lettura non e ancora sostenuta: prima si valida.',
                            'The reading is not supported yet: validate first.'],
  };

  /* ── ARCHETIPO · PERCHE QUESTO CASO ESISTE ────────────────────────────── */
  var ARCHETYPE = {
    O1_FIELD_PRESSURE:        ['PRESSIONE IN CAMPO', 'FIELD PRESSURE'],
    O2_MARKET_MOMENT:         ['MOMENTO DI MERCATO', 'MARKET MOMENT'],
    O3_RESISTANCE_MOA:        ['RESISTENZA E MECCANISMO D’AZIONE', 'RESISTANCE AND MODE OF ACTION'],
    O4_COMPETITIVE_OPENING:   ['APERTURA COMPETITIVA', 'COMPETITIVE OPENING'],
    O5_REGULATORY_PREPARATION:['PREPARAZIONE NORMATIVA', 'REGULATORY PREPARATION'],
    O6_SCIENCE_TO_FIELD:      ['DALLA SCIENZA AL CAMPO', 'SCIENCE TO FIELD'],
  };

  /* ── LA FINESTRA · TIPO ───────────────────────────────────────────────
     Il modello nuovo di finestra agronomica. RULE_DELEGATED_TO_FARM non e una
     finestra mancante: e una finestra la cui REGOLA e nota e la cui MISURA
     appartiene al frutteto. */
  var WINDOW_TYPE = {
    PHENOLOGY_WINDOW:         ['Finestra definita dallo stadio fenologico', 'Window defined by phenological stage'],
    PREHARVEST_WINDOW:        ['Finestra definita dall’intervallo di pre-raccolta', 'Window defined by the pre-harvest interval'],
    THRESHOLD_WINDOW:         ['Finestra definita da una soglia di intervento', 'Window defined by an intervention threshold'],
    PEST_STAGE_WINDOW:        ['Finestra definita dallo stadio dell’avversita', 'Window defined by the pest stage'],
    WEATHER_TRIGGERED_WINDOW: ['Finestra aperta da una condizione meteorologica', 'Window triggered by a weather condition'],
    CALENDAR_WINDOW:          ['Finestra definita da calendario', 'Window defined by calendar'],
    RULE_DELEGATED_TO_FARM:   ['La decisione dipende dall’osservazione in campo', 'The decision depends on farm-level observation'],
  };

  /* ── LA FINESTRA · STATO DELLA REGOLA ─────────────────────────────────── */
  var WINDOW_RULE_STATE = {
    RULE_DECLARED:           ['Regola dichiarata dalla fonte', 'Rule declared by the source'],
    RULE_ADMINISTRATIVE_ONLY:['Obbligo amministrativo — non e una finestra agronomica', 'Administrative obligation — not an agronomic window'],
    RULE_DELEGATED_TO_FARM:  ['La decisione dipende dall’osservazione in campo', 'The decision depends on farm-level observation'],
    RULE_NOT_DECLARED:       ['Nessuna regola dichiarata per questa coppia', 'No rule declared for this pair'],
  };
  /* La frase lunga che la riunione deve poter leggere ad alta voce. */
  var WINDOW_RULE_STATE_LONG = {
    RULE_DECLARED:           ['La fonte dichiara la condizione che apre il momento di intervento.',
                              'The source declares the condition that opens the intervention moment.'],
    RULE_ADMINISTRATIVE_ONLY:['Quello che la fonte fissa e una data di atto amministrativo. Non dice quando trattare.',
                              'What the source sets is an administrative act date. It does not say when to treat.'],
    RULE_DELEGATED_TO_FARM:  ['La regola tecnica e nota, ma la decisione ora dipende da un’osservazione o da una misura nel frutteto.',
                              'The technical rule is known, but the decision now depends on an observation or a measurement in the orchard.'],
    RULE_NOT_DECLARED:       ['Nessuna fonte regionale dichiara la condizione che definirebbe il momento.',
                              'No regional source declares the condition that would define the moment.'],
  };

  /* ── LA FINESTRA · E APERTA ADESSO? ───────────────────────────────────── */
  var WINDOW_DEFINED = {
    YES:     ['Condizione dichiarata', 'Condition declared'],
    NO:      ['Nessuna condizione dichiarata', 'No condition declared'],
    UNKNOWN: ['Non noto', 'Not known'],
  };
  var WINDOW_OPEN_NOW = {
    YES:     ['Aperta adesso', 'Open now'],
    NO:      ['Non aperta adesso', 'Not open now'],
    UNKNOWN: ['Stato attuale non misurato', 'Current state not measured'],
  };
  /* La frase del briefing, parola per parola, per il caso piu frequente:
     condizione nota e stato attuale ancora non misurato. */
  var WINDOW_KNOWN_STATE_UNMEASURED =
    ['Condizione nota; stato attuale non ancora misurato', 'Condition known; current state not yet measured'];

  var WINDOW_OPEN_NOW_METHOD = {
    ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO: [
      'Lo stesso documento dichiara lo stadio della coltura: la finestra e aperta adesso.',
      'The same document declares the crop stage: the window is open now.'],
    FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE: [
      'La fonte dichiara la condizione come presente adesso.',
      'The source declares the condition as present now.'],
    FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE: [
      'La condizione richiede una misura che la fonte non dichiara.',
      'The condition requires a measurement the source does not declare.'],
    REGRA_EXIGE_MEDICAO_DO_POMAR_QUE_NENHUMA_FONTE_REGIONAL_TEM: [
      'La regola richiede una misura del frutteto che nessuna fonte regionale possiede.',
      'The rule requires an orchard measurement that no regional source holds.'],
    NENHUMA_CONDICAO_DECLARADA_PARA_O_PAR: [
      'Nessuna condizione dichiarata per questa coppia coltura-avversita.',
      'No condition declared for this crop-target pair.'],
    DOCUMENTO_NAO_CORRENTE: [
      'Il documento che dichiara la condizione non e corrente.',
      'The document declaring the condition is not current.'],
  };

  /* ── DIREZIONE DELLA NECESSITA · CIO CHE LA FONTE CHIEDE DAVVERO ──────── */
  var NEED_DIRECTION = {
    POSITIVE_PRESSURE:     ['La fonte segnala pressione sulla coppia', 'The source reports pressure on the pair'],
    NO_ACTION_RECOMMENDED: ['La fonte raccomanda di monitorare, non di attivare', 'The source recommends monitoring, not activating'],
    ACTION_SUSPENDED:      ['La fonte sospende l’intervento', 'The source suspends intervention'],
    TREATMENT_PROHIBITED:  ['Il trattamento e vietato in questa fase', 'Treatment is prohibited at this stage'],
    WINDOW_CONCLUDED:      ['La fonte dichiara concluso il momento di intervento', 'The source declares the intervention moment concluded'],
    NEUTRAL_MENTION:       ['Menzione neutra: la fonte non chiede nulla', 'Neutral mention: the source asks for nothing'],
    UNKNOWN:               ['Direzione non dichiarata', 'Direction not declared'],
  };
  var NEED_METHOD = {
    PAIR_IN_SAME_CLAUSE:            ['coppia nella stessa frase', 'pair in the same clause'],
    PAIR_IN_DOCUMENT_TITLE:         ['coppia nel titolo del documento', 'pair in the document title'],
    CROP_FROM_PRECEDING_CLAUSE:     ['coltura dalla frase precedente', 'crop from the preceding clause'],
    CROP_FROM_SINGLE_CROP_DOCUMENT: ['documento di una sola coltura', 'single-crop document'],
  };

  /* ── STADIO DELL’AVVERSITA E RACCOMANDAZIONE ─────────────────────────
     DUE DOMANDE DIVERSE. Il volo puo essere finito E la raccomandazione puo
     restare attiva: lo schermo non deve MAI far discendere la seconda dalla
     prima. */
  var PEST_STAGE_STATE = {
    STAGE_PEAK:         ['Stadio al culmine', 'Stage at peak'],
    STAGE_DECLINING:    ['Stadio in calo', 'Stage declining'],
    STAGE_ENDED:        ['Stadio concluso', 'Stage ended'],
    STAGE_NOT_DECLARED: ['Stadio non dichiarato', 'Stage not declared'],
  };
  var ACTION_RECOMMENDATION_STATE = {
    START_RECOMMENDED:           ['La fonte raccomanda di iniziare', 'The source recommends starting'],
    CONTINUE_RECOMMENDED:        ['La fonte raccomanda di continuare', 'The source recommends continuing'],
    SUSPEND_RECOMMENDED:         ['La fonte raccomanda di sospendere', 'The source recommends suspending'],
    CONCLUDED_DECLARED:          ['La fonte dichiara concluso l’intervento', 'The source declares intervention concluded'],
    NOT_NEEDED_DECLARED:         ['La fonte dichiara che non servono interventi', 'The source declares no intervention is needed'],
    PROHIBITED_DECLARED:         ['La fonte dichiara il trattamento vietato', 'The source declares treatment prohibited'],
    RECOMMENDATION_NOT_DECLARED: ['Nessuna raccomandazione dichiarata', 'No recommendation declared'],
  };
  var THRESHOLD_STATE = {
    NOT_APPLICABLE: ['Soglia non applicabile a questa coppia', 'Threshold not applicable to this pair'],
    NOT_DECLARED:   ['Soglia non dichiarata dalla fonte', 'Threshold not declared by the source'],
  };
  /* La frase che la riunione deve sentire sul caso Veneto x carpocapsa. */
  var STAGE_VS_ACTION_NOTE =
    ['Lo stadio dell’avversita e la raccomandazione della fonte sono due letture distinte: la fine del volo non chiude da sola l’intervento.',
     'The pest stage and the source’s recommendation are two separate readings: the end of the flight does not by itself close the intervention.'];

  /* ── PERCHE ADESSO · LA CATENA ────────────────────────────────────────── */
  var WHY_NOW_CODES = {
    CADEIA_COMPLETA:            ['Finestra agronomica aperta', 'Agronomic window open'],
    SEM_SINAL_ATUAL:            ['Nessun segnale corrente', 'No current signal'],
    SEM_JANELA_DEFINIDA:        ['Nessuna finestra definita', 'No window defined'],
    SEM_JANELA_ABERTA_AGORA:    ['Finestra non aperta adesso', 'Window not open now'],
    SEM_VINCULO_COM_PORTFOLIO:  ['Nessun legame con il portafoglio', 'No portfolio link'],
    SEM_TEMPO_PARA_ACAO:        ['Nessun tempo provato per agire', 'No proven time to act'],
  };
  var WHY_NOW_CHAIN_LINK = {
    SINAL_ATUAL:            ['Segnale corrente', 'Current signal'],
    JANELA_DEFINIDA:        ['Finestra definita', 'Window defined'],
    JANELA_ABERTA_AGORA:    ['Finestra aperta adesso', 'Window open now'],
    VINCULO_COM_PORTFOLIO:  ['Legame con il portafoglio', 'Portfolio link'],
    TEMPO_PARA_ACAO:        ['Tempo per agire', 'Time to act'],
  };
  var CHAIN_STATE = {
    OK:      ['regge', 'holds'],
    MISSING: ['manca', 'missing'],
  };

  /* ── PERCHE E UN’OPPORTUNITA COMMERCIALE ───────────────────────────── */
  var WHY_COMMERCIAL_CODES = {
    ALL_GATES_CLOSE:               ['Tutti i portoni chiudono sulla stessa affermazione', 'Every gate closes on the same claim'],
    TIME_FROM_SOURCE_RECOMMENDATION:['Il tempo viene dalla raccomandazione corrente della fonte', 'The timing comes from the source’s current recommendation'],
    NEED_CLOSED:                   ['La necessita e chiusa da una frase della fonte', 'The need is closed by a source sentence'],
    NEED_NOT_POSITIVE:             ['La necessita non e positiva: la fonte non chiede di agire', 'The need is not positive: the source does not ask for action'],
    OPENING_WITHOUT_NEED:          ['C’e un’apertura, ma nessuna necessita dichiarata', 'There is an opening, but no declared need'],
    NEITHER_NEED_NOR_OPENING:      ['Ne necessita ne apertura dichiarate', 'Neither need nor opening declared'],
    LABEL_WITHOUT_CATALOG:         ['L’etichetta copre la coppia, il catalogo non dichiara la coltura', 'The label covers the pair, the catalogue does not declare the crop'],
    REGULATORY_BY_NATURE:          ['L’opportunita e normativa per natura', 'The opportunity is regulatory by nature'],
    REGULATORY_WITHOUT_CATALOG:    ['Fatto normativo senza prodotto a catalogo collegato', 'Regulatory fact with no linked catalogue product'],
  };

  /* ── CIO CHE MANCA ────────────────────────────────────────────────────── */
  var WHAT_IS_MISSING = {
    INTENSITY_UNKNOWN:              ['Intensita della pressione non nota', 'Pressure intensity not known'],
    RECURRENCE_UNKNOWN:             ['Ricorrenza non nota', 'Recurrence not known'],
    DIRECTION_UNKNOWN:              ['Direzione della necessita non nota', 'Direction of the need not known'],
    OFFICIAL_AREA_NOT_CLIENT_SAFE:  ['Superficie ufficiale non pubblicabile', 'Official area not publishable'],
    REGION_NOT_DECLARED:            ['Regione non dichiarata', 'Region not declared'],
    SIGNAL_NOT_RECENT:              ['Segnale non recente', 'Signal not recent'],
    NO_AGRONOMIC_TARGET:            ['Nessuna avversita agronomica dichiarata', 'No agronomic target declared'],
    COMMERCIAL_PRODUCT_MISSING:     ['Nessun prodotto commerciale collegato', 'No commercial product linked'],
    WINDOW_RULE_MISSING:            ['Regola della finestra non dichiarata', 'Window rule not declared'],
    WINDOW_STATE_UNKNOWN:           ['Stato della finestra non misurato', 'Window state not measured'],
    WINDOW_RULE_DELEGATED_TO_FARM:  ['La regola rimanda alla misura in campo', 'The rule defers to a field measurement'],
    WINDOW_RULE_ADMINISTRATIVE_ONLY:['La regola e solo amministrativa', 'The rule is administrative only'],
  };

  /* ── LA MAPPA DELLE AZIONI · DAL MOTORE, MAI DEDOTTA QUI ──────────────── */
  var DEPARTMENT = {
    MARKET_DEVELOPMENT:   ['SVILUPPO DI MERCATO', 'MARKET DEVELOPMENT'],
    COMMERCIAL:           ['COMMERCIALE', 'COMMERCIAL'],
    MARKETING:            ['MARKETING', 'MARKETING'],
    TECHNICAL_SCIENTIFIC: ['TECNICO E SCIENTIFICO', 'TECHNICAL AND SCIENTIFIC'],
    SUPPLY:               ['APPROVVIGIONAMENTO', 'SUPPLY'],
  };
  var ACTION_STATE = {
    ACT:       ['AGIRE', 'ACT'],
    VALIDATE:  ['VALIDARE', 'VALIDATE'],
    PREPARE:   ['PREPARARE', 'PREPARE'],
    WATCH:     ['OSSERVARE', 'WATCH'],
    NO_ACTION: ['NESSUN MOVIMENTO', 'NO MOVEMENT'],
  };
  var ACTION = {
    CONTACT_NOW:                  ['Contattare il cliente adesso', 'Contact the customer now'],
    MESSAGE_AVAILABLE:            ['Il messaggio e disponibile', 'The message is available'],
    CONFIRM_RECOMMENDATION_IN_FIELD:['Confermare la raccomandazione in campo', 'Confirm the recommendation in the field'],
    CONFIRM_WINDOW_CONDITION_MET: ['Confermare che la condizione della finestra sia soddisfatta', 'Confirm the window condition is met'],
    CONFIRM_AT_FARM_LEVEL:        ['Confermare a livello aziendale', 'Confirm at farm level'],
    VALIDATE_AT_FARM_LEVEL:       ['Validare a livello aziendale', 'Validate at farm level'],
    VALIDATE_WINDOW_IN_REGION:    ['Validare la finestra nella regione', 'Validate the window in the region'],
    ESTABLISH_WINDOW_CONDITION:   ['Stabilire la condizione della finestra', 'Establish the window condition'],
    WATCH_REGULATORY_DATE:        ['Sorvegliare la data normativa', 'Watch the regulatory date'],
    PREPARE:                      ['Preparare', 'Prepare'],
    NO_MOVEMENT:                  ['Nessun movimento', 'No movement'],
    NOT_CONVENED:                 ['Non convocato su questo caso', 'Not convened on this case'],
  };
  var ACTION_WHY_CODE = {
    CADEIA_COMPLETA:                    ['la catena regge in tutti i suoi elo', 'the chain holds in every link'],
    SINAL_ATUAL_COM_ALVO:               ['segnale corrente con avversita dichiarata', 'current signal with a declared target'],
    CONDICAO_DECLARADA_ESTADO_DESCONHECIDO:['condizione dichiarata, stato attuale non misurato', 'condition declared, current state not measured'],
    SEM_CONDICAO_DECLARADA:             ['nessuna condizione dichiarata', 'no declared condition'],
    SEM_SINAL_ATUAL:                    ['nessun segnale corrente', 'no current signal'],
    SEM_BASE_FACTUAL:                   ['nessuna base fattuale', 'no factual basis'],
    SEM_PRIORIDADE_COMERCIAL:           ['nessuna priorita commerciale', 'no commercial priority'],
    PRIORIDADE_COMERCIAL_SEM_TEMPO_PROVADO:['priorita commerciale senza tempo provato', 'commercial priority without proven timing'],
    NADA_A_VALIDAR:                     ['non c’e nulla da validare', 'there is nothing to validate'],
    NAO_AUTORIZADO_A_SAIR:              ['non autorizzato a uscire all’esterno', 'not cleared to go outside'],
    REGRA_DELEGADA_AO_POMAR:            ['la regola rimanda alla misura nel frutteto', 'the rule defers to the orchard measurement'],
    DATA_REGULATORIA_EM_ATIVO_LIGADO:   ['data normativa su una sostanza attiva collegata', 'regulatory date on a linked active substance'],
    EXTERNAL_MATERIAL_READY:            ['il materiale esterno e pronto', 'the external material is ready'],
  };

  /* ── CIO CHE SBLOCCA · LA DIPENDENZA E IL PROSSIMO INNESCO ────────────
     `DEPENDENCY` parla il vocabolario della catena: sono gli stessi elo di
     WHY_NOW_CHAIN, e si leggono con quelle parole.

     `NEXT_TRIGGER` no. MISURATO: i suoi due soli valori sono FRASI DI RICERCA
     IN PORTOGHESE, scritte per il pacchetto e non per il cliente italiano.
     Sono un vocabolario CHIUSO di due voci, e qui ricevono la frase nelle due
     lingue della riunione.

         IL PORTOGHESE DELLA RICERCA NON ARRIVA A UN ITALIANO.

     La chiave e la frase originale per intero: cosi, se il motore ne emette
     una terza, il portone la vede subito come priva di traduzione invece di
     lasciarla passare. */
  var NEXT_TRIGGER = {
    'evidencia de que a condicao declarada esta satisfeita agora \u2014 estadio, limiar medido, captura ou evento climatico':
      ['una prova che la condizione dichiarata sia soddisfatta adesso: stadio, soglia misurata, cattura o evento climatico',
       'evidence that the declared condition is met now: stage, measured threshold, trap catch or weather event'],
    'um boletim novo que declare necessidade positiva':
      ['un bollettino nuovo che dichiari una necessita positiva',
       'a new bulletin declaring a positive need'],
  };

  /* ── LE PROVE · IL RUOLO REALE, COMPRESO QUELLO CHE RAFFREDDA ─────────── */
  var EVIDENCE_ROLE = {
    SUPPORTS_SIGNAL:            ['sostiene il segnale', 'supports the signal'],
    SUPPORTS_WINDOW:            ['sostiene la finestra', 'supports the window'],
    SUPPORTS_DIRECTION:         ['sostiene la direzione', 'supports the direction'],
    SUPPORTS_PRODUCT_MATCH:     ['sostiene il legame con il prodotto', 'supports the product match'],
    SUPPORTS_COMMERCIAL_ACTION: ['sostiene l’azione commerciale', 'supports the commercial action'],
    SUPPORTS_REGIONAL_CONTEXT:  ['sostiene il contesto regionale', 'supports the regional context'],
    BACKGROUND_ONLY:            ['solo contesto: non decide nessun elo', 'background only: it decides no link'],
    /* I tre ruoli che RAFFREDDANO. Il motore oggi non ne emette nessuno sui 43
       casi (misurato: zero occorrenze), ma le frasi sono quelle concordate e
       stanno qui pronte: il giorno che il motore ne emette uno, lo schermo lo
       sa gia dire, e nessuno dovra inventarlo di corsa. */
    WEAKENS:     ['Questa evidenza riduce l’urgenza commerciale', 'This evidence lowers the commercial urgency'],
    CONTRADICTS: ['Questa evidenza contraddice la lettura', 'This evidence contradicts the reading'],
    CLOSES:      ['Il monitoraggio non sostiene un’azione ora', 'Monitoring does not support action now'],
  };
  var EVIDENCE_ROLE_WHY = {
    OBSERVACAO_DE_CAMPO_NA_MESMA_REGIAO: ['osservazione di campo nella stessa regione', 'field observation in the same region'],
    DECLARA_A_CONDICAO_DA_JANELA:        ['dichiara la condizione della finestra', 'declares the window condition'],
    DECLARA_A_REGRA_DO_MOMENTO:          ['dichiara la regola del momento', 'declares the rule of the moment'],
    FRASE_QUE_DECIDIU_A_DIRECAO:         ['la frase che ha deciso la direzione', 'the sentence that decided the direction'],
    ROTULO_MINISTERIAL_NO_PAR:           ['etichetta ministeriale sulla coppia', 'ministerial label on the pair'],
    MOVIMENTO_DE_CONCORRENTE:            ['movimento di un concorrente', 'a competitor movement'],
    CONTEXTO_DE_MERCADO:                 ['contesto di mercato', 'market context'],
    NAO_DECIDE_NENHUM_ELO:               ['non decide nessun elo', 'it decides no link'],
  };
  var EVIDENCE_FAMILY = {
    FIELD_SIGNAL:               ['Bollettino di campo', 'Field bulletin'],
    LABEL_USE_RELATIONSHIP:     ['Relazione d’uso in etichetta', 'Label use relationship'],
    SCIENTIFIC_RECORD:          ['Documento scientifico', 'Scientific record'],
    COMPETITOR_ACTIVITY:        ['Attivita di un concorrente', 'Competitor activity'],
    MARKET_OBSERVATION:         ['Osservazione di mercato', 'Market observation'],
    REGULATORY_FUTURE_FACT:     ['Fatto normativo futuro', 'Future regulatory fact'],
    REGULATORY_PRODUCT:         ['Registrazione del prodotto', 'Product registration'],
    RESISTANCE_RECORD:          ['Registro di resistenza', 'Resistance record'],
    ACTIVE_INGREDIENT:          ['Sostanza attiva', 'Active substance'],
    CROP_ECONOMIC_WEIGHT_CLAIM: ['Peso economico della coltura', 'Crop economic weight'],
    CROP_WINDOW:                ['Finestra colturale', 'Crop window'],
  };

  /* ── IL PORTAFOGLIO ───────────────────────────────────────────────────── */
  var PRODUCT_FIT = {
    /* CROP_FIT */
    DECLARED_ON_CATALOG_PAGE:  ['coltura dichiarata nella pagina di catalogo', 'crop declared on the catalogue page'],
    /* TARGET_FIT */
    ON_MINISTERIAL_LABEL:      ['avversita presente sull’etichetta ministeriale', 'target on the ministerial label'],
    /* REGIONAL_FIT */
    NATIONAL_AUTHORIZATION_CONTAINS_REGION: ['autorizzazione nazionale che comprende la regione', 'national authorisation covering the region'],
    /* REGULATORY_FIT */
    AUTHORIZATION_LIVE:        ['autorizzazione in vigore', 'authorisation live'],
    /* WINDOW_FIT */
    YES:                       ['compatibile con la finestra', 'fits the window'],
    NO:                        ['non compatibile con la finestra', 'does not fit the window'],
    UNKNOWN:                   ['non noto', 'not known'],
  };
  var VALIDATION_STATE = {
    LABEL_AND_CATALOG: ['Etichetta e catalogo', 'Label and catalogue'],
    LABEL_ONLY:        ['Solo etichetta', 'Label only'],
  };
  var MATCH_REASON = {
    REGISTRATION_NUMBER_JOIN: ['unito per numero di registrazione', 'joined on registration number'],
  };
  var PRIMARY_MATCH_REASON = {
    UNICO_PRODUTO_DO_CATALOGO_NO_PAR:   ['unico prodotto di catalogo sulla coppia', 'the only catalogue product on the pair'],
    SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER: ['nessuna regola difendibile per sceglierne uno', 'no defensible rule to pick one'],
  };
  var PRODUCT_LINK_STATE = {
    VERIFIED_LABEL_MATCH: ['Legame verificato in etichetta', 'Verified label match'],
    RELATED_PORTFOLIO:    ['Portafoglio correlato', 'Related portfolio'],
  };
  var RESTRICTION = {
    EU_APPROVAL_EXPIRES: ['Approvazione europea in scadenza', 'EU approval expiring'],
  };
  var MODE_OF_ACTION_STATE = {
    CLASSIFIED: ['Meccanismo d’azione classificato', 'Mode of action classified'],
    UNKNOWN:    ['Meccanismo d’azione non noto', 'Mode of action not known'],
  };
  var APPLICATION_STATE = {
    QUOTED_ON_LABEL: ['Impiego citato in etichetta', 'Use quoted on the label'],
    UNKNOWN:         ['Impiego non noto', 'Use not known'],
  };

  /* ── PUBBLICAZIONE · COSA REGGE FUORI DA QUESTA STANZA ────────────────── */
  var PUBLICATION_STATE = {
    PUBLISHABLE:         ['COMPROVATO', 'PROVEN'],
    VALIDATION_REQUIRED: ['IN VALIDAZIONE', 'IN VALIDATION'],
  };
  var PUBLICATION_STATE_LONG = {
    PUBLISHABLE:         ['Il metodo regge: questa lettura puo uscire da qui.',
                          'The method holds: this reading can leave this room.'],
    VALIDATION_REQUIRED: ['Lettura sostenuta ma non ancora validata: non va presentata come affermazione provata.',
                          'A supported reading, not yet validated: it must not be presented as a proven claim.'],
  };
  var TRAIL_STATE = {
    COMPLETE: ['Tracciato completo', 'Trail complete'],
  };
  var OPPORTUNITY_STATE = {
    OPPORTUNITY_CONFIRMED: ['CONVERGENZA VERIFICATA', 'VERIFIED CONVERGENCE'],
    OPPORTUNITY_CANDIDATE: ['DA VALIDARE', 'TO VALIDATE'],
  };
  var EXTERNAL_MATERIAL_READY = {
    YES: ['Materiale esterno pronto', 'External material ready'],
    NO:  ['Materiale esterno non pronto', 'External material not ready'],
  };
  var EXTERNAL_BLOCKER = {
    NOT_SALES_READY: ['non ancora pronta per la vendita', 'not sales ready yet'],
  };

  /* ── SEGNALE, TEMPO E AMPIEZZA ───────────────────────────────────────── */
  var SIGNAL_CURRENCY = {
    CURRENT: ['Segnale corrente', 'Current signal'],
    RECENT:  ['Segnale recente', 'Recent signal'],
    OLD:     ['Segnale non recente', 'Signal not recent'],
    UNKNOWN: ['Eta del segnale non nota', 'Signal age not known'],
  };
  var COMMERCIAL_TIMING_BASIS = {
    CURRENT_SOURCE_RECOMMENDATION: ['Tempo dalla raccomandazione corrente della fonte', 'Timing from the source’s current recommendation'],
    NONE:                          ['Nessuna base temporale dichiarata', 'No declared timing basis'],
  };
  var GEOGRAPHIC_SCOPE = {
    PROVINCIAL: ['Provinciale', 'Provincial'],
    REGIONAL:   ['Regionale', 'Regional'],
    NACIONAL:   ['Nazionale', 'National'],
    EUROPEU:    ['Europea', 'European'],
  };
  var COMMERCIAL_MAGNITUDE = {
    MEASURED_BY_DIMENSION: ['Misurata per dimensioni', 'Measured by dimension'],
    UNKNOWN:               ['Magnitudine non nota', 'Magnitude not known'],
  };
  var MAGNITUDE_DIMENSION = {
    SINAIS_DE_CAMPO:      ['segnali di campo', 'field signals'],
    FONTES_INDEPENDENTES: ['fonti indipendenti', 'independent sources'],
    REGIOES_DO_PAR:       ['regioni della coppia', 'regions on the pair'],
    AREA_OFICIAL_HA:      ['superficie ufficiale (ha)', 'official area (ha)'],
    AREA_OFICIAL_ANO:     ['anno della superficie ufficiale', 'official area year'],
    AREA_SELECTION_RULE:  ['regola di scelta della superficie', 'area selection rule'],
    AREA_EVIDENCE_ID:     ['prova della superficie', 'area evidence'],
  };

  /* ── IL BRIEF · FRASI COMPOSTE DAI CODICI DEL MOTORE ──────────────────
     {X} sono i VALORI che il motore porta. Nessuna frase aggiunge un fatto. */
  var BRIEF = {
    PRESSAO_RECENTE: ['Pressione recente di {ALVO} su {CULTURA} in {REGIAO}, sostenuta da {SINAIS} segnali di campo e {FONTES} fonti indipendenti.',
                      'Recent {ALVO} pressure on {CULTURA} in {REGIAO}, supported by {SINAIS} field signals and {FONTES} independent sources.'],
    FONTE_MANDA_PARAR: ['La fonte che sostiene la coppia non chiede di agire.',
                        'The source supporting the pair does not ask for action.'],
    JANELA_ABERTA: ['La condizione che definisce il momento e dichiarata e lo stesso documento dichiara lo stadio della coltura: la finestra e aperta adesso.',
                    'The condition defining the moment is declared and the same document declares the crop stage: the window is open now.'],
    JANELA_DEFINIDA_ESTADO_DESCONHECIDO: ['La condizione e nota, ma il suo stato attuale non e stato misurato.',
                                          'The condition is known, but its current state has not been measured.'],
    JANELA_DELEGADA_AO_POMAR: ['La regola e nota e rimanda a una misura nel frutteto.',
                               'The rule is known and defers to a measurement in the orchard.'],
    SEM_JANELA: ['Nessuna finestra definita per questa coppia.', 'No window defined for this pair.'],
    PORTFOLIO: ['{PRODUTOS} prodotti ADAMA reggono sulla coppia.', '{PRODUTOS} ADAMA products hold on the pair.'],
    SEM_PORTFOLIO: ['Nessun prodotto ADAMA collegato alla coppia.', 'No ADAMA product linked to the pair.'],
    ACAO_PRINCIPAL: ['Prossimo movimento: {DEPARTAMENTO} — {ACAO}.', 'Next movement: {DEPARTAMENTO} — {ACAO}.'],
    FONTE_NOMEIA_OUTRA_SUBSTANCIA: ['La fonte nomina un’altra sostanza attiva.', 'The source names a different active substance.'],
  };

  /* ── I NOMI PROPRI · colture, avversita, geografie ────────────────────
     Sono i nomi che il pacchetto canonico gia pubblica. Il guardiano li
     confronta con la risoluzione del modello: se divergono, fallisce. */
  var CROP = {
    CROP_APPLE:        ['Melo', 'Apple'],
    CROP_BARLEY:       ['Orzo', 'Barley'],
    CROP_CITRUS:       ['Agrumi', 'Citrus'],
    CROP_GRAPEVINE:    ['Vite', 'Grapevine'],
    CROP_MAIZE:        ['Mais', 'Maize'],
    CROP_OLIVE:        ['Olivo', 'Olive'],
    CROP_RICE:         ['Riso', 'Rice'],
    CROP_SOYBEAN:      ['Soia', 'Soybean'],
    CROP_SUGAR_BEET:   ['Barbabietola da zucchero', 'Sugar beet'],
    CROP_TOMATO:       ['Pomodoro', 'Tomato'],
    CROP_VEGETABLES:   ['Orticole', 'Vegetables'],
    CROP_WHEAT_GENERIC:['Frumento', 'Wheat'],
  };
  var TARGET = {
    ISSUE_BOTRYTIS:       ['Botrite', 'Botrytis'],
    ISSUE_CODLING_MOTH:   ['Carpocapsa', 'Codling moth'],
    ISSUE_CORN_BORER:     ['Piralide', 'European corn borer'],
    ISSUE_DIABROTICA:     ['Diabrotica', 'Diabrotica'],
    ISSUE_DOWNY_MILDEW:   ['Peronospora', 'Downy mildew'],
    ISSUE_ECHINOCHLOA:    ['Echinochloa', 'Echinochloa'],
    ISSUE_GRAPE_MOTH:     ['Tignoletta della vite', 'Grape moth'],
    ISSUE_POWDERY_MILDEW: ['Oidio', 'Powdery mildew'],
    ISSUE_SCAPHOIDEUS:    ['Scaphoideus titanus', 'Scaphoideus titanus'],
  };
  var GEOGRAPHY = {
    GEO_EU:                       ['Unione Europea', 'European Union'],
    GEO_ITALY:                    ['Italia', 'Italy'],
    REGION_EMILIA_ROMAGNA:        ['Emilia-Romagna', 'Emilia-Romagna'],
    REGION_FRIULI_VENEZIA_GIULIA: ['Friuli-Venezia Giulia', 'Friuli-Venezia Giulia'],
    REGION_LOMBARDIA:             ['Lombardia', 'Lombardia'],
    REGION_TOSCANA:               ['Toscana', 'Toscana'],
    REGION_UMBRIA:                ['Umbria', 'Umbria'],
    REGION_VENETO:                ['Veneto', 'Veneto'],
  };

  /* ── LE PAROLE DELLO SCHERMO ─────────────────────────────────────────── */
  var UI = {
    navCanonical:      ['Radar Canonico', 'Canonical Radar'],
    subCanonical:      ['I 43 casi che hanno attraversato per intero la trilha dell’intelligenza — nessuna prosa scritta a mano, nessun caso di presentazione.',
                        'The 43 cases that travelled the full intelligence trail — no hand-written prose, no presentation cases.'],
    lblCanonicalUniverse: ['ACERVO CANONICO', 'CANONICAL SET'],
    lblDemoSet:        ['CASI DI PRESENTAZIONE', 'PRESENTATION CASES'],
    lblDemoNote:       ['Insieme separato, scritto a mano per la dimostrazione. Non entra in nessun conteggio del motore.',
                        'A separate, hand-written demonstration set. It enters no engine count.'],
    lblCases:          ['CASI', 'CASES'],
    lblOf:             ['di', 'of'],
    lblTotal:          ['Casi canonici', 'Canonical cases'],
    lblProven:         ['Comprovati', 'Proven'],
    lblInValidation:   ['In validazione', 'In validation'],
    lblWindowDefined:  ['Finestra definita', 'Window defined'],
    lblWindowOpenNow:  ['Finestra aperta adesso', 'Window open now'],
    lblWhatIsHappening:['CHE COSA STA SUCCEDENDO', 'WHAT IS HAPPENING'],
    lblWhyCommercial:  ['PERCHE E UN’OPPORTUNITA PER ADAMA', 'WHY THIS IS AN ADAMA OPPORTUNITY'],
    lblWhyNow:         ['PERCHE ADESSO', 'WHY NOW'],
    lblWhyNotNow:      ['PERCHE NON ANCORA', 'WHY NOT YET'],
    lblWindow:         ['LA FINESTRA', 'THE WINDOW'],
    lblProducts:       ['PRODOTTI ADAMA CHE REGGONO', 'ADAMA PRODUCTS THAT HOLD'],
    lblWhatIsMissing:  ['CHE COSA MANCA', 'WHAT IS MISSING'],
    lblActionMap:      ['CHI DEVE AGIRE', 'WHO SHOULD ACT'],
    lblEvidence:       ['LE PROVE', 'THE EVIDENCE'],
    lblSource:         ['FONTI', 'SOURCES'],
    lblStage:          ['STADIO DELL’AVVERSITA', 'PEST STAGE'],
    lblRecommendation: ['RACCOMANDAZIONE DELLA FONTE', 'SOURCE RECOMMENDATION'],
    lblThreshold:      ['SOGLIA', 'THRESHOLD'],
    lblSignal:         ['SEGNALE', 'SIGNAL'],
    lblPrimary:        ['PRINCIPALE', 'PRIMARY'],
    lblNoPrimary:      ['Nessun prodotto principale: non c’e una regola difendibile per sceglierne uno.',
                        'No primary product: there is no defensible rule to pick one.'],
    lblNoProducts:     ['Nessun prodotto ADAMA collegato a questa coppia.', 'No ADAMA product linked to this pair.'],
    lblAllProducts:    ['Tutti i prodotti che reggono sono elencati.', 'Every product that holds is listed.'],
    lblDependency:     ['dipende da', 'depends on'],
    lblNextTrigger:    ['prossimo innesco', 'next trigger'],
    lblRestrictions:   ['LIMITI', 'RESTRICTIONS'],
    lblActive:         ['sostanze attive', 'active substances'],
    lblMoA:            ['meccanismo d’azione', 'mode of action'],
    lblRegistration:   ['registrazione', 'registration'],
    lblOpen:           ['APRI', 'OPEN'],
    lblBack:           ['INDIETRO', 'BACK'],
    lblEvidenceCount:  ['prove', 'evidence items'],
    lblDeclaredIn:     ['La condizione e dichiarata nel documento', 'The condition is declared in document'],
    lblSourceDoc:      ['documento', 'document'],
    lblArchetype:      ['PERCHE ESISTE', 'WHY IT EXISTS'],
    lblPriority:       ['PRIORITA COMMERCIALE', 'COMMERCIAL PRIORITY'],
    lblScope:          ['AMPIEZZA', 'SCOPE'],
    lblNoTarget:       ['Nessuna avversita agronomica: e un momento di mercato.', 'No agronomic target: this is a market moment.'],
    lblFilterAll:      ['Tutti', 'All'],
    lblFilterStatus:   ['Stato', 'Status'],
    lblFilterCrop:     ['Coltura', 'Crop'],
    lblFilterRegion:   ['Geografia', 'Geography'],
    lblFilterPriority: ['Priorita', 'Priority'],
    lblFilterPublication:['Pubblicazione', 'Publication'],
    lblClear:          ['Azzera', 'Clear'],
    lblNoResults:      ['Nessun caso con questi filtri.', 'No case matches these filters.'],
    lblSnapshot:       ['Istantanea dell’intelligenza', 'Intelligence snapshot'],
    lblEngineDecides:  ['Il motore decide, lo schermo presenta.', 'The engine decides, the screen presents.'],
  };

  var FAMILIES = {
    STATUS: STATUS,
    COMMERCIAL_PRIORITY: COMMERCIAL_PRIORITY,
    COMMERCIAL_PRIORITY_WHY: COMMERCIAL_PRIORITY_WHY,
    ARCHETYPE: ARCHETYPE,
    WINDOW_TYPE: WINDOW_TYPE,
    WINDOW_RULE_STATE: WINDOW_RULE_STATE,
    WINDOW_RULE_STATE_LONG: WINDOW_RULE_STATE_LONG,
    WINDOW_DEFINED: WINDOW_DEFINED,
    WINDOW_OPEN_NOW: WINDOW_OPEN_NOW,
    WINDOW_OPEN_NOW_METHOD: WINDOW_OPEN_NOW_METHOD,
    NEED_DIRECTION: NEED_DIRECTION,
    NEED_METHOD: NEED_METHOD,
    PEST_STAGE_STATE: PEST_STAGE_STATE,
    ACTION_RECOMMENDATION_STATE: ACTION_RECOMMENDATION_STATE,
    THRESHOLD_STATE: THRESHOLD_STATE,
    WHY_NOW_CODES: WHY_NOW_CODES,
    WHY_NOW_CHAIN_LINK: WHY_NOW_CHAIN_LINK,
    CHAIN_STATE: CHAIN_STATE,
    WHY_COMMERCIAL_CODES: WHY_COMMERCIAL_CODES,
    WHAT_IS_MISSING: WHAT_IS_MISSING,
    DEPARTMENT: DEPARTMENT,
    ACTION_STATE: ACTION_STATE,
    ACTION: ACTION,
    ACTION_WHY_CODE: ACTION_WHY_CODE,
    NEXT_TRIGGER: NEXT_TRIGGER,
    EVIDENCE_ROLE: EVIDENCE_ROLE,
    EVIDENCE_ROLE_WHY: EVIDENCE_ROLE_WHY,
    EVIDENCE_FAMILY: EVIDENCE_FAMILY,
    PRODUCT_FIT: PRODUCT_FIT,
    VALIDATION_STATE: VALIDATION_STATE,
    MATCH_REASON: MATCH_REASON,
    PRIMARY_MATCH_REASON: PRIMARY_MATCH_REASON,
    PRODUCT_LINK_STATE: PRODUCT_LINK_STATE,
    RESTRICTION: RESTRICTION,
    MODE_OF_ACTION_STATE: MODE_OF_ACTION_STATE,
    APPLICATION_STATE: APPLICATION_STATE,
    PUBLICATION_STATE: PUBLICATION_STATE,
    PUBLICATION_STATE_LONG: PUBLICATION_STATE_LONG,
    TRAIL_STATE: TRAIL_STATE,
    OPPORTUNITY_STATE: OPPORTUNITY_STATE,
    EXTERNAL_MATERIAL_READY: EXTERNAL_MATERIAL_READY,
    EXTERNAL_BLOCKER: EXTERNAL_BLOCKER,
    SIGNAL_CURRENCY: SIGNAL_CURRENCY,
    COMMERCIAL_TIMING_BASIS: COMMERCIAL_TIMING_BASIS,
    GEOGRAPHIC_SCOPE: GEOGRAPHIC_SCOPE,
    COMMERCIAL_MAGNITUDE: COMMERCIAL_MAGNITUDE,
    MAGNITUDE_DIMENSION: MAGNITUDE_DIMENSION,
    BRIEF: BRIEF,
    CROP: CROP,
    TARGET: TARGET,
    GEOGRAPHY: GEOGRAPHY,
    UI: UI,
  };

  /* Frasi singole che non appartengono a una famiglia di gettoni. */
  var PHRASE = {
    WINDOW_KNOWN_STATE_UNMEASURED: WINDOW_KNOWN_STATE_UNMEASURED,
    STAGE_VS_ACTION_NOTE: STAGE_VS_ACTION_NOTE,
  };

  var IDX = { it: 0, en: 1 };

  /* Un gettone senza frase NON esce sullo schermo: torna null, e chi chiama
     mostra il blocco solo quando c'e una parola umana da mostrare. Il gettone
     grezzo non e mai una risposta accettabile. */
  function label(lang, family, token) {
    var f = FAMILIES[family];
    if (!f || token === null || token === undefined || token === '') return null;
    var row = f[String(token)];
    if (!row) return null;
    return row[IDX[lang] === 1 ? 1 : 0] || row[0] || null;
  }
  function phrase(lang, key) {
    var row = PHRASE[key];
    if (!row) return null;
    return row[IDX[lang] === 1 ? 1 : 0] || row[0] || null;
  }
  /* Il brief: la frase del codice con i VALORI del motore sostituiti. Un
     segnaposto senza valore fa cadere la frase intera, perche una frase con
     {CULTURA} stampato dentro e peggio di nessuna frase. */
  function brief(lang, code, values) {
    var t = label(lang, 'BRIEF', code);
    if (!t) return null;
    var v = values || {};
    var missing = false;
    var out = t.replace(/\{([A-Z_]+)\}/g, function (m, k) {
      var val = v[k];
      if (val === null || val === undefined || val === '') { missing = true; return m; }
      /* I nomi propri passano dal dizionario quando sono gettoni. */
      return String(label(lang, 'CROP', val) || label(lang, 'TARGET', val)
                 || label(lang, 'GEOGRAPHY', val) || label(lang, 'DEPARTMENT', val)
                 || label(lang, 'ACTION', val) || val);
    });
    return missing ? null : out;
  }

  window.MEETING_LABELS = {
    version: '1.0',
    note: 'dizionario IT/EN dei gettoni di MEETING-INTELLIGENCE-SNAPSHOT. Nessun fatto vive qui.',
    FAMILIES: FAMILIES,
    PHRASE: PHRASE,
    label: label,
    phrase: phrase,
    brief: brief,
  };
})();
