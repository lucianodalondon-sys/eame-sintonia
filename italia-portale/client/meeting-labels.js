/* SINTONIA · IL DIZIONARIO DELLA RIUNIONE — meeting-labels.js
   ===========================================================================
   OGNI CODICE DEL MOTORE, IN ITALIANO E IN INGLESE. NIENTE ALTRO.

   Il motore parla in codici: ACT_NOW, RULE_DELEGATED_TO_FARM,
   ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO. Sono FATTI, e vanno benissimo dentro
   il pacchetto. Davanti a un cliente italiano non sono niente.

       UN CODICE INTERNO SULLO SCHERMO NON E UN DETTAGLIO TECNICO.
       E LA PROVA CHE NESSUNO HA LETTO QUELLA SCHERMATA.

   QUESTO FILE NON DECIDE NULLA
   ----------------------------
   Non calcola, non ordina, non sceglie, non nasconde. Prende un codice e
   restituisce una frase. Se il codice non c'e, restituisce `null` — e chi
   chiama decide cosa fare, il che e sempre meglio di inventare una parola.

       TRADURRE NON E INTERPRETARE. QUI SI TRADUCE.

   LA LEGGE DELL'IGNOTO
   --------------------
   `UNKNOWN` non diventa mai una frase rassicurante. Diventa «non ancora
   misurato», che e la verita. Una finestra di cui non si conosce lo stato
   NON e una finestra chiusa, e non e una finestra aperta.

       L'IGNOTO NON PUO SPARIRE DIETRO UNA COPY BELLA.

   LE OTTO FRASI DEL BRIEFING sono riprodotte parola per parola (§13):
   sono state scritte per essere lette a voce alta in riunione, non per
   essere riscritte da me.
   =========================================================================== */
(function () {
  'use strict';

  /* ── STATO DEL CASO · la parola che il commerciale legge per prima ────── */
  const STATUS = {
    ACT_NOW:            { it: 'AGIRE ORA',        en: 'ACT NOW' },
    VALIDATE_NOW:       { it: 'VALIDARE ORA',     en: 'VALIDATE NOW' },
    TO_VALIDATE:        { it: 'DA VALIDARE',      en: 'TO VALIDATE' },
    FUTURE_PREPARATION: { it: 'PREPARARE',        en: 'PREPARE' },
    WATCH:              { it: 'OSSERVARE',        en: 'WATCH' }
  };

  /* Perche quello stato, in una riga. */
  const STATUS_WHY = {
    ACT_NOW:            { it: 'la catena e completa: segnale attuale, finestra aperta e prodotto autorizzato.',
                          en: 'the chain is complete: current signal, open window and authorised product.' },
    VALIDATE_NOW:       { it: 'la condizione e nota, ma lo stato attuale va confermato prima di muoversi.',
                          en: 'the condition is known, but the current state must be confirmed before moving.' },
    TO_VALIDATE:        { it: 'manca un anello della catena: si valida prima di parlare di azione.',
                          en: 'a link in the chain is missing: validate before speaking of action.' },
    FUTURE_PREPARATION: { it: 'non e un momento di campo: e una preparazione con una data davanti.',
                          en: 'this is not a field moment: it is a preparation with a date ahead.' },
    WATCH:              { it: 'il caso resta sotto osservazione: oggi non sostiene un intervento.',
                          en: 'the case stays under observation: today it does not support an intervention.' }
  };

  /* ── PRIORITA COMMERCIALE ─────────────────────────────────────────────── */
  const COMMERCIAL_PRIORITY = {
    SALES_READY:           { it: 'PRONTO PER LA VENDITA',    en: 'SALES READY' },
    STRATEGIC_OPPORTUNITY: { it: 'OPPORTUNITA STRATEGICA',   en: 'STRATEGIC OPPORTUNITY' },
    COMMERCIAL_WATCH:      { it: 'OSSERVAZIONE COMMERCIALE', en: 'COMMERCIAL WATCH' },
    TO_VALIDATE:           { it: 'DA VALIDARE',              en: 'TO VALIDATE' }
  };

  /* ── ARCHETIPO · che TIPO di opportunita e ────────────────────────────── */
  const ARCHETYPE = {
    O1_FIELD_PRESSURE:        { it: 'Pressione in campo',         en: 'Field pressure' },
    O2_MARKET_MOMENT:         { it: 'Momento di mercato',         en: 'Market moment' },
    O3_RESISTANCE_MOA:        { it: 'Resistenza e meccanismo d’azione', en: 'Resistance and mode of action' },
    O4_COMPETITIVE_OPENING:   { it: 'Apertura competitiva',       en: 'Competitive opening' },
    O5_REGULATORY_PREPARATION:{ it: 'Preparazione regolatoria',   en: 'Regulatory preparation' },
    O6_SCIENCE_TO_FIELD:      { it: 'Dalla scienza al campo',     en: 'Science to field' }
  };

  /* ── STATO DI PUBBLICAZIONE · la catraca, in chiaro ───────────────────── */
  const PUBLICATION_STATE = {
    PUBLISHABLE:         { it: 'Verificato — utilizzabile con il cliente',
                           en: 'Verified — usable with the client' },
    VALIDATION_REQUIRED: { it: 'Richiede validazione prima dell’uso esterno',
                           en: 'Requires validation before external use' }
  };
  const PUBLICATION_STATE_SHORT = {
    PUBLISHABLE:         { it: 'VERIFICATO',           en: 'VERIFIED' },
    VALIDATION_REQUIRED: { it: 'DA VALIDARE',          en: 'VALIDATION REQUIRED' }
  };

  const TRAIL_STATE = {
    COMPLETE: { it: 'Tracciabilita completa dalla fonte alla schermata',
                en: 'Complete trail from source to screen' }
  };

  const OPPORTUNITY_STATE = {
    OPPORTUNITY_CONFIRMED: { it: 'Convergenza verificata', en: 'Verified convergence' },
    OPPORTUNITY_CANDIDATE: { it: 'Convergenza da validare', en: 'Convergence to validate' }
  };

  /* ── LA FINESTRA · §13 · le frasi del briefing, parola per parola ─────── */
  const WINDOW_TYPE = {
    PHENOLOGY_WINDOW:      { it: 'Finestra definita dallo stadio fenologico',
                             en: 'Window defined by phenological stage' },
    PREHARVEST_WINDOW:     { it: 'Finestra definita dall’intervallo di pre-raccolta',
                             en: 'Window defined by the pre-harvest interval' },
    THRESHOLD_WINDOW:      { it: 'Finestra definita da una soglia da misurare',
                             en: 'Window defined by a threshold to be measured' },
    PEST_STAGE_WINDOW:     { it: 'Finestra definita dallo stadio dell’insetto',
                             en: 'Window defined by the insect’s stage' },
    WEATHER_TRIGGERED_WINDOW:{ it: 'Finestra aperta da un evento meteorologico',
                             en: 'Window opened by a weather event' },
    CALENDAR_WINDOW:       { it: 'Finestra di calendario',
                             en: 'Calendar window' },
    RULE_DELEGATED_TO_FARM:{ it: 'La decisione dipende dall’osservazione in campo',
                             en: 'The decision depends on farm-level observation' }
  };

  const WINDOW_RULE_STATE = {
    RULE_DECLARED:          { it: 'La regola del momento e dichiarata dalla fonte',
                              en: 'The timing rule is declared by the source' },
    RULE_DELEGATED_TO_FARM: { it: 'La decisione dipende dall’osservazione in campo',
                              en: 'The decision depends on farm-level observation' },
    RULE_ADMINISTRATIVE_ONLY:{ it: 'Obbligo amministrativo — non e una finestra agronomica',
                              en: 'Administrative obligation — not an agronomic window' },
    RULE_NOT_DECLARED:      { it: 'Nessuna fonte dichiara la regola del momento per questa coppia',
                              en: 'No source declares the timing rule for this pair' }
  };

  const WINDOW_OPEN_NOW = {
    YES:     { it: 'Finestra agronomica aperta',            en: 'Agronomic window open' },
    NO:      { it: 'Finestra non aperta',                   en: 'Window not open' },
    UNKNOWN: { it: 'Condizione nota; stato attuale non ancora misurato',
               en: 'Condition known; current state not yet measured' }
  };

  const WINDOW_DEFINED = {
    YES: { it: 'Condizione della finestra dichiarata', en: 'Window condition declared' },
    NO:  { it: 'Nessuna condizione dichiarata',        en: 'No condition declared' }
  };

  /* COME si e stabilito se la finestra e aperta. Il metodo, non il codice. */
  const WINDOW_OPEN_NOW_METHOD = {
    ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO: {
      it: 'lo stesso bollettino che segnala il problema dichiara anche lo stadio della coltura.',
      en: 'the same bulletin that reports the problem also declares the crop stage.' },
    FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE: {
      it: 'la fonte dichiara la condizione come presente ora.',
      en: 'the source declares the condition as present now.' },
    FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE: {
      it: 'la condizione richiede una misura che la fonte non riporta.',
      en: 'the condition requires a measurement the source does not report.' },
    REGRA_EXIGE_MEDICAO_DO_POMAR_QUE_NENHUMA_FONTE_REGIONAL_TEM: {
      it: 'la regola richiede una misura del frutteto che nessuna fonte regionale possiede.',
      en: 'the rule requires an orchard measurement no regional source holds.' },
    NENHUMA_CONDICAO_DECLARADA_PARA_O_PAR: {
      it: 'nessuna fonte dichiara una condizione per questa coppia coltura × problema.',
      en: 'no source declares a condition for this crop × problem pair.' },
    DOCUMENTO_NAO_CORRENTE: {
      it: 'il documento che dichiara la condizione non e piu attuale.',
      en: 'the document declaring the condition is no longer current.' }
  };

  const WINDOW_CONFIDENCE = {
    NENHUMA: { it: 'nessuna', en: 'none' },
    BAIXA:   { it: 'bassa',   en: 'low' },
    MEDIA:   { it: 'media',   en: 'medium' },
    ALTA:    { it: 'alta',    en: 'high' }
  };

  /* ── LA DIREZIONE DELLA FONTE · §13 · «monitorare, non attivare» ──────── */
  const NEED_DIRECTION = {
    POSITIVE_PRESSURE:    { it: 'La fonte segnala pressione e giustifica un intervento',
                            en: 'The source reports pressure and justifies an intervention' },
    NO_ACTION_RECOMMENDED:{ it: 'La fonte raccomanda di monitorare, non di attivare',
                            en: 'The source recommends monitoring, not activating' },
    ACTION_SUSPENDED:     { it: 'La fonte dichiara l’intervento sospeso',
                            en: 'The source declares the intervention suspended' },
    TREATMENT_PROHIBITED: { it: 'Il trattamento e vietato in questa fase',
                            en: 'Treatment is prohibited at this stage' },
    WINDOW_CONCLUDED:     { it: 'La fonte dichiara la finestra conclusa',
                            en: 'The source declares the window concluded' },
    NEUTRAL_MENTION:      { it: 'La fonte cita il problema senza indicare una direzione',
                            en: 'The source mentions the problem without giving a direction' },
    UNKNOWN:              { it: 'Direzione non ancora determinata',
                            en: 'Direction not yet determined' }
  };

  const NEED_METHOD = {
    PAIR_IN_SAME_CLAUSE:          { it: 'coltura e problema nella stessa frase della fonte',
                                    en: 'crop and problem in the same clause of the source' },
    PAIR_IN_DOCUMENT_TITLE:       { it: 'coppia dichiarata nel titolo del documento',
                                    en: 'pair declared in the document title' },
    CROP_FROM_PRECEDING_CLAUSE:   { it: 'coltura ripresa dalla frase precedente',
                                    en: 'crop carried from the preceding clause' },
    CROP_FROM_SINGLE_CROP_DOCUMENT:{ it: 'documento dedicato a una sola coltura',
                                    en: 'document dedicated to a single crop' }
  };

  /* ── STADIO DELL’INSETTO ≠ RACCOMANDAZIONE · §17 D ────────────────── */
  const PEST_STAGE_STATE = {
    STAGE_PEAK:         { it: 'Volo al culmine',              en: 'Flight at its peak' },
    STAGE_DECLINING:    { it: 'Volo in calo',                 en: 'Flight declining' },
    STAGE_ENDED:        { it: 'Volo concluso',                en: 'Flight ended' },
    STAGE_NOT_DECLARED: { it: 'Stadio non dichiarato',        en: 'Stage not declared' }
  };

  const ACTION_RECOMMENDATION_STATE = {
    START_RECOMMENDED:          { it: 'La fonte raccomanda di iniziare',
                                  en: 'The source recommends starting' },
    CONTINUE_RECOMMENDED:       { it: 'La fonte raccomanda di proseguire la protezione',
                                  en: 'The source recommends continuing protection' },
    SUSPEND_RECOMMENDED:        { it: 'La fonte raccomanda di sospendere',
                                  en: 'The source recommends suspending' },
    CONCLUDED_DECLARED:         { it: 'La fonte dichiara il ciclo concluso',
                                  en: 'The source declares the cycle concluded' },
    NOT_NEEDED_DECLARED:        { it: 'La fonte dichiara che non servono interventi',
                                  en: 'The source declares no interventions are needed' },
    PROHIBITED_DECLARED:        { it: 'La fonte dichiara il trattamento vietato',
                                  en: 'The source declares treatment prohibited' },
    RECOMMENDATION_NOT_DECLARED:{ it: 'Nessuna raccomandazione dichiarata',
                                  en: 'No recommendation declared' }
  };

  /* La frase che impedisce l’errore di lettura piu costoso della riunione. */
  const STAGE_VS_RECOMMENDATION_NOTE = {
    it: 'Fine del volo non significa fine della necessita: la fonte distingue lo stadio dell’insetto dalla raccomandazione di protezione, e qui restano separati.',
    en: 'End of flight does not mean end of the need: the source separates the insect’s stage from the protection recommendation, and they stay separate here.'
  };

  const THRESHOLD_STATE = {
    NOT_APPLICABLE: { it: 'Nessuna soglia prevista per questa coppia',
                      en: 'No threshold foreseen for this pair' },
    NOT_DECLARED:   { it: 'Soglia prevista ma non dichiarata dalla fonte',
                      en: 'Threshold foreseen but not declared by the source' }
  };

  /* ── PERCHE ORA · i cinque anelli ─────────────────────────────────────── */
  const WHY_NOW_CODES = {
    CADEIA_COMPLETA:            { it: 'Catena completa: si puo agire ora',
                                  en: 'Complete chain: action is possible now' },
    SEM_SINAL_ATUAL:            { it: 'Nessun segnale attuale',
                                  en: 'No current signal' },
    SEM_JANELA_DEFINIDA:        { it: 'Nessuna finestra definita',
                                  en: 'No window defined' },
    SEM_JANELA_ABERTA_AGORA:    { it: 'Finestra non aperta ora',
                                  en: 'Window not open now' },
    SEM_VINCULO_COM_PORTFOLIO:  { it: 'Nessun legame con il portafoglio',
                                  en: 'No link to the portfolio' },
    SEM_TEMPO_PARA_ACAO:        { it: 'Nessun tempo utile dichiarato',
                                  en: 'No usable time declared' }
  };

  /* I cinque anelli, come nomi leggibili. */
  const CHAIN_LINK = {
    SINAL_ATUAL:           { it: 'Segnale attuale',          en: 'Current signal' },
    JANELA_DEFINIDA:       { it: 'Finestra definita',        en: 'Window defined' },
    JANELA_ABERTA_AGORA:   { it: 'Finestra aperta ora',      en: 'Window open now' },
    VINCULO_COM_PORTFOLIO: { it: 'Legame con il portafoglio',en: 'Link to the portfolio' },
    TEMPO_PARA_ACAO:       { it: 'Tempo per agire',          en: 'Time to act' }
  };

  /* ── PERCHE E UN’OPPORTUNITA COMMERCIALE ─────────────────────────── */
  const WHY_COMMERCIAL_CODES = {
    ALL_GATES_CLOSE:            { it: 'Necessita agronomica, finestra e prodotto autorizzato coincidono',
                                  en: 'Agronomic need, window and authorised product all coincide' },
    TIME_FROM_SOURCE_RECOMMENDATION:{ it: 'Il momento e dichiarato dalla raccomandazione della fonte',
                                  en: 'The timing comes from the source’s own recommendation' },
    NEED_NOT_POSITIVE:          { it: 'La fonte non afferma una necessita di intervento',
                                  en: 'The source does not state a need to intervene' },
    NEED_CLOSED:                { it: 'La fonte chiude la necessita di intervento',
                                  en: 'The source closes the need to intervene' },
    OPENING_WITHOUT_NEED:       { it: 'Apertura di mercato senza necessita agronomica dimostrata',
                                  en: 'Market opening without a demonstrated agronomic need' },
    NEITHER_NEED_NOR_OPENING:   { it: 'Ne necessita agronomica ne apertura di mercato',
                                  en: 'Neither agronomic need nor market opening' },
    REGULATORY_BY_NATURE:       { it: 'Opportunita di natura regolatoria, non di campo',
                                  en: 'A regulatory opportunity, not a field one' },
    LABEL_WITHOUT_CATALOG:      { it: 'Etichetta ministeriale senza pagina a catalogo',
                                  en: 'Ministerial label without a catalogue page' },
    REGULATORY_WITHOUT_CATALOG: { it: 'Fatto regolatorio senza prodotto a catalogo',
                                  en: 'Regulatory fact without a catalogue product' }
  };

  /* ── CHE COSA MANCA ANCORA ────────────────────────────────────────────── */
  const WHAT_IS_MISSING = {
    NO_AGRONOMIC_TARGET:          { it: 'Il caso non nomina un problema agronomico',
                                    en: 'The case does not name an agronomic problem' },
    REGION_NOT_DECLARED:          { it: 'La regione non e dichiarata',
                                    en: 'The region is not declared' },
    OFFICIAL_AREA_NOT_CLIENT_SAFE:{ it: 'La superficie ufficiale non e utilizzabile con il cliente',
                                    en: 'The official area is not client-usable' },
    COMMERCIAL_PRODUCT_MISSING:   { it: 'Nessun prodotto ADAMA a catalogo per questa coppia',
                                    en: 'No ADAMA catalogue product for this pair' },
    WINDOW_RULE_MISSING:          { it: 'La regola del momento non e dichiarata',
                                    en: 'The timing rule is not declared' },
    WINDOW_STATE_UNKNOWN:         { it: 'Lo stato attuale della finestra non e misurato',
                                    en: 'The current state of the window is not measured' },
    WINDOW_RULE_DELEGATED_TO_FARM:{ it: 'La decisione dipende dall’osservazione in campo',
                                    en: 'The decision depends on farm-level observation' },
    WINDOW_RULE_ADMINISTRATIVE_ONLY:{ it: 'La regola e un obbligo amministrativo, non una finestra agronomica',
                                    en: 'The rule is an administrative obligation, not an agronomic window' },
    DIRECTION_UNKNOWN:            { it: 'La direzione della fonte non e determinata',
                                    en: 'The source’s direction is not determined' },
    INTENSITY_UNKNOWN:            { it: 'L’intensita del fenomeno non e misurata',
                                    en: 'The intensity of the phenomenon is not measured' },
    RECURRENCE_UNKNOWN:           { it: 'La ricorrenza negli anni non e stabilita',
                                    en: 'Recurrence across years is not established' },
    SIGNAL_NOT_RECENT:            { it: 'Il segnale piu recente non e attuale',
                                    en: 'The most recent signal is not current' }
  };

  const EXTERNAL_BLOCKER_CODES = {
    NOT_SALES_READY: { it: 'Il materiale non e ancora pronto per il canale',
                       en: 'The material is not yet ready for the channel' }
  };

  const EXTERNAL_MATERIAL_READY = {
    YES: { it: 'Materiale utilizzabile all’esterno', en: 'Material usable externally' },
    NO:  { it: 'Uso interno — non ancora per il canale', en: 'Internal use — not yet for the channel' }
  };

  /* ── ATTUALITA E FIDUCIA ──────────────────────────────────────────────── */
  const SIGNAL_CURRENCY = {
    CURRENT: { it: 'Segnale attuale',      en: 'Current signal' },
    RECENT:  { it: 'Segnale recente',      en: 'Recent signal' },
    OLD:     { it: 'Segnale non recente',  en: 'Signal not recent' },
    UNKNOWN: { it: 'Attualita non determinata', en: 'Currency not determined' }
  };

  const CONFIDENCE = {
    ALTA:  { it: 'alta',  en: 'high' },
    MEDIA: { it: 'media', en: 'medium' },
    BAIXA: { it: 'bassa', en: 'low' }
  };

  /* ── IL PORTAFOGLIO · perche proprio questo prodotto ──────────────────── */
  const PRODUCT_LINK_STATE = {
    VERIFIED_LABEL_MATCH: { it: 'Corrispondenza verificata su etichetta ministeriale',
                            en: 'Match verified on the ministerial label' },
    RELATED_PORTFOLIO:    { it: 'Portafoglio collegato, coppia non confermata',
                            en: 'Related portfolio, pair not confirmed' }
  };

  const CROP_FIT = {
    DECLARED_ON_CATALOG_PAGE: { it: 'Coltura dichiarata nella pagina a catalogo',
                                en: 'Crop declared on the catalogue page' },
    UNKNOWN:                  { it: 'Coltura non confermata a catalogo',
                                en: 'Crop not confirmed in the catalogue' }
  };
  const TARGET_FIT = {
    ON_MINISTERIAL_LABEL: { it: 'Problema presente sull’etichetta ministeriale',
                            en: 'Problem present on the ministerial label' }
  };
  const REGIONAL_FIT = {
    NATIONAL_AUTHORIZATION_CONTAINS_REGION: { it: 'Autorizzazione nazionale che comprende la regione',
                                              en: 'National authorisation covering the region' }
  };
  const REGULATORY_FIT = {
    AUTHORIZATION_LIVE: { it: 'Autorizzazione in vigore', en: 'Authorisation in force' }
  };
  const WINDOW_FIT = {
    YES:     { it: 'Compatibile con la finestra',            en: 'Compatible with the window' },
    UNKNOWN: { it: 'Compatibilita con la finestra non misurata',
               en: 'Compatibility with the window not measured' }
  };
  const VALIDATION_STATE = {
    LABEL_AND_CATALOG: { it: 'Etichetta + catalogo',  en: 'Label + catalogue' },
    LABEL_ONLY:        { it: 'Solo etichetta',        en: 'Label only' }
  };
  const MATCH_REASON = {
    REGISTRATION_NUMBER_JOIN: { it: 'Collegato per numero di registrazione',
                                en: 'Joined by registration number' }
  };
  const PRIMARY_MATCH_REASON = {
    UNICO_PRODUTO_DO_CATALOGO_NO_PAR:  { it: 'unico prodotto a catalogo per questa coppia',
                                         en: 'the only catalogue product for this pair' },
    SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER:{ it: 'nessuna regola difendibile per eleggerne uno: sono presentati tutti',
                                         en: 'no defensible rule to elect one: all are presented' }
  };
  const RESTRICTION_CODE = {
    EU_APPROVAL_EXPIRES: { it: 'Approvazione UE della sostanza in scadenza',
                           en: 'EU approval of the active substance expiring' }
  };
  const MODE_OF_ACTION_STATE = {
    CLASSIFIED: { it: 'Meccanismo d’azione classificato', en: 'Mode of action classified' },
    UNKNOWN:    { it: 'Meccanismo d’azione non classificato', en: 'Mode of action not classified' }
  };
  const APPLICATION_STATE = {
    QUOTED_ON_LABEL: { it: 'Uso citato in etichetta', en: 'Use quoted on the label' },
    UNKNOWN:         { it: 'Uso non citato',          en: 'Use not quoted' }
  };

  /* ── LA MAPPA DELLE AZIONI · chi agisce, chi valida, chi aspetta ──────── */
  /* ⚠️ QUESTE PAROLE NON SONO LIBERE. Il portale nomina gia le stesse aree nel
     dizionario V21 (`italy-i18n.js`), e le usa nei filtri, nei brief e nelle
     schede. Scriverne qui una variante — «Sviluppo Mercato» accanto a
     «SVILUPPO DI MERCATO» — darebbe alla stessa area due nomi nello stesso
     prodotto, e nessuno dei due sarebbe sbagliato abbastanza da farsi notare.

         DUE NOMI PER LA STESSA COSA SONO PEGGIO DI UN NOME BRUTTO:
         UN NOME BRUTTO SI CORREGGE, DUE NOMI SI DISCUTONO.

     Sono quindi COPIATE da V21, parola per parola. Se un giorno cambiano li,
     devono cambiare qui — e il portone `action-map-consistency` se ne accorge,
     perche confronta le due liste. */
  const DEPARTMENT = {
    MARKET_DEVELOPMENT:   { it: 'SVILUPPO DI MERCATO',   en: 'MARKET DEVELOPMENT' },
    COMMERCIAL:           { it: 'COMMERCIALE',           en: 'COMMERCIAL' },
    MARKETING:            { it: 'MARKETING',             en: 'MARKETING' },
    TECHNICAL_SCIENTIFIC: { it: 'TECNICO E SCIENTIFICO', en: 'TECHNICAL AND SCIENTIFIC' },
    SUPPLY:               { it: 'APPROVVIGIONAMENTO',    en: 'SUPPLY' }
  };

  const ACTION_STATE = {
    ACT:       { it: 'AGISCE ORA', en: 'ACTS NOW' },
    VALIDATE:  { it: 'VALIDA',     en: 'VALIDATES' },
    PREPARE:   { it: 'PREPARA',    en: 'PREPARES' },
    WATCH:     { it: 'SEGUE',      en: 'WATCHES' },
    NO_ACTION: { it: 'NON CONVOCATO', en: 'NOT CALLED' }
  };

  const ACTION = {
    CONTACT_NOW:                 { it: 'Contattare ora i clienti dell’area',
                                   en: 'Contact the growers in the area now' },
    MESSAGE_AVAILABLE:           { it: 'Messaggio disponibile per il canale',
                                   en: 'Message available for the channel' },
    CONFIRM_RECOMMENDATION_IN_FIELD:{ it: 'Confermare la raccomandazione in campo',
                                   en: 'Confirm the recommendation in the field' },
    CONFIRM_WINDOW_CONDITION_MET:{ it: 'Confermare che la condizione della finestra e soddisfatta',
                                   en: 'Confirm the window condition is met' },
    CONFIRM_AT_FARM_LEVEL:       { it: 'Confermare con osservazione in azienda',
                                   en: 'Confirm with on-farm observation' },
    VALIDATE_AT_FARM_LEVEL:      { it: 'Validare con misura in azienda',
                                   en: 'Validate with an on-farm measurement' },
    VALIDATE_WINDOW_IN_REGION:   { it: 'Validare la finestra nella regione',
                                   en: 'Validate the window in the region' },
    ESTABLISH_WINDOW_CONDITION:  { it: 'Stabilire la condizione della finestra',
                                   en: 'Establish the window condition' },
    WATCH_REGULATORY_DATE:       { it: 'Seguire la scadenza regolatoria',
                                   en: 'Watch the regulatory date' },
    PREPARE:                     { it: 'Preparare il materiale',
                                   en: 'Prepare the material' },
    NO_MOVEMENT:                 { it: 'Nessun movimento richiesto',
                                   en: 'No movement required' },
    NOT_CONVENED:                { it: 'Area non convocata da questo caso',
                                   en: 'Area not called by this case' }
  };

  const ACTION_WHY_CODE = {
    CADEIA_COMPLETA:              { it: 'la catena e completa',
                                    en: 'the chain is complete' },
    SINAL_ATUAL_COM_ALVO:         { it: 'segnale attuale con un bersaglio nominato',
                                    en: 'current signal with a named target' },
    EXTERNAL_MATERIAL_READY:      { it: 'il materiale puo uscire verso il canale',
                                    en: 'the material may go out to the channel' },
    CONDICAO_DECLARADA_ESTADO_DESCONHECIDO:{ it: 'condizione dichiarata, stato attuale ignoto',
                                    en: 'condition declared, current state unknown' },
    REGRA_DELEGADA_AO_POMAR:      { it: 'la regola e delegata all’osservazione in campo',
                                    en: 'the rule is delegated to farm-level observation' },
    DATA_REGULATORIA_EM_ATIVO_LIGADO:{ it: 'scadenza regolatoria su una sostanza collegata',
                                    en: 'regulatory date on a linked active substance' },
    PRIORIDADE_COMERCIAL_SEM_TEMPO_PROVADO:{ it: 'priorita commerciale senza tempo dimostrato',
                                    en: 'commercial priority without proven timing' },
    SEM_CONDICAO_DECLARADA:       { it: 'nessuna condizione dichiarata',
                                    en: 'no condition declared' },
    SEM_SINAL_ATUAL:              { it: 'nessun segnale attuale',
                                    en: 'no current signal' },
    SEM_PRIORIDADE_COMERCIAL:     { it: 'nessuna priorita commerciale',
                                    en: 'no commercial priority' },
    SEM_BASE_FACTUAL:             { it: 'nessuna base fattuale per muoversi',
                                    en: 'no factual basis to move' },
    NADA_A_VALIDAR:               { it: 'non c’e nulla da validare',
                                    en: 'there is nothing to validate' },
    NAO_AUTORIZADO_A_SAIR:        { it: 'il materiale non e autorizzato a uscire',
                                    en: 'the material is not cleared to go out' }
  };

  /* Cosa sblocca il passo successivo. */
  const DEPENDENCY = {
    SINAL_ATUAL:         { it: 'un segnale attuale',        en: 'a current signal' },
    JANELA_ABERTA_AGORA: { it: 'la finestra aperta ora',    en: 'the window open now' }
  };

  const NEXT_TRIGGER = {
    'evidencia de que a condicao declarada esta satisfeita agora — estadio, limiar medido, captura ou evento climatico': {
      it: 'la prova che la condizione dichiarata e soddisfatta ora — stadio, soglia misurata, cattura o evento climatico',
      en: 'evidence that the declared condition is met now — stage, measured threshold, trap catch or weather event' },
    'um boletim novo que declare necessidade positiva': {
      it: 'un nuovo bollettino che dichiari una necessita positiva',
      en: 'a new bulletin declaring a positive need' }
  };

  /* ── LE PROVE · il ruolo di ogni documento ────────────────────────────── */
  const EVIDENCE_ROLE = {
    SUPPORTS_SIGNAL:           { it: 'Sostiene il segnale',            en: 'Supports the signal' },
    SUPPORTS_DIRECTION:        { it: 'Decide la direzione',            en: 'Decides the direction' },
    SUPPORTS_WINDOW:           { it: 'Sostiene la finestra',           en: 'Supports the window' },
    SUPPORTS_PRODUCT_MATCH:    { it: 'Sostiene il legame col prodotto',en: 'Supports the product match' },
    SUPPORTS_COMMERCIAL_ACTION:{ it: 'Sostiene l’azione commerciale', en: 'Supports the commercial action' },
    SUPPORTS_REGIONAL_CONTEXT: { it: 'Fornisce contesto regionale',    en: 'Provides regional context' },
    BACKGROUND_ONLY:           { it: 'Solo contesto',                  en: 'Background only' },
    /* L’INTELLIGENZA NEGATIVA E PARTE DEL PRODOTTO. §15 · verbatim. */
    WEAKENS:                   { it: 'Questa evidenza riduce l’urgenza commerciale',
                                 en: 'This evidence lowers the commercial urgency' },
    CONTRADICTS:               { it: 'Questa evidenza contraddice la lettura',
                                 en: 'This evidence contradicts the reading' },
    CLOSES:                    { it: 'Il monitoraggio non sostiene un’azione ora',
                                 en: 'Monitoring does not support action now' }
  };

  const EVIDENCE_WHY_CODE = {
    ROTULO_MINISTERIAL_NO_PAR:          { it: 'etichetta ministeriale sulla coppia',
                                          en: 'ministerial label on the pair' },
    FRASE_QUE_DECIDIU_A_DIRECAO:        { it: 'la frase che ha deciso la direzione',
                                          en: 'the sentence that decided the direction' },
    OBSERVACAO_DE_CAMPO_NA_MESMA_REGIAO:{ it: 'osservazione di campo nella stessa regione',
                                          en: 'field observation in the same region' },
    DECLARA_A_CONDICAO_DA_JANELA:       { it: 'dichiara la condizione della finestra',
                                          en: 'declares the window condition' },
    DECLARA_A_REGRA_DO_MOMENTO:         { it: 'dichiara la regola del momento',
                                          en: 'declares the timing rule' },
    CONTEXTO_DE_MERCADO:                { it: 'contesto di mercato',
                                          en: 'market context' },
    MOVIMENTO_DE_CONCORRENTE:           { it: 'movimento di un concorrente',
                                          en: 'a competitor’s move' },
    NAO_DECIDE_NENHUM_ELO:              { it: 'non decide nessun anello della catena',
                                          en: 'decides no link in the chain' }
  };

  const EVIDENCE_FAMILY = {
    FIELD_SIGNAL:             { it: 'Bollettino di campo',        en: 'Field bulletin' },
    LABEL_USE_RELATIONSHIP:   { it: 'Etichetta ministeriale',     en: 'Ministerial label' },
    SCIENTIFIC_RECORD:        { it: 'Documento scientifico',      en: 'Scientific record' },
    MARKET_OBSERVATION:       { it: 'Osservazione di mercato',    en: 'Market observation' },
    REGULATORY_FUTURE_FACT:   { it: 'Fatto regolatorio futuro',   en: 'Forward regulatory fact' },
    REGULATORY_PRODUCT:       { it: 'Registro del prodotto',      en: 'Product register' },
    ACTIVE_INGREDIENT:        { it: 'Sostanza attiva',            en: 'Active substance' },
    COMPETITOR_ACTIVITY:      { it: 'Attivita di un concorrente', en: 'Competitor activity' },
    RESISTANCE_RECORD:        { it: 'Registro di resistenza',     en: 'Resistance record' },
    CROP_ECONOMIC_WEIGHT_CLAIM:{ it: 'Peso economico della coltura', en: 'Crop economic weight' }
  };

  /* ── IL BRIEF · la prima lettura, breve ───────────────────────────────── */
  const BRIEF_CODE = {
    PRESSAO_RECENTE:  { it: 'Pressione recente sostenuta da segnali di campo e fonti indipendenti.',
                        en: 'Recent pressure supported by field signals and independent sources.' },
    JANELA_ABERTA:    { it: 'La condizione che definisce il momento e dichiarata presente ora.',
                        en: 'The condition that defines the moment is declared present now.' },
    JANELA_DEFINIDA_ESTADO_DESCONHECIDO:{ it: 'La condizione e nota; lo stato attuale non e ancora misurato.',
                        en: 'The condition is known; the current state is not yet measured.' },
    JANELA_DELEGADA_AO_POMAR:{ it: 'La decisione dipende dall’osservazione in campo.',
                        en: 'The decision depends on farm-level observation.' },
    SEM_JANELA:       { it: 'Nessuna condizione dichiarata definisce il momento.',
                        en: 'No declared condition defines the moment.' },
    FONTE_MANDA_PARAR:{ it: 'La fonte che sostiene la coppia non manda agire.',
                        en: 'The source behind the pair does not call for action.' },
    PORTFOLIO:        { it: 'Portafoglio ADAMA collegato alla coppia.',
                        en: 'ADAMA portfolio linked to the pair.' },
    SEM_PORTFOLIO:    { it: 'Nessun prodotto ADAMA a catalogo per questa coppia.',
                        en: 'No ADAMA catalogue product for this pair.' },
    ACAO_PRINCIPAL:   { it: 'Prima area chiamata ad agire.',
                        en: 'First area called to act.' }
  };

  const GEOGRAPHIC_SCOPE = {
    EUROPEU:    { it: 'Europeo',    en: 'European' },
    NACIONAL:   { it: 'Nazionale',  en: 'National' },
    REGIONAL:   { it: 'Regionale',  en: 'Regional' },
    PROVINCIAL: { it: 'Provinciale',en: 'Provincial' }
  };

  const COMMERCIAL_MAGNITUDE = {
    MEASURED_BY_DIMENSION: { it: 'Misurata per dimensioni dichiarate',
                             en: 'Measured by declared dimensions' },
    UNKNOWN:               { it: 'Non misurata',
                             en: 'Not measured' }
  };
  const COMMERCIAL_TIMING_BASIS = {
    CURRENT_SOURCE_RECOMMENDATION: { it: 'Raccomandazione attuale della fonte',
                                     en: 'Current source recommendation' },
    NONE:                          { it: 'Nessuna base temporale dichiarata',
                                     en: 'No declared timing basis' }
  };

  const MAGNITUDE_DIMENSION = {
    SINAIS_DE_CAMPO:      { it: 'segnali di campo',        en: 'field signals' },
    FONTES_INDEPENDENTES: { it: 'fonti indipendenti',      en: 'independent sources' },
    REGIOES_DO_PAR:       { it: 'regioni della coppia',    en: 'regions of the pair' },
    AREA_OFICIAL_HA:      { it: 'superficie ufficiale (ha)', en: 'official area (ha)' },
    AREA_OFICIAL_ANO:     { it: 'anno della superficie',   en: 'year of the area' }
  };

  /* ── LE ETICHETTE DI SCHERMO · titoli di sezione, non dati ────────────── */
  const UI = {
    whatIsHappening:  { it: 'CHE COSA STA SUCCEDENDO',       en: 'WHAT IS HAPPENING' },
    whyCommercial:    { it: 'PERCHE E UN’OPPORTUNITA PER ADAMA', en: 'WHY THIS IS AN OPPORTUNITY FOR ADAMA' },
    whatAdamaHas:     { it: 'CHE COSA HA ADAMA',             en: 'WHAT ADAMA HAS' },
    whyNow:           { it: 'PERCHE ORA',                    en: 'WHY NOW' },
    whatBlocks:       { it: 'CHE COSA IMPEDISCE ANCORA L’AZIONE', en: 'WHAT STILL BLOCKS ACTION' },
    theWindow:        { it: 'LA FINESTRA',                   en: 'THE WINDOW' },
    actionMap:        { it: 'MAPPA DELLE AZIONI',            en: 'ACTION MAP' },
    evidence:         { it: 'LE PROVE',                      en: 'THE EVIDENCE' },
    whoActs:          { it: 'Chi agisce ora',                en: 'Who acts now' },
    whoValidates:     { it: 'Chi valida',                    en: 'Who validates' },
    whoPrepares:      { it: 'Chi prepara',                   en: 'Who prepares' },
    whoWaits:         { it: 'Chi segue',                     en: 'Who watches' },
    whatUnlocks:      { it: 'Che cosa sblocca il passo successivo', en: 'What unlocks the next step' },
    dependsOn:        { it: 'Dipende da',                    en: 'Depends on' },
    nextTrigger:      { it: 'Si sblocca con',                en: 'Unlocked by' },
    openSource:       { it: 'APRI LA FONTE',                 en: 'OPEN SOURCE' },
    stage:            { it: 'Stadio dell’insetto',      en: 'Insect stage' },
    recommendation:   { it: 'Raccomandazione della fonte',   en: 'Source recommendation' },
    threshold:        { it: 'Soglia',                        en: 'Threshold' },
    activeIngredients:{ it: 'Sostanze attive',               en: 'Active ingredients' },
    modeOfAction:     { it: 'Meccanismo d’azione',      en: 'Mode of action' },
    registration:     { it: 'N. registrazione',             en: 'Registration no.' },
    restrictions:     { it: 'Limitazioni',                   en: 'Restrictions' },
    allMatches:       { it: 'Tutti i prodotti compatibili',  en: 'All compatible products' },
    noPrimaryRule:    { it: 'Nessun prodotto e indicato come principale',
                        en: 'No product is presented as primary' },
    windowCondition:  { it: 'La condizione e dichiarata nel documento',
                        en: 'The condition is declared in document' },
    meetingSnapshot:  { it: 'Snapshot della riunione',       en: 'Meeting snapshot' },
    notMeasured:      { it: 'non ancora misurato',           en: 'not yet measured' }
  };

  /* ── L’ACCESSO · una sola funzione, e restituisce null se non sa ─── */
  const TABLES = {
    STATUS: STATUS, STATUS_WHY: STATUS_WHY, COMMERCIAL_PRIORITY: COMMERCIAL_PRIORITY,
    ARCHETYPE: ARCHETYPE, PUBLICATION_STATE: PUBLICATION_STATE,
    PUBLICATION_STATE_SHORT: PUBLICATION_STATE_SHORT, TRAIL_STATE: TRAIL_STATE,
    OPPORTUNITY_STATE: OPPORTUNITY_STATE, WINDOW_TYPE: WINDOW_TYPE,
    WINDOW_RULE_STATE: WINDOW_RULE_STATE, WINDOW_OPEN_NOW: WINDOW_OPEN_NOW,
    WINDOW_DEFINED: WINDOW_DEFINED, WINDOW_OPEN_NOW_METHOD: WINDOW_OPEN_NOW_METHOD,
    WINDOW_CONFIDENCE: WINDOW_CONFIDENCE, NEED_DIRECTION: NEED_DIRECTION,
    NEED_METHOD: NEED_METHOD, PEST_STAGE_STATE: PEST_STAGE_STATE,
    ACTION_RECOMMENDATION_STATE: ACTION_RECOMMENDATION_STATE,
    THRESHOLD_STATE: THRESHOLD_STATE, WHY_NOW_CODES: WHY_NOW_CODES,
    CHAIN_LINK: CHAIN_LINK, WHY_COMMERCIAL_CODES: WHY_COMMERCIAL_CODES,
    WHAT_IS_MISSING: WHAT_IS_MISSING, EXTERNAL_BLOCKER_CODES: EXTERNAL_BLOCKER_CODES,
    EXTERNAL_MATERIAL_READY: EXTERNAL_MATERIAL_READY, SIGNAL_CURRENCY: SIGNAL_CURRENCY,
    CONFIDENCE: CONFIDENCE, PRODUCT_LINK_STATE: PRODUCT_LINK_STATE,
    CROP_FIT: CROP_FIT, TARGET_FIT: TARGET_FIT, REGIONAL_FIT: REGIONAL_FIT,
    REGULATORY_FIT: REGULATORY_FIT, WINDOW_FIT: WINDOW_FIT,
    VALIDATION_STATE: VALIDATION_STATE, MATCH_REASON: MATCH_REASON,
    PRIMARY_MATCH_REASON: PRIMARY_MATCH_REASON, RESTRICTION_CODE: RESTRICTION_CODE,
    MODE_OF_ACTION_STATE: MODE_OF_ACTION_STATE, APPLICATION_STATE: APPLICATION_STATE,
    DEPARTMENT: DEPARTMENT, ACTION_STATE: ACTION_STATE, ACTION: ACTION,
    ACTION_WHY_CODE: ACTION_WHY_CODE, DEPENDENCY: DEPENDENCY, NEXT_TRIGGER: NEXT_TRIGGER,
    EVIDENCE_ROLE: EVIDENCE_ROLE, EVIDENCE_WHY_CODE: EVIDENCE_WHY_CODE,
    EVIDENCE_FAMILY: EVIDENCE_FAMILY, BRIEF_CODE: BRIEF_CODE,
    GEOGRAPHIC_SCOPE: GEOGRAPHIC_SCOPE, COMMERCIAL_MAGNITUDE: COMMERCIAL_MAGNITUDE,
    COMMERCIAL_TIMING_BASIS: COMMERCIAL_TIMING_BASIS,
    MAGNITUDE_DIMENSION: MAGNITUDE_DIMENSION, UI: UI
  };

  /* label('STATUS','ACT_NOW','it') -> 'AGIRE ORA'
     Un codice sconosciuto restituisce null: chi chiama sceglie il fallback,
     e un null visibile in un gate vale piu di una parola inventata. */
  function label(table, code, lang) {
    if (code === null || code === undefined) return null;
    const T = TABLES[table];
    if (!T) return null;
    const row = T[String(code)];
    if (!row) return null;
    return row[(lang === 'en') ? 'en' : 'it'] || null;
  }

  function labels(table, codes, lang) {
    return (codes || []).map((c) => label(table, c, lang)).filter(Boolean);
  }

  /* Ogni codice che questo file conosce — il gate NO_INTERNAL_CODES lo usa
     per provare che nessuna tabella e rimasta indietro rispetto allo snapshot. */
  function known(table) { return Object.keys(TABLES[table] || {}); }

  window.MEETING_LABELS = {
    TABLES: TABLES, label: label, labels: labels, known: known,
    STAGE_VS_RECOMMENDATION_NOTE: STAGE_VS_RECOMMENDATION_NOTE
  };
})();
