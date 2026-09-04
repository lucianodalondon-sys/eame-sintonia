/* SINTONIA · MEETING LABELS — IT / EN for every code that reaches the screen
   ---------------------------------------------------------------------------
   The canonical snapshot speaks in CODES. A code is a key, never a sentence:
   it must not change with the language, and it must never be painted.

       IL CODICE E UNA CHIAVE. LO SCHERMO NON LEGGE CHIAVI.

   This file is the ONLY place where a canonical code becomes a human phrase.
   It decides nothing: every key here already exists in the snapshot, and no
   phrase adds a fact the engine did not state.

   Where the brief dictated the wording word-for-word, the wording is verbatim
   (RULE_DELEGATED_TO_FARM, RULE_ADMINISTRATIVE_ONLY, WINDOW_DEFINED+UNKNOWN,
   WEAKENS, CLOSES). Those are not suggestions and are not paraphrased here.

       UNKNOWN NON PUO SPARIRE DIETRO UNA FRASE BEN SCRITTA.

   Loaded AFTER italy-i18n.js so the portal dictionary stays one file and this
   one stays auditable on its own — see HANDOFF §6 trap 2, decided here. */
(function () {
  /* [it, en] — one row, both languages, so a missing translation is visible
     as a hole in THIS file instead of as an English word on an Italian page. */
  const L = {

    /* ── surface chrome ─────────────────────────────────────────────── */
    navMeeting:        ['Radar Canonico', 'Canonical Radar'],
    subMeeting:        ['I casi del motore canonico — nessuno riscritto a mano',
                        'The canonical engine cases — none hand-rewritten'],
    meetingSnapshot:   ['ISTANTANEA DELLA RIUNIONE', 'MEETING SNAPSHOT'],
    lblSourceHead:     ['origine', 'source head'],
    lblBuildId:        ['build', 'build'],
    lblCutoff:         ['taglio', 'cutoff'],
    lblCases:          ['casi', 'cases'],
    lblOf:             ['di', 'of'],
    lblAll:            ['TUTTI', 'ALL'],
    secWhyCommercial:  ['PERCHE E COMMERCIALE', 'WHY COMMERCIAL'],
    secWhyNow:         ['PERCHE ORA', 'WHY NOW'],
    secWindow:         ['FINESTRA', 'WINDOW'],
    secProducts:       ['PORTAFOGLIO', 'PORTFOLIO'],
    secActionMap:      ['MAPPA DELLE AZIONI', 'ACTION MAP'],
    secEvidence:       ['EVIDENZE', 'EVIDENCE'],
    secMissing:        ['COSA MANCA', 'WHAT IS MISSING'],
    secSource:         ['FONTI', 'SOURCES'],
    lblNoPrimary:      ['Nessun prodotto principale: il motore non dichiara una regola per sceglierne uno',
                        'No primary product: the engine declares no rule for choosing one'],
    lblAllProducts:    ['Tutti i prodotti collegati, nessuno incoronato',
                        'Every linked product, none crowned'],
    lblNoProducts:     ['Nessun prodotto del catalogo collegato a questa coppia',
                        'No catalogue product linked to this pair'],
    /* La riga di prodotto della SCHEDA. Dove il motore ha nominato un
       principale, la scheda lo nomina. Dove non l'ha nominato, la scheda
       CONTA e non sceglie — «3 prodotti collegati» e vero, «BANJO +2» no. */
    lblProductsLinked: ['prodotti collegati', 'linked products'],
    lblProductLinked:  ['prodotto collegato', 'linked product'],
    lblNoProductShort: ['nessun prodotto collegato', 'no linked product'],
    lblPrimaryOne:     ['Unico prodotto del catalogo per questa coppia',
                        'The only catalogue product for this pair'],
    lblEvidenceOf:     ['evidenze', 'evidence items'],
    lblNoEvidence:     ['nessuna evidenza collegata', 'no evidence linked'],
    lblRestrictions:   ['VINCOLI', 'RESTRICTIONS'],
    lblDependency:     ['DIPENDE DA', 'DEPENDS ON'],
    lblNextTrigger:    ['COSA LO SBLOCCA', 'WHAT UNLOCKS IT'],
    lblChainBroken:    ['anello mancante', 'missing link'],
    lblChainOk:        ['anello dimostrato', 'link proven'],
    lblDocumented:     ['La condizione e dichiarata nel documento',
                        'The condition is stated in document'],
    lblPtWithheld:     ['Il testo originale della ricerca non attraversa in italiano: si cita il documento',
                        'The original research text does not cross over: the document is cited instead'],

    /* ── STATUS ─────────────────────────────────────────────────────── */
    ACT_NOW:            ['AGIRE ORA', 'ACT NOW'],
    VALIDATE_NOW:       ['VALIDARE ORA', 'VALIDATE NOW'],
    WATCH:              ['OSSERVARE', 'WATCH'],
    TO_VALIDATE:        ['DA VALIDARE', 'TO VALIDATE'],
    FUTURE_PREPARATION: ['PREPARAZIONE FUTURA', 'FUTURE PREPARATION'],

    /* ── COMMERCIAL_PRIORITY ────────────────────────────────────────── */
    SALES_READY:           ['PRONTO PER LA VENDITA', 'SALES READY'],
    STRATEGIC_OPPORTUNITY: ['OPPORTUNITA STRATEGICA', 'STRATEGIC OPPORTUNITY'],
    COMMERCIAL_WATCH:      ['OSSERVAZIONE COMMERCIALE', 'COMMERCIAL WATCH'],

    /* ── PUBLICATION_STATE · never hidden ───────────────────────────── */
    PUBLISHABLE:          ['PUBBLICABILE', 'PUBLISHABLE'],
    VALIDATION_REQUIRED:  ['RICHIEDE VALIDAZIONE', 'VALIDATION REQUIRED'],

    /* ── OPPORTUNITY_STATE ──────────────────────────────────────────── */
    OPPORTUNITY_CANDIDATE: ['candidata', 'candidate'],
    OPPORTUNITY_CONFIRMED: ['confermata', 'confirmed'],

    /* ── ARCHETYPE ──────────────────────────────────────────────────── */
    O1_FIELD_PRESSURE:        ['Pressione di campo', 'Field pressure'],
    O2_MARKET_MOMENT:         ['Momento di mercato', 'Market moment'],
    O3_RESISTANCE_MOA:        ['Resistenza e meccanismo d’azione', 'Resistance and mode of action'],
    O4_COMPETITIVE_OPENING:   ['Apertura competitiva', 'Competitive opening'],
    O5_REGULATORY_PREPARATION:['Preparazione regolatoria', 'Regulatory preparation'],
    O6_SCIENCE_TO_FIELD:      ['Dalla scienza al campo', 'Science to field'],

    /* ── WINDOW_TYPE · the brief dictates the first two, verbatim ───── */
    PHENOLOGY_WINDOW:        ['Finestra definita dallo stadio fenologico',
                              'Window defined by phenological stage'],
    RULE_DELEGATED_TO_FARM:  ['La decisione dipende dall’osservazione in campo',
                              'The decision depends on farm-level observation'],
    PREHARVEST_WINDOW:       ['Finestra definita dall’intervallo di pre-raccolta',
                              'Window defined by the pre-harvest interval'],
    THRESHOLD_WINDOW:        ['Finestra definita da una soglia da misurare',
                              'Window defined by a threshold to be measured'],
    PEST_STAGE_WINDOW:       ['Finestra definita dallo stadio dell’insetto',
                              'Window defined by the pest stage'],
    WEATHER_TRIGGERED_WINDOW:['Finestra innescata da un evento climatico',
                              'Window triggered by a weather event'],
    CALENDAR_WINDOW:         ['Finestra di calendario', 'Calendar window'],

    /* ── WINDOW_RULE_STATE · brief wording, verbatim ────────────────── */
    RULE_DECLARED:           ['Regola di intervento dichiarata dalla fonte',
                              'Intervention rule stated by the source'],
    RULE_ADMINISTRATIVE_ONLY:['Obbligo amministrativo — non e una finestra agronomica',
                              'Administrative obligation — not an agronomic window'],
    RULE_NOT_DECLARED:       ['Nessuna fonte dichiara una regola di intervento per questa coppia',
                              'No source states an intervention rule for this pair'],

    /* ── WINDOW_DEFINED vs WINDOW_OPEN_NOW · never the same sentence ── */
    windowDefinedYes:  ['La regola che definisce il momento e nota',
                        'The rule that defines the moment is known'],
    windowDefinedNo:   ['Nessuna regola di intervento dichiarata per questa coppia',
                        'No intervention rule stated for this pair'],
    windowOpenYes:     ['Finestra agronomica aperta', 'Agronomic window open'],
    windowOpenNo:      ['La condizione dichiarata non e soddisfatta ora',
                        'The stated condition is not met now'],
    windowOpenUnknown: ['Condizione nota; stato attuale non ancora misurato',
                        'Condition known; current state not yet measured'],
    windowOpenNoRule:  ['Senza una regola dichiarata non c’e uno stato da misurare',
                        'With no stated rule there is no state to measure'],
    lblRule:           ['LA REGOLA', 'THE RULE'],
    lblStateNow:       ['LO STATO ADESSO', 'THE STATE NOW'],

    /* ── WINDOW_OPEN_NOW_METHOD ─────────────────────────────────────── */
    ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO: [
      'Lo stesso documento dichiara lo stadio che la condizione richiede',
      'The same document states the stage the condition requires'],
    FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE: [
      'La fonte dichiara la condizione come presente',
      'The source states the condition as present'],
    FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE: [
      'La fonte non dichiara la misura che la condizione richiede',
      'The source does not state the measurement the condition requires'],
    REGRA_EXIGE_MEDICAO_DO_POMAR_QUE_NENHUMA_FONTE_REGIONAL_TEM: [
      'La regola richiede una misura del frutteto che nessuna fonte regionale possiede',
      'The rule requires an orchard-level measurement no regional source holds'],
    NENHUMA_CONDICAO_DECLARADA_PARA_O_PAR: [
      'Nessuna condizione dichiarata per questa coppia',
      'No condition stated for this pair'],
    DOCUMENTO_NAO_CORRENTE: [
      'Il documento che porta la condizione non e della stagione corrente',
      'The document carrying the condition is not from the current season'],

    /* ── PEST_STAGE_STATE · a stage is not an action ────────────────── */
    STAGE_PEAK:        ['Volo al culmine', 'Flight at its peak'],
    STAGE_DECLINING:   ['Volo in calo', 'Flight declining'],
    STAGE_ENDED:       ['Volo concluso', 'Flight ended'],
    STAGE_NOT_DECLARED:['Stadio non dichiarato dalla fonte', 'Stage not stated by the source'],

    /* ── ACTION_RECOMMENDATION_STATE · a different owner from the stage */
    START_RECOMMENDED:          ['La fonte raccomanda di iniziare l’intervento',
                                 'The source recommends starting the intervention'],
    CONTINUE_RECOMMENDED:       ['La fonte raccomanda di proseguire l’intervento',
                                 'The source recommends continuing the intervention'],
    SUSPEND_RECOMMENDED:        ['La fonte raccomanda di sospendere l’intervento',
                                 'The source recommends suspending the intervention'],
    CONCLUDED_DECLARED:         ['La fonte dichiara concluso l’intervento',
                                 'The source states the intervention is concluded'],
    NOT_NEEDED_DECLARED:        ['La fonte dichiara che non sono necessari interventi',
                                 'The source states no intervention is needed'],
    PROHIBITED_DECLARED:        ['Trattamento vietato dalla norma', 'Treatment prohibited by regulation'],
    RECOMMENDATION_NOT_DECLARED:['La fonte non dichiara una raccomandazione',
                                 'The source states no recommendation'],

    /* ── THRESHOLD_STATE ────────────────────────────────────────────── */
    NOT_APPLICABLE: ['Soglia non applicabile a questa coppia', 'Threshold not applicable to this pair'],
    NOT_DECLARED:   ['Soglia non dichiarata dalla fonte', 'Threshold not stated by the source'],

    /* ── NEED_DIRECTION · the source may say STOP ───────────────────── */
    POSITIVE_PRESSURE:   ['La fonte dichiara pressione in atto', 'The source states pressure is present'],
    NO_ACTION_RECOMMENDED:['La fonte raccomanda di monitorare, non di attivare',
                           'The source recommends monitoring, not activating'],
    ACTION_SUSPENDED:    ['La fonte dichiara l’intervento sospeso', 'The source states the intervention is suspended'],
    TREATMENT_PROHIBITED:['La norma vieta il trattamento', 'Regulation prohibits the treatment'],
    WINDOW_CONCLUDED:    ['La fonte dichiara la finestra conclusa', 'The source states the window is concluded'],
    NEUTRAL_MENTION:     ['Menzione neutra: la fonte non indica una direzione',
                          'Neutral mention: the source gives no direction'],
    UNKNOWN:             ['Non dichiarato', 'Not stated'],

    /* ── NEED_METHOD ────────────────────────────────────────────────── */
    PAIR_IN_DOCUMENT_TITLE:       ['La coppia e nel titolo del documento', 'The pair is in the document title'],
    PAIR_IN_SAME_CLAUSE:          ['La coppia e nella stessa frase', 'The pair is in the same clause'],
    CROP_FROM_PRECEDING_CLAUSE:   ['La coltura viene dalla frase precedente', 'The crop comes from the preceding clause'],
    CROP_FROM_SINGLE_CROP_DOCUMENT:['Il documento tratta una sola coltura', 'The document covers a single crop'],

    /* ── WHY_NOW_CODES + the five chain links ───────────────────────── */
    CADEIA_COMPLETA:          ['Finestra agronomica aperta', 'Agronomic window open'],
    SEM_JANELA_ABERTA_AGORA:  ['La condizione non risulta soddisfatta adesso', 'The condition is not met right now'],
    SEM_JANELA_DEFINIDA:      ['Nessuna regola definisce il momento', 'No rule defines the moment'],
    SEM_SINAL_ATUAL:          ['Nessun segnale di campo corrente', 'No current field signal'],
    SEM_TEMPO_PARA_ACAO:      ['Non resta tempo utile per agire', 'No usable time left to act'],
    SEM_VINCULO_COM_PORTFOLIO:['Nessun prodotto del catalogo collegato', 'No catalogue product linked'],
    SINAL_ATUAL:              ['Segnale di campo corrente', 'Current field signal'],
    JANELA_DEFINIDA:          ['Regola del momento dichiarata', 'Rule of the moment stated'],
    JANELA_ABERTA_AGORA:      ['Condizione soddisfatta adesso', 'Condition met right now'],
    VINCULO_COM_PORTFOLIO:    ['Collegamento con il portafoglio', 'Link to the portfolio'],
    TEMPO_PARA_ACAO:          ['Tempo utile per agire', 'Usable time to act'],

    /* ── WHY_COMMERCIAL_CODES ───────────────────────────────────────── */
    ALL_GATES_CLOSE:              ['Tutti i cancelli si chiudono', 'Every gate closes'],
    LABEL_WITHOUT_CATALOG:        ['Etichetta ministeriale senza voce a catalogo', 'Ministerial label with no catalogue entry'],
    NEED_CLOSED:                  ['La necessita risulta chiusa dalla fonte', 'The need is closed by the source'],
    NEED_NOT_POSITIVE:            ['La necessita non e positiva', 'The need is not positive'],
    NEITHER_NEED_NOR_OPENING:     ['Ne necessita ne apertura di mercato', 'Neither need nor market opening'],
    OPENING_WITHOUT_NEED:         ['Apertura di mercato senza necessita dichiarata', 'Market opening with no stated need'],
    REGULATORY_BY_NATURE:         ['Caso regolatorio per natura', 'Regulatory case by nature'],
    REGULATORY_WITHOUT_CATALOG:   ['Fatto regolatorio senza voce a catalogo', 'Regulatory fact with no catalogue entry'],
    TIME_FROM_SOURCE_RECOMMENDATION:['Il tempo viene dalla raccomandazione della fonte', 'Timing comes from the source recommendation'],
    NOT_SALES_READY:              ['Non ancora pronto per uscire al cliente', 'Not yet ready to go to the customer'],

    /* ── WHAT_IS_MISSING ────────────────────────────────────────────── */
    COMMERCIAL_PRODUCT_MISSING:     ['Manca un prodotto commerciale collegato', 'A linked commercial product is missing'],
    DIRECTION_UNKNOWN:              ['La direzione della fonte non e nota', 'The direction of the source is unknown'],
    INTENSITY_UNKNOWN:              ['L’intensita non e nota', 'Intensity is unknown'],
    NO_AGRONOMIC_TARGET:            ['Nessun bersaglio agronomico dichiarato', 'No agronomic target stated'],
    OFFICIAL_AREA_NOT_CLIENT_SAFE:  ['La superficie ufficiale non e utilizzabile verso il cliente', 'The official area is not client-safe'],
    RECURRENCE_UNKNOWN:             ['La ricorrenza non e nota', 'Recurrence is unknown'],
    REGION_NOT_DECLARED:            ['La regione non e dichiarata', 'The region is not stated'],
    SIGNAL_NOT_RECENT:              ['Il segnale non e recente', 'The signal is not recent'],
    WINDOW_RULE_ADMINISTRATIVE_ONLY:['La regola e solo amministrativa', 'The rule is administrative only'],
    WINDOW_RULE_DELEGATED_TO_FARM:  ['La regola e delegata all’osservazione in campo', 'The rule is delegated to farm-level observation'],
    WINDOW_RULE_MISSING:            ['Manca la regola della finestra', 'The window rule is missing'],
    WINDOW_STATE_UNKNOWN:           ['Lo stato della finestra non e misurato', 'The window state is not measured'],

    /* ── ACTION MAP · departments ───────────────────────────────────── */
    MARKET_DEVELOPMENT:  ['SVILUPPO MERCATO', 'MARKET DEVELOPMENT'],
    COMMERCIAL:          ['COMMERCIALE', 'COMMERCIAL'],
    MARKETING:           ['MARKETING', 'MARKETING'],
    TECHNICAL_SCIENTIFIC:['TECNICO / SCIENTIFICO', 'TECHNICAL / SCIENTIFIC'],
    SUPPLY:              ['SUPPLY', 'SUPPLY'],

    /* ── ACTION_STATE ───────────────────────────────────────────────── */
    ACT:      ['AGIRE', 'ACT'],
    VALIDATE: ['VALIDARE', 'VALIDATE'],
    PREPARE:  ['PREPARARE', 'PREPARE'],
    NO_ACTION:['NESSUN MOVIMENTO', 'NO MOVEMENT'],

    /* ── ACTION ─────────────────────────────────────────────────────── */
    NO_MOVEMENT:                   ['Nessun movimento', 'No movement'],
    ESTABLISH_WINDOW_CONDITION:    ['Stabilire la condizione della finestra', 'Establish the window condition'],
    CONFIRM_WINDOW_CONDITION_MET:  ['Confermare che la condizione e soddisfatta', 'Confirm the condition is met'],
    VALIDATE_WINDOW_IN_REGION:     ['Validare la finestra nella regione', 'Validate the window in the region'],
    WATCH_REGULATORY_DATE:         ['Sorvegliare la data regolatoria', 'Watch the regulatory date'],
    MESSAGE_AVAILABLE:             ['Messaggio disponibile', 'Message available'],
    CONFIRM_RECOMMENDATION_IN_FIELD:['Confermare la raccomandazione in campo', 'Confirm the recommendation in the field'],
    CONTACT_NOW:                   ['Contattare adesso', 'Contact now'],
    VALIDATE_AT_FARM_LEVEL:        ['Validare a livello di azienda agricola', 'Validate at farm level'],
    CONFIRM_AT_FARM_LEVEL:         ['Confermare a livello di azienda agricola', 'Confirm at farm level'],
    NOT_CONVENED:                  ['Non convocato', 'Not convened'],

    /* ── ACTION WHY_CODE ────────────────────────────────────────────── */
    SEM_PRIORIDADE_COMERCIAL:              ['Nessuna priorita commerciale', 'No commercial priority'],
    NAO_AUTORIZADO_A_SAIR:                 ['Non autorizzato a uscire verso il cliente', 'Not cleared to go to the customer'],
    SEM_CONDICAO_DECLARADA:                ['Nessuna condizione dichiarata', 'No stated condition'],
    DATA_REGULATORIA_EM_ATIVO_LIGADO:      ['Data regolatoria su un principio attivo collegato', 'Regulatory date on a linked active ingredient'],
    CONDICAO_DECLARADA_ESTADO_DESCONHECIDO:['Condizione dichiarata, stato ancora ignoto', 'Condition stated, state still unknown'],
    PRIORIDADE_COMERCIAL_SEM_TEMPO_PROVADO:['Priorita commerciale senza tempo dimostrato', 'Commercial priority without proven timing'],
    EXTERNAL_MATERIAL_READY:               ['Materiale esterno pronto', 'External material ready'],
    SINAL_ATUAL_COM_ALVO:                  ['Segnale corrente con bersaglio', 'Current signal with a target'],
    NADA_A_VALIDAR:                        ['Nulla da validare', 'Nothing to validate'],
    REGRA_DELEGADA_AO_POMAR:               ['Regola delegata all’osservazione del frutteto', 'Rule delegated to orchard observation'],
    SEM_BASE_FACTUAL:                      ['Nessuna base fattuale', 'No factual basis'],

    /* ── NEXT_TRIGGER · the engine writes these in Portuguese.
         A closed vocabulary of two, keyed by exact value, so the research
         prose never reaches an Italian or English screen. ─────────────── */
    'um boletim novo que declare necessidade positiva': [
      'Un nuovo bollettino che dichiari una necessita positiva',
      'A new bulletin stating a positive need'],
    'evidencia de que a condicao declarada esta satisfeita agora — estadio, limiar medido, captura ou evento climatico': [
      'La prova che la condizione dichiarata e soddisfatta adesso — stadio, soglia misurata, cattura o evento climatico',
      'Evidence that the stated condition is met now — stage, measured threshold, trap catch or weather event'],

    /* ── EVIDENCE ROLES · including the negative ones, verbatim ─────── */
    SUPPORTS_SIGNAL:           ['Sostiene il segnale', 'Supports the signal'],
    SUPPORTS_WINDOW:           ['Sostiene la finestra', 'Supports the window'],
    SUPPORTS_DIRECTION:        ['Sostiene la direzione', 'Supports the direction'],
    SUPPORTS_PRODUCT_MATCH:    ['Sostiene il collegamento con il prodotto', 'Supports the product match'],
    SUPPORTS_COMMERCIAL_ACTION:['Sostiene l’azione commerciale', 'Supports the commercial action'],
    SUPPORTS_REGIONAL_CONTEXT: ['Sostiene il contesto regionale', 'Supports the regional context'],
    BACKGROUND_ONLY:           ['Solo contesto', 'Background only'],
    WEAKENS:                   ['Questa evidenza riduce l’urgenza commerciale',
                                'This evidence lowers the commercial urgency'],
    CLOSES:                    ['Il monitoraggio non sostiene un’azione ora',
                                'Monitoring does not support action now'],
    CONTRADICTS:               ['Questa evidenza contraddice il caso', 'This evidence contradicts the case'],

    /* ── EVIDENCE why-codes ─────────────────────────────────────────── */
    ROTULO_MINISTERIAL_NO_PAR:          ['Etichetta ministeriale sulla coppia', 'Ministerial label on the pair'],
    OBSERVACAO_DE_CAMPO_NA_MESMA_REGIAO:['Osservazione di campo nella stessa regione', 'Field observation in the same region'],
    DECLARA_A_CONDICAO_DA_JANELA:       ['Dichiara la condizione della finestra', 'States the window condition'],
    DECLARA_A_REGRA_DO_MOMENTO:         ['Dichiara la regola del momento', 'States the rule of the moment'],
    FRASE_QUE_DECIDIU_A_DIRECAO:        ['La frase che ha deciso la direzione', 'The sentence that decided the direction'],
    MOVIMENTO_DE_CONCORRENTE:           ['Movimento di un concorrente', 'A competitor move'],
    CONTEXTO_DE_MERCADO:                ['Contesto di mercato', 'Market context'],
    NAO_DECIDE_NENHUM_ELO:              ['Non decide nessun anello', 'Decides no link'],

    /* ── EVIDENCE families ──────────────────────────────────────────── */
    FIELD_SIGNAL:              ['Segnale di campo', 'Field signal'],
    LABEL_USE_RELATIONSHIP:    ['Relazione d’uso da etichetta', 'Label use relationship'],
    REGULATORY_PRODUCT:        ['Prodotto regolatorio', 'Regulatory product'],
    REGULATORY_FUTURE_FACT:    ['Fatto regolatorio futuro', 'Future regulatory fact'],
    ACTIVE_INGREDIENT:         ['Principio attivo', 'Active ingredient'],
    RESISTANCE_RECORD:         ['Registro di resistenza', 'Resistance record'],
    SCIENTIFIC_RECORD:         ['Registro scientifico', 'Scientific record'],
    MARKET_OBSERVATION:        ['Osservazione di mercato', 'Market observation'],
    COMPETITOR_ACTIVITY:       ['Attivita di un concorrente', 'Competitor activity'],
    CROP_ECONOMIC_WEIGHT_CLAIM:['Peso economico della coltura', 'Crop economic weight'],

    /* ── PRODUCT fits ───────────────────────────────────────────────── */
    PRIMARY_MATCH_REASON:                  ['MOTIVO', 'REASON'],
    UNICO_PRODUTO_DO_CATALOGO_NO_PAR:      ['Unico prodotto del catalogo su questa coppia', 'The only catalogue product on this pair'],
    SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER:    ['Nessuna regola difendibile per sceglierne uno', 'No defensible rule for choosing one'],
    DECLARED_ON_CATALOG_PAGE:              ['Dichiarato sulla pagina di catalogo', 'Stated on the catalogue page'],
    ON_MINISTERIAL_LABEL:                  ['Sull’etichetta ministeriale', 'On the ministerial label'],
    NATIONAL_AUTHORIZATION_CONTAINS_REGION:['Autorizzazione nazionale che copre la regione', 'National authorisation covering the region'],
    AUTHORIZATION_LIVE:                    ['Autorizzazione in vigore', 'Authorisation live'],
    LABEL_AND_CATALOG:                     ['Etichetta e catalogo', 'Label and catalogue'],
    LABEL_ONLY:                            ['Solo etichetta', 'Label only'],
    REGISTRATION_NUMBER_JOIN:              ['Unione per numero di registrazione', 'Joined by registration number'],
    EU_APPROVAL_EXPIRES:                   ['Approvazione UE in scadenza', 'EU approval expires'],
    VERIFIED_LABEL_MATCH:                  ['Corrispondenza da etichetta verificata', 'Verified label match'],
    RELATED_PORTFOLIO:                     ['Portafoglio collegato', 'Related portfolio'],
    CLASSIFIED:                            ['Classificato', 'Classified'],
    QUOTED_ON_LABEL:                       ['Citato in etichetta', 'Quoted on the label'],
    lblCropFit:      ['COLTURA', 'CROP'],
    lblTargetFit:    ['BERSAGLIO', 'TARGET'],
    lblRegionalFit:  ['REGIONE', 'REGION'],
    lblRegFit:       ['REGOLATORIO', 'REGULATORY'],
    lblWindowFit:    ['FINESTRA', 'WINDOW'],
    lblValidation:   ['VALIDAZIONE', 'VALIDATION'],
    lblActives:      ['PRINCIPI ATTIVI', 'ACTIVE INGREDIENTS'],
    lblMoa:          ['MECCANISMO D’AZIONE', 'MODE OF ACTION'],
    lblMatchReason:  ['MOTIVO DEL COLLEGAMENTO', 'MATCH REASON'],

    /* ── confidence / currency · the engine writes these in Portuguese */
    ALTA:    ['alta', 'high'],
    MEDIA:   ['media', 'medium'],
    BAIXA:   ['bassa', 'low'],
    NENHUMA: ['nessuna', 'none'],
    CURRENT: ['corrente', 'current'],
    RECENT:  ['recente', 'recent'],
    OLD:     ['non recente', 'not recent'],

    /* ── geography scope ────────────────────────────────────────────── */
    REGIONAL:  ['regionale', 'regional'],
    NACIONAL:  ['nazionale', 'national'],
    PROVINCIAL:['provinciale', 'provincial'],
    EUROPEU:   ['europeo', 'european'],

    /* ── crops · the source publishes the name; the code is ours ────── */
    CROP_GRAPEVINE:   ['Vite', 'Grapevine'],
    CROP_APPLE:       ['Melo', 'Apple'],
    CROP_MAIZE:       ['Mais', 'Maize'],
    CROP_RICE:        ['Riso', 'Rice'],
    CROP_TOMATO:      ['Pomodoro', 'Tomato'],
    CROP_OLIVE:       ['Olivo', 'Olive'],
    CROP_CITRUS:      ['Agrumi', 'Citrus'],
    CROP_SOYBEAN:     ['Soia', 'Soybean'],
    CROP_SUGAR_BEET:  ['Barbabietola da zucchero', 'Sugar beet'],
    CROP_BARLEY:      ['Orzo', 'Barley'],
    CROP_WHEAT_GENERIC:['Frumento', 'Wheat'],
    CROP_VEGETABLES:  ['Orticole', 'Vegetables'],

    /* ── targets ────────────────────────────────────────────────────── */
    ISSUE_BOTRYTIS:      ['Botrite', 'Botrytis'],
    ISSUE_CODLING_MOTH:  ['Carpocapsa', 'Codling moth'],
    ISSUE_GRAPE_MOTH:    ['Tignoletta della vite', 'Grape moth'],
    ISSUE_CORN_BORER:    ['Piralide del mais', 'European corn borer'],
    ISSUE_DIABROTICA:    ['Diabrotica', 'Diabrotica'],
    ISSUE_DOWNY_MILDEW:  ['Peronospora', 'Downy mildew'],
    ISSUE_POWDERY_MILDEW:['Oidio', 'Powdery mildew'],
    ISSUE_ECHINOCHLOA:   ['Giavone', 'Echinochloa'],
    ISSUE_SCAPHOIDEUS:   ['Scafoideo', 'Scaphoideus titanus'],

    /* ── geographies ────────────────────────────────────────────────── */
    REGION_EMILIA_ROMAGNA:       ['Emilia-Romagna', 'Emilia-Romagna'],
    REGION_TOSCANA:              ['Toscana', 'Tuscany'],
    REGION_VENETO:               ['Veneto', 'Veneto'],
    REGION_UMBRIA:               ['Umbria', 'Umbria'],
    REGION_LOMBARDIA:            ['Lombardia', 'Lombardy'],
    REGION_FRIULI_VENEZIA_GIULIA:['Friuli-Venezia Giulia', 'Friuli-Venezia Giulia'],
    GEO_ITALY:                   ['Italia', 'Italy'],
    GEO_EU:                      ['Unione Europea', 'European Union'],

    /* ── misc states ────────────────────────────────────────────────── */
    COMPLETE:            ['completa', 'complete'],
    MEASURED_BY_DIMENSION:['misurata per dimensione', 'measured by dimension'],
    YES:                 ['SI', 'YES'],
    NO:                  ['NO', 'NO'],
  };

  const pick = (key, lang) => {
    const row = L[key];
    if (!row) return null;
    return lang === 'en' ? row[1] : row[0];
  };

  window.MEETING_LABELS = {
    TABLE: L,
    /* Returns null when a code has no phrase — the caller decides what to do,
       and the gate can count the holes. A missing label must never fall back
       to the raw code, because that is exactly the leak this file prevents. */
    get: pick,
    has: (key) => Object.prototype.hasOwnProperty.call(L, key),
    keys: () => Object.keys(L),
  };
})();
