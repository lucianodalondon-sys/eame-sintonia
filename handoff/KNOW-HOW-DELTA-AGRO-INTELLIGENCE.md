# HANDOFF · DELTA DE KNOW-HOW · A MATÉRIA-PRIMA DA INTELLIGENCE AGRÍCOLA

**Para aplicar em `claude/sintonia-eame-know-how-v1` →
`SINTONIA-EAME-KNOW-HOW.md`, no PRÓXIMO NÚMERO LIVRE.**

> Quem integrar **lê o último `§` do ficheiro e usa o seguinte.** Este ficheiro
> não carrega número, pela razão que a linha do know-how já pagou duas vezes.
>
> ⚠️ **Último `§` medido no momento desta escrita: `§109`**, em
> `origin/claude/sintonia-eame-know-how-v1 @ 7b5e50cf`
> («o valor que existia em mãos e não atravessava a fronteira»). Ler o estado
> actual antes de aplicar — o know-how anda, e parte disto pode já lá estar.
> Em particular, **este delta é o irmão agrícola do `§109`**: a mesma forma de
> defeito, noutra camada.

```
ORIGEM      C-INT-AGRO-BENCH-01
MEDIDO_EM   2026-09-13
BASE        funcional f888776d · trabalho em claude/epic-archimedes-ryo0ms
INSTRUMENTO provas/auditoria_agro_fronteira.py
```

---

# §<PRÓXIMO LIVRE> · A ESPÉCIE DA EVIDÊNCIA É UM FACTO, E ELA NÃO VIAJA

## O QUÊ

Esta casa declara, **no contrato de fonte e antes de qualquer execução**, que
espécie de evidência cada fonte produz — e escreve leis ao lado:

```
AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE      IT-T2-001 · IT-T2-002
REGISTRY            != FIELD_SIGNAL         IT-T3-011
TECHNICAL_GUIDELINE != CURRENT_FIELD_SIGNAL IT-T5-002
COMPANY_CLAIM       != REGULATORY_FACT      IT-T9-008  (inclusive para a ADAMA)
```

**Nenhuma delas atravessa a fronteira para a Intelligence.** Medido: o contrato
comum (`ingresso.PARA_A_PORTA`) tem 10 nomes e nenhum é `EVIDENCE_CLASS`; o
contrato de saída (`pronto_para_inteligencia`, `COL-LAW-043`) tem 12 campos e
nenhum é `EVIDENCE_CLASS`.

## POR QUÊ — é o `§109` outra vez, num sítio diferente

O `§109` fechou-se sobre um valor que **existia em mãos** (`raw_asset_id`) e era
deitado fora exactamente na última porta. Este é o mesmo defeito, e a diferença
importa:

```
§109     o valor estava NO ITEM, e a porta deitava-o fora.
ESTE     o valor esta NO CONTRATO DA FONTE, e nunca chega a estar no item.
```

```
RUNTIME SABE != O SISTEMA GUARDA   (§86.4)
E AGORA TAMBEM:
O CONTRATO DECLARA != O ITEM CARREGA
```

Um contrato que declara e nunca é lido pela travessia é uma lei que só existe no
ficheiro onde foi escrita.

## PROVA

`python3 provas/auditoria_agro_fronteira.py` — seis ataques contra o código
real, com casos descartáveis, sem escrever nada:

```
A  39 campos de um FATO agronomico -> 12 no READY -> 30 perdidos
   (e o `estagio` do item E reconhecido como FATO: as MARCAS_DE_FATO
    — claim_id · subject · predicate · fact_id — ja existem no codigo,
    decidem a regua aplicada, e NAO SAEM)
C  0 de 23 campos agronomicos com chave propria no READY
F  contrato comum: 10 nomes, 0 agronomicos
   rota forward real: 9 nomes, sem FACT_TIME nem FACT_LOCATION
```

## CONSEQUÊNCIA

Do lado da Intelligence, um boletim agroclimático da ARPAE e um relato de campo
da ARIF são o mesmo objecto: `TEXTO`. Os quatro erros agrícolas mais caros —
clima favorável lido como doença, registo lido como mercado, guideline lida como
sinal actual, alegação de empresa lida como facto regulatório — tornam-se
**indistinguíveis por construção**, e nenhuma releitura do texto os separa,
porque a espécie não está no documento: está no contrato.

Está aberto em `docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md`.

---

# §<PRÓXIMO LIVRE + 1> · UM ZERO AGRÍCOLA PRECISA DE DENOMINADOR, E ISSO TEM NOME LÁ FORA

## O QUÊ

A `COL-LAW-214` classifica o zero **da coleta** em três palavras
(`EXPECTED_ZERO` · `UNEXPECTED_ZERO` · `UNKNOWN_ZERO`) e está certa — ela mede
anomalia técnica.

O agro tem um **segundo** zero, que ela não cobre e não devia cobrir: o zero
**do mundo**. E ele tem vocabulário internacional, com dono.

```
EFSA, inqueritos estatisticamente solidos:
  DESIGN PREVALENCE + POPULACAO-ALVO + SENSIBILIDADE DO METODO
  (= eficacia da amostragem x sensibilidade de diagnostico) + NIVEL DE CONFIANCA

ISPM 8 (IPPC), cinco especies de ausencia:
  pest not recorded · pest free area · pest records invalid ·
  pest no longer present · pest eradicated
```

## POR QUÊ

`UNEXPECTED_ZERO` responde «a minha recolha falhou?». Não responde «a praga está
lá?». São duas perguntas com dois donos, e usar a primeira para responder à
segunda é o erro que a `COL-LAW-035` já proíbe — sem lhe dar as palavras.

## PROVA

O schema desta casa já sabia disto antes de o benchmark o confirmar:

```sql
public.observacao.base_denominador numeric NOT NULL
  -- «Obrigatório. O Brasil já travava isso em termos_medicoes...»
public.lacuna_candidata
  CONSTRAINT zero_precisa_de_diagnostico_antes_de_virar_lacuna
  CHECK (estado <> 'LACUNA_CANDIDATA' OR zero_diagnosticado)
```

## CONSEQUÊNCIA

```
0 DOENCA · 0 OCORRENCIA · 0 CONCORRENTE · 0 PRODUTO · 0 OPPORTUNITY
sao, no maximo, NOT_FOUND_IN_SCANNED_UNIVERSE.
ZERO_PROVED exige um desenho de amostragem que nenhuma fonte publica
EAME conhecida declara — e isso e SOURCE_DOES_NOT_PROVIDE,
que NAO e COLLECTION_BUG.
```

---

# §<PRÓXIMO LIVRE + 2> · A IDENTIDADE AGRÍCOLA É 1:N, E FORÇAR 1:1 DEITA FORA TRÊS QUARTOS

## O QUÊ

O código EPPO é a identidade certa para o organismo — *«quando, por razões
taxonómicas, um nome científico muda, o código EPPO permanece o mesmo»*. E ele
**não resolve a maioria dos usos de rótulo**, por razão estrutural.

## PROVA — medida nesta árvore, não citada de fora

`data/samples/X-007-canonical-agro-dictionary.json`, sobre o corpo real dos usos
autorizados franceses (E-Phy, `FR-T4-001`):

```
corpo total ..................... 1 181 pares (cultura, alvo) · 14 931 usos
resolvido por codigo EPPO .......   105 pares (8,9 %) ·  3 509 usos (23,5 %)
excluindo termos de grupo FR ....          21,1 %      ·           43,8 %

GROUP ........................... 683 pares · 6 927 usos
AMBIGUOUS ....................... 131 pares · 2 111 usos
UNRESOLVED ...................... 262 pares · 2 384 usos

Ble x «Rouille(s)»  ->  PUCCRT **e** PUCCST
Cerisier x «Moniliose(s) et pourriture grise»  ->  GLOMCI **e** PHYTCC
40 de 105 resolvidos tem EPPO_CROP com CANONICAL_CROP = null (genero/agregado)
```

## POR QUÊ

```
O ROTULO FALA A LINGUA DO AGRICULTOR.
O REGISTO FALA A LINGUA DO REGULADOR.
NENHUMA DAS DUAS E A LINGUA DA TAXONOMIA.
```

O rótulo usa grupos **de propósito**: «Rouille(s)» cobre as ferrugens que aquele
produto trata, e não uma espécie. Dar-lhe um código de espécie não é normalizar:
é decidir por conta própria uma coisa que o rótulo deliberadamente não decidiu.

## CONSEQUÊNCIA

```
1. A CARDINALIDADE FAZ PARTE DA NORMALIZACAO. `NORMALIZED_ID` pode ser lista.
2. O `MATCH_TYPE` (CONTEXTUAL · GROUP_SCOPED · AMBIGUOUS · GROUP · UNRESOLVED)
   E INFORMACAO DE PRIMEIRA CLASSE: e o registo de COMO a identidade foi
   decidida. Deita-lo fora torna o erro de normalizacao permanente e invisivel
   — que e o que a COL-LAW-203 ja proibe.
3. RECUSAR E UM RESULTADO CORRECTO. O `normalize_agro.py` recusa dar codigo de
   especie a um termo de grupo, e isso esta certo.
4. UM CRUZAMENTO HERDA O PIOR DOS DOIS LADOS — e no agro o pior lado e quase
   sempre o rotulo. Cruzar `Cereali a paglia` com `Triticum aestivum` da um
   resultado ao nivel de GRUPO, por mais precisa que seja a observacao.
```

E a lei que já existia ganha um quarto elemento medido em falta:

```
COL-LAW-203 exige ORIGINAL + NORMALIZADO + AUTORIDADE + REGRA.
O dicionario agro guarda os dois primeiros, a evidencia e o MATCH_TYPE.
NAO guarda a VERSAO DA AUTORIDADE (que versao da EPPO GD respondeu)
NAO guarda a VERSAO DA REGRA (COL-LAW-042: «a versao da regra e o que
permite reprocessar»)
```

---

# §<PRÓXIMO LIVRE + 3> · UM SINAL NÃO É UM ACHADO, E A ATRIÇÃO É DE 93 %

## O QUÊ

A EFSA faz horizon scanning de saúde vegetal desde 2017, com MedISys/EIOS sobre
3 221 fontes diárias, selecção manual por peritos, e um rastreio barato
(PeMoScoring: 15 critérios em 5 categorias, phi de −1 a +1, resposta em um dia).

```
392 pragas novas identificadas entre 2017 e 2024.
 27 voltaram a ser mencionadas em artigos subsequentes.
```

## POR QUÊ

```
~7 % DOS SINAIS SOBREVIVERAM A PROPRIA REPETICAO.
UM SISTEMA QUE PROMOVESSE SINAL A ACHADO PRODUZIRIA 93 % DE INTELLIGENCE
FALSA — COM APARENCIA IMPECAVEL.
```

## CONSEQUÊNCIA — três coisas que faltavam à hipótese desta casa

A sequência `OBSERVED SIGNAL → CORROBORATED → HYPOTHESIS → VALIDATED
IMPLICATION → ACTIONABLE OPPORTUNITY` **sobreviveu ao ataque**, e ficou
incompleta em quatro pontos:

```
IDENTITY CHECK   antes de pontuar risco — saber DE QUE organismo se fala
SCREENING        barato, com criterios visiveis, feito PARA DESCARTAR
EXPERT REVIEW    como etapa nomeada, nao como opiniao difusa
REVERSAO         ISPM 8: «pest records invalid» · «pest no longer present»
```

E a quarta é a que muda a arquitectura:

```
UMA MAQUINA QUE SO SABE SUBIR NAO E UMA MAQUINA DE PROMOCAO. E UMA CATRACA.
UM OBJECTO QUE NAO SABE DESPROMOVER-SE ACUMULA MENTIRAS NA VELOCIDADE
A QUE O MUNDO MUDA — E NO AGRO O MUNDO MUDA TODAS AS CAMPANHAS.
```

E o corolário para o que a casa já tem:

```
FACTO PRESENTE SOBRE O FUTURO (uma data de caducidade, do regulador)
  !=
SINAL FRACO (algo que pode vir a ser, com ~7 % de sobrevivencia)

O card `future` mistura-os hoje, e o segundo herda a credibilidade do primeiro.
```

---

## NOTA PARA QUEM INTEGRAR

Estes quatro deltas **não** repetem lei. Três deles dão palavras e números a
leis que já existem (`COL-LAW-035`, `COL-LAW-203`, `COL-LAW-214`), e o primeiro
mede uma fronteira que nenhuma lei tinha ainda atravessado a medir.

```
NENHUM DELES PEDE UMA LEI NOVA NA BIBLIA.
O PRIMEIRO PEDE UMA DECISAO, E ELA E DO DONO DA COLLECTION:
docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md
```
