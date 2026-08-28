# MATRIZ DE CRUZAMENTOS — SINTONIA EAME

O valor do SINTONIA não está em nenhuma fonte isolada: está no que **duas ou mais fontes
juntas** revelam e nenhuma delas revela sozinha.

> **Não afirmar cruzamento apenas porque semanticamente parece interessante.**
> Clima + doença "parece" cruzar. A pergunta real é: **qual chave os une?**

**Estado:** MISSÃO 02 em curso — **2 COMPROVADOS, 1 PARCIAL**.
**Última atualização:** 2026-08-28

---

## AS DUAS PERGUNTAS

Para cada cruzamento candidato:

1. **A + B realmente podem ser unidos?**
2. **Qual chave permite uni-los?**

Sem chave explícita e verificada, o cruzamento não é COMPROVADO. As chaves candidatas
costumam ser: geografia (região/NUTS/coordenada), tempo (data/janela), cultura, alvo
(praga/doença), substância ativa, produto, organização, pessoa, identificador de documento.

Atenção ao alinhamento das chaves: duas fontes podem ambas ter "região" e mesmo assim não
cruzar, se uma usa NUTS-2 e a outra departamento, ou se uma é semanal e a outra mensal.
**Granularidade incompatível é motivo legítimo de NÃO COMPÕE.**

---

## CLASSIFICAÇÃO

| Classe | Significado |
|---|---|
| **COMPROVADO** | Cruzamento executado sobre dado real, com chave identificada e exemplo preservado. |
| **POSSÍVEL MAS NÃO TESTADO** | Chave plausível e identificada, mas ninguém executou ainda. |
| **PARCIAL** | Une de fato, mas com cobertura ou granularidade limitada — e o limite está medido, não estimado. |
| **NÃO COMPÕE** | Testado e não une — chave ausente, granularidade incompatível, tempos irreconciliáveis. Exige motivo escrito. |
| **NÃO SEI** | Não foi possível avaliar. |

---

## FICHA DO CRUZAMENTO

```
CROSSING_ID:
COMPONENTS:         # A + B (+ C...)
SOURCES:            # SOURCE_IDs envolvidos
KEY:                # a chave que efetivamente une — ou por que não existe
GRANULARITY_MATCH:  # geografias e tempos são compatíveis?
WHAT_IT_REVEALS:    # o que aparece que nenhuma fonte sozinha mostra
REAL_EXAMPLE:
CAPABILITY:         # que capacidade este cruzamento habilita
CLASS:              # COMPROVADO | POSSÍVEL MAS NÃO TESTADO | NÃO COMPÕE | NÃO SEI
```

---

## CRUZAMENTOS CANDIDATOS (do briefing)

Listados como **candidatos a testar**, não como afirmações. Todos partem em `NÃO SEI`.

| ID | Cruzamento | Classe |
|---|---|---|
| X-001 | CLIMATE + REGION + CROP + DISEASE ALERT | NÃO SEI |
| X-002 | RESEARCHER + PAPER + CROP + PROBLEM | NÃO SEI |
| X-003 | COMPETITOR + PRODUCT + CROP + COMMUNICATION | NÃO SEI (camada COMMUNICATION não investigada) |
| X-004 | REGULATORY + ADAMA PORTFOLIO + CROP + PEST | **COMPROVADO (FR)** |

> X-004 **foi resolvido para a França** sem dado interno: o registro oficial francês nomeia
> ADAMA FRANCE SAS como titular. Ver o registro abaixo. A camada de portfólio **comercial**
> continua fora de alcance.

---

## REGISTRO DE CRUZAMENTOS TESTADOS

### X-004 · REGULATORY + ADAMA PORTFOLIO + CROP + PEST — **COMPROVADO (França)**

```
CROSSING_ID:        X-004
COMPONENTS:         REGULATORY (autorização nacional) + PORTFOLIO (titular) + CROP + PEST
SOURCES:            FR-T4-001 (ANSES E-Phy)
KEY:                numero AMM (produto) → identifiant usage, decomposto em
                    Cultura * TipoTratamento * Alvo. O titular vem do mesmo registro.
                    Chave interna à fonte: o cruzamento acontece dentro do registro oficial.
GRANULARITY_MATCH:  SIM — todos os componentes vivem na mesma granularidade (país, produto,
                    uso). Não há descompasso geográfico nem temporal a reconciliar.
WHAT_IT_REVEALS:    Que a ADAMA pode legalmente atuar em 504 usos autorizados na França e
                    exatamente em quais pares cultura × alvo — e onde cada concorrente está.
REAL_EXAMPLE:       ADAMA FRANCE SAS: Vigne×Mildiou 17 usos, Vigne×Black rot 13,
                    Traitements généraux×Limaces 18, Blé×Septoriose 6.
                    Evidência: data/samples/FR-T4-001/FR-T4-001-adama-crop-target.json
CAPABILITY:         CAP-003, CAP-004, CAP-005
CLASS:              COMPROVADO
```

**As oito perguntas (§7):**
A · sujeito de A: o **produto autorizado** (nº AMM).
B · sujeito de B: o **uso autorizado** (cultura × alvo).
C · chave: nº AMM, ligação nativa dentro do registro.
D · granularidade: compatível — ambos nacionais e por produto.
E · período: compatível — mesma versão semanal do dataset.
F · **afirma fato**, não correlação: é o texto do ato administrativo, não inferência.
G · pergunta que passa a ser respondida: *"o que a ADAMA — ou o concorrente X — pode
legalmente vender na França, em que cultura e contra que alvo?"*
H · erro fácil de cometer: ler **presença regulatória** como **posição de mercado**.
Ver o RED TEAM em CAP-005.

**Ressalva sobre a camada PORTFOLIO:** o que foi cruzado é o portfólio **registrado**
(público). O portfólio **comercial** da ADAMA EAME (vendas, prioridade, pipeline)
permanece `NÃO TESTÁVEL COMPLETAMENTE` — não é público e não foi fornecido. Não foi inventado.

### X-005 · COMPETITOR + CROP + PEST via registro oficial — **COMPROVADO (França)**

```
CROSSING_ID:        X-005
COMPONENTS:         COMPETITOR (titular) + CROP + PEST + ACTIVE INGREDIENT
SOURCES:            FR-T4-001
KEY:                titulaire → nº AMM → identifiant usage; substância ativa no mesmo registro
GRANULARITY_MATCH:  SIM
WHAT_IT_REVEALS:    Um radar competitivo apoiado em ato administrativo, não em clipping:
                    quem tem direito de uso em cada combate agronômico, com que molécula.
REAL_EXAMPLE:       Vigne × Mildiou(s) — ADAMA 17, NUFARM 11, BAYER 8, UPL 7, SYNGENTA 5,
                    CORTEVA/DOW 3, BASF 2 (usos autorizados).
CAPABILITY:         CAP-005
CLASS:              COMPROVADO (para "usos autorizados"; NÃO para participação de mercado)
```

**Limite duro:** este cruzamento mede **direito de uso registrado**. Ele **não compõe** com
market share, faturamento ou adoção — essas variáveis não estão na fonte. Ver §8 da missão:
correlação não vira causalidade, e presença regulatória não vira liderança.

### X-006 · EU ACTIVE SUBSTANCE + NATIONAL PRODUCT AUTHORIZATION — **PARCIAL (testado, com limite medido)**

```
CROSSING_ID:        X-006
COMPONENTS:         EU-T4-001 (ato da UE por substância) + FR-T4-001 (produto nacional)
KEY CANDIDATA:      nome da substância ativa e/ou nº CAS.
                    E-Phy traz `substance_active_utf8.csv` com "Numero CAS" (1.337 linhas);
                    o ato da UE traz CAS no anexo (ex.: ácido pelargônico, CAS 112-05-0).
                    O CAS é, portanto, chave candidata forte — mas o CAS no ato da UE está
                    em texto corrido do anexo, não em campo estruturado.
GRANULARITY_MATCH:  ATENÇÃO — descompasso de sujeito: a UE regula SUBSTÂNCIA (nível UE);
                    a França autoriza PRODUTO (nível nacional). A relação é 1:N e a
                    expiração europeia não é a data de retirada do produto francês.
WHAT_IT_WOULD_REVEAL: quais produtos autorizados na França dependem de uma substância cuja
                    aprovação europeia expira em data conhecida — antecipação de perda.
CLASS:              PARCIAL
REAL_EXAMPLE:       CELEX 32026R1353 (15/06/2026) → CAS 70630-17-0 → E-Phy "Metalaxyl-M"
                    (INSCRITE) → 9 produtos autorizados na França → destes, 1 é da ADAMA:
                    PANDERO GOLD, AMM 2010398 (folpel 400 g/kg + metalaxil-M),
                    uso Vigne*Trt Part.Aer.*Mildiou(s), 2,0 kg/ha, autorizado.
                    Evidência: data/samples/X-006-eu-cas-to-ephy.json
```

**TESTADO — o que funcionou.** A cadeia completa fecha, ponta a ponta e de forma automática:

```
ato da UE (CELEX) → CAS → substância no E-Phy → produtos franceses → titular → cultura × alvo
```

**Por que PARCIAL e não COMPROVADO — os limites medidos, não estimados:**

| Medida | Resultado | Consequência |
|---|---|---|
| Atos da UE com CAS extraível do texto | **3 de 6** | Atos que só alteram o Reg. 540/2011 (prorrogação de período) citam a substância **pelo nome**, sem CAS no corpo. Para esses, a chave CAS não existe. |
| Casamento CAS → E-Phy, quando havia CAS | **3 de 4** | O CAS que falhou (67701-09-1) é de uma fração de ácidos graxos, não da substância principal do ato. |
| Substâncias do E-Phy que trazem nº CAS | **621 de 1.338** | Menos da metade. Para o resto, o casamento teria de ser por nome — e nome varia entre línguas e grafias. |

**Conclusão honesta:** a chave CAS é **real e funciona**, mas cobre apenas parte do universo.
Um cruzamento de produção precisaria de uma segunda chave (nome normalizado da substância)
e de medição da taxa de acerto dessa segunda chave. Enquanto isso não for feito, qualquer
número derivado deste cruzamento é **incompleto por construção** e assim deve aparecer.

**As oito perguntas (§7):**
A · sujeito de A: a **substância ativa**, no nível da União.
B · sujeito de B: o **produto comercial**, no nível nacional.
C · chave: **nº CAS** (verificada, cobertura parcial medida acima).
D · granularidade: **incompatível por natureza** — 1 substância : N produtos. O cruzamento
só é legítimo na direção substância → produtos, nunca produto → "situação europeia".
E · período: compatível, mas as datas **não** são a mesma coisa (ver H).
F · **afirma fato** (ambos são atos administrativos), com cobertura parcial.
G · pergunta respondida: *"que produtos autorizados na França — e de quem — dependem desta
substância cuja aprovação europeia tem data conhecida?"*
H · **erro fácil de cometer:** tratar a **data de expiração da aprovação europeia** como
**data de retirada do produto francês**. Não são a mesma data. A expiração europeia abre um
processo de renovação; a retirada nacional tem prazo próprio, com escoamento de estoque.
Confundir as duas produziria um alarme falso com data errada.



### Placar

| Classe | Quantidade |
|---|---|
| COMPROVADO | 2 |
| PARCIAL | 1 |
| POSSÍVEL MAS NÃO TESTADO | 0 |
| NÃO COMPÕE | 0 |
| NÃO SEI | 2 |
