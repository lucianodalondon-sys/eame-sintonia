# B2 — FECHAR O CAMINHO DA PROMOTION (e da DEMOTION) PELA CAUSA RAIZ

Branch `ponte-promocao-v1` (de `ponte-prova-viva-v1` @ 2495f7d7). Serviços vivos
intocados. Prova: `curadoria/B2-PONTE-PROMOCAO-V1.json`.

## As quatro causas, medidas

| sintoma (B1) | causa raiz | o que se fez |
|---|---|---|
| bot promove com PASS_PARCIAL | o bot vivo corre `409eeb8e`, anterior à UNIFICACAO-V1; o worker da linha já manda PASS_PARCIAL para CONTRACTED_CANARY_FAILED (`test_um_so_canario_promove`) | nada no código — **deploy** |
| 23 provas não importadas | a ponte viva corre `20c06500`, anterior a `be09703c` (a chave sintética nunca casava); e o que já atravessou nunca voltava ao plano | **recuperação idempotente** em `importar_provas_do_bot` |
| 35 sem contrato no livro do portão | nenhuma peça escrevia o contrato do bot aqui | **`importar_contratos_do_bot`**: só o que falta, nunca sobrepõe, colisão dita |
| IT-T5-041: bot bloqueia, portão aprova | **dois donos do contrato**: as 8 elegíveis têm contrato diferente no bot; T5-041 nem existe nele (T02077: «BLOCK sem contrato», sem transição) | **`dono_do_contrato`**: READY_CURRENT sem o mesmo contrato no bot → CANARY_PENDING, com o motivo |

## Prova ponta a ponta, em cópia

Uma volta REAL de `ponte_automatica.uma_volta` sobre cópias da fotografia B1
(`medidas/prova_b2_ponte_em_copia.py`); ficheiros reais conferidos por sha256.

* 114 provas e 364 contratos atravessaram; 9 colisões de dono ficaram de fora.
* **PROMOTION: 20 entraram** (ex.: IT-T8-030 Informatore Zootecnico, 18 227
  caracteres em parágrafos).
* **DEMOTION: 8 saíram** — as 8 elegíveis, incluindo **IT-T5-041**.
* Portão **8 → 20**.

⚠️ As 8 que saem incluem fontes boas; saem porque o bot mede outro contrato.
**Passo 0 do deploy é decisão do dono**: qual contrato o bot passa a medir.

## Correcção à B1

A B1 disse GIT_NO_CAMINHO = NO. Em parte é falso: `carregar_contexto()` faz
`git show` dos livros congelados B e B2 em cada processo. Só leitura de
referências fixas — mas é git no runtime. Proposta: congelá-los em ficheiros.

## RETIRADA_POR_DECISAO (M5B)

Respeitada: a marca vive no contrato e o portão lê-a; a importação nunca
sobrepõe um contrato existente, e a regra do dono só compara a aquisição.

## Testes

13 novos (positivo/negativo + ponta a ponta na fotografia); 108 vizinhos verdes
antes e depois; mutação 8/8.

## DEPLOY_PLAN

0. Dono decide o contrato das 7 elegíveis com contrato diferente.
1. Entregar esses contratos ao bot pela porta dele (a ponte não escreve lá).
2. Reiniciar o bot na linha unificada.
3. Reiniciar o observador da ponte nesta branch.
4. 1.ª volta com `--forcar`; ler PROVAS/CONTRATOS_IMPORTADOS, COLISOES, ENTRARAM/SAIRAM.
5. (proposta, fora do writeset) revalidação periódica das READY_CURRENT pelo bot.
