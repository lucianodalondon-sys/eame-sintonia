# SINAL-PRECOCE-PDF · o sinal precoce que JÁ está nos PDFs T3 do acervo (sem rede, sem resumir)

Ramo **`micro-prova-lote2b-v1`**, refeito por cima do vivo **`278cd489`** (rebase de 22 commits; 1 conflito só no mapa
declarado, resolvido pela união — o lado do vivo estava vazio nesse trecho). Feito a 26/09 depois das 14:00.

## 0 · ⚠️ Correção de um erro meu (passou para a coordenação)

Escrevi «Salerno ***Prays citri*** 4 → 40». **Errado.** A linha é «n. 0 catture di Prays Citri. n. **4** catture di
***Ceratitis Capitata***» (02/09) → «n. 0 catture di Prays Citri. n. **40** catture di Ceratitis Capitata» (16/09).
A *Prays citri* ficou em **0**; o **4 → 40 é a mosca-do-mediterrâneo** (*Ceratitis capitata*) nos citrinos de Angri.

## 1 · O que se leu

`curadoria/sinal_precoce_acervo.py` sobre `source-curator-service-v1/data/collection-store` + `C:/Users/London1/sintonia-sala-italia`
(só ficheiros; SOURCE_ID pelo caminho; o mesmo PDF conta 1 vez por sha256): **146 PDFs no acervo, 53 distintos; T3 = 8
distintos (13 cópias)**. Texto integral de cada um em `C:/Users/London1/sintonia-sala-italia/monitorizacao/acervo-t3/textos/`
(sha256 em `SHA256SUMS.txt`); **todas** as linhas com sinal, tal como estão, em `curadoria/SINAL-PRECOCE-PDF-ACERVO.json`.

| Fonte | PDF | Linhas com sinal | Sinal precoce? |
|---|---|---|---|
| IT-T3-002 Campania — Bollettino fitosanitario Prov. **Salerno** | N° 25 de 02/09/2026 · N° 27 de 16/09/2026 | 35 · 36 | **SIM — contagens por azienda/località** |
| IT-T3-010 **APOL** Puglia — Bollettino Mosca delle Olive | n.9 (07–13/09) · n.10 (14–20/09) | 49 · 47 | **SIM — valores por comprensorio** (colunas sem nome: ver §2.2) |
| IT-T3-008 **ARIF** Puglia — Notiziario agrometeorologico | N36 (02/09) · N38 (16/09) | 69 · 58 | **limiares + observação escrita** (sem números de captura) |
| IT-T3-011 AGRIOS | Requisiti concimi 2026 | 4 | não (requisitos de adubos) |
| IT-T3-020 SEI | Locandina (cartaz de evento) | 0 | não |

## 2 · As séries — valores EXATOS (texto do PDF entre aspas)

### 2.1 · IT-T3-002 — Salerno: rede de monitorização por AZIENDA (N° 25 → N° 27, **14 dias**)

| Cultura | Comune · Località · Azienda · Varietà | Fase (02/09 → 16/09) | Praga | 02/09/2026 | 16/09/2026 |
|---|---|---|---|---|---|
| Agrumi | Angri · Monte Longobardi · Taccaro Gennaro · varie | Accrescimento frutticini | *Prays citri* | «n. 0 catture» | «n. 0 catture» |
| Agrumi | idem | idem | ***Ceratitis capitata*** | «n. **4** catture» | «n. **40** catture» |
| Vite | Tramonti · Capitignano · Apicella P. · Piedirosso | Maturazione | *Lobesia botrana* | «n.3 catture» | «n.5 catture» |
| Vite | idem | idem | *Cryptoblabes gnidiella* | «n.0 catture» | «n.0 catture» |
| Vite | idem | idem | Scafoide (*Scaphoideus*) | «n. 3 catture» | «n. 4 catture» |
| Vite | Torchiara · Stazione di Torchiara · Cardone F. · Fiano | Maturazione → Post-raccolta | — | «Nessun rilevo» | «Nessun rilevo» |
| Castagno | Tramonti · Frescale · Apicella Gaetano · diverse | Accrescimento riccio | *Cydia fagiglandana* | «. 2 catture» | «n. 0 catture» |
| Castagno | idem | idem | *Pammene fasciana* | «n. 5 catture» | «n. 0 catture» |
| Castagno | idem | idem | Cinipide | «Presenza» | «Presenza» |
| Noce | Sarno · Quattrofuni · Fasolino · Sorrento | Maturazione frutti | *Cydia pomonella* | «n. 3 catture» | «n. 3 catture» |
| Olivo | Campagna (Reppuccia G., Rotondella) / Agropoli (S. Maria La Nova, Palombe; Cardone F., Salella-Frantoio-Leccino) | Accrescimento del frutto | mosca | 1.ª linha «Minime cattura di mosca» · 2.ª «Nulla» | 1.ª «Media catture **3** Infestazioni 0» · 2.ª «Media catture **7** Infestazioni 0» |
| Pomodoro | Sarno · San Vito · Raimo Aniello · San Marzano | Prosegue la raccolta | *Tuta absoluta* | «n. 5 catture» | «n. 5 catture» |
| Pomodoro | idem | idem | *Helicoverpa armigera* | «n. 0 catture» | «n. 0 catture» |
| Melanzana | Capaccio · Paestum Scalo · Mucciolo L. · Diverse | Maturazione commerciale | *Tuta absoluta* | «n. 6 catture» (+ «Presenza di cicaline») | «n. 9 catture» |
| Actinidia · Ciliegio · Fragola · Nocciolo · Pesco | Eboli, Nocera Inf., Battipaglia, Giffoni Sei Casali, Eboli | — | — | «Nulla» / «Nulla da segnalare» | idem |

⚠️ **Olivo:** a tabela põe 2 linhas (Campagna e Agropoli) mas o `-layout` mistura as colunas — **a que localidade pertence
cada valor (3 e 7) = NAO SEI** sem ver o PDF; a ordem é a das linhas. **Limiares escritos** no mesmo boletim (secção de
defesa): afídio dos citrinos «10%(5% per clementine e mandarino) dei germogli infestati»; cocciniglia bianca «Soglia: presenza».

### 2.2 · IT-T3-010 — APOL Puglia, mosca da azeitona (**semanal**)

| Comprensorio (comuni no PDF) | Fase | n.9 · 07–13/09/2026 | n.10 · 14–20/09/2026 |
|---|---|---|---|
| BR – Collina Litoranea (Brindisi, Carovigno, Ceglie Messapica, Cellino S. Marco, Fasano, Francavilla F., Mesagne, Oria, Ostuni, S. Donaci, S. Vito dei Normanni, Torchiarolo, Torre S. Susanna, Villa Castelli, S. Giorgio Ionico) | Ingrossamento frutti | «7 · 1 · 5% · STAZIONARIO · BASSO» | «7 · 1 · 5% · STAZIONARIO · BASSO» |
| LE – Pianura Salentina Nord (Arnesano, Campi Sal., Cavallino, Copertino, Lecce, Lizzanello, Monteroni, Nardò, Novoli, Salice Sal., Surbo, Trepuzzi, Veglie, Vernole) | Ingrossamento frutti | «5 · 1 · 5% · STAZIONARIO · BASSO» | «6 · 1 · 5% · STAZIONARIO · BASSO» |
| LE – Pianura Salentina Sud (Acquarica del Capo, Alezio, Cannole, Carpignano, Casarano, Gallipoli, Giuggianello, Giurdignano, Martano, Matino, Melendugno, Melissano, Minervino, Nociglia, Otranto, Palmariggi, Poggiardo, Presicce, Ruffano, Salve, S. Cassiano…) | Ingrossamento frutti | «4 · 1 · 5% · STAZIONARIO · BASSO» | «6 · 1 · 5% · STAZIONARIO · BASSO» |

⚠️ **O cabeçalho da tabela é imagem: o que são «7/5/4→6», «1» e «5%» = NAO SEI** (não se adivinha: pode ser catture,
punture, soglia…). O texto do próprio boletim diz: «non si sono rilevate raggiungimenti o superamenti della soglia di
intervento con pochissime punture fertili e ancora un basso numero di individui riscontrati sulle trappole a feromoni»
e (n.9) «punte del 2,0% osservate in zone irrigue costiere di tutti comprensori e su varietà a drupa grossa»; e avisa
«non c'è alcuna correlazione tra numero delle catture e reale infestazione in campo». O anexo (disciplinare) tem duas
camadas de texto sobrepostas e sai com letras misturadas — essas linhas estão no JSON tal como saíram e **não** se leem.

### 2.3 · IT-T3-008 — ARIF Puglia: observação escrita (N36 02/09 → N38 16/09) e limiares

| Cultura | Praga | N36 · 02/09/2026 | N38 · 16/09/2026 |
|---|---|---|---|
| Olivo | mosca (*Bactrocera oleae*) | «Poche catture, punture fertili di mosca (Bactrocera oleae) ma solo in alcuni contesti ad alta suscettibilità, su cv sensibili, in irriguo e generalmente al disotto delle soglie di intervento» | «**Aumento del numero di punture di ovodeposizione** da parte della mosca dell'olivo (Bactrocera oleae)» · «ancora si registrano poche catture di mosca (Bactrocera oleae), salvo casi isolati in contesti ad alta suscettibilità» |
| Olivo | tignola (*Prays oleae*) | — | «Cascola di olive dovute ai fori di sfarfallamento della tignola delle olive (Prays Oleae)» |
| Vite | tignoletta (*Lobesia botrana*) | «Per la tignoletta, si riscontrano poche catture nelle trappole a feromoni» | idem |
| Vite | *Planococcus ficus*, *Jacobiasca lybica* | — | «presente in qualche campo di osservazione» (as duas) |
| Agrumi (pela praga) | *Aleurocanthus spiniferus* | — | «in qualche campo di osservazione si osserva una ripresa» |

**Limiares escritos** (iguais nos dois números, texto tal como está): mosca olivo «soglia di infestazione, 4-5% per le olive
da olio e le prime punture per le olive da tavola» / «4-5% di infestazione attiva (sommatoria di uova e larve)» ·
cidia «10 catture per trappola a settimana» · anarsia «7 catture per trappola a settimana o di 10 catture per trappola in
due settimane» · tignoletta «in relazione alla curva di volo… insetticidi tradizionali: dopo 8-12 giorni dall'inizio del
volo; regolatori di crescita: 4-5 giorni; Bacillus thuringiensis: 5-7 giorni… ripetuto dopo 7-10 giorni» · cotonello
(*Planococcus citri*) «5% di frutti infestati» / «20% di frutti infestati» · *Tetranychus urticae* «10% di foglie infestate
da forme mobili e del 2% di frutti infestati» · *Panonychus citri* «30% di foglie infestate oppure in presenza di 3 acari
per foglia» · *Aonidiella aurantii* «10%…» · minatrice/acari «10% di foglie infestate». A cultura de cada limiar sai da
linha ou da praga (o `-layout` não deixa os títulos de secção legíveis). Localidade: regional (Puglia); NAO SEI mais fino.

## 3 · O COMANDO — Friuli (cimice 18/08) + Umbria (boletins semanais 2026), 1 pedido por PDF, teto 5/domínio

`curadoria/LOTE-PDF-SERIES.json`: **47 PDFs em 12 rondas** — Friuli «Monitoraggio Halyomorpha halys 18-agosto-2026» (ronda 1)
+ Umbria **olivo n.13 → n.1** (25/09 → 26/06), **vite n.21 → n.1**, **nocciolo n.12 → n.1** (2026). Endereços tirados dos links
das páginas da sonda lm-1310 (nenhum escrito à mão; o nocciolo n.3 tem o nome sem ano → 2026 pela série, marcado).
Cada ronda: **≤ 4 PDFs por domínio + robots = 5**. O leitor recusa correr um lote com rondas sem `--ronda=N`.

```bash
V=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1 ; M=C:/g/mprova
S=C:/Users/London1/sintonia-sala-italia/monitorizacao/series-$(date +%H%M) ; mkdir -p $S
git -C $M fetch origin micro-prova-lote2b-v1 && git -C $M checkout --detach FETCH_HEAD   # = o SHA do relatório
cd $M
for R in 1 2 3; do                                   # mosca do olivo primeiro: rondas 1-3 = olivo n.13..n.2 (+ cimice FVG)
  py superficie/rede.py --portao-de-egresso IT | tee $S/PORTAO-R$R.txt | grep -q "EGRESS_GATE=PASS" || break
  py curadoria/ler_pdf_monitorizacao.py --lote=curadoria/LOTE-PDF-SERIES.json --ronda=$R \
     --bytes=$S/pdfs --saida=$S/LINHAS-R$R.json | tee -a $S/stdout.txt
  sleep 1200                                         # 20 min entre rondas ao mesmo dominio
done
```
Rondas 4–12 (olivo n.1 + vite + nocciolo): o mesmo, `for R in 4 5 … 12`. Por ronda: Umbria 4 PDFs + 1 robots; a
ronda 1 também 1 robots + 1 PDF no ersa.fvg.it. **Total: 47 PDFs + 13 robots = 60 pedidos**, nunca > 5 por domínio e ronda.
Depois (sem rede): leio as linhas e monto a série semanal por cultura/praga como no §2, com os valores exatos.

## 4 · Testes e prova

`test_sinal_precoce_acervo` 3/3 · `test_ler_pdf_monitorizacao` 13/13 (inclui: nenhuma ronda passa 4 PDFs por domínio) ·
as outras ferramentas do ramo: `test_medir_contagens`, `test_colher_prova_territorio`, `test_micro_prova_colisao`,
`test_micro_prova_passo9` — todos verdes por cima do vivo `278cd489`.

## EM PALAVRAS SIMPLES

- **Errei um nome:** o salto de 4 para 40 insectos em Salerno é da **mosca-do-mediterrâneo** nos citrinos, não da traça
  dos citrinos (essa ficou em zero). Os números estão certos; o bicho estava trocado.
- **Já temos, no nosso arquivo, o primeiro sinal da praga:** Salerno conta insectos nas armadilhas **fazenda a fazenda**,
  a cada duas semanas (ex.: traça da uva 3 → 5, tuta no tomate/beringela 6 → 9); a Puglia publica **toda semana** um
  quadro da mosca da azeitona por zona (os números sobem de 4–5 para 6 em duas zonas — mas o que cada coluna mede não sei
  dizer, porque o título da tabela é uma imagem); e a Puglia escreve «aumentaram as picadas da mosca» de uma semana para a
  outra, e os limites a partir dos quais se deve tratar.
- **Pronto para correr:** a busca dos boletins semanais da Úmbria de 2026 (oliveira, videira, avelã) e do relatório da
  percevejo do Friuli, em rondas pequenas (no máximo 5 visitas por site de cada vez), começando pela oliveira.
