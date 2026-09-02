# Espanha — content freeze antes do design

2026-08-30 · `claude/sintonia-eame-collection-es` · 386 testes OK

---

## A correção que valia a rodada inteira

Eu tinha mantido o olivo como `AGIR AGORA` **porque a janela do CUPROXI FLO está aberta**. Janela aberta prova que o produto *pode* ser usado neste estágio. Não prova que há necessidade de aplicar.

Com a última leitura do oeste tendo 77 e 95 dias, a evidência sustenta **verificar o campo** — não aplicar. `CASE_TYPE` = **`VERIFY_FIELD_NOW`**, e os cinco estados agora vivem separados: `FIELD_SIGNAL_STATUS`, `APPLICATION_WINDOW_STATUS`, `MONITORING_NEED` (HIGH), `PRODUCT_ACTION_NEED` (**NOT_KNOWN**), `BUSINESS_ACTION`. O condicional está escrito: `APPLICATION_POSSIBLE_IF_FIELD_CONFIRMS`.

É o erro mais perigoso dos cinco que já cometi neste projeto, porque os outros quatro são de contagem ou de data — um leitor atento pega. Este é de **significado**: cada número continua certo e a conclusão fica errada.

A busca dirigida por leitura pós-junho não achou nada. `FIELD_CURRENTNESS_GAP` = `CONFIRMED_ON_TESTED_SOURCE`. E o que torna a lacuna legível: o RAIF **continuou** amostrando em agosto — Jaén 19/08, Granada 19/08, Córdoba 18/08, Sevilla 17/08. Faltam Huelva e Cádiz especificamente. É ausência de amostragem provincial, não fonte parada.

## O que o texto completo do artigo mudou

Li o artigo inteiro, não o resumo. E ele desmonta o que publiquei na rodada passada.

**Tabela 1 — a geografia real.** Três populações multirresistentes de **Calaf** e **Calonge de Segarra**, província de **Barcelona**, coletadas em 2014-2015. A população suscetível é de **Ballobar, Huesca**. Conferi os três municípios na mesma tabela oficial usada no crosswalk do milho. **Não existe, neste artigo, medição de resistência em Huesca** — a única população de Huesca é a suscetível.

Três geografias que coincidiriam num resumo desatento e não coincidem: afiliação (Lleida) ≠ local do experimento (Lleida) ≠ origem das populações (Barcelona e Huesca).

**A correção.** Eu escrevi que *"o portfólio genérico está onde o mercado foi parar"*. O texto completo diz `"ACCase, ALS AND PSII inhibitors resistance is now widespread"`, e o próprio artigo classifica clortolurón como **PSII, grupo 5**. Seis dos dez registros genéricos da ADAMA por cultura são clortolurón ou metribuzina. Não é a saída: é o terceiro grupo comprometido.

**E a Tabela 2 lista os produtos testados com marca e empresa.** Uma das linhas é `"Clortolurex · Adama Agriculture · Chlortoluron · PS II inhibitor"`. Resultado: MR nas três populações.

**A ressalva que isso obriga, contra o meu próprio impulso de fechar a narrativa:** na **dose de campo** o clortolurón ainda controlou duas das três. `MR` não é "não funciona". Publicar só o MR seria exagerar contra o produto.

Não classifiquei metribuzina nem pendimetalina. O artigo não as classifica e eu não invento grupo.

**Convergência regional: parcial.** A resistência está medida em Barcelona, que não está entre as oito maiores províncias de cereal. A escala está em Burgos, Valladolid, Huesca, Zaragoza. O que liga é a moldura do próprio artigo — *"north-eastern Spain"*, *"grass control was based on chlortoluron for several decades"*. Nomear Huesca como território de resistência seria promover moldura a medição.

## Action Map V2

Seis tipos no lugar do binário: `ACT_NOW` · `VERIFY_NOW` · `PREPARE` · `PLAN` · `WAIT_FOR_INTERNAL_DATA` · `NO_ACTION`.

| tipo | linhas |
|---|---|
| `ACT_NOW` | **1** |
| `VERIFY_NOW` | 3 |
| `PREPARE` | 4 |
| `PLAN` | 4 |
| `WAIT_FOR_INTERNAL_DATA` | 3 |
| `NO_ACTION` | 3 |

**Um único `ACT_NOW` em dezoito linhas**, e é o regulatório do Neptune — interno, não depende do campo nem do mercado. Um sistema que gritasse teria vários.

`COMMERCIAL` é `WAIT_FOR_INTERNAL_DATA` nos três: prepara briefing e verifica com o negócio, nunca recebe instrução externa de venda.

## Congelamento

`SPAIN-HERO-CASES-V1` · `ES-ACTION-MAP-V2` · `ASK-SINTONIA-ACCEPTANCE-ES` (13 perguntas, **frozen**) → agregados em **`SPAIN-DEMO-CONTENT-V1`**, com `EVIDENCE_MAP`, `UNKNOWN_MAP` e a lista do que a demo **não pode afirmar**.

`SPAIN_CONTENT_FREEZE_READY` = **YES** pelos oito critérios. `NEXT_PHASE` = design / protótipo de portal. **Nada foi construído.**

## Regressões

Sete, cada uma sobre um erro real: `FILE_DATE != FIELD_OBSERVATION_DATE` · `VARIANT_ROWS != UNIQUE_NATIONAL_REGISTRATION` · `21 != 23` · `substring "IRAC" != declaração IRAC` · `OPEN_WINDOW != CURRENT_NEED` · `ADJACENCY != COVERAGE` · `AFFILIATION != STUDY_GEOGRAPHY != SAMPLE_GEOGRAPHY`.

Os 6 testes novos quebraram outros 7: o repositório exige que o número publicado nos documentos venha da suíte real. 380 → 386 em oito arquivos.

## Paralelas

Itália avançou (`b8c0298` → `06b0165`): o ISTAT destravou a geografia e moveu o caso da videira de lugar, e o portfólio elegível inteiro vence antes da próxima janela obrigatória. Registrado, não consumido, sem merge.

`EAME_CROSS_MARKET_READY` = **NO**, inalterado. O avanço italiano foi em videira e em vencimento de portfólio — não em milho nem em cereal, que são os dois pontos de contato possíveis.

O paralelo que **não** vira caso: os dois países acharam achados de *tempo regulatório* em registros nacionais diferentes. É o mesmo tipo de pergunta, não o mesmo caso.
