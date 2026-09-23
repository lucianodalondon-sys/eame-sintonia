# RELATÓRIO — MISSÃO LD3 · O ERRO DA V1 É UM ERRO DE CONTRATO

Branch `listing-detail-v3`, a partir de `origin/listing-detail-v2 @ 45617b70`. Motor: `claude-opus-5-5`.

```
COLLECTION NÃO CORREU · NADA NA SALA · SERVIÇOS VIVOS INTOCADOS (lidos por cópia)
retrato_html.py, ready_split.py, canário = INTOCADOS
Rede: 5 pedidos a svilupposostenibile.regione.lombardia.it (autorizados), egresso IT antes
Prova: scripts/detector_capa/LISTING-DETAIL-GATE-V3.json
```

## 1 — A RÉGUA DOS 4 PASSOS JÁ REPROVA OS DOIS CONTRATOS

Li cópias do ledger, das evidências e dos contratos do serviço vivo (409eeb8e) com
`ready_split.passos_da_promocao`, sem alteração.

* **#28, IT-T11-010:** está READY desde 23/09 00:30Z, promovida pelo canário, mas a
  régua dá **LEGACY**. Falha o passo 2: `DETAIL_LINKS = 1 < 2`, porque a «listagem» é a
  página da feira. **Não é READY_CURRENT.**
* **#34, IT-T7-106:** `CONTRACTED_CANARY_FAILED`, **nunca promovida**. A página nunca chega
  ao detector.

⚠️ **Fragilidade:** a #28 cai por uma margem de 1 link. Das 32 fontes READY_CURRENT, uma
passa com exatamente 2 links e três com 3. A evidência do canário não guarda o retrato
da página do índice, por isso a régua não pode perguntar «o índice é ele próprio uma
matéria?» sem mexer no canário. **Condição nova: não é necessária** para a #28 e a #34.
Subir o mínimo para 5 tiraria 10 das 32 fontes de READY_CURRENT; os falsos positivos
**não foram medidos**, porque exigiriam ler essas fontes.

## 2 — A #28: NÃO SEI, AGORA DEFINITIVO PELA RÉGUA DE 10

Foram usados os 5 pedidos autorizados, com egresso IT e robots da casa.

* ⚠️ **Erro meu:** 2 dos 5 pedidos saíram com o endereço estragado. Uma substituição no
  bash trocou todas as letras «N» (`AmosNews` → `Amos12ews`). O servidor devolveu a
  listagem normal. Refiz a tentativa com o endereço construído em Python, mudando só
  `numElementsPerPage` e `per-page`.
* Com a paginação do próprio site pedida a 12 por página, o **servidor devolve as mesmas 3
  notícias**: o tamanho da página está fixo no servidor. Esta listagem **nunca** terá os
  10 links que o G1 exige.
* **O que falta é uma decisão, não uma visita:** aceitar outra forma de provar o índice em
  sites que paginam curto, ou deixar este contrato sem `INDEX_URL` provado. Até lá, a
  régua já o mantém LEGACY.

## 3 — V1 × ACTUAL, COM A RÉGUA APLICADA AOS CONTRATOS

| população | gabarito | ACTUAL listing→article | ACTUAL article→listing | V1 listing→article | V1 article→listing |
|---|---|---|---|---|---|
| todas as páginas | original | 63/109 | 6/37 | 20/109 | 7/37 |
| todas as páginas | controlo | 28/49 | 4/20 | 5/49 | 5/20 |
| **READY_CURRENT** (régua a mandar) | original (5 fontes) | 6/8 | 0/1 | **2/8** | **0/1** |
| **READY_CURRENT** | controlo (10 fontes) | 6/11 | 1/7 | **1/11** | **1/7** |
| READY de hoje (qualquer régua) | original (24 fontes) | 17/30 | 1/15 | 8/30 | 2/15 |
| READY de hoje | controlo (13 fontes) | 7/14 | 1/9 | 1/14 | 1/9 |

**Com a régua a mandar, a V1 domina nos dois gabaritos. Mesmo assim NÃO a apliquei:**

1. No original, as READY_CURRENT têm **uma** matéria. «0/1 contra 0/1» não prova que a V1
   não barra matérias.
2. A régua ainda não manda: 36 das 68 fontes READY são LEGACY. Com as READY de hoje, a V1
   ainda perde no original, pela #28.
3. Aplicar a V1 obriga a mudar a assinatura do portão, que hoje não recebe o endereço da
   página, e todos os chamadores e gémeos. É uma mudança grande para uma prova tão curta.

**Recomendação:** aplicar a V1 quando a B2 puser a régua a mandar (só se coleta
READY_CURRENT) e quando houver mais matérias READY_CURRENT no gabarito.

## 4 — NÃO SEI (D11): PREPARADO, NÃO LIGADO

`curadoria/politica_nao_sei.py` tem as três respostas — `PASSA`, `PESSOA`, `QUARENTENA` —
e `ACTIVA = PASSA`, que é o comportamento de hoje. Nenhum ficheiro a chama, e um teste
prova isso. Ligá-la é mudar `ACTIVA` e chamar `decidir()` no portão, depois da D11.

## ENTREGA

```
REGUA_JA_REPROVA_28_34     = YES — #28 LEGACY (DETAIL_LINKS 1 < 2), #34 nunca promovida (canario falhou)
CONDICAO_NOVA              = nao necessaria; fragilidade medida (1 fonte com 2 links, 3 com 3 entre 32 READY_CURRENT)
IT_28                      = NAO SEI definitivo: o servidor fixa 3 noticias por pagina; 5 pedidos (2 com URL estragado por erro meu)
V1_APLICADA                = NO (domina com a regua a mandar, mas n=1 materia no original e a regua ainda nao manda)
TESTS                      = 42/42 (politica_nao_sei, ld2_aditamento, medir_apos_receitas, aplicar_desbloqueio)
MUTATION                   = 4/4 mortos (politica_nao_sei)
EGRESS                     = IT (149.22.91.171, Palermo) antes de cada visita
LISTING_DETAIL_GATE_PROVEN = NO
```
