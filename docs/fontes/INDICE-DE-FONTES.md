# ÍNDICE DE FONTES — SINTONIA EAME

> **Este ficheiro é gerado.** Não o edite à mão: edite
> [`ATLAS-DE-FONTES-EAME.md`](ATLAS-DE-FONTES-EAME.md) ou
> [`CONTRATOS-DAS-FONTES-EAME.md`](../operacao/CONTRATOS-DAS-FONTES-EAME.md)
> e rode `py system-map/scripts/generate_system_map.py`.

O atlas guarda a ficha inteira de cada fonte. Esta página é só a porta de
entrada: quantas fontes existem, de que países, e quais delas a máquina já
sabe buscar sozinha.

---

## O NÚMERO

| | |
|---|---|
| fichas completas no atlas | **23** |
| dessas, com contrato de busca escrito | **5** |
| palavras de busca medidas no código | **103** em 34 grupos |
| endereços que o código realmente chama | **40** |

> ### ⚠ O cabeçalho do atlas e as fichas não batem
>
> O cabeçalho do atlas diz **37 fontes registradas**
> (linha 9). Fichas completas, com `SOURCE_ID` válido, há
> **23**. Faltam **14**.
>
> As fontes que faltam podem existir de verdade — mas sem ficha, ninguém
> consegue saber o que elas têm. Isto não é corrigido automaticamente:
> é decisão de gente escrever as fichas ou acertar o contador.

---

## A ESCADA — o que uma fonte tem de subir

A distância entre os degraus é o trabalho que falta fazer. Subir exige
gente: nenhum degrau se sobe sozinho.

| # | degrau | o que é | quantas | mora em | sobe como |
|---|---|---|---|---|---|
| 1 | **CANDIDATA** | alguem viu que existe. Ninguem abriu ainda. | **0** | `candidatas/FONTES-CANDIDATAS.json` | abrir, olhar o que entrega e guardar um exemplo real |
| 2 | **REGISTADA** | tem ficha no atlas, com exemplo real guardado. | **18** | `docs/fontes/ATLAS-DE-FONTES-EAME.md` | escrever COMO se busca e o que fazer quando quebrar |
| 3 | **CONTRATADA** | tem contrato de busca escrito. | **5** | `docs/operacao/CONTRATOS-DAS-FONTES-EAME.md` | por a busca a correr sozinha, num workflow |
| 4 | **AUTOMATICA** | a maquina vai la sozinha, sem ninguem por perto. | — | `.github/workflows/` | — |

### A porta de entrada

Fonte nova entra por `candidatas/fonte_nova.py` — na mão, ou de dentro de uma coleta
que tropeçou nela. **O que entra é candidata, nunca fonte.**

```bash
py candidatas/fonte_nova.py --tipos          # os tipos aceites
py candidatas/fonte_nova.py --listar         # a fila, agrupada por tipo
py candidatas/fonte_nova.py \
    --tipo BASE_OFICIAL --pais ES --nome "..." --url https://... \
    --para-que "para que serve" --quem-viu voce --onde-viu "onde viu"
```

Hoje há **0** candidata(s) na fila,
em `candidatas/FONTES-CANDIDATAS.json`.

`--para-que` é obrigatório de propósito: fonte sem uso declarado vira
entulho — daqui a seis meses ninguém sabe por que ela foi anotada.

---

## CONTAS PÚBLICAS, POR PLATAFORMA

Registradas em `data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json`.
**Estar na lista não é autorização:** só entra na coleta quem tem
identidade PROVADA e é conta local do país.

| plataforma | mapeadas | autorizadas a coletar |
|---|---|---|
| **FACEBOOK** | 17 | 10 |
| **INSTAGRAM** | 7 | 5 |
| **LINKEDIN** | 6 | 0 ⚠ |
| **YOUTUBE** | 14 | 7 |

Total: **44** contas, **22** autorizadas.

---

## A DIFERENÇA QUE IMPORTA

| | |
|---|---|
| **fonte registrada** | alguém abriu, olhou e guardou um exemplo real |
| **fonte com contrato** | a **máquina** sabe ir lá sozinha, sabe o que esperar de volta e o que fazer quando quebrar |

A distância entre as duas é o trabalho que falta fazer. Uma fonte sem
contrato só funciona enquanto a pessoa que a descobriu estiver por perto.

---

## POR PAÍS

### ESPANHA · 6 fontes · 2 com contrato de busca

| id | fonte | assunto | estado | a máquina busca? |
|---|---|---|---|---|
| `ES-T3-001` | Datos de seguimiento de plagas y enfermedades en las estac | T3 · Praga e doenca | 🟢 GREEN | sim |
| `ES-T4-001` | Jerarquía de especies vegetales · Clasificación de plagas | T4 · Regulatorio | 🟢 GREEN | **não** |
| `ES-T4-002` | Autorizaciones excepcionales vigentes | T4 · Regulatorio | 🟢 GREEN | **não** |
| `ES-T4-003` | Registro de Productos Fitosanitarios — aplicação de consul | T4 · Regulatorio | ⚪ NAO SEI | **não** |
| `ES-T4-005` | Registro Oficial de Productos Fitosanitarios — rotas públi | T4 · Regulatorio | 🟢 GREEN | sim |
| `ES-T5-002` | OpenAlex, recorte espanhol declarado | T5 · Preco e mercado | 🟢 GREEN | **não** |

### EUROPA · 11 fontes · 1 com contrato de busca

| id | fonte | assunto | estado | a máquina busca? |
|---|---|---|---|---|
| `EU-T1-001` | Crop production in EU standard humidity by NUTS 2 region | T1 · Cultura e producao | 🟢 GREEN | **não** |
| `EU-T1-002` | Crop production in EU standard humidity | T1 · Cultura e producao | 🟢 GREEN | **não** |
| `EU-T10-001` | European Commission — Agri-food Data Portal (cereal prices | T10 · Politica e subsidio | 🟢 GREEN | **não** |
| `EU-T12-001` | CELLAR / EU Publications Office — camada de política agríc | T12 · Substancia ativa | 🟢 GREEN | **não** |
| `EU-T2-001` | NASA POWER — Daily Point (community AG) | T2 · Clima e tempo | 🟢 GREEN | **não** |
| `EU-T2-002` | NUTS_LB_2024_4326_LEVL_2 (label points) | T2 · Clima e tempo | 🟢 GREEN | **não** |
| `EU-T2-003` | Open-Meteo Historical Weather API (ERA5) | T2 · Clima e tempo | ⚪ NAO SEI | **não** |
| `EU-T3-001` | EPPO Global Database | T3 · Praga e doenca | ⚪ NAO SEI | **não** |
| `EU-T4-001` | CELLAR / EU Publications Office (Official Journal of the E | T4 · Regulatorio | 🟢 GREEN | sim |
| `EU-T4-002` | EU Pesticides Database | T4 · Regulatorio | ⚪ NAO SEI | **não** |
| `EU-T5-001` | OpenAlex | T5 · Preco e mercado | 🟢 GREEN | **não** |

### FRANCA · 4 fontes · 1 com contrato de busca

| id | fonte | assunto | estado | a máquina busca? |
|---|---|---|---|---|
| `FR-T13-001` | recherche-entreprises.api.gouv.fr (base SIRENE) | T13 ·  | 🟢 GREEN | **não** |
| `FR-T3-001` | Bulletins de Santé du Végétal | T3 · Praga e doenca | 🟡 YELLOW | **não** |
| `FR-T3-002` | Archive en agro-écologie de BSV | T3 · Praga e doenca | ⚪ NAO SEI | **não** |
| `FR-T4-001` | Données ouvertes du catalogue E-Phy | T4 · Regulatorio | 🟢 GREEN | sim |

### ITALIA · 2 fontes · 1 com contrato de busca

| id | fonte | assunto | estado | a máquina busca? |
|---|---|---|---|---|
| `IT-T3-001` | IT-T3-001 | T3 · Praga e doenca | 🟡 YELLOW | **não** |
| `IT-T4-001` | Fitosanitari — elenco dei prodotti fitosanitari autorizzat | T4 · Regulatorio | 🟢 GREEN | sim |

---

## AS PALAVRAS USADAS NA BUSCA

Na língua do país, sempre. Buscar em inglês devolve literatura
internacional, não a conversa técnica local.

### `regras/rotulos_censo.py:48` · 35 palavras

| grupo | palavras |
|---|---|
| `SCAPHOIDEUS_TITANUS` | scaphoideus · scafoideo |
| `FLAVESCENZA_DOURADA` | flavescenza · giallumi della vite |
| `BACTROCERA_OLEAE` | bactrocera oleae · mosca dell.oliva · mosca dell.olivo |
| `BACTROCERA_OUTRAS` | bactrocera dorsalis · bactrocera zonata |
| `OCCHIO_DI_PAVONE` | occhio di pavone · spilocaea · cicloconio · venturia oleaginea |
| `OLIVO` | olivo · oliveto · olive da · olivicol |
| `VENTURIA_MELO` | ticchiolatura · venturia inaequalis |
| `HALYOMORPHA` | halyomorpha · cimice asiatica |
| `DIABROTICA` | diabrotica |
| `OSTRINIA` | ostrinia · piralide |
| `FUSARIUM` | fusarium · fusarios |
| `ZYMOSEPTORIA` | zymoseptoria · septoria · septorios |
| `ECHINOCHLOA` | echinochloa · giavone |
| `ORYZA_CRODO` | riso crodo |
| `AMBROSIA` | ambrosia artemisiifolia |
| `POPILLIA` | popillia japonica |
| `XYLELLA` | xylella |

### `regras/sensor_coleta.py:198` · 68 palavras

| grupo | palavras |
|---|---|
| `ES-OLIVE-REPILO` | repilo del olivo · Venturia oleaginea olivo · repilo olivar tratamiento · jornada tecnica olivar repilo |
| `ES-CEREAL-SEPTORIA` | septoria trigo · septoriosis del trigo · Zymoseptoria tritici trigo · jornada tecnica cereal septoria |
| `IT-VINE-FLAVESCENCE` | flavescenza dorata vite · flavescenza dorata vigneto · giallumi della vite · convegno flavescenza dorata |
| `IT-DURUM_WHEAT-FUSARIUM` | fusariosi grano duro · micotossine grano duro · fusariosi della spiga · convegno grano duro micotossine |
| `FR-VINE-DOWNY_MILDEW` | mildiou de la vigne · Plasmopara viticola vigne · mildiou vigne traitement · webinaire mildiou vigne |
| `FR-CEREAL-SEPTORIA` | septoriose du ble · Zymoseptoria tritici ble · septoriose ble traitement · webinaire septoriose ble |
| `IT-MAIZE-WEED` | diserbo del mais · infestanti del mais · diserbo mais pre-emergenza · diserbo mais post-emergenza |
| `IT-CEREAL-WEED` | diserbo dei cereali · diserbo del grano infestanti · loietto resistente frumento · avena resistente diserbo grano |
| `IT-SOYBEAN-AMARANTHUS` | amaranto resistente soia · diserbo della soia · infestanti resistenti soia · resistenza erbicidi soia |
| `IT-SUGARBEET-WEED` | diserbo barbabietola da zucchero · diserbo bietola · infestanti barbabietola · diserbo bietola post-emergenza |
| `IT-RICE-WEED` | diserbo del riso · riso crodo diserbo · giavone risaia · diserbo risaia infestanti |
| `IT-APPLE-DISEASE` | ticchiolatura del melo · difesa del melo · ticchiolatura melo trattamenti · melo maculatura bruna |
| `IT-VINE-WEED` | diserbo del vigneto · gestione del sottofila vigneto · inerbimento vigneto · diserbo sottofila vite |
| `IT-OLIVE-BACTROCERA` | mosca delle olive difesa · Bactrocera oleae olivo · monitoraggio mosca olivo · trattamento mosca olive |
| `IT-CEREAL-SEPTORIA` | septoriosi del frumento · malattie fogliari frumento · difesa cereali a paglia · ruggine gialla frumento |
| `IT-APPLE-INSECT` | afidi del melo difesa · carpocapsa del melo · insetticidi melo difesa · difesa melo insetti |
| `IT-TOMATO-DISEASE` | peronospora del pomodoro · difesa pomodoro malattie · alternaria pomodoro · botrite pomodoro difesa |

---

Veja também: o mesmo conteúdo, navegável e ligado ao código que
faz a coleta, no **System Map** em `/system-map/` (bloco **COLETA**).
