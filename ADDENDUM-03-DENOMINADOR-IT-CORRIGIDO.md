# ADDENDUM 03 — CORREÇÃO DO DENOMINADOR IT
# LER DEPOIS DOS ADDENDUM-01 E 02 — NÃO REINICIAR A MISSÃO

Precedência: **ADDENDUM-03 > ADDENDUM-02 > ADDENDUM-01 > MISSAO-...md**

Este addendum CORRIGE um número que o coordenador escreveu errado no ADDENDUM-02.
O ADDENDUM-02 já foi emendado no disco, mas se tiver lido a versão anterior:
**`ATLAS_IT = 162` e `GAP = 108` estão REVOGADOS.**

==================================================
1. CORRIGIR 162 → 157
==================================================

`162` resultava de `regex` sobre qualquer ocorrência textual do padrão
`IT-T\d+-\d+` dentro do Markdown. Isso conta **referências que não são fichas**.

VERIFICADO PELO COORDENADOR em `d915f85a`:

```
A) regex sobre qualquer menção          162
B) fichas com campo `SOURCE_ID: IT-*`   156
C) B + a ficha agrupada FR/ES/IT-T9-001 157   ← CORRETO
```

```
ATLAS_IT_CURRENT = 157
```

==================================================
2. OS 6 FALSOS POSITIVOS — CADA UM VERIFICADO NA LINHA
==================================================

A diferença `162 − 156 = 6` é exatamente este conjunto. Não é aproximação:

```
IT-T12-001   L135   "Exemplos: `EU-T4-001`, `FR-T3-002`, `ES-T1-001`, `IT-T12-001`."
             → EXEMPLO DE FORMATO. Não é fonte.

IT-T4-002    L150   "| `IT-T4-002` | 2 versões do atlas, em tabela de estado
                     (nunca teve ficha) | categoria fitoiatrica — taxonomia
                     oficial | **é vocabulário, não fonte.**"
             L152   "`IT-T4-002` **está gasto e não se reatribui.**"
             → ID GASTO, declarado pelo próprio Atlas. Não é fonte.

IT-T4-003    L153   "O próximo T4 italiano livre é o `IT-T4-003`."
             → ID RESERVADO / PRÓXIMO LIVRE. Não é fonte.

IT-T1-001    L630   tabela "não alcançadas": ISTAT — coltivazioni (SDMX) · NÃO SEI
             → LINHA HISTÓRICA sem ficha própria. Não é fonte atual.

IT-T13-001   L1337  tabela "não alcançadas": Registro Imprese · NÃO SEI
             → LINHA HISTÓRICA sem ficha própria. Não é fonte atual.

IT-T9-001    L1051  "#### FR/ES/IT-T9-001 · Sites e canais dos concorrentes"
             L1054  "SOURCE_ID: FR-T9-001 / ES-T9-001 / IT-T9-001 (mesma natureza)"
             → É FONTE VÁLIDA, em ficha agrupada multinacional.
               CONTA. É o +1 que leva 156 → 157.
```

==================================================
3. A REGRA DE CONTAGEM É DECLARADA PELO PRÓPRIO ATLAS
==================================================

Não é regra nova inventada por esta missão. Está escrita no Atlas, L7155–7159:

> ### Regra de contagem (declarada para evitar leitura ambígua)
>
> O placar conta **SOURCE_IDs**, não fichas. Uma ficha pode cobrir mais de um
> SOURCE_ID (ex.: `FR/ES/IT-T9-001` é uma ficha e três fontes), e algumas fontes
> testadas aparecem em tabelas de "não alcançadas" sem ficha própria (as nacionais
> de T1, EU-T10-002/003).

O Atlas nomeia explicitamente "as nacionais de T1" — que é exatamente o caso do
`IT-T1-001` excluído acima. A regra e a medição concordam.

==================================================
4. PROVA INDEPENDENTE — IGUALDADE DE CONJUNTOS
==================================================

Não basta dois métodos darem o mesmo NÚMERO: números iguais podem esconder
conjuntos diferentes. Foi verificada a **igualdade dos conjuntos**:

```
INDICE-DE-FONTES.md (gerado pelo owner canónico) · IT distintos   157
ATLAS fichas com campo SOURCE_ID + IT-T9-001                      157

CONJUNTOS IDÊNTICOS ?   True
só no índice:  nenhum
só no atlas :  nenhum
```

Portanto o mecanismo do gerador canónico e a contagem por ficha produzem **o mesmo
conjunto de 157 SOURCE_IDs**, elemento a elemento. `157` é o valor a usar.

REGRA PERMANENTE PARA ESTA MISSÃO:

- NÃO contar SOURCE_ID por regex sobre menção textual;
- ficha individual = 1 fonte;
- ficha multinacional pode representar >1 SOURCE_ID;
- exemplo ≠ fonte · ID reservado ≠ fonte · ID gasto ≠ fonte · linha histórica ≠ ficha;
- se o gerador canónico já produz 157 IT, **usar esse mecanismo ou o seu owner**.
  NÃO criar uma segunda regra de contagem — duas regras divergem e a partir daí
  nenhuma vale.

==================================================
5. CONSEQUÊNCIA PARA O GATE
==================================================

```
FOUNDATION_CENSUS_UNIVERSE   =  54     (candidatas/ITALY-SOURCE-MASTER-V1.json)
CURRENT_ATLAS_IT_UNIVERSE    = 157
UNIVERSE_GAP                 = 103     ← NÃO 108
FOUNDATION_DENOMINATOR_VALID = NO
```

O blocker correto é:

```
BLOCKER = FOUNDATION_DENOMINATOR_STALE
          54 / 157 · GAP = 103
```

NÃO `FOUNDATION_DENOMINATOR_UNPROVEN` (nome usado no ADDENDUM-02, revogado).
A diferença importa: **STALE** diz que o catálogo é uma fotografia histórica de
2026-09-07 que envelheceu — não que o denominador seja desconhecido. Sabemos qual
é; sabemos que está velho.

A conclusão do ADDENDUM-02 permanece INTACTA:

> Antes de fechar a fundação, o censo precisa de medir o universo atual correto,
> OU provar explicitamente por que um subconjunto menor é o denominador contratual.

`COLLECTION_FOUNDATION_CLOSED` **não se altera nesta etapa**. Apenas propor, com prova.

==================================================
6. ANOMALIA REGISTADA (não bloqueia, mas não se apaga)
==================================================

`IT-T1-001` foi corretamente EXCLUÍDO do universo atual — não tem ficha.
Porém existe, no mesmo HEAD, evidência recolhida sob esse ID:

```
data/samples/IT-SOURCE-SAMPLES/IT-T1-001/ISTAT_101_1015_COLTIVAZIONI_2_2025.csv
data/samples/IT-SOURCE-SAMPLES/IT-T1-001/MANIFEST.json
```

Isto é coerente com o `OUT_OF_FLOW_EVIDENCE = 13` já medido em
`docs/operacao/SOURCE-ID-WIRING-GAP-V1.md`: corpos cujo SOURCE_ID existe apenas
como nome de diretório, sem observação de coleta.

NÃO corrigir por atalho. NÃO promover a fonte para fazer o número subir.
Registar como achado, com o owner nomeado. Ver §8 da MISSÃO (SOURCE_ID) e §19
(red team: "convenção de caminho usada como identidade").

==================================================
7. O QUE NÃO MUDA
==================================================

Tudo o resto dos ADDENDUM-01 e 02 continua em vigor:

- o índice NÃO é owner do readiness (`INDEX_COLLECTION_READINESS_STALE = YES`);
- `DECLARED_CONTRACT` ≠ `TECHNICALLY_COLLECTION_READY` ≠ `FLOW_OBSERVED` ≠
  `BIG_COLLECTION_EXECUTABLE`;
- critérios A..N remedidos, cada um com PROOF **e com o denominador declarado**;
- `DIRECT_INTELLIGENCE_CHANGES = 0`;
- não editar generated JSON; não editar o índice à mão;
- HARD STOP: não abrir Intelligence mesmo que o gate passe.

Continue a missão.
