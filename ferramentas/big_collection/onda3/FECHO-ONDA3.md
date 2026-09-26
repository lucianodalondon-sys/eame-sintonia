# FECHO-ONDA3 — o fecho da 3.ª onda web, por leitura

Missão FECHAR-ONDA3 (coordenador, 25/09 22:30). Ramo `fechar-onda3-v1`, nascido do vivo
`ce28040c`. **Só leitura:** sem rede, sem coleta, sem escrita na Sala nem no vivo, nada instalado.
Sala lida com `default_transaction_read_only=on` (PGOPTIONS). Medido em 25/09/2026 ~22:00–22:35 (-03).

Onda: `C:\Users\London1\sintonia-sala-italia\ondas\ONDA3-WEB-20260925-1934`
(`ONDA-WEB-ESTADO.json` sha256 `3b64a3e2…`, `TETO-ONDA.json` `56079789…`).

---

## RESUMO (os campos pedidos)

| campo | valor | prova |
|---|---|---|
| C1 egresso IT por corrida | **PASS por leitura** (FAIL no relatório instalado) | ver C1 abaixo |
| C2 matéria não capa | **FAIL** — 1 de 7 suspeitas não é matéria (raw 1533) | ver C2 |
| C3 ponte em runtime | **PASS por leitura** (FAIL no relatório instalado) | ver C3 |
| C4 proveniência completa | **PASS** | 14/14 linhas da Sala com cadeia inteira; 75/75 observações com storage, derivado e decisão |
| C5 fact time/location | **PASS** | 14 na Sala; FACT_TIME_UNKNOWN 10, FACT_LOCATION_UNKNOWN 9; FACT_TIME = CAPTURED_AT 0 |
| C6 zero bypass | **PASS** | SALA_SEM_SIM_NO_LIVRO [] · SIM_FORA_DA_SALA [] |
| C7 proporção por fonte e classe | **PASS** | SIM 14 · NAO 31 · NAO_SEI 21 · NAO_SE_APLICA 9 (de 75) |
| C8 duas perguntas | **PASS** | gabarito 1/1 (IT-T10-022, NAO esperado NAO) |
| C9 idioma não dá NAO SEI | **PASS** | it 70 · en 3 · NAO SEI 2; estrangeiro sem sinal 0 |
| **ITENS_NOVOS_REAIS** | **12 de 14** | 14 − 1 tipo B − 1 tipo C (secção 5) |
| **DUPLICADOS** | **A 0 · B 1 · C 1** | IT-T9-011 (B), IT-T5-186 ENEA (C) |
| **RUNS_SEM_LINHA** | **0 de 38** | todas as 38 RUN_ID em `runs.ndjson` do vivo |
| **BYTES_OK** | **76 de 76** | ficheiro no armazém, sha256 e tamanho iguais ao `raw_asset` |
| **PROVA_TETO** | **PASS** | 38 corridas, 167 pedidos, 39 domínios, máx. 5, 0 acima; livro = `runs.ndjson` (39 = 39) |
| **VEREDITO_ONDA3** | **FECHADA, com 1 FAIL (C2) e 2 itens a corrigir na Sala** | secção 7 |

Relatório instalado (`relatorio/RELATORIO-PASSAGEM.json`): **6 de 9**. O mesmo relatório pelo ramo
`c9-idioma-v1` (não instalado), numa cópia, com o livro de decisões do vivo: **8 de 9** — só C2 fica.

---

## 1. Identidade da onda (modelo `065f7ceb`, preenchido)

| campo | valor | fonte |
|---|---|---|
| pasta da onda | `…\ondas\ONDA3-WEB-20260925-1934` | — |
| árvore do vivo | `ce28040c` | `ONDA-WEB-ESTADO.json` `ARVORE` |
| coorte | sha256 do blob `eb7b6ab7…` · **64 fontes** · `INSTALACAO 4c7f540c` · B5 «ninguem sai (… mantida na 3.a onda, D76)» | `COORTE-BIG-COLLECTION-V1.json` @ `ce28040c` |
| início → fim | 19:34:21 → 19:58:33 (24 min) | `ONDA-WEB-ESTADO.json` |
| disjuntor | nenhum (`PAROU: null`) | idem |

**Porque a mensagem do commit diz 60 e o ficheiro diz 64.** O ficheiro é coerente consigo: `COORTE`
tem 64 linhas, `COORTE_BIG_COLLECTION = 64`, e a onda correu 64 (`FONTES` com 64). O plano deu 65
PRONTAS; 17 ficam em `FORA` (com o porquê). Na lista, **4 fontes têm o canário de 22:27–22:28Z**,
quatro minutos antes do congelamento (22:31:43Z): IT-T2-006, IT-T5-025, IT-T9-009, IT-T9-011 (idade
0,0 dias). As outras 60 já tinham canário anterior. **Inferência, não provada:** o «60» foi contado
antes destes 4 canários. O número que vale é o do ficheiro: 64.

## 2. Resultado por fonte

Fonte: `ONDA-WEB-ESTADO.json` (`FONTES[]`, deltas `SALA_ANTES/SALA_DEPOIS`) e `RELATORIO-PASSAGEM.json`
(`C7.POR_FONTE`, admissão por derivado). Egresso IT/IT nas 38 que correram.

| N | SOURCE_ID | STATUS | s | domínio · pedidos | raw Δ | Sala Δ |
|---|---|---|---|---|---|---|
| 1 | IT-T10-018 | SUCCESS | 41 | myfruit.it · 5 | 3 | 1 |
| 2 | IT-T10-021 | SUCCESS | 26 | imagelinenetwork.com · 4 | 2 | 0 |
| 3 | IT-T10-022 | SUCCESS | 39 | zootecnicainternational.com · 5 | 3 | 0 |
| 4 | IT-T12-024 | SUCCESS | 70 | regione.veneto.it · 5 | 3 | 0 |
| 5 | IT-T12-117 | SUCCESS | 32 | calabriaimpresa.eu · 4 | 2 | 0 |
| 6 | IT-T12-129 | SUCCESS | 72 | regione.sicilia.it · 5 | 3 | 0 |
| 7 | IT-T12-130 | SUCCESS | 36 | edagricole.it · 5 | 3 | 0 |
| 9 | IT-T12-137 | SUCCESS | 25 | psrn.it · 5 | 1 | 0 |
| 10 | IT-T2-006 | SUCCESS | 37 | arpacampania.it · 5 | 3 | 0 |
| 11 | IT-T2-032 | SUCCESS | 25 | arpal.liguria.it · 4 | 2 | 0 |
| 12 | IT-T2-034 | SUCCESS | 11 | arpa.marche.it · 2 | 0 | 0 |
| 13 | IT-T2-037 | SUCCESS | 26 | arpat.toscana.it · 3 | 1 | 0 |
| 15 | IT-T2-051 | SUCCESS | 19 | arpae.it · 2 | 0 | 0 |
| 16 | IT-T2-146 | SUCCESS | 40 | arpa.veneto.it · 5 | 3 | 0 |
| 19 | IT-T5-025 | SUCCESS | 16 | santannapisa.it · 5 | 0 | 0 |
| 20 | IT-T5-056 | SUCCESS | 36 | crea.gov.it · 5 | 3 | 2 |
| 24 | IT-T5-160 | SUCCESS | 27 | cnr.it · 5 | 1 | 1 |
| 26 | IT-T5-186 | SUCCESS | 74 | enea.it · 5 | 3 | 2 |
| 29 | IT-T7-017 | SUCCESS | 37 | riuniteciv.com · 5 | 3 | 0 |
| 30 | IT-T7-019 | SUCCESS | 34 | confagricoltura.it · 5 | 3 | 0 |
| 31 | IT-T7-021 | SUCCESS | 26 | etvilloresi.it · 5 | 1 | 0 |
| 32 | IT-T7-033 | SUCCESS | 11 | chianticlassico.com · 2 | 0 | 0 |
| 33 | IT-T7-042 | SUCCESS | 36 | consorziobalsamico.it · 5 | 3 | 0 |
| 34 | IT-T7-043 | SUCCESS | 11 | federchimica.it · 2 | 0 | 0 |
| 35 | IT-T7-048 | SUCCESS | 65 | caiagromec.it · 5 | 3 | 0 |
| 36 | IT-T7-049 | SUCCESS | 36 | copagri.org · 5 | 3 | 0 |
| 37 | IT-T7-103 | SUCCESS | 31 | confcooperative.it · 5 | 3 | 0 |
| 38 | IT-T7-118 | SUCCESS | 31 | cia.it · 5 | 2 | 0 |
| 39 | IT-T7-117 | SUCCESS | 29 | caf-cia.it · 5 | 2 | 0 |
| 43 | IT-T7-125 | SUCCESS | 36 | cia-puglia.it · 5 | 3 | 0 |
| 45 | IT-T7-139 | SUCCESS | 34 | florovivaistiitaliani.it · 5 | 3 | 0 |
| 46 | IT-T7-141 | SUCCESS | 10 | ciatoscana.eu · 2 | 0 | 0 |
| 47 | IT-T7-163 | SUCCESS | 33 | casalasco.com · 5 | 3 | 3 |
| 48 | IT-T7-172 | SUCCESS | 10 | georgofili.info 1 + georgofili.it 1 | 0 | 0 |
| 61 | IT-T8-062 | SUCCESS | 17 | uniss.it · 5 | 1 | 0 |
| 62 | IT-T9-009 | SUCCESS | 34 | cifo.it · 5 | 3 | 1 |
| 63 | IT-T9-011 | SUCCESS | 29 | koppert.it · 5 | 1 | 1 |
| 64 | IT-T9-021 | SUCCESS | 34 | indire.it · 5 | 3 | 3 |

**TETO_DOMINIO (26, não correram):** edagricole.it 14 (IT-T12-131, IT-T3-023, IT-T8-021/022/024/028/029/030/034/039/040/041/042/051) ·
crea.gov.it 4 (IT-T5-080/111/113/167) · cia.it 4 (IT-T7-112/121/123/135) · enea.it 2 (IT-T5-185/187) ·
arpacampania.it 1 (IT-T2-050) · arpa.veneto.it 1 (IT-T2-145).

**Totais:** correram 38 de 64 · SUCCESS 38 · FAILED 0 · TETO_DOMINIO 26 · raw novos 76 (75 criados +
1 tentativa `TRANSPORT_OR_EMPTY` da IT-T8-062, cortada pelo teto do uniss.it) · itens novos na Sala 14 ·
admissão (75 derivados): SIM 14 · NAO 31 · NAO_SEI 21 · NAO_SE_APLICA 9.
7 corridas sem documento novo (raw Δ 0: IT-T2-034, IT-T2-051, IT-T5-025, IT-T7-033, IT-T7-043, IT-T7-141,
IT-T7-172) — por isso `collection_run` tem 31 linhas destas 38 corridas, e não 38.

Comparação com a 2.ª onda: 28 fontes → 64; SUCCESS 20 → 38; FAILED 1 → 0; TETO_DOMINIO 7 → 26;
itens novos na Sala 7 → 14.

## 3. Pedidos por domínio (D38)

- **PROVA-TETO = PASS** (`provas/prova_teto_dominio.py`, saída em
  `auditoria-madrugada\FECHAR-ONDA3-c9\PROVA-TETO-ONDA3.json`, sha256 `5f734cfb…`): 38 corridas ·
  **167 pedidos** · 39 domínios · máximo 5 · acima do teto: nenhum · corridas sem linha: nenhuma ·
  sem `PEDIDOS_POR_HOST`: nenhuma.
- Livro do teto (`TETO-ONDA.json`) contra `runs.ndjson`, domínio a domínio: **39 = 39, 167 = 167,
  0 diferenças.** Pela primeira vez a prova independente fecha sem NAO_SEI.
- A mensagem do coordenador diz 165 pedidos; o medido é 167. NÃO SEI de onde veio o 165 (talvez a previsão do plano).
- O `NETWORK_REQUESTS` do coletor no relatório (113) conta outra coisa (não inclui tudo o que o teto
  conta, p. ex. robots); não é contradição com os 167. **Não verificado linha a linha.**

## 4. Data e local dos 14 itens novos (migration 033)

Fonte: `SELECT … from sala_de_espera_atual` (read-only), com os 38 RUN_ID. Revisões nos itens da
onda: **0** (a Sala tem 478 revisões, nenhuma sobre estes 14).

| SOURCE_ID | item | publicação · base | data do fato · base | local do fato · base |
|---|---|---|---|---|
| IT-T10-018 | derived:991 | 2026-09-25 · meta article:published_time | NAO SEI | NAO SEI |
| IT-T5-056 | derived:1019 | NAO SEI | NAO SEI | NAO SEI |
| IT-T5-056 | derived:1018 | NAO SEI | NAO SEI | NAO SEI |
| IT-T5-160 | derived:1021 | 2020-02-20 · JSON-LD datePublished | NAO SEI | NAO SEI |
| IT-T5-186 | derived:1022 | NAO SEI | 5 ottobre 2026 · texto, EVENTO ⚠️ | Brindisi ; Roma · texto ⚠️ |
| IT-T5-186 | derived:1024 | 2026-09-18 · meta article:published_time | 28 settembre · texto, EVENTO | Napoli · texto |
| IT-T7-163 | derived:1055 | NAO SEI | NAO SEI | NAO SEI |
| IT-T7-163 | derived:1054 | NAO SEI | NAO SEI | NAO SEI |
| IT-T7-163 | derived:1056 | NAO SEI | NAO SEI | NAO SEI |
| IT-T9-009 | derived:1058 | 2026-02-10 · JSON-LD | NAO SEI | NAO SEI |
| IT-T9-011 | derived:1060 | 2025-09-12 · JSON-LD | NAO SEI | NAO SEI |
| IT-T9-021 | derived:1062 | 2026-09-25 · JSON-LD | 21-23 ottobre · texto, APPROXIMATE | Abruzzo · texto |
| IT-T9-021 | derived:1061 | 2026-09-24 · JSON-LD | NAO SEI | Abruzzo · texto |
| IT-T9-021 | derived:1063 | 2026-09-22 · JSON-LD | 21-23 ottobre 2026 · texto | Abruzzo · texto |

Local da fonte: **NAO SEI nos 14** — nenhum dos contratos destas fontes declara onde está quem publica.

| campo (denominador 14) | PROVADA | CALCULADA | NAO SEI |
|---|---|---|---|
| publicação | 8 | 0 | 6 |
| local da fonte | 0 | 0 | 14 |
| data do fato | 4 | 0 | 10 |
| local do fato | 5 | 0 | 9 |

(de `completude_tempo_lugar`; C5 do relatório diz o mesmo: FACT_TIME_UNKNOWN 10, FACT_LOCATION_UNKNOWN 9.)

⚠️ **derived:1022 está errado por dentro:** é uma página de lista (secção 5, tipo C). A data «5 ottobre»
vem do evento em L'Aia (Países Baixos), e «Brindisi» vem de outro evento da mesma lista. O leitor
juntou dois acontecimentos numa linha. «PROVADA» aqui quer dizer «tem frase», não «está certa».

## 5. Duplicados (tipos A/B/C da ROTEIRO-REUNIAO, `origin/roteiro-reuniao-v1:ROTEIRO-REUNIAO-SEGUNDA.md`)

Cada item novo comparado com as 94 linhas da Sala (endereço do bruto, sha256 do bruto, `item_id`, md5 do texto).

| tipo | regra | nesta onda | prova |
|---|---|---|---|
| A | mesmo documento, mesmo sha, mesmo `item_id` | **0** | — |
| B | mesmo documento (endereço), outro bruto, outro `item_id` | **1**: IT-T9-011 `derived:1060` | mesmo `source_url` que `derived:66` (2 linhas de 20/09); sha e texto diferentes. A regra de hoje não barra, porque compara o `item_id` |
| C | página de lista, não matéria | **1**: IT-T5-186 `derived:1022` (`sostenibilita.enea.it/eventi/meeting-internazionali-0`) | o texto na Sala traz vários eventos, cada um com «Leggi tutto su …» |

**ITENS_NOVOS_REAIS = 12 de 14.** Ressalvas que não entram na conta A/B/C mas pesam:
IT-T5-160 `derived:1021` é a página fixa de uma linha de investigação do CNR (publicada em 2020), não
notícia; IT-T9-011 é de 2025-09-12. Nenhum dos 14 repete um texto que já estava na Sala.

## 6. C1, C2, C3 — o que falha e porquê

**C1 e C3: a falha é só de leitura.** O relatório instalado (`ce28040c`) lê `MEDIDO: []` e
`GATE_NO_INSTANTE: []` porque não sabe ler as corridas do `ONDA-WEB-ESTADO.json`. O ramo
`c9-idioma-v1` (`bcefc6d9`, não instalado) traz `relatorio --estado=`. Corrido numa cópia própria
(`c9-copia-fechar-onda3`, detached), com a Sala em só-leitura e `ITALY_OPS_ROOT` = o vivo (só lido):
- C1 = PASS: 38 corridas, egresso IT antes e IT depois em todas;
- C3 = PASS: veredito do portão no instante = `ELIGIBLE` em todas.
- ⚠️ Na primeira passagem a cópia deu 5/9, com C4/C6/C7 em FAIL (`COM_DECISAO: 0`). A causa: o
  relatório lê `data/samples/LIVRO-DE-DECISOES.json` da **sua** árvore, e a do `c9-idioma-v1` (nascido
  de `df0865e6`) não tem as decisões da 3.ª onda. Com o livro do vivo copiado para a cópia (sha256
  igual, `a02db40c…`): **8 de 9**. Ao instalar o C9, este é o comportamento certo (o vivo tem o livro).
- Saídas: `auditoria-madrugada\FECHAR-ONDA3-c9\` (1.ª passagem) e `…\FECHAR-ONDA3-c9b\` (8/9).

**C2 = FAIL.** Li o bruto das 7 linhas de `relatorio/CAPAS-A-CONFIRMAR.tsv` no armazém:

| raw | fonte | o que é | classe |
|---|---|---|---|
| 1495 | IT-T12-024 | «Dettaglio news»: graduatoria promozione vini Paesi terzi, 23/09/2026 | matéria |
| 1501 | IT-T12-129 | aviso: Pratiche agroecologiche, L.R. 21/2021, publicado 21/01/2025 | matéria |
| 1502 | IT-T12-129 | aviso: commissioni d'esame esercizio venatorio, 12/11/2024 | matéria |
| 1515 | IT-T2-146 | «Pollini: giornate di studio a Pesaro», 1–2/10/2026 | matéria |
| 1523 | IT-T7-017 | «Ottocentorosa conquista i cieli di Roma» (texto de 2018) | matéria (antiga) |
| **1533** | **IT-T7-048** | **«L'Associazione / Chi siamo» do CAI: só menu institucional (147 caracteres no `<main>`)** | **não é matéria** |
| 1558 | IT-T9-009 | «Catalogo CIFO 2026» (post da newsroom) | matéria |

O juiz acertou 1 em 7. O 1533 **não chegou à Sala** (SELECT por `raw_observation_id=1533`: vazio), mas foi
coletado como matéria. Pela regra «matéria, não capa», uma página que não é matéria colhida faz C2 = FAIL.
E há outra página de lista que o juiz **não** apanhou e que **entrou** na Sala: `derived:1022` (secção 5).

## 7. RUNs e bytes

- 38 RUN_ID no estado; **38 com linha** em `source-curator-service-v1\data\collection-ledger\italy\runs.ndjson`;
  RUNS_SEM_LINHA = 0.
- `raw_asset` destas 38 corridas: 76 linhas, todas `preserved = true`; para as 76, o ficheiro existe em
  `%USERPROFILE%\sintonia-sala-italia\armazem`, com **sha256 e tamanho iguais** ao registo. BYTES_OK = 76/76.
- 7 corridas sem bruto (as de raw Δ 0, secção 2): viram só o que já conheciam.

## 8. Sala antes / depois

| tabela | início | fim | Δ | desceu? |
|---|---|---|---|---|
| sala_de_espera | 80 | 94 | +14 | não |
| raw_asset | 1486 | 1562 | +76 | não |
| storage_object | 1178 | 1254 | +76 | não |
| derived_artifact | 988 | 1063 | +75 | não |
| collection_run | 426 | 457 | +31 | não |

(fonte: `ONDA-WEB-ESTADO.json` `SALA_INICIO`/`SALA_FIM`; 94 linhas confirmadas por SELECT às 22:3x.)

## 9. VEREDITO_ONDA3

**FECHADA, com um FAIL (C2) e dois itens a corrigir.** A rede portou-se: 0 falhas, teto respeitado e
provado de forma independente, todos os bytes guardados e conferidos. A qualidade do que entrou tem
furos: 1 página de lista entrou na Sala com data e lugar misturados (`derived:1022`), 1 documento
repetido com outro número (`derived:1060`), e 1 página institucional foi colhida como matéria (raw 1533,
fora da Sala). C1/C3 passam quando o C9 for instalado.

Para a próxima onda (propostas, não decididas):
1. instalar o `c9-idioma-v1` (C1/C3 deixam de falhar por leitura);
2. o juiz de capa tem de apanhar a «lista de eventos com Leggi tutto» e a «página Chi siamo»;
3. a regra «um documento = uma linha» tem de comparar o documento (endereço), não o `item_id` (tipo B);
4. edagricole.it gasta o teto numa fonte e deixa 13 paradas: a rotação justa vai servi-las, uma por onda.

## EM PALAVRAS SIMPLES

- A 3.ª onda visitou 38 sites, sem nenhum erro, e trouxe 76 páginas. Todas estão guardadas e conferidas pela impressão digital.
- Nenhum site recebeu mais de 5 visitas. Desta vez conseguimos provar isso por dois cadernos diferentes, que batem: 167 = 167.
- Na Sala entraram 14 itens. **12 são novos de verdade.** 1 é uma notícia que já lá estava, com outro número. 1 é uma página com uma lista de eventos, e não uma notícia.
- Nesse item da lista, a data e o lugar vêm de eventos diferentes. É como pegar a data de uma festa e o endereço de outra.
- Dos 14 itens, 8 têm data de publicação provada, 4 têm a data do acontecimento e 5 têm o lugar do acontecimento. Onde fica quem publica: nenhum, porque nenhuma destas fontes diz isso no contrato.
- Das 9 verificações, 6 passam no relatório de hoje. Com o conserto C9, que ainda não está instalado, passam 8. A que continua a falhar é «matéria, não capa»: uma página «Quem somos» foi colhida como se fosse notícia (não entrou na Sala).

## O que NÃO fiz

Não abri rede, não corri coleta, não escrevi na Sala nem no vivo, não instalei nada. A cópia do C9 é
uma pasta minha (`c9-copia-fechar-onda3`), com o livro de decisões copiado do vivo só por leitura.
