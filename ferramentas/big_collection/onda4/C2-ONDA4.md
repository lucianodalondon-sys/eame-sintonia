# C2-ONDA4 — o C2 da 3.ª onda (causa, conserto, teste) e o plano da 4.ª onda

Missão C2-E-ONDA4-PREP (coordenador, 25/09 23:50). Ramo `c2-juiz-v1`, nascido do vivo `ce28040c` e já junto com o vivo novo `83de0ccd` (C9 instalado, 26/09 02:08): conflito só no `.gitattributes` (as duas linhas ficam). Na base nova: teste C2 14/14, C9 9/9, mutação 9/9; `test_micro_coleta_instrumento` (2) e `test_gate_de_aceitacao_tematica` (1) falham igual em `83de0ccd` puro.
Sem rede, sem coleta, sem escrita na Sala nem no vivo, nada instalado. Sala lida com
`default_transaction_read_only=on`. Medido em 26/09/2026, 00:00–01:30 (-03).

---

## 1. C2: defeito do JUIZ, não só do relatório

**Decisão: é defeito do juiz de página (regra operacional).** O relatório só repete o que o juiz diz.

O juiz é `curadoria/retrato_html.py` (gêmeo Node `coleta/retrato_html.mjs`). Ele é a pergunta
`materia` da Admissão (`admissao/admissao.py::_e_materia`, versões 6/7): CAPA → `NAO` ou quarentena;
MATÉRIA → segue para a Sala. O C2 do relatório (`micro_coleta.py`) chama o mesmo juiz.

Prova (3.ª onda, 75 HTML; leitura humana em `FECHO-ONDA3.md`, secção 6):

| raw | fonte | juiz (formato) | leitura humana | efeito na Sala |
|---|---|---|---|---|
| 1495, 1501, 1502, 1515, 1523, 1558 | T12-024, T12-129 ×2, T2-146, T7-017, T9-009 | CAPA (`NAVIGATION`) | **matéria** | 6 notícias barradas (nenhuma na Sala) |
| 1533 | IT-T7-048 | CAPA | capa («Chi siamo») | barrada — certo |
| **1520** | **IT-T5-186** | **MATÉRIA (`CONTENT`)** | **lista de eventos** | **entrou** (`derived:1022`, data de um evento e lugar de outro) |

O juiz mede só a FORMA (caracteres, parágrafos, ligações da página inteira): lê notícia curta com
menu grande como capa, e lista com muito texto como matéria. O erro que chegou à Sala (1520) é
operacional. Se fosse só o relatório, a Sala estaria limpa, e não está.

### O conserto: V2 «lista com leia mais»

- **Regra:** matéria com **≥ 6** chamadas «leia mais» (`leggi tutto`, `leggi di più`,
  `continua a leggere`, `read more`, `scopri di più`) passa a CAPA. Só aperta: nunca solta uma capa.
- **Onde:** `retrato_html.py` (nova medida `READ_MORE_LINKS` + `regra_e_veredito`, a V1 continua
  antes) e o gêmeo `retrato_html.mjs` (fronteira Unicode: o `\b` do JavaScript não conta «ù» como
  letra). A Admissão diz a regra no motivo («V2: página de lista…»). O C2 do relatório passa a usar o
  mesmo veredito da Admissão (antes lia só o formato e não via a lista).
- **Medido antes de escolher** (gabarito humano `GABARITO-CAPA-V1`, 146 páginas, bytes em
  `~/detector-capa-gabarito`):

  | juiz | capas que atravessam | matérias barradas |
  |---|---|---|
  | atual | 63 | 6 |
  | **V2 (≥ 6 leia mais)** | **58** | **7** |
  | regra de data (salvar notícia curta) | 74 | 4 |

  A regra de data foi **recusada**: deixava passar 11 capas a mais para salvar 2 notícias.
- **Limite conhecido (NÃO consertado):** as 6 notícias curtas continuam barradas pelo formato.
  Saída que já existe: uma pessoa registra `MATERIA` na quarentena humana (D11), pelo sha da página.
- **Margem:** o limiar 6 separa 10 (a lista ENEA) de 4 (a notícia com mais «leia mais» na onda). É um
  exemplo só, declarado.

### Teste e mutação

- `tests/test_c2_juiz.py`: **14/14**. Os 8 casos reais (os 7 de `CAPAS-A-CONFIRMAR.tsv` + a lista
  ENEA) estão em `tests/dados/c2-juiz/`, com `-text` no `.gitattributes`. Os bytes batem com o sha256
  do `raw_asset` da Sala. Cobre V2, limiar exato, V1 antes de V2, mensagem do gate, Admissão
  (1520 → `NAO` pela V2; 1533 continua `NAO`) e paridade Python = Node nos 8.
- Paridade em 221 páginas reais (146 do gabarito + 75 da onda): `READ_MORE_LINKS`, `CAPA_OU_MATERIA`
  e veredito iguais. As 2 diferenças de `TEXT_SHA256` (IT-T2-049, IT-T12-044 do gabarito) **já
  existiam** em `ce28040c`: defeito antigo, fora desta missão.
- **Mutação** (`provas/c2_juiz_mutacao.py`, cópia por `git archive`): **9/9 mortos**
  (`provas/C2-JUIZ-MUTACAO.json`): V2 desligada, limiar 11, sem «leggi tutto», veredito ignora V2,
  V2 aperta NAO_SEI, Node limiar 11, Node fronteira ASCII, Node ignora V2, Admissão perde a V2.
- **Testes vizinhos:** 9 ficheiros do juiz (104 testes) iguais antes e depois. 43 ficheiros que
  importam a Admissão ou o relatório: os mesmos resultados de `ce28040c` (os vermelhos são os de
  base). Os dois guardas «admissão não mudou por commitar» voltaram ao estado de base depois do commit.
- **Relatório da 3.ª onda com o novo juiz** (cópia, Sala só leitura): `CAPAS_DO_JUIZ` passa de 7 para
  **8** (entra o 1520). C2 continua `PENDENTE_HUMANO`, porque as 6 notícias ainda estão marcadas.

### O que fica para o coordenador

1. **`VERSAO_DA_REGRA` da Admissão NÃO subiu** (continua `9`). A lei do ficheiro pede que suba. Mas
   subir reprova `test_regua_t1`/`test_regua_t2`, que prendem as medições T1/T2 à versão 9. Decisão:
   subir e remedir, ou aceitar sem subir.
2. O `derived:1022` que já está na Sala **não sai** (a Sala não apaga). O replay da porta
   (`orquestrador --so-a-porta`) julgaria o bruto de novo com a V2.
3. **C2 = PASS** só com a leitura humana das 6 notícias (registo na quarentena humana) ou com uma
   regra nova que as salve sem soltar capas. Hoje: **C2 fica FAIL/PENDENTE**, e agora por razões
   documentadas.

---

## 2. Plano da 4.ª onda (só plano, sem rede, numa cópia)

Cópia `onda4-plano-copia` (destacada em `ce28040c`), com os 16 livros vivos copiados só por leitura
(lista e sha256 em `auditoria-madrugada\C2-ONDA4\LIVROS-COPIADOS-DO-VIVO.txt`). Fila do robô
esvaziada **na cópia** (4482 tarefas, D41.3). Proxy morto. Saídas em `auditoria-madrugada\C2-ONDA4\`.

### O que o plano mede hoje

- `micro_coleta.py plano`: **65 PRONTAS**, 18 bloqueadas (9 sem contrato de coleta, 7 T1 sem receita
  web, 1 T11 sem receita, 1 `CAPABILITY_BLOCK`). A missão falava em 61; o número de agora é 65.
- Coorte provisória (`coorte_unica.py`, **não congelada**): **64** — é **a mesma lista da 3.ª onda**
  (0 entram, 0 saem). A PRONTA de fora é IT-T5-090 (ISTAT, D45).
- `onda_web.py --so-plano --historico=<onda2>,<onda3>` numa só onda: correm 39, saltam 25 por
  `TETO_DOMINIO` + 1 parcial. **PODE_CORRER = false** (coorte `PROVISORIA`).

Conclusão: **as 26 barradas da 3.ª onda são as que ficam de fora**. Não há fonte nova na coorte, e
«as prontas do plano» são as mesmas 64.

### Rodadas para caber no teto (5 pedidos por domínio por onda)

Cada rodada é uma onda própria (`--fontes=` / `--lote=`, livro do teto novo por pasta). Ordem justa
do `onda_web` dentro de cada domínio. Pedidos previstos = o máximo medido na 2.ª/3.ª onda; sem
medida, o teto inteiro (5).

| rodada | fontes | pedidos previstos | domínios |
|---|---|---|---|
| 1 | 38 (uma por domínio) | 174 | 38, máx. 5 |
| 2 | 6: IT-T3-023, IT-T2-006, IT-T2-146, IT-T5-111, IT-T5-185, IT-T7-123 | 28 | edagricole, arpacampania, arpa.veneto, crea, enea, cia |
| 3 | 4: IT-T8-021, IT-T5-113, IT-T5-186, IT-T7-135 | 19 | edagricole, crea, enea, cia |
| 4 | 3: IT-T8-022, IT-T5-167, IT-T7-112 | 15 | edagricole, crea, cia |
| 5 | 3: IT-T8-024, IT-T5-056, IT-T7-118 | 15 | edagricole, crea, cia |
| 6–15 | 1 cada: IT-T8-028, -029, -030, -034, -039, -040, -041, -042, -051, IT-T12-130 | 5 cada | só edagricole.it |

**Total: 15 rodadas, 64 fontes, 301 pedidos previstos**, nunca mais de 5 por domínio numa rodada.
Detalhe por domínio em `auditoria-madrugada\C2-ONDA4\rodadas.txt`.

⚠️ **edagricole.it é o gargalo:** 15 fontes no mesmo domínio = 15 rodadas (uma em cada). Correr as 15 rodadas em
seguida seria 75 pedidos ao mesmo site no mesmo dia, o que contorna a intenção do D38. E não é só
ele: as rodadas 1 a 5 levam, cada uma, edagricole.it, crea.gov.it e cia.it, e juntas no mesmo dia
somam 25 pedidos a cada um desses três. **Proposta:** 1 rodada por dia (15 dias), ou, se o dono
aceitar mais de 5 por dia por domínio, um teto diário declarado (por exemplo 10). O espaçamento é
decisão do dono; o código de hoje não o impõe (o livro do teto é por onda, não por dia).

### O que precisa estar instalado antes

1. ~~`c9-idioma-v1`~~ **já instalado** (vivo `83de0ccd`, 26/09 02:08): o relatório de onda pede-se com `--estado=<ONDA-WEB-ESTADO.json>`.
2. **`c2-juiz-v1`** (este ramo), se o coordenador aceitar a V2 e decidir a versão da Admissão (ponto 1 acima).
3. **Coorte congelada** no ramo do vivo (`--congelar --instalacao=<commit> --demotion=<B5>`); hoje é provisória.
4. Um disparador de rodadas: hoje o `onda_web` corre uma onda por vez. As 15 rodadas são 15
   comandos `--correr --fontes=...` com pastas novas. Não há agendador de rodadas.

---

## EM PALAVRAS SIMPLES

- **O problema do C2 estava no juiz**, a parte que decide se uma página é notícia ou lista. Ele olha
  só o «formato» da página, como quem julga um livro pela capa. Por isso deixou entrar uma lista de
  eventos da ENEA, como se fosse uma notícia, e barrou 6 notícias curtas de sites com menu grande.
- **O conserto:** se a página tem 6 ou mais botões «leia mais», é uma lista, não uma notícia. Testei
  em 146 páginas que uma pessoa já tinha classificado: passam 5 listas a menos, e 1 notícia a mais fica
  presa. Nas 8 páginas da 3.ª onda, a lista da ENEA agora é pega.
- **O que NÃO consertei:** as 6 notícias curtas continuam presas. A regra que as salvaria deixava
  passar 11 listas. Por isso é melhor uma pessoa liberar essas 6 à mão.
- **A 4.ª onda:** as fontes prontas hoje são as mesmas 64 da 3.ª onda. Para visitar todas sem passar
  de 5 visitas por site, são 15 rodadas. A primeira pega 38 fontes de uma vez. As últimas 10 são só do
  site edagricole.it, que tem 15 fontes. Proponho espaçar essas rodadas por dias, para não visitar o
  mesmo site 75 vezes no mesmo dia.
- Nada foi instalado. Nada foi coletado. A Sala só foi lida.
