# PROVA-ROTA-CICLO — a prova de rota passa a correr sozinha

Ramo `prova-rota-ciclo-v1`, a partir de `ponte-onboard-v1` @ 7e3fed2c. **Não instalado.** Missão: `auditoria-madrugada/missao-prova-rota-ciclo.txt`.

## Em palavras simples

**Antes:** a prova de que a rota de uma fonte funciona só corria quando alguém a mandava correr. Sem prova, a fonte não entra no coletor.

**Agora**, o supervisor do bot faz sozinho, de 30 em 30 minutos:
1. vê que fontes **aprovadas** ainda não têm prova recente (até 7 dias) **do contrato de agora**;
2. escolhe até **8**, e **nunca duas do mesmo site** na mesma rodada. É a regra dos 5 pedidos por site: o canário faz no máximo 4;
3. pergunta ao **portão de consenso** se a saída é pela Itália. **Se não for, a rodada não sai**, e fica escrito porquê;
4. corre o canário **num processo à parte**, para o supervisor não ficar à espera da rede. Uma rodada presa há mais de 30 min é terminada.

A seguir, o passo da missão anterior (onboarding) mete as fontes provadas no coletor.

**Hoje, com os livros do vivo, sem rede:** 44 fontes precisam de prova. A 1.ª rodada leva 8, de 8 sites diferentes. As 44 fazem-se em ~6 rodadas, **pouco mais de 3 horas**, sem ninguém.

## ⚠️ Incidente causado por mim nesta missão (25/09, 08:01Z)

- **O que aconteceu:** na 1.ª versão, o supervisor ia sempre à rede. Os testes que já existiam para o ciclo do supervisor (os meus, da PONTE-ONBOARD) correram-no **sem dublê** para este passo novo. O passo verdadeiro correu: leu os livros desta árvore, perguntou ao portão (**PASS IT**) e **lançou canários reais — 6, ao mesmo tempo**, um por cada volta de teste. Todos começaram pela mesma fonte, IT-T2-056 (arpae.it).
- **Estrago:**
  - o **arpae.it recebeu robots + entrada + item de até 6 processos em ~1 minuto**. São cerca de 6 a 24 pedidos, e o teto D38 é 5;
  - houve tentativas de ligação falhadas a mais 2 sites (IT-T5-101 e Coldiretti IT-T7-053);
  - **parei os 6 processos às 08:01:57Z**;
  - nenhum ficheiro rastreado foi escrito (o canário só escreve no fim).
  - Registo: `INCIDENTE-20260925T0801Z-canarios-dos-testes.log` (sha256 a7e58e85…).
- **Conserto: a rede passou a ser opt-in.** `_loop` e `supervisionar` têm `prova_de_rota=False` por omissão, e **só `main()`** a liga. `main()` é o serviço, que o vivo arranca com `py curadoria/supervisor.py`. `--sem-prova-de-rota` desliga.
  - Todos os testes que correm o ciclo têm um **fio de tropeçar**: o lançamento e o portão verdadeiros rebentam se forem chamados.
  - Os avisos «subprocess still running» passaram a erro (`-W error::ResourceWarning`).
  - Depois de cada corrida de testes, mutação e regressão confirmei **0 canários a correr** e nenhum registo criado.

## O que mudou (ficheiro)

| O quê | Onde |
|---|---|
| quem precisa de prova, a rodada (1 por domínio, ≤ 8), o portão, o lançamento, o intervalo, o tempo máximo | `curadoria/prova_rota_ciclo.py` (novo) |
| o supervisor chama a prova e **depois** o onboarding, a cada volta; a prova só se `prova_de_rota` for verdadeira | `curadoria/supervisor.py` (`_loop`, `supervisionar`, `main`) |

**Domínio:** «domínio registável», a **mesma regra** da ONDA2-G3 (`coleta/italy_pilot_collect.mjs::dominioRegistavel`, no ramo `onda2-g3-v1`), copiada com a mesma lista de sufixos regionais. Há um teste que compara as duas quando o coletor instalado a exportar. Hoje fica `skipped`, porque a G3 ainda não está instalada.

**Porque não o contador da G3:** vive no coletor (Node), noutro processo. Aqui vale **1 fonte por domínio por rodada**.

**Intervalos declarados:**
- RONDA_INTERVALO = 30 min (conta do **fim** da rodada, ou da tentativa que não saiu);
- RONDA_MAX_FONTES = 8;
- RONDA_TEMPO_MAXIMO = 30 min;
- a prova vale 7 dias (`onboardar_rotas_provadas.PROVA_MAX_IDADE`);
- uma prova recente que falhou também espera os 7 dias, ou uma mudança de contrato.

## Provas

- **Testes:** `tests/test_prova_rota_ciclo.py` (27, novo). Cobrem: rodada sem VPN não sai; domínio repetido espera; só elegíveis; prova de outro contrato ou velha volta a provar; nunca provadas primeiro; em curso, acabada, presa e reinício do supervisor; portão só aceita PASS; ordem prova → onboarding; por omissão, sem rede. Com os da PONTE-ONBOARD: **62 testes OK**, sem rede.
- **Mutação:** `mutacao.py` → **13/13 mortos** (`MUTACAO.json`), incluindo «o loop vai à rede por omissão».
- **Regressão:** os mesmos 13 módulos da PONTE-ONBOARD. **156 OK, 4 skipped**, igual à produção: **0 falhas novas**.

## O que isto NÃO faz

- Não mede SIM. Prova **rota**, como antes.
- Não junta o contador por domínio com o da onda de coleta. Se uma onda da Big Collection e uma rodada de prova baterem no mesmo site ao mesmo tempo, os pedidos somam-se. **Não medi quanto.** A solução é o livro da onda (`SINTONIA_TETO_ONDA`, G3) ser lido também aqui, depois de a G3 estar instalada.
