# RELATÓRIO — MISSÃO LD1 · O GATE LISTING vs DETAIL DEPOIS DAS RECEITAS DO G1

Branch `listing-detail-v1`, a partir de `origin/desbloqueio-coorte-v1 @ 06d25deb`. Motor: `claude-opus-5-5`.

```
COLLECTION NÃO CORREU · NADA NA SALA · SEM REDE · SERVIÇOS VIVOS INTOCADOS
curadoria/retrato_html.py e os gémeos = INTOCADOS (nenhuma regra provada)
Prova: scripts/detector_capa/LISTING-DETAIL-GATE-V1.json
Medidor: scripts/detector_capa/medir_apos_receitas.py (usa os juízes de medir_gabarito.py sem os reescrever)
```

---

## 1 — O QUE SE MEDIU, E SOBRE O QUÊ

* **Livro antes** = cópia do livro do Curator do serviço vivo (`409eeb8e`).
  **Livro depois** = a mesma cópia com o pacote G1, em duas passagens: 73 alterações
  na 1.ª e 0 na 2.ª, como no relatório do G1. **Tabela** = cópia de
  `origin/unificacao-v1`; não entra no juízo capa/matéria.
* O G1 muda a receita de **17 fontes** (15 `LINK_PATTERN` + 2 `INDEX_URL`).
  13 delas estão no gabarito, com **26 das 146 páginas**. Só nessas 26 as receitas
  podem mudar alguma coisa.
* Gabarito: as mesmas 146 páginas da 6-PREP-c (109 capas, 37 matérias). Sem rede.

**Os dois erros** (mandato v2 §18):
`FALSE_LISTING_AS_ARTICLE` = capa que atravessa o portão de hoje. O portão só reprova
`CAPA_PROVAVEL`, por isso uma capa julgada `MATÉRIA` ou `NAO_SEI` passa.
`FALSE_ARTICLE_AS_LISTING` = matéria julgada capa.

---

## 2 — A TABELA (todas as 146 páginas)

| regra | antes das receitas: listing→article | article→listing | **depois das receitas: listing→article** | **article→listing** |
|---|---|---|---|---|
| **ACTUAL** (só formato) | 63/109 | 6/37 | **63/109** | **6/37** |
| SÓ_MORADA | 4/109 | 25/37 | 4/109 | 15/37 |
| PROPOSTA (morada antes do formato) | 4/109 | 25/37 | 4/109 | 15/37 |
| **V1** (INDEX_URL exacto = capa) | 20/109 | 9/37 | **20/109** | **7/37** |
| V2 (desacordo → pessoa) | 37/109 | 11/37 | 37/109 | 5/37 |

**Na fatia não circular** (as 120 páginas de fontes que o G1 não tocou), as receitas
não mudam nada: ACTUAL 55/97 · 2/23; V1 19/97 · 3/23; V2 33/97 · **4/23**.
**Na fatia circular** (26): ACTUAL 8/12 · 4/14; V1 1/12 · 4/14; V2 4/12 · 1/14.

---

## 3 — NENHUMA REGRA DOMINA O ACTUAL COM AS RECEITAS DE HOJE

Regra de entrada: **não ser pior que o ACTUAL em nenhum dos dois erros.**

* **SÓ_MORADA / PROPOSTA:** barram 15/37 matérias em vez de 6. Não entram.
* **V1:** 20/109 contra 63/109, mas **7/37 contra 6/37**. Falha por **uma** matéria, a
  #28 (IT-T11-010). O `INDEX_URL` do contrato dessa fonte é a página de uma feira
  (`…/educazione-ambientale/fiera/fiera-2026`). É o 3.º dos três `INDEX_URL` errados
  que a 6-PREP-c achou; o G1 corrigiu os outros dois.
* **V2:** ganha no total (37/109 · 5/37), mas **na fatia não circular barra 4/23
  contra 2/23**. A vitória vem das 26 páginas em que as receitas foram aprovadas contra
  este mesmo gabarito. Não é um benchmark válido.

**SIMULADO:** retirando o `INDEX_URL` errado de IT-T11-010, a V1 dá **20/109 · 6/37**.
Domina, porque é melhor num erro e igual no outro. Não sei qual é o endereço certo
da listagem dessa fonte; a simulação é só «não é aquela».

---

## 4 — O ERRO QUE SOBRA: DA REGRA OU DA RECEITA?

Uma página conta como erro **da receita** quando a morada, com o livro já corrigido, a
classifica mal; caso contrário, o erro é **da regra**.

| regra (depois das receitas) | erro da REGRA | erro da RECEITA |
|---|---|---|
| ACTUAL | 59 capas passam · 6 matérias barradas | 4 capas passam (3 fontes ausentes do livro vivo) |
| SÓ_MORADA / PROPOSTA | 0 | 4 capas (fontes ausentes) · **14 matérias que não casam o `LINK_PATTERN`** · 1 `INDEX_URL` = matéria |
| V1 | 16 capas não-índice passam · 6 matérias barradas (as do formato) | 4 capas (fontes ausentes) · 1 matéria (#28, IT-T11-010) |
| V2 | 33 capas passam | 4 capas · 5 matérias |

Leitura:

* **O ACTUAL erra por regra**: o formato sozinho não distingue uma página inicial ou uma
  listagem com muito texto de uma notícia.
* **As regras de morada erram por receita**: mesmo depois do G1, 14 matérias não casam
  a receita da sua própria fonte. O G1 levou esse número de 22 para 14, mas não chega.
* **A V1 erra pouco por receita (1) e pouco por regra (6 matérias, as mesmas do
  ACTUAL)**. As 16 capas não-índice que deixa passar (chi siamo, contatti, listagens
  com outro endereço) estão fora do que ela olha, por desenho.
* **Fontes ausentes:** IT-T5-041, IT-T9-015, IT-T9-019 estão no gabarito mas não no livro
  vivo. Em 8 fontes, o livro vivo aponta o `INDEX_URL` para a página inicial, onde o
  livro de `detector-capa-v1` apontava para a listagem de notícias. Por isso os números
  «antes» de hoje não são os da 6-PREP-c: V1 20/109 contra 13/109.

---

## 5 — AMEAÇAS À VALIDADE

* **Circularidade das receitas:** medida e separada (secção 2).
* **Circularidade do índice:** as capas-índice foram escolhidas pelo `INDEX_URL`; o ganho
  da V1 está todo nelas. A regra é lógica («a página que o contrato declara como
  listagem é listagem»), mas o gabarito não mede o que a V1 faria em índices que ele
  não escolheu.
* **Segunda leitura independente:** 20 páginas ao acaso (`random.seed(20260923)`), lidas
  às cegas antes de abrir o veredito do gabarito: **20/20 concordam**. Limite: o
  rotulador e o revisor são ambos agentes Claude. Não é um olho humano.
* 37 matérias: cada uma vale 2,7 pontos percentuais. A diferença que decide a V1 é
  **uma** página.

---

## ENTREGA

```
REGRA_RECOMENDADA          = V1 (INDEX_URL exacto = capa), DEPOIS de corrigir o INDEX_URL de IT-T11-010
APLICADA                   = NO
ERRO_RESIDUAL              = V1: 1 matéria por RECEITA (IT-T11-010) + 6 por REGRA (formato, iguais ao ACTUAL)
                             + 16 capas não-índice por REGRA + 4 capas por RECEITA (3 fontes fora do livro vivo)
SEGUNDA_LEITURA            = 20/20 concordam (ambos agentes; às cegas)
TESTS                      = 5/5 (tests/test_medir_apos_receitas.py)
MUTATION                   = 3/3 mortos (fatia circular · NAO_SEI conta como passar · antes ≠ depois)
LISTING_DETAIL_GATE_PROVEN = NO — com as receitas do G1, nenhuma regra é tão boa como o ACTUAL
                             nos dois erros; a V1 falha por uma matéria cuja causa é a receita
                             de IT-T11-010, e a V2 só ganha nas páginas circulares
```

**Próximos passos, por dono:**
1. **Curator/rotas:** corrigir o `INDEX_URL` de IT-T11-010, com a mesma prova do G1
   (página buscada e ≥ 10 links com forma de matéria). Re-correr
   `medir_apos_receitas.py`; se der 6/37, a V1 fica provada no gabarito.
2. **Dono de `retrato_html.py`:** só então aplicar a V1, com os gémeos `.mjs` e `_kind`
   no mesmo passo (6-PREP-c §4).
3. **Curator:** 14 matérias ainda não casam o `LINK_PATTERN` da sua fonte. É o que
   impede qualquer regra de morada, e é provável que também impeça o coletor. Isto
   último é inferência, não medido.
4. **Dono:** decidir se `NAO_SEI` passa ou vai para uma pessoa (6-PREP-c §4.4). É
   política, não régua.
