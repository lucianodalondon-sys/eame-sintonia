# COMANDO-HOJE — UMA coleta canônica de `IT-T4-001` (registro do Ministero)

> Para o coordenador, na máquina de operação (VPN Itália). Missão REFERENCIA-MANUTENCAO,
> 27/09/2026 (domingo). **Nada disto foi executado daqui** — esta sessão não tem VPN nem rede
> para fora do GitHub.

## ⚠️ LEIA ANTES: hoje o portão RECUSA esta fonte

Medido nesta árvore (`python3 curadoria/collection_gate.py --ids=IT-T4-001 --json`):

```
IT-T4-001 · STATE READY_FOR_COLLECTION · READY_RULE LEGACY · MOTIVO READY_LEGACY
«promovida pela régua antiga (LEGACY); as réguas de hoje são DETAIL/v1 / PAGINA_BOLETIM/v1 / SOCIAL/v1»
```

As **duas** rotas canônicas perguntam a este portão antes de ir à rede:
a coleta agendada (`coleta/italy_recurrent_collect.mjs`, passo 6b) e o pedido manual
(`coleta/italy_executor.py::admissao_do_curator`, desde 21/09). Por isso **o comando abaixo
vai parar em `BLOQUEADA_PELO_CURATOR`, sem tocar na fonte** — e isso é o portão a funcionar,
não uma falha. Nenhuma das três réguas de hoje foi feita para um CSV de dados abertos.

**Destravar é decisão do dono/Curator, não desta missão** (o livro `curadoria/*-V1.json` é
livro vivo). Duas saídas possíveis, nenhuma feita aqui:

1. uma régua de promoção para dataset oficial (ex.: `DATASET_OFICIAL/v1`: a página do dataset
   anuncia um CSV datado com as colunas do contrato), e promover `IT-T4-001` por ela; ou
2. uma decisão nomeada (D-número) que admita `IT-T4-001` por exceção, escrita no livro do Curator.

Correr o coletor Node **direto** (`node coleta/italy_pilot_collect.mjs --fonte=IT-T4-001`)
**salta o portão** — é possível, mas não é a rota canônica, e só se faz com a decisão escrita.

## O comando (Windows, raiz de operação)

```bat
cd /d C:\eame-sintonia-ops
set ITALY_OPS_ROOT=C:\eame-sintonia-ops
set SINTONIA_TETO_24H=<o MESMO livro de 24 h que as outras linhas usam>

REM 1 · portão de egresso: tem de dizer EGRESS_GATE = PASS (IT). Se não, PARE.
py superficie\rede.py --portao-de-egresso IT

REM 2 · portão de admissão: hoje diz READY_LEGACY. Se continuar assim, PARE aqui.
py curadoria\collection_gate.py --ids=IT-T4-001 --json

REM 3 · a coleta canônica — 1 pedido de coleta, 1 fonte, pelo orquestrador
py orquestrador\orquestrador.py "colete o registro regulatorio da Italia" --filtro fonte=IT-T4-001
```

O passo 3 foi conferido **offline** com `--so-plano`: a frase resolve para
`REGULATORY (T4) · fonte=IT-T4-001 · pais=IT`, e o primeiro executor é
`italia-recorrente -> coleta/italy_executor.py` — o mesmo caminho da corrida de 18/09
(`XX-T3-2026-09-18-172035-…`, que ainda precisou de `alvo=T3`; o BG-05 já foi consertado).

## O que ele faz na rede — medido no código, não suposto

| | pedido | host |
|---|---|---|
| 1 | `robots.txt` (lido antes do primeiro pedido à origem) | `www.dati.salute.gov.it` |
| 2 | a página do dataset `/it/dataset/fitosanitari/` — de onde sai o nome `PROD_FTS_6_AAAAMMDD.csv` | idem |
| 3 | o CSV anunciado | idem |

- **3 idas HTTP** a um só domínio registável (`salute.gov.it`), dentro do teto de **5 / domínio / 24 h**
  (cada ida reserva antes de sair no livro `SINTONIA_TETO_24H`). Não é «1 pedido HTTP»: é **1 coleta**.
- **Que edição vem:** a que a página anunciar. Se a de 21/09 existir e estiver anunciada, vem ela.
  Daqui **NÃO SEI** se existe — não se visitou o site.
- A edição nova guarda-se em pasta própria (`…/MINSALUTE_FTS6_<data>/v1_<sha>/`); a de 14/09 fica
  intacta (`guardarRaw` não reescreve ficheiro existente).
- `teto` do domínio: se outra linha já gastou `salute.gov.it` hoje (ex.: bulas), o pedido é
  **adiado** (`TETO_24H`), não falhado.

## Depois da coleta (offline, sem rede)

```bat
REM o diff produto a produto contra a edição anterior (guarda em data\derivados\IT-T4-001-EDICOES\)
py coleta\it\edicoes_do_registro.py

REM só com a Sala canônica ligada (SINTONIA_SALA_BACKEND=POSTGRES + DSN): emite os EVENTO_REGULATORIO
py coleta\it\edicoes_do_registro.py --pousar

REM o frescor que a Intelligence consulta
py leis\frescor_da_referencia.py
```

Hoje, nesta árvore, o frescor de `IT-T4-001` é `EM_DIA` (edição 14/09, checagem ok 18/09, 9 dias);
passa a `PODE_ESTAR_DESATUALIZADO` a **02/10** e as autorizações a «a confirmar» a **18/10**, se
ninguém voltar a olhar.
