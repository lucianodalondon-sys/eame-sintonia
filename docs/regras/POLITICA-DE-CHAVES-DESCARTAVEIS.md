# POLÍTICA DE CHAVES DESCARTÁVEIS — regra operacional permanente

**Vigora a partir de:** 2026-08-29 · aplicável a **todas** as missões do SINTONIA EAME.

---

## QUANDO O DONO ENVIA UMA CHAVE APIFY NA CONVERSA

A chave está **autorizada**, é **descartável**, e traz um orçamento próprio de
**≈ US$ 5**. Consequências operacionais, todas já decididas — não se pergunta de novo:

| | |
|---|---|
| usar até esgotar o crédito | **autorizado** |
| pedir nova autorização para gastar o restante | **não** |
| interromper a missão por receio de consumir saldo | **não** |
| interromper porque a chave apareceu no contexto | **não** — o dono aceita explicitamente esse risco |
| tratar como credencial permanente do projeto | **não** |
| quando o crédito acabar | a chave está **ENCERRADA**; avisar que é preciso uma nova |

**Cada chave é um orçamento independente.** Saldo de uma nunca é presumido para a
seguinte.

## ONDE A CHAVE PODE E NÃO PODE ESTAR

Não há motivo para gravá-la. Ela vive **apenas na execução** — no scratchpad da sessão,
que fica fora do repositório.

**Nunca:** arquivo versionado · commit · README · documentação canônica · fixture ·
dataset · relatório permanente.

**Esta política é documentada. A chave, não.**

## AUTONOMIA CONCEDIDA

Pesquisar Actors · testar vários · executar · abandonar os ruins · recuperar datasets ·
paginar · ampliar amostra · repetir buscas · comparar rotas · consumir o saldo · trocar
de plataforma quando fizer sentido.

## O ÚNICO LIMITE

O gasto tem de servir à missão. **Não gastar só para esgotar a chave.**

```
TESTE PEQUENO → MEDIR QUALIDADE → ESCOLHER A ROTA → USAR O RESTANTE COM PROPÓSITO
```

O objetivo é **máximo de inteligência útil por crédito** — nunca máximo de registros por
crédito. Um Actor com 5.000 posts sem identidade confiável é pior que um com 100 itens
verificáveis.

## RELATÓRIO OBRIGATÓRIO AO FIM DE CADA CHAVE

```
APIFY_KEY_RUN · ACTORS_TESTED · TOTAL_REAL_COST · RESULTS · UNIQUE_ORIGINS ·
USEFUL_ITEMS · BEST_ACTOR · BEST_COST_QUALITY · REMAINING_BALANCE · KEY_STATUS
```

`KEY_STATUS` ∈ `ACTIVE` · `EXHAUSTED` · `ABANDONED`.
**O valor do token nunca entra no relatório.**
