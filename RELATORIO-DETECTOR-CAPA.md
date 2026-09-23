# RELATÓRIO — MISSÃO 6-PREP-c · O DETECTOR DE CAPA, MEDIDO A SÉRIO

Branch `detector-capa-v1`, a partir de `10d907b7`. Motor: `claude-opus-5-5`.

```
COLLECTION NÃO CORREU · NADA NA SALA · DB_WRITES = 0
curadoria/retrato_html.py, admissao/, contratos, fila, livros = INTOCADOS
Rede: só a recolha do gabarito, com as regras do canário (abaixo)
```

---

## 1 — O GABARITO DE PÁGINAS REAIS

**Recolha** — `scripts/detector_capa/colher_gabarito.py`:

* **110 sites** distintos, tirados dos contratos HTML do Curator
  (`italy_contracts_curator.json`), escolhidos de forma determinística e
  espalhados por universo (T2, T3, T5, T7, T8, T9, T10, T11, T12).
* **Egresso medido antes de cada site: IT em 109 das 110 idas registadas**
  (`149.22.91.172`, Palermo, AS212238). Zero idas BR. A que falta é a do site
  que rebentou (abaixo): foi medida, mas o registo perdeu-se no rebentamento.
* **No máximo 3 pedidos por site** (robots + 2 páginas), 1 s de pausa, robots
  lido pelo leitor da casa (`curadoria/gate_de_rota.robots_de`, UA da casa).
  **10 sites** com o índice negado pelo robots: não se pediu nada. Outros
  paragens: 19 sem link com cara de matéria, 6 sem link de navegação, 1 ligação
  cortada pelo servidor.
* ⚠️ **Um defeito meu a meio:** um `href` mal formado («Invalid IPv6 URL»)
  rebentou o leitor de links no site 32 (IT-T9-021), depois de 2 pedidos. Não
  voltei lá: marquei-o à mão como visitado antes de retomar, para não passar
  de 3 pedidos. A página de índice dele ficou em disco e **não entra na
  contagem**.
* Bytes (**36 MB, 168 ficheiros**) em `~/detector-capa-gabarito/` — fora do
  Git, da Sala e do armazém oficial. O manifesto com URL, sha256, egresso e
  hora de cada página está no repositório: `MANIFESTO-RECOLHA-V1.json`.

**Como se escolheram as páginas, e porquê assim.** Não usei o `LINK_PATTERN`
do contrato para escolher nada: se as matérias fossem escolhidas pelo padrão
e as capas fossem o `INDEX_URL`, a proposta acertava por construção. Foi
exactamente a fraqueza da medição anterior (0/76 «por construção»).

* `CAPA_INDICE` — o `INDEX_URL` do contrato (circular para a proposta: está separado)
* `MATERIA` — o link interno com a âncora mais longa (um título), sem olhar ao padrão
* `CAPA_OUTRA` — um link de navegação que **não** é o índice (contatti, chi siamo, archivio, categoria, calendario, comunicati)

**Veredito, página a página** — `GABARITO-CAPA-V1.json`, com o porquê de cada
uma. Lido o título, o texto visível e a estrutura. **Humano-proposto por mim,
não por uma pessoa: precisa de visto do dono.** Definições escritas:

```
MATÉRIA = página individual com conteúdo próprio: notícia, comunicado, aviso,
          artigo, boletim, projecto descrito
CAPA    = página de entrada ou navegação: início, listagem, contatti, chi siamo,
          calendário, arquivo, organigrama, FAQ, login, página de cortesia
```

```
PÁGINAS RECOLHIDAS   167
FORA DA CONTAGEM      21  — 13 VAZIAS (< 500 caracteres: desenhadas por JavaScript)
                            ·  6 DUPLICADAS pelo texto (redirecções para a página inicial)
                            ·  2 AMBÍGUAS (número de revista; página de serviço)
GOLD_CAPAS           109  (82 são o INDEX_URL · 27 NÃO são o índice)
GOLD_MATERIAS         37  (10 curtas: < 1500 caracteres ou < 800 em parágrafos)
DOMINIOS              85
CASOS DIFÍCEIS       10 matérias curtas · 70 capas longas (≥ 800 caracteres em parágrafo)
                     3 INDEX_URL que são, na verdade, matéria (#28, #101, #161)
```

---

## 2 — AS MEDIÇÕES (em memória; `retrato_html.py` intocado)

Comando: `py scripts/detector_capa/medir_gabarito.py`. Seis juízes sobre as
mesmas 146 páginas. O portão de hoje só reprova `CAPA_PROVAVEL`: uma capa
julgada `NAO_SEI` **atravessa** hoje.

### Todas (109 capas · 37 matérias)

| juiz | capa → MATÉRIA (calada) | capa → pessoa | **capa atravessa hoje** | matéria → CAPA (barrada) | matéria → pessoa |
|---|---|---|---|---|---|
| **ACTUAL** (só formato) | 37/109 | 26/109 | **63/109** | **6/37** | 8/37 |
| SÓ_MORADA | 0/109 | 0 | 0/109 | **25/37** | 0 |
| **PROPOSTA** (morada antes do formato) | 0/109 | 0 | **0/109** | **25/37** | 3/37 |
| PROPOSTA_SEM_PADRÃO (controlo) | 37/109 | 26/109 | 63/109 | 6/37 | 8/37 |
| V1 — só o INDEX_URL exacto é capa | 7/109 | 6/109 | 13/109 | 9/37 | 6/37 |
| V2 — desacordo → pessoa lê | 0/109 | 37/109 | 37/109 | 11/37 | 17/37 |

### Só as 27 capas que NÃO são o índice (a parte não circular)

| juiz | apanhadas | calada como matéria | para pessoa |
|---|---|---|---|
| ACTUAL | 14 | **7** | 6 |
| PROPOSTA | 27 | 0 | 0 |
| V1 | 14 | 7 | 6 |
| V2 | 20 | 0 | 7 |

### O efeito da morada separado do efeito do formato

* **O formato sozinho (ACTUAL) deixa passar mais de metade das capas**: 63/109.
  Nas capas que não são o índice, 13/27. Chama matéria a páginas iniciais
  longas (Conserve Italia, MASAF, DISAFA, CREA…) e a listagens com muito texto
  (chianticlassico.com/news, «Ultime notizie», «Comunicati stampa»).
* **A morada sozinha (SÓ_MORADA) apanha todas as capas mas barra 25/37
  matérias.** A proposta, com o formato por cima, barra as mesmas 25. **O
  formato quase não acrescenta nada à proposta**: todo o efeito, bom e mau, é
  da morada.
* **Porque barra 25 matérias:** 3 são páginas de índice que são mesmo matéria
  (o `INDEX_URL` do contrato aponta para uma notícia ou um evento); **22 são
  matérias cuja morada não casa o `LINK_PATTERN` do contrato**. Esses padrões
  são quase todos o mesmo molde genérico de WordPress
  (`^https?://host/(?!category|tag|author|wp-json…)…`), e não reconhecem
  `winenews.it/it/…`, `freshplaza.it/article/9874675/…`, `?p=9079`,
  `/-/asi-caivano…`, `…/dettaglio-news?articleId=…`.

```
SEM_PADRAO_URL = a proposta cai no detector ACTUAL, página por página
                 (medido: matrizes idênticas). Nenhum ganho, nenhuma perda.
                 ⚠️ controlo SIMULADO: todas as 85 fontes têm LINK_PATTERN; tirei-o.
```

---

## 3 — O QUE ISTO DIZ

```
DETECTOR_ACTUAL: capa→matéria 37/109 (63/109 atravessam o portão) · matéria→capa 6/37
PROPOSTA:        capa→matéria  0/109 (0/109 atravessam)          · matéria→capa 25/37
SEM_PADRAO_URL = comportamento do ACTUAL
```

1. **A minha proposta da 6-PREP-b estava errada.** Os «0/76 e 0/14» eram
   circulares, como eu próprio avisara. Num gabarito que não foi escolhido pelo
   padrão, ela **barra 68% das matérias** (25/37). Troca um erro por outro pior.
2. **O detector actual é fraco no sentido perigoso**: deixa passar 58% das
   capas (63/109), e 48% das que não são o índice (13/27). **O «0 capas» de
   qualquer relatório de coleta que confie só nele não prova grande coisa.**
3. **A proposta falha por causa dos padrões de morada dos contratos**, não
   por causa do formato. 22 de 34 matérias reais (fora dos índices) não casam o
   `LINK_PATTERN` da sua própria fonte. Isto quer dizer, provavelmente, que
   **o coletor, que usa esses padrões, também não as apanharia**. Isto é
   inferência, não o medi no coletor.

---

## 4 — RECOMENDAÇÃO (nada aplicado)

```
RECOMENDACAO = NÃO APLICAR a proposta «morada antes do formato».
```

Porquê: barra 25/37 matérias reais, e a causa (padrões genéricos) não se
corrige no detector.

O que recomendo em vez disso, por ordem e por dono, **uma mudança de régua de
cada vez**:

1. **Rotas / Curator — rever os `LINK_PATTERN`** das fontes da coorte antes de
   qualquer micro-coleta. Medido: o molde genérico falha em 22/34 matérias
   reais. Medida de sucesso: o gabarito deste relatório, re-corrido.
2. **Curator — corrigir os 3 `INDEX_URL` que apontam para uma matéria**
   (IT-T11-010 #28, IT-T2-039 #101, IT-T12-044 #161: um evento, uma notícia de pólenes,
   uma notícia de app). São defeitos de contrato.
3. **Só depois, dono de `retrato_html.py` — aplicar a V1** («a morada
   exactamente igual ao `INDEX_URL` é capa»). Medido: capas que atravessam
   63 → 13 em 109; matérias barradas 6 → 9, e as 3 a mais são exactamente os
   INDEX_URL do ponto 2 — depois de os corrigir, o custo em matérias fica 6,
   igual ao de hoje. ⚠️ **O ganho da V1 está todo nas páginas de índice**, que
   são circulares neste gabarito: nas 27 capas que não são o índice, a V1 não
   muda nada (14 apanhadas, 7 caladas). Protege contra um defeito conhecido
   (o coletor guardar a listagem como documento — 9/104 na AQUISICAO-DETALHE),
   não contra o resto. Os gémeos `.mjs` e `_kind` teriam de mudar no mesmo passo.
4. **Portão — tratar `NAO_SEI` como «pessoa lê», não como «passa».** Hoje 26
   capas NAO_SEI atravessam caladas. Isto é política, não régua: é decisão do
   dono.

A V2 (desacordo → pessoa) não passa calada nenhuma capa, mas manda 54 de 146
páginas para uma pessoa e barra 11 matérias — **não recomendo** com os padrões
de hoje.

---

## 5 — LIMITES, DECLARADOS

* O veredito é meu, humano-proposto. Um revisor pode mudar linhas; o ficheiro
  diz o porquê de cada uma. Os 2 ambíguos ficaram fora, e não dentro a favor
  de ninguém.
* 37 matérias é o mínimo pedido (≥ 30), não uma amostra grande. As
  percentagens de matéria têm margem larga (cada página vale 2,7 pontos).
* 82 das 109 capas são o `INDEX_URL`: qualquer regra que olhe para o
  `INDEX_URL` está favorecida nessas 82. Por isso as 27 não circulares estão
  separadas.
* O controlo «sem padrão» é simulado (tirei o padrão); todas as fontes deste
  gabarito tinham um.
* Idioma das 37 matérias (leitura grosseira do `micro_coleta.idioma`): 27
  italiano, 6 inglês, 4 marcadas «pt» — provavelmente italiano mal lido pela
  heurística. O detector de capa não lê idioma; declarado só para o leitor.

---

## ENTREGA

```
GOLD_CAPAS    = 109 (27 não-índice) · GOLD_MATERIAS = 37 (10 curtas) · DOMINIOS = 85
EGRESS        = IT em 109/110 idas registadas (149.22.91.172 Palermo) · 0 BR · 1 registo perdido no crash
DETECTOR_ACTUAL: capa→matéria 37/109 · atravessa 63/109 · matéria→capa 6/37
PROPOSTA:        capa→matéria  0/109 · atravessa  0/109 · matéria→capa 25/37
SEM_PADRAO_URL = igual ao ACTUAL (medido, controlo simulado)
RECOMENDACAO   = NÃO aplicar a proposta. Corrigir primeiro os LINK_PATTERN (22/34
                 matérias falham) e 3 INDEX_URL; depois, V1 (índice exacto = capa).
```

---

## EM PALAVRAS SIMPLES

Pense no detector como um porteiro que tem de separar **cartas** (notícias)
de **envelopes vazios** (páginas de entrada, listas, "contactos").

Fui buscar 167 páginas verdadeiras a 110 sites italianos, sempre pela internet
italiana, sem nunca pedir mais de 3 coisas a cada site. Li-as uma a uma e
separei: 109 envelopes, 37 cartas.

**O porteiro de hoje deixa passar mais de metade dos envelopes** — 63 em 109.
Quando uma página de entrada tem muito texto, ele acha que é uma carta.

**A minha ideia da última vez era má.** Eu queria que o porteiro olhasse
primeiro para o endereço do remetente. Nas contas de antes dava perfeito, mas
eu tinha escolhido as cartas pelo próprio endereço — era como corrigir um
exame com a folha de respostas ao lado. Agora, com cartas escolhidas de
outra maneira, a ideia **deita fora 25 das 37 cartas**. Não se aplica.

**O verdadeiro problema está antes do porteiro:** a "morada de uma carta" que
temos escrita para cada site está mal descrita — é o mesmo molde genérico para
quase todos, e não reconhece 22 das 34 cartas verdadeiras. Primeiro há que
corrigir essas moradas; depois, sim, dá para ensinar o porteiro a recusar
pelo menos a página de entrada exacta.

Não mudei nada no porteiro. É tudo medida e recomendação.
