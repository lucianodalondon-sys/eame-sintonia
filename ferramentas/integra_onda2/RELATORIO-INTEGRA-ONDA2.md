# INTEGRA-ONDA2 · as peças da 2.ª onda juntas, e o ensaio integrado — 25/09/2026

Ramo `integra-onda2-v1`, a partir da produção `servico-20260923-0923 @ 7cdb7ea4`. **NÃO instalado, NÃO disparado.**
Números finais com a **D45** (bot Luciano): ISTAT (IT-T5-090) **fora desta onda**; nenhum livro do vivo é escrito.

## Em palavras simples

Juntei, sem nenhum conflito de código, as peças que entram antes do MICRO: o teto de 5 pedidos por
domínio com rotação justa (CONTRATOS-12, que contém a ONDA2-G3), a escolha de alvos novos e os dois
ajustes de contratos (CONTRATOS-AJUSTE, que contém a CAPA-MATERIA), a entrada das fontes provadas no
coletor (PONTE-ONBOARD) e a minha prova independente do teto. Numa cópia fiel do vivo, com a rede
FECHADA: entram **17 fontes** no coletor, a coorte passa de **18 para 28**, a 2.ª onda correria
**22 fontes com no máximo 5 pedidos por domínio (80 no total)**, e a prova do teto diz **PASS**.
O MICRO do LOTE-MICRO-V2 só tinha **1 fonte pronta de 6** (o lote V3 é da bancada APOIO-INTEGRA).

## 1 · A junção

| ordem | ramo | commit | conflitos |
|---|---|---|---|
| 1 | contratos-12-v1 (PRONTO; contém onda2-g3-v1 a55c667f) | **54c98fe4** | nenhum |
| 2 | contratos-ajuste-v1 (PRONTO; contém capa-materia-v1 a1dbebcc) | **ca923030** | só gerados pela cadeia |
| 3 | ponte-onboard-v1 (PRONTO) | **7e3fed2c** | só gerados pela cadeia |
| 4 | prova-teto-v1 (modo `--plano`) | **ed29f2d6** | nenhum |

(A história do ramo tem também as junções intermédias — a55c667f, 7c925f30, 1008b1bc, a1dbebcc, 819bfe81 —
que as versões finais contêm.) Os gerados em conflito ficaram na versão já no ramo e refazem-se pela cadeia.

**Único ficheiro de código tocado por dois ramos:** `coleta/italy_pilot_collect.mjs` (G3 e CAPA-MATERIA),
junto sem conflito. Sentido conferido: a única chamada à rede (`curl`) está dentro de `umaIda()` (o
contador por domínio); os alvos novos continuam a ser pedidos por `baixar()` → `umaIda()`. O teto não fica furado.

**Testes sobre a junção:** `test_onda_web` 17/17 · `test_teto_dominio` 1/1 · `teto_dominio_local.mjs` 7/7 ·
`test_canario_rotas_contrato_certo` 6/6 · `test_onboardar_rotas_provadas` 29/29 · `motor_de_rota_test.mjs` 62/62 ·
`test_prova_teto_dominio` 19/19.

## 2 · O ensaio integrado FINAL (`final/`, script `final/ensaio_integra.sh`)

- **Cópia:** clone local do ramo (sem rede) + os 14 livros do vivo `source-curator-service-v1 @ 7cdb7ea4`
  copiados por cima (`final/ENSAIO-FINAL-0-FOTO-DOS-LIVROS.txt`, sha256). A tabela do coletor e a
  prova de rotas vêm do **ramo** (o vivo tem-nas iguais ao Git de 7cdb7ea4, por isso o merge substitui-as).
- **Rede fechada (D41.3):** proxies em `127.0.0.1:9`, conferido (www.cia.it → recusado). **O robô não correu.**
- **Prova de rota: 0 pedidos** — a da PONTE-ONBOARD de hoje (`ferramentas/ponte_onboard/ENSAIO-2-rotas-provadas-3rondas.json`,
  06:38:58Z, portão PASS IT), juntada pela função `juntar` do canário.

| passo | resultado |
|---|---|
| onboarding ANTES | ENTRA=0 · FICA=44 |
| onboarding com a prova de hoje | **ENTRA=17** · FICA=27 → 17 escritas; livro do Curator igual (`b53743af`) |
| plano do runbook | PRONTAS 29 · BLOQUEADAS 44 |
| coorte congelada (ENSAIO, commit só na cópia) | **28** — a PRONTA IT-T5-090 (ISTAT) fica FORA por `CONTRATO_EXECUTAVEL` (D45) |
| 2.ª onda `onda_web.py --so-plano` | **22 de 28 correm**; saltam por TETO_DOMINIO IT-T2-146, IT-T5-186, IT-T5-187, IT-T7-121, IT-T7-123, IT-T7-135; parcial IT-T7-118; **máximo 5 por domínio**; **80 pedidos** |
| prova-teto sobre o plano da 2.ª onda | **PASS** · 80 previstos · 0 domínios acima de 5 · domínio de cada uma das 28 fontes (pelo INDEX_URL do contrato) igual ao do plano |
| MICRO LOTE-MICRO-V2 (`prova_teto_micro.py`) | **1 PRONTA de 6** (IT-T10-018 myfruit) · prova **PASS** (5 a myfruit.it, pior caso) |
| desfazer | tabela = a do Git (diferença só de fim de linha); coorte volta a PROVISORIA 18; livro do Curator igual |

## 3 · D45 — a ISTAT fora desta onda

A CONTRATOS-AJUSTE aponta a ISTAT (IT-T5-090) para `/comunicato-stampa/` e `/notizia/` na tabela do
coletor; o contrato do Curator (`curadoria/italy_contracts_curator.json`, livro do vivo) continua com
`https://www.istat.it/it/`. A prova `CONTRATO_EXECUTAVEL` da coorte exige os dois iguais byte a byte →
a ISTAT sai da coorte (28) e os seus 3 pedidos saem da onda (80). **Decisão D45: fica assim; alinha-se depois pelo Curator.**

## 4 · Antes do MICRO

O LOTE-MICRO-V2 tinha **1 fonte pronta de 6**: os 3 boletins continuam `READY_LEGACY` + `SEM_CONTRATO_DE_COLETA`
(PDF; a régua de promoção só aprova HTML); as 2 da R1 (IT-T3-023, IT-T7-049) estão `SEM_CONTRATO_DE_COLETA`.
O lote V3 é da bancada APOIO-INTEGRA; o plano de instalação (passo 13) confere-o com o mesmo comando.

## 5 · Ressalvas

1. A prova de rota do ensaio é a da PONTE (25/09 06:38:58Z) — **vale 7 dias, até 02/10 06:38Z**. O plano
   dá as duas formas: reaproveitá-la (0 pedidos) ou refazer as rondas no vivo.
2. `coorte_unica.py` só grava com `--saida=`; sem ele imprime e não escreve.
3. `onda_web.py --correr` exige a coorte COMMITADA no ramo do vivo e o `--sha256=` do COMMIT
   (`COORTE_SHA256_DO_COMMIT` do `--so-plano`), não o do ficheiro no disco (CRLF).
4. O 1.º ensaio (ficheiros `ENSAIO-0..5-*` nesta pasta) foi ANTES da CONTRATOS-12 e da CONTRATOS-AJUSTE
   (29 / 83). Os números que valem são os de `final/`.
