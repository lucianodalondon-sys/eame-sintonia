# GATE DE ACEITAÇÃO DE MECANISMO TEMÁTICO — V1

> **Isto é o alvo, desenhado antes da flecha.** As condições que um mecanismo
> temático precisa cumprir para ser considerado suficientemente bom para
> **avaliação** no SINTONIA — escritas antes de qualquer candidato existir.
>
> ```
> THIS_IS     = THEMATIC_MECHANISM_EVALUATION_GATE_V1
> THIS_IS_NOT = FULL_EAME_PRODUCTION_RELEASE_GATE
> GATE_OWNER  = provas/gate_de_aceitacao_tematica.py
> GATE_VERSION = V1
> ```
>
> **Os números vivem no código, não aqui.** Este documento explica e cita; o
> dono único dos limiares é o ficheiro acima, e um teste prova que os dois
> dizem a mesma coisa. Uma lei em dois sítios diverge.
>
> **Missão:** `C-FECHA-GATE-ACEITACAO-TEMATICA-V1`

---

## 1 · POR QUE ISTO PRECISOU DE EXISTIR

A baseline de T3 mediu o mecanismo de hoje e **não pôde dizer se ele presta**,
porque não havia critério escrito. Ela fechou com:

```
PERFORMANCE_GATE_PREDEFINED  = NO
CURRENT_MECHANISM_ACCEPTABLE = NOT_DECIDED
```

Sem alvo desenhado antes, a flecha aterra sempre no centro de alguma coisa. E o
contrário é a mesma fraude com o sinal trocado: escolher os números para o
mecanismo de hoje passar — ou para ele falhar.

```
OS LIMIARES NASCEM DO CUSTO OPERACIONAL,
NÃO DO RESULTADO QUE JÁ CONHECEMOS.
```

---

## 2 · O ESTUDO EXTERNO, COM AS FRAQUEZAS À VISTA

Quatro sistemas maduros, lidos nas fontes oficiais.

```
THERE_IS_A_UNIVERSAL_CLASSIFIER_ACCEPTANCE_THRESHOLD = NO
```

| sistema | prescreve número universal? | o que diz |
|---|---|---|
| [Google Cloud Document AI](https://docs.cloud.google.com/document-ai/docs/evaluate) | NÃO | calcula o limiar que maximiza F1 e devolve a escolha: *«You are free to choose your own confidence threshold»*. Recusa publicar *accuracy*: *«less meaningful»* |
| [Azure AI Document Intelligence](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/document-intelligence/transparency-note) | NÃO | *«To set the threshold for your application, use the confidence score from the response»* |
| [scikit-learn](https://scikit-learn.org/stable/modules/classification_threshold.html) | NÃO | sobre o 0.5: *«most certainly not ideal for most use cases»*. O limiar sai de *«a utility metric defined by the business»* |
| [NIST AI RMF 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) | NÃO | *«it does not prescribe risk tolerance … highly contextual»*; *«Human judgment should be employed when deciding … the precise threshold values»* |

### Onde a convergência é mais fraca do que parece

Registar só a concordância seria fabricar consenso.

- **A Google cala-se sobre assimetria de custo.** A sua documentação é um
  manual de **medição**, não de **decisão de implantação**. E o seu default de
  maximizar F1 assume que um falso positivo e um falso negativo custam o mesmo
  — que é exactamente a suposição que este gate rejeita.
- **A Azure é a única fonte que nomeia um número** (*«target a score of 80% or
  higher»*) — e nomeia-o contra uma estimativa de **treino**, não contra
  holdout. É o tipo de número de que a scikit-learn e o NIST avisam. Não serve
  de barra portável.
- **Maximizar F1 e maximizar utilidade sob custo assimétrico escolhem limiares
  diferentes** no mesmo modelo. Não são duas expressões do mesmo princípio.
- **O NIST está noutra altitude:** manda documentar a tolerância, não diz qual
  ela é. Concorda por se recusar a prescrever — acordo sobre a ausência de
  regra, não uma regra partilhada.
- **O próprio NIST avisa que o problema está por resolver:** *«The current lack
  of consensus on robust and verifiable measurement methods for risk and
  trustworthiness … is an AI risk measurement challenge»*. Nenhuma das três
  fontes de fornecedor reconhece isto.

**O que isto obriga.** Se ninguém prescreve o número, ele tem de ser escolhido
aqui e justificado aqui. Padrão externo não revoga lei canónica — e também não
dispensa a casa de escolher o próprio custo.

---

## 3 · A ASSIMETRIA DO ERRO — de onde todos os números vêm

```
FALSE_NEGATIVE_COST > FALSE_POSITIVE_COST
```

Um **falso positivo** deixa entrar material a mais num universo. A Inteligência
ainda o vê e ainda o pode descartar: o erro fica **visível** e reparável.

Um **falso negativo** manda embora material que pertencia ao universo. Ninguém
olha para ele outra vez, e não há como saber o que se perdeu.

```
UM FALSO POSITIVO CUSTA TRABALHO.
UM FALSO NEGATIVO CUSTA CONHECIMENTO, E EM SILÊNCIO.
```

Daí sai a ordem de dureza: falso negativo explícito tem **zero** tolerância;
captura de positivos é quase total; precisão é exigente mas não absoluta.

E daí sai também que **abster-se é melhor do que errar um NÃO** — uma abstenção
é uma confissão que alguém pode ir ver; um NÃO errado fecha o assunto com ar de
decisão tomada. Mas abster-se sempre também reprova: um mecanismo que nunca
decide não é cauteloso, é inútil. Por isso há limiar de cobertura.

---

## 4 · A UNIDADE: OBSERVAÇÃO, NÃO FICHEIRO

```
PRIMARY_UNIT    = INDEPENDENT_OBSERVATION      31 observações
DIAGNOSTIC_UNIT = DOCUMENT                     36 documentos (obrigatório)
```

Quatro edições seguidas do mesmo boletim são quatro ficheiros e uma observação.
Pontuar por ficheiro daria quatro créditos por resolver um documento.

**A regra da previsão de um grupo, fixada antes de qualquer número:** um grupo
tem previsão binária **só** quando todos os seus documentos receberam a mesma
previsão binária. Um que se abstenha, rebente ou discorde dos irmãos tira a
previsão binária ao grupo inteiro. Sem voto de maioria.

---

## 5 · OS DOIS GATES

Nunca somados numa acurácia única.

### GATE A — REACHABILITY

Quando a procedência já está comprovada, o item **tem** de chegar à pergunta
temática.

```
REACHABILITY_REQUIRED = 1.0    sobre os 36 com procedência comprovada
```

Isto **não** autoriza fabricar `SOURCE_ID`. Origem legitimamente desconhecida
fica fora do denominador; inventá-la para o gate passar seria mentir com a
palavra certa.

### GATE B — QUALIDADE TEMÁTICA

| condição | limiar | lê-se |
|---|---|---|
| POSITIVE_CAPTURE_RATE | ≥ 10/11 | 10 de 11 observações positivas capturadas |
| EXPLICIT_FALSE_NEGATIVE | = 0 | nenhum NÃO explícito sobre observação positiva |
| SPECIFICITY | ≥ 18/20 | 18 de 20 negativas resolvidas certas |
| PRECISION_T3 | ≥ 4/5 | 4 em cada 5 «isto é T3» estão certos |
| DECISION_COVERAGE | ≥ 28/31 | no máximo 3 observações sem decisão binária |
| GROUP_PASS_RATE | ≥ 28/31 | 28 de 31 resolvidas e certas |
| ERROR | = 0 | nenhuma falha de execução |
| FALSE_SUBSTRING_OUTCOME_DEPENDENCY | = 0 | nenhum resultado depende de casamento não pretendido |

**Nenhuma média compensa a falha de um hard gate.** Precisão excelente não
compensa captura positiva ruim. Um gate que se compensa é uma média com nome de
regra.

**A acurácia condicional não aprova.** Cobertura baixa com condicional alta mede
só os casos em que o mecanismo se atreveu — é assim que um mecanismo fraco
parece forte.

### GATE DE INTEGRAÇÃO

```
INTEGRATION_GATE_PASS = REACHABILITY_GATE_PASS AND THEMATIC_GATE_PASS

CLASSIFIER_GOOD + LINEAGE_BROKEN = NOT_READY
LINEAGE_GOOD    + CLASSIFIER_BAD = NOT_READY
```

---

## 6 · O GATE APLICADO AO BASELINE CONGELADO

Aplicado **mecanicamente**, depois de o gate estar escrito. Nada foi reajustado.

```
baseline    data/derivados/BASELINE-ADMISSION-T3-V1.json
fingerprint f24eceedd1235a1c1909a0d941aea4b87bdf8cba6547be762c5785e9ff635a85

unidade     31 observações (11 positivas · 20 negativas)
            TP 2 · FN 0 · TN 4 · FP 5 · sem previsão binária 20
```

| | medido | limiar | |
|---|---|---|---|
| POSITIVE_CAPTURE_RATE | 0.1818 | ≥ 0.9091 | **FALHA** |
| EXPLICIT_FALSE_NEGATIVE | 0 | ≤ 0 | passa |
| SPECIFICITY | 0.2000 | ≥ 0.9000 | **FALHA** |
| PRECISION_T3 | 0.2857 | ≥ 0.8000 | **FALHA** |
| DECISION_COVERAGE | 0.3548 | ≥ 0.9032 | **FALHA** |
| GROUP_PASS_RATE | 0.1935 | ≥ 0.9032 | **FALHA** |
| ERROR | 0 | ≤ 0 | passa |
| FALSE_SUBSTRING_OUTCOME_DEPENDENCY | 1 | ≤ 0 | **FALHA** |

```
GATE A · REACHABILITY = 15/36   exigido 1.0   FALHA
GATE B · THEMATIC_GATE_PASS = False
INTEGRATION_GATE_PASS = False   ->  NOT_READY

CURRENT_ADMISSION_GATE_RESULT = FAIL
```

**O mecanismo de hoje cumpre duas das oito condições.** Não comete falso
negativo explícito, e não rebenta. Falha as outras seis.

**Isto não autoriza consertar.** Mesmo com FAIL:

```
ADMISSION_CHANGED = NO · KEYWORDS_CHANGED = NO · CLASSIFIER_BUILT = NO
```

---

## 7 · INDEPENDÊNCIA, A PARTIR DESTE COMMIT

```
T3_GROUND_TRUTH_ROLE = EVALUATION
```

Um mecanismo ajustado a olhar para `T3-GROUND-TRUTH-EVAL-V1` **não pode** depois
usar os mesmos 36 como prova final independente. Candidatos futuros têm de ser
definidos antes de receberem os seus resultados; havendo afinação posterior, é
preciso holdout novo.

```
UM CONJUNTO SÓ É INDEPENDENTE DE QUEM NÃO OLHOU PARA ELE.
```

---

## 8 · O QUE ESTE GATE NÃO É

```
EVALUATION_SCOPE = ITALIAN_AGRO_INSTITUTIONAL_CORPUS
```

Não autoriza França, Espanha nem EAME.

E aprovar aqui **não** é aprovar para produção. Produção ainda exige validação
fresca e trancada, prova de integração, prova de runtime, regressão e auditoria
em live.
