# PERIODO-E-CHAVES — o período, a região sem nomes, a cultura fora de T1, e o caderno que as escreve

> Ramo `periodo-chaves-v1`, a partir do vivo `69b0e23f`. **NÃO instalado.** Missão:
> `auditoria-madrugada/missao-periodo-e-chaves.txt` (INT-LAW-091: sem chave não há cruzamento).
> Sem rede, Sala real só lida (`default_transaction_read_only=on`), RAW e livro intocados, nenhum
> Postgres ligado, trava D33 intacta: **nada foi cruzado**.

## Resposta curta

| | Cultura | Região do fato | Fase | Período | com cultura + região + período | com as 4 |
|---|---|---|---|---|---|---|
| **Sala (94)** · antes → depois | 0 → **14** | 19 → **18** | 0 → 0 | 0 → **18** | 0 → **1** | 0 → 0 |
| **Acervo (1.158)** · antes → depois | 4 → **56** | 51 → **44** | 0 → 0 | 0 → **18** | 0 → **5** | 0 → 0 |

«Antes» = QUATRO-CHAVES-MEDIR (`b2870420`); «depois» = este ramo, mesma estrada, mesmos dados.

- **Pares cruzáveis (mesma cultura + região + período, sem cruzar): 2.** Os dois são **a mesma página
  capturada duas vezes** pela mesma fonte (IT-T1-021 AgroNotizie, grano/patate × Basilicata ×
  24–27/09/2026; IT-T9-009 Cifo, pomodoro × Piacenza × 19–20/02/2026 — mesmo título, texto quase do
  mesmo tamanho, sha256 do texto diferente). **Pares entre factos diferentes: 0. Entre fontes
  diferentes: 0.**
- **As 4 chaves juntas: 0 em 1.252.** A FASE só existe em T1 com SIM na porta, e nenhum T1 teve SIM.

## 0. A base do ramo — depende do LOTE 2

O vivo `69b0e23f` (LOTE 1) **não tem** as quatro chaves nem o conserto da régua. Estão no LOTE 2
(`missao-integra-noite-lote2.txt`), ainda por instalar. Este ramo junta-os primeiro, tal e qual:

| Commit | O quê |
|---|---|
| `821ad553` | junta `quatro-chaves-v2` `b2870420` (só um gerado do mapa em conflito: ficou o do vivo) |
| `569cd507` | junta `conserto-regua-v1` `a139caad` (sem conflito) — 130 testes OK na base |

**Instala-se DEPOIS do LOTE 2.** Com o LOTE 2 no vivo, a junção deste ramo não traz nada de novo
desses dois: só os commits abaixo.

## 1. O PERÍODO (a chave JANELA) — só de FACT_TIME

`admissao.periodo_do_fato(item)` lê o `fact_time` que o extractor do facto escreveu (LUGAR-FATO, DA-6)
e devolve o intervalo que ele cobre, em ISO 8601, com a precisão:

| FACT_TIME (formas reais da Sala) | Período | Precisão |
|---|---|---|
| `12-13 novembre 2026` | `2026-11-12/2026-11-13` | INTERVALO |
| `29 settembre 2026` | `2026-09-29` | DIA |
| `maggio 2026` | `2026-05` | MES |
| `2025` · `campagna 2010` · `raccolta 2026` | `2025` · `2010` · `2026` | ANO |
| `2026-09-07/2026-09-13` (calculada da publicação, D63) | `2026-09-07/2026-09-13` | INTERVALO+CALCULADA |
| `28 settembre` · `21-23 ottobre` · `maggio` (sem ano) | **NAO SEI** | — |
| FACT_TIME `NAO SEI` | **NAO SEI** | — |

- **Nunca de PUBLISHED_AT nem de CAPTURED_AT.** Sem ano escrito, o ano **não** se completa com a
  publicação (isso faria da publicação o tempo do facto). Data que não existe (`31 febbraio`) ou
  intervalo ao contrário → NAO SEI.
- Uma data que o extractor **calculou** a partir da publicação («ieri» + data provada) é FACT_TIME do
  dono dela: passa, marcada `+CALCULADA`, para quem cruzar saber.
- A chave diz `VEIO_DE` (`item.fact_time`), `BASE` (a `fact_time_basis`), `PRECISAO`, `EXPRESSAO` (o
  texto original) e `FORMA`: «período do FACTO; não é janela agronómica (CAP-WIN)».

## 2. Região e cultura

### Região: os 3 erros da amostra

| Erro lido à mão | Quem conserta | Como |
|---|---|---|
| página com 2 eventos (IT-T5-186, «Brindisi ; Roma») | **CONSERTO-REGUA** (`a139caad`, já no ramo) | datas de evento diferentes: só vale o lugar do evento escolhido → NAO SEI |
| «oltre che **Bologna Fiere**, socio di FederBio» (IT-T7-031) | este ramo | o lugar colado a um nome de **empresa** (`Fiere`, `SpA`, `Srl`, `Group`, `Holding`) é o nome |
| «**ARPA Lazio** – Seminario…» (IT-T2-025) | este ramo | o lugar colado a um nome de **órgão** (`ARPA*`, `APPA`, `Agenzia regionale…`) é o nome |

`leis/fato_do_texto.py` (`_e_pedaco_de_nome`, secção 4c), no mesmo sítio onde o CONSERTO-REGUA
trabalhou — um só dono. **Exceção:** com uma preposição de lugar antes do nome («**a** Fiera Bolzano»,
«**presso** ARPA Lazio») é o SÍTIO do evento e continua a valer.

**O que mudou na medida** (as únicas 10 regiões diferentes em 1.252 documentos, todas lidas):
3 na Sala pelo CONSERTO-REGUA (Roma;Milano;Brescia;Padova;Napoli → Roma · Rimini;Piemonte → Rimini ·
Brindisi;Roma → NAO SEI) e 7 no acervo por este ramo (6 vídeos «ARPA Lazio» → NAO SEI · Bologna Fiere →
NAO SEI). Nenhuma região certa da amostra mudou (Firenze, Bolzano, Milano, Teramo, Napoli).

### Cultura fora de T1

A régua de cultura só existe para T1, e a porta **não muda** (nenhum gate relaxado). O dono das chaves
passa a **ler** a cultura fora de T1 — só em dois sítios:

1. o **título** (a primeira linha do texto);
2. a **frase que prova o lugar** (as citações «…» da `fact_location_basis`).

⚠️ Não o corpo inteiro: a barra lateral repete títulos de outras notícias («a Firenze prezzo mirtilli»
aparece em dezenas de páginas da myfruit). Vocabulário: o da régua T1 + `CULTURA_SO_DA_CHAVE`
(`mela`, `mirtillo/i`, `lampone/i`, `mora` — tirados dos 4 casos; «in/di mora» de pagamento fica de
fora). `VEIO_DE` diz de qual dos dois sítios veio; `BASE` diz «leitura para a chave, não decisão da
porta». A evidência de OUTRA régua (`cultura: True` num T2) **não** conta.

Os 4 casos da amostra: mirtilli (IT-T10-018), mela/meleto (IT-T10-018), fragole (IT-T10-017), mora
(IT-T9-017) — **4/4 lidos**.

**20 culturas novas lidas à mão** (ao acaso, semente `20260926`; `AMOSTRA-CULTURA.json`):
**19 certas, 1 duvidosa, 0 erradas.** A duvidosa: «Che ne sai tu di un campo di grano» (IT-T7-035) é um
verso de canção no título de um vídeo — pode ou não falar de trigo. Com 20 casos, é um sinal, não uma taxa.

⚠️ **Lei mudada, declarada.** Dois testes antigos (`tests/test_quatro_chaves.py`:
`test_outro_universo_nao_inventa_cultura`, `test_palavras_de_outra_regua_nao_viram_fase`) fixavam
«fora de T1 a cultura é sempre NAO SEI». Por ordem desta missão, passam a exigir: a cultura vem do
título (VEIO_DE), **nunca** da evidência da decisão; a FASE continua NAO SEI; texto sem cultura
continua NAO SEI.

## 3. O caderno de revisões escreve as chaves

`admissao/reprocessar_tempo_lugar.py` — as 2 mudanças pedidas:

1. `revisoes_de` acrescenta a revisão de `janela_declarada` (campo revisível da 033), com o JSON de
   chaves **ordenadas** — o mesmo código duas vezes dá o mesmo texto, e `rever()` não escreve de novo.
2. `ready_de` corre a régua de novo **só para ler a evidência de hoje** (sem ela, cultura e fase de T1
   dariam sempre NAO SEI). O resultado da linha continua **SIM** (quem entrou, entrou); o resultado da
   régua de hoje fica escrito na `BASE` da revisão («resultado de hoje: …; a admissão da linha não muda»).

## 4. Testes e mutação

| Prova | Resultado | Ficheiro |
|---|---|---|
| `tests/test_periodo_e_chaves.py` — 22 testes (período 7, região 5, cultura 6, caderno 4), exemplos reais salvo onde diz «sintético» | antes: 12 de 18 reprovam (5 FAIL + 7 ERROR; os 6 que passam são as guardas «não piora»); caderno: 3 de 4 reprovam · **depois: 22/22** | `data/derivados/PERIODO-E-CHAVES/testes-ANTES.txt`, `testes-caderno-ANTES.txt`, `testes-DEPOIS.txt` |
| Bateria leve (12 módulos: as chaves, a régua, LUGAR-FATO, tempo e lugar, rota do HTML, linhagem) | **286/286** | `…/testes-BATERIA-LEVE.txt` |
| Mutação deste ramo (P1–P4 período · R1–R4 região · C1–C5 cultura · K1–K3 caderno) | **16/16 mortos**, ficheiros repostos por sha256 | `…/mutacao.py.txt`, `…/mutacao-RESULTADO.txt` |
| Mutação do dono do LUGAR-FATO (`scripts/lugar_fato/mutar_fato_do_texto.py`) | **45/45** de novo (só mudam o sha do alvo e os tempos) | `scripts/lugar_fato/MUTACAO-FATO-DO-TEXTO-V1.json` |
| `tests.test_quatro_chaves_na_sala` com banco (Postgres descartável) | **NÃO corrido** — é pesado (LOCK-PESADO). A forma nova da JANELA foi conferida contra a trava `janela_declara_as_quatro_chaves` (VALOR não vazio + VEIO_DE + BASE): passa, por leitura | — |

## 5. A medida de novo (só leitura)

`data/derivados/PERIODO-E-CHAVES/medir.py.txt` → `MEDIDA.json` (a estrada da QUATRO-CHAVES-MEDIR, o
código deste ramo). Livro com o mesmo sha256 antes e depois.

| Classe | Sala: itens · cult · região · fase · período | Acervo: itens · cult · região · fase · período |
|---|---|---|
| T1 | — | 34 · 4 · 5 · 0 · 2 |
| T2 | 1 · 1 · 0 · 0 · 0 | 133 · 0 · 10 · 0 · 7 |
| T3 | 5 · 0 · 1 · 0 · 0 | 22 · 0 · 0 · 0 · 1 |
| T4 | — | 1 · 0 · 0 · 0 · 0 |
| T5 | 51 · 1 · 8 · 0 · 9 | 164 · 6 · 1 · 0 · 0 |
| T7 | 7 · 1 · 0 · 0 · 0 | 417 · 7 · 13 · 0 · 1 |
| T8 | — | 50 · 12 · 1 · 0 · 0 |
| T9 | 7 · 0 · 3 · 0 · 1 | 52 · 10 · 2 · 0 · 2 |
| T10 | 23 · 11 · 6 · 0 · 8 | 118 · 10 · 9 · 0 · 2 |
| T11 | — | 31 · 0 · 1 · 0 · 1 |
| T12 | — | 136 · 7 · 2 · 0 · 2 |

Período: 36 documentos (13 INTERVALO, 13 DIA, 9 ANO, 1 DIA+CALCULADA). O período só existe onde o
FACT_TIME existe e tem ano: 57 de 1.252 itens têm FACT_TIME.

### Os pares cruzáveis (NÃO cruzados)

Um documento conta uma vez por sha256 do bruto. Par = cultura em comum + região em comum + período
igual ou sobreposto.

| Documentos com cultura + região + período | Pares (período igual) | Pares (período sobreposto) | Entre fontes diferentes |
|---|---|---|---|
| 6 (4 páginas: 2 delas capturadas 2×) | 2 | 2 | **0** |

Os 2 pares são a mesma página duas vezes (ver «Resposta curta»). **Cruzamentos legítimos: 0.**

**O que ainda falta para haver cruzamento**, por ordem de peso:
1. **FACT_TIME com ano**: 57/1.252 itens têm tempo do facto; sem ele não há período.
2. **Região**: 62/1.252 — o LUGAR-FATO só aceita lugar preso a acontecimento, evento ou mercado.
3. **A mesma cultura noutra fonte**: das 70 culturas, 12 são de um só canal (IT-T8-006) e 12 da myfruit.
4. **Fase**: só T1 com SIM — 0 hoje.

## 6. Plano de instalação (para o coordenador — eu NÃO instalo)

> **D80 (v), coordenação 06:30:** NÃO gravar agora as 19 regiões da QUATRO-CHAVES-MEDIR. Primeiro este
> ramo corrige os 3 erros e prova o extrator (secções 2 e 4: os 3 erros dão NAO SEI; das 19, ficam 18;
> as 10 mudanças em 1.252 lidas uma a uma). Depois, gravar **SÓ por revisão append-only**
> (`sala_de_espera_revisao`, passo 4 abaixo) — **nunca** preencher as linhas antigas da Sala.
> Nada neste ramo escreve na Sala: `reprocessar_tempo_lugar.py` sem `--aplicar` só conta.

1. **Depois do LOTE 2** (`quatro-chaves-v2` + `conserto-regua-v1` no vivo). Juntar `periodo-chaves-v1`
   (merge `--no-ff`); conflito esperado só nos gerados do mapa (regerar pela cadeia).
2. **Banco: nada.** Nenhuma migração: `janela_declarada` e o caderno já existem (033).
3. Antes de ligar: a bateria leve acima (286) e, **com LOCK-PESADO**, `tests.test_quatro_chaves_na_sala`
   com banco (não corrida aqui).
4. **Reprocessar a Sala pelo caderno** (robô parado, backup antes, ensaio num descartável restaurado):
   `py admissao/reprocessar_tempo_lugar.py --livros "<livro>" --raizes "~/sintonia-sala-italia/armazem" --saida seco.json`
   (sem `--aplicar`). Esperado por esta medida, nas 94 linhas: **cultura 14 · região 18 · fase 0 ·
   período 18**. As 94 recebem uma revisão da janela: mesmo as que ficam NAO SEI passam de «não medido»
   a «medido, NAO SEI». Divergência = parar. Depois `--aplicar`, e outra vez `--aplicar` → `INSERIDAS: 0`.
5. **Desfazer:** nunca apagar revisões — uma revisão nova com `JANELA_NAO_MEDIDA` devolve a vista a
   «não medido», com o porquê.

## Ficheiros

| Ficheiro | O quê |
|---|---|
| `admissao/admissao.py` | `periodo_do_fato`, `CULTURA_SO_DA_CHAVE`, `_cultura_fora_da_regua`, `janela_declarada` |
| `leis/fato_do_texto.py` | `_e_pedaco_de_nome` (secção 4c) e a chamada em `_lugares` |
| `admissao/reprocessar_tempo_lugar.py` | as 2 mudanças do caderno |
| `tests/test_periodo_e_chaves.py`, `tests/test_quatro_chaves.py` | 22 testes novos; 2 antigos com a lei nova |
| `data/derivados/PERIODO-E-CHAVES/` | casos lidos à mão, testes antes/depois, mutação, medida, amostra das culturas |

Mapa: não regerado (PRONTO-SEM-MAPA).
