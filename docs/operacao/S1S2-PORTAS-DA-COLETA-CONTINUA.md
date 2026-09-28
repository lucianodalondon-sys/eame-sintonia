# S1 + S2 — AS PORTAS DA COLETA CONTÍNUA

> **Missão:** destravar as linhas de aquisição que estavam paradas na coleta contínua.
> **Ramo:** `lucianodalondo…` — ver `git branch --show-current`; **base:** `e24139702` (o que o serviço corre).
> **Medido em:** 28/09/2026, leitura apenas sobre a árvore do serviço. **Nada foi instalado.**
> O que transforma isto em verde é decisão do @sintonia-coordenador (D-S1).

---

## 1 · O QUE SE MEDIU (antes de tocar em nada)

O serviço `SINTONIA-COLETA-CONTINUA` corre a cada 30 min e **funciona**: `RESULT=0`, último 08:50:50,
próximo 09:20:20. O log (`ondas/COLETA-CONTINUA/servico.log`) mostra, dos ciclos 6 ao 22, o mesmo retrato
em **todas** as passagens:

```
BUSCA          ESPERA_LIGACAO  SEM_RESERVA_24H: coleta/linha_busca.py nao chama reserva_24h.reservar(
CIENCIA        ESPERA_LIGACAO  SEM_RESERVA_24H: coleta/pesquisadores_t6.py nao chama reserva_24h.reservar(
SOCIAL         ESPERA_LIGACAO  SEM_RESERVA_24H: coleta/teto_da_onda.py nao chama reserva_24h.reservar(
PESQUISADORES  ESPERA_LIGACAO  TRANSPORTE_NAO_EXISTE_NESTA_ARVORE: coleta/seguir.py
SITES          A_CORRER        (14 fontes, +58 documentos no ciclo 21)
```

Quatro das cinco linhas não corriam. O ciclo 21 correu **T5/T7/T8/T12 — só sites**.

## 2 · A CAUSA NÃO ERA A QUE PARECIA

`medir_ligacao` procurava a **string** `reserva_24h.reservar(` **dentro do ficheiro do transporte**.
Mas desde a **D124** a reserva vive no **dono único** — `coleta/teto_da_onda.py`, que chama
`cortesia_adaptativa.reservar_ou_esperar` — e é alcançada pelo abridor instalado em `coleta/scrap_http.py`.

O próprio ficheiro já dizia isto, na linha 33 da sua doutrina:

> *«A linha SITES prova-se LIGADA pelo COMPORTAMENTO do transporte … **nunca por um texto no ficheiro**.»*

O código só cumpria essa doutrina na SITES. **O que faltava não era a reserva — era a régua a medir o
ficheiro errado.** Resultado: duas linhas ligadas (`BUSCA`, `SOCIAL`) apareciam como desligadas, e a
corrente parava por causa da medição.

| linha | quem reserva por ela | como estava |
|---|---|---|
| SITES | `italy_pilot_collect.mjs` | ✅ LIGADA (tem SONDA) |
| BUSCA | `scrap_http.py` → `teto.reservar(` (abridor instalado, corre em cada pedido) | ❌ falso vermelho |
| SOCIAL | `teto_da_onda.py` — **é o reservador** (`ca.reservar_ou_esperar(`) | ❌ falso vermelho |
| CIENCIA | **ninguém** — `corpus_pesquisador._get` lia o orçamento e nunca reservava | ❌ vermelho **verdadeiro** |
| PESQUISADORES | `seguir.py` (contador injetado) | ❌ o ficheiro mudou de gaveta |

## 3 · O QUE MUDOU

1. **`ferramentas/big_collection/coleta_continua.py`**
   - `LINHAS` passa a declarar **`RESERVA_EM`**: *quem reserva por esta linha*, e não o ficheiro do transporte.
   - `medir_ligacao` mede nesse ficheiro e **rotula a medida**: `MEDIDO_EM = "COMPORTAMENTO"` (SONDA) ou
     `"TEXTO"` (fraca). O rótulo viaja até ao registo do ciclo — TEXTO não passa por comportamento.
   - **S2:** `PESQUISADORES` deixa de apontar para `coleta/seguir.py` (que já não existe ali) e passa a
     `ferramentas/seguir_pesquisadores/seguir.py`.
   - `SOCIAL`: deixa de exigir ao dono do freio que chame a própria fachada (`reserva_24h.reservar(`),
     o que criaria um **segundo dono** da mesma reserva.
2. **`coleta/corpus_pesquisador.py`** — o buraco verdadeiro: `_get` passa a **reservar antes do pedido**
   (`teto.reservar(...)`, o freio da casa), como manda a **D90**. Sem livro nomeado não trava nada — o
   comportamento antigo mantém-se; com livro, a reserva passa a existir.
3. **Testes** — dois testes afirmavam o erro antigo (`BUSCA` *não* ligada). Foram corrigidos para o
   contrato novo, e nasceu um teste que impede a mentira oposta: *uma linha não fica ligada por declaração*.

## 4 · AS DUAS PROVAS

### Prova A — a reserva da CIENCIA existe, medida por COMPORTAMENTO (sem rede)

Servidor local + livro de cortesia temporário; `_get` chamado como a linha o chama.

| árvore | resposta | livro | reserva |
|---|---|---|---|
| serviço (`e24139702`, sem a correção) | `{"ok": true}` | **não existe (0 linhas)** | pedido saiu **sem reserva** |
| nova (`scrap-s1s2-portas-v1`) | `{"ok": true}` | **1 linha** | `HOST=127.0.0.1 · LINHA=pesquisadores_t6 · TIPO=RESERVA` |

### Prova B — a régua, antes e depois (ciclo a seco, 0 rede, 0 Sala)

```
ANTES   BUSCA/CIENCIA/SOCIAL = ESPERA_LIGACAO · PESQUISADORES = TRANSPORTE_NAO_EXISTE · SITES = A_CORRER
AGORA   BUSCA/CIENCIA/SOCIAL/PESQUISADORES = NADA_ELEGIVEL · SITES = A_CORRER (12 fontes, 55 pedidos)
```

**E é aqui que aparece o bloqueio seguinte, agora com nome.**

## 5 · O QUE ESTA MISSÃO NÃO RESOLVE — E PASSA A ESTAR À VISTA

As quatro linhas passaram de **falso vermelho** para um **vermelho verdadeiro e nomeado**:

```python
cands = {l["LINHA"]: [] for l in LINHAS}      # ← as quatro ficam VAZIAS
cands["SITES"] = candidatas_do_plano(plano)   # ← só a SITES tem coorte
```

**Não existe coorte/plano a alimentar as outras quatro linhas.** Mesmo com a régua verde, correriam zero
fontes (`NADA_ELEGIVEL`). Religar a chamada era **necessário e não suficiente**.

> **MENOR CORREÇÃO SEGUINTE:** um alimentador por linha (o equivalente a `candidatas_do_plano` para
> `BUSCA`/`CIENCIA`/`SOCIAL`/`PESQUISADORES`) e o `SINTONIA_LINHA` exportado quando cada uma corre, para
> o livro atribuir a reserva à linha certa em vez de `pesquisadores_t6`/`scrap_http`.
> **Dono:** SCRAP/Collection. **Não entra nesta missão** — muda o desenho do ciclo e pede decisão do coordenador.

## 6 · O QUE FICA ABERTO, DITO EM VOZ ALTA

- **`RESERVA_EM` é medida fraca:** um comentário satisfá-la-ia. A correção definitiva é uma **SONDA por
  linha**, como a da SITES (D124). Fica aberta; até lá, o rótulo `MEDIDO_EM=TEXTO` impede que passe por prova.
- **`SINTONIA_LINHA`** não é exportado ao correr estas linhas — a reserva é escrita, mas com o nome de quem
  chamou, não o da linha.
- **As duas linhas de false-red precisam de verificação independente** antes da instalação: a régua foi
  corrigida por quem tem interesse em vê-la verde. É o @sintonia-lab que fecha isto.
- **System Map:** esta mudança toca `coleta/`, `ferramentas/` e `tests/`; o mapa tem de ser regerado pela
  cadeia canónica antes de a mudança ser considerada pronta.

## 7 · COMO INSTALAR (por conta de quem coordena, D-S1)

```bash
# 1. verificação independente no ramo novo
py -m pytest tests/test_coleta_continua.py tests/test_lote8_juncoes.py -q
# 2. com o robô PARADO, backup dos livros, avanço simples para a árvore do serviço
# 3. religar o serviço e ler UM ciclo: as quatro linhas deixam de dizer ESPERA_LIGACAO
```

**Freio que não muda:** o do canário (D124). Isto não autoriza gastar mais pedidos — só deixa de proibir
linhas que já estavam ligadas.