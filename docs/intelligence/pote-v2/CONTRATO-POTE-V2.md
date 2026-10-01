# CONTRATO-POTE-V2 — `POTE_INTELLIGENCE_CASCO/v2`, um só

> **EXPERIMENTAL · NAO_PARA_CLIENTE.** Missão POTE-V2-UNICO (27/09). D97, D112, D95 e D96 **não estão escritas
> no repositório**: este contrato segue o resumo delas no pedido da missão.
>
> **D97** — o casco só mostra o que a Intelligence produziu; a Sala de Espera aparece **só como prova** de
> onde veio.

Havia dois «v2» que não se encaixavam (medido em [`FORMATOS-MEDIDOS.md`](FORMATOS-MEDIDOS.md)): o POTE-R5 do
bot (com `INTELLIGENCE_RUN_ID` dentro de `CABECALHO`, compartimentos com `ENTRADA_QUE_EXISTE`,
`INDICES_DE_ENTREGA`, `CAMADA_DE_EVIDENCIA`) e o POTE-R6 do gerador `ce775ff5` (id no topo). **Fica um: o do
gerador**, com as regras abaixo.

| peça | onde | o que é |
|---|---|---|
| **dono da lei** | [`pacote/pote_intelligence_casco.py`](../../../pacote/pote_intelligence_casco.py) → `conferir_pote` | gera o pote e confere-o antes de sair |
| **forma** | [`POTE_INTELLIGENCE_CASCO-v2.schema.json`](POTE_INTELLIGENCE_CASCO-v2.schema.json) | JSON Schema; um teste reprova se divergir do código |
| **validador** | [`pacote/validar_pote_v2.py`](../../../pacote/validar_pote_v2.py) | FORMA (schema) + LEI (`conferir_pote`), para um `.json` ou o `sintonia-pote.js` |
| **leitor no casco** | [`italia-portale/client/sintonia-pote-casco.js`](../../../italia-portale/client/sintonia-pote-casco.js) | o **único** carregador de dado de ferramenta; confere o que torna a leitura impossível ou desonesta |

## 1 · Cabeçalho — uma corrida, no topo

```
SCHEMA "POTE_INTELLIGENCE_CASCO/v2" · MARCA · NAO_PARA_CLIENTE true
INTELLIGENCE_RUN_ID         obrigatório, NO TOPO
SOURCE_HEAD · CORTE          da corrida; ausentes = "NAO SEI" à vista
RESULT_STATE · RUN_SCHEMA · CORRIDA_SINTETICA · ENTRADA ("CORRIDA" | "PAYLOAD_V1") · LEI
LEITURA_DE_COMPATIBILIDADE   lista (vazia = nenhuma)
COMPARTIMENTOS (os doze) · LACUNAS_SEM_COMPARTIMENTO · RECUSADOS
```

**Compatibilidade, só de leitura e só na ENTRADA.** Se o livro da corrida não trouxer `INTELLIGENCE_RUN_ID`
(ou `SOURCE_HEAD`, `CORTE`, `RESULT_STATE`) no topo e o trouxer em `CABECALHO` (o formato R5), o gerador lê-o
de lá e **escreve essa leitura** em `LEITURA_DE_COMPATIBILIDADE`. O pote que sai tem-no sempre no topo. Topo e
`CABECALHO` que discordam = duas corridas = recusado. Um pote cujo id só está em `CABECALHO` **reprova** no
validador. Um ficheiro que já é pote (tem `COMPARTIMENTOS` e não `ITENS_POR_FERRAMENTA`, como o R5) **não** se
readapta: regenera-se a partir da saída do motor.

## 2 · Objeto

```
OBJETO_ID · ESPECIE · ESPECIE_DITA_POR ("INTELLIGENCE" | "CONTRATO_V1") · ESTADO "EXPERIMENTAL_CANDIDATE"
CHAVES{contrato do compartimento, NAO SEI por extenso} · CHAVES_NAO_SEI · FORA_DO_CONTRATO{nome: valor}
PORQUE · CONTRADIZ · INCERTEZA
RESULTADO                "NAO" | "NAO_TRATAR_AGORA" | "NO_DEFENSIBLE_ACTION_YET" | "NAO SEI"
USO_EXIGE_TEMPO          bool — P7
ENTITY_SOURCE?           D112, quando a Intelligence o diz
LOCATION_SOURCE?         D112; obrigatório (valor ou "NAO SEI") quando há FACT_LOCATION
MERCADO?                 só no compartimento market — P8
PROVA[ ≥1 ]
```

`ESPECIE` ∈ SINAL · FATO_PRESENTE_SOBRE_O_FUTURO · CROSSING · FINDING · OPORTUNIDADE · RENDIMENTO_DE_FONTE,
e tem de caber no compartimento (tabela em [`POTE-UNICO.md`](../../../POTE-UNICO.md) §1).

**D112 · de onde vêm a entidade e o lugar.** `ENTITY_SOURCE` / `LOCATION_SOURCE` viajam com o nome deles, nunca
como chave da vista nem em `FORA_DO_CONTRATO`. `LOCATION_SOURCE` que diga que o lugar veio da **fonte**
(`SOURCE_LOCATION`, `DOCUMENT_LOCATION`, `PUBLISHER_LOCATION`, `LOCAL_DA_FONTE`, `LOCAL_DO_DOCUMENTO`,
`SEDE_DA_FONTE`) é recusado: o lugar do documento não vira o lugar do facto.

## 3 · PROVA — até ao RAW, com URL e publicação

```
ITEM_ID → RAW_OBSERVATION_ID → SOURCE_ID → DOCUMENT_ID · CORRIDA_UPSTREAM
URL            + URL_BASE
PUBLISHED_AT   + PUBLISHED_AT_BASE
COLHIDO_EM · FACT_TIME
G0             o que a LINEAGE da corrida disse do item (a Sala só como prova)
ADMITIDA_POR   "G0_PASSOU" | "FUTURO_POR_DESENHO" | "USO_SEM_TEMPO" | "PONTE_V1"
INTELLIGENCE_RUN_ID   = o do topo
```

- A **base** diz de onde veio o valor (`PROVA.URL`, `LINEAGE.PUBLICATION_TIME`, …) ou, quando o valor é
  `NAO SEI`, **porque** (`NAO_VEIO: …`, `PAYLOAD_V1: …`). `NAO SEI` sem base reprova.
- Na entrada lêem-se `PUBLISHED_AT`, `PUBLICADO_EM` e `PUBLICATION_TIME` (nesta ordem), e `URL` / `SOURCE_URL`.
  No pote o nome é um só: `PUBLISHED_AT`. **A publicação nunca vira `FACT_TIME`.**

## 4 · P7 — o que exige tempo, e o que não

| uso | exige `FACT_TIME` ancorado? | a prova pode vir de um item que G0 bloqueou… |
|---|---|---|
| `RENDIMENTO_DE_FONTE` (Registro delle fonti) | **não** | só pelo tempo (`FACT_TIME`, `FACT_TIME:*`) |
| SINAL · CROSSING · FINDING com `RESULTADO` honesto (`NAO`, `NAO_TRATAR_AGORA`, `NO_DEFENSIBLE_ACTION_YET`; lido de `RESULTADO`, `CHAVES.RESULTADO` ou `CHAVES.CROSSING_STATE`) | **não** | só pelo tempo |
| FATO_PRESENTE_SOBRE_O_FUTURO | por desenho | só por `FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA` |
| todo o resto (sinal, oportunidade, janela, crossing afirmativo) | **sim** | nunca |

Faltar a fonte, o RAW ou o ITEM continua a bloquear em qualquer uso. `OPORTUNIDADE` nunca é «não».
O validador recalcula `USO_EXIGE_TEMPO` a partir da espécie e do `RESULTADO` e reprova uma prova
`USO_SEM_TEMPO` num uso que exige tempo.

## 5 · P8 — o Polso só lê mudança numa série

Todo objeto de `market` leva `MERCADO{LEITURA, PORQUE, PONTOS, UNIDADE, SERIE}`:

- `SERIE_MEDIDA` — `SERIE` com **≥ 2 pontos**, cada um com `PERIOD`, `PRICE`, `UNIT`, **todos na mesma unidade** e
  em períodos diferentes. O pote **confere** a série; **não calcula** a variação.
- `SINAL_SOLTO` — tudo o resto (um ponto, unidades diferentes, ponto sem preço…). O casco escreve
  «SEGNALE ISOLATO — NON è una variazione di mercato».

Um objeto que **afirme** `MUDANCA_DE_MERCADO` sem série medida é recusado
(`SINAL_SOLTO_NAO_E_MUDANCA_DE_MERCADO`). `MUDANCA_DE_MERCADO` não é campo do pote.

## 5b · LIGACAO_ADAMA — revisão anotada `v2 + LIGACAO_ADAMA/v1 (D123, 2026-09-27)`

D123 do dono (27/09): «todo fato do sintonia tem que estar linkado a bula e ao portfolio senão nada faz
sentido». **Mudança mínima**: o nome do contrato continua `POTE_INTELLIGENCE_CASCO/v2` (o casco lê-o assim);
o cabeçalho ganha `REVISAO_DO_CONTRATO`, e **todo objeto** ganha `LIGACAO_ADAMA`.

- A ligação é calculada **só** por `motor/porta_da_referencia.py` → `ligacao_adama(ref, chaves)`, com o
  carimbo da edição (`EDICAO_REGISTRO`, `DATA_DA_EDICAO_REGISTRO`, `ULTIMA_CHECAGEM_OK`, `ESTADO_FRESCOR`,
  `IMPRESSAO_DOS_LIVROS`/sha256) e um `SELO`. O pote **transporta**; nunca a calcula para um objeto da corrida.
- `ESTADO` ∈ `AUTORIZADO_BULA_LIDA` · `A_CONFIRMAR` · `SO_CULTURA` · `ADAMA_SEM_PRODUTO` · `NAO_SEI`
  (com `FALTA` ⊂ `CULTURA|PROBLEMA|SUBSTANCIA|REFERENCIA`); `PRODUTOS_ADAMA[]`, `CONCORRENTES_MESMA_SUBSTANCIA[]`,
  `BULAS_A_LER[]`; travas `NAO_PROVA = [PRESSAO_DE_CAMPO, DEMANDA]` (INT-LAW-145),
  `CONTA_COMO_FONTE_INDEPENDENTE = false` (INT-LAW-076), `CATALOGO_E_AUTORIZACAO = false` (D116).
- Recusas novas no gerador: `SEM_LIGACAO_ADAMA` · `LIGACAO_ADAMA_FORA_DA_PORTA` (selo ou lei de
  `PORTA.conferir_ligacao`) · `REFERENCIA_NAO_E_FONTE_INDEPENDENTE` (prova do objeto com `SOURCE_ID` da própria
  referência, IT-T4-001/IT-T9-008). `conferir_pote` reprova também ligações de **edições diferentes** num pote.
- Entrada `PAYLOAD_V1`: a v1 não transportava ligação nem referência — a porta diz `NAO_SEI · FALTA=REFERENCIA`.

Relatório: [`LIGACAO-ADAMA.md`](../../../LIGACAO-ADAMA.md).

## 5c · EIXOS/v1 — elegibilidade por objeto × ambiente por pote (K2, 2026-10-01)

**Origem.** O LAB reprovou o pote canónico `e97ce8b082a1…` (veredito K2 FAIL). Os 3 objetos saíam com `LIBERACAO = LIBERADO_PARA_CLIENTE` e, no mesmo objeto, `NAO_PARA_CLIENTE = true`, `MARCA = "EXPERIMENTAL · NAO_PARA_CLIENTE"` e `ESTADO = EXPERIMENTAL_CANDIDATE`. A raiz também dizia `NAO_PARA_CLIENTE`. Uma palavra estava a dizer duas coisas diferentes.

**Decisão do dono do contrato: são dois eixos, e nenhum fala pelo outro.**

| eixo | onde | campos | quem decide |
|---|---|---|---|
| 1 · ELEGIBILIDADE | cada OBJETO | `LIBERACAO` ∈ {`LIBERADO_PARA_CLIENTE`, `NAO_PARA_CLIENTE`}; `MARCA`, `NAO_PARA_CLIENTE` e `ESTADO` do objeto **dizem o mesmo** | só a Intelligence, pelo C8-AUTO (C1–C7) |
| 2 · AMBIENTE | RAIZ, compartimentos e MANIFESTO | `EIXOS = EIXOS/v1`, `AMBIENTE = PREVIEW_NAO_PRODUCAO`, `PRODUCAO = false`, `MARCA = "EXPERIMENTAL · PREVIEW_NAO_PRODUCAO"` | constante neste contrato |

- Objeto liberado: `NAO_PARA_CLIENTE = false`, `MARCA = "LIBERADO_PARA_CLIENTE · C8-AUTO"`, `ESTADO = LIBERADO_PARA_CLIENTE`.
- Objeto bloqueado: `NAO_PARA_CLIENTE = true`, `MARCA = "EXPERIMENTAL · NAO_PARA_CLIENTE"`, `ESTADO = EXPERIMENTAL_CANDIDATE`.
- A raiz e os compartimentos **não** levam `NAO_PARA_CLIENTE`: o cliente é eixo do objeto. A raiz só diz onde o pote pode aparecer.
- `aplicar_eixos` **não decide nada**. Copia a `LIBERACAO` que o C8 deu, e um objeto sem `LIBERACAO` faz parar.
- Um pote **sem** `EIXOS` é o v2 de sempre (marca `EXPERIMENTAL · NAO_PARA_CLIENTE` em tudo). Por isso **não pode** trazer objeto `LIBERADO_PARA_CLIENTE`, e o pote e97ce8b0 reprova no fiscal novo, nos 3 objetos.
- **Produção continua bloqueada (D141).** `PRODUCAO = true` não existe neste contrato e reprova na forma e na lei. Promover é a regra de promoção da L3, com aprovação do dono. Este eixo não a cria nem a afrouxa, e o C0 da L3 não muda.

Fiscal: `conferir_pote` (`_marcas_dos_eixos`, `_marca_do_compartimento`, `_marca_do_objeto`). Testes: `tests/test_pote_dois_eixos.py`.

## 6 · O casco

Um só carregador (`sintonia-pote-casco.js`), que só pede `sintonia-pote.js` com `?pote=local`. Com o pote,
cada ferramenta desenha o seu compartimento e **só ele** (o snapshot e a demo apagam-se). Pedido e não
chegou: cada ferramenta diz **NAO SEI · POTE NON CARICATO** — o legado não volta a tapar o buraco.
Compartimento vazio: **NAO SEI · VUOTO · <porquê>**. Cada prova mostra de onde veio (ITEM_ID, G0, admitida
por). Sem `?pote=local`, o casco fica como estava (mudar isso é mudar o que o deploy público mostra — decisão
do dono).

## 7 · Comandos

```bash
python3 pacote/pote_intelligence_casco.py <ENTRADA-DA-PONTE.json> italia-portale/client/sintonia-pote.js
python3 pacote/validar_pote_v2.py italia-portale/client/sintonia-pote.js
python3 -m unittest tests.test_pote_v2_unico tests.test_pote_intelligence_casco
```
