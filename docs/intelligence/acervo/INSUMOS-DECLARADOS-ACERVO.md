# Insumos declarados da Intelligence (R7/R8) — a referência oficial que já está no repositório

> O dado **não** é copiado para aqui. `INSUMOS-DECLARADOS-ACERVO.json` (gerado por
> `node pacote/acervo_inventario.mjs`) **aponta** para cada conjunto: ficheiro, contagem, sha256 do
> ficheiro, chaves de junção, a pergunta de cruzamento que ele permite e os **leitores que já existem**,
> cada um com `ficheiro:linha` procurado a cada corrida (um leitor que desapareça fica `NAO ENCONTRADO`).

## Porque isto é insumo e não objeto do casco

Registro ministerial, catálogo ADAMA, estatística oficial e base de resistência são **referência
oficial** (classe **b** do inventário). A lei D97 diz que o casco mostra só o que a Intelligence
produziu. Por isso um insumo **nunca** vira cartão sozinho: entra no pote apenas como objeto
referenciado ou procedência de um cruzamento que a Intelligence fez.

## Os dois cruzamentos pedidos

| pergunta | insumo | chaves | estado |
|---|---|---|---|
| «este produto ADAMA serve para esta praga nesta cultura?» | `italy-handoff-v21.js::productRelationships` (5 402 pares produto × cultura × alvo lidos no rótulo) + os usos da Label Intelligence (saída de ferramenta, com o estado de prova de cada par) | `REGISTRATION_NUMBER`, `CROP_ON_LABEL`/`CROP_IDS`, `TARGET_ON_LABEL`/`ISSUE_IDS`, `LINK_STRENGTH` | insumo **existe** no repo; leitores existentes: `motor/v21_crossings.py`, `motor/v21_oportunidades.py`, `italy-app-model.js` (linhas no JSON) |
| «que concorrentes estão registados para o mesmo alvo?» | `data/samples/IT-SOURCE-SAMPLES/IT-T4-001/PROD_FTS_6_20260907.csv` — o registro **inteiro** do Ministero (todos os titulares) | `sostanze_attive`, `attivita`, `ragione_sociale`, `stato_amministrativo` | pela **mesma substância ativa**: insumo existe. Pelo **mesmo alvo**: **NÃO SEI** — o registro não traz cultura × alvo; seria preciso ler os rótulos dos concorrentes, que não estão no repo (e esta missão não coleta) |

## O que não se sabe

- De que ficheiro a R7 leu o portfólio que usa em `CULTURAS_NO_ROTULO` / `PRODUTOS_ADAMA`: **NÃO SEI**.
  O motor da Intelligence (`a5db06c4`, ramo `int-intake-g0v4-v1`) não está neste repositório. Medido:
  em 11 dos 86 cruzamentos os produtos e as culturas coincidem exatamente com os usos da Label
  Intelligence; nos outros 75 não (grafias de substância diferentes, p.ex. `TAU-FLUVALINATE` ×
  `TAUFLUVALINATE`). Isso não prova nem desmente a origem.
- Os leitores `motor/v21_*.py` leem `build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/`, que **não está
  no repositório**: existem, mas não correm aqui sem esse pacote.
