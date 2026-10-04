/* SINTONIA · LABEL INTELLIGENCE · o dicionario dos estados, e de onde ele vem
   ---------------------------------------------------------------------------
   A ferramenta de origem tem uma lei que viaja com o dado:

       TODO TOKEN DE IGNORANCIA TEM DE CONTINUAR VISIVEL COM O PROPRIO NOME.
       Troca-lo por «-», «0», «N/A» ou celula vazia quebra a lei zero.

   E o portal tem a sua, do contrato de design: «NAO SEI» com o mesmo peso
   tipografico do facto, nunca cinza-claro, nunca colapsado por defeito.

   As duas leis apontam para o mesmo sitio, e nenhuma delas pede que o leitor
   saiba ingles de maquina. Entao a tela mostra as DUAS coisas, juntas:

       PAIR_NOT_CHECKABLE_ROUTE_NOT_GEOMETRIC     <- o nome proprio, intacto
       «non c'era tabella disegnata su cui misurare»

   A GLOSA NAO E MINHA. Cada uma abaixo e reducao do texto de
   `v1/inteligencia/REGRAS.md` — a lei escrita da propria ferramenta, no ramo
   claude/label-intelligence-v1-italy. Onde a lei nao explica um estado, a glosa
   fica vazia e o token aparece sozinho.

       UMA GLOSA INVENTADA E UMA AFIRMACAO SEM FONTE COM CARA DE AJUDA.

   `regra` liga o estado ao id que o emite, para a tela poder citar a lei e o
   leitor poder ir le-la. O portao `etichette-gate.mjs` confere duas coisas
   sobre este ficheiro: que todo estado que chega a tela tem entrada aqui, e que
   toda regra citada aqui existe em REGRAS.md — a mesma disciplina do portao
   `UI_RULE_IDS_ARE_DEFINED_IN_REGRAS` da ferramenta de origem.               */
(function () {
  const T = (regra, it, en) => ({ regra, it, en });

  window.ITALY_LABEL_LEXICON = {
    FONTE: {
      documento: 'v1/inteligencia/REGRAS.md',
      ramo: 'claude/label-intelligence-v1-italy',
      it: 'Ogni stato porta il nome della regola che lo emette.',
      en: 'Every state carries the name of the rule that emits it.',
    },

    /* ── la coppia coltura × bersaglio · R-14 ────────────────────────────── */
    PAIR_CONSISTENT_WITH_RULES: T('R-14',
      'il bersaglio sta dentro la cella disegnata della coltura: è la tabella che unisce i due',
      'the target sits inside the drawn cell of the crop: the table itself joins the two'),
    PAIR_NOT_CHECKABLE_ROUTE_NOT_GEOMETRIC: T('R-14',
      'non c’era tabella disegnata su cui misurare: la coppia viene dal testo, non dalla geometria',
      'there was no drawn table to measure on: the pair comes from text, not geometry'),
    PAIR_NOT_CHECKABLE_ANCHOR_NOT_FOUND: T('R-14',
      'il nome della coltura non è stato ritrovato nella pagina per ancorare la misura',
      'the crop name was not found on the page to anchor the measurement'),
    PAIR_NOT_CHECKABLE_NO_DRAWN_CELL: T('R-14',
      'la pagina non disegna la cella: non c’è cella da misurare',
      'the page draws no cell: there is no cell to measure'),
    PAIR_NOT_CHECKABLE_CROP_ALSO_OUTSIDE_TABLE: T('R-14',
      'il nome della coltura compare anche fuori dalla tabella: l’ancoraggio non è univoco',
      'the crop name also appears outside the table: the anchor is not unique'),
    PAIR_NOT_CHECKABLE_RULES_ARE_TEXT_UNDERLINES: T('R-14',
      'i tratti della pagina sono sottolineature di testo, non fili di tabella',
      'the strokes on the page are text underlines, not table rules'),
    PAIR_NOT_CHECKABLE_CROP_NAME_NOT_THE_ANCHOR: T('R-14',
      'il nome della coltura non è l’àncora della cella',
      'the crop name is not the anchor of the cell'),
    PAIR_NOT_CHECKABLE_TABLE_NOT_DESCRIBING_ITS_TEXT: T('R-14',
      'la tabella disegnata non descrive il testo che contiene',
      'the drawn table does not describe the text it contains'),
    USE_PAIR_PROVEN_BY_TABLE_GEOMETRY: T('R-14',
      'coppia provata dalla geometria della tabella',
      'pair proven by the geometry of the table'),
    USE_PAIR_NOT_VERIFIED_BY_ANY_RULE: T('R-14',
      'nessuna regola ha potuto verificare questa coppia: resta pubblicata, e resta non provata',
      'no rule was able to verify this pair: it stays published, and it stays unproven'),

    /* ── il nome del bersaglio · R-17 ────────────────────────────────────── */
    TARGET_NAME_LITERAL: T('R-17',
      'il nome del bersaglio è scritto così nel documento',
      'the target name is written exactly so in the document'),
    TARGET_NAME_INFLECTED_IN_LABEL: T('R-17',
      'il documento scrive una flessione del nome — «Ruggini» per RUGGINE',
      'the document writes an inflection of the name — «Ruggini» for RUGGINE'),
    TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL: T('R-17',
      'il nome viene da una tassonomia che questo archivio non possiede: è inferenza, e viaggia etichettata come inferenza',
      'the name comes from a taxonomy this archive does not hold: it is inference, and it travels labelled as inference'),
    TARGET_NAME_NOT_CHECKED: T('R-17', 'controllo non eseguito', 'check not run'),

    /* ── il nome della coltura · R-21 ────────────────────────────────────── */
    CROP_NAME_LITERAL: T('R-21',
      'il nome della coltura è scritto così nel documento',
      'the crop name is written exactly so in the document'),
    CROP_NAME_INFLECTED_IN_LABEL: T('R-21',
      'il documento scrive una flessione del nome',
      'the document writes an inflection of the name'),
    CROP_NAME_NOT_IN_LABEL: T('R-21',
      'il documento non scrive questo nome: passare dalla parola scritta al nome pubblicato sarebbe un’equivalenza di coltura, e un’equivalenza ha bisogno di prova',
      'the document does not write this name: going from the written word to the published name would be a crop equivalence, and an equivalence needs proof'),
    CROP_NAME_PREFIX_MATCH_ONLY: T('R-21',
      'combacia solo il prefisso della parola: somiglianza di scrittura non è prova',
      'only the prefix of the word matches: similarity of spelling is not proof'),
    CROP_NAME_NOT_FOUND_IN_LABEL_TEXT: T('R-21',
      'il nome non è stato ritrovato nel testo del documento',
      'the name was not found in the text of the document'),

    /* ── la citazione · R-18 ─────────────────────────────────────────────── */
    QUOTE_VERBATIM: T('R-18',
      'la frase esiste letterale e contigua in una lettura piatta del PDF: solo questo stato ottiene le virgolette',
      'the sentence exists literal and contiguous in a flat reading of the PDF: only this state earns quotation marks'),
    QUOTE_CUT_MID_WORD: T('R-18',
      'la lettura taglia a metà di una parola: non è una frase del documento',
      'the reading cuts mid-word: it is not a sentence of the document'),
    QUOTE_HAS_UNBALANCED_PARENTHESIS: T('R-18',
      'parentesi aperta e mai chiusa: il ritaglio ha perso un pezzo',
      'a parenthesis opened and never closed: the cut lost a piece'),
    QUOTE_NOT_CONTIGUOUS_IN_DOCUMENT: T('R-18',
      'le parole ci sono, ma non una accanto all’altra: la frase è stata rimontata',
      'the words are there, but not next to one another: the sentence was reassembled'),
    QUOTE_TOO_SHORT_TO_CHECK: T('R-18',
      'troppo corta perché il controllo abbia significato',
      'too short for the check to mean anything'),
    QUOTE_CUT_MID_LINE: T('R-18',
      'la lettura taglia a metà di una riga',
      'the reading cuts mid-line'),
    QUOTE_ONLY_IN_COLUMN_RECONSTRUCTION: T('R-18',
      'esiste solo nella ricostruzione per colonna, che incolla le righe senza guardare i fili orizzontali',
      'it exists only in the column reconstruction, which glues rows together without looking at the horizontal rules'),
    ROW_HAS_WORDS_NOT_ON_THE_PAGE: T('R-18',
      'la riga contiene parole che nella pagina non ci sono',
      'the row contains words that are not on the page'),
    ROW_RECONSTRUCTED_FROM_CELLS: T('R-18',
      'riga rimontata a partire dalle celle',
      'row reassembled from the cells'),

    /* ── la dose · R-11 R-12 R-13 R-15 R-22 ─────────────────────────────── */
    CROP_ASSIGNMENT_CONSISTENT_WITH_RULES: T('R-11',
      'la coltura sta nella stessa cella disegnata della riga di dose',
      'the crop sits in the same drawn cell as the dose row'),
    CROP_ASSIGNMENT_CONTRADICTED_BY_RULE: T('R-11',
      'un filo disegnato separa la riga dalla coltura: la riga non è di questa coltura, e la dose non si pubblica',
      'a drawn rule separates the row from the crop: the row does not belong to this crop, and the dose is withheld'),
    CROP_ASSIGNMENT_NOT_CHECKED: T('R-11', 'controllo non eseguito', 'check not run'),
    TARGET_TEXT_FOUND_LITERALLY: T('R-13',
      'il testo del bersaglio si ritrova letterale nel documento',
      'the target text is found literally in the document'),
    TARGET_TEXT_NOT_FOUND_LITERALLY: T('R-13',
      'il testo del bersaglio non si ritrova letterale: è la tela che toglie il numero',
      'the target text is not found literally: it is the screen that withholds the number'),
    DOSE_ROW_BAND_IS_ONE_DRAWN_ROW: T('R-22',
      'dentro la banda letta non passa nessun filo disegnato: è una riga sola',
      'no drawn rule crosses the band that was read: it is a single row'),
    DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE: T('R-22',
      'un filo disegnato attraversa la banda: sono due righe, e il numero non si pubblica. È la regola più severa del gruppo — delle 10 bande che boccia, un arbitro indipendente ne ha verificate 8 come dose corretta',
      'a drawn rule crosses the band: these are two rows, and the number is withheld. This is the strictest rule of the set — of the 10 bands it rejects, an independent referee verified 8 as correct doses'),
    DOSE_ROW_BAND_NOT_CHECKED: T('R-22', 'controllo non eseguito', 'check not run'),
    MAX_CONFIRMED_BY_RULE: T('R-15',
      'il massimo di applicazioni sta in una cella disegnata che copre la riga',
      'the maximum number of applications sits in a drawn cell that covers the row'),
    MAX_CONTRADICTED_BY_RULE: T('R-15',
      'la cella del massimo non copre questa riga: il numero non si eredita',
      'the cell of the maximum does not cover this row: the number is not inherited'),
    MAX_CONTRADICTED_BY_LABEL_NOTE: T('R-15',
      'una nota dell’etichetta contraddice il massimo ereditato',
      'a note on the label contradicts the inherited maximum'),
    MAX_NOT_INHERITED: T('R-15', 'non ereditato da nessuna cella', 'not inherited from any cell'),
    MAX_NOT_VALIDATED: T('R-15', 'senza prova: nessun numero col sigillo «ereditata»', 'without proof: no number carries the «inherited» seal'),
    MAX_NOT_PROVED_NOTE_BLOCK_UNKNOWN: T('R-15', 'il blocco di note non è stato riconosciuto', 'the note block was not recognised'),
    INTERVAL_CONFIRMED_BY_RULE: T('R-15', 'intervallo confermato dalla cella disegnata', 'interval confirmed by the drawn cell'),
    INTERVAL_CONTRADICTED_BY_RULE: T('R-15', 'la cella dell’intervallo non copre questa riga', 'the interval cell does not cover this row'),
    INTERVAL_NOT_INHERITED: T('R-15', 'non ereditato da nessuna cella', 'not inherited from any cell'),
    INTERVAL_NOT_VALIDATED: T('R-15', 'senza prova', 'without proof'),
    INTERVAL_NOT_CHECKED: T('R-15', 'controllo non eseguito', 'check not run'),
    CONFIRMED_BY_RULE: T('R-15', 'confermato dalla cella disegnata', 'confirmed by the drawn cell'),
    CONTRADICTED_BY_RULE: T('R-15', 'contraddetto dalla cella disegnata', 'contradicted by the drawn cell'),
    PLAUSIBILITY_REJECTED: T('P-01',
      'la nostra lettura di questa riga non sembra una riga di dose: è euristica nostra, non misura del documento, e manda la riga a revisione umana',
      'our reading of this row does not look like a dose row: this is our own heuristic, not a measurement of the document, and it sends the row to human review'),
    SPURIOUS_TABLE_DISCARDED: T('P-01',
      'nessuna riga della tabella candidata porta dose: l’estrattore ha trovato tabella dove c’era prosa',
      'no row of the candidate table carries a dose: the extractor found a table where there was prose'),

    /* ── l’esclusione · R-10 e R-10b ────────────────────────────────── */
    ATTESTED_OUTSIDE_EXCLUSION: T('R-10',
      'il nome della coltura compare almeno una volta fuori da una finestra di esclusione',
      'the crop name appears at least once outside an exclusion window'),
    CROP_ONLY_INSIDE_EXCLUSION: T('R-10',
      'l’unico appoggio testuale sta DENTRO una finestra di esclusione: un’esclusione non è un permesso',
      'the only textual support sits INSIDE an exclusion window: an exclusion is not a permission'),
    CROP_ONLY_IN_ROTATION_RESTRICTION: T('R-10b',
      'la coltura compare solo in una frase di semina in rotazione: un divieto di semina non è un uso',
      'the crop appears only in a sowing-in-rotation sentence: a sowing ban is not a use'),

    /* ── la vigenza dichiarata dall’etichetta · R-19 ────────────────── */
    VALIDITY_WINDOW_READ: T('R-19',
      'la finestra di validità è stata letta nella forma «valida dal X al Y»',
      'the validity window was read in the form «valida dal X al Y»'),
    VALIDITY_PHRASE_PRESENT_FORM_NOT_READ: T('R-19',
      'l’etichetta dichiara la validità in una forma che questa regola non traduce in data. Il fallimento del lettore non è assenza regolatoria: la frase letterale sta qui accanto',
      'the label declares validity in a form this rule does not turn into a date. Reader failure is not regulatory absence: the literal sentence is right beside it'),
    VALIDITY_PHRASE_NOT_FOUND: T('R-19', 'nessuna frase di validità trovata nel documento', 'no validity sentence found in the document'),
    VALIDITY_NOT_CHECKED: T('R-19', 'controllo non eseguito', 'check not run'),
    SOURCE_DATE_MATCHES_VALIDITY_PHRASE: T('R-19', 'la data della fonte coincide con la frase di validità', 'the source date matches the validity sentence'),
    SOURCE_DATE_MATCHES_DECREE_ONLY: T('R-19', 'la data della fonte coincide solo col decreto, non con la validità', 'the source date matches the decree only, not the validity'),
    SOURCE_DATE_NOT_FOUND_IN_DOCUMENT: T('R-19', 'la data della fonte non compare nel documento', 'the source date does not appear in the document'),

    /* ── la copertura per cella di coltura · R-20 ────────────────────────── */
    CROP_BLOCK_READ: T('R-20', 'cella di coltura disegnata e letta', 'crop cell drawn and read'),
    CROP_BLOCK_NOT_COLLECTED: T('R-20', 'cella non raccolta', 'cell not collected'),
    CROP_BLOCK_IN_VOCABULARY_NOT_READ: T('R-20',
      'il nome E nel vocabolario e la cella non è diventata coppia: non è differenza di dizionario, ed è il più grave dei tre stati',
      'the name IS in the vocabulary and the cell never became a pair: this is not a dictionary gap, and it is the gravest of the three states'),

    /* ── rotta e provenienza della riga ──────────────────────────────────── */
    TABLE_GEOMETRY: T('R-14', 'letta dalla geometria della tabella', 'read from the geometry of the table'),
    GEOMETRIC_TABLE: T('R-14', 'tabella con fili disegnati', 'table with drawn rules'),
    MERGED_COLUMN_TABLE: T('R-14', 'tabella a colonne unite', 'table with merged columns'),
    TEXT_INFERENCE: T('R-14', 'dedotta dal testo, non dalla geometria', 'inferred from the text, not from the geometry'),
    AUTHORISED_USE_LIST: T('R-14', 'da un elenco di usi autorizzati, non da una tabella', 'from a list of authorised uses, not from a table'),
    INLINE_COLON_HEAD: T('R-14', 'da una testata in linea con i due punti', 'from an inline heading with a colon'),
    INLINE_STATEMENT: T('R-14', 'da una frase in linea', 'from an inline statement'),
    HEADER_CONTINUATION: T('R-14', 'continuazione di un’intestazione', 'continuation of a header'),
    USE_TABLE_READ: T('R-14', 'tabella degli usi letta', 'use table read'),
    TABLE_FOUND_NO_ROWS: T('R-14', 'tabella trovata, nessuna riga letta', 'table found, no row read'),
    NO_USE_TABLE_FOUND: T('R-14',
      'nessuna tabella d’uso trovata in questo documento. Il fallimento del lettore non è assenza regolatoria',
      'no use table found in this document. Reader failure is not regulatory absence'),

    /* ── i tokens di ignoranza generici ──────────────────────────────────── */
    NOT_PRESERVED: T('', 'il dato esisteva a monte e non è stato conservato fin qui', 'the datum existed upstream and was not preserved this far'),
    NOT_PRESENT: T('', 'non presente nel documento', 'not present in the document'),
    NOT_APPLICABLE: T('', 'non applicabile a questa riga', 'not applicable to this row'),
    NOT_CHECKED: T('', 'controllo non eseguito', 'check not run'),
    NOT_ATTEMPTED: T('', 'controllo non tentato', 'check not attempted'),
    NOT_LOCATED: T('', 'non localizzato nel documento', 'not located in the document'),
  };
}());
