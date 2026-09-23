# SOC5 · os bancos de teste que estavam ligados — prova um a um, e o que se desligou

Medido em 2026-09-23 às 15:09 (hora local), depois da tela azul das 12:50.

## Antes

**Processos `postgres.exe` vivos: 4** (e só 4 — os outros 6 diretórios com `postmaster.pid` que a
SOC4 listou eram RESTOS: o ficheiro ficou no disco, o processo já não existia).

| Cluster (`%TEMP%`) | Porta | Nasceu | Última linha no log | Bancos | Clientes ligados | Quem o abriu | Descartável? |
|---|---|---|---|---|---|---|---|
| `pg-prova-cli-2yfqob57` | 53231 | 14:01 | 14:09 | postgres, descartavel | 0 | `Bancada` de `provas/a_porta_cli_liga_o_banco.py` (prefixo); o processo que o lançou já não existe; 1 corrida `IT-T2-2026-09-23-170325-…` | **sim** |
| `pg-prova-cli-0l8wy4al` | 53260 | 14:02 | 14:09 | postgres, descartavel | 0 | idem; 1 corrida `IT-T2-2026-09-23-170331-…` | **sim** |
| `pg-prova-cli-_q7txj5l` | 56232 | 14:11 | 14:19 | postgres, descartavel | 0 | idem; 0 corridas | **sim** |
| `pg-prova-cli-nbb5yq0n` | 58674 | 14:38 | 14:46 | postgres, descartavel | 0 | idem; 0 corridas | **sim** |

Como se provou «descartável», um critério por coluna:
* **nome/porta**: servidor em `127.0.0.1`, porta aleatória, base `descartavel` —
  `guarda/banco_descartavel.e_descartavel()` = True nas 4 moradas;
* **dono**: diretório com o prefixo da `Bancada` das provas, no `%TEMP%`, binários do Postgres
  portátil (`orca/pgtmp`);
* **sessão**: o `cmd.exe` que o `pg_ctl` deixou tem pai que já não existe — quem o abriu morreu sem
  o desligar (órfão); 0 clientes ligados; sem atividade no log há 23 a 60 minutos.
* **Não é a Sala real**: nenhum ouvia 54329/54330 nem estava fora do `%TEMP%`. Nenhuma Sala real
  estava a correr nesta máquina neste momento (0 `postgres.exe` depois de desligar os 4).

Nenhum destes foi aberto pelas missões SOC1–SOC5 (os da SOC3 foram desligados no fim de cada ronda).

## O que se fez
`pg_ctl -D <cluster> -m fast -w stop` nos 4 (rc=0 nos 4). Os diretórios ficam no disco (prova);
apagá-los é outra decisão.

## Depois
* `postgres.exe` vivos: **0**; portas 53231/53260/56232/58674: fechadas.
* Memória livre: 7693 MB de 32.7 GB.

## Não tocados (só restos no disco, sem processo)
`pg-prova-cli-3idp8i2_`, `-dqzp64tl`, `-v06yipna` (13:05–13:06 de hoje, à volta da tela azul) e
`-dbrez5y3`, `-pe8af968`, `-tlni6qlv` (22/09). Contribuição para a tela azul: NÃO SEI — 4 clusters
parados ocupam pouca memória cada; não há prova de que tenham causado o erro.
