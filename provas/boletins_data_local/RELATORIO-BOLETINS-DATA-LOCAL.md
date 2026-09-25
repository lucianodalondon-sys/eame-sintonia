# DA-2 · D61/D62/D69 — data e lugar em TODAS as rotas de boletim

Ramo `boletins-data-local-v1`: parte do `t2-boletins-v1` (4cec24c3), com a produção `origin/servico-20260923-0923` já
junta (88ee046f; o conflito foi só em ficheiros gerados pelo mapa, e o mapa é regerado no fim). **NÃO instalado.**
Vai com o pacote de data e local (DA-2).

## A regra, em palavras simples

A rota de um boletim conhece a FORMA dele: sabe em que linha está a data de emissão, o período e a área. O
contrato diz onde ler cada uma e COMO se soube (a BASE); o motor do coletor lê, confere e devolve:

| campo (nome da fronteira, `coleta/ingresso.py`) | o que é | quando fica NAO SEI |
|---|---|---|
| `PUBLISHED_AT` + `_BASIS` (= a PUBLICATION_TIME da D69) | a data de **emissão** do boletim | o boletim não a diz, ou não é data de calendário |
| `FACT_TIME` + `_BASIS` | o período do **facto** — **só** quando o TEXTO liga o período ao facto (D69: «Osservazioni della settimana da … a …», «Previsione … per oggi … per domani …») | sem essa ligação |
| `BULLETIN_PERIOD` + `_BASIS` (novo, D69) | a validade/cobertura do boletim, guardada como **evidência** | o boletim não a diz |
| `FACT_LOCATION` + `_BASIS` | a área que o boletim **declara** (província/zona) | não declara (o publicador nunca é o lugar) |

- **D62:** nada é obrigatório e **nenhum documento cai** por falta de data ou de lugar. As capturas destes campos
  têm de ser opcionais (o motor recusa o contrato se não forem); o que falta sai «NAO SEI» com o porquê.
- **Nunca se inventa:** um valor que não é data de calendário («31 febbraio»), um intervalo que começa depois de
  acabar, um mês que não é italiano → NAO SEI. A data de coleta nunca entra (o motor nem a recebe).
- **Uma data de calendário nunca vira janela agronómica:** o motor não tem campo de janela (há um teste para isso).
- **D69 no próprio motor:** um `FACT_TIME` num boletim só é aceite com a base a começar por
  `PERIODO_LIGADO_AO_FATO_NO_TEXTO`; a validade vai para `BULLETIN_PERIOD`, e o `FACT_TIME_BASIS` diz onde ela ficou.

## O que mudou no código

- `regras/motor_de_rota.mjs`: os campos acima (moldes com **filtros fechados**: `MES_IT`, `MES2`, `DIA2`, `ANO4`;
  **várias formas por campo**, pela ordem, vale a primeira válida; **BASE sem molde** = o contrato diz porque o
  boletim não traz aquilo). Contratos sem BASE saem exactamente como antes.
- `coleta/texto_de_pdf.mjs` (novo): **um leitor de PDF só** (pdftotext), injectado como `PDF_TEXT` pelo coletor e pelo
  canário (`regras/identidade_do_motor_cli.mjs`). Antes o coletor tinha-o escondido num `switch` e o canário não tinha.
- `coleta/italy_pilot_collect.mjs`: a ficha da observação leva os oito campos quando o contrato os declara.
- `curadoria/reparar_contrato.py` (a porta): PDF sem «.pdf» no endereço só com `PDF_SEM_EXTENSAO` = o porquê escrito,
  guardado na proveniência (Molise `…/E/pdf?mode=download`, VdA `allegato.aspx?pk=N`, Umbria/Veneto Liferay). Isto
  substitui o truque do «.pdf opcional» da Umbria (D51.3). A garantia continua nos bytes (`%PDF-`).
- `curadoria/validar_contratos.py`: `FACT_TIME_BASIS` sem molde conta como declaração do FACT_TIME.
- `curadoria/canario.py`: o canário PDF e o de «página = boletim» mostram os oito campos; o canário HTML só pergunta
  ao motor quando o contrato declara BASES (a ARSAC) — os outros ficam iguais.

## Provas

| prova | resultado |
|---|---|
| `regras/boletim_data_local_test.mjs` (motor) | **23/23** |
| `regras/motor_de_rota_test.mjs` · `recollection` · `incrementalidade` · `paridade` | 68/68 · 31/31 · 31/31 · 32/32 |
| `curadoria/test_boletim_data_local.py` + os 7 módulos da D47 | 9/9 · 86/86 |
| **coletor de verdade** contra servidor local, rede fechada: `boletim_pdf_local.mjs` | **4/4** (P1 campos com base · P2 PDF sem data COLETADO · P3 «31 febbraio» NAO SEI · P4 D69) |
| «página = boletim» da JANELA-FORMAS B (`pagina_boletim_local.mjs`) | 6/6 |
| **mutação** `mutacao_d61.py` (cópia da árvore, base verde primeiro) | **13/13** (8 motor, porta, validador, canário, 2 coletor) |
| `regras/italy_contract_test.mjs` | 348/77 — as **77 são herdadas**: a produção viva dá 77; 74 nomes iguais, 3 mudam só de número porque leem o livro de coleta LOCAL de cada árvore («piloto cobre as 7 fontes — 30» vs «— 16») |

## Canário real — 9 rotas de boletim (portão PASS IT, robots RFC 9309 + D39 lido na hora, D38)

Contratos pela porta, numa cópia (`CONTRATOS-PROPOSTOS-D61.json`); base = o livro vivo do Curator (só leitura).

| fonte | forma | emissão | FACT_TIME | BULLETIN_PERIOD | área | régua |
|---|---|---|---|---|---|---|
| IT-T2-148 ARSAC | página por edição | NAO SEI | NAO SEI (D69) | 2026-09-15/22 | Calabria, território regional (8 áreas) | **LEGACY** |
| IT-T3-032 Molise | lista → PDF | 2026-06-10 | 2026-06-10/11 (previsão «per oggi/domani») | 2026-06-10/11 (validade) | NAO SEI | DETAIL/v1 |
| IT-T3-055 Valle d'Aosta | lista → PDF | 2026-02-27 | NAO SEI | NAO SEI | NAO SEI | DETAIL/v1 |
| IT-T3-053 Umbria | lista → PDF | 2026-07-17 | NAO SEI | NAO SEI | Perugia e Terni | DETAIL/v1 |
| IT-T2-051 ARPAE | lista → PDF | 2026-03-02 | 2026-02-23/03-01 | 2026-02-23/03-01 | NAO SEI | DETAIL/v1 |
| IT-T3-014 SFN | lista → PDF | 2026-05-14 (assinatura) | NAO SEI | NAO SEI | NAO SEI | DETAIL/v1 |
| IT-T3-027 ERSA | lista → PDF | 2025-10-07 | NAO SEI | NAO SEI | NAO SEI | DETAIL/v1 |
| IT-T3-025 Campania NA | lista → PDF | 2026-04-01 | NAO SEI | NAO SEI | provincia di NAPOLI | DETAIL/v1 |
| IT-T2-152 LaMMA | página = boletim | 2026-09-24 | 2026-09-17/23 («Osservazioni della settimana») | NAO SEI | provincia di Firenze | PAGINA_BOLETIM/v1 |
| IT-T3-058 Veneto | — | — | — | — | — | **FORA: `Disallow: /documents/`** |

Pedidos por domínio (conta única em `rede/PEDIDOS-POR-DOMINIO.json`): calabria.it 5 · molise.it 5 · vda.it 5 ·
veneto.it 3 · arsacweb.it 3 · arsacagrometeo.it 2 · protezionedellepiante.it 3 · fvg.it 3 · campania.it 3. A
Umbria, a ARPAE e o LaMMA usaram os bytes lidos hoje (D47/D51.3/D42) — 0 pedidos.

### ⚠️ O que precisa de decisão ou de olhos

1. **ARSAC não fica pronta.** A página de `arsac.calabria.it` só **anuncia** a edição e liga para `arsacweb.it`
   (que NÃO parou em 2022: parou só a página de lista do contrato atual); a edição em `arsacweb.it` tem a emissão
   (`article:published_time` 2026-09-24T10:23Z) mas não o texto; o texto vive em `arsacagrometeo.it/bollettino_cover.php`,
   que hoje devolve **erro do servidor** («Access denied for user … mysqli»). A régua diz LEGACY: corpo não provado.
   Proposta: esperar o site do boletim voltar, ou decidir se a edição em `arsacweb.it` (emissão + período no título)
   serve como documento. O `CANONICAL_ENTRY_URL` do contrato continua `arsacweb.it` (a porta não o muda).
2. **ARPAE — juízo meu, para confirmar:** aceitei como «ligado ao facto» o período que **encabeça** o «Diario
   meteorologico» (o relato do tempo observado nessa semana). Se a D69 exigir a frase explícita, fica em
   BULLETIN_PERIOD e o FACT_TIME passa a NAO SEI (é mudar a base e a captura, sem código).
3. **Molise:** o «Comunicato fitosanitario N» não traz data de emissão no PDF — a data está só no **texto do link** da
   lista, que o motor não lê. Um leitor do texto do link seria um passo a mais (não feito).
4. **Umbria:** o ficheiro do NOCCIOLO n.10 diz «N.10» na 1.ª página e «N.11 del 17/07/2026» nas seguintes — o boletim
   contradiz-se; a rota fica com o cabeçalho da 1.ª página. A identidade por endereço continua a incluir `?version=`.
5. **SFN (DTU):** é uma norma técnica, não um boletim; a «emissão» é a data da assinatura digital (MASAF).
6. **ERSA:** o canário abre o 1.º por ordem alfabética — calhou um de 2025. Não muda a rota.
7. **LaMMA** não passa pela porta (a porta não muda `FORMA`/`STATIC_ENDPOINT`): o contrato é montado como na
   JANELA-FORMAS B e chega pelo onboarding.
8. **Fragilidade antiga (não consertada):** o teste M2b do motor mede uma janela fixa de 1 400 caracteres do coletor
   e depende do fim de linha da cópia de trabalho (CRLF acrescenta 1 por linha).

## Plano de instalação (writeset) — NÃO instalar

```
M regras/motor_de_rota.mjs          M regras/identidade_do_motor_cli.mjs   A regras/boletim_data_local_test.mjs
A coleta/texto_de_pdf.mjs           M coleta/italy_pilot_collect.mjs
M curadoria/reparar_contrato.py     M curadoria/validar_contratos.py        M curadoria/canario.py
M curadoria/test_receita_identidade.py                                      A curadoria/test_boletim_data_local.py
A provas/boletins_data_local/*      (+ tudo do t2-boletins-v1: STRIP_SUFFIX, IDENTITY pela porta, C-JS)
M system-map/* (cadeia)
```
Os contratos (`CONTRATOS-PROPOSTOS-D61.json`) **não** vão na instalação: entram depois pela porta e pelo
`onboardar_rotas_provadas` (decisão do dono). O que já colhe não muda: nenhum contrato atual declara BASES.

## PDFs fora do Git (sha256)

Ver `rede/PDFS-FORA-DO-GIT.txt` (7 PDFs em `C:/cur/d61/bytes/`), mais os da D47/D51.3 já listados no relatório T2-BOLETINS.
