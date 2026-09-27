# ACERVO-ORGANIZADO — o que já estava no repositório, arrumado no lugar certo

Missão D114 + correção do dono (27/09 16:50):

> «os números que estavam no portal antigo não eram mentiras, portfolio por exemplo bulas, parte da
> label intelligence, cheque o que já tem e não precisa coletar novamente, apenas organizar nos
> lugares novos e corretos» — e: «tudo está passando pelo processo correto? coleta, inteligência e
> casco? não tem nada se cruzando e indo pro casco só pra encher ele?»

Lei D97: `COLLECTION → SALA → INTELLIGENCE (e INTELLIGENCE TOOLS) → POTE → CASCO`. Nada foi coletado,
nada foi publicado. Tudo aqui é offline e reproduzível.

## O que foi entregue

| # | entrega | ficheiro | como se confere |
|---|---|---|---|
| 1 | inventário do acervo, conjunto a conjunto, com classe e motivo | `docs/acervo/INVENTARIO-ACERVO.md` + `.json` | `node pacote/acervo_inventario.mjs --conferir` |
| 2 | a Label Intelligence selada, na forma do pote v2, como **produto de ferramenta** | `docs/casco/ferramentas/POTE-FERRAMENTA-LABEL-INTELLIGENCE.json` (gerado por `pacote/pote_ferramenta_label.py`) | `python3 pacote/pote_ferramenta_label.py --conferir` |
| 3 | a referência oficial declarada como insumo da Intelligence | `docs/intelligence/acervo/INSUMOS-DECLARADOS-ACERVO.md` + `.json` | idem 1 |
| 4 | os itens coletados, normalizados, para a próxima rodada da Intelligence | `docs/intelligence/acervo/ENTRADA-INTELLIGENCE-ACERVO.json` | idem 1 |
| 5 | auditoria D97 do pote R7 e do casco | `docs/acervo/AUDITORIA-D97-R7.json` (gerado por `italia-portale/audit/casco/d97-auditoria.mjs`) | `node italia-portale/audit/casco/d97-auditoria.mjs` |
| 6 | o aviso «SHA256 do pote NÃO CORRESPONDE ao manifesto» | `pacote/publicar_pote_aprovado.py`, `sintonia-pote-publicacao.js`, `.gitattributes` | `tests/test_acervo_organizado.py` (S) + `tests/test_pote_publicado.mjs` (Q8) |

## 1 · O inventário, contado por classe

Canónico: `italy-handoff-v21.js` (build `V21-ef6e7e5f37eaa6e6`, pacote de 02/09, o que o portal carrega).
Cópias noutros ficheiros foram **medidas pelo ID** e não somam de novo.

| classe | o que é | conjuntos | registos (sem cópias) |
|---|---|---:|---:|
| **a** SAIDA_DE_INTELLIGENCE_TOOL | Label Intelligence selada (Ministero, snapshot `PROD_FTS_6_20260831`) | 5 | 555 (166 produtos · 210 objetos · 54 versões · 76 + 49 listas seladas) |
| **b** REFERENCIA_OFICIAL | registro 163, catálogo 51 + 44, pares produto×cultura×alvo 5 402, substâncias, ISTAT 2 978, resistência… | 18 (+2 blocos) | 9 572 |
| **c** ITEM_COLETADO | anúncios 577, ciência 851, transcrições 184, preços 157, boletins 133, vozes 79, agromet 44, eventos 40, noticias 8, sinais 7 | 11 | **2 080** |
| **d** FORA | demo inteira (39 blocos), 43 oportunidades V2.1 (`CLIENT_SAFE=false`), 19 cruzamentos V2.1 (`CLIENT_SAFE=false`), janelas montadas à mão, agregados derivados fora da Intelligence, os 43 casos do snapshot de 07/09 | 68 (49 blocos) | 323 |
| **NAO_SEI** | `italy-real-intelligence.js` (transcrito à mão do brief, sem URL nem data de coleta) e `italy-label-verdicts.js` (vereditos sem selo nem ferramenta nomeada) | 9 | 100 |

Achados do inventário que mudam decisões:

- `italy-v21.js` **não é carregado pelo portal**: é a build anterior (`V21-843baf`) do mesmo pacote; todos
  os seus registos com ID existem no handoff canónico.
- `italy-ingested.js` (design pack 02/09) é cópia: 163/163 produtos, 503/503 atividades de
  concorrentes, 88/88 ciência, 77/77 preços, 17/17 vozes estão no handoff pelo mesmo ID.
- `meeting-intelligence-snapshot.json` é o mesmo conteúdo do `.js` (medido).
- «clientSafeCrossings» chama-se assim, mas os 19 registos têm `CLIENT_SAFE=false`.
- 58 das 79 vozes e 40 dos 157 preços trazem a data como `NOT_ESTABLISHED`: o inventário conta-os
  (`SEM_DATA_EM`) em vez de fingir uma data.

## 2 · A Label Intelligence como produto de ferramenta

`pacote/pote_ferramenta_label.py` recalcula o selo (`CONTENT_SHA256 d27278de…`, as mesmas quatro
opções de `selo.py`) e **recusa** se não bater. Copia cada registo inteiro para
`REGISTRO_DA_FERRAMENTA`; agregados e versões vão inteiros para `FERRAMENTA`. Do pote dá para
reconstruir o payload — e o teste prova que o payload reconstruído dá **o mesmo selo**.

- 376 objetos no compartimento `portfolio` (vistas Portafoglio e Etichette): 166 produtos + 210 objetos de registro.
- `PRODUZIDO_POR = pilot-label-intelligence (SINTONIA — LABEL INTELLIGENCE V1) · RUN-2026-09-06-C · v1/inteligencia/REGRAS.md@5`.
- `INTELLIGENCE_RUN_ID = FERRAMENTA:pilot-label-intelligence@RUN-2026-09-06-C` — nenhuma menção à R7.
- `BUILT_AT 2026-09-06 · DATA_DATE 20260831 · SNAPSHOT PROD_FTS_6_20260831 · COLLECTED_AT 2026-09-04`, e o sha256 do ficheiro de origem.
- `DIAS_ATE_A_SCADENZA` diz contra que data a ferramenta contou (06/09), não «hoje».
- O leitor do casco (`sintonia-pote-casco.js`) aceita-o: `conferir()` devolve 0 violações.

**Para o coordenador instalar:** o casco lê **um** pote de cada vez (`window.SINTONIA_POTE`). Carregar
este no lugar do R7 apagaria a R7. Há duas maneiras honestas, e a escolha é do coordenador:
(1) juntar o compartimento `portfolio` deste ao do R7 no publicador, mantendo os `OBJETO_ID` `LI-*`
e o `PRODUZIDO_POR` de cada objeto; ou (2) dar ao leitor um segundo lugar só para potes de ferramenta.
Nada disto foi feito aqui.

## 3 · Insumos (b)

Ver `docs/intelligence/acervo/INSUMOS-DECLARADOS-ACERVO.md`. Resumo: o portfólio ADAMA × cultura × alvo
existe (`productRelationships`, 5 402 pares) e já tem leitores (`motor/v21_crossings.py:59`,
`motor/v21_oportunidades.py:398`, `italy-app-model.js:1663`). «Concorrentes registados para o **mesmo
alvo**» é **NÃO SEI** com o que está no repo: o registro completo do Ministero (17 695 linhas, todos os
titulares) responde pela **mesma substância**, não pelo alvo.

## 4 · Itens coletados (c) — não vão ao casco

**2 080** itens em `ENTRADA-INTELLIGENCE-ACERVO.json`, cada um com `ACERVO_ID`, fonte, URL, a data **do
próprio registo** (e o nome do campo de onde veio), `CLIENT_SAFE`, `QA_STATUS`, culturas/problemas/regiões
e o sha256 do ficheiro de origem. Entram pela porta `admissao/admissao.py` → Sala → G0. O passo da
Intelligence que os lê **não está neste repositório** (motor `a5db06c4`, ramo `int-intake-g0v4-v1`).

## 5 · Auditoria D97

| pergunta | resposta | onde |
|---|---|---|
| há objeto no pote R7 que não veio da Intelligence? | **não** — 47/47 com `ESPECIE_DITA_POR = INTELLIGENCE` e prova completa da mesma corrida | `AUDITORIA-D97-R7.json → OBJETOS` |
| há cruzamento no casco sem prova ligada? | **sim, 84 de 86.** O Portafoglio desenha os 86 cruzamentos da ANALISE-R7 (mesma corrida), mas só **2** são objetos do pote. **79** o pote recusou por `PROVA_INCOMPLETA: falta DOCUMENT_ID`, **1** por `ITEM_BLOQUEADO_EM_G0`, e **4** (`NOT_POSSIBLE`, fonte candidata) o pote nem conhece. A tela marca cada um com o destino no pote — mas continuam desenhados. | `AUDITORIA-D97-R7.json → CRUZAMENTOS.SEM_A_PROVA_QUE_O_POTE_EXIGE` (cada um com `ANALISE-R7.json:linha`) |
| há tela que mostra dado que não passou pela Intelligence? | **sim.** Com o pote carregado, a **busca** e **12 vistas de detalhe** continuam a ler o modelo antigo (V2.1 + demo). A busca «vite» devolve 58 resultados antigos, 16 deles oportunidades V2.1 (`CLIENT_SAFE=false`), e cada linha abre a ficha antiga. | `portale.html:4099` (`FLAGS_DO_LEGADO` não inclui `isSearch` nem as vistas de detalhe), `portale.html:12195` (a busca lê `AM.searchIndex`) |

Proposta (não feita — decisão do coordenador): com um pote aceite, a busca e as vistas de detalhe
entram em `FLAGS_DO_LEGADO` (ou passam a procurar só nos objetos do pote); e os 84 cruzamentos sem
objeto no pote saem da lista principal para um bloco «recusados pelo pote», como já acontece com os
recusados dos outros compartimentos.

## 6 · O aviso do SHA

**Causa medida:** o gerador escreveu `POTE-R7.json` em Windows com fim de linha **CRLF** e fez o hash
desses bytes (`2610af4b…`); o Git guardou-o com **LF** (`01899678…`). Trocar cada LF por CRLF nos bytes
do Git dá **exatamente** `2610af4b…`.

**Correção sem enfraquecer:** a conferência aceita duas formas e só duas, e diz qual:
`IGUAL_BYTE_A_BYTE`, ou `IGUAL_APOS_FIM_DE_LINHA_CRLF` (só se o ficheiro não tiver CR nenhum).
Qualquer outro byte mudado dá `DIFERENTE` e a tela continua âmbar. `.gitattributes` passa a ter
`docs/casco/** -text`, para um checkout em Windows não voltar a trocar os bytes em disco. A tela diz
agora «corrisponde al manifesto dopo il solo cambio di fine riga (CRLF nel manifesto, LF nel Git)».

## Antes / depois, por tela do portal

«Antes» = hoje, com o pote R7 publicado. «Depois» = com esta organização **instalada pelo coordenador**
(nada foi instalado aqui).

| tela (rota) | antes | depois | rótulo |
|---|---|---|---|
| Radar delle Opportunità (`meeting`) | pote R7: vazio (0) | igual; as 43 oportunidades V2.1 ficam fora | Intelligence |
| Radar Futuro (`radarfuturo`) | 10 FATO_PRESENTE_SOBRE_O_FUTURO | igual | Intelligence |
| Archivio (`archive`) | 22 objetos | igual | Intelligence |
| Finestre Colturali (`windows`) | 2 sinais + sonda olivo × mosca | igual; 29 janelas EXPECTED_NORM ficam fora | Intelligence |
| Polso di Mercato (`market`) | 6 sinais | igual; 157 preços vão para a ENTRADA, não para a tela | Intelligence |
| Voci dal Campo (`voices`) | vazio | igual; 79 vozes + 184 transcrições na ENTRADA | Intelligence |
| Concorrenza (`competitors`) | vazio | igual; 577 anúncios na ENTRADA | Intelligence |
| Intelligence Scientifica (`science`) | 2 sinais | igual; 851 registos na ENTRADA | Intelligence |
| **Portafoglio / Etichette** | 2 objetos + 86 cruzamentos (84 sem objeto no pote); a Label Intelligence **não aparece** | **+ 166 produtos e 210 objetos de registro da Label Intelligence**, com a data do snapshot (31/08) e da build (06/09); os 2 objetos da R7; cruzamentos conforme a decisão acima | **ferramenta** + Intelligence |
| Registro delle fonti (`sources`) | 3 rendimentos de fonte | igual; 196 fontes são procedência (b) | Intelligence |
| Rete Commerciale (`field`) | vazio do pote, demo fora | igual | fora |
| Busca + 12 vistas de detalhe | **legado V2.1 + demo** | fora (proposta acima) | **fora** |

## Testes e trava, ditos em voz alta

- `tests/test_acervo_organizado.py` (34 provas) e `tests/test_pote_publicado.mjs` (54, com o Q8 ajustado de
  forma **declarada**, citando o item 6 desta missão sobre a D114) passam.
- Nenhum nome de teste passou a falhar. `test_trava_da_inteligencia.test_nao_apareceu_inteligencia_nova` já
  falhava antes (3 caminhos) e agora lista **5**: o censo do congelamento classifica
  `docs/acervo/INVENTARIO-ACERVO.json` e `pacote/acervo_inventario.mjs` como inteligência nova. Não mudei
  palavras para escapar à régua; a decisão de destravar é do dono.

## Design

Nenhum componente visual novo. A única mudança de tela é o texto da linha do SHA, no componente que já
existia. `ADAMA_DESIGN_SYSTEM_MATCH` não se aplica: não houve padrão novo.

## EM PALAVRAS SIMPLES

Os números antigos não eram mentira — mas estavam misturados. Separei tudo em cinco gavetas:
o que uma ferramenta já produziu e selou (a leitura das bulas: 166 produtos), o que é registro oficial
(serve de matéria-prima para a Inteligência cruzar), o que é coleta crua (2 080 itens que a Inteligência
ainda tem de ler antes de irem para a tela), o que é demonstração ou palpite antigo (fica de fora), e o
que eu não sei de onde veio (fica de fora, com o motivo escrito). A leitura das bulas está pronta para
voltar ao Portafoglio como «produto da ferramenta», com a data dela, sem recalcular nada.
Respondendo à pergunta do dono: os objetos do pote vêm todos da Inteligência; mas o Portafoglio desenha
84 cruzamentos que o próprio pote recusou por falta de documento, e a busca ainda abre dados antigos.
O aviso do SHA era só o Windows a trocar o fim de linha — agora a verificação diz isso, e continua a
apanhar qualquer outra mudança.
