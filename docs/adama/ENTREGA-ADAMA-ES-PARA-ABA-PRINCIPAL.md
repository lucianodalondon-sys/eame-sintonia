# ENTREGA — Gêmeo público do portfólio ADAMA España

**Para a aba principal consumir.** Tudo aqui foi observado ao vivo em
**2026-08-30T03:19:24Z**, da rede local do usuário, e está no repositório.

| | |
|---|---|
| Branch | `claude/adama-es-local-browser` |
| Repositório | `lucianodalondon-sys/eame-sintonia` |
| Status | **SAFE_FOR_MAIN_SESSION_TO_CONSUME = YES** |
| Merge | **não feito** (a missão proíbe) |

---

## 0 · Leia isto antes de usar qualquer número

Quatro níveis de verdade atravessam todos os artefatos, e **cada linha carrega o seu**:

```
OBSERVED  !=  MANUFACTURER CLAIM  !=  REGULATORY FACT  !=  DERIVED INTERPRETATION
```

- **OBSERVED** — a ADAMA publica isto na página. Nada mais.
- **MANUFACTURER CLAIM** — a ADAMA afirma isto. Não vira fato por estar escrito.
- **REGULATORY FACT** — o MAPA confirma. Só 5 relações chegaram aqui, e só depois de
  perguntar ao registro oficial, par por par.
- **DERIVED** — recorte nosso a partir do acima.

**Nada nesta entrega prova:** estoque · venda · distribuição · market share · receita ·
prioridade interna da ADAMA. `CURRENT_COMMERCIAL_AVAILABILITY` é `NAO_SEI` para os 56
produtos, e continua sendo.

---

## 1 · Os arquivos

Todos em `data/samples/`, versionados.

| arquivo | o que é | tamanho |
|---|---|---|
| **`ADAMA-ES-PRODUCT-INTELLIGENCE.json`** | o artefato principal. Todas as estruturas. | 834 KB |
| `ADAMA-ES-CENSO-MANIFEST.csv` | 1 linha por produto (56). Abre no Excel. | 24 KB |
| `ADAMA-ES-DOCUMENTOS-MANIFEST.csv` | 1 linha por documento (147), com sha256. | 72 KB |
| `ADAMA-ES-CONFIRMACAO-REGULATORIA-DO-PAR.json` | os 5 pares contra o MAPA. | 9 KB |
| `ADAMA-ES-MAIZE-PUBLIC-PORTFOLIO-MAP.json` | milho — 15 produtos. | 34 KB |
| `ADAMA-ES-OLIVE-PUBLIC-PORTFOLIO-MAP.json` | olivar — 8 produtos. | 25 KB |
| `ADAMA-ES-WINTER_CEREALS-PUBLIC-PORTFOLIO-MAP.json` | cereais de inverno — 15. | 41 KB |
| `ADAMA-ES-PORTFOLIO-POR-CULTIVO.json` | 132 cultivos → produtos. | 126 KB |
| `ADAMA-ES-PORTFOLIO-POR-ISSUE.json` | 67 problemas → produtos. | 41 KB |

Método completo, com o que falhou e por quê: `docs/adama/COLETA-LOCAL-NAVEGADOR-2026-08-30.md`

**Os 138 PDFs não estão no Git** (296 MB). Estão no disco local em
`data/raw/ES/adama-website/documentos/`. Ver seção 7.

---

## 2 · O que foi capturado, em números

| estrutura | linhas | observação |
|---|---|---|
| PRODUCTS | **56** | catálogo inteiro, 0 falha de leitura |
| DOCUMENTS | 147 | 138 baixados, 9 falhos com motivo |
| CROP_RELATIONS | 717 | **594 declaradas** + 123 só citadas — ver §4 |
| ISSUE_RELATIONS | 184 | |
| CROP_ISSUE_RELATIONS | **5** | e os 5 confirmados pelo MAPA — ver §5 |
| CROP_DOSE_RELATIONS | 26 | cultivo × dose, sem problema. **Não é par.** |
| APPLICATION_WINDOWS | 3 | |
| ACTIVE_INGREDIENTS | 73 | 50 substâncias distintas |
| MODES_OF_ACTION | 19 | 12 códigos distintos |
| CLAIMS | 35 | 29 técnicos · 5 regulatórios · 1 comercial |
| TECHNOLOGIES | 1 | FullPage® |
| PRODUCT_RELATIONS | 1 | ANIBAL → HERBOLEX |
| VIDEOS | 3 | YouTube |
| RELATED_CONTENT | **0** | o site não publica. Zero medido, não falha. |
| AMBIGUOUS_TERMS | 212 | termos não resolvidos, listados em vez de chutados |

---

## 3 · Censo — 56 produtos

| categoria | nº |
|---|---|
| Control de Malas Hierbas | 31 |
| Control de Enfermedades | 16 |
| Control de Plagas | 8 |
| Mejora de Cultivos | 1 |

Duas contagens independentes batem: âncoras no catálogo × categoria derivada da URL de
cada ficha. Sem duplicata, sem página com falha.

**Contra o relato externo de 55: +1 herbicida.** As outras três categorias são idênticas.
Não digo qual produto entrou — o relato de terceiro não tinha lista nominal, e afirmar
sem lista seria inventar.

**Não entraram:** o relato de 55 (não é observação nossa) · o snapshot de 58 (cache
antigo) · a página `Descargar documentos` (é linkada, mas não abre — inflava em 1).

### Os 56, com registro e substância

**Control de Malas Hierbas (31)**

| produto | registro | substâncias |
|---|---|---|
| AGIL | 19140 | Propaquizafop |
| Alister | 24156 | Diflufenican |
| ANIBAL | 23912 | Diflufenican; Clortoluron |
| BASTOS | 18.087 | Prosulfocarb |
| COLTRANE | ES-00205 | Dicamba; Mesotriona |
| COTTONEX 50 SC | 15454 | Fluometuron |
| COTTONEX NEOPRO | 24583 | Fluometuron; Terbutilazina |
| DIODE 100 | ES-01677 | Mesotriona |
| DISCOVERY | ES-00711 | Fluroxipir |
| ELEGANT | ES-00198 | Florasulam |
| GOLTIX 700 SC | 22478 | Metamitrona |
| GOLTIX SILVER | ES-01603 | Metamitrona; Quinmerac |
| GOLTIX UNO | ES-00564 | Metamitrona; Etofumesato |
| HERBOLEX | ES-00742 | Glifosato |
| HIGHCARD | ES-01876 | Quizalofop-p-etil |
| KAMPAI | ES-01209 | Florasulam; Fluroxipir-meptyl; Pinoxaden |
| LEGACY PLUS | 24004 | Clortoluron; Diflufenican |
| NICOPERTS | 24.887 | Nicosulfuron |
| NIKITA | ES-00474 | Dicamba; Mesotriona; Nicosulfuron |
| ORDAGO CAPS | ES-00499 | Pendimetalina |
| ORDAGO SC | 25551 | Pendimetalina |
| POSTSCRIPT 80 | ES-01516 | Imazamox |
| ROMIN | 24.762 | Petoxamida |
| SONAVIO | ES-01867 | Bifenox |
| SULCOTREK | ES-00142 | Sulcotriona; Terbutilazina |
| SULTAN N | 25050 | Metazacloro |
| SUNBRIGHT | ES-01366 | Aclonifen; Imazamox |
| TOPIK 24EC | 19548 | Clodinafop-Propargil |
| TRIMMER SX | ES-00141 | Tribenuron-metil |
| TRINITY | 25667 | Diflufenican; Clortoluron; Pendimentalina¹ |
| TRINITY PACK | NÃO SEI | — (é pack, não tem registro único) |

**Control de Enfermedades (16)**

| produto | registro | substâncias |
|---|---|---|
| AVASTEL | ES-01818 | Protioconazol; Fluxapirosad² |
| BANJO | ES-01767 | Fluazinam |
| CUPROXI FLO | 19232 | Oxicloruro de cobre |
| FOLPAN 80WDG | 19994 | Folpet |
| FOLPAN GOLD | 24397 | Folpet; Metalaxil-M |
| GARMIL | 21.714 | Ciprodinil; Fludioxonil |
| KONA | 25186 | Mandipropamid |
| MAVITA 250 EC | 18767 | Difenoconazol |
| MERPAN 80WG | 13188 | Captan |
| MIRADOR | 22000 | Azoxistrobin |
| NEPTUNE | ES-00211 | Oxicloruro de cobre; Tebuconazol |
| NIMROD QUATTRO | 13261 | Bupirimato |
| ORISOS | 16.633 | Penconazol |
| SPYRALE | 21739 | Difenoconazol; Fenpropidin |
| TRICUPROXI F | 21506 | — (a ficha não publica concentração) |
| VINERGY | ES-01463 | Fosfonatos de Potasio; Folpet |

**Control de Plagas (8)**

| produto | registro | substâncias |
|---|---|---|
| APHOX | 11826 | Pirimicarb |
| COSAYR | ES-01942 | Clorantraniliprol |
| FADEUS | 25.454 | Lambda Cihalotrin; Clorantraniliprol |
| KENDO | 24942 | — (a ficha nomeia lambda cihalotrin, sem concentração) |
| KLARTAN EW | 23.858 | Tau-fluvalinato |
| LAMDEX EXTRA | 17091 | Lambda Cihalotrin |
| LEBRON | 17502 | — (a ficha diz "Teflutrin 0,5", sem unidade) |
| METENAL | 12469 | Metaldehído |

**Mejora de Cultivos (1)** — BREVIS · ES-00073 · Metamitrona

> Os 4 sem substância lida **não são falha de leitura**: em 3 deles a própria página não
> publica a concentração. O texto cru fica em `COMPOSITION_TEXT_PUBLICADO`.
>
> ¹ A ADAMA escreve **"Pendimentalina"** (com "n" a mais) na ficha do TRINITY e
> "Pendimetalina" nas do ORDAGO. Mantivemos a grafia de cada ficha: normalizar em
> silêncio esconderia que a fonte é inconsistente.
> ² A ADAMA escreve **"FLUXAPIROSAD"**; a denominação comum internacional é
> *fluxapyroxad*. Não corrigimos a fonte.

---

## 4 · A distinção que mais importa para quem for usar

**Cultivo DECLARADO ≠ cultivo CITADO.**

Toda ficha tem um bloco `Cultivos` — a lista que a própria ADAMA declara para o produto.
Isso é diferente da palavra aparecer em algum lugar do texto (comparação, contexto, nota).

- **594 relações declaradas** — use estas para portfólio por cultura.
- **123 só citadas** — não some com as de cima.

Cada linha de `CROP_RELATIONS` carrega `DECLARATION_SOURCE` com um dos dois valores. As
visões por cultura (§6) já filtram só as declaradas.

**Exemplo concreto:** no milho, 15 produtos declaram e 20 outros apenas mencionam. Somar
os dois daria 35 e estaria errado.

---

## 5 · Regulatório

### Crosswalk com o registro espanhol (ROPF)

| estado | nº |
|---|---|
| MATCHED_EXACT | **41** |
| MATCHED_WITH_EVIDENCE | 2 |
| AMBIGUOUS | 1 |
| ADAMA_SITE_ONLY | 12 |
| ROPF_ONLY | 52 |

Os quatro primeiros somam 56 — fecham o catálogo, o que prova que cada número veio de
classificar entrada por entrada.

⚠️ **96 registros vigentes no ROPF e 56 entradas no catálogo contam unidades diferentes.**
Um produto pode ter vários registros; um registro pode não ter exposição comercial.
**Nunca subtraia 96 − 56.** A diferença só vira achado depois do crosswalk.

### Os 5 pares, confirmados no registro oficial

| par | registro | conjunto do MAPA | veredito |
|---|---|---|---|
| ARROZ × Dicotiledóneas | ES-01516 · POSTSCRIPT 80 | 38 registros | **CONFIRMED** |
| CEBADA × Malas hierbas | 25667 · TRINITY | 12 | **CONFIRMED** |
| CENTENO × Malas hierbas | 25667 · TRINITY | 6 | **CONFIRMED** |
| TRIGO × Malas hierbas | 25667 · TRINITY | 16 | **CONFIRMED** |
| TRITICALE × Malas hierbas | 25667 · TRINITY | 6 | **CONFIRMED** |

Todos titulados à ADAMA Agriculture España, todos `Vigente`. O casamento é pelo **número
de registro**, nunca por nome comercial. Estes 5 são os únicos com `EVIDENCE_LEVEL =
REGULATORY_FACT`.

**Descoberta útil para a aba principal: o MAPA responde normalmente.** O bloqueio é só da
ADAMA. A rota do par (`POST /regfiweb/Exportaciones/ExportJsonProductos` com `idCultivo`
+ `idPlaga`) está executável, custa uma requisição por par, e a tabela de IDs (448
cultivos, 708 problemas) já está no repo.

---

## 6 · Recortes prontos

### Milho — 15 produtos (12 `MAÍZ` + 3 `MAÍZ DULCE`)

| produto | tipo | registro | substâncias |
|---|---|---|---|
| COLTRANE | herbicida | ES-00205 | Dicamba; Mesotriona |
| DIODE 100 | herbicida | ES-01677 | Mesotriona |
| DISCOVERY | herbicida | ES-00711 | Fluroxipir |
| NICOPERTS | herbicida | 24.887 | Nicosulfuron |
| NIKITA | herbicida | ES-00474 | Dicamba; Mesotriona; Nicosulfuron |
| ORDAGO CAPS | herbicida | ES-00499 | Pendimetalina |
| ORDAGO SC | herbicida | 25551 | Pendimetalina |
| ROMIN | herbicida | 24.762 | Petoxamida |
| SULCOTREK | herbicida | ES-00142 | Sulcotriona; Terbutilazina |
| COSAYR | inseticida | ES-01942 | Clorantraniliprol |
| FADEUS | inseticida | 25.454 | Lambda Cihalotrin; Clorantraniliprol |
| KENDO | inseticida | 24942 | (não publicada) |
| LAMDEX EXTRA | inseticida | 17091 | Lambda Cihalotrin |
| LEBRON | inseticida | 17502 | (não publicada) |
| MIRADOR | fungicida | 22000 | Azoxistrobin |

### Olivar — 8 produtos
CUPROXI FLO · KENDO · ANIBAL · AGIL · NEPTUNE · LAMDEX EXTRA · TRICUPROXI F · DISCOVERY

### Cereais de inverno — 15 produtos
Trigo 14 · Cevada 14 · Centeio 8 · Triticale 6
KENDO · Alister · KLARTAN EW · ORDAGO SC · MIRADOR · BASTOS · TRINITY · METENAL ·
ELEGANT · LAMDEX EXTRA · TOPIK 24EC · AVASTEL · KAMPAI · TRIMMER SX · LEGACY PLUS

### Cultivos com mais produtos

TOMATE 15 · CEBADA 14 · PATATA 14 · TRIGO 14 · BERENJENA 12 · **MAÍZ 12** ·
COLIFLOR 11 · FRUTALES DE PEPITA 11 · ALCACHOFA 10 · BRÉCOL 10 · REPOLLO 10

### Problemas mais cobertos

MALAS HIERBAS 46 · Dicotiledóneas (hoja ancha) 28 · LEPIDÓPTEROS 8 · ÁFIDOS/PULGONES 8 ·
Monocotiledóneas 6 · **Repilo del olivo (Venturia oleaginea) 6** · VALLICO 5

### Modos de ação publicados

FRAC 3 · 7 · 29 · M · M01 | HRAC 1 · 2 · 4 · A · K1 | IRAC 1A · 3A

---

## 7 · Documentos — 138 baixados de verdade

| | |
|---|---|
| descobertos | 147 |
| baixados | **138** |
| falhos | 9 |
| bytes | 295.911.775 (296 MB) |
| sha256 distintos | 138 (nenhum conteúdo repetido) |
| conferência | todos com magic `%PDF` e mime `application/pdf`; 138/138 hashes reconferidos |

Por tipo: **55 rótulos comerciais** · **55 fichas de segurança (FDS)** · 23 folhetos ·
9 fichas de registro · 5 outros.

Os 9 falhos são **links podres da própria ADAMA** para PDFs do MAPA em URLs que hoje dão
404 — dois daqueles domínios (`mapama.gob.es`, `magrama.gob.es`) nem resolvem mais.
Registrado como `FAILED` com o código. **Falha de link não é ausência de documento.**

### ⚠️ Pendência de storage

Os PDFs estão **só no disco local** (`data/raw/ES/adama-website/documentos/`, fora do
Git). Não havia credencial do Supabase nesta máquina, e a missão proíbe procurar segredo.

O manifesto com `SHA256`, `BYTES`, `MEDIA_TYPE`, `URL` e `STORAGE_KEY` sugerido de cada
um está versionado em `ADAMA-ES-DOCUMENTOS-MANIFEST.csv`. Quem tiver a credencial sobe
para `raw/ES/adama-website/<PRODUCT_ID>/<sha16>-<filename>` e confere pelo hash.

**Se essa máquina for reformatada antes do upload, os 296 MB se perdem.**

---

## 8 · Os buracos, nomeados

| o quê | por quê | onde provavelmente está |
|---|---|---|
| **Só 5 pares cultivo × problema** | a ADAMA quase não publica tabela cultivo×problema em HTML. Das 56 fichas, 14 têm tabela e quase todas são `CULTIVO × DOSE`, sem coluna de agente. Cruzar as duas listas seria cartesiano. | **dentro dos 55 rótulos em PDF, já baixados** |
| APPLICATION_WINDOWS = 3 | BBCH e intervalo quase não aparecem no HTML | rótulos em PDF |
| RELATED_CONTENT = 0 | a única ocorrência de "relacionad*" nas 56 fichas é "Documentos relacionados". O site não publica artigo/webinar/campanha na página de produto. | não existe na fonte |
| TECHNOLOGIES = 1 | só FullPage® é marcado com ® nas fichas. **Asorbital® aparece na home e em nenhuma das 56 fichas.** | página institucional, não coletada |
| Página `Descargar documentos` | atrás de portão duro da Akamai (devolve 3 KB de desafio) mesmo do navegador local | pode ter documentos que as fichas não linkam |
| AMBIGUOUS_TERMS = 212 | termos que casam mais de um rótulo oficial. Listados, não resolvidos por palpite. | resolução exige decisão humana |

**O próximo passo de maior retorno:** ler os 55 rótulos em PDF. É onde mora a tabela
`CULTIVO × AGENTE × DOSE × PRAZO`, que é o que falta para o gêmeo ficar completo. Os
arquivos já estão no disco.

---

## 9 · Confiança

- **41 guardas** em `tests/test_adama_es.py`, 0 falha. Eram 28 — os 13 novos guardam
  defeitos **medidos** nesta coleta, não imaginados.
- **149 testes** nas outras 10 suítes, todas OK.
- **Verificação manual 5/5** (ficha viva × saída do parser): KAMPAI, AVASTEL, COSAYR,
  BREVIS, COLTRANE.
- 0 erro cartesiano · 0 erro de tipo de documento · 0 fuzzy-match silencioso.

### 10 defeitos do coletor que só a coleta ao vivo revelou

Todos corrigidos, todos com guarda:

1. Rota do catálogo apontava para URL inexistente.
2. Categoria vinha do **menu** do site — as 56 fichas saíam como fungicida.
3. Documento sem extensão na URL era ignorado — **0 documentos em 56 fichas**.
4. Linha `CULTIVO × DOSE` era descartada inteira.
5. Unidade da dose vive no cabeçalho ("DOSIS (L/Ha)"), e a ADAMA parte uma tabela em
   vários `<table>` (7 doses → 26 com a herança de cabeçalho).
6. Concentração em `g/l` não era lida — COLTRANE saía sem nenhum ingrediente ativo.
7. Registro escrito em três grafias — 30 fichas saíam sem número (**crosswalk 20 → 41**).
8. Ingrediente ativo vinha da **tabela de dose** — CUPROXI FLO saía com
   "Ha Tuberculosis 0,15%".
9. Código de modo de ação era a **palavra seguinte** — "FRAC Grupo", "HRAC como".
10. Filtro do bloco `Cultivos` apagava cultivo real quando o nome também titulava outra
    seção (AVASTEL perdia o trigo).

E um defeito de **teste**: um guarda proibia o número 41 aparecer no crosswalk (porque
96−55=41). Quando o dado melhorou, `MATCHED_EXACT` virou 41 de verdade e o guarda
derrubou um número legítimo. Testar por *valor* era o erro; agora prova *partição*.

---

## 10 · Como rodar de novo

```bash
python3 scripts/adama_intelligence.py --build 2026-08-30T03:19:24Z > data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json
python3 scripts/adama_intelligence.py --manifest 2026-08-30T03:19:24Z > data/samples/ADAMA-ES-CENSO-MANIFEST.csv
python3 scripts/adama_es_confirmacao_mapa.py --build
python3 scripts/adama_es_visoes.py --build
python3 tests/test_adama_es.py
```

Exige os pacotes de captura em `data/raw/ES/adama-website/` (não versionados). Sem eles,
o portão devolve `SEM_CAPTURA` e o censo devolve `NOT_COLLECTED` — **nunca 0**.

Para capturar de novo, é preciso um navegador na máquina do usuário: `curl`, `requests`
e `urllib` levam 403 da Akamai mesmo saindo da rede doméstica. O método está em
`docs/adama/COLETA-LOCAL-NAVEGADOR-2026-08-30.md`.
