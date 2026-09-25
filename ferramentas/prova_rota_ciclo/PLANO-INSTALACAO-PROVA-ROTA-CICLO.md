# Plano de instalação — PROVA-ROTA-CICLO (depois da MICRO; não bloqueia; quem instala é o coordenador)

Este ramo **contém a PONTE-ONBOARD** (a base é 7e3fed2c). Instala-se as duas de uma vez, ou esta por cima da PONTE-ONBOARD já instalada.

## 0 · Antes
- O vivo em 7cdb7ea4, ou já com a PONTE-ONBOARD. Nenhum ficheiro do writeset sujo no vivo: medido para a PONTE-ONBOARD, e esta só acrescenta `curadoria/prova_rota_ciclo.py` e muda `curadoria/supervisor.py`.
- A VPN IT ligada. Sem ela, as rodadas não saem: ficam `RONDA_NAO_SAIU` no diário, e isso não é erro.
- Guardar a tabela do coletor (`regras/italy_contracts_onboarded.json`) e o `curadoria/ROTAS-ELEGIVEIS-V1.json`, com sha256.

## 1 · Instalar (bot quieto)
```
git fetch origin prova-rota-ciclo-v1
git merge --ff-only origin/prova-rota-ciclo-v1
```
Reiniciar o supervisor **pelo arranque normal** (`py curadoria/supervisor.py`, que liga a prova de rota).

## 2 · Ver acontecer (sem comandos)
No diário do supervisor, por esta ordem:
1. `PROVA_ROTA` / `RONDA_LANCADA` com 8 fontes, depois `RONDA_ACABOU`;
2. `ONBOARDING` / `ONBOARDOU` com as que entraram;
3. de 30 em 30 min, a rodada seguinte, até `SEM_FONTES_A_PROVAR`.

O que o canário escreve está em `curadoria/PROVA-ROTA-CICLO.log`.

## Desligar sem desinstalar
Arrancar o supervisor com `--sem-prova-de-rota`. Fica só o onboarding (sem rede), como na PONTE-ONBOARD.

## Desfazer
- Repor `ROTAS-ELEGIVEIS-V1.json` e a tabela do coletor a partir do corte.
- Código: `git reset --keep <sha de antes>`, e reiniciar o supervisor.
- Nenhum livro do Curator é escrito por este passo.
