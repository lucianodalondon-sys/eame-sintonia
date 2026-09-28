# COLETA-OCIOSA — um domínio fechado já não segura a passagem inteira

Missão `nuvem-coleta-ociosa-v1` · 28/09/2026 · D86 (24 h/dia) · D124 · D132 (saúde da coleta)
Base: `servico-20260923-0923` @ `fd8c9469` · ramo `claude/idle-passage-collection-hgkfrc` · **sem merge**.
Nada tocou em produção, na Sala, na coleta real nem na VPN: 0 rede externa, 0 Sala, 0 robô.

## ESTADO

```
CORRECAO            FEITA   ferramentas/big_collection/coleta_continua.py (so este ficheiro de codigo do servico)
TESTES              58/58   tests/test_coleta_continua.py (8 novos: classe ColetaOciosa)
MUTACAO             35/35   provas/COLETA-CONTINUA-MUTACAO.json (M30..M35 novos, todos MORTOS)
ENSAIO A SECO       ANTES 0 fontes (NADA_ELEGIVEL) · DEPOIS 49 fontes (RESTO_SO_DOMINIOS_FECHADOS)
BATERIA POR NOME    ver EVIDÊNCIA §5
SYSTEM MAP          regerado pela cadeia; VALIDAR = PASS; --conferir-carimbo no relatório de entrega
```

A regra nova, em `coleta_continua.py`:

- `resto_so_dominios_fechados(e)` (pura): verdadeira **só** quando nada corre **e** todas as candidatas
  que faltam na passagem esperam com `PORQUE = DOMINIO_FECHADO` **e** cada domínio fechado delas está fechado
  por uma razão que abre sozinha com o relógio: `ABREM_COM_O_TEMPO = TETO_24H, TETO_NO_CICLO, JANELA_24H`.
- Nesse caso, no ciclo, corre-se o **mesmo** `escolher()` com as feitas zeradas (sobre uma cópia do orçamento
  do ciclo). **Só se abre passagem nova se isso fizer alguma fonte correr** — senão nada muda.
- A passagem nova fica registada no ciclo (`LINHAS.SITES.PASSAGEM_NOVA`: `PASSAGEM`, `MOTIVO =
  RESTO_SO_DOMINIOS_FECHADOS`, `FEITAS_NA_ANTERIOR`, `FICARAM_A_ESPERA` com `ABRE_EM` e `DOMINIOS_FECHADOS` de cada
  uma) e no estado (`ABERTA_POR`, `A_ESPERA_AO_ABRIR`, `ABERTA_NO_CICLO`).
- As que esperavam **não** entram em `FEITAS_NA_PASSAGEM`: continuam candidatas na passagem nova e entram
  pelo `escolher()` de sempre quando o domínio abre.
- Teto, orçamento vigente (D124), orçamento partilhado no ciclo, janela D79, freio, robots, portão de egresso IT
  (D90/D91/D124), PROVA-TETO e reconciliação: **não mudaram** — a passagem nova passa pelo mesmo `escolher()`
  e pelo mesmo resto do ciclo.
- `--ensaio-a-seco` aceita `--estado-continua=<cópia de COLETA-CONTINUA-ESTADO.json>` (antes só sabia usar as
  feitas do disparador por rodada).

**Declarado — quando NADA muda (continua a esperar como hoje):** se pelo menos uma das que faltam espera por
`PAUSA_24H` ou `RETRY_AFTER` (o freio de **resistência**: o site pediu para parar), por `MAX_FONTES_NO_CICLO`,
ou por qualquer razão que não esteja em `ABREM_COM_O_TEMPO`; e se, mesmo zerando as feitas, nenhuma fonte cabe.

## EVIDÊNCIA

### 1. Ensaio a seco do ciclo 30, antes × depois (0 rede)

```
$ python3 provas/coleta_ociosa_ensaio.py
ANTES  NADA_ELEGIVEL  correriam  0 fontes (0 pedidos) · esperam 15 · passagem nova: None
         espera edagricole.it    15 fontes ['TETO_24H'] gasto 36/40 abre 2026-09-29T11:12:10+00:00
DEPOIS A_CORRER       correriam 49 fontes (226 pedidos) · esperam 15 · passagem nova: RESTO_SO_DOMINIOS_FECHADOS
         espera edagricole.it    15 fontes ['TETO_24H'] gasto 36/40 abre 2026-09-29T11:12:10+00:00
escrito: provas/COLETA-OCIOSA-ENSAIO.json
```

O ANTES (o `coleta_continua.py` de `fd8c9469`) reproduz o que o coordenador mediu: `NADA_ELEGIVEL`, 15 à espera,
todas `edagricole.it`, `TETO_24H` 36/40, `ABRE_EM 2026-09-29T11:12:10Z`. O DEPOIS, com os mesmos ficheiros,
correria as 49 fontes dos domínios abertos e deixaria as 15 na fila com a mesma hora de abertura.

O mesmo pelo CLI do serviço (o caminho que o coordenador vai usar com as cópias reais):

```
$ python3 ferramentas/big_collection/coleta_continua.py --ensaio-a-seco --base=<tmp> \
    --plano=<rec>/RODADAS-PLANO.json --teto-24h=<rec>/TETO-24H.json \
    --estado-continua=<rec>/COLETA-CONTINUA-ESTADO.json --agora=2026-09-28T15:50:00-03:00
SITES: A_CORRER 49 fontes · 226 pedidos · PASSAGEM_NOVA RESTO_SO_DOMINIOS_FECHADOS → PASSAGEM 3 · 15 à espera
PROXIMO_A_ABRIR {'DOMINIO': 'edagricole.it', 'ABRE_EM': '2026-09-29T11:12:10+00:00', 'FONTES_A_ESPERA': 15}
```

**Com os ficheiros vivos** (copiados; os originais só se leem, sem rede):

```
py provas\coleta_ociosa_ensaio.py --plano=<cópia RODADAS-PLANO.json> --estado=<cópia COLETA-CONTINUA-ESTADO.json> ^
   --livro=<cópia do livro da cortesia (TETO-24H.json)> --agora=2026-09-28T15:50:00-03:00 --saida=<pasta>\ENSAIO.json
```

### 2. Testes (`tests/test_coleta_continua.py`, classe `ColetaOciosa`)

Caso reconstruído: plano da 4.ª onda commitado (64 fontes, 15 `edagricole.it`), `SITES` em PASSAGEM 2 com todas
as outras feitas, livro da cortesia com 36 reservas `edagricole.it` (orçamento vigente 40, sem teto manual).
A onda falsa não faz HTTP: reserva cada pedido no livro da cortesia (o mesmo código do transporte) e regista a
resposta.

| teste | o que prova |
|---|---|
| `test_reconstrucao_e_o_ciclo_30` | a foto de partida: 15/49, `edagricole.it` 36/40 |
| `test_caso_real_abre_passagem_para_os_dominios_abertos` | ciclo real: corre as 49, **0 pedidos a edagricole**, PASSAGEM 3 com motivo e as 15 à espera (ABRE_EM certo), as 15 **não** contam como feitas, nenhum domínio acima do orçamento, PROVA-TETO PASS, orçamento do ciclo = o da passagem nova |
| `test_as_que_esperavam_entram_quando_abre_em_passa_e_o_teto_manda` | 1 min antes de ABRE_EM: edagricole ainda 0 pedidos; 1 min depois: entram **exatamente** `(orçamento vigente − gasto) // 5` fontes edagricole, nem uma a mais; gasto ≤ orçamento |
| `test_freio_de_resistencia_continua_a_esperar` | `RETRY_AFTER` em edagricole: `NADA_ELEGIVEL`, sem passagem nova, 0 pedidos, robô intocado |
| `test_um_so_do_resto_em_resistencia_segura_a_passagem` | 14 em TETO + 1 em RETRY_AFTER noutro domínio: sem passagem nova |
| `test_sem_dominio_aberto_nao_abre_passagem` | tudo fechado: PASSAGEM não anda, nada corre |
| `test_a_seco_mostra_a_passagem_nova_sem_escrever` | o ensaio mostra a passagem nova e não escreve o estado |
| `test_regra_pura` | a tabela da regra (TETO_24H/TETO_NO_CICLO/JANELA_24H sim; PAUSA_24H/RETRY_AFTER/MAX_FONTES não) |

```
$ python3 tests/test_coleta_continua.py          → Ran 58 tests · OK
$ python3 tests/test_teto_adaptativo_rebase.py   → Ran 24 tests · OK
$ python3 tests/test_lote8_juncoes.py            → Ran 8 tests · OK
```

### 3. Mutação (`provas/coleta_continua_mutacao.py --ref=HEAD`, cópia por `git archive`)

```
M30_SEM_A_CONDICAO_SO_DOMINIO_FECHADO     MORTO   (tirar a condição "só DOMINIO_FECHADO")
M31_RESISTENCIA_CONTA_COMO_FECHADO        MORTO
M32_SEM_PASSAGEM_NOVA                     MORTO   (o defeito de antes)
M33_PASSAGEM_ABERTA_SEM_NADA_A_CORRER     MORTO
M34_AS_QUE_ESPERAM_CONTAM_COMO_FEITAS     MORTO
M35_ORCAMENTO_DA_PASSAGEM_NOVA_PERDIDO    MORTO
COLETA_CONTINUA_MUTACAO · mortos=35 de 35   (sem mutante: 58 testes, código 0)
```

As âncoras dos mutantes de `provas/teto_adaptativo/mutacao_rebase.py` e `provas/lote8_integra/mutacao_lote8.py`
sobre `coleta_continua.py` continuam a aparecer exatamente uma vez (conferido).

### 4. System Map

`provas/coleta_ociosa_ensaio.py` declarado na peça das provas (P9); a frase da peça `C-ONDA-WEB` diz a regra
nova. Cadeia: `correr_a_cadeia.py REGERAR` → `CADEIA=OK`; `VALIDAR` → `SYSTEM_MAP_CHECK=PASS`.

### 5. Bateria inteira por nome, antes × depois

BATERIA_PLACEHOLDER

## PROBLEMA

1. **O preço da regra (medido no teste, não escondido):** enquanto `edagricole.it` estiver fechado, cada ciclo
   em que o resto for só edagricole abre **outra** passagem, e as fontes dos outros domínios voltam a ser
   visitadas até ao orçamento de 24 h de cada domínio as fechar (no teste: 1 min antes de ABRE_EM já ia na
   PASSAGEM 4, e fontes como `crea.gov.it` — 25 pedidos por passagem — ficaram à espera por orçamento). O freio
   é o orçamento vigente de cada domínio (D124), que não mudou. Se revisitar o mesmo índice a cada 30 min não
   rende documentos novos, isso gasta orçamento de 24 h sem retorno — é uma decisão do dono (ex.: intervalo
   mínimo entre passagens), não desta correção.
2. `PASSAGEM` passa a subir mais depressa; quem lê o número como "voltas completas à coorte" deixa de poder
   fazê-lo. O motivo de cada passagem aberta assim fica registado (`ABERTA_POR`).
3. O ANTES já tinha esta forma para a passagem que acaba com **todas** feitas (recomeça no ciclo seguinte);
   a regra nova só estende isso ao caso "o resto é só domínio fechado que abre com o tempo".

## O QUE NÃO SEI

- **Os ficheiros vivos não estão neste repositório.** O ensaio e os testes usam uma reconstrução: o plano é a
  tabela commitada da 4.ª onda (64 fontes; o vivo tem 61 — quais 3 faltam, não sei; as 15 edagricole batem) e
  o livro tem 36 reservas edagricole com a mais antiga às 11:12:10Z (as horas das outras 35 não sei: só mudam
  quantas cabem depois de ABRE_EM). O comando para o vivo está em §1.
- Se, no vivo, alguma das 46 estiver fechada por outra linha ou recibo no livro de 24 h: o ensaio com as cópias
  reais diz; aqui não se vê.
- `PAUSA_24H` — li "freio do domínio" (item 1) como o orçamento/teto e a janela D79, e "freio de resistência"
  (item 3) como a pausa de 24 h e o Retry-After que o **site** pediu. Por isso `PAUSA_24H` **não** abre
  passagem. Se o dono quis que abrisse, é mudar `ABREM_COM_O_TEMPO` (e M31 passa a sobreviver — o teste
  `test_regra_pura` tem de mudar junto).
- O orçamento de `edagricole.it` depois de ABRE_EM: a cortesia adaptativa pode dobrá-lo (a janela usou 36/40 ≥
  metade), por isso o teste mede "quantas cabem" pelo livro em vez de fixar um número.
- Não corri nada contra a coleta real, a Sala ou a rede — por mandato.

## EM PALAVRAS SIMPLES

A coleta ficava parada quase o dia inteiro porque as únicas fontes que faltavam eram de um site que já tinha
gastado a cota do dia.
Agora, quando só falta esse tipo de site, ela recomeça a volta com os outros sites e deixa as fontes dele na
fila, sem contar como feitas.
Quando a cota do site volta, elas entram — sem passar do limite, e se o site pedir para parar, continua esperando.
