# NOITE-CONTINUA — a rodada 1 e as seguintes, sozinhas, esta noite (D86)

Para o coordenador lançar em background até às 19:35. Ficheiros em `auditoria-madrugada/`:
`NOITE-CONTINUA.sh` (lançador) e `noite_continua.py` (a lógica). O vivo é `dc0de726`.

```
nohup bash C:/Users/London1/auditoria-madrugada/NOITE-CONTINUA.sh > C:/Users/London1/auditoria-madrugada/NOITE-CONTINUA.out 2>&1 &
```

Saída: `auditoria-madrugada/NOITE-<AAAAMMDD-HHMM>/` com `NOITE.log`, `RESUMO-NOITE.md` e `.json`, e a saída
de cada passo (`R01-portao.txt`, `R01-backup.txt`, `R01-rodadas.txt`, `R01-prova-teto.txt`, `backup-R01/`).
Código de saída: 0 = a noite não parou; 1 = parou (o porquê está no RESUMO).

## ⚠️ O que esta noite vai realmente fazer: SÓ a R1

Medido com o plano instalado (`ONDA4-RODADAS/RODADAS-SO-PLANO.json`) e a janela real. As janelas das
R3–R15 «a abrir 19:40–19:53» são **antes** da R1. Mas **todas as R3–R15 têm edagricole.it** (e a R3–R5
também cia.it), que a R1 visita às ~20:00. Depois da R1, cada uma delas fica **ADIADA até 27/09 ~20:30**.
O script trata ADIADA como «ainda não», e não como falha: regista `ABRE_EM` e passa à seguinte. Numa só
noite, com este plano, corre 1 rodada. É a consequência de 15 fontes num só domínio. A PARTE B trata disto.

## O que faz, por rodada (a ordem do RODADA1-ROTEIRO)

| passo | o quê | PARA TUDO se |
|---|---|---|
| 0 (uma vez) | vivo = `dc0de726` e `rodadas.py` com `--rendimento` | outro commit |
| janela | pré-verificação só de leitura (livros das ondas + recibos VOZES/MICRO-PROVA/T6): a R1 **espera** até abrir (19:58:33 + 1 min; no máximo 150 min); as outras, se fechadas, ficam ADIADAS | — (ADIADA não é falha) |
| 1 | portão IT de consenso, `--sem-cache`, com `SINTONIA_EGRESSO_CACHE` **novo** por rodada | código ≠ 0 |
| 2 | backup da Sala (`provar_backup_da_sala.py`), com as `SINTONIA_SALA_*` no ambiente do próprio comando; a DSN é lida de `SALA_DSN.txt` e nunca impressa | `PROVA_VALE` ≠ true |
| 3 | `PARAR.flag` e espera **0 processos** do robô no SO (até 20 min) | o robô não pára |
| 4 | `rodadas.py --correr --rodada=N` com os argumentos do roteiro | a rodada não fica FECHADA (a não ser que feche a janela: ADIADA) |
| 5 | prova-teto independente (`provas/prova_teto_dominio.py`) | código ≠ 0 (FAIL ou NAO_SEI) |
| 6 | reconciliar a Sala, só SELECT (`PGOPTIONS` só leitura): `raw_asset` e `sala_de_espera` das corridas = delta da Sala | não bate |
| 7 | religa o robô (apaga PARAR.flag, lança o supervisor como no cutover) e confere **exatamente 1** supervisor | ≠ 1 |

O robô é religado **depois de cada rodada**, para não ficar parado horas. Em qualquer paragem, o robô é
religado antes de sair (o `finally`). No fim: `RESUMO-NOITE.md` com fontes (correram), pedidos,
máximo por domínio, docs novos e a Sala antes e depois, por rodada.

## Ensaio a seco (0 rede), 26/09 ~18:00

Cópia de `dc0de726` com os 17 livros vivos copiados (só leitura) e a fila esvaziada na cópia. Robô
**simulado**: nenhum processo tocado. Todo o curl foi para um servidor local que conta; o Python ficou
com proxy morto. Resultados em `auditoria-madrugada/NOITE-SECO/`.

| cenário | o que se provou | tentativas de rede |
|---|---|---|
| S1: agora (janela fechada), sem espera | passo 0 PASS; as 14 rodadas ADIADAS com o `ABRE_EM` certo; código 0; resumo escrito | **0** |
| S2: hora simulada 20:05 (janela aberta) | o portão **real** sem rede falha → PARA TUDO **antes** do backup e do robô; robô religado; código 1; o RESUMO diz `PARADA (R01 PORTAO_IT)` | 1, e foi para o servidor local (`ip-api.com`) |
| prova-teto (dados reais da 3.ª onda) | PASS, 38 corridas, 167 pedidos | 0 |
| reconciliar (Sala real, só SELECT, 3.ª onda) | **BATE**: raw 76 = delta 76; sala 14 = delta 14; collection_run 31 | 0 |
| deteção do robô (vivo, só leitura) | encontra o supervisor 30824, o mesmo do `--estado` | 0 |

**Não ensaiado a seco (dito):** o backup real (restaura numa base descartável: é pesado e precisa da
LOCK), parar e religar o robô de verdade, e uma rodada inteira pela rede. Estes três passos já correram
na 3.ª onda pelo roteiro manual. O script usa os mesmos comandos.

## EM PALAVRAS SIMPLES

- É um programa que você liga e esquece. Ele espera dar 19:58, confere a VPN, faz backup da Sala,
  pausa o robô, roda a rodada 1, confere as visitas por outro caderno, confere a Sala e liga o robô de
  novo.
- Se qualquer coisa der errado, ele para tudo, liga o robô e deixa um resumo escrito.
- Esta noite só dá para rodar a **rodada 1**. As outras 13 repetem o site edagricole.it, que só pode ser
  visitado de novo depois de 24 horas. O programa entende isso e anota «volta amanhã», sem tratar como erro.
- Testei sem visitar nenhum site: ele parou nos lugares certos.
