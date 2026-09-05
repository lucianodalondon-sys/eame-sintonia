# PORTFOLIO ADAMA ITÁLIA — o que o registro oficial mostra

**Fonte:** IT-T4-001 · Ministero della Salute, Banca dati dei prodotti fitosanitari
**Arquivo:** `PROD_FTS_6_20260831.csv` (versão do dado 20260831) · **Coletado em:** 2026-09-02
**Evidência:** `data/samples/IT-T4-001/IT-T4-001-adama-portfolio.json` · **Coletor:** `scripts/adama_italia.py`
**Camada:** REGISTERED PRESENCE — e só ela.

---

## Por que não veio do site da ADAMA

`adama.com/italia/it` devolveu **403 (Akamai, "Access Denied")** em toda rota de saída testada:
curl, navegador Chromium real com locale `it-IT`, e a rota de fetch da ferramenta.
O bloqueio pega até `robots.txt` e `sitemap.xml` — ou seja, é **bloqueio de borda por IP de datacenter**,
não geo-bloqueio de conteúdo. Uma VPN italiana na máquina do usuário não muda a saída deste ambiente.
O RADAR-ADAMA-EAME já havia registrado o mesmo 403 em duas rotas distintas: é um bloqueio estável, não um incidente.

Portanto **portfólio, substâncias ativas e datas não vêm do site da empresa** — vêm do registro que a própria
empresa é obrigada a alimentar por lei, que é mais completo e mais auditável do que a vitrine comercial.

---

## O que existe

| | |
|---|---|
| Linhas no registro italiano | 17.695 |
| Registros do grupo ADAMA (histórico completo, desde a origem) | 602 |
| **Autorizações vivas hoje** | **163** |
| Vencendo nos próximos 180 dias | 64 |

### Vivos por titular

| Titular da autorização | Vivos | Histórico |
|---|---:|---:|
| ADAMA ITALIA S.R.L. | 85 | 240 |
| ADAMA AGAN LTD | 35 | 106 |
| ADAMA MAKHTESHIM LTD | 26 | 168 |
| ADAMA DEUTSCHLAND GMBH | 17 | 69 |

> O portfólio italiano **não está todo sob a ADAMA ITALIA S.R.L.**: 78 das 163 autorizações vivas
> estão sob entidades do grupo sediadas fora da Itália (AGAN e MAKHTESHIM em Israel, DEUTSCHLAND na Alemanha).
> Quem contar só "ADAMA ITALIA" perde quase metade do portfólio.

### Estado administrativo (histórico completo)

| Estado | Registros |
|---|---:|
| Revocato | 425 |
| Ri-registrato | 67 |
| Autorizzato | 60 |
| Autorizzato con procedura zonale | 20 |
| Scaduto | 14 |
| Autorizzato in regime di Riconoscimento Reciproco | 5 |
| Autorizzato Art. 34 Reg. 1107/2009 | 5 |
| Autorizzato Art. 10 D.P.R. 290/2001 | 4 |
| Ri-registrato (Air 1 Fase 1) | 1 |
| Rinnovato Art. 43 Reg. 1107/2009 | 1 |

---

## Substâncias ativas vivas — as 20 mais presentes

| Substância (ou mistura) | Produtos vivos |
|---|---:|
| GLYPHOSATE | 11 |
| PENDIMETHALIN | 10 |
| CLODINAFOP + CLOQUINTOCET MEXYL | 10 |
| FOLPET | 10 |
| QUIZALOFOP-P-ETHYL | 8 |
| METAMITRON | 7 |
| CYMOXANIL | 6 |
| BIFENOX | 6 |
| TAU-FLUVALINATE | 6 |
| PROPAQUIZAFOP | 5 |
| PIRIMICARB | 5 |
| LAMBDA-CYHALOTHRIN | 5 |
| FOSETYL-ALUMINIUM | 5 |
| IMAZAMOX | 4 |
| BUPIRIMATE | 4 |
| FLUAZINAM | 3 |
| AZOXYSTROBIN + TEBUCONAZOLE | 3 |
| CAPTAN | 3 |
| TRIBENURON | 3 |
| NICOSULFURON | 3 |

55 combinações distintas de substância ativa entre os 163 produtos vivos.

---

## Calendário de vencimento — próximos 180 dias

Este é o dado que a Itália dá e a França não dá: **data de vencimento por autorização**.

| Produto | Nº registro | Vencimento | Dias |
|---|---|---|---:|
| CONTATTO 320 | 009790 | 30/09/2026 | 28 |
| CONTATTO DOUBLE SC | 011734 | 30/09/2026 | 28 |
| SEEDRON | 016152 | 30/09/2026 | 28 |
| APHOX | 014091 | 31/10/2026 | 59 |
| APHOX 50 | 017340 | 31/10/2026 | 59 |
| CLORMET | 014380 | 31/10/2026 | 59 |
| MOMENTUM | 015235 | 31/10/2026 | 59 |
| MOMENTUM PFNPE | 018244 | 31/10/2026 | 59 |
| MOVER | 017335 | 31/10/2026 | 59 |
| PIRIMOR 17,5 | 007876 | 31/10/2026 | 59 |
| PIRIMOR 50 | 004701 | 31/10/2026 | 59 |
| RIMENSIS | 017898 | 31/10/2026 | 59 |
| SULTAN | 011526 | 31/10/2026 | 59 |
| VANGUARD | 017337 | 31/10/2026 | 59 |
| XINTECH 50 | 017409 | 31/10/2026 | 59 |
| APYZA 500 WG | 018165 | 30/11/2026 | 89 |
| APYZA WG | 018156 | 30/11/2026 | 89 |
| BREVIS | 016084 | 30/11/2026 | 89 |
| GOLD-BEET | 008599 | 30/11/2026 | 89 |
| GOLDBEET SUPER | 017983 | 30/11/2026 | 89 |
| GOLTIX | 002732 | 30/11/2026 | 89 |
| GOLTIX 700 SC | 010569 | 30/11/2026 | 89 |
| GOLTIX BETA | 018813 | 30/11/2026 | 89 |
| GOLTIX SUPER | 017580 | 30/11/2026 | 89 |
| GOLTIX TOP | 018814 | 30/11/2026 | 89 |
| NORTIM | 007603 | 30/11/2026 | 89 |
| ACTIGAN EKO | 017660 | 15/01/2027 | 135 |
| ACTIGAN ME | 017659 | 15/01/2027 | 135 |
| ACTIVUS 40 SC | 016823 | 15/01/2027 | 135 |
| ACTIVUS ME | 017116 | 15/01/2027 | 135 |
| ANTHEM EKO | 017094 | 15/01/2027 | 135 |
| AVANA | 017123 | 15/01/2027 | 135 |
| CINDER | 016697 | 15/01/2027 | 135 |
| DOMITREL 400 CS | 017398 | 15/01/2027 | 135 |
| PRESTIGAN EKO | 017661 | 15/01/2027 | 135 |
| PRESTIGAN ME | 017658 | 15/01/2027 | 135 |
| EVURE PRO | 014210 | 31/01/2027 | 151 |
| KLARTAN 20 EW | 007555 | 31/01/2027 | 151 |
| KLARTAN SMART | 012023 | 31/01/2027 | 151 |
| MAVRIK EW | 014190 | 31/01/2027 | 151 |
| MAVRIK JET | 017968 | 31/01/2027 | 151 |
| MAVRIK SMART | 009800 | 31/01/2027 | 151 |
| NIMROD | 002983 | 31/01/2027 | 151 |
| NIMROD 250 EW | 013771 | 31/01/2027 | 151 |
| TAU AL 240 EW | 007864 | 31/01/2027 | 151 |
| TRINEX 250 EW | 014074 | 31/01/2027 | 151 |
| VERBUM EW | 013405 | 31/01/2027 | 151 |
| VINETO | 015740 | 31/01/2027 | 151 |
| CLEAVE | 016475 | 15/02/2027 | 166 |
| MORAINE | 018101 | 15/02/2027 | 166 |
| TOMIGAN | 016312 | 15/02/2027 | 166 |
| AGIL | 009005 | 28/02/2027 | 179 |
| APACHE | 013876 | 28/02/2027 | 179 |
| ERBY 5 EC | 012279 | 28/02/2027 | 179 |
| FALCON MK | 015253 | 28/02/2027 | 179 |
| HANUKYS | 017332 | 28/02/2027 | 179 |
| LEOPARD 5 EC | 011243 | 28/02/2027 | 179 |
| LIGA | 017206 | 28/02/2027 | 179 |
| LION 5 EC | 014375 | 28/02/2027 | 179 |
| MAGIO' | 013299 | 28/02/2027 | 179 |
| MANAGER | 011789 | 28/02/2027 | 179 |
| QUIZA 5 EC | 013711 | 28/02/2027 | 179 |
| SHOGUN | 011660 | 28/02/2027 | 179 |
| ZETROLA | 017115 | 28/02/2027 | 179 |

---

## Portfólio vivo completo

| Produto | Nº registro | Titular | Formulação | Substâncias ativas | Teor /100 g | Vencimento |
|---|---|---|---|---|---|---|
| **ACTIGAN DFF** | 017703 | AGAN LTD | Sospensione Concentrata | PENDIMETHALIN|DIFLUFENICAN | 35.6 g|3.6 g | 31/08/2027 |
| **ACTIGAN EKO** | 017660 | ITALIA S.R.L. | Sospensione Concentrata | PENDIMETHALIN | 40.0 g | 15/01/2027 |
| **ACTIGAN ME** | 017659 | AGAN LTD | Concentrato Fluido Miscibile In Oli | PENDIMETHALIN | 34.8 g | 15/01/2027 |
| **ACTIVUS 40 SC** | 016823 | ITALIA S.R.L. | Sospensione Concentrata | PENDIMETHALIN | 40.0 g | 15/01/2027 |
| **ACTIVUS ME** | 017116 | AGAN LTD | Sospensione Di Capsule | PENDIMETHALIN | 34.8 g | 15/01/2027 |
| **AGHARTA** | 017432 | MAKHTESHIM LTD | Sospensione Concentrata | FLUAZINAM | 40.2 g | 30/11/2027 |
| **AGIL** | 009005 | ITALIA S.R.L. | Concentrato Emulsionabile | PROPAQUIZAFOP | 9.6 g | 28/02/2027 |
| **AKTIVIR** | 017930 | DEUTSCHLAND GMBH | Concentrato Solubile | GLYPHOSATE | 30.8 g | 15/12/2034 |
| **ANTARKTIS** | 014093 | AGAN LTD | Sospensione Concentrata | BIFENOX|FLORASULAM | 40.8 g|0.5 g | 31/12/2031 |
| **ANTERLEX** | 017688 | ITALIA S.R.L. | Granulare Idrodispersibile | CYMOXANIL | 45.0 g | 15/08/2026 |
| **ANTHEM EKO** | 017094 | ITALIA S.R.L. | Sospensione Concentrata | PENDIMETHALIN | 40.0 g | 15/01/2027 |
| **APACHE** | 013876 | AGAN LTD | Concentrato Emulsionabile | QUIZALOFOP-P-ETHYL | 5.4 g | 28/02/2027 |
| **APHOX** | 014091 | ITALIA S.R.L. | Granulare Idrodispersibile | PIRIMICARB | 17.5 g | 31/10/2026 |
| **APHOX 50** | 017340 | ITALIA S.R.L. | Granulare Idrodispersibile | PIRIMICARB | 50.0 g | 31/10/2026 |
| **APYZA 500 WG** | 018165 | ITALIA S.R.L. | Granulare Idrodispersibile | FLONICAMID (IKI-220) | 50.0 g | 30/11/2026 |
| **APYZA WG** | 018156 | ITALIA S.R.L. | Granulare Idrodispersibile | FLONICAMID (IKI-220) | 50.0 g | 30/11/2026 |
| **ARRODIM** | 018111 | ITALIA S.R.L. | Concentrato Emulsionabile | CLETHODIM | 25.3 g | 31/08/2026 |
| **AVANA** | 017123 | ITALIA S.R.L. | Sospensione Concentrata | PENDIMETHALIN | 40.0 g | 15/01/2027 |
| **AVASTEL** | 018089 | ITALIA S.R.L. | Concentrato Emulsionabile | PROTHIOCONAZOLE|FLUXAPYROXAD | 13.9 g|6.4 g | 31/03/2028 |
| **BADGER 45% WG** | 015629 | ITALIA S.R.L. | Granulare Idrodispersibile | CYMOXANIL | 45.0 g | 15/08/2026 |
| **BANJO** | 013905 | MAKHTESHIM LTD | Sospensione Concentrata | FLUAZINAM | 40.2 g | 30/11/2027 |
| **BIFENIX** | 017662 | DEUTSCHLAND GMBH | Sospensione Concentrata | BIFENOX | 40.6 g | 31/03/2027 |
| **BLAISE ULTRA** | 017358 | ITALIA S.R.L. | Sospensione Concentrata | AZOXYSTROBIN|TEBUCONAZOLE | 11.0 g|18.4 g | 15/08/2026 |
| **BREVIS** | 016084 | ITALIA S.R.L. | Granulare Solubile In Acqua | METAMITRON | 15.0 g | 30/11/2026 |
| **CAPTHENE 80 WDG** | 011500 | MAKHTESHIM LTD | Granulare Idrodispersibile | CAPTAN | 80.0 g | 31/10/2040 |
| **CARSON 45% WG** | 015630 | ITALIA S.R.L. | Granulare Idrodispersibile | CYMOXANIL | 45.0 g | 15/08/2026 |
| **CELIO** | 014728 | ITALIA S.R.L. | Concentrato Emulsionabile | CLODINAFOP|CLOQUINTOCET MEXYL | 22.1 g|5.6 g | 31/07/2027 |
| **CELIO 80 EC** | 014694 | ITALIA S.R.L. | Concentrato Emulsionabile | CLODINAFOP|CLOQUINTOCET MEXYL | 8.1 g|2.0 g | 31/07/2027 |
| **CHASER-S** | 017318 | AGAN LTD | Sospensione Concentrata | TERBUTHYLAZINE|SULCOTRIONE | 28.4 g|15.0 g | 31/05/2027 |
| **CINDER** | 016697 | AGAN LTD | Concentrato Fluido Miscibile In Oli | PENDIMETHALIN | 34.8 g | 15/01/2027 |
| **CLEAVE** | 016475 | ITALIA S.R.L. | Sospensione-Emulsione | FLUROXYPYR|FLORASULAM | 10.0 g|0.3 g | 15/02/2027 |
| **CLORMET** | 014380 | AGAN LTD | Sospensione Concentrata | METAZACHLOR | 44.3 g | 31/10/2026 |
| **CONTATTO 320** | 009790 | DEUTSCHLAND GMBH | Sospensione Concentrata | PHENMEDIPHAM | 29.2 g | 30/09/2026 |
| **CONTATTO DOUBLE SC** | 011734 | DEUTSCHLAND GMBH | Sospensione Concentrata | PHENMEDIPHAM | 29.2 g | 30/09/2026 |
| **COSAYR 200 SC** | 018561 | ITALIA S.R.L. | Sospensione Concentrata | CHLORANTRANILIPROLE | 18.5 g | 31/05/2027 |
| **CUSTODIA ULTRA** | 015232 | ITALIA S.R.L. | Sospensione Concentrata | AZOXYSTROBIN|TEBUCONAZOLE | 11.0 g|18.4 g | 15/08/2026 |
| **DAUPHIN 45** | 013899 | ITALIA S.R.L. | Granulare Idrodispersibile | CYMOXANIL | 45.0 g | 15/08/2026 |
| **DAVAI** | 017209 | AGAN LTD | Concentrato Solubile | IMAZAMOX | 7.6 g | 30/06/2027 |
| **DICURAN PLUS** | 016218 | ITALIA S.R.L. | Sospensione Concentrata | CHLOROTOLURON|DIFLUFENICAN | 40.0 g|2.5 g | 31/08/2027 |
| **DIODE** | 018694 | ITALIA S.R.L. | Sospensione Concentrata | MESOTRIONE | 9.4 g | 31/05/2032 |
| **DOMITREL 400 CS** | 017398 | AGAN LTD | Sospensione Di Capsule | PENDIMETHALIN | 34.8 g | 15/01/2027 |
| **DURAVIS** | 015275 | ITALIA S.R.L. | Granulare Idrodispersibile | LAMBDA-CYHALOTHRIN | 2.5 g | 31/08/2026 |
| **EARLEX** | 017655 | AGAN LTD | Concentrato Solubile | IMAZAMOX | 7.6 g | 30/06/2027 |
| **EDAPTIS** | 018176 | ITALIA S.R.L. | Olio Dispersibile | MEFENPYR DIETHYL|MESOSULFURON-METHYL|PINOXADEN | 3.6 g|6.2 g | 31/12/2029 |
| **EKO OIL SPRAY** | 012573 | MAKHTESHIM LTD | Olio Dispersibile | PARAFFIN OIL/(CAS 97862-82-3) | 98.8 g | 10/03/2027 |
| **ELEGANT 2FD** | 016553 | AGAN LTD | Sospensione-Emulsione | FLORASULAM|2,4-D | 0.6 g|42.3 g | 31/12/2031 |
| **ELTIRA** | 017687 | ITALIA S.R.L. | Granulare Idrodispersibile | LAMBDA-CYHALOTHRIN | 2.5 g | 31/08/2026 |
| **EMBRACE** | 015315 | MAKHTESHIM LTD | Sospensione Concentrata | FLUAZINAM | 40.2 g | 30/11/2027 |
| **ERBY 5 EC** | 012279 | AGAN LTD | Concentrato Emulsionabile | QUIZALOFOP-P-ETHYL | 5.4 g | 28/02/2027 |
| **ETHOSAT SC** | 018202 | AGAN LTD | Sospensione Concentrata | ETHOFUMESATE | 44.6 g | 31/10/2032 |
| **EVURE PRO** | 014210 | ITALIA S.R.L. | Concentrato Emulsionabile | TAU-FLUVALINATE | 21.4 g | 31/01/2027 |
| **FALCON MK** | 015253 | ITALIA S.R.L. | Concentrato Emulsionabile | PROPAQUIZAFOP | 9.6 g | 28/02/2027 |
| **FINESSOX** | 008401 | MAKHTESHIM LTD | Sospensione Concentrata | FOLPET | 39.7 g | 31/10/2040 |
| **FLOVINE** | 017111 | ITALIA S.R.L. | Granulare Idrodispersibile | FOLPET | 80.0 g | 31/10/2040 |
| **FOLPAN 80 WDG** | 008601 | ITALIA S.R.L. | Granulare Idrodispersibile | FOLPET | 80.0 g | 31/10/2040 |
| **FOLPAN ENERGY** | 016749 | MAKHTESHIM LTD | Sospensione Concentrata | FOLPET|POTASSIUM PHOSPHONATES (FORMERLY POTASSIUM PHOSPHITE) | 19.7 g|44.1 g | 31/10/2040 |
| **FOLPAN GOLD** | 012878 | ITALIA S.R.L. | Granulare Idrodispersibile | FOLPET|METALAXYL-M | 40.0 g|4.9 g | 31/10/2040 |
| **FOLPAN SC** | 010587 | MAKHTESHIM LTD | Sospensione Concentrata | FOLPET | 39.7 g | 31/10/2040 |
| **FOLVIT 80 WDG** | 013012 | ITALIA S.R.L. | Granulare Idrodispersibile | FOLPET | 80.0 g | 31/10/2040 |
| **FORZA** | 013560 | ITALIA S.R.L. | Granulare Idrodispersibile | LAMBDA-CYHALOTHRIN | 2.5 g | 31/08/2026 |
| **FOX** | 012060 | DEUTSCHLAND GMBH | Sospensione Concentrata | BIFENOX | 40.6 g | 31/03/2027 |
| **FOXPRO** | 017319 | DEUTSCHLAND GMBH | Sospensione Concentrata | BIFENOX | 40.6 g | 31/03/2027 |
| **GLIPHOGAN TOP CL** | 015096 | DEUTSCHLAND GMBH | Concentrato Emulsionabile | GLYPHOSATE | 32.4 g | 15/12/2034 |
| **GLIPHOGAN TOP CL PFNPE** | 018270 | DEUTSCHLAND GMBH | Concentrato Solubile | GLYPHOSATE | 30.8 % | 15/12/2034 |
| **GOLD-BEET** | 008599 | ITALIA S.R.L. | Granulare Solubile In Acqua | METAMITRON | 70.0 g | 30/11/2026 |
| **GOLDBEET SUPER** | 017983 | AGAN LTD | Sospensione Concentrata | ETHOFUMESATE|METAMITRON | 13.2 g|30.7 g | 30/11/2026 |
| **GOLTIX** | 002732 | ITALIA S.R.L. | Granulare Idrodispersibile | METAMITRON | 70.0 g | 30/11/2026 |
| **GOLTIX 700 SC** | 010569 | ITALIA S.R.L. | Sospensione Concentrata | METAMITRON | 57.9 g | 30/11/2026 |
| **GOLTIX BETA** | 018813 | ITALIA S.R.L. | Sospensione Concentrata | METAMITRON | 58.3 g | 30/11/2026 |
| **GOLTIX SUPER** | 017580 | AGAN LTD | Sospensione Concentrata | ETHOFUMESATE|METAMITRON | 13.2 g|30.7 g | 30/11/2026 |
| **GOLTIX TOP** | 018814 | ITALIA S.R.L. | Sospensione Concentrata | METAMITRON | 57.9 g | 30/11/2026 |
| **HANUKYS** | 017332 | AGAN LTD | Concentrato Emulsionabile | QUIZALOFOP-P-ETHYL | 5.4 g | 28/02/2027 |
| **HAWK** | 015316 | ITALIA S.R.L. | Concentrato Emulsionabile | CLODINAFOP|CLOQUINTOCET MEXYL | 22.1 g|5.6 g | 31/07/2027 |
| **HERBITOTAL CL** | 016387 | DEUTSCHLAND GMBH | Concentrato Solubile | GLYPHOSATE | 30.8 g | 15/12/2034 |
| **HERBITOTAL CL PFNPE** | 018271 | DEUTSCHLAND GMBH | Concentrato Solubile | GLYPHOSATE | 30.8 % | 15/12/2034 |
| **HIGHCARD** | 017995 | AGAN LTD | Concentrato Emulsionabile | ISOXADIFEN ETHYL|QUIZALOFOP-P-ETHYL | 7.1 g|10.0 g | 28/02/2028 |
| **KIKKO 50 WG** | 017664 | ITALIA S.R.L. | Granulare Idrodispersibile | TRIBENURON | 47.5 g | 31/01/2035 |
| **KLARTAN 20 EW** | 007555 | ITALIA S.R.L. | Emulsione Olio/Acqua | TAU-FLUVALINATE | 21.4 g | 31/01/2027 |
| **KLARTAN SMART** | 012023 | ITALIA S.R.L. | Concentrato Emulsionabile | TAU-FLUVALINATE | 21.4 g | 31/01/2027 |
| **KOJAMI** | 019095 | ITALIA S.R.L. | Sospensione Concentrata | AZOXYSTROBIN|PROTHIOCONAZOLE | 17.7 g|13.3 g | 31/05/2027 |
| **KORAL 50 WG** | 017663 | ITALIA S.R.L. | Granulare Idrodispersibile | TRIBENURON | 47.5 g | 31/01/2035 |
| **KORAVERT** | 017929 | DEUTSCHLAND GMBH | Concentrato Solubile | GLYPHOSATE | 30.8 g | 15/12/2034 |
| **LAMDEX EXTRA** | 008259 | ITALIA S.R.L. | Granulare Idrodispersibile | LAMBDA-CYHALOTHRIN | 2.5 g | 31/08/2026 |
| **LEBRON 0.5 G** | 008189 | ITALIA S.R.L. | Microgranulare | TEFLUTHRIN | 0.5 g | 31/05/2027 |
| **LEOPARD 5 EC** | 011243 | AGAN LTD | Concentrato Emulsionabile | QUIZALOFOP-P-ETHYL | 5.4 g | 28/02/2027 |
| **LIGA** | 017206 | ITALIA S.R.L. | Concentrato Emulsionabile | PROPAQUIZAFOP | 9.6 g | 28/02/2027 |
| **LION 5 EC** | 014375 | AGAN LTD | Concentrato Emulsionabile | QUIZALOFOP-P-ETHYL | 5.4 g | 28/02/2027 |
| **LUMA-KL** | 013402 | ITALIA S.R.L. | Esca Granulare | METALDEHYDE | 5.0 g | 31/08/2026 |
| **MAGANIC** | 017955 | MAKHTESHIM LTD | Concentrato Emulsionabile | DIFENOCONAZOLE|PROTHIOCONAZOLE | 11.5 g|16.1 g | 31/01/2028 |
| **MAGIO'** | 013299 | AGAN LTD | Concentrato Emulsionabile | QUIZALOFOP-P-ETHYL | 5.0 g | 28/02/2027 |
| **MAGNATE 500 EC** | 009783 | MAKHTESHIM LTD | Concentrato Emulsionabile | IMAZALIL (AKA ENILCONAZOLE) | 45.2 g | 31/05/2027 |
| **MAKE UP 80 WDG** | 012156 | ITALIA S.R.L. | Granulare Idrodispersibile | CAPTAN | 80.0 g | 31/10/2040 |
| **MAKURI** | 015847 | ITALIA S.R.L. | Concentrato Emulsionabile | CLODINAFOP|CLOQUINTOCET MEXYL | 8.0 g|1.9 g | 31/07/2027 |
| **MANAGER** | 011789 | AGAN LTD | Concentrato Emulsionabile | QUIZALOFOP-P-ETHYL | 5.4 g | 28/02/2027 |
| **MAVRIK EW** | 014190 | ITALIA S.R.L. | Emulsione Olio/Acqua | TAU-FLUVALINATE | 21.4 g | 31/01/2027 |
| **MAVRIK JET** | 017968 | ITALIA S.R.L. | Emulsione Olio/Acqua | TAU-FLUVALINATE|PIRIMICARB | 1.7 %|4.8 % | 31/01/2027 |
| **MAVRIK SMART** | 009800 | ITALIA S.R.L. | Emulsione Olio/Acqua | TAU-FLUVALINATE | 21.4 g | 31/01/2027 |
| **MAXENTIS** | 018067 | ITALIA S.R.L. | Concentrato Solubile | AZOXYSTROBIN|PROTHIOCONAZOLE | 17.7 g|13.3 g | 31/05/2027 |
| **MERPAN 80 WDG** | 008102 | ITALIA S.R.L. | Granulare Idrodispersibile | CAPTAN | 80.0 g | 31/10/2040 |
| **MEZAYO** | 018644 | ITALIA S.R.L. | Olio Dispersibile | MESOSULFURON-METHYL|PINOXADEN | 1.2 g|6.2 g | 31/12/2029 |
| **MIRADOR TURBO** | 017824 | ITALIA S.R.L. | Sospensione Concentrata | AZOXYSTROBIN|TEBUCONAZOLE | 11.3 g|18.4 g | 31/05/2027 |
| **MOMENTUM** | 015235 | MAKHTESHIM LTD | Granulare Idrodispersibile | FOSETYL-ALUMINIUM | 80.0 g | 31/10/2026 |
| **MOMENTUM PFNPE** | 018244 | MAKHTESHIM LTD | Granulare Idrodispersibile | FOSETYL-ALUMINIUM | 80.0 % | 31/10/2026 |
| **MORAINE** | 018101 | AGAN LTD | Concentrato Emulsionabile | FLUROXYPYR | 29.2 g | 15/02/2027 |
| **MOVER** | 017335 | MAKHTESHIM LTD | Granulare Idrodispersibile | FOSETYL-ALUMINIUM | 80.0 g | 31/10/2026 |
| **MOXYL MK** | 017689 | ITALIA S.R.L. | Granulare Idrodispersibile | CYMOXANIL | 45.0 g | 15/08/2026 |
| **NERASTAL** | 018545 | ITALIA S.R.L. | Sospensione Concentrata | BIFENOX | 40.7 g | 31/03/2028 |
| **NICAMACK V.O.** | 015182 | AGAN LTD | Olio Dispersibile | NICOSULFURON | 4.2 g | 31/03/2027 |
| **NICOGAN V.O.** | 013242 | AGAN LTD | Olio Dispersibile | NICOSULFURON | 4.2 g | 31/03/2027 |
| **NIMROD** | 002983 | MAKHTESHIM LTD | Emulsione Olio/Acqua | BUPIRIMATE | 23.8 g | 31/01/2027 |
| **NIMROD 250 EW** | 013771 | MAKHTESHIM LTD | Emulsione Olio/Acqua | BUPIRIMATE | 23.8 g | 31/01/2027 |
| **NINJA** | 013590 | ITALIA S.R.L. | Granulare | LAMBDA-CYHALOTHRIN | 2.5 g | 31/08/2026 |
| **NORTIM** | 007603 | ITALIA S.R.L. | Polvere Bagnabile | METAMITRON | - | 30/11/2026 |
| **OLIONET** | 014386 | MAKHTESHIM LTD | Emulsione Olio/Acqua | PARAFFIN OIL/(CAS 97862-82-3) | 98.8 g | 10/03/2027 |
| **PARIFOL** | 011501 | MAKHTESHIM LTD | Granulare Idrodispersibile | FOLPET | 80.0 g | 31/10/2040 |
| **PIRIMOR 17,5** | 007876 | ITALIA S.R.L. | Granulare Idrodispersibile | PIRIMICARB | 17.5 g | 31/10/2026 |
| **PIRIMOR 50** | 004701 | ITALIA S.R.L. | Granulare Idrodispersibile | PIRIMICARB | 50.0 g | 31/10/2026 |
| **POSTSCRIPT 80** | 017585 | AGAN LTD | Concentrato Solubile | IMAZAMOX | 7.6 g | 30/06/2027 |
| **POSTSCRIPT 80 XL** | 017868 | AGAN LTD | Concentrato Solubile | IMAZAMOX | 7.6 g | 30/06/2027 |
| **POWERFILM** | 017852 | ITALIA S.R.L. | Liquido (Senza Diluizione) | PLANT OILS / RAPE SEED OIL | 47.5 g | 31/10/2041 |
| **PRESSING 500** | 011794 | AGAN LTD | Sospensione Concentrata | DIFLUFENICAN | 42.0 g | 31/08/2027 |
| **PRESTIGAN EKO** | 017661 | ITALIA S.R.L. | Sospensione Concentrata | PENDIMETHALIN | 40.0 g | 15/01/2027 |
| **PRESTIGAN ME** | 017658 | AGAN LTD | Concentrato Fluido Miscibile In Oli | PENDIMETHALIN | 34.8 g | 15/01/2027 |
| **PYXIDES WG** | 015909 | ITALIA S.R.L. | Granulare Idrodispersibile | DICAMBA|NICOSULFURON|MESOTRIONE | 31.3 g|10.0 g|15.0 g | 31/05/2033 |
| **QUIZA 5 EC** | 013711 | AGAN LTD | Concentrato Emulsionabile | QUIZALOFOP-P-ETHYL | 5.4 g | 28/02/2027 |
| **RAVENAS** | 013807 | ITALIA S.R.L. | Concentrato Emulsionabile | CLODINAFOP|CLOQUINTOCET MEXYL | 22.1 g|5.6 g | 31/07/2027 |
| **RENDER V.O.** | 015183 | AGAN LTD | Olio Dispersibile | NICOSULFURON | 4.2 g | 31/03/2027 |
| **RIMENSIS** | 017898 | MAKHTESHIM LTD | Granulare Idrodispersibile | FOSETYL-ALUMINIUM | 80.0 g | 31/10/2026 |
| **SCHERMO 0.5 G** | 014479 | ITALIA S.R.L. | Granulare | TEFLUTHRIN | 0.5 g | 31/05/2027 |
| **SEEDRON** | 016152 | MAKHTESHIM LTD | Sospensione Concentrata Per Concia | FLUDIOXONIL|TEBUCONAZOLE | 4.6 g|0.9 g | 30/09/2026 |
| **SESTO GOLD** | 015317 | ITALIA S.R.L. | Granulare Idrodispersibile | FOLPET|METALAXYL-M | 40.0 g|4.9 g | 31/10/2040 |
| **SHAMAL MK PLUS CL** | 015405 | DEUTSCHLAND GMBH | Concentrato Solubile | GLYPHOSATE | 30.4 g | 15/12/2034 |
| **SHAMAL MK PLUS CL PFNPE** | 018277 | DEUTSCHLAND GMBH | Concentrato Solubile | GLYPHOSATE | 30.8 % | 15/12/2034 |
| **SHOGUN** | 011660 | ITALIA S.R.L. | Concentrato Emulsionabile | PROPAQUIZAFOP | 9.6 g | 28/02/2027 |
| **SOLOFOL** | 013585 | MAKHTESHIM LTD | Granulare Idrodispersibile | FOLPET | 80.0 g | 31/10/2040 |
| **SOLOFOL AP** | 014862 | MAKHTESHIM LTD | Granulare Idrodispersibile | FOLPET | 80.0 g | 31/10/2040 |
| **SONAVIO** | 018072 | ITALIA S.R.L. | Sospensione Concentrata | BIFENOX | 40.7 g | 31/03/2028 |
| **SORATEL** | 018175 | ITALIA S.R.L. | Concentrato Emulsionabile | PROTHIOCONAZOLE | 23.2 g | 31/03/2027 |
| **SPYRALE** | 009757 | ITALIA S.R.L. | Concentrato Emulsionabile | DIFENOCONAZOLE|FENPROPIDIN | 10.1 g|37.8 g | 31/01/2028 |
| **STAVENTO** | 017752 | MAKHTESHIM LTD | Sospensione Concentrata | FOLPET | 39.7 g | 31/10/2040 |
| **STOPPER P** | 015229 | AGAN LTD | Sospensione Concentrata | PENDIMETHALIN|DIFLUFENICAN | 35.6 g|3.6 g | 31/08/2027 |
| **SULCOTREK** | 010585 | AGAN LTD | Sospensione Concentrata | TERBUTHYLAZINE|SULCOTRIONE | 28.4 g|15.0 g | 31/05/2027 |
| **SULTAN** | 011526 | AGAN LTD | Sospensione Concentrata | METAZACHLOR | 44.3 g | 31/10/2026 |
| **TAIFUN  MK CL PFNPE** | 018279 | DEUTSCHLAND GMBH | Concentrato Solubile | GLYPHOSATE | 30.8 % | 15/12/2034 |
| **TAIFUN JARDIN** | 015592 | DEUTSCHLAND GMBH | Concentrato Emulsionabile | GLYPHOSATE | 30.8 g | 15/12/2034 |
| **TAIFUN MK CL** | 015401 | DEUTSCHLAND GMBH | Concentrato Solubile | GLYPHOSATE | 30.8 g | 15/12/2034 |
| **TAU AL 240 EW** | 007864 | ITALIA S.R.L. | Polvere Bagnabile | TAU-FLUVALINATE | 21.4 g | 31/01/2027 |
| **TOMIGAN** | 016312 | AGAN LTD | Concentrato Emulsionabile | FLUROXYPYR | 29.2 g | 15/02/2027 |
| **TOPIK 240 EC** | 008929 | ITALIA S.R.L. | Concentrato Emulsionabile | CLODINAFOP|CLOQUINTOCET MEXYL | 22.8 g|5.6 g | 31/07/2027 |
| **TOPIK 80 EC** | 010063 | ITALIA S.R.L. | Concentrato Emulsionabile | CLODINAFOP|CLOQUINTOCET MEXYL | 8.1 g|2.0 g | 31/07/2027 |
| **TRACE** | 013736 | ITALIA S.R.L. | Concentrato Emulsionabile | CLODINAFOP|CLOQUINTOCET MEXYL | 80.8 g|20.2 g | 31/07/2027 |
| **TRIMMER 50 WG** | 016575 | ITALIA S.R.L. | Granulare Idrodispersibile | TRIBENURON | 50.0 g | 30/01/2035 |
| **TRINEX 250 EW** | 014074 | MAKHTESHIM LTD | Emulsione Olio/Acqua | BUPIRIMATE | 23.8 g | 31/01/2027 |
| **VALLEY** | 016616 | DEUTSCHLAND GMBH | Sospensione Concentrata | BIFENOX | 40.6 g | 31/03/2027 |
| **VANGUARD** | 017337 | MAKHTESHIM LTD | Granulare Idrodispersibile | FOSETYL-ALUMINIUM | 80.0 g | 31/10/2026 |
| **VANTEX** | 017690 | ITALIA S.R.L. | Granulare Idrodispersibile | CYMOXANIL | 45.0 g | 15/08/2026 |
| **VERBUM EW** | 013405 | MAKHTESHIM LTD | Emulsione Olio/Acqua | BUPIRIMATE | 23.8 g | 31/01/2027 |
| **VINETO** | 015740 | MAKHTESHIM LTD | Concentrato Emulsionabile | BUPIRIMATE|TEBUCONAZOLE | 11.6 g|4.7 g | 31/01/2027 |
| **VINIFOL WDG** | 017311 | ITALIA S.R.L. | Granulare Idrodispersibile | FOLPET | 80.0 g | 31/10/2040 |
| **VIP** | 013332 | ITALIA S.R.L. | Concentrato Emulsionabile | CLODINAFOP|CLOQUINTOCET MEXYL | 22.1 g|5.6 g | 31/07/2027 |
| **VIP 80 EC** | 014693 | ITALIA S.R.L. | Concentrato Emulsionabile | CLODINAFOP|CLOQUINTOCET MEXYL | 8.1 g|2.0 g | 31/07/2027 |
| **XINTECH 50** | 017409 | ITALIA S.R.L. | Granulare Idrodispersibile | PIRIMICARB | 50.0 g | 31/10/2026 |
| **ZETROLA** | 017115 | ITALIA S.R.L. | Concentrato Emulsionabile | PROPAQUIZAFOP | 9.6 g | 28/02/2027 |

---

## NÃO SEI — o que esta coleta não entrega

- **cultura e alvo — nao estao neste dataset, estao na etichetta de cada produto**
- **volume, preco, share e prioridade interna — nenhuma fonte publica sustenta**
- **Bulas / etichette em PDF** — servidas pela Banca Dati (`fitosanitari.salute.gov.it`), que neste ambiente
  falha no handshake TLS pelo gateway de saída. Não foram coletadas. Não há PDF de bula neste repositório.
- **Materiais de marketing, catálogo comercial e posicionamento de marca** — vivem no site bloqueado.

Nenhuma linha acima é inferida. Cada número sai do JSON de evidência e pode ser refeito com `scripts/adama_italia.py`.
