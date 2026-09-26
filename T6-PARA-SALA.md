# T6-PARA-SALA — o que as rodadas trouxeram, e o caminho mínimo até à Sala

- **Ramo:** `t6-para-sala-v1`, a partir de `pesquisadores-t6-v1` (`34713ccc`, que parte do vivo `69b0e23f`).
  **Nada instalado.** Sem rede nesta missão; a Sala real só foi lida.
- **Material:** as 3 rodadas que a coordenação correu às 10:20, 10:45 e 11:05 (VPN IT), em
  `sintonia-sala-italia/pesquisadores-t6/rede`. Trabalhei sobre uma **fotografia** dela, `foto-final/`,
  feita depois da rodada 3, com o sha256 dos 46 ficheiros em `FOTO-FINAL.sha256`.
- **Pedidos da rede** (só lidos): 3 rodadas × {OpenAlex 5, 5, 2 · Crossref 5, 5, 5 · ORCID 5, 5, 5}.
  - **42 pedidos no total, todos com resposta boa.** Nenhum domínio passou de 5 por rodada.

## 1 · A qualidade real (589 trabalhos, `data/derivados/T6-PARA-SALA/MEDIDA-QUALIDADE.json`)

**Os trabalhos e os repetidos:**

| O quê | Quantos |
|---|---|
| Encontros trabalho × consulta | 657 |
| **Trabalhos depois de tirar os repetidos (por DOI)** | **589**. 64 vieram em mais de uma consulta |
| Grupos «provavelmente a mesma obra» (mesmo título + autor em comum, DOI diferente) | 26 grupos, para rever. Nada foi apagado |
| Grupos «mesmo ensaio provado» (mesmo ID de ensaio ou de dataset) | 0 |

**Os campos de cada trabalho:**

| Campo | Trabalhos (de 589) |
|---|---|
| Com DOI | 586. **555 confirmados no Crossref** |
| Com autor de instituição italiana escrita **na obra** | 589, porque é o filtro da consulta |
| Com esse autor italiano **provado como pessoa** (pelo ORCID ou pelo depósito do editor) | **323** |
| Com o par cultura × problema **escrito no texto** | 534 |
| Cultura escrita · problema escrito | 561 · 546 |
| Local do estudo escrito | 112. Desses, 60 abaixo do país (região ou província) |
| Período do estudo escrito | 58 |
| **Cultura + problema + local + período** | **31 (5,3 %)** |
| Molécula nomeada | 88. Desses, 18 são do portfólio ADAMA |
| ID de ensaio · ID de dataset | 0 · 13 |
| Sem resumo no índice (só título) | 70 |

**As pessoas:**

| O quê | Quantas |
|---|---|
| Com afiliação italiana escrita numa obra | **1.466** |
| Com ORCID no índice | 1.165 |
| Com o par cultura × problema no texto de pelo menos um trabalho | 1.359 |
| Mesmo ORCID partido em mais de um ID do OpenAlex | 4 |

**A melhor prova de cada pessoa:**

| Prova | Pessoas |
|---|---|
| ORCID autodeclarado | 8 |
| ORCID depositado pelo editor e autenticado pela pessoa | 23 |
| ORCID depositado pelo editor | 568 |
| ORCID lido, mas sem este DOI | 6 |
| **Só o índice (não é prova)** | **861** |

**Por par** (declarado pelo OpenAlex → trazido → par escrito no texto → pessoas italianas):

| Par | Declarado | Trazido | Par no texto | Pessoas IT |
|---|---|---|---|---|
| vite × peronospora | 179 | 179 | 169 | 477 |
| vite × scafoideo | 109 | 109 | 102 | 280 |
| vite × botrite | 84 | 84 | 76 | 253 |
| vite × oidio | 81 | 81 | 67 | 228 |
| pomodoro × botrite | 78 | 78 | 74 | 298 |
| vite × tignoletta | 33 | 33 | 25 | 65 |
| mais × piralide | 25 | 25 | 21 | 33 |
| pomodoro × peronospora | 24 | 24 | 21 | 93 |
| melo × carpocapsa | 15 | 14 | 11 | 27 |
| mais × diabrotica | 14 | 14 | 12 | 30 |
| pomodoro × oidio | 11 | 11 | 10 | 28 |
| melo × oidio | 5 | 5 | 4 | 23 |

- Todas as consultas couberam numa página de 200. **Nenhuma ficou cortada.**
- Em melo × carpocapsa, o OpenAlex declarou 15 e trouxe 14 **trabalhos distintos**. A diferença é um repetido dentro da própria resposta.

## 2 · Os 30 pesquisadores italianos com MAIS EVIDÊNCIA por par (`POR-EVIDENCIA.json`)

⚠️ **Isto não é nota de importância.** O dono pediu «os mais úteis»; o que se mede aqui é a
**evidência contada**, e o critério foi escrito antes de ver a lista:
1. trabalhos do par, com o par **escrito no texto** e a pessoa **afiliada a Itália na própria obra**;
2. depois, os que têm o local do estudo escrito;
3. depois, os publicados desde 2023;
4. depois, o mais recente.

Cada pessoa aparece uma vez, no par onde tem mais evidência.

| # | Pesquisador | Instituição (a mais frequente, pelo índice) | Par | Trab. | c/ local | desde 2023 | último | prova |
|---|---|---|---|---|---|---|---|---|
| 1 | Cristina Marzachì | CNR-IPSP (Institute for Sustainable Plant Protection) | vite × scafoideo | 23 | 6 | 8 | 2026-05 | depósito editor |
| 2 | Silvia Laura Toffolatti | University of Milan | vite × peronospora | 22 | 2 | 6 | 2025-05 | depósito autenticado |
| 3 | Vittorio Rossi | Università Cattolica del Sacro Cuore | vite × peronospora | 18 | 1 | 7 | 2026-04 | depósito editor |
| 4 | Luciana Galetto | CNR-IPSP | vite × scafoideo | 15 | 3 | 7 | 2026-05 | depósito editor |
| 5 | Domenico Bosco | University of Turin | vite × scafoideo | 14 | 3 | 6 | 2026-01 | depósito editor |
| 6 | Giuliana Maddalena | University of Milan | vite × peronospora | 14 | 2 | 5 | 2025-05 | depósito editor |
| 7 | Michele Perazzolli | Fondazione Edmund Mach | vite × peronospora | 14 | 0 | 5 | 2026-07 | depósito autenticado |
| 8 | Mariangela Coppola | University of Naples Federico II | pomodoro × botrite | 13 | 0 | 1 | 2026-09 | **só índice** |
| 9 | Marika Rossi | CNR-IPSP | vite × scafoideo | 12 | 3 | 4 | 2026-05 | depósito editor |
| 10 | Tito Caffi | Università Cattolica del Sacro Cuore | vite × peronospora | 12 | 1 | 8 | 2026-04 | depósito editor |
| 11 | Donata Molisso | University of Naples Federico II | pomodoro × botrite | 12 | 0 | 1 | 2024-05 | **só índice** |
| 12 | Andrea Lucchi | University of Pisa | vite × tignoletta | 11 | 5 | 6 | 2025-10 | **só índice** |
| 13 | Giorgia Fedele | Università Cattolica del Sacro Cuore | vite × botrite | 11 | 1 | 4 | 2025-05 | depósito editor |
| 14 | Oscar Giovannini | Fondazione Edmund Mach | vite × peronospora | 10 | 1 | 6 | 2026-07 | depósito autenticado |
| 15 | Gabriella De Lorenzis | University of Milan | vite × peronospora | 10 | 1 | 5 | 2026-07 | depósito editor |
| 16 | Rosa Rao | University of Naples Federico II | pomodoro × botrite | 10 | 0 | 1 | 2024-05 | depósito editor |
| 17 | Federica Bove | Università Cattolica del Sacro Cuore | vite × peronospora | 10 | 0 | 0 | 2022-11 | depósito editor |
| 18 | Giovanni Benelli | University of Pisa | vite × tignoletta | 9 | 4 | 6 | 2025-10 | depósito editor |
| 19 | Matteo Ripamonti | CNR-IPSP | vite × scafoideo | 9 | 3 | 1 | 2024-09 | depósito editor |
| 20 | Simona Abbà | CNR-IPSP | vite × scafoideo | 9 | 1 | 4 | 2026-05 | depósito editor |
| 21 | Anna Maria Aprile | University of Naples Federico II | pomodoro × botrite | 9 | 0 | 1 | 2024-05 | **só índice** |
| 22 | Fabio Quaglino | University of Milan | vite × scafoideo | 8 | 7 | 7 | 2026-08 | depósito editor |
| 23 | Renato Ricciardi | University of Pisa | vite × tignoletta | 8 | 3 | 5 | 2025-10 | depósito editor |
| 24 | P.A. Bianco | University of Milan | vite × peronospora | 8 | 1 | 2 | 2024-02 | depósito editor |
| 25 | O. Failla | University of Milan | vite × peronospora | 8 | 0 | 4 | 2025-02 | depósito editor |
| 26 | Ilaria Di Lelio | University of Naples Federico II | pomodoro × botrite | 8 | 0 | 1 | 2026-09 | depósito editor |
| 27 | Claudio Moser | Fondazione Edmund Mach | vite × peronospora | 8 | 0 | 1 | 2023-08 | depósito editor |
| 28 | Martina Buonanno | Institute of Biostructure and Bioimaging (CNR) | pomodoro × botrite | 7 | 0 | 2 | 2026-09 | depósito editor |
| 29 | Simona Maria Monti | Institute of Biostructure and Bioimaging (CNR) | pomodoro × botrite | 7 | 0 | 2 | 2026-09 | depósito editor |
| 30 | Francesco Pennacchio | University of Naples Federico II | pomodoro × botrite | 7 | 0 | 0 | 2022-06 | depósito editor |

**Grupos (instituição declarada nas obras do par, as 3 com mais trabalhos):**

| Par | Grupos |
|---|---|
| vite × peronospora | Fondazione Edmund Mach (38) · University of Milan (30) · «Cereal Research Centre» (25)* |
| vite × scafoideo | University of Turin (27) · CNR-IPSP (25) · University of Padua (14) |
| vite × botrite | University of Padua (15) · Università Cattolica (12) · «Cereal Research Centre» (11)* |
| vite × oidio | Fondazione Edmund Mach (18) · «Cereal Research Centre» (9)* · Università Cattolica (8) |
| vite × tignoletta | University of Pisa (11) · Fondazione Edmund Mach (5) · University of Udine (4) |
| pomodoro × botrite | University of Naples Federico II (21) · CNR (17) · Sapienza (13) |
| pomodoro × oidio | University of Turin (6) · INRiM (5) · CNR-IPSP (4) |
| pomodoro × peronospora | University of Turin (4) · CREA Cereali e Colture Industriali (4) · University of Milan (2) |
| melo × carpocapsa | Free University of Bozen-Bolzano (4) · University of Trento (3) · University of Padua (3) |
| melo × oidio | FEM (1) · Laimburg (1) · University of Udine (1) |
| mais × piralide | FAO (4) · Scuola Superiore Sant'Anna (4) · University of Bologna (4) |
| mais × diabrotica | University of Milan (4) · University of Bologna (3) · Centro Agricoltura Ambiente (2) |

**O que esta lista NÃO prova, medido:**
- **A instituição é a do ÍNDICE, e o índice erra.** Exemplos: «Bitron (Italy)», uma empresa, aparece para
  Domenico Bosco (Turim); «Federico II University Hospital» aparece no lugar da Universidade de Nápoles;
  e o \* «Cereal Research Centre» em trabalhos de videira é quase certamente um centro do CREA com o nome
  errado. Conferir antes de usar.
- **4 dos 30 têm só a prova do índice** (Coppola, Molisso, Lucchi, Aprile). Não se sabe se o ORCID é deles.
- **A lista mede os 12 pares do casco, e nada fora deles.** Os nomes do dono que trabalham noutros insetos
  (*Drosophila suzukii*, *Tuta absoluta*) ficam de fora por construção. É a Consulta 2 (§5).
- Nomes do dono que **aparecem** nos 589: Rossi, Caffi, Fedele, Salotti, Anfora, Ioriatti.
- **Não aparecem:** Grassi, Tonina, Zappalà e Antonio Biondi. O único «Biondi» é Lorenzo, da Marconi University.
  E **Daniele** Bosco também não aparece; aparece **Domenico** Bosco, de Turim.

## 3 · Os extractores v2: local, período e molécula (pedido da coordenação 11:08)

`ANTES-DEPOIS-EXTRATORES.json`: as mesmas 589 respostas, com o antes = `5db3be6f` e o depois = `t6-v2`.

| Campo | Antes | Depois | Ganhou | Perdeu |
|---|---|---|---|---|
| Local do estudo escrito | 112 | 112 | 0 | 0 |
| … abaixo do país | 54 | **60** | — | — |
| Período do estudo | 41 | **58** | 17 | 0 |
| Molécula | 13 | **88** | 75 | 0 |
| Cultura + problema + local + período | 24 | **31** | — | — |

**O que mudou:**
- **Local:**
  - lê também as **províncias** (o gazetteer do piloto, `leis/fato_local.PROVINCIAS`, 85, com o nome inglês de 11) e as **zonas** («northern / central / southern Italy»);
  - um nome logo depois de «University of / Istituto di» **não conta**, porque é afiliação.
  - **Não ganhou nenhum trabalho novo**: os resumos que nomeiam um lugar já nomeavam a Itália. Ganhou precisão (54 → 60 abaixo do país).
- **Período:**
  - novas âncoras: «2021 and 2022 growing seasons», «2019/2020 season», «vintage», «seasons 2019–2020», e um intervalo entre parênteses «(2018–2020)» (um ano sozinho entre parênteses é citação);
  - um ano **depois** da publicação cai;
  - a década continua a não contar.
- **Molécula:**
  - o léxico passou de 122 nomes (só ADAMA) para **835 nomes** do registo italiano de produtos fitossanitários (`PROD_FTS_6_20260907.csv`, Ministero della Salute, todas as empresas, autorizados e revogados);
  - o nome entre parênteses vira sinónimo; os microrganismos são cortados no «strain/ceppo»;
  - +«sulfur/zolfo», +«copper/rame» (família);
  - fora, declarados um a um:
    - coformulantes e palavras genéricas;
    - «carbon dioxide», a levedura do vinho e o ácido giberélico;
    - «X sp.» sem espécie;
    - «sulfur dioxide» (o SO₂ do vinho);
    - «copper content/levels» (cobre medido no solo).

**Lido à mão: as 20 primeiras mudanças por DOI (amostra pela ordem, não pelo resultado).**
- 18 certas.
- 2 duvidosas: geraniol num artigo sobre linalol; o período «(2019–2021)» numa revisão.
- ⚠️ **«Molécula» quer dizer NOMEADA no resumo, e não TESTADA.** Em 34 trabalhos a molécula é «copper».
  Muitos citam o cobre como referência a reduzir ou a substituir.

**O «resumo/método» da coordenação:** o registo do OpenAlex traz **só título e resumo**. A secção de
métodos não vem, e 70 trabalhos nem resumo têm. Ler os métodos exige o texto integral, e isso é outra
rota (o editor e o acesso aberto), com rede.

## 4 · Modelo/DSS, condição → risco, resistência (pedido da coordenação 12:00)

Nos 589, `MODELOS-E-RESISTENCIA.json`. **Só medida; nenhum campo novo no contrato.**

| Classe | Trabalhos | Lido à mão |
|---|---|---|
| **DSS ou modelo de risco nomeado** («decision support system», «forecasting / infection / phenological / weather-driven model», «early warning») | **25** | ~8 em 10 certos |
| Só «model / modelling» solto (pode ser modelo molecular) | 76 | não conta |
| **Condição → risco**: uma variável (temperatura, humidade, molhamento, chuva, graus-dia, fenologia, BBCH), uma resposta (infeção, risco, incidência, voo, geração) e uma relação (favorece, limiar, depende, associado), **na mesma frase** | **8** | ~7 em 8 |
| … o mesmo, com as três espalhadas no texto inteiro | 38 | ~6 em 10 (frases de contexto) |
| **DSS ou condição → risco** | **31** | |
| **Fala de resistência a produto** («fungicide resistance», «sensitivity to fungicides», «resistant to X») | **18** | ~5 em 10 são SOBRE resistência; os outros só a citam |
| Resistência da planta (cultivar, genes Rpv/Ren): outra pergunta, não se soma | 67 | |

- A v1 da resistência dava 69, com **1 em 10** certo: era resistência da planta ou resistência induzida.
- A condição → risco é **o texto dizer que o trabalho trata da relação**. Não é o risco (secção 9 do alinhamento).

## 5 · A CONSULTA 2 (tu corres na rede): os nomes do dono que deram 0

`coleta/pesquisadores_t6.py --rede2`. Vai pela **pessoa**, não pelo par, e por isso alarga-se sozinha à
entomologia e a outras culturas.

| Nome pedido | Instituição que tem de bater |
|---|---|
| Alberto Grassi | Fondazione Edmund Mach |
| Lorenzo Tonina | Fondazione Edmund Mach |
| Lucia Zappalà | Catania |
| Antonio Biondi | Catania |
| Daniele Bosco | Turim/Torino (⚠️ escrito como o dono escreveu; nos 589 existe **Domenico** Bosco, Turim) |

**Rodada 1:** `/authors?search=<nome>` com afiliação italiana. **5 pedidos ao OpenAlex.**
- O nome tem de bater (a inicial do primeiro nome vale) **e** a instituição também.
- 1 ID → RESOLVIDO.
- Vários → **AMBÍGUO**, com todos os IDs. Nada se funde.
- 0 → NÃO ENCONTRADO, que não é «não existe».

**Rodada 2:**
- as obras desde 2019 dos resolvidos e ambíguos (≤ 5 ao OpenAlex);
- o `/works` do ORCID de cada candidato (≤ 5);
- o Crossref dos DOI (≤ 5).

**Medida (`--medir2`, sem rede):** por pessoa:
- o estado da identidade;
- as obras;
- quantas têm um par do casco no texto;
- os organismos e culturas do alargamento, **só no título**: *D. suzukii, Tuta absoluta, H. halys, P. japonica, B. oleae, C. capitata, P. ficus, P. spumarius, Xylella, Cacopsylla*; pequenos frutos, cereja, oliveira, citrinos, pêssego, kiwi, avelã, pera, batata.

```
cd <clone do ramo t6-para-sala-v1>
py coleta/pesquisadores_t6.py --rede2 --rodada=1 --saida=C:/Users/London1/sintonia-sala-italia/pesquisadores-t6/consulta2
py coleta/pesquisadores_t6.py --rede2 --rodada=2 --saida=C:/Users/London1/sintonia-sala-italia/pesquisadores-t6/consulta2
```

- Teste com transporte falso (`tests/test_t6_para_sala.py::Consulta2`):
  - homónimo noutra casa → fora;
  - «L. Zappala» + «Lucia Zappalà» em Catania → AMBÍGUO com os 2;
  - instituição errada → NÃO ENCONTRADO;
  - teto 5 por domínio.

## 6 · Os degraus até à Sala, com o MÍNIMO de mudança

**O desenho** (ensaiado, §6.1 e §6.2):
- **A fonte já existe:** `EU-T5-001 · OpenAlex`, que o Atlas declara «T5 e T6». Não se cunha uma fonte por
  pessoa para os trabalhos passarem.
- **A unidade é o TRABALHO (DOI).** Os pesquisadores e a prova de cada um viajam **dentro** dele (campo `T6`).

**O que muda no código:**
1. `coleta/pesquisadores_t6_executor.py`, **NOVO**.
   - Declara as rodadas **já guardadas** como COLHEITA, no contrato de retorno (COL-LAW-505).
   - **Sem rede.**
   - O bruto de cada trabalho é o registo tal como veio na página, serializado de forma canónica. A página inteira fica, e `ORIGEM_DO_REGISTO` guarda o sha256 dela e a posição.
   - `FACT_TIME` e `FACT_LOCATION` ficam NÃO SEI. O local e o período escritos vão em `T6`, como candidatos.
2. `pedido/receitas.py`: a receita **T6 ganha o executor à frente**. O `corpus-pesquisador` fica atrás. A ordem é decisão do dono.
3. As duas guardas das receitas passam a declarar isto: `PEDEM_A_CORRIDA` e a fotografia de T6.

**O que NÃO muda:**
- a Admissão;
- a Sala e o esquema do banco;
- os contratos;
- o QUALIFY (a regra ORCID → T6 do ramo anterior continua lá, e é para a **identidade** das pessoas, não para os trabalhos);
- a derivação: não se aplica ao JSON; o orquestrador leva à Admissão o item da entrada, com o texto que a fonte publicou.

### 6.1 · Ensaio numa cópia do vivo (árvore `69b0e23f` + este ramo), Sala em ficheiro, sem Postgres

`provas/o_pedido_t6_atravessa.py` aperta **o botão canónico** (`orquestrador.correr`). Não chama a porta à mão.

| Universo do pedido | Colheita | RAW guardado | Admissão SIM / NÃO SEI / NÃO | Na Sala |
|---|---|---|---|---|
| **T5** (régua de ciência que já existe) | 589 | 589 | **100 / 332 / 157** | **100** |
| **T6** | 589 | 589 | 0 SIM · **589 NÃO SE APLICA** («não há regra escrita do que conta como T6») | **0** |

**Porque não entram mais pela régua T5:**
- «study» sozinho é **uma** palavra, e a régua pede duas.
- 157 NÃO: a régua vê o texto como de doença (T3: disease, pathogen, downy mildew) e **nenhuma** palavra de ciência.
- **Variante B:** se o texto levasse a linha do DOI do próprio registo, seriam **345 SIM / 244 NÃO SEI / 0 NÃO**. Medido chamando a régua diretamente, **não** pela estrada. Isto dá à palavra «doi» o valor de uma prova de ciência. É decisão do dono, não padrão.
- **Dos 100 SIM:**
  - 97 com o par escrito;
  - 26 com local escrito;
  - 13 com período;
  - 24 com molécula.

### 6.2 · Ensaio numa cópia da Sala (Postgres descartável, LOCK-PESADO)

**NÃO MEDIDO. A LOCK-PESADO nunca ficou livre para mim.**
- das 10:42 às 13:34 esteve com 5 missões seguidas: REPROC-EXTRATORES, DEDUP-INSTALAR, NUVEM-CONCORRENZA,
  ACERVO-PARA-SALA-2 (11:58–13:27) e INTEGRA-NOITE-LOTE2 (13:27, mapa);
- às 11:40 houve ainda uma trava de 0 bytes, que outra sessão tratou como órfã;
- não forcei nenhuma trava e não corri nada pesado.

**O ensaio está pronto e testado até ao ponto em que o banco entra:**
- o programa `provas/ensaio_t6_na_copia_da_sala.py`;
- o ambiente, uma cópia destacada deste ramo em `%TEMP%/t6-sonda` (`b8b43909`), com as 42 respostas da
  foto final em `data/colheita/pesquisadores-t6/rodadas`.

**O que ele faz:**
- a cópia da Sala real só com leitura (o mesmo `pg_dump` do `backup_sala.cmd`), fotografada antes e depois;
- um Postgres descartável `sala_italia` numa porta livre;
- **duas** passagens do botão canónico com a Sala em POSTGRES: a 1.ª mede quantos entram; a 2.ª que
  **não entram outra vez** (idempotência por documento);
- as contas por SQL na cópia, antes e depois: Sala total, T5, T6, a fonte `EU-T5-001`, `raw_asset` e as corridas;
- no fim desce o banco e apaga o cluster.

**Para correr** (com a LOCK-PESADO na mão e ≥ 5 GB livres):

```
cd %TEMP%\t6-sonda
py provas/ensaio_t6_na_copia_da_sala.py --saida=C:/Users/London1/sintonia-sala-italia/pesquisadores-t6/ensaio-copia-sala --universo=T5
```

**O que se espera, sem ter sido medido:**
- **100 linhas novas na Sala na 1.ª passagem e 0 na 2.ª.** São os 100 SIM do §6.1, e a Sala real
  não tem nenhum item da fonte `EU-T5-001`.
- **Há três riscos que só o banco responde:**
  - uma regra (CHECK) do esquema recusar a fonte com prefixo `EU-` na `sala_de_espera` (o coletor web só aceita `IT-`, D80);
  - o `raw_asset` recusar o tipo `application/json`;
  - a trava de identidade por documento tratar os 589 como novos.

## 7 · A decisão que falta ao dono (1 frase)

**Os trabalhos dos pesquisadores entram na Sala como T5, pela régua de ciência que já existe (100 dos
589 hoje), ou o dono quer um universo T6 com régua própria (sem ela entram 0)? E, nos dois casos,
autoriza pôr o executor `pesquisadores-t6` à frente na receita T6?**

(A variante «o DOI conta como palavra de ciência», com 345 SIM, é uma terceira resposta possível. Mexe na
régua, e por isso não vai como padrão.)

## Limites

1. **O período e o local vêm só do resumo.** O registo não traz os métodos.
2. **Molécula = nomeada, não testada.** Ninguém leu o artigo para saber se foi aplicada.
3. **A instituição é a do índice e erra** (Bitron, Hospital, «Cereal Research Centre» em videira).
4. **A lista dos 30 mede evidência nos 12 pares; não mede importância.** 861 das 1.466 pessoas só têm a prova do índice.
5. **A Consulta 2 não foi corrida** (rede). Só está ensaiada com transporte falso.
6. **O ensaio na cópia da Sala (Postgres) NÃO foi medido** — LOCK-PESADO ocupada toda a janela (§6.2).
7. **Mapa não corrido** (PRONTO-SEM-MAPA).
