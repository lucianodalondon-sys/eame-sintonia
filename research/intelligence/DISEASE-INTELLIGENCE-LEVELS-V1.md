# RÉGUA DE DISEASE / PEST INTELLIGENCE — V1

```
MISSAO     C-INT-AGRO-BENCH-01
ESPECIE    REGUA DERIVADA DE BENCHMARK
MEDIDO_EM  2026-09-13
```

> Cinco níveis. Cada um exige uma matéria-prima que o anterior não exigia.
> **Um sistema não «sobe de nível» por melhorar a apresentação.** Sobe quando
> recebe o dado que o nível seguinte pede, e não antes.

---

## A RÉGUA

### NÍVEL 0 · `MENÇÃO`
```
O QUE E        um texto nomeia uma praga ou doenca
EXIGE          texto + fonte
PROVA          nada sobre o mundo
NAO PODE DIZER que a doenca esta presente, nem onde
LEI            «convegno a Bologna» tem preposicao e proximidade, e nao diz
               nada sobre onde a doenca esta   (COL-LAW-032)
```

### NÍVEL 1 · `SINAL RELATADO`
```
O QUE E        uma fonte AFIRMA que o problema esta a ocorrer
EXIGE          FACT_LOCATION escrito ou citado (nao deduzido, nao da fonte)
               FACT_TIME real (nao PUBLISHED_AT)
               identidade do organismo (EPPO), ou o termo original preservado
               a ESPECIE da evidencia: OBSERVED_FIELD_SIGNAL
PROVA          que alguem com autoridade relatou
NAO PODE DIZER quanto · em que fraccao · com que metodo · se esta a aumentar
EXTERNO        ISPM 8 chama a isto um PEST RECORD, e um pest record NAO e um
               estado de praga: o estado e uma conclusao da autoridade sobre
               um conjunto de registos, e pode ser revertido
```

### NÍVEL 2 · `SINAL RELATADO COM CONTEXTO AGROCLIMÁTICO`
```
O QUE E        nivel 1 + condicoes favoraveis documentadas na mesma area e
               janela, vindas de outra fonte
EXIGE          serie agroclimatica com lugar e tempo compativeis
               a LEI a viajar com ela
PROVA          que houve relato E que as condicoes nao o contradizem
NAO PODE DIZER que o clima causou; nem que ha incidencia
LEI INTERNA    o contrato IT-T2-001/002 ja escreve, no proprio ficheiro:
                   AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE
```

### NÍVEL 3 · `RISCO MODELADO`
```
O QUE E        um modelo calcula probabilidade de infeccao para uma unidade
EXIGE          cultura + VARIEDADE (susceptibilidade)
               DATA DE SEMENTEIRA/PLANTACAO
               FENOLOGIA observada ou modelada (BBCH)
               meteorologia a escala e passo do modelo
               historico de doenca / inoculo
               aplicacoes de fungicida ja feitas
               cultura anterior · mobilizacao · irrigacao · azoto (conforme o modelo)
PROVA          que o modelo, com aqueles inputs, produziu aquele numero
NAO PODE DIZER que a doenca existe.   MODEL OUTPUT != FACT
EXTERNO        e o nivel a que operam xarvio e Cropwise, e ambos o fazem
               POR TALHAO, com limite de campo declarado
```

### NÍVEL 4 · `INCIDÊNCIA CONFIRMADA COM DENOMINADOR`
```
O QUE E        uma medicao de prevalencia, defensavel
EXIGE          POPULACAO-ALVO declarada (estrutura e dimensao)
               UNIDADE EPIDEMIOLOGICA e UNIDADE DE INSPECAO
               DESIGN PREVALENCE
               SENSIBILIDADE DO METODO = eficacia da amostragem x sensibilidade
                                          de diagnostico
               NIVEL DE CONFIANCA
               metodo de DIAGNOSTICO declarado
PROVA          prevalencia, com confianca — e, no negativo, AUSENCIA
EXTERNO        e exactamente o contrato das guidelines da EFSA para inqueritos
               estatisticamente solidos, e e o unico caminho conhecido para
               provar ausencia
```

---

## A LEI DA RÉGUA

```
NIVEL 0 -> 1   exige LUGAR DO FATO e TEMPO DO FATO
NIVEL 1 -> 2   exige SEGUNDA FONTE INDEPENDENTE e COMPATIBILIDADE espaco-tempo
NIVEL 2 -> 3   exige INPUTS DE MODELO, e o modelo
NIVEL 3 -> 4   exige DENOMINADOR, METODO DE DIAGNOSTICO e DESENHO DE AMOSTRAGEM

E NENHUM SALTO E GRATIS:
  clima favoravel        NAO promove nivel 2 a 3
  saida de modelo        NAO promove nivel 3 a 4
  revisao humana         NAO promove nivel nenhum   (INT-LAW-172)
  mais fontes do mesmo   NAO promove nivel nenhum
```

---

## ATÉ ONDE O SINTONIA CHEGA HOJE — MEDIDO

```
DISEASE_INTELLIGENCE_MAX_DEFENSIBLE_LEVEL = NIVEL 2
```

E mesmo o nível 2 está **condicionado**, porque na fronteira actual nem o nível 1
atravessa inteiro. Medido em `provas/auditoria_agro_fronteira.py`:

| exigência do nível | a Collection tem? | atravessa até à Intelligence? |
|---|---|---|
| identidade do organismo (EPPO) | **SIM** — `data/samples/X-007-canonical-agro-dictionary.json`, verificado contra a EPPO GD | **NÃO** — não há campo |
| `FACT_LOCATION` | **SIM** — lei, contratos e migration 015 | **contrato SIM, rota forward NÃO** — `item_para_a_porta` não o põe no item |
| `FACT_TIME` | **SIM** — lei canónica com quatro tempos | **contrato SIM, rota forward NÃO**; e a porta aceita `published_at` como resposta |
| espécie da evidência (`OBSERVED_FIELD_SIGNAL`) | **SIM** — declarada em 13 contratos de fonte | **NÃO** — não existe campo em lado nenhum da travessia |
| método / unidade / escala | **NÃO** — nenhuma fonte pública EAME o entrega estruturado | — |
| denominador / população-alvo | **NÃO** — e `SOURCE_DOES_NOT_PROVIDE` | — |
| inputs de modelo (variedade, sementeira, inóculo) | **NÃO** — e exigem dado privado de exploração | — |

### Porque o nível 3 não é uma questão de esforço

O nível 3 exige **limite de campo, variedade e data de sementeira**. Esses dados
pertencem ao agricultor. O EU Code of Conduct põe o originador do dado no centro
e reconhece-lhe o direito a beneficiar do seu uso. Não é um problema de
engenharia: é um problema de contrato.

```
O SINTONIA NAO DEVE CONSTRUIR UM MODELO DE TALHAO.
NAO PORQUE SEJA DIFICIL — PORQUE ELE NAO TEM, E NAO DEVE TER SEM CONTRATO,
O DADO QUE O MODELO COME.
```

### Porque o nível 4 é honestamente inalcançável hoje

Nenhuma das 13 fontes italianas contratadas declara população-alvo, dimensão de
amostra, sensibilidade do método ou prevalência de desenho. Isso **não é um bug
da Collection**:

```
SOURCE_DOES_NOT_PROVIDE != COLLECTION_BUG.
```

O que é um bug é dizer nível 4 quando se tem nível 1.

---

## O QUE ISTO OBRIGA A ESCREVER NA ENTREGA

Toda afirmação de doença/praga do SINTONIA **deve carregar o seu nível**. Não
como decoração: como parte do facto.

```
«Peronospora da videira relatada na provincia de Verona, 2026-05-02»
   NIVEL 1 · fonte: bollettino regional · metodo: NAO SEI · denominador: NAO SEI

nunca

«Peronospora com 12 % de incidencia em Verona»
   — que e NIVEL 4, e nos nao o temos
```

E o corolário para o zero:

```
0 OCORRENCIAS NO NOSSO CORPUS = NIVEL 0 DE AUSENCIA.
E o nivel 0 de ausencia chama-se NOT_FOUND_IN_SCANNED_UNIVERSE,
nunca ZERO_PROVED.
```
