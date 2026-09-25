# MICRO-PRONTO — revalidar os 3 boletins e a ponte Curator → coletor

25/09/2026, madrugada. Tudo foi feito em **cópias** do vivo: `git archive` do bot + os livros do disco copiados por cima, com o sha256 em `medidas/micro-pronto-copia*-livros.sha256`. **Nada mexeu no vivo.** A rede passou sempre pelo portão de consenso do vivo (PASS IT antes e depois de cada ronda), com no máximo 1 fonte por domínio por ronda e 4 pedidos por fonte.

## Em palavras simples

**1. Os 3 boletins não conseguem ser revalidados pelo caminho oficial, e isto não é defeito deles.**
- São fontes antigas do piloto. O contrato delas foi escrito à mão **só no coletor**, e o Curator não as conhece.
- O caminho oficial começa com «validar a rota» e pára logo: «sem contrato».
- A seguir, o reparo tenta escrever um contrato e recusa: não tem nenhum endereço de partida.
- **Resultado: não passam. Ficam «não rodou» na micro.**
- ⚠️ **Não correr o comando oficial no vivo para estas 3.** Tiraria-as de READY_LEGACY e deixava-as em CONTRACTED_CANARY_FAILED, sem ganho nenhum.

**2. A ponte funciona, mas leva as fontes para o sítio errado.**
- Desde a 01:45: 64 travessias e 104 contratos importados. Mas vão para os livros da própria ponte (`ponte-viva`), e **não para a tabela do coletor**.
- O passo que põe a fonte na tabela do coletor existe (`onboardar_rotas_provadas.py`). **Ninguém o chama.** E ele exige uma prova de rota que ninguém refaz desde 24/09.
- Na cópia, com esse passo feito: **17 fontes entrariam no coletor** (hoje entram 0).

**3. E há uma armadilha no meio.**
- O instrumento que prova a rota lê os contratos do **Git**, não do disco.
- O bot **escreve no disco e não faz commit**. No vivo, o ficheiro em Git tem 574 fontes e o disco 762. Das 17, **só 3** têm no Git o mesmo contrato que o disco.
- Corrido no vivo tal como está, o instrumento provaria o contrato errado em 14 de 17.

**Para a micro, isto quer dizer:** das 6 fontes da lista V2, hoje **só a myfruit corre**. Previsão: ~1 SIM em 3, ou seja ~40% (0 a 3). As 3 de boletim ficam «não rodou». As 2 da R1 (IT-T3-023, IT-T7-049) ainda não estão READY no vivo.

## 1 · Revalidar READY_LEGACY: o caminho canónico e onde pára

| Passo | Ficheiro:linha | Resultado na cópia (vivo 7cdb7ea4 + livros) |
|---|---|---|
| tirar de READY e remedir | `curadoria/ready_split.py:291` `remedir()` → CANARY_PENDING + VALIDATE_ROUTE | feito (só na cópia) |
| validar a rota | `curadoria/worker.py` (VALIDATE_ROUTE) com `_contratos()` = `worker.py:93`, que lê **só** `italy_contracts_curator.json` | **BLOCK «sem contrato»** nas 3 |
| o gatilho manda reparar | `curadoria/gatilho_discovery.py:264` «CANARY_PENDING sem contrato → REPAIR_CONTRACT» | enfileirado nas 3 |
| reparar o contrato | `curadoria/worker.py:494-498` `etapa_repair_contract`: precisa de contrato do Curator **ou** de alocação HTML com URL (`_contrato_do_molde`, ~`worker.py:471`) | **FAIL `REPARO_RECUSADO: SEM_IDENTIDADE`** nas 3 → CONTRACTED_CANARY_FAILED |

**Veredicto por fonte, pelas regras atuais: IT-T3-002 NÃO · IT-T3-010 NÃO · IT-T2-002 NÃO.** Porquê: não têm contrato no Curator.

**Comando exato para o vivo: NÃO HÁ nenhum que funcione hoje.** O que existe (`ready_split.remedir`) só as tirava de READY. O passo que falta é **código**: o Curator não sabe ler um contrato que só existe no coletor. Ou o reparo parte do `CANONICAL_ENTRY_URL` do contrato do coletor, ou estas 3 ganham contrato no Curator por BUILD_CONTRACT. Mesmo assim, a régua de promoção (4 passos com item HTML aberto) foi feita para HTML: um PDF por zona (ARPAV) não sei se passa.

Provas: `medidas/micro-pronto-revalidar-boletins.json` (antes/depois, passos do worker) · `medidas/micro-pronto-ciclo-completo-boletins.json` (as transições até SEM_IDENTIDADE).

## 2 · A ponte Curator → coletor, medida no vivo (só leitura)

`ponte_automatica.py`, a correr de `ponte-viva` @ 84c235da. Estado SAUDAVEL, 7074 voltas.

- **Desde a 01:45 (04:45Z até 06:00Z):** 64 travessias, 328 transições, 189 provas e **104 contratos importados**. O portão *da ponte* passou de 37 para 49 ELIGIBLE. Entraram 12, entre elas IT-T12-024, IT-T12-117, IT-T2-050, IT-T3-045 e IT-T7-172. Não saiu nenhuma. (O portão do *bot* passou de 38 às ~02:00 para 56 às ~06:00.)
- **Para onde vão:** para os livros da `ponte-viva` (`italy_contracts_curator.json` de lá, `ponte_automatica.py:139/157`), **não** para `regras/italy_contracts_onboarded.json`. Essa é a tabela que o coletor lê (`regras/italy_contracts.mjs:~577`).
- **O passo que falta:** `curadoria/onboardar_rotas_provadas.py` é **o** caminho Curator → coletor (docstring: «ELEGIVEL SEM CONTRATO NAO E UMA DECISAO QUE FALTA. E UMA PONTE QUE FALTA»). Só escreve com `--aplicar`, e exige 3 coisas juntas:
  1. ELIGIBLE;
  2. sem contrato no coletor;
  3. `ROUTE_PROVEN` em `curadoria/ROTAS-ELEGIVEIS-V1.json`.

  **Não é chamado pela ponte nem pelo supervisor** (só por dois scripts manuais). E o `ROTAS-ELEGIVEIS-V1.json` do vivo é de **24/09 às 00:16**, antes da R1.
- **Medido na cópia:**
  - sem prova nova: `ENTRA=0 FICA=27` (19 «SEM_CANARIO»);
  - com a prova de rota refeita para essas 19 (3 rondas, `medidas/canario_rotas_elegiveis.py`): **17 ROUTE_PROVEN, 2 CAPABILITY_BLOCK** (IT-T12-104, IT-T3-045), e depois **`ENTRA=17`**.
- **A armadilha:** `medidas/canario_rotas_elegiveis.py:177` lê os contratos por `git show HEAD:curadoria/italy_contracts_curator.json`. O bot não faz commit: no vivo, o HEAD tem 574 fontes e o disco 762. Das 17, só 3 têm no HEAD o contrato igual ao do disco. Na cópia contornei com um repositório local cujo HEAD é o disco (sha256 igual, contando só LF).

### Comandos para o vivo (decisão e execução do coordenador; bot quieto; um escritor)

**Antes de tudo:** o canário tem de ler o disco. Em `medidas/canario_rotas_elegiveis.py:177`, ler `RAIZ/curadoria/italy_contracts_curator.json` quando `ref` for `HEAD` (ou um `@DISCO`). Sem isto, não correr o passo 1: provaria o contrato errado. **Não fiz esta mudança.**

1. A prova de rota, em rondas de 1 fonte por domínio (≤ 4 pedidos por fonte):
   ```
   py medidas/canario_rotas_elegiveis.py --fontes=IT-T12-024,IT-T12-104,IT-T12-117,IT-T12-129,IT-T12-130,IT-T2-032,IT-T2-037,IT-T2-050,IT-T3-045,IT-T5-160,IT-T5-167,IT-T5-185,IT-T7-172,IT-T8-062 --escrever
   py medidas/canario_rotas_elegiveis.py --fontes=IT-T2-145,IT-T12-131,IT-T5-186 --escrever
   py medidas/canario_rotas_elegiveis.py --fontes=IT-T2-146,IT-T5-187 --escrever
   ```
   ⚠️ Cada `--escrever` **reescreve** o `ROTAS-ELEGIVEIS-V1.json`, não acrescenta. As rondas têm de ser juntadas, e com as linhas antigas das outras 8 (UNKNOWN/DUPLICADA), antes do passo 2. Foi o que fiz na cópia, à mão.
2. `py curadoria/onboardar_rotas_provadas.py` → na cópia deu **ENTRA=17**. Conferir que dá o mesmo.
3. `py curadoria/onboardar_rotas_provadas.py --aplicar` → escreve as 17 linhas em `regras/italy_contracts_onboarded.json`.

Provas: `medidas/micro-pronto-onboardar-antes.txt` (ENTRA=0) · `medidas/micro-pronto-rotas-elegiveis-3rondas.json` · `medidas/micro-pronto-onboardar-depois-do-canario.txt` (ENTRA=17).

## O que isto não prova

- Que as 17 **rendem SIM**. É prova de **rota** (abre um item com corpo), não de régua. Das 17, 5 são T12 e 1 é T8, sem régua. As T2 das ARPA não têm ligação agrícola no item provado.
- Que o `ROTAS-ELEGIVEIS` juntado à mão é o que o dono do instrumento quer. Ele não sabe juntar rondas.
- O mapa não foi regerado (a fila do LOCK-PESADO continua cheia; o coordenador disse que não bloqueia).
