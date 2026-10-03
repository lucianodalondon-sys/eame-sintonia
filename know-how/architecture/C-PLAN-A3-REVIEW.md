# C-PLAN-A3 — REVIEW

> Revisão do contrato `STRUCTURED por espécie` antes de implementação.

## VEREDITO

```text
C-PLAN-A3 = PASS para a decisão principal
RUNTIME_IMPLEMENTATION = AINDA NÃO
```

A decisão central é boa:

```text
STRUCTURED não é uma tabela universal.
T-32 não escolhe a espécie.
T-32 não infere espécie por campos/formato/canal.
Cada conceito STRUCTURED deve ter um owner.
NOT_APPLICABLE precisa de razão persistida.
```

## PONTO QUE CONTINUA PROVISÓRIO — CARDINALIDADE DO STRUCTURED_TARGET

A3 escolheu o contrato de fonte como autoridade de `STRUCTURED_TARGET`, mas escreveu o alvo no singular. Isso ainda precisa de medição antes de virar schema/runtime.

Uma mesma fonte pode potencialmente produzir mais de uma espécie estruturada. Exemplo conceitual já presente na casa social:

```text
mesma plataforma/conta/fonte
→ SOCIAL_CONTENT
→ SOCIAL_COMMENT
→ SOCIAL_TRANSCRIPT
```

Logo há três perguntas diferentes:

```text
1. Quais espécies esta fonte É AUTORIZADA/CAPAZ de produzir?
   owner provável: SOURCE CONTRACT

2. Qual espécie esta execução/unidade DEVE produzir agora?
   deve ser derivada do pedido/plano + contrato, antes do T-32

3. Quem persiste aquela espécie?
   owner: registry STRUCTURED_TARGET -> writer
```

Regra de Know How:

> Contrato de fonte deve possuir o conjunto/contrato de outputs permitidos. A unidade que entra no T-32 deve carregar um target explícito já resolvido. T-32 transporta; não escolhe nem deduz.

Não implementar um `STRUCTURED_TARGET` singular por fonte antes de provar que cardinalidade 1 é válida para todas as rotas.

## OWNERS AUSENTES NÃO INVALIDAM ONE-OWNER-PER-CONCEPT

A3 escreveu `ONE_STRUCTURED_OWNER_PER_CONCEPT = YES` como regra alvo, mas no AS-IS há conceitos sem owner:

```text
OFFICIAL_BULLETIN = owner ausente
TABULAR_MEASUREMENT = owner ausente
SOCIAL_TRANSCRIPT = store existe, writer/owner não provado
```

Portanto distinguir:

```text
TARGET_RULE_ONE_OWNER_PER_CONCEPT = YES
CURRENT_ONE_OWNER_PER_CONCEPT = NO
```

## CORREÇÃO DE IDENTIDADE SOCIAL

`public.conteudo` possui `raw_asset_id`; o defeito do PDF não era ausência de lineage. O defeito é `canal_id NOT NULL`, que força identidade social numa unidade documental.

Regra:

> Não fabricar organização/canal para encaixar documento em store social. Quando o modelo de identidade não descreve a unidade, o store/conceito está errado.

## PRÓXIMO BLOCO

Antes de runtime, medir/fechar:

```text
- cardinalidade source -> structured species;
- contrato de ALLOWED_STRUCTURED_TARGETS vs RESOLVED_STRUCTURED_TARGET;
- onde nasce o target resolvido por unidade;
- registry target -> owner/writer;
- owner/store/identity de OFFICIAL_BULLETIN;
- owner/store/identity de TABULAR_MEASUREMENT;
- writer/owner de SOCIAL_TRANSCRIPT;
- schema mínimo de NOT_APPLICABLE reason.
```

Isso deve ser decisão contratual, não implementação.
