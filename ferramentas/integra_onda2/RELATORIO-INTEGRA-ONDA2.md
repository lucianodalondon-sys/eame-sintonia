# INTEGRA-ONDA2 · as três peças da 2.ª onda juntas, e o ensaio integrado — 25/09/2026

Ramo `integra-onda2-v1`, a partir da produção `servico-20260923-0923 @ 7cdb7ea4`. **NÃO instalado, NÃO disparado.**

## Em palavras simples

Juntei as três peças que vão entrar antes do MICRO — o teto de 5 pedidos por domínio (ONDA2-G3), a
escolha de alvos novos (CAPA-MATERIA/ALVOS-NOVOS) e a entrada das fontes provadas no coletor
(PONTE-ONBOARD) — mais a minha prova do teto. Nenhum conflito de código. Numa cópia fiel do vivo,
com a rede FECHADA: entram **17 fontes** no coletor, a coorte passa de **18 para 29**, a 2.ª onda
correria **23 fontes com no máximo 5 pedidos por domínio (83 no total)**, e a prova independente
diz **PASS** nos dois planos. **Mas o MICRO do LOTE-MICRO-V2 só tem 1 fonte pronta das 6.**

## 1 · A junção

| ordem | ramo | commit | conflitos |
|---|---|---|---|
| 1 | onda2-g3-v1 (PRONTO) | a55c667f | nenhum |
| 2 | capa-materia-v1 (PRONTO) | 7c925f30 → 1008b1bc → **a1dbebcc** | só gerados pela cadeia (13, cada vez) |
| 3 | ponte-onboard-v1 (PRONTO) | 819bfe81 → **7e3fed2c** | só gerados pela cadeia (13) |
| 4 | prova-teto-v1 | 65050da3 → **ed29f2d6** (modo `--plano`) | nenhum |

Os gerados em conflito ficaram na versão já no ramo e refazem-se pela cadeia (LOCK-PESADO).

**O único ficheiro de código tocado por dois ramos:** `coleta/italy_pilot_collect.mjs` (G3 e CAPA-MATERIA),
junto sem conflito. Conferido o sentido: a única chamada à rede (`curl`) está dentro de `umaIda()`, o
contador por domínio da G3; a CAPA-MATERIA só muda QUAIS endereços se escolhem (`classificar` → `alvosDoContrato`),
e eles continuam a ser pedidos por `baixar()` → `umaIda()`. O teto não fica furado.

**Testes sobre a junção:** `test_onda_web` 12/12 · `test_teto_dominio` 1/1 · `teto_dominio_local.mjs` 7/7 ·
`test_canario_rotas_contrato_certo` 6/6 · `test_onboardar_rotas_provadas` 29/29 · `motor_de_rota_test.mjs` 60/60 ·
`test_prova_teto_dominio` 19/19.

## 2 · O ensaio integrado (cópia fiel do vivo, rede FECHADA — D41.3)

- **Cópia:** clone local do ramo (`C:/integra/copia`, sem rede) + os 14 livros do vivo
  `source-curator-service-v1 @ 7cdb7ea4` e a tabela do coletor e a prova de rotas copiados por cima
  (`ENSAIO-0-FOTO-DOS-LIVROS-DO-VIVO.txt`, sha256; nenhum mudou durante a cópia).
- **Rede fechada:** `HTTP(S)_PROXY/ALL_PROXY = http://127.0.0.1:9` em todos os comandos; conferido
  (ligar a www.cia.it → recusado na hora). **O robô (worker/supervisor) não correu na cópia.**
- **Prova de rota: 0 pedidos.** Não foi preciso rede: usei a prova que a PONTE-ONBOARD fez HOJE
  (`ferramentas/ponte_onboard/ENSAIO-2-rotas-provadas-3rondas.json`, 06:38Z, portão PASS IT, ≤ 1 fonte
  por domínio por ronda), juntada à prova do vivo pela própria função `juntar` do canário.

| passo | resultado |
|---|---|
| onboarding ANTES (provas do vivo, sem impressão) | ENTRA=0 · FICA=44 |
| onboarding com a prova de hoje | **ENTRA=17** · FICA=27 (as 27: sobretudo fontes novas da R1 sem canário) |
| aplicar | 17 escritas; tabela `856f833f → 6255cd27` (a mesma impressão do ensaio da PONTE); livro do Curator igual (`b53743af`) |
| plano do runbook (`micro_coleta.py plano`) | 73 elegíveis no portão · **PRONTAS 29** · BLOQUEADAS 44 |
| coorte congelada (valores de ENSAIO, commit só na cópia) | **CONGELADA 29** (as 18 da 1.ª onda + 11 novas: ARPA ×5, CNR IBBA, CREA, ENEA ×3, Georgofili) · sha256 do commit `c168e192…` |
| 2.ª onda `onda_web.py --so-plano` | **23 correm**, 6 saltam por TETO_DOMINIO (IT-T2-146, IT-T5-186, IT-T5-187, IT-T7-121, IT-T7-123, IT-T7-135), 1 parcial (IT-T7-118); 22 domínios; **máximo 5**; **83 pedidos previstos** |
| MICRO `micro_coleta.plano(LOTE-MICRO-V2)` | **1 PRONTA de 6** (IT-T10-018 myfruit) — ver ⚠️ abaixo |
| prova-teto sobre o plano da 2.ª onda | **PASS** · 83 previstos · 0 domínios acima de 5 · as 29 fontes com INDEX_URL no contrato e o domínio calculado por esta prova igual ao do plano |
| prova-teto sobre o plano do MICRO | **PASS** (pior caso: 5 pedidos a myfruit.it) |
| desfazer | tabela reposta → `856f833f`; coorte revertida → PROVISORIA 18; livro do Curator `b53743af` o tempo todo |

## ⚠️ O que é preciso saber antes do MICRO

**LOTE-MICRO-V2: só 1 das 6 fontes corre.**

| fonte | papel | falta |
|---|---|---|
| IT-T10-018 | PRINCIPAL (myfruit) | nada — PRONTA |
| IT-T3-002 | boletim fitossanitário | `GATE:READY_LEGACY` + `SEM_CONTRATO_DE_COLETA` |
| IT-T3-010 | boletim fitossanitário | `GATE:READY_LEGACY` + `SEM_CONTRATO_DE_COLETA` |
| IT-T2-002 | boletim agrometeo ARPAV | `GATE:READY_LEGACY` + `SEM_CONTRATO_DE_COLETA` |
| IT-T3-023 | da R1 | `SEM_CONTRATO_DE_COLETA` |
| IT-T7-049 | da R1 | `SEM_CONTRATO_DE_COLETA` |

A pré-condição dos 3 boletins («REVALIDAR READY_LEGACY → DETAIL/v1 no Curator») não foi feita, e a
régua de promoção de hoje só aprova HTML (os boletins são PDF — `PLANO-BOLETINS-READY-LEGACY.md` da
PONTE). As 2 da R1 não estão nas 17 que o onboarding põe no coletor (sem canário). Pela regra do
próprio lote, as 5 contam como NAO_CORREU. **Decisão do coordenador antes do MICRO.**

## Outras ressalvas

1. A prova de rota do ensaio é a da PONTE (hoje, 06:38Z). No vivo o canário tem de correr de novo
   (plano, passo 4): as provas do vivo não têm a impressão digital do contrato.
2. `coorte_unica.py` só grava com `--saida=`; sem ele imprime e não escreve (apanhado no ensaio).
3. O `onda_web.py --correr` exige a coorte COMMITADA no ramo do vivo (confere `git show HEAD:`) e o
   `--sha256=` do commit (`COORTE_SHA256_DO_COMMIT` do `--so-plano`), não o do ficheiro no disco.
4. O mapa deste ramo ainda está por regenerar pela cadeia (LOCK-PESADO ocupada por outras bancadas).
