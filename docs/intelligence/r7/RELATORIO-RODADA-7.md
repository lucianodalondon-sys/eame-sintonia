# RODADA 7 — INTELLIGENCE EXPERIMENTAL (Sala 204 → 242) · EXPERIMENTAL / NAO_PARA_CLIENTE

```text
ORDEM       coordenador: Sala 204→242 às 15:27 (LINHA-BUSCA-RAW-20260927T152708, 38 páginas achadas por busca, D93,
            fontes CANDIDATA/ACHADO_POR_BUSCA). Vivo = lote 4 (18461b92). R7 com G0/v4 + D112; POTE-R7 com o gerador ce775ff5.
CORRIDA     IR-e09acab6365032523d6e   (G0/v4 · DONE · IR novo: corte novo)
CHAVE       IR-e09acab6365032523d6e@e8ea4199b33a458e
MOTOR       int-intake-g0v4-v1 @ a5db06c4 (limpo)      PILOTO 2b4e095f      GRAFO do vivo 18461b92 (blob = eb3a7b1d)
CÓPIA       27/09 18:30:35 UTC · BEGIN READ ONLY · transaction_read_only on/on/on · IMPRESSOES ANTES = DEPOIS
            sala_de_espera 242 · revisao 730 · raw_asset 2243 · collection_run 482
SALA        nada escrito; nada publicado; nada ao cliente
```

## 1 · Quantos dos 242 entraram

| | R6 | R7 |
|---|---|---|
| READY na cópia | 204 | **242** |
| no livro da corrida (intake) | 204 | **242** (0 descartados antes do livro) |
| ANCORADO (data do fato provada) | 10 | 19 |
| FUTURO em relação à captura | 10 | 10 |
| UNKNOWN_WINDOW (FACT_TIME = NAO SEI, com motivo) | 184 | 213 |
| SINAIS (passaram G0) | 10 | **19** (+9, todos das 38 novas) |
| documentos distintos · SOURCE_ID | 184 · 47 | 222 · 75 |
| % sinais da fonte dominante | 60 % | 31,6 % |

Os 9 sinais novos têm todos data do fato provada, mas **nenhum é atual**: idades 138, 156, 172, 172, 635, 3557, 7940 dias,
e 2 «0 dias» que são anos inteiros («annata 2026», «2025/2026», precisão YEAR). Não dão ACT_NOW.

## 2 · Regras D112 aplicadas (e o que se mediu)

- **Lugar só do texto/cabeçalho escrito**: cada nome do `fact_location` tem de estar num trecho «…» da BASE.
  242 → SUSTENTADO 30 · NAO SEI 211 · **LOCAL_NAO_SUSTENTADO 1** (IT-T5-010: «Ferrara» sem trecho). Das 38: 11 sustentados, 27 NAO SEI.
- **ENTITY_SOURCE**: o READY não o tem (0/242; LOCATION_SOURCE 0/242). A única procedência por entidade é a secção do
  boletim (`PROBLEMA.SECOES[].TRECHO`): 1076 pares cultura×praga em 35 itens. Cultura do DOCUMENTO = ENTITY_SOURCE NAO SEI
  e **não vira CROP_ID**; no pote o CROP_ID só leva a cultura que a interpretação ligou à substância, com a procedência.
- **NAO SEI** onde falta evidência; **fonte × interpretação**: cada crossing traz `FONTE` (trecho literal, culturas do
  documento, local) e `INTERPRETACAO` (regra nossa X2/X3/X3w/X3h e o estado) separados (ANALISE-R7.json).

## 3 · Cruzamentos (pergunta: «o rótulo ADAMA lido autoriza a substância citada na cultura do boletim?»)

**86 tentados** = 39 pelo piloto (famílias IT-T3) + 47 por **extensão declarada** às fontes CANDIDATAS (o piloto só olha IT-T3;
corri a mesma pergunta nas 38 novas e marquei VIA=EXTENSAO_DECLARADA — fonte candidata ≠ fonte registada).

| estado final (depois de conferir o sentido) | todos | das 38 novas |
|---|---|---|
| POSSIBLE_ANSWER_YES_A_CONFIRMAR | **5** | 5 |
| POSSIBLE_ANSWER_NO (não está na referência lida) | 29 | 28 |
| PARTIAL_GRAO_INCOMPATIVEL | 48 | 46 |
| NOT_POSSIBLE (sem cultura) | 4 | 4 |

- **Os 3 antigos** não mudaram: ARIF n.37 e n.38 × taufluvalinate = PARTIAL_GRAO_INCOMPATIVEL; APOL × azoxistrobina (olivo) = NO.
- **Os 5 «sim a confirmar»** são todos boletins de **uma só cultura** de fontes CANDIDATAS:
  CAND-1209 (Cantina Negrar, vite, 30/06) azoxistrobina · CAND-1221 (Arezzo, vite) folpet · CAND-1223 (Reggio E., melo) captano ·
  CAND-1228 (Cantina Negrar, vite, 12/05) folpet · CAND-1229 (Parma, flavescenza) taufluvalinate.
  «Sim» = o rótulo ADAMA lido cobre essa substância nessa cultura. **Não** prova uso, recomendação de produto ADAMA,
  lugar nem momento; e todos são de maio–julho (fora de janela).
- ⚠️ **Honestidade de método**: a primeira passagem deu 19 «sim». Ao ler os trechos vi que os «troços» dos boletins sem
  secções eram o documento inteiro (até 989 580 caracteres), ou seja, a mesma falha de grão da R6. Criei **nesta rodada**
  duas regras: X3w (cultura a ≤ 400 caracteres da substância) e X3h (boletim de uma cultura nomeada no cabeçalho = D112
  «cabeçalho escrito»). Resultado: 19 → 0 → 5. Como as regras nasceram depois de ver os dados, **precisam de regressão**
  antes de valerem (caso a abrir: X3w/X3h).
- **Cruzamentos novos com as chaves da Sala**: 83 (todos das 38). **Fechados com «sim» defensável: 0.**

## 4 · Corte vertical olivo × mosca-da-oliveira (SONDA W0-W8; não é CAP-WIN instalada)

- 13 itens com o par **por secção** (8 das 38 novas: Assoprol Umbria ×2, Confagricoltura Siena, Modena, Abruzzo, ARPA Veneto, ARSAC Calabria, FruitJournal).
- Apoio válido (secção + tempo CURRENT + local sustentado + medição declarada): **1** — ARIF n.38 (IT-T3-008, 7–13/09/2026,
  Puglia/Lecce): «…poche catture di mosca (Bactrocera oleae)… comunque al disotto delle soglie di intervento».
- Correção da própria sonda: «nei casi di accertata presenza… si consiglia di intervenire» é **recomendação condicional**, não
  soglia superada (a 1.ª passagem tinha-a como CONFLICTING). Regra escrita no JSON (LEI_W).
- Fora: tempo não CURRENT 11 (APOL continua sem data do fato; Assoprol sem data), local não sustentado 9, sem medição declarada 9.
- **WINDOW_OPEN_NOW = NO em Puglia/Lecce (1 originador)**; resto de Itália = NAO SEI. ACT_NOW = NÃO.
- **Resultado: NO_DEFENSIBLE_ACTION_YET** — vigiar, não tratar. Assoprol Umbria (novo) diz o mesmo em texto («catture ancora
  limitate ma in lieve aumento»), mas sem data nem lugar provados, não conta.

## 5 · O que as 38 novas acrescentaram

- 38 itens · 28 fontes (23 CANDIDATAS) · todos universo T3 (boletins/defesa) · 38 com praga, 31 com cultura, 29 com pares por secção.
- Tempo: 9 ANCORADO, 29 NAO SEI; published_at só em 16; **6 publicadas antes de 2026** (2022–2025: Frontiers, uvadatavola, antropocene…).
- **3 páginas fora de Itália** (Ticino/CH: ti.ch ×2, agrometeo.ch) entraram como T3 italiano → pedido à Coleta (âmbito).
- Conteúdo: boletins de vite (peronospora/oidio/flavescenza), melo, nocciolo, cimice asiatica, Popillia; guias técnicos (tignoletta).
  Dão **muita estrutura** (cultura, praga, fase) e **pouca atualidade**: nenhum sinal atual, nenhum apoio novo ao corte.
- **Achados / oportunidades: 0 / 0. NO_DEFENSIBLE_ACTION_YET.**

## 6 · POTE-R7 (gerador do dono `pacote/pote_intelligence_casco.py` @ ce775ff5, cópia desanexada já removida)

- SCHEMA POTE_INTELLIGENCE_CASCO/v2 · **INTELLIGENCE_RUN_ID no topo** = IR-e09acab6365032523d6e · `conferir_pote` do dono: **PASSA (0 violações)**.
- 47 objetos · 245 recusados (visíveis). Toda prova com URL (0 NAO SEI); PUBLICADO_EM presente em todas, «NAO SEI» em 20 (declarado, não escondido).
- Compartimentos: future 10 · market 6 (SINAL, não MARKET_CHANGE) · windows 2 (ARIF) · science 2 · portfolio 2 · archive 22 · sources 3.
- **Defeito novo C1 (Coleta, bloqueia o pote): as 38 novas não têm `document_key` no raw_asset** (0/204 antes, 38/242 agora).
  O contrato v2 exige DOCUMENT_ID na prova → **nenhum objeto das 38 chegou ao pote** (199 recusas «falta DOCUMENT_ID»).
- P7 continua (só G0=PASSOU entra: APOL «NO» e 44 fontes recusadas); P8 continua.
- O compartimento portfolio do v2 **não transporta CROSSING_STATE** (as chaves são as do T4); o estado viaja só no PORQUE → pedido ao dono do pote.

## 7 · Pedidos (sem escolher coletor, URL ou rota)

| para | pedido |
|---|---|
| Coleta | DOCUMENT_ID (document_key) nas 38 da LINHA-BUSCA-RAW — REPROCESS_FIRST |
| Coleta | âmbito: 3 páginas suíças como T3 Itália (INVESTIGATE) |
| Coleta | APOL e Assoprol: data do fato (período do boletim já escrito no texto) |
| Coleta | secções por cultura nos boletins sem «Situazione Fenologica» (D18 continua) |
| Pote (bridge) | P7 (objetos atemporais), CROSSING_STATE no portfolio |
| Intelligence (eu) | regressão para X3w/X3h e para LEI_W (condicional ≠ soglia) antes de subirem para o motor |

## Arquivos
`copia/` (PROVA_RO*, IMPRESSOES_*) · `saida/` (LIVRO, RENDIMENTO) · `analise_r7.py` · `ANALISE-R7.json` · `analise.out.txt` ·
`../PARA-O-CASCO-R7/` (montar_entrada_r7.py, ENTRADA-DO-POTE-R7.json, POTE-R7.json, MANIFESTO.json) · SHA256SUMS.txt
