# CANARIO_1149_MAPA_DE_RESPONSABILIDADE

Coordenador · 28/09/2026 ~12:45 BRT · pedido do dono (D131) · medido no vivo `servico-20260923-0923 @ e24139702`, na Sala real (só leitura), no RAW guardado e nas Bíblias commitadas. **Lei = Bíblia + contrato; implementação = código; observação = o que o 1149 mostrou.** Onde a arquitetura não diz: `DONO = NÃO DEFINIDO`.

Autoridades lidas: `BIBLIA-CANONICA-DA-COLETA.md` @52da84376 (V1.5), `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` @86f3b5b22, `system-map/data/state.generated.json`, `AGENTS.md`, SOULs dos bots (scrap-engineer, intelligence-owner, casco-owner, source-curator). Divisão canônica (Intel. Bíblia §2, linhas 84-106): **COLLECTION OWNS RAW/ARTIFACT/DERIVED/STRUCTURED/ADMISSION + SOURCE FACTUAL CLAIM/FACT EXTRAÍDO e sua identidade/proveniência; INTELLIGENCE consome CLAIM/FACT admitido e NÃO fabrica outro.**

## 0 · O que o documento REALMENTE afirma (RAW 2272, sha256 f2158520…, 82.925 bytes, preservado)

| entidade | papel no texto | evidência literal (RAW) |
|---|---|---|
| CREA | quem publica / coordena 4 de 11 projetos | «COMUNICATO STAMPA … CREA in prima linea a coordinare 4 progetti» |
| 22/06/2026 | **data de publicação** do comunicado | `<div class="content-date"> 22 giu 2026 </div>` ao lado de `<div class="content-category">COMUNICATO STAMPA</div>` |
| encontro no CIHEAM Bari | evento que motivou o comunicado; **data do evento NÃO escrita** | «dall'incontro "Analisi e prospettive…" ospitato dal CIHEAM Bari» |
| *Xylella fastidiosa* | **agente causal** (bactéria) — «il batterio», «patogeno» | título + «contrastare la diffusione del batterio» |
| oliveira | **cultura/hospedeiro** principal (também vite, projeto NOVIXGEN) | «olivicoltura», «genotipi di olivo», «Questo progetto è l'unico ad occuparsi anche di vite» |
| sputacchina (*Philaenus spumarius*) | **vetor** do agente | «il controllo degli insetti vettori, in particolare la sputacchina (Philaenus spumarius)» |
| nematoides (2 espécies novas) | **organismo de controle** do vetor (NÃO praga) | «due nuove specie di nematodi parassiti della sputacchina» |
| óleos essenciais, microrganismos | meios de controle do vetor | «composti naturali … oli essenziali … microorganismi utili» |
| Salento | **lugar do estudo** (seleção de 200 genótipos) — não é foco de campo relatado | «selezionato e caratterizzato, nelle aree colpite del Salento 200 genotipi di olivo» |
| projetos DIACOX, COVEXY, GENFORAGRIS, NOVIXGEN | ações/estudos (Masaf) | nomes no corpo |
| espécie da afirmação | **RESULTADO_DE_PESQUISA** (comunicado de resultados parciais) — nem FATO_OBSERVADO de campo, nem PREVISAO | «Presentati i primi risultati dei progetti» |

## 1 · O caminho do 1149, elo por elo

| # | elo | componente (System Map) · arquivo | dono (lei) | entra | deve sair | PODE interpretar | NÃO PODE | evidência guardada | próximo | observado no 1149 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FONTE | contrato `IT-T5-111` em `curadoria/italy_contracts_curator.json` | Collection · Source Curator (COL-LAW-053/205) | — | SOURCE_ID, rota, EVIDENCE_CLASS, SOURCE_LOCATION_RULE | o que a fonte entrega | o conteúdo | contrato versionado | coleta | 🟡 contrato **não declara** EVIDENCE_CLASS nem SOURCE_LOCATION_RULE (`source_declared_evidence_class = NAO SEI`) |
| 2 | AQUISIÇÃO | `C-IT-COLETA` · `coleta/italy_pilot_collect.mjs` via `coleta_continua.py` | Collection (orquestrador); capability de aquisição = Scrap Engineer (SOUL «adapters, download») | pedido do ciclo 21 | RAW + storage + run | nada semântico | conteúdo | `raw_asset 2272`, sha, `collection_run`, egresso IT, prova-teto | derivação | 🟢 HTML inteiro preservado, com a data e o Salento dentro |
| 3 | DERIVAÇÃO HTML→texto | `C-EXECUTOR-TEXTO-HTML` · `coleta/executor_texto_de_html.py` → `coleta/texto_fonte.py::limpar` (l.67-73) | Collection (COL-LAW-008/203: derivado aponta pai + transformação); «parsing técnico inicial» = **Scrap Engineer** (SOUL §FRONTEIRA) | bytes do RAW | texto derivado **que preserve a estrutura** (HTML_RAW ≠ EXTRACTED_ARTICLE, Bíblia l.150) + PUBLISHED_AT com base | separar menu/corpo/rodapé; ler metadado de publicação | fato, tempo do fato, lugar do fato | `derived_artifact 1149`, receita | extração de tempo/lugar | 🔴 **PRIMEIRO VERMELHO.** `limpar()` troca cada tag por espaço (`re.sub(r'<[^>]+>',' ')`): 186 `</div>` e 28 `<p>` viram **uma linha só** (medido: o texto da Sala tem 1 linha, 8.989 caracteres; os primeiros 1.968 são menu). A data está num campo estruturado `content-date`, e `tempo_de_publicacao` (l.438) só procura JSON-LD/meta/`<time>`/itemprop/índice → PUBLISHED_AT = NAO SEI |
| 4 | TEMPO/LUGAR do item | `C-LUGAR-COLETA` · `leis/fato_do_texto.py`, `leis/fato_local.py`, `leis/estudo_chaves.py` | Collection (COL-LAW-031/032/201; DA-6 «dono de FACT_TIME a partir do texto = extrator lugar-fato») | texto derivado | FACT_TIME/FACT_LOCATION **só com trecho**, PUBLISHED_AT ≠ FACT_TIME | lugar e tempo **escritos** e ligados ao fato | inferir por fonte/publicação/vizinhança | `tempo_lugar_evidencia`, bases | admissão | 🔴 herdado do elo 3: `corpo()` filtra por linha → a linha única casa RODAPÉ → «o texto não tem corpo (só menu/rodapé)» |
| 5 | CLAIM/ENTIDADES + PAPEL | **COL-LAW-202 ARTEFATO→CLAIM** (SUBJECT·PREDICATE·OBJECT, EVIDENCE_SPAN); **COL-LAW-221** ENTITY_SOURCE; **COL-LAW-223** espécie; contratos parciais: `PROBLEMA/v1` (`leis/afirmacao_da_fonte.py:66-95`), CULTURA na `janela_declarada` | **Collection** (Intel. Bíblia l.84-106; Coleta COL-LAW-202) | texto + trecho | claim(s) com entidades, papel e trecho | nomear o que está escrito, com trecho | escolher entre entidades concorrentes; conhecimento externo | `janela_declarada`, `FATO` | admissão/READY | 🔴 **IMPLEMENTAÇÃO AUSENTE**: a Bíblia diz literalmente «Extração de claim é TARGET, nunca CURRENT … **IT ABSENT**» (COL-LAW-202). Hoje só existem blocos soltos: CULTURA = [olivo, vite] (certo); PROBLEMA = **um nome** ou NAO SEI → «xylella, nematode» = 2 candidatos → NAO SEI; `FATO = NAO_SE_APLICA` |
| 6 | ADMISSÃO (gaveta) | `C-ADMISSAO` · `admissao/admissao.py` `decidir()` l.1559 → `_do_universo` | Collection (COL-LAW-042: decisão por par item×universo, regra, versão, motivo, evidência) | item derivado + universo do PEDIDO | SIM/NAO/NAO_SEI/NSA/ERRO com motivo e prova | pertença do item ao universo pedido | o universo (vem do pedido); o fato | livro de decisões | Sala | 🟡 **DEFEITO A**: SIM por `tesi` ⊂ «at**tesi**» + `ricerca` (substring, l.876; T5 fora de `PALAVRA_INTEIRA` l.793; texto julgado = item inteiro com menu, l.861-862; `SINAIS_MINIMOS=2` l.768) |
| 7 | SALA | `C-SALA-DE-ESPERA` · `admissao/sala_de_espera.py` | Collection | READY | linha append-only, revisões | nada | nada | `sala_de_espera_atual derived:1149` | Intelligence | 🟢 guardou fielmente o que recebeu (pobre) |
| 8 | INTELLIGENCE | `C-INT-MOTOR-CAPACIDADES` · `motor/motor_das_capacidades.py` (+ `porta_da_referencia.py`) | Intelligence (INT-LAW-010, 030, 083, 090-095, 100-105) | READY admitido | CROSSING/SIGNAL/FINDING… ou NOT_POSSIBLE/UNKNOWN com lacuna | juntar READY por chaves; julgar | fabricar CLAIM, tempo ou lugar (INT-LAW-031/083/100) | `INTELLIGENCE_RUN`, REQUIREMENTS | pote | 🟡 cumpriu a lei: CAP-WIN NOT_POSSIBLE (PROBLEMA e REGIÃO NAO SEI), CAP-SCI FORA (sem DOI) → lacuna. Não deve «ler o texto» para compensar (INT-LAW-083) |
| 9 | POTE | `C-POTE-INT-CASCO` · `pacote/pote_intelligence_casco.py` | Entrega/pacote (contrato POTE v2) | corrida da Intelligence | objetos + LACUNAS, marca, SHA | nada analítico | recalcular | POTE `IR-04a259421a451a8aa778` (cópia) | casco | 🟡 1149 só em LACUNAS; pote EXPERIMENTAL·NAO_PARA_CLIENTE |
| 10 | CASCO/PORTAL | `italia-portale/` · casco-owner | Casco (SOUL: só apresenta) | pote validado | tela | nada | promover, completar NÃO SEI | deploy + antes/depois (D126) | — | ⚪ não chega; produção = 14/09 |

## 2 · Pergunta central — QUEM deveria ter identificado, campo por campo

| campo | está no RAW? | quem deveria (lei) | peça que implementa hoje | veredito |
|---|---|---|---|---|
| **data de publicação 22/06/2026** | SIM, em campo estruturado `content-date` | **B) derivação HTML** (`executor_texto_de_html.tempo_de_publicacao`; COL-LAW-031 PUBLISHED_AT; Coleta l.1188 dono do transporte = `coleta/ingresso.py`) | existe, mas só lê JSON-LD/meta/`<time>`/itemprop/índice | DONO DEFINIDO (Collection · derivação). Falhou por não ler o campo de data que a própria página estrutura |
| **data do acontecimento** | NÃO (o encontro no CIHEAM não tem data escrita; «22 giu» é publicação) | B) extrator tempo-do-fato (`leis/fato_do_texto`, DA-6) | existe | **NAO SEI é a resposta certa** — COL-LAW-031 proíbe FACT_TIME = PUBLISHED_AT |
| **cultura = oliveira** | SIM | B/E) Collection · CLAIM (COL-LAW-202) — hoje `janela_declarada.CULTURA` | existe (`coleta/pesquisadores_t6.py::CULTURAS` via estudo_chaves) | ✅ **já identificou** (olivo, e também vite — ambos escritos) |
| **Xylella fastidiosa** | SIM | B/E) Collection · CLAIM / `PROBLEMA/v1` | existe, mas o contrato aceita **UM** nome | ❌ perdido: virou NAO SEI porque «nematodi» contou como 2º problema (D112 «duas pragas = NAO SEI») |
| **papel: agente causal (bactéria)** | SIM | Collection · CLAIM com PAPEL (COL-LAW-202 SUBJECT/PREDICATE/OBJECT) | **NÃO EXISTE** | `DONO = Collection (lei)`, `IMPLEMENTAÇÃO = AUSENTE` |
| **papel dos nematoides (controle)** | SIM | idem | NÃO EXISTE (PROBLEMA/v1 não tem papel) | `ONTOLOGIA_INSUFICIENTE = SIM` |
| **papel do inseto vetor** | SIM | idem | NÃO EXISTE (sputacchina nem está no vocabulário) | `ONTOLOGIA_INSUFICIENTE = SIM` |
| **Salento** | SIM, como lugar do **estudo** | B) extrator de lugar (`leis/estudo_chaves.py` LOCAL_DO_ESTUDO; COL-LAW-032; D112) | existe, mas o gazetteer não tem «Salento» e o padrão «nelle aree … del X» não é lido | DONO DEFINIDO (Collection · lugar). ⚠️ É LOCAL_DO_ESTUDO, **não** FACT_LOCATION de campo (CAP-SCI: estudo nunca vira incidência de campo) |
| **espécie: resultado de pesquisa** | SIM («primi risultati dei progetti») | Collection (COL-LAW-223: FATO_OBSERVADO / PREVISAO / RECOMENDACAO…) + contrato da fonte (EVIDENCE_CLASS) | COL-LAW-223 não prevê «resultado de pesquisa sem DOI»; contrato da fonte = NAO SEI | `DONO = Collection`; **a CLASSE não existe na lista** → `ONTOLOGIA_INSUFICIENTE = SIM` |

Nenhum campo é da **Admissão** (ela julga pertença, não extrai) nem da **Intelligence** (ela consome; INT-LAW-083 proíbe fabricar o claim).

## 3 · ONTOLOGIA_INSUFICIENTE = SIM — o que falta (não ampliado)

`PROBLEMA/v1` guarda **um** nome sem papel; COL-LAW-202 prevê SUBJECT·PREDICATE·OBJECT mas está ABSENT; COL-LAW-223 não tem espécie para «resultado de pesquisa». Para este documento faltam, no mínimo: papel **HOSPEDEIRO**, **AGENTE_CAUSAL**, **VETOR**, **ORGANISMO_DE_CONTROLE**, **LUGAR_DO_ESTUDO** (existe só dentro de estudo_chaves), e a espécie **RESULTADO_DE_PESQUISA**. Decisão de ampliar = dono (não feita).

## 4 · Dois defeitos, duas causas-raiz independentes

**DEFEITO A — PORTÃO/ROTEAMENTO** (`C-ADMISSAO`, Collection). Causa-raiz: a régua T5 procura palavras por **substring** (l.876; T5 não está em PALAVRA_INTEIRA l.793) no **item inteiro, menu incluído** (l.861-862), e 2 palavras de «ciência» bastam (l.768/932). Nenhuma palavra exige assunto agro (l.1015-1021). Corrigir A **não** melhora B em nada.

**DEFEITO B — COMPREENSÃO** (Collection: derivação + claim). Causas-raiz, na ordem do caminho:
- B1 · **derivação** (`texto_fonte.limpar` l.69): tags viram espaço → a estrutura do HTML (menu/`content-date`/`<p>`/rodapé) é destruída; tudo a jusante lê uma linha só.
- B2 · **publicação** (`tempo_de_publicacao` l.438): não lê o campo estruturado de data que a página tem.
- B3 · **claim com papel**: não existe (COL-LAW-202 ABSENT); `PROBLEMA/v1` de um nome + regra «duas pragas = NAO SEI» apaga a Xylella quando aparece um organismo de controle.
- B4 · **lugar**: «Salento» fora do gazetteer (dado, não lei).

## 5 · Gaveta de ciência — tabela pedida (LAB MISSAO-07, 22 itens T5 de 28/09; rótulos do LAB = modelo, **não humano**)

Regra atual literal (`admissao.py:1015-1021`): `T5: doi, orcid, estudo, ensaio, pesquisa, revista, artigo, universidade, instituto, publicacao, studio, ricerca, rivista, articolo, universita, istituto, pubblicazione, convegno, sperimentazione, prova di campo, prove sperimentali, tesi` · busca por substring (l.876) · no item inteiro (l.861) · SIM com ≥2 (l.768/932). Menu entra: medido 12/12 ENEA casam «ricerca» do menu («Infrastrutture di ricerca»); no 1149 os primeiros 1.968 caracteres são menu.

| proposta | ENTRA_ANTES | ENTRA_DEPOIS | ÚTEIS_PERDIDOS | FALSOS_REMOVIDOS | FALSOS_RESTANTES |
|---|---|---|---|---|---|
| C1 · T5 exige +1 termo de praga (T3) ou cultura (T1), palavra inteira | 22 (5 úteis · 8 disc. · 9 falsos) | 8 (5 úteis · 3 disc.) | **0** | **9** | 0 (3 discutíveis ficam) |
| C2 · T5 julgado só no corpo | 22 | 10 (7 falsos · 3 disc.) | **5** | 2 | 7 → **rejeitar** |
| C3 · conter ENEA (IT-T5-185/186) — **aplicado 28/09 12:05 por D130** | 22 | 10 (5 úteis · 5 disc.) | 0 | 9 | 0 |

Fora do conjunto de hoje, C1 também tiraria agro sem cultura/praga nomeada (ex.: `derived:57` escola de verão «sistemi zootecnici»): **medir antes de ligar**. Nada ligado na produção além do C3 (decisão D130).

## 6 · Reroute
D130 mantida: reroute **só T1 (cultura) e T2 (clima)**. Medição nas 76 notícias automáticas de 28/09: +2 úteis (T10), 0 falsos — **medição de um conjunto, não lei**. O ramo `origin/nuvem/reroute-fecho-v1` está com a chave LIGADA e 4 gavetas → **não integrável como está**; a equipe `nuvem-reroute-t1t2-v1` o prende a T1/T2.

## 7 · O que fazer com a entrega `origin/claude/canario-1149-first-review-3llkwl`
Tratada como **ESTUDO, NÃO INSTALAR**. Ela consertou a jusante do vermelho real: partiu a «linha achatada» em frases dentro de `leis/fato_do_texto.py` (em vez de preservar a estrutura na derivação), leu a data **no texto achatado** por regex (em vez do campo `content-date` no HTML), criou a regra `agente_de_controle` em `leis/boletim_do_campo.py` (= ampliação de ontologia, que o dono vetou por ora), e pôs «Salento» no vocabulário. O diagnóstico dela confirma B1-B4 e é útil.

## 8 · PRIMEIRO VERMELHO COMPROVADO e quem resolve

```
ITEM              = derived:1149 (CREA · Xylella/oliveira · RAW 2272 · sha f2158520…)
ELO_ATUAL         = 3 · DERIVAÇÃO HTML→texto (C-EXECUTOR-TEXTO-HTML)
ENTROU_COM        = HTML preservado, 82.925 bytes, estrutura intacta (186 </div>, 28 <p>, content-date "22 giu 2026", "nelle aree colpite del Salento")
SAIU_COM          = texto de 1 linha (8.989 car., 1.968 de menu na frente), PUBLISHED_AT = NAO SEI
PRIMEIRO_VERMELHO = a derivação achata o HTML (tags → espaço) e não lê a data estruturada
DONO_DO_VERMELHO  = Collection · derivação HTML→texto; capability de «parsing técnico inicial» = SINTONIA SCRAP ENGINEER
PROVA_PARA_FICAR_VERDE = re-derivar SÓ o RAW 2272 (cópia, sem rede) e mostrar: texto com parágrafos/linhas separados (menu e rodapé separáveis do corpo pelo corpo() que JÁ existe, sem o remendo da linha achatada) + PUBLISHED_AT = 2026-06-22 com BASE = campo content-date; e o controle negativo: nenhuma outra página do acervo muda de PUBLISHED_AT por acaso (replay).
```
Depois dele, na fila, sem pular: elo 4 (lugar — só se ainda vermelho após B1), elo 5 (claim/papel = ONTOLOGIA_INSUFICIENTE → decisão do dono), elo 6 (Defeito A), elo 8 (triagem da espécie, Intelligence).
