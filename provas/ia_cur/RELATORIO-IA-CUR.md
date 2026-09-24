# IA-CUR — a IA do robô de fontes é um agente da casa, não a API paga

> Missão IA-CUR, 24/09/2026 (decisão do dono ~15:20: «faça um robô saindo daqui, ou saindo do
> Orca»). O agente é esta sessão Claude Code no Orca (assinatura do dono, `claude-opus-5-5`).
> Sem chave de API, sem custo novo. Tudo numa CÓPIA do livro vivo (foto 15:11, sha256 em
> `FOTO-1511.sha256`); nada instalado; nenhum livro de estado escrito pelo agente.

## 1 · O piloto — 30 casos parados

Egresso IT **BLOCKED** na primeira metade da missão (`EGRESS_COUNTRY_CODE = UNKNOWN`, o serviço
de medição não devolveu país): o agente trabalhou primeiro **só com bytes já guardados** e deixou
para o fim os casos que precisavam de página viva. Às 15:45 o portão por consenso foi instalado e
deu PASS IT — a segunda metade (§1b) correu com rede.

| grupo | casos | de onde o agente leu | resultado |
|---|---:|---|---|
| território NÃO SEI (SEMANTIC_REVIEW), com páginas que a S2 já leu (egresso IT, sha256 no `provas.jsonl` dela) | 14 | `%TEMP%\s2\provas\CAND-*` | **8 decididas** · 6 NÃO SEI com categoria |
| janela de cultura (D29) — serviços fitossanitários, agrometeo, boletins | 16 | capas que a coleta guardou por engano (`~/sintonia-sala-italia/acervo-coletor-*`) | 1 ficha de Atlas proposta · 15 **precisam de rede** |

**As 8 decisões, pela porta `decisao_semantica.py`** (3 provas cada: 1 INSTITUCIONAL + 2 CONTEÚDO,
sha256 reconferido contra os bytes; a decisão NÃO SEI da S2 passou a `ANTERIOR` na mesma linha —
a porta recusa duas linhas para a mesma candidata):

| candidata | território / país | o que aconteceu no ciclo determinístico (sem rede) |
|---|---|---|
| CAND-0503 CeMi Milano | T11 / IT | QUALIFY → **IT-T11-014** → contrato → VALIDATE_ROUTE: RETRY (robots ilegível sem rede) |
| CAND-0575 Agridigital | T10 / IT | QUALIFY → **IT-T10-045** → contrato → RETRY |
| CAND-0577 Assomao | T10 / IT | QUALIFY → **IT-T10-046** → contrato → RETRY |
| CAND-0579 Assotrattori | T10 / IT | QUALIFY → **IT-T10-047** → contrato → RETRY |
| CAND-0580 Comacomp | T10 / IT | QUALIFY → **IT-T10-048** → contrato → RETRY |
| CAND-0515 CropLife Europe | T9 / EU | a porta aceita; a QUALIFY recusa (só cunha números IT; EU é decisão do dono) |
| CAND-0527 IFA | T10 / INT | idem (INT) |
| CAND-0582 Club of Bologna | T11 / INT | idem (INT) |

O ciclo apanhou as decisões **sozinho**: o nível REPARAR da R1 (`requalificar_se_a_prova_mudou`)
viu «a prova da casa decide hoje o território» e voltou a enfileirar as 5 QUALIFY italianas.

**NÃO SEI, com a razão do agente** (registadas como proposta de relevância, `PROPOSTAS-IA-CUR-V1.json`):
Il Fatto Alimentare (consumo, fora do universo), Sherwood (identidade trocada: é a Radio Sherwood),
Quidanoi (loja online), Progetto Biomasse (bioenergia), Comagarden (jardinagem) — `NAO_E_FONTE`;
Italia Cooperativa — falta a página INSTITUCIONAL (precisa de rede).

**Janela de cultura (16)** — o diagnóstico está feito com prova; a proposta de padrão não, porque
a regra da casa é «nenhum padrão nasce sem uma matéria lida» e a listagem de boletins não está
guardada:
- 7 CANARY_PENDING: o LINK_PATTERN apanha a página institucional em vez do boletim (a coleta colheu
  «Piani Programmi Progetti», «Account area riservata», «PEC», «PR Veneto FESR», «sede di Bari»,
  «Progetti in corso», «chi siamo»); em Toscana, Veneto e ARSAC até o INDEX_URL não é a página
  de boletins;
- 6 CCF/DEGRADED: EMPTY_LIST — reparo pelo dono (R1) primeiro; o agente entra no que ela recusar;
- 2 UNKNOWN: a coleta colheu PDF de papelada;
- IT-T3-005 **Terre dell'Etruria**: boletim semanal da mosca-da-azeitona (Toscana), já colhido
  com sucesso; falta a ficha no Atlas — proposta com o sha256 do boletim guardado.

## 1b · Com rede (portão por consenso instalado às 15:45; PASS IT em cada lote)

Cópia `C:/cur/ia-copia2` (foto 15:11 + este ramo). O agente leu **15 páginas vivas** pelo MESMO
transporte do robô (`canario.buscar`, robots pela porta do robô, 2 s entre pedidos, sha256 em
`PAGINAS-LIDAS-COM-REDE.jsonl`); 1 recusada pelo robots (Lombardia: o portal do SFR está em
Disallow). Ordem da casa respeitada: **o determinístico primeiro** (importar da tabela do coletor →
REPAIR_CONTRACT da R1 → VALIDATE_ROUTE → CANARY); o agente só entrou onde a R1 recusou.

**Achado do agente que é defeito da casa**: `canario.hrefs_da_entrada` deitava fora a ligação
relativa sem barra («news_open.php?EW_ID=15142») e não desfazia `&amp;`. A Assomao tem 44 notícias
assim e o canário via 0 — e a R1, que lê pelo mesmo leitor, dizia SEM_FAMILIA_DE_ITENS. Consertado
no ramo (5239309a, com teste); o reparo da R1 foi repetido à mão, na cópia, depois do conserto.

**D31 (candidatas EU/INT)**: a QUALIFY aceita EU/INT só com `NUMERACAO_FORA_DE_IT` escrito na
decisão (b69febce) e o validador de contratos aceita `EU-`/`INT-` (55588d50). CropLife Europe →
**EU-T9-003**, IFA → **INT-T10-001**, Club of Bologna → **INT-T11-001**: contrato OK; CropLife e Club
of Bologna falham o canário (EMPTY_LIST; a R1 não acha família); a IFA tem o endereço em
**Disallow no robots** (ROUTE_BLOCKED). ⚠️ `reconciliar_livros.SOURCE_ID_RE` (a ponte para a produção)
só aceita `IT-` — EU/INT não atravessam a ponte até alguém a alargar.

## 2 · X/30 destravadas, e comparação com S2/S3

**Estado final dos 30 na cópia com rede** (`ESTADO-FINAL-30.json`):

| resultado | N | casos |
|---|---:|---|
| **READY_FOR_COLLECTION pela régua** | **6** | por proposta do agente: **Assomao IT-T10-046**, **Soc. Entomologica IT-T3-020**, **AIAM IT-T2-015** · pelo determinístico dentro do piloto (import CUR + R1): **SFR Toscana IT-T3-015**, **SIPaV IT-T3-021**, **Difesa fitosanitaria IT-T3-023** |
| a régua recusou a proposta do agente | 2 | ARSAC (achou os 5 boletins; o item é MIXED — corpo útil não provado), IPSP (o item parecia navegação) |
| andaram (SOURCE_ID + contrato) e pararam no canário/robots | 7 | CeMi IT-T11-014, Agridigital IT-T10-045, Assotrattori IT-T10-047 e Comacomp IT-T10-048 (comunicados em .docx, fora do HTML), EU-T9-003, INT-T11-001, INT-T10-001 (robots) |
| propostas para decisão humana/dono | 10 | ficha Atlas Terre dell'Etruria (boletim da mosca-da-azeitona), 5 recusas de relevância, SFN (os itens são PDF DTU: OUTPUT_TYPE), Campania agrometeo (é tabela: outra estratégia), Campania autorizações (app com login), SFR Lombardia (robots proíbe) |
| NÃO SEI | 5 | Italia Cooperativa (sem institucional), SFR Emilia-Romagna (boletins montados por JavaScript; importação recusada), CNR ISPA (importação recusada), Veneto (a newsletter-sr é do desenvolvimento rural), Agroinnova (entrada institucional) |

**6/30 chegaram a READY** (20 %); 3 delas por proposta do agente, 3 pelo caminho determinístico que o
piloto destravou (a importação do contrato da tabela do coletor, da CUR, e o reparo da R1).

| medida | piloto IA-CUR | S2/S3 (lote Opus 181) |
|---|---:|---|
| território decidido com prova | 8 / 14 dos casos de território (57 %) — **8 / 28** das NÃO SEI da S2 com bytes guardados (29 %) | 25 / 181 (14 %) |
| SOURCE_ID novo + contrato | **8 / 30** (5 IT + 3 EU/INT pela D31) | 18 / 181 viraram SOURCE_ID |
| READY_FOR_COLLECTION | **6 / 30** (3 por proposta do agente) | 5 / 181 hoje |

Leitura honesta: a taxa de decisão é mais alta que a da S2 porque o agente relê bytes já lidos e
aceita como CONTEÚDO as listagens datadas de comunicados que a S2 recusou (FederUnacoma); essa é uma
régua mais larga, escrita no PORQUE de cada decisão. Se o dono preferir a régua da S2, as 4
FederUnacoma voltam a NÃO SEI — e as 4 são a mesma família (FederUnacoma), com risco de fontes
irmãs a colher o mesmo. A amostra do piloto não é aleatória (escolhida entre as que tinham texto
ou prioridade D29), por isso 20 % READY não é a taxa esperada no livro inteiro.

## 3 · Quanto gastou (medido na sessão)

Registo desta sessão (`~/.claude/projects/.../*.jsonl`), desde a mensagem da missão até ao fim do
piloto com rede: **77 respostas, 101 mil tokens de saída, 61,4 milhões de tokens de entrada — dos
quais 61,2 milhões releitura de cache** (a parte sem rede, sozinha: 28 respostas, 34 mil de saída).
Em preço de API (Opus 5.5) seria ≈ US$ 15; pela assinatura, é cota. **Não consigo ler o
medidor de cota da assinatura** a partir daqui — só os tokens.

⚠️ A entrada é dominada pelo tamanho DESTA conversa (muito longa, relida a cada resposta), não pelo
trabalho de ler páginas. Uma bancada nova, só para este trabalho, releria muito menos. Estimativa
(não medida): ~40–60 mil tokens de contexto por resposta × ~30 respostas ≈ 1,5 milhão de entrada por
lote de 30.

## 4 · Funcionamento contínuo sem API

```
robô de fontes (determinístico, sem conta)          bancada Orca (Claude Code, assinatura)
────────────────────────────────────────            ─────────────────────────────────────────
QUALIFY bloqueia SEMANTIC  ─┐                       lê a fila por lotes de 30 (agendado:
R1 recusa o reparo  ────────┼─► FILA-PRECISA-DE-IA   2×/dia, ou quando a fila passa de N)
canário PASS_PARCIAL capa ──┘   (escritor: o robô)   lê os BYTES GUARDADOS (o robô busca as
o robô BUSCA as páginas pelo portão de egresso        páginas; o agente não vai à rede)
                                                     escreve SÓ nas portas:
QUALIFY lê DECISOES-SEMANTICAS  ◄─────────────────── DECISOES-SEMANTICAS-V1 (território)
reparar_contrato.aplicar lê as propostas ◄────────── PROPOSTAS-IA-CUR-V1 (padrão, relevância)
VALIDATE_ROUTE → CANARY → régua  (quem promove é a régua; o agente nunca)
```

- **Um escritor por ficheiro**: a fila é do robô (o agente só lê); as decisões e as propostas são do
  agente (o robô só lê). Nenhum livro de estado é escrito pelo agente.
- **Se o agente parar** (conta trocada, limite de uso, sessão morta): a fila cresce, os casos ficam
  NÃO SEI, e o ciclo determinístico continua igual — medido hoje: o ciclo correu, requalificou e
  escreveu contratos sem o agente estar no circuito.
- **Rede**: o agente não precisa dela; quem busca páginas é o robô, pelo portão de egresso IT.
- **Prova**: sem URL + sha256 de bytes lidos, a porta ignora a proposta («uma decisão sem prova é
  uma opinião»).

## 5 · O que falta (com dono)

- a ponte para a produção (`reconciliar_livros.SOURCE_ID_RE`) só aceita `IT-`: EU/INT (D31) não atravessam;
- o conserto do leitor do canário muda o que a R1 vê em TODAS as fontes com ligações relativas: medir no livro inteiro antes de instalar;
- A fila `FILA-PRECISA-DE-IA` e o agendamento da bancada: desenhados, **não construídos**.
- EU/INT: a numeração fora de IT é decisão do dono (3 decisões aceites e paradas por isso).
- Terre dell'Etruria no Atlas: decisão humana.
