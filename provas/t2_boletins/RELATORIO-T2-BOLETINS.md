# T2-BOLETINS (D47) · onde está o boletim agrometeo das 7 agências T2 da coorte

Ramo `t2-boletins-v1`, a partir de `janela-formas-v1` (d0093df0 + C-JS 2eb87123). **NÃO instalado.**
É para a onda seguinte, não para o MICRO nem para a 2.ª onda.

Rede: portão de consenso PASS IT antes de cada corrida; fila filtrada às 7; robots **lido na hora** pelo
leitor RFC 9309 + D39 (`robots-rfc9309-v1`, 9057284d); teto D38 contado num ficheiro só
(`rede/PEDIDOS-POR-DOMINIO.json`) e pausas de 5 s (10 s na ARPAE, pelo Crawl-delay dela).

| domínio | pedidos | quais |
|---|---:|---|
| liguria.it · marche.it · toscana.it · arpacampania.it | 2 cada | robots + 1 página |
| arpae.it | 5 | robots + lista (fase 1) · robots + PDF do canário + boletim mais recente (fase 2) |
| veneto.it | 5 | robots + página agrometeo · 2× `++api++` (**504**) · página «AGROMETEOROLOGICO REGIONALE» (**401**) |

## 1 · Onde está o boletim (com prova)

| agência | boletim agrometeo na agência? | prova | forma |
|---|---|---|---|
| IT-T2-032 ARPAL (Liguria) | **NÃO** | `/tematiche/meteo.html`: só «bollettino-liguria» (previsão do tempo) e «bollettino-mare»; 0 ocorrências de «agrometeo» | — |
| IT-T2-034 ARPA Marche | **NÃO** | a entrada só tem «bollettino-ozono» e liga para `allertameteo.regione.marche.it` (proteção civil); 0 «agrometeo» | — |
| IT-T2-037 ARPAT (Toscana) | **NÃO** | `/bollettini/`: ar, ozono, pólenes, esporos de fungos (aerobiologia/alergia), Arno, laguna; 0 «agrometeo» | — |
| IT-T2-050 ARPA Campania | **NÃO** | a entrada só liga para «agroambiente, suolo e siti contaminati»; 0 «agrometeo» | — |
| IT-T2-051 ARPAE (Emilia-Romagna) | **SIM** | lista `…/bollettini-agrometeo/bollettini-2026`: 30 boletins semanais (n.º 9 de 2/3 a n.º 38 de 21/09) | **lista → PDF** |
| IT-T2-145 / 146 ARPA Veneto | **SIM, mas não provado hoje** | a página `/dati-ambientali/bollettini/agrometeo` lista 5 secções; «AGROMETEOROLOGICO REGIONALE» devolve **401 (login)**; o `++api++` deu **504** duas vezes; D38 esgotado | PDF em endereço fixo (acervo) — ver §4 |

Nas 4 regiões sem boletim na ARPA, **quem publica é outro**: ASSAM (Marche, não está no Atlas),
LaMMA (Toscana, **IT-T2-152**, já provado na D42 B), Regione Campania (**IT-T2-109**
`agricoltura.regione.campania.it/meteo/agrometeo.htm`), Regione Liguria (o CAAR, IT-T2-153, remete para
`sia.regione.liguria.it`). Nada disto foi pedido hoje — é pista, não prova.

## 2 · Contrato novo — ARPAE, pela porta da receita (dono único)

`CONTRATO-PROPOSTO-IT-T2-051.json` (hash `1bb4b6047b54c536`; o atual é `e3eccc21823e1dd2`), feito por
`reparar_contrato.aplicar` numa cópia — **nada escrito nos livros vivos**:

```
INDEX_URL        = https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/bollettini-agrometeo/bollettini-2026
LINK_PATTERN     = …/bollettini-2026/\d{2}_boll_agro_\d{8}(-\d+)?\.pdf$
STRIP_SUFFIX     = /view            (as 60 ligações acabam em .pdf/view — a página do Plone, não o PDF)
OUTPUT_TYPE      = PDF              (explícito)
DOCUMENT_ID      = IT-T2-051:BOLETIM:AGROMETEO:<ano>-<n.º>        (do nome; sem hash)
PUBLICATION_TIME = SOURCE_DATE_ISO = a data do nome (AAAAMMDD)
FACT_TIME        = UNKNOWN — a semana descrita está só no texto do PDF
COLLECTION_TIME  = CAPTURED_AT do coletor (nunca no lugar dos outros dois)
```

Provado no PDF: «Bollettino AgroMeteorologico Settimanale **n. 38/2026 del 21 settembre 2026** ·
14 settembre 2026 - 20 settembre 2026». Ou seja: a data do nome **é** a da publicação, e o período do
facto (a semana anterior) existe — mas só no texto do PDF. O motor tem o leitor `PDF_TEXT` no
vocabulário e **o coletor não o injecta** (só RAW_UTF8, RAW_LATIN1, PAGE_TEXT); por isso FACT_TIME fica
UNKNOWN em vez de inventado. Injectar `PDF_TEXT` é o passo seguinte para o FACT_TIME sair do boletim.

Dois casos na lista de 2026 que a regra tem de aguentar:
- `15_boll_agro_20260413-2.pdf` (sem o `-1` na lista): o `-2` é aceite pelo padrão e o DOCUMENT_ID sai
  do **número** (`2026-15`), não do sufixo — se o `-1` voltar, é versão do mesmo boletim.
- ⚠️ **n.º 11 e n.º 12 têm a mesma data no nome** (`11_boll_agro_20260316`, `12_boll_agro_20260316`). O
  n.º 12 devia ser de 23/03. Não abri o n.º 12 (D38), por isso **NÃO SEI** qual data o PDF diz — mas a
  PUBLICATION_TIME pelo nome pode estar errada em **pelo menos 1 de 30**. Com `PDF_TEXT` injectado, a
  data sairia da linha «n. NN/2026 del …» do próprio boletim, que é a fonte certa.

### O que a porta e o canário passaram a saber (código)

- `reparar_contrato.aplicar`: aceita `STRIP_SUFFIX` e `IDENTITY` **explícitos** (como o `OUTPUT_TYPE`),
  com o anterior na proveniência. A `IDENTITY` só entra depois de o **motor do coletor** a conferir
  (`regras/identidade_do_motor_cli.mjs`, modo `SO_CONFERIR`); sem node, recusa.
- `canario.hrefs_da_entrada`: aplica o `STRIP_SUFFIX` do contrato, **o mesmo corte que o coletor já
  fazia** (`motor_de_rota.mjs` · `ligacoesDoIndice`). Paridade provada num teste que corre o motor.
- `canario._canario_pdf`: a identidade e os tempos vêm do **motor** (antes: um `replace("{doc.1}")` à
  mão). O canário HTML **não** mudou. O contrato de teste de `test_canario_pdf` ganhou o bloco
  `IDENTITY` que as 574 de 574 fontes do livro do Curator já têm (o motor exige `STRATEGY`).
- Testes: `test_strip_suffix` (8), `test_receita_identidade` (7); 86 verdes no conjunto tocado
  (`test_receita_pdf`, `test_canario_pdf`, `test_canario_hrefs`, `test_reparar_contrato`,
  `test_pagina_boletim`); `motor_de_rota_test.mjs` verde.
- **Mutação 9 de 9** (`mutacao_strip_suffix.py`): cada mutante numa cópia da árvore, sem `.pyc`, e a
  cópia **sem** mutação tem de ficar verde primeiro.

⚠️ Achado, **não** consertado (é de antes): uma ligação com `#fragmento` é **descartada** pelo motor
do coletor (a regex dele pára no `#`) e **aproveitada** pelo canário (que corta o fragmento). A ARPAE
não tem fragmentos; noutras fontes o canário pode dizer PASS a um alvo que o coletor nunca vê.

## 3 · Canário real + Admissão atual (T2)

| agência | canário | régua | Admissão T2 (VERSAO_DA_REGRA 9) |
|---|---|---|---|
| IT-T2-051 ARPAE | **PASS** — 30 alvos, PDF n.º 9 com camada de texto (2 679 car.) | **DETAIL/v1** (4 passos + contrato atual) | **2 SIM de 2** (n.º 9 de 02/03 e n.º 38 de 21/09): «pioggia, temperatura, siccità e agrometeo — condição do campo com ligação agrícola escrita» |
| IT-T2-145/146 ARPAV | não corrido (401 + 504; D38 esgotado) | — | NÃO SEI |
| IT-T2-032/034/037/050 | não há boletim a buscar | — | — |

**Em números:** das 7 agências T2 da coorte, **1** tem hoje contrato provado para o boletim (ARPAE,
2 SIM em 2 julgados); **2** (ARPAV) têm boletim mas a rota não foi provada; **4** não publicam boletim
agrometeo — reapontá-las não é possível: o boletim da região é de outro publicador.

## 4 · ARPA Veneto — o que falta, sem prova de hoje

O acervo tem dois endereços fixos (conteúdo muda a cada edição):
`/temi-ambientali/agrometeo/file-e-allegati/bollettino_agrometeo_regionale_settimanale.pdf/@@download/file`
e `/risorse/data-agrometeo/agrometeo/32zone/agro_NN.pdf` (32 zonas). Endereço fixo + conteúdo que muda
é a forma «a página é o boletim», **mas em PDF** — e essa forma hoje só lê `PAGE_TEXT` de HTML. Precisa:
(1) o coletor injectar `PDF_TEXT`; (2) `CONTENT_SCOPE`/impressão sobre o `PDF_TEXT`; (3) uma corrida
nova com D38 fresco: robots + 1 PDF. E decidir **qual SOURCE_ID** fica com o boletim: 145 e 146 hoje
são «comunicati stampa» e «notizie» do mesmo publicador (decisão do dono).

## Plano de instalação (writeset) — NÃO instalar

```
M curadoria/canario.py               M curadoria/reparar_contrato.py
M regras/identidade_do_motor_cli.mjs M curadoria/test_canario_pdf.py
A curadoria/test_strip_suffix.py     A curadoria/test_receita_identidade.py
A provas/t2_boletins/*               A provas/janela_formas/cjs/*  (C-JS + D46)
M system-map/* (cadeia — PENDENTE: LOCK-PRIORIDADE ativa e memória 4,9 GB < 5 GB)
```

O contrato da ARPAE **não** vai na instalação: chega depois pela porta (`reparar_contrato.aplicar`
com a receita de `CONTRATO-PROPOSTO-IT-T2-051.json`) e a linha do coletor pelo
`onboardar_rotas_provadas` — decisão do dono. Nenhum contrato atual usa `STRIP_SUFFIX` no Curator
nem `IDENTITY` pela porta, por isso o que já colhe não muda.

## Provas

No ramo: `provas/t2_boletins/` (scripts, `rede/*.json`, `rede/bytes/*` sem os PDFs).
Fora do Git (2 PDFs, ~2 MB):

| ficheiro | sha256 |
|---|---|
| `C:/cur/t2b/bytes/3d669b144010fd837fce.bin` (09_boll_agro_20260302.pdf) | `3d669b144010fd837fce8025c497fa7630819b53d3985e73d2506f1e8d5e6c78` |
| `C:/cur/t2b/bytes/e0a8f255b3091dc32eed.bin` (38_boll_agro_20260921.pdf) | `e0a8f255b3091dc32eedbf8684e5c25dff41bea9cc54bc8509a25d1af19b1daa` |
