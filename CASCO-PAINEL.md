# CASCO-PAINEL (D78) — o painel de operação, os 16 originais, e o contrato da Intelligence EXPERIMENTAL

- **Ramo:** `casco-painel-v1`, a partir de `casco-leitura-v1` (`b83b930f`, que já contém o vivo `83de0ccd`).
- **Tudo só de leitura, sem nota:**
  - sem rede e sem coleta;
  - o vivo não foi tocado: `supervisor.py --estado` correu lá sem escrever `.pyc`, e os ficheiros
    alterados da árvore do vivo eram 100 antes e 100 depois;
  - nenhum RAW foi alterado.
- **A Sala real foi lida uma vez**, numa transação `begin read only`. O próprio banco respondeu
  **`transaction_read_only = on`** dentro dela: é a prova que o D9 pede, e não só o `PGOPTIONS`.

## 1 · O PAINEL DE OPERAÇÃO

**Onde está:** no mesmo portal, em `http://localhost:8899/portale.html?sala=local#painel`, com a voz de
menu «Pannello operativo · sola lettura».
- Os dados vêm de `italia-portale/audit/casco/painel-operacao.mjs`, que escreve `italy-painel.local.js`
  (fora do Git e do deploy).
- Esse ficheiro só é pedido com `?sala=local`. Sem isso, o painel mostra só o aviso: 0 blocos
  (`painel-sem-dados.png`).

**Cada número traz a fonte ao lado** (ficheiro + sha256 + data), medida às 06:33–06:47 UTC de 26/09.

| Bloco | O que mostra | De onde vem |
|---|---|---|
| Ondas feitas | 5 ondas com datas, fontes que correram, estado por fonte, pedidos, domínios, máximo por domínio e Sala antes → depois | `BC5-BIG-COLLECTION-1A-ONDA.json` (vivo) + os 4 `ondas/*/ONDA-WEB-ESTADO.json` |
| Coorte congelada | 64 dentro e 17 fora, com o porquê | `COORTE-BIG-COLLECTION-V1.json` do vivo (`83de0ccd`) |
| Serviço do coletor | estado, worker, fila, batimento, reinícios | `supervisor.py --estado` (`SUPERVISOR-ESTADO.json`) |
| Pedidos por domínio | a última onda (ONDA3): 16 de 39 domínios, e quais estão no teto de 5 | `ONDA-WEB-ESTADO.json` da ONDA3 |
| Sala por dia | 18/09 → 25/09: 3 → 94 | leitura só-leitura da Sala (`LEITURA-SALA-PAINEL.json`) |
| Cobertura tempo/lugar | FACT_TIME 22 · PUBLICATION_TIME 46 · SOURCE_LOCATION 5 · FACT_LOCATION 19, de 94 | idem |
| Intelligence | **BLOQUEADA**; critérios da trava; EMENDA EXP-D78 (`db4bd022`, proposta, à espera das 2 assinaturas) | `TRAVA-DA-INTELIGENCIA.json` (vivo) + Git |
| D1–D10 | o que cada um é, e o estado de cada um | a lista está em `pergunta-emenda-exp-d78.txt`; o estado vem do **Git** |
| O que falta | as 4 condições da próxima onda, cada uma com o seu estado | regra do bot Luciano (23:17), estados medidos |

**As ondas medidas:**

| Onda | Quando | Correram | Pedidos | Máximo por domínio | Sala |
|---|---|---|---|---|---|
| 1.ª (BC5) | 24/09 09:05–09:12 | 18/18 | 54 | 16 ⚠️ (o teto D38 ainda não existia) | 66 → 69 |
| MICRO-V3 | 25/09 08:03–08:08 | 6/6 | 30 | 5 | 69 → 71 |
| ONDA2 | 25/09 08:12–08:25 | 21/28 (FAILED 1, teto 7) | 79 | 5 | 71 → 78 |
| MICRO-VERIF | 25/09 18:43–18:50 | 5/5 | 24 | 5 | 78 → 80 |
| ONDA3 | 25/09 19:34–19:58 | 38/64 (teto 26) | 167 | 5 | 80 → 94 |

**D1–D10:**
- D1–D4, D6, D7 e D8 (lado Intelligence): o **conserto está declarado** no ramo `int-consertos-v1 @ 60faa7cb`.
- D9 e D10 (lado Collection): o **conserto está declarado** no ramo `sala-leitura-v1 @ db02875c`.
- **Nenhum está no vivo.**
- D5 não é defeito: a própria lista diz que está correto.
- ⚠️ «Declarado» quer dizer que o commit nomeia o defeito. **Não corri os testes desses ramos.**

**O que falta para a próxima onda:**

| Condição | Estado |
|---|---|
| ✗ FECHAR-ONDA3 = PASS | «FECHADA, com 1 FAIL (C2) e 2 itens a corrigir na Sala» (FECHO-ONDA3.md) |
| ✓ C9 instalado no vivo | `83de0ccd` está no vivo |
| ✗ C2 (juiz capa/matéria) | o conserto está no ramo `c2-juiz-v1 @ b91e7661`, **não instalado** |
| ✗ VPN / teto / backup / robô parado | mede-se no disparo. Agora: serviço RUNNING, worker IDLE, portanto o robô **não** está parado |

## 2 · OS 16 ORIGINAIS: ONDE ESTÃO, COM PROVA

**Resposta: estão nesta máquina, os 16.** Foram guardados, e a Sala diz isso:
- `raw_asset.preserved = true`;
- `storage_object` com o **mesmo** caminho e o **mesmo** sha256.

Mas o ficheiro sumiu desse caminho (`armazem/XX/...`). Pela memória do projeto, a suíte de testes já
apagou `XX/` uma vez.

**Onde encontrei cópias byte a byte iguais** (mesmo tamanho **e** mesmo sha256; `procurar_16.py`, só leitura):
- **15** no armazém do próprio coletor, na árvore do vivo: `data/collection-store/italy/<SID>/<item>/v1_<sha>/…`.
  - 5 destes estão também no backup `sintonia-acervo-backup/lote-76-XX-20260922/`.
- **1** (o boletim ARIF N37 de 09/09, IT-T3-008) em `C:/sc-hot/data/collection-store/…` e no worktree `it-trunk-v1`.

**Na vista da Sala:**
- os 16 aparecem agora como «cópia IDÊNTICA noutro caminho (sha256 conferido)»;
- o link aponta para a cópia;
- o gerador **conferiu de novo** o sha256 antes de fazer o link.

Resultado: 78 conferidos no caminho da Sala, 16 noutro caminho, **0 não encontrados**.

**Nada foi copiado para o caminho da Sala.** Repor os ficheiros no armazém é uma decisão do dono da Sala.

## 3 · O CONTRATO DA INTELLIGENCE EXPERIMENTAL (só o contrato e um exemplo vazio)

- `italia-portale/audit/casco/INTELLIGENCE-EXPERIMENTAL-CONTRATO.json` (`CASCO_ENTRADA_INTELLIGENCE_EXPERIMENTAL/1`):
  - o cabeçalho exige `MARCA = EXPERIMENTAL`, `PUBLICO = NAO_PARA_CLIENTE`, a emenda aprovada e a fotografia da Sala;
  - cada item traz a chave da Sala, o estado, a conclusão, a **base**, e `USOU_PUBLICACAO_COMO_DATA_DO_FATO = false`;
  - o casco **só mostra**, com a faixa «EXPERIMENTAL · NÃO PARA CLIENTE», ao lado dos 4 campos e nunca no lugar deles;
  - não pontua, não ordena, não funde.
- `INTELLIGENCE-EXPERIMENTAL-EXEMPLO-VAZIO.json`: um cabeçalho válido e **0 itens**.
- O gerador da Sala aceita `--intel=<ficheiro>`:
  - recusa o ficheiro inteiro se o cabeçalho estiver errado;
  - recusa um item sem base, que use a publicação como data, ou cuja chave não exista na Sala.
- Com o exemplo vazio, a vista mostra **94 NÃO_EXECUTADA**, porque nada foi inventado.

## Limites
1. **A lista dos D1–D10** é a da pergunta do coordenador ao bot Luciano (02:05). O **estado** vem do
   Git. Os **testes** dos ramos de conserto não foram corridos aqui.
2. **O contrato da trava diz `MEDIDO_EM 2026-09-08`.** É o que o ficheiro tem, e o painel mostra a data tal como está.
3. **«Robô parado» e «VPN»** só se medem no disparo da onda. O painel não finge que já estão medidos.
4. **Pedidos por domínio:** mostro 16 dos 39 da ONDA3 (os de mais pedidos), e o painel diz isso.
5. **O portão `link-asset.mjs` continua sem correr nesta máquina** (falta o playwright-core). O
   `deploy-surface.mjs` deu 0 problemas no ramo anterior.
6. **Mapa: não corrido** (LOCK-PRIORIDADE a favor da INTEGRA-NOITE). É PRONTO-SEM-MAPA.

## Provas (fora do Git, `C:/Users/London1/sintonia-sala-italia/casco/painel/`)

| Ficheiro | sha256 | O que é |
|---|---|---|
| `prova/painel-it.png` | `845dc276…` | captura do painel |
| `prova/painel-it-dom.html` | `181e6791…` | HTML do painel, com os 7 blocos `data-painel` |
| `prova/painel-sem-dados.png` | `2aae20ec…` | o painel sem `?sala=local` |
| `prova/painel-sem-dados-dom.html` | `0afc2c78…` | HTML do mesmo |
| `prova/sala-it.png` | `1b72f375…` | captura da Sala |
| `prova/sala-it-dom.html` | `187ddbf9…` | HTML da Sala: 94 cartões; 16 «copia IDENTICA altrove»; 0 «NON TROVATO» |
| `LEITURA-SALA-PAINEL.json` | `9e78dfc2…` | a leitura da Sala + a procura dos 16 |
| `SUPERVISOR-ESTADO.json` | `d8847f2a…` | o estado do serviço |
| `italy-painel.local.js` | `8a6cbef2…` | os dados do painel |
| `leitura.sql` | `a52fa128…` | a consulta, só leitura |
| `procurar_16.py` | `4e369fa6…` | a procura dos 16 |
| `../italy-sala-leitura.local.js` | `9ddf4ea2…` | os dados da Sala |
