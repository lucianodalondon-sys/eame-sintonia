# PARA O CASCO — o pote que o disparador da Intelligence entrega, e onde

> L2-DISPARADOR-INTELLIGENCE (D140, 28/09/2026) · ramo `claude/l2-disparador-v1` · base produção `fd8c94698`.
> Aceite do Casco (28/09): **SERVE** — MANIFESTO.json + SHA256SUMS, campos existentes, `CORRIDA_SINTETICA` = DEMO/LIVE,
> **nenhum campo novo**. Este ficheiro responde às duas perguntas que faltavam (§3 e §4). Tudo o que está aqui foi
> **medido** no código ou nos ficheiros, com o sítio ao lado. O que não foi medido está escrito como NÃO SEI.

---

## 1 · Onde o pote aparece

| o quê | caminho (na árvore do serviço) | quando |
|---|---|---|
| o pote que o casco carrega | `italia-portale/client/sintonia-pote.js` (`window.SINTONIA_POTE = {...}`) | **só** se o fiscal `pacote/validar_pote_v2.py` disser PASSA |
| a entrega com prova de integridade | `curadoria/esteira/intelligence/PARA-O-CASCO/` → `POTE.json` · `MANIFESTO.json` · `SHA256SUMS.txt` | a mesma condição; a pasta é trocada **inteira** (escreve-se ao lado e renomeia-se), nunca meia |
| o pote reprovado (não é para o casco) | `curadoria/esteira/intelligence/<AAAAMMDDTHHMMSSZ>/POTE-REPROVADO-<RUN>.js` | quando o fiscal reprova; **não sobe** |

Os três ficam fora do Git (`italia-portale/client/.gitignore`, `curadoria/.gitignore`): têm dado real.

**Um pote reprovado nunca substitui o último aprovado.** Se nunca houve pote aprovado, a pasta `PARA-O-CASCO/` não existe
e `sintonia-pote.js` não existe. Pela regra do Casco, isso é **tela vazia**, nunca parcial.

## 2 · O formato — o pote v2 que já existe, sem campo novo

- `POTE.json` = o pote **POTE_INTELLIGENCE_CASCO/v2**, byte a byte o mesmo objeto que vai em `sintonia-pote.js`.
  Gerador: `pacote/pote_intelligence_casco.py` (`ler_entrada` → `adaptar`). Fiscal: `pacote/validar_pote_v2.py`
  (forma do schema `docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json` + lei `conferir_pote`).
- Chaves do topo (medidas num pote gerado pelo motor sobre a fixture `tests/dados/int-r7/SINTETICO-R7-SALA-EXPORT.json`):
  `COMPARTIMENTOS, CORRIDA_SINTETICA, CORTE, ENTRADA, INTELLIGENCE_RUN_ID, LACUNAS_SEM_COMPARTIMENTO, LEI,
  LEITURA_DE_COMPATIBILIDADE, MARCA, NAO_PARA_CLIENTE, RECUSADOS, RESULT_STATE, REVISAO_DO_CONTRATO, RUN_SCHEMA, SCHEMA, SOURCE_HEAD`.
- Cada compartimento: `ESTADO` (`COM_OBJETOS` | `VAZIO`), `PORQUE_VAZIO`, `CONTRATO_CHAVES`, `OBJETOS[]`.
  Cada objeto: `ESPECIE`, `CHAVES{<nome>: valor | "NAO SEI"}`, `CHAVES_NAO_SEI[]`, `PROVA[]`, `ESTADO`/`RESULTADO`/`INCERTEZA`/`CONTRADIZ`, `NAO_PARA_CLIENTE`.
- `CORRIDA_SINTETICA`: `false` quando o export veio da cópia da Sala real (o disparador lê `SINTETICO` do export).

`MANIFESTO.json` (o mesmo desenho do `MANIFESTO-R9.json`, reduzido a UM pote):

```json
{
 "INTELLIGENCE_RUN_ID": "IR-...",
 "RESULT_STATE": "DONE",
 "CORRIDA_SINTETICA": false,
 "SOURCE_HEAD": "<commit da árvore que correu o motor>",
 "CORTE": "<hora do export da cópia>",
 "GERADO_EM": "<ISO UTC>",
 "GERADO_POR": "admissao/gatilho_da_inteligencia.py (L2-DISPARADOR)",
 "POTE": {"ARQUIVO": "POTE.json", "SHA256_ARQUIVO": "<sha256 do ficheiro>", "CONTRATO": "POTE_INTELLIGENCE_CASCO/v2"},
 "VALIDAR_POTE_V2": "PASSA",
 "CORTE_VIGENTE": {"LINHAS_NO_EXPORT": 0, "LINHAS_NO_CORTE": 0, "DEFEITO_NA_SALA": false}
}
```

`SHA256SUMS.txt`, formato do `sha256sum` (o mesmo do R9): `<sha256> *POTE.json` e `<sha256> *MANIFESTO.json`.
Sha que não bate, ficheiro que falta ou `RESULT_STATE` fora de `DONE`/`REUSED` → **tela vazia** (regra do Casco).

### ⚠️ Hoje o disparador NÃO entrega pote nenhum

O motor escreve `ENTITY_SOURCE` como **objeto** (D112: `{VALOR, ENTITY_SOURCE, POR_ITEM}` por chave,
`motor/motor_das_capacidades.py:493-498`). O schema do pote pede **texto** (`POTE_INTELLIGENCE_CASCO-v2.schema.json:49`).
Medido na fixture: **7 violações em 7 objetos, as 7 de `ENTITY_SOURCE`**. O fiscal reprova, e o disparador obedece:
nada sobe, e o Casco continua a ver o último pote aprovado (ou tela vazia). Isto é **bloqueio do dono do pote**,
não do Casco: o formato acima não muda quando for resolvido.

## 3 · As chaves do compartimento `meeting` (Radar delle Opportunità)

Medido em `pacote/ponte_intelligence_casco.py:95-97` (`FERRAMENTAS["meeting"]["CHAVES"]`). O pote v2 lê daí
(`pacote/pote_intelligence_casco.py:127-130`), e o pote R9 real traz a mesma lista em `COMPARTIMENTOS.meeting.CONTRATO_CHAVES`.

| pergunta do Casco | nome da chave | onde se lê |
|---|---|---|
| cultura | **`CROP_ID`** | `COMPARTIMENTOS.meeting.OBJETOS[i].CHAVES.CROP_ID` |
| alvo / problema | **`ISSUE_ID`** | `...CHAVES.ISSUE_ID` |
| região | **`REGION_ID`** | `...CHAVES.REGION_ID` |
| janela temporal | **`TIME_WINDOW`** | `...CHAVES.TIME_WINDOW` |
| *(também no contrato, não pedidas)* | `ADAMA_PRODUCT_ID`, `AUTHORIZATION_EVIDENCE_ID` | idem |

Por item: o valor, ou a string `"NAO SEI"`, e o nome da chave em `CHAVES_NAO_SEI[]` quando é NÃO SEI.
Espécies admitidas no `meeting` (pote R9): `OPORTUNIDADE`, `CROSSING`, `FINDING`, `SINAL`.

**⚠️ Medido: hoje o `meeting` nasce SEMPRE vazio.** O motor que o disparador corre (`motor_das_capacidades.rodar`)
só produz objetos para `windows`, `science`, `future` e `sources` (`motor/motor_das_capacidades.py`, dict `objetos`).
A capacidade do `meeting` (`CAP-OPP`) não existe no motor. Por isso, em todo pote do disparador:
`meeting.ESTADO = "VAZIO"`, `PORQUE_VAZIO = "SEM_OBJETOS_NESTA_CORRIDA"`, e **nenhum item** — cultura, alvo, região
e janela são **NÃO SEI por ausência de objeto**, não por item. O pote R9 real também tem `meeting` = 0 objetos.

Atenção a outras ferramentas, para não confundir nomes: `windows` usa `DATE_OR_STAGE` (não `TIME_WINDOW`) para a
janela; `future` e `archive` usam `REGION_ID` + `FACT_LOCATION` + `FACT_TIME`.

## 4 · Onde caem os 2 objetos R9 (os fatos do clima)

Medido em `C:\Users\London1\sintonia-sala-italia\intelligence-experimental\PARA-O-CASCO-R9\POTE-R9-PARA_CLIENTE.json`
(corrida `IR-56c79b0c78fc3fa1e747`, fora do Git; `MANIFESTO-R9.json` diz `VALIDAR_POTE_V2 = PASSA`, 2 objetos liberados).

| objeto | compartimento | ESPECIE | o fato | CHAVES |
|---|---|---|---|---|
| `AF-2cc19f200815fa06` | **`windows`** | **`SINAL`** | variação de temperatura, semana 07–13/09, Puglia (grande parte) | `CROP_ID`, `REGION_ID`, `ISSUE_ID` = NAO SEI · `DATE_OR_STAGE` = `2026-09-07/2026-09-13` |
| `AF-11c9e6b6ee8caa6e` | **`windows`** | **`SINAL`** | chuva da semana 07–13/09, maiores acumulados em Nociglia e Otranto (LE) | idem |

- **Não** caem em `archive`, **não** em `meeting`, e **não** só como PROVA: são objetos de `windows`, com a espécie
  `SINAL`, `LIBERACAO = LIBERADO_PARA_CLIENTE`, `RESULTADO = "NAO SEI"`.
- Prova dos dois: o item `derived:11` → RAW 36 → `IT-T3-008` → `ARIF:SETTIMANALE:2026:N38` (boletim agrometeorológico da Puglia N38).
- ⚠️ **Onde está o lugar e a data do fato:** nestes dois, `FACT_LOCATION`, `FACT_TIME` e `FACT_TIME_BASIS` estão
  **dentro de `FORA_DO_CONTRATO`**, não no topo do objeto. `LOCATION_SOURCE` e `ENTITY_SOURCE` estão no topo
  (`"TRECHO_DA_AFIRMACAO"`). Se o Casco procurar `FACT_LOCATION` só no topo, vai achar vazio.
- O pote R9 **EXPERIMENTAL** (não é para cliente) tem mais um `windows`/`SINAL` (`SG-a5d48c8cb6f73f24`, **não** liberado:
  data e lugar do documento inteiro) e 2 objetos de `market`, que são de preço e não de clima.
- Estes dois objetos vieram do `montar_r9.py`, **não** do disparador. O disparador corre o motor canônico, que hoje não
  gera este objeto (e cujo pote é reprovado pelo `ENTITY_SOURCE`, §2).
