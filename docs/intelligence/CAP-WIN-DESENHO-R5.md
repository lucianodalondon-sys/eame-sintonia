# CAP-WIN — DESENHO DE PONTA A PONTA (NÃO IMPLEMENTADO) · EXPERIMENTAL / NAO_PARA_CLIENTE

D100, conserto (3) · D100-b/L6: a espinha G0-G6 é a ordem das dependências, e a CAP-WIN vem primeiro.
Autoridades: Bíblia V0.3, `CAP-WIN` (linhas 1795-1817), INT-LAW-091/100-105/070-077/084/030; PANORAMA §21 e §24.
Sonda medida sobre a cópia R5: `EXPD78-R5-20260927T125639Z/SONDA-CAP-WIN-ARIF-APOL.txt`.

```text
ESTADO             DESENHO — nenhuma linha de runtime escrita; nenhum objeto CROP_WINDOW produzido
RESPOSTA ESPERADA  NO_DEFENSIBLE_ACTION_YET no corte vertical (e isso é o SUCESSO do teste)
```

## 1 · O contrato (da Bíblia, sem acréscimo)

```text
PERGUNTA    nesta cultura e nesta região, qual é a janela em que agir ainda faz diferença?
ENTRADA     COLLECTION_FACT (fenologia · clima · rótulo) · CROSSING
SAÍDA       ANALYTIC_JUDGMENT de janela, com estado temporal  (no pote: espécie CROP_WINDOW)
JOIN_KEYS   CROP_ID × REGION_ID × PHENOLOGY_STAGE × TIME_WINDOW   (+ ISSUE_ID: a janela é de um problema)
HARD_GATES  INT-LAW-100..105 · INT-LAW-104 (ACT_NOW exige janela compatível)
MUST_NOT    data de calendário como janela · janela de um ano como janela deste
```

## 2 · A estrada, peça a peça — o que existe e de quem é

| # | etapa | peça | existe? | owner | decisão |
|---|---|---|---|---|---|
| 0 | READY com CROP_ID, ISSUE_ID, REGION_ID, FASE e FACT_TIME **em campo** | Sala (migration 033: `janela_declarada.CULTURA/FASE/JANELA`) | o **contrato** existe; os **valores** chegam `NAO SEI` nos 6 T3 | Collection | **requisito** `CROP_ISSUE_EM_CAMPO` (R5) |
| 1 | intake: todo READY entra, com estado temporal | `motor/corrida_da_inteligencia.py` G0/v4 `a5db06c4` | **SIM** (R5) | Intelligence | usar |
| 2 | orações → tipo de janela (WINDOW_DEFINED) | `scripts/v21_janelas.py` `tipos_da_oracao` @ `85df96f7` (8 tipos: CALENDAR, PHENOLOGY, PREHARVEST, THRESHOLD, WEATHER_TRIGGERED, PEST_STAGE, ADMINISTRATIVE, RULE_DELEGATED_TO_FARM) | SIM, **legado V21** (lê `DESIGN-INGEST/CURRENT-FIELD-SIGNALS.json`, não a Sala) | V21 (legado) | **portar a regra, não o ficheiro** (PANORAMA §24): um módulo novo que recebe **orações de um READY por par CROP_ID × ISSUE_ID em campo** |
| 3 | «a condição está satisfeita agora?» (WINDOW_OPEN_NOW) | `v21_janelas.aberta_agora` (YES / NO / UNKNOWN + **método**: `FONTE_NAO_DECLARA_A_MEDICAO...`, `FRASE_QUALITATIVA_NAO_RESPONDE...`) | SIM, legado | idem | portar, com os testes que ele já tem como casos |
| 4 | atribuir oração → par cultura × praga | `v21_necessidade.atribuicoes` (léxico `v21_normalizar`) | SIM, legado, **por texto** | idem | **NÃO portar como identidade**: atribuir por texto é fabricar CROP_ID (INT-LAW-084). Só serve de **sonda** do requisito (prova de que o valor está no bruto) |
| 5 | independência das fontes que falam do mesmo par | `motor/grafo_de_dependencia.py` @ `eb3a7b1d` (`nuvem-independencia-v1`) | SIM, **noutro ramo**, lido | Intelligence (outro ramo) | integrar no motor G0/v4 (o ramo parte de `60faa7cb` e perderia D11/D14/D15) |
| 6 | contradição | — | **NÃO** (`CONTRADICOES = NOT_MEASURED`) | Intelligence | construir: é obrigatória antes de qualquer juízo (L5.7) |
| 7 | juízo de janela | — | **NÃO** | Intelligence | novo: regras abaixo (§4) |
| 8 | pote → casco | `montar_pote_r5.py` (compartimento `windows`) | SIM | Intelligence | já tem as regras: CROP_WINDOW só entra com CAP-WIN em `CAPACIDADES_EXECUTADAS` e os 6 campos |

## 3 · O corte vertical: ARIF × APOL, mosca-da-oliveira, Puglia, semana 38 — medido na R5

| | APOL (IT-T3-010) | ARIF n.º 37 (IT-T3-008) | ARIF n.º 38 (IT-T3-008) |
|---|---|---|---|
| SALA_CHAVE | `XX-T3-2026-09-18-134205-772b57c43c0130fe#0` | `XX-T3-2026-09-18-171937-6f76511ca75100a5#0` | `IT-T3-2026-09-20-110656-6e4ffc27a86c5269#0` |
| período **escrito** | «14/09/2026 - 20/09/2026» | «09 - 15 settembre 2026» | «16 - 22 settembre 2026» |
| FACT_TIME no READY | **NAO SEI** → `UNKNOWN_WINDOW` | **NAO SEI** → `UNKNOWN_WINDOW` | 2026-09-07/13 → `ANCORADO` |
| cultura/praga em campo | NAO SEI / campo vazio | NAO SEI | NAO SEI |
| área escrita | comprensori BR e LE (Brindisi, Lecce) | Puglia por área (ex.: «TERRITORIO ESCLUSO GARGANO») | idem |
| o que a fonte diz | «non si sono rilevate raggiungimenti o superamenti della **soglia di intervento**»; «**non si ritiene giustificata** l'esecuzione di un trattamento» | «poche catture ... **al disotto delle soglie di intervento**» | idem; zona costeira do Gargano com «aumento delle catture» |
| V21 WINDOW_DEFINED | `THRESHOLD_WINDOW` (soglia 4-5% punture fertili) | `THRESHOLD_WINDOW` | `THRESHOLD_WINDOW` |
| V21 WINDOW_OPEN_NOW | UNKNOWN · `FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE` | UNKNOWN · idem / `FRASE_QUALITATIVA...` | idem |

**Achado da sonda (defeito do legado, antes de portar):** a APOL escreve a medição por extenso («non si sono rilevate
raggiungimenti o superamenti della soglia»), e o V21 responde que a fonte **não declara** a medição. A resposta
`UNKNOWN` fica certa; a **razão** fica errada. É o mesmo tipo de defeito que o próprio V21 registou para o Veneto
(«razão errada no cartão é mentira pequena»). A negação da ultrapassagem da soglia precisa de regra própria →
`WINDOW_OPEN_NOW = NO`, método `FONTE_DECLARA_SOGLIA_NAO_ATINGIDA`. Vira **caso de regressão** quando a CAP-WIN for implementada.

**Independência:** o grafo conta 2 originadores (apol.it, agrometeopuglia.it) e diz «CONVERGE». **Mas** os dois textos
partilham **82 sequências de 10 palavras** (as instruções de tratamento: esche proteiche, deltametrina, acetamiprid...),
que vêm do **Disciplinare di Difesa Integrata Puglia 2026**. Por isso:

- a **regra** (soglia 4-5 %, que substâncias usar) é **UMA origem**, e conta 1;
- a **observação** («catture basse, soglia não atingida») é de redes de monitorização diferentes (APOL por comprensorio,
  ARIF por área). É independente **só se** a Collection declarar as redes; hoje fica `NAO SEI`, com provável 2.

É exatamente o INT-LAW-070..077: dois domínios não bastam para dois apoios independentes.

## 4 · As regras do juízo (a escrever depois, com testes antes)

```text
W0  entrada = pares (CROP_ID, ISSUE_ID, REGION_ID) EM CAMPO no READY. Sem par em campo -> NOT_POSSIBLE (INT-LAW-091),
    com o requisito que o desbloqueia. Nunca a partir do texto.
W1  TIME_WINDOW = FACT_TIME do READY (período do boletim SÓ se a Collection o ligar ao facto, D69). PUBLICATION ≠ FACT.
W2  WINDOW_DEFINED = tipo(s) da condição (regra portada do V21, 8 tipos). ADMINISTRATIVE nunca é janela agronómica.
W3  WINDOW_OPEN_NOW ∈ {YES, NO, UNKNOWN} + MÉTODO verdadeiro (os 4 silêncios do V21 + SOGLIA_NAO_ATINGIDA).
    Qualitativo não responde a quantitativo, salvo equivalência declarada pela fonte.
W4  ESTADO TEMPORAL: CURRENT (fim da janela ≥ hoje - N dias, N fixado ANTES de olhar) · STALE (TRUE-BUT-STALE) · UNKNOWN.
W5  INDEPENDÊNCIA por par: originadores do grafo, MENOS o texto normativo partilhado (a regra conta uma vez).
W6  CONTRADIÇÃO: dois WINDOW_OPEN_NOW opostos no mesmo par, região e semana -> CONFLICTING_EVIDENCE, as duas visíveis.
W7  SAÍDA (CROP_WINDOW = ANALYTIC_JUDGMENT): CROP_ID, ISSUE_ID, REGION_ID, TIME_WINDOW, WINDOW_DEFINED, WINDOW_OPEN_NOW,
    MÉTODO, ESTADO_TEMPORAL, APOIOS (independentes / da mesma regra), CONTRADIÇÕES, LIMITAÇÕES, lineage até ao RAW.
W8  ACT_NOW só com WINDOW_OPEN_NOW = YES ∧ CURRENT ∧ ≥ 2 apoios independentes na OBSERVAÇÃO ∧ 0 contradições abertas.
    Caso contrário: NO_DEFENSIBLE_ACTION_YET, com o PORQUÊ.
```

## 5 · O que o corte vertical deve responder (resultado esperado, a provar depois)

```text
PAR          CROP_OLIVE × ISSUE_OLIVE_FLY × Puglia (BR, LE; ARIF por área) × semanas 37-38/2026
DEFINIDA     THRESHOLD_WINDOW — 4-5 % punture fertili (olive da olio); prime punture (da tavola)
ABERTA AGORA NO — as duas fontes declaram a soglia não atingida (APOL: «non si ritiene giustificata»)
             (Gargano costeiro: «aumento delle catture» -> subárea com UNKNOWN, não contradição do todo)
APOIOS       regra: 1 (disciplinare partilhado) · observação: 2 prováveis (NAO SEI até a Collection declarar as redes)
RESULTADO    NO_DEFENSIBLE_ACTION_YET — «monitorizar; tratamento não justificado nesta semana»
```

Isto prova o que o PANORAMA §21 pede: **ler, ligar, contradizer a expectativa comercial, dizer não e explicar porquê.**

## 6 · O que falta para correr, por ordem (nada disto se faz no casco)

1. **Collection** (requisitos R5):
   - `CROP_ISSUE_EM_CAMPO` nos 5 T3;
   - `FACT_TIME` da APOL, com o período escrito;
   - área (REGION_ID/PROVINCE_ID) em campo.
2. **Intelligence**:
   - integrar o grafo no motor G0/v4;
   - portar W2/W3 do V21, com os testes dele e o caso APOL (razão `SOGLIA_NAO_ATINGIDA`);
   - escrever W4-W8 com os testes antes;
   - offline eval nos 3 itens do corte, com o resultado esperado fixado acima **antes** de correr.
3. **Pote**: `CAPACIDADES_EXECUTADAS["CAP-WIN"]` com versão e run. O portão já exige os 6 campos.

## 7 · O que este desenho NÃO decide

- O limiar N de «CURRENT» (W4): é decisão de regra, tem de ser fixado **antes** de olhar para os dados.
- Se APOL e ARIF são redes de monitorização independentes: a Collection é que declara.
- CAP-SCI e CAP-FIELD vêm depois (D100-b), e CAP-OPP por último.
