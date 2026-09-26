# RELATÓRIO — ROTULOS-T4 (ramo `nuvem-rotulos-t4-v1`)

**Data:** 2026-09-26 · **Base:** produção `69b0e23f` · **Missão:** `C:/nuvem/prompts/nuvem-rotulos-t4-v1.txt`

Alimenta Portafoglio e Label Intelligence (Bíblia § 34, `CAP-PORT` e `CAP-LABEL`):
a chave produto × cultura × alvo, com dose, época, restrição e versão do documento.

---

## 1. O que já existia (medido antes de escrever)

| o quê | onde | número |
|---|---|---|
| registo oficial do Ministero (CSV `PROD_FTS_6`) | `data/samples/IT-SOURCE-SAMPLES/IT-T4-001/PROD_FTS_6_20260907.csv` | 17.695 produtos; 602 de titular ADAMA; **163 vivos** |
| manifesto dos rótulos baixados em 02/09 | `data/raw/IT-ROTULOS/_MANIFESTO.json` | 163 itens, 163 `OK` |
| os PDFs desses rótulos | **fora do Git** (`data/raw/*` no `.gitignore`); existem em `C:/eame-sintonia/data/raw/IT-ROTULOS/` | 163/163 com o sha256 do manifesto (conferido hoje), 33 MB |
| leitor antigo de pares cultura × alvo | `coleta/rotulos_ler.py` → `IT-ROTULOS-PARES.json` | 2.030 pares, 102/163 produtos; **sem** dose, época, restrição, estados |
| leitor geométrico de doses | `data/samples/IT-DOSE-ROTULO/IT-DOSES-2026-09-06.json` | 839 linhas em 21 rótulos (o cabeçalho diz 848 linhas e 23 rótulos — **9 linhas e 2 rótulos não batem**, não investigado) |
| referência ADAMA | `referencia/adama/AUTHORIZED-USES.json` | 2.030 registos = os mesmos pares |
| portal | `italia-portale/client/italy-label-intelligence.js` (3,8 MB de dados embutidos) | não consome nenhum parser; `MATERIAL ≠ FERRAMENTA` |

## 2. O que fiz

**O parser canónico** — `coleta/rotulo_t4_it.py` (703 linhas). Lê um rótulo **já
guardado** (PDF, HTML ou texto) e a linha do registo oficial, e devolve linhas de uso
com: `PRODUCT_ID · NUMERO_REGISTO · TITULAR · PRINCIPIOS_ATIVOS · FORMULACAO ·
VERSAO_DO_DOCUMENTO (sha256 + data do decreto + validade do rótulo) · CULTURA · ALVO ·
DOSE · EPOCA · RESTRICOES · MAX_APLICACOES · INTERVALO_ENTRE_APLICACOES ·
INTERVALO_DE_SEGURANCA · VALIDADE_DA_AUTORIZACAO · AUTORIZACAO_NACIONAL_VIVA`.
Cada campo leva o **seu** estado e a sua fonte.

| ponto | ficheiro:linha |
|---|---|
| vocabulário fechado de 4 estados; `NAO_AUTORIZADO` é recusado | `coleta/rotulo_t4_it.py:82`, `:91` |
| afirmação proibida («não provado ≠ não autorizado») | `coleta/rotulo_t4_it.py:84` |
| «vivo» é o que o Ministero escreve em `stato_amministrativo` | `coleta/rotulo_t4_it.py:116` |
| ficha do registo (titular, substâncias com teor, formulação, validade) | `coleta/rotulo_t4_it.py:131` |
| PDF: pypdf primeiro (o `-layout` põe o alvo uma linha acima da cultura) | `coleta/rotulo_t4_it.py:181` |
| número de registo nas 4 formas reais; número solto sem «Ministero» não conta | `coleta/rotulo_t4_it.py:292` |
| volume de água não é dose | `coleta/rotulo_t4_it.py:398` |
| sem unidade na linha: só com UM número candidato; senão `NAO_CONHECIDO` | `coleta/rotulo_t4_it.py:439` |
| bloco sem cabeçalho acaba no próximo título, conhecido ou não | `coleta/rotulo_t4_it.py:522`, `:542` |
| rótulo de outro registo → `ERRO` e zero linhas | `coleta/rotulo_t4_it.py:615` |
| `VERIFICADO` só para linha de tabela de rótulo conferido | `coleta/rotulo_t4_it.py:634` |
| aprovação UE em campo separado, nunca escreve na autorização nacional | `coleta/rotulo_t4_it.py:659` |

**Contrato de fonte e plano de coleta** — `docs/operacao/CONTRATO-FONTE-IT-T4-ROTULO.md`.
Não criei SOURCE_ID novo: o rótulo é documento do `IT-T4-001` (Bíblia § 28).

**Provas** — `provas/medir_rotulo_t4_nos_163.py` (mede os 163 reais, confere sha256
antes de ler) → `medidas/ROTULO-T4-MEDIDA-163.json`;
`provas/amostra_doses_rotulo_t4.py` (sorteio reprodutível) →
`medidas/ROTULO-T4-AMOSTRA-DOSES-S20260926.txt`.

**Mapa** — ficheiros novos declarados na peça `C-ROTULOS`
(`system-map/data/architecture.declared.json`).

## 3. Resultado nos 163 rótulos reais

| degrau | resultado |
|---|---|
| PDF conferido pelo sha256 | 163 / 163 |
| número do rótulo = registo oficial (`VERIFICADO`) | 144 / 163 · **0 conflitos** · 19 não escrevem o número de forma legível |
| titular do registo escrito no rótulo (`VERIFICADO`) | 135 / 163 |
| data do decreto lida | 140 / 163 · validade «dal … al …» 117 / 163 |
| rótulos com alguma linha de uso | 69 / 163 (94 saem `NAO_CONHECIDO`, com a afirmação proibida) |
| linhas de uso | 1.284 (790 de tabela, 70 de bloco com título, 424 de bloco sem título) |
| linhas com dose | 564, em 45 rótulos |

**Precisão da dose**, duas réguas:

- contra o leitor geométrico, nas frases reais de 493 linhas com UMA unidade de dose:
  quando o parser dá dose, é a mesma **54 / 54**; nas outras 439 cala-se. Cobertura
  baixa (11%) e precisão alta — de propósito.
- amostra lida à mão, 25 doses sorteadas nos 163 PDFs (semente `20260926`, sorteada
  **depois** dos consertos): **23 certas, 1 errada, 1 não sei**. A errada é TRINEX
  «tomate × *Sphaerotheca pannosa*» — a praga é da rosa, na mesma frase. A «não sei»
  é COSAYR: várias pragas com doses diferentes na mesma linha, e o parser dá a lista
  da linha, sem ligar dose a praga. Amostra pequena: **~96% com margem larga**.

## 4. Achados que não são desta missão consertar

1. **156 pares publicados são falsos por vazamento.** O bloco sem título do leitor
   antigo pega 8 linhas e entra na cultura seguinte: «KLARTAN 20 EW × VITE ×
   *Leptinotarsa decemlineata*» (a dorifora é da batata). **156 de 556** pares de
   bloco sem título em `IT-ROTULOS-PARES.json` só existem pelo vazamento, em 6
   rótulos (EVURE PRO 31, MAVRIK SMART 30, KLARTAN SMART 27, KLARTAN 20 EW 23,
   MAVRIK EW 23, TAU AL 240 EW 22 — os de tau-fluvalinate). Sorteei 12 (semente 7)
   e conferi contra o texto: **12 de 12 falsos**. Pelo mesmo
   número (2.030) é provável que estejam em `referencia/adama/AUTHORIZED-USES.json`
   e no portal — **não conferido**. Lista completa em
   `medidas/ROTULO-T4-MEDIDA-163.json` → `PARES_PUBLICADOS_PELO_VAZAMENTO`.
2. **Adjuvante lido como alvo.** No OLIONET (014386) a tabela é de parceiros de
   mistura; o parser lê o nome do herbicida parceiro como «alvo». Não consertado.
3. **Efeito colateral da suíte antiga**: a bateria reescreve
   `data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json` e cria
   `data/samples/PRONTO-PARA-INTELIGENCIA/`. Guardei a diferença
   (`/c/tmp/rt4/efeito-colateral-censo.diff`, sha256 `0d81280b…`) e repus.

## 5. Testes

`tests/test_rotulo_t4_it.py` — 44 testes, sem rede, cada classe diz se usa dado
REAL do repo ou SINTETICO marcado.

<<TESTES>>

## 6. Mutação

`tests/mutacao_rotulo_t4.py` planta 24 defeitos, um de cada vez, e exige que os
testes falhem; restaura pelos bytes guardados e confere o sha256.

**24 mutantes, 24 mortos, 0 vivos.** Três sobreviveram pelo caminho (M05 faixa
invertida, M15 duas unidades no cabeçalho, M22 número solto) e cada um virou um
teste novo — não se enfraqueceu teste nenhum.

## 7. Dependências e limites

- `pypdf` 6.19 está no `python` desta máquina; **não** está no `py` (o Python do
  runner). Sem ele o parser cai para `pdftotext` (poppler); sem os dois, `ERRO` com
  o nome da dependência. O teste de PDF salta, declarado, se faltarem os dois.
- Li os 163 PDFs **fora da pasta do ramo** (`C:/eame-sintonia/…`), só leitura, cada
  um conferido pelo sha256 do manifesto. Não escrevi lá.
- Dose por coluna (tabela com duas unidades) pede a geometria da página; não feito.
- Errei o processo uma vez: a primeira bateria de base correu **sem** a
  `LOCK-PESADO`, porque ainda não conhecia a regra. Daí em diante só com ela.

## 8. SHA

<<SHA>>

---

## EM PALAVRAS SIMPLES

O rótulo de um defensivo é a "bula" oficial: diz em que planta ele pode ser usado,
contra que praga, quanto usar e quando. Construí o programa que lê essa bula e a
transforma numa planilha, uma linha por uso.

Em cada linha, cada informação vem com um carimbo que diz o quanto confiamos nela:
**conferido** (duas fontes dizem o mesmo), **encontrado** (está escrito, mas ninguém
conferiu), **não sei**, ou **erro**. Não existe o carimbo "não autorizado": se o
programa não conseguiu ler um uso, isso é limite do programa, não prova de que a
ADAMA não pode vender para aquilo. É como não achar a chave na gaveta: não quer
dizer que a chave não existe.

Testei nos 163 rótulos reais da ADAMA. Em 144 de 163, o número do rótulo bate com o
registo oficial, sem nenhum conflito. O programa tira usos de 69 rótulos. Quando dá
uma dose, acertou 54 de 54 contra outra leitura, e 23 de 25 numa amostra que li à mão.
Quando não tem certeza de qual número é a dose, prefere dizer "não sei".

O achado mais importante: o leitor antigo, que já está publicado, misturava culturas
vizinhas no texto. Por exemplo, dizia que um inseticida serve na **uva** contra um
besouro que é praga da **batata**, só porque os dois parágrafos estavam colados. São
156 pares assim em 556 desse tipo. O programa novo não comete esse erro. O ficheiro
antigo não mexi — fica para o dono decidir.
