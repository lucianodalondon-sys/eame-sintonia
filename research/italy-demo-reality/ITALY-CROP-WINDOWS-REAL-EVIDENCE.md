# Crop Windows italianas — com a evidência de cada uma

**Data de referência:** 2026-09-01

**As cinco camadas nunca se misturam.** Cada linha deste documento diz de qual camada veio:

| Camada | O que é | Classe de evidência |
|---|---|---|
| **EXPECTED** | ciclo esperado da cultura | conhecimento agronômico / afirmação do fabricante |
| **OBSERVED** | fenologia observada e publicada por serviço regional | `PRIMARY_SOURCE_RAW` |
| **FIELD-REPORTED** | o que uma pessoa disse ter visto | `FIELD_VOICE_OBSERVED` |
| **LABEL** | o que o rótulo autoriza | `REGULATORY_FACT` |
| **MANDATORY / REGULATORY** | janela imposta por decreto | `REGULATORY_FACT` |
| **BUSINESS PREPARATION** | quando a ADAMA precisaria se mexer | `DERIVED_INTERPRETATION` |

---

## 1 · VITE × Flavescência dourada (vetor *Scaphoideus titanus*)

| Camada | Conteúdo | Fonte |
|---|---|---|
| **EXPECTED** | uma geração por ano; ovo hiberna; nascimento do fim de abril ao início de maio, com escalonamento notável até a primeira parte de junho | transcrição do convegno Coldiretti E-R, 26/02/2026 |
| **MANDATORY 2026 — Lombardia** | 2 tratamentos: **2–14/06** e **17–29/06**; ou 3 em biológico | Comunicato Giunta n. 39, 25/05/2026 |
| **MANDATORY 2026 — Veneto** | 2 tratamentos com ativos de síntese, 1ª janela **8–19/06**, 2ª a 10–15 dias; ou 3. **Primeiro tratamento só depois do fim da floração** | DDR n. 13645, 14/05/2026 + Bollettino vite n. 9, 03/06/2026 |
| **MANDATORY 2026 — Piemonte** | piano operativo 2026; obrigação estendida a hobbistas e terrenos incultos; **proibido tratar durante a floração** (L.R. 1/2019) | Det. Dirigenziale n. 280, 16/03/2026 |
| **MANDATORY 2026 — Trentino** | bollettino speciale n. 1 | 29/05/2026 |
| **OBSERVED** | adulto do vetor presente; videiras com sintomas de Giallumi devem ser capitozzate ou estirpate; trocar armadilhas cromotrópicas a cada duas semanas | Bollettino vite Veneto n. 19, 13/08/2026 |
| **OBSERVED** | 78% das empresas do painel positivas para escafoideo; 83% das biológicas; 2025 com recuperação clara após queda pós-2022 | Settore Fitosanitario Emilia-Romagna, no convegno de 26/02/2026 |
| **FIELD-REPORTED** | *"nella mia azienda, letteralmente distrutta dalla malattia"* — Trentino | comentário YouTube, `COUNTRY_OF_FACT = IT` |
| **LABEL** | 6 produtos ADAMA nomeiam *Scaphoideus titanus* no rótulo (tau-fluvalinato): KLARTAN 20 EW, KLARTAN SMART, TAU AL 240 EW, MAVRIK EW, MAVRIK SMART, EVURE PRO. Citação de rótulo: *"Vite (da vino e da tavola) Contro cicaline (Empoasca vitis, Scaphoideus titanus) … 30-300 ml/hl senza superare 0,3 l/ha"* | `IT-T4-001-ETICHETTA` |
| **LABEL — genérico** | 4 produtos com lambda-cialotrina cujo rótulo traz "cicaline": DURAVIS, ELTIRA, FORZA, NINJA | idem |
| **APPLICATION WINDOW 2026** | **FECHADA** — todas as janelas obrigatórias terminaram em junho/2026 | derivado |
| **MONITORING WINDOW** | **ABERTA AGORA** — início/meados de agosto a fim de setembro, para reconhecimento de sintoma foliar e captura de adultos | derivado dos boletins |
| **BUSINESS PREPARATION** | preparar até **2027-05-31**: a obrigação recorre por norma europeia, mas **as datas são fixadas a cada ano pelo monitoramento** — 2026 não é régua | derivado |
| ⚠️ **EXPOSIÇÃO DE VENCIMENTO** | tau-fluvalinato (6 produtos) vence **2027-01-31**; lambda-cialotrina (4) venceu **2026-08-31**. Todo o portfólio elegível vence antes da janela obrigatória de 2027 | `IT-T4-001` |

⚠️ `EXPIRY ≠ WITHDRAWAL`. Re-registro é rotina. `RENEWAL_STATUS = NÃO SEI`.

---

## 2 · MILHO × micotoxina (colheita — janela corrente)

| Camada | Conteúdo | Fonte |
|---|---|---|
| **EXPECTED** | colheita de grão em setembro–outubro no vale do Pó | conhecimento agronômico |
| **OBSERVED (2025)** | fumonisinas > 4 mg/kg em **72%** das amostras; **15%** não conformes para aflatoxina B1 | CREA, via AgroNotizie 13/02/2026 |
| **OBSERVED (2026, corrente)** | calor recorde e seca de verão favorecem os fungos aflatoxígenos, sobretudo em espigas estressadas; análises em campanha e nos centros de armazenagem concentradas em teor de micotoxina | imprensa técnica, ago–set/2026 |
| **CONTEXTO DE MERCADO** | produção francesa caiu de ~14 para 9 Mt, com reflexo no abastecimento italiano | idem |
| **BOA PRÁTICA** | colher com umidade **não inferior a 22%**; segregar lotes de borda de campo | idem |
| **REGULATORY** | Reg. (UE) 2024/1022: **DON de 1.250 → 1.000 µg/kg**; T-2+HT-2 máx. **50 µg/kg** | legislação europeia |
| **BIOCONTROLE** | AF-X1 utilizável em 2026 de **04/03 a 01/07** — janela **já fechada** | imprensa técnica |
| **LABEL — ADAMA** | **36 produtos citam MAIZE no rótulo: 24 herbicidas, 9 inseticidas e ZERO fungicidas** | `IT-T4-001` |

⚠️ Esta última linha é o fato estrutural mais importante do milho italiano para a ADAMA: **a janela de
micotoxina existe, é regulada, é comercialmente relevante — e a ADAMA não tem fungicida citando milho na
Itália.** Isso é contexto para decisão interna, **não** uma oportunidade de venda.

---

## 3 · CEREAIS (frumento, orzo) × infestantes e doenças

| Camada | Conteúdo | Fonte |
|---|---|---|
| **EXPECTED — herbicida** | prática dominante na Itália: **uma única intervenção entre afilhamento (accestimento) e início de alongamento (levata)** | página `/cereali` da ADAMA |
| **EXPECTED — leito de semeadura** | limpeza com glifosato, "fundamental no plantio direto" | idem |
| **EXPECTED — doença** | oídio favorecido entre fevereiro e abril com seco e poucas chuvas, sobretudo em áreas litorâneas; septoriose mais agressiva na fase de levata, favorecida por chuvas frequentes e 15–20 °C | idem |
| **OBSERVED** | *"Non riscontrata presenza di avversità ad eccezione di lieve attacco di Septoriosi nei Comuni di Branca di Gubbio. In pre-fioritura, in considerazione dell'instabilità climatica, si consiglia un intervento per il controllo della fusariosi della spiga"* | Bollettino cereali n. 04, Servizio Fitosanitario Umbria |
| **OBSERVED** | bollettino difesa integrata frumento-orzo n. 07 | ERSA FVG, 20/04/2026 |
| **OBSERVED** | bollettino fitossanitário provincial | LaMMA / Regione Toscana + CNR, Grosseto, 23/04/2026 |
| **OBSERVED** | notiziario di produzione integrada n. 615 e n. 616 | AMAP Marche — Ancona, 22 e 29/04/2026 |
| **LABEL** | 61 produtos citam WHEAT_GENERIC · 46 BARLEY · 25 TRITICALE · 24 COMMON_WHEAT · **14 DURUM_WHEAT** | `IT-T4-001` |
| **LABEL — linha autorizada** | MAXENTIS e KOJAMI em COMMON_WHEAT contra *Zymoseptoria tritici* e *Septoria*; STAVENTO em WHEAT_GENERIC contra *Septoria tritici*, **1,0–1,2 l/ha, intervalo 14 dias** | `IT-T4-001` |
| **BUSINESS PREPARATION** | semeadura de outono é **agora** (set–nov). A escolha de fungicida depende do areal, dos patógenos dominantes e da precocidade da variedade | imprensa técnica |

---

## 4 · SOJA e MILHO × *Amaranthus* resistente a ALS

| Camada | Conteúdo | Fonte |
|---|---|---|
| **EXPECTED — janela** | pré-emergência; pós-emergência precoce **até no máximo 2–4 folhas verdadeiras**; para *A. tuberculatus*, ainda mais antecipado | linhas-guia GIRE (via fonte secundária) |
| **OBSERVED — distribuição** | populações ALS-resistentes no Vêneto, Emilia-Romagna e, nos últimos anos, especialmente no Friuli-Venezia Giulia; origem no alto ferrarese; casos nas províncias de **Verona e Rovigo**, onde se pratica rotação milho-soja | GIRE / imprensa técnica |
| **OBSERVED — espécies** | *A. retroflexus*, *A. hybridus*, ***A. tuberculatus*** (dioica, alógama — a mais preocupante) e ***A. palmeri*** confirmada ALS-resistente no Vêneto | idem |
| **MANUFACTURER_CLAIM** | *"a resistência de diversos ecótipos de Amaranto a herbicidas ALS está se expandindo no norte da Itália"* | página `/soia` da ADAMA |
| **LABEL** | 33 produtos citam SOYBEAN; 36 citam MAIZE. Bifenox (**HRAC 14 / grupo E**) em **7 registros** ADAMA | `IT-T4-001` |
| **CONVERGÊNCIA** | a linha-guia italiana recomenda **grupo E (bifenox)** para *A. tuberculatus* depois que bentazone perde eficácia | GIRE, via fonte secundária ⚠️ não lida na fonte |

⚠️ Esta é a convergência mais promissora da pesquisa e **também a menos verificada**: o site do GIRE
devolveu certificado expirado hoje. Antes de virar peça de demo, a linha-guia precisa ser aberta.

---

## 5 · VITE × peronospora (*Plasmopara viticola*)

| Camada | Conteúdo | Fonte |
|---|---|---|
| **EXPECTED — ciclo** | oósporo hiberna no solo nos resíduos de folha; chuvas "preparatórias" de primavera fazem germinar; infeção primária pelos estômatos da página inferior; infeções secundárias com poucas horas de molhamento, até só orvalho | página `/vite` da ADAMA |
| **EXPECTED — sensibilidade** | cachos muito sensíveis em plena floração; depois, entrada pelo pedicelo ("peronospora larvata") quando os bagos passam de 3–4 mm | idem |
| **OBSERVED (2026)** | após as chuvas abundantes de março-abril, anata provavelmente "de virulência muito elevada" | Terra e Vita, maio/2026 |
| **OBSERVED** | bollettino difesa integrata vite n. 06, zona D.O.C. Collio, a cargo do enólogo **Dario Maurigh** | 15/05/2026 |
| **LABEL / CLAIM** | linha Folpan: Folpan® 80 WDG (multissítio de cobertura), Folpan® Gold (contato + sistêmico), **Folpan® Energy** (contato multissítio + sistêmico, protege tecidos em crescimento, até a **invaiatura**, **máximo 5 tratamentos**) | site ADAMA, artigo de 20/04/2026 |
| **COMPETIDOR** | ***Plasmopara viticola* é o problema mais nomeado da publicidade paga italiana: 16 dos 414 anúncios** | Meta Ads Library |

---

## 6 · Janela corrente — o que está aberto AGORA (01/09/2026)

| Cultura | Janela | Estado hoje |
|---|---|---|
| **Vite** | **vendemmia** | **em curso**, antecipada 7–10 dias (8–10 no Nordeste). Sem previsão nacional: Assoenologi, Ismea e UIV não publicam por instabilidade meteorológica |
| **Vite** | **monitoramento de flavescência** | **ABERTA** — reconhecimento de sintoma foliar e captura de adultos até fim de setembro |
| **Vite** | tratamento obrigatório 2026 | **FECHADA** desde junho |
| **Milho** | colheita e controle de micotoxina | **ABERTA** — alerta corrente de aflatoxina por calor e seca |
| **Milho** | biocontrole AF-X1 | **FECHADA** (foi 04/03–01/07/2026) |
| **Cereais** | semeadura de outono | **ABRINDO** (set–nov) |
| **Portfólio ADAMA** | vencimentos regulatórios | **71 de 163 vencem em até 6 meses** a partir de 30/08/2026 |

---

## 7 · O que NÃO temos de Crop Window

- **fenologia observada corrente** (setembro/2026) de qualquer região: os boletins preservados são de
  abril–maio/2026, e as rotas ao vivo do Veneto (bloqueio por IP), ERSA FVG e Emilia-Romagna (404 nos
  caminhos tentados) falharam hoje
- **janela de aplicação lida no rótulo** — a coluna de época não foi extraída dos 163 PDFs
- **as três maiores regiões de milho** (Veneto, Lombardia, Piemonte — 71,6% da área) **não têm boletim de
  milho medido** no acervo
- nenhuma janela de olivo, barbabietola, patata, girassol — culturas com registro ADAMA e sem cobertura
