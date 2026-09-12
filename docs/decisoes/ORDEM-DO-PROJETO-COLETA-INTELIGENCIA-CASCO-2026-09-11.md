# DECISÃO DE DIREÇÃO — FECHAR COLLECTION, COLETAR EM ESCALA, DEPOIS INTELLIGENCE, CASCO POR ÚLTIMO

**Data:** 2026-09-11  
**Estado:** DECIDIDO  
**Quem decidiu:** Luciano, dono do projeto  
**Escopo:** SINTONIA EAME  

## O QUE MUDOU

Fica congelada a ordem operacional das próximas macrofases do SINTONIA EAME:

```text
1. TERMINAR TODA A COLLECTION
   ↓
2. INTEGRAR AS CAPACIDADES DE AQUISIÇÃO QUE ESTÃO A EVOLUIR EM PARALELO
   — incluindo SINTONIA SCRAP — SEM CRIAR SEGUNDA ARQUITETURA
   ↓
3. EXECUTAR UMA COLETA GRANDE COM A MÁQUINA FECHADA
   ↓
4. RECONCILIAR / AUDITAR / ADMITIR O MATERIAL E LEVÁ-LO ATÉ READY / SALA DE ESPERA
   ↓
5. SÓ ENTÃO INICIAR INTELLIGENCE
   ↓
6. INTELLIGENCE TOOLS / VALIDATION
   ↓
7. CASCO / PORTAL POR ÚLTIMO
```

## O QUE “TERMINAR TODA A COLLECTION” SIGNIFICA

Não significa “coletar toda a internet”.

Collection fecha quando a máquina canônica consegue, de forma repetível e auditável:

```text
SOURCE / REQUEST
→ ORCHESTRATOR
→ EXECUTOR
→ RUN
→ RAW OBSERVATION
→ STORAGE OBJECT
→ DERIVED
→ STRUCTURED
→ ADMISSION
→ READY
→ SALA DE ESPERA
```

com identidade, procedência, tempo, geografia, lineage, retry, erro, reuso, custo, observabilidade e estados preservados conforme os contratos vigentes.

Código capaz de fazer não basta:

```text
CAN DO != DID DO
MODULE EXISTS != EDGE EXISTS != FLOW EXISTS
```

Antes da coleta grande, a estrada deve estar provada e a conformidade necessária para Collection V1 deve estar medida no HEAD vigente.

## O QUE “COLETA GRANDE” SIGNIFICA

Depois de fechar a máquina, executar uma campanha ampla sobre as fontes e capacidades aprovadas para o escopo EAME vigente, usando o fluxo canônico.

A campanha deve produzir prova operacional real de volume e variedade, não apenas um canário.

Ela deve preservar e reconciliar, quando aplicável:

- REQUEST / plano;
- RUN;
- SOURCE_ID;
- RAW_OBSERVATION_ID;
- STORAGE OBJECT;
- RAW;
- DERIVED;
- STRUCTURED;
- decisões de Admission;
- READY;
- Sala de Espera;
- erros / retries / reuso;
- custos;
- contagens de entrada, saída, perda e unknown;
- lineage e procedência.

A coleta grande não autoriza fabricar identidades, fatos, datas, lugares ou resultados para aumentar cobertura.

## SINTONIA SCRAP EM PARALELO

O SINTONIA SCRAP continua a evoluir em paralelo nesta fase e pode enriquecer as capacidades de aquisição.

Ele continua sendo:

```text
UMA FRENTE ESPECIALIZADA DE AQUISIÇÃO DENTRO DA COLLECTION
```

Não é:

```text
SEGUNDO ORQUESTRADOR GLOBAL
SEGUNDO MODELO DE RUN
SEGUNDO MODELO DE RAW
SEGUNDA ADMISSION
SEGUNDA SALA DE ESPERA
```

O trabalho paralelo do SCRAP só conta como capacidade integrada do SINTONIA quando regressar ao fluxo canônico e preservar os mesmos contratos de RUN, RAW, identidade, procedência, armazenamento, retry, custo, erros e Admission.

Até lá:

```text
SCRAP EVOLUI EM PARALELO
!=
SCRAP JÁ INTEGRADO À COLLECTION
```

## POR QUÊ

A máquina precisa ser provada antes de construir o cérebro que depende dela.

Começar Intelligence sobre uma Collection incompleta criaria consumidores compensando buracos de aquisição, identidade ou Admission. Isso inverteria a arquitetura e faria a Intelligence passar a conhecer detalhes de coleta que pertencem à Collection.

Do mesmo modo, construir o Casco antes da Intelligence estabilizada faria a superfície puxar a arquitetura para trás e incentivar dados, cruzamentos ou respostas inventados apenas para preencher telas.

A ordem escolhida força cada camada a receber um contrato já fechado da anterior.

## CONSEQUÊNCIA

Enquanto esta decisão vigorar:

### NÃO COMEÇAR INTELLIGENCE porque existe uma prova isolada ou um primeiro READY

Um item E2E é necessário para integração, mas não basta sozinho para declarar a fase Collection encerrada.

### NÃO COMEÇAR CASCO / PORTAL porque Collection ou Intelligence já possuem dados interessantes

O portal é consumidor final da máquina, não instrumento para decidir como ela deve funcionar.

### NÃO USAR A COLETA GRANDE COMO LABORATÓRIO DE ARQUITETURA

A ordem continua:

```text
PREPARAR
→ PROVAR EM AMBIENTE SEGURO
→ FECHAR A MÁQUINA
→ EXECUTAR EM ESCALA
→ AUDITAR
```

### A SALA DE ESPERA É O MARCO DE TRANSIÇÃO

A Collection entrega material `READY` na Sala de Espera e para.

Somente depois do fechamento da Collection e da coleta grande auditada a Intelligence recebe o acervo.

## NÃO-OBJETIVOS DESTA DECISÃO

Esta decisão não:

- altera a Bíblia da Collection;
- altera contratos de identidade;
- muda Admission;
- escolhe mecanismo temático;
- define volume numérico da coleta grande;
- autoriza nova fonte ou gasto;
- autoriza LIVE como laboratório;
- integra automaticamente o SINTONIA SCRAP;
- inicia Intelligence;
- inicia Casco.

## PROVA / BASE

A decisão é coerente com as autoridades já vigentes:

- Collection termina em READY / Sala de Espera;
- `COLETAR != ADMITIR != JULGAR`;
- Intelligence pode detectar Collection Gap, mas não cria caminho paralelo até coletores;
- System Map observa a máquina e não define arquitetura;
- `CAN DO != DID DO`;
- `MODULE EXISTS != EDGE EXISTS != FLOW EXISTS`;
- Casco / Portal permanece depois da máquina e das ferramentas.

## DIREÇÃO CONGELADA

```text
COLLECTION COMPLETA
→ COLETA GRANDE
→ SALA DE ESPERA POPULADA E AUDITADA
→ INTELLIGENCE
→ INTELLIGENCE TOOLS / VALIDATION
→ CASCO / PORTAL
```

**Não inverter esta ordem sem uma nova decisão explícita do dono do projeto.**
