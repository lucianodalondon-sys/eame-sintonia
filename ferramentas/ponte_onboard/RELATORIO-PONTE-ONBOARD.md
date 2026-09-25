# PONTE-ONBOARD — a fonte pronta do Curator passa a chegar ao coletor

Ramo `ponte-onboard-v1`, a partir da produção `servico-20260923-0923` @ 7cdb7ea4. **Não instalado.** Missão: `auditoria-madrugada/missao-ponte-onboard.txt`.

## Em palavras simples

**Antes:** uma fonte aprovada pelo Curator ficava à porta do coletor. **Entravam 0.** Por duas razões:
1. **O passo que a escreve na tabela do coletor não era chamado por ninguém.**
2. **O instrumento que prova a rota lia o contrato errado.** Lia a versão guardada no Git, e o bot escreve no disco sem guardar no Git: em 17 fontes, 14 tinham no Git um contrato diferente ou nenhum.

**Agora:**
- o instrumento prova **o contrato em disco**, que é o que o robô vai usar, e escreve na prova a **impressão digital** desse contrato (sha256) e a **hora**;
- o supervisor do bot chama o passo de entrada **sozinho**. O passo só escreve a fonte na tabela se:
  - a impressão provada for **igual** à do contrato de agora, e
  - a prova tiver **no máximo 7 dias**.

  Sem prova recente, não entra, **como hoje**;
- as provas feitas em rondas (uma fonte por domínio de cada vez) **juntam-se** (`--juntar`), em vez de a última apagar as anteriores.

**Ensaio numa cópia fiel do vivo** (livros de agora + este código): de **0** para **17** fontes no coletor. Os contratos do coletor passaram de 206 para 223, e as 17 ficaram colhíveis. Os livros do Curator **não mudaram** (sha256 igual). Desfazer é repor um ficheiro, e o sha256 volta ao de antes.

**Os 3 boletins (Campania, APOL, ARPAV): só plano.** São PDF, e a régua de promoção de hoje só aprova páginas HTML (`ready_split.py:133-134`). O Curator não aprovaria um PDF nem com contrato. O plano está em `PLANO-BOLETINS-READY-LEGACY.md`.

## O que mudou (ficheiro:linha)

| O quê | Onde |
|---|---|
| a impressão digital única (SOURCE_ID + OUTPUT_TYPE + ACQUISITION: o que vai para a tabela do coletor) | `curadoria/sha_do_contrato.py` (novo) |
| o canário lê o **disco** por omissão; Git só com `ID@ref` escrito por extenso; grava `CONTRATO_SHA256`, `PROVADO_EM` e `CONTRATO_LIDO_DE`; `--juntar` | `medidas/canario_rotas_elegiveis.py` (`_contratos_de`, `juntar`, `main`; antes era a linha 177) |
| o onboarding exige impressão igual (substitui a comparação só de INDEX_URL e LINK_PATTERN, que deixava passar outro `MAX_TARGETS`) e prova ≤ 7 dias; a linha da tabela leva a impressão; escrita atómica | `curadoria/onboardar_rotas_provadas.py` (`planear`, `linha_da_tabela`, `aplicar`) |
| **dono único do onboarding: o supervisor do bot**, a cada volta, por `onboardar_se_mudou` (corre quando a prova muda ou de 10 em 10 min; sem rede; um erro fica no diário e não derruba o supervisor) | `curadoria/supervisor.py` (`_loop`: `_hook_onboarding`) e `onboardar_rotas_provadas.py` (`onboardar_se_mudou`) |

**Porquê o supervisor, e não a ponte nem o alimentador:**
- A tabela que o coletor lê vive na lane do **bot**. A Big Collection corre com cwd = árvore do bot (`ferramentas/big_collection/bc5_big_collection.py`, linha 4).
- A ponte (`ponte_automatica.py`), por desenho, **só lê** a lane do bot.
- O alimentador (`gatilho_discovery.talvez_alimentar`) sai logo com QUEUE_OK quando a fila tem trabalho (`gatilho_discovery.py:429`). No vivo havia 3457 tarefas, por isso ele nunca correria.

## Provas

- **Testes:** `tests/test_canario_rotas_contrato_certo.py` (6, novo) e `tests/test_onboardar_rotas_provadas.py` (de 11 para 29). O caso medido dos **14/17 contratos trocados** é reproduzido com os contratos reais do vivo (`tests/fixtures/ponte_onboard_17_contratos.json`, HEAD e disco a 25/09). Sem rede: o `provar` e o resto do supervisor são dublos.
- **Mutação:** `ferramentas/ponte_onboard/mutacao.py` → **11/11 mortos** (`MUTACAO.json`). ⚠️ Na 1.ª corrida o M8 («o supervisor não chama o gancho») **sobreviveu**: o meu teste procurava o texto `_hook_onboarding()`, que também aparece na linha que define a função. Troquei-o por testes que correm o `_loop` verdadeiro do supervisor com dublos.
- **Regressão:** os 13 módulos de teste já existentes que tocam no supervisor, no onboarding ou no canário. 156 testes, **OK na produção 7cdb7ea4 e OK neste ramo**, 4 skipped nos dois: **0 falhas novas**. ⚠️ Esta suíte do curador lança um worker real que vai à rede; correu com a VPN IT (portão PASS).
- **Ensaio** (`ENSAIO-1..5`), numa cópia fiel do vivo em `C:/rend/ensaio-onboard`: `git archive` deste ramo + os livros do vivo copiados por cima, com sha256 em `ENSAIO-5`.
  1. Antes: `ENTRA=0 FICA=28` (20 sem canário, 3 provas antigas sem impressão, 3 UNKNOWN, 2 CAPABILITY).
  2. Canário, com `--juntar`, nas 28, em 3 rondas (20 + 5 + 3; ≤ 1 fonte por domínio por ronda; portão de consenso PASS IT antes e depois de cada ronda): **21 ROUTE_PROVEN, 4 CAPABILITY_BLOCK, 3 UNKNOWN**.
  3. O gancho do supervisor, uma vez: **`ONBOARDOU`, 17 escritas**. 2.ª volta: `NADA_MUDOU`.
  4. Depois: `ENTRA=0 FICA=11`. As 4 provadas que ficaram de fora são **duplicadas** de fontes já contratadas (IT-T2-056, IT-T2-106, IT-T7-100, IT-T8-068). É decisão de identidade, e a regra antiga mantém-se.
  5. sha256: **só `regras/italy_contracts_onboarded.json` mudou** (856f833f → 6255cd27). LIFECYCLE-LEDGER e italy_contracts_curator ficaram iguais. **Desfazer** = repor o ficheiro, e volta a 856f833f (206 contratos).

## O que isto NÃO faz, e é preciso saber

- **O canário continua a não correr sozinho.** O supervisor só onboarda o que tem prova recente. Depois de instalar, alguém corre as rondas do canário **uma vez** (comandos no plano de instalação), e a partir daí as provas valem 7 dias. Ligar o canário ao ciclo (tarefa do worker, com rede e cortesia) é o passo seguinte natural. **Não o fiz.**
- As 17 provam **rota** (abrir uma notícia com corpo), não **SIM**. 5 são T12 e 1 é T8, sem régua. As T2 das ARPA não têm ligação agrícola no item provado.
- As provas antigas do vivo não têm impressão. Por isso, até o canário ser refeito, **nenhuma fonte nova entra**. É a regra a funcionar: sem prova do contrato de agora, não entra.

## D41.3 (regra nova de 25/09: cópia do robô começa com rede fechada)

- **Este ensaio cumpre-a:**
  - **não correu o robô** (worker/supervisor) na cópia;
  - a rede foi só a do canário de rotas, **na lista filtrada** das 28 do `FICA`, com no máximo 4 pedidos por fonte e **1 fonte por domínio por ronda** (≤ 5 por domínio, D38), e o portão de consenso PASS IT antes e depois;
  - o gancho do onboarding **não usa rede**.
- **Confissão de uma corrida anterior** (REND, 24/09 à tarde, antes da D38 e da D41.3): na banca `C:/rend/banca` corri o `revisar_ready.py` da R1 com **rede aberta**.
  - O worker processou 142 tarefas, **todas das 40 fontes pedidas**, e 0 de outras (medido no log).
  - Mas 6 dessas fontes são do mesmo domínio (terraevita.edagricole.it), por isso **quase de certeza passou de 5 pedidos por esse domínio** nessa corrida.
