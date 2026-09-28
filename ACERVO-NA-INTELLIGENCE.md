# ACERVO-NA-INTELLIGENCE — o acervo antigo pelas capacidades da Intelligence, até ao pote v2

```text
ORDEM     D115: o acervo antigo é real e passa pela Intelligence antes do casco. D97: o casco só mostra o
          que a Intelligence produziu. D119: IDs PROVISORIO. (D115, D97 e D119 NÃO estão escritas no repo;
          segui o resumo do pedido.)
RAMO      claude/acervo-intelligence-processing-148qau  (base c551062 = lote6 + porta única)
REDE      nenhuma. Nada coletado. Nada publicado. Casco não tocado. Livros vivos não tocados.
CORRIDA   IR-c25ca7c56d432a223e5e · HOJE declarado 2026-09-27 · referência ADAMA PROD_FTS_6_20260831
          (PODE_ESTAR_DESATUALIZADO, 20 dias sem checagem)
```

## 1 · O que entrou na base, e como

| o quê | como | porquê |
|---|---|---|
| `origin/claude/pote-v2-unico-contract-y8o1pi` (contrato único + `validar_pote_v2.py`) | **merge** (`git merge`), conflitos só em ficheiros **gerados** (mapa, índice de fontes, censo) → fiquei com os desta branch e a cadeia regerou-os | o contrato único não estava nesta base |
| `origin/claude/organize-collection-system-japwor` | **só** `docs/intelligence/acervo/` (ENTRADA + INSUMOS, 3 ficheiros **novos**, nada sobrescrito) via `git checkout <ramo> -- docs/intelligence/acervo/` | o merge inteiro foi medido: **42 conflitos**, 142 ficheiros, e mexia em `portale.html`/casco — proibido nesta missão. **Declarado: não é merge completo.** |
| `origin/claude/rete-voci-dati-adapters-sit3hj` | **não trazido** | não foi preciso: a origem (`italy-handoff-v21.js`, mesmo sha256 que a ENTRADA declara) já tem os registos; só copiei o *padrão* (adaptador em `pacote/`, limite provado da captura) |

## 2 · O que foi feito — `pacote/acervo_na_intelligence.py`

Não é capacidade nova: monta o READY de cada item e chama as que já existem, **numa corrida só** (uma LINEAGE).

| regra | ficheiro:linha |
|---|---|
| a ENTRADA e a origem: sha256 conferido, cada ACERVO_ID acha **um** registo | `pacote/acervo_na_intelligence.py:186` |
| tempo do facto por tabela declarada (anúncio no ar; atividade orgânica do concorrente = publicar; período do preço; data do evento). Ciência, notícia, transcrição, voz, boletim: **NÃO SEI** | `:234` (tabela `:130`) |
| captura: dia real (OBSERVED_AT) ou **limite provado** — inferior = publicação/início do facto observado; superior = commit git `c24ea78` (2026-09-15). **DATA_DO_PACOTE não é limite**: medido, há OBSERVED_AT 2026-09-03 depois do «pacote» de 02/09 | `:262`, `:105` |
| **D112**: FACT_LOCATION do READY = NAO SEI sempre; o país da fonte fica em SOURCE_LOCATION | `:343`, `:365` |
| G0 + CAP-WIN + CAP-SCI + futuro + rendimento: `motor_das_capacidades.rodar` | `:711` |
| **concorrente**: substância/alvo no criativo → registo ADAMA com a **mesma substância**, só pela porta (`coleta/concorrencia_meta.adama_no_anuncio`); SINAL; cultura NAO SEI | `:408`, `:417` |
| **mercado (P8)**: série só com pontos admitidos da mesma praça×produto×estágio×unidade; a variação da fonte (CHANGE_VS_PREV_PCT) viaja como texto, sem período anterior | `:481` |
| **vozes (CAP-FIELD)**: `voce_dal_campo.extrair`; transcrição só se o texto está no repo e bate pelo TEXT_SHA256 | `:551` |
| portão próprio (oportunidade, ID PROVISORIO, COMPOSTO_DE, mudança, lugar da fonte, D112b) | `:780` |

**Saída** (commitada): `docs/intelligence/acervo/corrida-acervo/POTE-ACERVO.json` (validado: `validar_pote_v2.py` → **PASSA**, 1.128 objetos, 77 recusados) e `RESUMO-ACERVO.json`. O livro inteiro (~20 MB) **não** se commita: `--livro <caminho>` regera-o; o teste A5 prova que a árvore regera o pote commitado byte a byte (fora SOURCE_HEAD).

### Dois defeitos medidos em peças que JÁ existiam — declarados, não consertados aqui

1. **SOURCE_ID com «API» derruba a corrida G0 inteira.** `corrida_da_inteligencia` recusa escrever um requisito que nomeie palavra da Collection, e o requisito leva o SOURCE_ID (`SRC_API_ARPA_VENETO_IT`). 7 itens (6 agromet, 1 preço) ficam **FORA_DA_CORRIDA**, contados um a um (`:680`). Consertar é mudar a lei do motor — decisão do dono.
2. **O motor das capacidades e o contrato único nunca se encontraram.** O motor escreve `CHAVES.ENTITY_SOURCE` como **mapa**; o schema do pote v2 exige **texto** → com a saída crua, `validar_pote_v2` reprova **todo** objeto (o teste do motor que corria o gerador está em *skip*: `ce775ff5` não está no clone). Leitura de compatibilidade declarada: o mapa viaja inteiro como `ENTITY_SOURCE_POR_CHAVE` (`:632`). Nenhum dono mudado.

## 3 · Por compartimento (tipo) — entrou, virou objeto, recusado e porquê

| tipo | entrou | G0 passou | virou objeto | recusado | porquê (contado) |
|---|---:|---:|---:|---:|---|
| anúncio concorrente | 577 | 561 | **561** (competitors) | 16 | 16 sem data nenhuma (G0: FACT_TIME) |
| ciência | 851 | 0 | 0 | 851 | publicação ≠ período do estudo (INT-LAW-100) → G0 FACT_TIME; a CAP-SCI **julgou 849** (uso atemporal), mas o pote exige tempo para SINAL (P7) |
| transcrição | 184 | 0 | 0 | 184 | G0 FACT_TIME (publicação ≠ dia da fala); só 43 têm texto no repo (141 não) |
| preço | 157 | 77 | 0 | 157 | 77: **sem endereço do item** (só o editor) → pote PROVA_INCOMPLETA; 79: registo sem preço; 1: FORA_DA_CORRIDA |
| boletim | 133 | 0 | 0 | 133 | sem tempo do facto; sem JANELA_DECLARADA (é da Collection; derivá-la seria cunhar facto) → CAP-WIN 0 janelas |
| voz (comentário) | 79 | 0 | 0 | 79 | sem data (DATE_RELATIVE «1 year ago» não tem ano) |
| agromet | 44 | 0 | 0 | 44 | 38 G0 FACT_TIME; 6 FORA_DA_CORRIDA («API») |
| evento | 40 | 0 | **2** (future) | 38 | 22 sem data; 16 com data entre os limites da captura (nem passado nem futuro provado) |
| notícia | 8 | 0 | 0 | 8 | publicação ≠ facto |
| sinal de campo | 7 | 0 | 0 | 7 | sem data; 4 sem fonte (SRC_NAO_DECLARADA) |
| **total** | **2.080** | **638** | **563** | **1.517** | + `sources` 2 (rendimento) e `archive` 563 (os mesmos objetos) |

Medidas das capacidades: CAP-SCI 849 julgados (279 PARCIAL, 570 TEMA_NAO_PROVADO; ligação ao rótulo **849 NOT_POSSIBLE** — nenhum estudo traz molécula); CAP-FIELD 101 documentos, **930 vozes extraídas, 930 sem prova admitida**; CAP-COMP 2 anúncios com substância da referência, 92 com alvo.

## 4 · Dez exemplos reais, com a prova

| # | objeto / item | o que diz | prova |
|---|---|---|---|
| 1 | `R7-COMP-d9c31ef5768ad1a4` · BASF | criativo nomeia **FLUXAPYROXAD** → ADAMA **AVASTEL** reg. 018089 (mesma substância, pela porta) | facebook.com/ads/library/?id=1885465572852443 · no ar 2025-11-11..17 · colheita ≥ 2025-11-11 (limite; dia real NAO SEI) |
| 2 | `R7-COMP-06d13ab158abb7ee` · FMC (YouTube) | **GLYPHOSATE** → 11 registos ADAMA | youtube.com/watch?v=PNTFhajUB1A · publicado 2022-10-06 = o facto (atividade = publicar) |
| 3 | `R7-COMP-4c7cd1d092121bfe` · Bayer (Velsinum) | nenhuma substância da referência → **NAO SEI**, nunca «a ADAMA não tem» | ads/library/?id=1566954087923977 · 2026-01-30..02-09 |
| 4 | `R7-COMP-02b0dffd322883d1` · Syngenta **España** | o registo diz GEO_ITALY; FACT_LOCATION = **NAO SEI** (alcance ≠ lugar, D112) | youtube.com/watch?v=CUCdc8DX4g0 · 2020-02-19 |
| 5 | `R7-FUT-30b7157b64ad65f6` · EIMA 2026 | facto presente sobre o futuro (2026-11-10), não oportunidade | eima.it · G0 bloqueou só por futuro; captura ≤ 2026-09-15 (git) |
| 6 | `R7-FUT-c99de0ae7a826609` · Vinitaly | idem, 2027-04-11 | vinitaly.com |
| 7 | `R7-SRC-d242c0379865aaf2` | Registro delle fonti: SRC_FACEBOOK_COM 414 lidos, 414 G0, 414 objetos | as 414 provas da própria fonte |
| 8 | `marketObservations::IT-MKT-001` Alessandria | €215,50/t, 08–14/06/2026: **SINAL_SOLTO**; a fonte escreve «0,0% vs anterior» sem o período anterior → não é mudança. Recusado no pote: **sem endereço do item** | editor ec.europa.eu/agrifood/api (só o editor) |
| 9 | `scienceRecords::IT-SCI-001` | registo diz COUNTRY_OF_FACT=IT para uma revisão sobre Xylella de instituto espanhol — **não usado** (sem evidência); CAP-SCI julga, pote recusa (sem período do estudo) | doi.org/10.1094/phyto-12-23-0476-kc · publicado 2024-04-01 |
| 10 | `agrometConditions::IT-CAN-D31C8C3634` | **FORA_DA_CORRIDA**: SOURCE_ID `SRC_API_ARPA_VENETO_IT` derruba a corrida G0 | api.arpa.veneto.it/… |

## 5 · O que NÃO pode ser dito

- **Anúncio não é demanda nem oportunidade.** 561 anúncios dizem que o concorrente comunicou; nada sobre procura, venda ou pressão. O Radar delle Opportunità fica **vazio** desta corrida.
- **O concorrente só se compara por substância**; a cultura do anúncio é NAO SEI, e o registo do concorrente não está na referência (lacuna 3).
- **Preço isolado não é mercado.** Nenhuma série de 2+ pontos na mesma unidade existe no acervo (77 praças × produto, um ponto cada). «Variação %» da fonte não é série.
- **Lugar da fonte ≠ lugar do facto.** País do podcast, GEO_ITALY do anúncio, afiliação do autor: nenhum vira lugar.
- **Publicação ≠ tempo do facto** (ciência, fala, notícia). Por isso ciência e vozes, julgadas, **não** atravessam: o pote exige tempo para SINAL (P7).
- **Zero num compartimento não prova ausência no mundo** — prova ausência de prova neste acervo.
- «Colhido em» dos objetos é **limite provado**, não o dia real (escrito assim em cada prova).

## 6 · Testes — bateria inteira por nome (`provas/int_r7/bateria_por_nome.py`, rede fechada)

| | módulos | testes | falhas por nome |
|---|---:|---:|---:|
| base `c551062` | 314 | 7.030 | 123 |
| depois `92fef22` | 316 | 7.100 | 123 |

**Novas: 0. Sumidas: 0.** Módulos novos: `test_acervo_na_intelligence` **32/32**, `test_pote_v2_unico` **38/38** (trazido no merge). JSON em `provas/acervo_na_intelligence/BATERIA-*.json`. Nenhum teste existente foi mexido.

## 7 · Mutação — `provas/acervo_na_intelligence/mutantes.py`: **18/18 mortos**

Anúncio vira OPORTUNIDADE · anúncio entra no Radar · cultura do anúncio afirmada · ligação ADAMA pelo alvo · anúncio sem tempo sem G0 · **preço anterior vira ponto da série** · **variação vira MUDANCA_DE_MERCADO** · série mistura unidades · **país da fonte vira lugar do facto** · alcance vira lugar · publicação da ciência vira tempo · data do pacote vira limite · início do facto vira limite para todo tipo · URL ambígua escolhida · ID deixa de ser PROVISORIO · ENTITY_SOURCE cru ao pote · fora-da-corrida em silêncio · Archivio com recusados. Resultado: `provas/acervo_na_intelligence/MUTANTES.json`.

## 8 · System Map

`correr_a_cadeia.py REGERAR` → CADEIA=OK · `VALIDAR` → **SYSTEM_MAP_CHECK=PASS** · `--conferir-carimbo` → **IGUAL** (conferido de novo depois do commit final). Peças novas: `C-ACERVO-NA-INTELLIGENCE` (Z-PACOTE), `C-PROVA-ACERVO-NA-INTELLIGENCE` (Z-PROVA). Sem `--stamp`.

## 9 · NÃO SEI / por decidir

1. Texto de D115, D97, D119. 2. Consertar o «API» no requisito da corrida G0 (lei do motor). 3. Quem é dono do formato de ENTITY_SOURCE (motor × contrato único). 4. De onde tirar o **tempo do facto** da ciência (período do estudo) e das vozes (dia da fala) — sem ele, 1.035 itens julgados não atravessam. 5. Endereço de item dos 77 preços (a Collection só guardou o editor). 6. O prefixo `R7-` é o literal do esquema do motor, não a rodada.

## EM PALAVRAS SIMPLES

Pegamos nos 2.080 itens velhos que já estavam guardados e passámo-los pelas mesmas «máquinas» de análise que a Intelligence já tem, sem inventar máquina nova e sem internet. Saiu um pote novo, conferido pelo fiscal oficial, que **não** foi publicado nem ligado à tela.

O que passou: **561 anúncios de concorrentes** (e, em 2 deles, o sistema achou a substância ativa e o produto ADAMA com a mesma substância, pela porta oficial das bulas), **2 feiras futuras** (EIMA e Vinitaly) e a contagem das fontes. O que **não** passou, e porquê: a ciência, as falas e as notícias não dizem *quando* o facto aconteceu (a data de publicação não serve), os preços não têm o endereço do item, e os boletins não trazem a janela declarada. Cada recusa está contada com o motivo.

Achámos dois defeitos em peças antigas e deixámo-los escritos, sem mexer: fontes com «API» no nome derrubam a análise inteira, e duas peças da casa falam «formatos» diferentes da mesma informação. Plantámos 18 erros de propósito — os testes apanharam os 18 — e nenhum teste que passava antes passou a falhar.
