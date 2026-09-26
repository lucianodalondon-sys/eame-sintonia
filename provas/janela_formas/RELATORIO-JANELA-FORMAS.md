# JANELA-FORMAS (D42) · as janelas não publicam como «lista → notícia»

Ramo `janela-formas-v1`, a partir da produção `origin/servico-20260923-0923` (7cdb7ea4). **NÃO instalado.**
Rede fechada por omissão (D41.3). Rede só nos canários autorizados pela missão, com o portão de
consenso PASS IT, fila filtrada ao caso e o teto D38 (no máximo 5 pedidos por domínio).

## A · a receita liga a rota PDF que já existe (D42 (1))

- **Porta** (`curadoria/reparar_contrato.aplicar`, a da R1):
  - a proposta pode trazer `OUTPUT_TYPE` `HTML` ou `PDF`, **explícito** — nunca adivinhado pelo padrão;
  - PDF exige um padrão que aponte para `.pdf`;
  - o tipo anterior fica na proveniência (`REPARO_DE_CONTRATO` e `ROUTE_PROVENANCE`);
  - sem tipo pedido, o `OUTPUT_TYPE` continua fora dos campos que a porta pode mudar.
- **Canário:** vieram da D32 (não instalada) o leitor de links relativos e o ramo PDF pela esteira
  de PDF da Collection; a régua aceita corpo PDF (camada de texto com 800 ou mais caracteres).
- **RAW + proveniência:** o motor do coletor aceita os 3 contratos novos e monta o DOCUMENT_ID pelo
  endereço, com FACT_TIME UNKNOWN (medido sem rede, sobre as entradas guardadas).
- **Testes:** `test_receita_pdf` (7), `test_canario_pdf`, `test_canario_hrefs`. **Mutação 4 de 4**:
  o `XLSX` não matava o mutante do vocabulário, porque o validador já o recusa; o `VIDEO_METADATA`
  mata-o.
- **Canário real:** 5 pedidos no total, no máximo 2 por domínio.

| fonte | alvos | PDF aberto | régua |
|---|---:|---:|---|
| IT-T3-014 SFN | 10 | 10 305 caracteres | DETAIL/v1 |
| IT-T3-027 ERSA FVG | 22 | 8 064 | DETAIL/v1 (tentativa 1: o 1.º alvo em `/aziende/` dava 404; receita corrigida pela prova para `/cms/aziende/`) |
| IT-T3-025 Campania | 27 | 14 365 | DETAIL/v1 — **só a província NA** (SA já é colhida pelo caso IT-T3-002; as outras precisam de uma rota cada) |

## B · «a página é o boletim» (D42 (2))

**Lado do coletor** (`regras/motor_de_rota.mjs`, `coleta/italy_pilot_collect.mjs`, `coleta/retrato_html.mjs`):
- `PAGE_TEXT` é o texto visível, e o coletor passa a **injectar** os leitores de texto. Antes não
  injectava nenhum: uma captura sobre o texto rebentava.
- `CONTENT_SCOPE` recorta o boletim no texto. A impressão desse recorte (`CONTENT_SHA256`) sai
  **ao lado** da identidade, nunca dentro dela — a lei da casa: hash é BYTE_ID. Sem o recorte,
  `IDENTITY_FAILED` (falha fechada).
- **Identidade = fonte + BOLETIM + data comprovada.** Mesma impressão do boletim → `SEEN_AGAIN`;
  impressão nova com a mesma data → versão nova, preservada; data nova → documento novo.
- Um tempo que a fonte não disse fica `UNKNOWN` inteiro: os DEFAULTS só tapam a identidade, e a
  data de coleta **nunca** entra no lugar. FACT_TIME pode ser o período do boletim; COLLECTION_TIME
  é `CAPTURED_AT`, à parte.
- A forma exige `RECOLLECTION.DETAIL_CONTENT = MUTABLE` (palavra que já existia; sem ela o coletor
  salta a página com «já se tem este documento»).
- **Provas:** motor 53 de 53 (6 novos); **o coletor de verdade contra um servidor local, 6 de 6**
  (B1…B6); mutação 5 de 5.

**Lado do Curator:**
- `FORMA = PAGINA_E_BOLETIM` é explícita e verificada pela porta `FORM_RESOLVED` do validador.
- `canario_pagina_boletim` pergunta a identidade **ao motor do coletor** (`regras/identidade_do_motor_cli.mjs`
  — um motor só).
- O worker escolhe o canário pela FORMA, e a validação de rota passou a ler a `URL` da rota fixa
  (antes falhava com «sem endereço»).
- Régua irmã `PAGINA_BOLETIM/v1`. O portão, a ponte e os três red teams passam a aceitar «régua
  corrente», e as formas não se misturam.
- `test_pagina_boletim` 13 verdes; mutação 7 de 7.

**Canário real:** 9 páginas, no máximo 3 pedidos por domínio.
- **Das 8 que a bancada chamou «página = boletim», só o LaMMA (IT-T2-152) o é.** A bancada
  classificou mal; corrigido com prova:
  - ARSAC = uma publicação por semana (lista);
  - arsacweb = lista parada em 2022;
  - ARPA Lombardia = boletim fora do texto;
  - ARPAE ×2 = imagens;
  - CAAR e Liguria = páginas descritivas.
- **LaMMA:**
  - `IT-T2-152:BOLETIM:FIRENZE:2026-09-24`; publicação 2026-09-24; FACT_TIME 17/09 a 23/09/2026;
  - 3 848 caracteres no recorte; régua `PAGINA_BOLETIM/v1`;
  - **deduplicação na vida real:** bytes da manhã ≠ bytes de agora, mesma identidade e mesma impressão.

## C · JavaScript (D42 (3)) — só estudo

Ver `ESTUDO-JAVASCRIPT.md`:
- Emilia-Romagna (2): muito provavelmente a REST API do Plone (`++api++`), permitida pelo robots → ESPERA 1 pedido;
- agrometeopuglia (2): o endereço está dentro de `Bollettini.js` → ESPERA 2 pedidos;
- ISPA: robots.txt em HTML → **fora pela D39**;
- SIMfito: afinal não há JS na entrada → ESPERA 1 pedido.

Headless não é preciso decidir já.

## Testes: o que já falhava

`curadoria.test_reconciliar_livros.OsLivrosReais.test_zy_censo_dos_livros_reais` (985 ≠ 1003)
**já falha na produção limpa 7cdb7ea4** — não é desta missão.

## Plano de instalação (writeset) — NÃO instalar

`git diff --name-status 7cdb7ea4 janela-formas-v1` (código e testes):

```
M coleta/italy_pilot_collect.mjs    M coleta/retrato_html.mjs     M regras/motor_de_rota.mjs
A regras/identidade_do_motor_cli.mjs M regras/motor_de_rota_test.mjs
M curadoria/canario.py   M curadoria/ready_split.py   M curadoria/reparar_contrato.py
M curadoria/worker.py    M curadoria/collection_gate.py   M curadoria/validar_contratos.py
M curadoria/reconciliar_livros.py   M curadoria/red_team_lifecycle.py   M curadoria/red_team_ponte_curador.py
M medidas/red_team_canonico.py
A curadoria/test_receita_pdf.py  A curadoria/test_canario_pdf.py  A curadoria/test_canario_hrefs.py
A curadoria/test_pagina_boletim.py  A provas/janela_formas/*   M system-map/* (cadeia)
```

Os contratos das 3 fontes PDF e do LaMMA **não** vão na instalação. Chegam depois, pelas portas:
a receita pelo `reparar_contrato.aplicar` e a linha do coletor pelo `onboardar_rotas_provadas` —
decisão do dono. Nada disto bloqueia o MICRO nem a 2.ª onda: o que já colhe não muda. Nenhum
contrato atual usa capturas opcionais nem `FORMA`, e a regra UNKNOWN só atua em capturas ausentes.
