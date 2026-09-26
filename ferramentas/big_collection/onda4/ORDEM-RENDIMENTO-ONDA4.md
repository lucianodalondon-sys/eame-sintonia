# ORDEM PELO RENDIMENTO — as 15 rodadas da 4.ª onda, reordenadas

Ordem do coordenador (26/09 11:45), a partir do retorno da Intelligence, rodada 2
(`intelligence-experimental/EXPD78-R2-20260926T135653Z/RELATORIO-RODADA-2.md`, secção 2, e
`R1-X-R2-E-FONTES.json`): **T3/T10/T2 primeiro, T5 institucional por último, a rodada 1 é a de maior
rendimento previsto.** Ramo `ensaio-rodada1-v1`, sobre o vivo `69b0e23f`. Sem rede, nada instalado.

## O que mudou e o que NÃO mudou

- **Não mudou:** teto de 5 pedidos por domínio por rodada; 1 rodada por janela móvel de 24 h por
  domínio (D79); a coorte congelada (`eb7b6ab7`, 64 fontes, `PODE_CORRER=true`); 15 rodadas; 301 pedidos
  previstos. Ninguém sai da coorte («zero» da Intelligence = UNDER_SAMPLED, não «fonte má»).
- **Mudou (`rodadas.py`, `--rendimento=<R1-X-R2-E-FONTES.json>`):** dentro de cada domínio as fontes vão
  pela classe (0 A/B · 1 T3/T10/T2 · 2 sem medida · 3 C · 4 D fora de T5 · 5 T5 institucional); as T5
  institucionais vão para as **últimas** rodadas do plano; as outras para as primeiras.
- **Consertado na mesma passagem (a janela tinha dois buracos):**
  1. não lia os recibos das outras missões com rede — `--recibos=<pastas>` lê `RECIBO*.json`
     (PEDIDOS_POR_DOMINIO + GERADO_EM; planos não contam);
  2. olhava só o domínio do plano — cada fonte leva agora **todos os domínios que tocou** nas ondas
     anteriores. IT-T7-172 pede `georgofili.info` e é redireccionada para `georgofili.it`.
- **O plano recebe a hora de início** (`--inicio=2026-09-26T19:58:33-03:00`): um domínio visitado há
  menos de 24 h só entra na rodada cujo início previsto já passou a abertura.

## A colisão com o que já correu hoje: **0**

| missão de hoje | recibo lido | domínios pedidos | em comum com a R1 (todos os domínios tocados) |
|---|---|---|---|
| VOZES ronda 1 | `vozes-agronomos/RECIBO-RONDA-1.json` (14:22Z, 22 pedidos) | 11 | **0** (georgofili.it saiu da R1) |
| MICRO-PROVA 2B | `micro-prova/lote2b-1105` (82 pedidos) | 20 | **0** |
| T6 pesquisadores | `pesquisadores-t6/rede` | 3 (openalex, crossref, orcid) | **0** |

- **O caso que isto evitou:** na ordem antiga a R1 tinha IT-T7-172. Às 19:58 pediria `georgofili.it`
  menos de 24 h depois de VOZES (2 pedidos às 14:21Z), e a janela antiga não o via. Com a janela nova,
  sem mudar a ordem, a R1 inteira ficaria parada até 27/09 14:22Z. A ordem nova põe IT-T7-172 na R2.
- Com a janela nova (ondas + recibos), às 19:58:34 a R1 tem **0 domínios fechados**.

## Rendimento previsto (peso: A/B 3 · T3/T10/T2 2 · sem medida 1 · C 0,5 · D e T5 0)

- R1: **40,0** com 33 fontes e 152 pedidos. Na ordem antiga: 40,0 com 38 fontes e 174 pedidos. O mesmo
  rendimento com **5 fontes e 22 pedidos a menos** (os que saíram pesavam 0). A R2 vale 7,0.
- R1 por classe: A 1 (IT-T10-018) · T10 2 · T3 1 · T2 6 · sem medida 19 · D 4 · **T5 0**.
- ⚠️ **CNR (IT-T5-160, cnr.it)** está na coorte e foi para o fim. A mensagem de 26/09 10:13 diz «sem
  CNR/Coldiretti/ANGA/Unaprol» para a rede de hoje. Tirar a CNR da 4.ª onda é decisão do coordenador.

## Provas

- `tests/test_rodadas.py` **38/38** (29 + 9 novos: classes; T5 no fim e o resto no início; teto por
  rodada mantido; bloqueio de hoje empurra o domínio para a rodada que já abriu; sem `--rendimento` o
  plano é igual ao de antes; recibo conta; plano não é recibo; a janela vê o domínio do redireccionamento;
  a rodada para pelo recibo sem pedir nada).
- Mutação `provas/rodadas_mutacao.py` **24/24** (18 + 6: prioridade ignorada, T5 não vai para o fim,
  bloqueio ignorado, recibos ignorados, plano conta como recibo, janela só do domínio do plano).
- Plano real: cópia de `ensaio-rodada1-v1` com os 17 livros vivos copiados (só leitura), fila esvaziada
  na cópia, proxy morto. Saída: `auditoria-madrugada\ENSAIO-RODADA1\so-plano-rendimento\RODADAS-SO-PLANO.json`.

## Comando (para o roteiro)

```
py ferramentas/big_collection/rodadas.py --correr --sha256=eb7b6ab75056cff37b892cb7e9e59a553f6b9048ff8a5db961c532e643f0b9e4 ^
   --base=%USERPROFILE%\sintonia-sala-italia\ondas\ONDA4-RODADAS ^
   --historico=%USERPROFILE%\sintonia-sala-italia\ondas\ONDA2-WEB-20260925-0812\ONDA-WEB-ESTADO.json,%USERPROFILE%\sintonia-sala-italia\ondas\ONDA3-WEB-20260925-1934\ONDA-WEB-ESTADO.json ^
   --livros-do-dia=%USERPROFILE%\sintonia-sala-italia\ondas ^
   --rendimento=%USERPROFILE%\sintonia-sala-italia\intelligence-experimental\EXPD78-R2-20260926T135653Z\R1-X-R2-E-FONTES.json ^
   --recibos=%USERPROFILE%\sintonia-sala-italia\vozes-agronomos,%USERPROFILE%\sintonia-sala-italia\micro-prova,%USERPROFILE%\sintonia-sala-italia\pesquisadores-t6 ^
   --inicio=2026-09-26T19:58:33-03:00 --rodada=1
```

## As 15 rodadas

| rodada | fontes | pedidos | rendimento previsto | janela abre (UTC) |
|---|---|---|---|---|
| 1 | 33 | 152 | 40.0 | 2026-09-26T22:58:33+00:00 |
| 2 | 5 | 20 | 7.0 | 2026-09-27T14:22:41+00:00 |
| 3 | 2 | 9 | 2.0 | 2026-09-26T22:53:12+00:00 |
| 4 | 2 | 10 | 2.0 | 2026-09-26T22:53:12+00:00 |
| 5 | 2 | 10 | 2.0 | 2026-09-26T22:53:12+00:00 |
| 6 | 1 | 5 | 1.0 | 2026-09-26T22:40:21+00:00 |
| 7 | 1 | 5 | 1.0 | 2026-09-26T22:40:21+00:00 |
| 8 | 1 | 5 | 1.0 | 2026-09-26T22:40:21+00:00 |
| 9 | 1 | 5 | 1.0 | 2026-09-26T22:40:21+00:00 |
| 10 | 1 | 5 | 1.0 | 2026-09-26T22:40:21+00:00 |
| 11 | 2 | 10 | 1.0 | 2026-09-26T22:45:06+00:00 |
| 12 | 2 | 10 | 1.0 | 2026-09-26T22:45:06+00:00 |
| 13 | 3 | 15 | 1.0 | 2026-09-26T22:46:58+00:00 |
| 14 | 3 | 15 | 1.0 | 2026-09-26T22:46:58+00:00 |
| 15 | 5 | 25 | 1.0 | 2026-09-26T22:46:58+00:00 |

**Rodada 1**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T10-018 | myfruit.it | 5 | A_DEU_SINAL |
| 2 | IT-T10-021 | imagelinenetwork.com | 4 | T10 primeiro (sem medida) |
| 3 | IT-T10-022 | zootecnicainternational.com | 5 | T10 primeiro (sem medida) |
| 4 | IT-T12-024 | regione.veneto.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 5 | IT-T12-117 | calabriaimpresa.eu | 4 | sem medida (NEVER/UNDER_SAMPLED) |
| 6 | IT-T12-129 | regione.sicilia.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 7 | IT-T3-023 | edagricole.it | 5 | T3 primeiro (sem medida) |
| 8 | IT-T12-137 | psrn.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 9 | IT-T2-050 | arpacampania.it | 5 | T2 primeiro (sem medida) |
| 10 | IT-T2-032 | arpal.liguria.it | 5 | T2 primeiro (sem medida) |
| 11 | IT-T2-034 | arpa.marche.it | 5 | T2 primeiro (C_DATADO_SEM_SINAL) |
| 12 | IT-T2-037 | arpat.toscana.it | 5 | T2 primeiro (sem medida) |
| 13 | IT-T2-051 | arpae.it | 5 | T2 primeiro (sem medida) |
| 14 | IT-T2-145 | arpa.veneto.it | 5 | T2 primeiro (sem medida) |
| 15 | IT-T7-017 | riuniteciv.com | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 16 | IT-T7-019 | confagricoltura.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 17 | IT-T7-021 | etvilloresi.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 18 | IT-T7-033 | chianticlassico.com | 2 | D_ZERO_PARA_A_MAQUINA |
| 19 | IT-T7-042 | consorziobalsamico.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 20 | IT-T7-043 | federchimica.it | 2 | sem medida (NEVER/UNDER_SAMPLED) |
| 21 | IT-T7-048 | caiagromec.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 22 | IT-T7-049 | copagri.org | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 23 | IT-T7-103 | confcooperative.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 24 | IT-T7-121 | cia.it | 3 | sem medida (NEVER/UNDER_SAMPLED) |
| 25 | IT-T7-117 | caf-cia.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 26 | IT-T7-125 | cia-puglia.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 27 | IT-T7-139 | florovivaistiitaliani.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 28 | IT-T7-141 | ciatoscana.eu | 2 | sem medida (NEVER/UNDER_SAMPLED) |
| 29 | IT-T7-163 | casalasco.com | 5 | D_ZERO_PARA_A_MAQUINA |
| 30 | IT-T8-062 | uniss.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 31 | IT-T9-009 | cifo.it | 5 | D_ZERO_PARA_A_MAQUINA |
| 32 | IT-T9-011 | koppert.it | 5 | D_ZERO_PARA_A_MAQUINA |
| 33 | IT-T9-021 | indire.it | 5 | sem medida (X_CONTESTADA) |

**Rodada 2**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T12-131 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 2 | IT-T2-006 | arpacampania.it | 5 | T2 primeiro (sem medida) |
| 3 | IT-T2-146 | arpa.veneto.it | 5 | T2 primeiro (sem medida) |
| 4 | IT-T7-123 | cia.it | 3 | sem medida (NEVER/UNDER_SAMPLED) |
| 5 | IT-T7-172 | georgofili.info, georgofili.it | 2 | sem medida (NEVER/UNDER_SAMPLED) |

**Rodada 3**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-021 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 2 | IT-T7-135 | cia.it | 4 | sem medida (NEVER/UNDER_SAMPLED) |

**Rodada 4**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-022 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 2 | IT-T7-112 | cia.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |

**Rodada 5**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-024 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 2 | IT-T7-118 | cia.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |

**Rodada 6**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-028 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |

**Rodada 7**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-029 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |

**Rodada 8**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-030 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |

**Rodada 9**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-034 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |

**Rodada 10**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-039 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |

**Rodada 11**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-040 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 2 | IT-T5-080 | crea.gov.it | 5 | T5 institucional (sem medida) |

**Rodada 12**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-041 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 2 | IT-T5-111 | crea.gov.it | 5 | T5 institucional (sem medida) |

**Rodada 13**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-042 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 2 | IT-T5-113 | crea.gov.it | 5 | T5 institucional (sem medida) |
| 3 | IT-T5-187 | enea.it | 5 | T5 institucional (sem medida) |

**Rodada 14**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T8-051 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 2 | IT-T5-167 | crea.gov.it | 5 | T5 institucional (D_ZERO_PARA_A_MAQUINA) |
| 3 | IT-T5-185 | enea.it | 5 | T5 institucional (D_ZERO_PARA_A_MAQUINA) |

**Rodada 15**

| # | fonte | domínio(s) | pedidos | classe |
|---|---|---|---|---|
| 1 | IT-T12-130 | edagricole.it | 5 | sem medida (NEVER/UNDER_SAMPLED) |
| 2 | IT-T5-025 | santannapisa.it | 5 | T5 institucional (D_ZERO_PARA_A_MAQUINA) |
| 3 | IT-T5-056 | crea.gov.it | 5 | T5 institucional (D_ZERO_PARA_A_MAQUINA) |
| 4 | IT-T5-160 | cnr.it | 5 | T5 institucional (D_ZERO_PARA_A_MAQUINA) |
| 5 | IT-T5-186 | enea.it | 5 | T5 institucional (C_DATADO_SEM_SINAL) |

