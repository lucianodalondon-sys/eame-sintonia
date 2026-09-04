/* GERADO por scripts/it_casa_dados.py — nao editar a mao.
   Os numeros vem dos handoffs ja ingeridos; aqui nao se reconta nada. */
window.ITALY_CASA = {
 "AUTORIZACOES": {
  "AGRUPAR_AS_CINCO_E": "GIUDIZIO UMANO, non fatto del registro — è la lacuna DECK-015 (titolare non equivale a gruppo societario)",
  "AMPLIADO_CINCO_RAZOES": 155,
  "CRITERIO_AMPLIADO": "STRICT piu «Ri-registrato*» e «Rinnovato*»",
  "CRITERIO_STRICT": "solo gli stati amministrativi che contengono «Autorizzato»",
  "DATA_DO_SNAPSHOT": "2026-08-24",
  "LIMITE": "conteggio di registri, e nient'altro. Non è quota di mercato.",
  "SEM_DONO": "NON SO, dichiarato. Un'autorizzazione sospesa non è né vigente né revocata, e nessuno dei criteri sopra dice cosa farne. Non si forza da nessuna parte finché non esiste una regola che ne risponda.",
  "STRICT_CINCO_RAZOES": 89
 },
 "COBERTURA": {
  "A_EXPANSAO_E": "REGOLA METODOLOGICA, non dato grezzo: un'organizzazione territoriale Tier A/B senza specialità dichiarata copre tutte le specialità della sua coltura in quella regione",
  "A_EXPANSAO_E_PT": "REGRA METODOLÓGICA, não fato bruto: organização territorial Tier A/B sem especialidade declarada cobre todas as especialidades da sua cultura naquela região",
  "CELULAS": 117,
  "COM_EXPANSAO_GOOD": 72,
  "SEM_EXPANSAO_GOOD": 30
 },
 "DATA_DE_REFERENCIA": "2026-09-04",
 "DESTAQUE": {
  "ACTIVATION_QUESTION": "Portafoglio e Sviluppo Mercato: il rinnovo del 31/05/2027 è già in corso, e lo scarto di finestra conta commercialmente?",
  "ADAMA_ATE": "31/05/2027",
  "CONCORRENTE_ATE": "31/03/2028",
  "CRITERIO": "prodotti il cui campo `sostanze_attive` nomina AZOXYSTROBIN e PROTHIOCONAZOLE insieme",
  "CRITERIO_PT": "produtos cujo campo `sostanze_attive` nomeia AZOXYSTROBIN E PROTHIOCONAZOLE ao mesmo tempo",
  "DATA_DO_SNAPSHOT": "2026-08-24",
  "DELTA_MESES": 10,
  "E_UNIVERSO_FECHADO": "sì",
  "FATO": "quattro registri, tutti vigenti: due di ADAMA ITALIA S.R.L. in scadenza il 31/05/2027 e due di CAC CHEMICAL GMBH in scadenza il 31/03/2028",
  "FATO_PT": "quatro registros, todos vigentes: dois da ADAMA ITALIA S.R.L. vencendo em 31/05/2027 e dois da CAC CHEMICAL GMBH vencendo em 31/03/2028",
  "FONTE": "Ministero della Salute — Banca dati prodotti fitosanitari (dati.salute.gov.it), CC BY 4.0",
  "INTERPRETACAO": "il concorrente ha circa 10 mesi in più di finestra autorizzata sulla stessa coppia di sostanze",
  "INTERPRETACAO_PT": "o concorrente tem ~10 meses a mais de janela autorizada na mesma dupla de substâncias",
  "ITENS": [
   {
    "ESTADO_ADMINISTRATIVO": "Autorizzato con procedura zonale",
    "PRODUTO": "MAXENTIS",
    "REGISTRO": "018067",
    "TITULAR": "ADAMA ITALIA S.R.L.",
    "VENCIMENTO": "31/05/2027"
   },
   {
    "ESTADO_ADMINISTRATIVO": "Autorizzato con procedura zonale",
    "PRODUTO": "PROMINO XTRA",
    "REGISTRO": "019093",
    "TITULAR": "CAC CHEMICAL GMBH",
    "VENCIMENTO": "31/03/2028"
   },
   {
    "ESTADO_ADMINISTRATIVO": "Autorizzato Art. 10 D.P.R. 290/2001",
    "PRODUTO": "KOJAMI",
    "REGISTRO": "019095",
    "TITULAR": "ADAMA ITALIA S.R.L.",
    "VENCIMENTO": "31/05/2027"
   },
   {
    "ESTADO_ADMINISTRATIVO": "Autorizzato Art. 10 D.P.R. 290/2001",
    "PRODUTO": "AMISTAR ERA 240 EC",
    "REGISTRO": "019194",
    "TITULAR": "CAC CHEMICAL GMBH",
    "VENCIMENTO": "31/03/2028"
   }
  ],
  "QUEM_DECIDE": "se il rinnovo del 31/05/2027 sia già in corso, e se lo scarto di finestra conti commercialmente",
  "QUEM_DECIDE_PT": "se a renovação de 31/05/2027 já está em curso, e se a diferença de janela importa comercialmente",
  "TITULO": "AZOXYSTROBIN + PROTHIOCONAZOLE",
  "TRAVA_DE_INDEPENDENCIA": "atto europeo e registro nazionale NON sono due fonti indipendenti: il nazionale deriva dall'europeo. Contarli come due conferme gonfia la fiducia in un fatto che ha una sola origine.",
  "TRAVA_DE_INDEPENDENCIA_PT": "ato europeu e registro nacional NÃO são duas fontes independentes: o nacional deriva do europeu. Contá-los como duas confirmações infla a confiança de um fato que tem uma origem só.",
  "UNIVERSO": 4
 },
 "DETERMINISTICO": "SIM — sem relogio, sem aleatorio, chaves ordenadas",
 "DO_NOT_SHOW": [
  {
   "ACHADO": "04_SOCIAL_YOUTUBE",
   "DIZER": "existência de legenda: NÃO SEI em 150 de 150",
   "NAO_DIZER": "0 legendas"
  },
  {
   "ACHADO": "02_AUTORIZACOES_ADAMA",
   "DIZER": "155 sob critério AMPLIADO, cinco razões sociais somadas, snapshot de 2026-08-24; sob STRICT são 89",
   "NAO_DIZER": "ADAMA possui 155 autorizações"
  },
  {
   "ACHADO": "05_PESSOAS_E_PAPEIS",
   "DIZER": "90 entidades com ao menos um papel provado, de 221",
   "NAO_DIZER": "114 pessoas"
  },
  {
   "ACHADO": "05_PESSOAS_E_PAPEIS",
   "DIZER": "5 papéis de campo provados: 3 técnicos e 2 cooperativas; agrônomo, produtor e consultor provados = 0",
   "NAO_DIZER": "temos agrônomos e produtores na base"
  },
  {
   "ACHADO": "06_COBERTURA_TERRITORIAL",
   "DIZER": "72 com a expansão territorial declarada; 30 sem ela",
   "NAO_DIZER": "cobertura BOA em 72 células"
  },
  {
   "ACHADO": "06_COBERTURA_TERRITORIAL",
   "DIZER": "temos olhos nesta região",
   "NAO_DIZER": "há problema nesta região"
  },
  {
   "ACHADO": "04_SOCIAL_YOUTUBE",
   "DIZER": "61 por casamento lexical de título, não verificados — mesmo classificador dos 82 não julgáveis",
   "NAO_DIZER": "61 documentos relevantes"
  },
  {
   "ACHADO": "04_SOCIAL_YOUTUBE",
   "DIZER": "faixa de recência, sem exibir data",
   "NAO_DIZER": "qualquer data de publicação de documento social italiano"
  },
  {
   "ACHADO": "04_SOCIAL_YOUTUBE",
   "DIZER": "ULTIMA_COLETA nula em 243 de 243: não há linha de base",
   "NAO_DIZER": "mudou / está subindo, sobre fonte social italiana"
  },
  {
   "ACHADO": "04_SOCIAL_YOUTUBE",
   "DIZER": "sede legal é endereço de empresa, não lugar do fato",
   "NAO_DIZER": "mapa da Itália pintado pela sede do titular"
  },
  {
   "ACHADO": "09_ROTULO_OPORTUNIDADE",
   "DIZER": "ACTIVATION QUESTION — e para a Itália a base nem sustenta a pergunta ainda",
   "NAO_DIZER": "oportunidade / espaço livre / ativo subutilizado"
  },
  {
   "ACHADO": "01_AZOXISTROBINA_PROTIOCONAZOL",
   "DIZER": "o nacional deriva do europeu: é uma origem, não duas",
   "NAO_DIZER": "ato europeu e registro nacional confirmam o mesmo fato"
  },
  {
   "ACHADO": "03_REVOGADO_X_SCADUTO",
   "DIZER": "revogados; motivo declarado em 1.119 de 13.216",
   "NAO_DIZER": "X produtos foram retirados do mercado"
  },
  {
   "ACHADO": "02_AUTORIZACOES_ADAMA",
   "DIZER": "contagem de registros, e só",
   "NAO_DIZER": "contagem de registros como participação de mercado"
  }
 ],
 "EVIDENCIA": {
  "FITOSSANITARIO": 560,
  "LEI": "esta familia NAO e uma familia de cartoes. Sao 560 registos em 58 ficheiros de corpus bruto — videos, audios, transcricoes, falas, leituras de sessao e testemunhas de recolha. E a CAMADA DE EVIDENCIA por baixo das outras familias, e o seu lugar na tela e o destino de um link, nunca uma grelha propria.",
  "NUNCA_E_GRELHA": "raggiungibile dalla scheda che lo cita, mai come scheda propria"
 },
 "FONTES": {
  "COM_METODO": 91,
  "LIMITE": "qui c'è un problema",
  "LIMITE_PT": "há problema aqui",
  "RESPONDE": "qui abbiamo occhi",
  "RESPONDE_PT": "temos olhos aqui"
 },
 "GERADO_POR": "scripts/it_casa_dados.py",
 "HASHES_CONSUMIDOS": {
  "IT-FUTURO-HANDOFF-LINHA-B-V1.json": "sha256:5512f25e83a0da922fd6ca0e916f9ef398510633c62af3753f113674e58d0cc0",
  "IT-HANDOFF-LINHA-B-FITOSSANITARIO-V1.json": "sha256:328310a59e715c593405a51ee5eef4290bc17f502a3b6b6b854bb530158ed0db",
  "IT-HANDOFF-LINHA-B-FONTES-V1.json": "sha256:1f2058f40f0d0ff537c93eb7fa11deb605161f55d5d79e920e8a8265d3e901e1",
  "IT-HANDOFF-LINHA-B-SINAIS_DE_CAMPO-V1.json": "sha256:f7958ff29c00dddd282c9437c127c80d6b476c2e182e3ac558a53eefc33608f2",
  "IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json": "sha256:1283b4f7a292798f19a964421966316603e7c25aaa9d5b52aa7764bba74ec560",
  "IT-TOP3-SENSORES-V1.json": "sha256:bf134391b9f6f6ca7f5d8262516a13d5c3b43d877b2e5bbc24b2b7d045e39d88"
 },
 "LIMITACOES_DA_CAMADA_HUMANA": [
  "Nenhuma coleta de rede foi feita nesta rodada. Custo = 0.",
  "Nenhuma afirmação se apoia em legenda: nenhuma legenda foi obtida (D-040).",
  "data/raw/IT-T4-001/PROD_FTS.csv NÃO é versionado (D-003). Em clone novo ele não existe, e os achados 01, 02 e 03 voltam como NÃO SEI em vez de números. O hash do CSV está em ARTEFACT_HASHES para identificar o snapshot.",
  "O snapshot do registro é de 2026-08-24. Qualquer \"futuro\" calculado contra ele envelhece: 7 dos 20 próximos vencimentos publicados já haviam passado em 2026-09-04. Futuro se calcula contra a data de leitura.",
  "A camada territorial já gravada foi produzida com a leitura de data defeituosa (achado 07). Remedir antes de exibir qualquer recência.",
  "italia-portale/client não existe nesta branch e não foi tocado. O rótulo \"Radar Opportunità\" é relato do dono, não medição minha.",
  "Contagem de registros não é participação de mercado, em nenhum dos achados.",
  "P-012 (GDPR) segue aberta: a camada nomeia pessoas com afiliação e ORCID. Qualquer tela que liste gente identificada precisa de revisão antes."
 ],
 "NAO_ENTRA_NA_CASA": {
  "04_SOCIAL_YOUTUBE": "METHOD_ONLY no proprio handoff. Nao e destaque de HOME.",
  "05_PESSOAS_E_PAPEIS": "P-012 (GDPR) esta aberta: a camada nomeia pessoas com afiliacao e ORCID. Nao entra em tela nenhuma antes de revisao.",
  "RECENCIA_TERRITORIAL": "a camada territorial foi produzida com a leitura de data defeituosa do achado 07. Mostra-se cobertura, nunca recencia."
 },
 "RADAR_FUTURO": {
  "AGIR_AGORA": 0,
  "LIMITE": "nessuno di questi è un'opportunità di oggi: AGIRE ORA è zero per decisione della riga, non per mancanza di lettura",
  "MONITORAR": 21,
  "PORTFOLIO_LIMITED": 8,
  "PREPARAR": 23,
  "RENDERIZAVEIS": 44,
  "TOTAL": 45
 },
 "REVOGADO_X_SCADUTO": {
  "DEMONSTRACAO": "la sola data di scadenza non dice se un registro sia utilizzabile: 223 autorizzazioni sono REVOCATO con scadenza ancora nel futuro",
  "DEMONSTRACAO_PT": "data de validade sozinha não responde se um registro está utilizável: 223 autorizações estão REVOCATO com vencimento ainda no futuro",
  "LIMITE": "motivo dichiarato in 1.119 su 13.216. Per gli altri, il perché della revoca è NON SO — e non si deduce.",
  "LIMITE_PT": "motivo declarado em 1119 de 13216. Nos outros, por que foi revogado é NÃO SEI — e não se infere.",
  "REVOCATO": 13216,
  "REVOCATO_COM_VENCIMENTO_FUTURO": 223,
  "SCADUTO": 765
 },
 "SENSORES": {
  "DERRUBADOS": [
   {
    "AUTORIDADE": "SCIENTIFICA",
    "CAIU_PORQUE": "la clausola che sembrava piu solida — i bollettini di tre regioni — non ha retto: il segnale isola il danno sul grappolo, e la fonte che lo dichiara una volta l'anno non e un bollettino ma la sessione annuale di un convegno, con trascrizione da produrre.",
    "DECLARADA_PELO_AUTOR": "eseguibile con adattatore",
    "EXECUTABILITY": "non eseguibile",
    "EXECUTABILITY_TOKEN": "NAO_EXECUTAVEL",
    "ID": "ITFC-009",
    "TITULO": "Vite · black rot ed escoriosi su varietà resistenti",
    "TRANSICAO": "PREPARARE -> AGIRE ORA",
    "TRANSICAO_AUTORIZADA": "no",
    "TRANSICAO_TOKEN": "PREPARAR->AGIR_AGORA"
   },
   {
    "AUTORIDADE": "UFFICIALE",
    "CAIU_PORQUE": "quello che sembrava un innesco di cambiamento è, una volta reso osservabile, un innesco di conferma; e la fonte primaria — il Servizio Fitosanitario della Regione Siciliana — non ha scheda nel catalogo, quindi il suo accesso non è mai stato misurato. NON SO, non «non esiste».",
    "DECLARADA_PELO_AUTOR": "NON SO",
    "EXECUTABILITY": "non eseguibile",
    "EXECUTABILITY_TOKEN": "NAO_EXECUTAVEL",
    "ID": "ITFC-018",
    "TITULO": "Agrumi · dodina nelle linee tecniche siciliane",
    "TRANSICAO": "nessuna transizione sostenuta",
    "TRANSICAO_AUTORIZADA": "no",
    "TRANSICAO_TOKEN": "SEM_TRANSICAO_SUSTENTADA"
   }
  ],
  "NADA_FOI_REJULGADO": "SINAL_COMPLETO/PARCIAL/DERRUBADO, PREPARAR/MONITORAR/AGIR_AGORA, evidencia, portfolio, vocabulario e julgamento adversarial ficam exactamente como estavam em 9560823. Este ficheiro nao altera nenhum deles.",
  "REGRA": "si mostra solo ciò che ha retto all'attacco. Gli abbattuti compaiono come abbattuti, con il perché — mai come sensore.",
  "SOBREVIVERAM": [
   {
    "ADATTATORE": "tre pezzi: risolvere per anno il percorso della collezione Plone (la rotta provata finisce in «-2026»), filtrare la sezione MELO e leggere i PDF. La collezione 2027 non è ancora stata sondata.",
    "AUTORIDADE": "UFFICIALE",
    "CADENZA": "settimanale in stagione, da giugno alla fine della raccolta delle varietà tardive; mensile fuori stagione. Mai giornaliera.",
    "DECLARADA_PELO_AUTOR": "eseguibile con adattatore",
    "EXECUTABILITY": "eseguibile con adattatore",
    "EXECUTABILITY_TOKEN": "EXECUTAVEL_COM_ADAPTADOR",
    "FONTE": "Servizio Fitosanitario Emilia-Romagna — bollettini interprovinciali di produzione integrata e biologica (API Plone, JSON, senza chiave).",
    "ID": "ITFC-016",
    "INVALIDA": "quando nel CRIS UNIBO compare un record datato che conclude che l'inoculo rilevante sverna in gemme e borse fiorali.",
    "SCATTA": "quando un bollettino datato porta, nello stesso item di difesa della sezione MELO, un termine di posteriorità alla raccolta, il bersaglio e la sostanza — i tre insieme.",
    "TITULO": "Melo · antracnosi post-raccolta in Emilia-Romagna",
    "TRANSICAO": "nessuna transizione sostenuta",
    "TRANSICAO_AUTORIZADA": "no",
    "TRANSICAO_TOKEN": "SEM_TRANSICAO_SUSTENTADA",
    "VARIAVEL": "presenza o assenza di un'indicazione di trattamento DOPO la raccolta delle varietà precoci contro glomerella / complesso Colletotrichum, nella sezione MELO dei bollettini interprovinciali."
   }
  ]
 },
 "SINAIS_DE_CAMPO": {
  "CARTAO": 28,
  "COM_METODO": 19,
  "LIMITE": "le letture CON METODO viaggiano sempre con il modo in cui sono state lette",
  "VISIVEIS": 47
 }
};
