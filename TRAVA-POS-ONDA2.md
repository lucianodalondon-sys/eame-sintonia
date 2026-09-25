# TRAVA-POS-ONDA2 — a trava da Intelligence medida de novo, depois do MICRO-V3 e da 2.ª onda

> Entrega para a reunião de segunda (D50). **Só leitura.** A trava (`docs/operacao/TRAVA-DA-INTELIGENCIA.json`)
> **não foi editada**. Sala lida só por `SELECT` com `default_transaction_read_only = on` (conferido na saída).
> Rede fechada. Vivo não tocado. Ramo `trava-pos-onda2-v1`, a partir de `trava-medidores-v1 @ c821094d`.

## 0 · Em uma linha

**A trava continua FECHADA.** `COLLECTION_FOUNDATION_CLOSED = NAO`. **A..N = 4 SIM · 8 NÃO · 2 sem medidor — igual
à última medição.** As duas corridas trouxeram material real (Sala 69 → 78), mas **nenhum critério mudou**, por
três razões medidas:

1. o registo das ondas está **fora do Git** (`C:\Users\London1\sintonia-sala-italia\ondas\…`), e o medidor só lê o Git;
2. mesmo copiado para o lugar oficial, **o formato não seria reconhecido**: o `onda_web` não grava `RAW` nem `DERIVED`
   por fonte, e o medidor exige essas duas chaves (`system-map/scripts/censo_das_estradas_it.py:959-962`);
3. os outros critérios medem **código e donos**, e as corridas não mudam código.

## 1 · O que correu

| corrida | fontes | correram (SUCCESS) | trouxeram documento (RAW ≥ 1) | pousaram na Sala |
|---|---:|---:|---:|---:|
| MICRO-V3 (08:03–08:08) | 6 | 6 | 6 | 2 (IT-T10-018) |
| 2.ª onda (08:12–08:25) | 28 | 19 (+1 FAILED, 8 adiadas pelo teto D38 por domínio) | 13 | 7 (IT-T5-185 ×3, IT-T5-167 ×2, IT-T5-160, IT-T2-034) |

Fonte: `ONDA-WEB-ESTADO.json` de cada pasta (campo `C4` por fonte). **Sala 69 → 78.**

## 2 · Os 14 critérios, agora contra a última medição

Última medição: `trava-medidores-v1` (§5 de `TRAVA-MEDIDORES-V1.md` e §0 de `TRAVA-MEDIDORES-V1-D33-CRITERIO-A.md`).

| | critério | última | **agora** | o que mudou com as corridas, e porquê |
|---|---|---|---|---|
| **A** | toda fonte IT com classe provada ou bloqueio explícito | NÃO (98 provadas · 29 bloqueadas · 589 NÃO SEI, das 716) | **NÃO — igual** | nada no Git. **Simulado fora do repo** (ver §3): com os registos das ondas no lugar oficial e com `RAW/DERIVED`, **98 → 103** provadas, NÃO SEI 589 → 584. **A continuaria NÃO** |
| **B** | nenhuma fonte depende de writer improvisado | sem medidor | **sem medidor** | — |
| **C** | RAW tem um dono | NÃO (4 escritores) | **NÃO — igual** | é código; as corridas não mudam donos |
| **D** | a corrida tem um contrato | SIM | **SIM** | — |
| **E** | o checkpoint tem um dono | NÃO (2) | **NÃO — igual** | idem C |
| **F** | o derivado tem um dono | SIM | **SIM** | — |
| **G** | persistência estruturada com dono | NÃO | **NÃO — igual** | os 9 itens novos são todos `DOCUMENTO`; nenhum `FATO` estruturado |
| **H** | a escolha de rota não vive espalhada | NÃO | **NÃO — igual** | idem C |
| **I** | Apify não é rota por omissão | SIM | **SIM** | as corridas foram só HTTP |
| **J** | o Git não é estado operacional | NÃO (521 + 59 linhas de `ndjson` no Git) | **NÃO — e pior no vivo** | no Git: 521 + 59 (igual). No vivo, os mesmos ficheiros **rastreados** cresceram para **590 + 112** e estão por commitar (`git status` do vivo: `M`). Se forem commitados, o Git ganha 69 + 53 linhas de estado operacional |
| **K** | retry e queda não fabricam sucesso | sem medidor | **sem medidor** | o material existe (C4, `FAILED`, `TETO_DOMINIO` por fonte); ninguém o mede |
| **L** | UNKNOWN continua UNKNOWN | SIM | **SIM** | os 78 itens mantêm `NAO SEI` onde não há prova (tempos, lugar); `published_at = captured_at` em 0 — ninguém carimbou a nossa visita |
| **M** | o System Map representa tudo | NÃO (202 de 241 pendentes) | **NÃO — não re-medido** | valor publicado em `c821094d`; re-medir pede a cadeia do mapa (trabalho pesado) e o repo não mudou |
| **N** | a inteligência continua congelada | NÃO (16 mudaram · 5 novos; dos 21: 5 avanço proibido, 3 do dono, 1 por julgar) | **NÃO — igual** | é código; as corridas não mexem na fotografia |

**Totais: 4 SIM (D, F, I, L) · 8 NÃO (A, C, E, G, H, J, M, N) · 2 sem medidor (B, K). Condição de destrave: 0 de 5.**

O que foi re-corrido agora: o medidor do critério A (`criterio_a_no_curador`) e o inventário da Sala. Os outros
foram lidos dos ficheiros que os medidores publicaram em `c821094d`. Como o ramo e o código não mudaram, correr os
outros medidores daria o mesmo — **declarado, não verificado** (a cadeia inteira é trabalho pesado).

## 3 · O que falta para as corridas contarem no critério A (sem copiar nada para o repo)

Simulação feita **fora do repositório** (`C:\Users\London1\trava-pos-onda2\simulacao\`): cópia da pasta oficial +
os 2 `ONDA-WEB-ESTADO.json` com `RAW := C4.OBSERVACOES` e `DERIVED := C4.COM_DERIVADO`, lidos pelo **mesmo** medidor.
Resultado em `data/derivados/TRAVA-POS-ONDA2/A-SIMULADO-COM-AS-ONDAS.json`.

| fonte | antes | com as ondas | prova |
|---|---|---|---|
| IT-T10-021 | NÃO SEI | **RC-1** | MICRO-V3, RAW 3 / DERIVED 3 |
| IT-T2-034 | NÃO SEI | **RC-1** | MICRO-V3, RAW 3 / DERIVED 3 |
| IT-T2-051 | NÃO SEI | **RC-1** | MICRO-V3, RAW 3 / DERIVED 3 |
| IT-T7-017 | NÃO SEI | **RC-1** | MICRO-V3, RAW 3 / DERIVED 3 |
| IT-T7-112 | NÃO SEI | **RC-1** | 2.ª onda, RAW 2 / DERIVED 2 |

Não mudam, e porquê:
- IT-T10-018, IT-T7-021, IT-T7-117: **já provadas** (BC4D / 1.ª onda).
- IT-T2-032, IT-T2-037: trouxeram documento, mas **não têm contrato no livro do coletor deste ramo** → continuam NÃO SEI.
- IT-T2-145, IT-T5-160, IT-T5-167, IT-T5-185: **fora das 716** — o livro de estados do Curator que está no Git
  deste ramo é anterior a elas (entraram pela FILA-UNICA no vivo).

**O que falta, exactamente:**
1. **o formato:** o registo por fonte do `onda_web` (produção `df0865e6`, `ferramentas/big_collection/onda_web.py:312-319`) grava `C4`,
   `STATUS`, `RUN_ID`, mas **não** `RAW` e `DERIVED`, que o medidor exige (`censo_das_estradas_it.py:959-962`). O
   disparador da 1.ª onda (`bc5_big_collection.py`) gravava. Caminho mínimo: o `onda_web` passa a gravar
   `RAW` e `DERIVED` como o `bc5` (dono: quem mantém o `onda_web`), **ou** o medidor aceita `C4.OBSERVACOES` /
   `C4.COM_DERIVADO` (dono: `trava-medidores`, com teste e mutação). Uma das duas, não as duas;
2. **o lugar:** os dois `ONDA-WEB-ESTADO.json` têm de entrar no Git em `ferramentas/big_collection/` (decisão do
   coordenador; não copiei);
3. **o denominador:** o livro de estados do Curator e o livro de contratos do coletor, no Git, estão atrasados em
   relação ao vivo — 4 fontes fora das 716 e 2 sem contrato. Enquanto não forem actualizados, essas 6 não contam.

Com os três: **A iria de 98 para 103 (+5) e, com o denominador em dia, no máximo +11** (as 6 do ponto 3 só contam se tiverem contrato HTTP; NÃO SEI se têm) — e continuaria NÃO.

## 4 · As 4 chaves nos 9 itens novos da Sala

`data/derivados/TRAVA-POS-ONDA2/SALA-9-ITENS-NOVOS.json` (só metadados; o texto **não** foi lido, só o comprimento).

| chave | itens com valor | de que campo viria |
|---|---:|---|
| **cultura** | **0 / 9** | nenhum — a Sala não tem coluna de cultura; só dentro do envelope `fato`, que é `"NAO_SE_APLICA"` nos 9 |
| **região do FATO** | **0 / 9** | `fact_location` — existe, `NAO SEI` nos 9 (`fact_location_basis = NAO SEI`) |
| **fase** | **0 / 9** | nenhum — nem coluna, nem campo do contrato |
| **janela** | **0 / 9** | nenhum; o mais próximo é `fact_time` (um ponto, não um intervalo) — `NAO SEI` nos 9 |

Na Sala inteira (inventário completo re-corrido, `inventario-RESULTADO.txt`): **0 / 78** nas quatro. Os 9 são T5 (6),
T10 (2), T2 (1); textos de 3 984 a 27 475 letras. **0 consumidos** — a Intelligence nunca leu a Sala.

**Mudança face à SALA-PRONTA:** o **T2 entrou na Sala pela 1.ª vez** (IT-T2-034, 1 SIM). O risco «T2 corre e não
pousa por falta de régua» não se confirmou nesta corrida: há régua T2. T1 continua a 0 (nenhuma fonte T1 correu).

## 5 · Os 9 passos da D33 (caminho mínimo) — onde estamos

| | passo | estado |
|---|---|---|
| 1 | integrar os medidores corrigidos | **NÃO FEITO** — `c821094d` está fora da produção e da integração (só em `trava-medidores-v1` e `sala-pronta-v1`) |
| 2 | o critério A medir as 716 | feito **no ramo** dos medidores; não integrado |
| 3 | mapear cada fonte para classe real ou bloqueio | 98 de 716 (103 com as ondas, se o §3 for feito); **589 NÃO SEI** |
| 4 | reconciliar donos de RAW, checkpoint e rota | decididos pela Bíblia; **medidor dos donos ainda diz DUPLICADO** (C, E, H) |
| 5 | medidores determinísticos para B e K | **não existem** |
| 6 | persistência estruturada, tirar estado do Git, fechar o System Map | G, J, M = NÃO; **J piorou no vivo** |
| 7 | classificar e resolver os 21 do congelamento | classificados (`TRAVA-MEDIDORES-V1-OS-21.md`); **5 avanços proibidos por resolver**, 3 do dono, 1 por julgar |
| 8 | reexecutar os 14 critérios e as 5 condições | feito hoje (esta medição), com os medidores do ramo |
| 9 | mudar `COLLECTION_FOUNDATION_CLOSED` e a trava | **não** — nada provado para isso |

**O próximo passo com mais efeito:** 1 (integrar os medidores) + §3 (formato e lugar do registo da onda). Sem eles,
qualquer corrida nova continua invisível para a trava.

## 6 · O que NÃO foi feito

- a trava não foi editada; nada copiado para `ferramentas/big_collection/`;
- a cadeia do mapa não foi corrida neste ramo (M não re-medido);
- não li o texto de nenhum item da Sala;
- não corri os medidores de donos e do congelamento de novo (o código do ramo não mudou).
