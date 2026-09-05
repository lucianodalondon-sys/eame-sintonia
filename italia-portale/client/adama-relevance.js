/* GERADO por scripts/it_casa_dados.py — nao editar a mao.
   A LEI vive em scripts/adama_relevance.py e decide-se LA. Este ficheiro
   transporta o veredito para o browser, que nunca o recalcula. */
window.ADAMA_RELEVANCE = {
 "BUILD_ID": "V21-69bf448ac934a6d9",
 "DONO_DA_LEI": "scripts/adama_relevance.py",
 "GERADO_POR": "scripts/it_casa_dados.py + scripts/adama_relevance.py",
 "LEGGE": {
  "APPROVAL_EXPIRY_NAO_E_RISCO": "uma data de expiracao europeia NAO e risco de nao-renovacao. Medido nos 47 factos regulatorios do pacote: EU_STATE=APPROVED e IS_RISK=false em 47/47, e o proprio artefacto declara «APPROVAL EXPIRY IS NOT NON-RENEWAL». Um facto regulatorio NUNCA contribui para a classe A por si so; precisa de facto adicional de risco, que hoje nao existe em registo nenhum.",
  "BASTA_UM_PRODUTO": "um caso e oportunidade se PELO MENOS UM produto fechar a cadeia inteira. Os outros produtos ligados nao sao a prova e nao a estragam — o cartao nomeia qual deles a carrega. Exigir que TODOS fechassem derrubaria OPP_75C37DED9160, onde Lamdex Extra fecha e MAVRIK SMART nao.",
  "CADEIA_EXIGIDA": [
   "PAIS",
   "CULTURA",
   "ALVO/PROBLEMA",
   "PRODUTO ADAMA",
   "RELACAO produto x cultura (pagina de catalogo)",
   "RELACAO produto x alvo (rotulo ministerial)",
   "PROBLEMA OBSERVADO (evidencia que sustenta o sinal ou declara a direccao)",
   "AUTORIZACAO VIVA (registo + estado)"
  ],
  "CLASSES": {
   "A": "PRODUTO ADAMA PROVADO — publica-se como OPORTUNIDADE",
   "B": "PLAUSIVEL, NAO PROVADO — fica em RADAR / A VALIDAR",
   "C": "SEM PRODUTO ADAMA LIGAVEL — fica como SINAL BRUTO",
   "D": "LIGACAO ERRADA — NAO PUBLICAVEL, e um erro a corrigir",
   "E": "NAO SEI — dados insuficientes; nunca sobe"
  },
  "DATASET": "ADAMA-RELEVANCE-LAW-V1",
  "LEI": "todo caso promovido como inteligencia relevante tem de ter ligacao factual e defensavel com pelo menos um produto ADAMA. Sem ela, o caso continua a existir — como radar, sinal ou erro — mas nao como oportunidade.",
  "NAO_ACEITE": [
   "correspondencia lexical",
   "mesmo ingrediente activo",
   "produto parecido",
   "catalogo generico",
   "template",
   "inferencia nao provada",
   "proximidade de data de expiracao europeia",
   "alvo escrito no caso sem fonte que o tenha observado"
  ],
  "PREENCHER_NAO_PROMOVE": "TARGET_FIT vale ON_MINISTERIAL_LABEL em 65 de 65 correspondencias: e uma constante, e nao distingue nada. Se a lei se apoiasse nela, escrever um alvo no caso promovia-o — medido, 10 dos 21 B subiriam sem nada observado. Por isso o problema agronomico exige evidencia que DECIDA um elo (SUPPORTS_SIGNAL ou SUPPORTS_DIRECTION). Com a regra, preencher o alvo nos 21 B promove UM: OPP_00C5B6E15185, que ja traz 4 sinais de campo e 4 evidencias de sinal — esse subiria por ter facto, nao por ter campo cheio.",
  "SO_A_PUBLICA": true
 },
 "PER_CLASSE": {
  "A": 13,
  "B": 21,
  "C": 8,
  "D": 1,
  "E": 0
 },
 "PER_SUPERFICIE": {
  "ERRORE": 1,
  "OPPORTUNITA": 13,
  "RADAR": 21,
  "SEGNALI": 8
 },
 "SOURCE_HEAD": "55c2674",
 "TOTALE": 43,
 "VERDETTI": {
  "OPP_00C5B6E15185": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_169BD86DB324": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "Lamdex® Extra",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_195919127658": {
   "CLASSE": "C",
   "PERCHE": "RELEVANCE_C_NO_LINK",
   "PROVA": null,
   "SUPERFICIE": "SEGNALI"
  },
  "OPP_2BDE8FC566CE": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NAMED_ASSET_NO_RISK",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_314CBAE48A5C": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_3C8C3960CC66": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "Lamdex® Extra",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_48C2731BAFD1": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "MAVRIK SMART",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_4C39CCC05EEB": {
   "CLASSE": "D",
   "PERCHE": "RELEVANCE_D_LINK_FAILS",
   "PROVA": null,
   "SUPERFICIE": "ERRORE"
  },
  "OPP_568684853264": {
   "CLASSE": "C",
   "PERCHE": "RELEVANCE_C_NO_LINK",
   "PROVA": null,
   "SUPERFICIE": "SEGNALI"
  },
  "OPP_576D71D702F0": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_5D03565DB4C3": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_5F31A63F844D": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "BANJO",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_6B7D9CC9188B": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_6BA350CA1538": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_6E18A133EE14": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NAMED_ASSET_NO_RISK",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_75C37DED9160": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "MAVRIK SMART",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_81C053E9DCD3": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "Lamdex® Extra",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_84D116CA45B1": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_886307860F79": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_88CC35C57C7B": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_8E210567B01F": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_8EA4F5C0D3F4": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_9AB924CA36C8": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_9C600748BB1B": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "Lamdex® Extra",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_AA1A1FF77C8D": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_B19061BA418B": {
   "CLASSE": "C",
   "PERCHE": "RELEVANCE_C_NO_LINK",
   "PROVA": null,
   "SUPERFICIE": "SEGNALI"
  },
  "OPP_B362181E3A45": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_B9206ACFC797": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NAMED_ASSET_NO_RISK",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_BCD174C535AC": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_C1735138E362": {
   "CLASSE": "C",
   "PERCHE": "RELEVANCE_C_NO_LINK",
   "PROVA": null,
   "SUPERFICIE": "SEGNALI"
  },
  "OPP_C5F7888EC524": {
   "CLASSE": "C",
   "PERCHE": "RELEVANCE_C_NO_LINK",
   "PROVA": null,
   "SUPERFICIE": "SEGNALI"
  },
  "OPP_D11664591168": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "MAVRIK SMART",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_D9B21D005CC3": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "BANJO",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_DF0C3648893A": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "BANJO",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_E138ECDFD7D2": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "BANJO",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_E1A1D73F07BF": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_E6200AA0FA63": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NAMED_ASSET_NO_RISK",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_EA2AE1EFB775": {
   "CLASSE": "C",
   "PERCHE": "RELEVANCE_C_NO_LINK",
   "PROVA": null,
   "SUPERFICIE": "SEGNALI"
  },
  "OPP_EE1E2A3869EE": {
   "CLASSE": "C",
   "PERCHE": "RELEVANCE_C_NO_LINK",
   "PROVA": null,
   "SUPERFICIE": "SEGNALI"
  },
  "OPP_F383CF46E5BF": {
   "CLASSE": "B",
   "PERCHE": "RELEVANCE_B_NO_TARGET",
   "PROVA": null,
   "SUPERFICIE": "RADAR"
  },
  "OPP_F6EEF5B32F65": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "Lamdex® Extra",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_F8106D5E1767": {
   "CLASSE": "A",
   "PERCHE": "RELEVANCE_A_PROVEN",
   "PROVA": "BANJO",
   "SUPERFICIE": "OPPORTUNITA"
  },
  "OPP_FBA64D2CA10D": {
   "CLASSE": "C",
   "PERCHE": "RELEVANCE_C_NO_LINK",
   "PROVA": null,
   "SUPERFICIE": "SEGNALI"
  }
 }
};
