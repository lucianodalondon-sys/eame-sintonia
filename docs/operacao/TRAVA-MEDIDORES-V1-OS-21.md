# TRAVA-MEDIDORES-V1 · BLOCO (a) — os 21 ficheiros do congelamento, um a um

> Leitura autorizada pela D33 (bot Luciano, delegação do dono, `DECISOES-DONO-2026-09-23.md`).
> **Só leitura.** A trava não foi editada. **Até cada ficheiro ser julgado pelo dono, N = NAO.**

| campo | valor |
|---|---|
| fotografia | `FREEZE_MANIFEST` da trava, `FROZEN_AT_HEAD = 82ef1deb` (08/09) |
| árvore comparada | produção `egresso-consenso-v1` @ `a310487f` |
| a lista | `system-map/data/congelamento.generated.json` → `CONTRA_A_FOTOGRAFIA` (16 `MUDARAM` + 5 `NOVOS`), gerado pelo censo consertado neste ramo |
| método | `git log 82ef1deb..a310487f -- <ficheiro>` (intenção declarada) + `git diff 82ef1deb a310487f -- <ficheiro>` (o que mudou). Leitura feita por três leitores em paralelo; **as 8 linhas de prova mais pesadas foram reconferidas por mim no diff** (todas presentes) |

## 0 · O resultado

| classe (D33) | n | ficheiros |
|---|---|---|
| **AVANCO PROIBIDO** | **5** | `checks.mjs`, `adama-relevance.js`, `italy-casa.js`, `italy-i18n.js`, `meeting-intelligence-snapshot.js` |
| **CONSERTO PERMITIDO** | **7** | `instagram_coleta.py`, `casa-gate.mjs`, `release-gate.mjs`, `it_casa_dados.py`, `italy-app-model.js`, `meeting-surface.js`, `superficie-visivel.mjs` |
| **FALSO POSITIVO DO MEDIDOR** | **5** | `italy_contracts.mjs`, `sensor_coleta.py`, `sensor_medir.py`, `DATA-DEMAND-MATRIX-ITALY.json`, `architecture.declared.json` |
| **DECISÃO DO DONO REAL** | **3** | `meeting-gate.mjs`, `INTELLIGENCE-OBJECT-MODEL-V1.json`, `italy-label-intelligence.js` |
| **NAO SEI** | **1** | `italy-handoff-v21.js` |

**Por isso N continua NAO**: há 5 avanços proibidos, 3 à espera do dono e 1 por julgar.

## 1 · O facto que atravessa 12 dos 21: escrito a 07/09, entrou a 15/09

Os 12 ficheiros do portal (`italia-portale/…`) chegaram à produção por **um** commit,
`c24ea78a` (15/09, «casa: o Portal atual entra na linha técnica — uma casa só para o IT»),
que trouxe trabalho feito noutros ramos a 07/09. Conferido com `git merge-base --is-ancestor`:

```text
8b590a55 07/09 fora_de_B    fb96f49d 07/09 fora_de_B    2d1b07f2 07/09 fora_de_B
0df93115 07/09 fora_de_B    65d0de42 07/09 fora_de_B    dd4950e7 07/09 fora_de_B
c24ea78a 15/09 fora_de_B
```

Nenhum desses commits está na história da fotografia (`82ef1deb`). **Para a linha de produção,
o conteúdo chegou depois do congelamento.** Classifiquei pelo que o ficheiro passou a FAZER, não
pela data em que foi escrito. Se o dono decidir que «escrito antes, portado depois» não conta
como desenvolvimento novo, os 5 AVANCO do portal mudam de natureza — mas continuam a fazer uma
coisa que a trava proíbe pelo nome: **alimentar o portal com dado de inteligência**.

## 2 · A tabela

Lei da trava (`TRAVA-DA-INTELIGENCIA.json`): **permite** «ler o código de inteligência que já
exista», «preservar histórico e documentos», «corrigir um defeito que ameace dados», «medir o que
a inteligência futura vai esperar da coleta»; **impede** «desenvolvimento NOVO de inteligência»,
«ligar sinais», «pontuação e recomendação», «alimentar o portal com dado de inteligência»,
«ativar Field Voices ou Opportunity Radar».

### 2.1 · Os 16 que MUDARAM

| # | ficheiro | commit(s) | o que mudou → comportamento | lei | classe | linha que prova |
|---|---|---|---|---|---|---|
| 1 | `coleta/instagram_coleta.py` | `3fc3d1a9` SCRAP-OWNER-01 | passa a autorização de gasto da coleta paga ao dono único do Scrap; não toca em sinal | corrigir defeito que ameaça dados (gasto sem dono) | **CONSERTO PERMITIDO** | `+            autorizacao=autorizacao,` |
| 2 | `italia-portale/audit/casa-gate.mjs` | `c24ea78a` | o portão passa a correr em Windows, segue o registo novo e deixa de acusar um quantificador de regex; ganha controlo negativo | portão mais honesto | **CONSERTO PERMITIDO** (entrou no mesmo commit que a superfície nova) | `+import { chromium } from 'playwright-core';` |
| 3 | `italia-portale/audit/casco/release-gate.mjs` | `c24ea78a` | pode provar os bytes publicados em vez do disco de trabalho | medir | **CONSERTO PERMITIDO** | `+const SPECCHIO = process.env.SINTONIA_MIRROR \|\| null;` |
| 4 | `italia-portale/audit/checks.mjs` | `c24ea78a` | cria guardiões para dois contadores novos no menu — Radar Futuro e Label Intelligence; pares de rótulo 2030 → 5402 | ativar Opportunity Radar / alimentar o portal | **AVANCO PROIBIDO** | `+    ((m.ctx.ITALY_CASA \|\| {}).RADAR_FUTURO \|\| {}).RENDERIZAVEIS,` |
| 5 | `italia-portale/audit/meeting-gate.mjs` | `c24ea78a` | a causa é conserto de leitura (o acento de «MODALITÀ» escondia a secção de uso); o efeito é um caso a mais publicável (5 → 6) | conserto **e** mais inteligência no portal | **DECISÃO DO DONO REAL** | `+  if (shown.length !== 37) bad.push(…VALIDATION_REQUIRED cases reachable…)` |
| 6 | `superficie/it_casa_dados.py` | `150ac321` reconciliação S2A | tira do navegador o texto da lei de relevância (2 342 bytes) e deixa só o sha256 | remove inteligência exposta | **CONSERTO PERMITIDO** | `+           'LEGGE_SHA256': lei_sha,` |
| 7 | `regras/italy_contracts.mjs` | 11 commits (`63169df3`, `6e01e55f`, `8ae62ec7`, …) | contratos de coleta: rotas, identidade de documento, dono canónico, fontes retiradas por decisão, 14 → 186 contratos; nenhuma nota nem ordem | é coleta; congelado só por conter a palavra | **FALSO POSITIVO DO MEDIDOR** | `+    DISCOVERY_METHOD: "listagem de videos do canal pela capacidade ja provada youtube.channel.discovery",` |
| 8 | `regras/sensor_coleta.py` | 7 commits (`3fc3d1a9`, `28abe6f4`, `f9364fc0`, …) | troca o ator pago pela capacidade do Scrap, não repete POST (não paga duas vezes), mede quota | coleta | **FALSO POSITIVO DO MEDIDOR** | `+    vezes = 1 if metodo.upper() in ('POST', 'PUT', 'PATCH', 'DELETE') else tentativas` |
| 9 | `regras/sensor_medir.py` | `079dd155`, `75d3a97d`, `f9364fc0` | o lugar do facto casava pedaço de palavra (37 de 59 lugares declarados, segundo o commit) — corrigido com fronteira de palavra | coleta; e conserto de defeito que falseava dados | **FALSO POSITIVO DO MEDIDOR** | `+    return re.search(_FRONTEIRA % r'\s+'.join(partes), texto) is not None` |
| 10 | `italia-portale/client/adama-relevance.js` | `c24ea78a` (porta `8b590a55`, 07/09: «o radar passa de 13 a 17 oportunidades»); `150ac321` só fim de linha | 4 casos passam de SEGNALI para OPPORTUNITA | pontuação / alimentar o portal | **AVANCO PROIBIDO** | `+  "OPPORTUNITA": 17,` |
| 11 | `italia-portale/client/italy-app-model.js` | `c24ea78a` (porta `2d1b07f2`) | a ficha dizia «principio attivo: non noto» com o dado existente; passa a mostrar a palavra do rótulo; sem nota nem ordem nova | corrigir defeito que ameaça dados (tela que mentia) | **CONSERTO PERMITIDO** | `+        cropOnLabel: r.cropOnLabel, target: r.target, targetAsWritten: r.targetAsWritten,` |
| 12 | `italia-portale/client/italy-casa.js` | `c24ea78a`; `150ac321` | ficheiro gerado; os números de oportunidade mudam: OPPORTUNITA 13 → 17, CLIENT_ACT_NOW 5 → 6, PRIORITA_COMMERCIALE 26 → 27, SEGNALI 8 → 4 (diff bruto 16 313/15 450 linhas; sem fim de linha e espaços, ~2 503) | pontuação / alimentar o portal | **AVANCO PROIBIDO** | `+  "PRIORITA_COMMERCIALE": 27,` |
| 13 | `italia-portale/client/italy-handoff-v21.js` | `c24ea78a` | pacote V21 regerado: ligações de rótulo 2 030 → 5 402, provas das 43 oportunidades mudam de endereço; o ficheiro guarda texto como índices numa tabela, e o diff por linha não mostra se o sentido mudou | — | **NAO SEI** | `-   BUILD_ID  V21-06c6421d001ea52a` |
| 14 | `italia-portale/client/italy-i18n.js` | `c24ea78a` (porta `65d0de42` «Label Intelligence…» e `87dadd89` «Cercare l'opportunità…») | +272 linhas só de acréscimo: o texto inteiro de uma tela nova (Label Intelligence, com item no menu) e uma busca nos cartões do Radar | desenvolvimento novo / Opportunity Radar | **AVANCO PROIBIDO** | `+    radarSearchPh: 'Filtra: coltura, prodotto, avversita, regione…',` |
| 15 | `italia-portale/client/meeting-intelligence-snapshot.js` | `c24ea78a` | nova fotografia da «ÚNICA fonte de inteligência da interface»: SALES_READY 5 → 6, PUBLISHABLE 5 → 6, VALIDATE_NOW 3 → 4, WATCH 22 → 21 | alimentar o portal com dado de inteligência | **AVANCO PROIBIDO** | `+   SOURCE_HEAD fb96f49d · BUILD_ID V21-ef6e7e5f37eaa6e6 · MEETING_CUTOFF 2026-09-07T19:23:48Z */` |
| 16 | `italia-portale/client/meeting-surface.js` | `c24ea78a` (porta `0df93115`) | ~20 linhas: passa a mostrar a lacuna de lugar que já existia no dado e a chave do ícone ADAMA; sem sinal nem nota | preservar/mostrar o NÃO SEI (contrato de design) | **CONSERTO PERMITIDO** | `+      missingGeo: labList((c.WHAT_IS_MISSING \|\| []).filter((k) => GEO_GAP.has(k)), lang),` |

### 2.2 · Os 5 NOVOS

| # | ficheiro | commit(s) | o que é → comportamento | lei | classe | linha que prova |
|---|---|---|---|---|---|---|
| 17 | `docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json` | `e8b87f24` (14/09) C-INT-OBJECT-MODEL-01; `d2b5cb9c` (14/09) C-INT-PILOT-01 | modelo de objetos; não calcula nada, mas chama-se contrato e o 2.º commit regista um motor novo | a trava proíbe CONTRACT novo; a Bíblia (promovida a 14/09) autoriza a §32 | **DECISÃO DO DONO REAL** | `"O QUE ESTE FICHEIRO NAO FAZ: nao implementa runtime, nao persiste nada, nao toca a Collection, nao abre o Portal."` |
| 18 | `italia-portale/audit/superficie-visivel.mjs` | `c24ea78a` | régua de auditoria: conta o que o portal desenha (`VALUE_EXISTS = YES e VISIBLE = NO → NAO ESTA INTEGRADO`); idêntica byte a byte à de 07/09 | medir | **CONSERTO PERMITIDO** | `VALUE_EXISTS = YES  e  VISIBLE = NO   ->  NAO ESTA INTEGRADO.` |
| 19 | `italia-portale/client/italy-label-intelligence.js` | `c24ea78a` | dados da Label Intelligence **desenhados** na tela de produção (`portale.html:54` carrega o script; `:8907` usa-o); conteúdo idêntico ao de 07/09, e declara `"ACTION":"NOT_EMITTED_BY_THIS_TOOL"` | alimentar o portal — mas não é desenvolvimento novo | **DECISÃO DO DONO REAL** | `portale.html:8907: if (window.ITALY_LABEL_INTELLIGENCE) {` |
| 20 | `research/intelligence/DATA-DEMAND-MATRIX-ITALY.json` | `b8c23372` (14/09) | estudo medido: falta a chave ISSUE_ID, 6 de 12 cruzamentos impossíveis; entrou no censo só por ter «SCHEMA» no início | «medir o que a inteligência futura vai esperar da coleta» | **FALSO POSITIVO DO MEDIDOR** | `"ESPECIE": "ESTUDO MEDIDO — NAO IMPLEMENTA, NAO COLETA, NAO REDESENHA",` |
| 21 | `system-map/data/architecture.declared.json` | 219 commits; as palavras vieram de `c328086c` (14/09) | a declaração do System Map; marcas fortes 0 em B e 0 em H; OPPORTUNITY 0 → 1 e SCORE 0 → 1, ambas em frases que explicam (uma delas avisa **contra** dar nota) | não é inteligência | **FALSO POSITIVO DO MEDIDOR** | `"why_here": "Este cartao carregava TRES objetos do modelo debaixo do nome de um: OPPORTUNITY, FINDING e CLAIM_DOMAIN_JUDGMENT.` |

## 3 · ⚠️ O que NÃO está nos 21 e devia estar: o motor da Intelligence

`motor/corrida_da_inteligencia.py` **não existia** na fotografia e foi criado a 14/09
(`d2b5cb9c`, C-INT-PILOT-01), com o teste `tests/test_a_primeira_corrida_da_inteligencia.py`.
É código que corre (o `INTELLIGENCE_RUN` mínimo). O censo classifica-o como
**`MENCAO_FRACA_APENAS`** — porque a espécie sai das «marcas fortes», e o motor não usa
nenhuma (ele próprio escreve «NAO PRODUZ FINDING. NAO PRODUZ OPPORTUNITY. NAO PONTUA NADA.»).

É o **terceiro ponto cego** do vigia, e não foi consertado aqui (o conserto pedido era o da
fotografia): **a espécie é decidida pela palavra, e código de inteligência escrito sem as
palavras proibidas passa por «menção fraca».**

E toca no meu próprio plano: o plano da §32 (`intelligence-bc1-v1`) usa este motor. A §32 da
Bíblia V0.3, promovida a 14/09, foi a missão que o criou, e a Bíblia diz que a §32 continua
sujeita à trava. **Decisão do dono real**: o motor é a obra autorizada da §32 (e fica
registada como exceção escrita), ou é implementação nova sob trava `NAO`.

## 4 · Perguntas ao dono (só as que a tabela abriu)

1. «Escrito a 07/09 noutro ramo, entrado na produção a 15/09» conta como desenvolvimento novo?
   Muda a natureza dos 5 AVANCO do portal (não muda que alimentam o portal).
2. `meeting-gate.mjs`: o conserto do acento vale o caso publicável a mais?
3. `INTELLIGENCE-OBJECT-MODEL-V1.json` e `motor/corrida_da_inteligencia.py`: obra da §32 com
   exceção escrita, ou violação?
4. `italy-label-intelligence.js`: a Label Intelligence fica na tela de produção?
5. `italy-handoff-v21.js`: precisa de uma leitura com o dicionário de índices para sair de NAO SEI.
