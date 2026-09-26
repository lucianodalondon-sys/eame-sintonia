# CASCO-LEITURA (D78) — a Sala, só de leitura, dentro do portal que já existe

Ramo `casco-leitura-v1`, a partir de `ce28040c`. O vivo não foi tocado. A Sala real foi lida **uma vez**,
só em leitura (`PGOPTIONS='-c default_transaction_read_only=on'`; a DSN foi lida do ficheiro e nunca impressa).
Sem rede e sem coleta. **Nenhum RAW foi alterado.**

## 1 · O que foi reaproveitado (nenhum portal novo)

**Medido antes de fazer:**
- `CASCO-CLIENT-DEMO.md` e `DEPOIS-DO-PORTAL.md` (em `ce28040c` e em `claude/it-portal-reconciled-v1`)
  dizem que o casco vivo é `italia-portale/client/portale.html`. É o CLIENT-DEMO, já sem dados
  demonstrativos (154 → 3 leituras), servido por `audit/serve.mjs`.
- `claude/sintonia-eame-portal-baseline` e `claude/eame-portal-meeting-hotfix` são linhagens anteriores
  do mesmo portal.

**O que se reaproveitou:**
- **o mesmo portal:** `portale.html` ganhou uma vista `#sala`, pelo mesmo mecanismo das outras. Entra na
  lista de rotas admitidas (`AMMESSE`), no `CAPABILITY_OF` e numa voz do menu no grupo «Evidenza e
  contesto», com o contador vindo do dono do dado.
- **os mesmos cartões, cores e tipos** das vistas «Archivio» e «Registro delle fonti».
  - `ADAMA_DESIGN_SYSTEM_MATCH = componentes do próprio portal`, que já seguem o extrato
    `_ds/adama-brandwell`. Nenhum padrão visual novo.
  - O Claude Design não foi consultado: a missão é sem rede.
- **o mesmo servidor de prova:** `italia-portale/audit/serve.mjs`.
- **o mesmo contrato de design:**
  - `NAO SEI` visível, em âmbar, com o porquê;
  - a idade do dado ao lado: a hora do export no cabeçalho, e a data de pouso em cada item;
  - facto separado de interpretação: a coluna Intelligence está à parte.

**Ficheiros mudados no Git:**
- `italia-portale/client/portale.html`: a vista, o menu, a rota e o `<script src="italy-sala-leitura.js">`;
- `italia-portale/client/italy-sala-leitura.js`: **o carregador, sem dados**. Só pede os dados
  (`italy-sala-leitura.local.js`) com `?sala=local` no endereço. Sem essa marca **nada é pedido**:
  - o portão `link-asset` percorre todas as vistas e reprova um 404;
  - num deploy o ficheiro não existe;
  - por isso nenhum dos dois o pede;
- `italia-portale/client/.gitignore` e `.vercelignore`: `italy-sala-leitura.local.js` (os dados, com texto
  da Sala) nunca entra no Git nem num deploy;
- `italia-portale/audit/casco/sala-leitura.mjs`: o gerador;
- este relatório.

## 2 · Onde abrir

1. **Export da Sala** (fora do Git): `C:/Users/London1/sintonia-sala-italia/casco/SALA-EXPORT-LEITURA.json`.
   - 94 itens; sha256 `5c894ab0f62217b9970008180fd2cb58da571b0806b14514947e5dd16c8fb4ff`.
   - Consulta usada: `casco/export.sql`, sobre a vista `sala_de_espera_atual` + `raw_asset`.
2. **Gerar os dados da vista** (escreve `italia-portale/client/italy-sala-leitura.local.js`, ignorado pelo
   Git, e uma cópia em `casco/`):
   ```
   node italia-portale/audit/casco/sala-leitura.mjs C:/Users/London1/sintonia-sala-italia/casco/SALA-EXPORT-LEITURA.json C:/Users/London1/sintonia-sala-italia/armazem C:/Users/London1/sintonia-sala-italia/casco/italy-sala-leitura.local.js
   ```
3. **Abrir:**
   ```
   node italia-portale/audit/serve.mjs 8899
   ```
   e depois **`http://localhost:8899/portale.html?sala=local#sala`**. Sem `?sala=local`, a vista diz que o
   export não foi carregado. Isso está certo: é o que se vê num deploy.
4. **Prova já tirada** (fora do Git, `C:/Users/London1/sintonia-sala-italia/casco/prova/`):
   - com `?sala=local`: `sala-it.png` (captura de ecrã, sha256 `0a20a843…`) e `sala-it-dom.html` (o HTML
     desenhado pelo Chrome, `2a168e74…`);
   - sem ele: `sala-sem-export.png` (`58f1ca12…`) e `sala-sem-export-dom.html` (`5c3cbbe0…`). Mostram **0**
     cartões e a mensagem de «export não carregado»;
   - os dados gerados: `casco/italy-sala-leitura.local.js`, sha256 `43b283e8…`.
   - No HTML contei **94 cartões** (`data-sala-item`), **16** «file grezzo NON TROVATO», **78** «sha256
     verificato» e **94** «NON_ESEGUITA». Cada frase aparece mais 1 vez no código da própria página.

## 3 · O que cada item mostra, e as contagens (94 itens)

Por item: a data de pouso, a fonte (SOURCE_ID, universo, estágio) e o **trecho do documento** (a primeira
frase do corpo, nunca o texto inteiro). Depois os **quatro campos separados**, cada um com valor,
precisão e base, e um `NAO SEI` com o porquê. Por fim a **prova** (o endereço de origem e o bruto) e a
**Intelligence**.

| Campo | Com valor | NAO SEI | Com precisão |
|---|---|---|---|
| FACT_TIME (data do facto) | **22** | 72 | 22 |
| PUBLICATION_TIME (data de publicação) | **46** | 48 | 46 |
| SOURCE_LOCATION (lugar da fonte) | **5** | 89 | 5 |
| FACT_LOCATION (lugar do facto) | **19** | 75 | 19 |
| Bruto no armazém, conferido pelo sha256 | **78** | 16 NAO_ENCONTRADO | — |
| Intelligence | **0** | 94 NAO_EXECUTADA | — |

- A **base** vem preenchida em todos os FACT_TIME e FACT_LOCATION: nos `NAO SEI`, a base é o **porquê**
  (por exemplo, «o coletor declarou: UNKNOWN…»).
- Não há pontuação nem «relevância». A ordem é a do pouso na Sala, o mais recente primeiro.

## 4 · Limites (medidos, não escondidos)

1. **16 brutos não estão nesta máquina** no caminho que a Sala guarda: 12 do myfruit, 3 da IT-T5-049 e
   1 da IT-T3-008, todos de 18 a 22/09.
   - A vista diz «NÃO ENCONTRADO» com o sha256 guardado, e nunca mostra um link partido.
   - A causa provável, pela memória do projeto: a suíte já apagou `XX/` uma vez.
   - Procurei no armazém da Sala, na árvore do vivo e nos backups: não estão lá.
2. **SOURCE_LOCATION tem 5 de 94.** Nenhuma fonte da coorte declara a sede no contrato (achado da
   MICRO-VERIFICAÇÃO; proposta em `sede-fontes-v1`).
3. **Intelligence NAO_EXECUTADA em todos.** Não há saída da Intelligence, e o portal não a reconstrói
   (INT-LAW-023).
4. **O ficheiro de dados tem texto da Sala** (o trecho). Por isso é gerado **fora do Git**
   (`.gitignore`) e fora de qualquer deploy (`.vercelignore`), e só é pedido com `?sala=local`. Num deploy
   público a vista diz «export não carregado», que é o comportamento certo.
   - O portão `audit/link-asset.mjs` **não correu nesta máquina**: falta o `playwright-core` e o Chromium
     Linux. Fica `NAO MEDIDO`.
   - O `audit/deploy-surface.mjs` correu antes e depois do carregador: **0 problemas** das duas vezes.
5. **Os links do bruto são `file:///`:** só abrem nesta máquina.
6. **O cabeçalho do portal continua a dizer «AMBIENTE DIMOSTRATIVO»**, e o rodapé «Intelligence
   illustrativa». São do portal inteiro, não desta vista. Não mexi.
7. **A captura foi só em italiano.** O inglês existe (os rótulos estão no código), mas não o fotografei.
8. **O Chrome da prova**, no primeiro arranque, tentou registar-se na Google (erro GCM no terminal). É
   tráfego do próprio navegador, não coleta. Nas corridas seguintes desliguei-o
   (`--disable-background-networking`).
