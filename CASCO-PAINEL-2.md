# CASCO-PAINEL-2 — o painel lê o vivo atual, uma página por fonte, e um comando que refaz tudo

- **Ramo:** `casco-painel-2-v1`, a partir do vivo **`69b0e23f`** (LOTE 1), com o `casco-painel-v1` junto
  (`2744073c`, sem conflitos).
- **Só leitura, sem nota:**
  - sem rede nem coleta;
  - o vivo não foi tocado: o comando confere que os ficheiros alterados do vivo são os mesmos antes e
    depois do `supervisor --estado`, e **pára** se mudarem;
  - nenhum RAW foi alterado.
- **A Sala** foi lida em **duas** transações `begin read only`. As duas responderam
  `transaction_read_only = on` **dentro da transação** (`RECIBO-REFAZER.json`).

## 1 · O painel lê o vivo ATUAL, com a linha do tempo das instalações

- **O vivo que o painel mostra:** `origin/servico-20260923-0923 = 69b0e23f` e `HEAD` local do vivo =
  `69b0e23f`. Os dois aparecem no painel.
- **Linha do tempo das instalações:** vem do **reflog do ramo do vivo** (`git reflog show --date=iso
  servico-20260923-0923`). É a hora em que o vivo passou a cada SHA, e a mensagem. Lido, nunca escrito.
  - `69b0e23f` · **26/09 05:23:46 (-03)** · `merge origin/integra-noite-v1: Fast-forward` → **LOTE 1**;
  - `83de0ccd` · **26/09 01:59:36** · `merge 83de0ccd: Fast-forward` → **C9**;
  - `ce28040c` · 25/09 19:31:44 · coorte da 3.ª onda congelada. Seguem as instalações anteriores até
    25/09 01:42 (o painel mostra as últimas 14).
  - Também aparece o `reset: moving to 88ee046f` de 25/09 09:45, em âmbar: é o desfazer do FECHAR-ONDA2.
- **O resto do painel** (ondas, coorte, teto, Sala por dia, cobertura, Intelligence, D1–D10, o que
  falta) é refeito do mesmo modo. Com o vivo novo:
  - «C9 instalado» diz `83de0ccd está no vivo 69b0e23f`;
  - o conserto do C2 continua **fora do vivo** (`c2-juiz-v1 @ f6f3bb2f`; o ramo andou desde a última vez).

## 2 · A página POR FONTE (`#fontes`, «Per fonte · sola lettura»)

**109 cartões, em 3 grupos:**

| Grupo | Fontes | Com itens na Sala |
|---|---|---|
| Coorte congelada (a do vivo `69b0e23f`) | 64 | 13 |
| Prontas mas fora da coorte, com o porquê (`FALTA`) | 17 | 0 |
| Só na Sala: deram itens em corridas anteriores e não estão em nenhuma das duas listas | 28 | 28 |

Assim nenhum item da Sala fica sem fonte na página.

**Cada cartão mostra:**
- o endereço;
- **as visitas:** em quantas ondas, quantas correram, quantos pedidos no total;
- **a última visita:** a onda, a data e hora, o estado (ou porque não correu, por exemplo `TETO_DOMINIO`),
  os pedidos no domínio e os documentos novos;
- o último canário;
- **o que deu:** os itens na Sala, o intervalo das datas de publicação, as datas do facto, os lugares do
  facto, o lugar da fonte;
- **a Admissão:** SIM, NÃO e NÃO SEI, contados no livro de decisões;
- **porque não entrou**, quando não entrou.

**De onde vem, sempre juntado pelo `RUN_ID`, sem estimar nada:**
- `COORTE-BIG-COLLECTION-V1.json` do vivo: quem está dentro e fora, com o porquê;
- as linhas das 5 ondas (`ONDA-WEB-ESTADO.json` e a BC5): visitas, estado, pedidos;
- `data/collection-ledger/italy/runs.ndjson` do vivo, com 155 corridas: início e documentos novos;
- `data/samples/LIVRO-DE-DECISOES.json` do vivo, com 1.400 decisões: SIM/NÃO/NÃO SEI por `origem`;
- o export só-leitura da Sala: itens, datas, lugares, publicação.

Sem artefacto, o campo diz `NAO SEI`, ou «mai visitata in un'ondata misurata».

**Exemplo medido: IT-T10-018 (myfruit).**
- 5 visitas e 25 pedidos; 23 itens na Sala; publicação de 11/07 a 25/09;
- Admissão: NÃO SEI 36 · NÃO 22 · SIM 35;
- última visita: ONDA3 25/09 19:35, SUCCESS, 5 pedidos, 3 documentos novos.

## 3 · UM COMANDO que refaz os dados (para correr depois de cada onda)

```
node italia-portale/audit/casco/refazer-painel.mjs
```

**O que faz, por ordem, e pára se algo não bater:**
1. **Lê a Sala só em leitura:** os agregados e o export completo. Cada transação só é aceite se o banco
   disser `RO=on` dentro dela. A DSN vem de `SALA_DSN.txt` e nunca é impressa.
2. **Lê o estado do serviço:** `supervisor.py --estado` no vivo, sem `.pyc` e com a rede fechada. Se os
   ficheiros alterados do vivo mudarem entretanto, **PÁRA**.
3. **Procura os originais que não estejam no caminho da Sala**, por tamanho e sha256, nas raízes
   declaradas. Nunca copia nem move nada.
4. **Refaz os dados:** corre `sala-leitura.mjs` e `painel-operacao.mjs` (`italy-sala-leitura.local.js` e
   `italy-painel.local.js`, fora do Git e do deploy).
5. **Escreve `casco/painel/RECIBO-REFAZER.json`** com o sha256 de tudo o que gerou.

- Todos os caminhos têm valor por omissão para esta máquina e mudam por argumento: `--vivo=`, `--sala=`,
  `--casco=`, `--psql=`, `--dsn-ficheiro=`, `--ondas=`, `--armazem=`, `--raizes=a;b`, `--intel=`,
  `--fecho-onda3=`.
- **Uma onda nova** (pasta nova em `ondas/` com `ONDA-WEB-ESTADO.json`) **entra sozinha**. Não há nada
  para editar à mão.
- **Medido nesta corrida:** cerca de 5 s ao todo; RO `on`/`on`; Sala 94; 16 originais fora do caminho da
  Sala, 16 achados noutro caminho.

## Limites
1. **A hora das instalações** é a do reflog **desta máquina**. Se o vivo for reinstalado noutra máquina,
   o reflog não viaja.
2. **Os 17 «prontas fora da coorte» não têm visitas medidas.** Nenhuma onda as chamou; o cartão diz o
   porquê (`SEM_RECEITA_WEB…`, `SEM_CONTRATO_DE_COLETA`…).
3. **As decisões da Admissão são contadas por decisão, não por item** (um item pode ter decisão em mais
   de uma gaveta). Por exemplo, o Chianti Classico tem NÃO 29 e 1 item na Sala.
4. **D1–D10:** o estado vem do Git, isto é, do commit que nomeia o defeito. Os testes desses ramos **não**
   foram corridos aqui.
5. **O portão `link-asset.mjs` continua sem correr nesta máquina** (falta o playwright-core). O
   `deploy-surface.mjs` dá 0 problemas.
6. **Mapa: não corrido.** É PRONTO-SEM-MAPA.

## Provas (fora do Git, `C:/Users/London1/sintonia-sala-italia/casco/painel/`)

**Capturas e HTML** (`prova2/`, sha256 abreviado):

| Ficheiro | sha256 | O que mostra |
|---|---|---|
| `painel-topo-it.png` | `c3a5115d…` | a linha do tempo |
| `painel-it.png` | `edc9c884…` | o painel inteiro |
| `painel-it-dom.html` | `37b79f61…` | HTML do painel: 8 blocos `data-painel`, incluindo `instalacoes` |
| `fontes-it.png` | `2453e1c3…` | a página por fonte |
| `fontes-it-dom.html` | `b57b92ea…` | HTML da página por fonte: **109** `data-fonte` |
| `fontes-sem-dados.png` | `69121bf4…` | a página por fonte sem `?sala=local` |
| `fontes-sem-dados-dom.html` | `4687a1cc…` | HTML do mesmo: **0** cartões, e o aviso |
| `sala-it.png` | `fca912e3…` | a Sala |
| `sala-it-dom.html` | `dabc0489…` | HTML da Sala: 94 cartões |

**O recibo:** `RECIBO-REFAZER.json` (`ac84bf03…`) tem o sha256 do export, da leitura, do estado e dos
dois ficheiros gerados.
