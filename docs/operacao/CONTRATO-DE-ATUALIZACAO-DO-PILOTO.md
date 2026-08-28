# CONTRATO DE ATUALIZAÇÃO DO PILOTO

O que envelhece, com que velocidade, e como se sabe. **Data:** 2026-08-29 · MISSÃO 08

---

## TRÊS CADÊNCIAS QUE NÃO SÃO A MESMA COISA

| | o que é | quem decide |
|---|---|---|
| **SOURCE PUBLICATION CADENCE** | de quanto em quanto tempo a **fonte** publica | a fonte. Nós observamos, não escolhemos |
| **CHECK CADENCE** | de quanto em quanto tempo **nós olhamos** | nós |
| **PRODUCT SLA** | o que é **prometido** a quem usa | **decisão futura — não existe** |

> *"Verificar semanalmente"* **não** significa *"garantimos atualização semanal"*.
> Nenhuma linha deste documento é um SLA. Um SLA exige monitoramento, alerta de falha e
> alguém de plantão — nada disso existe hoje.

---

## POR COMPONENTE `PILOT READY`

`FRESHNESS LABEL` é o que aparece junto do número. `STALE CONDITION` é quando ele deixa
de poder ser apresentado como atual.

### Regulatory review · Molecule watch · Cross-market por molécula

| | |
|---|---|
| **SOURCE** | FR-T4-001 · IT-T4-001 · ES-T4-005 · EU-T4-001 |
| **CADÊNCIA DA FONTE** | FR **semanal** (declarada pelo catálogo) · ES **semanal** (a home diz a data e hora) · IT **NÃO SEI** — o nome do arquivo é datado mas a periodicidade não é declarada em lugar nenhum · EU **contínua** |
| **COMO SABEMOS** | FR: `last_update` da API · ES: o texto da home + `Fecha` do export · IT: **comparando nomes de arquivo entre execuções** · EU: o CELEX é imutável |
| **CHECK CADENCE RECOMENDADA** | **semanal** para FR e ES; **semanal** para IT (custa uma requisição à página); EU sob demanda |
| **FRESHNESS LABEL** | `dados de <data da versão>` — nunca "atualizado" |
| **STALE CONDITION** | mais de **14 dias** sem coleta bem-sucedida numa fonte de cadência semanal |
| **FAILURE BEHAVIOR** | a perna some do resultado com `SOURCE FAILED`. **Nunca** recalcular o total com as pernas restantes |

### Pest pressure ES (CASE-013, CASE-008, CASE-012)

| | |
|---|---|
| **SOURCE** | ES-T3-001 (RAIF) |
| **CADÊNCIA DA FONTE** | **semanal durante a safra**; fora da safra, **NÃO SEI** |
| **COMO SABEMOS** | atributo `generated` na raiz do XML + a data no título do recurso CKAN |
| **CHECK CADENCE RECOMENDADA** | semanal na safra |
| **FRESHNESS LABEL** | `safra 2026, leituras até <FECHA máxima>` |
| **STALE CONDITION** | a última `FECHA` do arquivo tem mais de **21 dias** durante a safra |
| **FAILURE BEHAVIOR** | mantém a série histórica com a data; **não** estende a curva |
| **NOTA** | é a única fonte crítica com **20 anos de história nativa**. Perder uma semana não apaga o passado |

### Science & experts

| | |
|---|---|
| **SOURCE** | EU-T5-001 (OpenAlex) |
| **CADÊNCIA DA FONTE** | contínua e **cumulativa** |
| **COMO SABEMOS** | não há campo de versão — o acervo só cresce |
| **CHECK CADENCE RECOMENDADA** | mensal |
| **FRESHNESS LABEL** | `consulta de <data>` |
| **STALE CONDITION** | não há stale duro: a resposta cresce, não inverte |
| **FAILURE BEHAVIOR** | falha fechado; **GDPR: P-008 continua aberto** |

### Climate **context**

| | |
|---|---|
| **SOURCE** | EU-T2-001 (NASA POWER) |
| **CADÊNCIA DA FONTE** | diária, com **latência de vários dias** |
| **COMO SABEMOS** | a última data com valor na série |
| **CHECK CADENCE RECOMENDADA** | sob demanda |
| **FRESHNESS LABEL** | `série até <data>` |
| **STALE CONDITION** | usar como **contexto** nunca expira; usar como **explicação** já é proibido (X-009) |

### Preço e área

| | |
|---|---|
| **SOURCE** | EU-T10-001 (semanal) · EU-T1-001/002 (Eurostat) |
| **CADÊNCIA DA FONTE** | preço **semanal**; Eurostat **anual, com anos de atraso** |
| **COMO SABEMOS** | a última semana publicada; o último ano com valor |
| **CHECK CADENCE RECOMENDADA** | preço semanal; Eurostat trimestral |
| **FRESHNESS LABEL** | `semana <n>` · `ano <aaaa>` |
| **STALE CONDITION** | preço com mais de 3 semanas |
| **FAILURE BEHAVIOR** | falha fechado |

### Ask Sintonia

| | |
|---|---|
| **SOURCE** | todas as acima |
| **FRESHNESS** | medida pergunta a pergunta em `scripts/ask_sintonia.py::FRESHNESS` |
| **PLACAR** | **19 CURRENT · 14 STRUCTURAL · 2 HISTORICAL**; 16 exigem frescor, 13 não, 6 dependem |
| **STALE CONDITION** | qualquer pergunta `CURRENT + FRESHNESS SIM` cuja fonte esteja stale |
| **NOTA** | **a recusa também envelhece.** 4 recusas (`B08`, `B17`, `B19`, `B33`) deixam de ser corretas quando a fonte abrir — foi o que aconteceu com `B03` e `B24` na MISSÃO 07 |

---

## O QUE NÃO SABEMOS, E FICA `NÃO SEI`

| pergunta | resposta |
|---|---|
| com que frequência o Ministero della Salute republica o CSV? | **NÃO SEI.** O nome é datado; a periodicidade não é declarada |
| o RAIF publica fora da safra? | **NÃO SEI** |
| o MAPA mantém as versões antigas do `dc_web.pdf` em algum lugar? | **NÃO SEI.** A URL é única e o conteúdo é substituído — é por isso que arquivamos |
| quanto tempo uma rota do `regfiweb` sobrevive sem mudar? | **NÃO SEI.** Não é dataset publicado e não há compromisso |

**Nenhuma destas foi preenchida com estimativa.** Uma cadência inventada vira SLA por
acidente na primeira vez que alguém a lê num slide.
